# Critique: the game maker's path (key `game-maker`)

Lens: track G as a person who has never programmed and wants to finish a game. Read: all nine plan files,
`inventory/gamedev.md` in full, the other inventories' proposed chapters (section 8) where they feed part `make`,
`research/curricula.md` sections 1.13 and 5, `research/captures.md` sections 1.3 and 5, `Docs/Manual/` (all ten
files' headings, Scripting and GameView in full), `Docs/Releases/PackageReadme.md`, the skill `strata-make-a-game`, the
samples' `Samples.json` and READMEs (Tetris, ThirdPerson) and asset folders, and these engine files at `822a7a46`:
`StrataEditor/src/Editor/ScriptToolchain.h/.cpp`, `EditorLayer.cpp` (menus), `Panels/ContentBrowserPanel.cpp`,
`Panels/ActivityPanel.cpp`, `Editor/EditorAnimationCommands.cpp`, `Editor/GameExport.cpp`.

Word counts below use the plan's sizes (S 1,500, M 3,000, L 5,000, XL 8,000).

## 1. The walk: install to shipped game

| # | What the reader must do | Page in the plan | Taught before it is needed? |
| --- | --- | --- | --- |
| 1 | Learn that gameplay is C++ only (no visual scripting) and that an AI agent can help | `start/welcome` (door text), `appendix/not-in-strata` | Not stated at the G door; the appendix is the only place |
| 2 | Use a terminal (macOS `xattr`, Linux `apt`, `StrataCLI`, `<Game> --headless`, PowerShell `| Write-Output`) | none | **No** |
| 3 | Download, unblock, start the editor; GPU and driver | `start/install` (H, S) | Yes, but the row also carries "Building Strata (short form)" |
| 4 | Install the C++ build tools (VS 2022 17.10+/2026 "Desktop development with C++", or g++/CMake/Ninja, or Xcode CLT + CMake) and a code editor | none named | **No**: needed by step 5 already |
| 5 | Open a copy of a sample and press Play | `start/first-game` | Play builds the copy's scripts first: fails without step 4 |
| 6 | New project from Basic 3D, place, play, stop | `start/first-game` | Yes (uses the editor before `make/editor-tour`) |
| 7 | Learn the editor | `make/editor-tour` (T, M) | Yes; M for 19 feature rows of gamedev 1.3 |
| 8 | Know the project's files, what to back up, never edit or move by hand | none (`world/projects-settings` is E internals) | **No** |
| 9 | Scene, transforms, assets, materials, prefabs | `make/scenes-entities` … `make/prefabs` | Yes; no page says where the reader gets a model, sound or font |
| 10 | Light the scene | `make/lighting` (W8), `make/reflections-gi` (W8), `make/look` | Yes, but three L pages (two waiting for 0.8.0) stand before any code |
| 11 | Learn to program | `make/cpp-for-scripts` (C, L) | Before the reader can run any code |
| 12 | Vector math for movement and cameras (normalize, cross, atan2, radians, `1 - exp(-k dt)`) | none at G level (`basics/math-vectors` is B/E, XL) | **No** |
| 13 | First script; code editor, IntelliSense, build errors | `make/first-script`; IDE and toolchains in `make/script-builds` six pages later | Partly |
| 14 | Debug a script (Console, Problems, logs, debugger, pause and step) | `make/play-test-debug`, 16 pages after the first script | **No** |
| 15 | Script API per topic | `make/gameplay-1..3` before `make/input`, `physics`, `sound`, `animation`, `ui`, `levels-saves` | **No**: their own prerequisites come after them |
| 16 | Features with no UI (create an animation controller, many instances at once, input sequences, command scripts) | `automation/outside` (E part) | **No** G page |
| 17 | Plan a game: core loop, scope, prototype, playtest | none (curricula 1.13 "[gap]") | **No** |
| 18 | Export, identity, start scene | `make/export` (page 29 of `make`) | Yes |
| 19 | Give the game to players (unsigned executables, notices, credits of CC-BY assets) | part of `make/export`? (not named) | Unclear |
| 20 | First finished game | `make/project-coin-run`, page 30 of `make`, after about 117,000 words | Too late |
| 21 | Move the project to a new Strata release | none | **No** |

## 2. Findings (most severe first)

### F1 — blocker — `start/install` and `start/first-game` (outline-1.md rows 20-21): the C++ build tools are missing, and the first success depends on them

**Problem.** Opening a sample and pressing Play builds the sample's scripts: samples are opened as copies without
`.strata` (gamedev 1.2, `ProjectSamples.h`), and `Docs/Releases/PackageReadme.md` ("Make a game", step 1) says "Press
Play in a sample: it builds the sample's scripts first". A fresh Windows machine without Visual Studio gets "Building
scripts needs Visual Studio's C++ tools: install Visual Studio 2022 (17.10 or later) or 2026 with the "Desktop
development with C++" workload…" (`ScriptToolchain.cpp` L272-276). Installing that workload alone takes longer than
the "30 minutes" the title of `start/first-game` promises. The `start/install` row is S (1,500 words) and names
"build-test Building Strata (short form)": source builds are an engine builder's path, while the release download,
three operating systems' first-start steps (Unblock/SmartScreen, `xattr`, MoltenVK, Linux packages) and the script
toolchain for three systems already fill an M page.

**Proposal.** Replace row 20 by
`| start/install | Installing Strata and the C++ build tools | H | M | gamedev 1.1 (release archives, requirements, first start, script toolchain discovery, logs); PackageReadme "Requirements", "First start"; Manual/Scripting "Where builds happen" |`,
with OS tabs, a code-editor recommendation (VS Code or Visual Studio Community) and a final check (open the
launcher; `script.status` names the toolchain, or Build Scripts on the generated `Spinner.cpp`). Move "Building
Strata (short form)" to `start/first-engine-change`. In `start/first-game` state that the 30 minutes start after the
install, and order it so the first result is visible within 5 minutes (research/curricula.md 5.2: "a tutorial with a
visible result in the first 5 minutes"): open the Tetris copy and play, then Basic 3D with falling bodies (no code),
then attach the generated `Spinner`.

### F2 — blocker — Part `make` order (outline-1.md rows 29-61): the first finished game comes after 29 pages and about 117,000 words

**Problem.** Before `make/project-coin-run` a G reader reads 14 M and 15 L pages (about 117,000 words), including
three pages of API listings (`gameplay-1..3`), `recipes`, `reflections-gi`, `look`, `large-worlds`,
`big-scenes-fast`, none of which Coin Run needs. All three projects sit at the end. The research the plan rests on
recommends the opposite: "Project chapters interleaved: a first game, a mid-size game, a capstone"
(research/curricula.md 5.2, Part II). A beginner who has to read a book-length text before finishing anything stops
before the end, so for the reader the owner names ("people who have no idea how to implement … a game") the track fails.
The W8 rows (`make/lighting`, `make/reflections-gi`) also stand on the core path, so the start of the G track cannot be
finished in phase A.

**Proposal.** Reorder `make` in three blocks, each ending in a project (new or changed rows marked; details in F3-F17):

| Block | Rows in order |
| --- | --- |
| A, "Your first finished game" (no W8 page) | `editor-tour` (L), *`project-files`* (S, new), `scenes-entities`, `transforms-units`, `assets`, `materials`, `prefabs`, *`lighting`* (stable half, F9), `first-script`, *`cpp-1`*, *`cpp-2`*, *`gameplay-math`* (new), `script-loop`, *`scripting-scene`* (was `gameplay-1`), `play-test-debug` (moved), `input`, `physics`, `sound`, *`ui`* (HUD half), `export`, *`designing-a-game`* (new), `project-coin-run` |
| B, "Bigger games" | `recipes` (M), *`menus`* (UI's second half), `levels-saves`, *`commands`* (new, F6), `automated-playtests`, `project-tetris`, `characters-cameras`, `animation`, `project-platformer` |
| C, "Polish, scale and help" | *`lamps`* (W8), `reflections-gi` (W8), `look`, *`quality`*, `big-scenes-fast`, `large-worlds`, *`with-an-agent`*, `script-builds`, `samples` |

Coin Run then is page 22, after about 75,000 words on 21 pages, and every page it needs is in front of it.

### F3 — major — `make/gameplay-1`, `-2`, `-3` (rows 41-43) come before the pages their own prerequisites name, and teach the same API those pages teach

**Problem.** The scripting inventory (section 8, chapters 5 and 6) gives their prerequisites: part 2 needs "the
Physics, Audio, Animation chapters"; part 3 needs "Game UI", "Input actions", "Quality settings". In the plan all three
come before `make/input`, `physics`, `characters-cameras`, `animation`, `sound`, `ui` and `levels-saves`. Their content
(physics, characters, audio, animation from scripts; input and rebinding with capture; UI callbacks; game flow; saves;
window; graphics options; worlds) is what those use pages also need, so either it is taught twice (against the one-home
rule) or the topic pages are left without their scripting half. A page titled "Gameplay API II" also tells a beginner
nothing about what it is for. `make/recipes` (row 44) repeats the samples' FollowCamera, Coin and Tetris board, which
are also in `characters-cameras` and the projects.

**Proposal.** Delete rows 42-43 and hand their allocation to the topic pages (input actions, devices and rebinding →
`make/input`; bodies, contacts, queries, controllers, drawn poses → `make/physics`/`make/characters-cameras`; audio →
`make/sound`; animator → `make/animation`; UI callbacks → `make/menus`; flow, saves, window, players' options →
`make/levels-saves`; World → `make/large-worlds`); the full listing is `reference/script-api`. Rename row 41
`| make/scripting-scene | Changing the scene from a script: entities, components, spawning and assets | H | L | scripting "Gameplay API 1" |`
and place it after `make/script-loop`. Shrink row 44 to
`| make/recipes | Helpers and patterns for game code | H | M | scripting "Building blocks and recipes" (Random, Timer, KeyRepeat, Motion; show/hide instead of create/destroy; cooldowns; state machines in code) |`.

### F4 — major — book.md "One home per concept" (book.md L56-83): the homes of what a game maker needs are engine-builder internals pages

**Problem.** book.md L27-28 says "A game maker never has to read internals", but the table sends `make` to internals
homes: fixed step → `core/time`/`world/systems`, interpolation → `world/interpolation`, stepping → `editor/stepping`,
simulated input → `input/simulated`, command scripts → `editor/command-scripts`, journal → `automation/journal`, debug
views → `indirect/measuring-light` (part prerequisites `light/brdf`, `basics/math-light`), residency → `assets/residency`,
sub-scenes → `world/sub-scenes`. Under the rule "every other page says one sentence and links", `make/automated-playtests`
would hold one sentence about `expect`/`until`/`bind`, yet the Tetris project needs the reader to write such a script
(gamedev G9). The inventories marked these chapters "both" because they have a game maker's half (editor-core 10 and 12,
scene-ecs 5, physics 2 and 10, render-direct 14, render-indirect 12). The plan already separates "use" from "data
model" for prefabs (L62) and launcher (L81), but for no other concept.

**Proposal.** Add a rule under the table: "A concept a game maker acts on has a *use home* in `make` that teaches
everything a maker does with it; its E home explains the mechanism and links back." Then add the use homes:

| Concept | Use home (add) |
| --- | --- |
| Fixed step, frame vs fixed updates, time scale, FixedRate | `make/script-loop` |
| Interpolation for game code (`GetDrawnPosition` in `OnLateUpdate`, `ResetInterpolation`, platforms in `OnFixedUpdate`) | `make/characters-cameras` |
| Pausing and stepping | `make/play-test-debug` |
| Simulated input, `input.sequence`, command scripts, `expect`/`until`/`bind`, session replay | `make/automated-playtests` |
| Activity journal (panel, Copy as script, Re-run, Undo to here) | `make/with-an-agent` |
| Light units, exposure, debug views `luminance`/`albedo` | `make/lighting` |
| Asking for assets early (`RequestLoad`, `Instantiate` never waits) | `make/scripting-scene` |
| Additive loads, loading scenes | `make/levels-saves` |
| Autosave and recovery, undo of asset deletes | `make/editor-tour` |
| Export (use) vs `worlds/export`, `assets/packs-export` (mechanism) | `make/export` |
| Players' graphics options (`Graphics::`) | `make/quality` (today claimed by `make/look`, `make/levels-saves`, `image/quality-settings`) |
| Project folder and files | `make/project-files` |

### F5 — major — How-to pages a game maker needs sit in engine-builder parts, where track G never goes

**Problem.** Parts carry one track each (book.md parts table), so these G-relevant pages are off the G path:
`animation/editor` (outline-3.md L96: controller tables, previews, edit pose; animation inventory ch. 13 "internals +
tutorial, both"), `physics/tuning` (outline-3.md L77: `Physics.Simulation`, `physics.stats`; the Physics Playground
"pile that never sleeps" lesson), `ui/testing` (outline-4.md L32: `ui.create`, `ui.layout`, `ui.hitTest`,
`input.click`), `worlds/measuring` (outline-4.md L47: `--perf-log` of a shipped game), `indirect/measuring-light`
(outline-3.md L41), `automation/outside` (outline-4.md L96: "game developers; tutorial" in automation inventory ch. 1).
`input/rebinding` "(the code side)" (outline-3.md L122) splits audio-input ch. 12, which the inventory wrote as one game
tutorial including the rebinding menu: the script calls (`BeginBindingCapture`, `PollBindingCapture`,
`SetActionBindings`, `SaveBindings`) are a maker's code, not engine internals.

**Proposal.** Add a Track column to every outline table (and give site.md's track navigation this column). Fold the
how-to halves into `make`: `animation/editor` → `make/animation`; `physics/tuning` → `make/physics` (keep an E page only
for the solver-side tuning); `ui/testing` → `make/automated-playtests`; `worlds/measuring` → `make/big-scenes-fast`
(rename "Making your game run fast": Performance panel, `renderStats`, quality costs, `--perf-log`); the debug-view use
→ `make/lighting`; `automation/outside` → `make/commands` (F6). Reword `input/rebinding` as "Players' bindings inside
the engine (the bindings file, capture in `InputActions`)" and keep the rebinding menu in `make/input`.

### F6 — major — No G page teaches the terminal or how to run an editor command, yet some features have no UI

**Problem.** The editor has no in-editor way to run an arbitrary command: the menus (`EditorLayer.cpp` L1460-1606) and
the Activity panel (`ActivityPanel.cpp` L372-397: Copy as script, Re-run, Undo to here) offer none. Some steps of the G
path exist only as commands: creating an animation controller (`animation.createController`,
`EditorAnimationCommands.cpp` L153; the Content Browser's New menu holds Folder, Material, World, Script...,
`ContentBrowserPanel.cpp` L568-578), placing many instances (`prefab.instantiate {instances}`), `input.sequence`,
command scripts (`StrataEditor --commands … --quit-after-commands`), headless checks of an exported game
(`<Game> --headless --frames 600`). The project-platformer (gamedev G11: "made with `animation.createController`")
cannot be done from the UI. The terminal itself is needed from the install on (macOS `xattr -dr
com.apple.quarantine`, Linux `apt install`; PowerShell waits for windowed programs only with `| Write-Output`). The
only teaching of `StrataCLI` is `automation/outside`, in an E part.

**Proposal.** Add `| start/terminal | Using a terminal | H | S | new; PackageReadme "First start" (PowerShell, Terminal: folders, running a program with arguments, quoting paths, `| Write-Output`) |`
after `start/install`, and
`| make/commands | Running editor commands yourself: StrataCLI and command scripts | H | M | automation "Driving the editor from outside" (use side); skill make-a-game §1 |`
before `make/automated-playtests` and `make/animation`. Add to style.md's tutorial shape: "a step with no UI says so
and gives the command; its page lists `make/commands` as a prerequisite". The allocator should list every command-only
step of the G pages, so these limits are checked.

### F7 — major — `make/cpp-for-scripts` (row 38): one concept page has to teach programming from zero, before the reader can run any code, and nothing teaches the math the projects use

**Problem.** The reader is "maybe no programming" (book.md L17), and the only programming on track G is one L page of
kind *concept*. style.md's concept shape (problem → naive answer → approaches engines use → Strata's choice) does not fit
learning to program, and the page sits before `make/first-script`, so none of its code can be run. The projects need
much more: Tetris is 829 lines (gamedev 1.20) with classes, arrays, enums, seeded randomness and a header/source split;
the controllers in the skill (L158-256) use `glm::normalize`, `glm::cross`, `std::atan2`, `glm::radians`,
`glm::quatLookAt` and `1 - exp(-k dt)` smoothing; `ThirdPersonPlayer.cpp` uses `std::remainder` (gamedev code #19);
module state across scene loads is namespace-scope state (#21). `make/transforms-units` explains the Inspector's
numbers, not vector operations. The research proposed an on-ramp page "The math you need for your first game"
(curricula.md 5.3), which the plan left out.

**Proposal.** Put `make/first-script` before the C++ pages, so the script module and `Log::Info` in the Console are the
reader's playground, and replace row 38 with three tutorials whose sketches run as scripts:
`| make/cpp-1 | Programming from zero, inside a script | T | L | gamedev concept 11; values, types, if, loops, functions, arrays and std::vector, reading compile errors |`,
`| make/cpp-2 | Classes, fields and callbacks: the C++ of a script | T | M | gamedev concept 11; Script.h L30-110; headers and sources, override, enums, namespaces, module state |`,
`| make/gameplay-math | The math of moving things: vectors, directions, angles and smoothing | T | M | new; skill make-a-game L158-256, FollowCamera.cpp L43-101, Playground.cpp L183-207 |`.
The B track can then send never-programmed readers here instead of `basics/computer` (caches and heaps) first. State
on `start/welcome`'s game-maker door that game logic is C++ (no visual scripting, book.md L98), and that an agent can
help (F16).

### F8 — major — Tools a scripting reader needs from the first build arrive late (rows 45 and 55)

**Problem.** `make/script-builds` holds "toolchains, IDE presets, where builds go, … debugging with a debugger"
(scripting inventory ch. 8) and comes six pages after the first script. `make/play-test-debug` (Console, Problems,
logs, Pause/Step, edits while playing) comes 16 pages after it. Manual/Scripting puts "When the build fails", "Your code
editor", "IntelliSense" and "When a script crashes" directly after "Attach it and play".

**Proposal.** Put the external editor, the `strata` CMake preset and IntelliSense, the Problems panel and the
crash toast in `make/first-script` (the scripting inventory's ch. 2 already has "crash on purpose, the Problems
panel"). Move `make/play-test-debug` to directly after `make/scripting-scene` and give it the debugger attach. Keep
`make/script-builds` in block C for building outside the editor, other platforms' compilers and warnings, long paths,
and shared libraries next to the module.

### F9 — major — `make/lighting` (row 35) puts W8 content on the core path; `make/reflections-gi` and `make/look` stand before the first script

**Problem.** `make/lighting` is W8 only for local and area lights; the sun, sky sources and presets, fog, sun shadows,
exposure and preview lighting date from 0.6.0-0.7.0 (gamedev 1.8). With the whole page waiting, block A cannot be
finished, reviewed and stamped in phase A. `make/reflections-gi` (W8, L) and `make/look` (L) are polish a first game
does not need; the inventory's own exercise G16 (a day/night script driving the sun) needs scripts, which come after
these pages in the plan's order.

**Proposal.** Split row 35:
`| make/lighting | Lighting a scene: sun, sky and exposure | T | L | gamedev 1.8 (units, sky sources, presets, fog, sun shadows, exposure, preview lighting, debug views luminance/albedo); render-direct "Lighting a scene in the editor" (outdoor half) |`
(not W8, in block A) and
`| make/lamps | Lamps, torches and area lights | T | M | render-direct (indoor half), gamedev 1.8 Source Radius, local shadows · W8 |`
(block C, beside `make/reflections-gi`). Move `make/look` to block C.

### F10 — major — Overloaded pages in `make`

**Problem and evidence.**
- `make/editor-tour` (row 29) is M, but editor-ui's proposal was "L; ~18 screenshots", and gamedev 1.3 lists 19 feature
  rows (13 panels, menus, chips, pills, gizmos, undo, recovery, placement, preferences).
- `make/look` (row 37) absorbs Manual/Camera (14.4 KB), Manual/AntiAliasing (12.2 KB) and Manual/Graphics (9.6 KB),
  about 36 KB of reference prose that a beginner's tutorial needs at least twice the words to explain, in one L page.
  Its source tutorial (render-image ch. 12) also assumes the E chapters 2-7 and 9.
- `make/ui` (row 51) merges gameui's "Making menus and HUDs" (L, ~10 screenshots) and "Widgets, events and scripts" (M).
- `make/input` (row 46) is M for device input, the Input Actions page, composites, dead zones, maps, cursor modes and a
  rebinding menu with capture (audio-input ch. 12 alone was M, before the device half of `gameplay-3` came to it).
- `make/automated-playtests` (row 56) is M for gamedev 1.17 and 1.19 plus automation's "Connecting an AI agent"
  (tutorial) and "Making a game as an agent" (tutorial, L): two subjects in one page.

**Proposal.** `make/editor-tour` → L. Split `make/look` into
`| make/look | The camera's image | T | L | render-image ch. 12; Manual/Camera |` and
`| make/quality | Anti-aliasing, graphics quality and players' options | H | M | Manual/AntiAliasing, Manual/Graphics (presets, costs, quality chip, `--quality`, players' options, why no render scale) |`.
Split `make/ui` into `| make/ui | HUDs: canvases, anchors, text and images | T | M | gameui ch. 2 |` (block A) and
`| make/menus | Menus that work: buttons, sliders, focus, pause and main menus | T | L | gameui ch. 3, ch. 2 (main menu scene) |`
(block B). `make/input` → L. Split row 56 into `make/automated-playtests` (H M: command scripts, `input.sequence`,
`ui.*` checks, replay, the Tetris-style regression) and
`| make/with-an-agent | Making a game with an AI agent | H | M | automation "Connecting an AI agent", "Making a game as an agent"; launcher's agent card; Activity panel |`.

### F11 — major — The three projects: Coin Run and the platformer teach almost the same things, and Coin Run needs too much

**Problem.** Gamedev G8 defines Coin Run as a first-person `CharacterController` player with the skill's mouse-look
script, coins as trigger prefabs, HUD, sound, win panel, `Game::ReloadScene` and export. G11 (the platformer) again has
a character controller, coins/jump-pad triggers, HUD, sounds and restart, plus animation, a follow camera and menus.
Most of what Coin Run teaches comes back in the platformer, and Coin Run needs `make/characters-cameras` (L), Euler
angles in radians, cursor lock and Shift+F1 before a reader has finished anything. None of the three projects uses
collision layers, raycasts from the cursor, contact strength or `OnFixedUpdate` forces, which the Physics Playground
teaches (gamedev 1.20, G12). The templates are `empty` and `basic3d` only; Basic 3D's 20×20 ground with a collider whose
top is y = 0 (`ProjectTemplates.cpp` L49-95) is an arena that is already finished.

**Proposal.** Make Coin Run a rolling-ball game on the Basic 3D ground: a dynamic sphere driven by an input action, with
force applied in `OnFixedUpdate` (gamedev pitfall 4), a camera that follows its drawn position, spinning trigger coins
as a prefab, a HUD, a coin sound, a win panel, a restart and an export. It needs only block-A pages, and it teaches the
fixed-step rule every later game relies on. Keep Tetris (pure programming, determinism, a regression with an exact
score; it needs `make/automated-playtests` and `make/recipes` before it, as F2 orders them) and the platformer as the
capstone (characters, animation through `make/commands`, follow camera, menus, several scenes, saves, pruned export).
Make G12 (the cursor-ray physics toy) the closing exercise of `make/physics`. Change the "From" of row 58 to
`gamedev G8 (rolling-ball variant); skill make-a-game §4-8`.

### F12 — major — Tutorials have no source assets and no starting points (pipelines.md L106-116; outline-1.md L8)

**Problem.** `make/assets`, `make/sound`, `make/animation`, `make/large-worlds` and the projects need files to import
(a model, a texture, a coin sound, a font, a rigged character, a kit), and the plan never says where the reader gets
them. The skill generates WAVs with the agent's own scripts, which a beginner cannot do. `tools/tutorials.py` starts "a
new project from the template the page names" (pipelines.md L111), so each chapter starts from nothing, or else the
pages are not connected at all. research/captures.md section 5 asked for "a step-by-step tutorial game whose stages are
saved scenes (each chapter's starting point)", and the plan dropped it. The projects are L and XL pages that the reader
works through over hours, and outline-1.md L8 forbids splitting a page ("never into several pages"), so a reader who
breaks something in step 20 of 40 has nowhere to restart.

**Proposal.** In pipelines.md: (a) tutorial assets come from the release's own `Samples/*/Assets/` (CC0, already
credited: e.g. `ThirdPerson/Assets/Sounds/Coin.ogg`, the Quaternius robot, the Kenney kits and UI pack), or from a
small `tutorials/assets/` pack with a `CREDITS.md`; every page names the file it imports. (b) A tutorial script may
declare `"startsFrom": "<part>/<chapter>#<section>"`, and the tool chains the stamps. (c) The tool publishes each
project's state at every section end (and each block-A chapter's end) as a downloadable zip, linked from the page
("start here if you skipped"). In outline-1.md L8 allow project tutorials to be split into numbered pages, or require
sections that each end in a playable, downloadable state.

### F13 — major — The UI path of G tutorials is never checked (pipelines.md L113, style.md L64-66, process.md L46)

**Problem.** For a game maker the UI steps are the tutorial; the command tab is secondary. The tool runs only the
commands. "The reviewer walks them by hand in a windowed editor" (pipelines.md L113), but every reviewer is an Opus
agent that reads code and writes text (process.md L97), and the novice reviewer gets "no code" and no editor. Menu
names and labels come from source strings (gamedev section 9: "No editor run… exact UI labels come from source
strings"). Drag-and-drop steps (drop to import, drag to the Content Browser to make a prefab, the placement ghost) can
be neither simulated nor captured (captures.md section 5, gap 7). The samples were all made through commands, so for a
person working in the UI this engine path has never been walked in a tutorial.

**Proposal.** (a) Add a label check to `tools/tutorials.py`: every UI string a page names (**Menu ▸ Item**, button and
property labels) must occur in `StrataEditor/src` at the pin, the same way excerpts are checked. (b) Add to process
phase B (after step 9): "The UI path of every G tutorial is walked once in a windowed editor from a release package, by
the owner or an agent with control of the screen; each step's screenshot is taken then. Steps that cannot be walked are
marked command-only." (c) List in each figure manifest the editor pictures only a person can take.

### F14 — major — Nothing tests the track as a whole, though the definition of done claims it (process.md L122)

**Problem.** "A reader can go from *Start here* to a finished game on track G … without leaving the book" is a
condition of done, but no stage checks it: tutorials are run one by one from templates, and reviewers read single pages.
The gaps of section 1 (toolchain, terminal, files, command-only steps) are the kind of thing that only a walk through
the whole track finds.

**Proposal.** Add to process.md phase B, step 10: "**Track G walk.** A fresh agent, with only the published book, a
release package and a user profile without Strata data, follows track G from `start/install` to the exported Coin Run
and then to the platformer, using the UI where it can. It logs every place where it had to guess or leave the book. The
planner fixes these before release." Do the same for track E up to `start/first-engine-change` and one tutorial.

### F15 — major — The pilot (process.md L69-70) tests no project and no UI-heavy tutorial

**Problem.** `make/first-script` is a small M tutorial. The parts of the tutorial pipeline most likely to need a
redesign (assets, chained starting points, checkpoints, the UI/command tabs on every step, script files built during
the run, steps with no UI) only show up in a project page, and those are written in wave 2, after the tools are fixed.

**Proposal.** Add `make/project-coin-run` (or swap `make/first-script` for it) to the pilot, and stamp its run before
the tools are frozen.

### F16 — minor — The AI-agent path, a main way the engine is meant to be used, sits on page 28 of `make`

**Problem.** The launcher shows "Connect an AI agent" with the exact `claude mcp add` line (gamedev 1.2); all five
samples were "made by an AI agent through the editor alone" (Samples READMEs); the release ships three skills.
For a game maker who does not program, an agent writing the C++ while the reader directs, reviews and undoes is a real
way to finish a game. The plan merges it into `make/automated-playtests` near the end.

**Proposal.** Make it `make/with-an-agent` (F10) and name it on `start/welcome`'s game-maker door ("make it yourself,
or with an agent: both use the same editor") and in `start/first-game`'s closing "what next". The page teaches how to
review what an agent did (Activity panel, Undo to here, `editor.activity.export`).

### F17 — minor — No home for "planning a game" (research/curricula.md 1.13: "[gap] … the brief says some readers never made a game")

**Proposal.** Add `| make/designing-a-game | Planning a small game: the core loop, scope, prototype, playtest | C | M | curricula 1.13; gamedev concept 23 (testing), the samples' READMEs as examples |`
in front of `make/project-coin-run`; each project's page opens with its one-paragraph design (loop, win, lose, scope).

### F18 — minor — Part `start` (outline-1.md rows 18-23) has no tracks per page; `start/first-engine-change` is on track G

**Problem.** Part 0 is "all" (book.md parts table), so track G's "next" after `start/first-game` leads to building
the engine from source and writing a test.

**Proposal.** Add the Track column (F5): `welcome`, `how-to-read`, `install`, `terminal`, `first-game`,
`what-an-engine-is`: G, E; `first-engine-change`: E. Put `what-an-engine-is` before `first-engine-change`.

### F19 — minor — No home for the project's files, backups, version control or moving to a new release

**Problem.** Gamedev concept 3 ("Projects and files": `.stproj`, `Assets/` with `.meta`, `Scripts/`, `.strata/`
cache, never edit or move by hand), diagram 2 (project folder anatomy), the generated `.gitignore`, and project
migration (gamedev 1.2: 0.5.0 projects move to v3; the 0.6.0 and 0.7.0 release notes have "Upgrading" sections) appear
in no G row; `world/projects-settings` is E internals.

**Proposal.** Add `| make/project-files | Your project's files: what to keep, back up and never touch | H | S | gamedev 1.2 (project file, creation, migration), concept 3, diagram 2, pitfall 1; release notes "Upgrading" |`
after `make/editor-tour`.

### F20 — minor — Asset licenses and what a shipped game owes have no named home

**Problem.** Gamedev concept 25 and pitfall 27 (CC0 or CC-BY only, credited) are a maker's duty. Export ships
`ThirdPartyNotices.md` by itself (`GameExport.cpp` L32, L200-201, L707), but the attributions that CC-BY assets ask
for must appear in the game. Unsigned executables also affect the game's players, not only its maker (PackageReadme
"First start").

**Proposal.** In the allocation: licenses, where to find CC0 assets (Kenney, Poly Haven, Quaternius, ambientCG, as the
samples use) and a `CREDITS.md` → `make/assets`; a credits screen, the notices file, and what players see on first
start (SmartScreen, quarantine, the `.desktop` file) → `make/export` under a section "Giving your game to players".

### F21 — minor — style.md L52-53: "at least one [exercise] changes or runs real code" cannot hold for G pages before the first script

**Proposal.** Reword: "at least one changes or runs real code (for G pages before `make/first-script`: does something in
the editor and checks its result, or runs a command)".

### F22 — minor — Game makers coming from other engines have no entry

**Problem.** research/curricula.md 5.2 (Part 0) and the Unreal notes recommend "Coming from Unity, Unreal or Godot"
mapping pages; the plan has none, though such readers are a large share of game makers.

**Proposal.** Add `| start/coming-from | Coming from Unity, Unreal or Godot | R | M | curricula 5.2; gamedev concepts 4, 7 (GameObject vs entity, prefab variants vs Strata's overrides, Blueprints vs C++ scripts) |`
to Part 0 (G).

### F23 — minor — `make/levels-saves` (row 52): "settings" is ambiguous and the page is a mix

**Problem.** "Settings" could mean the editor's Project Settings window or the players' settings menu. The page holds
scene switching, loading scenes and progress, additive loads, passing state between scenes, save files, window modes,
volume, and players' graphics options (also claimed by `make/look` and `image/quality-settings`, F4).

**Proposal.** Retitle "Levels, loading screens and save files" and allocate the players' settings menu (volume,
window, vsync, graphics row) to `make/menus`, with `make/quality` as the home of `Graphics::`.

## 3. What I did not check

- Whether the allocation step would fill the gaps on its own: I judged the outline rows and their "From" columns,
  which the allocator follows.
- The UI labels named here (menu items, buttons) were read from source, not seen in a running editor (as required).
- How track B is laid out in detail, the E parts beyond where they hide game-maker content, the site and the budgets.
