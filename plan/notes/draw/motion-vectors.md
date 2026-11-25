# Notes: draw/motion-vectors

## New terms

None proposed; the page defines motion vector (velocity target), motion history and write version (write log) from the brief.

## Since

since 0.6.0: Releases/0.6.0.md:37-44 lists motion vectors (from inventory render-scene:173-175).

## Requests

- Further reading cites Karis (SIGGRAPH 2014) and Real-Time Rendering without links; no host requested.

## Not verified

- Releases/0.6.0.md line range for the since evidence was taken from the inventory, not opened.
- The Further reading sources are cited from memory, not checked.
- The editor label **Motion** was read in StrataEditor/src/Panels/ViewportPanel.cpp, not seen in the running editor (the figure sets the view by command).

## Findings not applied

The brief lists no open findings. Items left out on purpose: the pipeline key's velocity flag (gpu/binding), the transparent pass's velocity, GPU-driven path comparisons, cross-fade details beyond one test bullet.

## Figures

- `motion-view`, published (live, 2 rounds, takes in one hold each). Earlier: a still `scene` capture could show no
  motion (a still capture renders a paused scene), so the recipe became a `live` figure, which the take tool now runs.
  - Round 1 (Move [1, 0] with Run, image at fixed step 45): the world was one blue-green (moving left), but the robot was
    hidden behind the Pine (Decoration, world about 4.8, 0, 4.2), which stands between the follow camera and the robot
    once the robot reaches x about 4.5 (it starts at 0, 0.02, 3; the camera keeps yaw 0 and follows from +Z).
  - Round 2 (same input, play 40 steps, image at fixed step 30, HUD time 0:00.5): the robot runs right of center, left
    of the Pine. Seen: ground, trees and fence share one blue-green, brighter near the camera; the sky stays dark (a
    sideways move does not shift it); the robot's body is olive green, one arm bright green, a foot orange. Three takes
    agreed. Caption, alt and shows rewritten to what is seen.
- The page's sentence after the figure now says "run the robot sideways or pan the camera while it runs", since the
  picture shows the camera following a sideways run (the follow camera turns only with the mouse or the Look action).
- Checked by eye: the Game view draws the viewport's motion debug view during play (`ViewportRenderer.cpp:437` sets
  `ShowMotionVectors` from the viewport's debug view). Colors follow `Strata/shaders/Overlay/MotionView.frag.slang`
  (left is cyan, the page's blue-green).

## Clerk

- Nothing to admit.
