# Notes: engineering/test-program

## New terms

- fuzz run: the CTest `StrataTests.Fuzz` (Release and Dist), which runs every `.Sweep` suite with every offset. Home: engineering/test-program. Aliases: StrataTests.Fuzz.
- sweep: a test that damages one valid file in many ways, one at a time, and checks the code fails cleanly or reads right. Home: engineering/test-program. Aliases: `.Sweep` suite.
- helper mode: a first argument `--strata-test-helper=<mode>` that turns StrataTests into a small child program. Home: engineering/test-program.
- fake CMake: the test binary standing in for CMake when `STRATA_TEST_FAKE_CMAKE` is set; the fake editor is its alias. Home: engineering/test-program.
- shard, label (CTest), fixture (CTest), resource lock, `RUN_SERIAL`, CTest: defined in bold as the brief's glossary terms.

## Requests

- Names/words: "macOS" and "Mac" avoided (macOS in code); `libFuzzer`, `AFL`, `GoogleTest`, `MSBuild`, `LNK` kept in code spans. If the clerk wants them plain: add to names.txt.
- Word "StrataTests" in the title triggers a heading-case warning: add to names.txt.
- Figure `core-shard-list` (text capture of `ctest -N -L core`) is requested in src/content/figures/engineering/test-program.json; not taken.
- Links to engineering/testing, cmake, test-kinds, feature-test, perf-lab pages exist only once those pages are written.

## Since

0.4.0: shards, `Testing.Shards`, sweeps and the fuzz run arrived in wave 4 (plan/inventory/build-test.md, 1.6).

## Not verified

- "More than 40 helper modes": counted 47 lines `mode == "` in TestMain.cpp including the fake CMake's three; the inventory says about 50.
- The Mac Debug ctest times (94 to 163 s against 500 to 804 s) are from Docs/Roadmap.md, not measured.
- Claims about doctest's/GoogleTest's CMake discovery, libFuzzer and property-based test libraries in the alternatives table are general knowledge, not read from a source.
- The text fence with the `Testing.Shards` failure message is composed from the format string in ShardTests.cpp, not a captured run (a capture needs a patched build).
- The exercise 3 pseudocode (`write-lines` mode) was not compiled.
- On Windows doctest's own crash report names the case: taken from the comment in TestCrashReporter.cpp.

## Findings not applied

None: the brief's open items (`build-test:756`, `:762`, `new:6`, `new:7`) are applied: the 13 shards are named with `SceneTiming`, no CTest count is typed, and the page says Strata has no coverage-guided fuzzer.

## Clerk

- Fuzz run, sweep, helper mode and fake CMake (with its alias fake editor) are in the glossary already, homed here; the code-form aliases StrataTests.Fuzz and `.Sweep` suite were left out (names checks code).
- Admitted to names.txt: StrataTests, Mac; libFuzzer, AFL, GoogleTest, MSBuild and LNK stay in code spans.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `core-shard-list` (text, `ctest --test-dir ../.. -C Debug -L core -N`): published at v0.8.0 (319075e3), round 2,
  filled into the page's fence. Round 1: the pin's build holds no StrataTests.exe (Release programs only), so ctest
  printed an 8-line "Could not find executable ... Looked in the following places:" warning before every test line
  (`-C Release` gave the same). Round 2: the redact patterns cut the header and each warning; each of the 13 lines
  (`StrataTests.Core.Core` to `StrataTests.Core.Editor`) starts with the mark, and `Total Tests: 13` ends the list.
  Caption and alt say so. The page's sentence after the fence stays true.
- Page problem for the writer: the filled fence holds 15 lines, so lint (`callouts`, fences of 10 lines or more) wants
  1 to 5 numbered callouts right after it instead of the paragraph "Each line is one shard as a CTest, ...". Until a
  writer turns that paragraph into callouts (for example Line 1, the first shard; Line 15, the count), pagecheck fails
  on this page for that rule alone.
