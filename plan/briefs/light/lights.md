# Brief: `light/lights`

| Field | Value |
| --- | --- |
| Title | Lights: the sun, points and spots |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `light/brdf`, `draw/render-scene`, `world/interpolation` |
| From | render-direct ch. 4; 1.3 (the components, falloff, the cone, one sun, what a light record holds, `LightData`, spot bounds, drawn transforms, preview lighting) · W8r (light components and records) |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/lights` — Lights: the sun, points and spots

**Covers.** The job: turn light components into what the forward pass shades with: one sun in the frame constants, point
and spot lights as records of the render scene. This page carries the full section on the problem: modelling the sun and
lamps cheaply, with punctual lights whose inverse-square falloff is windowed to a range (Karis 2013), against the legacy
constant, linear and quadratic attenuation. The components as plain data, with the unit of every field in its comment:
`DirectionalLightComponent` (lux, shadows, Angular Diameter, cascade fields), `PointLightComponent` (candela, range,
source radius, shadows) and `SpotLightComponent` (as the point light, with inner and outer half angles and defaults of
its own, 20 cd and 15 m against the point light's 10 cd and 10 m, which the page takes from the generated components
table and the excerpt), shining along the entity's -Z. One sun per frame: the brightest active directional light shines,
the others are ignored. The windowed falloff and the smooth cone (t squared between the cosines) in code; the range is a
culling bound, not a brightness. Light records: one 96-byte record per component, kept from EnTT signals and transform
changes with a change log the GPU copy follows; inactive lights keep a record marked not drawn; `MakeRecord` refuses
non-finite values; the spot's bounding sphere has two cases around 45 degrees; lights are placed where the scene draws
their entity (drawn transforms); `LightData` is 64 bytes, camera-relative, with the shadow slot and the source radius in
`SpotAngles`. The rule that a direct write to a light field must signal, like a transform write. Picking the sun and
filling the frame constants in code. Preview lighting: an editor view of a scene with no light gets a preview sun and
the default procedural sky. Imported lights: the glTF importer reads `KHR_lights_punctual` 1:1 (candela, lux), gives a
light without a glTF range 10 sqrt(I) meters, scales ranges with the model's Scale and clamps spot cones to 1 to 89
degrees. What Strata does not do here: no light cookies, IES profiles, light linking or lighting channels; every light
lights every surface in its range. A toy turns a list of lights into a uniform array. Figures: a spot's inner and outer
angles and a point light's range window as a sweep; preview lighting in the Scene view against the Game view.
Alternatives: one pass per light, several shadowed suns. How it is tested: the spot cone and units cases of
`GPU.SceneRenderer.Lighting`, `RendererComponentsTests.cpp`. Changing it safely: a new light type reaches the record,
`LightData`, the clusters and `ShadeLitSurface`; readers size `LightRecord` (96 bytes) by `sizeof`, and `LightData`
stays 64 bytes, mirrored by hand in `Lights.slang`. The exercises add a "lumens" helper for spot lights with a unit
test, and trace a light's change from its component to the record the GPU copy reads. Afterwards the reader can place
and tune lights and follow a component into a record and the frame constants.

**Leaves out.**

- The units of light → `light/units-exposure`
- Culling lights and assigning them to clusters → `light/many-lights`
- Source radius and sized highlights → `light/area-lights`
- Shadows of lights → `light/shadow-basics`
- The render scene's records and change logs in general → `draw/render-scene`
- The sky light and the preview sky → `light/sky`
- Interpolating fixed steps → `world/interpolation`
- The `ImportLights` setting of a glTF import → `assets/models-gltf`
- Placing lamps in a game → `make/lamps`

**Fit.** `fits`: about 4,550 words against L (5,000). Four excerpts and the record's contract take the most. Phase B
reads again the section on light components and records (W8r): what 0.8.0's rectangle lights add to the components,
`LightRecord` and `LightData`, and whether the entry on light cookies, IES profiles, light linking and lighting channels
still holds.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:74-84` | feature | home | The three light components, one sun per frame, the falloff and the cone, light records, the spot's bounding sphere, drawn transforms, `LightData`, preview lighting; the spot light's defaults are its own (20 cd and 15 m against the point light's 10 cd and 10 m, `Strata/src/Strata/Renderer/RendererComponents.h:53-54`, `:69-70`), and the page takes them from the generated components table and the excerpt, not from the item |
| `render-direct:341` | concept | home | Light sources: directional, point, spot; attenuation and range; the mistakes |
| `render-direct:433` | code | home | `Strata/src/Strata/Renderer/RendererComponents.h:17-78`: the light components as plain data with units in comments, defaults and range constants |
| `render-direct:444` | code | home | `Strata/shaders/Include/PBR.slang:194-207`: windowed inverse-square falloff and the spot cone |
| `render-direct:445` | code | home | `Strata/src/Strata/Renderer/RenderLights.cpp:44-85`: a light record, non-finite values refused, the spot's bounding sphere |
| `render-direct:446` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2557-2601`: picking the sun, the preview sun, the frame constants from the components |
| `render-direct:537` | figure | home | Sweep: a spot's inner and outer cone angles on a wall; a point light's range window |
| `render-direct:565` | figure | home | Preview lighting: an unlit scene in the Scene view against the Game view |
| `render-direct:595` | rule | home | Light records are kept from signals: a direct write to a light field must signal |
| `render-direct:616` | rule | home | Only one directional light shines, and only the first active sky light, height fog and post process apply |
| `render-direct:657` | hands-on | home | Exercise: a spot light "lumens" helper that converts to candela for a cone, with a unit test |
| `new:36` | not-done | home | Light cookies (projected textures), IES profiles, light linking and lighting channels: every light lights every surface in its range. Evidence: `git grep -niE -e cookie -e "light ?channel" -e "light ?layer" -e "light ?mask" -e "light ?link" 822a7a46 -- Strata/src Strata/shaders` finds only the DLL-directory cookie of `Strata/src/Platform/Windows/WindowsDynamicLibrary.cpp:21-36` and the socket notifier's cookie of `Strata/src/Platform/Windows/WindowsSocket.cpp:24-26`, `:549-571`; `git grep -nw IES 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `new:37` | hands-on | home | Exercise (trace it yourself): a point light's `Intensity` changed by `component.set`, followed with a debugger from the EnTT update signal that `RenderLights` connects, through the queued record built again by `MakeRecord` in `Sync`, to the change log that the GPU copy reads with `GetChanges`. Evidence: `Strata/src/Strata/Renderer/RenderLights.cpp:44-85`, `:91-98`, `:276`, `:315-340` |
| `render-direct:704-706` | term | home | Punctual light, range, inner and outer cone angle |
| `render-direct:710` | term | home | Light record |
| `render-direct:756` | term | home | Preview lighting |
| `render-indirect:62` | feature | home | Preview lighting as render-indirect lists it (`render-direct:84`) |
| `editor-core:697` | term | home | Preview lighting as the editor's inventory defines it (one glossary entry with `render-direct:756`) |
| `render-direct:49` | feature | use | The lights half of the glTF extensions, about 80 words: `KHR_lights_punctual` read 1:1, a light without a glTF range gets 10 sqrt(I) meters, ranges scale with the model's Scale, spot cones are clamped to 1 to 89 degrees (`Strata/src/Strata/Asset/GltfImporter.cpp:1828-1863`); the item's home is `light/materials`, and `assets/models-gltf` keeps the `ImportLights` setting |
| `render-direct:597` | rule | use | The rule's light half, under "Changing it safely": readers size `LightRecord` (96 bytes) by `sizeof`, and `LightData` stays 64 bytes, mirrored by hand in `Lights.slang` (`Strata/src/Strata/Renderer/SceneRenderData.h:259`, `:275`); the rule's home, with its material half, is `light/material-data` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Lux and candela | `light/units-exposure` | must |
| `EvaluateLight` and the forward shader | `light/brdf` | must |
| The render scene's records and change logs | `draw/render-scene` | must |
| Drawn transforms between fixed steps | `world/interpolation` | must |
| Components as registered data with properties | `world/reflection` | must |
| EnTT views | `world/ecs` | must |
| EnTT signals | `world/scene-graph` | must |
| The transform contract and change signals | `world/scene-graph` | must |
| Bounding spheres | `basics/math-geometry` | must |
| Camera-relative positions subtracted in double | `draw/mirrors-camera-relative` | must |
| The editor's Scene and Game views | `start/first-game` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `inner-outer-cone-angle` | Inner/outer cone angle | - |
| `light-record` | Light record | - |
| `preview-lighting` | Preview lighting | - |
| `punctual-light` | Punctual light | - |
| `range-light` | Range (light) | - |
