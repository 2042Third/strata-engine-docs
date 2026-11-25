# Notes: light/measuring-light

## New terms

None proposed. The page defines **percentile** in bold, a term homed in `core/profiling` per the brief's Assumes row; if the glossary does not home it there, the clerk should home it here (definition: the value below which a given share of the counted values lie; alias: 5th, 50th, 95th percentile).

## Requests

- Extra word: "bin" and "bins" (a histogram's counting slot; the engine's own name, 18 uses on the page). The page has a word-list failure for them until the clerk admits them.
- Figures: `views-lit`, `views-lighting`, `views-indirect`, `views-luminance`, `views-albedo` (one scene, five pictures) and `albedo-cubes` (black, gray and white cubes in the Albedo view), all `scene` kind from the `basic3d` template with materials made by `material.create`. The brief's luminance view of a sunlit street and of an interior is not requested: it needs a street scene and an interior scene that no committed project holds. The page gives the street and the room as a worked example with numbers instead.
- No editor window layout is needed.

## Since

`since: 0.7.0`. The inventory rows (`render-direct`, `render-indirect`) date the lighting views and their statistics 0.7.0.

## Not verified

- Which frame count the statistics arrive after: the page states no number, only that they come back through a ring of three readbacks and carry the render number they measured.
- That the `viewport.capture` command with only `debugView` set takes a picture with defaults for every other parameter (the schema says each has a default; no run was made).
- The street and room luminance example uses textbook values (100,000 lux full sun, 200 lux room, Lambertian surfaces), not Strata scenes.
- Whether the base colors of the exercise (copper, gold) match the editor's material presets; they are common reference values chosen for the exercise.

## Findings not applied

- The brief says `viewport.setSettings` returns `debugView.lighting`. At the pin, `setSettings` returns the viewport's settings (`debugView` as a name); only `viewport.capture` returns `debugView.lighting` (`StrataEditor/src/Editor/EditorViewportCommands.cpp`, `DescribeDebugView`). The page says capture.
- The brief's figure of a Luminance view of a sunlit street and an interior is not requested (see Requests).
- The `look-dev`, white furnace, exposure and legend topics are links or leave-outs as the brief says; no engine-vs-brief difference found there.

## Figures

Photographed 2026-11-18, all six published.

- Round 1: `views-lighting`, `views-indirect`, `views-luminance` and `views-albedo` failed: the figures share one
  project copy and the material files `views-lit` made stay on disk (`material.create`: already exists). Each of the four
  now makes its own materials (`Materials/Chalk<View>.stmat`, `Clay<View>.stmat`); same colors and roughness.
- Camera of the five views moved closer (0, 1.7, 4.2 toward 0, 0.5, 0) so the cube and sphere fill more of the frame.
- Texts fitted to the pictures: the basic3d sun comes from the upper right (shadows fall left), not the upper left;
  in the Indirect view the floor turns dark blue and the shadows vanish, but the pale cube stays bright (albedo 0.7
  under the sky), so "surfaces facing the sun go dark" was replaced; in the Luminance view the shadows are green (not
  dark blue), the cube near-white, the floor yellow, and the sky crosses several bands; the Albedo sphere reads
  brick-red. `albedo-cubes` shows exactly its caption (blue black cube, plain gray, red-striped white cube).
- Mended 2026-11-18 (a viewer's four faults, words only, no retake): `views-luminance` now names its bands (floor 14 to
  15, its far right corner and the ground beyond 15 to 16, cube 16 and above, shadows 11 to 12, teal core 10 to 11; the
  reasoning is the recipe's `numbers`). The viewer proposed shadows at 10 to 11; the sphere's smooth shading touches the
  seven flat colors in order, so they are consecutive bands and the green is 11 to 12. The captured colors are paler
  and less saturated than the palette of `SceneRenderer.h` (band 9, orange 250/179/61, shows as 233/204/116), so the
  captions name the colors as seen. `views-lighting` says why the cube's top merges with the floor (both face the sun:
  159 against 157); `views-indirect` says why the sphere is orange below and mauve on top (the environment's sunlit
  ground below the horizon is its brightest half; the cube's top takes the blue sky).
- Taken again 2026-11-23 at the pin v0.8.0 (319075e3, Release build), one hold, no recipe change: all six PNG
  originals are byte-identical to the published ones (`figures.py compare`: 0 of 6 differ; `publish`: 6 unchanged), so
  the files and `taken.json` stay as stamped at 822a7a46. Looked at again: the captions still state what each shows.

## Clerk

- Admitted to extra-words.txt: bin, bins.
- Percentile is left for the planner: the brief homes it on core/profiling, which uses it, and the glossary has no entry; the page's bold may stay.

## Pin v0.8.0

- The enum quote moved to `SceneRenderer.h#L346-L361`: 0.8.0 appended `Specular`, `Diffuse` and `Clusters`. Specular and Diffuse (one kind of light alone, `IsLightKindView` in `Strata/shaders/Scene/Forward.frag.slang`, exposed like the image, counted as light) are presented with the lighting views; `Clusters` is a value view of the many lights page, named in a callout only. Words were cut elsewhere to stay within size M.
