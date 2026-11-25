---
id: input/devices-state
title: "Input devices and per-frame state"
description: "How Input stores the keyboard, mouse and gamepads for one input frame, how edges, suspension, typed text and captures work, and why."
kind: internals
size: L
tracks: [E]
needs: [core/time, basics/bytes, input/how-input-works]
time: 80
learn:
  - id: codes
    text: explain why key codes are script ABI and are never renumbered, and how names reach them
  - id: edges
    text: trace a tap of Space from GLFW's callback to a script's IsKeyPressed and say what each frame reports
  - id: suspension
    text: predict what the game sees while input frames are suspended and after they resume
  - id: typed-text
    text: explain how typed text is assembled and checked, and why a frame keeps at most 1,024 bytes
  - id: capture
    text: choose the query that sees a key or a character while the keyboard is captured or input is disabled
since: 0.3.0
status: final
---

In the Third-Person sample, the robot jumps when the player taps Space. Between the key going down and the robot leaving the ground, the press passes through the :term[operating system]{id=operating-system}, a window library, a few functions of the engine and a script. `Input` is the part in the middle that remembers. It holds the state of the keyboard, the mouse and the gamepads as of the current input frame. A script asks it questions such as "was Space pressed in this frame?".

`Input` is static and belongs to the :term[main thread]{id=main-thread}, and the platform feeds it. It knows nothing of actions such as "Jump", and nothing of the game's user interface.

This page follows one tap of Space from :term[GLFW's]{id=glfw} :term[callback]{id=callback} to a script's call of `IsKeyPressed`. It then shows a toy version of the idea, the real code in the order the data flows, and the rules that keep the state honest. When you finish, you can say what `IsKeyPressed` returns in each frame of a tap, a hold and a paused game. You can also say who sees a key while a text field is being edited.

## The problem and how engines solve it

The operating system tells a program about a key when the key changes: "Space went down", and some time later "Space went up". A game does not want that story. In every frame it wants answers. Is the player holding forward? Did the jump key go down since the last frame?

The two views do not fit, because events arrive at any moment and the game updates at fixed points of the :term[frame loop]{id=game-loop}. The [page on how input works](how-input-works.md) names the ideas of polling and events; this page builds the polling side.

An engine can bridge the gap in three ways. It can hand the events themselves to the game in a queue, and let each system read what it needs in order. A queue keeps every detail, but each system must rebuild the state ("is Space down now?") for itself, and two systems that read the queue differently disagree.

The second way copies a snapshot of the whole state for each system, so that every system reads a frozen picture. A snapshot is simple to reason about and costs a copy per reader. The third way keeps one shared state that the platform updates and every system polls. Strata takes the third way.

A shared state has one price: it must say which changes happened in the current frame. A key that goes down and up between two frames would otherwise vanish. Strata keeps three flags for each key, and clears two of them at the start of each frame. The rest of the page explains the details, the rules around them and what the choice cannot do.

## Codes and names

Every key is a number, its :term[key code]{id=key-code}. Strata names a key by where it sits on a United States (US) keyboard, not by the letter on its cap. The key that is `W` on a US keyboard keeps the code of `W` on a French keyboard.

The codes are the values GLFW uses: Space is 32, `A` is 65 and `D` is 68. The type is `KeyCode`, a 16-bit number, and the engine accepts codes below `c_MaxKeyCode`, which is 512. The file `Strata/src/Strata/Input/KeyCodes.h` lists them in the :term[namespace]{id=namespace} `Key`.

The codes are part of the script application binary interface (ABI), the binary contract between the engine and compiled script modules. A compiled script embeds the number 32 wherever its source says `Key::Space`. If the engine changed the numbers, every module built before the change would read the wrong key. The :term[header]{id=header} says so in a comment: the codes were taken from GLFW's and never change. The GLFW backend passes its codes through, and a backend for another window library translates its own codes to these.

Mouse buttons follow the same rule, in `Strata/src/Strata/Input/MouseCodes.h`. The type is `MouseCode`, and `c_MaxMouseButtons` is 8, so a button is a number from 0 to 7. `Mouse::ButtonLeft` is 0, `Mouse::ButtonRight` is 1 and `Mouse::ButtonMiddle` is 2. The same file defines `CursorMode`, which is `Normal`, `Hidden` or `Locked`; [the page on the mouse and the cursor](mouse-cursor.md) uses it.

Numbers are poor for people and files, so `InputNames` gives every key, mouse button, gamepad button and gamepad axis a name. The key names spell the `Key` constants: `A`, `D1` for the digit 1, `Space`, `Left`, `F5`, `KPEnter` and `LeftShift`. The mouse buttons are `Left`, `Right`, `Middle` and `Button3` to `Button7`, and `Button0` to `Button2` are accepted too. Lookups ignore case, so "space" finds the code 32.

`GetKeyName` turns a code into its name and returns a :term[null pointer]{id=null-pointer} for a code that names no key. `FindKey` goes the other way and returns an empty `std::optional` for an unknown name. `GetKeyNames` lists every key name in code order. The editor's commands, the input bindings of a project and the editor's own pages use these names, so that no file holds a bare number. The Third-Person sample binds its Jump action to `Key/Space`.

## The map

Two flows meet in `Input`. Real devices reach it through the window library, and tools reach it through a queue of simulated events. Readers on the other side ask for merged answers.

```mermaid caption="Devices feed Input through GLFW's callbacks, tools feed it through a queue, and the merged queries serve scripts, the game interface and the input actions." alt="A flow diagram. Operating system events reach GLFW, whose callbacks call the process functions of Input and send engine events. Tools queue simulated events that apply when a frame starts. Device state and simulated state merge in the query functions that scripts, the game interface and the input actions read."
flowchart LR
	os["Operating system"] --> glfw["GLFW (window events)"]
	glfw --> callbacks["GLFWWindow callbacks"]
	callbacks --> process["Input::ProcessKey and the other Process functions"]
	callbacks --> events["Engine events"]
	poll["Gamepad polling"] --> process
	tools["Editor commands and tests"] --> simulate["Input::Simulate functions"]
	simulate --> queue["Simulated queue"]
	queue -->|"BeginFrame"| simulated["Simulated state"]
	process --> device["Device state"]
	device --> queries["Merged queries"]
	simulated --> queries
	queries --> scripts["Scripts through the host API"]
	queries --> ui["Game interface"]
	queries --> actions["InputActions"]
```

The merge is the reason the state has two halves. A tool that plays the game, such as an automated test, must look to the game exactly like a person. [The page on simulated input](simulated.md) gives the merge rules. Here it is enough to know that a key is down while either source holds it.

The state is read at a fixed place in each frame. In `Application::RunFrame`, the Input stage comes right after the work queued for the main thread: `Input::BeginFrame`, then `Window::ProcessEvents`, then `InputActions::Update`. Modules and layers run after that stage, so every system of a frame reads the same answers. [The page on the frame loop](../core/frame-loop.md) shows the stages around it.

One more piece sits in the map. `Input` needs the window's size, and it needs to hide or show the cursor, but it must not include the window class, because the application shell sits above `Input` in the layers.

`InputWindow`, in `Strata/src/Strata/Input/InputWindow.h`, is a small interface with three functions: `GetWidth`, `GetHeight` and `SetCursorMode`. `Window` implements it, and `Application` hands it to `Input::SetWindow`. The dependency now points downward: the window knows `Input`, and `Input` knows only an interface. [The page on layers and registries](../core/layers-registries.md) describes the idea.

## The contract

What may a caller assume, and what must a caller do? Three rules carry most of it, and each has a reason.

:::rule[Input is main-thread polling state, updated once per frame]
Read Pressed and Released in `OnUpdate`, on the main thread. The answers describe the current input frame. A script's `OnFixedUpdate` runs zero, one or several times in one frame (see [Time](../core/time.md)), so a press read there would be seen twice or not at all. [The scripting pages](../scripting/abi-sdk.md) show how scripts read input.
:::

:::rule[Suspend input frames while the game does not update]
When the editor pauses a game and no step is pending, the game's frames do not run, yet the window keeps producing events. Without suspension, the engine would clear a press at the next loop turn, and the game would never see a key pressed during the pause. The editor's call that suspends belongs to [stepping a paused game](../editor/stepping.md).
:::

:::rule[Key codes are ABI and never change]
Compiled script modules embed key codes, so a change of the numbers breaks every module built before it. A backend for a different window library translates its codes into these.
:::

Three smaller promises follow from the code. A code that is out of range is ignored or answers "up": `IsKeyDown` with the code 517 returns false, and `ProcessKey` with it changes nothing. Simulated events never apply in the middle of a frame. They wait for the next `BeginFrame`, because half of the frame's systems would see a press that the other half missed. And capturing, disabling and suspending change what a query answers, never what the state records: the state keeps tracking under all three.

## A toy version

The toy below keeps the whole idea. A `ButtonStates` holds three `std::bitset` values of 512 bits each, one bit per key: which keys are down, which went down in this frame and which went up in this frame. `Set` is the only function that records an edge, and it records one only when the state changes. The frame starts with `ClearTransitions`, then the platform's events call `Set`, and then the game reads. The script of events is the Space example: held for two frames, released, then tapped inside one frame.

```cpp sketch="input-devices-state-toy.cpp"
// A toy keyboard: three bitsets and a frame boundary, the whole of polled input state.
// Each frame starts by clearing the transitions, then the window's events arrive, then the game reads.
#include <bitset>
#include <cstddef>
#include <cstdio>
#include <vector>

constexpr size_t c_MaxKeyCode = 512;
constexpr size_t c_KeySpace = 32; // GLFW's value for Space, and the engine's

struct ButtonStates
{
	std::bitset<c_MaxKeyCode> Down;
	std::bitset<c_MaxKeyCode> Pressed;
	std::bitset<c_MaxKeyCode> Released;

	// The one place that records an edge: only a change of state is a transition.
	void Set(size_t key, bool down)
	{
		if (down && !Down.test(key))
			Pressed.set(key);
		else if (!down && Down.test(key))
			Released.set(key);
		Down.set(key, down);
	}

	void ClearTransitions()
	{
		Pressed.reset();
		Released.reset();
	}
};

struct KeyEvent
{
	size_t Key;
	bool Down;
};

int main()
{
	// What the operating system reports between two frames. Frames 1 and 2 hold Space; frame 4 is a tap inside one frame.
	const std::vector<std::vector<KeyEvent>> frames = {
		{ { c_KeySpace, true } },
		{},
		{ { c_KeySpace, false } },
		{ { c_KeySpace, true }, { c_KeySpace, false } },
		{},
	};

	ButtonStates keys;
	for (size_t frame = 0; frame < frames.size(); frame++)
	{
		keys.ClearTransitions(); // Input::BeginFrame
		for (const KeyEvent& event : frames[frame])
			keys.Set(event.Key, event.Down); // The window's callbacks
		std::printf("frame %zu: down %d pressed %d released %d\n", frame + 1, static_cast<int>(keys.Down.test(c_KeySpace)),
			static_cast<int>(keys.Pressed.test(c_KeySpace)), static_cast<int>(keys.Released.test(c_KeySpace)));
	}
}
```

```text output-of="input-devices-state-toy.cpp"
frame 1: down 1 pressed 1 released 0
frame 2: down 1 pressed 0 released 0
frame 3: down 0 pressed 0 released 1
frame 4: down 0 pressed 1 released 1
frame 5: down 0 pressed 0 released 0
```

1. **Lines 13–15:** the three sets of bits are the whole state of the keyboard: one bit per key in each.
2. **Lines 18–24:** `Set` compares the new state with `Down` before it writes, so repeating "down" records no second press.
3. **Line 54:** the frame boundary: the transitions are cleared before the new events arrive, and `Down` stays.
4. **Line 56:** stands for the window's callbacks; the real code calls `Input::ProcessKey` here.

The first two lines of output are a hold. Frame 1 is the press, so Pressed is 1. In frame 2 the key stays down and Pressed is back to 0, because the clear at the start of the frame removed it. Frame 3 is the release.

Frame 4 shows why Pressed and Released are separate sets of bits: the tap goes down and up before the game looks, and the game still sees both edges, with Down at 0. A single "state changed" flag would lose frame 4.

The toy omits most of what the real code needs: several sources, text, captures, gamepads and suspension. Each addition below has a reason.

## The real code

### `ButtonStates` records the edges

The real `ButtonStates` is the toy's, made a template of the number of buttons. `Input` has one for the keys (`c_MaxKeyCode` bits), one for the mouse buttons (`c_MaxMouseButtons` bits) and one for each gamepad. Each kind exists twice, once for the devices and once for simulated input, and `IsMergedDown` and `IsMergedTransition` combine them.

```cpp src="Strata/src/Strata/Input/Input.cpp#L19-L41"
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
};
```

1. **Lines 23–25:** one bit per button in each of the three states; the template's count is the number of keys or buttons.
2. **Lines 29–32:** `Set` records Pressed or Released only when the state changes, so a repeated "down" adds nothing.
3. **Line 33:** the new state is stored last, after the comparison with the old one.
4. **Lines 36–40:** `ClearTransitions` empties the two edge sets and leaves `Down` alone.

### The GLFW callbacks feed the state and the events

GLFW calls a function of the engine whenever the window gets a key event, while `Window::ProcessEvents` runs `glfwPollEvents`. Each callback does two jobs. It updates `Input`, which answers polling questions, and it builds an engine event for the layers that listen. The two stay separate: the state is for the game, and the events are for the user interface and the editor.

Search the key callback below for three things. A key that GLFW cannot name arrives with a negative code, and the callback returns at once, so such a key never reaches `Input`. A press and a release change the state and send an event. A repeat, which the operating system sends while a key is held, only sends an event. It never touches the state, because it is no new edge.

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

1. **Lines 288–289:** a key that GLFW cannot name has a negative code, so the callback returns and `Input` never hears of it.
2. **Lines 297–301:** a press changes the state first and then sends the engine event.
3. **Lines 305–309:** a release does the same with the opposite edge.
4. **Lines 312–316:** a repeat builds the event and never calls `ProcessKey`.

One more behavior comes from GLFW itself. When a window loses focus, GLFW calls the callbacks with a release for every key and every mouse button that it still holds as pressed (`Strata/vendor/glfw/src/window.c`). The releases pass through the same code, so after Alt+Tab nothing stays down. The character callback works alike: `glfwSetCharCallback` calls `Input::ProcessText` with the :term[code point]{id=code-point} that the keyboard layout produced.

### The Input stage runs first

The frame loop calls the three functions of the stage in this order.

```cpp src="Strata/src/Strata/Core/Application.cpp#L300-L308"
ST_PROFILE_STAGE("Input");
Input::BeginFrame();
if (m_Window)
{
	m_Window->ProcessEvents();
	m_Minimized = m_Window->IsMinimized();
}
// The frame's input is in: the actions take it (once per input frame; a binding capture at every call).
InputActions::Update();
```

The order matters. `BeginFrame` first clears what the last frame left. The events that `ProcessEvents` then delivers set the new edges, so they are fresh when the layers update. `InputActions::Update` then turns the frame's keys into the project's named actions, once per input frame. Its home is [the page on input actions](actions.md).

### `BeginFrame` starts an input frame

An **input frame** is the span between two calls of `Input::BeginFrame` in which the game updated. Normally an input frame is a frame of the loop. The two differ only when frames of the loop pass without a game update. `Input::GetFrameIndex` counts input frames.

```cpp src="Strata/src/Strata/Input/Input.cpp#L553-L586" symbol="Input::BeginFrame"
void Input::BeginFrame()
{
	// Transitions and movement are cleared once the game has had them (the first BeginFrame after a frame it updated in);
	// while input frames are suspended, what happens meanwhile accumulates for the game's next update.
	if (s_State.FrameSeen)
	{
		s_State.Keys.ClearTransitions();
		s_State.MouseButtons.ClearTransitions();
		s_State.MouseDelta = glm::vec2(0.0f);
		s_State.ScrollDelta = glm::vec2(0.0f);
		s_State.TypedText.Clear();
		for (GamepadState& gamepad : s_State.Gamepads)
			gamepad.Buttons.ClearTransitions();

		SimulatedState& simulated = s_State.Simulated;
		simulated.Keys.ClearTransitions();
		simulated.MouseButtons.ClearTransitions();
		for (SimulatedGamepad& gamepad : simulated.Gamepads)
			gamepad.Buttons.ClearTransitions();
		simulated.MouseDelta = glm::vec2(0.0f);
		simulated.ScrollDelta = glm::vec2(0.0f);
		simulated.TypedText.Clear();
		s_State.FrameSeen = false;
	}
	if (s_State.Suspended)
		return;

	s_State.FrameIndex++;
	SimulatedState& simulated = s_State.Simulated;
	for (const SimulatedEvent& event : simulated.Queue)
		ApplySimulatedEvent(simulated, event);
	simulated.Queue.clear();
	s_State.FrameSeen = true; // The game updates in this frame
}
```

1. **Line 557:** the clear happens only when the game has seen the current frame.
2. **Lines 559–574:** transitions, movement and text of the devices and of simulated input are cleared together.
3. **Lines 577–578:** while input frames are suspended, the function returns here, before any frame is counted.
4. **Line 580:** the input frame counter advances only for frames the game updates in.
5. **Lines 582–585:** the simulated queue applies at the frame boundary, and the frame counts as seen.

The function makes two decisions. The first asks whether the game has seen the current transitions (`FrameSeen`). If it has, the function clears every transition, movement and text of the devices and of simulated input, and marks the frame as not seen. If it has not, the transitions stay.

The second asks whether input frames are suspended. If they are, the function returns before it counts a frame or applies the simulated queue.

:::example[Space in a hold, a tap and a pause]
Take the Third-Person robot and a game that runs 60 frames a second, so one frame lasts 16.7 ms. A script calls `Input::IsKeyPressed(Key::Space)` in `OnUpdate`. The table shows what the three queries return in each frame of three cases. In the paused case, the editor pauses the game after frame 1, and the player presses Space during the pause.

| Case | Frame | What happens before the update | Down | Pressed | Released |
| --- | --- | --- | --- | --- | --- |
| Hold | 1 | Space goes down | yes | yes | no |
| Hold | 2 | nothing | yes | no | no |
| Hold | 3 | Space goes up | no | no | yes |
| Tap | 1 | Space goes down and up | no | yes | yes |
| Pause | 1 | nothing | no | no | no |
| Pause | 2 | the game was paused for 50 ms; Space went down meanwhile | yes | yes | no |
| Pause | 3 | nothing | yes | no | no |

A hold of three frames lasts 50 ms and is reported as one press and one release, however long it lasts. A tap shorter than a frame reports both edges in one frame, with Down at no.

In the paused case, about three loop turns pass without a game update. No input frame starts in them, so the press waits. The game's next update reports it as Pressed, and the frame index is only one higher than before the pause. The test `Suspended input frames keep their transitions and queued events for the next frame` checks the same sequence with the keys A and D.
:::

### Suspension keeps presses for the game's next update

When the editor pauses a game, the game does not update, yet the loop keeps running. If `BeginFrame` cleared the edges at every loop turn, a key pressed during the pause would be cleared before any game frame saw it. **Suspended input frames** are input frames that the engine halts while the game does not update.

`Input::SetSuspended(true)` makes `BeginFrame` end the frame the game saw and then return. Transitions, mouse movement, scroll and queued simulated events wait for the next update. Device events keep updating the state meanwhile.

The editor decides when to suspend; [the page on stepping](../editor/stepping.md) explains its call, `UpdateInputSuspension`. Simulated input counts its own frames in input frames, so `GetFrameIndex` stands still across a pause. The exercises below rebuild the pause in the toy.

Suspension has a cost. After a long pause, the first update reports every press and every release since the pause began as if they happened in one frame. A key pressed and released during the pause shows both edges together. That is the price of never losing an edge.

### The enabled flag silences the devices

In the editor, the Game view shows the game next to panels. When the Game view loses focus, keys typed into another panel must not move the player. `Input::SetEnabled(false)` makes every query report nothing from the devices. Keys and buttons are up, the mouse delta and the scroll delta are zero, and the :term[typed text]{id=typed-text} from the keyboard is empty.

The state keeps tracking underneath, so when the flag is enabled again, a key that is still held shows as down. Simulated input stays visible, because a tool drives the game on purpose, whatever has the focus. [The page on the Game view](../editor-ui/game-view.md) shows who calls `SetEnabled`. A game outside the editor never disables input in this way.

### Typed text is assembled and checked

Keys are not characters. Pressing the key `A` can type "a", "A", "ä" or nothing at all, depending on the layout, the Shift key, dead keys and input method editors, which compose Chinese or Japanese characters from several keys. The operating system knows the result, and GLFW's character callback reports it as a code point, a number that names one character of :term[Unicode]{id=unicode}. Strata writes the code point as :term[UTF-8]{id=utf-8}, one to four :term[bytes]{id=byte}. [The page on bytes](../basics/bytes.md) explains code points and UTF-8.

`Input::GetTypedText` returns the text typed during the current input frame as UTF-8, the bytes the rest of the engine uses for strings. Two limits apply. A frame keeps at most `c_MaxTypedTextBytes` bytes, which is 1,024, and it keeps whole characters. A code point is refused when it is not text. The refused ones are control characters (below 0x20, 0x7F, and 0x80 to 0x9F), numbers beyond 0x10FFFF and surrogates.

A **surrogate** is a code point from 0xD800 to 0xDFFF, which Unicode reserves for halves of a pair in UTF-16, so by itself it is invalid. `AppendCodepoint` writes the bytes of an accepted code point by its size: one byte below 0x80, two below 0x800, three below 0x10000 and four above.

```cpp src="Strata/src/Strata/Input/Input.cpp#L182-L215" symbol="AppendCodepoint"
// Appends a code point's UTF-8 to a frame's text while it fits within Input::c_MaxTypedTextBytes.
void AppendCodepoint(FrameText& text, uint32_t codepoint)
{
	if (text.Full)
		return;
	char bytes[4];
	size_t length = 0;
	if (codepoint < 0x80)
	{
		bytes[length++] = static_cast<char>(codepoint);
	}
	else if (codepoint < 0x800)
	{
		bytes[length++] = static_cast<char>(0xC0 | (codepoint >> 6));
		bytes[length++] = static_cast<char>(0x80 | (codepoint & 0x3F));
	}
	else if (codepoint < 0x10000)
	{
		bytes[length++] = static_cast<char>(0xE0 | (codepoint >> 12));
		bytes[length++] = static_cast<char>(0x80 | ((codepoint >> 6) & 0x3F));
		bytes[length++] = static_cast<char>(0x80 | (codepoint & 0x3F));
	}
	else
	{
		bytes[length++] = static_cast<char>(0xF0 | (codepoint >> 18));
		bytes[length++] = static_cast<char>(0x80 | ((codepoint >> 12) & 0x3F));
		bytes[length++] = static_cast<char>(0x80 | ((codepoint >> 6) & 0x3F));
		bytes[length++] = static_cast<char>(0x80 | (codepoint & 0x3F));
	}
	if (text.Bytes.size() + length <= Input::c_MaxTypedTextBytes)
		text.Bytes.append(bytes, length);
	else
		text.Full = true;
}
```

1. **Lines 185–186:** once a frame's text is full, nothing else is appended.
2. **Lines 189–210:** the code point's size picks the branch, and each branch writes the bytes of UTF-8.
3. **Lines 211–214:** the bytes are appended only if they fit within `c_MaxTypedTextBytes`; otherwise the frame is full.

:::example[Typing a word of five letters]
A player types `héllo`. The first letter, `h`, is U+0068 and takes one byte. The second, `é`, is U+00E9. It is above 0x7F and below 0x800, so the second branch writes two bytes, 0xC3 and 0xA9, and the word takes 6 bytes in all.

Now suppose the frame already holds 1,023 bytes and the player types `é`. The sum, 1,025, is more than 1,024, so `Full` becomes true. The `l` that comes next would fit, yet it is dropped too, because the frame keeps what was typed first and a gap in the middle would change the order of the text.
:::

Text from tools arrives as bytes, so it goes through a decoder: `Input::SimulateText` takes UTF-8 and decodes it by hand. The decoder refuses an encoding that is longer than the character needs, a surrogate written in UTF-8, and a sequence cut short. Each invalid sequence becomes `U+FFFD`, the replacement character, and the decoder continues with the next byte that can start a character. The devices' text comes first and the simulated text after it, within the same 1,024 bytes.

### Pointer capture and keyboard capture

A button on screen and a key that jumps compete for the same input. The game's interface is drawn in front of the world, so a click on a button must not also fire the gun. **Pointer capture** is a flag that the game interface sets while it owns the mouse: the game's queries for mouse buttons and scrolling then report nothing.

**Keyboard capture** is the same for keys and typed text while a text field is being edited, because typing a name must not move the player. Only the game's interface sets these flags; [the page on its input](../ui/input.md) shows when.

The interface itself must still see the click and the key. It uses queries that ignore the capture: `GetPointerState` for the pointer, `GetKeyState` for a key and `GetUncapturedTypedText` for the text. Binding capture, the menu that asks a player to press a new key, uses the raw queries (`IsRawKeyDown`, `IsRawMouseButtonDown`, `IsRawGamepadButtonDown` and `GetRawGamepadAxis`). They ignore capture, the enabled flag and suspension altogether.

The function below shows the rule for text. It starts from the devices' text, adds the simulated :term[text character]{id=text-character} by character, and stops when the next character would not fit.

```cpp src="Strata/src/Strata/Input/Input.cpp#L389-L405" symbol="Input::GetUncapturedTypedText"
std::string Input::GetUncapturedTypedText()
{
	std::string text = s_State.Enabled ? s_State.TypedText.Bytes : std::string();
	// Together within the frame's limit: simulated text after the devices', whole characters only.
	const std::string& simulated = s_State.Simulated.TypedText.Bytes;
	size_t index = 0;
	while (index < simulated.size())
	{
		const uint8_t lead = static_cast<uint8_t>(simulated[index]);
		const size_t length = lead < 0x80 ? 1 : ((lead & 0xE0) == 0xC0 ? 2 : ((lead & 0xF0) == 0xE0 ? 3 : 4));
		if (text.size() + length > c_MaxTypedTextBytes)
			break;
		text.append(simulated, index, length);
		index += length;
	}
	return text;
}
```

1. **Line 391:** the devices' text counts only while input is enabled.
2. **Lines 395–398:** the loop reads the simulated text one whole character at a time, taking the length from the lead byte.
3. **Lines 399–400:** a character that would pass the limit ends the text.

The table lists who sees what. "Devices hidden" means that only the devices' part is hidden and simulated input still shows.

| Query | Input disabled | Pointer captured | Keyboard captured |
| --- | --- | --- | --- |
| `IsKeyDown`, `IsKeyPressed`, `IsKeyReleased` | devices hidden | seen | hidden |
| `IsMouseButtonDown`, `IsMouseButtonPressed`, `IsMouseButtonReleased` | devices hidden | hidden | seen |
| `GetScrollDelta` | devices hidden | hidden | seen |
| `GetTypedText` | devices hidden | seen | hidden |
| `GetPointerState` | devices hidden | seen | seen |
| `GetKeyState` | devices hidden | seen | seen |
| `GetUncapturedTypedText` | devices hidden | seen | seen |
| `IsRawKeyDown` and the other raw queries | seen | seen | seen |

The raw row is the only one that ignores the enabled flag. Suspension changes no row: while input frames are suspended, each query answers with the transitions gathered since the game's last update. `Input::Reset` clears both captures, and the interface clears them itself when a text field loses focus or play stops.

### `Reset` brings everything back

`Input::Reset` replaces the whole state with a fresh one, keeps the window and resets the input actions as well. Tests call it first, so that each test starts from nothing.

### The script SDK shows the same state

A script never sees `Input` itself. The script software development kit (SDK), in `StrataScriptCore/Include/StrataScript/Input.h`, has an `Input` of its own. Its functions call the engine through the host application programming interface (API), as in `host->IsKeyDown(context, key)`. The answers are the ones above, in the same frame.

The SDK adds pieces that other pages teach: dead zones for gamepad sticks, input actions and binding capture. Its `GetTypedText` returns the capture-aware text. The comments of the header repeat the rule: the state is the current frame's, so read Pressed and Released in `OnUpdate`.

## What this choice cannot do

A polled state keeps no order. If the player pressed Space and then `A` in one frame, both show as pressed and the game cannot tell which came first. A game that needs the exact order, such as one that reads move sequences, would want the event queue. The engine sends events too, through the window's event callback, so the information exists, but it travels a different road.

A second limit is timing. All edges of a frame appear at its start, so a press that happened 1 ms after the previous update is reported 15 ms later at 60 frames a second. Strata prefers one consistent picture to the least delay.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| An event queue for gameplay | Libraries that offer a queue next to a key state array | The exact order of presses and a time stamp for each | Every system rebuilds the state, and a system that forgets to drain the queue misses presses |
| A snapshot copied for each system | Systems that read input on worker threads | A frozen picture, even for other threads | A copy per reader, and a rule for when to take it |
| The operating system's raw input API | Windows offers one for high-precision mice | Raw mouse data from several devices | Code for each platform, and no layouts or input methods |
| Asking GLFW for the key state directly | Small programs that call `glfwGetKey` | No state of its own | No edges that last a whole frame, no simulated input, no suspension |

## How it is tested

The suite `Core.Input` in `StrataTests/src/Core/InputTests.cpp` covers the state without a window. Its cases check that key transitions last one frame, including a tap inside a frame. They check that the viewport changes the mouse position and that `InputWindow` is all that `Input` needs of a window.

The cases also check that disabled input reports nothing but keeps tracking, that suspended frames keep their transitions, and that typed text is UTF-8 and stops at 1,024 whole bytes. They show that pointer and keyboard capture hide the game's queries and never the state. The suite `Core.InputNames` checks that every key name maps to its code and back, ignoring case.

Run them with `build/windows/bin/Debug/StrataTests.exe --test-suite=Core.Input*`. The tests create no window, so they need no :term[graphics card]{id=gpu}. A new regression test must fail without its fix.

## Changing it safely

A new device or flag extends `Input`. A new window library implements `InputWindow` and calls the `Process` functions from `Strata/src/Platform/`. Four rules keep the change safe, each with its reason.

- Never change a code's number. Compiled scripts embed it.
- Keep platform code in `Strata/src/Platform/`. GLFW and operating system headers stay in their own folders, so that the layering test can check that `Input` stays below the application shell.
- Handle bad data without asserting. Out-of-range codes, non-finite values and invalid text are ignored or replaced, never fatal.
- A change to a query's rules needs a case in the `Core.Input` suite beside the capture and suspension cases, and the feature test must still exercise it.

## Summary

- Key codes are GLFW's numbers, named by a US keyboard's layout. They are script ABI and never change, and `InputNames` turns them into the names that commands, bindings and the editor use.
- `ButtonStates` holds three `std::bitset` values for Down, Pressed and Released, and `Set` records an edge only when the state changes. A tap inside one frame reports Pressed and Released together.
- The GLFW callbacks feed `Input` and also send events. A repeat is an event only, keys GLFW cannot name never reach `Input`, and releases for every held key arrive when the window loses focus.
- `BeginFrame` clears transitions only once the game has seen them. While input frames are suspended, presses wait for the next update and the frame index stands still.
- Typed text is UTF-8 of whole characters, at most 1,024 bytes a frame, with control characters and surrogates dropped. Keyboard capture hides keys and text from the game and not from `GetKeyState` or `GetUncapturedTypedText`.

## Check yourself

1. A script calls `Input::IsKeyPressed(Key::Space)` in `OnUpdate`. The player holds Space for exactly three frames. Which line is right?

   - A. It returns true in all three frames, because the key is down.
   - B. It returns true in the first frame only.
   - C. It returns true in the frame of the release.
   - D. It returns true in the first frame, and `IsKeyDown` is false in the next two.

   :::answer{tests="edges"}
   B is right: the press is an edge, and `BeginFrame` clears the edge at the start of the next frame. A describes `IsKeyDown`. C describes `IsKeyReleased`, which fires in the frame in which the key goes up. D is wrong because `IsKeyDown` stays true for as long as the key is held.
   :::

2. Which statement about key codes is right?

   - A. The code of `W` depends on the keyboard layout of the player.
   - B. The engine may change codes in a release if it tells the editor.
   - C. A compiled script embeds the number, so the number never changes.
   - D. `InputNames` returns a name for every number below 512.

   :::answer{tests="codes"}
   C is right. A is wrong because codes follow the position on a US keyboard, not the layout. B is wrong because script modules are compiled already and cannot be told. D is wrong: `GetKeyName` returns a null pointer for a code that names no key.
   :::

3. Input frames are suspended. The player presses Space in the second tick of the pause, and the game resumes in the fifth tick. The frame index was 7 before the pause. In the first update after the pause, what are `IsKeyPressed(Key::Space)` and `GetFrameIndex()`?

   :::answer{tests="suspension"}
   The press waits, so `IsKeyPressed` returns true, and `GetFrameIndex` is 8. No frame was counted during the pause, and the resumed frame is the next one. The frame after that clears the press.
   :::

4. A text field has the keyboard. The player types `w` while input is enabled and not suspended. What do `IsKeyDown(Key::W)`, `GetKeyState(Key::W).Down`, `GetTypedText()` and `GetUncapturedTypedText()` return in that frame?

   :::answer{tests="capture"}
   `IsKeyDown(Key::W)` is false and `GetTypedText()` is empty, because keyboard capture hides both from the game. `GetKeyState(Key::W).Down` is true and `GetUncapturedTypedText()` is "w", because the interface's queries ignore capture. The raw query `IsRawKeyDown(Key::W)` is true as well.
   :::

5. The frame's text already holds 1,022 bytes. The player types "a", "€" and "b" in that order. The euro sign is U+20AC. What does the frame keep?

   :::answer{tests="typed-text"}
   The `a` takes 1 byte, which makes 1,023. The euro sign takes 3 bytes (0xE2, 0x82, 0xAC), which would make 1,026, so it does not fit and `Full` becomes true. The `b` would fit but is dropped as well. The frame keeps "a" and ends at 1,023 bytes.
   :::

## Exercises

1. **Basic.** In the test `Keyboard capture hides keys and typed text from the game, never from the key state`, the code presses `A`, types "a", simulates the text "b" and simulates Enter, then captures the keyboard. Predict what `IsKeyDown(Key::A)`, `GetKeyState(Key::A).Pressed` and `GetUncapturedTypedText()` return at once. Then predict what `GetUncapturedTypedText()` and `GetKeyState(Key::Enter).Pressed` return after the next `BeginFrame`.

   :::answer[Worked solution]{tests="capture,typed-text,edges"}
   At once, `IsKeyDown(Key::A)` is false (captured), `GetKeyState(Key::A).Pressed` is true and `GetUncapturedTypedText()` is "a". The simulated "b" and Enter still wait in the queue. After `BeginFrame`, the device frame is cleared and the queue applies, so `GetUncapturedTypedText()` is "b" and `GetKeyState(Key::Enter).Pressed` is true. `IsKeyPressed(Key::Enter)` stays false because the keyboard is captured. Compare with the test at line 681 of `StrataTests/src/Core/InputTests.cpp`.
   :::

2. **Medium.** Extend the toy of this page with suspension. A key pressed during a pause must be reported by the first update after it, and the frame index must stand still. Predict the table for six ticks, where ticks 3 and 4 are paused and `D` is pressed in tick 3, then write the program.

   :::answer[Worked solution]{tests="suspension,edges" solution="sketches/input-devices-state-pause.cpp"}
   The program adds two flags to the toy: `Suspended` and `FrameSeen`. `BeginFrame` clears transitions only when `FrameSeen` is true, then returns early when suspended, and otherwise counts a frame and sets `FrameSeen`. The press of D in tick 3 survives tick 4 because the frame was not seen, and tick 5 reports it with input frame 3.

   ```cpp sketch="input-devices-state-pause.cpp"
   // The toy keyboard with suspended input frames: transitions are cleared only once the game has seen them.
   // Ticks 3 and 4 are a paused game. D is pressed in tick 3; the game sees the press in tick 5.
   #include <bitset>
   #include <cstddef>
   #include <cstdio>

   constexpr size_t c_KeyCount = 128;
   constexpr size_t c_KeyA = 65;
   constexpr size_t c_KeyD = 68;

   struct Keyboard
   {
   	std::bitset<c_KeyCount> Down;
   	std::bitset<c_KeyCount> Pressed;
   	bool Suspended = false;
   	bool FrameSeen = true;
   	int FrameIndex = 0;

   	void Set(size_t key, bool down)
   	{
   		if (down && !Down.test(key))
   			Pressed.set(key);
   		Down.set(key, down);
   	}

   	// The engine's BeginFrame, reduced to its two decisions.
   	void BeginFrame()
   	{
   		if (FrameSeen)
   		{
   			Pressed.reset();
   			FrameSeen = false;
   		}
   		if (Suspended)
   			return;
   		FrameIndex++;
   		FrameSeen = true;
   	}
   };

   int main()
   {
   	Keyboard keyboard;
   	for (int tick = 1; tick <= 6; tick++)
   	{
   		keyboard.Suspended = tick == 3 || tick == 4;
   		keyboard.BeginFrame();
   		if (tick == 1)
   			keyboard.Set(c_KeyA, true);
   		if (tick == 3)
   			keyboard.Set(c_KeyD, true);
   		std::printf("tick %d: game updates %d, input frame %d, A pressed %d, D pressed %d\n", tick, static_cast<int>(!keyboard.Suspended),
   			keyboard.FrameIndex, static_cast<int>(keyboard.Pressed.test(c_KeyA)), static_cast<int>(keyboard.Pressed.test(c_KeyD)));
   	}
   }
   ```

   ```text output-of="input-devices-state-pause.cpp"
   tick 1: game updates 1, input frame 1, A pressed 1, D pressed 0
   tick 2: game updates 1, input frame 2, A pressed 0, D pressed 0
   tick 3: game updates 0, input frame 2, A pressed 0, D pressed 1
   tick 4: game updates 0, input frame 2, A pressed 0, D pressed 1
   tick 5: game updates 1, input frame 3, A pressed 0, D pressed 1
   tick 6: game updates 1, input frame 4, A pressed 0, D pressed 0
   ```

   1. **Lines 27–38:** `BeginFrame` has the engine's two decisions: clear once the frame was seen, and stop before counting while suspended.
   2. **Line 46:** ticks 3 and 4 are the pause.
   :::

3. **Medium.** Trace it yourself. Put breakpoints in `Input::ProcessKey` and `Input::BeginFrame`, play the Third-Person sample in the editor and tap Space. Find the callback that calls `ProcessKey`, the edge that `ButtonStates::Set` records and the frame where the edge is cleared.

   :::answer[Worked solution]{tests="edges"}
   The first breakpoint stops in `Input::ProcessKey` (`Strata/src/Strata/Input/Input.cpp`), called from the key callback in `GLFWWindow.cpp`, inside `glfwPollEvents` in `GLFWWindow::ProcessEvents`. Stepping into `ButtonStates::Set` shows `Pressed.set(32)`. The release of the key stops there again with `Released.set(32)`. At the next `BeginFrame` that finds `FrameSeen` true, `ClearTransitions` resets both sets of bits, and the game's later calls of `IsKeyPressed` return false.
   :::

4. **Hard.** A second :term[window backend]{id=window-backend}, for a library that is not GLFW, must feed `Input`. List what it must translate and what it must call, and say which rules of this page it must obey.

   :::answer[Worked solution]{tests="codes,typed-text,edges"}
   The backend implements `InputWindow` (`GetWidth`, `GetHeight`, `SetCursorMode`) and hands itself to `Input::SetWindow`. It translates its own key and mouse button numbers to `KeyCode` and `MouseCode`, because the codes are ABI. It passes them to `Input::ProcessKey` and `Input::ProcessMouseButton` for presses and releases, never for repeats. It calls `Input::ProcessMouseMove`, `Input::ProcessScroll`, `Input::ProcessText` with whole code points (never halves of a UTF-16 pair) and `Input::ProcessGamepad` with the gamepad's state.

   The backend must also release held keys and buttons when its window loses focus, as GLFW does, and drop keys it cannot name. All of this runs on the main thread, inside the window's `ProcessEvents` after `Input::BeginFrame`, and lives in `Strata/src/Platform/`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Input/Input.h` and `Input.cpp`: `Input`, `ButtonStates`, the text functions and `BeginFrame`.
- `Strata/src/Strata/Input/KeyCodes.h`, `MouseCodes.h` and `InputNames.h`: codes, `CursorMode` and names.
- `Strata/src/Strata/Input/InputWindow.h`: the window seam.
- `Strata/src/Platform/GLFW/GLFWWindow.cpp`: the callbacks that feed `Input`.
- `Strata/src/Strata/Core/Application.cpp`: the Input stage of `Application::RunFrame`.
- `StrataScriptCore/Include/StrataScript/Input.h`: the SDK's `Input`.
- `StrataTests/src/Core/InputTests.cpp`: the suites `Core.Input` and `Core.InputNames`.

## Further reading

- The GLFW input guide (<https://www.glfw.org/>, beginner to intermediate): keys, characters, mouse buttons and how GLFW reports key repeat and focus loss.
- "Event Queue" in Game Programming Patterns (gameprogrammingpatterns.com, intermediate): the alternative that this page's table names.
- "About Raw Input" (learn.microsoft.com, advanced): the Windows interface for raw device data.
