# Brief: `gpu/first-triangle`

| Field | Value |
| --- | --- |
| Title | Tutorial: your first triangle in Strata |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `core/first-change`, `gpu/shaders`, `gpu/coordinates` |
| From | render-core; home of writing a GPU test (the shared `GPUContext`, the error count, pixel readback); moved after `gpu/coordinates` (it uses shaders and clip space) |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/first-triangle` — Tutorial: your first triangle in Strata

**Covers.** What you will make: a GPU test that draws one triangle without a vertex buffer, reads its pixels back and
proves Strata's clip-space convention; then a shader of your own, registered, drawn and tested. What you need: the
source build of `core/first-change`, a terminal, about two hours. The step sections, each ending in a checkpoint of the
patch: "Run the triangle test" (`StrataTests --test-case="Triangle rendering follows*"`, the passing line as a text
capture); "Read what the test does" (the shader's three positions and `SV_VulkanVertexID`, a 64x64 target, a pipeline,
a command list, the clear, `draw` of three vertices, `Renderer::ReadTexture`, the two pixels, the error count; the
shared `GPUContext` and why a run has one device); "Break the convention on purpose" (move the triangle to the bottom
half, build, watch the expectation fail with its pixel values, restore it; a shader edit needs a build, not a
configure); "Add a shader of your own" (`Debug/Checker.frag`, its line in `strata_add_shaders`, configure again,
`ShaderLibrary::Get`); "Draw it and test it" (with `PostProcess/Fullscreen.vert` into an offscreen target, pixels checked
in a new `GPU.*` test that ends with `CHECK(gpu.GetNewErrorCount() == 0)`).

This page is the home of writing a GPU test: one shared device, validation on unless `STRATA_TEST_GPU_VALIDATION` is
`0`, the error count at the end, pixels read back with the blocking call that only tests and tools may use. The
exercise, with a worked solution, breaks a `mul` in a copy of a shader, sees that it compiles, and writes the pixel test
that catches it. A hint after it names the engine's second technique: a shader function tested against its C++ twin by a
small diagnostic compute shader (`Debug/BlueNoise.comp`, `Debug/LODSelection.comp`, `Debug/ShadowViewStats.comp`).

**Leaves out.**

- The GPU suites → `engineering/test-kinds`
- Exact-pixel specifications (`ExactSpecification`) and `AddNeutralPostProcess` → `image/tutorial-post-effect`
- Reading validation messages and capturing a frame → `gpu/debugging`
- Pipeline state objects and binding layouts in full → `gpu/binding`
- Non-blocking readback in a frame → `gpu/readback-timing`
- Writing a test from zero with doctest → `core/first-change`

**Fit.** `fits`: about 4,100 words against L (5,000). Five sections of one to three steps, four excerpts quoted from the
patch and the exercise with its solution and hint take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:442` | code | home | `Strata/shaders/Debug/ColorTriangle.vert.slang:1-35`, with its test `StrataTests/src/Renderer/GPURendererTests.cpp:131-172`: the smallest complete GPU program, and the convention proved by two pixels |
| `new:9` | code | home | `StrataTests/src/Renderer/GPUTestUtils.h:16-48`: `GPUContext`: one device per run, validation unless the variable is `0`, `GetNewErrorCount`, `ExecuteAndWait` |
| `new:10` | figure | home | The test's 64x64 image as a diagram: the top half red, the bottom half the blue clear, the two pixels the test reads marked. Evidence: `StrataTests/src/Renderer/GPURendererTests.cpp:137, 152, 167-170` |
| `render-core:607` | rule | home | GPU tests share one device and end with zero new errors: repeated `VkInstance` creation crashed drivers under load |
| `render-core:627` | hands-on | home | Read the triangle test, move the triangle to the bottom half, watch the test fail |
| `render-core:630` | hands-on | home | Add a debug shader entry, draw it with the fullscreen vertex shader, test its pixels |
| `render-core:634` | hands-on | home | Break and observe a dialect trap, as the exercise |
| `render-core:66` | feature | use | `Renderer::ReadTexture`, the blocking readback for tests |
| `render-core:120`, `render-core:125` | feature | use | Registering the new entry; loading it through `ShaderLibrary` |
| `render-core:139` | feature | use | Fullscreen UVs, for the checker |
| `build-test:125` | feature | home | The GPU test context from the test program's side: one headless device per process, validation unless `STRATA_TEST_GPU_VALIDATION` is `0`, `GetNewErrorCount`, `ExecuteAndWait`, `ShutdownShared`; the same subject as `new:9`, taught once with it |
| `build-test:512` | rule | home | Never create a graphics device in a test, and end GPU tests with the error check, as the test program states it: the same rule as `render-core:607`, taught once with it |
| `new:34` | feature | home | A hint after the exercise: shader functions are tested against their C++ twins by small diagnostic compute shaders that run an include's function and write the results to a buffer the test reads back (`Debug/BlueNoise.comp`, `Debug/LODSelection.comp`, `Debug/ShadowViewStats.comp`; the LOD case is `draw/lod`'s) (about 120 words). Evidence: `Strata/shaders/Debug/BlueNoise.comp.slang:5-6`; `Strata/CMakeLists.txt:103-105`; `StrataTests/src/Renderer/GPUBlueNoiseTests.cpp:35` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The short source build, one test case and running `StrataTests` | `core/first-change` | must |
| The terminal: a program with arguments, environment variables | `basics/tools` | must |
| Shaders, registering an entry, re-running configure | `gpu/shaders` | must |
| Clip space, NDC with +Y up, fullscreen UVs | `gpu/coordinates` | must |
| NVRHI's device, command lists and immediate lists | `gpu/vulkan-nvrhi` | must |
| GPU resources in NVRHI: a render target, a framebuffer and a draw's graphics state | `gpu/vulkan-nvrhi` | must |
| Pipeline state objects | `gpu/binding` | helps |
| Readback in a frame, polled | `gpu/readback-timing` | helps |

**Starting state.** The source build of `core/first-change`: the engine at the pin in the reader's own build directory,
configured with the platform's preset and built in Debug, so `StrataTests` exists and validation is on. No project and
no editor are used. The tutorial's patch starts from the pin; each section's checkpoint is the patch up to that section.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
