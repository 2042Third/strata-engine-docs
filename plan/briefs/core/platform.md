# Brief: `core/platform`

| Field | Value |
| --- | --- |
| Title | Talking to the operating system |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/jobs` |
| From | foundation "Talking to the operating system" (§1.7: `Platform`; §1.2: interrupts, the GUI subsystem, power throttling; concepts 19, 21-22): seams and detection, console and GUI programs, signals and exit codes, dialogs, thread priorities, sleep precision; files are `core/files`' |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/platform` — Talking to the operating system

**Covers.** The job: how engine code reaches the operating system through one seam, and what Strata asks of Windows,
Linux and macOS. The problem in the part's full section on it: platform abstraction (detection by the preprocessor; one
interface with one implementation per OS chosen when linking, against virtual backends; window libraries such as GLFW
and SDL; where OS headers may appear). The map: `Core/Platform.h` above `Platform/Windows/` and `Platform/Posix/`, the
window backends beside them. The contract: platform detection (exactly one `ST_PLATFORM_*`, an `#error` for 32-bit
Windows, other Apple systems and every other target) and the absence of mobile, console and web targets; the `Platform`
class by group (paths and the user's folders, fallback fonts, processes and their times, memory, secure random numbers,
environment variables, opening a file with its program, `FindProgram`, error dialogs, binary standard streams; its
debugger and memory functions are read again on `core/debugging`); `Process`, the seam for child processes, as its home
(the output captured, merged or as two streams, inherited or discarded; piped input; `Wait` with a timeout and `Run` to
completion; the whole tree ended as one, through a job object on Windows and a process group on POSIX; its users: the
editor's script builds, the external editor, StrataCLI's launcher and the tests' helper processes); the rule for headers
(platform, window and graphics headers only in their Platform folders; never `<Windows.h>` in a header; no X11 headers;
no names that Windows defines as macros; no `None` in an unscoped enum); `WindowsUtils` at Win32's boundary of wide
strings. Then programs on Windows: the console and GUI subsystems, why the editor and the runtime are GUI programs,
`ConnectStandardStreams` keeping the pipes it was given or attaching to the parent's console for a Console run, the
decision as a table, and why PowerShell waits for a GUI program only when its output is piped. Then interrupts: Ctrl+C,
Ctrl+Break and closing the console on Windows, SIGINT and SIGTERM on POSIX, each turned into a request the loop honours;
a handler that only counts, because a signal handler may do only async-signal-safe work; a second request ends the
process at once; exit code 130. Then scheduling and power: priorities and scheduling quanta, processors with two kinds
of cores, Windows 11's power throttling of programs in the background and the opt-out at startup; thread names and
priorities; precise sleep (`SleepUntil` through a high-resolution waitable timer on Windows, because the default tick is
15.6 ms and `timeBeginPeriod` changes the whole system). The toy is a seam with two implementations that the build
chooses, in 40 lines; the real code is the POSIX interrupt handler, `ConnectStandardStreams` and Windows' `SleepUntil`.
The page's example: the editor run headless from a terminal and stopped with Ctrl+C. The exercises add a `Platform::`
function for every OS and its test, and trace Ctrl+C from the handler to the end of `Run`. At the end the reader can add
a function to the platform seam on every OS, and explain how a Strata program talks to its terminal and stops when
asked.

**Leaves out.**

- Files, paths and private files → `core/files`
- The editor's script builds, which run CMake and the compilers through `Process` → `editor/script-builds`
- Shared libraries and how script modules are loaded → `scripting/loading`
- Containing crashes with structured exceptions and signals → `scripting/crash-containment`
- The window backends → `core/windows-events`
- Sockets → `automation/json-rpc`
- The debugger and memory functions in use → `core/debugging`
- The pools whose priorities this page sets → `core/jobs`

**Fit.** `fits`: about 5,300 words against L (5,000). The three concepts (platform abstraction, programs on Windows,
scheduling and power) and the `Platform` class take the most; `Process` takes about 250 and the trace exercise about
250.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:308` | concept | home | Platform abstraction: detection by the preprocessor, one interface with an implementation per OS chosen when linking, against virtual backends; window libraries; where OS headers may appear; the mistakes (`<Windows.h>` in a header, X11's `None`) |
| `foundation:313` | concept | home | Programs on Windows: console and GUI subsystems, attaching to a parent's console, why PowerShell does not wait, signals and console control handlers, async-signal safety, exit codes |
| `foundation:300` | concept | home | Scheduling and power: priorities, scheduling quanta, processors with two kinds of cores, Windows 11's power throttling |
| `foundation:119` | feature | home | Platform detection |
| `foundation:120` | feature | home | The `Platform` class, by group; its debugger and memory functions are read again on `core/debugging` |
| `foundation:133` | feature | home | `WindowsUtils`: `Utf8ToWide` and `WideToUtf8` at Win32's boundary |
| `foundation:58` | feature | home | The GUI subsystem and `ConnectStandardStreams` |
| `foundation:57` | feature | home | Interrupt handling on Windows and POSIX |
| `foundation:59` | feature | home | The power-throttling opt-out |
| `foundation:112` | feature | home | `SetCurrentThreadName`, `SetCurrentThreadPriority` and `SleepUntil` |
| `foundation:364` | code | home | `Strata/src/Platform/Windows/WindowsPlatform.cpp:337-380`: precise sleep through a high-resolution waitable timer of the thread's own |
| `foundation:365` | code | home | `Strata/src/Platform/Posix/PosixPlatform.cpp:903-920`: an async-signal-safe handler that counts, and re-raises on the second request; with `PosixPlatform.cpp:981-995`, its installation (the inventory's 900-922 starts three lines early) |
| `foundation:366` | code | home | `Strata/src/Platform/Windows/WindowsPlatform.cpp:755-793`: console against GUI subsystem, the pipes kept and the parent's console attached |
| `foundation:420` | figure | home | The decision of a Windows run as a table: streams given, a Console run, a parent's console to attach, a dialog to show |
| `foundation:437` | figure | home | A terminal running `StrataEditor --headless --frames 120`: a Console run's output, and the message after Ctrl+C |
| `foundation:472` | rule | home | Platform, window and graphics headers only in their Platform folders; never `<Windows.h>` in a header; no X11 headers; no names Windows defines as macros; no `None` in an unscoped enum |
| `foundation:494` | rule | home | Sleeps on Windows are coarse; never call `timeBeginPeriod` |
| `foundation:496` | rule | home | GUI programs and PowerShell: pipe their output, or use `Start-Process -Wait`, to get the exit code |
| `foundation:498` | rule | home | A second Ctrl+C ends the process at once; the signal handler only counts |
| `audio-input:539` | rule | home | Unscoped enums never use `None`, because X11 defines it as a macro: part of `foundation:472`, with `AudioAttenuationModel::NoAttenuation` as the example of the name it forces (taken here rather than on `core/conventions`, whose page leaves the platform rules to this one) |
| `foundation:525` | hands-on | home | A new `Platform::` function: declared in `Core/Platform.h`, implemented in `WindowsPlatform.cpp` and `PosixPlatform.cpp`, tested in `PlatformTests.cpp`, checked with `Architecture.Layering` |
| `new:30` | hands-on | home | Trace it yourself: Ctrl+C in the terminal of a headless editor followed from the handler of the reader's OS (the console control handler on Windows, `OnInterruptSignal` on POSIX) to `Platform::IsInterruptRequested` in `Run`, the warning line and exit code 130, with breakpoints or a search; then what a second Ctrl+C does. Evidence: `Strata/src/Platform/Posix/PosixPlatform.cpp:903-920`, `:981-995`; `Strata/src/Strata/Core/Application.cpp:261-269` |
| `foundation:602` | term | home | Two entries: thread priority and scheduling quantum |
| `foundation:603` | term | home | Power throttling (EcoQoS) |
| `foundation:619` | term | home | Two entries: platform layer and seam |
| `foundation:622` | term | home | Two entries: console subsystem and GUI subsystem |
| `foundation:624` | term | home | Two entries: signal (SIGINT, SIGTERM) and console control handler |
| `foundation:625` | term | home | Async-signal-safe |
| `scripting:609` | term | home | Signal, the same entry as `foundation:624`'s first term |
| `new:14` | not-done | home | No mobile, console or web targets: 64-bit Windows, Linux and macOS only. Evidence: `Strata/src/Strata/Core/PlatformDetection.h:5-22`, an `#error` for every other target |
| `foundation:128` | feature | home | `Process`, the platform's seam for child processes (about 250 words, R31, D12): `ProcessOutputMode`'s captured output (merged, or stdout and stderr apart), inherited or discarded; piped input; `Wait` with a timeout and `Run` to completion, which ends the child on timeout; `TerminateTree`, which ends the child and every process it starts as one unit, through a job object on Windows and a process group on POSIX; its users named: the editor's script builds and toolchain discovery, the external editor, StrataCLI's `LaunchEditor` and the tests' helper processes (`Strata/src/Strata/Core/Process.h:18-96`); `editor/script-builds` and `automation/sessions` use it and link here |
| `foundation:129` | feature | use | `DynamicLibrary`, named as the seam for shared libraries; its home is `scripting/loading` |
| `foundation:626` | term | link | Exit code, whose entry is `basics/tools`' |
| `build-test:541` | rule | use | The same rule about PowerShell from the build's side |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| `#if`, `#error` and macros | `basics/cpp-modern` | must |
| Processes, environment variables, the standard streams and exit codes | `basics/tools` | must |
| PowerShell, and piping a program's output | `basics/tools` | must |
| Static member functions | `basics/programming-2` | helps |
| The pools and their threads | `core/jobs` | must |
| Atomics | `basics/threads` | must |
| The frame loop, which polls the interrupt, and the pacer, which sleeps | `core/frame-loop` | must |
| Console and Interactive runs | `core/first-frame` | must |
| UTF-8 and UTF-16 | `basics/bytes` | must |
| Writing and running one test case | `core/first-change` | must |
| The layer table and `ExternalOwners` | `core/layers-registries` | helps |
| Processor cores and hardware threads | `basics/computer` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `async-signal-safe` | Async-signal-safe | - |
| `power-throttling-ecoqos` | Power throttling (EcoQoS) | - |
| `scheduling-quantum` | scheduling quantum | - |
| `thread-priority` | Thread priority | - |
