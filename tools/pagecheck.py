#!/usr/bin/env python3
"""One page's exit checks in one command (plan/card/checks.md; plan/process.md, "Write and the writer's exit checks"):

    python -I tools/pagecheck.py <page id> [--engine <clone>] [--root <book>] [--fill-sketches]

It runs, for the page src/content/docs/<page id>.md and in this order:
  markterms        tools/markterms.py <page>, which writes into the page the term marks the lint's term-mark rule asks
                   for (rulings-11.md, R53 and R54; never a link); a fill step: what it writes is counted, not failed
  lint             tools/lint.py <page>
  pages            tools/pages.py check (the whole book; only the page's own files count)
  names            tools/names.py check --dumps reference/_dumps/<pin> <page>; without that folder it is skipped with a
                   notice
  excerpts fill    tools/excerpts.py fill <page>, which writes the quotes' lines into the page
  excerpts check   tools/excerpts.py check <page>
  sketches fill    with --fill-sketches only: tools/sketches.py fill <page>, which writes each sketch's file into its
                   fence and each program's output into its output-of fence, with the compiler and PATH the check
                   below uses (so MSYS2's g++ is found here too); without a compiler only the copies are written
  sketches         tools/sketches.py check <page>, when the page has a sketch= or output-of= fence; only the page and
                   its own sketch files (sketches/<part>-<chapter>-*) count, and sketches.py compiles no other page's
                   files for it. Without $CXX and
                   without g++, clang++ or c++ on the PATH, a compiler in the Python interpreter's own folder (MSYS2's
                   mingw64/bin) is used, with that folder first on the child's PATH so that the program it builds runs;
                   without any compiler only the copies are compared (--no-compile), with a notice; without slangc
                   on the PATH, the slangc the engine's build fetched into its per-user cache is passed (--slangc)
  figures          tools/figures.py check (the whole book; only the page's manifest and pictures count), when the page
                   has src/content/figures/<page id>.json
  tutorials        tools/tutorials.py check <page>, when the page has tutorials/<page id>.tutorial.json, or its
                   exercises tutorials/<page id>/exercise-<n>.tutorial.json or .patch; only the page's own tutorial
                   files count, not those of the tutorials its stages start from

A part page (plan/site.md, "Part pages": <part>/index, whose file is src/content/docs/<part>/index.md, and
<part>/review, with generated: index or generated: review) is checked as what it is: the tools take it by the name the
outline's pages have (<part> for the index page, which either name finds), check the part editor's text with the rules
that apply to it (the lint checks its front matter as a part page's and has no size, row or Needs for it), and the
summary says that it is a part page.

--engine is the pin clone: the option, else the STRATA_ENGINE variable, else G:/GameEngineAI/.worktrees/docs-pin when
that folder exists. Every tool reads it at engine.pin's commit.

It prints one compact summary: per check "passed", or its failures grouped by rule id (a tool without rule ids groups
under its own name), each group with its count and at most five lines "file:line: message"; for markterms the count
of what it wrote and the first uses it left for the writer (notes); the lint's warnings as counts; findings of the
whole-book checks in files that are not the page's as counts, not counted. Before the last line it prints, in every
run, "words: <n> prose words; size <S|M|L|XL> holds <a> to <b>": the lint's own count, the one its size rule measures
(rulings-11.md, R54). The last line is "pagecheck: PASS" or "pagecheck: FAIL (<n> failing)", where n counts the
failures and each tool that could not run.

Only the standard library is used. Exit codes: 0 PASS, 1 FAIL, 2 usage errors (no such page, no engine clone).
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import repo  # noqa: E402

c_Tools = os.path.dirname(os.path.abspath(__file__))
c_PinClone = 'G:/GameEngineAI/.worktrees/docs-pin'
c_MaxLines = 5
c_Width = 160  # characters of a shown finding after the first of its group
c_Compilers = ('g++', 'clang++', 'c++')
c_Location = re.compile(r'^(?P<where>[^\s:]+(?::\d+)?): (?P<rest>.*)$')
c_Key = re.compile(r'^(?P<key>[A-Za-z0-9][\w.()\- ]{0,40}?): (?P<message>.*)$')
c_Info = re.compile(r'^(filled \d+ quotes?|filled|written)$')
c_SketchFence = re.compile(r'^\s*(```|~~~).*\b(sketch|output-of)="', re.MULTILINE)
c_Words = re.compile(r'^words: \d+ prose words; ')
c_Generated = re.compile(r'^generated:\s*(index|review)\s*$', re.MULTILINE)


class Line:
    """One line of a tool's output: kind is finding, warning, note, info or summary."""

    def __init__(self, kind, where=None, key=None, message=''):
        self.kind, self.where, self.key, self.message = kind, where, key, message

    @property
    def path(self):
        return self.where.rsplit(':', 1)[0] if self.where and re.search(r':\d+$', self.where) else self.where


def parse_line(text):
    """Reads "<file>:<line>: <rule>: <message>" and the tools' other forms; a line without a file is a summary, and the
    lint's "<file>: words: ..." is the page's prose words."""
    match = c_Location.match(text)
    if not match or not ('/' in match.group('where') or '.' in match.group('where')):
        return Line('summary', message=text)
    where, rest = match.group('where'), match.group('rest')
    if c_Words.match(rest):
        return Line('words', where, None, rest)
    if rest.startswith('note: ') or rest.endswith(' (note)'):
        return Line('note', where, None, rest)
    if c_Info.match(rest):
        return Line('info', where, None, rest)
    kind = 'warning' if rest.endswith('(warning)') else 'finding'
    key, message = None, rest
    keyed = c_Key.match(rest)
    if keyed and len(keyed.group('key').split()) <= 4:
        key, message = keyed.group('key'), keyed.group('message')
        if key.endswith(' (warning)'):
            key, kind = key[:-len(' (warning)')], 'warning'
    return Line(kind, where, key, message)


def page_file(root, named):
    """The page's file for the id a person gives: src/content/docs/<id>.md, or <id>/index.md for a part's index page
    (named <part> or <part>/index); None when there is none."""
    docs = os.path.join(root, 'src', 'content', 'docs')
    for relative in (named + '.md', named + '/index.md'):
        path = os.path.join(docs, *relative.split('/'))
        if os.path.isfile(path):
            return path
    return None


def owned_prefixes(page_id):
    """The files that are the page's own: a whole-book check counts only findings in these."""
    return ('src/content/docs/%s.md' % page_id, 'src/content/docs/%s/index.md' % page_id, 'src/content/figures/%s.json' % page_id,
            'src/assets/figures/%s/' % page_id, 'sketches/%s-' % page_id.replace('/', '-'),
            'tutorials/%s.tutorial.json' % page_id, 'tutorials/%s/' % page_id, 'public/downloads/solutions/%s/' % page_id,
            'plan/notes/%s.md' % page_id)


def is_owned(path, page_id):
    path = (path or '').replace('\\', '/')
    return any(path == prefix or path.startswith(prefix) for prefix in owned_prefixes(page_id))


class Outcome:
    def __init__(self, name):
        self.name = name
        self.groups = {}
        self.warnings = {}
        self.outside = {}
        self.notes = 0
        self.notices = []
        self.skipped = None
        self.fill = False
        self.written = 0
        self.words = None  # the lint's "words: ..." of the page

    @property
    def failing(self):
        return sum(len(lines) for lines in self.groups.values())

    def add(self, key, text):
        self.groups.setdefault(key, []).append(text)


def summarize(name, code, stdout, stderr, page_id, whole_book=False, fill=False):
    """The outcome of one tool's run. A whole-book check counts only the page's own files; a check of the page counts
    everything it prints. An exit code of 2 is a tool that could not run; an exit code of 1 with nothing counted is a
    failure all the same, unless it comes from other files of a whole-book check. A fill step's lines are what it
    wrote: counted, not failures."""
    outcome = Outcome(name)
    outcome.fill = fill
    counted_any = False
    for raw in stdout.splitlines():
        line = parse_line(raw.rstrip())
        if line.kind in ('summary', 'info'):
            continue
        owned = is_owned(line.path, page_id)
        if line.kind == 'words':
            if owned:
                outcome.words = line.message
            continue
        if whole_book and not owned:
            if line.kind in ('finding', 'warning'):
                key = line.key or name
                outcome.outside[key] = outcome.outside.get(key, 0) + 1
            continue
        if line.kind == 'note':
            outcome.notes += 1
        elif fill:
            outcome.written += 1
        elif line.kind == 'warning':
            key = line.key or name
            outcome.warnings[key] = outcome.warnings.get(key, 0) + 1
        else:
            outcome.add(line.key or name, '%s: %s' % (line.where, line.message))
            counted_any = True
    if code == 2:
        messages = [text for text in stderr.splitlines() if text.strip()] or [text for text in stdout.splitlines() if text.strip()][-1:]
        outcome.add('could not run', ' '.join(messages) or '%s exited with code 2' % name)
    elif code not in (0, 1):
        outcome.add('could not run', '%s exited with code %s: %s' % (name, code, ' '.join(stderr.split())[:c_Width]))
    elif code == 1 and not counted_any and not (whole_book and outcome.outside):
        tail = [text for text in (stdout + '\n' + stderr).splitlines() if text.strip()][-1:]
        outcome.add(name, '%s failed: %s' % (name, tail[0] if tail else 'no message'))
    return outcome


def shorten(text, width=c_Width):
    return text if len(text) <= width else text[:width - 1].rstrip() + '…'


def report_lines(outcome):
    """The outcome as the summary prints it."""
    if outcome.skipped:
        return ['%s: skipped: %s' % (outcome.name, outcome.skipped)] + ['  %s' % notice for notice in outcome.notices]
    extras = []
    if outcome.warnings:
        extras.append('%d warning%s' % (sum(outcome.warnings.values()), '' if sum(outcome.warnings.values()) == 1 else 's'))
    if outcome.notes:
        extras.append('%d note%s' % (outcome.notes, '' if outcome.notes == 1 else 's'))
    tail = ', '.join(extras)
    if outcome.failing:
        lines = ['%s: FAIL (%d failing%s)' % (outcome.name, outcome.failing, ', ' + tail if tail else '')]
    elif outcome.fill:
        lines = ['%s: %d written%s' % (outcome.name, outcome.written, ' (%s)' % tail if tail else '')]
    else:
        lines = ['%s: passed%s' % (outcome.name, ' (%s)' % tail if tail else '')]
    for key, found in sorted(outcome.groups.items(), key=lambda item: (-len(item[1]), item[0])):
        lines.append('  %s: %d' % (key, len(found)))
        for index, text in enumerate(found[:c_MaxLines]):
            lines.append('    %s' % (text if index == 0 else shorten(text)))
        if len(found) > c_MaxLines:
            lines.append('    (%d more)' % (len(found) - c_MaxLines))
    if outcome.warnings:
        lines.append('  warnings: %s' % ', '.join('%s %d' % (key, count) for key, count in
                                                  sorted(outcome.warnings.items(), key=lambda item: (-item[1], item[0]))))
    if outcome.outside:
        lines.append('  other files, not counted: %s' % ', '.join('%s %d' % (key, count) for key, count in
                                                                  sorted(outcome.outside.items(), key=lambda item: (-item[1], item[0]))))
    lines.extend('  %s' % notice for notice in outcome.notices)
    return lines


def resolve_engine(option, environ, default=None):
    """--engine, else STRATA_ENGINE, else the default clone (c_PinClone) when that folder exists; None without any."""
    default = c_PinClone if default is None else default
    if option:
        return option
    if environ.get('STRATA_ENGINE'):
        return environ['STRATA_ENGINE']
    return default if default and os.path.isdir(default) else None


def compiler_environment(environ, executable, which=shutil.which):
    """(environment for the sketches' child or None to keep the caller's, notice or None, compile). A C++ compiler in
    the folder of the Python interpreter is used when neither $CXX nor the PATH names one."""
    if environ.get('CXX') or any(which(name) for name in c_Compilers):
        return None, None, True
    folder = os.path.dirname(os.path.abspath(executable))
    for name in c_Compilers:
        for candidate in (os.path.join(folder, name), os.path.join(folder, name + '.exe')):
            if os.path.isfile(candidate):
                child = dict(environ)
                child['PATH'] = folder + os.pathsep + environ.get('PATH', '')
                return child, 'compiled with %s, found beside the Python interpreter' % candidate.replace('\\', '/'), True
    return None, 'not compiled: no C++ compiler (set CXX or put g++ on the PATH); only the copies were compared: report it', False


def slangc_arguments(environ, which=shutil.which):
    """`--slangc <path>` for sketches.py when no slangc is on the PATH: the release the engine's build fetched into its
    per-user cache (CMake/StrataSlang.cmake: STRATA_SLANG_ROOT, else %LOCALAPPDATA%/Strata/Toolchains,
    ~/Library/Caches/Strata/Toolchains or $XDG_CACHE_HOME/strata/toolchains), the newest one found; [] otherwise."""
    if which('slangc'):
        return []
    folders = []
    if environ.get('STRATA_SLANG_ROOT'):
        folders.append(environ['STRATA_SLANG_ROOT'])
    caches = []
    if environ.get('LOCALAPPDATA'):
        caches.append(os.path.join(environ['LOCALAPPDATA'], 'Strata', 'Toolchains'))
    if environ.get('HOME'):
        caches.append(os.path.join(environ['HOME'], 'Library', 'Caches', 'Strata', 'Toolchains'))
        caches.append(os.path.join(environ.get('XDG_CACHE_HOME') or os.path.join(environ['HOME'], '.cache'), 'strata', 'toolchains'))
    for cache in caches:
        if os.path.isdir(cache):
            folders += [os.path.join(cache, name) for name in sorted(os.listdir(cache), reverse=True) if name.startswith('slang-')]
    for folder in folders:
        for name in ('slangc.exe', 'slangc'):
            candidate = os.path.join(folder, 'bin', name)
            if os.path.isfile(candidate):
                return ['--slangc', candidate]
    return []


def run_tool(argv, cwd, env):
    result = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode, result.stdout.decode('utf-8', 'replace'), result.stderr.decode('utf-8', 'replace')


def tutorial_names(root, page_id):
    """The names tutorials.py check takes for the page: the page id when it has a tutorial file, else its exercises."""
    if os.path.isfile(os.path.join(root, 'tutorials', *(page_id + '.tutorial.json').split('/'))):
        return [page_id]
    folder = os.path.join(root, 'tutorials', *page_id.split('/'))
    names = set()
    if os.path.isdir(folder):
        for entry in os.listdir(folder):
            match = re.match(r'^(exercise-\d+)\.(tutorial\.json|patch)$', entry)
            if match:
                names.add('%s/%s' % (page_id, match.group(1)))
    return sorted(names)


def main(argv=None, runner=run_tool, environ=None, executable=None, which=shutil.which):
    repo.utf8_output()
    environ = dict(os.environ if environ is None else environ)
    executable = executable or sys.executable
    parser = argparse.ArgumentParser(description='One page\'s exit checks in one command, with one compact summary.',
                                     epilog=__doc__.split('\n\n', 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('page', help='the page id, such as core/time')
    parser.add_argument('--engine', help='the pin clone (default: STRATA_ENGINE, else %s when it exists)' % c_PinClone)
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--fill-sketches', action='store_true',
                        help='run tools/sketches.py fill on the page, with the compiler the check finds, before the sketches check')
    options = parser.parse_args(argv)
    root = os.path.abspath(options.root or repo.c_Root)
    named = options.page.strip('/').replace('\\', '/')
    if named.endswith('.md'):
        named = named[:-3]
    page_path = page_file(root, named)
    if page_path is None:
        print('pagecheck: there is no page src/content/docs/%s.md' % named, file=sys.stderr)
        return 2
    # The tools name a part's index page (<part>/index.md, id <part>/index) by its URL, <part> (repo.named_page).
    page_id = repo.page_id(os.path.relpath(page_path, os.path.join(root, 'src', 'content', 'docs')))
    engine = resolve_engine(options.engine, environ)
    if not engine:
        print('pagecheck: name the pin clone with --engine <folder> or the STRATA_ENGINE variable', file=sys.stderr)
        return 2
    try:
        pin = repo.read_pin(os.path.join(root, 'engine.pin'))
    except (OSError, ValueError) as error:
        print('pagecheck: %s' % error, file=sys.stderr)
        return 2
    dumps = os.path.join(root, 'reference', '_dumps', pin['commit'])
    dumps_shown = 'reference/_dumps/%s' % pin['commit']
    has_dumps = os.path.isdir(dumps)
    with open(page_path, encoding='utf-8') as file:
        page_text = file.read()

    def tool(name, *arguments):
        return [executable, '-I', os.path.join(c_Tools, name)] + list(arguments)

    common = ['--engine', engine, '--root', root]
    # (name, argv, whole book, environment, reason to skip, notice)
    checks = [
        ('markterms', tool('markterms.py', page_id, '--root', root), False, None, None, None),
        ('lint', tool('lint.py', page_id, *common), True, None, None, None),
        ('pages', tool('pages.py', 'check', '--root', root), True, None, None, None),
        ('names', tool('names.py', 'check', '--dumps', dumps, *common, page_id), False, None,
         None if has_dumps else 'no dumps at %s: the names are not checked; report it' % dumps_shown, None),
        ('excerpts fill', tool('excerpts.py', 'fill', *common, page_id), False, None, None, None),
        ('excerpts check', tool('excerpts.py', 'check', *common, page_id), False, None, None, None),
    ]
    if c_SketchFence.search(page_text):
        child, notice, compile_them = compiler_environment(environ, executable, which)
        no_compile = [] if compile_them else ['--no-compile']
        slangc = slangc_arguments(environ, which) if compile_them else []
        if options.fill_sketches:
            # The same compiler as the check, so that fill runs the programs whose output the page shows.
            checks.append(('sketches fill', tool('sketches.py', 'fill', *no_compile, *slangc, *common, page_id), False, child, None, notice))
        # Counted as a whole-book check: a finding in another page's sketch file is no failure of this page.
        checks.append(('sketches', tool('sketches.py', 'check', *no_compile, *slangc, *common, page_id), True, child, None, notice))
    if os.path.isfile(os.path.join(root, 'src', 'content', 'figures', *(page_id + '.json').split('/'))):
        checks.append(('figures', tool('figures.py', 'check', '--dumps', dumps, *common), True, None,
                       None if has_dumps else 'no dumps at %s; report it' % dumps_shown, None))
    names = tutorial_names(root, page_id)
    if names:
        # Counted as a whole-book check: the tutorial a stage starts from is another page's, and so are its findings.
        checks.append(('tutorials', tool('tutorials.py', 'check', '--dumps', dumps, *common, *names), True, None,
                       None if has_dumps else 'no dumps at %s; report it' % dumps_shown, None))

    generated = c_Generated.search(page_text)
    print('pagecheck %s (engine %s, pin %s)' % (page_id, engine.replace('\\', '/'), pin['commit'][:8]))
    if generated:
        # plan/site.md, "Part pages": the build draws the generated part; the tools check what the part editor wrote.
        print('a part page (generated: %s): the checks read the part editor\'s text; the build draws the rest, and the '
              'page has no row, no size and no Needs' % generated.group(1))
    failing = 0
    words = None
    for name, command, whole_book, child, skip, notice in checks:
        if skip:
            outcome = Outcome(name)
            outcome.skipped = skip
        else:
            code, stdout, stderr = runner(command, root, child if child is not None else environ)
            outcome = summarize(name, code, stdout, stderr, page_id, whole_book, fill=name == 'markterms')
            failing += outcome.failing
            if name == 'lint':
                words = outcome.words
        if notice:
            outcome.notices.append(notice)
        for line in report_lines(outcome):
            print(line)
    print(words or 'words: not counted: the lint did not report the page\'s prose words')
    print('pagecheck: PASS' if failing == 0 else 'pagecheck: FAIL (%d failing)' % failing)
    return 0 if failing == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
