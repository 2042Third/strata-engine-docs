"""The book's tutorials as files (plan/pipelines.md §6): reading them, the reader's copies and downloads that
tools/tutorials.py compile writes, the credits a download carries, and whether a stamp is current.

Files:

- tutorials/<part>/<chapter>.tutorial.json: a page's tutorial (§6.2), checked against
  tools/schemas/tutorial.schema.json; tutorials/<part>/<chapter>/exercise-<n>.tutorial.json: an editor exercise's
  worked solution, in the same format, whose "page" is its page; tutorials/<part>/<chapter>/exercise-<n>.patch: an
  engine exercise's worked solution (§6.6).
- tutorials/<part>/<chapter>.stamp.json, and tutorials/<part>/<chapter>/exercise-<n>.stamp.json for an exercise: the
  runs (§6.4), written only by tutorials.py run and patch.
- public/downloads/tutorials/<part>/<chapter>/stage-<step>.commands.json: the reader's copy of a stage's commands, an
  engine command script; stage-<step>.zip: the project after a stage that has "endState" (tutorials.py run).
- public/downloads/tutorials/<part>/<chapter>.patch: the download of a patch tutorial's patch.
- public/downloads/solutions/<part>/<chapter>/exercise-<n>.zip (an editor exercise: each stage's reader copy,
  stage-<step>.commands.json, the files its stages copy at their paths in the project, and CREDITS.md when one of them is
  a CC BY file) and exercise-<n>.patch (an engine exercise).

Credits: the samples' CREDITS.md at the pin and tutorials/assets/CREDITS.md are tables in the samples' form (a row per
file or folder: Files, Source, Author, License, Attribution, Changes; a folder ends with "/"). A file is CC BY when the
License of its row starts with "CC-BY". A download that holds such a file (found by its bytes, so a renamed or imported
copy counts) holds a CREDITS.md with the rows of its CC BY files.
"""

import hashlib
import io
import json
import os
import re
import zipfile

from booklib import blocks, frontmatter, jsonpos, markdown, repo, steps

c_Schema = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'schemas', 'tutorial.schema.json')
c_Placeholders = ('@PROJECT@', '@BOOK@', '@WORK@', '@RELEASE@')
c_Release = '@RELEASE@'  # the folder of the release a tutorial runs against (run's --build), which holds Samples/
c_ReleaseForReader = '<release folder>'  # how pages write that folder for a reader, and so the reader's copy
c_Placeholder = re.compile(r'@[A-Z][A-Z0-9_]*@')
c_AbsolutePath = re.compile(r'^(?:[A-Za-z]:[\\/]|/|\\\\)')
c_ExerciseFile = re.compile(r'^exercise-(?P<number>[1-9][0-9]*)\.(?P<kind>tutorial\.json|patch)$')
c_EntityBinding = 'entityName.'  # the bindings the reader's copy gives the entities entityName finds
c_DownloadsFolder = 'public/downloads/'  # every stamp input below it is a download that tutorials.py compile writes
c_Checkpoint = re.compile(r'^\s*::checkpoint(?:\{(?P<attributes>[^}]*)\})?\s*$')
c_Solution = re.compile(r'(?<![\w-])solution="(?P<file>[^"]+)"')
c_ZipLimit = 10 * 1000 * 1000
c_ZipsLimit = 150 * 1000 * 1000
c_CreditsHeader = ('# Credits\n\nThe third-party files of this download and their terms, as the engine\'s samples and the book\'s '
                   'tutorial assets credit them.\n\n')
c_CreditsColumns = ('Files', 'Source', 'Author', 'License', 'Attribution', 'Changes')


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as file:
        for block in iter(lambda: file.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def read_bytes(path):
    with open(path, 'rb') as file:
        return file.read()


class Tutorial:
    """One tutorial file: a page's (exercise None) or an exercise's. data is None when the file is no JSON (error says
    why); lines maps JSON pointers to lines."""

    def __init__(self, layout, path):
        self.layout = layout
        self.path = path
        self.relative = os.path.relpath(path, layout.root).replace(os.sep, '/')
        inside = os.path.relpath(path, layout.tutorials).replace(os.sep, '/')
        self.exercise = None
        match = c_ExerciseFile.match(inside.rsplit('/', 1)[-1])
        if match and inside.count('/') >= 2:
            self.page = inside.rsplit('/', 1)[0]
            self.exercise = int(match.group('number'))
        else:
            self.page = inside[:-len('.tutorial.json')]
        self.key = self.page if self.exercise is None else '%s/exercise-%d' % (self.page, self.exercise)
        self.data = None
        self.lines = {}
        self.error = None
        try:
            with open(path, encoding='utf-8') as file:
                self.data, self.lines = jsonpos.load(file.read())
        except jsonpos.JsonError as error:
            self.error = str(error)
            self.error_line = error.line
        except (OSError, UnicodeDecodeError) as error:
            self.error = str(error)
            self.error_line = 1

    def where(self, *path):
        return '%s:%d' % (self.relative, jsonpos.line_of(self.lines, jsonpos.pointer_of(path)))

    @property
    def stamp_relative(self):
        if self.exercise is None:
            return 'tutorials/%s.stamp.json' % self.page
        return 'tutorials/%s/exercise-%d.stamp.json' % (self.page, self.exercise)

    @property
    def stages(self):
        stages = self.data.get('stages') if isinstance(self.data, dict) else None
        return [stage for stage in stages if isinstance(stage, dict)] if isinstance(stages, list) else []

    @property
    def starts_from(self):
        value = self.data.get('startsFrom') if isinstance(self.data, dict) else None
        return value if isinstance(value, dict) else {}

    @property
    def automation(self):
        """Whether the reader's copies run in an editor that serves automation (plan/pipelines.md §6.2)."""
        return isinstance(self.data, dict) and self.data.get('automation') is True

    @property
    def patch(self):
        value = self.data.get('patch') if isinstance(self.data, dict) else None
        return value if isinstance(value, dict) else None

    @property
    def exercises(self):
        """{exercise number: [doctest suites]} of the page's engine exercises (plan/pipelines.md §6.6)."""
        value = self.data.get('exercises') if isinstance(self.data, dict) else None
        found = {}
        for key, entry in (value.items() if isinstance(value, dict) else []):
            if key.isdigit() and isinstance(entry, dict) and isinstance(entry.get('tests'), list):
                found[int(key)] = [suite for suite in entry['tests'] if isinstance(suite, str)]
        return found

    def downloads_folder(self):
        """The folder of the stage downloads, relative to the book: none for an exercise (its download is one zip)."""
        return None if self.exercise is not None else 'public/downloads/tutorials/%s' % self.page


def find_tutorials(layout):
    """Every tutorial file of the book, sorted: the pages' and the exercises'. tutorials/assets/ is both the part assets'
    folder and the tutorials' import files: of its folders only a chapter's are walked, one with a <chapter>.tutorial.json
    beside it or an exercise file in it, so that no file among the import files counts as a tutorial."""
    found = []
    if not os.path.isdir(layout.tutorials):
        return found
    part_assets = os.path.join(layout.tutorials, 'assets')

    def chapter_folder(name):
        folder = os.path.join(part_assets, name)
        return os.path.isfile(folder + '.tutorial.json') or any(c_ExerciseFile.match(entry) for entry in os.listdir(folder))

    for folder, directories, names in os.walk(layout.tutorials):
        if os.path.normpath(folder) == os.path.normpath(part_assets):
            directories[:] = [name for name in directories if chapter_folder(name)]
        directories.sort()
        for name in sorted(names):
            if name.endswith('.tutorial.json'):
                found.append(Tutorial(layout, os.path.join(folder, name)))
    return sorted(found, key=lambda tutorial: tutorial.relative)


def exercise_patches(layout):
    """{relative path: (page id, number)} of every engine exercise, tutorials/<part>/<chapter>/exercise-<n>.patch."""
    found = {}
    if not os.path.isdir(layout.tutorials):
        return found
    for folder, directories, names in os.walk(layout.tutorials):
        directories.sort()
        for name in sorted(names):
            match = c_ExerciseFile.match(name)
            if match and match.group('kind') == 'patch':
                relative = os.path.relpath(os.path.join(folder, name), layout.root).replace(os.sep, '/')
                page = os.path.relpath(folder, layout.tutorials).replace(os.sep, '/')
                found[relative] = (page, int(match.group('number')))
    return found


def page_kind_and_checkpoints(layout, path):
    """(kind from the front matter or None, [(line, stage or None)] of the page's ::checkpoint directives)."""
    text = repo.read_text(path)
    data, _, _, _ = frontmatter.read(text)
    kind = data.get('kind') if isinstance(data, dict) else None
    checkpoints = []
    fenced = set()
    total = text.count('\n') + 1
    for fence in markdown.fences(text):
        fenced.update(range(fence.open_line, (fence.close_line or total) + 1))
    for number, line in enumerate(text.split('\n'), 1):
        match = c_Checkpoint.match(line)
        if match and number not in fenced:
            stage = blocks.parse_attributes(match.group('attributes')).get('stage')
            checkpoints.append((number, int(stage) if stage and stage.isdigit() else None))
    return kind, checkpoints


def page_path(layout, page_id):
    return os.path.join(layout.docs, *page_id.split('/')) + '.md'


def offered_steps(layout, tutorial):
    """The stages of a page's tutorial file whose downloads its page offers (plan/pipelines.md §6.3): those its
    ::checkpoint directives name, or, on a how-to, which has none, the last (the build offers it at the end of "## Result",
    plan/site.md). Without its page every stage, which check reports."""
    numbers = [stage['step'] for stage in tutorial.stages if isinstance(stage.get('step'), int)]
    path = page_path(layout, tutorial.page)
    if not os.path.isfile(path):
        return set(numbers)
    kind, checkpoints = page_kind_and_checkpoints(layout, path)
    if checkpoints:
        return {stage for _, stage in checkpoints if stage in numbers}
    if kind == 'how-to' and numbers:
        return {max(numbers)}
    return set()


def solution_named(layout, page_id, relative):
    """Whether an answer of the page names the worked solution (solution="tutorials/<page>/exercise-<n>.…"), which makes
    the page link its download (src/plugins/answers.mjs)."""
    path = page_path(layout, page_id)
    return os.path.isfile(path) and any(match.group('file') == relative for match in c_Solution.finditer(repo.read_text(path)))


def made_downloads(layout, tutorial):
    """The downloads compile and run make of a tutorial file: the reader's copy and, after a stage with endState, the zip
    of each stage its page offers; an exercise's zip when an answer names it."""
    if tutorial.exercise is not None:
        named = solution_named(layout, tutorial.page, tutorial.relative)
        return {'public/downloads/solutions/%s/exercise-%d.zip' % (tutorial.page, tutorial.exercise)} if named else set()
    folder = tutorial.downloads_folder()
    offered = offered_steps(layout, tutorial)
    made = {'%s/%s' % (folder, stage_commands_name(step)) for step in offered}
    if 'sample' not in tutorial.starts_from:
        made |= {'%s/%s' % (folder, stage_zip_name(stage['step'])) for stage in tutorial.stages if stage.get('endState') and stage.get('step') in offered}
    return made


def page_tutorial_path(layout, page_id):
    return os.path.join(layout.tutorials, *(page_id + '.tutorial.json').split('/'))


# ---------------------------------------------------------------------------------------------------------------------
# The reader's copy of a stage (tools/tutorials.py compile).

def reader_copy(stage, release=c_ReleaseForReader):
    """The reader's copy of a stage's commands, an engine command script (plan/pipelines.md §6.3)."""
    return reader_script(stage.get('commands') or [], release)


def reader_script(commands, release=c_ReleaseForReader):
    """Commands as an engine command script: entityName becomes an entity.find step that binds the first match, which
    the step then names as its entity; checks and files are left out; expect, bind and until stay; @RELEASE@ becomes
    release (the reader's copy writes it as pages do, a run fills in the build's folder)."""
    script = []
    found = 0
    for step in commands:
        converted = {key: step[key] for key in steps.c_ScriptKeys if key in step}
        if 'parameters' in converted:
            converted['parameters'] = replace_text(converted['parameters'], c_Release, release)
        if 'entityName' in step:
            found += 1
            name = '%s%d' % (c_EntityBinding, found)
            script.append({'command': 'entity.find', 'parameters': {'name': step['entityName']}, 'bind': {name: '/entities/0'}})
            parameters = dict(converted.get('parameters') or {})
            parameters['entity'] = {'$ref': name}
            converted['parameters'] = parameters
            converted = {key: converted[key] for key in steps.c_ScriptKeys if key in converted}
        script.append(converted)
    return script


def command_segments(stage):
    """[(files, commands)]: a stage's commands cut before each command that carries files, with the files copied before
    each part (none before the first). The engine's runner cannot copy files, so a reader's copy runs part by part."""
    segments = [([], [])]
    for step in stage.get('commands') or []:
        if step.get('files'):
            segments.append((step['files'], []))
        segments[-1][1].append(step)
    return segments


def replace_text(value, old, new):
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, dict):
        return {key: replace_text(item, old, new) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_text(item, old, new) for item in value]
    return value


def reader_copy_bytes(stage):
    return script_bytes(reader_copy(stage))


def script_bytes(script):
    return (json.dumps(script, indent='\t', ensure_ascii=False) + '\n').encode('utf-8')


def stage_copies(stage):
    """The files a stage copies, in order: its own, then those of its commands."""
    return list(stage.get('files') or []) + [entry for step in stage.get('commands') or [] for entry in step.get('files') or []]


def stage_commands_name(step):
    return 'stage-%d.commands.json' % step


def stage_zip_name(step):
    return 'stage-%d.zip' % step


def zip_bytes(files):
    """A zip of (name, bytes) pairs, the same bytes for the same files: sorted, fixed times, no extra fields."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.create_system = 3
            archive.writestr(info, data)
    return buffer.getvalue()


# The vendor key of the CMakePresets.json the editor writes into a project's script folder for the engine and toolchain
# of the machine it runs on (StrataEditor/src/Editor/ScriptBuild.cpp:51 at 822a7a46). That file holds the machine's
# paths, so the project's .gitignore keeps it out of version control and an editor writes its own when it is missing
# (ScriptBuild.h:101-103): a download leaves it out.
c_PresetsVendor = 'strata.dev/editor'


def editor_presets(name, data):
    """Whether a project's file is the CMakePresets.json the editor wrote, by the editor's own test (its vendor key:
    ScriptBuild.cpp:598); presets a project wrote itself are its own."""
    if name.replace('\\', '/').rsplit('/', 1)[-1] != 'CMakePresets.json':
        return False
    try:
        value = json.loads(data.decode('utf-8'))
    except ValueError:  # UnicodeDecodeError is a ValueError too
        return False
    vendor = value.get('vendor') if isinstance(value, dict) else None
    return isinstance(vendor, dict) and c_PresetsVendor in vendor


def machine_folder_line(data, folders):
    """(line number, folder) of the first line of a file that names one of the folders (each lowercase, with /), as
    written or escaped in JSON, or None. A folder counts where its name ends: "work" is not named by "workshop"."""
    text = data.decode('utf-8', 'replace').lower().replace('\\\\', '/').replace('\\', '/')
    patterns = [(folder, re.compile(re.escape(folder) + r'(?![a-z0-9._~-])')) for folder in folders]
    for number, line in enumerate(text.split('\n'), 1):
        for folder, pattern in patterns:
            if pattern.search(line):
                return number, folder
    return None


class SourceError(Exception):
    """A file a tutorial copies cannot be read."""


class Sources:
    """The files a tutorial's stages copy: book:<path> from this repository, an engine path at the pin."""

    def __init__(self, layout, engine=None, pin=None):
        self.layout = layout
        self.engine = engine
        self.pin = pin

    def is_book(self, source):
        return source.startswith('book:')

    def read(self, source):
        if self.is_book(source):
            path = os.path.join(self.layout.root, *source[len('book:'):].split('/'))
            if not os.path.isfile(path):
                raise SourceError('%s does not exist: write the file, or correct "from"' % source[len('book:'):])
            return read_bytes(path)
        if self.engine is None:
            raise SourceError('%s is an engine file, read at the pin: pass --engine <clone>' % source)
        found = self.engine.object(self.pin, source)
        if found is None or found[0] != 'blob':
            raise SourceError('the engine has no file %s at the pin: name a file of Samples/<sample>/Assets/ there' % source)
        return found[1]


def solution_files(tutorial, sources):
    """(name, bytes) of an editor exercise's download, without its CREDITS.md: each stage's reader copy and the files its
    stages copy, at their paths in the project. A path copied more than once (a change the exercise makes later) holds
    its last copy, as the exercise leaves the project: a zip names each file once. A path an earlier stage copied keeps
    that copy, which the earlier stage's commands start from, and a later stage's copy of it stands under
    stage-<step>/, which the reader copies over the project before running that stage's commands."""
    files = {}
    for stage in tutorial.stages:
        files[stage_commands_name(stage.get('step'))] = reader_copy_bytes(stage)
        earlier = set(files)
        for entry in stage_copies(stage):
            name = entry['to']
            if name in earlier:
                name = 'stage-%s/%s' % (stage.get('step'), name)
            files[name] = sources.read(entry['from'])
    return list(files.items())


def compiled_files(layout, tutorials, sources, credits):
    """{path relative to the book: bytes} of every download compile writes for the tutorials (plan/pipelines.md §6.3):
    the reader's copies of the pages' stages, the patches' downloads and the solutions' downloads."""
    written = {}
    for tutorial in tutorials:
        if not isinstance(tutorial.data, dict):
            continue
        if tutorial.exercise is None:
            folder = tutorial.downloads_folder()
            offered = offered_steps(layout, tutorial)
            for stage in tutorial.stages:
                if isinstance(stage.get('step'), int) and stage['step'] in offered:
                    written['%s/%s' % (folder, stage_commands_name(stage['step']))] = reader_copy_bytes(stage)
            patch = tutorial.patch
            if patch and isinstance(patch.get('file'), str):
                path = os.path.join(layout.root, *patch['file'].split('/'))
                if os.path.isfile(path):
                    written['public/downloads/tutorials/%s.patch' % tutorial.page] = read_bytes(path)
        elif solution_named(layout, tutorial.page, tutorial.relative):
            files = solution_files(tutorial, sources)
            files += credits.file_for(data for _, data in files)
            written['public/downloads/solutions/%s/exercise-%d.zip' % (tutorial.page, tutorial.exercise)] = zip_bytes(files)
    for relative, (page, number) in exercise_patches(layout).items():
        if solution_named(layout, page, relative):
            written['public/downloads/solutions/%s/exercise-%d.patch' % (page, number)] = read_bytes(os.path.join(layout.root, *relative.split('/')))
    return written


# ---------------------------------------------------------------------------------------------------------------------
# Credits of the files a download holds.

def credit_rows(text):
    """The rows of a credits table in the samples' form: [{column: cell}] in the file's order, with the row's own line."""
    rows = []
    header = None
    for line in text.split('\n'):
        if not line.startswith('|'):
            header = None if not line.strip() else header
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if header is None:
            header = cells
            continue
        if all(set(cell) <= set('-: ') for cell in cells):
            continue
        if len(cells) == len(header):
            row = dict(zip(header, cells))
            row['line'] = line
            rows.append(row)
    return rows


def row_paths(row):
    """The files or folders a row names: the backticked paths of its Files cell."""
    return re.findall(r'`([^`]+)`', row.get('Files', ''))


def is_cc_by(row):
    return row.get('License', '').upper().startswith('CC-BY')


class Credits:
    """The CC BY files the book may copy into a download, by the SHA-256 of their bytes: the samples' (Samples/<s>/
    CREDITS.md at the pin, when an engine is given) and tutorials/assets/CREDITS.md's."""

    def __init__(self, layout, engine=None, pin=None):
        self.by_sha = {}
        self.engine_read = engine is not None
        assets = os.path.join(layout.tutorials, 'assets')
        credits = os.path.join(assets, 'CREDITS.md')
        if os.path.isfile(credits):
            with open(credits, encoding='utf-8') as file:
                for row in credit_rows(file.read()):
                    if is_cc_by(row):
                        for path in row_paths(row):
                            self.add_local(os.path.join(assets, *path.strip('/').split('/')), row)
        if engine is not None:
            samples = engine.tree(pin, 'Samples') or {}
            for sample, (mode, _) in sorted(samples.items()):
                if mode != '40000':
                    continue
                lines = engine.read(pin, 'Samples/%s/CREDITS.md' % sample)
                for row in credit_rows('\n'.join(lines or [])):
                    if is_cc_by(row):
                        for path in row_paths(row):
                            self.add_engine(engine, pin, 'Samples/%s/%s' % (sample, path.strip('/')), row)

    def add_local(self, path, row):
        if os.path.isfile(path):
            self.by_sha[sha256_file(path)] = row
        elif os.path.isdir(path):
            for folder, _, names in os.walk(path):
                for name in names:
                    self.by_sha[sha256_file(os.path.join(folder, name))] = row

    def add_engine(self, engine, pin, path, row):
        found = engine.object(pin, path)
        if found is None:
            return
        if found[0] == 'blob':
            self.by_sha[sha256_bytes(found[1])] = row
            return
        for name, (mode, _) in (engine.tree(pin, path) or {}).items():
            self.add_engine(engine, pin, '%s/%s' % (path, name), row)

    def rows_for(self, contents):
        """The credit rows of the CC BY files among the bytes given, in a stable order, once each."""
        rows = []
        for data in contents:
            row = self.by_sha.get(sha256_bytes(data))
            if row is not None and row['line'] not in rows:
                rows.append(row['line'])
        return sorted(rows)

    def text_for(self, rows):
        return (c_CreditsHeader + '| ' + ' | '.join(c_CreditsColumns) + ' |\n|' + ' --- |' * len(c_CreditsColumns) + '\n'
                + '\n'.join(rows) + '\n')

    def file_for(self, contents):
        """[('CREDITS.md', bytes)] when the files hold a CC BY file, else []."""
        rows = self.rows_for(list(contents))
        return [('CREDITS.md', self.text_for(rows).encode('utf-8'))] if rows else []


# ---------------------------------------------------------------------------------------------------------------------
# Stamps (plan/pipelines.md §6.4).

def read_stamp(layout, tutorial):
    """(stamp, problem): the stamp's data, or None with why."""
    path = os.path.join(layout.root, *tutorial.stamp_relative.split('/'))
    if not os.path.isfile(path):
        return None, '%s does not exist' % tutorial.stamp_relative
    try:
        with open(path, encoding='utf-8') as file:
            stamp = json.load(file)
    except ValueError as error:
        return None, '%s is not valid JSON (%s)' % (tutorial.stamp_relative, error)
    if not isinstance(stamp, dict) or stamp.get('page') != tutorial.page or not isinstance(stamp.get('runs'), list):
        return None, '%s is not the stamp of %s ("page" and a list of "runs")' % (tutorial.stamp_relative, tutorial.page)
    return stamp, None


def inputs_problem(layout, inputs, tutorial_relative, absent=None, made=None):
    """Why a run's inputs are not the files as they are now, or None. Given a list as absent, an input under
    public/downloads/ that does not exist (a download that tutorials.py compile writes) is added to it instead; given the
    downloads the tutorial makes, a missing one it no longer makes (no page offers it) is passed over."""
    if not isinstance(inputs, dict) or not inputs:
        return 'it records no inputs'
    if tutorial_relative not in inputs:
        return 'its inputs do not hold %s' % tutorial_relative
    for name, digest in sorted(inputs.items()):
        if name.startswith('/') or '..' in name.split('/') or c_AbsolutePath.match(name):
            return 'the input "%s" is not a path of this repository' % name
        path = os.path.join(layout.root, *name.split('/'))
        if not os.path.isfile(path):
            if made is not None and name.startswith(c_DownloadsFolder) and name not in made:
                continue
            if absent is not None and name.startswith(c_DownloadsFolder):
                absent.append(name)
                continue
            return 'the input %s does not exist' % name
        if sha256_file(path) != digest:
            return '%s changed since the run' % name
    return None


def stamp_problems(layout, tutorial, pin, changes_engine=False):
    """Why the stamp of a tutorial is not current, as a list (empty when it is): a run by a pin build or a patch build
    passed at the pin with the inputs as they are now, and at a release pin a run of the release's package passed too
    (a tutorial that changes the engine cannot run in a package, so it needs none). changes_engine: its chain applies a
    patch (a file without stages or patch that starts from a patch tutorial, which patch runs)."""
    patched = bool(tutorial.patch) or changes_engine
    command = 'patch' if patched else 'run'
    stamp, problem = read_stamp(layout, tutorial)
    if problem:
        return [problem + ': run it with python -I tools/tutorials.py %s %s' % (command, tutorial.key)]
    reasons = []
    absent = []
    made = None if tutorial.patch else made_downloads(layout, tutorial)

    def current(kinds):
        for position, run in enumerate(stamp['runs']):
            if not isinstance(run, dict) or run.get('passed') is not True or (run.get('build') or {}).get('kind') not in kinds:
                continue
            if run.get('engineCommit') != pin['commit']:
                reasons.append('run %d was at engine %s, not at the pin %s' % (position + 1, str(run.get('engineCommit'))[:8], pin['commit'][:8]))
                continue
            missing = []
            problem = inputs_problem(layout, run.get('inputs'), tutorial.relative, missing, made)
            if problem is None and missing:
                # Only downloads are missing: the run holds again once compile has written them with the same bytes.
                if len(missing) == 1:
                    problem = 'the input %s does not exist' % missing[0]
                else:
                    problem = 'the inputs %s do not exist' % ', '.join(missing)
                absent.extend(missing)
            if problem:
                reasons.append('run %d: %s' % (position + 1, problem))
                continue
            return True
        return False

    def because():
        return ' (%s)' % '; '.join(dict.fromkeys(reasons)) if reasons else ''

    def compiled():
        """The remedy when all a passing run lacks is downloads that compile writes (the reasons name them), or None."""
        if not absent:
            return None
        return ('write the missing downloads with python -I tools/tutorials.py compile %s, and run the tutorial again only if check '
                'still finds the stamp not current' % tutorial.key)

    problems = []
    if not current(('pin-build', 'patch-build')):
        problems.append('%s is not current: no run by a pin build or a patch build passed at the pin with the inputs as they '
                        'are now%s: %s' % (tutorial.stamp_relative, because(), compiled() or
                                           'run the tutorial again with python -I tools/tutorials.py %s %s, under the perf lock%s'
                                           % (command, tutorial.key, ' (phase B)' if command == 'patch' else '')))
    del reasons[:]
    del absent[:]
    if not pin['prerelease'] and not patched and not current(('package',)):
        problems.append('%s is not current: at a release pin a run of the release\'s package passes too%s: %s' % (
            tutorial.stamp_relative, because(), compiled() or 'run it with python -I tools/tutorials.py run %s --build <the unpacked '
            'package> --package <its archive>, under the perf lock' % tutorial.key))
    return problems
