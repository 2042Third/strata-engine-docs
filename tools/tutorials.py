#!/usr/bin/env python3
"""The book's tutorials (plan/pipelines.md §6): tutorials/<part>/<chapter>.tutorial.json with their files and worked
solutions, the downloads a reader gets, and the stamps that say a tutorial ran against the engine at the pin.

    python -I tools/tutorials.py check   [--release] --dumps reference/_dumps/<pin> [--engine <clone>] [pages...]
    python -I tools/tutorials.py compile [--engine <clone>] [pages...]
    python <engine>/Tools/PerfLock.py --label docs-tutorials --wait 120 -- python -I tools/tutorials.py run
        --engine <clone> --build <bin> [--package <archive>] [--work <dir>] [--record-examples] [--pictures] [pages...]
    python <engine>/Tools/PerfLock.py --label docs-patch --wait 120 -- python -I tools/tutorials.py patch
        --engine <clone> --build-dir <clone>/build/docs-patch [--work <dir>] [pages...]

pages are page ids: each names the page's tutorial and its exercises (make/first-script), or one exercise
(make/first-script/exercise-1). Without pages a command takes every tutorial of the book. While engine agents work,
PerfLock keeps its default limit of 25 minutes (plan/critique/rulings-5.md, R19), so run and patch take a page or a few
at a time; patch is planned for phase B, when the limit is 180 minutes (--limit 180).

The files (plan/pipelines.md §6.2-6.4, §6.6):
  tutorials/<part>/<chapter>.tutorial.json           a page's tutorial, checked against tools/schemas/tutorial.schema.json
  tutorials/<part>/<chapter>/                        the files its stages copy (book:tutorials/<part>/<chapter>/...)
  tutorials/<part>/<chapter>/exercise-<n>.tutorial.json   an editor exercise's worked solution, in the same format
  tutorials/<part>/<chapter>/exercise-<n>.patch      an engine exercise's worked solution, a diff against the pin
  tutorials/<part>/<chapter>.patch                   a tutorial that changes the engine (its "patch" key names it)
  tutorials/assets/, tutorials/assets/CREDITS.md     assets the tutorials import, and their credits
  tutorials/<part>/<chapter>.stamp.json              the runs of a page's tutorial (an exercise's: exercise-<n>.stamp.json)
  public/downloads/tutorials/<part>/<chapter>/stage-<step>.commands.json   the reader's copy of a stage's commands
  public/downloads/tutorials/<part>/<chapter>/stage-<step>.zip             the project after a stage with "endState"
      (both only for a stage the page offers: one its ::checkpoint names, or a how-to's last, drawn after "## Result")
  public/downloads/tutorials/<part>/<chapter>.patch                        the download of a patch tutorial's patch
  public/downloads/solutions/<part>/<chapter>/exercise-<n>.zip, .patch     the downloads of the worked solutions
  reference/_examples/<command>.json                 {"pin", "command", "parameters", "result"}: run --record-examples

check     Offline: every tutorial against the schema; "page" names the file's page, which exists; a tutorial page has its
          tutorial file, its stages are numbered 1, 2, 3 in order and match the page's ::checkpoint{stage=…}; startsFrom
          names a sample of the dumps or a tutorial that exists, without a loop, and only patch tutorials start from the
          pin or from a patch tutorial; {"tutorial": …, "exercise": n} names an exercise with its exercise-<n>.patch,
          applied after that tutorial's chain, and a file without stages or patch only carries the chain its page's
          engine exercises start from (rulings-9.md, R41); a patch tutorial has no stages, names tutorials/<page>.patch, which is a diff,
          and doctest suites that the pin's tests or its chain's patches declare; a files.from that does not exist, is
          not a file of the tutorial's own folder, of tutorials/assets/ (credited in its CREDITS.md) or of
          Samples/*/Assets/ at the pin; a "to" outside the project; a command the commands dump lacks, parameters that
          do not validate against its schema (a $ref stands for any value), an entityName on a command that takes no
          entity; until on a command that is no Query or without expect; editor.wait in commands; a placeholder or an
          absolute path in commands (but @RELEASE@/Samples/<sample>/Assets/… that asset.import imports); a setup step
          other than asset.import, or a placeholder other than @PROJECT@, @BOOK@, @WORK@ and @RELEASE@; a release file
          that is not at the pin; an asset.import of a file the page does not name; a command's files checked as a
          stage's, and a $ref across a command with files; a $ref to a name the stage has not bound; a
          malformed pointer or check; a step that changes the person's preferences; a reader copy, a patch download or a
          solution download that differs from what compile writes, or a stage download the tutorial no longer makes; a
          zip that holds a CC BY file without its CREDITS.md entry or the CMakePresets.json the editor writes with the
          folders of its machine, a zip over 10 MB, or zips of all tutorials over 150 MB together. Downloads not written
          yet and stamps that are missing or not current are notes in a draft and errors with --release. It needs
          --engine when a tutorial copies an engine file or a stage zip exists (the samples' CREDITS.md are read at the
          pin). Each stage of a tutorial page is an end state ("endState": true), since its checkpoint offers the project
          as a download, unless the tutorial starts from a sample, whose reader has the project (style.md §7.4).
compile   Writes the reader's copies of the stages the pages offer (entityName becomes an entity.find step that binds the
          first match, checks are left out), the patches' downloads and the downloads of the worked solutions an answer
          names (solution="…"), and removes the stage and solution downloads no page links any more.
run       Per tutorial, in a --no-gpu editor (StrataCLI launch --no-gpu --idle-timeout 900, no project; §1.4 check 4):
          makes the project (project.create or project.openSample in @PROJECT@, or the end state of the tutorial it
          starts from, replayed once per run and cached in the work folder by the SHA-256 of the chain's files and the
          pin); per stage copies the files, runs setup with the placeholders filled, saves the edited scene and keeps a
          copy of the project as the stage's start state, then runs each command through StrataCLI call with the
          engine's step rules (bind, $ref, expect, until, which here also asks again after a failing answer) and a
          command's files copied just before it (wait_past_outputs), @RELEASE@ filled with the build's folder, and the book's (entityName matches exactly one entity; checks
          on the full result; contains on an array: one element's text). After a stage with endState it saves the scene
          and zips the project without .strata/ and without the editor's CMakePresets.json, which holds the folders of
          its machine (with a CREDITS.md for its CC BY files; none for a tutorial that starts from a sample); a file of
          the zip that still names a folder of this machine (the work folder, the book, the clone, the build, the
          temporary or the home folder) fails the stage. Then editor.quit {force: true}; every reader copy runs in the
          engine's own runner on its stage's start state (StrataEditor --no-gpu --no-automation --project <copy>
          --commands <reader copy> --quit-after-commands --frames 36000; a tutorial with "automation": true leaves out
          --no-automation, so the editor serves on a free loopback port, its token only in the session folder), part by
          part when commands carry files (copied between the parts), which must exit 0; and the stamp gets the run.
          A start state keeps the project without .strata/ but for the built script module (.strata/Scripts/Bin), which
          the editor loads when it opens a project. --record-examples writes the first passing result of each command,
          with IDs and paths replaced by "…". Tutorials whose commands render (viewport.capture, lighting.bakeProbes)
          need the GPU and are skipped, as are patch tutorials (tutorials.py patch); --pictures (phase B) stops the run
          before it starts (exit 2). A build outside the clone is a release package: name its archive with --package.
patch     Per patch tutorial and engine exercise (phase B, §6.6): §1.4 checks 1 and 2; git apply --check, then git apply,
          for every patch of the chain in order; cmake --preset windows -B <build dir> in the clone (the engine's
          CONFIGURE_DEPENDS globs); cmake --build <build dir> --config Release --parallel 2 --target StrataTests (and
          StrataEditor, StrataRuntime, StrataCLI when the chain changes their folders) -- /p:CL_MPCount=4;
          StrataTests.exe --test-suite=Architecture.Layering and each suite of patch.tests, for an engine exercise its
          page's and those its page's file names for it in "exercises" (a suite that runs no test case fails);
          ctest -R "^StrataTests\\.FeatureTest$"; then git apply -R for every patch in reverse order, the clean check
          of §1.3 and, when the chain adds or removes files, the configure again; and the stamp, with the
          doctest and CTest results. A revert that fails leaves the clone dirty and stops with exit 2.

Every message names the file and the line and says what to do. Only the standard library is used. Exit codes: 0 all
is well, 1 problems were found or a run failed, 2 usage or environment errors (and every preflight check of §1.4).
"""

import argparse
import copy
import hashlib
import json
import os
import platform
import re
import shutil
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import blocks, editor, frontmatter, jsonpos, jsonschema, markdown, repo, steps  # noqa: E402
from booklib import tutorials as files  # noqa: E402

c_RenderingCommands = ('viewport.capture', 'lighting.bakeProbes')
c_SetupCommands = ('asset.import',)
c_ImportSources = ('file', 'files', 'directories')  # asset.import's absolute sources (EditorAssetCommands.cpp:765-767)
c_SlowCommands = ('asset.import', 'script.build', 'project.open', 'project.openSample', 'project.create', 'scene.open',
                  'scene.save', 'world.loadCells', 'project.export')
c_TimeStepSeconds = 2.1  # FAT and exFAT keep modification times in steps of 2 seconds
c_ReaderFrames = 36000
c_ReaderSeconds = 900
c_BuildSeconds = 180 * 60
c_TestSeconds = 60 * 60
c_DefaultSuites = ('Architecture.Layering',)
c_FeatureTest = '^StrataTests\\.FeatureTest$'
c_ProgramFolders = {'StrataEditor/': 'StrataEditor', 'StrataRuntime/': 'StrataRuntime', 'StrataCLI/': 'StrataCLI'}
c_PinBuildFolder = 'build/windows'
c_SampleAsset = re.compile(r'^Samples/[^/]+/Assets/[^/].*[^/]$')
c_Checkpoint = files.c_Checkpoint
c_DoctestSummary = re.compile(r'test cases:\s*(?P<cases>\d+)\s*\|\s*(?P<passed>\d+) passed\s*\|\s*(?P<failed>\d+) failed')
c_DeclaredSuite = re.compile(r'TEST_SUITE(?:_BEGIN)?\s*\(\s*"(?P<name>[^"]+)"')
c_HexId = re.compile(r'^[0-9A-Fa-f]{8,32}$')
c_PathInText = re.compile(r'(?:^|[^A-Za-z0-9])[A-Za-z]:[\\/]|\\\\|^/')
c_Hidden = '…'
c_EditorFailureRemedy = 'correct the step, or the steps before it (the run\'s log holds every call and its answer)'
c_StartFailureRemedy = ('the editor did not start, or did not make or save the project the tutorial starts from: read the run\'s log, '
                        'which holds every call and its answer, and correct what it names')
c_Marker = '.tutorials-run'
c_Tools = os.path.dirname(os.path.abspath(__file__))
c_Schema = os.path.join(c_Tools, 'schemas', 'tutorial.schema.json')


class UsageError(Exception):
    """A usage or environment problem: exit code 2."""


class RunError(Exception):
    """A stage or a run that failed: exit code 1."""


class ChainError(RunError):
    """A startsFrom chain that names a tutorial that does not exist, or loops: where (file:line) and what to do."""

    def __init__(self, where, message):
        super().__init__('%s: %s' % (where, message))
        self.where = where
        self.message = message


class RevertError(Exception):
    """A patch that could not be reverted: the clone stays dirty (exit code 2)."""


class Report:
    def __init__(self, release=False):
        self.release = release
        self.errors = []
        self.notes = []

    def error(self, where, message):
        self.errors.append((where, message))

    def note(self, where, message):
        self.notes.append((where, message))

    def pending(self, where, message):
        """What a draft may still lack and a release may not."""
        (self.error if self.release else self.note)(where, message)


# ---------------------------------------------------------------------------------------------------------------------
# The book's tutorials.

class ExercisePatch:
    """An engine exercise's worked solution, tutorials/<part>/<chapter>/exercise-<n>.patch: run by patch, stamped beside it."""

    def __init__(self, layout, relative, page, number):
        self.layout = layout
        self.relative = relative
        self.page = page
        self.exercise = number
        self.key = '%s/exercise-%d' % (page, number)
        self.patch = {'file': relative, 'tests': []}
        self.data = {'page': page}
        self.stages = []
        self.starts_from = {}

    @property
    def stamp_relative(self):
        return 'tutorials/%s/exercise-%d.stamp.json' % (self.page, self.exercise)

    def where(self, *path):
        return '%s:1' % self.relative


class Book:
    """Every tutorial of the book, by key (the page id, or <page id>/exercise-<n>), and the engine exercises."""

    def __init__(self, layout):
        self.layout = layout
        self.tutorials = files.find_tutorials(layout)
        self.by_key = {tutorial.key: tutorial for tutorial in self.tutorials}
        self.exercise_patches = [ExercisePatch(layout, relative, page, number)
                                 for relative, (page, number) in sorted(files.exercise_patches(layout).items())]
        self.pages = dict(layout.pages())
        self.schema = jsonschema.Validator(read_json(c_Schema))
        self.invalid = set()

    def select(self, names):
        """The tutorials and engine exercises the names ask for (every one without names); UsageError for a name that
        is no page with a tutorial and no exercise."""
        items = self.tutorials + self.exercise_patches
        if not names:
            return items
        unknown = [name for name in names if not any(item.page == name or item.key == name for item in items)]
        if unknown:
            raise UsageError('no tutorial or exercise of the book is named %s: name page ids such as make/first-script, or '
                             'exercises such as make/first-script/exercise-1' % ', '.join(unknown))
        return [item for item in items if item.page in names or item.key in names]

    def validate(self, tutorial, report):
        """The schema and the file's own page (the shape every later step relies on); False when it fails."""
        if tutorial.error is not None:
            report.error('%s:%d' % (tutorial.relative, tutorial.error_line), 'not valid JSON (%s): correct the tutorial file' % tutorial.error)
            self.invalid.add(tutorial.key)
            return False
        problems = self.schema.problems(tutorial.data)
        for pointer, message in problems:
            report.error('%s:%d' % (tutorial.relative, jsonpos.line_of(tutorial.lines, pointer)),
                         '%s %s: write the tutorial as plan/pipelines.md §6.2 gives its keys and forms' % (pointer or 'the tutorial', message))
        if problems:
            self.invalid.add(tutorial.key)
            return False
        if tutorial.data['page'] != tutorial.page:
            report.error(tutorial.where('page'), '"page" is %s, but the file is the tutorial of %s: name the page the file belongs to'
                         % (json.dumps(tutorial.data['page']), tutorial.page))
            self.invalid.add(tutorial.key)
            return False
        return True

    def chain(self, tutorial):
        """The tutorials of a chain, the first one first and the tutorial last; ChainError on a loop or a missing link."""
        found = [tutorial]
        while 'tutorial' in found[-1].starts_from:
            name = found[-1].starts_from['tutorial']
            following = self.by_key.get(name)
            if following is None:
                raise ChainError(found[-1].where('startsFrom', 'tutorial'), 'startsFrom names the tutorial %s, which does not exist: write '
                                 'tutorials/%s.tutorial.json, or start from a template or a sample' % (name, name))
            if following in found:
                raise ChainError(found[-1].where('startsFrom', 'tutorial'), 'startsFrom makes a loop (%s): start one of them from a '
                                 'template or a sample' % ' -> '.join(item.key for item in found + [following]))
            found.append(following)
        return list(reversed(found))

    def changes_engine(self, tutorial):
        """True when the tutorial has its patch or its chain applies one (a file without stages or patch that starts from a
        patch tutorial: patch runs it on the chain's engine); False on a broken chain, which check reports."""
        if tutorial.patch:
            return True
        try:
            return bool(self.chain_patches(tutorial))
        except ChainError:
            return False

    def chain_patches(self, tutorial):
        """The patches a tutorial's chain applies, the first one first: each tutorial's own, and after a tutorial the
        worked solution of the exercise the next one starts from ({"tutorial": …, "exercise": n}, rulings-9.md R41).
        ChainError as chain() raises it."""
        chain = self.chain(tutorial)
        found = []
        for index, item in enumerate(chain):
            if item.patch:
                found.append(item.patch['file'])
            following = chain[index + 1] if index + 1 < len(chain) else None
            if following is not None and following.starts_from.get('exercise') is not None:
                found.append(exercise_patch_relative(item.page, following.starts_from['exercise']))
        return found


def exercise_patch_relative(page, number):
    return 'tutorials/%s/exercise-%d.patch' % (page, number)


def read_json(path):
    with open(path, encoding='utf-8') as file:
        return json.load(file)


def write_bytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as file:
        file.write(data)


def write_json(path, data):
    write_bytes(path, (json.dumps(data, indent='\t', ensure_ascii=False) + '\n').encode('utf-8'))


def book_path(layout, relative):
    return os.path.join(layout.root, *relative.split('/'))


page_kind_and_checkpoints = files.page_kind_and_checkpoints


# ---------------------------------------------------------------------------------------------------------------------
# The dumps check reads (plan/pipelines.md §7.2).

class Dumps:
    def __init__(self, folder, pin):
        if not folder or not os.path.isdir(folder):
            raise UsageError('the dumps folder %s does not exist: name reference/_dumps/<pin> with --dumps, or run python -I '
                             'tools/reference.py dump at the pin (plan/pipelines.md §7.2)' % folder)
        commands = self.load(folder, 'commands.json', pin).get('commands') or []
        self.commands = {entry.get('name'): entry for entry in commands if isinstance(entry, dict)}
        self.samples = [entry.get('id') for entry in self.load(folder, 'samples.json', pin).get('samples') or [] if isinstance(entry, dict)]
        tests = os.path.join(folder, 'parsed', 'tests.json')
        self.suites = set()
        if os.path.isfile(tests):
            data = read_json(tests)
            if data.get('pin') != pin:
                raise UsageError('%s is the table of pin %s, but engine.pin names %s: run python -I tools/reference.py parse at the pin'
                                 % (tests, data.get('pin'), pin))
            self.suites = set(data.get('suites') or [])
        else:
            raise UsageError('%s does not exist: run python -I tools/reference.py parse at the pin' % tests)

    def load(self, folder, name, pin):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            raise UsageError('%s does not exist: run python -I tools/reference.py dump at the pin' % path)
        try:
            data = read_json(path)
        except ValueError as error:
            raise UsageError('%s is not valid JSON (%s): run python -I tools/reference.py dump again' % (path, error))
        if not isinstance(data, dict) or data.get('pin') != pin:
            raise UsageError('%s holds the dump of pin %s, but engine.pin names %s: run python -I tools/reference.py dump at the pin'
                             % (path, data.get('pin') if isinstance(data, dict) else None, pin))
        return data.get('result') or {}


# ---------------------------------------------------------------------------------------------------------------------
# check.

def walk_strings(value, path=()):
    """(path, string) of every string inside a JSON value, keys of objects included."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield path, key
            yield from walk_strings(item, path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, path + (index,))


def is_absolute_path(text):
    return bool(files.c_AbsolutePath.match(text))


def pointer_problem(pointer):
    return None if steps.parse_pointer(pointer) is not None else '%s is not a JSON pointer ("" for the whole result, or "/key/0")' % json.dumps(pointer)


def check_step_form(tutorial, path, step, dumps, bound, report, setup=False):
    """The checks of one command step (setup or commands) that need only the step and the dumps; adds its bindings."""
    where = tutorial.where(*path)
    name = step['command']
    entry = dumps.commands.get(name)
    if name in steps.c_RefusedCommands:
        report.error(where, '%s changes the person\'s preferences, which no tool does (plan/pipelines.md §2): use a project setting' % name)
    if entry is None:
        report.error(tutorial.where(*path, 'command'), 'the commands dump at the pin has no command %s: name a command of '
                     'editor.commands (src/generated/reference/commands-*.md lists them)' % name)
    if not setup and name == 'editor.wait':
        report.error(tutorial.where(*path, 'command'), 'editor.wait counts frames, which differ from machine to machine: count game '
                     'time in fixed steps (play.step {steps}, input.sequence {steps} or until {steps}; plan/pipelines.md §6.2)')
    parameters = step.get('parameters') or {}
    if 'entityName' in step and 'entity' in parameters:
        report.error(tutorial.where(*path, 'parameters', 'entity'), 'the step names its entity twice: keep entityName and drop '
                     '"entity" (entityName passes the entity it finds as "entity")')
    if entry is not None:
        schema = entry.get('parameters') or {'type': 'object'}
        sent = dict(parameters)
        if 'entityName' in step:
            sent['entity'] = '0'
        validator = jsonschema.Validator(schema, accept=steps.is_reference)
        try:
            problems = validator.problems(sent)
        except jsonschema.SchemaError as error:
            problems = []
            report.error(where, 'the parameters of %s cannot be checked: its schema at the pin has %s; teach tools/booklib/jsonschema.py '
                         'that keyword' % (name, error))
        for pointer, message in problems:
            if 'entityName' in step and pointer == '/entity':
                report.error(tutorial.where(*path, 'entityName'), '%s takes no "entity", and entityName passes the entity it finds as '
                             '"entity": drop entityName, or use a command that acts on an entity' % name)
                continue
            report.error(tutorial.where(*(path + ('parameters',) + tuple(jsonpos_path(pointer)))),
                         'parameters%s of %s %s: give the parameters its schema at the pin takes (src/generated/reference/commands-%s.md)'
                         % (pointer, name, message, name.split('.')[0]))
        if 'until' in step and entry.get('kind') != 'Query':
            report.error(tutorial.where(*path, 'until'), 'until repeats a query, and %s is a command of kind %s: wait with a query such '
                         'as play.state or component.get (EditorCommandRunner.h:91-98)' % (name, entry.get('kind')))
    if 'until' in step and not step.get('expect'):
        report.error(tutorial.where(*path, 'until'), 'until repeats the step until its expect holds: give it an expect')
    for pointer in (step.get('expect') or {}):
        problem = pointer_problem(pointer)
        if problem:
            report.error(tutorial.where(*path, 'expect'), 'expect: %s: write a JSON pointer' % problem)
    for check_index, check in enumerate(step.get('checks') or []):
        problem = pointer_problem(check.get('pointer'))
        if problem:
            report.error(tutorial.where(*path, 'checks', check_index), 'checks: %s: write a JSON pointer' % problem)
    names = references_outside_batches(name, parameters)
    for reference in names:
        if reference not in bound:
            report.error(tutorial.where(*path, 'parameters'), '$ref "%s" names no value an earlier step of this stage binds: bind it in '
                         'an earlier step of the same stage, or find the entity again with entityName (plan/pipelines.md §6.2)' % reference)
    for found_path, value in reference_pointers(parameters):
        problem = pointer_problem(value)
        if problem:
            report.error(tutorial.where(*(path + ('parameters',) + found_path)), '$ref pointer: %s: write a JSON pointer' % problem)
    if name == 'editor.batch':
        inner_bound = set()
        for index, inner in enumerate(parameters.get('steps') or []):
            if not isinstance(inner, dict):
                continue
            for reference in steps.references(inner.get('parameters') or {}):
                if reference not in inner_bound:
                    report.error(tutorial.where(*path, 'parameters', 'steps', index), '$ref "%s" names no value an earlier step of '
                                 'this editor.batch binds: a batch\'s steps refer only to what its own steps bind' % reference)
            inner_bound.update((inner.get('bind') or {}).keys())
    for binding, pointer in (step.get('bind') or {}).items():
        problem = pointer_problem(pointer)
        if problem:
            report.error(tutorial.where(*path, 'bind', binding), 'bind %s: %s: write a JSON pointer' % (binding, problem))
        bound.add(binding)


def jsonpos_path(pointer):
    tokens = steps.parse_pointer(pointer) or []
    return [int(token) if token.isdigit() else token for token in tokens]


def references_outside_batches(command, parameters):
    if command == 'editor.batch' and isinstance(parameters, dict):
        parameters = {key: value for key, value in parameters.items() if key != 'steps'}
    return steps.references(parameters)


def reference_pointers(value, path=()):
    """(path, pointer) of every {"$ref", "pointer"} inside a value."""
    if steps.is_reference(value):
        if 'pointer' in value:
            yield path + ('pointer',), value['pointer']
        return
    if isinstance(value, dict):
        for key, item in value.items():
            yield from reference_pointers(item, path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from reference_pointers(item, path + (index,))


def step_values(step):
    """(path, string) of the strings a step sends or compares: its parameters (without the JSON pointers of $ref and of
    an editor.batch's bind and expect), the values its expect and checks compare with, and the text contains looks for.
    Pointers start with "/" and are no paths."""
    def walk(value, path, inside_batch):
        if steps.is_reference(value):
            yield path + ('$ref',), value['$ref']
            return
        if isinstance(value, str):
            yield path, value
        elif isinstance(value, dict):
            for key, item in value.items():
                if inside_batch and key in ('bind', 'expect'):
                    continue
                yield from walk(item, path + (key,), inside_batch)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from walk(item, path + (index,), inside_batch)
    batch = step.get('command') == 'editor.batch'
    yield from walk(step.get('parameters') or {}, ('parameters',), batch)
    for pointer, expectation in (step.get('expect') or {}).items():
        if isinstance(expectation, dict) and 'equals' in expectation:
            yield from walk(expectation['equals'], ('expect', pointer, 'equals'), False)
    for index, check in enumerate(step.get('checks') or []):
        for key in ('contains', 'equals'):
            if isinstance(check, dict) and key in check:
                yield from walk(check[key], ('checks', index, key), False)


def release_import_source(step, found_path, value):
    """Whether a string of a step is a file or folder asset.import imports from the release: "@RELEASE@/…" as file, an
    item of files or an item of directories."""
    return (step.get('command') == 'asset.import' and len(found_path) >= 2 and found_path[0] == 'parameters'
            and found_path[1] in c_ImportSources and value.startswith(files.c_Release + '/') and value.count(files.c_Release) == 1)


def check_placeholders(tutorial, path, step, report, setup):
    """Setup may hold the placeholders the runner fills and absolute paths only through them; commands hold none but
    @RELEASE@ at the start of what asset.import imports from the release, which the page's command imports too."""
    for found_path, value in step_values(step):
        where = tutorial.where(*(path + found_path))
        placeholders = files.c_Placeholder.findall(value)
        if setup:
            for placeholder in placeholders:
                if placeholder not in files.c_Placeholders:
                    report.error(where, '%s is no placeholder of the runner: use @PROJECT@, @BOOK@, @WORK@ or @RELEASE@ (plan/pipelines.md '
                                 '§6.2)' % placeholder)
            if is_absolute_path(value):
                report.error(where, '%s is an absolute path of one machine: start it with @BOOK@ (this repository), @PROJECT@, @WORK@ '
                             'or @RELEASE@' % json.dumps(value))
        else:
            others = [placeholder for placeholder in placeholders if placeholder != files.c_Release]
            if others:
                report.error(where, '%s in commands: placeholders belong in setup (asset.import), which the page shows as a UI step; name '
                             'assets by their path in the project' % ', '.join(others))
            elif placeholders and not release_import_source(step, found_path, value):
                report.error(where, '@RELEASE@ in commands stands only at the start of a file or folder that asset.import imports from the '
                             'release ({"file": "@RELEASE@/Samples/<sample>/Assets/…"}): name assets by their path in the project')
            elif is_absolute_path(value):
                report.error(where, '%s is an absolute path in commands: name assets by their path in the project (plan/pipelines.md §6.2)'
                             % json.dumps(value))


def check_book_file(layout, tutorial, where, relative, credits_text, report):
    """A book: file a tutorial copies or imports: its own folder or tutorials/assets/ (credited), and it exists."""
    own = 'tutorials/%s/' % tutorial.page
    if not (relative.startswith(own) or relative.startswith('tutorials/assets/')):
        report.error(where, 'book:%s is neither a file of the tutorial\'s own folder %s nor of tutorials/assets/: move it there '
                     '(plan/pipelines.md §6.2)' % (relative, own))
        return
    if '..' in relative.split('/') or not os.path.isfile(book_path(layout, relative)):
        report.error(where, '%s does not exist: write the file, or correct the path' % relative)
        return
    if relative.startswith('tutorials/assets/') and relative != 'tutorials/assets/CREDITS.md':
        inside = relative[len('tutorials/assets/'):]
        rows = files.credit_rows(credits_text or '')
        if not any(inside == path.strip('/') or (path.endswith('/') and inside.startswith(path)) for row in rows for path in files.row_paths(row)):
            report.error(where, '%s has no row in tutorials/assets/CREDITS.md: credit it there (Files, Source, Author, License, '
                         'Attribution, Changes) before a tutorial uses it' % relative)


def check_release_sources(tutorial, path, step, engine, pin, report):
    """What asset.import imports from the release (@RELEASE@/…) is a file or folder of Samples/<sample>/Assets/, which
    the release copies from the engine at the pin."""
    if step.get('command') != 'asset.import':
        return
    for found_path, value in walk_strings(step.get('parameters') or {}):
        found_path = ('parameters',) + found_path
        if not release_import_source(step, found_path, value):
            continue
        where = tutorial.where(*(path + found_path))
        relative = value[len(files.c_Release) + 1:].rstrip('/')
        if not c_SampleAsset.match(relative) or '..' in relative.split('/'):
            report.error(where, '%s is no path under the release\'s Samples/<sample>/Assets/: import the release\'s sample assets as '
                         '@RELEASE@/Samples/<sample>/Assets/…, the book\'s own as @BOOK@/tutorials/… (plan/pipelines.md §6.2)' % json.dumps(value))
        elif engine is not None:
            folder = found_path[1] == 'directories'
            found = engine.object(pin, relative)
            if found is None or found[0] != ('tree' if folder else 'blob'):
                kind = 'folder' if folder else 'file'
                report.error(where, 'the release has no %s %s at the pin: name a %s of Samples/<sample>/Assets/ there' % (kind, relative, kind))


def check_copies(layout, tutorial, base, entries, engine, pin, credits_text, report):
    """The files a stage or a command copies: from the tutorial's folder, tutorials/assets/ or a sample's assets at the
    pin, to a path in the project."""
    for file_index, entry in enumerate(entries or []):
        source, target = entry['from'], entry['to']
        where = tutorial.where(*base, 'files', file_index, 'from')
        if source.startswith('book:'):
            check_book_file(layout, tutorial, where, source[len('book:'):], credits_text, report)
        elif not c_SampleAsset.match(source) or '..' in source.split('/'):
            report.error(where, '"%s" is neither book:tutorials/… nor a file under Samples/<sample>/Assets/ at the pin: copy the '
                         'tutorial\'s own files or the release\'s sample assets (plan/pipelines.md §6.2)' % source)
        elif engine is not None:
            found = engine.object(pin, source)
            if found is None or found[0] != 'blob':
                report.error(where, 'the engine has no file %s at the pin: name a file of Samples/<sample>/Assets/ there' % source)
        parts = target.replace('\\', '/').split('/')
        if is_absolute_path(target) or '..' in parts or '' in parts or '.' in parts or parts[0] == '.strata':
            report.error(tutorial.where(*base, 'files', file_index, 'to'), '"%s" is outside the project (or in its .strata/): give a '
                         'path relative to the project, without "..", such as Scripts/Spinner.cpp' % target)


def check_import_named(layout, tutorial, path, step, page_path, page_text, report):
    """Every page names the file it imports (plan/pipelines.md §6.2): the name of each file or folder an asset.import step
    imports appears on the page, which has the reader drag it into the Content Browser."""
    for found_path, value in walk_strings(step.get('parameters') or {}):
        if not found_path or found_path[0] not in c_ImportSources:
            continue
        name = value.replace('\\', '/').rstrip('/').rsplit('/', 1)[-1]
        if not name or files.c_Placeholder.fullmatch(name) or name in page_text:
            continue
        report.error(tutorial.where(*(path + ('parameters',) + found_path)), '%s does not name %s, which this step imports: name the file '
                     'where the page has the reader import it (plan/pipelines.md §6.2)' % (layout.relative(page_path), name))


def check_tutorial(book, tutorial, dumps, engine, pin, report):
    layout = book.layout
    data = tutorial.data
    page_path = book.pages.get(tutorial.page)
    if page_path is None:
        report.error(tutorial.where('page'), 'the page %s does not exist (src/content/docs/%s.md): write the page, or name its id'
                     % (tutorial.page, tutorial.page))
    # An exercise's solution is a download: the files it imports are named by the exercise, not by the page's steps.
    page_text = repo.read_text(page_path) if page_path is not None and tutorial.exercise is None else None
    stages = tutorial.stages
    for index, stage in enumerate(stages):
        if stage['step'] != index + 1:
            report.error(tutorial.where('stages', index, 'step'), 'stage %d of the file has step %d: number the stages 1, 2, 3 in page '
                         'order, as the page\'s ::checkpoint{stage=…} do (plan/pipelines.md §6.2)' % (index + 1, stage['step']))
    if page_path is not None and tutorial.exercise is None and not tutorial.patch:
        kind, checkpoints = page_kind_and_checkpoints(layout, page_path)
        if kind == 'tutorial' or checkpoints:
            written = [stage for _, stage in checkpoints]
            numbers = [stage['step'] for stage in stages]
            if written != numbers:
                line = checkpoints[0][0] if checkpoints else 1
                report.error('%s:%d' % (layout.relative(page_path), line), 'the page\'s checkpoints are stages %s, but %s has the '
                             'stages %s: end each step section with ::checkpoint{stage=N} of its stage' % (
                                 ', '.join(str(item) for item in written) or 'none', tutorial.relative,
                                 ', '.join(str(item) for item in numbers) or 'none'))
            if 'sample' not in tutorial.starts_from:
                for index, stage in enumerate(stages):
                    if stage.get('endState') is not True:
                        report.error(tutorial.where('stages', index), 'stage %d has no "endState": true, but its checkpoint offers the '
                                     'project as it is after the stage as a download (style.md §7.4): give the stage "endState": true'
                                     % stage['step'])
        elif kind == 'how-to' and stages and 'sample' not in tutorial.starts_from and stages[-1].get('endState') is not True:
            # plan/site.md, "Directives"; rulings-9.md, R40 and R42: the build draws a how-to's end state at the end of its
            # "## Result" from the last stage of its tutorial file.
            report.error(tutorial.where('stages', len(stages) - 1), 'the last stage of a how-to\'s tutorial file is its end state, which the '
                         'build offers as a download at the end of "## Result" (plan/site.md): give stage %d "endState": true'
                         % stages[-1]['step'])
    starts = tutorial.starts_from
    if 'sample' in starts and starts['sample'] not in dumps.samples:
        report.error(tutorial.where('startsFrom', 'sample'), 'startsFrom names the sample %s, which project.samples does not list at the '
                     'pin: name one of %s' % (json.dumps(starts['sample']), ', '.join(dumps.samples)))
    earlier = None
    changed_before = False
    if 'tutorial' in starts:
        try:
            chain = book.chain(tutorial)
            earlier = chain[-2]
            changed_before = bool([relative for relative in book.chain_patches(tutorial) if relative != (tutorial.patch or {}).get('file')])
        except ChainError as error:
            report.error(error.where, error.message)
    if starts.get('exercise') is not None:
        relative = exercise_patch_relative(starts.get('tutorial', ''), starts['exercise'])
        if not os.path.isfile(book_path(layout, relative)):
            report.error(tutorial.where('startsFrom', 'exercise'), 'startsFrom names exercise %d of %s, which has no worked solution %s: '
                         'write the exercise\'s patch, or start from the tutorial itself' % (starts['exercise'], starts.get('tutorial'), relative))
    if tutorial.exercise is not None and tutorial.patch:
        report.error(tutorial.where('patch'), 'an editor exercise has no patch: write an engine exercise as tutorials/%s/exercise-%d.patch'
                     % (tutorial.page, tutorial.exercise))
    if 'pin' in starts and not tutorial.patch:
        report.error(tutorial.where('startsFrom'), 'startsFrom {"pin": true} is for tutorials that change the engine: give the tutorial its '
                     '"patch", or start it from a template, a sample or a tutorial')
    check_exercise_suites(book, tutorial, dumps, report)
    if tutorial.patch:
        check_patch_tutorial(book, tutorial, changed_before, dumps, report)
    elif changed_before and (tutorial.stages or starts.get('exercise') is not None):
        # A file without stages or patch only carries the chain its page's engine exercises start from (R41).
        report.error(tutorial.where('startsFrom', 'tutorial'), 'the tutorial %s changes the engine, and the pin build holds no change: '
                     'start this tutorial from a template, a sample or an editor tutorial' % earlier.key)
    credits_path = os.path.join(layout.tutorials, 'assets', 'CREDITS.md')
    credits_text = repo.read_text(credits_path) if os.path.isfile(credits_path) else None
    for stage_index, stage in enumerate(stages):
        base = ('stages', stage_index)
        check_copies(layout, tutorial, base, stage.get('files'), engine, pin, credits_text, report)
        bound = set()
        for step_index, step in enumerate(stage.get('setup') or []):
            path = base + ('setup', step_index)
            if step['command'] not in c_SetupCommands:
                report.error(tutorial.where(*path, 'command'), 'setup holds only asset.import, the one step that needs an absolute path: '
                             'move %s into commands' % step['command'])
            check_placeholders(tutorial, path, step, report, setup=True)
            check_release_sources(tutorial, path, step, engine, pin, report)
            if step['command'] == 'asset.import' and page_text is not None:
                check_import_named(layout, tutorial, path, step, page_path, page_text, report)
            for found_path, value in walk_strings(step.get('parameters') or {}):
                if value.startswith('@BOOK@/'):
                    check_book_file(layout, tutorial, tutorial.where(*(path + ('parameters',) + found_path)), value[len('@BOOK@/'):],
                                    credits_text, report)
            check_step_form(tutorial, path, step, dumps, bound, report, setup=True)
        part_bound = set(bound)  # what the reader's copy has bound in its current part (files.command_segments)
        for step_index, step in enumerate(stage.get('commands') or []):
            path = base + ('commands', step_index)
            if step.get('files'):
                check_copies(layout, tutorial, path, step['files'], engine, pin, credits_text, report)
                part_bound = set()
            for reference in references_outside_batches(step['command'], step.get('parameters') or {}):
                if reference in bound and reference not in part_bound:
                    report.error(tutorial.where(*path, 'parameters'), '$ref "%s" names a value bound before a command that carries files: '
                                 'the reader\'s copy runs the commands between such commands in runs of their own, which keep no bindings: '
                                 'bind it again after the files' % reference)
            check_placeholders(tutorial, path, step, report, setup=False)
            check_release_sources(tutorial, path, step, engine, pin, report)
            if step['command'] == 'asset.import' and page_text is not None:
                check_import_named(layout, tutorial, path, step, page_path, page_text, report)
            check_step_form(tutorial, path, step, dumps, bound, report)
            part_bound.update((step.get('bind') or {}).keys())
        if stage.get('endState') and 'sample' in starts:
            report.note(tutorial.where(*base, 'endState'), 'a tutorial that starts from a sample publishes no zip (the reader has the '
                        'sample); its checkpoint links the stage\'s commands only')


def check_patch_tutorial(book, tutorial, changed_before, dumps, report):
    layout = book.layout
    patch = tutorial.patch
    if tutorial.stages:
        report.error(tutorial.where('stages'), 'a tutorial that changes the engine has no stages: the pin build that runs stages holds '
                     'no change; its page shows the build and test output (style.md §7.4, plan/pipelines.md §6.6)')
    expected = 'tutorials/%s.patch' % tutorial.page
    if patch['file'] != expected:
        report.error(tutorial.where('patch', 'file'), 'the patch of %s is %s: name it %s' % (tutorial.page, patch['file'], expected))
    path = book_path(layout, patch['file'])
    if not os.path.isfile(path):
        report.error(tutorial.where('patch', 'file'), '%s does not exist: write the change as git diff writes it, against the pin' % patch['file'])
        added = set()
    else:
        text = repo.read_text(path)
        if not changed_files(text):
            report.error('%s:1' % patch['file'], 'the patch changes no file: write it as git diff writes it (diff --git a/<path> b/<path>, '
                         'then its hunks), against the pin')
        added = declared_suites(text)
    starts = tutorial.starts_from
    if 'tutorial' in starts:
        try:
            chain = book.chain(tutorial)
            if not changed_before:
                report.error(tutorial.where('startsFrom', 'tutorial'), 'a tutorial that changes the engine starts from the pin or from '
                             'another one that changes it; %s has no patch' % chain[-2].key)
            for relative in book.chain_patches(tutorial):
                item_path = book_path(layout, relative)
                if relative != patch['file'] and os.path.isfile(item_path):
                    added |= declared_suites(repo.read_text(item_path))
        except ChainError:
            pass  # check_tutorial reports the broken chain
    for index, suite in enumerate(patch.get('tests') or []):
        if suite not in dumps.suites and suite not in added:
            report.error(tutorial.where('patch', 'tests', index), 'the doctest suite %s is neither one of the pin\'s tests '
                         '(reference/_dumps/<pin>/parsed/tests.json) nor declared (TEST_SUITE("%s")) by the chain\'s patches: name the '
                         'suite the page names' % (suite, suite))


def check_exercise_suites(book, tutorial, dumps, report):
    """The suites a page's file names for its engine exercises: each exercise has its worked solution, and each suite is the
    pin's or declared by the exercise's chain of patches."""
    if not tutorial.exercises:
        return
    layout = book.layout
    if tutorial.exercise is not None:
        report.error(tutorial.where('exercises'), 'an exercise\'s file names no exercises: name the suites of %s\'s engine exercises '
                     'in tutorials/%s.tutorial.json' % (tutorial.page, tutorial.page))
        return
    added = set()
    try:
        for relative in book.chain_patches(tutorial):
            if os.path.isfile(book_path(layout, relative)):
                added |= declared_suites(repo.read_text(book_path(layout, relative)))
    except ChainError:
        pass  # check_tutorial reports the broken chain
    for number, suites in sorted(tutorial.exercises.items()):
        relative = exercise_patch_relative(tutorial.page, number)
        if not os.path.isfile(book_path(layout, relative)):
            report.error(tutorial.where('exercises', str(number)), 'exercises names exercise %d, which has no worked solution %s: write '
                         'the exercise\'s patch, or drop its entry' % (number, relative))
            continue
        declared = added | declared_suites(repo.read_text(book_path(layout, relative)))
        for index, suite in enumerate(suites):
            if suite not in dumps.suites and suite not in declared:
                report.error(tutorial.where('exercises', str(number), 'tests', index), 'the doctest suite %s is neither one of the pin\'s '
                             'tests (reference/_dumps/<pin>/parsed/tests.json) nor declared (TEST_SUITE("%s")) by the patches of exercise '
                             '%d\'s chain: name the suite the exercise names' % (suite, suite, number))


def adds_or_removes_files(text):
    """Whether a unified diff creates or deletes a file: the engine's CONFIGURE_DEPENDS globs then need a configure."""
    return any(line.split('\t')[0].strip() in ('--- /dev/null', '+++ /dev/null') for line in text.split('\n'))


def changed_files(text):
    """The engine files a unified diff changes (its b/ side, or a/ for a deleted file)."""
    found = []
    for line in text.split('\n'):
        if line.startswith('+++ '):
            target = line[4:].split('\t')[0].strip()
            if target.startswith('b/'):
                found.append(target[2:])
        elif line.startswith('--- '):
            source = line[4:].split('\t')[0].strip()
            if source.startswith('a/'):
                found.append(source[2:])
    return sorted(set(found))


def declared_suites(text):
    """The doctest suites the added lines of a diff declare."""
    return {match.group('name') for line in text.split('\n') if line.startswith('+') and not line.startswith('+++')
            for match in c_DeclaredSuite.finditer(line)}


def zip_problems(layout, relative, credits):
    """Why a published zip breaks the rules (plan/pipelines.md §6.3): over 10 MB, a CC BY file without its credits, or
    the CMakePresets.json the editor writes with its machine's paths."""
    path = book_path(layout, relative)
    problems = []
    size = os.path.getsize(path)
    if size > files.c_ZipLimit:
        problems.append('%s is %.1f MB, over the 10 MB a download may have: leave out what the reader does not need' % (relative, size / 1e6))
    try:
        with zipfile.ZipFile(path) as archive:
            names = [info.filename for info in archive.infolist() if not info.is_dir()]
            members = [(name, archive.read(name)) for name in names if name != 'CREDITS.md']
            credits_text = archive.read('CREDITS.md').decode('utf-8', 'replace') if 'CREDITS.md' in names else ''
    except (zipfile.BadZipFile, OSError) as error:
        return problems + ['%s is not a zip (%s): make it again (tutorials.py run or compile)' % (relative, error)]
    contents = [data for _, data in members]
    for name, data in members:
        if files.editor_presets(name, data):
            problems.append('%s holds %s, the CMakePresets.json the editor writes with the folders of the machine it runs on '
                            '(StrataEditor/src/Editor/ScriptBuild.h:101-103 at the pin), and a reader\'s editor writes their own: '
                            'make the zip again with tutorials.py run, which leaves it out of a stage\'s zip (a worked solution\'s '
                            'zip holds what its stages copy: copy no such file)'
                            % (relative, name))
    for row in credits.rows_for(contents):
        if row not in credits_text:
            problems.append('%s holds a CC BY file, and its CREDITS.md lacks the file\'s row %s: make the zip again (tutorials.py run or '
                            'compile)' % (relative, row.strip()))
    return problems


def download_owner(book, relative):
    """The tutorial line a download comes from: the stage of a stage download, the tutorial of a solution, or None."""
    match = re.match(r'^public/downloads/tutorials/(?P<page>.+)/stage-(?P<step>\d+)\.(?:commands\.json|zip)$', relative)
    if match:
        tutorial = book.by_key.get(match.group('page'))
        if tutorial is not None and tutorial.key not in book.invalid:
            for index, stage in enumerate(tutorial.stages):
                if stage['step'] == int(match.group('step')):
                    return tutorial.where('stages', index)
            return tutorial.where('stages')
    match = re.match(r'^public/downloads/solutions/(?P<page>.+)/exercise-(?P<number>\d+)\.(?:zip|patch)$', relative)
    if match:
        key = '%s/exercise-%s' % (match.group('page'), match.group('number'))
        tutorial = book.by_key.get(key)
        if tutorial is not None:
            return tutorial.where()
        for item in book.exercise_patches:
            if item.key == key:
                return item.where()
    match = re.match(r'^public/downloads/tutorials/(?P<page>.+)\.patch$', relative)
    if match and match.group('page') in book.by_key:
        return book.by_key[match.group('page')].where('patch')
    return None


def check_downloads(book, selected, sources, credits, report):
    """The downloads compile writes, as they are on disk: missing (a draft's note), different (an error), or no longer made."""
    layout = book.layout
    expected = {}
    for item in selected:
        if isinstance(item, ExercisePatch):
            if files.solution_named(layout, item.page, item.relative):
                expected['public/downloads/solutions/%s/exercise-%d.patch' % (item.page, item.exercise)] = files.read_bytes(book_path(layout, item.relative))
            continue
        if item.key in book.invalid or not isinstance(item.data, dict):
            continue
        try:
            expected.update(files.compiled_files(layout, [item], sources, credits))
        except files.SourceError:
            continue  # check_tutorial names the file that cannot be read
    for relative, data in sorted(expected.items()):
        path = book_path(layout, relative)
        if not os.path.isfile(path):
            report.pending(download_owner(book, relative) or relative, '%s is not written yet: run python -I tools/tutorials.py compile' % relative)
        elif files.read_bytes(path) != data:
            report.error('%s:1' % relative, 'differs from what compile writes from %s: run python -I tools/tutorials.py compile' % (
                download_owner(book, relative) or 'its tutorial'))
    for item in selected:
        if item.key in book.invalid:
            continue
        for relative in unlinked_solutions(layout, item):
            report.error('%s:1' % relative, 'no answer of src/content/docs/%s.md names this worked solution (solution="%s"), so no page links '
                         'its download: name it in the exercise\'s answer, or run python -I tools/tutorials.py compile, which removes it' % (
                             item.page, item.relative))
        if isinstance(item, ExercisePatch) or item.exercise is not None:
            continue
        folder = item.downloads_folder()
        made = {relative.rsplit('/', 1)[1] for relative in files.made_downloads(layout, item)}
        absolute = book_path(layout, folder)
        for name in sorted(os.listdir(absolute)) if os.path.isdir(absolute) else []:
            if name in made or not re.match(r'^stage-\d+\.(?:commands\.json|zip)$', name):
                continue
            report.error('%s/%s:1' % (folder, name), 'the tutorial %s no longer makes this download (no stage its page offers%s: a checkpoint '
                         'names its stage, a how-to offers its last): run python -I tools/tutorials.py compile, which removes it' % (
                             item.relative, ', or one without endState' if name.endswith('.zip') else ''))
        for index, stage in enumerate(item.stages):
            name = files.stage_zip_name(stage['step'])
            if name in made and name.endswith('.zip') and not os.path.isfile(book_path(layout, '%s/%s' % (folder, name))):
                report.pending(item.where('stages', index, 'endState'), '%s/%s is not written yet: run the tutorial (python -I '
                               'tools/tutorials.py run, under the perf lock)' % (folder, name))


def unlinked_solutions(layout, item):
    """The worked solution's download of an exercise that exists though no answer of its page names the solution."""
    if isinstance(item, ExercisePatch):
        relative = 'public/downloads/solutions/%s/exercise-%d.patch' % (item.page, item.exercise)
    elif item.exercise is not None:
        relative = 'public/downloads/solutions/%s/exercise-%d.zip' % (item.page, item.exercise)
    else:
        return []
    if os.path.isfile(book_path(layout, relative)) and not files.solution_named(layout, item.page, item.relative):
        return [relative]
    return []


def check_zips(book, credits, report):
    """Every zip of the tutorials and solutions: its credits and size, and the size of all of them together."""
    layout = book.layout
    total = 0
    for folder, directories, names in os.walk(os.path.join(layout.root, 'public', 'downloads')):
        directories.sort()
        for name in sorted(names):
            if not name.endswith('.zip'):
                continue
            path = os.path.join(folder, name)
            relative = layout.relative(path)
            if not (relative.startswith('public/downloads/tutorials/') or relative.startswith('public/downloads/solutions/')):
                continue
            total += os.path.getsize(path)
            for problem in zip_problems(layout, relative, credits):
                report.error(download_owner(book, relative) or relative, problem)
    if total > files.c_ZipsLimit:
        report.error('public/downloads/', 'the tutorials\' zips hold %.1f MB together, over the 150 MB they may hold: make the end states '
                     'smaller' % (total / 1e6))


def needs_engine(book, selected, layout):
    """Why a check or compile of these tutorials reads the engine, or None."""
    for item in selected:
        for stage in getattr(item, 'stages', []):
            for entry in files.stage_copies(stage):
                if isinstance(entry, dict) and isinstance(entry.get('from'), str) and not entry['from'].startswith('book:'):
                    return '%s copies %s from the engine' % (item.relative, entry['from'])
            for step in (stage.get('setup') or []) + (stage.get('commands') or []):
                for _, value in walk_strings(step.get('parameters') or {}):
                    if value.startswith(files.c_Release + '/'):
                        return '%s imports %s from the release, whose samples are read at the pin' % (item.relative, value)
    downloads = os.path.join(layout.root, 'public', 'downloads')
    for folder, _, names in os.walk(downloads):
        if any(name.endswith('.zip') for name in names):
            return 'the downloads hold zips, whose credits are read from the samples\' CREDITS.md at the pin'
    return None


def check(layout, engine, pin, dumps_folder, names, release):
    report = Report(release)
    book = Book(layout)
    dumps = Dumps(dumps_folder, pin['commit'])
    selected = book.select(names)
    if engine is None:
        reason = needs_engine(book, selected, layout)
        if reason:
            raise UsageError('%s: pass --engine <the pin clone> (or set STRATA_ENGINE)' % reason)
    for page, path in sorted(book.pages.items()):
        if names and page not in names:
            continue
        kind, _ = page_kind_and_checkpoints(layout, path)
        if kind == 'tutorial' and page not in book.by_key:
            report.error('%s:1' % layout.relative(path), 'a tutorial page needs its tutorial file tutorials/%s.tutorial.json (plan/pipelines.md '
                         '§6.2): write it, one stage per step section' % page)
    for item in selected:
        if isinstance(item, ExercisePatch):
            if item.page not in book.pages:
                report.error(item.where(), 'the page %s does not exist: an exercise belongs to its page' % item.page)
            continue
        if book.validate(item, report):
            check_tutorial(book, item, dumps, engine, pin['commit'], report)
    sources = files.Sources(layout, engine, pin['commit'])
    credits = files.Credits(layout, engine, pin['commit'])
    check_downloads(book, selected, sources, credits, report)
    check_zips(book, credits, report)
    for item in selected:
        if item.key in book.invalid:
            continue
        stamp = book_path(layout, item.stamp_relative)
        where = '%s:1' % item.stamp_relative if os.path.isfile(stamp) else item.where()
        for problem in files.stamp_problems(layout, item, pin, changes_engine=book.changes_engine(item)):
            report.pending(where, problem)
    return report


# ---------------------------------------------------------------------------------------------------------------------
# compile.

def compile_downloads(layout, engine, pin, names):
    """Writes the downloads of the tutorials named (all without names): [(relative path, 'wrote' | 'unchanged' |
    'removed')]. Tutorials that fail the schema are not compiled: RunError lists them."""
    book = Book(layout)
    selected = book.select(names)
    if engine is None:
        reason = needs_engine(book, [item for item in selected if not isinstance(item, ExercisePatch)], layout)
        if reason and 'copies' in reason:
            raise UsageError('%s: pass --engine <the pin clone> (or set STRATA_ENGINE)' % reason)
    report = Report()
    tutorials = [item for item in selected if not isinstance(item, ExercisePatch) and book.validate(item, report)]
    if report.errors:
        raise RunError('\n'.join('%s: %s' % pair for pair in report.errors) + '\nrun python -I tools/tutorials.py check')
    sources = files.Sources(layout, engine, pin['commit'] if pin else None)
    credits = files.Credits(layout, engine, pin['commit'] if pin else None)
    try:
        compiled = files.compiled_files(layout, tutorials, sources, credits)
    except files.SourceError as error:
        raise RunError(str(error))
    written = []
    for item in selected:
        if isinstance(item, ExercisePatch):
            compiled['public/downloads/solutions/%s/exercise-%d.patch' % (item.page, item.exercise)] = files.read_bytes(book_path(layout, item.relative))
    for relative, data in sorted(compiled.items()):
        path = book_path(layout, relative)
        if os.path.isfile(path) and files.read_bytes(path) == data:
            written.append((relative, 'unchanged'))
            continue
        write_bytes(path, data)
        written.append((relative, 'wrote'))
    for item in selected:
        if isinstance(item, ExercisePatch) or item in tutorials:
            for relative in unlinked_solutions(layout, item):
                os.remove(book_path(layout, relative))
                written.append((relative, 'removed'))
    for tutorial in tutorials:
        if tutorial.exercise is not None:
            continue
        folder = book_path(layout, tutorial.downloads_folder())
        if not os.path.isdir(folder):
            continue
        keep = {relative.rsplit('/', 1)[1] for relative in files.made_downloads(layout, tutorial)}
        for name in sorted(os.listdir(folder)):
            if re.match(r'^stage-\d+\.(?:commands\.json|zip)$', name) and name not in keep:
                os.remove(os.path.join(folder, name))
                written.append(('%s/%s' % (tutorial.downloads_folder(), name), 'removed'))
    return written


# ---------------------------------------------------------------------------------------------------------------------
# run.

class TimedSession:
    """An editor session whose slow commands (builds, imports, opening projects and scenes) get the time for opening a
    scene (plan/pipelines.md §2: 300 s per call, 900 s for opening); every result is kept for --record-examples."""

    def __init__(self, session):
        self.session = session
        self.calls = []

    def call(self, command, parameters=None, timeout=None):
        if timeout is None:
            timeout = editor.c_OpenSeconds if command in c_SlowCommands else editor.c_CallSeconds
        result = self.session.call(command, parameters, timeout=timeout)
        self.calls.append((command, copy.deepcopy(parameters or {}), result))
        return result


def element_texts(value):
    """The texts of an element of an array that contains looks into: a string, or every string inside it (a log entry's
    message, for example)."""
    return [text for _, text in walk_strings(value)] if not isinstance(value, str) else [value]


def check_problem(command, result, check):
    """Why a result does not meet one of the book's checks (plan/pipelines.md §6.2), or None."""
    pointer = check['pointer']
    try:
        value = steps.resolve_pointer(result, pointer)
    except KeyError:
        return '%s: check %s: the result has no such value: check a pointer the result has' % (command, pointer)
    shown = json.dumps(value, ensure_ascii=False)
    shown = shown if len(shown) <= 200 else shown[:200] + '…'
    unmet = None
    if 'equals' in check and not steps.json_equal(value, check['equals']):
        unmet = '%s: check %s is %s, not %s' % (command, pointer, shown, json.dumps(check['equals'], ensure_ascii=False))
    elif 'approx' in check and (not steps.is_number(value) or abs(value - check['approx']) > check['tolerance']):
        unmet = '%s: check %s is %s, not %s within %s' % (command, pointer, shown, check['approx'], check['tolerance'])
    elif 'length' in check and (not isinstance(value, (list, dict, str)) or len(value) != check['length']):
        unmet = '%s: check %s has %s, not %d items' % (command, pointer, len(value) if isinstance(value, (list, dict, str)) else 'no length',
                                                       check['length'])
    elif 'contains' in check:
        text = check['contains']
        if isinstance(value, list):
            if not any(text in item for element in value for item in element_texts(element)):
                unmet = '%s: check %s: no element contains "%s" (%d elements)' % (command, pointer, text, len(value))
        elif not isinstance(value, str) or text not in value:
            unmet = '%s: check %s is %s, which does not contain "%s"' % (command, pointer, shown, text)
    return None if unmet is None else '%s: correct the steps before it, or the value the check asks for' % unmet


def fill_placeholders(value, values):
    if isinstance(value, str):
        for placeholder, replacement in values.items():
            value = value.replace(placeholder, replacement)
        return value
    if isinstance(value, dict):
        return {key: fill_placeholders(item, values) for key, item in value.items()}
    if isinstance(value, list):
        return [fill_placeholders(item, values) for item in value]
    return value


def default_project_name(page):
    return ''.join(word[:1].upper() + word[1:] for word in re.split(r'[^A-Za-z0-9]+', page.rsplit('/', 1)[-1]) if word)[:32] or 'Tutorial'


def same_folder(first, second):
    return os.path.normcase(os.path.abspath(first)) == os.path.normcase(os.path.abspath(second))


def copy_project(source, target):
    """The project as a reader has it, to start a stage from: everything but .strata/, except the built script module
    (.strata/Scripts/Bin), which the editor loads when it opens a project (EditorContext.h:555). The script build tree
    (.strata/Scripts/Build) names the project's folder and cannot move."""
    shutil.copytree(source, target, ignore=lambda folder, names: ['.strata'] if same_folder(folder, source) and '.strata' in names else [])
    binaries = os.path.join(source, '.strata', 'Scripts', 'Bin')
    if os.path.isdir(binaries):
        shutil.copytree(binaries, os.path.join(target, '.strata', 'Scripts', 'Bin'))


def newest_output(project, target):
    """The latest modification time of the file a stage replaces and of the project's script build (.strata/Scripts)."""
    newest = os.path.getmtime(target)
    for folder, _, names in os.walk(os.path.join(project, '.strata', 'Scripts')):
        for name in names:
            newest = max(newest, os.path.getmtime(os.path.join(folder, name)))
    return newest


def wait_past_outputs(project, target, sleep, clock=time.time):
    """Waits until a file written now gets a later modification time than the file it replaces and the script build's
    outputs, as a reader's edit does. Build tools decide by these times, and some file systems keep them in steps of 2
    seconds (exFAT, the authoring drive): a file replaced in the second its build ended would look built already."""
    ready = newest_output(project, target) + c_TimeStepSeconds
    now = clock()
    if now < ready:
        sleep(ready - now)


def project_files(project):
    """(name in the zip, bytes) of the project under a folder named like the project's, without .strata/ and without
    the CMakePresets.json the editor writes for its machine (files.editor_presets): a reader's editor writes their own."""
    found = []
    top = os.path.basename(os.path.normpath(project))
    for folder, directories, names in os.walk(project):
        if same_folder(folder, project):
            directories[:] = [name for name in directories if name != '.strata']
        directories.sort()
        for name in sorted(names):
            path = os.path.join(folder, name)
            relative = os.path.relpath(path, project).replace(os.sep, '/')
            data = files.read_bytes(path)
            if not files.editor_presets(relative, data):
                found.append(('%s/%s' % (top, relative), data))
    return found


def machine_path_problem(project_data, folders):
    """Why a stage's zip would publish a path of this machine, or None: a download names no folder of the machine that
    made it (the repository is public, and the reader's folders are others)."""
    for name, data in project_data:
        found = files.machine_folder_line(data, folders)
        if found:
            return ('%s names a folder of this machine on its line %d (%s), and the stage\'s zip would publish it: remove the file '
                    'from the project, or, when the editor writes it for the machine it runs on, leave it out of the zip as '
                    'project_files in tools/tutorials.py leaves out the editor\'s CMakePresets.json' % (name, found[0], found[1]))
    return None


def hide(value, paths):
    """A result as an example shows it: IDs and paths replaced by "…" (plan/pipelines.md §6.3)."""
    if isinstance(value, str):
        normal = value.replace('\\', '/')
        if c_HexId.match(value) or c_PathInText.search(value) or any(path and path.lower() in normal.lower() for path in paths):
            return c_Hidden
        return value
    if isinstance(value, dict):
        return {key: hide(item, paths) for key, item in value.items()}
    if isinstance(value, list):
        return [hide(item, paths) for item in value]
    return value


class Runner:
    def __init__(self, layout, book, engine, pin, build, work, build_record, record_examples):
        self.layout = layout
        self.book = book
        self.engine = engine
        self.pin = pin
        self.build = build
        self.work = work
        self.build_record = build_record
        self.record_examples = record_examples
        self.log = editor.Log(os.path.join(work, 'log'))
        self.sources = files.Sources(layout, engine, pin)
        self.credits = files.Credits(layout, engine, pin)
        self.cache = {}
        self.examples = {}
        self.folders = 0
        self.lines = []
        self.failed = 0
        self.passed = 0
        self.skipped = 0

    def new_folder(self):
        self.folders += 1
        path = os.path.join(self.work, 't%02d' % self.folders)
        os.makedirs(path)
        return path

    def chain_key(self, tutorial):
        """The SHA-256 of the chain's tutorial files and the files they copy, with the pin: the key of a cached end state."""
        digest = hashlib.sha256(self.pin.encode('ascii'))
        for item in self.book.chain(tutorial):
            for relative in sorted(self.inputs_of(item)):
                digest.update(relative.encode('utf-8') + b'\0' + files.read_bytes(book_path(self.layout, relative)) + b'\0')
        return digest.hexdigest()

    def inputs_of(self, tutorial):
        """The repository files a tutorial reads: the tutorial file, the book files its stages copy and import."""
        found = [tutorial.relative]
        for stage in tutorial.stages:
            for entry in files.stage_copies(stage):
                if entry['from'].startswith('book:'):
                    found.append(entry['from'][len('book:'):])
            for step in stage.get('setup') or []:
                for _, value in walk_strings(step.get('parameters') or {}):
                    if value.startswith('@BOOK@/'):
                        found.append(value[len('@BOOK@/'):])
        return found

    def reader_copy_paths(self, tutorial):
        """The reader's copies a run stamps: those compile writes (the stages its page offers, a solution an answer names)."""
        return sorted(relative for relative in files.made_downloads(self.layout, tutorial) if not relative.endswith('.zip') or tutorial.exercise is not None)

    def stamp_inputs(self, tutorial):
        inputs = {}
        for item in self.book.chain(tutorial):
            for relative in self.inputs_of(item) + (self.reader_copy_paths(item) if item is tutorial else []):
                inputs[relative] = files.sha256_file(book_path(self.layout, relative))
        return dict(sorted(inputs.items()))

    def save_scene(self, session):
        """Saves the edited scene when it has unsaved changes, so that a copy or a zip of the project holds what the reader
        has in the editor at that point."""
        status = session.call('editor.status', {})
        scene = status.get('scene') if isinstance(status, dict) else None
        if isinstance(scene, dict) and scene.get('modified') and scene.get('scene'):
            session.call('scene.save', {})

    def start(self, session, tutorial, project, folder):
        """Makes the project a tutorial starts from in the session (plan/pipelines.md §6.3, run step 2)."""
        starts = tutorial.starts_from
        if 'template' in starts:
            session.call('project.create', {'directory': project, 'name': starts.get('name') or default_project_name(tutorial.page),
                                            'template': starts['template']})
        elif 'sample' in starts:
            session.call('project.openSample', {'sample': starts['sample'], 'directory': project})
        else:
            earlier = self.book.by_key[starts['tutorial']]
            key = self.chain_key(earlier)
            if key not in self.cache:
                self.start(session, earlier, project, folder)
                results = self.run_stages(session, earlier, project, folder, publish=False)
                failed = [result for result in results if not result['passed']]
                if failed or len(results) != len(earlier.stages):
                    raise RunError('the tutorial it starts from, %s, failed: %s' % (earlier.key, failed[0]['error'] if failed else 'not every stage ran'))
                self.save_scene(session)
                cached = os.path.join(self.work, 'end-states', key[:16])
                if os.path.isdir(cached):
                    shutil.rmtree(cached)
                copy_project(project, cached)
                self.cache[key] = cached
                return
            copy_project(self.cache[key], project)
            session.call('project.open', {'path': project, 'force': True})
        session.call('scene.loadStatus', {'wait': True})

    def copy_files(self, entries, project):
        """Copies a stage's or a command's files into the project, each replaced file once it is newer than the outputs
        of the commands before it (wait_past_outputs)."""
        for entry in entries or []:
            target = os.path.join(project, *entry['to'].replace('\\', '/').split('/'))
            data = self.sources.read(entry['from'])
            if os.path.isfile(target):
                wait_past_outputs(project, target, time.sleep)
            write_bytes(target, data)

    def run_stages(self, session, tutorial, project, folder, publish):
        """[{step, passed, error, start, stage}] of the stages in order, up to the first that fails."""
        results = []
        made = files.made_downloads(self.layout, tutorial) if tutorial.exercise is None else set()
        values = {'@PROJECT@': project.replace('\\', '/'), '@BOOK@': self.layout.root.replace('\\', '/'), '@WORK@': self.work.replace('\\', '/'),
                  files.c_Release: self.release()}
        for index, stage in enumerate(tutorial.stages):
            step = stage['step']
            start = os.path.join(folder, 'start-%d' % step)
            where = tutorial.where('stages', index)
            try:
                self.copy_files(stage.get('files'), project)
                bound = {}
                for setup_index, setup in enumerate(stage.get('setup') or []):
                    where = tutorial.where('stages', index, 'setup', setup_index)
                    steps.run_step(session, fill_placeholders(setup, values), bound)
                where = tutorial.where('stages', index)
                self.save_scene(session)
                if os.path.isdir(start):
                    shutil.rmtree(start)
                copy_project(project, start)
                for command_index, command in enumerate(stage.get('commands') or []):
                    where = tutorial.where('stages', index, 'commands', command_index)
                    if command.get('files'):
                        self.copy_files(command['files'], project)
                    _, result = steps.run_step(session, fill_placeholders(command, {files.c_Release: self.release()}), bound)
                    for check in command.get('checks') or []:
                        problem = check_problem(command['command'], result, check)
                        if problem:
                            raise steps.StepError(problem)
                if publish and '%s/%s' % (tutorial.downloads_folder(), files.stage_zip_name(step)) in made:
                    self.save_scene(session)
                    project_data = project_files(project)
                    problem = machine_path_problem(project_data, self.machine_folders())
                    if problem:
                        raise RunError(problem)
                    data = files.zip_bytes(project_data + self.credits.file_for(item for _, item in project_data))
                    relative = '%s/%s' % (tutorial.downloads_folder(), files.stage_zip_name(step))
                    if len(data) > files.c_ZipLimit:
                        raise RunError('the project after stage %d zips to %.1f MB, over the 10 MB a download may have: leave out what the '
                                       'reader does not need' % (step, len(data) / 1e6))
                    write_bytes(book_path(self.layout, relative), data)
                results.append({'step': step, 'passed': True, 'start': start, 'stage': stage})
            except editor.EditorError as error:
                results.append({'step': step, 'passed': False, 'stage': stage,
                                'error': '%s: stage %d: %s: %s' % (where, step, error, c_EditorFailureRemedy)})
                break
            except (steps.StepError, files.SourceError, RunError, OSError) as error:
                results.append({'step': step, 'passed': False, 'error': '%s: stage %d: %s' % (where, step, error), 'stage': stage})
                break
        return results

    def release(self):
        """What @RELEASE@ stands for in a run: the folder of the build, which holds the release's Samples/."""
        return os.path.abspath(self.build).replace('\\', '/')

    def run_reader_copy(self, tutorial, result, folder):
        """Runs a stage's reader copy in the engine's own runner on the stage's start state, part by part when commands
        carry files (copied between the parts, as the reader edits them); None or why it failed."""
        segments = [(copies, commands) for copies, commands in files.command_segments(result['stage']) if copies or commands]
        for number, (copies, commands) in enumerate(segments, 1):
            part = '' if len(segments) == 1 else ' (part %d of %d: the commands before, between and after those that carry files)' % (
                number, len(segments))
            suffix = '' if len(segments) == 1 else '-part-%d' % number
            try:
                self.copy_files(copies, result['start'])
            except (files.SourceError, OSError) as error:
                return 'the files before part %d of the reader\'s copy of stage %d: %s' % (number, result['step'], error)
            if not commands:
                continue
            script = os.path.join(folder, 'reader-%d%s.commands.json' % (result['step'], suffix))
            write_bytes(script, files.script_bytes(files.reader_script(commands, self.release())))
            session = editor.new_session_dir()
            env = editor.environment(self.build, self.work, session)
            # A tutorial that asks for automation gets the editor's own server: on loopback, on the free port the editor
            # picks, its token only in the private session folder, which the run neither reads nor logs.
            serving = [] if tutorial.automation else ['--no-automation']
            arguments = [editor.program_path(self.build, 'StrataEditor'), '--no-gpu'] + serving + ['--project', result['start'],
                         '--commands', script, '--quit-after-commands', '--frames', str(c_ReaderFrames)]
            try:
                code, output, _ = editor.run_program(arguments, env, self.log, 'reader-copy-%s-stage-%d%s' % (tutorial.key, result['step'], suffix),
                                                     c_ReaderSeconds)
            except editor.EditorError as error:
                return str(error)
            finally:
                shutil.rmtree(session, ignore_errors=True)
            if code != 0:
                errors = [line for line in output.splitlines() if 'error' in line.lower()] or output.strip().splitlines()[-1:]
                return ('the engine\'s runner exited with %d on the reader\'s copy of stage %d%s: %s (log in %s): correct the stage so that '
                        'its reader\'s copy, the commands without the book\'s checks and with entity.find for each entityName, also passes '
                        'in the engine\'s own runner on the stage\'s start state' % (
                            code, result['step'], part, (errors[-1] if errors else '(no output)').strip(), self.log.folder))
        return None

    def run(self, tutorial):
        folder = self.new_folder()
        project = os.path.join(folder, tutorial.starts_from.get('name') or default_project_name(tutorial.page))
        compiled = files.compiled_files(self.layout, [tutorial], self.sources, self.credits)
        for relative, data in compiled.items():
            path = book_path(self.layout, relative)
            if not (os.path.isfile(path) and files.read_bytes(path) == data):
                write_bytes(path, data)
        session = editor.Editor(self.build, self.work, self.log)
        status = None
        results = []
        failure = None
        try:
            session.launch()
            status = session.check_commit(self.pin)
            timed = TimedSession(session)
            self.start(timed, tutorial, project, folder)
            results = self.run_stages(timed, tutorial, project, folder, publish=True)
            if all(result['passed'] for result in results) and len(results) == len(tutorial.stages) and tutorial.exercise is None \
                    and any(item.starts_from.get('tutorial') == tutorial.key for item in self.book.tutorials):
                # A later tutorial starts where this one ends: keep the end state, so the chain runs each tutorial once.
                self.save_scene(timed)
                cached = os.path.join(self.work, 'end-states', self.chain_key(tutorial)[:16])
                copy_project(project, cached)
                self.cache[self.chain_key(tutorial)] = cached
        except editor.EditorError as error:
            failure = '%s: %s: %s' % (tutorial.where('startsFrom'), error, c_StartFailureRemedy)
        except (steps.StepError, files.SourceError, RunError, OSError) as error:
            failure = '%s: %s' % (tutorial.where('startsFrom'), error)
        finally:
            session.quit()
        failed = [result for result in results if not result['passed']]
        if failure is None and failed:
            failure = failed[0]['error']
        if failure is None and len(results) != len(tutorial.stages):
            failure = '%s: not every stage ran' % tutorial.where('stages')
        if failure is None and self.record_examples:
            # Every stage passed, so every answer of the run is a passing result; the first of each command is kept.
            for command, parameters, result in timed.calls:
                self.examples.setdefault(command, (parameters, result))
        reader_copies = failure is None
        if failure is None:
            for result in results:
                problem = self.run_reader_copy(tutorial, result, folder)
                if problem:
                    failure = '%s: %s' % (tutorial.where('stages', result['step'] - 1), problem)
                    reader_copies = False
                    break
        passed = {result['step'] for result in results if result['passed']}
        record = {
            'build': self.build_record,
            'engineCommit': self.pin,
            'reportedCommit': status['engineCommit'] if status else None,
            'os': status['platform'] if status else None,
            'gpu': None,
            'inputs': self.stamp_inputs(tutorial),
            'stages': [{'step': stage['step'], 'passed': stage['step'] in passed} for stage in tutorial.stages],
            'readerCopies': reader_copies,
            'passed': failure is None,
        }
        write_stamp(self.layout, tutorial, record)
        if failure is None:
            self.passed += 1
            self.lines.append('%s: passed: %s: %d stage%s, the reader\'s copies in the engine\'s runner; stamped %s' % (
                tutorial.where(), tutorial.key, len(tutorial.stages), '' if len(tutorial.stages) == 1 else 's', tutorial.stamp_relative))
        else:
            self.failed += 1
            self.lines.append('%s: failed: %s: %s' % (tutorial.where(), tutorial.key, failure))

    def machine_folders(self):
        """The folders of this machine that nothing a run publishes may name: lowercase, with /, never a drive alone; the
        longest first, so a finding names the most specific one."""
        folders = (self.work, self.layout.root, self.build, self.engine.path, editor.system_temp(), os.path.expanduser('~'))
        normal = (os.path.abspath(path).replace('\\', '/').rstrip('/').lower() for path in folders if path)
        return sorted({path for path in normal if len(path) > 3}, key=lambda path: (-len(path), path))

    def write_examples(self):
        paths = self.machine_folders()
        folder = os.path.join(self.layout.root, 'reference', '_examples')
        written = []
        for command, (parameters, result) in sorted(self.examples.items()):
            relative = 'reference/_examples/%s.json' % command
            write_json(os.path.join(folder, command + '.json'), {'pin': self.pin, 'command': command, 'parameters': hide(parameters, paths),
                                                                 'result': hide(result, paths)})
            written.append(relative)
        return written


def write_stamp(layout, tutorial, record):
    """Adds a run to the tutorial's stamp, in place of the earlier run of the same build (plan/pipelines.md §6.4)."""
    path = book_path(layout, tutorial.stamp_relative)
    stamp = {'page': tutorial.page, 'runs': []}
    if os.path.isfile(path):
        try:
            existing = read_json(path)
            if isinstance(existing, dict) and isinstance(existing.get('runs'), list):
                stamp['runs'] = [run for run in existing['runs'] if isinstance(run, dict)]
        except ValueError:
            pass  # a stamp that is no JSON (check reports it) holds no run to keep: this run's stamp replaces it

    def same(run):
        build = run.get('build') or {}
        return build.get('kind') == record['build']['kind'] and build.get('package') == record['build'].get('package')
    stamp['runs'] = [run for run in stamp['runs'] if not same(run)] + [record]
    order = {'pin-build': 0, 'patch-build': 1, 'package': 2}
    stamp['runs'].sort(key=lambda run: order.get((run.get('build') or {}).get('kind'), 3))
    write_json(path, stamp)


def renders(book, tutorial):
    """The first command of the tutorial's chain that renders (and so needs the GPU), or None."""
    for item in book.chain(tutorial):
        for stage in item.stages:
            for step in (stage.get('setup') or []) + (stage.get('commands') or []):
                if step['command'] in c_RenderingCommands:
                    return step['command']
    return None


def ordered(book, tutorials):
    """The tutorials with every one after the tutorial it starts from, so a chain's end states are cached once."""
    return sorted(tutorials, key=lambda item: (len(book.chain(item)), item.relative))


def prepare_work(work, marker=c_Marker):
    """Empties the work folder of the previous run (only a folder this tool marked as its own)."""
    if os.path.isdir(work) and os.listdir(work):
        if not os.path.isfile(os.path.join(work, marker)):
            raise UsageError('the work folder %s holds files that are not a run of tutorials.py: name an empty folder with --work' % work)
        for entry in os.listdir(work):
            path = os.path.join(work, entry)
            if os.path.isdir(path):
                repo_remove_tree(path)
            else:
                os.remove(path)
    os.makedirs(work, exist_ok=True)
    repo.write_text(os.path.join(work, marker), 'A run of tools/tutorials.py; the next run empties this folder.\n')


def repo_remove_tree(path):
    def clear_and_retry(function, target, _):
        os.chmod(target, 0o700)
        function(target)
    shutil.rmtree(path, onerror=clear_and_retry)


def run(layout, engine, pin, build, work, names, record_examples, build_record):
    book = Book(layout)
    selected = book.select(names)
    report = Report()
    candidates = []
    runner = None
    for item in selected:
        if isinstance(item, ExercisePatch):
            continue
        if book.validate(item, report):
            candidates.append(item)
    if report.errors:
        raise RunError('\n'.join('%s: %s' % pair for pair in report.errors) + '\nrun python -I tools/tutorials.py check')
    prepare_work(work)
    runner = Runner(layout, book, engine, pin, build, work, build_record, record_examples)
    for item in [item for item in selected if isinstance(item, ExercisePatch)]:
        runner.skipped += 1
        runner.lines.append('%s: skipped: %s: an engine exercise; tutorials.py patch runs it (phase B)' % (item.where(), item.key))
    for tutorial in ordered(book, candidates):
        try:
            chain = book.chain(tutorial)
        except RunError as error:
            runner.failed += 1
            runner.lines.append('%s: failed: %s: %s' % (tutorial.where(), tutorial.key, error))
            continue
        if any(item.patch for item in chain):
            runner.skipped += 1
            runner.lines.append('%s: skipped: %s: it changes the engine; tutorials.py patch runs it (phase B)' % (tutorial.where(), tutorial.key))
            continue
        rendering = renders(book, tutorial)
        if rendering:
            runner.skipped += 1
            runner.lines.append('%s: skipped: %s: %s renders, which needs the GPU: run it with --pictures in phase B, after engine '
                                'release 0.8.0' % (tutorial.where(), tutorial.key, rendering))
            continue
        runner.run(tutorial)
    examples = runner.write_examples() if record_examples else []
    return runner, examples


# ---------------------------------------------------------------------------------------------------------------------
# patch.

class PatchItem:
    """A patch tutorial or an engine exercise with its chain of patches (the first one first) and its suites."""

    def __init__(self, book, item):
        self.item = item
        self.patches = []
        self.tutorials = []
        if isinstance(item, ExercisePatch):
            page = book.by_key.get(item.page)
            chain_patches = []
            if page is not None:
                self.tutorials = book.chain(page)
                chain_patches = book.chain_patches(page)
            self.patches = chain_patches + [item.relative]
            # The page's suites, then those its file names for this exercise (its "exercises").
            self.suites = list((page.patch or {}).get('tests') or []) if page is not None and page.patch else []
            if page is not None:
                self.suites += [suite for suite in page.exercises.get(item.exercise, []) if suite not in self.suites]
        else:
            self.tutorials = book.chain(item)
            self.patches = book.chain_patches(item)
            # A file without a patch of its own runs on its chain's engine with the suites of the chain's last patch tutorial.
            owner = item if item.patch else ([tutorial for tutorial in self.tutorials if tutorial.patch] or [item])[-1]
            self.suites = list((owner.patch or {}).get('tests') or [])


def git_apply(engine_path, log, arguments, name):
    """git apply in the clone. Paths go with forward slashes: MSYS2's git reads its command line as a shell would."""
    arguments = [argument.replace('\\', '/') for argument in arguments]
    code, output, _ = editor.run_program(['git', '-C', engine_path.replace('\\', '/'), 'apply'] + arguments, os.environ.copy(), log, name,
                                         editor.c_CallSeconds)
    return code, output.strip()


def doctest_result(output):
    """(test cases, failed) from doctest's summary line, or None when it printed none."""
    matches = list(c_DoctestSummary.finditer(output))
    if not matches:
        return None
    last = matches[-1]
    return int(last.group('cases')), int(last.group('failed'))


def ctest_count(output):
    match = re.search(r'tests passed, (\d+) tests? failed out of (\d+)', output)
    return (int(match.group(2)), int(match.group(1))) if match else None


class Patcher:
    def __init__(self, layout, book, engine, pin, build_dir, work, cmake, ctest):
        self.layout = layout
        self.book = book
        self.engine = engine
        self.pin = pin
        self.build_dir = build_dir
        self.work = work
        self.cmake = cmake
        self.ctest = ctest
        self.log = editor.Log(os.path.join(work, 'log'))
        self.env = os.environ.copy()
        self.env['MSBUILDDISABLENODEREUSE'] = '1'
        self.lines = []
        self.passed = 0
        self.failed = 0

    def program(self, arguments, name, seconds):
        try:
            return editor.run_program(arguments, self.env, self.log, name, seconds, cwd=self.engine.path)
        except editor.EditorError as error:
            raise RunError(str(error))

    def configure(self, name):
        """cmake --preset windows -B <build dir>: (exit code, last line). The engine collects its sources with CONFIGURE_DEPENDS
        globs (AGENTS.md, "Building"): without a configure after files come or go, the build reconfigures the shared folder in its
        middle, after MSBuild loaded the old projects, and fails with C1083 or an unresolved symbol of a new file."""
        code, output, _ = self.program([self.cmake, '--preset', 'windows', '-B', self.build_dir], name, c_BuildSeconds)
        return code, editor.last_line(output)

    def build_and_test(self, chain_files, suites):
        """Configures the applied chain, builds the targets it needs, runs the tests: (test results, ctest result)."""
        code, last = self.configure('configure')
        if code != 0:
            raise RunError('cmake --preset windows -B %s exited with %d: %s (log in %s): correct what the log names, a CMake file the '
                           'patches change or a tool the configure needs, and run patch again' % (self.build_dir, code, last, self.log.folder))
        targets = ['StrataTests'] + sorted({target for folder, target in c_ProgramFolders.items()
                                           if any(path.startswith(folder) for path in chain_files)})
        code, output, _ = self.program([self.cmake, '--build', self.build_dir, '--config', 'Release', '--parallel', '2', '--target']
                                       + targets + ['--', '/p:CL_MPCount=4'], 'build', c_BuildSeconds)
        if code != 0:
            errors = [line for line in output.splitlines() if ': error ' in line or ' error ' in line.lower()]
            raise RunError('the build of %s exited with %d: %s (log in %s): correct the patch until the engine builds, with warnings as '
                           'errors as in CI (plan/pipelines.md §6.6)' % (', '.join(targets), code, (errors or [editor.last_line(output)])[0].strip(),
                                                                       self.log.folder))
        tests = editor.program_path(os.path.join(self.build_dir, 'bin', 'Release'), 'StrataTests')
        results = []
        for suite in list(c_DefaultSuites) + [suite for suite in suites if suite not in c_DefaultSuites]:
            code, output, _ = self.program([tests, '--test-suite=%s' % suite], 'test-%s' % suite, c_TestSeconds)
            summary = doctest_result(output)
            cases = summary[0] if summary else 0
            passed = code == 0 and summary is not None and cases > 0 and summary[1] == 0
            results.append({'suite': suite, 'testCases': cases, 'passed': passed})
            if not passed:
                if summary is not None and cases == 0:
                    reason = ('ran no test case: no suite %s is in the build (log in %s): name in patch.tests only suites that the '
                              'patch or the pin declares in a test file StrataTests builds' % (suite, self.log.folder))
                else:
                    reason = ('exited with %d (log in %s): correct the patch until the suite passes; the log holds the failing checks'
                              % (code, self.log.folder))
                raise RunError('StrataTests --test-suite=%s %s' % (suite, reason), results)
        code, output, _ = self.program([self.ctest, '--test-dir', self.build_dir, '-C', 'Release', '-R', c_FeatureTest], 'ctest-feature-test', c_TestSeconds)
        counted = ctest_count(output)
        ctest = {'test': 'StrataTests.FeatureTest', 'passed': code == 0 and counted is not None and counted[0] > 0 and counted[1] == 0}
        if not ctest['passed']:
            if counted is None or counted[0] == 0:
                reason = ('found no test (log in %s): the engine registers the feature test only in a build with every optional module '
                          '(STRATA_WITH_PHYSICS, STRATA_WITH_AUDIO and STRATA_WITH_ANIMATION on: StrataTests/CMakeLists.txt:83-86 and '
                          ':316 at the pin), so keep them on in the patch and in %s' % (self.log.folder, os.path.join(self.build_dir, 'CMakeCache.txt')))
            else:
                reason = ('exited with %d (log in %s): correct the patch until the feature test passes; a patch that adds a component, a '
                          'script API or a command also adds its feature-test exercise (plan/pipelines.md §6.6)' % (code, self.log.folder))
            raise RunError('ctest -R "%s" %s' % (c_FeatureTest, reason), results, ctest)
        return results, ctest

    def run(self, patch_item):
        item = patch_item.item
        applied = []
        failure = None
        tests, ctest = [], None
        chain_files = []
        adds_files = False
        try:
            for relative in patch_item.patches:
                path = book_path(self.layout, relative)
                if not os.path.isfile(path):
                    raise RunError('%s does not exist: write the patch' % relative)
                text = repo.read_text(path)
                chain_files += changed_files(text)
                adds_files = adds_files or adds_or_removes_files(text)
                code, output = git_apply(self.engine.path, self.log, ['--check', path], 'apply-check')
                if code != 0:
                    raise RunError('%s does not apply to the pin%s: %s; write it against the pin again (git diff)' % (
                        relative, ' after %s' % ', '.join(applied) if applied else '', (output.splitlines() or ['(no output)'])[0]))
                code, output = git_apply(self.engine.path, self.log, [path], 'apply')
                if code != 0:
                    raise RunError('git apply %s exited with %d: %s: a git apply that fails changes no file, and git apply --check had '
                                   'passed, so read the log in %s and run patch again' % (relative, code, output, self.log.folder))
                applied.append(relative)
            tests, ctest = self.build_and_test(chain_files, patch_item.suites)
        except RunError as error:
            failure = str(error.args[0])
            if len(error.args) > 1:
                tests = error.args[1]
            if len(error.args) > 2:
                ctest = error.args[2]
        finally:
            for relative in reversed(applied):
                code, output = git_apply(self.engine.path, self.log, ['-R', book_path(self.layout, relative)], 'revert')
                if code != 0:
                    raise RevertError('git apply -R %s failed in %s (%s): the clone stays dirty, and every tool\'s preflight refuses it until a '
                                      'person restores it (git -C %s checkout -- . after reading what changed)' % (relative, self.engine.path, output, self.engine.path))
            try:
                editor.preflight_clone(self.engine, self.pin)
            except editor.PreflightError as error:
                raise RevertError('after the patches were reverted: %s' % error)
        if applied and adds_files:
            # The shared build folder lists the chain's files until it is configured at the pin again.
            try:
                code, last = self.configure('configure-reverted')
            except RunError as error:
                code, last = -1, str(error)
            if code != 0:
                reverted = ('after the patches were reverted, cmake --preset windows -B %s exited with %d: %s (log in %s): the build folder '
                            'still lists the files the chain adds or removes; correct what the log names and run patch again' % (
                                self.build_dir, code, last, self.log.folder))
                failure = reverted if failure is None else '%s; %s' % (failure, reverted)
        inputs = {}
        for tutorial in patch_item.tutorials:
            inputs[tutorial.relative] = files.sha256_file(book_path(self.layout, tutorial.relative))
        for relative in patch_item.patches:
            path = book_path(self.layout, relative)
            if os.path.isfile(path):
                inputs[relative] = files.sha256_file(path)
        if isinstance(item, ExercisePatch):
            inputs.setdefault(item.relative, files.sha256_file(book_path(self.layout, item.relative)))
        record = {
            'build': {'kind': 'patch-build', 'configuration': 'Release', 'buildDirectory': self.layout_relative_build()},
            'engineCommit': self.pin,
            'reportedCommit': None,
            'os': platform.system(),
            'gpu': None,
            'inputs': dict(sorted(inputs.items())),
            'stages': [],
            'tests': tests,
            'ctest': ctest,
            'readerCopies': False,
            'passed': failure is None,
        }
        write_stamp(self.layout, item, record)
        if failure is None:
            self.passed += 1
            self.lines.append('%s: passed: %s: %s, %d doctest suite%s and the feature test; stamped %s' % (
                item.where(), item.key, ', '.join(patch_item.patches), len(tests), '' if len(tests) == 1 else 's', item.stamp_relative))
        else:
            self.failed += 1
            self.lines.append('%s: failed: %s: %s' % (item.where(), item.key, failure))

    def layout_relative_build(self):
        return os.path.relpath(self.build_dir, self.engine.path).replace(os.sep, '/')


def check_build_dir(engine_path, build_dir):
    """The patch build's folder: inside the clone's build/, never the pin build's (plan/pipelines.md §6.6)."""
    if not build_dir:
        raise UsageError('name the patch build\'s folder with --build-dir <clone>/build/docs-patch (plan/pipelines.md §6.6)')
    absolute = os.path.abspath(build_dir)
    relative = os.path.relpath(absolute, engine_path).replace(os.sep, '/') if os.path.splitdrive(absolute)[0].lower() == \
        os.path.splitdrive(engine_path)[0].lower() else '..'
    if relative.startswith('..') or not relative.startswith('build/') or relative.count('/') != 1:
        raise UsageError('--build-dir %s is not a folder build/<name> of the clone %s: use %s/build/docs-patch' % (build_dir, engine_path, engine_path))
    if relative == c_PinBuildFolder:
        raise UsageError('--build-dir %s is the pin build\'s folder, which never holds patched code: use %s/build/docs-patch' % (build_dir, engine_path))
    return absolute


def patch(layout, engine, pin, build_dir, work, names, cmake, ctest):
    book = Book(layout)
    selected = book.select(names)
    report = Report()
    items = []
    skipped = []
    for item in selected:
        if isinstance(item, ExercisePatch):
            items.append(item)
        elif book.validate(item, report):
            if book.changes_engine(item):
                items.append(item)
            else:
                skipped.append('%s: skipped: %s: it changes no engine code; tutorials.py run runs it' % (item.where(), item.key))
    if report.errors:
        raise RunError('\n'.join('%s: %s' % pair for pair in report.errors) + '\nrun python -I tools/tutorials.py check')
    prepare_work(work)
    patcher = Patcher(layout, book, engine, pin, build_dir, work, cmake, ctest)
    patcher.lines += skipped
    for item in items:
        try:
            patch_item = PatchItem(book, item)
        except RunError as error:
            patcher.failed += 1
            patcher.lines.append('%s: failed: %s: %s' % (item.where(), item.key, error))
            continue
        patcher.run(patch_item)
    return patcher, len(skipped)


# ---------------------------------------------------------------------------------------------------------------------
# The command line.

def default_work(layout, tool):
    """The work folder beside the clone: <parent of the clone>/docs-work/<tool> (plan/pipelines.md §2)."""
    return os.path.join(os.path.dirname(layout.root), 'docs-work', tool)


def open_engine(path, layout, required=True):
    if not path:
        if required:
            raise UsageError('name the pin clone with --engine <folder> (or set STRATA_ENGINE) (plan/pipelines.md §1.2)')
        return None
    try:
        engine = repo.Engine(path)
        engine.resolve(repo.read_pin(layout.pin_file)['commit'])
    except repo.EngineError as error:
        raise UsageError('%s (plan/pipelines.md §1.4, check 1)' % error)
    return engine


def read_pin(layout):
    try:
        return repo.read_pin(layout.pin_file)
    except (OSError, ValueError) as error:
        raise UsageError('%s: engine.pin names the pin (plan/pipelines.md §1.1)' % error)


def run_build_record(engine, build, package):
    """The build as the stamp records it: the pin build (inside the clone), or a release package with its archive."""
    record = editor.build_record(build, engine.path)
    if record['kind'] == 'pin-build':
        if package:
            raise UsageError('--package names a release package\'s archive, but --build %s is the pin build inside the clone: leave out '
                             '--package, or name the unpacked package with --build' % build)
        return record
    if not package or not os.path.isfile(package):
        raise UsageError('--build %s is outside the clone, so it is a release package: name the archive it was unpacked from with '
                         '--package <archive> (plan/pipelines.md §1.3, §6.4)' % build)
    record['package'] = os.path.basename(package)
    record['packageSha256'] = files.sha256_file(package)
    return record


def main(argv=None):
    repo.utf8_output()
    parser = argparse.ArgumentParser(description='The book\'s tutorials: check, compile, run and patch (plan/pipelines.md §6).',
                                     epilog=__doc__.split('\n\n', 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['check', 'compile', 'run', 'patch'])
    parser.add_argument('pages', nargs='*', help='page ids, or exercises <page id>/exercise-<n> (default: every tutorial)')
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--engine', default=repo.c_DefaultEngine, help='the pin clone (default: $STRATA_ENGINE)')
    parser.add_argument('--dumps', help='check: reference/_dumps/<pin>')
    parser.add_argument('--release', action='store_true', help='check: downloads not written and stamps not current are errors')
    parser.add_argument('--build', help='run: the pin build\'s bin/Release folder, or an unpacked release package')
    parser.add_argument('--package', help='run: the archive of the release package --build was unpacked from')
    parser.add_argument('--build-dir', help='patch: the patch build\'s folder, <clone>/build/docs-patch')
    parser.add_argument('--work', help='run, patch: the work folder (default: docs-work/tutorials beside the clone)')
    parser.add_argument('--record-examples', action='store_true', help='run: write reference/_examples/<command>.json')
    parser.add_argument('--pictures', action='store_true', help='run: pictures of each stage (phase B, with the GPU)')
    parser.add_argument('--quiet', action='store_true', help='check: print errors only')
    options = parser.parse_args(argv)
    layout = repo.Layout(options.root)
    engine = None
    try:
        pin = read_pin(layout)
        if options.command == 'check':
            if not options.dumps:
                parser.error('check needs --dumps reference/_dumps/<pin>')
            engine = open_engine(options.engine, layout, required=False)
            report = check(layout, engine, pin, options.dumps, options.pages, options.release)
            for where, message in report.errors:
                print('%s: %s' % (where, message))
            if not options.quiet:
                for where, message in report.notes:
                    print('%s: note: %s' % (where, message))
            print('tutorials: %d error%s, %d note%s%s' % (len(report.errors), '' if len(report.errors) == 1 else 's', len(report.notes),
                                                          '' if len(report.notes) == 1 else 's', ' (release)' if options.release else ''))
            return 1 if report.errors else 0
        if options.command == 'compile':
            engine = open_engine(options.engine, layout, required=False)
            written = compile_downloads(layout, engine, pin, options.pages)
            for relative, state in written:
                if state != 'unchanged':
                    print('%s: %s' % (relative, state))
            print('tutorials: %d download%s written, %d unchanged, %d removed' % (
                sum(1 for _, state in written if state == 'wrote'), '' if sum(1 for _, state in written if state == 'wrote') == 1 else 's',
                sum(1 for _, state in written if state == 'unchanged'), sum(1 for _, state in written if state == 'removed')))
            return 0
        if options.command == 'run':
            if options.pictures:
                raise UsageError('--pictures takes a whole-editor picture after each stage with the GPU: it runs in phase B, after engine '
                                 'release 0.8.0 (plan/pipelines.md §6.5, §13); run without it now')
            engine = open_engine(options.engine, layout)
            commit = engine.resolve(pin['commit'])
            editor.preflight_clone(engine, commit)
            editor.preflight_build(options.build, ('StrataEditor', 'StrataCLI'))
            record = run_build_record(engine, options.build, options.package)
            work = os.path.abspath(options.work or default_work(layout, 'tutorials'))
            runner, examples = run(layout, engine, commit, os.path.abspath(options.build), work, options.pages, options.record_examples, record)
            for line in runner.lines:
                print(line)
            for relative in examples:
                print('%s: recorded' % relative)
            print('tutorials: %d passed, %d failed, %d skipped%s' % (runner.passed, runner.failed, runner.skipped,
                                                                    '; every command and its answer are in %s' % runner.log.folder))
            return 1 if runner.failed else 0
        if options.command == 'patch':
            engine = open_engine(options.engine, layout)
            commit = engine.resolve(pin['commit'])
            editor.preflight_clone(engine, commit)
            build_dir = check_build_dir(engine.path, options.build_dir)
            cmake, ctest = shutil.which('cmake'), shutil.which('ctest')
            if not cmake or not ctest:
                raise UsageError('the patch runner needs cmake and ctest on the PATH (CMake 3.25 or later), which %s: put the folder of '
                                 'CMake\'s programs on the PATH' % ('are missing' if not cmake and not ctest else '%s is missing' % (
                                     'cmake' if not cmake else 'ctest')))
            work = os.path.abspath(options.work or default_work(layout, 'patch'))
            patcher, skipped = patch(layout, engine, commit, build_dir, work, options.pages, cmake, ctest)
            for line in patcher.lines:
                print(line)
            print('tutorials: %d passed, %d failed, %d skipped; every command\'s output is in %s' % (patcher.passed, patcher.failed, skipped,
                                                                                                  patcher.log.folder))
            return 1 if patcher.failed else 0
    except (UsageError, editor.PreflightError, RevertError) as error:
        print('tutorials: %s' % error, file=sys.stderr)
        return 2
    except RunError as error:
        print('%s' % error, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
