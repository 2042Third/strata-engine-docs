# Brief: `editor/placement`

| Field | Value |
| --- | --- |
| Title | Placing content |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `editor/undo`, `basics/math-geometry`, `draw/bounds-culling`, `editor/deferred-commands` |
| From | editor-core ch. 13 (raycasts against the scene, fallbacks, snapping, resting boxes, `asset.place` and the Scene view's drop sharing one request) |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/placement` — Placing content

**Covers.** The problem: a person drags a prefab into the Scene view, or an agent calls `asset.place` with a point of the
view, and both must land the asset on the surface under that point, resting on it, the same way to the bit; the ghost
shown while dragging must show exactly that place and write nothing. The naive answers: place at the origin, rest the
box's center instead of its bottom, drop where the ghost was not. The idea, with its geometry: a ray from the camera
through a point of the image (from normalized device coordinates), candidates from a spatial index, exact tests on
triangles, fallbacks when nothing is hit, snapping, and a box resting on a slanted plane by its support distance along the
normal (`|n|·extents − n·center`). Strata's code: `SceneRaycast::Cast`, the editor's own ray against what the scene
draws, taught under its own name (the glossary's raycast, a query against colliders, is `physics/queries`' and is
linked): the render scene's spatial index, then the loaded triangles, or bounds while a mesh loads, with the entities
being placed ignored; `EditorPlacement::Place` (a surface hit,
else the grid plane y = 0 within 500 m, else a point in front; snapping across the normal's main axis, with a ray cast
down again on upward ground; `RestOn`); `FindPivotSurface`, where the create menus put new entities; `MakeRayRequest` and
`MakeViewRay`, one request with the same floats for the drop and for `asset.place`, the ray relative to the camera;
`PlacementPreview`, the ghost's box, ring and label, which writes nothing and casts again only when its key changes;
`AssetBounds`, what an asset draws around its origin, cached by content stamp; `scene.raycast` and `asset.place`, an Edit
command that waits by the clock; `entity.dropToGround` with five rays; `SceneBounds` for framing and placement. Placement
by a ray is new after 0.7.0. The rule: place through `EditorPlacement::Place`, and the drop and its ghost use one request.
The example calls `asset.place` for a crate at a point over a ramp and at a point of the sky, and compares the answers
with the ghost. The exercise adds a `stackOn` option that rests an asset on another entity's bounds; the trace exercise
compares the request of a drop with that of an `asset.place` call. Afterwards the reader can change how content is
placed and keep the person's drop and the agent's call identical.

**Leaves out.**

- Rays, planes, boxes and their tests → `basics/math-geometry`
- Bounds and the render scene's spatial index → `draw/bounds-culling`
- The drop and the ghost as the Scene view draws them → `editor-ui/scene-view`
- Physics raycasts against colliders, and the glossary's entry raycast → `physics/queries`
- Positions relative to the camera → `draw/mirrors-camera-relative`

**Fit.** `over`: about 5,300 words against M (3,000). Counted again from the sections, with the trace exercise: the
geometry of resting a box, nine features, four excerpts and two exercises pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:363` | concept | home | Placing objects in 3D: rays from the camera, broad and narrow tests, fallbacks, snapping, resting a box |
| `editor-core:190-198` | feature | home | `SceneRaycast::Cast`, `EditorPlacement::Place`, `FindPivotSurface`, `MakeRayRequest`, `PlacementPreview`, `AssetBounds`, `scene.raycast` and `asset.place`, `entity.dropToGround`, `SceneBounds` |
| `editor-core:800` | open | home | Placement by a ray (`asset.place`, `scene.raycast`, the ghost) came after 0.7.0: its sections are marked new in 0.8.0; the other dates the survey could not find stay unstated |
| `editor-core:443` | code | home | `StrataEditor/src/Editor/EditorPlacement.cpp:125-213`: `Place` and `RestOn` |
| `new:38` | code | home | `StrataEditor/src/Editor/EditorPlacement.h:82-94`: `MakeViewRay` and `MakeRayRequest`, one request for the drop and the command |
| `new:39` | code | home | `StrataEditor/src/Editor/Commands/PlacementCommands.cpp:463-600`: `asset.place`, the Edit command that waits by the clock |
| `new:40` | code | home | `StrataEditor/src/Editor/SceneRaycast.h:17-41`: where a ray meets what a scene draws |
| `editor-core:498` | figure | home | The placement decision flow, and a box resting on a slanted surface |
| `editor-core:526` | figure | home | The placement ghost on a surface and over empty sky |
| `scene-ecs:482` | figure | home | The prefab placement ghost; one picture with `editor-core:526` |
| `editor-ui:568` | figure | home | Dragging a prefab over the Scene view: the box ghost and its label; one picture with `editor-core:526` and `scene-ecs:482` |
| `editor-core:589` | rule | home | Place through `EditorPlacement::Place`; the drop and its ghost use one request |
| `editor-core:637` | hands-on | home | Exercise: a `stackOn` option |
| `new:63` | hands-on | home | Trace it yourself (D27): drop a prefab on the Scene view, then call `asset.place` at the same point of the view, each with a breakpoint in `MakeRayRequest`, and compare the two requests' origin, direction and distances to the float. Evidence: `StrataEditor/src/Editor/EditorPlacement.h:82-94`; `StrataEditor/src/Editor/EditorPlacement.cpp:97-123` |
| `editor-core:725` | term | link | Raycast, one entry homed on `physics/queries`; the page teaches the editor's ray against the scene under its own name (`SceneRaycast`) and links the entry |
| `editor-core:727-729` | term | home | Support function, snapping, placement ghost |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Rays, planes, boxes and intersection tests | `basics/math-geometry` | must |
| Dot products and normals | `basics/math-vectors` | must |
| Bounds and the spatial index | `draw/bounds-culling` | must |
| Normalized device coordinates | `gpu/coordinates` | must |
| Positions relative to the camera | `draw/mirrors-camera-relative` | helps |
| Undo steps | `editor/undo` | must |
| Deferred commands | `editor/deferred-commands` | must |
| Prefab instances | `editor/prefab-instances` | helps |
| Content stamps of assets | `assets/importing` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `placement-ghost` | Placement ghost | - |
| `snapping-editor` | Snapping (editor) | - |
| `support-function` | Support function | - |
