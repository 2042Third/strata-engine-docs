"""tools/tutorials.py (plan/pipelines.md §6) on a small book and a small engine: check, compile, run (with a stand-in
editor and a stand-in engine runner) and patch (with real git apply on the small engine and stand-ins for CMake, the
tests and CTest)."""

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import helpers  # noqa: E402
import tutorials  # noqa: E402
from booklib import editor  # noqa: E402
from booklib import tutorials as tutorial_files  # noqa: E402

c_Fixture = os.path.join(helpers.c_Fixtures, 'tutorials')
c_Greeter = os.path.join(c_Fixture, 'greeter')
c_FoxRow = ('| `Assets/Models/Fox.glb` | https://example.com/fox | A. Author | CC-BY-4.0 | Fox by A. Author (CC BY 4.0) | none |')
c_Patch = '''diff --git a/Strata/src/Strata/World/Wind.h b/Strata/src/Strata/World/Wind.h
--- a/Strata/src/Strata/World/Wind.h
+++ b/Strata/src/Strata/World/Wind.h
@@ -1,2 +1,3 @@
 #pragma once
 struct Wind {};
+struct WindZone {};
diff --git a/StrataTests/src/World/WindTests.cpp b/StrataTests/src/World/WindTests.cpp
--- a/StrataTests/src/World/WindTests.cpp
+++ b/StrataTests/src/World/WindTests.cpp
@@ -1 +1,2 @@
 // tests
+TEST_SUITE("World.WindZone") {}
'''
c_AddingPatch = '''diff --git a/Strata/src/Strata/World/Gust.h b/Strata/src/Strata/World/Gust.h
new file mode 100644
--- /dev/null
+++ b/Strata/src/Strata/World/Gust.h
@@ -0,0 +1 @@
+#pragma once
'''
c_EditorPatch = '''diff --git a/StrataEditor/src/Panel.cpp b/StrataEditor/src/Panel.cpp
--- a/StrataEditor/src/Panel.cpp
+++ b/StrataEditor/src/Panel.cpp
@@ -1 +1,2 @@
 // panel
+// more
'''


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = function(list(arguments))
    return code, output.getvalue()


def read_json(path):
    with open(path, encoding='utf-8') as file:
        return json.load(file)


class TutorialsTestCase(unittest.TestCase):
    """A book with the fixture tutorial test/greeter and an engine whose pin has a sample with a CC BY file."""

    def setUp(self):
        self.engine = helpers.TempEngine()
        self.pin = self.engine.commit({
            '.gitignore': 'build/\n',
            'Samples/ThirdPerson/CREDITS.md': '# Credits\n\n| Files | Source | Author | License | Attribution | Changes |\n'
                                              '| --- | --- | --- | --- | --- | --- |\n' + c_FoxRow + '\n',
            'Samples/ThirdPerson/Assets/Models/Fox.glb': 'fox model',
            'Strata/src/Strata/World/Wind.h': '#pragma once\nstruct Wind {};\n',
            'StrataTests/src/World/WindTests.cpp': '// tests\n',
            'StrataEditor/src/Panel.cpp': '// panel\n',
        })
        self.book = helpers.TempBook(pin_commit=self.pin)
        shutil.copytree(c_Greeter, self.book.root, dirs_exist_ok=True)
        with open(os.path.join(c_Fixture, 'dumps.json'), encoding='utf-8') as file:
            text = file.read().replace('@PIN12@', self.pin[:12]).replace('@PIN@', self.pin)
        data = json.loads(text)
        self.dumps = os.path.join(self.book.root, 'reference', '_dumps', self.pin)
        self.book.write('reference/_dumps/%s/commands.json' % self.pin, json.dumps(data['commands']))
        self.book.write('reference/_dumps/%s/samples.json' % self.pin, json.dumps(data['samples']))
        self.book.write('reference/_dumps/%s/parsed/tests.json' % self.pin, json.dumps(data['tests']))

    def tearDown(self):
        self.book.cleanup()
        self.engine.cleanup()

    def tutorial(self, page='test/greeter'):
        return json.loads(self.book.read('tutorials/%s.tutorial.json' % page))

    def write_tutorial(self, data, page='test/greeter'):
        self.book.write('tutorials/%s.tutorial.json' % page, json.dumps(data, indent='\t') + '\n')

    def check(self, *extra):
        return quiet(tutorials.main, 'check', '--root', self.book.root, '--dumps', self.dumps, '--engine', self.engine.root, *extra)

    def assertCheck(self, text, *extra):
        code, output = self.check(*extra)
        self.assertEqual(code, 1, output)
        self.assertIn(text, output)
        return output


class CheckTests(TutorialsTestCase):
    def test_the_part_assets_has_tutorials_beside_the_import_files(self):
        # tutorials/assets/ holds the tutorials' import files and the part assets' tutorials: only the import files
        # are skipped, so a page or exercise tutorial of the part is found.
        data = self.tutorial()
        for page in ('assets/extending', 'assets/extending/exercise-1', 'assets/robustness/exercise-3'):
            self.write_tutorial(data, page)
        self.book.write('tutorials/assets/Textures/rock.tutorial.json', '{}')
        self.book.write('tutorials/assets/rock.png', 'rock')
        found = [tutorial.relative for tutorial in tutorial_files.find_tutorials(tutorials.repo.Layout(self.book.root))]
        self.assertEqual([name for name in found if name.startswith('tutorials/assets/')],
                         ['tutorials/assets/extending.tutorial.json', 'tutorials/assets/extending/exercise-1.tutorial.json',
                          'tutorials/assets/robustness/exercise-3.tutorial.json'])

    def test_the_fixture_tutorial_passes_with_what_a_draft_may_lack(self):
        code, output = self.check()
        self.assertEqual(code, 0, output)
        self.assertIn('tutorials/test/greeter.tutorial.json:5: note: public/downloads/tutorials/test/greeter/stage-1.commands.json is '
                      'not written yet: run python -I tools/tutorials.py compile', output)
        self.assertIn('note: tutorials/test/greeter.stamp.json does not exist', output)
        self.assertIn('tutorials: 0 errors, 5 notes', output)
        # A release refuses what a draft may lack.
        code, output = self.check('--release')
        self.assertEqual(code, 1, output)
        self.assertIn('tutorials: 5 errors, 0 notes (release)', output)

    def test_the_schema_and_the_page_name_the_line(self):
        data = self.tutorial()
        data['stages'][0]['speed'] = 2
        self.write_tutorial(data)
        output = self.assertCheck('/stages/0/speed is not a known field: write the tutorial as plan/pipelines.md §6.2 gives its keys and forms')
        self.assertRegex(output, r'tutorials/test/greeter\.tutorial\.json:\d+: /stages/0/speed')
        self.book.write('tutorials/test/greeter.tutorial.json', '{"page": "test/greeter",\n "startsFrom": }')
        self.assertCheck('tutorials/test/greeter.tutorial.json:2: not valid JSON')
        self.write_tutorial(dict(read_json(os.path.join(c_Greeter, 'tutorials', 'test', 'greeter.tutorial.json')), page='test/other'))
        self.assertCheck('"page" is "test/other", but the file is the tutorial of test/greeter: name the page the file belongs to')

    def test_a_how_to_s_tutorial_file_ends_in_its_end_state(self):
        # plan/site.md: a how-to of make that changes Coin Run has no checkpoint; the build draws the downloads of its tutorial
        # file's last stage, which has endState, at the end of "## Result" (rulings-9.md, R40 and R42).
        self.book.write('src/content/docs/test/howto.md', '---\nkind: how-to\n---\n\n## Steps\n\n## Result\n')
        data = dict(self.tutorial(), page='test/howto')
        self.write_tutorial(data, 'test/howto')
        _, output = self.check()
        self.assertNotIn('the last stage of a how-to', output)
        del data['stages'][-1]['endState']
        self.write_tutorial(data, 'test/howto')
        self.assertCheck('the last stage of a how-to\'s tutorial file is its end state, which the build offers as a download at the end of '
                         '"## Result" (plan/site.md): give stage 2 "endState": true')

    def test_a_tutorial_page_needs_its_file_and_its_checkpoints_match_the_stages(self):
        self.book.write('src/content/docs/test/lonely.md', '---\nkind: tutorial\n---\n\n## What you will make\n')
        self.assertCheck('src/content/docs/test/lonely.md:1: a tutorial page needs its tutorial file tutorials/test/lonely.tutorial.json')
        self.book.remove('src/content/docs/test/lonely.md')
        page = self.book.read('src/content/docs/test/greeter.md').replace('::checkpoint{stage=2}', '::checkpoint{stage=3}')
        self.book.write('src/content/docs/test/greeter.md', page)
        self.assertCheck('src/content/docs/test/greeter.md:16: the page\'s checkpoints are stages 1, 3, but tutorials/test/greeter.tutorial.json '
                         'has the stages 1, 2: end each step section with ::checkpoint{stage=N} of its stage')
        self.book.write('src/content/docs/test/greeter.md', page.replace('stage=3', 'stage=2'))
        data = self.tutorial()
        data['stages'][1]['step'] = 3
        self.write_tutorial(data)
        self.assertCheck('stage 2 of the file has step 3: number the stages 1, 2, 3 in page order')
        # Each checkpoint offers the project after its stage, so each stage of a tutorial page is an end state.
        data['stages'][1]['step'] = 2
        del data['stages'][1]['endState']
        self.write_tutorial(data)
        output = self.assertCheck('stage 2 has no "endState": true, but its checkpoint offers the project as it is after the stage as a '
                                  'download (style.md §7.4): give the stage "endState": true')
        self.assertRegex(output, r'tutorials/test/greeter\.tutorial\.json:72: stage 2 has no "endState"')
        data['startsFrom'] = {'sample': 'Showcase'}
        self.write_tutorial(data)
        _, output = self.check()
        self.assertNotIn('"endState"', output)  # the reader of a tutorial that starts from a sample has the project
        self.book.remove('src/content/docs/test/greeter.md')
        self.assertCheck('the page test/greeter does not exist (src/content/docs/test/greeter.md): write the page, or name its id')

    def test_starts_from_a_sample_of_the_dumps_or_a_tutorial_without_a_loop(self):
        data = self.tutorial()
        data['startsFrom'] = {'sample': 'Nowhere'}
        self.write_tutorial(data)
        self.assertCheck('startsFrom names the sample "Nowhere", which project.samples does not list at the pin: name one of Showcase')
        data['startsFrom'] = {'tutorial': 'test/missing'}
        self.write_tutorial(data)
        self.assertCheck('startsFrom names the tutorial test/missing, which does not exist: write tutorials/test/missing.tutorial.json')
        other = {'page': 'test/other', 'startsFrom': {'tutorial': 'test/greeter'}, 'stages': [{'step': 1}]}
        self.book.write('src/content/docs/test/other.md', '---\nkind: how-to\n---\n')
        self.write_tutorial(other, 'test/other')
        data['startsFrom'] = {'tutorial': 'test/other'}
        self.write_tutorial(data)
        self.assertCheck('startsFrom makes a loop (test/greeter -> test/other -> test/greeter): start one of them from a template or a sample')
        data['startsFrom'] = {'pin': True}
        self.write_tutorial(data)
        self.assertCheck('startsFrom {"pin": true} is for tutorials that change the engine')

    def test_the_files_a_stage_copies(self):
        data = self.tutorial()
        files = data['stages'][1]['files']
        files.append({'from': 'book:sketches/core-time-x.cpp', 'to': 'Scripts/X.cpp'})
        files.append({'from': 'book:tutorials/test/greeter/Missing.cpp', 'to': 'Scripts/Missing.cpp'})
        files.append({'from': 'Samples/ThirdPerson/Assets/Models/Fox.glb', 'to': '../Fox.glb'})
        files.append({'from': 'Samples/ThirdPerson/Assets/Models/Wolf.glb', 'to': 'Assets/Wolf.glb'})
        files.append({'from': 'Strata/src/Strata/World/Wind.h', 'to': 'Assets/Wind.h'})
        files.append({'from': 'book:tutorials/assets/rock.png', 'to': 'Assets/rock.png'})
        self.book.write('tutorials/assets/rock.png', 'rock')
        self.write_tutorial(data)
        output = self.assertCheck('book:sketches/core-time-x.cpp is neither a file of the tutorial\'s own folder tutorials/test/greeter/ nor '
                                  'of tutorials/assets/: move it there')
        self.assertIn('tutorials/test/greeter/Missing.cpp does not exist: write the file, or correct the path', output)
        self.assertIn('"../Fox.glb" is outside the project (or in its .strata/)', output)
        self.assertIn('the engine has no file Samples/ThirdPerson/Assets/Models/Wolf.glb at the pin', output)
        self.assertIn('"Strata/src/Strata/World/Wind.h" is neither book:tutorials/… nor a file under Samples/<sample>/Assets/ at the pin', output)
        self.assertIn('tutorials/assets/rock.png has no row in tutorials/assets/CREDITS.md: credit it there', output)
        self.book.write('tutorials/assets/CREDITS.md', '| Files | Source | Author | License | Attribution | Changes |\n| --- | --- | --- | --- | --- | --- |\n'
                        '| `rock.png` | https://example.com | B. Author | CC0-1.0 | | none |\n')
        self.assertNotIn('rock.png has no row', self.check()[1])
        # Every page names the file it imports (plan/pipelines.md §6.2): a reader drags it into the Content Browser.
        data['stages'][1]['setup'] = [{'command': 'asset.import', 'parameters': {'file': '@BOOK@/tutorials/assets/rock.png',
                                                                                 'directories': ['@BOOK@/tutorials/assets/']}}]
        self.write_tutorial(data)
        output = self.assertCheck('src/content/docs/test/greeter.md does not name rock.png, which this step imports: name the file where '
                                  'the page has the reader import it (plan/pipelines.md §6.2)')
        self.assertRegex(output, r'tutorials/test/greeter\.tutorial\.json:\d+: src/content/docs/test/greeter\.md does not name rock\.png')
        self.assertIn('does not name assets, which this step imports', output)
        page = self.book.path('src/content/docs/test/greeter.md')
        with open(page, encoding='utf-8') as file:
            text = file.read()
        self.book.write('src/content/docs/test/greeter.md', text + '\nDrag rock.png, then the folder assets, into the Content Browser.\n')
        self.assertNotIn('does not name', self.check()[1])
        # An engine file needs the engine: without --engine the check cannot run.
        code, output = quiet(tutorials.main, 'check', '--root', self.book.root, '--dumps', self.dumps)
        self.assertEqual(code, 2, output)
        self.assertIn('copies Samples/ThirdPerson/Assets/Models/Fox.glb from the engine: pass --engine <the pin clone>', output)

    def test_commands_against_the_dumps_and_the_step_rules(self):
        data = self.tutorial()
        commands = data['stages'][1]['commands']
        commands += [
            {'command': 'entity.vanish'},
            {'command': 'editor.wait', 'parameters': {'frames': 10}},
            {'command': 'play.step', 'parameters': {'steps': 'many'}},
            {'command': 'component.get', 'parameters': {'entity': {'$ref': 'nobody'}, 'component': 'Transform'}},
            {'command': 'play.step', 'until': {'steps': 5}, 'expect': {'/stepsRun': {'min': 1}}},
            {'command': 'play.state', 'until': {'steps': 5}},
            {'command': 'play.start', 'entityName': 'Cube'},
            {'command': 'preferences.set', 'parameters': {'section': 'Editor.Theme', 'value': {}}},
            {'command': 'script.build', 'expect': {'success': {'equals': True}}},
            {'command': 'entity.create', 'parameters': {'name': '@PROJECT@'}},
            {'command': 'entity.create', 'parameters': {'name': 'C:/Games/cube'}},
            {'command': 'script.add', 'entityName': 'Cube', 'parameters': {'entity': '1', 'class': 'Greeter'}},
        ]
        data['stages'][1]['setup'] = [{'command': 'entity.create', 'parameters': {'name': 'Early'}},
                                      {'command': 'asset.import', 'parameters': {'file': '@ENGINE@/x.png'}},
                                      {'command': 'asset.import', 'parameters': {'file': 'D:/x.png'}}]
        self.write_tutorial(data)
        output = self.assertCheck('the commands dump at the pin has no command entity.vanish')
        for text in ('editor.wait counts frames, which differ from machine to machine: count game time in fixed steps',
                     'parameters/steps of play.step must be of type integer',
                     '$ref "nobody" names no value an earlier step of this stage binds',
                     'until repeats a query, and play.step is a command of kind Session',
                     'until repeats the step until its expect holds: give it an expect',
                     'play.start takes no "entity", and entityName passes the entity it finds as "entity"',
                     'preferences.set changes the person\'s preferences, which no tool does',
                     'expect: "success" is not a JSON pointer',
                     '@PROJECT@ in commands: placeholders belong in setup (asset.import)',
                     '"C:/Games/cube" is an absolute path in commands',
                     'the step names its entity twice: keep entityName and drop "entity"',
                     'setup holds only asset.import, the one step that needs an absolute path: move entity.create into commands',
                     '@ENGINE@ is no placeholder of the runner: use @PROJECT@, @BOOK@, @WORK@ or @RELEASE@',
                     '"D:/x.png" is an absolute path of one machine: start it with @BOOK@'):
            self.assertIn(text, output)
        # JSON pointers in expect, bind and checks are no absolute paths, and $ref may stand for any value.
        self.assertNotIn('"/success" is an absolute path', output)
        self.assertNotIn('/values/Rotation/1', output)
        self.assertNotIn('parameters/entity of component.get', output)

    def append_to_page(self, text):
        page = self.book.path('src/content/docs/test/greeter.md')
        with open(page, encoding='utf-8') as file:
            self.book.write('src/content/docs/test/greeter.md', file.read() + '\n' + text + '\n')

    def test_the_release_folder_placeholder(self):
        # A page has the reader import a file of the release's Samples/ folder; setup and the command that imports it name
        # the release's folder @RELEASE@, and the reader's copy writes it as pages write it for a reader.
        self.append_to_page('Import Fox.glb from the Samples folder of the release.')
        fox = '@RELEASE@/Samples/ThirdPerson/Assets/Models/Fox.glb'
        data = self.tutorial()
        data['stages'][1]['setup'] = [{'command': 'asset.import', 'parameters': {'file': fox}}]
        data['stages'][1]['commands'].insert(0, {'command': 'asset.import', 'parameters': {'files': [fox], 'directory': 'Models'}})
        self.write_tutorial(data)
        quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        code, output = self.check()
        self.assertEqual(code, 0, output)
        script = read_json(self.book.path('public/downloads/tutorials/test/greeter/stage-2.commands.json'))
        self.assertEqual(script[0]['parameters']['files'], ['<release folder>/Samples/ThirdPerson/Assets/Models/Fox.glb'])
        data['stages'][1]['commands'][1:1] = [
            {'command': 'asset.import', 'parameters': {'file': '@RELEASE@/Samples/ThirdPerson/Assets/Models/Wolf.glb'}},
            {'command': 'asset.import', 'parameters': {'file': '@RELEASE@/StrataEditor.exe'}},
            {'command': 'entity.create', 'parameters': {'name': '@RELEASE@/Cube'}},
            {'command': 'asset.import', 'parameters': {'file': '@BOOK@/tutorials/test/greeter/Greeter.cpp'}}]
        data['stages'][1]['setup'].append({'command': 'asset.import', 'parameters': {'directories': ['@RELEASE@/Samples/ThirdPerson/Assets/Sounds']}})
        self.write_tutorial(data)
        output = self.assertCheck('the release has no file Samples/ThirdPerson/Assets/Models/Wolf.glb at the pin: name a file of '
                                  'Samples/<sample>/Assets/ there')
        self.assertIn('the release has no folder Samples/ThirdPerson/Assets/Sounds at the pin', output)
        self.assertIn('"@RELEASE@/StrataEditor.exe" is no path under the release\'s Samples/<sample>/Assets/: import the release\'s sample '
                      'assets as @RELEASE@/Samples/<sample>/Assets/…', output)
        self.assertIn('@RELEASE@ in commands stands only at the start of a file or folder that asset.import imports from the release', output)
        self.assertIn('@BOOK@ in commands: placeholders belong in setup (asset.import)', output)
        self.assertIn('src/content/docs/test/greeter.md does not name Wolf.glb, which this step imports', output)

    def test_the_files_a_command_copies(self):
        data = self.tutorial()
        data['stages'][1]['commands'].insert(1, {'command': 'script.build', 'files': [
            {'from': 'book:tutorials/test/greeter/Missing.cpp', 'to': '../X.cpp'}]})
        data['stages'][0]['commands'].append({'command': 'component.get', 'parameters': {'entity': {'$ref': 'cube'}, 'component': 'Transform'},
                                              'files': [{'from': 'book:tutorials/test/greeter/Greeter.cpp', 'to': 'Scripts/Greeter.cpp'}]})
        self.write_tutorial(data)
        output = self.assertCheck('tutorials/test/greeter/Missing.cpp does not exist: write the file, or correct the path')
        self.assertIn('"../X.cpp" is outside the project (or in its .strata/)', output)
        self.assertIn('$ref "cube" names a value bound before a command that carries files: the reader\'s copy runs the commands between '
                      'such commands in runs of their own, which keep no bindings: bind it again after the files', output)

    def test_a_batch_refers_to_its_own_bindings(self):
        data = self.tutorial()
        data['stages'][0]['commands'].append({'command': 'editor.batch', 'parameters': {'steps': [
            {'command': 'entity.create', 'bind': {'made': '/id'}},
            {'command': 'component.get', 'parameters': {'entity': {'$ref': 'made'}, 'component': 'Transform'}},
            {'command': 'component.get', 'parameters': {'entity': {'$ref': 'cube'}, 'component': 'Transform'}}]}})
        self.write_tutorial(data)
        output = self.assertCheck('$ref "cube" names no value an earlier step of this editor.batch binds')
        self.assertNotIn('$ref "made"', output)

    def test_a_patch_tutorial(self):
        self.book.write('src/content/docs/world/tutorial-component.md', '---\nkind: tutorial\n---\n')
        patch = {'page': 'world/tutorial-component', 'startsFrom': {'pin': True},
                 'patch': {'file': 'tutorials/world/tutorial-component.patch', 'tests': ['World.WindZone', 'World.ECS', 'World.Gone']}}
        self.write_tutorial(patch, 'world/tutorial-component')
        output = self.assertCheck('tutorials/world/tutorial-component.patch does not exist: write the change as git diff writes it')
        self.book.write('tutorials/world/tutorial-component.patch', c_Patch)
        output = self.assertCheck('the doctest suite World.Gone is neither one of the pin\'s tests')
        self.assertNotIn('World.WindZone is neither', output)
        self.assertNotIn('World.ECS is neither', output)
        patch['stages'] = [{'step': 1}]
        patch['patch']['file'] = 'tutorials/world/other.patch'
        self.write_tutorial(patch, 'world/tutorial-component')
        output = self.assertCheck('a tutorial that changes the engine has no stages')
        self.assertIn('the patch of world/tutorial-component is tutorials/world/other.patch: name it tutorials/world/tutorial-component.patch', output)
        # An editor tutorial cannot start from one that changes the engine, which the pin build lacks.
        del patch['stages']
        patch['patch'] = {'file': 'tutorials/world/tutorial-component.patch', 'tests': []}
        self.write_tutorial(patch, 'world/tutorial-component')
        data = self.tutorial()
        data['startsFrom'] = {'tutorial': 'world/tutorial-component'}
        self.write_tutorial(data)
        self.assertCheck('the tutorial world/tutorial-component changes the engine, and the pin build holds no change')
        self.book.write('tutorials/world/tutorial-component.patch', 'not a diff\n')
        self.assertCheck('tutorials/world/tutorial-component.patch:1: the patch changes no file')

    def test_an_engine_exercise_s_suites_are_named_for_a_worked_solution_the_chain_declares(self):
        self.book.write('src/content/docs/world/tutorial-component.md', '---\nkind: tutorial\n---\n')
        self.book.write('src/content/docs/gpu/debug-drawing.md', '---\nkind: internals\n---\n')
        self.write_tutorial({'page': 'world/tutorial-component', 'startsFrom': {'pin': True},
                             'patch': {'file': 'tutorials/world/tutorial-component.patch', 'tests': ['World.WindZone']}},
                            'world/tutorial-component')
        self.book.write('tutorials/world/tutorial-component.patch', c_Patch)
        self.book.write('tutorials/gpu/debug-drawing/exercise-3.patch', c_Patch.replace('World.WindZone', 'World.Gizmo'))
        data = {'page': 'gpu/debug-drawing', 'startsFrom': {'tutorial': 'world/tutorial-component'},
                'exercises': {'3': {'tests': ['World.WindZone', 'World.Gizmo']}}}
        self.write_tutorial(data, 'gpu/debug-drawing')
        code, output = self.check()
        self.assertNotIn('exercises', output)
        data['exercises'] = {'3': {'tests': ['World.Gust']}, '4': {'tests': ['World.WindZone']}}
        self.write_tutorial(data, 'gpu/debug-drawing')
        output = self.assertCheck('the doctest suite World.Gust is neither one of the pin')
        self.assertIn('exercises names exercise 4, which has no worked solution tutorials/gpu/debug-drawing/exercise-4.patch', output)
        self.assertNotIn('the doctest suite World.WindZone is neither', output)

    def test_a_patch_tutorial_that_starts_from_an_exercise_s_solution(self):
        # rulings-9.md, R41: scripting/tutorial-host-function starts from the worked solution of gpu/debug-drawing's
        # exercise 3, and that page's file, without stages or patch, starts from world/tutorial-component. The chain's
        # patches are the component's, the exercise's and the tutorial's own, and the suites of all three count.
        self.book.write('src/content/docs/world/tutorial-component.md', '---\nkind: tutorial\n---\n')
        self.book.write('src/content/docs/gpu/debug-drawing.md', '---\nkind: internals\n---\n')
        self.book.write('src/content/docs/scripting/tutorial-host-function.md', '---\nkind: tutorial\n---\n')
        self.write_tutorial({'page': 'world/tutorial-component', 'startsFrom': {'pin': True},
                             'patch': {'file': 'tutorials/world/tutorial-component.patch', 'tests': ['World.WindZone']}},
                            'world/tutorial-component')
        self.book.write('tutorials/world/tutorial-component.patch', c_Patch)
        self.write_tutorial({'page': 'gpu/debug-drawing', 'startsFrom': {'tutorial': 'world/tutorial-component'}}, 'gpu/debug-drawing')
        self.book.write('tutorials/gpu/debug-drawing/exercise-3.patch', c_Patch.replace('World.WindZone', 'World.Gizmo'))
        host = {'page': 'scripting/tutorial-host-function', 'startsFrom': {'tutorial': 'gpu/debug-drawing', 'exercise': 3},
                'patch': {'file': 'tutorials/scripting/tutorial-host-function.patch', 'tests': ['World.WindZone', 'World.Gizmo', 'World.Host']}}
        self.write_tutorial(host, 'scripting/tutorial-host-function')
        self.book.write('tutorials/scripting/tutorial-host-function.patch', c_Patch.replace('World.WindZone', 'World.Host'))
        code, output = self.check()
        for text in ('is neither one of the pin', 'which does not exist', 'has no patch', 'changes the engine, and the pin build',
                     'has no worked solution'):
            self.assertNotIn(text, output)
        book = tutorials.Book(tutorials.repo.Layout(self.book.root))
        self.assertEqual(tutorials.PatchItem(book, book.by_key['scripting/tutorial-host-function']).patches,
                         ['tutorials/world/tutorial-component.patch', 'tutorials/gpu/debug-drawing/exercise-3.patch',
                          'tutorials/scripting/tutorial-host-function.patch'])
        exercise = [item for item in book.exercise_patches if item.key == 'gpu/debug-drawing/exercise-3'][0]
        self.assertEqual(tutorials.PatchItem(book, exercise).patches,
                         ['tutorials/world/tutorial-component.patch', 'tutorials/gpu/debug-drawing/exercise-3.patch'])
        # Without the exercise's solution, neither its suite nor the exercise is there.
        host['startsFrom']['exercise'] = 4
        self.write_tutorial(host, 'scripting/tutorial-host-function')
        output = self.assertCheck('startsFrom names exercise 4 of gpu/debug-drawing, which has no worked solution '
                                  'tutorials/gpu/debug-drawing/exercise-4.patch')
        self.assertIn('the doctest suite World.Gizmo is neither one of the pin', output)
        self.assertNotIn('the doctest suite World.WindZone is neither', output)

    def test_downloads_follow_compile_and_zips_carry_their_credits(self):
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertEqual(code, 0, output)
        self.assertIn('public/downloads/tutorials/test/greeter/stage-1.commands.json: wrote', output)
        code, output = self.check()
        self.assertEqual(code, 0, output)
        self.assertNotIn('commands.json is not written yet', output)
        # A hand-edited reader copy, and a download of a stage the tutorial no longer has.
        self.book.write('public/downloads/tutorials/test/greeter/stage-1.commands.json', '[]\n')
        self.book.write('public/downloads/tutorials/test/greeter/stage-7.commands.json', '[]\n')
        output = self.assertCheck('public/downloads/tutorials/test/greeter/stage-1.commands.json:1: differs from what compile writes from '
                                  'tutorials/test/greeter.tutorial.json:5: run python -I tools/tutorials.py compile')
        self.assertIn('stage-7.commands.json:1: the tutorial tutorials/test/greeter.tutorial.json no longer makes this download', output)
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertIn('stage-7.commands.json: removed', output)
        # A zip that holds the sample's CC BY fox without its credits, and one over 10 MB.
        with zipfile.ZipFile(self.book.path('public/downloads/tutorials/test/greeter/stage-1.zip'), 'w') as archive:
            archive.writestr('Greeter/Assets/Fox.glb', 'fox model')
        output = self.assertCheck('tutorials/test/greeter.tutorial.json:5: public/downloads/tutorials/test/greeter/stage-1.zip holds a CC BY '
                                  'file, and its CREDITS.md lacks the file\'s row')
        with zipfile.ZipFile(self.book.path('public/downloads/tutorials/test/greeter/stage-1.zip'), 'w') as archive:
            archive.writestr('Greeter/Assets/Fox.glb', 'fox model')
            archive.writestr('CREDITS.md', c_FoxRow + '\n')
        self.assertNotIn('holds a CC BY file', self.check()[1])
        with mock.patch.object(tutorial_files, 'c_ZipLimit', 10), mock.patch.object(tutorial_files, 'c_ZipsLimit', 20):
            output = self.assertCheck('over the 10 MB a download may have')
            self.assertIn('over the 150 MB they may hold', output)
        # Zips need the samples' credits, so the check needs the engine.
        code, output = quiet(tutorials.main, 'check', '--root', self.book.root, '--dumps', self.dumps)
        self.assertEqual(code, 2, output)
        self.assertIn('the downloads hold zips', output)

    def test_a_zip_holds_no_presets_the_editor_wrote_for_its_machine(self):
        quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        editor_presets = json.dumps({'version': 3, 'vendor': {'strata.dev/editor': {'note': 'Written by the Strata editor'}}})
        with zipfile.ZipFile(self.book.path('public/downloads/tutorials/test/greeter/stage-1.zip'), 'w') as archive:
            archive.writestr('Greeter/Scripts/CMakePresets.json', editor_presets)
        self.assertCheck('tutorials/test/greeter.tutorial.json:5: public/downloads/tutorials/test/greeter/stage-1.zip holds '
                         'Greeter/Scripts/CMakePresets.json, the CMakePresets.json the editor writes with the folders of the machine '
                         'it runs on (StrataEditor/src/Editor/ScriptBuild.h:101-103 at the pin), and a reader\'s editor writes their '
                         'own: make the zip again with tutorials.py run, which leaves it out')
        # Presets the project wrote itself are its own.
        with zipfile.ZipFile(self.book.path('public/downloads/tutorials/test/greeter/stage-1.zip'), 'w') as archive:
            archive.writestr('Greeter/Scripts/CMakePresets.json', json.dumps({'version': 3, 'configurePresets': []}))
        self.assertNotIn('CMakePresets.json', self.check()[1])

    def test_a_stamp_is_current_while_its_inputs_are(self):
        quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        tutorial = tutorials.Book(tutorials.repo.Layout(self.book.root)).by_key['test/greeter']
        inputs = {}
        for relative in ('tutorials/test/greeter.tutorial.json', 'tutorials/test/greeter/Greeter.cpp',
                         'public/downloads/tutorials/test/greeter/stage-1.commands.json',
                         'public/downloads/tutorials/test/greeter/stage-2.commands.json'):
            with open(self.book.path(relative), 'rb') as file:
                inputs[relative] = hashlib.sha256(file.read()).hexdigest()
        run = {'build': {'kind': 'pin-build'}, 'engineCommit': self.pin, 'inputs': inputs, 'passed': True}
        tutorials.write_stamp(tutorials.repo.Layout(self.book.root), tutorial, run)
        code, output = self.check('--release', 'test/greeter')
        self.assertNotIn('stamp', output)
        # A reader copy the run hashed is not in the tree: compile writes it again, and no engine program needs to run.
        os.remove(self.book.path('public/downloads/tutorials/test/greeter/stage-2.commands.json'))
        self.assertCheck('tutorials/test/greeter.stamp.json:1: tutorials/test/greeter.stamp.json is not current: no run by a pin build or a '
                         'patch build passed at the pin with the inputs as they are now (run 1: the input '
                         'public/downloads/tutorials/test/greeter/stage-2.commands.json does not exist): write the missing downloads with '
                         'python -I tools/tutorials.py compile test/greeter, and run the tutorial again only if check still finds the stamp '
                         'not current', '--release')
        quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root, 'test/greeter')
        code, output = self.check('--release', 'test/greeter')
        self.assertNotIn('stamp', output)
        self.book.write('tutorials/test/greeter/Greeter.cpp', '// changed\n')
        output = self.assertCheck('tutorials/test/greeter.stamp.json:1: tutorials/test/greeter.stamp.json is not current: no run by a pin build or a '
                                  'patch build passed at the pin with the inputs as they are now (run 1: tutorials/test/greeter/Greeter.cpp '
                                  'changed since the run): run the tutorial again with python -I tools/tutorials.py run test/greeter, under '
                                  'the perf lock', '--release')
        # A file the run read changed, and a download is missing too: only a run makes the stamp current.
        os.remove(self.book.path('public/downloads/tutorials/test/greeter/stage-2.commands.json'))
        output = self.assertCheck('changed since the run): run the tutorial again with python -I tools/tutorials.py run test/greeter', '--release')
        self.assertNotIn('only if check still finds', output)
        quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root, 'test/greeter')
        # A stamp that does not exist names the command that writes it.
        os.remove(self.book.path('tutorials/test/greeter.stamp.json'))
        self.assertCheck('tutorials/test/greeter.stamp.json does not exist: run it with python -I tools/tutorials.py run test/greeter', '--release')
        tutorials.write_stamp(tutorials.repo.Layout(self.book.root), tutorial, run)
        # At a release pin a run of the release's package is needed too.
        self.book.write('engine.pin', 'commit %s\nrelease 0.8.0\nprerelease no\nrepository https://github.com/2042Third/GameEngine\n' % self.pin)
        self.assertCheck('at a release pin a run of the release\'s package passes too: run it with python -I tools/tutorials.py run '
                         'test/greeter --build <the unpacked package> --package <its archive>, under the perf lock', '--release')
        # A package run that lacks only a reader copy holds again once compile has written it.
        now = {}
        for relative in inputs:
            with open(self.book.path(relative), 'rb') as file:
                now[relative] = hashlib.sha256(file.read()).hexdigest()
        tutorials.write_stamp(tutorials.repo.Layout(self.book.root), tutorial, {
            'build': {'kind': 'package', 'package': 'Strata-0.8.0-Windows.zip'}, 'engineCommit': self.pin, 'inputs': now, 'passed': True})
        os.remove(self.book.path('public/downloads/tutorials/test/greeter/stage-1.commands.json'))
        output = self.assertCheck('at a release pin a run of the release\'s package passes too (run 2: the input '
                                  'public/downloads/tutorials/test/greeter/stage-1.commands.json does not exist): write the missing downloads '
                                  'with python -I tools/tutorials.py compile test/greeter', '--release')
        self.assertIn('(run 1: tutorials/test/greeter/Greeter.cpp changed since the run): run the tutorial again', output)

    def test_usage(self):
        code, output = quiet(tutorials.main, 'check', '--root', self.book.root, '--engine', self.engine.root, 'test/nothing', '--dumps', self.dumps)
        self.assertEqual(code, 2)
        self.assertIn('no tutorial or exercise of the book is named test/nothing', output)
        code, output = quiet(tutorials.main, 'check', '--root', self.book.root, '--dumps', os.path.join(self.book.root, 'nowhere'))
        self.assertEqual(code, 2)
        self.assertIn('the dumps folder', output)
        with self.assertRaises(SystemExit) as raised:
            quiet(tutorials.main, 'check', '--root', self.book.root)
        self.assertEqual(raised.exception.code, 2)
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            tutorials.main(['--help'])
        self.assertEqual(raised.exception.code, 0)
        # --help says what the plan says each command does.
        for text in ('check     Offline', 'compile   Writes the reader\'s copies', 'run       Per tutorial, in a --no-gpu editor',
                     'patch     Per patch tutorial and engine exercise (phase B, §6.6)', '--label docs-tutorials --wait 120'):
            self.assertIn(text, output.getvalue())


class CompileTests(TutorialsTestCase):
    def test_the_reader_copy_is_an_engine_command_script(self):
        quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        script = read_json(self.book.path('public/downloads/tutorials/test/greeter/stage-2.commands.json'))
        self.assertEqual(script[0], {'command': 'script.build', 'expect': {'/success': {'equals': True}}})
        # entityName becomes an entity.find step that binds the first match, which the step names as its entity.
        self.assertEqual(script[1], {'command': 'entity.find', 'parameters': {'name': 'Cube'}, 'bind': {'entityName.1': '/entities/0'}})
        self.assertEqual(script[2], {'command': 'script.add', 'parameters': {'class': 'Greeter', 'fields': {'DegreesPerStep': 0.75},
                                                                            'entity': {'$ref': 'entityName.1'}}})
        self.assertEqual(script[5], {'command': 'play.state', 'expect': {'/fixedSteps': {'min': 60}}, 'until': {'steps': 10}})
        self.assertFalse(any('checks' in step or 'entityName' in step for step in script))
        for step in script:
            self.assertLessEqual(set(step), {'command', 'parameters', 'expect', 'bind', 'until'})
        first = self.book.read('public/downloads/tutorials/test/greeter/stage-2.commands.json')
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertIn('0 downloads written, 2 unchanged', output)
        self.assertEqual(first, self.book.read('public/downloads/tutorials/test/greeter/stage-2.commands.json'))

    def test_a_how_to_offers_only_its_last_stage(self):
        # plan/site.md: a how-to has no checkpoints; the build offers its tutorial file's last stage at the end of "## Result",
        # so the earlier stages make no download, which no page would link.
        self.book.write('src/content/docs/test/howto.md', '---\nkind: how-to\n---\n\n## Steps\n\n## Result\n')
        self.write_tutorial(dict(self.tutorial(), page='test/howto'), 'test/howto')
        folder = 'public/downloads/tutorials/test/howto'
        self.book.write(folder + '/stage-1.commands.json', '[]')
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertEqual(code, 0, output)
        self.assertEqual(sorted(os.listdir(self.book.path(folder))), ['stage-2.commands.json'])
        self.assertIn('%s/stage-1.commands.json: removed' % folder, output)
        _, output = self.check()
        self.assertNotIn('test/howto/stage-1', output)
        # A stage download the page does not offer is one the tutorial no longer makes.
        self.book.write(folder + '/stage-1.zip', 'zip')
        self.assertCheck('%s/stage-1.zip:1: the tutorial tutorials/test/howto.tutorial.json no longer makes this download' % folder)
        os.remove(self.book.path(folder + '/stage-1.zip'))
        # A stamp whose inputs name the earlier stage's reader copy, which compile no longer writes, is still current.
        layout = tutorials.repo.Layout(self.book.root)
        howto = [item for item in tutorial_files.find_tutorials(layout) if item.key == 'test/howto'][0]
        inputs = {name: tutorial_files.sha256_file(self.book.path(name)) for name in ('tutorials/test/howto.tutorial.json', folder + '/stage-2.commands.json')}
        inputs[folder + '/stage-1.commands.json'] = '0' * 64
        self.book.write('tutorials/test/howto.stamp.json', json.dumps({'page': 'test/howto', 'runs': [
            {'engineCommit': self.pin, 'passed': True, 'build': {'kind': 'pin-build'}, 'inputs': inputs}]}))
        self.assertEqual(tutorial_files.stamp_problems(layout, howto, {'commit': self.pin, 'prerelease': True}), [])

    def test_a_solution_download_is_made_for_an_answer_that_names_it(self):
        self.book.write('tutorials/test/greeter/exercise-2.patch', c_Patch)
        self.write_tutorial({'page': 'test/greeter', 'startsFrom': {'template': 'empty'}, 'stages': [
            {'step': 1, 'commands': [{'command': 'entity.find', 'parameters': {'name': 'Sun'}}]}]}, 'test/greeter/exercise-1')
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertEqual(code, 0, output)
        # No answer of test/greeter names either solution: no page would link their downloads.
        solutions = self.book.path('public/downloads/solutions/test/greeter')
        self.assertEqual(os.listdir(solutions) if os.path.isdir(solutions) else [], [])
        page = self.book.read('src/content/docs/test/greeter.md')
        self.book.write('src/content/docs/test/greeter.md', page + '\n1. **Basic.** Do it.\n\n   :::answer[Worked solution]{tests="greet" '
                        'solution="tutorials/test/greeter/exercise-1.tutorial.json"}\n   Done.\n   :::\n\n2. **Medium.** Change it.\n\n'
                        '   :::answer[Worked solution]{solution="tutorials/test/greeter/exercise-2.patch"}\n   Changed.\n   :::\n')
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertEqual(code, 0, output)
        self.assertEqual(sorted(os.listdir(self.book.path('public/downloads/solutions/test/greeter'))), ['exercise-1.zip', 'exercise-2.patch'])
        # An answer that stops naming its solution leaves a download that check refuses and compile removes.
        self.book.write('src/content/docs/test/greeter.md', page)
        self.assertCheck('public/downloads/solutions/test/greeter/exercise-1.zip:1: no answer of src/content/docs/test/greeter.md names this '
                         'worked solution (solution="tutorials/test/greeter/exercise-1.tutorial.json"), so no page links its download')
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertIn('public/downloads/solutions/test/greeter/exercise-1.zip: removed', output)
        self.assertFalse(os.path.exists(self.book.path('public/downloads/solutions/test/greeter/exercise-2.patch')))

    def test_patch_and_solution_downloads(self):
        self.book.write('src/content/docs/world/tutorial-component.md', '---\nkind: tutorial\n---\n')
        self.write_tutorial({'page': 'world/tutorial-component', 'startsFrom': {'pin': True},
                             'patch': {'file': 'tutorials/world/tutorial-component.patch', 'tests': []}}, 'world/tutorial-component')
        self.book.write('tutorials/world/tutorial-component.patch', c_Patch)
        self.book.write('tutorials/world/tutorial-component/exercise-2.patch', c_Patch)
        # The answers name the worked solutions, so the pages link their downloads.
        self.book.write('src/content/docs/world/tutorial-component.md', '---\nkind: tutorial\n---\n\n:::answer{solution="tutorials/world/tutorial-component/exercise-2.patch"}\nDone.\n:::\n')
        self.book.write('src/content/docs/test/greeter.md', self.book.read('src/content/docs/test/greeter.md') + '\n:::answer{solution="tutorials/test/greeter/exercise-1.tutorial.json"}\nDone.\n:::\n')
        self.write_tutorial({'page': 'test/greeter', 'startsFrom': {'template': 'empty'}, 'stages': [
            {'step': 1, 'files': [{'from': 'Samples/ThirdPerson/Assets/Models/Fox.glb', 'to': 'Assets/Fox.glb'},
                                  {'from': 'book:tutorials/test/greeter/Greeter.cpp', 'to': 'Scripts/Greeter.cpp'}],
             'commands': [{'command': 'entity.find', 'parameters': {'name': 'Sun'}}]}]}, 'test/greeter/exercise-1')
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertEqual(code, 0, output)
        with open(self.book.path('public/downloads/tutorials/world/tutorial-component.patch'), encoding='utf-8') as file:
            self.assertEqual(file.read(), c_Patch)
        self.assertTrue(os.path.isfile(self.book.path('public/downloads/solutions/world/tutorial-component/exercise-2.patch')))
        with zipfile.ZipFile(self.book.path('public/downloads/solutions/test/greeter/exercise-1.zip')) as archive:
            self.assertEqual(sorted(archive.namelist()), ['Assets/Fox.glb', 'CREDITS.md', 'Scripts/Greeter.cpp', 'stage-1.commands.json'])
            self.assertIn(c_FoxRow, archive.read('CREDITS.md').decode('utf-8'))
        # The solution's download is the same bytes every time, and check agrees with it.
        with open(self.book.path('public/downloads/solutions/test/greeter/exercise-1.zip'), 'rb') as file:
            first = file.read()
        quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        with open(self.book.path('public/downloads/solutions/test/greeter/exercise-1.zip'), 'rb') as file:
            self.assertEqual(first, file.read())
        code, output = self.check()
        self.assertNotIn('differs', output)
        self.assertNotIn('exercise-1.zip holds a CC BY file', output)
        # An engine file of an exercise needs the engine.
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root)
        self.assertEqual(code, 2)
        self.assertIn('pass --engine', output)
        # A file a later command copies again is in the download once, as the exercise leaves it.
        self.book.write('tutorials/test/greeter/GreeterFast.cpp', '// fast\n')
        self.write_tutorial({'page': 'test/greeter', 'startsFrom': {'template': 'empty'}, 'stages': [
            {'step': 1, 'files': [{'from': 'book:tutorials/test/greeter/Greeter.cpp', 'to': 'Scripts/Greeter.cpp'}],
             'commands': [{'command': 'script.build'},
                          {'command': 'script.build', 'files': [{'from': 'book:tutorials/test/greeter/GreeterFast.cpp', 'to': 'Scripts/Greeter.cpp'}]}]}]},
                            'test/greeter/exercise-1')
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertEqual(code, 0, output)
        with zipfile.ZipFile(self.book.path('public/downloads/solutions/test/greeter/exercise-1.zip')) as archive:
            self.assertEqual(sorted(archive.namelist()), ['Scripts/Greeter.cpp', 'stage-1.commands.json'])
            self.assertEqual(archive.read('Scripts/Greeter.cpp'), b'// fast\n')
        # A file a later stage copies again keeps the copy the first stage's commands start from, and the later stage's copy
        # stands in a folder named after that stage, for the reader to copy before running its commands.
        self.write_tutorial({'page': 'test/greeter', 'startsFrom': {'template': 'empty'}, 'stages': [
            {'step': 1, 'files': [{'from': 'book:tutorials/test/greeter/Greeter.cpp', 'to': 'Scripts/Greeter.cpp'}],
             'commands': [{'command': 'script.build'}]},
            {'step': 2, 'files': [{'from': 'book:tutorials/test/greeter/GreeterFast.cpp', 'to': 'Scripts/Greeter.cpp'}],
             'commands': [{'command': 'script.build'}]}]}, 'test/greeter/exercise-1')
        code, output = quiet(tutorials.main, 'compile', '--root', self.book.root, '--engine', self.engine.root)
        self.assertEqual(code, 0, output)
        with zipfile.ZipFile(self.book.path('public/downloads/solutions/test/greeter/exercise-1.zip')) as archive:
            self.assertEqual(sorted(archive.namelist()), ['Scripts/Greeter.cpp', 'stage-1.commands.json', 'stage-2.commands.json',
                                                          'stage-2/Scripts/Greeter.cpp'])
            self.assertEqual(archive.read('stage-2/Scripts/Greeter.cpp'), b'// fast\n')
            self.assertNotEqual(archive.read('Scripts/Greeter.cpp'), b'// fast\n')


class ZipContentTests(unittest.TestCase):
    """What a stage's zip leaves out and refuses (booklib.tutorials)."""

    def test_the_editors_presets_by_their_vendor_key(self):
        editor_presets = json.dumps({'version': 3, 'vendor': {'strata.dev/editor': {'note': 'x'}}}).encode('utf-8')
        self.assertTrue(tutorial_files.editor_presets('Spin/Scripts/CMakePresets.json', editor_presets))
        self.assertTrue(tutorial_files.editor_presets('Scripts\\CMakePresets.json', editor_presets))
        self.assertFalse(tutorial_files.editor_presets('Scripts/Other.json', editor_presets))
        for own in (b'{"version": 3}', b'{"vendor": {"example.com/ide": {}}}', b'{"vendor": "strata.dev/editor"}', b'[]',
                    b'not json', b'\xff\xfe'):
            self.assertFalse(tutorial_files.editor_presets('Scripts/CMakePresets.json', own), own)

    def test_a_folder_of_this_machine_as_written_or_escaped(self):
        folders = ['c:/users/someone/work']
        self.assertEqual(tutorial_files.machine_folder_line(b'first\n{"dir": "C:\\\\Users\\\\Someone\\\\Work\\\\Spin"}\n', folders),
                         (2, 'c:/users/someone/work'))
        self.assertEqual(tutorial_files.machine_folder_line(b'path C:/Users/someone/work/x', folders), (1, 'c:/users/someone/work'))
        self.assertEqual(tutorial_files.machine_folder_line(b'C:\\Users\\someone\\work', folders), (1, 'c:/users/someone/work'))
        self.assertEqual(tutorial_files.machine_folder_line(b'"C:/Users/someone/work"', folders), (1, 'c:/users/someone/work'))
        # A folder whose name starts like it is another folder.
        self.assertIsNone(tutorial_files.machine_folder_line(b'c:/users/someone/workshop and c:/users/someone/work-2', folders))
        self.assertIsNone(tutorial_files.machine_folder_line(b'Assets/Scenes/Main.stscene', folders))


class FakeEditor:
    """A stand-in for booklib.editor.Editor with a tiny engine behind it: projects are folders, entities have names,
    the Transform of an entity with a script turns 0.75 degrees per fixed step, and saving writes the scene."""
    instances = []
    calls = []
    reported = None
    entities_named = {}
    fail = {}
    built = []  # Scripts/Greeter.cpp as each script.build found it
    machine_files = {}  # more files a new project gets: {relative path: text, where @DIRECTORY@ is the project's folder}

    def __init__(self, build, work, log, project=None, gpu=False):
        self.log = log
        self.entities = {}
        self.scripted = set()
        self.project = None
        self.steps = 0
        self.playing = False
        self.modified = False
        FakeEditor.instances.append(self)

    def launch(self):
        FakeEditor.calls.append(('launch', None))
        return {'ProcessId': 1}

    def check_commit(self, pin):
        reported = FakeEditor.reported or pin[:12]
        if not pin.startswith(reported):
            raise editor.PreflightError('the editor reports the engine commit %s, which is not the pin' % reported)
        return {'engineCommit': reported, 'platform': 'Windows', 'gpu': None}

    def make_project(self, directory, name):
        os.makedirs(os.path.join(directory, 'Assets', 'Scenes'))
        os.makedirs(os.path.join(directory, 'Scripts'))
        os.makedirs(os.path.join(directory, '.strata', 'Scripts', 'Build'))
        os.makedirs(os.path.join(directory, '.strata', 'Scripts', 'Bin'))
        # As the editor writes them (ScriptBuild.cpp: UpdateScriptCMakePresets): presets for this machine's engine and
        # toolchain, with its folders, and the .gitignore that keeps them out of version control.
        presets = json.dumps({'version': 3, 'configurePresets': [{'name': 'strata', 'binaryDir': os.path.join(directory, '.strata', 'Scripts', 'IDE')}],
                              'vendor': {'strata.dev/editor': {'note': 'Written by the Strata editor for this machine'}}}, indent=2)
        written = [('%s.stproj' % name, '{}'), ('Assets/Scenes/Main.stscene', 'Sun'), ('Scripts/CMakeLists.txt', '# build'),
                   ('Scripts/CMakePresets.json', presets), ('Scripts/.gitignore', '/CMakePresets.json\n'),
                   ('.strata/Scripts/Build/CMakeCache.txt', directory), ('.strata/Scripts/Bin/Module.dll', 'module')]
        written += [(relative, text.replace('@DIRECTORY@', directory)) for relative, text in FakeEditor.machine_files.items()]
        for relative, text in written:
            os.makedirs(os.path.dirname(os.path.join(directory, *relative.split('/'))), exist_ok=True)
            with open(os.path.join(directory, *relative.split('/')), 'w', encoding='utf-8') as file:
                file.write(text)
        self.project = directory
        self.entities = {'5000': 'Sun'}

    def call(self, command, parameters=None, timeout=300):
        parameters = parameters or {}
        FakeEditor.calls.append((command, parameters))
        if command in FakeEditor.fail:
            raise editor.EditorError('%s failed (StrataCLI exit code 1): %s' % (command, FakeEditor.fail[command]))
        if command == 'project.create':
            self.make_project(parameters['directory'], parameters['name'])
            return {'projectFile': 'x', 'startScene': 'Scenes/Main.stscene'}
        if command == 'project.openSample':
            self.make_project(parameters['directory'], parameters['sample'])
            return {'sample': parameters['sample']}
        if command == 'project.open':
            self.project = parameters['path']
            with open(os.path.join(self.project, 'Assets', 'Scenes', 'Main.stscene'), encoding='utf-8') as file:
                names = file.read().split(',')
            self.entities = {str(5000 + index): name for index, name in enumerate(names)}
            return {'startSceneOpened': True}
        if command == 'scene.loadStatus':
            return {'open': None}
        if command == 'editor.status':
            return {'scene': {'name': 'Main', 'scene': 'Scenes/Main.stscene', 'modified': self.modified}}
        if command == 'scene.save':
            with open(os.path.join(self.project, 'Assets', 'Scenes', 'Main.stscene'), 'w', encoding='utf-8') as file:
                file.write(','.join(self.entities.values()))
            self.modified = False
            return {'scene': 'Scenes/Main.stscene', 'path': os.path.join(self.project, 'Assets', 'Scenes', 'Main.stscene'), 'seconds': 0.1}
        if command == 'entity.create':
            identifier = '%016X' % (0xC82E016AB2AB7100 + len(self.entities))
            self.entities[identifier] = parameters.get('name', 'Entity')
            self.modified = True
            return {'id': identifier}
        if command == 'entity.find':
            found = [identifier for identifier, name in self.entities.items() if name == parameters.get('name')]
            return {'entities': found * FakeEditor.entities_named.get(parameters.get('name'), 1)}
        if command == 'component.get':
            turned = 0.75 * self.steps if parameters['entity'] in self.scripted else 0.0
            import math
            half = math.radians(turned) / 2
            return {'values': {'Translation': [0, 0.5, 0], 'Rotation': [0, math.sin(half), 0, math.cos(half)], 'Scale': [1, 1, 1]}}
        if command == 'script.build':
            source = os.path.join(self.project, 'Scripts', 'Greeter.cpp')
            if os.path.isfile(source):
                with open(source, encoding='utf-8') as file:
                    FakeEditor.built.append(file.read())
            # The log names a folder of the machine inside its text, as the engine's build log does.
            return {'success': True, 'diagnostics': [], 'log': '> cmake: C:/Program Files/CMake/bin/cmake.exe --version', 'module': self.project}
        if command == 'script.add':
            self.scripted.add(parameters['entity'])
            self.modified = True
            return {'entity': parameters['entity'], 'script': {'class': parameters['class']}}
        if command == 'play.start':
            self.playing = True
            return {'paused': True, 'state': 'Play'}
        if command == 'play.step':
            self.steps += parameters.get('steps', 1)
            return {'stepsRun': parameters.get('steps', 1), 'fixedSteps': self.steps}
        if command == 'play.state':
            return {'paused': True, 'fixedSteps': self.steps}
        if command == 'play.stop':
            self.playing = False
            self.steps = 0
            return {}
        if command == 'log.read':
            return {'messages': [{'level': 'Info', 'logger': 'Script', 'message': 'Hello from Greeter'}]}
        return {}

    def quit(self):
        FakeEditor.calls.append(('quit', None))


class RunTests(TutorialsTestCase):
    def setUp(self):
        super().setUp()
        self.build = os.path.join(self.engine.root, 'build', 'windows', 'bin', 'Release')
        os.makedirs(self.build)
        for name in ('StrataEditor', 'StrataCLI'):
            with open(editor.program_path(self.build, name), 'wb') as file:
                file.write(b'program')
        self.work = os.path.join(tempfile.mkdtemp(prefix='work-'), 'tutorials')
        FakeEditor.instances = []
        FakeEditor.calls = []
        FakeEditor.reported = None
        FakeEditor.entities_named = {}
        FakeEditor.fail = {}
        FakeEditor.built = []
        FakeEditor.machine_files = {}
        self.programs = []
        self.reader_sources = []  # Scripts/Greeter.cpp of the project each run of the engine's runner opened
        self.reader_code = 0

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.work), ignore_errors=True)
        super().tearDown()

    def run_tool(self, *extra):
        def program(arguments, env, log, name, timeout, cwd=None, merge=True):
            self.programs.append((arguments, env))
            # The start state the engine's runner opens has the project's files and its built module, never its
            # script build tree, which names another folder.
            project = arguments[arguments.index('--project') + 1]
            self.assertTrue(os.path.isfile(os.path.join(project, 'Assets', 'Scenes', 'Main.stscene')))
            self.assertTrue(os.path.isfile(os.path.join(project, '.strata', 'Scripts', 'Bin', 'Module.dll')))
            self.assertFalse(os.path.exists(os.path.join(project, '.strata', 'Scripts', 'Build')))
            source = os.path.join(project, 'Scripts', 'Greeter.cpp')
            if os.path.isfile(source):
                with open(source, encoding='utf-8') as file:
                    self.reader_sources.append(file.read())
            log.write(name, arguments, 'ran', self.reader_code)
            return self.reader_code, 'Command script finished' if self.reader_code == 0 else '[error] App: Command script finished with errors', ''
        with mock.patch.object(editor, 'Editor', FakeEditor), mock.patch.object(editor, 'run_program', program):
            return quiet(tutorials.main, 'run', '--root', self.book.root, '--engine', self.engine.root, '--build', self.build, '--work', self.work, *extra)

    def stamp(self, page='test/greeter'):
        return read_json(self.book.path('tutorials/%s.stamp.json' % page))

    def test_a_run_that_passes(self):
        code, output = self.run_tool('--record-examples')
        self.assertEqual(code, 0, output)
        self.assertIn('tutorials/test/greeter.tutorial.json:1: passed: test/greeter: 2 stages, the reader\'s copies in the engine\'s runner; '
                      'stamped tutorials/test/greeter.stamp.json', output)
        self.assertIn('tutorials: 1 passed, 0 failed, 0 skipped', output)
        commands = [command for command, _ in FakeEditor.calls]
        self.assertEqual(commands[0], 'launch')
        self.assertEqual(commands[-1], 'quit')
        create = next(parameters for command, parameters in FakeEditor.calls if command == 'project.create')
        self.assertEqual((create['name'], create['template']), ('Greeter', 'basic3d'))
        self.assertTrue(os.path.isabs(create['directory']) and create['directory'].startswith(self.work))
        # The stage's file was copied into the project, the scene saved before each start state and each zip.
        self.assertTrue(os.path.isfile(os.path.join(create['directory'], 'Scripts', 'Greeter.cpp')))
        self.assertIn('scene.save', commands)
        with zipfile.ZipFile(self.book.path('public/downloads/tutorials/test/greeter/stage-2.zip')) as archive:
            names = archive.namelist()
        self.assertIn('Greeter/Scripts/Greeter.cpp', names)
        self.assertIn('Greeter/Assets/Scenes/Main.stscene', names)
        self.assertFalse(any('.strata' in name for name in names), names)
        # The presets the editor wrote hold this machine's folders: a reader's editor writes their own.
        self.assertNotIn('Greeter/Scripts/CMakePresets.json', names)
        self.assertIn('Greeter/Scripts/.gitignore', names)
        # Each reader copy ran in the engine's own runner on its stage's start state.
        self.assertEqual(len(self.programs), 2)
        arguments, env = self.programs[1]
        self.assertEqual(arguments[0], editor.program_path(self.build, 'StrataEditor'))
        self.assertEqual(arguments[1:3], ['--no-gpu', '--no-automation'])
        self.assertEqual(arguments[-3:], ['--quit-after-commands', '--frames', '36000'])
        self.assertTrue(arguments[arguments.index('--project') + 1].endswith('start-2'))
        self.assertEqual(read_json(arguments[arguments.index('--commands') + 1]),
                         read_json(self.book.path('public/downloads/tutorials/test/greeter/stage-2.commands.json')))
        self.assertTrue(env['STRATA_SESSION_DIR'].startswith(editor.system_temp()))
        self.assertEqual(env['STRATA_SCRIPT_BUILDS_DIR'], os.path.join(self.work, 'script-builds'))
        # The stamp: the pin build, the pin, what the editor reported, the inputs, every stage and the reader's copies.
        run = self.stamp()['runs'][0]
        self.assertEqual(run['build']['kind'], 'pin-build')
        self.assertEqual(run['build']['configuration'], 'Release')
        self.assertEqual(run['build']['editorSha256'], hashlib.sha256(b'program').hexdigest())
        self.assertEqual((run['engineCommit'], run['reportedCommit'], run['os'], run['gpu']), (self.pin, self.pin[:12], 'Windows', None))
        self.assertEqual(sorted(run['inputs']), ['public/downloads/tutorials/test/greeter/stage-1.commands.json',
                                                 'public/downloads/tutorials/test/greeter/stage-2.commands.json',
                                                 'tutorials/test/greeter.tutorial.json', 'tutorials/test/greeter/Greeter.cpp'])
        self.assertEqual(run['stages'], [{'step': 1, 'passed': True}, {'step': 2, 'passed': True}])
        self.assertTrue(run['readerCopies'] and run['passed'])
        # The check now finds the stamp current and the downloads in place.
        code, output = self.check('--release')
        self.assertEqual(code, 0, output)
        # Examples hide IDs and paths.
        example = read_json(self.book.path('reference/_examples/entity.create.json'))
        self.assertEqual(example, {'pin': self.pin, 'command': 'entity.create', 'parameters': example['parameters'], 'result': {'id': '…'}})
        build = read_json(self.book.path('reference/_examples/script.build.json'))['result']
        self.assertEqual((build['log'], build['module'], build['success']), ('…', '…', True))
        self.assertEqual(read_json(self.book.path('reference/_examples/script.add.json'))['parameters']['entity'], '…')
        # Every editor of the run ended.
        self.assertEqual(commands.count('launch'), commands.count('quit'))

    def test_failures_name_the_stage_and_the_step(self):
        data = self.tutorial()
        data['stages'][1]['commands'][5]['checks'][0]['approx'] = 0.5
        self.write_tutorial(data)
        code, output = self.run_tool('--record-examples')
        self.assertEqual(code, 1, output)
        self.assertFalse(os.path.exists(self.book.path('reference/_examples')), 'a failed run records no example')
        self.assertRegex(output, r'tutorials/test/greeter\.tutorial\.json:1: failed: test/greeter: tutorials/test/greeter\.tutorial\.json:\d+: '
                                 r'stage 2: component\.get: check /values/Rotation/1 is 0\.38\d+, not 0\.5 within 0\.001: correct the steps '
                                 r'before it, or the value the check asks for')
        run = self.stamp()['runs'][0]
        self.assertEqual(run['stages'], [{'step': 1, 'passed': True}, {'step': 2, 'passed': False}])
        self.assertFalse(run['passed'] or run['readerCopies'])
        self.assertEqual(self.programs, [], 'no reader copy runs after a failed stage')
        # entityName must match exactly one entity.
        self.write_tutorial(read_json(os.path.join(c_Greeter, 'tutorials', 'test', 'greeter.tutorial.json')))
        FakeEditor.entities_named = {'Cube': 2}
        code, output = self.run_tool()
        self.assertIn('entityName "Cube" matches 2 entities; it must match exactly one: name an entity the scene has at this step', output)
        # A command the editor refuses, and a reader copy the engine's runner fails.
        FakeEditor.entities_named = {}
        FakeEditor.fail = {'script.build': 'the build failed'}
        code, output = self.run_tool()
        self.assertIn('stage 2: script.build failed (StrataCLI exit code 1): the build failed: correct the step, or the steps before it '
                      '(the run\'s log holds every call and its answer)', output)
        # A project the editor cannot make.
        FakeEditor.fail = {'project.create': 'the folder is not empty'}
        code, output = self.run_tool()
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'tutorials/test/greeter\.tutorial\.json:1: failed: test/greeter: tutorials/test/greeter\.tutorial\.json:\d+: '
                                 r'project\.create failed \(StrataCLI exit code 1\): the folder is not empty: the editor did not start, or did '
                                 r'not make or save the project the tutorial starts from')
        FakeEditor.fail = {}
        self.reader_code = 1
        code, output = self.run_tool()
        self.assertEqual(code, 1, output)
        self.assertIn('the engine\'s runner exited with 1 on the reader\'s copy of stage 1: [error] App: Command script finished with errors', output)
        self.assertIn('correct the stage so that its reader\'s copy, the commands without the book\'s checks and with entity.find for each '
                      'entityName, also passes in the engine\'s own runner on the stage\'s start state', output)
        run = self.stamp()['runs'][0]
        self.assertEqual(run['stages'], [{'step': 1, 'passed': True}, {'step': 2, 'passed': True}])
        self.assertFalse(run['readerCopies'] or run['passed'])
        self.assertEqual(len(self.stamp()['runs']), 1, 'a run replaces the earlier run of the same build')

    def test_a_tutorial_that_asks_for_automation(self):
        # A page about what an agent sees of the automation server: its reader's copies run in an editor that serves
        # automation, on the free loopback port the editor picks itself; the run names no port and passes no token.
        data = self.tutorial()
        data['automation'] = True
        self.write_tutorial(data)
        code, output = self.check()
        self.assertEqual(code, 0, output)
        code, output = self.run_tool()
        self.assertEqual(code, 0, output)
        self.assertEqual(len(self.programs), 2)
        for arguments, env in self.programs:
            self.assertEqual(arguments[1], '--no-gpu')
            self.assertNotIn('--no-automation', arguments)
            self.assertNotIn('--automation-port', arguments)
            self.assertFalse({'STRATA_EDITOR_PORT', 'STRATA_EDITOR_TOKEN'} & set(env))
            self.assertTrue(env['STRATA_SESSION_DIR'].startswith(editor.system_temp()))
        # Only that file: another tutorial's reader copies still run without automation.
        data['automation'] = False
        self.write_tutorial(data)
        self.programs = []
        code, output = self.run_tool()
        self.assertEqual(code, 0, output)
        self.assertTrue(self.programs and all('--no-automation' in arguments for arguments, _ in self.programs))

    def test_a_command_s_files_and_the_release_folder(self):
        # A page that teaches a build error and its fix inside one stage: the fix is copied just before the build that
        # follows it, and the import names the release's folder, which is the build's.
        self.book.write('tutorials/test/greeter/GreeterFixed.cpp', '// fixed\n')
        fox = '@RELEASE@/Samples/ThirdPerson/Assets/Models/Fox.glb'
        data = self.tutorial()
        stage = data['stages'][1]
        stage['setup'] = [{'command': 'asset.import', 'parameters': {'file': fox}}]
        stage['commands'][1:1] = [{'command': 'asset.import', 'parameters': {'file': fox, 'directory': 'Models'}},
                                  {'command': 'script.build', 'expect': {'/success': {'equals': True}},
                                   'files': [{'from': 'book:tutorials/test/greeter/GreeterFixed.cpp', 'to': 'Scripts/Greeter.cpp'}]}]
        self.write_tutorial(data)
        code, output = self.run_tool()
        self.assertEqual(code, 0, output)
        with open(self.book.path('tutorials/test/greeter/Greeter.cpp'), encoding='utf-8') as file:
            original = file.read()
        self.assertEqual(FakeEditor.built, [original, '// fixed\n'])
        release = self.build.replace('\\', '/') + '/Samples/ThirdPerson/Assets/Models/Fox.glb'
        imports = [parameters['file'] for command, parameters in FakeEditor.calls if command == 'asset.import']
        self.assertEqual(imports, [release, release])
        # The reader's copy of stage 2 runs in two runs of the engine's runner, the file copied between them; the run's
        # copies name the release's folder, the download names it as pages do.
        self.assertEqual(len(self.programs), 3)
        self.assertEqual(self.reader_sources, [original, '// fixed\n'])
        first = read_json(self.programs[1][0][self.programs[1][0].index('--commands') + 1])
        second = read_json(self.programs[2][0][self.programs[2][0].index('--commands') + 1])
        self.assertEqual([step['command'] for step in first], ['script.build', 'asset.import'])
        self.assertEqual(first[1]['parameters']['file'], release)
        self.assertEqual(second[0], {'command': 'script.build', 'expect': {'/success': {'equals': True}}})
        download = read_json(self.book.path('public/downloads/tutorials/test/greeter/stage-2.commands.json'))
        self.assertEqual(download[1]['parameters']['file'], '<release folder>/Samples/ThirdPerson/Assets/Models/Fox.glb')
        self.assertEqual([step['command'] for step in download], [step['command'] for step in first + second])
        self.assertIn('tutorials/test/greeter/GreeterFixed.cpp', self.stamp()['runs'][0]['inputs'])

    def test_a_stage_zip_names_no_folder_of_this_machine(self):
        # A file the editor wrote with the project's folder, which a zip would publish (JSON escapes the backslashes).
        FakeEditor.machine_files = {'Assets/Settings/Local.json': json.dumps({'cache': '@DIRECTORY@'})}
        code, output = self.run_tool()
        self.assertEqual(code, 1, output)
        self.assertRegex(output, r'tutorials/test/greeter\.tutorial\.json:1: failed: test/greeter: tutorials/test/greeter\.tutorial\.json:\d+: '
                                 r'stage 1: Greeter/Assets/Settings/Local\.json names a folder of this machine on its line 1 \(.+\), and the '
                                 r'stage\'s zip would publish it: remove the file from the project, or, when the editor writes it for the '
                                 r'machine it runs on, leave it out of the zip')
        self.assertFalse(os.path.exists(self.book.path('public/downloads/tutorials/test/greeter/stage-1.zip')))
        run = self.stamp()['runs'][0]
        self.assertEqual(run['stages'], [{'step': 1, 'passed': False}, {'step': 2, 'passed': False}])
        self.assertFalse(run['passed'])
        # The same file without the folder is the project's own and is published.
        FakeEditor.machine_files = {'Assets/Settings/Local.json': json.dumps({'cache': 'Cache'})}
        code, output = self.run_tool()
        self.assertEqual(code, 0, output)
        with zipfile.ZipFile(self.book.path('public/downloads/tutorials/test/greeter/stage-1.zip')) as archive:
            self.assertIn('Greeter/Assets/Settings/Local.json', archive.namelist())

    def test_preflight_and_what_waits_for_phase_b(self):
        FakeEditor.reported = 'abcdef123456'
        code, output = self.run_tool()
        self.assertEqual(code, 2, output)
        self.assertIn('the editor reports the engine commit abcdef123456, which is not the pin', output)
        self.assertFalse(os.path.exists(self.book.path('tutorials/test/greeter.stamp.json')))
        FakeEditor.reported = None
        code, output = self.run_tool('--pictures')
        self.assertEqual(code, 2)
        self.assertIn('--pictures takes a whole-editor picture after each stage with the GPU: it runs in phase B', output)
        # A tutorial that renders, and one that changes the engine, are skipped and reported.
        data = self.tutorial()
        data['stages'][0]['commands'].append({'command': 'viewport.capture', 'parameters': {'width': 64, 'height': 64}})
        self.write_tutorial(data)
        self.book.write('src/content/docs/world/tutorial-component.md', '---\nkind: tutorial\n---\n')
        self.write_tutorial({'page': 'world/tutorial-component', 'startsFrom': {'pin': True},
                             'patch': {'file': 'tutorials/world/tutorial-component.patch', 'tests': []}}, 'world/tutorial-component')
        FakeEditor.calls = []
        code, output = self.run_tool()
        self.assertEqual(code, 0, output)
        self.assertIn('skipped: test/greeter: viewport.capture renders, which needs the GPU: run it with --pictures in phase B', output)
        self.assertIn('skipped: world/tutorial-component: it changes the engine; tutorials.py patch runs it (phase B)', output)
        self.assertNotIn('launch', [command for command, _ in FakeEditor.calls])
        # A clone that is not at the pin, a build without the editor, a work folder of something else.
        os.remove(editor.program_path(self.build, 'StrataEditor'))
        code, output = self.run_tool()
        self.assertEqual(code, 2)
        self.assertIn('lacks StrataEditor', output)
        with open(editor.program_path(self.build, 'StrataEditor'), 'wb') as file:
            file.write(b'program')
        other = os.path.join(os.path.dirname(self.work), 'other')
        os.makedirs(other)
        with open(os.path.join(other, 'mine.txt'), 'w', encoding='utf-8') as file:
            file.write('not a run')
        code, output = self.run_tool('--work', other)
        self.assertEqual(code, 2)
        self.assertIn('holds files that are not a run of tutorials.py', output)
        self.assertTrue(os.path.isfile(os.path.join(other, 'mine.txt')))
        self.engine.commit({'Samples/new.txt': 'x'})
        code, output = self.run_tool()
        self.assertEqual(code, 2)
        self.assertIn('not at the pin', output)

    def test_a_chain_runs_each_tutorial_once_and_a_sample_publishes_no_zip(self):
        self.book.write('src/content/docs/test/after.md', '---\nkind: tutorial\n---\n\n::checkpoint{stage=1}\n')
        self.write_tutorial({'page': 'test/after', 'startsFrom': {'tutorial': 'test/greeter'}, 'stages': [
            {'step': 1, 'commands': [{'command': 'entity.find', 'parameters': {'name': 'Cube'}, 'checks': [{'pointer': '/entities', 'length': 1}]}],
             'endState': True}]}, 'test/after')
        code, output = self.run_tool()
        self.assertEqual(code, 0, output)
        self.assertIn('passed: test/after', output)
        commands = [command for command, _ in FakeEditor.calls]
        self.assertEqual(commands.count('project.create'), 1, 'the end state of test/greeter is cached, not replayed')
        self.assertEqual(commands.count('project.open'), 1)
        self.assertIn('tutorials/test/greeter.tutorial.json', self.stamp('test/after')['runs'][0]['inputs'])
        # Run alone, the later tutorial replays the earlier one in its own editor.
        FakeEditor.calls = []
        code, output = self.run_tool('test/after')
        self.assertEqual(code, 0, output)
        commands = [command for command, _ in FakeEditor.calls]
        self.assertEqual((commands.count('project.create'), commands.count('script.build')), (1, 1))
        self.assertFalse(os.path.exists(self.book.path('public/downloads/tutorials/test/after/stage-2.zip')))
        # A tutorial that starts from a sample publishes no zip: the reader has the sample.
        data = self.tutorial()
        data['startsFrom'] = {'sample': 'ThirdPerson'}
        self.write_tutorial(data)
        shutil.rmtree(self.book.path('public/downloads/tutorials/test/greeter'))
        code, output = self.run_tool('test/greeter')
        self.assertEqual(code, 0, output)
        self.assertIn(('project.openSample', {'sample': 'ThirdPerson', 'directory': os.path.join(self.work, 't01', 'Greeter')}), FakeEditor.calls)
        self.assertEqual(sorted(os.listdir(self.book.path('public/downloads/tutorials/test/greeter'))),
                         ['stage-1.commands.json', 'stage-2.commands.json'])

    def test_a_release_package_is_named_by_its_archive(self):
        package = tempfile.mkdtemp(prefix='package-')
        try:
            for name in ('StrataEditor', 'StrataCLI'):
                with open(editor.program_path(package, name), 'wb') as file:
                    file.write(b'packaged')
            self.build = package
            code, output = self.run_tool()
            self.assertEqual(code, 2)
            self.assertIn('is outside the clone, so it is a release package: name the archive it was unpacked from with --package', output)
            archive = os.path.join(package, 'Strata-0.8.0-Windows.zip')
            with open(archive, 'wb') as file:
                file.write(b'archive')
            code, output = self.run_tool('--package', archive)
            self.assertEqual(code, 0, output)
            build = self.stamp()['runs'][0]['build']
            self.assertEqual((build['kind'], build['package'], build['packageSha256']),
                             ('package', 'Strata-0.8.0-Windows.zip', hashlib.sha256(b'archive').hexdigest()))
        finally:
            shutil.rmtree(package, ignore_errors=True)


class PatchTests(TutorialsTestCase):
    def setUp(self):
        super().setUp()
        self.book.write('src/content/docs/world/tutorial-component.md', '---\nkind: tutorial\n---\n')
        self.write_tutorial({'page': 'world/tutorial-component', 'startsFrom': {'pin': True},
                             'patch': {'file': 'tutorials/world/tutorial-component.patch', 'tests': ['World.WindZone']}}, 'world/tutorial-component')
        self.book.write('tutorials/world/tutorial-component.patch', c_Patch)
        self.build_dir = os.path.join(self.engine.root, 'build', 'docs-patch')
        self.work = os.path.join(tempfile.mkdtemp(prefix='work-'), 'patch')
        self.ran = []
        self.outputs = {}

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.work), ignore_errors=True)
        super().tearDown()

    def run_tool(self, *extra, revert_fails=False):
        real = editor.run_program

        def program(arguments, env, log, name, timeout, cwd=None, merge=True):
            if arguments[0] == 'git':
                if revert_fails and '-R' in arguments:
                    return 1, 'error: patch failed', ''
                return real(arguments, env, log, name, timeout, cwd, merge)
            self.ran.append(arguments)
            self.assertEqual(env['MSBUILDDISABLENODEREUSE'], '1')
            if name == 'configure':
                os.makedirs(self.build_dir, exist_ok=True)
                open(os.path.join(self.build_dir, 'CMakeCache.txt'), 'w').close()
            # The patch is applied while the build and the tests run, and reverted before the configure that follows the revert.
            with open(os.path.join(self.engine.root, 'Strata', 'src', 'Strata', 'World', 'Wind.h'), encoding='utf-8') as file:
                (self.assertNotIn if name == 'configure-reverted' else self.assertIn)('WindZone', file.read())
            return self.outputs.get(name, (0, '[doctest] test cases:  3 |  3 passed | 0 failed | 0 skipped' if name.startswith('test-')
                                           else '100% tests passed, 0 tests failed out of 1' if name.startswith('ctest') else 'done', ''))
        with mock.patch.object(editor, 'run_program', program), mock.patch.object(tutorials.shutil, 'which', lambda name: '/bin/' + name):
            return quiet(tutorials.main, 'patch', '--root', self.book.root, '--engine', self.engine.root, '--build-dir', self.build_dir,
                         '--work', self.work, *extra)

    def clean(self):
        return self.engine.git('status', '--porcelain') == ''

    def test_a_patch_is_applied_built_tested_and_reverted(self):
        code, output = self.run_tool()
        self.assertEqual(code, 0, output)
        self.assertIn('passed: world/tutorial-component: tutorials/world/tutorial-component.patch, 2 doctest suites and the feature test', output)
        self.assertTrue(self.clean())
        self.assertEqual(self.ran[0], ['/bin/cmake', '--preset', 'windows', '-B', self.build_dir])
        self.assertEqual(self.ran[1], ['/bin/cmake', '--build', self.build_dir, '--config', 'Release', '--parallel', '2', '--target',
                                       'StrataTests', '--', '/p:CL_MPCount=4'])
        tests = editor.program_path(os.path.join(self.build_dir, 'bin', 'Release'), 'StrataTests')
        self.assertEqual(self.ran[2], [tests, '--test-suite=Architecture.Layering'])
        self.assertEqual(self.ran[3], [tests, '--test-suite=World.WindZone'])
        self.assertEqual(self.ran[4], ['/bin/ctest', '--test-dir', self.build_dir, '-C', 'Release', '-R', '^StrataTests\\.FeatureTest$'])
        run = read_json(self.book.path('tutorials/world/tutorial-component.stamp.json'))['runs'][0]
        self.assertEqual(run['build']['kind'], 'patch-build')
        self.assertEqual(run['tests'], [{'suite': 'Architecture.Layering', 'testCases': 3, 'passed': True},
                                        {'suite': 'World.WindZone', 'testCases': 3, 'passed': True}])
        self.assertEqual(run['ctest'], {'test': 'StrataTests.FeatureTest', 'passed': True})
        self.assertEqual(sorted(run['inputs']), ['tutorials/world/tutorial-component.patch', 'tutorials/world/tutorial-component.tutorial.json'])
        self.assertTrue(run['passed'])
        # The configure step runs after every apply (a chain adding no file needs none after the revert); a chain that changes
        # the editor builds it too.
        self.book.write('tutorials/world/tutorial-component/exercise-1.patch', c_EditorPatch)
        self.ran = []
        code, output = self.run_tool('world/tutorial-component/exercise-1')
        self.assertEqual(code, 0, output)
        self.assertEqual(self.ran[0], ['/bin/cmake', '--preset', 'windows', '-B', self.build_dir])
        self.assertEqual(self.ran[1][:2], ['/bin/cmake', '--build'])
        self.assertEqual(self.ran[1][8:10], ['StrataTests', 'StrataEditor'])
        self.assertEqual(len(self.ran), 5)
        self.assertTrue(os.path.isfile(self.book.path('tutorials/world/tutorial-component/exercise-1.stamp.json')))
        self.assertTrue(self.clean())

    def test_a_chain_that_adds_files_is_configured_after_the_apply_and_after_the_revert(self):
        # The engine collects its sources with a CONFIGURE_DEPENDS glob: built without a configure, the shared build folder
        # reconfigures in the middle of the build, after MSBuild loaded the old projects (C1083 on another chain's file).
        configure = ['/bin/cmake', '--preset', 'windows', '-B', self.build_dir]
        os.makedirs(self.build_dir, exist_ok=True)
        open(os.path.join(self.build_dir, 'CMakeCache.txt'), 'w').close()
        self.book.write('tutorials/world/tutorial-component.patch', c_Patch + c_AddingPatch)
        code, output = self.run_tool()
        self.assertEqual(code, 0, output)
        self.assertEqual(self.ran[0], configure)
        self.assertEqual(self.ran[1][:2], ['/bin/cmake', '--build'])
        self.assertEqual(self.ran[-1], configure)
        self.assertEqual(len(self.ran), 6)
        self.assertTrue(self.clean())
        self.assertFalse(os.path.exists(os.path.join(self.engine.root, 'Strata', 'src', 'Strata', 'World', 'Gust.h')))
        # A configure after the revert that fails fails the run: the build folder still lists the chain's files.
        self.outputs = {'configure-reverted': (1, 'CMake Error at Strata/CMakeLists.txt:12', '')}
        code, output = self.run_tool()
        self.assertEqual(code, 1, output)
        self.assertIn('after the patches were reverted, cmake --preset windows -B %s exited with 1' % self.build_dir, output)
        self.assertFalse(read_json(self.book.path('tutorials/world/tutorial-component.stamp.json'))['runs'][0]['passed'])
        self.assertTrue(self.clean())

    def test_an_engine_exercise_runs_the_suites_its_page_s_file_names_for_it(self):
        self.book.write('src/content/docs/gpu/debug-drawing.md', '---\nkind: internals\n---\n')
        self.write_tutorial({'page': 'gpu/debug-drawing', 'startsFrom': {'tutorial': 'world/tutorial-component'},
                             'exercises': {'3': {'tests': ['World.Gizmo']}}}, 'gpu/debug-drawing')
        self.book.write('tutorials/gpu/debug-drawing/exercise-3.patch', c_EditorPatch)
        code, output = self.run_tool('gpu/debug-drawing/exercise-3')
        self.assertEqual(code, 0, output)
        tests = editor.program_path(os.path.join(self.build_dir, 'bin', 'Release'), 'StrataTests')
        self.assertEqual([arguments for arguments in self.ran if arguments[0] == tests],
                         [[tests, '--test-suite=Architecture.Layering'], [tests, '--test-suite=World.Gizmo']])
        run = read_json(self.book.path('tutorials/gpu/debug-drawing/exercise-3.stamp.json'))['runs'][0]
        self.assertEqual([result['suite'] for result in run['tests']], ['Architecture.Layering', 'World.Gizmo'])

    def test_a_file_without_stages_on_a_patched_chain_is_run_by_patch(self):
        # rulings-9.md, R41: gpu/debug-drawing's file, without stages or patch, starts from world/tutorial-component; run
        # skips it (its chain changes the engine), so patch runs it on the chain's patched engine with the suites of the
        # chain's last patch tutorial, and at a release pin it needs no package run.
        self.book.write('src/content/docs/gpu/debug-drawing.md', '---\nkind: internals\n---\n')
        self.write_tutorial({'page': 'gpu/debug-drawing', 'startsFrom': {'tutorial': 'world/tutorial-component'}}, 'gpu/debug-drawing')
        _, output = self.check()
        self.assertIn('tutorials/gpu/debug-drawing.stamp.json does not exist: run it with python -I tools/tutorials.py patch '
                      'gpu/debug-drawing', output)
        code, output = self.run_tool('gpu/debug-drawing')
        self.assertEqual(code, 0, output)
        self.assertIn('passed: gpu/debug-drawing: tutorials/world/tutorial-component.patch, 2 doctest suites and the feature test', output)
        self.assertTrue(self.clean())
        run = read_json(self.book.path('tutorials/gpu/debug-drawing.stamp.json'))['runs'][0]
        self.assertEqual([result['suite'] for result in run['tests']], ['Architecture.Layering', 'World.WindZone'])
        self.assertEqual(sorted(run['inputs']), ['tutorials/gpu/debug-drawing.tutorial.json', 'tutorials/world/tutorial-component.patch',
                                                 'tutorials/world/tutorial-component.tutorial.json'])
        layout = tutorials.repo.Layout(self.book.root)
        book = tutorials.Book(layout)
        item = book.by_key['gpu/debug-drawing']
        self.assertTrue(book.changes_engine(item))
        self.assertEqual(tutorial_files.stamp_problems(layout, item, {'commit': self.pin, 'prerelease': False}, changes_engine=True), [])
        _, output = self.check()
        self.assertNotIn('gpu/debug-drawing.stamp.json', output)

    def test_what_fails_a_patch_run(self):
        self.outputs['test-World.WindZone'] = (0, '[doctest] test cases:  0 |  0 passed | 0 failed | 0 skipped', '')
        code, output = self.run_tool()
        self.assertEqual(code, 1, output)
        self.assertIn('StrataTests --test-suite=World.WindZone ran no test case: no suite World.WindZone is in the build', output)
        self.assertTrue(self.clean())
        self.outputs = {'ctest-feature-test': (0, 'No tests were found!!!', '')}
        code, output = self.run_tool()
        self.assertIn('ctest -R "^StrataTests\\.FeatureTest$" found no test', output)
        self.outputs = {'build': (1, 'Wind.h(3): error C2011: redefinition', '')}
        code, output = self.run_tool()
        self.assertIn('the build of StrataTests exited with 1: Wind.h(3): error C2011: redefinition', output)
        self.assertFalse(read_json(self.book.path('tutorials/world/tutorial-component.stamp.json'))['runs'][0]['passed'])
        self.book.write('tutorials/world/tutorial-component.patch', c_Patch.replace('struct Wind {};', 'struct Gust {};'))
        code, output = self.run_tool()
        self.assertIn('tutorials/world/tutorial-component.patch does not apply to the pin', output)
        self.assertTrue(self.clean())
        # A revert that fails leaves the clone dirty and stops the run.
        self.book.write('tutorials/world/tutorial-component.patch', c_Patch)
        self.outputs = {}
        code, output = self.run_tool(revert_fails=True)
        self.assertEqual(code, 2, output)
        self.assertIn('the clone stays dirty, and every tool\'s preflight refuses it until a person restores it', output)
        self.engine.git('checkout', '--', '.')

    def test_every_failure_of_a_patch_run_says_what_to_do(self):
        cases = [
            ({'configure': (1, 'CMake Error at Strata/CMakeLists.txt:12', '')},
             'exited with 1: CMake Error at Strata/CMakeLists.txt:12', 'correct what the log names, a CMake file the patches change or a tool'),
            ({'build': (1, 'Wind.h(3): error C2011: redefinition', '')},
             'the build of StrataTests exited with 1: Wind.h(3): error C2011', 'correct the patch until the engine builds, with warnings as errors'),
            ({'test-World.WindZone': (1, '[doctest] test cases:  3 |  2 passed | 1 failed | 0 skipped', '')},
             'StrataTests --test-suite=World.WindZone exited with 1', 'correct the patch until the suite passes'),
            ({'test-World.WindZone': (0, '[doctest] test cases:  0 |  0 passed | 0 failed | 0 skipped', '')},
             'StrataTests --test-suite=World.WindZone ran no test case', 'name in patch.tests only suites that the patch or the pin declares'),
            ({'ctest-feature-test': (0, 'No tests were found!!!', '')},
             'found no test', 'STRATA_WITH_PHYSICS, STRATA_WITH_AUDIO and STRATA_WITH_ANIMATION on'),
            ({'ctest-feature-test': (8, '0% tests passed, 1 tests failed out of 1', '')},
             'ctest -R "^StrataTests\\.FeatureTest$" exited with 8', 'also adds its feature-test exercise'),
        ]
        for outputs, fault, remedy in cases:
            with self.subTest(fault=fault):
                shutil.rmtree(self.build_dir, ignore_errors=True)
                self.outputs = outputs
                code, output = self.run_tool()
                self.assertEqual(code, 1, output)
                self.assertIn('tutorials/world/tutorial-component.tutorial.json:1: failed: world/tutorial-component: ', output)
                self.assertIn(fault, output)
                self.assertIn(remedy, output)
                self.assertTrue(self.clean())

    def test_the_build_folder_is_never_the_pin_builds(self):
        self.build_dir = os.path.join(self.engine.root, 'build', 'windows')
        code, output = self.run_tool()
        self.assertEqual(code, 2)
        self.assertIn('is the pin build\'s folder, which never holds patched code', output)
        self.build_dir = os.path.join(tempfile.gettempdir(), 'elsewhere')
        code, output = self.run_tool()
        self.assertEqual(code, 2)
        self.assertIn('is not a folder build/<name> of the clone', output)


class TimeStepTests(unittest.TestCase):
    def test_a_replaced_file_waits_until_it_is_newer_than_the_build(self):
        project = tempfile.mkdtemp(prefix='project-')
        try:
            output = os.path.join(project, '.strata', 'Scripts', 'Build', 'Spinner.obj')
            os.makedirs(os.path.dirname(output))
            target = os.path.join(project, 'Spinner.cpp')
            for path in (output, target):
                open(path, 'w').close()
            os.utime(target, (1800000000.0, 1800000000.0))
            os.utime(output, (1800000010.0, 1800000010.0))
            slept = []
            tutorials.wait_past_outputs(project, target, slept.append, clock=lambda: 1800000010.5)
            self.assertAlmostEqual(slept[0], 1.6, places=3)
            slept = []
            tutorials.wait_past_outputs(project, target, slept.append, clock=lambda: 1800000020.0)
            self.assertEqual(slept, [])
        finally:
            shutil.rmtree(project, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
