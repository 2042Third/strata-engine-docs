---
id: editor/stepping
title: "Pausing, stepping and exact tests"
description: "How Strata pauses a running game and runs it for an exact number of fixed steps, so tests, agents and simulated input give the same result on every machine."
kind: internals
size: M
tracks: [E]
needs: [editor/play-mode, input/simulated]
time: 65
learn:
  - id: count-steps
    text: explain why a check of a running game counts fixed steps and never frames
  - id: pause-step
    text: trace how Scene and EditorContext run exactly n fixed steps of a paused game
  - id: play-step
    text: name the ways play.step answers or fails, and the state its poll keeps
  - id: hold-steps
    text: compute how many fixed steps a simulated hold covers and when input steps differ from fixed steps
  - id: write-sequence
    text: write an input.sequence that presses a key at a fixed step and samples a value
since: 0.3.0
status: final
---

A test or an agent often needs the same thing: run the game for exactly 60 :term[fixed steps]{id=fixed-step}, then check where the ball is. The editor does this with three parts. The scene can pause and run a chosen number of fixed steps, and the editor counts those steps and keeps the game's input quiet between them. The commands `play.step` and `input.sequence` use both, and the other `input.*` commands give input durations in the same steps. This page follows that chain from the scene up, and leaves the fixed step itself, the simulated device and the files of such checks to their own pages.

## The problem and how engines solve it

Suppose a test starts a game, waits 60 frames and then reads the height of a falling ball. On a computer that draws 125 frames in each second, 60 frames last under half a second. On a slow computer that draws 30 frames in each second, they last two seconds. The ball has fallen a different distance, so the test passes on one machine and fails on the other. The cause is that a frame is a unit of drawing, and the game's physics does not run once per frame.

The usual answers are to wait by the clock, to wait by frames, or to count the simulation's own steps. A clock wait inherits the speed of the machine and its other work. A frame count inherits the :term[frame rate]{id=frame-rate}. Only the third gives a result that does not depend on the machine, because [the fixed step](../core/time.md) is the unit the game itself uses to move bodies and run scripts. Strata takes the third answer and makes it a rule: game time counts fixed steps, never frames.

To count steps exactly, the game must stop on its own. A paused game that runs one fixed step in each frame, when asked, gives the same state at the end whatever the frame rate. Some frames take 8 ms and some take 33 ms, and the step is still the same step.

**Stepping** is running a paused game for an exact number of fixed steps, one step in each frame, and then looking at its state.

## The map

The scene owns the pause and the step counts. The editor's context owns the counters that tools read, and it decides when the game's input may move. The commands sit on top. The editor's :term[frame loop]{id=game-loop} only lifts its frame cap while steps are pending.

```mermaid caption="The scene runs the steps, the editor context counts them and suspends input, and the commands wait for the counts." alt="A diagram with the scene at the bottom, the editor context above it and the play step, input sequence and input commands above that."
flowchart TB
    S["Scene: SetPaused, Step, GetFixedStepCount"]
    E["EditorContext: SetPaused, Step, counters, input suspension"]
    L["EditorLayer: frame cap"]
    P["play.step: poll with its own state"]
    Q["input.sequence: events per step"]
    I["input.key, input.action, input.click: holds"]
    S --> E
    E --> L
    E --> P
    E --> Q
    E --> I
```

All of it runs on the :term[main thread]{id=main-thread}, in the frame loop. Nothing waits: each command that needs steps returns a :term[poll function]{id=poll-function}, and the editor continues to draw while the steps run.

## The contract

The pieces keep a few promises, and each has a reason.

- A paused scene does not update its running systems; it tells them once (`OnPausedChanged`). The reason is that a paused game must stand still while the editor draws it, picks in it and captures it.
- `Scene::Step(n)` lets the next n updates each run exactly one fixed step. Steps asked for while paused are the only way a paused scene moves.
- `Scene::GetFixedStepCount` counts the fixed steps since the game started, whether they were stepped or due on the clock. This is the clock that tools count in.
- Resuming drops the steps that have not run, so that steps asked for in one pause never run in a later one.
- A tool reads the count and never counts frames, because frames change with the machine.

:::rule
Tools count game time in fixed steps, never frames. The reason is that the fixed step is the game's own time base, so the same steps give the same state on every machine. The rule is stated in full in [Time](../core/time.md).
:::

The input tools keep one exception to the rule, and the reason comes from pause menus. A **hold** is the editor's record that a simulated key, button, axis or input action is down, with the fixed steps it covers. Holds count `EditorContext::GetInputStepCount`: the fixed steps, plus each frame in which the running game updates with its :term[time scale]{id=time-scale} at 0 and runs no fixed step. A pause menu stops game time by setting the time scale to 0, so no fixed step ever runs there. If holds counted only fixed steps, a tap on a menu button would never end.

## A toy version

The sketch below is a toy scene with the same three operations. It keeps a falling ball, a paused flag, the steps still to run and the count of fixed steps. When it is not paused, it adds the frame's length to an :term[accumulator]{id=accumulator} and runs a step for each 10 ms. When it is paused, it runs one step for each frame in which a step is due, and nothing otherwise. Look at how the two ways to wait differ between a fast and a slow frame rate.

```cpp sketch="editor-stepping-toy.cpp"
#include <cstdint>
#include <cstdio>

// A falling ball moved by fixed steps of 10 ms. Times are whole milliseconds, so the sums are exact.
struct ToyScene
{
	static constexpr uint32_t c_StepMs = 10;

	bool Paused = false;
	uint32_t StepFrames = 0;
	uint64_t FixedSteps = 0;
	uint32_t AccumulatorMs = 0;
	double Height = 100.0;
	double Speed = 0.0;

	void SetPaused(bool paused)
	{
		Paused = paused;
		if (!paused)
			StepFrames = 0;
	}

	void Step(uint32_t frames) { StepFrames += frames; }

	void Update(uint32_t frameMs)
	{
		if (Paused)
		{
			if (StepFrames == 0)
				return;
			StepFrames--;
			RunFixedStep();
			return;
		}
		AccumulatorMs += frameMs;
		while (AccumulatorMs >= c_StepMs)
		{
			AccumulatorMs -= c_StepMs;
			RunFixedStep();
		}
	}

	void RunFixedStep()
	{
		const double seconds = c_StepMs / 1000.0;
		Speed -= 9.8 * seconds;
		Height += Speed * seconds;
		FixedSteps++;
	}
};

int main()
{
	const uint32_t frameLengths[] = { 8, 33 };
	for (const uint32_t frameMs : frameLengths)
	{
		ToyScene waiting;
		for (int frame = 0; frame < 60; frame++)
			waiting.Update(frameMs);

		ToyScene stepped;
		stepped.SetPaused(true);
		stepped.Step(60);
		for (int frame = 0; frame < 60; frame++)
			stepped.Update(frameMs);

		std::printf("frames of %2u ms | wait 60 frames: %3llu steps, height %6.2f | step 60: %llu steps, height %6.2f\n", frameMs,
			static_cast<unsigned long long>(waiting.FixedSteps), waiting.Height, static_cast<unsigned long long>(stepped.FixedSteps),
			stepped.Height);
	}
	return 0;
}
```

```text output-of="editor-stepping-toy.cpp"
frames of  8 ms | wait 60 frames:  48 steps, height  98.85 | step 60: 60 steps, height  98.21
frames of 33 ms | wait 60 frames: 198 steps, height  80.69 | step 60: 60 steps, height  98.21
```

1. **Lines 18–20:** resuming drops the steps that have not run.
2. **Lines 27–33:** a paused scene runs one step in each frame that has one due, and nothing else.
3. **Lines 35–40:** a running scene adds the frame to the accumulator and runs a step for each 10 ms.

Waiting 60 frames gives 48 steps at one frame length and 198 at the other, so the two balls are in different places. Stepping 60 times gives 60 steps and one height, 98.21, whatever the frame length. The real code adds what the toy omits: the systems that learn about the pause, the exact drawing of paused poses, the counters that let a command see a resume, and the input suspension.

## The real code

Start with the scene. `Scene::SetPaused` does nothing when the state does not change. On resume it drops the pending steps; on pause it clears the drawn :term[interpolation]{id=interpolation} and tells every system.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2337-L2353" symbol="Scene::SetPaused"
void Scene::SetPaused(bool paused)
{
	if (paused == m_IsPaused)
		return;

	m_IsPaused = paused;
	if (!paused)
		m_StepFrames = 0;
	if (!m_IsRunning)
		return;
	// A paused game is drawn exactly, so that gizmos, picking and captures agree with what is drawn. Resuming needs nothing:
	// the next stepping frame's set starts from the paused poses.
	if (paused)
		ClearInterpolation();
	for (const Scope<SceneSystem>& system : m_Systems)
		system->OnPausedChanged(paused);
}
```

1. **Lines 2339–2340:** a call that changes nothing returns at once.
2. **Lines 2343–2344:** resuming drops the pending steps.
3. **Lines 2349–2352:** pausing clears the interpolation, so poses draw exactly, and tells every system.

Then comes the update. When the scene is paused and has no step to run, it only keeps transforms current and lets the systems that asked for it run their paused update. When a step is due, the frame's time is the fixed step itself, not the frame's length, so the result does not depend on how long the frame took.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2221-L2259"
const bool stepping = m_IsPaused && m_StepFrames > 0;
if (m_IsPaused && !stepping)
{
	UpdateWorldTransforms();
	if (!m_PausedUpdateCalls.empty())
	{
		m_IsUpdating = true;
		ForEachSystemCall(m_PausedUpdateCalls, [](SceneSystem& system) { system.OnPausedUpdate(); });
		m_IsUpdating = false;
		FlushPendingDestroys();
		UpdateWorldTransforms();
	}
#ifdef ST_DEBUG
	CheckCachesAfterUpdate();
#endif
	return;
}

const float fixedTimestep = GetFixedTimestep();
const float deltaTime = stepping ? fixedTimestep : static_cast<float>(timestep) * m_TimeScale;
const bool interpolating = IsInterpolating();
// Stepped frames draw exactly; a new rate (the project's FixedRate, scene.setSettings) leaves poses of the old one.
if (stepping || (interpolating && m_InterpolationTimestep != 0.0f && fixedTimestep != m_InterpolationTimestep))
	ClearInterpolation();
// Unscaled time goes on at time scale 0 (a pause menu's fades): the frame's timestep before the time scale, the fixed
// step while stepping.
m_UnscaledDeltaTime = stepping ? fixedTimestep : std::max(static_cast<float>(timestep), 0.0f);
m_UnscaledTime += m_UnscaledDeltaTime;

m_IsUpdating = true;
UpdateWorldTransforms();

ForEachSystemCall(m_UpdateCalls, [deltaTime](SceneSystem& system) { system.OnUpdate(Timestep(deltaTime)); });

if (stepping)
{
	ForEachSystemCall(m_FixedUpdateCalls, [fixedTimestep](SceneSystem& system) { system.OnFixedUpdate(fixedTimestep); });
	m_StepFrames--;
	m_FixedSteps++;
```

1. **Line 2221:** the scene steps only when it is paused and a step is pending.
2. **Lines 2222–2228:** with no step due, only the paused update of the systems runs.
3. **Lines 2257–2259:** one fixed update runs, the pending count falls and the fixed step count rises.

The editor's side is thin. `EditorContext::SetPaused` records the fixed step count and bumps a counter at each resume, then calls the scene. `EditorContext::Step` forwards to the scene only while the game is paused. Both end by updating the input suspension.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1560-L1582"
void EditorContext::SetPaused(bool paused)
{
	if (!paused && IsPaused())
	{
		m_FixedStepsAtResume = GetFixedStepCount();
		m_ResumeCount++;
	}
	if (m_RuntimeScene)
		m_RuntimeScene->SetPaused(paused);
	UpdateInputSuspension();
}

bool EditorContext::IsPaused() const
{
	return m_RuntimeScene && m_RuntimeScene->IsPaused();
}

void EditorContext::Step(uint32_t frames)
{
	if (m_RuntimeScene && m_RuntimeScene->IsPaused())
		m_RuntimeScene->Step(frames);
	UpdateInputSuspension();
}
```

1. **Lines 1562–1566:** resuming a paused game records the fixed step count and counts the resume.
2. **Lines 1567–1569:** the call reaches the scene and updates the input suspension.
3. **Lines 1579–1580:** `Step` reaches the scene only while it is paused.

The counters exist for the commands that wait. A poll that sees the resume count change knows the game was resumed, and the count of fixed steps at the resume tells it how many pending steps ran before the rest were dropped.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1620-L1624" symbol="EditorContext::UpdateInputSuspension"
void EditorContext::UpdateInputSuspension()
{
	// The game updates in the next frame unless it is paused without a step to run: only then may input frames go on.
	Input::SetSuspended(m_RuntimeScene && m_RuntimeScene->IsPaused() && m_RuntimeScene->GetStepFrames() == 0);
}
```

:term[Input frames]{id=input-frame} stop only when the game is paused with no step to run. While a step is pending, the game updates in the next frame, so input may arrive with it. A key tapped while the game is paused therefore reaches the game in the next step that `play.step` runs, or after a resume.

### play.step

The command `play.step {steps, wait}` is a deferred Session command. It refuses to run unless the game runs paused, and it refuses while an input sequence plays. It computes where its last step falls: the fixed steps so far, plus the steps already pending, plus its own. A second `play.step` therefore queues behind the first and answers when its own last step ran. Then it calls `EditorContext::Step`; with `wait: false` it answers at once with the number of pending steps, and otherwise it returns a poll function.

The poll keeps its own state: the first step number, the target, the play session and the resume count it saw at the start, and the last fixed step count it saw. Look at the three ways it can end.

```cpp src="StrataEditor/src/Editor/Commands/PlayCommands.cpp#L225-L255"
return EditorCommandResult::Defer([first, target, steps, session = context.GetPlaySession(), resumes = context.GetResumeCount(),
	lastSeen = context.GetFixedStepCount()](EditorContext& context) mutable -> std::optional<EditorCommandResult>
{
	const auto ran = [&first, &steps](uint64_t count) { return std::clamp<int64_t>(static_cast<int64_t>(count) - static_cast<int64_t>(first), 0, steps); };
	if (!context.IsPlaying() || context.GetPlaySession() != session)
	{
		const uint64_t atStop = context.GetFixedStepCountAtStop(session).value_or(lastSeen);
		return EditorCommandResult::Fail(fmt::format("Play mode stopped (play.stop, or the game quit or crashed) after {} of {} steps", ran(atStop),
			steps), { { "stepsRun", ran(atStop) } });
	}
	// Resumed (also when paused again since): the steps that ran before the resume count; the rest were dropped with it.
	// A poll runs every frame, so the resumes it has not seen yet all happened in one frame, at one step count.
	const bool resumed = context.GetResumeCount() != resumes;
	lastSeen = resumed ? context.GetFixedStepCountAtResume() : context.GetFixedStepCount();
	if (lastSeen >= target)
	{
		const Scene& scene = *context.GetActiveScene();
		nlohmann::json value = DescribePlayState(context);
		value["stepsRun"] = steps;
		value["frameIndex"] = scene.GetFrameIndex();
		value["time"] = scene.GetTime();
		value["fixedSteps"] = lastSeen;
		return EditorCommandResult::Ok(std::move(value));
	}
	if (resumed)
	{
		return EditorCommandResult::Fail(fmt::format("Play mode was resumed after {} of {} steps; the rest were dropped", ran(lastSeen), steps),
			{ { "stepsRun", ran(lastSeen) } });
	}
	return std::nullopt;
});
```

1. **Lines 225–226:** the poll copies its own state: the session, the resume count and the last count seen.
2. **Lines 229–233:** a stopped game fails the request with the steps that ran.
3. **Lines 237–238:** a changed resume count reads the fixed steps at that resume.
4. **Lines 239–247:** past the target, the poll answers with `stepsRun` and the state.
5. **Lines 249–254:** a resume before the target fails; otherwise the poll waits.

The answer carries `stepsRun`, the frame index, the game time and `fixedSteps`. The two failures also carry `stepsRun`, so a client knows how far the game got. The poll never blocks, and it allocates nothing in a frame.

While steps are pending, the editor lifts its frame cap, so 600 steps cost the work of 600 frames and not ten seconds at 60 frames per second. `EditorLayer::UpdateSteppingFrameRate` remembers the cap when steps start and puts it back when they end.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1169-L1182" symbol="EditorLayer::UpdateSteppingFrameRate"
void EditorLayer::UpdateSteppingFrameRate()
{
	const bool stepping = m_Context.HasPendingSteps();
	if (stepping && !m_CapBeforeSteps)
	{
		m_CapBeforeSteps = m_Host->GetMaxFrameRate();
		m_Host->SetMaxFrameRate(0);
	}
	else if (!stepping && m_CapBeforeSteps)
	{
		m_Host->SetMaxFrameRate(*m_CapBeforeSteps);
		m_CapBeforeSteps.reset();
	}
}
```

1. **Lines 1174–1175:** when steps start, the layer remembers the cap and removes it.
2. **Lines 1179–1180:** when they end, the cap returns.

The editor also has a switch for :term[time dilation]{id=time-dilation}, the slowing of a game whose steps cannot match real time. It is on in interactive and automation sessions, where the game follows the wall clock. It is off in tests and in scripted runs with `--frames` or `--commands`, which count frames and expect exact steps. A game under test therefore never slows to match the clock.

### Input in steps

The `input.key`, `input.mouseButton`, `input.gamepadButton` and `input.action` commands make holds. A tap has a length in fixed steps (given as `steps`, or as `seconds` of game time that Strata rounds up to whole steps), and a press lasts until a release. Each hold records the first and last step it covers, and after every game update `SimulatedInput::Update` receives the input step count and lets go of the taps whose last step has passed. In a running game a frame can run several steps, so a release may land up to `maxFixedSteps - 1` steps late. While stepping, each frame runs one step, so a tap of n steps covers exactly n.

**Input sequence** is the editor's name for a list of input events, each placed on a fixed step, that the editor plays while it steps the game itself. The command `input.sequence {events, steps, observe, keepHeld, wait}` pauses the game, resumes it at the end if it ran, and runs one step in each frame. Event steps count from 0, so the events of step k apply, in order, once k steps have run. After each step, it takes the observations whose `every` divides the number of steps run so far. At the end it takes every observation once more, and it releases the holds unless `keepHeld` is set.

```cpp src="StrataEditor/src/Editor/InputSequence.cpp#L96-L129" symbol="InputSequence::Update"
void InputSequence::Update(EditorContext& context)
{
	if (m_Result.Finished)
		return;
	if (!context.IsPlaying() || context.GetPlaySession() != m_Session)
	{
		Fail(context, fmt::format("Play mode stopped after {} of {} steps of the input sequence", m_Result.StepsRun, m_Result.Steps));
		return;
	}
	if (!context.IsPaused())
	{
		Fail(context, fmt::format("The game was resumed after {} of {} steps of the input sequence; the rest did not run", m_Result.StepsRun,
			m_Result.Steps));
		return;
	}
	// The step given its events has not run yet (a frame without a game update).
	if (context.GetFixedStepCount() < m_ExpectedSteps)
		return;
	m_Result.StepsRun++;
	if (m_Result.StepsRun == m_Result.Steps)
	{
		Finish(context);
		return;
	}
	Sample(context, false);
	std::string error;
	if (!ApplyEvents(context, &error))
	{
		Fail(context, std::move(error));
		return;
	}
	m_ExpectedSteps = context.GetFixedStepCount() + 1;
	context.Step(1);
}
```

1. **Lines 100–110:** a stopped or resumed game fails the sequence with the steps that ran.
2. **Lines 112–119:** the sequence waits for the step it asked for, then counts it and ends after the last.
3. **Lines 120–128:** it samples, applies the events of the next step and asks for that one step.

An event that fails ends the sequence with its error. Resuming or stopping the game ends it too, with the steps that ran. While a sequence plays, `play.step` and a second sequence fail, since both want to own the stepping.

The other commands that act on the game's input as a whole are small. `input.action` holds an input action, a named control such as jump or a menu confirm, whatever its bindings. It is named as scripts name it, and its value is refused when it does not fit the action's kind. An action has one value, so a new hold replaces the one before without letting the action go; the game still reads it as up while its map is disabled or a binding capture listens.

`input.state` lists the held actions, every action as the game reads it, the enables of the maps, the players' bindings that replace the project's, and whether a capture listens. `input.type` queues :term[typed text]{id=typed-text} of 1 to 1,024 :term[bytes]{id=byte}. `input.releaseAll` ends every hold and drops presses that still wait.

The command `input.click` takes a user interface (UI) element and finds the center of its rect, moves the simulated pointer there and taps a mouse button for n steps. It fails and changes nothing when something covers the element, and the error names the cover. World canvases are projected through the game camera first. How the hit test finds an element is the subject of [UI input](../ui/input.md).

:::example
You want the ball's height 30 steps after the game starts. Start the game paused, so that its first fixed step has not run, then step.

```json
{ "command": "play.start", "parameters": { "paused": true } }
{ "command": "play.step", "parameters": { "steps": 30 } }
```

The first command answers with the state `Play` and `paused` true, and no fixed step has run yet. The second returns after its last step, with `stepsRun` 30 and `fixedSteps` 30; at the default rate of 60 steps in each second, the game time is near 0.5 s. The game stays paused. Read the ball's transform with an ordinary command and it is the same on every machine.

Now add input. This sequence taps the Space key at step 10 and samples the ball's position every 5 steps over 60 steps. The entity value stands for the ball's id, a number that this example invents.

```json
{ "command": "input.sequence", "parameters": {
	"steps": 60,
	"events": [ { "step": 10, "key": "Space", "action": "tap", "steps": 1 } ],
	"observe": [ { "entity": "1234567890", "component": "Transform", "property": "Translation", "every": 5 } ]
} }
```

The key goes down after 10 steps ran and goes up after the next one, so the game sees it for one fixed step. The samples carry the steps 5, 10, 15 and so on to 55, and a final one at 60: twelve in all. Compare the samples of steps 10 and 15: any jump from the key shows between them.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Wait by the clock | Scripts that sleep and then read state | Nothing the game needs | The result changes with the speed of the machine |
| Count frames | Test loops that call the update a set number of times | The simplest loop | A result that changes with the frame rate and with time scale |
| Stepping in fixed steps (Strata) | Tools that must be exact | The same state on every machine | The game must be paused, and one step takes one frame |
| Record input and replay it later | Tools that compare whole runs | Runs that need no live client | A recorder and storage for every run |

## How it is tested

The suite `Editor.Input` checks that a tap lasts its fixed steps whatever the frame rate. It also checks that input given while the game is paused reaches the next stepped frame, and that an input sequence gives the same game at every frame rate. The suite `Editor.GameFlow` has a test named "play.step answers once its steps ran, and steps a resume dropped never run at a later pause". The same test covers two waiting calls. The suite `Scene.Timing` holds "Pause, step, resume, time scale" for the scene's side.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Input
```

Run it from the :term[repository's]{id=repository} root after a build. Doctest filters take a test name with `--test-case`.

## Changing it safely

Extension points are few. A new tool that needs exact time reads `GetFixedStepCount` and, if it waits, returns a deferred result whose poll owns its data and allocates nothing in a frame. A new input command gives its durations in `steps` and `seconds` with the shared schema, and registers with `MayDefer`.

- Never count frames for a result that a test compares; the counts differ between machines.
- Never let a pending count last beyond a resume: the scene clears it, and a poll must treat a changed resume count as the end of its request.
- Keep a poll's state inside the :term[lambda]{id=lambda}; the runner may call it once in every frame for as long as the request lives.
- Test the rule's exception: a game at time scale 0 with a tap that must end.

Check the change with the suites `Editor.Input`, `Editor.GameFlow` and `Scene.Timing`.

## Summary

- A check of a running game counts fixed steps, the game's own time base, because frames change with the machine.
- The scene pauses, runs one fixed step for each requested update and counts steps; the editor keeps the resume counters and suspends input while no step is due.
- `play.step` waits through a poll that keeps its own state, queues behind earlier calls and fails with `stepsRun` on a resume or a stop.
- A hold counts input steps: the fixed steps plus the frames of a running game whose time scale is 0.
- `input.sequence` gives each fixed step its events, samples values every n steps and releases its holds at the end.

## Check yourself

1. A test waits 60 frames, once on a computer that draws 125 frames in each second and once on one that draws 30. The game runs 60 fixed steps in each second. How many steps does it run each time, and is the result the same?

   :::answer{tests="count-steps"}
   About 29 steps (60 frames take 0.48 s) and 120 steps (they take 2 s). The results differ, because the frames change with the machine and the steps do not. A test that steps 60 times gets 60 steps on both.
   :::

2. The game is paused. You call `play.step {steps: 5}` and then `play.step {steps: 5}` before the first answers. After how many steps of the game does the second answer?

   :::answer{tests="pause-step,play-step"}
   After ten steps since the first call began. The second computes its first step as the fixed steps so far plus the five pending, so its target lies five steps beyond the first's. Each answers when its own last step ran.
   :::

3. A `play.step {steps: 10}` waits. After 4 steps someone calls `play.pause {paused: false}`. What does the poll do?

   :::answer{tests="play-step"}
   The poll fails with `stepsRun` 4. The resume dropped the six pending steps, the poll sees the changed resume count, and it reads the fixed step count at the resume to learn how many ran.
   :::

4. The game runs at 60 steps in each second. What does `input.key {key: "Space", seconds: 0.26}` hold?

   :::answer{tests="hold-steps"}
   Sixteen fixed steps. Seconds are rounded up to whole steps: 0.26 times 60 is 15.6, which becomes 16. At one step in each frame, as in `input.sequence`, the key covers exactly 16 steps.
   :::

5. A sequence lists a tap at step 10 and sets `steps` to 10. What happens?

   :::answer{tests="write-sequence"}
   The command is refused before it plays. Its `steps` must be at least the last event's step plus one, here 11, so that the event has a step to run in.
   :::

## Exercises

1. **Basic.** The scene's fixed step is 1/60 s. A hold lasts 12 steps. How many seconds of game time is that, and how many frames at 125 frames in each second pass while the game runs freely?

   :::answer[Worked solution]{tests="count-steps,hold-steps"}
   12 steps of 1/60 s are 0.2 s. At 125 frames in each second, 0.2 s is 25 frames. At 30 frames in each second it is 6 frames. The number of frames changes with the machine and the 12 steps do not, which is why durations are given in steps.
   :::

2. **Medium.** Write the commands that start a game paused and run an `input.sequence` of 40 steps. It holds the key D from step 5 to step 25 and samples the world position of an entity every 10 steps. List the steps of the samples.

   :::answer[Worked solution]{tests="write-sequence"}
   Start with `play.start {paused: true}`. The sequence has `steps` 40, an event at step 5 with `key` "D" and `action` "press", an event at step 25 with `key` "D" and `action` "release", and one observation `{entity, world: true, every: 10}`. The samples have steps 10, 20 and 30, and a final one at 40. The key is released by the event; `keepHeld` stays false.
   :::

3. **Hard.** A paused game has a pending `play.step {steps: 10}`. Write a small program that models the counters, resumes the game after 4 steps and prints what the poll says in each frame.

   :::answer[Worked solution]{tests="pause-step,play-step"}
   The sketch below keeps the counters of the real code and the poll's rules. The resume count changes at frame 4, after the fourth step ran, so the poll fails with `stepsRun` 4.

   ```cpp sketch="editor-stepping-poll.cpp"
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>
   #include <optional>
   #include <string>

   // A paused game that runs one step per frame, with the counters play.step's poll reads.
   struct ToyGame
   {
   	bool Paused = true;
   	uint32_t StepFrames = 0;
   	uint64_t FixedSteps = 0;
   	uint64_t FixedStepsAtResume = 0;
   	uint32_t ResumeCount = 0;

   	void Resume()
   	{
   		if (Paused)
   		{
   			FixedStepsAtResume = FixedSteps;
   			ResumeCount++;
   		}
   		Paused = false;
   		StepFrames = 0;
   	}

   	void Frame()
   	{
   		if (Paused && StepFrames > 0)
   		{
   			StepFrames--;
   			FixedSteps++;
   		}
   	}
   };

   // Returns the answer once the request is over, or nothing while it waits.
   std::optional<std::string> Poll(const ToyGame& game, uint64_t first, int64_t steps, uint32_t resumes)
   {
   	const auto ran = [first, steps](uint64_t count) { return std::clamp<int64_t>(static_cast<int64_t>(count) - static_cast<int64_t>(first), 0, steps); };
   	const bool resumed = game.ResumeCount != resumes;
   	const uint64_t seen = resumed ? game.FixedStepsAtResume : game.FixedSteps;
   	if (seen >= first + steps)
   		return "answers: stepsRun " + std::to_string(steps);
   	if (resumed)
   		return "fails: stepsRun " + std::to_string(ran(seen));
   	return std::nullopt;
   }

   int main()
   {
   	ToyGame game;
   	const uint64_t first = game.FixedSteps + game.StepFrames;
   	game.StepFrames += 10;
   	const uint32_t resumes = game.ResumeCount;
   	for (int frame = 1; frame <= 6; frame++)
   	{
   		game.Frame();
   		if (frame == 4)
   			game.Resume();
   		const std::optional<std::string> answer = Poll(game, first, 10, resumes);
   		std::printf("frame %d: %llu steps run, %s\n", frame, static_cast<unsigned long long>(game.FixedSteps),
   			answer ? answer->c_str() : "still waiting");
   		if (answer)
   			break;
   	}
   	return 0;
   }
   ```

   ```text output-of="editor-stepping-poll.cpp"
   frame 1: 1 steps run, still waiting
   frame 2: 2 steps run, still waiting
   frame 3: 3 steps run, still waiting
   frame 4: 4 steps run, fails: stepsRun 4
   ```

   1. **Lines 20–21:** a resume records the step count and counts the resume.
   2. **Lines 41–42:** the poll sees the changed count and reads the steps at the resume.
   3. **Lines 43–46:** it answers past the target, fails after a resume, and otherwise waits.
   :::

4. **Hard.** Trace it yourself: start a game paused, run `play.step {steps: 3}` and find which frames run a fixed step, and where the count of `stepsRun` is made.

   :::answer[Worked solution]{tests="pause-step,play-step"}
   Put breakpoints in `EditorContext::Step`, in `Scene::OnUpdateRuntime` at the stepping branch, and in the poll of `play.step` in `StrataEditor/src/Editor/Commands/PlayCommands.cpp`. The command calls `EditorContext::Step(3)` once. Then each frame runs one fixed step in `Scene::OnUpdateRuntime`, lowering the pending count, so three frames run one step each and the fourth runs none. The poll reads `GetFixedStepCount` in each frame, and `stepsRun` is the clamped difference to its first step.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/Scene.h` and `Strata/src/Strata/Scene/Scene.cpp`: `SetPaused`, `Step`, `GetFixedStepCount`, `OnUpdateRuntime`.
- `StrataEditor/src/Editor/EditorContext.cpp`: `SetPaused`, `Step`, `GetInputStepCount`, `UpdateInputSuspension`.
- `StrataEditor/src/Editor/Commands/PlayCommands.cpp`: `play.step`, `play.start {paused}`.
- `StrataEditor/src/Editor/EditorInputCommands.cpp`, `StrataEditor/src/Editor/InputSequence.cpp`, `StrataEditor/src/Editor/SimulatedInput.cpp`: the `input.*` commands, sequences and holds.
- `StrataEditor/src/EditorLayer.cpp`: `UpdateSteppingFrameRate`.
- Tests: suites `Editor.Input`, `Editor.GameFlow`, `Scene.Timing`.

## Further reading

- Glenn Fiedler, "Fix Your Timestep" (gafferongames.com): why a simulation advances in fixed steps; beginner to intermediate.
