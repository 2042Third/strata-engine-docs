# Brief: `draw/occlusion`

| Field | Value |
| --- | --- |
| Title | Occlusion culling |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `draw/gpu-driven`, `gpu/coordinates` |
| From | render-scene; the cascades' occlusion and the shadow cascade cache are `light/sun-shadows-1`'s, linked forward |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/occlusion` — Occlusion culling

**Covers.** The job: leave out what is in the frustum but hidden behind other geometry, without ever hiding something
visible and without drawing anything a frame late. The problem section teaches the approaches: hardware occlusion
queries (and their latency), software-rasterized occluders, reprojecting last frame's depth pyramid, and the two-phase
depth pyramid of Haar and Aaltonen and of Nanite, compared in a table. The idea of a conservative test: drawing too much
only costs time, hiding wrongly is a visible bug. The toy builds a farthest-depth pyramid of a small depth array on the
CPU and tests a rectangle against it.

The real code. The depth pyramid: level 0 half the depth buffer rounded up, every level the farthest depth (the
smallest, with reversed Z) of the 2x2 above it, the last row and column covering what lies past them, one sample of a
minimum sampler per 2x2 where the device has `samplerFilterMinmax` and four loads elsewhere; `GetPyramidFootprint`, the
finest level at which a box's screen rectangle spans at most 2x2 texels; `IsOccluded`, the box's nearest depth against
the pyramid. Two-phase view occlusion: the first phase draws what the view saw last frame into the prepass, a pyramid is
built from that depth, the second phase tests every proxy in the frustum and draws the newly visible ones in the same
frame; the two visibility bits per proxy that alternate by frame parity, cleared on a camera cut, a renderer's first
frame or another render scene. The rules: occlusion stays conservative; anything new that reads the view's depth runs
after the second phase's prepass; tests that count draws render a frame more first or turn occlusion off. Visibility
feedback still marks occluded proxies' assets as in view. What went wrong before: a minimum sampler's coordinates
normalized by the wrong size moved the footprints and hid visible objects (fixed in wave 8). What Strata does not do
here: portals. How it is tested: `GPU.SceneRenderer.Occlusion`, whose cases hide a box behind a wall and draw it in the
frame the wall goes or the camera steps aside, cover a screen rectangle that reaches the last row and column at odd and
even sizes, orthographic views, the cascades' casters and the pause of their culling, a box in plain view below a
window, and the pyramid's texels holding the farthest depth of what they cover. A second exercise cuts the camera in
that test's wall scene and traces where the cut clears the visibility bits. The page runs on a wall in front of many
boxes, with `occludedProxies` and `visibleProxies` before and after the wall is removed, and the exercise computes a
pyramid of a 7x5 depth buffer by hand. At the end the reader can build a pyramid level by hand, find a box's footprint,
and explain why nothing appears a frame late.

**Leaves out.**

- The cascades' occlusion and the shadow cascade cache → `light/sun-shadows-1`
- Reversed Z and depth precision → `gpu/coordinates`
- Mip chains → `assets/textures`
- The depth prepass and the passes that read the final depth → `gpu/frame-tour`
- The counting and write passes this page adds a phase to → `draw/gpu-driven`

**Fit.** `fits`: about 4,050 words against L (5,000). Two multi-part excerpts, three figures and three rules take the
most, with the case of what went wrong before; the page stands about 50 words above L's bottom.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:299` | concept | home | Occlusion culling with a hierarchical depth buffer: the approaches and the conservative test |
| `render-scene:138-140` | feature | home | Two-phase view occlusion, the depth pyramid and its wave 8 fix, the visibility bits |
| `render-scene:366` | code | home | `Strata/shaders/Scene/HZBBuild.comp.slang:41-83`: a conservative farthest-depth pyramid, with `GetPyramidFootprint` (`Strata/shaders/Include/Culling.slang:225-246`) and `IsOccluded` (`Strata/shaders/Scene/Cull.comp.slang:165-191`) |
| `render-scene:367` | code | home | `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:1028-1064`: the two-phase sequence, with `CullSecondPhase` (`Cull.comp.slang:516-547`) and the alternating bits |
| `render-scene:407` | figure | home | Two-phase occlusion over two frames: the bits by parity, phase 1, the pyramid, phase 2 |
| `render-scene:409` | figure | home | The pyramid's levels with odd sizes and the footprint of a box's rectangle; farthest is smallest |
| `render-scene:446` | figure | home | A wall in front of many boxes, with the occluded and visible counts before and after |
| `render-scene:484` | rule | home | Occlusion culling must stay conservative |
| `render-scene:487` | rule | home | Anything new that reads the view's depth runs after the second phase's prepass |
| `render-scene:505` | rule | home | Tests that count draws render a frame more first or turn occlusion off; tests of requests wait for feedback |
| `render-scene:539` | hands-on | home | A pyramid of a 7x5 depth buffer by hand, and the footprint of a rectangle touching the last column |
| `new:18` | hands-on | home | Exercise (done, with a "trace it yourself"): in a copy of the wall scene of `CheckOcclusion`, jump the camera more than 10 units (a camera cut) to a place where the wall still hides the box, and check that the frame after the cut draws the box (no history: `OccludedProxies` is 0) and the next frames leave it out; then find with a search where the cut clears the visibility bits (`m_ResetVisibility` set at the cut, the clear in `RunGPUCulling`); the solution is the test and the path. Evidence: `StrataTests/src/Renderer/GPUSceneOcclusionTests.cpp:74-120`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:3155-3159`; `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp:950-955` |
| `render-scene:609-612` | term | home | Occlusion culling; hierarchical Z-buffer (depth pyramid); two-phase occlusion culling; visibility parity |
| `render-scene:614` | term | home | Minimum sampler (`samplerFilterMinmax`) |
| `new:5` | not-done | home | No portals. Evidence: `git grep -ni "portal" 822a7a46 -- Strata/src` finds nothing |
| `render-scene:613` | term | use | The conservative test, met first in frustum culling |
| `render-scene:141` | feature | link | The cascades' occlusion, at `light/sun-shadows-1` |
| `render-scene:142` | feature | link | The shadow cascade cache, at `light/sun-shadows-1` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Reversed Z: near is 1, far is 0 | `gpu/coordinates` | must |
| Mip chains and their sizes | `assets/textures` | must |
| The depth prepass and the passes after it | `gpu/frame-tour` | must |
| Sampling, filtering and samplers | `gpu/how-a-gpu-frame-works` | must |
| The counting and write passes and the culling buckets | `draw/gpu-driven` | must |
| Shadow cascades | `light/sun-shadows-1` | helps |
| Visibility feedback and its latency | `draw/gpu-driven` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `hierarchical-z-buffer` | Hierarchical Z-buffer | HZB, depth pyramid |
| `min-max-sampler` | Min/max sampler | samplerFilterMinmax |
| `occlusion-culling` | Occlusion culling | - |
| `two-phase-occlusion-culling` | Two-phase occlusion culling | - |
| `visibility-parity` | Visibility parity | - |
