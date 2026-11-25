"""The book's outline: plan/outline-1.md to outline-4.md and plan/tracks.md, read into rows and checked against their
rules, the rulings and the counts that plan/book.md, plan/process.md and plan/README.md state.

This module is the one implementation of the outline's rules (plan/site.md, "Outline rules on the pages"):
plan/check_outline.py calls it to check the plan, and tools/pages.py runs it and its rules on the pages' front
matter. The rules are those of plan/outline-1.md ("How to read the tables" and "The check"), plan/tracks.md and the
rulings (rulings 1: R1, R2, R4, R6; rulings 2: the order of the parts; rulings 4: R7 to R11; rulings 5: R17).

The book's own decisions (its parts, the pages its track rules name, the W8 marks, the writing waves) are a Book;
c_Book is the real book's, and tests pass a smaller one. Problems are Problem objects: `text` is the problem (the
same words plan/check_outline.py printed before it called this module), `advice` says what to do, and `where` names
the file for problems whose text does not start with one.
"""

import hashlib
import os
import re

c_OutlineFiles = ('outline-1.md', 'outline-2.md', 'outline-3.md', 'outline-4.md')
c_TracksFile = 'tracks.md'
c_Documents = ('book.md', 'process.md', 'README.md')

c_Kinds = {'C': 'concept', 'I': 'internals', 'T': 'tutorial', 'H': 'how-to', 'R': 'reference', 'P': 'primer'}
c_KindLetters = {word: letter for letter, word in c_Kinds.items()}
c_Sizes = ('S', 'M', 'L', 'XL')
c_Words = {'S': 1500, 'M': 3000, 'L': 5000, 'XL': 8000}
# The range of prose words of each size (rulings 7, R28, rule S; rulings 8, R37: the tops and bottoms).
c_Ranges = {'S': (600, 2250), 'M': (2251, 4000), 'L': (4001, 6500), 'XL': (6501, 10000)}
c_TrackLetters = ('G', 'B', 'E')
c_Columns = ['id', 'Title', 'Kind', 'Size', 'Tracks', 'Needs', 'From']
# At most five page ids in a row's Needs, alternatives included (rulings 1, R1).
c_MaxNeedIds = 5
# Last segments a row may not use: the generated part pages <part>/index and <part>/review (rulings 1, R2).
c_ReservedLastSegments = ('index', 'review')
# First segments no page id may start with: the site's own folders and archived versions (site.md, "The base path",
# rule 8; downloads holds the files readers download, rulings-6 R26). A "v" followed by a digit is matched by
# c_ReservedFirstSegment.
c_ReservedFirstSegments = ('print', 'pagefind', 'downloads', '_astro', '_figures', '404')
c_ReservedFirstSegment = re.compile(r'^v[0-9]')
c_GeneratedPagesFrom = 8
# style.md §2.2, rule `banned-word`: words that tell a reader who is lost that the reader is the problem. No title
# holds one (rulings 5, R17); tools/lint.py flags them in prose.
c_BannedWords = ('simply', 'just', 'obviously', 'of course', 'clearly', 'basically', 'easy', 'easily', 'trivial',
                 'trivially', 'needless to say', 'as everyone knows', 'it follows', 'it is easy to see')

c_PartHeading = re.compile(r'^## Part (\d+) — (.+) \(`([a-z0-9-]+)`\)\s*$')
c_BlockLine = re.compile(r'^\*\*Block ([A-Z]) — .+\*\*\s*$')
c_TracksLine = re.compile(r'^Tracks:\s*(.*)$')
# A Tracks line or cell starts with its letters ("G, B" or "-"); prose may follow after ".", ";", " (" or " —".
c_TrackList = re.compile(r'^(-|[GBE](?:, [GBE])*)(.*)$')
c_PartNeedsLine = re.compile(r'^Needs of the part:\s*(.*)$')
c_IdPattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)+$')
# A page id of the site (site.md, rule O1): one segment or more.
c_PageIdPattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*$')
c_CodeId = re.compile(r'^`([^`]+)`$')
c_MarkAtEnd = re.compile(r' · (W8r?)(?: \(([^()]+)\))?\s*$')
c_AnyMark = re.compile(r'\bW8\w*')
c_TrackHeading = re.compile(r'^## Track ([A-Z])\b')
c_OtherHeading = re.compile(r'^#{1,6} ')
c_TrackEntry = re.compile(r'^(\d+)\. `([^`]+)`( \(side step\))?(?: — .+)?\s*$')
c_NumberedLine = re.compile(r'^\d+\. ')
c_NumberWords = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
                 'ten': 10, 'eleven': 11, 'twelve': 12}


class Book:
    """The book's decisions that the rules check, as data. A test builds a smaller book with the same shape."""

    def __init__(self, part_order, trackless_parts, first_script, programming_primers, g_side_steps,
                 b_before_first_script, not_on_b, gb_kinds, w8_pages, w8r_pages, waves, documents=True):
        # The parts in the book's order (rulings 2, "Order of the parts").
        self.part_order = list(part_order)
        self.trackless_parts = set(trackless_parts)
        # The track sequences of rulings 1, R4, and the pages they name.
        self.first_script = first_script
        self.programming_primers = list(programming_primers)
        self.g_side_steps = list(g_side_steps)
        self.b_before_first_script = list(b_before_first_script)
        self.not_on_b = set(not_on_b)
        # A game maker never has to read internals (book.md, "Tracks", rule 2): the kinds a page of track G or B may have.
        self.gb_kinds = set(gb_kinds)
        # The marks of rulings 1, R6.
        self.w8_pages = set(w8_pages)
        self.w8r_pages = set(w8r_pages)
        # The writing waves: (name, description, selectors). A selector is a part slug, or "make:A", "make:B",
        # "make:C" for a block of part make; "W8" holds every page marked W8 and is tried first.
        self.waves = list(waves)
        # Whether the counts of book.md, process.md and README.md are checked (the real book's documents).
        self.documents = documents


# The writing waves: rulings 3 ("process.md", PR1), corrected where the check found a page that needs a page of a
# later wave (the ruling: fix the wave list, not the Needs). Corrections: `editor` moves from wave 3 to wave 5 (its
# pages need `draw`, `input`, `scripting` and `worlds`); `scripting` moves from wave 4 to wave 5
# (`scripting/script-system` needs `animation/time-events`). Phase B holds the W8 pages and, as process.md's phase B
# says, the reference pages and the appendices.
c_Waves = [
    ('1', 'start, basics, core, world', ['start', 'basics', 'core', 'world']),
    ('2', 'make block A, gpu', ['make:A', 'gpu']),
    ('3', 'assets, make block B without W8 pages', ['assets', 'make:B']),
    ('4', 'draw, light and image without W8 pages, physics, audio, input',
        ['draw', 'light', 'image', 'physics', 'audio', 'input']),
    ('5', 'indirect without W8 pages, animation, scripting, ui, worlds, editor, make block C',
        ['indirect', 'animation', 'scripting', 'ui', 'worlds', 'editor', 'make:C']),
    ('6', 'editor-ui, automation, engineering, capstone', ['editor-ui', 'automation', 'engineering', 'capstone']),
    ('B', 'phase B: the W8 pages, reference, appendix', ['W8', 'reference', 'appendix']),
]

c_Book = Book(
    part_order=['start', 'make', 'basics', 'core', 'world', 'gpu', 'assets', 'draw', 'light', 'image', 'indirect',
                'physics', 'animation', 'audio', 'input', 'scripting', 'ui', 'worlds', 'editor', 'editor-ui',
                'automation', 'engineering', 'capstone', 'reference', 'appendix'],
    trackless_parts=['reference', 'appendix'],
    first_script='make/first-script',
    programming_primers=['basics/programming-1', 'basics/programming-2', 'basics/programming-3', 'basics/debugging'],
    g_side_steps=['basics/tools', 'basics/math-vectors'],
    b_before_first_script=['basics/computer', 'basics/tools'],
    not_on_b=['start/coming-from'],
    gb_kinds=['C', 'H', 'P', 'T'],
    w8_pages=['light/local-shadows', 'light/area-lights', 'indirect/gi-voxels', 'indirect/gi-cascades',
              'indirect/gi-limits', 'make/lamps', 'make/gi'],
    w8r_pages=['light/lights', 'light/many-lights', 'gpu/frame-tour', 'image/quality-settings', 'make/look',
               'make/quality', 'make/performance'],
    waves=c_Waves,
)


class Problem:
    """One problem: `text` says what is wrong (with its file and line where it has one), `advice` what to do, and
    `where` names the file for a problem whose text names none."""

    def __init__(self, text, advice=None, where=None):
        self.text = text
        self.advice = advice
        self.where = where

    def __str__(self):
        return '%s%s%s' % (self.where + ': ' if self.where else '', self.text, '; ' + self.advice if self.advice else '')

    def __repr__(self):
        return 'Problem(%r)' % str(self)


class Page:
    """A row of the outline."""

    def __init__(self, file, line, part, block, cells):
        self.file = file
        self.line = line
        self.part = part
        self.block = block
        self.raw = cells
        self.id = ''
        self.title = cells[1].strip()
        self.kind = cells[2].strip()
        self.size = cells[3].strip()
        self.tracks = []
        self.needs = []  # a list of Needs; a Need is a list of alternative ids
        self.mark = None  # None, "W8" or "W8r"
        self.mark_section = None
        self.index = 0  # the position in the book's order of rows
        self.wave = None

    def where(self):
        return '%s:%d: `%s`' % (self.file, self.line, self.id)

    @property
    def kind_word(self):
        return c_Kinds.get(self.kind, self.kind)

    @property
    def needs_text(self):
        """The Needs in the front matter's form: each a page id, or alternatives joined by "|"."""
        return ['|'.join(need) for need in self.needs]


class Part:
    def __init__(self, number, title, slug, file, line):
        self.number = number
        self.title = title
        self.slug = slug
        self.file = file
        self.line = line
        self.tracks_line = None
        self.needs_line = None
        self.needs_line_number = None
        self.pages = []


class Outline:
    def __init__(self, plan, book=c_Book):
        self.plan = plan
        self.book = book
        self.parts = []
        self.pages = []
        self.by_id = {}
        self.tracks = {}  # letter -> list of (id, side_step, line)
        self.problems = []

    def problem(self, text, advice=None, where=None):
        self.problems.append(Problem(text, advice, where))

    def path(self, name):
        return os.path.join(self.plan, name)


def split_row(line):
    """Splits a table row on pipes that are not escaped (`\\|` is the alternative separator)."""
    text = line.strip()
    if text.startswith('|'):
        text = text[1:]
    if text.endswith('|') and not text.endswith('\\|'):
        text = text[:-1]
    return [cell.strip() for cell in re.split(r'(?<!\\)\|', text)]


def parse_needs(cell, where, outline):
    cell = cell.strip()
    if cell == '-':
        return []
    needs = []
    for item in cell.split(','):
        item = item.strip()
        alternatives = []
        for alternative in item.split('\\|'):
            match = c_CodeId.match(alternative.strip())
            if not match:
                outline.problem('%s: Needs item %r is not `id` or `a`\\|`b`' % (where, item),
                                'write each Need as a page id in backticks, alternatives joined by \\|')
                alternatives = []
                break
            alternatives.append(match.group(1))
        if alternatives:
            if len(set(alternatives)) != len(alternatives):
                outline.problem('%s: Need %r names one alternative twice' % (where, item), 'name each alternative once')
            needs.append(alternatives)
    return needs


def parse_track_list(text):
    """The set of letters a Tracks line or a Parts table cell starts with, or None when it starts with no list."""
    match = c_TrackList.match(text.strip())
    if not match:
        return None
    rest = match.group(2)
    if rest and not (rest[0] in '.;' or rest.startswith(' (') or rest.startswith(' —')):
        return None
    return set() if match.group(1) == '-' else set(match.group(1).split(', '))


def parse_tracks_cell(cell, where, outline):
    cell = cell.strip()
    if cell == '-':
        return []
    letters = [letter.strip() for letter in cell.split(',')]
    for letter in letters:
        if letter not in c_TrackLetters:
            outline.problem('%s: Tracks %r holds %r; allowed: G, B, E or -' % (where, cell, letter),
                            'write the tracks as letters separated by ", "')
    if len(set(letters)) != len(letters):
        outline.problem('%s: Tracks %r names a track twice' % (where, cell), 'name each track once')
    return [letter for letter in letters if letter in c_TrackLetters]


def read_text(path):
    with open(path, encoding='utf-8') as file:
        return file.read()


def read_rows(outline):
    for name in c_OutlineFiles:
        path = outline.path(name)
        if not os.path.isfile(path):
            outline.problem('%s: file missing' % name, 'the outline is the four files %s' % ', '.join(c_OutlineFiles))
            continue
        part = None
        block = None
        continuing = None  # "tracks" or "needs" while a part's line wraps onto the next lines
        for number, line in enumerate(read_text(path).splitlines(), start=1):
            if continuing is not None:
                if (line.strip() and not line.startswith(('|', '#', '**'))
                        and not c_TracksLine.match(line) and not c_PartNeedsLine.match(line)):
                    if continuing == 'tracks':
                        part.tracks_line += ' ' + line.strip()
                    else:
                        part.needs_line += ' ' + line.strip()
                    continue
                continuing = None
            heading = c_PartHeading.match(line)
            if heading:
                part = Part(int(heading.group(1)), heading.group(2), heading.group(3), name, number)
                outline.parts.append(part)
                block = None
                continue
            if line.startswith('## ') or line.startswith('# '):
                if line.startswith('## Part'):
                    outline.problem('%s:%d: part heading not understood: %r' % (name, number, line),
                                    'write it as ## Part N — Title (`slug`)')
                part = None
                continue
            if part is None:
                if line.startswith('| `'):
                    outline.problem('%s:%d: a table row outside a part (no `## Part N — Title (`slug`)` heading above '
                                    'it): it is no page' % (name, number), 'move the row under its part\'s heading')
                continue
            block_line = c_BlockLine.match(line)
            if block_line:
                block = block_line.group(1)
                continue
            tracks_line = c_TracksLine.match(line)
            if tracks_line and part.tracks_line is None:
                part.tracks_line = tracks_line.group(1)
                continuing = 'tracks'
                continue
            needs_line = c_PartNeedsLine.match(line)
            if needs_line and part.needs_line is None:
                part.needs_line = needs_line.group(1)
                part.needs_line_number = number
                continuing = 'needs'
                continue
            if not line.startswith('|'):
                continue
            cells = split_row(line)
            if cells and cells[0] == 'id':
                if cells != c_Columns:
                    outline.problem('%s:%d: header %s differs from %s' % (name, number, cells, c_Columns),
                                    'use the columns of outline-1.md')
                continue
            if cells and set(cells[0]) <= {'-', ' ', ':'}:
                continue
            if len(cells) != len(c_Columns):
                outline.problem('%s:%d: row has %d columns, not %d' % (name, number, len(cells), len(c_Columns)),
                                'escape a | inside a cell as \\|')
                continue
            page = Page(name, number, part, block, cells)
            id_match = c_CodeId.match(cells[0])
            if not id_match:
                outline.problem('%s:%d: id %r is not written as `id`' % (name, number, cells[0]),
                                'write the id in backticks')
                continue
            page.id = id_match.group(1)
            where = page.where()
            page.tracks = parse_tracks_cell(cells[4], where, outline)
            page.needs = parse_needs(cells[5], where, outline)
            from_cell = cells[6]
            mark = c_MarkAtEnd.search(from_cell)
            rest = from_cell[:mark.start()] if mark else from_cell
            if mark:
                page.mark = mark.group(1)
                page.mark_section = mark.group(2)
            if c_AnyMark.search(rest):
                outline.problem('%s: From holds a mark other than a final ` · W8` or ` · W8r (<section>)`' % where,
                                'end the From with the mark, or remove it')
            part.pages.append(page)
            page.index = len(outline.pages)
            outline.pages.append(page)


def read_tracks(outline):
    path = outline.path(c_TracksFile)
    if not os.path.isfile(path):
        outline.problem('%s: file missing' % c_TracksFile, 'write the three tracks as numbered lists')
        for letter in c_TrackLetters:
            outline.tracks[letter] = []
        return
    letter = None
    expected = 1
    for number, line in enumerate(read_text(path).splitlines(), start=1):
        heading = c_TrackHeading.match(line)
        if heading:
            letter = heading.group(1)
            if letter not in c_TrackLetters:
                outline.problem('%s:%d: track %s is not one of G, B, E' % (c_TracksFile, number, letter),
                                'name the track G, B or E')
            if letter in outline.tracks:
                outline.problem('%s:%d: track %s is listed twice' % (c_TracksFile, number, letter),
                                'keep one list per track')
            outline.tracks[letter] = []
            expected = 1
            continue
        if c_OtherHeading.match(line):
            letter = None
            continue
        if letter is None or not c_NumberedLine.match(line):
            continue
        entry = c_TrackEntry.match(line)
        if not entry:
            outline.problem('%s:%d: entry not understood: %r' % (c_TracksFile, number, line),
                            'write it as N. `page/id`, optionally followed by " (side step)" and " — text"')
            continue
        if int(entry.group(1)) != expected:
            outline.problem('%s:%d: track %s entry numbered %s, expected %d' % (c_TracksFile, number, letter,
                            entry.group(1), expected), 'number the entries 1, 2, 3, … without gaps')
        expected = int(entry.group(1)) + 1
        outline.tracks[letter].append((entry.group(2), bool(entry.group(3)), number))
    for letter in c_TrackLetters:
        if letter not in outline.tracks:
            outline.problem('%s: track %s has no list (heading `## Track %s ...`)' % (c_TracksFile, letter, letter),
                            'add the heading and its numbered list')
            outline.tracks[letter] = []


def id_problems(page_id, part_page=False):
    """What is wrong with a page id of the site (rule O1, without uniqueness): (problem, advice) pairs. Part pages
    (`<part>/index`, `<part>/review`) may end in a reserved last segment; rows may not."""
    problems = []
    if not c_PageIdPattern.match(page_id):
        problems.append(('id %r is not lowercase segments of [a-z0-9-] joined by /' % page_id,
                         'rename the file in lowercase words joined by "-"'))
    first = page_id.split('/')[0]
    if first in c_ReservedFirstSegments or c_ReservedFirstSegment.match(first):
        problems.append(('id %r starts with %r, which the site reserves (site.md, "The base path", rule 8)'
                         % (page_id, first), 'choose another first segment'))
    if not part_page and page_id.split('/')[-1] in c_ReservedLastSegments and '/' in page_id:
        problems.append(('`%s` is reserved for a generated part page' % page_id, 'choose another last segment'))
    return problems


def banned_words_in(text):
    """The banned words (style.md §2.2) a text holds, as whole words in any case."""
    found = []
    for word in c_BannedWords:
        pattern = r'(?<![\w-])' + r'\s+'.join(map(re.escape, word.split())) + r'(?![\w-])'
        if re.search(pattern, text, re.IGNORECASE):
            found.append(word)
    return found


def check_rows(outline):
    book = outline.book
    seen = {}
    for page in outline.pages:
        where = page.where()
        if page.id in seen:
            outline.problem('%s: id duplicated (first at %s)' % (where, seen[page.id]), 'give each row its own id')
        else:
            seen[page.id] = '%s:%d' % (page.file, page.line)
            outline.by_id[page.id] = page
        if not c_IdPattern.match(page.id):
            outline.problem('%s: id is not lowercase segments of [a-z0-9-] joined by /' % where,
                            'write it as <part>/<chapter> in lowercase words joined by "-"')
        segments = page.id.split('/')
        if segments[0] != page.part.slug:
            outline.problem('%s: first segment %r is not the part\'s slug %r' % (where, segments[0], page.part.slug),
                            'start the id with its part\'s slug')
        if segments[-1] in c_ReservedLastSegments:
            outline.problem('%s: `%s/%s` is reserved for a generated part page' % (where, page.part.slug, segments[-1]),
                            'choose another last segment')
        first = segments[0]
        if first in c_ReservedFirstSegments or c_ReservedFirstSegment.match(first):
            outline.problem('%s: the first segment %r is reserved by the site (site.md, "The base path", rule 8)'
                            % (where, first), 'choose another slug')
        if not page.title:
            outline.problem('%s: no title' % where, 'write the page\'s published title')
        for word in banned_words_in(page.title):
            outline.problem('%s: the title holds %r, a banned word of style.md §2.2' % (where, word),
                            'say it without the word (rulings 5, R17)')
        if page.kind not in c_Kinds:
            outline.problem('%s: kind %r is not one of %s' % (where, page.kind, ', '.join(c_Kinds)),
                            'write one of the six letters')
        if page.size not in c_Sizes:
            outline.problem('%s: size %r is not one of %s' % (where, page.size, ', '.join(c_Sizes)),
                            'write S, M, L or XL')
        if page.size == 'XL' and (page.kind == 'P' or 'B' in page.tracks):
            outline.problem('%s: primers and pages of track B are at most L' % where,
                            'make it L, or split the page (rulings 4, R7)')
        if page.mark == 'W8' and page.mark_section:
            outline.problem('%s: a W8 mark names no section' % where, 'write ` · W8` alone')
        if page.mark == 'W8r' and not page.mark_section:
            outline.problem('%s: a W8r mark names its revised section: ` · W8r (<section>)`' % where,
                            'add the section in parentheses')
        ids = sum(len(need) for need in page.needs)
        if ids > c_MaxNeedIds:
            outline.problem('%s: its Needs name %d page ids (alternatives included), more than %d'
                            % (where, ids, c_MaxNeedIds), 'leave out Needs that an earlier Need already needs')
        if (set(page.tracks) & {'G', 'B'}) and page.kind in c_Kinds and page.kind not in book.gb_kinds:
            outline.problem('%s: kind %s on track G or B; a game maker never has to read internals or reference '
                            '(allowed: %s)' % (where, page.kind, ', '.join(sorted(book.gb_kinds))),
                            'change the kind or the tracks')
        if page.part.slug == 'basics' and page.kind != 'P':
            outline.problem('%s: every page of `basics` is a primer (kind P), not %s' % (where, page.kind),
                            'make it a primer or move it to another part')
        expected_mark = 'W8' if page.id in book.w8_pages else 'W8r' if page.id in book.w8r_pages else None
        if page.mark != expected_mark:
            outline.problem('%s: mark %s, but rulings 1 (R6) give it %s' % (where, page.mark or 'none',
                            expected_mark or 'none'), 'write the mark rulings 1 give')
    for part in outline.parts:
        if not part.pages:
            outline.problem('%s:%d: part `%s` has no rows' % (part.file, part.line, part.slug),
                            'add its rows or remove the part')
    numbers = [part.number for part in outline.parts]
    if numbers != list(range(len(numbers))):
        outline.problem('parts are numbered %s, not 0 to %d in order' % (numbers, len(numbers) - 1),
                        'number the part headings 0, 1, 2, … in order', where=c_OutlineFiles[0])
    slugs = [part.slug for part in outline.parts]
    for slug in set(slugs):
        if slugs.count(slug) > 1:
            outline.problem('part slug `%s` is used by %d parts' % (slug, slugs.count(slug)),
                            'give each part its own slug', where=c_OutlineFiles[0])
    if slugs != book.part_order:
        outline.problem('the parts are %s; rulings 2 order them %s' % (slugs, book.part_order),
                        'put the part headings in that order', where=c_OutlineFiles[0])
    for mark, pages in (('W8', book.w8_pages), ('W8r', book.w8r_pages)):
        for page_id in sorted(pages):
            if page_id not in seen:
                outline.problem('rulings 1 (R6) mark `%s` %s, but it is no row of the outline' % (page_id, mark),
                                'add the row, or ask the planner to change the ruling', where=c_OutlineFiles[0])


def expected_tracks(outline, page):
    """The tracks a row is on, by rulings 1 (R4): its part decides, and within `start`, `make` and `basics` the
    rows R4 names."""
    book = outline.book
    slug = page.part.slug
    if slug == 'start':
        return {'G', 'E'} if page.id in book.not_on_b else {'G', 'B', 'E'}
    if slug == 'make':
        return {'G', 'B'} if page.block == 'A' else {'G'}
    if slug == 'basics':
        return {'G', 'B', 'E'} if page.id in book.programming_primers else {'B', 'E'}
    if slug in book.trackless_parts:
        return set()
    return {'E'}


def check_page_tracks(outline):
    for page in outline.pages:
        want = expected_tracks(outline, page)
        if set(page.tracks) != want:
            outline.problem('%s: Tracks %s; rulings 1 (R4) put it on %s' % (page.where(), ', '.join(page.tracks) or '-',
                            ', '.join(letter for letter in c_TrackLetters if letter in want) or '-'),
                            'write those tracks')
    make = next((part for part in outline.parts if part.slug == 'make'), None)
    if make is not None:
        for page in make.pages:
            if page.block not in ('A', 'B', 'C'):
                outline.problem('%s: a row of `make` outside the blocks A, B and C' % page.where(),
                                'put it under a **Block A|B|C — …** line')


def expected_sequences(outline):
    """The three tracks as rulings 1 (R4) state them, from the rows of the outline; None when a named page is missing."""
    book = outline.book
    rows = {slug: [page.id for page in outline.pages if page.part.slug == slug] for slug in book.part_order}
    block_a = [page.id for page in outline.pages if page.part.slug == 'make' and page.block == 'A']
    named = ([book.first_script] + book.programming_primers + book.g_side_steps + book.b_before_first_script
             + sorted(book.not_on_b))
    missing = [page_id for page_id in named if page_id not in outline.by_id]
    if missing or book.first_script not in block_a:
        for page_id in missing:
            outline.problem('rulings 1 (R4) name `%s`, which is no row of the outline' % page_id,
                            'add the row, or ask the planner to change the ruling', where=c_OutlineFiles[0])
        if book.first_script in outline.by_id and book.first_script not in block_a:
            outline.problem('`%s` is not in block A of `make`' % book.first_script, 'move it to block A',
                            where=c_OutlineFiles[0])
        return None
    make = rows.get('make', [])
    at = make.index(book.first_script) + 1
    g = rows.get('start', []) + make[:at] + book.programming_primers + make[at:]
    at = block_a.index(book.first_script)
    taken = set(book.b_before_first_script) | set(book.programming_primers)
    b = ([page_id for page_id in rows.get('start', []) if page_id not in book.not_on_b] + block_a[:at]
         + book.b_before_first_script + [book.first_script] + book.programming_primers + block_a[at + 1:]
         + [page_id for page_id in rows.get('basics', []) if page_id not in taken])
    e = [page.id for page in outline.pages if page.part.slug != 'make' and page.part.slug not in book.trackless_parts]
    return {'G': g, 'B': b, 'E': e}


def check_needs_exist(outline):
    for page in outline.pages:
        for need in page.needs:
            for alternative in need:
                if alternative not in outline.by_id:
                    outline.problem('%s: Need `%s` does not exist' % (page.where(), alternative),
                                    'name a row of the outline')
                elif alternative == page.id:
                    outline.problem('%s: needs itself' % page.where(), 'remove the Need')


def find_cycles(graph, order):
    """Each cycle of a graph of Needs ({id: [ids it needs]}), as a list of ids with the first repeated at the end, in
    the order a walk from each id of `order` finds them. Ids the graph does not hold are skipped."""
    state = {}
    cycles = []

    def visit(node, stack):
        state[node] = 1
        stack.append(node)
        for following in graph.get(node, []):
            if following not in graph:
                continue
            if state.get(following) == 1:
                cycles.append(stack[stack.index(following):] + [following])
            elif following not in state:
                visit(following, stack)
        stack.pop()
        state[node] = 2

    for node in order:
        if node not in state and node in graph:
            visit(node, [])
    return cycles


def check_cycles(outline):
    # Pages on a track cannot form a cycle (each Need is earlier); this also covers pages on no track.
    graph = {page_id: [alternative for need in page.needs for alternative in need]
             for page_id, page in outline.by_id.items()}
    for cycle in find_cycles(graph, [page.id for page in outline.pages]):
        first = outline.by_id[cycle[0]]
        outline.problem('Needs form a cycle: %s' % ' -> '.join(cycle), 'remove one of these Needs',
                        where='%s:%d' % (first.file, first.line))


def part_needs(part):
    """The part's Needs of the part, computed from its rows: each Need of a row that points outside the part, once, as
    "a|b" strings; a Need with an alternative inside the part is met inside it and is left out."""
    ids_in_part = {page.id for page in part.pages}
    needs = []
    for page in part.pages:
        for need in page.needs:
            if not any(alternative in ids_in_part for alternative in need):
                text = '|'.join(need)
                if text not in needs:
                    needs.append(text)
    return needs


def check_part_lines(outline):
    for part in outline.parts:
        letters = set()
        for page in part.pages:
            letters.update(page.tracks)
        if part.tracks_line is None:
            outline.problem('%s:%d: part `%s` has no `Tracks:` line' % (part.file, part.line, part.slug),
                            'add it below the heading')
        else:
            written = parse_track_list(part.tracks_line)
            if written is None:
                outline.problem('%s:%d: part `%s`\'s Tracks line does not start with its letters (`G, B, E` or `-`), '
                                'followed by nothing or by ".", ";", " (" or " —"' % (part.file, part.line, part.slug),
                                'start it with the letters')
            elif written != letters:
                outline.problem('%s:%d: part `%s`\'s Tracks line names %s, its rows are on %s'
                                % (part.file, part.line, part.slug, sorted(written), sorted(letters)),
                                'write the tracks of its rows')
        if part.needs_line is None:
            outline.problem('%s:%d: part `%s` has no `Needs of the part:` line' % (part.file, part.line, part.slug),
                            'add it below the Tracks line')
            continue
        expected = set(part_needs(part))
        written = set()
        text = part.needs_line.strip()
        if text != '-':
            for item in text.split(','):
                alternatives = re.findall(r'`([^`]+)`', item)
                if not alternatives or re.sub(r'`[^`]+`|\\\||\s|\.$', '', item):
                    outline.problem('%s:%d: Needs of the part item %r is not `id` or `a`\\|`b`'
                                    % (part.file, part.needs_line_number, item.strip()),
                                    'write each Need as a page id in backticks, alternatives joined by \\|')
                    continue
                written.add('|'.join(alternatives))
        for need in sorted(expected - written):
            outline.problem('%s:%d: Needs of the part lacks `%s`, which a row of `%s` needs'
                            % (part.file, part.needs_line_number, need.replace('|', '`|`'), part.slug),
                            'add it to the line')
        for need in sorted(written - expected):
            outline.problem('%s:%d: Needs of the part names `%s`, which no row of `%s` needs from another part'
                            % (part.file, part.needs_line_number, need.replace('|', '`|`'), part.slug),
                            'remove it from the line')


def track_order(outline, letter):
    """The pages on a track, in order: side steps are offered, not on the track."""
    return [page_id for page_id, side_step, _ in outline.tracks[letter] if not side_step]


def needs_met_earlier(order, needs_of):
    """For a track's reading order and a function giving a page's Needs (lists of alternatives, or None for an
    unknown page): (page id, Need) for every Need of which no alternative comes earlier on the track (rule O4)."""
    position = {page_id: number for number, page_id in enumerate(order)}
    missing = []
    for page_id in order:
        needs = needs_of(page_id)
        if needs is None:
            continue
        for need in needs:
            if not any(alternative in position and position[alternative] < position[page_id] for alternative in need):
                missing.append((page_id, need))
    return missing


def check_tracks(outline):
    book = outline.book
    for letter in c_TrackLetters:
        entries = outline.tracks[letter]
        listed = {}
        for page_id, side_step, line in entries:
            if page_id not in outline.by_id:
                outline.problem('%s:%d: track %s lists `%s`, which is no row of the outline'
                                % (c_TracksFile, line, letter, page_id), 'list rows only')
                continue
            if page_id in listed:
                outline.problem('%s:%d: track %s lists `%s` twice' % (c_TracksFile, line, letter, page_id),
                                'list each page once')
            listed[page_id] = side_step
            page = outline.by_id[page_id]
            if side_step and letter in page.tracks:
                outline.problem('%s:%d: `%s` is a side step of track %s, but its Tracks column names %s'
                                % (c_TracksFile, line, page_id, letter, letter),
                                'a side step is not on the track: change the entry or the Tracks column')
        on_track = {page_id for page_id, side_step in listed.items() if not side_step}
        for page in outline.pages:
            if letter in page.tracks and page.id not in on_track:
                outline.problem('%s: Tracks names %s, but track %s\'s list in %s does not hold it'
                                % (page.where(), letter, letter, c_TracksFile), 'add it to the list or the Tracks column')
            if letter not in page.tracks and page.id in on_track:
                outline.problem('%s: track %s\'s list in %s holds it, but its Tracks column does not name %s'
                                % (page.where(), letter, c_TracksFile, letter), 'add the letter or remove the entry')
        order = track_order(outline, letter)
        position = {page_id: number for number, page_id in enumerate(order)}
        # Every Need, or one of its alternatives, comes earlier on the track.

        def needs_of(page_id):
            page = outline.by_id.get(page_id)
            return page.needs if page is not None else None

        for page_id, need in needs_met_earlier(order, needs_of):
            outline.problem('%s: on track %s, no alternative of Need `%s` comes earlier'
                            % (outline.by_id[page_id].where(), letter, '`|`'.join(need)),
                            'move the Need earlier on the track, or change the Need')
        # Within one part, a track keeps the outline's row order.
        last_in_part = {}
        for page_id in order:
            page = outline.by_id.get(page_id)
            if page is None:
                continue
            previous = last_in_part.get(page.part.slug)
            if previous is not None and outline.by_id[previous].index > page.index:
                outline.problem('%s: track %s puts `%s` after `%s`, against the order of their part\'s rows'
                                % (c_TracksFile, letter, page_id, previous), 'list them in the order of the rows')
            last_in_part[page.part.slug] = page_id
        # A side step stands directly before the first page of the track whose Needs name it, and its own Needs (one
        # alternative of each) come earlier on the track, or are earlier side steps.
        side_steps_before = set()
        for number, (page_id, side_step, line) in enumerate(entries):
            if not side_step or page_id not in outline.by_id:
                continue
            following = next((entry for entry in entries[number + 1:] if not entry[1]), None)
            first_user = next((other for other in order if other in outline.by_id
                               and any(page_id in need for need in outline.by_id[other].needs)), None)
            if first_user is None:
                outline.problem('%s:%d: side step `%s` of track %s: no page of the track names it in its Needs'
                                % (c_TracksFile, line, page_id, letter), 'remove the side step')
            elif following is None or following[0] != first_user:
                outline.problem('%s:%d: side step `%s` of track %s must stand directly before `%s`, the first page of '
                                'the track whose Needs name it' % (c_TracksFile, line, page_id, letter, first_user),
                                'move the entry')
            at = position.get(following[0], len(order)) if following is not None else len(order)
            for need in outline.by_id[page_id].needs:
                if not any((alternative in position and position[alternative] < at) or alternative in side_steps_before
                           for alternative in need):
                    outline.problem('%s:%d: side step `%s` of track %s: no alternative of its Need `%s` comes earlier '
                                    'on the track, so its reader meets it untaught'
                                    % (c_TracksFile, line, page_id, letter, '`|`'.join(need)),
                                    'move the side step later or change its Needs')
            side_steps_before.add(page_id)
    # The lists are the sequences of rulings 1 (R4); track E is the book's order.
    sequences = expected_sequences(outline)
    if sequences is not None:
        for letter in c_TrackLetters:
            order = track_order(outline, letter)
            want = sequences[letter]
            if order != want:
                number = next((n for n, (got, expected) in enumerate(zip(order, want)) if got != expected),
                              min(len(order), len(want)))
                got = '`%s`' % order[number] if number < len(order) else 'the end of the list'
                expected = '`%s`' % want[number] if number < len(want) else 'the end of the list'
                outline.problem('%s: track %s entry %d is %s; rulings 1 (R4) put %s there'
                                % (c_TracksFile, letter, number + 1, got, expected),
                                'write the track as rulings 1 (R4) give it')
        side_steps = {letter: [page_id for page_id, side_step, _ in outline.tracks[letter] if side_step]
                      for letter in c_TrackLetters}
        if sorted(side_steps['G']) != sorted(book.g_side_steps):
            outline.problem('%s: track G\'s side steps are %s; rulings 1 (R4) give %s'
                            % (c_TracksFile, side_steps['G'], book.g_side_steps), 'list exactly those side steps')
        for letter in ('B', 'E'):
            if side_steps[letter]:
                outline.problem('%s: track %s has side steps %s; only track G has side steps (rulings 1, R4)'
                                % (c_TracksFile, letter, side_steps[letter]), 'remove them')
    # A page on no track: every Need (one alternative) comes earlier in the book's order of rows (rulings 1, R1).
    for page in outline.pages:
        if page.tracks:
            continue
        for need in page.needs:
            if not any(alternative in outline.by_id and outline.by_id[alternative].index < page.index
                       for alternative in need):
                outline.problem('%s: on no track, and no alternative of its Need `%s` comes earlier in the book\'s '
                                'order' % (page.where(), '`|`'.join(need)), 'move the row later or change the Need')


def assign_waves(outline):
    book = outline.book
    names = [wave[0] for wave in book.waves]
    for page in outline.pages:
        keys = []
        if page.mark == 'W8':
            keys.append('W8')
        if page.part.slug == 'make':
            keys.append('make:%s' % page.block)
        keys.append(page.part.slug)
        for key in keys:
            for name, _, selectors in book.waves:
                if key in selectors:
                    page.wave = name
                    break
            if page.wave is not None:
                break
        if page.wave is None:
            outline.problem('%s: no writing wave holds it (the waves in tools/booklib/outline.py)' % page.where(),
                            'add its part to a wave')
    selectors_used = {}
    for name, _, selectors in book.waves:
        for selector in selectors:
            if selector in selectors_used:
                outline.problem('WAVES: selector %r is in waves %s and %s' % (selector, selectors_used[selector], name),
                                'keep each selector in one wave', where='tools/booklib/outline.py')
            selectors_used[selector] = name
    rank = {name: number for number, name in enumerate(names)}
    for page in outline.pages:
        if page.wave is None:
            continue
        for need in page.needs:
            waves = [outline.by_id[alternative].wave for alternative in need
                     if alternative in outline.by_id and outline.by_id[alternative].wave is not None]
            if waves and all(rank[wave] > rank[page.wave] for wave in waves):
                outline.problem('%s: wave %s page needs `%s` of wave %s'
                                % (page.where(), page.wave, '`|`'.join(need), min(waves, key=rank.get)),
                                'fix the wave list, not the Needs (rulings 3)')


def to_number(text):
    text = text.strip().replace(',', '')
    if text.isdigit():
        return int(text)
    return c_NumberWords.get(text.lower())


def table_rows(text, header_start):
    """The rows of the first table whose header line starts with `header_start`, as lists of cells; None if absent."""
    lines = [line.strip() for line in text.splitlines()]  # a table may stand indented inside a list item
    for number, line in enumerate(lines):
        if line.startswith(header_start):
            rows = []
            for row in lines[number + 2:]:
                if not row.startswith('|'):
                    break
                rows.append(split_row(row))
            return rows
    return None


def compute_counts(outline):
    pages = outline.pages
    counts = {
        'pages': len(pages),
        'parts': len(outline.parts),
        'kinds': {kind: sum(1 for page in pages if page.kind == kind) for kind in c_Kinds},
        'sizes': {size: sum(1 for page in pages if page.size == size) for size in c_Sizes},
        'track': {letter: sum(1 for page in pages if letter in page.tracks) for letter in c_TrackLetters},
        'side steps': {letter: sum(1 for _, side_step, _ in outline.tracks[letter] if side_step)
                       for letter in c_TrackLetters},
        'trackless': sum(1 for page in pages if not page.tracks),
        'track kinds': {letter: {kind: sum(1 for page in pages if letter in page.tracks and page.kind == kind)
                                 for kind in c_Kinds} for letter in c_TrackLetters},
        'words': sum(c_Words.get(page.size, 0) for page in pages),
        'track words': {letter: sum(c_Words.get(page.size, 0) for page in pages if letter in page.tracks)
                        for letter in c_TrackLetters},
        'generated parts': sum(1 for part in outline.parts if len(part.pages) >= c_GeneratedPagesFrom),
        'waves': {name: (sum(1 for page in pages if page.wave == name),
                         sum(c_Words.get(page.size, 0) for page in pages if page.wave == name))
                  for name, _, _ in outline.book.waves},
        'W8': sum(1 for page in pages if page.mark == 'W8'),
        'W8r': sum(1 for page in pages if page.mark == 'W8r'),
        'part': {part.slug: part for part in outline.parts},
    }
    counts['phase B'] = counts['waves'].get('B', (0, 0))[0]
    counts['phase A'] = counts['pages'] - counts['phase B']
    return counts


def document_sentences(counts):
    """(file, pattern, expected values): every sentence of book.md, process.md and README.md that states a count of
    the outline. Each pattern must occur at least once, and every occurrence must state the expected values."""
    kinds = counts['kinds']
    sizes = counts['sizes']
    words = counts['track words']
    part = counts['part']
    generated = counts['generated parts']
    reference = len(part['reference'].pages) if 'reference' in part else 0
    appendix = len(part['appendix'].pages) if 'appendix' in part else 0
    return [
        ('book.md', r'\*\*(\d+) pages\*\* in (\d+) parts, plus (\d+) generated index and review pages in (\d+) parts',
            (counts['pages'], counts['parts'], 2 * generated, generated)),
        ('book.md', r'About ([\d,]+) words: track G reads about ([\d,]+), track B ([\d,]+) and track E ([\d,]+)',
            (counts['words'], words['G'], words['B'], words['E'])),
        ('book.md', r'Kinds: P (\d+), C (\d+), I (\d+), T (\d+), H (\d+), R (\d+)',
            tuple(kinds[kind] for kind in 'PCITHR')),
        ('book.md', r'Sizes: S about ([\d,]+) words \((\d+) pages\), M ([\d,]+) \((\d+)\), L ([\d,]+) \((\d+)\), XL ([\d,]+) '
            r'\((\d+)\)', tuple(value for size in c_Sizes for value in (c_Words[size], sizes[size]))),
        ('book.md', r'A size is a budget of prose words with a range: S ([\d,]+) to ([\d,]+), M ([\d,]+) to ([\d,]+), '
            r'L ([\d,]+) to ([\d,]+), XL ([\d,]+) to ([\d,]+)', tuple(value for size in c_Sizes for value in c_Ranges[size])),
        ('book.md', r'Each of the (\d+) parts with eight or more rows', (generated,)),
        ('book.md', r'That makes (\d+) generated pages', (2 * generated,)),
        ('book.md', r'The (\d+) pages of `reference` and `appendix` are on no track', (counts['trackless'],)),
        ('README.md', r'(\d+) pages in (\d+) parts', (counts['pages'], counts['parts'])),
        ('README.md', r'The outline is final: (\d+) pages', (counts['pages'],)),
        ('README.md', r'the (\d+) primers of `basics`', (kinds['P'],)),
        ('README.md', r'The (\d+) parts of eight or more pages', (generated,)),
        ('README.md', r'The (\w+) W8 pages', (counts['W8'],)),
        ('README.md', r'the (\w+) W8r pages', (counts['W8r'],)),
        ('process.md', r'(\d+) pages in (\d+) parts, (\d+) of them written in phase A and (\d+) in phase B',
            (counts['pages'], counts['parts'], counts['phase A'], counts['phase B'])),
        ('process.md', r'for the (\d+) parts of eight or more pages', (generated,)),
        ('process.md', r'the (\d+) parts of eight or more pages have their index and review pages', (generated,)),
        ('process.md', r'the (\d+) W8 pages are written', (counts['W8'],)),
        ('process.md', r'the (\d+) W8r pages have the section', (counts['W8r'],)),
        ('process.md', r'the (\d+) pages of `reference` are written .{0,60}?, and the (\d+) pages of `appendix`',
            (reference, appendix)),
        ('process.md', r'the (\d+) W8 pages, `reference` \((\d+) pages\), `appendix` \((\d+) pages\)',
            (counts['W8'], reference, appendix)),
        ('process.md', r'The work is large: (\d+) pages', (counts['pages'],)),
        ('process.md', r'all (\d+) pages of the outline are `final`', (counts['pages'],)),
        ('process.md', r'for each of the (\d+) parts', (counts['parts'],)),
    ]


def check_documents(outline):
    """The counts book.md, process.md and README.md state agree with the outline (rulings 3: the counts come from
    this check)."""
    counts = compute_counts(outline)
    texts = {}
    for name in c_Documents:
        path = outline.path(name)
        if not os.path.isfile(path):
            outline.problem('%s: file missing' % name, 'the plan states its counts in it')
            continue
        texts[name] = read_text(path)
    flat = {name: re.sub(r'\s+', ' ', text) for name, text in texts.items()}
    for name, pattern, expected in document_sentences(counts):
        if name not in flat:
            continue
        matches = list(re.finditer(pattern, flat[name]))
        if not matches:
            outline.problem('%s: no sentence matches %r; it states counts this script checks (document_sentences in '
                            'tools/booklib/outline.py)' % (name, pattern),
                            'restore the sentence, or change the pattern with it')
        for match in matches:
            got = tuple(to_number(group) for group in match.groups())
            if got != tuple(expected):
                outline.problem('%s: %r states %s; the outline gives %s' % (name, match.group(0), got, tuple(expected)),
                                'write the outline\'s counts (--counts, --words and --waves print them)')
    book = texts.get('book.md')
    if book is not None:
        check_book_tables(outline, counts, book, flat['book.md'])
    process = texts.get('process.md')
    if process is not None:
        rows = table_rows(process, '| Wave | Parts | Pages |')
        if rows is None:
            outline.problem('process.md: no table of the waves (header `| Wave | Parts | Pages | Estimated words |`)',
                            'restore the table')
        else:
            seen = []
            for cells in rows:
                name = cells[0].strip()
                seen.append(name)
                if name not in counts['waves']:
                    outline.problem('process.md: wave %r is not in WAVES' % name,
                                    'name the waves of tools/booklib/outline.py')
                    continue
                want = counts['waves'][name]
                got = (to_number(cells[2]), to_number(cells[3]))
                if got != want:
                    outline.problem('process.md: wave %s states %s pages and %s words; the outline gives %s and %s'
                                    % (name, got[0], cells[3], want[0], format(want[1], ',')),
                                    'write the outline\'s counts (--waves prints them)')
            if seen != [name for name, _, _ in outline.book.waves]:
                outline.problem('process.md: the waves table lists %s, WAVES %s'
                                % (seen, [name for name, _, _ in outline.book.waves]),
                                'list the waves of tools/booklib/outline.py in order')


def check_book_tables(outline, counts, book, flat):
    rows = table_rows(book, '| # | Part | Slug |')
    if rows is None:
        outline.problem('book.md: no Parts table (header `| # | Part | Slug | Tracks | Pages | Words (estimate) '
                        '| Index and review pages |`)', 'restore the table')
    else:
        slugs = []
        for cells in rows:
            if len(cells) < 7:
                outline.problem('book.md: Parts table row %s has fewer than 7 cells' % cells, 'fill every cell')
                continue
            slug = cells[2].strip('` ')
            slugs.append(slug)
            part = counts['part'].get(slug)
            if part is None:
                outline.problem('book.md: Parts table row `%s` is no part of the outline' % slug,
                                'list the outline\'s parts')
                continue
            where = 'book.md: Parts table, `%s`' % slug
            if to_number(cells[0]) != part.number:
                outline.problem('%s: number %s, the outline\'s is %d' % (where, cells[0], part.number),
                                'write the outline\'s number')
            letters = set()
            for page in part.pages:
                letters.update(page.tracks)
            written = parse_track_list(cells[3])
            if written != letters:
                outline.problem('%s: Tracks %r does not start with the tracks of its rows, %s'
                                % (where, cells[3], ', '.join(letter for letter in c_TrackLetters if letter in letters)
                                   or '-'), 'start the cell with those letters')
            pages = re.match(r'(\d+)', cells[4])
            if not pages or int(pages.group(1)) != len(part.pages):
                outline.problem('%s: Pages %r, the outline has %d' % (where, cells[4], len(part.pages)),
                                'write the outline\'s count')
            blocks = dict((block, int(n)) for block, n in re.findall(r'\b([A-Z]) (\d+)\b', cells[4]))
            for block, n in blocks.items():
                actual = sum(1 for page in part.pages if page.block == block)
                if n != actual:
                    outline.problem('%s: block %s has %d pages in the table, %d in the outline'
                                    % (where, block, n, actual), 'write the outline\'s count')
            part_words = sum(c_Words.get(page.size, 0) for page in part.pages)
            if to_number(cells[5]) != part_words:
                outline.problem('%s: Words %r, the outline\'s sizes give %s' % (where, cells[5],
                                format(part_words, ',')), 'write the outline\'s estimate')
            generated = 'yes' if len(part.pages) >= c_GeneratedPagesFrom else 'no'
            if cells[6].strip() != generated:
                outline.problem('%s: Index and review pages %r, the outline gives %r' % (where, cells[6], generated),
                                'write the outline\'s answer')
        if slugs != [part.slug for part in outline.parts]:
            outline.problem('book.md: the Parts table does not list the outline\'s parts in order',
                            'list them in the outline\'s order')
    rows = table_rows(book, '| Kind | Answers |')
    if rows is None:
        outline.problem('book.md: no table of the kinds of page (header `| Kind | Answers | ...`)', 'restore the table')
    else:
        for cells in rows:
            kind = re.match(r'\*\*([A-Z]) ', cells[0])
            if kind and kind.group(1) in c_Kinds and to_number(cells[-1]) != counts['kinds'][kind.group(1)]:
                outline.problem('book.md: kind %s has %s pages in the table, %d in the outline'
                                % (kind.group(1), cells[-1], counts['kinds'][kind.group(1)]),
                                'write the outline\'s count')
    rows = table_rows(book, '| Track | Persona |')
    if rows is None:
        outline.problem('book.md: no table of the tracks (header `| Track | Persona | Reads | Size |`)',
                        'restore the table')
    else:
        for cells in rows:
            letter = re.match(r'\*\*([GBE])\*\*', cells[0])
            size = re.match(r'(\d+) pages(?: and (\d+) side steps)?', cells[-1])
            if not letter:
                continue
            letter = letter.group(1)
            want = (counts['track'][letter], counts['side steps'][letter])
            got = (int(size.group(1)), int(size.group(2) or 0)) if size else None
            if got != want:
                outline.problem('book.md: track %s\'s Size %r; the outline gives %d pages and %d side steps'
                                % (letter, cells[-1], want[0], want[1]), 'write the outline\'s counts')
    match = re.search(r'track G holds (.+?) pages, and track B holds (.+?)\.', flat)
    if not match:
        outline.problem('book.md: no sentence "track G holds … pages, and track B holds …" (rule 2 of Tracks)',
                        'restore the sentence')
    else:
        for letter, text in (('G', match.group(1)), ('B', match.group(2))):
            written = {kind: int(n) for kind, n in re.findall(r'\b([A-Z]) (\d+)\b', text)}
            actual = {kind: n for kind, n in counts['track kinds'][letter].items() if n}
            if written != actual:
                outline.problem('book.md: track %s holds %s by rule 2 of Tracks, %s by the outline'
                                % (letter, written, actual), 'write the outline\'s counts')


def read(plan, book=c_Book, documents=None):
    """Reads and checks the outline in the folder `plan`. `documents` (default: the book's setting) also checks the
    counts that book.md, process.md and README.md state. The problems are in `outline.problems`."""
    outline = Outline(plan, book)
    read_rows(outline)
    read_tracks(outline)
    check_rows(outline)
    check_page_tracks(outline)
    check_needs_exist(outline)
    check_cycles(outline)
    check_part_lines(outline)
    check_tracks(outline)
    assign_waves(outline)
    if book.documents if documents is None else documents:
        check_documents(outline)
    return outline


def needed(outline, page):
    """The Needs a page has for its closure: its own, or, for a row with `-` that is not its part's first row, the
    part's first row (style.md §1.2: "A page whose outline row has `-` needs the first page of its part")."""
    if page.needs:
        return page.needs
    first = page.part.pages[0] if page.part.pages else None
    return [[first.id]] if first is not None and first is not page else []


def closure(outline, page_id):
    """Every page reached from a page through its Needs (needed()), every alternative followed; the page itself is not
    in it."""
    seen = set()
    stack = [page_id]
    while stack:
        page = outline.by_id.get(stack.pop())
        if page is None:
            continue
        for need in needed(outline, page):
            for alternative in need:
                if alternative not in seen and alternative != page_id:
                    seen.add(alternative)
                    stack.append(alternative)
    return seen


def taught(outline, page_id, memo=None):
    """The pages whose teaching a page may use (style.md §1.2, item 2): its Needs closure, where a Need with
    alternatives (`a|b`) counts only what both alternatives teach, with their closures. The page itself is not in it.
    `memo` keeps the sets of pages already computed across calls."""
    memo = {} if memo is None else memo
    if page_id in memo:
        return memo[page_id]
    memo[page_id] = set()  # a cycle (the outline check reports it) adds nothing
    page = outline.by_id.get(page_id)
    result = set()
    if page is not None:
        for need in needed(outline, page):
            shared = None
            for alternative in need:
                pages = ({alternative} | taught(outline, alternative, memo)) if alternative in outline.by_id else set()
                shared = pages if shared is None else shared & pages
            result |= shared or set()
    result.discard(page_id)
    memo[page_id] = result
    return result


def level(outline, page):
    """style.md §6.2: 1 when every page of the Needs closure is in parts 0 to 2; 3 when it holds a page of a part
    numbered 6 or higher other than the page's own part; 2 otherwise. The closure follows every alternative."""
    numbers = {part.slug: part.number for part in outline.parts}
    parts = {outline.by_id[other].part.slug for other in closure(outline, page.id) if other in outline.by_id}
    if all(numbers[slug] <= 2 for slug in parts):
        return 1
    if any(numbers[slug] >= 6 and slug != page.part.slug for slug in parts):
        return 3
    return 2


def source_digests(plan):
    """{"plan/<file>": sha256} of the outline's and the tracks' files."""
    digests = {}
    for name in c_OutlineFiles + (c_TracksFile,):
        path = os.path.join(plan, name)
        with open(path, 'rb') as file:
            digests['plan/' + name] = hashlib.sha256(file.read()).hexdigest()
    return digests


def to_data(outline):
    """The outline as the data of src/generated/outline.json (.tools/handover/outline-format.md)."""
    def letters(tracks):
        return [letter for letter in c_TrackLetters if letter in tracks]

    return {
        'generated': 'tools/pages.py outline --write; do not edit',
        'sources': source_digests(outline.plan),
        'parts': [{
            'number': part.number,
            'slug': part.slug,
            'title': part.title,
            'tracks': letters({letter for page in part.pages for letter in page.tracks}),
            'needs': part_needs(part),
            'pages': [page.id for page in part.pages],
            'partPages': len(part.pages) >= c_GeneratedPagesFrom,
        } for part in outline.parts],
        'pages': [{
            'id': page.id,
            'title': page.title,
            'kind': page.kind_word,
            'size': page.size,
            'tracks': letters(page.tracks),
            'needs': page.needs_text,
            'part': page.part.slug,
            'block': page.block if page.part.slug == 'make' else None,
            'mark': page.mark,
            'markSection': page.mark_section,
            'wave': page.wave,
            'level': level(outline, page),
            'row': 'plan/%s:%d' % (page.file, page.line),
        } for page in outline.pages],
        'tracks': {letter: [dict({'id': page_id}, **({'sideStep': True} if side_step else {}))
                            for page_id, side_step, _ in outline.tracks[letter]] for letter in c_TrackLetters},
    }


def print_counts(outline, write):
    """--counts: pages per part, block, kind, size, track and wave, the marked pages and the total."""
    def table(title, rows):
        write(title)
        width = max(len(str(label)) for label, _ in rows) if rows else 0
        for label, value in rows:
            write('  %s  %s' % (str(label).ljust(width), value))

    table('Pages per part:', [('%2d %s' % (part.number, part.slug), len(part.pages)) for part in outline.parts])
    make = next((part for part in outline.parts if part.slug == 'make'), None)
    if make is not None:
        blocks = {}
        for page in make.pages:
            blocks[page.block] = blocks.get(page.block, 0) + 1
        table('Pages per block of make:', [('block %s' % block, count)
                                           for block, count in sorted(blocks.items(), key=lambda item: str(item[0]))])
    table('Pages per kind:', [('%s %s' % (kind, name), sum(1 for page in outline.pages if page.kind == kind))
                              for kind, name in c_Kinds.items()])
    table('Pages per size:', [(size, sum(1 for page in outline.pages if page.size == size)) for size in c_Sizes])
    rows = []
    for letter in c_TrackLetters:
        side_steps = sum(1 for _, side_step, _ in outline.tracks[letter] if side_step)
        count = sum(1 for page in outline.pages if letter in page.tracks)
        rows.append((letter, '%d' % count + (' (and %d side steps)' % side_steps if side_steps else '')))
    rows.append(('on no track', sum(1 for page in outline.pages if not page.tracks)))
    table('Pages per track:', rows)
    table('Pages per writing wave:', [('%s (%s)' % (name, description),
                                       sum(1 for page in outline.pages if page.wave == name))
                                      for name, description, _ in outline.book.waves])
    generated = [part.slug for part in outline.parts if len(part.pages) >= c_GeneratedPagesFrom]
    write('Parts with generated <part>/index and <part>/review pages (%d or more rows): %d: %s'
          % (c_GeneratedPagesFrom, len(generated), ', '.join(generated)))
    for mark in ('W8', 'W8r'):
        marked = [page for page in outline.pages if page.mark == mark]
        write('%s pages: %d' % (mark, len(marked)))
        for page in marked:
            section = ' (%s)' % page.mark_section if page.mark_section else ''
            write('  %s%s' % (page.id, section))
    write('Total pages: %d' % len(outline.pages))


def print_words(outline, write):
    """--words: the estimated words per part and track."""
    write('Estimated words (S 1,500, M 3,000, L 5,000, XL 8,000):')
    width = max(len(part.slug) for part in outline.parts) + 3 if outline.parts else 3
    for part in outline.parts:
        words = sum(c_Words.get(page.size, 0) for page in part.pages)
        write('  %s  %9s' % (('%2d %s' % (part.number, part.slug)).ljust(width), format(words, ',')))
    for letter in c_TrackLetters:
        words = sum(c_Words.get(page.size, 0) for page in outline.pages if letter in page.tracks)
        write('  %s  %9s' % (('track %s' % letter).ljust(width), format(words, ',')))
    write('  %s  %9s' % ('total'.ljust(width), format(sum(c_Words.get(page.size, 0) for page in outline.pages), ',')))


def print_waves(outline, write):
    """--waves: the pages of every writing wave."""
    for name, description, _ in outline.book.waves:
        pages = [page for page in outline.pages if page.wave == name]
        words = sum(c_Words.get(page.size, 0) for page in pages)
        write('Wave %s (%s): %d pages, %s words' % (name, description, len(pages), format(words, ',')))
        for page in pages:
            write('  %s' % page.id)
