# Allocation: make-b1

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

## `make/timers-events` — Timers, time scale and events between scripts

**Covers.** A how-to on a small arcade room built from a new Basic 3D project. First the `Time` clocks a script can read:
the frame's delta and the fixed delta, the elapsed time and the frame index, the time scale, and the two clocks that go
on at time scale 0, the unscaled delta and the real time; which one to use for what, in a table. Then `Timer`: a crate
dropped every two seconds by a repeating timer (`for (int32_t i = timer.Update(deltaTime); i > 0; i--)`, and why a
repeating timer keeps its overshoot), a one-shot delay, and a cooldown on a dash key; a timer fed with scaled time stops
while the game is paused, and a duration that is not positive stops it. Then `KeyRepeat`: a selection marker moved along a
row of cubes while an arrow key is held, fired on the press, after a delay and then at an interval; the excerpt of
`Gameplay.h` shows it as a small state machine. One sentence says that `KeyRepeat` is the script's own helper and
differs from the menu key repeat of UI actions, which the engine applies on the UI map (`input/actions` homes it,
`make/menus` uses it). Then time scale as a game uses it: slow motion at 0.25 and a pause at 0,
with a "Paused" text that blinks on unscaled time; the pause menu itself is `make/menus`'. Last, scripts that talk to
each other: a `Scoreboard` script on an entity named "Game", and pickups that find it again each time they need it
(`Scene::FindEntityByName("Game").GetScript<Scoreboard>()`, checked for `nullptr`) and call its `AddPoint`, as the
Third-Person sample's `Coin` calls `CourseState::AddCoin`; the rule that a `GetScript<T>()` pointer is never kept from
one frame to the next, because the script may be destroyed or reloaded, so a script keeps the `Entity` and checks
`IsValid()`; `AddScript<T>()` to give an entity a behaviour while the game runs, and `HasScript` and `RemoveScript` by
class name. What Strata does not do here: coroutines; nothing waits inside a callback, and timers and state machines
do that work. The exercises, done in a script: a dash cooldown shown as a bar that fills with the timer's progress, and
a countdown on unscaled time beside one on scaled time, with what each does while the game is paused. At the end the
reader can time things in game time or in real time, repeat a held key, slow and pause the game, and let scripts call
each other safely.

**Leaves out.**

- Frame and fixed updates, `FixedRate` and what time scale does to the loop → `make/script-loop`
- The fixed step, time dilation and the accumulator as a mechanism → `core/time`
- A pause menu and UI animated on unscaled time → `make/menus`
- The UI's own key repeat on the UI map → `make/menus`
- Smoothing over time → `make/gameplay-math`
- Random numbers and seeds → `make/recipes`
- State machines, managers and object pools → `make/patterns`
- Fields set in the Inspector, entity and asset fields → `make/script-fields`
- Waiting for game time in a play-test, counted in fixed steps → `make/automated-playtests`

**Fit.** `fits`: about 3,200 words against M (3,000). The `Timer` section and the scripts that call each other, with
its rule (about 1,000 words), the table of clocks, the `KeyRepeat` excerpt and the two exercises take the most; the
absence of coroutines is one sentence.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:146` | feature | home | `KeyRepeat`: fires on the press, after a delay, then at an interval while the key stays down |
| `audio-input:174` | feature | home | The same helper as the input survey lists it: it runs inside the script module, with a delay of 0.25 s and an interval of 0.05 s by default |
| `gamedev:371` | code | home | `StrataScriptCore/Include/StrataScript/Gameplay.h:178-219`: `KeyRepeat`, a small state machine for a held key (press, delay, interval, a long frame repeating once) |
| `gameui:208` | feature | home | `Time::GetUnscaledDeltaTime`, the clock that goes on at time scale 0, for whatever moves while the game is paused |
| `gamedev:618` | term | home | Unscaled time |
| `gamedev:496` | rule | home | Never keep a `GetScript<T>()` pointer from one frame to the next; keep the `Entity`, check `IsValid()` and ask again |
| `scripting:123` | feature | home | `Time` in the SDK, beside `gameui:208`: delta, fixed delta, elapsed time, frame index, time scale, unscaled delta, real time, and which clock to use for what; `reference/script-api` lists the declarations and links here |
| `scripting:134` | feature | home | `Timer` in the SDK: one-shot and repeating, the overshoot kept so that a repeating timer does not drift, a duration that is not positive stops it; `reference/script-api` lists the declarations and links here |
| `scripting:135` | feature | home | `KeyRepeat` in the SDK, one entry with `gamedev:146` and `audio-input:174`; `reference/script-api` lists the declaration and links here |
| `scripting:343` | concept | use | The determinism helpers' timer: a repeating `Timer` keeps its overshoot, so it does not drift (the concept's home is `make/recipes`) |
| `scripting:118` | feature | use | `Entity`'s `GetScript<T>`, `AddScript<T>`, `HasScript` and `RemoveScript` |
| `scripting:474` | rule | use | The scripting survey's form of the same rule, with its reason |
| `scripting:385` | code | use | Lines 43-44 of `Coin.cpp`: the coin finds `CourseState` again when it is collected (the whole script is `make/recipes`') |
| `gamedev:321` | concept | use | The script lifecycle's mistake of caching `T*` across frames (its home is `make/script-loop`) |
| `new:13` | not-done | home | Coroutines: nothing waits inside a callback; timers and state machines do that work. Evidence: `git grep -n -i -e coroutine -e co_await 822a7a46 -- Strata/src StrataScriptCore` finds nothing; `StrataScriptCore/Include/StrataScript/Script.h:83-97` (the 15 callbacks, plain `void` functions) |
| `new:14` | hands-on | home | Exercises, done in a script: a dash cooldown shown on the HUD as a bar that fills with `Timer::GetProgress`; a countdown on `Time::GetUnscaledDeltaTime` beside one on the scaled delta, and what each does at time scale 0. Evidence: `StrataScriptCore/Include/StrataScript/Gameplay.h:143` (`Update`), `:166-170` (`IsRunning`, `GetRemaining`, `GetProgress`); `StrataScriptCore/Include/StrataScript/Time.h:57` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The script lifecycle: `OnCreate`, `OnUpdate`, `OnFixedUpdate`, and `deltaTime` | `make/script-loop` | must |
| What time scale does to the loop | `make/script-loop` | must |
| Finding entities by name from a script; instantiating a prefab and asking for it early | `make/scripting-scene` | must |
| Prefabs | `make/prefabs` | must |
| Pointers at the use level: `T*`, a `nullptr` check, `->` | `basics/programming-3` | must |
| Classes with member variables and methods | `basics/programming-3` | must |
| Loops and functions | `basics/programming-2` | must |
| Keys and input actions in a script | `make/input` | must |
| Triggers and `OnTriggerEnter` | `make/physics` | must |
| Text on a HUD set from a script | `make/hud` | must |
| The fixed step and time dilation as a mechanism | `core/time` | helps |

**Starting state.** A new project from the Basic 3D template; no checkpoint. The first step makes a crate prefab from a
cube with a dynamic RigidBody, as `make/prefabs` and `make/physics` taught, and a text element for the score, as
`make/hud` taught.

**Command-only steps.** none

## `make/script-fields` — Tuning scripts from the editor: fields, references and prefabs

**Covers.** A how-to on a crate spawner built from a new Basic 3D project. The goal: tune a script from the Inspector
instead of the code. It starts with a `Spawner` class that has one field of each of the ten types (`bool`, `int32_t`,
`float`, `glm::vec2`, `glm::vec3`, `glm::vec4`, `glm::quat`, `std::string`, `Entity`, `AssetHandle`), and the steps show
how the Inspector's Script section shows each one: the class picker, the default that the class gives, the value set on
one entity, and the reset button. No other type exists: a `std::vector`, an array, an enum, a `double`, an `int64_t` or
a struct fails to compile with "Unsupported script field type", and the usual ways around it are several fields, an
`int32_t` for an enum, or a string. An `Entity` field takes an entity of the scene (the spawn point); an `AssetHandle`
field takes an asset (the crate prefab). Then the spawner works: it asks for the prefab in `OnCreate`, instantiates it by its
handle at the spawn point at an interval given by a float field, and handles "not loaded yet": `Scene::Instantiate`
returns a null entity until the prefab is in, and never waits. Then values while playing: a field changed during Play
takes effect at once, and Stop brings back the edited value, because Play runs on a copy. Hot reload keeps every field
whose name and type stay the same; a renamed or retyped field loses its stored value and the log says so. A renamed
class is lost the same way: an entity whose Script entry names a class the module no longer has gets no instance, and
the log says so; so after renaming a class, the reader picks it again on each entity. Last, fields
in prefabs: the spawner made into a prefab, a field's value overridden on one instance (shown as an override, like any
property), applied to the prefab or reverted; an entity field that points inside the prefab follows each instance. The
exercises, done in the editor and in a script: a second spawner whose interval and prefab are overridden on the
instance and then reverted, and an `Entity` field left empty, which the spawner checks with `IsValid` and replaces with
its own position. At the end the reader can expose any value of a script to the editor, wire entities and assets into
scripts without code, and spawn prefabs safely.

**Leaves out.**

- Writing a script class, `ST_SCRIPT_FIELD` and building, the first time → `make/first-script`
- Hot reload as a workflow → `make/first-script`
- Timers → `make/timers-events`
- Many instances in one call (`Scene::InstantiateMany`) → `make/performance`
- Prefabs, overrides, apply and revert in general → `make/prefabs`
- How the Inspector is built from registered properties → `editor-ui/inspectors`
- How fields and their defaults cross the binary interface → `scripting/abi-sdk`
- How prefab overrides are stored and kept exact → `world/prefabs`

**Fit.** `fits`: about 3,200 words against M (3,000). Ten numbered steps with their results and the table of the ten
types (about 1,900 words), three rules (assets asked for early, what hot reload keeps, a renamed class) and the two
exercises take the most; the absence of other field types is one short paragraph.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:131` | feature | home | Attaching a class (Add Component > Script) and its fields per entity, with defaults and reset, and their live values while the game plays |
| `scripting:432` | figure | home | The Inspector with a Script component: the class picker and one field of every type with its default and reset button |
| `scripting:515` | hands-on | home | The spawner: a prefab field asked for early, `Scene::Instantiate` by handle, "not loaded yet" handled; its 100 instances in one call are `make/performance`' |
| `scripting:114` | feature | use | `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`, which register the fields |
| `scripting:115` | feature | use | The ten field types |
| `scripting:117` | feature | use | `AssetHandle`, the type of an asset field |
| `scripting:118` | feature | use | `Entity` as the type of an entity field, and `IsValid` |
| `scripting:121` | feature | use | `Assets::RequestLoad`, `Assets::IsLoaded` and `Scene::Instantiate` by handle |
| `scripting:154` | feature | use | The Script component: the classes of an entity and their field values, saved with the scene |
| `scripting:326` | concept | use | Serialized fields: stored per entity by name and type; a renamed field's values are ignored with a warning |
| `scripting:472` | rule | use | Only fields survive hot reload |
| `scripting:481` | rule | use | Request assets early; `Instantiate` never waits |
| `gamedev:494` | rule | use | The same rule as game makers meet it (its home is `make/scripting-scene`) |
| `scene-ecs:174` | feature | use | Prefab overrides per property, script fields among them (`Script` and `<Class>.<Field>`) |
| `new:15` | not-done | home | Script field types beyond the ten: no `std::vector`, array, enum, `double`, `int64_t` or struct; such a field fails to compile with "Unsupported script field type"; the ways around it are several fields, an `int32_t` for an enum, or a string. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:133-137` (`c_IsFieldType`), `:785-786` (the `static_assert` and its message) |
| `new:36` | rule | home | After renaming a script class, pick it again on each entity: an entry whose class the module lacks gets no instance and a problem is reported, and a hot reload removes the vanished class's instances from the playing entities, so a rename detaches the class everywhere, as renaming a field loses its value. Evidence: `Strata/src/Strata/Scripting/ScriptSystem.cpp:619-624` (a class the module lacks: no instance, a problem reported), `:1290-1295` (on reload, a class that no longer exists is removed from the entity); `Strata/src/Strata/Scripting/ScriptEngine.h:60-62` (classes that no longer exist lose their instances); `Docs/DeveloperGuide.md:2129-2131` |
| `new:16` | hands-on | home | Exercises, done in the editor and in a script: a second spawner instance whose interval and prefab are overridden and then reverted; an `Entity` field left empty, which the spawner checks with `IsValid` and replaces with its own position. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:39` (`IsValid`); `StrataScriptCore/Include/StrataScript/Script.h:133-137` (the field types) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A script class, `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD` and a float field | `make/first-script` | must |
| Hot reload | `make/first-script` | must |
| Prefabs, instances, overrides, apply and revert | `make/prefabs` | must |
| Asset handles, in one paragraph | `make/assets` | must |
| `Instantiate` never waits: asking for assets early | `make/scripting-scene` | must |
| A rotation stored as a quaternion | `make/transforms-units` | must |
| `std::string` | `basics/programming-2` | must |
| Play on a copy, and Stop | `make/play-test-debug` | must |
| `Timer` | `make/timers-events` | helps |

**Starting state.** A new project from the Basic 3D template; no checkpoint. The first step makes a crate prefab from a
cube with a dynamic RigidBody, as `make/prefabs` and `make/physics` taught, and an empty entity named "Spawn Point".

**Command-only steps.** none

## `make/patterns` — Patterns for game code: state machines, managers and object pools

**Covers.** A concept page about the shapes game code takes once it grows. The problem as a reader meets it: a script
like Coin Run's, grown for a week, with flags (`isPaused`, `isDead`, `hasWon`) that contradict each other, every coin
looking for the score, and bullets created and destroyed many times a second. The naive answers (more flags, a search
for the scoreboard on every coin, `Instantiate` and `Destroy` for everything) and where each breaks. Then the idea: name
the states, give shared work one owner, and keep objects instead of remaking them. The approaches follow, each from the
flaw of the one before, with a table of what each costs and which engines use them (Nystrom's *Game Programming
Patterns*: State, Update Method, Object Pool; Unity's and Godot's habits for comparison):

1. State machines: flags, then a scoped enum with a `switch` (the page's guard, which patrols, chases and returns, is
   the running example; it is also the answer to "where is the AI": Strata has none, see below), then states that own
   their enter and exit code; the excerpt of the Third-Person pause menu, whose Pause action moves between playing,
   paused and "settings open"; an animation controller is a state machine kept as data, which `make/animation` edits.
2. The update method: the engine already calls every script's `OnUpdate` and `OnFixedUpdate` in a known order; game code
   does not need its own loop.
3. Managers: one script on an entity named "Game" that owns the course's state (the Third-Person sample's
   `CourseState`), found by name by whoever needs it (the coins), against a global variable or a singleton; state that
   must outlive a scene is `make/levels-saves`'.
4. Object pools and showing instead of creating: entities made once in `OnCreate` and switched with `SetActive`; the
   Tetris board's 200 cells, found again in `OnReload` instead of made twice; the board's `Refresh`, which compares what
   it shows with what it should show and touches only what changed (a material set, an entity shown or hidden, a HUD
   text rewritten only when its number changed). An inactive pooled entity gets no `OnUpdate`, `OnFixedUpdate` or
   `OnLateUpdate`, but `OnCreate` and `OnDestroy` still run, and a contact that began before it was deactivated still
   ends with its Exit.

Strata's choice, in a `:::why` aside: no gameplay framework above the script lifecycle. Game code is script classes on
entities, and these patterns are plain C++ in them; the samples use all four. One sentence says that Strata has no game
AI (steering, pathfinding, navigation meshes, behaviour trees), so a guard is a state machine in a script, and links
`appendix/game-ai`, which holds the absence and the general techniques. Common mistakes: a flag for every state, a
pointer to another script kept across frames, destroying and creating what could be hidden, creating the pool again in
`OnReload`. The exercises: the guard's flags turned into a scoped enum with a `switch`; a pool of bullets made once and
switched with `SetActive`, done in a script; a design question on where a score that outlives a scene lives. At the end
the reader can choose a pattern for a growing script and recognize each pattern in the samples.

**Leaves out.**

- Timers, key repeat, and scripts that find each other → `make/timers-events`
- Animation state machines as game makers edit them → `make/animation`
- State that survives a scene switch → `make/levels-saves`
- Recipes built on these patterns (the coin, the grab tool, the sound budget) → `make/recipes`
- Game AI techniques in general → `appendix/game-ai`
- Tetris built whole, with its rules class → `make/project-tetris`
- The script lifecycle and its order → `make/script-loop`
- How the engine dispatches script updates → `scripting/script-system`

**Fit.** `fits`: about 5,400 words against L (5,000). The four patterns taught from zero for a reader who has written
only block A's scripts, with their three excerpts (about 2,550 words), take the most, then the problem and its naive
answers, the three diagrams (the guard's states, a manager and its callers, a pool's life), the three exercises, the
approaches table and the common mistakes.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:374` | code | home | `Samples/Tetris/Scripts/TetrisBoard.cpp:282-369`: `Refresh` and `ShowCell`, touching only what changed: the cached shown state, `SetActive`, the material by `SetProperty`, HUD texts rewritten only when their numbers changed |
| `new:2` | code | home | `Samples/ThirdPerson/Scripts/CourseState.h:7-39`: a manager, the course's state on its "Game" entity, which the coins call through `AddCoin`. No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `new:3` | code | home | `Samples/ThirdPerson/Scripts/PauseMenu.cpp:38-52`: a small state machine: one action moves between playing, paused and "settings open". No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `new:4` | not-done | link | No game AI: steering, pathfinding, navigation meshes and behaviour trees are left to scripts; the page says so in one sentence and links `appendix/game-ai`, the home of the absence. Evidence: `git grep -niE -e pathfind -e navmesh -e "nav mesh" -e "navigation mesh" -e "behaviou?r ?tree" -e steering 822a7a46 -- Strata/src StrataScriptCore` finds nothing (the word "navigation" alone matches only the game UI's focus navigation: `Strata/src/Strata/GameUI/`, `Strata/src/Strata/Input/UIActions.h`, `Strata/src/Strata/Scene/SceneServices.h`) |
| `new:17` | erratum | home | `Samples/Tetris/README.md:14` says that the sample's cells are "created and destroyed by a script"; the board creates its cells once and then only shows, hides and recolors them. Evidence: `Samples/Tetris/Scripts/TetrisBoard.cpp:222-247` (`CreateCells`, `CreateCell`), `:355-369` (`ShowCell`); `git grep -n Destroy 822a7a46 -- Samples/Tetris/Scripts` finds nothing |
| `new:18` | erratum | home | The gamedev survey says that inactive entities get nothing (`plan/inventory/gamedev.md:322`); they get no `OnUpdate`, `OnFixedUpdate` or `OnLateUpdate`, but `OnCreate` and `OnDestroy` run regardless, and a contact that began before the entity was deactivated still ends with its Exit. Evidence: `Strata/src/Strata/Scripting/ScriptSystem.cpp:276-280`; `Strata/src/Strata/Scripting/ScriptSystem.h:55-56`; `Strata/src/Strata/Scripting/ScriptSystem.cpp:664-679` (`RunPendingStarts` reads no activity); `StrataScriptCore/Include/StrataScript/Script.h:57-58` |
| `new:19` | hands-on | home | Exercises: the guard's three flags turned into a scoped enum with a `switch` (modify); a pool of 20 bullets made in `OnCreate` and switched with `SetActive`, against `Instantiate` and `Destroy` for every shot, done in a script; where a score that must outlive a scene switch lives (design). Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:51` (`SetActive`), `:59` (`Destroy`); `StrataScriptCore/Include/StrataScript/Scene.h:156-174` (`Instantiate`) |
| `gamedev:373` | code | use | The Tetris board making its cells once and finding them again in `OnReload` (its home is `make/project-tetris`) |
| `gamedev:372` | code | use | The Tetris rules class kept apart from the engine, named as a state kept in plain C++ (its home is `make/project-tetris`) |
| `scripting:385` | code | use | Lines 38-46 of `Coin.cpp`: a caller of the manager (its home is `make/recipes`) |
| `gamedev:321` | concept | use | The lifecycle's order: `OnCreate` after every script exists, updates parents first, destruction at the end of the frame (its home is `make/script-loop`) |
| `animation:283` | concept | link | State machines for animation, named as the data form of the same pattern (`animation/state-machines`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The script lifecycle and its order; destruction at the end of the frame | `make/script-loop` | must |
| Finding, spawning, hiding and destroying entities from a script | `make/scripting-scene` | must |
| Scripts that find each other each time; timers | `make/timers-events` | must |
| Scoped enum values and `switch` | `basics/programming-1` | must |
| `std::vector` and loops | `basics/programming-2` | must |
| Classes and member functions | `basics/programming-3` | must |
| Entity and asset fields set in the Inspector | `make/script-fields` | must |
| Prefabs | `make/prefabs` | must |
| Hot reload and `OnReload` | `make/first-script` | must |
| Contacts and triggers | `make/physics` | must |
| Animation controllers | `make/animation` | helps |

## `make/recipes` — Building blocks and recipes

**Covers.** A how-to of recipes taken from the samples. Each recipe says what it does, where its sample has it, the
numbered steps that add it to the reader's project, and what to change to make it one's own. It opens with `Random`:
`Range` for whole numbers (a die) and for decimals, `NextFloat`, `Chance`; a seed in a field gives the same sequence on
every computer, an unseeded generator always gives the same one, and a seed from something that varies (a level number)
gives variety; then a deterministic replay: seed from a field, record the outcomes, play again and get them again. Then
the recipes:

1. The coin (Third-Person `Coin.cpp`): spin and bob, collect once on a trigger tagged "Player", tell the manager, hide;
   `OnReload` calling `OnCreate` to find its model again.
2. The seeded pour (Physics Playground `SpawnBalls`): balls in a loose column, each nudged by `Random` from a seed, so
   the same seed pours the same pile; the call that makes them all at once, `Scene::InstantiateMany`, is given with its
   one line per transform, and `make/performance` teaches it.
3. The grab tool (Physics Playground `UpdateGrab`): a ray through the cursor, `Physics::Raycast` for the body under it,
   then a velocity toward a point in front of the camera, proportional to the distance and capped at 20 m/s, with the
   spin damped.
4. Impact sounds with a budget (Physics Playground `Impact.cpp`): the hit's strength from the bodies' speed along the
   contact's normal, volume and pitch from it, `Audio::PlayOneShotAt` at the contact point, and a token bucket shared by
   every body (at most 8 sounds in a frame and 16 a second on average), so a pour of hundreds of contacts plays a few
   voices. This finishes G12, the exercise of `make/gameplay-math`.

The Open World sample's day and night script (`DayNight.h`, hands-on G16) is a recipe of `make/reflections`, beside the
times of day with baked probes; one sentence names it and links there. The exercises, done in a script: the coin made to
come back after a delay with a `Timer`, and the pour seeded from the level number, so that each level pours its own
pile and the same level the same one. At the end the reader can use seeded randomness for variety and for replays, and
can take a recipe from a sample's script into a game and change it.

**Leaves out.**

- `Timer` and `KeyRepeat` → `make/timers-events`
- `Motion`, `LookAt`, `SmoothDamp` and the pointer ray → `make/gameplay-math`
- Probability, generators and seeds as mathematics → `basics/math-probability`
- Many instances in one call → `make/performance`
- A day and night cycle (`DayNight.h`, G16), and times of day with baked reflection probes → `make/reflections`
- Raycasts, masks and contacts → `make/physics`
- The Tetris board, its rules class and its seeded 7-bag → `make/project-tetris`

**Fit.** `fits`: about 4,700 words against L (5,000). Four recipes of about 700 to 800 words each (an introduction, an
excerpt, three steps with their results, what to change) and the `Random` section with its replay (about 800) take the
most; the day and night recipe is one sentence that links `make/reflections`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:385` | code | home | `Samples/ThirdPerson/Scripts/Coin.cpp:1-59`: a complete small game script: fields, `OnCreate` and `OnReload`, spin and bob in `OnUpdate`, `OnTriggerEnter` collecting once and calling `CourseState` |
| `gamedev:383` | code | home | `Samples/PhysicsPlayground/Scripts/Playground.cpp:223-275`: the grab, a velocity toward a target with a speed cap, and the seeded pour with `Random` jitter (its `InstantiateMany` line read as given) |
| `gamedev:384` | code | home | `Samples/PhysicsPlayground/Scripts/Impact.cpp:13-61`: the token bucket shared by every body, and the hit's strength from the velocities along the contact's normal |
| `gamedev:386` | code | link | The day and night script `DayNight.h`, named in one sentence (`make/reflections`) |
| `physics:450` | hands-on | home | The grab tool, built as `UpdateGrab` builds it |
| `gamedev:549` | hands-on | link | G16, the day and night script, named in the same sentence (`make/reflections`) |
| `scripting:527` | hands-on | home | A deterministic replay: `Random` seeded from a field, outcomes recorded and reproduced |
| `gamedev:663` | term | home | Seed |
| `gamedev:664` | term | home | Token bucket |
| `scripting:133` | feature | home | `Random` in the SDK: PCG32, the same on every platform, unbiased whole-number ranges by rejection; `reference/script-api` lists the declarations and links here |
| `scripting:343` | concept | home | Determinism helpers: a seeded generator gives the same sequence on every computer, which the replay builds on; the SDK's helpers (PCG32 with unbiased ranges, timers that keep their overshoot, critically damped smoothing) are compiled into the script module and behave the same everywhere; why they live in the module is `scripting/abi-sdk`'s |
| `new:20` | hands-on | home | Exercises, done in a script: the coin made to come back after a delay with a one-shot `Timer` (shown again with `SetActive`); the pour seeded from the level number, so that each level pours its own pile and the same level the same one. Evidence: `Samples/ThirdPerson/Scripts/Coin.cpp:1-59`; `StrataScriptCore/Include/StrataScript/Gameplay.h:23-110` (`Random`, its seed), `:115-176` (`Timer`); `StrataScriptCore/Include/StrataScript/Entity.h:51` |
| `physics:325` | code | use | The physics survey's excerpt of the same `UpdateGrab` (its home is `physics/queries`) |
| `gamedev:545` | hands-on | use | G12, whose impact sounds with a budget this page finishes (its home is `make/gameplay-math`) |
| `gamedev:387` | code | link | Times of day with baked probes switched with an overlap (`make/reflections`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Raycasts, velocities, triggers, contacts and their normals | `make/physics` | must |
| The pointer ray and the dot product | `make/gameplay-math` | must |
| One-shot sounds at a position, and asking for clips early | `make/sound` | must |
| Managers and state machines | `make/patterns` | must |
| Scripts that find each other each time | `make/timers-events` | must |
| Entity and asset fields set in the Inspector | `make/script-fields` | must |
| Opening a sample as a copy | `start/first-game` | must |
| Finding entities by tag and setting a property by name | `make/scripting-scene` | must |
| Variables outside a class, shared by every instance in the module | `make/levels-saves` | helps |
| Seeds, generators and uniform ranges as mathematics | `basics/math-probability` | helps |

**Starting state.** No checkpoint: each recipe opens its sample as a copy from the launcher (Third-Person for the coin,
Physics Playground for the pour, the grab and the impact sounds) to read the script at work, then adds it to a new
project from the Basic 3D template. The `Random` section starts in that new project.

**Command-only steps.** none

## `make/script-builds` — Building and shipping script modules

**Covers.** A how-to for the reader who wants to build the game's scripts outside the editor: from a terminal, from an
IDE, or with a library of someone else's. It starts with what a module is, at the use level, in two sentences and a
diagram: every `.cpp` and `.h` file under `Scripts/` is compiled into one shared library, which the editor and the
exported game load, and which talks to the engine through a C interface of version 1 that only grows, so that modules
keep loading across releases. Then the game's `CMakeLists.txt` as the editor writes it (`find_package` of the
`StrataScriptCore` package from the folder `STRATA_ENGINE_DIR` names, and `strata_add_script_module`), read line by line.
The numbered steps: open a terminal in the project's folder; configure the scripts with `cmake -S Scripts -B <build
folder> -DSTRATA_ENGINE_DIR=<Strata folder>`; build them with `cmake --build <build folder>`; watch the running editor
load the new module, as after its own build. Each command is given exactly, with what the terminal prints, per OS in
tabs. Then the IDE: open the `Scripts` folder in Visual Studio or in VS Code with the CMake Tools extension and pick the
"strata" preset that the editor wrote into `Scripts/CMakePresets.json`; build there; the editor hot reloads it; the
presets hold paths of this machine, so the project's `.gitignore` keeps them out of version control. Then what can go
wrong: other compilers (the same scripts built on another platform, and the warnings each compiler gives, such as a
missing include that one accepts and another refuses); a project in a deep folder on Windows, which builds in a folder of
the user data instead and is refused only when even that is too deep; and libraries: prefer static ones, and a shared
library the module links must sit next to the module on Windows or be found through its RUNPATH on Linux and macOS,
where `$ORIGIN` fails under hot reload because the editor runs a private copy. The exercise, done in a terminal and
the editor: a small static library of the reader's own, in a folder beside `Scripts` (sources under `Scripts` belong to
the module itself), linked with `target_link_libraries` after `strata_add_script_module`, called from a script, and hot
reloaded. At the end the reader can build the module by hand and in an IDE, read the build's folders, and add a
third-party library without breaking hot reload.

**Leaves out.**

- Building in the editor, the Problems panel and the crash toast → `make/first-script`
- How the editor finds a toolchain, configures and reports diagnostics → `editor/script-builds`
- Shared libraries and binary interfaces in depth → `scripting/shared-libraries`
- The C interface and the SDK inside → `scripting/abi-sdk`
- How modules load, and hot reload inside → `scripting/loading`, `scripting/hot-reload`
- The module shipped with the exported game → `make/export`
- Compiling, linking and CMake from zero → `basics/build`
- Building the engine itself from source → `core/first-change`

**Fit.** `fits`: about 2,800 words against M (3,000). Seven numbered steps with tabs per OS and what the terminal prints
(about 1,000 words) take the most, then the three rules with their reasons, the exercise, the excerpt of the generated
`CMakeLists.txt` and the module's diagram.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:124` | feature | home | The script module: every `.cpp` and `.h` under `Scripts/` compiled into one shared library through the `StrataScriptCore` package |
| `scripting:145` | feature | home | The package a game project finds: `find_package(StrataScriptCore CONFIG ... PATHS <Strata folder>/StrataScriptCore/CMake)`, glm with it, a `Dist` configuration |
| `gamedev:364` | code | home | `StrataEditor/src/Editor/ScriptProject.cpp:207-226`: the game's `CMakeLists.txt` as the editor writes it, with its comment on building by hand, to `find_package` and `strata_add_script_module` and the function's end |
| `gamedev:134` | feature | home | The code editor and IDE: the "strata" preset of `Scripts/CMakePresets.json` for Visual Studio, VS Code and clangd; an IDE's build hot reloads too |
| `gamedev:136` | feature | home | The long-path fallback: a deep project builds in `<user data>/Strata/Builds/<hash>` |
| `gamedev:521` | rule | home | Windows path length: deep folders build elsewhere, extremely deep ones are refused with a shorter folder named |
| `gamedev:137` | feature | home | The script interface is C, of version 1, its host functions only appended, so modules keep loading across releases |
| `gamedev:606` | term | home | ABI |
| `gamedev:410` | figure | home | The module boundary: game code, CMake, the shared library, the C table of host functions and class descriptions, the engine; hot reload swapping copies; the crash guard |
| `gamedev:524` | rule | home | Shared libraries a module links sit next to it, or are found through RUNPATH; `$ORIGIN` fails under hot reload |
| `scripting:144` | feature | use | `strata_add_script_module` and what it sets, in one sentence each |
| `scripting:143` | feature | use | `StrataScriptCore`, the headers and glm that a module builds against |
| `scripting:494` | rule | use | Hot reload runs a copy, so `$ORIGIN` points at the copy's folder |
| `scripting:596` | term | use | Module (script module) |
| `new:21` | hands-on | home | Exercise, done in a terminal and the editor: a small static library in a folder beside `Scripts`, linked to the module with `target_link_libraries(<module> PRIVATE <library>)` after `strata_add_script_module`, called from a script, built and hot reloaded. Evidence: `StrataScriptCore/CMake/StrataScriptModule.cmake:21` (`strata_add_script_module(target)`), `:89-90` (the module is a `MODULE` library target of that name); `StrataEditor/src/Editor/ScriptProject.cpp:213-215` (every `.cpp` and `.h` under the folder belongs to the module) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The terminal: a folder, a program with arguments, a quoted path, pasting a command | `start/install` | must |
| A code editor, and opening a folder in it | `start/install` | must |
| Building scripts in the editor, Ctrl+B, the Problems panel, hot reload | `make/first-script` | must |
| Files of code: headers and sources, compile errors | `basics/programming-3` | must |
| The project folder, its hidden `.strata` folder and file extensions | `make/project-files` | must |
| Compiling, linking, static and shared libraries, CMake | `basics/build` | helps |
| Environment variables and the user data folder | `basics/tools` | helps |
| Exporting a game | `make/export` | helps |

**Starting state.** A new project from the Basic 3D template whose `Scripts` folder holds the generated `Spinner`
script, built once in the editor (as `start/first-game` did); no checkpoint.

**Command-only steps.** none

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

## `make/animation` — Animation for game makers

**Covers.** A tutorial: the player of `make/characters-cameras` becomes the Third-Person sample's robot, which idles,
walks, runs, jumps, steps with sounds and holds a flag. It opens with the words, each from zero and on the robot: a
skeleton of joints, clips that move them, a skin that bends the mesh with them; an animator that plays an animation
controller, a state machine of states, transitions, parameters (float, bool, trigger) and cross-fades. The step
sections, each ending in a checkpoint:

1. What the import made: the robot's model was imported into the checkpoint; placed under the player, its root has an
   `Animator`, and the model's skeleton, clips and skin are sub-assets. In edit mode it stands in its rest pose; the
   Scene view's camera chip shows the first frame of its clip instead. Its morph targets (the face) are not imported.
2. The controller: the checkpoint holds `Animations/Player.stanimator`, made by the command
   `animation.createController`, because no menu or button makes one (one sentence and a link to `make/commands`, where
   the command is run). The steps assign it to the Animator's Controller field, play, and watch the Inspector's live
   state: the state, `from -> to` during a fade, the normalized time and the parameters. The robot's own controller is
   read as data, its parameters, states and footstep events. The step's "If you do not see it" reads the table of
   `animation/system` of what a character shows while something is missing: the bind pose until the skeleton, the
   controller and the clips are in (for good, with one warning, when the skeleton does not load), the component's Clip
   when the controller does not load, the rest pose for a state whose clip does not load.
3. Walk and run: in the Asset tab, **Add Parameter** (Speed), **Add State** (Walk, Run, each with its clip) and **Add
   Transition** (Idle to Walk on `Speed > 0.1`, Walk to Run, and back), with the condition text; a cross-fade's duration.
   The pitfall: a transition with no condition and no exit time fires in the first update of its state, so that state
   hardly plays.
4. Drive it from the script: `GetAnimator()` and `SetFloat("Speed", ...)` and `SetBool("Grounded", ...)` from the
   controller's velocity, every frame, as the Third-Person player does.
5. Jump from any state: a trigger parameter, a transition from Any State on it, an exit time back to Idle; a trigger
   stays set until a transition uses it.
6. Footsteps: Footstep events on the Walk and Run states, and a `Footsteps` script on the robot, the entity with the
   Animator, as the sample has it, whose `OnAnimationEvent` plays one of four step sounds at the robot with a random
   pitch. Only the scripts on the animator's own entity receive its events, so the same script on the player hears
   nothing, and nothing warns. The pitfall: an event whose time is past its clip's duration never fires, and nothing
   warns.
7. Hold a flag: an `AttachToJoint` component keeps an entity on the hand's joint. It writes the entity's translation,
   rotation and scale every update, so the step builds a holder and its child, as the sample does: the holder is
   attached with no offset, and the flag under it carries the offset, the turn and the scale. The Joint field is a typed
   name that nothing checks: a misspelt name leaves the entity where it is, with no warning. Then the same in a script
   with `GetJointTransform`, and why the component is the better choice: a script reads the previous update's pose,
   since Animation runs after Scripting. A joint that gameplay reads also depends on the camera, unlike time, events
   and root motion: while a WhenVisible animator is unseen, it is a stale pose.
8. Root motion: the move of a clip reaches a character controller only on the animator's own entity, and the course's
   robot sits under the player, as in the sample. So the step places a second robot in the course and gives its root,
   the entity with the Animator, a `CharacterController`; with `ApplyRootMotion` on, the controller walks what the clip
   travels and collides as it walks. The step's "If you do not see it" is the drift: `ApplyRootMotion` on the player's
   robot moves the model away from its capsule, through walls, while the capsule stays. Then when to leave it off and let
   the script move the character, as the Third-Person sample does.
9. Animate only what is seen: the Animator's culling mode, WhenVisible, on the second robot, with the follow camera
   turned away from it and back, and what the robot does meanwhile. The player's robot cannot show it: the follow
   camera always looks at it, so it is always seen.

It ends with what Strata's animation does not do (blend trees, animation layers, IK, morph targets, clip compression) and
links `animation/limits`. The exercise, done in the editor, is G8 on the page's robot: a Crouch state on a bool, edited
in the Asset tab and undone. At the end the reader can bring a rigged model into a game, give it a controller, drive it
from a script and react to its events.

**Leaves out.**

- Importing models and their settings in general → `make/assets`
- Skeletons, clips and skinning as the engine does them → `animation/skeletons`, `animation/clips`, `animation/skinning`
- State machines, cross-fades, events and root motion inside → `animation/state-machines`, `animation/blending`,
  `animation/time-events`, `animation/root-motion`
- Showing a pose without playing (`animation.preview` and its chip) → `make/commands`
- Running `animation.createController` → `make/commands`
- Measuring many animated characters → `make/performance`
- The character controller and the follow camera → `make/characters-cameras`
- Everything Strata's animation does not do, in full → `animation/limits`

**Fit.** `over`: about 7,600 words against L (5,000). The words of animation for a reader who has none (about 1,500)
and nine step sections of about 25 steps (about 4,900 words with their three excerpts, rules, pitfalls and figures)
reach L's top; the next size is XL (8,000) by S2, and the split of the earlier line stays the other way:
`make/animation` "Animation for game makers: models, controllers and parameters" (sections 1 to 5 and 9) and
`make/animation-events` "Animation events, attachments and root motion" (sections 6 to 8). The wave 8 animation graph is
not at the pin (`plan/inventory/gamedev.md:174`); the page describes the controller of 822a7a46 only.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:335` | concept | home | Animation for makers: skeletons, clips, state machines, parameters against triggers, cross-fades, events, root motion, attachments; the mistakes of setting a trigger every frame and of feet that slide |
| `gamedev:167-172` | feature | home | The import of a skinned glTF (the root becomes an Animator); `.stanimator` controllers with parameters, states and transitions; the script API; `AttachToJoint`, root motion and the culling mode; the rest pose and first frame in edit mode; what is not imported (morph targets) |
| `gamedev:630-635` | term | home | Skeleton, joint, clip, skin; animator, animation controller, state, transition, parameter, trigger parameter; cross-fade; animation event; root motion; `AttachToJoint` |
| `animation:177` | feature | home | The SDK's `Animator`, from `Entity::GetAnimator()`: parameters, play and cross-fade, the current state, normalized time, joints |
| `animation:191` | feature | home | The Asset tab's views: the skeleton's joints, a clip's channels, and the controller as tables with **Add Parameter**, **Add State** and **Add Transition** and the condition and event texts |
| `animation:192` | feature | home | The Inspector's live state while playing: the state, `from -> to` during a fade, normalized time, parameters |
| `gamedev:381` | code | home | `Samples/ThirdPerson/Assets/Animations/Robot.stanimator:1-51`: a controller as data: its five parameters, the Idle state, and the Walk state with its two Footstep events |
| `animation:363` | code | home | `Samples/ThirdPerson/Scripts/Footsteps.cpp:12-42`: `OnAnimationEvent` playing one of four clips with a random pitch, the clips asked for in `OnCreate`; with `ThirdPersonPlayer.cpp` 129-133, where the player sets Speed and Grounded each frame |
| `animation:514-519` | hands-on | home | G1 to G6: import and rest pose, a two-state controller driven by Speed, footstep events, an any-state jump with exit times, a flag on a joint, root motion with and without a character controller |
| `animation:521` | hands-on | home | G8, the page's exercise, done on its robot: a Crouch state on a bool, edited in the Asset tab and undone |
| `audio-input:559` | hands-on | home | Footsteps from animation events, with a random pitch |
| `render-scene:561` | hands-on | home | The culling mode WhenVisible on a second robot placed in the course: turn the follow camera away from it and back, and watch the pose catch up (the player's robot is always in view, so it cannot show this) |
| `new:5` | not-done | home | No blend trees, animation layers, IK, morph targets or clip compression. Evidence: `git grep -nilE -e "blend ?tree" -e "inverse kinematics" -e morph -e compress 822a7a46 -- Strata/src/Strata/Animation` finds nothing; `Strata/src/Strata/Asset/GltfImporter.cpp:1031` (weight channels skipped); `Docs/Roadmap.md:1649-1652` |
| `new:6` | not-done | home | No menu or button creates an animation controller; only the command `animation.createController` does. Evidence: `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153`; the Content Browser's New menu makes folders, materials, worlds and scripts only (`StrataEditor/src/Panels/ContentBrowserPanel.cpp:564-580`); `git grep -n "createController" 822a7a46 -- StrataEditor/src` finds only `EditorAnimationCommands.cpp` |
| `new:25` | rule | home | Root motion walks a character controller only when the Animator and the `CharacterController` are on one entity; otherwise the move is written to the animator's own transform, and a model under its player leaves the capsule. Step 8 is done on a second robot whose root carries the controller, with the drift as its "If you do not see it". Evidence: `Strata/src/Strata/Animation/AnimationSystem.cpp:801-826` (`AddCharacterMotion(animator, move)`, else the animator's transform moves); `Strata/src/Strata/Physics/CharacterControllers.cpp:816-822, 1050-1056` (the controller is looked up on that entity alone); `Samples/ThirdPerson/Assets/Scenes/Course.stscene:151-152` (Player with the CharacterController, Robot with the Animator as its child) |
| `new:34` | rule | home | Step 7: `AttachToJoint` writes the entity's translation, rotation and scale every update, so an offset, a turn or a scale goes on a child: the holder is attached with no offset, and the flag under it carries the offset, the turn and the scale, as the sample's FlagHolder and Flag do. The Joint field is a typed name that nothing checks: a misspelt name leaves the entity where it is, with no warning. Evidence: `Strata/src/Strata/Animation/AnimationComponents.h:39-45` (the world transform becomes the animator's times the joint's; children keep their offsets); `Strata/src/Strata/Animation/AnimationSystem.cpp:849-851` (a joint the skeleton lacks is skipped, and nothing is logged), `:877-880` (the three fields written); `Strata/src/Strata/Animation/AnimationComponents.cpp:52` (Joint, a plain text property); `Samples/ThirdPerson/Assets/Scenes/MainMenu.stscene:72-73` (FlagHolder on `Palm2.R` with an identity transform; its child Flag with the offset, the turn and the scale 0.035) |
| `new:35` | rule | home | The pitfall lines of steps 3 and 6: a transition with no condition and no exit time fires in the first update of its source state, so that state hardly plays; an event whose time is past its clip's duration never fires, and nothing warns (the internals are on `animation/state-machines` and `animation/time-events`). Evidence: `Strata/src/Strata/Animation/AnimationController.h:77-80` ("None: it fires as soon as they hold"); `Strata/src/Strata/Animation/AnimatorInstance.cpp:426-444` (no condition holds as all conditions holding), `:734-737` (no exit time counts as reached), `:480-503` (an event fires when the playhead crosses its time), `:505-511` (a clip that does not loop stops at its duration), `:514-516` (a looping one wraps there); `Strata/src/Strata/Animation/AnimationController.cpp:187-188` (validation refuses only a negative or non-finite time) |
| `animation:74` | feature | use | `AnimatorComponent`'s fields (Skeleton, Controller, Clip, Speed, Loop, Play On Start, Apply Root Motion, Culling Mode) |
| `animation:76` | feature | use | `AnimatorCullingMode`: AlwaysAnimate and WhenVisible |
| `animation:78` | feature | use | `AttachToJointComponent` |
| `animation:84-88` | feature | use | Simple mode against a state machine; conditions; triggers consumed; exit times |
| `animation:90` | feature | use | Cross-fades |
| `animation:97-98` | feature | use | Events; the rest pose when nothing plays; with the table of `animation/system` of what a character shows while its skeleton, controller or clips are missing, which step 2's "If you do not see it" reads |
| `animation:178` | feature | use | `OnAnimationEvent` reaches only the active scripts on the animator's own entity, so `Footsteps` goes on the robot (its home is `scripting/script-system`) |
| `animation:111` | feature | use | Root motion through a character controller |
| `animation:129` | feature | use | WhenVisible culling, in a game maker's words, shown on the second robot of step 9 |
| `animation:450` | rule | use | WhenVisible keeps time, events, transitions and root motion but not the pose: in step 7, a joint that gameplay reads while the animator is unseen is a stale pose, placed at the entity's current transform, and a script reads the previous update's pose, since Animation runs after Scripting (both beside this rule on `animation/culling`) |
| `animation:166-167` | feature | use | Rest poses and the first frame of the clip in edit mode |
| `animation:185` | feature | use | `animation.createController`, the command that made the checkpoint's controller |
| `animation:212` | feature | use | The Third-Person robot: its model and licence, its controller and its scripts |
| `animation:283` | concept | use | State machines for animation (their home is `animation/state-machines`) |
| `animation:296` | concept | use | Animation events |
| `animation:300` | concept | use | Root motion |
| `animation:305` | concept | use | Attachments (sockets) |
| `animation:387`, `gamedev:422` | figure | use | The robot's controller as a state machine: Idle, Walk and Run on Speed, Jump from any state on a trigger, Wave and Dance, the Footstep event times. One file, drawn once and homed on `animation/state-machines`, which this page shows (R34, D42); gamedev figure 14 is the same figure |
| `animation:416` | figure | use | The Inspector of the playing robot during a fade |
| `animation:418`, `gamedev:458` | figure | use | The controller's tables in the Asset tab with `Robot.stanimator` open. One screenshot, taken once and homed on `animation/state-machines`, which this page shows (R34, D42); gamedev screenshot 20 is the same picture. The robot's pose is shown in play mode, since a pose preview needs a command (`make/commands`) |
| `animation:421` | figure | use | The menu robot holding the flag |
| `animation:485` | rule | use | Triggers stay set until consumed |
| `animation:487` | rule | use | A walk-to-run cross-fade without phase matching slides the feet |
| `scripting:128` | feature | home | `Animator` and `JointTransform` in the SDK, one entry with `animation:177`: states, clips, cross-fade, parameters, speed, state queries, joints; `reference/script-api` lists the declarations and links here |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Importing a glTF model; sub-assets | `make/assets` | must |
| Models as entity templates; placing a model in the scene | `make/prefabs` | must |
| The character controller and the player's script | `make/characters-cameras` | must |
| Input actions in a script | `make/input` | must |
| One-shot sounds at a position, and asking for clips early | `make/sound` | must |
| Asset fields set in the Inspector | `make/script-fields` | must |
| Reading JSON | `start/how-to-read` | must |
| Undo | `make/project-files` | must |
| Random numbers in a range | `make/recipes` | helps |
| Running a command | `make/commands` | helps |

**Starting state.** A downloadable checkpoint of the obstacle course: the end checkpoint of `make/characters-cameras`
(the course, the player and the follow camera), with three additions made for this page: the
Third-Person sample's robot (`RobotExpressive.glb`, CC0, Tomás Laulhé (Quaternius), modified by Don McCurdy) imported,
its four footstep sounds (Kenney, CC0) imported, and `Animations/Player.stanimator`, a minimal controller made by
`animation.createController` (one state, Idle, playing the robot's Idle clip; no parameters), which the reader edits in the
Asset tab. The page says in one sentence that a command made the controller.

**Command-only steps.** none

## `make/menus` — Menus: buttons, navigation, pause and settings screens

**Covers.** A tutorial: the course of `make/animation` gets a main menu, a pause menu, a settings screen, a rebinding
screen and a name field. It opens with how a widget reaches a script: a button, toggle, slider or input field calls the
scripts on its own entity and then those on its Event Target, before the frame's `OnUpdate`, so that one menu script
handles a whole menu. The step sections, each ending in a checkpoint:

1. A main menu scene: a new scene with a canvas and no camera, a panel with a vertical layout group, a title and three
   buttons from the Hierarchy's **+ > UI** presets. A scene without a camera shows its UI over black.
2. Make the buttons work: a `MainMenu` script (the Manual's example), the buttons' Event Target set to its entity,
   `OnUIClick` telling the buttons apart; Play switches to the course with `Game::LoadScene` and Quit ends the game with
   `Game::Quit`, one line each, given with a link to `make/levels-saves`, which teaches scene switches.
3. Keyboard and gamepad: the canvas's First Selected, the focus, navigation with the UI map's Submit, Cancel and four
   directions (rebindable, and repeating when held), the states a selectable shows (normal, hover, pressed, focused,
   disabled). Nothing shows focus until the first press, which only focuses (Submit clicks nothing yet); without First
   Selected the start is the top-left selectable, so the menu sets First Selected or calls `Focus()` when it opens.
4. A pause menu at time scale 0: a Pause action, a panel on a canvas of its own in the course, `Time::SetTimeScale(0)`,
   the cursor freed and the focus put on Resume; Resume undoes it. The pause canvas's Sort Order is above that of the
   game's other canvases, such as a HUD, so that it draws over them and takes the input first, as the sample's Menus
   canvas (10) does over its HUD (0). The UI keeps fading and repeating at time scale 0 because it runs on unscaled
   time, and so must anything a pause menu animates; the excerpt is the Third-Person pause menu. A test that taps the
   paused menu through simulated input still sees its taps end, since they count the frames a game updates at time
   scale 0 as well as its fixed steps (`editor/stepping`).
5. A settings screen, made a prefab and placed in both scenes: a volume slider whose `OnUIValueChanged` calls
   `Audio::SetMasterVolume`, a toggle group for the window mode (Windowed, Borderless, Fullscreen) that acts only on a
   toggle's value 1, with one sentence on what the modes do (Fullscreen switches the display to the resolution asked
   for, Borderless covers the display at the desktop's mode without a switch, Windowed restores the last windowed place
   and size, and a game whose manifest says Fullscreen starts Borderless), and a vsync toggle; values set from code raise
   no events, so showing the current values triggers nothing. In the editor's play mode the window requests are only
   recorded and shown over the Game view; the exported game applies them between frames. The settings last for the
   session; `make/levels-saves` keeps them for the next, and `make/quality` adds the Graphics row.
6. A rebinding screen: one row per action with its bindings as text (`Input::GetActionBindings`), whose key names are
   those of the keys' US positions, since a game's key names do not follow the player's keyboard layout; a button that
   listens for the next control (`BeginBindingCapture`, then `PollBindingCapture` every frame, `CancelBindingCapture`
   after a timeout); `SetActionBindings`; `SaveBindings` when the screen closes; and Reset to defaults. While it listens
   no action reacts, so the key pressed does not also close the menu. In the editor the players' bindings are kept in the
   project's `.strata/Saves` folder, and the Input Actions page marks them "In play".
7. A name field: an Input Field with a placeholder and a character limit; `OnUISubmit` when the player presses Enter,
   the text read with `GetUI().GetText()` and shown on the HUD; while the field is edited the keyboard is the UI's.
8. Scrolling credits: the main menu's credits move inside a mask, on unscaled time, as the Third-Person main menu's do.
9. A sign in the world: a world-space canvas on a wall with a button that the player clicks through the game camera.
   The Scene view's 2D canvas mode edits screen-space canvases only, so the sign is laid out in the viewport, or turned
   to Screen Space while it is built.

It ends with what game UI does not have (scroll views, drop-downs, rich text, multi-line fields; localization and
right-to-left text; key names that follow the player's keyboard layout), linking `appendix/not-in-strata`. The
exercises extend the menus: a confirmation panel on Quit that takes the focus when it opens and that Cancel closes, and
a Back button on the settings screen. At the end the reader can build menus that work with a mouse, a keyboard and a
gamepad, pause a game, and let players change their volume, window and controls.

**Leaves out.**

- Canvases, rects, anchors, images and text, and a HUD → `make/hud`
- Scene switches, loading screens and saving the settings for the next run → `make/levels-saves`
- The Graphics row and players' graphics options → `make/quality`
- How widgets, focus, navigation and events work inside → `ui/input`
- Text fields and typed text inside → `ui/text`
- The UI map and its key repeat inside → `input/actions`
- The players' bindings file and capture inside → `input/rebinding`
- Building and testing a menu through commands → `make/automated-playtests`

**Fit.** `over`: about 6,850 words against L (5,000). Nine step sections of about 29 steps (about 5,400 words with
their two excerpts, rules and figures), the opening on how a widget reaches a script and the exercises reach L's top.
The next size is XL (8,000) by S2; the split of the earlier line stays the other way: `make/menus` "Menus: buttons,
navigation, pause and settings screens" (sections 1 to 5, 8 and 9) and `make/rebinding` "Controls players can change: a
rebinding screen and a name field" (sections 6 and 7).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:185` | feature | home | The widgets and navigation of game UI for a maker: selectable states, buttons, toggles in groups, sliders, input fields, layout groups and masks, the **+ > UI** presets, navigation through the UI map, pause menus at time scale 0, the pause canvas's Sort Order above the other canvases' so that it draws over them and takes the input first, a main menu scene with no camera (canvases, rects, images and text are `make/hud`'s) |
| `gamedev:204` | feature | home | The window from a script: `Game::SetWindowMode` (Windowed, Fullscreen, Borderless), `SetResolution`, `SetVSync`, `GetWindowSize`; the editor records the requests |
| `gamedev:145` | feature | home | Player rebinding: `GetActionBindings`, `SetActionBindings`, `ResetActionBindings`, `SaveBindings` and binding capture; saved per player; "In play" and Reset Player Bindings on the Input Actions page |
| `gamedev:426` | figure | home | UI event routing: a widget, its own scripts, then its Event Target's scripts, before `OnUpdate` |
| `gamedev:520` | rule | home | In a toggle group act only on value 1 |
| `gamedev:543` | hands-on | home | G10: the main menu scene without a camera, the settings screen with a volume slider, the pause menu at time scale 0; its Graphics row is `make/quality`'s and its best score `make/levels-saves`' |
| `gamedev:547` | hands-on | home | G14: the rebinding screen: list, capture, save, reset |
| `gamedev:641-644` | term | home | Layout group and mask; selectable, focus and navigation; event target; toggle group |
| `gamedev:646` | term | home | Rebinding and binding capture |
| `gameui:381` | concept | home | Scaled against unscaled time for a pause menu; the mistake of animating it with `Time::GetDeltaTime()` |
| `gameui:425` | code | home | `Docs/Manual/GameUI.md:69-87`: the Manual's `MainMenu`: `OnUIClick` telling buttons apart by name, `OnUIValueChanged` for a volume slider |
| `new:9` | code | home | `Samples/ThirdPerson/Scripts/PauseMenu.cpp:97-122`: pause and resume: the time scale, the panel, the focus and the cursor. No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `gameui:492` | figure | home | A toggle group and a slider with its fill and handle at two values, from the page's settings screen |
| `gameui:500` | figure | home | A main menu scene without a camera, its UI over black (its capture waits for the check `new:26`) |
| `gameui:733` | open | home | Settled at the pin: the Third-Person `MainMenu.stscene` has a primary camera, so the picture over black is made from the page's own main menu scene, which has none |
| `gameui:571` | hands-on | home | The first menu: canvas, panel, vertical layout, title and buttons, a `MainMenu` script through the Event Target, a scene without a camera |
| `gameui:577` | hands-on | home | The pause menu at time scale 0, with a volume slider and gamepad navigation from First Selected |
| `foundation:540` | hands-on | home | The same task as the foundation survey gives it: time scale 0 for a pause menu, and a fade driven by the unscaled delta |
| `gameui:580` | hands-on | home | The settings screen: a toggle group, sliders and a name field with `OnUISubmit` |
| `gameui:582` | hands-on | home | Scrolling credits inside a mask |
| `gameui:584` | hands-on | home | A sign in the world: a world-space canvas whose button is clicked through the game camera, laid out in the viewport or turned to Screen Space while it is built, since the 2D canvas mode edits screen-space canvases only |
| `scripting:442` | figure | home | The page's settings screen with its rebinding row capturing a control (the Graphics row appears on `make/quality`) |
| `scripting:520` | hands-on | home | The pause and settings menu: time scale 0, unscaled time, `OnUIClick`, a rebinding row with capture; the graphics preset row is `make/quality`'s |
| `audio-input:570` | hands-on | home | The rebinding menu: bindings listed, capture with a timeout, `SetActionBindings`, `SaveBindings`, reset; "In play" in the editor |
| `new:7` | not-done | home | No scroll views, drop-downs, rich text or multi-line input fields: a mask clips a scrolling list, and an input field is one line. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.cpp:211-397` registers no such component; `Strata/src/Strata/GameUI/GameUIComponents.h:255-260, 272-273` |
| `new:8` | erratum | home | The UI map's default bindings are those of `Strata/src/Strata/Input/InputActionSet.cpp:147-152`: Submit is Enter, keypad Enter, Space or gamepad A; Cancel is Escape or gamepad B; the directions are the arrows, the d-pad and the left stick. Evidence: the comment at `Strata/src/Strata/Input/UIActions.h:12-13` gives Enter, Escape and the arrows and leaves out keypad Enter and Space; `StrataScriptCore/Include/StrataScript/UI.h:17-18` agrees with the code |
| `new:26` | open | home | Check: A capture of the Game view without a camera. The claim: the figure `gameui:500` is taken from the page's own main menu scene, which has no camera, as the Game view shows it, its UI over black, with a live `viewport.capture` of the Game view (`live`, `camera` "scene"), which reads back the frame that view rendered; a capture that is not live resolves its view without that fallback and finds no camera. The photographer runs it, and the page's brief waits for the result (R39). Evidence: the Game view's fallback, `StrataEditor/src/Panels/GameViewPanel.cpp:112-116` and `StrataEditor/src/Editor/ViewportRenderer.cpp:72-86`; the live capture reads the Game view's renderer, `StrataEditor/src/Editor/EditorViewportCommands.cpp:516-520, 538-555`; the capture that is not live, `StrataEditor/src/Editor/EditorViewportCommands.cpp:430-433` and `StrataEditor/src/Editor/ViewportRenderer.h:58-61` (nullopt for the Game view without a camera) |
| `new:27` | not-done | home | Key names that follow the player's keyboard layout: a game shows a key's name by its US position, so the rebinding screen of step 6 does too; only the editor's shortcuts follow the layout. Evidence: `Docs/Releases/0.7.0.md:361-362`; `git grep -n GetLayoutKey 822a7a46 -- Strata/src StrataScriptCore` finds only the window's own code (`Strata/src/Platform/GLFW/GLFWWindow.cpp:626`, `GLFWWindow.h:48`, `Strata/src/Strata/Core/Window.h:117`) and the ImGui platform's (`Strata/src/Strata/ImGui/ImGuiPlatform.cpp:180` and a comment of its header) |
| `new:28` | not-done | home | Localization and right-to-left text: a menu's texts are the strings its elements hold, in one language and written left to right. Evidence: `Docs/Releases/0.7.0.md:415` (localization among what the release does not have); `Docs/Roadmap.md:1713`; `git grep -niE -e "locali[sz]" -e "right-to-left" 822a7a46 -- Strata/src StrataScriptCore` finds nothing |
| `new:29` | erratum | home | The game UI survey's mistake "a menu unusable with a gamepad because nothing is focused" (`plan/inventory/gameui.md:369-370`) is wrong: with nothing focused, the first direction press or Submit focuses the topmost input canvas's First Selected, else its top-left selectable; the menu works, and that first press only focuses. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:526-531, 539-542` (no focus: `Focus(FindStartSelectable(...))`), `:769-807` |
| `new:30` | hands-on | home | Exercises (make it yours), done in the editor and in a script: a confirmation panel on Quit whose No button takes the focus when it opens and which the UI map's Cancel closes; a Back button on the settings screen. Evidence: `StrataScriptCore/Include/StrataScript/UI.h:123-127` (`UIElement::Focus`), `:165-169` (`UI::IsActionPressed`) |
| `gameui:59-62` | feature | use | `UISelectable`, `UIButton`, `UIToggle` (and its group) and `UISlider`, in a maker's words (their home is `ui/input`) |
| `gameui:63-65` | feature | use | `UILayout`, `UIInputField` and `UIMask` |
| `gameui:145` | feature | use | A scene with no camera but with screen UI shows the UI over black |
| `gameui:182` | feature | use | Toggles flip, groups are exclusive, switching the one that is on off does nothing |
| `gameui:185-190` | feature | use | The UI map, the start of navigation, automatic navigation, slider steps, Submit and Cancel, visual states and their fades on unscaled time |
| `gameui:201-206` | feature | use | The four callbacks, dispatch to the widget's scripts then the Event Target's, and the SDK's `UIElement` and `UI` |
| `gameui:226` | feature | use | The Third-Person main menu, the model the page's menu follows |
| `gameui:363` | concept | use | Widgets as state machines: the states by priority, click on release, toggle groups |
| `gameui:367` | concept | use | Focus and navigation for keyboard and gamepad; with nothing focused the first press only focuses, so the menu sets First Selected or calls `Focus()` when it opens (the survey's "unusable" is corrected by `new:29`) |
| `gameui:372` | concept | use | Text input in a field |
| `gameui:376` | concept | use | Events that decouple game logic from widgets |
| `gameui:423` | code | use | The Third-Person `MainMenu.cpp`: focus on create, Cancel, credits scrolled in their mask (its home is `ui/input`) |
| `gameui:539` | rule | use | The UI runs on unscaled time |
| `gameui:543` | rule | use | Values set from code raise no events |
| `gameui:545` | rule | use | Read navigation through the UI map, not raw keys |
| `gameui:554` | rule | use | Keep the field's text element a `UIText` and give the field a `UIMask` |
| `gamedev:380` | code | use | The comment of `SettingsMenu.cpp` on a toggle group's 0 events (its home is `make/quality`) |
| `gamedev:198-199` | feature | use | `Game::LoadScene` and `Game::Quit`, one line each for Play and Quit (their home is `make/levels-saves`) |
| `audio-input:162` | feature | use | The players' bindings, kept apart from the project's |
| `audio-input:165-166` | feature | use | Binding capture; the UI actions and their repeat |
| `audio-input:458` | figure | use | Binding capture as a state machine, the idea behind the page's capture button |
| `audio-input:478` | figure | use | "In play" markers and Reset Player Bindings on the Input Actions page |
| `audio-input:525` | rule | use | Gameplay reads rebindable controls as input actions |
| `audio-input:533` | rule | use | A capture's press triggers nothing |
| `scripting:122` | feature | use | `Input`'s binding capture and its rebinding functions |
| `scripting:129` | feature | use | `Game`'s window functions |
| `scripting:131` | feature | use | `UIElement`, `UI` and `UIAction` |
| `scripting:338` | concept | use | Player-facing systems: rebindable input, the window applied after the frame |
| `worlds-runtime:91` | feature | use | The game window from scripts, through `IGameWindow` |
| `worlds-runtime:449` | rule | use | Window changes apply between frames, and only when they change something |
| `foundation:80` | feature | use | One sentence of the window modes' contract beside the window-mode toggle of step 5: Fullscreen switches the display to the resolution asked for, Borderless covers the display at the desktop's mode, Windowed restores the last windowed place and size, and a Fullscreen manifest starts Borderless (its home is `core/windows-events`) |
| `gameui:219` | feature | link | The 2D canvas mode edits screen-space canvases only, which step 9 meets (its home is `editor-ui/scene-view`) |
| `audio-input:521` | rule | link | Simulated taps on the paused menu of step 4 end, since the input step count adds the frames a game updates at time scale 0 to its fixed steps (`EditorContext::GetInputStepCount`, taught on `editor/stepping`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Canvases, rects, anchors, images and text; the Hierarchy's UI presets | `make/hud` | must |
| Time scale, unscaled time, and scripts that find each other | `make/timers-events` | must |
| Entity and asset fields set in the Inspector | `make/script-fields` | must |
| Input actions, their bindings and the Input Actions page | `make/input` | must |
| Making a scene and opening it | `make/scenes-entities` | must |
| Prefabs and their instances | `make/prefabs` | must |
| Master volume and one-shot sounds | `make/sound` | must |
| `std::string`, `std::vector` and `std::optional` | `basics/programming-3` | must |
| Scene switches and quitting | `make/levels-saves` | helps |
| The exported game, where the window changes show | `make/export` | helps |
| Players' graphics options | `make/quality` | helps |

**Starting state.** The end checkpoint of `make/animation`, downloadable: the course with the animated robot as the
player and the follow camera. The steps add a Pause action to the Gameplay map, as `make/input` taught.

**Command-only steps.** none

## `make/levels-saves` — Levels, loading screens and save files

**Covers.** A how-to that turns the course of `make/menus` into a game with levels, a loading screen and save files.
Game flow comes first, in a few sentences and the Third-Person sample's scene flow: a game is scenes (a main menu, a
loading scene, levels) and the moves between them, and what must outlive a scene has to be kept somewhere else, because
no entity survives `Game::LoadScene`. The numbered steps, by goal:

1. Levels: a second course; a goal trigger whose script holds the next level in a scene field and calls
   `Game::LoadScene`; a fall that restarts with `Game::ReloadScene`; a button back to the main menu. A switch loads the next
   scene in the background while the current one goes on, then swaps them between frames; asking again for the scene
   that is loading changes nothing.
2. State between scenes: variables at namespace scope in the script module stay while the game switches scenes; the
   Third-Person sample keeps its settings and its attract mode there (`ThirdPerson.h`), and its main menu starts the
   attract mode, the course playing itself, after ten idle seconds. Such state lives as long as the module's library is
   loaded: in the editor it carries over from one Play to the next, because the module unloads only when the project
   closes; every hot reload, and every reload after a crash, starts it over; an exported game starts it fresh at each
   run. So in the editor a score or a "settings read" flag kept there survives Stop and Play.
3. A loading bar: `Game::GetSceneLoadProgress` on a filled image and a text while the next level loads (the sample's
   `LoadingScreen.cpp`); then the start scene (**File > Set as Start Scene**) and the loading scene that an exported
   game plays while its start scene loads (Project Settings > Game). How fast the bar fills is bounded by the frame's
   upload budgets, which a game cannot raise for its loading screen; one sentence links `assets/uploads`, which explains
   the budgets and the staging bound.
4. A part of a level loaded beside it: `Scene::LoadAdditive` of a room's scene, `Assets::GetLoadProgress` on a bar,
   `SubScene::IsLoaded`, and `Unload`, which takes the room out at once and destroys it over the next frames; a
   sub-scene keeps the IDs of its file, so the same one cannot be loaded twice.
5. Save files: the best time written with `Game::WriteSaveFile` as one value per line (`std::to_string`) and read back
   with `Game::ReadSaveText` (a `std::optional`, empty when there is no file yet) and `std::stoi`, with the page's exact
   code, and checked, because a file can be missing or damaged; names of 1 to 64 safe characters; where the files are
   (the project's `.strata/Saves` in the editor, `<user data>/<Game>/Saves` for the exported game, the folder named after
   the project's name and not its title, so a rename keeps the saves); `ListSaveFiles` and `DeleteSaveFile`; a write
   replaces the whole file and waits for the disk, so a game saves at quiet moments (a checkpoint, a menu).
6. Settings that last: the settings of `make/menus` written to a save file when they change and read once into module
   state, as the sample's `GetSettings` does; the rebinding screen's bindings are kept by the engine already.
7. A checkpoint save: the position and the coins at a checkpoint, saved and loaded on the next start. In a world, the
   player stays in the saved scene with its streaming source, and a restored position is prefetched before the player
   is placed there, since a world starts with the cells around its sources as the scene was saved
   (`make/large-worlds`).

What Strata does not do here: the editor edits one scene at a time (with a world's loaded cells); additive loads run in
play mode only; a game cannot raise its streaming budgets for a loading screen. The exercises, done in a script: a
"Delete save" button on the main menu that removes the best time and shows that none is kept, and a third level named
in the goal's scene field. At the end the reader can split a game into scenes, show progress while one loads, carry
state from one scene to the next and keep a player's progress between runs.

**Leaves out.**

- The scene loader, sub-scene states and the frame's work budget inside → `world/sub-scenes`
- Scene switches inside the runtime of an exported game → `worlds/runtime`
- Scene switches in the editor's play mode → `editor/play-mode`
- Residency, pins and load progress inside → `assets/residency`, `assets/references`
- The upload budgets and the staging bound that limit how fast a loading bar fills → `assets/uploads`
- The export itself, its start scene and loading scene in the export dialog → `make/export`
- Streaming a world in cells, and prefetching before a teleport or a restored player → `make/large-worlds`
- Players' graphics options and their file → `make/quality`
- Text formats such as JSON for a settings file → `basics/data-formats`

**Fit.** `fits`: about 5,300 words against L (5,000). Seven goals of about 20 numbered steps with four excerpts, the
page's own save code and three rules (about 3,800 words) take the most, then game flow with its figure, the two
exercises and the absences.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:342` | concept | home | Game flow and persistence: scenes as levels and menus, loading screens, passing state (fields or module state), save files and where they are; the mistake of expecting entities to survive `LoadScene` |
| `gamedev:198` | feature | home | Scene switches: `Game::LoadScene` by handle or path, `ReloadScene`, `GetSceneLoadProgress`; the background load and the swap between frames; a scene named in a field is an asset reference that a pruned export keeps |
| `gamedev:199` | feature | home | `Game::Quit(code)`: the exported game exits with the code, the editor stops play |
| `gamedev:200` | feature | home | Additive sub-scenes: `Scene::LoadAdditive`, `SubScene::Unload`, `Assets::GetLoadProgress` (`Scene::InstantiateMany` is `make/performance`'s) |
| `gamedev:201` | feature | home | Module state across scene loads: namespace-scope state survives `LoadScene` (the attract mode, a settings cache) |
| `gamedev:202` | feature | home | The start scene (**File > Set as Start Scene**) and the loading scene that plays while the start scene loads |
| `gamedev:203` | feature | home | Save files: `WriteSaveFile`, `ReadSaveText`, `ListSaveFiles`, `DeleteSaveFile`; names; the folders of the editor and of the exported game; synchronous |
| `gamedev:379` | code | home | `Samples/ThirdPerson/Scripts/ThirdPerson.h:1-46`: what the sample's scripts share across scenes (the settings, the attract mode), with `ThirdPerson.cpp` 68-77, where the settings are read from their save file once |
| `gamedev:427` | figure | home | The scene flow of the Third-Person sample: main menu (the attract mode after 10 s), loading, course, pause; the module state beside them |
| `gamedev:504` | rule | home | Entities do not survive `Game::LoadScene`: pass state through the next scene's fields, save files or module state |
| `gamedev:647` | term | home | Save file |
| `gamedev:648` | term | home | Sub-scene (additive load) |
| `gamedev:661` | term | home | Attract mode |
| `scene-ecs:604` | hands-on | home | A part of a level loaded additively with the SDK's `SubScene`, its progress on a UI bar, and unloaded |
| `scripting:523` | hands-on | home | Save and load a checkpoint with `WriteSaveFile` and `ReadSaveText`; an invalid name fails |
| `new:11` | code | home | `Samples/ThirdPerson/Scripts/LoadingScreen.cpp:12-28`: a loading screen: `Game::GetSceneLoadProgress` on a filled image and a percentage. No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `new:12` | code | home | `Samples/ThirdPerson/Scripts/CourseState.cpp:94-104`: reading a value back from a save file that may be missing or hold nonsense. No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `new:10` | not-done | home | The editor edits one scene at a time (and a world's loaded cells); `scene.loadAdditive` works in play mode only. Evidence: `StrataEditor/src/Editor/EditorSceneCommands.cpp:458-460` |
| `new:31` | not-done | home | Raising the streaming budgets of a game for a loading screen: no script function and no settings section sets the upload, finalization and staging budgets, and the runtime's `--asset-budget-mb` sets only the GPU texture budget; the page links `assets/uploads` for the budgets and the staging bound. Evidence: `Strata/src/Strata/Asset/AssetResidency.h:56-64` (raise all three for a loading screen); `git grep -ln -e UploadBytesPerFrame -e FinalizeMsPerFrame 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataScriptCore` finds only the asset manager's files (`Strata/src/Strata/Asset/AssetManager.cpp`, `AssetManager.h`, `AssetResidency.cpp`, `AssetResidency.h`) and the editor's (`StrataEditor/src/Editor/EditorStreamingCommands.cpp`, `StrataEditor/src/Panels/StreamingPanel.cpp`); `StrataRuntime/src/RuntimeApplication.cpp:56, 94-95` |
| `new:37` | rule | home | Step 2: module state at namespace scope lives as long as the module's library is loaded: in the editor it carries over from one Play to the next, since the module unloads only when the project closes; every hot reload and every reload after a crash starts it over, because a new library is loaded; an exported game starts it fresh at each run. Evidence: `Samples/ThirdPerson/Scripts/ThirdPerson.h:3-5` (the module stays loaded while the game switches scenes); `StrataEditor/src/Editor/EditorContext.cpp:655` and `:2406-2419` (the only unload, `CloseScriptEngine`, when the project closes); `StrataEditor/src/Editor/EditorContext.cpp:2594-2604` (a build loads the module again only when it changed or crashed); `Strata/src/Strata/Scripting/ScriptEngine.cpp:107` (a reload unloads the previous module) |
| `gamedev:515` | rule | link | Prefetch before placing a restored player in a world, and keep the player with its streaming source in the saved scene, since the start cells load around the sources as the scene was saved (step 7; the rule's home is `make/large-worlds`, the prepared start's `worlds/physics-scripts`) |
| `new:32` | hands-on | home | Exercises, done in a script: a "Delete save" button on the main menu that calls `Game::DeleteSaveFile` and then shows that no best time is kept (`ReadSaveText` empty); a third level named in the goal's scene field. Evidence: `StrataScriptCore/Include/StrataScript/Game.h:129` (`ReadSaveText`), `:151` (`DeleteSaveFile`), `:47` (`LoadScene` by handle) |
| `scripting:129` | feature | home | `Game` and `WindowMode` in the SDK: quit, scene switches and their progress, save files as bytes or text; the window functions are taught on `make/menus` (`gamedev:204`); `reference/script-api` lists the declarations and links here |
| `scripting:121` | feature | use | `Scene::LoadAdditive`, `SubScene` and `Assets::GetLoadProgress` |
| `scripting:338` | concept | use | Player-facing systems: save files written whole, with validated names |
| `worlds-runtime:78-79` | feature | use | Sub-scenes and their states, in a game maker's words (their home is `world/sub-scenes`) |
| `worlds-runtime:93` | feature | use | Scene loads and quits from scripts, which the exported game honors |
| `worlds-runtime:126-127` | feature | use | Scene switches that never block, and the loading scene |
| `worlds-runtime:149` | feature | use | The saves' folder is named after the manifest's name, not the title |
| `worlds-runtime:237` | concept | use | Additive scenes |
| `worlds-runtime:288` | concept | use | Startup and scene switching as players see them |
| `worlds-runtime:448` | rule | use | Saves are keyed by the manifest's name, never the title |
| `gamedev:577` | term | use | Start scene and loading scene: this page teaches the loading scene (`gamedev:202`); the item's home stays on `make/export` for "start scene", and the glossary step splits the entry and homes "loading scene" here |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A main menu, a pause menu and a settings screen | `make/menus` | must |
| Entity and asset fields; a scene in a field | `make/script-fields` | must |
| `std::to_string` and `std::stoi` | `basics/programming-2` | must |
| `std::optional` with `has_value` and `value_or` | `basics/programming-3` | must |
| Namespaces and `::` | `basics/programming-1` | must |
| `Game::ReloadScene` in one step | `make/project-coin-run` | must |
| A filled image and a text on the HUD | `make/hud` | must |
| Triggers | `make/physics` | must |
| Asking for assets early | `make/scripting-scene` | must |
| The project folder and its hidden `.strata` folder | `make/project-files` | must |
| The exported game and the user data folder | `make/export` | must |
| Load progress and the dependency closure inside | `assets/references` | helps |

**Starting state.** The end checkpoint of `make/menus`, downloadable: the course with its main menu, pause menu,
settings screen, rebinding screen and name field. The steps add a second course scene, a goal and a small room scene.

**Command-only steps.** none

## Passed on

none

## Not taken

none

## Questions for the planner

none
