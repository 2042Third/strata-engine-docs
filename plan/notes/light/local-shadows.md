# Notes: light/local-shadows

## New terms

None proposed. The five glossary terms of the brief (cube shadow, shadow atlas, tile, guard band, quadtree allocator) are defined in bold. The page also bolds caster: a proposal for the planner (caster: an object that is drawn into a shadow view; home: this page).

## Since

0.6.0: the atlas, the quadtree allocator, tile fitting, the view cache and the redraw budget are dated 0.6.0 in the inventory (`plan/inventory/render-direct.md`, rows 136-145). Not checked against the tags. The many-lights additions (up to 256 lights, fades by time, fixed noise) are 0.8.0 (`Docs/Releases/0.8.0.md`).

## Requests

- Words for extra-words: `paraboloid` (the table names dual-paraboloid maps, a technique of the cited 2002 paper). The page otherwise uses only listed words.
- A figure of lanterns under trees (`CastShadows` off and on; `ShadowFilterRadius` 0 against 8) is wanted but not asked for in a figures file: the page's pictures are Mermaid diagrams, and no scene with lanterns and entity names could be checked at the pin from this task. The planner may add a figure with the Showcase sample (`Samples/Showcase/Assets/Scenes/Outpost.stscene` holds a `Lantern` prefab).
- A drawn diagram of the atlas with a point light's six faces, spot tiles and guard bands is not made: the atlas layout is shown by the allocator's hand trace and the sketch's output.
- Further reading cites Williams 1978, Brabec, Annen and Seidel 2002, Real-Time Rendering (Akenine-Moller, Haines, Hoffman) and Epic's documentation of virtual shadow maps without links.
- The link `../light/area-lights.md` points to a page that did not exist when this page was written.

## Not verified

- That Real-Time Rendering presents one cube map per light as the standard method; that dual-paraboloid shadows need small triangles to keep edges straight (general knowledge, the cited 2002 paper); that Unreal Engine 5 uses virtual shadow maps with pages; that "many games" split static and dynamic shadow maps (the Alternatives table).
- The exact reason the culling shader takes at most 12 local views per batch: the code states the limit (`ST_CULL_MAX_LOCAL_VIEWS` 12), not why.
- Memory figures of the atlas (16, 64, 256 MiB) are D32 texels times the side squared; the engine's comment names only the 256 MiB of the 8192 atlas, the guide the 64 MiB of 4096.
- No timing is measured on the page: the only time figure is the engine's target of 0.5 ms for the caster search.

## Findings not applied

- The brief says the sampling's noise "also turns with the TAA frame (on main the exception to fixed noise)" and its exercise moves the rotation to a fixed tile. At the pin (`Strata/shaders/Include/LocalShadows.slang:32-41`) the rotation is fixed per pixel (interleaved gradient noise of the pixel alone), so the page teaches the fixed noise and its exercise compares the engine's rule with an invented turning rule.
- The brief gives `MaxShadowedLocalLights` 4, 16, 16, 16 and the erratum of the Manual's "at most 16". At the pin the row is 4, 16, 64, 256 (`Strata/src/Strata/Renderer/RendererQuality.cpp:45`) and the Manual says so; the page names no limit but the rows' effect.
- The brief names `PerfGPU.Renderer.ShadowRedraw4K*` as the local shadows' perf tests. Those measure the sun's cascades (`StrataTests/src/Perf/RendererPerfTests.cpp:1428`); the local ones are `PerfGPU.Renderer.LocalShadows16Lights*`, `LocalShadows64LightsHigh*`, `LocalShadows256LightsUltra*`. The page describes the latter in words.
- The brief's figure of lanterns (`tp.lantern`) is not produced (see Requests).
- Soft shadows of rectangle lights are taught only as far as the atlas is concerned (six views, guard band reach of an eighth of the tile, a second atlas of back faces, at most four at once); the filter belongs to `light/area-lights`.

## Movable claims

Reviewed at v0.8.0 (319075e3) against `Docs/Releases/0.8.0.md` and `Docs/DeveloperGuide.md` ("Local light shadows").

- The preset rows: atlas side 2048, 4096, 4096, 8192; largest tile 512, 1024, 1024, 2048; shadowed lights 4, 16, 64, 256; views per frame 12, 12, 24, 48 (`RendererQuality.cpp:41-46`). The page states the atlas sides, their memory and the views per frame.
- The fade: 0.2 s, at least 8 frames (`SceneRenderer.h:1046-1047`); the keep ratio 1.25, the hysteresis band 0.4 to 1.25, seven eighths of the atlas, at most two lights between sizes, 80 degrees for a spot light, the aged share of a quarter of the budget.
- 4,096 followed bounds per shadowed light, counted as at least 16 lights.
- The batch of at most 12 local views in the GPU culling (`ST_CULL_MAX_LOCAL_VIEWS`).
- At most four rectangle lights hold a shadow at once (`RenderData::c_MaxAreaShadowMasks`).
- The smallest tile of 128 texels and the fallback atlas floor of 2048.
- Known issues of 0.8.0: at High and Ultra with many lamps in view the nearest lamps' shadows are softer than 0.7.0's; point and spot shadow edges under TAA keep a fixed pattern that leaves a grain; beyond 4,096 casters per shadowed light the tracking starts over; a camera cut that reorders many shadowed lights orders them in quadratic time. The page names only the grain under TAA.
- The target of 0.5 ms for the search for casters (`LocalShadows256LightsUltraMoving1kFind`, provisional in `StrataTests/Perf/Budgets.json`).
- The metric names `LocalShadows16Lights` and the like of the `PerfGPU.Renderer` suite are not named on the page.
