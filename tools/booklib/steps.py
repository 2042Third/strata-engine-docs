"""Command steps as the engine's command-script runner runs them, plus the book's own key entityName (plan/pipelines.md
§5.2 and §6.3): what figures.py take and tutorials.py run send to an editor through StrataCLI call.

The rules are the runner's at 822a7a46 (StrataEditor/src/Editor/EditorCommandRunner.h:74-98 and
EditorCommandRunner.cpp):

- a step is {"command", "parameters", "expect", "bind", "until"} (all but "command" optional);
- "expect" maps JSON pointers into the result ("" is the whole result) to {"equals": value, "min": n, "max": n};
  "equals" compares JSON values as nlohmann::json does (a boolean is never a number, 1 equals 1.0), "min" and "max"
  need a number;
- "bind" names values of the result, {"name": "/id"}, which later parameters use as {"$ref": "name"} or
  {"$ref": "name", "pointer": "/entities/0"};
- "until" {"steps": n, "seconds": s} repeats a query until its expect holds: one more fixed step between attempts in
  a paused game, one frame otherwise; it fails after n fixed steps (counted by play.state's fixedSteps) or s seconds
  (300 when only steps are given, c_DefaultUntilSeconds). A failing answer (CommandFailed: asset.info of an asset still
  being imported) is asked again like an unmet expect, and the step fails with the last error when until runs out; the
  engine's runner stops at a failing answer (EditorCommandRunner.cpp, JudgeUntilAttempt), so a reader's copy never
  needs this.

entityName (the book's key) becomes entity.find {name}, which must match exactly one entity, and that entity is passed
as the step's "entity" parameter. A step that would change the person's preferences is refused (plan/pipelines.md §2).
"""

import json
import time

c_ScriptKeys = ('command', 'parameters', 'expect', 'bind', 'until')
c_RefusedCommands = ('preferences.set', 'preferences.save')
c_DefaultUntilSeconds = 300.0  # EditorCommandRunner.h:135
c_MaxUntilSteps = 10000000  # EditorCommandRunner.h:136
c_MaxUntilSeconds = 24.0 * 60.0 * 60.0  # EditorCommandRunner.h:137
c_ExpectRemedy = 'correct the steps before it, or the value its expect asks for'


class StepError(Exception):
    """A step failed, or its result does not meet what the step expects."""


class CommandFailed(Exception):
    """The editor answered a command with an error (booklib.editor.CommandError is one), as opposed to an editor that
    gave no answer: until asks again after it."""


def parse_pointer(pointer):
    """The reference tokens of a JSON pointer (RFC 6901: "" or "/token/…", "~0" for "~" and "~1" for "/"), or None when it
    is malformed, as the engine's ParseJsonPointer reads it."""
    if not isinstance(pointer, str):
        return None
    if pointer == '':
        return []
    if not pointer.startswith('/'):
        return None
    tokens = []
    for raw in pointer[1:].split('/'):
        token = ''
        index = 0
        while index < len(raw):
            char = raw[index]
            if char != '~':
                token += char
                index += 1
                continue
            if index + 1 >= len(raw) or raw[index + 1] not in '01':
                return None
            token += '~' if raw[index + 1] == '0' else '/'
            index += 2
        tokens.append(token)
    return tokens


def resolve_pointer(value, pointer):
    """The value a JSON pointer names inside value; KeyError when there is none. Array indices are decimal numbers
    without leading zeros (the engine's ResolveJsonPath)."""
    tokens = parse_pointer(pointer)
    if tokens is None:
        raise KeyError(pointer)
    for token in tokens:
        if isinstance(value, dict):
            if token not in value:
                raise KeyError(pointer)
            value = value[token]
            continue
        if not isinstance(value, list) or not token.isdigit() or not token.isascii() or len(token) > 9 \
                or (len(token) > 1 and token[0] == '0') or int(token) >= len(value):
            raise KeyError(pointer)
        value = value[int(token)]
    return value


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def json_equal(left, right):
    """Equality of two JSON values as nlohmann::json compares them: types matter (true is not 1), numbers compare by
    value (1 equals 1.0), objects by their members, arrays element by element."""
    if is_number(left) and is_number(right):
        return left == right
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(json_equal(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(json_equal(a, b) for a, b in zip(left, right))
    if type(left) is not type(right):
        return False
    return left == right


def is_reference(value):
    """True for {"$ref": "<name>"} and {"$ref": "<name>", "pointer": "<pointer>"} (EditorCommandScript::IsReference)."""
    if not isinstance(value, dict) or not isinstance(value.get('$ref'), str):
        return False
    return len(value) == 1 or (len(value) == 2 and isinstance(value.get('pointer'), str))


def references(value):
    """The names of every $ref inside a value, in document order."""
    if is_reference(value):
        return [value['$ref']]
    if isinstance(value, dict):
        return [name for item in value.values() for name in references(item)]
    if isinstance(value, list):
        return [name for item in value for name in references(item)]
    return []


def substitute(value, bound):
    """The value with every $ref replaced by what an earlier step bound."""
    if is_reference(value):
        if value['$ref'] not in bound:
            raise StepError('$ref "%s" names no value bound earlier: bind it in an earlier step' % value['$ref'])
        found = bound[value['$ref']]
        if 'pointer' not in value:
            return found
        try:
            return resolve_pointer(found, value['pointer'])
        except KeyError:
            raise StepError('$ref "%s" with pointer %s: the bound value has nothing there: point into the value it binds'
                            % (value['$ref'], value['pointer']))
    if isinstance(value, dict):
        return {key: substitute(item, bound) for key, item in value.items()}
    if isinstance(value, list):
        return [substitute(item, bound) for item in value]
    return value


def unmet_expectation(command, result, pointer, expectation):
    """Why the result does not meet one expectation, as (what is wrong, what to do), or None (the engine's
    CheckExpectations). The second is c_ExpectRemedy when the value is there and not the one expected."""
    try:
        value = resolve_pointer(result, pointer)
    except KeyError:
        return '%s: expect %s: the result has no such value' % (command, pointer), 'expect a pointer the result has'
    if 'equals' in expectation and not json_equal(value, expectation['equals']):
        return '%s: %s is %s, not %s' % (command, pointer, json.dumps(value), json.dumps(expectation['equals'])), c_ExpectRemedy
    if 'min' in expectation and not (is_number(value) and value >= expectation['min']):
        return '%s: %s is %s, below %s' % (command, pointer, json.dumps(value), expectation['min']), c_ExpectRemedy
    if 'max' in expectation and not (is_number(value) and value <= expectation['max']):
        return '%s: %s is %s, above %s' % (command, pointer, json.dumps(value), expectation['max']), c_ExpectRemedy
    return None


def check_expectation(command, result, pointer, expectation):
    unmet = unmet_expectation(command, result, pointer, expectation)
    if unmet:
        raise StepError('%s: %s' % unmet)


def check_expectations(command, result, expect):
    for pointer, expectation in (expect or {}).items():
        check_expectation(command, result, pointer, expectation)


def find_entity(session, name):
    """The ID of the one entity named name (entity.find {name}); StepError unless exactly one matches."""
    found = session.call('entity.find', {'name': name})
    entities = found.get('entities', []) if isinstance(found, dict) else []
    if len(entities) != 1:
        raise StepError('entityName "%s" matches %d entities; it must match exactly one: name an entity the scene has at this step, '
                        'under a name no other entity has' % (name, len(entities)))
    entity = entities[0]
    return entity.get('id', entity) if isinstance(entity, dict) else entity


def step_parameters(session, step, bound):
    """The parameters a step sends: its $refs substituted and its entityName found."""
    parameters = substitute(step.get('parameters') or {}, bound)
    if 'entityName' in step:
        parameters['entity'] = find_entity(session, step['entityName'])
    return parameters


def run_step(session, step, bound):
    """Runs one step: (parameters sent, result). Checks expect, then binds; raises StepError or the session's error."""
    if step.get('command') in c_RefusedCommands:
        raise StepError('%s changes the person\'s preferences, which no tool does (pipelines.md §2): use a project setting' % step['command'])
    parameters = step_parameters(session, step, bound)
    result = until_met(session, step, parameters) if 'until' in step else session.call(step['command'], parameters)
    check_expectations(step['command'], result, step.get('expect'))
    for name, pointer in (step.get('bind') or {}).items():
        try:
            bound[name] = resolve_pointer(result, pointer)
        except KeyError:
            raise StepError('%s: bind %s: the result has no %s: bind a pointer the result has' % (step['command'], name, pointer))
    return parameters, result


def run_steps(session, steps, bound):
    """Runs command steps in order, as the engine's runner does, stopping at the first that fails."""
    for step in steps:
        run_step(session, step, bound)


def until_met(session, step, parameters, clock=time.monotonic):
    """The result of a query asked until its expect holds, within until's fixed steps (counted by play.state's
    fixedSteps) and seconds (c_DefaultUntilSeconds unless given). A failing answer is asked again; when until runs out
    after one, the step fails with that error."""
    until = step['until']
    if not step.get('expect'):
        raise StepError('%s: a step with until is a query with an expect: add the expect it waits for' % step['command'])
    deadline = clock() + until.get('seconds', c_DefaultUntilSeconds)
    start_steps = None
    while True:
        failure = None
        unmet = None
        try:
            result = session.call(step['command'], parameters)
            unmet = next((reason for pointer, expectation in step['expect'].items()
                          for reason in [unmet_expectation(step['command'], result, pointer, expectation)] if reason), None)
            if unmet is None:
                return result
        except CommandFailed as error:
            failure = error
        state = session.call('play.state', {})
        steps_now = state.get('fixedSteps', 0) if isinstance(state, dict) else 0
        if not isinstance(steps_now, int) or isinstance(steps_now, bool):
            steps_now = 0
        start_steps = steps_now if start_steps is None else start_steps
        if ('steps' in until and steps_now - start_steps >= until['steps']) or clock() >= deadline:
            if failure is not None:
                raise StepError('%s: until ran out, and its last answer was an error: %s: give until more steps or seconds, or correct '
                                'the steps before it' % (step['command'], failure))
            raise StepError('%s: until ran out: %s: %s' % (step['command'], unmet[0], 'give until more steps or seconds, or ' + unmet[1]
                                                           if unmet[1] == c_ExpectRemedy else unmet[1]))
        if isinstance(state, dict) and state.get('paused'):
            session.call('play.step', {'steps': 1})
        else:
            session.call('editor.wait', {'frames': 1})
