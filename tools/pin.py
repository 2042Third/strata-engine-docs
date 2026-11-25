#!/usr/bin/env python3
"""The engine commit the book is checked against (engine.pin) and what moving it changes (plan/pipelines.md §10).

    python -I tools/pin.py show
    python -I tools/pin.py report --engine <clone> [--to <commit>] [--dumps-to reference/_dumps/<new pin>]
    python -I tools/pin.py move   --engine <clone> <commit> [--release <x.y.z>] [--prerelease yes|no]

report prints, per chapter and for the whole book (§10.2):
  1. quotes: same, moved (move updates them), moved-file, changed, missing (tools/excerpts.py relocate);
  2. tutorials to run again: every tutorial (tutorials/<part>/<chapter>.tutorial.json) whose stamp has no passing run at
     the new pin, and the patch tutorials and engine exercises whose patch no longer applies there: each patch after the
     patches its chain applies before it, in order, as tutorials.py patch applies them (git apply --cached on the new
     pin's tree, in an index file and an object folder of their own: the clone is not touched);
  3. pictures to take again: every figure stamped at another commit; and every figure whose recipe reuses a shot whose
     Setup, Scene, AntiAliasing or DebugView changed in Tools/LookDev/Shots.json, and every shot a recipe uses that
     names entities by ID;
  4. the pages marked W8 or W8r in the outline, each with the "## Movable claims" of plan/notes/<part>/<chapter>.md; a
     written W8 or W8r page whose notes lack that section fails the report;
  5. with --dumps-to: the pages whose prose numbers may be stale: every page that links a reference page that includes a
     table whose dump or parsed table differs between the old pin's dumps and --dumps-to (a table from <name>.json is
     src/generated/reference/<name>.md, or <name>-<group>.md when split), with each number of its prose;
  6. the engine files the tools depend on that changed (Tools/PerfLock.py among them: a moved lock no longer keeps the
     runs apart);
  7. text figures to take again.
Without --to it reports against the pin itself, which shows what is out of date now. The exit code is 1 when anything
needs a person (a quote moved-file, changed or missing; a patch that no longer applies; a W8 or W8r page without its
movable claims; a reused shot that changed or names entities by ID; an engine file the tools depend on that changed),
0 otherwise; the runs to do (tutorials, pictures, text figures) are listed either way.

move runs relocate --write, writes engine.pin (its header is always the current one), and exits 1 when anything needs a
person, so that the move is not mistaken for a finished one. After a move, in this order: the pin build, reference.py
dump, parse and render, names.py check and excerpts.py check on every page, tutorials.py run, and in phase B
figures.py take, compare and publish.

--engine is the pin clone (default: $STRATA_ENGINE). Commits are resolved with "<name>~0" (never the brace form). Only
the standard library is used. Exit codes: 0 nothing needs a person, 1 something does, 2 usage or environment errors.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import excerpts  # noqa: E402
import figures  # noqa: E402
import tutorials  # noqa: E402
from booklib import markdown, outline as outline_rules, repo  # noqa: E402

c_ToolFiles = ('Tools/PerfLock.py', 'Tools/LookDev.py', 'Tools/LookDev/Shots.json', 'Tools/LookDev/LookDevScene.json',
               'Tools/GenerateShowcaseTerrain.py', 'CMake/StrataSlang.cmake', 'Strata/vendor/glm', 'ThirdPartyNotices.md',
               'StrataEditor/src/Editor/EditorCommandRunner.h', 'StrataTests/src/FeatureTest/SDKReader.h')
c_ShotFields = ('Setup', 'Scene', 'AntiAliasing', 'DebugView')
c_EntityId = re.compile(r'^[0-9A-F]{16}$')
c_MovableClaims = '## Movable claims'


class UsageError(Exception):
    pass


class Report:
    def __init__(self):
        self.pages = {}
        self.book = []
        self.person = 0
        self.runs = 0

    def page(self, page, line):
        self.pages.setdefault(page, []).append(line)

    def add(self, line, person=False, run=False, page=None):
        (self.pages.setdefault(page, []) if page else self.book).append(line)
        self.person += 1 if person else 0
        self.runs += 1 if run else 0


def tutorial_files(layout):
    return sorted(glob.glob(os.path.join(layout.tutorials, '**', '*.tutorial.json'), recursive=True))


def stamp_current(path, commit):
    """True when the tutorial's stamp has a passing run at the commit."""
    stamp = path[:-len('.tutorial.json')] + '.stamp.json'
    if not os.path.isfile(stamp):
        return False
    try:
        with open(stamp, encoding='utf-8') as file:
            data = json.load(file)
    except ValueError:
        return False
    return any(run.get('engineCommit') == commit and run.get('passed') for run in data.get('runs', []) if isinstance(run, dict))


def git_objects(engine):
    """The clone's object folder, absolute, with forward slashes."""
    found = subprocess.run(['git', '-C', engine.path, 'rev-parse', '--git-common-dir'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if found.returncode != 0:
        raise UsageError('git rev-parse --git-common-dir in %s: %s' % (engine.path, found.stderr.decode('utf-8', 'replace').strip()))
    common = found.stdout.decode('utf-8', 'replace').strip()
    return (common if os.path.isabs(common) else os.path.join(engine.path, common)).replace('\\', '/') + '/objects'


def chain_applies(engine, commit, patches):
    """(None, '') when the patches apply one after the other to the commit's tree, as tutorials.py patch applies a
    chain; else (the first that does not, git's message). They go into an index file and an object folder of their own,
    which read the clone's objects as alternates (a quoted path: a drive's colon is no separator), so the clone's index,
    working tree and objects are not touched."""
    with tempfile.TemporaryDirectory(prefix='pin-index-') as folder:
        env = dict(os.environ)
        env['GIT_INDEX_FILE'] = os.path.join(folder, 'index')
        env['GIT_OBJECT_DIRECTORY'] = os.path.join(folder, 'objects')
        env['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = '"%s"' % git_objects(engine)
        os.makedirs(env['GIT_OBJECT_DIRECTORY'])
        read = subprocess.run(['git', '-C', engine.path, 'read-tree', commit + '~0'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if read.returncode != 0:
            raise UsageError('git read-tree %s: %s' % (commit[:12], read.stderr.decode('utf-8', 'replace').strip()))
        for patch in patches:
            applied = subprocess.run(['git', '-C', engine.path, 'apply', '--cached', patch.replace('\\', '/')], env=env, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            if applied.returncode != 0:
                return patch, applied.stderr.decode('utf-8', 'replace').strip()
    return None, ''


def report_patches(layout, engine, new, report):
    """Every patch tutorial's and engine exercise's patch, applied after its chain (tutorials.py's PatchItem); a chain that
    breaks at an earlier patch reports that patch once (at its own tutorial) and the later ones as not checked."""
    book = tutorials.Book(layout)
    chains = []
    for item in book.tutorials + book.exercise_patches:
        exercise = isinstance(item, tutorials.ExercisePatch)
        if not exercise and (item.error is not None or not item.patch or not isinstance(item.patch.get('file'), str)):
            continue
        try:
            chains.append((item, tutorials.PatchItem(book, item).patches))
        except tutorials.ChainError as error:
            report.add('the chain of its patch is broken (%s): tutorials.py check reports it' % error.message, person=True, page=item.relative)
    failed = {}
    # The shorter chains first, so that a patch is applied at its own tutorial before the chains that build on it.
    for item, chain in sorted(chains, key=lambda pair: (len(pair[1]), pair[0].relative)):
        own = chain[-1]
        broken = next((patch for patch in chain[:-1] if patch in failed), None)
        if broken is None:
            patch, why = chain_applies(engine, new, [os.path.join(layout.root, *relative.split('/')) for relative in chain])
            if patch is not None:
                broken = layout.relative(patch)
                failed[broken] = why
                if broken == own:
                    before = chain[:-1]
                    report.add('the patch %s no longer applies at %s%s (%s): make it again against the new pin' % (
                        own, new[:12], ' after %s' % ', '.join(before) if before else '', why.splitlines()[0] if why else 'git apply failed'),
                        person=True, page=item.relative)
                    continue
                report.add('the patch %s no longer applies at %s (%s): make it again against the new pin' % (
                    broken, new[:12], why.splitlines()[0] if why else 'git apply failed'), person=True, page=broken)
        if broken is not None:
            report.add('the patch %s is not checked: %s, which its chain applies before it, no longer applies' % (own, broken), page=item.relative)


def shots_at(engine, commit):
    data = figures.json_lines(engine, commit, 'Tools/LookDev/Shots.json') or {}
    return {shot.get('Name'): shot for shot in data.get('Shots', []) if isinstance(shot, dict)}


def names_entities_by_id(shot):
    for step in shot.get('Setup', []) or []:
        for _, value in figures.walk_strings((step or {}).get('Parameters')):
            if c_EntityId.match(value):
                return True
    return False


def movable_claims(layout, page):
    """The lines of the "## Movable claims" section of the page's notes, or None when the notes lack it."""
    path = os.path.join(layout.root, 'plan', 'notes', *page.split('/')) + '.md'
    if not os.path.isfile(path):
        return None
    lines = repo.read_text(path).split('\n')
    for index, line in enumerate(lines):
        if line.strip() == c_MovableClaims:
            claims = []
            for following in lines[index + 1:]:
                if following.startswith('## '):
                    break
                if following.strip():
                    claims.append(following.strip())
            return claims
    return None


def dump_files(folder):
    """{name: result} of every dump and parsed table of a dumps folder ("commands", "parsed/macros")."""
    found = {}
    for path in glob.glob(os.path.join(folder, '*.json')) + glob.glob(os.path.join(folder, 'parsed', '*.json')):
        name = os.path.relpath(path, folder).replace(os.sep, '/')[:-5]
        with open(path, encoding='utf-8') as file:
            data = json.load(file)
        if isinstance(data, dict):
            data = {key: value for key, value in data.items() if key not in ('pin', 'engineCommit')}
        found[name] = data
    return found


def table_name(dump):
    return dump.split('/')[-1]


def stale_numbers(layout, old_dumps, new_dumps, report):
    if not os.path.isdir(new_dumps):
        raise UsageError('--dumps-to %s does not exist: run tools/reference.py dump and parse at the new pin first' % new_dumps)
    if not os.path.isdir(old_dumps):
        report.add('5. prose numbers: not compared: the old pin has no dumps at %s: read the numbers of the pages that link the '
                   'reference against the new tables' % layout.relative(old_dumps), person=True)
        return
    old, new = dump_files(old_dumps), dump_files(new_dumps)
    changed = sorted({table_name(name) for name in set(old) | set(new) if old.get(name) != new.get(name)})
    if not changed:
        report.add('5. prose numbers: no dump or parsed table changed')
        return
    pages = dict(layout.pages())
    including = set()
    for page, path in pages.items():
        if not page.startswith('reference/'):
            continue
        for match in re.finditer(r'::include\{file="([^"]+)\.md"\}', repo.read_text(path)):
            stem = match.group(1)
            if any(stem == name or stem.startswith(name + '-') for name in changed):
                including.add(page)
    report.add('5. prose numbers: the tables %s changed; reference pages that include them: %s' % (
        ', '.join(changed), ', '.join(sorted(including)) or 'none'))
    for page, path in sorted(pages.items()):
        text = repo.read_text(path)
        links = {link_target(page, target) for _, target in re.findall(r'\[([^\]]*)\]\(([^)\s]+)\)', text)}
        if not links & including:
            continue
        for number, line in markdown.prose_lines(text):
            values = re.findall(r'(?<![\w.])\d+(?:[.,]\d+)*(?![\w])', markdown.strip_inline_code(line))
            if values:
                report.add('line %d: %s: check these numbers against the new tables' % (number, ', '.join(values)), person=True, page=layout.relative(path))


def link_target(page, target):
    """The page id a relative link of a page names (../reference/commands.md#x is reference/commands)."""
    target = target.split('#')[0]
    if not target.endswith('.md'):
        return None
    parts = page.split('/')[:-1]
    for part in target[:-3].split('/'):
        if part == '..':
            parts = parts[:-1]
        elif part and part != '.':
            parts.append(part)
    return '/'.join(parts)


def report_move(layout, engine, old, new, write, dumps_to=None, book=outline_rules.c_Book):
    report = Report()
    report.add('pin: from %s to %s' % (old[:12], new[:12]))
    sources = excerpts.Sources(layout, engine)
    counts = {}
    for page, path in layout.pages():
        text = repo.read_text(path)
        new_text, entries = excerpts.relocate_text(text, sources, old, new, write)
        for line, status, message in entries:
            counts[status] = counts.get(status, 0) + 1
            if status != 'same':
                report.add('line %d: %s: %s' % (line, status, message), person=status in ('moved-file', 'changed', 'missing'), page=layout.relative(path))
        if write and new_text != text:
            repo.write_text(path, new_text)
    report.add('1. quotes: %s' % (', '.join('%d %s' % (counts[key], key) for key in sorted(counts)) if counts else 'none'))
    files = tutorial_files(layout)
    to_run = 0
    for path in files:
        relative = layout.relative(path)
        if not stamp_current(path, new):
            to_run += 1
            report.add('tutorial to run again: %s' % relative, run=True, page=relative)
        try:
            with open(path, encoding='utf-8') as file:
                json.load(file)
        except ValueError:
            report.add('not valid JSON: tools/tutorials.py check reports it', person=True, page=relative)
    report_patches(layout, engine, new, report)
    report.add('2. tutorials: %d of %d to run again' % (to_run, len(files)))
    old_shots, new_shots = shots_at(engine, old), shots_at(engine, new)
    to_take = 0
    text_figures = 0
    invalid = set()
    recipes = figures.load_recipes(layout, None, invalid)
    for page in sorted(invalid):
        report.add('the figure manifest fails its schema, so its figures are not listed: run figures.py check', person=True,
                   page='src/content/figures/%s.json' % page)
    for recipe in recipes:
        taken = figures.Taken(layout, recipe.page)
        stamped = [record for record in taken.files.values() if record.get('figure') == recipe.id]
        stale = not stamped or any(record.get('pin') != new and new not in record.get('checkedAt', []) for record in stamped)
        where = recipe.where()
        if recipe.kind == 'text':
            if stale:
                text_figures += 1
                report.add('text figure to take again: %s' % recipe.id, run=True, page=where)
            continue
        if recipe.kind == 'diagram':
            continue
        if stale:
            to_take += 1
            report.add('picture to take again: %s (%s)' % (recipe.id, 'never taken' if not stamped else 'taken at %s' % stamped[0].get('pin', '')[:12]), run=True, page=where)
        shot = recipe.entry.get('shot')
        if shot:
            before, after = old_shots.get(shot), new_shots.get(shot)
            if after is None:
                report.add('%s: the shot %s is gone from Shots.json at %s: choose another shot, or a camera of the recipe\'s own' % (
                    recipe.id, shot, new[:12]), person=True, page=where)
            elif before is not None:
                moved = [field for field in c_ShotFields if before.get(field) != after.get(field)]
                if moved:
                    report.add('%s reuses the shot %s, whose %s changed: judge its picture again' % (recipe.id, shot, ', '.join(moved)), person=True, page=where)
            if after is not None and names_entities_by_id(after):
                report.add('%s reuses the shot %s, which names entities by ID: check that they are the ones meant' % (recipe.id, shot), person=True, page=where)
    report.add('3. pictures: %d to take again and compare (figures.py take, compare, publish)' % to_take)
    pages = dict(layout.pages())
    for mark, ids in (('W8', sorted(book.w8_pages)), ('W8r', sorted(book.w8r_pages))):
        for page in ids:
            claims = movable_claims(layout, page)
            if page not in pages:
                report.add('4. %s %s: not written yet' % (mark, page))
            elif claims is None:
                report.add('4. %s %s: plan/notes/%s.md has no "%s" section: add one line per claim wave 8 can move, with its source'
                           % (mark, page, page, c_MovableClaims), person=True)
            else:
                report.add('4. %s %s: %d movable claim%s: %s' % (mark, page, len(claims), '' if len(claims) == 1 else 's', '; '.join(claims)))
    if dumps_to:
        stale_numbers(layout, os.path.join(layout.root, 'reference', '_dumps', old), os.path.abspath(dumps_to), report)
    changed = []
    for path in c_ToolFiles:
        if tool_file_id(engine, old, path) != tool_file_id(engine, new, path):
            changed.append(path)
    for path in changed:
        report.add('6. %s changed between the pins: read the change before the next run of the tools' % path, person=True)
    if not changed:
        report.add('6. no engine file the tools depend on changed')
    report.add('7. text figures: %d to take again (figures.py take --kinds text)' % text_figures)
    return report


def tool_file_id(engine, commit, path):
    folder, _, name = path.rpartition('/')
    entries = engine.tree(commit, folder) or {}
    entry = entries.get(name)
    return entry[1] if entry else None


def print_report(report):
    for page in sorted(report.pages):
        print('%s:' % page)
        for line in report.pages[page]:
            print('  %s' % line)
    for line in report.book:
        print(line)
    print('pin: %d thing%s need%s a person; %d run%s to do' % (report.person, '' if report.person == 1 else 's', 's' if report.person == 1 else '',
                                                               report.runs, '' if report.runs == 1 else 's'))


def main(argv=None):
    repo.utf8_output()
    parser = argparse.ArgumentParser(description='Shows, reports on and moves the engine commit the book is checked against (plan/pipelines.md §10).',
                                     epilog=__doc__.split('\n\n', 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['show', 'report', 'move'])
    parser.add_argument('commit', nargs='?', help='move: the new commit')
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--engine', default=repo.c_DefaultEngine, help='the pin clone (default: $STRATA_ENGINE)')
    parser.add_argument('--to', help='report: the commit to compare with (default: the pin)')
    parser.add_argument('--dumps-to', help='report: the dumps of the new pin (reference/_dumps/<new pin>)')
    parser.add_argument('--release', help='move: the engine release the new commit belongs to (x.y.z)')
    parser.add_argument('--prerelease', choices=['yes', 'no'], help='move: whether the commit is still before that release\'s tag')
    options = parser.parse_args(argv)
    layout = repo.Layout(options.root)
    engine = None
    try:
        pin = repo.read_pin(layout.pin_file)
        if options.command == 'show':
            if options.commit or options.to or options.release or options.prerelease:
                parser.error('show takes no commit or options')
            print('commit %s\nrelease %s%s\nrepository %s' % (pin['commit'], pin.get('release'), ' (pre-release)' if pin['prerelease'] else '', pin.get('repository')))
            return 0
        if options.release is not None and not re.match(r'^\d+\.\d+\.\d+$', options.release):
            parser.error('--release is x.y.z, such as 0.8.1')
        try:
            engine = repo.Engine(options.engine)
            old = engine.resolve(pin['commit'])
        except repo.EngineError as error:
            raise UsageError('%s (pipelines.md §1.4, check 1)' % error)
        if options.command == 'report':
            if options.commit or options.release or options.prerelease:
                parser.error('report takes --to <commit>, not a commit or --release')
            try:
                new = engine.resolve(options.to) if options.to else old
            except repo.EngineError as error:
                raise UsageError(str(error))
            report = report_move(layout, engine, old, new, False, options.dumps_to)
            print_report(report)
            return 1 if report.person else 0
        if not options.commit:
            parser.error('move needs the new commit')
        if options.to or options.dumps_to:
            parser.error('--to and --dumps-to belong to report')
        try:
            new = engine.resolve(options.commit)
        except repo.EngineError as error:
            raise UsageError(str(error))
        report = report_move(layout, engine, old, new, True)
        repo.write_pin(layout.pin_file, new, options.release, None if options.prerelease is None else options.prerelease == 'yes')
        print_report(report)
        print('pin: engine.pin now names %s' % new)
        return 1 if report.person else 0
    except (UsageError, figures.UsageError, repo.EngineError, ValueError, OSError) as error:
        print('pin: %s' % error, file=sys.stderr)
        return 2
    finally:
        if engine is not None:
            engine.close()


if __name__ == '__main__':
    sys.exit(main())
