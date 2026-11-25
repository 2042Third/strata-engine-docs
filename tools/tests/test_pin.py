"""pin.py (plan/pipelines.md §10): show, report and move against a small engine with history."""

import contextlib
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import pin
from booklib import repo

c_Source = '// One step.\nvoid Scene::Step()\n{\n\tTick();\n}\n'
c_Shots = {'Projects': {'ThirdPerson': {'Sample': 'ThirdPerson'}}, 'Shots': [
    {'Name': 'tp.scene', 'Project': 'ThirdPerson', 'Camera': 'scene'},
    {'Name': 'tp.dof', 'Project': 'ThirdPerson', 'Camera': 'scene', 'Setup': [{'Command': 'component.set', 'Parameters': {'entity': '350D7DDD7ED21DD5'}}]}]}


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = function(list(arguments))
    return code, output.getvalue()


class PinTests(unittest.TestCase):
    def setUp(self):
        self.engine = helpers.TempEngine()
        self.first = self.engine.commit({'Strata/src/Scene.cpp': c_Source, 'Tools/LookDev/Shots.json': json.dumps(c_Shots), 'Tools/PerfLock.py': '# lock\n'})
        self.book = helpers.TempBook(self.first)
        self.book.page('core/time', helpers.frontmatter() + '\n```cpp src="Strata/src/Scene.cpp#L1-L5"\n// One step.\nvoid Scene::Step()\n{\n\tTick();\n}\n```\n' + helpers.c_BottomStrip)
        self.book.write('src/content/figures/core/time.json', json.dumps({'figures': [
            {'id': 'shot', 'shows': 'The island from the scene camera.', 'caption': 'The island in the sky.', 'alt': 'An island in the sky.', 'kind': 'scene',
             'project': {'sample': 'ThirdPerson'}, 'shot': 'tp.scene'},
            {'id': 'blur', 'shows': 'The robot sharp before a blurred sky.', 'caption': 'The robot in focus.', 'alt': 'A robot before a blurred sky.', 'kind': 'scene',
             'project': {'sample': 'ThirdPerson'}, 'shot': 'tp.dof'},
            {'id': 'help', 'shows': 'The help of the command-line client.', 'caption': 'The help of StrataCLI.', 'alt': 'The text StrataCLI prints.', 'kind': 'text',
             'text': {'program': 'StrataCLI', 'arguments': ['--help']}}]}))
        self.book.write('tutorials/core/time.tutorial.json', json.dumps({'page': 'core/time', 'startsFrom': {'pin': True},
                                                                        'patch': {'file': 'tutorials/core/time.patch', 'tests': []}}))
        self.book.write('tutorials/core/time.patch', '--- a/Strata/src/Scene.cpp\n+++ b/Strata/src/Scene.cpp\n@@ -3,3 +3,3 @@\n {\n-\tTick();\n+\tTick(2);\n }\n')

    def tearDown(self):
        self.book.cleanup()
        self.engine.cleanup()

    def run_tool(self, *arguments):
        return quiet(pin.main, *(list(arguments) + ['--root', self.book.root, '--engine', self.engine.root]))

    def test_show(self):
        code, output = quiet(pin.main, 'show', '--root', self.book.root)
        self.assertEqual(code, 0)
        self.assertEqual(output, 'commit %s\nrelease 0.8.0 (pre-release)\nrepository https://github.com/2042Third/GameEngine\n' % self.first)

    def test_report_at_the_pin_lists_the_runs_to_do_and_what_needs_a_person(self):
        code, output = self.run_tool('report')
        self.assertIn('1. quotes: 1 same', output)
        self.assertIn('tutorial to run again: tutorials/core/time.tutorial.json', output)
        self.assertIn('2. tutorials: 1 of 1 to run again', output)
        self.assertIn('picture to take again: shot (never taken)', output)
        self.assertIn('text figure to take again: help', output)
        self.assertIn('blur reuses the shot tp.dof, which names entities by ID', output)
        self.assertIn('6. no engine file the tools depend on changed', output)
        self.assertNotIn('no longer applies', output)
        self.assertIn('4. W8 light/local-shadows: not written yet', output)
        self.assertEqual(code, 1)  # the shot that names entities by ID needs a person
        # A stamp that passed at the pin is current.
        self.book.write('tutorials/core/time.stamp.json', json.dumps({'page': 'core/time', 'runs': [{'engineCommit': self.first, 'passed': True}]}))
        self.assertIn('2. tutorials: 0 of 1 to run again', self.run_tool('report')[1])

    def test_a_stacked_patch_is_applied_after_its_chain(self):
        # core/later builds on core/time, and the engine exercise of core/time on its patch: alone, neither applies.
        self.book.write('tutorials/core/later.tutorial.json', json.dumps({'page': 'core/later', 'startsFrom': {'tutorial': 'core/time'},
                                                                         'patch': {'file': 'tutorials/core/later.patch', 'tests': []}}))
        self.book.write('tutorials/core/later.patch', '--- a/Strata/src/Scene.cpp\n+++ b/Strata/src/Scene.cpp\n@@ -3,3 +3,3 @@\n {\n-\tTick(2);\n+\tTick(3);\n }\n')
        self.book.write('tutorials/core/time/exercise-1.patch', '--- a/Strata/src/Scene.cpp\n+++ b/Strata/src/Scene.cpp\n@@ -3,3 +3,3 @@\n {\n-\tTick(2);\n+\tTick(4);\n }\n')
        objects = sorted(os.listdir(os.path.join(self.engine.root, '.git', 'objects')))
        code, output = self.run_tool('report')
        self.assertNotIn('no longer applies', output)
        self.assertNotIn('is not checked', output)
        # The clone keeps its index and its objects: the chain is applied in a scratch index and object folder.
        self.assertEqual(sorted(os.listdir(os.path.join(self.engine.root, '.git', 'objects'))), objects)
        # A chain that breaks at its first patch reports that patch once, and the patches after it as not checked.
        moved = self.engine.commit({'Strata/src/Scene.cpp': c_Source.replace('Tick();', 'Tock();')})
        code, output = self.run_tool('report', '--to', moved)
        self.assertEqual(output.count('the patch tutorials/core/time.patch no longer applies at %s' % moved[:12]), 1, output)
        self.assertIn('the patch tutorials/core/later.patch is not checked: tutorials/core/time.patch, which its chain applies before it, no '
                      'longer applies', output)
        self.assertIn('the patch tutorials/core/time/exercise-1.patch is not checked', output)
        # A patch of the chain that fails after the earlier ones applied names them.
        self.book.write('tutorials/core/later.patch', '--- a/Strata/src/Scene.cpp\n+++ b/Strata/src/Scene.cpp\n@@ -3,3 +3,3 @@\n {\n-\tTick(5);\n+\tTick(3);\n }\n')
        code, output = self.run_tool('report')
        self.assertIn('the patch tutorials/core/later.patch no longer applies at %s after tutorials/core/time.patch (' % self.first[:12], output)

    def test_report_of_a_move(self):
        moved = self.engine.commit({'Strata/src/Scene.cpp': '// New.\n\n' + c_Source.replace('Tick();', 'Tock();'),
                                    'Tools/LookDev/Shots.json': json.dumps({'Projects': c_Shots['Projects'], 'Shots': [
                                        {'Name': 'tp.scene', 'Project': 'ThirdPerson', 'Camera': 'scene', 'AntiAliasing': ['off']}]}),
                                    'Tools/PerfLock.py': '# a new lock\n'})
        code, output = self.run_tool('report', '--to', moved)
        self.assertEqual(code, 1)
        self.assertIn('changed: Strata/src/Scene.cpp#L1-L5', output)
        self.assertIn('the patch tutorials/core/time.patch no longer applies at %s' % moved[:12], output)
        self.assertIn('): make it again against the new pin', output)
        self.assertIn('shot reuses the shot tp.scene, whose AntiAliasing changed: judge its picture again', output)
        self.assertIn('blur: the shot tp.dof is gone from Shots.json at %s: choose another shot' % moved[:12], output)
        self.assertIn('6. Tools/PerfLock.py changed between the pins', output)
        self.assertEqual(repo.read_pin(self.book.path('engine.pin'))['commit'], self.first)  # report writes nothing

    def test_move_writes_the_pin_with_its_header_and_moves_the_quotes(self):
        moved = self.engine.commit({'Strata/src/Scene.cpp': '// New.\n\n' + c_Source})
        code, output = self.run_tool('move', moved, '--release', '0.8.1', '--prerelease', 'no')
        self.assertIn('moved: Strata/src/Scene.cpp#L1-L5 -> Strata/src/Scene.cpp#L3-L7', output)
        self.assertIn('pin: engine.pin now names %s' % moved, output)
        self.assertEqual(code, 1)  # tp.dof names entities by ID
        text = self.book.read('engine.pin')
        self.assertTrue(text.startswith(repo.c_PinHeader))
        values = repo.read_pin(self.book.path('engine.pin'))
        self.assertEqual((values['commit'], values['release'], values['prerelease']), (moved, '0.8.1', False))
        self.assertIn('src="Strata/src/Scene.cpp#L3-L7"', self.book.read('src/content/docs/core/time.md'))
        with self.assertRaises(SystemExit) as caught, contextlib.redirect_stderr(io.StringIO()):
            pin.main(['move', moved, '--release', 'one', '--root', self.book.root, '--engine', self.engine.root])
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual(self.run_tool('move', 'no-such-commit')[0], 2)

    def test_movable_claims_of_the_w8_pages(self):
        self.book.write('plan/notes/core/time.md', '# Notes\n\n## Movable claims\n\n- the shadowed lights: 8 (Strata/src/Light.cpp:12)\n\n## Requests\n\n- none\n')
        self.assertEqual(pin.movable_claims(repo.Layout(self.book.root), 'core/time'), ['- the shadowed lights: 8 (Strata/src/Light.cpp:12)'])
        self.book.write('plan/notes/core/time.md', '# Notes\n')
        self.assertIsNone(pin.movable_claims(repo.Layout(self.book.root), 'core/time'))
        marks = type('Marks', (), {'w8_pages': ['core/time'], 'w8r_pages': []})()
        engine = repo.Engine(self.engine.root)
        try:
            report = pin.report_move(repo.Layout(self.book.root), engine, self.first, self.first, False, book=marks)
        finally:
            engine.close()
        self.assertTrue(any('W8 core/time: plan/notes/core/time.md has no "## Movable claims" section' in line for line in report.book))
        self.assertGreater(report.person, 0)


if __name__ == '__main__':
    unittest.main()
