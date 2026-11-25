# Brief: `make/gameplay-math`

| Field | Value |
| --- | --- |
| Title | The math of moving things: vectors, directions, angles and smoothing |
| Kind | H |
| Size | L |
| Tracks | G |
| Needs | `make/project-coin-run`, `make/transforms-units`\|`basics/math-vectors` |
| From | new; skill `strata-make-a-game` L158-256, `Samples/ThirdPerson/Scripts/FollowCamera.cpp` L43-101, `Samples/PhysicsPlayground/Scripts/Playground.cpp` L183-207; scripting "The gameplay API, part 1": `TransformComponent`'s Euler angles and its forward, right and up directions (-Z forward); the SDK's `Motion` (`LookAt`, `SmoothDamp`); each formula (a vector's length and `normalize`, the dot product, `atan2`, the `tan` of half the field of view, `1 - exp(-k dt)`) is given as a recipe: what it computes, at most two sentences of why, and a link to its primer (`make/transforms-units` gave positions, directions and rotations); use home of vectors (length, normalize, dot), angles (`atan2`) and frame-rate-independent smoothing for makers; closing exercise: hands-on G12 (balls shot through the cursor along a ray built from the camera's field of view, as `Playground::GetPointerRay` builds it) |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/gameplay-math` — The math of moving things: vectors, directions, angles and smoothing

**Covers.** A how-to of recipes (`critique/rulings-4.md`, R7): each recipe is one or two lines to type, what they
compute, when to use them, at most two sentences of why, and a link to the primer that teaches the mathematics. The page
runs on one small example built from a new Basic 3D project: a turret that watches a rolling ball. Each recipe adds a
few lines to its `Turret` script, and Play shows the result. In order: the vector from one position to another and its
length with `glm::length` (how far away the ball is); a direction with `glm::normalize`, and why a zero vector must never
be normalized; the dot product with `glm::dot` (is the ball in front or behind, and how far to the side); the angle to
turn with `std::atan2`, set with `SetEulerAngles` in radians, and why a glTF model faces +Z while an entity's forward is
-Z; an entity's forward, right and up (`GetForward`, `GetRight`, `GetUp`) and moving along a forward flattened onto the
ground, read in the skill's first-person controller (mouse and stick look as yaw and pitch, pitch clamped); the
third-person mover, where the direction is relative to the camera (`glm::cross` gives its right) and the body turns to
face where it walks; `Motion::LookAt`; smoothing that looks the same at any frame rate, `1 - exp(-k * deltaTime)` as the
weight of `glm::mix`, and the SDK's `Motion::SmoothDamp` with its velocity kept between frames; last, the ray through the
cursor, built from the camera's forward, right and up and the `tan` of half its field of view, as
`Playground::GetPointerRay` builds it. The character controller calls in the excerpts are lines to copy, with one
sentence and a link to `make/characters-cameras`, which teaches them.

The closing exercise is hands-on G12: shoot balls through the cursor along that ray, count those that land in a goal
trigger, and let them pass a glass wall on a Ghost collision layer; G12's sound budget is finished on `make/recipes`. At
the end the reader can measure a distance, tell in front from behind, turn and move things toward a target, smooth a
motion so that it does not depend on the frame rate, and aim through the cursor.

**Leaves out.**

- Vectors, the dot and cross products, sine, cosine and `atan2` as mathematics → `basics/math-vectors`
- Euler angles, quaternions and slerp as mathematics → `basics/math-rotations`
- The projection behind the pointer ray → `basics/math-projection`
- Exponential smoothing, lerp and easing as mathematics → `basics/math-interpolation`
- The exponential function and the number e → `basics/numbers`
- Moving a character with a controller, and the whole follow camera → `make/characters-cameras`
- A ray from the view in engine code (`Ray::FromNDC`) → `core/math`
- Random numbers and seeds, and the sound budget of G12 → `make/recipes`
- Raycasts, masks and collision layers as a game maker sets them → `make/physics`
- The camera's lens, its field of view and exposure → `make/look`

**Fit.** `fits`: about 5,400 words against L (5,000). Nine recipes of 250 to 550 words (code, what it computes, two
sentences of why, a step with its result), about 3,650 words with their three excerpts, take the most, then the closing
exercise G12 with its solution and the three diagrams.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:376` | code | home | `.claude/skills/strata-make-a-game/SKILL.md:158-189`: the first-person controller: yaw and pitch from the mouse and the Look action, the pitch clamped, `SetEulerAngles` with `glm::radians`, the forward flattened and normalized, the right; `Move` and `Jump` given as lines to copy |
| `new:1` | code | home | `.claude/skills/strata-make-a-game/SKILL.md:204-228`: the third-person mover: the camera's forward flattened, its right from `glm::cross`, a direction from the Move action, and the body turned to it with `std::atan2(direction.x, direction.z)` because glTF models face +Z |
| `gamedev:382` | code | home | `Samples/PhysicsPlayground/Scripts/Playground.cpp:183-207`: `GetPointerRay`, the cursor's place on the camera's image plane from the vertical field of view, the aspect and the window size |
| `gameui:207` | feature | home | The SDK's `Motion` helpers: `LookAt` (turns -Z toward a point, keeps +Y up) and `SmoothDamp` for a number, a `glm::vec2` and a `glm::vec3`, with its velocity kept between calls and an optional top speed |
| `gamedev:545` | hands-on | home | The closing exercise, G12: balls shot through the cursor, a goal trigger that counts them, a Ghost layer that a glass wall lets through; the impact sounds with a budget are the exercise of `make/recipes` |
| `scripting:120` | feature | use | `TransformComponent`'s Euler angles in radians, world position and rotation, and forward, right and up with -Z forward |
| `scripting:136` | feature | home | `Motion` in the SDK, one entry with `gameui:207`: `LookAt` and the critically damped `SmoothDamp` for a number and a vector; `reference/script-api` lists the declarations and links here |
| `scripting:343` | concept | use | The determinism helpers' smoothing: `SmoothDamp` is critically damped, so it never overshoots (the concept's home is `make/recipes`) |
| `gamedev:378` | code | use | Line 79 of `FollowCamera.cpp`, the smoothing weight `1 - exp(-FollowSharpness * deltaTime)`, read first here; the whole camera is `make/characters-cameras`' |
| `scripting:122` | feature | use | `Input::GetMousePosition` and `GetMouseDelta`, and the Look action, for mouse look and the pointer ray |
| `scripting:129` | feature | use | `Game::GetWindowSize`, the pixels the pointer ray divides by |
| `scripting:125` | feature | use | `RigidBody::SetLinearVelocity` to shoot a ball, and `Physics::Raycast` named for what the ray is used for next |
| `physics:122-126` | feature | use | The project's collision layers, named and set for the exercise's Ghost layer (their use home is `make/physics`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A position or a direction as three numbers (x, y, z); adding and scaling them | `make/transforms-units` | must |
| Degrees and radians, and `glm::radians` | `make/transforms-units` | must |
| A rotation stored as a quaternion and combined by multiplying | `make/transforms-units` | must |
| A script class with float fields, `OnUpdate` and `deltaTime` | `make/first-script` | must |
| Variables, expressions, `if`, and namespaces with `::` | `basics/programming-1` | must |
| Functions with parameters and return values, structs | `basics/programming-2` | must |
| Classes, references, `std::optional` and template arguments (`GetProperty<float>`) | `basics/programming-3` | must |
| Frame and fixed updates, `OnLateUpdate` | `make/script-loop` | must |
| Finding an entity and its transform from a script; reading a property by name; `Instantiate` that never waits | `make/scripting-scene` | must |
| Input actions (Move, Look) and the mouse in a script | `make/input` | must |
| Rigid bodies, velocities, triggers and collision layers | `make/physics` | must |
| Vectors, length, the dot product, angles, sine, cosine and `atan2` as mathematics | `basics/math-vectors` | helps |
| Euler angles and quaternions as mathematics | `basics/math-rotations` | helps |
| Perspective projection and the field of view | `basics/math-projection` | helps |
| The exponential function | `basics/numbers` | helps |
| Exponential smoothing and lerp | `basics/math-interpolation` | helps |
| The camera entity and its field of view in the Inspector | `make/look` | helps |

**Starting state.** A new project from the Basic 3D template (its camera, sun, sky and ground); no checkpoint. The first
step adds a sphere named "Ball" with a dynamic RigidBody and a cylinder named "Turret", as `make/scenes-entities` and
`make/physics` taught. The closing exercise starts from the page's end state and adds a ball prefab.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b1-2 | must | missing-item | `gamedev:545` and `scripting:125` on `make/gameplay-math` (the closing exercise G12) | G12 shoots balls by giving a new ball a velocity. A ball made with `Scene::Instantiate` has its physics body only from the next fixed step. A `SetLinearVelocity` call in the same update fails and logs "'Ball' has no body in the physics simulation (bodies are active entities with a RigidBody component and colliders)", which a reader whose ball has a RigidBody cannot explain; the ball drops at the muzzle. The Physics Playground keeps the new ball and sets its velocity in `OnFixedUpdate` until the call succeeds. No page says this; the gotchas of `make/physics` do not hold it either. | The shooting step of G12 and its worked solution keep the spawned ball in a member and set its velocity in `OnFixedUpdate` until `SetLinearVelocity` returns true, as the sample does, with the log line as the step's "If you do not see it" (about 100 words). See forPlanner for `make/physics`. | `allocation/make-b1.md:21-22`, `:51`, `:58`; `allocation/make-a.md:1288-1290`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:103-115`, `:209-221`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1202-1227`, `:1285-1289` |
| critic-make-b1-3 | should | shape | `make/gameplay-math`, `make/timers-events`, `make/script-fields`, `make/script-builds`, `make/levels-saves` | style.md gives a how-to a `## Variations` section: the same goal under other conditions. The Covers of these five how-tos name no variation, so the writer has nothing to fill it with. The how-tos of `make-a` and `make-b2` name theirs. (`make/recipes` has its "what to change" per recipe.) | Each Covers names two variations (about 250 words a page). From the pin: gameplay-math, aiming with the right stick through the Look action instead of the cursor (`FollowCamera.cpp:57-60`), and a turret that turns at a limited speed (critic-make-b1-16); timers-events, a timer in `OnFixedUpdate` fed with the fixed delta, for gameplay that keeps step with physics, and a held gamepad direction repeated (critic-make-b1-5); script-fields, tuning many spawners at once through their prefab (critic-make-b1-4); script-builds, the plain `cmake -S` and `-B` build as a check that the code compiles on another machine (critic-make-b1-1); levels-saves, three save slots named "Slot 1" to "Slot 3" and listed with `ListSaveFiles`. The five Fit lines count them. | `style.md:535-541`; `allocation/make-b1.md:5-24`, `:91-111`, `:174-193`, `:420-440`, `:922-962`; `allocation/make-a.md:130`, `:424`; `allocation/make-b2.md:393`; `StrataScriptCore/Include/StrataScript/Game.h:104-107`, `:157-158` |
| critic-make-b1-16 | should | missing-item | `make/gameplay-math` | The page turns things toward a target with `atan2` and teaches smoothing, but not how to smooth a turn. An angle jumps from +180 to -180 degrees, so a yaw smoothed toward an `atan2` target swings the long way round when the target passes behind. The sample's follow camera wraps the difference with `std::remainder(behind - Yaw, 360.0f)`. The other way is to smooth the rotation itself toward the one `Motion::LookAt` gives, with `glm::slerp`. | Add a recipe after the smoothing recipe: a turret that turns smoothly, with the wrap, the `glm::slerp` form and the frame-rate-independent weight (about 250 words). | `allocation/make-b1.md:10-16`; `Samples/ThirdPerson/Scripts/FollowCamera.cpp:63-69`; `StrataScriptCore/Include/StrataScript/Gameplay.h:226-248` |
| critic-make-b1-22 | could | other | the pointer ray of `make/gameplay-math`; the check "Mouse units on a scaled display" | The pointer ray divides `Input::GetMousePosition` by `Game::GetWindowSize`. critic-audio-input-7 suspects that the two differ on a scaled display in an exported game, and its check names only `input/mouse-cursor`. The recipe, G12 and the grab tool of `make/recipes` rest on the same division, so the check's result would not reach them. | The check's pages include `make/gameplay-math` and `make/recipes`; the pointer-ray recipe holds an item of type `open` ("Check: Mouse units on a scaled display.") until the result is in. | `allocation/README.md:282`; `allocation/completeness.md:101`; `allocation/make-b1.md:17-18`, `:49`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:183-207`; `StrataScriptCore/Include/StrataScript/Input.h:274` |
