#!/usr/bin/env python3
"""Assembles a release of the book from a built site (plan/site.md, "What a release holds"):

    python tools/release.py assemble --tag <tag> [--dist dist] [--base <base>] [--out release]
    python tools/release.py layout --dist dist --out <folder> [--base <base>]
    python tools/release.py csp [--dist dist]

assemble writes release/<tag>/: strata-engine-docs-<tag>.tar.gz (one top folder, the base's path, "strata-engine-docs/"
for site.json's base or "site/" for the root of a host: the built site with its .gz files), strata-engine-docs-deploy-
<tag>.tar.gz (one top folder, "deploy/": the committed files of deploy/ and the two the release step writes from the
built HTML, nginx-csp.conf and nginx-redirects.conf) and SHA256SUMS (sha256sum -c SHA256SUMS verifies them). <tag> is
a release tag, book-v<engine release>-r<n> (book-v0.8.1-r1), or main-<the first 8 hex digits of the commit> for a build
that is not a release. The tarballs are reproducible: entries sorted, time stamps 0, owner 0, no name in the gzip
header; two runs on one build give the same bytes.

--base is the base the site was built for (default: site.json's). The committed deploy files are written for
site.json's base; for another base every deploy file is rewritten for it (tools/booklib/deploy.py), and a book at the
root of a host drops the blocks marked "redirect" and "outside".

layout writes, for deploy/Dockerfile.build, what the container's final stage copies: <folder>/nginx/ (deploy/'s
server files under the names deploy/Dockerfile gives them in /etc/nginx/, and strata-engine-docs-base, the base for the
health check) and <folder>/www/ (the built site under /srv/www/ at its base). csp prints the policy.

Before it packs anything, assemble checks the built site: built for the base, precompressed (node scripts/precompress.mjs:
a current .gz beside every text file of 1 KB or more, no .br), no inline code the policy would block, and, for a
release tag, license.txt and third-party-notices.txt at the top (other tags note their absence).

Only the standard library is used. Exit codes: 0 written, 1 the site is not ready, 2 usage errors.
"""

import argparse
import gzip
import hashlib
import io
import os
import re
import shutil
import sys
import tarfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import deploy  # noqa: E402
from booklib import settings  # noqa: E402

c_Root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c_Name = 'strata-engine-docs'
c_ReleaseTag = re.compile(r'^book-v\d+\.\d+\.\d+-r[1-9]\d*$')
c_BuildTag = re.compile(r'^main-[0-9a-f]{8}$')
# What a text file is to scripts/precompress.mjs; the two lists must agree (tools/tests/test_release.py reads both).
c_TextExtensions = ('.html', '.css', '.js', '.mjs', '.json', '.svg', '.xml', '.txt', '.webmanifest')
c_MinimumGzipBytes = 1024
c_Notices = ('license.txt', 'third-party-notices.txt')
c_Executable = ('deploy-files.sh',)


class ReleaseError(Exception):
    pass


def check_tag(tag):
    """'release' for book-v<release>-r<n>, 'build' for main-<8 hex>; anything else is refused."""
    if c_ReleaseTag.match(tag):
        return 'release'
    if c_BuildTag.match(tag):
        return 'build'
    raise ReleaseError('the tag %r is neither a release (book-v<engine release>-r<n>, such as book-v0.8.1-r1) nor a build '
                       '(main-<the first 8 hex digits of the commit>)' % tag)


def site_files(site):
    """Every file of the built site, relative with "/", sorted."""
    found = []
    for folder, directories, names in os.walk(site):
        directories.sort()
        for name in names:
            found.append(os.path.relpath(os.path.join(folder, name), site).replace(os.sep, '/'))
    return sorted(found)


def built_for(site, base):
    """Whether the built site's pages load their files under `base` (a site built with another DOCS_BASE does not)."""
    with open(os.path.join(site, 'index.html'), encoding='utf-8') as file:
        text = file.read()
    return re.search(r'(?:href|src)="%s/_astro/' % re.escape(base), text) is not None


def site_problems(site, base, kind):
    """(problems, notes) of a built site before it is packed."""
    problems = []
    notes = []
    for name in ('index.html', '404.html'):
        if not os.path.isfile(os.path.join(site, name)):
            problems.append('%s has no %s: is it the built site?' % (site, name))
    if problems:
        return problems, notes
    if not built_for(site, base):
        problems.append('%s was not built for the base %s: build it with DOCS_BASE=%s, or name its base with --base' % (site, base or '/', base or '/'))
    files = site_files(site)
    present = set(files)
    for relative in files:
        if relative.endswith('.br'):
            problems.append('%s: a release holds no .br file (no stock nginx serves brotli)' % relative)
        elif relative.endswith('.gz'):
            source = relative[:-3]
            if source not in present or not wants_gzip(site, source):
                problems.append('%s: a .gz beside no text file of 1 KB or more: run node scripts/precompress.mjs' % relative)
        elif wants_gzip(site, relative):
            packed = relative + '.gz'
            if packed not in present:
                problems.append('%s has no .gz beside it: run node scripts/precompress.mjs' % relative)
                continue
            with open(os.path.join(site, *relative.split('/')), 'rb') as file:
                data = file.read()
            try:
                with gzip.open(os.path.join(site, *packed.split('/')), 'rb') as file:
                    same = file.read() == data
            except (OSError, EOFError):
                same = False
            if not same:
                problems.append('%s does not hold %s: run node scripts/precompress.mjs again' % (packed, relative))
    for name in c_Notices:
        if not os.path.isfile(os.path.join(site, name)):
            message = 'the site has no %s at its top: a release serves it (plan/critique/rulings-6.md, R20 and R22)' % name
            (problems if kind == 'release' else notes).append(message)
    return problems, notes


def wants_gzip(site, relative):
    return os.path.splitext(relative)[1].lower() in c_TextExtensions and os.path.getsize(os.path.join(site, *relative.split('/'))) >= c_MinimumGzipBytes


def server_files(site, base, deploy_folder):
    """{name: (text, mode)} of the deploy tarball: the committed files of deploy/ for the base and the two generated
    from the built site. Raises ReleaseError when the policy would block something a page runs."""
    files = {}
    for name in deploy.deploy_files(deploy_folder):
        with open(os.path.join(deploy_folder, name), encoding='utf-8') as file:
            text = file.read()
        if name == 'README.md' and base != deploy.c_CommittedPrefix:
            text = ('> This release was assembled for the base `%s`: where this file writes `%s`, read `%s`, and the site\'s top\n'
                    '> folder is `%s/`.\n\n' % (base or '/', deploy.c_CommittedPrefix, base or '/', deploy.top_folder(base))) + text
        elif name != 'README.md':
            text = deploy.for_base(text, base, name)
        files[name] = (text, 0o755 if name in c_Executable else 0o644)
    policy, problems = deploy.content_security_policy(site)
    if problems:
        raise ReleaseError('\n'.join(problems))
    files['nginx-csp.conf'] = (deploy.csp_conf(policy), 0o644)
    files['nginx-redirects.conf'] = (deploy.redirects_conf(deploy.moved_pages(site, base)), 0o644)
    return files


def tar_info(name, size, mode, directory=False):
    info = tarfile.TarInfo(name)
    info.size = 0 if directory else size
    info.type = tarfile.DIRTYPE if directory else tarfile.REGTYPE
    info.mode = 0o755 if directory else mode
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ''
    return info


def write_tarball(path, entries):
    """A reproducible .tar.gz: `entries` maps archive paths ("deploy/nginx.conf") to (bytes or a file path, mode). Its
    folders are written as entries of their own; everything sorted, time stamps 0, owner 0."""
    folders = set()
    for name in entries:
        parts = name.split('/')[:-1]
        for index in range(1, len(parts) + 1):
            folders.add('/'.join(parts[:index]))
    names = sorted(set(entries) | folders)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.PAX_FORMAT) as archive:
        for name in names:
            if name in folders and name not in entries:
                archive.addfile(tar_info(name + '/', 0, 0o755, directory=True))
                continue
            content, mode = entries[name]
            if isinstance(content, bytes):
                archive.addfile(tar_info(name, len(content), mode), io.BytesIO(content))
            else:
                with open(content, 'rb') as file:
                    archive.addfile(tar_info(name, os.path.getsize(content), mode), file)
    with open(path, 'wb') as file:
        with gzip.GzipFile(filename='', mode='wb', fileobj=file, compresslevel=9, mtime=0) as packed:
            packed.write(raw.getvalue())


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as file:
        for block in iter(lambda: file.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def assemble(site, base, tag, out, deploy_folder):
    """Writes <out>/<tag>/ and returns (its folder, notes). Raises ReleaseError when the site is not ready."""
    kind = check_tag(tag)
    problems, notes = site_problems(site, base, kind)
    if problems:
        raise ReleaseError('\n'.join(problems))
    files = server_files(site, base, deploy_folder)
    folder = os.path.join(out, tag)
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)
    top = deploy.top_folder(base)
    site_name = '%s-%s.tar.gz' % (c_Name, tag)
    deploy_name = '%s-deploy-%s.tar.gz' % (c_Name, tag)
    write_tarball(os.path.join(folder, site_name),
                  {'%s/%s' % (top, relative): (os.path.join(site, *relative.split('/')), 0o644) for relative in site_files(site)})
    write_tarball(os.path.join(folder, deploy_name),
                  {'deploy/%s' % name: (text.encode('utf-8'), mode) for name, (text, mode) in files.items()})
    with open(os.path.join(folder, 'SHA256SUMS'), 'w', encoding='utf-8', newline='\n') as file:
        for name in sorted((site_name, deploy_name)):
            file.write('%s  %s\n' % (sha256_of(os.path.join(folder, name)), name))
    return folder, notes


def dockerfile_copies(text):
    """[(source, destination)] of the COPY lines of a Dockerfile's last stage, without their options."""
    copies = []
    for line in text.split('\n'):
        if re.match(r'^\s*FROM\s', line, re.IGNORECASE):
            copies = []
        match = re.match(r'^\s*COPY\s+((?:--\S+\s+)*)(\S+)\s+(\S+)\s*$', line, re.IGNORECASE)
        if match:
            copies.append((match.group(2), match.group(3)))
    return copies


def layout(site, base, out, deploy_folder):
    """Writes what deploy/Dockerfile's final stage copies into <out>/nginx/ (for /etc/nginx/) and <out>/www/ (for
    /srv/www/), from the built site and the deploy files for its base."""
    problems, _ = site_problems(site, base, 'build')
    if problems:
        raise ReleaseError('\n'.join(problems))
    files = server_files(site, base, deploy_folder)
    if os.path.isdir(out):
        shutil.rmtree(out)
    top = deploy.top_folder(base)
    places = {'/etc/nginx/': os.path.join(out, 'nginx'), '/srv/www/': os.path.join(out, 'www')}
    for source, destination in dockerfile_copies(files['Dockerfile'][0]):
        root = next((prefix for prefix in places if destination.startswith(prefix)), None)
        if root is None:
            raise ReleaseError('deploy/Dockerfile copies %s to %s, outside /etc/nginx/ and /srv/www/' % (source, destination))
        target = os.path.join(places[root], *destination[len(root):].split('/'))
        if source.startswith('deploy/') and source[len('deploy/'):] in files:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, 'w', encoding='utf-8', newline='\n') as file:
                file.write(files[source[len('deploy/'):]][0])
        elif source.rstrip('/') == top:
            shutil.copytree(site, target, dirs_exist_ok=True)
        else:
            raise ReleaseError('deploy/Dockerfile copies %s, which is neither a deploy file nor the site\'s top folder %s/' % (source, top))
    os.makedirs(places['/etc/nginx/'], exist_ok=True)
    with open(os.path.join(places['/etc/nginx/'], 'strata-engine-docs-base'), 'w', encoding='utf-8', newline='\n') as file:
        file.write(base + '\n')


def committed_base(root):
    try:
        return settings.read_site(root)['base']
    except settings.SettingsError as error:
        raise ReleaseError(str(error))


def main(argv=None):
    parser = argparse.ArgumentParser(description='Assembles a release of the book from a built site.')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('assemble', 'layout', 'csp'):
        command = commands.add_parser(name)
        command.add_argument('--root', default=c_Root, help='the book\'s folder (its site.json and deploy/)')
        command.add_argument('--dist', help='the built site (default: <root>/dist)')
        if name != 'csp':
            command.add_argument('--base', help='the base the site was built for; "/" for the root of a host (default: site.json\'s)')
        if name == 'assemble':
            command.add_argument('--tag', required=True, help='book-v<engine release>-r<n>, or main-<8 hex digits of the commit>')
            command.add_argument('--out', help='the folder of releases (default: <root>/release)')
        if name == 'layout':
            command.add_argument('--out', required=True, help='the folder to write nginx/ and www/ into (replaced)')
    options = parser.parse_args(argv)
    root = os.path.abspath(options.root)
    site = os.path.abspath(options.dist or os.path.join(root, 'dist'))
    deploy_folder = os.path.join(root, 'deploy')
    try:
        if options.command == 'csp':
            policy, problems = deploy.content_security_policy(site)
            for problem in problems:
                print('release: %s' % problem, file=sys.stderr)
            print(policy)
            return 1 if problems else 0
        base = committed_base(root) if options.base is None else settings.normalize_base(options.base)
        if options.command == 'layout':
            layout(site, base, os.path.abspath(options.out), deploy_folder)
            print('release: wrote the server files and the site for the base %s into %s' % (base or '/', options.out))
            return 0
        folder, notes = assemble(site, base, options.tag, os.path.abspath(options.out or os.path.join(root, 'release')), deploy_folder)
    except settings.SettingsError as error:
        print('release: %s' % error, file=sys.stderr)
        return 2
    except ReleaseError as error:
        for line in str(error).split('\n'):
            print('release: %s' % line, file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print('release: %s' % error, file=sys.stderr)
        return 2
    for note in notes:
        print('release: note: %s' % note)
    print('release: wrote %s' % folder)
    return 0


if __name__ == '__main__':
    sys.exit(main())
