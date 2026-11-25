# Walk E-final-8: track E (engine builder, persona E1), segment 8

Entries walked: `world/what-a-world-is`, `world/ecs`, `world/scene-graph`, `world/systems`, `world/interpolation`, `world/reflection`.
Package: Strata 0.8.0 Windows x64 (official package from `docs-package-0.8.0`: StrataEditor, StrataCLI; every editor session run under the perf lock). Book: the built site at 127.0.0.1:4329; engine source only as the pages quote it (read in `docs-pin` at 319075e3).
Work folder: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-8/` (`world_*.txt` page texts, `sk/` the 11 extracted sketches, `b/` their builds, `hold1.ps1` `hold2.ps1` the scripts run under the lock, `h1/` `h2/` the editor answers, `proj-tp` a copy of Samples/ThirdPerson, `proj-fov` a copy whose Course scene file holds a field of view of 200).

How the walk went: all six pages read in full. All 11 sketches were taken from the pages' sketch blocks and compiled with g++ `-std=c++20 -Wall -Wextra` (glm from the package's `StrataScriptCore/ThirdParty/glm` for the nlerp sketch): no warnings, and every output equals the page's output. The "Line N" notes of every sketch match the sketch (counting its lines without the extra blank lines my extraction added). Every engine excerpt (about 55) starts and ends on the lines the heading names in `docs-pin`. Check-yourself and exercise answers recomputed by hand (cache lines 1,875 and 6,250, door frame 4, versions 1,048,581 and 3,145,737, frontier S T U V W, update-check pace 1, 4, 7 and 1, 5, 9, step caps 4/8/16/32, accumulator 203 ms gives 8 steps, 11 dropped, 10 ms kept, alphas 0.65, 0.8 and 0.747, order A D B C): all as printed. Perf numbers (MoveRoot100k 0.328 ms, MoveRoot1M 6.57 ms, MoveLeaf100k, CleanTransformUpdate1M, Delete10kOf100kRoots 47 ms), test names, file paths and the 5.5 ms against 2.6 ms of the release notes exist as the pages say.
Editor runs (two holds of the lock, no editor left running): ThirdPerson headless, opened `Scenes/Course.stscene`: 288 entities; Camera, Sun and `BlockTall (1)` hold exactly the components of the table of what-a-world-is, and the block's Translation (-4, -4, 4) and Scale 2 equal the figure; the log line "Engine modules: Input, Scene, Renderer, Physics, Audio, Animation, Scripting, World, GameUI. Scene systems update in the order UI, Scripting, Animation, World, Physics, Audio" equals the systems page. Scene graph by commands: car/wheel/bolt give world x 10, 12, 12.5 and after the car moves 20, 22, 22.5; a keep-world reparent under a parent at x 10, scale 2 gives local offset 2 and scale 0.5; the sheared child reparented to the top level gets scale (1.581, 1.581, 1); a cycle is refused. Reflection by commands: `component.set` FOV 200 is refused with "Camera.PerspectiveFOV must be between 1 and 179, not 200" and `component.get` keeps 60; "wide" is refused; an unknown property is refused; a lower-case component name works; `component.get` lists `inactive` reasons that change with Projection; `component.add UIImage` on a bare entity adds UIRect too, a second add changes nothing; a second `PointLight` add with new values changes the light (Intensity 9); the scene file with FOV 200 opens as 179 with no warning about the camera. Play started paused, 3 steps: time 0.05 s, 3 fixed steps, interpolation enabled in `play.state` and `physics.stats`.

Not walked: everything that needs a source build or a debugger (the Medium "trace it yourself" exercises of ecs, systems, interpolation and reflection; the Visual Studio break at `MarkTransformDirty`; the doctest cases and test runs of "How it is tested"; the Spinner system, the `IWindQuery` service, the changed queue of the "build from the front" Hard exercise and the Spinner interpolation test; the Hard exercises of scene-graph, interpolation and reflection that write engine code or tests). The Add Component figure of reflection is an SVG I could not look at; its group lists equal what `component.list` answers. Side steps: none to other book pages; I used `docs-pin` only for the line checks above and `Tools/PerfLock.py`.

## WK1
- Entry: `world/what-a-world-is`
- Page: What a game world is made of
- Step or section: the start of the entry ("What you need", stage download)
- Kind: guessed
- What happened: the task says a reader starts at the "What you need" section of the first entry and may take a stage download. None of the six pages has such a section or a download: each has "Before you start", a list of earlier pages. I took the installed package for the programs, and nothing on the page says what a reader who arrives here has built or installed (the page needs no build, the exercises of later pages say "a Debug build").

## WK2
- Entry: `world/reflection`
- Page: Reflection: one registration, many uses
- Step or section: Exercise Basic, "send `{"entity": "<id>", "component": "Camera", "values": {...}}` through StrataCLI"
- Kind: guessed
- What happened: the page gives bare JSON and no command line. I used `'<json>' | StrataCLI call component.set -` (the form of make/with-an-agent), because Windows PowerShell 5.1 strips the quotes of an inline argument (met in segment 7). The command worked and the error text equals the page's; PowerShell shows it wrapped as `NativeCommandError`. The page does not say which form to use, how to get `<id>` (I used `entity.find` with a name), or that the project must first open the Course scene (`scene.open`).

## WK3
- Entry: `world/interpolation`
- Page: Drawing between fixed steps
- Step or section: Exercise Medium, the nlerp sketch (`#include <glm/glm.hpp>`)
- Kind: guessed
- What happened: the sketch needs glm and the page does not say where a reader finds it or how to compile it. I found glm in the package (`StrataScriptCore/ThirdParty/glm`) and added it as an include path; the output then equals the page's.

## WK4
- Entry: `world/scene-graph`
- Page: The scene graph
- Step or section: Exercise Basic ("start the editor from Visual Studio ... make it stop when it enters `Scene::MarkTransformDirty`")
- Kind: left the book
- What happened: the exercise needs a source build with a debugger, which the package does not hold. I read the chain it names in `docs-pin` (`component.set` in `EntityCommands.cpp`, `CommandUtils::ApplyComponents`, patch, `OnTransformChanged`, `MarkTransformDirty`): all names exist as the answer says. The same holds for the "trace it yourself" exercises of the other pages and for the doctest exercises (no test program that a reader can rebuild).

## WK5
- Entry: all six
- Page: the task's lock command
- Step or section: running a program under `PerfLock.py`
- Kind: failed
- What happened: `python` is not on the PATH of the Bash or PowerShell tool of this machine ("command not found"), so the lock command and my page-text script did not start. I called the MSYS2 Python by its full path (`C:\msys64\mingw64\bin\python.exe`). The book's pages do not use Python; this is the machine.

## Answers

The log lists no patches under "## Built by the integrator", and none of the six pages has a tutorial file, so no
`tutorials.py run` or `patch` applies. The reflection steps were rerun with the official v0.8.0 package in Windows
PowerShell 5.1, headless, in one hold of the perf lock (`docs-work/walkfix-E-final-8`, `hold.ps1`, `out/run.txt`); both
editors it started quit, none was left running, and the pin clone is untouched. The nlerp sketch was compiled with `cl`
and the package's glm (`nlerp/`). Every changed page passes `tools/pagecheck.py`. No engine fault was found, so no page
got an `## Engine` note; each changed page's notes have a section "Track walk E-final-8".

### WK1
- Fixed on `world/what-a-world-is`. Why: a concept or internals page has no "What you need" and no stage download by
  the book's style (style.md §7.4, as the answers of E-final-1, E-final-3, E-final-4 and E-final-7 say), but the
  first page of the part never said that it needs nothing, nor which programs the part's later pages use.
- Change: a paragraph after the introduction says that the page needs no project and no download, that its exercise is
  a program for the compiler of How a C++ program is built (linked to "Open a terminal that finds a compiler"), that the
  figure's scene opens from **Open Sample...** as a copy of **Third-Person Adventure**, and that the next pages use the
  installed Strata for commands and the source build of Your first engine change for the exercises that trace or test
  the engine.

### WK2
- Fixed on `world/reflection`. Why: the Basic exercise gave bare JSON for "a scratch project", with no command line,
  no way to get the id and no word that the Course scene must be opened. Track E reaches this page before
  `editor/commands`, so the step must give the complete lines to paste (process.md, "Allocation"; `plan/critique/rulings-4.md`, R11).
- Change: the exercise copies **Third-Person Adventure** from the launcher and runs four lines from the Strata folder in
  OS tabs: `scene.open` of `Scenes/Course.stscene`, `entity.find` of `Camera`, `component.set` with 200 and
  `component.get`; the Windows tab pipes the parameters in and says why. It names the id, `350D7DDD7ED21DD5`, which the
  scene file stores, and the edit by hand (`"PerspectiveFOV":60` to 200 in the copy's `Assets/Scenes/Course.stscene`,
  then `scene.open` and `component.get` again). The answer says `component.get` keeps 60, the file opens as 179, and
  the Console has no warning about the camera, only the sample's own.
- Measured: `entity.find` answered `350D7DDD7ED21DD5`; `component.set` exited 1 with the message `Camera.PerspectiveFOV
  must be between 1 and 179, not 200`; `component.get` read 60; the inline JSON argument failed in PowerShell 5.1
  ("params must be a JSON object or array"). After the file was changed while the editor ran, `scene.open` of the open
  scene read it again and the field read 179; a new editor on that file also read 179. From Warn up, the log held only
  "scripts not built yet" and two morph-target lines of `RobotExpressive.glb`.

### WK3
- Fixed on `world/interpolation`. Why: the Medium exercise's sketch includes `glm/glm.hpp`, and the page did not say
  where glm is or how to compile; Blending and smoothing, on the page's Needs, gives the lines but the exercise did not
  point there.
- Change: the exercise says that glm's headers are in the Strata folder, links Blending and smoothing's "Why you will
  need this", and gives the two lines: `cl /std:c++20 /EHsc /I "<Strata folder>\StrataScriptCore\ThirdParty\glm"
  sketch.cpp` on Windows, `c++ -std=c++20 -I "<Strata folder>/StrataScriptCore/ThirdParty/glm" sketch.cpp -o sketch`
  on Linux and macOS. Measured: the sketch built with `cl` (Visual Studio 2026) and the package's glm prints the page's
  four lines.

### WK4
- Fixed on `world/scene-graph`. Why: the walk's rules give the walker only the package, but a reader of track E has
  the source build of `core/first-change` (entry 38), which `core/debugging` puts under the debugger. The exercise said
  only "start the editor from Visual Studio", without naming that build, how to give the editor a project, or where the
  doctest case goes.
- Change: the exercise says it runs in the source build of your first engine change because the installed Strata holds
  no source; it starts `StrataEditor` with `--project` and a copy of a sample under the debugger, as Debugging the
  engine (linked to "The engine under a debugger") starts `StrataTests`; it sets the breakpoint once the project is
  open, because loading links the scene's roots and marks each one dirty (`Scene::FinishLinking`,
  `Strata/src/Strata/Scene/Scene.cpp:1243-1251`); and the doctest case goes into
  `StrataTests/src/Scene/SceneTransformTests.cpp`. The "trace it yourself" and test exercises of the other pages are
  covered by WK1's paragraph, which names the source build for them; ecs already says "a Debug build of the tests".
  Words were cut elsewhere on the page to stay within size XL (10,000).

### WK5
- Rejected. Why: the step that failed is not a step of the book. None of the six pages runs Python or `PerfLock.py`
  (`grep` of the pages: no match), and the walker's own notes say so. The lock command is the walk's instruction to
  the agent; in this machine's PowerShell `python` resolves to `C:\msys64\mingw64\bin\python.exe` (checked with
  `Get-Command python`), the program the walker then called by its full path, and the lock ran with it here. A tool
  shell without that folder on its PATH is the walker's environment, which no page can change; the walk instructions
  are the planner's files, not a page's.


## Confirm

Walked by E1 as a reader of the built book at http://127.0.0.1:4329/strata-engine-docs/ (Strata 0.8.0 package). The served build did not hold every fix: it was built before the last two commits of `book/write` (`docs-site` is at 5e9f7dc1, the fixes of WK1 and WK4 are in 79aba53f and 9aeb8a9b).

### WK1: not confirmed (the fix is not in the served book)
- `world/what-a-world-is`, served: the introduction goes straight to "When you opened your first game..." and the page holds no paragraph with "needs no project and no download" (searched for "no project", "no download", "compiler": no hit). A reader gets the "Before you start" list (four pages) and nothing about the compiler, the sample or the two programs, so the reader must guess.
- The book's source (`src/content/docs/world/what-a-world-is.md`, line 31) holds the paragraph: no project and no download; the exercise's program needs the compiler of "How a C++ program is built" (linked to its terminal section); the figure's scene opens as a copy through Open Sample... and Third-Person Adventure; the next pages use the installed Strata for commands and the source build of "your first engine change" for tracing and tests. Read as written, it names everything: no guess. Confirms once the preview is rebuilt from `book/write`.

### WK2: fixed, confirmed
- Headless, package 0.8.0, copy of Samples/ThirdPerson, one hold under the perf lock, Strata folder as the working directory, the four Windows-tab lines exactly as printed (PowerShell 5.1, piped with `-`).
- `scene.open` opened Course (288 entities); `entity.find` gave `350D7DDD7ED21DD5`; `component.set` failed with `Camera.PerspectiveFOV must be between 1 and 179, not 200` (code -32602); `component.get` read `"PerspectiveFOV": 60`.
- The copy's Course.stscene held `"PerspectiveFOV":60` once; changed to 200; first and last line again: `PerspectiveFOV` read 179. A second hold read `log.read` (minLevel Warn): only the sample's own three warnings (scripts not built, two morph-target imports), none about the camera. Matches the page's answer, including its remark about those warnings. Editor quit. No mismatch, no guess, no leaving the book.
- Note: the exercise text is "Start the editor, press Open Sample... ... Copy and Open"; I used the headless route for the copy, as the task allowed.

### WK3: fixed, confirmed
- The exercise (served) says glm's headers are in the Strata folder, links Blending and smoothing, and gives both lines. Saved the sketch as sketch.cpp and ran `cl /std:c++20 /EHsc /I "<Strata folder>\StrataScriptCore\ThirdParty\glm" sketch.cpp` (Visual Studio 2026 environment), then `.\sketch.exe`: the four lines (0.001, 0.033, 0.919, 6.755 degrees for 10, 30, 90, 170) equal the page's output exactly. No guess needed.

### WK4: not confirmed in the served book; the source is right
- Served `world/scene-graph` Exercise 1 still reads "start the editor from Visual Studio, make it stop when it enters Scene::MarkTransformDirty ..."; it names no source build, no `--project`, no debugging link, no breakpoint timing and no `SceneTransformTests.cpp`. A reader of track E must guess which build and how to give it a project.
- The source (`scene-graph.md`, lines 1528-1536) names: the source build of "your first engine change" (linked), "the installed Strata holds no source", `StrataEditor` with `--project` and a sample's copy under the debugger, the link to Debugging the engine's "The engine under a debugger" (`../core/debugging.md#the-engine-under-a-debugger`), the breakpoint set "once the project is open", and `StrataTests/src/Scene/SceneTransformTests.cpp`. All five names are present. The reason for the timing (`Scene::FinishLinking` marking roots dirty) is not in the exercise text; the instruction alone is enough to follow. No debugger run (no source build in the walk).

### Result
WK2 and WK3 confirmed. WK1 and WK4 are fixed in the book's source but absent from the served preview: rebuild the preview from `book/write` (79aba53f) and repeat the two reads.

## Answers (after confirm)

Both entries are right in the source at `book/write`; the confirmer read a preview built before their commits. Read
again in the source, with no change.

### WK1 world/what-a-world-is
- Holds in the source: line 31, right after the introduction, says the page needs no project and no download, that its
  one exercise is a program for the compiler of How a C++ program is built (linked to "Open a terminal that finds a
  compiler"), that the figure's scene is the Third-Person Adventure copy from **Open Sample...**, and that the next pages
  use the installed Strata for commands and the source build of Your first engine change for the exercises that trace or
  test the engine.

### WK4 world/scene-graph, Exercise 1 (Basic)
- Holds in the source (lines 1528-1536): the source build of Your first engine change (the package holds no source),
  `StrataEditor` started with `--project` and a sample's copy under the debugger as Debugging the engine shows, the
  breakpoint set once the project has opened, and the doctest case in `StrataTests/src/Scene/SceneTransformTests.cpp`.
  The pin's file has that path. A debugger run was not made; the build it needs is the patch build, which
  `tutorials.py patch` used for segment E:9 (below in E-final-9) and E:5.

## Confirm (after the second answers)

Read as a fresh reader: the pages at book/write, the 0.8.0 package, the pin, under the perf lock; results in `docs-work/walk-final-confirm-2`. Every entry below: through without guessing, leaving the book or a mismatch.

### WK1 world/what-a-world-is
- Holds. Source line 31, right after the introduction, says: no project and no download, the compiler of How a C++ program is built (link and anchor exist), Open Sample... then Third-Person Adventure, and the two programs of the next pages. A reader needs nothing else.

### WK4 world/scene-graph, Exercise 1
- Holds. Lines 1528-1536 name the first-change source build, `StrataEditor` with `--project` under the debugger as Debugging the engine does (anchor `the-engine-under-a-debugger` exists), the stop in `Scene::MarkTransformDirty` once the project is open, and `StrataTests/src/Scene/SceneTransformTests.cpp` (exists at the pin; `GetTransformUpdateCount` exists). Read only.
