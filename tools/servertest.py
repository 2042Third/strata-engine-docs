#!/usr/bin/env python3
"""Tests the deployments of deploy/ with real nginx (plan/site.md, gates (a) and (c) and "The ten requirements and
their tests"): it serves an assembled release the two ways deploy/README.md gives, crawls the book through each
server, checks every header the configurations promise, and stops every server it started with its process tree.

    python tools/servertest.py nginx --program <nginx> --release release/<tag> [--container-program <nginx>] [--runtime]
    python tools/servertest.py url --url <origin><base>/ [--release release/<tag> | --dist dist] [--runtime]
    python tools/servertest.py layout --kind <copied|container|hostile|proxy> --release release/<tag> --out <folder>
    python tools/servertest.py static

nginx runs, with one nginx program (the Windows builds of 1.20.1 and 1.30.6 that tools/bootstrap.py --servers puts
into .tools/, or a system's nginx):

  copied     the release's files copied into a host's nginx as deploy/README.md says: deploy/nginx-http.conf in the
             http context, deploy/nginx.conf in the server block of a host that serves a site of its own at its root,
             sends X-Frame-Options and X-Content-Type-Options of its own (without "always", as the owner's host does),
             sets "expires" and has a regular-expression location for static files that answers 418 (requirement 1)
  container  the container's server (deploy/nginx-container.conf as its only server, as deploy/Dockerfile copies it)
  hostile    the container's server with that regular-expression location beside the book's include (requirement 1)
  proxy      the host's nginx in front of the container (deploy/nginx-proxy.conf in such a host's server block)

copied and proxy run once without and once with a host-headers file (/etc/nginx/snippets/strata-engine-docs-host-
headers.conf) that sends Strict-Transport-Security. Each server's files are written by write_layout, with the work
folder's paths in place of /etc/nginx/, /srv/www and /srv/host; nothing else of the files changes. layout writes the
same files with those paths kept, for a container that mounts them: CI runs nginx's official 1.20.1 image with the
copied layout, the image of deploy/Dockerfile with the hostile server, and nginx images on the host's network with the
proxy layout in front of the container (requirements 1, 8 and 10). url checks a server that already runs (CI's
containers, the live address), and only reads; --wait <seconds> first waits for a server that is starting; --container
says that it is the container (a path outside the prefix answers 404). "servertest.py --url <address>", the form of
plan/site.md, is "servertest.py url --url <address>". static checks the deploy files alone, as every command does
first.

What every served run checks: tools/crawl.py through the server (gate (a)); the redirects of the base and of a page
without their slash (301 with a path as Location); the cache class, type and compression of every kind of file;
Pagefind's own compressed files not compressed again; the manifest's type; the book's 404 page with status 404 for a
missing page, a folder without index.html and missing hashed files; a path outside the prefix that never answers the
book's 404 page; every moved page of the build answering 301 to its new page; and on every response under the prefix
the book's four headers, each exactly once, the policy of the release's nginx-csp.conf, no Strict-Transport-Security
without a host-headers file and the file's header with one. The static checks fail on "alias", an add_header inside
a nested location or without "always", Strict-Transport-Security in a deploy file, a proxy_pass with a path, and a
COPY of the final stage of deploy/Dockerfile or deploy/Dockerfile.build that brings anything but the built site and
nginx's files.

With --runtime every served run, and url, also runs gate (b): node scripts/runtime.mjs --url <the run's address> --dist
<the served build> in Playwright's Chromium (plan/site.md, "(b) Runtime"), with the Node.js of --node (default: node
on the PATH, which .tools/env.sh puts there).

Only the standard library is used. Exit codes: 0 when every check passes, 1 otherwise, 2 for usage errors (no
release, a server that does not start or leaves a process behind).
"""

import argparse
import ctypes
import glob
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import crawl  # noqa: E402
from booklib import deploy  # noqa: E402

c_Root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c_Deploy = os.path.join(c_Root, 'deploy')
c_Immutable = 'public, max-age=31536000, immutable'
# The book's four headers (plan/site.md, gate (c)): on every response under the prefix, each exactly once.
c_BookHeaders = {'content-security-policy': None, 'x-content-type-options': 'nosniff',
                 'referrer-policy': 'strict-origin-when-cross-origin', 'x-frame-options': 'SAMEORIGIN'}
# The host-headers file of the runs with one, and the header it adds.
c_HostHeader = ('strict-transport-security', 'max-age=300')
# A host's own rule for static files (requirement 1): the book's "^~" location must keep it from the book's files.
c_HostileLocation = 'location ~* \\.(css|js|mjs|json|png|svg|woff2|avif|webp|pagefind|pf_meta|pf_index|pf_fragment|pf_filter|webmanifest)$ { return 418; }'
# Where deploy/README.md, section 2, puts the release's files on a host (paths under /etc/nginx/).
c_CopiedPlaces = (('nginx-http.conf', 'conf.d/strata-engine-docs-http.conf'), ('nginx.conf', 'snippets/strata-engine-docs.conf'),
                  ('nginx-csp.conf', 'snippets/strata-engine-docs-csp.conf'),
                  ('nginx-redirects.conf', 'snippets/strata-engine-docs-redirects.conf'))
# The folder of the host's own site in CI's containers.
c_HostRoot = '/srv/host'
# The servers write_layout writes: see there.
c_Layouts = ('copied', 'container', 'hostile', 'proxy')


# ---------------------------------------------------------------------------------------------------------------------
# The deploy files alone

def nginx_statements(text):
    """(line, statement, number of locations around it) of every statement of an nginx file. Quotes are respected
    (a regular expression may hold braces), and comments are skipped."""
    stack = []
    statement = ''
    quote = None
    for number, line in enumerate(text.split('\n'), 1):
        index = 0
        while index < len(line):
            char = line[index]
            if quote:
                statement += char
                if char == '\\' and index + 1 < len(line):
                    statement += line[index + 1]
                    index += 1
                elif char == quote:
                    quote = None
            elif char in '"\'':
                quote = char
                statement += char
            elif char == '#':
                break
            elif char == '{':
                stack.append('location' if statement.strip().startswith('location') else 'block')
                statement = ''
            elif char == '}':
                if stack:
                    stack.pop()
                statement = ''
            elif char == ';':
                yield number, statement.strip(), stack.count('location')
                statement = ''
            else:
                statement += char
            index += 1
        statement += ' '


def final_stage_copies(text):
    """(line, COPY or ADD, options, sources, destination) of every COPY and ADD of a Dockerfile's last stage."""
    copies = []
    joined = []
    start = None
    for number, raw in enumerate(text.split('\n'), 1):
        line = raw.rstrip()
        if start is None:
            start = number
        if line.endswith('\\'):
            joined.append(line[:-1])
            continue
        joined.append(line)
        logical = ' '.join(part.strip() for part in joined).strip()
        joined = []
        if re.match(r'^FROM\s', logical, re.IGNORECASE):
            copies = []
        match = re.match(r'^(COPY|ADD)\s+(.*)$', logical, re.IGNORECASE)
        if match:
            words = match.group(2).split()
            options = [word for word in words if word.startswith('--')]
            paths = [word for word in words if not word.startswith('--')]
            copies.append((start, match.group(1).upper(), options, paths[:-1], paths[-1] if paths else ''))
        start = None
    return copies


def dockerfile_problems(name, text):
    """A COPY of the final stage brings only the built site (to /srv/www/) and nginx's files (to /etc/nginx/), from the
    release's folders or from the build stage's /book/serve/ (rulings 6, R22 and R26: no node_modules, nothing that
    only builds or tests the book)."""
    problems = []
    for number, instruction, options, sources, destination in final_stage_copies(text):
        if instruction == 'ADD':
            problems.append('%s:%d: ADD in the final stage: copy only the built site and nginx\'s files with COPY' % (name, number))
            continue
        allowed = destination.startswith('/etc/nginx/') or destination.startswith('/srv/www/')
        for source in sources:
            plain = source.strip('/')
            if plain in ('.', '') or not allowed or not (
                    re.match(r'^deploy/nginx[\w.-]*\.conf$', plain) or plain == deploy.top_folder(deploy.c_CommittedPrefix)
                    or plain in ('book/serve/nginx', 'book/serve/www')):
                problems.append('%s:%d: the final stage copies %s to %s: it holds only the built site and nginx\'s files' % (name, number, source, destination))
        if any(option.startswith('--from=') for option in options) and not all(source.startswith('/book/serve/') for source in sources):
            problems.append('%s:%d: the final stage copies from another stage something else than /book/serve/' % (name, number))
    return problems


def static_problems(folder=c_Deploy):
    """Problems of the deploy files themselves (plan/site.md, requirements 6, 7, 8 and 10, and the two Dockerfiles)."""
    problems = []
    for path in sorted(glob.glob(os.path.join(folder, '*.conf'))):
        name = os.path.basename(path)
        with open(path, encoding='utf-8') as file:
            text = file.read()
        for number, statement, locations in nginx_statements(text):
            if re.match(r'^alias\s', statement):
                problems.append('%s:%d: "alias": serve the book with "root", so that the URL and the path are one string' % (name, number))
            if re.match(r'^add_header\s', statement):
                if locations >= 2:
                    problems.append('%s:%d: add_header inside a nested location drops every add_header of the location around it' % (name, number))
                if not re.search(r'\salways$', statement):
                    problems.append('%s:%d: an add_header of the book carries "always", so that the 404 page has it too' % (name, number))
                if re.match(r'^add_header\s+strict-transport-security\b', statement, re.IGNORECASE):
                    problems.append('%s:%d: the book sends no Strict-Transport-Security: it binds the whole host, so it is the host\'s decision' % (name, number))
            if re.match(r'^proxy_pass\s+https?://[^/\s]+/', statement):
                problems.append('%s:%d: proxy_pass with a path changes the prefix the book needs' % (name, number))
    for name in ('Dockerfile', 'Dockerfile.build'):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            with open(path, encoding='utf-8') as file:
                problems.extend(dockerfile_problems(name, file.read()))
    return problems


# ---------------------------------------------------------------------------------------------------------------------
# Servers and their process trees

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [('dwSize', ctypes.c_uint32), ('cntUsage', ctypes.c_uint32), ('th32ProcessID', ctypes.c_uint32),
                ('th32DefaultHeapID', ctypes.c_size_t), ('th32ModuleID', ctypes.c_uint32), ('cntThreads', ctypes.c_uint32),
                ('th32ParentProcessID', ctypes.c_uint32), ('pcPriClassBase', ctypes.c_int32), ('dwFlags', ctypes.c_uint32),
                ('szExeFile', ctypes.c_wchar * 260)]


def windows_processes():
    """{pid: (parent pid, program name)} of every process (Windows only), from a Toolhelp snapshot."""
    kernel = ctypes.windll.kernel32
    kernel.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
    snapshot = kernel.CreateToolhelp32Snapshot(0x2, 0)  # TH32CS_SNAPPROCESS
    if snapshot in (None, ctypes.c_void_p(-1).value):
        raise OSError('cannot list the processes of this machine')
    processes = {}
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        found = kernel.Process32FirstW(ctypes.c_void_p(snapshot), ctypes.byref(entry))
        while found:
            processes[entry.th32ProcessID] = (entry.th32ParentProcessID, entry.szExeFile.lower())
            found = kernel.Process32NextW(ctypes.c_void_p(snapshot), ctypes.byref(entry))
    finally:
        kernel.CloseHandle(ctypes.c_void_p(snapshot))
    return processes


def descendants(pid, processes, program):
    """The processes below `pid` that run `program` (nginx's workers), however deep."""
    found = set()
    frontier = [pid]
    while frontier:
        parent = frontier.pop()
        for child, (child_parent, name) in processes.items():
            if child_parent == parent and child not in found and child != pid and name == program:
                found.add(child)
                frontier.append(child)
    return found


class Server:
    """One nginx started for a test; stop() ends it with every process it started (plan/critique/rulings-5.md, R17:
    on Windows nginx's worker keeps running when only its master is ended)."""

    def __init__(self, name, command, cwd, log):
        self.name = name
        self.command = command
        self.log_path = log
        self.log = open(log, 'w', encoding='utf-8')
        options = {'start_new_session': True} if os.name != 'nt' else {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
        self.process = subprocess.Popen(command, cwd=cwd, stdout=self.log, stderr=subprocess.STDOUT, **options)
        self.program = os.path.basename(command[0]).lower()

    def stop(self):
        """Ends the server's process tree; returns the pids that could not be ended (an empty list when all are gone)."""
        left = []
        if os.name == 'nt':
            tree = {self.process.pid} | descendants(self.process.pid, windows_processes(), self.program)
            subprocess.run(['taskkill', '/T', '/F', '/PID', str(self.process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                pass
            # A worker whose master is already gone is not in taskkill's tree any more: end it by its own pid.
            deadline = time.monotonic() + 15
            while True:
                alive = {pid for pid, (_, name) in windows_processes().items() if pid in tree and name == self.program}
                if not alive or time.monotonic() > deadline:
                    break
                for pid in alive:
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.2)
            left = sorted(alive)
        else:
            try:
                os.killpg(self.process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait()
            # A member of the group that the signal ended may still be exiting, or waiting as a zombie for the process
            # that adopted it to reap it: the group counts as gone only once kill finds none of them (CI saw a worker
            # there right after its master's wait). One still there after 5 seconds gets SIGKILL.
            deadline = time.monotonic() + 15
            killed = False
            while True:
                try:
                    os.killpg(self.process.pid, 0)
                except ProcessLookupError:
                    left = []
                    break
                if time.monotonic() > deadline:
                    left = [self.process.pid]
                    break
                if not killed and time.monotonic() > deadline - 10:
                    try:
                        os.killpg(self.process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    killed = True
                time.sleep(0.1)
        self.log.close()
        return left

    def log_tail(self):
        with open(self.log_path, encoding='utf-8', errors='replace') as file:
            return file.read()[-2000:]


def free_port():
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        return probe.getsockname()[1]


def forward(path):
    return os.path.abspath(path).replace('\\', '/')


def wait_for(url, seconds, server=None):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if server is not None and server.process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=2):
                return True
        except urllib.error.HTTPError:
            return True
        except OSError:
            time.sleep(0.2)
    return False


# ---------------------------------------------------------------------------------------------------------------------
# The release and the configurations of the runs

def unpack_release(release, work):
    """Unpacks a release folder's two tarballs into <work>/release/; returns (site folder, deploy folder, top folder)."""
    sites = sorted(glob.glob(os.path.join(release, 'strata-engine-docs-*.tar.gz')))
    deploys = [path for path in sites if os.path.basename(path).startswith('strata-engine-docs-deploy-')]
    sites = [path for path in sites if path not in deploys]
    if len(sites) != 1 or len(deploys) != 1:
        raise ValueError('%s does not hold one site tarball and one deploy tarball: assemble it with tools/release.py assemble' % release)
    target = os.path.join(work, 'release')
    for archive in (sites[0], deploys[0]):
        with tarfile.open(archive) as bundle:
            if hasattr(tarfile, 'data_filter'):
                bundle.extractall(target, filter='data')
            else:
                bundle.extractall(target)
    tops = sorted(name for name in os.listdir(target) if name != 'deploy')
    if len(tops) != 1:
        raise ValueError('the site tarball of %s holds %d top folders, not one' % (release, len(tops)))
    site = os.path.join(target, tops[0])
    while not os.path.isfile(os.path.join(site, 'index.html')):
        children = [name for name in os.listdir(site) if os.path.isdir(os.path.join(site, name))]
        if len(children) != 1:
            raise ValueError('the site tarball of %s holds no built site under its top folder' % release)
        site = os.path.join(site, children[0])
    return site, os.path.join(target, 'deploy')


def site_origin_and_base(site):
    """The origin and the base the site was built for, read from its landing page's canonical link."""
    with open(os.path.join(site, 'index.html'), encoding='utf-8') as file:
        match = re.search(r'<link rel="canonical" href="(https?://[^/"]+)(/[^"]*)"', file.read())
    if not match:
        raise ValueError('%s/index.html has no canonical link: is it the built site?' % site)
    return match.group(1), crawl.normalize_base(match.group(2))


def read(path):
    with open(path, encoding='utf-8') as file:
        return file.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as file:
        file.write(text)


def place_paths(text, etc, www):
    """A deploy file with its absolute paths moved into the work folder: /etc/nginx/ and the root /srv/www."""
    return text.replace('/etc/nginx/', forward(etc) + '/').replace('root /srv/www;', 'root %s;' % forward(www))


def with_hostile_location(text):
    """The container's server block with a host's regular-expression location for static files right after the book's
    include (requirement 1; plan/site.md calls this server block nginx-hostile.conf)."""
    include = re.compile(r'^([ \t]*include[ \t]+\S*/snippets/strata-engine-docs\.conf;)[ \t]*$', re.MULTILINE)
    if len(include.findall(text)) != 1:
        raise ValueError('deploy/nginx-container.conf does not include the book\'s snippets/strata-engine-docs.conf exactly once')
    return include.sub(lambda match: '%s\n\t# A host\'s own rule for static files: the book\'s "^~" keeps it from the book\'s files.\n\t%s'
                       % (match.group(1), c_HostileLocation), text)


def write_layout(kind, deploy_folder, site, base, out, host_headers=False, listen=None, upstream=None, move=False):
    """Writes under <out> the files of one server of a deployment, where deploy/README.md and deploy/Dockerfile put
    them: <out>/etc/nginx/ stands for /etc/nginx/, <out>/srv/www/ for /srv/www/ (the book) and <out>/srv/host/ for the
    host's own site. The server block is <out>/etc/nginx/conf.d/default.conf, read in the http context of an nginx whose
    main configuration includes conf.d/*.conf, as the official images' and most installations' do. Kinds:

      copied     a host with a site of its own and the release's files copied in (deploy/README.md, section 2)
      container  what deploy/Dockerfile copies into its image (deploy/nginx-container.conf is its server)
      hostile    the container with a host's regular-expression location for static files in its server (requirement 1)
      proxy      a host with a site of its own in front of the container (deploy/README.md, section 3)

    `listen` is what the server listens on (default: 8080 in the container, as deploy/Dockerfile exposes it, and 80 on
    a host); `upstream` is the container's address for the proxy (default: deploy/nginx-proxy.conf's 127.0.0.1:8080);
    `host_headers` adds the host-headers file that sends Strict-Transport-Security (copied and proxy only). With `move`
    the files name the folders under <out> in place of /etc/nginx/, /srv/www and /srv/host (this tool's own runs);
    without it they keep those paths, for a container that mounts the folders there. Returns the server block's path."""
    if kind not in c_Layouts:
        raise ValueError('a layout is one of %s, not %r' % (', '.join(c_Layouts), kind))
    if host_headers and kind not in ('copied', 'proxy'):
        raise ValueError('a host-headers file belongs to a host: the copied or the proxy layout, not the %s' % kind)
    etc = os.path.join(out, 'etc', 'nginx')
    www = os.path.join(out, 'srv', 'www')
    host = os.path.join(out, 'srv', 'host')
    server = os.path.join(etc, 'conf.d', 'default.conf')

    def put(relative, text):
        write(os.path.join(etc, *relative.split('/')), place_paths(text, etc, www) if move else text)

    def deploy_text(name):
        return read(os.path.join(deploy_folder, name))

    def copy_site(relative):
        shutil.copytree(site, os.path.join(www, *[part for part in relative.split('/') if part]), dirs_exist_ok=True)

    if kind in ('container', 'hostile'):
        for number, _, _, sources, destination in final_stage_copies(deploy_text('Dockerfile')):
            for source in sources:
                if destination.startswith('/etc/nginx/') and re.match(r'^deploy/nginx[\w.-]*\.conf$', source):
                    put(destination[len('/etc/nginx/'):], deploy_text(source[len('deploy/'):]))
                elif destination.startswith('/srv/www/') and source.rstrip('/') == deploy.top_folder(base):
                    copy_site(destination[len('/srv/www/'):])
                else:
                    raise ValueError('deploy/Dockerfile:%d copies %s to %s, which is neither an nginx file of deploy/ in /etc/nginx/ '
                                     'nor the site\'s top folder %s/ in /srv/www/' % (number, source, destination, deploy.top_folder(base)))
        if not os.path.isfile(server):
            raise ValueError('deploy/Dockerfile does not copy the container\'s server to /etc/nginx/conf.d/default.conf')
        text = read(server)
        if 'listen 8080;' not in text:
            raise ValueError('deploy/nginx-container.conf does not listen on 8080 as deploy/Dockerfile exposes it')
        text = text.replace('listen 8080;', 'listen %s;' % (listen or '8080'))
        write(server, with_hostile_location(text) if kind == 'hostile' else text)
        return server
    if kind == 'copied':
        for name, relative in c_CopiedPlaces:
            put(relative, deploy_text(name))
        copy_site(base)
        include = 'strata-engine-docs.conf'
    else:
        text = deploy_text('nginx-proxy.conf')
        if 'proxy_pass http://127.0.0.1:8080;' not in text:
            raise ValueError('deploy/nginx-proxy.conf does not forward to http://127.0.0.1:8080 as deploy/README.md runs the container')
        put('snippets/strata-engine-docs-proxy.conf', text.replace('proxy_pass http://127.0.0.1:8080;', 'proxy_pass http://%s;' % (upstream or '127.0.0.1:8080')))
        include = 'strata-engine-docs-proxy.conf'
    if host_headers:
        write(os.path.join(etc, 'snippets', 'strata-engine-docs-host-headers.conf'),
              'add_header %s "%s" always;\n' % ('Strict-Transport-Security', c_HostHeader[1]))
    if base:
        write_host_site(host)
    named_etc, named_host = (forward(etc), forward(host)) if move else ('/etc/nginx', c_HostRoot)
    write(server, '\n'.join(host_server(listen or '80', named_etc, named_host, base, include)) + '\n')
    return server


def conf_d(out):
    """The http context's line that reads a layout's server files, as the official images' nginx.conf reads them."""
    return ['include %s;' % forward(os.path.join(out, 'etc', 'nginx', 'conf.d', '*.conf'))]


def main_conf(prefix, program, http_lines):
    """An nginx main configuration in its own prefix folder; returns the command that runs it in the foreground."""
    for name in ('conf', 'logs', 'temp'):
        os.makedirs(os.path.join(prefix, name), exist_ok=True)
    mime = None
    for candidate in (os.path.join(os.path.dirname(program), 'conf', 'mime.types'), '/etc/nginx/mime.types'):
        if os.path.isfile(candidate):
            mime = candidate
            break
    if mime is None:
        raise ValueError('mime.types of nginx not found next to %s or in /etc/nginx' % program)
    shutil.copy(mime, os.path.join(prefix, 'conf', 'mime.types'))
    temp = '\n'.join('\t%s_temp_path temp/%s;' % (name, name) for name in ('client_body', 'proxy', 'fastcgi', 'uwsgi', 'scgi'))
    write(os.path.join(prefix, 'conf', 'nginx.conf'),
          'daemon off;\nmaster_process on;\nworker_processes 1;\nerror_log logs/error.log;\npid logs/nginx.pid;\n'
          'events { worker_connections 256; }\nhttp {\n\tinclude mime.types;\n\tdefault_type application/octet-stream;\n'
          '\taccess_log off;\n%s\n%s\n}\n' % (temp, '\n'.join('\t' + line for line in http_lines)))
    # -e: nginx opens its compiled-in error log before it reads the configuration; that folder may not be writable.
    return [program, '-p', forward(prefix) + '/', '-e', 'logs/error.log', '-c', 'conf/nginx.conf']


def host_server(listen, etc, host_root, base, book_include):
    """The server block of a host that also serves a site of its own at its root (as the owner's host does): its own
    headers without "always", an "expires", a regular-expression location for static files, and the book's include.
    `etc` and `host_root` are the paths nginx reads (/etc/nginx and /srv/host in CI's containers). A book at the root
    of a host is the whole server: the host keeps no site of its own beside it."""
    lines = ['server {', '\tlisten %s;' % listen, '\tserver_name localhost;',
             '\tadd_header X-Frame-Options "SAMEORIGIN";', '\tadd_header X-Content-Type-Options "nosniff";', '\texpires 1h;',
             '\t' + c_HostileLocation]
    if base:
        lines += ['\troot %s;' % host_root, '\terror_page 404 /404.html;', '\tlocation / { try_files $uri $uri/ =404; }']
    lines += ['\tinclude %s/snippets/%s;' % (etc, book_include), '}']
    return lines


def write_host_site(folder):
    write(os.path.join(folder, 'index.html'), '<!doctype html><title>The host</title><p>The host\'s own site.</p>\n')
    write(os.path.join(folder, '404.html'), '<!doctype html><title>Not found</title><p>The host\'s own 404 page.</p>\n')


# ---------------------------------------------------------------------------------------------------------------------
# The checks of a served book

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *arguments):
        return None


s_Opener = urllib.request.build_opener(NoRedirect)


def request(url, accept_encoding=None):
    """(status, headers as [(lowercase name, value)], body) without following redirects."""
    headers = {'User-Agent': 'strata-book-servertest'}
    if accept_encoding:
        headers['Accept-Encoding'] = accept_encoding
    try:
        with s_Opener.open(urllib.request.Request(url, headers=headers), timeout=15) as response:
            return response.status, [(name.lower(), value) for name, value in response.headers.items()], response.read()
    except urllib.error.HTTPError as error:
        return error.code, [(name.lower(), value) for name, value in error.headers.items()], error.read()


def header(headers, name):
    values = [value for key, value in headers if key == name]
    return values[0] if values else ''


def first_file(folder, pattern):
    found = sorted(glob.glob(os.path.join(folder, pattern), recursive=True))
    return os.path.relpath(found[0], folder).replace(os.sep, '/') if found else None


def first_page_folder(site):
    """The relative path of a page below a part ("core/time"), for the redirect of a page without its slash."""
    for path in sorted(glob.glob(os.path.join(site, '*', '*', 'index.html'))):
        relative = os.path.relpath(os.path.dirname(path), site).replace(os.sep, '/')
        if not relative.startswith(('_', 'pagefind', 'print')):
            return relative
    return None


def origin_of(url):
    parts = urllib.parse.urlsplit(url)
    return '%s://%s' % (parts.scheme, parts.netloc)


def header_checks(start, site, base, policy=None, container=False, host_header=None, forbid_header=None):
    """Problems with the headers the deploy configurations promise (gate (c)). `start` is "<origin><base>/", `site` the
    built files being served, `policy` the release's Content Security Policy, `container` whether the server serves
    nothing but the book, `host_header` a (name, value) every response under the prefix carries, `forbid_header` a
    name none carries."""
    problems = []
    origin = origin_of(start)
    with open(os.path.join(site, '404.html'), 'rb') as file:
        not_found_page = file.read()
    responses = []

    def get(path, accept_encoding=None, under_prefix=True):
        status, headers, body = request(origin + path, accept_encoding)
        if under_prefix:
            responses.append((path, status, headers))
        return status, headers, body

    def expect_redirect(path, target, under_prefix=True):
        status, headers, _ = get(path, under_prefix=under_prefix)
        location = [value for name, value in headers if name == 'location']
        if status != 301 or location != [target]:
            problems.append('%s answers %d with Location %r: it must answer 301 with the path %s' % (path, status, location, target))
        for name in c_BookHeaders:
            if len([key for key, _ in headers if key == name]) > 1:
                problems.append('%s answers %s more than once' % (path, name))

    def expect_cache(relative, want_immutable, content_type=None, encoded=None):
        if relative is None:
            return
        status, headers, _ = get('%s/%s' % (base, relative), accept_encoding='gzip')
        cache = header(headers, 'cache-control')
        if status != 200:
            problems.append('%s/%s answers %d' % (base, relative, status))
            return
        if want_immutable and cache != c_Immutable:
            problems.append('%s is not cached as immutable (Cache-Control: %s)' % (relative, cache or 'none'))
        if not want_immutable and cache != 'no-cache':
            problems.append('%s must be checked again on every visit (Cache-Control: no-cache), not %r' % (relative, cache or 'none'))
        if content_type and not re.match(content_type, header(headers, 'content-type')):
            problems.append('%s is served as %r' % (relative, header(headers, 'content-type')))
        encoding = header(headers, 'content-encoding')
        if encoded is False and encoding:
            problems.append('%s is compressed again (Content-Encoding: %s): Pagefind compressed it already' % (relative, encoding))
        if encoded is True and encoding != 'gzip':
            problems.append('%s is not compressed (Content-Encoding: %s)' % (relative, encoding or 'none'))

    def expect_not_found(path, why):
        status, headers, body = get(path)
        if status != 404 or body != not_found_page:
            problems.append('%s (%s) answers %d%s: it must answer the book\'s 404 page with status 404' % (path, why, status, '' if body == not_found_page else ' without the book\'s 404 page'))
        if 'immutable' in header(headers, 'cache-control'):
            problems.append('%s (%s) answers its 404 as immutable: a file missing for a moment would stay missing for a year' % (path, why))

    # Redirects: 301, and Location is a path, never a scheme, host or port. The base without its slash is answered by
    # an exact location outside the book's location; it is not under the prefix.
    if base:
        expect_redirect(base, base + '/', under_prefix=False)
    page = first_page_folder(site)
    if page:
        expect_redirect('%s/%s' % (base, page), '%s/%s/' % (base, page))
    # Pages: HTML with its charset, checked again, compressed.
    status, headers, _ = get(base + '/', accept_encoding='gzip')
    if status != 200 or not re.match(r'text/html;\s*charset=utf-8$', header(headers, 'content-type'), re.IGNORECASE):
        problems.append('%s/ answers %d as %r: a page is text/html; charset=utf-8' % (base, status, header(headers, 'content-type')))
    expect_cache('', False, encoded=True)
    if page:
        expect_cache(page + '/', False, r'text/html;\s*charset=utf-8$', encoded=True)
    # Files named by their hash: immutable, with the book's own types (nginx 1.20.1's mime.types knows no avif).
    expect_cache(first_file(site, '_astro/*.css'), True, r'text/css')
    expect_cache(first_file(site, '_astro/*.js'), True, r'(text|application)/javascript')
    expect_cache(first_file(site, '_astro/*.woff2'), True, r'font/woff2$')
    expect_cache(first_file(site, '_figures/**/*.avif'), True, r'image/avif$')
    expect_cache(first_file(site, '_figures/**/*.webp'), True, r'image/webp$')
    for folder in ('index', 'fragment', 'filter'):
        expect_cache(first_file(site, 'pagefind/%s/*' % folder), True, r'application/octet-stream$', encoded=False)
    expect_cache(first_file(site, 'pagefind/pagefind.*.pf_meta'), True, r'application/octet-stream$', encoded=False)
    # Pagefind's files without a hash in their names: a new build changes them under the same name. Its scripts are
    # not compressed by Pagefind: the server sends their .gz (scripts/search-payload.mjs counts on it).
    for name in ('pagefind/pagefind.js', 'pagefind/pagefind-worker.js', 'pagefind/pagefind-entry.json', 'pagefind/pagefind-ui.js', 'pagefind/pagefind-ui.css'):
        path = os.path.join(site, *name.split('/'))
        if os.path.isfile(path):
            expect_cache(name, False, encoded=True if os.path.getsize(path) >= 1024 else None)
    expect_cache(first_file(site, 'pagefind/wasm.*.pagefind'), False, r'application/octet-stream$', encoded=False)
    # The manifest's type, in its nested location, with the book's headers (requirement 7).
    status, headers, _ = get('%s/manifest.webmanifest' % base)
    if status != 200 or not header(headers, 'content-type').startswith('application/manifest+json'):
        problems.append('manifest.webmanifest answers %d as %s' % (status, header(headers, 'content-type') or 'nothing'))
    for name in ('license.txt', 'third-party-notices.txt'):
        if os.path.isfile(os.path.join(site, name)):
            expect_cache(name, False, r'text/plain;\s*charset=utf-8$')
    # Missing addresses: the book's 404 page with status 404, never cached as immutable.
    expect_not_found('%s/a/b/c/' % base, 'a missing page')
    expect_not_found('%s/_astro/' % base, 'a folder without index.html: no listing, no bare 403')
    expect_not_found('%s/_astro/missing-%d.js' % (base, os.getpid()), 'a missing hashed script')
    expect_not_found('%s/_figures/missing.0123456789.960.avif' % base, 'a missing picture')
    for name in sorted(os.listdir(site)):
        if os.path.isdir(os.path.join(site, name)) and not os.path.isfile(os.path.join(site, name, 'index.html')) and name != '_astro':
            expect_not_found('%s/%s/' % (base, name), 'a folder without index.html')
    # Moved pages: the old address, with and without its slash, answers 301 with the new page's path.
    for old, new in deploy.moved_pages(site, base):
        expect_redirect(old, new)
        expect_redirect(old.rstrip('/'), new)
    # Outside the prefix: the container answers 404, its root too (whatever nginx's default root holds); a host
    # answers for itself. Never the book's 404 page.
    if base:
        for path in ['/outside-the-book-%d/' % os.getpid()] + (['/'] if container else []):
            status, _, body = request(origin + path)
            if body == not_found_page:
                problems.append('%s, outside the prefix, answers the book\'s 404 page' % path)
            if container and status != 404:
                problems.append('%s, outside the prefix, answers %d in the container: nothing but the book is served there, so it answers 404' % (path, status))
    # The book's headers on every response under the prefix, each exactly once.
    for path, status, headers in responses:
        for name, value in c_BookHeaders.items():
            found = [received for key, received in headers if key == name]
            if not found:
                problems.append('%s (%d) has no %s' % (path, status, name))
            elif len(found) > 1:
                problems.append('%s (%d) has %s %d times: %s' % (path, status, name, len(found), ' | '.join(found)))
            elif name == 'content-security-policy' and policy is not None and found[0] != policy:
                problems.append('%s (%d) sends another policy than the release\'s nginx-csp.conf: %s' % (path, status, found[0]))
            elif value is not None and found[0] != value:
                problems.append('%s (%d) has %s: %s, not %s' % (path, status, name, found[0], value))
        if len([key for key, _ in headers if key == 'cache-control']) > 1:
            problems.append('%s (%d) has Cache-Control more than once: the host\'s "expires" reached it' % (path, status))
        if host_header is not None:
            found = [received for key, received in headers if key == host_header[0]]
            if found != [host_header[1]]:
                problems.append('%s (%d) has %s %r: the host-headers file sends %r once' % (path, status, host_header[0], found, host_header[1]))
        if forbid_header is not None and any(key == forbid_header for key, _ in headers):
            problems.append('%s (%d) has %s: the book never sends it, and no host-headers file asked for it' % (path, status, forbid_header))
    return problems


def check_served(start, site, base, site_origin, runtime=None, **options):
    """Crawls a served site and checks its headers, and with `runtime` (the Node.js program) runs gate (b) through
    it; returns (crawl exit code, problems)."""
    code = crawl.main(['--url', start, '--dist', site, '--base=%s' % (base or '/'), '--site', site_origin])
    problems = header_checks(start, site, base, **options)
    if runtime:
        problems += runtime_problems(runtime, start, site)
    return code, problems


def runtime_problems(node, start, site):
    """Gate (b) through a running server: scripts/runtime.mjs in Chromium, its output passed through; a list with one
    problem when it fails."""
    command = [node, os.path.join(c_Root, 'scripts', 'runtime.mjs'), '--url', start, '--dist', site]
    try:
        result = subprocess.run(command, cwd=c_Root)
    except OSError as error:
        return ['the runtime check (gate (b)) did not start: %s: name Node.js with --node, or source .tools/env.sh' % error]
    return ['the runtime check (gate (b)) failed (its problems are above)'] if result.returncode != 0 else []


# ---------------------------------------------------------------------------------------------------------------------
# The runs

def run_servers(program, release, work, only=None, container_program=None, runtime=None):
    """Runs the copied, container, hostile and proxy runs against a release; returns the problems. `program` is the
    host's nginx; the container runs `container_program`, or the same program (the owner's host runs 1.20.1 in front of
    the container's 1.30.6). Each server reads the files write_layout writes for it, from the same code that writes
    CI's containers' files, with the work folder's paths in place of /etc/nginx/ and /srv/."""
    container_program = container_program or program
    site, deploy_folder = unpack_release(release, work)
    origin, base = site_origin_and_base(site)
    policy = re.search(r'add_header Content-Security-Policy "([^"]*)" always;', read(os.path.join(deploy_folder, 'nginx-csp.conf'))).group(1)
    problems = []
    runs = [('copied', False), ('copied', True), ('container', False), ('hostile', False), ('proxy', False), ('proxy', True)]
    for kind, host_headers in runs:
        if only and kind not in only:
            continue
        label = '%s%s' % (kind, ' with a host-headers file' if host_headers else '')
        folder = os.path.join(work, '%s%s' % (kind, '-headers' if host_headers else ''))
        servers = []
        try:
            port = free_port()
            container_port = port if kind in ('container', 'hostile') else free_port()
            if kind != 'copied':
                container = os.path.join(folder, 'container')
                write_layout('container' if kind == 'proxy' else kind, deploy_folder, site, base, container,
                             listen='127.0.0.1:%d' % container_port, move=True)
                # nginx's default root (html/ in its prefix) holds a welcome page, as many installations do: the
                # container's server must not serve it.
                write(os.path.join(container, 'prefix', 'html', 'index.html'), '<!doctype html><title>Welcome to nginx</title>\n')
                servers.append(Server('container', main_conf(os.path.join(container, 'prefix'), container_program, conf_d(container)), folder,
                                      os.path.join(folder, 'container.log')))
            if kind in ('copied', 'proxy'):
                host = os.path.join(folder, 'host')
                write_layout(kind, deploy_folder, site, base, host, host_headers, listen='127.0.0.1:%d' % port,
                             upstream='127.0.0.1:%d' % container_port, move=True)
                servers.append(Server('host', main_conf(os.path.join(host, 'prefix'), program, conf_d(host)), folder, os.path.join(folder, 'host.log')))
            start = 'http://127.0.0.1:%d%s/' % (port, base)
            for server in servers:
                server_port = port if server.name == 'host' else container_port
                if not wait_for('http://127.0.0.1:%d/' % server_port, 30, server):
                    raise ValueError('nginx (%s of the %s run) did not start:\n%s' % (server.name, label, server.log_tail()))
            code, found = check_served(start, site, base, origin, runtime=runtime, policy=policy, container=(kind in ('container', 'hostile')),
                                       host_header=c_HostHeader if host_headers else None,
                                       forbid_header=None if host_headers else c_HostHeader[0])
            if code != 0:
                found.insert(0, 'the crawl through the server failed (its problems are above)')
            for problem in found:
                print('servertest: %s: %s' % (label, problem))
            print('servertest: %s at the base %s: %s' % (label, base or '/', 'passed' if not found else 'FAILED'))
            problems += ['%s: %s' % (label, problem) for problem in found]
        finally:
            for server in reversed(servers):
                left = server.stop()
                if left:
                    raise ValueError('nginx (%s of the %s run) left processes %s running' % (server.name, label, ', '.join(map(str, left))))
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description='Tests the deploy files with real nginx, or checks a running server.')
    commands = parser.add_subparsers(dest='command', required=True)
    served = commands.add_parser('nginx', help='serve a release the two ways of deploy/README.md and check it')
    served.add_argument('--program', required=True, help='the nginx executable')
    served.add_argument('--release', required=True, help='the release folder tools/release.py assemble wrote (release/<tag>)')
    served.add_argument('--runs', help='only these runs, separated by commas: %s' % ', '.join(c_Layouts))
    served.add_argument('--container-program', help='the nginx of the container runs (default: --program)')
    served.add_argument('--runtime', action='store_true', help='also run gate (b), scripts/runtime.mjs in Chromium, through every run')
    served.add_argument('--node', default='node', help='the Node.js program of --runtime (default: node on the PATH)')
    url = commands.add_parser('url', help='check a server that already runs (it only reads)')
    url.add_argument('--url', required=True, help='the served book, "<origin><base>/"')
    source = url.add_mutually_exclusive_group()
    source.add_argument('--release', help='the release being served')
    source.add_argument('--dist', help='the built files being served (default: <root>/dist)')
    url.add_argument('--root', default=c_Root, help='the book\'s folder')
    url.add_argument('--site', help='the origin the site was built for (default: read from its landing page)')
    url.add_argument('--container', action='store_true', help='the server serves nothing but the book: a path outside the prefix answers 404')
    url.add_argument('--host-header', help='"Name: value" that every response under the prefix carries (a host-headers file)')
    url.add_argument('--no-header', help='a header no response under the prefix carries (Strict-Transport-Security)')
    url.add_argument('--wait', type=int, default=0, help='wait up to this many seconds for the server to answer (a container that is starting)')
    url.add_argument('--runtime', action='store_true', help='also run gate (b), scripts/runtime.mjs in Chromium, through the server')
    url.add_argument('--node', default='node', help='the Node.js program of --runtime (default: node on the PATH)')
    laid = commands.add_parser('layout', help='write the files of one server, for a container that mounts them (CI)')
    laid.add_argument('--kind', required=True, choices=c_Layouts, help='copied, container, hostile or proxy (see write_layout)')
    laid.add_argument('--release', required=True, help='the release folder tools/release.py assemble wrote (release/<tag>)')
    laid.add_argument('--out', required=True, help='a new or empty folder: <out>/etc/nginx/ and <out>/srv/ are written')
    laid.add_argument('--listen', help='what the server listens on (default: 8080 in the container, 80 on a host)')
    laid.add_argument('--host-headers', action='store_true', help='add the host-headers file, which sends Strict-Transport-Security "%s" (copied and proxy)' % c_HostHeader[1])
    commands.add_parser('static', help='check the deploy files alone')
    argv = list(sys.argv[1:] if argv is None else argv)
    # plan/site.md and deploy/README.md's other form for a running server: "servertest.py --url <address>".
    if argv and (argv[0] == '--url' or argv[0].startswith('--url=')):
        argv.insert(0, 'url')
    options = parser.parse_args(argv)
    problems = static_problems()
    for problem in problems:
        print('servertest: %s' % problem)
    if options.command == 'static':
        print('servertest: the deploy files %s' % ('passed' if not problems else 'FAILED'))
        return 1 if problems else 0
    # The long form of the path: nginx for Windows cannot open a configuration under a short (8.3) name such as
    # C:/Users/ABCDEF~1/, which the system's temporary folder may have.
    work = os.path.realpath(tempfile.mkdtemp(prefix='servertest-'))
    try:
        if options.command == 'layout':
            out = os.path.abspath(options.out)
            if os.path.exists(out) and (not os.path.isdir(out) or os.listdir(out)):
                raise ValueError('%s is not a new or empty folder' % out)
            site, deploy_folder = unpack_release(os.path.abspath(options.release), work)
            _, base = site_origin_and_base(site)
            server = write_layout(options.kind, deploy_folder, site, base, out, options.host_headers, options.listen)
            print('servertest: wrote the %s server for the base %s: %s' % (options.kind, base or '/', server))
            return 1 if problems else 0
        if options.command == 'url':
            parts = urllib.parse.urlsplit(options.url)
            if parts.scheme not in ('http', 'https') or not parts.netloc:
                raise ValueError('--url is an http or https address such as https://books.example.org/strata-engine-docs/')
            start = options.url if options.url.endswith('/') else options.url + '/'
            base = crawl.normalize_base(parts.path or '/')
            if options.wait and not wait_for(start, options.wait):
                raise ValueError('%s did not answer within %d seconds' % (start, options.wait))
            if options.release:
                site, deploy_folder = unpack_release(os.path.abspath(options.release), work)
                match = re.search(r'add_header Content-Security-Policy "([^"]*)" always;', read(os.path.join(deploy_folder, 'nginx-csp.conf')))
                policy = match.group(1) if match else None
            else:
                site = os.path.abspath(options.dist or os.path.join(options.root, 'dist'))
                policy = None
            if not os.path.isfile(os.path.join(site, '404.html')):
                raise ValueError('%s has no built site' % site)
            origin = options.site or site_origin_and_base(site)[0]
            host_header = None
            if options.host_header:
                name, _, value = options.host_header.partition(':')
                host_header = (name.strip().lower(), value.strip())
            code, found = check_served(start, site, base, origin, runtime=options.node if options.runtime else None, policy=policy, container=options.container,
                                       host_header=host_header, forbid_header=options.no_header.lower() if options.no_header else None)
            for problem in found:
                print('servertest: %s' % problem)
            passed = code == 0 and not problems and not found
            print('servertest: %s %s' % (start, 'passed' if passed else 'FAILED'))
            return 0 if passed else 1
        program = os.path.abspath(options.program)
        if not os.path.isfile(program):
            raise ValueError('%s does not exist: python tools/bootstrap.py --servers fetches nginx into .tools/' % program)
        only = set(options.runs.split(',')) if options.runs else None
        if only and not only <= set(c_Layouts):
            raise ValueError('--runs names %s' % ', '.join(c_Layouts))
        container_program = os.path.abspath(options.container_program) if options.container_program else program
        if not os.path.isfile(container_program):
            raise ValueError('%s does not exist' % container_program)
        problems += run_servers(program, os.path.abspath(options.release), work, only, container_program, options.node if options.runtime else None)
        versions = [subprocess.run([name, '-v'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout.strip() for name in (program, container_program)]
        label = versions[0] if versions[0] == versions[1] else '%s (the container: %s)' % (versions[0], versions[1])
        print('servertest: %s, every run %s' % (label, 'passed' if not problems else 'FAILED'))
        return 1 if problems else 0
    except (OSError, ValueError, tarfile.TarError) as error:
        print('servertest: %s' % error, file=sys.stderr)
        return 2
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
