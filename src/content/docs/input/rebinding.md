---
id: input/rebinding
title: "Players' bindings inside the engine: the bindings file and capture"
description: "How Strata keeps the controls a player rebinds, loads them in each session, and listens for the next press without that press doing anything else."
kind: internals
size: M
tracks: [E]
needs: [input/actions]
time: 55
learn:
  - id: where-stored
    text: name where a player's binding is stored, what the file holds and which function reads and writes it
  - id: when-applies
    text: explain when a saved binding applies, when a session resets it and what happens to a damaged file
  - id: capture-rules
    text: trace how a capture picks a control and why the captured press triggers no action
  - id: capture-owners
    text: explain how the capture number lets several owners share one listener
since: 0.6.0
status: final
---

A game lets its players change the controls: the player of a third-person game opens a menu, chooses Jump, presses a
gamepad button, and from then on that button jumps. The engine's part of this has three jobs. It keeps the replacements
the player made and restores them in the next session. It listens for "the next control the player presses". It makes
sure the press that was heard does nothing else.

The page does not teach the menu a game builds, the editor's **Input Actions** page, or where a shipped game's save folder is: those belong to other pages.

## The problem and how engines solve it

Start with the first half, the memory. The project defines actions and the controls that trigger them, and the
[actions page](../input/actions.md) shows how the engine compiles them. The project's set is the designer's choice. The
player's choice must live elsewhere, because the project's set ships inside the game and the game must not change its
own files. The player's choice therefore goes into a small file in a folder that belongs to the player's copy.

The listening half has three traps. First, the press that picks the new control is still a press. If the player
presses Space to bind it, Space must not also make the character jump, and a mouse click that picks a button must not
also click the button below it. Second, the player may open the rebinding menu while the game is paused, so the
listener cannot rely on frames of game input that do not advance. Third, two parts of the program may want the listener
at once: the editor's page and a game's menu.

Engines meet these in three common ways.

Some read the key inside the menu widget, so the widget swallows the event
itself. Some let each screen own a listener, which is simple until two exist. Some keep one listener with one result,
which needs a rule for who may take it. Strata keeps one listener inside the input system, reads the devices directly,
and gives each listening a number.

:::why
The cost is a shared state: every user of the listener must check that the listening is still its own. In return the
press never reaches the actions, whatever draws the menu.
:::

## The map

Two ideas need a picture. The first is how a player's replacement reaches the actions. The project's section holds the
designer's set. The bindings file holds the replacements. In each session the engine reads both and compiles them
into the one set that games query.

```mermaid caption="The project's set and the player's file meet in one compile step; saving writes the file, loading reads it." alt="The project's input section and the saved bindings file both feed the compile step that makes the set games read. Saving writes the file in the save folder; the editor's save folder lies in the project and a shipped game's in the user data folder."
flowchart LR
	P[Project section Input.Actions] --> C[Compile]
	F[InputBindings.json in the save folder] -->|LoadBindings| S[Players' bindings]
	S --> C
	C --> G[Set games query]
	U[SetBindings] --> S
	S -->|SaveBindings| F
	S -->|ResetBindings| S
	D[DeleteSavedBindings] --> F
```

The save folder depends on who runs the game. The editor keeps it inside the project, in `.strata/Saves`. A shipped
game keeps it in the :term[user data folder]{id=user-data-folder} of its player, under the game's name. Both come from the `IGameSaves` service,
which [the game identity page](../worlds/game-identity.md) teaches; the input code only asks it for the folder.

The second picture is the capture. A capture is in one of a few states, and the rules of the page are the arrows between
them.

```mermaid caption="A capture listens, then holds a result, then gives it away; the control stays silent for actions until the player lets go." alt="Idle moves to listening when a capture begins. Listening moves to captured when a control goes down, to idle when cancelled, and to listening again under a new number when another owner begins. Captured moves to taken when its owner takes the text, and taken moves back to idle. The control stays suppressed until it is released."
stateDiagram-v2
	[*] --> Idle
	Idle --> Listening: BeginCapture
	Listening --> Captured: a control goes down
	Listening --> Idle: CancelCapture
	Listening --> Listening: another owner begins (new number)
	Captured --> Taken: TakeCapturedBinding
	Captured --> Listening: another owner begins
	Taken --> Idle: result given
```

Read the diagram as two clocks. The capture itself ends when the first control goes down. The **suppression** of that
control, which keeps it silent for actions, ends later, when the player lets go.

## The contract

Callers may assume the rules below. Each has a reason, and the reasons are what you keep when you change the code.

:::rule
Only `InputActions` touches the players' bindings file. One owner keeps the size limit, the :term[header]{id=header} check and the
per-entry checks in one place; see [the actions page](../input/actions.md) for the set it applies them to.
:::

- **A capture's press triggers nothing.** While a capture listens, every action reads as up. After it ends, its control
  stays up for actions until the player releases it. Without this, binding Space would also make the character jump.
- **Another binding of the same action still works.** Suppression silences one control, not the action.
- **A capture runs while the game is paused.** It reads the devices' raw state, so frames of game input that do not
  advance do not stop it.
- **A listening belongs to one owner.** Each `BeginCapture` makes a new number. `InputActions` does not check who
  asks, so each owner takes the result or cancels only while its number is still the current one.
- **A bad file never stops a game.** A file that cannot be used is ignored with a warning, and the project's bindings
  apply.

:::why
The capture reads raw state, not the evaluated actions, because actions are the thing being changed. A capture that
asked "which action fired" could not bind a control that no action uses yet.
:::

**Players' bindings** are the lists of replacement controls the player chose, one list for each action, kept for the
session. An empty list is a choice too: it removes every control of the action. An action with no entry keeps the
project's controls.

## A toy version

:::question
New to C++ here? Read [the classes page](../basics/programming-3.md) and [the modern C++ page](../basics/cpp-modern.md) first.
:::

The toy models three keys and one action, Jump, bound to Space. It keeps the capture's three pieces of state: the keys
that were down when it began, the result, and the suppressed key. Search for how `Update` compares the raw state with the
remembered one, and how `IsJumpDown` stays false in two cases.

```cpp sketch="input-rebinding-toy.cpp"
#include <array>
#include <cstdio>
#include <optional>
#include <string>

namespace
{
	constexpr int c_KeyCount = 3;
	constexpr int c_Space = 0;
	const char* c_KeyNames[c_KeyCount] = { "Space", "Enter", "Escape" };

	struct Capture
	{
		bool Active = false;
		std::array<bool, c_KeyCount> Held = {}; // The keys that were down when the capture began, then at the last update
		std::optional<std::string> Result;
		int Suppressed = -1;                    // The captured key, until it is released
	};

	std::array<bool, c_KeyCount> s_Raw = {}; // What the keys do now, whatever the game thinks
	Capture s_Capture;

	void Begin()
	{
		s_Capture = Capture();
		s_Capture.Active = true;
		s_Capture.Held = s_Raw; // A key that is already down is not a new press
	}

	void Update()
	{
		if (s_Capture.Active)
		{
			for (int key = 0; key < c_KeyCount; key++)
			{
				const bool wentDown = s_Raw[key] && !s_Capture.Held[key];
				s_Capture.Held[key] = s_Raw[key];
				if (!wentDown)
					continue;
				s_Capture.Active = false;
				s_Capture.Result = c_KeyNames[key];
				s_Capture.Suppressed = key;
				return;
			}
		}
		if (s_Capture.Suppressed >= 0 && !s_Raw[s_Capture.Suppressed])
			s_Capture.Suppressed = -1;
	}

	// The action Jump, bound to Space: up while a capture listens and while its control is suppressed.
	bool IsJumpDown()
	{
		return !s_Capture.Active && s_Capture.Suppressed != c_Space && s_Raw[c_Space];
	}

	void Frame(int number, bool space, bool enter)
	{
		s_Raw[c_Space] = space;
		s_Raw[1] = enter;
		Update();
		std::printf("frame %d: result=%s jump=%d\n", number, s_Capture.Result ? s_Capture.Result->c_str() : "-", IsJumpDown() ? 1 : 0);
	}
}

int main()
{
	s_Raw[1] = true; // Enter is down: it started the capture
	Begin();
	Frame(1, false, true);
	Frame(2, true, false);
	Frame(3, true, false);
	Frame(4, false, false);
	Frame(5, true, false);
	return 0;
}
```

```text output-of="input-rebinding-toy.cpp"
frame 1: result=- jump=0
frame 2: result=Space jump=0
frame 3: result=Space jump=0
frame 4: result=Space jump=0
frame 5: result=Space jump=1
```

1. **Line 27:** the capture copies the raw state when it begins, so a key that is already down is not new.
2. **Lines 36–37:** a key counts when it is down now and was up before; every update remembers the state.
3. **Lines 40–43:** the first new key ends the capture, stores its name and marks the key suppressed.
4. **Lines 46–47:** the suppression ends when the key is up.
5. **Line 53:** Jump reads as up while a capture listens and while its key is suppressed.

The run follows one player. In frame 1 Enter is still down, because it clicked the "Rebind" button; the toy copied the
state at `Begin`, so Enter is not new and nothing happens. In frame 2 Space goes down and the capture ends with the
result Space, yet Jump reads as up. In frames 3 and 4 the capture is over but Space is suppressed, and frame 5
shows the first press that counts for the action.

## The real code

The real code differs from the toy in four ways: players' bindings are validated and saved, sessions reset them, the
raw state covers three devices, and owners share the listener. The sections follow the data.

### The players' bindings and their file

`SetBindings` replaces one action's list. It rejects an unknown action, more than eight controls, or a control the action's kind
cannot use, such as a stick for a button. Each failure returns false with a message and changes nothing. An empty list
is accepted and leaves the action with no controls. `ResetBindings` removes one entry, or all of them when the name is empty, and both
calls compile the set again.

`GetPlayerBindings` returns the replacements that apply now: an entry whose action no longer exists, or no longer fits
the kind, is omitted. `SaveBindings` writes exactly that. It goes through `FileSystem::WriteText`, which writes a
temporary file and renames it, so a crash leaves the old file or the new one; [the files page](../core/files.md) teaches
why. The file is a [JavaScript Object Notation](../basics/data-formats.md) (JSON) document with a :term[header]{id=header} that names its
format and its version.

The reader is the part to read slowly, because the file is outside the engine's control: the player, a copy from another
machine or a newer engine may have changed it.

```cpp src="Strata/src/Strata/Input/InputActionSet.cpp#L757-L773"
if (text.size() > c_MaxFileBytes)
	return fail(fmt::format("it is larger than {} bytes", c_MaxFileBytes));
std::string parseError;
const std::optional<nlohmann::json> document = JsonUtils::Parse(text, &parseError);
if (!document)
	return fail(fmt::format("it is not JSON ({})", parseError));
const nlohmann::json* header = JsonUtils::Find(*document, "Strata");
if (!header || !header->is_object() || JsonUtils::GetString(*header, "Format") != "InputBindings")
	return fail("it is no input bindings file (no Strata.Format \"InputBindings\")");
const nlohmann::json* version = JsonUtils::Find(*header, "Version");
if (!version || !version->is_number_unsigned() || version->get<uint64_t>() == 0)
	return fail("its Strata.Version is not a version");
if (version->get<uint64_t>() > c_FormatVersion)
	return fail(fmt::format("it was written by a later version of the engine (format {}; this one reads {})", version->get<uint64_t>(), c_FormatVersion));
const nlohmann::json* actions = JsonUtils::Find(*document, "Actions");
if (!actions || !actions->is_object())
	return fail("it has no Actions object");
```

1. **Line 757:** a file over the size limit fails before any parsing.
2. **Lines 763–765:** the header must name the format `InputBindings`.
3. **Lines 769–770:** a file from a later engine version is refused, never guessed at.
4. **Lines 771–773:** the document needs an `Actions` object; the entries come after.

Reading starts from the :term[bytes]{id=byte}. The engine reads at most 65,536 bytes plus one: a longer file fails the size test
without being loaded whole. After the header checks, each entry is judged alone. A name without a map, an unknown
action or a binding the action cannot use is dropped with a message. If dropping empties a list, the entry is skipped, so
the project's bindings apply; an empty list that was in the file stays, because that was the player's choice.

:::example
A player of the Third-Person game rebinds Jump from Space to the gamepad's A button. The game calls `SetBindings` with
the one control, then `SaveBindings`. The file in the save folder now holds this content, shown here compactly:

```json
{
	"Strata": { "Format": "InputBindings", "Version": 1 },
	"Actions": { "Gameplay/Jump": [ "Gamepad/A" ] }
}
```

The next session loads it, and Jump answers to A alone. Suppose the designer later renames Jump to Leap. The entry
`Gameplay/Jump` finds no action, so it is dropped with a warning that names the first dropped entry and the count, and
Leap keeps its project controls. The file itself stays on disk until the next save writes only what applies.
:::

`LoadBindings` is the read side.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L952-L969" symbol="InputActions::LoadBindings"
void InputActions::LoadBindings()
{
	Refresh();
	s_State.Players.Actions.clear();
	if (std::optional<BindingsFile> file = ReadBindingsFile())
	{
		if (file->Bindings)
			s_State.Players = std::move(*file->Bindings);
		else
			ST_CORE_WARN("The players' input bindings '{}' are ignored ({}): the project's bindings apply", file->Path, file->Error);
		if (!file->Dropped.empty())
		{
			ST_CORE_WARN("The players' input bindings '{}' name what the game's actions no longer have ({} dropped; the project's bindings apply "
				"there): {}", file->Path, file->Dropped.size(), file->Dropped.front());
		}
	}
	Compile(InputActionSet(s_State.Set), true);
}
```

1. **Line 955:** the replacements are cleared first, so a missing file leaves the project's bindings.
2. **Lines 958–961:** a usable file replaces them; a damaged one logs a warning and changes nothing.
3. **Lines 962–966:** entries the actions no longer have get their own warning, with a count.
4. **Line 968:** the set is compiled again, with whatever the file gave.

The warning for a whole ignored file and the warning for dropped entries are separate, so a log tells a damaged file from a
stale one. `ReadSavedBindings` runs the same reader but only returns the result, so the editor can learn what the file holds
without changing the session. `DeleteSavedBindings` removes the file and reports failure if
it is still there afterwards.

### Sessions

A **session** here means one run of the game: a play session in the editor, or one start of an exported game. At the
start of the session the engine calls `ResetSession`, which clears the replacements, any simulated input and any capture,
and refreshes the project's set. Then `LoadBindings` reads the saved file. The editor does this when play starts, and
`ResetSession` again when play stops, so a rebinding made in play never leaks into the editor's own use of the actions.
`GameRuntime` does the pair at start and `ResetSession` when the game ends.

The editor's **Input Actions** page shows the result: an "In play" marker beside each action the saved file replaces, and a
**Reset Player Bindings** button that deletes the file.

### Binding capture

**Binding capture** is the engine's one listener for the next control a player presses, and the editor and games share
it. The real `UpdateCapture` extends the toy to three devices.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L608-L634"
void UpdateCapture(bool begin)
{
	CaptureState& capture = s_State.Capture;
	if (!capture.Active)
		return;
	if (capture.Devices.Keyboard)
	{
		for (KeyCode key = 0; key < c_MaxKeyCode; key++)
		{
			const bool held = Input::IsRawKeyDown(key);
			const bool wentDown = held && !capture.Keys.test(key);
			capture.Keys.set(key, held);
			if (wentDown && !begin && InputNames::GetKeyName(key))
				return FinishCapture({ InputControlType::Key, key, 1 });
		}
	}
	if (capture.Devices.Mouse)
	{
		for (MouseCode button = 0; button < c_MaxMouseButtons; button++)
		{
			const bool held = Input::IsRawMouseButtonDown(button);
			const bool wentDown = held && !capture.MouseButtons.test(button);
			capture.MouseButtons.set(button, held);
			if (wentDown && !begin && InputNames::GetMouseButtonName(button))
				return FinishCapture({ InputControlType::MouseButton, button, 1 });
		}
	}
```

1. **Lines 611–612:** a capture that is not listening does nothing.
2. **Lines 617–619:** the raw state is compared with the held state, which is updated on every call.
3. **Lines 620–621:** only a call that is not the first, and a key that has a name, finishes the capture.
4. **Lines 624–634:** the mouse buttons follow the same pattern.

The loop is the toy's comparison, repeated for each device. Keys come first, then mouse buttons, then gamepad buttons,
then axes, each in code order, so when two controls go down in the same frame the earlier one wins. `begin` is true
only in the call that starts the capture: it records what is held without capturing, which is why the key that clicked
the button does not bind itself. A key without a name is skipped, because a binding needs text to be saved.

A :term[half axis]{id=half-axis}, one direction of a stick or a trigger, counts as pressed past 0.5 and stays pressed until it falls to
0.35, the same :term[hysteresis]{id=hysteresis} that actions use. A trigger has only its positive half. Whole axes and sticks cannot be
captured; only halves can.

`FinishCapture` stores the binding's text and marks the control suppressed. Suppression lasts until a frame that was
evaluated sees the control up.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L563-L593"
void UpdateSuppression()
{
	if (!s_State.Suppressed)
		return;
	const InputControl& control = *s_State.Suppressed;
	bool held = false;
	switch (control.Type)
	{
		case InputControlType::Key:
			held = Input::IsRawKeyDown(control.Code);
			break;
		case InputControlType::MouseButton:
			held = Input::IsRawMouseButtonDown(control.Code);
			break;
		case InputControlType::GamepadButton:
			for (uint32_t gamepad = 0; gamepad < c_MaxGamepads; gamepad++)
				held = held || Input::IsRawGamepadButtonDown(gamepad, static_cast<GamepadButton>(control.Code));
			break;
		case InputControlType::GamepadHalfAxis:
			for (uint32_t gamepad = 0; gamepad < c_MaxGamepads; gamepad++)
			{
				const float value = Input::GetRawGamepadAxis(gamepad, static_cast<GamepadAxis>(control.Code)) * static_cast<float>(control.Sign);
				held = held || value > InputActions::c_Release;
			}
			break;
		case InputControlType::GamepadAxis:
		case InputControlType::GamepadStick:
			break; // A capture takes no whole axes
	}
	if (!held)
		s_State.Suppressed.reset();
```

1. **Lines 565–566:** with nothing suppressed there is nothing to do.
2. **Lines 571–573:** a key is read from the raw state, not from the actions.
3. **Lines 578–580:** a gamepad button counts as held when any gamepad holds it.
4. **Lines 581–587:** a half axis is held until it falls to the release level, 0.35.
5. **Lines 592–593:** when the control is up, the suppression ends.

The wait for an evaluated frame matters while the game is paused. A press and release during a pause reach the game's
next :term[input frame]{id=input-frame} as transitions, and that frame must not report the captured press. So the release is counted only after
an evaluation went by without the control.

### Owners

`BeginCapture` returns false when no device is asked for. Otherwise it adds one to the capture number, clears the old
state and starts listening. `GetCaptureId` returns the number of the latest capture. An owner remembers the number it got,
and before it takes or cancels, it compares: a different number means another owner replaced its capture, and what it
would take is not its own.

A script follows the same rule.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L2963-L2991"
bool OwnsBindingCapture(const ScriptSystem& system)
{
	return system.GetBindingCapture() != 0 && system.GetBindingCapture() == InputActions::GetCaptureId();
}

bool HostInputBeginBindingCapture(StrataScriptContext* context, uint32_t devices)
{
	return HostCall("InputBeginBindingCapture", false, [&]()
	{
		ScriptSystem* system = ResolveContext(context, "InputBeginBindingCapture");
		if (!system)
			return false;
		constexpr uint32_t c_KnownDevices = StrataScriptInputDevices_Keyboard | StrataScriptInputDevices_Mouse | StrataScriptInputDevices_Gamepad;
		if (devices == 0 || (devices & ~c_KnownDevices) != 0)
		{
			system->ReportProblem("InputBeginBindingCapture", fmt::format("the devices {:#x} are not a combination of Keyboard (1), Mouse (2) and "
				"Gamepad (4)", devices));
			return false;
		}
		InputCaptureDevices captureDevices;
		captureDevices.Keyboard = (devices & StrataScriptInputDevices_Keyboard) != 0;
		captureDevices.Mouse = (devices & StrataScriptInputDevices_Mouse) != 0;
		captureDevices.Gamepad = (devices & StrataScriptInputDevices_Gamepad) != 0;
		if (!InputActions::BeginCapture(captureDevices))
			return false;
		system->SetBindingCapture(InputActions::GetCaptureId());
		return true;
	});
}
```

1. **Lines 2963–2966:** a script owns the capture only while its remembered number is the current one.
2. **Lines 2976–2981:** the devices must be a combination of the three known ones.
3. **Lines 2986–2988:** the script begins the capture, then remembers its number.

The scripting system remembers the number of the capture a script started, and the poll and cancel host functions act
only while that number is still the current one. The editor's `BindingCapture` does the same, and adds a time limit and
an "abandoned" check for an owner that stops drawing.

`TakeCapturedBinding` hands out the text once and clears it. `GetCapturedControl` reports the control that is
suppressed, for code that needs to know which one.

### Key names

Strata names keys by their position on an American keyboard. A player with a French keyboard who captures the key printed A sees the
text of the key in that position, Q. Only the editor's shortcuts follow the layout, through `Window::GetLayoutKey`; a
game shows the position name. Engines that want printed labels ask the :term[operating system]{id=operating-system} for a key's label, which the
engine has not done for games.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One capture for each owner | Engines with per-screen input handlers | No check of the number; two screens listen at once | Two listeners could bind the same press twice; the actions would need a mask for each |
| Capture inside the menu widget | Many interface libraries | No shared state | A paused game or a second widget would need its own copy of the rules |
| Reading the evaluated actions | Simple engines | Less code | A control no action uses could not be captured |
| Printed key labels | Operating system calls for keys | Names the player reads | Bindings that differ from machine to machine |

## How it is tested

The capture tests live in `StrataTests/src/Core/InputActionsTests.cpp`. `A capture returns the first control and no action sees it`
covers the first rule.

`Every capture has its own number, and its binding reads before it is taken` covers owners.
`The captured control stays up for actions until it is released` presses, takes, and watches Jump for three frames,
then checks the other bindings and the half axis threshold. `A capture runs while input frames are suspended` covers pause.
Run them with `build/windows/bin/Debug/StrataTests.exe --test-case="*capture*"`, a doctest filter.

## Changing it safely

- Keep the file reader forgiving per entry and strict on the header. A new field needs a new `Version`; the reader
  refuses a later version so an old engine never reads a new file wrongly.
- Never read or write the bindings file outside `InputActions`: it is the one place that knows the set.
- A new device for capture goes into `UpdateCapture`, `CaptureState` and `UpdateSuppression` together.
- Add a test that fails without the change, then run the `Core*` suites.

## Summary

- A player's bindings live in `InputBindings.json` in the save folder, written atomically through `SaveBindings` and read through `LoadBindings`.
- A session resets the replacements, then loads the file; a damaged or stale file is ignored per entry with a warning.
- A capture picks the first control that goes down in the raw state, in device order, and its control stays silent for actions until released.
- The capture number lets several owners share one listener: each takes or cancels only its own.

## Check yourself

1. Where does a shipped game keep a player's binding?

   - A. In the project's `.strata` folder.
   - B. In the game's save folder in the user data folder, as `InputBindings.json`.
   - C. Inside the manifest.

   :::answer{tests="where-stored"}
   B. The editor uses the project's `.strata/Saves` (A is only the editor's place), and the manifest holds the designer's set, not the player's choice (C).
   :::

2. The designer deletes the action Leap that a player rebound last week. What happens at the next start?

   :::answer{tests="when-applies"}
   The entry is dropped with a warning, the other entries still apply, and the file stays until the next save.
   :::

3. In the toy, Space is released in frame 4 and pressed again in frame 5. In which frame does Jump first read as down?

   :::answer{tests="capture-rules"}
   Frame 5. Frame 4 has the key up, and the press of frame 2 was swallowed by suppression.
   :::

4. A menu begins a capture while the editor's page listens. The page then cancels with its old number. What does the capture do?

   :::answer{tests="capture-owners"}
   The capture keeps listening for the menu. The page compares its old number with `GetCaptureId`, sees a newer one,
   and does not call `CancelCapture`.
   :::

## Exercises

1. **Basic.** Run the owners sketch below in your head, then check its output.

   :::answer[Worked solution]{tests="capture-owners" solution="sketches/input-rebinding-owners.cpp"}
   The page begins first and gets 1; the menu begins second and gets 2. The page's cancel fails, and the capture is still
   listening. The menu's cancel works, and the capture stops.

   ```cpp sketch="input-rebinding-owners.cpp"
   #include <cstdint>
   #include <cstdio>

   namespace
   {
   	struct Capture
   	{
   		bool Active = false;
   		uint64_t Id = 0; // The number of the last Begin: it never goes back
   	};

   	Capture s_Capture;

   	uint64_t Begin()
   	{
   		s_Capture.Id++;
   		s_Capture.Active = true;
   		return s_Capture.Id;
   	}

   	// An owner cancels only the capture it began: its number must still be the current one.
   	bool CancelIfOwned(uint64_t owned)
   	{
   		if (owned != s_Capture.Id)
   			return false;
   		s_Capture.Active = false;
   		return true;
   	}
   }

   int main()
   {
   	const uint64_t page = Begin();
   	const uint64_t menu = Begin();
   	std::printf("page owns %llu, menu owns %llu\n", static_cast<unsigned long long>(page), static_cast<unsigned long long>(menu));
   	// Each cancel runs before its printf reads the state: the order of a call's arguments is not fixed.
   	const bool pageCancelled = CancelIfOwned(page);
   	std::printf("page cancels: %d, still listening: %d\n", pageCancelled ? 1 : 0, s_Capture.Active ? 1 : 0);
   	const bool menuCancelled = CancelIfOwned(menu);
   	std::printf("menu cancels: %d, still listening: %d\n", menuCancelled ? 1 : 0, s_Capture.Active ? 1 : 0);
   	return 0;
   }
   ```

   ```text output-of="input-rebinding-owners.cpp"
   page owns 1, menu owns 2
   page cancels: 0, still listening: 1
   menu cancels: 1, still listening: 0
   ```

   1. **Line 16:** every capture that begins raises the number.
   2. **Lines 24–25:** an owner may cancel only while its number is still the current one.
   3. **Lines 33–34:** two owners begin one after the other, and the page loses the capture.
   :::

2. **Medium.** Trace it yourself: find where a play session in the editor saves the bindings file.

   :::answer[Worked solution]{tests="where-stored"}
   Search for `GetBindingsFile` in `Strata/src/Strata/Input/InputActions.cpp`. The function asks `IGameSaves` for the save folder
   and joins the file name `InputBindings.json`. The editor's service answers with `.strata/Saves` of the project.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Input/InputActions.cpp`: the bindings, the file, sessions and the capture.
- `Strata/src/Strata/Input/InputActionSet.cpp`: the file's header and reader.
- `StrataEditor/src/UI/BindingCapture.cpp`: the editor's owner of the capture.
- `StrataTests/src/Core/InputActionsTests.cpp`: the capture tests.

## Further reading

- Robert Nystrom, Game Programming Patterns, the chapter on the Command pattern: how input becomes commands that a player can rebind (intermediate).
