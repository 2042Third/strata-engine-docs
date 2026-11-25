# Brief: `core/debugging`

| Field | Value |
| --- | --- |
| Title | Debugging the engine: debuggers, asserts, the log and crash reports |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/first-change`, `core/platform`, `basics/debugging` |
| From | new (curricula 1.18); foundation §1.5, §1.7 (`Platform`'s debugger functions, memory); debugger setup per OS, asserts and verifies, the log, crash reports, debugging one test; the general method is `basics/debugging`'s |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/debugging` — Debugging the engine: debuggers, asserts, the log and crash reports

**Covers.** The job: how to find a bug in the engine itself with a debugger, the asserts, the log and what a crash
leaves behind. The method is `basics/debugging`'s; this page applies it to Strata, and its problem section is one
paragraph on why engines are harder to debug (optimized builds, threads, the GPU, crashes in code the reader did not
write). The map: where each tool hooks in. The contract and its use: the debugger on the engine built from source, in
tabs per OS (the Visual Studio solution the `windows` preset writes; `compile_commands.json` for other code editors; gdb
on Linux and lldb on macOS with the Ninja presets; Debug for stepping, Release when a bug shows only optimized); asserts
while debugging (the default handler logs, breaks when a debugger is attached and aborts otherwise; `SetAssertHandler`
with Break, Abort and Continue; `Platform::IsDebuggerAttached`; `ST_DEBUGBREAK`); the log as a tool, its machinery as
its home: `LogBuffer`, the ring that the Console panel and `log.read` read at once; `BackgroundLogSink`, which writes
the console and the file in order on a thread of its own; warnings and errors that wait for it, so they are on disk if
the process dies next; its bounded queue, and `FlushFor` for console control handlers; where the log file is (every
start empties it, and every editor of the user writes the same `StrataEditor.log`, a game its `Game.log`: read or copy
the log before starting again), and what a Console run prints; the asserts' handler quoted (`Assert.cpp`: the log line,
the handler, the abort); what a crash leaves: in a test, doctest's "test case CRASHED", the crash reporter's line that
names the test, and `STRATA_TEST_TRACE`; in a script, a contained crash reported with file and line (named,
`scripting/crash-containment`); in engine code nothing of Strata's own, an absence of "What Strata does not do" (no
crash handler and no dump: the log up to its last flushed line and the OS's report are what is left, and running under
the debugger or turning on the OS's crash dumps is what to do); one test debugged alone (doctest's `--test-case` and
`--test-suite` filters, the test program under the debugger, temporary checkpoints on standard error for a crash);
memory as a clue (`GetProcessMemory` and the peaks). The toy is a log sink that queues messages for a thread of its own,
in 40 lines; the real code is `Log::Init`, which builds the loggers from their sinks, and `BackgroundLogSink`'s
contract. The page's example: a test made to assert on purpose, found and fixed with the debugger, in tabs per OS. The
trace exercise follows one `ST_CORE_WARN` to the log file with the debugger. At the end the reader can debug the engine
and its tests on their OS, read an assert and the log, and find which test crashed.

**Leaves out.**

- A method for finding bugs; breakpoints and stepping in general → `basics/debugging`
- Debugging a game's scripts with a debugger attached to the editor → `make/play-test-debug`
- Debugging the GPU: the validation layer and frame captures → `gpu/debugging`
- Containing the crashes of scripts → `scripting/crash-containment`
- From an address to a file and line → `scripting/symbolization`
- The test program's crash reporter and helpers in full → `engineering/test-program`
- How to log: levels, macros and throttling → `core/conventions`

**Fit.** `fits`: about 4,400 words against L (5,000). The debugger set-ups in tabs per OS and the log's machinery take
the most; the assert handler's quote, the missing crash handler and the trace exercise follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:16` | feature | home | The engine under a debugger, per OS: the Visual Studio solution the `windows` preset writes, `compile_commands.json` for other code editors, gdb and lldb with the Ninja presets; Debug and Release for debugging. Evidence: `CMakePresets.json:10-48`; `CMake/StrataConfigurations.cmake:31` (`CMAKE_EXPORT_COMPILE_COMMANDS`) |
| `foundation:91` | feature | home | `LogBuffer`: the ring of recent messages with their sequence numbers, read by the Console panel and `log.read` |
| `foundation:92` | feature | home | `BackgroundLogSink`: the console and the file written on a thread of their own; warnings flush before the call returns; the bounded queue; `FlushFor`; one sentence next to where the log is (about 60 words, with `make/play-test-debug`'s line): every program start empties its log file, every editor of the user writes the same `StrataEditor.log` and a game writes its `Game.log`, so the log of a run that crashed is read or copied before the next start (`Strata/src/Strata/Core/Log.cpp:224`, the file sink opened with truncation; `StrataEditor/src/EditorApplication.cpp:283-287`; `StrataRuntime/src/RuntimeApplication.cpp:457-458`) |
| `foundation:355` | code | home | `Strata/src/Strata/Core/Log.cpp:193-268`: loggers built from sinks (the ring, the background writer, the file), flush on warning, the three loggers; the inventory's 193-265 stops before the Script logger |
| `foundation:356` | code | home | `Strata/src/Strata/Core/BackgroundLogSink.h:21-89`: asynchronous logging as a contract: order, flushes, the bounded queue, stopping |
| `foundation:416` | figure | home | The log's path: a log call to the ring at once and to the queue, the writer thread to the console and the file, the flush barrier of warnings |
| `foundation:436` | figure | home | The editor's Console panel, backed by `LogBuffer`, with the Strata, App and Script loggers and their levels |
| `foundation:615` | term | home | Asynchronous logging |
| `foundation:93` | feature | use | The assert handler and the debugger detection in use: what a failed assert does with and without a debugger |
| `foundation:354` | code | use | `Strata/src/Strata/Core/Assert.cpp:32-66`, quoted here and not on `core/conventions`: the log line, the handler that can be replaced, the abort, read while debugging |
| `foundation:120` | feature | use | `Platform::IsDebuggerAttached`, `GetProcessMemory` and the peaks |
| `foundation:97` | feature | link | `CrashGuard` and `Symbolizer`, named as what reports a script's crash |
| `foundation:614` | term | link | Ring buffer, whose entry is `basics/data-structures`' |
| `build-test:112` | feature | use | The crash reporter that names the test that crashed, and `STRATA_TEST_TRACE` |
| `build-test:249` | feature | home | Debugging a crashing test: temporary checkpoints on standard error, flushed, between statements, the one test case run alone, a copy of the file kept and the checkpoints removed afterwards |
| `build-test:105` | feature | use | The test program, run alone under the debugger with doctest's filters |
| `new:33` | not-done | home | No crash handler and no crash dumps for the engine's own crashes: only guarded script calls are contained; a crash in engine code ends the process with no report or dump of Strata's own, and the log keeps every warning and error but loses the info and trace lines still queued. What is left (the log up to its last flushed line, the OS's report) and what to do (run under the debugger, or turn on the OS's crash dumps; the writer checks each OS's tool), about 100 words, by book.md's rule 1. Evidence: `git grep -n -e MiniDumpWriteDump -e SetUnhandledExceptionFilter -e set_terminate 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src` finds nothing; `Strata/src/Platform/Posix/PosixCrashGuard.cpp:92-109` (outside a guarded call a signal goes where it would have gone without the guard); `Strata/src/Strata/Core/BackgroundLogSink.h:29-32` |
| `new:34` | hands-on | home | Trace it yourself, the page's trace exercise: one `ST_CORE_WARN` followed with the debugger from the macro to the ring of `LogBuffer`, the queue of `BackgroundLogSink`, its writer thread and the log file, and the flush that makes the warning reach the file before the call returns. Evidence: `Strata/src/Strata/Core/Log.cpp:193-268`; `Strata/src/Strata/Core/BackgroundLogSink.h:21-32` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A method, breakpoints, stepping, the call stack, attaching a debugger | `basics/debugging` | must |
| The source build in Debug, and one test case run alone | `core/first-change` | must |
| Asserts, verifies and the log macros | `core/conventions` | must |
| The `Platform` class and signals | `core/platform` | must |
| Threads, mutexes and condition variables | `basics/threads` | must |
| The threads of a process | `core/jobs` | must |
| Ring buffers | `basics/data-structures` | helps |
| Containing the crashes of scripts | `scripting/crash-containment` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `asynchronous-logging` | Asynchronous logging | - |
