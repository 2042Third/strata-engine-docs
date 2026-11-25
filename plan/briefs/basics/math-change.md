# Brief: `basics/math-change`

| Field | Value |
| --- | --- |
| Title | Change over time: rates, accumulation, Euler steps and Newton's laws |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/math-vectors` |
| From | new; derivatives as rates and integrals as accumulation, both from tables of numbers and graphs before any symbol; explicit and semi-implicit Euler steps, and why the step's size matters; Newton's laws (force, mass, acceleration, momentum and impulse); home of rates, integration over time and Newton's laws; blending and smoothing are `basics/math-interpolation`'s |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-change` — Change over time: rates, accumulation, Euler steps and Newton's laws

**Covers.** Every idea comes first as a table of numbers and a graph, and only then as a formula. In order: (1) a rate
of change from a table: positions written down every second, the change per second, the slope of the graph; (2) the
derivative as the rate at one moment, found from shorter and shorter intervals, then its notation read aloud; (3)
accumulation: from a table of speeds back to the distance, rectangles under the graph, and the integral as the area
under it (named here, used again by `basics/math-probability`); accumulating small steps along a path, as a march
through fog or air adds up light (`light/atmosphere`); (4) velocity and acceleration as vectors: velocity the rate of
change of position, acceleration the rate of change of velocity, gravity as a constant acceleration of 9.81 m/s²
downward; (5) the explicit Euler step: the position moved by the old velocity, then the velocity changed, run by hand
in a table for a falling ball; (6) the semi-implicit Euler step: the velocity first, then the position with the new
velocity, the same table for a spring, the explicit step's energy that grows and the semi-implicit step's that stays;
physics engines step this way, as Strata's does (`physics/dynamics`); (7) the size of the step: the error a larger step
brings, a step so large that the spring explodes, and why games simulate with a fixed step (its home is `core/time`);
(8) Newton's laws: a body keeps its velocity, force equals mass times acceleration, every force has an equal and
opposite one; forces in newtons, mass in kilograms; (9) momentum and impulse: mass times velocity, a hit as a large
force over a short time, an impulse that changes the velocity at once, and the SDK's `AddForce` against `AddImpulse`.

Figures: a position graph with its slope, rectangles under a speed graph, the explicit and the semi-implicit spring, a
step that explodes. The common mistakes: multiplying by `deltaTime` twice or not at all, moving by the old velocity
where the new one was meant, a varying step for physics, a force applied once as if it were an impulse. Practice
(three to eight exercises, `style.md` §8) ends with the optional Coin Run item: the ball's speed computed from its
positions in two fixed steps and logged next to `RigidBody::GetLinearVelocity`, then a jump pad that gives the ball an
upward impulse.
"Where the book uses it" names `core/time`, `physics/dynamics`, `audio/spatial` and `light/atmosphere`.

**Leaves out.**

- Exponential decay and its total over a distance, with exponential smoothing → `basics/math-interpolation`
- Lerp, easing and smoothing → `basics/math-interpolation`
- Integrals over directions and Monte Carlo estimates → `basics/math-probability`
- The fixed step, its accumulator and time scale in Strata → `core/time`
- Torque, inertia and how bodies turn → `physics/dynamics`
- Forces, impulses and velocities for makers → `make/physics`
- The Doppler effect from velocities → `audio/spatial`

**Fit.** `fits`: about 5,100 words against L (5,000). The nine ideas at 400 to 500 words take the most (4,000); the
fixed parts with the Test out box, Practice and the Coin Run item take the rest (1,100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:56` | concept | home | A rate of change from a table of numbers, and the slope of a graph. Figure: a position graph. General knowledge. |
| `new:57` | concept | home | The derivative as the rate at one moment, from shorter and shorter intervals. General knowledge. |
| `new:58` | concept | home | Accumulation and the integral as the area under a graph; accumulating small steps along a path. Figure: rectangles under a speed graph. General knowledge. |
| `new:59` | concept | home | Velocity and acceleration as vectors; gravity as a constant acceleration. General knowledge. |
| `new:60` | concept | home | The explicit Euler method, run by hand in a table. General knowledge. |
| `new:61` | concept | home | The semi-implicit Euler method, and the energy it keeps where the explicit method adds energy. Figure: the two springs. General knowledge. |
| `new:62` | concept | home | The size of the time step: error, instability, and why simulations take fixed steps. Figure: a step that explodes. General knowledge. |
| `new:63` | concept | home | Newton's laws of motion: force, mass and acceleration; newtons and kilograms. General knowledge. |
| `new:64` | concept | home | Momentum and impulse: a hit as a large force over a short time, an impulse as an instant change of velocity. General knowledge. |
| `new:65` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: the ball's speed from two fixed steps' positions beside `GetLinearVelocity`; a jump pad with an upward impulse. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:85` (`OnFixedUpdate`), `StrataScriptCore/Include/StrataScript/Physics.h:55` (`GetLinearVelocity`) and `:93` (`AddImpulse`) |
| `physics:511` | term | home | Impulse, an instant change of momentum, force times time; one glossary entry with the seed's |
| `scripting:125` | feature | use | The SDK's `RigidBody`: `GetLinearVelocity`, `AddForce` and `AddImpulse` |
| `physics:225` | concept | link | Rigid body state and its semi-implicit Euler step in Strata's physics; its home is `physics/dynamics` |
| `foundation:228` | concept | link | The fixed step and its accumulator; its home is `core/time` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vectors: adding and scaling them, length | `basics/math-vectors` | must |
| Loops and `std::vector`, for tables of numbers in code | `basics/programming-2` | must |
| A script of the playground: `OnUpdate`, `deltaTime` and `Log::Info` | `basics/programming-1` | must |
| Fixed updates in a script (`OnFixedUpdate`) | `make/script-loop` | helps |
| Decimals and floating-point rounding | `basics/numbers` | helps |
| Rigid bodies, forces and impulses in the editor | `make/physics` | helps |

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
| `acceleration` | acceleration | - |
| `accumulation` | accumulation | - |
| `derivative` | derivative | - |
| `explicit-euler-method` | explicit Euler method | forward Euler |
| `force` | force | - |
| `impulse` | impulse | - |
| `integral` | integral | - |
| `mass` | mass | - |
| `momentum` | momentum | - |
| `newtons-laws-of-motion` | Newton's laws of motion | Newton's laws |
| `numerical-integration` | numerical integration | integration |
| `rate-of-change` | rate of change | rate |
| `semi-implicit-euler-method` | semi-implicit Euler method | symplectic Euler |
| `time-step` | time step | timestep |
| `velocity` | velocity | - |
