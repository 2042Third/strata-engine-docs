# Notes: `basics/programming-3`

## New terms

None proposed. The page defines in bold the 18 terms the brief lists: class, member function, object, constructor,
inheritance, base class, derived class, C++ reference, pointer, null pointer, optional value, template argument,
declaration, header file, source file, include directive, compile error and compile time.

## Requests

- No new hosts: the Further reading entries use `en.cppreference.com` and `learncpp.com`, both on the list.
- Figures: none requested; the page has no diagram and no figures file.
- Sketches: eight files `sketches/basics-programming-3-*.cpp` (purse, pickup, references, pointer, optional for the
  body; practice-reference, practice-counter, practice-coinrun for the Practice). All compile with the sketch check and
  their output is filled in. Each holds at most 25 lines, as a level-1 page requires.
- The sketches check also lists a failing sketch of another page (`sketches/basics-bytes-bounds.cpp`): not mine.

## Not verified

- The compiler messages in the text fences are real output of GCC 15.2 (MSYS2), made by compiling files of the work
  folder against a copy of the pin's `StrataScriptCore/Include`. The wording of MSVC is not quoted except the line
  `error C2065: 'speed': undeclared identifier`, which the engine's `ScriptBuildTests.cpp` holds. Since the answers to
  walk G-final-4 the MSVC rows of the `double` field error (C2338 `static assertion failed`, C2027, C2065, all in
  `Script.h`), the Console lines that name the script's file, and the five rows of Practice 4 come from builds with the
  official 0.8.0 package and Visual Studio 18 2026 (work folder `docs-work/walkfix-G4`, `out/` and `out2/`); the earlier
  wording `static_assert failed` was wrong.
- That the Problems panel's error rows have a red icon: `ProblemsPanel.cpp` uses the icons `CircleX` and `TriangleAlert`
  and the theme's error colour; the colour itself was not checked. The summary lines `Build N failed: E errors, W
  warnings.` and `Build N succeeded with W warnings.` and the double click that opens a file are from the code.
- That a null pointer read ends in the Problems panel as the page says: taken from the panel's code (it leads with the
  crash) and the inventory (`editor-ui:149`), not from a run.
- That a new file in `Scripts` joins the module at the next build with no step of the reader's: the CMake module globs
  with `CONFIGURE_DEPENDS`; how the editor re-configures was not traced.
- The component name `PointLight` and its `Intensity` property are from `RendererComponents.cpp`; the label of the
  Inspector's add-component entry is not named on the page for that reason.
- The `BobbingCoin` and `Coin` scripts of Practice 5 are `pseudocode`. Since the answers to walk G-final-4 they were
  built in the last checkpoint of `make/first-script` with the 0.8.0 package, and the Inspector steps were done as
  `script.remove`, `script.add` and `prefab.apply` (component `Script`): four instances updated, and after 45 fixed
  steps `Coin (2)` stood 0.249 m up and turned 67.5 degrees (`docs-work/walkfix-G4/out3/`). `std::sin` there relies on
  the SDK's headers pulling in `<cmath>` through glm (the exercise in `make/first-script` uses it too).
- That Coin Run's script is `Coin` in `Coin.cpp` with a field `DegreesPerSecond`: the brief's start state. The
  `make/first-script` page at this commit teaches `Spinner`.
- Links to pages not written yet: `basics/programming-2`, `basics/cpp-classes`, `basics/cpp-memory`, `basics/cpp-generic`,
  `basics/cpp-modern`, `basics/numbers`, `basics/build`, `basics/debugging`, `make/script-loop`, `make/script-fields`,
  `reference/script-api`.

## Findings not applied

- critic-basics-a-2, -6, -13, -17: applied. The section on files of code gives the registration rules (once per class,
  in the `.cpp`, the message `class 'Coin' is registered twice`, each field listed, setup in `OnCreate`) and
  `#pragma once` with the error it prevents; the inheritance section says that the base's field is listed again and
  that `GetScript<Coin>()` misses a `BobbingCoin`; the errors section shows the `double` field error from GCC. From -2,
  the rule of the loop for track E (stop, build, Play) stays on `basics/programming-1`; Practice 5 repeats it for the
  one place it matters here.
- critic-basics-a-12: applied as a table of seven words (`std::string_view`, `uint32_t` and `uint64_t`, `template<typename
  T>`, `explicit`, `[[maybe_unused]]`, `constexpr`, `= default`). Links only for those whose home the page names
  (`basics/cpp-modern`, `basics/numbers`, `basics/cpp-generic`); the homes of `explicit`, `[[maybe_unused]]` and
  `= default` are not known, so they carry no link. The advice to copy a view's text is general C++, not a claim about a
  callback's copy.
- The brief's item `gamedev:372` (a class in `Samples/Tetris/Scripts/TetrisGame.h`, read for its declarations): not
  used; the page reads declarations of the SDK's headers, which the card's 25-line limit fits better.
- The brief's "numbers turned into text with `std::to_string` read again in declarations": not applied; no declaration
  of the page uses it.

## Engine

- The Problems panel at the pin keeps only lines with a severity (`ParseDiagnosticLine`,
  `StrataEditor/src/Editor/ScriptBuild.cpp:313-381`). The place of the instantiation that a field type error comes from
  stands in note lines, MSVC's `<file>(<line>,<column>):` then `see reference to function template instantiation`, and
  GCC's `required from here`, so no row of the panel names the script's file and line, and the Console line that does
  cannot be opened by a double click (`FindSourceReference`, `:754-791`, wants a severity too). The page tells the reader
  to search the Console for `Coin.cpp(`. For the engine's agents: a row for the user's own line, or the note's place on
  the `Script.h` row, would let the reader jump to it.

## Clerk

- Nothing asked. The other page's failing sketch: see the sketches check (the clerk's report).
