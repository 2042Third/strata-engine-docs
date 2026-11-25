#!/usr/bin/env python3
"""Downloads the book's toolchain into .tools/ (git-ignored) and writes the scripts that put it on the PATH.

    python tools/bootstrap.py            # Node.js and the checkers (typos, lychee, actionlint) for this platform, then
                                          # .tools/env.sh and .tools/env.ps1
    . .tools/env.sh                       # Git Bash, Linux, macOS shells
    . .tools/env.ps1                      # PowerShell

Nothing is installed system-wide and nothing outside the repository's .tools/ folder is written: npm's cache, Playwright's
browsers and temporary files all go there. Every archive is checked against the SHA-256 pinned in tools/toolchain.json;
for Node.js the official SHASUMS256.txt is downloaded too and must agree with the pin. Only the standard library is used.
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import tarfile
import urllib.request
import zipfile

c_RepositoryRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c_ToolchainFile = os.path.join(c_RepositoryRoot, 'tools', 'toolchain.json')


class BootstrapError(Exception):
    pass


def platform_key(system=None, machine=None):
    """The toolchain.json key of this machine's archives ("windows-x64", "linux-x64")."""
    system = (system or platform.system()).lower()
    machine = (machine or platform.machine()).lower()
    if machine in ('amd64', 'x86_64', 'x64'):
        architecture = 'x64'
    else:
        raise BootstrapError('unsupported processor %s: the toolchain pins x64 archives only' % machine)
    if system.startswith('windows') or system.startswith('mingw') or system.startswith('msys') or system.startswith('cygwin'):
        return 'windows-' + architecture
    if system == 'linux':
        return 'linux-' + architecture
    raise BootstrapError('unsupported system %s: add its archives to tools/toolchain.json' % system)


def parse_shasums(text):
    """Maps file names to SHA-256 sums from a SHASUMS256.txt ("<sum>  <file>" per line)."""
    sums = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        digest, name = parts
        if len(digest) == 64 and all(c in '0123456789abcdef' for c in digest.lower()):
            sums[name.lstrip('*')] = digest.lower()
    return sums


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as file:
        for block in iter(lambda: file.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def download(url, destination):
    """Downloads url to destination through a temporary file, so that an interrupted download leaves nothing behind."""
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    partial = destination + '.partial'
    try:
        with urllib.request.urlopen(url, timeout=120) as response, open(partial, 'wb') as file:
            shutil.copyfileobj(response, file, 1 << 20)
        os.replace(partial, destination)
    except OSError as error:
        if os.path.exists(partial):
            os.remove(partial)
        raise BootstrapError('cannot download %s: %s' % (url, error))


def is_inside(root, path):
    root = os.path.abspath(root)
    path = os.path.abspath(path)
    return os.path.commonpath([root, path]) == root


def extract(archive, destination):
    """Unpacks a .zip, .tar.gz or .tar.xz into destination; refuses members that would land outside it."""
    os.makedirs(destination, exist_ok=True)
    if archive.endswith('.zip'):
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.namelist():
                if not is_inside(destination, os.path.join(destination, member)):
                    raise BootstrapError('%s: member %s leaves the destination' % (archive, member))
            bundle.extractall(destination)
        return
    if archive.endswith('.tar.gz') or archive.endswith('.tar.xz'):
        with tarfile.open(archive) as bundle:
            for member in bundle.getmembers():
                target = os.path.join(destination, member.name)
                if not is_inside(destination, target) or member.issym() and os.path.isabs(member.linkname):
                    raise BootstrapError('%s: member %s leaves the destination' % (archive, member.name))
            if hasattr(tarfile, 'data_filter'):
                bundle.extractall(destination, filter='data')
            else:
                bundle.extractall(destination)
        return
    raise BootstrapError('unknown archive type: %s' % archive)


def fetch_checked(url, destination, expected, official=None):
    """Downloads (unless already there) and checks the pinned sum, and the official sum when one is given."""
    if official is not None and official != expected:
        raise BootstrapError('%s: the official sum %s differs from the pin %s' % (os.path.basename(destination), official, expected))
    if not os.path.exists(destination) or sha256_of(destination) != expected:
        download(url, destination)
    actual = sha256_of(destination)
    if actual != expected:
        os.remove(destination)
        raise BootstrapError('%s: SHA-256 %s, expected %s' % (os.path.basename(destination), actual, expected))


def node_directory(tools, toolchain, key):
    name = toolchain['node']['archives'][key]['file']
    for suffix in ('.zip', '.tar.xz', '.tar.gz'):
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    folder = os.path.join(tools, name)
    return folder if key.startswith('windows') else os.path.join(folder, 'bin')


# The pinned checkers bootstrap.py installs beside Node.js, each a single program: typos (spelling), lychee (gate (a)'s
# offline link check and links.yml's weekly external one) and actionlint (CI's workflows).
c_Checkers = ('typos', 'lychee', 'actionlint')


def checker_directory(tools, toolchain, key, name):
    """The folder that holds a pinned checker's program, for the PATH: its unpacked folder, or the folder below it where
    the archive keeps the program."""
    folder = os.path.join(tools, '%s-%s' % (name, toolchain[name]['version']))
    found = find_program(folder, name + ('.exe' if key.startswith('windows') else ''))
    return os.path.dirname(found) if found else folder


def install_node(tools, toolchain, key):
    node = toolchain['node']
    archive = node['archives'][key]
    binary = os.path.join(node_directory(tools, toolchain, key), 'node.exe' if key.startswith('windows') else 'node')
    if os.path.exists(binary):
        return binary
    downloads = os.path.join(tools, 'downloads')
    sums_path = os.path.join(downloads, 'node-%s-%s' % (node['version'], node['sums_file']))
    download(node['base_url'] + node['sums_file'], sums_path)
    with open(sums_path, encoding='utf-8') as file:
        official = parse_shasums(file.read()).get(archive['file'])
    if official is None:
        raise BootstrapError('%s is not listed in the official %s' % (archive['file'], node['sums_file']))
    path = os.path.join(downloads, archive['file'])
    fetch_checked(node['base_url'] + archive['file'], path, archive['sha256'], official)
    extract(path, tools)
    if not os.path.exists(binary):
        raise BootstrapError('the Node.js archive did not contain %s' % binary)
    return binary


def install_tool(tools, toolchain, key, name, program, version=None):
    """Downloads, checks and unpacks one pinned single-folder tool (a checker, or nginx in one of its versions); returns its
    program's path. A tool pinned in several versions holds them under "versions"; `version` names one."""
    entry = toolchain[name]
    if version is not None:
        if version not in entry.get('versions', {}):
            raise BootstrapError('tools/toolchain.json pins no %s %s' % (name, version))
        entry = dict(entry['versions'][version], base_url=entry['base_url'], version=version)
    archive = entry['archives'].get(key)
    if archive is None:
        raise BootstrapError('tools/toolchain.json pins no %s archive for %s' % (name, key))
    folder = os.path.join(tools, '%s-%s' % (name, entry['version']))
    executable = program + ('.exe' if key.startswith('windows') else '')
    found = find_program(folder, executable)
    if found:
        return found
    path = os.path.join(tools, 'downloads', archive['file'])
    fetch_checked(entry['base_url'] + archive['file'], path, archive['sha256'])
    extract(path, folder)
    found = find_program(folder, executable)
    if not found:
        raise BootstrapError('the %s archive did not contain %s' % (name, executable))
    return found


def find_program(folder, executable):
    """The program in the folder or one level below it (nginx's zip holds a nginx-<version>/ folder)."""
    if not os.path.isdir(folder):
        return None
    candidates = [os.path.join(folder, executable)] + [os.path.join(folder, child, executable) for child in sorted(os.listdir(folder))]
    return next((candidate for candidate in candidates if os.path.isfile(candidate)), None)


def install_checkers(tools, toolchain, key):
    """typos, lychee and actionlint, each from its checked archive: {name: program}."""
    return {name: install_tool(tools, toolchain, key, name, name) for name in c_Checkers}


def install_nginx(tools, toolchain, key):
    """Every pinned version of nginx that has an archive for this machine (the Windows builds; Linux gets nginx from
    its packages or images): {version: program}. tools/servertest.py runs the deploy files with each of them."""
    programs = {}
    for version in sorted(toolchain['nginx']['versions'], key=lambda text: tuple(int(part) for part in text.split('.'))):
        if key in toolchain['nginx']['versions'][version]['archives']:
            programs[version] = install_tool(tools, toolchain, key, 'nginx', 'nginx', version)
    return programs


def environment(tools, toolchain, key):
    """The variables the book's commands run with: tools first on the PATH, every cache and temporary file in .tools/."""
    return {
        # A toolchain file that pins fewer checkers (an older one, a test's) puts only those on the PATH.
        'paths': [node_directory(tools, toolchain, key)] + [checker_directory(tools, toolchain, key, name) for name in c_Checkers if name in toolchain],
        'variables': {
            'npm_config_cache': os.path.join(tools, 'npm-cache'),
            'npm_config_update_notifier': 'false',
            'npm_config_fund': 'false',
            'PLAYWRIGHT_BROWSERS_PATH': os.path.join(tools, 'ms-playwright'),
            'ASTRO_TELEMETRY_DISABLED': '1',
            'DO_NOT_TRACK': '1',
            'TMP': os.path.join(tools, 'tmp'),
            'TEMP': os.path.join(tools, 'tmp'),
            'TMPDIR': os.path.join(tools, 'tmp'),
        },
    }


def to_posix(path):
    """C:\\x\\y → /c/x/y for Git Bash; other paths unchanged."""
    if len(path) > 2 and path[1] == ':':
        return '/' + path[0].lower() + path[2:].replace('\\', '/')
    return path.replace('\\', '/')


def shell_script(env, windows):
    convert = to_posix if windows else (lambda p: p)
    lines = ['# Generated by tools/bootstrap.py: puts the book\'s toolchain first on the PATH. Source it: . .tools/env.sh']
    # The engine's Tools/PerfLock.py keeps its lock in the user's own temporary directory; remember it before moving TMP.
    lines.append('export STRATA_DOCS_SYSTEM_TEMP="${STRATA_DOCS_SYSTEM_TEMP:-${TMP:-${TMPDIR:-/tmp}}}"')
    lines.append('export PATH="%s:$PATH"' % ':'.join(convert(p) for p in env['paths']))
    for name, value in env['variables'].items():
        # Windows programs (node, npm) read Windows paths; only TMPDIR is read by the POSIX tools of Git Bash.
        if windows and name == 'TMPDIR':
            value = to_posix(value)
        lines.append('export %s="%s"' % (name, value))
    if windows:
        # Git Bash and MSYS2 turn a value that starts with "/" into a Windows path before a native program (node,
        # python) sees it: DOCS_BASE=/x/y would reach the build as C:/msys64/x/y, and "--base /x/y" as X:/y. These keep
        # DOCS_BASE and "--base=/x/y" (written with "=") as they are; other paths are still converted.
        lines.append('export MSYS2_ENV_CONV_EXCL="DOCS_BASE${MSYS2_ENV_CONV_EXCL:+;$MSYS2_ENV_CONV_EXCL}"')
        lines.append('export MSYS2_ARG_CONV_EXCL="--base=${MSYS2_ARG_CONV_EXCL:+;$MSYS2_ARG_CONV_EXCL}"')
    return '\n'.join(lines) + '\n'


def powershell_script(env):
    lines = ['# Generated by tools/bootstrap.py: puts the book\'s toolchain first on the PATH. Source it: . .tools/env.ps1']
    lines.append('if (-not $env:STRATA_DOCS_SYSTEM_TEMP) { $env:STRATA_DOCS_SYSTEM_TEMP = $env:TEMP }')
    lines.append("$env:Path = '%s;' + $env:Path" % ';'.join(env['paths']))
    for name, value in env['variables'].items():
        lines.append("$env:%s = '%s'" % (name, value))
    return '\r\n'.join(lines) + '\r\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description='Downloads Node.js, typos, lychee and actionlint into .tools/ and writes .tools/env.sh and .tools/env.ps1.')
    parser.add_argument('--tools', default=os.path.join(c_RepositoryRoot, '.tools'), help='folder for the toolchain (default .tools/)')
    parser.add_argument('--only-node', action='store_true', help='only Node.js, none of the checkers')
    parser.add_argument('--servers', action='store_true', help='also nginx in each pinned version (Windows builds), to test deploy/ against real servers')
    options = parser.parse_args(argv)
    try:
        with open(c_ToolchainFile, encoding='utf-8') as file:
            toolchain = json.load(file)
        key = platform_key()
        tools = os.path.abspath(options.tools)
        for folder in ('downloads', 'npm-cache', 'ms-playwright', 'tmp'):
            os.makedirs(os.path.join(tools, folder), exist_ok=True)
        node = install_node(tools, toolchain, key)
        print('node: %s' % node)
        if not options.only_node:
            for name, program in install_checkers(tools, toolchain, key).items():
                print('%s: %s' % (name, program))
        if options.servers:
            programs = install_nginx(tools, toolchain, key)
            for version, program in programs.items():
                print('nginx %s: %s' % (version, program))
            if not programs:
                print('nginx: no archive is pinned for %s; use the system\'s nginx or the images CI runs' % key)
        env = environment(tools, toolchain, key)
        windows = key.startswith('windows')
        with open(os.path.join(tools, 'env.sh'), 'w', encoding='utf-8', newline='\n') as file:
            file.write(shell_script(env, windows))
        with open(os.path.join(tools, 'env.ps1'), 'w', encoding='utf-8', newline='') as file:
            file.write(powershell_script(env))
        print('wrote %s and %s' % (os.path.join(tools, 'env.sh'), os.path.join(tools, 'env.ps1')))
    except (BootstrapError, OSError, ValueError, KeyError) as error:
        print('bootstrap: %s' % error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
