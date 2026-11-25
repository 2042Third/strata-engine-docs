# Brief: `make/lighting`

| Field | Value |
| --- | --- |
| Title | Lighting a scene: sun, sky and exposure |
| Kind | T |
| Size | L |
| Tracks | G, B |
| Needs | `make/prefabs` |
| From | gamedev "Lighting a scene" (§1.8: units, sky sources and presets, sun shadows, exposure, preview lighting, the luminance and albedo debug views; fog is `make/look`'s); render-direct "Lighting a scene in the editor (tutorial)" (the outdoor half); emission in nits; use home of light units, exposure, the sky as a light and the default template's lighting; Coin Run's level lit for play |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/lighting` — Lighting a scene: sun, sky and exposure

**Covers.** The page lights Coin Run for play and teaches light at the maker's level. It starts with what Basic 3D
already holds, because this page is the home of the default template's lighting: a Sun of 120,000 lux 40 degrees up
with soft shadows, a Sky with the physical atmosphere of the Clear preset, a Post Process with the Filmic tone curve,
automatic exposure and a compensation of +0.25, and why each value is real. Then, in this order, each idea with a step
and what to see. Light in real units, from zero: lux for the sun's light on the ground, candela for a lamp, nits for
the sky and for emission, with the reference values table (a sunny day, an office, a candle). Exposure in EV stops from
zero: each stop doubles or halves the light, so a table of powers of two stands in for logarithms. (1) Change the Sun to
60,000 lux: little changes, because automatic exposure follows. (2) Turn **Auto Exposure** off: at an **Exposure** of 0
the image is white; set it near -15 and back, which is G7's "break it and fix it"; turn Auto Exposure on again. (3) The
washed-out gray failure: turn the Sun off and see automatic exposure brighten the dark scene to gray; the fix with the
Auto Exposure limits; why a real sun needs **Auto Exposure Max EV** 16. (4) The sky's three sources on the Sky entity:
Atmosphere, Procedural, and Environment Map with an HDR sky from
`Samples/ThirdPerson/Assets/Environment/kloofendal_48d_partly_cloudy_puresky_1k.hdr` (Poly Haven, CC0), its **Extract
Sun** and **Remove Sun**, so the sun is not counted twice. (5) The presets in the Inspector's Sky section (nothing
selected): Clear, Hazy, Overcast and Golden Hour, one undo step each, which keep the sun's direction and set exposure
safely; the sun-to-sky ratio table explained (6 to 10 on a clear noon, below 0.3 overcast). What Strata does not do
here (`new:20`): no clouds, stars or moon; the atmosphere's haze is clear aerosol, and Overcast is a nearly uniform
procedural sky. (6) Turn the Sun with the
Rotate gizmo and watch the shadows follow. (7) Sun shadows at the maker's level: Cast Shadows, Shadow Distance (enough
for the 20 m level), Shadow Softness (the sun's size), Cascade Blend; point and spot shadows are `make/lamps`'. (8)
Preview lighting: in a new, unsaved scene with no light the Scene view still shows the objects lit while the Game view
is black; the rule that a scene with no light is unlit in the game. (9) The Luminance debug view: read the ground's EV
band; the Albedo view is `make/materials`' audit. (10) The coin's emission strength in nits, set against the reference
values. (11) Coin Run lit for play: the chosen preset, the sun turned so that coins cast readable shadows; save. At the
end the reader can read and set light in real units, choose a sky and its preset, set exposure on purpose and tell
preview lighting from real light; G7's lantern is `make/lamps`', fog is `make/look`'s.

**Leaves out.**

- Light units as physics: radiometry, photometry, conversions → `light/units-exposure`
- Metering, adaptation and the exposure key inside → `image/exposure`
- Pre-exposure → `image/pre-exposure`
- Tone mapping and the Filmic curve → `image/tone-mapping`
- The sky as a light inside, `HDRSun` and the atmosphere → `light/sky`, `light/atmosphere`
- Shadow mapping, cascades and the shadows view → `light/shadow-basics`, `light/sun-shadows-1`
- The lights, preview lighting inside → `light/lights`
- Measuring light and the other debug views → `light/measuring-light`
- Point and spot lights, their shadows and source radius → `make/lamps`
- Fog, the camera's image and post effects → `make/look`
- Reflections, probes and ambient occlusion → `make/reflections`
- Powers and logarithms from zero → `basics/numbers`

**Fit.** `fits`: about 5,100 words against L (5,000). Eleven steps at B0's length take most of it, with the template's
values read first, light units and EV stops taught from zero with their tables, the units map, nine pictures and two
exercises. The shadows stay at the maker's four controls and the debug views at one.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:106` | feature | home | The balanced default template: Basic 3D's sun, sky and exposure, read first; the home of the default template's lighting |
| `gamedev:106` | feature | home | Light units: lux for the sun, candela for lamps, nits for the sky and emission; Source Radius named for `make/lamps` |
| `gamedev:107` | feature | home | The sky's three sources, Extract Sun and Remove Sun |
| `gamedev:108` | feature | home | The four sky presets in the Inspector's Sky section |
| `gamedev:110` | feature | home | Sun shadows at the maker's level; point and spot shadows left to `make/lamps` |
| `gamedev:114` | feature | home | The Luminance debug view in EV; the Albedo view named for `make/materials` |
| `gamedev:118` | feature | home | Preview lighting: editor views light a scene with no light; the game does not |
| `gamedev:311` | concept | home | Light, units and exposure: real units, EV like a camera, automatic exposure; the two mistakes |
| `gamedev:461` | figure | home | Basic 3D under each sky preset |
| `gamedev:462` | figure | home | Auto Exposure on and off; the washed-out gray failure and its fix |
| `gamedev:463` | figure | home | Preview lighting in the Scene view against the black Game view |
| `gamedev:464` | figure | home | The Luminance view on Coin Run's level (the Albedo view is shown by `make/materials`) |
| `gamedev:506` | rule | home | A scene with no light is unlit in the game, though editor views show preview lighting |
| `gamedev:508` | rule | home | Automatic exposure brightens dark scenes to gray; a real sun needs Max EV 16 |
| `gamedev:540` | hands-on | home | G7's sky and exposure half: each preset, exposure broken at -15 and fixed; the lantern is `make/lamps`' |
| `gamedev:597` | term | home | Preview lighting |
| `gamedev:598` | term | home | Lux, candela, nits |
| `gamedev:599` | term | home | Exposure (EV) |
| `render-indirect:531` | hands-on | home | Step 4: each sky source, the HDR map with Extract Sun, the atmosphere |
| `render-indirect:532` | hands-on | home | Step 5: the four presets and the ratio table |
| `new:20` | not-done | home | Clouds, stars and a moon: the atmosphere's haze is clear aerosol, and the Overcast preset is a nearly uniform procedural sky. Evidence: `Strata/src/Strata/Renderer/SkyPresets.cpp:35-37`; `git grep -niw -e moon -e stars -e starfield -e cloud -e clouds 822a7a46 -- Strata/src Strata/shaders` finds only that comment, a tooltip's full-moon illuminance (`Strata/src/Strata/Renderer/RendererComponents.cpp:289`) and two comments on cloud placeholder files (`Strata/src/Platform/Windows/WindowsFileSecurity.h:28`, `Strata/src/Strata/Core/Platform.h:104`) (run at the pin) |
| `render-direct:37` | feature | use | Emission in nits, for the coin's glow |
| `render-direct:84` | feature | use | Preview lighting |
| `render-direct:101-102` | feature | use | Photometric units on one scale; the exposure model, at the maker's level |
| `render-direct:105` | feature | use | The table of reference values |
| `render-direct:120` | feature | use | Cascade Blend, as a maker's control |
| `render-direct:159-161` | feature | use | The presets; Extract Sun and Remove Sun; the sun-to-sky ratio |
| `render-direct:178` | feature | use | The lighting debug views, Luminance among them |
| `render-direct:278` | concept | use | Light as a quantity, at the maker's level |
| `render-direct:293` | concept | use | Exposure and EV, at the maker's level |
| `render-direct:480` | figure | use | The light units map |
| `render-direct:539-540` | figure | use | The same scene at two lights and two exposures; the Luminance view |
| `render-direct:555` | figure | use | The three sky sources side by side |
| `render-direct:564-565` | figure | use | Extract Sun before and after; preview lighting |
| `render-direct:571` | rule | use | Every intensity has a unit |
| `render-direct:616` | rule | use | Only one directional light shines |
| `render-direct:624` | rule | use | A real sun needs automatic exposure with Max EV 16 |
| `render-direct:639` | hands-on | use | Each preset with its ground illuminance and ratio, as an exercise |
| `render-direct:648` | hands-on | use | Extract Sun and the shadows that appear, as an exercise |
| `render-image:66` | feature | use | Manual exposure |
| `render-image:88` | feature | use | The Min and Max EV limits of automatic exposure |
| `render-image:95` | feature | use | EV100 and its reference table |
| `render-image:99` | feature | use | Presets that set exposure safely |
| `render-image:101` | feature | use | The Luminance view |
| `render-image:334` | concept | use | Automatic exposure's intent, at the maker's level |
| `render-image:486-487` | figure | use | The manual exposure sweep; automatic exposure on and off |
| `render-image:587` | hands-on | use | Find your exposure |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Components, the Inspector and scene settings | `make/scenes-entities` | must |
| Turning things with the Rotate gizmo; degrees | `make/transforms-units` | must |
| Materials and emission as a color and a strength | `make/materials` | must |
| The Scene view's chips and the Game view | `make/editor-tour` | must |
| Powers and logarithms | `basics/numbers` | helps |

**Starting state.** The end state of `make/prefabs` (`startsFrom {"tutorial": "make/prefabs"}`): the level with five
coin instances, the gold and metal materials, and Basic 3D's own lighting. The HDR sky comes from the release's
`Samples/ThirdPerson/Assets/Environment/` (credited in that sample's `CREDITS.md`); the scene with no light of step 8
is not saved. The page ends with Coin Run lit for play.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `exposure-ev` | Exposure (EV) | - |
| `candela` | Candela (use) | cd |
| `lux` | Lux (use) | lx, nits |
| `preview-lighting` | Preview lighting (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-14 | should | shape | `make/lighting` (step 8) | Step 8 shows preview lighting "in a new, unsaved scene with no light", the Game view black. **File ▸ New Scene** makes an empty scene: without a camera the Game view shows the notice that no camera is primary, not black, and without an object nothing shows lit. The steps that add them are not in the list. | Step 8 adds **+ ▸ Cube** and **+ ▸ Camera** (a new camera is Primary) to the new scene before comparing the views, and says that New Scene first asks about Coin Run's unsaved changes (about 50 words). | `allocation/make-a.md:719-720`; `StrataEditor/src/EditorLayer.cpp:1486-1487`; `StrataEditor/src/Editor/EditorSceneCommands.cpp:380`; `Strata/src/Strata/Scene/Components.h:139`; `Docs/Manual/GameView.md:19-21` |
| critic-make-a-16 | should | stale-item | `make/lighting` (step 7), `make/physics` (steps 1, 7 and 8), `make/input` (step 4), `make/export` (step 8) | Labels the steps name differ at the pin. The sun's softness is **Angular Diameter** in the Inspector (stored as `ShadowSoftness`); the component is **Rigid Body**; the export's pruning box reads **Leave out unused assets**, not Prune; and Project Settings lists its pages under Physics (Collision Layers, Simulation, Timing), Input (Input Actions) and Rendering (Graphics Quality). | The steps use the pin's labels and paths (**Project Settings ▸ Physics ▸ Collision Layers**); `make/lighting` keeps "the sun's size" as the meaning of Angular Diameter (no words added). | `allocation/make-a.md:718`, `:1261-1262`, `:1280`, `:1148`, `:1707`; `StrataTests/Architecture/ComponentSchema.json:480`, `:2173`; `StrataEditor/src/UI/ExportDialog.cpp:311`; `Strata/src/Strata/Scene/ProjectCollisionLayers.cpp:59-60`; `Strata/src/Strata/Physics/PhysicsSimulationSettings.cpp:55-56`; `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:78-80`; `Strata/src/Strata/Input/InputActionSet.cpp:627-628`; `Strata/src/Strata/Renderer/RendererQuality.cpp:712-713` |
