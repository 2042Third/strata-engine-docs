# Notes: `basics/cpp-memory`

## New terms

None proposed. The page defines in bold the 13 terms the brief lists (dereference, lifetime, dynamic allocation, memory leak, dangling pointer, undefined behavior, destructor, RAII, ownership, smart pointer, unique pointer, shared pointer, allocator). It uses "weak pointer", "arena", "pool" and "free list" as plain words without a bold definition.

## Requests

- `tools/external-hosts.txt`: `learncpp.com`. Further reading cites "Learn C++" without a link until the host is allowed.
- Figures: none requested. The page has two Mermaid diagrams (three whole numbers in memory with a pointer; a decision path for the kind of pointer) and no figure manifest.
- Sketches: fifteen files `sketches/basics-cpp-memory-*.cpp` (pointers, references, lifetimes, order, guard, unique, shared, weak, cycle, arena, pool and exercise-order, -move, -count, -arena), each at most 25 lines, all compiled with the sketch check and their output filled in.

## Not verified

- The text of the compiler error for copying a `std::unique_ptr`: the page says "a use of a deleted function" in general terms and quotes no message.
- Sizes 8 and 16 of the unique and shared pointer: printed by `basics-cpp-memory-shared.cpp` on the book's 64-bit compiler; "often 1 to 8 MB" for a stack and the 100 ns heap request (marked as an assumption) are general knowledge, not at the pin.
- Why `Base.h` names the three smart pointers: the file states no reason, so the `:::why` box gives only the visible effects (no run-time cost, the job in the name).
- Coin Run, exercise 5: the end state of `make/project-coin-run`, the `Coin` script and how a script finds the coin's entity are not at the pin. That `GetScript` returns `nullptr` for a destroyed entity follows from the comment of `Entity` ("every operation on an entity that no longer exists is a harmless no-op that returns an empty result") and from `Entity::GetScript`'s code (null when the host returns no instance); `ScriptHostAPI.cpp` was not traced.
- That `GeometryPool` uses `RangeAllocator` to place geometry in its buffers: `GeometryPool.h` includes it and holds `RangeAllocator Allocator` members; the use was not traced further.
- Links to pages not written yet: `basics/computer`, `basics/numbers`, `basics/bytes`, `basics/cpp-classes`, `basics/cpp-generic`, `basics/cpp-modern`, `basics/threads`, `basics/debugging`, `core/conventions`, `assets/residency`, `gpu/geometry-pool`, `gpu/resources-lifetimes`.
- The sketch check of the whole book fails for sketches of other pages (`basics-build-Greeting`, `basics-build-main`, `basics-bytes-bounds`); none is this page's.

## Findings not applied

- critic-basics-a-20: applied. The allocator section teaches alignment (the round-up `(used + align - 1) / align * align`, the aligned buffer start), `std::construct_at` and `std::destroy_at` in Exercise 4's sketch, and links `basics/numbers` (round-up rule) and `basics/bytes` (layouts and padding).
- The brief's item `foundation:353` names `Base.h` lines 40-61; at the pin the aliases are lines 42-61 (the namespace opens on 39), and the page quotes those.
- The 55 `passive` and 3 `noun-stack` warnings are left: they are states of objects ("the local is gone", "the object is deleted") where naming the actor would be false or awkward.

## Clerk

- Nothing new: `learncpp.com` is on `external-hosts.txt` already.

## Track walk E-final-2

Each sketch of the page compiled warning-free with `cl /std:c++20 /EHsc /W3` (Visual Studio 2026, 19.50, x64) and with g++ 15 `-std=c++20`; both printed the same output (`docs-work/walkfix-E2/cl/`, 2026-11-24, 60 sketches of the four C++ pages).

Up-to-date builds (WK10): reproduced with the official 0.8.0 package, headless, under the perf lock (`docs-work/walkfix-E2/session.ps1`, `session.out`): of the walker's 18 exercise files, written with verified bytes, one (`g1bad`, which cannot compile) built `success`, `moduleChanged: false`, and the Console line ends `Script build 12 finished in 0.6 s (the module was up to date)`. The work folders lie on G:, an exFAT drive, which stores file times rounded to 2 seconds (18:39:37.456 reads back 18:39:38.000; NTFS keeps 18:39:37.456), so a file saved within about 2 seconds of the last build's object file is no newer than it, and MSBuild skips it. Not an engine fault: the build's file-time rule (basics/build) on a coarse file system. The Practice intro says what the reader sees and does.

Exercise 5 now runs in `Playground` (track E never makes Coin Run, and its coins exist only in play). Run as a script with the package: the bug version logged `frame 58, marker: Marker` to frame 60, then the warning `GetEntityName (called by script 'Playground' on entity 'Playground'): entity FA0D88BAFB96FE56 does not exist` and empty names in frames 61 and 62; the fix logged `gone` there (`variants/hm.cpp`, `hmfix.cpp`). The hot reload paragraph follows `StrataScriptCore/include/StrataScript/Script.h:49-52` (non-field state starts over, `OnReload` instead of `OnCreate`); the earlier answer said the kept pointer dangles after a reload, but the new instance's pointer starts as `nullptr`.

WK4: the answer "512. The pointer ..." was parsed as an ordered list that starts at 512, so the number vanished from the text; the answer now starts with words. Same pattern elsewhere (reported, not changed here): data-formats:781, threads:28, programming-2:318, 763, 776, programming-3:29, 309, draw/skinned:397.
