# Brief: `basics/math-rotations`

| Field | Value |
| --- | --- |
| Title | Rotations and quaternions |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/math-bases` |
| From | animation "Rotations that interpolate: quaternions, slerp and TRS"; foundation "The math toolkit" (rotations); Euler angles, axis and angle, quaternions, slerp; the mathematics behind `make/transforms-units` |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-rotations` — Rotations and quaternions

**Covers.** In order: (1) Euler angles: yaw, pitch and roll as turns around the up, the side and the forward axis, the
order in which they apply, and how Strata shows them (degrees in the Inspector; radians in scripts, where
`GetEulerAngles` and `SetEulerAngles` hold pitch, yaw and roll); (2) a direction from yaw and pitch, the two angles of
an orbit camera, named as the spherical coordinates that `basics/math-sphere` measures from the up axis; (3) gimbal lock,
shown with the pitch at 90°, and why blending Euler angles takes strange paths; (4) axis and angle: a rotation as one
axis and the angle to turn around it (`glm::angleAxis`), and the rotation matrix it gives; (5) quaternions: four numbers,
the axis times sin(θ / 2) and cos(θ / 2), why half the angle, unit length and normalizing, the identity; (6) combining
by multiplying: the `Spinner`'s `turn * transform.GetRotation()` applies the turn around the world's axis, the other
order around the entity's own; rotating a direction with `q * v`; the conjugate as the inverse; (7) q and -q, the
double cover: two quaternions for one rotation, and comparing rotations by the absolute value of their dot product, as
Strata's math code does; (8) interpolating rotations: slerp, which blends by a weight from 0 to 1 at an even speed,
nlerp as the cheaper approximation, and the shorter arc (one quaternion negated when the dot product is negative);
(9) converting between Euler angles, axis and angle, matrices and quaternions, with a table of what each is good for;
(10) angular velocity as a vector: its direction the axis and its length the rate in radians per second
(`RigidBody::GetAngularVelocity`), and turning by it in one small step.

Figures: the three Euler turns on a model aeroplane, gimbal lock, the half angle of a quaternion, slerp's arc against
lerp's chord, the shorter and the longer arc. The common mistakes: degrees where radians go, multiplying in the wrong
order, a blend not normalized, blending q with -q (a spin the long way round), quaternions compared number by number.
Practice (three to eight exercises, `style.md` §8) ends with the optional Coin Run item: coins that spin around a tilted
axis with `glm::angleAxis`, and an arrow above the ball that turns smoothly toward the nearest coin with `glm::slerp`
toward `Motion::LookAt`'s rotation. "Where the book uses it" names `world/interpolation`, `animation/blending`,
`physics/dynamics` and `editor-ui/inspectors`.

**Leaves out.**

- Strata's rotation helpers in code (`EulerDegreesToQuat`, `LookRotation`, `IsNearlyEqual`) → `core/math`
- The interpolated transforms drawn between fixed steps → `world/interpolation`
- Blending many rotations, and `AnimationMath::Slerp` with its nlerp fallback → `animation/blending`
- Integrating angular velocity in the physics step → `physics/dynamics`
- Solid angles and spherical coordinates measured from the up axis → `basics/math-sphere`
- Rotations with the Inspector and the gizmo, for makers → `make/transforms-units`
- The Inspector's Euler fields and how an edit keeps the quaternion → `editor-ui/inspectors`
- Dual quaternions → `animation/skinning`

**Fit.** `over`: about 7,700 words against L (5,000). The ten ideas from zero at 500 words each, the upper value for B0
(5,000), the five figures (750), the five common mistakes (600), the `Spinner`'s two lines (150), the opening (100) and
the fixed parts with the Test out box, Practice and the Coin Run item (1,100). A primer is at most L, so the page
splits (S3): `basics/math-rotations`, "Rotations: Euler angles, axis and angle, and gimbal lock" (M, about 3,600: ideas
1 to 4), and after it `basics/math-quaternions`, "Quaternions: combining, normalizing and slerp" (L, about 5,300: ideas
5 to 10, the conversions with them because they end in quaternions).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:34` | concept | home | Euler angles: yaw, pitch and roll, their order; degrees in the Inspector, radians in scripts. Figure: the three turns. General knowledge. |
| `new:35` | concept | home | A direction from yaw and pitch, the two angles of an orbit camera (spherical coordinates measured from the horizon). General knowledge. |
| `new:36` | concept | home | Gimbal lock, and why Euler angles blend badly. Figure: two axes lined up. General knowledge. |
| `new:37` | concept | home | Axis and angle (`glm::angleAxis`), and the rotation matrix of an axis and an angle. General knowledge. |
| `new:38` | concept | home | Quaternions: the axis times sin(θ / 2) and cos(θ / 2), unit length, normalizing, the identity. Figure: the half angle. General knowledge. |
| `new:39` | concept | home | Combining rotations by multiplying, and the order (around the world's axes or the entity's own); rotating a direction (`q * v`); the conjugate as the inverse. General knowledge. |
| `new:40` | concept | home | The double cover: q and -q are one rotation; comparing rotations by the absolute value of their dot product. General knowledge. |
| `new:41` | concept | home | Interpolating rotations: slerp, nlerp, and the shorter arc. Figure: slerp's arc, the shorter and the longer arc. General knowledge. |
| `new:42` | concept | home | Converting between Euler angles, axis and angle, matrices and quaternions; a table of what each is good for. General knowledge. |
| `new:43` | concept | home | Angular velocity as a vector (an axis with a rate in radians per second), and turning by it in a small step. General knowledge. |
| `new:44` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: coins spun around a tilted axis with `glm::angleAxis`, and an arrow that turns toward the nearest coin with `glm::slerp` to `Motion::LookAt`'s rotation. Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:249-250` (`glm::angleAxis` and the turn), `StrataScriptCore/Include/StrataScript/Gameplay.h:229` (`Motion::LookAt`), `StrataScriptCore/Include/StrataScript/Entity.h:184-191` (`SetRotation`, `SetEulerAngles`) |
| `animation:254` | concept | home | Quaternions for rotation: why not Euler angles (gimbal lock, bad blends) or matrices, unit quaternions, the double cover, normalization; Strata's `AnimationMath::Normalize` stays on `animation/skeletons` |
| `animation:536` | term | home | Quaternion; one glossary entry with `foundation:638` and the seed's |
| `animation:537` | term | home | Slerp and nlerp, two entries |
| `scene-ecs:684` | term | home | Nlerp, normalized linear interpolation of quaternions, as the scene part's glossary words it; one glossary entry with `animation:537`'s nlerp; `world/interpolation` links |
| `animation:574` | term | home | Yaw; one glossary entry with the seed's yaw angle |
| `foundation:638` | term | home | Quaternion, q and -q the same rotation |
| `foundation:639` | term | home | Euler angles as pitch, yaw and roll |
| `gamedev:359` | code | use | The `Spinner`'s turn, `StrataEditor/src/Editor/ScriptProject.cpp:249-250`: `glm::angleAxis` and `turn * transform.GetRotation()`; its home is `make/first-script` |
| `foundation:142` | feature | use | Strata's rotations: Euler degrees against quaternions, forward, right and up, and `IsNearlyEqual`, which compares quaternions without their sign |
| `scripting:120` | feature | use | `TransformComponent`'s `GetEulerAngles` and `SetEulerAngles` in radians (pitch, yaw, roll), `GetRotation` and `SetRotation` |
| `scripting:125` | feature | use | `RigidBody::GetAngularVelocity`, an angular velocity as one vector |
| `animation:538` | term | link | The quaternion hemisphere (the shorter arc), defined on `animation/blending` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Matrices, columns as axes, combining transforms in order | `basics/math-matrices` | must |
| The transpose, and the inverse of a rotation as its transpose | `basics/math-bases` | must |
| Vectors, length, normalizing, the dot and cross products | `basics/math-vectors` | must |
| Sine, cosine, radians and `atan2` | `basics/math-vectors` | must |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |
| Rotations with the Inspector and the gizmo | `make/transforms-units` | helps |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `axis-angle` | axis-angle | axis and angle |
| `euler-angles` | Euler angles | - |
| `gimbal-lock` | gimbal lock | - |
| `nlerp` | nlerp | - |
| `pitch-angle` | pitch angle | - |
| `quaternion` | quaternion | - |
| `roll-angle` | roll angle | - |
| `slerp` | slerp | spherical linear interpolation |
| `yaw-angle` | yaw angle | yaw |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-2 | must | missing-item | `new:34` and `scripting:120` on `basics/math-rotations` | The Covers teaches "the order in which they apply", but not Strata's order. `SetEulerAngles` and the Inspector build the rotation as glm does: the turn about Z times the turn about Y times the turn about X. So pitch applies first and roll last, all about the parent's axes; after a yaw, a roll is not a bank about the object's own forward axis, which the aeroplane figure would suggest. `GetEulerAngles` reads the angles back with `glm::eulerAngles`, whose yaw is an arcsine between -90° and 90°: a yaw of 120° reads back as (180°, 60°, 180°), and a script that turns by adding to the yaw it reads back never gets past 90°. The Inspector keeps the angles it edits for this very reason. | Idea (1) states Strata's order, and the aeroplane figure shows that order. Add the read-back range with the 120° example, and a common mistake: angles read back, changed and written again; the fix is to keep yaw and pitch in fields, as `FollowCamera` and `ThirdPersonPlayer` do. About 200 words. | `allocation/basics-b.md:311-313`, `:327-329`, `:357`, `:377`; `StrataScriptCore/Include/StrataScript/Entity.h:174-175`, `:191`; `Strata/vendor/glm/glm/detail/type_quat.inl:220-229`; `Strata/vendor/glm/glm/gtc/quaternion.inl:10-13`, `:41-44`; `Strata/src/Strata/Math/Math.cpp:93-101`; `StrataEditor/src/UI/PropertyWidgets.cpp:566-569`; `Samples/ThirdPerson/Scripts/FollowCamera.cpp:43-60`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:97-101` |
| critic-basics-b-8 | should | missing-item | `new:38` and the mistake "a blend not normalized" on `basics/math-rotations` | The reader meets a quaternion's four numbers in three orders, and no row says so. glm's constructor takes w first (`glm::quat(1, 0, 0, 0)` is the identity), glm stores x, y, z, w, `Log::Info` prints `quat(x, y, z, w)`, and commands take `[x, y, z, w]`. Also, the host normalizes every rotation a script sets and refuses a zero one ("the rotation must be a finite, non-zero quaternion"). So a blend that was not normalized still turns the entity right, and the mistake shows only in the script's own math, such as `q * v`. | Idea (5) adds the three orders, with the identity as the example and how it logs (about 60 words). The mistake "a blend not normalized" states what Strata shows, with the message (about 40 words). | `allocation/basics-b.md:317`, `:329`, `:361`; `Strata/vendor/glm/glm/detail/type_quat.hpp:44-49`, `:82-86`; `StrataScriptCore/Include/StrataScript/Log.h:41-44`; `.claude/skills/strata-scripting/SKILL.md:703`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:213-228`; `allocation/reference.md:1221` |
| critic-basics-b-18 | could | stale-item | `gamedev:359` and `new:39` on `basics/math-rotations` | The Covers says that `turn * transform.GetRotation()` turns around the world's axis. `GetRotation` is the local rotation, so the turn is around the parent's axis, which is the world's only for an entity without a rotated parent. The generated Spinner's comment says "the world's Y axis" too, and Coin Run's coins are placed under the `Coins` entity. | The Covers and the row say "around the parent's axes (the world's for an entity without a parent)" (about 20 words); the Spinner's comment goes to the table of errata (see forPlanner). | `allocation/basics-b.md:318-319`, `:375`; `StrataEditor/src/Editor/ScriptProject.cpp:240`, `:246-250`; `StrataScriptCore/Include/StrataScript/Entity.h:160`, `:172`; `allocation/make-a.md:1057` |
