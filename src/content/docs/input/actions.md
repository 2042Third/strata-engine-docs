---
id: input/actions
title: "Input actions"
description: "How Strata defines input actions, compiles them into flat arrays, evaluates them each input frame and offers them to scripts, menus and the editor."
kind: internals
size: XL
tracks: [E]
needs: [input/mouse-cursor, input/gamepads, world/projects-settings]
time: 110
learn:
  - id: write-bindings
    text: write bindings in the grammar for an action of each kind and name the ones Strata refuses
  - id: predict-states
    text: predict an action's Down, Pressed and Released in each frame of a press, a map disable and a live edit
  - id: compiled-arrays
    text: explain why evaluation runs on compiled arrays and how a live edit keeps the state of unchanged actions
  - id: compute-repeat
    text: compute the updates at which a held menu key repeats
  - id: script-access
    text: name the script functions and editor commands through which a game and an agent reach input actions
since: 0.6.0
status: final
---

A game rarely wants to know that the player pressed the key called Space. It wants to know that the player asked to jump. An **input action** is that request, a named control that the project defines and that the game reads each frame. It is a Button that is up or down, an Axis from -1 to 1, or a Vector2 with two values.

The project's definition is the value `InputActionSet`, stored in the :term[settings section]{id=settings-section-world} `Input.Actions`. `InputActions` evaluates it once per :term[input frame]{id=input-frame} from four sources: the devices, the players' own bindings, the map enables and any simulated holds. The players' bindings are the lists that a player chose in the game's rebinding menu, and they replace the project's. The game's menus read six of the actions through `UIActionState`.

This page follows the data from the project file to the answer of `IsDown`. Other pages teach why games use actions, the players' bindings file, the simulated device and the menus' navigation.

## The problem and how engines solve it

A game that asks "is Space down?" ties its rules to one keyboard, and a player with another layout, a gamepad or a hand that cannot reach Space is stuck. [How input works](how-input-works.md) names the cure that Unity, Unreal and Strata share: the game asks about intents, and a table maps intents to controls. Strata's table is data in the project, so the editor, scripts, tests and players all change one thing, and the evaluation has to be cheap, because it runs for every action in every input frame.

## The map

Two pictures give the page's vocabulary. The first is the model that the project file holds. A set has maps, a map has actions, and an action has bindings. Each binding reads one control or two or four controls combined.

```mermaid caption="The model of a project's input actions: a set holds at most 32 maps, a map holds actions, and an action holds at most 8 bindings that each read one, two or four controls." alt="A class diagram. The input action set holds maps. A map holds actions. An action holds bindings with a kind and a dead zone. A binding holds one to four controls."
classDiagram
	InputActionSet "1" *-- "1..32" InputActionMap : Maps
	InputActionMap "1" *-- "0..*" InputAction : Actions
	InputAction "1" *-- "0..8" InputBinding : Bindings
	InputBinding "1" *-- "1, 2 or 4" InputControl : Controls
	class InputActionSet {
		FindAction(name)
		MakeSection()
	}
	class InputActionMap {
		Name
		Enabled
	}
	class InputAction {
		Name
		Kind
		DeadZone
	}
	class InputBinding {
		Shape
		Parse(text)
		FitsKind(kind)
	}
	class InputControl {
		Type
		Code
		Sign
	}
```

The second picture is the compiled form, which `InputActions` builds from the model and the players' bindings. Everything is a flat array, and an index replaces every pointer. An action record names the range of its bindings, a compiled binding names the range of its controls, and a parallel array holds one :term[hysteresis]{id=hysteresis} flag per control and per gamepad.

```mermaid caption="The compiled form: each array points into the next by the index of its first element and a count, and the names table finds a record from a lower-case name." alt="A flow diagram. A names table leads to the action records. Each record points to a range of compiled bindings. Each compiled binding points to a range of controls. A parallel array of half axis flags has one entry per control."
flowchart LR
	Names["Names: lower-case text to record index"] --> Records["ActionRecord[]: state, kind, dead zone, first binding, count"]
	Records --> Bindings["CompiledBinding[]: shape, first control"]
	Bindings --> Controls["InputControl[]: type, code, sign"]
	Controls -.same index.- Held["HalfAxisHeld[]: one flag per gamepad"]
```

All of this runs on the :term[main thread]{id=main-thread}, like `Input`. The engine's `Application` calls `InputActions::Update` in its Input stage, after the window's events are in. Code that runs a game in the same process calls it after `Input::BeginFrame`. The files are `InputActionSet.h` and `InputActionSet.cpp` (the model, the grammar, the :term[parser]{id=parser} and the section), `InputActions.h` and `InputActions.cpp` (the compiled form and the evaluation) and `UIActions.h` and `UIActions.cpp` (the menus' view), all under `Strata/src/Strata/Input/`.

## The contract

Callers may assume that an action's state is that of the current input frame, that a name is found by its text and that the same text always finds the same action. They must follow three rules, each with a reason.

:::rule[Gameplay reads controls that players can rebind as input actions]
`AGENTS.md` says that gameplay and menus read the controls that players can rebind as input actions, and that the players' bindings travel only through `InputActions`. The reason is the player: a key that a script reads directly cannot be rebound. Read a device directly only for what nobody rebinds: mouse look, :term[typed text]{id=typed-text} and debug keys.
:::

The second rule concerns a map that is disabled while one of its actions is held. The action is released once, in the next input frame, and then reads as up. A script that waits for a release, such as a charge that fires when a button lets go, is never left waiting.

The third rule concerns a live edit. When the project's actions change while a game runs, the state of every action that keeps its name and kind carries over. A held Jump is not pressed again, and a stick that rests between the two thresholds keeps its hold. The reason is the editor: a designer who changes the :term[dead zone]{id=dead-zone} of Look in the middle of a test must not trigger every held action.

:::example[A live edit while Jump is held]
Space is held, so `Gameplay/Jump` is down. In frame 10 a designer adds `Key/J` to its bindings with `inputActions.setAction`. `Compile` finds the key `gameplay/jump`, sees a Button on both sides and copies the state, so frame 11 reports Down and no Pressed. Suppose the designer had made Jump an Axis instead. The kinds differ, so the state starts empty, the action is evaluated from its bindings, and frame 11 reports Pressed again while Space is down.
:::

## The model

A **qualified name** is an action's full name, `<Map>/<Action>`, such as `Gameplay/Jump`.

A **bare name** is the action's name alone, accepted where no other map has an action of that name. A name has 1 to 64 characters: the letters A to Z, digits, spaces, `_`, `-` and `.`, with no space at either end. Names compare without regard to case. A bare name that two maps share is refused with a message that names every match.

:::example[Left in two maps]
Suppose a game defines `Gameplay/Left` for a side-scroller. The reserved map `UI` already has `UI/Left`, so the text `Left` matches two actions. `FindAction("Left")` fails with `'Left' is ambiguous: Gameplay/Left, UI/Left`, the matches sorted without regard to case. The text `Gameplay/Left` finds the first and `UI/Left` the second. A script that wrote `Left` is reported once and reads the action as up.
:::

An **action map** is a named group of input actions that is enabled or disabled as a whole: gameplay, a vehicle, a build mode. A map's field `Enabled` says whether its actions work when the game starts. Scripts enable and disable maps while the game runs.

Each action has a kind, from `InputActionKind`. A Button is down or up. An Axis holds one value from -1 to 1. A Vector2 holds two values, with +X right and +Y up, at most 1 long.

An Axis or a Vector2 has a dead zone, 0.15 by default and at most 0.9 (the constant `c_MaxDeadZone`). Values within it read 0, and the rest is scaled to reach 1. The set holds at most 32 maps and 256 actions, the six of the `UI` map included. An action holds at most 8 bindings.

The Third-Person sample shows a real set. Its `Gameplay` map has eight actions. The drawing shows them on the **Input Actions** page of the Project Settings window, which lists the maps and the actions of the map you select.

::figure{id=input-actions-gameplay}

| Action | Kind | Bindings |
| --- | --- | --- |
| `Move` | Vector2 | `2D:Key/W,Key/S,Key/A,Key/D`, `2D:Key/Up,Key/Down,Key/Left,Key/Right`, `Gamepad/LeftStick` |
| `Look` | Vector2 | `Gamepad/RightStick` |
| `Jump` | Button | `Key/Space`, `Gamepad/A` |
| `Run` | Button | `Key/LeftShift`, `Key/RightShift`, `Gamepad/RightBumper` |
| `Wave` | Button | `Key/D1`, `Gamepad/X` |
| `Dance` | Button | `Key/D2`, `Gamepad/Y` |
| `Respawn` | Button | `Key/R` |
| `Pause` | Button | `Key/Escape`, `Gamepad/Start` |

The mouse looks around through the raw device calls, because mouse motion is no action source. The rest of the sample reads these eight actions by name, and the project's `UI` map, next to them, steers the menus.

## The binding grammar

A **binding** is the text that ties an action to controls, such as `Key/Space`. The project file, the editor's commands, scripts and the players' bindings file all use the same text, so one parser serves them all. This table is the grammar. Prefixes and names ignore case when read; Strata writes them back as shown.

| Text | Control read | Reads |
| --- | --- | --- |
| `Key/<key>` | one key | down or up |
| `Mouse/<button>` | one mouse button | down or up |
| `Gamepad/<button>` | one gamepad button, on any gamepad | down or up |
| `Gamepad/<axis>` | the whole axis, such as `Gamepad/LeftX` | -1 to 1 |
| `Gamepad/<axis>+` or `Gamepad/<axis>-` | half an axis; a trigger has only `+` | 0 to 1 |
| `Gamepad/LeftStick`, `Gamepad/RightStick` | both axes of a stick | a vector, +Y up |
| `1D:<negative>,<positive>` | two button-like controls | -1, 0 or 1 |
| `2D:<up>,<down>,<left>,<right>` | four button-like controls | a vector |

A **composite** is a binding that builds one value from several button-like controls: `1D:` makes an axis from two of them, and `2D:` makes a vector from four. A control is button-like when it is a key, a mouse button, a gamepad button or a :term[half axis]{id=half-axis}. The whole axes and the sticks are not, because they already carry values.

The type in `InputActionSet.h` is small. A binding has a shape and an array of four controls, and the shape says how many of them count.

```cpp src="Strata/src/Strata/Input/InputActionSet.h#L71-L95"
struct InputBinding
{
	enum class Shape : uint8_t
	{
		Control = 0,
		Composite1D,
		Composite2D
	};

	// The longest valid text is 90 bytes (a 2D composite of four Gamepad/RightTrigger+).
	static constexpr size_t c_MaxTextBytes = 96;

	Shape Type = Shape::Control;
	// Control: [0]; Composite1D: negative, positive; Composite2D: up, down, left, right.
	std::array<InputControl, 4> Controls = {};

	static std::optional<InputBinding> Parse(std::string_view text, std::string* outError = nullptr);
	std::string ToString() const;

	uint32_t GetControlCount() const { return Type == Shape::Control ? 1 : (Type == Shape::Composite1D ? 2 : 4); }
	// Button takes button-like controls; Axis those, whole axes and 1D composites; Vector2 sticks and 2D composites.
	bool FitsKind(InputActionKind kind) const;

	bool operator==(const InputBinding&) const = default;
};
```

1. **Lines 73–78:** the shape says how many of the four control slots count: one, two or four.
2. **Line 81:** the longest text a binding may have; a longer text is refused before it is read.
3. **Lines 83–85:** a binding is a shape and four control slots, a fixed array that needs no allocation.
4. **Line 92:** `FitsKind` holds the rule of which kind takes which binding.

The next paragraph is the rule of which kind takes which binding. Strata calls it fitting, and `FitsKind` answers it.

```cpp src="Strata/src/Strata/Input/InputActionSet.cpp#L488-L501" symbol="InputBinding::FitsKind"
bool InputBinding::FitsKind(InputActionKind kind) const
{
	const InputControl& control = Controls[0];
	switch (kind)
	{
		case InputActionKind::Button:
			return Type == Shape::Control && control.IsButtonLike();
		case InputActionKind::Axis:
			return Type == Shape::Composite1D || (Type == Shape::Control && (control.IsButtonLike() || control.Type == InputControlType::GamepadAxis));
		case InputActionKind::Vector2:
			return Type == Shape::Composite2D || (Type == Shape::Control && control.Type == InputControlType::GamepadStick);
	}
	return false;
}
```

1. **Line 494:** a Button takes a single button-like control.
2. **Line 496:** an Axis adds the 1D composite and the whole axis.
3. **Line 498:** a Vector2 takes a 2D composite or a stick.
4. **Line 500:** an unknown kind fits nothing.

A Button takes one button-like control and nothing else. An Axis takes a button-like control (1 while down), a whole axis or a `1D:` composite. A Vector2 takes a stick or a `2D:` composite. So `Key/W` fits a Button and an Axis; `Gamepad/LeftX` fits only an Axis; `Gamepad/LeftStick` fits only a Vector2.

Strata checks the fit in four places: when it reads the project, when a command sets bindings, when a script sets the players' bindings and when it reads the players' file. A binding that does not fit refuses the whole list, and nothing changes.

## The parser

`InputBinding::Parse` reads the text by hand, in a few steps. It rejects an empty text and one longer than `c_MaxTextBytes`, which is 96: the longest valid text is 90 :term[bytes]{id=byte}, a 2D composite of four `Gamepad/RightTrigger+`. It tests the prefix `1D:` or `2D:`, case aside. Without one, it reads a single control. With one, it splits the rest at commas, expects exactly the right number of parts and reads each part as a control that must be button-like.

A hand-written parser suits a grammar this small, because every failure has its own message, and the messages reach the person who typed the text. In the quoted part, look at how the loop finds each part and what it refuses.

```cpp src="Strata/src/Strata/Input/InputActionSet.cpp#L446-L469" from="binding.Type = composite1D ?" to="parts = parts.substr(comma + 1);" symbol="InputBinding::Parse"
binding.Type = composite1D ? Shape::Composite1D : Shape::Composite2D;
const uint32_t count = binding.GetControlCount();
std::string_view parts = text.substr(c_Composite1DPrefix.size());
for (uint32_t index = 0; index < count; index++)
{
	const size_t comma = parts.find(',');
	const bool last = index + 1 == count;
	if (last != (comma == std::string_view::npos))
	{
		error = composite1D ? "a 1D composite has two parts: 1D:<negative>,<positive>" : "a 2D composite has four parts: 2D:<up>,<down>,<left>,<right>";
		return fail();
	}
	const std::string_view part = last ? parts : parts.substr(0, comma);
	const std::optional<InputControl> control = ParseControl(part, error);
	if (!control)
		return fail();
	if (!control->IsButtonLike())
	{
		error = fmt::format("'{}' cannot be part of a composite: parts are keys, mouse buttons, gamepad buttons or half axes", part);
		return fail();
	}
	binding.Controls[index] = *control;
	if (!last)
		parts = parts.substr(comma + 1);
```

1. **Lines 446–448:** the prefix chose the shape; the rest of the text is the list of parts.
2. **Lines 451–457:** every part but the last needs a comma after it and the last needs none; one test fails on a missing and on an extra comma.
3. **Lines 458–461:** each part is read by the function that reads a single control.
4. **Lines 462–466:** a whole axis or a stick is refused as a part, with a message that names the part.

The loop reads one part per round. The test `last != (comma == npos)` fails when a text has a comma too many or too few, and one test serves both cases. These are the messages a person meets, written as the code gives them.

| Text | Message |
| --- | --- |
| an empty text | `a binding is empty` |
| `Pad/A` | `'Pad/A' is no control: bindings start with Key/, Mouse/, Gamepad/, 1D: or 2D:` |
| `1D:Key/A` | `a 1D composite has two parts: 1D:<negative>,<positive>` |
| `2D:Key/W,Key/S` | `a 2D composite has four parts: 2D:<up>,<down>,<left>,<right>` |
| `1D:Gamepad/LeftX,Key/D` | `'Gamepad/LeftX' cannot be part of a composite: parts are keys, mouse buttons, gamepad buttons or half axes` |
| `Gamepad/LeftTrigger-` | `'LeftTrigger' has no - half: a trigger goes from 0 to 1 (use LeftTrigger+)` |

## The reserved UI map

Every set has one reserved map named `UI`, with six Buttons that the menus of the game's user interface (UI) read: `UI/Submit`, `UI/Cancel`, `UI/Up`, `UI/Down`, `UI/Left` and `UI/Right`. The **UI map**, also called the UI actions, is that map. Its bindings can change, in the project or by a player, but not its names, its kinds or the map itself. The code gives these default bindings.

| Action | Default bindings |
| --- | --- |
| `Submit` | `Key/Enter`, `Key/KPEnter`, `Key/Space`, `Gamepad/A` |
| `Cancel` | `Key/Escape`, `Gamepad/B` |
| `Up` | `Key/Up`, `Gamepad/DPadUp`, `Gamepad/LeftY+` |
| `Down` | `Key/Down`, `Gamepad/DPadDown`, `Gamepad/LeftY-` |
| `Left` | `Key/Left`, `Gamepad/DPadLeft`, `Gamepad/LeftX-` |
| `Right` | `Key/Right`, `Gamepad/DPadRight`, `Gamepad/LeftX+` |

The comment above `UIAction` in `UIActions.h` lists Enter, Escape, the arrows, A, B, the d-pad and the left stick. The code also binds `Key/KPEnter` and Space to `Submit`, so the table above is the one to trust.

The stick bindings are half axes, not sticks, and the difference matters. A Button reads a half axis with the same hysteresis as every button action: down above 0.5, held until the value falls to 0.35 or below. The `UI` map therefore has no values of its own. A menu that a player steers with the left stick moves one step when the stick passes 0.5 and moves again only after it came back to 0.35 or below.

If a project defines no actions, or omits the `UI` map, Strata adds the map with these defaults when it reads the set. A project that defines the map keeps its bindings. A set that has 32 maps already, or 256 actions, has no room for the map and is refused with a message that says so.

## The section

The settings section `Input.Actions` holds the set. `InputActionSet::MakeSection` builds its description: the id, the title **Input Actions**, the category `Input`, a JSON Schema, a default value and a reader. The schema bounds every member: names at most 64 characters, dead zones from 0 to 0.9, at most 8 bindings of at most 96 bytes, at most 32 maps. It lets a member of an unknown name fail, as `additionalProperties` set to false does.

The reader is `FromJson` followed by `ToJson`. `FromJson` checks the whole value: names, limits, kinds, bindings that fit their kind, dead zones and unknown members, with a message for each failure. Then it adds the `UI` map where it is missing. `ToJson` writes the value back in one canonical form, so a file that a person edited by hand comes out the same as one that a command wrote.

A project reads and writes the section through `IProjectSettings`, as [Project settings](../world/projects-settings.md) describes for every section. `RegisterInputModule` registers it.

A set that fails to read is not fatal at run time. `InputActions` logs the reason and uses the default set, the `UI` map alone, so a game with a broken section still has working menus.

## A toy version

The toy evaluates one Button, `Jump`, and one Vector2, `Move`, from a list of bindings. Five frames of fake devices play: nothing, Space, W, W with D, and a left stick pushed to (0.3, 0.4). The toy has the three jobs of the engine in small form: read each binding, combine them, then derive Pressed and Released from the previous frame. It omits the compiled arrays, the hysteresis, the map enables and the gamepads' counting. Read `Evaluate`, then the output.

```cpp sketch="input-actions-toy.cpp"
// A toy of input actions: one Button and one Vector2, evaluated once per frame from a list of bindings.
#include <glm/glm.hpp>

#include <array>
#include <cstdio>
#include <vector>

enum class Key
{
	Space = 0,
	W,
	S,
	A,
	D
};

struct Devices
{
	std::array<bool, 5> Keys = {};
	glm::vec2 LeftStick = glm::vec2(0.0f);
};

enum class Shape
{
	Key,
	Composite2D,
	Stick
};

// Key: Keys[0]. Composite2D: up, down, left, right. Stick: the left stick.
struct Binding
{
	Shape Type = Shape::Key;
	std::array<Key, 4> Keys = {};
};

struct Action
{
	bool IsVector = false;
	float DeadZone = 0.15f;
	std::vector<Binding> Bindings;
	bool Down = false;
	bool Pressed = false;
	bool Released = false;
	glm::vec2 Value = glm::vec2(0.0f);
};

static float Read(const Devices& devices, Key key)
{
	return devices.Keys[static_cast<size_t>(key)] ? 1.0f : 0.0f;
}

static glm::vec2 ReadBinding(const Binding& binding, const Devices& devices)
{
	if (binding.Type == Shape::Stick)
		return devices.LeftStick;
	if (binding.Type == Shape::Key)
		return glm::vec2(Read(devices, binding.Keys[0]), 0.0f);
	glm::vec2 vector(Read(devices, binding.Keys[3]) - Read(devices, binding.Keys[2]), Read(devices, binding.Keys[0]) - Read(devices, binding.Keys[1]));
	const float length = glm::length(vector);
	return length > 1.0f ? vector / length : vector;
}

static glm::vec2 ApplyDeadZone(const glm::vec2& value, float deadZone)
{
	const float length = glm::length(value);
	if (!(length > deadZone))
		return glm::vec2(0.0f);
	return value / length * ((length - deadZone) / (1.0f - deadZone));
}

static void Evaluate(Action& action, const Devices& devices)
{
	const bool wasDown = action.Down;
	glm::vec2 value(0.0f);
	for (const Binding& binding : action.Bindings)
	{
		const glm::vec2 read = ReadBinding(binding, devices);
		if (glm::dot(read, read) > glm::dot(value, value))
			value = read;
	}
	if (action.IsVector)
	{
		value = ApplyDeadZone(value, action.DeadZone);
		action.Down = glm::length(value) > 0.5f;
	}
	else
	{
		action.Down = value.x > 0.0f;
		value = glm::vec2(action.Down ? 1.0f : 0.0f, 0.0f);
	}
	action.Pressed = action.Down && !wasDown;
	action.Released = !action.Down && wasDown;
	action.Value = value;
}

int main()
{
	Action jump;
	jump.Bindings.push_back({ Shape::Key, { Key::Space } });
	Action move;
	move.IsVector = true;
	move.Bindings.push_back({ Shape::Composite2D, { Key::W, Key::S, Key::A, Key::D } });
	move.Bindings.push_back({ Shape::Stick, {} });

	Devices frames[5];
	frames[1].Keys[static_cast<size_t>(Key::Space)] = true;
	frames[2].Keys[static_cast<size_t>(Key::W)] = true;
	frames[3].Keys[static_cast<size_t>(Key::W)] = true;
	frames[3].Keys[static_cast<size_t>(Key::D)] = true;
	frames[4].LeftStick = glm::vec2(0.3f, 0.4f);
	for (int frame = 0; frame < 5; frame++)
	{
		Evaluate(jump, frames[frame]);
		Evaluate(move, frames[frame]);
		std::printf("frame %d: Jump down=%d pressed=%d released=%d | Move (%.2f, %.2f) down=%d\n", frame, jump.Down, jump.Pressed, jump.Released,
			move.Value.x, move.Value.y, move.Down);
	}
	return 0;
}
```

```text output-of="input-actions-toy.cpp"
frame 0: Jump down=0 pressed=0 released=0 | Move (0.00, 0.00) down=0
frame 1: Jump down=1 pressed=1 released=0 | Move (0.00, 0.00) down=0
frame 2: Jump down=0 pressed=0 released=1 | Move (0.00, 1.00) down=1
frame 3: Jump down=0 pressed=0 released=0 | Move (0.71, 0.71) down=1
frame 4: Jump down=0 pressed=0 released=0 | Move (0.25, 0.33) down=0
```

1. **Lines 53–62:** one binding read: a key gives 1 or 0, a stick gives its vector, and a composite gives a vector that is divided by its length when that is above 1.
2. **Lines 64–70:** the dead zone scales the length and keeps the direction.
3. **Lines 76–81:** the binding with the longest vector wins.
4. **Lines 82–91:** a vector is down above 0.5 and a Button when its value is above 0; the toy has no hysteresis.
5. **Lines 92–94:** Pressed and Released come from the previous Down.

The output shows each rule at work. In frame 1, `Jump` is down and pressed. In frame 2 the player lets go of Space, so `Jump` reports Released once. Meanwhile W alone gives the vector (0, 1) of length 1, which passes the dead zone unchanged, so `Move` is down.

Frame 3 holds W and D. The raw vector (1, 1) is 1.41 long, and the composite divides it by its length, so the diagonal has length 1, like a full stick: (0.71, 0.71). In frame 4 the stick's (0.3, 0.4) is 0.5 long. The dead zone leaves (0.5 − 0.15) ÷ 0.85 = 0.41 of that length, so `Move` is (0.25, 0.33). Its value is not zero, but it is below the press threshold of 0.5, so its Down is false.

## The real code

The real code differs from the toy in four ways. It compiles the set once, so evaluation touches arrays and no strings. It carries state across a rebuild. It applies hysteresis, so a stick near a threshold does not flicker. And it counts four gamepads, not one stick.

### Compiling the set

`Compile` runs when the set changes or the players' bindings change. It makes a table of the old records by key, then walks the new set map by map and writes the new arrays. The key is the lower-case qualified name: the one thing that stays the same when an edit moves, adds or removes actions around it.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L154-L186" from="record.Key = StringUtils::ToLower(s_State.Set.GetQualifiedName({ map, index }));" to="moved[found->second] = static_cast<int32_t>(s_State.Actions.size());" symbol="Compile"
record.Key = StringUtils::ToLower(s_State.Set.GetQualifiedName({ map, index }));
record.Map = map;
record.Kind = action.Kind;
record.DeadZone = action.DeadZone;
record.FirstBinding = static_cast<uint32_t>(s_State.Bindings.size());

// The players' list replaces the project's when every binding still fits the action (its kind may have changed).
const std::vector<InputBinding>* bindings = &action.Bindings;
if (const auto player = players.find(record.Key); player != players.end())
{
	const bool fits = std::all_of(player->second->begin(), player->second->end(),
		[&action](const InputBinding& binding) { return binding.FitsKind(action.Kind); });
	if (fits)
		bindings = player->second;
}
for (const InputBinding& binding : *bindings)
{
	s_State.Bindings.push_back({ binding.Type, static_cast<uint32_t>(s_State.Controls.size()) });
	for (uint32_t control = 0; control < binding.GetControlCount(); control++)
		s_State.Controls.push_back(binding.Controls[control]);
}
record.BindingCount = static_cast<uint32_t>(s_State.Bindings.size()) - record.FirstBinding;

if (const auto found = previousIndex.find(record.Key); found != previousIndex.end())
{
	const ActionRecord& old = previous[found->second];
	if (old.Kind == record.Kind)
	{
		record.State = old.State;
		record.ValueHeld = old.ValueHeld;
		record.SimulatedDown = old.SimulatedDown;
		record.SimulatedValue = old.SimulatedValue;
		moved[found->second] = static_cast<int32_t>(s_State.Actions.size());
```

1. **Line 154:** the key is the lower-case qualified name, the one thing that identifies an action across edits.
2. **Lines 160–168:** the players' list replaces the project's when every binding fits the action's kind.
3. **Lines 169–175:** bindings and controls are appended to the two flat arrays, and the record keeps the first index and the count.
4. **Lines 177–186:** the old record with the same key and kind hands over its state, simulated holds included, and `moved` remembers where it went.

An action keeps its state only when its kind is the same, because a Button's Down means something other than an Axis's. After the loop, a second pass copies the hysteresis flags of Button actions whose bindings did not change. A stick that rests between 0.35 and 0.5 then keeps its hold through an edit of another action. Simulated events that wait in the queue follow their actions through the `moved` table.

Last, `Compile` raises two version counters. `GetVersion` changes when the set or the players' bindings change, and `GetStateVersion` changes whenever what an action reports might have changed.

### Update and the input frame

`Update` is short on purpose. It reads the project's set again if the project settings changed, lets a binding capture advance, and evaluates only when `Input::GetFrameIndex` advanced since the last evaluation. That one comparison is why Pressed and Released last exactly one input frame and survive suspended frames, as the keys' states do. A binding capture is a rebinding menu's wait for the next control that the player presses; while it listens, no action sees input, and [Rebinding](rebinding.md) teaches it.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L710-L723" symbol="InputActions::Update"
void InputActions::Update()
{
	ST_PROFILE_FUNCTION();
	Refresh();
	UpdateCapture(false);
	const uint64_t frame = Input::GetFrameIndex();
	if (frame == s_State.EvaluatedFrame)
		return;
	s_State.EvaluatedFrame = frame;
	Evaluate();
	// After the evaluation: the input frame in which the captured control was released (and the press Input kept for it
	// while frames were suspended) went by without it.
	UpdateSuppression();
}
```

1. **Line 713:** the project's set is read again if the provider's version changed.
2. **Line 714:** a capture advances even while input frames are suspended.
3. **Lines 716–717:** one comparison decides whether this is a new input frame.
4. **Line 722:** the suppression of a captured control ends after the evaluation.

A frame that does not start an input frame, such as a paused one, evaluates nothing and leaves every state as it was.

### Evaluate

`Evaluate` first applies the simulated events and takes one snapshot of the gamepads. Then it visits every action record. A record whose map is disabled, or while a capture listens, takes the first branch.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L474-L489" from="if (s_State.Capture.Active || !s_State.MapEnabled[record.Map])" to="continue;" symbol="Evaluate"
if (s_State.Capture.Active || !s_State.MapEnabled[record.Map])
{
	// Let go as a released key would be: an action held when its map was disabled reports Released in this input
	// frame and reads as up after it, so code waiting for the release (a charge, a held state) is never left
	// waiting. While a capture listens the release is hidden with everything else (GetReported).
	state = {};
	state.Released = wasDown;
	record.ValueHeld = false;
	for (uint32_t binding = record.FirstBinding; binding < record.FirstBinding + record.BindingCount; binding++)
	{
		const CompiledBinding& compiled = s_State.Bindings[binding];
		const uint32_t count = compiled.Shape == InputBinding::Shape::Control ? 1u : (compiled.Shape == InputBinding::Shape::Composite1D ? 2u : 4u);
		for (uint32_t control = compiled.FirstControl; control < compiled.FirstControl + count; control++)
			s_State.HalfAxisHeld[control] = {};
	}
	continue;
```

1. **Line 474:** a disabled map and a running capture take the same branch.
2. **Lines 479–480:** the state is emptied, and Released is true if the action was down.
3. **Lines 482–488:** the hysteresis flags of its controls are cleared, so no hold survives the disable.

The state becomes empty, but `Released` is true if the action was down. That is the contract's second rule in code. Every other action reads its bindings. The kind chooses how they combine: a Button is down when any binding is, an Axis keeps the binding of the largest magnitude, and a Vector2 keeps the longest vector.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L499-L530" from="switch (record.Kind)" to="value = vector;" symbol="Evaluate"
switch (record.Kind)
{
	case InputActionKind::Button:
		ReadButton(compiled.FirstControl, gamepads, down, pressed);
		break;
	case InputActionKind::Axis:
	{
		const float axis = compiled.Shape == InputBinding::Shape::Composite1D
			? ReadValue(controls[1], gamepads) - ReadValue(controls[0], gamepads)
			: ReadValue(controls[0], gamepads);
		if (std::abs(axis) > std::abs(value.x))
			value.x = axis;
		break;
	}
	case InputActionKind::Vector2:
	{
		glm::vec2 vector(0.0f);
		if (compiled.Shape == InputBinding::Shape::Composite2D)
		{
			vector = glm::vec2(ReadValue(controls[3], gamepads) - ReadValue(controls[2], gamepads),
				ReadValue(controls[0], gamepads) - ReadValue(controls[1], gamepads));
			// Normalized: a diagonal of two keys has length 1, like a full stick.
			const float length = glm::length(vector);
			if (length > 1.0f)
				vector /= length;
		}
		else
		{
			vector = ReadStick(controls[0], gamepads);
		}
		if (glm::dot(vector, vector) > glm::dot(value, value))
			value = vector;
```

1. **Lines 501–503:** a Button reads each control through `ReadButton`.
2. **Lines 504–512:** an Axis takes the positive part minus the negative one for a 1D composite and keeps the value of the largest magnitude.
3. **Lines 516–524:** a 2D composite builds its vector and divides it by its length when that is above 1.
4. **Lines 525–530:** a stick reads as a vector, and the longest vector of all bindings wins.

An Axis from a `1D:` composite is the positive part minus the negative one, so pressing both reads 0. A `2D:` composite makes a vector from the four parts and divides it by its length when that is above 1, so two keys together give a diagonal of length 1. A stick reads as the vector of the gamepad that pushes it furthest. After the loop over bindings, the last lines derive the state.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L536-L556" from="if (record.Kind != InputActionKind::Button)" to="state.Value = value;" symbol="Evaluate"
if (record.Kind != InputActionKind::Button)
{
	value = ApplyDeadZone(value, record.DeadZone);
	const float magnitude = glm::length(value);
	record.ValueHeld = record.ValueHeld ? magnitude > InputActions::c_Release : magnitude > InputActions::c_Press;
	down = record.ValueHeld;
}
if (record.SimulatedDown)
{
	down = true;
	value = record.Kind == InputActionKind::Vector2 ? record.SimulatedValue
		: glm::vec2(record.Kind == InputActionKind::Axis ? record.SimulatedValue.x : 1.0f, 0.0f);
}
pressed = pressed || record.SimulatedPressed;
if (record.Kind == InputActionKind::Button)
	value = glm::vec2(down ? 1.0f : 0.0f, 0.0f);

state.Down = down;
state.Pressed = !wasDown && (down || pressed);
state.Released = !down && (wasDown || state.Pressed);
state.Value = value;
```

1. **Lines 536–542:** an Axis or a Vector2 gets its dead zone and then the hysteresis.
2. **Lines 543–548:** a simulated hold forces Down and takes its value from the simulation.
3. **Lines 550–551:** a Button's value is 1 while it is down and 0 otherwise.
4. **Lines 553–556:** Pressed and Released follow from the previous Down.

The round dead zone is applied to the combined value, once. Then the hysteresis: an Axis or a Vector2 is down above 0.5 until it falls to 0.35 or below. A simulated hold overrides the bindings.

The last lines are the heart of the state. `Pressed` is true when the action was up and is now down, or when it was pressed during the frame. `Released` is true when it is up and was down, or when that press ended. A Button pressed and released within one input frame therefore reports both.

```mermaid caption="Evaluation of one action, from a disabled map through the bindings, the dead zone, the hysteresis and the simulated hold to Pressed and Released." alt="A flow chart. A disabled map or an active capture gives an empty state and a release. Otherwise the bindings are read and combined by kind. Axes and vectors then pass the dead zone and the hysteresis. A simulated hold overrides the result, and pressed and released follow from the previous state."
flowchart TD
	Start["One action record"] --> Off{"Map disabled or capture active?"}
	Off -- yes --> Empty["State empty; Released if it was down"]
	Off -- no --> Read["Read each binding; combine by kind"]
	Read --> Kind{"Kind"}
	Kind -- Button --> Sim
	Kind -- "Axis or Vector2" --> Zone["Radial dead zone, then hysteresis at 0.5 and 0.35"]
	Zone --> Sim{"Simulated hold?"}
	Sim -- yes --> Over["Down true; value from the simulation"]
	Sim -- no --> Edges
	Over --> Edges["Pressed and Released from the previous Down"]
```

### The dead zone

`ApplyDeadZone` is a free function. The software development kit (SDK) for scripts scales the same way in `GetGamepadStick`, so a script that reads the stick directly and an action agree.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L441-L450" symbol="ApplyDeadZone"
// Values within the dead zone read 0, the rest is rescaled to reach 1 (as the script SDK's GetGamepadAxis and
// GetGamepadStick do): for a vector by its length, so diagonals keep their direction.
glm::vec2 ApplyDeadZone(const glm::vec2& value, float deadZone)
{
	const float length = glm::length(value);
	if (!(length > deadZone) || deadZone >= 1.0f)
		return glm::vec2(0.0f);
	const float scaled = std::min((length - deadZone) / (1.0f - deadZone), 1.0f);
	return value / length * scaled;
}
```

1. **Lines 441–442:** the comment says that the script SDK scales the same way.
2. **Lines 446–447:** a length within the dead zone gives 0, and so does a dead zone of 1 or more, which would divide by 0.
3. **Lines 448–449:** the scale reaches 1 at the full push, and the direction is kept.

In symbols, with a result of 0 when the length is not above the dead zone:

$$v' = \frac{v}{|v|}\,\min\!\left(\frac{|v| - d}{1 - d},\ 1\right)$$

Here $v$ is the raw vector, $|v|$ is its length, $d$ is the dead zone and $v'$ is the result. The limits agree with the idea: at $|v| = d$ the result is 0, and at $|v| = 1$ it is the :term[unit vector]{id=unit-vector}. The function divides by the length, not by each axis, so a stick pushed diagonally keeps its direction. The test `!(length > deadZone)` uses the not operator, so that a length that is not a number also gives 0.

### Reading a button from a half axis

A Button reads a control through `ReadButton`. Keys and mouse buttons read the device and the pressed flag. A gamepad button reads all four gamepads from the snapshot, so a player may use any pad. A half axis needs memory: the flag in `HalfAxisHeld` for that control and that gamepad.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L365-L376"
case InputControlType::GamepadHalfAxis:
{
	std::array<bool, c_MaxGamepads>& held = s_State.HalfAxisHeld[controlIndex];
	for (uint32_t gamepad = 0; gamepad < c_MaxGamepads; gamepad++)
	{
		// Pushed beyond c_Press, released below c_Release: a stick resting near the threshold does not flicker.
		const float value = gamepads.Axes[gamepad][control.Code] * static_cast<float>(control.Sign);
		held[gamepad] = held[gamepad] ? value > InputActions::c_Release : value > InputActions::c_Press;
		down = down || held[gamepad];
	}
	return;
}
```

1. **Line 367:** each control has one flag per gamepad.
2. **Line 371:** the sign picks the half, so `LeftY-` reads a pull the other way.
3. **Line 372:** the flag is set beyond 0.5 and cleared at 0.35 or below.
4. **Line 373:** the Button is down when any pad holds the flag.

The flag is set beyond `c_Press` (0.5) and cleared only at or below `c_Release` (0.35). Each gamepad has its own flag, so two pads do not disturb each other. The flag array is parallel to the controls, which is why `Compile` copies it when it keeps an action.

### A whole axis from the pad pushed furthest

A whole axis read by an Axis action takes the gamepad pushed furthest in either direction. The code compares the pads with each other, and a long comment explains why.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L407-L420"
case InputControlType::GamepadAxis:
{
	// The gamepads are compared with each other, not with a running value that starts at 0: Apple Clang 17
	// (clang-1700.0.13.5, -O2 and above, arm64) took that value, chosen by "|first| > 0 ? first : 0", for
	// one that is never negative and dropped its std::abs in the next comparison, so a first gamepad held
	// to the negative side lost to an idle second one and the axis read 0.
	uint32_t furthest = 0;
	for (uint32_t gamepad = 1; gamepad < c_MaxGamepads; gamepad++)
	{
		if (std::abs(gamepads.Axes[gamepad][control.Code]) > std::abs(gamepads.Axes[furthest][control.Code]))
			furthest = gamepad;
	}
	return std::clamp(gamepads.Axes[furthest][control.Code], -1.0f, 1.0f);
}
```

1. **Lines 409–412:** the comment records the :term[compiler]{id=compiler} bug that shaped the loop.
2. **Lines 413–418:** each pad is compared by absolute value with the best one so far, which begins as the first pad.
3. **Line 419:** the value keeps its sign and is clamped to the range.

The comment names Apple's Clang 17 for arm64. At `-O2` and above, that compiler took a running value, which began at 0, for one that is never negative. It then dropped the `std::abs` in the next comparison. A first pad held to the negative side lost to an idle second pad, and the axis read 0. The fix compares pads with each other by index, so no running value exists to be mistaken.

### Map enables, fast reads and the cost

`SetMapEnabled` writes the flag and raises the state version. The next evaluation applies it, which is why a change takes effect from the next input frame and never inside the one being read. A map enable survives a live edit: `Compile` carries it by the map's lower-case name, and a map that is new starts as its `Enabled` field says.

Code that reads the same actions every update, such as the menus, avoids the name lookup. `FindIndex` finds an action's index once, and `GetStateAt` reads the state at an index. The index is valid until `GetVersion` changes. `GetStateVersion` tells a reader that nothing changed since its last look, so it may skip the work. The versions never return to 0 after a reset, which is how code holding an old index notices.

The metric `Actions256` of the `Perf.Input` suite measures the whole evaluation on a set of 256 actions with four bindings each, of every kind and every control, with all four gamepads connected. The generated table of the engine's budgets lists it with a measurement of 7.451 microseconds per input frame and a budget of 11.17 microseconds (`StrataTests/Perf/Budgets.json`). A frame at 60 :term[frames per second]{id=frame-rate} is 16.7 ms, so the evaluation takes 0.04 % of it. Flat arrays, an index in place of a lookup and no allocation make that possible.

### Simulated actions

A tool that plays the game, such as the editor's automation, may hold an action down whatever the bindings say.

```cpp src="Strata/src/Strata/Input/InputActions.cpp#L994-L1004" symbol="InputActions::SimulateAction"
bool InputActions::SimulateAction(std::string_view action, bool down, const glm::vec2& value, std::string* outError)
{
	const ActionRecord* record = FindRecord(action, outError);
	if (!record)
		return false;
	glm::vec2 clamped(0.0f);
	if (std::isfinite(value.x) && std::isfinite(value.y))
		clamped = glm::clamp(value, glm::vec2(-1.0f), glm::vec2(1.0f));
	s_State.SimulatedQueue.push_back({ static_cast<uint32_t>(record - s_State.Actions.data()), down, clamped });
	return true;
}
```

1. **Lines 996–998:** an unknown or ambiguous name fails with the reason.
2. **Lines 1000–1001:** a value that is not finite becomes 0, and the rest is clamped to the range.
3. **Line 1002:** the event is queued for the next evaluation.

`SimulateAction` does not change the state at once. It clamps the value to the range -1 to 1, ignores a value that is not finite and appends an event to a queue that the next evaluation drains. `ReleaseAllSimulated` queues a release for each held action, and `ClearSimulated` drops the holds without releases. [Simulated input](simulated.md) teaches how this merges with a simulated device.

### UI actions and menu key repeat

A menu wants the first press at once, then nothing for a moment, then a steady stream while the key stays down. The game makes this repetition itself, after a delay, at a steady interval. The :term[operating system]{id=operating-system} does the same for keys with its :term[key repeat]{id=key-repeat}, but a game cannot use it, because a game's menus must work on a gamepad and at :term[time scale]{id=time-scale} 0. `UIActionState` repeats the six UI actions. It reads them by the qualified names, `UI/Submit` and the others, once per update, so a game's own `Left` never interferes.

```cpp src="Strata/src/Strata/Input/UIActions.cpp#L39-L87" symbol="UIActionState::Update"
void UIActionState::Update(float deltaSeconds)
{
	// Nothing held and nothing changed since the last update: this one would read the same.
	const uint64_t stateVersion = InputActions::GetStateVersion();
	if (stateVersion == m_StateVersion && !m_Active)
		return;
	m_StateVersion = stateVersion;
	const uint64_t setVersion = InputActions::GetVersion();
	if (setVersion != m_SetVersion)
	{
		// Every set has the UI map's actions (InputActionSet::FromJson adds them), so the lookups find them.
		m_SetVersion = setVersion;
		for (uint32_t action = 0; action < c_UIActionCount; action++)
			m_Indices[action] = InputActions::FindIndex(GetUIActionQualifiedName(static_cast<UIAction>(action)));
	}

	const float delta = std::isfinite(deltaSeconds) && deltaSeconds > 0.0f ? deltaSeconds : 0.0f;
	m_Active = false;
	for (uint32_t action = 0; action < c_UIActionCount; action++)
	{
		const InputActionState state = m_Indices[action] ? InputActions::GetStateAt(*m_Indices[action]) : InputActionState();
		ActionRecord& record = m_Actions[action];
		record.Pressed = state.Pressed;
		record.Down = state.Down;
		record.Repeated = false;
		if (record.Pressed)
		{
			record.Repeated = true;
			record.HeldTime = 0.0f;
			record.NextRepeat = c_RepeatDelay;
		}
		else if (state.Down)
		{
			// One repeat an update at most; time beyond it is not owed later.
			record.HeldTime += delta;
			if (record.HeldTime >= record.NextRepeat)
			{
				record.Repeated = true;
				while (record.NextRepeat <= record.HeldTime)
					record.NextRepeat += c_RepeatInterval;
			}
		}
		else
		{
			record.HeldTime = 0.0f;
		}
		m_Active = m_Active || record.Down || record.Pressed || record.Repeated;
	}
}
```

1. **Lines 41–44:** nothing held and nothing changed means this update would read the same, so it returns.
2. **Lines 46–53:** the indices are found again only when the set changed.
3. **Line 55:** a delta that is not finite or not positive counts as 0.
4. **Lines 64–69:** a press repeats at once and sets the first due time.
5. **Lines 70–80:** a held action repeats once when the held time reaches the due time, and the due time moves past it.

Each record holds how long the action was held and when the next repeat is due. A press repeats at once and sets the next repeat at 0.4 seconds (`c_RepeatDelay`). A held action adds the update's delta, and when the held time reaches the next repeat time, it repeats and moves the due time forward by 0.1 seconds (`c_RepeatInterval`) until it passes the held time. At most one repeat happens in an update, and time beyond it is not owed later, so a slow frame never fires a burst. The delta is the :term[unscaled time]{id=unscaled-time}: a menu repeats at time scale 0.

The first lines skip an update at the cost of one comparison. When nothing was held in the last update and `GetStateVersion` did not change, this update would read the same, so it returns. Every scene updates its UI, also one without a canvas, so the common case has to be cheap. The record of indices is found again only when `GetVersion` changes.

:::example[Four updates of a held key]
A player holds Down while slow frames bring updates at 0, 0.25, 0.5 and 0.75 seconds. At 0 the action is pressed: Repeated is true and the next repeat is due at 0.4. At 0.25 the held time is 0.25, below 0.4, so nothing repeats. At 0.5 the held time passes 0.4, so Repeated is true; the due time moves to 0.5, then to 0.6, which is past the held time. At 0.75 the held time passes 0.6, so Repeated is true again and the due time moves to 0.8.

| Time held | Pressed | Repeated | Next repeat due |
| --- | --- | --- | --- |
| 0 s | yes | yes | 0.4 s |
| 0.25 s | no | no | 0.4 s |
| 0.5 s | no | yes | 0.6 s |
| 0.75 s | no | yes | 0.8 s |

:::

At 60 updates per second the repeats come about 0.4 s after the press and then about every sixth update. The game's text fields repeat their edit keys, such as the delete key and the arrows, on the same two constants, in `GameUISystem::IsEditKeyRepeated`; [Text and fonts in the game UI](../ui/text.md) teaches that part.

:::simplified[Two repeats, one name]
A script has another helper, the SDK's `KeyRepeat`, which runs in the script's own module on one key and by default waits 0.25 s, then repeats every 0.05 s. It is not the engine's repeat of the six UI actions. [Timers and events](../make/timers-events.md) covers it.
:::

### How scripts reach input

A script module never links the engine, so everything it asks crosses the application binary interface (ABI), a table of C functions that the engine fills and the script calls. [The script ABI](../scripting/abi-sdk.md) explains why new functions are appended at the end. The input functions come in three groups.

The device functions are the oldest. Keys and the mouse belong to the initial set of the ABI: `IsKeyDown`, `IsKeyPressed`, `IsKeyReleased`, the same three for mouse buttons, `GetMousePosition`, `GetMouseDelta` and `GetScrollDelta`. Gamepads, the cursor and typed text came after it. `GetTypedText` copies the text the player typed during the frame into a buffer the script owns, at most 1,024 bytes. `SetCursorMode` takes Normal, Hidden or Locked, and its host function records the game's wish through `Input::SetGameCursorMode`, which the window applies while the game has the input.

The ten action functions and three capture functions were appended later. The action functions are `InputIsActionDown`, `InputIsActionPressed`, `InputIsActionReleased`, `InputGetActionValue`, `InputSetActionMapEnabled`, `InputIsActionMapEnabled`, `InputGetActionBindings`, `InputSetActionBindings`, `InputResetActionBindings` and `InputSaveBindings`. The capture functions are `InputBeginBindingCapture`, `InputPollBindingCapture` and `InputCancelBindingCapture`. Names and bindings go across as text, and bindings come back one per line, each followed by a line break. Because a script module may be older than the engine, the SDK checks that a member exists before it calls it.

```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L2756-L2763" symbol="ReadActionState"
std::optional<InputActionState> ReadActionState(ScriptSystem& system, StrataScriptString action, const char* function)
{
	std::string error;
	std::optional<InputActionState> state = InputActions::GetState(ScriptStringView(action), &error);
	if (!state)
		system.ReportProblem(function, error);
	return state;
}
```

The host function reads the state and, when the name is unknown or ambiguous, calls `ReportProblem` with the reason. `ReportProblem` logs each distinct message once, so a script that asks for a wrong name every frame fills the log with one line, and the call returns false, which reads as up. [Host functions](../scripting/host-api.md) teaches the pattern.

### The editor's commands

The editor changes the set only through commands, so an agent does what a person does. `inputActions.setMap` adds, renames, enables or removes a map, and `inputActions.setAction` adds, changes, moves or removes an action. Both are Edit commands that leave one project undo step. A game that plays at the time reads the change at its next frame, which is the live edit of the contract. `inputActions.resetPlayerBindings` is a Session command that deletes the players' bindings file, so that the project's bindings apply again.

The full parameters are in the generated command reference. For an agent, these parameters of `inputActions.setAction` set the bindings of `Gameplay/Jump`.

```json
{ "action": "Gameplay/Jump", "kind": "Button", "bindings": ["Key/Space", "Gamepad/A"] }
```

In the editor, the same edit is a click in Project Settings, **Input Actions**, where a button binds the next control that you press. [Settings windows](../editor-ui/settings-windows.md) draws that page.

Input actions arrived with the release 0.6.0, together with their rebinding.

## What Strata does not do

Strata has no processors that change a binding's value, no chords and no interactions such as hold or tap. A binding is one control or one composite, and the parser refuses every other text. Mouse motion and the scroll wheel are no action sources: a game that wants them reads the raw device calls. The reasons are cost and clarity: each of these ideas needs state per binding or per pair of bindings, and the evaluation above is stateless apart from the hysteresis flags. A game that needs Shift plus a key builds the chord in a script, or gives the combination an action of its own.

:::elsewhere[Other engines]
Unity's Input System package gives bindings processors, such as a dead zone or an inversion, and interactions, such as hold, tap and multi-tap, and its composites can require a second button held with the first. Unreal's Enhanced Input gives an action `UInputModifier` and `UInputTrigger` objects, which change its value and decide when it fires. Both can read mouse motion and the wheel as action sources. See Further reading.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Value filters and triggers on every binding | Unreal's Enhanced Input; Unity's processors and interactions | Hold, tap and chord logic in data, with no script | State per binding, a larger :term[file format]{id=file-format} and a costlier evaluation |
| Mouse motion and wheel as action sources | Unity and Unreal | Rebinding for the wheel, with no raw calls | A second kind of value, with sensitivity and no clear dead zone |
| Evaluation on demand, when a script reads | Many small engines | No work for an action nobody reads | Pressed and Released tied to the first reader, and a cost per read |
| Strings as keys at every read | Scripts that find an action by name each frame | No compile step | A :term[hash]{id=hash} of a string per read, and no cached index for the menus |
| A binding as a class with a virtual read | Engines with add-on input parts | New control types without a change to the engine | Pointers instead of arrays, and a cost the perf test would show |

## How it is tested

The suite `Core.InputActions` in `StrataTests/src/Core/InputActionsTests.cpp` holds the tests of this page. Its test cases check these things:

- The binding text round-trips for every control and composite.
- The reader refuses names, kinds and bindings that do not fit, with the reason.
- The `UI` map is added when it is missing and cannot lose an action.
- A gameplay `Left` coexists with `UI/Left`, and an ambiguous bare name is refused with both matches named.
- A set at every limit fits its section bound and round-trips through the project file.
- Button, Axis and Vector2 values combine their bindings as specified, and dead zones are round and scaled.
- A whole axis reads the pad pushed furthest, either way, and half axes press at 0.5 and release at 0.35.
- A press or a release shows for one input frame, also when frames are suspended.
- A map disabled while its action is held releases it once, and then the action reads as up.
- A simulated action is down from the next input frame, whatever its bindings.

The suite `Core.InputActions.Sweep` truncates and flips bytes of binding texts, section values and bindings files, and requires a refusal or a valid result, never a crash. The metric `Actions256` of the `Perf.Input` suite has its own budget. Run the correctness suites with a filter on the test binary.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite="Core.InputActions*"
```

The filter takes a doctest pattern. The star also matches `Core.InputActions.Sweep`.

## Changing it safely

Three kinds of change are common. A new control type needs a case in `InputControlType`, the parser, `ToString`, `ReadButton`, `ReadValue` and `FitsKind`, with a round-trip test and a sweep entry. A new binding rule belongs in `FitsKind`, which every entry point uses. A new default for the `UI` map goes into `MakeDefaultUIActions`; the sample projects hold a copy, so they need the same change.

Four rules of `AGENTS.md` apply. Append host functions at the end of the ABI table and never change its order, because script modules built earlier would call the wrong function. Report misuse with `ReportProblem` and return a failure value, because a script's mistake must not stop the game. Send every change to the project through a command, because a panel that writes the file skips undo. Read the controls that players can rebind as actions, because the players' bindings reach only them.

Before a commit, run the `Core.InputActions*` suites, the `Scripting.*` tests that use input, and the feature test that holds the action functions.

## What went wrong before

A first pad held to the negative side lost to an idle second one on Apple's Clang 17, as the section on the whole axis told. The regression test is `A whole axis reads the gamepad pushing it furthest, either way`, and its words show the lesson: a test of a maximum has to push the first element the wrong way.

## Summary

- A binding is text from one grammar: a control, `1D:` with two button-like parts or `2D:` with four. A Button takes button-like controls, an Axis those and whole axes and `1D:`, a Vector2 sticks and `2D:`. The parser names its refusal.
- An action's state follows from the bindings and the previous frame. Pressed and Released last one input frame, a disabled map releases once, a stick holds from 0.5 down to 0.35, and a live edit presses nothing again.
- Compiling the set makes flat arrays and carries state by the lower-case qualified name and the kind, so the evaluation of 256 actions takes microseconds and an edit keeps the state of unchanged actions.
- The menus repeat the six UI actions after 0.4 s, then every 0.1 s of unscaled time, at most once an update.
- Scripts reach actions through ten action functions and three capture functions with names and bindings as text; agents use `inputActions.setMap`, `inputActions.setAction` and `inputActions.resetPlayerBindings`.

## Check yourself

1. Which of these bindings does a Vector2 action accept? (a) `Gamepad/LeftX` (b) `2D:Key/W,Key/S,Key/A,Key/D` (c) `1D:Key/A,Key/D` (d) `Gamepad/RightStick`.

   :::answer{tests="write-bindings"}
   (b) and (d). A Vector2 takes `2D:` composites and sticks. (a) is a whole axis, which only an Axis takes. (c) is a `1D:` composite, which an Axis takes.
   :::

2. `Jump` is bound to `Key/Space`. The player presses Space in input frame 1 and holds it. In frame 3 a script disables the map of `Jump`, which takes effect from frame 4. What do Down, Pressed and Released read in frames 1 to 5?

   :::answer{tests="predict-states"}
   Frame 1: Down and Pressed. Frames 2 and 3: Down only. Frame 4: the map is disabled, so the action lets go: Down is false and Released is true, once. Frame 5: all false, though Space is still held, until the map is enabled again.
   :::

3. A designer edits the dead zone of `Look` while a player holds Jump. Does Jump report Pressed again? What if the edit changes the kind of Jump from Button to Axis?

   :::answer{tests="compiled-arrays"}
   No in the first case. `Compile` finds the old record by the key `gameplay/jump`, sees the same kind and copies the state, so Jump stays down with no new Pressed. In the second case the kind differs, so the state is not copied: the action starts as up and is evaluated again from its bindings, and it may then report Pressed.
   :::

4. A held `UI/Down` is read at updates 0.125 s apart. At which held times does it repeat?

   :::answer{tests="compute-repeat"}
   At 0.125, 0.25 and 0.375 s the held time is below 0.4, so it does not repeat. At 0.5 s it repeats and the due time moves to 0.6. At 0.625 s it repeats (due time 0.7), at 0.75 s again (0.8), and so on. The interval of 0.1 s is shorter than the update, so every update repeats, and the code allows one repeat an update.
   :::

5. A script calls `InputIsActionDown` with `Left`, and the project has `Gameplay/Left` and `UI/Left`. What happens, and what is the fix?

   :::answer{tests="script-access"}
   The name is ambiguous. The host function calls `ReportProblem` once with `'Left' is ambiguous: Gameplay/Left, UI/Left`, and the call returns false, which reads as up. The fix is the qualified name, `Gameplay/Left`.
   :::

## Exercises

1. **Basic.** Write bindings for three actions. `Fire` is a Button on the left mouse button or the right trigger. `Steer` is an Axis on A and D or the left stick's X axis. `Aim` is a Vector2 on the arrow keys or the right stick.

   :::answer[Worked solution]{tests="write-bindings"}
   `Fire`: `Mouse/Left` and `Gamepad/RightTrigger+`, both button-like. `Steer`: `1D:Key/A,Key/D` and `Gamepad/LeftX`: the negative part first. `Aim`: `2D:Key/Up,Key/Down,Key/Left,Key/Right` and `Gamepad/RightStick`: the order is up, down, left, right. Each fits its kind.
   :::

2. **Medium.** A Button is bound to `Gamepad/LeftY+`. The stick's value goes 0, 0.4, 0.6, 0.45, 0.36, 0.3, 0.4, 0.55. Predict Down, Pressed and Released at each value, then write a program that checks you.

   :::answer[Worked solution]{tests="predict-states" solution="sketches/input-actions-hysteresis.cpp"}
   The flag is set above 0.5 and cleared at or below 0.35. So 0 and 0.4 read up, 0.6 presses, 0.45 and 0.36 stay down, 0.3 releases, 0.4 stays up, and 0.55 presses again.

   ```cpp sketch="input-actions-hysteresis.cpp"
   // A half axis holding a Button: pressed beyond 0.5, held until the value falls below 0.35.
   #include <cstdio>

   int main()
   {
   	const float c_Press = 0.5f;
   	const float c_Release = 0.35f;
   	const float samples[] = { 0.0f, 0.4f, 0.6f, 0.45f, 0.36f, 0.3f, 0.4f, 0.55f };
   	bool held = false;
   	for (const float value : samples)
   	{
   		const bool wasHeld = held;
   		held = held ? value > c_Release : value > c_Press;
   		std::printf("value %.2f: down=%d pressed=%d released=%d\n", value, held, held && !wasHeld, !held && wasHeld);
   	}
   	return 0;
   }
   ```

   ```text output-of="input-actions-hysteresis.cpp"
   value 0.00: down=0 pressed=0 released=0
   value 0.40: down=0 pressed=0 released=0
   value 0.60: down=1 pressed=1 released=0
   value 0.45: down=1 pressed=0 released=0
   value 0.36: down=1 pressed=0 released=0
   value 0.30: down=0 pressed=0 released=1
   value 0.40: down=0 pressed=0 released=0
   value 0.55: down=1 pressed=1 released=0
   ```

   1. **Lines 6–7:** the two thresholds, as `InputActions` names them.
   2. **Line 13:** the whole rule: the threshold depends on whether the flag is already set.
   3. **Line 14:** Pressed and Released come from the previous flag.

   The line `held = held ? value > c_Release : value > c_Press;` is the whole rule, as in `ReadButton`. A reading of 0.4 means two things, up before the press and up after the release, because of the two thresholds.
   :::

3. **Hard.** Design Shift plus a key as a chord, and the mouse wheel as a half-axis control. Say what the data and the evaluation need, which files change and what the perf test would show.

   :::answer[Worked solution]{tests="write-bindings"}
   A chord needs a new shape with a list of controls that must all be down. So `InputBinding::Shape`, the parser, `ToString`, `GetControlCount` and `FitsKind` change, and a Button takes it. `ReadButton` tests every part.

   The wheel is no held state: the raw device calls report a scroll delta per frame. A control type that reads it is non-zero for one frame, and a half axis from it needs its own rule, because it has no rest value. Both changes add a case to the sweep and the round-trip tests. The perf budget would move little for chords and not at all for the wheel, since both add one case to a switch; the arrays keep their shape.
   :::

4. **Hard.** Trace it yourself. Run the Third-Person sample, put a breakpoint in `Evaluate`, and hold W and D. Find where the composite becomes length 1 and, with a gamepad, where the dead zone of `Gamepad/LeftStick` applies.

   :::answer[Worked solution]{tests="compiled-arrays"}
   Both are in `Strata/src/Strata/Input/InputActions.cpp`, in the anonymous :term[namespace]{id=namespace}.

   In `Evaluate`, the `Vector2` case reads a `2D:` binding and builds the vector from the four `ReadValue` results. It divides the vector by its length when that is above 1, so W and D give (1, 1), which becomes (0.71, 0.71). For the stick, `ReadStick` returns the raw vector. After the loop, `ApplyDeadZone(value, record.DeadZone)` scales it, so a stick at (0.3, 0.4) becomes (0.25, 0.33). Look at `record.ValueHeld` to see the hysteresis.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Input/InputActionSet.h` and `InputActionSet.cpp`: `InputActionSet`, `InputBinding`, the parser, `FitsKind`, `FromJson` and `MakeSection`.
- `Strata/src/Strata/Input/InputActions.h` and `InputActions.cpp`: `InputActions`, `Compile`, `Evaluate`, `ApplyDeadZone`, the simulated actions.
- `Strata/src/Strata/Input/UIActions.h` and `UIActions.cpp`: `UIActionState` and the repeat of held menu actions.
- `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`, `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the host functions and their table.
- `StrataEditor/src/Editor/EditorInputActionsCommands.cpp`: the `inputActions.*` commands.
- `StrataTests/src/Core/InputActionsTests.cpp` and `StrataTests/src/Perf/InputPerfTests.cpp`: the tests. The setting `Input.Actions` holds the data.

## Further reading

- Unity's documentation, "Input System: actions, bindings, processors and interactions": the model that Strata's is the smaller form of. Intermediate.
- Unreal Engine's documentation, "Enhanced Input": input actions with modifiers and triggers. Intermediate.
- Robert Nystrom, "Game Programming Patterns", chapter "Command": why games turn input into objects. Beginner.
