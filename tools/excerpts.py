#!/usr/bin/env python3
"""The book's quotes (plan/pipelines.md §3): every fence with src="…" holds exactly the lines it names, at the pinned
engine commit (engine.pin), in a vendored library at the commit the pin records for it, or in this repository.

    python -I tools/excerpts.py fill     --engine <clone> [pages...]
    python -I tools/excerpts.py check    --engine <clone> [--release] [pages...]
    python -I tools/excerpts.py relocate --engine <clone> --from <old pin> [--to <new pin>] [--write] [pages...]
    python -I tools/excerpts.py list     [--since <commit of this repository>] [pages...]

Sources (§3.2). src begins with
  an engine path            the file at the pin; its first part is a top-level entry of the engine (Strata/, Tools/ …)
  vendor:<lib>/<path>       the file of the submodule Strata/vendor/<lib> at the commit the pin records for it, read
                            from the clone's checkout of that submodule
  book:<path>               a file of this repository (tutorial files, labs, patches)
  book:<path>.patch#hunk-<n>  the n-th hunk of a tutorial's patch, its " ", "+" and "-" lines (a ```diff fence)

Forms of src (§3.3). A filled quote is src="<source>#L<first>-L<last>" (or #L<n>). While a page is written an anchor
stands in place of the lines, and fill turns it into lines:
  src="<source>#<symbol>"                   the whole definition of the symbol, with the comment just above it
    plus from="<text>" to="<text>"          from the first line inside the definition that contains from to the first
                                            later line that contains to; each text occurs once inside the definition
    plus overload="<n>"                     the n-th definition in file order, when the symbol has several
  src="<source>" command="<name>"           the registration of an editor command: the Register( call that holds
                                            "<name>", from its first line to the line that closes it (from and to
                                            choose lines inside it, as for a symbol)
After fill, src ends with #L<first>-L<last>, and the anchor attributes (symbol, from, to, overload, command) stay on the
fence, so that relocate finds the lines again after a pin move. A filled quote's #L… is what fill and check read; to
choose other lines, write the draft form again.

Normalization (§3.4): fill and check remove the smallest number of leading tabs over the quoted lines that are not
blank and not preprocessor lines at column 0, and nothing else.

fill      writes the bodies, the #L… of src and symbol into pages. It refuses a quote, leaving it unchanged, when it
          would hold more than 60 lines, when its anchor matches no place or several, or when its file does not exist at
          the pin; then it exits 1. It also writes src/generated/vendor.json, which the build reads for the header of a
          vendor: quote: {"pin", "libraries": {"<lib>": {"name", "version", "license", "repository", "commit"}}} for
          every library a page quotes, as ThirdPartyNotices.md records it at the pin (rulings-6, R26; the form is in
          .tools/handover/vendor-format.md). While no page quotes a library, no file is needed.
check     fails (exit 1) on a body that differs from the normalized lines at the pin; a draft form; a quote over 60
          lines; a page of kind internals with fewer than three quotes; an engine path named in backticks in the prose
          that does not exist at the pin (a path through a submodule is looked up in it); Expressive Code's own markers
          on a quote ({…} ranges, ins=, del=, title=, a mark= that is not the file's lines inside the quote) and a
          mark="L…" on a fence without src; and a vendor: quote whose library is not in the engine's
          ThirdPartyNotices.md at the pin (matched by the submodule's URL in .gitmodules) or not named, with its license
          as ThirdPartyNotices.md writes it, on one line of the page appendix/credits. While appendix/credits is not
          written, that last check is a note; with --release it is an error. It also fails when
          src/generated/vendor.json is not what fill writes.
relocate  per quote, in this order: the same lines hold the same text at the new pin (same); the same text is elsewhere
          in the same file (moved, to the nearest place; --write updates #L…, the marks and the numbered callouts after
          the fence, "1. **Lines 5–10:**", that name its lines); the quote's most distinctive line (its longest line that
          occurs once in the old file) is found by git grep -F at the new pin and the whole quote is there (moved-file;
          --write updates src, the marks and the callouts; the prose may name the old path, so read it); the
          anchor finds its lines at the new pin but the text differs (changed: read the page again, then fill);
          otherwise missing. Exit 1 when any quote is moved-file, changed or missing. Quotes of book: files do not
          follow the pin; vendor: quotes follow the commit each pin records for their submodule.
list      prints every quote as <page>:<line>: <src>; with --since <commit>, only the fences whose src or anchor
          changed since that commit of this repository (a change after review needs the page's confirm).

Every message names the page and the line. --engine is the pin clone (default: $STRATA_ENGINE); the tool reads it at
the pin through one git cat-file process (§1.2), and stops with exit code 2 when the clone does not have the pin
(§1.4, check 1). Only the standard library is used. Exit codes: 0 all is well, 1 problems were found, 2 usage or
environment errors.
"""

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import frontmatter, markdown, repo  # noqa: E402

c_MaxLines = 60
c_MinInternalsQuotes = 3
c_Anchors = ('symbol', 'from', 'to', 'overload', 'command')
# A from= or to= value as a fence's info string writes it, and what follows its closing quote: an inner quote, escaped
# or not, ends the attribute in the site's reader (src/lib/markdown.mjs parseMeta after remark removes the escapes).
c_QuotedAnchor = re.compile(r'(?<![\w-])(?P<name>from|to)="(?P<value>(?:[^"\\]|\\.)*)"(?P<after>\S?)')
c_Credits = 'appendix/credits'
c_InlineCode = re.compile(r'(`+)([^`]+?)\1')
c_PathSuffix = re.compile(r'(?::\d+(?:[-–]\d+)?(?:,\s*:?\d+(?:[-–]\d+)?)*|#L\d+(?:-L\d+)?)$')
c_Symbol = re.compile(r'^[A-Za-z_~][\w:~<>,]*$')
c_Lines = re.compile(r'^L(\d+)(?:-L(\d+))?$')
c_RefusedAttributes = ('ins', 'del', 'title')


class ExcerptError(Exception):
    pass


class UsageError(Exception):
    pass


# ---------------------------------------------------------------------------------------------------------------------
# The src attribute.

class Source:
    """A parsed src: namespace ('engine', 'vendor', 'book'), path (inside its namespace), lib (vendor), and one of
    start/end (lines), symbol (a draft), hunk (a patch's hunk) or neither (the command form, with command=)."""

    def __init__(self, namespace, path, lib=None, start=None, end=None, symbol=None, hunk=None):
        self.namespace, self.path, self.lib = namespace, path, lib
        self.start, self.end, self.symbol, self.hunk = start, end, symbol, hunk

    @property
    def prefix(self):
        if self.namespace == 'vendor':
            return 'vendor:%s/%s' % (self.lib, self.path)
        if self.namespace == 'book':
            return 'book:' + self.path
        return self.path

    @property
    def filled(self):
        return self.start is not None or self.hunk is not None

    def with_lines(self, start, end):
        return '%s#L%d' % (self.prefix, start) if start == end else '%s#L%d-L%d' % (self.prefix, start, end)

    def label(self):
        if self.hunk is not None:
            return '%s#hunk-%d' % (self.prefix, self.hunk)
        if self.start is not None:
            return self.with_lines(self.start, self.end)
        return self.prefix + ('#' + self.symbol if self.symbol else '')


def parse_source(value, attributes=None):
    """The Source of a src value; raises ExcerptError with what to write instead."""
    attributes = attributes or {}
    location, hash_mark, fragment = value.partition('#')
    namespace, lib = 'engine', None
    if location.startswith('vendor:'):
        namespace = 'vendor'
        lib, _, location = location[len('vendor:'):].partition('/')
        if not re.match(r'^[A-Za-z0-9._-]+$', lib or '') or not location:
            raise ExcerptError('src="%s": a vendored file is vendor:<library>/<path in the library>, such as vendor:glm/glm/glm.hpp' % value)
    elif location.startswith('book:'):
        namespace = 'book'
        location = location[len('book:'):]
    if not location or location.startswith('/') or '\\' in location or '..' in location.split('/') or re.match(r'^[A-Za-z]:', location):
        raise ExcerptError('src="%s": the path is relative to %s, with "/" separators' % (
            value, {'engine': "the engine's root", 'vendor': "the library's root", 'book': "this repository's root"}[namespace]))
    if not hash_mark:
        if 'command' in attributes:
            return Source(namespace, location, lib)
        raise ExcerptError('src="%s" names no lines: write src="%s#L<first>-L<last>", a symbol (src="%s#<Class::Function>") '
                           'or a command (command="<group.action>")' % (value, location, location))
    lines = c_Lines.match(fragment)
    if lines:
        start = int(lines.group(1))
        end = int(lines.group(2) or lines.group(1))
        if start < 1 or end < start:
            raise ExcerptError('src="%s": the lines run forwards from line 1 or later (#L<first>-L<last>)' % value)
        return Source(namespace, location, lib, start=start, end=end)
    hunk = re.match(r'^hunk-([1-9]\d*)$', fragment)
    if hunk:
        if namespace != 'book' or not location.endswith('.patch'):
            raise ExcerptError('src="%s": #hunk-<n> names a hunk of a tutorial\'s patch: src="book:<path>.patch#hunk-<n>"' % value)
        return Source(namespace, location, lib, hunk=int(hunk.group(1)))
    if c_Symbol.match(fragment):
        return Source(namespace, location, lib, symbol=fragment)
    raise ExcerptError('src="%s": "#%s" is neither lines (#L10-L20) nor a symbol (#Scene::OnUpdate)' % (value, fragment))


def is_quote(fence):
    return 'src' in fence.attributes


def quotes(text):
    """(fence, Source or ExcerptError) for every fence with src= in a page."""
    result = []
    for fence in markdown.fences(text):
        if not is_quote(fence):
            continue
        try:
            result.append((fence, parse_source(fence.attributes['src'], fence.attributes)))
        except ExcerptError as error:
            result.append((fence, error))
    return result


def set_attribute(info, name, value):
    """The info string with name="value" set: replaced where it stands, else appended."""
    pattern = re.compile(r'''(?<![\w-])%s=("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\S+)''' % re.escape(name))
    quoted = '%s="%s"' % (name, value.replace('\\', '\\\\').replace('"', '\\"'))
    if pattern.search(info):
        return pattern.sub(lambda _: quoted, info, count=1)
    return info.rstrip() + ' ' + quoted


def shift_marks(info, delta):
    """The info string with every engine line number of mark="L…" moved by delta (the quote's lines moved by as many).
    Marks that are not the file's lines stay as they are, for check to report."""
    def shift(match):
        value = next(group for group in match.groups() if group is not None)
        parts = []
        for part in value.split(','):
            numbers = re.match(r'^\s*L(\d+)(?:-L(\d+))?\s*$', part)
            if not numbers:
                return match.group(0)
            first = int(numbers.group(1)) + delta
            parts.append('L%d' % first if numbers.group(2) is None else 'L%d-L%d' % (first, int(numbers.group(2)) + delta))
        return 'mark="%s"' % ','.join(parts)
    return re.sub(r'''(?<![\w-])mark=(?:"([^"]*)"|'([^']*)'|(\S+))''', shift, info, count=1)


def parse_marks(value):
    """[(first, last)] of a mark="L…" value, or None when it is not the file's lines."""
    ranges = []
    for part in value.split(','):
        numbers = re.match(r'^\s*L(\d+)(?:-L(\d+))?\s*$', part)
        if not numbers:
            return None
        first = int(numbers.group(1))
        ranges.append((first, int(numbers.group(2) or first)))
    return ranges


# ---------------------------------------------------------------------------------------------------------------------
# Normalization (§3.4).

def normalize(lines):
    """The lines without the smallest number of leading tabs of the lines that are not blank and not preprocessor lines at
    column 0; every line loses at most that many."""
    counted = [line for line in lines if line.strip() and not line.startswith('#')]
    if not counted:
        return list(lines)
    smallest = min(len(line) - len(line.lstrip('\t')) for line in counted)
    if not smallest:
        return list(lines)
    result = []
    for line in lines:
        tabs = len(line) - len(line.lstrip('\t'))
        result.append(line[min(tabs, smallest):])
    return result


# ---------------------------------------------------------------------------------------------------------------------
# A small C++ scanner: enough to match brackets outside comments, strings, characters and raw strings.

def code_chars(lines, first):
    """Yields (line index, column, char) of every character of code from line `first` on: not in a comment or a
    literal, and not white space."""
    state = 'code'
    raw_end = None
    for index in range(first, len(lines)):
        line = lines[index]
        column = 0
        if state == 'line-comment':
            state = 'code'
        while column < len(line):
            char = line[column]
            ahead = line[column:column + 2]
            if state == 'code':
                if ahead == '//':
                    state = 'line-comment'
                    break
                if ahead == '/*':
                    state = 'block-comment'
                    column += 2
                    continue
                raw = re.match(r'(?:u8|u|U|L)?R"([^(\s]{0,16})\(', line[column:])
                if raw and (column == 0 or not (line[column - 1].isalnum() or line[column - 1] == '_')):
                    state = 'raw'
                    raw_end = ')' + raw.group(1) + '"'
                    column += raw.end()
                    continue
                if char == '"':
                    state = 'string'
                    yield index, column, char
                elif char == "'" and not (column > 0 and line[column - 1].isalnum()):
                    state = 'char'
                    yield index, column, char
                elif not char.isspace():
                    yield index, column, char
            elif state == 'block-comment':
                if ahead == '*/':
                    state = 'code'
                    column += 2
                    continue
            elif state in ('string', 'char'):
                if char == '\\':
                    column += 2
                    continue
                if (state == 'string' and char == '"') or (state == 'char' and char == "'"):
                    state = 'code'
            elif state == 'raw':
                end = line.find(raw_end, column)
                if end < 0:
                    break
                column = end + len(raw_end)
                state = 'code'
                continue
            column += 1
        if state in ('string', 'char'):
            state = 'code'  # An unterminated literal ends with its line (a macro continuation is rare in the engine).


def definition_end(lines, start, init_lists=True):
    """The last line (index) of the definition whose signature starts at `start`, or None for a declaration.

    Before the body opens: parentheses are counted, and whatever they hold (default arguments such as "= {}",
    lambdas, HLSL semantics) is part of the signature; a ";" outside them makes a declaration. With `init_lists` (C++,
    not shaders), a ":" after the parameter list starts a constructor's member initializers, whose "m_X{1}" braces
    follow a name, while the body's "{" follows the ")" or "}" of the last initializer."""
    depth = 0
    opened = False
    parens = 0
    skipping = 0
    closed_parameters = False
    initializers = False
    previous = ''
    for index, column, char in code_chars(lines, start):
        if opened:
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    return index
            continue
        if skipping:
            skipping += 1 if char == '{' else -1 if char == '}' else 0
        elif char == '(':
            parens += 1
        elif char == ')':
            parens -= 1
            if parens == 0:
                closed_parameters = True
        elif parens > 0:
            pass
        elif char == ';':
            return None
        elif char == ':':
            initializers = init_lists and closed_parameters and previous != ':'
        elif char == '{':
            if initializers and (previous.isalnum() or previous in '_>'):
                skipping = 1
            else:
                opened = True
                depth = 1
        previous = char
    return None


def call_end(lines, start, column):
    """The line (index) of the ")" that closes the "(" at lines[start][column], outside comments and literals."""
    depth = 0
    for index, char_column, char in code_chars(lines, start):
        if index == start and char_column < column:
            continue
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                return index
    return None


# Lines that belong to a definition above its signature: comments, template heads and attributes ([[nodiscard]],
# HLSL's [numthreads(8, 8, 1)]).
c_Preamble = re.compile(r'^\s*(//|template\s*<|\[\[.*\]\]\s*$|\[[A-Za-z_]\w*\s*(\(.*\))?\]\s*$)')
c_ShaderExtensions = ('.slang', '.hlsl', '.hlsli')


def preamble_start(lines, start):
    """The first line (index) of the comments, template heads and attributes right above line `start`."""
    while start > 0:
        above = lines[start - 1]
        if c_Preamble.match(above):
            start -= 1
            continue
        if re.search(r'\*/\s*$', above):
            opening = start - 1
            while opening >= 0 and '/*' not in lines[opening]:
                opening -= 1
            if opening < 0:
                break
            start = opening
            continue
        break
    return start


def symbol_definitions(lines, symbol, path):
    """[(first, last)] line indexes of every definition of `symbol` (comments above included), in file order."""
    parts = symbol.split('::')
    name = parts[-1]
    init_lists = not path.endswith(c_ShaderExtensions)
    patterns = [re.compile(r'(?<![\w:~])' + re.escape(symbol) + r'\s*\(')]
    if len(parts) > 1:
        # In a header the member is defined inside its class, without the class name.
        patterns.append(re.compile(r'(?<![\w:~.>])' + re.escape(name) + r'\s*\('))
    for pattern in patterns:
        found = []
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('//', '*', 'return ', '#')) or not pattern.search(line):
                continue
            if re.match(r'^\s*(if|while|for|switch|else)\b', line):
                continue
            end = definition_end(lines, index, init_lists)
            if end is not None:
                found.append((preamble_start(lines, index), end))
        if found:
            return found
    return []


def find_symbol(lines, symbol, path, overload=None):
    """(first, last) line numbers (1-based) of the definition of `symbol`, with the comment and attributes just above
    it; overload chooses the n-th of several definitions."""
    found = symbol_definitions(lines, symbol, path)
    if not found:
        raise ExcerptError('%s: no definition of "%s" found: check the name (Class::Function) and the file' % (path, symbol))
    if overload is not None:
        if not 1 <= overload <= len(found):
            raise ExcerptError('%s: overload="%d", but "%s" has %d definition%s' % (path, overload, symbol, len(found), '' if len(found) == 1 else 's'))
        first, last = found[overload - 1]
        return first + 1, last + 1
    if len(found) > 1:
        raise ExcerptError('%s: "%s" has %d definitions (lines %s): add overload="<n>" to choose one' % (
            path, symbol, len(found), ', '.join(str(first + 1) for first, _ in found)))
    first, last = found[0]
    return first + 1, last + 1


def find_command(lines, name, path):
    """(first, last) line numbers (1-based) of the Register( call that holds "<name>",."""
    needle = '"%s",' % name
    found = []
    for index, line in enumerate(lines):
        if needle not in line:
            continue
        # The Register( call around it: on this line or on one of the few lines above (a call may open first).
        for opening in range(index, max(-1, index - 3), -1):
            column = lines[opening].rfind('Register(') if opening != index else lines[opening].rfind('Register(', 0, line.index(needle))
            if column >= 0:
                end = call_end(lines, opening, column + len('Register'))
                if end is not None and end >= index:
                    found.append((opening + 1, end + 1))
                break
    if not found:
        raise ExcerptError('%s: no Register( call holds "%s",: check the command\'s name and the file that registers it' % (path, name))
    if len(found) > 1:
        raise ExcerptError('%s: %d Register( calls hold "%s", (lines %s): quote the lines with src="<path>#L<first>-L<last>"' % (
            path, len(found), name, ', '.join(str(first) for first, _ in found)))
    return found[0]


def narrow(lines, first, last, start_text, end_text, path, what):
    """(first, last) of the lines from the one inside first..last that contains start_text to the first later line that
    contains end_text; each text must occur exactly once in the range."""
    inside = lines[first - 1:last]
    for label, text in (('from', start_text), ('to', end_text)):
        count = sum(line.count(text) for line in inside)
        if count != 1:
            raise ExcerptError('%s: %s="%s" occurs %d times inside %s (lines %d-%d); it must occur exactly once: write more of the line' % (
                path, label, text, count, what, first, last))
    begin = next(index for index, line in enumerate(inside) if start_text in line)
    finish = next((index for index in range(begin, len(inside)) if end_text in inside[index]), None)
    if finish is None:
        raise ExcerptError('%s: to="%s" does not come after from="%s" inside %s: swap them, or choose other texts' % (path, end_text, start_text, what))
    return first + begin, first + finish


def anchor_lines(lines, attributes, path, symbol=None):
    """The (first, last) the anchor attributes of a quote choose in lines: symbol (or command), from and to, overload."""
    symbol = symbol or attributes.get('symbol')
    overload = attributes.get('overload')
    if overload is not None:
        if not re.match(r'^[1-9]\d*$', overload):
            raise ExcerptError('overload="%s": the number of the definition in file order, from 1' % overload)
        overload = int(overload)
    if 'command' in attributes:
        if symbol:
            raise ExcerptError('a quote names its lines by a symbol or by a command, not both')
        first, last = find_command(lines, attributes['command'], path)
        what = 'the registration of %s' % attributes['command']
    elif symbol:
        first, last = find_symbol(lines, symbol, path, overload)
        what = 'the definition of %s' % symbol
    else:
        return None
    if ('from' in attributes) != ('to' in attributes):
        raise ExcerptError('from= and to= come together: the first and the last line of the piece to quote')
    if 'from' in attributes:
        first, last = narrow(lines, first, last, attributes['from'], attributes['to'], path, what)
    return first, last


# ---------------------------------------------------------------------------------------------------------------------
# Reading sources at a pin.

def patch_hunk(lines, number):
    """{file, start, count, lines} of the n-th hunk of a unified diff, as src/plugins/excerpts.mjs reads it."""
    file = None
    found = 0
    for index, line in enumerate(lines):
        old = re.match(r'^--- (?:a/(.+)|/dev/null)$', line)
        if old:
            file = old.group(1)
            following = re.match(r'^\+\+\+ (?:b/(.+)|/dev/null)$', lines[index + 1] if index + 1 < len(lines) else '')
            if not file and following:
                file = following.group(1)
            continue
        header = re.match(r'^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@', line)
        if not header:
            continue
        found += 1
        if found != number:
            continue
        body = []
        for inner in range(index + 1, len(lines)):
            if not re.match(r'^[ +\-\\]', lines[inner]) or lines[inner].startswith('--- '):
                break
            body.append(lines[inner])
        if not file:
            raise ExcerptError('hunk %d names no file it changes: write the patch with git diff, which names the file of every hunk' % number)
        return {'file': file, 'start': int(header.group(1)), 'count': 1 if header.group(2) is None else int(header.group(2)), 'lines': body}
    raise ExcerptError('the patch has %d hunk%s, not %d: name a hunk from 1 to %d' % (found, '' if found == 1 else 's', number, found))


class Sources:
    """Reads the files quotes name: the engine and its submodules at a pin, and this repository's files."""

    def __init__(self, layout, engine):
        self.layout = layout
        self.engine = engine
        self.top = {}

    def top_level(self, pin):
        if pin not in self.top:
            self.top[pin] = set(self.engine.tree(pin) or {})
        return self.top[pin]

    def read(self, source, pin):
        """The file's lines, or raises ExcerptError naming what to do."""
        if source.namespace == 'book':
            path = os.path.join(self.layout.root, *source.path.split('/'))
            if not os.path.isfile(path):
                raise ExcerptError('book:%s does not exist in this repository: correct the path, or write the file' % source.path)
            return repo.read_text(path).rstrip('\n').split('\n')
        if source.namespace == 'vendor':
            folder = 'Strata/vendor/' + source.lib
            commit = self.engine.gitlink(pin, folder)
            if not commit:
                raise ExcerptError('vendor:%s: %s is not a submodule of the engine at %s (the libraries are the folders of '
                                   'Strata/vendor that are submodules)' % (source.lib, folder, pin[:8]))
            submodule = self.engine.submodule(folder)
            try:
                lines = submodule.read(commit, source.path)
            except repo.EngineError as error:
                raise ExcerptError('vendor:%s: %s; run git submodule update --init --recursive --depth 1 in the clone' % (source.lib, error))
            if lines is None:
                if submodule.object(commit, '') is None:
                    raise ExcerptError('the clone\'s checkout of %s lacks its commit %s: run git submodule update --init '
                                       '--recursive --depth 1 in the clone (pipelines.md §1.3)' % (folder, commit[:12]))
                raise ExcerptError('%s does not exist in %s at %s (the commit the pin records): correct the path inside the library' % (source.path, folder, commit[:12]))
            return lines
        first = source.path.split('/')[0]
        if first not in self.top_level(pin):
            raise ExcerptError('%s: "%s" is no top-level entry of the engine at %s; other sources are vendor:<lib>/<path> and '
                               'book:<path>' % (source.path, first, pin[:8]))
        inside = self.engine.submodule_of(pin, source.path)
        if inside:
            raise ExcerptError('%s is inside the submodule %s: quote it as vendor:%s/%s' % (source.path, inside[0], inside[0].split('/')[-1], inside[1]))
        lines = self.engine.read(pin, source.path)
        if lines is None:
            hint = ''
            if self.engine.read(pin, source.path + '.in') is not None:
                hint = ': it exists only in builds, made from %s.in; quote that' % source.path
            raise ExcerptError('%s does not exist in the engine at %s%s' % (source.path, pin[:8], hint or ': correct the path (git ls-tree -r %s)' % pin[:12]))
        return lines

    def exists(self, pin, path):
        """True when an engine path (a file or a folder) exists at the pin, also inside a submodule."""
        if self.engine.exists(pin, path):
            return True
        inside = self.engine.submodule_of(pin, path)
        if not inside:
            return False
        commit = self.engine.gitlink(pin, inside[0])
        try:
            return self.engine.submodule(inside[0]).exists(commit, inside[1])
        except repo.EngineError:
            return False


def quoted_lines(sources, source, attributes, pin):
    """(first, last, body) of a quote at the pin: the lines its src names or its anchor finds, normalized."""
    lines = sources.read(source, pin)
    if source.hunk is not None:
        hunk = patch_hunk(lines, source.hunk)
        return None, None, hunk['lines']
    if source.start is not None:
        first, last = source.start, source.end
    else:
        found = anchor_lines(lines, attributes, source.label(), source.symbol)
        if found is None:
            raise ExcerptError('src="%s" names no lines: write #L<first>-L<last>, or a draft form, and run fill' % source.label())
        first, last = found
    if last > len(lines):
        raise ExcerptError('%s has %d lines; the quote names L%d-L%d: write its draft form again and run fill' % (source.prefix, len(lines), first, last))
    return first, last, normalize(lines[first - 1:last])


# ---------------------------------------------------------------------------------------------------------------------
# fill and check.

def fill_text(text, sources, pin):
    """(new text, number of quotes changed, problems as (line, message))."""
    problems = []
    changed = 0
    for fence, source in reversed(quotes(text)):
        if isinstance(source, ExcerptError):
            problems.append((fence.open_line, str(source)))
            continue
        try:
            first, last, body = quoted_lines(sources, source, fence.attributes, pin)
        except ExcerptError as error:
            problems.append((fence.open_line, '%s; the quote is left as it is' % error))
            continue
        info = fence.info
        if first is not None:
            if last - first + 1 > c_MaxLines:
                problems.append((fence.open_line, 'the quote %s would hold %d lines (at most %d): choose a smaller piece with '
                                 'from= and to=, or quote lines' % (source.with_lines(first, last), last - first + 1, c_MaxLines)))
                continue
            info = set_attribute(info, 'src', source.with_lines(first, last))
            if source.symbol:
                info = set_attribute(info, 'symbol', source.symbol)
        if body == fence.body and info == fence.info:
            continue
        if body != fence.body:
            text = markdown.replace_fence_body(text, fence, body)
        if info != fence.info:
            text = markdown.replace_fence_info(text, fence, info)
        changed += 1
    return text, changed, problems


def marker_problems(fence, source):
    """The markers of Expressive Code that a quote refuses (§3.1), as messages."""
    problems = []
    for flag in fence.flags:
        if flag.startswith('{'):
            problems.append('Expressive Code\'s line markers (%s) count the block\'s lines: mark the file\'s lines with '
                            'mark="L<n>"' % flag)
    for name in c_RefusedAttributes:
        if name in fence.attributes:
            problems.append('%s= is not used on a quote: the header names the file and its lines' % name)
    if 'mark' in fence.attributes:
        ranges = parse_marks(fence.attributes['mark'])
        if ranges is None:
            problems.append('mark="%s" is not the file\'s lines: write mark="L<n>,L<a>-L<b>"' % fence.attributes['mark'])
        elif source is not None and source.start is not None:
            outside = [(a, b) for a, b in ranges if a < source.start or b > source.end or b < a]
            if outside:
                problems.append('mark="%s" names lines outside the quote L%d-L%d: mark only quoted lines' % (fence.attributes['mark'], source.start, source.end))
        elif source is not None and source.hunk is not None:
            problems.append('a hunk of a patch shows its changes with "+" and "-": remove mark')
    return problems


class Vendors:
    """The engine's ThirdPartyNotices.md at the pin, read once: {repository URL: (name, version, license)}."""

    def __init__(self, engine, pin):
        self.engine = engine
        self.pin = pin
        self.libraries = {}
        for line in engine.read(pin, 'ThirdPartyNotices.md') or []:
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')] if line.startswith('|') else []
            link = re.match(r'^\[([^\]]+)\]\((https?://[^)]+)\)', cells[0]) if len(cells) >= 3 else None
            if link:
                self.libraries[normal_url(link.group(2))] = (link.group(1), cells[1], cells[2].split(' (')[0].strip())
        self.urls = engine.submodule_urls(pin)

    def library(self, lib):
        """(name, license) of the vendored library, or None when ThirdPartyNotices.md does not list it."""
        found = self.record(lib)
        return (found['name'], found['license']) if found else None

    def record(self, lib):
        """The library's entry of src/generated/vendor.json, or None when ThirdPartyNotices.md does not list it."""
        url = self.urls.get('Strata/vendor/' + lib)
        found = self.libraries.get(normal_url(url)) if url else None
        if not found:
            return None
        name, version, license_id = found
        repository = url.strip().rstrip('/')
        if repository.endswith('.git'):
            repository = repository[:-4]
        return {'name': name, 'version': version, 'license': license_id, 'repository': repository,
                'commit': self.engine.gitlink(self.pin, 'Strata/vendor/' + lib)}


def vendor_path(layout):
    return os.path.join(layout.root, 'src', 'generated', 'vendor.json')


def vendor_text(layout, vendors):
    """What src/generated/vendor.json holds: the version and license id of every library a page quotes with vendor:,
    as ThirdPartyNotices.md records them at the pin, with the library's repository and the commit the pin records for it
    (pipelines.md §3.2; rulings-6, R26). The build reads it for the header of a vendor quote."""
    libraries = {}
    for _, page_path in layout.pages():
        for fence, source in quotes(repo.read_text(page_path)):
            if isinstance(source, Source) and source.namespace == 'vendor' and source.lib not in libraries:
                found = vendors.record(source.lib)
                if found:
                    libraries[source.lib] = found
    return json.dumps({'pin': vendors.pin, 'libraries': {lib: libraries[lib] for lib in sorted(libraries)}}, indent='\t', ensure_ascii=False) + '\n'


def vendor_problem(layout, vendors):
    """A message when the committed src/generated/vendor.json is not what fill writes, else None."""
    expected = vendor_text(layout, vendors)
    path = vendor_path(layout)
    current = repo.read_text(path) if os.path.isfile(path) else None
    if current == expected or (current is None and not json.loads(expected)['libraries']):
        return None
    return '%s is %s: run python -I tools/excerpts.py fill (the build reads it for the headers of vendor: quotes)' % (
        layout.relative(path), 'missing' if current is None else 'stale')


def normal_url(url):
    url = url.strip().lower().rstrip('/')
    return url[:-4] if url.endswith('.git') else url


def credits_problem(layout, lib, library, release):
    """('error' or 'note', message) when appendix/credits does not name the library with its license on one line, else
    None. While the page is not written the check is a note, and an error in a release."""
    path = os.path.join(layout.docs, *c_Credits.split('/')) + '.md'
    if not os.path.isfile(path):
        if release:
            return ('error', 'vendor:%s: %s is not written, and a release needs it to credit %s (%s) (pipelines.md §3.2)'
                    % (lib, c_Credits, library[0], library[1]))
        return ('note', 'vendor:%s: %s is not written yet, so the credit of %s (%s) is not checked' % (lib, c_Credits, library[0], library[1]))
    name, license_id = library
    for line in repo.read_text(path).split('\n'):
        folded = line.lower()
        if (name.lower() in folded or lib.lower() in folded) and license_id.lower() in folded:
            return None
    return ('error', 'vendor:%s: %s does not name %s with its license %s on one line (pipelines.md §3.2): add its credit there'
            % (lib, c_Credits, name, license_id))


def engine_paths(text, top_level):
    """(line, path) of the engine paths named in backticks in the prose: the first part is a top-level entry."""
    found = []
    for number, line in markdown.prose_lines(text):
        for match in c_InlineCode.finditer(line):
            value = c_PathSuffix.sub('', match.group(2).strip())
            if '/' not in value or ' ' in value or value.startswith(('/', './', 'book:', 'vendor:')):
                continue
            if value.split('/')[0] in top_level and re.match(r'^[\w.+/-]+$', value):
                found.append((number, value.rstrip('/')))
    return found


def check_text(text, sources, pin, layout, release, vendors):
    """(problems, notes) of one page, each as (line, message)."""
    problems = []
    notes = []
    data = None
    try:
        data, _, _, _ = frontmatter.read(text)
    except frontmatter.FrontmatterError:
        pass  # tools/pages.py check reports front matter that cannot be read
    count = 0
    for fence in markdown.fences(text):
        if not is_quote(fence) and 'mark' in fence.attributes and parse_marks(fence.attributes['mark']) is not None:
            problems.append((fence.open_line, 'mark="L…" names the lines of a quoted file, but this fence has no src='))
        for match in c_QuotedAnchor.finditer(fence.meta if is_quote(fence) else ''):
            if '\\"' in match.group('value') or match.group('after'):
                problems.append((fence.open_line, '%s= holds a double quote: the site\'s Markdown reader ends the attribute at it and '
                                 'refuses the fence; name a part of the line without quotes, such as %s="%s"' % (
                                     match.group('name'), match.group('name'), re.split(r'\\?"', match.group('value'))[0])))
    for fence, source in quotes(text):
        if isinstance(source, ExcerptError):
            problems.append((fence.open_line, str(source)))
            continue
        for message in marker_problems(fence, source):
            problems.append((fence.open_line, message))
        if not source.filled:
            problems.append((fence.open_line, 'the quote is a draft (src="%s"%s): run python -I tools/excerpts.py fill' % (
                fence.attributes['src'], ' command="%s"' % fence.attributes['command'] if 'command' in fence.attributes else '')))
            continue
        count += 1
        if source.namespace == 'vendor':
            library = vendors.library(source.lib)
            if library is None:
                problems.append((fence.open_line, 'vendor:%s: the engine\'s ThirdPartyNotices.md at %s does not list this library, so '
                                 'the book does not quote it (pipelines.md §3.2)' % (source.lib, pin[:8])))
            else:
                found = credits_problem(layout, source.lib, library, release)
                if found:
                    (problems if found[0] == 'error' else notes).append((fence.open_line, found[1]))
        if source.start is not None and source.end - source.start + 1 > c_MaxLines:
            problems.append((fence.open_line, 'the quote holds %d lines; at most %d: quote a smaller piece' % (source.end - source.start + 1, c_MaxLines)))
            continue
        try:
            _, _, expected = quoted_lines(sources, source, {}, pin)
        except ExcerptError as error:
            problems.append((fence.open_line, str(error)))
            continue
        if fence.body != expected:
            first = next((index for index in range(max(len(expected), len(fence.body)))
                          if index >= len(expected) or index >= len(fence.body) or expected[index] != fence.body[index]), 0)
            where = 'line L%d' % (source.start + first) if source.start is not None else 'line %d of hunk %d' % (first + 1, source.hunk)
            problems.append((fence.open_line + 1 + min(first, len(fence.body)), 'the quote differs from %s at %s (%s): the page '
                             'says %r, the source %r; run python -I tools/excerpts.py fill' % (
                                 source.prefix, pin[:8] if source.namespace != 'book' else 'this repository', where,
                                 fence.body[first] if first < len(fence.body) else '<nothing>',
                                 expected[first] if first < len(expected) else '<nothing>')))
        elif source.start is not None and fence.body:
            # The site's build (src/plugins/excerpts.mjs): Expressive Code draws no blank line at a block's start or end, so
            # a blank first line would put every line number one line late and a blank last line would show fewer lines.
            filled = [index for index, line in enumerate(fence.body) if line.strip()]
            if not filled:
                problems.append((fence.open_line, 'src="%s": every line of the quote is blank: quote lines that hold code' % fence.attributes['src']))
            elif filled[0] > 0 or filled[-1] < len(fence.body) - 1:
                starts = filled[0] > 0
                problems.append((fence.open_line, 'src="%s": the quote %s with a blank line, which Expressive Code does not draw, so %s: '
                                 'quote L%d-L%d instead' % (fence.attributes['src'], 'starts' if starts else 'ends',
                                                            'its line numbers and marks would be one line late' if starts
                                                            else 'the page would show fewer lines than src names',
                                                            source.start + filled[0], source.start + filled[-1])))
    if data and data.get('kind') == 'internals' and count < c_MinInternalsQuotes:
        problems.append((1, 'a page of kind internals quotes the engine at least %d times; this one quotes it %d time%s: quote the code the page explains' % (
            c_MinInternalsQuotes, count, '' if count == 1 else 's')))
    for number, path in engine_paths(text, sources.top_level(pin)):
        if not sources.exists(pin, path):
            problems.append((number, '`%s` does not exist in the engine at %s: check the path (git ls-tree -r %s)' % (path, pin[:8], pin[:12])))
    return problems, notes


# ---------------------------------------------------------------------------------------------------------------------
# relocate.

def find_block(haystack, needle):
    """Start indexes (0-based) where the normalized lines `needle` occur in `haystack`."""
    if not needle:
        return []
    first = needle[0].lstrip('\t')
    found = []
    for index in range(len(haystack) - len(needle) + 1):
        if haystack[index].lstrip('\t') == first and normalize(haystack[index:index + len(needle)]) == needle:
            found.append(index)
    return found


def enclosing_definition(lines, start, end):
    """The name of the innermost function whose definition holds lines start..end (1-based), or None."""
    for index in range(end - 1, -1, -1):
        match = re.search(r'([A-Za-z_][\w]*(?:::[~A-Za-z_][\w]*)*)\s*\([^;]*$', lines[index])
        if not match or re.match(r'^\s*(if|while|for|switch|return|else)\b', lines[index]):
            continue
        last = definition_end(lines, index)
        if last is not None and last + 1 >= end:
            return match.group(1)
    return None


def distinctive_line(lines, start, end):
    """The longest line of lines start..end that occurs exactly once in the whole file, or None."""
    counts = {}
    for line in lines:
        counts[line] = counts.get(line, 0) + 1
    candidates = [line for line in lines[start - 1:end] if line.strip() and counts.get(line) == 1]
    return max(candidates, key=lambda line: len(line.strip())) if candidates else None


def grep_files(engine, commit, line):
    """(path, line number) of every line at the commit that contains the text, by git grep -F."""
    result = subprocess.run(['git', '-C', engine.path, 'grep', '-F', '-n', '-I', '--no-color', '-e', line, commit, '--'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode not in (0, 1):
        raise ExcerptError('git grep in %s: %s' % (engine.path, result.stderr.decode('utf-8', 'replace').strip()))
    found = []
    prefix = commit + ':'
    for entry in result.stdout.decode('utf-8', 'replace').splitlines():
        if entry.startswith(prefix):
            entry = entry[len(prefix):]
        path, _, rest = entry.partition(':')
        number, _, _ = rest.partition(':')
        if number.isdigit():
            found.append((path, int(number)))
    return found


def relocate_quote(fence, source, sources, old, new):
    """What became of a quote between two pins: {'status': same|moved|moved-file|changed|missing, ...}. Text is compared
    normalized on both sides, so a quote filled before the normalization of §3.4 is found again as well. A filled body is
    compared as it stands too: normalizing it again can take a tab more (an indented #define that lost its tab no longer
    counts), and such a body would never match."""
    bodies = [fence.body]
    if normalize(fence.body) != fence.body:
        bodies.append(normalize(fence.body))
    body = bodies[0]
    if source.namespace == 'book':
        return {'status': 'same'}
    if source.hunk is not None:
        return {'status': 'same'}
    try:
        new_lines = sources.read(source, new)
    except ExcerptError:
        new_lines = None
    start, end = source.start, source.end
    if new_lines is not None:
        if normalize(new_lines[start - 1:end]) in bodies:
            return {'status': 'same'}
        matches = []
        for candidate in bodies:
            matches = find_block(new_lines, candidate)
            if matches:
                body = candidate
                break
        if matches:
            best = min(matches, key=lambda index: abs(index + 1 - start))
            result = {'status': 'moved', 'start': best + 1, 'end': best + len(body)}
            if len(matches) > 1:
                result['note'] = 'the text occurs %d times; the nearest was taken' % len(matches)
            return result
    try:
        old_lines = sources.read(source, old)
    except ExcerptError:
        old_lines = []
    if source.namespace == 'engine' and old_lines:
        line = distinctive_line(old_lines, start, end)
        offset = old_lines[start - 1:end].index(line) if line is not None else None
        for path, number in grep_files(sources.engine, new, line) if line is not None else []:
            if path == source.path:
                continue
            candidate = sources.engine.read(new, path) or []
            first = number - offset
            if first >= 1 and normalize(candidate[first - 1:first - 1 + len(body)]) in bodies:
                return {'status': 'moved-file', 'path': path, 'start': first, 'end': first + len(body) - 1}
    if new_lines is None:
        return {'status': 'missing', 'reason': '%s does not exist at %s' % (source.prefix, new[:8])}
    anchored = None
    try:
        anchored = anchor_lines(new_lines, fence.attributes, source.prefix)
        name = fence.attributes.get('symbol') or fence.attributes.get('command')
    except ExcerptError:
        anchored = None
    if anchored is None and old_lines and normalize(old_lines[start - 1:end]) in bodies:
        # A quote filled before anchors were kept: the function that held it.
        name = enclosing_definition(old_lines, start, end)
        if name:
            try:
                anchored = find_symbol(new_lines, name, source.path)
            except ExcerptError:
                anchored = None
    if anchored:
        return {'status': 'changed', 'anchor': name, 'start': anchored[0], 'end': anchored[1]}
    return {'status': 'missing', 'reason': 'the quoted text is no longer in %s, and its anchor finds no lines there' % source.prefix}


c_Callout = re.compile(r'^(\s*\d+\.\s+\*\*Lines?\s+)(\d+)(?:(\s*[–—-]\s*)(\d+))?(:\*\*)')


def shift_callouts(text, fence, first, last, delta):
    """The text with the numbered callouts after the fence (up to the next fence or heading) that name lines first..last
    of the quote moved by delta, as its src moved: "1. **Lines 5–10:**" becomes "1. **Lines 7–12:**"."""
    lines = text.split('\n')
    index = fence.close_line  # the line after the closing fence, 0-based
    while index < len(lines) and not lines[index].lstrip().startswith(('```', '~~~')) and not lines[index].startswith('#'):
        match = c_Callout.match(lines[index])
        if match:
            low = int(match.group(2))
            high = int(match.group(4)) if match.group(4) else low
            if first <= low <= high <= last:
                shifted = match.group(1) + str(low + delta)
                if match.group(4):
                    shifted += match.group(3) + str(high + delta)
                lines[index] = shifted + match.group(5) + lines[index][match.end():]
        index += 1
    return '\n'.join(lines)


def relocate_text(text, sources, old, new, write):
    """(new text, report entries as (line, status, message)), in page order."""
    entries = []
    for fence, source in reversed(quotes(text)):
        if isinstance(source, ExcerptError) or not source.filled:
            entries.append((fence.open_line, 'missing', 'not a filled quote: src="%s"; run fill at the old pin first' % fence.attributes.get('src')))
            continue
        result = relocate_quote(fence, source, sources, old, new)
        label = source.label()
        status = result['status']
        if status == 'same':
            entries.append((fence.open_line, 'same', label))
        elif status == 'moved':
            new_src = source.with_lines(result['start'], result['end'])
            entries.append((fence.open_line, 'moved', '%s -> %s%s' % (label, new_src, '; ' + result['note'] if 'note' in result else '')))
            if write:
                info = shift_marks(set_attribute(fence.info, 'src', new_src), result['start'] - source.start)
                text = markdown.replace_fence_info(text, fence, info)
                text = shift_callouts(text, fence, source.start, source.end, result['start'] - source.start)
        elif status == 'moved-file':
            moved = Source('engine', result['path'], start=result['start'], end=result['end'])
            new_src = moved.with_lines(result['start'], result['end'])
            entries.append((fence.open_line, 'moved-file', '%s -> %s: the quote is in another file now; the prose may name the old '
                            'path, so read the page' % (label, new_src)))
            if write:
                info = shift_marks(set_attribute(fence.info, 'src', new_src), result['start'] - source.start)
                text = markdown.replace_fence_info(text, fence, info)
                text = shift_callouts(text, fence, source.start, source.end, result['start'] - source.start)
        elif status == 'changed':
            entries.append((fence.open_line, 'changed', '%s: the text changed; %s is now at L%d-L%d: read the page again, then choose '
                            'the lines and run fill' % (label, result['anchor'], result['start'], result['end'])))
        else:
            entries.append((fence.open_line, 'missing', '%s: %s: find what took its place at the new pin and quote that, or remove the '
                            'quote' % (label, result['reason'])))
    return text, list(reversed(entries))


# ---------------------------------------------------------------------------------------------------------------------
# list.

def quote_keys(text):
    """The (src, anchors) of every quote of a page's text, for list --since."""
    keys = set()
    for fence in markdown.fences(text):
        if is_quote(fence):
            keys.add((fence.attributes['src'],) + tuple(fence.attributes.get(name) for name in c_Anchors))
    return keys


def book_git(layout, *arguments):
    result = subprocess.run(['git', '-C', layout.root] + list(arguments), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode, result.stdout.decode('utf-8', 'replace'), result.stderr.decode('utf-8', 'replace')


def text_at(layout, commit, path):
    code, output, _ = book_git(layout, 'show', '%s:%s' % (commit, layout.relative(path)))
    return output.replace('\r\n', '\n') if code == 0 else None


# ---------------------------------------------------------------------------------------------------------------------

def selected_pages(layout, names):
    pages = layout.pages()
    if not names:
        return pages
    wanted = {os.path.normcase(os.path.abspath(name)) for name in names}
    ids = {repo.named_page(name) for name in names}
    chosen = [(page, path) for page, path in pages if os.path.normcase(os.path.abspath(path)) in wanted or page in ids]
    missing = [name for name in names if not any(repo.named_page(name) == page or os.path.normcase(os.path.abspath(name)) == os.path.normcase(os.path.abspath(path)) for page, path in pages)]
    if missing:
        raise UsageError('not pages of the book: %s (give page ids such as core/time, or files)' % ', '.join(missing))
    return chosen


def main(argv=None):
    repo.utf8_output()
    parser = argparse.ArgumentParser(description='Fills and checks the book\'s quotes of the engine at the pinned commit (plan/pipelines.md §3).',
                                     epilog=__doc__.split('\n\n', 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['fill', 'check', 'relocate', 'list'])
    parser.add_argument('pages', nargs='*', help='page ids or files (default: every page)')
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--engine', default=repo.c_DefaultEngine, help='the pin clone (default: $STRATA_ENGINE)')
    parser.add_argument('--release', action='store_true', help='check: the credits of vendored libraries must be checkable')
    parser.add_argument('--from', dest='old', help='relocate: the pin the quotes were filled at')
    parser.add_argument('--to', dest='new', help='relocate: the pin to find them at (default: engine.pin\'s)')
    parser.add_argument('--write', action='store_true', help='relocate: update the src of quotes that moved')
    parser.add_argument('--since', help='list: only the quotes whose src or anchor changed since this commit of this repository')
    options = parser.parse_args(argv)
    layout = repo.Layout(options.root)
    engine = None
    try:
        pages = selected_pages(layout, options.pages)
        if options.command == 'list':
            since = None
            if options.since:
                code, resolved, error = book_git(layout, 'rev-parse', '--verify', '--quiet', options.since + '~0')
                if code != 0:
                    raise UsageError('--since %s is not a commit of this repository' % options.since)
                since = resolved.strip()
            for page, path in pages:
                old = quote_keys(text_at(layout, since, path) or '') if since else None
                for fence, _ in quotes(repo.read_text(path)):
                    key = (fence.attributes['src'],) + tuple(fence.attributes.get(name) for name in c_Anchors)
                    if old is None or key not in old:
                        print('%s:%d: %s' % (layout.relative(path), fence.open_line, fence.attributes['src']))
            return 0
        if options.command != 'relocate' and (options.old or options.new or options.write):
            parser.error('--from, --to and --write belong to relocate')
        pin = repo.read_pin(layout.pin_file)
        try:
            engine = repo.Engine(options.engine)
            commit = engine.resolve(pin['commit'])
        except repo.EngineError as error:
            raise UsageError('%s (pipelines.md §1.4, check 1)' % error)
        sources = Sources(layout, engine)
        failures = 0
        if options.command == 'relocate':
            if not options.old:
                parser.error('relocate needs --from <the pin the quotes were filled at>')
            try:
                old = engine.resolve(options.old)
                new = engine.resolve(options.new) if options.new else commit
            except repo.EngineError as error:
                raise UsageError(str(error))
            counts = {}
            for page, path in pages:
                text = repo.read_text(path)
                new_text, entries = relocate_text(text, sources, old, new, options.write)
                for line, status, message in entries:
                    counts[status] = counts.get(status, 0) + 1
                    if status != 'same':
                        print('%s:%d: %s: %s' % (layout.relative(path), line, status, message))
                    if status in ('moved-file', 'changed', 'missing'):
                        failures += 1
                if options.write and new_text != text:
                    repo.write_text(path, new_text)
            print('quotes: %s' % (', '.join('%d %s' % (counts[key], key) for key in sorted(counts)) if counts else 'none'))
            return 1 if failures else 0
        vendors = Vendors(engine, commit)
        if options.command == 'check':
            stale = vendor_problem(layout, vendors)
            if stale:
                print(stale)
                failures += 1
        note_count = 0
        for page, path in pages:
            text = repo.read_text(path)
            if options.command == 'fill':
                new_text, changed, problems = fill_text(text, sources, commit)
                notes = []
                if changed:
                    repo.write_text(path, new_text)
                    print('%s: filled %d quote%s' % (layout.relative(path), changed, '' if changed == 1 else 's'))
            else:
                problems, notes = check_text(text, sources, commit, layout, options.release, vendors)
            for line, message in problems:
                print('%s:%d: %s' % (layout.relative(path), line, message))
            for line, message in notes:
                print('%s:%d: note: %s' % (layout.relative(path), line, message))
            failures += len(problems)
            note_count += len(notes)
        if options.command == 'fill':
            expected = vendor_text(layout, vendors)
            target = vendor_path(layout)
            current = repo.read_text(target) if os.path.isfile(target) else None
            if current != expected and (current is not None or json.loads(expected)['libraries']):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                repo.write_text(target, expected)
                print('%s: written' % layout.relative(target))
        if options.command == 'check':
            print('excerpts: %d problem%s, %d note%s in %d page%s at engine %s' % (
                failures, '' if failures == 1 else 's', note_count, '' if note_count == 1 else 's', len(pages), '' if len(pages) == 1 else 's', commit[:8]))
        return 1 if failures else 0
    except (UsageError, ValueError, OSError) as error:
        print('excerpts: %s' % error, file=sys.stderr)
        return 2
    finally:
        if engine is not None:
            engine.close()


if __name__ == '__main__':
    sys.exit(main())
