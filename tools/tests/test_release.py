"""tools/release.py and the release pieces of booklib/deploy.py (plan/site.md, "What a release holds" and "Moved
pages"): the tag, the checks of the built site, the Content Security Policy from the built HTML, the moved pages'
server rules, the reproducible tarballs and SHA256SUMS, the files rewritten for another base, and the layout that
deploy/Dockerfile.build copies, at the bases /, /strata-engine-docs and /x/y."""

import contextlib
import gzip
import hashlib
import io
import os
import re
import shutil
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
import release
from booklib import deploy

c_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c_Deploy = os.path.join(c_Root, 'deploy')
c_Big = 'x' * 2048
c_Bases = (('', '/'), ('/strata-engine-docs', '/strata-engine-docs'), ('/x/y', '/x/y'))


def write(path, content, mode='w'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, **({} if 'b' in mode else {'encoding': 'utf-8', 'newline': '\n'})) as file:
        file.write(content)


def moved_page(base, target):
    return ('<!doctype html><html><head><meta name="robots" content="noindex"><meta name="strata-book-moved" content="%s">'
            '<link rel="canonical" href="https://example.com%s"><meta http-equiv="refresh" content="0; url=%s"></head>'
            '<body><a href="%s">Time</a></body></html>' % (target, target, target, target))


def make_site(folder, base, notices=True, gzipped=True):
    """A small built site for `base`: two pages with inline scripts, a 404 page, a style sheet, Pagefind's files, a
    moved page and (unless told) the two notices, with a .gz beside every text file of 1 KB or more."""
    files = {
        'index.html': '<link rel="stylesheet" href="%s/_astro/a.css"><script>theme()</script><script type="module">import "./x.js"</script>'
                      '<script type="application/json">{"data": 1}</script><script src="%s/_astro/p.js"></script>%s' % (base, base, c_Big),
        '404.html': '<link rel="stylesheet" href="%s/_astro/a.css"><script>theme()</script>' % base,
        'core/time/index.html': '<script>\nsidebar();\n</script>' + c_Big,
        'core/old/index.html': moved_page(base, base + '/core/time/'),
        '_astro/a.css': c_Big,
        '_astro/small.js': 'x',
        'pagefind/pagefind.js': c_Big,
        'pagefind/index/en_1.pf_index': c_Big,
    }
    if notices:
        files['license.txt'] = 'Copyright'
        files['third-party-notices.txt'] = c_Big
    for relative, content in files.items():
        write(os.path.join(folder, *relative.split('/')), content)
        if gzipped and os.path.splitext(relative)[1] in release.c_TextExtensions and len(content) >= 1024:
            write(os.path.join(folder, *relative.split('/')) + '.gz', gzip.compress(content.encode('utf-8')), 'wb')
    return folder


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp(prefix='release-test-')

    def tearDown(self):
        shutil.rmtree(self.work, ignore_errors=True)

    def test_a_tag_is_a_release_or_a_build(self):
        self.assertEqual(release.check_tag('book-v0.8.1-r1'), 'release')
        self.assertEqual(release.check_tag('main-0123abcd'), 'build')
        for bad in ('v0.8.1', 'book-v0.8-r1', 'book-v0.8.1-r0', 'main-0123ABCD', 'main-0123abc', 'main-0123abcde'):
            with self.assertRaises(release.ReleaseError):
                release.check_tag(bad)

    def test_the_text_files_agree_with_scripts_precompress(self):
        with open(os.path.join(c_Root, 'scripts', 'precompress.mjs'), encoding='utf-8') as file:
            text = file.read()
        listed = re.search(r'c_Extensions = \[([^\]]*)\]', text).group(1)
        self.assertEqual(tuple(re.findall(r"'([^']+)'", listed)), release.c_TextExtensions)
        self.assertIn('c_MinimumBytes = %d;' % release.c_MinimumGzipBytes, text)

    def test_the_built_site_is_checked_before_it_is_packed(self):
        site = make_site(os.path.join(self.work, 'site'), '/b')
        self.assertEqual(release.site_problems(site, '/b', 'release'), ([], []))
        problems, _ = release.site_problems(site, '/other', 'build')
        self.assertIn('was not built for the base /other', '\n'.join(problems))
        os.remove(os.path.join(site, '_astro', 'a.css.gz'))
        write(os.path.join(site, 'pagefind', 'pagefind.js.gz'), gzip.compress(b'stale'), 'wb')
        write(os.path.join(site, 'index.html.br'), b'br', 'wb')
        write(os.path.join(site, '_astro', 'small.js.gz'), gzip.compress(b'x'), 'wb')
        problems = '\n'.join(release.site_problems(site, '/b', 'build')[0])
        self.assertIn('_astro/a.css has no .gz beside it: run node scripts/precompress.mjs', problems)
        self.assertIn('pagefind/pagefind.js.gz does not hold pagefind/pagefind.js', problems)
        self.assertIn('index.html.br: a release holds no .br file', problems)
        self.assertIn('_astro/small.js.gz: a .gz beside no text file of 1 KB or more', problems)

    def test_the_notices_are_required_by_a_release_and_noted_for_a_build(self):
        site = make_site(os.path.join(self.work, 'site'), '/b', notices=False)
        problems, notes = release.site_problems(site, '/b', 'release')
        self.assertEqual(len(problems), 2)
        self.assertIn('the site has no license.txt at its top', problems[0])
        problems, notes = release.site_problems(site, '/b', 'build')
        self.assertEqual(problems, [])
        self.assertIn('the site has no third-party-notices.txt at its top', notes[1])

    def test_the_policy_holds_the_hash_of_every_inline_script_a_page_runs(self):
        site = make_site(os.path.join(self.work, 'site'), '/b')
        policy, problems = deploy.content_security_policy(site)
        self.assertEqual(problems, [])
        hashes = sorted(deploy.script_hash(text) for text in ('theme()', 'import "./x.js"', '\nsidebar();\n'))
        self.assertEqual(policy, deploy.c_PolicyTemplate.format(scripts=''.join(' ' + entry for entry in hashes)))
        # The hash is the base64 of the SHA-256 of the script's text, as browsers compute it.
        self.assertEqual(deploy.script_hash('theme()'), "'sha256-%s'" % __import__('base64').b64encode(hashlib.sha256(b'theme()').digest()).decode())
        self.assertIn("script-src 'self' 'wasm-unsafe-eval' 'sha256-", policy)
        self.assertIn("font-src 'self'; connect-src 'self'; worker-src 'self' blob:; object-src 'none'", policy)
        write(os.path.join(site, 'core', 'bad', 'index.html'), '<button onclick="go()">x</button><a href="javascript:go()">y</a>')
        problems = '\n'.join(deploy.content_security_policy(site)[1])
        self.assertIn('core/bad/index.html: button onclick runs inline code, which the policy blocks', problems)
        self.assertIn('core/bad/index.html: a href="javascript:…" runs inline code', problems)
        self.assertIn('add_header Content-Security-Policy "%s" always;' % policy, deploy.csp_conf(policy))
        with self.assertRaises(ValueError):
            deploy.csp_conf('a "b"')

    def test_moved_pages_become_exact_locations_with_and_without_their_slash(self):
        for base, _ in c_Bases:
            site = make_site(os.path.join(self.work, 'site' + base.replace('/', '-')), base)
            moves = deploy.moved_pages(site, base)
            self.assertEqual(moves, [('%s/core/old/' % base, '%s/core/time/' % base)])
            rules = deploy.redirects_conf(moves)
            self.assertIn('location = %s/core/old/ { return 301 %s/core/time/; }' % (base, base), rules)
            self.assertIn('location = %s/core/old { return 301 %s/core/time/; }' % (base, base), rules)
            if base != '/strata-engine-docs':
                self.assertNotIn('/strata-engine-docs', rules)
        self.assertIn('# No page has moved.', deploy.redirects_conf([]))
        write(os.path.join(self.work, 'away', 'index.html'), '<p>')
        write(os.path.join(self.work, 'away', 'core', 'old', 'index.html'), moved_page('/b', 'https://elsewhere.example.org/'))
        with self.assertRaisesRegex(ValueError, 'not a page path under /b/'):
            deploy.moved_pages(os.path.join(self.work, 'away'), '/b')

    def tar_entries(self, path):
        with tarfile.open(path) as archive:
            return [(member.name, member.mode, member.mtime, member.uid, member.gid, member.uname, member.gname, member.type) for member in archive.getmembers()]

    def test_assemble_writes_two_reproducible_tarballs_and_their_sums_at_three_bases(self):
        for base, label in c_Bases:
            site = make_site(os.path.join(self.work, 'site' + base.replace('/', '-')), base)
            out = os.path.join(self.work, 'release' + base.replace('/', '-'))
            folder, notes = release.assemble(site, base, 'main-0123abcd', out, c_Deploy)
            self.assertEqual(notes, [])
            self.assertEqual(sorted(os.listdir(folder)), ['SHA256SUMS', 'strata-engine-docs-deploy-main-0123abcd.tar.gz', 'strata-engine-docs-main-0123abcd.tar.gz'])
            site_tar = os.path.join(folder, 'strata-engine-docs-main-0123abcd.tar.gz')
            deploy_tar = os.path.join(folder, 'strata-engine-docs-deploy-main-0123abcd.tar.gz')
            top = deploy.top_folder(base)
            entries = self.tar_entries(site_tar)
            names = [entry[0] for entry in entries]
            self.assertEqual(names, sorted(names), label)
            self.assertEqual(names[0], top.split('/')[0], label)
            self.assertIn('%s/core/time/index.html' % top, names)
            self.assertIn('%s/_astro/a.css.gz' % top, names)
            self.assertTrue(all(entry[2:7] == (0, 0, 0, '', '') for entry in entries), label)
            self.assertTrue(all(entry[1] == (0o755 if entry[7] == tarfile.DIRTYPE else 0o644) for entry in entries), label)
            with open(site_tar, 'rb') as file:
                header = file.read(10)
            self.assertEqual(header[3] & 0x08, 0, 'no file name in the gzip header')
            self.assertEqual(header[4:8], b'\0\0\0\0', 'no time stamp in the gzip header')
            with tarfile.open(deploy_tar) as archive:
                members = {member.name: member for member in archive.getmembers()}
                self.assertEqual(sorted(name for name in members if name != 'deploy'),
                                 sorted('deploy/' + name for name in deploy.deploy_files(c_Deploy) + list(deploy.c_GeneratedFiles)))
                self.assertEqual(members['deploy/deploy-files.sh'].mode, 0o755)
                nginx = archive.extractfile('deploy/nginx.conf').read().decode('utf-8')
                docker = archive.extractfile('deploy/Dockerfile').read().decode('utf-8')
                readme = archive.extractfile('deploy/README.md').read().decode('utf-8')
                redirects = archive.extractfile('deploy/nginx-redirects.conf').read().decode('utf-8')
                csp = archive.extractfile('deploy/nginx-csp.conf').read().decode('utf-8')
            self.assertIn('location ^~ %s/ {' % base, nginx)
            self.assertIn('COPY --chown=101:101 %s/ /srv/www%s/' % (top, base), docker)
            self.assertIn('location = %s/core/old/ { return 301 %s/core/time/; }' % (base, base), redirects)
            self.assertIn('add_header Content-Security-Policy "%s" always;' % deploy.content_security_policy(site)[0], csp)
            if base == deploy.c_CommittedPrefix:
                with open(os.path.join(c_Deploy, 'nginx.conf'), encoding='utf-8') as file:
                    self.assertEqual(nginx, file.read())
                self.assertFalse(readme.startswith('> This release was assembled for the base'))
            else:
                self.assertNotRegex(nginx + docker, r'/strata-engine-docs(?![-.\w])')
                self.assertTrue(readme.startswith('> This release was assembled for the base `%s`' % label))
            with open(os.path.join(folder, 'SHA256SUMS'), encoding='utf-8') as file:
                sums = file.read()
            for name in ('strata-engine-docs-main-0123abcd.tar.gz', 'strata-engine-docs-deploy-main-0123abcd.tar.gz'):
                with open(os.path.join(folder, name), 'rb') as file:
                    self.assertIn('%s  %s\n' % (hashlib.sha256(file.read()).hexdigest(), name), sums)
            # Two runs on one build give the same bytes.
            again, _ = release.assemble(site, base, 'main-0123abcd', os.path.join(self.work, 'again' + base.replace('/', '-')), c_Deploy)
            with open(os.path.join(again, 'SHA256SUMS'), encoding='utf-8') as file:
                self.assertEqual(file.read(), sums, label)

    def test_assemble_refuses_a_site_that_is_not_ready(self):
        site = make_site(os.path.join(self.work, 'site'), '/b', gzipped=False)
        with self.assertRaisesRegex(release.ReleaseError, 'has no .gz beside it'):
            release.assemble(site, '/b', 'main-0123abcd', os.path.join(self.work, 'out'), c_Deploy)
        site = make_site(os.path.join(self.work, 'notices'), '/b', notices=False)
        with self.assertRaisesRegex(release.ReleaseError, 'no license.txt'):
            release.assemble(site, '/b', 'book-v0.8.1-r1', os.path.join(self.work, 'out'), c_Deploy)
        folder, notes = release.assemble(site, '/b', 'main-0123abcd', os.path.join(self.work, 'out'), c_Deploy)
        self.assertEqual(len(notes), 2)
        write(os.path.join(site, 'core', 'bad', 'index.html'), '<body onload="x()">')
        with self.assertRaisesRegex(release.ReleaseError, 'body onload runs inline code'):
            release.assemble(site, '/b', 'main-0123abcd', os.path.join(self.work, 'out'), c_Deploy)

    def test_layout_writes_what_the_container_s_final_stage_copies(self):
        for base, _ in c_Bases:
            site = make_site(os.path.join(self.work, 'site' + base.replace('/', '-')), base)
            out = os.path.join(self.work, 'serve' + base.replace('/', '-'))
            release.layout(site, base, out, c_Deploy)
            nginx = os.path.join(out, 'nginx')
            for relative in ('conf.d/00-strata-engine-docs-http.conf', 'conf.d/default.conf', 'snippets/strata-engine-docs.conf',
                             'snippets/strata-engine-docs-csp.conf', 'snippets/strata-engine-docs-redirects.conf'):
                self.assertTrue(os.path.isfile(os.path.join(nginx, *relative.split('/'))), relative)
            with open(os.path.join(nginx, 'strata-engine-docs-base'), encoding='utf-8') as file:
                self.assertEqual(file.read(), base + '\n')
            self.assertTrue(os.path.isfile(os.path.join(out, 'www', *[part for part in base.split('/') if part], 'core', 'time', 'index.html')))
            with open(os.path.join(nginx, 'snippets', 'strata-engine-docs.conf'), encoding='utf-8') as file:
                self.assertIn('location ^~ %s/ {' % base, file.read())
        # deploy/Dockerfile.build copies exactly those two folders and reads the base for its health check.
        with open(os.path.join(c_Deploy, 'Dockerfile.build'), encoding='utf-8') as file:
            text = file.read()
        self.assertEqual(release.dockerfile_copies(text), [('/book/serve/nginx/', '/etc/nginx/'), ('/book/serve/www/', '/srv/www/')])
        self.assertIn('$(cat /etc/nginx/strata-engine-docs-base)', text)
        self.assertIn('python3 tools/release.py layout --dist dist --out /book/serve', text)

    def test_the_command_line(self):
        site = make_site(os.path.join(self.work, 'site'), '/strata-engine-docs')
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(release.main(['assemble', '--dist', site, '--tag', 'main-0123abcd', '--out', os.path.join(self.work, 'r')]), 0)
            self.assertEqual(release.main(['csp', '--dist', site]), 0)
        self.assertIn("default-src 'self'", out.getvalue())
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            self.assertEqual(release.main(['assemble', '--dist', site, '--tag', 'v1', '--out', os.path.join(self.work, 'r')]), 1)
            self.assertEqual(release.main(['assemble', '--dist', site, '--tag', 'main-0123abcd', '--base', 'nope', '--out', os.path.join(self.work, 'r')]), 2)
        self.assertIn('neither a release', errors.getvalue())


if __name__ == '__main__':
    unittest.main()
