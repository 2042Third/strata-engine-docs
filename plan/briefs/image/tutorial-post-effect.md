# Brief: `image/tutorial-post-effect`

| Field | Value |
| --- | --- |
| Title | Tutorial: adding a post effect |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `image/taa`, `gpu/first-triangle`, `core/first-change` |
| From | render-image ch. 13 (push constants, `PostSource`, the neutral helper, the GPU stage, GPU tests, a feature-test value) |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `image/tutorial-post-effect` — Tutorial: adding a post effect

**Covers.** What you will make: a post effect of the reader's own, end to end: a letterbox, the first of the two effects
the engine-developer hands-on proposes, black bars that crop the image to a wider aspect, with a picture of it off and
on rendered from the tutorial's patch. Its neutral value (off) leaves the image exact and its GPU test checks exact
pixels; no letterbox pass exists in the renderer at the pin (the editor's letterboxing of the Game view's panel is
another thing, named in one sentence). What you need: the source build of `core/first-change` and the GPU test of
`gpu/first-triangle`. The step sections, each ending in a checkpoint of the patch whose result is a build or test
output: (1) a property on the Post Process component, registered with its range, and an inactive reason where another
property turns it off; (2) its parameters by push constants in `PostProcessData.h`, never by new `FrameConstants` fields,
with a static_assert of their layout; (3) the shader, listed in `strata_add_shaders`; (4) the pass in
`SceneRendererPost.cpp`, between the TAA resolve and the tone mapping, reading the frame's `PostSource` through one
binding set per source and becoming the next source (code #2 is walked here as the place where it goes); when its
resources cannot be made, the pass returns failure and `RenderFrame` sets `degraded`, as the other passes do, and the
frame goes on without it; (5) off in
`Tests::AddNeutralPostProcess` and bit-identical at its neutral value; (6) the GPU stage it belongs to, `GPU.Post` or a
stage of its own; (7) a GPU test with `Tests::GPUContext`, `ExactSpecification` and the error count; (8) a value in the
feature test.

Each change is quoted from the patch, and each "You should see" is the build or test output as a text capture; the last
checkpoint shows the effect in the editor's viewport after the property is set in the inspector. The two rules of the
inventory frame the steps: post passes take their parameters by push constants or by buffers of their own, and a new
effect runs between the TAA resolve and the tone mapping, reads the post source, is off in the neutral helper and keeps
the image bit-identical at its neutral value. At the end the reader can add a post effect that passes the review
checklist. The bottom strip's exercises are open extensions: bars of a color the component sets (`new:27`), and a GPU
stage of the effect's own (`new:28`).

**Leaves out.**

- Why the chain has this order and these rules → `image/why-post`
- Every preset, configuration and option of the build → `engineering/building`
- The feature test in full → `engineering/feature-test`
- The GPU suites and the tests that compare exact pixels → `engineering/test-kinds`
- Registering a GPU stage in general → `gpu/readback-timing`

**Fit.** `fits`: about 4,350 words against L (5,000). Eight step sections, each with its patch quote and its text
capture, and the walk of code #2 in step 4 take the most words; the two open exercises add about 450.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:618` | hands-on | home | The tutorial's subject, a letterbox (R32, D43): a new post effect with push constants, `PostSource` sets, off in `AddNeutralPostProcess`, bit-identical at neutral, a GPU stage only if its own, the feature test; no letterbox pass exists at the pin (`git grep -n -i letterbox 822a7a46 -- Strata/src/Strata/Renderer Strata/shaders` finds nothing) |
| `render-image:396` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:3582-3629`: the post block of `RenderFrame`: the source switching from HDR to History, DepthOfField and MotionBlur, the key's reference, the sun's place on screen; where the new pass goes |
| `render-image:49` | feature | home | The post passes' GPU data in `PostProcessData.h`: constant buffers, push constants, slots, static_asserted offsets |
| `render-image:273` | feature | home | `Tests::AddNeutralPostProcess`, `AddTemporalPostProcess` and `ExactSpecification` (`SceneRendererTestUtils.h:237-277`) |
| `render-image:535`, `render-image:542` | rule | home | Post passes take parameters by push constants or their own buffers, never new `FrameConstants` fields; a new post effect runs between the TAA resolve and the tone mapping, reads the frame's `PostSource`, is off in `AddNeutralPostProcess` and bit-identical at its neutral value |
| `new:27` | hands-on | home | Exercise (extend, make it yours): bars of a color the component sets, a second property with its range, its push constant and its feature-test value; the GPU test reads a bar's pixel, and the neutral value still renders bit-identically. The worked solution is a patch against the tutorial's last checkpoint. Evidence: the patch chain starts at the pin (`pipelines.md` §6.6); `StrataTests/src/Renderer/SceneRendererTestUtils.h:251` (`AddNeutralPostProcess`) |
| `new:28` | hands-on | home | Exercise (extend): give the letterbox a GPU stage of its own beside `GPU.Post`, read its time in `viewport.capture`'s `gpuMs`, and say when a stage of its own is worth its line in every profile. Evidence: `Strata/src/Strata/Renderer/GPUProfiler.cpp:44-66` (the stages registered in one order); `StrataEditor/src/Editor/EditorViewportCommands.cpp:1244` (`viewport.capture` reports `gpuMs` per stage) |
| `render-image:38` | feature | use | `PostSource` and `SelectPostSet` |
| `render-image:46` | feature | use | `DrawFullscreen` and `GetFullscreenPipeline`, for an effect drawn as a fragment pass |
| `render-image:545` | rule | use | Neutral settings render bit-identically |
| `render-image:426` | code | use | `AddNeutralPostProcess` (`StrataTests/src/Renderer/SceneRendererTestUtils.h:248-267`), one of the short snippets |
| `render-image:723` | term | use | Post source |
| `new:31` | feature | use | The chain's failure path in step 4: the new pass returns failure and sets `degraded` as the other passes do |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source; one test case written and run | `core/first-change` | must |
| Writing a GPU test: the shared `GPUContext`, the error count, pixel readback | `gpu/first-triangle` | must |
| Why images need post-processing; the post chain, `PostSource`, the fullscreen pass | `image/why-post` | must |
| Temporal anti-aliasing: the resolve that the effect follows | `image/taa` | must |
| The shader build: writing and registering a shader | `gpu/shaders` | must |
| Pipelines and binding: push constants | `gpu/binding` | must |
| Readback and GPU timestamps and stages | `gpu/readback-timing` | must |
| Reflection: registering a component's property | `world/reflection` | must |
| The feature test's minimum | `world/tutorial-component` | must |
| A feature that is off is invisible bit for bit | `gpu/frame-tour` | must |
| Neutral settings render bit-identically | `image/grading` | must |

**Starting state.** The engine's source at the pin, configured and built in Debug as `core/first-change` builds it, with
the unit tests and the GPU suites passing (the test of `gpu/first-triangle` runs). The page starts from no checkpoint of
an earlier tutorial: its patch chain starts at the pin and is not part of WindZone's. The tutorial's patch and its
stages are written with the page (`pipelines.md` §6.6). Every step changes code or runs CMake, the build and `ctest` in
a terminal; the effect is turned on in the editor's inspector.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
