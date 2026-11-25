---
id: input/how-input-works
title: "How input reaches a game: events, polling, edges and intents"
description: "How a key press travels from the operating system to a game, why a game polls state with edges, and why it reads intents instead of keys."
kind: concept
size: M
tracks: [E]
needs: [core/frame-loop, core/windows-events]
time: 50
learn:
  - id: sources
    text: explain how a key press reaches a game as an event, and why a key code names a position and not a letter
  - id: polling-edges
    text: predict what down, pressed and released report in each frame for a held key and for a tap inside one frame
  - id: fixed-update
    text: explain why a game reads pressed in the frame update and not in the fixed update
  - id: text-focus
    text: explain why typed text is not key input, and which capture keeps a text field from moving the player
  - id: intents
    text: compare actions with raw keys and say why a game reads actions
since: 0.3.0
status: final
---

Open the Third-Person sample and play for a minute. Four things must work.

Space makes the robot jump once, however long you hold it. Holding W walks the robot for as long as you hold it. Typing a name into a menu field must not walk the robot. A gamepad must do all of this with other controls.

Each of the four is a different question put to the keyboard. Space asks "did something happen?" W asks "does the player hold it now?" The name field asks "which characters did the person mean?" The gamepad asks all of these about controls that are not keys.

This page shows how a game answers each question, and why Strata gives the game a fifth kind of answer, the intent.

## A tap can be shorter than a frame

The first answer a new programmer writes is "is the key down?", asked once per frame in the game's update. It works for walking: while W is down, move.

Now count. A person who holds Space for 300 ms keeps it down for about 18 frames at 60 :term[frames per second]{id=frame-rate}, because one frame lasts 16.7 ms. Asking "is Space down?" returns true 18 times, so the robot jumps 18 times. You wanted one.

Next, repair it: remember the answer of the last frame, and jump when the key is down now and was not before. That version fixes the held key. It still loses a quick tap.

Suppose a loading hitch makes one frame last 120 ms and a tap lasts 80 ms. The key goes down and up inside the frame. Both frames, before and after, see the key up, and the jump never happens.

So the question "is it down?" is not enough. The game also needs to know what changed while it was not looking.

## Input starts as events from the operating system

A window belongs to the :term[operating system]{id=operating-system}, which also owns the keyboard. When you press a key, the system sends the window a message. The message says what happened, to which key, and when. A message about a change, delivered once, is an **event**.

Strata does not read the keyboard hardware. It asks a library, :term[GLFW]{id=glfw}, to open the window and to call functions of Strata, called :term[callbacks]{id=callback}, when the system sends an event. [Windows, events and layers](../core/windows-events.md) shows the path of an event through the engine. This page follows only the part about keys.

The callback receives a number that names the key. Two kinds of number exist. The keyboard hardware reports a **scancode**, the code of a key's position, which differs from one keyboard model to the next.

The library translates it into a **key code**, Strata's number for a physical key position, named as if the keyboard had a layout of the United States (US).

The code names a position and never a letter. On a French `AZERTY` keyboard, the key labelled A sits where a US keyboard has Q. Pressing it reports `Key::Q`, which is 81, not `Key::A`, which is 65. For a walking game that is what you want: W, A, S and D form the same shape under the left hand on every layout, even where the letters differ.

The system can also send many presses for one physical press. Hold a letter in a text editor, and after a delay the letter repeats. This **key repeat** is a series of events the system invents to help typing. A game that moves a character on every press event would walk in jerks that follow the repeat settings of the player's system.

The next fence shows Strata's callback for keys. Look at what each of the three cases does with the polled state and what it does with the event.

```cpp src="Strata/src/Platform/GLFW/GLFWWindow.cpp#L286-L319"
glfwSetKeyCallback(m_Window, [](GLFWwindow* window, int key, int, int action, int)
{
	if (key < 0)
		return;

	WindowData& data = *static_cast<WindowData*>(glfwGetWindowUserPointer(window));
	const KeyCode keyCode = static_cast<KeyCode>(key);
	switch (action)
	{
		case GLFW_PRESS:
		{
			Input::ProcessKey(keyCode, true);
			KeyPressedEvent event(keyCode, false);
			if (data.EventCallback)
				data.EventCallback(event);
			break;
		}
		case GLFW_RELEASE:
		{
			Input::ProcessKey(keyCode, false);
			KeyReleasedEvent event(keyCode);
			if (data.EventCallback)
				data.EventCallback(event);
			break;
		}
		case GLFW_REPEAT:
		{
			KeyPressedEvent event(keyCode, true);
			if (data.EventCallback)
				data.EventCallback(event);
			break;
		}
	}
});
```

1. **Line 297:** a press changes the polled state, then sends an event.
2. **Line 305:** a release does the same.
3. **Lines 313–315:** a repeat sends an event only; the state stays as it was, so repeat never moves a character.

## Events and polling answer different questions

An event answers "what changed, and in which order?" **Polling** is reading the current state when you need it, instead of reacting to each event. Polling answers "what is true right now?" A walking character needs polling: once per frame, ask whether W is held. A shortcut such as Ctrl+S needs events: react once, in order.

Strata does both, and the two meet in the callbacks. A press or release callback first writes the polled state in `Input`, then sends the matching event into the layer stack. Gamepads differ: the window system sends no events for them, so Strata asks each of the four possible pads for its state once per frame, and the answer goes to the same polled state.

```mermaid caption="Key events change the polled state and also travel to the layers. Gamepads are read once per frame. The frame clears the changes, takes the new input, and only then updates the game." alt="A flow from the operating system through callbacks into two outputs, the polled state and the events for layers, with the frame's start clearing changes before input arrives and the game updating after."
flowchart LR
    OS["Operating system events"] --> CB["Window callbacks"]
    PAD["Gamepads, read each frame"] --> ST
    CB --> ST["Polled state"]
    CB --> EV["Events for layers"]
    CLR["Frame start: clear changes"] --> ST
    ST --> UP["Game update reads the state"]
```

The order inside one frame matters. At its start `Application::RunFrame` calls `Input::BeginFrame`, then asks the window to process its events, so that the callbacks run, and then updates the input actions. Only after that does game code run. Every event since the last frame is in the state before the game reads it.

## Polling needs edges to see taps

Now you can repair the first section's version properly. Keep three answers for every key, not one.

A key is **down** when the player holds it now.

A key is **pressed** when it went down during this frame.

A key is **released** when it went up during this frame.

A change from one state to the other is an **edge**, so pressed and released are the two edges. The state clears both at the start of each frame, and then the frame's events set them again. The code is short.

```cpp src="Strata/src/Strata/Input/Input.cpp#L19-L40"
// Keys or mouse buttons of one source (the devices, or simulated input).
template<size_t Count>
struct ButtonStates
{
	std::bitset<Count> Down;
	std::bitset<Count> Pressed;
	std::bitset<Count> Released;

	void Set(size_t index, bool down)
	{
		if (down && !Down.test(index))
			Pressed.set(index);
		else if (!down && Down.test(index))
			Released.set(index);
		Down.set(index, down);
	}

	void ClearTransitions()
	{
		Pressed.reset();
		Released.reset();
	}
```

1. **Lines 27–34:** a press sets Pressed only when the key was up; a release sets Released only when it was down. A press followed by a release inside one frame sets both.
2. **Lines 36–40:** clearing the edges leaves Down alone, because a key still held stays held.

:::example[A held key and a tap inside one frame]
Take six frames. W goes down before frame 2, stays down, and comes up before frame 4. The player taps Space, a press and a release, before frame 5. The table shows what the game reads in its update.

| Frame | Events before the update | W down | W pressed | W released | Space down | Space pressed | Space released |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | no | no | no | no | no | no |
| 2 | W press | yes | yes | no | no | no | no |
| 3 | none | yes | no | no | no | no | no |
| 4 | W release | no | no | yes | no | no | no |
| 5 | Space press, Space release | no | no | no | no | yes | yes |
| 6 | none | no | no | no | no | no | no |

W is down in frames 2 and 3, and pressed only in frame 2: a jump on pressed happens once, while a walk on down lasts two frames. The Space tap is never down at an update. A game that compares down with the last frame sees nothing in frame 5. A game that reads pressed sees the tap, and sees the release too.
:::

Strata reads the state through `Input::IsKeyDown`, `Input::IsKeyPressed` and `Input::IsKeyReleased`, and the same three exist for mouse buttons and gamepad buttons. The edges last one input frame, the span between two calls of `Input::BeginFrame` in which the game updates. When the editor pauses a game, the frames stop, so a tap made during the pause waits for the next update instead of passing unseen. [Input devices and their state](../input/devices-state.md) explains this in the code.

## Read pressed in the frame update

A game has two kinds of update. The frame update runs once per frame. The fixed update runs at a constant step, zero or more times in a frame, so that physics stays steady ([Time](../core/time.md)). Strata runs the frame update first, then the fixed steps.

The edges belong to the frame, not to the step. Suppose the fixed step is 20 ms and a frame lasts 50 ms. The first frame owes 50 ms, so two steps run, and each sees pressed as true. A jump read in the fixed update happens twice.

Now suppose the frame lasts 16.7 ms. No step is due, so zero steps run, and the next frame clears the press before any step sees it. The jump is lost.

Read edges in `OnUpdate`, once per frame, and keep the result in a field of your script. The fixed update then takes the field and clears it after use. The held state, down, is safe in either update, because it stays true across the steps.

## Text is not key input

Games also need words: a player's name, a chat line. The naive answer builds a string from key presses. It fails at once. The key code for the A key says nothing about capital letters, accents or other layouts. It cannot make "é" on a layout with a dead key, where one key press adds an accent and the next key adds the letter.

**Typed text** is the sequence of characters the keyboard produces after the layout, the shift keys and any input method have acted. The window system delivers it as a separate character event, one per character, each holding a Unicode code point, the number that names a character. Strata's character callback hands it to `Input::ProcessText` and also sends a typed event.

Some languages need more than one key per character. An **IME**, short for input method editor, is a program of the system that turns several key presses into one character: typing `nihongo` makes three characters of Japanese, from seven keys. The game sees seven key events and three character events. Only the character events say what the person meant.

Strata stores a frame's typed text as UTF-8, the :term[byte]{id=byte} encoding of Unicode ([Bytes](../basics/bytes.md)). It ignores control characters and invalid code points. It keeps at most 1,024 bytes per frame, in whole characters, and drops the rest of a frame's text. A game reads it with `Input::GetTypedText`. The game's own user interface handles input method composition in [Text in the game's interface](../ui/text.md).

## Focus and capture decide who hears a key

One keyboard serves the editor, the running game, the game's menus and a text field. Each key press must reach one of them, not all. The usual answers are focus (the part the person is working in owns the input) and consumption (a part that takes an event hides it from the parts below).

Strata has four tools for this. `Input::SetEnabled` switches the devices off for the game: the editor enables the devices only while the game plays and the Game view has the focus, so typing into another panel never moves the robot. Pointer capture makes the game's mouse button and scroll queries report nothing while the game's interface holds a mouse gesture. Keyboard capture does the same for keys and typed text while a text field is edited. A fourth path, the raw reads, ignores all three, because a screen that asks the player to press a new control needs to see everything.

The mistake to avoid is a script that reads devices directly while the player types. With keyboard capture on, a name such as `Ana` reaches the text field as three characters, and the robot never sees the keys. [Input devices and their state](../input/devices-state.md) shows the capture in code.

## Actions turn controls into intents

Keys, sticks and buttons answer "what did the hand do?" A game cares about "what did the player want?" An intent is the thing a player wants to do, such as jump or move. A game that asks for the intent works with a keyboard, a pad or the controls the player chose.

Engines call the intent an action. An action has a kind. A button action is pressed, held or released. An axis action holds one number between -1 and 1.

A vector action holds two numbers, such as a walking direction. Bindings link controls to an action: Space and the pad's A button can both be Jump.

A composite builds one value from several controls. Four keys, W, S, A and D, make the vector (x, y). Normalizing matters here. Press W and D together: x is 1 and y is 1, and the length is $\sqrt{1^2 + 1^2}$, about 1.41, so the diagonal walks 41 % faster. Dividing by the length gives 0.71 and 0.71 with length 1.

Maps group the actions of one mode. A game enables the walking map while the robot walks, the driving map in a car and the menu map in a menu, and a disabled map reads as up. A player may also rebind: the game keeps the player's bindings apart from the project's defaults.

The engines compare as follows. The claims about them come from their manuals, listed at the end of the page.

| System | Actions | Maps or contexts | Composites | Modifiers and processors | Rebinding |
| --- | --- | --- | --- | --- | --- |
| Unity Input System | Button, value, pass-through | Action maps, switched at run time | A vector from four buttons | Processors, interactions | Functions to rebind |
| Unreal Enhanced Input | Input actions with value types | Mapping contexts with priorities | A modifier turns keys into axes | `Modifiers` and triggers | Keys the player may change |
| Godot `InputMap` | Named actions, global | None built in | Helper functions such as `get_vector` | A dead zone per action | Edit the map in code |
| Strata | Button, Axis, Vector2 | Maps, enabled per mode | 1D and 2D, the 2D one normalized | None | Players' bindings file |

Like Unity and Unreal, Strata keeps maps and composites. It drops modifiers, processors and chords.

## Strata keeps a polled state and builds actions on it

Strata's input has three layers. At the bottom, window callbacks fill a polled state and also send events. Above it, `Input` answers down, pressed and released, with captures. At the top, `InputActions` evaluates the project's maps once per frame from those answers.

The Third-Person sample binds its Move action to two sets of four keys and to the left stick. The next fence shows the first part of its entry in the project's settings. Look at the `2D:` prefix: the four names after it are up, down, left and right.

```json src="Samples/ThirdPerson/ThirdPerson.stproj#L95-L102"
"Bindings": [
	"2D:Key/W,Key/S,Key/A,Key/D",
	"2D:Key/Up,Key/Down,Key/Left,Key/Right",
	"Gamepad/LeftStick"
],
"DeadZone": 0.15,
"Kind": "Vector2",
"Name": "Move"
```

The sample binds Jump to `Key/Space` and `Gamepad/A`, so its script asks `Input::IsActionPressed("Gameplay/Jump")` in `OnUpdate` and never names a key. The same script reads `Input::GetActionValue("Gameplay/Move")` for walking. Every action reads from the same polled queries as a raw key, so a keyboard capture hides actions too, and the typed name never walks the robot.

:::why[Why edges in the polled state and not only events?]
A game is a loop that wants one answer per frame. Events arrive at any moment, in any number, so each script would have to store them and clear them. One shared state with edges does this once, in one place, and every script gets the same answer. The cost is that the edges last exactly one frame, so a script that reads late loses them, as the previous section showed.
:::

## What this design cannot do

Strata keeps no modifiers, chords or processors, so "Shift plus Jump" or a custom curve for a stick is code in your script. Mouse motion and scroll stay on the raw functions, not in actions. Strata has no touch input: it has no touch screens or gestures. Many engines map each finger to a pointer; Strata does not, so [what Strata does not do](../appendix/not-in-strata.md) lists it.

A polled state also hides the order of events inside one frame. If a key goes down and up and down again before one update, the game sees a single pressed edge and a released edge, and cannot tell which came first. Layers that need the exact order read events instead.

## Common mistakes

- **Key codes taken for characters.** Symptom: on `AZERTY` the player's A key walks right when the code says `Key::A`. Fix: bind positions for controls and read typed text for characters.
- **Key repeat used for movement.** Symptom: the character walks in jerks and the speed changes with the system's settings. Fix: read the held state; repeat sends events only.
- **"Pressed" made by comparing with the last frame.** Symptom: quick taps vanish after a slow frame. Fix: use the edge answers.
- **Text built from key presses.** Symptom: no capitals, no accents, nothing from an input method. Fix: read typed text.
- **Pressed read in the fixed update.** Symptom: a jump that happens twice at low frame rates and never at high ones. Fix: read in `OnUpdate` and keep a flag.
- **Gameplay that reads devices while a text field is edited.** Symptom: typing a name moves the player. Fix: read through the gameplay queries or actions, which keyboard capture hides.

## Summary

- A key press reaches the game as an event from the window system; the key code names a position on a US layout, and repeat only makes events.
- A game polls down, pressed and released; the frame clears the edges first, and a tap inside one frame reports both edges while a comparison with the last frame loses it.
- Pressed lasts one frame, so a fixed update that runs zero or two times would miss or repeat it; read it in `OnUpdate`.
- Typed text comes from character events after layouts and input methods, and keyboard capture keeps a text field's typing from reaching the player.
- A game reads actions, intents bound to controls, so that a pad, a rebound key and a composite all give the same answer.

## Check yourself

1. On a French `AZERTY` keyboard a player presses the key labelled A. Which `Key` value does Strata report, and which character does the typed event carry?

   :::answer{tests="sources"}
   The key code is `Key::Q`, 81, because key codes name the position of a key on a US layout, and the key labelled A sits where Q sits there. The character event carries the code point of the letter "a", 97, because the character comes after the layout. Position drives controls; characters drive text.
   :::

2. A game polls once per frame. W is held in frames 2 and 3 and released before frame 4. What do pressed and released report in frames 2, 3 and 4?

   :::answer{tests="polling-edges"}
   Pressed is true in frame 2 only, false in frames 3 and 4. Released is true in frame 4 only. The edges last one frame, while down is true in frames 2 and 3.
   :::

3. Which choice explains a jump that happens twice at 20 fps? (a) The system's key repeat. (b) Pressed is read in a fixed update and two steps ran in the frame. (c) The key code was a letter. (d) The tap was shorter than a frame.

   :::answer{tests="fixed-update"}
   Choice (b) holds. Pressed stays true for the whole frame, so each of two steps sees it. Choice (a) is wrong because repeat sends events and never changes the state. Choice (c) names a position problem, not a doubled jump. Choice (d) loses a jump, it does not double one.
   :::

4. A menu field asks for a player name while the robot stands in the scene. Which mechanism stops the letters from walking the robot, and which read still sees the keys?

   :::answer{tests="text-focus"}
   Keyboard capture, set by the text field, makes the gameplay key queries and `Input::GetTypedText` report nothing. The raw reads and `Input::GetKeyState` ignore the capture, so the field itself, and a screen that waits for a new binding, still see the keys.
   :::

5. A game's walk reads W, A, S and D by key. Name two things the player loses compared with a Move action.

   :::answer{tests="intents"}
   The player cannot use a pad or another layout's keys without new code, and cannot rebind the keys. A game that adds the four values by hand also walks 41 % faster on a diagonal, unless it divides by the length; a composite already does.
   :::

## Exercises

1. **Basic.** A player uses a German keyboard, where Y and Z swap places compared with a US one. Which `Key` value does the key labelled Z report, and why must the player be able to change a jump bound to `Key/Y`?

   :::answer[Worked solution]{tests="sources,intents"}
   The key labelled Z sits where US Y sits, so it reports `Key::Y`. A jump bound to `Key/Y` is a position the German player finds at the label Z, which may feel wrong, so the game lets the player rebind. Strata saves the player's choice in `InputBindings.json` in the game's save folder.
   :::

2. **Medium.** Predict, then run. A program plays six frames of one Space key: a press arrives before frame 2, a release before frame 4, and a press with a release before frame 5. The fixed update runs 0, 2, 1, 1, 0 and 1 times. Predict the jumps counted from pressed in the frame update, from a comparison with the last frame, and from pressed in the fixed update.

   :::answer[Worked solution]{tests="polling-edges,fixed-update" solution="sketches/input-how-input-works-edges.cpp"}
   The program applies each frame's events to a `Button`, then counts. Read it, then compare its output with your numbers.

   ```cpp sketch="input-how-input-works-edges.cpp"
   #include <cstdio>

   // One key as the polled state keeps it: held now, and what changed since the frame began.
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

   	void BeginFrame()
   	{
   		Pressed = false;
   		Released = false;
   	}
   };

   int main()
   {
   	// Per frame: 0 nothing happened, 1 a press arrived, 2 a release arrived, 3 a press and a release arrived.
   	const int events[6] = { 0, 1, 0, 2, 3, 0 };
   	// Per frame: how many fixed steps ran after the frame's update.
   	const int steps[6] = { 0, 2, 1, 1, 0, 1 };

   	Button space;
   	bool lastDown = false;
   	int updateJumps = 0;
   	int comparedJumps = 0;
   	int fixedJumps = 0;
   	for (int frame = 1; frame <= 6; frame++)
   	{
   		space.BeginFrame();
   		const int event = events[frame - 1];
   		if (event == 1 || event == 3)
   			space.Set(true);
   		if (event == 2 || event == 3)
   			space.Set(false);

   		const bool compared = space.Down && !lastDown;
   		lastDown = space.Down;
   		updateJumps += space.Pressed ? 1 : 0;
   		comparedJumps += compared ? 1 : 0;
   		fixedJumps += space.Pressed ? steps[frame - 1] : 0;
   		std::printf("Frame %d: down=%d pressed=%d released=%d compared=%d steps=%d\n", frame, space.Down, space.Pressed,
   			space.Released, compared, steps[frame - 1]);
   	}
   	std::printf("Jumps: update %d, compared with the last frame %d, fixed update %d\n", updateJumps, comparedJumps, fixedJumps);
   	return 0;
   }
   ```

   ```text output-of="input-how-input-works-edges.cpp"
   Frame 1: down=0 pressed=0 released=0 compared=0 steps=0
   Frame 2: down=1 pressed=1 released=0 compared=1 steps=2
   Frame 3: down=1 pressed=0 released=0 compared=0 steps=1
   Frame 4: down=0 pressed=0 released=1 compared=0 steps=1
   Frame 5: down=0 pressed=1 released=1 compared=0 steps=0
   Frame 6: down=0 pressed=0 released=0 compared=0 steps=1
   Jumps: update 2, compared with the last frame 1, fixed update 2
   ```

   1. **Lines 12–15:** the same rules as the engine's state: a press sets pressed only from up.
   2. **Line 40:** each frame starts by clearing the edges.
   3. **Line 47:** the faulty test, down now and up before.
   4. **Line 51:** a fixed update that reads pressed counts once per step.

   Pressed is true in frames 2 and 5, so the frame update counts 2 jumps. The comparison misses the tap of frame 5 and counts 1. The fixed update sees frame 2 with two steps and frame 5 with none, so it counts 2 jumps: the held press doubled and the tap lost.
   :::

3. **Hard.** Design the maps and actions of a game with a walk mode, a drive mode and a menu. List the actions of each map, their kinds and their bindings on a keyboard and a pad, and say which maps are enabled at the start and when they change.

   :::answer[Worked solution]{tests="intents"}
   `Walk` holds `Move` (Vector2: `2D:Key/W,Key/S,Key/A,Key/D` and `Gamepad/LeftStick`) and `Jump` (Button: `Key/Space`, `Gamepad/A`). `Drive` holds `Steer` (Axis: `1D:Key/A,Key/D` and `Gamepad/LeftX`), `Throttle` (Axis: `1D:Key/S,Key/W` and `Gamepad/RightTrigger+`) and `Exit` (Button: `Key/E`, `Gamepad/Y`).

   `Menu` holds `Resume` (Button: `Key/Escape`, `Gamepad/Start`). The reserved `UI` map exists in every set and serves the game's own interface. At the start only `Walk` is enabled. Entering a car disables `Walk` and enables `Drive`, and a held `Jump` reports released in the next input frame. Opening the menu disables the mode in use and enables `Menu`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Input/Input.h` and `Strata/src/Strata/Input/Input.cpp`: the polled state, `Input::BeginFrame`, the captures and `Input::ProcessText`.
- `Strata/src/Strata/Input/KeyCodes.h`: the key codes, named by US position.
- `Strata/src/Platform/GLFW/GLFWWindow.cpp`: the callbacks and the gamepad polling.
- `Strata/src/Strata/Core/Application.cpp`: `Application::RunFrame` and its Input stage.
- `Strata/src/Strata/Scene/Scene.cpp`: where the frame update runs before the fixed steps.
- `Strata/src/Strata/Input/InputActions.h`: the actions, their kinds, composites and the players' bindings.
- `StrataEditor/src/Panels/GameViewPanel.cpp`: the Game view enables the input while it has the focus.
- The project's settings section `Input.Actions` holds the maps; the players' file is `InputBindings.json`.
- `StrataScriptCore/Include/StrataScript/Script.h`: `OnUpdate` and `OnFixedUpdate`.

## Further reading

- GLFW input guide (<https://www.glfw.org/>, intermediate): key tokens, character input and the difference between them.
- Godot documentation on input events and `InputMap` (docs.godotengine.org, beginner): actions and how a game reads them.
- Unity's manual for the Input System package (beginner): actions, maps, composites and rebinding.
- Unreal Engine's documentation for Enhanced Input (intermediate): mapping contexts, modifiers and triggers.
