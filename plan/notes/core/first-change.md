# Notes: core/first-change

## New terms

None proposed. `Dist`, which the brief homes here, is already a glossary entry (id `dist`, home `core/first-change`);
the page defines it in bold in the paragraph after the build section's steps.

## Requests

- Text figures of programs the schema does not allow: `StrataTests` (the run of `--test-suite=Core.StringUtils`, passing
  and failing) and `cmake` (the configure and build logs), and figures taken on a build with the page's patch applied.
  `text.program` allows only `StrataEditor`, `StrataRuntime`, `StrataCLI` and `ctest`, run on the pin's build. The
  page therefore describes those outputs in words (the doctest summary lines, verified in
  `Strata/vendor/doctest/doctest/doctest.h:7168-7186` and `:6846-6850`; the counts 3 test cases and 21 checks follow
  from `StringUtilsTests.cpp` plus the patch), instead of the text captures the brief asks for.
- An `editor` figure of the editor's welcome window before any project is open (step 3 of "Build the engine and start
  the editor"): editor figures must name a project (`figures.py`: "a editor figure runs an editor on a project"), so
  the page has no picture of it; the window's labels are from `StrataEditor/src/Panels/WelcomePanel.cpp:394-552`.
- `names`: `ST_DIST` is reported as "no #define at the pin defines it". It is a compile definition that
  `strata_configure_target` adds per configuration (`CMake/StrataCompilerOptions.cmake:100-103`) and that
  `Strata/src/Strata/Core/Base.h:10-12` and `ScriptHostAPI.cpp:3626` test; the names dump should list CMake
  definitions too.
- Names for `tools/data/names.txt`, avoided on the page for now: MoltenVK, LunarG, Homebrew, CTest, cppreference.

## Not verified

- git's own messages (cloning progress, "switched to a new branch", one block per submodule) and CMake's last configure
  lines ("build files have been written to") are the tools' general behaviour, not read at the pin.
- That a Debug build on Windows fails to link `StrataEditor.exe` while the editor runs: from the skill
  `strata-make-a-game` (line 31, "the executable is locked") and Windows behaviour; not reproduced.
- The Hard exercise in Debug: `Assert.cpp` logs the critical line and calls `std::abort` (no debugger attached). Read
  at the pin, not run: on Windows doctest's SIGABRT handler calls `reportFatal`, which ends with `test_run_end`, so the
  summary prints (`doctest.h:7866-7877`, `:7949-7955`); on Linux and macOS `DOCTEST_CONFIG_NO_POSIX_SIGNALS` is set
  (`StrataTests/CMakeLists.txt:164-168`) and `TestCrashReporter.cpp:97-112` prints `Fatal signal 6 in test case:`.
  That the Windows Debug runtime shows its "abort() has been called" box first comes from
  `PhysicsCapacityTests.cpp:100-103`, which turns that box off for its own process; the order was not reproduced.
- The `core-shards` recipe (blocked) runs `ctest --test-dir ../.. -C Debug -L core` from `bin/Debug`; whether two runs
  give the same order of tests (CTest's cost data) is not known; the redact list removes times and the project path only.
- GLFW's X11 configure also requires the X Shape headers (`libxext-dev`, `Strata/vendor/glfw/src/CMakeLists.txt:213-216`);
  the page keeps `Docs/DeveloperGuide.md`'s package list, which omits it. Whether `libxrandr-dev` brings it was not
  checked.
- How long the first build and the core run take: not measured, so the page gives no time; `time: 120` is an estimate
  that includes the first build.

## Findings not applied

- The brief asks for four sections "each ending in a checkpoint of the patch". The tutorial card (kind-T, "has no
  checkpoints") and `tools/tutorials.py` (a patch tutorial has no stages) say an engine-changing tutorial has none, so
  the page has no `::checkpoint`.
- The brief asks that every "You should see" be a text capture; see the first request: two are captures
  (`editor-version`, `core-shards`), the others are described in words.
- Debug, Release and Dist take two paragraphs, not one: one paragraph would hold six sentences (`paragraph-length`).
- The brief's Linux box names the developer guide's packages; the page adds `ninja-build`, because the `linux` and
  `macos` presets use the generator Ninja Multi-Config (`CMakePresets.json:34-47`, `.github/workflows/ci.yml:78-85`).

## Since

`since: 0.3.0`: `StringUtils.h`, `StringUtilsTests.cpp` and `CMakePresets.json` were added by a0f2865f, c53f9a35
and c4336171 (2026-10-08 to 2026-10-11), all contained in the tag `v0.3.0` (`git tag --contains`).

## Figures

- `editor-version` (text): retaken at the pin v0.8.0 (319075e3), 1 round. The new take reads `Strata Editor 0.8.0`
  where the one published at 822a7a46 read `Strata Editor 0.7.0`; the version number is the only change, and the
  caption and alt still hold. Published, and `fill` wrote the new line into the page's fence.
- `core-shards` (text, `ctest`): left untaken, 0 rounds, again at v0.8.0 (the pin build still has only `bin/Release`). The photographer's card leaves `ctest` text figures to
  others (step 2), and the pin has only a Release build (`docs-pin/build/windows/bin/Release`; no `bin/Debug`), so the
  recipe's `-C Debug -L core` has nothing to run. The photographer's proposal, the same run with `-C Release`, cannot be
  taken either: `bin/Release` holds `StrataEditor`, `StrataRuntime` and `StrataCLI` only, no `StrataTests.exe`
  (2026-11-24). Now `blocked` with that reason, kept as the request for a later edition (a build of `StrataTests` at
  the pin, and a take that may hold the lock for the whole core run), with `standIn: core-groups`.
- `core-groups` (text, `ctest`, the stand-in): `ctest --test-dir ../.. -C Debug -L core -N`, the recipe of
  `engineering/test-program`'s `core-shard-list` with the same redact list (the project line, and each "Could not find
  executable" warning, which leaves the mark `…`). It lists the 13 group names that the run's `Passed` lines carry,
  without running them; the caption says so and names the cut warnings. Taken at v0.8.0 (319075e3), 1 round, and
  published; the page's step 4 now says that the names on the run's lines are the groups that `ctest -N -L core` lists, and two callouts after the fence (lines 1 to 13, line 15)
  tie the list to the run's `Passed` lines and summary.
  Not verified: that a run prints the groups in the order of this list (CTest may order them by its cost data), so
  neither the page nor the caption claims an order.

## Clerk

- `tools/data/names.txt`: MoltenVK, LunarG, Homebrew, CTest and cppreference added.
- The text-figure programs, the welcome-window figure and the `ST_DIST` names finding are tool requests for the
  planner, not the clerk's.

## Tutorial run

`tutorials.py patch` at v0.8.0 (319075e3), 2 rounds (work folders `docs-work/patch-runs/core-first-change/round-<n>`).

- `first-change.patch` applied as written. Round 1 failed in the build on `C1083` for `WindScripts.cpp` and three more
  files that an earlier runner's WindZone chain had added to the shared `build/docs-patch`; that build ran configure
  again, and round 2 built it.
- `exercise-1.patch` and `-2.patch` were diffs against the pin that held the page's change too; the runner applies an
  exercise's patch after the page's (`PatchItem`), so they no longer applied. Remade as diffs on top of the page's
  patch, same code; both answers now say so.
- `exercise-3.patch` (the assert) failed as the exercise means it to: Release keeps the asserts, and the run logged
  `Assertion '!text.empty()' failed at …StringUtils.h:26: ToUpper was given empty text`, then doctest's `test case
  CRASHED: SIGABRT` and its summary, `Status: FAILURE!` (Windows). No patch of it can pass, and its end state is the
  Basic exercise's, so the patch and its download are gone and the answer names no `solution=`. The Debug message box
  is still not reproduced.

Track walk E-final-5 (2026-11-24, work folder `docs-work/walkfix-E5`): `tutorials.py patch core/first-change` passed
all three files again, with the stamps unchanged (3 | 21, 3 | 23, 4 | 26). By hand in the same Release build: with
`std::tolower` in `ToUpper`, 3 | 2 passed | 1 failed and 21 | 17 passed | 4 failed, four `is NOT correct!`; with
exercise 1 on top, 23 | 18 | 5, the check of `été` failing and the empty one passing; the Hard exercise's two lines
logged `Assertion '!text.empty()' failed at …StringUtils.h:26: ToUpper was given empty text`, then `test case CRASHED:
SIGABRT` and `Status: FAILURE!`. Debug and Dist are not built in `build/docs-patch`, so the Debug message box and the
Dist pass stay unrun. The configure error of a clone without submodules was taken from a copy of `CMakeLists.txt` and
`CMakePresets.json` (`cmake --preset windows`, Visual Studio 2026): CMake wraps the message onto two lines.
