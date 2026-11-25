# Brief: `make/transforms-units`

| Field | Value |
| --- | --- |
| Title | Positions, rotations and units |
| Kind | C |
| Size | L |
| Tracks | G, B |
| Needs | `make/scenes-entities` |
| From | gamedev "Positions, rotations and units" (concept 5); use home, for makers, of a position or a direction as three numbers (x, y, z), adding and scaling them, degrees and radians (`glm::radians`), a rotation as an axis and an angle, a rotation stored as a quaternion and combined by multiplying (the `Spinner`'s `turn * transform.GetRotation()`, `StrataEditor/src/Editor/ScriptProject.cpp:249-250`), axes, handedness and units (their mathematics is `basics/math-vectors`', `basics/math-matrices`' and `basics/math-rotations`'); every idea is first shown with the Inspector's numbers and the gizmo, because the reader cannot read code yet; the code forms stand in one last section, "The same ideas in code", which says that it is read again from `make/scripting-scene`, the first page that uses them |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/transforms-units` — Positions, rotations and units

**Covers.** A concept page for a reader who cannot read code yet: every idea is shown first with the Inspector's
numbers and the gizmo on Coin Run's level, and the code forms come only in the last section. The problem as the reader
met it: the walls of `make/scenes-entities` took numbers like (0, 0.5, -10), and the coin needed a turn of 90 degrees
to stand up; what do the numbers mean? The naive answer (x is right, y is up, done) and where it breaks: which way is
forward, which way does a turn go, what does a child's position count from. The ideas, in this order: a position as
three numbers (x, y, z) along the three axes shown by the Move gizmo's red, green and blue arrows, y up, in metres
(the ball is 1 m across, the ground 20 m); adding numbers moves a thing, multiplying them scales a distance; a
direction as three numbers, and forward as -Z for cameras, lights and a script's forward, while glTF models face +Z;
handedness shown with the right hand; scale as three factors, and a negative scale that mirrors an object and still
draws and lights it correctly; a rotation in degrees, the Rotate gizmo's rings and the Inspector's three angles (pitch,
yaw, roll) in degrees; a rotation as an axis and an angle (the coin's spin about the vertical axis); degrees and
radians from zero (a full turn is 360 degrees or 2π radians, about 6.283); a rotation stored as a quaternion of four
numbers that nobody types, and two rotations combined by multiplying, in an order that matters (shown with two turns
in the Inspector, done in both orders); parent and child, local against world position, with the solar-system exercise
(Sun, Earth and Moon in the Hierarchy: turn the Sun and its children follow) and the gizmo's World and Local switch.
The approaches engines use, in a short table with sources: which axis is up, left- or right-handed, metres or
centimetres, angles stored as Euler angles or quaternions. Strata's choice and its reason: y up, right-handed, -Z
forward and metres as glTF has them, quaternions stored and angles shown. What it cannot do: the Inspector's angles are
the ones typed, and a rotation read back as angles may show other numbers that mean the same turn. Common mistakes: a
model that walks backwards (+Z against -Z), adding angles to a stored rotation, a model in centimetres a hundred times
too large (fixed by `make/assets`). The last section, "The same ideas in code", shows a position and a direction as
`glm::vec3`, `glm::radians`, the `Spinner`'s turn (`glm::angleAxis` and `turn * transform.GetRotation()`), and the
Transform's local and world positions in the SDK; it says that `make/scripting-scene` sends the reader back to it.
At the end the reader can read and set any Transform in the Inspector, predict where a child goes when its parent
turns, and convert between degrees and radians.

**Leaves out.**

- The mathematics of vectors: length, dot and cross products → `basics/math-vectors`
- Matrices, spaces and matrix order → `basics/math-matrices`
- Euler angles, quaternions and slerp as mathematics → `basics/math-rotations`
- Vectors, `normalize`, `atan2` and smoothing as recipes for game code → `make/gameplay-math`
- Strata's clip space and depth conventions → `gpu/coordinates`
- World transforms, their caches and the transform contract → `world/scene-graph`
- How mirrored instances are drawn → `draw/mirrors-camera-relative`
- A model's import scale → `make/assets`

**Fit.** `fits`: about 5,750 words against L (5,000). Ten ideas taught from zero at B0's length take most of it, each
shown with the gizmo or the Inspector, with the conventions figure, the approaches table, the solar-system exercise and
two short code excerpts in the last section.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:71` | feature | home | The conventions a maker must know: -Z forward, glTF's +Z, Euler degrees in commands and the Inspector but radians in `SetEulerAngles`, metres, y up |
| `gamedev:301` | concept | home | Transforms and the hierarchy: local and world, parent and child, units, axes, Euler against quaternions; the mistakes (backwards models, angles added to a quaternion) |
| `gamedev:404` | figure | home | The coordinate conventions: y up, -Z forward, glTF's +Z, yaw, pitch and roll |
| `gamedev:581` | term | home | World position and local position |
| `gamedev:582` | term | home | Quaternion |
| `gamedev:583` | term | home | Forward (-Z) |
| `render-scene:559` | hands-on | home | Mirroring safely: a negative scale mirrors the ball, and it still draws and lights correctly |
| `scene-ecs:596` | hands-on | home | The solar system in the Hierarchy: local against world |
| `gamedev:359` | code | use | The `Spinner`'s two lines of the turn, `StrataEditor/src/Editor/ScriptProject.cpp:249-250`, in "The same ideas in code" |
| `scene-ecs:55` | feature | use | The Transform component: translation, rotation, scale relative to the parent |
| `scene-ecs:292` | concept | use | Transforms and the scene graph, at the user's level |
| `scene-ecs:628-629` | term | use | Local and world transform; translation, rotation and scale |
| `editor-ui:177` | feature | use | Rotations edited as the angles the person typed |
| `editor-ui:202` | feature | use | The gizmo: move, rotate and scale, World and Local, snapping |
| `editor-ui:563` | figure | use | The three gizmos on a selected object, World against Local |
| `editor-ui:769-771` | term | use | Gizmo; world and local space; snapping |
| `scripting:120` | feature | use | The SDK's `TransformComponent`, local and world, in the last section |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Entities, the Transform component, the Hierarchy and the Inspector | `make/scenes-entities` | must |
| Moving the Scene view and selecting | `make/editor-tour` | must |
| How to read code you do not understand yet (for the last section) | `start/how-to-read` | helps |
| Vectors as mathematics | `basics/math-vectors` | helps |
| Rotations and quaternions as mathematics | `basics/math-rotations` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `forward-z` | Forward (-Z) | - |
| `local-position` | local position | - |
| `world-position` | World position | - |
| `quaternion` | quaternion (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-15 | should | stale-item | `make/scenes-entities` (step 2), `make/transforms-units` | The pages call a Transform's first value "Position". The Inspector labels it **Translation**, and the SDK's local calls are `GetTranslation` and `SetTranslation`, beside `GetWorldPosition`. A B0 reader told to "type its Position" finds no such field. | `make/scenes-entities` step 2 says "**Translation**, its position"; `make/transforms-units` teaches the word once where it teaches a position, and its code section names `SetTranslation` for the local position and `SetWorldPosition` for the world one (about 40 words). | `allocation/make-a.md:221`, `:321-322`, `:337-339`; `StrataTests/Architecture/ComponentSchema.json:57`; `Strata/src/Strata/Scene/ComponentRegistration.cpp:84`; `StrataScriptCore/Include/StrataScript/Entity.h:171`, `:177`, `:200` |
| critic-make-a-18 | should | missing-item | `make/input` (steps 1 and 5) | No step says which world direction a key or the Move action becomes. A Vector2 action gives +Y for forward (W, or the stick pushed up), while forward on the level, away from Basic 3D's camera, is -Z. A reader who writes `glm::vec3(move.x, 0.0f, move.y)` sends the ball toward the camera on W, the backwards mistake of `make/transforms-units`. | Step 1 moves the ball along -Z for W and +X for D; step 5 turns the action's vector into `glm::vec3(move.x, 0.0f, -move.y)`; each with one sentence that names the -Z forward of `make/transforms-units` (about 60 words). | `allocation/make-a.md:1141-1142`, `:1151-1152`, `:336`; `StrataScriptCore/Include/StrataScript/Input.h:402-403`; `.claude/skills/strata-make-a-game/SKILL.md:130`, `:180`; `StrataEditor/src/Editor/ProjectTemplates.cpp:31`, `:53-54` |
