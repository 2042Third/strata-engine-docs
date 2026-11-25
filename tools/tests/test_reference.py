"""Tests of tools/reference.py (plan/pipelines.md §7): dump with a stand-in editor, parse of a pretend engine
(tools/tests/fixtures/reference/engine/, committed into a git repository with release tags and a vendored submodule),
render, render --check and check."""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reference  # noqa: E402
from booklib import editor, repo, routes, tables  # noqa: E402
from tests import helpers  # noqa: E402

c_Fixtures = os.path.join(helpers.c_Fixtures, 'reference')
c_Engine = os.path.join(c_Fixtures, 'engine')
c_Limits = os.path.join(c_Fixtures, 'limits.json')
c_ABI = 'StrataScriptCore/Include/StrataScript/ScriptABI.h'
c_Entt = '#pragma once\nstruct entt_traits_32\n{\n    static constexpr entity_type entity_mask = 0xFFFFF;\n};\n'


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            code = function(list(arguments))
        except SystemExit as error:  # argparse's --help and usage errors
            code = error.code
    return code, output.getvalue()


def fixture_files():
    files = {}
    for folder, _, names in os.walk(c_Engine):
        for name in names:
            path = os.path.join(folder, name)
            with open(path, encoding='utf-8') as file:
                files[os.path.relpath(path, c_Engine).replace(os.sep, '/')] = file.read()
    return files


def make_engine():
    """The pretend engine: the script ABI in three commits (v0.1.0 and v0.2.0-rc1 on the first, v0.2.0 on the second, the
    third untagged), entt as a submodule. Returns (engine, pin)."""
    engine = helpers.TempEngine()
    files = fixture_files()
    abi = files[c_ABI]
    first = '\n'.join(line for line in abi.split('\n') if '(*GetFrameIndex)' not in line and '(*SetTimeScale)' not in line)
    second = '\n'.join(line for line in abi.split('\n') if '(*SetTimeScale)' not in line)
    engine.add_submodule('Strata/vendor/entt', {'src/entt/entity/entity.hpp': c_Entt}, 'https://github.com/skypjack/entt')
    engine.commit(dict(files, **{c_ABI: first}), 'first')
    engine.git('tag', 'v0.1.0')
    engine.git('tag', 'v0.2.0-rc1')
    engine.commit({c_ABI: second}, 'second')
    engine.git('tag', 'v0.2.0')
    pin = engine.commit({c_ABI: abi}, 'third')
    return engine, pin


def answers(home, build):
    with open(os.path.join(c_Fixtures, 'answers.json'), encoding='utf-8') as file:
        text = file.read()
    return json.loads(text.replace('@HOME@', home.replace('\\', '/')).replace('@BUILD@', build.replace('\\', '/')))


class FakeEditor:
    """A stand-in for booklib.editor.Editor: answers from tools/tests/fixtures/reference/answers.json; component.add refuses
    the component Broken."""
    calls = []
    data = {}
    session = None

    def __init__(self, build, work, log, project=None, gpu=False):
        self.log = log
        self.entities = {}
        self.count = 0
        self.session = FakeEditor.session

    def launch(self):
        FakeEditor.calls.append(('launch', None))
        return {'ProcessId': 1}

    def check_commit(self, pin):
        return {'engineCommit': pin[:12], 'platform': 'Windows', 'gpu': None}

    def call(self, command, parameters=None, timeout=300):
        FakeEditor.calls.append((command, parameters))
        if command in FakeEditor.data:
            value = FakeEditor.data[command]
            if isinstance(value, Exception):
                raise value
            return json.loads(json.dumps(value))
        if command == 'entity.create':
            self.count += 1
            entity = '%X' % (0xA0 + self.count)
            self.entities[entity] = {'Name': {'Name': 'Defaults'}, 'Transform': {'Translation': [0, 0, 0]}}
            return {'id': entity}
        if command == 'component.add':
            if parameters['component'] == 'Broken':
                raise editor.EditorError('component.add failed (StrataCLI exit code 1): Broken needs a camera')
            values = {'Camera': {'FieldOfView': 60.0, 'FocusDistance': 10.0},
                      'PostProcess': {'Bloom': False, 'BloomIntensity': 1.0, 'HistoryFrames': 8}}[parameters['component']]
            self.entities[parameters['entity']][parameters['component']] = values
            if parameters['component'] == 'PostProcess':
                self.entities[parameters['entity']]['Volume'] = {}
            return {}
        if command == 'entity.get':
            components = self.entities[parameters['entity']]
            result = {'id': parameters['entity'], 'components': components}
            if 'PostProcess' in components:
                result['inactive'] = {'PostProcess': {'BloomIntensity': 'Bloom is off'}}
            return result
        if command == 'entity.delete':
            for entity in parameters['entities']:
                self.entities.pop(entity, None)
            return {'count': len(parameters['entities'])}
        return {}

    def quit(self):
        FakeEditor.calls.append(('quit', None))


class ReferenceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine, cls.pin = make_engine()

    @classmethod
    def tearDownClass(cls):
        cls.engine.cleanup()

    def setUp(self):
        self.book = helpers.TempBook(pin_commit=self.pin)
        self.build = tempfile.mkdtemp(prefix='build-')
        for name in ('StrataEditor', 'StrataCLI'):
            with open(editor.program_path(self.build, name), 'wb') as file:
                file.write(b'program')
        self.work = os.path.join(tempfile.mkdtemp(prefix='work-'), 'reference')
        self.home = tempfile.mkdtemp(prefix='home-')
        FakeEditor.calls = []
        FakeEditor.data = answers(self.home, self.build)
        FakeEditor.session = os.path.join(self.home, 'StrataDocs-1-1')
        self.budgets = os.path.join(self.book.root, 'budgets.json')
        self.set_budget(770)

    def tearDown(self):
        self.book.cleanup()
        for folder in (self.build, os.path.dirname(self.work), self.home):
            shutil.rmtree(folder, ignore_errors=True)

    def set_budget(self, kilobytes):
        with open(self.budgets, 'w', encoding='utf-8') as file:
            json.dump({'largest_page_kilobytes': kilobytes}, file)

    def run_tool(self, *arguments):
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(reference, 'c_LimitsPath', c_Limits), \
                mock.patch.object(reference, 'c_BudgetsPath', self.budgets), mock.patch.object(editor, 'system_temp', lambda: self.home), \
                mock.patch.object(os.path, 'expanduser', lambda path: self.home if path == '~' else path):
            return quiet(reference.main, *arguments, '--root', self.book.root)

    def dump(self, *extra):
        return self.run_tool('dump', '--engine', self.engine.root, '--build', self.build, '--work', self.work, *extra)

    def dumps(self):
        return os.path.join(self.book.root, 'reference', '_dumps', self.pin)

    def read_dump(self, name):
        with open(os.path.join(self.dumps(), name + '.json'), encoding='utf-8') as file:
            return json.load(file)

    def make_all(self):
        code, output = self.dump()
        self.assertEqual(code, 0, output)
        code, output = self.run_tool('parse', '--engine', self.engine.root)
        self.assertEqual(code, 0, output)
        code, output = self.run_tool('render')
        self.assertEqual(code, 0, output)
        self.render_output = output

    def generated(self, name):
        return repo.read_text(os.path.join(self.book.root, 'src', 'generated', 'reference', name))


class DumpTests(ReferenceTestCase):
    def test_the_dump_runs_the_plan_s_commands_and_keeps_no_machine_path(self):
        code, output = self.dump()
        self.assertEqual(code, 0, output)
        for name in reference.c_Dumps:
            data = self.read_dump(name)
            self.assertEqual((data['pin'], data['engineCommit'], data['command']), (self.pin, self.pin[:12], reference.c_DumpCommands[name]))
        commands = [command for command, _ in FakeEditor.calls]
        self.assertEqual(commands[:6], ['launch', 'editor.commands', 'preferences.get', 'project.templates', 'project.samples', 'project.create'])
        self.assertEqual(commands[-1], 'quit')
        created = dict(FakeEditor.calls)['project.create']
        self.assertEqual(created, {'directory': os.path.join(self.work, 'Empty'), 'name': 'Empty', 'template': 'empty'})
        self.assertEqual(dict(FakeEditor.calls)['scene.new'], {'name': 'Defaults'})
        deletes = [parameters for command, parameters in FakeEditor.calls if command == 'entity.delete']
        self.assertEqual(len(deletes), 4)  # the probe, and one per addable component
        self.assertTrue(all(set(parameters) == {'entities'} for parameters in deletes))
        # The person's values and the preferences file are never kept; pictures are relative to the build.
        preferences = self.read_dump('preferences')['result']
        self.assertEqual(set(preferences), {'sections'})
        self.assertNotIn('value', preferences['sections'][0])
        self.assertEqual(self.read_dump('samples')['result']['samples'][0]['picture'], 'Samples/Tetris/Picture.png')
        defaults = {record['component']: record for record in self.read_dump('component-defaults')['result']['components']}
        self.assertEqual(defaults['Camera'], {'component': 'Camera', 'values': {'FieldOfView': 60.0, 'FocusDistance': 10.0}})
        self.assertEqual(defaults['PostProcess']['inactive'], {'BloomIntensity': 'Bloom is off'})
        self.assertEqual(defaults['PostProcess']['added'], ['Volume'])
        self.assertEqual(defaults['Broken'], {'component': 'Broken', 'error': 'Broken needs a camera'})
        self.assertNotIn('Name', defaults)  # not addable
        with open(os.path.join(self.work, reference.c_WorkMarker), encoding='utf-8') as file:
            self.assertIn('reference.py', file.read())

    def test_only_runs_the_named_dumps_and_leaves_the_others(self):
        self.assertEqual(self.dump('--only', 'commands,templates')[0], 0)
        self.assertEqual(sorted(os.listdir(self.dumps())), ['commands.json', 'templates.json'])
        self.assertNotIn('project.create', [command for command, _ in FakeEditor.calls])
        code, output = self.dump('--only', 'settings')
        self.assertEqual(code, 0, output)
        self.assertEqual(sorted(os.listdir(self.dumps())), ['commands.json', 'settings.json', 'templates.json'])
        self.assertEqual(self.dump('--only', 'nothing')[0], 2)

    def test_a_machine_path_stops_the_dump_before_anything_is_written(self):
        FakeEditor.data['project.templates']['templates'][0]['description'] = 'Made in %s/Templates' % self.home
        code, output = self.dump()
        self.assertEqual(code, 1)
        self.assertIn('templates.json/templates/0/description holds', output)
        self.assertIn('a path of this machine', output)
        self.assertFalse(os.path.isdir(self.dumps()))
        FakeEditor.data['project.templates']['templates'][0]['description'] = 'C:/Users/someone/Templates'
        self.assertEqual(self.dump()[0], 1)
        self.assertEqual(reference.find_machine_paths({'a': ['/c/Users/x', 'fine text', '\\\\host\\share']}, set()),
                         [('/a/0', '/c/Users/x'), ('/a/2', '\\\\host\\share')])

    def test_a_failing_command_fails_the_dump_and_writes_nothing(self):
        FakeEditor.data['project.settings'] = editor.EditorError('project.settings failed (StrataCLI exit code 1): No project is open')
        code, output = self.dump()
        self.assertEqual(code, 1)
        self.assertIn('No project is open', output)
        self.assertIn('every command and its answer are in', output)
        self.assertFalse(os.path.isdir(self.dumps()))
        self.assertEqual(FakeEditor.calls[-1], ('quit', None))

    def test_a_sample_picture_outside_the_build_is_refused(self):
        FakeEditor.data['project.samples']['samples'][0]['picture'] = os.path.join(self.home, 'Picture.png')
        code, output = self.dump('--only', 'samples')
        self.assertEqual(code, 1)
        self.assertIn('outside the build', output)

    def test_preflight_checks_stop_the_dump(self):
        os.remove(editor.program_path(self.build, 'StrataCLI'))
        code, output = self.dump()
        self.assertEqual(code, 2)
        self.assertIn('check 3', output)
        self.assertEqual(FakeEditor.calls, [])
        code, output = self.run_tool('dump', '--engine', os.path.join(self.home, 'missing'), '--build', self.build)
        self.assertEqual(code, 2)
        self.assertIn('check 1', output)


class ParseTests(ReferenceTestCase):
    def parse(self):
        engine = repo.Engine(self.engine.root)
        try:
            data, problems = routes.parse_all(engine, self.pin, '0.8.0', c_Limits)
        finally:
            engine.close()
        self.assertEqual(problems, [])
        return data

    def test_commands_and_toolsets(self):
        data = self.parse()['commands']
        registrations = {record['name']: record for record in data['registrations']}
        self.assertEqual(sorted(registrations), ['asset.list', 'asset.setBudget', 'asset.stats', 'editor.commands', 'editor.showPanel',
                                                 'entity.create', 'scene.open', 'viewport.capture'])
        self.assertEqual({key: registrations['scene.open'][key] for key in ('kind', 'results', 'mayDefer', 'waitsForAssets')},
                         {'kind': 'Session', 'results': 'Content', 'mayDefer': True, 'waitsForAssets': False})
        self.assertEqual((registrations['asset.list']['kind'], registrations['asset.list']['waitsForAssets']), ('Query', True))
        self.assertEqual((registrations['entity.create']['kind'], registrations['entity.create']['line']), ('Edit', 22))
        self.assertEqual(registrations['editor.showPanel']['results'], 'Session')
        self.assertEqual(data['toolsets']['core'], ['editor.commands', 'entity.create'])
        self.assertEqual(data['toolsets']['exact'], [['asset.list', 'streaming']])
        self.assertEqual(tables.toolsets_of('asset.list', data['toolsets']), ['streaming'])
        self.assertEqual(tables.toolsets_of('entity.create', data['toolsets']), ['core', 'scene'])
        self.assertEqual(tables.toolsets_of('viewport.capture', data['toolsets']), ['viewport'])

    def test_components_hidden_parts_and_inactive_reasons(self):
        data = self.parse()['components']
        by_name = {record['name']: record for record in data['components']}
        self.assertEqual(by_name['ID']['flags'], ['Hidden', 'NoSerialize'])
        self.assertEqual(by_name['PostProcess']['displayName'], 'Post Process')
        camera = {item['name']: item for item in by_name['Camera']['properties']}
        self.assertEqual(camera['Cache']['flags'], ['Transient'])
        reasons = {(item['component'], item['property']): item['messages'] for item in data['inactive']}
        self.assertEqual(reasons[('Camera', 'FieldOfView')], ["The camera's projection is Orthographic"])
        self.assertEqual(reasons[('Camera', 'FocusDistance')], ['Depth Of Field is off', "The camera's projection is Orthographic"])
        self.assertEqual(reasons[('PostProcess', 'BloomIntensity')], ['Bloom is off'])
        self.assertEqual(reasons[('PostProcess', 'HistoryFrames')], ['Only a Custom preset uses it (the preset is {})'])

    def test_asset_types_quality_stages_and_statistics(self):
        data = self.parse()
        types = {item['name']: item for item in data['asset-types']['types']}
        self.assertEqual((types['Texture']['value'], types['Texture']['comment'], types['AudioClip']['value']), (2, 'Images', 7))
        self.assertEqual([(item['type'], item['class'], item['version'], item['extensions']) for item in data['asset-types']['importers']],
                         [('AudioClip', 'AudioClipImporter', 2, ['.wav', '.ogg']), ('Scene', 'NativeAssetImporter', 1, []),
                          ('Texture', 'TextureImporter', 5, [])])
        rows = {row['row']: row for row in data['quality']['rows']}
        self.assertEqual(rows['ShadowResolution']['values'][2], 'ShadowMapResolution::Auto')
        self.assertEqual(rows['LODErrorPixels']['values'], [2.0, 1.0, 1.0, 0.5])
        self.assertEqual(rows['ShadowResolution']['comment'], 'Sharper shadows cost memory.')
        self.assertEqual([stage['name'] for stage in data['gpu-stages']['stages']], ['GPU.UI', 'GPU.Shadows', 'GPU.Opaque'])
        keys = data['render-stats']['keys']
        self.assertEqual([item['key'] for item in keys], ['quality', 'cascades', 'draws', 'geometryPool', 'exposure'])
        self.assertEqual(keys[0]['comment'], 'What the frame drew with.')
        self.assertEqual(keys[2]['source'], 'SceneRendererStats::DrawCalls')
        self.assertEqual([[child['key'] for child in item.get('children', [])] for item in keys],
                         [[], ['near', 'far'], [], ['usedMB', 'moves'], ['ev100']])
        renderer = data['renderer']
        self.assertEqual([field['name'] for field in renderer['specification']['fields']], ['DebugName', 'MaxLights', 'LightClusterGrid', 'EntityIDs'])
        self.assertEqual([field['name'] for field in renderer['stats']['fields']], ['DrawCalls', 'CascadeCount', 'Cascades'])
        self.assertEqual(renderer['specification']['fields'][3]['comment'], 'Picking reads them')

    def test_perf_log_options_and_build(self):
        data = self.parse()
        columns = data['perf-log']['columns']
        self.assertEqual([column['name'] for column in columns], ['Frame', 'WorkMs', '<stage>', 'LoadingAssets', 'QueuedLoads', 'InFlightLoads'])
        self.assertEqual(columns[5]['description'], 'the asset manager after the frame; empty without one')
        self.assertEqual([(group['owner'], group['names']) for group in data['perf-log']['groups']],
                         [('GameRuntime', ['WorldCellsLoaded', 'PhysicsBodies']), ('GameRenderer', ['DrawCalls'])])
        programs = data['options']['programs']
        self.assertEqual(programs['StrataEditor'], {'': ['--help', '--no-gpu', '--project']})
        self.assertEqual(programs['StrataCLI'][''], ['--help', '--verbose', '--version'])
        self.assertEqual(programs['StrataCLI']['call'], ['--port', '--timeout', '--token', '--verbose'])
        self.assertIn('--idle-timeout', programs['StrataCLI']['launch'])
        details = data['options']['details']
        self.assertEqual(details['StrataEditor']['options'][1]['description'], 'Run without a graphics device (implies --headless)')
        cli = details['StrataCLI']
        self.assertEqual(cli['usage'][1], 'StrataCLI launch [--project <dir>] [--headless | --no-gpu] [--idle-timeout <s>]')
        self.assertEqual(cli['commands'][0]['description'], 'Call an editor method and print its result ({"Image"} results are saved)')
        self.assertEqual(len(cli['environment']), 1)
        self.assertTrue(cli['environment'][0]['description'].endswith('~/.local/share/Strata/Sessions)'))
        self.assertEqual(cli['exitCodes'], '0 success; 1 the editor answered with an error.')
        build = data['build']
        self.assertEqual([option['name'] for option in build['options']], ['STRATA_BUILD_TESTS', 'STRATA_WITH_AUDIO', 'STRATA_USE_PCH'])
        self.assertEqual(build['options'][1]['description'], 'Build the audio module ("miniaudio")')
        self.assertEqual([(test['name'], test['labels']) for test in build['tests']],
                         [('StrataTests.Core.Core', ['core']), ('StrataTests.Core.Scene', ['core']), ('StrataTests.Perf', ['perf', 'gpu']),
                          ('StrataRuntime.InvalidFrames.abc', []), ('StrataRuntime.InvalidFrames.0', []), ('StrataTools.Offline', [])])
        self.assertEqual([preset['name'] for preset in build['presets']['configurePresets']], ['base', 'windows'])
        self.assertEqual(data['tests']['suites'], ['Core.Time', 'Scene.Big'])
        self.assertEqual(data['macros']['macros'], ['ST_BIT', 'ST_CORE_ASSERT', 'ST_SCRIPT_CLASS', 'ST_SCRIPT_DETAIL_CLASS', 'ST_SCRIPT_FIELD'])
        # The frame profiler's stage names, which the names lint reads: the built-in list, RegisterStage and
        # RegisterGPUStage calls, a scene system's ProfileStage and the ST_PROFILE_STAGE macro.
        self.assertEqual(data['frame-stages']['stages'], ['GPU.Opaque', 'GPU.Shadows', 'GPU.UI', 'Input', 'Present', 'Render.Extract',
                                                          'Render.UI', 'Scene.Physics', 'Scene.Transforms'])
        # The CPU stages' table (rulings-10.md, R48): the built-in ones first in their order, then the others; where each
        # is declared and timed, and whether it lies in the work time. The GPU's stages are not among them.
        cpu = {item['name']: item for item in data['frame-stages']['cpu']}
        self.assertEqual([item['name'] for item in data['frame-stages']['cpu']],
                         ['Input', 'Render.Extract', 'Present', 'Render.UI', 'Scene.Physics', 'Scene.Transforms'])
        self.assertEqual(cpu['Present']['declared'], [{'by': 'c_BuiltinFrameStages', 'file': 'Strata/src/Strata/Core/FrameProfiler.h', 'line': 9}])
        self.assertEqual((cpu['Present']['inWorkTime'], cpu['Input']['inWorkTime']), (False, True))
        self.assertEqual(cpu['Render.UI']['declared'], [{'by': 'RegisterStage', 'file': 'Strata/src/Strata/GameUI/GameUIRenderer.cpp', 'line': 8}])
        self.assertEqual(cpu['Scene.Physics']['declared'][0]['by'], 'ProfileStage')
        self.assertEqual((cpu['Scene.Transforms']['declared'], cpu['Scene.Transforms']['timed']),
                         ([], [{'file': 'Strata/src/Strata/Physics/PhysicsRegistration.cpp', 'line': 11}]))
        self.assertIn('CMakeLists.txt', data['paths']['paths'])
        self.assertEqual(list(data['paths']['submodules']), ['Strata/vendor/entt'])
        literals = data['ui-literals']['literals']
        for literal in ('Add Component', 'Create Child', 'Save', '\u25b8 Next', 'File'):
            self.assertIn(literal, literals)

    def test_script_api_added_in_and_the_sdk(self):
        data = self.parse()['script-api']
        functions = [(member['name'], member['addedIn']) for member in data['hostAPI']['members'] if member['kind'] == 'function']
        self.assertEqual(functions, [('Log', '0.1.0'), ('GetDeltaTime', '0.1.0'), ('GetFrameIndex', '0.2.0'), ('SetTimeScale', '0.8.0')])
        log = data['hostAPI']['members'][2]
        self.assertEqual((log['declaration'], log['comment']), ('void (*Log)(uint32_t level, StrataScriptString message)',
                                                                 'Diagnostics (callable from any thread).'))
        self.assertEqual([member['name'] for member in data['classDesc']['members']], ['StructSize', 'Name', 'OnCreate', 'OnUpdate'])
        functions = {(function['class'] or function['namespace'], function['name']): function for function in data['sdk']['functions']}
        # As SDKReader reads them: public members and namespace functions outside Detail; a pure virtual one counts, a
        # defaulted constructor and a private member do not.
        self.assertEqual(sorted(functions), [('Entity', 'Find'), ('Entity', 'GetComponent'), ('Entity', 'IsValid'), ('Entity', 'OnHit'),
                                             ('Key', 'IsDown')])
        self.assertTrue(functions[('Entity', 'OnHit')]['virtual'])
        self.assertEqual(functions[('Entity', 'IsValid')]['comment'], 'Whether the entity still exists.')
        self.assertTrue(functions[('Entity', 'Find')]['static'])
        self.assertEqual(functions[('Entity', 'Find')]['declaration'], 'static Entity Find(std::string_view name)')
        self.assertEqual(functions[('Entity', 'GetComponent')]['templateParameters'], ['T'])
        self.assertEqual([macro['name'] for macro in data['sdk']['macros']], ['ST_SCRIPT_CLASS', 'ST_SCRIPT_FIELD'])
        self.assertEqual(data['sdk']['macros'][0]['comment'], 'Registers a script class.')

    def test_performance_and_limits(self):
        data = self.parse()
        self.assertEqual([entry['name'] for entry in data['performance']['budgets']], ['Perf.Scene.Update', 'Perf.Pacer.Error'])
        self.assertEqual(data['performance']['budgets'][1]['Provisional'], True)
        self.assertEqual({item['name']: item['value'] for item in data['limits']['limits']},
                         {'Scene::c_MaxEntities': 1048575, 'Scene::c_MaxMoves': 4096, 'Scene::c_Budget': 2000.0,
                          'SceneSettings::c_MaxBodiesLimit': 2097152})
        self.assertEqual(data['limits']['limits'][0]['comment'], 'A registry holds at most this many live entities.')

    def test_a_route_that_finds_nothing_fails_naming_its_file(self):
        engine = helpers.TempEngine()
        try:
            files = fixture_files()
            files['Strata/src/Strata/Renderer/RendererQuality.cpp'] = files['Strata/src/Strata/Renderer/RendererQuality.cpp'].replace(
                'c_ShadowCascadesRow', 'c_ShadowSplitsRow')
            files['Strata/src/Strata/Runtime/FramePerfLog.h'] = '#pragma once\n'
            files['StrataEditor/src/Editor/EditorCommands.cpp'] += ('\nvoid More(EditorCommandRegistry& registry)\n{\n\tregistry.Register({ "x.y", "Z.", '
                                                                    'ObjectSchema({}), Handler, Something::Else });\n}\n')
            pin = engine.commit(files)
            reader = repo.Engine(engine.root)
            try:
                data, problems = routes.parse_all(reader, pin, '0.8.0', c_Limits)
            finally:
                reader.close()
            text = '\n'.join(problems)
            self.assertIn('Strata/src/Strata/Renderer/RendererQuality.cpp:13: the row c_ShadowSplitsRow has no field "ShadowSplits"', text)
            self.assertIn('Strata/src/Strata/Runtime/FramePerfLog.h: no comment "The header names the columns:"', text)
            self.assertIn('the registration of x.y has "Something::Else" where EditorCommand\'s field 5', text)
            self.assertIn('change the quality route of tools/booklib/routes.py', text)
            self.assertIn('Strata/vendor/entt/src/entt/entity/entity.hpp', text)  # the submodule is not in this engine
            self.assertNotIn('quality', data)
            self.assertIn('gpu-stages', data)
        finally:
            engine.cleanup()

    def test_macros_hold_the_definitions_of_the_cmake_files(self):
        # `ST_DIST` and `ST_WITH_PHYSICS` are no #define: CMake's compile definitions give them (the names lint refused
        # them on wave 1a's pages). A generator expression, a value and a line of several names each give theirs; a
        # name only mentioned in a comment or another command does not count.
        text = '\n'.join([
            '# Code tests ST_WITH_COMMENTED, a definition.',
            'target_compile_definitions(${target} PRIVATE',
            '\t"$<$<CONFIG:Debug>:ST_DEBUG>"',
            '\t"$<$<CONFIG:Dist>:ST_DIST>")',
            'target_compile_definitions(Strata_Core PUBLIC',
            '\t"ST_WITH_PHYSICS=$<BOOL:${STRATA_WITH_PHYSICS}>"  # ST_IN_A_COMMENT',
            '\t"ST_WITH_GLFW=$<BOOL:${STRATA_WITH_GLFW}>")',
            'add_compile_definitions(ST_ENABLE_TRACY NOMINMAX ST_LEVEL=2)',
            'message(STATUS "ST_NOT_A_DEFINITION")',
            'target_compile_definitions(other PRIVATE "STRATA_TESTS_HAVE_CLI")'])
        self.assertEqual(routes.cmake_definitions(text),
                         ['ST_DEBUG', 'ST_DIST', 'ST_ENABLE_TRACY', 'ST_LEVEL', 'ST_WITH_GLFW', 'ST_WITH_PHYSICS'])

        class FakeReader:
            def grep_output(self, pattern, options, paths):
                return '#define ST_BIT\n'  # git grep -h -o: the match alone

            def grep(self, pattern, paths):
                return ['CMake/StrataCompilerOptions.cmake']

            def text(self, path):
                return text if path == 'CMake/StrataCompilerOptions.cmake' else None

        self.assertEqual(routes.route_macros(FakeReader())['macros'],
                         ['ST_BIT', 'ST_DEBUG', 'ST_DIST', 'ST_ENABLE_TRACY', 'ST_LEVEL', 'ST_WITH_GLFW', 'ST_WITH_PHYSICS'])

    def test_parse_writes_every_route_or_nothing(self):
        code, output = self.run_tool('parse', '--engine', self.engine.root)
        self.assertEqual(code, 0, output)
        parsed = os.path.join(self.dumps(), 'parsed')
        self.assertEqual(sorted(os.listdir(parsed)), sorted(name + '.json' for name in (
            'commands', 'components', 'asset-types', 'quality', 'gpu-stages', 'render-stats', 'renderer', 'perf-log', 'options',
            'script-api', 'performance', 'limits', 'build', 'tests', 'macros', 'frame-stages', 'paths', 'ui-literals')))
        with open(os.path.join(parsed, 'tests.json'), encoding='utf-8') as file:
            self.assertEqual(json.load(file)['pin'], self.pin)
        broken = os.path.join(self.book.root, 'limits.json')
        with open(broken, 'w', encoding='utf-8') as file:
            json.dump({'limits': [{'file': 'Strata/src/Strata/Scene/Scene.h', 'name': 'Scene::c_Missing'}]}, file)
        shutil.rmtree(parsed)
        with mock.patch.object(reference, 'c_LimitsPath', broken):
            code, output = quiet(reference.main, 'parse', '--engine', self.engine.root, '--root', self.book.root)
        self.assertEqual(code, 1)
        self.assertIn('limits[0]: Strata/src/Strata/Scene/Scene.h declares no constant c_Missing at the pin', output)
        self.assertFalse(os.path.isdir(parsed))


# The files of reference/commands that the fixture's commands make: the toolsets and one file per group.
c_CommandFiles = ['commands-asset.md', 'commands-editor.md', 'commands-entity.md', 'commands-scene.md', 'commands-toolsets.md', 'commands-viewport.md']


class RenderTests(ReferenceTestCase):
    def test_every_table_with_its_stamp_and_the_values(self):
        self.make_all()
        folder = os.path.join(self.book.root, 'src', 'generated', 'reference')
        names = sorted(os.listdir(folder))
        self.assertEqual(names, sorted(['asset-budgets.md', 'asset-types.md', 'build.md'] + c_CommandFiles + ['components.md', 'debug-views.md',
                                        'cpu-stages.md', 'figures.md', 'gpu-stages.md', 'limits.md', 'options-cli.md', 'options-editor.md', 'options-runtime.md',
                                        'perf-log.md', 'performance.md', 'preferences.md', 'quality.md', 'render-stats.md', 'renderer.md',
                                        'script-api.md', 'settings.md', 'values.json']))
        for name in names:
            if name.endswith('.md'):
                stamp = tables.read_stamp(self.generated(name))
                self.assertEqual((stamp['engine'], stamp['sha256']), (self.pin, stamp['actual']), name)
        values = json.loads(self.generated('values.json'))
        expected = {'engine.commit': self.pin, 'commands.count': 8, 'commands.query.count': 4, 'hostFunctions.count': 4, 'debugViews.count': 3,
                    'components.count': 4, 'quality.ShadowResolution.Low': '1024', 'quality.ShadowResolution.High': 'Auto',
                    'quality.ShadowCascades.Ultra': 4, 'importer.Texture.version': 5, 'limits.Scene.c_MaxEntities': 1048575,
                    'limits.SceneSettings.c_MaxBodiesLimit': 2097152, 'toolsets.core.count': 2, 'samples.count': 1, 'cpuStages.count': 6}
        self.assertEqual({key: values.get(key) for key in expected}, expected)
        self.assertTrue(all(isinstance(value, (int, float, str)) for value in values.values()))
        # rulings-10.md, R48: the CPU's stages are a generated table like the GPU's.
        stages = self.generated('cpu-stages.md')
        self.assertIn('| `Present` | `c_BuiltinFrameStages`, `Strata/src/Strata/Core/FrameProfiler.h:9` |   | no |', stages)
        self.assertIn('| `Scene.Transforms` |   | `Strata/src/Strata/Physics/PhysicsRegistration.cpp:11` | yes |', stages)
        self.assertNotIn('GPU.', stages)
        # §7.3: each budget gives perf.<name>.<Measured|Budget|Unit>; a Provisional entry gives none.
        self.assertEqual(sorted(key for key in values if key.startswith('perf.')),
                         ['perf.Perf.Scene.Update.Budget', 'perf.Perf.Scene.Update.Measured', 'perf.Perf.Scene.Update.Unit'])
        # §7.3: the keys pages may name are the ones render lists in its output.
        self.assertIn('reference: values.json holds %d keys: %s\n' % (len(values), ', '.join(sorted(values))), self.render_output)

    def test_engine_text_is_escaped_and_never_raw_html(self):
        self.make_all()
        commands = '\n'.join(self.generated(name) for name in c_CommandFiles)
        self.assertIn('| `name` | string | no |   | Entity name &lt;with \\| a pipe&gt; and &#96;code&#96;. |', commands)
        self.assertIn('| `region.min` | array of number | no |   | Items: at least 2, at most 2. |', commands)
        self.assertIn('| `force` | boolean | no | `false` | Discard changes. |', commands)
        self.assertIn('<details>\n<summary>Parameter schema of scene.open</summary>\n\n```json\n{', commands)
        self.assertIn('Kind: `Session` · Results: `Content` · MCP toolsets: `scene` · Answers later (MayDefer): yes', commands)
        self.assertEqual(tables.md('a <b> & "c" | `d` *e* _f_ [g] $h ~i :name[x] \\'),
                         'a &lt;b&gt; &amp; &quot;c&quot; \\| &#96;d&#96; \\*e\\* \\_f\\_ \\[g\\] \\$h \\~i \\:name\\[x\\] \\\\')
        self.assertEqual(tables.row([tables.code('a | b'), tables.md('c | d')]), '| `a \\| b` | c \\| d |')
        # A summary is raw HTML, where backslash escapes would show: only the HTML escapes.
        self.assertTrue(tables.details('Schema of c_Max* <x> & "y"', {}).startswith(
            '<details>\n<summary>Schema of c_Max* &lt;x&gt; &amp; &quot;y&quot;</summary>\n\n```json\n{}\n```'))
        components = self.generated('components.md')
        self.assertIn('| `BloomIntensity` | Bloom Intensity | `Float` | `1.0` |   | Inactive (it has no effect) when: Bloom is off. '
                      'Inspector section: Bloom. |', components)
        self.assertIn('It has no defaults here: `component.add` refuses it on a new entity (Broken needs a camera).', components)
        self.assertIn('Adding it also adds `Volume`.', components)
        self.assertIn('| `ID` | `Hidden`, `NoSerialize` | `ID` |', components)
        self.assertIn('| `Camera` | `Cache` | `Transient` |', components)
        preferences = self.generated('preferences.md')
        self.assertNotIn('125%"', preferences.replace('&quot;', '"').split('## ')[0])
        self.assertIn('Its schema gives no default per field.', preferences)
        self.assertIn('| `LODErrorPixels` | Level of detail error | `2.0` | `1.0` | `1.0` | `0.5` |', self.generated('quality.md'))
        self.assertIn('| 3 | `GetFrameIndex` | `uint64_t (*GetFrameIndex)(StrataScriptContext* context)` | 0.2.0 |', self.generated('script-api.md'))

    def test_the_commands_are_one_page_of_group_files_and_a_page_over_the_budget_fails_the_render(self):
        # rulings 13, R59's approval: reference/commands stays one page, which includes the toolsets' file and a file
        # per group with prose of its own between them; past the largest page's budget the render fails and never
        # splits the page.
        self.make_all()
        folder = os.path.join(self.book.root, 'src', 'generated', 'reference')
        self.assertEqual(sorted(name for name in os.listdir(folder) if name.startswith('commands')), c_CommandFiles)
        self.assertIn('\n## scene.open\n', self.generated('commands-scene.md'))
        page = tables.page_estimate('\n\n'.join(self.generated(name) for name in c_CommandFiles))
        self.assertGreater(page, tables.c_PageChromeBytes)
        self.set_budget((page + 1024) / 1024)
        code, output = self.run_tool('render')
        self.assertEqual(code, 0, output)
        self.assertEqual(sorted(name for name in os.listdir(folder) if name.startswith('commands')), c_CommandFiles)
        self.set_budget((page - 1024) / 1024)
        code, output = self.run_tool('render')
        self.assertEqual(code, 1)
        self.assertIn("reference/commands would be a page of about %d KB, more than the largest page's budget of %d KB" % (page // 1024, (page - 1024) // 1024), output)
        self.assertIn('the page stays one page (rulings 13, R59): ask the planner for a ruling', output)

    def test_the_page_estimate_follows_the_built_reference_pages(self):
        # The release book-v0.8.0-r2's built reference pages (2026-11-25): the Markdown of the generated files each
        # includes, outside fences in KB, its fence lines, and the built HTML in KB. The estimate and the build agree
        # within 10 per cent (R59's approval), reference/commands within 2, since its estimate decides the render.
        measured = {'commands': (242.8, 3843, 1547.1), 'components': (70.5, 0, 225.1), 'settings': (19.0, 591, 273.9),
                    'performance': (21.0, 0, 136.2), 'script-api': (105.1, 0, 259.5), 'figures': (174.9, 0, 333.3)}
        for name, (outside, lines, built) in measured.items():
            text = 'x' * int(outside * 1024)
            if lines:
                text += '\n\n```json\n' + '\n'.join(['a'] * lines) + '\n```\n'
            estimate = tables.page_estimate(text)
            self.assertLess(abs(estimate - built * 1024), (0.02 if name == 'commands' else 0.1) * built * 1024, name)

    def test_render_check_finds_hand_edits_stale_and_extra_files_and_other_pins(self):
        self.make_all()
        self.assertEqual(self.run_tool('render', '--check'), (0, 'reference: 0 problems\n'))
        folder = os.path.join(self.book.root, 'src', 'generated', 'reference')
        path = os.path.join(folder, 'limits.md')
        text = repo.read_text(path)
        repo.write_text(path, text.replace('4096', '4097'))
        code, output = self.run_tool('render', '--check')
        self.assertEqual(code, 1)
        self.assertIn("limits.md:1: the content does not match its stamp's sha256 (the file was edited by hand)", output)
        self.assertIn('limits.md: differs from what render writes', output)
        repo.write_text(path, text)
        os.remove(os.path.join(folder, 'gpu-stages.md'))
        repo.write_text(os.path.join(folder, 'old.md'), 'old')
        code, output = self.run_tool('render', '--check')
        self.assertIn('gpu-stages.md: missing', output)
        self.assertIn('old.md: render writes no such file', output)
        self.assertIn('old.md:1: no stamp', output)
        # A dump of another pin, and an editor that reported another commit.
        data = self.read_dump('templates')
        data['engineCommit'] = 'f' * 12
        reference.write_json(os.path.join(self.dumps(), 'templates.json'), data)
        code, output = self.run_tool('render', '--check')
        self.assertIn('templates.json: the editor reported the engine commit ffffffffffff, which is not a prefix of the pin', output)
        self.book.write('engine.pin', 'commit %s\nrelease 0.8.0\nprerelease yes\nrepository https://github.com/2042Third/GameEngine\n' % ('1' * 40))
        code, output = self.run_tool('render', '--check')
        self.assertEqual(code, 1)
        self.assertIn('no dumps for the pin 1111111111111111111111111111111111111111', output)
        self.assertIn('the stamp names the engine %s, but engine.pin names %s' % (self.pin, '1' * 40), output)

    def test_a_page_that_names_a_key_render_does_not_write_fails_the_check(self):
        # rulings-9.md, R41: a Provisional budget gives no perf.<name>.Measured, and a page that names it fails.
        self.make_all()
        self.book.page('core/time', '---\nid: core/time\n---\n\nThe update takes :value{key="perf.Perf.Scene.Update.Measured"} ms.\n\n'
                       '```text\n:value{key="in.a.fence"}\n```\n')
        self.assertEqual(self.run_tool('render', '--check'), (0, 'reference: 0 problems\n'))
        self.book.page('core/time', '---\nid: core/time\n---\n\nThe error is :value{key="perf.Perf.Pacer.Error.Measured"}.\n')
        code, output = self.run_tool('render', '--check')
        self.assertEqual(code, 1)
        self.assertIn('src/content/docs/core/time.md:5: :value{key="perf.Perf.Pacer.Error.Measured"}: render writes no such key', output)

    def test_check_compares_parse_and_render_with_the_committed_files(self):
        self.make_all()
        code, output = self.run_tool('check', '--engine', self.engine.root)
        self.assertEqual((code, output), (0, 'reference: 0 problems\n'))
        path = os.path.join(self.dumps(), 'parsed', 'gpu-stages.json')
        with open(path, encoding='utf-8') as file:
            data = json.load(file)
        data['stages'] = data['stages'][:1]
        reference.write_json(path, data)
        code, output = self.run_tool('check', '--engine', self.engine.root)
        self.assertEqual(code, 1)
        self.assertIn('parsed/gpu-stages.json: differs from what parse finds at the pin', output)
        reference.write_json(path, dict(data, stages=[]))
        repo.write_text(os.path.join(self.book.root, 'src', 'generated', 'reference', 'gpu-stages.md'), 'by hand\n')
        code, output = self.run_tool('check', '--engine', self.engine.root)
        self.assertIn('gpu-stages.md: differs from what render writes', output)
        self.assertIn('gpu-stages.md:1: no stamp', output)

    def test_a_quality_row_that_does_not_fit_its_field_fails_the_render(self):
        self.dump()
        self.run_tool('parse', '--engine', self.engine.root)
        settings = self.read_dump('settings')
        settings['result']['sections'][0]['schema']['properties']['ShadowResolution']['default'] = '2048'
        reference.write_json(os.path.join(self.dumps(), 'settings.json'), settings)
        code, output = self.run_tool('render')
        self.assertEqual(code, 1)
        self.assertIn("c_ShadowResolutionRow's High value Auto is not the field's default 2048", output)
        self.assertFalse(os.path.isdir(os.path.join(self.book.root, 'src', 'generated', 'reference')))

    def test_usage_and_help(self):
        code, output = self.run_tool('--help')
        self.assertEqual(code, 0)
        for word in ('dump', 'parse', 'render', 'check', '--only', 'component-defaults', 'ui-literals', 'values.json', 'sha256'):
            self.assertIn(word, output)
        self.assertEqual(self.run_tool('parse', '--check')[0], 2)
        self.assertEqual(self.run_tool('render', '--build', self.build)[0], 2)
        code, output = self.run_tool('render')
        self.assertEqual(code, 2)
        self.assertIn('no dumps at reference/_dumps/%s: run python -I tools/reference.py dump and parse at the pin' % self.pin, output)


if __name__ == '__main__':
    unittest.main()
