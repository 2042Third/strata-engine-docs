# Brief: `physics/why`

| Field | Value |
| --- | --- |
| Title | Why games need physics |
| Kind | C |
| Size | S |
| Tracks | E |
| Needs | - |
| From | physics ch. 1 (the problems, the engines on the market, why box3d, what Strata does not do) |
| Unit | `plan/allocation/physics.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `physics/why` — Why games need physics

**Covers.** The page opens on the part's running example, the Physics Playground sample: a crate tower, a domino run,
a pit of 500 balls, a goal that counts what falls into it and ghost boxes that sink through the balls (its two
screenshots). From it the reader meets the problem: things that fall, collide, stack and are pushed, and questions
about space ("what is under the cursor", "is the player on the ground"). The naive answer is collision written by hand
in game code (move, test for overlap, push back), and the page shows where it breaks: stacks, many objects, fast
objects. The idea: a physics engine is a second simulation beside the scene, stepped in fixed steps, that must be kept
in step with the scene's transforms. The approaches engines use come next: hand-written gameplay collision, a
third-party engine (PhysX, Havok, Jolt, Bullet, Box2D and box3d) or an engine's own solver, with a table of their
cost, quality, licence and users (sources in Further reading). Strata's choice and its reason: box3d (MIT, pinned in
`ThirdPartyNotices.md`) behind Strata's own components and scene services, with Strata's own character controller on
box3d's mover queries; box3d replaced Jolt in 0.5.0 (`Docs/Releases/0.5.0.md:30, 64-66, 75-100`). What Strata does not
do here: joints, ragdolls and vehicles; cloth, soft bodies, destruction, fluids and buoyancy. The common mistake: to
think the physics body is the transform. At the end the reader can say what box3d does and what Strata adds around
it, and which page of the part answers which question.

**Leaves out.**

- How a body and its colliders are set up → `physics/bodies-colliders`
- How a solver moves bodies and resolves contacts → `physics/dynamics`
- The fixed step and the accumulator → `core/time`
- Making a game with physics in the editor → `make/physics`
- Every property with its default and range → `reference/components`
- The units of every property and settings field → `reference/physics`

**Fit.** `over`: about 2,750 words against S (1,500). The concept shape's eight sections, from the Playground's opening
to the table of six engines, with the two exercises of D27, pass S's top; M (3,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:217` | concept | home | What a physics engine is for in a game; the approaches (hand-written, third-party, own); Strata's choice of box3d behind components and services, with its own character controller; the mistake "physics is the transform" |
| `physics:187` | feature | home | The Physics Playground sample: six stations, about 600 bodies, its scripts and its regression; the part's running example, whose stations later pages take up |
| `physics:367` | figure | home | `Samples/PhysicsPlayground/Screenshots/Overview.png` and `BallPit.png` (both exist at the pin) as the page's opening |
| `new:1` | not-done | home | Joints, ragdolls and vehicles: Strata has none; the Roadmap lists them on box3d's joints. Evidence: `git grep -nE "b3Create[A-Za-z]*Joint" 822a7a46 -- Strata/src` finds nothing (run at the pin); `Docs/Roadmap.md:1716-1718` |
| `new:2` | not-done | home | Cloth, soft bodies, destruction, fluids and buoyancy. Evidence: `git grep -niE "cloth\|soft ?bod\|fluid\|buoyan\|fractur\|destructible" 822a7a46 -- Strata/src` finds nothing (run at the pin); the word "destruction" matches only the destruction of entities and objects |
| `new:10` | hands-on | home | Exercises (D27): in a copy of the Physics Playground, one crate lifted 3 m in the Scene view and played: it falls; its Rigid Body type set to Static and played again: it hangs in the air; its Box Collider removed: a ball shot at it with a left click passes through it. What is drawn is the MeshRenderer, what collides is the collider, and only a dynamic body falls (done, editor task). For three games (a stacking puzzle, a top-down shooter whose bullets are rays, a card game), which needs bodies, which needs only queries and which needs no physics engine, and why (design). Evidence: `Samples/PhysicsPlayground/Assets/Prefabs/Crate.stprefab:2` (a BoxCollider, a MeshRenderer and a Dynamic RigidBody on one entity); `Samples/PhysicsPlayground/README.md:35` (left click shoots a ball); `Strata/src/Strata/Physics/PhysicsComponents.h:15-18` |
| `physics:116` | feature | link | No shape sweeps in the API, named in the list of absences and linked to its page |
| `physics:51` | feature | link | The 1e5 m coordinate limit, named in one sentence |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a game engine is, and one frame from start to finish | `start/what-an-engine-is` | must |
| Entities and components | `world/what-a-world-is` | helps |
| The fixed step | `core/time` | helps |
| Opening a copy of a sample and pressing Play | `start/first-game` | helps |
| A velocity as a direction with a length | `basics/math-vectors` | helps |
| Third-party libraries in Strata and their licences | `engineering/third-party` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
