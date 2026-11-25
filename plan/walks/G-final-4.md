# Walk log: track G (persona G0), segment 4, at v0.8.0

Entries walked: `basics/programming-1`, `basics/programming-2`, `basics/programming-3`, `basics/debugging`.
Package: official Strata 0.8.0 Windows package (`Strata-0.8.0-windows-x64`), headless StrataEditor driven by StrataCLI,
one editor session under the perf lock. Project made in `walk-G-final-4/CoinRun` (template basic3d).

Not walked: the Visual Studio and launch-file attach steps, breakpoints, stepping, watches and the call stack of
`basics/debugging` (no window, no debugger); the endless-loop freeze of `basics/programming-2`; clicks in the
Hierarchy, Scripts menu, Inspector, Console and Problems panels (done through commands, read through `log.read` and
`script.status`).

## WK1
- Entry: `basics/programming-1`; page: same; section: "Before you start" (the page the track starts at).
- Kind: left the book.
- The page has no "What you need" section and offers no stage download. "Before you start" only links to Your first
  script and Your first game. I had no project, so I made one with `project.create` (template basic3d) after finding the
  command in `StrataCLI list`; a reader cannot get to a project that holds a Spinner and a Coin Run coin from this page.

## WK2
- Entry: `basics/programming-1`; section: "The playground is a script of your own" (also the Practice sections of all
  four pages).
- Kind: guessed.
- The steps are written for the mouse only (plus button, Scripts > New Script, Add Component > Script, Ctrl+B, Play,
  read the Console). There is no command tab. I mapped them to `entity.create`, `script.create`, `script.add`,
  `script.build`, `play.start` and `log.read` by reading `StrataCLI list`; nothing in these four pages names them.

## WK3
- Entry: `basics/programming-1`; section: "A script is steps that run in order" (the quoted Spinner).
- Kind: did not match.
- "The editor writes the script below for you." The Spinner.cpp that the basic3d template wrote has a five-line comment
  header before `#include`, tabs, and no trailing comment on the `DegreesPerSecond` line; the quote shows 22 lines
  without them. The code is the same; the line numbers 236-257 of the quote cannot be found in the file.

## WK4
- Entry: `basics/programming-1`; section: Practice, "Hard" (Spinner with IsGold) and the "Basic" const exercise.
- Kind: guessed.
- The exercises say "the cube", "your spinning script". My project had no cube (the template gives a ground, camera,
  sun, sky), so I put Spinner on a new empty entity and set IsGold with `script.add` fields. The rotation after 2.05 s
  at 180 degrees per second was right (9 degrees past a full turn). The const line failed with
  "error C3892: 'cs': you cannot assign to a variable that is const", which names the variable as the page says.

## WK5
- Entry: `basics/programming-2`; section: Practice, "Hard. Coin Run item".
- Kind: guessed.
- The exercise loads `Prefabs/Coin.stprefab`, which only exists after the Coin Run tutorial. I made an entity named Coin
  and ran `prefab.create` with that path. With it, five coins stood 2 m apart (entity count 9 to 14). The page does not
  say where a reader without the tutorial gets the prefab.

## WK6
- Entry: `basics/programming-3`; section: Practice, "Hard" (three planted errors).
- Kind: did not match.
- The worked solution says the first row names the missing `;` (or the line below) and that later first rows name
  `bonus` and then `Counter`. With the Visual Studio compiler the first row, after the first build, was
  `C2065 'Counter': undeclared identifier` (line 31), followed by knock-on rows for `counter`. The `;` row (C2143, line
  46, the line below) came only after I added the include, then `bonus`. So the order of the three fixes the page gives
  is the reverse of what a Windows reader sees. Eight rows appeared at the first build, as the page warned.

## WK7
- Entry: `basics/programming-3`; section: Practice, "Medium" (GetProperty and GetScript).
- Kind: did not match.
- Without a point light the first line shows `intensity -1` as the page says, but the Console also gets a Warn line:
  "GetProperty (called by script 'Playground' on entity 'Playground'): entity 'Playground' has no PointLight component".
  The page says only that the optional is empty and does not mention the warning. With the light added (`component.add`),
  the line shows `intensity 10`; `GetScript<Unused>()` was null as described.

## WK8
- Entry: `basics/programming-3`; section: "Reading a compile error" (the double field).
- Kind: did not match.
- The page shows the first error in Script.h and says "Your own line is in the lines above it: Scripts/Coin.cpp:13:2:
  required from here". On Windows the diagnostics list had three rows, all in `Script.h` (C2338 with the message
  "Unsupported script field type: use bool, int32_t, float, ...", then C2027 and C2065), and none names my file. My line
  (`Playground.cpp(53,26)`) is only in the build log under "see reference to function template instantiation". The
  page says Visual Studio words it differently, but not that no row names the file.

## WK9
- Entry: `basics/programming-3`; section: Practice, "Hard. Start from Coin Run and its coin prefab".
- Kind: guessed.
- "Put BobbingCoin on the coin prefab in the place of Coin": I added BobbingCoin with `script.add` to the Coin instance
  in the scene and did not write it back to the prefab (the page names no step). The coin turned (rotation changed) and
  bobbed (y 1.22 and then 0.78 at about 1.2 s and 1.9 s). `std::sin` compiled without a `<cmath>` include.

## WK10
- Entry: `basics/debugging`; section: Practice 1, 2, 3 and 5, and the worked bug "The coins crawl".
- Kind: left the book.
- These need a debugger attached to a window editor. I could not do them. I did the method with log lines instead:
  Playground with `m_Time += deltaTime * 2.0f` wrote "Time is up" 1.48 s after play started (page: about 1.5 s); the
  Hard exercise with `OnLateUpdate` resetting `m_Counter` logged `counter 1` in every frame and never reached ten, as the
  page says. `OnLateUpdate` exists as a callback (script.status lists it). The radians-twice numbers (0.0262, 0.000457)
  were not read in a watch.

## Answers

### WK1
- Fixed. Why: `basics/programming-1` is a primer and has no "What you need"; the project it works in was named only by
  the two links of "Before you start". The walker started this segment without that project.
- Change: "The playground is a script of your own" now opens with the project the page works in: Coin Run as
  `make/first-script` left it (five instances of `Prefabs/Coin.stprefab` turned by `Coin`), or the project of
  `start/first-game` (the cube `Top` turned by `Spinner`), and, for a reader with neither, the download at the last
  checkpoint of `make/first-script`.

### WK2
- Fixed on `basics/programming-1`. Why: the playground steps had only the editor's form; the tutorials before them
  (`make/first-script`, `start/first-game`) offer a command tab, so the primer is the odd one out. The editor tab stays
  complete on its own (style.md §10, track G).
- Change: the four playground steps are a `sync=how` tab set; "With a command" lists `entity.create`, `script.create`,
  `script.build`, `script.add`, `play.start`, `play.stop` and `log.read`, with the build before `script.add` (it takes
  built classes only). The Practice sections of the other three pages run in this playground, so they name no
  commands of their own; programming-3's exercise 5 now names the Inspector steps (WK9).

### WK3
- Fixed. Why: the quote is lines 236-257 of `StrataEditor/src/Editor/ScriptProject.cpp`; the file that the template
  writes, `Scripts/Spinner.cpp`, starts with the five comment lines of `MakeExampleScript` (lines 230-234) and a blank
  line, so its `#include` is line 7 and no line number of the page fits it. The field comment is in the file the
  editor writes (line 15); the walker's file had lost it to the walker's own edit for exercise 5.
- Change: the paragraph before the quote names the file, says that the quote omits its five comment lines, and says
  that the numbers are the engine file's: in `Spinner.cpp` each line is 229 lower (line 238 is line 9). "The same
  lines" of `Coin` became "the same code".

### WK4
- Fixed with WK1. Why: the exercises name "the coin or cube" of the project that the page's Needs leave; the walker
  had a bare template project. The results matched (rotation, the C3892 error naming `speed`'s variable).
- Change: the project paragraph of WK1 says which coin or cube the exercises mean and where to get it.

### WK5
- Fixed. Why: track G reaches `basics/programming-2` from `make/first-script`, whose project holds
  `Prefabs/Coin.stprefab`; the exercise said "Coin Run" without saying that this is that project, and a reader from
  `start/first-game` has no prefab at all. The walker's result (five coins 2 m apart) matched.
- Change: Practice 7 says that the prefab is the coin of Coin Run that `make/first-script` gave `Coin`, and that a
  reader from `start/first-game` downloads the last checkpoint of `make/first-script` and does the exercise there.

### WK6
- Fixed. Why: the order the page gives is the order of the file, and it holds for an `OnCreate` that has only the four
  planted lines. A build with the 0.8.0 package and Visual Studio 18 2026 of exactly that (work folder
  `docs-work/walkfix-G4`, `out/build-P0.txt` to `build-P3.txt`) gave five rows: C2143 `missing ';'` on the line below,
  C2065 `bonus`, C2065 `Counter`, C2146 and C3861 for `counter`; then `bonus` and `Counter` after the first fix, then
  `Counter`, then success. The walker's `OnCreate` still held exercise 2's `Counter counter(3);` at line 31, above the
  planted lines, and it had removed exercise 2's `#include "Counter.h"`: so `Counter` came first. The page never said
  to clear `OnCreate`, and with exercise 2's include in place there is no missing include to find.
- Change: Practice 4 starts from an empty `OnCreate`, without exercise 2's include and with `Counter.h` and
  `Counter.cpp` kept; the worked solution lists Visual Studio's five rows and says what a `Counter` row that comes
  first means.

### WK7
- Fixed. Why: at the pin `GetProperty` on a missing component calls `ScriptSystem::ReportProblem`
  (`Strata/src/Strata/Scripting/ScriptHostAPI.cpp:655`), which logs a Warn line once per distinct message
  (`ScriptSystem.cpp:1541-1558`). That is the engine's design for a failed host call, not a fault; the page omitted it.
- Change: the worked solution of Practice 3 says that without the light the engine writes, once per play, a warning
  that ends `has no PointLight component`, and that the call still gives back an empty optional.

### WK8
- Fixed. Why: the Problems panel keeps only lines with a severity (`ParseDiagnosticLine`,
  `StrataEditor/src/Editor/ScriptBuild.cpp:313-381`); the place of the field's line is in note lines (MSVC's
  `<file>(<line>,<column>):` and `see reference to function template instantiation`, GCC's `required from here`). A
  build of a `double` field with the package gave three rows, all in `Script.h` (C2338 `static assertion failed`, C2027,
  C2065), and the Console lines `...\Scripts\Playground.cpp(26,2):` (`out2/`). The page's `static_assert failed` was
  wrong too.
- Change: "Reading a compile error" says that every row names `Script.h`, gives Visual Studio's three rows, and tells
  the reader to type `Coin.cpp(` in the Console's **Search** box, where two lines end in `Scripts\Coin.cpp(13,2):`.
  The panel's lack is in the page's notes under "## Engine".

### WK9
- Fixed. Why: "Put `BobbingCoin` on the coin prefab in the place of `Coin`" named no step, and "write ... as a class
  `Coin` in `Coin.h` and `Coin.cpp`" did not say that the reader's project already has `Coin.cpp` from
  `make/first-script`. The walker's result (turn and bob) matched; `std::sin` needs no include, as the page assumes.
- Change: Practice 5 says to split `make/first-script`'s `Coin.cpp` into `Coin.h` and `Coin.cpp`, and names the
  Inspector steps: the cross of `Coin` in the Script component (`InspectorPanel.cpp:1247-1272`, `script.remove`),
  **Add Script...** and `BobbingCoin`, then **Apply to Prefab** in the component's menu.
  Checked with the package in `make/first-script`'s last checkpoint, by the commands of those steps: `prefab.apply`
  updated the other four coins, and after 45 fixed steps `Coin (2)` stood 0.249 m up and had turned 67.5 degrees
  (`docs-work/walkfix-G4/out3/`).

### WK10
- Rejected. Why: the steps need a windowed editor and a debugger, which the reader of track G has (`start/install`
  checks Visual Studio or the build tools; the page's attach sections give each system's way); the walker drove a
  headless editor through StrataCLI and had none. The page says at the head of its Practice which exercises need a
  breakpoint and that exercise 4 needs none. What the walker could do with log lines matched the page: "Time is up" at
  1.48 s (page: about 1.5 s), `counter 1` in every frame, `OnLateUpdate` a callback. The two radians numbers are the
  output of the page's sketch `basics-debugging-radians.cpp`, which pagecheck compiles and runs. A fresh walker with a
  windowed editor and Visual Studio walks Practice 1, 2, 3 and 5.

## Confirm

Walker: confirm pass, 2026-11-24, official 0.8.0 package, one headless editor session under the perf lock, work folder
`docs-work/walk-G-final-4`. The served preview was stale at the start (built 12:21, before the answers: no command tab
on `basics/programming-1`); the walker merged `book/write` into `site/preview`, rebuilt, and copied `dist/` over the
staged folder the server serves, then walked the book as built from that. Start state of WK1: no project; the page's
link goes to `make/first-script`, where the walker took checkpoint 4 (`stage-4.zip`) and opened it.

- WK1 holds. The new paragraph names the project and the download. The link leads to the page of the tutorial, not to
  the ZIP: the reader finds "Checkpoint 4" there (one step, not a mismatch). The project opens with five instances of
  `Prefabs/Coin.stprefab`, each with `Coin`; after `script.build` and `play.start` all five turn (Y rotation changes
  every second, five "Coin starts with ..." lines).
- WK4 holds. Practice 2: `const float speed` at 180 turns twice as fast; `speed = 45.0f;` fails with
  `error C3892: 'speed': you cannot assign to a variable that is const`. Practice 5: with `IsGold` set on one coin, 60
  fixed steps turn it 180 degrees and a plain coin 90.
- WK2 holds, with two small gaps the walker crossed without guessing: `<id of Playground>` is the `id` that
  `entity.create` answers (the page does not say so), and `script.create` with `"open": true` starts the machine's
  default application for the file (on this machine Visual Studio, left open; the walker could not close it). Build
  before `script.add` is right; `play.start`, `play.stop` and `log.read` show the logged line.
- WK3 holds. `Scripts/Spinner.cpp` of a new basic3d project starts with five comment lines and a blank line;
  `#include` is line 7, `using namespace Strata;` is line 9 (engine line 238), the field is line 15 (244), `OnUpdate`
  line 17 (246), `ST_SCRIPT_CLASS` line 25 (254).
- WK5 holds. `CoinLine` with the page's code: entity count 23 to 33 (five coins of two entities), translations x = 0,
  2, 4, 6, 8, y = 1.
- WK6 holds. From an empty `OnCreate` (no include, `Counter.h`/`.cpp` kept) the first build gave five rows in the
  page's order: C2143 (line 19, the line below), C2065 `bonus`, C2065 `Counter`, C2146, C3861; after the `;` four, after
  `bonus` three (`Counter` first), after the include success and both lines in the Console.
- WK7 holds. Without the light: `intensity -1`, one Warn line `GetProperty (called by script 'Playground' on entity
  'Playground'): entity 'Playground' has no PointLight component`, written before the intensity line; `Speed is 1`; no
  `Unused` script.
- WK8 holds only where `Coin.cpp` uses a float in `angleAxis`. With a `double` field and the `speed` local of
  programming-1's Practice 5, Problems shows three `Script.h` rows (C2338, C2027, C2065) and the Console shows two lines
  ending `Scripts\Coin.cpp(31,2):`. With the plain checkpoint-4 `Coin.cpp` (field `double`, `DegreesPerSecond` in
  `angleAxis`) the build stops earlier with two rows in the reader's own file: `Coin.cpp(18,31) C2672 'glm::angleAxis':
  no matching overloaded function found` and `Coin.cpp(18,19) C2737 'turn': const object must be initialized`; no
  `Script.h` row. The page's "line 13" fits neither file (the field line is 25 in the checkpoint's `Coin.cpp`, 31 after
  Practice 5). The page does not tell the reader to make this edit, so a reader who tries it from the plain file meets
  rows the page does not show.
- WK9 holds. Split `Coin.h`/`Coin.cpp` and `BobbingCoin.cpp` built clean (new files were found by the build); removing
  `Coin` from one coin, adding `BobbingCoin` and applying to the prefab (`script.remove`, `script.add`, `prefab.apply`:
  four instances updated) left all five coins with `BobbingCoin`; after play all five turned and their height changed
  (0.08, then 0.24 above their base), `std::sin` needed no include.
- WK10 not repeated (rejected).

## Answers (after confirm)

Measured with the 0.8.0 package in a headless editor (`docs-work/walk-final-fix/drive.py`, `results.json`): a Basic 3D
project, `script.create` of `Playground` (the field `float Speed = 1.0f;`, `ST_SCRIPT_FIELD(Speed);` on line 28), and
`Coin.cpp` from checkpoint 4 of make/first-script.

### WK8 basics/programming-3, Reading a compile error
- The confirmer is right: the rows depend on how the field is used. `double Speed` in `Playground`, which no code reads,
  gave three `Script.h` rows (C2338 `static assertion failed: 'Unsupported script field type: ...'`, C2027, C2065) and
  two Console lines ending `Scripts\Playground.cpp(28,2):`, the line of `ST_SCRIPT_FIELD(Speed);`, then `see reference to
  function template instantiation ...`. `double DegreesPerSecond = 90.0` in checkpoint 4's `Coin.cpp` gave two rows in
  `Coin.cpp` only: (18,31) C2672 `'glm::angleAxis': no matching overloaded function found` and (18,19) C2737 `'turn':
  const object must be initialized`. The page's "line 13" belonged to its GCC example, not to the reader's file.
- Change: the GCC block is introduced as the output for a file `Coin.cpp` whose line 13 registers a `double` field. The
  reader then tries it in `Playground` (`double Speed` for `float Speed`, which nothing else reads); the Windows rows are
  the three `Script.h` rows, and the Console search is `Playground.cpp(`, whose two lines end in
  `Scripts\Playground.cpp(<line>,2):`, the line of `ST_SCRIPT_FIELD(Speed);` (28 in the file New Script wrote). A new
  paragraph says that the same change in the `Coin` of Your first script fails earlier, in `Coin.cpp` at the line of
  `glm::angleAxis`, with C2672 and C2737. pagecheck PASS; the page has no tutorial file.

## Confirm (after the second answers)

Read as a fresh reader: the pages at book/write, the 0.8.0 package, the pin, under the perf lock; results in `docs-work/walk-final-confirm-2`. Every entry below: through without guessing, leaving the book or a mismatch.

### WK8 basics/programming-3, Reading a compile error
- Holds. In a project with the New Script Playground, `double Speed` built with three Problems rows, all `Script.h` (C2338 at 785, C2027 and C2065 at 790); the Console search `Playground.cpp(` showed two lines ending `Scripts\Playground.cpp(28,2):`, 28 being the line of `ST_SCRIPT_FIELD(Speed)`, as the page says. The Coin of Your first script with `double DegreesPerSecond` gave C2672 and C2737, both in `Coin.cpp` at line 18 (`glm::angleAxis`, `turn`), as the new paragraph says. A reader gets through.
