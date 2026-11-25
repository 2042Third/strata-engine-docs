# Brief: `make/lamps`

| Field | Value |
| --- | --- |
| Title | Lamps: point, spot and area lights and their shadows |
| Kind | T |
| Size | L |
| Tracks | G |
| Needs | `make/project-coin-run` |
| From | render-direct "Lighting a scene in the editor (tutorial)" (the indoor half); gamedev §1.8 (Source Radius, local shadows; hands-on G7's lantern) · W8 |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b2-12 | should | other | `make/reflections` (`gamedev:386`; G16, `gamedev:549`) | The first excerpt's light values are not the real units the book teaches: `SunIntensity` 3 lux, `MoonIntensity` 0.05 lux (no script field, so only the code changes it) and campfires of 6 cd. The courtyard's sun is the Clear preset's 120,000 lux, `make/lamps` taught a 0.2 lux moon, and the Showcase's own script uses 120,000 lux. Ported as it stands, G16 drops the courtyard's sun to 3 lux, and probes baked under 120,000 lux then outshine it. | Two sentences after the excerpt: the sample's values are small but agree with each other, and automatic exposure and the atmosphere, which follow the sun, hide the scale; G16's port sets `SunIntensity` to 120,000 in the Inspector, the moon to about 0.2 lux in the code, and the campfires in candela as `make/lamps` taught. About 70 words. | `allocation/make-b2.md:7`, `:120-121`, `:154-155`; `allocation/make-a.md:700`; pin: `Samples/OpenWorld/Scripts/DayNight.h:19-26`, `:61`, `:66`; `Samples/OpenWorld/Scripts/DayNight.cpp:3-12`; `Samples/Showcase/Scripts/Stations.h:47-48`; `StrataEditor/src/Panels/InspectorPanel.cpp:1693` |
| critic-make-b2-21 | could | thin-home | `make/lamps` (the shadows section) | The page sets "the two biases" but never says what they fight: acne (stripes of shadow on lit surfaces), and shadows that detach from their casters when a bias is too large. `make/lighting` teaches no bias, and the terms' home is on track E. | A `use` row of `render-direct:718` and one sentence for each bias, from its tooltip, in the step that sets them. About 50 words. | `allocation/make-b2.md:13-15`; `allocation/make-a.md:717-719` (the sun's shadows without biases); `inventory/render-direct.md:718`; pin: `Strata/src/Strata/Renderer/RendererComponents.cpp:103-106` |
| critic-make-b2-22 | could | stale-item | `make/lamps` (`render-direct:76-79`) | The row gives "the Point and Spot Light fields with their defaults (10 cd, 10 m, Cast Shadows off)", which are the point light's. A new Spot Light has 20 cd and a Range of 15 m, and its Inner and Outer Cone Angles (20 and 30) are half angles, so an Outer Cone Angle of 30 lights a cone 60 degrees wide. | The row's take names both lights' defaults, and the spot's step says that the angles are half angles. About 30 words. | `allocation/make-b2.md:11-12`, `:57`; pin: `Strata/src/Strata/Renderer/RendererComponents.h:53-54`, `:69-73`; `Strata/src/Strata/Renderer/RendererComponents.cpp:348-349` |
