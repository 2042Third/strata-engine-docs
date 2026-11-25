# Notes: `basics/cpp-modern`

## New terms

- variant: a type that holds exactly one of several listed types at a time and knows which (`std::variant`); home
  `basics/cpp-modern`; alias `std::variant`.
- forwarding reference: a parameter written `Args&&...` in a template, which binds to both temporaries and named objects
  and remembers which; passing it on with `std::forward` is perfect forwarding; home `basics/cpp-modern`.
- structured binding: a declaration such as `const auto [end, error] = ...` that splits a pair or struct into named
  variables; home `basics/cpp-modern`.
- incomplete type: a class that is declared (`class Scene;`) but not yet defined; home `basics/cpp-modern`.
- type trait: a template in `<type_traits>` that answers a question about a type at compile time (`std::is_same_v`);
  home `basics/cpp-modern`.

## Requests

- `tools/data/extra-words.txt` or the glossary: `unwinding` is written in code, not proposed as a word.
- Sketches: fifteen files `sketches/basics-cpp-modern-*.cpp` (move, forward, optional, variant, span, flags, constexpr,
  macros, exceptions, path for the body; vectors, firsteven, visit, levels, coins for the Practice). All compile with
  `-std=c++20 -Wall -Wextra` and their output is filled in.
- Figures: none. The page has no picture and no figure manifest.

## Not verified

- `ST_DIST` and the `ST_WITH_` options in `names`: they are compile definitions that CMake passes
  (`CMake/StrataCompilerOptions.cmake:103`, `Strata/CMakeLists.txt:26-29`), not `#define` lines, so the names check
  finds no definition. They were read in the CMake files at the pin.
- Standard-library statements that are not about Strata (a vector is three pointers, a moved-from `std::vector` is empty,
  `std::span` needs a complete element type, short strings live inside the string) come from the C++ standard and
  common implementations, not from the pin.
- The Coin Run item: the page gives a standalone program with its own `Coin` struct. The names of the scripts and
  entities of `make/project-coin-run` at the pin were not read, so the exercise names none.
- Links to pages not written yet: `basics/build`, `core/conventions`, `core/files`, `world/reflection`,
  `scripting/abi-sdk`, `engineering/flags-portability`, `make/project-coin-run`.

## Findings not applied

- critic-basics-a-12: not applied to this page. It asks `basics/programming-3` for a table of SDK words; the page
  teaches `std::string_view`, `constexpr` and the callback copy (a view that must be kept is copied into a
  `std::string`) in the sections on views and constexpr, so `basics/programming-3` can link them.
- critic-basics-a-16: applied for this page: structured bindings (with `auto`), `mutable`, `reinterpret_cast`,
  `std::memcpy` and `std::bit_cast`. Not applied: `std::numeric_limits` (`basics/numbers`) and `std::chrono`
  (`basics/cpp-generic`), which name other pages. `static_cast` is taught here, as the finding says, and
  `basics/cpp-generic` should say where.
- Concepts and `requires`: the brief asks for them "in the measure Strata's code uses them". At the pin Strata defines
  none (`rg "concept"` and `rg "requires"` over `Strata/src` find only comments and strings), so the page teaches the
  syntax in one `pseudocode` example and says so.
- `std::visit` with `std::variant` for values (`world/reflection`) and the macros of the script SDK
  (`scripting/abi-sdk`): only named, as the brief's "Leaves out" says.

## Clerk

- Admitted: Variant (basics) (the glossary's variant is homed on `gpu/shaders`; alias `std::variant` left out: code), forwarding reference, structured binding, incomplete type, type trait.
- `ST_WITH_` (the start of the module switches): `tools/names.py` now accepts a name ending in "_" that starts macros of the pin, and the macros table holds CMake's compile definitions (ST_DIST, ST_WITH_AUDIO).

## Track walk E-final-2

Each sketch of the page compiled warning-free with `cl /std:c++20 /EHsc /W3` (Visual Studio 2026, 19.50, x64) and with g++ 15 `-std=c++20`; both printed the same output (`docs-work/walkfix-E2/cl/`, 2026-11-24, 60 sketches of the four C++ pages).

Up-to-date builds (WK10): reproduced with the official 0.8.0 package, headless, under the perf lock (`docs-work/walkfix-E2/session.ps1`, `session.out`): of the walker's 18 exercise files, written with verified bytes, one (`g1bad`, which cannot compile) built `success`, `moduleChanged: false`, and the Console line ends `Script build 12 finished in 0.6 s (the module was up to date)`. The work folders lie on G:, an exFAT drive, which stores file times rounded to 2 seconds (18:39:37.456 reads back 18:39:38.000; NTFS keeps 18:39:37.456), so a file saved within about 2 seconds of the last build's object file is no newer than it, and MSBuild skips it. Not an engine fault: the build's file-time rule (basics/build) on a coarse file system. The Practice intro says what the reader sees and does.

WK5: the learn line with `#if` was unquoted YAML, so ` #if ...` was read as a comment and the line ended at "an"; it is now quoted. Same pattern on `editor-ui/imgui` ("the suffixes ## and ###"), reported, not changed here.

Exercise 5 names its start: your Coin Run or Checkpoint 4 of Ship the finished game. Not run as a script.
