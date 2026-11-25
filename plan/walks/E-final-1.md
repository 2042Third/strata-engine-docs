# Walk E-final-1: track E (engine builder, persona E1), segment 1

Entries walked: `basics/computer`, `basics/git`, `basics/numbers`, `basics/data-structures`, `basics/trees-graphs`.
Package: Strata 0.8.0 Windows x64 (official package, StrataCLI and StrataEditor from it, headless `--no-gpu` editor under the perf lock).
Book: the built site at 127.0.0.1:4329, engine source read only at the places the pages name (docs-pin, 319075e3).
Work folder: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-1/` (sketches extracted to `sk3/`, git practice in `settings-demo/` and `proj-coin/`).

How the walk went: every page read in full; every sketch of numbers (8), data-structures (12) and trees-graphs (5) compiled with g++ 15 `-std=c++20 -Wall` and run (all outputs and all "Line N" notes match, no warnings); every worked number checked by hand; every engine quote and file the pages name found in docs-pin with the quoted lines (FloorDivide, SetCollide, CalculateMipCount, HierarchyComponent, LookupIndex, Scene.cpp 782-786, AssetStreamingQueue key, RadixSort 54-62, EngineModule cycle message and others); the git practice done in a scratch repository (init, status, diff, branch, merge, conflict, abort, patch, apply, grep, worktree) and on an editor-made project; one editor session (`project.create`, `script.build`).
Not walked: `git clone` of the engine and `git submodule update --init --recursive --depth 1` (a large download, not needed by the page's exercises); the editor-side half of the optional Coin Run exercises (see WK4); computer Practice 3 in the editor (see WK3).

## WK1
- Entry: `basics/computer`
- Page: How a computer runs a program
- Step: the start of the page ("What you need", the stage download)
- What happened: the page has no "What you need" section and offers no stage download for a reader who arrives here. It has "Before you start" (a link to "Your first game"), "Test out" and "Why you will need this". I installed the package as start/install says and went on; no stage project exists for the practice that says "in the project of your first game". The same holds for the other four pages of this segment.

## WK2
- Entry: `basics/computer`
- Page: How a computer runs a program
- Step: Practice 1 (Basic): "find its process id, its memory and its number of threads"
- What happened: I started the editor with StrataCLI (`launch --no-gpu`) and read `Get-Process StrataEditor`: 27 to 29 MB working set and 53 to 55 threads. The worked solution says "the editor uses hundreds of MB and tens of threads". The thread count matches, the memory does not. The figures are for a headless editor without a graphics device, which a CLI reader may well use; the page does not say that a window and GPU change the number. I used PowerShell, not Task Manager and its Details tab.

## WK3
- Entry: `basics/computer`
- Page: How a computer runs a program
- Step: Practice 3 (Medium): "change the full stop at the end of the first comment line ... press Ctrl+B ... read the lines that start [Scripts] >"
- What happened: (a) The first line of the package's `Scripts/Spinner.cpp` (project from `project.create`, template basic3d) is `// An example script. Attach it to an entity to make it spin: select the entity, Add Component > Script in the` and has no full stop at its end; the comment block runs over five lines. The text the page speaks of is not there. I added a space to that line instead (a guess). (b) The "Download the worked solution" ZIP (`exercise-3.zip`) holds a `Scripts/Spinner.cpp` that is a different file from the one the project has: no header comment, `DegreesPerSecond = 360.0f` (the project has 90.0f) and a changed comment (`Y axis!`). Copying it over the project replaces the reader's file. I did not apply it. (c) I ran `script.build` through the CLI (Ctrl+B is its editor form): the result's `log` shows `cmake.exe -S ... -B ... -G "Visual Studio 18 2026" ...` first (configure) and then `cmake.exe --build <folder> --parallel --config Dist -- /nodeReuse:false`, so the page's command line is right, with the extra `-- /nodeReuse:false` and the configuration Dist for the package's editor. A second build after a change and the "[Scripts] >" lines of the Console I did not read: the second session waited for the perf lock (held by another walker for the whole time) and I stopped it; I left no editor running.

## WK4
- Entry: `basics/numbers`, `basics/data-structures`, `basics/trees-graphs`
- Page: the optional Practice exercises on Coin Run ("Hard. Optional, starting from the end of Coin Run ...", "Optional, on Coin Run", "Optional, on your Coin Run project")
- Step: Practice, last exercise of each page
- What happened: there is no Coin Run project for a reader who arrives here (WK1), and no stage download. I did not build the game. For numbers and data-structures I ran the pages' own sketches (the clock drift sketch and the hash set sketch give the numbers the worked solutions give). For trees-graphs the exercise asks for a script that walks the hierarchy; I checked only that the names in the pseudocode exist in the SDK (`Scene::GetRootEntities`, `Entity::GetChildren`, `GetName`, variadic `Log::Info`) and did not run it in the editor.

## WK5
- Entry: `basics/trees-graphs`
- Page: Data structures II
- Step: the "Try it" boxes (six of them: walks, search tree, heap, spatial tree, union-find, radix)
- What happened: after the answer of each "Try it" the rendered page shows a paragraph that holds only the three characters `:::` (six times in the HTML, `<p>:::</p>`). It is a leftover of the source markup, not text. The answers themselves are right.

## WK6
- Entry: `basics/numbers`
- Page: Numbers in a computer
- Step: Practice 1 and Practice 4, "In the playground" ("log 13 and 0xFF from int variables", "In a script, Log shows six digits")
- What happened: the page names "the playground" without saying what it is or linking to it; an E1 who tested out of the programming primers does not know the word (it is taught on programming-1, "A playground is a script of your own"). I guessed it means a script in a project and ran the numbers as standalone programs instead; the sketch outputs and the worked solutions agree.

## WK7
- Entry: `basics/computer` (and the other four)
- Page: the strip "Previous and next on your track" at the foot of the page
- Step: leaving `basics/computer` for `basics/git`
- What happened: the entries I was given go computer, git, numbers, data-structures, trees-graphs, but on the Engine builder track the strip of `basics/computer` says Next: "The tools: the terminal, files and a code editor", and `basics/git`'s strip says Previous: "Finding bugs: a method, the log and the debugger" (the Beginner strip says "Project: Coin Run"). The page's own Test out list sends an E reader to `basics/tools`, not to git. I opened `basics/git` by its address. Later strips are consistent (git, numbers, data-structures, trees-graphs, then C++ memory).

## Answers

Checks were run with the official 0.8.0 package under the perf lock, in `docs-work/walkfix-E1` (`measure.ps1`, results
in `measure.txt` and `log-window.json`, project from checkpoint 5 of `start/first-game`). The changed tutorial file
(`basics/computer` exercise 3) passed with the pin build and with the package (`runs/`). The log lists no patches under
"## Built by the integrator".

### WK1
- Fixed on `basics/computer`, `basics/numbers`, `basics/data-structures` and `basics/trees-graphs`. Why: a primer has
  no "What you need" by the book's style (style.md §7.4 gives it to tutorials only; a primer's "Before you start" lists
  its Needs), but the practice items that need a project named one that a reader of track E may not have: "the project
  of your first game" with no download, and Coin Run, which track E never makes.
- Change: computer's Practice 3 names `FirstGame` or the download at the last checkpoint of "Make it spin with a script"
  on `start/first-game`, opened with **File ▸ Open Project...**; the Coin Run items of numbers, data-structures and
  trees-graphs name Checkpoint 4 at the end of "Ship the finished game" on `make/project-coin-run` (WK4). `basics/git`
  needs no change: its first four items make their own repository, and its fifth works on any project the editor
  made, as the walker did.

### WK2
- Fixed on `basics/computer`. Why: the worked solution gave the windowed editor's figure only. Measured with the
  package on the first game's project: a windowed editor with a GPU has a working set of 225 to 229 MB and 80 threads;
  `StrataCLI launch --no-gpu` has 28 MB and 55 threads, the walker's figures.
- Change: the answer gives both, about 230 MB and 80 threads with a window, about 30 MB and 55 threads without a
  window and graphics device, and says why (no graphics driver, no pictures kept for the GPU). Notes: "Track walk
  E-final-1".

### WK3
- Fixed on `basics/computer` and its tutorial file. Why: (a) "the first comment line" was meant as the comment above
  the class, but the file's first line is the template's header comment, which has no full stop at its end. (b) The
  solution's `Spinner.cpp` was a copy without the header comment, so copying it changed more than one character; its
  360 degrees and `OnCreate` are those of Your first game, not of a new project (90 degrees). (c) The page did not
  name `Dist` or the `-- /nodeReuse:false` that the Visual Studio generator adds
  (`StrataEditor/src/Editor/ScriptBuild.cpp:451-460`).
- Change: Practice 3 names the file and the line, `// Turns its entity around the world's Y axis.` above
  `class Spinner`. `tutorials/basics/computer/exercise-3/Spinner.cpp` is now `start/first-game`'s file with only that
  full stop changed to "!", and the answer says so and tells a reader of another project to change the character
  instead of copying. The answer names `--config Dist` for the installed Strata and the `-- /nodeReuse:false` ending;
  the tutorial file checks that ending too. Measured: the `[Scripts] >` lines read `cmake.exe -S ... -B ... -G ...`
  (first build only) and `cmake.exe --build <project>/.strata/Scripts/Build --parallel --config Dist --
  /nodeReuse:false`; during the second build, after the comment change, the tree was editor, `cmake.exe`,
  `MSBuild.exe` (twice), `Tracker.exe`, `cl.exe`, as the answer says. Passed with the pin build and the package.

### WK4
- Fixed on `basics/numbers`, `basics/data-structures` and `basics/trees-graphs`. Why: tracks.md gives these optional
  items to a track B reader, who owns Coin Run; the pages offered a reader of track E no copy.
- Change: each item names Checkpoint 4 at the end of "Ship the finished game" (`make/project-coin-run`), the zip whose
  `CoinRun.stproj` opens with **File ▸ Open Project...**. The checkpoint holds what the items use: the clock of
  numbers is the field `TimeLimit` of `CoinRunGame` on the entity `Game` (now named on the page), and the scene has
  the `Walls` entity that trees-graphs asks for.

### WK5
- Fixed on `basics/trees-graphs`. Why: each of the six "Try it" lines and its `:::answer` stood inside the
  `:::example` box with a fence of the same length, so the answer's closing line closed the example and the next
  `:::` was left as text.
- Change: each example now closes before its "Try it", which follows it with its answer, as on
  `basics/data-structures` and `basics/computer`. The same nesting stands, outside this segment, on `basics/tools`
  (lines 112, 208, 242), `make/input` (77, 253), `worlds/why-streaming` (219) and `automation/agents` (155); those
  pages' fixers should check them, and a lint for it belongs to the tool builder.

### WK6
- Fixed on `basics/numbers`. Why: the answers of Practice 1 and 4 used "the playground", which
  `basics/programming-1` teaches, without a link; a reader who tested out of that page does not know the word.
- Change: Practice 1's answer links "The playground is a script of your own" on `basics/programming-1`, and Practice
  4's answer names the two headers the logging lines need (`<iomanip>`, `<sstream>`).

### WK7
- Rejected. Why: the strip follows track E's list in `plan/tracks.md`, entries 7 to 13: `basics/computer`,
  `basics/tools`, `basics/programming-1`, `-2`, `-3`, `basics/debugging`, `basics/git`. So computer's next page is
  "The tools" and git's previous page is "Finding bugs", and the Test out box's "next page of your track" is right
  too. The segment the walker was given skipped entries 8 to 12; a reader of the track meets the pages in the strip's
  order.

## Confirm

Walker: E-final-1 confirm, persona E1. Package 0.8.0 (official, StrataCLI and StrataEditor), one session per perf-lock hold, no editor left running by me. Work folder `docs-work/walk-E-final-1/`.
The book at 127.0.0.1:4329 was still the build of 15:22, from before the fixes (its Practice 3 still said "the full stop at the end of the first comment line", its trees-graphs still had six `<p>:::</p>`). I merged `book/write` into `site/preview`, rebuilt `dist` (the preview script stops on its empty `scripts/preview-omit.txt`: `grep` exits 1 under `pipefail`, so I ran its steps by hand) and served that build on port 4331; everything below is read from it.

### WK1 and WK3: confirmed
- Start: `basics/computer` Practice 3 names `FirstGame` or the download at the last checkpoint of "Make it spin with a script"; the link leads to `start/first-game`, whose stage-5 ZIP I downloaded and opened (`FirstGame.stproj`). No guessing, no side trip.
- The line `// Turns its entity around the world's Y axis.` is above `class Spinner` as the page says. I changed the full stop to "!" and ran `script.build` (the form of Ctrl+B). The Console lines: `cmake.exe -S ... -B ... -G "Visual Studio 18 2026"` (first build only) and `cmake.exe --build <project>/.strata/Scripts/Build --parallel --config Dist -- /nodeReuse:false`, as the answer says. The process watcher saw `cl.exe` under `Tracker.exe` under `MSBuild.exe` under `cmake.exe` under the editor; the second build, with no change, started `cmake.exe` and `MSBuild.exe` but no `cl.exe`: the answer's claims hold.
- The solution ZIP's `Scripts/Spinner.cpp` differs from my edited file in no byte (`diff` empty) and from the checkpoint's file on that one line only.

### WK2: confirmed (one small figure)
- Windowed editor (`launch --project FirstGame --window-size 1280x720`): working set 224 and 227 MB, 80 threads. `--no-gpu`: 22 MB, 55 threads. The answer says about 230 MB and 80 threads, about 30 MB and 55 threads; the first pair matches, and the second pair's 30 MB is 22 MB here, which the answer's "tens of MB" and "about" cover. I read the figures with `Get-Process`, not Task Manager.

### WK4: confirmed
- Checkpoint 4 at the end of "Ship the finished game" (`make/project-coin-run`, stage-4 ZIP) opens with `CoinRun.stproj`, builds (`script.build` ok) and has the entity `Game` with `CoinRunGame` and the field `TimeLimit`.
- Numbers Practice 6: with `TimeLimit` 600000 the HUD text stays `Time: 600000` after 5, 100, 400 and 800 frames (1341 fixed steps): the frame adds nothing, as the answer says. With 20000 it reads 20000, 19998, 19992 and 19978; 1339 steps are 22.3 s, so the display agrees with the time that passed, and the 5.5 % drift is too small to see in the whole seconds the HUD shows (the sketch shows it).
- Trees-graphs Practice 3: I wrote the page's depth-first pseudocode as a script (`SDK` calls `Scene::GetRootEntities`, `GetChildren`, `GetName`, `Log::Info` all exist; it needed `#include <vector>` and `ST_SCRIPT_CLASS`) plus a breadth-first loop with a growing head; it compiled, ran from `OnCreate` and logged `DFS 0 Walls` and `BFS 0 Walls` with the walls at depth 1.
- Data-structures Practice 6: the sketch runs as the page says, but the checkpoint's coins are all named `Coin` (the prefab's name), not `Coin1`..`Coin6`; a reader who wants to test in the game must name them first. The exercise says "Keep the collected coins' names", so I took the sketch's names as invented. Small mismatch, not blocking.

### WK5: confirmed
- Built `basics/trees-graphs`: zero `<p>:::</p>`; each of the six "Try it" lines (walks, search tree, heap, spatial tree, union-find, radix) follows the example it belongs to, with its answer after it.

### WK6: confirmed
- The answer of numbers Practice 1 links "The playground is a script of your own" to the right section of `basics/programming-1` (anchor exists). I made the Playground there as the page says (`entity.create`, `script.create`, `script.build`, `script.add`, `play.start`): the Console showed `thirteen 13 ff 255 binary 13`, and the Practice 4 lines with `<iomanip>` and `<sstream>` showed `plain sum 1` and `digits 1.00000012`. The includes are named, nothing is missing.
- Side note, not the book's: my first run edited `Playground.cpp` a second after the template's build and the next build said "the module was up to date" without compiling it; touching the file and building again compiled it. It did not happen with the Spinner edit, which was made well after its build; I did not look further.

### WK7: confirmed (rejected stays right)
- The built strips on track E: `basics/computer` Next is "The tools: the terminal, files and a code editor"; `basics/git` Previous is "Finding bugs: a method, the log and the debugger", Next "Numbers in a computer"; this matches `plan/tracks.md` entries 7 to 13.
