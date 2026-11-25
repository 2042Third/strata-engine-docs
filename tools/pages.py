#!/usr/bin/env python3
"""Check 1 of the book without building it: the pages' front matter (plan/style.md §6.1), the outline rules O1 to O9
on the pages and the sidebar, the page shape rules P1 to P4 (plan/site.md, "Front matter and the teaching checks"),
the glossary (plan/pipelines.md §9) and the outline's data file. A tutorial's file, downloads and stamps are
tools/tutorials.py check's (plan/pipelines.md §6.3).

    python -I tools/pages.py check [--release] [--root <book>] [--plan <folder>] [--glossary <file>] [--quiet]
    python -I tools/pages.py outline [--write | --check] [--root <book>] [--plan <folder>]

check    Every page under src/content/docs/ against its row of the outline (plan/outline-*.md, read and checked by
         tools/booklib/outline.py, the module plan/check_outline.py runs), src/sidebar.json against plan/tracks.md,
         the shape of each page's body for its kind, and src/content/glossary.json. An answer's solution="…" names a
         sketch of the page (sketches/<part>-<chapter>-<name>.<ext>) that the answer shows in a sketch= fence and
         then its ```text output-of= fence, or a worked solution of the page's own tutorials/<page id>/ folder,
         exercise-<n>.tutorial.json or exercise-<n>.patch, which exists, with its download under
         public/downloads/solutions/<page id>/ (style.md §8). A ::checkpoint stands only on a tutorial page, and the
         next block is its picture, ::figure{id=…} (style.md §7.4). In a draft, what is not written yet (a page an
         outline row promises, a Need's page, a part's index and review pages, a glossary home, a solution's
         download) is a note; --release makes these errors.
outline  Prints the outline as data (.tools/handover/outline-format.md); --write writes src/generated/outline.json,
         which the build reads; --check fails when that file is not what the outline gives today.

Every message names the file and its line and says what to do. The build makes the checks one page can make in its
strips plugin (src/plugins/strips.mjs); this tool gives the answer in seconds, and CI runs it first.

Only the standard library is used. Exit codes: 0 when all is well, 1 when problems were found, 2 for usage errors.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import blocks, frontmatter, markdown, outline as outline_rules, repo  # noqa: E402

c_Statuses = ('draft', 'reviewed', 'final')
c_Generated = ('index', 'review')
c_LearnId = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
c_Release = re.compile(r'^(\d+)\.(\d+)\.(\d+)$')
c_MaxDescription = 160
# style.md §6.1: a learn line starts with an observable verb, never with one of c_UnobservableVerbs.
c_ObservableVerbs = ('explain', 'compute', 'name', 'choose', 'write', 'build', 'find', 'predict', 'change', 'add', 'fix',
                     'trace', 'measure', 'compare', 'draw', 'export', 'create', 'run', 'set')
c_UnobservableVerbs = ('understand', 'know', 'learn', 'be familiar with')
# The book's front matter keys (style.md §6.1, §7.7) and the Starlight keys a page may set for its display.
c_BookKeys = ('id', 'title', 'description', 'kind', 'size', 'tracks', 'needs', 'time', 'learn', 'since', 'status')
c_PartPageKeys = ('id', 'title', 'description', 'tracks', 'status', 'generated')
c_StarlightKeys = ('template', 'hero', 'tableOfContents', 'pagefind', 'sidebar', 'banner', 'lastUpdated', 'editUrl')
# Keys that would let a page leave the book's rules: its URL, its navigation, its head (site.md, "The base path").
c_RefusedKeys = {
    'slug': 'the id is the file\'s path; rename the file instead',
    'draft': 'the book writes "status: draft"',
    'prev': 'previous and next follow the tracks',
    'next': 'previous and next follow the tracks',
    'head': 'pages set no head (site.md, "The base path", rule 4)',
    'level': 'the level is computed from the Needs closure (style.md §6.2)',
    'engine': 'the engine release comes from engine.pin (style.md §6.2)',
    'prerequisites': 'the key is "needs" (style.md §6.1)',
}
# style.md §6.3: the section the body ends with, and the bottom strip, per kind.
c_StripOfConcept = ['Summary', 'Check yourself', 'Exercises', 'Where it lives in Strata', 'Further reading']
c_Strips = {
    'primer': ['Summary', 'Check yourself', 'Practice', 'Where the book uses it', 'Further reading'],
    'concept': c_StripOfConcept,
    'internals': c_StripOfConcept,
    'tutorial': c_StripOfConcept,
    'how-to': c_StripOfConcept,
    'reference': ['Where it lives in Strata'],
}
c_BodyEnds = {'primer': 'Common mistakes', 'concept': 'Common mistakes', 'how-to': 'Variations'}
# style.md §7: the exact headings of the body of each kind, in their order (those written in backticks there).
c_BodyHeadings = {
    'primer': ['Why you will need this', 'Common mistakes'],
    'concept': ['Common mistakes'],
    'internals': ['The problem and how engines solve it', 'Alternatives Strata did not choose', 'How it is tested',
                  'Changing it safely'],
    'tutorial': ['What you will make', 'What you need'],
    'how-to': ['Result', 'Variations'],
}
c_FirstHeading = {'primer': 'Why you will need this', 'tutorial': 'What you will make'}
# style.md §6.3 and §8: how many items each section of the strip holds.
c_Counts = {'Check yourself': (3, 6), 'Exercises': (1, 4), 'Practice': (3, 8)}
c_AnsweredSections = ('Check yourself', 'Exercises', 'Practice')
c_MinBookUses = 3
c_TestOutQuestions = 5
c_MinQuotes = 3
# What an answer's solution="…" names (style.md §8, as src/plugins/answers.mjs reads it), and a checkpoint with the
# picture that follows it (style.md §7.4, as src/plugins/checkpoint.mjs reads it).
c_SketchFile = re.compile(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9]+(\.[A-Za-z0-9]+)?$')
c_ExerciseSolution = re.compile(r'^tutorials/(?P<page>.+)/exercise-(?P<number>[1-9][0-9]*)\.(?P<kind>tutorial\.json|patch)$')
c_CheckpointLine = re.compile(r'^\s*::checkpoint(?:\{[^}]*\})?\s*$')
c_FigureLine = re.compile(r'^\s*:{2,}(?P<name>figure|compare)(?:\[[^\]]*\])?(?:\{(?P<attributes>[^}]*)\})?\s*$')
# Parts whose concept, internals, tutorial and how-to pages carry `since` (style.md §6.1: parts 1 and 3 to 21).
c_SinceParts = ((1, 1), (3, 21))
c_SinceKinds = ('concept', 'internals', 'tutorial', 'how-to')
c_FirstRelease = '0.3.0'
c_SidebarTracks = {'game': 'G', 'beginner': 'B', 'engine': 'E'}
c_GlossaryKeys = ('id', 'term', 'definition', 'home', 'use', 'aliases', 'avoid', 'known')
c_OutlineData = 'src/generated/outline.json'


class Report:
    """Errors and notes, each (where, message); `where` is "<file>:<line>"."""

    def __init__(self, release):
        self.release = release
        self.errors = []
        self.notes = []

    def error(self, where, message):
        self.errors.append((where, message))

    def pending(self, where, message):
        """Something not written yet: a note in a draft, an error in a release."""
        (self.errors if self.release else self.notes).append((where, message))


def quoted_value_lines(text):
    """{key: (line number, raw value)} of the top-level keys of a page's front matter, read from the file's lines."""
    lines = text.split('\n')
    found = {}
    first = 0
    while first < len(lines) and not lines[first].lstrip('\ufeff').strip():
        first += 1
    if first >= len(lines) or lines[first].lstrip('\ufeff').rstrip('\r') != '---':
        return found
    for index in range(first + 1, len(lines)):
        line = lines[index].rstrip('\r')
        if line.rstrip(' \t') == '---':
            break
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_-]*):(?:\s+(.*))?$', line)
        if match and match.group(1) not in found:
            found[match.group(1)] = (index + 1, (match.group(2) or '').strip())
    return found


def error_line(message):
    """The file's line a front matter error names ("line N: …"), or 1."""
    match = re.match(r'^line (\d+): ', message or '')
    return int(match.group(1)) if match else 1


def release_tuple(text):
    match = c_Release.match(text or '')
    return tuple(int(part) for part in match.groups()) if match else None


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def needs_of(value):
    """The Needs of a front matter `needs` list as lists of alternatives, or None when it is not a list of strings."""
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        return None
    return [item.split('|') for item in value]


class BookPage:
    """A page file: its id (its path without .md), its Starlight id, its front matter and its text."""

    def __init__(self, layout, path):
        self.path = path
        self.relative = layout.relative(path)
        relative = os.path.relpath(path, layout.docs).replace(os.sep, '/')
        self.id = relative[:-3]
        self.slug = repo.page_id(relative)
        self.text = repo.read_text(path)
        self.data, self.body, self.body_line, self.error = frontmatter.read(self.text)
        self.values = quoted_value_lines(self.text)
        self.part_page = (self.id.count('/') == 1 and self.id.split('/')[1] in c_Generated)
        self.special = self.id in ('index', '404')

    def at(self, line=1):
        return '%s:%d' % (self.relative, line)

    def key_at(self, key):
        """The file's line of a front matter key (the first line of the front matter when the key is absent), as a
        Where that also names the key (tools/lint.py reports the message under the key's rule)."""
        if key in self.values:
            return Where(self.at(self.values[key][0]), key)
        return Where(self.at(min((line for line, _ in self.values.values()), default=2) - 1 if self.values else 1), key)


class Where(str):
    """A "<file>:<line>" that names the front matter key a message is about."""

    def __new__(cls, text, key):
        where = super().__new__(cls, text)
        where.key = key
        return where


def check_quoting(page, report):
    """rulings 5, R17: `title` and `description` are always written in double quotes."""
    for key in ('title', 'description'):
        if key not in page.values:
            continue
        _, raw = page.values[key]
        value = frontmatter.strip_comment(raw, 0)
        if not (len(value) >= 2 and value.startswith('"') and value.endswith('"')):
            parsed = page.data.get(key) if page.data else None
            shown = parsed if isinstance(parsed, str) else value.strip('\'"')
            report.error(page.key_at(key), '"%s" is not written in double quotes: write %s: %s (rulings 5, R17: a bare '
                         'value holding ": " is not valid YAML)' % (key, key, json.dumps(shown, ensure_ascii=False)))


def check_keys(page, allowed, report):
    for key in page.data:
        if key in c_RefusedKeys:
            report.error(page.key_at(key), 'the key "%s" is not part of the book\'s front matter: %s' % (key, c_RefusedKeys[key]))
        elif key not in allowed and key not in c_StarlightKeys:
            report.error(page.key_at(key), 'unknown front matter key "%s": the keys are %s (style.md §6.1); fix its spelling or '
                         'remove it' % (key, ', '.join(allowed)))


def check_text_keys(page, report):
    data = page.data
    for key in ('title', 'description'):
        if not isinstance(data.get(key), str) or not data[key].strip():
            report.error(page.key_at(key), '"%s" is missing: write %s: "…" in double quotes' % (key, key))
    description = data.get('description')
    if isinstance(description, str) and description.strip():
        if len(description) > c_MaxDescription:
            report.error(page.key_at('description'), '"description" has %d characters: shorten it to one sentence of at most %d'
                         % (len(description), c_MaxDescription))
        if re.search(r'[.?!]\s+\S', description.strip()) or not re.search(r'[.?!]$', description.strip()):
            report.error(page.key_at('description'), '"description" is one sentence that ends with ".", "?" or "!" '
                         '(style.md §6.1): join or cut its sentences')


def check_learn(page, report):
    learn = page.data.get('learn')
    where = page.key_at('learn')
    if not isinstance(learn, list) or not 2 <= len(learn) <= 5:
        report.error(where, '"learn" holds two to five objectives, each "- id: <id>" with "text: <what the reader can do>" '
                     'below it (style.md §6.1)')
        return []
    ids = []
    for number, item in enumerate(learn, start=1):
        if not isinstance(item, dict) or set(item) != {'id', 'text'}:
            report.error(where, 'learn line %d is not {id, text}: write "- id: <lowercase-words>" and "  text: <objective>"' % number)
            continue
        learn_id, text = item['id'], item['text']
        if not isinstance(learn_id, str) or not c_LearnId.match(learn_id):
            report.error(where, 'learn line %d: the id %r is not lowercase words joined by "-"' % (number, learn_id))
        elif learn_id in ids:
            report.error(where, 'learn line %d: the id "%s" is used twice: give each objective its own id' % (number, learn_id))
        else:
            ids.append(learn_id)
        if not isinstance(text, str) or not text.strip():
            report.error(where, 'learn line %d has no text: say what the reader can do afterwards' % number)
            continue
        words = text.strip().lower()
        first = re.match(r'[a-z]*', words).group(0)
        never = next((verb for verb in c_UnobservableVerbs if words == verb or words.startswith(verb + ' ')), None)
        if never:
            report.error(where, 'learn line %d starts with "%s", which no one can observe: start with a verb such as %s'
                         % (number, never, ', '.join(c_ObservableVerbs[:6])))
        elif first not in c_ObservableVerbs:
            report.error(where, 'learn line %d starts with "%s": start it with an observable verb (%s)'
                         % (number, first or words[:10], ', '.join(c_ObservableVerbs)))
    return ids


def check_book_page(page, row, outline, pin, report):
    """style.md §6.1 and rule O7 for a page that is a row of the outline."""
    data = page.data
    check_keys(page, c_BookKeys, report)
    check_text_keys(page, report)
    if data.get('id') != page.id:
        report.error(page.key_at('id'), '"id" must be the file\'s path under src/content/docs/ without .md: write id: %s' % page.id)
    kind = data.get('kind')
    if kind not in outline_rules.c_KindLetters:
        report.error(page.key_at('kind'), '"kind" must be one of %s' % ', '.join(outline_rules.c_KindLetters))
    if data.get('size') not in outline_rules.c_Sizes:
        report.error(page.key_at('size'), '"size" must be one of %s' % ', '.join(outline_rules.c_Sizes))
    tracks = data.get('tracks')
    if not isinstance(tracks, list) or any(track not in outline_rules.c_TrackLetters for track in tracks):
        report.error(page.key_at('tracks'), '"tracks" is a list of the letters G, B and E ([] for a page on no track)')
        tracks = None
    elif len(set(tracks)) != len(tracks):
        report.error(page.key_at('tracks'), '"tracks" names a track twice: name each once')
    needs = needs_of(data.get('needs'))
    if needs is None:
        report.error(page.key_at('needs'), '"needs" is a list of page ids, "a|b" for alternatives ([] for none)')
    else:
        for need in needs:
            for alternative in need:
                if not outline_rules.c_PageIdPattern.match(alternative):
                    report.error(page.key_at('needs'), 'the Need "%s" is not a page id: write <part>/<chapter>, alternatives '
                                 'joined by "|" without spaces' % '|'.join(need))
        count = sum(len(need) for need in needs)
        if count > outline_rules.c_MaxNeedIds:
            report.error(page.key_at('needs'), 'O3: the Needs name %d page ids (alternatives included), more than %d: '
                         'leave out what an earlier Need already needs' % (count, outline_rules.c_MaxNeedIds))
    if data.get('status') not in c_Statuses:
        report.error(page.key_at('status'), '"status" must be one of %s' % ', '.join(c_Statuses))
    elif report.release and data['status'] == 'draft':
        report.error(page.key_at('status'), 'a release has no draft pages (site.md, "Where the site is served"): finish the '
                     'page\'s review (process.md)')
    learn_ids = []
    if kind == 'reference':
        for key in ('time', 'learn'):
            if key in data:
                report.error(page.key_at(key), '"%s" is absent on reference pages (style.md §7.6): remove it' % key)
    elif kind in outline_rules.c_KindLetters:
        if not is_int(data.get('time')) or data['time'] < 1:
            report.error(page.key_at('time'), '"time" is the whole minutes the page takes, such as time: 45')
        learn_ids = check_learn(page, report)
    check_since(page, row, kind, pin, report)
    if row is not None:
        check_against_row(page, row, needs, tracks, report)
    return needs, tracks, learn_ids


def check_since(page, row, kind, pin, report):
    if row is None:
        return  # O7 reports a page that is no row; where `since` belongs depends on the row's part
    since = page.data.get('since')
    number = row.part.number
    wanted = kind in c_SinceKinds and any(low <= number <= high for low, high in c_SinceParts)
    if 'since' not in page.data:
        if wanted:
            report.error(page.key_at('since'), '"since" is missing: write the first release whose engine had the page\'s '
                         'subject, such as since: 0.3.0 (style.md §6.1)')
        return
    if not wanted:
        report.error(page.key_at('since'), '"since" is written only on concept, internals, tutorial and how-to pages of '
                     'parts 1 and 3 to 21 (style.md §6.1): remove it')
        return
    value = release_tuple(since if isinstance(since, str) else None)
    if value is None:
        report.error(page.key_at('since'), '"since" is a release written X.Y.Z, such as since: 0.3.0')
    elif value < release_tuple(c_FirstRelease):
        report.error(page.key_at('since'), '"since" is %s or later: the book counts anything older than the first tag '
                     'as %s' % (c_FirstRelease, c_FirstRelease))
    elif release_tuple(pin.get('release')) and value > release_tuple(pin.get('release')):
        report.error(page.key_at('since'), '"since" %s is later than the book\'s release %s (engine.pin)'
                     % (since, pin.get('release')))


def check_against_row(page, row, needs, tracks, report):
    """O7: the front matter equals the page's row of the outline."""
    data = page.data
    source = 'its row (plan/%s:%d)' % (row.file, row.line)
    if data.get('title') != row.title:
        report.error(page.key_at('title'), 'O7: the title differs from %s: write title: %s' % (source, json.dumps(row.title, ensure_ascii=False)))
    if data.get('kind') != row.kind_word:
        report.error(page.key_at('kind'), 'O7: the kind differs from %s: write kind: %s' % (source, row.kind_word))
    if data.get('size') != row.size:
        report.error(page.key_at('size'), 'O7: the size differs from %s: write size: %s' % (source, row.size))
    if tracks is not None and set(tracks) != set(row.tracks):
        report.error(page.key_at('tracks'), 'O7: the tracks differ from %s: write tracks: [%s]' % (source, ', '.join(
            letter for letter in outline_rules.c_TrackLetters if letter in row.tracks)))
    if needs is not None and needs != row.needs:
        report.error(page.key_at('needs'), 'O7: the Needs differ from %s: write needs: [%s]' % (source, ', '.join(row.needs_text)))


def check_part_page(page, outline, report):
    data = page.data
    check_keys(page, c_PartPageKeys, report)
    check_text_keys(page, report)
    slug, last = page.id.split('/')
    if data.get('id') != page.id:
        report.error(page.key_at('id'), '"id" must be the file\'s path under src/content/docs/ without .md: write id: %s' % page.id)
    if data.get('generated') != last:
        report.error(page.key_at('generated'), 'a part page carries generated: %s (style.md §7.7)' % last)
    part = next((part for part in outline.parts if part.slug == slug), None)
    if part is None:
        report.error(page.at(), 'O1: "%s" is no part of the outline: part pages belong to a part (plan/outline-*.md)' % slug)
        return
    if len(part.pages) < outline_rules.c_GeneratedPagesFrom:
        report.error(page.at(), 'O8: part "%s" has %d rows, fewer than %d, so it has no %s page (style.md §7.7): remove the '
                     'file' % (slug, len(part.pages), outline_rules.c_GeneratedPagesFrom, last))
    letters = [letter for letter in outline_rules.c_TrackLetters if any(letter in row.tracks for row in part.pages)]
    tracks = data.get('tracks')
    if not isinstance(tracks, list) or set(tracks) != set(letters) or len(set(tracks)) != len(tracks):
        report.error(page.key_at('tracks'), 'a part page carries its part\'s tracks: write tracks: [%s]' % ', '.join(letters))
    if data.get('status') not in c_Statuses:
        report.error(page.key_at('status'), '"status" must be one of %s' % ', '.join(c_Statuses))
    elif report.release and data['status'] == 'draft':
        report.error(page.key_at('status'), 'a release has no draft pages (site.md, "Where the site is served"): finish the '
                     'part\'s edit pass (process.md)')


def check_special_page(page, report):
    """index.md (the landing page) and 404.md carry only title and description of the book's keys."""
    check_keys(page, ('title', 'description'), report)
    check_text_keys(page, report)


def with_article(kind):
    return ('an ' if kind[:1] in 'aeiou' else 'a ') + kind


def check_shape(page, kind, learn_ids, outline, report):
    """P1 to P4 (site.md, "Page shape"; style.md §6.3, §7 and §8) on the page's body."""
    body = blocks.Page(page.text)
    for directive in body.unclosed:
        report.error(page.at(directive.line), 'the directive %s%s is never closed: end it with a line of %s'
                     % (directive.marker, directive.name, directive.marker))
    titles = [section.title for section in body.sections]
    strip = c_Strips[kind]
    # P1: the bottom strip, and the section before it.
    if titles[-len(strip):] != strip:
        at = body.sections[-1].line if body.sections else 1
        report.error(page.at(at), 'P1: %s page ends with the sections %s, in this order (style.md §6.3); its last sections '
                     'are %s' % (with_article(kind), ', '.join('"## %s"' % title for title in strip),
                                 ', '.join('"## %s"' % title for title in titles[-len(strip):]) or 'none'))
    else:
        before = titles[:-len(strip)]
        last = before[-1] if before else None
        at = page.at(body.sections[len(before) - 1].line if before else body.sections[0].line)
        if kind == 'internals':
            if not (last == 'Changing it safely' or (last == 'What went wrong before' and before[-2:-1] == ['Changing it safely'])):
                report.error(at, 'P1: the body of an internals page ends with "## Changing it safely", followed by "## What went '
                             'wrong before" when the history has one, before the bottom strip (style.md §6.3)')
        elif kind in c_BodyEnds:
            if last != c_BodyEnds[kind]:
                report.error(at, 'P1: the body of a %s page ends with "## %s" before the bottom strip (style.md §6.3)'
                             % (kind, c_BodyEnds[kind]))
        elif kind == 'tutorial' and before[-1:] in (['What you need'], ['What you will make'], []):
            report.error(at, 'P1: a tutorial has its step sections after "## What you need" and before the bottom strip '
                         '(style.md §7.4)')
    # P1: the exact headings of the body (style.md §7), in order.
    wanted = c_BodyHeadings.get(kind, [])
    positions = [titles.index(title) if title in titles else None for title in wanted]
    for title, position in zip(wanted, positions):
        if position is None:
            report.error(page.at(body.sections[0].line if body.sections else 1), 'P1: %s page has the section "## %s" '
                         '(style.md §7): add it' % (with_article(kind), title))
    present = [position for position in positions if position is not None]
    if present != sorted(present):
        report.error(page.at(body.sections[0].line if body.sections else 1), 'P1: the sections %s stand in this order on %s '
                     'page (style.md §7)' % (', '.join('"## %s"' % title for title in wanted), with_article(kind)))
    first = c_FirstHeading.get(kind)
    if first and titles and titles[0] != first:
        report.error(page.at(body.sections[0].line), 'P1: the first section of %s page is "## %s" (style.md §7)' % (with_article(kind), first))
    # P1: the counts of the strip.
    summary = body.section('Summary')
    if summary is not None and kind != 'reference':
        count = len(blocks.items(summary.lines, 0, ordered=False))
        if count != len(learn_ids):
            report.error(page.at(summary.line), 'P1: "## Summary" holds %d items; it holds one bulleted item per learn line '
                         '(%d), in their order (style.md §6.3)' % (count, len(learn_ids)))
    tested = set()
    checked = set()  # the lines of the answers whose tests the strip's sections checked
    for title in c_AnsweredSections:
        section = body.section(title)
        if section is None:
            continue
        questions = blocks.items(section.lines, 0)
        low, high = c_Counts[title]
        if not low <= len(questions) <= high:
            report.error(page.at(section.line), 'P1: "## %s" holds %d numbered items; it holds %d to %d (style.md §8)'
                         % (title, len(questions), low, high))
        for item, rest in questions:
            answers = blocks.answers_in(rest)
            if not answers:
                report.error(page.at(item.number), 'every question and exercise is followed by an :::answer (style.md §8): '
                             'add one')
                continue
            for line, attributes in answers:
                checked.add(line.number)
                if 'tests' not in attributes:
                    report.error(page.at(line.number), 'P2: an answer in "## %s" carries tests="<learn ids>", the objectives it '
                                 'tests (style.md §8)' % title)
                ids = blocks.split_ids(attributes.get('tests'))
                for learn_id in ids:
                    if learn_id not in learn_ids:
                        report.error(page.at(line.number), 'P2: tests names "%s", which is no learn id of the page (%s)'
                                     % (learn_id, ', '.join(learn_ids) or 'none'))
                if title == 'Check yourself':
                    tested.update(ids)
    if kind != 'reference':
        check_yourself = body.section('Check yourself')
        for learn_id in learn_ids:
            if learn_id not in tested:
                report.error(page.at(check_yourself.line if check_yourself else page.values.get('learn', (1,))[0]),
                             'P2: the learn id "%s" is in the tests of no "Check yourself" answer: add a question that tests '
                             'it' % learn_id)
    for directive in body.directives:
        if directive.name != 'answer':
            continue
        for name in directive.attributes:
            if name not in ('tests', 'solution'):
                report.error(page.at(directive.line), 'an :::answer carries only tests="<learn ids>" and solution="<file>" '
                             '(site.md, "Directives"): remove %s' % name)
    # The tests of the other answers (the Test out box, the body) name learn ids too.
    for directive in body.directives:
        if directive.name == 'answer' and 'tests' in directive.attributes and directive.line not in checked:
            for learn_id in blocks.split_ids(directive.attributes['tests']):
                if learn_id not in learn_ids:
                    report.error(page.at(directive.line), 'P2: tests names "%s", which is no learn id of the page (%s)'
                                 % (learn_id, ', '.join(learn_ids) or 'none'))
    if kind == 'primer':
        check_test_out(page, body, learn_ids, report)
        check_book_uses(page, body, outline, report)
    elif any(directive.name == 'test-out' for directive in body.directives):
        first = next(directive for directive in body.directives if directive.name == 'test-out')
        report.error(page.at(first.line), 'the Test out box stands only on primers (style.md §12): remove it')
    if kind == 'internals':
        quotes = [fence for fence in markdown.fences(page.text) if 'src' in fence.attributes
                  and not fence.attributes['src'].startswith(('book:', 'vendor:'))]
        if len(quotes) < c_MinQuotes:
            report.error(page.at(body.sections[0].line if body.sections else 1), 'P4: an internals page quotes the engine at '
                         'least %d times (src="<engine path>#L<a>-L<b>"); this one quotes it %d times' % (c_MinQuotes, len(quotes)))


def check_test_out(page, body, learn_ids, report):
    """P3: a primer opens with its Test out box, before any heading."""
    boxes = [directive for directive in body.directives if directive.name == 'test-out']
    first_heading = body.headings[0][2] if body.headings else None
    first_text = next((line for line in body.lines if line.stripped and not line.stripped.startswith('<!--')), None)
    if not boxes:
        report.error(page.at(first_text.number if first_text else page.body_line), 'P3: a primer opens with its Test out box '
                     '(::::test-out holding five questions, each with an :::answer{tests="…"}) before any heading')
        return
    box = boxes[0]
    if len(boxes) > 1:
        report.error(page.at(boxes[1].line), 'P3: a primer has one Test out box: remove this one')
    if box.depth != 0 or (first_heading is not None and box.line > first_heading) or (first_text and first_text.number != box.line):
        report.error(page.at(box.line), 'P3: the Test out box is the first thing of the page, before any heading and any text')
    inside = [line for line in body.lines if box in line.containers]
    questions = blocks.items(inside, box.depth + 1)
    if len(questions) != c_TestOutQuestions:
        report.error(page.at(box.line), 'P3: the Test out box holds %d numbered questions; it holds exactly %d'
                     % (len(questions), c_TestOutQuestions))
    covered = set()
    for item, rest in questions:
        answers = [(line, attributes) for line, attributes in blocks.answers_in(rest)]
        if not answers:
            report.error(page.at(item.number), 'P3: each Test out question is followed by an :::answer{tests="…"}: add one')
            continue
        line, attributes = answers[0]
        if 'tests' not in attributes:
            report.error(page.at(line.number), 'P3: the answer carries tests="<learn ids>", the objectives the question tests')
        covered.update(blocks.split_ids(attributes.get('tests')))
    for learn_id in learn_ids:
        if learn_id not in covered:
            report.error(page.at(box.line), 'P3: the Test out answers\' tests do not cover the learn id "%s": a reader who passes '
                         'the box must know everything the page teaches' % learn_id)


def link_target(page_id, target):
    """The page id a relative link to a .md file names, or None."""
    path = target.split('#', 1)[0]
    if not path.endswith('.md') or path.startswith('/') or '://' in path:
        return None
    folder = page_id.rsplit('/', 1)[0] if '/' in page_id else ''
    parts = [part for part in (folder + '/' + path).split('/') if part not in ('', '.')]
    resolved = []
    for part in parts:
        if part == '..':
            if not resolved:
                return None
            resolved.pop()
        else:
            resolved.append(part)
    return '/'.join(resolved)[:-3]


def check_book_uses(page, body, outline, report):
    """style.md §6.3: "Where the book uses it" links at least three pages whose Needs closure holds the primer."""
    section = body.section('Where the book uses it')
    if section is None:
        return
    targets = []
    for line, target in blocks.links(section.lines):
        linked = link_target(page.id, target)
        if linked is not None and linked not in [item for _, item in targets]:
            targets.append((line, linked))
    if len(targets) < c_MinBookUses:
        report.error(page.at(section.line), '"## Where the book uses it" links %d pages; it links at least %d, each with one '
                     'sentence on what it uses (style.md §6.3)' % (len(targets), c_MinBookUses))
    for line, linked in targets:
        if linked not in outline.by_id:
            report.error(page.at(line.number), 'the link to %s names no row of the outline: link a page of the book' % linked)
        elif page.id not in outline_rules.closure(outline, linked):
            report.error(page.at(line.number), '%s does not have %s in its Needs closure, so it does not use what the primer '
                         'teaches (style.md §6.3): link a page that does' % (linked, page.id))


def build_end(page, body, directive):
    """The line that ends a container as the site's reader (remark-directive) ends it: a closing line of colons that
    ends a container nested in it ends this one too when it has at least as many colons as this one's opening, so an
    answer opened with ::: ends where a :::question inside it ends (the outer container needs more colons: ::::answer)."""
    lines = page.text.split('\n')
    end = directive.close_line or len(lines)
    for other in body.directives:
        if directive.line < other.line < end and other.close_line is not None and other.close_line < end:
            closing = blocks.c_ContainerClose.match(lines[other.close_line - 1].strip())
            if closing and len(closing.group('marker')) >= len(directive.marker):
                end = other.close_line
    return end


def solution_forms(page_id):
    return ('a sketch the answer shows with its output (solution="sketches/%s-<name>.cpp"), an editor exercise '
            '(solution="tutorials/%s/exercise-<n>.tutorial.json") or an engine exercise (solution="tutorials/%s/exercise-<n>.patch")'
            % (page_id.replace('/', '-'), page_id, page_id))


def check_solutions(layout, page, body, report):
    """style.md §8: a worked solution's file, as the build reads solution="…" (src/plugins/answers.mjs). A sketch is
    shown in the answer in full, with its output; an exercise's file is its own page's and exists, and the reader gets
    its download (plan/pipelines.md §6.3, compile), which a draft may still lack and a release may not."""
    fences = markdown.fences(page.text)
    for fence in fences:
        if 'solution' in fence.attributes:
            report.error(page.at(fence.open_line), 'a code fence has no attribute "solution" (src/plugins/excerpts.mjs): a worked '
                         'solution is named by its answer, :::answer{solution="sketches/%s-<name>.cpp"}, which shows the sketch '
                         'fence and its output; remove solution= from the fence' % page.id.replace('/', '-'))
    for directive in body.directives:
        if directive.name != 'answer' or 'solution' not in directive.attributes:
            continue
        value = directive.attributes['solution'].strip()
        where = page.at(directive.line)
        if not value:
            report.error(where, 'solution="" names no file: name the solution\'s file, or remove it')
            continue
        if value.startswith('sketches/'):
            name = value[len('sketches/'):]
            prefix = page.id.replace('/', '-') + '-'
            if not c_SketchFile.match(name):
                report.error(where, 'solution="%s" must name a file of sketches/ with its extension, such as sketches/%stoy.cpp' % (value, prefix))
                continue
            if not name.startswith(prefix):
                report.error(where, 'solution="%s": a sketch\'s file name starts with its page\'s id, sketches/%s<name>.<extension> '
                             '(plan/pipelines.md §4)' % (value, prefix))
                continue
            end = build_end(page, body, directive)
            inside = [fence for fence in fences if directive.line < fence.open_line < end]
            shown = [fence.open_line for fence in inside if fence.attributes.get('sketch') == name]
            output = [fence.open_line for fence in inside if fence.attributes.get('output-of') == name and fence.lang == 'text']
            if not shown or not any(line > shown[0] for line in output):
                report.error(where, 'solution="%s": the answer shows the sketch in full, with its output: a fence with sketch="%s", then '
                             'its ```text output-of="%s" fence (style.md §8)' % (value, name, name))
            continue
        exercise = c_ExerciseSolution.match(value)
        if exercise is None:
            report.error(where, 'solution="%s" names the file of a worked solution: %s (style.md §8)' % (value, solution_forms(page.id)))
            continue
        if exercise.group('page') != page.id:
            report.error(where, 'solution="%s": the solution of an exercise is a file of its own page, tutorials/%s/exercise-<n>.%s'
                         % (value, page.id, exercise.group('kind')))
            continue
        if not os.path.isfile(os.path.join(layout.root, *value.split('/'))):
            report.error(where, 'solution="%s": %s does not exist: write the worked solution (plan/pipelines.md §6.2), or name the '
                         'file the answer works through' % (value, value))
            continue
        download = 'public/downloads/solutions/%s/exercise-%s.%s' % (page.id, exercise.group('number'),
                                                                      'patch' if exercise.group('kind') == 'patch' else 'zip')
        if not os.path.isfile(os.path.join(layout.root, *download.split('/'))):
            report.pending(where, 'solution="%s": its download %s is not written yet: run python -I tools/tutorials.py compile'
                           % (value, download))


def check_checkpoints(page, kind, report):
    """style.md §7.4: a ::checkpoint{stage=N} ends a step section of a tutorial, and the next block is its picture,
    headed "You should now have": one ::figure{id=…}, not a ::compare slider (src/plugins/checkpoint.mjs). Its stage
    against the tutorial file is tools/tutorials.py check's."""
    lines = page.text.split('\n')
    for number, text in markdown.prose_lines(page.text):
        if not c_CheckpointLine.match(text):
            continue
        where = page.at(number)
        if kind != 'tutorial':
            report.error(where, '::checkpoint ends a step section of a tutorial (style.md §7.4), and this page\'s kind is %s: remove it'
                         % (kind or 'not given'))
            continue
        following = next(((line, lines[line - 1]) for line in range(number + 1, len(lines) + 1) if lines[line - 1].strip()), None)
        picture = c_FigureLine.match(following[1]) if following else None
        if picture is None or picture.group('name') == 'compare':
            report.error(where, 'the checkpoint is followed by its picture, headed "You should now have": write ::figure{id=…} on the '
                         'next line, a recipe of the page\'s figure manifest that shows the project at this point%s (style.md §7.4)'
                         % (', not a ::compare slider' if picture is not None else ''))
        elif not blocks.parse_attributes(picture.group('attributes')).get('id'):
            report.error(page.at(following[0]), 'the checkpoint\'s picture names its recipe: ::figure{id=<figure id>}')


# The rules below are the site build's (src/plugins/strips.mjs, tabs.mjs, links.mjs), in its words, so that a writer's
# pagecheck sees what the build would refuse.
c_TabLabels = {'how': ['In the editor', 'With a command'], 'os': ['Windows', 'Linux', 'macOS']}
c_ExampleKinds = ('primer', 'concept', 'internals')
c_CommandOnlyStep = 'This step has no menu or button'
c_CommandPages = {'G': 'make/commands', 'B': 'make/commands', 'E': 'editor/commands'}
c_CommentLine = re.compile(r'^\s*<!--.*-->\s*$')
# The container directives' text in brackets and attributes (src/lib/directives.mjs): name -> (label, attributes),
# label 'none', 'optional' or 'required'; attributes None for any.
c_Containers = {name: ('optional', ('icon',)) for name in ('note', 'tip', 'caution', 'danger')}
c_Containers.update({name: ('optional', ()) for name in ('why', 'question', 'history', 'elsewhere', 'rule', 'simplified', 'analogy',
                                                         'example', 'files')})
c_Containers.update({'derivation': ('none', ()), 'test-out': ('none', ()), 'answer': ('optional', ('tests', 'solution')),
                     'tabs': ('none', ('sync',)), 'tab': ('required', ()), 'steps': ('none', ()), 'figure': ('none', None),
                     'compare': ('none', None)})


c_ValueDirective = re.compile(r':value\{key="(?P<key>[^"]*)"\}')
c_ValuesFile = 'src/generated/reference/values.json'


def generated_values(layout):
    """The keys of src/generated/reference/values.json (tools/reference.py render), or None when it cannot be read."""
    try:
        data = json.loads(repo.read_text(os.path.join(layout.root, *c_ValuesFile.split('/'))))
    except (OSError, ValueError):
        return None
    return set(data) if isinstance(data, dict) else None


def relative_link(page_id, target):
    """The relative .md link from a page to an absolute path such as /gpu/shaders/#binding (src/plugins/links.mjs)."""
    path, _, anchor = target.partition('#')
    linked = path.strip('/')
    if not linked:
        return None
    folder = page_id.rsplit('/', 1)[0] if '/' in page_id else ''
    if folder and linked.startswith(folder + '/'):
        relative = linked[len(folder) + 1:]
    else:
        relative = ('../' * (folder.count('/') + 1) if folder else '') + linked
    return relative + '.md' + ('#' + anchor if anchor else '')


def is_patch_tutorial(layout, page_id):
    """A tutorial whose file holds a patch changes the engine: it has no project and no checkpoints."""
    try:
        data = json.loads(repo.read_text(os.path.join(layout.tutorials, *(page_id + '.tutorial.json').split('/'))))
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and bool(data.get('patch'))


def section_blocks(page, body, section):
    """The section's non-blank lines up to the next level-2 heading, code and HTML comments included, as written."""
    lines = page.text.split('\n')
    following = [other.line for other in body.sections if other.line > section.line]
    end = following[0] - 1 if following else len(lines)
    return [(number, lines[number - 1].strip()) for number in range(section.line + 1, end + 1)
            if lines[number - 1].strip() and not c_CommentLine.match(lines[number - 1])]


c_GeneralSection = 'The problem and how engines solve it'
c_GeneralShare = 1 / 5
c_ProseHeading = re.compile(r'^#{1,6}(\s|$)')
c_TableRule = re.compile(r'^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?$')
c_LineMarker = re.compile(r'^(?:>\s?|[-*+]\s+|\d+[.)]\s+)+')
c_LeafDirective = re.compile(r'^::[A-Za-z][\w-]*(?:\[[^\]]*\])?(?:\{[^}]*\})?\s*$')


def prose_words(lines, headings=False):
    """The prose words of (number, line) pairs outside fences, as the site counts them (src/plugins/strips.mjs
    proseWords, style.md §2.2): runs of characters between spaces, without headings, block math and HTML; a code span
    or an inline formula counts as one word, a link or a text directive as its text, a container directive as its
    label. With headings, the text of headings counts too (the site counts the headings inside a section)."""
    count = 0
    in_math = False
    for _, raw in lines:
        line = raw.strip()
        if line.startswith('$$'):
            in_math = not in_math and not (len(line) > 2 and line.endswith('$$'))
            continue
        if in_math or not line or line.startswith('<') or (c_ProseHeading.match(line) and not headings) or c_LeafDirective.match(line) \
                or c_TableRule.match(line):
            continue
        opening = blocks.c_ContainerOpen.match(line)
        if opening:
            line = opening.group('label') or ''
        elif blocks.c_ContainerClose.match(line):
            continue
        line = c_LineMarker.sub('', c_ProseHeading.sub('', line))
        line = re.sub(r'(`+)(.+?)\1', 'x', line)
        line = re.sub(r'\$[^$]+\$', 'x', line)
        line = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', line)
        line = re.sub(r'(?<![\w:]):[A-Za-z][\w-]*\[([^\]]*)\](?:\{[^}]*\})?', r'\1', line)
        line = re.sub(r'\[([^\]]*)\](?:\([^)]*\)|\[[^\]]*\])', r'\1', line)
        line = re.sub(r'<[^>]+>', '', line)
        count += len(line.replace('|', ' ').split())
    return count


def check_general_section(page, body, kind, report):
    """style.md §7.3, as the site's build refuses it (src/plugins/strips.mjs generalSectionProblems): the section
    "## The problem and how engines solve it" of an internals page holds at most a fifth of the page's prose words,
    its heading not counted on either side."""
    if kind != 'internals':
        return
    section = body.section(c_GeneralSection)
    if section is None:
        return
    prose = markdown.prose_lines(page.text)
    following = [other.line for other in body.sections if other.line > section.line]
    end = following[0] if following else len(page.text.split('\n')) + 1
    own = prose_words([item for item in prose if section.line < item[0] < end], headings=True)
    total = prose_words(prose)
    if own > total * c_GeneralShare:
        report.error(page.at(section.line), 'the section "## %s" holds %d of the page\'s %d prose words; it holds at most a fifth, '
                     '%d (style.md §7.3): keep it to the approaches and their costs, or link the concept page of the part that '
                     'holds them' % (c_GeneralSection, own, total, int(total * c_GeneralShare)))


def check_build_rules(layout, page, kind, outline, report):
    """What the site's build refuses and the rules above do not see: absolute links, links to no page, tab sets, a
    primer's, concept page's or internals page's worked example, a checkpoint at the end of each step section of a
    tutorial, and the page that teaches running a command in the Needs closure of a page with a command-only step."""
    body = blocks.Page(page.text)
    check_general_section(page, body, kind, report)
    for line, target in blocks.links(body.lines):
        if target.startswith('/'):
            suggestion = relative_link(page.id, target)
            report.error(page.at(line.number), '"%s" is an absolute path: link to the page\'s .md file with a relative path%s (the '
                         'base path is added by the build)' % (target, ', %s' % suggestion if suggestion else ''))
            continue
        linked = link_target(page.id, target)
        if linked is not None and linked not in outline.by_id and not os.path.isfile(os.path.join(layout.docs, *(linked + '.md').split('/'))):
            report.error(page.at(line.number), '"%s": there is no page %s.md' % (target, linked))
    values = None
    for line in body.lines:
        for match in c_ValueDirective.finditer(markdown.strip_inline_code(line.text)):
            values = generated_values(layout) if values is None else values
            if values is not None and match.group('key') not in values:
                report.error(page.at(line.number), ':value{key="%s"}: %s has no key "%s"; tools/reference.py render lists the keys it '
                             'writes' % (match.group('key'), c_ValuesFile, match.group('key')))
    for directive in body.directives:
        label, attributes = c_Containers.get(directive.name, (None, None))
        written = directive.marker + directive.name
        if label == 'none' and directive.label:
            report.error(page.at(directive.line), '%s[%s] takes no text in brackets' % (written, directive.label))
        if label == 'required' and not (directive.label or '').strip():
            report.error(page.at(directive.line), '%s needs its text in brackets: %s[…]' % (written, written))
        for name in directive.attributes if attributes is not None else ():
            if name not in attributes:
                report.error(page.at(directive.line), '%s has no attribute "%s" (%s)' % (
                    written, name, 'it takes %s' % ', '.join(attributes) if attributes else 'it takes none'))
        if directive.name == 'tab' and (directive.parent is None or directive.parent.name != 'tabs'):
            report.error(page.at(directive.line), ':::tab belongs inside ::::tabs (four colons around the set, three around each tab)')
        if directive.name != 'tabs':
            continue
        labels = [child.label for child in body.directives if child.parent is directive and child.name == 'tab']
        if len(labels) < 2:
            report.error(page.at(directive.line), 'a tab set holds at least two tabs')
        fixed = c_TabLabels.get(directive.attributes.get('sync'))
        if fixed and labels != fixed:
            report.error(page.at(directive.line), 'a tab set with sync=%s holds the tabs %s, in this order (style.md §10); this one '
                         'holds %s' % (directive.attributes['sync'], ', '.join('"%s"' % label for label in fixed),
                                       ', '.join('"%s"' % label for label in labels) or 'none'))
    if kind in c_ExampleKinds:
        strip = body.section(c_Strips[kind][0])
        if not any(directive.name == 'example' and (strip is None or directive.line < strip.line) for directive in body.directives):
            report.error(page.at(strip.line if strip else 1), 'a :::example stands before the bottom strip of %s page: a worked example '
                         'comes before the first exercise (style.md §8)' % with_article(kind))
    titles = [section.title for section in body.sections]
    if kind == 'tutorial' and 'What you need' in titles and not is_patch_tutorial(layout, page.id):
        end = titles.index('Summary') if 'Summary' in titles else len(titles)
        for section in body.sections[titles.index('What you need') + 1:end]:
            found = [text for _, text in section_blocks(page, body, section)]
            if found and (c_CheckpointLine.match(found[-1]) or (len(found) > 1 and c_FigureLine.match(found[-1])
                                                                and c_CheckpointLine.match(found[-2]))):
                continue
            report.error(page.at(section.line), 'the step section "## %s" of a tutorial ends with ::checkpoint{stage=…}, the project as '
                         'it is after its last step, and then the checkpoint\'s "You should now have" picture, ::figure{id=…} (style.md '
                         '§7.4): a section that explains goes before "## What you need", a closing note into the last step section, '
                         'before its checkpoint' % section.title)
    steps = [line for line in body.lines if blocks.c_OrderedItem.match(line.stripped)
             and blocks.c_OrderedItem.sub('', line.stripped).lstrip('*_ ').startswith(c_CommandOnlyStep)]
    tracks = page.data.get('tracks') if isinstance(page.data.get('tracks'), list) else []
    if steps and page.id in outline.by_id:
        closure = outline_rules.closure(outline, page.id)
        for needed in sorted({c_CommandPages[letter] for letter in tracks if letter in c_CommandPages}):
            if needed != page.id and needed not in closure:
                letters = [letter for letter in tracks if c_CommandPages.get(letter) == needed]
                report.error(page.at(steps[0].number), 'a step that has no menu or button runs a command, and %s, which teaches running '
                             'one, is not in the page\'s Needs closure (track%s %s; style.md §10): move the step to a later page, or start '
                             'the tutorial where its result is done' % (needed, 's' if len(letters) > 1 else '', ' and '.join(letters)))


def check_sidebar(layout, outline, pages, report):
    """O5 and O9: src/sidebar.json lists the parts in the outline's order with their titles, every written page once
    in the order of its part's rows, and the three tracks exactly as plan/tracks.md writes them (every row of a track,
    written or not; .tools/handover/outline-format.md §3)."""
    where = 'src/sidebar.json:1'
    try:
        sidebar = json.loads(repo.read_text(layout.sidebar))
    except FileNotFoundError:
        report.error(where, 'the sidebar is missing: the build reads its parts and tracks from src/sidebar.json')
        return
    except ValueError as error:
        report.error('src/sidebar.json:%d' % getattr(error, 'lineno', 1), 'not valid JSON: %s' % error)
        return
    text = repo.read_text(layout.sidebar)

    def line_of(needle):
        index = text.find(needle)
        return 'src/sidebar.json:%d' % (text.count('\n', 0, index) + 1 if index >= 0 else 1)

    existing = {page.id for page in pages if not page.special}
    parts = sidebar.get('parts') if isinstance(sidebar, dict) else None
    if not isinstance(parts, list):
        report.error(where, 'O9: "parts" is the list of the book\'s parts, each {"slug", "label", "pages"}')
        parts = []
    slugs = [part.get('slug') if isinstance(part, dict) else None for part in parts]
    wanted = [part.slug for part in outline.parts]
    if slugs != wanted:
        report.error(line_of('"parts"'), 'O9: the sidebar lists the parts %s; the outline\'s %d parts are, in order, %s'
                     % (slugs, len(wanted), wanted))
    listed = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        slug = part.get('slug')
        at = line_of('"%s"' % slug)
        outline_part = next((candidate for candidate in outline.parts if candidate.slug == slug), None)
        if outline_part is not None and part.get('label') != outline_part.title:
            report.error(at, 'O9: part "%s" has the label %s; its title in the outline (plan/%s:%d) is "%s": write that'
                         % (slug, json.dumps(part.get('label')), outline_part.file, outline_part.line, outline_part.title))
        items = part.get('pages')
        if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
            report.error(at, 'O9: part "%s": "pages" is a list of page ids' % slug)
            continue
        listed.extend(items)
        for item in items:
            if not item.startswith('%s/' % slug):
                report.error(line_of('"%s"' % item), 'O9: "%s" is not a page of part "%s": list it in its own part' % (item, slug))
            elif item not in existing:
                report.error(line_of('"%s"' % item), 'O9: the sidebar lists "%s", which is no page (src/content/docs/%s.md): '
                             'remove it or write the page' % (item, item))
        if outline_part is None:
            continue
        rows = [row.id for row in outline_part.pages]
        expected = ([slug + '/index'] if slug + '/index' in items else []) + [row for row in rows if row in items] \
            + ([slug + '/review'] if slug + '/review' in items else [])
        if [item for item in items if item in expected] != expected:
            report.error(at, 'O9: part "%s" lists its pages in another order than the outline\'s rows (the index page first, '
                         'the review page last): %s' % (slug, ', '.join(expected)))
    for item in sorted(set(listed)):
        if listed.count(item) > 1:
            report.error(line_of('"%s"' % item), 'O9: "%s" is listed %d times: list every page exactly once' % (item, listed.count(item)))
    for page_id in sorted(existing - set(listed)):
        report.error(where, 'O9: src/content/docs/%s.md is not listed in src/sidebar.json: add it to its part' % page_id)
    tracks = sidebar.get('tracks') if isinstance(sidebar, dict) else None
    if not isinstance(tracks, dict):
        report.error(where, 'O5: "tracks" holds the tracks game, beginner and engine, each with its "sequence"')
        return {}
    sequences = {}
    for key, letter in c_SidebarTracks.items():
        track = tracks.get(key)
        at = line_of('"%s"' % key)
        if not isinstance(track, dict) or not isinstance(track.get('sequence'), list):
            report.error(at, 'O5: track "%s" (%s) has no "sequence" of page ids' % (key, letter))
            continue
        sequence = track['sequence']
        if any(not isinstance(item, str) for item in sequence):
            report.error(at, 'O5: track "%s"\'s "sequence" holds something that is not a page id' % key)
            continue
        expected = outline_rules.track_order(outline, letter)
        for item in sequence:
            if item not in outline.by_id:
                report.error(at, 'O5: track "%s" lists "%s", which is no row of the outline: remove it' % (key, item))
        for item in sorted(set(item for item in sequence if isinstance(item, str))):
            if sequence.count(item) > 1:
                report.error(at, 'O5: track "%s" lists "%s" twice: list each page once' % (key, item))
        if sequence != expected:
            number = next((n for n, (got, want) in enumerate(zip(sequence, expected)) if got != want), min(len(sequence), len(expected)))
            got = '"%s"' % sequence[number] if number < len(sequence) else 'the end of the list'
            want = '"%s"' % expected[number] if number < len(expected) else 'the end of the list'
            report.error(at, 'O5: track "%s" entry %d is %s; plan/tracks.md\'s track %s puts %s there: write the track\'s rows '
                         'in its order, written or not' % (key, number + 1, got, letter, want))
        entries = outline.tracks[letter]
        wanted_steps = [{'id': page_id, 'before': next((entry[0] for entry in entries[number + 1:] if not entry[1]), None)}
                        for number, (page_id, side_step, _) in enumerate(entries) if side_step]
        if track.get('sideSteps') != wanted_steps:
            report.error(at, 'O5: track "%s"\'s "sideSteps" are %s; plan/tracks.md gives %s: write that list ([] for none)'
                         % (key, json.dumps(track.get('sideSteps')), json.dumps(wanted_steps)))
        sequences[letter] = sequence
    return sequences


def check_tracks_of_pages(pages, records, sequences, outline, report):
    """O4 and O5 on the front matter: a page's tracks are the tracks whose list holds it, and each Need comes earlier."""
    for letter in outline_rules.c_TrackLetters:
        if letter not in sequences:
            continue
        on_track = set(sequences[letter])
        for page in pages:
            record = records.get(page.id)
            if record is None or record['tracks'] is None:
                continue
            if (letter in record['tracks']) != (page.id in on_track):
                report.error(page.key_at('tracks'), 'O5: %s, but the sidebar\'s track %s %s it: the tracks name exactly the '
                             'tracks whose list holds the page' % ('"tracks" names %s' % letter if letter in record['tracks']
                                                                   else '"tracks" does not name %s' % letter, letter,
                                                                   'does not hold' if letter in record['tracks'] else 'holds'))
        order = outline_rules.track_order(outline, letter)

        def needs(page_id):
            record = records.get(page_id)
            if record is None or record['needs'] is None or record['tracks'] is None or letter not in record['tracks']:
                return None
            return record['needs']

        for page_id, need in outline_rules.needs_met_earlier(order, needs):
            page = next(page for page in pages if page.id == page_id)
            report.error(page.key_at('needs'), 'O4: on track %s, no alternative of the Need "%s" comes earlier: change the Need '
                         'or ask the planner to change the outline' % (letter, '|'.join(need)))


def check_glossary(layout, path, outline, pages, report):
    """pipelines.md §9: src/content/glossary.json's schema, its homes and its names."""
    relative = layout.relative(path)
    try:
        text = repo.read_text(path)
    except FileNotFoundError:
        report.error('%s:1' % relative, 'the glossary is missing: write {"terms": []} at least')
        return
    try:
        data = json.loads(text)
    except ValueError as error:
        report.error('%s:%d' % (relative, getattr(error, 'lineno', 1)), 'not valid JSON: %s' % error)
        return
    terms = data.get('terms') if isinstance(data, dict) else None
    if not isinstance(terms, list) or set(data) != {'terms'}:
        report.error('%s:1' % relative, 'the glossary is {"terms": [{"id", "term", "definition", "home", …}]} (pipelines.md §9)')
        return
    written = {page.id for page in pages}
    names = {}
    ids = {}
    search_from = 0
    for number, entry in enumerate(terms, start=1):
        line = 1
        if isinstance(entry, dict):
            # The entry's line: where its term (or its id) is written, searching on from the entry before it.
            for key in ('term', 'id'):
                if isinstance(entry.get(key), str):
                    index = text.find('"%s": %s' % (key, json.dumps(entry[key], ensure_ascii=False)), search_from)
                    if index >= 0:
                        line = text.count('\n', 0, index) + 1
                        search_from = index
                        break
        where = '%s:%d' % (relative, line)
        if not isinstance(entry, dict):
            report.error(where, 'entry %d is not an object {"id", "term", "definition", "home"}' % number)
            continue
        for key in entry:
            if key not in c_GlossaryKeys:
                report.error(where, 'entry %d has the unknown key "%s": the keys are %s' % (number, key, ', '.join(c_GlossaryKeys)))
        term = entry.get('term')
        if not isinstance(term, str) or not term.strip():
            report.error(where, 'entry %d has no "term": write the term as the book writes it' % number)
            continue
        label = '"%s"' % term
        expected_id = glossary_id(term)
        if entry.get('id') != expected_id:
            report.error(where, '%s: "id" is the term in lowercase words joined by "-": write "id": "%s"' % (label, expected_id))
        if expected_id in ids:
            report.error(where, '%s: the id "%s" is also the id of the entry at line %s: two meanings get two qualified terms '
                         '("pack block", "BC block")' % (label, expected_id, ids[expected_id]))
        ids.setdefault(expected_id, line)
        definition = entry.get('definition')
        if not isinstance(definition, str) or not definition.strip():
            report.error(where, '%s has no "definition": write one sentence that says what it is' % label)
        elif re.search(r'[.?!]\s+[A-Z0-9]', definition.strip()) or not definition.strip().endswith('.'):
            report.error(where, '%s: the definition is one sentence ending with "." (pipelines.md §9): join or cut its sentences'
                         % label)
        home = entry.get('home')
        if not isinstance(home, str) or not home:
            report.error(where, '%s has no "home": name the page that defines it' % label)
        elif home not in outline.by_id:
            report.error(where, '%s: the home "%s" is no page of the outline (plan/outline-*.md): name the row that defines it'
                         % (label, home))
        elif home not in written:
            report.pending(where, '%s: its home page %s is not written yet' % (label, home))
        use = entry.get('use')
        if use is not None:
            if not isinstance(use, str) or use not in outline.by_id or not use.startswith('make/'):
                report.error(where, '%s: "use" names its use home, a page of part make in the outline (style.md §3)' % label)
            elif use not in written:
                report.pending(where, '%s: its use home %s is not written yet' % (label, use))
        if 'known' in entry and not isinstance(entry['known'], bool):
            report.error(where, '%s: "known" is true or false' % label)
        own = [term]
        for key in ('aliases', 'avoid'):
            value = entry.get(key, [])
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                report.error(where, '%s: "%s" is a list of names' % (label, key))
                continue
            if key == 'aliases':
                own.extend(value)
        for name in own:
            key = name.strip().lower()
            if key in names and names[key] != (number, line):
                report.error(where, '%s: the name "%s" is also a name of the entry at line %d: each name belongs to one entry'
                             % (label, name, names[key][1]))
            names.setdefault(key, (number, line))
    for number, entry in enumerate(terms, start=1):
        if not isinstance(entry, dict) or not isinstance(entry.get('avoid'), list):
            continue
        for name in entry['avoid']:
            if isinstance(name, str) and name.strip().lower() in names:
                other = names[name.strip().lower()]
                report.error('%s:%d' % (relative, other[1]), '"%s" is a name of this entry and an "avoid" name of entry %d: the '
                             'book uses it or avoids it, not both' % (name, number))


def glossary_id(term):
    """pipelines.md §9: an entry's id is its term in lowercase words joined by "-" (apostrophes dropped)."""
    return re.sub(r'[^a-z0-9]+', '-', term.lower().replace("'", '').replace('’', '')).strip('-')


def check_outline_data(layout, outline, report):
    """src/generated/outline.json is what the outline gives today."""
    path = os.path.join(layout.root, *c_OutlineData.split('/'))
    expected = outline_text(outline)
    try:
        current = repo.read_text(path)
    except FileNotFoundError:
        report.error('%s:1' % c_OutlineData, 'the outline\'s data file is missing: run python -I tools/pages.py outline --write')
        return
    if current != expected:
        report.error('%s:1' % c_OutlineData, 'the file is not what the outline gives today: run python -I tools/pages.py '
                     'outline --write and commit it with the outline\'s change')


def outline_text(outline):
    return json.dumps(outline_rules.to_data(outline), indent='\t', ensure_ascii=False) + '\n'


def check(layout, release, plan=None, book=outline_rules.c_Book, glossary=None):
    """(errors, notes) of the whole book; each a list of (where, message)."""
    report = Report(release)
    plan = plan or os.path.join(layout.root, 'plan')
    outline = outline_rules.read(plan, book, documents=False)
    for problem in outline.problems:
        report.error(outline_problem_where(problem), 'the outline: %s (the planner fixes it; python plan/check_outline.py '
                     'lists every problem)' % problem)
    pin = repo.read_pin(layout.pin_file)
    pages = [BookPage(layout, path) for _, path in layout.pages()]
    records = {}
    slugs = {}
    for page in pages:
        if page.slug in slugs:
            report.error(page.at(), 'O1: %s and %s are served at the same address /%s/: rename one' % (slugs[page.slug], page.relative, page.slug))
        slugs.setdefault(page.slug, page.relative)
        if page.error:
            report.error(page.at(error_line(page.error)), 'the front matter is not valid YAML or not the book\'s subset: %s'
                         % re.sub(r'^line \d+: ', '', page.error))
            check_quoting(page, report)
            continue
        check_quoting(page, report)
        if page.special:
            check_special_page(page, report)
            continue
        for problem, advice in outline_rules.id_problems(page.id, part_page=page.part_page):
            report.error(page.at(), 'O1: %s: %s' % (problem, advice))
        if page.part_page:
            check_part_page(page, outline, report)
            continue
        row = outline.by_id.get(page.id)
        if row is None:
            report.error(page.at(), 'O7: %s is no row of the outline (plan/outline-*.md): pages and plan cannot drift; ask the '
                         'planner for a row, or rename the file to its row\'s id' % page.id)
        needs, tracks, learn_ids = check_book_page(page, row, outline, pin, report)
        records[page.id] = {'needs': needs, 'tracks': tracks}
        kind = page.data.get('kind')
        if kind in c_Strips:
            check_shape(page, kind, learn_ids, outline, report)
        check_solutions(layout, page, blocks.Page(page.text), report)
        check_checkpoints(page, kind, report)
        check_build_rules(layout, page, kind, outline, report)
    written = {page.id for page in pages}
    for page in pages:
        record = records.get(page.id)
        if record is None or record['needs'] is None:
            continue
        for need in record['needs']:
            for alternative in need:
                if alternative == page.id:
                    report.error(page.key_at('needs'), 'O2: the page needs itself: remove the Need')
                elif alternative not in outline.by_id:
                    report.error(page.key_at('needs'), 'O2: the Need "%s" is no page of the outline: name a row' % alternative)
                elif alternative not in written:
                    report.pending(page.key_at('needs'), 'O2: the Need "%s" is not written yet' % alternative)
    graph = {page_id: [alternative for need in record['needs'] or [] for alternative in need] for page_id, record in records.items()}
    for cycle in outline_rules.find_cycles(graph, sorted(graph)):
        page = next(page for page in pages if page.id == cycle[0])
        report.error(page.key_at('needs'), 'O6: the Needs form a cycle: %s; remove one of these Needs' % ' -> '.join(cycle))
    for row in outline.pages:
        if row.id not in written:
            report.pending('plan/%s:%d' % (row.file, row.line), 'O7: the row %s has no page yet (src/content/docs/%s.md)' % (row.id, row.id))
    for part in outline.parts:
        if len(part.pages) < outline_rules.c_GeneratedPagesFrom:
            continue
        missing = ['%s/%s' % (part.slug, last) for last in c_Generated if '%s/%s' % (part.slug, last) not in written]
        if len(missing) == 1:
            report.error('src/content/docs/%s.md:1' % ('%s/%s' % (part.slug, [last for last in c_Generated if '%s/%s' % (part.slug, last) not in missing][0])),
                         'O8: the part pages come together: write src/content/docs/%s.md too' % missing[0])
        for page_id in missing:
            report.pending('plan/%s:%d' % (part.file, part.line), 'O8: part "%s" has %d rows, so it has src/content/docs/%s.md; '
                           'the part editor writes it' % (part.slug, len(part.pages), page_id))
    sequences = check_sidebar(layout, outline, pages, report)
    check_tracks_of_pages(pages, records, sequences, outline, report)
    check_glossary(layout, glossary or layout.glossary, outline, pages, report)
    check_outline_data(layout, outline, report)
    return report.errors, report.notes


def outline_problem_where(problem):
    """"plan/<file>:<line>" (or "tools/booklib/outline.py:1") of a problem of the outline."""
    match = re.match(r'^(?P<file>[\w./-]+\.(?:md|py))(?::(?P<line>\d+))?', problem.where or problem.text)
    if not match:
        return 'plan/%s:1' % outline_rules.c_OutlineFiles[0]
    name = match.group('file')
    return '%s:%s' % (name if '/' in name else 'plan/' + name, match.group('line') or 1)


def summary_of_notes(notes):
    """The notes, with the many "not written yet" notes of a draft counted instead of listed one by one."""
    groups = (('has no page yet', 'O7: %d rows of the outline have no page yet (--release lists them)'),
              ('the part editor writes it', 'O8: %d part pages of the parts with eight or more rows are not written yet '
               '(--release lists them)'))
    result = list(notes)
    for marker, summary in groups:
        found = [note for note in result if marker in note[1]]
        if len(found) > 10:
            result = [note for note in result if marker not in note[1]] + [('plan/outline-1.md:1', summary % len(found))]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['check', 'outline'], help='check the book, or print or write the outline as data')
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--plan', help='the plan folder with outline-1.md to outline-4.md and tracks.md (default: <root>/plan)')
    parser.add_argument('--glossary', help='check: the glossary file (default: <root>/src/content/glossary.json)')
    parser.add_argument('--release', action='store_true', help='check: what is not written yet is an error, not a note')
    parser.add_argument('--quiet', action='store_true', help='check: print errors only')
    parser.add_argument('--write', action='store_true', help='outline: write src/generated/outline.json')
    parser.add_argument('--check', action='store_true', help='outline: fail when src/generated/outline.json is stale')
    repo.utf8_output()
    options = parser.parse_args(argv)
    layout = repo.Layout(options.root)
    plan = os.path.abspath(options.plan) if options.plan else os.path.join(layout.root, 'plan')
    if not os.path.isfile(os.path.join(plan, outline_rules.c_OutlineFiles[0])):
        print('pages: no outline at %s: pass --plan <folder>' % plan, file=sys.stderr)
        return 2
    if options.command == 'outline':
        if options.write and options.check:
            print('pages: outline takes --write or --check, not both', file=sys.stderr)
            return 2
        outline = outline_rules.read(plan)
        if outline.problems:
            for problem in outline.problems:
                print(problem)
            print('pages: the outline has %d problems; fix them before writing its data' % len(outline.problems), file=sys.stderr)
            return 1
        text = outline_text(outline)
        path = os.path.join(layout.root, *c_OutlineData.split('/'))
        if options.write:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            repo.write_text(path, text)
            print('pages: wrote %s (%d pages)' % (c_OutlineData, len(outline.pages)))
            return 0
        if options.check:
            current = repo.read_text(path) if os.path.isfile(path) else None
            if current != text:
                print('%s:1: the file is not what the outline gives today: run python -I tools/pages.py outline --write' % c_OutlineData)
                return 1
            print('pages: %s is current' % c_OutlineData)
            return 0
        sys.stdout.write(text)
        return 0
    if options.write or options.check:
        print('pages: --write and --check belong to the outline command', file=sys.stderr)
        return 2
    try:
        errors, notes = check(layout, options.release, plan=plan, glossary=options.glossary and os.path.abspath(options.glossary))
    except (OSError, ValueError) as error:
        print('pages: %s' % error, file=sys.stderr)
        return 2
    for where, message in errors:
        print('%s: %s' % (where, message))
    if not options.quiet:
        for where, message in summary_of_notes(notes):
            print('%s: note: %s' % (where, message))
    count = len(layout.pages())
    print('pages: %d page%s, %d error%s, %d note%s' % (count, '' if count == 1 else 's', len(errors), '' if len(errors) == 1 else 's',
                                                      len(notes), '' if len(notes) == 1 else 's'))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
