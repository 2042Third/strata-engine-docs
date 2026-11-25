# Allocation: basics-a

## `basics/computer` — How a computer runs a program: CPU, memory, caches and processes

**Covers.** The page is read on track B right after `make/lighting`, before any programming, so it teaches with
pictures, numbers and the editor, never with code. In order: a program is a list of machine instructions kept in a
file, and running it means that the processor does them one after another, billions of times a second (machine
instruction, machine code, processor, clock rate). Memory is a long row of numbered bytes; a memory address finds one
byte the way a house number finds a house; storage keeps data while the computer is off, memory only while it runs.
A processor holds several cores, and a core can run two lines of instructions at once (hardware threads, which the
operating system shows as "logical processors"); one paragraph says that some processors mix two kinds of cores and
links `core/platform`. Memory is far slower than the processor, so the processor keeps copies of recent data in small
caches, in levels, and copies memory in cache lines of 64 bytes; a figure with a table of rough waiting times (a
register, each cache level, memory) shows why reading data in the order it lies in memory is fast and jumping around
is slow (caches and why the order of data in memory matters). Code is data in memory too, read through its own cache,
so where code lands can change a measurement a little (the place of code in memory, for `engineering/perf-lab`).
Processors speak an instruction set (x64, ARM) with extensions such as SSE 4.2 and AVX2; a program built for newer
instructions does not start on an older processor; SIMD in one section: one instruction that adds four or eight
numbers at once. One paragraph names the GPU as a second processor with its own memory, made for drawing, which works
at the same time as the CPU (its frame is `gpu/how-a-gpu-frame-works`'). Then the operating system: it starts
programs, gives each one its own memory and shares the cores between them. A process is a running program, with its
own memory, a process id, an environment of named texts that it passes to the processes it starts (child processes),
and an exit code when it ends (exit codes and setting environment variables are `basics/tools`'). The editor is the
example: building the scripts with **Ctrl+B** starts CMake as a child process, which starts the compiler, and the
editor's log shows the command line it ran. Last, a process's memory has regions: its code, its fixed data, the stack
for the short-lived data of the steps in progress (a pile of plates: the last put on is the first taken off) and the
heap for data of any size kept as long as it is needed. The exercises are editor and system tasks: find the editor's
process, its id, memory and threads in the Task Manager (Activity Monitor, System Monitor), press **Ctrl+B** and watch
CMake and the compiler appear under it, watch the logical processors' graphs while a scene plays.

**Leaves out.**

- Threads that a program starts, races and locks → `basics/threads`
- Strata's job system and its pools → `core/jobs`
- The stack and the heap in code, allocators → `basics/cpp-memory`
- The call stack and stack frames as a debugger shows them → `basics/debugging`
- Arrays of structs against structs of arrays, sparse sets → `basics/data-structures`
- Exit codes, the standard streams and setting environment variables → `basics/tools`
- Binary numbers, and what a byte can hold → `basics/numbers`
- How source code becomes machine code → `basics/build`
- What the GPU does with a frame → `gpu/how-a-gpu-frame-works`
- Priorities and the two kinds of cores in Strata → `core/platform`

**Fit.** `fits`: about 5,100 words against L (5,000). Twelve ideas from zero at B0's length with the cache figure and
its table (about 4,150), the three exercises in the editor and the system's tools (about 350) and the fixed parts
(about 600), no code; caches and the order of data, processes and the regions of memory take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | concept | home | A program as a list of machine instructions kept in a file; machine code. General knowledge. |
| `new:2` | concept | home | The processor runs instructions one after another, billions a second; the clock rate. General knowledge. |
| `new:3` | concept | home | Memory as numbered bytes, a memory address, and storage that keeps data while the computer is off. General knowledge. |
| `new:4` | concept | home | Processor cores and hardware threads (logical processors); processors with two kinds of cores named. General knowledge. |
| `new:5` | concept | home | Memory is slow next to the processor: CPU caches in levels, cache lines of 64 bytes, rough waiting times. General knowledge. |
| `new:6` | concept | home | Caches and why the order of data in memory matters: reading in order against jumping around, with a figure. General knowledge. |
| `new:7` | concept | home | Code lives in memory too and is read through its own cache, so the place of code can change a measurement. General knowledge. |
| `new:8` | concept | home | Instruction sets (x64, ARM) and their extensions (SSE 4.2, AVX2); a program built for newer instructions on an older processor. General knowledge. |
| `new:9` | concept | home | SIMD: one instruction on four or eight numbers at once. General knowledge. |
| `new:10` | concept | home | The GPU as a second processor with its own memory, working at the same time as the CPU, in one paragraph. General knowledge. |
| `new:11` | concept | home | The operating system starts programs, gives each its own memory and shares the cores between them. General knowledge. |
| `new:12` | concept | home | A process: its own memory, a process id, an environment it passes to its child processes, an exit code at its end. General knowledge. |
| `new:13` | concept | home | The editor's script build as the example of a child process: **Ctrl+B** runs `cmake --build <folder> --parallel`, which runs the compilers, and the log line `[Scripts] > cmake ...` shows the command. Evidence: `StrataEditor/src/Editor/ScriptBuild.cpp:451-460`, `StrataEditor/src/Editor/ScriptBuild.cpp:1125-1153` |
| `new:14` | concept | home | The regions of a process's memory: code, fixed data, the stack (a pile of plates) and the heap. General knowledge. |
| `new:15` | hands-on | home | Exercises in the system's process viewer: the editor's process, id, memory and threads; CMake and the compiler under it during a build; the logical processors' graphs while a scene plays. Evidence: `StrataEditor/src/Editor/ScriptBuild.cpp:1125-1153` |
| `automation:714` | term | home | Process: a running program with its own memory, named by a process id |
| `foundation:208` | concept | use | What a program is, its process and an executable, the general half; Strata's programs are `core/map`'s |
| `scripting:147` | feature | use | The editor's build pipeline, named only as the program that starts CMake |
| `foundation:128` | feature | link | Strata's `Process`, which starts the script builds' child processes, linked to `core/platform` |
| `foundation:300` | concept | link | Scheduling, priorities and two kinds of cores, linked to `core/platform` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building the scripts with **Ctrl+B**, pressing **Play**, and the Console | `start/first-game` | must |
| One frame, and the CPU preparing a frame while the GPU draws the one before | `start/what-an-engine-is` | helps |

## `basics/tools` — The tools: the terminal, files and a code editor

**Covers.** The page assumes nothing of `basics/computer`, because track G takes it as a side step before
`make/first-script`, and its first line says that `make/first-script` needs only the sections on the terminal and the
code editor. The terminal: a terminal and the shell inside it (PowerShell, bash, zsh), a command line as a program's
name followed by words. Folders and paths written as text: absolute and relative paths, `~`, `.` and `..`, the
separators `\` and `/`, file extensions and hidden files and folders (the project's `.strata/`). The current folder:
`cd`, listing a folder, running a program of the current folder (`./`, `.\`). Arguments and options: `--version`,
`--help`, an option with a value, a path with spaces in quotes; a command line with options as the reference pages
print them. The standard streams: standard input, output and error; sending output to a file (`>`, `2>`), and a pipe
`|` that joins two programs. Exit codes: 0 when a program worked, another number when it did not, read with `$?` or
`$LASTEXITCODE`; Strata's codes are named with a link to `core/first-frame`. PowerShell waits for a windowed program
only when its output is piped: `.\StrataEditor --version | Write-Output` (the reason is `core/platform`'s).
Environment variables: named texts that each process carries and passes to the processes it starts, read and set for
one command in PowerShell and in a POSIX shell, `PATH` and how a shell finds a program; the example is
`STRATA_EXTERNAL_EDITOR`. The user data folder (`%LOCALAPPDATA%`, `~/.local/share`, `~/Library/Application Support`)
with the editor's log in it. Permissions as a user meets them: read-only files, files only you may change, the
executable bit (`chmod +x`), administrator rights and `sudo`. Files of commands: a shell script (`.sh` for bash, `.ps1`
for PowerShell) that stops at the first command that fails, and running a Python tool from a terminal
(`python Tools/<tool>.py --help`). A code editor: open a folder, IntelliSense, search across files, the terminal
inside the editor (VS Code or Visual Studio, as `start/install` installed them). Every command is shown in PowerShell
and in a POSIX shell, in OS tabs where they differ. The Test out box asks the reader to work out a relative path from
a current folder, to predict where `>` and `|` send a program's output, and to read an exit code. The Practice runs in
a terminal on a project folder and changes nothing in it: list the folder with its hidden files and find `.strata/`,
print the editor's version (with `| Write-Output` in PowerShell) and read its exit code, find the editor's log in the
user data folder and print its last lines, and search the folder's files in the code editor.

**Leaves out.**

- Opening a terminal for the first time on each OS → `start/install`
- What a process is inside the computer → `basics/computer`
- Strata's exit codes and how an interrupt sets 130 → `core/first-frame`, `core/platform`
- Why PowerShell does not wait for a windowed program → `core/platform`
- Version control: repositories, commits, branches, submodules and worktrees → `basics/git`
- Building C++ with CMake from a terminal → `basics/build`
- Building Strata from source → `core/first-change`, `engineering/building`

**Fit.** `over`: about 4,350 words against M (3,000). The twelve ideas of the terminal and the code editor with their
OS tabs take about 3,250 words at B0's length, and the primer's fixed parts with the Test out box and the Practice
about 1,100. The next size is L (5,000), which a primer may take (S2), and the page stays the one lesson that track G's
side step and `make/first-script` need.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:16` | concept | home | A terminal, the shell inside it (PowerShell, bash, zsh), and a command line as a program's name and words. General knowledge. |
| `new:17` | concept | home | Paths as text: absolute and relative, `~`, `.` and `..`, the two separators, file extensions, hidden files and folders. General knowledge. |
| `new:18` | concept | home | The current folder, `cd`, listing a folder, running a program of the current folder (`./`, `.\`). General knowledge. |
| `new:19` | concept | home | Arguments and options, an option with a value, quoting a path with spaces; the editor's `--version`, `--help` and `--headless` as examples. Evidence: `Docs/Releases/PackageReadme.md:77-81` |
| `new:20` | concept | home | The standard streams, sending output to a file (`>`, `2>`), and pipes between programs. General knowledge. |
| `new:21` | concept | home | Exit codes: 0 for success, other numbers for failure, read with `$?` and `$LASTEXITCODE`. General knowledge. |
| `new:22` | concept | home | PowerShell waits for a windowed program only when its output is piped: `.\StrataEditor --version \| Write-Output`. Evidence: `Docs/Releases/PackageReadme.md:80-81` |
| `new:23` | concept | home | Environment variables: inherited by child processes, read and set for one command, `PATH`; `STRATA_EXTERNAL_EDITOR` as the example. Evidence: `StrataEditor/src/Editor/ExternalEditor.cpp:25` |
| `new:24` | concept | home | The user data folder on each OS, with the editor's log `Strata/Logs/StrataEditor.log` in it. Evidence: `Docs/Releases/PackageReadme.md:75-77` |
| `new:25` | concept | home | Permissions as a user meets them: read-only files, files only you may change, the executable bit, administrator rights and `sudo`. General knowledge. |
| `new:26` | concept | home | Shell scripts (`.sh`, `.ps1`) that stop at the first failing command; running a Python tool from a terminal. General knowledge. |
| `new:27` | concept | home | A code editor: open a folder, IntelliSense, search across files, its own terminal. General knowledge. |
| `new:205` | hands-on | home | Practice in a terminal on a project folder, changing nothing: its hidden `.strata/` folder listed, the editor's `--version` printed (piped in PowerShell) and its exit code read, the editor's log found in the user data folder and its last lines printed, the folder searched in the code editor. Evidence: `Strata/src/Strata/Project/Project.h:109`, `Docs/Releases/PackageReadme.md:75-81` |
| `automation:768` | term | home | stdin, stdout, stderr: a process's standard streams |
| `foundation:626` | term | home | Exit code, in general; Strata's 0, 1, 3 and 130 are named with a link |
| `foundation:51` | feature | link | Strata's exit codes, linked to `core/first-frame` |
| `foundation:313` | concept | link | Why PowerShell does not wait for a windowed program, linked to `core/platform` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Opening a terminal, changing folder and running a program, per OS | `start/install` | helps |
| A process and its environment | `basics/computer` | helps |
| A code editor installed | `start/install` | must |

**Starting state.** No checkpoint: the Practice reads a project folder the reader already has and changes nothing in
it (on tracks B and G Coin Run's project as `make/lighting` leaves it, on track E the Basic 3D project of
`start/first-game`).

## `basics/programming-1` — Programming from zero I: values, variables, expressions and decisions

**Covers.** The reader has never programmed. The playground is a Strata script: on tracks G and B the reader's own
`Coin` script from `make/first-script`, on track E the `Spinner` of `start/first-game`; output goes to the log (the
Console) and to the coin that turns. Each section links its learncpp lesson. In order: a program as steps that run in
order, source code, and the script as the frame the page fills in: `OnCreate` runs once, `OnUpdate` every frame, and
the class around them is read as a frame here and taught on `basics/programming-3` (a script at the use level: a class
and calls into the SDK). Statements end with `;`, braces group them, `//` starts a comment. The first call into the
SDK: `Log::Info` takes its pieces separated by commas and joins them (it is not a format string), so
`Log::Info("Speed: ", speed)` prints both; `true` and `false` print as words, a `glm::vec3` as `(x, y, z)`; `Trace`,
`Warn` and `Error` are named as the class's other levels, and `reference/script-api` lists its declarations. Values and
types: `int`, `float` with the `f` of `90.0f`, `double`, `bool`, text in double quotes, and `int32_t` named as the
whole number that fields use (its size is `basics/numbers`'). Variables: declare with a type and a first value, assign,
names that say what they hold, `const`; a field is a variable that the editor shows. Expressions: arithmetic, the order
of operations, integer division and `%`, mixing `int` and `float`, `+=` and `++`. Comparisons give a `bool`; `&&`, `||`
and `!` join them. Decisions: `if`, `else if`, `else`, and blocks with their scope (a variable lives inside its braces).
Namespaces and `::`: `Strata::`, `glm::vec3`, `glm::radians`, `using namespace Strata;`, and `Key::Space`, a name inside
the namespace `Key`, used with `Input::IsKeyDown(Key::Space)` in an `if`. Scoped enumerations: `enum class` with
values written after the type's name and `::` (`CursorMode::Locked`, shown from `Input.h`), and `switch` with `case`,
`break` and `default`. Common mistakes: `=` in place of `==`, a missing `;`, integer division where a fraction was
meant, a variable used outside its braces. The Practice runs in the playground's script, from easy to hard: integer
and float division predicted, then run; a `const` speed changed; the lines of an `if` and its `else` put in order; a
`switch` whose missing `break` shows in the output; it ends with the Coin Run item: the spin speed in a variable, and
a `bool` field `IsGold` ticked on one coin in the Inspector with an `if` that spins that coin faster.

**Leaves out.**

- Loops, functions, lists, structs and text → `basics/programming-2`
- Classes, references, pointers, files of code and reading errors → `basics/programming-3`
- What is special to script code (`override`, `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD`) → `make/first-script`
- Binary, the sizes and ranges of integer types, floating-point precision → `basics/numbers`
- Vectors and the turn in the spin's line as mathematics → `basics/math-vectors`, `basics/math-rotations`
- Finding bugs with the log and a debugger → `basics/debugging`

**Fit.** `fits`: about 5,500 words against L (5,000). Ten ideas from zero, each run in the script with its output,
with the quotes of `Log.h` and `Input.h` (about 4,150), and the common mistakes, the Practice's four exercises, the
Coin Run item and the fixed parts (about 1,350); values and types, expressions and decisions take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:34` | concept | home | A program as steps in order, source code, and the script as the playground: `OnCreate` once, `OnUpdate` every frame. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:30-33` |
| `new:35` | concept | home | Statements and `;`, braces, comments. General knowledge. |
| `new:36` | code | home | `StrataScriptCore/Include/StrataScript/Log.h:58-73`: `Log` joins its arguments ("Arguments are concatenated") and has four levels |
| `new:37` | concept | home | Values and types: `int`, `float` and its `f`, `double`, `bool`, text in quotes; `int32_t` named. General knowledge. |
| `new:38` | concept | home | Variables: declare, give a first value, assign, name, `const`; a field as a variable the editor shows. General knowledge. |
| `new:39` | concept | home | Expressions and arithmetic operators, the order of operations, integer division and `%`, `+=` and `++`. General knowledge. |
| `new:40` | concept | home | Comparison operators, `bool`, and the logical operators `&&`, `\|\|` and `!`. General knowledge. |
| `new:41` | concept | home | `if`, `else if`, `else`; blocks and scope. General knowledge. |
| `new:42` | concept | home | Namespaces and `::`: `Strata::`, `glm::`, `using namespace`; `Key::Space` as a name in the namespace `Key`. Evidence: `StrataScriptCore/Include/StrataScript/Input.h:16-24` |
| `new:43` | concept | home | Scoped enumerations (`enum class`) and `switch` with `case`, `break` and `default`. General knowledge. |
| `new:44` | code | home | `StrataScriptCore/Include/StrataScript/Input.h:212-217`: `CursorMode`, a scoped enumeration of the SDK |
| `new:45` | erratum | home | The outline's row wrote "scoped enum values written as `Key::Space`" until R30 (D6) corrected it. At the pin `Key` is a namespace whose unnamed enum has the type `KeyCode` (`uint16_t`), so `Key::Space` is a name in a namespace; the SDK's scoped enumerations are `CursorMode`, `GamepadButton`, `WindowMode` and others. The page teaches both and never calls `Key::Space` a scoped enum value. Evidence: `StrataScriptCore/Include/StrataScript/Input.h:16-24`, `StrataScriptCore/Include/StrataScript/Input.h:212-217` |
| `new:46` | hands-on | home | Coin Run practice: the spin speed in a variable, a `bool` field `IsGold` and an `if` that spins the gold coin faster, from `make/first-script`'s checkpoint. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:854-856` |
| `new:212` | hands-on | home | Practice before the Coin Run item, run in the playground's script and read in the Console, from easy to hard: Basic, predict then run: what `Log::Info` prints for `7 / 2`, `7 % 2` and `7 / 2.0f`; Basic, modify: a `const float` speed doubled and the spin watched; Medium, a Parsons problem: the shuffled lines of an `if`, `else if` and `else` that log "slow", "fast" or "very fast" for a speed; Hard: a `switch` on a whole number with `case`, `break` and `default` that logs one word per value, and a missing `break` found from the output. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `gamedev:359` | code | use | The generated `Spinner`, read again line by line as values, a variable and an expression |
| `scripting:105` | feature | use | The `Script` base class, as the frame the page writes in |
| `scripting:124` | feature | home | `Log`, the first class of the SDK the reader calls: `Log::Info` writes to the Console, its arguments joined in order (no format string), `true` and `false` as words and a `glm::vec3` as `(x, y, z)`; `Trace`, `Warn` and `Error` are named as its other levels, which `basics/debugging` uses; its declarations are linked to `reference/script-api` |
| `scripting:122` | feature | use | `Input::IsKeyDown` in an `if` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Editing a script in the code editor, building with **Ctrl+B**, Play, and reading `Log::Info` in the Console | `start/first-game` | must |
| How to read code you do not understand yet | `start/how-to-read` | helps |
| Coin Run's `Coin` script and its `DegreesPerSecond` field | `make/first-script` | helps |
| A rotation as an axis and an angle, in degrees and radians | `make/transforms-units` | helps |
| Memory as numbered cells | `basics/computer` | helps |

**Starting state.** The end state of `make/first-script`, from which the Coin Run item of the Practice starts: Coin
Run lit for play, its five coin instances spinning by the reader's `Coin` script and its `DegreesPerSecond` field; on
track E it is downloaded. The other exercises run in the playground: on tracks G and B the reader's own `Coin` script,
on track E the `Spinner` of `start/first-game`'s project.

## `basics/programming-2` — Programming from zero II: loops, functions, lists and structs

**Covers.** The same playground. Loops: `while` with its condition checked before each turn, and why a loop that never
ends freezes the editor, which logs nothing (the call cannot be stopped; the engine has a watchdog that would log it,
but only tests turn it on, `scripting/crash-containment`; so the editor must be closed, and recovery is
`make/project-files`'); `for` that counts from 0 while `i < count`, and the range-based `for` over a list. Functions: a
name, parameters with types, a body and a return value; calling one with arguments; arguments copied into parameters;
local variables that start over at each call, unlike fields; `void`. Default arguments and functions that share a name
with other parameters, read on `Scene::Instantiate`'s four forms. Static member functions called through a type's name
and `::`, as `Input::IsActionDown("Jump")` and `Input::GetGamepadAxis(axis, 0)` with its default dead zone. Lists:
`std::array<float, 3>` with indexes from 0 and reading past the end as a mistake; `std::vector` with `push_back`, `size`
and a loop over it. Structs: values grouped under one name, members reached with `.`, and `glm::vec3` as the struct of
`x`, `y` and `z`. Text: `std::string`, joining with `+`, comparing with `==`, `std::to_string` (numbers turned into
text) and `std::stoi` (text turned into a number); `std::stoi` on text that is no number throws an exception, and the
editor then turns that script off on its entity (named here, explained by `scripting/crash-containment`). Common
mistakes: a loop off by one, a function that forgets to return, changing a parameter and expecting the caller's variable
to change. The Practice runs in the playground's script, from easy to hard: a `for` loop's output predicted, then run; a
function with a default argument; a `std::vector` summed; numbers turned into text and back; it ends with the Coin Run
item: a function `PlaceCoin` and a loop that line coins up, with the lines that request and instantiate the prefab
given. The coin prefab is asked for in `OnCreate` and the loop runs once it is loaded, because `Instantiate` never waits
for an asset and returns a null entity until it is loaded (the page says so in two sentences; asking early is
`make/scripting-scene`'s use home).

**Leaves out.**

- Classes, references, pointers and `std::optional` → `basics/programming-3`
- Asking for assets early and finding entities → `make/scripting-scene`
- Exceptions in C++ → `basics/cpp-modern`
- What an exception and a crash do to a script → `scripting/crash-containment`
- What lists cost, and other data structures → `basics/data-structures`, `basics/trees-graphs`
- The standard containers in depth → `basics/cpp-generic`

**Fit.** `fits`: about 5,400 words against L (5,000). Nine ideas from zero run in the script, with the quotes of
`Scene.h` and `Input.h` (about 3,950), and the common mistakes, the Practice's four exercises, the Coin Run item with
its given lines and the fixed parts (about 1,450); functions, loops and text take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:47` | concept | home | `while` loops; a loop that never ends freezes the editor, which logs nothing: the engine's watchdog is off unless a host sets a timeout, and only tests set one (`scripting/crash-containment`); close the editor, and recovery is `make/project-files`'. Evidence: `Strata/src/Strata/Scripting/ScriptEngine.cpp:35`, `Strata/src/Strata/Scripting/ScriptEngine.cpp:257-266`, `Strata/src/Strata/Scripting/ScriptWatchdog.h:16-18`, `Docs/Architecture.md:1415`; `git grep -n SetWatchdogTimeout 822a7a46` finds the call only in `StrataTests/src/Scripting/ScriptFaultTests.cpp` and `StrataTests/src/Scripting/ScriptModuleTests.cpp` |
| `new:48` | concept | home | `for` loops that count from 0, and the range-based `for` over a list. General knowledge. |
| `new:49` | concept | home | Functions: name, parameters, body, return value; calling with arguments; arguments copied. General knowledge. |
| `new:50` | concept | home | Local variables and their scope, against fields that keep their values. General knowledge. |
| `new:51` | concept | home | Default arguments, and functions that share a name with other parameters. General knowledge. |
| `new:52` | code | home | `StrataScriptCore/Include/StrataScript/Scene.h:177-186`: `Scene::Instantiate` by path, with default arguments |
| `new:53` | concept | home | Static member functions called through the type's name and `::`, with default arguments (`GetGamepadAxis`). Evidence: `StrataScriptCore/Include/StrataScript/Input.h:328` |
| `new:54` | code | home | `StrataScriptCore/Include/StrataScript/Input.h:380-388`: `Input::IsActionDown`, a static member function with its comment |
| `new:55` | concept | home | `std::array`, indexes from 0, reading past the end. General knowledge. |
| `new:56` | concept | home | `std::vector`: `push_back`, `size`, a loop over it. General knowledge. |
| `new:57` | concept | home | Structs and members; `glm::vec3` as a struct of three floats. General knowledge. |
| `new:58` | concept | home | `std::string`: joining, comparing, `std::to_string` and `std::stoi`, and the exception of `std::stoi`. General knowledge. |
| `new:59` | hands-on | home | Coin Run practice: `PlaceCoin` and a loop that line coins up; the lines that request and instantiate the prefab are given: `Assets::Find` and `Assets::RequestLoad` in `OnCreate`, a check of `Assets::IsLoaded`, then `Scene::Instantiate` with a `bool` so that the loop runs once, because `Instantiate` never waits. Evidence: `StrataScriptCore/Include/StrataScript/Scene.h:18-42`, `StrataScriptCore/Include/StrataScript/Scene.h:152-156` |
| `new:213` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: what a `for` loop logs from 0 while `i < 3`, and the extra turn that `<=` gives; Medium: a function `Clamp` with a default argument, called with and without it; Medium: the speeds of a `std::vector<float>` summed in a range-based `for` and logged; Hard, faded examples: a score turned into text with `std::to_string` and back with `std::stoi`, three times with less help each time, the last on text that is no number, predicted before the run. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `scripting:121` | feature | use | `Assets::Find`, `Assets::RequestLoad`, `Assets::IsLoaded` and `Scene::Instantiate`, the given lines of the practice |
| `scripting:122` | feature | use | `Input`'s static member functions |
| `scripting:176` | feature | use | The watchdog, named as on only in tests, so that in the editor an endless loop freezes it and logs nothing |
| `scripting:190` | feature | use | An exception switches off one instance, named for `std::stoi` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Values, variables, expressions, `if` and namespaces | `basics/programming-1` | must |
| The coin as a prefab | `make/prefabs` | helps |
| A position as three numbers (x, y, z) | `make/transforms-units` | helps |
| Recovery after the editor was closed | `make/project-files` | helps |

**Starting state.** The end state of `make/first-script`, from which the Coin Run item of the Practice starts: Coin Run
lit for play, its five instances of `Prefabs/Coin.stprefab` spinning by the reader's `Coin` script; on track E it is
downloaded. The practice gives the lines that request and instantiate the prefab (`book.md`'s running examples):
`Assets::Find("Prefabs/Coin.stprefab")` and `Assets::RequestLoad` in `OnCreate`, a check of `Assets::IsLoaded` in
`OnUpdate`, and `Scene::Instantiate` with a `bool` so that the loop runs once
(`StrataScriptCore/Include/StrataScript/Scene.h:18-42`, `:152-156`). The other exercises run in the playground, as on
`basics/programming-1`.

## `basics/programming-3` — Programming from zero III: classes, references, files of code and reading errors

**Covers.** The same playground, and the C++ of gamedev concept 11 as far as a script needs it (the rules that are
special to scripts stay `make/first-script`'s). Classes: values and the functions that work on them in one type,
`public:` and `private:`, member functions called with `.`; a script class is a class, and each entity gets its own
object of it with its own fields. Constructors and the first values written beside the members (why a script does its
setup in `OnCreate` is `make/first-script`'s). Inheritance at the level a script needs: `class Coin : public Script`,
the base class and the derived class, `override`, a derived class that calls its base's function
(`Coin::OnUpdate(deltaTime)`), and a derived script whose base's fields still show in the editor. References: `&` in a
type, a function that changes its caller's variable, `const &` that avoids a copy (as the SDK's `const glm::vec3&`).
Pointers at the use level: `T*`, `nullptr`, the check before use, and `->`, on what `GetScript<T>()` returns.
`std::optional` at the use level: `has_value`, `value_or` and `*`, on what `Entity::GetProperty` and
`Game::ReadSaveText` return. Template arguments in angle brackets: `GetProperty<float>`, `GetScript<Coin>`,
`std::vector<int>`. Files of code: a header (`.h`) declares, a source file (`.cpp`) defines, `#include` copies a header
in; a class in a header and its functions in a source file; every `.cpp` and `.h` of the `Scripts` folder belongs to
the module; calling a public member function of another class through its header. Reading a C++ declaration: return
type, name, parameters with types and defaults, `const` and `static`, and an enum's declaration, practised on lines of
the SDK's headers, so that `reference/script-api` can be read; the earlier pages' parts (scoped enum values from
`basics/programming-1`, numbers turned into text with `std::to_string` from `basics/programming-2`) are read again in
declarations. Reading compile errors: the first error first, its file and line, the common messages (a missing `;`, an
unknown name, a wrong type, a missing `#include`), the Problems panel, and warnings against errors. The Practice runs
in the playground's script, from easy to hard: a value and a reference parameter predicted, then run; a small class
in a header and a source file; a property and a script read through `std::optional` and a pointer; planted compile
errors fixed from the first message; it ends with the Coin Run item: a `Coin` class with a field, in `Coin.h` and
`Coin.cpp`, and a `BobbingCoin` derived from it that also bobs.

**Leaves out.**

- Virtual calls, interfaces and operators in depth → `basics/cpp-classes`
- Pointers, lifetimes, ownership and smart pointers in depth → `basics/cpp-memory`
- `std::optional` beyond the use level, and the rest of modern C++ → `basics/cpp-modern`
- Templates written by the reader → `basics/cpp-generic`
- Compiling and linking, and why a header is not compiled alone → `basics/build`
- `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD` and no work in the constructor → `make/first-script`
- The callbacks and when each runs → `make/script-loop`
- Finding a bug in running code → `basics/debugging`

**Fit.** `fits`: about 5,800 words against L (5,000). Ten ideas from zero with the two quotes of `Entity.h` and a set
of compiler messages (about 4,450), and the common mistakes, the Practice's four exercises, the Coin Run item and the
fixed parts (about 1,350); classes, files of code and reading compile errors take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:60` | concept | home | Classes: data and functions together, `public:` and `private:`, member functions. General knowledge. |
| `new:61` | concept | home | Constructors and first values written beside the members. General knowledge. |
| `new:62` | concept | home | Objects: the engine makes one object of a script class per entity, each with its own fields. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:30-31` |
| `new:63` | concept | home | Inheritance at the script's level: base and derived class, `override`, calling the base's function; a derived script registers its base's fields. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:779-786` |
| `new:64` | concept | home | References: `&` in a type, changing the caller's variable, `const &` to avoid a copy. General knowledge. |
| `new:65` | concept | home | Pointers at the use level: `*` in a type (`T*`), `nullptr`, the check before use, `->`. General knowledge. |
| `new:66` | code | home | `StrataScriptCore/Include/StrataScript/Entity.h:86-92`: `GetScript<T>` returns a `T*` |
| `new:67` | concept | home | `std::optional` at the use level: `has_value`, `value_or`, `*`. General knowledge. |
| `new:68` | code | home | `StrataScriptCore/Include/StrataScript/Entity.h:66-72`: `GetProperty<T>` returns a `std::optional<T>`, with the types its comment lists |
| `new:69` | concept | home | Template arguments in angle brackets. General knowledge. |
| `new:70` | concept | home | Files of code: header and source, `#include`, declaration and definition; every `.cpp` and `.h` of the `Scripts` folder is in the module. Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:213-215` |
| `new:71` | concept | home | Reading a C++ declaration: return type, name, parameters, defaults, `const`, `static`, an enum. General knowledge. |
| `new:72` | concept | home | Reading compile errors: the first one first, file and line, common messages, warnings against errors. General knowledge. |
| `new:73` | hands-on | home | Coin Run practice: a `Coin` class with a field in `Coin.h` and `Coin.cpp`, and `BobbingCoin` derived from it. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:779-786` |
| `new:214` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: a function that takes an `int` by value and one that takes it by `&`, and what the caller's variable holds after each; Medium: a class `Counter` with a `private` count, a constructor and two `public` member functions, declared in a header and defined in a source file; Medium: a component's property read with `GetProperty<float>` and `value_or`, and `GetScript<T>()` checked against `nullptr` before `->`; Hard: three planted compile errors (a missing `;`, an unknown name, a missing `#include`), each fixed from the first message in the Problems panel. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:66-72`, `StrataScriptCore/Include/StrataScript/Entity.h:86-92` |
| `gamedev:317` | concept | home | Scripts in C++: classes, inheritance for `override`, public members as fields, headers and sources, compile errors and the Problems panel; the rules special to scripts are `make/first-script`'s and building the module is `make/script-builds`' |
| `gamedev:372` | code | use | `Samples/Tetris/Scripts/TetrisGame.h:8-106`: a class in a header, read for its declarations |
| `scripting:118` | feature | use | `Entity`'s `GetScript` and `GetProperty` |
| `scripting:129` | feature | use | `Game::ReadSaveText` and its `std::optional` |
| `editor-ui:149` | feature | use | The Problems panel, where compile errors are read |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Loops, functions, structs, `std::vector` and `std::string` | `basics/programming-2` | must |
| The script class, `override` and the Problems panel as `make/first-script` shows them | `make/first-script` | helps |

**Starting state.** The end state of `make/first-script`, from which the Coin Run item of the Practice starts: Coin
Run lit for play, its five coin instances spinning by the reader's `Coin` script in `Coin.cpp`; on track E it is
downloaded. The other exercises run in the playground, as on `basics/programming-1`.

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

## `basics/git` — Version control with git

**Covers.** The page is read on track B after `make/project-coin-run` and on track E after `basics/debugging`, and it
needs only the terminal and the code editor of `basics/tools`. Version control, and git as the program that does it: a
repository and its history of commits; `git init` for a folder of one's own and `git clone` for someone else's
repository; submodules and `git submodule update --init --recursive --depth 1` as Strata's source needs it;
`git status`, `git diff`, staging with `git add` and `git commit` with a message; the `.gitignore` a new project gets
(`/.strata/`) and the one in its `Scripts` folder (`/CMakePresets.json`); branches, switching, merging and merge
conflicts; remotes, `git push`, `git pull` and tags; a patch as a diff saved to a file and applied with `git apply`;
searching with `git grep`, as the evidence of `appendix/not-in-strata` is written; a worktree as a second working folder
of one repository. Every command is shown in PowerShell and in a POSIX shell, in OS tabs where they differ. The Test out
box asks the reader to predict what `git status` shows after an edit and a `git add`, to read the markers of a merge
conflict, and to give the command that fetches Strata's submodules. The Practice runs git on a folder of the reader's
own and ends with the optional item on the reader's Coin Run: `git init` in the project's folder, `git status` with
`.strata/` kept out by the `.gitignore` the editor wrote, a first commit, the `Coin` script's `DegreesPerSecond` changed
and read with `git diff`, and a branch that changes it again and is merged back.

**Leaves out.**

- The terminal, paths and hidden folders → `basics/tools`
- Strata's branches, reviews and commits → `engineering/contributing`
- Building Strata from a clone → `core/first-change`, `engineering/building`
- How Strata pins its submodules and upgrades them → `engineering/third-party`
- What runs when a branch is pushed → `engineering/ci`

**Fit.** `fits`: about 3,700 words against M (3,000). Six ideas from zero at B0's length, with the three places of a
change (the folder, the staging area, the history) and a branch's merge drawn (about 2,600), and the primer's fixed
parts with the Test out box, the Practice and the Coin Run item (about 1,100); branches, merges and conflicts take the
most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:28` | concept | home | Version control: a repository, its commits, `git clone`, submodules and the command Strata's source needs. Evidence: `AGENTS.md:54` |
| `new:29` | concept | home | `git status`, `git diff`, staging, `git commit` with a message. General knowledge. |
| `new:30` | concept | home | `.gitignore`: a new project ignores `/.strata/`, and its `Scripts` folder ignores `/CMakePresets.json`. Evidence: `Strata/src/Strata/Project/Project.cpp:198-200`, `StrataEditor/src/Editor/ScriptBuild.cpp:613-614` |
| `new:31` | concept | home | Branches, switching, merging and merge conflicts. General knowledge. |
| `new:32` | concept | home | Remotes, `git push`, `git pull` and tags. General knowledge. |
| `new:33` | concept | home | A patch (`git diff` saved, `git apply`), searching with `git grep`, and worktrees. General knowledge. |
| `new:206` | hands-on | home | Optional practice on Coin Run: `git init` in the project's folder, `git status` with `.strata/` kept out by the `.gitignore` the editor wrote when it made the project, a first commit, `DegreesPerSecond` changed and read with `git diff`, a branch merged back. Evidence: `Strata/src/Strata/Project/Project.cpp:198-200` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A terminal: the current folder, relative paths, hidden folders, running a program with arguments | `basics/tools` | must |
| A code editor, for a commit message and a file with a merge conflict | `basics/tools` | must |
| Coin Run's `Coin` script and its `DegreesPerSecond` field | `make/first-script` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts: Coin Run's project folder with the `.gitignore` the editor wrote when it made the
project, and no repository yet.

## `basics/numbers` — Numbers in a computer: binary, integers, floating point and precision

**Covers.** The page starts track B's second visit to `basics` and uses the reader's Coin Run as its source of numbers.
Binary: place values worth twice the place to their right, counting in binary, a bit, a byte of eight bits; hexadecimal
with four bits per digit and the `0x` prefix (colors, addresses and hashes are written in it); other bases, and writing
a number's digits backwards behind the point in base 2 and base 3 (the radical inverse that `image/taa` uses). Integers
of fixed sizes: `int8_t` to `uint64_t`, `int32_t` and `uint32_t`, their ranges, 16-bit samples of sound; two's
complement for signed integers; integer overflow, which wraps for unsigned types and is not allowed for signed ones
(undefined behavior is `basics/cpp-memory`'s). Integer division that rounds down, the rule that rounds up
(`(a + b - 1) / b`), and `%`. Bits: the bitwise operators `&`, `|`, `^` and `~`, masks that keep, set, clear and test
bits, bit flags (a collision layer's mask in words); shifts `<<` and `>>` as multiplying and dividing by powers of two;
two numbers packed into one integer and taken out again (an index of 20 bits and a version of 12, as `world/ecs` shows);
counting trailing zeros (`std::countr_zero`); interleaving the bits of two numbers (Morton order). Floating point: a
sign, an exponent and a significand (IEEE 754), `float` of 32 bits and `double` of 64, and the bits of a float laid out
in a figure; the spacing between neighbouring floats grows with their size, so precision falls far from the origin (the
gap at 1 m, 1 km and 20 km in a table; a timer in a `float` after hours) and `double` is the cure where it matters.
Rounding: which operations are exact (small integers, halving and doubling), why `0.1 + 0.2` is not `0.3`, comparing
with a tolerance, and quantizing a float into fewer bits. Determinism: the same inputs give the same bits, and why two
results can still differ in the last bit (the order of additions; fused multiply-add in one sentence, which is
`engineering/flags-portability`'s); Strata's promise that results do not depend on the number of threads is `core/jobs`'
design decision. The values that are not numbers: infinities, NaN (which is not equal to itself and spreads through
every sum), overflow of floats to infinity, subnormals near zero, and half floats of 16 bits with their range and the
integers they hold exactly. Powers: powers of two, sizes in KiB, MiB and GiB against kB and MB, bandwidth in GB/s; a
geometric series (1 + 1/2 + 1/4 + ...) is named in one sentence with a link to `basics/math-interpolation`, which
teaches it and its sum. Logarithms: the exponent asked for backwards, base 2 (how many times a size halves: mip levels)
and base 10, the logarithm of a product; ratios on a logarithmic scale, EV stops (each a factor of two of light) and
decibels (10 dB is ten times the energy). The exponential function and the number e: growth or decay by the same factor
in each equal step, `exp(-k t)`, which `basics/math-interpolation` turns into smoothing. The Practice runs by hand and
in the playground's script, from easy to hard: numbers converted between binary, decimal and hexadecimal; an integer's
overflow predicted, then run; bits set, cleared and tested with masks; a float sum compared with and without a
tolerance; the gap between neighbouring floats measured; it ends with the optional Coin Run item: keep the HUD's timer
in a `float`, find after how long adding one frame's time no longer changes it, and keep it in a `double`.

**Leaves out.**

- Bytes in files, byte order and text → `basics/bytes`
- The sRGB curve and the half-float range for colors → `basics/color`
- Fused multiply-add and determinism across compilers → `engineering/flags-portability`
- Strata's deterministic parallel work → `core/jobs`
- Why a world must stream, and its 20 km limit → `worlds/why-streaming`
- Rendering relative to the camera → `draw/mirrors-camera-relative`
- Exponential smoothing and `1 - exp(-k dt)` → `basics/math-interpolation`
- A geometric series and its sum → `basics/math-interpolation`
- Exposure in EV stops in the editor → `make/lighting`
- Undefined behavior → `basics/cpp-memory`

**Fit.** `over`: about 7,050 words against L (5,000). Seventeen ideas from zero at B0's length with the figure of a
float's bits and the table of gaps (about 5,750), and the common mistakes, the Practice's five exercises, the Coin Run
item and the fixed parts (about 1,300). A primer is at most L, so the page splits (S3), in this order on tracks B and E:
`basics/numbers` "Numbers in a computer: binary, integers, bits and floating point" (L, about 5,800) and
`basics/math-powers` "Powers, logarithms and the exponential function" (S, about 2,100 with a practice of its own);
`book.md`'s one-home row for powers and logarithms would then name the second.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:82` | concept | home | Binary: place values, counting, a bit, a byte of eight bits. General knowledge. |
| `new:83` | concept | home | Hexadecimal: four bits per digit and the `0x` prefix. General knowledge. |
| `new:84` | concept | home | Other bases, and a number's digits written backwards behind the point (the radical inverse in base 2 and 3). General knowledge. |
| `new:85` | concept | home | Integer types of fixed sizes and their ranges; 16-bit samples. General knowledge. |
| `new:86` | concept | home | Two's complement, signed and unsigned, and integer overflow. General knowledge. |
| `new:87` | concept | home | Integer division that rounds down, the rule that rounds up, and `%`. General knowledge. |
| `new:88` | concept | home | Bitwise operators, masks and bit flags. General knowledge. |
| `new:89` | concept | home | Shifts, two numbers packed into one integer, counting trailing zeros, interleaved bits (Morton order). General knowledge. |
| `new:90` | concept | home | Floating point: sign, exponent and significand; `float` and `double`; the bits of a float. General knowledge. |
| `new:91` | concept | home | Spacing that grows with magnitude: precision far from the origin, a float timer after hours, `double`. General knowledge. |
| `new:92` | concept | home | Rounding: exact operations, `0.1 + 0.2`, tolerances, quantizing a float into fewer bits. General knowledge. |
| `new:93` | concept | home | Determinism as the same bits for the same inputs, and why two results differ in the last bit. General knowledge. |
| `new:94` | concept | home | Infinities, NaN, overflow of floats, subnormals, and half floats with their range and exact values. General knowledge. |
| `new:95` | concept | home | Powers and powers of two; KiB, MiB and GiB against kB and MB; bandwidth in GB/s. General knowledge. |
| `new:96` | concept | link | A geometric series, named beside the powers with a link to `basics/math-interpolation`, which teaches it and its sum. General knowledge. |
| `new:97` | concept | home | Logarithms: base 2 and base 10, the logarithm of a product. General knowledge. |
| `new:98` | concept | home | Ratios on a logarithmic scale: EV stops and decibels. General knowledge. |
| `new:99` | concept | home | The exponential function and the number e; decay by the same factor in each step, `exp(-k t)`. General knowledge. |
| `new:100` | hands-on | home | Optional practice on Coin Run: the HUD's timer in a `float` stops growing; keep it in a `double`. General knowledge. |
| `new:216` | hands-on | home | Practice before the Coin Run item, by hand and in the playground's script with `Log::Info`, from easy to hard: Basic: 13 written in binary and `0xFF` in decimal, each checked with a logged value; Basic, predict then run: a `uint16_t` of 65,535 plus one stored back, and an `int` division that rounds down; Medium: bit 3 of a flags value set, cleared and tested with masks; Medium, predict then run: `0.1f + 0.2f == 0.3f`, then the same sum compared with a tolerance; Hard: the gap between neighbouring floats at 1, 1,000 and 20,000 found with `std::nextafter` and logged. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `physics:538` | term | home | Determinism, in general; that Strata's holds for any thread count is linked to `core/jobs` |
| `render-image:639` | term | home | NaN and Inf, the results of broken arithmetic |
| `scene-ecs:421` | figure | link | The entity handle's 20-bit index and its version, linked to `world/ecs` as the packing example |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Memory as numbered bytes | `basics/computer` | must |
| Variables, the types `int`, `float`, `double` and `bool`, and operators | `basics/programming-1` | must |
| Loops, for the worked examples that repeat a step | `basics/programming-2` | helps |
| Exposure in EV stops as the editor shows it | `make/lighting` | helps |
| Coin Run's HUD timer | `make/hud` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run by hand and in the playground's script.

## `basics/data-structures` — Data structures I: arrays, lists, hash maps and their cost

**Covers.** Every structure is drawn first, then written in a few lines of C++ with arrays, structs and loops, and its
cost counted. The cost of operations: counting steps, big-O (O(1), O(log n) with the logarithms of `basics/numbers`,
O(n), O(n log n), O(n²)), constant time, and why a cost on paper meets the cache of `basics/computer`. Arrays: side by
side in memory, an index in constant time, inserting in the middle in O(n), a dynamic array that grows by doubling,
arrays and their cost as the base of everything after. Binary search on a sorted array. Removing from an array by
swapping with the last element; free lists of slots, and indices that stay valid with a version that catches a stale
one. Linked lists, single and double, with pointers or with indices, and lists kept inside the items themselves (as
Strata's hierarchy keeps its links in a component, `world/scene-graph`); their cost against arrays. Stacks (last in,
first out; the word's second meaning beside the stack of memory). Queues (first in, first out), double-ended queues,
and ring buffers of fixed size that overwrite the oldest entry (the log's buffer and the profiler's frames). Hash maps
and hash sets: a hash function turns a key into a number (stable hashes are `basics/data-formats`'), buckets,
collisions, the load factor and growing; a cache as a hash map from a key to a result already computed; hash maps and
what they cost. Prefix sums and arrays of indices that point into one shared array. Arrays of structs against structs
of arrays, with the cache. Sparse sets: a packed array and an array of positions, adding, removing by a swap and
finding in constant time, walking the packed data; the sparse set and its cost (Strata's storage is `world/ecs`'). The
Test out box asks for the cost of an operation in big-O, the array left after a swap-remove, and the bucket a key lands
in. The Practice draws, writes and costs small cases of these structures and ends with the optional item on the
reader's Coin Run: keep the collected coins' names in a `std::vector` and in a hash set, remove with a swap, and count
the steps of each.

**Leaves out.**

- Trees, heaps, graphs and sorting → `basics/trees-graphs`
- The standard library's containers and algorithms as C++ → `basics/cpp-generic`
- Strata's sparse sets and entity storage → `world/ecs`
- Strata's hierarchy as linked lists and its lookup index → `world/scene-graph`
- Job queues → `core/jobs`
- Least recently used eviction → `assets/residency`
- Stable hashes, checksums and cryptographic hashes → `basics/data-formats`

**Fit.** `fits`: about 5,250 words against L (5,000). Eleven structures and ideas, each drawn, written in a few lines
of C++ and costed from zero (about 4,150), and the primer's fixed parts with the Test out box, the Practice and the
Coin Run item (about 1,100); hash maps and sparse sets take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:101` | concept | home | The cost of operations: counting steps, big-O, constant time. General knowledge. |
| `new:102` | concept | home | Arrays and dynamic arrays: an index in constant time, inserting in O(n), growth by doubling. General knowledge. |
| `new:103` | concept | home | Binary search and what it costs. General knowledge. |
| `new:104` | concept | home | Removing by a swap with the last element; free lists of slots; indices with a version. General knowledge. |
| `new:105` | concept | home | Linked lists with pointers or indices, and lists kept inside the items; their cost. General knowledge. |
| `new:106` | concept | home | Stacks, the data structure: last in, first out. General knowledge. |
| `new:107` | concept | home | Queues, double-ended queues and ring buffers of fixed size. General knowledge. |
| `new:108` | concept | home | Hash functions, hash maps and hash sets: buckets, collisions, load factor, growth; a cache as a hash map. General knowledge. |
| `new:109` | concept | home | Prefix sums and arrays of indices into one shared array. General knowledge. |
| `new:110` | concept | home | Arrays of structs against structs of arrays, with the cache. General knowledge. |
| `new:111` | concept | home | Sparse sets: packed array, positions, add, swap-remove and find in constant time. General knowledge. |
| `new:118` | hands-on | home | Optional practice on Coin Run: the collected coins in a vector and in a hash set, a swap-remove, the steps counted. General knowledge. |
| `foundation:614` | term | home | Ring buffer, in general; Strata's `LogBuffer` and the profiler's frames are its examples |
| `render-scene:571` | term | home | Structure of arrays, against an array of structs |
| `scene-ecs:284` | concept | use | Sparse sets as the storage `world/ecs` teaches, named as the reason for the structure |
| `scene-ecs:376` | code | use | `SceneHierarchy.h`, the links kept in a component, named as the example of a list inside its items |
| `scene-ecs:385` | code | use | The scene's lookup index, hash buckets with a swap-remove, named as an example |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Arrays, `std::vector`, loops, functions and structs | `basics/programming-2` | must |
| Pointers at the use level, and template arguments | `basics/programming-3` | must |
| Logarithms in base 2 | `basics/numbers` | must |
| Caches, and why the order of data in memory matters | `basics/computer` | must |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts.

## `basics/trees-graphs` — Data structures II: trees, heaps, graphs and sorting

**Covers.** The page goes on from `basics/data-structures` the same way: every structure is drawn first, then written
in a few lines of C++ with arrays, structs and loops, and its cost counted. Trees: root, parent and children; binary
search trees and ordered maps that keep their keys in order, whose nodes do not move, so references to them stay
valid; trees, their costs and big-O; depth-first walks with a stack and breadth-first walks with a queue. Binary heaps
as priority queues (a queue of loading work by priority, the open set of A*). Spatial trees (bounding volume
hierarchies, quadtrees and octrees) as the idea of halving the space to search. Graphs: nodes and edges, directed
graphs, dependency graphs, walking a graph breadth-first and depth-first, cycles; the topological order is named, and
Kahn's algorithm is `core/engine-modules`'. Union-find (disjoint sets) in one worked example. Sorting: what O(n log n)
means, stable sorts, and radix sort by the bytes of a key in O(n). The Test out box asks for the orders in which a
depth-first and a breadth-first walk visit a small tree, the item a heap gives out next, and whether a small graph has
a cycle. The Practice draws, writes and costs small cases of these structures and ends with the optional item on the
reader's Coin Run: walk the level's hierarchy from its roots, depth-first and breadth-first, and log each entity's name
with its depth.

**Leaves out.**

- `std::map`, `std::set` and `std::sort` as C++ → `basics/cpp-generic`
- Topological sort (Kahn) → `core/engine-modules`
- Reference graphs and closures of assets → `assets/references`
- Bounding volume trees in physics → `physics/collision-detection`
- A* and other searches for game AI → `appendix/game-ai`

**Fit.** `fits`: about 3,800 words against M (3,000). Seven ideas, each drawn, written in a few lines of C++ and costed
from zero (about 2,700), and the primer's fixed parts with the Test out box, the Practice and the Coin Run item (about
1,100); trees with their walks, graphs and sorting take the most, and the page stands about 200 words under M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:112` | concept | home | Trees, binary search trees and ordered maps whose nodes stay put; depth-first and breadth-first walks. General knowledge. |
| `new:113` | concept | home | Binary heaps as priority queues. General knowledge. |
| `new:114` | concept | home | Spatial trees as halving the space to search. General knowledge. |
| `new:115` | concept | home | Graphs, directed and dependency graphs, walks, cycles, a topological order named. General knowledge. |
| `new:116` | concept | home | Union-find (disjoint sets). General knowledge. |
| `new:117` | concept | home | Sorting: O(n log n), stable sorts, radix sort by bytes in O(n). General knowledge. |
| `new:207` | hands-on | home | Optional practice on Coin Run: the level's hierarchy walked from `Scene::GetRootEntities` through `Entity::GetChildren`, depth-first with a stack and breadth-first with a queue (both kept in a `std::vector`), each name logged with its depth, the `Walls` parent among them. Evidence: `StrataScriptCore/Include/StrataScript/Scene.h:134`, `StrataScriptCore/Include/StrataScript/Entity.h:53-56` |
| `foundation:332` | concept | use | The radix sort of the utilities, taught here as a sort (the item's home is `basics/data-formats`) |
| `foundation:256` | concept | link | Topological sorting and Kahn's algorithm, linked to `core/engine-modules` |
| `assets:297` | concept | link | Priority queues of loading work, linked to `assets/loading` |
| `assets:318` | concept | link | Dependency graphs of assets, linked to `assets/references` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Arrays, stacks, queues, hash maps, and the cost of an operation in big-O | `basics/data-structures` | must |
| Loops, functions, structs and `std::vector` | `basics/programming-2` | must |
| Pointers at the use level | `basics/programming-3` | must |
| Logarithms in base 2; bytes, shifts and masks, for radix sort | `basics/numbers` | must |
| Parents and children in the Hierarchy, as Coin Run's `Walls` holds the walls | `make/scenes-entities` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts.

## `basics/cpp-memory` — C++ memory: pointers, references, lifetimes, RAII and smart pointers

**Covers.** The page extends `basics/programming-3`, which used pointers and references only as far as a script calls
them, and puts the stack and the heap of `basics/computer` into code. Pointers in depth: `&` takes an address, `*`
reaches what a pointer points to (dereference), `->` on a member, a pointer drawn as an arrow into the row of memory.
References against pointers: a reference cannot be null or point elsewhere later; `const` references in parameters as
the way to pass large values. Three kinds of lifetime: automatic (local variables on the stack, gone at the closing
brace), static (globals, and `static` locals built the first time they are reached and kept to the end), and dynamic
(the heap, `new` and `delete`). What goes wrong: a memory leak, a dangling pointer, a double delete, a use after free.
Undefined behavior: a rule of C++ that nothing checks, after which the program may seem to work, crash or do anything,
with signed overflow and reading past an array's end as further cases. Destructors, which run by themselves at the end
of a lifetime, in the reverse order of construction; RAII, a resource tied to an object (a file, a lock, memory).
Ownership: one owner destroys; `std::unique_ptr` and `std::make_unique`; a factory that returns a unique pointer;
unique pointers cannot be copied, only moved (the mechanism of moving is `basics/cpp-modern`'s), so types that hold one
can only move. Shared ownership: `std::shared_ptr` and `std::make_shared`, the reference count and `use_count`, shared
state between parts of a program, and the cost (a count changed with atomic operations, a block beside the object).
Weak references: `std::weak_ptr`, `lock` and `expired`, and cycles of shared pointers that never die. Strata's names for
the three: `Scope`, `Ref` and `WeakRef` with `CreateScope` and `CreateRef`, shown from `Base.h` (Strata's rules for
them are `core/conventions`'). Raw pointers as borrowed: who deletes what, and never deleting what one does not own.
The cost of heap allocation, and why engines allocate early or later instead of every frame (heap allocation and why it
can wait); allocators: an arena that hands out memory in a row, a pool of equal slots, a free list. The Practice runs in
the playground's script, from easy to hard: the order of destructors predicted, then run; the compile error of copying
a unique pointer; a shared pointer's count and a weak pointer that expires; a small arena; it ends with the optional
Coin Run item: a HUD script keeps the `Coin*` that `GetScript` returned across frames; the coin is collected and
destroyed at the end of the frame, or hot reload makes the script again, and the kept pointer dangles; the fix is to
ask again each frame.

**Leaves out.**

- Move semantics and `std::move` → `basics/cpp-modern`
- Strata's rules for `Scope`, `Ref` and borrowed pointers → `core/conventions`
- The range allocator of the geometry pool → `gpu/geometry-pool`
- Locks as objects, and atomic counters → `basics/threads`
- Virtual destructors → `basics/cpp-classes`
- Holding asset handles instead of `Ref`s across frames → `assets/residency`
- GPU resources released later → `gpu/resources-lifetimes`

**Fit.** `fits`: about 5,850 words against L (5,000). Twelve ideas, each with a sketch and its output or its crash,
the pictures of pointers into memory and the quote of `Base.h` (about 4,550), and the common mistakes, the Practice's
four exercises, the Coin Run item and the fixed parts (about 1,300); ownership with the three smart pointers takes the
most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:119` | concept | home | Pointers in depth, extending the use level of `basics/programming-3` (`*` in a type, `nullptr`, `->`): `&`, `*`, `->`, a pointer drawn into memory. General knowledge. |
| `new:120` | concept | home | References against pointers; `const` references in parameters. General knowledge. |
| `new:121` | concept | home | Lifetimes: automatic, static (globals and `static` locals) and dynamic (`new`, `delete`). General knowledge. |
| `new:122` | concept | home | Memory leaks, dangling pointers, double deletes, use after free. General knowledge. |
| `new:123` | concept | home | Undefined behavior, with signed overflow and reading past an array's end. General knowledge. |
| `new:124` | concept | home | Destructors and their order; RAII. General knowledge. |
| `new:125` | concept | home | Ownership with `std::unique_ptr` and `std::make_unique`; factories; types that can only move. General knowledge. |
| `new:126` | concept | home | Shared ownership: `std::shared_ptr`, the reference count, `use_count`, shared state, the cost. General knowledge. |
| `new:127` | concept | home | Weak references: `std::weak_ptr`, `lock`, `expired`, cycles of shared pointers. General knowledge. |
| `new:128` | concept | home | Raw pointers as borrowed, and who deletes what. General knowledge. |
| `new:129` | concept | home | The cost of heap allocation, allocation that can wait, and allocators: arena, pool, free list. General knowledge. |
| `new:130` | hands-on | home | Optional practice on Coin Run: a `Coin*` kept across frames dangles after the coin's destruction or a hot reload. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:38`, `StrataScriptCore/Include/StrataScript/Script.h:49-52` |
| `new:217` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: the order in which three objects' destructors log, in one scope and in nested scopes; Medium: the compile error of copying a `std::unique_ptr` read, and the given line with `std::move` that compiles; Medium: the `use_count` of a `std::shared_ptr` logged as copies come and go, and a `std::weak_ptr` whose `expired` turns true; Hard: an arena over a fixed buffer that hands out memory in a row and frees it all at once, its use logged. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `foundation:152` | feature | home | `Scope`, `Ref` and `WeakRef` as aliases of `unique_ptr`, `shared_ptr` and `weak_ptr`, with `CreateScope` and `CreateRef` |
| `foundation:616` | term | home | RAII |
| `foundation:617` | term | home | `Scope`, `Ref` and `WeakRef` |
| `foundation:353` | code | use | `Strata/src/Strata/Core/Base.h`, its lines 40-61 shown as the three aliases (the whole excerpt is `core/conventions`') |
| `foundation:270` | concept | link | Ownership in Strata, linked to `core/conventions` |
| `foundation:162` | feature | link | The range allocator, linked to `gpu/geometry-pool` as an allocator of offsets |
| `gamedev:321` | concept | use | Destruction at the end of the frame, and the mistake of keeping `T*` across frames, for the practice |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The stack and the heap as places in memory; memory addresses | `basics/computer` | must |
| Classes, constructors, references and pointers at the use level | `basics/programming-3` | must |
| Destroying a collected coin | `make/scripting-scene` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in the playground's script.

## `basics/cpp-classes` — C++ classes in depth: inheritance, virtual calls and interfaces

**Covers.** The page extends the inheritance that `basics/programming-3` used for `override`. Inheritance in depth:
`public`, `protected` and `private` members, and the order in which the constructors and destructors of a base and a
derived class run. Virtual functions: a call through a base pointer or reference reaches the derived class's function;
`virtual`, `override` and `final`; the SDK's `Script` with its virtual callbacks as the first example. How a virtual
call works: one table of functions per class and a hidden pointer in each object, drawn, and what the call costs (one
more memory read, no inlining). Pure virtual functions (`= 0`), abstract classes, and interfaces: one interface with two
implementations and a virtual call, which is how an engine lets a lower layer call code written above it (`Window`,
`EngineModule`, an undo step as examples named for the parts that teach them). Virtual destructors, and deleting through
a base pointer. Polymorphism, and slicing (a derived object copied into a base value loses its own part). Operator
overloading: `+`, `==` and `[]` for one's own types, glm's vector operators as the example, and a defaulted `==`.
Enough to read a test framework's macros, which make classes that derive from one base. The Practice runs in the
playground's script, from easy to hard: the order of constructors and destructors predicted, then run; a call with and
without `virtual`; slicing; operators for a small struct; it ends with the optional Coin Run item: a base class
`Pickup` with a virtual `OnCollected`, and `Coin` and a new `SpeedBoost` derived from it, called through a `Pickup*`.

**Leaves out.**

- Templates, and type erasure without inheritance → `basics/cpp-generic`
- Strata's interfaces and registries as architecture → `core/layers-registries`
- The engine module interface → `core/engine-modules`
- Windows, events and layers → `core/windows-events`
- How the SDK detects which callbacks a script overrides → `scripting/abi-sdk`

**Fit.** `fits`: about 3,950 words against M (3,000). Eight ideas with sketches and the drawing of a table of
functions (about 2,650), and the common mistakes, the Practice's four exercises, the Coin Run item and the fixed parts
(about 1,300); virtual calls and interfaces take the most, and the page stands about 50 words under M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:131` | concept | home | Inheritance in depth: access, and the order of constructors and destructors. General knowledge. |
| `new:132` | concept | home | Virtual functions: a call through a base pointer, `virtual`, `override`, `final`. General knowledge. |
| `new:133` | concept | home | How a virtual call works: a table of functions per class, a hidden pointer per object, the cost. General knowledge. |
| `new:134` | concept | home | Pure virtual functions, abstract classes and interfaces; an interface that lets lower code call higher code. General knowledge. |
| `new:135` | concept | home | Virtual destructors. General knowledge. |
| `new:136` | concept | home | Polymorphism and slicing. General knowledge. |
| `new:137` | concept | home | Operator overloading, glm's operators, a defaulted `==`. General knowledge. |
| `new:138` | hands-on | home | Optional practice on Coin Run: `Pickup` with a virtual `OnCollected`, `Coin` and `SpeedBoost` derived from it. General knowledge. |
| `new:218` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: the order of a base's and a derived class's constructor and destructor logs; Medium: one call through a base reference, with and without `virtual`; Medium, predict then run: a derived object copied into a base value, and what its virtual call logs (slicing); Hard: `operator+` and a defaulted `==` for a small `Money` struct. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `scripting:105` | feature | use | The `Script` base class and its virtual callbacks as the first example |
| `foundation:348` | code | link | `EngineModule.h`, an interface with virtual hooks, linked to `core/engine-modules` |
| `foundation:350` | code | link | `Event.h`, a base class and its derived events, linked to `core/windows-events` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Inheritance and `override` at the script's level | `basics/programming-3` | must |
| Pointers, references, destructors and ownership | `basics/cpp-memory` | must |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in the playground's script.

## `basics/cpp-generic` — Generic C++: templates, lambdas and the standard containers

**Covers.** Templates: a function template and a class template, the compiler that writes a version for each type,
type and value arguments, several arguments (a format string and its values as an example), and `static_assert` that
checks a template's argument while compiling. The standard containers and what they cost, from
`basics/data-structures`: `std::vector`, `std::array`, `std::deque`, `std::map` and its order, `std::unordered_map`,
`std::set`, `std::bitset`, `std::pair` and `std::tuple`. Iterators: `begin` and `end`, the range-based `for` as
iterators, reverse iterators, and iterators that a change of the container makes invalid. The standard algorithms:
`std::sort` with a comparator, `std::find_if`, `std::remove_if` with `erase`. `std::map`'s node handles: `extract`
and `insert` with a hint. Lambdas: their syntax, captures by value and by reference, `this`, and object lifetimes (a
lambda that keeps a reference to a local that is gone). `std::function`: keeping any callable, callbacks stored in a
container, a function that takes a function and returns one. The C form of a callback: function pointers and a user
pointer (`void*`), and calling a C library from C++ with its configuration structs and result codes. Type erasure
(scene-ecs concept 17): one type that hides many, `std::function` and `void*` with `static_cast` back; CRTP, a base
class template that knows its derived class, for builders that chain calls; pointers to members (`float Coin::*`,
`&Coin::Speed`), as `ST_SCRIPT_FIELD` passes a member to the builder (`if constexpr` and `std::variant` of the same
concept are `basics/cpp-modern`'s). The Practice runs in the playground's script, from easy to hard: a function
template; sorting and removing with lambdas; captures by value and by reference predicted, then run; stored callbacks
and an iterator a change made invalid; it ends with the optional Coin Run item: sort the coins left by their distance
to the ball with `std::sort` and a lambda, and call a stored callback when the last coin is taken.

**Leaves out.**

- Move semantics, `if constexpr`, `std::variant`, concepts and `requires` → `basics/cpp-modern`
- What each data structure costs, from zero → `basics/data-structures`, `basics/trees-graphs`
- Strata's reflection, its builders and type erasure in use → `world/reflection`
- What `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD` do inside → `scripting/abi-sdk`
- Callbacks from a window library → `core/windows-events`
- Job functions moved into a queue → `core/jobs`

**Fit.** `fits`: about 5,550 words against L (5,000). Templates, the containers and their iterators, the algorithms,
node handles, lambdas, `std::function`, the C form of callbacks, type erasure, CRTP and pointers to members, twelve
ideas from zero (about 4,250), and the common mistakes, the Practice's four exercises, the Coin Run item and the fixed
parts (about 1,300); the containers and lambdas take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:139` | concept | home | Function and class templates; type and value arguments; several arguments. General knowledge. |
| `new:140` | concept | home | `static_assert` that checks a template's argument while compiling. General knowledge. |
| `new:141` | concept | home | The standard containers and their costs, `std::pair` and `std::tuple`. General knowledge. |
| `new:142` | concept | home | Iterators, reverse iterators, and iterators made invalid by a change. General knowledge. |
| `new:143` | concept | home | The standard algorithms: `std::sort` with a comparator, `std::find_if`, `std::remove_if`. General knowledge. |
| `new:144` | concept | home | `std::map`'s node handles: `extract`, and `insert` with a hint. General knowledge. |
| `new:145` | concept | home | Lambdas and captures by value and by reference; object lifetimes in a capture. General knowledge. |
| `new:146` | concept | home | `std::function`, callbacks in a container, functions that take and return functions. General knowledge. |
| `new:147` | concept | home | Function pointers and a user pointer; calling a C library: configuration structs and result codes. General knowledge. |
| `new:148` | concept | home | Pointers to members, as `ST_SCRIPT_FIELD` passes a member to the builder. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:857-858` |
| `new:149` | hands-on | home | Optional practice on Coin Run: coins sorted by distance with a lambda; a callback when the last coin is taken. General knowledge. |
| `new:219` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic: a function template `Largest` called with `int` and with `float`; Medium: `std::sort` with a lambda comparator, then `std::remove_if` with `erase`; Medium, predict then run: a lambda that captures a counter by value and one that captures it by reference, both called after the counter changes; Hard: a `std::vector` of `std::function` callbacks called in order, and why an iterator kept across a `push_back` must not be used. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `scene-ecs:336` | concept | home | Type erasure and templates: `std::function`, `void*` with `static_cast`, CRTP builders; its `if constexpr` and `std::variant` are taught on `basics/cpp-modern` |
| `scene-ecs:651` | term | home | Type erasure |
| `scene-ecs:652` | term | home | CRTP |
| `scripting:113` | feature | use | `ScriptClassBuilder<T>::Field<&T::M>`, a pointer to a member as a template argument |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Template arguments in angle brackets | `basics/programming-3` | must |
| Arrays and hash maps, and what they cost | `basics/data-structures` | must |
| Trees and ordered maps, and what they cost | `basics/trees-graphs` | must |
| Pointers, references and object lifetimes | `basics/cpp-memory` | must |
| Virtual functions | `basics/cpp-classes` | must |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in the playground's script.

## `basics/cpp-modern` — Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts

**Covers.** In the measure Strata's code uses each feature. Move semantics: copying against moving, `std::move`, `&&` in
a type, what is left in an object moved from, and types that can only move (a unique pointer, a thread); perfect
forwarding with `std::forward` and `Args&&...`, read on `CreateScope`. `std::optional` in depth, beyond the `has_value`
and `value_or` of `basics/programming-3`: `std::nullopt`, `*` and `->`, `value()` and its exception, and when to return
one. `std::variant` and `std::visit`. Views that point into someone else's data: `std::string_view` and `std::span`, how
they dangle, and walking a span backwards with reverse iterators. Scoped enumerations with a fixed underlying type
(`enum class X : uint32_t`), `static_cast` to and from numbers, and flag operators for scoped enums, as Strata's
`Base.h` defines them. `constexpr` variables and functions, `static_assert` on them, `if constexpr`. `auto`, `decltype`
and type traits (`std::is_same_v`, `std::is_base_of_v`). Concepts and `requires`. The preprocessor: `#include`,
`#define` and macros with arguments, `#if`, `#ifdef` and `#error`, definitions that the build passes in (`ST_DIST`,
`ST_WITH_<MODULE>` as examples), and why macros are kept for what nothing else can do (`ST_CORE_ASSERT`,
`ST_SCRIPT_CLASS`). Exceptions: `throw`, `try` and `catch`, one sentence that unwinding runs the destructors of the
objects it leaves, and that engine code does not throw (the rule is `core/conventions`'). `std::filesystem::path`:
joining with `/` and the extension (why its text encoding matters on Windows is `core/files`'). Incomplete types: a
class declared but not defined (`class Scene;`), and what a `std::unique_ptr` or a `std::span` of one needs. The
Practice runs in the playground's script, from easy to hard: a copy against a move predicted, then run; a function that
returns a `std::optional`; a `std::variant` visited; a `constexpr` function and a scoped enum with its type; it ends
with the optional Coin Run item: a function that returns the nearest coin as a `std::optional` (none when all are
taken), an `enum class` for the game's state with a `switch`, and the number of coins as a `constexpr`.

**Leaves out.**

- Strata's rules for errors, asserts and exceptions → `core/conventions`
- Paths and text encodings on Windows → `core/files`
- The flags and portability of Strata's build → `engineering/flags-portability`
- Compile definitions set by CMake → `basics/build`
- Strata's reflection with `std::variant` values → `world/reflection`
- The macros of the script SDK inside → `scripting/abi-sdk`

**Fit.** `fits`: about 6,000 words against L (5,000). Thirteen features, each with a sketch from zero (about 4,700),
and the common mistakes, the Practice's four exercises, the Coin Run item and the fixed parts (about 1,300); move
semantics and the preprocessor take the most, and the page stands about 500 words under L's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:150` | concept | home | Move semantics: copy against move, `std::move`, `&&`, the object moved from, types that only move. General knowledge. |
| `new:151` | concept | home | Perfect forwarding with `std::forward`, read on `CreateScope`. General knowledge. |
| `new:152` | concept | home | `std::optional` in depth, extending the use level of `basics/programming-3` (`has_value`, `value_or`): `std::nullopt`, `*`, `->`, `value()`. General knowledge. |
| `new:153` | concept | home | `std::variant` and `std::visit`. General knowledge. |
| `new:154` | concept | home | Views: `std::string_view` and `std::span`, how they dangle, reverse iterators over a span. General knowledge. |
| `new:155` | concept | home | Scoped enumerations with a fixed underlying type, `static_cast`, flag operators. General knowledge. |
| `new:156` | concept | home | `constexpr`, `static_assert` on it, `if constexpr`. General knowledge. |
| `new:157` | concept | home | `auto`, `decltype` and type traits. General knowledge. |
| `new:158` | concept | home | Concepts and `requires`. General knowledge. |
| `new:159` | concept | home | The preprocessor: `#include`, macros, `#if`, `#ifdef`, `#error`, definitions passed by the build. General knowledge. |
| `new:160` | concept | home | Exceptions: `throw`, `try`, `catch`; unwinding runs the destructors of the objects it leaves, in one sentence (core-q8). General knowledge. |
| `new:161` | concept | home | `std::filesystem::path`: joining, the extension. General knowledge. |
| `new:162` | concept | home | Incomplete types and forward declarations. General knowledge. |
| `new:163` | hands-on | home | Optional practice on Coin Run: the nearest coin as a `std::optional`, an `enum class` state with a `switch`, a `constexpr` count. General knowledge. |
| `new:220` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: the sizes of two `std::vector`s logged after a copy and after a `std::move`; Medium: a function that returns `std::optional<int>` and a caller that uses `value_or`; Medium: a `std::variant<int, std::string>` logged with `std::visit`; Hard: a `constexpr` function checked with `static_assert`, and an `enum class` with a fixed underlying type cast to a number and back with `static_cast`. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `foundation:353` | code | use | `Base.h`: `CreateScope`'s forwarding and the flag operators for scoped enums (the whole excerpt is `core/conventions`') |
| `scene-ecs:336` | concept | use | `if constexpr` for tag types and `std::variant` for values, the part of the concept taught here |
| `foundation:275` | concept | link | Errors: asserts, verifies, returned errors and exceptions, linked to `core/conventions` |
| `foundation:317` | concept | link | Paths made from narrow strings on Windows, linked to `core/files` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Templates, lambdas and the standard containers | `basics/cpp-generic` | must |
| Ownership and `std::unique_ptr` | `basics/cpp-memory` | must |
| `std::optional` at the use level | `basics/programming-3` | must |
| Header files and `#include` | `basics/programming-3` | must |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in the playground's script.

## `basics/build` — How a C++ program is built: from two files by hand to CMake

**Covers.** A two-file program built by hand, then with CMake, so that every later build is understood. From source to
machine code: the compiler turns one source file into an object file (`c++ -c main.cpp`, `cl /c main.cpp`, in OS tabs).
Translation units: the preprocessor copies each `#include`d header into the source file first (its directives are
`basics/cpp-modern`'s), so a header is never compiled alone; declarations against definitions, and the one-definition
rule. The linker joins object files and libraries, connects each use of a name to its definition (symbols), and reports
link errors (`undefined reference`, `unresolved external symbol`), which are not compile errors: the page shows one of
each. Executables and libraries: a static library is an archive of object files copied into each program that links
it, and on GNU's linker the order of static libraries on the link line matters (Strata's case stays an example of
`engineering/third-party`); a shared library (`.dll`, `.so`, `.dylib`) is loaded when a program starts; a module
library is loaded on purpose while the program runs, which is what a script module is. What runs before `main`:
globals are built in an order that C++ leaves open between translation units (static initialization and its order),
and a linker may drop an object file of a static library that nothing names. The worked example: `main.cpp`,
`Greeting.h` and `Greeting.cpp` compiled and linked in a terminal, run, then broken twice (a missing `;` and a missing
definition) to see both kinds of error. Build systems and incremental builds: compare file times and build only what
changed, and why changing a header rebuilds many files. CMake: a `CMakeLists.txt` with `add_executable`, `add_library`
and `target_link_libraries`, the configure step and the build step, generators (Visual Studio, Ninja), the cache, and
definitions passed to the code (`target_compile_definitions`); the two-file program built again with CMake. Build
configurations: Debug and Release, what optimization changes, debug information beside the machine code (what a
debugger reads, `basics/debugging`), and asserts that only some configurations keep. Linker optimizations: dropping
code nothing uses and folding identical functions into one (so two functions can share one address). The Practice
runs in a terminal on the two-file program, from easy to hard: what a changed file rebuilds predicted, then run; a link
error made and fixed; Debug against Release with an assert; a static library and the order of the link line; it ends
with the optional Coin Run item: read the `Scripts/CMakeLists.txt` the editor wrote and build the module by hand with
the two commands its comment gives.

**Leaves out.**

- The preprocessor's directives and macros → `basics/cpp-modern`
- Strata's CMake: layers as libraries, options and presets → `engineering/cmake`
- Building Strata from source → `engineering/building`, `core/first-change`
- Strata's configurations and Dist → `engineering/building`
- Shared libraries, symbol visibility and loading code at run time in Strata → `scripting/shared-libraries`
- How the editor builds scripts → `editor/script-builds`
- Building script modules outside the editor, as a game maker does it → `make/script-builds`
- Self-registration and Strata's composition root → `core/layers-registries`

**Fit.** `fits`: about 5,450 words against L (5,000). Ten ideas, with the two-file program built by hand with its real
output and its two errors and built again with CMake (about 4,150), and the common mistakes, the Practice's four
exercises, the Coin Run item and the fixed parts (about 1,300); libraries and CMake take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:164` | concept | home | The compiler: one source file into one object file, by hand. General knowledge. |
| `new:165` | concept | home | Translation units: headers copied in first, declarations and definitions, the one-definition rule. General knowledge. |
| `new:166` | concept | home | The linker, symbols, and link errors against compile errors. General knowledge. |
| `new:167` | concept | home | Executables, static libraries and their order on GNU's link line, shared libraries, module libraries. General knowledge. |
| `new:168` | concept | home | What runs before `main`: static initialization and its order; objects of a static library that a linker drops. General knowledge. |
| `new:169` | hands-on | home | The two-file program built and linked by hand, run, and broken twice. General knowledge. |
| `new:170` | concept | home | Build systems and incremental builds by file times; a changed header. General knowledge. |
| `new:171` | concept | home | CMake: `add_executable`, `add_library`, `target_link_libraries`, configure and build steps, generators, the cache, compile definitions. General knowledge. |
| `new:172` | concept | home | Build configurations: Debug and Release, optimization, debug information, asserts. General knowledge. |
| `new:173` | concept | home | Linker optimizations: unused code dropped, identical functions folded. Evidence: `CMake/StrataConfigurations.cmake:49-51` |
| `new:174` | hands-on | home | Optional practice on Coin Run: the module built by hand with the two commands in its `CMakeLists.txt`. Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:216-218` |
| `new:221` | hands-on | home | Practice before the Coin Run item, in a terminal on the two-file program, from easy to hard: Basic, predict then run: which files a build compiles again after `Greeting.cpp` changes, and which after `Greeting.h` changes; Medium: a third file that declares a function and never defines it, and the link error read and fixed; Medium: the program built in Debug and in Release with CMake, and an `assert` that stops only one of them; Hard: `Greeting.cpp` made into a static library, and with GNU's linker two libraries swapped on the link line to see the error. General knowledge. |
| `build-test:271` | concept | home | From source files to a program: compiling per translation unit, then linking; the mistakes of thinking a header is compiled and of taking a link error for a compile error |
| `build-test:609` | term | home | Translation unit |
| `build-test:610` | term | home | Linker |
| `build-test:611` | term | home | Static library, shared library and module library |
| `gamedev:364` | code | use | The game's `CMakeLists.txt` as the editor writes it, read for the practice (its home is `make/script-builds`) |
| `foundation:208` | concept | use | An executable against a library, static against shared, the general half |
| `build-test:277` | concept | link | Configure, build and test as Strata's three steps, linked to `engineering/cmake` |
| `build-test:380` | code | link | Strata's three configurations, linked to `engineering/cmake` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A terminal: running a program with arguments, quoting a path | `basics/tools` | must |
| Header and source files, `#include`, declarations | `basics/programming-3` | must |
| Machine code and a process | `basics/computer` | must |
| Macros and `#if` | `basics/cpp-modern` | helps |
| Debug information as a debugger uses it | `basics/debugging` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in a terminal on the page's two-file program.

## `basics/bytes` — Bytes in files and memory: layouts, byte order and text encodings

**Covers.** Files as bytes: a file format as the agreed layout of a file's bytes, text files and binary files, and the
sizes of files and buffers in bytes, KiB and MiB (the prefixes are `basics/numbers`' powers of two). Numbers as bytes:
the sizes of types, byte order (little-endian and big-endian), and a 32-bit number read from four bytes. Binary layouts:
offsets, a header with a magic number and a version, sizes and counts, and lengths read from a file that cannot be
trusted (bounded by the file's size before anything is allocated). Structs as bytes: `sizeof`, alignment and padding,
`offsetof`, standard-layout types, and a layout checked with `static_assert` (sizes, alignment and `static_assert` as
the GPU's data and the packs need them). Images as bytes: pixels, channels and rows. Text: a text character, Unicode
and its code points, ASCII. UTF-8: one to four bytes per code point, continuation bytes of the form `10xxxxxx`, why
cutting text by bytes can split a character (eliding text by characters), U+FFFD for bytes that are not valid UTF-8,
and counting characters against counting bytes. UTF-16 and code pages: Windows' wide text and its older narrow
encodings (Strata's rule at the boundary is `core/files`'). The Test out box asks for the four bytes of a 32-bit number
in little-endian order, the size of a struct with padding, and the number of bytes a character takes in UTF-8. The
Practice reads and writes bytes by hand and ends with the optional item on the reader's Coin Run: rename a coin with a
letter outside ASCII (`Münze`) and log its name's length in bytes and in code points.

**Leaves out.**

- Binary, hexadecimal and the sizes of integer types → `basics/numbers`
- JSON, Base64, hashes, checksums and UUIDs → `basics/data-formats`
- Text and paths on Windows, and Strata's conversions → `core/files`
- Corrupt and hostile files in the asset pipeline → `assets/robustness`
- Text on screen: shaping and fonts → `gpu/text`, `ui/text`
- A binary format read defensively in Strata's tools → `engineering/generated-code`

**Fit.** `fits`: about 4,300 words against L (5,000). Eight ideas from zero at B0's length, with a header's layout, a
padded struct and UTF-8's bytes drawn (about 3,200), and the primer's fixed parts with the Test out box, the Practice
and the Coin Run item (about 1,100); binary layouts and structs as bytes take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:175` | concept | home | Files as bytes, file formats, text and binary files; sizes in bytes, KiB and MiB. General knowledge. |
| `new:176` | concept | home | Numbers as bytes: sizes of types, byte order, a 32-bit number read from four bytes. General knowledge. |
| `new:177` | concept | home | Binary layouts: offsets, a header with a magic number and a version, counts, lengths that cannot be trusted. General knowledge. |
| `new:178` | concept | home | Structs as bytes: `sizeof`, alignment, padding, `offsetof`, standard layout, a layout checked with `static_assert`. General knowledge. |
| `new:179` | concept | home | Images as bytes: pixels, channels and rows. General knowledge. |
| `new:180` | concept | home | Text characters, Unicode, code points and ASCII. General knowledge. |
| `new:181` | concept | home | UTF-8: one to four bytes, continuation bytes, cutting by bytes, U+FFFD, counting characters. General knowledge. |
| `new:182` | concept | home | UTF-16 and code pages. General knowledge. |
| `new:208` | hands-on | home | Optional practice on Coin Run: a coin renamed `Münze` in the Inspector, and a script that logs the name's length in bytes and in code points, counted by skipping continuation bytes. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:43-44`, `StrataScriptCore/Include/StrataScript/ScriptABI.h:14` |
| `audio-input:666` | term | home | UTF-8 |
| `audio-input:667` | term | home | Code point; U+FFFD |
| `gameui:678` | term | home | Code point; UTF-8 continuation byte |
| `foundation:627` | term | home | UTF-8, UTF-16 and code page |
| `foundation:317` | concept | link | Text and paths in Strata, linked to `core/files` |
| `assets:351` | concept | link | Untrusted input and corruption, linked to `assets/robustness` |
| `build-test:390` | code | link | `ParseSpirv`, a binary format read defensively, linked to `engineering/generated-code` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Binary, hexadecimal, integer types and their sizes, shifts | `basics/numbers` | must |
| Files, folders and a code editor | `basics/tools` | must |
| Structs and their members | `basics/programming-2` | must |
| `static_assert` and `sizeof` in code | `basics/cpp-generic` | must |
| Renaming an entity, for the Coin Run item | `make/scenes-entities` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts.

## `basics/data-formats` — JSON, Base64, hashes and UUIDs

**Covers.** The page goes on from `basics/bytes` to the formats written in text and to the numbers made from data to
check it or to name it. Numbers written as text and read back, with enough digits to give the same float again. JSON:
objects, arrays, strings, numbers, `true`, `false` and `null`, quotes and commas; comparing two JSON values; a format
header with a version, read on the Tetris sample's project file (whose start scene is a handle of 16 hexadecimal
digits); reading text by hand, a character at a time into tokens, as the start of a parser, and why a strict reader
refuses what a lenient one forgives. Regular expressions, in about 350 words, because pages of track E quote patterns
that no earlier page teaches (`critique/rulings-7.md`, R31): literal characters, `.`, `*`, `+`, `?`, classes such as
`[a-z]`, the anchors `^` and `$`, groups and escaping; a glob such as `*.cpp` turned into a pattern; and why JSON needs
a parser and not a pattern. Base64: three bytes written as four safe characters. Hashes: the hash function of
`basics/data-structures` recalled, a stable hash against `std::hash`, FNV-1a in Strata's own ten lines (`Hash.h`), and
in one sentence `Hash::Combine`, which mixes one hash into another. Checksums: CRC-32C catches damaged data; in one
sentence, Strata computes it with the processor's CRC instructions where it has them and gets the same result
everywhere; a checksum is no protection against someone who changes the data on purpose. Cryptographic hashes: SHA-256,
why it cannot be undone or forged, a digest written in hexadecimal, and a keyed hash and a comparison in constant time
named with a link to `automation/security`, which teaches HMAC. UUIDs: random identifiers so large that two never meet;
the standard's UUID has 128 bits written as 32 hexadecimal digits, while Strata's has 64 bits written as 16 (`world/ecs`
uses it). The Test out box asks the reader to find the error in a broken JSON text, to say what a checksum catches and
what it does not, and to tell how many hexadecimal digits Strata's UUID takes. The Practice reads, tokenizes and hashes
small texts and ends with the optional item on the reader's Coin Run: open its `.stproj` in the code editor without
changing it, and find its format header, its version and the handle of its start scene.

**Leaves out.**

- Byte order, binary layouts and UTF-8 → `basics/bytes`
- Hash maps, buckets and collisions → `basics/data-structures`
- Radix sort and the offset allocator of the utilities → `basics/trees-graphs`, `gpu/geometry-pool`
- Scene documents, streams and their formats → `world/serialization`
- Strata's UUID as the identity of entities and assets → `world/ecs`, `assets/handles-meta`
- HMAC, the challenge and the constant-time compare → `automation/security`
- JSON as a game maker writes it in command scripts → `make/automated-playtests`

**Fit.** `fits`: about 4,700 words against L (5,000). Nine ideas from zero at B0's length, the hash function recalled
rather than taught and `Hash::Combine` and the CRC instructions in a sentence each (about 3,100), two excerpts with what
to look for, the Tetris project file and FNV-1a in `Hash.h` (about 500), and the primer's fixed parts with the Test out
box, the Practice and the Coin Run item (about 1,100); JSON with reading text into tokens takes the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:183` | concept | home | Numbers written as text and read back exactly. General knowledge. |
| `new:184` | concept | home | JSON: objects, arrays, strings, numbers, `true`, `false`, `null`; comparing values; a format header and versions. General knowledge. |
| `new:185` | code | home | `Samples/Tetris/Tetris.stproj:1-22`: a JSON document with a format header (`"Format": "Project"`, `"Version": 3`) and handles as 16 hexadecimal digits |
| `new:186` | concept | home | Reading text by hand into tokens, the start of a parser; strict and lenient readers. General knowledge. |
| `new:209` | concept | home | Regular expressions in about 350 words: literal characters, `.`, `*`, `+`, `?`, classes such as `[a-z]`, the anchors, groups and escaping; a glob turned into a pattern; why JSON needs a parser and not a pattern. `editor-ui/ui-testing`, `engineering/cmake` and `engineering/generated-code` use it (`critique/rulings-7.md`, R31). General knowledge. |
| `new:187` | concept | home | Base64: three bytes as four characters. General knowledge. |
| `new:188` | concept | use | Hash functions as `basics/data-structures` teaches them (its home row `new:108`), recalled before a stable hash against `std::hash`. General knowledge. |
| `new:189` | code | home | `Strata/src/Strata/Core/Hash.h:11-28`: FNV-1a, a stable 64-bit hash in ten lines |
| `new:190` | concept | home | Checksums: CRC-32C for damaged data, with `CRC32C("123456789")` as the worked check value. Evidence: `Strata/src/Strata/Core/Hash.h:49-53` |
| `new:191` | concept | home | Cryptographic hashes: SHA-256, digests in hexadecimal; a keyed hash and a constant-time compare named. General knowledge. |
| `new:192` | concept | home | UUIDs: the standard's 128 bits in 32 hexadecimal digits, Strata's 64 bits in 16. Evidence: `Strata/src/Strata/Core/UUID.h:13-14` |
| `new:193` | hands-on | home | Optional practice on Coin Run: its `.stproj` read in the code editor, its format header, version and start scene's handle found. Evidence: `Samples/Tetris/Tetris.stproj:1-22` |
| `automation:728` | term | home | JSON |
| `automation:745` | term | home | Hash (SHA-256) |
| `foundation:643` | term | home | FNV-1a, CRC-32C and SHA-256 taught here; HMAC named with a link to `automation/security`, which teaches it |
| `scene-ecs:664` | term | home | CRC-32C, a checksum that catches damaged data: one glossary entry with `foundation:643`'s CRC-32C; `world/serialization` links it for the cooked scene's header |
| `foundation:332` | concept | home | Utilities engines need: stable hashes against `std::hash`, UUIDs, CRCs, cryptographic hashes, constant-time compares, Base64; its binary layouts and untrusted lengths are taught on `basics/bytes`, radix sort on `basics/trees-graphs`, the offset allocator on `gpu/geometry-pool`, HMAC on `automation/security` |
| `foundation:155` | feature | home | Strata's `Hash`: FNV-1a (the excerpt `new:189`), `Combine`, which mixes one hash into another (`Strata/src/Strata/Core/Hash.h:41-47`), and CRC-32C, computed with the processor's CRC instructions where it has them and with the same result everywhere (`new:190`; `Hash.h:49-53`); `Combine` and the hardware path take a sentence each; `reference/core` keeps the header's generated table and links here |
| `foundation:156` | feature | link | `Crypto` (SHA-256, HMAC, the constant-time compare), linked to `automation/security` |
| `foundation:154` | feature | link | Strata's `UUID`, linked to `world/ecs` |
| `scene-ecs:342` | concept | link | Serialization formats, linked to `world/serialization` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Bytes, byte order, binary layouts and UTF-8 | `basics/bytes` | must |
| Binary, hexadecimal, bits and shifts, floating point | `basics/numbers` | must |
| Loops, functions and `std::string`, for reading text a character at a time | `basics/programming-2` | must |
| Files and a code editor | `basics/tools` | must |
| Hash maps, which use hash functions | `basics/data-structures` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts.

## `basics/threads` — Threads, atomics and races

**Covers.** In general; Strata's job system is `core/jobs`'. A thread: one line of work inside a process that runs at
the same time as the others and shares the process's memory; starting one with `std::thread` and a lambda, `join`, and
the main thread a program starts with. Parallel and concurrent: several threads on several cores at once, or taking
turns on one (the cores and hardware threads of `basics/computer`); the CPU and the GPU are two processors that work at
the same time, and threads in general. Data races and race conditions: a counter that two threads increment loses
counts, a data race is undefined behavior, and a test that passes a thousand times can still hide one. Mutexes and
locks: `std::mutex`, `std::lock_guard` and `std::scoped_lock` as RAII, what a locked call costs when no other thread
waits and when one does, and shared and exclusive locks (`std::shared_mutex`) for many readers and one writer.
Deadlock: two locks taken in two orders, and the cures: take locks one at a time, or always in one order. Condition
variables: a thread that waits until another tells it, with a predicate against spurious wake-ups, `notify_one` and
`notify_all`, and waiting until a time (`wait_until`). Atomics: `std::atomic` counters and flags, `exchange` and
compare-exchange, an atomic flag that tells a thread to stop, and joining threads after it. Memory order: why one
thread can see another's writes in another order, relaxed order for a counter, acquire and release for handing over a
message, and fences. Thread-local variables (`thread_local`, written `t_` in Strata's code). Thread pools and jobs, a
fixed set of threads that run small pieces of work; lock-free sharing in general; and one owner thread for some data as
a design that needs no lock (the main-thread rule, whose Strata form is `core/jobs`'). The Practice runs in the
playground's script, whose threads call nothing of the engine and are joined before the callback returns, from easy to
hard: a race on a counter predicted, then run; the same with a mutex and an atomic; a deadlock and its cure; a
condition variable that hands one value over; it ends with the optional Coin Run item: all of Coin Run's script
callbacks run on the main thread, so its scripts share data without a lock; the reader explains why, and predicts what
would break if a script started a thread that moved the ball.

**Leaves out.**

- Strata's job system, pools, `ParallelFor` and waiting → `core/jobs`
- The threading model of the engine: who owns the scene, hand-offs to the main thread → `core/jobs`
- The audio thread's hand-off → `audio/engine`
- GPU work in parallel, and synchronizing with the GPU → `gpu/how-a-gpu-frame-works`, `gpu/compute`
- Determinism of parallel work → `core/jobs`
- Threads in automation's server → `automation/rpc-server`

**Fit.** `fits`: about 5,450 words against L (5,000). Ten ideas, each with a sketch that runs and its output, and two
timelines of threads (about 4,150), and the common mistakes, the Practice's four exercises, the Coin Run item and the
fixed parts (about 1,300); memory order takes the most room.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:194` | concept | home | A thread: `std::thread` with a lambda, `join`, the main thread. General knowledge. |
| `new:195` | concept | home | Parallel and concurrent; threads on cores; the CPU and the GPU at the same time. General knowledge. |
| `new:196` | concept | home | Data races and race conditions; undefined behavior; tests that miss them. General knowledge. |
| `new:197` | concept | home | Mutexes and locks as RAII, the cost of a locked call, shared and exclusive locks. General knowledge. |
| `new:198` | concept | home | Deadlock and its cures: one lock at a time, or one order. General knowledge. |
| `new:199` | concept | home | Condition variables: a predicate, spurious wake-ups, notify, `wait_until`. General knowledge. |
| `new:200` | concept | home | Atomics: counters, flags, `exchange`, compare-exchange; a stop flag and joining threads. General knowledge. |
| `new:201` | concept | home | Memory order: relaxed, acquire and release, fences. General knowledge. |
| `new:202` | concept | home | Thread-local variables, written `t_` in Strata's code. Evidence: `Strata/src/Strata/Core/JobSystem.cpp:27-31` |
| `new:203` | concept | home | Thread pools and jobs; lock-free sharing; one owner thread as a design. General knowledge. |
| `new:204` | hands-on | home | Optional practice on Coin Run: its scripts run on the main thread and share data without a lock. Evidence: `AGENTS.md:188-190` |
| `new:222` | hands-on | home | Practice before the Coin Run item, in the playground's script, with threads that call nothing of the engine and are joined before the callback returns, from easy to hard: Basic, predict then run: two `std::thread`s that each add one to a plain `int` a million times, and the total logged after both are joined; Medium: the same with a `std::mutex` and with a `std::atomic<int>`, each timed; Medium: a deadlock drawn as two threads that take two locks in two orders, and its cure; Hard: a condition variable with a predicate that hands one value from a worker thread to the waiting callback. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `foundation:284` | concept | home | Threads and synchronization basics: threads, data races, mutexes, condition variables, atomics, memory order and fences, thread-local storage; its Strata examples (`ThreadActivity`'s sequence lock, `JobState`'s claim flag) are named with links to `core/jobs` |
| `foundation:596` | term | home | Deadlock |
| `foundation:597` | term | home | Data race |
| `foundation:598` | term | home | Mutex and condition variable |
| `foundation:599` | term | home | Atomic, memory order and fence |
| `foundation:601` | term | home | Thread-local |
| `audio-input:634` | term | home | Atomic, in general |
| `foundation:288` | concept | link | Job systems, linked to `core/jobs` |
| `foundation:296` | concept | link | The threading model of an engine, linked to `core/jobs` |
| `foundation:361` | code | link | The sequence lock, linked to `core/jobs` as memory order at work |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Processor cores and hardware threads; caches | `basics/computer` | must |
| Lambdas and `std::function` | `basics/cpp-generic` | must |
| RAII, destructors and undefined behavior | `basics/cpp-memory` | must |
| Queues | `basics/data-structures` | must |
| Moving an object that can only move | `basics/cpp-modern` | helps |
| The CPU preparing a frame while the GPU draws the one before | `start/what-an-engine-is` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in the playground's script.

## Passed on

none

## Not taken

none

## Questions for the planner

none
