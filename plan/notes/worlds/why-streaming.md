# Notes: worlds/why-streaming

## New terms

None beyond the brief's four (world, persistent scene, cell, HLOD), each defined in bold on the page.

## Since

since: 0.4.0. Evidence: Docs/Releases/0.4.0.md line 30 and 126 (a world is a persistent scene plus a World asset of layers cut into cells).

## Requests

- Figure `cell-map-island` (editor, project OpenWorld, layout layouts/why-streaming.ini): the Streaming panel's cell map around the player; taken at v0.8.0 (see ## Figures).
- Host request: docs.unrealengine.com (Unreal Engine documentation on World Partition and Level Streaming), cited without a link. The Unity link (docs.unity3d.com) is on the list.
- The chart `spacing-chart` is an SVG made from computed data (src/assets/figures/worlds/why-streaming/spacing-chart.svg), with a diagram entry in the figures file.

## Not verified

- The suite name `World.Coordinates` is in StrataTests/src/World/WorldCoordinatesTests.cpp and EditorWorldTests.cpp at the pin, but `names` reads it as a component property (World.Coordinates); left as the brief names it.
- Fog that thickens before the streaming distance as a way to hide the edge: general advice, not checked as a Strata setting.
- Unity's additive scene loading and Unreal's volumes and World Partition are described from general knowledge; sources listed in Further reading, not fetched.
- The 2 microseconds per entity is an assumption stated as such on the page.
- ClosureBytes sums count shared assets once per cell, so 45.8 MB is an upper bound (stated on the page).

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Nothing to admit.
- Hosts: none admitted; the sources are cited without links, so no host is needed (docs.unrealengine.com is not on the list and is the planner's).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `cell-map-island` (pin 319075e3, v0.8.0), published after two rounds. Round 1: the Streaming tab was shown before play started, so the map kept the view it framed at the first frames of play; the player marker sat low and the loaded squares ran past the map's bottom edge. Round 2: the recipe shows the Inspector tab first and brings the Streaming tab to the front only after play has stepped 120 fixed steps, so the map frames the player on its first draw: the marker is centered, 43 orange loaded squares surround it inside a blue circle, and 54 dark unloaded squares fill the rest. The alt text now names the colors and the circle.
- `cell-map-island`, round 3 (a viewer's report: the map cut the island's top row and the blue circle, and the status line ran off the panel). The map is never taller than 18 font sizes (252 px, `CellMap::c_HeightInFontSizes`) and frames the circle by the mean of its sides (`CellMap::FrameSources`), so a taller dock changes nothing and a wide map always cuts the circle. The layout now docks the Streaming panel 282 px wide (map about square), the window is 960 × 526 so the panel ends under the legend, and the unused Asset tab is closed so the tab titles read whole. During the tour the player sits near the island's edge, where no map size frames the whole island, so the recipe puts the player at the island's middle (0, 140, 0), flying, with `TourOnStart` off. The picture shows the whole 10 × 10 island, the whole circle, 53 loaded squares around the marker and 44 unloaded ones. The status line is still cut after "0 streaming": it is one unwrapped run of about 470 px, and a panel that wide cannot frame the whole island; only a crop below that line (a page change) would remove it.
