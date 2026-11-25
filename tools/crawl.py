#!/usr/bin/env python3
"""The staged crawl: proves that the built site works under its base path on a plain static server.

    python tools/crawl.py                         stage dist/ under stage/<base>/, serve stage/, crawl from <base>/
    python tools/crawl.py --url http://127.0.0.1:8080/strata-engine-docs/
                                                  crawl a site another server serves (nginx, the container, the live
                                                  address); it only reads
    python tools/crawl.py --serve-only --port 4321
                                                  stage and serve for a person's browser until Ctrl+C

The crawler starts at <base>/ and follows every link, image (src, srcset, a video's poster, an object's data, an
SVG image's href), script, style sheet (and the fonts and images they load), module import (static and dynamic, in
quotes or backticks, in files and in inline scripts), fetch() and new URL(..., import.meta.url) of a literal path, the
web manifest, the sitemap and canonical links. It fails when anything answers other than 200, when a URL of the site
leaves the prefix, when a page or resource loads from another host, when a link names an anchor its page does not
have, when a page holds an id twice, when an HTML page of the build is never reached (an orphan), when any other file
of the build is referenced by nothing (the 404 page, Pagefind's files, the sitemaps, the manifest, the favicon and a
.gz beside its file are exempt; a .br, which a release never holds, and a .gz beside no file are not), and when a
canonical link, og:url or a sitemap <loc> is not on --site under the base (a canonical must name its own page; the
404 page has none, and no index), when a page holds an element of the class katex-error (a formula KaTeX drew in red
instead of failing the build), when the build holds a robots.txt (crawlers read only the host's own), when the
sitemap lists a page that asks search engines not to index it, when a print view (<base>/print/…) does not, and when
a built style sheet holds a font as a data: URL (the release's policy allows fonts only from the site), when a link
names a host that tools/external-hosts.txt does not list, when a link into the engine's repository (engine.pin's
"repository" followed by /blob/ or /tree/) names a commit that is not 40 hex digits, or another commit than the pin
outside a :::history aside, when anything names the book's own repository (it is closed source: rulings 6, R20), when
a URL path outside <base>/_astro/ holds a capital letter, when a URL path holds a character outside ASCII, when a URL
does not match a file of the build byte for byte (a wrong case that a case-insensitive disk would forgive), and, once
the build holds license.txt (plan/site.md, change 15), when an HTML file lacks the footer line: the copyright line
built from site.json and its links to <base>/license.txt and <base>/third-party-notices.txt. With --lychee it also
runs lychee 0.24.2 offline over the staged folder (plan/site.md, gate (a) 1) and reports what it fails on. The fallback
pages of moved pages (src/redirects.json) are crawled too: each must name the page it sends the reader to as its
refresh, its canonical link and its link, and ask not to be indexed. It also asks for a page that does not exist and
for every top folder without an index.html, to prove that its 404 page works under the prefix (the missing page three
levels deep, with every resource its 404 page loads from there), and, on its own staged server, for "/", to prove
that the site does not need the host's root. A server that already runs (--url) may answer "/" with a site of its
own, as a host with a site at its root does; a page that requests it still fails. With
--forbid-prefix it fails on any URL string of the build that starts with that prefix (a build for another base that
still names the default one). The static server behaves as the deployments do: index.html for folders, a redirect to
add the trailing slash, the site's 404.html with status 404 (folders without index.html included), no folder listings.

The base and the origin are site.json's (tools/booklib/settings.py), unless DOCS_BASE and DOCS_SITE (one build for
another place) or --base and --site say otherwise.

Only the standard library is used. Exit codes: 0 clean, 1 problems found, 2 usage errors.
"""

import argparse
import concurrent.futures
import gzip
import html.parser
import http.server
import json
import mimetypes
import os
import re
import shutil
import socketserver
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import deploy  # noqa: E402
from booklib import repo  # noqa: E402
from booklib import settings  # noqa: E402

c_Root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The hosts a page may link to (plan/site.md, gate (a)): adding one is a change a reviewer sees.
c_ExternalHosts = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'external-hosts.txt')
# The book's own repository: the site links nowhere in it, with any path or none (plan/critique/rulings-6.md, R20).
c_BookRepository = 'https://github.com/2042Third/strata-engine-docs'
# The level of scripts/precompress.mjs's .gz files, which are what a reader's browser receives (plan/site.md, budgets).
c_GzipLevel = 9
# Three levels deep (plan/site.md, gate (a)): the 404 page is served at any depth, so a resource it names relative to
# its own place (../_astro/x.css) would load at one level and fail at three.
c_MissingPage = 'this-page-does-not-exist-%d/a/b/' % os.getpid()
c_ParsedTypes = ('text/html', 'text/css', 'text/javascript', 'application/javascript', 'application/json', 'application/manifest+json', 'application/xml', 'text/xml')
c_Types = {
    '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json', '.webmanifest': 'application/manifest+json',
    '.xml': 'application/xml', '.svg': 'image/svg+xml', '.avif': 'image/avif', '.webp': 'image/webp', '.png': 'image/png',
    '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.wasm': 'application/wasm', '.txt': 'text/plain; charset=utf-8',
}


def normalize_base(value):
    """"/a/b" (no trailing slash), or "" for the root of the host, written "/": the rules of src/lib/settings.mjs. An
    empty value is refused, never read as the root."""
    value = (value or '').strip()
    if value == '':
        raise ValueError('the base is empty: leave DOCS_BASE unset for site.json\'s base, or write / for the root of the host')
    if value == '/':
        return ''
    if not value.startswith('/') or value.startswith('//'):
        raise ValueError('the base must be a path starting with "/": %r' % value)
    if not re.match(r'^[A-Za-z0-9/._~-]+$', value):
        raise ValueError('the base may hold only letters, digits and / . _ ~ -: %r' % value)
    base = value[:-1] if value.endswith('/') else value
    segments = base.split('/')[1:]
    if '' in segments:
        raise ValueError('the base has an empty segment ("//"): %r' % value)
    if '.' in segments or '..' in segments:
        raise ValueError('the base must not contain . or .. segments: %r' % value)
    return base


# ---------------------------------------------------------------------------------------------------------------------
# Staging and the static server


def stage(dist, stage_root, base):
    """Copies dist/ to <stage>/<base>/ (hard links where the file system allows, copies otherwise)."""
    if not os.path.isfile(os.path.join(dist, 'index.html')):
        raise ValueError('%s has no index.html: build the site first' % dist)
    if os.path.exists(stage_root):
        shutil.rmtree(stage_root)
    target = os.path.join(stage_root, *[part for part in base.split('/') if part])

    def link_or_copy(source, destination):
        try:
            os.link(source, destination)
        except OSError:
            shutil.copy2(source, destination)
    shutil.copytree(dist, target, copy_function=link_or_copy)
    return target


class StaticHandler(http.server.BaseHTTPRequestHandler):
    """Serves the staged folder the way the deployments of deploy/ do."""

    root = None
    base = ''
    protocol_version = 'HTTP/1.1'

    def log_message(self, format, *arguments):  # noqa: A002 (the name is http.server's)
        pass

    def send_file(self, path, status, head):
        size = os.path.getsize(path)
        self.send_response(status)
        extension = os.path.splitext(path)[1].lower()
        self.send_header('Content-Type', c_Types.get(extension) or mimetypes.guess_type(path)[0] or 'application/octet-stream')
        self.send_header('Content-Length', str(size))
        self.end_headers()
        if not head:
            with open(path, 'rb') as file:
                shutil.copyfileobj(file, self.wfile)

    def send_plain(self, status, text, head, headers=None):
        body = text.encode('utf-8')
        self.send_response(status)
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def serve(self, head):
        path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        local = os.path.normpath(os.path.join(self.root, path.lstrip('/')))
        if os.path.commonpath([self.root, local]) != self.root:
            return self.send_plain(400, 'bad path', head)
        if os.path.isdir(local):
            if not path.endswith('/'):
                return self.send_plain(301, 'moved', head, {'Location': path + '/'})
            index = os.path.join(local, 'index.html')
            if os.path.isfile(index):
                return self.send_file(index, 200, head)
        elif os.path.isfile(local):
            return self.send_file(local, 200, head)
        not_found = os.path.join(self.root, self.base.lstrip('/'), '404.html')
        if path.startswith(self.base + '/') and os.path.isfile(not_found):
            return self.send_file(not_found, 404, head)
        return self.send_plain(404, 'not found', head)

    def do_GET(self):  # noqa: N802 (http.server's name)
        self.serve(False)

    def do_HEAD(self):  # noqa: N802
        self.serve(True)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def handle_error(self, request, client_address):
        # A browser closes connections it no longer needs when a page moves on (the browser checks of scripts/ serve
        # the build through this server): that is no error of the site, and its traceback would bury the checks' output.
        if isinstance(sys.exc_info()[1], (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


def start_server(stage_root, base, port=0):
    handler = type('Handler', (StaticHandler,), {'root': os.path.abspath(stage_root), 'base': base})
    server = Server(('127.0.0.1', port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ---------------------------------------------------------------------------------------------------------------------
# Reading pages


class PageParser(html.parser.HTMLParser):
    """Collects what an HTML page references and the anchors it defines."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []  # (url, kind) kind: link | history-link (a link inside a :::history aside) | resource | canonical
        self.anchors = set()
        self.in_style = False
        self.styles = []
        self.in_template = 0
        self.in_script = False
        self.scripts = []
        self.canonical = []
        self.robots = []
        self.id_counts = {}
        self.katex_errors = []
        self.moved = None  # the new page's path, on the fallback page of a moved page
        self.refresh = None
        self.asides = []  # one entry per open <aside>: whether it is a :::history aside
        self.script_sources = []  # the scripts the page loads: <script src> and <link rel="modulepreload">
        self.text = []  # the page's text, for the footer line
        self.navs = []  # (is the sidebar, start offset) of each open <nav>
        self.sidebar_bytes = 0  # the size of Starlight's sidebar (<nav aria-label="Main">), its markup included

    def position(self):
        """The parser's place in the document as a character index (HTMLParser counts lines and columns)."""
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def feed(self, data):
        # Line starts, so that offset() can turn the parser's (line, column) into an index of the text.
        starts = [0]
        for index, character in enumerate(data):
            if character == '\n':
                starts.append(index + 1)
        self.line_starts = starts
        self.document = data
        super().feed(data)

    def handle_starttag(self, tag, attributes):
        values = dict(attributes)
        if tag == 'aside':
            self.asides.append('book-aside--history' in (values.get('class') or '').split())
        if tag == 'nav':
            self.navs.append(((values.get('aria-label') or '') == 'Main', self.position()))
        if tag == 'script' and values.get('src'):
            self.script_sources.append(values['src'])
        if tag == 'link' and values.get('href') and 'modulepreload' in (values.get('rel') or '').lower().split():
            self.script_sources.append(values['href'])
        if tag == 'template':
            self.in_template += 1
        if values.get('id'):
            self.anchors.add(values['id'])
            # Ids inside a <template> are not in the document until a script copies them out.
            if not self.in_template:
                self.id_counts[values['id']] = self.id_counts.get(values['id'], 0) + 1
        if tag == 'a' and values.get('name'):
            self.anchors.add(values['name'])
        if tag == 'a' and values.get('href') is not None:
            self.references.append((values['href'], 'history-link' if any(self.asides) else 'link'))
        elif tag == 'link' and values.get('href'):
            rel = (values.get('rel') or '').lower().split()
            if 'canonical' in rel:
                kind = 'canonical'
                self.canonical.append(values['href'])
            else:
                kind = 'link' if set(rel) & {'alternate', 'sitemap', 'prev', 'next'} else 'resource'
            self.references.append((values['href'], kind))
        elif tag in ('script', 'img', 'iframe', 'audio', 'video', 'source', 'track', 'embed', 'input') and values.get('src'):
            self.references.append((values['src'], 'resource'))
        if tag in ('img', 'source') and values.get('srcset'):
            for candidate in values['srcset'].split(','):
                url = candidate.strip().split(' ')[0]
                if url:
                    self.references.append((url, 'resource'))
        if tag == 'video' and values.get('poster'):
            self.references.append((values['poster'], 'resource'))
        if tag == 'object' and values.get('data'):
            self.references.append((values['data'], 'resource'))
        if tag in ('image', 'use', 'feimage'):
            # SVG: href, or the older xlink:href.
            href = values.get('href') or values.get('xlink:href')
            if href:
                self.references.append((href, 'resource'))
        if tag == 'meta' and (values.get('property') or '').startswith('og:') and (values.get('property') or '').endswith(('image', 'url')) and values.get('content'):
            if values['property'].endswith('url'):
                self.canonical.append(values['content'])
            self.references.append((values['content'], 'canonical' if values['property'].endswith('url') else 'resource'))
        if tag == 'meta' and (values.get('name') or '').lower() == 'robots':
            self.robots.append((values.get('content') or '').lower())
        if tag == 'meta' and values.get('name') == deploy.c_MovedMeta:
            self.moved = values.get('content') or ''
        if tag == 'meta' and (values.get('http-equiv') or '').lower() == 'refresh':
            self.refresh = values.get('content') or ''
            match = re.match(r'^\s*\d+\s*;\s*url=(.+)$', self.refresh, re.IGNORECASE)
            if match:
                self.references.append((match.group(1).strip(), 'link'))
        if 'katex-error' in (values.get('class') or '').split():
            self.katex_errors.append(values.get('title') or '')
        if values.get('style'):
            self.styles.append(values['style'])
        if tag == 'style':
            self.in_style = True
        if tag == 'script' and not values.get('src') and (values.get('type') or 'text/javascript').lower() in ('text/javascript', 'module', 'application/javascript'):
            self.in_script = True
            self.scripts.append('')

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False
        if tag == 'script':
            self.in_script = False
        if tag == 'template' and self.in_template:
            self.in_template -= 1
        if tag == 'aside' and self.asides:
            self.asides.pop()
        if tag == 'nav' and self.navs:
            sidebar, start = self.navs.pop()
            if sidebar:
                # From its start tag to the end of its end tag ("</nav>"), in UTF-8 bytes as the page is served.
                self.sidebar_bytes += len(self.document[start:self.position() + len('</nav>')].encode('utf-8'))

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)
        if self.in_script:
            self.scripts[-1] += data
        if not self.in_style and not self.in_script:
            self.text.append(data)


def font_data_urls(text):
    """The fonts a style sheet holds as data: URLs (rulings 6, R23: the policy's font-src 'self' would block them)."""
    return re.findall(r'url\(\s*["\']?(data:(?:font/|application/(?:x-)?font)[^;,"\')]*)', text, re.IGNORECASE)


def css_references(text):
    found = re.findall(r'url\(\s*(["\']?)([^"\')]+)\1\s*\)', text)
    found = [url for _, url in found]
    found += re.findall(r'@import\s+["\']([^"\']+)["\']', text)
    return [url for url in found if not url.startswith('data:') and not url.startswith('#')]


# A string literal in quotes or backticks; a template with "${" in it names no fixed file and is left alone.
c_Literal = r'''(["'`])((?:(?!\1)[^\\$\n]|\$(?!\{))+)\1'''
c_ScriptPatterns = [
    # import x from "./a.js", export * from "./b.js", import "./c.js"
    re.compile(r'''(?:^|[;\s}])(?:import|export)\s*(?:[\w*{}\s,$]+?\s*from\s*)?''' + c_Literal, re.MULTILINE),
    # import("./d.js"), import(`./e.js`): Vite 8 writes dynamic imports with backticks.
    re.compile(r'''\bimport\s*\(\s*''' + c_Literal + r'''\s*\)'''),
    # fetch("/x.json") and new URL("./y.wasm", import.meta.url)
    re.compile(r'''\bfetch\s*\(\s*''' + c_Literal),
    re.compile(r'''\bnew\s+URL\s*\(\s*''' + c_Literal + r'''\s*,\s*import\.meta\.url'''),
]


def js_references(text, static_only=False):
    """Paths a script loads that a crawl can follow: literals starting with "./", "../" or "/". With static_only,
    only its static imports and exports, which the browser loads with it (not import(), fetch() or new URL())."""
    found = []
    for pattern in c_ScriptPatterns[:1] if static_only else c_ScriptPatterns:
        for match in pattern.finditer(text):
            url = match.group(match.lastindex)
            if url.startswith(('./', '../', '/')) and not url.startswith('//'):
                found.append(url)
    return found


def forbidden_prefix_uses(folder, prefix):
    """(file, text) of every URL string of the build that starts with `prefix`: a quoted, parenthesized or attribute
    value, or a URL whose path starts with it right after the host. Links to the repository of the same name
    (github.com/<owner>/strata-engine-docs) are not URLs of the site."""
    pattern = re.compile(r'''(?:["'`(=\s]|//[A-Za-z0-9.-]+(?::\d+)?)''' + re.escape(prefix) + r'''(?=[/"'`)?#\s<]|$)''', re.MULTILINE)
    found = []
    for current, _, names in os.walk(folder):
        for name in sorted(names):
            if os.path.splitext(name)[1].lower() not in ('.html', '.css', '.js', '.mjs', '.json', '.xml', '.webmanifest', '.svg', '.txt'):
                continue
            path = os.path.join(current, name)
            with open(path, encoding='utf-8', errors='replace') as file:
                for match in pattern.finditer(file.read()):
                    found.append((os.path.relpath(path, folder).replace(os.sep, '/'), match.group(0).strip()))
    return found


# ---------------------------------------------------------------------------------------------------------------------
# The crawl


class Crawl:
    def __init__(self, start, base, site, workers):
        self.start = start
        self.base = base
        self.origin = '{0.scheme}://{0.netloc}'.format(urllib.parse.urlsplit(start))
        self.site = site.rstrip('/')
        self.workers = workers
        self.lock = threading.Lock()
        self.seen = set()
        self.results = {}
        self.anchors = {}
        self.fragments = []  # (from url, target url, fragment)
        self.problems = []
        self.external_links = set()
        self.html_bytes = {}
        self.noindex = set()  # pages that ask search engines not to index them
        self.listed = set()  # pages a sitemap lists
        self.moved = {}  # the old address of a moved page: the URL of its new page
        self.external_hosts = None  # the hosts a link may name (tools/external-hosts.txt); None checks none
        self.engine = None  # {"repository", "commit"} of engine.pin; None checks no engine link
        self.page_scripts = {}  # page URL: the URLs of the scripts it loads
        self.script_imports = {}  # script URL: the URLs it imports statically
        self.script_gzip = {}  # script URL: its size gzipped
        self.inline_script_gzip = {}  # page URL: the size of its inline scripts, each gzipped
        self.sidebar_bytes = {}  # page URL: the size of its sidebar's markup
        self.footers = {}  # page URL: (the page's text, the URLs it links to), for the footer line

    def problem(self, message):
        with self.lock:
            self.problems.append(message)

    def check_external_link(self, absolute, page, history):
        """A link to another host: the host is one tools/external-hosts.txt lists, the book's own repository is never
        named, and a link into the engine's repository at a commit names the pin (outside a :::history aside)."""
        parts = urllib.parse.urlsplit(absolute)
        host = (parts.hostname or '').lower()
        if self.external_hosts is not None and host not in self.external_hosts:
            self.problem('%s links to %s: the host %s is not in tools/external-hosts.txt (add it there if the link is meant)' % (page, absolute, host))
        book = urllib.parse.urlsplit(c_BookRepository)
        path = parts.path.rstrip('/').lower()
        if host == book.hostname and (path == book.path.lower() or path.startswith(book.path.lower() + '/')):
            self.problem('%s names the book\'s repository (%s): the book is closed source, and the site links nowhere in it' % (page, absolute))
        if self.engine:
            repository = self.engine['repository'].rstrip('/')
            for kind in ('/blob/', '/tree/'):
                if absolute.startswith(repository + kind):
                    commit = absolute[len(repository + kind):].split('/')[0].split('#')[0].split('?')[0]
                    if not re.match(r'^[0-9a-f]{40}$', commit):
                        self.problem('%s links to %s: a link into the engine names a full commit (40 hex digits), not %r' % (page, absolute, commit))
                    elif commit != self.engine['commit'] and not history:
                        self.problem('%s links to %s at the commit %s, not the pin %s (only a :::history aside links another commit)' % (page, absolute, commit, self.engine['commit']))

    def local(self, url):
        """Maps a URL on the site's public origin (canonical links, the sitemap) to the server being crawled."""
        if self.site and url.startswith(self.site + '/'):
            return self.origin + url[len(self.site):]
        return url

    def check_canonical(self, raw, page, own_page):
        """A canonical link, og:url or sitemap <loc> is a URL on --site under the base; a page's own canonical names
        that page. Returns False when it does not (reported)."""
        expected_start = self.site + self.base + '/'
        if not (raw == expected_start or raw.startswith(expected_start)):
            self.problem('%s: %s is not on the site %s under %s/ (was it built with another DOCS_SITE, or is --site wrong?)' % (page, raw, self.site, self.base))
            return False
        if own_page and self.local(raw).split('#')[0] != page:
            self.problem('%s: its canonical URL %s names another page' % (page, raw))
        return True

    def classify(self, raw, page, kind, history=False):
        """None (ignored), or the absolute URL to fetch; reports URLs that leave the site. `history` says the link
        stands in a :::history aside, which may link the engine at another commit."""
        raw = raw.strip()
        if not raw or raw.startswith(('mailto:', 'data:', 'tel:')):
            return None
        if raw.lower().startswith('javascript:'):
            self.problem('%s: a javascript: URL (%s)' % (page, raw))
            return None
        absolute = self.local(urllib.parse.urljoin(page, raw))
        parts = urllib.parse.urlsplit(absolute)
        if parts.scheme not in ('http', 'https'):
            return None
        origin = '%s://%s' % (parts.scheme, parts.netloc)
        if origin != self.origin:
            if kind == 'resource':
                self.problem('%s loads %s from another host: the site must work offline' % (page, raw))
            else:
                with self.lock:
                    self.external_links.add(absolute.split('#')[0])
                self.check_external_link(absolute, page, history)
            return None
        if not (parts.path == self.base + '/' or parts.path.startswith(self.base + '/')) and self.base:
            self.problem('%s: %s leaves the prefix %s/' % (page, raw, self.base))
            return None
        if kind == 'canonical':
            kind = 'link'
        if parts.fragment:
            with self.lock:
                self.fragments.append((page, urllib.parse.urlunsplit(parts._replace(fragment='')), urllib.parse.unquote(parts.fragment)))
        return urllib.parse.urlunsplit(parts._replace(fragment=''))

    def fetch(self, url, method='GET'):
        request = urllib.request.Request(url, method=method, headers={'User-Agent': 'strata-book-crawl'})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.status, response.headers.get('Content-Type', ''), response.read() if method == 'GET' else b'', response.geturl()
        except urllib.error.HTTPError as error:
            return error.code, error.headers.get('Content-Type', ''), error.read() if method == 'GET' else b'', url
        except (urllib.error.URLError, OSError) as error:
            return None, '', str(error).encode('utf-8'), url

    def visit(self, url, referrer):
        parsed = urllib.parse.urlsplit(url).path
        extension = os.path.splitext(parsed)[1].lower()
        method = 'GET' if (parsed.endswith('/') or extension in ('', '.html', '.css', '.js', '.mjs', '.json', '.webmanifest', '.xml')) else 'HEAD'
        status, content_type, body, final = self.fetch(url, method)
        found = []
        with self.lock:
            self.results[url] = {'status': status, 'type': content_type, 'bytes': len(body), 'referrer': referrer}
        if status != 200:
            self.problem('%s answers %s (linked from %s)' % (url, status, referrer))
            return found
        if final != url and self.moved.get(url) == final:
            # A server with the release's rules answers the old address of a moved page with a 301 to its new page
            # (nginx-redirects.conf), before its fallback page is ever read; the new page is crawled on its own.
            return found
        if final != url:
            self.problem('%s redirects to %s (linked from %s): link to the final URL' % (url, final, referrer))
        mime = content_type.split(';')[0].strip()
        text = body.decode('utf-8', 'replace') if mime in c_ParsedTypes else ''
        if mime == 'text/html':
            parser = PageParser()
            parser.feed(text)
            with self.lock:
                self.anchors[url] = parser.anchors
                self.html_bytes[url] = body
                if any('noindex' in robots for robots in parser.robots):
                    self.noindex.add(url)
            if parser.katex_errors:
                # site.md, "Math": the build fails on a formula KaTeX cannot render; this is the net behind it.
                self.problem('%s holds %d formula%s KaTeX could not render (class katex-error): %s' % (url, len(parser.katex_errors), '' if len(parser.katex_errors) == 1 else 's', '; '.join(parser.katex_errors[:3])))
            if parser.moved is not None:
                self.check_moved(url, parser)
            repeated = sorted(name for name, count in parser.id_counts.items() if count > 1)
            if repeated:
                self.problem('%s has %d id%s more than once (a link to it jumps to the first): %s' % (url, len(repeated), '' if len(repeated) == 1 else 's', ', '.join(repeated[:8]) + (' …' if len(repeated) > 8 else '')))
            links = set()
            for raw, kind in parser.references:
                if kind == 'canonical' and not self.check_canonical(raw, url, parser.moved is None):
                    continue
                history = kind == 'history-link'
                kind = 'link' if history else kind
                target = self.classify(raw, url, kind, history)
                found.append((target, url))
                if kind == 'link' and target:
                    links.add(target)
            scripts = [self.local(urllib.parse.urljoin(url, raw)).split('#')[0] for raw in parser.script_sources]
            with self.lock:
                self.page_scripts[url] = scripts
                self.inline_script_gzip[url] = sum(len(gzip.compress(script.encode('utf-8'), c_GzipLevel)) for script in parser.scripts if script.strip())
                self.sidebar_bytes[url] = parser.sidebar_bytes
                self.footers[url] = (' '.join(' '.join(parser.text).split()), links)
            for style in parser.styles:
                found.extend((self.classify(raw, url, 'resource'), url) for raw in css_references(style))
            for script in parser.scripts:
                found.extend((self.classify(raw, url, 'resource'), url) for raw in js_references(script))
        elif mime == 'text/css':
            for font in font_data_urls(text):
                self.problem('%s holds a font as a data: URL (%s…): the policy allows fonts only from the site; the build '
                             'inlines no font (src/lib/assets.mjs)' % (url, font[:40]))
            found.extend((self.classify(raw, url, 'resource'), url) for raw in css_references(text))
        elif mime in ('text/javascript', 'application/javascript'):
            found.extend((self.classify(raw, url, 'resource'), url) for raw in js_references(text))
            with self.lock:
                self.script_gzip[url] = len(gzip.compress(body, c_GzipLevel))
                self.script_imports[url] = [urllib.parse.urljoin(url, raw) for raw in js_references(text, static_only=True)]
        elif mime == 'application/manifest+json':
            try:
                manifest = json.loads(text)
            except ValueError:
                self.problem('%s is not valid JSON' % url)
                manifest = {}
            for raw in [manifest.get('start_url'), manifest.get('scope')] + [icon.get('src') for icon in manifest.get('icons', [])]:
                if raw:
                    found.append((self.classify(raw, url, 'link'), url))
        elif mime in ('application/xml', 'text/xml'):
            for raw in re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', text):
                if self.check_canonical(raw, url, False):
                    listed = self.classify(raw, url, 'link')
                    found.append((listed, url))
                    if listed and not listed.endswith('.xml'):
                        with self.lock:
                            self.listed.add(listed)
        return found

    def check_moved(self, url, parser):
        """The fallback page of a moved page sends the reader to its new page under the base, by its refresh, its
        canonical link and a link, and is not indexed (site.md, "Moved pages")."""
        target = parser.moved
        if not (target == self.base + '/' or target.startswith(self.base + '/')):
            self.problem('%s: a moved page names %s, which is not under %s/' % (url, target, self.base))
            return
        if not parser.refresh or not re.match(r'^\s*0\s*;\s*url=%s\s*$' % re.escape(target), parser.refresh, re.IGNORECASE):
            self.problem('%s: a moved page refreshes to %r, not to its new page %s' % (url, parser.refresh, target))
        if parser.canonical != [self.site + target]:
            self.problem('%s: a moved page names %s as its canonical URL, not its new page %s' % (url, parser.canonical or 'nothing', self.site + target))
        if not any(urllib.parse.urljoin(url, raw).split('#')[0] == self.origin + target for raw, kind in parser.references if kind == 'link'):
            self.problem('%s: a moved page has no plain link to its new page %s' % (url, target))
        if not any('noindex' in robots for robots in parser.robots):
            self.problem('%s: a moved page has no <meta name="robots" content="noindex">' % url)

    def check_indexing(self):
        """The sitemap lists only pages for finding, and the print views ask not to be indexed (site.md, "Navigation"):
        a page that says "noindex" has no place in the sitemap."""
        for url in sorted(self.listed & self.noindex):
            self.problem('%s is in the sitemap but asks search engines not to index it (noindex): the sitemap\'s filter '
                         '(src/lib/sitemap.mjs) leaves such pages out' % url)
        prefix = self.start + 'print/'
        for url in sorted(self.html_bytes):
            if url.startswith(prefix) and url not in self.noindex:
                self.problem('%s is a print view without <meta name="robots" content="noindex">: print views repeat the '
                             'book\'s pages for printing, not for search engines' % url)

    def run(self, extra=()):
        queue = [(self.start, '(start)')] + [(url, '(checks)') for url in extra]
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as pool:
            pending = set()
            while queue or pending:
                while queue:
                    url, referrer = queue.pop()
                    if url is None or url in self.seen:
                        continue
                    self.seen.add(url)
                    pending.add(pool.submit(self.visit, url, referrer))
                done, pending = concurrent.futures.wait(pending, return_when=concurrent.futures.FIRST_COMPLETED)
                for future in done:
                    queue.extend(future.result())

    def check_fragments(self):
        for page, target, fragment in self.fragments:
            anchors = self.anchors.get(target)
            if anchors is not None and fragment not in anchors:
                self.problem('%s links to %s#%s, which has no element with that id' % (page, target, fragment))


def page_urls_of(stage_folder, prefix_url):
    """The URL of every HTML page of the staged build except the 404 page."""
    urls = {}
    for folder, _, files in os.walk(stage_folder):
        for name in files:
            if not name.endswith('.html') or (name == '404.html' and folder == stage_folder):
                continue
            relative = os.path.relpath(os.path.join(folder, name), stage_folder).replace(os.sep, '/')
            url = prefix_url + (relative[:-len('index.html')] if relative.endswith('index.html') else relative)
            urls[url] = relative
    return urls


def check_root_and_missing(crawl, base_url, site_root, own_server=True):
    """The host's root is not part of the site, and a missing page gets the site's 404 page with its resources. On
    the crawl's own server the root answers nothing; a server that already runs may serve a site of its own there."""
    if own_server:
        status, _, _, _ = crawl.fetch(site_root)
        if status == 200 and base_url != site_root:
            crawl.problem('%s answers 200: the site must not need the host\'s root (is something deployed there?)' % site_root)
    missing = base_url + c_MissingPage
    status, content_type, body, _ = crawl.fetch(missing)
    if status != 404:
        crawl.problem('%s answers %s instead of 404' % (missing, status))
        return []
    if not content_type.startswith('text/html'):
        crawl.problem('%s answers 404 without the site\'s 404 page' % missing)
        return []
    parser = PageParser()
    parser.feed(body.decode('utf-8', 'replace'))
    resources = [crawl.classify(raw, missing, kind) for raw, kind in parser.references if kind == 'resource']
    if not resources:
        crawl.problem('the 404 page at %s loads no style sheet: it is not the site\'s page' % missing)
    # A canonical URL or og:url on the 404 page names an address that answers 404; search engines must not index it.
    for raw in parser.canonical:
        crawl.problem('the 404 page names %s as its canonical URL or og:url, an address that is not a page' % raw)
    if not any('noindex' in robots for robots in parser.robots):
        crawl.problem('the 404 page has no <meta name="robots" content="noindex">')
    return [url for url in resources if url]


def check_folders(crawl, base_url, site_folder):
    """Every top folder of the site without an index.html (a part's folder, _astro/) answers the site's 404 page with
    status 404: no listing, and no bare error page of the server."""
    not_found = os.path.join(site_folder, '404.html')
    if not os.path.isfile(not_found):
        return
    with open(not_found, 'rb') as file:
        expected = file.read()
    for name in sorted(os.listdir(site_folder)):
        folder = os.path.join(site_folder, name)
        if os.path.isdir(folder) and not os.path.isfile(os.path.join(folder, 'index.html')):
            url = base_url + name + '/'
            status, _, body, _ = crawl.fetch(url)
            if status != 404 or body != expected:
                crawl.problem('%s (a folder without index.html) answers %s%s, not the site\'s 404 page' % (url, status, '' if body == expected else ' with another page'))


def is_unreferenced_exempt(relative, present):
    """The files of a build that no page, style sheet or script needs to name (plan/site.md, gate (a)): the 404 page,
    which the server sends for a missing address; Pagefind's files, which its script fetches by names it builds; the
    sitemaps, the manifest and the favicon, which crawlers and browsers ask for by their names; and a .gz beside
    another file, which nginx's gzip_static sends in that file's place. A .br is not exempt: a release holds none."""
    if relative in ('404.html', 'manifest.webmanifest', 'favicon.svg') or relative.startswith('pagefind/'):
        return True
    if re.match(r'^sitemap-[^/]*\.xml$', relative):
        return True
    return relative.endswith('.gz') and relative[:-len('.gz')] in present


def check_unreferenced(crawl, site_folder):
    """Every file of the build is asked for by the crawl, which follows every reference of the site, unless it is
    exempt (is_unreferenced_exempt): a file nothing names is either dead weight or something a reader cannot reach."""
    fetched = set()
    for url in crawl.results:
        path = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
        fetched.add(path)
        if path.endswith('/'):
            fetched.add(path + 'index.html')
    files = []
    for folder, directories, names in os.walk(site_folder):
        directories.sort()
        for name in names:
            files.append(os.path.relpath(os.path.join(folder, name), site_folder).replace(os.sep, '/'))
    present = set(files)
    for relative in sorted(files):
        if is_unreferenced_exempt(relative, present) or '%s/%s' % (crawl.base, relative) in fetched:
            continue
        if relative.endswith('.br'):
            crawl.problem('%s is referenced by nothing: a release holds no .br file, because no stock nginx serves brotli '
                          '(node scripts/precompress.mjs writes only .gz)' % relative)
        elif relative.endswith('.gz'):
            crawl.problem('%s stands beside no file of the build, so nothing serves it: run node scripts/precompress.mjs '
                          'on a fresh build' % relative)
        else:
            crawl.problem('%s is referenced by nothing: no page, style sheet or script of the build links or loads it' % relative)


def check_no_robots(crawl, site_folder):
    """The build holds no robots.txt (site.md, "The base path", rule 5): crawlers read only <host>/robots.txt, so one
    under the base is never read, and one at the root of a host would rule over every other site of that host. The
    host's own file names the book's sitemap (deploy/README.md)."""
    for folder, _, names in os.walk(site_folder):
        for name in sorted(names):
            if name.lower() == 'robots.txt':
                relative = os.path.relpath(os.path.join(folder, name), site_folder).replace(os.sep, '/')
                crawl.problem('%s: the build holds no robots.txt; crawlers read only the host\'s own, which names the book\'s sitemap (deploy/README.md)' % relative)


def read_external_hosts(path):
    """The hosts of tools/external-hosts.txt: one per line, lowercase; "#" starts a comment."""
    hosts = set()
    with open(path, encoding='utf-8') as file:
        for number, raw in enumerate(file, 1):
            line = raw.split('#', 1)[0].strip()
            if not line:
                continue
            if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$', line):
                raise ValueError('%s:%d: %r is not a host name in lowercase (one per line, no scheme or path)' % (path, number, line))
            hosts.add(line)
    return hosts


def file_of(relative, site_folder):
    """The file of the build a path below the base names (a folder's index.html), or None when none exists."""
    path = os.path.join(site_folder, *[part for part in relative.split('/') if part])
    if relative == '' or relative.endswith('/'):
        path = os.path.join(path, 'index.html')
    return path if os.path.isfile(path) else None


def exact_case(site_folder, path):
    """Whether every component of `path` (below site_folder) is spelled as the file system lists it: a URL that a
    case-insensitive disk serves can still fail on the Linux servers (plan/site.md, "Every way the site can leave the
    base": case)."""
    current = site_folder
    for part in os.path.relpath(path, site_folder).split(os.sep):
        if part not in os.listdir(current):
            return False
        current = os.path.join(current, part)
    return True


def check_case(crawl, site_folder):
    """Every URL the crawl fetched under the base: no character outside ASCII, no capital letter outside _astro/
    (where Vite and KaTeX name the files; page ids, pictures, downloads and Pagefind's files are lowercase: plan/site.md,
    "The base path", rule 8), and a file of the build whose name matches it byte for byte."""
    for url in sorted(crawl.results):
        if crawl.results[url]['status'] != 200:
            continue
        raw_path = urllib.parse.urlsplit(url).path
        path = urllib.parse.unquote(raw_path)
        if not (path == crawl.base + '/' or path.startswith(crawl.base + '/')):
            continue
        relative = path[len(crawl.base) + 1:]
        if any(ord(character) > 127 for character in path):
            crawl.problem('%s: a URL path holds a character outside ASCII (page ids and file names are lowercase ASCII)' % url)
        elif not relative.startswith('_astro/') and relative != relative.lower():
            crawl.problem('%s: a URL path holds a capital letter (page ids and file names below the base are lowercase; only _astro/ keeps Vite\'s names)' % url)
        local = file_of(relative, site_folder)
        if local and not exact_case(site_folder, local):
            crawl.problem('%s does not match a file of the build byte for byte (its case differs): a Linux server answers 404' % url)


def footer_line(copyright):
    """The copyright line of every page's footer, built from site.json (plan/site.md, "The copyright statement")."""
    return 'Copyright © %d %s. All rights reserved.' % (copyright['year'], copyright['holder'])


def check_footer(crawl, site_folder, copyright):
    """Every HTML page the crawl read holds the footer line and links to <base>/license.txt and
    <base>/third-party-notices.txt (rulings 6, R20). The build writes license.txt from LICENSE (plan/site.md, change
    15): before that exists there is no footer to check, and the crawl says so. Returns whether it checked."""
    if not os.path.isfile(os.path.join(site_folder, 'license.txt')):
        return False
    if copyright is None:
        crawl.problem('the build holds license.txt, but the footer line cannot be checked without site.json\'s copyright')
        return True
    line = footer_line(copyright)
    targets = [crawl.start + name for name in ('license.txt', 'third-party-notices.txt')]
    for url in sorted(crawl.footers):
        text, links = crawl.footers[url]
        missing = [target[len(crawl.start):] for target in targets if target not in links]
        if line not in text:
            crawl.problem('%s lacks the footer line "%s"' % (url, line))
        if missing:
            crawl.problem('%s: its footer does not link %s' % (url, ' and '.join('<base>/' + name for name in missing)))
    return True


def script_bytes_of_pages(crawl):
    """Page URL: the gzip size of the scripts it loads without searching (its inline scripts, the scripts it names and
    what they import statically; Pagefind's files only load when a reader searches): budget row 11."""
    sizes = {}
    for page, scripts in crawl.page_scripts.items():
        seen = set()
        queue = [script for script in scripts if '/pagefind/' not in script]
        while queue:
            script = queue.pop()
            if script in seen:
                continue
            seen.add(script)
            queue.extend(target for target in crawl.script_imports.get(script, []) if '/pagefind/' not in target)
        sizes[page] = crawl.inline_script_gzip.get(page, 0) + sum(crawl.script_gzip.get(script, 0) for script in seen)
    return sizes


def lychee_problems(program, stage_root):
    """lychee 0.24.2 offline over the staged folder (plan/site.md, gate (a) 1): every page and style sheet, links and
    fragments resolved against the staged files, with root-relative URLs read from the folder that holds <base>/.
    Returns the failures as problems; raises OSError when lychee cannot run."""
    stage_root = os.path.abspath(stage_root)
    stage_name = os.path.basename(stage_root)
    handle, output = tempfile.mkstemp(prefix='lychee-', suffix='.json')
    os.close(handle)
    try:
        # Relative globs from the stage's parent, as plan/site.md writes the command; lychee expands them itself. A
        # link to a folder means its index.html, as the servers read it (--index-files): without it lychee accepts any
        # folder that exists and finds no fragment of its page ("core/time/#steps" would fail).
        command = [program, '--offline', '--root-dir', stage_root, '--include-fragments', '--index-files', 'index.html',
                   '--no-progress', '--format', 'json', '--output', output, '%s/**/*.html' % stage_name, '%s/**/*.css' % stage_name]
        result = subprocess.run(command, cwd=os.path.dirname(stage_root), capture_output=True, text=True, encoding='utf-8', errors='replace')
        try:
            with open(output, encoding='utf-8') as file:
                report = json.load(file)
        except (OSError, ValueError):
            report = None
    finally:
        os.remove(output)
    if report is None:
        raise OSError('lychee wrote no report (exit %d): %s' % (result.returncode, (result.stderr or result.stdout).strip()[-500:]))
    problems = []
    for source, failures in sorted((report.get('error_map') or {}).items()):
        for failure in failures:
            status = failure.get('status') or {}
            reason = status.get('text') or status.get('details') or json.dumps(status)
            problems.append('lychee: %s: %s: %s' % (os.path.relpath(source, stage_root).replace(os.sep, '/') if os.path.isabs(source) else source, failure.get('url'), reason))
    if result.returncode != 0 and not problems:
        problems.append('lychee exited %d without naming a failure: %s' % (result.returncode, (result.stderr or result.stdout).strip()[-500:]))
    return problems


def summarize(crawl, stage_folder, started):
    pages = {url: body for url, body in crawl.html_bytes.items()}
    # Print views hold a whole part on one page; they are measured apart from the chapters readers open.
    printed = crawl.start + 'print/'
    sized = sorted(((len(gzip.compress(body, c_GzipLevel)), len(body), url) for url, body in pages.items()), reverse=True)
    every_chapter = [entry for entry in sized if not entry[2].startswith(printed)]
    chapters = every_chapter[:5]
    prints = [entry for entry in sized if entry[2].startswith(printed)][:5]
    scripts = script_bytes_of_pages(crawl)
    heaviest_scripts = max(((size, url) for url, size in scripts.items() if not url.startswith(printed)), default=(0, None))
    sidebar = max(((crawl.sidebar_bytes.get(url, 0), raw, url) for _, raw, url in every_chapter), default=(0, 0, None))
    total = 0
    search = 0
    files = 0
    if stage_folder:
        for folder, _, names in os.walk(stage_folder):
            for name in names:
                # Apparent sizes before precompression (plan/site.md, "Budgets and the spike"): a .gz beside its file
                # is the release's copy of that file, not more of the site.
                if name.endswith('.gz') and name[:-len('.gz')] in names:
                    continue
                size = os.path.getsize(os.path.join(folder, name))
                total += size
                files += 1
                if os.sep + 'pagefind' in folder or folder.endswith('pagefind'):
                    search += size
    return {
        'seconds': round(time.monotonic() - started, 2),
        'requests': len(crawl.results),
        'pages': len(pages),
        'external_links': len(crawl.external_links),
        'largest_pages': [{'url': url, 'bytes': raw, 'gzip_bytes': packed} for packed, raw, url in chapters],
        'largest_print_pages': [{'url': url, 'bytes': raw, 'gzip_bytes': packed} for packed, raw, url in prints],
        # Budget rows 9 to 11 (plan/site.md; rulings 5, R13): the median page, the HTML of the chapter pages and of
        # the print views (recorded, each against a regression budget), the heaviest page's scripts without search,
        # and the sidebar's share of the page that carries the most of it.
        'median_page_gzip_bytes': int(statistics.median(entry[0] for entry in every_chapter)) if every_chapter else 0,
        'chapter_html_bytes': sum(entry[1] for entry in every_chapter),
        'print_html_bytes': sum(len(body) for url, body in pages.items() if url.startswith(printed)),
        'scripts_per_page_gzip_bytes': heaviest_scripts[0],
        'scripts_heaviest_page': heaviest_scripts[1],
        'sidebar_bytes': sidebar[0],
        'sidebar_share': round(sidebar[0] / sidebar[1], 4) if sidebar[1] else 0,
        'site_bytes': total,
        'site_files': files,
        'search_index_bytes': search,
        'problems': len(crawl.problems),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Stages the built site under its base path and crawls it.')
    parser.add_argument('--root', default=c_Root, help='the book\'s folder (default: this repository)')
    parser.add_argument('--dist', help='the built site (default: <root>/dist)')
    parser.add_argument('--stage', help='the staging folder (default: <root>/stage)')
    parser.add_argument('--base', default=os.environ.get('DOCS_BASE'), help='the base path (default: $DOCS_BASE or site.json\'s base)')
    parser.add_argument('--site', default=os.environ.get('DOCS_SITE'), help='the public origin canonical links use (default: $DOCS_SITE or site.json\'s origin)')
    parser.add_argument('--url', help='crawl this already served site instead of staging one (its path must be the base)')
    parser.add_argument('--serve-only', action='store_true', help='stage and serve until Ctrl+C, without crawling')
    parser.add_argument('--port', type=int, default=0, help='port of the staged server (default: a free one)')
    parser.add_argument('--workers', type=int, default=4, help='requests at a time (default 4)')
    parser.add_argument('--report', help='write the summary and problems as JSON to this file')
    parser.add_argument('--forbid-prefix', help='fail on any URL string of the build that starts with this prefix (gate (a) at another base)')
    parser.add_argument('--external-hosts', default=c_ExternalHosts, help='the hosts a link may name, one per line (default tools/external-hosts.txt)')
    parser.add_argument('--pin', help='engine.pin, for the commits of links into the engine (default <root>/engine.pin; without the file they are not checked)')
    parser.add_argument('--lychee', help='also run this lychee program offline over the staged folder (gate (a) 1); not with --url')
    options = parser.parse_args(argv)
    root = os.path.abspath(options.root)
    copyright = None
    try:
        if options.base is None or options.site is None:
            site_json = settings.read_site(root)
            options.base = site_json['base'] or '/' if options.base is None else options.base
            options.site = site_json['origin'] if options.site is None else options.site
        base = normalize_base(options.base)
        if os.path.isfile(os.path.join(root, settings.c_File)):
            copyright = settings.read_site(root)['copyright']
        external_hosts = read_external_hosts(options.external_hosts)
        pin_file = os.path.abspath(options.pin or os.path.join(root, 'engine.pin'))
        engine = None
        if os.path.isfile(pin_file):
            pin = repo.read_pin(pin_file)
            if not pin.get('repository'):
                raise ValueError('%s has no "repository" line' % pin_file)
            engine = {'repository': pin['repository'], 'commit': pin['commit']}
        elif options.pin:
            raise ValueError('%s does not exist' % pin_file)
        if options.lychee and options.url:
            raise ValueError('--lychee reads the staged folder; it does not run with --url')
    except (ValueError, OSError, settings.SettingsError) as error:
        parser.error(str(error))
    dist = os.path.abspath(options.dist or os.path.join(root, 'dist'))
    stage_root = os.path.abspath(options.stage or os.path.join(root, 'stage'))
    started = time.monotonic()
    server = None
    stage_folder = None
    try:
        if options.url:
            start = options.url if options.url.endswith('/') else options.url + '/'
            if urllib.parse.urlsplit(start).path.rstrip('/') != base:
                parser.error('the URL\'s path must be the base path %s/' % base)
            stage_folder = dist
        else:
            stage_folder = stage(dist, stage_root, base)
            server = start_server(stage_root, base, options.port)
            start = 'http://127.0.0.1:%d%s/' % (server.server_address[1], base)
            if options.serve_only:
                print('serving %s at %s (Ctrl+C stops)' % (stage_root, start))
                try:
                    while True:
                        time.sleep(3600)
                except KeyboardInterrupt:
                    return 0
        crawl = Crawl(start, base, options.site, options.workers)
        crawl.external_hosts = external_hosts
        crawl.engine = engine
        notes = []
        if engine is None:
            notes.append('links into the engine were not checked: %s does not exist' % pin_file)
        site_root = '{0.scheme}://{0.netloc}/'.format(urllib.parse.urlsplit(start))
        extra = check_root_and_missing(crawl, start, site_root, own_server=not options.url)
        # The fallback pages of moved pages: no page links to them, so the crawl starts at them too.
        crawl.moved = {site_root.rstrip('/') + old: site_root.rstrip('/') + new for old, new in deploy.moved_pages(stage_folder, base)}
        crawl.run(extra + sorted(crawl.moved) + [start + 'sitemap-index.xml', start + 'pagefind/pagefind-entry.json', start + 'pagefind/pagefind.js'])
        crawl.check_fragments()
        crawl.check_indexing()
        check_folders(crawl, start, stage_folder)
        check_unreferenced(crawl, stage_folder)
        check_no_robots(crawl, stage_folder)
        check_case(crawl, stage_folder)
        if not check_footer(crawl, stage_folder, copyright):
            notes.append('the footer line was not checked: the build holds no license.txt yet (LICENSE and the footer come with plan/site.md\'s change 15)')
        if options.lychee:
            for message in lychee_problems(options.lychee, stage_root):
                crawl.problem(message)
        if options.forbid_prefix:
            for relative, found in forbidden_prefix_uses(stage_folder, options.forbid_prefix.rstrip('/')):
                crawl.problem('%s names %s: a URL of this build that starts with %s' % (relative, found, options.forbid_prefix))
        expected = page_urls_of(stage_folder, start)
        for url, relative in sorted(expected.items()):
            if url not in crawl.results:
                crawl.problem('%s is never reached from %s (an orphan page)' % (relative, start))
        summary = summarize(crawl, stage_folder, started)
    except (ValueError, OSError) as error:
        print('crawl: %s' % error, file=sys.stderr)
        return 2
    finally:
        if server:
            server.shutdown()
            server.server_close()
    for message in sorted(set(crawl.problems)):
        print(message)
    for note in notes:
        print('crawl: note: %s' % note)
    summary['problems'] = len(set(crawl.problems))
    print('crawl: %(requests)d requests, %(pages)d pages, %(external_links)d external links, %(problems)d problems, %(seconds).1f s' % summary)
    for entry in summary['largest_pages'][:3]:
        print('  largest page: %s %d bytes (%d gzip)' % (entry['url'], entry['bytes'], entry['gzip_bytes']))
    for entry in summary['largest_print_pages'][:1]:
        print('  largest print view: %s %d bytes (%d gzip)' % (entry['url'], entry['bytes'], entry['gzip_bytes']))
    print('  site: %d files, %.1f MB; search index %.1f MB' % (summary['site_files'], summary['site_bytes'] / 1e6, summary['search_index_bytes'] / 1e6))
    print('  HTML: chapter pages %.1f MB, print views %.1f MB; median page %.1f KB gzip; scripts of the heaviest page %.1f KB gzip; sidebar %.1f KB (%.0f %% of its page)' % (
        summary['chapter_html_bytes'] / 1e6, summary['print_html_bytes'] / 1e6, summary['median_page_gzip_bytes'] / 1024,
        summary['scripts_per_page_gzip_bytes'] / 1024, summary['sidebar_bytes'] / 1024, summary['sidebar_share'] * 100))
    if options.report:
        with open(options.report, 'w', encoding='utf-8') as file:
            json.dump({'summary': summary, 'problems': sorted(set(crawl.problems))}, file, indent=1)
    return 1 if crawl.problems else 0


if __name__ == '__main__':
    sys.exit(main())
