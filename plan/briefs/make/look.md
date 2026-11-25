# Brief: `make/look`

| Field | Value |
| --- | --- |
| Title | The camera's image |
| Kind | T |
| Size | L |
| Tracks | G |
| Needs | `make/project-coin-run` |
| From | gamedev "The camera's image and graphics quality" (the camera half); render-image "Tutorial: giving a scene a camera look"; Manual/Camera; height fog (moved from `make/lighting`, whose tutorial has no room for it); use home of height fog and of the quality rows of each effect · W8r (the effects' quality presets) |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `tone-mapping-make` | Tone mapping (make) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b2-17 | should | shape | `make/look` (the exercise; `render-direct:646`) | The exercise lays valley fog on "the valley floor", but the page's scene, the Third-Person Adventure's course, is floating islands with no valley; the inventory's hands-on was written for a valley. | The exercise lays the fog as a sea below the islands (its base under the lowest island, a falloff for a layer 50 m thick), or it opens the High Desert Outpost copy in Edit mode, whose 300 m valley fits it. No words added. | `allocation/make-b2.md:301-302`, `:348`, `:368-369`; `inventory/render-direct.md:646`; pin: `Samples/ThirdPerson/README.md:3`; `Samples/Showcase/README.md:20` |
