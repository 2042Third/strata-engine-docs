# Brief: `make/input`

| Field | Value |
| --- | --- |
| Title | Input and input actions |
| Kind | T |
| Size | L |
| Tracks | G, B |
| Needs | `make/scripting-scene` |
| From | gamedev "Input and input actions" (§1.10, concept 14); audio-input "Controls players can change" (use side: actions and their bindings); scripting "The gameplay API, part 3": `Input` (keys, mouse, gamepads, sticks and dead zones, cursor mode, input actions); hold and toggle; Coin Run's Move action. Binding capture, saving the bindings and typed text are `make/menus`', where the rebinding screen and text fields are built |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/input` — Input and input actions

**Covers.** The page gives Coin Run its Move action and teaches devices against actions. The idea first, in one
paragraph and the input actions figure: a game can read keys and sticks directly, but players want to choose their
controls and to use a keyboard or a gamepad alike, so games name actions (Move, Jump) and bind controls to them; the
project holds the actions in maps, and a player's own bindings override the project's. Then the steps. (1) Read the
keyboard: a new script `BallControl` on the ball moves it with W, A, S and D through `Input::IsKeyDown`, by writing its
position (the ball has no rigid body yet), scaled by `deltaTime`; press, hold and release with `IsKeyPressed`,
`IsKeyDown` and `IsKeyReleased`, read in `OnUpdate`. (2) Keys reach the game only while the Game view has the focus
and the game plays; clicking the Inspector takes them away. (3) Read a gamepad: `IsGamepadConnected`, the left stick
with `Input::GetGamepadStick(GamepadStick::Left)` and its round dead zone (from zero: the small movement a resting
stick reports, ignored in every direction, with the round dead zone drawn; the vector's length is at most 1), and
`GetGamepadAxis` named for one axis or a trigger, whose dead zone works per axis; buttons, the Xbox layout. (4) Make
the action: **File ▸ Project Settings ▸ Input Actions**, the
map **Gameplay** and the action **Move** of kind Vector2, with a `2D:` composite of W, A, S and D, another of the
arrows, and the gamepad's left stick; bind a key by pressing it (the page's binding capture). (5) Read it:
`Input::GetActionValue("Gameplay/Move")` gives a vector of length at most 1 with the dead zone applied; the ball's
script uses it, and the keyboard and gamepad code of steps 1 and 3 goes. (6) Two Button actions: **Jump** (Space and
the gamepad's A), read once per press with `IsActionPressed` (it only logs here; `make/physics` makes the ball jump),
and **Boost** (Shift), held with `IsActionDown`; a toggle made from presses; hold and toggle compared. (7) Edit the
actions while the game plays: the change applies at once and keeps the state of the other actions. (8) Look around:
a Vector2 action **Look** bound to the gamepad's right stick, and the mouse read beside it, because mouse motion is no
binding: the camera turns from `Input::GetMouseDelta()` while the right button is held, with the cursor **Locked** by
`SetCursorMode`; Shift+F1 gives the cursor back to the editor (an optional section, its camera script left out of the
checkpoint; the Look action stays). (9) Several maps, one short section of about 200 words: why a project has several
(walking and driving, a menu over the game); a second map **Vehicle** with one action, which the ball's script
switches on, and **Gameplay** off, with `Input::SetActionMapEnabled` (read back with `IsActionMapEnabled`); the change
applies from the next input frame, and an action held at that moment reports `IsActionReleased` once, as a key let go
would; maps start as the project says in every session; and every gamepad drives an action, so two local players read
their own pads by index (`IsGamepadButtonDown(button, 1)`). The section is optional and its map is left out of the
checkpoint. The binding grammar in a small table (`Key/Space`,
`Gamepad/LeftStick`, `Gamepad/LeftX+`, `1D:`, `2D:`), the reserved map `UI` named for `make/menus`. The rule in a
`:::rule` aside: read the player's controls as input actions, never as fixed keys, because players rebind them. What
Strata does not do here, each in a sentence or two: touch input (`new:24`); action modifiers, chords, processors and
interactions, and mouse motion or scroll as action sources (`new:25`); force feedback (`new:26`); devices assigned to
players for local multiplayer (`new:27`); controllers missing from GLFW's gamepad database, more than four gamepads,
and mappings that a game adds (`new:28`). The exercises (`new:29`) are done in the editor and in a script. At the
end the reader can define actions, bind them, read them from a script and tell when to read devices directly.

**Leaves out.**

- How input reaches a game: events, polling and edges → `input/how-input-works`
- Device state, keyboard capture and the enabled flag → `input/devices-state`
- Gamepads inside: mappings and layouts → `input/gamepads`
- Mouse spaces and cursor modes inside → `input/mouse-cursor`
- Actions inside: evaluation, thresholds, combining → `input/actions`
- Players' bindings, binding capture in a game, saving them, the rebinding screen → `make/menus`
- Typed text in a text field → `make/menus`
- Simulated input for play-tests → `make/automated-playtests`
- The Game view's input ownership inside → `editor-ui/game-view`

**Fit.** `fits`: about 5,250 words against L (5,000). Nine steps, most with code, take most of it, with the idea and the
round dead zone taught from zero, the grammar table, the dead zone plots, four pictures, the five absences and two
exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:143` | feature | home | Device input: keys, mouse, gamepads 0 to 3 with round dead zones, cursor modes, only while the Game view has the focus; Shift+F1 |
| `gamedev:144` | feature | home | Input actions: maps of Button, Axis and Vector2 actions, bindings and composites, dead zones; the reserved `UI` map named |
| `gamedev:325` | concept | home | Input: devices against actions; the mistakes (fixed keys, ignored dead zones, mouse look through an action) |
| `gamedev:414` | figure | home | The input actions pipeline: devices, bindings, the strongest binding, dead zone, value; the player's bindings over the project's |
| `gamedev:498` | rule | home | Read controls as input actions; mouse motion is no action |
| `gamedev:645` | term | home | Input action, map, binding, composite, dead zone |
| `audio-input:563` | hands-on | home | Steps 1 and 3: the keyboard and a gamepad read directly, the left stick with `GetGamepadStick` (a round dead zone, length at most 1) and `GetGamepadAxis` named for one axis or a trigger (a dead zone per axis). Evidence: `StrataScriptCore/Include/StrataScript/Input.h:326-353` (read at the pin) |
| `audio-input:565` | hands-on | home | Step 8: mouse look with a locked cursor |
| `audio-input:567` | hands-on | home | Steps 4 and 5: the direct reads converted to the Move action; step 9: the Vehicle map switched on and off from a script (`SetActionMapEnabled`, `IsActionMapEnabled`), with what disabling does to a held action |
| `new:24` | not-done | home | Touch input. Evidence: `git grep -ni touch 822a7a46 -- Strata/src/Strata/Input Strata/src/Platform/GLFW` finds nothing (run at the pin) |
| `new:25` | not-done | home | Action modifiers, chords, processors and interactions; mouse motion and scroll as action sources (they stay on the raw API). Evidence: `Docs/DeveloperGuide.md:1464-1465`; `Docs/Releases/0.7.0.md:361`, `:412`; `Strata/src/Strata/Input/InputActionSet.cpp:102` refuses every binding but `Key/`, `Mouse/<button>`, `Gamepad/`, `1D:` and `2D:` (read at the pin) |
| `new:26` | not-done | home | Force feedback (rumble, vibration). Evidence: `git grep -ni -e rumble -e vibrat -e haptic 822a7a46 -- Strata/src StrataScriptCore` finds nothing (run at the pin) |
| `new:27` | not-done | home | Devices assigned to players for local multiplayer: gamepad bindings read every gamepad, and all players share one set of actions; a game reads each player's pad by index. Evidence: `Docs/DeveloperGuide.md:1460`; `Docs/Releases/0.7.0.md:361-362`, `:412`; `Docs/Roadmap.md:1707`; `StrataScriptCore/Include/StrataScript/Input.h:301-312` (read at the pin) |
| `new:28` | not-done | home | Controllers missing from GLFW's gamepad database, more than four gamepads, and gamepad mappings that a game adds: an unmapped controller reads as not connected and keeps its slot. Evidence: `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`; `Strata/src/Strata/Input/GamepadCodes.h:42` (`c_MaxGamepads = 4`); `git grep -n glfwUpdateGamepadMappings 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src` finds nothing (run at the pin) |
| `new:29` | hands-on | home | Exercises: **Basic.** predict what `Input::GetActionValue("Gameplay/Move")` reads while W and D are held together (a diagonal of length at most 1, not 1.41), then log it to check; **Medium.** a Button action **Pause** (P and the gamepad's Start) whose press sets the time scale to 0 and back with `Time::SetTimeScale`, and a prediction of what the ball and the coins' bob do meanwhile. Evidence: `StrataScriptCore/Include/StrataScript/Input.h:402-404` (a Vector2 action's length at most 1); `StrataScriptCore/Include/StrataScript/Time.h:28-33` (elapsed time is simulation time), `:43-53` (`GetTimeScale`, `SetTimeScale`) |
| `editor-ui:691` | hands-on | home | Step 4's binding of an action by pressing its key; the exercise's collision layers and quality preset are `make/physics`' and `make/quality`'s |
| `audio-input:107-109` | feature | use | Key, mouse and gamepad codes |
| `audio-input:122` | feature | use | Cursor modes |
| `audio-input:148-152` | feature | use | The action model, the binding grammar, kinds, names and the reserved `UI` map |
| `audio-input:153-157` | feature | use | The settings section, evaluation, combining bindings, thresholds and the radial dead zone, at the maker's level |
| `audio-input:158-159` | feature | use | Step 9: every gamepad drives an action, so two local players read their own pads by index; maps switched off and on, applied from the next input frame, a held action released once |
| `audio-input:160` | feature | use | Live edits of the actions while playing |
| `audio-input:162` | feature | use | Players' bindings over the project's, named for `make/menus` |
| `audio-input:180-181` | feature | use | The `inputActions.*` commands; the Input Actions page |
| `audio-input:315` | concept | use | Mouse spaces and cursor modes, at the maker's level |
| `audio-input:321` | concept | use | Gamepads, at the maker's level |
| `audio-input:339` | concept | use | Actions instead of keys |
| `audio-input:451-452` | figure | use | The gamepad's conventions; the dead zone plots, step 3's showing the round zone of `GetGamepadStick` |
| `audio-input:474` | figure | use | Project Settings ▸ Input Actions |
| `audio-input:476-477` | figure | use | The add-binding popup; binding by pressing a key |
| `audio-input:479` | figure | use | The Game view with a locked cursor |
| `audio-input:525` | rule | use | Gameplay reads rebindable controls as input actions |
| `audio-input:537` | rule | use | The game's cursor mode applies only while it has the input |
| `scripting:122` | feature | use | The SDK's `Input` |
| `scripting:483` | rule | use | Press and release edges read in `OnUpdate` |
| `scripting:487` | rule | use | Input actions for what a player might rebind |
| `editor-ui:208` | feature | use | Who gets the keys in play mode; Shift+F1 |
| `editor-ui:231` | feature | use | The Input Actions page and binding a key by pressing it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Writing positions and rotations from a script | `make/scripting-scene` | must |
| `OnUpdate`, `deltaTime`, and why what must happen once a frame goes in `OnUpdate` | `make/script-loop` | must |
| Project Settings and its pages | `make/project-files` | must |
| A direction as (x, y), scaled by a number | `make/transforms-units` | must |
| `if`, names in a namespace such as `Key::W`, and scoped enum values such as `CursorMode::Locked` | `basics/programming-1` | must |
| Functions, and static member functions called as `Input::IsKeyDown` | `basics/programming-2` | must |
| The Game view and keyboard focus | `make/editor-tour` | must |

**Starting state.** The end state of `make/scripting-scene` (`startsFrom {"tutorial": "make/scripting-scene"}`): coins
placed by `CoinPlacer` and collected by the distance test. The page ends with the ball moved by the Move action
(by writing its position) and the Gameplay map (Move, Jump, Boost, Look) saved in the project; step 8's camera script
and step 9's Vehicle map are left out of the checkpoint.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `map` | map | - |
| `dead-zone` | Dead zone (use) | - |
| `composite` | Composite (use) | - |
| `input-action` | Input action (use) | - |
| `ref` | `$ref` (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-16 | should | stale-item | `make/lighting` (step 7), `make/physics` (steps 1, 7 and 8), `make/input` (step 4), `make/export` (step 8) | Labels the steps name differ at the pin. The sun's softness is **Angular Diameter** in the Inspector (stored as `ShadowSoftness`); the component is **Rigid Body**; the export's pruning box reads **Leave out unused assets**, not Prune; and Project Settings lists its pages under Physics (Collision Layers, Simulation, Timing), Input (Input Actions) and Rendering (Graphics Quality). | The steps use the pin's labels and paths (**Project Settings ▸ Physics ▸ Collision Layers**); `make/lighting` keeps "the sun's size" as the meaning of Angular Diameter (no words added). | `allocation/make-a.md:718`, `:1261-1262`, `:1280`, `:1148`, `:1707`; `StrataTests/Architecture/ComponentSchema.json:480`, `:2173`; `StrataEditor/src/UI/ExportDialog.cpp:311`; `Strata/src/Strata/Scene/ProjectCollisionLayers.cpp:59-60`; `Strata/src/Strata/Physics/PhysicsSimulationSettings.cpp:55-56`; `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:78-80`; `Strata/src/Strata/Input/InputActionSet.cpp:627-628`; `Strata/src/Strata/Renderer/RendererQuality.cpp:712-713` |
| critic-make-a-18 | should | missing-item | `make/input` (steps 1 and 5) | No step says which world direction a key or the Move action becomes. A Vector2 action gives +Y for forward (W, or the stick pushed up), while forward on the level, away from Basic 3D's camera, is -Z. A reader who writes `glm::vec3(move.x, 0.0f, move.y)` sends the ball toward the camera on W, the backwards mistake of `make/transforms-units`. | Step 1 moves the ball along -Z for W and +X for D; step 5 turns the action's vector into `glm::vec3(move.x, 0.0f, -move.y)`; each with one sentence that names the -Z forward of `make/transforms-units` (about 60 words). | `allocation/make-a.md:1141-1142`, `:1151-1152`, `:336`; `StrataScriptCore/Include/StrataScript/Input.h:402-403`; `.claude/skills/strata-make-a-game/SKILL.md:130`, `:180`; `StrataEditor/src/Editor/ProjectTemplates.cpp:31`, `:53-54` |
| critic-make-a-19 | should | order | `make/scenes-entities`; `make/project-coin-run` (step 5) | Coin Run's camera is framed only on `make/project-coin-run`. Until then the Game view shows Basic 3D's camera, 6 m back and 2 m up, aimed at the centre with a vertical view of 60 degrees. The ground nearest the camera, from about z = 4 to the wall at z = 10, almost a third of the 20 m level, and that wall are out of view, so the ball and coins leave the screen on `make/input` to `make/hud`. | `make/scenes-entities` adds a step after the walls: the Main Camera set high and tilted down over the level (for example Translation (0, 16, 13), Rotation (-55, 0, 0)), checked with the Game camera chip (F8); `make/project-coin-run` step 5 then only adjusts it (about 120 words). | `allocation/make-a.md:221-223`, `:1812`; `StrataEditor/src/Editor/ProjectTemplates.cpp:31`, `:51-55`; `Strata/src/Strata/Scene/Components.h:133`; `StrataEditor/src/Panels/ViewportPanel.cpp:460-461` |
