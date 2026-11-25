# Brief: `editor-ui/scene-view`

| Field | Value |
| --- | --- |
| Title | The Scene view |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `editor-ui/shell`, `editor/camera-viewport`, `editor/placement`, `gpu/frame-tour`, `gpu/readback-timing` |
| From | editor-ui ch. 11 (`ViewportPanel`, toolbar and chips, async picking, ImGuizmo and `TransformDrag`, debug view legends, the drop and its ghost, the agent chip, canvas mode); home of picking and gizmos |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/scene-view` — The Scene view

**Covers.** The Scene view as a 3D view inside a UI, home of picking and gizmos. The problem and how engines solve it:
render the view offscreen at the panel's pixel size and show it as an image item; pick by CPU rays against bounds or by
a GPU buffer of entity IDs read back at the pixel; move objects with screen-space handles. The map is a diagram: the
toolbar strip with its chips above the image (never over the game's HUD), the image rendered by the view's renderer, the
overlays drawn over it. The contract: ImGuizmo starts a drag only while no item is hovered; a gizmo drag is one undo
step computed from its start state; picking never stalls. The toy is a viewport panel of about 60 lines: an image, a
pick request and a drag.

The real code: the image and how it cooperates with ImGuizmo (no item under the gizmo, no window move); camera drags
fed from the panel (first-frame and non-finite deltas dropped, the cursor locked while flying; the camera's math is
`editor/camera-viewport`'s); asynchronous picking with a one-pixel readback, applied frames later only if the same scene
still shows, with a timeout (a diagram), UI elements picked first, Ctrl and Shift; the gizmo drag with `TransformDrag`
(one undo step, locals recomputed under parents, none while playing, snapping inverted by Ctrl, ended when the selection
changes; a diagram). ImGuizmo is linked only by the editor's UI library, and themed with the axis colors. Then the chips
(camera settings, grid, outline, gizmos, stats, preview lighting, game UI, the debug view and its legend with counts per
color, quality, the game camera on F8, the animation preview), the agent chip after an automation command (shown while
an agent is connected and for a minute after, a click opening its entry in the Activity panel) and the flash that
outlines the entities the command touched for 0.6 s (their bounds taken once per command, the fade timed by the clock
so the panel stops animating), the drop of an asset and its ghost (the panel's side), the scene-load overlay, and
canvas mode for screen-space UI canvases (a world-space canvas is edited in the scene), which drives the screen view
that `gpu/debug-drawing` teaches. Pictures: the three gizmos, the LOD debug view with its legend and the stats, the agent
chip with the flash, the drop ghost, canvas mode. At the end the reader can follow a click on the image to the
selection, and a gizmo drag to its undo step.

**Leaves out.**

- Orbit, pan, dolly and fly, `FitBounds`, per-scene cameras → `editor/camera-viewport`
- How placement decides where a dropped asset lands → `editor/placement`
- The list of debug views and what each colors → `gpu/debugging`
- Readback without stalls in general → `gpu/readback-timing`
- Overlays, the selection outline and gizmo shapes → `gpu/debug-drawing`
- The Game view and who owns input → `editor-ui/game-view`
- The Scene view's shortcuts → `editor-ui/game-view`
- Game UI rects and anchors, which canvas mode edits → `ui/layout`

**Fit.** `fits`: about 7,375 words against XL (8,000). Three concepts, four excerpts, three diagrams and five pictures
take the most; the camera's mathematics stays on `editor/camera-viewport`, and the agent chip and flash take one
paragraph.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:142` | feature | home | The Scene view panel (`ViewportPanel`) |
| `editor-ui:155` | feature | home | Canvas mode: a UI canvas laid out in 2D at its reference aspect, outlines, handles, zoom and pan |
| `editor-ui:196-199` | feature | home | Render to texture at the panel's pixel size; the toolbar strip; the chips; the debug view's legend |
| `editor-ui:201-202` | feature | home | Asynchronous picking; the gizmo with `TransformDrag` |
| `editor-ui:204-206` | feature | home | The agent chip and flash; the drop and its ghost (the panel's side); the scene-load overlay card |
| `editor-ui:384` | concept | home | The viewport: render to texture inside a UI, input only while hovered or focused, overlays over the image; first-frame and non-finite deltas, dragging the window instead of the camera |
| `editor-ui:390` | concept | home | Picking: CPU rays or an ID buffer; Strata's asynchronous read and stale-result rejection; blocking readbacks, picking against a resized image |
| `editor-ui:394` | concept | home | Transform gizmos: handles, world and local axes, snapping, a primary, locals under parents, one undo step from the start state; items stealing the click, a drag outliving its entity |
| `editor-ui:460` | code | home | `StrataEditor/src/Panels/ViewportPanel.cpp:149-210`: cooperating with ImGuizmo: no item under the gizmo, no window move |
| `editor-ui:461` | code | home | `StrataEditor/src/Panels/ViewportPanel.cpp:867-930`: camera drags from the panel; the camera's own math (`EditorCamera.cpp`) is `editor/camera-viewport`'s |
| `editor-ui:462` | code | home | `StrataEditor/src/Panels/ViewportPanel.cpp:936-994`: the gizmo drag's life with `TransformDrag`, snapping inverted by Ctrl, cancelling |
| `editor-ui:463` | code | home | `StrataEditor/src/Editor/EditorViewport.cpp:415-454`: asynchronous picking with a readback, a timeout and stale-result rejection |
| `editor-ui:514` | figure | home | The viewport's composition: toolbar strip and agent chip, the offscreen image, overlays, toasts in the view's corner |
| `editor-ui:518` | figure | home | The pick's timeline: click at frame N, readback ready at N+k, the scene check, `ApplyPick`, the timeout |
| `editor-ui:520` | figure | home | The gizmo drag's sequence from `Manipulate` to one undo step |
| `editor-ui:563` | figure | home | The translate, rotate and scale gizmos on a selected crate, World against Local |
| `editor-ui:565` | figure | home | The LOD debug view and its legend (`viewport.setSettings {debugView: "lod"}`), and the stats overlay |
| `editor-ui:567` | figure | home | The agent chip and the accent outline flash after an automation command |
| `editor-ui:569` | figure | home | Canvas mode on a UI canvas |
| `editor-ui:638` | rule | home | ImGuizmo starts a drag only while no item is hovered: the image becomes a `Dummy` over the gizmo |
| `editor-ui:640` | rule | home | A gizmo drag is one undo step computed from its start state |
| `editor-ui:642` | rule | home | Picking never stalls, and a late result never selects in another scene |
| `editor-ui:765` | term | home | Render target and render to texture, inside a UI |
| `editor-ui:769-772` | term | home | Gizmo and ImGuizmo; world and local space; snapping (of gizmo drags); picking (the entity-ID buffer, `render-core:772`, is `gpu/frame-tour`'s word and readback, `render-core:758`, `gpu/readback-timing`'s: the page links both) |
| `editor-ui:774` | term | home | The debug view's legend, with its counts per color (the word debug view is `gpu/debugging`'s, `render-scene:182`, and the page links it) |
| `new:38` | hands-on | home | Exercises (D27): a gizmo drag with snapping on and Ctrl held, what the crate's position does and how many undo steps the drag leaves (Basic, predict then run); a click on the image followed with breakpoints in `EditorViewport::RequestPick` and `UpdatePicking`, the frames counted until the readback is ready and the scene check read (Medium, trace); why the pick reads back the entity-ID buffer instead of casting a CPU ray against bounds, for a scene of skinned characters and foliage (Hard, design). Evidence: `StrataEditor/src/Editor/EditorViewport.cpp:415-454`; `StrataEditor/src/Panels/ViewportPanel.cpp:936-994` |
| `editor-ui:776` | term | home | Game camera (pilot) |
| `new:8` | feature | home | ImGuizmo is linked privately by `StrataEditorUI` only, beside nfd: only the viewport draws gizmos, and no game or core library links it. Evidence: `StrataEditor/CMakeLists.txt:53-54`; `Strata/vendor/CMakeLists.txt:102-105` |
| `editor-ui:200` | feature | use | The editor camera, as `editor/camera-viewport` teaches it |
| `editor-ui:516` | figure | link | The camera's geometry, drawn on `editor/camera-viewport` |
| `editor-ui:568` | figure | use | The drop's ghost, the picture `editor/placement` holds |
| `editor-ui:766` | term | use | Editor camera; orbit, pan, dolly and fly |
| `editor-ui:763` | term | use | Viewport, Scene view and Game view: "Game view" is one glossary entry with `editor-core:694`, homed on `editor/play-mode`; "Scene view" and "viewport" are homed on this page, where the glossary step splits the item (R46) |
| `editor-ui:203` | feature | link | The Scene view's shortcuts (`editor-ui/game-view`) |
| `editor-core:121` | feature | home | `TransformDrag`: a gizmo drag as one undo step with its merge key, its values computed from the drag's start |
| `gameui:159` | feature | home | How canvas mode drives the screen view to zoom and pan; the struct `SceneScreenView` is taught on `gpu/debug-drawing`, which the page links (critic-gameui-18) |
| `gameui:218-219` | feature | home | The Game UI chip, a click selecting the topmost UI element; canvas mode: the letterboxed canvas, outlines and handles, drag and resize with snapping, zoom about the pointer, pan, F and Home; the 2D canvas mode edits screen-space canvases only: a selected world-space canvas is edited in the scene, and the mode shows the scene's first screen-space canvas instead (critic-gameui-8, about 40 words; `StrataEditor/src/Editor/CanvasEdit.cpp:110-125`, `StrataEditor/src/Editor/CanvasEdit.h:52-54`) |
| `gameui:243` | feature | home | The editor's game-UI tests (`EditorGameUITests`, `EditorUICommandTests`, `GPUCanvasEditTests`) in "How it is tested" |
| `gameui:483` | figure | home | Canvas mode with outlines and handles on the selection, zoomed in with F: one picture with `editor-ui:569` |
| `gameui:502` | figure | home | The Scene view with the Game UI chip off and on (screen canvases hidden, world canvases still drawn) |
| `gameui:684` | term | home | Canvas mode (2D) |
| `gameui:685` | term | link | Screen view, homed on `gpu/debug-drawing` beside `SceneScreenView`, the page that teaches it (critic-gameui-18) |
| `render-core:773` | term | home | Picking: one glossary entry with `editor-ui:772` |
| `automation:183-184` | feature | home | The agent chip ("Agent: entity.create · 3 s ago" while a client is connected or 60 s after, its text made again once a second at most, a click showing the entry in the Activity panel) and the flash (the bounds of at most 64 entities taken once per command, accent rectangles fading over 0.6 s, timed by the clock): taught with `editor-ui:204` |
| `automation:579` | figure | home | The agent chip and the flash during its 0.6 s, or frames of the fade: one picture with `editor-ui:567` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor camera, per-scene cameras, viewport settings | `editor/camera-viewport` | must |
| Placing content: `asset.place`, the drop and its ghost | `editor/placement` | must |
| Readback and GPU timing: non-blocking readback | `gpu/readback-timing` | must |
| A frame of the scene renderer, the entity-ID buffer | `gpu/frame-tour` | must |
| Overlay passes and debug drawing | `gpu/debug-drawing` | must |
| Matrices, transforms and spaces | `basics/math-matrices` | must |
| The transform contract: world and local transforms under parents | `world/scene-graph` | must |
| Undo and redo: one step per drag | `editor/undo` | must |
| The kit's chips and the chip strip | `editor-ui/widget-kit` | must |
| Panels | `editor-ui/shell` | must |
| Play and Simulate (no undo while playing) | `editor/play-mode` | helps |
| The activity journal (the agent chip's last command) | `editor/journal` | helps |
| The debug views | `gpu/debugging` | helps |
| Rects, anchors and layout of game UI | `ui/layout` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `canvas-mode-2d` | Canvas mode (2D) | - |
| `debug-view-editor-ui` | Debug view (editor-ui) | - |
| `game-camera-pilot` | Game camera (pilot) | - |
| `gizmo-editor-ui` | Gizmo (editor-ui) | - |
| `imguizmo` | ImGuizmo | - |
| `picking` | Picking | entity-ID buffer |
| `render-target` | Render target | render to texture |
| `scene-view` | Scene view | viewport |
| `snapping-editor-ui` | Snapping (editor-ui) | - |
| `world-editor-ui` | World (editor-ui) | - |
