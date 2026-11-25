# Brief: `scripting/crash-containment`

| Field | Value |
| --- | --- |
| Title | Crash containment |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `scripting/loading`, `core/conventions`, `core/debugging` |
| From | scripting ch. 12 without symbolization (hardware exceptions, SEH and signals, `CrashGuard` on Windows and POSIX, abort, what is not contained, exceptions against crashes, the watchdog; excerpts 16-19, figures 8 and 11) |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `scripting/crash-containment` — Crash containment

**Covers.** The job: keep the engine and the editor running when native game code faults, and say exactly what cannot be
contained. The problem and how engines solve it, the full section for the part: most engines go down with the game;
process isolation (a process per plug-in, as browsers do); sandboxed virtual machines (Lua, WebAssembly); and Strata's
guard in the same process, which faults the module and keeps the engine, with a table of what each costs per call and
what each contains. Then from zero: hardware exceptions (an access violation, a division by zero, an illegal
instruction, a stack overflow and the guard page; integer division by zero traps on x64 but not on ARM64, where it gives
0, so the engine's fault tests leave it out there), Windows structured exception handling against POSIX signals, and how
a guard resumes after a fault (`__try` and `__except`; `sigsetjmp` and `siglongjmp` from a handler on an alternate
signal stack). Where the guard lives: `CrashGuard` and `Symbolizer` are Core classes with their halves in
`Platform/Windows` and `Platform/Posix`, and only `ScriptModule` calls them. The contract as `CrashGuard.h` writes it:
what is contained, what is not (fail-fast terminations, `abort()` on POSIX, a heap corrupted while the allocator holds
its locks, `exit`), destructors that do not run, the module that is never called again until it is reloaded (a rebuild
or `script.reload` clears the fault). The toy: a POSIX guard in about 40 lines. The real code: the Windows filter that
chooses 18 exception codes, `_resetstkoflw` after a stack overflow and the separate function that error C2712 forces;
the 32 KiB stack guarantee; the POSIX handler on its alternate stack, the delivered signal unblocked, handlers of other
code forwarded, and macOS's return into a recovery routine. Abort containment in modules: the SDK's entry file with
`init_seg(lib)`, `_set_abort_behavior` and a SIGABRT handler that raises `ST_SCRIPT_ABORT_EXCEPTION_CODE`, only with the
static C runtime. Exceptions against crashes: an exception the SDK's firewall caught disables one instance; a crash
faults the module, whose instances are leaked on purpose. The watchdog, a thread that can only log a call that runs too
long: it is off by default, `SetWatchdogTimeout` turns it on, and neither the editor nor the runtime calls it (only
tests do), so an endless loop freezes the editor and logs nothing; and why a script must never block. What the person
sees: the Console's crash line, and the toast whose button is **Show Problems**. Tests: `Scripting.Faults` with the
`Faults` and `LoadFault` modules, and the guard's own cases in `Core.Platform` (faults repeated, on other threads,
nested, the signal mask kept), whose helper processes show what the guard lets through: an `abort()`, a signal another
process sends, and a thread that exits on Linux. The example is a null write in a copy of the `Coin` script's
`OnUpdate`, then an exception thrown in its place, compared. At the end the reader can say for any fault whether Strata
contains it, and in what state the engine is afterwards.

**Leaves out.**

- Walking the stack and naming its frames → `scripting/symbolization`
- Debugging a crash with a debugger, and the engine's own crash reports → `core/debugging`
- What the editor does after a crash (play stops) → `editor/play-mode`
- A shipped game's crash policy (scripts disabled, exit code 2) → `worlds/runtime`
- Process signals such as SIGINT and SIGTERM, and exit codes → `core/platform`

**Fit.** `fits`: about 6,300 words against L (5,000). The full section on how engines solve the problem, the hardware
background taught from zero, five excerpts and three exercises take the most words; the stack walk is
`scripting/symbolization`'s.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:303` | concept | home | Crash containment of native code: hardware exceptions, SEH against signals, recovery by jump, alternate stacks, guard pages, destructors that do not run, what cannot be contained; the approaches elsewhere; the mistakes |
| `scripting:311` | concept | home | Exceptions against crashes, and why the engine's own exceptions never unwind into the module |
| `scripting:183-186` | feature | home | `CrashGuard::Invoke` and `CrashInfo`; the Windows guard; the POSIX guard; abort containment in modules |
| `scripting:52` | feature | home | `ST_SCRIPT_ABORT_EXCEPTION_CODE` (0xE0535441), the exception a module raises when it calls `abort()` on Windows |
| `scripting:163` | feature | home | The containment contract that `ScriptEngine.h` lists |
| `scripting:176` | feature | home | The watchdog: off by default; `SetWatchdogTimeout` turns it on, and neither the editor nor the runtime calls it, only tests (`Strata/src/Strata/Scripting/ScriptEngine.h:95-96`, `ScriptEngine.cpp:257-266`; `StrataTests/src/Scripting/ScriptFaultTests.cpp:346`, `ScriptModuleTests.cpp:330`, `:341`); when on, it logs a call that runs too long and cannot interrupt it |
| `scripting:190` | feature | home | The policy: an exception disables one instance, a crash faults the module |
| `foundation:97` | feature | home | `CrashGuard` and `Symbolizer` as the Core layer lists them: Core classes with their halves in `Platform/`, called only by `ScriptModule`; the guard's cases in `Core.Platform` (`StrataTests/src/Core/PlatformTests.cpp:729-912`). The facts of `Symbolizer` are taught with `scripting:188` on `scripting/symbolization` |
| `scripting:369` | code | home | `Strata/src/Strata/Core/CrashGuard.h:35-68`: the contract, what is not contained included |
| `scripting:370` | code | home | `Strata/src/Platform/Windows/WindowsCrashGuard.cpp:96-159`: the SEH filter, `_resetstkoflw`, the `__try` in its own function (C2712); with lines 196-212, `Invoke` |
| `scripting:372` | code | home | `Strata/src/Platform/Posix/PosixCrashGuard.cpp:348-402`: `Invoke` with `sigsetjmp`, the unblocked signal, the alternate stack check; with lines 28-40 (leaving the handler on Linux and macOS) and 239-260 (the handler) |
| `scripting:359` | code | home | `StrataScriptCore/Source/ScriptModuleEntry.cpp:1-81`: abort containment in the module, `init_seg(lib)`, `_set_abort_behavior` and the SIGABRT handler, and the two exports |
| `scripting:417` | figure | home | Crash containment, Windows and POSIX side by side: the guarded call, the fault, the filter or handler, unwind or jump, `Invoke` returns false, the fault recorded, the module faulted; and the exits that are not contained |
| `scripting:437` | figure | home | The Console's crash message and location line, and the toast with **Show Problems** |
| `scripting:476` | rule | home | Exceptions disable an instance; crashes fault the module |
| `scripting:479` | rule | home | Never block in a script: native code cannot be preempted, and the watchdog can only log, and only where a host turned it on; the editor and the runtime do not, so an endless loop freezes the editor without a line in the log |
| `scripting:492` | rule | home | Windows modules use the static C runtime and the SDK's entry points to contain `abort()` |
| `scripting:525` | hands-on | home | Crash on purpose: a null write in `OnUpdate`, then an exception in its place; one instance disabled against the module faulted |
| `scripting:544` | hands-on | home | Lab: a small program around `CrashGuard::Invoke` that divides by zero, overflows the stack twice and calls `abort()`, on Windows and Linux; integer division by zero traps on x64, not on ARM64, where it gives 0 (`StrataTests/src/Scripting/ScriptFaultTests.cpp:31-34`) |
| `scripting:550` | hands-on | home | Design review: in-process containment against a child process or WebAssembly, the cost per call and what each contains |
| `new:24` | hands-on | home | The "trace it yourself" exercise (R32, D27): the null write of `scripting:525` followed with a debugger on the source build: on Windows the first-chance access violation, the filter that accepts it and `Invoke` returning false; on Linux the handler on the alternate stack and the jump back into `Invoke`; then `ScriptModule::Call`, which records the fault and returns `Faulted` (about 250 words). Evidence: `Strata/src/Platform/Windows/WindowsCrashGuard.cpp:96-159`, `:196-212`; `Strata/src/Platform/Posix/PosixCrashGuard.cpp:239-260`, `:348-402`; `Strata/src/Strata/Scripting/ScriptModule.cpp:317-327` |
| `scripting:564` | term | home | Alternate signal stack |
| `scripting:573` | term | home | CrashGuard |
| `scripting:582` | term | home | Fault: a faulted module is never called again until the module is reloaded; a rebuild or `script.reload` clears the fault (`Strata/src/Strata/Scripting/ScriptEngine.h:27-29`) |
| `scripting:608` | term | home | SEH (structured exception handling) |
| `scripting:610` | term | home | `sigsetjmp` and `siglongjmp` |
| `scripting:611` | term | home | Stack guarantee |
| `scripting:620` | term | home | Watchdog: off by default; `SetWatchdogTimeout` turns it on, and neither the editor nor the runtime calls it |
| `scripting:371` | code | use | `Strata/src/Platform/Windows/WindowsCrashGuard.cpp`, lines 43-60 of the excerpt: the stack guarantee (the stack walk of lines 61-94 is `scripting/symbolization`'s) |
| `scripting:106` | feature | use | The SDK's exception firewall, which decides that an exception is no crash |
| `scripting:385` | code | use | The `Coin` script, broken on purpose in a copy |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| How a computer runs a program: the CPU, the stack and the heap | `basics/computer` | must |
| Talking to the operating system: signals, exit codes, platform seams | `core/platform` | must |
| Debugging the engine: debuggers, asserts and crash reports | `core/debugging` | must |
| C++ exceptions and the engine's error policy | `core/conventions` | must |
| `ScriptModule::Call` and the fault it records | `scripting/loading` | must |
| The SDK's exception firewall (`InvokeScript`) | `scripting/abi-sdk` | must |
| Threads and per-thread state | `basics/threads` | helps |
| Hexadecimal numbers and bit patterns | `basics/numbers` | helps |
| Play mode and what stops it | `editor/play-mode` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `sigsetjmp-siglongjmp` | `sigsetjmp`/`siglongjmp` | - |
| `alternate-signal-stack` | Alternate signal stack | - |
| `crashguard` | CrashGuard | - |
| `fault` | Fault | - |
| `seh` | SEH | structured exception handling |
| `stack-guarantee` | Stack guarantee | - |
| `watchdog` | Watchdog | - |
