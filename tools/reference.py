#!/usr/bin/env python3
"""The generated reference (plan/pipelines.md §7): the engine's tables, dumped from a --no-gpu editor and parsed from the
source at the pin, rendered as Markdown that the reference pages include (plan/site.md, "Generated reference").

    python <engine>/Tools/PerfLock.py --label docs-reference --wait 120 -- python -I tools/reference.py dump
        --engine <clone> --build <bin> [--work <dir>] [--only <dump>,...]
    python -I tools/reference.py parse  --engine <clone>
    python -I tools/reference.py render [--check]
    python -I tools/reference.py check  --engine <clone>

dump      Starts one --no-gpu editor without a project (pipelines.md §1.4 and §2: preflight, a private session folder,
          the work folder's recent projects and script builds, editor.quit {force: true} and the process tree ended
          after) and runs editor.status {sections: ["engine"]} (preflight), editor.commands, preferences.get,
          project.templates, project.samples, project.create {directory: <work>/Empty, name: "Empty", template:
          "empty"}, project.settings, component.list, scene.new {name: "Defaults"} and, for each component whose addable
          is true, entity.create {name: "Defaults"}, component.add {entity, component}, entity.get {entity} and
          entity.delete {entities: [entity]}; then editor.quit. It writes reference/_dumps/<pin>/<dump>.json for the
          dumps commands, preferences, templates, samples, settings, components and component-defaults, each
          {"pin": <full pin>, "engineCommit": <12 hex>, "command": <name>, "result": ...}. --only names the dumps of
          this run (each run starts its own editor and leaves the other files alone), so that a long dump can be run
          one hold of the perf lock at a time (rulings 5, R19). What a dump keeps of a result:
            preferences         the sections' id, title, category, description, version and schema; never the
                                person's values, the file's path or its state (pipelines.md §2: the reference
                                shows the schema's defaults)
            samples             each picture as a path relative to --build
            settings            the result of a new empty project (its values are the defaults)
            component-defaults  {"components": [{"component", "values", "inactive", "added"} or {"component",
                                "error"}]}: entity.get's values of the component on a new entity, the properties it
                                reports inactive, and the components the add brought along; a component that
                                component.add refuses is kept with its error
          No dump may hold a path of this machine: a string that names the clone, the build, the work folder, the
          temporary folder or the home folder, or that is an absolute path, stops the run before anything is written.
          It fails (exit 1) when a command other than the per-component steps fails, and writes nothing then; exit 2
          on a preflight check.
parse     Reads the pin clone at the pin (files through one git cat-file process, searches through git grep) and writes
          reference/_dumps/<pin>/parsed/<route>.json, each {"pin": <full pin>, ...}. It fails (exit 1, writing nothing)
          when a route finds nothing where the pin has something. The routes (pipelines.md §7.1; their sources at the
          pin in brackets):
            commands      each registration's MayDefer, WaitsForAssets, Results and Kind, and the MCP toolsets: core,
                          exact names, prefixes, the known toolsets (StrataEditor/src,
                          StrataCLI/src/CLI/McpToolsets.cpp)
            components    every ComponentRegistry::Register chain: type, flags, its properties and their flags;
                          SetInactiveReason calls with the messages their functions return; hidden and NoSerialize
                          components and hidden or transient properties, which component.list leaves out
            asset-types   the AssetType enum, and each importer's GetVersion() const override { return N; } with its
                          type (Strata/src/Strata/Asset)
            quality       the lines c_<Row>Row = { Low, Medium, High, Ultra } and the Renderer.Quality fields the
                          source registers (Strata/src/Strata/Renderer/RendererQuality.cpp)
            gpu-stages    the names passed to RegisterGPUStage and to RegisterStage(..., FrameStageKind::GPU)
            render-stats  the keys of the renderStats object (EditorStateCommands.cpp, DescribeRenderStats)
            renderer      the fields of SceneRendererSpecification and SceneRendererStats (SceneRenderer.h)
            perf-log      the columns of FramePerfLog and of each MakePerfLogColumns, with the header's descriptions
            options       the c_Arguments arrays of the editor and the runtime and the CLI's usage text, in the form
                          tools/names.py reads ({"programs": ...}) and with every description ({"details": ...})
            script-api    StrataScriptHostAPI and StrataScriptClassDesc in declaration order, each host function's
                          "added in" (the first release tag that contains the commit git log -S<name> finds in
                          ScriptABI.h), the SDK's public functions by the rules of SDKReader with their // comments,
                          and its public macros
            performance   StrataTests/Perf/Budgets.json
            limits        the constants tools/reference-limits.json lists as (file, name); every entry must resolve
            build         option( in CMakeLists.txt and CMake/*.cmake, CMakePresets.json, the CTest names and labels of
                          StrataTests/CMakeLists.txt, StrataTests/CoreShards.json
            tests         {"suites": doctest suites, "ctest": CTest names} (tools/names.py)
            macros        {"macros": every ST_ macro a #define or a CMake compile definition at
                          the pin defines} (tools/names.py)
            frame-stages  {"stages": the frame profiler's stage names: c_BuiltinFrameStages, the first string of
                          RegisterStage, RegisterGPUStage and ST_PROFILE_STAGE, ProfileStage = "…"} (tools/names.py);
                          "cpu": each stage no RegisterGPUStage or FrameStageKind::GPU registers, the built-in ones
                          first in their order: {"name", "declared": [{"by", "file", "line"}], "timed": [{"file",
                          "line"}] (its ST_PROFILE_STAGE scopes), "inWorkTime"}, for cpu-stages.md
            paths         {"paths": every file of git ls-tree -r <pin>, "submodules": {path: commit}} (tools/names.py)
            ui-literals   {"literals": the C++ string literals of StrataEditor/src/UI/, Panels/ and EditorLayer.cpp,
                          adjacent ones joined, ImGui ## suffixes removed} (tools/names.py)
render    Pure Python: reads the dumps, the parsed tables, reference/_examples/<command>.json ({"pin", "command",
          "parameters", "result"}), the figure manifests and their taken.json, and writes src/generated/reference/:
            commands-*.md        every command: description, kind, results, MCP toolsets, MayDefer, the asset scan,
                                 its registration, parameters as a table, the JSON Schema (and an example result) in a
                                 closed <details> as a json fence; commands-toolsets.md and one commands-<group>.md per
                                 group (in lowercase), which the one page reference/commands includes. When that page
                                 would exceed the largest page of tools/budgets.json the render fails: the page stays
                                 one page (rulings 13, R59). The estimate, fitted to the release's built reference pages:
                                 102 KB of the page's own markup, 1.46 times the Markdown outside code fences, 289 bytes
                                 per line of a fence.
            debug-views.md       the debugView enum of viewport.capture
            components.md        per category, each component and its properties: type, default (component-defaults),
                                 range or options, inactive reasons; the components and properties the list leaves out
            settings.md          the project settings sections: fields, defaults, schemas
            preferences.md       the preference sections: schemas and defaults, never a person's values
            asset-types.md       the AssetType enum and the importers with their versions
            asset-budgets.md     the asset settings sections, asset.stats and asset.setBudget
            quality.md           the quality rows in the four presets, as the Renderer.Quality fields write them
            gpu-stages.md, render-stats.md, renderer.md, perf-log.md
            cpu-stages.md        the CPU stages of the frame: where each is declared and timed, and whether it lies
                                 in the work time (rulings-10.md, R48)
            options-editor.md, options-runtime.md, options-cli.md
            script-api.md        host functions (with "added in"), class callbacks, the SDK by class and
                                 namespace, macros
            performance.md, limits.md, build.md
            figures.md           every figure: what it shows, its recipe, its state and GPU (taken.json)
            values.json          a flat map of keys to numbers or strings (pipelines.md §7.3): engine.commit;
                                 commands.count, commands.<kind>.count, toolsets.count, toolsets.core.count;
                                 components.count, components.addable.count; settings.count, preferences.count;
                                 assetTypes.count, importer.<type>.version; quality.<field>.<Low|Medium|High|Ultra>;
                                 debugViews.count, gpuStages.count, cpuStages.count, renderStats.count; hostFunctions.count,
                                 scriptCallbacks.count, sdkClasses.count; perfBudgets.count; limits.<name> (:: as .);
                                 cmakeOptions.count, ctest.count, doctestSuites.count; figures.count; samples.count,
                                 templates.count
          Each table starts with <!-- generated by tools/reference.py render <version>; engine <full pin>; sha256 <hex
          of the rest of the file>; do not edit -->. Engine text is escaped for Markdown and HTML, never raw HTML.
          It fails (exit 1, writing nothing) when the dumps and parsed tables do not fit together (a command the
          parse finds no registration of, a quality row none of whose field's options it can write, a High value that
          is not the field's default).
          With --check it writes nothing and fails (exit 1) when a committed file differs from what render writes,
          when a stamp names another commit than engine.pin's or its sha256 does not match the file, or when a dump's
          pin is not engine.pin's commit or its engineCommit is not a prefix of it.
check     Runs parse and render into a temporary folder and fails (exit 1) when the result differs from the committed
          parsed/ and src/generated/reference/, and on everything render --check fails on.

Every message names the file and, where there is one, the line, and says what to do. Only the standard library is
used. Exit codes: 0 all is well, 1 problems were found, 2 usage or environment errors (and every preflight check of
pipelines.md §1.4).
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import editor, markdown, repo, routes, tables  # noqa: E402

c_Dumps = ('commands', 'preferences', 'templates', 'samples', 'settings', 'components', 'component-defaults')
c_DumpCommands = {'commands': 'editor.commands', 'preferences': 'preferences.get', 'templates': 'project.templates',
                  'samples': 'project.samples', 'settings': 'project.settings', 'components': 'component.list',
                  'component-defaults': 'entity.get'}
c_WorkMarker = '.reference-dump'
c_Tools = os.path.dirname(os.path.abspath(__file__))
c_LimitsPath = os.path.join(c_Tools, 'reference-limits.json')  # the scene and world limits (pipelines.md §7.1)
c_BudgetsPath = os.path.join(c_Tools, 'budgets.json')  # the largest page's budget, which splits the commands table
# An absolute path: a drive (C:\, C:/), a share (\\host), a home or temporary folder, or an MSYS2 drive (/c/).
c_ValueDirective = re.compile(r':value\{key="(?P<key>[^"]*)"\}')  # as tools/pages.py reads it
c_DriveOrRoot = re.compile(r'^(?:[A-Za-z]:[\\/]|\\\\|/(?:home|Users|tmp|var|private|mnt|[A-Za-z])/)')


class UsageError(Exception):
    """A usage or environment problem: exit code 2."""


class DumpError(Exception):
    """A command of the dump failed, or a result holds something the dump may not keep: exit code 1."""


def dumps_folder(layout, pin):
    return os.path.join(layout.root, 'reference', '_dumps', pin)


def generated_folder(layout):
    return os.path.join(layout.root, 'src', 'generated', 'reference')


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    repo.write_text(path, json.dumps(data, indent='\t', ensure_ascii=False, sort_keys=False) + '\n')


def default_work(layout, tool):
    """The work folder beside the clone: <parent of the clone>/docs-work/<tool> (plan/pipelines.md §2)."""
    return os.path.join(os.path.dirname(layout.root), 'docs-work', tool)


def open_engine(path, layout):
    try:
        engine = repo.Engine(path)
        pin = engine.resolve(repo.read_pin(layout.pin_file)['commit'])
    except repo.EngineError as error:
        raise UsageError('%s (pipelines.md §1.4, check 1)' % error)
    return engine, pin


# ---------------------------------------------------------------------------------------------------------------------
# dump.

def prepare_work(work):
    """Empties the work folder of the previous dump (only a folder this tool marked as its own)."""
    marker = os.path.join(work, c_WorkMarker)
    if os.path.isdir(work) and os.listdir(work):
        if not os.path.isfile(marker):
            raise UsageError('the work folder %s holds files that are not a dump of reference.py: name an empty folder with --work' % work)
        for entry in os.listdir(work):
            path = os.path.join(work, entry)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    os.makedirs(work, exist_ok=True)
    repo.write_text(marker, 'A dump of tools/reference.py; the next dump empties this folder.\n')


def reduce_preferences(result):
    """The sections' description and schema only: the person's values, the file and its state are never kept (§2)."""
    keep = ('id', 'title', 'category', 'description', 'version', 'schema')
    sections = result.get('sections') if isinstance(result, dict) else None
    if not isinstance(sections, list):
        raise DumpError('preferences.get answered without a list of sections: compare with '
                        'StrataEditor/src/Editor/EditorPreferencesCommands.cpp at the pin')
    return {'sections': [{key: section[key] for key in keep if key in section} for section in sections]}


def relative_pictures(result, build):
    """project.samples with each picture relative to the build (the build's Samples/ folder)."""
    samples = result.get('samples') if isinstance(result, dict) else None
    if not isinstance(samples, list):
        raise DumpError('project.samples answered without a list of samples: compare with '
                        'StrataEditor/src/Editor/EditorAssetCommands.cpp at the pin')
    base = os.path.normcase(os.path.abspath(build))
    out = []
    for sample in samples:
        sample = dict(sample)
        picture = sample.get('picture')
        if isinstance(picture, str):
            absolute = os.path.normcase(os.path.abspath(picture))
            if not absolute.startswith(base + os.sep):
                raise DumpError('project.samples names the picture %s, which is outside the build %s: the dump keeps pictures '
                                'relative to the build' % (picture, build))
            sample['picture'] = os.path.relpath(os.path.abspath(picture), os.path.abspath(build)).replace(os.sep, '/')
        out.append(sample)
    return dict(result, samples=out)


def machine_strings(build, work, engine_path, session):
    """The folders of this machine no dump may name, each as it may be spelled (both slashes, any case)."""
    folders = {os.path.abspath(build), os.path.abspath(work), os.path.abspath(engine_path), editor.system_temp(), os.path.expanduser('~')}
    if session:
        folders.add(session)
    spelled = set()
    for folder in folders:
        if not folder or len(folder) < 4:
            continue
        for variant in (folder, folder.replace('\\', '/'), folder.replace('/', '\\')):
            spelled.add(variant.lower())
    return spelled


def find_machine_paths(value, forbidden, pointer=''):
    """[(pointer, string)] of every string in value that names a folder of this machine or is an absolute path."""
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            found += find_machine_paths(item, forbidden, '%s/%s' % (pointer, str(key).replace('~', '~0').replace('/', '~1')))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found += find_machine_paths(item, forbidden, '%s/%d' % (pointer, index))
    elif isinstance(value, str):
        lowered = value.lower()
        if c_DriveOrRoot.match(value) or any(folder in lowered for folder in forbidden):
            found.append((pointer or '/', value))
    return found


def dump_component_defaults(session, components):
    """For each addable component: its values on a new entity (entity.get), or the error component.add gave."""
    probe = session.call('entity.create', {'name': 'Defaults'})
    probe_id = probe.get('id') if isinstance(probe, dict) else None
    if not probe_id:
        raise DumpError('entity.create answered without an id: compare with StrataEditor/src/Editor/Commands/EntityCommands.cpp at the pin')
    base = set((session.call('entity.get', {'entity': probe_id}).get('components') or {}).keys())
    session.call('entity.delete', {'entities': [probe_id]})
    records = []
    for component in components:
        if not component.get('addable'):
            continue
        name = component['name']
        created = session.call('entity.create', {'name': 'Defaults'})
        entity = created.get('id') if isinstance(created, dict) else None
        if not entity:
            raise DumpError('entity.create answered without an id while dumping the defaults of %s' % name)
        try:
            try:
                session.call('component.add', {'entity': entity, 'component': name})
            except editor.EditorError as error:
                records.append({'component': name, 'error': str(error).split(': ', 1)[-1]})
                continue
            described = session.call('entity.get', {'entity': entity})
            values = (described.get('components') or {}) if isinstance(described, dict) else {}
            if name not in values:
                records.append({'component': name, 'error': 'component.add succeeded but entity.get shows no %s' % name})
                continue
            record = {'component': name, 'values': values[name]}
            inactive = (described.get('inactive') or {}).get(name)
            if inactive:
                record['inactive'] = inactive
            added = sorted(set(values) - base - {name})
            if added:
                record['added'] = added
            records.append(record)
        finally:
            session.call('entity.delete', {'entities': [entity]})
    return {'components': records}


def dump(layout, engine, pin, build, work, only):
    """Runs the dumps named in only (all of them by default) in one editor and writes them; returns the files written."""
    wanted = list(only or c_Dumps)
    prepare_work(work)
    log = editor.Log(os.path.join(work, 'log'))
    session = editor.Editor(build, work, log)
    results = {}
    try:
        session.launch()
        status = session.check_commit(pin)
        reported = status['engineCommit']
        if 'commands' in wanted:
            results['commands'] = session.call('editor.commands')
        if 'preferences' in wanted:
            results['preferences'] = reduce_preferences(session.call('preferences.get'))
        if 'templates' in wanted:
            results['templates'] = session.call('project.templates')
        if 'samples' in wanted:
            results['samples'] = relative_pictures(session.call('project.samples'), build)
        if set(wanted) & {'settings', 'components', 'component-defaults'}:
            if set(wanted) & {'settings', 'component-defaults'}:
                session.call('project.create', {'directory': os.path.join(work, 'Empty'), 'name': 'Empty', 'template': 'empty'},
                             timeout=editor.c_OpenSeconds)
            if 'settings' in wanted:
                results['settings'] = session.call('project.settings')
            listed = session.call('component.list')
            if 'components' in wanted:
                results['components'] = listed
            if 'component-defaults' in wanted:
                session.call('scene.new', {'name': 'Defaults'}, timeout=editor.c_OpenSeconds)
                results['component-defaults'] = dump_component_defaults(session, listed.get('components') or [])
    except editor.EditorError as error:
        raise DumpError('%s; every command and its answer are in %s' % (error, log.folder))
    finally:
        forbidden = machine_strings(build, work, engine.path, session.session)
        session.quit()
    problems = []
    for name in wanted:
        for pointer, value in find_machine_paths(results[name], forbidden):
            problems.append('%s.json%s holds "%s", a path of this machine: the dump keeps no such path; change what reference.py keeps '
                            'of %s' % (name, pointer, value, c_DumpCommands[name]))
    if problems:
        raise DumpError('; '.join(problems))
    folder = dumps_folder(layout, pin)
    written = []
    for name in wanted:
        path = os.path.join(folder, name + '.json')
        write_json(path, {'pin': pin, 'engineCommit': reported, 'command': c_DumpCommands[name], 'result': results[name]})
        written.append(path)
    return written


# ---------------------------------------------------------------------------------------------------------------------
# parse, render, check.

def read_parsed(folder):
    """{route: data} of a parsed/ folder."""
    found = {}
    parsed = os.path.join(folder, 'parsed')
    if os.path.isdir(parsed):
        for name in sorted(os.listdir(parsed)):
            if name.endswith('.json'):
                with open(os.path.join(parsed, name), encoding='utf-8') as file:
                    found[name[:-5]] = json.load(file)
    return found


def write_parsed(folder, data):
    parsed = os.path.join(folder, 'parsed')
    if os.path.isdir(parsed):
        for name in os.listdir(parsed):
            if name.endswith('.json') and name[:-5] not in data:
                os.remove(os.path.join(parsed, name))
    for name, value in data.items():
        write_json(os.path.join(parsed, name + '.json'), value)


def parse(layout, engine, pin):
    """(data by route, problems) of every parsed route at the pin."""
    limits_path = c_LimitsPath
    release = repo.read_pin(layout.pin_file).get('release')
    return routes.parse_all(engine, pin, release, limits_path)


def render(layout, pin, folder):
    """{file name: text} of every generated file, from the dumps folder, the examples and the figures; and problems."""
    examples = os.path.join(layout.root, 'reference', '_examples')
    return tables.render_all(folder, pin, examples, layout, c_BudgetsPath)


def compare_files(expected, folder, label):
    """Problems where the files of folder differ from expected ({name: text}): changed, missing or extra."""
    problems = []
    present = set(name for name in os.listdir(folder)) if os.path.isdir(folder) else set()
    for name, text in sorted(expected.items()):
        path = os.path.join(folder, name)
        if name not in present:
            problems.append('%s/%s: missing: run python -I tools/reference.py render and commit it' % (label, name))
            continue
        if repo.read_text(path) != text:
            problems.append('%s/%s: differs from what render writes: run python -I tools/reference.py render and commit the result '
                            '(a generated file is never edited by hand)' % (label, name))
    for name in sorted(present - set(expected)):
        if name.endswith('.md') or name == 'values.json':
            problems.append('%s/%s: render writes no such file: remove it, or run python -I tools/reference.py render' % (label, name))
    return problems


def check_dumps(folder, pin, label):
    """Problems of the dumps' pins: every dump's pin is engine.pin's commit and its engineCommit a prefix of it."""
    problems = []
    if not os.path.isdir(folder):
        return ['%s: no dumps for the pin %s: run python -I tools/reference.py dump and parse at the pin' % (label, pin)]
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.json'):
            continue
        path = os.path.join(folder, name)
        try:
            with open(path, encoding='utf-8') as file:
                data = json.load(file)
        except ValueError as error:
            problems.append('%s/%s: not valid JSON (%s): run python -I tools/reference.py dump again' % (label, name, error))
            continue
        if not isinstance(data, dict) or data.get('pin') != pin:
            problems.append('%s/%s: dumped at the pin %s, but engine.pin names %s: run python -I tools/reference.py dump at the pin'
                            % (label, name, data.get('pin') if isinstance(data, dict) else None, pin))
            continue
        reported = data.get('engineCommit')
        if not isinstance(reported, str) or reported == 'unknown' or not reported or not pin.startswith(reported):
            problems.append('%s/%s: the editor reported the engine commit %s, which is not a prefix of the pin %s: dump again with a '
                            'build of the pin (pipelines.md §1.3)' % (label, name, reported, pin))
    for name in sorted(read_parsed(folder)):
        data = read_parsed(folder)[name]
        if not isinstance(data, dict) or data.get('pin') != pin:
            problems.append('%s/parsed/%s.json: parsed at another pin than engine.pin\'s %s: run python -I tools/reference.py parse'
                            % (label, name, pin))
    return problems


def check_stamps(folder, pin, label):
    """Problems of the stamps of the committed tables: the commit is the pin's, the hash is the content's."""
    problems = []
    if not os.path.isdir(folder):
        return problems
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.md'):
            continue
        text = repo.read_text(os.path.join(folder, name))
        stamp = tables.read_stamp(text)
        if stamp is None:
            problems.append('%s/%s:1: no stamp "<!-- generated by tools/reference.py render …": run python -I tools/reference.py render'
                            % (label, name))
            continue
        if stamp['engine'] != pin:
            problems.append('%s/%s:1: the stamp names the engine %s, but engine.pin names %s: run python -I tools/reference.py dump, '
                            'parse and render at the pin' % (label, name, stamp['engine'], pin))
        if stamp['sha256'] != stamp['actual']:
            problems.append('%s/%s:1: the content does not match its stamp\'s sha256 (the file was edited by hand): run python -I '
                            'tools/reference.py render and commit the result' % (label, name))
    return problems


def page_value_problems(layout, values_text):
    """A page's :value{key=…} that render writes no key for (rulings-9.md, R41: a perf budget without a measurement has
    no perf.<name>.Measured; its page states the budget and says that it is provisional)."""
    values = json.loads(values_text)
    problems = []
    for _, path in layout.pages():
        for number, line in markdown.prose_lines(repo.read_text(path)):
            for match in c_ValueDirective.finditer(markdown.strip_inline_code(line)):
                if match.group('key') not in values:
                    problems.append('%s:%d: :value{key="%s"}: render writes no such key; name one that values.json lists, or, for a '
                                    'budget the reference machine has not measured, state the budget and say that it is provisional'
                                    % (layout.relative(path), number, match.group('key')))
    return problems


def render_check(layout, pin):
    folder = dumps_folder(layout, pin)
    label = layout.relative(folder)
    problems = check_dumps(folder, pin, label)
    generated = generated_folder(layout)
    problems += check_stamps(generated, pin, layout.relative(generated))
    if os.path.isdir(folder):
        files, render_problems = render(layout, pin, folder)
        problems += render_problems
        if not render_problems:
            problems += compare_files(files, generated, layout.relative(generated))
            problems += page_value_problems(layout, files['values.json'])
    return problems


def full_check(layout, engine, pin):
    """parse and render into a temporary folder, compared with the committed files; and render --check's checks."""
    folder = dumps_folder(layout, pin)
    label = layout.relative(folder)
    problems = check_dumps(folder, pin, label)
    data, parse_problems = parse(layout, engine, pin)
    problems += parse_problems
    if parse_problems:
        return problems
    committed = read_parsed(folder)
    for name in sorted(set(data) | set(committed)):
        if name not in committed:
            problems.append('%s/parsed/%s.json: missing: run python -I tools/reference.py parse and commit it' % (label, name))
        elif name not in data:
            problems.append('%s/parsed/%s.json: parse writes no such file: run python -I tools/reference.py parse' % (label, name))
        elif json.loads(json.dumps(data[name])) != committed[name]:
            problems.append('%s/parsed/%s.json: differs from what parse finds at the pin: run python -I tools/reference.py parse and '
                            'render, and commit both' % (label, name))
    temporary = tempfile.mkdtemp(prefix='reference-check-')
    try:
        for name in c_Dumps:
            source = os.path.join(folder, name + '.json')
            if os.path.isfile(source):
                shutil.copyfile(source, os.path.join(temporary, name + '.json'))
        write_parsed(temporary, data)
        files, render_problems = render(layout, pin, temporary)
        problems += render_problems
        generated = generated_folder(layout)
        problems += check_stamps(generated, pin, layout.relative(generated))
        if not render_problems:
            problems += compare_files(files, generated, layout.relative(generated))
            problems += page_value_problems(layout, files['values.json'])
    finally:
        shutil.rmtree(temporary, ignore_errors=True)
    return problems


def write_generated(layout, files):
    folder = generated_folder(layout)
    os.makedirs(folder, exist_ok=True)
    for name in os.listdir(folder):
        if (name.endswith('.md') or name == 'values.json') and name not in files:
            os.remove(os.path.join(folder, name))
    for name, text in sorted(files.items()):
        repo.write_text(os.path.join(folder, name), text)


def main(argv=None):
    repo.utf8_output()
    parser = argparse.ArgumentParser(description='The generated reference: dumps, parsed tables and rendered files (plan/pipelines.md §7).',
                                     epilog=__doc__.split('\n\n', 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['dump', 'parse', 'render', 'check'])
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--engine', default=repo.c_DefaultEngine, help='the pin clone (default: $STRATA_ENGINE)')
    parser.add_argument('--build', help='dump: the pin build\'s bin/Release folder')
    parser.add_argument('--work', help='dump: the work folder (default: docs-work/reference beside the clone)')
    parser.add_argument('--only', help='dump: the dumps of this run, comma separated (default: all of them: %s)' % ', '.join(c_Dumps))
    parser.add_argument('--check', action='store_true', help='render: write nothing; fail when the committed files differ')
    options = parser.parse_args(argv)
    layout = repo.Layout(options.root)
    engine = None
    try:
        if options.check and options.command != 'render':
            parser.error('--check belongs to render')
        if options.command != 'dump' and (options.build or options.work or options.only):
            parser.error('--build, --work and --only belong to dump')
        if options.command == 'dump':
            only = [name.strip() for name in (options.only or '').split(',') if name.strip()]
            unknown = [name for name in only if name not in c_Dumps]
            if unknown:
                parser.error('--only: %s; the dumps are %s' % (', '.join(unknown), ', '.join(c_Dumps)))
            engine, pin = open_engine(options.engine, layout)
            editor.preflight_clone(engine, pin)
            editor.preflight_build(options.build, ('StrataEditor', 'StrataCLI'))
            work = os.path.abspath(options.work or default_work(layout, 'reference'))
            written = dump(layout, engine, pin, options.build, work, only)
            for path in written:
                print('reference: wrote %s' % layout.relative(path))
            return 0
        if options.command == 'parse':
            engine, pin = open_engine(options.engine, layout)
            data, problems = parse(layout, engine, pin)
            for line in problems:
                print(line)
            if problems:
                print('reference: parse found %d problem%s and wrote nothing' % (len(problems), '' if len(problems) == 1 else 's'))
                return 1
            folder = dumps_folder(layout, pin)
            write_parsed(folder, data)
            print('reference: wrote %d parsed tables into %s' % (len(data), layout.relative(os.path.join(folder, 'parsed'))))
            return 0
        pin = repo.read_pin(layout.pin_file)['commit']
        if options.command == 'render':
            if options.check:
                problems = render_check(layout, pin)
                for line in problems:
                    print(line)
                print('reference: %d problem%s' % (len(problems), '' if len(problems) == 1 else 's'))
                return 1 if problems else 0
            folder = dumps_folder(layout, pin)
            if not os.path.isdir(folder):
                raise UsageError('no dumps at %s: run python -I tools/reference.py dump and parse at the pin' % layout.relative(folder))
            files, problems = render(layout, pin, folder)
            for line in problems:
                print(line)
            if problems:
                print('reference: render found %d problem%s and wrote nothing' % (len(problems), '' if len(problems) == 1 else 's'))
                return 1
            write_generated(layout, files)
            print('reference: wrote %d files into %s' % (len(files), layout.relative(generated_folder(layout))))
            # pipelines.md §7.3: the keys a page may write in :value{key=…} are the ones render lists here.
            keys = sorted(json.loads(files['values.json']))
            print('reference: values.json holds %d keys: %s' % (len(keys), ', '.join(keys)))
            return 0
        engine, pin = open_engine(options.engine, layout)
        problems = full_check(layout, engine, pin)
        for line in problems:
            print(line)
        print('reference: %d problem%s' % (len(problems), '' if len(problems) == 1 else 's'))
        return 1 if problems else 0
    except (UsageError, editor.PreflightError, ValueError, OSError) as error:
        print('reference: %s' % error, file=sys.stderr)
        return 2
    except DumpError as error:
        print('reference: %s' % error, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.close()


if __name__ == '__main__':
    sys.exit(main())
