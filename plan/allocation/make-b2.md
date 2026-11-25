# Allocation: make-b2

## `make/lamps` — Lamps: point, spot and area lights and their shadows

**Covers.** Track G meets lights other than the sun here, on a small night scene of the page's own: a yard with a hut,
a sign and four lantern posts, built from built-in meshes in the starting checkpoint. The page teaches, in this order.
First the night: the sun dimmed to moonlight (about 0.2 lux, from the reference values), the exposure set by hand in EV
stops as `make/lighting` taught, then given back to Auto Exposure. Then one lamp: a Point Light from the Hierarchy's
**+** menu; its Intensity in candela, with the recipe that a lamp of 800 lumens is about 64 cd (lumens are about 12.6
times the candela of a point light); its Color; its Range, which ends the light smoothly and bounds its cost, and is no
brightness knob; and a bulb beside it as an emissive material in nits. Then a Spot Light on the sign: Inner and Outer
Cone Angle, and the rule that its candela is along its axis, so a narrower cone is not brighter. Then the lantern as a
prefab (post, housing, bulb and the light as a child), placed four times. Then shadows: Cast Shadows on each lantern,
Shadow Filter Radius and the two biases, and the pitfall that the lantern's own housing shadows its light (Cast Shadows
off on that mesh); how many lamps cast shadows at once (16 in view, the nearest and largest first; 4 at the Low preset)
and that each shadowed point light draws six views; the preset's fact is one sentence with a link forward to
`make/quality`, which teaches the presets. Then Source Radius (0.04 m for a lantern's bulb): it widens only
the highlight on shiny and wet ground, and neither softens the shadow nor spreads the light. Then the moving lamp: the
`Spinner` script of `make/first-script` turns the arm of one lantern, and an input action switches it on and off with
`SetProperty("PointLight", "Intensity", ...)`; the viewport's **Stats** chip shows the shadow draw calls rise while it
moves, because a still lamp's shadow views are kept and a moving one's are drawn again each frame. What Strata does not
do here, in one paragraph: light cookies, IES profiles, light linking and lighting channels (every light lights every
surface in its range). The last section, area lights (0.8.0's rectangle lights), is written in phase B from the release.
The exercise: the hut's inside lit for the night with a 1 cd candle and a lamp of 800 lumens, the exposure set by hand.
At the end the reader can light a night scene with point and spot lights in real units, give lamps shadows, and keep
their cost down.

**Leaves out.**

- The sun, the sky, exposure in EV and sun shadows → `make/lighting`
- How the light units are defined and converted → `light/units-exposure`
- How lights are stored, culled and gathered per pixel → `light/lights`, `light/many-lights`
- The shadow atlas, its tiles, caches and fades → `light/local-shadows`
- Why a sized highlight keeps its energy; how rectangle lights are shaded → `light/area-lights`
- What the presets are and what each costs → `make/quality`
- Measuring a game's frame → `make/performance`
- Lights that follow a time of day → `make/reflections`

**Fit.** `fits`: about 4,400 words against L (5,000). Seven step sections of about 19 steps, each with its picture and
its "If you do not see it", the candela recipe, the shadow budget and the exercise take the most; the not-done paragraph
is about 50 words. Phase B adds the section on area lights from 0.8.0's rectangle lights (their component, units,
Inspector and script surface, and their soft shadows), and looks again at the number of shadowed lamps and the redraw
budget of the local-lights stream, whether a moving lamp still redraws all its views, the two not-done entries of
`light/area-lights`, and this page's not-done entry (light cookies, IES profiles, light linking and lighting
channels).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:644` | hands-on | home | The lantern yard: four shadowed point lights with Source Radius 0.04 m, one moved by a script; the shadow draws read on the viewport's Stats overlay instead of `renderStats`, which only a command returns |
| `new:10` | not-done | home | Light cookies, IES profiles, light linking and lighting channels: every light lights every surface in its range, and no projected texture or measured profile shapes a lamp's light; what a lamp has instead is a spot's cone, its Range and Cast Shadows on the meshes that should block it. Evidence: `git grep -niE -e cookie -e "light ?channel" -e "light ?layer" -e "light ?mask" -e "light ?link" 822a7a46 -- Strata/src Strata/shaders` finds only the DLL-directory cookie of `Strata/src/Platform/Windows/WindowsDynamicLibrary.cpp:21-36` and the socket notifier's cookie of `Strata/src/Platform/Windows/WindowsSocket.cpp`; `git grep -nw IES 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `new:21` | hands-on | home | Exercise, done in the editor: the hut lit for the night inside, a 1 cd candle on a table and a lamp of 800 lumens (about 64 cd) at the doorway, each Range fitted to the room, the exposure set by hand and read in the Luminance view. Evidence: `Docs/Manual/Lighting.md:42-43` (a household lamp of 800 lumens 64 cd, a candle 1 cd); `Strata/src/Strata/Renderer/RendererComponents.cpp:325` |
| `gamedev:106` | feature | use | Point and spot lights in candela and Source Radius for highlights, as a maker sets them (home `make/lighting`) |
| `gamedev:110` | feature | use | Cast Shadows on points and spots, at most 16 in view (home `make/lighting`) |
| `gamedev:540` | hands-on | use | G7's lantern point light with shadows; its sky presets and exposure are `make/lighting`'s |
| `render-direct:76-79` | feature | use | The Point and Spot Light fields with their defaults (10 cd, 10 m, Cast Shadows off), the windowed falloff to Range and the smooth cone |
| `render-direct:61` | feature | use | Sized sources widen the highlight only |
| `render-direct:105` | feature | use | The reference values: moon, lamp and candle |
| `render-direct:142`, `render-direct:144` | feature | use | The redraw budget and fade-in of shadowed lamps; at most 16 shadow slots |
| `render-direct:193` | feature | use | `MaxShadowedLocalLights`: 4 at Low, 16 at the other presets |
| `render-direct:217` | feature | use | Area lights at the pin: none in the engine; the section is written in phase B |
| `render-direct:341` | concept | use | Light sources and their range; the mistake of huge ranges |
| `render-direct:347` | concept | use | Sized sources; the mistake of a large Source Radius used as softer light |
| `render-direct:390` | concept | use | Shadows of lamps; the mistakes of a lamp model in its own light and of a moving light thought free |
| `render-direct:640` | hands-on | use | The night scene: a 0.2 lux moon, a 64 cd lamp of 800 lm, a 1 cd candle, exposure by hand then automatic |
| `render-direct:536-537` | figure | use | The Source Radius sweep on wet ground; the spot's cone angles on a wall |
| `render-direct:553` | figure | use | Point light shadows on and off, Shadow Filter Radius 0 against 8, the lamp casting into its own light |
| `render-direct:573` | rule | use | A spot light's candela is along its axis |
| `render-direct:593` | rule | use | A light's size widens only its highlight |
| `render-direct:614` | rule | use | Keep the lamp's mesh out of its own light's shadow |
| `render-direct:696`, `render-direct:698` | term | link | Candela, lumen |
| `render-direct:704-707` | term | link | Punctual light, range, inner and outer cone angle, source radius |
| `render-direct:829` | open | use | Area lights and the local-lights stream were branches at the pin: phase B writes the area-light section from 0.8.0 |
| `render-scene:184` | feature | use | The viewport's Stats overlay (the **Stats** chip, `StrataEditor/src/Panels/ViewportPanel.cpp:605`), with its shadow draw calls |
| `render-scene:555` | hands-on | use | Cast Shadows per mesh renderer, here on the lantern's housing |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Light units: lux, candela, nits; exposure in EV stops | `make/lighting` | must |
| The sun, its shadows and the debug view chip | `make/lighting` | must |
| Emission as a color and a strength | `make/materials` | must |
| Entities from the Hierarchy's **+** menu, components in the Inspector | `make/scenes-entities` | must |
| Prefabs and their instances | `make/prefabs` | must |
| Attaching and building a script; the `Spinner` script | `make/first-script` | must |
| `OnUpdate` and the frame | `make/script-loop` | must |
| An entity's components and properties from a script (`SetProperty`) | `make/scripting-scene` | must |
| Input actions read by a script | `make/input` | must |
| The Graphics Quality presets (Low draws the shadows of four lamps) | `make/quality` | helps |

**Starting state.** The book's start checkpoint of the tutorial file, downloadable: a new project from the Basic 3D
template whose scene `Scenes/Yard.stscene` holds a yard of built-in meshes (the ground, a hut of cubes with a doorway, a
sign board, four lantern posts of cylinders and a lantern arm on one of them). No light besides the template's sun;
nothing of Coin Run.

**Command-only steps.** none

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

## `make/gi` — Trying global illumination

**Covers.** The goal: see what Strata's experimental global illumination adds to a room and where it fails, so that a
game maker can decide whether a game's interiors use it. What must be true first: a project at the High or Ultra preset
(High is a new project's), because Low and Medium draw no global illumination, said in one sentence with a link forward
to `make/quality`, which teaches the presets. The steps: build a closed room of built-in cubes with walls 0.3 m thick
and a window toward the sun (G8), and a red floor; turn on Global Illumination on the Post Process; see the sunlit floor
light the walls and the ceiling and the red floor tint them; read the four views of the debug view chip (GI: the bounce
light on white surfaces; Open: how much of the sky a surface sees; Voxels: the voxel copy of the room; Probes: the
probes, dead ones dark red); make one wall 10 cm thick and see it in the error color of the Voxels view and lit from
both sides; frame the camera elsewhere and back, and watch the light fill in over about twelve frames; turn the sun and
see the bounce follow in the same frame; change Global Illumination Intensity; set the view to Medium with the quality
chip and see the image exactly as without it. The design decision in one sentence: global illumination traces the world,
never the screen, so it sees what is off screen and needs no history (linking `indirect/problem`). What it cannot do
yet, as the page lists it: gaps and ledges thinner than two voxels go dark, the light fades out 7.5 to 9.5 m around the
camera (outdoors the edge shows), Low bounces once and is too dark, round objects read a little dark at their sides, it
costs about 4 ms at 3840 x 2160 at High, lamps and moving or skinned objects add no bounce light, and the bounce light
is diffuse only, never in reflections; the rest of the not-done entry (no Ultra level, no textured albedo per voxel, no
hardware ray queries, no nested probe-field levels or denser probes near surfaces) in one sentence with a link to
`indirect/gi-limits`. Result: the room with and without bounce light. Variations: a room lit by an emissive ceiling
panel; an outdoor yard, where the field's edge shows; global illumination turned on only in a game's interior scenes.
The exercise: the thinnest wall that keeps the light out, found in steps of 5 cm (two voxels, 20 cm at High).

**Leaves out.**

- Indirect light from the sky, AO, probes and SSR → `make/reflections`
- How the world is voxelized → `indirect/gi-voxels`
- How radiance cascades gather the light → `indirect/gi-cascades`
- Everything global illumination does not do, with its evidence → `indirect/gi-limits`
- Why tracing the world and never the screen → `indirect/problem`
- The presets and the Global illumination row → `make/quality`

**Fit.** `fits`: about 3,250 words against M (3,000): ten steps with the four views, the list of limits with its
not-done sentence, three variations and the exercise take the most. Phase B must look again at all of it, because
0.8.0 changes it: the views, the voxel size and the wall thickness, the frames the light takes to settle, the fade
distances, the cost, Low's behaviour, whether lamps and moving objects join, and the list of limits with its not-done
entry (global illumination from local lights and from moving or skinned objects, specular light from it, and the rest
of the W8 table's row).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:538` | hands-on | home | G8: a closed room with a window and walls of at least 20 cm under GI at High; the `gi`, `open`, `voxels` and `probes` views; a wall too thin |
| `new:13` | not-done | home | Global illumination from local lights and from moving or skinned objects; specular light from global illumination (the field changes only the diffuse indirect light), the open share in specular occlusion, an Ultra level, textured albedo per voxel, hardware ray queries for global illumination, nested probe-field levels and denser probes near surfaces: the page's list of what it cannot do yet, in a maker's words. Evidence: `Docs/Plans/Wave8/specs/radiance-cascades-world.md:896-917` ("Below the cut", items 1 to 6 and 8; item 7, probe relocation, is at the pin: `Docs/DeveloperGuide.md:5090`); `Docs/DeveloperGuide.md:4960-4961, 5164, 5271` |
| `new:22` | hands-on | home | Exercise, done in the editor: one wall of the room made thinner in steps of 5 cm until the Voxels view shows it in the error color and its outside lights up; the limit is two voxels, 20 cm at High. Evidence: `Docs/Manual/Lighting.md:334`; `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:153` (the first voxel level's size, 0.10 m at High and 0.20 m at Low) |
| `gamedev:113` | feature | use | Global illumination (experimental) on the Post Process, High and Ultra only (home `make/reflections`, with AO) |
| `render-indirect:153` | feature | use | What the pin has of global illumination, and what is not on main (lamps in the voxels, moving and skinned objects) |
| `render-indirect:162-164` | feature | use | The scene's switch and intensity, the quality row, the voxel sizes of High and Low |
| `render-indirect:175` | feature | use | Bounces arrive a frame each; the frames to settle |
| `render-indirect:180`, `render-indirect:182` | feature | use | The four debug views; captures wait for the light to settle |
| `render-indirect:303` | concept | use | Global illumination: the problem and its families, as far as a maker needs it |
| `render-indirect:405` | figure | use | The overview diagram, drawn for makers |
| `render-indirect:455-457`, `render-indirect:459` | figure | use | GI off and on (the red floor: the look-dev shots `lookdev.sunroom.redfloor.lit` against `lookdev.sunroom.redfloor.lit.gi`, `Tools/LookDev/Shots.json:146-147`), its views, Low against High, its artefacts |
| `render-indirect:506`, `render-indirect:508`, `render-indirect:510` | rule | use | Off costs nothing and leaves the image bit for bit; GI traces the world, never the screen |
| `render-indirect:515`, `render-indirect:517`, `render-indirect:519` | rule | use | Moving objects stay out of the voxels; walls thicker than two voxels; captures wait for the light to settle |
| `render-indirect:623-624`, `render-indirect:644`, `render-indirect:646` | term | link | Global illumination, voxel, open share, settled and pending |
| `render-indirect:698` | open | use | GI batches were still landing at the pin: phase B writes the page from 0.8.0 |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Indirect light, AO and probes in a game | `make/reflections` | must |
| Entities from the Hierarchy's **+** menu; position and scale | `make/scenes-entities` | must |
| Scale in meters | `make/transforms-units` | must |
| The Post Process component and the debug view chip | `make/lighting` | must |
| Emission as a color and a strength | `make/materials` | helps |
| The Graphics Quality presets | `make/quality` | helps |

**Starting state.** The page's starting checkpoint, downloadable: a new project from the Basic 3D template (its Graphics
Quality is High), saved with nothing added; the steps build the room from built-in cubes.

**Command-only steps.** none

## `make/look` — The camera's image

**Covers.** The tutorial gives a copy of the Third-Person Adventure's course a camera look by day and then by night, on
the scene's Post Process and Camera. It opens with the idea at a maker's level: the renderer computes light in real
units, and a camera turns it into a picture in a fixed order (exposure; the lens's bloom and vignette on the light;
white balance and grading; the tone curve; a lookup on the finished picture; grain; the screen), drawn as one diagram;
the first active Post Process sets the look, and a scene without one uses the defaults. Then, one section each, with a
checkpoint at the end of every section: exposure beyond `make/lighting` (Auto Exposure and the Exposure compensation in
stops, Metering Center Weighted against Average, the light and dark adaptation speeds, Min and Max EV with Max EV 16 for
a real sun, the exposure key that lets an interior read darker than the street, each checked in the Luminance view); the
tone curve (Filmic with its Toe and Shoulder, ACES at +0.8 EV, Contrast and Saturation, and the hue of a red lamp under
each); color (White Balance Temperature and Tint, Color Slope, Offset and Power); a color lookup (the book's `.cube`
file imported as a Color Lookup with its Size setting, then Color Lookup and its Intensity on the Post Process, and why
a lookup is made from a capture of the game's own picture); the lens (Bloom Intensity, Radius and Threshold, Vignette,
Lens Flare with the sun in view, Film Grain and Chromatic Aberration used sparingly); height fog (**Add Height Fog** in
the Inspector's Sky section, Density, Base Height, Falloff, Color From Sky and Sun Scattering; fog is no volume and
needs a falloff above 0; fog matched to how far the world is drawn); motion blur (Shutter Angle 180 against 90, Max
Length, only the Game view while the game plays); the Camera component as a lens (Primary, the camera the game draws
through; its field of view; its near and far planes, the far one matched to the fog; Projection, with Orthographic Size,
the view's height in meters, for a 2D, top-down or puzzle game, and the orthographic near and far planes, while the
perspective fields grey out and their tooltip says why; Clear Color, which shows wherever no sky is drawn: a scene
without a sky, or a Sky Light with Show Background off) and depth of field on it (Focus Entity on the robot, Aperture
f/2 against f/8, Sensor Height); a night look from the recipe (Exposure -1.5, 4500 K, Toe 0.6, Bloom 0.06) with each
value's reason. The last section, the W8r one, gives what each effect costs and its quality rows: the players' rows that
turn effects off (Motion blur, Depth of field, Film grain, Chromatic aberration: Scene or Off, the same at every preset)
and Motion blur samples, from generated tables; what a preset is, a link forward to `make/quality`. What Strata does not
do here: particles, trails and decals; post-process volumes (the first active Post Process applies, with no shape and no
blending); volumetric fog, light shafts and fog volumes. The exercise: valley fog, a layer 50 m thick on the valley
floor. At the end the reader can give a scene a look with exposure, tone, color, a lookup, lens effects, fog and lens
blur, and say what each costs.

**Leaves out.**

- Exposure in EV stops, first met → `make/lighting`
- Anti-aliasing, the Graphics Quality presets and the players' Graphics row → `make/quality`
- How metering and adaptation are computed → `image/exposure`
- How the tone curves are built → `image/tone-mapping`
- How white balance and lookups are computed; making a lookup in a grading tool → `image/grading`
- How bloom, the vignette, flares and fringes are made → `image/lens-effects`
- How motion blur and depth of field are drawn → `image/motion-blur`, `image/depth-of-field`
- How height fog is integrated, and the fog it does not have → `light/fog`
- Measuring what the look costs in a game → `make/performance`

**Fit.** `fits`: about 5,100 words against L (5,000). Nine sections of about 23 steps, the diagram of the order, four
short ideas (metering, the curve, a lookup, a lens's blur) and the exercise take the most; the cost table is kept to the
effects of this page. W8r: phase B revises the section on the effects' costs and quality rows (the motion blur samples
row and any rows 0.8.0 adds), whose values come from generated tables in phase A, and checks the page's three not-done
entries again (particles, trails and decals; post-process volumes; volumetric fog, light shafts and fog volumes).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:109` | feature | home | Height fog: **Add Height Fog**, Density, Base Height, Falloff, Color From Sky |
| `gamedev:115` | feature | home | The camera's image on the Post Process: exposure, auto exposure, the tone curve, color, lookups, bloom, vignette, motion blur, depth of field on the Camera, grain, chromatic aberration, flares |
| `gamedev:600` | term | home | Tone mapping (Filmic, ACES) |
| `new:14` | not-done | home | Particles, trails and decals: fire, smoke, sparks, skid marks and bullet holes have no system in the engine; the Roadmap's `vfx` item names them. Evidence: `git grep -ni -e particle -e decal 822a7a46 -- Strata/src Strata/shaders` finds nothing; `git grep -niw -e trail -e trails 822a7a46 -- Strata/src Strata/shaders` finds only the anti-aliasing tooltips of `Strata/src/Strata/Renderer/RendererComponents.cpp:508, 519, 523`; `Docs/Roadmap.md:1690` |
| `new:15` | not-done | home | Post-process volumes: the first active Post Process applies to the whole view, with no shape and no blending between two; a game changes its look by turning one Post Process off and another on. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:1447-1455` (`GetPostProcessSettings` returns the first active `PostProcessComponent`, else the defaults) |
| `new:16` | not-done | home | Volumetric fog, light shafts and fog volumes: Height Fog has no volume, so it shows no light shafts and lamps do not light it. Evidence: `Strata/src/Strata/Renderer/RendererComponents.h:126-129`; `Strata/shaders/Include/Scene.slang:13-14` (SRVs 34 and 36 reserved for volumetric fog and fog volumes); `Docs/Roadmap.md:948` |
| `render-image:38` | feature | use | The post chain's order, as one diagram for makers |
| `render-image:66`, `render-image:80`, `render-image:84`, `render-image:88-89`, `render-image:101` | feature | use | Manual exposure, metering modes, adaptation, Min and Max EV, the exposure key, the Luminance view |
| `render-image:106`, `render-image:111`, `render-image:116` | feature | use | The tone operators, Filmic with Toe and Shoulder, Contrast and Saturation |
| `render-image:123`, `render-image:127`, `render-image:131` | feature | use | White balance, slope, offset and power, the Color Lookup asset |
| `render-image:149`, `render-image:155`, `render-image:158`, `render-image:161`, `render-image:164` | feature | use | Bloom, vignette, chromatic aberration, film grain, lens flares |
| `render-image:175`, `render-image:182` | feature | use | Motion blur; depth of field on the Camera |
| `render-image:238`, `render-image:268` | feature | use | The players' rows; the Post Process component and its sections |
| `scene-ecs:58` | feature | use | The Camera component for makers: Primary, the field of view, the near and far planes, the lens fields of depth of field; Projection, Orthographic Size (the view's height in meters) and the orthographic near and far planes, the perspective fields greyed out with their reason; Clear Color where no sky is drawn (`Strata/src/Strata/Scene/Components.h:124-142`; `Strata/src/Strata/Scene/ComponentRegistration.cpp:36-44`; home `gpu/coordinates`) |
| `render-direct:167`, `render-direct:169`, `render-direct:171` | feature | use | The Height Fog component, its lighting from the sky and the sun, its limits |
| `render-direct:410` | concept | use | Height fog and aerial perspective at a maker's level |
| `render-image:322`, `render-image:339`, `render-image:349`, `render-image:354`, `render-image:358`, `render-image:378`, `render-image:381` | concept | use | Exposure, the tone curve, grading, bloom, the lens, motion blur and depth of field, each at a maker's level |
| `render-image:487-488`, `render-image:491`, `render-image:494`, `render-image:496` | figure | use | Auto exposure and metering, the key, the tone curves side by side, white balance, a lookup at 0, 0.5 and 1 |
| `render-image:499`, `render-image:501`, `render-image:504`, `render-image:513-514` | figure | use | Bloom, vignette, a lens flare, motion blur and depth of field |
| `render-direct:560` | figure | use | Height fog's density, falloff, sun scattering and color from the sky |
| `render-image:587`, `render-image:589`, `render-image:591`, `render-image:593`, `render-image:595`, `render-image:601` | hands-on | use | Find your exposure, interior against exterior, pick a tone curve, a night look, a lookup, motion blur and depth of field |
| `render-direct:646` | hands-on | use | The page's exercise, done in the editor: valley fog, the base at the valley floor and a falloff for a layer 50 m thick |
| `render-image:531`, `render-image:533`, `render-image:565`, `render-image:577`, `render-image:579` | rule | use | Adaptation does not depend on the frame rate; the key only darkens; quality rows never change a scene's look; a lookup shows once it has loaded; motion blur skips the first frame and cuts |
| `render-direct:620-621` | rule | use | Height fog needs a falloff above 0; fog is not a volume |
| `render-image:644`, `render-image:651`, `render-image:657`, `render-image:664`, `render-image:672`, `render-image:681`, `render-image:687`, `render-image:690`, `render-image:715`, `render-image:718-719` | term | link | Exposure, the key, toe and shoulder, white balance, a lookup, bloom, vignette, lens flare, shutter angle, circle of confusion, f-number |
| `render-direct:753` | term | link | Height fog |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Exposure in EV stops and Auto Exposure on the Post Process | `make/lighting` | must |
| The Luminance debug view | `make/lighting` | must |
| The sky sources and the sun | `make/lighting` | helps |
| Opening a copy of a sample | `start/first-game` | must |
| Importing a file into the project | `make/assets` | must |
| The Scene view and the Game view | `make/editor-tour` | must |
| Playing in the editor | `make/play-test-debug` | must |
| An entity field set in the Inspector (the Focus Entity) | `make/first-script` | helps |
| The Graphics Quality presets | `make/quality` | helps |

**Starting state.** A copy of the Third-Person Adventure sample made with File ▸ Open Sample, with
`Scenes/Course.stscene` open; the page's download, from the book's tutorial asset pack, supplies the `.cube` file of the
lookup section (a small warm lookup made for the book). Each section's checkpoint is the copy as that section leaves it.

**Command-only steps.** none

## `make/quality` — Graphics quality and options for players

**Covers.** The goal: choose how the game smooths its edges and how much the renderer spends, and let players choose
too. What must be true first: the settings screen of `make/menus` (its end checkpoint). The steps, in order.
Anti-aliasing on the Post Process: FXAA, Morphological or TAA, and TAA's presets Sharp, Original and Custom; which suits
which look (thin detail and moving cameras: TAA; flat colors and pixel art such as Tetris: FXAA or Morphological,
because TAA softens them), with the comparison on a thin-detail scene. **Project Settings ▸ Graphics Quality**: the
presets Low, Medium, High (the default) and Ultra side by side, a row per setting with its memory and GPU time, and
Custom; a preset changes what the renderer spends, never what a scene stores (its lights, its Post Process, its sky).
The presets table is the W8r section: its values come from generated tables. The Scene view's quality chip for one view,
and that the Game view draws as the game will. `--quality low` for one run of the exported game. Then the players' side:
a Graphics row added to the settings screen, a toggle group of the four presets that acts only on the toggle switched on
and calls `Graphics::SetPreset` and `Graphics::Save` (the Third-Person sample's code, quoted), an anti-aliasing choice
with `Graphics::Set("AntiAliasing", ...)`, and `Graphics::GetPreset` to show the choice in effect; where the choice is
kept (`GraphicsOptions.json` beside the game's saves, in the editor the project's `.strata/Saves`), that a player's
saved preset hides the project's while you play in the editor, and **Reset Player Options** on the Graphics Quality
page. Why there is no render scale, the design decision named again in two sentences with a link to
`image/quality-settings`. What Strata does not do here: no command sets a player's options; no MSAA and no supersampling
(a render scale above 1); no HDR display output (the swap chain is sRGB only). Result: a settings screen whose Graphics
row works in the exported game. Variations: a Custom preset one row at a time; `Graphics::Options()` for a full options
screen. The exercise: the anti-aliasing shoot-out on the Physics Playground's floor.

**Leaves out.**

- How FXAA and morphological AA work → `image/spatial-aa`
- How TAA works, and its tunables → `image/taa`
- How presets, traits and the players' file are built → `image/quality-settings`
- The quality rows of each post effect → `make/look`
- Building the settings screen, toggles and toggle groups → `make/menus`
- Measuring what the presets cost in a game → `make/performance`

**Fit.** `fits`: about 3,700 words against M (3,000): eleven steps, one excerpt, two figures, the idea of the
anti-aliasing kinds and of presets as cost knobs, and the exercise take the most; the TAA tunables stay on `image/taa`.
W8r: phase B revises the presets table, with the rows 0.8.0 changes (shadows of lamps, global illumination, reflections)
and their costs, and checks the page's three not-done entries again (MSAA and supersampling; HDR display output; setting
a player's graphics options by command).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:116` | feature | home | Anti-aliasing: FXAA, TAA (Sharp, Original, Custom), Morphological |
| `gamedev:117` | feature | home | Graphics Quality: the project page with Low, Medium, High, Ultra and Custom, the cost per row, players' choices, the Scene view's quality chip, `--quality` |
| `gamedev:205` | feature | home | Graphics options for players: `Graphics::SetPreset`, `Set`, `Get`, `Reset`, `Save`, `Options`, `FindOption`; `GraphicsOptions.json`; resetting them |
| `gamedev:314` | concept | home | The camera's image and quality: anti-aliasing kinds, presets as cost knobs, no render scale; the mistakes (a render-scale slider looked for, TAA on pixel art) |
| `gamedev:380` | code | home | `Samples/ThirdPerson/Scripts/SettingsMenu.cpp:26-39`: the Graphics row as one toggle group, the events of switched-off toggles ignored, `Graphics::SetPreset` and `Graphics::Save` |
| `gamedev:465` | figure | home | TAA against FXAA on a thin-detail scene; TAA softening a Tetris-like flat image |
| `gamedev:466` | figure | home | Graphics Quality Low against High on the Showcase's second shot |
| `gamedev:518` | rule | home | No render scale, ever: presets lower costs, not resolution |
| `gamedev:601` | term | home | Anti-aliasing (FXAA, TAA, Morphological) |
| `gamedev:602` | term | home | Graphics Quality preset |
| `render-image:603` | hands-on | home | A Graphics options menu: preset toggles and an anti-aliasing chooser, `GraphicsOptions.json` checked, the runtime restarted, reset |
| `new:1` | not-done | home | Setting a player's graphics options by command: the only graphics command deletes them. Evidence: `StrataEditor/src/Editor/EditorGraphicsCommands.cpp:16`, `graphics.resetPlayerOptions`, the file's only command; `git grep -n "\"graphics\." 822a7a46 -- StrataEditor/src` finds only it, registered there and run by the page's **Reset Player Options** (`StrataEditor/src/UI/GraphicsQualityPage.cpp:350`) |
| `new:17` | not-done | home | MSAA and supersampling (a render scale above 1): no multisampled targets and no render scale above 1; edges are smoothed by FXAA, Morphological or TAA. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2767` refuses targets whose sample count is not 1; `Docs/Roadmap.md:944, 1670, 1672`; `Docs/Releases/0.7.0.md:409, 411` |
| `new:18` | not-done | home | HDR display output (HDR10, scRGB): the swap chain is sRGB only, so the game's picture is an SDR picture on every display. Evidence: `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:1131-1136` (an 8-bit UNORM back buffer in the sRGB nonlinear color space) |
| `render-image:194`, `render-image:196`, `render-image:198`, `render-image:203`, `render-image:214` | feature | use | The Post Process's anti-aliasing and its methods; TAA's presets |
| `render-image:227`, `render-image:232`, `render-image:243` | feature | use | The quality settings, the presets table, who follows which quality (project, Scene view chip, Game view, `--quality`) |
| `render-image:246`, `render-image:250`, `render-image:254`, `render-image:258`, `render-image:260` | feature | use | The players' options file, the SDK's `Graphics`, the Graphics Quality page and its reset, the runtime's `--quality`, no render scale |
| `scripting:130` | feature | use | `Graphics`, `GraphicsOption`, `QualityPreset` in the SDK (home `image/quality-settings`) |
| `worlds-runtime:92`, `worlds-runtime:135` | feature | use | Graphics options from scripts; the service that owns the file |
| `editor-ui:229` | feature | use | The Graphics Quality page: preset chips, the table, the Custom column, the players' banner and reset |
| `render-image:362`, `render-image:364`, `render-image:371`, `render-image:384` | concept | use | Aliasing, spatial AA, TAA and presets as a product concept, at a maker's level |
| `render-image:506`, `render-image:509`, `render-image:515`, `render-image:517`, `render-image:519` | figure | use | AA crops, TAA's presets in a pan, the presets of one shot, the Graphics Quality page, the Third-Person settings menu |
| `worlds-runtime:380` | figure | use | The layers of the choice: the project, the player's file, `--quality` |
| `render-image:597` | hands-on | use | The page's exercise, done in the editor: the anti-aliasing shoot-out on the Physics Playground's floor |
| `render-image:565`, `render-image:572`, `render-image:574` | rule | use | Quality rows never change a scene's look; only the graphics service touches the players' file; never below native resolution |
| `gamedev:520` | rule | use | In a toggle group act only on value 1 (home `make/menus`) |
| `render-image:693-694`, `render-image:698`, `render-image:728-729` | term | link | FXAA, morphological AA, TAA, quality preset and row, Custom |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The settings screen, toggles and toggle groups, `OnUIValueChanged` | `make/menus` | must |
| The Post Process component | `make/lighting` | must |
| The post effects and their players' rows | `make/look` | must |
| Exporting the game and running it from a terminal with an option | `make/export` | must |
| `std::optional` in a script | `basics/programming-3` | helps |
| Where a game keeps its save files | `make/levels-saves` | helps |

**Starting state.** The end checkpoint of `make/menus`, downloadable: its project with the settings screen (volume,
window mode, vsync) built and working in play.

**Command-only steps.** none

## `make/large-worlds` — Large worlds

**Covers.** The tutorial turns a small level into a streamed world, on the page's own example: a project whose player is
Coin Run's rolling ball and whose props are a few nature prefabs (the starting checkpoint). The idea comes first, in a
maker's words: a large level cannot stay loaded whole (memory, and the wait to load it), so a world keeps a persistent
scene that never unloads (the player, cameras, lights, the sky, managers, screen UI) and splits the rest into layers of
square cells, each layer with its own cell size and streaming distance; streaming sources decide which cells load (the
diagram of cells around a source, and a prefetch before a teleport). Then the sections, each ending in a checkpoint.
Make the world: **New ▸ World** in the Content Browser writes a World asset and its persistent scene and opens it; the
Asset panel lists its four layers (Terrain, Buildings, Props and Gameplay, 64 m cells streaming four cells away; Terrain
loads before a game starts). Fill its cells: the Hierarchy's world strip and its edit layer (Persistent for the player,
the camera and the managers; Terrain for the ground's plane tiles; Props for the level's content), the prefabs dragged
in, the Inspector naming an entity's cell ("Cell: Props (3, -1)"), an entity moved across a border changing cell in the
same undo step, and the Hierarchy's search `l:Props`; a gotcha: choose the edit layer before creating, because a new
entity goes into that layer's cell and a moved one stays in its own layer, and children belong to their top-level
parent's cell. See the cells: the viewport's **Cells** chip (loading, loaded, unloading), the cell map in **View ▸
Streaming** (unsaved cells, pins, sources; **Load and pin**); flying away and back; Save writes only what changed, and a
prefab changed later reaches a cell's instances only when the cell loads in the editor, so cells that use it are loaded
and saved before an export (the page says that this was read in the code, not run). The player as the streaming source:
the ball in the persistent scene with a Streaming Source component (Radius, Layers, Priority); Play, and the cell map
follows it; roaming things belong in the persistent scene, because a body unloads with the cell it loaded with; keep the
player saved there with its source, because the exported game loads the start cells around the saved sources before any
script runs, so a player that a script spawns or moves (to a position from a save file) needs a prefetch first, while
Play in the editor starts from the cells the editor has loaded. **Cook** in the Asset panel, and what its numbers and
warnings say, with a gotcha: the physics room it reserves counts only the enabled streaming sources saved in the
persistent scene (at least one, the largest radius per layer), so sources a game spawns later are not counted. A
teleport: a script asks for the cells around a far marker with `World::RequestCellsAround`, waits for
`World::IsLoadedAround` and for a raycast to find the ground, then teleports the ball and releases the request (the Open
World's `Explorer` code, quoted); without the prefetch the ball falls through ground that is not there yet. Why the
raycast, in one sentence: `IsLoadedAround` says the cells are loaded, and a mesh collider in them may still wait for its
shape, so a hit is the test of collision (read in the code, not run). A layer switched off from a script with
`World::SetLayerEnabled`; a forgotten `WorldCellRequest` keeps its cells loaded until `Release` or the scene stops, and
requests and layer toggles belong to the running scene. The exported world: the export with the loading scene of
`make/levels-saves`, run, waiting for the Terrain layer's cells and their collision before the ball drops ("a world that
waits for its ground"). The limits and what Strata does not do: worlds within 20 km of the origin (positions are kept to
about 2 mm there) and no origin rebasing; distant cells are not drawn, with no simplified far versions (match fog and
the camera's far plane to the streaming distances); no terrain system (the samples' terrains are meshes made by tools);
a moving body cannot pass from one cell to another. A last look at the Open World sample's island. The exercise moves a
plain scene 50 km from the origin: it still draws without shaking, which is why the limit is about the precision of
positions, not the renderer. At the end the reader can build, play, cook and export a streamed world and move a player
across it safely.

**Leaves out.**

- Why levels stream, and floating-point precision far from the origin → `worlds/why-streaming`
- The World document, its grid and the streamer's rules → `worlds/grids`, `worlds/streamer`
- What a world reserves in physics, and prefetching as the engine does it → `worlds/physics-scripts`
- How the editor keeps cells, saves and play copies → `editor/worlds`
- Changing a world's layers (cell size, distance, Load Before Start), a step with no menu or button → `make/commands`
- Loading scenes and scene switches → `make/levels-saves`
- Exporting in general → `make/export`
- Measuring a world's streaming in the exported game → `make/performance`

**Fit.** `fits`: about 4,600 words against L (5,000): the idea with its diagram, seven step sections of about 18 steps
with their gotchas, one excerpt of 39 lines, the limits with the four not-done entries in one paragraph, and the
exercise take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:210` | feature | home | Worlds for makers: New ▸ World, layers (cell size, streaming distance, Load Before Start), the edit layer strip, entities re-celled by moving, the Cells chip, the cell map (load and pin), Save of changed cells, Cook, Play from loaded cells, `StreamingSource`, the scripts' `World` calls, the limits |
| `gamedev:344` | concept | home | Large worlds: why stream, cells, layers, sources, prefetch before a teleport, precision; the mistake of a player in a cell |
| `gamedev:385` | code | home | `Samples/OpenWorld/Scripts/Explorer.cpp:209-247`: the prefetch before a teleport, the wait for the cells and a raycast to the ground, the teleport and the request released |
| `gamedev:428` | figure | home | World streaming: the persistent scene and layers of cells around a source with their radii; the teleport's prefetch |
| `gamedev:457` | figure | home | World editing in the Open World copy: the Hierarchy's strip with the edit layer, the Cells chip, the cell map in the Streaming panel; a capture that shows a fox names the fox's authors and license in its caption (`appendix/credits` holds the full entry) |
| `gamedev:514` | rule | home | Keep worlds within 20 km; roaming things in the persistent scene |
| `gamedev:515` | rule | home | Prefetch cells before a teleport |
| `gamedev:546` | hands-on | home | G13: a small world, props in a layer, a streaming source on the player, a teleport with prefetch (New ▸ World in place of `world.create`) |
| `gamedev:649` | term | home | World, persistent scene, layer, cell, streaming source, edit layer, cook |
| `gamedev:650` | term | home | Prefetch |
| `render-core:670` | hands-on | home | Exercise: a plain scene 50 km from the origin draws as well as at the origin; what still loses precision there |
| `new:2` | not-done | home | Terrain: a terrain system, sculpting and painting; the samples' terrains are meshes made by `Tools/GenerateIslandTerrain.py` and `Tools/GenerateShowcaseTerrain.py`. Evidence: `git grep -ni terrain 822a7a46 -- Strata/src` finds only comments (`Strata/src/Strata/Renderer/Mesh.cpp:447`, `RenderScene.h:94`, `SceneRenderData.h:695`, `SpatialIndex.h:20`, `Strata/src/Strata/World/WorldAsset.h:19`); `Docs/Roadmap.md:1694-1695` |
| `new:3` | not-done | home | Bodies that move from one world cell to another: a moving body unloads with the cell it loaded with. Evidence: `Docs/Releases/0.7.0.md:387-388`; `Docs/Manual/Worlds.md:97-98` |
| `new:8` | open | home | Check: `PrefabSync` with cells. Prefab changes reach a cell's instances when the cell loads in the editor; cells not loaded since the change keep their old instances in their files, and an export packs those files as they are. `PrefabSync` catches a prefab's instances up once per prefab and scene, the first time it looks, so a cell that loads after another cell used the prefab may not catch up; no test covers cells. Until the engine's agents run the check, the page tells the reader to load and save the cells that use a changed prefab, and says that this was read, not run. Evidence: `Docs/Manual/Worlds.md:100`; `StrataEditor/src/Editor/PrefabSync.cpp:174-181`, `:205-241`; `git grep -n -i prefab 822a7a46 -- StrataTests/src/Editor/EditorWorldTests.cpp` finds nothing |
| `new:9` | open | home | Check: The pending window of mesh colliders. `World::IsLoadedAround` reports loaded cells, whose entities exist, and the SDK's comment says that the ground there has collision then; a mesh collider's body stays pending until its mesh data is in and its shape is cooked on a job, so a cell whose ground is a mesh collider may count as loaded before it collides. The teleport waits for a raycast hit, which is the test of collision, and the page says that this was read, not run (the island's ground is in the persistent scene, so the sample's raycast finds the ground's height). Evidence: `StrataScriptCore/Include/StrataScript/World.h:38-41`; `Strata/src/Strata/Physics/PhysicsWorld.h:41-43`, `:129-132`; `Samples/OpenWorld/Scripts/Explorer.cpp:229-233` |
| `new:4` | not-done | home | Worlds beyond 20 km from the origin, HLOD (distant cells are not drawn) and origin rebasing. Evidence: `Docs/Releases/0.7.0.md:386, 414`; `Docs/Roadmap.md:1693, 1706` |
| `worlds-runtime:24-25`, `worlds-runtime:29` | feature | use | Layers, cells and the limits (`c_SupportedExtent` 20 km) |
| `worlds-runtime:41-42` | feature | use | The World and Streaming Source components |
| `worlds-runtime:47-48` | feature | use | The exported game's prepared start, which waits for the start cells around the sources saved in the persistent scene before any script runs; Play in the editor starts from the cells the editor has loaded (`Strata/src/Strata/World/WorldStreamingSystem.cpp:276-310`; `StrataEditor/src/Editor/EditorContext.cpp:1382-1385`; `Docs/Manual/Worlds.md:68-71`) |
| `worlds-runtime:89` | feature | use | The SDK's `World` and `WorldCellRequest`: a request holds its cells until `Release` or the scene stops, and requests and layer toggles belong to the running scene (`StrataScriptCore/Include/StrataScript/World.h:14-36`; `Strata/src/Strata/World/WorldStreamingSystem.cpp:187-191`; home `worlds/physics-scripts`) |
| `worlds-runtime:104` | feature | use | Re-celling as a maker meets it: a new top-level entity goes into the edit layer's cell, a moved entity changes cell within its own layer, children belong to their top-level parent's cell (`StrataEditor/src/Editor/EditorWorld.cpp:315-345`; home `editor/worlds`) |
| `worlds-runtime:105-106`, `worlds-runtime:110`, `worlds-runtime:112-117` | feature | use | Moving entities between cells, the world's save, the cook (which counts only the enabled streaming sources saved in the persistent scene, at least one: `StrataEditor/src/Editor/WorldCook.cpp:76-81`, `:313-325`), the defaults of a new world, the cell map, the Hierarchy's strip and search, the Inspector's cell line, the Cells chip, the Asset panel and New ▸ World (home `editor/worlds`) |
| `worlds-runtime:185` | feature | use | The Open World sample as the last look |
| `worlds-runtime:227`, `worlds-runtime:251`, `worlds-runtime:268`, `worlds-runtime:272` | concept | use | Why a level must be bounded, streaming sources, floating-point range, no HLOD |
| `worlds-runtime:388`, `worlds-runtime:390`, `worlds-runtime:392`, `worlds-runtime:394`, `worlds-runtime:396`, `worlds-runtime:399` | figure | use | The Open World in the editor with the strip, the Cells chip, the cell map (editing and playing), the Inspector's cell line, New ▸ World; a capture that shows a fox names the fox's authors and license in its caption |
| `worlds-runtime:403` | figure | use | The exported Open World: its loading scene, then the island; a capture that shows a fox names the fox's authors and license in its caption |
| `worlds-runtime:422`, `worlds-runtime:438` | rule | use | Worlds stay within 20 km; roaming objects belong in the persistent scene |
| `worlds-runtime:467`, `worlds-runtime:469`, `worlds-runtime:473`, `worlds-runtime:475`, `worlds-runtime:477` | hands-on | use | A first world, a source on the player, prefetch before a teleport, a layer toggled from gameplay, cook and read the numbers |
| `worlds-runtime:513-517`, `worlds-runtime:522`, `worlds-runtime:532`, `worlds-runtime:542`, `worlds-runtime:544` | term | link | World, World asset, persistent scene, layer, cell, streaming source, `LoadBeforeStart`, edit layer, cell map |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Prefabs, and placing them by dragging into the Scene view | `make/prefabs` | must |
| Position and scale in meters | `make/transforms-units` | must |
| The start scene and the loading scene | `make/levels-saves` | must |
| Exporting the game and running it | `make/export` | must |
| Finding an entity by name and reading its transform in a script | `make/scripting-scene` | must |
| A raycast and teleporting a body | `make/physics` | must |
| `std::optional` (the raycast's hit) | `basics/programming-3` | must |
| Input actions read by a script | `make/input` | must |
| Undo | `make/project-files` | helps |
| A UI image used as a fade | `make/hud` | helps |
| Height fog and the camera's far plane | `make/look` | helps |

**Starting state.** The book's start checkpoint of the tutorial file, downloadable: a new project from the Basic 3D
template holding a player prefab (Coin Run's ball with its `Move` action, its rolling script and a camera that follows
it), three nature prop prefabs from Kenney's Nature Kit (CC0, credited in the checkpoint's `CREDITS.md`), a loading
scene as `make/levels-saves` built it, and a `Teleport` script with its key unbound. No world yet.

**Command-only steps.** none

## `make/performance` — Making your game run fast

**Covers.** The tutorial builds a scene too big to run well, measures it and makes it fast, on the page's own example: a
field of 5,000 props spawned by a script, then the Open World copy for streaming. The ideas come first, at a maker's
level: a frame's time in milliseconds against frames per second; a frame is bound by the CPU, by the GPU or by the
display's cap; an average hides spikes, so the panel shows p95 and the maximum; measure, change one thing, measure
again, on a named computer (the design decision that trade-offs are measured and the numbers shown, named again with a
link to `engineering/perf-lab`). The sections: spawn the field with one `Scene::InstantiateMany` call, each transform
built by one given line (`glm::translate(glm::mat4(1.0f), position)`); the viewport's **Stats** chip (draw calls opaque
and shadow, instances, triangles, visible and occluded proxies, assets loading), with the camera moved behind the hut to
see occluded proxies rise, and what raises the draw-call line, with a link to `draw/batching`: draws follow the mesh,
its submesh and level of detail and the pipeline state (double-sided, alpha-masked, mirrored, skinned), never the
material or the number of copies, so the common advice to merge materials to cut draw calls does not apply here; **View
▸ Performance** while playing (frame time, p95, maximum, FPS, the CPU and GPU stages, what bounds the frame, **Pause**
with Space to read a spike, **Copy as JSON**), and the editor's idle throttling in two sentences with a link to
`editor-ui/status`: while nothing happens the editor redraws at 30 frames per second, 10 without the focus, so the frame
pill shows that and not the game's speed; while the game plays it redraws up to the active frame rate of the
Preferences' Frame Rate page, unlimited by default (vsync sets the pace); levels of detail (200 copies of an imported
model receding, the LOD debug view, the project's preset Low against Ultra and its "Level of detail error" row); the
cost of shadows per object (Cast Shadows off on the field's small props and the shadow draw calls falling); streaming
(the Open World copy in the Streaming debug view, requests following the view as the camera flies); the exported game
(`--perf-log run.csv --frames 600 --resolution 1280x720`, the file opened in a spreadsheet program, frame time and GPU
stages per row, `--quality low` against `ultra`). Variations: vsync on and off in the exported game from the settings
screen, and what a capped frame shows in the panel; a world's streaming columns in the perf log; many animated
characters and their culling mode, read in the panel's animation stage; many scripts against one manager script, with
the engine's measured cost of a trivial `OnUpdate` and the rule to override only the callbacks you use. The exercise:
ten materials on the field's props, and the opaque draw calls that do not change. The W8r section, the Stats overlay's
lines and the Performance panel's numbers, is revised in phase B. At the end the reader can tell what bounds a game's
frame and lower its cost with numbers to show for it.

**Leaves out.**

- How the profiler measures stages, self time and percentiles → `core/profiling`
- How culling, batching, levels of detail and streaming work → `draw/bounds-culling`, `draw/batching`, `draw/lod`, `draw/asset-requests`
- GPU timestamps and readbacks → `gpu/readback-timing`
- Every perf budget and the machine it was measured on → `reference/performance`
- The runtime's options in general → `worlds/runtime`
- The presets and their rows → `make/quality`
- Spawning many instances by a command → `make/commands`

**Fit.** `over`: about 4,050 words against M (3,000): the three ideas, seven sections of about 16 steps with their
numbers, four variations and the exercise reach M's top; the next size is L (5,000) by S2, which also holds phase B's
revised numbers. W8r: phase B revises the section on the Stats overlay's lines and the Performance panel's numbers (and
the `renderStats` keys behind them), and the costs the presets show.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:56` | feature | home | The Streaming and Performance panels: budgets, loads, uploads, the cell map, physics; frame timings per stage with a pause |
| `foundation:541` | hands-on | home | Reading the Performance panel during play: CPU-bound, GPU-bound or capped |
| `render-core:661` | hands-on | home | Variation: vsync on and off in the exported game and its cost (the editor keeps its own vsync in play) |
| `render-core:672` | hands-on | home | The GPU stages of the game from `--perf-log` or the Performance panel, and which feature they come from |
| `render-scene:550` | hands-on | home | Is the scene drawing efficiently: draws, instances, triangles, visible and occluded, read on the Stats overlay instead of `renderStats` |
| `render-scene:553` | hands-on | home | The LOD view on 200 copies of a model, Graphics Quality Low against Ultra |
| `render-scene:555` | hands-on | home | Cast Shadows off on a dense prop field and the shadow draw calls |
| `render-scene:557` | hands-on | home | The Open World copy in the streaming view: requests follow the view |
| `render-scene:80`, `render-scene:82` | feature | use | What the draw-call line counts and what raises it: the pipeline state (double-sided, alpha-masked, mirrored, skinned), the mesh, its submesh and level of detail; not the material or the number of copies (`Strata/src/Strata/Renderer/SceneDrawKey.h:9-13`; 10,000 materials in one opaque draw call, `StrataTests/Perf/Budgets.json:155`; home `draw/batching`) |
| `render-scene:182-184` | feature | use | The debug views lod and streaming, the quality rows of detail, the Stats overlay |
| `render-scene:181` | feature | link | `renderStats`, the same numbers for commands (`make/commands`) |
| `editor-ui:150-151` | feature | use | The Streaming and Performance panels |
| `editor-ui:118` | feature | use | Idle throttling as a maker meets it: an idle editor redraws at 30 frames per second, 10 without the focus; while the game plays, up to the active frame rate of Preferences, Frame Rate, unlimited by default (home `editor-ui/status`; `StrataEditor/src/Editor/EditorFrameRate.h:26-28`, `:39`; `StrataEditor/src/EditorLayer.h:118-124`) |
| `foundation:303` | concept | use | Profiling: the method, frame time, percentiles, CPU-bound, GPU-bound or capped (home `core/profiling`) |
| `foundation:431`, `foundation:433` | figure | use | The Performance panel's stacked stages; the frame pill and what bounds the frame |
| `foundation:608-609` | term | link | Percentile; CPU-bound, GPU-bound, capped |
| `scripting:121` | feature | use | `Scene::InstantiateMany` (home `make/scripting-scene`) |
| `gamedev:239` | feature | use | The runtime's options `--perf-log`, `--frames`, `--resolution`, `--quality` (home `make/export`) |
| `worlds-runtime:130`, `worlds-runtime:132`, `worlds-runtime:136` | feature | use | The perf log's columns: the runtime's, the renderer's, the column groups |
| `worlds-runtime:295` | concept | use | Measuring a shipped game: per-frame logs, deterministic runs; the mistake of comparing runs whose game time followed the frame rate |
| `worlds-runtime:408` | figure | use | A perf log plotted in a spreadsheet |
| `worlds-runtime:481` | hands-on | use | Measure a run with `--frames 600 --perf-log run.csv --resolution 1280x720`, Low against Ultra |
| `animation:520` | hands-on | home | Variation: 500 animated characters spawned at once, their Culling Mode Always Animate against When Visible, read in the `Scene.Animation` stage of the Performance panel |
| `new:28` | hands-on | home | Variation: many scripts against one manager script. 100,000 scripts with a trivial `OnUpdate` take about 1.9 ms a frame on the reference machine, about 20 ns a call; a class that does not override a callback costs nothing for it, so an empty `OnUpdate` is not free: override only the callbacks you use. Evidence: `StrataTests/Perf/Budgets.json:40`, `:42` (`Perf.Scripting.TrivialUpdate100k` and `300k`, measured 1.856 and 5.745 ms); `Strata/src/Strata/Scripting/ScriptSystem.cpp:27-28`; `Strata/src/Strata/Scripting/ScriptSystem.h:54-55` |
| `new:23` | hands-on | home | Exercise, done in the editor: the field's props given ten different materials, and the Stats chip read before and after: the opaque draw calls stay as they were, because draws follow the mesh, its level of detail and the pipeline state, not the material. Evidence: `Strata/src/Strata/Renderer/SceneDrawKey.h:9-13`; `StrataTests/Perf/Budgets.json:155` (10,000 materials drawn in one opaque draw call); `StrataTests/src/Renderer/GPURenderSceneTests.cpp:120` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Frame time in milliseconds and frames per second | `start/what-an-engine-is` | must |
| Spawning a prefab from a script | `make/scripting-scene` | must |
| Importing a model | `make/assets` | must |
| The Graphics Quality presets and the project's page | `make/quality` | must |
| Running the exported game from a terminal with options | `make/export` | must |
| Mesh renderers and their Cast Shadows | `make/scenes-entities` | must |
| A world's cells and streaming | `make/large-worlds` | helps |
| Vsync on the settings screen | `make/menus` | helps |
| An Animator and its Culling Mode | `make/animation` | helps |

**Starting state.** The page's starting checkpoint, downloadable: a new project from the Basic 3D template with the
book's tutorial asset pack's prop prefab (a CC0 rock with its credit) and a small hut of built-in cubes to hide behind;
a copy of the Open World sample for the streaming section; the exported game of the same project for the last section.

**Command-only steps.** none

## `make/automated-playtests` — Automated play-tests

**Covers.** The goal: a play-test the editor runs by itself, which fails when a change breaks the game. What must be
true first: a terminal (`start/install`), a copy of the Tetris sample, and the menus of `make/menus` for the UI section.
The order. Why a script: a person cannot repeat a play-test exactly, a script can (the testing loop: build, play,
simulated input, observe, check, run again). JSON as the reader writes it, from zero: objects, arrays, strings, numbers,
`true` and `false`, quotes and commas, and the editor's message for a broken file. A command script: a list of steps,
each a `command` with its `parameters`; the first one starts play, reads the score's text and stops; it runs with
`StrataEditor --project <dir> --commands test.json --quit-after-commands` (on Windows piped to `Write-Output`, so that
PowerShell waits), and its exit code says passed (0) or failed (1). `expect` on a result: `equals`, `min` and `max` at a
JSON pointer such as `/values/Text`. Exact play: `play.start {paused: true}`, `play.step {steps}`, simulated keys and
actions held for a number of fixed steps, `input.sequence` with events at given steps, and why the same steps give the
same game on any computer (seeds, fixed steps, paused waits; a call takes about a tenth of a second and the steps per
frame differ between machines). `until` for an outcome that takes game time; `bind` and `$ref` for an ID a step returns.
The Tetris regression as the model (the excerpt): fields set so that time cannot move the pieces, an `input.sequence` of
26 steps, an exact score of 209; the excerpt ends there (line 24), because the sample's script then waits 300 frames for
game over, which the book's scripts never do (the erratum below): they wait with `until`. What a test can read:
`editor.status` errors, `log.read`, `component.get`, `script.get` (fields, live), `physics.stats`, `audio.state`,
`input.state`, and `viewport.capture` of a picture at a fixed step for a person to look at. Game UI tested without eyes:
`ui.create` builds a menu in one undo step, `ui.layout` gives every rect at 1280 x 720 and 2560 x 1440 without drawing,
`ui.hitTest` names what lies under a point, `input.click` presses a button in play. Record and replay: every command,
also those the person's clicks in menus and panels run, lands in the activity journal; the Activity panel's **Copy as
script** turns one entry into a step; what a replay script is: a session's commands as a script whose later steps refer
to earlier results through `bind` and `$ref`; turning a session into a regression test is `make/with-an-agent`'s (G15),
linked. What Strata does not do here: an exported game runs no command script. Result: a test file that fails when the
score rule changes. Variations: a smoke test of the reader's own game (build, play, a few steps, no errors in
`editor.status`) modeled on the engine's smoke script; a physics play-test that pauses and waits with `until` (the
Physics Playground's pattern); a test of a game's audio (`audio.state`). The exercise: the Tetris test made to fail by
one changed field, and its failing `expect` read.

**Leaves out.**

- Running commands from outside a running editor with StrataCLI → `make/commands`
- Exporting a whole session as a replay script and running it on a copy → `make/with-an-agent`
- How command scripts, batches and the replay export are built → `editor/command-scripts`, `editor/journal`
- How simulated input merges with the real devices → `input/simulated`
- Stepping a paused game as the editor does it → `editor/stepping`
- How UI layout and hit tests work → `ui/layout`, `ui/input`
- Tests of the engine itself → `engineering/testing`

**Fit.** `fits`: about 4,500 words against L (5,000): JSON from zero, the command script's parts, exact play with its
reasons, the Tetris excerpt, the UI tests and record and replay, each with its steps, take the most; the three
variations and the exercise take about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:224` | feature | home | Simulated input: `input.key`, `mouseButton`, `mouseMove`, `scroll`, `click`, `type`, `gamepadButton`, `gamepadAxis`, `action`, `releaseAll`, `state`; durations in fixed steps |
| `gamedev:225` | feature | home | Deterministic sequences: `input.sequence {steps, events, observe}`, `play.step` answering after its steps, `play.start {paused}` |
| `gamedev:226` | feature | home | Viewport capture with its camera, size, debug view, quality and fixed step; it waits for assets |
| `gamedev:227` | feature | home | Command scripts and expectations: `--commands` and `--quit-after-commands`, `expect`, `until`, `bind` and `$ref`, exit code 1 on failure |
| `gamedev:228` | feature | home | What a replay script is: the journal turned into a command script with bindings; the export and the regression test made from it are `make/with-an-agent`'s (G15) |
| `gamedev:230` | feature | home | What a test reads: `editor.status` errors, `log.read`, `script.status`, `component.get`, `entity.get`, `physics.stats`, `animation.info` |
| `gamedev:346` | concept | home | Testing a game: determinism, observability, automated play-tests, regression scripts; the mistake of timing-dependent checks |
| `gamedev:375` | code | home | `StrataTests/Editor/TetrisCommands.json.in:1-24`: `expect`, `script.setField` that takes timing out, `ui.layout` at two resolutions, an `input.sequence` of 26 steps and the exact score 209 |
| `gamedev:431` | figure | home | The testing loop: script, build, play, simulated input, observe, regression script |
| `gamedev:516` | rule | home | Deterministic play-tests: seeds, input durations in fixed steps, `input.sequence`, paused `until` waits |
| `gamedev:655` | term | home | Command, command script, expect, until, bind |
| `gamedev:656` | term | home | Simulated input, input sequence |
| `gamedev:657` | term | home | Viewport capture |
| `gamedev:658` | term | home | Activity journal, replay |
| `gameui:214` | feature | home | `ui.create` (presets in one transaction, a canvas when needed, anchor presets), `ui.layout` (rects at any screen without rendering), `ui.hitTest` |
| `gameui:384` | concept | home | Testing UI headlessly: simulated input, layout without rendering, hit tests; agents build UI through commands |
| `gameui:586` | hands-on | home | A menu built with `ui.create` and checked with `ui.hitTest` and `input.click` in play |
| `physics:456` | hands-on | home | Variation: a script that pauses, steps to a fixed step and checks an outcome with `until`, as the Playground's regression |
| `build-test:598` | hands-on | home | Variation: a smoke test of the reader's game modeled on `SmokeCommands.json.in`, run with `--commands` and `--quit-after-commands`; why PowerShell needs the pipe (the page writes `\| Write-Output`, as `start/install` taught) |
| `audio-input:573` | hands-on | home | Playing a game by commands (`input.key {steps}`, `input.action`), reading `audio.state` and `input.state`, an `input.sequence` that gives the same result at different frame rates |
| `new:5` | not-done | home | Automating an exported game: command scripts, simulated input and expectations run in the editor only. Evidence: `Docs/Roadmap.md:1697`; `Docs/Releases/0.7.0.md:414` |
| `new:20` | erratum | home | `StrataTests/Editor/TetrisCommands.json.in:28`, the Tetris sample's command script, waits 300 frames (`editor.wait {frames}`) before it reads game over: the page's excerpt ends at line 24, its own scripts wait with `until` in fixed steps, and it never shows the sample's wait as a model. Evidence: `StrataTests/Editor/TetrisCommands.json.in:28`; `AGENTS.md:117-118` (tests wait by the clock or a condition, never frames) |
| `new:24` | hands-on | home | Exercise, done with a command script: the Tetris test's `LinesPerLevel` step set to 2 and the test run again; it fails with exit code 1, and the reader finds in its output which `expect` failed and why. Evidence: `StrataTests/Editor/TetrisCommands.json.in:5` (`LinesPerLevel` 1), `:22-24` (the lines, score and level expected) |
| `editor-core:222-226` | feature | use | Pause and step, `play.start {paused}`, `play.step {steps, wait}`, the editor's simulated input |
| `editor-core:240` | feature | use | The command script format with `expect`, `bind`, `$ref` and `until` (home `editor/command-scripts`) |
| `editor-core:359` | concept | use | Scripts of commands, record and replay (the replay as a regression test is `make/with-an-agent`'s) |
| `editor-core:450` | code | use | The engine's smoke script, the model of the smoke-test variation (home `editor/command-scripts`) |
| `editor-core:535` | figure | use | A command script's run in the terminal with its exit code |
| `editor-core:580` | rule | use | Tools count game time in fixed steps, never frames |
| `editor-core:615` | hands-on | use | A first command script, run headless |
| `editor-core:662-665` | term | link | Command script, `expect`, `bind` and `$ref`, `until` |
| `audio-input:136`, `audio-input:164` | feature | use | The virtual devices; simulated actions |
| `audio-input:357` | concept | use | Simulated input, determinism and fixed steps |
| `audio-input:464` | figure | use | Simulated holds counted in fixed steps |
| `audio-input:521` | rule | link | Durations of simulated input count fixed steps, and while a running game updates at time scale 0 its frames too (the input step count, `StrataEditor/src/Editor/EditorContext.h:349-352`): linked to `editor/stepping`, which teaches it |
| `audio-input:98` | feature | use | `audio.state` |
| `physics:172` | feature | use | `physics.stats` |
| `automation:157` | feature | use | Command scripts, the same format `editor.batch` and the export use |
| `automation:176` | feature | use | The Activity panel's **Copy as script** |
| `automation:666` | hands-on | home | A deterministic play-test: paused, an `input.sequence` with observations, checks on its samples |
| `automation:444` | concept | use | Determinism for agents and tests |
| `gamedev:229` | feature | link | The samples' regressions run by CTest (home `engineering/test-kinds`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A terminal: running a program with arguments, quoting a path, `\| Write-Output` on Windows | `start/install` | must |
| Reading a command and its JSON result | `start/how-to-read` | must |
| Opening a copy of a sample | `start/first-game` | must |
| Play, pause and step; "same inputs, same game" | `make/play-test-debug` | must |
| Fixed steps and the frame | `make/script-loop` | must |
| Script fields | `make/first-script` | must |
| Input actions | `make/input` | must |
| UI canvases, texts and buttons | `make/hud` | must |
| Menus, buttons and their events | `make/menus` | must |
| Random numbers and seeds | `make/recipes` | helps |

**Starting state.** A copy of the Tetris sample made with File ▸ Open Sample (its scene's entity IDs are those of the
sample, so the page's script names them), and the end checkpoint of `make/menus`, downloadable, for the UI section.

**Command-only steps.**

- Every step of the page that runs a test: the reader writes a command script and runs it with `StrataEditor --project
  <dir> --commands <file> --quit-after-commands`; no menu or button runs a command script. The page is track G's
  teacher of running a command script (R33, D20), so these steps need no `make/commands`.
- The commands inside the scripts (`play.start`, `play.step`, `input.sequence`, `component.get`, `script.setField`,
  `ui.create`, `ui.layout`, `ui.hitTest`, `input.click`, `viewport.capture`), which the scripts run, not the reader.
- The export of a whole session (`editor.activity.export`) needs StrataCLI and a running editor: moved to
  `make/with-an-agent` (process.md, "Allocation and part briefs"); this page uses **Copy as script** in the Activity
  panel instead.

## `make/commands` — Driving the editor from outside: the CLI and command scripts

**Covers.** The goal: drive a running editor from a terminal, run any command (also those no menu or button has) and
write scripts that build content. What must be true first: the terminal of `start/install`, command scripts as
`make/automated-playtests` wrote them, and the reader's Coin Run project open in the editor. The steps. One sentence on
the idea, linking `editor/commands`: every menu and button runs a command, and the same commands answer a terminal. Find
the editor: the status bar's automation pill ("port N · no agent"), `StrataCLI status`; or start one with `StrataCLI
launch --project <dir>` (`--headless`, `--no-gpu`). `StrataCLI list` for the commands and their one-line descriptions;
`StrataCLI list --json` for a command's parameters as a JSON Schema (which names are required, their types). Call one:
`StrataCLI call editor.status`; parameters from a file (`@params.json`) or from standard input (`-`), because quoting
JSON on a Windows command line breaks; read the answer and the exit codes (0, 1 with the error's `data`, 2 no editor, 4
no answer in time, which is no failure: never start a second editor). Read an error: a misspelled parameter and the
error's list of the parameters the command takes. Steps with no menu or button: 200 coins scattered with one
`prefab.instantiate {instances: [...]}` in one undo step; a controller made with `animation.createController` (the step
`make/animation` named), and a pose previewed with `animation.preview` (the viewport's preview chip names it, and a
click on it stops it); a world's layers changed with `world.setLayers`, with one warning line: removing a layer that has
cells, or changing a layer's cell size, is refused unless `deleteCells` moves those cells to the trash; store-page
screenshots with `viewport.capture --save-image` at a quality and size, overlays off; probes baked with
`lighting.bakeProbes` and a GI view captured (`viewport.capture` with `debugView`), the agent route of
`make/reflections` and `make/gi`. A script that builds content: `editor.batch` with `bind` and `$ref`, atomic, so a
failed step undoes the batch, and the same steps as a `--commands` file. Commands that replace the scene refuse unsaved
changes unless `force`, and a script never forces away a person's work. What Strata does not do here: no place in the
editor's window types and runs any command (the Activity panel re-runs only commands the journal recorded). Result: a
scene changed from the terminal and a build script that repeats it. Variations: a wrapper script for a long command; a
headless editor with no window. The exercise: the scatter undone and redone from the terminal.

**Leaves out.**

- What a command is in the editor, and how the registry checks parameters → `editor/commands`
- The MCP server and its toolsets → `make/with-an-agent`
- Sockets, JSON-RPC and the editor's server → `automation/json-rpc`, `automation/rpc-server`
- Who may connect, tokens and session files → `automation/security`, `automation/sessions`
- StrataCLI's own structure → `automation/mcp`
- Every command with its schema → `reference/commands`

**Fit.** `fits`: about 3,700 words against M (3,000): about 17 steps with their terminal captures, one error read and
one batch, of which seven are steps no menu or button can do, two variations and the exercise take the most. The counts
of commands are never typed (the erratum below).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:247` | feature | home | StrataCLI: `launch --headless` and `--no-gpu`, `list`, `call cmd @p.json`; its MCP half (`StrataCLI mcp`, toolsets) is used on `make/with-an-agent` |
| `scene-ecs:600` | hands-on | home | Scattering 200 instances of a prefab with `prefab.instantiate {instances: [...]}` in one undo step (Coin Run's coin in place of the crates) |
| `render-core:667` | hands-on | home | Screenshots for a store page with `viewport.capture`: path, quality, size, overlays off |
| `render-indirect:540` | hands-on | home | G10: the probe bake and the GI view through StrataCLI (`lighting.bakeProbes`, `viewport.capture` with `debugView: "gi"`) |
| `new:6` | not-done | home | A place in the editor's UI to type and run any command; the Activity panel re-runs only commands the journal recorded. Evidence: `EditorLayer::DrawMenuBar`, `StrataEditor/src/EditorLayer.cpp:1449-1627`, has no such item; `StrataEditor/src/Panels/ActivityPanel.cpp:368-397` (Copy as script, Re-run, Undo to here) |
| `automation:656`, `automation:658`, `automation:660` | hands-on | home | First contact (`launch`, `status`, `list`, `call editor.status`, `call editor.quit`), a scene built from the shell with parameters from `@file`, a misspelled parameter's error read and fixed |
| `automation:664` | hands-on | home | A capture saved with `--save-image` from the scene's camera, with and without lights (preview lighting) |
| `automation:671` | hands-on | home | An atomic `editor.batch` with `bind` and `$ref`; one failing step undoes the batch |
| `new:7` | erratum | home | The inventories count 151, 153 and 154 editor commands; the page never types a count and writes `:value{key="commands.count"}`. Evidence: `StrataTests/src/Editor/CommandJournalTests.cpp:102-164` lists the commands of `StrataEditorCore` and `:234` checks the number; `StrataEditor/src/EditorLayer.cpp:177, 233` add `editor.showPanel` and `editor.showDialog` |
| `new:25` | hands-on | home | Exercise, done with StrataCLI: the scatter of 200 coins undone with one `StrataCLI call edit.undo`, checked with `entity.find`, and brought back with `edit.redo`. Evidence: `StrataEditor/src/Editor/EditorStateCommands.cpp:364`, `:376` (`edit.undo`, `edit.redo`); `StrataEditor/src/Editor/Commands/EntityCommands.cpp:401` (`entity.find`) |
| `gamedev:246` | feature | use | Commands are the API: one registry with a JSON Schema and a description per command (home `make/editor-tour`) |
| `automation:192-193`, `automation:195`, `automation:197`, `automation:199` | feature | use | StrataCLI's commands, exit codes, image results, finding the editor, launching one |
| `automation:148-150` | feature | use | `editor.status`, `editor.commands`, `editor.batch` |
| `automation:269` | concept | use | Why automate an editor at all |
| `automation:534`, `automation:577`, `automation:586` | figure | use | Commands are the API (fan-in); the status bar's automation pill; terminal sessions |
| `automation:642-643` | rule | use | A CLI timeout is no failure, never start another editor; never force away a person's unsaved changes (the second's home is `make/with-an-agent`) |
| `editor-core:175` | feature | use | `prefab.instantiate` and its `instances` |
| `editor-core:241` | feature | use | `editor.batch {steps, atomic}` (home `editor/command-scripts`) |
| `animation:185` | feature | use | `animation.createController` |
| `animation:190` | feature | home | The viewport's preview chip (`ViewportPanel::DrawPreviewChip`, `StrataEditor/src/Panels/ViewportPanel.cpp:464`): it names the pose that `animation.preview` shows, and a click on it stops the preview |
| `worlds-runtime:111` | feature | use | The world commands, `world.setLayers` among them: removing a layer that has cells, or changing a layer's cell size, is refused unless `deleteCells` moves those cells to the trash (`StrataEditor/src/Editor/EditorWorldCommands.cpp:670-675`) |
| `render-scene:181` | feature | use | `renderStats` in a capture's answer |
| `automation:705`, `automation:713`, `automation:766-767` | term | link | Command, binding and `$ref`, StrataCLI, exit code |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A terminal: running a program with arguments, quoting a path | `start/install` | must |
| JSON written by hand; command scripts with `expect`, `bind` and `$ref` | `make/automated-playtests` | must |
| Reading a command and its JSON result | `start/how-to-read` | must |
| Prefabs and their instances | `make/prefabs` | must |
| Undo | `make/project-files` | must |
| Unsaved changes and saving | `make/project-files` | must |
| Reflection probes and the GI views | `make/reflections` | helps |
| A world's layers | `make/large-worlds` | helps |
| An animation controller | `make/animation` | helps |

**Starting state.** The end checkpoint of `make/project-coin-run`, downloadable, open in the editor (its coin prefab is
what the scatter step places).

**Command-only steps.**

- Every step: the page teaches running commands from a terminal, and its steps are `StrataCLI` lines.
- The steps no menu or button can do: `prefab.instantiate {instances: [...]}`, `animation.createController`,
  `animation.preview`, `world.setLayers`, `viewport.capture --save-image` and `lighting.bakeProbes` from the terminal,
  `editor.batch`; the page itself teaches calling a command with StrataCLI (R33, D20).
- The batch's steps run again as a `--commands` file: a command script, run as `make/automated-playtests` (a Need)
  taught.

## `make/with-an-agent` — Making a game with an AI agent

**Covers.** The tutorial lets an AI agent build a level in the reader's editor while the reader watches, checks and
undoes. It opens with the idea: an agent is a program driven by a language model that acts through tools; Strata gives
it the editor's commands as tools through MCP, so it does what the menus do, and every step it takes is journaled (the
agent's path: the agent, `StrataCLI mcp`, the editor's loopback connection, the same commands as the UI). Sections, each
ending in a checkpoint: connect an agent from the launcher's "Connect an AI agent" card (the exact `claude mcp add
strata -- "<StrataCLI>" mcp` line, copied), and see the automation pill turn to "Agent connected"; what the agent sees:
the `core` toolset (at most 32 tools), `strata_describe`, `strata_toolsets` to enable another group such as `scene`,
`strata_call` for any command, and the shipped skills (editor automation, scripting, making a game) placed where the
agent reads them; ask the agent to place props with `asset.place` and watch the viewport's agent chip and the outline
flash of what it changed; the Activity panel: every row by the person, the agent (by name) or a script, a row's details,
**Copy as script**, **Re-run**, **Undo to here**; steering an agent safely (unsaved changes are refused unless forced, a
toast names the agent that discarded changes and offers Recover, an agent's name is shown but never trusted, what to ask
an agent to check: `editor.status`, a capture; and one sentence with a pointer to recovery on `make/project-files`: an
editor the agent started with `strata_launch_editor` closes after 600 s without a client, and its unsaved scene changes
are discarded and kept as recovery data); the session as a regression: note where the session starts, have
`editor.activity.export` write it as a command script with `bind` and `$ref`, add `expect`s, copy the project's
`Scripts/` (and any source assets the session generated) into a fresh copy, because files written outside commands are
not in the script (if you do not see the scripts build in the replay, they were not copied), and run the script on the
copy with `StrataEditor --commands` (G15); the whole game the agent way: the `strata-make-a-game` playbook in eight
steps (an editor, a project and a plan, assets, scripts, the scene, playing and looking, a regression, the export), with
the Tetris sample as the game an agent made through the editor alone. What Strata does not do here: MCP resources,
prompts and logging, a transport other than the standard streams, and cancellation (an agent that gives up loses only
the answer; the editor finishes the command). The exercise: an agent's three props taken back with **Undo to here**. At
the end the reader can connect an agent, follow and undo what it does, and keep its work as a test.

**Leaves out.**

- Why automate an editor, tools for agents and accountability, as engine design → `automation/agents`
- The MCP server's protocol, tool mapping and token budget → `automation/mcp`
- The journal, command kinds and how a replay script is built → `editor/journal`
- Running commands from the terminal → `make/commands`
- Command scripts and their checks → `make/automated-playtests`
- The Activity panel's drawing → `editor-ui/instrument-panels`

**Fit.** `fits`: about 4,450 words against L (5,000): the idea and its diagram, seven sections of about 17 steps (an
agent's answers shown as text captures), the safety rules, the playbook's outline and the exercise take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:55` | feature | home | The Activity panel: every command with who ran it (person, agent, script); a session exported as a replayable command script |
| `gamedev:248` | feature | home | The skills shipped in the archive's `Skills/`: editor automation, scripting, making a game |
| `gamedev:433` | figure | home | The agent's path: the agent, MCP (`StrataCLI mcp`), JSON-RPC on loopback with a token, the editor's commands (the same as the UI's) |
| `gamedev:455` | figure | home | The Activity panel listing commands by the person and by an agent |
| `gamedev:548` | hands-on | home | G15: an agent connected through MCP places props with `asset.place`; the Activity panel; the session exported as a command script and replayed on a fresh copy |
| `gamedev:660` | term | home | MCP, toolset |
| `automation:225` | feature | home | The package readme's "Connect an AI agent": the `claude mcp add` line, the toolsets, where the skills go |
| `automation:581` | figure | home | The Activity panel after an agent's session: rows by source, an expanded entry, Copy as script, Re-run, Undo to here |
| `automation:584` | figure | home | The toast that names the agent that discarded unsaved changes, with Recover |
| `automation:643` | rule | home | Commands that replace the scene refuse unsaved changes unless `force`; an agent never forces away a person's work |
| `automation:662` | hands-on | home | Connect Claude Code with `claude mcp add strata -- <bin>/StrataCLI mcp`, ask for a scene, watch the pill, the chip and the Activity panel, enable `scene` with `strata_toolsets` |
| `automation:668` | hands-on | home | A session turned into a regression test: note `journal.latest`, build, `editor.activity.export`, add `expect`, copy `Scripts/` (and generated source assets) into the fresh copy first, because files written outside commands are not in the script (`.claude/skills/strata-make-a-game/SKILL.md:441-443`), run it on the copy with `--commands` (passed to `make/automated-playtests`; it needs StrataCLI, so it is taken here) |
| `automation:673` | hands-on | home | A whole game the agent way: the `strata-make-a-game` playbook, Tetris as the reference, a regression script and the exported game run headless |
| `editor-ui:694` | hands-on | home | Connecting an agent from the launcher, watching the agent chip and the outline flash, inspecting its work in the Activity panel |
| `new:19` | not-done | home | MCP resources, prompts and logging, a transport other than the standard streams, and cancellation: the MCP server offers tools only, and nothing cancels a command once it is sent; an agent that gives up or disconnects only loses the answer, and the editor finishes the command, as after the CLI's exit code 4. Evidence: `StrataCLI/src/CLI/McpServer.cpp:367-372` (every notification but `notifications/initialized` is dropped), `:379-397`, `:420` (the `tools` capability alone); `StrataCLI/src/CLI/CliApplication.cpp:357-358` (standard input and output); `StrataCLI/src/CLI/CliApplication.h:24` (exit code 4: the command may still be running in the editor); `git grep -n -i "notifications/cancel" 822a7a46 -- StrataCLI Strata/src/Strata/Network` finds nothing |
| `new:26` | hands-on | home | Exercise, done in the editor: the agent asked to add three props, its work taken back with **Undo to here** on the Activity panel's last row before the agent's first, and the Hierarchy checked. Evidence: `StrataEditor/src/Panels/ActivityPanel.cpp:393-397` (Undo to here undoes the steps after the row) |
| `automation:182-185` | feature | use | The automation pill, the agent chip, the outline flash, the launcher's "Connect an AI agent" card |
| `automation:176` | feature | use | The Activity panel: rows, details, Copy as script, Re-run, Undo to here |
| `automation:152`, `automation:173` | feature | use | `editor.activity.export`; the replay script with its bindings |
| `automation:207-209`, `automation:211`, `automation:213-214` | feature | use | MCP's protocol, the generic tools, commands as tools, toolsets, the 32-tool budget, `strata_describe` |
| `automation:215`, `automation:136` | feature | use | An editor started with `strata_launch_editor` closes after 600 s without a client, and its unsaved scene changes are discarded and kept as recovery data (`StrataCLI/src/CLI/McpServer.h:34-36`; `StrataEditor/src/EditorLayer.cpp:684-691`) |
| `automation:223-224` | feature | use | The skills `strata-editor-automation` and `strata-make-a-game` |
| `automation:415`, `automation:430`, `automation:444` | concept | use | MCP and tool design for models, accountability (journal, presence, replay), determinism for agents |
| `automation:530`, `automation:562`, `automation:564` | figure | use | The four layers, the toolsets, the replay export |
| `automation:574`, `automation:579`, `automation:588` | figure | use | The launcher's card, the agent chip and flash, the agent's tool list |
| `automation:634`, `automation:640` | rule | use | At most 32 tools by default; client names shown, never trusted |
| `editor-core:243` | feature | use | `editor.activity` and `editor.activity.export` (home `editor/journal`) |
| `editor-core:504` | figure | use | Record and replay: entries, the export, a run on a copy |
| `editor-ui:204`, `editor-ui:214` | feature | use | The agent chip and flash; the launcher with its agent card |
| `automation:704`, `automation:769`, `automation:771-773`, `automation:780`, `automation:782-783` | term | link | Agent, MCP, tool, toolset, core toolset, activity journal, presence, replay script |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Running commands from a terminal with StrataCLI | `make/commands` | must |
| Command scripts, `expect`, `bind` and `$ref` | `make/automated-playtests` | must |
| Undo and unsaved changes | `make/project-files` | must |
| Prefabs and placing them | `make/prefabs` | must |
| The launcher | `start/first-game` | must |
| Installing a program | `start/install` | helps |

**Starting state.** The page's starting checkpoint, downloadable: a new project from the Basic 3D template with the
tutorial asset pack's props as prefabs (CC0, credited), saved; an AI agent program that speaks MCP installed on the
reader's computer (the page names Claude Code, whose line the launcher shows); and a copy of the Tetris sample for the
last section.

**Command-only steps.**

- `claude mcp add strata -- "<StrataCLI>" mcp`, the agent program's line that the launcher's card gives.
- The session's export, `editor.activity.export`: a command called with StrataCLI, taught by `make/commands` (a Need).
- The replay on a fresh copy: a command script run with `StrataEditor --commands`, taught by `make/automated-playtests`
  (in the closure through `make/commands`).

## `make/samples` — Studying the samples

**Covers.** The goal: learn from the three samples that block C does not build (Physics Playground, Open World and the
High Desert Outpost) by playing them, reading how they are made and changing one thing. What must be true first: Open
Sample as `start/first-game` used it. The steps. Open a copy: **File ▸ Open Sample** (or the launcher's sample cards)
makes a copy in a folder the reader chooses, without the original's `.strata` folder, and the sample's picture becomes
the copy's; Play builds the scripts first. Read the README: what it shows (a table from each engine feature to the
files that hold it), its controls, how it was made (by an AI agent through the editor, with the commands named) and its
credits (the `CREDITS.md` table of files, source, author, license, attribution and changes); each sample's regression
is a command script of the engine's tests. Then the three samples, each with what to look at and one change to try.
Physics Playground: about 600 bodies of four materials, triggers counting the goal's balls, the Ghost layer that does
not collide with balls, a ball shot through the cursor and a body grabbed, 100 balls poured in one
`Scene::InstantiateMany` call, impact sounds within a budget of voices, slow motion, a reset that reloads the scene.
Open World: a world of three layers in 64 m cells around a persistent scene of 97 terrain tiles, 20,000 props drawn on
the GPU, a teleport that prefetches cells and waits for the ground, foxes in streamed cells, a day that turns into night
under the atmosphere with campfires at dusk, a loading scene. High Desert Outpost: the graphics showcase, made from
scans and generated terrain and props, three times of day each with two baked probes switched with a hold, a camera
tour, walking and flying, a photo mode (time, exposure, field of view, focus, f-number, the players' quality and
anti-aliasing), flickering fire and lanterns; its copy is the largest of the samples. The samples' rules as a model for
the reader's own game: a README with the feature table, controls, how it was made and credits, a picture, a few
screenshots within a size limit, CC0 or CC-BY assets only. Result: a list of where each feature lives in the samples.
Variations: reading a sample's regression script; changing a value of a sample's script and hot reloading it. The
exercise: the Open World's day shortened in the Inspector until the campfires light.

**Leaves out.**

- Tetris, built as a project → `make/project-tetris`
- The Third-Person Adventure, built as a project → `make/project-platformer`
- Templates, samples as copies and recent projects, as the editor models them → `editor/projects`
- The launcher and the Open Sample dialog as UI → `editor-ui/launcher-dialogs`
- Each feature the samples show → `make/physics`, `make/large-worlds`, `make/reflections`, `make/look`
- How the samples' regressions run in the engine's tests → `engineering/test-kinds`

**Fit.** `fits`: about 3,750 words against M (3,000): three steps for opening and reading, about 630 words for each
sample with its screenshots and its change to try, the samples' rules, two variations and the exercise take the most.
The Showcase is a wave 8 sample: the pin move's diff decides what is read again.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:35` | feature | home | Samples and Open Sample: `Samples.json`, copies without `.strata`, the picture as the copy's thumbnail |
| `gamedev:256` | feature | home | Physics Playground: bodies, materials, triggers, the Ghost layer, shoot, grab, pour with `InstantiateMany`, impact sounds, slow motion, reset, hot reload, the export's demo |
| `gamedev:257` | feature | home | Open World: three layers in 64 m cells, 97 terrain tiles, 20,000 props drawn GPU-driven, the source on the player, teleport with prefetch, foxes, day and night, the loading scene |
| `gamedev:258` | feature | home | High Desert Outpost: scans and generated content, three stations with baked probes, the tour, walk and flight, photo mode, flicker, the loading scene |
| `gamedev:260` | feature | home | The samples' rules: README with a feature-to-file table, controls, how it was made, credits; `CREDITS.md`; picture and screenshots within a size; source assets within a size; game identity |
| `gamedev:472` | figure | home | Physics Playground: the overview, the ball pit after a pour (existing `Screenshots/`), a grab, slow motion |
| `gamedev:473` | figure | home | Open World: the tour (existing `Tour.png`), the forest (`Forest.png`), night with campfires, the teleport's fade; a capture that shows a fox names the fox's authors and license in its caption (`appendix/credits` holds the full entry); `Samples/OpenWorld/Screenshots/Tour.png` and `Forest.png` show no fox |
| `gamedev:474` | figure | home | Showcase: the six tour shots (existing `Screenshots/`), the photo mode's panel |
| `new:27` | hands-on | home | Exercise, done in the editor: in the Open World copy, the sun's `DayNight` fields set in the Inspector, `DayLengthSeconds` 60 and `TimeOfDay` 17, then Play: the campfires light at dusk and the log says so. Evidence: `Samples/OpenWorld/Scripts/DayNight.h:19-20`, `:61-68` |
| `worlds-runtime:179` | feature | use | Samples as copies, the picture cards (home `editor/projects`) |
| `worlds-runtime:185` | feature | use | The Open World sample's world, as its README describes it |
| `editor-ui:215` | feature | use | The Open Sample dialog |
| `editor-ui:550` | figure | use | The New Project and Open Sample dialogs |
| `gamedev:254-255` | feature | link | Tetris and the Third-Person Adventure, built in block C |
| `gamedev:229` | feature | link | The samples' regressions (home `engineering/test-kinds`) |
| `gamedev:519` | rule | use | Asset licenses: CC0 or CC-BY only, credited (home `make/assets`) |
| `gamedev:575` | term | link | Sample |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Opening a copy of a sample; Play | `start/first-game` | must |
| Reading a script and its fields | `make/scripting-scene` | must |
| Hot reload | `make/first-script` | must |
| Asset licenses and credits | `make/assets` | must |
| Bodies, triggers and collision layers | `make/physics` | helps |
| Worlds, cells and prefetching | `make/large-worlds` | helps |
| Baked probes and times of day | `make/reflections` | helps |
| The camera's image and depth of field | `make/look` | helps |

**Starting state.** No project of the reader's and nothing to download: the three samples ship with the editor, and the
steps open copies of them from the editor's launcher.

**Command-only steps.** none

## Passed on

none

## Not taken

none

## Questions for the planner

none
