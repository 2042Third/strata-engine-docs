# Notes: `basics/math-matrices`

## New terms

- **affine transform**: a 3×3 change followed by a move; its 4×4 matrix has the bottom row 0, 0, 0, 1. Home:
  `basics/math-matrices`. Aliases: affine transformation.

The page also defines, in bold, the glossary terms the brief lists for this page: axis, basis vector, coordinate
space, handedness, identity matrix, inverse matrix, local space, local transform, matrix, matrix multiplication, matrix
order, rotation, scale, transform, transform hierarchy, translation, TRS, up axis, world space and world transform.

## Requests

- `tools/external-hosts.txt`: `www.3blue1brown.com` (the series "Essence of linear algebra") and `learnopengl.com`
  (the chapter "Transformations"); `## Further reading` cites both without a link until the hosts exist.
- Figures: four diagram requests in `src/content/figures/basics/math-matrices.json` (`axes-moved`, `turn-then-move`,
  `parent-and-child`, `right-hand-axes`). None is drawn yet.

## Not verified

- The Coin Run item (Practice 5) was not run: that the **Console** prints about (0, 1, -3), that a `Spinner` with
  `DegreesPerSecond` 0 leaves the rotation as set in the Inspector, and that `GetWorldPosition` is current in the same
  call as `SetParent` and `SetTranslation`. `make/project-coin-run` is not written, so the item names no coin of that
  project and makes its own `Ring`.
- That `Log::Info` rejects a matrix: read from `StrataScriptCore/Include/StrataScript/Log.h` (it formats numbers, text,
  float vectors, quaternions, entities and asset handles, and the SDK includes no `glm/gtx/io.hpp`), not compiled.
- That a glTF model faces +Z and that `Math.h`'s "(glTF)" names glTF's axes: the page cites Strata's own
  `.claude/skills/strata-make-a-game/SKILL.md` and the comment; the glTF specification was not read. The gain named in the
  `:::why` aside (the file's axes already match) is the book's reading of that comment.
- The `:::why` aside on TRS fields (one field changes without the others) is the book's reading of
  `Strata/src/Strata/Scene/Components.h`; no engine document states the motive.
- That one scene unit is one metre: no engine document says it in so many words. The page rests on the default gravity
  `SceneSettings::Gravity` (0, -9.81, 0), and on the comments in `PhysicsTypes.h` and `Components.h` that give lengths in
  metres.
- That the view matrix is the inverse of the camera's world transform: read at `SceneRenderer.cpp` (`camera.View =
  glm::inverse(translate * mat4_cast(rotation))`); the function around it was not read in full.
- That the **Inspector** edits the local fields: the page does not say it.

## Findings not applied

- `critic-basics-b-3`: applied in part. Practice holds five exercises (hand work, a standalone program with
  `solution="sketches/basics-math-matrices-ring.cpp"`, and the optional Coin Run item). No exercise runs in the playground's
  script except the Coin Run item, whose script is `pseudocode`.
- The brief's Coin Run item (six coins, a ring that turns, the prediction checked in the log): the item uses one coin and a
  ring whose `Spinner` is set to 0 degrees per second, so that the world position does not change each frame and can be
  predicted. It places no coin with `Scene::InstantiateMany` (`critic-basics-b-15`); the TRS section says what that call does.
- `critic-basics-b-9`, `-10`, `-14`, `-19`: applied (the column-by-column `Log::Info`, the declared-without-value mistake,
  the inside-out `glm` builders with the Physics Playground line, `SetParent`'s second parameter, and glTF's +Z facing).

## Clerk

- Admitted: affine transform (alias affine transformation).
- `external-hosts.txt`: `www.3blue1brown.com` (front page fetched). Left for the planner: `learnopengl.com` (the fetch returned "Not Acceptable!", nothing to confirm).

## Track walk E, final, segment 3 (2026-11-24)

- WK1 (`plan/walks/E-final-3.md`): Practice 5 names its start (your Coin Run, or Checkpoint 4 of Ship the finished
  game). In that state the coins appear only in play, so the reader places one more from `Prefabs/Coin.stprefab`; the
  pseudocode is the whole file `RingChild.cpp`.
- Checked with the 0.8.0 package, headless, on a copy of Checkpoint 4 (`docs-work/walkfix-E3`, `run1.out`): `Ring` at
  (0, 1, 0) turned (0, 90, 0) with `Spinner` at 0, a placed coin with `RingChild` beside `Coin`; the Console shows
  `coin world position (1.78814e-07, 1, -3)`.
