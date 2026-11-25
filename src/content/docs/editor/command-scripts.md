---
id: editor/command-scripts
title: "Command scripts and batches"
description: "How a JSON file of editor commands runs without a window, checks each answer, names values for later steps, waits for a condition and fails with an exit code."
kind: internals
size: M
tracks: [E]
needs: [editor/stepping]
time: 70
learn:
  - id: write-script
    text: write a command script that creates an entity, binds its id, refers to it later and checks a result with expect
  - id: until-exact
    text: explain why an until step in a paused game waits for an exact number of fixed steps on any machine
  - id: batch-rules
    text: name what editor.batch refuses before it runs and what an atomic batch does when a step fails
  - id: exit-code
    text: trace a failed expect from the script's check to the exit code 1 of the editor
  - id: run-headless
    text: run a command script with the editor's command line options and read its result in the terminal
since: 0.3.0
status: final
---

Someone will change a command tomorrow, and nobody wants to click through the editor to learn what broke. Strata keeps such a check as a file: a list of commands, each with the
answer it must give. The editor runs the file without a window and ends with a code that says whether every answer was
right. This page shows the format, how the editor runs it, and the batch that runs a short list as one :term[undo step]{id=undo-step}. It
omits the journal, the test suites that run scripts, and the scripts of a game's own logic.

## The problem and how engines solve it

Take a simple wish. You add a command that moves an entity, and you want proof that after sixty steps of physics a
falling ball is about five metres lower. A person can check it once: open a project, create a ball, press play, wait,
read the number. A person cannot check it after every change, on every machine, for a year. A program has to run the
check and judge it.

Engines meet this wish in a few ways, and each costs something.

- **A test written in the engine's language.** It is fast and reaches everything, but it needs a build for each new
  check, and only programmers write it.
- **A recording of the mouse and keyboard.** Anyone can make it, but it breaks when a button moves, and it cannot say
  which answer was wrong.
- **A script in an embedded language.** It can loop and branch, but it brings an interpreter, new bugs and the chance of
  a check that never ends.
- **A data file of commands.** It cannot loop or branch, but it needs nothing beyond the commands that exist, and a
  person, a test or an agent can write it.

Strata chose the data file. Every action of the editor is already a command with a name, parameters and a result (see
[Commands](commands.md)), so a check is a list of command calls plus the answers they must give. The cost is real: a
script cannot decide anything. It runs its steps in order, and a step that needs a value takes it from a name that an
earlier step bound. A file of data can also be written by a tool, and produced from a recorded session, as the last part
of this page shows.

## The map

A command script is read once, checked, and then run one step per turn of the editor's :term[frame loop]{id=game-loop}. The diagram shows the
parts and what each one owns.

```mermaid caption="A script file is checked as a whole, then run step by step; a failed step marks the script, and the editor layer turns the mark into the exit code." alt="A flow of boxes. A script file goes to a loader that checks every step. The script object hands one step at a time to the command runner, which runs the command and returns its result. At the end the editor layer sets the exit code from the failed mark. The batch command reaches the same script object and an undo group."
flowchart LR
	File["script file (JSON array)"] --> Load["EditorCommandScript::FromJson<br/>checks every step and name"]
	Load --> Script["EditorCommandScript<br/>one step per frame"]
	Script --> Runner["EditorCommandRunner<br/>holds a pending command"]
	Runner --> Registry["command registry<br/>runs the command"]
	Registry -->|"result"| Script
	Script -->|"finished, failed or not"| Layer["EditorLayer::UpdateCommandScript<br/>exit code 1 on failure"]
	Batch["editor.batch"] -->|"RunStepNow"| Script
	Batch --> Undo["UndoStack group"]
```

Four pieces matter. `EditorCommandScript` in `StrataEditor/src/Editor/EditorCommandRunner.h` holds the steps, the bound
values and the mark that says whether any step failed. `EditorCommandRunner` runs one command and holds it while it
waits for frames, and `EditorLayer` owns the script and asks it, once per frame, to continue. `editor.batch`, in
`StrataEditor/src/Editor/Commands/BatchCommands.cpp`, builds a script of its own and runs it inside one frame. All of it
runs on the :term[main thread]{id=main-thread}, as every editor command does.

## The contract: the format

A **command script** is a :term[JSON array]{id=json-array} of steps that the editor runs one after another, each step a command with its
parameters and the answers it must give. If JSON is new to you, [data formats](../basics/data-formats.md) teaches it. The
engine's own smoke test is the best first example. Look at a part of it, in which a crate is created and then changed.

```json src="StrataTests/Editor/SmokeCommands.json.in#L7-L11"
{ "command": "entity.create", "parameters": { "name": "Lamp", "components": { "PointLight": { "Intensity": 5, "Range": 8 } } } },
{ "command": "entity.create", "parameters": { "name": "Crate", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "Transform": { "Translation": [0, 0.5, 0] } } },
	"bind": { "crate": "/id" } },
{ "command": "component.set", "parameters": { "entity": { "$ref": "crate" }, "component": "Transform", "values": { "Rotation": [0, 30, 0] } } },
{ "command": "entity.create", "parameters": { "name": "Camera", "components": { "Camera": {}, "Transform": { "Translation": [0, 2, 6] } } } },
```

A step is an object with a `command` and, when the command needs them, `parameters`. The step that creates the `Crate`
also has `bind`, which the next section explains, and the step after it uses the crate. Only five keys are allowed in a
step: `command`, `parameters`, `expect`, `bind` and `until`. Any other key makes the whole file invalid, so a key with a
wrong letter cannot quietly check nothing.

A **JSON pointer** is a path into a JSON document. The pointer `/id` names the member `id` of a result, and
`/values/Translation/1` names the second number of the array `Translation` inside `values`. The empty string names the
whole result. Pointers are the way a script looks inside the answer of a command.

An **`expect`** is the key that lists what a step's result must hold: each member is a pointer, and its value is a
condition. A condition has `equals` (the value must be the same), `min` and `max` (a number in the closed range, one bound
alone is allowed). The smoke script has two such checks.

```json
{ "command": "editor.status", "expect": { "/editor/launcher": { "equals": false } } }
{ "command": "play.step", "parameters": { "steps": 2 }, "expect": { "/stepsRun": { "equals": 2 } } }
```

The first reads `launcher` inside `editor` and demands `false`. The second runs two :term[fixed steps]{id=fixed-step} (see
[Stepping](stepping.md)) and demands that `stepsRun` is 2. A result that misses a condition fails its step like a failed
command, and the log names the pointer and the value it found. A pointer with nothing behind it fails too, so a slip in a
pointer cannot pass by accident.

A failed step does not stop the script. The editor logs it, marks the script failed and runs the steps that follow, so
one run reports every broken answer, not only the first. The price is that later steps may fail from the same cause,
which the next section limits.

## The contract: names and waiting

A script often needs something an earlier step made. The id of the crate is new in every run, so the script cannot write
it down.

The step that makes the crate gives it a name with the key **`bind`** that maps a name to a pointer into that step's
result: `"bind": { "crate": "/id" }` stores the value at `/id` as `crate`.

A later step uses the name with **`$ref`** as an object `{ "$ref": "crate" }` that the bound value replaces anywhere in the
parameters, however deep. A reference may also take a `pointer` into the bound value, as in
`{ "$ref": "crate", "pointer": "/entities/0" }`.

Two rules keep references safe. `EditorCommandScript::FromJson` checks every reference when it reads the file: a name
that no earlier step binds makes the whole file invalid, and nothing runs. A binding can still lack a value at run time,
because the step that binds it failed or its result had nothing at the pointer. The runner then drops the name, and a
later step that uses it fails without running, as a call with invalid parameters. So no step ever runs with the value of
an older step that failed.

Some answers are not ready at once. A body that falls needs time, and a scene that loads needs frames. The key
**`until`** repeats a step until its `expect` holds, within bounds the step names: `{ "steps": 600 }` stops after 600
fixed steps of the game, and `{ "seconds": 5 }` after five seconds. One bound must stand at least. The seconds default to
300 and may not pass a day, and the steps may not pass 10,000,000.

The step must be a query, a command that only reads, because it runs many times. The editor checks this, with the
bounds, before the first step runs, and a script that fails the check does not start.

What does a wait cost in a paused game? Let the game be paused, and let a query count the fixed steps run; the step
expects at least 5. Attempt 1 sees 0 and misses, so the script runs exactly one fixed step before the next attempt.
Attempts 2 to 5 see 1, 2, 3 and 4. Attempt 6 sees 5 and meets the condition, after five fixed steps, whether the
machine draws 30 or 300 frames a second.

```cpp src="StrataEditor/src/Editor/EditorCommandRunner.cpp#L683-L706"
if (result.Success)
{
	unmet = CheckExpectations(result.Value, step.Expectations);
	if (!unmet.empty() && (!step.Until->Steps || stepsRun < *step.Until->Steps) && seconds < step.Until->Seconds)
	{
		// Not yet: the next attempt comes in a later frame, after one more fixed step while the game is paused.
		if (context.IsPlaying() && context.IsPaused() && !context.IsInputSequenceRunning())
		{
			if (!context.HasPendingSteps())
				context.Step(1);
			wait.StepTarget = context.GetFixedStepCount() + context.GetPendingSteps();
		}
		return false;
	}
}

// The final attempt is the step's one entry in the activity journal, with how many attempts it took.
CommandJournal& journal = context.GetJournal();
const uint64_t entry = journal.Begin(CommandOrigin { CommandSource::CommandScript }, step.Command, wait.Kind, wait.Results, wait.Parameters,
	context.IsPlaying());
EditorCommandResult recorded = result;
if (recorded.Value.is_object())
	recorded.Value["attempts"] = wait.Attempts;
journal.Complete(entry, recorded);
```

1. **Line 685:** a successful result is judged against the step's `expect`; a failed command is not.
2. **Lines 686–696:** a miss within both bounds ends this frame's judging. In a playing, paused game with no :term[input
   sequence]{id=input-sequence} running, one fixed step is requested, and only when none is pending.
3. **Line 693:** the next attempt waits until that step has run, so it never sees an older state.
4. **Lines 699–706:** the final attempt, and only it, becomes one entry of the journal, with its number of `attempts`.

:::why
A game that is not paused keeps advancing by its own clock while the script waits a frame between attempts, so the
number of fixed steps between two attempts is not under the script's control. A paused game advances only when the
script says so, which makes the count the same everywhere. That is why physics checks pause
first and then wait. The price is a frame for each fixed step.
:::

## A toy version

:::question
The toy uses loops, functions, :term[structs]{id=struct} and a map of strings. If a line looks strange, read [programming 2](../basics/programming-2.md), [programming 3](../basics/programming-3.md) and [generic C++](../basics/cpp-generic.md) first.
:::

The toy runs two scripts against a pretend world. It has `bind`, a reference and `expect`, and nothing else: no `until`,
no pending commands and no JSON. A result is a map from a pointer to a number. Look at how the second script ends: its
first step fails a condition, so its name is dropped, and the step that refers to it does not run.

```cpp sketch="editor-command-scripts-toy.cpp"
// A toy command script runner: steps with expect, bind and a reference to a bound value.
#include <cstdio>
#include <limits>
#include <map>
#include <string>
#include <vector>

namespace
{
	constexpr double c_Infinity = std::numeric_limits<double>::infinity();

	// A result maps a JSON pointer to a number: a stand-in for a JSON document.
	using Result = std::map<std::string, double>;

	struct Step
	{
		std::string Command;
		std::string Ref;         // The name of a bound value this step uses; empty for none
		double Number = 0.0;     // Another parameter, such as the count of steps
		std::string Pointer;     // Where to look in the result for the expectation
		double Min = -c_Infinity;
		double Max = c_Infinity;
		std::string BindName;    // A name for the "/id" of the result; empty for none
	};

	// A fake world: every entity starts 10 m up and falls under gravity as steps run.
	Result RunCommand(const Step& step, int& nextId, int& stepsRun)
	{
		if (step.Command == "create")
			return { { "/id", nextId++ } };
		if (step.Command == "step")
		{
			stepsRun += static_cast<int>(step.Number);
			return { { "/stepsRun", stepsRun } };
		}
		const double seconds = stepsRun / 60.0;
		return { { "/y", 10.0 - 0.5 * 9.81 * seconds * seconds } };
	}

	bool RunScript(const char* title, const std::vector<Step>& steps)
	{
		std::printf("%s\n", title);
		std::map<std::string, int> bindings;
		bool failed = false;
		int nextId = 100;
		int stepsRun = 0;
		for (size_t index = 0; index < steps.size(); index++)
		{
			const Step& step = steps[index];
			if (!step.Ref.empty())
			{
				if (bindings.find(step.Ref) == bindings.end())
				{
					std::printf("  step %zu %s: no value for the reference '%s', not run\n", index + 1, step.Command.c_str(), step.Ref.c_str());
					failed = true;
					continue;
				}
			}
			const Result result = RunCommand(step, nextId, stepsRun);
			bool met = true;
			if (!step.Pointer.empty())
			{
				const double value = result.at(step.Pointer);
				met = value >= step.Min && value <= step.Max;
				std::printf("  step %zu %s: %s = %.2f %s\n", index + 1, step.Command.c_str(), step.Pointer.c_str(), value, met ? "ok" : "FAILED");
			}
			if (!met)
				failed = true;
			if (!step.BindName.empty())
			{
				if (met)
					bindings[step.BindName] = static_cast<int>(result.at("/id"));
				else
					bindings.erase(step.BindName); // Later steps must not use a value of a failed step
			}
		}
		return !failed;
	}
}

int main()
{
	const bool first = RunScript("Script 1: a ball falls for one second", {
		{ "create", "", 0.0, "/id", 100.0, 100.0, "ball" },
		{ "step", "", 60.0, "/stepsRun", 60.0, 60.0, "" },
		{ "get", "ball", 0.0, "/y", 4.0, 6.0, "" },
		{ "get", "ball", 0.0, "/y", 9.0, 11.0, "" },
		{ "get", "ball", 0.0, "/y", 4.0, 6.0, "" } });
	const bool second = RunScript("Script 2: the step that binds fails", {
		{ "create", "", 0.0, "/id", 500.0, 500.0, "ball" },
		{ "get", "ball", 0.0, "/y", 9.0, 11.0, "" } });
	std::printf("exit code %d\n", first && second ? 0 : 1);
	return 0;
}
```

```text output-of="editor-command-scripts-toy.cpp"
Script 1: a ball falls for one second
  step 1 create: /id = 100.00 ok
  step 2 step: /stepsRun = 60.00 ok
  step 3 get: /y = 5.09 ok
  step 4 get: /y = 5.09 FAILED
  step 5 get: /y = 5.09 ok
Script 2: the step that binds fails
  step 1 create: /id = 100.00 FAILED
  step 2 get: no value for the reference 'ball', not run
exit code 1
```

1. **Lines 15–24:** a step holds the keys of a script step: the command, a reference, a number, a pointer with a range, and a name to bind.
2. **Lines 27–38:** the pretend world creates entities and drops them under gravity as steps run.
3. **Lines 50–58:** a reference with no binding fails its step without running it.
4. **Lines 69–75:** a name is bound only when the step passed, and dropped when it failed.

In the first script the ball is created, falls for 60 steps and is read three times: inside the range, outside it, and
inside it again. The failed read does not hide the next one, and the :term[exit code]{id=exit-code} is 1 at the end. The second script shows
the dropped binding. The toy omits the hard parts of the engine's runner: steps that answer later, waits, and the
check of the whole file before the first step.

## The real code: loading, running and the exit code

`StrataEditor --commands <file>` loads the file when the editor starts. A file that does not read, or a script whose
references are wrong, sets the exit code to 1, and with `--quit-after-commands` the editor closes at once. Otherwise the
script gets its first `Update` before the first frame, so steps that answer at once run immediately. After that
`EditorLayer` calls `UpdateCommandScript` once per frame. Look at what the function does when the script ends.

```cpp src="StrataEditor/src/EditorLayer.cpp#L709-L723"
void EditorLayer::UpdateCommandScript()
{
	if (!m_CommandScript || !m_CommandScript->Update(m_CommandRunner, m_Context, m_Commands))
		return;
	// A failed script fails the process, so scripted runs (CI, automation) notice.
	if (m_CommandScript->HasFailed())
	{
		ST_ERROR("Command script finished with errors");
		m_Host->SetExitCode(1);
	}
	else
	{
		ST_INFO("Command script finished ({} commands)", m_CommandScript->GetStepCount());
	}
	m_CommandScript.reset();
```

1. **Line 711:** `Update` runs steps until one is pending or the script ends; it returns true only at the end.
2. **Lines 714–717:** a failed script logs an error and sets the exit code of the process to 1, which tests and agents read.
3. **Line 721:** a passing script logs how many commands it ran and leaves the exit code at 0.
4. **Line 723:** the script is released; the lines after it close the editor when `--quit-after-commands` was given.

Two more cases end with exit code 1. If the script is not finished when `editor.quit` runs, the editor logs how many
commands were done and exits with 1, so a script that quits early cannot look successful. If `--frames` limits the run and
the last frame comes first, the same happens. Note that `editor.quit` refuses while the scene has changes that are not
saved, unless `force` is true. The option `--quit-after-commands` needs neither.

## The real code: batches

A **batch** is the command `editor.batch`: it runs up to 1,000 steps in one frame as one undo step. It takes a `steps`
array in the format above and an `atomic` flag, true by default. The single undo step comes from an undo group, which
[Undo](undo.md) teaches: the edits of all steps are recorded between a begin and an end, and one undo takes them all back.

:::rule[Commands never block a frame]
A command that cannot answer in its frame returns a poll function and carries the `MayDefer` flag, as
[Commands that take frames](deferred-commands.md) explains. A batch has to finish within one frame, so it refuses every
command that carries the flag: a frame that waits for another frame cannot end.
:::

Before anything runs, the handler refuses an empty list, more than 1,000 steps, a step that the script reader refuses, an unknown
command, `editor.batch` inside itself and a step with `until`. It also refuses every command that may take frames, such as
`project.create`, `play.start` and `play.step`. The message names the step and says to run that command on its own. A
refused batch changes nothing, because the checks come first.

```cpp src="StrataEditor/src/Editor/Commands/BatchCommands.cpp#L81-L107"
UndoStack& undo = context.GetUndoStack();
if (!undo.BeginGroup(fmt::format("Batch of {} {}", script->GetStepCount(), script->GetStepCount() == 1 ? "command" : "commands")))
	return EditorCommandResult::Fail("Another batch is running");
nlohmann::json results = nlohmann::json::array();
bool runningCopy = false;
for (size_t index = 0; index < script->GetStepCount(); index++)
{
	const EditorCommandResult result = script->RunStepNow(index, context, registry);
	const std::string& name = script->GetStep(index).Command;
	runningCopy = runningCopy || result.RunningCopy;
	if (result.Success)
	{
		results.push_back({ { "command", name }, { "result", result.Value } });
		continue;
	}
	results.push_back({ { "command", name }, { "error", DescribeStepError(result) } });
	if (atomic)
	{
		// The steps before it go, as if the batch had not run.
		std::string undoError;
		const bool reverted = undo.CancelGroup(&undoError);
		return EditorCommandResult::Fail(fmt::format("Step {} ({}) failed: {}{}", index, name, result.Error,
			reverted ? std::string(" (the steps before it were undone)") : fmt::format(" (undoing the steps before it failed: {})", undoError)),
			result.ErrorKind == EditorCommandError::InvalidParameters ? EditorCommandError::InvalidParameters : EditorCommandError::Failed);
	}
}
undo.EndGroup();
```

1. **Lines 81–83:** the undo group opens here; a batch that is already open makes this one fail, because groups do not nest.
2. **Lines 86–88:** every step runs through `RunStepNow`, which substitutes references, runs the command at once and takes its bindings.
3. **Line 96:** a failed step still adds its error to the answer, so the caller sees which step broke.
4. **Lines 97–105:** an atomic batch cancels the group, so the steps before the failure are undone, and fails naming the step.
5. **Line 107:** a batch that did not stop ends the group, and the whole list becomes one undo step.

With `atomic` false, the batch runs every step and keeps what succeeded. The answer holds each step's result or error and
the bindings, so a client can use the ids the batch created. A batch that changes the :term[running copy]{id=running-copy} of a playing scene adds
a warning, because `play.stop` discards those changes.

## The real code: from a session to a script

The journal records every command of a session, and the command that exports a replay turns it into a script of this
format. It writes `bind` and `$ref` for the ids that results gave, so the file runs on a copy of the project, where every
id is new. [The journal](journal.md) teaches how it is built. A hand-written script, a batch and an exported replay share
one reader, so a session can become a regression test of the editor.

:::example[A ball that falls for one second]
The script below drops a ball from 10 m up and checks its height after 60 fixed steps. At 9.81 m/s² a fall of one second covers about 5 m, so a window from 4 to 6 holds.

```json
[
	{ "command": "project.create", "parameters": { "directory": "FallTestProject", "name": "FallTest" } },
	{ "command": "entity.create", "parameters": { "name": "Ball", "components": { "Transform": { "Translation": [0, 10, 0] }, "RigidBody": { "Type": "Dynamic" }, "BoxCollider": {} } }, "bind": { "ball": "/id" } },
	{ "command": "play.start", "parameters": { "paused": true } },
	{ "command": "play.step", "parameters": { "steps": 60 }, "expect": { "/stepsRun": { "equals": 60 } } },
	{ "command": "component.get", "parameters": { "entity": { "$ref": "ball" }, "component": "Transform" }, "expect": { "/values/Translation/1": { "min": 4, "max": 6 } } }
]
```

The first step creates the project in `FallTestProject`, a folder relative to where the editor starts. Delete it before a
second run, because `project.create` refuses a folder that holds a project.

The second step creates the ball and names its id `ball`. The third starts the game paused, so no step runs before the
script says so. The fourth runs exactly 60 steps and checks that 60 ran. The fifth reads the transform of the ball by the
bound id and requires the second number of `Translation`, the height, to lie between 4 and 6. Save the file as
`FallTest.json` and run it without a window.

```sh
StrataEditor --no-gpu --no-automation --quit-after-commands --commands FallTest.json
```

The option `--no-gpu` runs without a :term[graphics card]{id=gpu}, `--no-automation` starts no server for outside clients, and
`--quit-after-commands` closes the editor once the script ends. After the start-up lines, the log shows each step's answer
and how the script ended.

```text capture="script-run"
… [info] App: Strata Editor 0.8.0 (Windows)
… [info] Strata: Engine modules: Input, Scene, Renderer, Physics, Audio, Animation, Scripting, World, GameUI. Scene systems update in the order UI, Scripting, Animation, World, Physics, Audio
… [info] Strata: JobSystem: 23 worker threads, 2 I/O threads, 20 background threads
… [info] Strata: AudioEngine: mixing without an output device (48000 Hz, 2 channels)
… [info] Strata: Asset scan: 0 assets, 0 imported, 0 failed (0 ms)
… [info] App: Opened project 'FallTest' (S:/FallTestProject)
… [info] App: project.create -> {"discardedChanges":false,"discardedSettings":false,"projectFile":"S:/FallTestProject/FallTest.stproj","startScene":null,"template":"empty"}
… [info] App: entity.create -> {"id":"…"}
… [info] App: play.start -> {"paused":true,"state":"Play"}
… [info] App: Started in …
… [info] App: play.step -> {"fixedSteps":60,"frameIndex":60,"paused":true,"state":"Play","stepsRun":60,"time":1.0000000521540642}
… [info] App: component.get -> {"values":{"Rotation":[0,0,0,1],"Scale":[1,1,1],"Translation":[0,5.1553044,0]}}
… [info] App: Command script finished (5 commands)
… [info] Strata: AudioEngine: shut down
```

1. **Lines 6–7:** the project lies where the editor started: for this log, a folder of its own seen as the drive `S:`.
2. **Line 12:** the ball is at 5.16 m, inside the window.
3. **Line 13:** every step passed, and the exit code is 0.

Change `max` to 4.5 and run again. The last step now logs an error that names the pointer and
the height it found, the script ends with the line "Command script finished with errors", and the exit code is 1. Read it with `echo $?` in a Linux or macOS terminal, or `$LASTEXITCODE` in
PowerShell.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A scripting language for checks | Many tools for their automated tests | Loops, branches and helper functions in a check | An interpreter, its bugs, and checks that can hang |
| Recorded input (mouse and keyboard replay) | Test tools for graphical programs | Checks made without knowing the commands | Checks that break when a button moves, and no way to judge a result by value |
| Tests written in C++ against the editor's classes | The engine's own unit tests | Direct access to every function, and speed | A build per check; no way for an agent to add one |
| One command per call from outside | Agents through the automation server | Decisions between steps by the caller | A process that must stay connected, and no single exit code for the run |

The last row is no rival: [agents that run commands](../automation/agents.md) use the server for decisions between steps and a file for a check that can run again.

## How it is tested

The suite `Editor.CommandRunner` tests commands that finish at once, pending commands polled once per update, and
cancelling. The suite `Editor.CommandScript` tests the script: validation before anything runs, badly formed
expectations, `until` in a running and in a paused game, its bounds. Another case checks that a failed step marks the script
while the rest still runs. The suites `Editor.CommandScriptBindings` and `Editor.Replay` test bindings in exported
replays, and `Editor.Commands` holds the batch cases: one undo step, the atomic cancel and the refusals.

The smoke script runs end to end in the test `StrataEditor.Smoke`, which passes only when the exit code is 0. It carries
the label `gpu`, so a machine without a graphics card skips it. Run one suite with
`StrataTests --test-suite=Editor.CommandScript`. [The kinds of tests](../engineering/test-kinds.md) shows how these fit
the others.

## Changing it safely

- **A new key in a step** goes into the list of known keys in `EditorCommandScript::FromJson`: an unknown key must stay
  an error.
- **Keep the order of checks.** References are checked when the file is read, `until` steps before the first step runs,
  and `editor.batch` refuses its list before it changes anything. A check moved later turns a refusal into a script that
  fails half done.
- **Never let a step use a stale binding.** `TakeBindings` drops the name of a failed step, and that alone keeps a later
  step from changing the wrong entity.
- **Do not wait in a batch.** A command that waits carries `MayDefer`, which `editor.batch` reads; a new command that waits
  and forgets the flag would stall the frame.

Run the suites above and the smoke test, and add a case to `Editor.CommandScript` that fails without your change.

## Summary

- A command script is a JSON array of steps; each step is a command with optional `expect`, `bind` and `until`, and `bind` with `$ref` carries a value to a later step.
- `until` repeats a query until its `expect` holds; in a paused game one fixed step runs between attempts, so the wait is exact on any machine.
- `editor.batch` runs up to 1,000 steps in one frame as one undo step, refuses commands that wait, and an atomic batch undoes its earlier steps when one fails.
- A failed step marks the script failed, the later steps still run, and `EditorLayer::UpdateCommandScript` turns the mark into exit code 1.
- `StrataEditor --commands <file> --no-gpu --quit-after-commands` runs a script without a window, and the terminal shows its log and exit code.

## Check yourself

1. A script has five steps, and step 2 fails its `expect`. Which steps run, and what is the exit code?
   (a) Step 1 only, exit code 1; (b) all five, exit code 1; (c) all five, exit code 0, because only the last step counts;
   (d) none, because the file is checked first.

   :::answer{tests="exit-code"}
   (b). A failed step marks the script and the rest still run, and a failed script sets exit code 1. Answer (a) describes
   a runner that stops at the first failure, which Strata does not. Answer (c) is wrong because any failed step marks the
   whole script. Answer (d) fits a reference with no earlier binding or a bad `until`, not an `expect` that misses.
   :::

2. Step 3 binds `"crate": "/id"` and fails. Step 4 uses `{"$ref": "crate"}`. What happens to step 4?

   :::answer{tests="write-script"}
   Step 4 fails without running, as a call with invalid parameters, and the script is marked failed. The file was valid,
   because step 3 binds the name, so the check at load time passes. At run time the failed step drops the name. Step 5
   still runs.
   :::

3. The game is paused and a query returns the count of fixed steps run so far. A step has `expect` with a minimum of 3 and
   `until` with `{"steps": 600}`. How many attempts and fixed steps run, and what does the journal hold?

   :::answer{tests="until-exact"}
   Four attempts, which see 0, 1, 2 and 3, and three fixed steps. After each miss the script runs one step. The journal
   holds one entry, the last attempt, with `attempts` equal to 4.
   :::

4. A batch has these steps: `entity.create`, `play.step`, `entity.create`. What happens?

   :::answer{tests="batch-rules"}
   The batch is refused before anything runs, because `play.step` can take frames. The message names step 1 (the batch
   counts from 0) and says to run it on its own. Nothing is created, and no undo step is recorded.
   :::

5. Which :term[command line]{id=terminal-command} runs `Smoke.json` without a window and closes the editor when the script ends?
   (a) `StrataEditor --commands Smoke.json`; (b) `StrataEditor --no-gpu --quit-after-commands --commands Smoke.json`;
   (c) `StrataEditor --frames 0 Smoke.json`; (d) `StrataEditor --no-gpu --quit-after-commands Smoke.json`.

   :::answer{tests="run-headless"}
   (b). It names the script, runs without a graphics card and closes after the script. Answer (a) opens a window and
   stays open. Answers (c) and (d) never name the script as the value of `--commands`.
   :::

## Exercises

1. **Medium.** The toy checks a reference only when its step runs. Write the check that the engine does at load time: a
   function that reads the whole script and reports the first reference that no earlier step binds.

   :::answer[Worked solution]{tests="write-script" solution="sketches/editor-command-scripts-validate.cpp"}
   Keep the set of names bound so far, and visit the steps in order. A reference whose name is not in the set is an error.
   A binding adds its name only after the step's own reference was checked, so a step cannot use its own name. The sketch
   tries three scripts: a good one, one that refers before the binding, and one with a wrong name.

   ```cpp sketch="editor-command-scripts-validate.cpp"
   // Checks the references of a script against the names earlier steps bind, before anything runs.
   #include <cstdio>
   #include <set>
   #include <string>
   #include <vector>

   namespace
   {
   	struct Step
   	{
   		std::string Command;
   		std::string Ref;      // A bound name this step uses; empty for none
   		std::string BindName; // A name this step binds; empty for none
   	};

   	// Returns an empty string when every reference names a value that an earlier step binds.
   	std::string CheckReferences(const std::vector<Step>& steps)
   	{
   		std::set<std::string> bound;
   		for (size_t index = 0; index < steps.size(); index++)
   		{
   			const Step& step = steps[index];
   			if (!step.Ref.empty() && bound.count(step.Ref) == 0)
   				return "step " + std::to_string(index + 1) + " (" + step.Command + "): no earlier step binds '" + step.Ref + "'";
   			if (!step.BindName.empty())
   				bound.insert(step.BindName);
   		}
   		return "";
   	}
   }

   int main()
   {
   	const std::vector<Step> good = { { "create", "", "ball" }, { "get", "ball", "" } };
   	const std::vector<Step> late = { { "get", "ball", "" }, { "create", "", "ball" } };
   	const std::vector<Step> typo = { { "create", "", "ball" }, { "get", "bal", "" } };
   	for (const std::vector<Step>* script : { &good, &late, &typo })
   	{
   		const std::string error = CheckReferences(*script);
   		std::printf("%s\n", error.empty() ? "ok: the script may run" : error.c_str());
   	}
   	return 0;
   }
   ```

   ```text output-of="editor-command-scripts-validate.cpp"
   ok: the script may run
   step 1 (get): no earlier step binds 'ball'
   step 2 (get): no earlier step binds 'bal'
   ```

   1. **Line 19:** the names bound by the steps so far.
   2. **Lines 23–24:** a reference is checked before the step's own binding is added.
   3. **Lines 25–26:** a step that binds adds its name for the steps after it.
   4. **Line 28:** an empty string means that every reference has a binding.
   :::

2. **Hard.** Trace it yourself. Run a script with a step whose `expect` cannot hold, with `--commands` and
   `--quit-after-commands`, and find the line that sets exit code 1.

   :::answer[Worked solution]{tests="exit-code,run-headless"}
   Search for `SetExitCode` in `StrataEditor/src/EditorLayer.cpp`. In `EditorLayer::UpdateCommandScript` the call stands in
   the branch that tests `HasFailed()`. The flag comes from `StrataEditor/src/Editor/EditorCommandRunner.cpp`: the
   completion of the step in `EditorCommandScript::Update` calls `CheckExpectations`, logs the failed condition and sets
   `m_Failed`. A breakpoint on `SetExitCode` shows `UpdateCommandScript` called from the layer's update.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorCommandRunner.h` and `EditorCommandRunner.cpp`: `EditorCommandScript` (`FromJson`, `Load`, `Update`, `RunStepNow`, `CheckUntilSteps`, `JudgeUntilAttempt`, `TakeBindings`) and `EditorCommandRunner`.
- `StrataEditor/src/Editor/Commands/BatchCommands.cpp`: `editor.batch`.
- `StrataEditor/src/EditorLayer.cpp`: `UpdateCommandScript` and the exit codes; `StrataEditor/src/EditorApplication.cpp`: the options `--commands` and `--quit-after-commands`.
- `StrataTests/Editor/SmokeCommands.json.in` and the test `StrataEditor.Smoke` in `StrataTests/CMakeLists.txt`.
- Tests: `StrataTests/src/Editor/EditorCommandRunnerTests.cpp`, `EditorCommandTests.cpp` and `ReplayTests.cpp`.

## Further reading

- JSON Pointer, RFC 6901: the exact syntax of the paths that `expect` and `bind` use; intermediate.
- Martin Fowler, "Self-Testing Code": why checks that run by themselves matter; beginner.
- Gerard Meszaros, "xUnit Test Patterns", the chapter on data-driven tests: checks held as data; advanced.
