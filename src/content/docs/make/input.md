---
id: make/input
title: "Input and input actions"
description: "Move the ball with keys and a gamepad, then name the controls as input actions that players can change."
kind: tutorial
size: L
tracks: [G, B]
needs: [make/scripting-scene]
time: 90
learn:
  - id: why-actions
    text: explain why a game names its controls as input actions instead of reading keys
  - id: read-devices
    text: write a script that reads keys, the mouse and a gamepad stick with its dead zone
  - id: define-actions
    text: create a map with Button and Vector2 actions and bind keys and sticks to them
  - id: read-actions
    text: write a script that reads a Vector2 action, a held Button and a pressed Button
  - id: choose-direct
    text: choose between reading an input action and reading a device directly
since: 0.3.0
status: final
---

## What you will make

Coin Run's ball moves over the ground when you press W, A, S and D, push the left stick, or use the arrow keys. All of it comes from one action named Move, and you can change its controls in the project without touching the code.

::figure{id=ball-on-ground}

## Why games name actions

A game must know what the player does. The direct way is to ask the devices: is the W key down, how far is the left stick tilted? That works for a while. Then a player wants a gamepad, or wants Space on another key, or plays on a keyboard with another layout. If your code says `Key::W`, you change the code for each wish.

So a game names what the player means. Move and Jump are not keys; they are things the player wants to do. An **input action** is a named control of the game, such as Move or Jump, whose value Strata computes from the devices bound to it. A script asks for `Gameplay/Move` and never learns which device answered.

Actions live in groups. A **map** is a named group of input actions that the game enables and disables together: walking, driving, a menu. The project keeps its maps in Project Settings, under **Input Actions**. Each action lists its bindings, the controls that drive it, such as the key W or the left stick. A player's own bindings, when the game saved some, replace the project's for that action.

```mermaid caption="From devices to an action value: bindings read the devices, the strongest one wins, the dead zone cleans the result, and scripts read the value. A player's saved bindings replace the project's." alt="A flow from devices to bindings, then the strongest binding, the dead zone and the action value that scripts read. Two boxes, the project's bindings and the player's bindings, both feed the bindings step."
flowchart LR
  D["Keys, mouse buttons, gamepads"] --> B["Bindings of the action"]
  P["The project's bindings"] --> B
  Q["The player's bindings, if saved"] --> B
  B --> S["The strongest binding"]
  S --> Z["Dead zone"]
  Z --> V["Action value for scripts"]
```

Two mistakes follow from skipping this idea. A game that reads fixed keys cannot offer other controls, and a game that ignores the dead zone of a stick drifts, because a stick at rest never reads exactly zero. Mouse motion is no action source in Strata: look around with `Input::GetMouseDelta`, as the optional section below does.

:::why
Strata keeps the actions in the project, not in code. The editor, the commands and the player's own file can then change a binding while the game runs, with no build. The cost is that a binding is only a control or a composite of controls: there are no chords or filters, and scripts do the rest ([what Strata does not do](#what-strata-does-not-do-here)).
:::

## What you need

- The end state of [Scripts and the scene](scripting-scene.md): Coin Run with its coins placed by `CoinPlacer` and collected by the distance test. The ball is the sphere named `Ball` at (0, 0.5, 6), and it has no rigid body yet. The script writes its position. Continue your own project, or download the project at the end of that page: the box under its [Result](scripting-scene.md#result) offers it.
- A code editor for C++ files, set as in [Your first script](first-script.md).
- Nothing to import. A gamepad is welcome but optional: every step that needs one has a command that plays the part of the pad.
- About 90 minutes. The two optional sections near the end take 20 of them.

The **With a command** tabs send editor commands. A command script names a result once with `bind`. A **`$ref`** is a value such as `{ "$ref": "ball" }` that uses a named result again in a later command: here it stands for the entity found earlier.

## Move the ball with the keyboard

Start with the direct way, so that you see what the actions will replace. The script `BallControl` adds a direction to the ball's position every frame. The direction comes from the keys: W, A, S and D. The step is the direction, times the speed, times `deltaTime`, the seconds the frame lasted.

Here are the numbers. The ball's `Speed` is 4 m per second. At 60 frames per second a frame lasts 0.0167 seconds, so holding W moves the ball 4 × 0.0167 = 0.067 m per frame, and 4 m in a second. At 30 frames per second the step is twice as long and there are half as many of them, so the speed stays the same.

The direction needs care. On Coin Run's level, forward is away from the camera, which is the -Z direction ([Transforms and units](transforms-units.md)). So W subtracts from `z`, S adds, A subtracts from `x` and D adds.

Now hold W and D together: the direction is (1, 0, -1), which is 1.41 long. At 4 m per second that is a ball that moves 5.7 m per second on the diagonal: faster than straight ahead. The script cuts a direction longer than 1 back to 1.

:::question
The class below is derived from `Script` and its function says `override`. What does that mean? See [classes and inheritance](../basics/cpp-classes.md).

:::answer
`Script` is the class every script builds on, and `override` says that `OnUpdate` replaces the function of that class, so that the engine calls yours each frame.
:::
:::

The code below is the first half of `OnUpdate`. Read the four `if` lines, then the cut to length 1, then the write to the position.

```cpp src="book:tutorials/make/input/BallControl-1.cpp#L5-L27"
// Moves its entity over the ground with W, A, S and D.
class BallControl : public Script
{
public:
	float Speed = 4.0f; // Metres per second

	void OnUpdate(float deltaTime) override
	{
		glm::vec3 direction(0.0f);
		if (Input::IsKeyDown(Key::W))
			direction.z -= 1.0f; // Forward is -Z
		if (Input::IsKeyDown(Key::S))
			direction.z += 1.0f;
		if (Input::IsKeyDown(Key::A))
			direction.x -= 1.0f;
		if (Input::IsKeyDown(Key::D))
			direction.x += 1.0f;

		if (glm::length(direction) > 1.0f)
			direction = glm::normalize(direction);

		TransformComponent transform = GetTransform();
		transform.SetTranslation(transform.GetTranslation() + direction * Speed * deltaTime);
```

1. **Lines 14–21:** each `Input::IsKeyDown` is `true` for as long as the key is held, so the direction changes by the frame.
2. **Lines 23–24:** `glm::length` is the length of the vector. A diagonal longer than 1 is turned back to length 1 with `glm::normalize`.
3. **Lines 26–27:** the script reads the position, adds the step and writes it back. The `Speed` field shows in the Inspector, so you can tune it per entity.

A key has three states for a frame: it went down, it is down, it came up. `IsKeyPressed` is `true` only in the frame where the key went down, and `IsKeyReleased` only in the frame where it came up. `IsKeyDown` is `true` in every frame between. Read the three in `OnUpdate`, once per frame, as every frame-by-frame check goes there ([The script loop](script-loop.md)). The second half of the function logs the first two for Space.

```cpp src="book:tutorials/make/input/BallControl-1.cpp#L29-L33"
	if (Input::IsKeyPressed(Key::Space))
		Log::Info("Space went down");
	if (Input::IsKeyReleased(Key::Space))
		Log::Info("Space came up");
}
```

A held Space gives one line `Space went down`, silence while it is held, and one line `Space came up` when you let go.

:::caution
Keys reach the game only while the Game view has the focus and the game plays. When you click the Inspector, the Hierarchy or any other panel, the game stops seeing keys, and the ball stops. Click into the Game view to give the keys back. A script cannot tell this from "no key pressed", so a ball that does not move is often a focus problem, not a code problem.
:::

:::::steps

1. Create the :term[script class]{id=script-class}.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ New Script...**, type the class name `BallControl`, and create it.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "BallControl", "fields": { "Speed": "float" } } }
   ```

   :::
   ::::

   **You should see:** a new file `Scripts/BallControl.cpp` in the project's folder. The Content Browser lists it under its **Scripts** root.

   **If you do not see it:** the name is taken by another script, or the project has no script build. Choose another name, or look in the :term[Problems panel]{id=problems-panel}.

2. Replace the whole file with the code of this stage. Copy it from the checkpoint download, or type the two parts above and the end of the class into your code editor.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open `Scripts/BallControl.cpp` in your code editor, and save the file after you wrote it.
   :::
   :::tab[With a command]
   No command writes a file. The stage's download holds `Scripts/BallControl.cpp` already written.
   :::
   ::::

   **You should see:** a file whose class `BallControl` has the field `Speed` and the function `OnUpdate`.

   **If you do not see it:** the editor did not save the file. Save it, then build in the next step.

3. Build the scripts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ Build Scripts** (**Ctrl+B**).
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** "Building" leave the status bar.

   **If you do not see it:** the status bar says "Build failed". Click it and read the first error in the Problems panel.

4. Attach the script to the ball.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Ball` in the Hierarchy. In the Inspector choose **Add Component ▸ Script**, and pick `BallControl`.
   :::
   :::tab[With a command]

   ```json
   [
     { "command": "entity.find", "parameters": { "name": "Ball" }, "bind": { "ball": "/entities/0" } },
     { "command": "script.add", "parameters": { "entity": { "$ref": "ball" }, "class": "BallControl", "fields": { "Speed": 4 } } }
   ]
   ```

   :::
   ::::

   **You should see:** a Script component on `Ball` with the class `BallControl` and `Speed` at 4.

   **If you do not see it:** `BallControl` is missing from the list. The build of step 3 failed or did not run: build again.

5. Play and move the ball.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play** (**Ctrl+P**). Click into the Game view, then hold W, A, S and D. Press and release Space, and look in the Console panel. Press **Stop** (**Ctrl+P**) when you are done.
   :::
   :::tab[With a command]

   ```json
   [
     { "command": "play.start" },
     { "command": "input.key", "parameters": { "key": "W", "steps": 60 } },
     { "command": "component.get", "parameters": { "entity": { "$ref": "ball" }, "component": "Transform" } },
     { "command": "input.key", "parameters": { "key": "Space" } },
     { "command": "log.read", "parameters": { "newest": true, "limit": 50 } },
     { "command": "play.stop" }
   ]
   ```

   Read the ball while the game still plays. `play.stop` throws away the playing copy of the scene, so a `component.get` after it reads the ball where it stood before **Play**, at z = 6.
   :::
   ::::

   **You should see:** the ball roll away from the camera while W is held, about 4 m in the second the key is down: the `Translation` reads about (0, 0.5, 2). The Console holds the two Space lines.

   **If you do not see it:** the game does not have the keys. Click into the Game view, or press **Play** again. A ball back at z = 6 was read after **Stop**.

:::::

::checkpoint{stage=1}

::figure{id=ball-moves}

## Read a gamepad

Strata numbers the gamepads 0 to 3 in the order they connect, and `IsGamepadConnected()` asks about gamepad 0 unless you pass another number. The buttons follow the `Xbox` layout, so on another pad the button in the same place has the same name.

A stick reports two numbers, x from -1 (left) to 1 (right) and y from -1 (down) to 1 (up). A stick at rest reports a small movement, noise of the springs, which makes the ball creep. A **dead zone** is a small range of stick values that Strata reads as no movement, so that a stick at rest means zero.

The shape of the zone matters. Take the default size, 0.15. The simplest zone is a square: each axis alone is zero when its own value is under 0.15, and the rest is stretched so that 1 still reads 1. A stick pushed to (0.14, 0.90) loses its x: the ball goes straight forward, though the player leaned to the side.

A round zone looks at the length of the whole tilt. It keeps the direction, and it reads zero only when the length is under 0.15.

:::question
The sketch uses functions, `glm::vec2` and `std::printf`. How do you read a :term[function call]{id=function-call} such as `glm::length(value)`? See [classes and calls](../basics/programming-3.md) and [functions](../basics/programming-2.md).

:::answer
The call runs the function `length` of the :term[namespace]{id=namespace} `glm` with `value` and gives back the length of the vector.
:::
:::

The sketch below runs both zones on four sticks. Read the two functions first: the first treats one axis, the second treats the vector. Then look at what each prints.

```cpp sketch="make-input-deadzone.cpp"
#include <cstdio>
#include <glm/glm.hpp>

// A square zone: each axis alone, stretched so that 1 stays 1.
static float Axis(float value, float zone)
{
	const float size = glm::abs(value);
	return size <= zone ? 0.0f : glm::sign(value) * (size - zone) / (1.0f - zone);
}

// A round zone: the length of the whole tilt, so the direction stays.
static glm::vec2 Stick(glm::vec2 value, float zone)
{
	const float length = glm::length(value);
	return length <= zone ? glm::vec2(0.0f) : value / length * (length - zone) / (1.0f - zone);
}
int main()
{
	const glm::vec2 samples[] = { { 0.10f, 0.10f }, { 0.14f, 0.90f }, { 0.60f, 0.00f }, { 0.60f, 0.80f } };
	for (const glm::vec2& s : samples)
	{
		const glm::vec2 r = Stick(s, 0.15f);
		std::printf("stick (%.2f, %.2f): square (%.2f, %.2f), round (%.2f, %.2f)\n", s.x, s.y, Axis(s.x, 0.15f), Axis(s.y, 0.15f), r.x, r.y);
	}
}
```

```text output-of="make-input-deadzone.cpp"
stick (0.10, 0.10): square (0.00, 0.00), round (0.00, 0.00)
stick (0.14, 0.90): square (0.00, 0.88), round (0.14, 0.88)
stick (0.60, 0.00): square (0.53, 0.00), round (0.53, 0.00)
stick (0.60, 0.80): square (0.53, 0.76), round (0.60, 0.80)
```

1. **Lines 4–9:** the square zone, one axis at a time. A value at or under the dead zone reads 0, and `(size - zone) / (1.0f - zone)` stretches what is left so that 1 stays 1.
2. **Lines 11–16:** the round zone divides the vector by its length to get the direction, and scales it by the stretched length. The direction is kept.
3. **Lines 19–23:** four sticks. The first, (0.10, 0.10), is under the zone in both ways. The second, (0.14, 0.90), shows the difference: the square result has no x, and the round result keeps it.

::figure{id=dead-zones}

Strata gives you both zones. `Input::GetGamepadStick(GamepadStick::Left)` has the round zone and returns a vector of length 1 at most: the call that movement wants.

`Input::GetGamepadAxis(GamepadAxis::LeftTrigger)` reads one axis or one trigger, with the dead zone applied to that axis alone. Triggers go from 0 to 1, not from -1 to 1. Both calls take a gamepad number and a dead zone as extra arguments, and a dead zone of 0 reads the device as it is.

Add the stick to `BallControl`. The `+=` lines add the stick to what the keys gave, and the length cut keeps the sum within 1. The stick's +Y is up, while forward on the level is -Z, so `z` subtracts the stick's y.

```cpp src="book:tutorials/make/input/BallControl-2.cpp#L23-L34"
if (Input::IsGamepadConnected())
{
	const glm::vec2 stick = Input::GetGamepadStick(GamepadStick::Left);
	direction.x += stick.x;
	direction.z -= stick.y; // The stick's +Y is up, the level's forward is -Z
}

if (glm::length(direction) > 1.0f)
	direction = glm::normalize(direction);

TransformComponent transform = GetTransform();
transform.SetTranslation(transform.GetTranslation() + direction * Speed * deltaTime);
```

1. **Line 23:** `IsGamepadConnected` is `false` when no pad is connected, so the code is safe without one. A pad missing from the gamepad database of GLFW, the library Strata reads the devices with, reads as not connected.
2. **Lines 25–27:** the stick vector joins the direction. `z` takes the minus of the stick's y.

:::::steps

1. Replace the file with the code of this stage, and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Paste the stage's `BallControl.cpp` into your file and choose **Scripts ▸ Build Scripts** (**Ctrl+B**). You can do this while the game plays: the module reloads in place.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the build finish. The fields of the script keep their values after the reload.

   **If you do not see it:** the build failed and the old module keeps running. Read the Problems panel.

2. Push the left stick.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, and push the left stick of a connected gamepad up and a little to the right. Press **Stop** when you are done.
   :::
   :::tab[With a command]

   ```json
   [
     { "command": "play.start" },
     { "command": "input.gamepadAxis", "parameters": { "axis": "LeftY", "value": 0.6, "steps": 60, "wait": false } },
     { "command": "input.gamepadAxis", "parameters": { "axis": "LeftX", "value": 0.3, "steps": 60 } },
     { "command": "play.stop" }
   ]
   ```

   :::
   ::::

   The first command has `"wait": false`, so the second starts at once and both axes are held together.

   **You should see:** the ball move away from the camera and to the right, slower than with W: the length of (0.3, 0.6) is 0.67, which the dead zone stretches to 0.61.

   **If you do not see it:** no gamepad is connected, or the game has no keys. Click into the Game view.

:::::

::checkpoint{stage=2}

::figure{id=ball-pad}

## Make the Move action

Every new control would add lines to `BallControl`. The action turns this around: the code reads one value, and the project says which controls make it.

Open the project's actions. Choose **File ▸ Project Settings...** and select **Input Actions** under **Input**. You add the map **Gameplay**, and in it the action **Move** with the kind **Vector2**: a pair of numbers, x to the right and y up, whose length is at most 1.

The drawing below shows the page at the end of this section.

::figure{id=input-actions-drawing}

A Vector2 action needs bindings that make two numbers. A **composite** is a binding that builds one value from several controls: a `2D:` composite takes four keys, in the order up, down, left, right, and gives a vector. The stick needs no composite, because it is a vector already. You give Move three bindings: W, A, S and D as a composite, the four arrows as another, and the left stick.

Every binding has a text form, which the editor writes and the commands take:

| Text | Meaning |
| --- | --- |
| `Key/Space` | The Space key. Mouse buttons are `Mouse/Left`, `Mouse/Right` and `Mouse/Middle`. |
| `Gamepad/A` | The A button, on any connected pad. |
| `Gamepad/LeftStick` | Both axes of the left stick. `Gamepad/RightStick` is the right one. |
| `Gamepad/LeftX+` | The positive half of one axis, such as the stick pushed right. A button action takes it. |
| `1D:Key/Left,Key/Right` | An Axis value from two keys: the negative one, then the positive one. |
| `2D:Key/W,Key/S,Key/A,Key/D` | A vector from four keys: up, down, left, right. |

A gamepad binding reads every connected pad, so a second player on pad 1 also drives the action. When several bindings are active, a Button is down when any binding is down. A Vector2 takes the binding with the longest vector.

A 2D composite is cut to length 1, so W and D together give (0.71, 0.71), a vector of length 1, not 1.41. The dead zone of the action, 0.15 unless you change it, then applies to the whole vector, round, as in the last section.

:::::steps

1. Add the map `Gameplay`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In **Input Actions**, press **Add Map**. Name the new map `Gameplay`.
   :::
   :::tab[With a command]

   ```json
   { "command": "inputActions.setMap", "parameters": { "map": "Gameplay" } }
   ```

   :::
   ::::

   **You should see:** a map `Gameplay` in the list, with **Enabled at start** on.

   **If you do not see it:** the name is taken, or it uses a character that names cannot hold. Names have 1 to 64 letters, digits, spaces, `_`, `-` and `.`.

2. Add the action `Move`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   With `Gameplay` selected, press **Add Action**. Name it `Move` and set its **Kind** to `Vector2`.
   :::
   :::tab[With a command]

   ```json
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Move", "kind": "Vector2" } }
   ```

   :::
   ::::

   **You should see:** the action `Move` with the kind Vector2 and a **Dead zone** of 0.15.

   **If you do not see it:** the kind stayed Button. Change **Kind** in the action's row.

3. Bind W, A, S and D as a 2D composite.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+** beside **Bindings**. Set **Shape** to **2D**. For each of **Up**, **Down**, **Left** and **Right**, press the button beside it and then press the key W, S, A or D. Press **Add**.
   :::
   :::tab[With a command]

   ```json
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Move", "bindings": [ "2D:Key/W,Key/S,Key/A,Key/D" ] } }
   ```

   :::
   ::::

   **You should see:** one chip on Move that reads `2D:Key/W,Key/S,Key/A,Key/D`.

   **If you do not see it:** a press did not land on the part you chose. The page listens for ten seconds and then stops. Press the button of the part again.

4. Bind the arrows and the left stick.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add a second 2D composite in the same way, with the arrow keys. Press **+** once more, choose the shape **Control**, and pick **Gamepad/LeftStick** from the list.
   :::
   :::tab[With a command]

   ```json
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Move", "bindings": [
     "2D:Key/W,Key/S,Key/A,Key/D", "2D:Key/Up,Key/Down,Key/Left,Key/Right", "Gamepad/LeftStick" ] } }
   ```

   :::
   ::::

   **You should see:** three chips on Move.

   **If you do not see it:** a Vector2 takes sticks and 2D composites only. A single key is refused: use the composite.

5. Read the action in the script.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace the file with the code of this stage and build (**Ctrl+B**). The keyboard and gamepad code of the last two sections is gone.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the build finish.

   **If you do not see it:** the Problems panel lists the error.

:::::

The new script is shorter. Read the name `Gameplay/Move`: the map, a slash, the action. A bare name such as `Move` works only when no other map has an action with that name, and an unknown or doubtful name reads as up and logs a warning.

```cpp src="book:tutorials/make/input/BallControl-3.cpp#L11-L19"
void OnUpdate(float deltaTime) override
{
	// Up on the action (+Y) is forward on the level (-Z).
	const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
	const glm::vec3 direction(move.x, 0.0f, -move.y);

	TransformComponent transform = GetTransform();
	transform.SetTranslation(transform.GetTranslation() + direction * Speed * deltaTime);
}
```

1. **Line 14:** `GetActionValue` gives the vector of the action, with the dead zone applied. Its length is at most 1.
2. **Line 15:** the action's +Y is up, and the level's forward is -Z, so `y` goes in with a minus sign. Writing `move.y` without it sends the ball toward the camera when you press W.

:::::steps

1. Play and test all three controls.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, click into the Game view, and move the ball with W, A, S and D, with the arrows and, if you have a gamepad, with the left stick. Press **Stop** when you are done.
   :::
   :::tab[With a command]

   ```json
   [
     { "command": "play.start" },
     { "command": "input.action", "parameters": { "action": "Gameplay/Move", "value": [0.0, 1.0], "steps": 60 } },
     { "command": "play.stop" }
   ]
   ```

   :::
   ::::

   **You should see:** the ball move the same way with all three.

   **If you do not see it:** the ball does not move at all. The name in the script does not match: `Gameplay/Move` must match the map and the action exactly, and the Console shows a warning for an unknown name.

:::::

::checkpoint{stage=3}

::figure{id=ball-action}

## Add Jump and Boost

A Button action is down or up. Strata gives a script three questions about it, as for a key: `IsActionPressed` (it went down this frame), `IsActionDown` (it is down) and `IsActionReleased` (it came up). You add two. **Jump** is read once per press, so a held key does not jump again and again: it only logs a line here, and [Physics and rigid bodies](physics.md) makes the ball jump. **Boost** is read while held: the ball goes faster as long as you hold it.

A Button can also be bound to half an axis, such as `Gamepad/RightTrigger+`. That binding counts as down from 0.5 and as up again below 0.35. A trigger pulled half way counts as pressed, and a small shake near the edge does not flicker.

:::::steps

1. Add the actions `Jump` and `Boost`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Add Action** twice. Name them `Jump` and `Boost`, kind `Button`. For Jump, press **+** and the button beside it, then press Space; repeat with the A button of a gamepad. For Boost, bind the left Shift key.
   :::
   :::tab[With a command]

   ```json
   [
     { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Jump", "kind": "Button", "bindings": [ "Key/Space", "Gamepad/A" ] } },
     { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Boost", "kind": "Button", "bindings": [ "Key/LeftShift" ] } }
   ]
   ```

   :::
   ::::

   **You should see:** two actions of kind Button in `Gameplay`.

   **If you do not see it:** the key did not bind. While the page listens, it takes the keys from the editor for ten seconds: press the key you want in that time.

:::::

Now use them. The new script reads Jump by its press and Boost while held. The `BoostFactor` field is new: it is a number the Inspector shows. The listing is the whole file but its end, which closes the class with `};` and registers both fields: `ST_SCRIPT_CLASS(BallControl)` with `ST_SCRIPT_FIELD(Speed);` and `ST_SCRIPT_FIELD(BoostFactor);`.

```cpp src="book:tutorials/make/input/BallControl-4.cpp#L1-L25"
#include "StrataScript/StrataScript.h"

using namespace Strata;

// Moves its entity with the Move action, faster while Boost is held.
class BallControl : public Script
{
public:
	float Speed = 4.0f;       // Metres per second
	float BoostFactor = 2.0f; // Speed is multiplied by it while Boost is held

	void OnUpdate(float deltaTime) override
	{
		if (Input::IsActionPressed("Gameplay/Jump"))
			Log::Info("Jump pressed");

		const float speed = Input::IsActionDown("Gameplay/Boost") ? Speed * BoostFactor : Speed;

		// Up on the action (+Y) is forward on the level (-Z).
		const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
		const glm::vec3 direction(move.x, 0.0f, -move.y);

		TransformComponent transform = GetTransform();
		transform.SetTranslation(transform.GetTranslation() + direction * speed * deltaTime);
	}
```

1. **Line 10:** the new field, 2 by default, so Boost doubles the speed.
2. **Lines 14–15:** `IsActionPressed` is `true` for one frame per press, so the line `Jump pressed` appears once for each tap of Space.
3. **Line 17:** `IsActionDown` is `true` as long as Boost is held, so the speed is doubled for the time you hold Shift.

Hold and toggle are two ways to use one Button. A **hold** acts while the control is down and stops the instant it is not. A **toggle** switches a state with each press and keeps it until the next press. A toggle is a hold's press edge turned into a stored flag.

```cpp src="book:tutorials/make/input/BallControl-toggle.cpp#L12-L27"
	void OnUpdate(float deltaTime) override
	{
		if (Input::IsActionPressed("Gameplay/Boost"))
			m_BoostLatched = !m_BoostLatched;

		const float speed = m_BoostLatched ? Speed * BoostFactor : Speed;
		const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
		const glm::vec3 direction(move.x, 0.0f, -move.y);

		TransformComponent transform = GetTransform();
		transform.SetTranslation(transform.GetTranslation() + direction * speed * deltaTime);
	}

private:
	bool m_BoostLatched = false;
};
```

1. **Lines 14–15:** each press of Boost flips `m_BoostLatched`, a private member, so one press keeps the boost on and the next ends it.
2. **Line 17:** the speed reads the flag in place of the held state.

A sprint wants a hold, since letting go is the natural way to stop, and a long drive wants a toggle. A good game offers both. Try the toggle, then return the hold: the checkpoint keeps the hold.

:::::steps

1. Replace the file with the code of this stage, the hold, and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Paste the stage's `BallControl.cpp` into your file, save, and choose **Scripts ▸ Build Scripts** (**Ctrl+B**).
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the build finish, and `BoostFactor` at 2 under `BallControl` in the Inspector.

   **If you do not see it:** the Problems panel lists the error.

2. Play, and hold Boost and a direction together.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play** and click into the Game view. Hold W for a second, then hold Left Shift and W together for a second. Tap Space, and press **Stop**.
   :::
   :::tab[With a command]
   A tap of `input.key` lets go of its key at its end, so Boost is held with `"action": "press"` and let go with `"action": "release"`. The W tap runs while Shift is down.

   ```json
   [
     { "command": "play.start" },
     { "command": "input.key", "parameters": { "key": "LeftShift", "action": "press" } },
     { "command": "input.key", "parameters": { "key": "W", "steps": 60 } },
     { "command": "input.key", "parameters": { "key": "LeftShift", "action": "release" } },
     { "command": "component.get", "parameters": { "entity": { "$ref": "ball" }, "component": "Transform" } },
     { "command": "input.key", "parameters": { "key": "Space" } },
     { "command": "play.stop" }
   ]
   ```

   :::
   ::::

   **You should see:** the ball move about 8 m in the second that Shift and W are held together, twice the walk: from z = 6 to about z = -2. The Console holds one line `Jump pressed`.

   **If you do not see it:** the ball moves only 4 m: press Shift first and keep it down.

:::::

:::tip
You can edit the actions while the game plays. The change applies at once, and the actions you did not touch keep their state, so a held key does not "press" again. Open **Input Actions** in the middle of a run and add Left Ctrl to Boost: the next frame obeys it.
:::

::checkpoint{stage=4}

::figure{id=ball-boost}

## Look around (optional)

This section adds a camera that turns. It is optional: the checkpoint keeps only its action, not the camera script, so this page gives the whole script in three parts.

Add an action **Look**, a Vector2 bound to `Gamepad/RightStick`. Then read the mouse beside it. Mouse motion is not an action source: Strata binds only keys, mouse buttons and gamepad controls to actions. So a script reads `Input::GetMouseDelta()`, the pixels the mouse moved in this frame, while the right button is held. The script also locks the cursor with `SetCursorMode(CursorMode::Locked)`: the cursor is hidden and kept in the window, and `GetMouseDelta` continues to report movement.

The first part is the start of the file: two fields and an `OnCreate` that reads the camera's angles once.

```cpp src="book:tutorials/make/input/LookCamera.cpp#L1-L17"
#include "StrataScript/StrataScript.h"

using namespace Strata;

// Turns its entity with the mouse while the right button is held, and with the Look action.
class LookCamera : public Script
{
public:
	float DegreesPerPixel = 0.1f;
	float StickDegreesPerSecond = 120.0f;

	void OnCreate() override
	{
		const glm::vec3 angles = GetTransform().GetEulerAngles();
		m_Pitch = angles.x;
		m_Yaw = angles.y;
	}
```

1. **Lines 9–10:** the turn for one pixel of mouse motion, and for a full tilt of the stick in one second, both in degrees.
2. **Lines 12–17:** the camera starts from the angles it has in the scene, so it does not jump at the first frame.

The second part is the update. Look at where the mouse turns the camera and where the stick does.

```cpp src="book:tutorials/make/input/LookCamera.cpp#L19-L37"
void OnUpdate(float deltaTime) override
{
	const bool looking = Input::IsMouseButtonDown(Mouse::ButtonRight);
	Input::SetCursorMode(looking ? CursorMode::Locked : CursorMode::Normal);

	if (looking)
	{
		const glm::vec2 delta = Input::GetMouseDelta();
		m_Yaw -= glm::radians(delta.x * DegreesPerPixel);   // Mouse right turns right
		m_Pitch -= glm::radians(delta.y * DegreesPerPixel); // Mouse down looks down
	}

	const glm::vec2 look = Input::GetActionValue("Gameplay/Look");
	m_Yaw -= glm::radians(look.x * StickDegreesPerSecond * deltaTime);
	m_Pitch += glm::radians(look.y * StickDegreesPerSecond * deltaTime);
	m_Pitch = glm::clamp(m_Pitch, glm::radians(-89.0f), glm::radians(89.0f));

	GetTransform().SetEulerAngles(glm::vec3(m_Pitch, m_Yaw, 0.0f));
}
```

1. **Lines 21–22:** the cursor locks while the right button is held, and returns to normal when it is released.
2. **Lines 24–29:** the mouse delta turns the camera. A mouse moved to the right turns the camera to the right, which is a smaller yaw angle; a mouse moved down looks down.
3. **Lines 31–34:** the Look action turns the camera with the right stick, and the pitch stays under 89 degrees so the camera never flips over.
4. **Line 36:** the script writes both angles to the camera's rotation.

The third part closes the class.

```cpp src="book:tutorials/make/input/LookCamera.cpp#L39-L48"
private:
	float m_Pitch = 0.0f;
	float m_Yaw = 0.0f;
};

ST_SCRIPT_CLASS(LookCamera)
{
	ST_SCRIPT_FIELD(DegreesPerPixel);
	ST_SCRIPT_FIELD(StickDegreesPerSecond);
}
```

1. **Lines 39–41:** the members hold the angles in radians, since `glm::radians` converted every turn.
2. **Lines 44–48:** only the two fields are registered; the members stay out of the Inspector.

The editor gives the cursor back when the Game view loses the focus, and **Shift+F1** frees it at once while the game keeps running. Click the Game view to take it again. The game's cursor mode applies only while the game has the input, so a locked cursor never traps you in the editor.

:::::steps

1. Add the action `Look`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Add Action**, name it `Look`, set **Kind** to `Vector2`, press **+**, and choose **Gamepad/RightStick** from the list.
   :::
   :::tab[With a command]

   ```json
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Look", "kind": "Vector2", "bindings": [ "Gamepad/RightStick" ] } }
   ```

   :::
   ::::

   **You should see:** the action `Look` with one chip.

   **If you do not see it:** the kind is Button. A Button cannot take a stick: set the kind first.

2. Optional: create the script `LookCamera`, replace its text with the three parts above, build, and attach it to the `Main Camera`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ New Script...** and name the class `LookCamera`. Replace the new file's text with the three parts, save, build, and attach the class with **Add Component ▸ Script** on `Main Camera`. Press **Play**, hold the right mouse button in the Game view and move the mouse.
   :::
   :::tab[With a command]
   No command writes the file: create it with `script.create` and the class `LookCamera`, and replace its text in your code editor. Then build, attach and play. The right stick of a gamepad plays the part of the mouse here.

   ```json
   [
     { "command": "script.build" },
     { "command": "entity.find", "parameters": { "name": "Main Camera" }, "bind": { "camera": "/entities/0" } },
     { "command": "script.add", "parameters": { "entity": { "$ref": "camera" }, "class": "LookCamera" } },
     { "command": "play.start" },
     { "command": "input.gamepadAxis", "parameters": { "axis": "RightX", "value": 1.0, "steps": 30 } },
     { "command": "entity.get", "parameters": { "entity": { "$ref": "camera" }, "world": true } },
     { "command": "play.stop" }
   ]
   ```

   :::
   ::::

   **You should see:** the camera turn while you hold the right mouse button and move the mouse. With the command, half a second of the stick turns the camera 60 degrees right: `world.rotation.euler` goes from about (-55, 0, 0) to (-55, -60, 0).

   **If you do not see it:** the cursor does not lock. The Game view has no focus: click it.

:::::

::checkpoint{stage=5}

::figure{id=ball-look}

## Switch maps (optional)

A project has several maps because a game has several modes. While you walk, the controls of a car must do nothing, and while you drive, the controls of walking must do nothing. A menu over the game is a third mode. A map turns a whole mode on or off with one call.

Add a map **Vehicle** with the action **Drive**, a Vector2 with the same W, A, S and D composite. The script switches the maps with `Input::SetActionMapEnabled`, and reads the state with `Input::IsActionMapEnabled`, which says nothing for a map the project does not have. The change applies from the next input frame. An action held at that moment reports `IsActionReleased` once, as a key you let go, and then reads as up.

This version replaces all of `BallControl.cpp` for this section. Lines 1 to 3 are the include and `using namespace Strata;`, and the end closes the class and registers `Speed` alone.

```cpp src="book:tutorials/make/input/BallControl-vehicle.cpp#L5-L28"
// V switches between walking (the Gameplay map) and driving (the Vehicle map, twice as fast).
class BallControl : public Script
{
public:
	float Speed = 4.0f;

	void OnUpdate(float deltaTime) override
	{
		if (Input::IsKeyPressed(Key::V)) // A test switch, not a control for players
		{
			const bool driving = Input::IsActionMapEnabled("Vehicle").value_or(false);
			Input::SetActionMapEnabled("Vehicle", !driving);
			Input::SetActionMapEnabled("Gameplay", driving);
		}

		// The disabled map reads as up: only one of the two vectors is not zero.
		const glm::vec2 walk = Input::GetActionValue("Gameplay/Move");
		const glm::vec2 drive = Input::GetActionValue("Vehicle/Drive");
		const glm::vec2 move = walk + drive * 2.0f;
		const glm::vec3 direction(move.x, 0.0f, -move.y);

		TransformComponent transform = GetTransform();
		transform.SetTranslation(transform.GetTranslation() + direction * Speed * deltaTime);
	}
```

1. **Line 9:** only `Speed` is left: this version has no Boost and no Jump.
2. **Lines 13–18:** the V key flips the maps. V is a test switch for this tutorial, not a control for players.
3. **Lines 20–23:** the disabled map reads as up, so only one of the two vectors is not zero. The vehicle runs at twice the speed.

:::::steps

1. Add the map `Vehicle` with **Enabled at start** off, and its action `Drive`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In **Input Actions**, press **Add Map**, name it `Vehicle` and clear **Enabled at start**. Add the action `Drive` of kind `Vector2` and bind W, S, A and D to it as a 2D composite, as for Move.
   :::
   :::tab[With a command]

   ```json
   [
     { "command": "inputActions.setMap", "parameters": { "map": "Vehicle", "enabled": false } },
     { "command": "inputActions.setAction", "parameters": { "action": "Vehicle/Drive", "kind": "Vector2", "bindings": [ "2D:Key/W,Key/S,Key/A,Key/D" ] } }
   ]
   ```

   :::
   ::::

   **You should see:** the map `Vehicle` with **Enabled at start** off, and one chip on `Drive`.

   **If you do not see it:** **Add Action** added `Drive` to `Gameplay`. Select `Vehicle` first, or name the action `Vehicle/Drive`.

2. Replace the text of `Scripts/BallControl.cpp` with this version, build, and play.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Build with **Ctrl+B** and press **Play**. Hold W for a second, press V, and hold W again.
   :::
   :::tab[With a command]

   ```json
   [
     { "command": "script.build" },
     { "command": "play.start" },
     { "command": "input.key", "parameters": { "key": "V" } },
     { "command": "input.key", "parameters": { "key": "W", "steps": 60 } },
     { "command": "component.get", "parameters": { "entity": { "$ref": "ball" }, "component": "Transform" } },
     { "command": "play.stop" }
   ]
   ```

   :::
   ::::

   **You should see:** 4 m in a second of W before V, and 8 m in a second after it: with the command, the ball goes from z = 6 to about z = -2.

   **If you do not see it:** the ball runs at three times the speed before V: `Vehicle` is enabled at start, so its vector adds to Move's. Clear the box.

:::::

Maps start as the project says, in every session: a map you enabled in a script is back at its project value the next time you play. For one pad per player, read the pads by number: `Input::IsGamepadButtonDown(GamepadButton::A, 1)` asks pad 1. The map `UI` is reserved for the game's menus, which [Menus and rebinding](menus.md) builds.

The checkpoint leaves this map out: it is a playground. Its `BallControl.cpp` is the Boost version of Checkpoint 4, so put that version back when you are done; the map `Vehicle` may stay, since nothing else reads it.

### What Strata does not do here

Each of these is an absence at this version, not a promise.

- **Touch input.** There is no touch screen input in the input module or in the window code.
- **Modifiers, chords, processors and interactions.** An action takes a binding of a key, a mouse button, a gamepad control or a composite, nothing more. A chord such as Ctrl and S is two keys read in code. Mouse motion and the scroll wheel are not action sources: they stay on `GetMouseDelta` and `GetScrollDelta`.
- **Force feedback.** Rumble and vibration are not among the script calls.
- **Devices assigned to players.** Gamepad bindings read every pad, and all players share one set of actions. A game that wants one pad per player reads the pads by number.
- **Unknown controllers.** A controller missing from GLFW's gamepad database reads as not connected and keeps its slot. Strata reads at most four gamepads and adds no mappings of its own.

### Reading devices or reading actions

:::rule
Read the player's controls as input actions, never as fixed keys, because players change them. Mouse motion is the exception: it has no action, so you read it from the device.
:::

Read a device when no action can stand for the value: the mouse's motion, the scroll wheel, typed text, and a test key that players never see. When you are unsure, make an action: it costs a line in Project Settings and saves a rewrite.

::checkpoint{stage=6}

::figure{id=ball-vehicle}

## Summary

- A game names its controls as input actions grouped in maps, so players with any device can play and change them.
- Keys, the mouse and gamepads are read with `Input`; sticks read through `GetGamepadStick` have a round dead zone and a length of at most 1.
- Maps, Button and Vector2 actions and their bindings, with 2D composites, are made in **Project Settings ▸ Input Actions** or with `inputActions.*` commands.
- `GetActionValue`, `IsActionPressed` and `IsActionDown` read the actions by the name `Map/Action`.
- Read an action for what players may change, and a device for mouse motion, scrolling and test keys.

## Check yourself

1. Why does Move read the same for a keyboard and for a stick?

   :::answer{tests="why-actions"}
   Because the script reads the action, not the devices. The project binds the keys and the stick to Move, Strata combines the bindings, and the script gets one vector. A new device is a new binding, with no change in the code.
   :::

2. A stick rests at (0.10, 0.10) and you read it with `GetGamepadStick` and the default dead zone. What do you get, and why is the zone round?

   :::answer{tests="read-devices"}
   You get (0, 0): the length 0.14 is under 0.15. The zone is round, so a tilt keeps its direction: a square zone would drop an axis that is small and bend the direction.
   :::

3. You bound W, A, S and D as a 2D composite and press W and D together. What is the length of the vector?

   :::answer{tests="define-actions"}
   The length is 1. A 2D composite is cut to length 1, so the diagonal is (0.71, 0.71) and not (1, 1), whose length is 1.41.
   :::

4. A script calls `Input::IsActionDown("Boost")` and the map `Vehicle` has an action Boost too. What happens?

   :::answer{tests="read-actions"}
   The bare name is doubtful, so the action reads as up and the engine logs a warning. Write `Gameplay/Boost`.
   :::

5. Which of these do you read as an action: the jump, the mouse's motion in a first-person camera, the pause?

   :::answer{tests="choose-direct"}
   The jump and the pause, because a player may want other keys for them. Mouse motion is not an action source, so you read it with `GetMouseDelta`.
   :::

## Exercises

1. **Basic.** Predict what `Input::GetActionValue("Gameplay/Move")` reads while W and D are held together. Then log it to check.

   :::answer{tests="read-actions"}
   The prediction is (0.71, 0.71), a length of 1 and not 1.41. Check it with `Log::Info(move.x, " ", move.y)` in `OnUpdate`, after the line that reads the action.
   :::

2. **Medium.** Add a Button action **Pause**, bound to P and to the gamepad's Start. Its press sets the :term[time scale]{id=time-scale} to 0, and the next press sets it back to 1. Predict what the ball and the coins do while the time scale is 0.

   :::answer[Worked solution]{tests="define-actions read-actions" solution="tutorials/make/input/exercise-2.tutorial.json"}
   Make `Gameplay/Pause` with the bindings `Key/P` and `Gamepad/Start`. In `OnUpdate`, when `IsActionPressed("Gameplay/Pause")` is true, call `Time::SetTimeScale` with 0 or 1, by `Time::GetTimeScale()`. The ball stops, because `deltaTime` is 0. The coins stop bobbing, because the time they bob by is simulation time, and it stands still. The script still runs and still reads the action, so the next press ends the pause.
   :::

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/Input.h`: the `Input` class of the script software development kit (:term[SDK]{id=sdk}), with the key codes and every call of this page.
- `Strata/src/Strata/Input/InputActionSet.h`: maps, actions, kinds, the binding forms and their limits.
- `Strata/src/Strata/Input/InputActions.cpp`: how Strata evaluates the actions each frame.
- `StrataEditor/src/UI/InputActionsPage.cpp`: the **Input Actions** page of Project Settings.
- `StrataEditor/src/Editor/EditorInputActionsCommands.cpp`: the commands `inputActions.setMap` and `inputActions.setAction`.

## Further reading

- Godot's manual, "Input examples" (docs.godotengine.org): how another engine names actions in an Input Map; beginner.
- Unity's Input System manual, "Actions" (docs.unity3d.com): maps, actions and bindings in another engine; intermediate.
