# Notes: gpu/frame-tour

## New terms

None proposed. The page defines the six glossary terms it homes in bold: forward, depth prepass (EQUAL depth test), clustered forward, deferred, entity ID buffer, invariant position.

## Since

0.3.0: the prepass of depth, normals and entity IDs and picking from it ship in 0.3.0 (`plan/inventory/render-core.md` section 1.11, Picking row); the stage timer is 0.4.0 but the frame itself is older.

## Movable claims

- The stage list and its order (Setup, Cull, Aerial, Shadows, Prepass, ScreenShadows, AO, RadianceCascades, Reflections, Opaque, Transparent, TAA, DepthOfField, MotionBlur, Post, Overlays): `Strata/src/Strata/Renderer/GPUProfiler.h:20-39`, `SceneRenderer.cpp:3473-3940` at 319075e3.
- The GI stage keeps the name `RadianceCascades`: `GPUProfiler.h:30-32`.
- Light passes are timed in the running stage (Cull or Setup): `SceneRenderer.cpp:3561-3573`.
- Local shadow work (views, tile clears, fresh ranges) starts the Shadows stage; rect lights draw back faces into a second atlas: `SceneRenderer.cpp:3613-3640`, `SceneRendererLocalShadows.cpp:1496-1499`.
- ScreenShadows holds the sun's mask and the rect lights' masks, at most 4: `SceneRenderer.cpp:3646-3661`, `SceneRenderData.h:345`.
- Forward shader forms `AreaLights` and `Field` chosen per frame: `SceneRenderer.h:1218-1232`, `SceneRenderer.cpp:2486-2490`, `:3521-3524`.
- The depth switch, with unbiased back-face passes: `SceneRenderer.cpp:2566-2592`.
- The statistics named (`AreaLights`, `LocalShadowFading`, `GlobalIlluminationShaded`): `SceneRenderer.h:586-588`, the stats struct at 550.
- The overlays include the Wireframe and Culled views: `SceneRenderer.cpp:4026-4029`, `:4287-4290`.
- The GI join comment names 0.7.0's indirect light: `SceneRenderer.cpp:3512`.
- `RenderFrame` is about 930 lines: `SceneRenderer.cpp:3035-3960`.

## Requests

- Figure: the intermediate targets of one view (render-core:525, depth, normals, entity IDs, HDR before tone mapping, output) is not requested: no debug view shows raw depth, normals or entity IDs (render-core:837), so the page shows a Mermaid diagram of the targets. Request a capture figure when the capture addition ships.
- Further reading names a book, two papers and a conference talk without links; no host asked.

## Not verified

- That a graphics debugger shows `beginMarker` names as groups (NVRHI's Vulkan backend was not read for debug labels).
- That the 1 by 1 `NoShadows` array is made for binding when no shadow map exists (only its creation at SceneRenderer.cpp:444-451 was read).
- The authors' reason for a half-float pre-exposure (the page states no motive).
- The citations of other engines' designs are by source only (Gregory, Olsson, Burns and Hunt, O'Donnell); the books and papers were not read here.
- The rect lights' back faces and depth ranges were read in the frame's calls and comments only (`SceneRendererLocalShadows.cpp:33`, `SceneRenderer.cpp:3335-3355`); `BuildLocalShadowRanges` and the mask shader were not read.

## Findings not applied

- `render-core:162` and `render-direct:205` (light passes in `GPU.Cull`): applied as the erratum, light passes are timed in the running stage (`Cull` on GPU-driven frames, `Setup` on the CPU path).
- `names` lint: none left.
- Passive-voice and noun-stack warnings (57 and 6) are left: they do not fail.

## Clerk

- No term or word asked.
- Left for the planner: the capture figure of one view's targets.
