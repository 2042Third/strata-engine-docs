# Notes: `core/jobs`

## New terms

- **thread pool**: a fixed set of threads that take pieces of work, called jobs, from a queue. Home: `core/jobs`.
  Aliases: thread pools, pool. (Defined in bold on the page; the brief's items `foundation:590` to `foundation:592`
  name it, "job", "worker thread", "I/O thread" and "background thread" as homed here, but the page's terms table
  lists only batch, claim, job handle, ParallelFor and sequence lock. "Job" and the three thread kinds are explained in
  plain words, not bolded.)
- **priorities** (job priorities): several queues in one pool, emptied in order, so that urgent work overtakes work
  that can wait. Home: `core/jobs`.
- **task graph**: a set of jobs in which each job names the jobs it needs first, so that the system runs every job
  whose inputs are done. Home: `core/jobs`.
- **work stealing**: a scheme in which each thread has a queue of its own and a thread without work takes jobs from
  another thread's queue. Home: `core/jobs`.
- **fibers**: light stacks that a program switches between by itself, without the operating system. Home: `core/jobs`.

The page also defines the glossary's own entries homed here: batch (core), claim, job handle, ParallelFor, sequence
lock; and "main thread" (homed at `core/frame-loop`) in one sentence of the problem section.

## Requests

- `tools/data/names.txt`: Rayon (a Rust library named in the table of alternatives). Its word-list finding is left until
  then. "oneTBB" and "Naughty Dog" pass already; the Further reading entries are not read.
- No external host is needed: Further reading cites books, a talk and a library's documentation without links.

## Since

`since: 0.3.0`. `JobSystem.h` and `JobSystem.cpp` exist since the first commit (`a0f2865f`, "Add build system, pinned
dependencies and engine core"), which `v0.3.0` contains. Later changes the page describes: `bc5394b2` (its title says workers below the
main thread's priority; at the pin they run at the normal priority), `63a5b5cb` ("Release what a job captures on the thread
that runs it"), `e57138c5` ("Leave four hardware threads to the frame when background work runs") and `e2671835`
("Queue a scene read's chunks ahead of imports waiting to start", `SubmitBackgroundPart`). `SequenceLock.h` came with
`42577b40` ("Factor the listener's sequence lock out and test it across threads").

## Not verified

- Work stealing in Intel's oneTBB and in the Rayon library, and the task graph of Unreal Engine (table of
  alternatives): written from general knowledge; no source was opened.
- Naughty Dog's fibers: that the talk is "Parallelizing the Naughty Dog Engine Using Fibers" by Christian Gyrling at
  GDC 2015 comes from the brief's wording and general knowledge; the talk was not opened.
- The other books and the documentation in Further reading (Gregory, Williams, oneTBB): chapter names and levels come
  from general knowledge.
- The measured frame times (3 ms stretched to 10 to 30 ms, 5 to 27 ms, 2.0 to 2.8 ms, a million entities in 7 s instead
  of 1.3 s) come from comments in `Strata/src/Strata/Core/JobSystem.h` and from `Docs/Architecture.md` at the pin, not
  from a run.
- The hand-offs named in the second diagram (completion queue, change queue, request queue) are the classes and
  methods `AssetManagerBase::PushCompletion`, `FileWatcher::PollChanges` and `RpcServer::ProcessRequests`, found in the
  headers; their consumers in the editor's `Update` calls come from `Docs/Architecture.md`, not from the code.
- The three sketches compile warning-free here with the MSYS2 g++ with -Wall -Wextra; the toy's run of the "waiting thread runs the job"
  case depends on the pool's thread being busy in a spinning job, which the program makes certain with a flag.
- Exercise 2 (trace it yourself) was not run with a debugger; its answer follows the code of `JobSystem::Wait` and
  `TryRunJob` and the test `Jobs may wait on other jobs without deadlocking`.
- The sizes in the table of defaults are computed from `JobSystem::GetDefaultBackgroundThreadCount`; the tests check the
  values for 4, 8, 16 and 24 hardware threads.

## Findings not applied

- The brief has no open findings at its end.
- Figures `foundation:410` (a job's states) and `foundation:412` (the flow of `ParallelFor`) are not drawn: the page
  teaches both in text, a worked example and callouts, and the size range left no room for two more diagrams.
  `foundation:408` (the pools) and `foundation:414` (the threads and their hand-offs) are Mermaid diagrams on the page.
- The brief's hands-on `foundation:520` (batch sizes 1, 64 and 4096 measured with the workers' busy share) is the
  page's Basic exercise as a computation of batches, last batch and helpers; no measurement was made, because the
  task forbids starting an engine program. The editor's Performance panel shows the share it would read.
- The toy is 135 lines, not 30 to 80: it holds the pool, the claim, `Wait` and both demonstrations (the one-worker case
  and the waiting thread that runs the job). `pagecheck` accepts it.

## Clerk

- Admitted: Priority (jobs) (alias priorities), task graph, work stealing, fiber (alias fibers).
- Refused: thread pool: homed on `basics/threads` (only its home words it); the page's bold use is a definition of a term homed elsewhere, the part reviewer's.
- `names.txt`: Rayon.

## Track walk E-final-6

- WK1, WK6: a paragraph after the introduction says that the page needs no project and no download and that its test
  commands and trace need the source build of Your first engine change; one sentence of How it is tested was cut to
  stay within size L.
