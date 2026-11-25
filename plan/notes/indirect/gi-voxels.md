# Notes: indirect/gi-voxels

## New terms

- anchor: a voxel index that is a multiple of 1,024 voxels, which the voxelization subtracts from every coordinate so that voxel bits depend on the anchor and never on the camera. Home: indirect/gi-voxels. Aliases: anchor voxel.
- slab: the box of voxels that a scroll brings into a window, which the old window did not hold. Home: indirect/gi-voxels. Aliases: slabs.
- region: a box of at most 64 voxels on a side, cut where texels wrap, that the clipmap queues and the GPU voxelizes together. Home: indirect/gi-voxels. Aliases: regions.
- solid fill: marking every voxel inside a closed mesh as solid by counting winding steps along vertical columns. Home: indirect/gi-voxels. Aliases: winding, winding steps.
- interior class: the class of a voxel inside a closed mesh that no triangle marked: occupancy 1, no color, no normal. Home: indirect/gi-voxels. Aliases: interior voxel.

## Since

0.8.0: global illumination first ships in the release 0.8.0 (`Docs/Releases/0.8.0.md`, "What's new in 0.8.0": "Global illumination (experimental)"); no earlier tag has `VoxelClipmap` or `GlobalIlluminationLayout`.

## Requests

- Names list: the word "Akenine-Moller" (the surname of the author of the triangle-box test), used once in the definition of the triangle-box overlap; the page's one `word-list` finding.
- Figures (all taken at the pin, all with the look-dev project): `cornell-gi-off-on` (a compare of `lookdev.cornell` with the Post Process's `GlobalIllumination` false and true, quality High) and `voxels-view` (`lookdev.sunroom.view.voxels`) are homed on indirect/gi-cascades by the brief; this page defines its own entries so that its figures file is complete, and the planner should keep one entry of each and let the other page use its id. `low-high` is the sweep of the quality row: `lookdev.room` with `GlobalIllumination` true, once with the custom quality field `GlobalIllumination` at Low and once at High (the room's own scene does not ask for GI).
- No editor layout is needed; no tutorial files.
- No external link was added (Further reading cites without links).
- Links to indirect/gi-cascades and indirect/gi-limits point at pages written elsewhere; they must exist before the build.
- The brief's clipmap diagram shows the scroll and the anchor cells; the page draws the nested levels as a Mermaid diagram and teaches the scroll and the anchors with worked examples. A picture of a scroll writing only its slabs, and of the anchor cells, is not drawn.

## Not verified

- That the Mermaid nested-subgraph diagram of the clipmap levels renders as intended (the site build is not run here).
- The cost of a dispatch limit: the page says `c_MaxDispatchGroups` (65,535) is "the limit of one dispatch"; the constant is in `SceneRendererGlobalIllumination.cpp`, the reason (the device's limit on groups of one dimension) was not checked.
- That a 6 cm wall really lands in one voxel depends on its place on the grid; the check question states it as given.
- Which of the far cascades' reads falls in level 1 or coarser was read from `ProbeCascadeLayout::MinimumLevel` (0 for cascades 0 and 1, 1 above); the dark wall below two finest voxels follows the Manual's rule (`Docs/Manual/Lighting.md`, "Walls") and the finalize rules, not a test of a 15 cm wall.
- The sentence about Epic's and NVIDIA's techniques in the alternatives table comes from the cited papers and talks, not from reading their code.

## Findings not applied

- The brief says movers wait 30 frames (item `render-indirect:515`). At the pin (release 0.8.0) a mover leaves the voxels while it moves and stays in a dynamic layer until it has kept its place for 0.25 s (`c_GIMoverRestSeconds`; `Docs/DeveloperGuide.md`, "Moving objects"). The page says only that an object that moves leaves while it moves, and links indirect/gi-limits.
- `new:12` (a stale memory comment of 18 and 111 MiB): at the pin the comment at `Strata/src/Strata/Renderer/RendererQuality.h` already reads 25 MiB at Low and 156 MiB at High, and the totals are 26,091,120 and 163,305,072 bytes (24.9 and 155.7 MiB) because the dynamic layer of moving objects joined them. The brief's 22.6 and 146.4 MiB are out of date; the page uses the pin's.
- `new:13` (directions per cascade): applied. The guide still says 16 to 1,024; the page gives 64, 64, 256 and 1,024 at High and 64, 64 and 256 at Low, from `ComputeLayout` and its test.
- The brief makes the toy version exercise E10 (the CPU test against `Tests::ReferenceVoxels`). The page's toy is a standalone sketch that voxelizes a box and counts 98 voxels; it does not compare with `ReferenceVoxels`, which needs engine types. The hard exercise extends the toy with the solid fill instead.
- The brief's claim "the same scene gives the same bits wherever the camera is" is applied for the camera. The test `20 km out` shows that a scene placed 20 km from the origin differs by at most 1 % of its voxels, from the floats' rounding of its own translation; the page says both.
- The brief's overview figure shows the whole frame; the page draws it and says it covers the first three boxes. Light injection, the cascades and the field are left to indirect/gi-cascades, as the brief's "Leaves out" says.

## Movable claims

- Memory per view that runs GI: 155.7 MiB at High and 24.9 MiB at Low; the voxel levels take 83,886,080 bytes at High.
- The layouts: High has 4 voxel levels of 128 × 64 × 128 from 10 cm and 4 cascades from 0.5 m (64, 64, 256, 1,024 directions); Low has 3 levels of 64 × 32 × 64 from 20 cm and 3 cascades from 1 m (64, 64, 256 directions); High bounces on, Low once.
- The quality row: Off at Low and Medium, High at High and Ultra; GI runs only where a scene asks.
- Budgets: 500,000 triangles a frame and 4,000,000 on a rebuild or a jump; at least one region a frame; regions of at most 64 voxels a side; tiles of 8 × 8 × 8 voxels for triangles whose bounds hold more than 64 voxels; at most 32,768 tiles a batch.
- The scroll step of 4 voxels; the finest level 0.8 m below the camera at High; anchors every 1,024 voxels, moving at 1,000 m beyond the cell.
- Two-sided rules: 0.5 times the count, 0.75 facing, a quarter share; the wall rule of 20 cm at High and 40 cm at Low.
- What enters: the Static arena only; submeshes past the 256th omitted; closed meshes with a glass or cut-out part count as open.
- Known issues of 0.8.0 that touch this page: thin gaps and recesses under about two voxels get darker light (the wall rule); the scratch, the tile limit and the limits of moving objects may change.
- The test `20 km out` allows at most 1 % of voxels to differ.

## Figures

Taken at the pin 319075e3 (release 0.8.0), first takes (nothing was published at 822a7a46).

- `cornell-gi-off-on`: round 1 failed (`/previewLighting` true: the Cornell scene has no directional, point, spot or sky light, so the editor view lit it with its preview sun). Round 2 adds `play: {steps: 2}` (as indirect/problem does), which renders the scene as a game shows it; the off variant then showed a bloom glare over the ceiling at its auto exposure (EV100 -1 against 8.3 with GI). Round 3 adds `Bloom: false`. Published. The caption no longer claims that the floor near each wall is tinted: at this layout the floor stays nearly neutral and only the sphere's side toward the green wall takes a faint green; it says the off picture is brightened about nine stops by automatic exposure.
- `voxels-view`: round 1 (shot `lookdev.sunroom.view.voxels`, automatic exposure) was nearly all white. Round 2 uses the manual exposure -11.5 of indirect/gi-cascades' `gi-views` and a closer camera at the window and the sun's patch. Published. The view shades each surface by the light its voxels store (not by albedo), so flat walls look smooth; cubes show as steps where light or geometry changes (the patch's edges). The window shows the ground outside and the view's background color, not an empty opening. Caption and alt rewritten to that.
- `low-high`: published from round 1. High's walls are brighter, warmer and even; Low's are darker, bluer, with uneven patches on the right wall. No stepped edges were visible at Low, so the caption no longer says "cleaner edges".
- Page words: the paragraph before `voxels-view` says "each cube is one voxel of the finest level that holds a surface"; in the picture cubes are visible only as steps at the edges of light, so a sentence saying that the view shades surfaces by their stored light would fit it better.

Mended after a viewer's report (2026-11-23):

- `voxels-view`: no retake. `VoxelView.frag` blends occupancy trilinearly, so the pin's view cannot draw cubes; the caption and alt now say that the view smooths surfaces between voxels and shows the grid only where light changes (the sun patch's steps). The page's sentence "each cube is one voxel of the finest level that holds a surface" is still untrue of the picture: it should say that the view draws the voxel surfaces smoothed between voxels and shaded by their stored light, the grid showing only where light changes.
- `low-high`: round 2 sets one manual exposure (AutoExposure false, Exposure -11.3; round 1 ran each at its automatic exposure, EV100 10.1 at Low and 11.5 at High, hiding High's gain) and hides `Room Ball` (its upper half had a dark navy cap at Low the caption could not explain). Measured: ceiling 77 against 139, right wall 49 against 126 (8-bit means). Caption and alt rewritten to it.
- `cornell-gi-off-on`: no retake; caption and alt now name the square-edged dark patches on the floor beside the sphere and at the box's foot as the voxel grid in the bounce light.
