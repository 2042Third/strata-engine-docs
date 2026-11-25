# Brief: `indirect/gi-voxels`

| Field | Value |
| --- | --- |
| Title | Global illumination I: a voxel copy of the world |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `indirect/seam`, `gpu/compute`, `gpu/geometry-pool`, `draw/render-scene`, `indirect/problem` |
| From | render-indirect ch. 9; 1.8 (the voxel clipmap, voxelizing the geometry pool's static submeshes, fill, finalize, budgets and anchors) · W8 |
| Unit | `plan/allocation/indirect.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `indirect/gi-voxels` — Global illumination I: a voxel copy of the world

**Covers.** The job: the first half of Strata's experimental global illumination, a voxel copy of the static world
around the camera that the cascades of `indirect/gi-cascades` march. The page first shows the whole at a glance: the
scene asks with Post Process `GlobalIllumination` (off by default; `GlobalIlluminationIntensity` 0 to 4, with an
inactive reason), the quality row `GlobalIllumination` (Off at Low and Medium, Low and High layouts), the GPU stage
`GPU.RadianceCascades` between `GPU.AO` and `GPU.Reflections`, and the overview diagram from the geometry pool to the
forward gather. The opening picture is GI off and on in the Cornell box; the voxels view shows what this page builds.

The problem section is one paragraph that links `indirect/problem`'s families. The concept is taught from zero:
voxelization by a conservative triangle-box test (Akenine-Moller's separating axes), buffer atomics, solid fill by
counting windings along columns, two-sided voxels, clipmap levels each twice the size of the one before, toroidal
addressing so that a scroll writes only the slabs that entered, anchors so that the same scene gives the same bits
wherever the camera is, and budgets per frame. The layout comes from first principles in `ComputeLayout`: High has four
voxel levels of 128x64x128 from 10 cm and four cascades from 0.5 m; Low three levels of 64x32x64 from 20 cm and three
cascades from 1 m; the field's extent; High bounces on and Low once (`indirect/gi-cascades` says why); the memory per
view that runs GI, at any resolution, 146.4 MiB at High and 22.6 MiB at Low, so two views that run GI hold it twice
(exercise E9 computes it).

The contract: anchors for voxel coordinates (worlds stay within 20 km); walls thicker than two voxels (20 cm at High,
40 cm at Low) or they turn two-sided and dark from both sides; GI traces world data, never the screen (`indirect/problem`).
A toy version is exercise E10: the triangle-box test on the CPU, voxelizing a box against `Tests::ReferenceVoxels`. The
real code: the CPU clipmap (`VoxelClipmap`: per level a camera-centered window snapped to 4-voxel steps, toroidal
storage, the region queue of changes, slabs and whole windows, budgets of 500,000 and 4 million triangles a frame) and
its arithmetic (`GetVoxelIndex`, `GetWindowMinimum`, `GetTexel`, `GetScrollSlabs`, `GetAnchorVoxel`); what enters the
voxels (indexed opaque and alpha-masked submeshes of the static arena, a level of detail within half a voxel, material
means; movers wait 30 frames, `indirect/gi-limits`); the GPU passes `VoxelTriangles` (a thread per triangle),
`VoxelTiles` (large triangles, indirect), `VoxelFill` (closed meshes become solid) and `VoxelFinalize` (material,
emission in RGB9E5, normal, two-sided detection); the closed-mesh test (every directed edge has one opposite). The
voxel classes diagram shows a surface, a solid interior, a two-sided thin wall and an alpha-masked partial voxel.

Alternatives: sparse voxel octrees (SVOGI), voxel cone tracing on clipmaps (VXGI), signed distance fields (Lumen),
DDGI's ray-traced probes. Tests: `Renderer.GlobalIlluminationLayout` ("Memory adds up"), `Renderer.VoxelClipmap`,
`Renderer.Mesh` ("Closed meshes are found"), and a trace of one batch through the four voxel passes. Two errata: a stale
memory comment and the cascades' direction counts. Figures: Low against High as a sweep, the clipmap and the voxel
classes as diagrams, the overview diagram, and the voxels view and GI off and on, both homed on `indirect/gi-cascades`.
The reader can explain how the world becomes voxels and change the voxelizer safely.

**Leaves out.**

- The families of GI and why Strata traces the world → `indirect/problem`
- Light injection, the cascades, the field and the GI debug views → `indirect/gi-cascades`
- Moving and skinned objects, local lights and the other limits → `indirect/gi-limits`
- The geometry pool's arenas and submeshes → `gpu/geometry-pool`
- The render scene's proxies and change logs → `draw/render-scene`
- The 20 km limit of worlds → `worlds/why-streaming`
- Turning GI on in a game → `make/gi`

**Fit.** `fits`: about 6,050 words against L (5,000). The GI at a glance, the concept of voxelization and clipmaps in
eight parts, three excerpts and the four GPU passes take the most words; about 450 words remain below L's top. Phase B
must look again at: which GI batches landed after the pin (`render-indirect:698`), the files the survey did not read in
full (`VoxelClipmap.cpp`, the bodies of `VoxelTriangles`, `VoxelTiles`, `VoxelFill`, `VoxelFinalize`, most of
`SceneRendererGlobalIllumination.cpp`: `render-indirect:687`), the spec's "Review corrections" (`render-indirect:695`),
the layout's numbers and the two errata, the memory per view and whether Low still bounces once (`render-indirect:163`,
`:164`).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:309` | concept | home | Voxelization and clipmaps: conservative triangle-box overlap, atomics, solid fill by winding, two-sided voxels, levels, toroidal addressing and scrolling, anchors, budgets; errors: recomputing the volume when the camera moves, floating-point origins far from zero |
| `render-indirect:162` | feature | home | The scene's ask: `PostProcessComponent::GlobalIllumination` (off) and `GlobalIlluminationIntensity` (1, 0 to 4, with an inactive reason) |
| `render-indirect:163` | feature | home | The quality row `Renderer.Quality.GlobalIllumination`: Off, Low, High (Off at Low and Medium); High bounces on and Low once (`GlobalIlluminationLayout::Bounces`, taught on `indirect/gi-cascades`) |
| `render-indirect:164` | feature | home | The layout of Low and High and its memory (146.4 MiB and 22.6 MiB) per view that runs GI, at any resolution (`Strata/src/Strata/Renderer/RendererQuality.h:166-168`; `Docs/DeveloperGuide.md:4975`); the direction counts per cascade as the erratum `new:13` states them |
| `render-indirect:165` | feature | home | The CPU clipmap: windows snapped to 4-voxel steps, toroidal storage, anchors, the region queue, budgets |
| `render-indirect:166` | feature | home | What enters the voxels: static indexed opaque and alpha-masked submeshes, LOD within half a voxel, material means; movers excluded for 30 frames |
| `render-indirect:167` | feature | home | The GPU voxelization: `VoxelTriangles`, `VoxelTiles`, `VoxelFill`, `VoxelFinalize`, dispatched in `RecordGlobalIllumination` |
| `render-indirect:168` | feature | home | The closed-mesh test (`MeshUtils::IsClosed`, `Mesh::IsClosed`) |
| `render-indirect:183` | feature | home | The GPU stage `GPU.RadianceCascades`, after `GPU.AO` and before `GPU.Reflections` |
| `render-indirect:361` | code | home | `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:147-192`: a layout from first principles (voxel levels, cascades with spacing x2, directions x4, intervals x4, the field's extent) |
| `render-indirect:362` | code | home | `Strata/shaders/Include/Voxelize.slang:160-196`: Akenine-Moller's triangle-box overlap by separating axes |
| `new:14` | code | home | `Strata/src/Strata/Renderer/GlobalIlluminationLayout.h:142-167`: the clipmap's arithmetic: voxel index, window minimum, toroidal texel, scroll slabs, anchors, and the camera-independent voxel coordinate |
| `render-indirect:405` | figure | home | Diagram: the GI overview from the geometry pool to the forward gather, the previous field feeding the injection |
| `render-indirect:407` | figure | home | Diagram: the clipmap levels (10, 20, 40, 80 cm), a scroll writing only the slabs that entered, the anchor cells |
| `render-indirect:409` | figure | home | Diagram: the voxel classes (surface, solid interior, two-sided thin wall, alpha-masked partial) |
| `render-indirect:457` | figure | home | Sweep: the quality row's Low against High in the same room: the shot `lookdev.room` at Low and High, with the Post Process's `GlobalIllumination` set as the Setup of `lookdev.sunroom.lit.gi` sets it, since the room's own scene does not ask for GI (`Tools/LookDev/Shots.json:28`, `:141`; `Tools/LookDev/LookDevScene.json:22`) |
| `render-indirect:513` | rule | home | Anchors for voxel coordinates: the same scene voxelizes to the same bits wherever the camera is; worlds stay within 20 km |
| `render-indirect:517` | rule | home | Walls must be thicker than two voxels (20 cm High, 40 cm Low), or they turn two-sided and dark from both sides |
| `render-indirect:554` | hands-on | home | E9: compute the Low layout's memory by hand and check "Memory adds up" |
| `render-indirect:555` | hands-on | home | E10: the CPU triangle-box test, a voxelized box against `Tests::ReferenceVoxels` (the toy version) |
| `new:26` | hands-on | home | Exercise (trace it yourself, R32, D27): one batch of the frame's regions followed from the CPU's frame to the voxels: `PrepareGlobalIllumination` builds the frame with the clipmap, and `RecordGlobalIllumination` clears the scratch buffer, dispatches `VoxelTriangles` in parts of at most `c_MaxDispatchGroups` groups, `VoxelTiles` as an indirect dispatch whose group count `VoxelTriangles` wrote, then `VoxelFill` per column and `VoxelFinalize` per voxel, with a barrier after each; the solution names the lines and says why the tiles' dispatch is indirect. Evidence: `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp:514-524`, `:639-644`, `:780-830` |
| `new:12` | erratum | home | The comment at `Strata/src/Strata/Renderer/RendererQuality.h:166-168` gives 18 MiB at Low and 111 MiB at High; `GetMemory` gives 23,659,120 and 153,469,552 bytes (22.6 and 146.4 MiB). Evidence: `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:153`, `:167`; `Docs/DeveloperGuide.md:4975-4976` |
| `new:13` | erratum | home | `Docs/DeveloperGuide.md:4974` and the inventory (`render-indirect:164`, figure `render-indirect:411`) give the cascades 16 to 1,024 directions; at the pin cascade 0 marches cascade 1's 64 directions, so High's cascades have 64, 64, 256 and 1,024 and Low's 64, 64 and 256. Evidence: `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:167-169`; `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:102-105`, `:127-129` |
| `render-indirect:624` | term | home | Voxel and voxelization, two entries |
| `render-indirect:625` | term | home | Clipmap |
| `render-indirect:626` | term | home | Toroidal addressing |
| `render-indirect:627` | term | home | Slab, region, brick and anchor, four entries |
| `render-indirect:628` | term | home | Triangle-box overlap (Akenine-Moller) |
| `render-indirect:629` | term | home | Winding and solid fill, two entries |
| `render-indirect:630` | term | home | Closed mesh |
| `render-indirect:631` | term | home | Two-sided voxel |
| `render-indirect:632` | term | home | RGB9E5 |
| `render-indirect:455` | figure | use | GI off and on in the Cornell box as the opening picture; its home is `indirect/gi-cascades` |
| `render-indirect:456` | figure | use | The `voxels` view of the sun room (`lookdev.sunroom.view.voxels`); its home is `indirect/gi-cascades` |
| `render-indirect:508` | rule | use | GI traces world data, never the screen; the decision's home is `indirect/problem` |
| `render-indirect:515` | rule | link | Movers stay out of the voxels for 30 frames; taught on `indirect/gi-limits` |
| `render-indirect:303` | concept | link | The families of GI, taught on `indirect/problem` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The families of GI and the decision to trace world data | `indirect/problem` | must |
| The geometry pool's static arena and submeshes | `gpu/geometry-pool` | must |
| Render-scene proxies, their records and change logs | `draw/render-scene` | must |
| Compute atomics and indirect dispatches | `gpu/compute` | must |
| Separating axes and triangle-box tests | `basics/math-geometry` | must |
| Floating point far from the origin | `basics/numbers` | must |
| Levels of detail of a mesh | `draw/lod` | helps |
| Where the field joins the shading | `indirect/seam` | must |
| A material's base color, emission and their maps | `light/materials` | must |
| Inactive reasons (`SetInactiveReason`): a property that another property turns off | `world/reflection` | helps |
| Quality rows and their presets | `image/quality-settings` | helps |
| The 20 km limit of worlds | `worlds/why-streaming` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `clipmap` | Clipmap | - |
| `closed-mesh` | Closed mesh | - |
| `rgb9e5` | RGB9E5 | - |
| `toroidal-addressing` | Toroidal addressing | - |
| `triangle-box-overlap-akenine-moller` | Triangle-box overlap (Akenine-Moller) | - |
| `two-sided-voxel` | Two-sided voxel | - |
| `voxel` | Voxel | - |
| `voxelization` | voxelization | - |
