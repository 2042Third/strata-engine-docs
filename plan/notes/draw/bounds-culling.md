# Notes: draw/bounds-culling

## New terms

None proposed beyond the seven the brief homes (conservative test, frustum culling, loose grid, positive vertex test, screen fraction, size culling, spatial index), all defined in bold on the page. "Frustum" and "bounding volume" are defined in bold in plain prose as well; if the glossary homes them elsewhere, the planner may drop the bold.

## Requests

- Names: "Gribb" and "Hartmann" (authors of the plane extraction method, named in prose and in Further reading).
- Figures not drawn: the 2D picture of the planes and a box's positive vertex (foundation:425) and the loose grid in two dimensions with a block, the large-object list and a frustum classifying cells (render-scene:397). The page carries the numbers of the first as a sketch with output and the map as a Mermaid diagram; a drawn figure of each would help. No figures file was written.

## Since

0.3.0: the spatial index, frustum culling and the screen fraction exist from the first tag (inventory render-scene:56-60 and :98 give 0.3.0); size culling arrived in 0.4.0 but the page's subject starts at 0.3.0.

## Not verified

- That the texture streamer uses the screen fraction: `TextureStreamer.cpp` has its own computation commented as "like LODSelection::GetScreenFraction"; the page says it works out the same measure.
- `MathTests.cpp` covers the frustum: the file includes `Frustum(` calls; its test cases were not read.
- That `GatherDraws` uses the same chunk pattern (inventory render-scene:79 says so; `ExtractionChunk` seen in the code).
- A timing of brute force against the grid is left to the reader: no timing numbers appear on the page.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Admitted to names.txt: Gribb, Hartmann.
- Frustum and bounding volume are the glossary's (basics/math-projection, basics/math-geometry): the bold may stay or go, the planner's.
