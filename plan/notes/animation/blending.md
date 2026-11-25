# Notes: animation/blending

## New terms

None proposed. The page defines the five glossary terms of its brief (cross-fade, blend weight, inertialization, sync markers, hemisphere).

## Since

0.3.0: `Strata/src/Strata/Animation/AnimatorInstance.cpp` first appears in the tag v0.3.0.

## Requests

- Figure `halfway`: taken at the pin (see ## Figures); no request is left.
- Diagram 7 of the brief (stacked weights over time for three interrupting fades) is not drawn; the page shows the same numbers as a table. An SVG with a `diagram` entry would add it.
- Host request: a link for the Further reading entries is not needed (cited without links).

## Figures

- `halfway` (kind `live`, taken at v0.8.0 319075e3). The old recipe (kind `scene`, shot `tp.live.fast`, `waitsFor` tier 3) needed no engine addition: a live capture with input reaches the fade. Round 1 failed: `script.setField` needs a loaded module, so the setup now starts with `script.build`. Round 2: `Scenes/Course.stscene`, the follow camera's `Distance` 3 and `Pitch` -8, `Gameplay/Move` held to the right from step 1, `Gameplay/Run` held from step 40, captured at fixed step 47 (three takes agree). The picture shows the robot from behind, running to the right in mid stride, with the HUD. The exact weight is not read back: the Walk to Run transition (0.2 s, 12 steps) starts one or two steps after the press, so the progress is 0.42 to 0.58, and the caption says "about halfway". A later edition could read the animator's weights in the capture's result and record them.
- `halfway`, mended after a viewer's report: the single frame from behind (robot hiding its legs, a mix claim with nothing to compare) became a `::compare` of two variants from one follow camera (Yaw -120, Distance 4.6, PivotHeight 1.0, Pitch -6, field of view 40 degrees, Move held at (-0.866, -0.5) so the robot heads along -Z seen from its side, 960 by 720): `walk` at fixed step 39, before Run, and `halfway` at step 47. Round 1 (Distance 3.5, PivotHeight 0.8) was too close; round 2 (Distance 7) too far; round 3 is published. The walk side shows arms low and both feet down; the halfway side arms swung wide and its shadow apart from its feet. A third frame of the full run was not added: the page stands at 3,998 of 4,000 prose words (size M), and a slider shows two sides. The caption now ties the frame to the phase paragraph it follows: the run starts at its first frame, so the pose mixes unrelated moments of two cycles.


- Which engines use which technique (the Alternatives table's "Who uses it" column is general; only inertialization cites a talk, by title).
- The 27 % phase difference of the robot's walk and run is quoted from `Docs/Roadmap.md`, not measured.
- The 1 second cycle in the phase example is an assumption, said so in the text.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
