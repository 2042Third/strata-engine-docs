"""Test helpers: a small book and a small engine repository in temporary folders.

The small book's plan is tools/tests/fixtures/outline/ (an outline of nine parts with the real book's shape) and
c_TestBook names its decisions, as booklib.outline.c_Book names the real book's. page() writes a page whose front
matter is its row's and whose body has the shape of its kind (plan/style.md §6 and §7), so that a test changes one
thing and sees one rule fail.
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from booklib import outline as outline_rules  # noqa: E402

c_Fixtures = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
c_OutlineFixture = os.path.join(c_Fixtures, 'outline')

c_TestBook = outline_rules.Book(
    part_order=['start', 'make', 'basics', 'core', 'world', 'gpu', 'draw', 'reference', 'appendix'],
    trackless_parts=['reference', 'appendix'],
    first_script='make/first-script',
    programming_primers=['basics/programming-1'],
    g_side_steps=['basics/tools', 'basics/math-vectors'],
    b_before_first_script=['basics/computer', 'basics/tools'],
    not_on_b=['start/coming-from'],
    gb_kinds=['C', 'H', 'P', 'T'],
    w8_pages=['draw/culling'],
    w8r_pages=['gpu/frame'],
    waves=[
        ('1', 'start, basics, core', ['start', 'basics', 'core']),
        ('2', 'make block A, world', ['make:A', 'world']),
        ('3', 'make block B, gpu, draw', ['make:B', 'gpu', 'draw']),
        ('4', 'make block C', ['make:C']),
        ('B', 'phase B: the W8 pages, reference, appendix', ['W8', 'reference', 'appendix']),
    ],
    documents=False,
)

c_SidebarKeys = {'G': 'game', 'B': 'beginner', 'E': 'engine'}

# A bottom strip for tests of other tools, which do not read it.
c_BottomStrip = """
## Summary

- One line.

## Check yourself

1. One?

   :::answer{tests="one"}
   Yes.
   :::

## Further reading

- A book.
"""


def remove_tree(path):
    """Removes a folder, also the read-only files git writes for its objects (Windows refuses to delete those)."""
    def clear_and_retry(function, target, _):
        os.chmod(target, stat.S_IWRITE)
        function(target)
    if os.path.exists(path):
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, onexc=clear_and_retry)
        else:
            shutil.rmtree(path, onerror=clear_and_retry)


def frontmatter(**overrides):
    """Front matter in plan/style.md §6.1's form; a value of None leaves the key out. Values are YAML as written."""
    data = {
        'id': 'core/time', 'title': '"A page"', 'description': '"A page of the test book."', 'kind': 'concept', 'size': 'M',
        'tracks': '[E]', 'needs': '[]', 'time': '30',
        'learn': '\n  - id: one\n    text: explain one thing\n  - id: two\n    text: compute another thing',
        'since': '0.3.0', 'status': 'draft',
    }
    data.update(overrides)
    return '---\n' + '\n'.join('%s: %s' % (key, value) for key, value in data.items() if value is not None) + '\n---\n'


def read_outline():
    return outline_rules.read(c_OutlineFixture, c_TestBook)


def row_frontmatter(row, **overrides):
    """The front matter of the page of an outline row, as its writer would write it."""
    kind = row.kind_word
    data = {
        'id': row.id,
        'title': json.dumps(row.title),
        'description': json.dumps('What %s teaches.' % row.id),
        'kind': kind,
        'size': row.size,
        'tracks': '[%s]' % ', '.join(row.tracks),
        'needs': '[%s]' % ', '.join(row.needs_text),
        'time': None if kind == 'reference' else '30',
        'learn': None if kind == 'reference' else '\n  - id: one\n    text: explain the first idea\n  - id: two\n    text: compute the second',
        'since': '0.3.0' if kind in ('concept', 'internals', 'tutorial', 'how-to') and (row.part.number == 1 or 3 <= row.part.number <= 21) else None,
        'status': 'draft',
    }
    data.update(overrides)
    return frontmatter(**data)


def answer(tests='one two'):
    return '   :::answer{tests="%s"}\n   Because it is.\n   :::\n' % tests


def strip(kind, summary=2, questions=3, exercises=1, tests=('one two', 'one', 'two'), uses=None):
    """The bottom strip of a page of a kind (style.md §6.3)."""
    if kind == 'reference':
        return '\n## Where it lives in Strata\n\n- `Strata/src/Strata/Core/Time.h`\n'
    text = '\n## Summary\n\n' + ''.join('- Item %d answers its objective.\n' % (number + 1) for number in range(summary))
    text += '\n## Check yourself\n\n'
    for number in range(questions):
        text += '%d. Question %d?\n\n%s\n' % (number + 1, number + 1, answer(tests[number % len(tests)]))
    if kind == 'primer':
        text += '## Practice\n\n'
        for number in range(max(exercises, 3)):
            text += '%d. **Basic.** Practice %d.\n\n%s\n' % (number + 1, number + 1, answer('one'))
        text += '## Where the book uses it\n\n'
        for target in uses or []:
            text += '- [%s](%s) uses it.\n' % (target, target)
        text += '\n'
    else:
        text += '## Exercises\n\n'
        for number in range(exercises):
            text += '%d. **Basic.** Exercise %d.\n\n%s\n' % (number + 1, number + 1, answer('two'))
        text += '## Where it lives in Strata\n\n- `Strata/src/Strata/Core/Time.h`\n\n'
    text += '## Further reading\n\n- A book, for beginners.\n'
    return text


def quote(line):
    return '```cpp src="Strata/src/Strata/Core/Time.h#L%d-L%d"\nint a;\nint b;\nint c;\nint d;\nint e;\n```\n\nIt counts.\n\n' % (line, line + 4)


def body(kind, **strip_options):
    """A body of the shape style.md §7 gives a kind, followed by its bottom strip."""
    if kind == 'primer':
        test_out = '::::test-out\n' + ''.join('%d. Question %d?\n\n   :::answer{tests="%s"}\n   Yes.\n   :::\n\n'
                                              % (number + 1, number + 1, 'one' if number % 2 else 'two') for number in range(5)) + '::::\n'
        text = test_out + '\n## Why you will need this\n\nIt is used later.\n\n## The idea\n\n:::example\nA worked example.\n:::\n\n## Common mistakes\n\n- One.\n'
    elif kind == 'concept':
        text = '\nA story.\n\n## The idea\n\n:::example\nA worked example.\n:::\n\n## Common mistakes\n\n- One.\n'
    elif kind == 'internals':
        text = ('\nThe job.\n\n## The problem and how engines solve it\n\nApproaches.\n\n## The real code\n\n' + quote(1) + quote(10) + quote(20)
                + ':::example\nA worked example.\n:::\n\n## Alternatives Strata did not choose\n\nA table.\n\n## How it is tested\n\nTests.\n\n'
                '## Changing it safely\n\nRules.\n')
    elif kind == 'tutorial':
        text = ('\n## What you will make\n\nA game.\n\n## What you need\n\nA template.\n\n## Make the ball roll\n\n1. Do it.\n\n'
                '::checkpoint{stage=1}\n\n::figure{id=ball-rolling}\n')
    elif kind == 'how-to':
        text = '\nThe goal.\n\n## Do the task\n\n1. Do it.\n\n## Result\n\nIt is done.\n\n## Variations\n\nOther ways.\n'
    else:
        text = '\nWhat the table is.\n'
    return text + strip(kind, **strip_options)


def part_page(slug, last, outline=None, **overrides):
    outline = outline or read_outline()
    part = next(part for part in outline.parts if part.slug == slug)
    letters = [letter for letter in outline_rules.c_TrackLetters if any(letter in row.tracks for row in part.pages)]
    data = {'id': '%s/%s' % (slug, last), 'title': json.dumps('%s %s' % (part.title, last)), 'description': '"The part\'s %s."' % last,
            'kind': None, 'size': None, 'needs': None, 'time': None, 'learn': None, 'since': None,
            'tracks': '[%s]' % ', '.join(letters), 'status': 'draft', 'generated': last}
    data.update(overrides)
    return frontmatter(**data) + '\nThe part editor\'s paragraph.\n'


def sidebar_data(outline, written):
    """src/sidebar.json in the site's form (.tools/handover/outline-format.md §3) for the written pages."""
    parts = []
    for part in outline.parts:
        rows = [row.id for row in part.pages if row.id in written]
        pages = ([part.slug + '/index'] if part.slug + '/index' in written else []) + rows \
            + ([part.slug + '/review'] if part.slug + '/review' in written else [])
        parts.append({'slug': part.slug, 'label': part.title, 'pages': pages})
    tracks = {}
    for letter, key in c_SidebarKeys.items():
        entries = outline.tracks[letter]
        tracks[key] = {
            'label': key, 'description': 'the %s track' % key,
            'sequence': outline_rules.track_order(outline, letter),
            'sideSteps': [{'id': page_id, 'before': next((entry[0] for entry in entries[number + 1:] if not entry[1]), None)}
                          for number, (page_id, side_step, _) in enumerate(entries) if side_step],
        }
    return {'parts': parts, 'tracks': tracks}


class TempBook:
    """A book folder: write(relative path, text), page(id, text), sidebar(), cleanup(). With plan=True it holds the
    small outline in plan/, src/generated/outline.json, and a sidebar that follows the written pages."""

    def __init__(self, pin_commit='0' * 40, plan=False):
        self.root = tempfile.mkdtemp(prefix='book-test-')
        self.write('engine.pin', 'commit %s\nrelease 0.8.0\nprerelease yes\nrepository https://github.com/2042Third/GameEngine\n' % pin_commit)
        self.write('src/content/glossary.json', json.dumps({'terms': []}))
        self.pages = []
        self.plan = plan
        self.outline = None
        if plan:
            shutil.copytree(c_OutlineFixture, os.path.join(self.root, 'plan'))
            self.outline = outline_rules.read(os.path.join(self.root, 'plan'), c_TestBook)
            import pages  # the tool under test writes its own data file
            self.write('src/generated/outline.json', pages.outline_text(self.outline))
        self.sidebar()

    def path(self, relative):
        return os.path.join(self.root, *relative.split('/'))

    def write(self, relative, text, binary=False):
        path = self.path(relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb' if binary else 'w', **({} if binary else {'encoding': 'utf-8', 'newline': '\n'})) as file:
            file.write(text)
        return path

    def read(self, relative):
        with open(self.path(relative), encoding='utf-8') as file:
            return file.read()

    def remove(self, relative):
        os.remove(self.path(relative))

    def page(self, page_id, text, listed=True):
        self.write('src/content/docs/%s.md' % page_id, text)
        if listed and page_id not in ('index', '404') and page_id not in self.pages:
            self.pages.append(page_id)
        self.sidebar()

    def row_page(self, page_id, frontmatter_overrides=None, **body_options):
        """Writes the page of an outline row with its row's front matter and a body of its kind's shape."""
        row = self.outline.by_id[page_id]
        self.page(page_id, row_frontmatter(row, **(frontmatter_overrides or {})) + body(row.kind_word, **body_options))

    def sidebar(self):
        if self.plan:
            data = sidebar_data(self.outline, set(self.pages))
        else:
            data = {'parts': [], 'tracks': {}}
        self.write('src/sidebar.json', json.dumps(data, indent='\t'))

    def cleanup(self):
        remove_tree(self.root)


class TempEngine:
    """A git repository standing in for the engine: commit(files) returns the new commit's id."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix='engine-test-')
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.com')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'commit.gpgsign', 'false')

    def git(self, *arguments):
        result = subprocess.run(['git', '-C', self.root] + list(arguments), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode('utf-8', 'replace'))
        return result.stdout.decode('utf-8').strip()

    def add_submodule(self, path, files, url):
        """A vendored library as git submodule update leaves it: a repository of its own at path inside the clone, named
        in .gitmodules and initialized. Returns its commit; the next commit() records it as the gitlink."""
        folder = os.path.join(self.root, *path.split('/'))
        os.makedirs(folder, exist_ok=True)
        for arguments in (['init', '-q'], ['config', 'user.email', 'test@example.com'], ['config', 'user.name', 'Test'],
                          ['config', 'commit.gpgsign', 'false']):
            subprocess.run(['git', '-C', folder] + arguments, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for relative, text in files.items():
            target = os.path.join(folder, *relative.split('/'))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, 'w', encoding='utf-8', newline='\n') as file:
                file.write(text)
        subprocess.run(['git', '-C', folder, 'add', '-A'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['git', '-C', folder, 'commit', '-q', '-m', 'library'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        modules = os.path.join(self.root, '.gitmodules')
        with open(modules, 'a', encoding='utf-8', newline='\n') as file:
            file.write('[submodule "%s"]\n\tpath = %s\n\turl = %s\n' % (path, path, url))
        commit = subprocess.run(['git', '-C', folder, 'rev-parse', 'HEAD'], check=True, stdout=subprocess.PIPE).stdout.decode().strip()
        self.git('config', 'submodule.%s.url' % path, url)
        self.git('config', 'submodule.%s.active' % path, 'true')
        return commit

    def commit(self, files, message='change'):
        for relative, text in files.items():
            path = os.path.join(self.root, *relative.split('/'))
            if text is None:
                os.remove(path)
                continue
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8', newline='\n') as file:
                file.write(text)
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def cleanup(self):
        remove_tree(self.root)
