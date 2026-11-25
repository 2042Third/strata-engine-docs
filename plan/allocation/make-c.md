# Allocation: make-c

## `make/designing-a-game` — Planning a small game: the core loop, scope, prototype and playtest

**Covers.** The page opens with a problem every reader of block C meets: after Coin Run and the toolbox of block B,
the reader wants to make "a real game", and the first idea is usually far too big. The reader lists what a large
adventure would need and compares the list with the two games block C builds: Tetris is three source files of 829
lines and one scene; Sky Islands is 18 source files of 1,720 lines and three scenes. The naive answer, building
everything at once from a long document, breaks there: nothing is playable for weeks, nobody knows whether it is fun,
and nothing can be cut. The idea follows: the **core loop**, the short cycle the player repeats every few seconds,
shown as a diagram for Tetris (a piece falls, the player moves and turns it, it locks, rows clear, the score rises,
gravity speeds up) and for Sky Islands (run, jump, collect coins, reach a checkpoint, finish faster). Then the
approaches, each brought in by the flaw of the one before: a design document first, a paper prototype, a grey box
built in the editor from built-in meshes, and a vertical slice, ending with a table of what each costs, what it tests
and who uses it. **Scope** is taught as a cut list (must, should, could), with the platformer's own cuts as the example
(lanterns, probes, the Graphics row and the attract mode are "could").

Strata's part is the samples' way of working, stated once in a `:::why` aside: design the code so that tools can check
it, with the rules in a plain class, randomness from a seed field, tuning as fields that change while the game plays,
and one log line per event (`.claude/skills/strata-make-a-game/SKILL.md:53-62`). The **one-paragraph design** that
each project page opens with is taught next, from the samples' READMEs, and the reader writes one as the page's
`:::example`. **Playtests** with people close the page: watch without explaining, note where the player stops, change
one thing, test again; a play-test that a machine runs is a different tool, linked to its page. What the choice cannot
do: a tool can check the rules, never the fun. Common mistakes: scope that grows, polish before the loop works, testing
only by yourself, numbers changed in code instead of in fields. The exercises: the core loop and the cut list of Coin
Run (a design exercise), then a grey box of the reader's own design built in the editor and play-tested with one person
(an editor task). At the end the reader can write a one-paragraph design with a core loop and a cut list for a game of
their own, and knows how to test it with a person.

**Leaves out.**

- State machines, managers and object pools for game code → `make/patterns`
- Play-tests that a command script runs, and regression tests → `make/automated-playtests`
- Finding the same bug twice: same inputs, same game → `make/play-test-debug`
- Game AI: steering, pathfinding and behaviour trees → `appendix/game-ai`
- Planning and building a game with an AI agent → `make/with-an-agent`
- Reading the samples' code and READMEs in depth → `make/samples`
- Asset licenses for a prototype's downloaded assets → `make/assets`
- Building the two designs → `make/project-tetris`, `make/project-platformer`

**Fit.** `over`: about 4,100 words against M (3,000). Counted again from the sections: the problem and the naive
answer (about 400 words), the core loop with its diagram (470), the approaches with their table (500), scope (350),
the one-paragraph design with its example (400), playtests (350), Strata's aside, what the choice cannot do and four
common mistakes (530), the two exercises (500) and the fixed parts (600), with no code excerpt. Over M's top of
4,000, the page takes L by S2 (4,001 to 6,500 words), which the second size pass decides.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | concept | home | The core loop: the short cycle a player repeats, found by asking what the player does every few seconds; Tetris's loop and Sky Islands' loop as the examples. Evidence: `Samples/Tetris/README.md:3-5`; `Samples/ThirdPerson/README.md:3-7` |
| `new:2` | concept | home | Scope as a cut list of must, should and could, with the samples' sizes as a yardstick: Tetris has three source files of 829 lines and one scene, Sky Islands 18 source files of 1,720 lines and three scenes. Evidence: `Samples/Tetris/Scripts/TetrisGame.h:108`, `TetrisGame.cpp:269` and `TetrisBoard.cpp:452` (the last lines); `git ls-tree -r --name-only 822a7a46 -- Samples/ThirdPerson/Scripts` lists 18 `.cpp` and `.h` files besides `CMakeLists.txt` and `.gitignore`, 1,720 lines in all; `Samples/ThirdPerson/Assets/Scenes/` holds `MainMenu`, `Course` and `Loading` |
| `new:3` | concept | home | The approaches to planning a game: a design document first, a paper prototype, a grey box in the engine, a vertical slice; a table of their cost, what each tests (the loop, the feel, the content) and who uses them, with sources in Further reading. General knowledge. |
| `new:4` | concept | home | Playtests with people: watch without explaining, note where the player stops or is lost, change one thing, test again; how this differs from a play-test a machine runs. General knowledge. |
| `new:5` | concept | home | The one-paragraph design that each project page of block C opens with: what the player does, the core loop, how the game is won and lost, the controls, and what is left out. Evidence: `Samples/Tetris/README.md:3-5`; `Samples/ThirdPerson/README.md:3-7`; `Samples/PhysicsPlayground/README.md:3-6` |
| `new:6` | concept | home | Strata's way of working, in a `:::why` aside: design the code so that tools can check it (rules in a plain class, randomness from a seed field, tuning as fields, one log line per event). Evidence: `.claude/skills/strata-make-a-game/SKILL.md:53-62` |
| `new:7` | figure | home | Diagram: the core loops of Tetris and of Sky Islands as two cycles side by side. Evidence: `Samples/Tetris/README.md:3-5`; `Samples/ThirdPerson/README.md:3-7` |
| `gamedev:254-255` | feature | use | The two samples that block C follows, as the examples of a core loop, a scope and a one-paragraph design |
| `gamedev:256-258` | feature | link | The other three samples, named as further examples of a small scope |
| `gamedev:346` | concept | use | Testing a game: determinism and observability, named as the reason for designing the code for tools; the automated play-test is linked; the page uses it for play-tests by people |
| `new:25` | hands-on | home | Exercise (Basic, design): the core loop of Coin Run written as a cycle, and its features sorted into must, should and could; the answer discusses good cut lists. General knowledge. |
| `new:26` | hands-on | home | Exercise (Medium, editor task): the core loop of the reader's own one-paragraph design built as a grey box from the built-in meshes of the Hierarchy's "+" menu in a project from the Basic 3D template, played by one person without explaining, one change, played again; the worked solution is a command script that builds a small grey box. Evidence: `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:72-89` |
| `gamedev:516` | rule | link | Deterministic play-tests need seeds and fixed steps: one sentence in the aside |
| `gamedev:663` | term | link | Seed, used in the aside |
| `automation:224` | feature | link | The `strata-make-a-game` skill, the playbook the samples were made by |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Game flow: levels, win, lose, restart | `make/project-coin-run` | must |
| The finished Coin Run, which the page compares with the projects | `make/project-coin-run` | must |
| One frame, start to finish; frame time | `start/what-an-engine-is` | helps |
| Built-in meshes from the Hierarchy's "+" menu, for a grey box | `make/scenes-entities` | helps |
| Fields changed in the Inspector while the game plays; hot reload | `make/first-script` | helps |
| `Log::Info` and the Console panel | `make/first-script` | helps |
| Same inputs, same game | `make/play-test-debug` | helps |
| Opening a copy of a sample | `start/first-game` | helps |
| `Random` and seeds | `make/recipes` | helps |
| Play-tests of a game that a command script runs | `make/automated-playtests` | helps |
| Exercises: a new project from the Basic 3D template | `make/project-files` | helps |

## `make/project-tetris` — Project: Tetris

**Covers.** The page builds Tetris from a new Basic 3D project, with a copy of `Samples/Tetris` open beside it to
compare, and opens with its one-paragraph design (a 10 × 20 well, seven pieces from a seeded 7-bag, line clears,
levels that speed gravity up, a ghost piece, a preview of the next piece, pause and game over) and a picture of the
result. The reader learns, in this order: to keep the rules of a game in a plain C++ class that calls nothing of the
engine, and a script that feeds it input and time and draws its state; to draw a grid with entities created once and
then shown, hidden or recolored, touching only what changed; to read held keys with `KeyRepeat` and to run gravity as
an accumulator of `deltaTime`; to keep a HUD current; to survive a hot reload by finding the cells again in
`OnReload`; to prove the game with a command script that expects an exact score; and to export it. At the end the
reader owns a finished, exported Tetris and a play-test that fails when its rules break.

Stage 1, the project and the well: the design paragraph, a Basic 3D project named Tetris, the template's Ground and
`Spinner` deleted, the camera moved to face the well, and the walls, floor and backdrop as scaled cubes under a `Well`
entity with their materials (checkpoint `tetris-1`). Stage 2, the rules: `TetrisGame.h` and `TetrisGame.cpp` written
in four pieces (the well, the shapes in their rotation box and the quarter turn; moves, `Fits` and rotation with kicks;
gravity steps, locking, clearing rows, score and levels; the 7-bag from a seeded `Random`), and a first `TetrisBoard`
script that starts a game in `OnCreate` and logs its pieces: with seed 60 the Console shows "piece 1 is J, next I"
(`tetris-2`). Stage 3, drawing the well: seven piece materials and a ghost material as asset fields, the 200 cells
and four preview cells created once under a `Cells` child, and `Refresh` with `ShowCell`, which change only the cells
whose piece changed (`tetris-3`). Stage 4, play: `KeyRepeat` pairs for left, right and soft drop, rotation and hard
drop on presses, gravity as an accumulator whose interval shrinks per level, and the ghost piece; the game is playable
(`tetris-4`). Stage 5, the HUD: a canvas that scales with the screen from 1280 × 720, a stats panel with a layout,
the score, level and lines texts as the board's entity fields, the controls text and the next piece's label, each
text written only when its value changes (`tetris-5`). Stage 6, a finished game: four one-shot sounds requested in
`OnCreate`, pause with P as a flag of the script (compared in two sentences with time scale 0), the game-over panel
and message, R or Enter restarting with the next seed, Escape quitting, and `OnReload` finding the cells again so that
a hot reload adds no second set (`tetris-6`). Stage 7, an exact play-test: a command script that slows gravity with
`script.setField`, checks the HUD at two resolutions with `ui.layout`, plays a 26-step `input.sequence` and expects
"Score: 209", "Lines: 1" and "Level: 2", then speeds gravity up, waits with `until` for "GAME OVER", restarts with R
and expects "Score: 0"; it finds its entities with `entity.find` and `bind` where the sample's script names fixed ids,
and it counts game time in steps where the sample's waits 300 frames; it passes, and fails once the reader breaks the
scoring on purpose (`tetris-7`). Stage 8, shipping: the game's title and icon on the Project Settings Game page, the
export, and the exported game run (`tetris-8`, the end state). The exercises make it the reader's own: the best score
kept in a save file, a hold piece with its play-test, and the pieces played with a gamepad.

**Leaves out.**

- Input actions and gamepad controls for the pieces (the sample reads keys; an exercise applies them) → `make/input`
- A pause menu with buttons at time scale 0 → `make/menus`
- Saving the best score in a save file (the Basic exercise applies it) → `make/levels-saves`
- How TAA softens the cubes, and choosing the anti-aliasing → `make/quality`
- How an agent made the sample through commands alone → `make/with-an-agent`
- The CTest that runs the sample's own script and its exported game → `engineering/test-kinds`
- How the canvas computes the HUD's rects at each resolution → `ui/layout`
- What a shuffle's random numbers are and why a seed repeats them → `make/recipes`

**Fit.** `fits`: about 9,800 words against XL (8,000). Counted again from the sections: eight stages of four to seven
steps with their results (about 5,400 words), five excerpts explained (1,250), the rules as data, the two ways to
pause, two diagrams and the play-test's numbers (820), three rules, two errata and eight checkpoints (590), three
exercises (750), What you will make and What you need with the design (400) and the fixed parts (600); inside XL's
range of 6,501 to 10,000, near its top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:254` | feature | home | The Tetris sample as the model of the project: rules in a plain class, a script for input, time and drawing, entities created once and shown or hidden, `KeyRepeat`, the seeded 7-bag, HUD texts, one-shot sounds, Escape quits; its files and scene named as the page builds each again. The page says that the rules can be tested without the engine, never that they are: no test builds the rules class at the pin, and the page's notes record that the README's "tested on their own" (`Samples/Tetris/README.md:13`) is false there (pipelines.md §11) |
| `gamedev:372` | code | home | `Samples/Tetris/Scripts/TetrisGame.h:8-106`: the rules class without engine calls: the well's size and hidden rows, the piece types, the moves that return false and change nothing, `StepResult`, the score, level and lines, the private bag and `Random`; a class that could be tested without the engine, which no test at the pin does (the only match of `TetrisGame` under `StrataTests` is `StrataTests/src/Editor/ProjectSamplesTests.cpp:203`, a copied file) |
| `gamedev:373` | code | home | `Samples/Tetris/Scripts/TetrisBoard.cpp:60-104`: `OnCreate` requests the materials and sounds, creates the cells, sets up input and starts a game; `OnReload` finds the cells again; `OnUpdate` quits, restarts, pauses, plays and refreshes. With lines 109-150, `Play`: `KeyRepeat` pairs, rotation and hard drop on presses, soft drop, gravity as an accumulator |
| `new:8` | code | home | `Samples/Tetris/Scripts/TetrisGame.cpp:255-267`: the 7-bag, a Fisher-Yates shuffle of the seven pieces with the seeded `Random`, dealt one by one until the bag is empty |
| `new:9` | code | home | `Samples/Tetris/Scripts/TetrisGame.cpp:195-237`: `Lock` and `ClearFullRows`: the piece written into the well, full rows removed and the rows above moved down, points by rows times level (the table at lines 32-33), game over when a piece locks above the well or the next has no room |
| `new:10` | code | home | `Samples/Tetris/Scripts/TetrisGame.cpp:90-108`: `Rotate` tries the turned piece at the kick offsets of lines 29-30 and keeps the first that fits; the O piece does not turn |
| `new:11` | concept | home | The rules of the falling-block game as data: a 10 × 20 well with four hidden rows above it, seven tetrominoes in a rotation box, the quarter turn (x, y) to (y, size - 1 - x), gravity steps, locking, line clears, score and levels. Evidence: `Samples/Tetris/Scripts/TetrisGame.h:8-18`; `Samples/Tetris/Scripts/TetrisGame.cpp:17-33, 48-60` |
| `new:12` | concept | home | Two ways to pause: the sample's flag, which stops the rules while the scene runs on, and time scale 0, which stops game time for every script (`make/menus`' pause menu). Evidence: `Samples/Tetris/Scripts/TetrisBoard.cpp:96-102` |
| `new:13` | feature | home | The numbers the page's play-test expects: with seed 60 the first piece is J and the next I; the sample's 26-step sequence ends with one line, score 209 and level 2 when `LinesPerLevel` is 1. Evidence: `StrataTests/CMakeLists.txt:874-875`; `StrataTests/Editor/TetrisCommands.json.in:5-6, 16-24` |
| `new:14` | figure | home | Diagram: the rules class, the board script and the engine: input and time go into the rules, their state comes out to the cells and the HUD; the rules call nothing of the engine. Evidence: `Samples/Tetris/Scripts/TetrisBoard.cpp:1-4`; `Samples/Tetris/Scripts/TetrisGame.h:8-10` |
| `new:15` | figure | home | Diagram: the well's coordinates: cell (x, y) at world position (x, y, 0) from the board's origin, row 0 at the bottom, the hidden rows above row 19, where a piece spawns, and the preview's offset. Evidence: `Samples/Tetris/Scripts/TetrisBoard.cpp:1-2, 45`; `Samples/Tetris/Scripts/TetrisGame.h:14-16`; `Samples/Tetris/Scripts/TetrisGame.cpp:239-253` |
| `new:16` | erratum | home | The sample's README says its cells are "created and destroyed by a script"; the board creates them once and only shows, hides and recolors them, and destroys none. Evidence: `Samples/Tetris/README.md:14`; `git grep -n Destroy 822a7a46 -- Samples/Tetris/Scripts` finds nothing; `Samples/Tetris/Scripts/TetrisBoard.cpp:222-247, 355-369` |
| `new:27` | erratum | home | The sample's command script waits 300 frames for game over (`editor.wait {frames: 300}`); the engine's rule for tests is to wait by the clock or a condition, never by frames, so the page's script waits with `until` and counts game time in steps, and never shows that line as a model. Evidence: `StrataTests/Editor/TetrisCommands.json.in:28`; `AGENTS.md:117-118` |
| `new:28` | hands-on | home | Exercise (Basic): the best score kept between runs: written with `Game::WriteSaveFile` when a game ends, read with `Game::ReadSaveText` in `OnCreate` (empty when there is no file yet) and shown as a fourth HUD text. Evidence: `StrataScriptCore/Include/StrataScript/Game.h:104-148` |
| `new:29` | hands-on | home | Exercise (Medium): a hold piece, a rule the sample does not have: one key swaps the falling piece with the held one, once per piece; added to the rules class with its own preview cells, and the play-test of stage 7 extended to expect it. Evidence: `git grep -ni hold 822a7a46 -- Samples/Tetris/Scripts` finds only the 7-bag's comment (`Samples/Tetris/Scripts/TetrisGame.cpp:259`) |
| `new:30` | hands-on | home | Exercise (Hard): the pieces played with a gamepad: the moves as input actions of a Gameplay map with keys and gamepad bindings, read with `Input::IsActionDown` and `IsActionPressed`, and a repeat for held actions written like `KeyRepeat`, which reads keys only. Evidence: `StrataScriptCore/Include/StrataScript/Gameplay.h:181-211`; `StrataScriptCore/Include/StrataScript/Input.h:384-393` |
| `gamedev:469` | figure | home | The finished Tetris with its HUD and ghost piece (What you will make) and the game-over panel (the picture of `tetris-6`) |
| `gamedev:542` | hands-on | home | G9, the page's whole path: rules class, board script, `KeyRepeat`, HUD, sounds, pause, game over, and a command-script regression with an exact score |
| `gamedev:662` | term | home | 7-bag |
| `gamedev:374` | code | use | `Refresh` and `ShowCell`, "touch only what changed", built again in stage 3 (its home is `make/patterns`) |
| `gamedev:375` | code | use | The sample's regression, which the reader's script of stage 7 follows (its home is `make/automated-playtests`) |
| `gamedev:371` | code | use | `KeyRepeat`, used for held keys in stage 4 (its home is `make/timers-events`) |
| `gamedev:286` | concept | use | The loop: gravity counts `deltaTime`, so the game falls at the same speed at any frame rate |
| `gamedev:323` | concept | use | Hot reload and state: the game restarts in `OnReload`, and the cells are found again, never made twice |
| `gamedev:484`, `gamedev:486` | rule | use | Work in `OnCreate`, not the constructor; only fields survive a hot reload |
| `gamedev:494` | rule | use | Request assets early: the materials and sounds are requested in `OnCreate` |
| `gamedev:509-510` | rule | use | The HUD is a canvas, not screen-space text; `UIText` is centered unless set to Left |
| `gamedev:346` | concept | use | Testing a game: a seed and fields that slow gravity make the play-test exact |
| `gamedev:516` | rule | use | Deterministic play-tests: seeds, input counted in steps, `input.sequence`, waits with `until` |
| `gamedev:348` | concept | use | Shipping: the export of stage 8 |
| `gamedev:35` | feature | use | Open Sample makes the copy the reader compares with; the sample itself is never changed |
| `gamedev:456` | figure | use | The viewport's canvas mode, used to lay out the HUD in stage 5 |
| `gamedev:663` | term | link | Seed |
| `scripting:118`, `scripting:120`, `scripting:121`, `scripting:122`, `scripting:124`, `scripting:127`, `scripting:129`, `scripting:131`, `scripting:133`, `scripting:135` | feature | use | The SDK the page calls: `Entity` (`SetActive`, `SetProperty`, `GetChildren`), `TransformComponent`, `Scene` and `Assets` (`CreateEntity`, `Find`, `RequestLoad`), `Input::IsKeyPressed`, `Log::Info`, `Audio::PlayOneShot`, `Game::Quit`, `UIElement::SetText`, `Random`, `KeyRepeat` |
| `gameui:224` | feature | use | The Tetris HUD on a canvas, which stage 5 builds |
| `audio-input:100` | feature | use | Tetris's one-shot sounds among the samples' sounds |
| `editor-core:240` | feature | use | The command script that stage 7 writes and runs |
| `editor-core:580` | rule | use | Tools count game time in fixed steps: the page's script waits for game over with `until`, where the sample's waits with `editor.wait {frames: 300}` (`StrataTests/Editor/TetrisCommands.json.in:28`) |
| `editor-core:662-665` | term | link | Command script, `expect`, `bind` and `$ref`, `until` |
| `build-test:167` | feature | link | The sample tests that run the sample's own script (`StrataEditor.Tetris`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Stage 1: the one-paragraph design and the core loop | `make/designing-a-game` | must |
| Stage 1: a project from the Basic 3D template; saving the scene | `make/project-files` | must |
| Stage 1: entities and components in the Hierarchy and the Inspector | `make/scenes-entities` | must |
| Stage 1: positions and scales typed in the Inspector; parents and children | `make/transforms-units` | must |
| Stages 1 and 3: materials made in the material editor | `make/materials` | must |
| Stage 2: values, variables, decisions, scoped enum values, namespaces and `::` | `basics/programming-1` | must |
| Stage 2: functions, loops and lists (`std::array`, `std::vector`) | `basics/programming-2` | must |
| Stage 2: structs, classes, and files of code (a header and its source file) | `basics/programming-3` | must |
| Stage 2: a script class, building with Ctrl+B, the Problems panel and the Console | `make/first-script` | must |
| Stage 2: `Random` and seeds | `make/recipes` | must |
| Stage 2: finding a wrong rule with the debugger | `basics/debugging` | helps |
| Stage 3: creating entities from a script; `SetActive`, `SetProperty`, `GetChildren` | `make/scripting-scene` | must |
| Stage 3: showing and hiding instead of creating and destroying | `make/patterns` | must |
| Stages 3 and 5: entity and asset fields set in the Inspector | `make/script-fields` | must |
| Stage 4: `OnUpdate`, `deltaTime`, and counting time instead of frames | `make/script-loop` | must |
| Stage 4: reading keys with `Input::IsKeyPressed` | `make/input` | must |
| Stage 4: `KeyRepeat` for held keys | `make/timers-events` | must |
| Stage 5: a UI canvas, anchors, `UIText` and text a script writes | `make/hud` | must |
| Stage 5: layout groups and panels | `make/menus` | helps |
| Stage 6: importing sounds; one-shots requested in `OnCreate` | `make/sound` | must |
| Stage 6: hot reload: what survives, and `OnReload` | `make/first-script` | must |
| Stage 6: pausing with time scale 0 | `make/menus` | helps |
| Stage 6: `Game::Quit` | `make/levels-saves` | helps |
| Stage 7: JSON as a reader writes it; command scripts with `expect`, `until`, `bind`, `input.sequence` and `ui.layout`; `StrataEditor --commands` | `make/automated-playtests` | must |
| Stage 7: running a program with arguments in a terminal | `start/install` | must |
| Stage 7: same inputs, same game | `make/play-test-debug` | helps |
| Stage 8: the game's title and icon, the export, running the exported game | `make/export` | must |
| Exercises: save files with `Game::WriteSaveFile` and `Game::ReadSaveText` | `make/levels-saves` | helps |
| Exercises: input actions with gamepad bindings, `IsActionDown` and `IsActionPressed` | `make/input` | helps |

**Starting state.** A new project made in the launcher from the Basic 3D template (the tutorial file's `startsFrom
{"template": "basic3d"}`), named Tetris: its Main scene holds Main Camera, Sun, Sky, Ground and Post Process
(`StrataEditor/src/Editor/ProjectTemplates.cpp:51-87`), and its `Scripts/` folder the example `Spinner` script
(`.claude/skills/strata-make-a-game/SKILL.md:44-46`), which stage 1 deletes. The page starts from no checkpoint of an
earlier page: block C does not continue Coin Run (`book.md`, "Running examples"). Beside it the reader opens a copy of
the sample (Open Sample > Tetris) to compare, never the sample itself. The four sounds are imported from the release's
`Samples/Tetris/Assets/Sounds/` (`Move.wav`, `Lock.wav`, `Clear.wav`, `GameOver.wav`, made for Strata:
`Samples/Tetris/CREDITS.md`). Each stage starts from the checkpoint of the stage before (`tetris-1` to `tetris-7`);
`tetris-8` is the end state.

**Command-only steps.**

- Stage 7 runs a command script, which no menu or button runs: the file of commands is run with `StrataEditor
  --commands <file>` (in PowerShell piped to `Out-Host`, so that it waits: `Docs/DeveloperGuide.md:334-336`). A step
  that runs a script needs `make/automated-playtests`, which is in the page's Needs and teaches it; the Medium exercise
  runs the same script again. No step calls a command through StrataCLI, so the page needs no `make/commands`. Every
  other step has a menu, a button or a panel.

## `make/project-platformer` — Project: a third-person platformer

**Covers.** The page builds a smaller Sky Islands from a new Basic 3D project, with a copy of `Samples/ThirdPerson` open
beside it, and opens with its one-paragraph design (an animated robot runs and jumps over floating islands, bounces on
jump pads, collects coins, rides a moving platform and races for the best time to a flag; a main menu, a pause menu and
a loading screen) and its cut list (lanterns, probes, the settings screen, the crate and the attract mode are left for
later). It is the page where the toolbox of block B works together: the reader learns to give a skinned model a
character controller and camera-relative controls, to drive its animator from the movement, to let triggers report to
one state of the course, to reuse the follow camera and the moving platform of an earlier page, to split a game into
scenes that pass nothing but save files, and to ship it pruned with a loading scene. At the end the reader owns a
multi-scene third-person game and its exported folder.

Stage 1, the plan and the assets: the design paragraph, a Basic 3D project named Platformer, the robot, a few Platformer
Kit models and the sounds imported from the release's `Samples/ThirdPerson/Assets/` with a `CREDITS.md`
(`platformer-1`). Stage 2, the course: prefabs of kit blocks at twice their size, each static with a mesh collider, laid
out as islands on a 4 m grid at three heights with gaps to jump, under a `Course` entity; the template's Ground deleted
(`platformer-2`). Stage 3, the player: a `Player` entity tagged "Player" with a character controller and the robot as
its child, turned 180 degrees because glTF models face +Z; the project's Gameplay map (Move, Run, Jump, Respawn, Look,
Pause); `ThirdPersonPlayer`, which walks where the camera looks, turns the body toward its walk with `std::remainder`,
jumps with a short coyote time and goes back to the start when it falls; the robot slides in its rest pose
(`platformer-3`). Stage 4, the camera: two files of `make/characters-cameras` copied into the project from the book's
tutorial files (`book:tutorials/make/characters-cameras/`), `FollowCamera.cpp` and the platform script beside it, never
taught again; the follow camera pointed at the player, orbiting with the mouse and the Look action, its arm shortened by
a raycast, following the drawn position (`platformer-4`). Stage 5, the robot comes alive: the controller made by one
command, then edited in the Asset tab (Speed, Grounded and Jump; Idle, Walk, Run and Jump with their transitions;
Footstep events in Walk and Run), the Animator on the robot, the player script setting Speed and Grounded every update
and Jump when it jumps, and `Footsteps` playing a step at a random pitch on each event (`platformer-5`). Stage 6, a
course to finish: a `Game` entity whose `CourseState` counts coins and time on a HUD; a coin prefab (a sphere trigger
whose child spins), a jump pad prefab (a box trigger that calls the player's `Launch`), checkpoints as marker entities
`Checkpoint1`, `Checkpoint2` found by name, and the goal, which completes the course, shows the time and keeps the best
one in a save file (`platformer-6`). Stage 7, a moving platform, which the sample does not have: a kinematic body with a
box collider across a gap of the course, given the platform script copied in stage 4 (the book's own code, which moves
it between two points in `OnFixedUpdate`); the robot rides it and the camera does not judder, for the reasons
`make/characters-cameras` taught, said in two sentences with a link (`platformer-7`). Stage 8, menus: a `MainMenu` scene
saved with Save Scene As, with Play and Quit, set as the start scene; the course as an asset field of the menu; a pause
menu at time scale 0 with Resume, Restart and Main Menu, the cursor freed while paused; the completion panel's Play
Again and Menu buttons (`platformer-8`). Stage 9, shipping: a `Loading` scene with the loading bar of
`make/levels-saves` (its `LoadingScreen` script linked, not shown again), chosen as the Export dialog's Loading scene;
an export with "Leave out unused assets"; the exported game run from its folder, the loading scene shown while the main
menu loads (`platformer-9`, the end state). The exercises: a lantern that casts shadows (Basic), the settings screen's
Graphics row (Medium) and a regression play-test of the course (Hard).

**Leaves out.**

- Lanterns: point lights that cast shadows → `make/lamps`
- Reflection probes and their bake → `make/reflections`
- The HDR sky and the sun extracted from it → `make/lighting`
- The settings screen (volume, mouse sensitivity, window and vsync) and credits scrolling in a mask → `make/menus`
- The settings screen's Graphics row → `make/quality`
- The attract mode, and state the script module keeps across scene switches → `make/levels-saves`
- The crate the controller pushes into the pit → `make/characters-cameras`
- The menu robot holding a flag with `AttachToJoint` → `make/animation`
- The robot's faces, morph targets that the importer skips → `animation/limits`
- Laying out many prefabs with one command → `make/commands`
- A regression play-test of the course → `make/automated-playtests`
- Why the loading scene plays only while the start scene loads → `worlds/runtime`

**Fit.** `over`: about 10,100 words against XL (8,000). Counted again from the sections: nine stages of four to eight
steps with their results (about 5,800 words), four excerpts explained (1,000), one state for the course, the diagram,
the scene field and the erratum (560), six rules and nine checkpoints (750), three exercises (750), What you will make
and What you need with the design and its cut list (530), the platform's two sentences (60) and the fixed parts (600).
At or over XL's top of 10,000, the page splits after stage 5 (S3; past 10,000 words a page splits into pages, R7) into
"Project: a third-person platformer, the course and the character" (stages 1 to 5 and the lantern exercise, about
5,200 words, L) and "Project: a third-person platformer, a game to finish and ship" (stages 6 to 9 and the other two
exercises, about 5,600 words, L), which the second size pass decides.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:255` | feature | home | Sky Islands as the model of the project: the controller with camera-relative movement, coyote time, checkpoints and respawn; the follow camera; the skinned robot and its controller with Footstep events; coins, jump pads and the goal as trigger prefabs; the course of kit blocks with mesh colliders on a 4 m grid; three scenes; the menus, pause at time scale 0 and save files; what the page leaves out of it |
| `gamedev:377` | code | home | `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:54-137`: the player's update: the walk measured, the ground state read, landing sounds, movement along the camera's view, the body turned toward it with `std::remainder` and a turn rate, the jump with coyote time, the animator's Speed and Grounded, checkpoints and the fall back |
| `new:17` | code | home | `Samples/ThirdPerson/Scripts/JumpPad.cpp:38-51`: a trigger that checks the tag "Player", finds the player's script on the other entity and calls its `Launch`, then plays the bounce at its position |
| `new:18` | code | home | `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:212-225`: checkpoints reached on the ground within 3 m, in order; with lines 19-30 (markers found by name, `Checkpoint1`, `Checkpoint2`) and 144-157 (`Respawn` teleports the controller to the last one) |
| `new:19` | code | home | `Samples/ThirdPerson/Scripts/CourseState.cpp:68-92`: the course completed once, the best time kept in a save file, the completion panel's texts and its first button focused, the cursor freed |
| `new:20` | code | use | The loading screen's script, whose excerpt `make/levels-saves` holds and teaches: stage 9 links it and shows only what it changes here (the `Loading` scene's own bar and label, the scene chosen as the Export dialog's Loading scene). Evidence: `Samples/ThirdPerson/Scripts/LoadingScreen.cpp:18-27` |
| `new:21` | concept | use | A moving platform, which the sample does not have: stage 7 gives a kinematic body the platform script copied in stage 4 (the book's own code under `tutorials/`, moved in `OnFixedUpdate`). Why the robot rides it (physics follows a kinematic body with a velocity that reaches the new place in one step; a controller on the ground takes on that velocity and keeps it when it walks off) is taught by `make/characters-cameras`, which the page links. Evidence: `git grep -n OnFixedUpdate 822a7a46 -- Samples/ThirdPerson` finds nothing; `Strata/src/Strata/Physics/PhysicsWorld.cpp:3402-3409`; `Strata/src/Strata/Physics/CharacterControllers.cpp:39-41, 653-654`; `Docs/Manual/Scripting.md:174-175` |
| `new:22` | concept | home | One state for the course: a `Game` entity whose `CourseState` the coins and the goal find by name and report to, found again at each event, never kept. Evidence: `Samples/ThirdPerson/Scripts/CourseState.h:7-9`; `Samples/ThirdPerson/Scripts/Coin.cpp:43-44`; `Samples/ThirdPerson/Scripts/Goal.cpp:15-16` |
| `new:23` | figure | home | Diagram: the entities of the reader's course and their scripts: `Player` (controller, `ThirdPersonPlayer`) with the robot (Animator, `Footsteps`), the camera (`FollowCamera`), `Game` (`CourseState`, `PauseMenu`), the coins, jump pads and goal reporting to it, the moving platform. Evidence: `grep -o '"Class":"[^"]*"' Samples/ThirdPerson/Assets/Scenes/Course.stscene` lists the sample's classes |
| `new:24` | rule | home | A scene the game loads is an asset field of a script, not a path, so that a pruned export keeps it. Evidence: `.claude/skills/strata-make-a-game/SKILL.md:509-510`; `Samples/ThirdPerson/Scripts/MainMenu.cpp:16`; `Samples/ThirdPerson/Scripts/CourseState.h:13` |
| `new:31` | erratum | home | A menu works with a gamepad without a script's focus: with nothing focused, the first direction press or Submit focuses the topmost input canvas's `FirstSelected`, else its top-left selectable, and only focuses. The sample's `Focus()` calls (the main menu's Play, the completion panel's Play Again) save that first press; the page never says that a menu without them is unusable with a gamepad, as `plan/inventory/gameui.md:369-370` does. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:526-531, 539-542, 769-807`; `Samples/ThirdPerson/Scripts/MainMenu.cpp:44-45`; `Samples/ThirdPerson/Scripts/CourseState.cpp:88-89` |
| `new:32` | hands-on | home | Exercise (Basic): a lantern that casts shadows, a point light under a tree of the course with a glowing material, as the sample's two lanterns are. Evidence: `Samples/ThirdPerson/README.md:28` |
| `new:33` | hands-on | home | Exercise (Medium): the settings screen's Graphics row, four toggles in one group that set the quality preset with `Graphics::SetPreset` and keep it with `Graphics::Save`, as the sample's settings menu does. Evidence: `Samples/ThirdPerson/Scripts/SettingsMenu.cpp:28-36`, `:114-118` |
| `new:34` | hands-on | home | Exercise (Hard): a regression play-test of the reader's course, a command script that drives the player with `input.sequence` on the Gameplay actions, places it at a coin and at the goal, and expects the coin counted and the course completed, waiting with `until` in steps, as the sample's own script does. Evidence: `StrataTests/Editor/ThirdPersonCommands.json.in:41`, `:74-75`, `:91-93` |
| `gamedev:470` | figure | home | The sample's course with a coin and a jump pad (its `Screenshots/Course.png` and `JumpPad.png`) and its main and pause menus, as the game the page follows; the settings menu's Graphics row is `make/quality`'s |
| `gamedev:544` | hands-on | home | G11, the page's whole path: the skinned character whose controller `animation.createController` makes, the follow camera with a raycast arm, jump pads, checkpoints, a moving platform in `OnFixedUpdate`, footstep events, menus, a loading scene and a pruned export |
| `gamedev:378` | code | use | The follow camera: the book's own `FollowCamera.cpp` of `make/characters-cameras`, copied in stage 4 from `book:tutorials/make/characters-cameras/`, of which the sample's file is the finished form (its home is `make/characters-cameras`) |
| `gamedev:381` | code | use | The robot's controller as data, of which stage 5 builds a smaller one (its home is `make/animation`) |
| `gamedev:427` | figure | use | The sample's scene flow, of which the page builds the menu, course and loading scenes without the attract mode |
| `gamedev:301` | concept | use | A model that walks backwards: glTF faces +Z while forward is -Z, so the robot child turns 180 degrees |
| `gamedev:331`, `gamedev:333` | concept | use | Characters and cameras that follow, as stages 3 and 4 apply them |
| `gamedev:335` | concept | use | Animation for makers, as stage 5 applies it |
| `gamedev:342` | concept | use | Game flow: the menu, the course and the loading scene; state passed only through save files |
| `gamedev:348` | concept | use | Shipping: the pruned export and the exported game |
| `gamedev:490`, `gamedev:492` | rule | use | The camera follows the drawn position in `OnLateUpdate`; the respawn uses `Teleport` |
| `gamedev:496` | rule | use | `GetScript<T>` found again at each event, never kept across frames |
| `gamedev:498` | rule | use | Controls read as the Gameplay map's actions |
| `gamedev:500-501` | rule | use | The player has a controller and no rigid body; the coins and pads are convex triggers, because triggers do not see the course's mesh colliders |
| `gamedev:504` | rule | use | Entities do not survive `Game::LoadScene`: the best time goes through a save file |
| `gamedev:511` | rule | use | Pruned exports drop what is loaded by path: why stage 8 makes the scenes asset fields |
| `gamedev:519` | rule | use | The imported assets are CC0 and credited |
| `gamedev:628-629`, `gamedev:631`, `gamedev:633`, `gamedev:647`, `gamedev:651` | term | link | Character controller, coyote time, the animator's words, animation event, save file, pruned export |
| `gamedev:661` | term | link | Attract mode, named as left out |
| `gamedev:379-380` | code | link | Module state across scenes and the Graphics row, named as left out |
| `animation:185` | feature | use | `animation.createController`, the one step of stage 5 that only a command can do |
| `animation:363` | code | use | `Footsteps.cpp` and the lines that set the animator's parameters, written again in stage 5 (its home is `make/animation`) |
| `animation:212` | feature | link | The sample's robot, the running example of part `animation` |
| `scripting:385` | code | use | The coin script of stage 6 (its home is `make/recipes`) |
| `scripting:122`, `scripting:123`, `scripting:125`, `scripting:126`, `scripting:127`, `scripting:128`, `scripting:129`, `scripting:131`, `scripting:133` | feature | use | The SDK the page calls: input actions and the cursor, `Time::SetTimeScale` and unscaled time, `Collision` and `RigidBody`, `CharacterController`, `Audio::PlayOneShotAt`, `Animator`, `Game` (`LoadScene`, `ReloadScene`, `Quit`, save files, load progress), `UIElement`, `Random` |
| `physics:42` | feature | use | A kinematic body follows its entity with a velocity that reaches the target in one step: the moving platform |
| `physics:134` | feature | use | A controller carries the velocity of the platform it stands on, and keeps it when it leaves |
| `physics:408` | rule | use | Triangle meshes only on static bodies, and triggers do not see them: the course is static, the platform a box |
| `physics:425` | rule | use | Move what others ride in `OnFixedUpdate` |
| `gameui:226` | feature | use | The sample's main menu, of which stage 8 builds a smaller one |
| `audio-input:183` | feature | use | The sample's Gameplay map, which stage 3 builds again |
| `worlds-runtime:127` | feature | use | The loading scene, which plays while the start scene loads |
| `worlds-runtime:160` | feature | use | Pruning: the export keeps only what the scenes reference |
| `worlds-runtime:168` | feature | use | The Export dialog's Loading scene and "Leave out unused assets" |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Stage 1: the one-paragraph design and a cut list | `make/designing-a-game` | must |
| Stage 1: a project from the Basic 3D template; Save Scene As | `make/project-files` | must |
| Stage 1: importing glTF models and sounds; the import scale; licenses and a `CREDITS.md` | `make/assets` | must |
| Stage 2: prefabs, their instances, placing them by drop | `make/prefabs` | must |
| Stage 2: positions typed in the Inspector | `make/transforms-units` | must |
| Stage 2: static bodies with mesh colliders | `make/physics` | must |
| Stage 3: a model that faces +Z while forward is -Z | `make/transforms-units` | must |
| Stage 3: input actions, the Gameplay map, `IsActionPressed` and `GetActionValue` | `make/input` | must |
| Stage 3: a vector's length and `normalize`, the cross product, `atan2`, the camera's forward on the ground | `make/gameplay-math` | must |
| Stage 3: a character controller: `Move`, `Jump`, `IsGrounded`, `Teleport`; coyote time | `make/characters-cameras` | must |
| Stage 3: a class in a header and its source file; calling a public method of another class | `basics/programming-3` | must |
| Stages 3 and 6: entity and asset fields | `make/script-fields` | must |
| Stage 4: the follow camera with its raycast arm; `GetDrawnPosition` in `OnLateUpdate`; the locked cursor | `make/characters-cameras` | must |
| Stage 5: running a command with StrataCLI | `make/commands` | must |
| Stage 5: a controller's parameters, states, transitions and events in the Asset tab; the Animator; `OnAnimationEvent` | `make/animation` | must |
| Stage 5: a random pitch from `Random` | `make/recipes` | helps |
| Stage 6: triggers, tags and `OnTriggerEnter` | `make/physics` | must |
| Stage 6: finding another script with `GetScript<T>` at each event | `make/timers-events` | must |
| Stage 6: HUD texts on a canvas | `make/hud` | must |
| Stage 6: one-shot sounds at a position, requested in `OnCreate` | `make/sound` | must |
| Stage 6: save files with `Game::WriteSaveFile` and `Game::ReadSaveText` | `make/levels-saves` | must |
| Stage 7: `OnFixedUpdate` and the fixed step | `make/script-loop` | must |
| Stage 7: platforms moved in `OnFixedUpdate`; kinematic bodies | `make/characters-cameras` | must |
| Stage 8: buttons, `OnUIClick`, focus; a pause menu at time scale 0 | `make/menus` | must |
| Stage 8: `Game::LoadScene`, `ReloadScene` and `Quit`; entities do not survive a scene switch | `make/levels-saves` | must |
| Stage 9: a loading screen that shows progress | `make/levels-saves` | must |
| Stage 9: the export, the Export dialog, pruning, running the exported game | `make/export` | must |
| Exercises: a regression play-test of the course | `make/automated-playtests` | helps |
| Exercises: the settings screen's Graphics row | `make/quality` | helps |
| Exercises: a lantern with shadows | `make/lamps` | helps |

**Starting state.** A new project made in the launcher from the Basic 3D template (`startsFrom {"template":
"basic3d"}`), named Platformer, with the template's Main Camera, Sun, Sky, Ground and Post Process
(`StrataEditor/src/Editor/ProjectTemplates.cpp:51-87`); stage 2 deletes the Ground and stage 4 replaces the camera's
script setup. The page starts from no checkpoint of an earlier page. Stage 4 copies two files of
`make/characters-cameras`, `FollowCamera.cpp` and the platform script, from `book:tutorials/make/characters-cameras/`
(the stage's `files` in the tutorial file, pipelines.md §6.2), so that the two pages agree by construction. Beside
it the reader opens a copy of the sample (Open Sample > Third-Person Adventure) to compare. The files imported in
stage 1 come from the release's
`Samples/ThirdPerson/Assets/`: `Models/Robot/RobotExpressive.glb`, a few models of `Models/Platformer/` with their
`Textures/colormap.png`, and the sounds `Jump.ogg`, `Land.ogg`, `Coin.ogg`, `Bounce.ogg`, `Complete.ogg` and
`Footsteps/Grass1.ogg` to `Grass4.ogg`, all CC0 (`Samples/ThirdPerson/CREDITS.md`). Each stage starts from the
checkpoint of the stage before (`platformer-1` to `platformer-8`); `platformer-9` is the end state.

**Command-only steps.**

- Stage 5, making the animation controller: no menu or button creates one (the Content Browser's New menu holds
  Folder, Material, World and Script: `StrataEditor/src/Panels/ContentBrowserPanel.cpp:564-580`), only
  `animation.createController` (`StrataEditor/src/Editor/EditorAnimationCommands.cpp:153`). The step says so in its
  first sentence, lists the robot's clips with `animation.info` and creates the controller with its states through
  StrataCLI; its parameters, transitions and events are then edited in the Asset tab, as `make/animation` taught. A
  step that calls a command needs `make/commands`, which is in the page's Needs and teaches StrataCLI.
- Not command-only: laying out the course. The editor tab drops each prefab and types its position; the command tab
  places them all with one `prefab.instantiate {instances}`, a command called through StrataCLI as in stage 5.
- No step runs a command script. The Hard exercise does, as `make/automated-playtests` teaches; that page is in the
  page's Needs closure through `make/commands`.

## Passed on

none

## Not taken

none

## Questions for the planner

none
