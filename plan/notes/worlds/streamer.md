# Notes: worlds/streamer

## New terms

None. The page defines streaming source, streaming distance, wanted cell, view bias and adoption, all homed here by the glossary.
It gives hysteresis, total order, load radius and keep radius in plain words and links the gamepads page for the first.

## Requests

- Figure `island-cells` (kind editor, project OpenWorld, `waitsFor` tier 2: editor screenshot) needs an editor window layout named `layouts/streaming.ini`: the Streaming panel with its cell map, played in the Open World sample while the player moves, so that cells ahead are loading.
- The three Mermaid diagrams (map, update flowchart, cell states) need rendering by the site build.
- Link targets not yet written when this page was made: `worlds/grids`, `worlds/why-streaming`, `worlds/physics-scripts`.
- Sidebar: `worlds/streamer` after `worlds/grids`.

## Not verified

- The Open World sample's streaming source radius (the page says only that layers use their streaming distance when a source's radius is 0; the layer distances 192, 128 and 320 m and 64 m cells come from the sample's README).
- Claims about World Partition (Further reading only, cited without a link); no claim about other engines is made beyond it.
- Whether the sort rule's use of `std::sort` can reorder equal keys: the page only says the order is total, so none tie.

## Since

`0.4.0`: `git tag --contains 554aed00` (the commit "Stream a world's cells around sources with WorldStreamer") lists `v0.4.0` as the first tag.

## Findings not applied

- Brief item `worlds-runtime:191`: the inventory's "World.Streamer" suite does not exist; the page uses `World.Streaming` (named in the command and as "the streaming suite" because the names check reads `World.Streaming` in prose as a component property).
- The brief's exercises 2 (statistic), 3 (property) and 4 (cone of priority) are not on the page; it holds the keep-radius experiment (done, as a sketch), a candidate-merge exercise and the trace-it-yourself exercise. The page is at the top of its size.
- The `Elsewhere` and `History` asides are omitted for size.

## Clerk

- Nothing to admit.
- The sidebar's order is generated from the outline (clerk-wave2/sidebar.py) and was run for this batch.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

island-cells published 2026-11-24 at the pin v0.8.0 (319075e3): `waitsFor` removed as `check` asked, one take without
`--provisional`, the recipe unchanged. The picture: the white dot and its direction line near the map's center inside
the blue circle, 45 loaded cells in orange around it, 52 unloaded, the legend Wanted 0, Loading 0, Unloading 0,
Failed 0. Caption, alt and shows hold.

island-cells settled 2026-11-18 with the provisional build (engine 5b975ad2831e, `--provisional`), three rounds in three
holds; nothing published, the recipe keeps `waitsFor`. New layout `layouts/streaming.ini` (960 × 540): a copy of
`layouts/world-editing.ini` as it stood then (300 px Hierarchy, 520 px right column holding Streaming), so that the cell
map is wide and its top line fits; the recipe pictures the Streaming panel at its own pixels (520 × 462).

- Round 1 (kept): Open World opens `Worlds/Island`; `play.start` (builds the scripts, about 9 s; the game starts its
  tour), 240 frames, selection cleared. The map: the player's white dot with its direction line, 45 loaded cells in
  orange around it inside the blue circle, 52 unloaded in dark gray, and the legend Wanted 0, Loading 0, Unloading 0,
  Failed 0. The play.start to screenshot interval was about 3 s.
- Round 2: the same with `script.setField` Explorer `TourSeconds` 8 on the Player (three times the tour's speed, about
  165 m/s), 180 frames: still 0 loading and 0 wanted, 41 loaded.
- Round 3: `TourSeconds` 3 (about 430 m/s), 60 frames: still 0 loading, and the player had flown off the top of the
  map, which does not scroll with it. Recipe returned to round 1.
- Mend (2026-11-18, one hold): a viewer saw round 3's picture (the work folder kept it): no player dot, the circle's
  center above the map, the top row cut, and three orange cells outside the circle. The cell map frames the sources
  once, on its first draw after play starts (`CellMap::FrameSources`), and does not follow them. The layout already
  keeps Inspector in front (node `0x4` `Selected=0x36DC96AB`, Inspector's tab id), so the map first drew at the
  recipe's `editor.showPanel`, 120 frames before the screenshot, while the fast tour flew on. The recipe now ends with
  `selection.set`: the map first draws at the panel `take` shows just before the screenshot. The new take, at the
  tour's own speed: the white dot and its direction line near the map's center, the whole circle's width, every row,
  45 loaded cells, all inside the circle, 52 unloaded, 0 loading. Caption, alt and shows hold as they are.

What commands cannot show: the writer's caption, cells ahead of the player loading while those behind are kept. A cell
of the island loads within a few frames (at most 4 at once), and `take` waits 120 frames after the last step before the
screenshot, so a loading cell is gone before the picture even at many times the tour's speed. Caption, alt and shows
now describe the loaded cells around the player and the legend with zero loading. To show cells loading ahead, the
page would need a diagram of the ring with a loading front (the states diagram already names the states), or an engine
command that captures the panel at a given frame (no settle wait) during play.

Mend (2026-11-24, words only, no retake): a viewer saw that the legend (Loaded 45, Unloaded 52) does not match the
squares (35 orange, 26 gray), that the island's northern rows and the circle's top and bottom are cut off, and that the
caption never said what the circle is. All stand. `Worlds/Island.stworld` has three layers of 64 m cells on one grid
(Vegetation 192 m, 81 cells; Wildlife 128 m, 10; Landmarks 320 m, 6): 97 cells on 81 squares, so All overlays them
and the legend counts 97. Measured on the take: cell pitch 29.5 px, circle 296 px across (321 m radius, Landmarks'
320 m), map 250 px tall, 7 of Vegetation's 10 rows shown, the 3 missing above. The map is at most 18 font sizes tall
(`CellMap::c_HeightInFontSizes`) and frames by the mean of its sides (`CellMap::FrameSources`, 2.4 diameters), so
the 490 px wide map cuts the circle; only a column under about 360 px would fit it, which would cut the panel's top
line, and a new layout is outside this page's files. Caption, alt and shows now say what the circle is, that Vegetation
stays loaded within its 224 m keep radius, that the legend counts three layers sharing squares, and that the northern
rows lie above the map; `numbers` gives the sources. The page sits at its 6,500-word size limit, so caption and alt were
shortened to fit (6,500 words).
