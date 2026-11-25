# Brief: `core/jobs`

| Field | Value |
| --- | --- |
| Title | Threads and the job system |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/frame-loop`, `basics/threads` |
| From | foundation "Threads and the job system" (§1.6); home of the threading model and the threads of a process (foundation figure 12) and of "parallel work is deterministic" (ordered records, fixed chunks, serial publish); threads in general are `basics/threads`' |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/jobs` — Threads and the job system

**Covers.** The job: how Strata runs work on other threads without making the frame wait for what it does not need, and
who owns what across threads. The problem in the part's full section on it: job systems (thread pools, task graphs, work
stealing and fibers, priorities, pools for blocking reads) and the threading model of an engine (one thread owns the
world's changing state, or every system runs in parallel; results handed back through queues and polling, never through
callbacks). The map: the three pools and who submits to which, then the threads of the editor's process and their
hand-offs into the main thread. The contract: the pools (workers, one fewer than the hardware threads, at normal
priority; two I/O threads; background threads below normal priority, which leave four hardware threads to the frame);
`Submit`, `SubmitIO`, `SubmitBackgroundPart` and `JobPriority` (High, Normal, Low, Background; work started from
background stays background); `JobHandle`, `Wait` and `WaitAll` (whoever claims a job first runs it, by an atomic
exchange; a waiter runs the job it waits for when no thread has started it, and never another job, so waiting inside a
job cannot deadlock); `ParallelFor` (an atomic counter of batches, the caller takes batches too, helpers that have not
started are dropped once every batch is taken, shared state keeps it alive); jobs that run on the caller before `Init`
and after `Shutdown`; a `try` and `catch` around every job and batch; `GetStats` and `ThreadActivity`, read without
stopping the pool; `SequenceLockedValue<T>`, one writer and one reader that never wait (the audio thread's hand-off).
The rules with their reasons: the main thread owns the scene, input, scripts and rendering submission, and workers hand
results back; never block a frame on long work, and never let a waiter run other jobs; the main thread's frame work
touches no file, because a blocking read stalls the frame, so reads go to the I/O pool and their results come back by
polling (`core/files` shows the counter that tests prove it with); long work at `JobPriority::Background` (the measured
stalls: frames of about 3 ms stretched to 10-30 ms while an import compressed textures); what a job captures is released
where it runs (libc++ copies small callables when they are moved). Then deterministic parallel work, as its home: jobs
write only their own records, the main thread publishes them in order afterwards, and the result does not depend on the
number of threads (the design decision's `:::why`, with the places that keep it: animation, physics and the scene's
parallel writer). What Strata does not do: work stealing, fibers and a task graph of the frame. The toy is a pool with
one queue and a `Wait` that runs the job itself, in 60 lines; the real code is the claim and the wait, the pool's
thread, `ParallelFor`, the emptied `std::function` and the sequence lock. The exercises: `ParallelFor` at batch sizes 1,
64 and 4096, measured with the workers' busy share; a job that waits on a job, traced with breakpoints into `Wait` and
`TryRunJob`, and why it cannot deadlock; the captured last `Ref`; a hand-off through `SequenceLockedValue`. At the end
the reader can put work on the right pool, wait for it safely, and keep its result the same on any number of threads.

**Leaves out.**

- Threads, races, mutexes, atomics and memory order in general → `basics/threads`
- Thread priorities and how each OS sets them → `core/platform`
- The deterministic step of physics in detail → `physics/world-step`
- The animation system's ordered publish → `animation/system`
- The parallel writer's identical bytes → `world/serialization`
- The audio thread and its mixer → `audio/engine`
- The RPC server's thread → `automation/rpc-server`
- The profiler's view of the pools → `core/profiling`

**Fit.** `fits`: about 5,950 words against L (5,000). The pools, the wait and `ParallelFor`, with five quotes and four
figures, take the most, then the threading model and deterministic parallel work; four exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:288` | concept | home | Job systems: pools, task graphs, work stealing, fibers, priorities, pools for blocking reads; Strata's three pools and why; the mistakes (a job that waits and deadlocks a naive pool, a waiter that picks up long jobs, a moved `std::function` that is not empty) |
| `foundation:296` | concept | home | The threading model of an engine: one owner of the world's state, or full parallelism; hand-offs through queues and polling; Strata's table of producers and consumers |
| `new:13` | concept | home | Deterministic parallel work: jobs write only their own records, the main thread publishes them in order, and runs with different numbers of threads agree bit for bit; the design decision's `:::why`. Evidence: `AGENTS.md:308-309`; `Docs/DeveloperGuide.md:2209-2212` |
| `foundation:103` | feature | home | The three pools, workers, I/O and background, their sizes and priorities |
| `foundation:104` | feature | home | `Submit`, `SubmitIO`, `SubmitBackgroundPart` and `JobPriority` |
| `foundation:105` | feature | home | `JobHandle`, `Wait` and `WaitAll`: the claim by exchange, no deadlock, never another job |
| `foundation:106` | feature | home | `ParallelFor` |
| `foundation:107` | feature | home | Jobs run on the caller before `Init` and after `Shutdown` |
| `foundation:108` | feature | home | A `try` and `catch` around every job and batch |
| `foundation:109` | feature | home | `GetStats` and `ThreadActivity`, read without stopping the pool |
| `foundation:110` | feature | home | `SequenceLockedValue<T>`, the hand-off of one writer to one reader |
| `foundation:113` | feature | home | The threading model: what the main thread owns, and the hand-offs |
| `foundation:357` | code | home | `Strata/src/Strata/Core/JobSystem.cpp:33-81`: `ExecuteJob`, `TryRunJob` and `DropJob`, whoever claims first runs the job; with `JobSystem.cpp:502-514`, `Wait` |
| `foundation:358` | code | home | `Strata/src/Strata/Core/JobSystem.cpp:165-313`: `JobPool`, a pool with queues by priority and a shutdown that drains them (`ThreadMain` at 274-304) |
| `foundation:359` | code | home | `Strata/src/Strata/Core/JobSystem.cpp:357-401`: `ParallelFor`'s shared batches; with `JobSystem.cpp:522-566`, the caller's part and the dropped helpers |
| `foundation:360` | code | home | `Strata/src/Strata/Core/JobSystem.cpp:335-342`: a `std::function` emptied after the move, so that captures die where the job runs; with `JobSystem.cpp:460-474`, `Submit` |
| `foundation:361` | code | home | `Strata/src/Strata/Core/SequenceLock.h:13-66`: the sequence lock (odd while writing, fences, retry); `ThreadActivity` in `JobSystem.cpp` 88-163 is the same idea inside the pool |
| `foundation:408` | figure | home | The job system: three pools with their queues, who submits to which, the threads' priorities, the four hardware threads left to the frame |
| `foundation:410` | figure | home | A job's states: queued, claimed by a pool thread or by a waiter, completed; dropped for `ParallelFor`'s helpers |
| `foundation:412` | figure | home | `ParallelFor`: batches, the atomic next batch, the caller and its helpers taking batches, helpers dropped, the wait for the finished count |
| `foundation:414` | figure | home | The threads of the editor's process and their hand-offs into the main thread's polled queues |
| `foundation:447` | rule | home | The main thread owns the scene, input, scripts and rendering submission; workers hand results back through queues or `SubmitToMainThread` |
| `foundation:450` | rule | home | Never block a frame on a job that may run long, and never let a waiting thread run other jobs |
| `new:29` | rule | home | The main thread's frame work does no file I/O: a blocking read there stalls the frame, so reads go to the I/O pool (`SubmitIO`) and their results come back by polling or `SubmitToMainThread`; stated with `foundation:450` (about 60 words); `core/files` keeps the per-thread operation counter as the proof tests use. Evidence: `AGENTS.md:188-190`; `AGENTS.md:353` (saves never serialize on the main thread); `Docs/DeveloperGuide.md:1698` (registering and applying touch no file on the main thread); `Strata/src/Strata/Core/FileSystem.h:70-74`; `StrataTests/src/Asset/AssetRegistrationTests.cpp:123-125`; `Strata/src/Strata/Core/JobSystem.h:113` |
| `foundation:452` | rule | home | Long work goes to `JobPriority::Background`; frame work stays on workers of normal priority |
| `foundation:454` | rule | home | What a job captures is released where it runs |
| `foundation:520` | hands-on | home | A loop through `ParallelFor` at batch sizes 1, 64 and 4096, measured with the workers' busy share |
| `foundation:521` | hands-on | home | Trace it yourself, the page's trace exercise: a test whose job waits on another job, followed with breakpoints into `JobSystem::Wait` (`Strata/src/Strata/Core/JobSystem.cpp:502-514`) and `TryRunJob` (`:60-67`), where the waiter claims the job that no thread has started by an atomic exchange and runs it; the reason it cannot deadlock |
| `foundation:522` | hands-on | home | The captured last reference: a job holding the last `Ref` of an object whose destructor records its thread |
| `foundation:523` | hands-on | home | A lock-free hand-off with `SequenceLockedValue<T>` between a thread and the main loop |
| `foundation:590` | term | home | Thread pool |
| `foundation:591` | term | home | Two entries: job and job handle |
| `foundation:592` | term | home | Three entries: worker thread, I/O thread and background thread |
| `foundation:593` | term | home | ParallelFor |
| `foundation:594` | term | home | Batch, a slice of a `ParallelFor`'s range (the other meaning, batching draws, is `draw/batching`'s) |
| `foundation:595` | term | home | Claim |
| `foundation:600` | term | home | Sequence lock |
| `audio-input:633` | term | home | Sequence lock, one entry with `foundation:600` (a writer bumps a counter around a write, readers retry if it changed), passed by `audio-input` (R31, "The sequence lock"); the excerpt `SequenceLock.h` stays here, and `audio/engine` quotes only its use |
| `new:12` | not-done | home | No work stealing, no fibers and no task graph of the frame: three pools with central queues. Evidence: `Docs/Roadmap.md:1704-1705` lists "JobSystem v2 with work stealing and a frame task graph" under "Further"; `git grep -ni fiber 822a7a46 -- Strata/src` finds nothing; `git grep -ni steal 822a7a46 -- Strata/src` finds only voice stealing (`Strata/src/Strata/Audio/AudioEngine.cpp:147`, `Strata/src/Strata/Audio/AudioSystem.cpp:895`) |
| `foundation:284` | concept | link | Threads and synchronization in general, `basics/threads`' |
| `foundation:596`, `foundation:597`, `foundation:598`, `foundation:599`, `foundation:601` | term | link | Deadlock, data race, mutex and condition variable, atomics and memory order, thread-local, whose entries are `basics/threads`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Threads, races, mutexes, condition variables, atomics and memory order | `basics/threads` | must |
| `std::function`, lambdas and captures | `basics/cpp-generic` | must |
| Move semantics | `basics/cpp-modern` | must |
| `shared_ptr` and shared state | `basics/cpp-memory` | must |
| Queues and priority queues | `basics/trees-graphs` | must |
| The frame loop and `SubmitToMainThread` | `core/frame-loop` | must |
| Writing and running one test case | `core/first-change` | must |
| Processor cores and hardware threads | `basics/computer` | helps |
| Thread priorities | `core/platform` | helps |
| The frame profiler's busy shares, for the first exercise | `core/profiling` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `batch-core` | Batch (core) | - |
| `claim` | Claim | - |
| `job-handle` | job handle | - |
| `parallelfor` | ParallelFor | - |
| `sequence-lock` | Sequence lock | - |
