# Brief: `physics/contacts-triggers`

| Field | Value |
| --- | --- |
| Title | Contacts and triggers |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `physics/world-step`, `physics/collision-layers` |
| From | physics ch. 6; 1.6 (events, pair folding, interest, dispatch rules, trigger limits); home of contacts and triggers reaching scripts |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `physics/contacts-triggers` — Contacts and triggers

**Covers.** The job: tell game code when two entities start and stop touching, and when something enters or leaves a
trigger. The problem and how engines solve it, taught here in full: triggers as sensors (overlap without a response,
events only, what a sensor can see) and contact events (Begin and End per pair, why a library's per-shape events are
folded per entity, why events are delivered after the step and never from inside the solver, why every Begin has exactly
one End, what tracking costs), on the Playground's goal basket that counts balls and its impact sounds. The map: box3d's
contact and sensor events, `ProcessStepEvents`, the touching pairs, `CollisionEvent`s, the dispatch on the main thread
and the listeners, among them the script system's. The contract: events come after the step, on the main thread, and
listeners may destroy entities or call the physics API. A toy version: counting contacts per entity pair. The real code:
`TouchingPair` with `CountBegin` and `CountEnd` (a pair begins with its first contact and ends with its last; a rebuilt
body marks its pairs Unconfirmed instead of an End and a Begin; constant-time removal); reading box3d's event buffers in
`ProcessStepEvents` (static-static sensor pairs dropped, nothing tracked that nobody wants); contact interest and
watches (nobody listening costs nothing); the contact point midway between the surfaces and the trigger point at the
centre of the boxes' overlap; `ICollisionEventSource` with its two scopes; `DispatchCollisionEvents` over a snapshot of
the listeners; and the scripts' side, `OnCollisionEnter`, `OnCollisionExit`, `OnTriggerEnter` and `OnTriggerExit` with
the SDK's `Collision`, in the Playground's `GoalBasket` and `LaunchPad`. What Strata does not do: triggers that see
triangle-mesh colliders; stay events, and the impulse or impact speed of a contact (a script reads the bodies'
velocities, as `Impact.cpp` does). The pair-folding figure (a small state machine), then the alternatives, how it is
tested and changing it safely. At the end the reader can write a trigger script and explain why its Enter and Exit
always come in pairs.

**Leaves out.**

- How the script system calls a script's callbacks → `scripting/script-system`
- The contacts of character controllers → `physics/character-controllers`
- Impact sounds that are louder for harder hits → `make/sound`
- Triggers in a game, for game makers → `make/physics`

**Fit.** `fits`: about 5,100 words against L (5,000). The problem section taught in full (sensors and per-entity
contact events) and four excerpts, from the pair folding to the Playground's trigger scripts, take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:50` | feature | home | Triggers are box3d sensors: they see convex shapes and characters, never triangle meshes; static-static sensor pairs are dropped |
| `physics:101-108` | feature | home | `CollisionEvent`; `ICollisionEventSource`; pair folding; contact interest; contact and trigger points; dispatch after the step; the scripts' callbacks; constant-time pair upkeep |
| `physics:261-263` | concept | home | Triggers (sensors) and contact events |
| `physics:310` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:3598-3625`: `CountBegin` and `CountEnd`, with `TouchingPair` at `PhysicsWorld.cpp:422-443`; per-shape contacts folded into per-entity Begin and End |
| `physics:311` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:3643-3710`: `ProcessStepEvents`, reading a library's event buffers and skipping work nobody wants |
| `physics:312` | code | home | `Strata/src/Strata/Physics/PhysicsSystem.cpp:636-660`: `DispatchCollisionEvents`, a snapshot of the listeners, removed listeners, re-entrancy |
| `physics:324` | code | home | `Samples/PhysicsPlayground/Scripts/GoalBasket.cpp:1-26`, with `Samples/PhysicsPlayground/Scripts/LaunchPad.cpp:1-22`: triggers in game code, the smallest useful scripts |
| `physics:345` | figure | home | Contact pair folding: shape contacts feeding one touching pair, Begin at the first, End at the last, Unconfirmed on rebuild |
| `physics:402` | rule | home | Events are delivered after the step, not from inside it |
| `physics:485` | term | home | Terms: trigger, sensor |
| `scripting:618` | term | home | Term: trigger, as the scripting inventory defines it (the same entry as `physics:485`) |
| `physics:521-523` | term | home | Terms: collision event, touching pair, contact interest, watch |
| `new:16` | hands-on | home | Exercises (D27): breakpoints in `CountBegin` and `CountEnd` while a body of two box colliders lands on the ground: two shape contacts, one touching pair, one Begin (trace). A doctest with `Tests::CollisionRecorder`: a ball dropped through a static trigger counts one Begin and one End, and a second ball destroyed while it is inside the trigger still ends its pair, so every Begin has its End (done). Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:3598-3625`; `StrataTests/src/Physics/PhysicsBox3DBehaviorTests.cpp:275`; `StrataTests/src/Physics/PhysicsTestUtils.h:95-112`; `StrataTests/src/Physics/PhysicsEventTests.cpp:14`, `:104`; `Strata/src/Strata/Scene/SceneServices.h:47-48` |
| `new:4` | not-done | home | Triggers that see triangle-mesh colliders (box3d's sensors test convex shapes only); the Roadmap lists them. Evidence: `Docs/Releases/0.7.0.md:399`; `Docs/Roadmap.md:1719-1720` |
| `new:9` | not-done | home | Stay events, and the impulse or impact speed of a contact: events are only Begin and End, so scripts get Enter and Exit and no "stay" callback, and a contact carries the other entity, a point and a normal but no impulse, because box3d's hit events are not used; game code that needs a hit's strength reads the bodies' velocities, as the Playground's `Impact.cpp` does (about 80 words; a reader who knows Unity expects `OnCollisionStay` and the contact's impulse). Evidence: `Strata/src/Strata/Scene/SceneServices.h:41-45`; `StrataScriptCore/Include/StrataScript/Script.h:89-92`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:181-188`; `git grep -n enableHitEvents 822a7a46 -- Strata/src` finds nothing (run at the pin); `Samples/PhysicsPlayground/Scripts/Impact.cpp:53-55` |
| `physics:139` | feature | link | Character contacts that join entity pairs, and triggers that reach the presence body |
| `physics:377` | figure | use | The frames of the balls counted by the goal |
| `scripting:382` | code | link | The script system's contact delivery, walked on `scripting/script-system` |
| `scripting:125` | feature | use | The SDK's `Collision`, which the four contact callbacks receive (the other entity, the point, the normal) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| One step: sync, box3d steps and write-back | `physics/world-step` | must |
| Collision layers and filters | `physics/collision-layers` | must |
| Callbacks stored as `std::function` | `basics/cpp-generic` | must |
| A script class and `override` | `basics/programming-3` | must |
| Scene services | `world/systems` | must |
| Hash maps, and removing from an array by swapping with the last element | `basics/data-structures` | must |
| UUIDs as the identities of entities | `world/ecs` | helps |
| How the script system delivers callbacks | `scripting/script-system` | helps |
| Writing and running one doctest case | `core/first-change` | helps |
| Running a debugger on a test or the editor | `core/debugging` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `collision-event` | Collision event | - |
| `contact-interest` | Contact interest | - |
| `touching-pair` | Touching pair | - |
| `trigger` | Trigger | - |
