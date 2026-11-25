# Notes: draw/occlusion

## New terms

None proposed. The page defines the five glossary terms of its brief: occlusion culling, hierarchical Z-buffer (HZB, depth pyramid), two-phase occlusion culling, min/max sampler, visibility parity.

## Since

0.4.0: two-phase view occlusion (Releases/0.4.0.md, per inventory render-scene:138); the wave 8 fix of the minimum sampler's coordinates. The `since` key may not be allowed on a `draw` page: drop it if the planner says so.

## Requests

- Names for tools/data/names.txt: Haar, Aaltonen, Nanite, Frostbite (word-list findings left on purpose).
- Figures: none requested. The three pictures of the brief are Mermaid diagrams (the frame sequence, the two-frames comparison) and a table of the wall scene's frames; a recorded capture of a wall in front of many boxes with the two counters is not requested because no recipe was verified.

## Not verified

- That phase 1 draws nothing of a disabled wall (table row 4): the test shows only that the box is drawn in that frame.
- That a renderer switched to another render scene clears the bits: taken from the comment in `RunGPUCulling`, the code path that sets `m_ResetVisibility` for it was not read.
- The statements about other engines (hardware queries, Frostbite's software occluders, Nanite, Haar and Aaltonen) rest on the cited talks and were not checked.
- That feedback arrives two to three frames late: taken from the engine's guide, not measured.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Admitted to names.txt: Haar, Aaltonen, Nanite, Frostbite.
