#!/usr/bin/env python3
"""Writes the term marks a page needs (plan/critique/rulings-11.md, R53 and R54; plan/style.md §3):

    python -I tools/markterms.py <page id> [--check] [--root <book>] [--plan <folder>] [--glossary <file>]

It asks the lint which first uses of terms term-mark reports (tools/lint.py unmarked_terms, the rule's own functions,
so that the two never disagree) and writes, at each, the mark :term[<the words as written>]{id=<entry id>}. Those are
first uses of terms whose home or use home is a page of the page's Needs closure (R54): a term homed outside the
closure is neither marked nor linked, since the writer says in the sentence what it is, and the tool never writes a
link. term-mark also leaves alone, so the tool does too, a one-word term of the common list (R53), a use in a block
quote, in the test-out box or anywhere in an entry of Further reading, a use in a sentence that already links the
term's home, and a use in the sentence of the page's own bold definition of the term or right after it (the same or
the next block).
The tool changes only the words of the first use: never a heading, a fence, inline code or a formula, an existing
link's text, a word in bold (a definition or a UI label), a directive (its label and its attributes), an HTML comment
or the front matter; a first use inside one of these is left for the writer, with a note. No rule limits the length of
a line (.markdownlint-cli2.jsonc turns MD013 off, and the book has no .editorconfig), so the lines stay as they are: a
mark over a line end keeps the line end inside its text, as remark reads it. A second run changes nothing.

It prints one line per change, "<file>:<line>: mark: ...", one "... (note)" line per first use it leaves for the
writer, and a count. --check writes nothing and exits 1 when a run would change the page.

Only the standard library is used. Exit codes: 0 when the page needs nothing more or was written, 1 with --check when a
run would change the page, 2 for usage or environment errors.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lint  # noqa: E402
from booklib import outline as outline_rules, prose, repo  # noqa: E402

# What a mark cannot stand in or around: the inline forms of booklib/prose.py that are not plain words.
c_Protected = ('code', 'math', 'image', 'link', 'directive', 'mark', 'autolink', 'comment', 'html', 'escape')
# Between the words of a name: spaces or a line end (a block quote's "> " after it), and emphasis marks.
c_Between = r'[*_]*\s+(?:>[ \t]*)*[*_]*'


class Change:
    def __init__(self, occurrence, start, end, words, replacement):
        self.occurrence = occurrence
        self.start, self.end = start, end
        self.words = words
        self.replacement = replacement


def read_page(context, page_id, path, text=None):
    """The lint's view of a page; with text, of that text instead of the file's."""
    page = lint.PageText(context, page_id, path)
    if text is not None:
        page.text = text
        page.body = prose.Page(text)
    return page


def eligible(word):
    """A word a mark may be written around: plain text, outside bold, links, marks and directives."""
    return word.kind == 'word' and not word.bold and word.link is None and word.term is None and word.directive is None


def name_pattern(words):
    """The words as the source writes them, whole: not inside a longer word ("snake_loop", "re-loop", "loop's")."""
    body = c_Between.join(re.escape(word.bare) for word in words)
    return re.compile(r'(?<![^\W_])(?<![^\W_]_)(?<![\-‐‑])' + body + r'(?![^\W_])(?!_[^\W_])(?![\-‐‑])(?![\'’][^\W_])')


def protected_spans(text):
    """The spans of a block's source that hold no plain words: inline code, formulas, links, directives, marks, HTML,
    escapes, and the text between bold marks."""
    spans = []
    bold_start = None
    for match in prose.c_Inline.finditer(text):
        if match.group('strong'):
            if bold_start is None:
                bold_start = match.start()
            else:
                spans.append((bold_start, match.end()))
                bold_start = None
            continue
        if any(match.group(name) for name in c_Protected):
            spans.append((match.start(), match.end()))
    if bold_start is not None:
        spans.append((bold_start, len(text)))
    return spans


def place(page, occurrence):
    """(start, end, text) of the occurrence in the page's text, or the reason it cannot be marked."""
    words = occurrence.words
    if not all(eligible(word) for word in words):
        return 'its words stand in a link, a directive or bold text, which the tool does not change'
    block = occurrence.block
    lines = page.text.split('\n')
    first, last = block.lines[0][0], block.lines[-1][0]
    offset = sum(len(line) + 1 for line in lines[:first - 1])
    source = '\n'.join(lines[first - 1:last])
    # The occurrence is the n-th time these words stand, as plain words, in the block: count the ones before it.
    bares = [word.bare for word in words]
    index = block.words.index(words[0])
    before = 0
    for start in range(index):
        window = block.words[start:start + len(words)]
        if [word.bare for word in window] == bares and all(eligible(word) for word in window):
            before += 1
    spans = protected_spans(source)
    found = [match for match in name_pattern(words).finditer(source)
             if not any(start < match.end() and match.start() < end for start, end in spans)]
    if len(found) <= before:
        return 'the tool did not find its words in the source of the block'
    match = found[before]
    return offset + match.start(), offset + match.end(), match.group(0)


def changes_for(context, page):
    """The changes a run makes on the page, and the first uses it leaves for the writer (occurrence, reason)."""
    changes, left = [], []
    for occurrence in lint.unmarked_terms(context, page):
        entry = occurrence.entry
        placed = place(page, occurrence)
        if isinstance(placed, str):
            left.append((occurrence, placed))
            continue
        start, end, words = placed
        changes.append(Change(occurrence, start, end, words, ':term[%s]{id=%s}' % (words, entry['id'])))
    return changes, left


def apply(text, changes):
    for change in sorted(changes, key=lambda change: change.start, reverse=True):
        text = text[:change.start] + change.replacement + text[change.end:]
    return text


def mark_page(context, page_id, path):
    """(new text, changes, left) for a page. Each change is checked on the text it gives: a change after which the
    lint still reports its term is dropped and its first use left for the writer."""
    page = read_page(context, page_id, path)
    changes, left = changes_for(context, page)
    while changes:
        text = apply(page.text, changes)
        still = {occurrence.entry['id'] for occurrence in lint.unmarked_terms(context, read_page(context, page_id, path, text))}
        failed = [change for change in changes if change.occurrence.entry['id'] in still]
        if not failed:
            return text, changes, left
        for change in failed:
            left.append((change.occurrence, 'the lint still reports it after the change, so the tool does not make it'))
        changes = [change for change in changes if change not in failed]
    return page.text, [], left


def main(argv=None, book=outline_rules.c_Book):
    repo.utf8_output()
    parser = argparse.ArgumentParser(description='Writes the term marks a page needs (rulings-11.md, R53 and R54).',
                                     epilog=__doc__.split('\n\n', 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('page', help='the page id, such as core/time')
    parser.add_argument('--check', action='store_true', help='write nothing; exit 1 when a run would change the page')
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--plan', help='the plan folder (default: <root>/plan)')
    parser.add_argument('--glossary', help='the glossary (default: src/content/glossary.json)')
    options = parser.parse_args(argv)
    page_id = repo.named_page(options.page)
    try:
        layout = repo.Layout(options.root)
        path = dict(layout.pages()).get(page_id)
        if path is None:
            print('markterms: no page %s under src/content/docs/ (give a page id such as core/time)' % page_id, file=sys.stderr)
            return 2
        context = lint.Terms(layout, plan=options.plan, book=book, glossary=options.glossary)
        page = read_page(context, page_id, path)
        if page.book_page.special:
            print('markterms: %s has no term rules (style.md §3): nothing to write' % page_id)
            return 0
        text, changes, left = mark_page(context, page_id, path)
    except (lint.LintError, OSError, ValueError) as error:
        print('markterms: %s' % error, file=sys.stderr)
        return 2
    relative = layout.relative(path)
    for change in sorted(changes, key=lambda change: change.start):
        print('%s:%d: mark: "%s" -> %s' % (relative, change.occurrence.line, change.occurrence.entry['term'],
                                           change.replacement.replace('\n', ' ')))
    for occurrence, reason in left:
        print('%s:%d: left for the writer: "%s": %s (note)' % (relative, occurrence.line, occurrence.entry['term'], reason))
    counts = '%d mark%s' % (len(changes), '' if len(changes) == 1 else 's')
    tail = ', %d left for the writer' % len(left) if left else ''
    if options.check:
        if changes:
            print('markterms: %d to write (%s)%s: run python -I tools/markterms.py %s' % (len(changes), counts, tail, page_id))
            return 1
        print('markterms: nothing to write%s' % tail)
        return 0
    if changes:
        repo.write_text(path, text)
    print('markterms: %d written (%s)%s' % (len(changes), counts, tail))
    return 0


if __name__ == '__main__':
    sys.exit(main())
