# Walk log: track G (persona G0), segment 9, at v0.8.0

Entries walked: `make/lamps`, `make/reflections`, `make/gi`, `make/look`, `make/quality`.
Package: official Strata 0.8.0 Windows package (`Strata-0.8.0-windows-x64`); one StrataEditor session (headless) driven by
StrataCLI under one perf-lock hold; projects in `walk-G-final-9/proj` (Lamps stage 1, Courtyard, a new Basic 3D project Room,
two copies of the Third-Person sample, Menus stage 7).

Not walked: clicks, menus, drags and the Inspector (everything through commands, read back with `component.get`, `scene.hierarchy`,
`viewport.capture` and its `renderStats`; about 20 pictures looked at and compared with the page's). Not done: the Stats chip
itself (read through `renderStats`), the motion blur streaks, depth of field and lens flare looks, the exported game with
`--quality low`, clicking the new Graphics toggles (the settings panel is hidden at start), the Medium exercise of
`make/quality`, sounds. Exercises: Basic and Hard of `make/lamps` by hand (answers matched), Medium run from its worked
solution; Hard of `make/reflections` run from its worked solution (matched: Sun 0.2 at 21:00, fire 100 cd); Hard of `make/gi` run.

## WK1
- Entry: `make/lamps`; page: same; section: "What you need".
- Kind: left the book.
- "Download the start checkpoint of this page" has no link: the page offers only Checkpoints 1 to 8. I opened the Checkpoint 1
  zip (its project already has the yard, the moon at 0.2 and the exposure at 4, which the first section builds) and walked on
  from "Light the yard with one lamp". The yard's start state (no moon, day) never exists as a download.

## WK2
- Entry: `make/lamps`; all five pages; every "With a command" tab that names an entity.
- Kind: failed.
- The tabs are written as `{ "command": "component.set", "entityName": "Sun", "parameters": {...} }`. Given to `StrataCLI call
  component.set` the answer is `Unknown parameter 'entityName' ... (parameters: component, entities, entity, values)`. A reader
  has to find the id with `entity.find` and pass `entity`. I wrote a small script that does this; no page I read says that
  `entityName` is not a parameter of the call. Tabs with `<id of Lantern>` need the same lookup by hand.

## WK3
- Entry: `make/lamps`; section: "Add a bulb", "Make the lantern a prefab" (the `prefab.apply` and `setParent` steps).
- Kind: guessed.
- The bulb tab gives `material.set` and the bulb's `entity.create` only in a sentence; I guessed `properties` and the
  `Material` key of `MeshRenderer` (both worked). The tab for `prefab.apply` shows no parameters: I guessed `entity` (the
  root); `entities` is refused. After `entity.setParent` the child's Translation was already 0, 0, 0 (world kept), so the
  step "Set the Translation of both to 0, 0, 0" had nothing to do.

## WK4
- Entry: `make/lamps`; section: "Give the lanterns shadows", step "Count the shadowed lamps".
- Kind: did not match (a command cannot read it).
- The tab `viewport.setSettings {"stats": true}` answers with the view settings only; no command prints the line
  "4 of 4 shadowed lights ... views drawn". I took it from `viewport.capture`'s `renderStats` (`localShadowLights 4`,
  `localShadowRequested 4`, `localShadowViewsDrawn 0` after the shadows were drawn; 8 while the arm turned, 0 when it stood
  still). The values agree with the page ("six or more", then 0), but a reader of the tab cannot know where to look.

## WK5
- Entry: `make/lamps`; section: "Move a lamp and switch it", step "Make the script LanternSwitch".
- Kind: failed.
- "Replace the new file's content with the code above": the code shown is "lines 5-28" and starts at `class LanternSwitch`.
  Replacing the file with it, `script.build` failed: `error C2504: 'Script': base class undefined`, `C3646: 'Lamp': unknown
  override specifier`. I had to add `#include "StrataScript/StrataScript.h"` and `using namespace Strata;` (lines 1-4, which
  the page does not show) from the template the command had made. After that the build, `script.add`, `script.setField`,
  play, `input.key L` (Intensity 0, then 64) all matched.

## WK6
- Entry: `make/lamps`; section: "Light the hut with a rectangle", exercise Medium.
- Kind: did not match.
- The worked solution (`exercise-2.zip`, a commands file) ran without a failure, but on the finished yard (Checkpoint 8) the
  hut's ceiling panel is on and the exposure is automatic, so the picture of the hut inside is a bright white room, not the
  candle-and-lamp night the exercise describes ("exposure about -2"). The page does not say to switch the panel off first.

## WK7
- Entry: `make/reflections`; page: same; section: "Give the room a reflection probe" and "Make the floor wet".
- Kind: guessed.
- The camera tab for the limits step gives only `camera.set {"position": ...}` and says to turn with the mouse; I used the
  `target` parameter (accepted) because a CLI reader has no mouse. Likewise "Put the Scene view in the doorway, looking in" has
  no command; I used `camera.set` with position and target. The probes and the bakes (`lighting.bakeProbes`, six bakes, the
  files in `Lighting/Main`) and the Indirect and AO views matched the "You should see" lines.

## WK8
- Entry: `make/reflections`; section: "Give the courtyard a day" and exercise Hard.
- Kind: guessed.
- The Hard solution's `stage-1.commands.json` creates the class, but the port `Scripts/DayNight.cpp` is in the zip beside it
  and no command copies it: I copied it by hand between stage 1 and stage 2 (stage 2 then ran with no failure and matched). The
  page's Medium and High quality step was only set (`viewport.setSettings {"quality": ...}`), not compared by eye.

## WK9
- Entry: `make/gi`; page: same; section: "What you need".
- Kind: guessed.
- "A new project from the Basic 3D template" has no command in a tab; I used `project.create` and had to find out that it
  wants `directory` and `name` (the first try with `path` was refused). The page's one download is the finished project, which
  I did not use. Building the room, camera, GI on, GI view, Open view, Voxels view, the thin wall (magenta, 45,669 pixels),
  the off/on settle, the sun turn, intensity and Medium (the picture was bit for bit the same as GI off) all matched.

## WK10
- Entry: `make/gi`; section: "Enable global illumination and read it", step "Read the probes".
- Kind: did not match (could not tell).
- The page says the probes inside the floor, ceiling and walls are dark red (dead) and that the legend counts both. The capture
  reports `deadProbes: 0` and `liveProbes: 92160`, and the spheres in the room's air are dark maroon, so I could not tell
  dead from alive in the picture.

## WK11
- Entry: `make/gi`; exercise Hard (worked solution and "Voxels" view).
- Kind: did not match.
- The page expects the error color only at 0.05 m ("on the fixed 10 cm grid only the 0.05 m wall lies inside one voxel").
  I ran thicknesses 0.25, 0.20, 0.15, 0.10 and 0.05 with the inner face at x = 2 (centers 2 plus half): none of the five
  pictures held a magenta pixel (0 of 921,600), the 0.05 wall looked dark gray. The 0.06 m wall at x = 2.05 of the earlier
  step did turn magenta.

## WK12
- Entry: `make/look`; page: same; section: "What you need" and "Start from the course".
- Kind: left the book.
- "One file from this page's download, warm-look.cube": the page offers only commands files (and a solution zip), no
  `warm-look.cube`. I wrote a 33-point warm `.cube` myself (a guess at what the page means) and imported it with the
  `asset.import` tab (Size 33 matched). The Checkpoint 4 commands file starts with `asset.info Lookups/warm-look.cube`, which
  fails (-32602) when the file was not imported first; the other eight stage files ran with no failure on a fresh copy.
- The copy of the Third-Person sample: the page says File > Open Sample; the CLI has no tab. I found `project.openSample`
  with `StrataCLI list`, and passed `sample` and `directory` (guess).

## WK13
- Entry: `make/look`; section: "Set the exposure", step "Open the Luminance debug view".
- Kind: did not match.
- "colored bands, each one stop wide, so the ground in the sun lies several bands above its shadow": the capture was one flat
  dark blue (lighting stats: `sunIlluminance` 3.26, `surfaceEv100` median 1.9, so the sample's light lies far below the view's
  range). No bands could be seen; checked again after a wait of 30 frames.

## WK14
- Entry: `make/look`; section: "Give the course a night look".
- Kind: did not match (small).
- After the moonlight and the recipe (Exposure -1.5, Min EV -2.5, 4500 K, Toe 0.6, Bloom 0.06) the picture was nearly black
  with a teal island; the lanterns did not "glow white". The earlier steps (curves, color offset, lookup at 0, 0.5, 1, lens
  values, fog, camera projection, clear color, depth of field with the Robot as `FocusEntity`, aperture) ran with no failure.
  The play steps ran (`play.start` first built the scripts, "not built yet"), but motion blur streaks, flare and depth of
  field were not looked at.

## WK15
- Entry: `make/quality`; page: same; section: "Before you start".
- Kind: left the book.
- The page needs "the project of Menus and settings screens"; it offers no download. I took Checkpoint 7 of `make/menus`
  (side step), opened it with `project.open` (its project file is named CharactersCameras.stproj) and used its settings screen.
  The commands for AA, the TAA preset, `project.settings`, `project.setSettings {"Preset": "Low"}` (then "High"), the Scene
  view's `quality` and `graphics.resetPlayerOptions` (answer `{"reset": []}`) all worked.

## WK16
- Entry: `make/quality`; section: "Give players a Graphics row".
- Kind: guessed.
- The page shows the excerpt of the sample only; `GetGraphicsPreset` and the fields are not shown, so I wrote them (and
  read lines 114-132 of the sample's `SettingsMenu.cpp` in the pinned source, a side step); the script built with no error.
  `ui.create` of a toggle needed a `parent` that the tab does not name (I used the settings column). The four new toggles came
  with `IsOn` true, no `EventTarget` (the existing window toggles use the panel as target) and the same rect
  (1490, 520, 220 x 40), and the page does not say to set these. The settings panel is hidden at start (`visible: false`),
  so I could not click them in play; after play start `GraphicsHigh` had value 1 (the preset in effect), as the page says.
  The `--quality low` export step was not run.

## Answers

Checks were run with the official 0.8.0 package under the perf lock, in `docs-work/walkfix-G9` (`tools/drive.py`, results
in `results.json`, pictures in `out/`): the page's GI room, Checkpoint 8 of `make/lamps` from its zip, and a copy of the
Third-Person sample. The changed tutorial files (`lamps` and its exercise 2, `look`, `gi` exercise 3, and the new
`quality.tutorial.json`) were run with the pin build and with the package (`docs-work/tutorial-runs/*-walkfix9-*`). The
log lists no patches under "## Built by the integrator". No engine fault was found: every entry is a page or tutorial
fault, so no page gained an `## Engine` note.

### WK1
- Fixed on `make/lamps`. Why: "Download the start checkpoint" named a download that does not exist: the tutorial starts
  from the Basic 3D template, and its first stage builds the yard and ends with the moon and the exposure.
- Change: "What you need" says that no download holds the yard before the first section, that Checkpoint 1 holds it with
  that section's moon and exposure set, and how to build it instead (a Basic 3D project, `project.create` with
  `basic3d`, then Checkpoint 1's commands). Step 1 says that in Checkpoint 1 steps 2 and 3 are already done, and its
  "If you do not see it" names Checkpoint 1.

### WK2
- Fixed on `make/lamps`, `make/reflections`, `make/gi`, `make/look` and `make/quality`. Why: the tabs showed the
  tutorial file's `entityName`, which only the book's runner reads (the reader's copies turn it into `entity.find`).
- Change: every tab passes `"entity": "<the ID of …>"` inside `parameters` (51 tabs), and the first such tab of each
  page says that a command takes an entity's identifier (ID), which `entity.find` returns for the name. On `make/lamps`
  the tabs that name one of four lanterns' entities show `entity.find` with a `box` around the first lantern (stages 5
  and 6 of the file find it the same way); on `make/quality` the placeholder `<post process entity>` is gone.

### WK3
- Fixed on `make/lamps` and its tutorial file. Why: the bulb's `material.set` and `entity.create` and every
  `prefab.apply` were told in a sentence, without their parameters; and `entity.setParent` keeps the world placement
  (`keepWorldTransform` defaults to true), so the step's "Set the Translation of both to 0, 0, 0" had nothing to do.
- Change: the bulb tab holds the three commands; the three `prefab.apply` tabs pass `entity` (the first lantern's
  root); the parenting tab creates `Lantern`, moves `Lamp` and `Bulb` in one `entity.setParent` and renames the lamp.
  The step now says that both keep their place in the world, so each **Translation** reads 0, 0, 0, and the "If you do
  not see it" says to correct the root. Stage 4 of the file checks the zeros with `component.get` instead of setting
  them.

### WK4
- Fixed on `make/lamps`. Why: no command answers the Stats chip's line; a capture's `renderStats` holds its numbers
  (checked: `localShadowLights` 4, `localShadowViewsDrawn` 0 in a still yard).
- Change: the Stats tab adds `viewport.capture` and names `localShadowLights`, `localShadowViewsDrawn` and
  `localShadowViewsPending` in its `renderStats`; the play step's tab adds a scene-camera capture and points to
  `localShadowViewsDrawn`. The step-5 tab also gained the `script.setField` that stops the arm, and the attach tab the
  build, the second `script.add`, the `entity.find` of the arm's light and the `script.setField`.

### WK5
- Fixed on `make/lamps`. Why: the excerpt shows lines 5-28 of `LanternSwitch.cpp`, and the step said to replace the new
  file's whole content with it, which drops the `#include` and the `using` line. (The whole file, 28 lines, exceeds the
  25 lines a fence may hold on track G.)
- Change: the step says to keep the file's first four lines, the `#include` and the `using` line, and to replace the
  rest with the code above.

### WK6
- Fixed on `make/lamps` and `tutorials/make/lamps/exercise-2.tutorial.json`. Why: the exercise starts from the finished
  yard, whose ceiling panel lights the hut as a bright room. Checked on Checkpoint 8 at exposure -2 by hand: with the
  panel active the hut is near white (mean 196, 191, 184); with it inactive it is dark, lit by the doorway lamp and the
  candle (mean 68, 62, 52; `surfaceEv100` median 0.6).
- Change: the worked solution first clears the active box of `Ceiling Panel` (the file starts with `entity.setActive`
  false on it), and the answer says what the **Luminance** view shows then: nearly the whole hut in the lowest band,
  the table near the candle higher.

### WK7
- Fixed on `make/reflections`. Why: the limits tab moved the view without turning it, and "Put the Scene view in the
  doorway, looking in" had no command.
- Change: the courtyard's paragraph gives `camera.set` with `position` 0, 1.5, 2.6 and `target` 0, 0.9, -2 (the result
  figure's view); step 16's tab gives two `camera.set` lines with `target`, the first toward the sphere, the second away
  from it toward the soil bed.

### WK8
- Fixed on `make/reflections`. Why: the answer did not say that the solution's download holds the port as a file that
  no commands file writes.
- Change: the answer says the download holds two commands files and the port `Scripts/DayNight.cpp`, that the commands
  write no file, and to run the first, copy the port over the same file of the project, then run the second.

### WK9
- Fixed on `make/gi`. Why: "Before you start" asked for a new Basic 3D project without saying how.
- Change: the item names **New Project** in the launcher, or `project.create` with `directory`, `name` and the template
  `basic3d`.

### WK10
- Fixed on `make/gi`. Why: the page said the probes inside the floor, the ceiling and the walls are dead; at the pin a
  covered probe moves off its surface or searches its cell for open space
  (`Strata/shaders/GI/ProbeValidity.comp.slang`), so the room's 0.3 m parts leave none dead. Checked: `deadProbes` 0 of
  92,160 in the page's room, 48 with a 2 m solid cube added.
- Change: step 5's "You should see" says no probe is dark red and the legend counts 0 dead, that a probe inside the
  floor, the ceiling or a wall moves into open space, and that only a probe deep in a thick solid, such as a 2 m cube,
  is dead and dark red.

### WK11
- Fixed on `make/gi` and `tutorials/make/gi/exercise-3.tutorial.json`. Why: a face adds only to the voxels not wholly
  behind it (`Strata/shaders/GI/VoxelFinalize.comp.slang`), so a face on a grid line counts only in the voxel in front
  of it: with the inner face at x = 2 every thickness, 0.05 m too, stays one-sided. Checked with Voxels captures: inner
  face at 2, thicknesses 0.25 to 0.05, no two-sided pixels; inner face at 2.02, only 0.05 turns the error color (60,598
  pixels, as the 0.06 m wall of the steps); 0.08, 0.10 and 0.15 do not.
- Change: the exercise sets the five walls with the inner face at x = 2.02, off the grid, then 0.05 with the inner face
  at x = 2; the answer says only the 0.05 m wall at 2.02 turns, why the one at 2 stays gray, and that the view marks only
  walls whose faces share a voxel, so the 20 cm rule stands. The file sets the six walls (centers 2.145 to 2.025).

### WK12
- Fixed on `make/look` and its tutorial folder. Why: a tutorial that starts from a sample publishes no zip, and a stage's
  setup file is no download, so `warm-look.cube` reached no reader; the page also said each checkpoint is a copy of the
  project, which no checkpoint of this page offers.
- Change: "What you need" prints the lookup (`LUT_3D_SIZE 2` and its eight corner colors) to save under that name,
  with a sentence on what it holds; `tutorials/make/look/warm-look.cube` is now the same nine lines. The old 17-point
  table was the same affine map clamped at 1, which the tone pass clamps anyway: scene-camera takes with both differ by
  at most 3 levels, so the published pictures stand. The import tab says Checkpoint 4's commands start with the
  `asset.info` check, so the file is imported first. The sample's copy is named with its command, `project.openSample`
  with `ThirdPerson` and an empty folder as `directory`, and the paragraph on checkpoints says they hold commands only.

### WK13
- Fixed on `make/look`. Why: the Luminance view's bands start at EV100 5, 4 nits (`LuminanceFirstEV100`,
  `Strata/src/Strata/Renderer/SceneRenderer.h:382`), and the sample lights the Course with a sun of 3.26 lux
  (`surfaceEv100` median 1.9 to 2.3), so the whole picture is the lowest band.
- Change: step 1's "You should see" says one flat dark blue, the legend's `EV <6`, why (bands from 4 nits, a sun of
  about 3 lux), and that the meter lifts that dim light to a bright picture. The night's step 3 says the same flat blue
  shows by night, with the capture's median falling from about 2 to about 1 (0.83 measured), and its tab adds the
  capture.

### WK14
- Fixed on `make/look`. Why: after the recipe the editor camera's view of the Course holds no lantern (mean 5, 7, 7, near
  black); the scene camera shows a dark teal course under a black sky; a lantern glows white only where one is in view
  (checked with `camera.focus` on `Lantern A`).
- Change: step 2's "You should see" says a dim blue-green course under a black sky, and that a lantern glows white
  where one is in view: select `Lantern A` and press **F**, or `camera.focus` with its ID. The unchecked motion blur,
  flare and depth of field looks were not walked: no change.

### WK15
- Fixed on `make/quality`. Why: "Before you start" named the Menus project but no download.
- Change: the item says no download starts the page, to open the project of `make/menus`'s Checkpoint 7, and that its
  folder `Menus` holds `CharactersCameras.stproj`, named after the page where the course began.

### WK16
- Fixed on `make/quality`, with a new tutorial file `tutorials/make/quality.tutorial.json` (from `make/menus`) and its
  script `tutorials/make/quality/SettingsMenu.cpp`. Why: the page quoted the sample's handler, whose fields and helper
  the reader's Menus script does not have, and the toggle tab named no parent, no group of their own, no event target
  and no **Is On**.
- Change: step 8 builds a horizontal layout `GraphicsRow` in `SettingsColumn` with four toggles, each with `GraphicsRow`
  as **Group** (the window toggles already use `SettingsPanel`), `SettingsPanel` as **Event Target** and **Is On**
  off, in both tabs. Step 9 has the reader copy the page's `Scripts/SettingsMenu.cpp` (the Menus script plus the four
  fields, the helper and the preset shown at start), quoted in three parts with callouts. Step 10 builds, fills the
  fields, applies the panel to its prefab, saves, plays and clicks `GraphicsLow`; step 11 stops and resets. The
  anti-aliasing choice is a paragraph with its two calls, no longer a step. The file runs all of it and checks that
  `GraphicsHigh` is on at the start, that the click switches `GraphicsLow` on and `GraphicsHigh` off, and that
  `graphics.resetPlayerOptions` answers one choice, then none. The page now offers its download after the Result.

## Steps for a fresh walker

With the official package, from a new session folder:

- `make/lamps`: from Checkpoint 1's project, the steps of "Make the lantern a prefab" (the parenting and the three
  `prefab.apply` tabs), "Give the lanterns shadows" step 4 (the capture's `renderStats`), "Move a lamp and switch it"
  steps 2 to 5 (keep the first four lines of the new file); exercise 2 from Checkpoint 8 with the worked solution.
- Every command tab of the five pages that names an entity: pass the ID that `entity.find` returns.
- `make/reflections`: from its download, the doorway `camera.set`, step 16's two `camera.set` lines; exercise 3's
  solution as its answer says (copy the port between the two commands files).
- `make/gi`: a new project with `project.create` (`basic3d`), the room, step 5 of "Enable global illumination" (0
  dead), exercise 3 from the room (inner face 2.02, then 0.05 at x = 2) in the Voxels view.
- `make/look`: save the printed `warm-look.cube`, copy the sample with `project.openSample`, the Luminance step of "Set
  the exposure", the import and the lookup of "Grade the color", the night's steps 2 and 3 (`camera.focus` on
  `Lantern A`).
- `make/quality`: from `make/menus` Checkpoint 7, steps 8 to 11 (row, script from the page's download, fields, apply,
  click `GraphicsLow`, reset).

## Confirm

Segment 9 confirmation, official 0.8.0 package, one headless editor under one perf-lock hold (it waited behind another
walker once), work folder `walk-G-final-9/c`, everything through StrataCLI, every entity passed by the ID `entity.find`
returned. Note: the served preview was built before the fixes (its `make/lamps` page had no `entity.find`) and was rebuilt
at 17:55 while I walked; I read the fixed pages from the book's sources and took every download from the rebuilt server.

- WK1 holds. "What you need" says no download holds the yard before the first section and names Checkpoint 1; its project
  opened. (The lantern steps need the lamp and the bulb of the next two checkpoints; I ran their commands files.)
- WK2 holds. Every tab of the five pages passes `"entity": "<the ID of ...>"`; the CLI took the IDs with no refusal
  (lamps, reflections, gi, look and quality tabs run).
- WK3 holds. The parenting tab moved `Lamp` and `Bulb` in one call; both read Translation 0, 0, 0. `prefab.apply` with
  `entity` (the first lantern's `Lantern`, found by `box`) answered `updatedInstances 3`; `box` found exactly one
  `Light`, `Lantern` and `Housing`.
- WK4 holds. `viewport.capture` `renderStats` gave `localShadowLights` 4, `localShadowViewsDrawn` 0 when still; in play 8
  while the arm turned, 0 after `Spinner` was set to 0.
- WK5 does NOT hold. "Keep the file's first four lines, the `#include` and the `using` line": the file `script.create`
  makes in 0.8.0 starts with four comment lines, then the `#include` on line 6 and `using` on line 8. Keeping lines 1-4 and
  pasting the code after them fails the build (`C2504: 'Script': base class undefined`, `C3646`), as the first walk did.
  Keeping the `#include` and `using` lines (what the sentence means) builds; `script.add`, `script.setField`, play and
  `input.key L` (Intensity 0, then 64) matched. The page has to say "keep the comment, the `#include` and the `using`
  line", or "everything above `class LanternSwitch`".
- WK6 holds. The worked solution's file now starts with `entity.setActive` false on `Ceiling Panel`; run on Checkpoint 8
  it ran with no failure, and the Luminance capture shows the hut in the lowest band with only the table by the candle
  higher, as the answer says.
- WK7 half holds. The doorway `camera.set` (0, 1.5, 2.6 to 0, 0.9, -2) shows the room from the door, with the sphere at the
  left. Step 16's first line looks at the sphere from low beside it (crescent of sky above the cream floor). The second
  line does not turn the view away: the sphere is at -1.2, 0.5, 0.8, the new target direction from (-2.5, 0.4, 1.5) is
  about 5 degrees from the sphere's, so the sphere stays in the middle of the picture, and the sentence "when the sphere is
  out of the picture, its reflection is gone" cannot be seen. The target has to turn farther (for example toward +x and +z).
- WK8 holds. The answer says the download holds two commands files and `Scripts/DayNight.cpp`, written by no command; stage
  1, copy, stage 2 ran with no failure: Sun Intensity 0.2 at 21:00, the fire 100.
- WK9 holds. `project.create` with `directory`, `name` and `basic3d` made the project at the first try; the room, GI, and the
  views matched.
- WK10 holds with a small remark. The capture and the legend count `deadProbes` 0 of 92,160, as the page says. The spheres in
  the room's air are still dark maroon (a reader looking only at the picture cannot tell them from "dark red"); the count
  is what settles it.
- WK11 holds. Voxels captures, error-color pixels (of 921,600): inner face 2.02 with 0.25, 0.20, 0.15 and 0.10: 0; 0.05: 60,480;
  0.05 with the inner face at x = 2: 0.
- WK12 holds. The nine printed lines saved as `warm-look.cube` imported (type ColorLookup, `Size` 33); `project.openSample`
  with `ThirdPerson` and `directory` made the copy; Checkpoint 4's commands ran with no failure after the import.
- WK13 holds. The Luminance view is one flat dark blue, `surfaceEv100` median 1.7, sun 3.26 lux.
- WK14 holds. After the recipe the picture is a dim blue-green course under a black sky; `camera.focus` with Lantern A's ID in
  `entities` shows the lantern glowing white. The Luminance capture is flat dark blue; the median `surfaceEv100` was 0.40 from
  the focused camera (the page says "about 1"): the number depends on the view, a small difference.
- WK15 holds. The page names Checkpoint 7 of `make/menus` and the project file `CharactersCameras.stproj`; it opened.
- WK16 holds. `ui.create` of `GraphicsRow` and four toggles with the parent, Group and Event Target the tabs give; the page's
  `SettingsMenu.cpp` (the download after the Result) differs from the Menus script by the four fields, the helper and the
  preset code, and built with no error; fields, `prefab.apply`, `scene.save`, play, `input.click` on `GraphicsLow`
  (`GraphicsHigh` on at start; after the click only `GraphicsLow` on), `play.stop`, `graphics.resetPlayerOptions` answered
  `["Preset"]`, then `[]`.

Still open: WK5 and the second `camera.set` of WK7 (mismatches). Not done: clicks and the Inspector, the exported game.

## Answers (after confirm)

Measured with the 0.8.0 package in a headless editor with the GPU (`docs-work/walk-final-fix/drive.py`, `results.json`,
captures in `out/`).

### WK5 make/lamps, Make the script LanternSwitch
- The confirmer is right: `script.create` of `LanternSwitch` writes four comment lines, a blank line, the `#include`
  (line 6), a blank line, `using namespace Strata;` (line 8), a blank line and `class LanternSwitch : public Script`
  (line 10). Kept down to the `using` line and followed by lines 5 to 28 of the page's file, the module built with no
  diagnostic (the build log names `LanternSwitch.cpp`).
- Change: step 2 says to keep the file's comment lines, the `#include` and the `using` line, and to replace the rest,
  from `class LanternSwitch`, with the code above. The page stays within size L (6,498 words).
- `tutorials.py run make/lamps` passed with the pin build and with the package (the page and exercise 2; the tutorial
  file is unchanged). pagecheck PASS.

### WK7 make/reflections, step 16
- The confirmer is right: from (-2.5, 0.4, 1.5) the old target (2, 0.3, -1.5) lies about 5 degrees from the sphere's
  direction. Measured on Checkpoint 1's courtyard with the floor wet (`Roughness` 0.04, `IOR` 1.33) and **Screen Space
  Reflections** on: the first `camera.set` shows the sphere large with its reflection in the floor; the target
  (-3, 0.3, 0), the left wall, about 80 degrees from the sphere, shows the left wall, the back wall and the floor with
  no sphere and no reflection of it, and its capture equals, byte for byte, the same view with the sphere moved away.
- Change: the tab's second line targets (-3, 0.3, 0) and its sentence says "toward the left wall"; "You should see" says
  that turned to the left wall the picture holds no sphere and the floor reflects only the walls.
- `tutorials.py run make/reflections` passed with the pin build and with the package (the page and exercise 1; the
  tutorial file has no stage for step 16 and is unchanged). pagecheck PASS.

## Confirm (after the second answers)

Read as a fresh reader: the pages at book/write, the 0.8.0 package, the pin, under the perf lock; results in `docs-work/walk-final-confirm-2`. Every entry below: through without guessing, leaving the book or a mismatch.

### WK5 make/lamps, step 2
- Holds. From checkpoint 6, `script.create` LanternSwitch wrote a file with comments on lines 1-4, `#include` on 6 and `using` on 8, then `class LanternSwitch` at 10. Keeping those lines and replacing from the class with the page's lines 5-28 built with success and no diagnostics.

### WK7 make/reflections, step 16
- Holds. On checkpoint 1 with Ground Roughness 0.04, IOR 1.33 and SSR on, `camera.set` target (-1.2, 0.3, 0.8) showed the sphere and its reflection (capture differs from the no-sphere one); target (-3, 0.3, 0) showed the left and back walls and the floor only, and its capture is byte-identical to the one with the sphere moved away. The page's text (turned to the left wall, no sphere, no reflection) matches.
