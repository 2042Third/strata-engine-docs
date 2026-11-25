# Brief: `engineering/test-kinds`

| Field | Value |
| --- | --- |
| Title | GPU, end-to-end and package tests |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `engineering/test-program`, `gpu/first-triangle`, `editor/command-scripts` |
| From | build-test ch. 8 (`GPUContext`, validation errors, readback: writing a GPU test is `gpu/first-triangle`'s, this page is the suites; `EndToEnd` suites, the editor's smoke and export chains, sample runners, package and install tests) |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/test-kinds` — GPU, end-to-end and package tests

**Covers.** The job: the tests that need more than the test binary's own process: a GPU, the built programs, a
toolchain, an installation. The problem: GPU testing, with what `gpu/first-triangle` teaches linked (headless devices,
the one shared device and its reason, validation errors as failures, the error count, readback) and what this page
adds (exact pixels against tolerances; counts that arrive frames later; the perf suites with validation off; the
helpers), and end-to-end testing of programs (private sessions,
free ports, `--no-gpu`, killing what a failed test started). The map: the CTest fixture chains (the export chain, the
feature-test chain, the sample exports with their windowed checks and the samples' GPU perf test, the clean of the
perf results). The contract: GPU suites share one device and end with no new validation errors; end-to-end suites own
what they start. The toy: a test that starts a program, waits for its output by the clock and checks its exit code. The
GPU suites, from the test program's side: the shared device made on first use and the error count taken when a
context starts, `STRATA_TEST_GPU_VALIDATION=0`, which the GPU perf tests set so that they measure without validation,
and the command-buffer recycling of `ExecuteAndWait`; writing a GPU test is `gpu/first-triangle`'s. The helpers:
`GetDrawnCounts`, `ReadBufferRange`, `ReadMeshGeometry`, `MeasureNoise`; `ExactSpecification` and
`AddNeutralPostProcess` are named with a link to `image/tutorial-post-effect`. The flicker metrics of `FlickerMetrics.h`,
the book's home of measuring flicker in tests: each pixel of the newest frame reprojected by depth into the two before,
the second difference measured only where all three saw the same surface, with per-pixel and 32-pixel-block
statistics. A table of the GPU suites by area, with the light area's as the example (`GPU.SceneRenderer.Lighting`,
`.Shadows`, `.ShadowFilter` and the CPU suites beside them). End-to-end: the `EndToEnd` suites (`StandardStreams`,
`EditorAutomation`, `Recovery`) that run the built editor, CLI and runtime; the runners `ExpectFailure.cmake` and
`RunAndExpect.cmake`; command scripts as test data (the smoke script itself is quoted on `editor/command-scripts` and
linked), and the editor's smoke test followed from its CTest to
`SmokeViewport.png`; the scripts that must fail, wait or quit; the export chain and the runtime's option tests.
Sample regressions: `SampleProject.cmake` copies a sample, runs its `<Sample>Commands.json.in`, exports the game full
and pruned, runs both headless and fails on any warning nobody listed. Package and install tests:
`StrataScriptCore.Package` and `.PackageDist` build a project against the installed-style SDK; `StrataTests.Package`;
`StrataEditor.Scripts` makes, builds, plays and exports a scripted game with the real editor; `StrataEditor.Install`
installs into a fresh prefix, checks the exact top-level layout and makes a game with the installed editor alone. How
it is tested: `GPU.TestUtils`. Exercises: a GPU readback test with `ReadBufferRange`; a new `expect` in a sample's
command script, run through its CTest; trace it yourself: follow the export chain by a search for its fixtures, from
`StrataExport.Clean` through `StrataEditor.Export` to every CTest that requires the exported game, and check the
order with `ctest -N`. At the end the reader can choose the kind of suite a change needs, write a GPU
check that respects the shared device, and extend an end-to-end or sample test.

**Leaves out.**

- Writing a GPU test: `GPUContext`, the shared device and its reason, validation, the error count and pixel readback → `gpu/first-triangle`
- `ExactSpecification` and `AddNeutralPostProcess` → `image/tutorial-post-effect`
- The validation layer and frame captures → `gpu/debugging`
- The command-script format: `expect`, `bind` and `until`, and the smoke script quoted whole → `editor/command-scripts`
- Image comparisons between builds → `engineering/look-dev`
- The feature test's runners → `engineering/feature-test`
- The perf suites → `engineering/perf-lab`
- The install rules the install test checks → `engineering/releasing`
- Play-tests a game maker writes for a game → `make/automated-playtests`

**Fit.** `fits`: about 4,715 words against L (5,000). The two problems (the GPU testing this page adds, end-to-end
testing), four excerpts, two figures, the table of GPU suites by area and the package and install tests take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:348` | concept | home | GPU testing, the part `gpu/first-triangle` does not teach: exact pixels against tolerances, counts that arrive frames later (`GetDrawnCounts`), the perf suites with validation off, the helper catalogue; the shared device and its reason, validation, the error count and readback are linked to `gpu/first-triangle` |
| `build-test:119-124` | feature | home | The expect-failure and run-and-expect runners; command scripts as test data; the editor's smoke and script checks; the export chain and the runtime's option tests; the `EndToEnd` suites |
| `build-test:126` | feature | home | The GPU test helpers `GetDrawnCounts`, `ReadBufferRange`, `ReadMeshGeometry` and `MeasureNoise`; `ExactSpecification` and `AddNeutralPostProcess` are named with a link to `image/tutorial-post-effect`, their home |
| `build-test:164-168` | feature | home | The script-SDK package tests; `StrataTests.Package`; `StrataEditor.Scripts`; the sample tests; the install test |
| `gamedev:229` | feature | home | Sample regressions: one command script per sample, run by `SampleProject.cmake` |
| `render-indirect:197` | feature | home | The flicker meter, as the indirect area uses it in a strafe |
| `render-direct:228` | feature | home | The light area's CPU and GPU suites, as rows of the page's table of renderer suites; each light page's "How it is tested" names its own |
| `build-test:401` | code | home | `StrataTests/src/Renderer/GPUTestUtils.cpp:29-50`: `GPUContext`'s constructor, cut to what `gpu/first-triangle` does not show: the device made on first use, validation off for the perf suites, the error count's starting value |
| `build-test:411` | code | link | An end-to-end test as data: the smoke script, `StrataTests/Editor/SmokeCommands.json.in`, quoted on `editor/command-scripts` |
| `new:8` | code | home | `StrataTests/src/Renderer/FlickerMetrics.h:11-50`: the flicker meter's contract, the frame it reads and the statistics it reports |
| `new:9` | code | home | `StrataTests/Editor/SampleProject.cmake:1-20`: the sample runner's steps and options, as its header states them |
| `new:10` | code | home | `StrataTests/Editor/InstallEndToEnd.cmake:43-60`: `cmake --install` into a fresh prefix and the exact top-level layout |
| `build-test:438` | figure | home | The CTest fixture chains as graphs |
| `build-test:472` | figure | home | `SmokeViewport.png`, the smoke test's capture of floor, crate and lights, as an end-to-end artifact |
| `build-test:576` | hands-on | home | A GPU readback test: write a buffer, read it with `ReadBufferRange`, end with the error-count check, under validation |
| `gamedev:562` | hands-on | home | Extend a sample's command script with a new `expect` for a feature you added; run its CTest |
| `new:33` | hands-on | home | Trace it yourself, by a search for the fixtures' names: the export chain from `StrataExport.Clean` through `StrataEditor.Export`, which sets up `StrataExportedGame`, to every CTest that requires it (`StrataRuntime.PerfLog`, `.Render`, `.Resolution`, `.PerfLogWindowed`), then the order checked with `ctest -N` (about 150 words). Evidence: `StrataTests/CMakeLists.txt:591`, `:598`, `:673`, `:718`, `:726`, `:760` |
| `render-indirect:649` | term | home | Flicker meter |
| `build-test:125` | feature | use | `GPUContext` from the test program's side; `gpu/first-triangle` teaches it |
| `render-core:607` | rule | use | GPU tests share one device and end with zero new errors, as the suites keep it |
| `build-test:117` | feature | use | CTest fixtures, the mechanism of the chains |
| `render-image:273` | feature | link | `ExactSpecification` and `AddNeutralPostProcess`, taught on `image/tutorial-post-effect` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The test program: shards, labels, fixtures and helper modes | `engineering/test-program` | must |
| Writing a GPU test: `GPUContext`, the shared device and its reason, validation, the error count, pixel readback | `gpu/first-triangle` | must |
| `ExactSpecification` and `AddNeutralPostProcess` | `image/tutorial-post-effect` | helps |
| Command scripts: `expect`, `bind` and `$ref`, `until` | `editor/command-scripts` | must |
| Headless runs and `--no-gpu` | `core/first-frame` | helps |
| An exported game and its folder | `worlds/export` | helps |
| Script modules and the SDK they build against | `scripting/shared-libraries` | helps |
| Reprojection by depth and motion | `draw/motion-vectors` | helps |
| Luminance | `basics/color` | helps |
| TAA and its jitter | `image/taa` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `flicker-meter` | Flicker meter | - |
