# Brief: `light/shadow-basics`

| Field | Value |
| --- | --- |
| Title | Shadow mapping from first principles |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `light/lights`, `gpu/coordinates`, `basics/math-projection` |
| From | render-direct ch. 6 (rendering and sampling a shadow map, reversed-Z comparisons, acne and the four biases, pancaking, alpha-masked casters) |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/shadow-basics` — Shadow mapping from first principles

**Covers.** The problem as the reader meets it: is a point visible from the light? The page shows a scene with and
without the sun's shadow, then acne on a surface the sun grazes. The naive answers and where they break: a ray per pixel
per light (cost), shadow volumes (stencil and fill rate). The idea: render depth from the light, then compare a point's
depth in light space with the stored one (the shadow-mapping diagram): light space, orthographic projections for the sun
and perspective ones for lamps, reversed-Z (nearer to the light is larger), comparison samplers and percentage-closer
filtering. What goes wrong: acne and peter-panning. The four biases: the rasterizer's slope bias, a depth bias of one
texel, a normal offset of 1.5 texels measured in texels, and a receiver-plane bias computed from the inverse transpose
of the light's projection, not from screen derivatives (which are wrong at silhouettes and depend on how the GPU groups
pixels). Pancaking: casters between the light and the near plane are flattened onto it instead of clipped, in two lines
of a vertex shader. Alpha-masked casters discard their cut-out texels in the shadow pass; transparent surfaces (Blend
and glass) cast no shadow at all, into the cascades or the local atlas, on both paths, so there are no partial or
colored shadows. The approaches engines use (shadow volumes, shadow maps, ray-traced shadows) end in a table. Strata's
choice: reversed-Z D32 maps, a hardware comparison sampler, texel-relative biases and the receiver plane; the bridge to
the sun's cascades and to the lamps' atlas. The common mistakes: a constant bias in world units, screen derivatives for
the receiver plane. Figures: the diagram, and acne with both biases at 0 against the defaults at a low sun, with a crop.
Exercises: predict, then run, the shadows of a masked fence at two cutoffs and of a glass pane; a sketch of a shadow map
over a sloped line that counts acne with each bias off and on. Afterwards the reader can explain a shadow map, its
comparison and its biases, and set the biases of a light.

**Leaves out.**

- The sun's cascades → `light/sun-shadows-1`
- Soft shadows and the filter → `light/sun-shadows-2`
- Shadows of point and spot lights → `light/local-shadows`
- Reversed-Z as Strata's depth convention → `gpu/coordinates`
- Sun shadows in a game → `make/lighting`

**Fit.** `fits`: about 4,750 words against L (5,000). The shadow-mapping idea and the four biases, with two short
excerpts, take the most; the two exercises add about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:116` | feature | home | Pancaking: casters before the near plane flattened onto it |
| `render-direct:122` | feature | home | The biases: slope, depth (one texel), normal offset (1.5 texels), receiver plane from the inverse transpose |
| `render-direct:129` | feature | home | Alpha-masked casters: cut-out texels discarded in the shadow pass |
| `new:40` | rule | home | Opaque and masked surfaces cast shadows; transparent ones (Blend, and glass, which is always transparent) never do, into the cascades or the local atlas, on the CPU and the GPU-driven path: no partial or colored shadows (about 80 words). Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:58`, `:1203-1205`; `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp:730-731`; `Strata/shaders/Scene/Cull.comp.slang:314-325` |
| `render-direct:361` | concept | home | Shadow mapping: light space, projections, reversed-Z, comparison samplers, acne, the biases, pancaking; the mistakes |
| `render-direct:456` | code | home | `Strata/shaders/Include/Shadows.slang:94-111`: the receiver-plane depth bias from the projection's cofactor |
| `render-direct:459` | code | home | `Strata/shaders/Scene/ShadowMesh.vert.slang:47-51`: pancaking in two lines (the inventory's 46-51 starts at the preprocessor line) |
| `render-direct:498` | figure | home | Diagram: the light's view, the depth comparison, acne and the biases, pancaking |
| `render-direct:547` | figure | home | Acne with `ShadowBias` and `ShadowNormalBias` at 0 against the defaults at a grazing sun (`ow.lowsun`), with a crop |
| `render-direct:715` | term | home | Shadow map |
| `render-direct:717-720` | term | home | Comparison sampler and PCF; shadow acne and peter-panning; depth, slope, normal-offset and receiver-plane bias; pancaking (each a glossary entry) |
| `new:41` | hands-on | home | Exercises: predict, then run: a fence with an alpha-masked material at `AlphaCutoff` 0.1 and 0.9, and a glass pane beside it, under a low sun (which shadows change, and which never appears); a sketch of a shadow map over a sloped line that counts the acne texels with the depth, slope and normal-offset biases off and on, and shows peter-panning when they are too large. Evidence: `Strata/shaders/Scene/ShadowMask.frag.slang:6`, `:15-16`; `Strata/src/Strata/Renderer/MaterialData.cpp:16-21`; `Strata/src/Strata/Renderer/RendererComponents.h:28-29`; `Strata/shaders/Include/Shadows.slang:94-111` |
| `render-direct:716` | term | link | Reversed-Z; its home is `basics/math-projection`, and Strata's depth convention is `gpu/coordinates`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Orthographic and perspective projections, depth | `basics/math-projection` | must |
| Reversed-Z and Strata's clip space | `gpu/coordinates` | must |
| Depth buffers and depth tests | `gpu/how-a-gpu-frame-works` | must |
| The sun, points and spots | `light/lights` | must |
| Bilinear filtering | `basics/signals` | must |
| The Mask alpha mode | `light/materials` | must |
| Normals through the inverse transpose | `basics/math-bases` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `comparison-sampler` | Comparison sampler | - |
| `pancaking` | Pancaking | - |
| `pcf` | PCF | - |
| `peter-panning` | peter-panning | - |
| `shadow-acne` | Shadow acne | - |
| `shadow-map` | Shadow map | - |
