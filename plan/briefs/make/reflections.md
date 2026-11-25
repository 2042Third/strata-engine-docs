# Brief: `make/reflections`

| Field | Value |
| --- | --- |
| Title | Sky light, ambient occlusion and reflections in your game |
| Kind | H |
| Size | L |
| Tracks | G |
| Needs | `make/project-coin-run` |
| From | render-indirect "Using sky, AO and probes in your game", "Shiny worlds: a wet-floor tutorial" (the sky's light on surfaces, AO, probes and their bakes, times of day, a wet floor with screen-space reflections; choosing the sky source and its preset is `make/lighting`'s) |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/reflections` — Sky light, ambient occlusion and reflections in your game

**Covers.** The goal: make shaded sides, creases and shiny floors look right with the light that comes from the sky and
the surroundings, not from lamps. What must be true first: a sky from `make/lighting`, and the page's own example, a
courtyard of built-in cubes (a room with a doorway, a plaster wall, a dark soil bed, a polished metal sphere and a
smooth floor) from the starting checkpoint. The steps, in order. The sky's light on surfaces: what lights the shaded
side of the room besides the sun, seen in the **Indirect** debug view. Ambient occlusion on the Post Process: Radius,
Intensity and Multi Bounce on the plaster corner against the soil corner, compared in the **AO** view and the lit image;
AO darkens only the indirect light and sees only what is on screen. A Reflection Probe in the room: add it, fit its box
(Extents) to the walls by their sizes, because the Scene view draws no box for a probe (the fit is checked after the
bake, by the reflections), **Bake** it in the Inspector (or **Bake Reflection Probes** in the Sky section with nothing
selected, `StrataEditor/src/Panels/InspectorPanel.cpp:1721`), Box Projection on and off; a second probe at the doorway
with Priority and Blend Distance. Bake again after the light changed, and each bake adds a bounce until the pictures
stop changing (the Showcase bakes eight times). Why, in two sentences: a probe is a picture the editor takes, never the
running game, and it leaves out the sun's disk and the lamps' highlights, which the lights draw themselves. A wet floor:
water's IOR 1.33 and a roughness of 0.02 to 0.06, Screen Space Reflections on the Post Process and its Max Roughness;
its limits (only what is on screen is reflected, a ball shows a crescent of its back, glass gets none); Medium against
High with the Scene view's quality chip (half resolution that needs TAA, against every pixel), in one sentence with a
link forward to `make/quality`, which teaches the presets and TAA. Times of day, one section: a day and night script
turns the sun under the Atmosphere sky (the sky's light follows, refreshed every half degree), read in the Open World's
`DayNight.h` (the first excerpt): the sun's angle from the hour, turned in steps of at most a quarter degree so that its
shadow cascades are drawn again only when it moved, the same light as the moon at night, and campfires found by tag and
lit at dusk; a probe's picture stays fixed, so each time of day gets its own probe set, switched with `SetActive`, the
old set kept on for a second with the new one's Priority raised, and the captures kept loaded with
`Assets::GetLoadProgress`, as the Showcase's `Outpost` script does (the second excerpt). The section's exercise, G16,
ports the day and night script to the courtyard. What Strata does not do here: a gizmo for probes, and cube-map texture
assets (skies and captures are equirectangular HDR textures, made into cubes at run time). Result: the courtyard at noon
and at dusk. Variations: an open yard (Box Projection off), a cave, a probe per room of a house.

**Leaves out.**

- Choosing the sky source and its preset → `make/lighting`
- How the sky's light reaches surfaces (image-based lighting, the split sum) → `indirect/ibl`
- How AO is computed without history → `indirect/ao`
- How probes are gathered, blended, converted and baked → `indirect/probes`
- How screen-space reflections are traced and validated → `indirect/ssr`
- Bounce light traced in the world → `make/gi`
- The Graphics Quality presets and the anti-aliasing choices → `make/quality`

**Fit.** `fits`: about 4,900 words against L (5,000). Six step sections (sky light, AO, probes, bakes, the wet floor,
times of day) with about 20 steps, the two excerpts (`DayNight.h` and the `Outpost` script's probe sets), the limits of
probes and SSR and the times-of-day section's exercise (G16) take the most. The page carries no mark, but 0.8.0's
reflection work (R1, R2) is already at the pin; the pin move's diff decides what is read again.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:111` | feature | home | Reflection probes: the box, Bake, Box Projection, time-of-day probe sets |
| `gamedev:112` | feature | home | Screen-space reflections on the Post Process |
| `gamedev:113` | feature | home | Ambient occlusion (radius, multi-bounce); its other half, global illumination, is tried on `make/gi` |
| `gamedev:387` | code | home | `Samples/Showcase/Scripts/Outpost.cpp:205-267`: `SetProbes`, the one-second hold and `SwitchProbes`, with the stations' table at `Samples/Showcase/Scripts/Stations.h:39-43` (the inventory's 38-42 is one line early) |
| `gamedev:603` | term | home | Reflection probe, bake |
| `render-direct:645` | hands-on | home | A day script that turns the sun under the Atmosphere sky; the environment refreshed every half degree; the sky at sunset |
| `gamedev:386` | code | home | `Samples/OpenWorld/Scripts/DayNight.h:16-73`: the sun's angle from the hour, turned in steps of at most `StepDegrees` so that its shadow cascades are drawn again only when it moved; the same light as the moon at night, opposite the sun and far dimmer; campfires found by tag and lit at dusk with `SetProperty` (the inventory's 16-72 leaves out the class's closing line) |
| `gamedev:549` | hands-on | home | G16, the times-of-day section's exercise: a day and night script that drives the sun under the atmosphere and lights campfires by tag, ported from `DayNight.h` to the courtyard |
| `new:11` | not-done | home | A gizmo for reflection probes: the Scene view draws no box for a probe's Extents, so the reader fits Extents and the entity's scale by the walls' sizes and checks the fit after a bake by the reflections. Evidence: `Strata/src/Strata/Renderer/SceneGizmos.cpp:224-345` draws lights and cameras; `git grep -n "\.Gizmo(" 822a7a46 -- Strata/src StrataEditor/src` finds only the colliders and the character controller (`Strata/src/Strata/Physics/PhysicsComponents.cpp:143-184`) and the call that draws them (`Strata/src/Strata/Renderer/SceneGizmos.cpp:176`) |
| `new:12` | not-done | home | Cube-map texture assets: skies and probe captures are equirectangular HDR textures, made into cubes at run time, and a `.cube` file is a color lookup, not a cube map. Evidence: `Strata/src/Strata/Asset/AssetTypes.h:14-31`, no cube texture type (`ColorLookup`, `:30`, is the `.cube` files'); `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp:20`, `:464` (a capture is an equirectangular HDR texture, converted to a cube); `Docs/Roadmap.md:947` |
| `render-indirect:533` | hands-on | home | G3: AO's radius, intensity and multi-bounce on white and dark materials, in the `ao` view and lit |
| `render-indirect:534` | hands-on | home | G4: a probe in a room, its box fitted, baked, Box Projection, a second probe with Priority and Blend Distance |
| `render-indirect:535` | hands-on | home | G5: bakes repeated after a change of the light until the bounces settle |
| `render-indirect:536` | hands-on | home | G6: two probe sets switched by a script with `SetActive`, captures kept loaded |
| `render-indirect:537` | hands-on | home | G7: a wet floor with IOR 1.33, low roughness and SSR; Medium (TAA) against High; the crescent and the screen's edge |
| `render-indirect:53` | feature | use | The first active Sky Light lights the scene |
| `render-indirect:96`, `render-indirect:99`, `render-indirect:101`, `render-indirect:103-104` | feature | use | AO's quality samples, its radius held on screen, multi-bounce, its fields, and that it applies to indirect light only |
| `render-indirect:118`, `render-indirect:120-121`, `render-indirect:123` | feature | use | The probe's fields, two probes blended, box projection, 128 or 256 texels per face by preset |
| `render-indirect:129-131` | feature | use | The bake, bounces by baking again, probe sets per time of day |
| `render-indirect:137-138`, `render-indirect:147`, `render-indirect:149` | feature | use | SSR's fields, its quality row (Off, Checkerboard with TAA, Spatial), the first frame without reflections, none on transparent surfaces |
| `render-indirect:189` | feature | use | The Indirect and AO debug views |
| `render-direct:154`, `render-direct:157` | feature | use | The physical atmosphere and its environment refreshed as the sun turns |
| `render-indirect:230`, `render-indirect:269`, `render-indirect:286`, `render-indirect:300` | concept | use | What indirect light is; AO; probes and their mistakes (a box that does not fit, probes expected to update in play); the fallback from SSR to probes to the sky |
| `render-indirect:433`, `render-indirect:435`, `render-indirect:437` | figure | use | AO on and off, AO radius, multi-bounce on plaster and soil |
| `render-indirect:439`, `render-indirect:441-442`, `render-indirect:445` | figure | use | A probe on and off in the Showcase's hut, box projection, Blend Distance, bakes 1, 2 and 8 |
| `render-indirect:446`, `render-indirect:451` | figure | use | SSR off, Checkerboard and Spatial; the crescent of a ball's back |
| `render-direct:556` | figure | use | The atmosphere at sun elevations from 60 to -6 degrees |
| `render-indirect:479`, `render-indirect:486`, `render-indirect:494`, `render-indirect:496`, `render-indirect:500` | rule | use | AO darkens indirect light only; AO never darkens what SSR found; Checkerboard needs TAA; probes are baked in the editor; a bake replaces only its own capture |
| `render-indirect:591`, `render-indirect:602-604`, `render-indirect:608` | term | link | Ambient occlusion; extents and blend distance, box projection, probe priority; SSR |
| `gamedev:89-90` | feature | use | Water's IOR 1.33 and roughness 0.02 to 0.06 from the material guidance (home `make/materials`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The sky sources, the Atmosphere and its presets; the sun's direction | `make/lighting` | must |
| The Post Process component and its exposure | `make/lighting` | must |
| The debug view chip | `make/lighting` | must |
| Base color, metallic, roughness and IOR on a material | `make/materials` | must |
| Entities from the Hierarchy, position and scale in the Inspector | `make/scenes-entities` | must |
| Finding entities, `SetActive`, `SetProperty` and `Assets::GetLoadProgress` from a script | `make/scripting-scene` | must |
| `OnUpdate` and `deltaTime` | `make/script-loop` | must |
| Undo of a bake | `make/project-files` | helps |
| The Graphics Quality presets and TAA as an anti-aliasing | `make/quality` | helps |

**Starting state.** The page's starting checkpoint, downloadable: a new project from the Basic 3D template whose scene
holds the courtyard (a room of built-in cubes with a doorway, a white plaster wall, a dark soil bed, a polished metal
sphere and a smooth floor) and the Atmosphere sky with the Clear preset. No probe yet.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `bake` | bake | - |
| `reflection-probe` | Reflection probe (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b2-2 | must | shape | `make/commands` (Starting state; `animation:185`, `animation:190`, `worlds-runtime:111`, `render-indirect:540`) | The page starts from Coin Run's end checkpoint: a rolling ball and coins. That project has no skinned model with clips, no world, no reflection probe and no global illumination, so the steps `animation.createController`, `animation.preview`, `world.setLayers`, `lighting.bakeProbes` and the GI capture have nothing to act on. | The Starting state names the project each section opens, each a download of the book (the end checkpoints are planned already; the last two are states of those pages' steps, which the book adds as downloads): Coin Run's end for the scatter, the batch and the store-page captures; the end checkpoint of `make/animation` (its robot and clips) for the controller and the preview; the end checkpoint of `make/large-worlds` for `world.setLayers`; the courtyard of `make/reflections` with its probe, and the room of `make/gi` with Global Illumination on, for the bake and the GI view. About 60 words. | `allocation/make-b2.md:800-807`, `:869-870`, `:875-876`; `outline-1.md:196` (Coin Run as a rolling ball); pin: `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153-157` (each state plays an animation clip); `StrataEditor/src/Editor/EditorWorldCommands.cpp:670-673` (a world's layer list); `StrataEditor/src/Editor/EditorLightingCommands.cpp:872-883` (the scene's probes) |
| critic-make-b2-10 | should | stale-item | `make/reflections` (`gamedev:387`; Covers, times of day) | The Covers says the captures are kept loaded with `Assets::GetLoadProgress` "as the Showcase's `Outpost` script does (the second excerpt)". The excerpt, `Outpost.cpp:205-267`, holds `SetProbes`, the hold and `SwitchProbes`, and no `GetLoadProgress`: the requests are made by `RequestCaptures` and `PollCaptures`, lines 154 to 189. | Add a new item of type code for `Samples/Showcase/Scripts/Outpost.cpp:154-171`: each probe's Capture read with `GetProperty`, and the first `GetLoadProgress` call, which loads it and keeps it loaded while the scene plays. Or say it in prose and drop "the second excerpt" from the sentence. About 150 words with the quote. | `allocation/make-b2.md:122-124`, `:151`, `:161`; pin: `Samples/Showcase/Scripts/Outpost.cpp:154-171`, `:174-189`, `:205-267`; `StrataScriptCore/Include/StrataScript/Scene.h:53-61` |
| critic-make-b2-11 | should | missing-item | `make/reflections` (times of day; `render-indirect:129-131`, `render-indirect:536`, `gamedev:549`) | The page gives each time of day its own probe set, but not how a reader bakes one. A bake renders the edited scene as it is and is refused while playing, so the day script does not run then; it draws every active probe's capture; and **Bake Reflection Probes** bakes every active probe. A set is therefore baked with the sun turned to its hour by hand and only that set active; otherwise one set's light leaks into the other's captures. | A step in the times-of-day section: turn the sun to the hour (or apply the Golden Hour preset), turn the other set off, bake this set until it settles, then the next, as the Showcase's bake does for each station. About 100 words. | `allocation/make-b2.md:118-124`, `:159-161`, `:166`; pin: `StrataEditor/src/Editor/EditorLightingCommands.cpp:872-883`; `StrataEditor/src/Panels/InspectorPanel.cpp:1716-1724`; `Tools/GenerateShowcaseTerrain.py:83-86`, `:2125-2128` |
| critic-make-b2-12 | should | other | `make/reflections` (`gamedev:386`; G16, `gamedev:549`) | The first excerpt's light values are not the real units the book teaches: `SunIntensity` 3 lux, `MoonIntensity` 0.05 lux (no script field, so only the code changes it) and campfires of 6 cd. The courtyard's sun is the Clear preset's 120,000 lux, `make/lamps` taught a 0.2 lux moon, and the Showcase's own script uses 120,000 lux. Ported as it stands, G16 drops the courtyard's sun to 3 lux, and probes baked under 120,000 lux then outshine it. | Two sentences after the excerpt: the sample's values are small but agree with each other, and automatic exposure and the atmosphere, which follow the sun, hide the scale; G16's port sets `SunIntensity` to 120,000 in the Inspector, the moon to about 0.2 lux in the code, and the campfires in candela as `make/lamps` taught. About 70 words. | `allocation/make-b2.md:7`, `:120-121`, `:154-155`; `allocation/make-a.md:700`; pin: `Samples/OpenWorld/Scripts/DayNight.h:19-26`, `:61`, `:66`; `Samples/OpenWorld/Scripts/DayNight.cpp:3-12`; `Samples/Showcase/Scripts/Stations.h:47-48`; `StrataEditor/src/Panels/InspectorPanel.cpp:1693` |
| critic-make-b2-13 | should | thin-home | `make/reflections` (the probe section; `render-indirect:118`, `render-indirect:534`) | The page fits the probe's box (Extents) to the walls "by their sizes", but Extents are half sizes, times the entity's scale: the default (5, 5, 5) is a 10 m box, and a room's width typed in makes a box twice too large. No menu creates a probe: the Hierarchy's **+** menu has no Reflection Probe, so the reader adds one with Add Component on an empty entity. | The probe step names both: **+ ▸ Empty**, then **Add Component ▸ Reflection Probe**; Extents are half the room's width, height and depth, with one example (a room 6 m wide, 3 m high and 4 m deep gets 3, 1.5, 2). About 50 words. | `allocation/make-b2.md:108-112`; pin: `Strata/src/Strata/Renderer/RendererComponents.h:162`; `Strata/src/Strata/Renderer/RendererComponents.cpp:434-435`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:100-113`; `StrataEditor/src/Panels/InspectorPanel.cpp:448` |
| critic-make-b2-23 | could | order | `make/reflections` (`gamedev:386`, `gamedev:387`) | The two excerpts use C++ that no page of track G teaches and no Assumes row names: `static_cast` (`Outpost.cpp` lines 224, 225, 241, 249; `DayNight.h` line 68) and `std::fmod` and `std::clamp` (`DayNight.h` lines 33, 56, 58); a `for` over a braced list (`Outpost.cpp` lines 207, 256) goes one step past the range-based `for` of `basics/programming-2`. The homes, `basics/cpp-modern` and `basics/cpp-generic`, are not on track G. | Assumes rows of depth `helps` that name those two pages (N2), and each feature said in one sentence at its first use, as the `cpp-feature` aside asks. About 80 words. | `allocation/make-b2.md:151`, `:154`, `:181-191`; `style.md:647`, `:658-659`; `allocation/basics-a.md:237`, `:943`; pin: `Samples/Showcase/Scripts/Outpost.cpp:207`, `:224-225`, `:241`, `:249`, `:256`; `Samples/OpenWorld/Scripts/DayNight.h:33`, `:56`, `:58`, `:68` |
