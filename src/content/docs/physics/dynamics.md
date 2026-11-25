---
id: physics/dynamics
title: "Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision"
description: "How one physics step moves bodies, keeps them apart, lets piles rest and catches fast bodies, and which of box3d's choices Strata keeps."
kind: concept
size: L
tracks: [E]
needs: [physics/collision-detection, core/time, basics/math-change, basics/math-rotations]
time: 60
learn:
  - id: integrate
    text: compute one semi-implicit Euler step and the velocity of a point on a turning body
  - id: contact-push
    text: compute the speed with which a soft contact pushes out an overlap for a given contact hertz and damping ratio
  - id: tunnel
    text: predict whether a fast body tunnels through a thin wall from its speed, the step and the body types
  - id: bounce-sleep
    text: predict whether a body bounces, rests or falls asleep from its impact speed and its speed over time
  - id: settings
    text: name what each field of the Physics.Simulation section changes in the solver
since: 0.3.0
status: final
---

Open the Physics Playground sample and press Play. A tower of crates stands on a floor, a pit holds 500 balls in rows on its floor, and a run of 64 standing blocks waits for a push. Nobody animated any of it. At 6 s the sample pours 100 more balls into the pit. They fall, bounce a little, settle in a layer and lie still, and some 15 seconds later the whole pit stops moving.

::figure{id=pit-pouring}

::figure{id=pit-resting}

Both pictures were taken at exact :term[fixed steps]{id=fixed-step}, so they show the same frames on every run. Between them lies a long chain of tiny decisions. How far does a ball move in one step? What stops it at the floor without a jolt? Why does a stack of crates not sink into the ground, and why does a ball that rolls at the speed of a walk finally stop for good?

This page answers those questions for one step of the simulation. It starts with the answer you would write first, shows where it fails, and then builds the answer that [box3d](../physics/why.md), the library Strata uses, gives.

## The first answer fails in three ways

Your first answer is likely this. Each step, move every body by its velocity. Then search for overlaps and push each overlapping body out along the contact normal. Keep the velocities as they are.

Try it on one ball that lies on a floor at 60 steps per second. Gravity adds 9.81 × (1/60) = 0.1635 m/s to the downward velocity in every step. The ball moves down 2.7 mm, overlaps the floor, and your code pushes it up again. The position looks right, but nobody removed the speed.

After one second the stored velocity is 9.81 m/s downward. The ball only rests because the push-out hides the speed. Roll the ball off a ledge at that moment, and it leaves with a speed it never earned.

You can fix that one by zeroing the velocity at the floor. Two other failures remain. The first is energy: how you add the velocity to the position decides whether a spring or a swing gains energy every step. The second is the stack. Push one overlapping pair apart and you push a third body into overlap, so a tower of ten crates shakes itself apart or sinks a little in every step.

A better answer has three parts. The step changes the velocities first, using forces. It then treats contacts as rules that velocities must obey, and solves those rules for all contacts of a pile together. Finally it moves the bodies with the corrected velocities. The sections below build these parts in that order.

## A body is a state, and a step changes it

A :term[rigid body]{id=rigid-body} has a state of four things. Its position is the world position of its center of mass. Its rotation is a quaternion (four numbers that store an orientation, from [the page on rotations](../basics/math-rotations.md)). Its linear velocity is how fast the center moves, in m/s. Its :term[angular velocity]{id=angular-velocity} is a vector whose direction is the axis of the turn and whose length is the rate in :term[radians]{id=radian} per second.

A body that turns also moves at every point except the center. The velocity of the point at offset $r$ from the center is:

$$v_p = v + \omega \times r$$

Here $v_p$ is the velocity of the point in m/s, and $v$ is the linear velocity of the center in m/s. Next, $\omega$ is the angular velocity in radians per second, and $r$ is the offset in metres. The sign $\times$ is the :term[cross product]{id=cross-product}. The cross product gives a vector at right angles to both inputs.

Take a wheel of radius 0.5 m that turns at 4 radians per second about the z axis, and let its center move at 2 m/s along x.

Then $\omega = (0, 0, 4)$. The point at the top has $r = (0, 0.5, 0)$, so $\omega \times r = (-2, 0, 0)$ and the point moves at 0 m/s. The point at the bottom moves at 4 m/s. Touching bodies use exactly this formula. The speed with which two surfaces approach at the touch point is the difference of two such velocities.

:::note[Why the touch point matters]
An impact sound is louder for a fast approach, and the approach speed at a contact is measured at the :term[contact point]{id=manifold}, not at the center. A box that tumbles has a corner that moves much faster than its center. The same formula tells a push at a point how much it turns the body.
:::

### Mass and the inertia tensor

Mass says how hard it is to change the linear velocity. The **inertia tensor** is a 3 × 3 matrix that says the same for the angular velocity: it turns a torque into an angular acceleration, and it depends on how the mass is spread. A long plank turns with little effort about its long axis and slowly about its middle. Rotating the body rotates its tensor, so the engine computes it again in :term[world space]{id=world-space} in every step.

Strata gets both from the shapes.

Every :term[collider]{id=collider} shape is given a density of 1, and box3d computes the mass, center and tensor of the shapes together. Strata then scales the mass to the value of the component and scales the tensor by the same factor (`ApplyMass`). The mass you set is the real mass; the shapes only decide how it is distributed.

### Semi-implicit Euler

The step needs the new velocity and the new position. Both change by small amounts per step $h$:

$$v \leftarrow v + a\,h, \qquad x \leftarrow x + v\,h$$

Here $v$ is the velocity in m/s, $a$ is the acceleration in m/s², $h$ is the step length in seconds and $x$ is the position in metres. The arrows mean "becomes". The order matters. Explicit Euler moves with the old velocity first, semi-implicit Euler changes the velocity first and moves with the new one, as the arrows above are written. The page on [change over time](../basics/math-change.md) explains both.

Take a unit mass on a spring with stiffness 100 at 60 steps per second, released at $x = 1$ m, so its energy is 50 units. The explicit rule multiplies the energy by about 1.028 in every step. After 10 s the spring has 689 million units. The semi-implicit rule keeps the energy within a few percent of its start: 53 after 10 s. Physics engines pay the same price for the second rule as for the first, one multiplication more or less, so every engine uses it.

### Forces, impulses and set velocities

A game changes motion in three ways. A force is pushed for a time: it changes the velocity by $F\,h / m$ in a step, so a wind or an engine adds a force in every step it should act. An impulse is an instant change of momentum: the velocity changes by $J/m$ at once, which suits a kick or a jump. Setting the velocity overrides whatever the contact step found, so contacts cannot undo it in the same step.

Strata adds a rule on top. A force you add acts during the next fixed step only. Strata queues it and applies it again before each box3d step of that fixed step, and then forgets it.

An impulse changes the velocity when you call it. Scripts run once per frame, and a frame may hold no fixed step or several. A wind that you want to act for a second needs an `AddForce` call in every fixed step of that second. A single call in `OnUpdate` gives one fixed step of push and nothing after it.

## A toy of the contact step comes first

Before the real contact step, one that fits on a page. The toy has two parts. The first compares the two Euler rules on the spring above. The second drops a unit mass on a floor and compares "push out and keep the velocity" with "remove the approach speed by an impulse".

:::question[Never read C++ before?]
The page on [programs and variables](../basics/programming-1.md) explains values and `if`, the page on [loops and functions](../basics/programming-2.md) the loops, and the page on [classes and calls](../basics/programming-3.md) calls such as `std::printf(`.
:::

The program below runs both comparisons. Look at the two lines it prints: the energy of the explicit spring against the semi-implicit one, and the velocity that each floor method stores for a body that rests.

```cpp sketch="physics-dynamics-toy.cpp"
// A toy solver: two Euler steps on a spring, then a resting body on a floor with and without an impulse at the contact.
#include <cstdio>

int main()
{
	const float h = 1.0f / 60.0f; // one step
	const float stiffness = 100.0f; // a unit mass on a spring: energy = v * v / 2 + stiffness * x * x / 2

	float explicitX = 1.0f, explicitV = 0.0f; // explicit Euler: move with the old velocity, then change it
	float semiX = 1.0f, semiV = 0.0f;         // semi-implicit Euler: change the velocity first, move with the new one
	for (int step = 0; step < 600; step++)
	{
		const float acceleration = -stiffness * explicitX;
		explicitX += explicitV * h;
		explicitV += acceleration * h;
		semiV += -stiffness * semiX * h;
		semiX += semiV * h;
	}
	std::printf("energy after 10 s: explicit %.0f, semi-implicit %.1f\n",
		explicitV * explicitV / 2 + stiffness * explicitX * explicitX / 2, semiV * semiV / 2 + stiffness * semiX * semiX / 2);

	const float gravity = -9.81f;
	float naiveY = 0.0f, naiveV = 0.0f; // push the overlap out, keep the velocity
	float impulseY = 0.0f, impulseV = 0.0f;
	for (int step = 0; step < 60; step++)
	{
		naiveV += gravity * h;
		naiveY += naiveV * h;
		if (naiveY < 0.0f)
			naiveY = 0.0f;

		impulseV += gravity * h;
		if (impulseY + impulseV * h < 0.0f) // the step would end below the floor: an impulse removes the approach speed
			impulseV += -impulseV;          // impulse = mass * (-velocity), mass 1
		impulseY += impulseV * h;
	}
	std::printf("resting body after 1 s: naive velocity %.2f m/s, impulse velocity %.2f m/s\n", naiveV, impulseV);
}
```

```text output-of="physics-dynamics-toy.cpp"
energy after 10 s: explicit 689453056, semi-implicit 53.2
resting body after 1 s: naive velocity -9.81 m/s, impulse velocity 0.00 m/s
```

1. **Lines 13–17:** the explicit rule moves with the old velocity, the semi-implicit rule changes the velocity first.
2. **Lines 27–30:** the naive floor pushes the overlap out and keeps the velocity.
3. **Lines 32–35:** the impulse removes the approach speed only when the step would end below the floor.

The first line shows the energy gain of the explicit rule. The second line shows the failure of the first answer: the naive body rests with a stored speed of 9.81 m/s, and the impulse body rests at 0. The impulse code asks whether the step would end below the floor, and if it would, it cancels the approach speed. That is a contact constraint in its smallest form, and the next section makes it general.

## Contacts are rules, solved with impulses

A **contact constraint** is a rule that two touching bodies must not move into each other: along the contact normal their approach speed must not be negative. The engine looks at every contact point and finds the smallest impulse along the normal that makes the rule true. The impulse is never negative, because a contact can push but not pull.

For a body of mass $m$ that lands on a fixed floor at speed $u$, the impulse that stops it is $m\,u$. A 10 kg crate that lands at 3 m/s needs a normal impulse of 30 N·s. If the floor pushes for the whole of a 1/240 s sub-step, that is an average force of 7,200 N, about 73 times the weight of the crate. The engine does not think in forces: it finds the impulse directly.

When the contact is off the body's center, part of the impulse turns the body. The mass that counts is then the effective mass, which combines the mass with the inertia tensor and the lever arm of the contact point. A body that is hit near its edge acts lighter than the same body hit at its center, because it has two ways to move away. The character controllers use the same quantity, and the page on [character controllers](../physics/character-controllers.md) returns to it.

A pile has many contacts, and each impulse changes the speeds that the others see. Box3d goes through all contacts several times, one after the other. Each pass brings the whole pile closer to a state where every rule holds, a method called sequential impulses. How many passes are enough, and what happens to a contact that has no overlap yet, are the next questions.

### Contacts that look ahead

A contact does not wait for an overlap. When the gap $s$ is still positive, box3d lets the bodies approach by at most $s/h$ per sub-step, which brings them exactly to touch at the end of the sub-step. Such a contact is speculative: it acts before the touch, so it seldom has a deep overlap to repair. Take a ball that arrives at 5 m/s with a gap of 1 cm, at a sub-step of 1/240 s. It may approach by 0.01 × 240 = 2.4 m/s only, so the contact slows it by the difference in that sub-step.

When two bodies do overlap, because they spawned that way or because a push was strong, box3d has two choices. It can push them apart hard, which makes a jolt, or softly, which takes several sub-steps. Box3d pushes softly.

### Soft contacts

A **soft contact** is a contact that behaves like a damped spring in the overlap direction instead of a rigid wall. Two numbers shape the spring. The **contact hertz** is its stiffness as a frequency: how many times per second the overlap would swing back and forth if nothing damped it. The **damping ratio** says how strongly the spring is damped: 1 is the smallest damping that stops the swinging, and box3d's default of 10 is far above it, so a contact never rings.

The speed with which a soft contact pushes an overlap apart follows from these numbers. Let $\omega = 2\pi f$ for a contact hertz $f$, and let $h$ be the sub-step in seconds. Then:

$$k = 2\zeta + h\omega, \qquad \beta = \frac{\omega}{k}, \qquad \mu = \frac{h\omega k}{1 + h\omega k}$$

In these formulas $\zeta$ is the damping ratio, $k$ is a helper number without a unit, $\beta$ is the bias rate in 1/s and $\mu$ is the mass scale. The mass scale is a share between 0 and 1: how much of the exact correction box3d applies. The push-out speed for an overlap of depth $d$ metres is then capped:

$$u = \min(\mu\,\beta\,d,\ c)$$

Here $u$ is the push-out speed in m/s, $d$ is the depth of the overlap in metres, and $c$ is the cap. The cap is the **push speed**, the fastest speed at which box3d resolves an overlap, 3 m/s by default; its name inside box3d is `contactSpeed`. The function $\min$ takes the smaller of its two inputs.

:::example[How fast a soft contact pushes out]
Use Strata's defaults, contact hertz 30 and damping ratio 10, with a sub-step of 1/240 s. Then $\omega = 2\pi \times 30 = 188.5$ per second and $h\omega = 0.785$. The helper $k = 20 + 0.785 = 20.785$, so $\beta = 188.5 / 20.785 = 9.07$ per second. The mass scale is $\mu = 16.32 / 17.32 = 0.942$.

A crate that overlaps the floor by 0.1 m is pushed out at $0.942 \times 9.07 \times 0.1 = 0.85$ m/s. An overlap of 0.2 m gives 1.71 m/s. An overlap of 0.5 m would give 4.27 m/s, so the cap of 3 m/s applies. Check the limits: for a depth of 0 the push is 0, and for any large depth the push stays at 3 m/s. A body that spawns half inside another is thrown out at 3 m/s, enough to send a light body over a low wall.
:::

:term[Static bodies]{id=static-body} are stiffer to meet. Box3d uses twice the contact hertz and half the damping ratio for contacts with a static body, so a floor pushes back more firmly than another crate does.

### Friction and restitution

Friction is a second rule at each contact, along the surface. Its impulse may not exceed the friction coefficient times the sum of the normal impulses of the contact. That is the classic law of dry friction: the harder two surfaces press, the more sliding they resist. When two shapes touch, box3d mixes their two coefficients into one. By default it uses the square root of their product for friction and the larger value for restitution; Strata does not replace those :term[callbacks]{id=callback}, and [the page on bodies and colliders](../physics/bodies-colliders.md) lists the materials.

Restitution is how much of the approach speed returns after the touch: 0 gives a dead stop, 1 a full rebound. Box3d applies it in a separate stage after the solve, and only when the approach speed is above a threshold of 1 m/s. Strata does not change that threshold.

A ball of restitution 1 that falls 2 cm meets the floor at $\sqrt{2 \times 9.81 \times 0.02} = 0.63$ m/s and does not bounce at all. The same ball dropped from 1 m arrives at 4.43 m/s and bounces. The threshold keeps resting bodies from jittering: a stack at rest constantly has tiny approach speeds, and bouncing them would never let them settle.

## Sub-steps divide a step

A **sub-step** is one of the equal parts into which box3d divides each of its steps, 4 in Strata. A step first finds the contacts once. It then repeats the stages below in each sub-step. First it changes the velocities by the forces and gravity, applies the impulses the contacts stored in the last step (a warm start).

Then it solves the contact rules and moves the bodies. A relax pass solves once more. After the last sub-step it applies restitution and stores the impulses for the next step.

```mermaid caption="One box3d step finds contacts once, repeats five stages in every sub-step, and applies restitution at the end." alt="A flow from finding contacts, through a loop of integrate velocities, warm start, solve, integrate positions and relax, to restitution and storing impulses."
flowchart LR
    A["Find contacts"] --> B["Integrate velocities"]
    B --> C["Warm start"]
    C --> D["Solve contacts"]
    D --> E["Integrate positions"]
    E --> F["Relax"]
    F -->|"next sub-step"| B
    F -->|"last sub-step"| G["Restitution and store impulses"]
```

Several short sub-steps beat one long step with many passes. Each sub-step moves the bodies, so contacts always see the current positions, and the stiffness of the springs is easier to integrate. The cost is that box3d does its work four times per step.

A fixed step of 1/60 s, one collision step and 4 sub-steps give a sub-step of 1/240 s, a rate of 240 per second. Box3d limits the contact stiffness to an eighth of that rate: $0.125 \times 240 = 30$ Hz, which is exactly Strata's default. A higher `ContactHertz` acts as 30.

The reason is the spring: a spring that swings at 30 Hz has a period of 1/30 s, which spans 8 sub-steps. Fewer sub-steps per period make the integration inaccurate or unstable. Strata computes the value that box3d really uses:

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L5660-L5665" from="const PhysicsSettings& settings" to="return std::min(settings.ContactHertz, 0.125f * subStepRate);" symbol="PhysicsWorld::GetEffectiveContactHertz"
const PhysicsSettings& settings = m_Data->Settings;
if (!(timestep > 0.0f) || !std::isfinite(timestep))
	return settings.ContactHertz;
// As b3World_Step computes it: its substep rate is the solver's substeps over each box3d step's time.
const float subStepRate = static_cast<float>(c_SolverSubSteps) * static_cast<float>(settings.CollisionSteps) / timestep;
return std::min(settings.ContactHertz, 0.125f * subStepRate);
```

Two things raise the ceiling: a shorter fixed step (1/120 s gives 60 Hz), or more collision steps per fixed step, which Strata's `CollisionSteps` field sets. Each collision step is one box3d step with its own 4 sub-steps, so two of them double the cost of the contact work. Lower values of `ContactHertz` always take effect.

## Fast bodies tunnel unless the engine looks along the path

A discrete step checks overlaps only at the end of each step. A ball at 240 m/s moves 4 m in a step of 1/60 s. Put a wall 0.1 m thick at 6 m, and the ball is at 4 m after one step and at 8 m after the next: at neither position does it overlap the wall. That failure is tunnelling.

**Continuous collision** (CCD) fixes it by testing the whole path of the step instead of its end points. A swept test moves the shape along the path and finds the first moment of contact, the time of impact, as a share of the step. In the example the sphere has a radius of 0.1 m, so its surface meets the front face at 5.95 m when its center is at 5.85 m. The share is $(5.85 - 4) / 4 = 0.46$: the ball stops 46 % into the second step, in front of the wall, and the contact rules take over from there.

Box3d sweeps every :term[dynamic body]{id=dynamic-body} against static bodies. A body that moves against other moving bodies needs more. The `ContinuousCollision` field of a body makes it a bullet in box3d's words: swept against kinematic and dynamic bodies too. Without it, a fast ball is safe against static walls and can still pass through a thin wall that is kinematic, for example a sliding door. Sweeping costs time, so only fast small bodies should be bullets.

The other remedy is more collision steps. At 240 m/s and four collision steps the ball is tested every metre, and a wall thicker than 1 m cannot be skipped. The method is blunt: it multiplies the cost of the whole step by the number of collision steps and still cannot catch a thinner wall. Two collision steps per fixed step doubled the cost in Strata's measurements and kept a settling pile awake longer.

:::example[Three walls, one ball]
A sphere of radius 0.1 m flies at 240 m/s toward a wall 0.1 m thick, 6 m away. With a static wall, box3d's sweep stops the sphere at 5.85 m. With a kinematic wall and a plain sphere, the sphere ends the step at 8 m: only the end positions were tested. With a kinematic wall and `ContinuousCollision` on the sphere, it stops at 5.85 m again. The engine's own test `Bullets do not tunnel through thin kinematic walls` checks the last two cases.
:::

## Islands let piles rest

An **island** is a group of bodies that touch each other, directly or through a chain of other bodies. Two crates on opposite ends of the arena are two islands; a tower of crates is one. Box3d works island by island, and sleep works the same way.

A body is quiet when its speed stays below the **sleep threshold**, a speed in m/s. When every body of an island has stayed below the threshold for 0.5 s, box3d puts the whole island to sleep: it stops simulating the island, which costs nothing afterwards. Any single moving body keeps the island awake. A touch from an awake body, a force, an impulse or a new velocity wakes it again.

Strata raises the threshold from box3d's 0.05 m/s to 0.08 m/s; the measurement behind that choice comes below. A threshold that is too high stops slow rolling and sliding visibly early. One that is too low keeps piles awake and costs time.

A pile's time to sleep is chaotic: a ball that starts a tiny distance elsewhere changes the time by seconds. You cannot compare two settings by one run. The same lesson applies to any physics number you tune: compare medians over many starting layouts.

:::example[Will this body sleep?]
A crate slides at 0.5 m/s on a rough floor and slows by friction. Its speed falls until it is below 0.08 m/s; at that moment its sleep timer starts. Half a second later, if no body of its island has moved faster in between, the island sleeps. If a ball rolls into the crate before the timer ends, the timer starts over.
:::

## Engines solve contacts in four ways

Penalty methods treat a contact as a spring that grows with the overlap and add its force to the others. The method is simple, but a stiff spring needs a tiny step, and a soft one lets stacks sink.

Sequential impulses solve velocities directly and are stable for stacks, but a hard overlap correction still adds energy. Position-based methods move the positions straight to satisfy the rules and derive velocities afterwards. They are robust and good for cloth, but their stiffness depends on how many passes you run. The soft step of box3d keeps sequential impulses and adds sub-steps and a spring-like softness to the contacts.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Penalty forces | Small step needed | Stacks sink or explode | Lowest | Early engines, some cloth |
| Sequential impulses | Several passes per step | Stable stacks, adds energy at overlaps | Moderate | Box2D before version 3, Bullet |
| Position-based | Passes per step | Robust, stiffness depends on the passes | Moderate | Cloth and soft bodies in many engines |
| Soft step with sub-steps | Passes per sub-step, 4 sub-steps | Stable stacks, little added energy | Highest | box3d, Box2D 3 |

The sources are listed under further reading.

## Strata uses box3d's soft step and tunes five numbers

Strata runs box3d's contact step as it is and exposes five of its numbers as the project's `Physics.Simulation` section. The defaults are box3d's, except the sleep threshold.

| Field | Default | What it changes in the contact step |
| --- | --- | --- |
| `ContactRecycleDistance` | 0.05 m | How far two bodies may move before box3d works out a contact again instead of using the old one |
| `SleepThreshold` | 0.08 m/s | The speed below which a body counts as quiet |
| `ContactHertz` | 30 | The stiffness of soft contacts, up to the ceiling of an eighth of the sub-step rate |
| `ContactDampingRatio` | 10 | How strongly a soft contact is damped |
| `ContactPushSpeed` | 3 m/s | The cap of the push-out speed |

The values are clamped (hertz from 1 to 240, damping ratio from 0 to 100, push speed from 0.01 to 100 m/s) and apply from the next fixed step. The page on [tuning the simulation](../physics/tuning.md) shows how to change and measure them.

:::why[Why keep box3d's contact step and not write one?]
A contact step is years of work and the part of an engine that is hardest to test. Box3d's soft step is the newest approach in the table, and its author describes its stack stability in public. Strata keeps its code and its defaults and moves only what its measurements showed to matter. The cost is that a change in the library, such as the damping formula, becomes a change for Strata's games.
:::

One such change came from the previous library, Jolt. Box3d multiplies the velocity by $1 / (1 + d h)$ in every sub-step, where $d$ is the damping of the body and $h$ the sub-step, and Jolt multiplied it by $1 - d h$ per step. A body with a damping of 2 keeps 0.14 of its speed after a second at 240 sub-steps per second, where Jolt at 60 steps per second kept 0.13. A box that lands flat may slide a few mm.

### Defaults come from measurement

Strata chose its defaults by sweeps over representative scenes: a tower of 20 crates, a run of 64 standing blocks, balls in a pit and the Playground itself. A script, `Tools/PhysicsSweep.py`, plays each scene at each value and writes what it measured. A single run of a pile ranks nothing, so the pits are played in nine layouts and compared by their medians.

At the defaults the 2,000-ball pit slept after 14.7 s in the median, and between 8.3 and 34.2 s over the layouts. With these medians the sweep showed that a threshold of 0.08 m/s put both pits to sleep sooner than 0.05 m/s in every layout. It also showed that the recycle distance did not change how soon the 500-ball pit slept. The page on [tuning](../physics/tuning.md) gives the steps.

## What this choice cannot do

Box3d's soft step trades some exactness for stability. A body that spawns inside another leaves it at up to the push speed, not gently. A contact is softer than a rigid wall, so a stack of heavy bodies compresses a little: the Playground's 20-crate tower drifts 8 to 11 mm at the top. Contact stiffness above the ceiling has no effect.

Continuous collision covers static walls and bullets only. Joints belong to [the overview page](../physics/why.md), and this page covers contacts. The [list of what Strata does not do](../appendix/not-in-strata.md) names the rest.

## Common mistakes

- **Spawning bodies that overlap.** Symptom: light bodies shoot away at spawn. Fix: place bodies apart; box3d pushes an overlap out at up to 3 m/s.
- **Raising `ContactHertz` above 30.** Symptom: nothing changes. Fix: shorten the fixed step or raise `CollisionSteps`, or accept the ceiling.
- **Calling `AddForce` once in `OnUpdate`.** Symptom: a push that lasts one fixed step. Fix: call it in every fixed step the force should act, or use an impulse for a one-time kick.
- **Expecting slow bodies to bounce.** Symptom: a ball of restitution 1 dropped from 2 cm stays down. Fix: restitution acts only above 1 m/s of approach speed.
- **Expecting a plain fast body to stop at a kinematic wall.** Symptom: the body finishes behind the wall. Fix: set `ContinuousCollision` on the body.
- **Moving a sleeping body's transform without a signal.** Symptom: physics may keep the old pose. Fix: tell the scene that the transform changed, with `MarkModified`, as the :term[transform contract]{id=transform-contract} requires.
- **Judging a setting by one run of a pile.** Symptom: a conclusion that reverses on the next run. Fix: compare medians over many layouts.

## Summary

- A step changes velocities first and positions second (semi-implicit Euler), and the velocity of a point on a body is $v + \omega \times r$.
- A soft contact pushes an overlap out at $\mu\,\beta\,d$, capped by the push speed; with Strata's defaults, 0.1 m of overlap gives 0.85 m/s.
- A body tunnels when its step is longer than the wall plus its own size and nothing sweeps its path; static walls are always swept, moving ones only for bullets.
- A body bounces only above 1 m/s of approach speed and sleeps when its whole island stays below 0.08 m/s for 0.5 s.
- The five fields of `Physics.Simulation` are the recycle distance, the sleep threshold, the contact hertz, the damping ratio and the push speed.

## Check yourself

1. A wheel of radius 0.3 m turns at 5 radians per second about the z axis, and its center moves at 1 m/s along x. How fast does the point at the bottom move?

   - A. 0.5 m/s backward
   - B. 1 m/s
   - C. 2.5 m/s
   - D. 4 m/s

   :::answer{tests="integrate"}
   C. The offset of the bottom point is $(0, -0.3, 0)$, so $\omega \times r = (1.5, 0, 0)$, which adds to the center's 1 m/s. A is the top point, where the turn subtracts. B forgets the turn. D adds the radius times the rate twice.
   :::

2. With a sub-step of 1/240 s, contact hertz 30 and damping ratio 10, a soft contact has $\mu\,\beta = 8.55$ per second. How fast does it push out an overlap of 0.2 m, and an overlap of 0.6 m?

   :::answer{tests="contact-push"}
   For 0.2 m: $8.55 \times 0.2 = 1.71$ m/s. For 0.6 m the formula gives 5.13 m/s, so the cap of 3 m/s applies.
   :::

3. A bullet of radius 0.05 m flies at 120 m/s through a fixed step of 1/60 s toward a kinematic wall 0.2 m thick. Which statement holds?

   - A. It always stops, because box3d sweeps every body.
   - B. It tunnels unless `ContinuousCollision` is on or the wall is static.
   - C. It tunnels, because 120 m/s is above the speed limit of box3d.
   - D. It stops, because 2 m per step is less than the wall.

   :::answer{tests="tunnel"}
   B. The body moves 2 m per step and the wall is 0.2 m thick, so a discrete test can skip it, and box3d sweeps dynamic bodies against static ones only. A is wrong for a kinematic wall. C is wrong: the default limit is 400 m/s. D mixes up the step length and the thickness.
   :::

4. A ball of restitution 1 is dropped on a floor of restitution 0 from 5 cm. Does it bounce?

   :::answer{tests="bounce-sleep"}
   The impact speed is $\sqrt{2 \times 9.81 \times 0.05} = 0.99$ m/s, below the threshold of 1 m/s, so it does not bounce. The pair would use the larger restitution, 1, if the speed were above the threshold. It then rests and sleeps after 0.5 s below 0.08 m/s.
   :::

5. Which field of `Physics.Simulation` caps how fast an overlap is resolved?

   :::answer{tests="settings"}
   `ContactPushSpeed`, 3 m/s by default. `ContactHertz` sets the stiffness, `ContactDampingRatio` the damping, `SleepThreshold` when bodies count as quiet, and `ContactRecycleDistance` when old contacts are used again.
   :::

## Exercises

1. **Basic.** Compute the push-out speed of a soft contact with contact hertz 30 and damping ratio 10 at a sub-step of 1/240 s for an overlap of 0.3 m.

   :::answer[Worked solution]{tests="contact-push"}
   From the example, $\mu\,\beta = 0.942 \times 9.07 = 8.55$ per second. Then $u = 8.55 \times 0.3 = 2.56$ m/s, below the cap of 3 m/s, so the body leaves at 2.56 m/s.
   :::

2. **Medium.** Predict what the program below prints for a static wall, a kinematic wall and a kinematic wall with a bullet, and for drops from 2 cm and 1 m. Then run it.

   :::answer[Worked solution]{tests="tunnel bounce-sleep" solution="sketches/physics-dynamics-tunnel.cpp"}
   Predict: a sphere at 240 m/s moves 4 m per step, so its end positions are 0, 4 and 8 m, and the wall at 5.95 to 6.05 m is skipped by the end positions. Only the sweep sees it. The sweep stops the sphere at 5.85 m, 46 % into the second step. The drops meet the floor at 0.63 m/s and 4.43 m/s.

   ```cpp sketch="physics-dynamics-tunnel.cpp"
   // Predict then run: where a fast sphere meets a thin wall, and whether a dropped sphere of restitution 1 bounces.
   #include <cmath>
   #include <cstdio>

   // Positions of the sphere at the ends of steps are 0, 4 and 8 m; the wall spans 5.95 to 6.05 m, the sphere's radius is 0.1 m.
   bool Overlaps(float centerA, float radius, float front, float back)
   {
   	return centerA + radius > front && centerA - radius < back;
   }

   void Fire(const char* name, bool sweptTest)
   {
   	const float radius = 0.1f, front = 5.95f, back = 6.05f, stepLength = 4.0f; // 240 m/s at 60 steps per second
   	for (int step = 1; step <= 2; step++)
   	{
   		const float before = stepLength * static_cast<float>(step - 1);
   		const float after = stepLength * static_cast<float>(step);
   		const bool hit = sweptTest ? Overlaps(0.5f * (before + after), 0.5f * stepLength + radius, front, back)
   								   : Overlaps(after, radius, front, back);
   		if (hit)
   		{
   			const float fraction = (front - radius - before) / stepLength; // time of impact as a share of the step
   			std::printf("%s: stops at x = %.2f m, %.1f %% into step %d\n", name, front - radius, fraction * 100.0f, step);
   			return;
   		}
   	}
   	std::printf("%s: tunnels, ends at x = 8.00 m\n", name);
   }

   void Drop(float height)
   {
   	const float speed = std::sqrt(2.0f * 9.81f * height); // speed at the floor
   	std::printf("dropped from %.2f m: meets the floor at %.2f m/s, %s\n", height, speed,
   		speed > 1.0f ? "bounces" : "does not bounce");
   }

   int main()
   {
   	Fire("static wall, swept", true);
   	Fire("kinematic wall, no bullet", false);
   	Fire("kinematic wall, bullet", true);
   	Drop(0.02f);
   	Drop(1.0f);
   }
   ```

   ```text output-of="physics-dynamics-tunnel.cpp"
   static wall, swept: stops at x = 5.85 m, 46.2 % into step 2
   kinematic wall, no bullet: tunnels, ends at x = 8.00 m
   kinematic wall, bullet: stops at x = 5.85 m, 46.2 % into step 2
   dropped from 0.02 m: meets the floor at 0.63 m/s, does not bounce
   dropped from 1.00 m: meets the floor at 4.43 m/s, bounces
   ```

   1. **Lines 6–9:** two intervals overlap when each starts before the other ends.
   2. **Lines 18–19:** a discrete test looks at the end position only; a swept test looks at the whole interval the sphere covers in the step.
   3. **Line 22:** the time of impact as a share of the step.
   4. **Lines 32–34:** the speed at the floor is the square root of 2 g h, and only a speed above 1 m/s bounces.

   The kinematic wall without a bullet is the only tunnelling case, and only the drop from 1 m bounces.
   :::

3. **Hard.** A game fires arrows at 90 m/s at a fixed step of 1/60 s. The targets are wooden boards 3 cm thick that a script moves. Choose between more collision steps and a bullet, and say what each costs.

   :::answer[Worked solution]{tests="tunnel settings"}
   An arrow moves 1.5 m per step, 50 times the board's thickness, and the boards move, so box3d's static sweep does not apply. Setting `ContinuousCollision` on the arrows sweeps them against the boards at the cost of a sweep for a few bodies. Raising `CollisionSteps` to 50 would test every 3 cm and multiply the cost of the whole step by 50. Choose the bullet.
   :::

## Where it lives in Strata

The contact step is box3d's, in `Strata/vendor/box3d/src/solver.c` and `Strata/vendor/box3d/src/contact_solver.c`. Strata's use of it is in `Strata/src/Strata/Physics/PhysicsWorld.cpp`: `MakeBodySetup` sets the damping, the sleep threshold and the bullet flag, `ApplyMass` scales the mass, and the world definition sets continuous collision and the contact tuning. The `Physics.Simulation` section is in `Strata/src/Strata/Physics/PhysicsSimulationSettings.h`; the tests are `Physics.Settings` and the case `Bullets do not tunnel through thin kinematic walls`. The sweep script is `Tools/PhysicsSweep.py`. The page on [one step in Strata's code](../physics/world-step.md) follows a fixed step through these files.

## Further reading

- Erin Catto, "Solver2D" and its soft step article (beginner to intermediate): compares the solvers in the table on one set of scenes.
- Glenn Fiedler, "Integration Basics" at [Gaffer On Games](https://gafferongames.com/post/integration_basics/) (beginner): Euler rules and why the step matters.
- Matthias Müller and others, "Position Based Dynamics" (advanced): the position-based row of the table.
- Erin Catto, "Iterative Dynamics with Temporal Coherence" (advanced): sequential impulses and warm starting.
