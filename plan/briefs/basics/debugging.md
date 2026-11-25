# Brief: `basics/debugging`

| Field | Value |
| --- | --- |
| Title | Finding bugs: a method, the log and the debugger |
| Kind | P |
| Size | L |
| Tracks | G, B, E |
| Needs | `basics/programming-3` |
| From | new (curricula 1.18); a method for finding bugs, the log, breakpoints, stepping, the call stack; a process as a running program (one paragraph, since tracks G and B have not read `basics/computer`'s); a debugger attached to the editor's process, with the setup per OS (Manual/Scripting "Debugging with a debugger": Visual Studio's Attach to Process, VS Code's "Attach" entry; the writer checks what each OS asks before an attach, such as Linux's ptrace setting); use home of attaching a debugger to the editor; debugging the engine itself is `core/debugging`'s; Coin Run checkpoint: a planted bug in the coins' spin, found with breakpoints |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/debugging` — Finding bugs: a method, the log and the debugger

**Covers.** A method for finding bugs: make the bug happen again, look at what really happens, guess one cause, test the
guess with one change, fix it, check, and keep the check. The log as a tool: `Log::Info`, `Warn` and `Error` with the
values that matter, the Console's levels and filter, its file and line that open the code, and why logging every frame
floods the log. A process in one paragraph (track G has not read `basics/computer`): a running program, the editor's
among them. A debugger: a program that stops another one and shows its variables. Debug information: what lets the
debugger name files, lines and variables; the script module's PDB stays in `.strata/Scripts/Bin` while the editor runs a
private copy of the module, so breakpoints bind; optimized code steps in odd jumps. Attaching a debugger to the editor's
process, per OS in tabs: Visual Studio's **Debug ▸ Attach to Process...** and `StrataEditor.exe`, VS Code's "Attach"
entry with the C++ debugger, and what Linux and macOS ask before an attach (Linux's ptrace setting, macOS's prompt),
which the writer checks on each OS; adding `.strata/Scripts/Bin` to the symbol path when the symbols are not found. The
Linux and macOS tabs say what the pin does: only MSVC gives a script module debug information in every configuration;
with GCC and Clang the editor builds scripts in its own configuration, whose Release and Dist flags hold none, so with a
Release or Dist editor a breakpoint in a script may not bind there (one sentence says that this was read in the build
files, not run). Breakpoints and conditions; pausing in the debugger pauses the whole editor. Stepping over, into and
out; watching variables and changing one. The call stack: which function called which, each call's stack frame, and a
stack trace in a crash report (the editor's crash toast is `make/first-script`'s). Debugging the engine itself is
`core/debugging`'s. The Practice runs on the playground's script with the debugger attached, from easy to hard: a
breakpoint and a watch; a conditional breakpoint; stepping in and out with the call stack; a bug found by the method
alone; it ends with the Coin Run item: a planted bug in the coins' spin (the speed turned into radians twice, so the
coins crawl), found with a breakpoint on the turn's line and a watch on the angle.

**Leaves out.**

- Debugging a Coin Run script while it plays, and pausing and stepping the game → `make/play-test-debug`
- Debugging the engine, its asserts and its crash reports → `core/debugging`
- How the editor finds a crash's file and line → `scripting/symbolization`
- Crash containment inside → `scripting/crash-containment`
- How a build makes debug information → `basics/build`
- The stack and the heap as regions of memory → `basics/computer`

**Fit.** `fits`: about 5,100 words against L (5,000). The method, the log, debug information, attaching on three
operating systems with their steps and pictures, breakpoints, stepping and the call stack (about 3,750), and the common
mistakes, the Practice's four exercises, the Coin Run item and the fixed parts (about 1,350); attaching per OS takes the
most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:74` | concept | home | A bug, and a method to find it: reproduce, observe, guess, test one change, fix, check. General knowledge. |
| `new:75` | concept | home | The log as a tool: the four levels of `Log`, values in the message, the Console's filter, not logging every frame. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:62-73` |
| `new:76` | concept | home | A process in one paragraph, and what a debugger is. General knowledge. |
| `new:77` | concept | home | Debug information: the module's PDB in `.strata/Scripts/Bin`, the private copy that still names it, optimized code. Evidence: `Docs/Manual/Scripting.md:202-206`, `StrataScriptCore/CMake/StrataScriptModule.cmake:110-122` |
| `new:78` | concept | home | Breakpoints and conditions; pausing in the debugger pauses the whole editor. Evidence: `Docs/Manual/Scripting.md:206` |
| `new:79` | concept | home | Stepping over, into and out; watching and changing variables. General knowledge. |
| `new:80` | concept | home | The call stack, stack frames, and a stack trace. General knowledge. |
| `new:81` | hands-on | home | Coin Run practice: the spin's angle turned into radians twice, found with a breakpoint on the turn's line. Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:246-250` |
| `new:215` | hands-on | home | Practice before the Coin Run item, on the playground's script with a debugger attached to the editor, from easy to hard: Basic: a breakpoint in `OnUpdate` and its `deltaTime` read in a watch; Medium: a conditional breakpoint that stops only when a counter reaches 100; Medium: stepping into a function of one's own and out again, the call stack read at each stop; Hard: a bug the page gives (a counter set back to zero in the wrong callback) found with the method alone, each guess written down before its test. Evidence: `Docs/Manual/Scripting.md:200-206`, `StrataScriptCore/Include/StrataScript/Script.h:83-84` |
| `new:210` | open | home | Check: Script breakpoints on Linux and macOS. The claim: with a Release or Dist editor built with GCC or Clang, a breakpoint in a script module does not bind, because the module carries no debug information; the page states it as read in the build files, not run, and does not block the brief (R39). Evidence: `StrataScriptCore/CMake/StrataScriptModule.cmake:110-133` (debug information only in the MSVC branch), `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:37-52` (Dist takes Release's flags), `StrataEditor/src/Editor/ScriptBuild.cpp:402`, `StrataEditor/src/Editor/ScriptBuild.cpp:436` and `StrataEditor/CMakeLists.txt:36` (scripts built in the editor's configuration) |
| `new:211` | not-done | home | No debug information in script modules that a Release or Dist editor builds with GCC or Clang: only MSVC builds get it in every configuration, and the editor builds scripts in its own configuration, whose Release and Dist flags hold no `-g`; asked for v0.8.1 (`book.md`, "What Strata does not do"). Evidence: `StrataScriptCore/CMake/StrataScriptModule.cmake:110-133`, `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:37-52`, `StrataEditor/src/Editor/ScriptBuild.cpp:402`; `git grep -n -- '-g"' 822a7a46 -- StrataScriptCore 'StrataEditor/src/Editor/Script*'` finds nothing |
| `gamedev:135` | feature | home | Attaching a debugger to `StrataEditor`, with the PDB in `.strata/Scripts/Bin`; the use home of attaching, which `make/play-test-debug` applies |
| `scripting:157` | feature | use | The private copy of the module that the editor runs, in one sentence |
| `scripting:384` | code | use | `StrataScriptModule.cmake`'s PDB in every configuration, named as the reason breakpoints bind on Windows |
| `scripting:124` | feature | use | `Log`'s levels |
| `gamedev:54` | feature | use | The Console's file and line that open the code |
| `gamedev:133` | feature | link | Crash containment as the maker sees it, linked to `make/first-script` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Classes, functions and reading compile errors | `basics/programming-3` | must |
| A code editor installed | `start/install` | must |
| A process and the stack | `basics/computer` | helps |
| A script crash as the editor reports it | `make/first-script` | helps |

**Starting state.** The end state of `make/first-script`, from which the Coin Run item of the Practice starts: Coin
Run lit for play, its five coin instances spinning by the reader's `Coin` script; on track E it is downloaded. The
page gives the line that plants the bug. The other exercises run in the playground, as on `basics/programming-1`.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `attaching-a-debugger` | attaching a debugger | attach to process |
| `breakpoint` | breakpoint | - |
| `bug` | bug | - |
| `call-stack` | call stack | - |
| `crash` | crash | - |
| `debug-information` | debug information | debug symbols |
| `debugger` | debugger | - |
| `debugging` | debugging | - |
| `stack-frame` | stack frame | - |
| `stack-trace` | stack trace | backtrace |
| `stepping-through-code` | stepping through code | step over, step into, step out |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-1 | must | missing-item | `new:59` on `basics/programming-2`; the playground of `basics/programming-1` to `basics/debugging` on tracks G and B | On tracks G and B the playground is the reader's `Coin` script, which runs on all five instances of the coin prefab. Every line a practice logs in `OnCreate` appears five times. Worse, the Coin Run item of `basics/programming-2` puts a loop that instantiates the coin prefab into that script: every coin it makes carries the same script, runs `OnCreate` and makes coins again, so their number grows every frame until the editor stalls. style.md defines the playground as a project whose one script moves one entity. | On tracks G and B the playground is a script of its own (`Playground`, made with **Scripts ▸ New Script...**) on one new empty entity of Coin Run, as style.md §8 asks; the Starting state of the five pages says so (about 40 words on `basics/programming-1`). `new:59` puts `PlaceCoin` and its loop in a new script `CoinLine` on its own empty entity, with one sentence on why it never goes into `Coin` (about 80 words). | `allocation/basics-a.md:158-160`, `:229-230`, `:248-253`, `:284`, `:300-306`; `allocation/make-a.md:829-830`; `style.md:616-617`; `StrataScriptCore/Include/StrataScript/Scene.h:152-156` |
| critic-basics-a-9 | should | shape | `basics/debugging` (`new:210`, `new:215`, `new:81`) | The Linux and macOS tabs say that a breakpoint "may not bind" with a Release or Dist editor. The downloaded Strata is built in Dist and the editor builds scripts in its own configuration, so on Linux and macOS no reader of the release gets a breakpoint that binds in a script (as read). Three of the four practice items and the Coin Run item need one: on two of the three systems the page's main skill has nothing to practise on. | The tabs say plainly what the pin does for the downloaded Strata (read, not run). The Practice marks the items that need a binding breakpoint and gives Linux and macOS readers a path: the method-and-log item, and the planted bug found with `Log` lines (about 150 words). The check "Script breakpoints on Linux and macOS" also tries whether a `-g` added to the module in `Scripts/CMakeLists.txt` makes breakpoints bind; if it does, the tabs teach that line. | `allocation/basics-a.md:397-400`, `:433-436`; `.github/workflows/release.yml:149`, `:182`; `StrataEditor/CMakeLists.txt:39`; `StrataScriptCore/CMake/StrataScriptModule.cmake:110-133`; `StrataEditor/src/Editor/ScriptProject.cpp:211-221` |
| critic-basics-a-10 | should | missing-item | `basics/debugging` | The VS Code path is "VS Code's 'Attach' entry with the C++ debugger", but nothing makes that entry. The editor writes no `.vscode/launch.json`; VS Code needs Microsoft's C/C++ extension for it; on Linux the extension needs `gdb`, which `start/install`'s package line does not install. A B0 reader on VS Code, the only code editor `start/install` gives Linux and macOS, cannot attach, and JSON is taught only on `basics/data-formats`. | The VS Code tab gives the steps: install the C/C++ extension, `sudo apt install gdb` on Linux, and paste a complete `.vscode/launch.json` with one attach configuration into the `Scripts` folder (a folder whose name starts with a dot, which the module neither compiles nor watches), with one sentence that it is a JSON file shown whole (about 150 words). | `allocation/basics-a.md:394-396`; `Docs/Manual/Scripting.md:202-203`; a search of `StrataEditor/src`, `Docs/Manual` and `.claude/skills` at the pin for "launch.json" and ".vscode" finds nothing; `allocation/start.md:157-160`; `StrataScriptCore/CMake/StrataScriptModule.cmake:2-5` |
| critic-basics-a-11 | should | stale-item | `basics/debugging` (`new:75`, `gamedev:54`); `basics/programming-1` (`scripting:124`) | The log as a tool leans on "the Console's ... file and line that open the code". A script's own `Log` line carries no file and line: the SDK passes only the level and the text, and the Console opens only messages in a compiler's or a crash report's form. Two facts the method needs are missing: `Log::Trace` lines stay hidden until the Console's Trace box is ticked, and the Console keeps the last 4,096 lines, so a line logged every frame pushes the earlier ones out in about a minute (the log file keeps them). | Say that a log line names its place in its own text (the class and the callback), that build errors and crash reports are the lines that open the code, that Trace is off by default, and that the Console holds 4,096 lines while the file holds all (about 100 words); `basics/programming-1` says in one sentence that Trace lines need the box ticked. | `allocation/basics-a.md:165-166`, `:388-390`, `:427`, `:441`; `StrataScriptCore/Include/StrataScript/Log.h:74-83`; `StrataEditor/src/Panels/ConsolePanel.cpp:28`, `:66-70`, `:139-146`; `StrataEditor/src/Panels/ConsolePanel.h:45`; `StrataEditor/src/Editor/ScriptBuild.h:132-135`; `Strata/src/Strata/Core/Log.h:73`; `Strata/src/Strata/Core/Log.cpp:65-69` |
| critic-basics-a-28 | could | duplicate | `basics/debugging` (`new:76`) | `new:76` is a second home of "a process", which `new:12` homes on `basics/computer` with its glossary term (`automation:714`). By the rule for a page whose Needs closure lacks the home, `basics/debugging` explains the word in a paragraph and links the home. | Split `new:76`: "what a debugger is" stays `home`; "a process in one paragraph" becomes a `use` row of `new:12` with the link. No words change. | `allocation/basics-a.md:63`, `:67`, `:390`, `:428`; `allocation/README.md:243-246` |
