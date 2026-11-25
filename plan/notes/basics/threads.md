# Notes: `basics/threads`

## New terms

All glossary terms of the brief are defined once in bold on the page; this page is the home of each. One more:

- fence (alias: memory fence): a call such as `std::atomic_thread_fence` that orders the reads and writes around it, in the direction of release or acquire, without an operation on a variable.

## Requests

- `tools/data/extra-words.txt`: "predicate" (15 uses: the C++ name of the test passed to `wait`, `wait_until` and `wait_for`) and "spurious" (once, in "spurious wake-up", the standard's name). Both are the exact terms a reader meets in the standard library's documentation.
- `tools/external-hosts.txt`: `preshing.com` (Jeff Preshing's articles on lock-free programming and acquire and release); it is cited in Further reading without a link. Learn C++ (learncpp.com) is cited without a link, as on the other pages.
- Figures: none requested. The page has two Mermaid diagrams (two threads that lose a count; two locks taken in two orders) and no figure manifest.
- Sketches: 14 files `sketches/basics-threads-*.cpp` (10 for the text, 3 for the Practice, 1 shared by both: `timed`, `cure` and `handover` are the Practice's; the others are the text's). All compile with the sketch check and their output is filled in. Their output never changes between runs: they print booleans or sums, and the one real race (`race`) prints only whether counts were lost.
- Back link: `basics/cpp-generic` should teach `std::chrono::steady_clock` and durations (critic-basics-a-16); until it does, Practice 2 shows the clock only in its worked solution.

## Not verified

- The measurements on the page (about 1.1 million with `-O0` and exactly 2,000,000 with `-O2` for a plain `int`; 1.2 to 1.8 million for the load-then-store atomic; about 9 ns for a locked call against about 3.5 ns for `fetch_add`; about 50 ms against about 18 ms for 2,000,000 additions on two threads) were measured with MSYS2 g++ 15.2 on the author's machine, not with the engine's or the editor's compiler (MSVC, Clang). That the `-O2` plain-`int` total is exact because the compiler removed the loop is inferred from the run time (a fraction of a millisecond), not read from the assembly.
- Critic-basics-a-3: that a fault, an escaping exception or a `std::thread` destroyed before `join` on a thread a script started ends the editor on every system is inferred from `Strata/src/Strata/Core/CrashGuard.h` ("Guards may be nested and are per thread"; the guard is entered by `Invoke` on the calling thread) and from the C++ rule that these cases call `std::terminate`; no program was run. That a deadlock the callback joins freezes the editor follows from `ScriptWatchdog`, which only logs ("the main thread stays blocked until it returns").
- That only `Log` works from a script's own thread: `HostLog` in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` does not call `ResolveContext`; the other host functions were not all read, so the page says "engine calls check their thread" and names `Log` as the one that works.
- That a late audio buffer is audible as a click, the reason the page gives for the audio thread never waiting, is general knowledge; `SequenceLock.h` says only that the value is handed "to a real-time audio thread" and that neither side waits.
- That `std::scoped_lock` with several mutexes cannot deadlock is the C++ standard's deadlock-avoidance guarantee, not read from the engine.
- Links to pages not written yet: `core/jobs`, `audio/engine`, `core/frame-loop` (exists), `gpu/how-a-gpu-frame-works`, `assets/loading`, `basics/data-structures`, `basics/cpp-memory`, `basics/programming-1`.
- The Coin Run item: that the ball is an entity a script moves and that all Coin Run callbacks run on the main thread (`ScriptHostAPI.cpp`: `s_OwnerThread`, set when a scene starts to play).

## Findings not applied

- critic-basics-a-3: applied (Practice opening, Common mistakes, the Coin Run answer). The deadlock stays on paper in Practice 3.
- critic-basics-a-15: applied: the race is shown with a load-then-store atomic, and the plain `int` is explained with the measured `-O0` and `-O2` totals. Practice 1 asks for both variants.
- critic-basics-a-16: names other pages; this page only uses `std::chrono::steady_clock` in Practice 2's solution (see Requests).

## Clerk

- Admitted: Fence (basics) (alias memory fence; the glossary's Fence is homed on `gpu/how-a-gpu-frame-works`).
- `extra-words.txt`: "predicate" (used without a bold definition), "spurious". `external-hosts.txt`: `preshing.com` (front page fetched).
- Left for the planner: the back link to `basics/cpp-generic` (steady_clock).

## Track walk E-final-4

Each sketch of the page compiled with `cl /std:c++20 /EHsc` (Visual Studio 2026, 19.50) and with g++ 15 `-std=c++20`, glm from the 0.8.0 package's `StrataScriptCore/ThirdParty/glm`; both printed the same output (`docs-work/walkfix-E4/cl/`, 2026-11-24). The exact Windows line of the page was run in PowerShell in a Visual Studio developer environment (`cmdtest/`).

Exercises 1 and 2 as a `Playground` script on Checkpoint 4 of `make/first-script`, with the official 0.8.0 package, headless, under the perf lock (`docs-work/walkfix-E4/session.ps1`, `Playground.cpp`, `session.out`): the build ran `--config Dist` (Release flags, MSVC). Five runs: plain `int` 1,275,176, 1,166,509, 1,428,447, 1,130,698, 1,179,559; load-then-store atomic 1,156,103, 1,168,687, 1,152,798, 1,101,195, 1,193,566. Three runs of the mutex and `fetch_add`: 2,000,000 each, 23.9 to 24.8 ms and 15.5 to 16.4 ms.
