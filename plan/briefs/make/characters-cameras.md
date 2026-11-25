# Brief: `make/characters-cameras`

| Field | Value |
| --- | --- |
| Title | Characters and cameras |
| Kind | T |
| Size | L |
| Tracks | G |
| Needs | `make/gameplay-math`, `make/script-fields` |
| From | gamedev "Characters and cameras" (§1.11, concepts 16-17); scripting "The gameplay API, part 2": `CharacterController`, `GroundState`, drawn poses for cameras; `TransformComponent`'s drawn pose and `ResetInterpolation`; Manual/Scripting "Following moving things"; use home of interpolation for game code (`GetDrawnPosition` in `OnLateUpdate`, platforms in `OnFixedUpdate`) |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/characters-cameras` — Characters and cameras

**Covers.** A tutorial: a player character that walks an obstacle course, and a camera that follows it. It opens with
why a character is not a rigid body: a kinematic capsule moved by code does not tip over, climbs steps, stops at steep
slopes, rides platforms and pushes crates, and an entity has either a `RigidBody` or a `CharacterController`, never both
(with both it is the rigid body, and the log warns). The step sections, each ending in a checkpoint:

1. Make the player: an entity with a `CharacterController` (Height, Radius, Step Height, Max Slope Degrees, Push
   Strength, its layer) and a capsule mesh as a child, feet at the entity's origin.
2. Walk relative to the camera: a `PlayerController` script reads the Move action, flattens the camera's forward,
   builds the direction with the recipes of `make/gameplay-math`, calls `Move` every frame and turns the body to face
   where it walks.
3. Jump: `Jump` while `IsGrounded`, the four ground states (on ground, on steep ground, not supported, in air), and
   coyote time, a jump that still counts a moment after walking off a ledge (the Third-Person player's 0.15 s).
4. Stairs and slopes: up a 0.3 m step, stopped by a 0.5 m one; standing on 40 degrees, sliding on 50.
5. A camera that follows: a `FollowCamera` script on the primary camera, an entity field naming the player, placed in
   `OnLateUpdate` from the player's drawn position, with the frame-rate-independent smoothing of `make/gameplay-math`.
   First the camera follows `GetWorldPosition()` and the player judders; then `GetDrawnPosition()` fixes it. Why: what
   moves in fixed steps is drawn between its last two steps, so the drawn pose is where the player is seen.
6. Feel the fixed rate: Project Settings > Physics > Timing at 30 and at 120 steps a second, and Interpolation off and
   on: smoothness, latency and the judder come and go.
7. A camera arm that walls do not cut: `Physics::Raycast` from the player's head toward the camera, ignoring the player,
   shortens the arm at once and lets it out smoothly; orbiting with the mouse, the cursor locked while the course
   plays, and with the Look action.
8. A moving platform: a kinematic body moved by a script in `OnFixedUpdate`, so that it and its rider are drawn
   together; the character rides it and leaves it with its motion.
9. Respawn: a fall below a height teleports the player with the controller's `Teleport`, drawn where it lands; after
   moving an entity far by setting its transform in `OnFixedUpdate`, `ResetInterpolation` keeps it from being drawn
   sliding there.
10. More than one camera: a second camera that looks down on the course, and a key that switches to it and back. A game
   is drawn from one camera, the first active entity whose Camera is Primary, in hierarchy order; a script finds it with
   `Scene::GetPrimaryCamera()`, and switches by clearing Primary on it and setting it on the other with
   `SetProperty("Camera", "Primary", ...)`, or by turning the camera's entity off. The switch is a cut: the next frame
   is drawn from the other camera.

The Third-Person sample's `FollowCamera.cpp` is read at the end as the finished form of sections 5 to 7. The page's own
`FollowCamera.cpp` and the moving platform's script are two files of its tutorial, side by side in
`book:tutorials/make/characters-cameras/`, which `make/project-platformer` copies in its stage 4, so that the two pages
agree by construction (pipelines.md §6.2). What Strata
does not do here: a second view (split-screen, picture-in-picture, a camera that renders into a texture for a mirror or a
minimap), since a game is drawn from one camera, as section 10 showed; and a sequencer or
timeline for cutscenes, since camera moves and cuts are scripted, as the Showcase's camera tour (`TourPath.h`) is. The
exercises make the course the reader's own, in a script: a double jump, one more `Jump` in the air once the first is
used, and a coyote time tuned by feel. At the end the reader can make a character that walks, jumps, climbs and rides,
and a camera that follows it smoothly at any frame rate.

**Leaves out.**

- Animating the character → `make/animation`
- How the controller moves inside: collide and slide, step-up, snapping, the presence body → `physics/character-controllers`
- Strata's interpolated set and drawn transforms inside → `world/interpolation`
- The fixed step and `FixedRate` → `make/script-loop`
- Vectors, `atan2` and the smoothing weight → `make/gameplay-math`
- The camera's lens: field of view, exposure, depth of field → `make/look`
- Rigid bodies, `Teleport` of bodies and raycasts in general → `make/physics`
- Root motion through a character controller → `make/animation`

**Fit.** `over`: about 6,950 words against L (5,000). Ten step sections of about 29 steps (about 5,000 words with their
rules and figures), the opening on why a character is not a rigid body, the sample's `FollowCamera.cpp` read at the end
and the exercises reach L's top. The next size is XL (8,000) by S2; the split of the earlier line stays the other way:
`make/characters` "Characters: walking, jumping, stairs and platforms" (sections 1 to 4, 8 and 9) and
`make/follow-cameras` "Cameras that follow a character" (sections 5 to 7 and 10).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:331` | concept | home | Characters: why a kinematic capsule controller and not a rigid body, move against jump, ground state, coyote time, movement relative to the camera, facing; the mistake of both components |
| `gamedev:333` | concept | home | Cameras that follow: smoothing independent of the frame rate, drawn poses, `OnLateUpdate`, an arm that walls shorten; the mistake of following `GetWorldPosition()` |
| `gamedev:157` | feature | home | The character controller: the capsule's fields and `Move`, `Jump`, `Teleport`, `IsGrounded`, `GetGroundState` and `GetVelocity` |
| `gamedev:628` | term | home | Character controller |
| `gamedev:629` | term | home | Coyote time |
| `gamedev:619` | term | home | Interpolation, drawn pose and step alpha, in a game maker's words |
| `gamedev:500` | rule | home | One of `RigidBody` or `CharacterController`, never both |
| `gamedev:490` | rule | home | Follow moving bodies with `GetDrawnPosition()` in `OnLateUpdate` |
| `gamedev:378` | code | home | `Samples/ThirdPerson/Scripts/FollowCamera.cpp:43-101`: the orbit from the mouse and the Look action, the pivot following the drawn position with exponential smoothing on unscaled time, a teleport followed at once, the arm shortened by a raycast and let out smoothly |
| `gamedev:420` | figure | home | The capsule with its feet at the origin, step height and slope limit; the camera's pivot and arm, shortened by a ray; the movement vectors relative to the camera |
| `physics:452` | hands-on | home | The player: walk, jump, stairs, a slope too steep, a kinematic moving platform |
| `physics:453` | hands-on | home | The follow camera that judders, then fixed with `GetDrawnPosition` in `OnLateUpdate`, with Timing's Interpolation off and on |
| `scene-ecs:601` | hands-on | home | Timing at 30 and 120 with Interpolation off and on, felt in play (on the course instead of the Physics Playground) |
| `scene-ecs:602` | hands-on | home | A camera that follows a moving body with its drawn position in `OnLateUpdate`, against its world position in `OnUpdate` |
| `scripting:517` | hands-on | home | A character driven by the Move and Jump actions and a follow camera in `OnLateUpdate` with a raycast against walls |
| `new:22` | not-done | home | A second view: split-screen, picture-in-picture, a camera that renders into a texture for a mirror or a minimap; a game is drawn from one camera, the first active entity whose Camera is Primary. Evidence: `Strata/src/Strata/Scene/Scene.cpp:867-879`; `Strata/src/Strata/Runtime/GameRenderer.cpp:114-126`; `git grep -niE -e "split-?screen" -e "render-?to-?texture" -e "picture-in-picture" -e RenderTexture 822a7a46 -- Strata/src StrataScriptCore Docs` finds nothing |
| `new:23` | not-done | home | A sequencer or timeline for cutscenes: camera moves and cuts are scripted, as the Showcase's camera tour is (`TourPath.h`, which `make/samples` studies). Evidence: `Samples/Showcase/Scripts/TourPath.h:3-6`; `git grep -niE -e sequencer -e cutscene -e cinematic 822a7a46 -- Strata/src StrataEditor/src StrataScriptCore Docs/Roadmap.md` finds only the editor's input sequences (`IsInputSequenceRunning`, `DescribeSequenceResult`) |
| `new:33` | rule | home | More than one camera (section 10): a game is drawn from one camera, the first active entity whose Camera is Primary, in hierarchy order; a script finds it with `Scene::GetPrimaryCamera()` and switches by clearing Primary on it and setting it on another with `SetProperty("Camera", "Primary", ...)`, or by turning the camera's entity off; the switch is a cut. Evidence: `Strata/src/Strata/Scene/Scene.cpp:867-881` (`GetPrimaryCameraEntity`); `Strata/src/Strata/Runtime/GameRenderer.h:23-24` and `Strata/src/Strata/Runtime/GameRenderer.cpp:114-126` (the game is rendered from that camera alone); `Strata/src/Strata/Scene/ComponentRegistration.cpp:153, 162` (the Camera component's Primary property); `StrataScriptCore/Include/StrataScript/Scene.h:145-150` (`GetPrimaryCamera`); `StrataScriptCore/Include/StrataScript/Entity.h:72` (`SetProperty`), `:51` (`SetActive`) |
| `scene-ecs:93` | feature | use | The lookup of the primary camera, the first active Primary in hierarchy order, in a game maker's words (its home is `world/scene-graph`) |
| `new:24` | hands-on | home | Exercises (make it yours), done in a script: a double jump, one more `Jump` while in the air once the first is used, since `Jump` works off the ground too; a coyote time tuned by feel. Evidence: `StrataScriptCore/Include/StrataScript/CharacterController.h:54-60` (`Jump`, on the ground or not), `:74` (`IsGrounded`) |
| `physics:33` | feature | use | `CharacterControllerComponent` and its fields (their home is `physics/character-controllers`) |
| `physics:132-139` | feature | use | What the controller does, in a game maker's words: steps, slopes, ground states, platforms, being landed on, pushing |
| `physics:271` | concept | use | Character controllers as the physics part explains them, linked as "how it works" |
| `physics:382` | figure | use | A controller on stairs and slopes, the shot this page's section 4 takes again on its own course |
| `physics:425` | rule | use | Move what others ride in `OnFixedUpdate` or as a kinematic body |
| `physics:429-431` | rule | use | A controller's rotation and scale do not change its capsule; with a `RigidBody` too it is the rigid body |
| `scripting:126` | feature | use | `CharacterController` and `GroundState` in the SDK |
| `scripting:120` | feature | use | `GetDrawnPosition`, `GetDrawnRotation` and `ResetInterpolation` |
| `scripting:485` | rule | use | Read the drawn pose in `OnLateUpdate` for cameras; move ridden platforms in `OnFixedUpdate` |
| `scene-ecs:546` | rule | use | The same rule as the scene part states it (its home is `world/interpolation`) |
| `scene-ecs:489` | figure | use | Interpolation off against on, the idea of the page's section 6 picture |
| `gamedev:377` | code | use | The Third-Person player's lines on air time and coyote time (`ThirdPersonPlayer.cpp` 77-88 and 109) and its turn rate (its home is `make/project-platformer`) |
| `gamedev:156` | feature | use | Timing's `FixedRate` and Interpolation settings (their use home is `make/script-loop`) |
| `gamedev:492` | rule | use | Teleport instead of writing a transform (its home is `make/physics`) |
| `scripting:125` | feature | use | `Physics::Raycast` with an entity to ignore, for the camera arm |
| `animation:111` | feature | link | Root motion through a character controller (`make/animation`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Length, normalize, a forward flattened onto the ground, `atan2` to face a direction | `make/gameplay-math` | must |
| Smoothing that does not depend on the frame rate | `make/gameplay-math` | must |
| Frame and fixed updates, `OnLateUpdate`, `FixedRate` | `make/script-loop` | must |
| Input actions Move, Look and Jump in a script | `make/input` | must |
| Static, dynamic and kinematic bodies; raycasts; `Teleport` | `make/physics` | must |
| An entity field set in the Inspector | `make/script-fields` | must |
| `std::optional` (what `Physics::Raycast` returns) | `basics/programming-3` | must |
| Project Settings and its pages | `make/project-files` | must |
| The camera entity and its Primary flag | `make/look` | helps |

**Starting state.** A starting checkpoint, "Course", downloadable: a project from the Basic 3D template with an obstacle
course built of cubes (steps of 0.3 m and 0.5 m, ramps of 40 and 50 degrees, a gap, a wall, a kinematic platform without
a script, a crate) and the Gameplay map with Move, Look and Jump. Everything in it is made with the editor as block A
taught; the checkpoint saves the time of building it.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `coyote-time` | Coyote time | - |
| `drawn-pose` | drawn pose | - |
| `interpolation` | interpolation (use) | state interpolation, Interpolation (render) |
| `step-alpha` | step alpha (use) | - |
| `character-controller` | Character controller (use) | - |
