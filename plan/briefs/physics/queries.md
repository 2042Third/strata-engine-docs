# Brief: `physics/queries`

| Field | Value |
| --- | --- |
| Title | Physics queries |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `physics/collision-layers` |
| From | physics ch. 7; 1.7 (raycasts, overlaps, masks, ignored bodies, deterministic results; no shape sweep in the API) |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `physics/queries` — Physics queries

**Covers.** The job: answer questions about space without moving anything. The problem and how engines solve it,
taught here in full: raycasts (the closest hit or all hits), overlaps, shape casts; layer masks, ignoring oneself,
triggers or not, a ray that starts inside a shape; and the question of when a query sees the world (Strata's: as of the
last step or change, with pending changes applied first). The example is the Playground: shooting a ball through the
cursor and the grab tool. The map: the SDK's `Physics::Raycast`, its host function, `IPhysicsQueries`, `PhysicsSystem`
and `PhysicsWorld`, down to box3d's ray cast and overlap tests. The contract: results in a deterministic order, the
world as of the last step, distances clamped to 1e5 m. A toy version: a ray against a list of spheres. The real code:
`RayCallback` and `Raycast` (a callback that clips the ray to closer hits, so the closest wins; rays that start inside a
convex collider do not hit it); `RaycastAll`, the closest hit per entity sorted by distance; `CollectOverlaps`, results
sorted by body index; the grab tool (`UpdateGrab`: a raycast picks a body, a capped velocity pulls it). What Strata
does not do: shape sweeps in the API (box3d's mover cast is used only inside the character controller). Then the
alternatives, how it is tested, and changing it safely: adding a query end to end, with the host function appended at
the end and the feature test extended (the exercises `OverlapCapsule` and `SphereCast`). At the end the reader can
choose the query for a gameplay question and say what it returns and in which order.

**Leaves out.**

- A camera's ray through the cursor → `make/gameplay-math`, `core/math`
- The ground probes inside the character controller → `physics/character-controllers`
- Adding a host function, step by step → `scripting/tutorial-host-function`
- Picking in the editor's Scene view → `editor-ui/scene-view`

**Fit.** `over`: about 4,200 words against M (3,000). The problem section taught in full, three excerpts with the grab
tool and three exercises (two of them extend the API) pass M's top; L (5,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:114-116` | feature | home | `Raycast`, `RaycastAll`, `OverlapSphere`, `OverlapBox` with masks, ignored entity and triggers; the world as of the last step; no shape casts in the public API |
| `physics:265` | concept | home | Spatial queries: closest and all, overlaps, shape casts, masks, ignoring self, triggers, starting inside a shape |
| `physics:313` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4499-4519`: `RayCallback`, with `Raycast` at `PhysicsWorld.cpp:5399-5417`; clipping the ray to closer hits, the inside-convex rule |
| `physics:314` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:4535-4571`: `CollectOverlaps`, results made deterministic by body index |
| `physics:325` | code | home | `Samples/PhysicsPlayground/Scripts/Playground.cpp:223-255`: `UpdateGrab`, raycast picking and grabbing by velocity |
| `physics:465-466` | hands-on | home | Exercises: an `OverlapCapsule` query through every layer (world, system, service, host function at the end, SDK, test, feature script); a `SphereCast` with sorted hits and the same filters |
| `new:17` | hands-on | home | Trace it yourself (D27): a breakpoint in `RayCallback` while a ray is cast through three boxes in a row (a copy of the test `Raycast reports the closest hit`): `Raycast`'s callback returns the hit's fraction, which clips the ray, so later calls come only for closer hits; `RaycastAll`'s returns 1 and never clips; a ray that starts inside a box passes out of it without a hit. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:4499-4519`, `:5399-5417`; `StrataTests/src/Physics/PhysicsQueryTests.cpp:13` |
| `physics:520` | term | home | Terms: raycast, `RaycastAll`, overlap, shape cast, sweep |
| `editor-core:725` | term | home | Term: raycast, as the editor inventory defines it (finding what a ray from the camera hits), one entry with `physics:520`; `editor/placement` teaches the editor's own ray against the scene under its own name and links this entry |
| `new:5` | not-done | home | Shape sweeps in the API: queries cast rays, and a sweep is used only inside the character controller. Evidence: `git grep -n "b3World_Cast" 822a7a46 -- Strata/src` finds `b3World_CastRay` (`Strata/src/Strata/Physics/PhysicsWorld.cpp:5413, 5435`; the controller's ground ray, `Strata/src/Strata/Physics/CharacterControllers.cpp:436`) and `b3World_CastMover` only at `CharacterControllers.cpp:373` |
| `physics:177`, `scripting:125` | feature | use | The query host functions, the SDK's `Physics` queries and `RaycastHit` |
| `physics:124` | feature | use | The query category bit that lets a query see every layer |
| `scripting:73` | feature | link | The query functions of the C ABI |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Rays and ray-shape intersection | `basics/math-geometry` | must |
| The broad phase's trees | `physics/collision-detection` | must |
| Layer masks and the query category bit | `physics/collision-layers` | must |
| `std::optional` | `basics/cpp-modern` | must |
| `std::vector` and sorting a list | `basics/cpp-generic` | must |
| A camera's ray from the cursor (`Ray::FromNDC`) | `core/math` | helps |
| Determinism as bit-identical results | `basics/numbers` | helps |
| Appending a host function | `scripting/host-api` | helps |
| The feature test | `engineering/feature-test` | helps |
| Running a debugger on a test or the editor | `core/debugging` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `raycast` | Raycast | RaycastAll, shape cast (sweep) |
