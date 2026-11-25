"""tools/names.py: the names lint of plan/pipelines.md §8 on pages of a small book, against a small engine repository and
the dumps of fixtures/names/dumps.json; and the generated block of _typos.toml (rulings 5, R17)."""

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import names

c_Engine = {
    'CMakeLists.txt': 'project(Strata)\n',
    'Strata/src/Strata/Scene/Scene.h': 'namespace Strata\n{\n\tclass Scene\n\t{\n\tpublic:\n\t\tAssetManager& GetAssetManager();\n\t\tvoid Update();\n'
                                       '\t\tvoid UpdateRuntime();\n\t};\n}\n',
    'Strata/src/Strata/Renderer/Renderer.cpp': 'void Renderer::PrepareBackBuffer() {}\nvoid Scene::UpdateRuntime() {}\n',
    'Tools/LookDev.py': 'print("look")\n',
    'Samples/Tetris/Assets/Block.png': 'png\n',
    'Samples/Coins/Assets/Coin.png': 'png\n',
}

c_GoodPage = '''
Run `editor.status`, `editor.status {sections: ["engine"]}` and
`viewport.capture {width: 640, debugView: "lod", camera: scene, gameView: {mode: "fixed"}, height: …}`.
Set `Transform.Rotation`, `AntiAliasingMethod = TAA`, `AntiAliasing = true` and `Intensity = 3`.
The sections `Renderer.Quality`, `Renderer.Quality.Preset` and `Editor.ExternalEditor`; the suites `Architecture.Layering`
and `Editor.UI.Dialogs`; the test `StrataTests.FeatureTest`.
The macros `ST_CORE_ASSERT(condition, "message")` and `ST_PROFILE_FUNCTION`.
The names `Scene::GetAssetManager`, `Renderer::PrepareBackBuffer()`, `Scene::Update`, `Strata::Scene` and `Toy::Step`.
The programs `StrataEditor --no-gpu --project <dir>`, `StrataCLI launch --no-gpu --idle-timeout 900` and `StrataRuntime --windowed`.
The files `Strata/src/Strata/Scene/Scene.h`, `Strata/src/Strata/Scene/Scene.h:6-7`, `Strata/src/Strata/Scene`, `Tools/LookDev.py`,
`CMakeLists.txt`, `Samples/*/Assets/`, `Strata/vendor/glm`, `Strata/vendor/glm/glm/vec3.hpp` and `Strata/vendor/glm/glm`.
Not names of the engine: `project.json`, `index.md`, `std::vector<int>` in a sketch, `x = 1`.
Choose **File ▸ New Project...**.

## Add the component

1. Open the **Inspector**, click **Add Component** and choose **Post Process**. Press **Ctrl+B** or **F5**. The **scenes**
   are terms.

   **You should see:** the component.

   **If you do not see it:** try again.

```json
[{"command": "scene.open", "parameters": {"scene": "Scenes/Main.stscene"}}, {"command": "play.step", "parameters": {"steps": 60}}]
```

## Check yourself

1. Is **anything bold** here a step? No: questions are not steps.
'''

# The misspelt names are put together at run time, so that the repository's spelling gate passes this file.
c_BadPage = '''
`editor.stat`
`editor.status {sections: ["engines"]}`
`viewport.capture {@WIDTH@: 640}`
`viewport.capture {gameView: {mode: "loose"}}`
`viewport.capture {width 640}`
`Transform.@ROTATION@`
`AntiAliasingMethod = SMAA`
`AntiAliasing = yes`
`Bogus = 1`
`Renderer.Qualty`
`Renderer.Quality.Presett`
`ST_NOPE`
`Scene::Nope`
`StrataEditor --gpu`
`StrataCLI lunch --project x`
`Strata/src/Missing.h`
`Strata/vendor/glm/glm/nope.hpp`
**File ▸ Nope**

1. Click **Nope Button**.

```json
{"command": "scene.close", "parameters": {}}
```
'''.replace('@WIDTH@', 'wid' + 'ht').replace('@ROTATION@', 'Rota' + 'ton')


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = function(list(arguments))
    return code, output.getvalue()


class NamesTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = helpers.TempEngine()
        self.pin = self.engine.commit(c_Engine)
        # A vendor library: its own repository inside the clone, as git submodule update makes it.
        vendor = os.path.join(self.engine.root, 'Strata', 'vendor', 'glm')
        os.makedirs(os.path.join(vendor, 'glm'))
        with open(os.path.join(vendor, 'glm', 'vec3.hpp'), 'w', encoding='utf-8', newline='\n') as file:
            file.write('struct vec3 {};\n')
        for arguments in (['init', '-q'], ['config', 'user.email', 'test@example.com'], ['config', 'user.name', 'Test'],
                          ['config', 'commit.gpgsign', 'false'], ['add', '-A'], ['commit', '-q', '-m', 'glm']):
            subprocess.run(['git', '-C', vendor] + arguments, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.glm = subprocess.run(['git', '-C', vendor, 'rev-parse', 'HEAD'], check=True, stdout=subprocess.PIPE).stdout.decode().strip()
        self.book = helpers.TempBook(self.pin)
        self.book.write('src/content/glossary.json', json.dumps({'terms': [{'id': 'scene', 'term': 'scene', 'definition': 'A world.', 'home': 'core/map'}]}))
        self.book.write('sketches/core-time-toy.cpp', 'struct Toy\n{\n\tvoid Step();\n};\n')
        self.write_dumps()

    def tearDown(self):
        self.book.cleanup()
        self.engine.cleanup()

    def write_dumps(self, change=None):
        with open(os.path.join(helpers.c_Fixtures, 'names', 'dumps.json'), encoding='utf-8') as file:
            files = json.load(file)['files']
        for name, data in files.items():
            text = json.dumps(data).replace('@PIN12@', self.pin[:12]).replace('@PIN@', self.pin).replace('@GLM@', self.glm)
            if change:
                text = change(name, text)
            if text is not None:
                self.book.write('reference/_dumps/%s/%s' % (self.pin, name), text)
        self.dumps = self.book.path('reference/_dumps/%s' % self.pin)

    def lint(self, *extra):
        return quiet(names.main, 'check', '--root', self.book.root, '--dumps', self.dumps, '--engine', self.engine.root, *extra)


class CheckTests(NamesTestCase):
    def test_every_form_of_a_good_page_passes(self):
        self.book.page('core/time', helpers.frontmatter(kind='how-to') + c_GoodPage)
        code, output = self.lint()
        self.assertEqual(code, 0, output)
        self.assertIn('names: 0 findings', output)

    def test_every_form_of_a_bad_page_is_found_with_its_line(self):
        self.book.page('core/time', helpers.frontmatter(kind='tutorial') + c_BadPage)
        code, output = self.lint('core/time')
        self.assertEqual(code, 1, output)
        page = 'src/content/docs/core/time.md'
        expected = [
            '%s:19: command: editor.stat: no registered command has this name (did you mean `editor.status`?)' % page,
            '%s:20: command parameters: editor.status: sections[0] is "engines"; its values are "engine", "editor"' % page,
            '%s:21: command parameters: viewport.capture: the command has no parameter "@WIDTH@" (did you mean `width`?)' % page,
            '%s:22: command parameters: viewport.capture: gameView.mode is "loose"; its values are "free", "fixed"' % page,
            '%s:23: command parameters: viewport.capture {width 640}: the parameters are not an object' % page,
            '%s:24: component property: Transform.@ROTATION@: component Transform has no property @ROTATION@ (did you mean `Rotation`?)' % page,
            '%s:25: property value: AntiAliasingMethod = SMAA: PostProcess.AntiAliasingMethod is one of FXAA, TAA, Morphological' % page,
            '%s:26: property value: AntiAliasing = yes: PostProcess.AntiAliasing is true or false' % page,
            '%s:27: property value: Bogus: no component has this property' % page,
            '%s:28: section or test: Renderer.Qualty: neither a settings or preferences section' % page,
            '%s:29: section field or test: Renderer.Quality.Presett: section Renderer.Quality has no field Presett (did you mean `Preset`?)' % page,
            '%s:30: macro: ST_NOPE: no #define or CMake compile definition at the pin defines it' % page,
            '%s:31: scope name: Scene::Nope: no file at the pin contains it' % page,
            '%s:32: program option: StrataEditor --gpu: not an option of StrataEditor' % page,
            '%s:33: program option: StrataCLI lunch: StrataCLI has no command "lunch"; its commands are call, launch' % page,
            '%s:34: engine path: Strata/src/Missing.h: no file or folder at the pin has this path' % page,
            '%s:35: engine path: Strata/vendor/glm/glm/nope.hpp: no file or folder of Strata/vendor/glm at the commit the pin records' % page,
            '%s:36: menu path: File ▸ Nope: "Nope" is no UI name of the editor at the pin' % page,
            '%s:38: UI name: Nope Button: a bold span in a step names a UI label' % page,
            '%s:41: command step: scene.close: no registered command has this name' % page,
        ]
        expected = [line.replace('@WIDTH@', 'wid' + 'ht').replace('@ROTATION@', 'Rota' + 'ton') for line in expected]
        for line in expected:
            self.assertIn(line, output)
        self.assertIn('names: 20 findings', output)

    def test_scope_names_of_the_page_s_own_sketches_only(self):
        self.book.page('core/time', helpers.frontmatter() + '\n`Toy::Step`\n')
        self.book.page('core/map', helpers.frontmatter(id='core/map') + '\n`Toy::Step`\n')
        code, output = self.lint()
        self.assertEqual(code, 1, output)
        self.assertIn('src/content/docs/core/map.md:19: scope name: Toy::Step', output)
        self.assertNotIn('core/time.md:19', output)

    def test_a_name_hidden_inside_a_longer_one_is_found(self):
        # "Scene::Update" stands alone only in Scene.h's declaration, which a batched search reports as the longer
        # "Scene::UpdateRuntime" in Renderer.cpp; the lint asks again for each miss.
        self.book.page('core/time', helpers.frontmatter() + '\n`Scene::UpdateRuntime` and `Scene::Update`\n')
        self.assertEqual(self.lint()[0], 0)

    def test_a_macro_prefix_names_the_family_of_macros_it_starts(self):
        # `ST_WITH_` followed by a module (basics/cpp-modern): a name that ends with "_" is the start of the macros of a
        # family, and passes when a macro at the pin starts with it.
        self.book.page('core/time', helpers.frontmatter() + '\nThe family `ST_PROFILE_`.\n\nThe family `ST_NOPE_`.\n')
        code, output = self.lint()
        self.assertEqual(code, 1, output)
        self.assertNotIn('ST_PROFILE_:', output)
        self.assertIn('macro: ST_NOPE_: no macro at the pin starts with it', output)

    def test_frame_profiler_stages_are_names_of_the_pin(self):
        # `GPU.AO` and `Scene.Physics` are stages of the frame profiler (parsed/frame-stages.json), neither a section nor a
        # test: the lint refused them on wave 5's pages. `World.Streaming` is a stage and `World.Coordinates` a doctest
        # suite although World is a component. A stage the pin lacks is still found, and so is a component's property the
        # pin lacks.
        self.book.page('core/time', helpers.frontmatter() + '\nThe stages `GPU.AO`, `Scene.Physics`, `Render.Extract` and '
                       '`World.Streaming`, the suite `World.Coordinates`; not `GPU.Nope` or `World.Nope`.\n')
        code, output = self.lint()
        self.assertEqual(code, 1, output)
        for name in ('GPU.AO', 'Scene.Physics', 'Render.Extract', 'World.Streaming', 'World.Coordinates'):
            self.assertNotIn(name + ':', output)
        self.assertIn('section or test: GPU.Nope: neither a settings or preferences section, a doctest suite, a CTest name nor a '
                      'frame profiler stage', output)
        self.assertIn('component property: World.Nope: component World has no property Nope', output)

    def test_icon_labels_and_component_categories_are_ui_names(self):
        # The Create menu draws "{}  Mesh only" with an icon in front, and Add Component groups the components under
        # their categories (Core, World): the lint refused **Mesh only** and **Core** on make/scenes-entities.
        def change(name, text):
            if name == 'parsed/ui-literals.json':
                return text.replace('"Play"', '"Play", "{}  Mesh only", "{}  {}"')
            return text
        self.write_dumps(change)
        self.book.page('make/levels', helpers.frontmatter(id='make/levels', kind='how-to') + '\n## Make it\n\n1. Choose '
                       '**Mesh only**, then **Core** and **World**; not **Mesh** or **{}**.\n')
        code, output = self.lint()
        self.assertEqual(code, 1, output)
        for name in ('Mesh only', 'Core', 'World'):
            self.assertNotIn('UI name: %s:' % name, output)
        self.assertIn('UI name: Mesh:', output)

    def test_names_of_the_page_s_notes_are_allowed_on_that_page_only(self):
        # Names the reader makes up (a stage Game.MyWork) or that the page's own patch adds (a suite Physics.WindZone)
        # are not the pin's; the page's notes list them with a reason, and only that page may write them.
        text = helpers.frontmatter() + '\nThe stage `Game.MyWork` and the suite `Physics.WindZone`; not `GPU.Nope`.\n'
        self.book.page('core/time', text)
        self.book.page('core/map', text)
        self.book.write('plan/notes/core/time.md', '# Notes: core/time\n\n## Names of this page\n\n'
                        '- `Game.MyWork`: a stage name the reader makes up in exercise 2.\n'
                        '- `Physics.WindZone`: the suite the page\'s own patch adds.\n- `GPU.Nope`\n')
        code, output = self.lint()
        self.assertEqual(code, 1, output)
        time = [line for line in output.split('\n') if 'core/time.md' in line]
        self.assertFalse(any('Game.MyWork' in line or 'Physics.WindZone' in line for line in time), output)
        self.assertTrue(any('GPU.Nope' in line for line in time), output)
        self.assertIn('core/map.md', output)
        self.assertTrue(any('core/map.md' in line and 'Game.MyWork' in line for line in output.split('\n')), output)

    def test_a_missing_table_is_a_note_and_with_release_an_error(self):
        self.write_dumps(lambda name, text: None if name == 'parsed/macros.json' else text)
        os.remove(os.path.join(self.dumps, 'parsed', 'macros.json'))
        self.book.page('core/time', helpers.frontmatter() + '\n`ST_CORE_ASSERT`\n')
        code, output = self.lint()
        self.assertEqual(code, 0, output)
        self.assertIn('names: macros cannot be checked: the dumps lack parsed/macros.json; run python -I tools/reference.py dump and parse '
                      'at the pin (note)', output)
        code, output = self.lint('--release')
        self.assertEqual(code, 1, output)

    def test_dumps_of_another_pin_and_a_clone_without_the_pin_stop_the_run(self):
        self.book.page('core/time', helpers.frontmatter() + '\nText.\n')
        self.write_dumps(lambda name, text: text.replace(self.pin, '1' * 40) if name == 'commands.json' else text)
        code, output = self.lint()
        self.assertEqual(code, 2, output)
        self.assertIn('holds the names of pin 1111111111111111111111111111111111111111, but engine.pin names', output)
        self.write_dumps()
        other = helpers.TempEngine()
        try:
            other.commit({'a.txt': 'a\n'})
            code, output = quiet(names.main, 'check', '--root', self.book.root, '--dumps', self.dumps, '--engine', other.root)
            self.assertEqual(code, 2, output)
            self.assertIn('pipelines.md §1.4, check 1', output)
        finally:
            other.cleanup()
        self.assertEqual(quiet(names.main, 'check', '--root', self.book.root, '--dumps', self.dumps)[0], 2)
        self.assertEqual(self.lint('core/none')[0], 2)

    def test_a_since_older_than_the_files_it_names_is_a_warning(self):
        page = helpers.frontmatter(since='0.3.0') + '\nText.\n\n## Where it lives in Strata\n\n- `Strata/src/Strata/Light/AreaLight.h`\n'
        self.book.page('core/time', page.replace('Light/AreaLight.h', 'Scene/Scene.h'))
        code, output = self.lint()
        self.assertEqual(code, 0, output)
        self.assertIn('the clone has no tag v0.7.0', output)
        # The files at v0.7.0, then a pin that adds the area light.
        self.engine.git('tag', 'v0.7.0')
        self.pin = self.engine.commit({'Strata/src/Strata/Light/AreaLight.h': 'class AreaLight {};\n'})
        self.book.write('engine.pin', 'commit %s\nrelease 0.8.0\nprerelease yes\nrepository https://github.com/2042Third/GameEngine\n' % self.pin)
        self.write_dumps(lambda name, text: text.replace('"Tools/LookDev.py"', '"Tools/LookDev.py", "Strata/src/Strata/Light/AreaLight.h"')
                         if name == 'parsed/paths.json' else text)
        self.book.page('core/time', page)
        code, output = self.lint()
        self.assertEqual(code, 0, output)
        self.assertIn('src/content/docs/core/time.md:23: since: 0.3.0: every file "## Where it lives in Strata" names is absent at v0.7.0, so '
                      'the subject looks new in 0.8.0: write since: 0.8.0, or name the files it had before (warning)', output)
        self.book.page('core/time', page.replace('since: 0.3.0', 'since: 0.8.0'))
        self.assertNotIn('(warning)', self.lint()[1])
        self.book.page('core/time', page + '- `Strata/src/Strata/Scene/Scene.h`\n')
        self.assertNotIn('(warning)', self.lint()[1])

    def test_the_relaxed_parameters(self):
        self.assertEqual(names.parse_parameters('{a: 1, "b": [x, \'y\'], c, d: {e: …}}'),
                         {'a': 1, 'b': ['x', 'y'], 'c': Ellipsis, 'd': {'e': Ellipsis}})
        for text in ('{a 1}', '{a: 1', '[1]', '{a: 1} x'):
            with self.assertRaises(ValueError):
                names.parse_parameters(text)


class SpellingTests(unittest.TestCase):
    def test_the_block_is_appended_to_the_table_and_replaced_later(self):
        text = '[files]\nextend-exclude = []\n\n[default.extend-words]\n# Engine names.\nNVRHI = "NVRHI"\n'
        written = names.spelling_text(text, {'lod', 'nvrhi', 'ssr'})
        self.assertEqual(written, '[files]\nextend-exclude = []\n\n[default.extend-words]\n# Engine names.\nNVRHI = "NVRHI"\n'
                         + names.c_BlockStart + '\nlod = "lod"\nssr = "ssr"\n' + names.c_BlockEnd + '\n')
        again = names.spelling_text(written + '\n', {'gi'})
        self.assertIn(names.c_BlockStart + '\ngi = "gi"\n' + names.c_BlockEnd + '\n\n', again)
        self.assertNotIn('lod', again)

    def test_the_block_needs_its_table(self):
        with self.assertRaises(names.UsageError):
            names.spelling_text('[default.extend-words]\n\n[files]\nx = []\n', {'lod'})
        with self.assertRaises(names.UsageError):
            names.spelling_text(names.c_BlockEnd + '\n' + names.c_BlockStart + '\n', {'lod'})


c_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SpellingWordsTests(NamesTestCase):
    @unittest.skipUnless(names.find_typos(c_Root), 'needs typos (python tools/bootstrap.py downloads it into .tools/)')
    def test_the_words_typos_flags_from_page_ids_and_engine_names(self):
        shutil.copytree(helpers.c_OutlineFixture, self.book.path('plan'))
        typos = names.find_typos(c_Root)  # the small book has no .tools/ of its own
        layout = names.repo.Layout(self.book.root)
        folder = self.book.path('spelling')
        os.makedirs(folder)
        words = names.spelling_words(layout, self.book.path('plan'), None, helpers.c_TestBook)
        self.assertIn('ecs', words)
        self.assertEqual(names.flagged_words(typos, words, folder), set())
        words = names.spelling_words(layout, self.book.path('plan'), self.dumps, helpers.c_TestBook)
        self.assertIn('LodSelection', words)
        self.assertIn('lod', names.flagged_words(typos, words, folder))


if __name__ == '__main__':
    unittest.main()
