# Notes: basics/math-rotations

## New terms

| Term | Definition | Home | Aliases |
| --- | --- | --- | --- |
| conjugate | The quaternion with the signs of x, y and z flipped; for a unit quaternion it is the inverse. | `basics/math-rotations` | quaternion conjugate |
| double cover | The fact that each rotation has exactly two unit quaternions, q and -q. | `basics/math-rotations` | - |
| angular velocity | A vector whose direction is the axis a body turns around and whose length is the rate in radians per second. | `basics/math-rotations` | - |
| orbit camera | A camera that circles a target and keeps a yaw, a pitch and a distance. | `basics/math-rotations` | - |
| identity (rotation) | The rotation that changes nothing, the quaternion (1, 0, 0, 0); the matrix identity is homed on `basics/math-matrices`. | `basics/math-rotations` | identity quaternion |

## Requests

- Word list: add `conjugate` to `tools/data/extra-words.txt` (the only `word-list` finding left; the page defines it in bold).
- External host: `eater.net` for the entry "Visualizing quaternions" of Further reading, which the page cites without a link.
- Figures (kind diagram, not drawn): `three-turns`, `gimbal-lock`, `half-angle`, `slerp-arc`, `short-arc` in `src/content/figures/basics/math-rotations.json`.
- Errata for the engine's table: the comment of the generated Spinner (`StrataEditor/src/Editor/ScriptProject.cpp:240`) says "the world's Y axis", but `GetRotation` is the local rotation, so the turn is around the parent's Y axis (finding critic-basics-b-18).

## Not verified

- That the coins of Coin Run stand under a parent entity (`make/project-coin-run`'s end state is not in the pin clone); the page says only "when the entity has no rotated parent".
- The wording of `make/first-script` about the `Spinner`; the page says that the editor generates it for a new script project, as the inventory `gamedev:359` states.
- The page "Visualizing quaternions" at eater.net, cited from memory without a link.
- `allocation/*.md` and `reference.md` lines named by the findings were not read; each claim was checked in the pin's code instead (`Entity.h`, `ScriptHostAPI.cpp`, `Log.h`, `Math.h`, glm's `type_quat.inl`, `quaternion.inl`, `quaternion_common.inl`, `PropertyWidgets.cpp`, the `ThirdPerson` scripts).

## Findings not applied

- Brief "Fit" (split into `math-rotations` and `math-quaternions`): not applied; the task and the brief's table make this one page of size L with all ten ideas.
- Brief Covers (3), "gimbal lock shown with the pitch at 90 degrees": applied as the toy aeroplane's story (own axes, middle angle the pitch), and the page says that in Strata's order (Z times Y times X) the middle angle is the yaw, so the lock is at a yaw of 90 degrees; the sketch shows that case.
- critic-basics-b-2, critic-basics-b-8 and critic-basics-b-18 are applied; the Spinner comment's erratum is listed under Requests.
- Not applied from the brief: nothing else; the Coin Run item is the last Practice exercise (worked solution in `pseudocode`).

## Sketches

- `basics-math-rotations-euler.cpp`, `-compose.cpp`, `-slerp.cpp`, `-spin.cpp` (standalone, glm only). The pagecheck run also compiled `sketches/basics-math-sphere-rows.cpp` of another page once and reported a compile failure there; it is not part of this page.

## Clerk

- Admitted: conjugate, double cover, angular velocity, Identity (rotation) (alias identity quaternion). Refused: orbit camera (homed on `editor/camera-viewport`).
- `external-hosts.txt`: `eater.net` (front page fetched: Ben Eater's site). The engine erratum is the planner's.

## Track walk E, final, segment 3 (2026-11-24)

- WK1 (`plan/walks/E-final-3.md`): Practice 7 names its start, your Coin Run or Checkpoint 4 of Ship the finished
  game, with a link to that section. Not built: the tilted axis replaces the axis in `Scripts/Coin.cpp` of that
  checkpoint, which holds the line the answer changes.
