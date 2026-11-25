# Notes: make/characters-cameras

## New terms

- None proposed. The page defines the glossary's own terms in bold: character controller, coyote time, drawn pose, interpolation, step alpha.

## Requests

- The starting checkpoint "Course" is a downloadable project that does not exist yet: the first stage of `tutorials/make/characters-cameras.tutorial.json` builds the course with commands from the Basic 3D template (two steps, two ramps, wall, ledge, crate, kinematic platform, the Gameplay map), so the integrator can export it as the checkpoint.
- Figures: `follow-judder`, `timing-felt`, `camera-arm`, `jump-states`, `walk-vectors` and `respawn-path` are diagram requests (numbers given in the figure file); the scene figures show static arrangements only (no script runs in a recipe).
- The tutorial files need `tutorials/make/characters-cameras/*` (copied per stage) and `exercise-2.tutorial.json`; `make/project-platformer` copies `step7/FollowCamera.cpp` and `step9/MovingPlatform.cpp`.
- Link targets assumed to exist: `gameplay-math.md`, `script-fields.md`, `physics.md`, `../basics/cpp-classes.md`, `cpp-memory.md`, `cpp-modern.md`.

## Since

- since 0.3.0: the character controller and the drawn-pose rule date from 0.3.0 (brief; Strata's own controller on box3d 0.5.0).

## Not verified

- The six script files now compile and run at the pin (tutorial run, below); what they do under the mouse, the coyote window and riding the platform are still not checked by the run.
- The editor's labels `+ ▸ Empty`, `Create Child`, `Add Component ▸ Character Controller` and `Scripts ▸ Build Scripts`, and dragging an entity onto a script field, are taken from earlier pages, not seen at the pin.
- Command shapes: `entity.create` with `parent` as an ID, `script.add` with an entity field given as an ID, `Camera` and `CharacterController` in `components`.
- That the stick on the course reads `Gameplay/Look` as the right stick only; the mouse comes through `GetMouseDelta`.
- That `Input::IsActionPressed` is true for the frame of the press only (used as in `BallControl-4.cpp`).
- That the cursor lock ends with the game (the script also sets the normal mode in `OnDestroy`).
- The delays 33, 17 and 8 ms are 1 over the rate; the manual states 17 ms at 60 steps.

## Findings not applied

- None: the brief lists no open findings. Brief section 8 says the platform is "a kinematic body moved by a script"; the page does so with a transform write in `OnFixedUpdate` (the skill says it takes effect at the next fixed step).
- The brief's "gap" of the course is replaced by the ledge and the ground's edge (the fall for the return).
- The brief's exercise "a coyote time tuned by feel" is a Basic exercise with numbers; the camera-switch by turning the entity off is described, not built.

## Clerk

- No term or word asked.
- Left for the planner: the start checkpoint "Course", the six diagram figures, the tutorial files make/project-platformer copies.

## Figures

- `result`: round 1 stood behind the wall (camera at z 10, wall at z 7) and showed only the wall's back. Round 2 looks down from 8 m above and behind the wall, so the whole course, the player and the top of the wall show; shows and alt rewritten to that view. Published.
- `player-capsule`: round 1 framed it well but small; round 2 narrows the view to 42 degrees. Published.
- `stairs-slopes`: round 1 looked straight down the ramps, which then read as upright panels, and the platform and the player's head cluttered the frame. Round 2 keeps only the two steps and the two ramps and looks from the front and the right, so the step heights and the two angles show in the caption's order, left to right. Published.
  Round 3 (viewer: from 6 m up the ramps read as two leaning rectangles, the 50 degree one not visibly steeper): the
  camera now stands 1.5 m up at (14, 1.5, 6), fov 28, looking at (1.5, 0.9, -3). Everything lies along x, so a pure
  side view would stack the blocks; from this diagonal the ramps rise to the right at about 45 and 60 degrees in the
  picture, the steps stay apart on the left, and the caption's left-to-right order holds. Alt and shows rewritten.
  Published.
- `platform-ride`: round 1 left the platform at its start (x -5) and the player floating 3 m beside it at x -2. Round 2 puts the platform halfway along its 6 m trip (x -2), under the player, and looks from the front and the left. Published.
- `top-camera`: round 1 shows the course from 20 m as asked; alt names the ledge too. Published.
- Retakes went in four short holds of the lock, one figure each (a take empties its work folder).
- 2026-11-23, pin v0.8.0 (319075e3): all five scene figures taken again in one hold; `figures.py compare` found 0 of 5
  pictures differing from the originals taken at 822a7a46, so `publish` kept the files and their stamps (unchanged).
  Looked at again: all five still show their captions. `platform-ride`'s caption said "while it moves", which a still
  picture cannot show; it now says what the picture shows (the player on the platform halfway along its trip, its
  feet on the top of the slab).
- 2026-11-23, viewer's faults. `top-camera`: the caption said "slightly from the front", but the camera (0, 20, 6)
  stands over the start side, where the result's alt says "behind", and the caption did not name the player. Caption
  now: high above the start side, facing along the course, the player the small capsule in the middle (no "20 m":
  the figure lint refuses unrecorded numbers in captions). Words only, picture unchanged, no retake.
  `platform-ride`: the viewer read the slab at x -2 as the platform's start. It is not: the course puts `Platform` at
  (-5, 0.15, -7.5) (stage 1 of `characters-cameras.tutorial.json` and the other four recipes), and this recipe moves
  slab, `Player` and `Body` to x -2, 3 m along +X, where the tutorial run finds the moving platform after 2 s. Caption
  kept.

## Tutorial run

- 2026-11-18, four rounds at the pin's Release build. Round 1: stages 1 to 9 passed as written; stage 10 failed to build:
  `CameraSwitch.cpp` called `SetProperty` (not const) on `const Entity`. The file and the page's excerpt now use plain
  `Entity`.
- The file was thinner than the page: it now checks the controller's fields, the player resting at (0, 0, 2), the
  script fields each step names, walking with W (5 m/s) and S (stops at the Wall at z 6.45), the 1.3 m jump and the
  ground states 0 and 3, climbing Step03 and stopping at Step05, climbing Ramp40, the camera's place behind the player
  and against the Wall, the platform halfway at x -2 after 2 s, the respawn, the loop's jump back and the C switch. The
  exercise checks the double jump (about 2.2 m) and that a third press does nothing.
- Stage order: the drawn-position build (`step5b`) belonged to checkpoint 5 on the page but to stage 6 in the file, and
  the file reset the fixed rate inside stage 5; stage 5 now leaves Fixed Rate at 30 as the page does, and stage 6 ends
  with the page's `reset: true`. The file's `component.set` of the camera to (0, 3, 9), which the page never told, is gone.
- Page mended where it said what the pin does not: W walks away from the Wall, not into it (S reaches it); the follow
  camera starts behind the Wall, which hides the player until it walks; the 50 degree ramp stops the walking player at
  its foot with the state 0, and only a jump onto it shows the slide with the state 1 (seen in steps 38 to 101 of an
  input.sequence).
- 2026-11-24, track G walk segment 8 (WK5): the walker's one `-32602` of checkpoint 9's `script.setField` was not
  reproduced (twelve tries right after `play.stop`, one right after `script.build`, with the 0.8.0 package); the step's
  "If you do not see it" names the remedy. The tutorial file did not change.

## Engine

- None found: the controller stops at a slope above Max Slope Degrees as its description says.
