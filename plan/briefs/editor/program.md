# Brief: `editor/program`

| Field | Value |
| --- | --- |
| Title | The editor is a program: core, UI and host |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `world/systems`, `core/windows-events`, `core/layers-registries` |
| From | editor-core ch. 1 (`EditorContext`, the core and UI libraries, the frame order); home of what an editor is and why it is not the game |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/program` — The editor is a program: core, UI and host

**Covers.** The page starts from the problem a reader of `start/first-game` has met: a game needs levels, objects and
settings made by people who do not program, and the tool that makes them is not the game. The naive answer is a debug
menu inside the game, which breaks as soon as content must be saved, undone and shipped without the tool. The idea: an
editor is a separate program that links the same engine, holds the content being made, plays it in place, and is left
out of the exported game. The approaches follow with a table of their costs: in-engine editors that run the game code
(Unity, Unreal, Godot), external content tools with exporters, and data files edited by hand. The second idea is model
and view: UI code that changes state directly (simple, untestable) against a core without UI that the UI only draws and
calls. Strata's choice and its reason: `StrataEditorCore` holds all state and logic in `EditorContext`, `StrataEditorUI`
draws it and reaches the application only through `EditorHost`, so tests and agents drive the same core with no window.
`StrataEditor/CMakeLists.txt` builds the two as static libraries and the executable from one file,
`EditorApplication.cpp`; the editor's ImGui is a Tooling layer, so an exported game links neither ImGui nor the editor
(named here, taught on `editor-ui/immediate-mode`). The page then tours what `EditorContext` holds (project, asset manager, edited scene, running copy, selection, inspection
target, undo stack and the rest), each named in one line with the page that teaches it; the switches of
`EditorContextSpecification` that make tests deterministic; and one editor frame in order (`EditorLayer::OnUpdate`: the
last frame's time, `EditorContext::Update`, the command polls, automation, the command script, the panels), with the rule
that every command poll runs before the views render. It ends with the ways the editor runs: in a window; headless, by
one of two options (`--headless` runs without a window and keeps the graphics device, so captures still work; `--no-gpu`
drops the device and implies `--headless`; the word headless is `core/first-frame`'s and is linked); scripted with
`--commands`; and exit code 3 for a bad argument. The example is the editor of `start/first-game`, seen once as the
person sees it and once as three layers. The exercise runs the editor with a bad argument and reads its exit code, then
follows one frame of `EditorLayer::OnUpdate` with a debugger. Afterwards the reader can name the three layers, say which
one a change belongs in, and follow one editor frame from start to end.

**Leaves out.**

- What a command is and how it runs → `editor/commands`
- How the editor is drawn: host, layer, docking and panels → `editor-ui/shell`
- Why the editor's UI is immediate mode → `editor-ui/immediate-mode`
- Notifications, their model and their drawing → `editor-ui/status`
- The table of every command-line option → `reference/editor`
- Headless as a word, and the application's flag → `core/first-frame`
- The tour of the editor for game makers → `make/editor-tour`

**Fit.** `over`: about 4,050 words against M (3,000). Counted again from the sections, with the exercise (D27) and the
editor's two options of headless: two concepts from zero with the approaches' table, the tour of `EditorContext`, one
excerpt and three figures reach M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:290` | concept | home | What an editor is and why it is a separate program from the game; the approaches and their costs |
| `editor-core:295` | concept | home | Model and view: a core without UI that the UI only draws and calls |
| `editor-core:39-43` | feature | home | The core/UI split, `EditorContext`, `EditorContextSpecification`, the per-frame update and the frame order |
| `editor-core:44-45` | feature | home | Selection (ordered, with a set and a version) and the inspection target as state of the core |
| `editor-core:48` | feature | home | The ways the editor runs (window, headless, scripted) and exit code 3 on a bad argument; the table is `reference/editor`'s |
| `editor-core:449` | code | home | `StrataEditor/src/EditorLayer.cpp:614-668`: the editor's frame order; the function runs on to line 701 (the last frame and quitting) |
| `editor-core:461` | figure | home | The layer stack: StrataEditor, StrataEditorUI, StrataEditorCore, the engine |
| `editor-core:467` | figure | home | The editor frame timeline, marking that command polls run before the views render |
| `editor-core:511` | figure | home | The whole editor with its panels docked, to name the parts once |
| `editor-core:648-650` | term | home | Editor core (`StrataEditorCore`), `EditorContext`, `EditorHost` |
| `editor-ui:747` | term | home | Editor host (`EditorHost`): what the editor's UI needs from the application; one entry with `editor-core:650`, as passed by `editor-ui` |
| `editor-core:739` | term | use | Headless, one entry of `core/first-frame`; the page states the editor's two options: `--headless` keeps the graphics device, `--no-gpu` drops it and implies `--headless` |
| `new:47` | erratum | home | `plan/inventory/editor-core.md:739` defines headless as running without a window or GPU (`--no-gpu`); these are two options, and the page states both: `--headless` runs without a window and keeps the graphics device, so captures still work; `--no-gpu` runs without a graphics device and implies `--headless` (process.md's table of errata, kind `inventory`). Evidence: `StrataEditor/src/EditorApplication.cpp:70-71`, `:323-324` |
| `new:48` | hands-on | home | Exercise (D27, done): run the editor with an unknown argument and read exit code 3 in the terminal; then, with a breakpoint in `EditorLayer::OnUpdate`, follow one frame of a project and name the line where the command polls run before the panels draw. Evidence: `StrataEditor/src/EditorApplication.cpp:272-281`; `Strata/src/Strata/Core/CommandLineOptions.h:27`; `StrataEditor/src/EditorLayer.cpp:614-668` |
| `editor-ui:284` | concept | home | What an editor is and why it is not the game, as the UI survey states it; one home with `editor-core:290`; the Tooling layers that keep ImGui out of games are named and linked to `editor-ui/immediate-mode` |
| `editor-ui:49` | feature | home | The two libraries and the executable of one file in `StrataEditor/CMakeLists.txt`; one home with `editor-core:39` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor as a person uses it to make a first game | `start/first-game` | must |
| What a game engine is; one frame from start to finish | `start/what-an-engine-is` | helps |
| The frame loop of an application | `core/frame-loop` | must |
| Windows, events and application layers | `core/windows-events` | must |
| The layer table, the composition root and no tooling in games | `core/layers-registries` | must |
| Scene systems and the scene's update | `world/systems` | must |
| Static libraries, executables and linking | `basics/build` | helps |
| Console and GUI programs, exit codes | `core/platform` | helps |
| Breakpoints in a debugger attached to the engine | `core/debugging` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `editorcontext` | `EditorContext` | - |
| `editorhost` | `EditorHost` | Editor host, EditorHost |
| `editor-core` | Editor core | StrataEditorCore |
