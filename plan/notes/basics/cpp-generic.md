# Notes: `basics/cpp-generic`

## New terms

All are defined once in bold on the page; this page is the home of each.

- type argument: an argument of a template that is a type, as the `float` of `Row<float, 3>`.
- node handle: the object `extract` returns, which owns one node of a map and lets you change its key before `insert`.
- invalid iterator (alias: iterator made invalid): an iterator that points at a place that no longer holds what it did.
- function pointer: the address of a plain function, the C form of a callback.
- user pointer (alias: user data): a `void*` that a C library stores and passes back to the callback.
- configuration struct: a plain struct a C library takes its settings in, completed by the caller and passed by pointer.
- result code: a number a C library returns to name success or the kind of failure.
- pointer to a member: a value of type `float Coin::*` that names a field of a class, not of one object.

## Requests

- `tools/external-hosts.txt`: none. Learn C++ (learncpp.com) is cited in Further reading without a link; its chapter numbers (11, 16, 18, 20, 26) are given from memory of the site's layout.
- Figures: none requested. The page has one Mermaid diagram (a template and the two functions the compiler writes from it) and no figure manifest.
- Sketches: 15 files `sketches/basics-cpp-generic-*.cpp` (10 for the text, 5 for the Practice). All compile with the sketch check and their output is filled in.

## Not verified

- The Coin Run item: that the reader's coins carry the tag `Coin` and that the ball is an entity the script finds. `Scene::FindEntitiesByTag` (returns `std::vector<Entity>`, `Scene.h:123`) and `GetTransform().GetWorldPosition()` are in the SDK at the pin; the project state itself is `make/project-coin-run`'s.
- That `spdlog`'s `{}` takes the next value in `ST_CORE_INFO("Loaded {}", path)`: the macro forwards to the logger (`Strata/src/Strata/Core/Log.h`) and the engine guide says messages are fmt-formatted; the vendored library was not read.
- General C++ facts that are not about Strata: growth of a full `std::vector`, which iterators each container's insert and erase invalidate, that an empty `std::function` fails when called, that a `std::function` may allocate for a large capture, and `sizeof(Row<float, 3>)` of 12 and `sizeof(Row<double, 3>)` of 24 (the sketch's output on one platform).
- The window code's use of the user pointer is shown for `glfwSetWindowSizeCallback` only; the other callbacks of that function were not read in full.
- Links to pages not written yet: `basics/cpp-modern`, `basics/threads`, `scripting/abi-sdk`, `world/ecs`, `make/project-coin-run`, `basics/programming-3`, `basics/data-structures`, `basics/trees-graphs`.

## Findings not applied

- critic-basics-a-16: applied for this page. `std::chrono::steady_clock` with durations is a note in the algorithms section (clock, time point, `duration_cast`, and the deadline code of `PosixProcess.cpp`), and `static_cast` is explained where the page first uses it, in the C callbacks section. Not applied here, by the finding's own split: structured bindings, `mutable` and `reinterpret_cast` (`basics/cpp-modern`) and `std::numeric_limits` (`basics/numbers`).
- Brief items left to other pages, as its "Leaves out" says: move semantics, `if constexpr`, `std::variant`, concepts (`basics/cpp-modern`). The page shows `std::move` once, in the node handle sketch, with a question that links `basics/cpp-modern`.

## Clerk

- Admitted: type argument, node handle, function pointer, user pointer (alias user data), configuration struct, pointer to a member.
- Not admitted, because the page check would then fail and the page is the writer's: invalid-iterator (the page bolds only "invalid", so term-defined would fail); result-code (its paragraph would define 2 terms with configuration struct (term-paragraph)). The part's reviewer splits the paragraph or section or bolds the term; the next clerk admits it then.

## Track walk E-final-2

Each sketch of the page compiled warning-free with `cl /std:c++20 /EHsc /W3` (Visual Studio 2026, 19.50, x64) and with g++ 15 `-std=c++20`; both printed the same output (`docs-work/walkfix-E2/cl/`, 2026-11-24, 60 sketches of the four C++ pages).

Up-to-date builds (WK10): reproduced with the official 0.8.0 package, headless, under the perf lock (`docs-work/walkfix-E2/session.ps1`, `session.out`): of the walker's 18 exercise files, written with verified bytes, one (`g1bad`, which cannot compile) built `success`, `moduleChanged: false`, and the Console line ends `Script build 12 finished in 0.6 s (the module was up to date)`. The work folders lie on G:, an exFAT drive, which stores file times rounded to 2 seconds (18:39:37.456 reads back 18:39:38.000; NTFS keeps 18:39:37.456), so a file saved within about 2 seconds of the last build's object file is no newer than it, and MSBuild skips it. Not an engine fault: the build's file-time rule (basics/build) on a coarse file system. The Practice intro says what the reader sees and does.

Exercise 5 names its start: your Coin Run or Checkpoint 4 of Ship the finished game. Read against that checkpoint (`public/downloads/tutorials/make/project-coin-run/stage-4.zip`): the coins carry the tag `Coin` (`Scripts/CoinHud.cpp`, `CoinRunGame.cpp` count them so) and are placed by `CoinPlacer` once play starts; the ball is `Ball` (`Scripts/Coin.cpp`). Not run as a script.
