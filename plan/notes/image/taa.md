# Notes: image/taa

## New terms

- ping-pong: two textures that swap roles each frame, the resolve reading one and writing the other. Home: image/taa. Aliases: ping-pong history.

## Requests

- Hosts for Further reading (cited without links): the SIGGRAPH 2014 and GDC 2016 talks (Karis, Salvi, Pedersen); ask for the hosts of their slides.
- Figures (sample projects and look-dev shots are guesses, to confirm): taa-presets-slow-pan (variants original, sharp, custom), taa-trail-clamp-variance (range, variance), taa-disocclusion-ghost (off, on), taa-transparent-weight (zero, half). Placed with ::compare. No layout needed. The Post Process inspector capture (editor-ui:560) is homed on editor-ui/inspectors and not placed here; TAA off and on (render-image:506) is on image/spatial-aa.
- Diagrams: five Mermaid diagrams (map, history's life, nine reads, variance clip, disocclusion test). The brief's Catmull-Rom weight-merging and overview-with-8-Halton-points diagrams are simplified into the nine-read and map diagrams.

## Not verified

- The statements on other engines in the problem section and table (published clamp and clip designs, a talk on a puzzle game that tests depth, Unreal's temporal super resolution, vendors' libraries) are from memory and cited only in Further reading.
- That the sample projects named in the figure recipes show the scenes described.
- The Manual's numbers (about half and three quarters detail; about 17 frames) are quoted, not re-measured.

## Findings not applied

- None open: new:8 (field name `Sharpening` of `RenderData::TonemapConstants`) is applied; new:30 limits are applied; the decision's aside states the Checkerboard exception and the local-shadow filter as it holds at the pin.
- render-image:599 and 623 exercises: the tuning exercise is exercise 1; the clamp-off and variance-clip exercise is exercise 3 (a sketch solution); new:22 is exercise 2.

## Since

- 0.6.0: Docs/Releases/0.6.0.md lists TAA among what 0.6.0 added.

## Figures

State at the final pin v0.8.0 (319075e3), 2026-11-24, after the `live` kind was taken (three takes per variant,
agreeing in fixed steps and camera; the original is take 1's last frame).

- Round 0 (2026-11-17): the recipes were kind `scene`, whose still captures settle and can show no motion; they became
  kind `live` (auto exposure frozen, motion blur off, TAA on, preset Custom where one tunable is compared).
- Round 1, all four in one hold (work folder `docs-work/photo/last-image-taa`):
  - taa-presets-slow-pan (ThirdPerson, `Gameplay/Look` held at 0.0375): the sample starts on its main menu, so the
    view did not turn and the crop showed a flat, untextured green slope behind the menu. Not usable.
  - taa-trail-clamp-variance (Showcase, shot 4, step 600): MinMax and Variance differ in 164,153 pixels by at most 67
    levels, but only in the apron's fine noise and a halo around the sun; enlarged, neither the glint crop nor the
    puddle, the pillars against the glare or the bus show a faint copy that one keeps and the other removes.
  - taa-disocclusion-ghost (PhysicsPlayground, TowerTop dropped in front of Wall North): the crate falls about 25 px a
    frame at step 30, but rejection off and on differ in 169 pixels by at most 5 levels: the range clamp already
    removes the crate's old colour, since brown wood, pale bricks and blue sky differ.
  - taa-transparent-weight (the eight Ghost boxes falling, camera at 10, 3, -3.5): Transparent Weight 0 and 0.5
    differ only in a line of pixels along the box edges (amplified difference map), no visible drag: the plain pale
    boxes fall outside the colours of the bricks and the sky around them, so the clamp removes the drag.
- Decisions:
  - taa-presets-slow-pan: retaken on the Showcase's fourth flight (step 600), Original against Sharp (TAA on), cropped
    to the apron's grain near the camera. Round 2 showed the difference clearly (Original soft, Sharp crisp, 612,055
    pixels differ); its crop held the Showcase's subtitle, so round 3 moved the crop to [0.2, 0.7, 0.44, 0.88]. The
    page's lead-in now says that the figure is a moment of the flight, not the Manual's slow pan; the caption names
    both causes the presets differ in (Resample Weight 0 and 0.25, Sharpening 0 and 0.5). Round 4 (a viewer's report:
    that crop's left half was almost black shadow, so the two crops looked alike at page size) moved it right onto the
    lit grain, [0.32, 0.7, 0.56, 0.88], still above the subtitle; the alt now names the golden, sunlit right side.
  - taa-trail-clamp-variance: `blocked` (reason in the manifest), stand-in the drawing taa-clamp-clip-axis, the page's
    worked example on one brightness axis (range 0.1 to 1.0 keeps a history of 1.0; the box ends at 0.554, the
    range's 0.1 below, as TAA.comp.slang lines 111 and 112 limit it). Placed after the worked example, whose last
    sentence introduces it. Request for a later edition: a scene with a dark edge sliding past bright glints over a
    plain dark ground, or a capture of the history before and after the clamp.
  - taa-transparent-weight and taa-disocclusion-ghost: `blocked`, `noStandIn`, and their `::compare` lines removed:
    the paragraphs state the rules in full (the disocclusion test also has its code, numbers and flowchart), and a
    picture of the pin shows nothing to remove. Request for a later edition: a textured blended surface moving over a
    still background (for the drag), and a dark object leaving a wall of the same material (for the ghost).

## Clerk

- Admitted the term ping-pong, homed here.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
