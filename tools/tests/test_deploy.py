"""The deploy files (plan/site.md, "The deploy folder"): written for site.json's base and rewritten for another one
(booklib/deploy.py, tools/deployfiles.py), the static checks and the configurations of tools/servertest.py, its
header checks against a small server, the processes it ends, the base path's rules (crawl.normalize_base) and
deploy/deploy-files.sh's two passes."""

import contextlib
import http.server
import io
import os
import re
import shutil
import socketserver
import stat
import subprocess
import sys
import tempfile
import threading
import unittest

# The tools and this folder as packages, however unittest was started: discover -s tools/tests -t tools, -t . or
# discover tools/tests (plan/pipelines.md writes the last one).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
import crawl
import deployfiles
import release
import servertest
from booklib import deploy
from booklib import settings

c_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c_Deploy = os.path.join(c_Root, 'deploy')


def read(name):
    with open(os.path.join(c_Deploy, name), encoding='utf-8') as file:
        return file.read()


class BaseTests(unittest.TestCase):
    def test_the_base_follows_the_build_s_rules(self):
        self.assertEqual(crawl.normalize_base('/strata-engine-docs/'), '/strata-engine-docs')
        self.assertEqual(crawl.normalize_base('/'), '')
        for bad, message in (('', 'empty'), ('  ', 'empty'), ('docs', 'starting with'), ('//host/x', 'starting with'), ('/a//b', 'empty segment'), ('/a/../b', r'\.\.'), ('/a b', 'only letters')):
            with self.assertRaisesRegex(ValueError, message):
                crawl.normalize_base(bad)


class CommittedFilesTests(unittest.TestCase):
    def test_the_deploy_files_are_written_for_site_json_s_base(self):
        # rulings 6, R24: a move of site.json's base rewrites deploy/ in the same commit.
        base = settings.read_site(c_Root)['base']
        self.assertEqual(base, deploy.c_CommittedPrefix,
                         'site.json\'s base is %s but deploy/ is written for %s: write deploy/\'s files for the new base with '
                         'tools/deployfiles.py, copy them over deploy/ and change c_CommittedPrefix in tools/booklib/deploy.py' % (base, deploy.c_CommittedPrefix))
        self.assertIn('location ^~ %s/ {' % base, read('nginx.conf'))
        self.assertIn('location = %s {' % base, read('nginx.conf'))
        self.assertIn('error_page 403 404 =404 %s/404.html;' % base, read('nginx.conf'))
        self.assertIn('location = %s/manifest.webmanifest {' % base, read('nginx.conf'))
        self.assertIn('location ^~ %s/ {' % base, read('nginx-proxy.conf'))
        self.assertEqual(sorted(set(re.findall(r'"?~\^(/[\w-]+)/', read('nginx-http.conf')))), [base])
        self.assertIn('COPY --chown=101:101 %s/ /srv/www%s/' % (deploy.top_folder(base), base), read('Dockerfile'))
        self.assertIn('http://127.0.0.1:8080%s/' % base, read('Dockerfile'))
        self.assertIn('location = %s {' % base, read('nginx-proxy.conf'))

    def test_the_deploy_folder_holds_the_files_of_the_plan_and_no_caddy(self):
        self.assertEqual(deploy.deploy_files(c_Deploy), ['Dockerfile', 'Dockerfile.build', 'README.md', 'deploy-files.sh',
                                                        'nginx-container.conf', 'nginx-http.conf', 'nginx-proxy.conf', 'nginx.conf'])
        for name in deploy.deploy_files(c_Deploy):
            self.assertNotRegex(read(name), r'(?i)caddy', name)
        self.assertIn('FROM nginxinc/nginx-unprivileged:1.30.6-alpine', read('Dockerfile'))
        self.assertTrue(read('nginx.conf').startswith('# The Strata Engine Book under /strata-engine-docs/, tested with nginx 1.20.1 and 1.30.6.'))

    def test_no_file_of_the_site_names_caddy(self):
        # plan/site.md, "The spike against this file", item 16: nginx is the one server, in every file of the tree.
        # The tests that check this name it, and tools/data's word lists hold the word "caddy" as a verb.
        paths = [os.path.join(c_Root, name) for name in ('astro.config.mjs', 'ec.config.mjs', 'package.json', 'README.md', '.dockerignore',
                                                         '.gitignore', 'site.json')]
        paths += [os.path.join(c_Root, 'tools', name) for name in ('crawl.py', 'servertest.py', 'release.py', 'budgets.py', 'measure.py',
                                                                   'bootstrap.py', 'toolchain.json', 'deployfiles.py', 'booklib/deploy.py')]
        for folder in ('src', 'scripts', 'deploy', '.github'):
            for parent, _, names in os.walk(os.path.join(c_Root, folder)):
                paths += [os.path.join(parent, name) for name in names if os.path.splitext(name)[1] in
                          ('.mjs', '.js', '.ts', '.astro', '.json', '.md', '.css', '.yml', '.sh', '.conf', '')]
        found = []
        for path in paths:
            if os.path.isfile(path):
                with open(path, encoding='utf-8', errors='replace') as file:
                    if re.search(r'(?i)\bcaddy', file.read()):
                        found.append(os.path.relpath(path, c_Root))
        self.assertEqual(found, [])

    def test_a_generated_file_in_deploy_is_refused(self):
        folder = tempfile.mkdtemp(prefix='deploy-generated-')
        try:
            for name in ('nginx.conf', 'nginx-csp.conf'):
                open(os.path.join(folder, name), 'w').close()
            with self.assertRaisesRegex(ValueError, 'nginx-csp.conf, which the release step writes'):
                deploy.deploy_files(folder)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_the_copy_script_is_executable_in_the_repository(self):
        listed = subprocess.run(['git', '-C', c_Root, 'ls-files', '-s', 'deploy/deploy-files.sh'], stdout=subprocess.PIPE, text=True).stdout
        if listed:
            self.assertTrue(listed.startswith('100755 '), listed)


class DeployFilesTests(unittest.TestCase):
    def test_another_prefix_replaces_every_occurrence_and_keeps_the_redirect(self):
        for name in deployfiles.written_files():
            text = deploy.for_base(read(name), '/docs/strata', name)
            self.assertNotRegex(text, r'/strata-engine-docs(?![-.\w])', name)
        # File names that hold the prefix's words stay: the container includes its snippet by name.
        self.assertIn('include /etc/nginx/snippets/strata-engine-docs.conf;', deploy.for_base(read('nginx-container.conf'), '/docs/strata'))
        self.assertIn('location = /docs/strata {', deploy.for_base(read('nginx.conf'), '/docs/strata'))
        self.assertIn('location = /docs/strata {', deploy.for_base(read('nginx-proxy.conf'), '/docs/strata'))
        docker = deploy.for_base(read('Dockerfile'), '/docs/strata', 'Dockerfile')
        self.assertIn('COPY --chown=101:101 docs/strata/ /srv/www/docs/strata/', docker)
        self.assertIn('http://127.0.0.1:8080/docs/strata/', docker)
        self.assertIn('-t strata-engine-docs:<tag>', docker)
        self.assertEqual(deploy.for_base(read('nginx.conf'), deploy.c_CommittedPrefix), read('nginx.conf'))

    def test_the_root_of_a_host_drops_the_redirect_and_the_outside_blocks(self):
        nginx = deploy.for_base(read('nginx.conf'), '')
        proxy = deploy.for_base(read('nginx-proxy.conf'), '')
        container = deploy.for_base(read('nginx-container.conf'), '')
        # Replacing the prefix alone would leave "location =  {", which nginx refuses.
        self.assertNotIn('location =  {', nginx)
        self.assertNotIn('return 301', nginx)
        self.assertIn('location ^~ / {', nginx)
        self.assertIn('error_page 403 404 =404 /404.html;', nginx)
        self.assertNotIn('return 301', proxy)
        self.assertIn('location ^~ / {', proxy)
        self.assertNotIn('return 404;', container)
        docker = deploy.for_base(read('Dockerfile'), '', 'Dockerfile')
        self.assertIn('COPY --chown=101:101 site/ /srv/www/', docker)
        self.assertIn('http://127.0.0.1:8080/ ', docker)
        self.assertEqual(deploy.top_folder(''), 'site')
        self.assertEqual(deploy.top_folder('/x/y'), 'x/y')

    def test_unpaired_markers_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'without its'):
            deploy.for_base('a\n# (redirect: begin)\nb\n', '')
        with self.assertRaisesRegex(ValueError, 'without its'):
            deploy.for_base('a\n# (outside: end)\n', '')
        with self.assertRaisesRegex(ValueError, 'the base must be'):
            deploy.for_base('x', '/a b')

    def test_deployfiles_writes_every_file_but_the_readme(self):
        out = tempfile.mkdtemp(prefix='deployfiles-')
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(deployfiles.main(['--base=/', '--out', out]), 0)
            self.assertEqual(sorted(os.listdir(out)), sorted(name for name in deploy.deploy_files(c_Deploy) if name != 'README.md'))
            with open(os.path.join(out, 'nginx-http.conf'), encoding='utf-8') as file:
                self.assertIn('~^/_astro/', file.read())
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(deployfiles.main(['--base=/x', '--out', c_Deploy]), 2)
        finally:
            shutil.rmtree(out, ignore_errors=True)


class StaticCheckTests(unittest.TestCase):
    def test_the_deploy_files_pass_their_static_checks(self):
        self.assertEqual(servertest.static_problems(), [])

    def test_the_static_checks_find_alias_nested_add_header_without_always_hsts_and_a_proxy_path(self):
        folder = tempfile.mkdtemp(prefix='deploy-static-')
        try:
            with open(os.path.join(folder, 'bad.conf'), 'w', encoding='utf-8') as file:
                file.write('location ^~ /b/ {\n\tadd_header A b always;\n\tlocation ~ "\\.x{2}$" { add_header B c always; }\n\talias /srv/b/;\n}\n'
                           'location /p/ { proxy_pass http://127.0.0.1:8080/p/; }\n'
                           'location /q/ {\n\tadd_header C d;\n\tadd_header Strict-Transport-Security "max-age=1" always;\n}\n')
            problems = '\n'.join(servertest.static_problems(folder))
            self.assertIn('bad.conf:3: add_header inside a nested location', problems)
            self.assertNotIn('bad.conf:2:', problems)
            self.assertIn('bad.conf:4: "alias"', problems)
            self.assertIn('bad.conf:6: proxy_pass with a path', problems)
            self.assertIn('bad.conf:8: an add_header of the book carries "always"', problems)
            self.assertIn('bad.conf:9: the book sends no Strict-Transport-Security', problems)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_the_final_stage_of_a_dockerfile_copies_only_the_site_and_nginx_s_files(self):
        # rulings 6, R22 and R26: no node_modules, nothing that only builds or tests.
        self.assertEqual(servertest.dockerfile_problems('Dockerfile', read('Dockerfile')), [])
        self.assertEqual(servertest.dockerfile_problems('Dockerfile.build', read('Dockerfile.build')), [])
        bad = ('FROM node:26 AS build\nCOPY . .\nRUN npm ci\nFROM nginx\nCOPY deploy/nginx.conf /etc/nginx/x.conf\n'
               'COPY --from=build /book/node_modules /srv/www/node_modules\nCOPY . /srv/www/\nADD site.tar /srv/www/\n'
               'COPY --from=build /book/dist/ \\\n  /srv/www/strata-engine-docs/\nCOPY deploy/README.md /etc/nginx/README.md\nCOPY deploy/nginx.conf /app/nginx.conf\n')
        problems = '\n'.join(servertest.dockerfile_problems('Bad', bad))
        self.assertNotIn('Bad:3:', problems)  # the build stage may copy anything
        self.assertNotIn('Bad:5:', problems)
        self.assertIn('Bad:6: the final stage copies /book/node_modules', problems)
        self.assertIn('Bad:7: the final stage copies .', problems)
        self.assertIn('Bad:8: ADD in the final stage', problems)
        self.assertIn('Bad:9: the final stage copies /book/dist/', problems)
        self.assertIn('Bad:11: the final stage copies deploy/README.md', problems)
        self.assertIn('Bad:12: the final stage copies deploy/nginx.conf to /app/nginx.conf', problems)


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp(prefix='servertest-config-')

    def tearDown(self):
        shutil.rmtree(self.work, ignore_errors=True)

    def deploy_folder(self, base):
        folder = os.path.join(self.work, 'deploy')
        os.makedirs(folder, exist_ok=True)
        for name in deploy.deploy_files(c_Deploy):
            with open(os.path.join(folder, name), 'w', encoding='utf-8') as file:
                file.write(deploy.for_base(read(name), base, name))
        for name in deploy.c_GeneratedFiles:
            open(os.path.join(folder, name), 'w').close()
        return folder

    def built_site(self, base):
        site = os.path.join(self.work, 'built')
        for relative, text in (('index.html', '<link rel="canonical" href="https://example.com%s/"><link rel="stylesheet" href="%s/_astro/a.css">' % (base, base)),
                               ('404.html', '<p>not found'), ('_astro/a.css', 'a{}')):
            path = os.path.join(site, *relative.split('/'))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(text)
        return site

    def layout(self, kind, base, **options):
        out = os.path.join(self.work, 'layout-%s%s' % (kind, base.replace('/', '-')))
        server = servertest.write_layout(kind, self.deploy_folder(base), self.built_site(base), base, out, **options)
        return out, server

    def text(self, *parts):
        with open(os.path.join(*parts), encoding='utf-8') as file:
            return file.read()

    def files(self, folder):
        found = []
        for parent, _, names in os.walk(folder):
            found += [os.path.relpath(os.path.join(parent, name), folder).replace(os.sep, '/') for name in names]
        return sorted(found)

    def test_the_copied_layout_puts_the_files_where_deploy_readme_says_for_ci_s_official_image(self):
        out, server = self.layout('copied', '/x/y', host_headers=True)
        self.assertEqual(server, os.path.join(out, 'etc', 'nginx', 'conf.d', 'default.conf'))
        self.assertEqual(self.files(out), ['etc/nginx/conf.d/default.conf', 'etc/nginx/conf.d/strata-engine-docs-http.conf',
                                           'etc/nginx/snippets/strata-engine-docs-csp.conf', 'etc/nginx/snippets/strata-engine-docs-host-headers.conf',
                                           'etc/nginx/snippets/strata-engine-docs-redirects.conf', 'etc/nginx/snippets/strata-engine-docs.conf',
                                           'srv/host/404.html', 'srv/host/index.html', 'srv/www/x/y/404.html', 'srv/www/x/y/_astro/a.css',
                                           'srv/www/x/y/index.html'])
        # CI's container mounts these folders at /etc/nginx/ and /srv/: the files keep the paths deploy/README.md gives.
        self.assertEqual(self.text(out, 'etc', 'nginx', 'snippets', 'strata-engine-docs.conf'), deploy.for_base(read('nginx.conf'), '/x/y'))
        self.assertEqual(self.text(out, 'etc', 'nginx', 'conf.d', 'strata-engine-docs-http.conf'), deploy.for_base(read('nginx-http.conf'), '/x/y'))
        host = self.text(server)
        for line in ('listen 80;', 'add_header X-Frame-Options "SAMEORIGIN";', 'add_header X-Content-Type-Options "nosniff";', 'expires 1h;',
                     servertest.c_HostileLocation, 'root /srv/host;', 'include /etc/nginx/snippets/strata-engine-docs.conf;'):
            self.assertIn('\t%s\n' % line, host)
        self.assertEqual(self.text(out, 'etc', 'nginx', 'snippets', 'strata-engine-docs-host-headers.conf'),
                         'add_header Strict-Transport-Security "max-age=300" always;\n')
        # A book at the root of a host is the whole server: the host keeps no site of its own beside it.
        out, server = self.layout('copied', '')
        self.assertNotIn('root /srv/host;', self.text(server))
        self.assertNotIn('srv/host/index.html', self.files(out))
        self.assertIn('srv/www/index.html', self.files(out))

    def test_the_container_layouts_follow_deploy_dockerfile_s_copies(self):
        out, server = self.layout('container', '/x/y')
        self.assertEqual(self.files(out), ['etc/nginx/conf.d/00-strata-engine-docs-http.conf', 'etc/nginx/conf.d/default.conf',
                                           'etc/nginx/snippets/strata-engine-docs-csp.conf', 'etc/nginx/snippets/strata-engine-docs-redirects.conf',
                                           'etc/nginx/snippets/strata-engine-docs.conf', 'srv/www/x/y/404.html', 'srv/www/x/y/_astro/a.css',
                                           'srv/www/x/y/index.html'])
        self.assertEqual(self.text(server), deploy.for_base(read('nginx-container.conf'), '/x/y'))
        out, server = self.layout('container', '', listen='127.0.0.1:4321')
        self.assertIn('srv/www/index.html', self.files(out))
        self.assertIn('\tlisten 127.0.0.1:4321;\n', self.text(server))
        out, server = self.layout('hostile', '/x/y')
        hostile = self.text(server)
        self.assertIn('\tlisten 8080;\n', hostile)
        self.assertEqual(hostile.count(servertest.c_HostileLocation), 1)
        self.assertLess(hostile.index('include /etc/nginx/snippets/strata-engine-docs.conf;'), hostile.index(servertest.c_HostileLocation))
        self.assertLess(hostile.index(servertest.c_HostileLocation), hostile.index('return 404;'))
        with self.assertRaisesRegex(ValueError, 'exactly once'):
            servertest.with_hostile_location('server {\n\tlisten 8080;\n}\n')

    def test_the_proxy_layout_forwards_to_the_container_from_a_host_with_a_site_of_its_own(self):
        out, server = self.layout('proxy', '/x/y', listen='127.0.0.1:8090', upstream='127.0.0.1:4322', host_headers=True)
        self.assertEqual(self.files(out), ['etc/nginx/conf.d/default.conf', 'etc/nginx/snippets/strata-engine-docs-host-headers.conf',
                                           'etc/nginx/snippets/strata-engine-docs-proxy.conf', 'srv/host/404.html', 'srv/host/index.html'])
        proxy = self.text(out, 'etc', 'nginx', 'snippets', 'strata-engine-docs-proxy.conf')
        self.assertIn('proxy_pass http://127.0.0.1:4322;', proxy)
        self.assertIn('location ^~ /x/y/ {', proxy)
        host = self.text(server)
        self.assertIn('\tlisten 127.0.0.1:8090;\n', host)
        self.assertIn('\tinclude /etc/nginx/snippets/strata-engine-docs-proxy.conf;\n', host)
        self.assertIn('\tadd_header X-Frame-Options "SAMEORIGIN";\n', host)
        # Without an upstream the proxy forwards where deploy/README.md runs the container.
        out, _ = self.layout('proxy', '')
        self.assertIn('proxy_pass http://127.0.0.1:8080;', self.text(out, 'etc', 'nginx', 'snippets', 'strata-engine-docs-proxy.conf'))

    def test_moved_layouts_name_the_work_folder_for_this_tool_s_own_runs(self):
        # The work folder's own path may hold the prefix (the clone's name): only /etc/nginx/, /srv/www and /srv/host move.
        site = self.built_site('/x/y')
        out = os.path.join(self.work, 'strata-engine-docs')
        server = servertest.write_layout('copied', self.deploy_folder('/x/y'), site, '/x/y', out, listen='127.0.0.1:4321', move=True)
        etc = servertest.forward(os.path.join(out, 'etc', 'nginx'))
        rules = self.text(out, 'etc', 'nginx', 'snippets', 'strata-engine-docs.conf')
        self.assertIn('root %s;' % servertest.forward(os.path.join(out, 'srv', 'www')), rules)
        self.assertIn('location ^~ /x/y/ {', rules)
        self.assertIn('include %s/snippets/strata-engine-docs-csp.conf;' % etc, rules)
        self.assertIn('include %s/snippets/strata-engine-docs-host-headers*.conf;' % etc, rules)
        host = self.text(server)
        self.assertIn('\troot %s;\n' % servertest.forward(os.path.join(out, 'srv', 'host')), host)
        self.assertIn('\tinclude %s/snippets/strata-engine-docs.conf;\n' % etc, host)
        self.assertEqual(servertest.conf_d(out), ['include %s/conf.d/*.conf;' % etc])

    def test_a_layout_refuses_an_unknown_kind_and_host_headers_in_the_container(self):
        site = self.built_site('/x/y')
        with self.assertRaisesRegex(ValueError, 'a layout is one of copied, container, hostile, proxy'):
            servertest.write_layout('caddy', self.deploy_folder('/x/y'), site, '/x/y', os.path.join(self.work, 'a'))
        with self.assertRaisesRegex(ValueError, 'belongs to a host'):
            servertest.write_layout('hostile', self.deploy_folder('/x/y'), site, '/x/y', os.path.join(self.work, 'b'), host_headers=True)

    def test_the_layout_command_writes_a_release_s_files_into_a_new_folder(self):
        for base in ('', '/strata-engine-docs', '/x/y'):
            site = os.path.join(self.work, 'site' + base.replace('/', '-'))
            shutil.move(self.built_site(base), site)
            folder, _ = release.assemble(site, base, 'main-0123abcd', os.path.join(self.work, 'release' + base.replace('/', '-')), c_Deploy)
            out = os.path.join(self.work, 'out' + base.replace('/', '-'))
            with contextlib.redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(servertest.main(['layout', '--kind', 'copied', '--release', folder, '--out', out, '--host-headers']), 0)
            self.assertIn('wrote the copied server for the base %s' % (base or '/'), printed.getvalue())
            self.assertTrue(os.path.isfile(os.path.join(out, 'srv', 'www', *[part for part in base.split('/') if part], 'index.html')))
            self.assertTrue(os.path.isfile(os.path.join(out, 'etc', 'nginx', 'snippets', 'strata-engine-docs-host-headers.conf')))
            self.assertIn('include /etc/nginx/snippets/strata-engine-docs.conf;', self.text(out, 'etc', 'nginx', 'conf.d', 'default.conf'))
            # A folder that holds something is never written into.
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(servertest.main(['layout', '--kind', 'proxy', '--release', folder, '--out', out]), 2)
            self.assertIn('is not a new or empty folder', errors.getvalue())

    def test_the_plan_s_form_of_a_running_server_is_the_url_command(self):
        # plan/site.md writes "python tools/servertest.py --url <address>"; it reaches the url command's checks.
        for argv in (['--url', 'ftp://127.0.0.1/b/'], ['--url=ftp://127.0.0.1/b/']):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(servertest.main(argv), 2)
            self.assertIn('--url is an http or https address', errors.getvalue())

    def test_url_waits_for_a_server_that_is_starting_and_fails_when_none_answers(self):
        # CI starts a container and checks it at once: --wait gives it the seconds it needs, and no more.
        port = servertest.free_port()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(servertest.main(['url', '--wait', '1', '--url', 'http://127.0.0.1:%d/b/' % port]), 2)
        self.assertIn('http://127.0.0.1:%d/b/ did not answer within 1 seconds' % port, errors.getvalue())

    def test_the_host_server_has_its_own_site_headers_and_hostile_location(self):
        lines = '\n'.join(servertest.host_server('127.0.0.1:8080', '/etc/nginx', '/srv/host', '/b', 'strata-engine-docs.conf'))
        self.assertIn('listen 127.0.0.1:8080;', lines)
        self.assertIn('add_header X-Frame-Options "SAMEORIGIN";', lines)
        self.assertIn('add_header X-Content-Type-Options "nosniff";', lines)
        self.assertIn('expires 1h;', lines)
        self.assertIn('return 418;', lines)
        self.assertIn('error_page 404 /404.html;', lines)
        self.assertIn('include /etc/nginx/snippets/strata-engine-docs.conf;', lines)
        # A book at the root of the host is the whole server: the host keeps no site of its own beside it.
        self.assertNotIn('error_page', '\n'.join(servertest.host_server('80', '/etc/nginx', '/srv/host', '', 'x.conf')))


class Handler(http.server.BaseHTTPRequestHandler):
    """A small server with the headers deploy/nginx.conf promises, which a test spoils one at a time."""

    answers = {}
    protocol_version = 'HTTP/1.1'

    def log_message(self, *arguments):
        pass

    def do_GET(self):  # noqa: N802 (http.server's name)
        path = self.path.split('?')[0]
        status, headers, body = self.answers.get(path) or self.answers.get('*missing*' if path.startswith('/b/') else '*outside*')
        self.send_response(status)
        for name, value in headers:
            self.send_header(name, value)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class HeaderCheckTests(unittest.TestCase):
    c_Book = [('Content-Security-Policy', "default-src 'self'"), ('X-Content-Type-Options', 'nosniff'),
              ('Referrer-Policy', 'strict-origin-when-cross-origin'), ('X-Frame-Options', 'SAMEORIGIN')]

    def setUp(self):
        self.site = tempfile.mkdtemp(prefix='servertest-headers-')
        for relative, content in (('index.html', b'<p>home'), ('404.html', b'<p>not found'), ('core/time/index.html', b'<p>time'),
                                  ('_astro/a.css', b'a{}'), ('manifest.webmanifest', b'{}')):
            path = os.path.join(self.site, *relative.split('/'))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as file:
                file.write(content)
        page = [('Content-Type', 'text/html; charset=utf-8'), ('Cache-Control', 'no-cache'), ('Content-Encoding', 'gzip')]
        missing = [('Content-Type', 'text/html; charset=utf-8'), ('Cache-Control', 'no-cache')]
        answers = {
            '/b': (301, [('Location', '/b/')], b''),
            '/b/': (200, page + self.c_Book, b'<p>home'),
            '/b/core/time': (301, [('Location', '/b/core/time/')] + self.c_Book, b''),
            '/b/core/time/': (200, page + self.c_Book, b'<p>time'),
            '/b/_astro/a.css': (200, [('Content-Type', 'text/css'), ('Cache-Control', servertest.c_Immutable)] + self.c_Book, b'a{}'),
            '/b/manifest.webmanifest': (200, [('Content-Type', 'application/manifest+json'), ('Cache-Control', 'no-cache')] + self.c_Book, b'{}'),
            '*missing*': (404, missing + self.c_Book, b'<p>not found'),
            '*outside*': (404, [('Content-Type', 'text/html')], b'<p>the host\'s own 404 page'),
        }
        self.handler = type('TestHandler', (Handler,), {'answers': answers})
        self.server = socketserver.ThreadingTCPServer(('127.0.0.1', 0), self.handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.start = 'http://127.0.0.1:%d/b/' % self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        shutil.rmtree(self.site, ignore_errors=True)

    def check(self, **options):
        return servertest.header_checks(self.start, self.site, '/b', **options)

    def test_a_server_that_keeps_every_promise_passes(self):
        self.assertEqual(self.check(policy="default-src 'self'", forbid_header='strict-transport-security'), [])

    def test_a_header_twice_a_missing_header_another_policy_and_a_host_header_fail(self):
        answers = self.handler.answers
        answers['/b/core/time/'] = (200, answers['/b/core/time/'][1] + [('X-Frame-Options', 'DENY')], b'<p>time')
        answers['*missing*'] = (404, [(name, value) for name, value in answers['*missing*'][1] if name != 'Referrer-Policy'], b'<p>not found')
        problems = '\n'.join(self.check(policy="default-src 'none'", host_header=('strict-transport-security', 'max-age=300')))
        self.assertIn('/b/core/time/ (200) has x-frame-options 2 times: SAMEORIGIN | DENY', problems)
        self.assertIn('/b/a/b/c/ (404) has no referrer-policy', problems)
        self.assertIn("sends another policy than the release's nginx-csp.conf", problems)
        self.assertIn("has strict-transport-security []: the host-headers file sends 'max-age=300' once", problems)

    def test_redirects_caching_types_and_the_404_page_are_checked(self):
        answers = self.handler.answers
        answers['/b'] = (308, [('Location', 'http://127.0.0.1:8080/b/')], b'')
        answers['/b/_astro/a.css'] = (200, [('Content-Type', 'application/octet-stream'), ('Cache-Control', 'max-age=60')] + self.c_Book, b'a{}')
        answers['/b/'] = (200, [('Content-Type', 'text/html'), ('Cache-Control', 'no-cache'), ('Cache-Control', 'max-age=3600')] + self.c_Book, b'<p>home')
        answers['*missing*'] = (404, [('Cache-Control', servertest.c_Immutable)] + self.c_Book, b'nginx')
        answers['*outside*'] = (200, [('Content-Type', 'text/html')], b'<p>Welcome to nginx')
        problems = '\n'.join(self.check(container=True))
        self.assertIn("/b answers 308 with Location ['http://127.0.0.1:8080/b/']: it must answer 301 with the path /b/", problems)
        self.assertIn('_astro/a.css is not cached as immutable', problems)
        self.assertIn("_astro/a.css is served as 'application/octet-stream'", problems)
        self.assertIn("/b/ answers 200 as 'text/html': a page is text/html; charset=utf-8", problems)
        self.assertIn('/b/ (200) has Cache-Control more than once', problems)
        self.assertIn("/b/a/b/c/ (a missing page) answers 404 without the book's 404 page", problems)
        self.assertIn('answers its 404 as immutable', problems)
        self.assertIn('outside the prefix, answers', problems)


class ProcessTreeTests(unittest.TestCase):
    def test_stop_ends_the_program_and_what_it_started(self):
        # A program that starts a child of its own, as nginx's master starts its worker, and waits.
        work = tempfile.mkdtemp(prefix='servertest-tree-')
        try:
            script = os.path.join(work, 'parent.py')
            with open(script, 'w', encoding='utf-8') as file:
                file.write('import subprocess, sys, time\n'
                           'child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])\n'
                           'open(sys.argv[1], "w").write(str(child.pid))\n'
                           'time.sleep(120)\n')
            marker = os.path.join(work, 'child.pid')
            server = servertest.Server('test', [sys.executable, '-I', script, marker], work, os.path.join(work, 'log.txt'))
            def written():
                if not os.path.isfile(marker):
                    return ''
                with open(marker, encoding='utf-8') as file:
                    return file.read()
            for _ in range(100):
                if written():
                    break
                threading.Event().wait(0.1)
            child = int(written())
            self.assertEqual(server.stop(), [])
            self.assertIsNotNone(server.process.poll())
            if os.name == 'nt':
                self.assertNotIn(child, servertest.windows_processes())
            else:
                with self.assertRaises(ProcessLookupError):
                    os.kill(child, 0)
        finally:
            shutil.rmtree(work, ignore_errors=True)


@unittest.skipUnless(shutil.which('sh'), 'needs a POSIX shell (CI runs it on Linux)')
class RuntimeGateTests(unittest.TestCase):
    """--runtime: gate (b), scripts/runtime.mjs, through each served run (plan/site.md, "(b) Runtime")."""

    def test_the_runtime_check_runs_through_the_server_with_the_served_build(self):
        calls = []
        real = servertest.subprocess.run

        def fake(command, cwd=None):
            calls.append(command)
            return subprocess.CompletedProcess(command, len(calls) - 1)
        servertest.subprocess.run = fake
        try:
            self.assertEqual(servertest.runtime_problems('node', 'http://127.0.0.1:1/docs/', '/srv/site'), [])
            self.assertEqual(servertest.runtime_problems('node', 'http://127.0.0.1:1/docs/', '/srv/site'),
                             ['the runtime check (gate (b)) failed (its problems are above)'])
        finally:
            servertest.subprocess.run = real
        self.assertEqual(calls[0], ['node', os.path.join(c_Root, 'scripts', 'runtime.mjs'), '--url', 'http://127.0.0.1:1/docs/', '--dist', '/srv/site'])

    def test_a_node_that_does_not_start_is_a_problem(self):
        problems = servertest.runtime_problems(os.path.join(c_Root, 'no-such-node-program'), 'http://127.0.0.1:1/', '/srv/site')
        self.assertEqual(len(problems), 1)
        self.assertIn('the runtime check (gate (b)) did not start', problems[0])

    def test_both_commands_take_runtime(self):
        for command in ('nginx', 'url'):
            with contextlib.redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit):
                servertest.main([command, '--help'])
            self.assertIn('--runtime', out.getvalue())


class DeployFilesScriptTests(unittest.TestCase):
    """deploy/deploy-files.sh: pass 1 copies without deleting, pass 2 deletes but keeps archived versions (requirement
    9). A stand-in rsync first on the PATH records each pass's arguments and what the served folder holds after it."""

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='deploy-copy-')
        self.new = os.path.join(self.folder, 'new')
        self.served = os.path.join(self.folder, 'served')
        files = {
            'new': {'index.html': 'new page', '_astro/new.css': 'new', 'core/time/index.html': 'time'},
            'served': {'index.html': 'old page', '_astro/old.css': 'old', 'v0.7/index.html': 'archive', 'versions.json': '[]'},
        }
        for top, entries in files.items():
            for relative, text in entries.items():
                path = os.path.join(self.folder, top, *relative.split('/'))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8', newline='\n') as file:
                    file.write(text)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def served_files(self):
        found = []
        for folder, _, names in os.walk(self.served):
            for name in names:
                found.append(os.path.relpath(os.path.join(folder, name), self.served).replace(os.sep, '/'))
        return sorted(found)

    def run_script(self, *arguments, path=None):
        environment = dict(os.environ)
        # Git for Windows' shell turns an argument that starts with / into a Windows path when it starts a native
        # program (the stand-in's Python): /versions.json would arrive as C:/.../versions.json. rsync is no native
        # program there, and Linux turns nothing.
        environment['MSYS2_ARG_CONV_EXCL'] = '*'
        if path is not None:
            environment['PATH'] = path
        return subprocess.run(['sh', os.path.join(c_Deploy, 'deploy-files.sh')] + list(arguments), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, env=environment)

    def stand_in(self, real):
        """A folder with an rsync that logs its arguments and the served files after each call, then runs `real`."""
        folder = os.path.join(self.folder, 'bin')
        os.makedirs(folder)
        log = os.path.join(self.folder, 'rsync.log')
        record = os.path.join(self.folder, 'record.py')
        with open(record, 'w', encoding='utf-8') as file:
            file.write('import os, sys\nlog, served = sys.argv[1], sys.argv[2]\nfiles = sorted(os.path.relpath(os.path.join(f, n), served).replace(os.sep, "/") '
                       'for f, _, ns in os.walk(served) for n in ns)\nopen(log, "a").write(" ".join(sys.argv[3:]) + "\\n" + ",".join(files) + "\\n")\n')
        script = os.path.join(folder, 'rsync')
        with open(script, 'w', encoding='utf-8', newline='\n') as file:
            run = '"%s" "$@" || exit $?\n' % real.replace('\\', '/') if real else ''
            file.write('#!/bin/sh\n%s"%s" "%s" "%s" "%s" "$@"\n' % (run, sys.executable.replace('\\', '/'), record.replace('\\', '/'), log.replace('\\', '/'), self.served.replace('\\', '/')))
        os.chmod(script, os.stat(script).st_mode | stat.S_IEXEC)
        return folder, log

    def test_the_script_makes_two_passes_with_the_plan_s_arguments(self):
        folder, log = self.stand_in(None)
        result = self.run_script(self.new, self.served, path=folder.replace('\\', '/') + os.pathsep + os.environ.get('PATH', ''))
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', 'replace'))
        with open(log, encoding='utf-8') as file:
            lines = file.read().split('\n')
        new = self.new.replace('\\', '/') + '/'
        served = self.served.replace('\\', '/') + '/'
        calls = [line.replace('\\', '/') for line in lines[0::2] if line]
        self.assertEqual(len(calls), 2)
        self.assertTrue(calls[0].endswith('-a %s %s' % (new, served)) or calls[0] == '-a %s %s' % (new, served), calls[0])
        self.assertIn("-a --delete --exclude /v[0-9]*/ --exclude /versions.json", calls[1])

    # CI's serve-test job installs rsync and runs this test as requirement 9's two-pass copy test: there a missing
    # rsync is a failure, never a reason to skip.
    @unittest.skipUnless(shutil.which('rsync') or os.environ.get('CI'), 'needs rsync (CI\'s ubuntu runner has it)')
    def test_pass_1_keeps_the_stale_file_and_pass_2_removes_it_but_not_the_archive(self):
        self.assertIsNotNone(shutil.which('rsync'), 'requirement 9 copies with the real rsync: install it')
        folder, log = self.stand_in(shutil.which('rsync'))
        result = self.run_script(self.new, self.served, path=folder + os.pathsep + os.environ.get('PATH', ''))
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', 'replace'))
        with open(log, encoding='utf-8') as file:
            after = [line.split(',') for line in file.read().split('\n')[1::2] if line]
        self.assertIn('_astro/old.css', after[0])
        self.assertIn('_astro/new.css', after[0])
        self.assertNotIn('_astro/old.css', after[1])
        self.assertIn('v0.7/index.html', after[1])
        self.assertIn('versions.json', after[1])
        self.assertEqual(self.served_files(), ['_astro/new.css', 'core/time/index.html', 'index.html', 'v0.7/index.html', 'versions.json'])

    def test_the_script_refuses_wrong_arguments(self):
        folder, _ = self.stand_in(None)
        path = folder.replace('\\', '/') + os.pathsep + os.environ.get('PATH', '')
        for arguments in ([self.new], [os.path.join(self.folder, 'none'), self.served], [self.new, self.new]):
            result = self.run_script(*arguments, path=path)
            self.assertEqual(result.returncode, 2, result.stdout.decode('utf-8', 'replace'))


if __name__ == '__main__':
    unittest.main()
