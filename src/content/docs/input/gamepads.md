---
id: input/gamepads
title: "Gamepads"
description: "How Strata reads gamepads: one layout for every model, dead zones that steady a resting stick, and two thresholds that stop a button from flickering."
kind: internals
size: M
tracks: [E]
needs: [input/devices-state, basics/math-vectors]
time: 50
learn:
  - id: conventions
    text: name the layout and the value ranges of Strata's gamepads and the steps that turn GLFW's values into them
  - id: dead-zone-choice
    text: choose a dead zone for a stick and say what a value that is too small or too large costs
  - id: diagonals
    text: explain why an axial dead zone snaps diagonals toward the axes and a radial one keeps the direction
  - id: two-thresholds
    text: explain why an axis used as a button needs two thresholds, and trace the states for a series of readings
  - id: absences
    text: name what Strata does not do for gamepads, and what a game must do instead
since: 0.3.0
status: final
---

A gamepad is a box of switches and springs, and a game wants to ask it simple questions: is the jump button down, and how far is the left stick pushed? This page teaches how Strata answers them for hundreds of controller models. It covers the mapping database that gives every model one layout, the value ranges that layout promises, the polling code, and the dead zones and thresholds that turn a noisy stick into steady movement. The per-frame state and the window feed belong to [Devices and the per-frame state](devices-state.md), and the actions that read the values to [Input actions](actions.md).

## The problem and how engines solve it

Imagine that you make a robot walk with the left stick. One controller reports the stick's sideways movement as its axis 0 and its forward movement as axis 1. Another model puts the triggers on axes 2 and 5, or numbers its buttons in a different order. Each maker chose an order. A game that trusts the numbers works with one model and fails with the next.

A second problem hides in the stick. It is a small lever held by a spring, and the spring never returns it exactly to the middle. A worn stick may rest at 0.04 sideways and -0.03 forward. If the game moves the robot by that value, the robot creeps across the floor while nobody touches the pad.

Engines solve the first problem in three ways. They can write code for each model, which never ends. They can ask the player to map every button, which players dislike. Or they can keep a database that translates each model to the standard layout, and Strata takes this way: it gets the database from its window library.

For the second problem, every engine ignores small values, and engines differ in the shape of what they ignore, as the dead zone sections show.

## The map

Figure 1 shows how a value travels from the controller to a game script. Everything after the window library runs on the :term[main thread]{id=main-thread}.

```mermaid caption="A controller's values pass through the window library's mapping, a polling function of the window that converts them, and the input state, which the script kit and the input actions read." alt="A flow from left to right. The controller feeds the window library, whose mapping database turns the model into the standard layout. A polling function of the window converts signs and ranges and writes the input state. The script kit and the input actions both read the input state."
flowchart LR
  C[Controller] --> G[GLFW: mapping database]
  G --> P[GLFWWindow::PollGamepads]
  P --> I[Input: gamepad state]
  I --> S[StrataScript Input: dead zones]
  I --> A[InputActions: thresholds]
```

The database is `Strata/vendor/glfw/src/mappings.h`, which :term[GLFW]{id=glfw} 3.4 compiles in. The window code is `Strata/src/Platform/GLFW/GLFWWindow.cpp`, the state is `Strata/src/Strata/Input/Input.cpp`, and the codes are `Strata/src/Strata/Input/GamepadCodes.h`. The dead zones are in `StrataScriptCore/Include/StrataScript/Input.h`, and the thresholds in `Strata/src/Strata/Input/InputActions.cpp`.

## The contract

A **gamepad mapping** is a line of text that says which of a controller model's raw buttons and axes plays which part of the standard layout. It holds the model's identifier, its name, and pairs such as `a:b0` ("the standard A button is raw button 0") and `lefty:a1` ("the left stick's forward movement is raw axis 1"). GLFW holds more than 900 lines, copied from the community project `SDL_GameControllerDB`, and picks the one that matches a connected controller.

The standard layout is that of an Xbox controller. What callers may assume, and must do, follows from it.

1. **There are four gamepads, numbered 0 to 3, each with 15 buttons and 6 axes.** The constants are `c_MaxGamepads`, `c_GamepadButtonCount` and `c_GamepadAxisCount`. A number outside the range reads as nothing pressed, so a script cannot crash on a bad number.
2. **Sticks run from -1 to 1, with +X to the right and +Y up.** GLFW reports +Y down, so the window flips the sign. The reason is the rest of the engine: a push forward is a positive number, as it is for a key.
3. **Triggers run from 0 (released) to 1 (fully pressed).** GLFW reports -1 to 1, so the window remaps them. A trigger is a **half axis**: an axis that takes values on one side of zero only. `GetGamepadAxisMinimum` returns the lowest value of an axis, -1 for a stick and 0 for a trigger.
4. **A pad that is not connected is at rest.** Every stick and trigger reads 0 and every button reads up, so a game never reads the last values of a pad that was pulled out.
5. **`Input` returns the device's values, without a dead zone.** A menu, a racing game and a shooter want different amounts of filtering, so the reader chooses. While input is disabled (`Input::SetEnabled`), the axes read at rest instead.
6. **The codes are never renumbered.** They are part of the script ABI (the application binary interface between the engine and a script module), so a compiled script that uses `GamepadButton::A` keeps its meaning after an update.

The button numbers 0 to 14 follow GLFW's standard order: A, B, X, Y, the two bumpers, Back, Start, Guide, the two stick presses and the four directions of the D-pad.

:::rule[Controls that players change are read as input actions]
Gameplay and interface code reads controls that players can change through input actions. The raw queries of this page are for code that wants the device itself.
:::

## A toy version

The second problem, the creeping robot, needs a function that turns a raw reading into the reading a game wants. The program below applies a dead zone to one axis. Values within 0.15 of rest become 0, and the rest is stretched so that a full push still gives 1.

:::question
New to C++ functions and loops? Read [Programming basics 2](../basics/programming-2.md) and [Programming basics 3](../basics/programming-3.md) first.
:::

Check the line that subtracts the dead zone, then read the output to see what each device value becomes.

```cpp sketch="input-gamepads-toy.cpp"
// A dead zone on one axis: values near rest read 0, the rest is rescaled so that full tilt still reads 1.
#include <cmath>
#include <cstdio>

namespace
{
	float ApplyDeadZone(float value, float deadZone)
	{
		const float magnitude = std::fabs(value);
		if (magnitude <= deadZone)
			return 0.0f;
		const float scaled = (magnitude - deadZone) / (1.0f - deadZone);
		return value < 0.0f ? -scaled : scaled;
	}
}

int main()
{
	const float readings[] = { 0.02f, -0.08f, 0.15f, 0.20f, 0.575f, -1.0f, 1.0f };
	for (const float reading : readings)
		std::printf("device %+.3f -> game %+.4f\n", reading, ApplyDeadZone(reading, 0.15f));
	return 0;
}
```

```text output-of="input-gamepads-toy.cpp"
device +0.020 -> game +0.0000
device -0.080 -> game +0.0000
device +0.150 -> game +0.0000
device +0.200 -> game +0.0588
device +0.575 -> game +0.5000
device -1.000 -> game -1.0000
device +1.000 -> game +1.0000
```

1. **Lines 10–11:** a value within the dead zone, the test being "at most", reads 0.
2. **Line 12:** the part beyond the dead zone is divided by the room that is left.
3. **Line 13:** the sign comes back, so the left side works as the right side does.

A resting 0.02 or -0.08 reads 0, so the robot stands still. A value of 0.575 reads 0.5: the 0.425 beyond the dead zone is divided by 0.85. This stretching is **rescaling**, the step that maps the range outside a dead zone back onto the full range. Without it, a stick pushed to the end would read 0.85, and the robot would never reach its top speed.

## Dead zones: axial and radial

A **dead zone** is the region around a stick's rest position inside which it reads as untouched. A stick has two axes, so the choice is how to apply the region to both. An axial dead zone treats each axis alone, and its region is a square. A radial one looks at the stick's length, the distance of its position from the middle, as [Vectors](../basics/math-vectors.md) teaches, and its region is a circle.

Take a push to (0.2, 0.6) with a dead zone of 0.15. The push points about 18.4 degrees from straight up, since the sideways part is a third of the forward part.

- **Axial.** The sideways 0.2 becomes (0.2 - 0.15) / 0.85, which is 0.0588. The forward 0.6 becomes 0.5294. The result points about 6.3 degrees from straight up.
- **Radial.** The length is 0.6325, which becomes (0.6325 - 0.15) / 0.85 = 0.5676. The result is the direction times that length: (0.1795, 0.5385). It points 18.4 degrees from straight up, as the player pushed.

The axial result has the right size and the wrong direction. Each axis loses its dead zone alone, so a small sideways push loses most of its value, and the character walks nearly straight when the player steered a little. This is why diagonals snap toward the axes. A radial dead zone cuts the length and leaves the direction alone, which is why `GetGamepadStick` is radial.

An axial dead zone still fits a single axis, such as a trigger, which has no direction to keep. Figure 2 shows one axis with a dead zone of 0.15: flat at 0, then a steeper line that still reaches 1.

```mermaid caption="The reading of one axis against the device value for a dead zone of 0.15: flat at zero until 0.15, then a steeper line that still ends at one, beside the unchanged device value." alt="A line chart with the device value from 0 to 1 on the horizontal axis. One line is the device value itself, a straight diagonal. The other stays at zero until 0.15 and then rises more steeply to meet the first at 1."
xychart-beta
  title "Reading against device value, dead zone 0.15"
  x-axis [0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1]
  y-axis "Reading" 0 --> 1
  line [0, 0, 0, 0.0588, 0.1765, 0.2941, 0.4118, 0.5294, 0.7647, 1]
  line [0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1]
```

:::why[Why 0.15]
The SDK's `c_DefaultDeadZone` is 0.15. A dead zone must exceed the noise of the worst stick that a player owns, and it costs reach, since the first 15 % of the travel does nothing. A game with fine aim may lower it, at the price of drift on a worn pad. A menu may raise it.
:::

## The real code, in the order the data flows

The window polls every pad once per frame, right after the window library handles the :term[operating system's]{id=operating-system} events. Check the test that decides whether a pad is a gamepad, the sign flips, the remap, and the call that reports a missing pad.

```cpp src="Strata/src/Platform/GLFW/GLFWWindow.cpp#L416-L442" symbol="GLFWWindow::PollGamepads"
void GLFWWindow::PollGamepads()
{
	for (uint32_t gamepad = 0; gamepad < c_MaxGamepads; gamepad++)
	{
		const int joystick = GLFW_JOYSTICK_1 + static_cast<int>(gamepad);
		GLFWgamepadstate state;
		if (glfwJoystickIsGamepad(joystick) && glfwGetGamepadState(joystick, &state))
		{
			bool buttons[c_GamepadButtonCount];
			for (uint32_t index = 0; index < c_GamepadButtonCount; index++)
				buttons[index] = state.buttons[index] == GLFW_PRESS;
			// Input's conventions (GamepadCodes.h): sticks +Y up (GLFW reports +Y down), triggers 0 to 1 (GLFW: -1 to 1).
			float axes[c_GamepadAxisCount];
			axes[static_cast<size_t>(GamepadAxis::LeftX)] = state.axes[GLFW_GAMEPAD_AXIS_LEFT_X];
			axes[static_cast<size_t>(GamepadAxis::LeftY)] = -state.axes[GLFW_GAMEPAD_AXIS_LEFT_Y];
			axes[static_cast<size_t>(GamepadAxis::RightX)] = state.axes[GLFW_GAMEPAD_AXIS_RIGHT_X];
			axes[static_cast<size_t>(GamepadAxis::RightY)] = -state.axes[GLFW_GAMEPAD_AXIS_RIGHT_Y];
			axes[static_cast<size_t>(GamepadAxis::LeftTrigger)] = (state.axes[GLFW_GAMEPAD_AXIS_LEFT_TRIGGER] + 1.0f) * 0.5f;
			axes[static_cast<size_t>(GamepadAxis::RightTrigger)] = (state.axes[GLFW_GAMEPAD_AXIS_RIGHT_TRIGGER] + 1.0f) * 0.5f;
			Input::ProcessGamepad(gamepad, true, axes, buttons);
		}
		else
		{
			Input::ProcessGamepad(gamepad, false, nullptr, nullptr);
		}
	}
}
```

1. **Line 422:** a controller counts only when it has a mapping and GLFW can read its state.
2. **Line 430:** the left stick's forward value changes sign, so up is positive; line 432 does the same for the right stick.
3. **Lines 433–434:** a trigger from -1 to 1 becomes 0 to 1, by adding 1 and halving.
4. **Line 439:** a slot without a gamepad reports a pad that is not connected, so its values rest.

The toy had no device, and the real code differs in three ways. It loops over the first four of GLFW's slots, although GLFW has 16. A controller counts only when it has a mapping: otherwise `glfwJoystickIsGamepad` is false and the slot is reported as not connected. And no dead zone is applied here; the values go to `Input` as the device sends them.

`Input::ProcessGamepad` stores them. Check what it does with a value that is not a number and with a pad that is not connected.

```cpp src="Strata/src/Strata/Input/Input.cpp#L663-L679" symbol="Input::ProcessGamepad"
void Input::ProcessGamepad(uint32_t gamepad, bool connected, const float* axes, const bool* buttons)
{
	if (gamepad >= c_MaxGamepads)
		return;

	GamepadState& state = s_State.Gamepads[gamepad];
	state.Connected = connected;
	for (uint32_t index = 0; index < c_GamepadAxisCount; index++)
	{
		// At rest without a device; finite values within the axis' range otherwise.
		const GamepadAxis axis = static_cast<GamepadAxis>(index);
		const float value = connected && axes && std::isfinite(axes[index]) ? axes[index] : GetRestValue(axis);
		state.Axes[index] = std::clamp(value, GetGamepadAxisMinimum(axis), 1.0f);
	}
	for (uint32_t index = 0; index < c_GamepadButtonCount; index++)
		state.Buttons.Set(index, connected && buttons ? buttons[index] : false);
}
```

1. **Lines 665–666:** a number beyond the last pad is ignored.
2. **Line 674:** a pad that is not connected, or a value that is not finite, takes the rest value.
3. **Line 675:** every value is clamped to the range of its axis.
4. **Line 678:** a button of a pad that is not connected reads up.

A faulty driver can send a value that is not a number, or one outside the range. The function clamps each axis to its range and reads a value that is not finite as rest, so nothing downstream sees one. A pad that is not connected passes the same lines with `connected` false, which gives 0 on every axis and up on every button.

`Input::GetGamepadAxis` in `Strata/src/Strata/Input/Input.h` returns the stored value. The dead zones live in the script kit, short enough for a game maker to copy. Check how the dead zone is tested before the rescaling.

```cpp src="StrataScriptCore/Include/StrataScript/Input.h#L326-L339" symbol="Input::GetGamepadAxis"
// An axis with a dead zone: values within it read 0, the rest is rescaled so that the axis still reaches 1 (a dead zone
// of 0 reads the device's value).
static float GetGamepadAxis(GamepadAxis axis, uint32_t gamepad = 0, float deadZone = c_DefaultDeadZone)
{
	const StrataScriptHostAPI* host = ST_SCRIPT_DETAIL_HOST_WITH(GetGamepadAxis);
	const float value = host ? host->GetGamepadAxis(Detail::GetContext(), gamepad, static_cast<uint32_t>(axis)) : 0.0f;
	const float magnitude = value < 0.0f ? -value : value;
	if (!(deadZone > 0.0f))
		return value;
	if (magnitude <= deadZone || deadZone >= 1.0f)
		return 0.0f;
	const float scaled = (magnitude - deadZone) / (1.0f - deadZone);
	return value < 0.0f ? -scaled : scaled;
}
```

1. **Lines 333–334:** a dead zone of 0 or less returns the device's value.
2. **Lines 335–336:** a value within the dead zone, or a dead zone of 1 or more, reads 0.
3. **Line 337:** the same rescaling as in the toy.

A dead zone of 0 or less returns the device's value, as the comment says. A dead zone of 1 or more returns 0 always, so the division never runs by zero. The rest is the toy, with its guard clauses. For a stick, `GetGamepadStick` reads both axes without a dead zone and applies the radial one.

```cpp src="StrataScriptCore/Include/StrataScript/Input.h#L341-L353" symbol="Input::GetGamepadStick"
// A stick as a vector (+X right, +Y up) with a round dead zone: small tilts in any direction read zero, diagonals keep
// their direction, and the length reaches 1 at full tilt (it never exceeds 1). What character movement wants.
static glm::vec2 GetGamepadStick(GamepadStick stick, uint32_t gamepad = 0, float deadZone = c_DefaultDeadZone)
{
	const bool left = stick == GamepadStick::Left;
	const glm::vec2 value(GetGamepadAxis(left ? GamepadAxis::LeftX : GamepadAxis::RightX, gamepad, 0.0f),
		GetGamepadAxis(left ? GamepadAxis::LeftY : GamepadAxis::RightY, gamepad, 0.0f));
	const float length = glm::length(value);
	if (!(length > deadZone) || deadZone >= 1.0f)
		return glm::vec2(0.0f);
	const float scaled = glm::min((length - glm::max(deadZone, 0.0f)) / (1.0f - glm::max(deadZone, 0.0f)), 1.0f);
	return value / length * scaled;
}
```

1. **Lines 346–347:** both axes are read without a dead zone, so the stick's true position is known.
2. **Lines 349–350:** a length within the dead zone reads (0, 0).
3. **Line 351:** the length is scaled to the room beyond the dead zone and capped at 1.
4. **Line 352:** the unit direction times the new length keeps the direction.

Each axis is clamped to 1, so a stick that moves in a square can report (1, 1), which has length 1.41. The `glm::min` caps the scaled length at 1, so the result never exceeds a full push.

:::example[The robot walks]
The Third-Person sample's project has a `Move` action of the kind Vector2, bound to `Gamepad/LeftStick` with the dead zone 0.15. A worn stick at rest reads (0.04, -0.03), which has length 0.05, so `Move` reads (0, 0) and the robot stands. A push to (0, 0.6) reads (0, 0.5294), and a push to the end reads (0, 1).
:::

## Hysteresis: an axis used as a button

A game sometimes wants an axis to act as a button, such as a trigger that fires. The plain rule is one threshold: down while the value exceeds 0.5. A finger holding a trigger near 0.5 shakes by a few percent, so the button goes down and up again and again.

**Hysteresis** means two thresholds: one enables the state, and a lower one disables it, so that a value near a threshold cannot make the state flicker. Strata's actions press above 0.5 and release at 0.35 or below, in `c_Press` and `c_Release`. The state of a half axis is kept for each gamepad, in `Strata/src/Strata/Input/InputActions.cpp`. Table 1 follows a trigger through nine readings, with one threshold and with two.

| Step | Reading | One threshold, 0.5 | Two thresholds, 0.5 and 0.35 |
| --- | --- | --- | --- |
| 1 | 0.49 | up | up |
| 2 | 0.51 | down | down |
| 3 | 0.49 | up | down (still above 0.35) |
| 4 | 0.51 | down | down |
| 5 | 0.49 | up | down |
| 6 | 0.40 | up | down |
| 7 | 0.34 | up | up (at or below 0.35) |
| 8 | 0.45 | up | up (not above 0.5) |
| 9 | 0.55 | down | down |

The single threshold changes state five times after the first step. The two thresholds change it three times, and each change is a real push or a real release. An Axis or Vector2 action read as down uses the same two numbers, and [Input actions](actions.md) teaches how the actions apply them.

The word has a second use. The world streamer keeps a cell loaded until the camera is farther away than the radius that loaded it, so a camera at the border cannot make a cell load and unload every frame. [The world streamer](../worlds/streamer.md) shows it.

## Several gamepads, and a game in the background

`Input::IsGamepadConnected` tells whether a pad is connected, and the pad's number is an argument of every gamepad query of the script kit. A gamepad binding of an action reads every pad: a button is down when it is down on any pad, and a whole axis takes the pad pushed furthest. The test `A whole axis reads the gamepad pushing it furthest, either way` of the suite `Core.InputActions` checks this with four pads.

The release notes of 0.7.0 say that gamepads are still read while an exported game is in the background. The polling code above never asks whether the window has the focus. In the editor, the Game view disables `Input` while it lacks the focus or the game is not playing, so the sticks read at rest there.

## What Strata does not do

- **Force feedback.** A search of the engine's sources for rumble or vibration finds nothing, so a game cannot make a pad shake.
- **Pads assigned to players.** A gamepad binding reads every pad, and all players share one set of actions. A game for two local players reads pad 0 and pad 1 itself with the raw queries.
- **Controllers missing from the database.** A model without a mapping reads as not connected and keeps its slot, so a player's first real pad may be gamepad 1. Nothing in the engine calls GLFW's function that adds mappings, so a game cannot add one.
- **More than four pads.** The code reads GLFW's first four slots only.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| The gamepad interface of `SDL` | Many games and engines | Rumble, hot-plug events, hints that add mappings | A second library beside GLFW |
| `XInput` | Windows games | A fixed layout with no database, and rumble | Other controllers and systems |
| `GameInput` | Newer Windows games | One interface for many devices | Other systems, and a new dependency |
| The raw device interface of the system | Engines that read devices themselves | Special devices | A mapping for each model, kept by the engine |

## How it is tested

The tests need no :term[graphics card]{id=gpu} and no real pad: they feed values to `Input::ProcessGamepad` or simulate a pad. In the suite `Core.Input`, the test `Gamepad axes are clamped to their ranges and rest at zero, triggers at released` sends 2 and -3 for the sticks and a value that is not a number, and expects 1, -1 and 0. The test `Simulated gamepads connect when used, merge with the devices and release like keys` covers the pad that a command drives. The suite `Scripting.Input` checks that scripts read both kinds of pad. Run a suite directly:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Core.Input
```

The polling function needs a real window and a real pad, and the window-backend tests feed a fake window with pads instead.

## Changing it safely

The buttons cannot grow alone: a compile-time check in `GLFWWindow.cpp` demands that they are GLFW's 15, in GLFW's order, because `PollGamepads` copies GLFW's button array. Any new code is appended at the end of its enum in `GamepadCodes.h` and in the script kit. Never insert one or change a number, since compiled scripts hold the old numbers. A change that breaks compatibility raises the ABI version of the scripts; an appended one does not.

A :term[window backend]{id=window-backend} other than GLFW writes its own polling function and calls `Input::ProcessGamepad` with the contract's signs and ranges. The checks to pass are the suites `Core.Input`, `Core.InputActions` and `Scripting.Input`, and the feature test, which exercises every script function.

## Summary

- Strata gives every controller one Xbox layout of 15 buttons, 6 axes and 4 pads. Sticks run from -1 to 1 (+Y up) and triggers from 0 to 1, all made by GLFW's database and the window's polling.
- A dead zone of 0.15 hides a resting stick and rescaling makes the rest reach 1; a dead zone too small lets the stick drift, and one too large hides the start of the movement.
- An axial dead zone cuts each axis alone and snaps a diagonal toward the axes; a radial one cuts the length and keeps the direction.
- An axis used as a button presses above 0.5 and releases at 0.35, so a reading near a threshold cannot flicker.
- Strata has no rumble, no pads assigned to players, no mappings that a game adds and no more than four pads.

## Check yourself

1. A stick rests at (0.05, -0.12). What does `GetGamepadStick` return with the default dead zone, and what does an axial dead zone of 0.15 return?

   :::answer{tests="dead-zone-choice,diagonals"}
   The length is about 0.13, within 0.15, so `GetGamepadStick` returns (0, 0). The axial one also returns (0, 0), since both values are within 0.15. They differ only for stronger pushes.
   :::

2. Which statement is wrong? (a) GLFW reports +Y down for a stick. (b) Strata's triggers run from 0 to 1. (c) The window applies the dead zone before it stores the stick. (d) A pad without a mapping reads as not connected.

   :::answer{tests="conventions,absences"}
   Statement (c) is wrong: `Input` stores the device's values, and the script kit or the actions apply the dead zone. Statements (a), (b) and (d) are what the polling function does.
   :::

3. A trigger gives 0.52, 0.48, 0.36, 0.34 and 0.40 in turn. With the thresholds 0.5 and 0.35, what are the states, starting from up?

   :::answer{tests="two-thresholds"}
   Down at 0.52, still down at 0.48 and 0.36 (above 0.35), up at 0.34 (at or below 0.35), and still up at 0.40 (not above 0.5). A single threshold of 0.5 would go up at 0.48.
   :::

## Exercises

1. **Medium.** Predict the axial and radial readings of a stick at (0.1, 0.1), (0.2, 0) and (0.6, 0.6) with a dead zone of 0.15, then run the sketch.

   :::answer[Worked solution]{tests="diagonals,dead-zone-choice" solution="sketches/input-gamepads-stick.cpp"}
   By hand, (0.1, 0.1) gives (0, 0) in both, since each value and the length 0.14 are within 0.15. (0.2, 0) gives 0.0588 on the x axis in both, since one axis has the same value and length. (0.6, 0.6) gives 0.5294 on each axis for the axial one, and for the radial one the length 0.8485 becomes 0.8218, so each value is 0.5811.

   ```cpp sketch="input-gamepads-stick.cpp"
   // An axial and a radial dead zone side by side, with the default dead zone of 0.15.
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   #include <glm/glm.hpp>

   namespace
   {
   	constexpr float c_DeadZone = 0.15f;

   	float Rescale(float magnitude)
   	{
   		return (magnitude - c_DeadZone) / (1.0f - c_DeadZone);
   	}

   	glm::vec2 Axial(const glm::vec2& stick)
   	{
   		glm::vec2 result(0.0f);
   		for (int index = 0; index < 2; index++)
   		{
   			const float magnitude = std::fabs(stick[index]);
   			if (magnitude > c_DeadZone)
   				result[index] = std::copysign(Rescale(magnitude), stick[index]);
   		}
   		return result;
   	}

   	glm::vec2 Radial(const glm::vec2& stick)
   	{
   		const float length = glm::length(stick);
   		if (!(length > c_DeadZone))
   			return glm::vec2(0.0f);
   		return stick / length * std::min(Rescale(length), 1.0f);
   	}
   }

   int main()
   {
   	const glm::vec2 sticks[] = { glm::vec2(0.1f, 0.1f), glm::vec2(0.2f, 0.0f), glm::vec2(0.6f, 0.6f) };
   	for (const glm::vec2& stick : sticks)
   	{
   		const glm::vec2 axial = Axial(stick);
   		const glm::vec2 radial = Radial(stick);
   		std::printf("stick (%.2f, %.2f): axial (%.4f, %.4f), radial (%.4f, %.4f)\n", stick.x, stick.y, axial.x, axial.y, radial.x, radial.y);
   	}
   	return 0;
   }
   ```

   ```text output-of="input-gamepads-stick.cpp"
   stick (0.10, 0.10): axial (0.0000, 0.0000), radial (0.0000, 0.0000)
   stick (0.20, 0.00): axial (0.0588, 0.0000), radial (0.0588, 0.0000)
   stick (0.60, 0.60): axial (0.5294, 0.5294), radial (0.5811, 0.5811)
   ```

   1. **Lines 17–27:** the axial function cuts each axis alone.
   2. **Lines 29–35:** the radial function cuts the length and keeps the direction.
   :::

2. **Medium.** Trace it yourself. Find where a pad's forward stick value changes sign, and what happens in the same function when no pad is connected.

   :::answer[Worked solution]{tests="conventions"}
   Search for `glfwGetGamepadState`: it is in `GLFWWindow::PollGamepads` in `Strata/src/Platform/GLFW/GLFWWindow.cpp`. A breakpoint on the line with `GLFW_GAMEPAD_AXIS_LEFT_Y` shows a stick pushed forward changing from negative to positive, and a released trigger going from -1 to 0. Without a pad, the `else` branch calls `Input::ProcessGamepad` with `false`, and every axis rests.
   :::

3. **Hard.** A racing game reads the right trigger as a button for its menu. Say what one threshold would do, why two are better, and which two you choose.

   :::answer[Worked solution]{tests="two-thresholds,absences"}
   A trigger held near the one threshold flickers with the shake of the finger, so the menu would select and cancel again and again. Two thresholds fix this: a press at 0.5 is far from rest, and a release at 0.35 leaves a gap of 0.15, wider than the shake. A smaller gap would flicker again, and a much wider one makes the release feel late. The engine's 0.5 and 0.35 are a good start, and a test with a real pad shows whether to change them.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Input/GamepadCodes.h`: the buttons, axes, counts and `GetGamepadAxisMinimum`.
- `Strata/src/Platform/GLFW/GLFWWindow.cpp`: `GLFWWindow::PollGamepads`.
- `Strata/src/Strata/Input/Input.cpp`: `Input::ProcessGamepad` and the stored state.
- `StrataScriptCore/Include/StrataScript/Input.h`: `Input::GetGamepadAxis`, `Input::GetGamepadStick`, `Input::c_DefaultDeadZone`.
- `Strata/src/Strata/Input/InputActions.cpp`: the thresholds, with `c_Press` and `c_Release` in `InputActions.h`.
- `Strata/vendor/glfw/src/mappings.h`: the mapping database.
- Tests: the suites `Core.Input`, `Core.InputActions` and `Scripting.Input`.

## Further reading

- GLFW documentation, "Input guide" (<https://www.glfw.org/docs/latest/input_guide.html>): joysticks, gamepad mappings and the function that adds them. Level: intermediate.
- SDL_GameControllerDB (<https://github.com/mdqinc/SDL_GameControllerDB>): the community database that GLFW compiles in. Level: intermediate.
- Microsoft, "Getting started with XInput" (<https://learn.microsoft.com/en-us/windows/win32/xinput/getting-started-with-xinput>): the dead zone constants and the four-controller limit of XInput. Level: intermediate.
