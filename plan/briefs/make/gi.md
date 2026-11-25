# Brief: `make/gi`

| Field | Value |
| --- | --- |
| Title | Trying global illumination |
| Kind | H |
| Size | M |
| Tracks | G |
| Needs | `make/reflections` |
| From | render-indirect "Trying global illumination in a scene" · W8 |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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
| critic-make-b2-2 | must | shape | `make/commands` (Starting state; `animation:185`, `animation:190`, `worlds-runtime:111`, `render-indirect:540`) | The page starts from Coin Run's end checkpoint: a rolling ball and coins. That project has no skinned model with clips, no world, no reflection probe and no global illumination, so the steps `animation.createController`, `animation.preview`, `world.setLayers`, `lighting.bakeProbes` and the GI capture have nothing to act on. | The Starting state names the project each section opens, each a download of the book (the end checkpoints are planned already; the last two are states of those pages' steps, which the book adds as downloads): Coin Run's end for the scatter, the batch and the store-page captures; the end checkpoint of `make/animation` (its robot and clips) for the controller and the preview; the end checkpoint of `make/large-worlds` for `world.setLayers`; the courtyard of `make/reflections` with its probe, and the room of `make/gi` with Global Illumination on, for the bake and the GI view. About 60 words. | `allocation/make-b2.md:800-807`, `:869-870`, `:875-876`; `outline-1.md:196` (Coin Run as a rolling ball); pin: `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153-157` (each state plays an animation clip); `StrataEditor/src/Editor/EditorWorldCommands.cpp:670-673` (a world's layer list); `StrataEditor/src/Editor/EditorLightingCommands.cpp:872-883` (the scene's probes) |
