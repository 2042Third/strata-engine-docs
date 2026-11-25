# Brief: `editor/camera-viewport`

| Field | Value |
| --- | --- |
| Title | The editor camera and viewport state |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `gpu/coordinates`, `basics/math-rotations`, `draw/bounds-culling`, `editor/commands` |
| From | editor-core ch. 14 (orbit, pan, dolly and fly, `FitBounds`, per-scene cameras, which camera each view uses, viewport settings); last before the tutorial so that `editor-ui/scene-view` builds on it |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/camera-viewport` — The editor camera and viewport state

**Covers.** The problem: a person must look at any part of a scene quickly (orbit around what they look at, pan, dolly
in, fly through), frame a selection, find each scene as they left it, and every view (the Scene view, the Game view, a
capture) must know which camera it draws with. The idea, with its geometry: an orbit camera in spherical coordinates
(yaw and pitch in degrees, a distance around a target), pitch clamped at 89 degrees, panning by the units one pixel
covers at the target's depth, dollying by a factor per wheel step in double precision, framing a box by its eight
corners against the frustum, the position as the target minus the forward direction times the distance, and a reversed-Z
projection. The code: `EditorCamera` (Orbit, Look, Pan, Dolly by 0.85 per wheel step, Move, fly mode at a speed the
wheel changes by 1.25 per step and Shift makes four times faster, Focus on the bounding sphere at r·1.1/sin of the
narrower half field of view, `FitBounds`, `LookAt`, saved as JSON; the mouse buttons and keys that drive it are named
once); `EditorViewport` (the camera; a camera stored per scene; `ViewportSettings`; three renderers for the Scene view,
the Game view and captures; picking named and linked; `FrameScene`; saved to `<project>/.strata/EditorViewport.json`);
`ViewportSettings` (grid, outline, gizmos, colliders, stats, preview lighting, game UI, canvas mode, gizmo mode and
space, snap steps, debug view, cell bounds, the Game view's mode, piloting the game camera, edit pose, quality); the
first framing of a scene along its primary camera, framed again once loading meshes arrive unless the person moved the
camera; which camera each view uses (`ResolveViewportView`, `ResolveSceneView` with the Game camera on F8,
`ResolveGameView` with UI over black when there is no camera, `GetViewportRenderOptions` with preview lighting and the
HUD hidden in editor views); and the view commands `camera.get`, `camera.set`, `camera.focus`, `viewport.getSettings`,
`viewport.setSettings` and `viewport.capture`, which record no undo step. Then the section "Captures", because the
book's own figures come from it: a capture is not a screenshot of the viewport. It renders with the capture renderer,
which keeps its own history, through the camera it is asked for (the editor camera, the scene's, or one of its own made
from position, target and field of view, which leaves the person's view where it was), at the view's size or 1280x720
while the view is hidden; its poll renders again while glyphs, assets, finer mips, poses, new instances, shadow views,
the pre-exposure, global illumination or TAA are still pending, each with its own frame limit (glyphs 120, assets 300,
mips 120, poses 8, instances 120, shadow views 16, pre-exposure 8, TAA 16); the pixels are read back without a stall and
encoded as PNG on a job, and the result reports what was still pending (`pendingAssets`, `texturesBelowWanted`,
`waitedFrames`, `previewLighting`, the hidden canvases). Live captures (`live`, `atFixedStep`, `frames` up to 16) read
back what a view presented instead, its last frame, because the command polls run before the views render. The example
focuses the camera on a selection with `camera.focus`, turns it with `camera.set {yaw, pitch}`, reads `camera.get` and
takes a capture. The exercise derives `Pan`'s units per pixel from the field of view and the distance, and why
`FitBounds` uses the corners; the trace exercise checks `Focus`'s distance in a debugger. Afterwards the reader can
change the editor camera, the views' camera choice and the captures, which `editor-ui/scene-view` and the book's figures
build on.

**Leaves out.**

- Picking and gizmos → `editor-ui/scene-view`
- The Scene view's drags that drive the camera (mouse buttons, keys, the locked cursor) → `editor-ui/scene-view`
- The Game view's resolutions and letterboxing → `editor-ui/game-view`
- Projection, frustums and depth as mathematics → `basics/math-projection`
- Strata's clip space and reversed depth → `gpu/coordinates`
- Debug views and what each shows → `gpu/debugging`
- Reading pixels back without a stall → `gpu/readback-timing`
- TAA, its jitter and its history → `image/taa`

**Fit.** `fits`: about 5,300 words against L (5,000). Counted again from the sections: the section "Captures" (about 700
words with its excerpt) and the camera's concept with its geometry take the most, beside six features, two more
excerpts, one figure and three hands-on.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:367` | concept | home | Editor cameras: orbit, pan, dolly and fly, framing, reversed-Z, a view state per scene |
| `editor-core:230` | feature | home | Which camera each view uses and what editor views change |
| `editor-core:251-255` | feature | home | `EditorCamera`, `EditorViewport`, `ViewportSettings`, the first framing, the view commands |
| `editor-core:445` | code | home | `StrataEditor/src/Editor/EditorCamera.cpp:70-91`: orbit; with `:136-170` (`FitBounds` over eight corners) and `:256-259` (the position) |
| `editor-core:447` | code | home | `StrataEditor/src/Editor/ViewportRenderer.cpp:24-95`: which camera a view uses |
| `new:65` | feature | home | How `viewport.capture` works (the section "Captures", about 700 words, with `editor-core:255`): the capture renderer and its own history; the camera a capture uses (editor, scene, or its own from position, target and field of view, the person's view unmoved; 1280x720 while the view is hidden); the poll that renders again while glyphs (120 frames), assets (300), finer mips (120), poses (8), new instances (120), shadow views and probes (16), the pre-exposure (8), global illumination (54: its 38 settle frames plus 16) are pending, and then TAA (16) and spatial reflections (2) settle; the readback and the PNG encoded on a job; what the result reports (`pendingAssets`, `texturesBelowWanted`, `waitedFrames`, `previewLighting`, hidden canvases); live captures (`live`, `atFixedStep`, `frames` up to 16), which read back a view's last frame because polls run before views render. Evidence: `StrataEditor/src/Editor/EditorViewportCommands.cpp:36-81`, `:480-660`, `:723-735`, `:808-845`, `:878-962`, `:1211-1235`; `Strata/src/Strata/Renderer/SceneRenderData.h:771` (`c_GIMaxSettleFrames`) |
| `new:66` | code | home | `StrataEditor/src/Editor/EditorViewportCommands.cpp:808-845`: the capture's poll, what is still pending and the limit of each, and the history started again while the content is incomplete |
| `editor-core:500` | figure | home | The editor camera's model: target, distance, yaw, pitch, the pan plane, framing |
| `editor-core:641` | hands-on | home | Exercise: the camera's mathematics |
| `new:67` | hands-on | home | Trace it yourself (D27): select an entity, run `camera.focus` with a breakpoint in `EditorCamera::Focus`, and check the distance it sets against r·1.1/sin of the narrower half field of view, with r the bounding sphere's radius. Evidence: `StrataEditor/src/Editor/EditorCamera.cpp:117-134`; `StrataEditor/src/Editor/EditorCamera.h:57` |
| `editor-core:696` | term | home | Editor view |
| `editor-core:730-732` | term | home | Orbit camera, pivot, dolly, pan and fly |
| `editor-core:734` | term | home | Framing |
| `editor-ui:200` | feature | home | The editor camera as the UI survey lists it: orbit, pan, dolly, fly with Shift, Focus and `FitBounds`, saved per scene; one home with `editor-core:251`; the drags are `editor-ui/scene-view`'s |
| `editor-ui:516` | figure | home | The camera's geometry with the pitch clamp, pan's units per pixel and the focus distance; one picture with `editor-core:500` |
| `editor-ui:766`, `editor-ui:768` | term | home | Editor camera with orbit, pan, dolly and fly; framing (Focus, `FitBounds`); one home with `editor-core:730-732` and `editor-core:734` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projection, the field of view and frustums | `basics/math-projection` | must |
| Angles, yaw and pitch, spherical coordinates | `basics/math-rotations` | must |
| Bounding boxes and their corners | `draw/bounds-culling` | must |
| The camera, clip space and reversed depth | `gpu/coordinates` | must |
| The editor core and `EditorContext` | `editor/program` | must |
| Commands and their kinds | `editor/commands` | must |
| The running copy, the Scene view and the Game view | `editor/play-mode` | helps |
| The placement preview | `editor/placement` | helps |
| Deferred commands and their polls (a capture is one; the page says so in a sentence) | `editor/deferred-commands` | helps |
| Readback without stalls | `gpu/readback-timing` | must |
| Jobs and returning results to the main thread | `core/jobs` | helps |
| TAA and its settling | `image/taa` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `dolly` | Dolly | - |
| `editor-camera-orbit` | Editor camera; orbit | - |
| `editor-view` | Editor view | - |
| `fly` | fly | - |
| `framing-editor` | Framing (editor) | - |
| `orbit-camera` | Orbit camera | - |
| `pan` | pan | - |
| `pivot-editor` | Pivot (editor) | - |
