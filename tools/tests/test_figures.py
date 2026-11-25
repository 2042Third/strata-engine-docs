"""figures.py (plan/pipelines.md §5) on a small book and a small engine: the recipe's schema, check, fill, labs, take
(with a stand-in editor), publish (with a stand-in encoder), archive, compare and list, and the two Node scripts when
node is on the PATH."""

import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import figures
from booklib import editor, images, repo

c_Fake = os.path.join(helpers.c_Fixtures, 'figures', 'fake_encoder.py')
c_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

c_Shots = {
    'Projects': {'ThirdPerson': {'Sample': 'ThirdPerson', 'Scene': 'Scenes/Course.stscene'}, 'Basic3D': {'Template': 'basic3d', 'Scene': 'Scenes/Main.stscene'},
                 'LookDev': {'Name': 'LookDev', 'Script': 'LookDevScene.json', 'Scene': 'Scenes/LookDev.stscene'}},
    'Shots': [
        {'Name': 'tp.scene', 'Project': 'ThirdPerson', 'Camera': 'scene', 'Crops': [{'Name': 'feet', 'Rect': [0.25, 0.5, 0.75, 1.0]}]},
        {'Name': 'tp.editor', 'Project': 'ThirdPerson', 'Camera': 'editor'},
        {'Name': 'tp.dof', 'Project': 'ThirdPerson', 'Camera': 'scene', 'Setup': [{'Command': 'component.set', 'Parameters': {'entity': '350D7DDD7ED21DD5'}}]},
        {'Name': 'lookdev.thin', 'Project': 'LookDev', 'Position': [6, 1.5, 8], 'Target': [6, 0.8, 0], 'Fov': 40,
         'Crops': [{'Name': 'poles', 'Rect': [0.2, 0.3, 0.6, 0.9]}]},
    ],
}
c_LookDev = [
    {'command': 'project.create', 'parameters': {'directory': '@LOOKDEV_DIRECTORY@', 'name': 'LookDev'}},
    {'command': 'scene.new', 'parameters': {'name': 'LookDev'}},
    {'command': 'entity.create', 'parameters': {'name': 'Sun'}},
    {'command': 'entity.create', 'parameters': {'name': 'Pole'}},
    {'command': 'entity.create', 'parameters': {'name': 'Pole'}},
    {'command': 'scene.saveAs', 'parameters': {'path': 'Scenes/LookDev.stscene'}},
]
c_Course = {'Strata': {'Format': 'Scene'}, 'Scene': {'Name': 'Course', 'Entities': [
    {'Components': {'Name': {'Name': 'Camera'}}, 'ID': '350D7DDD7ED21DD5'},
    {'Components': {'Name': {'Name': 'Sun'}}, 'ID': '0A16D1AE6976CD46'},
    {'Components': {'Name': {'Name': 'Coin'}}, 'ID': '1'}, {'Components': {'Name': {'Name': 'Coin'}}, 'ID': '2'}]}}
c_Capture = '''		void Finish()
		{
			nlohmann::json result = {
				{ "Image", { { "MimeType", "image/png" } } },
				{ "width", encoded.Image.Width },
				{ "pendingAssets", progress.PendingAssets },
				{ "ui", { { "canvases", 1 }, { "pendingGlyphs", 0 } } },
				{ "renderStats", std::move(progress.RenderStats) }
			};
		}
'''
c_Stats = '''			return {
				// What the frame drew with.
				{ "quality", RendererQuality::ToSectionValue(stats.Quality) },
				{ "shadowMapSize", stats.ShadowMapSize },
				{ "exposure", stats.Exposure ? nlohmann::json { { "ev100", 1 } } : nlohmann::json(nullptr) },
				{ "draws", stats.DrawCalls } };
'''
c_CompleteResult = {
    'pendingAssets': 0, 'texturesBelowWanted': 0, 'stalePoses': 0, 'pendingTextGlyphs': 0, 'ui': {'pendingGlyphs': 0}, 'localShadowViewsPending': 0,
    'reflectionProbesPending': 0, 'renderStats': {'deferredInstanceBytes': 0, 'draws': 3}, 'preExposureSettled': True,
    'globalIlluminationSettled': True, 'previewLighting': False, 'temporalFrames': 0, 'width': 8, 'height': 4}
# The renderer switches of viewport.capture as the pin's commands dump describes them (CaptureRendererSwitches::GetSchema).
c_Renderer = {'type': 'object', 'additionalProperties': False, 'properties': {
    'DitherOutput': {'type': 'boolean'}, 'FXAASubpixel': {'type': 'number', 'enum': [0.25, 0.75]},
    'GlobalIlluminationBounceGain': {'type': 'number', 'minimum': 0.0, 'maximum': 1.0}}}
# The root under which a take's stand-in drive shows a folder to the programs it runs (figures.map_drive).
c_DriveRoot = os.path.join(os.sep, 'neutral') + os.sep
c_Templates = 'Entity camera = scene.CreateEntity("Main Camera");\nscene.CreateEntity("Sun");\nscene.CreateEntity("Post Process");\n'


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = function(list(arguments))
    return code, output.getvalue()


def read_bytes(path):
    with open(path, 'rb') as file:
        return file.read()


def read_text(path):
    with open(path, encoding='utf-8') as file:
        return file.read()


def grey_png(width, height, grey=128):
    return images.png_bytes(images.Image(width, height, 3, bytearray([grey]) * (width * height * 3)))


def speckled_png(width, height, pixels, levels, grey=128):
    """A grey picture whose first pixels are lighter by levels in every channel."""
    data = bytearray([grey]) * (width * height * 3)
    for index in range(pixels * 3):
        data[index] = grey + levels
    return images.png_bytes(images.Image(width, height, 3, data))


# Figures whose second capture differs from the first: (pixels, levels).
c_Speckles = {'dither': (1, 1), 'speckle': (2, 1), 'jump': (1, 2)}


def dump(pin, command, result):
    return json.dumps({'pin': pin, 'engineCommit': pin[:12], 'command': command, 'result': result})


class FiguresTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = helpers.TempEngine()
        self.pin = self.engine.commit({
            'Tools/LookDev/Shots.json': json.dumps(c_Shots), 'Tools/LookDev/LookDevScene.json': json.dumps(c_LookDev),
            'Samples/ThirdPerson/Assets/Scenes/Course.stscene': json.dumps(c_Course),
            'Samples/ThirdPerson/Assets/Scenes/Course.stscene.meta': json.dumps({'Handle': 'B186E06AB3CF53CC'}),
            'Samples/ThirdPerson/ThirdPerson.stproj': json.dumps({'Project': {'StartScene': 'B186E06AB3CF53CC'}}),
            'StrataEditor/src/Editor/ProjectTemplates.cpp': c_Templates,
            'StrataEditor/src/Editor/EditorViewportCommands.cpp': c_Capture, 'StrataEditor/src/Editor/EditorStateCommands.cpp': c_Stats,
            'StrataEditor/src/EditorApplication.cpp': '{ "--windowed", nullptr, "" },\n',
            'Tools/LookDev.py': ('import os, sys\nout = sys.argv[sys.argv.index("--output") + 1]\nos.makedirs(out, exist_ok=True)\n'
                                 'open(os.path.join(out, "report.txt"), "w").write(" ".join(sorted(os.listdir(os.path.join(sys.argv[2], "shots")))))\n'
                                 'print("compared", sys.argv[2], sys.argv[3])\n'),
        })
        self.book = helpers.TempBook(self.pin)
        self.dumps = 'reference/_dumps/%s' % self.pin
        self.write_dumps()

    def tearDown(self):
        self.book.cleanup()
        self.engine.cleanup()

    def write_dumps(self, debug_views=('none', 'shadows', 'ao'), extra_commands=(), renderer=True):
        capture = {'name': 'viewport.capture', 'kind': 'Query', 'parameters': {'properties': {
            'debugView': {'enum': list(debug_views)}, 'quality': {'enum': ['project', 'low', 'medium', 'high', 'ultra']}}}}
        if renderer:
            capture['parameters']['properties']['renderer'] = c_Renderer
        commands = [capture] + [{'name': name, 'parameters': {}} for name in ('component.set', 'entity.create', 'scene.saveAs', 'scene.new',
                                                                               'project.templates', 'editor.status') + tuple(extra_commands)]
        self.book.write(self.dumps + '/commands.json', dump(self.pin, 'editor.commands', {'commands': commands}))
        self.book.write(self.dumps + '/settings.json', dump(self.pin, 'project.settings', {'sections': [
            {'id': 'Renderer.Quality', 'schema': {'properties': {'Preset': {}, 'ShadowMapSize': {}}}}]}))
        self.book.write(self.dumps + '/components.json', dump(self.pin, 'component.list', {'components': [
            {'name': 'PostProcess', 'properties': [{'Name': 'Bloom', 'Type': 'Bool'}, {'Name': 'Exposure', 'Type': 'Float', 'Min': -10, 'Max': 10},
                                                   {'Name': 'Tonemapper', 'Type': 'Enum', 'Options': ['Filmic', 'None']}]}]}))

    def recipe(self, **fields):
        data = {'id': 'shot', 'shows': 'A robot on an island under a blue sky.', 'caption': 'The robot stands on the island.',
                'alt': 'A small grey robot on a floating island.', 'kind': 'scene', 'project': {'sample': 'ThirdPerson'}, 'shot': 'tp.scene'}
        data.update(fields)
        return {key: value for key, value in data.items() if value is not None}

    def manifest(self, *entries, page='core/time'):
        self.book.write('src/content/figures/%s.json' % page, json.dumps({'figures': list(entries)}, indent='\t'))

    def page(self, body, page='core/time'):
        self.book.page(page, helpers.frontmatter(id=page) + '\n' + body + '\n')

    def check(self, *extra):
        return quiet(figures.main, 'check', '--root', self.book.root, '--engine', self.engine.root, '--dumps', self.book.path(self.dumps), *extra)

    def errors(self, *extra):
        code, output = self.check(*extra)
        return code, [line for line in output.splitlines() if ': note: ' not in line and not line.startswith('figures:')]


class SchemaTests(FiguresTestCase):
    def test_a_good_recipe_passes_and_notes_what_is_not_taken(self):
        self.page('::figure{id=shot crop=feet}\n\n::figure{id=shot}')
        self.manifest(self.recipe())
        code, output = self.check()
        self.assertEqual(code, 0, output)
        self.assertIn('note: no src/assets/figures/core/time/shot.avif yet (not taken)', output)
        self.assertIn('note: no src/assets/figures/core/time/shot-feet.webp yet', output)
        code, output = self.check('--release')
        self.assertEqual(code, 1)
        self.assertIn('no src/assets/figures/core/time/shot.avif yet', output)

    def test_schema_problems_name_their_line(self):
        self.page('::figure{id=shot}')
        self.manifest(self.recipe(project='Samples/ThirdPerson', camera='editor', size=[8, 9000], extra=1, expect='PICTURE_COMPLETE'))
        code, lines = self.errors()
        self.assertEqual(code, 1)
        text = '\n'.join(lines)
        self.assertIn('src/content/figures/core/time.json:9: /figures/0/project is none of its 4 forms (a sample; a template; the look-dev project; a lab)', text)
        self.assertIn('/figures/0/size/0 must be at least 16', text)
        self.assertIn('/figures/0/size/1 must be at most 4096', text)
        self.assertIn('/figures/0/extra is not a known field', text)
        self.assertIn("/figures/0/expect must be 'complete'", text)
        # A page's references to an invalid manifest are not reported a second time.
        self.assertNotIn('has no figure', text)
        self.book.write('src/content/figures/core/time.json', '{"figures": [\n\t{"id": "x",}\n]}')
        self.assertIn('src/content/figures/core/time.json:2: not valid JSON', self.check()[1])


class CheckTests(FiguresTestCase):
    def test_step_parameters_outside_their_enum_at_the_pin(self):
        self.book.write(self.dumps + '/commands.json', dump(self.pin, 'editor.commands', {'commands': [
            {'name': 'editor.showPanel', 'parameters': {'properties': {'panel': {'enum': ['Inspector', 'AssetInspector']}}}}]}))
        self.page('')
        self.manifest(self.recipe(setup=[{'command': 'editor.showPanel', 'parameters': {'panel': 'Asset'}},
                                         {'command': 'editor.showPanel', 'parameters': {'panel': 'AssetInspector'}}]))
        code, lines = self.errors()
        text = '\n'.join(lines)
        self.assertEqual(code, 1)
        self.assertIn('the parameter panel of editor.showPanel is "Asset", which the editor at the pin refuses: use one of Inspector, '
                      'AssetInspector', text)
        self.assertNotIn('is "AssetInspector"', text)

    def test_shots_cameras_scenes_and_entities_at_the_pin(self):
        self.page('')
        self.manifest(self.recipe(id='missing', shot='tp.nothing'), self.recipe(id='editor-shot', shot='tp.editor'),
                      self.recipe(id='other-project', shot='lookdev.thin'), self.recipe(id='beside', camera={'position': [0, 0, 0], 'target': [0, 0, 1]}),
                      self.recipe(id='no-scene', shot=None, camera='scene', scene='Scenes/Gone.stscene'),
                      self.recipe(id='names', setup=[{'command': 'component.set', 'entityName': 'Coin'}, {'command': 'component.set', 'entityName': 'Sun'},
                                                     {'command': 'entity.create', 'parameters': {'name': 'Lamp'}}, {'command': 'component.set', 'entityName': 'Lamp'},
                                                     {'command': 'material.make'}, {'command': 'preferences.set'}]),
                      self.recipe(id='lookdev', project={'lookdev': True}, shot='lookdev.thin', setup=[{'command': 'component.set', 'entityName': 'Pole'}]),
                      self.recipe(id='basic', project={'template': 'basic3d'}, shot=None, camera='scene', setup=[{'command': 'component.set', 'entityName': 'Post Process'}]),
                      self.recipe(id='empty', project={'template': 'empty'}, shot=None, camera='scene', scene='Scenes/Main.stscene'))
        code, lines = self.errors()
        text = '\n'.join(lines)
        self.assertEqual(code, 1)
        self.assertIn('Tools/LookDev/Shots.json at the pin has no shot "tp.nothing"', text)
        self.assertIn('the shot tp.editor uses the editor camera', text)
        self.assertIn('the shot lookdev.thin belongs to the project LookDev of Shots.json, not to {"sample": "ThirdPerson"}', text)
        self.assertIn('a recipe with a shot takes the shot\'s camera: remove camera', text)
        self.assertIn('the scene Scenes/Gone.stscene does not exist in Samples/ThirdPerson/Assets at the pin', text)
        self.assertIn('entityName "Coin" names 2 entities of the scene at the pin', text)
        self.assertNotIn('"Sun" names', text)
        self.assertNotIn('"Lamp" names', text)
        self.assertIn('the command material.make is not one the editor at the pin registers', text)
        self.assertIn('preferences.set changes the person\'s preferences, which no tool does (pipelines.md §2)', text)
        self.assertIn('entityName "Pole" names 2 entities', text)
        self.assertNotIn('"Post Process" names', text)
        self.assertIn('an empty project has no scene Scenes/Main.stscene', text)
        # Each message names the manifest's line of the field.
        self.assertTrue(all(line.startswith('src/content/figures/core/time.json:') for line in lines), lines)

    def test_values_against_the_dumps(self):
        self.page('')
        self.manifest(self.recipe(id='views', debugView='wireframe', quality='ultra', postProcess={'Glow': 1, 'Exposure': 40, 'Tonemapper': 'ACES', 'Bloom': True}),
                      self.recipe(id='custom', quality={'custom': {'ShadowMapSize': 1024, 'Rays': 3}}))
        dumped = json.loads(self.book.read(self.dumps + '/commands.json'))
        dumped['result']['commands'][0]['parameters']['properties']['quality']['enum'].remove('ultra')
        self.book.write(self.dumps + '/commands.json', json.dumps(dumped))
        code, lines = self.errors()
        text = '\n'.join(lines)
        self.assertIn('debugView "wireframe" is not a debug view of viewport.capture at the pin: use one of none, shadows, ao', text)
        self.assertIn('quality "ultra" is not a preset of viewport.capture: use one of project, low, medium, high', text)
        self.assertIn('PostProcess has no property Glow at the pin: use a property of the components dump', text)
        self.assertIn('PostProcess.Exposure runs from -10 to 10, not 40', text)
        self.assertIn('PostProcess.Tonemapper is one of Filmic, None, not "ACES"', text)
        self.assertIn('Renderer.Quality has no field Rays at the pin', text)
        self.assertNotIn('ShadowMapSize at the pin', text)
        # Without the dumps, these are notes in a draft and errors in a release.
        shutil.rmtree(self.book.path(self.dumps))
        code, output = self.check()
        self.assertNotIn('wireframe', output)
        self.assertIn('note: the dump commands.json is missing', output)
        self.assertEqual(self.check('--release')[0], 1)

    def test_renderer_switches_against_the_dumped_schema(self):
        self.page('::figure{id=pair variant=off}\n\n::figure{id=bad}\n\n::figure{id=thrown variant=on}\n\n::figure{id=live-one}\n\n```text capture="words"\n```')
        self.manifest(
            self.recipe(id='pair', variants={'off': {'renderer': {'DitherOutput': False}}, 'on': {'renderer': {'DitherOutput': True}}}),
            self.recipe(id='bad', renderer={'Nope': True, 'FXAASubpixel': 0.5, 'GlobalIlluminationBounceGain': 2, 'DitherOutput': 'yes'}),
            self.recipe(id='thrown', variants={'off': {'setup': [{'command': 'viewport.capture', 'parameters': {'renderer': {'DitherOutput': False}}}]},
                                               'on': {}}),
            self.recipe(id='live-one', kind='live', shot=None, camera='scene', live={'atFixedStep': 1, 'frames': 1}, play={'steps': 4},
                        renderer={'DitherOutput': False}),
            self.recipe(id='words', kind='text', shot=None, project=None, renderer={'DitherOutput': False},
                        text={'program': 'StrataCLI', 'arguments': ['--help']}))
        code, lines = self.errors()
        self.assertEqual(code, 1, lines)
        text = '\n'.join(lines)
        self.assertIn('renderer: viewport.capture at the pin has no switch Nope: use one of DitherOutput, FXAASubpixel, '
                      'GlobalIlluminationBounceGain', text)
        self.assertIn('renderer: the switch FXAASubpixel is 0.5, which viewport.capture at the pin refuses', text)
        self.assertIn('renderer: the switch GlobalIlluminationBounceGain is 2, which viewport.capture at the pin refuses', text)
        self.assertIn('renderer: the switch DitherOutput is "yes", which viewport.capture at the pin refuses', text)
        self.assertIn('a setup step\'s viewport.capture takes a picture of its own, which the take throws away: set renderer on the recipe or '
                      'the variant, which the figure\'s own captures take', text)
        self.assertIn('live captures refuse renderer', text)
        self.assertIn('renderer switches are viewport.capture\'s: only scene figures take them', text)
        self.assertEqual(len(lines), 7, lines)
        # A pin whose viewport.capture takes no switches refuses them.
        self.write_dumps(renderer=False)
        self.manifest(self.recipe(id='pair', variants={'off': {'renderer': {'DitherOutput': False}}, 'on': {'renderer': {'DitherOutput': True}}}))
        code, lines = self.errors()
        self.assertEqual(code, 1, lines)
        self.assertIn('renderer: viewport.capture at the pin takes no renderer switches: take the figure once the pin has them '
                      '(waitsFor "tier 2: renderer switches")', '\n'.join(lines))

    def test_automation_runtime_and_live_recipes(self):
        self.book.write('layouts/inspect.ini', '; Strata editor layout for a window of 1280x720 pixels at UI scale 1 (tools/figures.py layout)\n')
        self.book.write('tutorials/core/time/Late.cpp', '// copied later\n')
        window = {'layout': 'layouts/inspect.ini', 'steps': [{'command': 'entity.create', 'parameters': {'name': 'A'}}]}
        self.page('\n\n'.join('::figure{id=%s}' % name for name in ('served', 'agent', 'still', 'game', 'short', 'still-live')))
        self.manifest(
            self.recipe(id='served', kind='editor', shot=None, project={'template': 'basic3d'}, editorWindow=window, automation=True),
            self.recipe(id='agent', kind='editor', shot=None, project={'template': 'basic3d'}, editorWindow=window, automation={'client': 'claude-code'},
                        files=[{'from': 'book:tutorials/core/time/Late.cpp', 'to': 'Scripts/Late.cpp', 'atStep': 1}]),
            self.recipe(id='still', automation=True),
            self.recipe(id='game', kind='runtime', shot=None, postProcess={'Bloom': True}, runtime={'resolution': [1280, 720], 'seconds': 2.5, 'quality': 'high'}),
            self.recipe(id='short', kind='live', shot=None, camera='scene', live={'atFixedStep': 30, 'frames': 2}, play={'steps': 10}),
            self.recipe(id='still-live', kind='live', shot=None, camera='scene', live={'atFixedStep': 3, 'frames': 1}),
            self.recipe(id='both', waitsFor='tier 3: a menu held open; no command opens it', blocked='the pin has no menu to hold open at all',
                        noStandIn='The page describes the menu in words.'))
        code, lines = self.errors()
        self.assertEqual(code, 1, lines)
        text = '\n'.join(lines)
        self.assertRegex(text, r'time\.json:\d+: automation is an editor figure\'s \(the window\'s status bar, Activity panel and Scene view show it\)')
        self.assertIn('an agent (automation.client) drives one window, and atStep closes it: copy the files before the editor opens the project', text)
        self.assertIn('a runtime figure is the exported game, which draws what the project saved with the runtime\'s options: it takes no '
                      'postProcess; change the copy in setup steps and save it (scene.save)', text)
        self.assertIn('runtime.seconds is 2.5: the runtime at the pin counts whole seconds of game time (--seconds <count>)', text)
        self.assertIn('play runs 10 fixed steps, fewer than live.atFixedStep 30: the capture would wait for a step that never runs', text)
        self.assertIn('a live figure plays its game to the fixed step it captures: add play {steps} (and input)', text)
        self.assertIn('a figure either waits for an addition (waitsFor) or is blocked at the pin with its reason (blocked): keep one', text)
        self.assertEqual(len(lines), 7, lines)
        # An agent's name is a short word or words, never a path.
        self.manifest(self.recipe(id='served', kind='editor', shot=None, project={'template': 'basic3d'}, editorWindow=window,
                                  automation={'client': 'C:\\Users\\someone'}))
        self.assertEqual(self.check()[0], 1)

    def test_a_figure_no_take_makes_is_placed_by_its_stand_in(self):
        self.page('::figure{id=drawing}\n\n:::figure{id=taken}\nMore about it.\n:::\n\n::figure{id=placed-waiting}\n\n::figure{id=other-drawing}')
        drawing = lambda name: self.recipe(id=name, kind='diagram', shot=None, project=None)
        waits = 'tier 3: a menu held open; no command opens it'
        self.manifest(
            drawing('drawing'), drawing('other-drawing'), drawing('unplaced-drawing'),
            self.recipe(id='taken'),
            self.recipe(id='menu', waitsFor=waits, standIn='drawing'),
            self.recipe(id='menu-words', waitsFor=waits, noStandIn='The page describes the menu in words.'),
            self.recipe(id='alone', blocked='the pin has no wind zone to show at all'),
            self.recipe(id='hidden', waitsFor=waits, standIn='unplaced-drawing'),
            self.recipe(id='placed-waiting', waitsFor=waits, standIn='other-drawing'),
            self.recipe(id='nowhere', waitsFor=waits, standIn='ghost'),
            self.recipe(id='eager', standIn='drawing'),
            self.recipe(id='forgotten'))
        code, lines = self.errors()
        self.assertEqual(code, 1, lines)
        text = '\n'.join(lines)
        page = 'src/content/docs/core/time.md'
        self.assertIn('the figure alone is blocked, and %s does not place it: name the figure that stands in for it (standIn) and place that, or '
                      'say why the page shows none (noStandIn)' % page, text)
        self.assertIn('%s does not place the stand-in unplaced-drawing of hidden: write ::figure{id=unplaced-drawing} where hidden would stand' % page, text)
        self.assertIn('%s places placed-waiting, which no take makes at the pin, and its stand-in is other-drawing: place other-drawing in its place' % page, text)
        self.assertIn('standIn "ghost" is no figure of src/content/figures/core/time.json', text)
        self.assertIn('only a figure that waits for an addition (waitsFor) or that no take can make at the pin (blocked) has a stand-in: remove standIn', text)
        self.assertIn('%s does not place the figure eager' % page, text)
        self.assertIn('%s does not place the figure forgotten: place it (::figure{id=forgotten}, or a text fence for a text figure), or remove its recipe' % page, text)
        self.assertEqual(len(lines), 7, lines)
        # list names the files of a blocked figure.
        code, output = quiet(figures.main, 'list', '--root', self.book.root)
        self.assertIn('core/time\talone\tscene\talone.avif blocked', output)

    def test_kinds_variants_crops_captions_and_records(self):
        self.page('')
        self.manifest(
            self.recipe(id='live-one', kind='live', camera=None, debugView='ao', live={'atFixedStep': 10, 'frames': 2}),
            self.recipe(id='crops', shot=None, camera='scene', crops=[{'name': 'a', 'rect': [0.5, 0.1, 0.2, 0.9], 'scale': 9}, {'name': 'a', 'rect': [0, 0, 1, 1], 'scale': 2}]),
            self.recipe(id='variants', variants={'one': {'size': [32, 32], 'antiAliasing': 'off'}}),
            self.recipe(id='caption', caption='The shadow map is 2048 texels wide, {stats.size} in all, {stats.off.width} off.',
                        record={'draws': '/renderStats/draws', 'bad': '/renderStats/nothing', 'worse': '/missing'},
                        variants={'off': {'antiAliasing': 'off'}, 'on': {'antiAliasing': 'taa'}}),
            self.recipe(id='relax', relax={'/pendingAssets': 'the sky loads late', '/nowhere': 'x', '/stalePoses': ' '}),
            self.recipe(id='text-one', kind='text', project=None, shot=None, text={'program': 'StrataCLI', 'arguments': ['--help'], 'redact': ['(']}),
            self.recipe(id='tool-one', kind='tool', project=None, shot=None, takenBy='playwright'),
            self.recipe(id='station', station='Dawn'),
        )
        code, lines = self.errors()
        text = '\n'.join(lines)
        self.assertIn('a live figure captures what the Game view shows: set camera "scene"', text)
        self.assertIn('live captures refuse debugView', text)
        self.assertIn('a crop is [x0, y0, x1, y1] of the picture, from 0 to 1, with x0 < x1 and y0 < y1', text)
        self.assertIn('scale is the whole factor the page enlarges the crop by, 1 to 8', text)
        self.assertIn('the crop name "a" is used twice', text)
        self.assertIn('a recipe with variants has at least two', text)
        self.assertIn('a variant may not set size', text)
        self.assertIn('{stats.size}: the recipe records no size', text)
        self.assertIn('{stats.off.width}: the variant off records no width', text)
        self.assertIn('the caption writes a number that is not {stats.…}', text)
        self.assertIn('record bad: renderStats has no field nothing at the pin', text)
        self.assertIn('record worse: /missing is no field of viewport.capture\'s result at the pin', text)
        self.assertNotIn('record draws', text)
        self.assertIn('relax /nowhere: only the pointers of the complete set can be relaxed', text)
        self.assertIn('relax /stalePoses needs its reason', text)
        self.assertNotIn('relax /pendingAssets', text)
        self.assertIn('redact "(" is not a regular expression', text)
        self.assertIn('a tool figure taken by Playwright names its page: add url', text)
        self.assertIn('stations are the Showcase\'s times of day', text)

    def test_measured_values_are_kept_named_as_patterns_and_said_in_the_caption(self):
        self.page('')
        self.manifest(
            self.recipe(id='perf', kind='text', project=None, shot=None, caption="One run's measurements.",
                        text={'command': {'command': 'editor.status'}, 'keep': ['/scene'], 'measured': ['/scene/name', '/engineCommit']}),
            self.recipe(id='uncaptioned', kind='text', project=None, shot=None, text={'command': {'command': 'editor.status'}, 'keep': ['/scene'], 'measured': ['/scene']}),
            self.recipe(id='clock', kind='text', project=None, shot=None, caption="One run's measurements.",
                        text={'program': 'StrataCLI', 'arguments': ['--help'], 'measured': ['[']}))
        code, lines = self.errors()
        text = '\n'.join(lines)
        self.assertIn('measured /engineCommit is no value keep shows: measure a value inside a kept pointer', text)
        self.assertNotIn('measured /scene/name', text)
        self.assertIn('the text holds measurements (measured): say in the caption that they are one run\'s measurements', text)
        self.assertEqual(text.count('the text holds measurements'), 1)
        self.assertIn('measured "[" is not a regular expression', text)

    def test_publish_is_required_for_renders_of_three_parts_and_interface_pictures_are_lossless(self):
        self.page('', page='image/tone-mapping')
        self.manifest(self.recipe(), self.recipe(id='window', kind='editor', shot=None, publish='lossless', editorWindow={'layout': 'layouts/one.ini', 'steps': []}),
                      self.recipe(id='viewport', kind='editor', shot=None, publish='lossy', editorWindow={'layout': 'layouts/one.ini', 'steps': []},
                                  variants={'a': {}, 'b': {'publish': 'lossless'}}),
                      page='image/tone-mapping')
        code, lines = self.errors()
        text = '\n'.join(lines)
        self.assertIn('a render of the part image says how it is published: add publish "lossy" or "lossless"', text)
        # An interface picture is lossless unless its recipe says lossy, for all its variants (rulings-13, R59).
        self.assertIn('pictures of the editor and of tools are lossless unless they say publish "lossy"', text)
        self.assertEqual(text.count('pictures of the editor and of tools are lossless unless'), 1)
        self.assertIn('says publish for the whole recipe: remove it from the variant', text)

    def test_interface_pictures_that_say_lossy_are_avif_at_quality_90(self):
        recipe = figures.Recipe('core/time', 'src/content/figures/core/time.json', {'id': 'viewport', 'kind': 'editor', 'publish': 'lossy'}, 0, [])
        self.assertEqual(recipe.publish(), 'lossy')
        self.assertEqual(recipe.extension(), '.avif')
        self.assertEqual(figures.encoder_settings(recipe, recipe.entry, None, False), ('lossy', 90))
        self.assertEqual(figures.encoder_settings(recipe, recipe.entry, 'chip', False), ('lossless', None))
        window = figures.Recipe('core/time', 'src/content/figures/core/time.json', {'id': 'window', 'kind': 'editor'}, 1, [])
        self.assertEqual(window.publish(), 'lossless')

    def test_waits_for_names_an_addition_the_pin_lacks(self):
        self.page('')
        self.manifest(self.recipe(id='a', waitsFor='tier 2: debug view specular'), self.recipe(id='b', waitsFor='tier 2: debug view ao'),
                      self.recipe(id='c', waitsFor='tier 1: something'), self.recipe(id='d', waitsFor='tier 3: the depth target; no debug view shows raw depth'),
                      self.recipe(id='e', waitsFor='tier 1: asset types'))
        self.write_dumps(debug_views=('none', 'ao'), extra_commands=('asset.types',))
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertNotIn('"tier 2: debug view specular": the pin already has', output)
        self.assertIn('note: waits for tier 2: debug view specular', output)
        self.assertIn('waitsFor names an addition of pipelines.md §11', output)
        self.assertIn('waitsFor "tier 1: asset types": the pin already has the command asset.types', output)
        self.assertNotIn('tier 3: the depth target; no debug view shows raw depth" ', output.replace('note: waits for', ''))
        self.assertEqual(output.count('waitsFor names an addition of pipelines.md §11'), 2)  # "debug view ao" and "tier 1: something"
        code, output = quiet(figures.main, 'list', '--waits', '--root', self.book.root)
        self.assertIn('tier 2: debug view specular (the debug view specular of viewport.capture):\n  core/time/a', output)
        self.assertIn('tier 3: the depth target; no debug view shows raw depth (a capture of tier 3):\n  core/time/d', output)


    def test_a_figure_no_take_makes_is_a_note_in_a_release_too(self):
        # At the final pin a figure that waits for an addition the release lacks, or is blocked, keeps its waitsFor or
        # blocked and its page shows its stand-in (rulings-12, R55): a release passes with it, its text file not taken.
        self.page('::figure{id=shot}\n\n```text capture="words"\n```')
        self.manifest(self.recipe(id='later', waitsFor='tier 3: the depth target; no debug view shows raw depth', standIn='shot'),
                      self.recipe(id='words', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['--help']}),
                      self.recipe(id='run', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['--version']},
                                  blocked='The pin\'s build holds no such program.', standIn='words'),
                      self.recipe())
        code, lines = self.errors('--release')
        text = '\n'.join(lines)
        self.assertNotIn('waits for tier 3', text)
        self.assertNotIn('run.txt', text)
        self.assertIn('no src/assets/figures/core/time/shot.avif yet', text)
        code, output = self.check('--release')
        self.assertIn('note: waits for tier 3: the depth target', output)
        self.assertIn('note: no src/assets/figures/core/time/run.txt yet (not taken)', output)
    def test_baselines(self):
        self.page('')
        baselines = tempfile.mkdtemp(prefix='baselines-')
        try:
            os.makedirs(os.path.join(baselines, 'v0.6.0', 'shots'))
            with open(os.path.join(baselines, 'v0.6.0', 'shots', 'tp.scene-1920x1080-off.png'), 'wb') as file:
                file.write(grey_png(4, 4))
            self.manifest(self.recipe(variants={'before': {'baseline': 'v0.6.0', 'antiAliasing': 'off'}, 'now': {'antiAliasing': 'off'}}),
                          self.recipe(id='taa', variants={'before': {'baseline': 'v0.7.0'}, 'now': {}}),
                          self.recipe(id='no-shot', shot=None, camera='scene', variants={'before': {'baseline': 'v0.7.0'}, 'now': {}}))
            code, output = self.check('--baselines', baselines)
            self.assertIn('the baseline set v0.7.0 has no v0.7.0', output)
            self.assertNotIn('tp.scene-1920x1080-off.png', output)
            self.assertIn('a "before" picture is the baseline set\'s file of a shot: the recipe needs shot', output)
            self.page('', page='core/other')
            self.manifest(self.recipe(id='other-set', variants={'before': {'baseline': 'v0.5.0'}, 'now': {}}), page='core/other')
            self.assertIn("must be one of 'v0.6.0', 'v0.7.0', 'v0.7.0-medium'", self.check()[1])
        finally:
            shutil.rmtree(baselines, ignore_errors=True)

    def test_labs_and_their_downloads(self):
        self.page('')
        self.book.write('labs/ladder.json', json.dumps([
            {'command': 'scene.new', 'parameters': {'name': 'Ladder'}}, {'command': 'entity.create', 'parameters': {'name': 'Rung'}},
            {'command': 'scene.saveAs', 'parameters': {'path': 'Scenes/Ladder.stscene'}},
            {'command': 'project.create', 'parameters': {'directory': 'C:/work'}}, {'command': 'asset.import', 'parameters': {'file': '@BOOK@/x.png'}},
            {'command': 'component.set', 'entityName': 'Rung'}, {'command': 'lab.unknown'}, {'command': 'preferences.save'}], indent='\t'))
        self.book.write('labs/ladder/Textures/rock.png', 'pixels')
        self.book.write('labs/CREDITS.md', '# Lab credits\n\n## ladder/Textures/rock.png\n\nRock, by Someone, CC BY 4.0.\n\n## other/file.png\n\nNot this lab.\n')
        self.manifest(self.recipe(shot=None, camera='scene', project={'lab': 'labs/ladder.json', 'template': 'empty'}, scene='Scenes/Ladder.stscene',
                                  setup=[{'command': 'component.set', 'entityName': 'Rung'}]),
                      self.recipe(id='gone', shot=None, camera='scene', project={'lab': 'labs/gone.json', 'template': 'basic3d'}))
        code, lines = self.errors()
        text = '\n'.join(lines)
        self.assertIn('labs/gone.json does not exist', text)
        self.assertIn('labs/ladder.json:', text)
        self.assertIn('a lab runs in an open project, so it never calls project.create: remove the step', text)
        self.assertIn('a lab holds no absolute path (C:/work)', text)
        self.assertIn('a lab holds no placeholder (@BOOK@)', text)
        self.assertIn('not entityName (entityName is the book\'s', text)
        self.assertIn('the command lab.unknown is not one the editor at the pin registers', text)
        self.assertIn('preferences.save changes the person\'s preferences', text)
        self.assertIn('its download public/downloads/labs/ladder.zip is missing: run python -I tools/figures.py labs ladder', text)
        self.assertNotIn('entityName "Rung" names', text)
        self.assertEqual(quiet(figures.main, 'labs', '--root', self.book.root)[0], 0)
        with zipfile.ZipFile(self.book.path('public/downloads/labs/ladder.zip')) as archive:
            self.assertEqual(sorted(archive.namelist()), ['CREDITS.md', 'Textures/rock.png', 'ladder.json'])
            credits = archive.read('CREDITS.md').decode('utf-8')
        self.assertIn('Rock, by Someone, CC BY 4.0.', credits)
        self.assertNotIn('Not this lab', credits)
        first = read_bytes(self.book.path('public/downloads/labs/ladder.zip'))
        quiet(figures.main, 'labs', 'ladder', '--root', self.book.root)
        self.assertEqual(read_bytes(self.book.path('public/downloads/labs/ladder.zip')), first)
        self.assertNotIn('download', '\n'.join(self.errors()[1]))
        self.book.write('labs/ladder/Textures/rock.png', 'other pixels')
        self.assertIn('differs from what figures.py labs writes', '\n'.join(self.errors()[1]))

    def test_published_files_against_their_recipes_and_stamps(self):
        self.page('::compare{id=pair}\n\n::figure{id=shot}\n\n::figure{id=shot crop=feet}')
        avif = figures_fake_avif(1920, 1080)
        self.book.write('src/assets/figures/core/time/shot.avif', avif, binary=True)
        self.book.write('src/assets/figures/core/time/shot.png', grey_png(4, 4), binary=True)
        self.book.write('src/assets/figures/core/time/shot-feet.webp', figures_fake_webp(960, 540, lossless=False), binary=True)
        self.book.write('src/assets/figures/core/time/stray.webp', figures_fake_webp(4, 4), binary=True)
        self.book.write('src/assets/figures/core/time/pair-off.avif', figures_fake_avif(1920, 1080), binary=True)
        self.book.write('src/assets/figures/core/time/pair-on.avif', figures_fake_avif(1920, 1080), binary=True)
        record = lambda name, data, size, quality=80: {'figure': name.split('.')[0].rsplit('-', 1)[0] if name.startswith('pair') else 'shot',
                                                       'variant': None, 'crop': None, 'kind': 'scene', 'pin': self.pin, 'build': None, 'reportedCommit': None,
                                                       'os': None, 'gpu': None, 'size': size, 'original': '0' * 64, 'sha256': hashlib.sha256(data).hexdigest(),
                                                       'encoder': {'format': 'avif', 'lossless': False, 'quality': quality, 'chromaSubsampling': '4:4:4', 'effort': 4, 'sharp': 'x'},
                                                       'recorded': {}, 'checkedAt': []}
        taken = {'shot.avif': record('shot.avif', avif, [1920, 1080]), 'pair-off.avif': record('pair-off.avif', figures_fake_avif(1920, 1080), [1920, 1080], 90),
                 'pair-on.avif': record('pair-on.avif', figures_fake_avif(1920, 1080), [1280, 720], 80), 'gone.avif': record('gone.avif', avif, [1, 1])}
        taken['pair-off.avif']['variant'] = 'off'
        taken['pair-on.avif']['variant'] = 'on'
        self.book.write('src/assets/figures/core/time/taken.json', json.dumps({'files': taken}, indent='\t'))
        self.manifest(self.recipe(), self.recipe(id='pair', variants={'off': {}, 'on': {}}))
        code, lines = self.errors()
        text = '\n'.join(lines)
        self.assertIn('src/assets/figures/core/time/shot.png: the recipe shot (src/content/figures/core/time.json:3) publishes this picture as '
                      'shot.avif (lossy: AVIF): remove shot.png', text)
        self.assertIn('shot-feet.webp: a lossy WebP file: crop pictures are lossless WebP (recipe src/content/figures/core/time.json:3): take and '
                      'publish it again (figures.py take, then figures.py publish)', text)
        self.assertIn('src/assets/figures/core/time/stray.webp: no recipe promises this file', text)
        self.assertIn('taken.json stamps gone.avif, which no recipe promises', text)
        self.assertIn('pair-on.avif: it is 1920 x 1080; its stamp says 1280 x 720', text)
        self.assertIn('a lossy picture on a slider is encoded at quality 90; its stamp says 80', text)
        self.assertIn('the slider\'s sides off and on differ in size', text)
        self.assertNotIn('shot.avif: its SHA-256', text)
        code, output = self.check()
        self.assertIn('shot-feet.webp: note: a placeholder: taken.json has no stamp for it (recipe src/content/figures/core/time.json:', output)
        self.book.write('src/assets/figures/core/time/shot.avif', figures_fake_avif(1280, 720), binary=True)
        self.assertIn('shot.avif: its SHA-256 differs from its stamp', '\n'.join(self.errors()[1]))

    def test_a_published_crop_no_page_places_is_an_error(self):
        self.page('::figure{id=shot}')
        self.manifest(self.recipe())
        webp = figures_fake_webp(256, 252)
        self.book.write('src/assets/figures/core/time/shot-feet.webp', webp, binary=True)
        record = {'figure': 'shot', 'variant': None, 'crop': 'feet', 'kind': 'scene', 'pin': self.pin, 'build': None, 'reportedCommit': None,
                  'os': None, 'gpu': None, 'size': [256, 252], 'original': '0' * 64, 'sha256': hashlib.sha256(webp).hexdigest(),
                  'encoder': {'format': 'webp', 'lossless': True, 'effort': 4, 'sharp': 'x'}, 'recorded': {}, 'checkedAt': []}
        self.book.write('src/assets/figures/core/time/taken.json', json.dumps({'files': {'shot-feet.webp': record}}, indent='\t'))
        text = '\n'.join(self.errors()[1])
        self.assertIn('src/assets/figures/core/time/shot-feet.webp: no page places the crop feet of shot (::figure{id=shot crop=feet}): remove the file '
                      'and its stamp, or place the crop', text)
        self.assertIn('taken.json stamps shot-feet.webp, the crop feet of shot, which no page places: remove the stamp and the file, or place the crop', text)
        self.assertNotIn('no recipe promises', text)
        self.page('::figure{id=shot}\n\n::figure{id=shot crop=feet}')
        self.assertNotIn('shot-feet', '\n'.join(self.errors()[1]))

    def test_a_text_figure_is_shown_in_a_fence_not_a_figure_directive(self):
        self.page('::figure{id=help}')
        self.manifest(self.recipe(id='help', kind='text', project=None, shot=None, text={'program': 'StrataCLI', 'arguments': ['--help']}))
        code, errors = self.errors()
        self.assertEqual(code, 1)
        self.assertIn('figure "help" is a text figure: show it in a fence, ```text capture="help"', '\n'.join(errors))

    def test_pages_name_recipes_variants_crops_and_text_figures(self):
        self.page('::figure{id=shot}\n\n::figure{id=pair}\n\n::figure{id=pair variant=up}\n\n::compare{id=shot}\n\n::compare{id=pair before=off after=down}\n\n'
                  '::figure{id=nothing}\n\n::figure{id=shot crop=hands}\n\n::figure\n\n```text capture="help"\nold\n```\n\n```text capture="shot"\n```')
        self.manifest(self.recipe(), self.recipe(id='pair', variants={'off': {}, 'on': {}}),
                      self.recipe(id='help', kind='text', project=None, shot=None, text={'program': 'StrataCLI', 'arguments': ['--help']}))
        self.manifest(self.recipe(), page='core/gone')
        code, lines = self.errors()
        text = '\n'.join(lines)
        self.assertIn('::figure{id=pair} names one of its variants: variant=off or variant=on', text)
        self.assertIn('::compare{id=shot} needs a recipe with two variants', text)
        self.assertIn('::compare after="down" is not a variant of pair: use one of off, on', text)
        self.assertIn('::figure{id=nothing}: src/content/figures/core/time.json has no figure "nothing"', text)
        self.assertIn('crop="hands" is not a crop of shot: use one of feet', text)
        self.assertIn('::figure needs an id', text)
        self.assertIn('capture="shot": the page has no text figure of that id', text)
        self.assertIn('src/content/figures/core/gone.json:1: there is no page core/gone.md for this manifest: write the page', text)
        # A text figure: fill copies it into its fence, check compares.
        self.book.write('src/assets/figures/core/time/help.txt', 'Usage: StrataCLI\n  call\n')
        self.assertIn('the fence differs from src/assets/figures/core/time/help.txt: run python -I tools/figures.py fill', text + '\n'.join(self.errors()[1]))
        code, output = quiet(figures.main, 'fill', '--root', self.book.root)
        self.assertEqual(code, 1)  # the capture="shot" fence names no text figure that was taken
        self.assertIn('```text capture="help"\nUsage: StrataCLI\n  call\n```', self.book.read('src/content/docs/core/time.md'))
        self.assertNotIn('help.txt', '\n'.join(self.errors()[1]))

    def test_a_text_figure_s_fence_has_the_form_the_build_reads(self):
        self.manifest(self.recipe(id='help', kind='text', project=None, shot=None, text={'program': 'StrataCLI', 'arguments': ['--help']}))
        self.book.write('src/assets/figures/core/time/help.txt', 'Usage: StrataCLI\n')
        self.page('```json capture="help"\nold\n```\n\n```text capture="help" sketch="core-time-help.cpp"\nold\n```\n\n'
                  '```text capture="help" pseudocode\nold\n```\n\n```text capture="help" variant="short"\nold\n```')
        lines = self.errors()[1]
        self.assertIn('src/content/docs/core/time.md:19: capture="help" is on a ```json fence: show a text figure in a ```text fence', lines)
        self.assertIn('src/content/docs/core/time.md:23: capture="help" is a kind of fence of its own: remove sketch', lines)
        self.assertIn('src/content/docs/core/time.md:27: capture="help" is a kind of fence of its own: remove pseudocode', lines)
        self.assertIn('src/content/docs/core/time.md:31: capture="help" has no variants: remove variant="short"', lines)
        # fill leaves those fences as they are and reports them.
        before = self.book.read('src/content/docs/core/time.md')
        code, output = quiet(figures.main, 'fill', '--root', self.book.root)
        self.assertEqual(code, 1, output)
        self.assertIn('src/content/docs/core/time.md:19: capture="help" is on a ```json fence: show a text figure in a ```text fence', output)
        self.assertIn('src/content/docs/core/time.md:23: capture="help" is a kind of fence of its own: remove sketch', output)
        self.assertEqual(self.book.read('src/content/docs/core/time.md'), before)


def figures_fake_avif(width, height):
    sys.path.insert(0, os.path.dirname(c_Fake))
    import fake_encoder
    return fake_encoder.avif(width, height, 128)


def figures_fake_webp(width, height, lossless=True):
    sys.path.insert(0, os.path.dirname(c_Fake))
    import fake_encoder
    data = fake_encoder.webp(width, height, 128)
    if not lossless:
        import struct
        body = b'\0\0\0\x9d\x01\x2a' + struct.pack('<HH', width, height) + b'\0' * 4
        data = b'RIFF' + struct.pack('<I', 4 + 8 + len(body)) + b'WEBP' + b'VP8 ' + struct.pack('<I', len(body)) + body
    return data


class FakeEditor:
    """A stand-in for booklib.editor.Editor: answers the commands a take of text figures sends. scene.loadStatus is ready
    after two fixed steps of a paused game."""
    calls = []
    steps = 0
    gpus = []
    commits = []
    captures = 0
    perfs = 0

    def __init__(self, build, work, log, project=None, gpu=False, window=None):
        self.log = log
        self.project = project
        self.window = window
        FakeEditor.gpus.append(gpu)

    def launch(self):
        FakeEditor.calls.append(('launch', None))
        self.running = True
        return {'ProcessId': 1}

    def check_commit(self, pin, provisional=False):
        FakeEditor.commits.append(provisional)
        return {'engineCommit': 'abcdef123456' if provisional else pin[:12], 'platform': 'Windows', 'gpu': None, 'provisional': provisional}

    def call(self, command, parameters=None, timeout=300):
        FakeEditor.calls.append((command, parameters))
        if command == 'project.templates':
            return {'templates': [{'id': 'empty'}, {'id': 'basic3d'}], 'default': 'empty'}
        if command == 'project.settings':
            return {'sections': [{'id': 'Renderer.Quality', 'value': {'Preset': 'High'}, 'isDefault': True}]}
        if command == 'entity.find':
            if parameters.get('component') == 'PostProcess':
                return {'entities': ['5EED']}
            return {'entities': [{'id': 'AB'}] if parameters.get('name') == 'Sun' else []}
        if command == 'editor.status':
            return {'scene': {'name': 'Main', 'modified': False}, 'engineCommit': '123'}
        if command == 'play.state':
            return {'paused': True, 'fixedSteps': FakeEditor.steps}
        if command == 'play.step':
            FakeEditor.steps += parameters['steps']
        if command == 'scene.loadStatus':
            return {'ready': FakeEditor.steps >= 2}
        if command == 'viewport.capture':
            # A figure named flicker gives another picture at every capture; the others the same one.
            FakeEditor.captures += 1
            grey = 100 + FakeEditor.captures if 'flicker' in parameters['path'] else 128
            data = grey_png(parameters['width'], parameters['height'], grey)
            for name, (pixels, levels) in c_Speckles.items():
                if '.%s-1.png' % name in parameters['path']:
                    data = speckled_png(parameters['width'], parameters['height'], pixels, levels)
            with open(parameters['path'], 'wb') as file:
                file.write(data)
            return dict(c_CompleteResult, Image={'MimeType': 'image/png', 'Data': 'AAAA'})
        if command == 'editor.perf':
            # Timings differ at every call; the count of frames does not.
            FakeEditor.perfs += 1
            return {'frames': 60, 'frame': {'mean': 16.0 + FakeEditor.perfs}, 'stages': {'Scene.Physics': {'mean': 2.0 + FakeEditor.perfs, 'calls': 1}}}
        return {}

    def quit(self):
        # As the editor's: a second quit of the same editor does nothing.
        if getattr(self, 'running', False):
            FakeEditor.calls.append(('quit', None))
        self.running = False


class TakeTests(FiguresTestCase):
    def setUp(self):
        super().setUp()
        self.build = tempfile.mkdtemp(prefix='build-')
        for name in ('StrataEditor', 'StrataCLI'):
            with open(editor.program_path(self.build, name), 'wb') as file:
                file.write(b'program')
        self.work = os.path.join(tempfile.mkdtemp(prefix='work-'), 'figures')
        FakeEditor.calls = []
        FakeEditor.steps = 0
        FakeEditor.gpus = []
        FakeEditor.commits = []
        FakeEditor.captures = 0
        FakeEditor.perfs = 0
        # A take shows the folders of its editor windows and staged programs under a drive of their own (subst on Windows);
        # the stand-in maps one folder at a time under c_DriveRoot and records each mapping and its release.
        self.mappings = []

        def map_drive(folder, work=None):
            self.assertFalse([entry for entry in self.mappings if not entry['released']], 'a drive is mapped twice at once')
            entry = {'folder': folder, 'released': False}
            self.mappings.append(entry)

            def release():
                entry['released'] = True
            return c_DriveRoot, release
        self.drive = mock.patch.object(figures, 'map_drive', map_drive)
        self.drive.start()

    def real(self, path):
        """The folder a path on the stand-in drive names, while its mapping lasts."""
        if not isinstance(path, str) or not path.startswith(c_DriveRoot):
            return path
        current = [entry for entry in self.mappings if not entry['released']]
        self.assertTrue(current, 'a program was given %s while no drive was mapped' % path)
        return os.path.join(current[-1]['folder'], path[len(c_DriveRoot):])

    def tearDown(self):
        self.drive.stop()
        shutil.rmtree(self.build, ignore_errors=True)
        shutil.rmtree(os.path.dirname(self.work), ignore_errors=True)
        super().tearDown()

    def take(self, *extra):
        def program(arguments, env, log, name, timeout, cwd=None, merge=True):
            self.assertEqual(env['STRATA_EDITOR_PATH'], editor.program_path(self.build, 'StrataEditor'))
            log.write(name, arguments, 'ran', 0)
            return 0, 'StrataCLI 0.7.0 - command-line client\n  call\n', ''
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', program):
            return quiet(figures.main, 'take', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build, '--work', self.work, *extra)

    def test_baselines_stop_the_run_and_look_dev_text_figures_wait_for_the_gpu(self):
        self.assertEqual(self.take('--kinds', 'text', '--baselines', self.work)[0], 2)
        # Text figures of the look-dev project are skipped and reported; the run takes the others (phase A, §13).
        self.manifest(self.recipe(id='lookdev', kind='text', shot=None, project={'lookdev': True}, text={'command': {'command': 'editor.status'}, 'keep': ['/scene']}),
                      self.recipe(id='templates', kind='text', shot=None, project=None, text={'command': {'command': 'project.templates'}, 'keep': ['/default']}))
        code, output = self.take('--kinds', 'text')
        self.assertEqual(code, 0, output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: skipped: core/time/lookdev: the look-dev project is made by '
                                 r'Tools/LookDev\.py capture, which needs the GPU: take it in phase B, after engine release 0\.8\.0$')
        self.assertIn('took 1 file into', output)
        self.assertNotIn('project.create', [command for command, _ in FakeEditor.calls])

    def test_scene_figures_are_captured_twice_in_a_gpu_editor_and_must_be_complete(self):
        self.manifest(
            self.recipe(id='lanterns', size=[16, 16], record={'draws': '/renderStats/draws'},
                        variants={'a': {'postProcess': {'Bloom': True}}, 'b': {'postProcess': {'Bloom': False}}}),
            self.recipe(id='poles', project={'lookdev': True}, shot='lookdev.thin', size=[16, 16], quality={'custom': {'ShadowMapSize': 1024}},
                        setup=[{'command': 'component.set', 'entityName': 'Sun', 'parameters': {'component': 'DirectionalLight', 'values': {}}}]),
            self.recipe(id='busy', size=[16, 16], expectAlso={'/renderStats/draws': {'min': 5}}),
            self.recipe(id='flicker', size=[16, 16]),
            self.recipe(id='before', size=[16, 16], variants={'old': {'baseline': 'v0.7.0'}, 'now': {}}))
        made = []

        def program(arguments, env, log, name, timeout, cwd=None, merge=True):
            log.write(name, arguments, 'ran', 0)
            if any(argument.endswith('LookDev.py') for argument in arguments):
                # LookDev.py capture makes the look-dev project in <--work>/projects/LookDev.
                project = os.path.join(arguments[arguments.index('--work') + 1], 'projects', 'LookDev')
                os.makedirs(project)
                open(os.path.join(project, 'LookDev.stproj'), 'w').close()
                made.append(arguments)
            return 0, '', ''
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', program):
            code, output = quiet(figures.main, 'take', '--kinds', 'scene', '--root', self.book.root, '--engine', self.engine.root,
                                 '--build', self.build, '--work', self.work)
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/busy: incomplete: /renderStats/draws is 3, at least 5 wanted')
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/flicker: the two captures differ in 256 pixels \(100 per cent\), by up to 1 level: nondeterministic')
        self.assertTrue(os.listdir(os.path.join(self.work, 'nondeterministic', 'core.time.flicker')))
        self.assertIn('skipped: core/time/before.old: a "before" picture', output)
        # Every scene figure runs in an editor with the GPU; the look-dev project is made once by LookDev.py and opened as a copy.
        self.assertEqual(set(FakeEditor.gpus[1:]), {True})
        self.assertEqual(len(made), 1)
        self.assertEqual(made[0][made[0].index('--shots') + 1], 'lookdev.overview')
        opened = [parameters['path'] for command, parameters in FakeEditor.calls if command == 'project.open']
        self.assertEqual(len(opened), 1)
        self.assertTrue(os.path.isfile(os.path.join(opened[0], 'LookDev.stproj')))
        # Two captures per picture, every parameter explicit.
        captures = [parameters for command, parameters in FakeEditor.calls if command == 'viewport.capture']
        self.assertEqual(len(captures), 2 * 6)  # lanterns a and b, poles, busy, flicker, before.now
        lantern = [parameters for parameters in captures if 'lanterns.a' in parameters['path']][0]
        self.assertEqual({key: value for key, value in lantern.items() if key != 'path'},
                         {'width': 16, 'height': 16, 'camera': 'scene', 'overlays': False, 'quality': 'high', 'debugView': 'none',
                          'waitForAssets': True, 'overwrite': True})
        pole = [parameters for parameters in captures if '.poles' in parameters['path']][0]
        self.assertEqual((pole['position'], pole['target'], pole['fov'], pole['quality']), ([6, 1.5, 8], [6, 0.8, 0], 40, 'project'))
        # The engine's PNG is the original; crops are cut from it; the result is kept without its image.
        self.assertEqual(read_bytes(os.path.join(self.work, 'shots', 'core.time.lanterns.a.png')), grey_png(16, 16))
        self.assertTrue(os.path.isfile(os.path.join(self.work, 'crops', 'core.time.lanterns.a-feet.png')))
        self.assertTrue(os.path.isfile(os.path.join(self.work, 'crops', 'core.time.poles-poles.png')))
        with open(os.path.join(self.work, 'results', 'core.time.lanterns.a.json'), encoding='utf-8') as file:
            self.assertNotIn('Image', json.load(file))
        with open(os.path.join(self.work, 'taken-pending.json'), encoding='utf-8') as file:
            pending = json.load(file)['pictures']
        self.assertEqual(sorted(pending), ['core.time.before.now', 'core.time.before.now-feet', 'core.time.lanterns.a', 'core.time.lanterns.a-feet',
                                           'core.time.lanterns.b', 'core.time.lanterns.b-feet', 'core.time.poles', 'core.time.poles-poles'])
        self.assertEqual((pending['core.time.lanterns.a']['kind'], pending['core.time.lanterns.a']['size'], pending['core.time.lanterns.a']['recorded']),
                         ('scene', [16, 16], {'draws': 3}))
        commands = [command for command, _ in FakeEditor.calls]
        self.assertEqual(commands.count('launch'), commands.count('quit'))

    def test_two_captures_are_one_picture_within_a_level_in_half_a_per_cent_of_the_pixels(self):
        # R57: every channel within 1 level and at most 0.5 per cent of the pixels differing is the same picture.
        self.manifest(self.recipe(id='steady', size=[16, 16]), self.recipe(id='dither', size=[16, 16]), self.recipe(id='speckle', size=[16, 16]),
                      self.recipe(id='jump', size=[16, 16]))
        code, output = self.take('--kinds', 'scene')
        self.assertEqual(code, 1, output)
        self.assertNotIn('core/time/dither', output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/speckle: the two captures differ in 2 pixels '
                                 r'\(0\.781 per cent\), by up to 1 level: nondeterministic')
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/jump: the two captures differ in 1 pixel '
                                 r'\(0\.391 per cent\), by up to 2 levels: nondeterministic')
        self.assertTrue(os.listdir(os.path.join(self.work, 'nondeterministic', 'core.time.speckle')))
        self.assertFalse(os.path.isdir(os.path.join(self.work, 'nondeterministic', 'core.time.dither')))
        # The first capture is the original, and the pending stamp records the measured difference.
        self.assertEqual(read_bytes(os.path.join(self.work, 'shots', 'core.time.dither.png')), grey_png(16, 16))
        with open(os.path.join(self.work, 'taken-pending.json'), encoding='utf-8') as file:
            pending = json.load(file)['pictures']
        self.assertEqual(sorted(pending), ['core.time.dither', 'core.time.dither-feet', 'core.time.steady', 'core.time.steady-feet'])
        self.assertEqual(pending['core.time.dither']['pairDifference'], {'pixels': 1, 'percent': 0.391, 'largest': 1})
        self.assertIsNone(pending['core.time.steady']['pairDifference'])

    def test_measured_values_of_a_text_figure_are_published_as_taken_once(self):
        # R57: a command's or a program's measurements cannot repeat; the rest of the text must.
        caption = "One run's measurements of the frame."
        self.manifest(
            self.recipe(id='perf', kind='text', shot=None, project=None, caption=caption,
                        text={'command': {'command': 'editor.perf'}, 'keep': ['/frames', '/frame', '/stages/Scene.Physics'],
                              'measured': ['/frame', '/stages/Scene.Physics/mean']}),
            self.recipe(id='unmeasured', kind='text', shot=None, project=None, text={'command': {'command': 'editor.perf'}, 'keep': ['/frames', '/frame']}),
            self.recipe(id='clock', kind='text', shot=None, project=None, caption=caption,
                        text={'program': 'StrataCLI', 'arguments': ['time'], 'redact': ['v[0-9]+'], 'measured': ['[0-9]+ ms']}),
            self.recipe(id='clockless', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['time']}))
        runs = []

        def program(arguments, env, log, name, timeout, cwd=None, merge=True):
            runs.append(arguments)
            log.write(name, arguments, 'ran', 0)
            return 0, 'StrataCLI v7: took %d ms\n' % (10 + len(runs)), ''
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', program):
            code, output = quiet(figures.main, 'take', '--kinds', 'text', '--root', self.book.root, '--engine', self.engine.root,
                                 '--build', self.build, '--work', self.work)
        self.assertEqual(code, 1, output)
        self.assertIn('failed: core/time/unmeasured: two runs of editor.perf gave different text', output)
        self.assertIn('failed: core/time/clockless: two runs of StrataCLI time gave different text after redact', output)
        text = lambda stem: read_text(os.path.join(self.work, 'text', stem + '.txt'))
        self.assertEqual(json.loads(text('core.time.perf')), {'frames': 60, 'frame': {'mean': 17.0}, 'stages': {'Scene.Physics': {'mean': 3.0, 'calls': 1}}})
        self.assertEqual(text('core.time.clock'), 'StrataCLI …: took 11 ms\n')

    def test_the_gpu_an_editor_reports_is_stamped_as_one_line_of_text(self):
        # editor.status {sections: ["editor"]} reports the GPU as an object; taken.json holds a string or null.
        answers = {'engine': {'engineCommit': self.pin[:12], 'platform': 'Windows'},
                   'editor': {'editor': {'gpu': {'api': 'Vulkan', 'apiVersion': '1.3.0', 'driver': '621.1.0', 'name': 'A GPU'}}}}
        session = editor.Editor(self.build, self.work, editor.Log(os.path.join(self.work, 'log')))
        with mock.patch.object(session, 'call', lambda command, parameters=None, timeout=0: answers[parameters['sections'][0]]):
            status = session.check_commit(self.pin)
        self.assertEqual(status['gpu'], 'A GPU (Vulkan 1.3.0, driver 621.1.0)')
        answers['editor'] = {'editor': {'gpu': 'Another GPU'}}
        with mock.patch.object(session, 'call', lambda command, parameters=None, timeout=0: answers[parameters['sections'][0]]):
            self.assertEqual(session.check_commit(self.pin)['gpu'], 'Another GPU')

    def test_text_figures_of_commands_and_programs(self):
        self.manifest(
            self.recipe(id='templates', kind='text', shot=None, project=None, text={'command': {'command': 'project.templates'}, 'keep': ['/default', '/templates/1/id']}),
            self.recipe(id='scene', kind='text', shot=None, project={'template': 'basic3d'}, setup=[{'command': 'component.get', 'entityName': 'Sun', 'parameters': {}}],
                        text={'command': {'command': 'editor.status'}, 'keep': ['/scene/name']}, record={'name': '/scene/name'}),
            self.recipe(id='help', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['--help'], 'redact': ['[0-9]+\\.[0-9]+\\.[0-9]+']}),
            self.recipe(id='later', kind='text', shot=None, project=None, waitsFor='tier 1: asset types', text={'command': {'command': 'asset.types'}, 'keep': ['/types']}),
            self.recipe(id='lost', kind='text', shot=None, project={'template': 'empty'}, setup=[{'command': 'component.get', 'entityName': 'Nobody'}],
                        text={'command': {'command': 'editor.status'}, 'keep': ['/scene/name']}))
        code, output = self.take('--kinds', 'text')
        self.assertEqual(code, 1, output)
        self.assertIn('skipped: core/time/later waits for tier 1: asset types', output)
        self.assertIn('failed: core/time/lost: entityName "Nobody" matches 0 entities; it must match exactly one', output)
        # Each line of the report starts with the recipe's file and line, and the summary says where the log is.
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: skipped: core/time/later waits for tier 1: asset types; take it once')
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/lost: ')
        self.assertIn('1 failed, 1 skipped; every command and its answer are in %s' % os.path.join(self.work, 'log'), output)
        text = lambda stem: read_text(os.path.join(self.work, 'text', stem + '.txt'))
        self.assertEqual(json.loads(text('core.time.templates')), {'default': 'empty', 'templates': {'1': {'id': 'basic3d'}}})
        self.assertEqual(json.loads(text('core.time.scene')), {'scene': {'name': 'Main'}})
        self.assertEqual(text('core.time.help'), 'StrataCLI … - command-line client\n  call\n')
        with open(os.path.join(self.work, 'taken-pending.json'), encoding='utf-8') as file:
            pending = json.load(file)['pictures']
        self.assertEqual(pending['core.time.scene']['recorded'], {'name': 'Main'})
        self.assertEqual(pending['core.time.help']['kind'], 'text')
        self.assertEqual(pending['core.time.templates']['reportedCommit'], self.pin[:12])
        # The project copy is made, the entity found by name and the settings restored; every editor ends.
        commands = [command for command, _ in FakeEditor.calls]
        self.assertIn('project.create', commands)
        self.assertEqual(commands.count('launch'), commands.count('quit'))
        self.assertEqual(sum(1 for command, parameters in FakeEditor.calls if command == 'component.get' and parameters.get('entity') == 'AB'), 1)
        # The next take empties the folder; a folder that is not a take's is refused.
        self.assertTrue(os.path.isfile(os.path.join(self.work, 'log', '0001-ran.log')) or os.listdir(os.path.join(self.work, 'log')))
        stranger = os.path.join(os.path.dirname(self.work), 'stranger')
        os.makedirs(stranger)
        open(os.path.join(stranger, 'mine.txt'), 'w').close()
        with mock.patch.object(editor, 'Editor', FakeEditor):
            code, output = quiet(figures.main, 'take', '--kinds', 'text', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build, '--work', stranger)
        self.assertEqual(code, 2)
        self.assertIn('holds files that are not a take of figures.py', output)

    def test_each_figure_of_a_copy_starts_from_its_scene_in_the_order_of_section_5_4(self):
        status = {'command': {'command': 'editor.status'}, 'keep': ['/scene/name']}
        self.manifest(
            self.recipe(id='first', kind='text', shot=None, project={'template': 'basic3d'}, text=status,
                        setup=[{'command': 'entity.create', 'parameters': {'name': 'Extra'}}]),
            self.recipe(id='second', kind='text', shot=None, project={'template': 'basic3d'}, text=status, world={'loadAll': True},
                        quality={'custom': {'ShadowMapSize': 1024}}, materials={'Materials/Ground.stmat': {'Roughness': 0.5}},
                        antiAliasing='fxaa', postProcess={'Bloom': False}, play={'steps': 4}),
            self.recipe(id='baked', kind='text', shot=None, project={'template': 'basic3d'}, text=status,
                        setup=[{'command': 'lighting.bakeProbes', 'parameters': {}}]),
            self.recipe(id='empty', kind='text', shot=None, project={'template': 'empty'}, text=status),
            self.recipe(id='course', kind='text', project={'sample': 'ThirdPerson'}, shot='tp.dof', text=status))
        code, output = self.take('--kinds', 'text')
        self.assertEqual(code, 0, output)
        calls = FakeEditor.calls
        commands = [command for command, _ in calls]
        # One basic3d copy holds first and second; baked and empty get copies of their own; the sample is a copy of its own kind.
        self.assertEqual([parameters['template'] for command, parameters in calls if command == 'project.create'], ['basic3d', 'basic3d', 'empty'])
        self.assertEqual([parameters for command, parameters in calls if command == 'project.openSample'][0]['sample'], 'ThirdPerson')
        # Every figure with a scene opens it again with force first, so the entity first made is gone for second.
        opened = [parameters for command, parameters in calls if command == 'scene.open']
        self.assertIn({'scene': 'Scenes/Main.stscene', 'force': True}, opened)
        self.assertIn({'scene': 'Scenes/Course.stscene', 'force': True}, opened)
        self.assertEqual(commands.count('scene.open'), 4)  # first, second, baked, course; the empty project has no scene to open
        second = commands.index('world.loadCells')
        self.assertEqual(commands[second - 2:second], ['scene.open', 'scene.loadStatus'])
        self.assertEqual(commands[second:second + 7], ['world.loadCells', 'project.setSettings', 'material.set', 'entity.find', 'component.set',
                                                       'play.start', 'play.step'])
        self.assertEqual(calls[second][1], {'region': {'min': [-20000, -20000], 'max': [20000, 20000]}, 'wait': True})
        self.assertEqual(calls[second + 1][1], {'section': 'Renderer.Quality', 'value': {'Preset': 'Custom', 'ShadowMapSize': 1024}})
        self.assertEqual(calls[second + 2][1], {'material': 'Materials/Ground.stmat', 'properties': {'Roughness': 0.5}, 'save': False})
        self.assertEqual(calls[second + 4][1], {'entity': '5EED', 'component': 'PostProcess', 'values': {
            'AntiAliasing': True, 'AntiAliasingMethod': 'FXAA', 'Bloom': False}})
        self.assertEqual(calls[second + 5][1], {'paused': True})
        self.assertEqual(calls[second + 6][1], {'steps': 4})
        self.assertEqual(commands[second + 7:second + 10], ['editor.status', 'editor.status', 'play.stop'])
        # The shot's Setup runs with its entity named by ID, as Shots.json writes it.
        self.assertIn(('component.set', {'entity': '350D7DDD7ED21DD5'}), calls)
        self.assertEqual(commands.count('launch'), commands.count('quit'))

    def test_a_lab_and_a_station_in_a_text_take(self):
        self.book.write('labs/yard.json', json.dumps([
            {'command': 'scene.new', 'parameters': {'name': 'Yard'}}, {'command': 'entity.create', 'parameters': {'name': 'Lamp'}},
            {'command': 'scene.saveAs', 'parameters': {'path': 'Scenes/Yard.stscene'}}]))
        self.book.write('labs/yard/Textures/stone.png', 'pixels')
        status = {'command': {'command': 'editor.status'}, 'keep': ['/scene/name']}
        self.manifest(self.recipe(id='yard', kind='text', shot=None, project={'lab': 'labs/yard.json', 'template': 'empty'},
                                  scene='Scenes/Yard.stscene', text=status),
                      self.recipe(id='dawn', kind='text', shot=None, project={'sample': 'Showcase'}, station='Dawn', text=status))
        stations = []

        def program(arguments, env, log, name, timeout, cwd=None, merge=True):
            log.write(name, arguments, 'ran', 0)
            if name.startswith('station-'):
                stations.append(arguments[1:])
                return 0, json.dumps([{'command': 'component.set', 'parameters': {'component': 'DirectionalLight', 'values': {'Intensity': 7}}}]), ''
            return 0, 'StrataCLI 0.7.0\n', ''
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', program):
            code, output = quiet(figures.main, 'take', '--kinds', 'text', '--root', self.book.root, '--engine', self.engine.root,
                                 '--build', self.build, '--work', self.work)
        self.assertEqual(code, 0, output)
        calls = FakeEditor.calls
        commands = [command for command, _ in calls]
        # The lab: an empty project, the lab's files in its asset folder, its script run step by step, then its saved scene opened.
        self.assertIn(('project.create', {'directory': os.path.join(self.work, 'projects', '01'), 'name': 'Lab', 'template': 'empty'}), calls)
        self.assertTrue(os.path.isfile(os.path.join(self.work, 'projects', '01', 'Assets', 'Textures', 'stone.png')))
        created = commands.index('project.create')
        self.assertEqual(commands[created + 1:created + 6], ['scene.new', 'entity.create', 'scene.saveAs', 'project.settings', 'scene.open'])
        self.assertEqual(calls[created + 5][1], {'scene': 'Scenes/Yard.stscene', 'force': True})
        # The station: the steps Tools/GenerateShowcaseTerrain.py writes for it, run on a copy of the Showcase.
        self.assertEqual(stations, [['-I', os.path.join(self.engine.root, 'Tools', 'GenerateShowcaseTerrain.py'), 'setup', '--station', 'Dawn',
                                     '--format', 'script']])
        self.assertIn(('project.openSample', {'sample': 'Showcase', 'directory': os.path.join(self.work, 'projects', '02')}), calls)
        self.assertIn(('component.set', {'component': 'DirectionalLight', 'values': {'Intensity': 7}}), calls)

    def test_steps_with_until_are_asked_again_between_fixed_steps(self):
        ready = {'command': 'scene.loadStatus', 'until': {'steps': 5}, 'expect': {'/ready': {'equals': True}}}
        self.manifest(self.recipe(id='ready', kind='text', shot=None, project={'template': 'basic3d'}, setup=[ready],
                                  text={'command': {'command': 'editor.status'}, 'keep': ['/scene/name']}),
                      self.recipe(id='never', kind='text', shot=None, project={'template': 'basic3d'}, setup=[dict(ready, until={'steps': 1}, expect={'/ready': {'equals': 'never'}})],
                                  text={'command': {'command': 'editor.status'}, 'keep': ['/scene/name']}))
        code, output = self.take('--kinds', 'text')
        self.assertEqual(code, 1)
        self.assertNotIn('core/time/ready:', output)
        self.assertIn('failed: core/time/never: scene.loadStatus: until ran out: scene.loadStatus: /ready is true, not "never"', output)
        self.assertEqual([command for command, _ in FakeEditor.calls].count('play.step'), 3)

    def test_reference_and_tool_figures_with_their_crops(self):
        import sketches
        self.book.write('sketches/core-time-tracer.cpp', 'int main() { return 0; }\n')
        self.manifest(self.recipe(id='box', kind='reference', shot=None, project=None, publish='lossless', reference={'sketch': 'core-time-tracer.cpp'},
                                  crops=[{'name': 'corner', 'rect': [0.5, 0.5, 1.0, 1.0], 'scale': 2}]),
                      self.recipe(id='page', kind='tool', shot=None, project=None, takenBy='playwright', url='https://example.com/run'),
                      self.recipe(id='desk', kind='tool', shot=None, project=None, takenBy='owner'))
        ppm = b'P6\n4 2\n255\n' + bytes(range(24))
        ran = []
        real_run = subprocess.run

        def run(arguments, **options):
            if 'core-time-tracer' not in arguments[0]:
                return real_run(arguments, **options)  # git, for the preflight checks
            ran.append(arguments[0])
            return subprocess.CompletedProcess(arguments, 0, ppm, b'')

        def screenshot(arguments, env, log, name, timeout, cwd=None, merge=True):
            with open(arguments[-1], 'wb') as file:
                file.write(grey_png(8, 4))
            return 0, '', ''
        with mock.patch.object(sketches, 'find_compiler', lambda otherwise: 'c++'), mock.patch.object(sketches, 'glm_include', lambda engine, pin: None), \
                mock.patch.object(sketches, 'compile_cpp', lambda *arguments: None), mock.patch.object(figures.subprocess, 'run', run), \
                mock.patch.object(editor, 'run_program', screenshot), mock.patch.object(figures.shutil, 'which', lambda name: name):
            code, output = quiet(figures.main, 'take', '--kinds', 'reference,tool', '--root', self.book.root, '--engine', self.engine.root, '--work', self.work)
        self.assertEqual(code, 0, output)
        self.assertEqual(len(ran), 2)  # two runs of the sketch, which must give the same image
        self.assertIn('skipped: core/time/desk: the owner takes it (takenBy "owner")', output)
        shot = images.read_png(read_bytes(os.path.join(self.work, 'shots', 'core.time.box.png')))
        self.assertEqual((shot.width, shot.height, bytes(shot.data)), (4, 2, bytes(range(24))))
        corner = images.read_png(read_bytes(os.path.join(self.work, 'crops', 'core.time.box-corner.png')))
        self.assertEqual((corner.width, corner.height, bytes(corner.data)), (2, 1, bytes(range(18, 24))))
        with open(os.path.join(self.work, 'taken-pending.json'), encoding='utf-8') as file:
            pending = json.load(file)['pictures']
        self.assertEqual(sorted(pending), ['core.time.box', 'core.time.box-corner', 'core.time.page'])
        self.assertEqual((pending['core.time.box-corner']['crop'], pending['core.time.box-corner']['size']), ('corner', [2, 1]))
        self.assertIsNone(pending['core.time.page']['build'])

    def test_reference_figures_find_their_compiler_and_glm_before_anything_starts(self):
        import sketches
        later = self.recipe(id='later', kind='reference', shot=None, project=None, publish='lossless', waitsFor='tier 1: asset types',
                            reference={'sketch': 'core-time-later.cpp'})
        self.manifest(self.recipe(id='box', kind='reference', shot=None, project=None, publish='lossless', reference={'sketch': 'core-time-tracer.cpp'}), later)
        take = lambda: quiet(figures.main, 'take', '--kinds', 'reference', '--root', self.book.root, '--engine', self.engine.root, '--work', self.work)
        real_which = shutil.which
        no_compiler = lambda name, *arguments, **options: None if name in ('g++', 'clang++', 'c++') else real_which(name, *arguments, **options)
        with mock.patch.dict(os.environ, {'CXX': ''}), mock.patch.object(sketches.shutil, 'which', no_compiler):
            code, output = take()
        self.assertEqual(code, 2, output)
        self.assertIn('figures: reference figures: no C++ compiler found: set CXX or put g++ on the PATH, or leave reference out of --kinds', output)
        self.assertFalse(os.path.exists(self.work))  # nothing was started or written
        stale = sketches.UsageError('the clone\'s Strata/vendor/glm is at 0123456789ab, not at ba9876543210, the commit the pin records')
        with mock.patch.object(sketches, 'find_compiler', lambda otherwise: 'c++'), mock.patch.object(sketches, 'glm_include', mock.Mock(side_effect=stale)):
            code, output = take()
        self.assertEqual(code, 2, output)
        self.assertIn('figures: reference figures: the clone\'s Strata/vendor/glm is at 0123456789ab', output)
        # A sketch that does not exist fails its figure, and names what to do.
        with mock.patch.object(sketches, 'find_compiler', lambda otherwise: 'c++'), mock.patch.object(sketches, 'glm_include', lambda engine, pin: None):
            code, output = take()
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/box: sketches/core-time-tracer\.cpp does not '
                                 r'exist: write the sketch, or correct its name in the recipe$')
        # Figures that wait for an addition need no compiler.
        self.manifest(later)
        with mock.patch.dict(os.environ, {'CXX': ''}), mock.patch.object(sketches.shutil, 'which', no_compiler):
            code, output = take()
        self.assertEqual(code, 0, output)
        self.assertIn('skipped: core/time/later waits for tier 1: asset types', output)

    def editor_recipes(self):
        self.book.write('layouts/inspect.ini', '; Strata editor layout for a window of 1280x720 pixels at UI scale 1 (tools/figures.py layout)\n[Docking][Data]\n')
        waits = 'tier 2: editor screenshot'
        self.manifest(
            self.recipe(id='inspector', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                        editorWindow={'layout': 'layouts/inspect.ini', 'panel': 'Inspector', 'steps': [
                            {'command': 'entity.find', 'parameters': {'name': 'Sun'}, 'bind': {'sun': '/entities/0'}},
                            {'command': 'selection.set', 'parameters': {'entities': [{'$ref': 'sun'}]}},
                            {'command': 'component.get', 'entityName': 'Sun', 'parameters': {'component': 'Transform'}}]}),
            self.recipe(id='window', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                        editorWindow={'layout': 'layouts/inspect.ini', 'windowSize': [1280, 720], 'steps': []},
                        crops=[{'name': 'corner', 'rect': [0.5, 0.5, 1.0, 1.0], 'scale': 2}]),
            self.recipe(id='unsettled', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                        editorWindow={'layout': 'layouts/inspect.ini', 'steps': []}),
            self.recipe(id='missing', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                        editorWindow={'layout': 'layouts/gone.ini', 'steps': []}),
            self.recipe(id='wide', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                        editorWindow={'layout': 'layouts/inspect.ini', 'windowSize': [1600, 900], 'steps': []}),
            self.recipe(id='later', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor='tier 3: a menu held open; the editor has no command for it',
                        editorWindow={'layout': 'layouts/inspect.ini', 'steps': []}))

    def window_program(self, runs):
        """A stand-in for the editors in a window: runs holds (arguments, script); the screenshot is grey, a panel 120 x 80,
        and a picture named unsettled stops the script as the editor's runner does; the layout file is written at the end."""
        def program(arguments, env, log, name, timeout, cwd=None, merge=True):
            log.write(name, arguments, 'ran', 0)
            if '--window-size' not in arguments:
                return 0, '', ''
            with open(self.real(arguments[arguments.index('--commands') + 1]), encoding='utf-8') as file:
                script = json.load(file)
            runs.append((arguments, script))
            with open(self.real(arguments[arguments.index('--layout') + 1]), 'w', encoding='utf-8', newline='\n') as file:
                file.write('[Docking][Data]\nDockSpace ID=0x8B93E3BD Window=0xA787BDB4 Pos=0,24 Size=1280,696\n')
            for number, step in enumerate(script):
                if step['command'] != 'editor.screenshot':
                    continue
                if 'unsettled' in arguments[arguments.index('--commands') + 1]:
                    return 1, 'Strata Editor\nCommand script step %d (editor.screenshot) failed: expected /settled to equal true, got false\n' % (number + 1), ''
                width, height = (120, 80) if 'panel' in step['parameters'] else map(int, arguments[arguments.index('--window-size') + 1].split('x'))
                with open(self.real(step['parameters']['path']), 'wb') as file:
                    file.write(grey_png(width, height))
            return 0, 'ran', ''
        return program

    def test_editor_figures_wait_for_the_pin_and_a_provisional_build_takes_them(self):
        self.editor_recipes()
        runs = []
        take = lambda *extra: quiet(figures.main, 'take', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build, '--work', self.work,
                                    '--kinds', 'editor', *extra)
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', self.window_program(runs)):
            # At the pin's build the figures still wait for editor.screenshot: no window opens.
            code, output = take()
            self.assertEqual(code, 0, output)
            self.assertIn('skipped: core/time/inspector waits for tier 2: editor screenshot', output)
            self.assertEqual(runs, [])
            FakeEditor.calls, FakeEditor.commits = [], []
            code, output = take('--provisional')
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'(?m)^figures: provisional: the build reports the engine commit abcdef123456, not the pin %s: the commit check '
                                 r'is skipped; publish refuses this take$' % self.pin[:12])
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: provisional: core/time/inspector waits for tier 2: editor screenshot '
                                 r'at the pin; taken with the provisional build \(keep waitsFor\)$')
        self.assertIn('skipped: core/time/later waits for tier 3: a menu held open', output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/missing: the layout layouts/gone\.ini does not '
                                 r'exist: make it with figures\.py layout gone \(plan/card/photo-editor\.md\)$')
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/wide: the layout layouts/inspect\.ini was made for '
                                 r'a window of 1280x720, not 1600x900: make a layout for that window, or take the figure at 1280x720$')
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/unsettled: the window\'s command script .+ stopped '
                                 r'\(StrataEditor exit code 1\): Command script step 4 \(editor\.screenshot\) failed: expected /settled to equal true, got false$')
        self.assertTrue(FakeEditor.commits and all(FakeEditor.commits))
        # The project copies are made in editors without a window, one per figure; each figure then runs one editor in a
        # window at the recipe's size, on a copy of the layout, without automation.
        self.assertEqual([parameters['template'] for command, parameters in FakeEditor.calls if command == 'project.create'], ['basic3d'] * 3)
        commands = [command for command, _ in FakeEditor.calls]
        self.assertEqual(commands.count('launch'), commands.count('quit'))
        self.assertEqual(len(runs), 3)
        for arguments, _ in runs:
            # The window sees its copy, its layout and its script on a drive of its own: no path of the machine.
            self.assertEqual(arguments[:7], [editor.program_path(self.build, 'StrataEditor'), '--window-size', '1280x720', '--ui-scale', '1', '--layout',
                                             c_DriveRoot + os.path.join('Editor', 'Layout.ini')])
            self.assertEqual(arguments[7:], ['--no-automation', '--project', c_DriveRoot + os.path.join('Projects', 'Figures'), '--commands', arguments[11],
                                             '--quit-after-commands'])
            self.assertTrue(arguments[11].startswith(c_DriveRoot + 'Editor' + os.sep))
        self.assertTrue(self.mappings and all(entry['released'] for entry in self.mappings))
        self.assertTrue(all(entry['folder'].startswith(os.path.join(self.work, 'projects') + os.sep) for entry in self.mappings))
        script = [script for arguments, script in runs if 'core.time.inspector.json' in arguments[11]][0]
        self.assertEqual([step['command'] for step in script], ['scene.open', 'scene.loadStatus', 'entity.find', 'selection.set', 'entity.find', 'component.get',
                                                                'editor.wait', 'editor.showPanel', 'editor.screenshot'])
        self.assertEqual(script[0]['parameters'], {'scene': 'Scenes/Main.stscene', 'force': True})
        self.assertEqual(script[3]['parameters'], {'entities': [{'$ref': 'sun'}]})
        self.assertEqual((script[4], script[5]), ({'command': 'entity.find', 'parameters': {'name': 'Sun'}, 'bind': {'figuresEntity1': '/entities/0'}},
                                                 {'command': 'component.get', 'parameters': {'component': 'Transform', 'entity': {'$ref': 'figuresEntity1'}}}))
        self.assertEqual(script[-1], {'command': 'editor.screenshot', 'parameters': {
            'panel': 'Inspector', 'path': c_DriveRoot + os.path.join('Editor', 'Screenshot.png'), 'overwrite': True}, 'expect': {'/settled': {'equals': True}}})
        self.assertEqual(read_bytes(os.path.join(self.work, 'shots', 'core.time.inspector.png')), grey_png(120, 80))
        window = [script for arguments, script in runs if 'core.time.window.json' in arguments[11]][0]
        self.assertEqual(window[-1]['expect'], {'/settled': {'equals': True}, '/width': {'equals': 1280}, '/height': {'equals': 720}})
        with open(os.path.join(self.work, 'taken-pending.json'), encoding='utf-8') as file:
            pending = json.load(file)
        self.assertEqual(pending['provisional'], {'reportedCommit': 'abcdef123456'})
        self.assertEqual(sorted(pending['pictures']), ['core.time.inspector', 'core.time.window', 'core.time.window-corner'])
        self.assertEqual((pending['pictures']['core.time.inspector']['kind'], pending['pictures']['core.time.inspector']['size']), ('editor', [120, 80]))
        self.assertEqual(pending['pictures']['core.time.window']['size'], [1280, 720])
        # A provisional take is for trying recipes: publish refuses it.
        code, output = quiet(figures.main, 'publish', '--from', self.work, '--root', self.book.root)
        self.assertEqual(code, 2, output)
        self.assertIn('was taken with --provisional (a build that is not the pin\'s): publish refuses it; take the figures again at the pin', output)
        self.assertFalse(os.path.exists(self.book.path('src/assets/figures/core/time')))

    def tutorial_files(self):
        """A page tutorial whose stage 1 copies Coin.cpp, and a file a recipe names alone."""
        self.book.write('tutorials/core/time/Coin.cpp', '// the coin\n')
        self.book.write('tutorials/core/time/Late.cpp', '// copied later\n')
        self.book.write('tutorials/core/time.tutorial.json', json.dumps({'page': 'core/time', 'startsFrom': {'template': 'basic3d'}, 'stages': [
            {'step': 1, 'files': [{'from': 'book:tutorials/core/time/Coin.cpp', 'to': 'Scripts/Coin.cpp'}]}]}))

    def test_files_go_into_the_project_copy_before_the_window_opens_or_at_their_step(self):
        self.tutorial_files()
        self.book.write('layouts/inspect.ini', '; Strata editor layout for a window of 1280x720 pixels at UI scale 1 (tools/figures.py layout)\n[Docking][Data]\n')
        steps = [{'command': 'entity.create', 'parameters': {'name': 'A'}}, {'command': 'script.build', 'parameters': {'wait': True}}]
        self.manifest(self.recipe(id='built', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor='tier 2: editor screenshot',
                                  editorWindow={'layout': 'layouts/inspect.ini', 'panel': 'Problems', 'steps': steps},
                                  files=[{'stage': 1}, {'from': 'book:tutorials/core/time/Late.cpp', 'to': 'Scripts/Later/Late.cpp', 'atStep': 2}]))
        runs, seen = [], []
        program = self.window_program(runs)

        def watching(arguments, env, log, name, timeout, cwd=None, merge=True):
            if '--window-size' in arguments:
                project = self.real(arguments[arguments.index('--project') + 1])
                seen.append(sorted(os.path.relpath(os.path.join(folder, file), project).replace(os.sep, '/')
                                   for folder, _, files in os.walk(project) for file in files))
            return program(arguments, env, log, name, timeout, cwd, merge)
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', watching):
            code, output = quiet(figures.main, 'take', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build, '--work',
                                 self.work, '--kinds', 'editor', '--provisional')
        self.assertEqual(code, 0, output)
        # Stage 1's file is there when the first window opens; the file of atStep 2 only after that window closed, and a
        # second window runs the rest on the same copy.
        self.assertEqual(seen, [['Scripts/Coin.cpp'], ['Scripts/Coin.cpp', 'Scripts/Later/Late.cpp']])
        self.assertEqual([[step['command'] for step in script] for _, script in runs], [
            ['scene.open', 'scene.loadStatus', 'entity.create'],
            ['scene.open', 'scene.loadStatus', 'script.build', 'editor.wait', 'editor.showPanel', 'editor.screenshot']])
        self.assertEqual(runs[0][0][runs[0][0].index('--project') + 1], runs[1][0][runs[1][0].index('--project') + 1])
        self.assertEqual(len({entry['folder'] for entry in self.mappings}), 1)
        self.assertEqual(read_text(os.path.join(self.mappings[0]['folder'], 'Projects', 'Figures', 'Scripts', 'Coin.cpp')), '// the coin\n')
        self.assertTrue(os.path.isfile(os.path.join(self.work, 'shots', 'core.time.built.png')))

    def test_a_scene_figure_opens_its_copy_again_after_the_files_and_copies_later_ones_at_their_step(self):
        self.tutorial_files()
        seen = []
        late = []

        class Watching(FakeEditor):
            def call(self, command, parameters=None, timeout=300):
                if command in ('entity.create', 'script.build'):
                    seen.append((command, os.path.isfile(late[0]) if late else None))
                if command == 'project.openSample':
                    late.append(os.path.join(parameters['directory'], 'Scripts', 'Late.cpp'))
                return FakeEditor.call(self, command, parameters, timeout)
        self.manifest(self.recipe(id='coins', size=[16, 16], setup=[{'command': 'entity.create', 'parameters': {}}, {'command': 'script.build'}],
                                  files=[{'from': 'book:tutorials/core/time/Coin.cpp', 'to': 'Scripts/Coin.cpp'},
                                         {'from': 'book:tutorials/core/time/Late.cpp', 'to': 'Scripts/Late.cpp', 'atStep': 2}]))
        with mock.patch.object(editor, 'Editor', Watching), mock.patch.object(editor, 'run_program', lambda *arguments, **options: (0, '', '')):
            code, output = quiet(figures.main, 'take', '--kinds', 'scene', '--root', self.book.root, '--engine', self.engine.root,
                                 '--build', self.build, '--work', self.work)
        self.assertEqual(code, 0, output)
        self.assertEqual(seen, [('entity.create', False), ('script.build', True)])
        commands = [command for command, _ in FakeEditor.calls]
        self.assertLess(commands.index('project.openSample'), commands.index('project.open'))
        opened = [parameters for command, parameters in FakeEditor.calls if command == 'project.open'][0]
        self.assertEqual(opened, {'path': os.path.dirname(os.path.dirname(late[0])), 'force': True})
        self.assertTrue(os.path.isfile(os.path.join(opened['path'], 'Scripts', 'Coin.cpp')))

    def test_renderer_switches_reach_the_figure_s_own_captures_and_its_stamp(self):
        self.manifest(self.recipe(id='dither', size=[16, 16], variants={'off': {'renderer': {'DitherOutput': False}}, 'on': {'renderer': {'DitherOutput': True}}}),
                      self.recipe(id='plain', size=[16, 16]),
                      self.recipe(id='ignored', size=[16, 16], renderer={'SpecularAntiAliasing': False}))

        class Echoing(FakeEditor):
            # As the pin's capture: the result echoes the switches it drew with; one that ignored them echoes none.
            def call(self, command, parameters=None, timeout=300):
                result = FakeEditor.call(self, command, parameters, timeout)
                if command == 'viewport.capture':
                    result['renderer'] = {} if 'ignored' in parameters['path'] else dict(parameters.get('renderer') or {})
                return result
        with mock.patch.object(editor, 'Editor', Echoing), mock.patch.object(editor, 'run_program', lambda *arguments, **options: (0, '', '')):
            code, output = quiet(figures.main, 'take', '--kinds', 'scene', '--root', self.book.root, '--engine', self.engine.root,
                                 '--build', self.build, '--work', self.work)
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/ignored: the capture drew with the renderer '
                                 r'switches \{\}, not \{"SpecularAntiAliasing": false\}')
        captures = [parameters for command, parameters in FakeEditor.calls if command == 'viewport.capture']
        self.assertEqual([parameters['renderer'] for parameters in captures if '.dither.off' in parameters['path']], [{'DitherOutput': False}] * 2)
        self.assertEqual([parameters['renderer'] for parameters in captures if '.dither.on' in parameters['path']], [{'DitherOutput': True}] * 2)
        self.assertFalse([parameters for parameters in captures if '.plain' in parameters['path'] and 'renderer' in parameters])
        with open(os.path.join(self.work, 'taken-pending.json'), encoding='utf-8') as file:
            pending = json.load(file)['pictures']
        self.assertEqual(pending['core.time.dither.off']['renderer'], {'DitherOutput': False})
        self.assertEqual(pending['core.time.dither.off-feet']['renderer'], {'DitherOutput': False})
        self.assertIsNone(pending['core.time.plain']['renderer'])

    def test_automation_figures_serve_and_an_agent_sends_their_steps(self):
        self.book.write('layouts/inspect.ini', '; Strata editor layout for a window of 1280x720 pixels at UI scale 1 (tools/figures.py layout)\n[Docking][Data]\n')
        steps = [{'command': 'entity.create', 'parameters': {'name': 'Crate'}, 'bind': {'crate': '/id'}},
                 {'command': 'selection.set', 'parameters': {'entities': [{'$ref': 'crate'}]}}]
        self.manifest(
            self.recipe(id='served', kind='editor', shot=None, project={'template': 'basic3d'}, editorWindow={'layout': 'layouts/inspect.ini', 'steps': []},
                        automation=True),
            self.recipe(id='agent', kind='editor', shot=None, project={'template': 'basic3d'}, editorWindow={'layout': 'layouts/inspect.ini', 'steps': steps},
                        automation={'client': 'claude-code'}))
        runs, programs, agents = [], [], []
        test = self

        class Window:
            def __init__(self, arguments, env, log, name, cwd=None):
                programs.append((arguments, env))
                self.pid = 7

            def alive(self):
                return True

            def finish(self, timeout):
                return 0, '[info] Automation: listening on 127.0.0.1:50001\n'

        class Agent:
            def __init__(self, build, env, log, client, project=None, timeout=300, program=None):
                self.client, self.env, self.project, self.sent = client, env, project, []
                agents.append(self)

            def initialize(self):
                self.sent.append('initialize')

            def wait_for_editor(self, seconds, alive):
                self.sent.append('tools/list')

            def call(self, command, parameters=None, timeout=300):
                self.sent.append(command)
                if command == 'entity.create':
                    return {'id': 'C4A7E'}
                if command == 'selection.set':
                    test.assertEqual(parameters, {'entities': ['C4A7E']})
                if command == 'editor.screenshot':
                    with open(test.real(parameters['path']), 'wb') as file:
                        file.write(grey_png(1280, 720))
                    return {'settled': True, 'width': 1280, 'height': 720}
                return {}

            def close(self):
                self.sent.append('close')
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', self.window_program(runs)), \
                mock.patch.object(editor, 'Program', Window), mock.patch.object(editor, 'McpClient', Agent), \
                mock.patch.dict(os.environ, {'STRATA_EDITOR_TOKEN': 'secret', 'STRATA_EDITOR_PORT': '1'}):
            code, output = quiet(figures.main, 'take', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build, '--work', self.work,
                                 '--kinds', 'editor')
        self.assertEqual(code, 0, output)
        # automation true: the window's script runs as before, but the editor serves automation.
        served = [arguments for arguments, _ in runs if 'core.time.served.json' in arguments[arguments.index('--commands') + 1]][0]
        self.assertNotIn('--no-automation', served)
        # An agent: the editor in a window serves without a script, and StrataCLI mcp, named claude-code, sends the steps
        # after the frames waited for, then the screenshot while it is connected, then editor.quit.
        (arguments, env), = programs
        self.assertNotIn('--no-automation', arguments)
        self.assertNotIn('--commands', arguments)
        self.assertEqual(arguments[arguments.index('--project') + 1], c_DriveRoot + os.path.join('Projects', 'Figures'))
        agent, = agents
        self.assertEqual((agent.client, agent.project), ('claude-code', c_DriveRoot + os.path.join('Projects', 'Figures')))
        self.assertEqual(agent.sent, ['initialize', 'tools/list', 'scene.loadStatus', 'scene.open', 'scene.loadStatus', 'editor.wait', 'entity.create',
                                      'selection.set', 'editor.screenshot', 'editor.quit', 'close'])
        # No token or port of the person's environment reaches the editor or the agent: the agent finds the editor
        # through the take's own session folder.
        for environment in (env, agent.env):
            self.assertNotIn('STRATA_EDITOR_TOKEN', environment)
            self.assertNotIn('STRATA_EDITOR_PORT', environment)
        self.assertEqual(env['STRATA_SESSION_DIR'], agent.env['STRATA_SESSION_DIR'])
        self.assertEqual(read_bytes(os.path.join(self.work, 'shots', 'core.time.agent.png')), grey_png(1280, 720))
        self.assertTrue(all(entry['released'] for entry in self.mappings))

    def test_runtime_figures_export_the_copy_and_run_the_game(self):
        with open(editor.program_path(self.build, 'StrataRuntime'), 'wb') as file:
            file.write(b'program')
        self.manifest(self.recipe(id='game', kind='runtime', shot=None, project={'template': 'basic3d'}, setup=[{'command': 'scene.save', 'parameters': {}}],
                                  runtime={'resolution': [64, 32], 'seconds': 2, 'quality': 'high'}),
                      self.recipe(id='wrong', kind='runtime', shot=None, project={'template': 'basic3d'},
                                  runtime={'resolution': [48, 32], 'seconds': 3, 'quality': 'low'}))

        class Exporting(FakeEditor):
            def call(self, command, parameters=None, timeout=300):
                if command == 'project.export':
                    FakeEditor.calls.append((command, parameters))
                    os.makedirs(parameters['directory'], exist_ok=True)
                    executable = os.path.join(parameters['directory'], 'Figures.exe')
                    with open(executable, 'wb') as file:
                        file.write(b'game')
                    return {'executable': executable, 'manifest': os.path.join(parameters['directory'], 'Figures.stgame')}
                return FakeEditor.call(self, command, parameters, timeout)
        games = []

        def program(arguments, env, log, name, timeout, cwd=None, merge=True):
            log.write(name, arguments, 'ran', 0)
            if arguments[0].endswith('Figures.exe'):
                games.append((arguments, cwd))
                # The game's window is 64 x 32 whatever it was asked for.
                with open(arguments[arguments.index('--screenshot') + 1], 'wb') as file:
                    file.write(grey_png(64, 32))
            return 0, 'ran\n', ''
        with mock.patch.object(editor, 'Editor', Exporting), mock.patch.object(editor, 'run_program', program):
            code, output = quiet(figures.main, 'take', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build, '--work', self.work,
                                 '--kinds', 'runtime')
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/wrong: the exported game\'s screenshot is 64x32, not '
                                 r'the window\'s 48x32: take a resolution the display holds$')
        commands = [command for command, _ in FakeEditor.calls]
        # Each figure gets a copy in a headless editor with the GPU, its setup steps, then the export.
        self.assertEqual(commands.count('project.create'), 2)
        self.assertLess(commands.index('scene.save'), commands.index('project.export'))
        exports = [parameters['directory'] for command, parameters in FakeEditor.calls if command == 'project.export']
        self.assertEqual(exports, [os.path.join(self.work, 'export', 'core.time.game'), os.path.join(self.work, 'export', 'core.time.wrong')])
        self.assertIn(True, FakeEditor.gpus)
        arguments, cwd = games[0]
        self.assertEqual(arguments, [os.path.join(exports[0], 'Figures.exe'), '--windowed', '--resolution', '64x32', '--seconds', '2', '--quality', 'high',
                                     '--save-directory', os.path.join(self.work, 'saves', 'core.time.game'), '--screenshot',
                                     os.path.join(self.work, 'log', 'core.time.game-runtime.png')])
        self.assertEqual(cwd, exports[0])
        self.assertEqual(read_bytes(os.path.join(self.work, 'shots', 'core.time.game.png')), grey_png(64, 32))
        with open(os.path.join(self.work, 'taken-pending.json'), encoding='utf-8') as file:
            self.assertEqual(json.load(file)['pictures']['core.time.game']['kind'], 'runtime')

    def test_live_figures_are_three_takes_in_editors_in_windows(self):
        self.manifest(self.recipe(id='turn', kind='live', shot=None, camera='scene', size=[32, 16], quality='medium', postProcess={'Bloom': False},
                                  play={'steps': 8, 'input': [{'step': 1, 'action': 'Look', 'mode': 'press', 'value': [1, 0]}]},
                                  live={'atFixedStep': 4, 'frames': 2}),
                      self.recipe(id='drift', kind='live', shot=None, camera='scene', size=[32, 16], play={'steps': 8}, live={'atFixedStep': 4, 'frames': 1}))
        windows = []

        class Live(FakeEditor):
            takes = 0

            def __init__(self, build, work, log, project=None, gpu=False, window=None):
                FakeEditor.__init__(self, build, work, log, project, gpu, window)
                if window:
                    windows.append((project, window, gpu))

            def start_call(self, command, parameters=None, timeout=300):
                FakeEditor.calls.append(('started ' + command, parameters))
                return parameters

            def finish_call(self, command, started, timeout=300):
                Live.takes += 1
                images = []
                for frame in range(started['frames']):
                    path = started['path'] if frame == 0 else '%s-%d.png' % (started['path'][:-4], frame + 1)
                    with open(path, 'wb') as file:
                        file.write(grey_png(32, 16, 100 + frame))
                    # The drifting figure reaches its step later at every take.
                    steps = started['atFixedStep'] + frame + (Live.takes if 'drift' in path else 0)
                    images.append({'fixedSteps': steps, 'temporalFrames': 8, 'width': 32, 'height': 16, 'path': path})
                return {'live': True, 'camera': 'scene', 'images': images}
        with mock.patch.object(editor, 'Editor', Live), mock.patch.object(editor, 'run_program', lambda *arguments, **named: (0, '', '')):
            code, output = quiet(figures.main, 'take', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build, '--work', self.work,
                                 '--kinds', 'live')
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/drift: the 3 live takes differ in their fixed steps or '
                                 r'camera \(take 1: \[\[5\], "scene"\]; take 2: \[\[6\], "scene"\]; take 3: \[\[7\], "scene"\]\): the figure is not repeatable')
        # Each take: a fresh copy, then an editor in a window around the Game view, on that copy, with the GPU.
        self.assertEqual(len(windows), 6)
        self.assertEqual(len({project for project, _, _ in windows}), 6)
        self.assertTrue(all(window['size'] == [32 + 480, 16 + 360] and gpu for _, window, gpu in windows))
        self.assertEqual([command for command, _ in FakeEditor.calls].count('project.openSample'), 6)
        calls = FakeEditor.calls
        # The first take of turn (drift's takes come first, in the order of their labels), at its quality preset.
        first = [index for index, (command, parameters) in enumerate(calls) if command == 'project.setSettings' and parameters['value'] == {'Preset': 'Medium'}][0]
        take = calls[first:[index for index, (command, _) in enumerate(calls) if command == 'play.stop' and index > first][0] + 1]
        self.assertEqual([command for command, _ in take], ['project.setSettings', 'graphics.resetPlayerOptions', 'editor.showPanel', 'viewport.setSettings',
                                                            'scene.open', 'scene.loadStatus', 'entity.find', 'component.set', 'play.start',
                                                            'started viewport.capture', 'input.sequence', 'play.stop'])
        self.assertEqual(take[0][1], {'section': 'Renderer.Quality', 'value': {'Preset': 'Medium'}})
        self.assertEqual(take[3][1], {'gameView': {'mode': 'custom', 'width': 32, 'height': 16}})
        self.assertEqual({key: value for key, value in take[9][1].items() if key != 'path'},
                         {'live': True, 'camera': 'scene', 'atFixedStep': 4, 'frames': 2, 'overwrite': True})
        self.assertEqual(take[10][1], {'events': [{'step': 1, 'action': 'Look', 'mode': 'press', 'value': [1, 0]}], 'steps': 8})
        # The first take's last frame is the original; every take's frames stay for the photographer.
        self.assertEqual(read_bytes(os.path.join(self.work, 'shots', 'core.time.turn.png')), grey_png(32, 16, 101))
        for number in (1, 2, 3):
            self.assertTrue(os.path.isfile(os.path.join(self.work, 'live', 'core.time.turn', 'take-%d' % number, 'frame-2.png')))
        self.assertFalse(os.path.exists(os.path.join(self.work, 'shots', 'core.time.drift.png')))

    def test_a_program_s_files_are_staged_in_a_run_folder_it_sees_as_a_drive_of_its_own(self):
        self.book.write('tutorials/core/time/FallTest.json', '[]\n')
        files = [{'from': 'book:tutorials/core/time/FallTest.json', 'to': 'FallTest.json'}]
        self.manifest(
            self.recipe(id='script', kind='text', shot=None, project=None, files=files,
                        text={'program': 'StrataEditor', 'arguments': ['--commands', 'FallTest.json'], 'redact': ['at [0-9]+']}),
            self.recipe(id='leaky', kind='text', shot=None, project=None, files=files, text={'program': 'StrataEditor', 'arguments': ['--leak']}),
            self.recipe(id='plain', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['--help']}))
        runs = []

        def program(arguments, env, log, name, timeout, cwd=None, merge=True):
            log.write(name, arguments, 'ran', 0)
            folder = self.real(cwd)
            runs.append((arguments, cwd, sorted(os.listdir(folder)) if cwd != self.build else None, env['STRATA_RECENT_PROJECTS']))
            if '--leak' in arguments:
                return 0, 'Opened project (%s)\n' % os.path.join(folder, 'FallTestProject'), ''
            if cwd == self.build:
                return 0, 'help\n', ''
            with open(os.path.join(folder, 'FallTest.json'), 'a', encoding='utf-8') as file:
                file.write('changed by the run\n')  # a run's changes stay in its own folder
            return 0, 'Command script finished in %s at %d\n' % (cwd, len(runs)), ''
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', program):
            code, output = quiet(figures.main, 'take', '--kinds', 'text', '--root', self.book.root, '--engine', self.engine.root,
                                 '--build', self.build, '--work', self.work)
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/leaky: the text names the work folder \(.+\): '
                                 r'give the program files and relative paths, or redact the path$')
        self.assertEqual(read_text(os.path.join(self.work, 'text', 'core.time.script.txt')), 'Command script finished in %s …\n' % c_DriveRoot)
        staged = [run for run in runs if run[0][1:] == ['--commands', 'FallTest.json']]
        # Each run gets a fresh copy of the files in a folder of its own, which it sees as the root of a drive.
        self.assertEqual([(cwd, listing) for _, cwd, listing, _ in staged], [(c_DriveRoot, ['Editor', 'FallTest.json'])] * 2)
        self.assertEqual({recent for _, _, _, recent in staged}, {c_DriveRoot + os.path.join('Editor', 'RecentProjects.json')})
        script_folders = [entry['folder'] for entry in self.mappings if 'core.time.script' in entry['folder']]
        self.assertEqual(len(set(script_folders)), 2)
        for folder in script_folders:
            self.assertEqual(read_text(os.path.join(folder, 'FallTest.json')), '[]\nchanged by the run\n')
        self.assertTrue(all(entry['released'] for entry in self.mappings))
        # A program without files runs in the build, as before.
        self.assertEqual([cwd for arguments, cwd, _, _ in runs if arguments[1:] == ['--help']], [self.build] * 2)

    def launcher_recipes(self):
        self.book.write('layouts/inspect.ini', '; Strata editor layout for a window of 1280x720 pixels at UI scale 1 (tools/figures.py layout)\n[Docking][Data]\n'
                        '\n[StrataLauncher][Settings]\nProjectLocation=C:\\Old\n\n[Window][Debug]\nPos=0,0\n')
        window = {'layout': 'layouts/inspect.ini', 'steps': [{'command': 'editor.showDialog', 'parameters': {'dialog': 'newProject'}}]}
        self.manifest(
            self.recipe(id='launcher', kind='editor', shot=None, project=None, editorWindow=dict(window, launcher=True)),
            self.recipe(id='export', kind='editor', shot=None, project={'sample': 'ThirdPerson'}, editorWindow=window),
            self.recipe(id='leaky', kind='editor', shot=None, project={'template': 'basic3d'}, editorWindow=window),
            self.recipe(id='homely', kind='editor', shot=None, project={'template': 'basic3d'}, editorWindow=window))

    def test_an_editor_figure_without_a_project_shows_the_launcher_and_windows_see_neutral_paths(self):
        self.launcher_recipes()
        home = os.path.join(os.path.dirname(self.work), 'Users', 'someone')
        runs, layouts, environments = [], {}, {}
        program = self.window_program(runs)

        def watching(arguments, env, log, name, timeout, cwd=None, merge=True):
            if '--window-size' not in arguments:
                return program(arguments, env, log, name, timeout, cwd, merge)
            stem = os.path.basename(arguments[arguments.index('--commands') + 1])[:-5]
            layouts[stem] = read_text(self.real(arguments[arguments.index('--layout') + 1]))
            environments[stem] = (env['STRATA_RECENT_PROJECTS'], env['STRATA_SCRIPT_BUILDS_DIR'])
            code, output, errors = program(arguments, env, log, name, timeout, cwd, merge)
            if stem == 'core.time.leaky':
                output += '\n[info] App: Opened project \'Figures\' (%s)\n' % self.real(arguments[arguments.index('--project') + 1]).replace('\\', '/')
            if stem == 'core.time.homely':
                output += '\n[warning] App: Could not read %s\n' % os.path.join(home, 'AppData', 'x.json')
            return code, output, errors
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', watching), \
                mock.patch.dict(os.environ, {'USERPROFILE': home, 'HOME': home}):
            code, output = quiet(figures.main, 'take', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build, '--work', self.work,
                                 '--kinds', 'editor')
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/leaky: the editor\'s log names the work folder '
                                 r'\(.+\) in "\[info\] App: Opened project \'Figures\' \(.+\)": the picture may show it; give the editor paths on its '
                                 r'drive \(plan/pipelines\.md §5\.4\)$')
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/homely: the editor\'s log names the user\'s home '
                                 r'folder \(.+\) in "\[warning\] App: Could not read .+": the picture may show it')
        self.assertFalse(os.path.exists(os.path.join(self.work, 'shots', 'core.time.leaky.png')))
        # The launcher: no project is made or opened, and its script only waits and takes the picture.
        arguments, script = [(arguments, script) for arguments, script in runs if 'core.time.launcher.json' in arguments[arguments.index('--commands') + 1]][0]
        self.assertNotIn('--project', arguments)
        self.assertEqual([step['command'] for step in script], ['editor.showDialog', 'editor.wait', 'editor.screenshot'])
        made = [command for command, _ in FakeEditor.calls if command in ('project.create', 'project.openSample')]
        self.assertEqual(made, ['project.openSample', 'project.create', 'project.create'])
        self.assertTrue(os.path.isfile(os.path.join(self.work, 'shots', 'core.time.launcher.png')))
        # The sample's copy is ThirdPerson in the drive's Projects folder, which the New Project and Open Sample dialogs
        # suggest; the layout's own remembered location is replaced.
        export = [arguments for arguments, _ in runs if 'core.time.export.json' in arguments[arguments.index('--commands') + 1]][0]
        self.assertEqual(export[export.index('--project') + 1], c_DriveRoot + os.path.join('Projects', 'ThirdPerson'))
        copied = [parameters['directory'] for command, parameters in FakeEditor.calls if command == 'project.openSample']
        self.assertEqual(copied, [os.path.join(self.mappings[0]['folder'], 'Projects', 'ThirdPerson')])
        for stem in ('core.time.launcher', 'core.time.export'):
            self.assertIn('[StrataLauncher][Settings]\nProjectLocation=%sProjects\n' % c_DriveRoot, layouts[stem])
            self.assertNotIn('C:\\Old', layouts[stem])
            self.assertIn('[Window][Debug]\nPos=0,0\n', layouts[stem])
            self.assertEqual(environments[stem], (c_DriveRoot + os.path.join('Editor', 'RecentProjects.json'), c_DriveRoot + os.path.join('Editor', 'ScriptBuilds')))
        launcher_folder = [entry['folder'] for entry in self.mappings if os.path.isfile(os.path.join(entry['folder'], 'Editor', 'core.time.launcher.json'))][0]
        self.assertEqual(os.listdir(os.path.join(launcher_folder, 'Projects')), [])
        self.assertTrue(all(entry['released'] for entry in self.mappings))

    def test_a_take_that_names_the_work_folder_or_the_home_in_its_stamp_or_recipe_fails(self):
        home = os.path.join(os.path.dirname(self.work), 'Users', 'someone')
        self.manifest(self.recipe(id='homely', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['--help']},
                                  caption='The help, as %s shows it.' % os.path.join(home, 'x')),
                      self.recipe(id='gpu', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['--help']}))

        class Revealing(FakeEditor):
            def check_commit(self, pin, provisional=False):
                return dict(FakeEditor.check_commit(self, pin, provisional), gpu='A GPU in %s' % os.path.join(home.replace('\\', '/'), 'gpu'))
        with mock.patch.dict(os.environ, {'USERPROFILE': home, 'HOME': home}), mock.patch.object(editor, 'Editor', Revealing), \
                mock.patch.object(editor, 'run_program', lambda arguments, env, log, name, timeout, cwd=None, merge=True: (0, 'help\n', '')):
            code, output = quiet(figures.main, 'take', '--kinds', 'text', '--root', self.book.root, '--engine', self.engine.root,
                                 '--build', self.build, '--work', self.work)
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/homely: the recipe names the user\'s home folder')
        self.assertRegex(output, r'(?m)^src/content/figures/core/time\.json:\d+: failed: core/time/gpu: the stamp names the user\'s home folder')

    def test_the_commit_check_of_a_provisional_build_reports_instead_of_stopping(self):
        session = editor.Editor(self.build, self.work, editor.Log(os.path.join(self.work, 'log')))
        answers = {'engine': {'engineCommit': 'abcdef123456', 'platform': 'Windows'}, 'editor': {'editor': {'gpu': {'name': 'GPU'}}}}
        session.call = lambda command, parameters=None, timeout=0: answers[parameters['sections'][0]]
        with self.assertRaises(editor.PreflightError):
            session.check_commit(self.pin)
        self.assertEqual(session.check_commit(self.pin, provisional=True),
                         {'engineCommit': 'abcdef123456', 'platform': 'Windows', 'gpu': 'GPU', 'provisional': True})

    def test_layout_makes_a_layout_file_for_a_window_size(self):
        runs = []
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', self.window_program(runs)):
            code, output = quiet(figures.main, 'layout', 'first-script', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build,
                                 '--work', self.work, '--window-size', '1280x720', '--provisional')
        self.assertEqual(code, 0, output)
        self.assertIn('figures: wrote layouts/first-script.ini (the editor\'s default layout for a window of 1280x720', output)
        self.assertEqual(self.book.read('layouts/first-script.ini'),
                         '; Strata editor layout for a window of 1280x720 pixels at UI scale 1 (tools/figures.py layout, engine abcdef123456)\n'
                         '[Docking][Data]\nDockSpace ID=0x8B93E3BD Window=0xA787BDB4 Pos=0,24 Size=1280,696\n')
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0][0][1:5], ['--window-size', '1280x720', '--ui-scale', '1'])
        self.assertEqual(runs[0][1], [{'command': 'editor.wait', 'parameters': {'frames': 120}}])
        self.assertIn(('project.create', {'directory': os.path.join(self.work, 'projects', '01'), 'name': 'Figures', 'template': 'basic3d'}), FakeEditor.calls)
        self.assertEqual(quiet(figures.main, 'layout', 'Bad Name', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build,
                               '--window-size', '1280x720')[0], 2)
        self.assertEqual(quiet(figures.main, 'layout', 'other', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build,
                               '--window-size', '100x100')[0], 2)

    def test_publish_text_and_fill_them_into_the_page(self):
        self.page('```text capture="help"\n```')
        self.manifest(self.recipe(id='help', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['--help']}))
        self.assertEqual(self.take('--kinds', 'text')[0], 0)
        code, output = quiet(figures.main, 'publish', '--from', self.work, '--root', self.book.root)
        self.assertEqual(code, 0, output)
        self.assertIn('published: help.txt', output)
        taken = json.loads(self.book.read('src/assets/figures/core/time/taken.json'))['files']['help.txt']
        self.assertEqual((taken['kind'], taken['encoder'], taken['pin']), ('text', None, self.pin))
        self.assertEqual(quiet(figures.main, 'fill', '--root', self.book.root)[0], 0)
        self.assertIn('```text capture="help"\nStrataCLI 0.7.0 - command-line client\n  call\n```', self.book.read('src/content/docs/core/time.md'))
        code, output = self.check('--release')
        self.assertEqual(code, 0, output)
        self.assertIn('unchanged: help.txt', quiet(figures.main, 'publish', '--from', self.work, '--root', self.book.root)[1])


class EditorCheckTests(FiguresTestCase):
    """check on editor figures: the panel a recipe pictures, its layout's window, and waitsFor kept until the pin has it."""

    def test_panels_layouts_and_waits_of_editor_figures(self):
        commands = [{'name': 'editor.showPanel', 'parameters': {'properties': {'panel': {'enum': ['Inspector', 'Console', 'Scene']}}}},
                    {'name': 'entity.create', 'parameters': {}}]
        self.book.write(self.dumps + '/commands.json', dump(self.pin, 'editor.commands', {'commands': commands}))
        self.book.write('layouts/small.ini', '; Strata editor layout for a window of 1280x720 pixels at UI scale 1 (tools/figures.py layout)\n[Docking][Data]\n')
        waits = 'tier 2: editor screenshot'
        self.page('::figure{id=good}\n\n::figure{id=bad-panel}\n\n::figure{id=bad-window}\n')
        self.manifest(
            self.recipe(id='good', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                        editorWindow={'layout': 'layouts/small.ini', 'panel': 'Console', 'steps': []}),
            self.recipe(id='bad-panel', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                        editorWindow={'layout': 'layouts/small.ini', 'panel': 'Toolbar', 'steps': []}),
            self.recipe(id='bad-window', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                        editorWindow={'layout': 'layouts/small.ini', 'windowSize': [1600, 900], 'steps': []}))
        code, errors = self.errors()
        self.assertEqual(code, 1, errors)
        self.assertEqual(len(errors), 2, errors)
        self.assertRegex(errors[0], r'^src/content/figures/core/time\.json:\d+: the panel Toolbar is not one editor\.showPanel names at the pin '
                                    r'\(Inspector, Console, Scene\): picture one of those, or the whole window$')
        self.assertRegex(errors[1], r'^src/content/figures/core/time\.json:\d+: the layout layouts/small\.ini was made for a window of 1280x720, not '
                                    r'1600x900: make a layout for that window \(figures\.py layout\), or set windowSize to 1280x720$')
        # A window size out of the editor's range is a schema error.
        self.manifest(self.recipe(id='good', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                                  editorWindow={'layout': 'layouts/small.ini', 'windowSize': [320, 200], 'steps': []}))
        self.page('::figure{id=good}\n')
        code, errors = self.errors()
        self.assertEqual(code, 1, errors)
        self.assertIn('windowSize', ' '.join(errors))
        # Once the pin has editor.screenshot, the wait is an error, as for every addition.
        commands.append({'name': 'editor.screenshot', 'parameters': {}})
        self.book.write(self.dumps + '/commands.json', dump(self.pin, 'editor.commands', {'commands': commands}))
        self.manifest(self.recipe(id='good', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits,
                                  editorWindow={'layout': 'layouts/small.ini', 'steps': []}))
        code, errors = self.errors()
        self.assertEqual(code, 1, errors)
        self.assertIn('tier 2: editor screenshot', ' '.join(errors))

    def test_a_missing_layout_fails_a_release_only_for_a_figure_a_take_makes(self):
        self.page('::figure{id=drawing}\n\n::figure{id=made}\n')
        self.manifest(
            self.recipe(id='blocked', kind='editor', shot=None, project={'template': 'basic3d'}, blocked='The pin has no wind zone.',
                        standIn='drawing', editorWindow={'layout': 'layouts/missing.ini', 'steps': []}),
            self.recipe(id='drawing', kind='diagram', shot=None, project=None),
            self.recipe(id='made', kind='editor', shot=None, project={'template': 'basic3d'}, editorWindow={'layout': 'layouts/absent.ini', 'steps': []}))
        code, output = self.check('--release')
        lines = [line for line in output.splitlines() if 'does not exist yet' in line]
        self.assertEqual(len(lines), 2, output)
        self.assertIn(': note: the layout layouts/missing.ini does not exist yet: the figure is blocked, so no take needs it at the pin', output)
        self.assertNotIn('note: the layout layouts/absent.ini', output)
        self.assertIn('the layout layouts/absent.ini does not exist yet', output)

    def test_files_are_book_files_that_land_inside_the_project(self):
        self.book.write('layouts/small.ini', '; Strata editor layout for a window of 1280x720 pixels at UI scale 1 (tools/figures.py layout)\n[Docking][Data]\n')
        self.book.write('tutorials/core/time/Coin.cpp', '// the coin\n')
        self.book.write('tutorials/core/time/Big.cpp', 'x' * 64)
        self.book.write('tutorials/core/time.tutorial.json', json.dumps({'page': 'core/time', 'startsFrom': {'template': 'basic3d'}, 'stages': [
            {'step': 1, 'files': [{'from': 'book:tutorials/core/time/Coin.cpp', 'to': 'Scripts/Coin.cpp'}]},
            {'step': 2, 'files': [{'from': 'book:tutorials/core/time/Gone.cpp', 'to': 'Scripts/Coin.cpp'}]}]}))
        waits = 'tier 2: editor screenshot'
        window = {'layout': 'layouts/small.ini', 'steps': [{'command': 'entity.create', 'parameters': {}}]}
        good = [{'stage': 1}, {'from': 'book:tutorials/core/time/Coin.cpp', 'to': 'Scripts/Other.cpp', 'atStep': 1}]
        self.page('::figure{id=good}\n\n::figure{id=bad}\n\n```text capture="help"\n```\n')
        self.manifest(
            self.recipe(id='good', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits, editorWindow=window, files=good),
            self.recipe(id='bad', kind='editor', shot=None, project={'template': 'basic3d'}, waitsFor=waits, editorWindow=window, play={'steps': 1}, files=[
                {'from': 'book:tutorials/core/time/Missing.cpp', 'to': 'Scripts/Missing.cpp'},
                {'from': 'book:src/content/docs/core/time.md', 'to': 'Scripts/Page.md'},
                {'from': 'book:tutorials/core/time/Coin.cpp', 'to': '../Coin.cpp'},
                {'from': 'book:tutorials/core/time/Coin.cpp', 'to': '.strata/Coin.cpp'},
                {'from': 'book:tutorials/core/time/Big.cpp', 'to': 'Scripts/Big.cpp'},
                {'stage': 2}, {'stage': 3},
                {'from': 'book:tutorials/core/time/Coin.cpp', 'to': 'Scripts/Late.cpp', 'atStep': 2}]),
            self.recipe(id='help', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['--help']}, files=good))
        with mock.patch.object(figures, 'c_ProjectFileLimit', 32):
            code, errors = self.errors()
        self.assertEqual(code, 1, errors)
        text = '\n'.join(errors)
        for expected in (
                r'the book has no file tutorials/core/time/Missing\.cpp: name a file of the book, or write it',
                r'"book:src/content/docs/core/time\.md" is not a file under tutorials/: copy a tutorial\'s files or assets \(book:tutorials/…\)',
                r'"\.\./Coin\.cpp" is outside the project \(or in its \.strata/\): give a path relative to the project, without "\.\.", such as '
                r'Scripts/Coin\.cpp',
                r'"\.strata/Coin\.cpp" is outside the project',
                r'tutorials/core/time/Big\.cpp has 64 bytes, more than the 32 a recipe copies into a project: copy a smaller file',
                r'stage 2 copies book:tutorials/core/time/Gone\.cpp: the book has no file tutorials/core/time/Gone\.cpp',
                r'stage 3: tutorials/core/time\.tutorial\.json has no stage 3 \(its stages: 1, 2\): name one of them',
                r'atStep 2: editorWindow\.steps holds 1 step: copy before one of them, or leave atStep out to copy before the editor opens the project',
                r'atStep closes the window before that step and opens it again on the copy, which ends play: leave play out, or copy before the '
                r'editor opens the project',
                r'atStep 1: a program\'s files are staged in its run folder before it starts: leave atStep out'):
            self.assertRegex(text, r'(?m)^src/content/figures/core/time\.json:\d+: ' + expected, text)
        self.assertEqual(len(errors), 10, errors)

    def test_program_files_relative_arguments_and_paths_of_the_machine(self):
        self.book.write('tutorials/core/time/FallTest.json', '[]\n')
        files = [{'from': 'book:tutorials/core/time/FallTest.json', 'to': 'FallTest.json'}]
        home = os.path.expanduser('~')
        self.page('```text capture="script"\n```\n\n```text capture="absolute"\n```\n\n```text capture="escapes"\n```\n\n```text capture="status"\n```\n\n'
                  '```text capture="build"\n```\n\n```text capture="homely"\n```\n')
        self.manifest(
            self.recipe(id='script', kind='text', shot=None, project=None, files=files, text={'program': 'StrataEditor', 'arguments': ['--commands', 'FallTest.json']}),
            self.recipe(id='absolute', kind='text', shot=None, project=None, text={'program': 'StrataEditor', 'arguments': ['--commands', 'C:/Work/FallTest.json']}),
            self.recipe(id='escapes', kind='text', shot=None, project=None, files=files, text={'program': 'StrataEditor', 'arguments': ['--commands', '../FallTest.json']}),
            self.recipe(id='status', kind='text', shot=None, project={'template': 'basic3d'}, files=files, text={'command': {'command': 'editor.status'}, 'keep': ['/scene']}),
            self.recipe(id='build', kind='text', shot=None, project=None, text={'program': 'ctest', 'arguments': ['--test-dir', '../..', '-N']}),
            self.recipe(id='homely', kind='text', shot=None, project=None, text={'program': 'StrataCLI', 'arguments': ['--help']},
                        alt='The help of the command-line client, from %s.' % os.path.join(home, 'Strata')))
        code, errors = self.errors()
        self.assertEqual(code, 1, errors)
        text = '\n'.join(errors)
        self.assertRegex(text, r'(?m)^src/content/figures/core/time\.json:\d+: the argument "C:/Work/FallTest\.json" is an absolute path, which names a folder '
                               r'of the machine the take runs on: stage the file with files and name it relative to the run folder$')
        self.assertRegex(text, r'(?m)^src/content/figures/core/time\.json:\d+: the argument "\.\./FallTest\.json" leaves the run folder the files are '
                               r'staged in: name a file the recipe stages$')
        self.assertRegex(text, r'(?m)^src/content/figures/core/time\.json:\d+: only editor, scene and program text figures copy files: remove files$')
        self.assertRegex(text, r'(?m)^src/content/figures/core/time\.json:\d+: the recipe names the user\'s home folder \(.+\): a picture never shows a '
                               r'path of the machine; name a folder of the project or the run folder$')
        self.assertEqual(len(errors), 4, errors)

    def test_launcher_figures_open_no_project(self):
        self.book.write('layouts/small.ini', '; Strata editor layout for a window of 1280x720 pixels at UI scale 1 (tools/figures.py layout)\n[Docking][Data]\n')
        launcher = {'layout': 'layouts/small.ini', 'launcher': True, 'steps': []}
        self.page('::figure{id=good}\n\n::figure{id=with-project}\n\n::figure{id=with-scene}\n\n::figure{id=no-project}\n')
        self.manifest(
            self.recipe(id='good', kind='editor', shot=None, project=None, editorWindow=launcher),
            self.recipe(id='with-project', kind='editor', shot=None, project={'template': 'basic3d'}, editorWindow=launcher),
            self.recipe(id='with-scene', kind='editor', shot=None, project=None, editorWindow=launcher, scene='Scenes/Main.stscene', play={'steps': 1},
                        setup=[{'command': 'entity.create', 'parameters': {}}]),
            self.recipe(id='no-project', kind='editor', shot=None, project=None, editorWindow={'layout': 'layouts/small.ini', 'steps': []}))
        code, errors = self.errors()
        self.assertEqual(code, 1, errors)
        text = '\n'.join(errors)
        self.assertRegex(text, r'(?m)^src/content/figures/core/time\.json:\d+: the launcher shows while no project is open: remove project, or '
                               r'editorWindow\.launcher$')
        for field in ('scene', 'play', 'setup'):
            self.assertRegex(text, r'(?m)^src/content/figures/core/time\.json:\d+: a figure of the launcher opens no project, so it takes no %s: '
                                   r'remove %s$' % (field, field))
        self.assertRegex(text, r'(?m)^src/content/figures/core/time\.json:\d+: a editor figure runs an editor on a project: add project \(or '
                               r'editorWindow\.launcher: true for the launcher\)$')
        self.assertEqual(len(errors), 5, errors)


class PublishTests(FiguresTestCase):
    """publish, archive and compare on a take written by hand, with the stand-in encoder."""

    def setUp(self):
        super().setUp()
        self.work = tempfile.mkdtemp(prefix='take-')
        self.patcher = mock.patch.object(figures, 'encoder_command', lambda: [sys.executable, c_Fake])
        self.patcher.start()
        self.page('::compare{id=pair}\n\n::figure{id=shot}\n\n::figure{id=shot crop=middle}')
        self.manifest(self.recipe(shot=None, camera='scene', size=[40, 20], crops=[{'name': 'middle', 'rect': [0.25, 0.25, 0.75, 0.75], 'scale': 2}]),
                      self.recipe(id='pair', shot=None, camera='scene', size=[40, 20], variants={'off': {}, 'on': {}}))

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.work, ignore_errors=True)
        super().tearDown()

    def write_take(self, grey=128, corrupt=None, pin=None, recorded=None):
        if os.path.isdir(self.work):
            shutil.rmtree(self.work)
        for folder in ('shots', 'crops', 'results', 'text'):
            os.makedirs(os.path.join(self.work, folder))
        pictures = {}
        def add(stem, figure, variant, crop, width, height, folder):
            data = grey_png(width, height, grey)
            with open(os.path.join(self.work, folder, stem + '.png'), 'wb') as file:
                file.write(data if stem != corrupt else b'other')
            pictures[stem] = {'page': 'core/time', 'figure': figure, 'variant': variant, 'crop': crop, 'kind': 'scene', 'sha256': hashlib.sha256(data).hexdigest(),
                              'pin': pin or self.pin, 'build': None, 'reportedCommit': (pin or self.pin)[:12], 'os': 'Windows', 'gpu': 'A GPU',
                              'size': [width, height], 'recorded': recorded or {'draws': 3}, 'pairDifference': {'pixels': 2, 'percent': 0.25, 'largest': 1} if stem == 'core.time.shot' else None,
                              'renderer': {'DitherOutput': False} if stem == 'core.time.pair.off' else None}
        add('core.time.shot', 'shot', None, None, 40, 20, 'shots')
        add('core.time.shot-middle', 'shot', None, 'middle', 20, 10, 'crops')
        add('core.time.pair.off', 'pair', 'off', None, 40, 20, 'shots')
        add('core.time.pair.on', 'pair', 'on', None, 40, 20, 'shots')
        with open(os.path.join(self.work, 'results', 'core.time.shot.json'), 'w', encoding='utf-8') as file:
            json.dump({'Image': {'Data': 'AAAA'}, 'renderStats': {'draws': 3}}, file)
        with open(os.path.join(self.work, 'taken-pending.json'), 'w', encoding='utf-8') as file:
            json.dump({'pin': pin or self.pin, 'pictures': pictures}, file)

    def publish(self, *extra):
        return quiet(figures.main, 'publish', '--from', self.work, '--root', self.book.root, *extra)

    def test_publish_encodes_stamps_keeps_originals_and_judges_retakes(self):
        self.write_take()
        code, output = self.publish()
        self.assertEqual(code, 0, output)
        folder = self.book.path('src/assets/figures/core/time')
        self.assertEqual(sorted(os.listdir(folder)), ['pair-off.avif', 'pair-on.avif', 'shot-middle.webp', 'shot.avif', 'shot.result.json', 'taken.json'])
        taken = json.loads(self.book.read('src/assets/figures/core/time/taken.json'))['files']
        self.assertEqual(taken['shot.avif']['encoder']['quality'], 80)
        self.assertEqual(taken['pair-off.avif']['encoder']['quality'], 90)
        self.assertTrue(taken['shot-middle.webp']['encoder']['lossless'])
        self.assertEqual(taken['shot.avif']['recorded'], {'draws': 3})
        # A pair within R57's rule: the stamp records how its two captures differed; an identical pair records nothing.
        self.assertEqual(taken['shot.avif']['pairDifference'], {'pixels': 2, 'percent': 0.25, 'largest': 1})
        self.assertNotIn('pairDifference', taken['pair-off.avif'])
        # The renderer switches a capture drew with are stamped; a picture drawn without them has none.
        self.assertEqual(taken['pair-off.avif']['renderer'], {'DitherOutput': False})
        self.assertNotIn('renderer', taken['pair-on.avif'])
        self.assertEqual(json.loads(self.book.read('src/assets/figures/core/time/shot.result.json')), {'renderStats': {'draws': 3}})
        for record in taken.values():
            self.assertTrue(os.path.isfile(self.book.path('originals/%s.png' % record['original'])))
        code, output = self.check('--release')
        self.assertEqual(code, 0, output)
        # The same originals change nothing.
        self.assertIn('figures: 0 published, 4 unchanged', self.publish()[1])
        # A retake below the thresholds keeps the file and records the commit it was checked at.
        self.write_take(grey=130)
        code, output = self.publish()
        self.assertIn('checked: shot.avif (mean 0.200, largest block 0.20)', output)
        self.assertEqual(json.loads(self.book.read('src/assets/figures/core/time/taken.json'))['files']['shot.avif']['checkedAt'], [self.pin])
        # Above them it is a candidate until the photographer accepts it.
        self.write_take(grey=200)
        code, output = self.publish()
        self.assertIn('candidates: shot.avif (mean 7.200, largest block 7.20): judge it, then publish with --accept --figures core/time/shot', output)
        self.assertTrue(os.path.isfile(os.path.join(self.work, 'candidates', 'core', 'time', 'shot.avif')))
        before = json.loads(self.book.read('src/assets/figures/core/time/taken.json'))['files']['shot.avif']['original']
        code, output = self.publish('--accept', '--figures', 'core/time/shot')
        self.assertIn('published: shot.avif', output)
        self.assertNotIn('pair', output.replace('figures:', ''))
        after = json.loads(self.book.read('src/assets/figures/core/time/taken.json'))['files']['shot.avif']['original']
        self.assertNotEqual(before, after)

    def test_an_equal_retake_at_another_pin_restamps_the_file_it_keeps(self):
        self.write_take()
        self.assertEqual(self.publish()[0], 0)
        before = json.loads(self.book.read('src/assets/figures/core/time/taken.json'))['files']
        published = {name: read_bytes(self.book.path('src/assets/figures/core/time/' + name)) for name in before}
        moved = 'b' * 40
        self.write_take(pin=moved, recorded={'draws': 4})
        code, output = self.publish()
        self.assertEqual(code, 0, output)
        self.assertIn('restamped: shot.avif (the same original, taken at %s)' % moved[:12], output)
        self.assertIn('figures: 0 published, 0 unchanged, 4 restamped, 0 checked', output)
        after = json.loads(self.book.read('src/assets/figures/core/time/taken.json'))['files']
        self.assertEqual(sorted(after), sorted(before))
        for name, record in after.items():
            # The stamp says at which pin the take was made and what it measured; the file and its hashes stay.
            self.assertEqual((record['pin'], record['reportedCommit']), (moved, moved[:12]))
            self.assertEqual({key: record[key] for key in ('original', 'sha256', 'encoder', 'size')},
                             {key: before[name][key] for key in ('original', 'sha256', 'encoder', 'size')})
            self.assertEqual(read_bytes(self.book.path('src/assets/figures/core/time/' + name)), published[name])
        self.assertEqual(after['shot.avif']['recorded'], {'draws': 4})
        self.assertEqual(after['shot.avif']['pairDifference'], {'pixels': 2, 'percent': 0.25, 'largest': 1})
        self.assertEqual(after['pair-off.avif']['renderer'], {'DitherOutput': False})
        # The same take again changes nothing.
        self.assertIn('figures: 0 published, 4 unchanged, 0 restamped', self.publish()[1])

    def test_publish_leaves_out_the_pictures_and_crops_no_page_places(self):
        self.page('::figure{id=pair variant=off}\n\n::figure{id=shot}')
        self.write_take()
        code, output = self.publish()
        self.assertEqual(code, 0, output)
        self.assertIn('skipped: shot-middle.webp: no page places the crop middle of shot', output)
        self.assertIn('skipped: pair-on.avif: no page places the variant on of pair', output)
        self.assertFalse(os.path.isfile(self.book.path('src/assets/figures/core/time/pair-on.avif')))
        # A variant published before its page stopped placing it is an error of check, its capture result too.
        self.book.write('src/assets/figures/core/time/pair-on.result.json', '{}')
        self.assertIn('src/assets/figures/core/time/pair-on.result.json: no page places the variant on of pair (::figure{id=pair variant=on}): '
                      'remove the file, or place the picture', '\n'.join(self.errors()[1]))
        os.remove(self.book.path('src/assets/figures/core/time/pair-on.result.json'))
        self.assertNotIn('shot-middle.webp', json.loads(self.book.read('src/assets/figures/core/time/taken.json'))['files'])
        self.assertFalse(os.path.isfile(self.book.path('src/assets/figures/core/time/shot-middle.webp')))
        code, output = self.check()
        self.assertNotIn('shot-middle', output)

    def test_publish_fails_on_missing_or_changed_originals(self):
        self.write_take(corrupt='core.time.pair.on')
        os.remove(os.path.join(self.work, 'shots', 'core.time.pair.off.png'))
        code, output = self.publish()
        self.assertEqual(code, 1)
        self.assertIn('core.time.pair.off: the original is missing', output)
        self.assertIn('core.time.pair.on: the original differs from taken-pending.json', output)
        self.assertEqual(quiet(figures.main, 'publish', '--from', self.book.root, '--root', self.book.root)[0], 2)

    def test_archive_packs_every_original_a_stamp_names(self):
        self.write_take()
        self.publish()
        code, output = quiet(figures.main, 'archive', '--tag', 'book-v0.8.1', '--root', self.book.root)
        self.assertEqual(code, 0, output)
        with tarfile.open(self.book.path('release/strata-engine-docs-originals-book-v0.8.1.tar')) as tar:
            names = sorted(tar.getnames())
        taken = json.loads(self.book.read('src/assets/figures/core/time/taken.json'))['files']
        self.assertEqual(names, sorted({'originals/%s.png' % record['original'] for record in taken.values()}))
        archive = self.book.path('release/strata-engine-docs-originals-book-v0.8.1.tar')
        with open(archive, 'rb') as file:
            digest = hashlib.sha256(file.read()).hexdigest()
        self.assertEqual(self.book.read('release/strata-engine-docs-originals-book-v0.8.1.tar.sha256'),
                         '%s  strata-engine-docs-originals-book-v0.8.1.tar\n' % digest)
        with mock.patch.object(figures, 'c_ArchiveLimit', 10):
            self.assertIn('more than the archive\'s 1 GB', quiet(figures.main, 'archive', '--tag', 'x', '--root', self.book.root)[1])
        os.remove(self.book.path('originals/%s.png' % taken['shot.avif']['original']))
        code, output = quiet(figures.main, 'archive', '--tag', 'book-v0.8.1', '--root', self.book.root)
        self.assertEqual(code, 1)
        self.assertIn('is missing (a stamp names it)', output)
        self.assertEqual(quiet(figures.main, 'archive', '--tag', '../x', '--root', self.book.root)[0], 2)

    def test_compare_lays_out_the_originals_beside_the_take(self):
        self.write_take()
        self.publish()
        output_folder = tempfile.mkdtemp(prefix='compare-')
        try:
            code, output = quiet(figures.main, 'compare', '--after', self.work, '--output', output_folder, '--engine', self.engine.root, '--root', self.book.root)
            self.assertEqual(code, 0, output)
            self.assertIn('compared 4 originals with the take', output)
            with open(os.path.join(output_folder, 'report.txt'), encoding='utf-8') as file:
                self.assertEqual(file.read(), 'core.time.pair.off.png core.time.pair.on.png core.time.shot.png')
            code, output = quiet(figures.main, 'compare', '--after', self.work, '--output', self.book.path('src/out'), '--engine', self.engine.root, '--root', self.book.root)
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(output_folder, ignore_errors=True)

    def test_list_names_each_file_s_state(self):
        self.write_take()
        self.publish()
        os.remove(self.book.path('src/assets/figures/core/time/pair-on.avif'))
        code, output = quiet(figures.main, 'list', '--root', self.book.root)
        self.assertIn('core/time\tshot\tscene\tshot-middle.webp taken, shot.avif taken', output)
        self.assertIn('core/time\tpair\tscene\tpair-off.avif taken, pair-on.avif missing', output)


class McpClientTests(unittest.TestCase):
    """booklib.editor.McpClient against a stand-in StrataCLI mcp (fixtures/figures/fake_mcp.py)."""

    def test_the_agent_names_itself_reaches_the_editor_and_sends_commands_without_a_token(self):
        folder = tempfile.mkdtemp(prefix='mcp-')
        self.addCleanup(shutil.rmtree, folder, True)
        log = editor.Log(os.path.join(folder, 'log'))
        with mock.patch.dict(os.environ, {'STRATA_EDITOR_TOKEN': 'secret-token', 'STRATA_EDITOR_PORT': '4711'}):
            env = editor.environment(folder, folder, editor.new_session_dir())
        client = editor.McpClient(folder, env, log, 'claude-code', project='S:\\Projects\\Figures',
                                  program=[sys.executable, '-I', os.path.join(helpers.c_Fixtures, 'figures', 'fake_mcp.py')])
        try:
            client.initialize()
            client.wait_for_editor(30)
            answer = client.call('scene.open', {'scene': 'Scenes/Main.stscene'})
            self.assertEqual((answer['method'], answer['params'], answer['client']), ('scene.open', {'scene': 'Scenes/Main.stscene'}, 'claude-code'))
            self.assertEqual(answer['arguments'], ['mcp', '--project', 'S:\\Projects\\Figures', '--timeout', '300000'])
            self.assertFalse(answer['token'])
            with self.assertRaises(editor.CommandError) as caught:
                client.call('broken', {})
            self.assertIn('broken failed (through StrataCLI mcp): Error -32000: the command failed', str(caught.exception))
        finally:
            client.close()
        self.assertIsNotNone(client.process.returncode)
        for name in os.listdir(log.folder):
            with open(os.path.join(log.folder, name), encoding='utf-8', errors='replace') as file:
                self.assertNotIn('secret-token', file.read())


@unittest.skipUnless(shutil.which('node') and os.path.isdir(os.path.join(c_Root, 'node_modules', 'sharp')), 'node or the pinned sharp is not installed (source .tools/env.sh)')
class EncoderScriptTests(unittest.TestCase):
    """scripts/encode-figures.mjs with the pinned sharp."""

    def run_script(self, *arguments):
        result = subprocess.run([shutil.which('node'), figures.c_Encoder] + list(arguments), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=c_Root)
        return result.returncode, result.stdout.decode('utf-8'), result.stderr.decode('utf-8')

    def test_one_format_per_picture_and_the_difference_of_two(self):
        folder = tempfile.mkdtemp(prefix='encode-')
        try:
            png = os.path.join(folder, 'a.png')
            image = images.Image(64, 32, 3, bytearray((x * 4) & 255 for x in range(64 * 32 * 3)))
            with open(png, 'wb') as file:
                file.write(images.png_bytes(image))
            code, output, errors = self.run_script('encode', '--publish', 'lossy', png, os.path.join(folder, 'a.avif'))
            self.assertEqual(code, 0, errors)
            settings = json.loads(output)
            self.assertEqual({key: settings[key] for key in ('format', 'quality', 'chromaSubsampling', 'effort', 'lossless')},
                             {'format': 'avif', 'quality': 80, 'chromaSubsampling': '4:4:4', 'effort': 4, 'lossless': False})
            self.assertEqual(settings['sharp'], '0.35.5')
            data = read_bytes(os.path.join(folder, 'a.avif'))
            self.assertEqual((images.format_of(data), images.size_of(data)), ('avif', (64, 32)))
            code, output, errors = self.run_script('encode', '--publish', 'lossless', png, os.path.join(folder, 'a.webp'))
            self.assertEqual(code, 0, errors)
            data = read_bytes(os.path.join(folder, 'a.webp'))
            self.assertTrue(images.webp_is_lossless(data))
            self.assertEqual(images.size_of(data), (64, 32))
            code, output, errors = self.run_script('diff', os.path.join(folder, 'a.webp'), os.path.join(folder, 'a.webp'))
            self.assertEqual(json.loads(output)['mean'], 0)
            code, output, errors = self.run_script('diff', os.path.join(folder, 'a.webp'), os.path.join(folder, 'a.avif'))
            difference = json.loads(output)
            self.assertGreater(difference['mean'], 0)
            self.assertGreaterEqual(difference['largestBlockMean'], difference['mean'])
            self.assertEqual(self.run_script('encode', '--publish', 'lossy', png, os.path.join(folder, 'a.webp'))[0], 2)
            self.assertEqual(self.run_script('encode', '--publish', 'lossless', '--quality', '80', png, os.path.join(folder, 'b.webp'))[0], 2)
            self.assertEqual(self.run_script('encode', '--publish', 'lossy', os.path.join(folder, 'a.webp'), os.path.join(folder, 'c.avif'))[0], 1)
        finally:
            shutil.rmtree(folder, ignore_errors=True)


@unittest.skipUnless(shutil.which('node') and os.path.isdir(os.path.join(c_Root, 'node_modules', 'playwright')), 'node or the pinned Playwright is not installed (source .tools/env.sh)')
class ScreenshotScriptTests(unittest.TestCase):
    def test_a_page_s_picture_at_its_size(self):
        folder = tempfile.mkdtemp(prefix='page-')
        try:
            page = os.path.join(folder, 'page.html')
            with open(page, 'w', encoding='utf-8') as file:
                file.write('<!doctype html><title>x</title><body style="background:#123456;margin:0"><p>A tool page.</p></body>')
            url = 'file:///' + page.replace(os.sep, '/').lstrip('/')
            target = os.path.join(folder, 'page.png')
            result = subprocess.run([shutil.which('node'), figures.c_Screenshot, url, target, '--size', '320x200'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=c_Root)
            self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
            picture = images.read_png(read_bytes(target))
            self.assertEqual((picture.width, picture.height), (320, 200))
            self.assertEqual(bytes(picture.data[(199 * 320 + 319) * picture.channels:][:3]), bytes([0x12, 0x34, 0x56]))
            usage = subprocess.run([shutil.which('node'), figures.c_Screenshot, url, os.path.join(folder, 'x.jpg')], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=c_Root)
            self.assertEqual(usage.returncode, 2)
        finally:
            shutil.rmtree(folder, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
