# Notes: make/script-builds

## Since

0.3.0: the script module and its CMake file exist since the first tag (inventory gamedev:124, 0.3.0).

## New terms

- integrated development environment (IDE): a code editor with a build button and name completion; home this page; alias IDE.

## Requests

- Word: IDE is proposed as the term above (word-list finding stays until the clerk admits it).
- Host: none.

## Not verified

- The exact lines CMake and the generators print for `cmake --preset strata` and `cmake --build --preset strata`: the page names only their shape (the closing configure line and the module file).
- That "Developer PowerShell" of Visual Studio finds a CMake: taken from the finding critic-make-b1-1 and the manual (Visual Studio ships one).
- The IDEs' own menu names beyond "File > Open > Folder..." and the preset list.
- The module name `CoinRunScripts` assumes the project is named Coin Run (rule of `Project::MakeScriptModuleName`, read at the pin).

## Findings not applied

- critic-make-b1-1: applied (preset steps; plain build moved to Variations).
- critic-make-b1-3: applied (Variations: plain build as a check, other compiler, deep folder, libraries).
- critic-make-b1-12: applied (four lines taught; Play versus Ctrl+B pitfall); the exercise is Exercise 1, not a separate section, because the how-to's body ends with Variations.

## Clerk

- Admitted the term integrated development environment, homed here (aliases IDE, IDEs), from the page's sentence.

## Tutorial run

- 2026-11-23, round 1 at the pin: exercise-1 passes after the Coin Run chain. The file was thinner than the answer; it now
  also checks the Console line `Triple of 14 is 42`, rebuilds with the factor 4 while playing (`/reloaded` true) and
  checks `Triple of 14 is 56` at the next start.
- The solution zip held `Libraries/Triple/Triple.cpp` twice (both factors); `solution_files` now keeps a path's last
  copy (test in tools/tests/test_tutorials.py).
- 2026-11-23, re-run at the pin v0.8.0 (319075e3): exercise-1 passes as written after the Coin Run chain; nothing mended.
- 2026-11-24, track G walk segment 8 (WK3): exercise-1 has two stages, so that the reader's commands show 42 and then
  56; `solution_files` keeps the first stage's copy of a path a later stage copies again and puts the later copy under
  `stage-<step>/` of the zip. Passed with the pin build and the 0.8.0 package.
