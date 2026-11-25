---
id: input/simulated
title: "Simulated input"
description: "How tools, tests and agents press keys, move the mouse and tilt gamepad sticks for a running game, and how Strata merges that with real devices."
kind: internals
size: M
tracks: [E]
needs: [input/mouse-cursor, input/gamepads]
time: 60
learn:
  - id: queue-frame
    text: explain why a simulated press waits for the next input frame and what the game sees meanwhile
  - id: merge-rule
    text: predict what a game sees when a tool and a person press or release the same key
  - id: release-clear
    text: compare what releasing all simulated input and clearing it leave behind
  - id: trace-tap
    text: trace a simulated tap from the input.key command to a script's key query
since: 0.8.0
status: final
---

A game normally learns what the player does from the keyboard, the mouse and the gamepads. This page is about a second source: a **virtual keyboard, mouse and set of gamepads** that tools, tests and agents press. The game reads both sources through the same queries and sees one state. The page covers the engine's half: the queue of simulated events, the rules that merge them with real devices, and the calls that let go of them. How long an editor command holds a key, counted in :term[fixed steps]{id=fixed-step}, belongs to [stepping a paused game](../editor/stepping.md).

## The problem and how engines solve it

Suppose you write a test that plays your game: it presses Space, waits, and checks that the robot jumped. A person can run that test once. A machine has to run it a thousand times, on a server with no screen and no keyboard, and get the same answer each time.

Three difficulties follow. First, the machine has no hands: something must produce key presses that the game cannot tell from real ones. Second, the game reads input once per :term[input frame]{id=input-frame}, so a press that arrives while the frame is half done could be seen by some code and missed by other code. Third, a person might touch the real keyboard at the same moment, and the two sources must not confuse each other.

Engines solve the first difficulty in two main ways. Some inject events into the :term[operating system]{id=operating-system}, so the window receives them like real ones. Others keep a virtual device inside the engine and let tools write to it.

Operating-system injection works for any program, but it needs the window to have focus, it differs on each platform and it cannot run without a display. A virtual device works anywhere the game runs, at the price that it skips the operating system's own input code. Strata chose the virtual device, which the [Alternatives](#alternatives-strata-did-not-choose) section weighs again with a table.

The [page on devices and state](../input/devices-state.md) taught that the game sees input as three sets of bits per button, rebuilt at each input frame. A virtual device follows that design: it has its own three sets, and the queries combine the two.

## The map

Everything lives in `Strata/src/Strata/Input/Input.cpp` and its :term[header]{id=header} `Strata/src/Strata/Input/Input.h`. The editor's commands reach the device through `StrataEditor/src/Editor/SimulatedInput.cpp`, which owns the editor's holds. The diagram shows the path of one press, and the :term[main thread]{id=main-thread} runs all of it.

```mermaid caption="A tool's press is queued, applied at the start of the next input frame and merged with the real device before the game reads it." alt="A flow from an editor command through a queue and the start of an input frame into the simulated state, which joins the real device state in the merged queries that scripts read."
flowchart LR
    Command["input.key command"] --> Hold["SimulatedInput"]
    Hold --> Sim["Input::SimulateKey"]
    Sim --> Queue["queue of events"]
    Queue -->|"BeginFrame applies"| State["simulated state"]
    Window["window callbacks"] --> Device["device state"]
    State --> Merge["IsKeyDown, IsKeyPressed, IsKeyReleased"]
    Device --> Merge
    Merge --> Script["script"]
```

**Simulated input** is input that a tool or a test produces for the running game, through a virtual keyboard, mouse and gamepads inside the engine, and that the game sees merged with the real devices. The device state changes the moment a window :term[callback]{id=callback} arrives. The simulated state changes only when `Input::BeginFrame` applies the queue, so the two are written at different times and read together.

## The contract

Callers of the `Simulate*` functions may assume the following, and must do the following.

- A call queues an event. It changes nothing the game can see until the next input frame starts. `Input::HasQueuedSimulatedInput` tells you that events wait.
- Events of one frame apply in the order they were queued, so a press and a release queued together report both transitions in one frame.
- Invalid :term[key codes]{id=key-code} and non-finite numbers are ignored; the call does nothing and does not fail.
- Simulated input reaches the game even while `Input::IsEnabled` is false. A tool drives the game on purpose, whether or not the game view has the focus.
- While input frames are suspended (the editor's paused game), `BeginFrame` does not apply the queue. The events wait for the first frame the game updates in.
- A caller that ends a session must say whether it lets go of the keys (`ReleaseAllSimulated`) or forgets them (`ClearSimulated`).

:::why
Simulated events apply at the next input frame, never at once. Applied at once, half of a frame's systems would have run before the press and half after it, so some would see a press and others would not. A whole frame per transition makes every system agree.
:::

The second rule is the merge, and the truth table below lists it in full. While either source holds a button, the game sees the button down. A press or release of one source counts as a transition only when the other source did not hold the button for the whole frame.

## A toy version

The toy models one key. A `Button` keeps the three flags of the earlier page. A person's event changes the device at once; a tool's event waits in a queue until the start of the next frame. The two merge functions are the whole rule.

```cpp sketch="input-simulated-toy.cpp"
// A toy virtual keyboard for one key: a queue of tool events applied at the frame boundary, merged with the device.
#include <cstdio>
#include <vector>

struct Button
{
	bool Down = false;
	bool Pressed = false;
	bool Released = false;

	void Set(bool down)
	{
		if (down && !Down)
			Pressed = true;
		else if (!down && Down)
			Released = true;
		Down = down;
	}

	void ClearTransitions()
	{
		Pressed = false;
		Released = false;
	}

	bool HeldThroughout() const { return Down && !Pressed && !Released; }
};

// A transition of one source counts only if the other source did not hold the key through the frame.
bool MergedPressed(const Button& device, const Button& tool)
{
	return (device.Pressed && !tool.HeldThroughout()) || (tool.Pressed && !device.HeldThroughout());
}

bool MergedReleased(const Button& device, const Button& tool)
{
	return (device.Released && !tool.HeldThroughout()) || (tool.Released && !device.HeldThroughout());
}

// What happens in one frame: the person's event arrives at once; the tool's is queued for the next frame.
struct Frame
{
	int Person; // 0 nothing, 1 press, 2 release
	int Tool;
};

void Run(const char* title, const std::vector<Frame>& frames)
{
	std::printf("%s\n", title);
	Button device;
	Button tool;
	std::vector<bool> queue;
	for (size_t i = 0; i < frames.size(); i++)
	{
		device.ClearTransitions(); // Input::BeginFrame
		tool.ClearTransitions();
		for (const bool down : queue)
			tool.Set(down);
		queue.clear();
		if (frames[i].Person != 0)
			device.Set(frames[i].Person == 1);
		std::printf("frame %zu: down %d pressed %d released %d\n", i + 1, static_cast<int>(device.Down || tool.Down),
			static_cast<int>(MergedPressed(device, tool)), static_cast<int>(MergedReleased(device, tool)));
		if (frames[i].Tool != 0)
			queue.push_back(frames[i].Tool == 1); // Applied at the next frame's start
	}
}

int main()
{
	Run("A tool taps a key nobody holds", { { 0, 1 }, { 0, 2 }, { 0, 0 }, { 0, 0 } });
	Run("A person holds the key, the tool taps it, the person lets go", { { 1, 0 }, { 0, 1 }, { 0, 2 }, { 2, 0 }, { 0, 0 } });
}
```

```text output-of="input-simulated-toy.cpp"
A tool taps a key nobody holds
frame 1: down 0 pressed 0 released 0
frame 2: down 1 pressed 1 released 0
frame 3: down 0 pressed 0 released 1
frame 4: down 0 pressed 0 released 0
A person holds the key, the tool taps it, the person lets go
frame 1: down 1 pressed 1 released 0
frame 2: down 1 pressed 0 released 0
frame 3: down 1 pressed 0 released 0
frame 4: down 0 pressed 0 released 1
frame 5: down 0 pressed 0 released 0
```

1. **Line 26:** a source held a key through the frame when it is down with no transition.
2. **Line 32:** one source's press counts only when the other source did not hold the key.
3. **Lines 55–59:** a frame starts by clearing transitions and applying the queue, as `Input::BeginFrame` does.
4. **Line 65:** the tool's event is queued, so it applies at the start of the next frame.

The toy runs two scenarios. In the first a tool taps a key nobody holds: the game sees the press one frame after the tool asked, and the release one frame after that. In the second a person holds the key, so the tool's press and release change nothing the game sees, and only the person's release counts.

Read frame 3 of the second scenario. The tool's press arrives in frame 3 (it was queued in frame 2) and the key is already held by the device, so `Pressed` stays 0. The game does not see a second press, and a script that jumps on a press does not jump twice.

## The real code

Strata stores one `ButtonStates` per source with the same three `std::bitset` sets as the toy, one bit per key. The real file adds three things the toy skips: many buttons, other kinds of events and the `Enabled` flag. The code is in the order data flows, from the call to the query.

### Queuing the events

`Input::SimulateKey` and its relatives check the code and push a small `SimulatedEvent` onto `s_State.Simulated.Queue`. Pointer moves, scrolls and :term[typed text]{id=typed-text} are events of the same list, with a position or a string in place of a flag.

The queue applies in `Input::BeginFrame`. The first part of that function clears the transitions of every source once the game has had them; the lines below come after that.

```cpp src="Strata/src/Strata/Input/Input.cpp#L577-L585" from="if (s_State.Suspended)" to="s_State.FrameSeen = true; // The game updates in this frame" symbol="Input::BeginFrame"
if (s_State.Suspended)
	return;

s_State.FrameIndex++;
SimulatedState& simulated = s_State.Simulated;
for (const SimulatedEvent& event : simulated.Queue)
	ApplySimulatedEvent(simulated, event);
simulated.Queue.clear();
s_State.FrameSeen = true; // The game updates in this frame
```

Three facts show here. A suspended input returns before the queue applies, so events wait. The frame counter grows before the events apply, which is why `SimulatedInput::Press` adds one to it. The events apply in order and the queue empties.

### Applying an event

Each event type has one case in `ApplySimulatedEvent`. A button event goes through `ButtonStates::Set`, which records a transition only when the state changes, exactly like the toy's `Set`.

```cpp src="Strata/src/Strata/Input/Input.cpp#L296-L330" symbol="ApplySimulatedEvent"
void ApplySimulatedEvent(SimulatedState& state, const SimulatedEvent& event)
{
	switch (event.Type)
	{
		case SimulatedEventType::Key:
			state.Keys.Set(event.Code, event.Down);
			break;
		case SimulatedEventType::MouseButton:
			state.MouseButtons.Set(event.Code, event.Down);
			break;
		case SimulatedEventType::GamepadButton:
			state.Gamepads[event.Gamepad].Connected = true;
			state.Gamepads[event.Gamepad].Buttons.Set(event.Code, event.Down);
			break;
		case SimulatedEventType::GamepadAxis:
			state.Gamepads[event.Gamepad].Connected = true;
			state.Gamepads[event.Gamepad].Axes[event.Code] = event.Value.x;
			break;
		case SimulatedEventType::GamepadAxisRelease:
			state.Gamepads[event.Gamepad].Axes[event.Code].reset();
			break;
		case SimulatedEventType::MouseMove:
			// Like a device, the first position only establishes where the pointer is.
			if (state.MousePosition)
				state.MouseDelta += event.Value - *state.MousePosition;
			state.MousePosition = event.Value;
			break;
		case SimulatedEventType::Scroll:
			state.ScrollDelta += event.Value;
			break;
		case SimulatedEventType::Text:
			AppendUTF8(state.TypedText, event.Text);
			break;
	}
}
```

1. **Lines 300–301:** a key event goes through `ButtonStates::Set`, which records a transition only for a change of state.
2. **Lines 306–308:** a gamepad button event also marks the pad as connected.
3. **Lines 317–321:** the first simulated move only sets the position; later moves add the difference to the frame's movement.

### The merge

The queries read both states. The helper below is a template over the number of buttons, so keys, mouse buttons and gamepad buttons share one rule. Its first parameter is a :term[pointer to a member]{id=pointer-to-a-member}: `std::bitset<Count> ButtonStates<Count>::* transition` names either the `Pressed` or the `Released` field, so one function serves both questions.

```cpp src="Strata/src/Strata/Input/Input.cpp#L162-L175" symbol="IsMergedTransition"
// A press or release of one source is a transition of the merged button only if the other source did not hold the button
// through the frame: a tool pressing or letting go of a key a person holds (or the other way round) changes nothing the game
// sees, and never restarts a key repeat.
template<size_t Count>
bool IsMergedTransition(std::bitset<Count> ButtonStates<Count>::* transition, const ButtonStates<Count>& device, const ButtonStates<Count>& simulated,
	size_t index)
{
	if (index >= Count)
		return false;
	const bool deviceTransition = s_State.Enabled && (device.*transition).test(index);
	const bool deviceHeld = s_State.Enabled && IsHeldThroughout(device, index);
	const bool simulatedTransition = (simulated.*transition).test(index);
	return (deviceTransition && !IsHeldThroughout(simulated, index)) || (simulatedTransition && !deviceHeld);
}
```

1. **Line 166:** the first parameter picks the `Pressed` or the `Released` set of both sources.
2. **Lines 171–173:** each source's own transition, and whether the device held the key through the frame.
3. **Line 174:** the device's transition counts unless the tool held the key through, and the tool's counts unless the device did.

## Truth table

The table lists, for one frame, what each source did and what the game sees. "Held" means down through the whole frame with no transition. Input is enabled.

| Device | Tool | Down | Pressed | Released |
| --- | --- | --- | --- | --- |
| up | up | no | no | no |
| up | pressed | yes | yes | no |
| up | released | no | no | yes |
| held | held | yes | no | no |
| held | pressed | yes | no | no |
| held | released | yes | no | no |
| pressed | held | yes | no | no |
| released | held | yes | no | no |
| pressed | pressed | yes | yes | no |
| released | released | no | no | yes |

When `Enabled` is false, the device column reads as "up" for the game, so the tool's transitions always count. The pair "pressed, pressed" is one press, not two: both sources pressed in the same frame, and neither held the key through it.

:::example
A person holds W to walk the Third-Person robot, and has done since input frame 100. At frame 120 an agent runs the `input.key` command for Space. The command calls `Input::SimulateKey` for Space. Nothing changes in frame 120.

At the start of frame 121, `BeginFrame` applies the event. Space is down and pressed in frame 121, and the robot's jump action, bound to Space, fires. W is still held by the device, with no transition, in every frame. If the agent also asked for W, the game would still see W held. It would see no press and no release of W: the jump and the walk do not interfere, and a repeat of W does not restart.
:::

## Simulated pointer and gamepads

The pointer has no button states, only a position, so it has its own rule: once a tool has moved the simulated pointer, `GetMousePosition` reports the simulated position and ignores the device's. The first simulated move only sets the position. Later moves add to the simulated movement of the frame, the way a device's moves do, and `GetMouseDelta` includes them. A move queued with `SimulateMouseMove` takes a position in pixels from the top-left corner of the input :term[viewport]{id=viewport-input}.

A simulated gamepad is connected as soon as a tool uses it, and stays connected until `ClearSimulated`. Its buttons merge with the device's, like keys. Its axes do not merge: while a tool holds an axis, its value replaces the device's value, and `ReleaseSimulatedGamepadAxis` hands the axis back to the device. The engine clamps a simulated axis value to the range of the axis.

The reason is that a stick has no "transition" to compare; two values cannot both hold. The tool wins while it holds, and the device wins again when the tool lets go.

## Release and clear

A tool that is done has two ways to end, and they differ.

`Input::ReleaseAllSimulated` lets go of every simulated key, mouse button, gamepad button and held axis. The releases are queued, so the game sees them in the next input frame as real transitions. It also drops presses and axis values that are still queued, so a press that never applied cannot apply after the release. Pointer moves, scrolls, typed text and axis releases stay queued.

`Input::ClearSimulated` forgets everything at once: the held state and the queue, with no releases. The editor calls it through `EditorContext::ResetSimulatedInput` when the game it served stops, and again when a new game starts. The game is gone, so nobody should see a release.

```cpp src="Strata/src/Strata/Input/Input.cpp#L741-L773" symbol="Input::ReleaseAllSimulated"
void Input::ReleaseAllSimulated()
{
	std::vector<SimulatedEvent>& queue = s_State.Simulated.Queue;
	queue.erase(std::remove_if(queue.begin(), queue.end(), [](const SimulatedEvent& event)
	{
		return event.Type == SimulatedEventType::Key || event.Type == SimulatedEventType::MouseButton || event.Type == SimulatedEventType::GamepadButton
			|| event.Type == SimulatedEventType::GamepadAxis;
	}), queue.end());
	for (KeyCode key = 0; key < c_MaxKeyCode; key++)
	{
		if (s_State.Simulated.Keys.Down.test(key))
			SimulateKey(key, false);
	}
	for (MouseCode button = 0; button < c_MaxMouseButtons; button++)
	{
		if (s_State.Simulated.MouseButtons.Down.test(button))
			SimulateMouseButton(button, false);
	}
	for (uint32_t gamepad = 0; gamepad < c_MaxGamepads; gamepad++)
	{
		const SimulatedGamepad& state = s_State.Simulated.Gamepads[gamepad];
		for (uint32_t button = 0; button < c_GamepadButtonCount; button++)
		{
			if (state.Buttons.Down.test(button))
				SimulateGamepadButton(gamepad, static_cast<GamepadButton>(button), false);
		}
		for (uint32_t axis = 0; axis < c_GamepadAxisCount; axis++)
		{
			if (state.Axes[axis])
				ReleaseSimulatedGamepadAxis(gamepad, static_cast<GamepadAxis>(axis));
		}
	}
}
```

1. **Lines 744–748:** presses and axis values still in the queue are dropped.
2. **Lines 749–753:** a release is queued for each simulated key that is down, and the same follows for buttons and axes.

The `IsSimulated*` queries answer from the simulated state as it stands in the current frame. Events still in the queue do not appear in them.

## Why durations count steps

The editor's `input.key` command taps for a number of fixed steps, not frames, and it holds the key by calling `Press` now and the release when the game has run the steps. A tap that lasted one frame would last 16.7 ms at 60 :term[frames per second]{id=frame-rate} and 8.3 ms at 120, so a test would play differently on two machines. Fixed steps make the tap last the same game time at any frame rate.

That mechanism is [the editor's stepping](../editor/stepping.md). This page needs one fact from it: `SimulatedInput::Press` records the input frame `Input::GetFrameIndex() + 1` as the first frame of the press. That frame is the one in which the queue applies.

## The test of the whole path

The feature test project runs a script, `InputFeatures`, whose runner feeds the device side of `Input` around a field named `PressFrame`, through `Input::ProcessKey` and the other process functions, as a window would. In the frame before it, the mouse moves to (100, 60). At `PressFrame`, Space and the left mouse button go down, the mouse moves to (120, 50) and the wheel scrolls by (0, 2). Gamepad 0 connects with A down, the left stick at (0.6, 0.8) and the right trigger at 0.5. One frame later nothing happens and everything stays down; two frames later Space, the button and A go up.

The script reads every query in each frame and expects the right answer, so the unit tests' small cases run once more across the whole path from the device state to the script. The simulated queue reaches scripts in the suite `Editor.Input`, whose test `Simulated gamepad buttons and axes reach the game's scripts` reads a simulated pad from a script. Around the presses it also rebinds actions, saves bindings and captures a binding. The feature test page, [the feature test](../engineering/feature-test.md), says how a script like this is checked.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Inject operating-system events into the window | Desktop test tools that drive any program | The game's own window code runs, so a test covers it | A window with focus, a display and one implementation per platform |
| Record raw device streams and replay them | Engines with replay systems | Exact reproduction of a real person's play | Recordings tied to one frame rate and one input format |
| Call the game's functions directly from the test | Unit tests of :term[game logic]{id=game-logic} | Speed and no input code at all | The input path, bindings and actions are never checked |

Sources are in Further reading.

## How it is tested

`StrataTests/src/Core/InputTests.cpp` holds the suites. Run them with `build/windows/bin/Debug/StrataTests.exe --test-suite=Core*` or through `ctest`. The cases that cover this page:

- `Simulated input applies at the next frame and is merged with the devices` checks that a press stays queued until `BeginFrame`, and that a key stays down while either source holds it.
- `A source pressing or releasing a button the other source holds reports no transition` is the merge rule: a person holds W, a tool presses and releases it, and the game sees no transition; with input disabled, the tool's transitions count.
- `Releasing all simulated input also drops presses still queued` and `Clearing simulated input forgets held keys and queued events without releases` cover the two ways to end.
- `Simulated input reaches the game while device input is disabled` covers the second contract rule.
- `The simulated pointer takes over the mouse position` and `Simulated gamepads connect when used, merge with the devices and release like keys` cover the pointer and the pads.

## Changing it safely

New kinds of simulated events extend `SimulatedEventType` and `ApplySimulatedEvent`, with a `Simulate*` function that checks its arguments. Add the case to the tests above, and to the feature script `InputFeatures`.

- Keep the queue. A change that applies events at once breaks the rule above and the suite `Simulated input applies at the next frame and is merged with the devices` will fail.
- Keep every query on the merge helpers. A query that reads only the device would ignore tools; one that reads only the simulated state would ignore people.
- Never make simulated input depend on the focus of a window. The game must run on a machine with no screen.
- Count tool durations in fixed steps in the editor, never in frames, as the [stepping page](../editor/stepping.md) explains.

Before a commit, run the `Core*` tests and the feature test. A change to the merge rule needs a new case in `InputTests.cpp` that fails without it.

## Summary

- A simulated press is queued and applies at the start of the next input frame, so every system of a frame agrees, and while input is suspended the queue waits.
- The game sees a button down while either source holds it; a source's press or release changes nothing when the other source already held the button for the whole frame.
- Releasing queues releases and drops queued presses; clearing forgets without any release, for a session that ended.
- A tap goes from `input.key` through `SimulatedInput::Press` and `Input::SimulateKey` into the queue, and `BeginFrame` of the next input frame makes `IsKeyPressed` true.

## Check yourself

1. A tool calls `Input::SimulateKey(Key::Space, true)` in the middle of input frame 50, after the physics system ran and before the scripts. Do the scripts of frame 50 see Space pressed?
   :::answer{tests="queue-frame"}
   No. The call only queues an event. The scripts of frame 50 see the old state; frame 51 applies the event at `BeginFrame`, and the scripts of frame 51 see Space down and pressed. Seeing the press in the middle of a frame would let the physics system and the scripts disagree.
   :::
2. A person holds E. A tool presses E and holds it for three frames. What do the scripts see in the frame where the tool's press applies?
   :::answer{tests="merge-rule"}
   E is down, not pressed and not released. The tool's press is no transition because the device held E through the frame. The same holds for every later frame, and the tool's release is also no transition while the person still holds E.
   :::
3. A tool holds the left stick at x = 0.5 while a person pushes the real stick to 1.0. What does the game read for that axis, and what after the tool calls `ReleaseSimulatedGamepadAxis`?
   :::answer{tests="merge-rule"}
   The game reads 0.5, because a held simulated axis replaces the device's value; the pad also counts as connected. After the release applies, the game reads 1.0 from the device again.
   :::
4. A tool holds Q and queues a press of E that has not applied. The editor calls `ReleaseAllSimulated`. Then it later calls `ClearSimulated` on a different game. Which key does the game see released in the first case, and in the second?
   :::answer{tests="release-clear"}
   In the first case Q is released in the next input frame, and E never goes down, because the queued press is dropped. In the second case no key sees a release: the state and the queue are forgotten at once.
   :::
5. A tap of Space starts when the game is at input frame 40. Which frame does `SimulatedInput::Press` record as the first frame, and which function turns the queued event into state?
   :::answer{tests="trace-tap"}
   Frame 41, one more than `Input::GetFrameIndex()` gives. `Input::BeginFrame` of frame 41 runs `ApplySimulatedEvent`, which sets the state; `Input::SimulateKey` only queued the event.
   :::

## Exercises

1. **Basic.** Write a program that prints the truth table by trying all 16 pairs of states, using the merge rule of the toy.
   :::answer[Worked solution]{tests="merge-rule" solution="sketches/input-simulated-table.cpp"}
   The program builds a `Button` for each state (up, pressed, released, held), tries every device state against every tool state and prints what the merge functions say. The output has 16 lines; the table in this page lists ten of them.

   ```cpp sketch="input-simulated-table.cpp"
   // The merge rule of one button, tried on every pair of states a source can be in during a frame.
   #include <cstdio>

   struct Button
   {
   	bool Down = false;
   	bool Pressed = false;
   	bool Released = false;

   	bool HeldThroughout() const { return Down && !Pressed && !Released; }
   };

   enum class State
   {
   	Up,
   	Pressed,
   	Released,
   	Held
   };

   const char* c_Names[] = { "up", "pressed", "released", "held" };

   Button MakeButton(State state)
   {
   	Button button;
   	button.Down = state == State::Pressed || state == State::Held;
   	button.Pressed = state == State::Pressed;
   	button.Released = state == State::Released;
   	return button;
   }

   int main()
   {
   	for (int d = 0; d < 4; d++)
   	{
   		for (int s = 0; s < 4; s++)
   		{
   			const Button device = MakeButton(static_cast<State>(d));
   			const Button tool = MakeButton(static_cast<State>(s));
   			const bool pressed = (device.Pressed && !tool.HeldThroughout()) || (tool.Pressed && !device.HeldThroughout());
   			const bool released = (device.Released && !tool.HeldThroughout()) || (tool.Released && !device.HeldThroughout());
   			std::printf("device %-8s tool %-8s down %d pressed %d released %d\n", c_Names[d], c_Names[s],
   				static_cast<int>(device.Down || tool.Down), static_cast<int>(pressed), static_cast<int>(released));
   		}
   	}
   }
   ```

   ```text output-of="input-simulated-table.cpp"
   device up       tool up       down 0 pressed 0 released 0
   device up       tool pressed  down 1 pressed 1 released 0
   device up       tool released down 0 pressed 0 released 1
   device up       tool held     down 1 pressed 0 released 0
   device pressed  tool up       down 1 pressed 1 released 0
   device pressed  tool pressed  down 1 pressed 1 released 0
   device pressed  tool released down 1 pressed 1 released 1
   device pressed  tool held     down 1 pressed 0 released 0
   device released tool up       down 0 pressed 0 released 1
   device released tool pressed  down 1 pressed 1 released 1
   device released tool released down 0 pressed 0 released 1
   device released tool held     down 1 pressed 0 released 0
   device held     tool up       down 1 pressed 0 released 0
   device held     tool pressed  down 1 pressed 0 released 0
   device held     tool released down 1 pressed 0 released 0
   device held     tool held     down 1 pressed 0 released 0
   ```

   1. **Lines 23–30:** a button for each state, with the flags a source would show in a frame of that kind.
   2. **Lines 40–41:** the merge rule of the toy, written inline for the pair under test.
   :::
2. **Medium.** Trace it yourself: find where an `input.key` tap for Space reaches the queue and where a script reads it, naming the files and functions in order. Assume the game is at input frame 40.
   :::answer[Worked solution]{tests="trace-tap"}
   The command `input.key` is registered in `StrataEditor/src/Editor/EditorInputCommands.cpp`; its handler calls `RunButtonAction`, which calls `SimulatedInput::Press` in `StrataEditor/src/Editor/SimulatedInput.cpp`. `Press` records frame 41 (`Input::GetFrameIndex() + 1`) as the first frame and the next fixed step as the first step, then calls its local `SimulateControl`, which calls `Input::SimulateKey` in `Strata/src/Strata/Input/Input.cpp`. That pushes a `SimulatedEvent` onto the queue. `Input::BeginFrame` of frame 41 runs `ApplySimulatedEvent` and sets the transition, and a script's `Input::IsKeyPressed(Key::Space)` in frame 41 calls the host function `HostIsKeyPressed` in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`, which asks the engine's `Input::IsKeyPressed`, which reads it through `IsMergedTransition`.
   :::
3. **Hard.** In a scratch branch, change the pressed case of `IsMergedTransition` so that a tool's press counts even when the device holds the key. Predict which test fails and which check inside it, then run the `Core*` tests.
   :::answer[Worked solution]{tests="merge-rule"}
   Drop the `!deviceHeld` part of the tool's term. The test `A source pressing or releasing a button the other source holds reports no transition` fails: after the person holds W and the tool presses it, `CHECK_FALSE(Input::IsKeyPressed(Key::W))` is the first check that fails, because the game now sees a second press. The test `Simulated input applies at the next frame and is merged with the devices` still passes, since its keys are never held by a device through a frame. The failure shows that the rule exists so that a tool cannot restart the repeat that a menu counts from a person's press of a key.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Input/Input.cpp` and `Strata/src/Strata/Input/Input.h`: the `Simulate*` functions, `BeginFrame`, the merge helpers and the `IsSimulated*` queries.
- `StrataEditor/src/Editor/SimulatedInput.cpp`: the editor's holds, and `StrataEditor/src/Editor/EditorInputCommands.cpp`: the `input.*` commands.
- `StrataTests/src/Core/InputTests.cpp`: the unit tests; `StrataTests/FeatureTest/Scripts/InputFeatures.cpp`: the feature script.

## Further reading

- Gaffer On Games, "Fix Your Timestep": the case for fixed steps, advanced.
- The documentation of GLFW's input guide: how real devices report events, beginner.
