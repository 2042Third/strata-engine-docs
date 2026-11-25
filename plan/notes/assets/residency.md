# Notes: `assets/residency`

## New terms

None proposed. The page defines the thirteen glossary terms it homes in bold: residency, memory pool, budget, eviction, LRU (by "Least recently used"), recency order, device memory budget, request (touch), pin, grace window, trim, room before arrival, reservation.

## Since

`since: 0.3.0`: the inventory dates pools, budgets, LRU, protections, pins and room before arrival to wave 1 (0.3.0), manager extensions and `UpdateMemoryUsage` to wave 3 (0.3.0).

## Requests

- Layout `layouts/streaming-panel.ini` for the figure `streaming-evictions` (the Streaming panel docked and large enough for its table).
- No new words or hosts. The Further reading entries are cited without links.

## Not verified

- The frames in flight the renderer reports (`RendererAssetGraphics::GetFramesInFlight`); the page says 2 as the default used when the device reports none, and a grace window of 4 for it.
- That `editor.showPanel` accepts the panel name `Streaming` (figure recipe).
- The page's 8 GiB, 6 GiB and 4 GiB cards are worked numbers, not measured devices.

## Findings not applied

The brief lists no open findings.

## Clerk

- No term or word asked.
- Left for the planner: `layouts/streaming-panel.ini`.

## Figures

Published 2026-11-23 at the pin v0.8.0 (319075e3): `check` found `editor.screenshot` in the pin, so the `waitsFor` line went, and one take without `--provisional` shows what round 2 showed: GPU textures 32.0 / 32.0 MB (100 %) in yellow, GPU buffers 33.8 / 4712.8 MB (1 %), "Evictions 356 (525 checked)", every texture "this frame", some meshes "393 frames ago" (420 in the provisional take), an empty Pins column. Caption, alt and shows hold unchanged. The page's sentence after the figure (review 2026-11-18 below) now matches the picture.

Settled 2026-11-18 with the provisional build (engine 5b975ad2), the picture checked by eye. The requested `layouts/streaming-panel.ini` was not needed: `layouts/residency-streaming.ini` (1280 by 1040, a copy of `layouts/make-performance-tall.ini` with a 220 px Hierarchy) docks Streaming in 800 by 760 px bottom tabs, narrower than the 60 text heights from which the panel puts its overview beside the table, so it stacks them and the table has every column: Asset, Type, State, GPU MB, Mip, CPU MB, Last used, Pins.

- streaming-evictions (round 1): the 860 px tabs of `make-performance-tall.ini` put the table beside the overview with only four columns, and three camera moves over the Outpost requested the same textures each time: the pool at 32.0 of 32.0 MB, Evictions 0 (85 checked), every row "this frame". Mip streaming kept the pool within the budget by dropping fine levels, and nothing unrequested was left to drop.
- streaming-evictions (round 2): the new layout, and the steps open `Scenes/Loading.stscene`, wait 120 frames, then open `Scenes/Outpost.stscene` again and wait 300 frames, so the first visit's textures go unrequested while the second needs the whole budget. The panel shows GPU textures 32.0 / 32.0 MB (100 %) in yellow, GPU buffers 33.8 / 4712.8 MB, "Evictions 356 (525 checked)", the textures all "this frame" and some meshes "420 frames ago" (the buffer pool is far below its budget, so nothing drops them), and an empty Pins column (the Showcase pins nothing). Caption, alt and shows were rewritten to these; the asset names are cut at the column's width.
- The page's sentence after the figure ("the rows with the oldest requests disappear first") holds per pool only: the picture shows meshes requested 420 frames ago staying, because their pool is under budget. A still picture cannot show rows leaving; "grows" is seen only as a count in the hundreds.
- Review 2026-11-18, words: a viewer found the sentence after the figure (residency.md, the paragraph after `::figure{id="streaming-evictions"}`) false of the picture, which keeps mesh rows "420 frames ago", the oldest shown. The fault stands, but it is in the page's words, which the photographer does not edit; caption, alt and shows already state it truly. Proposed for the writer: "The figure shows the panel with the texture budget set to 32 MB in the Showcase. The texture pool stays at its budget and the eviction count is in the hundreds; every texture left in the table was requested this frame, because the older ones were evicted. Meshes requested hundreds of frames ago stay, because the buffer pool is at 1 % of its budget."
- streaming-evictions (round 3, review 2026-11-18, Asset column): the viewer asked for a wider dock so that the texture rows ("Textures/asphalt_02/asphalt_0" twice, "Textures/dry_ground_01/dry_gr" three times) read apart. Taken with `residency-streaming.ini` widened to 1580 by 1040 and 1100 px bottom tabs: the panel put the overview beside the table (from 60 text heights, `c_SideBySideWidthInFontSizes`, about 840 px), and the table's share left the Asset column a few pixels wide ("Te", "Sc"), worse than before. Stacked, the tabs can grow only to about 850 px, so the Asset column gains about 50 px: "Textures/dry_ground_01/dry_ground_01_" still hides the `arm`, `diff` and `nor_gl` that tell the rows apart. Side by side, every column and the whole names (about 330 px) need tabs of about 1650 px, a picture shrunk to under half at the page's width. Reverted to the 800 px layout of round 2; no command fills the panel's filter. The rows are the three maps of one material (`<material>_arm_2k.jpg`, `_diff_2k.jpg`, `_nor_gl_2k.jpg`); the caption claims nothing of the names.
