# Brief: `gpu/debugging`

| Field | Value |
| --- | --- |
| Title | Debugging the GPU: validation, frame captures, the error count and debug views |
| Kind | H |
| Size | M |
| Tracks | E |
| Needs | `gpu/first-triangle`, `core/debugging` |
| From | new; render-core concept 4 and hands-on 12 (a frame in RenderDoc or Nsight); the validation layer, debug names and markers, `GetNewErrorCount`, the editor's debug views (`debugView`) and the page that reads each; curricula 1.9.1 [gap] |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/debugging` — Debugging the GPU: validation, frame captures, the error count and debug views

**Covers.** The goal: find out why a frame looks wrong or why a GPU test fails, with the GPU's own tools. What must be
true first: a Debug build of the pin, a copy of the Showcase sample open in its editor, RenderDoc or Nsight Graphics
installed. The steps: run with validation (on in Debug builds, off in the others, on in tests unless
`STRATA_TEST_GPU_VALIDATION` is `0`); read a validation message in the log and its severity, with two sentences on why
it is counted and a link to `gpu/vulkan-nvrhi`, which teaches what the layer checks and how messages are classified;
recognize the reports Strata demotes on purpose (MoltenVK's blending report, the bindless support query, the loader's
search for a missing layer) and NVRHI's own errors; use the error count in a test and stop in the message callback to
find the call that caused it; give resources names and passes markers; capture a frame with RenderDoc and find the
markers of `gpu/frame-tour`'s passes, knowing that shaders carry no source-level debug information; switch the Scene
view's debug view and go to the page that reads it.

The page holds the table of debug views (streaming, lod, mip, motion, shadows, lighting, ao, indirect, luminance,
albedo, voxels), each with what it shows in one line and the page that teaches reading it. The result: the reader can
tell API misuse (validation), wrong data (a capture) and a wrong look (a debug view) apart. Variations: Nsight in place
of RenderDoc; macOS and MoltenVK; a failing GPU test instead of the editor; a debug view saved to a file with
`viewport.capture`, given as the complete line to paste with a link forward to `editor/commands`. The exercise breaks an
NVRHI rule on purpose in a scratch copy of the triangle test and finds the line through the message callback.

**Leaves out.**

- What the validation layer checks, why it is off outside Debug and how errors are counted → `gpu/vulkan-nvrhi`
- What each lighting view measures and its statistics → `light/measuring-light`
- Reading the streaming, lod, mip and motion views → `draw/asset-requests`
- How overlays draw the tints and views over the image → `gpu/debug-drawing`
- The frame's passes the markers name → `gpu/frame-tour`
- Debugger setup per OS and asserts → `core/debugging`
- The GPU suites and their error checks → `engineering/test-kinds`

**Fit.** `fits`: about 2,900 words against M (3,000). Seven steps without theory, the table of debug views, four
variations and the exercise take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:304` | concept | link | Validation layers and error counting, in the two sentences a how-to allows, with a link to `gpu/vulkan-nvrhi`, its home |
| `render-core:41` | feature | use | Reading a classified message in the log: an error counted, a warning logged, the demoted reports recognized |
| `render-core:42` | feature | use | NVRHI's errors in the log and in the error count a test checks |
| `new:11` | feature | home | Debug names on resources and markers around passes, which a frame capture shows. Evidence: `Strata/src/Strata/Renderer/Renderer.cpp:63, 119` (`desc.debugName`); `Strata/src/Strata/Renderer/SceneRenderer.cpp:3286` (the renderer's name as the frame's marker) and `:3361-3723` (a marker per pass) |
| `new:12` | not-done | home | No shader debug information: slangc runs without `-g`, so a frame capture shows shaders without their source. Evidence: `CMake/StrataShaders.cmake:77-79`; `Docs/Roadmap.md:1090` (read again at the pin) |
| `render-core:542` | figure | home | A validation error in the log, counted as an error (a text capture) |
| `render-core:656` | hands-on | home | Capture the editor in RenderDoc or Nsight and match the markers to the passes |
| `render-core:845` | open | home | Settled: the engine's documents describe no capture tool (the Roadmap names RenderDoc once, `Docs/Roadmap.md:1090`); the markers exist, so the capture steps are checked on the GPU in phase B |
| `render-core:691`, `build-test:668` | term | link | Validation layer, homed on `gpu/vulkan-nvrhi` with `render-core:304` |
| `render-core:52` | feature | use | Validation on by default in Debug builds only |
| `render-scene:182` | feature | home | The viewport's debug views as a list, and their mechanism: the lod, streaming, mip and motion tints and views; each view is read on its subject's page |
| `render-direct:757` | term | home | Debug view (lighting, AO, indirect, luminance, albedo, shadows), beside the list of views it names; `light/measuring-light` links (about 30 words) |
| `editor-ui:198` | feature | use | The Scene view's chips, the debug view among them |
| `render-direct:177`, `render-direct:178` | feature | link | The shadows view; the lighting views |
| `render-indirect:180` | feature | link | The GI's views (voxels) |
| `render-image:174` | feature | link | The motion view |
| `assets:214` | feature | link | The streaming and mip views |
| `new:35` | hands-on | home | Exercise (modify): in a scratch copy of the triangle test, break one NVRHI rule on purpose, run it with validation, stop in the message callback and follow the call stack to the line that caused the error; the worked solution is a patch that names the rule broken. Evidence: `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:86-106, 110-134`; `StrataTests/src/Renderer/GPURendererTests.cpp:131-172` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Writing a GPU test and its error count | `gpu/first-triangle` | must |
| Debugging the engine: a debugger attached, breakpoints, the log | `core/debugging` | must |
| Opening a sample's copy in the editor and its Scene view | `start/first-game` | must |
| The frame's passes, for the markers | `gpu/frame-tour` | helps |
| How to read and run a command | `start/how-to-read` | helps |

**Starting state.** A Debug build of the pin made as `core/first-change` shows, with its editor; a copy of the Showcase
sample made from the launcher and opened, as `start/first-game` shows; RenderDoc or Nsight Graphics installed for the
capture step. No change to the engine.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `debug-view-gpu` | Debug view (gpu) | - |
