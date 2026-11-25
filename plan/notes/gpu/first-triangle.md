# Notes: gpu/first-triangle

## New terms

None proposed. The glossary homes no term on this page.

## Since

`since: 0.3.0`. The suite test file `StrataTests/src/Renderer/GPURendererTests.cpp` was added in a commit contained first
in the tag `v0.3.0-rc1`, and `Debug/ColorTriangle` has been in `Strata/CMakeLists.txt` since `v0.3.0` (`git tag
--contains` on the commits that added them).

## Requests

- A text capture of the passing run (`StrataTests --test-case="Triangle rendering follows*"`): `text.program` allows only
  `StrataEditor`, `StrataRuntime`, `StrataCLI` and `ctest`, so the page describes the three doctest summary lines in
  words (7 checks by count of the test's `REQUIRE` and `CHECK` lines). Please allow `StrataTests` as a text program, or take
  the capture by the integrator.
- Figures `result` and `checker` are diagrams drawn as SVG (`src/assets/figures/gpu/first-triangle/`); the integrator
  should check that the pixel values they show equal the first run of the tutorial.
- Link targets that other pages of the book must provide: `gpu/coordinates`, `gpu/debugging`, `gpu/readback-timing`,
  `engineering/test-kinds`, `draw/lod`.

## Not verified

- The doctest output of the broken run (`top pixel 0 0 255` from `INFO`, `5 | 5 passed | 2 failed`) follows from the code and
  doctest's variadic `INFO`; it was not run. How doctest prints a `glm::u8vec4` in a failed `CHECK` was not found (no printer
  at the pin), which is why the page adds `INFO` lines.
- That the first GPU test of a run is the slowest because it creates the device: from `GPUContext`'s constructor, not timed.
- The phrase that some drivers handle repeated instance creation poorly is from the comment of `GPUTestUtils.h:16-20`; the
  inventory's "crashed drivers under load" was not reproduced.
- Whether `ctest -L gpu` passes on a machine without a Vulkan device (it does not; the page says a real device is needed).

## Findings not applied

- The brief's figure row says "the top half red, the bottom half the blue clear". At the pin the triangle covers only the
  part of the top half under its tip (corners at pixels (0, 32), (64, 32), (32, 0)); the page and the figure say so.
- The brief says "Read what the test does ... `Renderer::ReadTexture`, the two pixels" with a 64x64 target: applied. The
  `ExactSpecification` and `AddNeutralPostProcess` items are left out as the brief says.
- `ShutdownShared` (named in the brief's `build-test:125` row) is not taught: only perf tests call it (`LocalShadowsMemory.cpp:124`,
  `StressProject.cpp:979`), and the page names `ExecuteAndWait` only.

## Clerk

- No term or word asked.
- Left for the planner: StrataTests as a text figure's program, the SVG figures, the patches' runs, the links to unwritten pages.

## Tutorial run

- 2026-11-24, `tutorials.py patch` at the pin 319075e3: the page's patch and exercise 2 pass (build, `Architecture.Layering`,
  `GPU.Renderer` with 12 and 13 test cases, the feature test). `Checker.frag.slang` and `ChannelRotate.frag.slang` compile
  with the pinned slangc, the five checker pixels and the blue of exercise 2 come out as the page says.
- `exercise-2.patch` was a diff against the pin that also created the checker; the tool applies it after the page's patch,
  so it was remade as a diff on top of the page's change, and the exercise's answer says so.
