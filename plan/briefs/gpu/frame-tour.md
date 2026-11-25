# Brief: `gpu/frame-tour`

| Field | Value |
| --- | --- |
| Title | A frame of the scene renderer, pass by pass |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `gpu/coordinates`, `gpu/binding`, `gpu/geometry-pool` |
| From | render-core; the map every rendering page links back to; the renderer's half of the frame map; home of forward, deferred and visibility buffers, the depth prepass, `EQUAL` and invariant positions, and of the rule that a feature turned off is invisible bit for bit and costs nothing · W8r (the list of passes and the statistics they report) |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/frame-tour` — A frame of the scene renderer, pass by pass

**Covers.** The job: what `SceneRenderer::Render` does with a scene and a camera, pass by pass, as the map every
rendering page links back to. The problem and the approaches: forward, forward with clustered lights, deferred with a
G-buffer, visibility buffers, with a table of their costs; Strata's choice, clustered forward with a depth, normal and
entity-ID prepass and an opaque pass that tests depth for equality, and why that needs positions identical to the bit
(the invariant decoration). The engine's documents give no reason for forward over deferred, so the page presents the
choice as a trade-off and names no motive. The map: the passes as a vertical timeline by GPU stage, with the targets
each one reads and
writes, and how the frame's code is split over files. The contract: the `SceneRenderer` API (output, HDR, depth, normal
and entity-ID textures; `SetViewportSize`, checked and released through `ReleaseDeferred`; `SetQuality`; stats; history
and exposure resets), the target framebuffer's rules (the viewport's size, non-sRGB UNORM), `SceneRenderOptions`, the
callers with `GameRenderer` as the simplest, the `SceneCamera` each caller passes (taught on `gpu/coordinates`), and the
rule that a feature switched off is invisible bit for bit and costs nothing (no target made, no stage timed, a dummy
bound). The toy is a frame of prepass, forward pass and one post pass in about 70 lines.

The real frame is walked in order as a trimmed outline: the targets checked; `RenderScene::Sync` and extraction; the
GPU mirror; lights, resolved assets, draw arguments and frame constants with the relative view and the jittered
projection; the command list and its timer; setup; GPU culling; light culling and clusters; aerial perspective; shadows;
clears and the prepass; the sun's screen-space shadow mask; ambient occlusion; GI voxels; reflections; the opaque pass;
the sky; the scene color copy and the transparents; TAA; depth of field; motion blur; exposure, bloom, flares, color
lookup, tone mapping and anti-aliasing; overlays; close and execute. Each step names the page that teaches its feature
and the stage it is timed in; the light passes are timed in the stage before them, as the code has it, not as the
inventories say. The HDR target and the display transform are taught here at the foundation level, with the
intermediate targets as figures (the words HDR, tone mapping, sRGB encoding and half float each said in one sentence and
linked to their homes). A section "Looking inside a frame" matches a capture's markers to the steps. What Strata does
not do here (particles, trails and decals; a render graph; a second view: split-screen, picture-in-picture or a camera
that renders into a texture), alternatives, tests and changing it safely (a new pass: its stage, its slot, its dummy,
invisible when off) close the page; the exercise traces one pass from its marker to its stage and its switch.

**Leaves out.**

- The lights a pass shades with → `light/lights`
- The sun's shadows and the screen-space mask → `light/sun-shadows-1`
- Ambient occlusion → `indirect/ao`
- Screen-space reflections → `indirect/ssr`
- Global illumination's voxels → `indirect/gi-voxels`
- The post chain and its passes → `image/why-post`
- The render scene, extraction and draws → `draw/render-scene`
- GPU culling and the two-phase prepass → `draw/gpu-driven`
- Tiled against clustered light culling → `light/many-lights`
- GPU timestamps and stages → `gpu/readback-timing`
- Overlays in detail → `gpu/debug-drawing`
- Jitter on the frame's camera copy → `image/taa`
- `SanitizeHDR` and the half-float range → `light/brdf`
- The renderer's switches and statistics as tables → `reference/renderer`

**Fit.** `fits`: about 7,500 words against XL (8,000). Twenty-four steps at about 80 words each, the outline from three
ranges, the forward and deferred comparison and the HDR target take the most words. W8r: phase B must read again the
list of passes (local light shadows, area lights, the GI's later stages) and the statistics they report, and the page's
entries of "What Strata does not do": particles, trails and decals; a render graph or frame graph; a second view.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:409` | concept | home | Forward with a depth prepass, against forward+, deferred and visibility buffers; `EQUAL` and identical positions; the mistake of changing the prepass's vertex math alone |
| `render-core:414` | concept | home | HDR rendering and the display transform at the foundation level: the RGBA16F target, tone mapping into UNORM, why the engine encodes sRGB itself |
| `render-indirect:329` | concept | home | The rule of the renderer: a feature that is off is invisible bit for bit and costs nothing (`book.md`'s design decision), checked by tests; the mistake of a uniform branch that changes the default path's rounding. Its places at the pin: `AGENTS.md:393, 399-401, 405-406`; `Docs/DeveloperGuide.md:4968, 5404, 5762` |
| `render-direct:822` | open | home | Settled: the documents give no reason for forward over deferred (no match for "deferred shading", "G-buffer" or "forward rendering" in `Docs/DeveloperGuide.md`, `Docs/Architecture.md`, `Docs/Roadmap.md` and `AGENTS.md`); the page states the trade-off without a motive |
| `render-core:155-178` | feature | home | The 24 steps of `RenderFrame` in the code's order, each with its stage; the light passes are timed in the stage before them (`GPU.Cull` on the GPU-driven path, `GPU.Setup` otherwise: `SceneRenderer.cpp:3360-3378`), not always `GPU.Cull` as the inventory's table says |
| `render-core:180` | feature | home | The `SceneRenderer` API, `SetViewportSize`, `SetQuality`, stats, resets, temporal jitter named, output target rules, `SceneRenderOptions` |
| `render-core:187` | feature | home | The frame's code split over the `SceneRenderer*.cpp` files |
| `render-core:193` | feature | home | `GameRenderer` as the simplest caller of `SceneRenderer::Render` |
| `render-core:467` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2901-3735`: the frame as timed passes, shown as a trimmed outline from lines 3283-3289, 3360-3420 and 3489-3541 |
| `render-core:509` | figure | home | The pass graph: the steps as a timeline colored by stage, with the targets read and written |
| `render-core:525` | figure | home | The intermediate targets of one view: depth, normals, entity IDs, HDR before tone mapping, output |
| `render-core:837` | open | home | No debug view shows raw depth, normals or entity IDs: figure 525 waits for a capture addition (`pipelines.md` §11) and shows a diagram until it ships |
| `render-core:592` | rule | home | The prepass and the forward pass produce identical positions; `Mesh.vert` is decorated `Invariant` by the shader tool |
| `render-core:604` | rule | home | A target framebuffer has the viewport's size and a non-sRGB UNORM format |
| `render-core:724`, `render-core:733`, `render-core:734` | term | home | Invariant position; depth prepass; forward and deferred, with clustered shading linked to its one entry on `light/many-lights` (`render-direct:712`) |
| `render-core:772` | term | home | Entity ID buffer |
| `render-core:754`, `render-core:757` | term | link | HDR, tone mapping and sRGB encoding (homed on `image/why-post`, tone mapping on `image/tone-mapping`); RGBA16F and half float (homed on `basics/color`): each said in one sentence with a link |
| `render-scene:606`, `render-scene:607` | term | home | `EQUAL` depth test; depth prepass (one entry with `render-core:733`) |
| `build-test:648` | term | home | Invariant position, as the build's glossary words it (what the prepass's `EQUAL` test needs); one entry with `render-core:724` |
| `render-scene:479` | rule | home | The prepass and the forward pass produce identical positions, the same rule as `render-core:592`, with LOD fades in both passes |
| `render-direct:204` | feature | home | The stages in frame order as the lighting part lists them, merged into the steps; the same slip as the inventory's step 7 (the light passes are in `GPU.Setup` on the CPU path) |
| `new:15` | not-done | home | No particles, trails or decals. Evidence: `git grep -niE -e particle -e decal 822a7a46 -- Strata/src Strata/shaders` finds nothing; `git grep -niwE "trails?"` there finds only the anti-aliasing tooltips of `Strata/src/Strata/Renderer/RendererComponents.cpp:508, 519, 523`; `Docs/Roadmap.md:1690` (run again at the pin) |
| `new:16` | not-done | home | No render graph or frame graph: `RenderFrame` orders the passes by hand. Evidence: `git grep -n -e RenderGraph -e FrameGraph 822a7a46 -- Strata/src` finds nothing; `Strata/src/Strata/Renderer/SceneRenderer.cpp:2901` (run again at the pin) |
| `new:45` | not-done | home | No second view: no split-screen, no picture-in-picture, no camera that renders into a texture for a mirror or a minimap; a game is drawn from one camera, the first active entity whose Camera is Primary in hierarchy order (`make/characters-cameras` tells makers how to switch). Evidence: `Strata/src/Strata/Scene/Scene.cpp:867-879`; `Strata/src/Strata/Runtime/GameRenderer.cpp:114-126`; `git grep -niE -e "split-?screen" -e "render-?to-?texture" -e "picture-in-picture" -e "RenderTexture" 822a7a46 -- Strata/src StrataScriptCore Docs` finds nothing (run again at the pin) |
| `new:46` | erratum | home | `plan/inventory/render-core.md:162` and `plan/inventory/render-direct.md:205` time light culling and the light clusters in `GPU.Cull` (process.md's table, kind `inventory`): `GPU.Cull` starts only on GPU-driven frames, and light culling and the clusters are recorded after it, so they are timed in `GPU.Cull` on GPU-driven frames and in `GPU.Setup` on frames of the CPU path. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3289, 3343, 3360, 3365-3377` |
| `new:47` | hands-on | home | Exercise ("trace it yourself"): one pass from its marker to its stage and its switch: find the marker `Aerial` in `RenderFrame`, the stage its time goes to (`gpuTimer.Next`), the switch that skips it (`m_AerialFrame`) and the page that teaches the feature, then render a scene without the atmosphere on the source build, with a breakpoint there, and see the step skipped. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3379-3382`; `Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp:370` |
| `new:33` | feature | use | `SceneCamera`, as the API contract's camera that every caller passes |
| `render-core:656` | hands-on | use | A capture's markers matched to the steps, in "Looking inside a frame" |
| `render-core:94` | feature | use | Pipelines by key, as each pass picks its pipeline |
| `render-core:212` | feature | link | The GPU stages the steps are timed in |
| `render-core:774` | term | link | Jitter, named in the frame constants |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Clip space, reversed Z and the camera | `gpu/coordinates` | must |
| Pipelines by key, binding layouts and the ledger | `gpu/binding` | must |
| Meshes in the pool, instances and the draw list | `gpu/geometry-pool` | must |
| Compute shaders and dispatches | `gpu/compute` | must |
| Resources and deferred release | `gpu/resources-lifetimes` | must |
| Color: linear and sRGB values, the half-float range | `basics/color` | must |
| GPU stages | `gpu/readback-timing` | helps |
| The render scene's proxies | `draw/render-scene` | helps |
| Lights and shadows as features | `light/lights` | helps |
| The post chain | `image/why-post` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `clustered-forward` | clustered forward | - |
| `deferred` | deferred | - |
| `depth-prepass` | Depth prepass | EQUAL depth test |
| `entity-id-buffer` | Entity ID buffer | - |
| `forward` | Forward | - |
| `invariant-position` | Invariant position | Invariant (position) |
