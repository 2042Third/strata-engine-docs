# Brief: `basics/threads`

| Field | Value |
| --- | --- |
| Title | Threads, atomics and races |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/computer`, `basics/cpp-generic` |
| From | new; foundation concept 16; home of threads, races, mutexes, atomics and memory order in general (Strata's job system is `core/jobs`') |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `atomic-operation` | atomic operation | atomic |
| `condition-variable` | condition variable | - |
| `data-race` | data race | - |
| `deadlock` | deadlock | - |
| `job` | job | - |
| `lock` | lock | - |
| `lock-free` | lock-free | - |
| `main-thread` | main thread | - |
| `memory-order` | memory order | memory ordering |
| `mutex` | mutex | mutual exclusion |
| `parallelism` | parallelism | - |
| `race-condition` | race condition | race |
| `thread` | thread | - |
| `thread-pool` | thread pool | - |
| `thread-local` | Thread-local | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-3 | must | missing-item | `basics/threads` (`new:222`, `new:204`) | The Practice starts threads inside the editor's process, but no row says what happens when such a thread goes wrong. Crash containment guards only the thread on which the engine calls the script: a fault on a thread the script started, an exception that leaves the thread's function, or a `std::thread` destroyed before `join` ends the whole editor with its unsaved work, on every system. A deadlock that the callback joins hangs the editor. And SDK calls from such a thread do nothing and report "scripts can only use the engine from the main thread" (only `Log` works there), so the true answer of the Coin Run item, a script thread that moves the ball, is that the ball does not move and the engine reports it. | The Practice opens with the rule and its reasons: save first; join every thread before the callback returns; catch exceptions inside the thread's function. The deadlock stays drawn on paper, or uses `try_lock_for` with a timeout. The Common mistakes hold the three ways a script's thread ends the editor, and the Coin Run item's worked answer states what the pin does (about 200 words). | `allocation/basics-a.md:1244-1249`, `:1278-1279`; `Strata/src/Strata/Core/CrashGuard.h:35-55`; `StrataScriptCore/Include/StrataScript/Script.h:184-203`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:67-78`, `:99-126`, `:284-298` |
| critic-basics-a-15 | should | other | `basics/threads` (`new:222`) | The first exercise predicts lost counts when two threads each add one to a plain `int` a million times. The editor builds scripts in its own configuration, Dist for the downloaded Strata, with the optimizer on, and an optimizer may turn such a loop (no call, no atomic) into one addition of a million; the two threads then rarely overlap, the total comes out right, and the exercise teaches that the code is safe. The claim rests on how compilers optimize, and a run settles it. | Show the lost counts with a race that the optimizer keeps and that is no undefined behavior: a `std::atomic<int>` read and written in two steps (`counter.store(counter.load() + 1)`), a race condition beside the data race; the plain `int` stays as the case the page explains (about 80 words). Hold the claim as a check before writing (see forPlanner). | `allocation/basics-a.md:1233-1234`, `:1279`; `.github/workflows/release.yml:149`, `:182`; `StrataEditor/CMakeLists.txt:39`; `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:37-52` |
| critic-basics-a-16 | should | missing-item | `basics/cpp-modern`, `basics/numbers`, `basics/cpp-generic` | A sweep of `Strata/src` finds C++ that track E's internals pages will quote and that no primer lists: `std::chrono` (348 lines in 70 files), structured bindings such as `auto [end, error]` (240 lines in 65 files), `reinterpret_cast` (103 in 47), `std::numeric_limits` (72 in 41) and `mutable` (65 in 28, mostly a mutex in a class with `const` member functions). `basics/threads`' practice times a mutex against an atomic, which needs a clock. And `static_cast` is used on `basics/cpp-generic` but taught on `basics/cpp-modern`, the next page. | `basics/cpp-modern` takes structured bindings, `mutable` and the casts (`reinterpret_cast`, and why a number is read from bytes through `std::memcpy` or `std::bit_cast`); `basics/numbers` takes `std::numeric_limits` beside the ranges; `basics/cpp-generic` takes `std::chrono::steady_clock` with durations, and `static_cast` where it first uses it (about 450 words over the three pages). | `grep -rnE` over `Strata/src` at the pin, counts as given; `Strata/src/Strata/Core/Application.cpp:28`; `Strata/src/Strata/Core/CommandLine.cpp:59`; `Strata/src/Strata/Core/BinaryStream.h:24`; `Strata/src/Strata/Core/BoundedRead.cpp:15`; `Strata/src/Strata/Core/BackgroundLogSink.h:74`; a search of `allocation/*.md` for `std::chrono`, `steady_clock`, `reinterpret_cast`, `numeric_limits` and "structured binding" finds nothing; `allocation/basics-a.md:879`, `:943`, `:1279` |
