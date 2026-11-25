# Notes: editor/worlds

## New terms

None. The page defines dirty cell, edit layer, re-celling, cell map and cell bounds, all homed here by the glossary. It uses adoption (homed on worlds/streamer) in plain words.

## Requests

- Figures `world-strip` and `cell-map` (kind editor, project OpenWorld, `waitsFor` tier 2: editor screenshot) need the layout `layouts/world-editing.ini`: the Hierarchy with the world strip, the Streaming panel with its cell map, one Landmarks cell edited and unsaved, the editor camera in the middle of the loaded cells. Steps are empty and need the integrator's setup (open `Worlds/Island`, `world.edit` with the Landmarks layer, move one entity).
- The two Mermaid diagrams (the map, the save sequence) need rendering by the site build.
- Sidebar: `editor/worlds` after `editor/recovery`.

## Not verified

- The values the examples say `world.status` reads (`cells.dirty` 0, 2, 0; `editLayer`; the Inspector line) and the files the saves write follow from the code of `EditorWorld` and `EditorWorldCommands.cpp` and from the test "A move across a cell border is one undo step", but the examples were not run.
- `Camp2 Logs` stands at (67, 19.37, 188) in the Landmarks cell (1, 2) of the OpenWorld sample (read from `Samples/OpenWorld/Assets/Worlds/Island/Landmarks/1_2.stscene`); the layer has no file for the cell (0, 2).
- The 50 ms for writing one cell file is an assumption of the page's arithmetic, stated as such.
- The Prefab section is read from `PrefabSync.cpp` only (`CaughtUp`, once per prefab and scene). Whether an export packs the old cell files was not checked, so the page does not say it.
- Claims about other engines: the table's "who uses it" column (external actors, one file per actor) rests on Further reading entries that were not read; the Epic and Gregory entries are cited without links.
- That the second save request's failure leaves the scene modified is read from `OnWorldIndexSaved` and `MarkWorldSaved` in `EditorContext.cpp`, not run.

## Since

`0.4.0`: `git tag --contains c38f558e` (the commit "Stream an open world's cells around the editor camera", which added `EditorWorld.cpp`) lists `v0.4.0` as the first tag.

## Findings not applied

- Brief figures: the page has two editor figures (the Hierarchy strip, the cell map) and two Mermaid diagrams (the map and the save sequence), not the brief's eleven (eight screenshots), because the size is at the middle of L. The play-from-editor figure (`worlds-runtime:369`), the cell map's menu, the Inspector's cell line, the search, an unsaved cell and the Asset panel are described in words.
- The brief's History, Elsewhere and a "What went wrong before" section are omitted: no bug with a regression test belongs to this part, and size.
- The brief's open item `new:58` (PrefabSync) is stated as read in the code, in about 110 words, not run.

## Clerk

- Nothing to admit.
- The sidebar's order is generated from the outline (clerk-wave2/sidebar.py) and was run for this batch.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Editor figures settled 2026-11-18 with the provisional build (engine 5b975ad2831e, `--provisional`), one round, one
hold; nothing published, both recipes keep `waitsFor`. New layout `layouts/world-editing.ini` (960 × 540, from
`make-large-worlds-wide.ini`: a 300 px Hierarchy so the strip reads whole, a 380 px right column holding Streaming so
the map is wide).

- Steps for both (the state of the example "A crate across a border"): the Open World sample opens `Worlds/Island`
  (its start scene); `world.loadCells` Landmarks (1, 2) with `wait`; `entity.find Camp2 Logs`; `component.set`
  Transform Translation [60, 19.372288, 188]; `world.edit` edit layer Landmarks; editor camera at (60, 60, 250)
  looking at (60, 19, 188), fov 50; selection cleared; 120 frames.
- world-strip: the Hierarchy at its own pixels. Reads "Island 32 cells loaded · 2 unsaved", the map button and
  "Edit layer: Landmarks"; the entity list fills the rest. The caption names the counts without numbers (pagecheck).
- cell-map: the Streaming panel at its own pixels. Orange loaded cells, the cell (1, 2) with a thin yellow outline
  (the dirty outline, `colors.Warning`) and its pin glyph, the camera as a white dot with a direction line, the blue
  radius circle, the legend 65 unloaded and 32 loaded.

Found while taking (the page's words are not changed here):

- The strip counts 2 cells not saved, but the map outlines only (1, 2): the new cell (0, 2), made in memory, is not in
  the streamer's cell states yet, so the map does not draw it. The page's "outlines for cells that changed since the
  save" holds only for cells the world already lists.
- The strip shows the loading count only when it is not 0.

Mended 2026-11-18 after a viewer's report (provisional build 5b975ad2831e, `--provisional`, one hold, both figures;
nothing published, `waitsFor` kept):

- world-strip, caption: it came before the example that introduces Camp2 Logs, so "the logs" named nothing. Caption
  now: "after the example below moves Camp2 Logs from the Landmarks cell (1, 2) into (0, 2)"; a `numbers` line says
  where the cells come from. Picture unchanged (the Hierarchy keeps its 300 px).
- cell-map, caption: the strip says 2 unsaved but the map outlines one cell. Caption now says the cell the logs left
  has the yellow outline and the pin, and the cell they joined, (0, 2), has no file yet, so the map gives it no
  outline (the orange square left of the pin is loaded but not outlined: enlarged and checked). Same wording as
  world-strip for the move.
- cell-map, top line: it was cut at "0 pinnec" and its asset counts read as cell counts. `layouts/world-editing.ini`
  (used only by this page) now gives the right column 520 px (viewport and bottom dock 136 px): the line reads whole,
  "391 registered · 251 ready · 0 streaming · 0 failed · 0 pinned · frame 250", and the caption and alt say it counts
  assets, not cells. Cropping to the World header was not possible: a crop shows only where the page's `::figure`
  names it, and the page's words are not changed here.
- Seen in the new take: the map frames the streaming circle by the geometric mean of its sides (`CellMap::FrameSources`),
  so the wider map draws cells about 20 % larger and its top row of cells and the circle's top and bottom run past the
  map's edges. The engine does this on purpose for wide maps; the alt says so.

Published 2026-11-23 at the pin v0.8.0 (319075e3), without `--provisional`, one round, one hold; `waitsFor` removed
from both recipes as `check` asked. Recipes unchanged.

- world-strip: reads "Island 32 cells loaded · 2 unsaved" (yellow), the map button, "Edit layer Landmarks", then the
  entity list. Matches caption and alt.
- cell-map: top line "391 registered · 251 ready · 0 streaming · 0 failed · 0 pinned · frame 250", read whole; the
  cell (1, 2) with a thin yellow outline and the pin (enlarged), (0, 2) orange without outline, the camera's white dot
  and line, the blue circle running past the map's top and bottom, legend 65 unloaded and 32 loaded. Matches caption
  and alt.

Mended 2026-11-23 after a viewer's report (pin v0.8.0, 319075e3, one hold, cell-map only):

- cell-map, unreadable: the pinned cell's outline is 2 px of pale yellow (233, 195, 77) on orange (224, 138, 46), the
  dirty outline the editor draws at UI scale 1; the pin build draws it no thicker. The recipe now cuts the crop
  `pinned` (rect [0.365, 0.216, 0.692, 0.541] of the 520 × 462 panel: the pinned cell, (0, 2) left of it and the
  camera dot), shown up to 4 times, and it is published as `cell-map-pinned.webp`. The page shows it only when a
  `::figure{id=cell-map crop}` follows `::figure{id=cell-map}` (the page's words are not changed here: that line is
  the writer's to add).
- cell-map, unclear: the caption now says that (0, 2) is directly left of the pinned cell and that the white dot is the
  editor camera; alt and shows say the square left of the pinned one has no outline. Checked on the map: x grows to
  the right and z downwards (the camera at x = 60, z = 250 sits just left of and below (1, 2), its line pointing up to
  its target at z = 188).
