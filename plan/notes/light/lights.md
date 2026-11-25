# Notes: light/lights

## New terms

None proposed. The five terms the brief names are defined in bold on the page: punctual light, range (light), light record, inner/outer cone angle, preview lighting.

## Since

Light components, the windowed falloff and the cone: 0.3.0 (inventory render-direct:74-84; light records 0.4.0, drawn transforms 0.8.0).

## Movable claims

Reviewed at v0.8.0 (319075e3) against `Docs/Releases/0.8.0.md` ("Rect lights", "Highlights like in a drawing", "Shading").

- Four light components; defaults 3 lux, 10 cd and 10 m, 20 cd and 15 m, cone 20 and 30 degrees:
  `Strata/src/Strata/Renderer/RendererComponents.h:25`, `:54-55`, `:70-74`.
- Source Radius at most 2 m, highlights only: `Strata/src/Strata/Renderer/RendererComponents.h:56`, `:63`.
- Angular Diameter is the stored `ShadowSoftness`, 0.53 degrees, sizing highlight and penumbra:
  `Strata/src/Strata/Renderer/RendererComponents.h:28`, `Strata/src/Strata/Renderer/RendererComponents.cpp:290-294`.
- Rect Light: 1 x 0.5 m, 25 nits (or lumens through `Units`), range 10 m from the face:
  `Strata/src/Strata/Renderer/RendererComponents.h:86-94`; display name `RendererComponents.cpp:357-358`.
- Light Surface tag, no data, added by Make Area Light, left out of reflections, probes and area shadows:
  `Strata/src/Strata/Renderer/RendererComponents.h:107-115`, `RendererComponents.cpp:384-389`.
- `c_LightRect = 2`, three record types: `Strata/src/Strata/Renderer/SceneRenderData.h:37-38`.
- `LightRecord` eight vectors, 128 bytes; `LightData` 64 bytes; `LightShape` 48 bytes:
  `Strata/src/Strata/Renderer/SceneRenderData.h:305`, `:273`, `:283`.
- A rect record's center, radiance, normal, axes: `Strata/src/Strata/Renderer/RenderLights.cpp:99-117`; its bound
  range plus the half diagonal: `Strata/src/Strata/Renderer/AreaLights.cpp:275`.
- Change log of at most 65,536 changes: `Strata/src/Strata/Renderer/RenderLights.h:40`.
- Preview lighting off for any of five light kinds: `Strata/src/Strata/Renderer/SceneRenderer.cpp:180-187`; preview
  sun 55 degrees up: `SceneRenderer.cpp:115`.
- Test suites `Renderer.AreaLights` and `GPU.SceneRenderer.AreaLights`: `StrataTests/src/Renderer/AreaLightsTests.cpp:240`,
  `StrataTests/src/Renderer/GPUSceneAreaLightTests.cpp:450`; the rect record case `RenderSceneTests.cpp:1222`.

## Requests

- Word: `falloff` (8 uses; the industry term for how light weakens with distance). Add to tools/data/extra-words.txt.
- Figures not drawn (no figures file): a sweep of a spot light's inner and outer cone angles on a wall together with a point light's range window; preview lighting in the Scene view against the Game view of the same empty scene. Layout for the editor picture: the default Scene and Game view layout.
- Further reading entries: Karis, "Real Shading in Unreal Engine 4" (SIGGRAPH 2013) and the Khronos KHR_lights_punctual specification are cited without links; the hosts are not asked for.

## Not verified

- The Karis formula is described from memory of the paper (a window of one minus the fourth power, squared, over the squared distance plus one); the page names the "plus one" only in the alternatives table.
- Fog and post process choosing the first active component (the brief's rule row) is not stated on the page; only the sky light's first-active loop was read.
- Which engines support several shadowed suns and which use light cookies (alternatives table, general wording).
- The Debug-build assert on a missing signal is taken from a comment of the RenderSceneTests case, not from the sync code.

## Findings not applied

- Brief Fit (superseded at v0.8.0): the rectangle light now exists (`RectLightComponent`, `c_LightRect`, a 128-byte `LightRecord`); the page states its component, record and `LightShape` and leaves its shading to light/area-lights.
- The brief's spot-bounds, drawn-transform and record items are applied; `RendererComponentsTests.cpp` holds no spot-cone or units case at the pin (those are in `GPUSceneLightingTests.cpp`), so the page cites that file.

## Clerk

- Admitted to extra-words.txt: falloff.
