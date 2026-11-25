"""booklib/steps.py: the command step rules of the engine's command-script runner (StrataEditor/src/Editor/
EditorCommandRunner.h:74-98) that tools/figures.py take and tools/tutorials.py run share: JSON pointers, equality,
bindings, expectations and until."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
from booklib import steps  # noqa: E402


class FakeSession:
    def __init__(self, answers):
        self.answers = answers
        self.calls = []

    def call(self, command, parameters=None, timeout=None):
        self.calls.append((command, parameters))
        answer = self.answers[command]
        return answer(parameters) if callable(answer) else answer


class StepsTests(unittest.TestCase):
    def test_pointers_and_equality_as_the_engine_reads_them(self):
        value = {'a/b': [10, {'~x': 1}], 'list': [1, 2]}
        self.assertEqual(steps.resolve_pointer(value, '/a~1b/1/~0x'), 1)
        self.assertEqual(steps.resolve_pointer(value, ''), value)
        for pointer in ('/list/01', '/list/2', 'list', '/a~2b'):
            with self.assertRaises(KeyError):
                steps.resolve_pointer(value, pointer)
        self.assertTrue(steps.json_equal(1, 1.0))
        self.assertFalse(steps.json_equal(True, 1))
        self.assertFalse(steps.json_equal([1, 2], [1]))
        self.assertTrue(steps.is_reference({'$ref': 'x', 'pointer': '/0'}))
        self.assertFalse(steps.is_reference({'$ref': 'x', 'other': 1}))

    def test_bindings_and_expectations(self):
        session = FakeSession({'entity.create': {'id': 'AB'}, 'component.get': {'values': {'Speed': 2}}})
        bound = {}
        steps.run_step(session, {'command': 'entity.create', 'bind': {'made': '/id'}}, bound)
        steps.run_step(session, {'command': 'component.get', 'parameters': {'entity': {'$ref': 'made'}},
                                 'expect': {'/values/Speed': {'min': 1, 'max': 3}}}, bound)
        self.assertEqual(session.calls[1], ('component.get', {'entity': 'AB'}))
        with self.assertRaisesRegex(steps.StepError, r'^component\.get: /values/Speed is 2, not 3: correct the steps before it, or the '
                                                     r'value its expect asks for$'):
            steps.run_step(session, {'command': 'component.get', 'expect': {'/values/Speed': {'equals': 3}}}, bound)
        with self.assertRaisesRegex(steps.StepError, r'^component\.get: /values/Speed is 2, below 5: correct the steps before it'):
            steps.run_step(session, {'command': 'component.get', 'expect': {'/values/Speed': {'min': 5}}}, bound)
        with self.assertRaisesRegex(steps.StepError, r'^component\.get: expect /values/Size: the result has no such value: expect a '
                                                     r'pointer the result has$'):
            steps.run_step(session, {'command': 'component.get', 'expect': {'/values/Size': {'equals': 3}}}, bound)
        with self.assertRaisesRegex(steps.StepError, r'names no value bound earlier'):
            steps.run_step(session, {'command': 'component.get', 'parameters': {'entity': {'$ref': 'other'}}}, bound)
        with self.assertRaisesRegex(steps.StepError, r'changes the person\'s preferences'):
            steps.run_step(session, {'command': 'preferences.save'}, bound)

    def test_until_steps_a_paused_game_and_waits_frames_otherwise(self):
        state = {'steps': 0, 'paused': True}

        def play_state(_):
            return {'fixedSteps': state['steps'], 'paused': state['paused']}

        def step(parameters):
            state['steps'] += parameters['steps']
            return {}
        session = FakeSession({'play.state': play_state, 'play.step': step, 'editor.wait': {}})
        steps.run_step(session, {'command': 'play.state', 'until': {'steps': 10}, 'expect': {'/fixedSteps': {'min': 3}}}, {})
        self.assertEqual(state['steps'], 3)
        with self.assertRaisesRegex(steps.StepError, r'^play\.state: until ran out: play\.state: /fixedSteps is 5, below 100: give until '
                                                     r'more steps or seconds, or correct the steps before it, or the value its expect asks for$'):
            steps.run_step(session, {'command': 'play.state', 'until': {'steps': 2}, 'expect': {'/fixedSteps': {'min': 100}}}, {})
        with self.assertRaisesRegex(steps.StepError, r'^play\.state: until ran out: play\.state: expect /frames: the result has no such '
                                                     r'value: expect a pointer the result has$'):
            steps.run_step(session, {'command': 'play.state', 'until': {'steps': 1}, 'expect': {'/frames': {'min': 1}}}, {})
        state['paused'] = False
        clock = iter([0.0, 0.0, 0.5, 2.0])
        with self.assertRaisesRegex(steps.StepError, r'until ran out'):
            steps.until_met(session, {'command': 'play.state', 'until': {'seconds': 1}, 'expect': {'/fixedSteps': {'min': 100}}}, {},
                            clock=lambda: next(clock))
        self.assertIn(('editor.wait', {'frames': 1}), session.calls)

    def test_until_asks_again_through_failing_answers(self):
        # asset.info of a file being imported fails until the asset exists: until asks again until it answers.
        attempts = []

        def info(_):
            attempts.append(1)
            if len(attempts) < 3:
                raise steps.CommandFailed("asset.info failed (StrataCLI exit code 1): Parameter 'asset': no asset 'Coin.glb'")
            return {'imported': True}
        answers = {'asset.info': info, 'play.state': {'fixedSteps': 0, 'paused': False}, 'editor.wait': {}}
        step = {'command': 'asset.info', 'parameters': {'asset': 'Coin.glb'}, 'until': {'seconds': 60}, 'expect': {'/imported': {'equals': True}}}
        steps.run_step(FakeSession(answers), step, {})
        self.assertEqual(len(attempts), 3)

        # Out of time, the step fails with the last error.
        def never(_):
            raise steps.CommandFailed("asset.info failed (StrataCLI exit code 1): Parameter 'asset': no asset 'Coin.glb'")
        answers['asset.info'] = never
        clock = iter([0.0, 0.5, 2.0])
        with self.assertRaisesRegex(steps.StepError, r"^asset\.info: until ran out, and its last answer was an error: asset\.info failed "
                                                     r"\(StrataCLI exit code 1\): Parameter 'asset': no asset 'Coin\.glb': give until more "
                                                     r"steps or seconds, or correct the steps before it$"):
            steps.until_met(FakeSession(answers), dict(step, until={'seconds': 1}), {}, clock=lambda: next(clock))

        # An editor that is gone gave no answer: the step ends at once.
        def lost(_):
            raise RuntimeError('the editor is gone')
        answers['asset.info'] = lost
        with self.assertRaisesRegex(RuntimeError, 'the editor is gone'):
            steps.run_step(FakeSession(answers), step, {})

    def test_an_entity_name_matches_exactly_one_entity(self):
        for found in ([], [{'id': 'A1'}, {'id': 'B2'}]):
            session = FakeSession({'entity.find': {'entities': found}, 'component.get': {}})
            with self.assertRaisesRegex(steps.StepError, r'^entityName "Cube" matches %d entities; it must match exactly one: name an entity '
                                                         r'the scene has at this step, under a name no other entity has$' % len(found)):
                steps.run_step(session, {'command': 'component.get', 'entityName': 'Cube'}, {})
        session = FakeSession({'entity.find': {'entities': [{'id': 'A1'}]}, 'component.get': {}})
        self.assertEqual(steps.run_step(session, {'command': 'component.get', 'entityName': 'Cube'}, {})[0], {'entity': 'A1'})

if __name__ == '__main__':
    unittest.main()
