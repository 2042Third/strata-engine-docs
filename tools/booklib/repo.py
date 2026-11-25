"""The book repository's layout and the engine at the pinned commit.

Every tool takes --root (the book's folder; the repository by default, a copy for the scale test) and, when it reads
the engine, --engine (the pin clone). Files are read at the full pin through one "git cat-file --batch" process
(plan/pipelines.md §1.2), so for reading the clone's working tree does not matter; pictures, tutorials and the
reference dump need it at the pin and clean (§1.3), which the tools that start engine programs check.
"""

import os
import re
import subprocess
import sys

c_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c_DefaultEngine = os.environ.get('STRATA_ENGINE')


class Layout:
    def __init__(self, root=None):
        self.root = os.path.abspath(root or c_Root)
        self.docs = os.path.join(self.root, 'src', 'content', 'docs')
        self.figures = os.path.join(self.root, 'src', 'content', 'figures')
        self.pictures = os.path.join(self.root, 'src', 'assets', 'figures')
        self.glossary = os.path.join(self.root, 'src', 'content', 'glossary.json')
        self.sidebar = os.path.join(self.root, 'src', 'sidebar.json')
        self.sketches = os.path.join(self.root, 'sketches')
        self.tutorials = os.path.join(self.root, 'tutorials')
        self.pin_file = os.path.join(self.root, 'engine.pin')

    def pages(self):
        """(page id, absolute path) of every page, sorted; names starting with _ or . are not pages (as Starlight)."""
        result = []
        for folder, directories, files in os.walk(self.docs):
            directories[:] = sorted(d for d in directories if not d.startswith(('_', '.')))
            for name in sorted(files):
                if name.endswith('.md') and not name.startswith(('_', '.')):
                    path = os.path.join(folder, name)
                    result.append((page_id(os.path.relpath(path, self.docs)), path))
        return sorted(result)

    def relative(self, path):
        return os.path.relpath(path, self.root).replace(os.sep, '/')


def page_id(relative):
    posix = relative.replace(os.sep, '/')
    stem = posix[:-3] if posix.endswith('.md') else posix
    if stem == 'index':
        return 'index'
    return stem[:-6] if stem.endswith('/index') else stem


def named_page(name):
    """The page id the tools give a page that a person names, as page_id gives it for the page's file: a part's index
    page, src/content/docs/<part>/index.md, whose front matter carries the id <part>/index, is the page <part> (its URL)
    under either name (plan/site.md, "Part pages"). A trailing .md is dropped."""
    text = name.strip().replace('\\', '/').strip('/')
    return page_id(text if text.endswith('.md') else text + '.md')


def read_pin(path):
    """engine.pin as a dict: commit, release, prerelease (bool), repository."""
    values = {}
    with open(path, encoding='utf-8') as file:
        for raw in file:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            key, _, value = line.partition(' ')
            values[key] = value.strip()
    if not re.match(r'^[0-9a-f]{40}$', values.get('commit', '')):
        raise ValueError('%s: "commit" must be a full 40-digit commit id' % path)
    values['prerelease'] = values.get('prerelease') == 'yes'
    return values


c_PinHeader = """# The engine commit this book is checked against (plan/pipelines.md §1.1). The tools read the engine's files at this
# commit through git, so for quotes and parsing the clone's working tree does not matter; the working tree must be at
# the pin and clean for pictures, tutorials and the reference dump (plan/pipelines.md §1).
# release: the engine release the book describes; prerelease: yes while the commit is not that release's tag.
# Only tools/pin.py move writes this file: python -I tools/pin.py move --engine <clone> <commit> [--release <x.y.z>]
# [--prerelease yes|no].
"""


def pin_text(values):
    """engine.pin's text: the header, then commit, release, prerelease and repository in this order."""
    lines = ['commit %s' % values['commit'], 'release %s' % values['release'], 'prerelease %s' % ('yes' if values['prerelease'] else 'no'),
             'repository %s' % values['repository']]
    return c_PinHeader + '\n'.join(lines) + '\n'


def write_pin(path, commit, release=None, prerelease=None):
    """Writes engine.pin with a new commit (and release, prerelease), keeping the repository; the header is always the
    current one (plan/pipelines.md §1.1)."""
    values = read_pin(path)
    values['commit'] = commit
    if release is not None:
        values['release'] = release
    if prerelease is not None:
        values['prerelease'] = prerelease
    for key in ('release', 'repository'):
        if not values.get(key):
            raise ValueError('%s: "%s" is missing' % (path, key))
    with open(path, 'w', encoding='utf-8', newline='\n') as file:
        file.write(pin_text(values))


class EngineError(Exception):
    pass


class Engine:
    """Files of the engine at commits, read through git (cached)."""

    def __init__(self, path):
        if not path:
            raise EngineError('name a clone of the engine with --engine <folder> (or set STRATA_ENGINE)')
        self.path = os.path.abspath(path)
        self.cache = {}
        self.batch = None
        self.submodules = {}
        if not os.path.exists(self.path):
            raise EngineError('no engine clone at %s (pass --engine or set STRATA_ENGINE)' % self.path)

    def git(self, *arguments, check=True):
        result = subprocess.run(['git', '-C', self.path] + list(arguments), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check and result.returncode != 0:
            raise EngineError('git %s: %s' % (' '.join(arguments), result.stderr.decode('utf-8', 'replace').strip()))
        return result

    def resolve(self, commit):
        """The full id of the commit a name means (a commit, a branch, a tag)."""
        # "<name>~0" peels tags to their commit and fails for anything that is not a commit; "<name>^{commit}" would be
        # the usual spelling, but MSYS2's git expands braces in the arguments native programs give it.
        result = self.git('rev-parse', '--verify', '--quiet', commit + '~0', check=False)
        if result.returncode != 0:
            raise EngineError('the engine clone at %s does not have the commit %s (fetch it, or clone with that commit)' % (self.path, commit))
        return result.stdout.decode('ascii').strip()

    def object(self, commit, path):
        """(type, bytes) of the object at commit:path ("blob", "tree"), or None when there is none. One "git cat-file
        --batch" process answers every request: starting git once per file is slow on Windows (1,500 quotes took 73 s)."""
        if self.batch is None:
            self.batch = subprocess.Popen(['git', '-C', self.path, 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        name = '%s:%s' % (commit, path)
        if '\n' in name:
            return None
        self.batch.stdin.write(name.encode('utf-8') + b'\n')
        self.batch.stdin.flush()
        header = self.batch.stdout.readline().decode('utf-8', 'replace').split()
        if len(header) != 3:
            if not header:
                raise EngineError('git cat-file --batch ended unexpectedly in %s' % self.path)
            return None  # "<name> missing" (or "ambiguous")
        size = int(header[2])
        data = self.batch.stdout.read(size)
        self.batch.stdout.read(1)  # the newline after every object
        return header[1], data

    def read(self, commit, path):
        """The file's lines at the commit (without line endings), or None when the file does not exist there."""
        key = (commit, path)
        if key not in self.cache:
            found = self.object(commit, path)
            if found is None or found[0] != 'blob':
                self.cache[key] = None
            else:
                text = found[1].decode('utf-8', 'replace').replace('\r\n', '\n')
                if text.endswith('\n'):
                    text = text[:-1]
                self.cache[key] = text.split('\n')
        return self.cache[key]

    def exists(self, commit, path):
        """True when the path is a file or a folder at the commit."""
        return self.object(commit, path.rstrip('/')) is not None

    def tree(self, commit, path=''):
        """{name: (mode, object id)} of the folder at commit:path (the root for ''), or None when it is no folder there.
        A submodule is an entry of mode 160000 whose id is the commit the folder records for it."""
        key = ('tree', commit, path)
        if key not in self.cache:
            found = self.object(commit, path.strip('/'))
            entries = None
            if found is not None and found[0] == 'tree':
                entries = {}
                data = found[1]
                offset = 0
                while offset < len(data):
                    space = data.index(b' ', offset)
                    end = data.index(b'\0', space)
                    mode = data[offset:space].decode('ascii')
                    name = data[space + 1:end].decode('utf-8', 'replace')
                    entries[name] = (mode, data[end + 1:end + 21].hex())
                    offset = end + 21
            self.cache[key] = entries
        return self.cache[key]

    def gitlink(self, commit, path):
        """The commit a submodule folder records at the commit (mode 160000), or None when the path is no submodule."""
        folder, _, name = path.strip('/').rpartition('/')
        entries = self.tree(commit, folder)
        entry = entries.get(name) if entries else None
        return entry[1] if entry and entry[0] == '160000' else None

    def submodule_of(self, commit, path):
        """(submodule folder, path inside it) when the path runs through a submodule at the commit, else None."""
        parts = path.strip('/').split('/')
        for count in range(1, len(parts)):
            folder = '/'.join(parts[:count])
            if self.gitlink(commit, folder):
                return folder, '/'.join(parts[count:])
            entries = self.tree(commit, folder)
            if entries is None:
                return None
        return None

    def submodule(self, folder):
        """The reader of a submodule's repository in the clone (its checkout at <clone>/<folder>)."""
        if folder not in self.submodules:
            self.submodules[folder] = Engine(os.path.join(self.path, *folder.split('/')))
        return self.submodules[folder]

    def submodule_urls(self, commit):
        """{submodule path: url} from .gitmodules at the commit."""
        lines = self.read(commit, '.gitmodules') or []
        urls = {}
        current = {}
        for line in lines + ['[submodule end]']:
            stripped = line.strip()
            if stripped.startswith('['):
                if 'path' in current and 'url' in current:
                    urls[current['path']] = current['url']
                current = {}
            elif '=' in stripped:
                key, _, value = stripped.partition('=')
                current[key.strip()] = value.strip()
        return urls

    def close(self):
        if self.batch is not None:
            self.batch.stdin.close()
            self.batch.wait()
            self.batch.stdout.close()
            self.batch = None
        for submodule in self.submodules.values():
            submodule.close()


def utf8_output():
    """Writes the tool's messages in UTF-8, as the book's files are, whatever the console's code page (Windows starts
    Python with cp1252, which cannot write a page's "…" or a section sign)."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure') and (stream.encoding or '').lower().replace('-', '') != 'utf8':
            stream.reconfigure(encoding='utf-8', errors='replace')


def write_text(path, text):
    with open(path, 'w', encoding='utf-8', newline='\n') as file:
        file.write(text)


def read_text(path):
    """A file's text with LF line ends and without a byte-order mark (Notepad writes one; Astro reads past it)."""
    with open(path, encoding='utf-8', newline='') as file:
        text = file.read().replace('\r\n', '\n')
    return text[1:] if text.startswith('\ufeff') else text
