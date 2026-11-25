# Brief: `engineering/test-program`

| Field | Value |
| --- | --- |
| Title | Inside StrataTests |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `engineering/testing`, `engineering/cmake` |
| From | build-test ch. 7, the program half, and §1.6 (`TestMain`, helper modes, the fake CMake and editor, `CoreShards.json` and `Testing.Shards`, labels, fixtures, locks, `SelectSweepOffsets` and `StrataTests.Fuzz`, `TestCrashReporter.cpp`, test helpers; excerpts 19-23); home of corruption sweeps and fuzzing |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/test-program` — Inside StrataTests

**Covers.** The job: one test binary, `StrataTests`, holds the module tests, runs as its own helper processes, and
CTest runs its suites side by side in shards; the GPU, end-to-end and package tests are `engineering/test-kinds`'.
The problem, in the part's full section on it: test organisation at scale (one big binary against many, running in
parallel, splitting by suite name and keeping a shard under a minute, labels for what a machine can do and for cost,
fixtures, locks), how CTest describes a test (a command with properties), and the mistake of a suite that silently
runs nowhere. The map: the shard figure (every suite of the binary in one column, arrows to the eight own CTests and
the 13 shards, the check that each suite runs exactly once, the `.Sweep` suites also to `StrataTests.Fuzz`). The
contract: every test case belongs to a `TEST_SUITE` and every suite prefix to a shard or an own CTest; tests write only
into `CreateTemporaryDirectory()`, never open a sample in place, never set the process's environment for a child.
The toy: a test runner's `main` with one helper mode, in 40 lines. The real code. What the binary compiles: the
module tests without the files of a module a build leaves out (`STRATA_TESTS_OF_*`), the test script modules built
with `strata_add_script_module`, the definitions the tests read (`STRATA_SOURCE_DIR`, `ST_TESTS_HAVE_EVERY_MODULE`,
`ST_TESTS_HAVE_EDITOR`, `DOCTEST_CONFIG_NO_POSIX_SIGNALS`). `main`: console streams, the log at Warn, the helper modes
and the composition root as every program runs it, the fake CMake and the fake editor, execution-speed throttling off,
private `STRATA_RUNTIME_DIR`, `STRATA_RECENT_PROJECTS` and `STRATA_SCRIPT_BUILDS_DIR`, the shared GPU shut down last.
The test binary as its own helper process: `--strata-test-helper=<mode>` with about 50 modes, among them
`run-with-environment` and `write-component-schema`, which writes the component schema snapshot again, and why a unit
test never depends on `cat`, Python or a real CMake. Crash containment against
the framework: doctest's signal handlers would replace `CrashGuard`'s and leave script crashes uncontained, so they
are off, and `TestCrashReporter.cpp` names the crashing case itself, with `STRATA_TEST_TRACE=1` printing each case
as it starts. Shards: `CoreShards.json` turned into `StrataTests.Core.<Shard>` CTests (label `core`); `Testing.Shards`,
which asks the binary for its suites in a child process, matches doctest's filters with backtracking and fails on a
suite in no shard or two, and on a case outside any suite; what the shards bought, in one sentence: after wave 4 a
Debug ctest on the Mac took 94 to 163 s with `-j 8` instead of 500 to 804 s serially. Labels (`core`, `fuzz`, `gpu`,
`perf`, `package`, `feature`, `tools`), fixtures, `RESOURCE_LOCK toolchain`, with its reason (concurrent builds
through one toolchain fail at random, with MSBuild's and mspdbsrv's C1090 and LNK errors) and the trap beside it (the
`Package*` suites build in the system temporary folder, where MSBuild does not track files, MSB8029, and may relink an
unchanged module), and `RUN_SERIAL`. Corruption sweeps, the book's home of
sweeps and fuzzing: exhaustive against sampled offsets, fixed seeds so a failure repeats, `SelectSweepOffsets`
(headers, the bytes near every block edge, and 512 offsets from a fixed seed), the whole sweep in `StrataTests.Fuzz`
with `STRATA_TEST_SWEEP=full` in Release and Dist, the pack sweep as the example; Strata has no coverage-guided
fuzzer. The helper catalogue: `WaitUntil`, `LogCapture`, `ScopedEnvironmentVariable`, `CopySampleProject`,
`CheckSceneCaches`, `RunCommandToCompletion`, and `ImGuiHarness` named with its page. The page states the 13 shards,
`SceneTiming` among them, where the Developer Guide and the build-test skill name 12; it never types the number of
CTests, which `ctest -N` prints. What went wrong before: a crash in static initialization leaves the Linux loader's
lock held, so such tests live in the `LoaderFaults` shard. Exercises: a suite with a new prefix and the failure of
`Testing.Shards`; a corruption sweep for a small parser, sampled and full; a helper-mode process test; trace it
yourself: follow `--strata-test-helper=run-with-environment` by a search from `main` to `RunHelperMode` and the mode's
code, and say what the child's environment holds. At the end the
reader can add a suite where CTest will run it, write a test that starts a child process without outside programs,
and write a sweep whose failures repeat.

**Leaves out.**

- What tests are for, the kinds of tests and flakiness → `engineering/testing`
- The GPU suites, the end-to-end suites and the package tests → `engineering/test-kinds`
- The feature test → `engineering/feature-test`
- The perf suites and their budgets → `engineering/perf-lab`
- Debugging a test that crashes → `core/debugging`
- `CrashGuard` itself → `scripting/crash-containment`
- Testing the editor's UI with `ImGuiHarness` → `editor-ui/ui-testing`
- Validating untrusted bytes in loaders → `assets/robustness`

**Fit.** `fits`: about 6,460 words against L (5,000). Four concepts, five excerpts, three figures, five rules, three
exercises and the trace take the most. The count puts the page 40 words below L's top, so it has no room for more.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:330` | concept | home | Test organisation at scale: runners, CTest, labels, sharding, fixtures and locks; the mistake of a suite prefix that matches no shard |
| `build-test:339` | concept | home | The test binary as its own helper process: spawning, crashes, consoles and exit codes tested without outside programs |
| `build-test:342` | concept | home | Crash containment against the test framework: signal handlers are process-wide, so doctest's are off and the reporter names the case |
| `build-test:345` | concept | home | Fuzzing and corruption sweeps: exhaustive and sampled offsets, fixed seeds, full sweeps in optimized runs; the mistake of seeds that change per run |
| `build-test:105-118` | feature | home | The binary and what it links; its definitions; the module-dependent test files; the test script modules; `main`; the helper modes, `write-component-schema` among them; the fake CMake; crash naming; the shards, and the Debug ctest they bought (94 to 163 s with `-j 8` against 500 to 804 s serially, on the Mac after wave 4); `Testing.Shards`; sweeps and the fuzz run; the resource lock with its reason (C1090 and LNK errors from concurrent builds through one toolchain) and the trap of the `Package*` suites in the system temporary folder (MSB8029, relinked modules); fixtures; labels |
| `build-test:127-129` | feature | home | The helper catalogue: the general helpers, the editor's (`RunCommandToCompletion`, `ImGuiHarness`), `CheckSceneCaches` |
| `build-test:396` | code | home | `StrataTests/CMakeLists.txt:209-255`: the shards read from `StrataTests/CoreShards.json` (shown beside it, lines 1-36) and turned into CTests, the own CTests' suites always excluded |
| `build-test:397` | code | home | `StrataTests/src/Testing/ShardTests.cpp:118-153`: `CheckShards`, "exactly once"; with `MatchesFilter` at lines 26-58 and the test case at 244-277 that asks the binary for its suites |
| `build-test:398` | code | home | `StrataTests/src/TestHelpers.cpp:700-737`: `SelectSweepOffsets`, all offsets in a full sweep, else the ranges, the block edges and seeded offsets; used by `StrataTests/src/Asset/AssetPackTests.cpp:984-1031` |
| `build-test:399` | code | home | `StrataTests/src/TestMain.cpp:1309-1370`: a test runner's `main`: the user's environment kept out, modules registered, helper modes |
| `build-test:400` | code | home | `StrataTests/src/TestCrashReporter.cpp:19-87`: a doctest listener that remembers the running case, and why doctest's signal handling is off |
| `build-test:436` | figure | home | The shards: every suite to exactly one own CTest or shard, the `Testing.Shards` check, the sweeps also to `StrataTests.Fuzz` |
| `build-test:462` | figure | home | Text captures of `ctest --preset windows-debug -N -L core` listing the shards, and the summary of a `ctest -j 8` run |
| `build-test:463` | figure | home | A text capture of `Testing.Shards` failing on a suite in no shard |
| `build-test:508` | rule | home | Every test case in a `TEST_SUITE`, every new suite prefix in a shard; shards under about a minute in Debug |
| `build-test:510` | rule | home | Tests that crash the dynamic loader go in `LoaderFaults` |
| `build-test:516` | rule | home | Never set the test process's environment for a child; use `run-with-environment` |
| `build-test:518` | rule | home | Tests write only into `CreateTemporaryDirectory()` and never open samples in place |
| `build-test:521` | rule | home | doctest's POSIX signal handling is off, because it would take `CrashGuard`'s handlers away |
| `build-test:572` | hands-on | home | Add a suite with a new prefix, watch `Testing.Shards` fail, add it to `CoreShards.json` |
| `build-test:574` | hands-on | home | A corruption sweep for a small parser with `SelectSweepOffsets` in a `.Sweep` suite, sampled in Debug and full with `STRATA_TEST_SWEEP=full` |
| `build-test:582` | hands-on | home | A new `--strata-test-helper=` mode and a test that runs it with `Process::Run` and checks its output and exit code |
| `new:32` | hands-on | home | Trace it yourself, by a search: `--strata-test-helper=run-with-environment` from `main` to `RunHelperMode` and the mode's code; what the child's environment holds and why the test process's own stays untouched (about 150 words). Evidence: `StrataTests/src/TestMain.cpp:238`, `:289-320`, `:1340` |
| `build-test:658-667` | term | home | CTest; label; shard; fixture; resource lock; `RUN_SERIAL`; helper mode; fake CMake and fake editor (two entries); sweep and `.Sweep` suite; fuzz run |
| `build-test:756` | open | home | The page states the shards of `CoreShards.json`, as `new:6` corrects the guide and the skill |
| `build-test:762` | open | home | The number of CTests depends on the configuration and the programs built; the page shows `ctest -N` instead of a count |
| `new:6` | erratum | home | `Docs/DeveloperGuide.md:402-405` and `.claude/skills/strata-build-test/SKILL.md:73-74` name 12 shards; `CoreShards.json` has 13: they omit `SceneTiming`, which runs `Scene.Timing*`. The page names the 13. Evidence: `StrataTests/CoreShards.json:14-35` |
| `new:7` | not-done | home | No coverage-guided fuzzer (libFuzzer, AFL): the sweeps test fixed, seeded offsets. Evidence: `git grep -niE "libfuzzer\|LLVMFuzzerTestOneInput\|fsanitize=fuzzer" 822a7a46 -- Strata/src StrataTests CMake CMakeLists.txt .github` finds nothing |
| `editor-ui:256` | feature | link | `ImGuiHarness`, taught on `editor-ui/ui-testing` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Kinds of tests, doctest, flakiness and its rules | `engineering/testing` | must |
| CMake targets, functions and generator expressions | `engineering/cmake` | must |
| Processes, exit codes, the standard streams and environment variables | `basics/tools` | must |
| Signals, exit codes and console programs | `core/platform` | must |
| JSON | `basics/data-formats` | must |
| The composition root and `ModuleRegistrationOptions` | `core/layers-registries` | must |
| Crash containment with `CrashGuard` | `scripting/crash-containment` | helps |
| Script modules and the dynamic loader | `scripting/loading` | helps |
| Random generators and fixed seeds | `basics/math-probability` | helps |
| Validating untrusted input | `assets/robustness` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `run-serial` | `RUN_SERIAL` | - |
| `ctest` | CTest | - |
| `fake-cmake` | Fake CMake | fake editor |
| `fixture-ctest` | Fixture (CTest) | - |
| `fuzz-run` | Fuzz run | - |
| `helper-mode` | Helper mode | - |
| `label-ctest` | Label (CTest) | - |
| `resource-lock` | Resource lock | - |
| `shard` | Shard | - |
| `sweep` | Sweep | `.Sweep` suite |
