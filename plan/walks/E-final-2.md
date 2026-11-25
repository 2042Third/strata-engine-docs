# Walk E-final-2: track E (engine builder, persona E1), segment 2

Entries walked: `basics/cpp-memory`, `basics/cpp-classes`, `basics/cpp-generic`, `basics/cpp-modern`, `basics/build`.
Package: Strata 0.8.0 Windows x64 (official package from `docs-package-0.8.0`; StrataCLI and StrataEditor run under the perf lock, headless `--no-gpu`, one hold for each group of calls, each with a private `STRATA_SESSION_DIR`, `STRATA_RECENT_PROJECTS` and `STRATA_SCRIPT_BUILDS_DIR` in the work folder; preferences untouched; no editor left running).
Book: the built site at 127.0.0.1:4329. Engine source read in `docs-pin` at 319075e3, only to compare the quoted excerpts and the names the pages give.
Work folder: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-2/` (page texts and HTML, `sk-*` the extracted sketches with their outputs, `hello`, `hello2` the build page's programs, `proj` the editor project, `variants/` the exercise scripts, `stage2.ps1` and its outputs).

How the walk went: every page read in full. All 63 sketches (memory 15, classes 12, generic 18, modern 15, build 3, the practice ones included) were extracted from the page, compiled with g++ 15 `-std=c++20 -Wall -Wextra` and run: no warnings, every output equals the page's (two differ only by a trailing space), and every "Line N" note points at the right line of the shown file. The engine quotes (Base.h, Script.h, Log.h, UndoStack.h, Property.cpp, PropertyBuilder.h, AssetResidency.cpp, Input.cpp, Application.cpp, GLFWWindow.cpp, AudioEngine.cpp, CommandLine.cpp, Assert.h, JobSystem.cpp, FileWatcher.h, RadixSort.h, ComponentRegistry.h) are equal to the pin, and the files, constants and functions the pages name exist as described (including "Strata's sources define no concept": none found; `requires { &T::OnCreate; }` is in Script.h). Every worked number and "Try it" was recomputed by hand.
Exercises in the editor (project from `project.create`, template basic3d, a script `Playground` made with `script.create`): memory 1 to 4, classes 1 to 4, generic 1 to 4 and modern 1 to 4, each as the page says (types above the class, statements in OnCreate, `Log::Info` for `std::cout`), built with `script.build`, played and read with `log.read`. All logs equal the worked solutions (memory 1: make x, make y, make z, drop z, make w, drop w, drop y, drop x; memory 3: 3, 2, true; memory 4: made 8, used 64; classes 3: value: pickup, reference: coin; and so on). The compile errors the pages predict were seen: `unique_ptr` copy (MSVC C2280, "attempting to reference a deleted function") and `Largest(3, 2.5f)` (C2672, no matching overloaded function). The classes "Hard" exercise (Pickup, Coin, SpeedBoost) and the memory "Hard" fix (ask `GetScript` again each frame) were built as scripts in a stand-in project: `GetScript<Pickup>()` is null, `GetScript<Coin>()` and `GetScript<SpeedBoost>()` reach the right object and `pickup->OnCollected()` runs the right version; `GetScript<Coin>()` on a missing entity is null.
Build page on Windows: the three files, `cl /EHsc /c`, `dumpbin /symbols`, `link`, a compile error, a link error (LNK2019, LNK1120), `lib`, a two-library link, the CMake project with the Visual Studio generator (configure, build, build again, touch the .cpp: compile and 2 links; touch the .h: 2 compiles and links), `--config Release`, the `stop` program in Debug and Release with 5 and -5 (only Debug with -5 stops, exit 3), the optional by-hand build of the editor's `Scripts/CMakeLists.txt` (it produced `CoinTestScripts.dll`). With MinGW g++ and ld: `nm -C`, the swapped link order (undefined reference to `Frame(...)`), the registry-in-a-static-library trap (printed only "main runs", then "registered" first when the object is named), `-DNDEBUG` (checks run: 0).

Not walked: the Linux and macOS tabs (the `nm` lines and the Linux link-order failure were run with MinGW's ld as a stand-in); the Coin Run checkpoint (the optional exercises on it, see WK3); the pictures (I read their captions and labels).

## WK1
- Entry: `basics/cpp-memory` (and `cpp-classes`, `cpp-generic`, `cpp-modern`, `build`)
- Page: the top of each page
- Step: "What you need" and the stage download for a reader who arrives here
- What happened: none of the five pages has a "What you need" section or a stage download. They have "Before you start", a list of the earlier pages, and nothing else. The practice items lean on a project: "the Playground script of Programming 1" (memory, generic, modern), "the playground project" (classes). A reader who arrives here, as the walk asks, has no Playground. I opened `basics/programming-1` (side step), read "The playground is a script of your own" and made a project with `project.create` and the script with `script.create`.

## WK2
- Entry: `basics/cpp-classes`
- Page: C++ classes in depth
- Step: Practice, first paragraph: "Run exercises 1 to 4 in the playground project"
- What happened: this is the only one of the four C++ pages that says "the playground project", with a lower-case p and no link. The others say "the Playground script of Programming 1" with a link. I guessed that it is the same script and used it.

## WK3
- Entry: `basics/cpp-memory`, `basics/cpp-classes`
- Page: the last, optional Hard exercise of each
- Step: "Optional, on the end state of make/project-coin-run" (memory) and "Optional, in your Coin Run project" (classes)
- What happened: memory writes the page name as plain text, not as a link, and says "end state" without naming a download. Classes names no page at all. generic and modern do link `make/project-coin-run` but also name no download or checkpoint. Track E never makes Coin Run, so a reader has no such project. I did not open the page. I built the scripts in my own stand-in project: the memory fix and the Pickup, Coin and SpeedBoost scripts of classes compile and give the page's answers there; the "collect the coin or rebuild while the game runs and watch the dangling pointer" step I did not run (undefined behavior needs the real HUD script).

## WK4
- Entry: `basics/cpp-memory`
- Page: C++ memory
- Step: "Walking a row by hand", Try it: "float values[4] lies at address 500 ... What address does values + 3 hold?"
- What happened: the answer reads "The pointer moves three elements of four bytes each: 500 + 3 x 4." and stops. It never gives the address, 512. The reader has to finish the sum. The worked example above it (row at 2000, `row + 2` is 2008) does give its result.

## WK5
- Entry: `basics/cpp-modern`
- Page: Modern C++ as Strata uses it
- Step: "After this page you can", fifth bullet
- What happened: the bullet is cut off in the page: "predict what a macro with arguments, an". It is cut in the HTML itself (the list item ends there), so no reader sees the end of the sentence. The other four bullets are whole.

## WK6
- Entry: `basics/build`
- Page: How a C++ program is built
- Step: "The linker joins object files and connects names", the `dumpbin /symbols` alternative to `nm -C`
- What happened: the page says dumpbin "prints the same facts in a longer format" and then explains the letters U and T. dumpbin prints no such letters. For `main.obj` it printed `UNDEF ... External | ?MakeGreeting@@...` and for `Greeting.obj` `SECT5 ... External | ?MakeGreeting@@...`, plus more lines with `Static`. I guessed that UNDEF stands for U and a section number for T. The page does not say how to read those words, and it shows only the Linux output.

## WK7
- Entry: `basics/build`
- Page: How a C++ program is built
- Step: "Two kinds of error", delete the `;` in main.cpp and compile
- What happened: the page shows the GCC message (`main.cpp:7:54: error: expected ';' before 'return'`) and says "it names a file and a line, here line 7", and that MSVC "words it differently ... but gives the same facts". MSVC printed `main.cpp(8): error C2143: syntax error: missing ';' before 'return'`: line 8, not line 7. The statement that ends at line 7 is reported at the next line. The link error matched: LNK2019, then LNK1120 "1 unresolved externals".

## WK8
- Entry: `basics/build`
- Page: How a C++ program is built
- Step: "Open a terminal that finds a compiler" (Developer PowerShell for VS)
- What happened: I cannot open the Start menu, so I could not start "Developer PowerShell for VS". `Launch-VsDevShell.ps1` failed here (`vswhere.exe` is not recognized), so I loaded the compiler's environment with `vcvars64.bat` from VS 2026 and put the CMake that belongs to Visual Studio first on the PATH. In my ordinary terminal `cl` was "not recognized" as the page says, but `cmake` was already found (an MSYS2 CMake, 4.2.2), unlike the page's "cmake are not recognized". After the setup, `cl` printed the x64 banner and the CMake default generator was "Visual Studio 18 2026", as the page's Windows tab says.

## WK9
- Entry: `basics/build`
- Page: How a C++ program is built
- Step: Practice 3, `echo -5 | .\stop.exe` "in Windows PowerShell"
- What happened: in my Windows PowerShell 5.1 the pipe gave `coins: 0` for 5 and for -5 in both configurations, and no assertion. The cause is on my side: this console is UTF-8, and PowerShell 5.1 then sends a byte order mark first (`\xef\xbb\xbf-5` seen by a test program), which `std::cin >> coins` cannot read. The same lines through `cmd /c "echo -5 | stop.exe"` gave the page's results: Debug with -5 stops with `Assertion failed: coins >= 0 && "coins cannot be negative", file ...stop.cpp, line 10`, exit code 3; Release prints `coins: -5`. A reader with the usual console codepage will probably get the page's result. The page does not warn about it.

## WK10
- Entry: `basics/cpp-memory`, `basics/cpp-classes`, `basics/cpp-generic`, `basics/cpp-modern`
- Page: the Practice items of the four C++ pages
- Step: building the Playground script with `script.build` after each edit (the page: "press Ctrl+B")
- What happened: in the headless editor the file watcher also builds a changed script by itself. In 4 of the 18 exercise variants I wrote, `script.build` answered `success: true, errorCount: 0, moduleChanged: false` although the file had just changed (once even with a line that cannot compile, the `unique_ptr` copy), and the next play printed the lines of the previous script. Reading the same variants again, built in a second session, gave the right answers every time. A direct `script.build` right after the file write gave the C2280 error as the page says. I cannot say whether this comes from the race of the watcher and my command or from the build; a reader who presses Ctrl+B a few seconds after saving may meet it. I waited 7 seconds after each write and compared the log with the script I had written to catch it.

## Answers

Checks were run in `docs-work/walkfix-E2`, 2026-11-24. The 60 sketches of the four C++ pages compiled warning-free with
`cl /std:c++20 /EHsc /W3` (Visual Studio 2026, 19.50, x64) and with g++ 15, and both printed the same output (`cl/`).
The build page's Windows lines ran in the x64 developer Command Prompt (`hello/run.cmd`, `run2.cmd`) and its pipes in
Windows PowerShell 5.1 (`hello/pipe.ps1`, `pipe2.ps1`). The exercise scripts ran with the official 0.8.0 package,
headless, under the perf lock, on a new project made with `project.create` and `script.create` (`session.ps1`,
`session.out`); the editor quit and none was left running. None of the five pages has a tutorial file, so no
`tutorials.py run` applies, and the log lists no patches under "## Built by the integrator". No engine fault was found,
so no page got an `## Engine` note; each page's notes have a section "Track walk E-final-2" with the checks. Every
changed page passes `tools/pagecheck.py`.

### WK1
- Fixed on all five pages. Why: a primer has no "What you need" and no stage download by the book's style (style.md
  §7.1 and §7.4, as answered for E-final-1, E-final-3 and E-final-4), but the pages never said in words what they need.
- Change: the end of "Why you will need this" now says "This page needs no download" and that only the Practice needs a
  project, the one that holds your `Playground`, linked to the section "The playground is a script of your own" of
  Programming from zero I (which names the project, or the download of Your first script's last checkpoint); generic
  and modern add Coin Run for the optional last exercise. A second paragraph says each sketch is a whole program and
  gives the two compile lines (`cl /std:c++20 /EHsc sketch.cpp`, `c++ -std=c++20 sketch.cpp -o sketch`), with the
  terminal of How a C++ program is built linked as "four pages on" (memory), "three", "two", "the next page". The
  build page says it needs no download and no project, only a compiler and CMake, and that only its optional last
  exercise opens the project that holds `Playground`.

### WK2
- Fixed on `basics/cpp-classes`. Why: the Practice said "the playground project", unlinked.
- Change: "Run every exercise in `Playground`, the script of Programming from zero I", linked to its section; memory,
  generic and modern now link the same section (they linked only the page, memory and modern as "Programming 1").

### WK3
- Fixed on `basics/cpp-memory`, `basics/cpp-classes`, `basics/cpp-generic`, `basics/cpp-modern`. Why: the optional
  exercises named Coin Run without a start, and on Checkpoint 4 of Coin Run the memory and classes exercises could not
  be done as written: the coins exist only in play (`CoinPlacer` makes them), so no `OnCreate` can take a coin's
  script; `Coin` lives in `Scripts/Coin.cpp`, which no other script file sees; and the memory answer said that a hot
  reload leaves the kept pointer dangling, while the new instance's non-field state starts over
  (`StrataScriptCore/include/StrataScript/Script.h:49-52`), so its pointer is `nullptr`.
- Change: memory's exercise 5 now runs in `Playground`: the given code makes an entity `Marker` with a script, keeps
  the pointer from `AddScript<Marker>()`, destroys the entity in frame 60 and logs frames 58 to 62; callouts explain
  lines 6, 12 and 14. The answer gives what the package showed (frames 58 to 60 `Marker`, then the warning
  `GetEntityName (called by script 'Playground' on entity 'Playground'): entity ... does not exist` and empty names),
  the fix (keep the `Entity`, `GetScript` every frame: `gone` in frames 61 and 62, also run), and the hot reload case
  as Script.h states it. Classes' exercise 5 now runs in `Playground` too: `Pickup`, `Star` and `SpeedBoost` above it
  (`Coin` would clash with Coin Run's `Coin`, `Gem` with exercise 1), two entities made with `AddScript`; the answer's
  script and its Console lines were run (`Star: GetScript<Pickup> is null: true`, `star collected`, `Boost: ...`,
  `speed boost collected`), and the plain sketch was renamed to match. Generic and modern now start "Optional, on Coin
  Run: your Coin Run, or Checkpoint 4 at the end of Ship the finished game, opened with File ▸ Open Project...";
  generic adds that the coins carry the tag `Coin` and appear once play starts and that the ball is `Ball`, read
  against the checkpoint (those two exercises were read, not run).

### WK4
- Fixed on `basics/cpp-memory`. Why: the answer did state 512, as "512. The pointer moves ...", but Markdown reads a
  paragraph that starts with "512." as an ordered list that starts at 512, so the number became a list marker and the
  walker's text had none.
- Change: "The address is 512. The pointer moves three elements of four bytes each: 500 + 3 × 4 = 512." The two
  test-out answers of `basics/build` that started "4." and "0." had the same fault and now start with words. Other
  pages with the pattern, left to their fixers: `basics/data-formats.md:781`, `threads.md:28`, `programming-2.md:318`,
  `763` and `776`, `programming-3.md:29` and `309`, `draw/skinned.md:397`.

### WK5
- Fixed on `basics/cpp-modern`. Why: the learn line was unquoted YAML, and YAML reads ` #if ...` as a comment, so the
  line ended at "an".
- Change: the line is quoted. `editor-ui/imgui` has the same fault ("the suffixes ## and ###"), left to its fixer.

### WK6
- Fixed on `basics/build`. Why: the page said `dumpbin` prints "the same facts" and explained only `nm`'s letters.
- Change: a paragraph gives `dumpbin /symbols main.obj | findstr MakeGreeting` (and for `Greeting.obj`) and reads its
  words: `UNDEF` where `nm` writes `U`, a section number such as `SECT5` where it writes `T`, the machine form of the
  name and then the readable one between round brackets, `External` for a name other files may use, `Static` for
  extra names only the file uses. Run: `UNDEF ... External | ?MakeGreeting@@...` and `SECT5 ... External`, as written.

### WK7
- Fixed on `basics/build`. Why: the page said MSVC gives "the same facts" as GCC's line 7.
- Change: the page quotes MSVC's `main.cpp(8): error C2143: syntax error: missing ';' before 'return'` (run) and says
  that it names line 8, where it met the `return`, because a compiler names the line where it noticed the mistake.

### WK8
- Fixed on `basics/build`. Why: the Start menu's **Developer PowerShell for VS** runs the 32-bit Windows PowerShell with
  `Enter-VsDevShell` and no architecture, which prepares the x86 compiler: its `cl` banner ends "for x86"
  (`VSCMD_ARG_TGT_ARCH=x86`, run), so the page's own check fails there. The `cmake` of another installation (here
  MSYS2's) can come first on the PATH.
- Change: the page sends the reader to **x64 Native Tools Command Prompt for VS** ("for x64", run), says every Windows
  line of the page runs in it as written (all were run there), and that Developer PowerShell for VS does not fit. "In
  an ordinary terminal, `cl` is not recognized"; `where cmake` must list the Visual Studio CMake first, else add
  `-G "Visual Studio 18 2026"` (or `17 2022`). The walker's `vswhere.exe` message also appears on this machine and does
  not stop the setup.

### WK9
- Fixed on `basics/build`. Why: as the walker found, Windows PowerShell 5.1 sends a byte order mark (`ef bb bf`) before
  piped text when its console is at code page 65001, also with `$OutputEncoding` ASCII; under code page 437 it does
  not (run). A reader with the UTF-8 option of Windows meets it.
- Change: Practice 3 runs `echo -5 | .\stop.exe` in the Command Prompt (Debug: the assertion, exit 3; Release:
  `coins: -5`, run), and the answer says what PowerShell 5.1 with a UTF-8 console does instead (`coins: 0` for every
  number). Practice 5 says the Command Prompt runs the `&&` line as written.

### WK10
- Fixed on the four C++ pages. Why: reproduced with the package and the walker's 18 files, written with checked bytes:
  `g1bad`, which cannot compile, built with `success: true`, `moduleChanged: false`, and the Console line
  `Script build 12 finished in 0.6 s (the module was up to date)`. The cause is the drive: `docs-work` lies on G:, an
  exFAT drive, which stores file times rounded to 2 seconds (a time set to 18:39:37.456 reads back 18:39:38.000; NTFS
  keeps it). A file saved within about 2 seconds of the last build's object file is then no newer than it, and MSBuild
  skips the compile, by the file-time rule that `basics/build` teaches. No file watcher builds scripts at the pin (the
  editor builds on Ctrl+B, the menu, the toolbar, the status pill, New Script and Play). Not an engine fault.
- Change: each Practice intro says that if the Console still shows the earlier code's lines, a build line ending
  `(the module was up to date)` compiled nothing, that a drive keeping times in steps of two seconds can hide a change
  saved right after a build, and to save again and press Ctrl+B.

### For the tool builder
- `tools/sketches.py:216` runs a sketch without `stdin=subprocess.DEVNULL`; `basics-build-stop.cpp` reads `std::cin`
  and once ran past the 10-second limit when pagecheck ran from a shell with an open input.

### Steps for the confirming walker
- From the start of track E's segment 2 with the 0.8.0 package: read the top of each of the five pages (WK1), follow
  the Playground link (WK2), and do memory and classes exercise 5 in `Playground` as written (WK3); generic and modern
  exercise 5 on Checkpoint 4 of Ship the finished game.
- Read memory's "Walking a row by hand" Try it answer and build's test-out answers 1 and 5 in the built site (WK4),
  and cpp-modern's fifth learn line (WK5).
- On Windows, open **x64 Native Tools Command Prompt for VS** and walk the build page from "Open a terminal" to
  Practice 3: `cl` banner, `where cmake`, `dumpbin ... | findstr MakeGreeting`, the deleted `;`, `echo -5 | .\stop.exe`
  (WK6 to WK9).
- Build the Practice variants with Ctrl+B (or `script.build`) and compare the Console with the written script; on a
  2-second drive, meet and handle "(the module was up to date)" as the Practice says (WK10).

## Confirm

Confirming walk, segment 2 (persona E1), 2026-11-24, with the official 0.8.0 package, headless editors under the perf lock
(`--no-gpu`, private `STRATA_SESSION_DIR`, `STRATA_RECENT_PROJECTS` and `STRATA_SCRIPT_BUILDS_DIR` in
`docs-work/walk-E-final-2/c/`, preferences untouched, no editor left running). Result: all ten fixes hold. Three small
notes at the end; none stops a reader.

Setup fault, not a book fault: the preview at 127.0.0.1:4329 still served the build of 17:51, 33 commits before these
fixes (every page still had the old text). I merged `book/write` into `site/preview`, rebuilt `docs-site/dist` with the
steps of `scripts/preview.ps1` and copied it into the folder the running server serves (`docs-site/stage`). All reads
below are of that build.

- WK1 holds. Each of the five pages ends "Why you will need this" with "This page needs no download. Only the Practice
  needs a project: the one that holds your Playground script, which Programming from zero I puts on an empty entity"
  (generic and modern add Coin Run for the optional exercise, build says it needs no project at all), then the
  sketch paragraph with `cl /std:c++20 /EHsc sketch.cpp` and `c++ -std=c++20 sketch.cpp -o sketch`. No page has a "What
  you need" section, as the book's style has it for a primer; the sentence answers the question, and a reader is not left
  guessing which project is meant.
- WK2 holds. Classes now says "Run every exercise in `Playground`, the script of Programming from zero I", linked, and the
  other three link the same section. I followed it: the section says to work in the project that Your first script
  left or to download its last checkpoint (stage-4.zip, opened with `project.open`). Its commands, run as written
  (`entity.create`, `script.create` with `open: true`, `script.build`, `script.add`), made the Playground script and built
  it (7.8 s, 3 classes). `open: true` answers `openedWith: the default application`; nothing visible in a headless run.
- WK3 holds. Memory 5 (Marker): build, play 100 frames, Console: frames 58, 59, 60 `Marker`, then the warning
  `GetEntityName (called by script 'Playground' on entity 'Playground'): entity ... does not exist` and `frame 61, marker: `
  (empty), the same again for 62; the fixed script logs `Marker` in 58 to 60 and `gone` in 61 and 62. Classes 5:
  `Star: GetScript<Pickup> is null: true`, `star collected`, `Boost: GetScript<Pickup> is null: true`,
  `speed boost collected`. Generic 5 and modern 5 on Checkpoint 4 of Ship the finished game (project-coin-run stage-4.zip,
  opened with `project.open`): the page's facts hold (tag `Coin`, coins appear once play starts, the ball is `Ball`,
  `a.GetTransform().GetWorldPosition()` compiles). Generic: a script on the ball sorts `FindEntitiesByTag("Coin")` by
  distance with `std::sort` and a lambda, logs `5 coins left, nearest at 3.58` down to `1 coins left`, then the stored
  `std::function` logs `all coins taken` (a stand-in in the script destroyed the nearest coin every 20 frames for the
  ball's collecting). Modern: `std::optional<Entity>` nearest, `enum class GameState : uint8_t`, `constexpr size_t`,
  a `switch`: `nearest of 5 (of 5): Coin` ... `you win`. Writing it I met a mistake of mine, not the book's: `Destroy()` is
  not const, so the optional must not be `const`.
- WK4 holds: "The address is 512. The pointer moves three elements of four bytes each: 500 + 3 × 4 = 512." Build's test-out
  answers read "Four. The build system compiles again each file ..." (1) and "A Release build prints 0: it defines NDEBUG ..." (5).
- WK5 holds: the fifth line reads "predict what a macro with arguments, an #if block and a type trait decide before the
  program runs".
- WK6 holds. In the x64 developer environment `dumpbin /symbols main.obj | findstr MakeGreeting` prints
  `UNDEF notype () External | ?MakeGreeting@@... (class std::basic_string<...> __cdecl MakeGreeting(...))`; for
  `Greeting.obj` `SECT5 ... External | ...` plus `SECT6`/`SECTBD`... lines marked `Static`. Every word the paragraph names is
  there (UNDEF, SECT5, machine name then readable name in round brackets, External, Static).
- WK7 holds: with the `;` deleted, `cl /EHsc /c main.cpp` prints `main.cpp(8): error C2143: syntax error: missing ';'
  before 'return'`, as the page quotes and explains. The link error: `LNK2019 ... referenced in function main`, `LNK1120: 1
  unresolved externals`.
- WK8 holds. I cannot open the Start menu: I used `cmd` with `vcvars64.bat` of Visual Studio 2026, which is what the
  shortcut of x64 Native Tools Command Prompt runs ("Environment initialized for: 'x64'"); the `vswhere.exe is not
  recognized` line appears and does not stop it. `cl` prints "... Version 19.50.35724 for x64". In an ordinary terminal `cl` is not
  recognized. `where cmake` here lists MSYS2's CMake first and the Visual Studio one second (the environment appends its
  folders), so the page's check fails on this machine: the default generator is Ninja (`-- Building for: Ninja`). The
  page's remedy, `-G "Visual Studio 18 2026"`, works (MSBuild, `build\Debug\stop.exe`). A reader without another CMake
  does not meet this.
- WK9 holds. In the Command Prompt: Debug 5 prints `coins: 5` (exit 0); Debug -5 prints `Assertion failed: coins >= 0 &&
  "coins cannot be negative", file ...stop.cpp, line 10` (exit 3); Release 5 prints `coins: 5`; Release -5 prints
  `coins: -5` (exit 0). I did not repeat the PowerShell 5.1 pipe: the page's warning about it is the earlier walker's run.
- WK10 holds. Building 18 variants at once after each save (`script.build`, the same call as Ctrl+B), 4 of them
  (`c2`, `c4`, `o1`, `o4`) ended `Script build N finished in 0.6 s (the module was up to date)` with `moduleChanged: false`
  and the Console showed the previous script's lines, as the Practice intro says. Saving again (3 s later) and building
  again compiled it (`moduleChanged: true`) and the Console showed the written script's lines in all four, and in
  the others the first build was right: memory 1 to 4, classes 1 to 4, generic 1 to 4 and modern 1 to 4 equal the worked
  solutions, `m2bad` gives C2280 and `g1bad` C2672. Mind: the first build after `script.create` plus an immediate
  overwrite of the file also built nothing (memory 5), so the intro's advice is needed there too.

Notes (not fixes):
- Memory 5's answer says "Frame 61 brought the warning"; the run printed the warning in frame 61 and again in frame 62
  (each empty name has its own). Say "Frames 61 and 62 each brought the warning" if it is touched again.
- On this machine the first line of `where cmake` was MSYS2's CMake in the developer prompt; the page's sentence covers it,
  and the first `cmake -S . -B build` of the page then uses Ninja, whose steps and file names (`greeting.lib`, no
  `--config`) differ a little from the page's Windows lines.
- The preview server stages `dist` once at its start: after a rebuild the files must be copied to `stage/` or the server
  restarted (the stage here was copied in place).
