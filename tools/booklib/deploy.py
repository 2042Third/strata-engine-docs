"""The deployment's shared pieces (plan/site.md, "Deployment"): the files of deploy/ written for another base, the
release's top folder, the moved pages of a built site, and the Content Security Policy and the server rules the
release step generates from the built HTML. tools/release.py, tools/servertest.py, tools/crawl.py and
tools/deployfiles.py use them.

The committed files of deploy/ are written for c_CommittedPrefix, which is site.json's base (a test fails when the
two differ). For another base every "/strata-engine-docs" that is the prefix becomes that base; file names such as
snippets/strata-engine-docs.conf (the prefix followed by "-", "." or a letter) stay. For the root of a host (the base
"") the blocks between the markers "(redirect: begin)" and "(redirect: end)" (the redirect of the prefix without its
slash, which would become a redirect of "" or "/") and between "(outside: begin)" and "(outside: end)" (the answer for
everything outside the prefix, which would hide the book itself) are dropped first, from the line holding the begin
marker to the line holding the end marker.
"""

import base64
import hashlib
import html.parser
import os
import re

c_CommittedPrefix = '/strata-engine-docs'
c_Blocks = ('redirect', 'outside')
# The files the release step writes into the deploy folder; deploy/ itself never holds them.
c_GeneratedFiles = ('nginx-csp.conf', 'nginx-redirects.conf')
# The nginx files a host or the container includes, and which tools/deployfiles.py writes for another base.
c_ServerFiles = ('nginx-http.conf', 'nginx.conf', 'nginx-container.conf', 'nginx-proxy.conf')
c_PrefixPattern = re.compile(re.escape(c_CommittedPrefix) + r'(?![-.\w])')
# The release's top folder where deploy/Dockerfile names it: "strata-engine-docs/" not preceded by a path or a name.
c_TopFolderPattern = re.compile(r'(?<![/\w.-])' + re.escape(c_CommittedPrefix.lstrip('/')) + r'/')
# The meta element of the fallback page of a moved page (src/lib/redirects.mjs): its content is the new page's path.
c_MovedMeta = 'strata-book-moved'
# The policy of plan/site.md, "What a release holds"; {scripts} becomes the hashes of the inline scripts.
c_PolicyTemplate = ("default-src 'self'; script-src 'self' 'wasm-unsafe-eval'{scripts}; style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data:; font-src 'self'; connect-src 'self'; worker-src 'self' blob:; object-src 'none'; "
                    "base-uri 'self'; form-action 'self'; frame-ancestors 'self'")
# Script types a browser runs, or checks against script-src (import maps and speculation rules): HTML's JavaScript
# MIME types, "module" and an absent or empty type. Data blocks (application/json, application/ld+json) are not run.
c_ScriptTypes = {'', 'module', 'importmap', 'speculationrules', 'application/ecmascript', 'application/javascript',
                 'application/x-ecmascript', 'application/x-javascript', 'text/ecmascript', 'text/javascript',
                 'text/javascript1.0', 'text/javascript1.1', 'text/javascript1.2', 'text/javascript1.3',
                 'text/javascript1.4', 'text/javascript1.5', 'text/jscript', 'text/livescript', 'text/x-ecmascript',
                 'text/x-javascript'}


def check_base(base):
    if base != '' and not re.match(r'^(/[A-Za-z0-9._~-]+)+$', base):
        raise ValueError('the base must be "" (the root) or a path such as /docs/strata: %r' % base)


def remove_block(text, name):
    """The text without the lines from "(<name>: begin)" to "(<name>: end)"; raises ValueError on unpaired markers."""
    result = []
    inside = False
    for line in text.split('\n'):
        if '(%s: begin)' % name in line:
            if inside:
                raise ValueError('"(%s: begin)" twice without "(%s: end)" between them' % (name, name))
            inside = True
            continue
        if '(%s: end)' % name in line:
            if not inside:
                raise ValueError('"(%s: end)" without its "(%s: begin)"' % (name, name))
            inside = False
            continue
        if not inside:
            result.append(line)
    if inside:
        raise ValueError('"(%s: begin)" without its "(%s: end)"' % (name, name))
    return '\n'.join(result)


def top_folder(base):
    """The release's top folder for a base: the base's path ("strata-engine-docs", "x/y"), or "site" for the root of
    a host, whose files the host's root serves."""
    check_base(base)
    return base.lstrip('/') or 'site'


def for_base(text, base, name=''):
    """A deploy file's text for the base path `base` ("" for the root of the host, else "/a/b" without a trailing
    slash). `name` is the file's name: deploy/Dockerfile also names the release's top folder."""
    check_base(base)
    if base == c_CommittedPrefix:
        return text
    if base == '':
        for block in c_Blocks:
            text = remove_block(text, block)
    if name == 'Dockerfile':
        text = c_TopFolderPattern.sub(top_folder(base) + '/', text)
    return c_PrefixPattern.sub(base, text)


def deploy_files(folder):
    """The committed files of deploy/, sorted: every file but the generated ones, which the release step writes."""
    names = sorted(name for name in os.listdir(folder) if os.path.isfile(os.path.join(folder, name)))
    generated = [name for name in names if name in c_GeneratedFiles]
    if generated:
        raise ValueError('deploy/ holds %s, which the release step writes from the built site: remove it' % ', '.join(generated))
    return names


class _HeadParser(html.parser.HTMLParser):
    """The inline scripts of a page, its moved-page meta element and its inline event handlers."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scripts = []
        self.moved = None
        self.handlers = []
        self._script = None

    def handle_starttag(self, tag, attributes):
        values = {}
        for name, value in attributes:
            values.setdefault(name, value or '')
            if name.startswith('on') and len(name) > 2:
                self.handlers.append('%s %s' % (tag, name))
            if name in ('href', 'src', 'action', 'formaction') and (value or '').strip().lower().startswith('javascript:'):
                self.handlers.append('%s %s="javascript:…"' % (tag, name))
        if tag == 'meta' and values.get('name') == c_MovedMeta:
            self.moved = values.get('content', '')
        if tag == 'script' and 'src' not in values:
            kind = values.get('type', '').split(';')[0].strip().lower()
            self._script = [] if kind in c_ScriptTypes else None
        elif tag == 'script':
            self._script = None

    def handle_endtag(self, tag):
        if tag == 'script':
            if self._script is not None:
                self.scripts.append(''.join(self._script))
            self._script = None

    def handle_data(self, data):
        if self._script is not None:
            self._script.append(data)


def read_page(path):
    with open(path, encoding='utf-8') as file:
        parser = _HeadParser()
        parser.feed(file.read())
        parser.close()
    return parser


def html_files(site):
    """Every HTML file of a built site, relative and with "/", sorted."""
    found = []
    for folder, directories, names in os.walk(site):
        directories.sort()
        for name in sorted(names):
            if name.endswith('.html'):
                found.append(os.path.relpath(os.path.join(folder, name), site).replace(os.sep, '/'))
    return sorted(found)


def script_hash(text):
    """The CSP source of an inline script: 'sha256-<base64 of the SHA-256 of its UTF-8 text>'."""
    return "'sha256-%s'" % base64.b64encode(hashlib.sha256(text.encode('utf-8')).digest()).decode('ascii')


def content_security_policy(site):
    """(policy, problems): the policy with a hash of every inline script a page of the site runs (Starlight's theme
    and sidebar scripts, Astro's inlined modules), and what the policy would block that a page needs (an inline event
    handler, a javascript: URL)."""
    hashes = set()
    problems = []
    for relative in html_files(site):
        page = read_page(os.path.join(site, *relative.split('/')))
        hashes.update(script_hash(script) for script in page.scripts)
        for handler in page.handlers:
            problems.append('%s: %s runs inline code, which the policy blocks: move it into a script' % (relative, handler))
    scripts = ''.join(' ' + source for source in sorted(hashes))
    return c_PolicyTemplate.format(scripts=scripts), problems


def csp_conf(policy):
    """nginx-csp.conf: the policy as one add_header line, with "always" (included in the book's location)."""
    if '"' in policy or '\n' in policy:
        raise ValueError('the policy holds a double quote or a line break: %r' % policy)
    return ('# The Strata Engine Book: its Content Security Policy, written by tools/release.py from the built HTML (the\n'
            '# hashes of its inline scripts). Included in the book\'s location (deploy/nginx.conf).\n'
            'add_header Content-Security-Policy "%s" always;\n' % policy)


def moved_pages(site, base):
    """[(old path, new path)] of the fallback pages of a built site, sorted: "<base>/core/old/" and the path its
    refresh names. A fallback page whose target leaves the base is refused."""
    moves = []
    for relative in html_files(site):
        if not relative.endswith('/index.html'):
            continue
        page = read_page(os.path.join(site, *relative.split('/')))
        if page.moved is None:
            continue
        target = page.moved
        if not re.match(r'^%s/([a-z0-9-]+/)*$' % re.escape(base), target):
            raise ValueError('%s: its moved page names %r, which is not a page path under %s/' % (relative, target, base))
        moves.append(('%s/%s' % (base, relative[:-len('index.html')]), target))
    return moves


def redirects_conf(moves):
    """nginx-redirects.conf: per moved page an exact location for its old address, with and without its slash, that
    answers 301 with the new page's path. It stands inside the book's location, so the locations need no headers of
    their own and Location is a path (absolute_redirect off)."""
    lines = ['# The Strata Engine Book: its moved pages (src/redirects.json), written by tools/release.py from the built site.',
             '# Included inside the book\'s location (deploy/nginx.conf).']
    if not moves:
        lines.append('# No page has moved.')
    for old, new in moves:
        for path in (old, old.rstrip('/')):
            if not re.match(r'^/[a-z0-9/-]+$', path) or not re.match(r'^/[a-z0-9/-]*$', new):
                raise ValueError('a moved page with an address nginx would read otherwise: %r to %r' % (path, new))
            lines.append('location = %s { return 301 %s; }' % (path, new))
    return '\n'.join(lines) + '\n'
