# Brief: `make/project-tetris`

| Field | Value |
| --- | --- |
| Title | Project: Tetris |
| Kind | T |
| Size | XL |
| Tracks | G |
| Needs | `make/designing-a-game`, `make/recipes`, `make/automated-playtests` |
| From | gamedev "Tutorial: Tetris" (hands-on G9: the rules class, the board script, `KeyRepeat`, HUD, sounds, pause, game over, a command-script regression with an exact score); `Samples/Tetris` |
| Unit | `plan/allocation/make-c.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `7-bag` | 7-bag | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-c-1 | must | shape | `make/project-tetris` stages 2 to 6, `make/project-platformer` stages 3, 6 and 8 | The steps cannot be followed from the lists. About 470 of the 829 lines of the reader's Tetris are in no row: the shapes, moves, drops, `Fits` and `SpawnNext` of `TetrisGame.cpp`, and the board's fields, `ST_SCRIPT_CLASS` block, `SetupInput`, `CreateCells`, `FindCells`, `NewGame` and `HandleStep`. On the platformer, `ThirdPersonPlayer.h`, the player's helpers, `CourseState.h`, `Goal`, the main menu's script and the pause menu's script have no row. Neither page says whether the reader types these lines or copies them. Pages of track G show at most 25 lines per fence, and a stage's `files` may copy only from `book:tutorials/` or `Samples/*/Assets/`, not from `Samples/*/Scripts/`. | Each page's What you need names its script files under `book:tutorials/make/project-tetris/` and `book:tutorials/make/project-platformer/` (the book's copies of the samples' scripts, quoted with `src="book:…"`), with their downloads. Each stage names the files it adds, copies them through its `files`, and walks through the excerpts its rows name. The pause menu reuses the script that `make/menus` built. About 150 words per page. The other way, every part quoted on the page, does not fit XL (forPlanner). | `allocation/make-c.md:97-101`, `:141-145`, `:304-308`; `pipelines.md:879`, `:894-896`; `style.md:646`; `allocation/make-b1.md:831` (`make/menus` homes `PauseMenu.cpp:97-122`); pin: `Samples/Tetris/Scripts/TetrisGame.h:1-108`, `TetrisGame.cpp:1-269`, `TetrisBoard.cpp:1-452`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.h:1-70`, `PauseMenu.cpp:1-138`, `CourseState.h:1-48` |
| critic-make-c-2 | must | missing-item | `make/project-tetris` stages 2 and 3 (`gamedev:372`, `new:8` to `new:10`, `gamedev:373`); `make/project-platformer` stage 3 | The code the reader writes uses C++ that no page of track G teaches and no row names. These are `constexpr` constants (`TetrisGame.h:14-18`), an enum with a fixed type and `static_cast` to and from it (`h:21`, `cpp:37`, `:261`), `using` for a type's second name (`h:34`), the unnamed namespace (`cpp:8`), `return {}` (`cpp:126`) and `std::swap` (`cpp:263`). There is also a lambda given to `std::none_of` (`cpp:224`), a lambda kept in an `auto` variable (`TetrisBoard.cpp:291`), and `static constexpr` members and `std::pow` (`TetrisBoard.cpp:106-107`, `:192`). Their homes, `basics/cpp-modern` and `basics/cpp-generic`, are not on track G. The page's only C++ rows name `basics/programming-1` to `-3`. | Add a new concept item on `make/project-tetris`. It explains each of these where it is first used, at the use level, in one to three sentences, with a link to its home (about 400 words). Add Assumes rows of depth `helps` that name `basics/cpp-modern` and `basics/cpp-generic` (N2). `make/project-platformer` gets a `helps` row naming `make/project-tetris`, and says what `std::clamp` does where `ThirdPersonPlayer.cpp:100` uses it (about 30 words). With critic-make-c-1, -4 and -5, the Tetris estimate passes 10,000 words, so the page splits by S3 (the second size pass). | `allocation/make-c.md:190-192`; `allocation/basics-a.md:156-384` (programming-1 to -3: no `constexpr`, lambda or `static_cast`), `:875` (lambdas on `basics/cpp-generic`), `:943` (`static_cast` on `basics/cpp-modern`); `style.md:653-659`; `tracks.md`, track G; pin: `Samples/Tetris/Scripts/TetrisGame.h:14-34`, `TetrisGame.cpp:8`, `:126`, `:224`, `:263`, `TetrisBoard.cpp:106-107`, `:192`, `:291`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:97-100` |
| critic-make-c-3 | must | stale-item | Command-only steps of `make/project-tetris` (stage 7) | The row runs the script with `StrataEditor --commands <file>`, piped to `Out-Host`. Without `--project`, the editor opens no project, so the script's first `play.start` fails. Without `--quit-after-commands`, the editor stays open when the script ends. `make/automated-playtests`, which this step needs, teaches the line `StrataEditor --project <dir> --commands <file> --quit-after-commands`, piped to `Write-Output` on Windows, as `start/install` teaches the pipe. | The row and stage 7 give the line of `make/automated-playtests` exactly, with its exit codes (0 passed, 1 failed). No words are added. | `allocation/make-c.md:227-228`; `allocation/make-b2.md:675-677`, `:779-781`; pin: `StrataEditor/src/EditorApplication.cpp:65-67`, `:296-299`; `StrataEditor/src/EditorLayer.cpp:463-471`, `:1069-1071`; `StrataTests/Editor/SampleProject.cmake:110-111` |
| critic-make-c-4 | should | missing-item | `make/project-tetris` stage 7 (`editor-core:240`, `gamedev:375`) | `script.setField` before `play.start` edits the saved scene: the change is undoable, and it leaves the scene modified. The sample's script undoes both of its edits after `play.stop` and expects `scene.info` to report `/modified` false. The page's script sets LinesPerLevel to 1 and StartInterval to 100 in the same way, but has no such step. A reader who then saves ships a game that goes up a level at every line and whose gravity takes 100 s per row. Also, the `ui.layout` rects that the sample expects (70, 70, 131.68, 42.19 at 1280 × 720) hold only for the sample's exact HUD. | Stage 7's script ends with `play.stop`, one `edit.undo` per edit and `scene.info` expecting `/modified` false, with one sentence on why (about 60 words). Stage 5 fixes the HUD numbers that stage 7 expects, or stage 7 reads the rects from a first `ui.layout` run and writes them in (about 40 words). | `allocation/make-c.md:110-115`; `allocation/make-b2.md:682-684` (the excerpt there ends at line 24); pin: `StrataEditor/src/Editor/EditorScriptCommands.cpp:635-637`, `:680-683`; `StrataTests/Editor/TetrisCommands.json.in:4-10`, `:38-41` |
| critic-make-c-5 | should | order | `make/project-tetris` stage 7 | The script finds the board and the HUD texts with `entity.find` and binds their IDs. No page of track G teaches `entity.find`. `make/automated-playtests` uses the sample's fixed IDs, which its copy of the sample keeps. `make/commands` is outside the page's Needs closure, and it uses `entity.find` only to check its exercise. The page has no row for it. | Stage 7 teaches it in two or three sentences, `entity.find {name}` and `bind` of `/entities/0`, as `ThirdPersonCommands.json.in:8` does. It gets a `use` row (the command's catalogue row is `reference/commands`'). The Assumes row on line 208 keeps `bind` with `make/automated-playtests`. About 70 words. | `allocation/make-c.md:113-114`, `:208`; `allocation/make-b2.md:774`, `:840`; pin: `StrataEditor/src/Editor/Commands/EntityCommands.cpp:401-411`; `StrataTests/Editor/ThirdPersonCommands.json.in:8-9` |
| critic-make-c-11 | should | duplicate | `new:16` and `new:27` on `make/project-tetris` | Both errata of the page are also placed on earlier pages of track G. The one about `Samples/Tetris/README.md:14` is on `make/patterns` (make-b1's `new:17`), and the one about `TetrisCommands.json.in:28` is on `make/automated-playtests` (make-b2's `new:20`). R46 keeps the row of the page that comes first in the outline. The check cannot see these pairs, because each row is a new item of its own file. | `make/project-tetris` drops its rows `new:16` and `new:27`. Its Covers keeps the two clauses (the cells are made once; the script waits with `until`) and links the pages that hold the errata. No words are added; the Fit's errata share (about 100 words) goes. | `allocation/make-c.md:151-152`; `allocation/make-b1.md:304`; `allocation/make-b2.md:737`; `critique/rulings-10.md:72-74`; `process.md:122-123` |
| critic-make-c-14 | should | missing-item | Starting state of `make/project-tetris` (stage 8) | Stage 8 sets the game's icon, but the page names no image to import: the Starting state lists only the four sounds. Style.md §7.4 and pipelines.md ask a tutorial to name every file it imports, with its source and license. | The Starting state names the icon. It is either the release's `Samples/Tetris/Assets/Icon.png` (a 256 × 256 render made for Strata), imported in stage 8, or the image of `tutorials/assets/` that `make/export` uses. About 25 words. | `allocation/make-c.md:115-116`, `:220-222`; `style.md:521-523`; `pipelines.md:894`; `allocation/make-a.md:1690-1691`; pin: `Samples/Tetris/CREDITS.md:6`; `Samples/Tetris/Tetris.stproj:7` |
