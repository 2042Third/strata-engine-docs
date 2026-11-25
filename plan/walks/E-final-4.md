# Walk E-final-4: track E (engine builder, persona E1), segment 4

Entries walked: `basics/math-geometry`, `basics/math-change`, `basics/math-interpolation`, `basics/color`, `basics/signals`, `basics/math-probability`, `basics/math-sphere`, `basics/threads`.
Package: Strata 0.8.0 Windows x64 (official package from `docs-package-0.8.0`: StrataEditor and StrataCLI; every engine program run under the perf lock, two holds, no editor left running).
Book: the built site at 127.0.0.1:4329; engine source read in `docs-pin` (319075e3) only for the quotes the pages name.
Work folder: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-4/` (`*.txt` page texts, `src/<page>/x<N>.cpp` every code block of the page as the copy button gives it, `out/` the program runs, `Playground.cpp` and `Playground2.cpp` the exercise scripts, `session1.ps1` and `session2.ps1` the two editor holds, `proj/FirstScript` the Coin Run project of make/first-script stage 4).

How the walk went: every page read in full, every internal link of the eight pages answers 200. Every sketch (66 programs with a `main`, out of 19, 18, 17, 15, 11, 16, 12 and 32 code blocks per page) extracted from the page, compiled with g++ 15 `-std=c++20` against glm and run: all 66 compile, and every printed output equals the "Output of the sketch" block under it (the threads sketches too, whose printed numbers do not vary). Every "Line N" note of the sketches checked against the numbered code: no off-by-one. Every engine excerpt the pages quote (Common.slang 25-39, Exposure.slang 14-21, Scene.slang 171-182 and 380-395, AODenoise.comp.slang 74-89, IBL.slang 26-34 and 59-65, Common.slang 41-46, Gameplay.h 32-48 and 62-70, FollowCamera.cpp 73-79) compared with the file: all equal. The claims about Ray.cpp (1e-8, 1e-12), AABB.h (IsValid, empty box), Scene.h (gravity, fixed step, 8 steps), PhysicsWorld.cpp (4 sub-steps), RigidBody (damping 0.05, mass 1), TextureCooker.cpp (Mitchell, sRGB conversion) and the SDK (Raycast, GetDrawnPosition, SmoothDamp, Range, Chance, AddImpulse, AddForce) hold. Every "Try it", "Check yourself", test-out and Practice answer worked by hand and compared with the page (about 150 answers): all agree. Threads Practice 1 to 4 ran in the editor as a script (see WK3): plain int 1,197,787 and load-then-store atomic 1,573,682 (the page: about 1.1 million at -O0, and 1.2 to 1.8 million for the atomic), mutex and fetch_add 2,000,000 each (26 ms and 13 ms here; the page's 50 and 18 are "on the test computer"), scoped_lock 200,000 rounds without a deadlock, sum 5050. Threads Practice 5: a std::thread that calls `SetWorldPosition` got `false`, the entity did not move, and the Console showed the Error "SetWorldTransform: scripts can only use the engine from the main thread" while `Log::Info` worked in the thread, as the page says.

Not walked: the optional "Hard" exercises "in Coin Run" of math-geometry, math-change, math-interpolation, color, signals, math-probability and math-sphere (see WK4); threads Practice 5 as written (the ball of Coin Run: I moved the Playground entity instead); the pictures (the eight pages hold no `img`, only inline SVG, 57 to 71 of each; I read their text labels, I did not see them); Linux and macOS.

## WK1
- Entry: `basics/math-geometry` (the same on the seven pages after it)
- Page: Geometry for engines: rays, planes, boxes and intersection tests
- Step: the start of the page ("What you need", the stage download)
- What happened: the page has no "What you need" section and offers no stage download; it has "After this page you can", "Before you start" (two links: Matrices and transforms, Cameras and projection) and "Test out". None of the eight pages has either, and none has a command tab or a "You should see" (no StrataCLI call anywhere; the pages are paper-and-program work). I started with the installed package and the text of the page, which is all the page needs; the page does not say in words that a reader arriving from the track has nothing to download and nothing to set up.

## WK2
- Entry: `basics/math-geometry` (and every page after it)
- Page: Geometry for engines: rays, planes, boxes and intersection tests
- Step: the Sketches, and Practice "Hard. Write a function that returns the box that holds a list of points ... Run it"
- What happened: the book never says how to compile and run a sketch. The pages show `#include <glm/glm.hpp>` programs and their output ("Why do these programs start with lines I have not seen?" points to Programming 3, which explains the lines, not the compiling); signals even says "You can read only their output and the numbered notes". Yet Practice asks the reader to write and run programs (math-geometry Hard, math-change Hard, math-sphere Medium and Hard, math-probability Basic and Hard, threads Basic, Medium and Hard). The editor's Playground script is the only place the book gives for a program, and the sketches have a `main`. I left the book: compiled the copied code with the MSYS2 g++ already on this machine, taking glm from `StrataScriptCore/ThirdParty/glm` of the package (`-I <package>/StrataScriptCore/ThirdParty/glm`); a reader without a compiler on the path and without that include folder would not know where to start. All sketches ran as printed.

## WK3
- Entry: `basics/threads`
- Page: Threads, atomics and races
- Step: Practice, "Run exercises 1 to 4 in Playground, the script of Programming from zero I"
- What happened: the page names the Playground script but not the project it lives in or where to get it. I took a side step to `basics/programming-1` ("The playground is a script of your own": the project is Coin Run as "Your first script" leaves it, or its last checkpoint download) and to `make/first-script` for the download (`stage-4.zip`, which unpacks to `FirstScript/CoinRun.stproj`). Then, with the commands of programming-1 (`entity.create`, `script.create`, `script.build`, `script.add`, `play.start`, `log.read`, `play.stop`), `StrataCLI launch --headless` and the Visual Studio 2026 on this machine, the build took 7 s and the four exercises printed their lines in the Console. Nothing failed. The page does not say which build configuration the script is built in, so the plain int total cannot be compared with the worked solution's two figures (mine, 1,197,787, is near its -O0 figure, not the exactly 2,000,000 of -O2).

## WK4
- Entry: `basics/math-geometry`, `basics/math-change`, `basics/math-interpolation`, `basics/color`, `basics/signals`, `basics/math-probability`, `basics/math-sphere`, `basics/threads`
- Page: the optional "Hard" exercise of each page (Coin Run)
- Step: Practice, "Hard. Optional, in Coin Run ..."
- What happened: I guessed. The pages say "from the end state of Coin Run", "as Coin Run finishes it", "as Project: Coin Run leaves it" or just "in Coin Run" and link the Coin Run page, but no page offers the project's download, and `make/project-coin-run` has four checkpoints (`stage-1.zip` to `stage-4.zip`) and none is labelled "end state". I did not walk the seven exercises (each needs that project, a ball, coin or HUD script of my own and a build) and used the project of make/first-script for the threads exercise because Playground needs it (WK3). The worked solutions (CoinPop and the camera follow, CoinPlacer, the time bar, the dome of coins) were checked as the plain C++ sketches next to them, which compile and print what the page says.

## Answers

Checks were run in `docs-work/walkfix-E4`. Every sketch of the eight pages (56 files under `sketches/`) compiled with
`cl /std:c++20 /EHsc` (Visual Studio 2026, glm from the 0.8.0 package) and with g++ `-std=c++20`, and both printed the
same output (`cl/`); the exact Windows line the pages now give was run in PowerShell in a developer environment
(`cmdtest/`). The threads exercises ran as a `Playground` script on Checkpoint 4 of `make/first-script` with the
official 0.8.0 package, headless, under the perf lock (`session.ps1`, `session.out`); the editor quit, and the
StrataEditor still running afterwards (pid 50304, started 17:55 by `walk-G-final-9`'s hold) is another walk's. None of
the eight pages has a tutorial file, so no `tutorials.py run` applies. The log lists no patches under "## Built by the
integrator". No engine fault was found, so no page got an `## Engine` note; each page's notes have a section "Track
walk E-final-4" with the checks. Every changed page passes `tools/pagecheck.py`.

### WK1
- Fixed on all eight pages. Why: a primer has no "What you need" and no stage download by the book's style (style.md
  §7.1 and §7.4, as answered for E-final-1 and E-final-3), and no step of these pages calls the editor, so a command tab
  or a "You should see" has nothing to show. But the page never said in words that nothing needs setting up.
- Change: the last paragraph of "Why you will need this" now opens with "This page needs no project and no download"
  (color), "Only the optional Coin Run exercise needs a project" (the six math and signals pages) or "Only the Practice
  needs a project, which it names" (threads), and goes on with WK2's lines.

### WK2
- Fixed on all eight pages. Why: `basics/build` (before these pages on track E) teaches `cl` and `c++` on a three-file
  program, but not the C++20 flag the sketches need (`cl` defaults to C++14, too old for `std::optional` and
  `std::numbers`) nor where `glm` comes from; the pages never joined the two.
- Change: the same paragraph says each sketch is a whole program, to be saved as `sketch.cpp` and compiled in the
  terminal of How a C++ program is built (linked to its section "Open a terminal that finds a compiler"), and gives the
  two lines: `cl /std:c++20 /EHsc /I "<Strata folder>\StrataScriptCore\ThirdParty\glm" sketch.cpp` then
  `.\sketch.exe` on Windows, `c++ -std=c++20 -I "<Strata folder>/StrataScriptCore/ThirdParty/glm" sketch.cpp -o
  sketch` then `./sketch` on Linux and macOS. The four pages whose sketches use no glm (math-change, signals,
  math-probability, threads) give the lines without `-I`. Without a compiler the reader reads each output and its
  notes. Words were cut on math-geometry and math-sphere (a repeated output list, a duplicate mistake, a repeated count)
  to stay within size L.

### WK3
- Fixed on `basics/threads`. Why: (a) the Practice named `Playground` without its project; (b) the worked solution
  gave only the figures of a program built with `-O0` and `-O2`, while the editor builds the script in its own
  configuration. Measured with the package: the build ran `--config Dist`, which takes the Release flags
  (`StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:38`); five runs of the plain `int` left 1,130,698 to
  1,428,447, the load-then-store atomic 1,101,195 to 1,193,566, the mutex and `fetch_add` 2,000,000 each in about 24 ms
  and 16 ms. The walker's 1,197,787 is one of these, not the `-O0` figure.
- Change: the Practice intro links the section "The playground is a script of your own" of Programming from zero I and
  names its project: your Coin Run, or the project at the last checkpoint of Your first script, linked. Exercise 1's
  answer says that the installed Strata builds scripts in `Dist`, optimized as Release, and that five runs on Windows
  left 1.13 to 1.43 million (the atomic 1.10 to 1.19 million), beside the program's `-O0` and `-O2` figures; exercise
  2's notes add the script's 24 ms and 16 ms. Exercise 5 works on the same project (it is an explain-and-predict
  exercise; the walker's check on the Playground entity matches its answer).

### WK4
- Fixed on the seven pages with a Coin Run item; on `basics/threads` by WK3. Why: the items said "the end state of
  Coin Run", "as Coin Run finishes it" or "in Coin Run" without naming a checkpoint.
- Change: math-geometry, math-change, math-interpolation, signals, math-probability and math-sphere now start their
  item "Optional, on your Coin Run or Checkpoint 4 of Ship the finished game", both linked, as E-final-3's pages do.
  Read against that checkpoint (`public/downloads/tutorials/make/project-coin-run/stage-4.zip`): the ball's script is
  `BallControl`, with an `OnFixedUpdate`, which math-geometry now names; math-change asks for a new script on the
  ball; signals' answer names the script that turns the coins, `Coin` in `Scripts/Coin.cpp`; math-probability's
  script was named `CoinPlacer`, which the checkpoint already holds (it places the five coins), so it is now
  `RandomCoin`, for one coin; math-sphere's answer puts its loop in that `CoinPlacer`, which already waits for the
  prefab. Color's item was a computation that named "the optional Coin Run exercise", which the page does not have:
  it now names the time bar of the page on heads-up displays (linked) and asks for a program of the reader's own,
  which its worked solution already is.

## Confirm

Walker: E1, segment 4 confirmation. Work folder `docs-work/walk-E-final-4/confirm/` (`session.ps1`, `session.out`,
`Playground.cpp`, `proj/` from `stage-4.zip` of make/first-script, `cr4/` from `stage-4.zip` of make/project-coin-run);
`scr/run.ps1` and `wk1-result.txt` one level up. The package was the official 0.8.0 one; every editor run was under the
perf lock, one hold, and the editor quit (a StrataEditor seen afterwards, pid 41760 started 18:18:57, is another
walker's).

One finding about the check itself: the built book served at 127.0.0.1:4329 is not rebuilt since 11 November. Its eight
pages still show the old text (no "needs no project" paragraph, no `sketch.cpp` line, "Hard. Optional, from the end
state of Coin Run", no link to the last checkpoint). I therefore read the fixed pages from the book's source
(`src/content/docs/basics/*.md` at 40a398cf), with the links as the source writes them; the downloads I took from the
served site (stage zips) and they match. A reader of the served preview gets none of the four fixes until it is rebuilt.

### WK1 and WK2: fixed (in the source)
- The last paragraph of "Why you will need this" of all eight pages now says what the page needs (no project, or only
  the optional Coin Run exercise, or only the Practice) and gives the lines. I read it as a reader: save a sketch as
  `sketch.cpp`, open the terminal of build ("Open a terminal that finds a compiler": Developer PowerShell for VS, the
  section answers `cl` with "for x64"), run the given line, then `.\sketch.exe`.
- Run: all 43 sketches of the eight pages, each copied from its block, saved as `sketch.cpp` and compiled with exactly
  `cl /std:c++20 /EHsc [/I "<Strata folder>\StrataScriptCore\ThirdParty\glm"] sketch.cpp` (Visual Studio 18, x64; `/I`
  on geometry, interpolation, color and sphere, none on the other four, as the pages say). All 43 compile and every
  output equals the page's output block (0 differences). No guessing: the flag, the glm folder and the terminal are
  all named; the four pages without glm give the line without `/I` and need none.
- Small remark, not a fault: the line says `<Strata folder>`; a reader must know that it is the unpacked package folder
  (install page), which the glm path then finds (`StrataScriptCore\ThirdParty\glm` exists there).

### WK3: fixed (in the source)
- The Practice now links the section "The playground is a script of your own" and names the project (Coin Run, or the
  last checkpoint of Your first script, linked to its section). From there I took `stage-4.zip` of make/first-script
  (answers 200), opened `FirstScript/CoinRun.stproj` headless, and followed the section's command tab: `entity.create`,
  `script.create`, replace the file text, `script.build` (0 errors, 7.0 s), `script.add`, `play.start`, `log.read`,
  `play.stop`, `editor.quit`. No step needed the book to be left.
- Result with exercises 1 and 2 as one `Playground`: plain `int` 1,275,203 (page: 1.13 to 1.43 million, in range);
  load-then-store atomic 1,232,308 (page: 1.10 to 1.19 million: this one run is 3 % above the range, so the range is a
  little narrow, the claim "left 1.2 to 1.8 million in the program" still true); mutex total 2,000,000 in 24.9 ms (page:
  about 24 ms); `fetch_add` total 2,000,000 in 13.4 ms (page: about 16 ms). Totals and the order of the times agree
  with the worked solutions. Suggest "1.10 to 1.25 million" for the atomic.

### WK4: fixed (in the source)
- All six Coin Run items (geometry 5, change 5, interpolation 7, signals 6, probability 6, sphere 5) now say "on your
  Coin Run or Checkpoint 4 of Ship the finished game" with the link `project-coin-run.md#ship-the-finished-game`; the
  section exists and ends in `::checkpoint{stage=4}`; its zip downloads (200, `ProjectCoinRun/`).
- The scripts the items name exist in that project: `BallControl` (with `OnFixedUpdate`, geometry 5), `Coin` (with
  `OnUpdate`, `OnTriggerEnter`: signals 6, interpolation 7), `CoinPlacer` (sphere 5). `RandomCoin` (probability 6) does
  not exist there and clashes with nothing (scripts: BallControl, Bump, Coin, CoinHud, CoinPlacer, CoinRunGame,
  GhostSwitch, Spinner, VolumeKeys). Change 5's "new script" and "jump pad" take names no script holds.
- Color Practice 6 reads as a program of its own ("In a program of your own"), needs no project; its worked solution
  sketch (`basics-color-time-bar.cpp`) is among the 43 and matches its output.
- I did not write the seven Hard exercises themselves (as in the first walk); only their start state was confirmed.

### Verdict
WK1, WK2, WK3 and WK4 are fixed in the book's source: a reader gets through without guessing, without leaving the
book (beyond the links the pages give) and without a mismatch. The only open point is that the served preview must be
rebuilt for a reader to see them, and the atomic range of threads exercise 1 (see WK3).
