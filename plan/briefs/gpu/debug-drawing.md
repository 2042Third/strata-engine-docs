# Brief: `gpu/debug-drawing`

| Field | Value |
| --- | --- |
| Title | Overlays, debug drawing and gizmos |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `gpu/frame-tour`, `world/tutorial-component` |
| From | render-core; home of overlay passes (`SceneOverlayRegistry`); its exercise gives WindZone a gizmo |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/debug-drawing` — Overlays, debug drawing and gizmos

**Covers.** The job: draw over the finished image what helps people see the scene (the grid, the selection outline,
tints, debug lines, gizmos, text and the game's UI) in exact display colors, and let modules above the renderer add
passes the renderer never names. The problem and the approaches: immediate-mode debug lines, retained gizmos, overlay
passes found through a registry (dependency inversion). The map is the overlay order. The contract: overlays are drawn
after post-processing into the output; overlays placed in the scene use constants without jitter and a one-pixel depth
bias under TAA; tints and the outline need the entity-ID buffer; the renderer reaches higher modules only through
registries. The toy is a recorder of line lists and its draw in about 40 lines.

The real code: `DebugDraw` (immediate shapes in two depth modes, circles from tables, packed sRGB colors);
`RenderOverlays` in its order (the views and tints first, the grid, lines uploaded relative to the camera in double,
the world text, the world canvases, the outline, the lines on top, the HUD); `DrawSceneGizmos` (lights, cameras and
colliders through `ComponentInfoBuilder::Gizmo` and its `ComponentGizmo` shapes: box, sphere, capsule, mesh bounds;
culled to the view, icons below a pixel size); `ISceneOverlayPass`,
`SceneOverlayRegistry` and `SceneOverlayFrame`; `SceneScreenView` for the editor's 2D canvas (the struct and the term
"screen view" are taught here; `editor-ui/scene-view` says how canvas mode drives it); `SetJitteredDepthBias`.
The figures show the overlays off and on, and the tints with the streaming view. What Strata does not do: debug drawing
from scripts. Alternatives, tests (`Renderer.DebugDraw`, the overlay GPU tests), changing safely. The exercise starts
from `world/tutorial-component`'s end state and gives the WindZone its gizmo, a sphere of its radius; its solution patch
is the WindZone chain's gizmo, from which `scripting/tutorial-host-function` starts (R41), and `capstone/build` adds
only the arrow. A second draws a path with `DebugDraw` from C++, depth-tested and on top; a third traces a gizmo from
its registration to its lines.

**Leaves out.**

- Picking and the transform gizmo the person drags → `editor-ui/scene-view`
- The game UI's quads, runs and shaders → `ui/drawing`
- Text, fonts and the glyph atlas → `gpu/text`
- What each debug view shows and the page that reads it → `gpu/debugging`
- TAA's jitter → `image/taa`
- LOD selection shared by tools and the renderer → `draw/lod`

**Fit.** `fits`: about 4,900 words against L (5,000). Seven features with three excerpts, two figures and three
exercises, the WindZone chain's gizmo among them, take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:433` | concept | home | Overlays and editor visualisation; overlay passes from higher modules through a registry; the mistake of renderer code including GameUI |
| `render-core:220`, `render-core:221`, `render-core:222` | feature | home | The overlay set; `DebugDraw`; `DrawSceneGizmos` |
| `render-core:223`, `render-core:224`, `render-core:225` | feature | home | `ISceneOverlayPass`, `SceneOverlayRegistry` and `SceneOverlayFrame`; `SceneScreenView`, the struct taught here (critic-gameui-18); `SetJitteredDepthBias` |
| `gameui:685` | term | home | Screen view, beside `SceneScreenView`, which this page teaches; the glossary entry follows the teaching page (critic-gameui-18; passed by `ui`) |
| `new:19` | code | home | `Strata/src/Strata/Renderer/DebugDraw.h:29-62`: the immediate shapes, the depth modes, packed colors |
| `new:20` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:4055-4126`: the overlays' order, the entity-ID check, debug lines made relative to the camera in double |
| `new:21` | code | home | `Strata/src/Strata/Renderer/SceneOverlay.h:92-136`: `ISceneOverlayPass` and `SceneOverlayRegistry`: modules register factories, each renderer makes one pass per factory |
| `new:22` | not-done | home | No debug drawing from scripts. Evidence: no such function in `StrataScriptCore/Include/StrataScript/` (`git grep -niE -e debugdraw -e drawline 822a7a46 -- StrataScriptCore` finds nothing, run again at the pin) |
| `render-core:515` | figure | home | The overlay order |
| `render-core:528` | figure | home | Overlays isolated: the grid, an outline, gizmos; overlays on and off |
| `render-core:530` | figure | home | Entity tints with the streaming view, as an overlay-based view |
| `render-core:616` | rule | home | The renderer reaches higher modules only through registries |
| `render-core:663` | hands-on | home | Debug drawing from C++, with and without the depth test; scripts cannot |
| `render-core:841` | open | home | Settled: games cannot reach `DebugDraw` from scripts (`new:22`) |
| `render-core:770`, `render-core:771` | term | home | Overlay; gizmo |
| `scene-ecs:203` | feature | home | `ComponentGizmo`: the shapes a component asks the editor to draw (Box, Sphere, Capsule, MeshBounds), which the WindZone's gizmo uses |
| `new:49` | hands-on | home | Exercise (extend), the WindZone chain's gizmo: from `world/tutorial-component`'s end state, the WindZone gets its gizmo through `ComponentInfoBuilder::Gizmo`, a sphere of its radius (`ComponentGizmoShape::Kind::Sphere`), drawn in the one gizmo group the pin has, `Collider`; the solution is the patch `exercise-<n>.patch` of this page's tutorial file, a patch of the chain, from which `scripting/tutorial-host-function` starts (`startsFrom` with the exercise, R41; critic-book-27), and `capstone/build` adds only the arrow of a Directional zone. Evidence: `Strata/src/Strata/Reflection/ComponentRegistry.h:340-341`; `Strata/src/Strata/Reflection/ComponentGizmo.h:16-20, 23-38`; `Strata/src/Strata/Renderer/SceneGizmos.cpp:122-145` |
| `new:50` | hands-on | home | Exercise ("trace it yourself"): one component gizmo from its registration to its lines: with colliders shown and a Box Collider in view on the source build, a breakpoint in `DrawSceneGizmos`, the step into `BoxColliderGizmo`, registered with `.Gizmo(ComponentGizmoGroup::Collider, ...)`, which fills a `ComponentGizmoShape`, and `DrawShape` turning the shape into `DebugDraw` lines. Evidence: `Strata/src/Strata/Renderer/SceneGizmos.cpp:122, 165-176, 215`; `Strata/src/Strata/Physics/PhysicsComponents.cpp:143` |
| `gameui:342` | concept | home | Overlay passes and dependency inversion, as the game UI meets them; the same idea as `render-core:433` |
| `gameui:660` | term | home | Overlay pass |
| `render-core:177` | feature | use | The frame's overlay step |
| `render-core:226` | feature | link | LOD selection as pure functions, which tools show |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame's passes and its overlay step | `gpu/frame-tour` | must |
| Adding a component and its system (the WindZone) | `world/tutorial-component` | must |
| Reflection: one registration, `ComponentInfoBuilder` | `world/reflection` | must |
| The composition root, registries and dependency inversion | `core/layers-registries` | must |
| Camera-relative positions subtracted in double | `draw/mirrors-camera-relative` | helps |
| TAA's jitter | `image/taa` | helps |
| The Scene view and its chips | `editor-ui/scene-view` | helps |
| The game UI's overlay pass | `ui/drawing` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `gizmo-gpu` | Gizmo (gpu) | - |
| `overlay-gpu` | Overlay (gpu) | - |
| `overlay-pass` | Overlay pass | - |
| `screen-view` | Screen view | - |
