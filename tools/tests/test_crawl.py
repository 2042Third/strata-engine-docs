"""crawl.py on small built sites: what a clean site looks like, and every kind of problem it must catch."""

import contextlib
import glob
import io
import json
import os
import re
import sys
import shutil
import tempfile
import unittest
import urllib.parse

# The tools and this folder as packages, however unittest was started: discover -s tools/tests -t tools, -t . or
# discover tools/tests (plan/pipelines.md writes the last one).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
import crawl

c_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

c_Head = '<link rel="stylesheet" href="/docs/_astro/site.css"><link rel="canonical" href="https://example.com/docs/%s"><script type="module" src="/docs/_astro/page.js"></script>'


def page(path, body):
    return '<!doctype html><html><head><title>%s</title>%s</head><body>%s</body></html>' % (path, c_Head % path, body)


class CrawlTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='crawl-test-')
        self.dist = os.path.join(self.root, 'dist')
        self.files = {
            'index.html': page('', '<a href="/docs/a/">A</a> <a href="https://github.com/x">out</a> <img src="/docs/_figures/p.webp" srcset="/docs/_figures/p.webp 1w, /docs/_figures/q.avif 2w">'),
            'a/index.html': page('a/', '<h2 id="part">Part</h2><a href="/docs/#top">home</a><a href="#part">here</a><a href="/docs/a/#part">again</a>'),
            '404.html': '<!doctype html><html><head><title>404</title><meta name="robots" content="noindex"><link rel="stylesheet" href="/docs/_astro/site.css"></head><body><p>Not here.</p></body></html>',
            '_astro/site.css': '@font-face{src:url(./font.woff2)} body{background:url("/docs/_figures/p.webp")}',
            '_astro/page.js': 'import {x} from "./chunk.js";\nconst y = import("./lazy.js");',
            '_astro/chunk.js': 'export const x = 1;',
            '_astro/lazy.js': 'export default 2;',
            '_astro/font.woff2': 'font',
            '_figures/p.webp': 'p',
            '_figures/q.avif': 'q',
            'sitemap-index.xml': '<sitemapindex><sitemap><loc>https://example.com/docs/sitemap-0.xml</loc></sitemap></sitemapindex>',
            'sitemap-0.xml': '<urlset><url><loc>https://example.com/docs/</loc></url><url><loc>https://example.com/docs/a/</loc></url></urlset>',
            'pagefind/pagefind-entry.json': '{}',
            'pagefind/pagefind.js': 'export {}',
        }
        self.files['index.html'] = self.files['index.html'].replace('<body>', '<body><span id="top"></span>')
        self.write()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self):
        if os.path.exists(self.dist):
            shutil.rmtree(self.dist)
        for relative, text in self.files.items():
            path = os.path.join(self.dist, *relative.split('/'))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(text)

    def run_crawl(self):
        report = os.path.join(self.root, 'report.json')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = crawl.main(['--root', self.root, '--base', '/docs', '--site', 'https://example.com', '--workers', '2', '--report', report])
        with open(report, encoding='utf-8') as file:
            return code, json.load(file), output.getvalue()

    def test_a_clean_site_passes_and_is_measured(self):
        code, report, output = self.run_crawl()
        self.assertEqual(code, 0, output)
        self.assertEqual(report['summary']['pages'], 2)  # the 404 page is asked for apart from the crawl
        self.assertEqual(report['summary']['external_links'], 1)
        self.assertTrue(os.path.isfile(os.path.join(self.root, 'stage', 'docs', 'index.html')))

    def test_broken_links_resources_and_anchors_fail(self):
        self.files['a/index.html'] = page('a/', '<a href="/docs/missing/">x</a><img src="/docs/_figures/none.webp"><a href="/docs/#nowhere">y</a>')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = '\n'.join(report['problems'])
        self.assertIn('/docs/missing/ answers 404', problems)
        self.assertIn('/docs/_figures/none.webp answers 404', problems)
        self.assertIn('#nowhere, which has no element with that id', problems)

    def test_leaving_the_prefix_and_loading_from_other_hosts_fail(self):
        self.files['a/index.html'] = page('a/', '<a href="/other/">x</a><script src="https://cdn.example.org/lib.js"></script>')
        self.write()
        code, report, _ = self.run_crawl()
        problems = '\n'.join(report['problems'])
        self.assertEqual(code, 1)
        self.assertIn('/other/ leaves the prefix /docs/', problems)
        self.assertIn('loads https://cdn.example.org/lib.js from another host', problems)

    def test_an_id_twice_on_a_page_fails(self):
        self.files['a/index.html'] = page('a/', '<h2 id="part">Part</h2><figure id="fig-x"></figure><figure id="fig-x"></figure>'
                                          '<template data-book-track="game"><nav id="track"></nav></template><template data-book-track="engine"><nav id="track"></nav></template>')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = '\n'.join(report['problems'])
        self.assertIn('has 1 id more than once (a link to it jumps to the first): fig-x', problems)
        self.assertNotIn('track', problems)

    def test_orphan_pages_fail(self):
        self.files['lost/index.html'] = page('lost/', 'No one links here.')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        self.assertIn('lost/index.html is never reached', '\n'.join(report['problems']))

    def test_a_missing_page_gets_the_site_s_404_page(self):
        os.remove(os.path.join(self.dist, '404.html'))
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        self.assertIn('answers 404 without the site\'s 404 page', '\n'.join(report['problems']))

    def test_the_404_page_loads_its_resources_from_a_missing_path_three_levels_deep(self):
        # plan/site.md, gate (a): one level down, "../_astro/site.css" still reaches <base>/_astro/; three levels down
        # it does not, as a reader's browser would find on any deeper missing address.
        self.files['404.html'] = self.files['404.html'].replace('href="/docs/_astro/site.css"', 'href="../_astro/site.css"')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1, report['problems'])
        self.assertEqual(crawl.c_MissingPage.count('/'), 3)
        wrong = urllib.parse.urljoin('/docs/' + crawl.c_MissingPage, '../_astro/site.css')
        self.assertIn('%s answers 404' % wrong, '\n'.join(report['problems']))

    def test_the_server_redirects_folders_and_never_lists_them(self):
        stage_root = os.path.join(self.root, 'stage')
        crawl.stage(self.dist, stage_root, '/docs')
        server = crawl.start_server(stage_root, '/docs')
        try:
            base = 'http://127.0.0.1:%d' % server.server_address[1]
            checker = crawl.Crawl(base + '/docs/', '/docs', '', 1)
            self.assertEqual(checker.fetch(base + '/docs/a')[3], base + '/docs/a/')
            self.assertEqual(checker.fetch(base + '/docs/_astro/')[0], 404)
            self.assertEqual(checker.fetch(base + '/')[0], 404)
            self.assertEqual(checker.fetch(base + '/docs/../x')[0], 404)
        finally:
            server.shutdown()
            server.server_close()

    def test_the_server_is_quiet_when_a_browser_drops_a_connection_and_reports_other_errors(self):
        server = crawl.start_server(self.dist, '/docs')
        try:
            for error, printed in ((ConnectionAbortedError('dropped'), False), (ConnectionResetError('reset'), False), (ValueError('a bug'), True)):
                errors = io.StringIO()
                with contextlib.redirect_stderr(errors):
                    try:
                        raise error
                    except Exception:
                        server.handle_error(None, ('127.0.0.1', 1))
                self.assertEqual(bool(errors.getvalue()), printed, (error, errors.getvalue()))
        finally:
            server.shutdown()
            server.server_close()

    def test_references_of_css_and_javascript(self):
        self.assertEqual(crawl.css_references('a{b:url(x.png)} @import "y.css"; c{d:url(data:abc)}'), ['x.png', 'y.css'])
        self.assertEqual(crawl.js_references('import a from "./a.js";export * from "./b.js";import("./c.js");import "d";'), ['./a.js', './b.js', './c.js'])
        # Vite 8 writes dynamic imports in backticks; fetch and new URL of a literal path load files too. A template
        # with ${…} names no fixed file.
        script = 'import(`./ui-core.js`);fetch("/docs/api.json");fetch(`${base}x.json`);new URL("./w.wasm", import.meta.url);import(`${o}pagefind.js`)'
        self.assertEqual(crawl.js_references(script), ['./ui-core.js', '/docs/api.json', './w.wasm'])

    def test_every_channel_a_page_loads_from_is_followed(self):
        self.files['a/index.html'] = page('a/', '<video poster="/docs/_figures/poster.webp"></video><object data="/docs/_figures/o.svg"></object>'
                                          '<svg><image href="/docs/_figures/i.png"/><use xlink:href="#part"/></svg><h2 id="part">Part</h2>'
                                          '<script type="module">import("/docs/_astro/inline.js")</script>')
        self.files['_astro/page.js'] += '\nimport(`./lazy-backtick.js`);fetch("/docs/data.json");'
        self.write()
        code, report, _ = self.run_crawl()
        problems = '\n'.join(report['problems'])
        self.assertEqual(code, 1)
        for missing in ('_figures/poster.webp', '_figures/o.svg', '_figures/i.png', '_astro/inline.js', '_astro/lazy-backtick.js', 'data.json'):
            self.assertIn('/docs/%s answers 404' % missing, problems)
        self.assertNotIn('#part', problems)

    def test_canonical_links_and_sitemaps_must_be_on_the_site(self):
        self.files['a/index.html'] = page('a/', '').replace('https://example.com/docs/a/', 'https://wrong.example.org/docs/a/')
        self.files['sitemap-0.xml'] = self.files['sitemap-0.xml'].replace('https://example.com/docs/a/', 'https://other.example.org/docs/a/')
        self.files['index.html'] = self.files['index.html'].replace('<link rel="canonical" href="https://example.com/docs/">', '<link rel="canonical" href="https://example.com/docs/a/">')
        self.write()
        code, report, _ = self.run_crawl()
        problems = '\n'.join(report['problems'])
        self.assertEqual(code, 1)
        self.assertIn('https://wrong.example.org/docs/a/ is not on the site https://example.com under /docs/', problems)
        self.assertIn('https://other.example.org/docs/a/ is not on the site', problems)
        self.assertIn('its canonical URL https://example.com/docs/a/ names another page', problems)

    def test_canonical_og_url_and_sitemap_name_the_origin_the_base_and_the_page_at_three_bases(self):
        # plan/site.md, gate (a): "canonical or og:url is not the origin + the base + the page's path, or names a page
        # that does not exist"; "Every way the site can leave the base": canonical, og:url and the sitemap.
        own = '<meta property="og:url" content="https://example.com/docs/%s">'
        original = dict(self.files)
        original['index.html'] = original['index.html'].replace('</head>', own % '' + '</head>')
        original['a/index.html'] = original['a/index.html'].replace('</head>', own % 'a/' + '</head>')
        for base in ('/', '/docs', '/x/y'):
            with self.subTest(base=base):
                prefix = '' if base == '/' else base
                self.files = {name: text.replace('/docs/', prefix + '/') for name, text in original.items()}
                self.write()
                code, report, output = self.run_crawl_at(base)
                self.assertEqual(code, 0, output)
                at = 'https://example.com%s/' % prefix
                # og:url on another host, og:url naming a missing page, a canonical link naming another page, and a
                # sitemap entry off the site.
                self.files['index.html'] = self.files['index.html'].replace('<meta property="og:url" content="%s">' % at, '<meta property="og:url" content="https://wrong.example.org%s/">' % prefix)
                self.files['a/index.html'] = self.files['a/index.html'].replace('<meta property="og:url" content="%sa/">' % at, '<meta property="og:url" content="%sgone/">' % at)
                self.files['a/index.html'] = self.files['a/index.html'].replace('<link rel="canonical" href="%sa/">' % at, '<link rel="canonical" href="%s">' % at)
                self.files['sitemap-0.xml'] = self.files['sitemap-0.xml'].replace('<loc>%sa/</loc>' % at, '<loc>https://other.example.org%s/a/</loc>' % prefix)
                self.write()
                code, report, _ = self.run_crawl_at(base)
                problems = '\n'.join(report['problems'])
                self.assertEqual(code, 1)
                self.assertIn('https://wrong.example.org%s/ is not on the site https://example.com under %s/' % (prefix, prefix), problems)
                self.assertRegex(problems, r'%s/a/: its canonical URL %sgone/ names another page' % (re.escape(prefix), re.escape(at)))
                self.assertRegex(problems, r'%s/a/: its canonical URL %s names another page' % (re.escape(prefix), re.escape(at)))
                self.assertRegex(problems, r'%s/gone/ answers 404 \(linked from http://127\.0\.0\.1:\d+%s/a/\)' % (re.escape(prefix), re.escape(prefix)))
                self.assertIn('https://other.example.org%s/a/ is not on the site https://example.com under %s/' % (prefix, prefix), problems)

    def test_a_crawl_with_the_wrong_site_fails_instead_of_skipping_the_check(self):
        report = os.path.join(self.root, 'report.json')
        with contextlib.redirect_stdout(io.StringIO()):
            code = crawl.main(['--root', self.root, '--base', '/docs', '--site', 'https://book.example.org', '--workers', '2', '--report', report])
        with open(report, encoding='utf-8') as file:
            problems = '\n'.join(json.load(file)['problems'])
        self.assertEqual(code, 1)
        self.assertIn('is not on the site https://book.example.org', problems)

    def test_the_404_page_has_no_canonical_link_and_is_not_indexed(self):
        self.files['404.html'] = page('404', '<p>Not here.</p>')
        self.write()
        code, report, _ = self.run_crawl()
        problems = '\n'.join(report['problems'])
        self.assertEqual(code, 1)
        self.assertIn('the 404 page names https://example.com/docs/404 as its canonical URL', problems)
        self.assertIn('the 404 page has no <meta name="robots" content="noindex">', problems)

    def test_folders_without_an_index_answer_the_404_page(self):
        stage_root = os.path.join(self.root, 'stage')
        site = crawl.stage(self.dist, stage_root, '/docs')
        server = crawl.start_server(stage_root, '/docs')
        try:
            checker = crawl.Crawl('http://127.0.0.1:%d/docs/' % server.server_address[1], '/docs', '', 1)
            crawl.check_folders(checker, checker.start, site)
            self.assertEqual(checker.problems, [])
        finally:
            server.shutdown()
            server.server_close()
        # A server that answers such a folder with anything else is reported.
        checker = crawl.Crawl('http://127.0.0.1:9/docs/', '/docs', '', 1)
        checker.fetch = lambda url: (403, 'text/html', b'<center>nginx</center>', url)
        crawl.check_folders(checker, checker.start, site)
        self.assertIn('_astro/ (a folder without index.html) answers 403', '\n'.join(checker.problems))

    def test_a_robots_txt_in_the_build_fails(self):
        # site.md, "The base path", rule 5: crawlers read only <host>/robots.txt; the build never holds one, at the base
        # or below it.
        self.files['robots.txt'] = 'User-agent: *\nAllow: /\n'
        self.files['a/ROBOTS.TXT'] = 'User-agent: *\n'
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = '\n'.join(report['problems'])
        self.assertIn('robots.txt: the build holds no robots.txt', problems)
        self.assertIn('a/ROBOTS.TXT: the build holds no robots.txt', problems)

    def test_a_formula_drawn_as_a_katex_error_fails(self):
        # site.md, "Math": gate (a) checks again that the built HTML holds no element of the class katex-error.
        self.files['a/index.html'] = page('a/', '<p>Area: <span class="katex-error" title="ParseError: Expected group after \\frac">\\frac{1}</span></p>'
                                          '<p>A class that only starts so: <span class="katex-errors">x</span></p>')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = [problem for problem in report['problems'] if 'katex-error' in problem]
        self.assertEqual(len(problems), 1, report['problems'])
        self.assertIn('/docs/a/ holds 1 formula KaTeX could not render (class katex-error): ParseError: Expected group after', problems[0])

    def test_the_sitemap_lists_no_page_that_asks_not_to_be_indexed_and_print_views_ask(self):
        # site.md, "Navigation": the print views carry "noindex" and the sitemap's filter leaves them out.
        noindex = '<meta name="robots" content="noindex">'
        self.files['index.html'] = self.files['index.html'].replace('</body>', '<a href="/docs/print/a/">print</a><a href="/docs/print/b/">print b</a></body>')
        self.files['print/a/index.html'] = page('print/a/', 'The whole part.').replace('<title>', noindex + '<title>')
        self.files['print/b/index.html'] = page('print/b/', 'Another part.')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = '\n'.join(report['problems'])
        self.assertIn('/docs/print/b/ is a print view without <meta name="robots" content="noindex">', problems)
        self.assertNotIn('/docs/print/a/ is a print view', problems)
        self.assertNotIn('in the sitemap', problems)
        # A print view the sitemap lists, and a listed page that asks not to be indexed, fail.
        self.files['print/b/index.html'] = self.files['print/a/index.html'].replace('print/a/', 'print/b/')
        self.files['a/index.html'] = self.files['a/index.html'].replace('<title>', noindex + '<title>')
        self.files['sitemap-0.xml'] = self.files['sitemap-0.xml'].replace('</urlset>', '<url><loc>https://example.com/docs/print/a/</loc></url></urlset>')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = [problem for problem in report['problems'] if 'in the sitemap' in problem]
        self.assertEqual(len(problems), 2, report['problems'])
        self.assertIn('/docs/a/ is in the sitemap but asks search engines not to index it (noindex)', problems[0])
        self.assertIn('/docs/print/a/ is in the sitemap but asks search engines not to index it (noindex)', problems[1])

    def test_a_build_for_another_base_must_not_name_the_default_prefix(self):
        self.files['a/index.html'] = page('a/', '<a href="https://github.com/2042Third/strata-engine-docs/edit/main/x.md">edit</a><img src="/strata-engine-docs/_figures/p.webp">')
        self.files['_astro/site.css'] += ' x{background:url(/strata-engine-docs/_astro/b.png)}'
        self.files['_astro/page.js'] += '\nconst u = `/strata-engine-docs/pagefind/`;'
        self.write()
        found = crawl.forbidden_prefix_uses(self.dist, '/strata-engine-docs')
        self.assertEqual(sorted(name for name, _ in found), ['_astro/page.js', '_astro/site.css', 'a/index.html'])
        report = os.path.join(self.root, 'report.json')
        with contextlib.redirect_stdout(io.StringIO()):
            code = crawl.main(['--root', self.root, '--base', '/docs', '--site', 'https://example.com', '--report', report, '--forbid-prefix', '/strata-engine-docs'])
        self.assertEqual(code, 1)

    def moved(self, target, refresh=None, canonical=None, link=None, noindex=True):
        return ('<!doctype html><html><head>%s<meta name="strata-book-moved" content="%s"><link rel="canonical" href="https://example.com%s">'
                '<meta http-equiv="refresh" content="0; url=%s"></head><body><a href="%s">The page</a></body></html>'
                % ('<meta name="robots" content="noindex">' if noindex else '', target, canonical or target, refresh or target, link or target))

    def test_the_fallback_page_of_a_moved_page_is_crawled_and_checked(self):
        # Moved pages (site.md, "Moved pages"): no page links to a fallback page, so the crawl starts at it.
        self.files['old/index.html'] = self.moved('/docs/a/')
        self.write()
        code, report, output = self.run_crawl()
        self.assertEqual(code, 0, output)
        self.assertEqual(report['summary']['pages'], 3)
        self.files['old/index.html'] = self.moved('/docs/a/', refresh='/docs/', canonical='/docs/', link='/docs/', noindex=False)
        self.files['gone/index.html'] = self.moved('/docs/none/')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = '\n'.join(report['problems'])
        self.assertIn("/docs/old/: a moved page refreshes to '0; url=/docs/', not to its new page /docs/a/", problems)
        self.assertIn('/docs/old/: a moved page names [\'https://example.com/docs/\'] as its canonical URL, not its new page https://example.com/docs/a/', problems)
        self.assertIn('/docs/old/: a moved page has no plain link to its new page /docs/a/', problems)
        self.assertIn('/docs/old/: a moved page has no <meta name="robots" content="noindex">', problems)
        self.assertIn('/docs/none/ answers 404', problems)
        # Through a server with the release's rules the old address answers 301 to the new page before its fallback
        # page is read: that is the moved page working, and any other redirect still fails.
        crawl_object = crawl.Crawl('http://127.0.0.1:1/docs/', '/docs', 'https://example.com', 1)
        crawl_object.moved = {'http://127.0.0.1:1/docs/old/': 'http://127.0.0.1:1/docs/a/'}
        crawl_object.fetch = lambda url, method='GET': (200, 'text/html', b'<p>a', 'http://127.0.0.1:1/docs/a/')
        self.assertEqual(crawl_object.visit('http://127.0.0.1:1/docs/old/', '(checks)'), [])
        self.assertEqual(crawl_object.problems, [])
        crawl_object.visit('http://127.0.0.1:1/docs/other/', 'x')
        self.assertIn('/docs/other/ redirects to http://127.0.0.1:1/docs/a/', '\n'.join(crawl_object.problems))

    def test_a_font_inlined_into_a_style_sheet_fails(self):
        # rulings 6, R23: the policy's font-src 'self' blocks a font given as a data: URL.
        self.files['_astro/site.css'] += ' @font-face{src:url(data:font/woff2;base64,AAAA) format("woff2")} x{background:url("data:image/svg+xml,%3Csvg%3E")}'
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = [problem for problem in report['problems'] if 'data: URL' in problem]
        self.assertEqual(len(problems), 1, report['problems'])
        self.assertIn('_astro/site.css holds a font as a data: URL (data:font/woff2', problems[0])
        self.assertEqual(crawl.font_data_urls('url("data:application/font-woff;base64,AA")'), ['data:application/font-woff'])
        self.assertEqual(crawl.font_data_urls('url(data:image/png;base64,AA)'), [])

    def test_a_file_referenced_by_nothing_fails_and_the_exempt_files_pass_at_three_bases(self):
        # plan/site.md, gate (a), and requirement 5: a .br is a file nothing references, and so is a .gz beside no
        # file; the 404 page, Pagefind's files, the sitemaps, the manifest, the favicon and a .gz beside its file are
        # exempt.
        original = dict(self.files)
        exempt = {
            'a/index.html.gz': 'gzip of a/index.html',
            '_astro/site.css.gz': 'gzip of site.css',
            'pagefind/fragment/en_1.pf_fragment': 'f',
            'pagefind/wasm.en.pagefind': 'w',
            'sitemap-1.xml': '<urlset></urlset>',
            'manifest.webmanifest': '{}',
            'favicon.svg': '<svg/>',
            '404.html.gz': 'gzip of 404.html',
        }
        unreferenced = {
            '_astro/site.css.br': 'brotli of site.css',
            '_astro/gone.css.gz': 'gzip of a file that is not there',
            '_astro/unused.js': 'export {}',
            'a/notes.txt': 'nothing links here',
        }
        for base in ('/', '/docs', '/x/y'):
            with self.subTest(base=base):
                prefix = '' if base == '/' else base
                self.files = {name: text.replace('/docs/', prefix + '/') for name, text in original.items()}
                self.files.update(exempt)
                self.write()
                code, report, output = self.run_crawl_at(base)
                self.assertEqual(code, 0, output)
                self.files.update(unreferenced)
                self.write()
                code, report, _ = self.run_crawl_at(base)
                self.assertEqual(code, 1)
                problems = [problem for problem in report['problems'] if 'referenced by nothing' in problem or 'stands beside no file' in problem]
                self.assertEqual(len(problems), 4, report['problems'])
                self.assertEqual(len(report['problems']), 4, report['problems'])
                text = '\n'.join(problems)
                self.assertIn('_astro/site.css.br is referenced by nothing: a release holds no .br file', text)
                self.assertIn('_astro/gone.css.gz stands beside no file of the build', text)
                self.assertIn('_astro/unused.js is referenced by nothing', text)
                self.assertIn('a/notes.txt is referenced by nothing', text)
        self.assertTrue(crawl.is_unreferenced_exempt('sitemap-0.xml', set()))
        self.assertFalse(crawl.is_unreferenced_exempt('a/sitemap-0.xml', set()))
        self.assertFalse(crawl.is_unreferenced_exempt('a/404.html', set()))
        self.assertTrue(crawl.is_unreferenced_exempt('x.js.gz', {'x.js'}))
        self.assertFalse(crawl.is_unreferenced_exempt('x.js.gz', set()))
        self.assertFalse(crawl.is_unreferenced_exempt('x.js.br', {'x.js'}))

    def run_crawl_at(self, base):
        report = os.path.join(self.root, 'report.json')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = crawl.main(['--root', self.root, '--base=%s' % base, '--site', 'https://example.com', '--workers', '2', '--report', report])
        with open(report, encoding='utf-8') as file:
            return code, json.load(file), output.getvalue()

    def test_a_running_server_may_serve_a_site_of_its_own_at_its_root(self):
        # rulings 6, R24: a host with a site at its root answers 200 there; the staged server must not.
        site_root = 'http://127.0.0.1:1/'
        crawl_object = crawl.Crawl(site_root + 'docs/', '/docs', 'https://example.com', 1)
        crawl_object.fetch = lambda url, method='GET': (200, 'text/html', b'<p>the host', url) if url == site_root else (404, 'text/html', b'<link rel="stylesheet" href="/docs/_astro/site.css"><meta name="robots" content="noindex">', url)
        crawl.check_root_and_missing(crawl_object, site_root + 'docs/', site_root, own_server=False)
        self.assertEqual(crawl_object.problems, [])
        crawl.check_root_and_missing(crawl_object, site_root + 'docs/', site_root, own_server=True)
        self.assertIn('http://127.0.0.1:1/ answers 200: the site must not need the host\'s root', '\n'.join(crawl_object.problems))

    def test_a_link_to_a_host_the_list_does_not_name_fails(self):
        # plan/site.md, gate (a): an <a href> names only hosts of tools/external-hosts.txt.
        self.files['a/index.html'] = page('a/', '<a href="https://unlisted.example.net/page">x</a><a href="https://GitHub.com/x">y</a>')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = '\n'.join(report['problems'])
        self.assertIn('/docs/a/ links to https://unlisted.example.net/page: the host unlisted.example.net is not in tools/external-hosts.txt', problems)
        self.assertNotIn('github.com is not in', problems.lower())
        hosts = os.path.join(self.root, 'hosts.txt')
        with open(hosts, 'w', encoding='utf-8') as file:
            file.write('# a comment\ngithub.com\nunlisted.example.net  # the page cites it\n')
        report_file = os.path.join(self.root, 'report.json')
        with contextlib.redirect_stdout(io.StringIO()):
            code = crawl.main(['--root', self.root, '--base', '/docs', '--site', 'https://example.com', '--report', report_file, '--external-hosts', hosts])
        self.assertEqual(code, 0)
        with open(hosts, 'w', encoding='utf-8') as file:
            file.write('https://github.com/\n')
        with self.assertRaisesRegex(ValueError, 'is not a host name in lowercase'):
            crawl.read_external_hosts(hosts)
        # The repository's own list names every host the sample pages link (the crawl of the build proves the rest).
        self.assertIn('github.com', crawl.read_external_hosts(crawl.c_ExternalHosts))

    def write_pin(self, commit):
        with open(os.path.join(self.root, 'engine.pin'), 'w', encoding='utf-8') as file:
            file.write('commit %s\nrelease 0.8.0\nprerelease yes\nrepository https://github.com/owner/engine\n' % commit)

    def test_a_link_into_the_engine_names_the_pin_outside_a_history_aside(self):
        # plan/site.md, gate (a): a link to <repository>/blob/ or /tree/ names a full commit, the pin's, except inside
        # a :::history aside (asides.mjs draws it as aside.book-aside--history).
        pin, other = '1' * 40, '2' * 40
        self.write_pin(pin)
        repository = 'https://github.com/owner/engine'
        self.files['a/index.html'] = page('a/', '<a href="%s/blob/%s/Strata/a.cpp#L1-L2">at the pin</a>' % (repository, pin)
                                          + '<a href="%s/tree/%s/Strata">at the pin</a><a href="%s/releases">releases</a>' % (repository, pin, repository)
                                          + '<aside class="starlight-aside book-aside book-aside--history"><p><a href="%s/blob/%s/a.cpp">then</a></p></aside>' % (repository, other))
        self.write()
        code, report, output = self.run_crawl()
        self.assertEqual(code, 0, output)
        self.files['a/index.html'] = page('a/', '<a href="%s/blob/main/a.cpp">a branch</a><a href="%s/tree/%s">another commit</a>' % (repository, repository, other)
                                          + '<a href="%s/blob/1234567/a.cpp">a short commit</a>' % repository
                                          + '<aside class="starlight-aside book-aside book-aside--why"><a href="%s/blob/%s/b.cpp">why</a></aside>' % (repository, other)
                                          # The same link inside a history aside exempts only that one.
                                          + '<aside class="starlight-aside book-aside book-aside--history"><a href="%s/tree/%s">then</a></aside>' % (repository, other))
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = '\n'.join(report['problems'])
        self.assertIn("a link into the engine names a full commit (40 hex digits), not 'main'", problems)
        self.assertIn("not '1234567'", problems)
        self.assertIn('%s/tree/%s at the commit %s, not the pin %s' % (repository, other, other, pin), problems)
        self.assertIn('%s/blob/%s/b.cpp at the commit' % (repository, other), problems)

    def test_a_link_to_the_book_s_repository_fails_with_any_path_or_none(self):
        # rulings 6, R20: the book is closed source, so the site links nowhere in its repository.
        for href in (crawl.c_BookRepository, crawl.c_BookRepository + '/', crawl.c_BookRepository.upper().replace('HTTPS://GITHUB.COM', 'https://github.com') + '/edit/main/x.md'):
            with self.subTest(href=href):
                self.files['a/index.html'] = page('a/', '<a href="%s">the repository</a>' % href)
                self.write()
                code, report, _ = self.run_crawl()
                self.assertEqual(code, 1)
                self.assertIn('names the book\'s repository', '\n'.join(report['problems']))
        # Another repository of the same owner is not the book's.
        self.files['a/index.html'] = page('a/', '<a href="%s-other">another</a>' % crawl.c_BookRepository)
        self.write()
        self.assertEqual(self.run_crawl()[0], 0)

    def test_a_capital_letter_a_character_outside_ascii_or_a_wrong_case_fails(self):
        # plan/site.md, gate (a) and "Every way the site can leave the base" (case): a Linux server answers 404 to a URL
        # whose case differs from the file's; _astro/ keeps the names Vite gives (with capitals) and passes.
        self.files['_astro/Page.Ab12Cd.js'] = 'export {}'
        self.files['_figures/Big.webp'] = 'B'
        self.files['_figures/ü.webp'] = 'u'
        self.files['a/index.html'] = page('a/', '<script type="module" src="/docs/_astro/Page.Ab12Cd.js"></script><img src="/docs/_figures/Big.webp">'
                                          '<img src="/docs/_figures/%C3%BC.webp"><a href="/docs/A/">a wrong case</a>')
        self.write()
        code, report, _ = self.run_crawl()
        self.assertEqual(code, 1)
        problems = '\n'.join(report['problems'])
        self.assertNotIn('Page.Ab12Cd.js', problems)
        self.assertIn('/docs/_figures/Big.webp: a URL path holds a capital letter', problems)
        self.assertIn('/docs/_figures/%C3%BC.webp: a URL path holds a character outside ASCII', problems)
        # A case-insensitive disk serves /docs/A/ and the crawl says the case differs; a Linux server answers 404.
        self.assertTrue('/docs/A/ does not match a file of the build byte for byte' in problems or '/docs/A/ answers 404' in problems, problems)
        site = os.path.join(self.root, 'stage', 'docs')
        self.assertTrue(crawl.exact_case(site, os.path.join(site, 'a', 'index.html')))
        self.assertFalse(crawl.exact_case(site, os.path.join(site, 'A', 'index.html')))

    def footed(self, prefix, line='Copyright © 2026 Someone. All rights reserved.', links=('license.txt', 'third-party-notices.txt')):
        return '<footer><p>%s %s</p></footer>' % (line, ' '.join('<a href="%s/%s">%s</a>' % (prefix, name, name) for name in links))

    def test_every_page_holds_the_footer_line_and_its_two_links_once_the_build_has_license_txt_at_three_bases(self):
        # rulings 6, R20 and plan/site.md, gate (a): every HTML file holds the copyright line built from site.json and
        # links to <base>/license.txt and <base>/third-party-notices.txt. Before the build holds license.txt (LICENSE,
        # plan/site.md's change 15) there is nothing to check, and the crawl says so.
        with open(os.path.join(self.root, 'site.json'), 'w', encoding='utf-8') as file:
            file.write('{"base": "/docs", "origin": "https://example.com", "copyright": {"holder": "Someone", "year": 2026}}')
        original = dict(self.files)
        for base in ('/', '/docs', '/x/y'):
            with self.subTest(base=base):
                prefix = '' if base == '/' else base
                self.files = {name: text.replace('/docs/', prefix + '/') for name, text in original.items()}
                code, _, output = self.run_crawl_at_after_write(base)
                self.assertEqual(code, 0, output)
                self.assertIn('the footer line was not checked: the build holds no license.txt yet', output)
                self.files['license.txt'] = 'Copyright'
                self.files['third-party-notices.txt'] = 'Notices'
                self.files['index.html'] = self.files['index.html'].replace('</body>', self.footed(prefix) + '</body>')
                self.files['a/index.html'] = self.files['a/index.html'].replace('</body>', self.footed(prefix, line='Copyright © 2025 Someone. All rights reserved.', links=('license.txt',)) + '</body>')
                code, report, output = self.run_crawl_at_after_write(base)
                self.assertEqual(code, 1)
                problems = '\n'.join(report['problems'])
                self.assertIn('%s/a/ lacks the footer line "Copyright © 2026 Someone. All rights reserved."' % prefix, problems)
                self.assertIn('%s/a/: its footer does not link <base>/third-party-notices.txt' % prefix, problems)
                self.assertNotIn('%s/: its footer' % prefix, problems.replace('%s/a/: its footer' % prefix, ''))
                self.assertNotIn('footer line was not checked', output)
                self.files['a/index.html'] = original['a/index.html'].replace('/docs/', prefix + '/').replace('</body>', self.footed(prefix) + '</body>')
                code, report, output = self.run_crawl_at_after_write(base)
                self.assertEqual(code, 0, output)
                del self.files['license.txt'], self.files['third-party-notices.txt']

    def run_crawl_at_after_write(self, base):
        self.write()
        return self.run_crawl_at(base)

    def test_the_summary_measures_rows_9_to_11(self):
        # plan/site.md, budget rows 9 to 11 (rulings 5, R13): the median page, the HTML of the chapter pages and of the
        # print views, the scripts a page loads without searching, and the sidebar's markup.
        self.files['index.html'] = self.files['index.html'].replace('<body>', '<body><nav class="sidebar" aria-label="Main"><ul><li>Part</li></ul><nav aria-label="Inner">x</nav></nav>'
                                                                    '<script>let inline = 1;</script><a href="/docs/print/a/">print</a>')
        self.files['print/a/index.html'] = page('print/a/', 'All of it.').replace('<title>', '<meta name="robots" content="noindex"><title>')
        self.files['_astro/page.js'] += '\nimport "/docs/pagefind/pagefind.js";'
        self.write()
        code, report, output = self.run_crawl()
        self.assertEqual(code, 0, output)
        summary = report['summary']
        sizes = {name: os.path.getsize(os.path.join(self.dist, *name.split('/'))) for name in ('index.html', 'a/index.html', 'print/a/index.html')}
        self.assertEqual(summary['chapter_html_bytes'], sizes['index.html'] + sizes['a/index.html'])
        self.assertEqual(summary['print_html_bytes'], sizes['print/a/index.html'])
        import gzip
        packed = sorted(len(gzip.compress(self.files[name].encode('utf-8'), 9)) for name in ('index.html', 'a/index.html'))  # no line ends in them
        self.assertEqual(summary['median_page_gzip_bytes'], int(sum(packed) / 2))
        # page.js and the chunk it imports statically count; the lazy import() and Pagefind's script, which loads only
        # when a reader searches, do not; the inline script does.
        def written(name):
            with open(os.path.join(self.dist, *name.split('/')), 'rb') as file:
                return file.read()
        scripts = sum(len(gzip.compress(written(name), 9)) for name in ('_astro/page.js', '_astro/chunk.js'))
        self.assertEqual(summary['scripts_per_page_gzip_bytes'], scripts + len(gzip.compress(b'let inline = 1;', 9)))
        sidebar = '<nav class="sidebar" aria-label="Main"><ul><li>Part</li></ul><nav aria-label="Inner">x</nav></nav>'
        self.assertEqual(summary['sidebar_bytes'], len(sidebar))
        self.assertAlmostEqual(summary['sidebar_share'], round(len(sidebar) / sizes['index.html'], 4))


    def test_the_base_and_the_origin_come_from_site_json(self):
        with open(os.path.join(self.root, 'site.json'), 'w', encoding='utf-8') as file:
            file.write('{"base": "/docs", "origin": "https://example.com", "copyright": {"holder": "Someone", "year": 2026}}')
        environment = {name: os.environ.pop(name) for name in ('DOCS_BASE', 'DOCS_SITE') if name in os.environ}
        try:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = crawl.main(['--root', self.root, '--workers', '2'])
            self.assertEqual(code, 0, output.getvalue())
            os.remove(os.path.join(self.root, 'site.json'))
            with contextlib.redirect_stderr(io.StringIO()) as errors, self.assertRaises(SystemExit):
                crawl.main(['--root', self.root])
            self.assertIn('site.json does not exist', errors.getvalue())
        finally:
            os.environ.update(environment)


def find_lychee():
    found = shutil.which('lychee')
    if found:
        return found
    for pattern in ('lychee-*/lychee*', 'lychee-*/*/lychee*'):
        for candidate in sorted(glob.glob(os.path.join(c_Root, '.tools', *pattern.split('/')))):
            if os.path.basename(candidate) in ('lychee', 'lychee.exe'):
                return candidate
    return None


# CI's jobs run tools/bootstrap.py, which installs lychee: there a missing program is a failure, not a reason to skip.
@unittest.skipUnless(find_lychee() or os.environ.get('CI'), 'needs lychee (python tools/bootstrap.py downloads it into .tools/)')
class LycheeTests(unittest.TestCase):
    """Gate (a) 1 (plan/site.md): lychee offline over the staged folder, with fragments, as tools/crawl.py --lychee runs it."""

    def setUp(self):
        self.program = find_lychee()
        self.assertIsNotNone(self.program, 'lychee is not installed: run python tools/bootstrap.py')
        self.stage = os.path.join(tempfile.mkdtemp(prefix='lychee-test-'), 'stage')

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.stage), ignore_errors=True)

    def site(self, files):
        for relative, text in files.items():
            path = os.path.join(self.stage, *relative.split('/'))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(text)

    def test_a_clean_site_passes_at_three_bases_and_planted_faults_fail(self):
        for base in ('/', '/docs', '/x/y'):
            with self.subTest(base=base):
                shutil.rmtree(self.stage, ignore_errors=True)
                prefix = '' if base == '/' else base
                folder = prefix.strip('/')
                at = (folder + '/') if folder else ''
                self.site({
                    at + 'index.html': '<a href="%s/a/#part">a</a><a href="a/">a</a><link rel="stylesheet" href="%s/_astro/s.css">' % (prefix, prefix),
                    at + 'a/index.html': '<h2 id="part">Part</h2><a href="../#top">home</a><a href="#part">here</a>',
                    at + '_astro/s.css': 'body{background:url(./b.png)}',
                    at + '_astro/b.png': 'png',
                })
                self.assertEqual(crawl.lychee_problems(self.program, self.stage), [])
                self.site({
                    at + 'index.html': '<a href="%s/a/#nowhere">a</a><a href="%s/missing/">gone</a><a href="a/">a</a><link rel="stylesheet" href="%s/_astro/s.css">' % (prefix, prefix, prefix),
                    at + '_astro/s.css': 'body{background:url(./none.png)}',
                })
                problems = '\n'.join(crawl.lychee_problems(self.program, self.stage))
                self.assertIn('#nowhere', problems)
                self.assertIn('missing', problems)
                self.assertIn('none.png', problems)

    def test_what_lychee_reads_of_srcset_and_templates(self):
        # plan/site.md, confirm item 8: lychee 0.24.2 reads every srcset candidate and the links inside <template>;
        # where it does not, tools/crawl.py covers them (test_every_channel_a_page_loads_from_is_followed and the
        # links inside <template> in test_an_id_twice_on_a_page_fails). This test records what lychee does.
        self.site({
            'docs/index.html': '<img src="/docs/a.webp" srcset="/docs/a.webp 1x, /docs/missing-candidate.webp 2x">'
                               '<template data-book-track="game"><a href="/docs/missing-in-template/">next</a></template>',
            'docs/a.webp': 'a',
        })
        problems = '\n'.join(crawl.lychee_problems(self.program, self.stage))
        self.assertIn('missing-candidate.webp', problems)
        self.assertIn('missing-in-template', problems)

    def test_the_crawl_runs_lychee_over_its_staged_folder(self):
        root = os.path.dirname(self.stage)
        dist = os.path.join(root, 'dist')
        os.makedirs(os.path.join(dist, 'a'))
        files = {
            'index.html': '<link rel="canonical" href="https://example.com/docs/"><a href="/docs/a/">a</a>',
            'a/index.html': '<link rel="canonical" href="https://example.com/docs/a/"><style>p{background:url(#paint)}</style><p>x</p>',
            '404.html': '<meta name="robots" content="noindex"><link rel="stylesheet" href="/docs/s.css">',
            's.css': 'p{}',
        }
        for relative, text in files.items():
            with open(os.path.join(dist, *relative.split('/')), 'w', encoding='utf-8') as file:
                file.write(text)
        report = os.path.join(root, 'report.json')
        with contextlib.redirect_stdout(io.StringIO()):
            crawl.main(['--root', root, '--base', '/docs', '--site', 'https://example.com', '--report', report, '--lychee', self.program])
        with open(report, encoding='utf-8') as file:
            problems = json.load(file)['problems']
        # The style sheet's url(#paint) names an element the page lacks: the crawl itself does not read it, lychee does.
        self.assertTrue(any(problem.startswith('lychee: ') and '#paint' in problem for problem in problems), problems)


if __name__ == '__main__':
    unittest.main()
