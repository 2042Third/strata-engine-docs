# Brief: `input/how-input-works`

| Field | Value |
| --- | --- |
| Title | How input reaches a game: events, polling, edges and intents |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `core/frame-loop`, `core/windows-events` |
| From | new; the input part had no concept page: audio-input concepts B1, B2, B5-B7 (where input comes from, events against polling, edges, text is not keys, focus and capture, actions instead of keys in Unity, Unreal and Godot) |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `input/how-input-works` — How input reaches a game: events, polling, edges and intents

**Covers.** The page starts with the problem as a reader meets it, in the Third-Person sample: Space makes the robot
jump once, holding W walks it, typing a name in a menu must not walk it, and a gamepad does all of it with other
controls. The naive answer, "is the key down?" asked once a frame, loses a tap shorter than a frame and jumps every frame
the key is held. In this order the page teaches: where input comes from (the operating system sends events to a window;
GLFW's callbacks; key codes by position against characters by layout; the system's key repeat, which only makes
events); events against polling, and Strata doing both (the callbacks feed a polled state and also send engine events);
polling with edges (down, pressed and released, cleared at the start of each frame; a press and a release inside one
frame both reported; why Pressed is read in the frame update and not in the fixed update, which runs zero or more times
in a frame); text is not keys (character events after layouts, dead keys and input methods; code points and UTF-8);
focus, enabling and capture (who gets the input when the editor, the game, its UI and a text field share one keyboard);
actions instead of keys (intents bound to controls, kinds, composites such as WASD, maps enabled per mode, players'
rebinding).

The approaches table compares Unity's Input System, Unreal's Enhanced Input and Godot's InputMap (actions, maps or
contexts, composites, modifiers and processors, rebinding). Strata's choice, as a bridge to the internals pages: a polled
state with edges in `Input`, events beside it, and actions with maps, composites and players' bindings, without
modifiers. What Strata does not do: touch input. Common mistakes: key codes taken for characters (on AZERTY, `Key::A` is
where A sits on a US keyboard), key repeat used for movement, "pressed" made by comparing with the last frame, text built
from key presses, and gameplay that reads devices while a text field is being edited. At the end the reader can say which
question each form of input answers, and why a game reads actions rather than keys.

**Leaves out.**

- Strata's `Input`: its bitsets, input frames, suspension and captures in code → `input/devices-state`
- The event classes and the layer stack → `core/windows-events`
- Mouse spaces and cursor modes → `input/mouse-cursor`
- Gamepads, dead zones and hysteresis → `input/gamepads`
- Strata's input actions → `input/actions`
- Input-method composition in game UI → `ui/text`
- UTF-8 as an encoding → `basics/bytes`

**Fit.** `over`: about 4,150 words against M (3,000). Five concepts at an engine builder's pace (about 1,750 words), the
problem and its naive answer, the approaches table, the mistakes and three exercises go past M's top. Proposed: L
(5,000) by S2, whose range holds the estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:302` | concept | home | B1: where input comes from; key codes by US position (`Strata/src/Strata/Input/KeyCodes.h:10-11`); repeat only as events |
| `audio-input:309` | concept | home | B2: polling and edges; a tap inside one frame; Pressed in a fixed update missed or doubled |
| `audio-input:329` | concept | home | B5: text input is not key input |
| `audio-input:333` | concept | home | B6: focus, enabling and capture, as ideas; the engine's side is `input/devices-state`'s |
| `audio-input:339` | concept | home | B7: actions instead of keys; Unity, Unreal and Godot compared; composites normalized (a WASD diagonal is not 1.41) |
| `audio-input:445` | figure | home | Timeline: a key held three frames and a tap inside one frame, with the transitions cleared at each frame's start |
| `audio-input:655-658` | term | home | Polling; event (input); down, pressed and released; edge (transition) |
| `audio-input:661-665` | term | home | Key code, scancode, key repeat, typed text and character event, IME |
| `audio-input:187` | feature | use | The event classes the callbacks send beside the state, to contrast events and polling (home `core/windows-events`) |
| `audio-input:517` | rule | link | Read Pressed and Released in `OnUpdate` |
| `audio-input:666` | term | use | UTF-8 (home `basics/bytes`) |
| `new:9` | not-done | home | Touch input: no touch screens or gestures; how engines map touches to pointers. Evidence: `git grep -niE "touch" 822a7a46 -- Strata/src/Strata/Input Strata/src/Platform/GLFW` finds nothing |
| `foundation:587` | term | home | Polling input: one glossary entry with polling (`audio-input:655`) |
| `new:27` | hands-on | home | Exercises (D27): which `Key` value the key labelled A on a French AZERTY keyboard reports, and which character its event carries (computation); a script in the playground that counts the frames in which `Input::IsKeyPressed(Key::Space)` is true in `OnUpdate` and in `OnFixedUpdate` while Space is tapped and held, each count predicted first (predict, then run; done); the actions and maps of a game that walks, drives and opens a menu (design). Evidence: `Strata/src/Strata/Input/KeyCodes.h:10-11`; `StrataScriptCore/Include/StrataScript/Script.h:84-85` |
| `gameui:736` | open | home | Settled with `new:9`: the game UI has no touch input either; the search over `Strata/src/Strata/GameUI` finds only `GameUIScene::TouchHits`, which marks hit tests stale (`Strata/src/Strata/GameUI/GameUIScene.h:297-298`), so the book claims no touch anywhere |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame loop | `core/frame-loop` | must |
| Windows and the events they deliver | `core/windows-events` | must |
| The fixed step, which runs zero or more times in a frame | `core/time` | must |
| Unicode code points and UTF-8 | `basics/bytes` | must |
| A callback | `basics/cpp-generic` | helps |
| Project settings, where a project keeps its actions | `world/projects-settings` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `down` | Down | - |
| `edge-transition` | Edge (transition) | - |
| `event-input` | Event (input) | - |
| `ime` | IME | - |
| `key-code` | Key code | - |
| `key-repeat` | Key repeat | - |
| `polling` | Polling | Polling input |
| `pressed` | Pressed | - |
| `released` | Released | - |
| `scancode` | Scancode | - |
| `typed-text` | Typed text | character event |
