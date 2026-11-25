# Brief: `draw/bounds-culling`

| Field | Value |
| --- | --- |
| Title | Bounding volumes, frustums and the spatial index |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `draw/render-scene`, `basics/math-geometry`, `core/math` |
| From | render-scene; the CPU path, taught first; home of frustum and box tests (plane extraction, the positive vertex, `AABB::Transformed`) and of the screen fraction (`GetScreenFraction`, a section "How big does it look?"); sun shadow casters are `light/sun-shadows-1`'s |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/bounds-culling` — Bounding volumes, frustums and the spatial index

**Covers.** The CPU path, taught first. The job: find the proxies the camera can see, exactly and in time that follows
what is visible, and say how large each looks on screen. The page carries the full section "The problem and how engines
solve it": a per-object test of every proxy is linear in the scene, and engines answer with bounding volume
hierarchies, octrees and loose octrees, uniform and loose grids, and hashing, compared in a table. Then the ideas in
order. Bounding volumes and their transforms: spheres, axis-aligned and oriented boxes, and why transforming only the
minimum and maximum corners is wrong under rotation (`AABB::Transformed`). Frustum culling: six planes extracted from the
view-projection matrix, the positive vertex test of a box against a plane, the three answers inside, intersecting and
outside, and why the test is conservative (a box near a corner passes while it is outside). Strata's `Frustum` type does
this: the Gribb and Hartmann extraction for depth from 0 to 1, where the depth-0 plane is the far plane of reversed Z, an
infinite far plane that comes out degenerate and never culls, and the point, sphere and box tests; a two-dimensional
sketch shows the planes and a box's positive vertex. The toy: a brute-force culler over a list of boxes, then a uniform
grid.

The real code: the positive and negative vertex tests (`SpatialIndex.cpp:56-107`); Strata's loose two-level grid, with
cells of 32 units keyed by the box's centre, cell bounds that are the union of their objects, blocks of 8x8x8 cells and
a separate list for objects longer than four cells; queries that take wholly inside blocks and cells whole and test
straddlers one by one, so the result equals a brute-force scan; constant-time edits and the lazy shrink in `Refresh`;
`CullView`, which queries the frustum, computes each visible proxy's screen fraction in parallel chunks and merges the
marks in chunk order, and the prefetch sphere. The index has another reader: the editor's raycast asks it for the boxes
along a ray, a thin prism of six planes, as the broad phase before its exact tests. A section "How big does it look?"
teaches the screen fraction (the projected bounding-sphere diameter over the viewport height, perspective and
orthographic), which level of detail, request priority, size culling and texture streaming all use, and size culling
with the quality row "Smallest drawn size". Why a grid and not a BVH: proxies move every frame, and a cell move costs
less than a refit. How it is tested: `SpatialIndexTests`, with the reader's own test that compares a sphere query with
brute force, and a timing of brute force against the grid; the "trace it yourself" exercise follows two boxes through
the query. The page runs on a camera over a field of boxes. At the end the reader can extract a frustum's planes, test a
box against them, and explain why the grid's answer is exact.

**Leaves out.**

- The mathematics of planes, boxes and intersection tests → `basics/math-geometry`
- The `AABB` type → `core/math`
- The rest of the editor's raycast → `editor/placement`
- Finding the sun's shadow casters → `light/sun-shadows-1`
- The same tests on the GPU → `draw/gpu-driven`
- What is hidden behind other objects → `draw/occlusion`
- Choosing a level of detail from the screen fraction → `draw/lod`

**Fit.** `fits`: about 5,550 words against L (5,000). The full section on spatial structures and three concepts take
the most, then five excerpts (`Frustum.cpp` and `AABB.cpp` quoted here among them) and three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:243` | concept | home | Spatial acceleration structures, compared; why a loose grid for moving proxies |
| `render-scene:233` | concept | home | Bounding volumes and their transforms; `AABB::Transformed` and the corner mistake |
| `render-scene:238` | concept | home | Frustum culling: plane extraction, the positive vertex test, conservative results |
| `render-scene:248` | concept | home | The screen fraction, the section "How big does it look?" |
| `render-scene:56-60` | feature | home | The loose two-level grid, exact queries, constant-time edits and lazy shrink, `CullView`, size culling |
| `render-scene:98` | feature | home | `LODSelection::GetScreenFraction` for perspective and orthographic cameras |
| `render-scene:347` | code | home | `Strata/src/Strata/Renderer/SpatialIndex.cpp:56-107`: the positive and negative vertex tests; inside, intersecting, outside |
| `render-scene:348` | code | home | `Strata/src/Strata/Renderer/SpatialIndex.cpp:406-438`: the query that takes whole cells and tests straddlers (with `Update`, 303-345) |
| `render-scene:349` | code | home | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:249-328`: `CullView` and `MarkVisibleProxies`, chunks merged in order |
| `render-scene:397` | figure | home | The loose grid in two dimensions, a block, the large-object list, a frustum classifying cells |
| `render-scene:524` | hands-on | home | Write a spatial-index test that compares a sphere query with brute force |
| `render-scene:526` | hands-on | home | Brute force against the loose grid on 100,000 random boxes |
| `new:12` | hands-on | home | Exercise ("trace it yourself"): with a breakpoint in `SpatialIndex::Query`, follow two boxes of the page's field from `CullView` through `QueryFrustum` to the visible list: one in a cell wholly inside the frustum, taken with its cell, and one in a straddling cell, tested alone by `Frustum::IsAABBVisible`; the solution names each function and the overlap each test returned. Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:249-256`, `Strata/src/Strata/Renderer/SpatialIndex.cpp:406-444` |
| `render-scene:595-599` | term | home | Positive vertex test; loose grid; spatial index; screen fraction; size culling |
| `render-scene:613` | term | home | Conservative test |
| `foundation:144` | feature | home | `Frustum` (`Strata/src/Strata/Math/Frustum.cpp:12-73`): Gribb and Hartmann extraction for depth 0 to 1, the depth-0 plane as reversed Z's far plane, a degenerate infinite far plane that never culls; point, sphere and box (positive vertex) tests |
| `foundation:425` | figure | home | Its first sketch: the frustum's planes and a box's positive vertex in two dimensions (the second, the ray from NDC, is drawn on `core/math`) |
| `foundation:636` | term | home | Frustum culling, as Strata tests it; the frustum as a volume is `basics/math-geometry`'s (`render-scene:593`) |
| `editor-core:726` | term | home | Spatial index: one glossary entry with `render-scene:597`; the editor's raycast queries the index with a thin prism of planes (`StrataEditor/src/Editor/SceneRaycast.cpp:116-132`). The word "broad phase" is linked to its home, `physics:499` on `physics/collision-detection` (the merge "Broad phase") |
| `render-scene:79` | feature | use | Extraction in chunks of 2,048 proxies, merged in chunk order |
| `render-scene:183` | feature | use | The quality row "Smallest drawn size (pixels)" |
| `foundation:370` | code | use | `Strata/src/Strata/Math/Frustum.cpp:12-35`, with lines 57-73: the Gribb and Hartmann plane extraction for depth 0 to 1 and the positive-vertex box test, quoted here (book.md's row of frustum and box tests); the item's home row, its reversed-Z projections, is on `core/math` |
| `foundation:373` | code | use | `Strata/src/Strata/Math/AABB.cpp:7-25`: `AABB::Transformed` by Arvo's method, the answer to the corner mistake, quoted here (book.md's row of frustum and box tests); the item's home row is on `core/math` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Planes, boxes, frustums and intersection tests as mathematics | `basics/math-geometry` | must |
| View and projection matrices, the frustum | `basics/math-projection` | must |
| Strata's `AABB` type | `core/math` | must |
| The camera and Strata's clip space | `gpu/coordinates` | must |
| Dot products and vector length | `basics/math-vectors` | must |
| The render scene's proxies and their world bounds | `draw/render-scene` | must |
| Deterministic parallel work in fixed chunks | `core/jobs` | must |
| The cost of operations (big-O) | `basics/data-structures` | helps |
| Perf tests run only in Release | `engineering/perf-lab` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `conservative-test` | Conservative test | - |
| `frustum-culling` | frustum culling | - |
| `loose-grid` | Loose grid | - |
| `positive-vertex-test` | Positive vertex test | - |
| `screen-fraction` | Screen fraction | - |
| `size-culling` | Size culling | - |
| `spatial-index` | Spatial index | SpatialIndex |
