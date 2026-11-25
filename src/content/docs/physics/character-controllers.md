---
id: physics/character-controllers
title: "Character controllers"
description: "How Strata walks a player capsule through a world of bodies: collide and slide, steps, slopes, ground snapping, platforms, pushing and the presence body."
kind: internals
size: L
tracks: [E]
needs: [physics/world-step, physics/queries]
time: 90
learn:
  - id: why-kinematic
    text: explain why a player capsule moves by collide and slide and not by forces
  - id: slide
    text: compute where a circle ends when it slides along a slope and stops at a wall
  - id: walker
    text: predict what a controller does at a 0.3 m step, a 0.5 m step, a 40 degree slope and a 50 degree slope
  - id: ground-state
    text: name the four ground states and the move each one allows
  - id: others
    text: explain how a controller meets platforms, crates, triggers and other characters
since: 0.3.0
status: final
---

A game needs a person who walks. You press a key, the person moves forward, climbs a stair, stops at a wall and stands on a hill. A **character controller** is the part of the engine that does this for one entity: an upright capsule that game code steers with a velocity, and that the engine moves through a world of bodies. Strata does not simulate the capsule with forces. It moves the capsule itself, asks the world what it touches, and writes the result to the entity once per :term[fixed step]{id=fixed-step}.

This page covers what a controller does and does not do. It walks, jumps, falls, slides down steep ground, rides platforms and pushes crates. It does not animate anything and it does not read input: other pages cover those. You will learn why a walker is built this way, how each rule of the move works with real numbers, and which rules to keep when you change the code.

## The problem and how engines solve it

Start with the obvious idea: make the player a dynamic capsule, as you would a crate, and push it with forces. The idea fails in four ways. Each failure teaches a rule of the real design.

First, an upright capsule on a force-driven body tips over. A push at the height of the chest turns the body as well as moving it, so you must lock its rotation. Second, it bounces and slides. A landing at speed returns some of the speed, and a body on a slope slides unless friction holds it. You tune friction until the body stands on a hill, and then it sticks to walls too.

Third, a stair is a wall to a capsule. Fourth, the body has inertia: when you release the key it keeps sliding, so you add damping, and the character feels heavy. Every fix makes another case worse. A person in a game follows the player's wishes, and the world must only stop it.

The kinematic answer is to move the capsule from game code, as a :term[kinematic body]{id=kinematic-body} moves, and to let the engine decide how far each move may go. The player's wish is a velocity. The engine turns it into a displacement for one step and asks the world where the capsule can go without entering anything.

The usual algorithm is **collide and slide**: move the capsule by the wish, find what it overlaps, and remove from the move the part that points into each surface. Repeat a few times until the move stops changing. A wall removes the part of the move that goes into the wall, and the rest slides along it. Strata gives the planes it finds (a point and a normal each) to a function of box3d. The function pushes the move out of each plane in turn, as the toy below does, and repeats until the move satisfies all of them.

Collide and slide alone gives a capsule that never enters a wall. A walker needs more:

- A stair is a small wall. The controller has a **step height**, the highest ledge it walks up. To step up, it lifts the capsule by up to that height, repeats the move and keeps the result if it lands on ground it can stand on.
- A slope is walkable when it is not steeper than a limit angle. Steeper ground counts as a wall for walking and as a slide for falling.
- Walking down a slope, the capsule leaves the ground at every step, because it moves forward before it falls. **Ground snapping** moves it back down to the ground, within the step height, so that the character follows the slope instead of hopping.
- The game needs to know what the capsule stands on. The **ground state** says whether it is on walkable ground, on steep ground, touching something that does not hold it, or in the air.
- What the capsule stands on may move, and the character must move with it.
- Crates are :term[dynamic bodies]{id=dynamic-body}. The capsule is not one, so it must hand them an impulse itself, and a crate that lands on the character must find something to land on.

Engines choose among a few approaches. Some keep the dynamic body and add a spring that holds it above the ground. That gives physical reactions, but the controls feel loose and the tuning never ends.

Unity's Character Controller, Godot's `CharacterBody3D` and Jolt's `CharacterVirtual` move a kinematic capsule with swept queries instead: a query that slides the capsule's shape along the move and reports the first contact. The control is exact and the same every time. The price is that you write every rule yourself, because the physics step does not know the capsule exists.

Some of these engines sweep one hit at a time: move to the first contact, slide, repeat. Others, Strata among them, collect all the planes at the new position and solve them together, which settles a corner in one solve. The table near the end of the page compares the choices.

## The map

A script never calls a controller directly. It calls the SDK's `CharacterController` (`Move`, `Jump`, `Teleport`), which reaches the :term[scene service]{id=scene-service} `ICharacterControl`. The physics module implements the service. It owns a `CharacterControllerSet` per physics world, with one record per controller entity, and calls the set's `Step` once per fixed step before box3d's own step.

The set moves the capsules with box3d's **mover** queries, the library's tools for characters. `b3World_CollideMover` collects the planes of everything a capsule overlaps. `b3SolvePlanes` turns a wanted move into one that satisfies the planes. `b3World_CastMover` finds how far a capsule can travel before it touches something. All three only read the world.

```mermaid caption="A script asks the scene service to move a character. The set of controllers moves the capsule with the library's mover queries, writes the entity and keeps a presence body in step." alt="A flow from a script through the character service and the set of controllers to the library's mover queries, with arrows from the set to the entity's transform and to the presence body."
flowchart LR
	S[Script: CharacterController] --> I[ICharacterControl]
	I --> C[CharacterControllerSet]
	C --> M[b3World_CollideMover, b3SolvePlanes, b3World_CastMover]
	C --> T[Entity transform]
	C --> P[Presence body]
	P --> W[box3d world]
	M --> W
```

Because the queries change nothing, the capsule alone would be invisible to the rest of physics. A crate would fall through the character, a trigger would not see it and a ray would miss it. Strata therefore gives each controller a **presence body**: a kinematic capsule in the box3d world that follows the controller. Bodies land on it, triggers detect it and queries hit it.

Its radius is 90 % of the character's, so that it stays clear of what the character touches at its sides and meets only what moves into the character. Its top is the character's top, so that a crate on the head rests where the head is. Its bottom stays a little above the ground.

Characters block each other through these bodies. A controller collides with the presence bodies of other controllers, as it does with any body on a layer that its own layer collides with. It never collides with the bodies of its own entity, and never with triggers. A trigger reaches a controller through its presence body, as `OnTriggerEnter` and `OnTriggerExit` of the scripts.

```mermaid caption="The character's capsule meets the world through queries only. Everything that moves into the character, a falling crate, a trigger or a ray, meets the smaller presence body instead." alt="A group labelled character holds a capsule moved by queries and a smaller presence body. The capsule collides with ground, walls and crates. A falling crate lands on the presence body, a trigger detects it and a ray hits it."
flowchart TB
	subgraph Character
		K[Capsule: moved by queries, radius 1.0]
		P[Presence body: kinematic, radius 0.9]
	end
	K -->|collides with| G[Ground, walls, crates, other presence bodies]
	F[Falling crate] -->|lands on| P
	T[Trigger] -->|detects| P
	R[Ray] -->|hits| P
```

## The contract

What a caller may assume, and what a caller must do, with the reason for each rule:

- The capsule stands on the entity's origin. Its bottom is the origin, and its height and radius come from the component. The entity's rotation and scale do not change it, so a tilted or scaled entity keeps an upright capsule of the same size. The reason: the step and slope rules only mean something for an upright capsule.
- A controller replaces a :term[rigid body]{id=rigid-body}. An entity with both a `RigidBody` and a controller is simulated as the rigid body, and the controller does nothing, because only one of them can move the entity.
- Gameplay gives a velocity, and the move reads it every step. Walking is horizontal. While gravity is on, the vertical part of the walk velocity is dropped, because gravity and the jump own the vertical motion. A script that sets a vertical walk velocity with gravity on therefore moves nothing; to fly or swim, set the controller's :term[gravity scale]{id=gravity-scale} to zero.
- What others ride moves in the fixed step. Platforms move inside the fixed step: in `OnFixedUpdate`, or as kinematic bodies. Then carrier and rider share one clock. A platform that a script moves every frame in `OnUpdate` is drawn where it is, and its rider a step behind.
- An entity moved from outside :term[teleports]{id=teleport} its controller. A script that writes the entity's transform, or the editor, moves the entity but not the controller's record. At the next step the set compares the entity's world position with where it put the controller. A difference above 1e-4 of the position's size (and at least 1e-4 m) counts as a move from outside, and the controller is placed there with no velocity kept.
- Moves do not see each other. In one step each controller reads the world as it was before the step, so two characters that walk into each other in one step both move. They block each other from the next step on.

:::rule[Presence bodies never recycle contacts]
A presence body is made with :term[contact recycling]{id=contact-recycling} off, as box3d advises for characters. The body is placed again at every step, so a recycled contact would keep the geometry of its old position and leave a ghost under a crate that the character carries. Kinematic bodies follow the same rule. See [the world step](../physics/world-step.md).
:::

## A toy version

:::question
Does `glm::dot(` or `std::span<const Plane>` look strange? Read [classes and calls](../basics/programming-3.md) and [templates](../basics/cpp-generic.md) first.
:::

Before the real code, a version that fits one screen. It works in two dimensions, with a circle instead of a capsule and lines instead of planes. A plane is a normal and an offset, and the circle's gap to a plane is the :term[signed distance]{id=signed-distance} of its centre minus the radius. The function aims at the end of the move, then pushes that target out of each plane it sinks into, four times.

```cpp sketch="physics-character-controllers-toy.cpp"
#include <array>
#include <cstdio>
#include <span>

#include <glm/glm.hpp>

// A wall or floor in two dimensions: the points where dot(Normal, point) equals Offset. The normal points to the free side.
struct Plane
{
	glm::vec2 Normal;
	float Offset;
};

// Moves a circle by `displacement`, stopping at the planes and sliding along them: each pass pushes the target out of the
// planes it would sink into, and several passes settle a corner where one push undoes another.
glm::vec2 CollideAndSlide(glm::vec2 position, glm::vec2 displacement, float radius, std::span<const Plane> planes)
{
	glm::vec2 target = position + displacement;
	for (int pass = 0; pass < 4; pass++)
	{
		for (const Plane& plane : planes)
		{
			const float gap = glm::dot(plane.Normal, target) - plane.Offset - radius;
			if (gap < 0.0f)
				target -= plane.Normal * gap;
		}
	}
	return target;
}

int main()
{
	const float radius = 0.5f;
	const Plane floor { { 0.0f, 1.0f }, 0.0f };
	const Plane wall { { -1.0f, 0.0f }, -3.0f }; // a wall at x = 3
	const Plane ramp { glm::normalize(glm::vec2(-1.0f, 1.0f)), -0.7071f }; // rises at 45 degrees from x = 1
	const std::array<Plane, 2> room = { floor, wall };
	const std::array<Plane, 2> slope = { floor, ramp };

	const glm::vec2 free = CollideAndSlide({ 0.0f, 0.5f }, { 0.5f, 0.0f }, radius, room);
	std::printf("free walk: x %.3f y %.3f\n", free.x, free.y);

	const glm::vec2 blocked = CollideAndSlide({ 2.0f, 0.5f }, { 2.0f, -0.2f }, radius, room);
	std::printf("into the wall at x = 3: x %.3f y %.3f\n", blocked.x, blocked.y);

	const glm::vec2 climbed = CollideAndSlide({ 0.5f, 0.5f }, { 1.0f, 0.0f }, radius, slope);
	std::printf("onto the ramp: x %.3f y %.3f\n", climbed.x, climbed.y);
	return 0;
}
```

```text output-of="physics-character-controllers-toy.cpp"
free walk: x 0.500 y 0.500
into the wall at x = 3: x 2.500 y 0.500
onto the ramp: x 1.146 y 0.854
```

1. **Lines 10–11:** a plane is a normal and an offset, so one pair of numbers describes a floor, a wall or a ramp.
2. **Line 19:** four passes, because pushing out of one plane can push the target into another.
3. **Line 23:** the gap is the target's distance to the plane, minus the radius; below zero means the circle sinks in.
4. **Lines 24–25:** the push removes exactly the sunk part, along the normal, and keeps the rest of the move.
5. **Line 36:** the ramp's offset is the plane through the point (1, 0), rising at 45 degrees.

The first case has nothing in the way, so the circle goes where it was sent. In the second, the move is 2 m to the right and 0.2 m down. The wall at x = 3 stops the circle at x = 2.5, one radius before the wall, and the floor keeps it at the height of its radius. The part of the move that the floor and the wall forbid is removed and the rest stays.

In the third case, a 45 degree ramp turns a move along the floor into a move up the ramp. Compute it by hand. The move is $(1, 0)$ and the ramp's normal is $(-0.707, 0.707)$, so the target $(1.5, 0.5)$ sinks 0.5 m into the plane once the radius counts. The push is $0.5 \times (-0.707, 0.707) = (-0.354, 0.354)$, and the circle ends at $(1.146, 0.854)$, which the program prints.

The toy is right as an idea and wrong for a game in five ways. It moves the target and never casts, so a fast circle could jump through a thin wall. It has no gravity and no ground. It cannot climb a step.

The toy does not treat steep ramps as walls, so a steep ramp would carry the circle up. And it knows nothing of other bodies. The real code repairs these in the order below.

## The real code

### The knobs

The component holds what an artist or a script sets. Read the units: lengths are in metres, and the slope is an angle in degrees.

```cpp src="Strata/src/Strata/Physics/PhysicsComponents.h#L75-L85"
struct CharacterControllerComponent
{
	float Height = 1.8f;           // Total height of the capsule in world units (a sphere when below twice the radius)
	float Radius = 0.3f;           // World units
	float StepHeight = 0.35f;      // Highest step it walks up, and how far it follows the ground down, in world units
	float MaxSlopeDegrees = 45.0f; // Steepest slope it walks up, in degrees from the horizontal
	uint32_t Layer = 0;            // Collision layer (0-31)
	float GravityScale = 1.0f;     // Times the scene's gravity
	float PushStrength = 200.0f;   // Largest force with which it pushes dynamic bodies, in newtons
	bool Enabled = true;           // A disabled controller neither moves nor collides; its entity moves freely
};
```

1. **Line 79:** the step height is also how far the capsule follows the ground down.
2. **Line 80:** the slope limit is an angle from the horizontal.
3. **Line 83:** the push strength is a force in newtons, and a push in one step is limited to this force times the step.

The defaults give a capsule 1.8 m tall and 0.6 m wide that climbs 0.35 m and walks slopes up to 45 degrees. The set limits the numbers: a radius above half the height becomes half the height, so a capsule shorter than its diameter is a sphere.

### Planes for a pass: `ShapePlanes` and `SlideMove`

The move runs three kinds of pass. `Across` is walking: ground too steep to stand on blocks like a wall, and walkable ground is climbed. `Vertical` is falling or rising: walkable ground holds the capsule, and steeper ground lets it slide down. `Standing` is for a capsule on the ground, an edge of a step included: whatever faces up holds it.

`ShapePlanes` makes the kinds differ. It rewrites the planes that box3d found before the solving function sees them.

```cpp src="Strata/src/Strata/Physics/CharacterControllers.cpp#L383-L402" symbol="ShapePlanes"
// Adapts the planes to a pass (see PassKind).
void ShapePlanes(std::vector<b3CollisionPlane>& planes, PassKind pass, float cosMaxSlope)
{
	for (b3CollisionPlane& plane : planes)
	{
		b3Vec3& normal = plane.plane.normal;
		const bool upward = normal.y > 1.0e-3f;
		const bool walkable = upward && normal.y >= cosMaxSlope;
		if (pass == PassKind::Across && upward && !walkable)
		{
			const float horizontal = std::sqrt(normal.x * normal.x + normal.z * normal.z);
			if (horizontal > 1.0e-4f)
				normal = b3Vec3 { normal.x / horizontal, 0.0f, normal.z / horizontal };
		}
		else if ((pass == PassKind::Vertical && walkable) || (pass == PassKind::Standing && upward))
		{
			normal = b3Vec3 { 0.0f, 1.0f, 0.0f };
		}
	}
}
```

1. **Line 390:** walkable means the normal's Y part reaches the :term[cosine]{id=cosine} of the slope limit.
2. **Lines 391–395:** across, a steep upward plane gets a horizontal normal: the slope becomes a vertical wall.
3. **Lines 397–399:** falling or standing, a walkable plane gets the flat normal $(0, 1, 0)$, so the capsule does not slide on it.

A flat floor has a normal with Y part 1, and a wall has a Y part of 0. At a limit of 45 degrees the :term[cosine]{id=cosine} is 0.707, and every normal with a larger Y part is walkable. Steep ground keeps its real normal in the vertical pass, which is why a capsule on it slides.

```cpp src="Strata/src/Strata/Physics/CharacterControllers.cpp#L404-L422" symbol="SlideMove"
// Moves a capsule from `position` by `displacement` as far as it can, sliding along what it meets (box3d's plane
// solver and mover cast). The planes of the last iteration stay in the query.
glm::vec3 SlideMove(MoverQuery& query, glm::vec3 position, const glm::vec3& displacement, const b3Capsule& capsule, PassKind pass, float cosMaxSlope)
{
	const glm::vec3 target = position + displacement;
	for (int iteration = 0; iteration < c_MoveIterations; iteration++)
	{
		CollidePlanes(query, position, capsule);
		ShapePlanes(*query.Planes, pass, cosMaxSlope);
		const b3PlaneSolverResult solved = b3SolvePlanes(ToB3(target - position), query.Planes->data(), static_cast<int>(query.Planes->size()));
		glm::vec3 delta = ToGlm(solved.delta);
		const float fraction = CastCapsule(query, position, capsule, delta);
		delta *= fraction;
		position += delta;
		if (glm::dot(delta, delta) < c_MoveTolerance * c_MoveTolerance)
			break;
	}
	return position;
}
```

1. **Line 408:** the target is fixed once, from where the move began.
2. **Lines 411–413:** collect the planes at the current position, shape them, and solve for the move that satisfies them.
3. **Lines 415–417:** cast the capsule along that move and go only as far as the first contact.
4. **Lines 418–419:** stop early when a round moves less than 0.1 mm.

`SlideMove` is the toy's loop with a real world. The cast is what the toy lacked: a fast capsule cannot pass through a thin wall, because the cast stops it at the wall. At most four rounds run, which is enough for a corner.

:::example[A 40 degree slope and a 50 degree slope]
The limit is 45 degrees, so the cosine to beat is 0.707. A 40 degree slope has a normal with Y part $\cos 40° = 0.766$, which is walkable. A 50 degree slope has $\cos 50° = 0.643$, which is not.

Walk at 2 m/s into the 40 degree slope. In one step of 1/60 s the wish is 0.0333 m along the floor. The across pass keeps the slope's real normal, and the plane removes the part of the move that goes into the slope. For a single plane the result is the move projected onto the slope. Its length is $0.0333 \cos 40° = 0.0255$ m, which is 1.53 m/s along the slope.

The character climbs slower than it walks, by 0.0196 m forward and 0.0164 m up each step, and the ground state stays on ground.

Walk at 2 m/s into the 50 degree slope. The across pass flattens its normal to horizontal, so the plane becomes a wall, and the whole move is removed: the capsule stops at the foot of the slope. Put a capsule on that slope instead, and the vertical pass keeps the real normal. Gravity pulls with $9.81 \sin 50° = 7.5$ m/s² along the slope, the capsule slides down, and the ground state reads steep ground. A test of the suite does this on a 60 degree slope and checks that the capsule drops more than 0.3 m in 30 steps, half a second.
:::

### The whole move: `MoveController`

`MoveController` runs once per controller and per fixed step. It reads the world as it was before the step and writes only its own record. Read it in four parts. The first builds the velocity.

```cpp src="Strata/src/Strata/Physics/CharacterControllers.cpp#L568-L586" from="const GroundContact& previousGround = record.Ground;" to="record.StepVelocity = velocity;" symbol="MoveController"
const GroundContact& previousGround = record.Ground;
const bool onGround = previousGround.State == CharacterGroundState::OnGround;
// Standing, it moves with what it stands on; in the air or on steep ground its motion goes on (sliding down a steep
// slope speeds up like falling).
glm::vec3 carried = onGround ? previousGround.Velocity : record.CarriedVelocity;
const bool jumping = record.JumpRequested;
if (jumping)
	carried.y = (onGround ? previousGround.Velocity.y : 0.0f) + record.JumpSpeed;
const glm::vec3 scaledGravity = gravity * record.GravityScale;
carried += scaledGravity * timestep;
// Moving away from the ground faster than c_LeaveGroundSpeed leaves it (a jump or a launch).
const bool leaving = carried.y - (onGround ? previousGround.Velocity.y : 0.0f) > c_LeaveGroundSpeed;

// Walking is horizontal; the vertical part of the walk velocity counts only without gravity (flying, swimming).
glm::vec3 walk = record.WalkVelocity;
if (record.GravityScale != 0.0f)
	walk.y = 0.0f;
const glm::vec3 velocity = carried + walk + record.Motion / timestep;
record.StepVelocity = velocity;
```

1. **Line 572:** standing, the character carries the ground's velocity; otherwise the velocity the last step left.
2. **Lines 574–575:** a jump replaces the vertical carried speed with the jump speed, plus the ground's own.
3. **Line 579:** moving away from the ground faster than 0.1 m/s counts as leaving it.
4. **Lines 582–584:** with gravity on, the vertical part of the walk velocity is dropped.
5. **Line 585:** the step's velocity is the carried, the walk and the queued motion divided by the step.

The carried velocity is what the character keeps from step to step. In the air or on steep ground it keeps falling or sliding, so a launch from a platform keeps the platform's motion. The move starts from this given velocity, never from the velocity measured from the last move. A step up lifts the capsule by a whole step in one step, and reading that back as speed would launch the character.

The second part is the move across, and the step up.

```cpp src="Strata/src/Strata/Physics/CharacterControllers.cpp#L588-L616" from="const glm::vec3 start = record.Position;" to="position = stepped;" symbol="MoveController"
const glm::vec3 start = record.Position;
const b3Capsule capsule = MakeCapsule(record.Shape, 1.0f);
const glm::vec3 across(velocity.x * timestep, 0.0f, velocity.z * timestep);

// Across: slide along walls and up walkable slopes.
glm::vec3 position = SlideMove(query, start, across, capsule, PassKind::Across, record.CosMaxSlope);
GatherPushes(query, record, position);
// What blocked the carried motion across stops it (a wall stops a slide or a flight).
glm::vec3 horizontal(carried.x, 0.0f, carried.z);
horizontal = ToGlm(b3ClipVector(ToB3(horizontal), planes.data(), static_cast<int>(planes.size())));
horizontal.y = 0.0f;

// Steps: blocked while standing, it tries the same move from up to a step higher and keeps it if it lands on walkable
// ground further along.
const float wanted = glm::length(glm::vec2(across.x, across.z));
const float made = glm::length(glm::vec2(position.x - start.x, position.z - start.z));
if (onGround && !jumping && record.StepHeight > 0.0f && wanted > c_MoveTolerance && made < wanted * 0.99f)
{
	const glm::vec3 up(0.0f, record.StepHeight, 0.0f);
	const glm::vec3 lifted = start + up * CastCapsule(query, start, capsule, up);
	glm::vec3 stepped = SlideMove(query, lifted, across, capsule, PassKind::Across, record.CosMaxSlope);
	const glm::vec3 down(0.0f, -(lifted.y - start.y) - c_ContactMargin, 0.0f);
	stepped += down * CastCapsule(query, stepped, capsule, down);
	const float steppedMade = glm::length(glm::vec2(stepped.x - start.x, stepped.z - start.z));
	// It must stand on walkable ground no higher above its feet than the step height (on a higher step's edge it
	// would only hang on).
	const GroundContact landed = FindGround(query, record, stepped);
	if (steppedMade > made + c_MoveTolerance && landed.State == CharacterGroundState::OnGround && landed.Point.y - start.y <= record.StepHeight + c_ContactMargin)
		position = stepped;
```

1. **Line 590:** the across move is horizontal only; the vertical motion has its own pass.
2. **Line 593:** slide along walls and up walkable slopes.
3. **Line 604:** try a step only when standing, not jumping, with a step height, and when less than 99 % of the wish was made.
4. **Lines 607–610:** lift by the step height or less, slide again, then put the capsule down by what it was lifted plus 2 cm.
5. **Lines 614–616:** keep the stepped position only if it made more progress and stands on walkable ground no higher than the step height.

The last condition rejects a high ledge that the capsule would only hang on by its rounded bottom.

:::example[A 0.3 m step and a 0.5 m step]
The step height is 0.35 m. Two static boxes stand across the path, one 0.3 m high and one 0.5 m high, and the character walks at 2 m/s. The tests of the suite build exactly this scene.

At the 0.3 m box the across slide is blocked, so the move made is below 99 % of the wish and the step test runs. The capsule is lifted by 0.35 m, slides across and is cast down by 0.37 m. It lands on the box's top, 0.3 m above its start. That is walkable ground, and 0.3 is at most 0.35 plus 0.02, so the step is kept. The test expects the character 0.3 m up and on the ground.

At the 0.5 m box the capsule is lifted by the same 0.35 m. Its lower sphere then has the centre 0.65 m above the ground, so the centre sits 0.15 m above the box's corner, and the sphere's radius is 0.3 m. For a corner, box3d gives the plane whose normal points from the corner to the sphere's centre, so this plane leans back with a Y part of $0.15 / 0.3 = 0.5$. That is below 0.707, so the across pass makes it a wall and the lifted move makes no progress.

The step fails, and the character stays about one radius, 0.3 m, from the box's face. The test expects it no more than 5 cm past that spot, within 2 cm of height zero.
:::

The third part is the vertical pass and the snap.

```cpp src="Strata/src/Strata/Physics/CharacterControllers.cpp#L619-L638" from="// Vertical: fall, rise or stand." to="position = snapped;" symbol="MoveController"
// Vertical: fall, rise or stand.
const glm::vec3 vertical(0.0f, velocity.y * timestep, 0.0f);
position = SlideMove(query, position, vertical, capsule, onGround && !leaving ? PassKind::Standing : PassKind::Vertical, record.CosMaxSlope);
// What the collisions left of the carried motion: a floor stops a fall, a ceiling a rise, steep ground turns a fall
// into a slide down along it.
glm::vec3 next = ToGlm(b3ClipVector(ToB3(glm::vec3(horizontal.x, carried.y, horizontal.z)), planes.data(), static_cast<int>(planes.size())));

// Stick to the ground: walking down a slope or a step within the step height, it stays on the ground.
if (onGround && !leaving && record.StepHeight > 0.0f)
{
	const GroundContact ground = FindGround(query, record, position);
	if (ground.State == CharacterGroundState::InAir || ground.State == CharacterGroundState::NotSupported)
	{
		const glm::vec3 down(0.0f, -record.StepHeight, 0.0f);
		const float fraction = CastCapsule(query, position, capsule, down);
		if (fraction < 1.0f)
		{
			const glm::vec3 snapped = position + down * fraction;
			if (FindGround(query, record, snapped).State == CharacterGroundState::OnGround)
				position = snapped;
```

1. **Line 621:** a capsule that stood and did not leave uses the standing pass, so it does not slide off an edge.
2. **Line 624:** clip the carried velocity by the planes: a floor stops a fall, a ceiling a rise.
3. **Lines 632–638:** if nothing holds the capsule now, cast down by the step height and accept only walkable ground.

That last block is ground snapping. A character that walks down a 0.3 m step follows it instead of flying for a moment, and the next step starts with a ground state of `OnGround`.

The fourth part reads the ground state and prepares the next step.

```cpp src="Strata/src/Strata/Physics/CharacterControllers.cpp#L643-L661" from="record.Ground = FindGround(query, record, position);" to="record.Velocity = (record.NewPosition - start) / timestep;" symbol="MoveController"
record.Ground = FindGround(query, record, position);
if (leaving && record.Ground.State == CharacterGroundState::OnGround)
	record.Ground.State = CharacterGroundState::InAir; // Rising off the ground (a jump)
if (record.Ground.State == CharacterGroundState::InAir)
{
	record.Ground.Normal = glm::vec3(0.0f);
	record.Ground.Velocity = glm::vec3(0.0f);
	record.Ground.Body = b3_nullBodyId;
	record.Ground.Entity = UUID::Null();
}
// Standing, it carries what it stands on (so that it keeps the motion of a platform it walks off).
record.CarriedVelocity = record.Ground.State == CharacterGroundState::OnGround ? record.Ground.Velocity : next;
if (collectContacts)
	GatherTouching(query, record, position);
else
	record.Touching.clear();

record.NewPosition = IsFinite(position) ? position : start;
record.Velocity = (record.NewPosition - start) / timestep;
```

1. **Lines 644–645:** a capsule that left the ground this step is in the air, even if ground is still in reach.
2. **Line 654:** standing, it carries what it stands on, so it keeps a platform's motion when it walks off.
3. **Lines 660–661:** the new position is kept only if it is finite, and the measured velocity is stored for scripts.

`FindGround` collects the planes within 2 cm of a slightly larger capsule, keeps those below the lower sphere's centre that face up, and takes the most upward. A plane no steeper than the limit gives `OnGround`. A steeper one gives `OnSteepGround`. Touching only something beside or above it gives `NotSupported`, and touching nothing gives `InAir`.

```mermaid caption="The four ground states and what moves the controller between them. A jump or a launch leaves the ground, and a wall or a ceiling alone gives no support." alt="A state diagram with four states: on ground, on steep ground, not supported and in air. Arrows show landing, jumping, walking onto steep ground, touching only a wall and sliding off."
stateDiagram-v2
	[*] --> InAir
	InAir --> OnGround: lands on walkable ground
	InAir --> OnSteepGround: lands on steep ground
	InAir --> NotSupported: touches only a wall or a ceiling
	OnGround --> InAir: jump or launch, or walks off an edge
	OnGround --> OnSteepGround: walks onto steep ground
	OnSteepGround --> OnGround: slides to walkable ground
	OnSteepGround --> InAir: slides off
	NotSupported --> InAir: moves away from the wall
```

:::example[A turning platform]
A kinematic platform turns at 1 :term[radian]{id=radian} per second around its centre, and a character stands 3 m from the centre. The ground's velocity where the capsule touches the platform is the speed $\omega r = 1 \times 3 = 3$ m/s, along the tangent of the circle. The character is `OnGround`, so its carried velocity is 3 m/s, and each step moves it 0.05 m along the tangent.

The next step reads the point velocity again, at the spot where the capsule now stands, so the direction follows the turn. The character's own rotation does not turn, because the controller writes only the entity's translation. If the character walks off the edge, it keeps the 3 m/s as its carried velocity, and gravity does the rest. A jump from the platform starts with the platform's vertical velocity plus the jump speed.
:::

### Pushing: `PushBodies`

During the across pass the move records each dynamic body it met, once per body. After every controller has moved, the set walks them in order and pushes. A push has no bounce: the body gets the impulse that makes the spot where it touches the character move away as fast as the character closes in on it. The character then keeps its pace instead of pressing against the body.

```cpp src="Strata/src/Strata/Physics/CharacterControllers.cpp#L695-L715" from="const float maxImpulse = record.PushStrength * timestep;" to="b3Body_ApplyLinearImpulse(push.Body, ToB3(impulse), ToB3(push.Position), true);" symbol="PushBodies"
const float maxImpulse = record.PushStrength * timestep;
for (const PushContact& push : record.Pushes)
{
	if (!b3Body_IsValid(push.Body) || b3Body_GetType(push.Body) != b3_dynamicBody || !b3Body_IsEnabled(push.Body))
		continue;
	// The normal points from the body to the character: the character closes in while the body's point moves
	// towards it faster than the character moves away.
	const float closingSpeed = glm::dot(push.Velocity - record.StepVelocity, push.Normal);
	if (!(closingSpeed > 0.0f))
		continue;
	const glm::vec3 arm = push.Position - ToGlm(b3Body_GetWorldCenter(push.Body));
	const glm::vec3 turn = glm::cross(arm, push.Normal);
	const b3Vec3 inverseInertiaTurn = b3MulMV(b3Body_GetWorldInverseRotationalInertia(push.Body), ToB3(turn));
	const float inverseMassAtContact = b3Body_GetInverseMass(push.Body) + glm::dot(turn, ToGlm(inverseInertiaTurn));
	if (!(inverseMassAtContact > 0.0f))
		continue;
	const float magnitude = std::min(closingSpeed / inverseMassAtContact, maxImpulse);
	glm::vec3 impulse = -magnitude * push.Normal;
	impulse.y = std::max(impulse.y, 0.0f);
	if (impulse != glm::vec3(0.0f))
		b3Body_ApplyLinearImpulse(push.Body, ToB3(impulse), ToB3(push.Position), true);
```

1. **Line 695:** the most a push may give in one step is the push strength times the step.
2. **Line 702:** the closing speed is how fast the :term[contact point]{id=manifold} comes at the character along the normal.
3. **Lines 705–708:** the inverse of the body's effective mass at the contact point.
4. **Line 711:** the impulse is the closing speed times the effective mass, capped.
5. **Line 713:** a push never points down.

[Dynamics](../physics/dynamics.md) derives the effective mass. A box pushed off its centre turns as well as slides. It gives way sooner than its mass says.

$$m_e = \frac{1}{\frac{1}{m} + (r \times n) \cdot I^{-1} (r \times n)}$$

Here $m_e$ is the effective mass in kilograms. $m$ is the body's mass, $r$ is the arm from the body's centre to the contact point in metres, $n$ is the contact normal and $I^{-1}$ is the inverse inertia of the body. Read the cross as "cross" and the dot as "dot". Pushed through the centre, $r$ is zero and $m_e$ equals $m$.

The impulse is capped at the push strength times the step, so a strength of 200 newtons gives at most $200 / 60 = 3.3$ newton-seconds per step.

A second block of `PushBodies` lets a character press on the dynamic body it stands on, with its weight of 70 kg under the scene's gravity. The body feels all of the weight while the character stands, and only the part that presses into the surface, along its normal, while the character slides.

:::example[A box in the way]
Suppose a 5 kg box lies in front of a character who walks at 2 m/s, and the contact is on the line through the box's centre, so $m_e$ is 5 kg. The closing speed is 2 m/s, so the wanted impulse is $2 \times 5 = 10$ newton-seconds. The cap with the default strength is 3.3, so the box gets 3.3 newton-seconds and a speed of $3.3 / 5 = 0.67$ m/s in the first step.

The character's own move still stops at the box in that step, as at a wall. After about three steps, ignoring friction, the box moves nearly as fast as the character and the closing speed falls, so the impulse falls below the cap. With a push strength of 0 the box gets nothing, and the character stays at the box like at a wall. A test of the suite does both with a 5 kg box.
:::

### The presence body

The set creates the presence body when a controller starts and teleports it after every move.

```cpp src="Strata/src/Strata/Physics/CharacterControllers.cpp#L290-L309" symbol="CreatePresenceBody"
// The presence body of a record at `position`: kinematic, on the controller's layer, seen by sensors. Moving wakes it;
// standing still it falls asleep like any body (at the world's sleep threshold), so that its contacts with sleeping
// bodies (a crate on its head) last. It never recycles contacts, as box3d advises for characters: it is teleported every
// step, and a recycled contact would keep the manifold of where it stood (a ghost under a crate it pushes or carries).
void CreatePresenceBody(CharacterControllerSetData& data, ControllerRecord& record, const glm::vec3& position)
{
	b3BodyDef bodyDefinition = b3DefaultBodyDef();
	bodyDefinition.type = b3_kinematicBody;
	bodyDefinition.position = ToB3(position);
	bodyDefinition.sleepThreshold = data.Settings->SleepThreshold;
	bodyDefinition.enableContactRecycling = false;
	record.PresenceBody = b3CreateBody(data.World, &bodyDefinition);
	b3ShapeDef shapeDefinition = b3DefaultShapeDef();
	shapeDefinition.userData = reinterpret_cast<void*>(static_cast<uintptr_t>(static_cast<uint64_t>(record.EntityID)));
	shapeDefinition.filter = PhysicsFilters::MakeShapeFilter(record.Shape.Layer, data.Settings->LayerCollisionMasks);
	shapeDefinition.enableSensorEvents = true;
	shapeDefinition.enableContactEvents = true;
	const b3Capsule capsule = MakeCapsule(record.Shape, c_PresenceRadiusFraction);
	record.PresenceShape = b3CreateCapsuleShape(record.PresenceBody, &shapeDefinition, &capsule);
}
```

1. **Line 297:** the body is kinematic: other bodies react to it, and only the controller moves it.
2. **Line 300:** contact recycling is off, as the rule above requires.
3. **Line 303:** the shape carries the entity's identifier, so that contacts and triggers name the character.
4. **Line 307:** the capsule uses the radius fraction of 0.9, so 0.27 m for the default radius, and keeps the full height.

Standing still, the body falls asleep like any body, so that a crate resting on the head keeps its contact with a sleeping body. Each step the set places it with a transform, never with a velocity. A velocity would carry what rests on it by friction and push what it touches harder than the push strength allows.

What a controller touches at the end of its move joins the contact pairs of the step, one contact per touched entity. Scripts see them as `OnCollisionEnter` and `OnCollisionExit`, like those of any body.

### One step of all controllers

`CharacterControllerSet::Step` runs the moves in parallel and writes the results in order.

```cpp src="Strata/src/Strata/Physics/CharacterControllers.cpp#L967-L997" from="const uint32_t count = static_cast<uint32_t>(records.size());" to="scene.MarkTransformsChanged(output.Moved);" symbol="CharacterControllerSet::Step"
const uint32_t count = static_cast<uint32_t>(records.size());
const uint32_t threads = JobSystem::IsInitialized() ? JobSystem::GetWorkerThreadCount() + 1 : 1;
const uint32_t batchSize = std::max(c_MinBatchSize, (count + threads * c_BatchesPerThread - 1) / (threads * c_BatchesPerThread));
const uint32_t batches = (count + batchSize - 1) / batchSize;
const auto move = [&](uint32_t begin, uint32_t end)
{
	for (uint32_t index = begin; index < end; index++)
		MoveController(data, *records[index], timestep, gravity, collectContacts);
};
if (batches > 1 && JobSystem::IsInitialized())
	JobSystem::ParallelFor(count, batchSize, move);
else
	move(0, count);

// After the moves, on the main thread in controller order: write the entities, move the presence bodies, push.
for (ControllerRecord* record : records)
{
	if (record->NewPosition != record->Position && IsFinite(record->NewPosition))
	{
		if (WriteBack(data, *record))
		{
			output.Moved.push_back(record->Handle);
			record->Position = record->NewPosition;
		}
		MovePresenceBody(*record);
	}
	PushBodies(*record, timestep, gravity);
	if (collectContacts)
		output.Contacts.insert(output.Contacts.end(), record->Touching.begin(), record->Touching.end());
}
scene.MarkTransformsChanged(output.Moved);
```

1. **Line 969:** a batch holds at least 16 controllers, and the count is split into about four batches per thread; the batches change with the threads, the results do not.
2. **Lines 976–979:** the moves run on the job system when there is more than one batch, and in order otherwise.
3. **Lines 981–982:** the shared writes run in controller order on the :term[main thread]{id=main-thread}.
4. **Lines 986–988:** write the entity's translation, and list it as moved.
5. **Line 997:** signal the scene's caches once, for every entity written.

Before this code, on the main thread, the set teleports the controllers whose entities moved from outside and reads each parent's :term[world transform]{id=world-transform} for the :term[write-back]{id=write-back}. The moves run in batches because box3d's queries only read the world. After them, in order, the set writes each translation (divided by the parent's transform when there is a parent), moves the presence body and pushes.

The results therefore do not depend on the number of threads: the parallel part writes only each controller's own record, and the order of the shared writes is fixed. The last line is the :term[transform contract]{id=transform-contract} of [the world step](../physics/world-step.md).

The root-motion hook, `AddCharacterMotion`, queues a displacement that `MoveController` adds to the walk, so that an animation can drive a character through the same move. [Root motion](../animation/root-motion.md) explains it.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Dynamic capsule with a locked rotation and forces | A first attempt in many tutorials | Interaction with every body for free, no code for platforms or pushing | Loose control, sliding on slopes, no steps, hard tuning |
| Dynamic capsule held above the ground by a spring | Games that want the character to react like a body | Natural reactions to bumps and one simulation | Steps and slopes need hand tuning, and the ground state is a guess |
| Kinematic capsule moved by sweeps, one hit at a time | Unity's Character Controller, Godot's `CharacterBody3D` | A simple, well-known algorithm | Corners need extra rules, and each sweep costs a query |
| Kinematic capsule with all planes solved together (Strata) | Jolt's `CharacterVirtual`, box3d's mover | Corners in one solve, reads that run side by side | Every rule (steps, snapping, platforms, pushing) written by hand |

Strata chose the fourth because players judge control, and because the reads run on every core the job system has. The cost is a set of rules that you must keep correct.

## How it is tested

The suite `Physics.Character` of `StrataTests/src/Physics/PhysicsCharacterTests.cpp` holds cases for standing and falling, steps, slopes, snapping, platforms, jumps and pushing. Other cases cover the weight on a dynamic ground, layers, contacts and triggers, component changes, invalid requests, root motion, scripts and sub-scenes.

One case moves 48 characters over crates, a step and a ramp with 0, 1, 2 and 4 workers and requires the same final poses. The step case builds the 0.3 m and 0.5 m boxes of the example above.

Run the suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Physics.Character`. The tests build their scenes in code with the helpers of the file, so you can copy a case, change a number and read the result.

## Changing it safely

A new knob is a field of `CharacterControllerComponent`, with its registration, a case in the suite and a line in the feature test. A property that another property can disable also gets an :term[inactive reason]{id=inactive-reason}. A new host function for scripts is appended at the end of the host table, never inserted.

- Keep the moves read-only. A write to shared state in `MoveController` breaks the guarantee that results do not depend on the thread count. Writes belong in the serial part of `Step`.
- Keep the pass kinds. Changing what `ShapePlanes` does for one pass changes steps, slopes and sliding together, so run the step and slope cases first.
- Keep the presence body's contact recycling off, and place it with a transform, never a velocity.
- Signal every write to a transform: the scene's caches depend on it.
- A change that alters the move is a change of :term[determinism]{id=determinism}: the cross-thread case must still pass.

## Summary

- A player is not a dynamic capsule: forces make it tip, bounce, slide and feel heavy, so Strata moves a kinematic capsule by collide and slide.
- Collide and slide removes from each move the part that goes into a plane and repeats; the real code adds casts, passes and steps to the toy.
- A controller steps up a ledge up to its step height, walks slopes up to its limit angle, treats steeper ones as walls across and slides along them, and snaps down.
- The ground state is on ground, on steep ground, not supported or in air; platforms carry the character through the ground's velocity.
- The presence body lets crates land, triggers fire and rays hit; pushes are capped by the push strength times the step; the moves read in parallel and write in order.

## Check yourself

1. A level designer builds a stair of 0.3 m steps and a ramp of 55 degrees. With the defaults, which can a character climb?

   :::answer{tests="walker"}
   The stair, because 0.3 m is below the step height of 0.35 m. Not the ramp: 55 degrees is steeper than the 45 degree limit, so the walking pass turns it into a wall. A limit of 60 degrees would make the ramp walkable.
   :::

2. A script sets the walk velocity to $(0, 3, 0)$ every step to climb, with gravity on. The character does not rise. Why?

   A. The step height is too small.

   B. The vertical part of the walk velocity is dropped while gravity is on.

   C. The presence body blocks the move.

   D. The slope limit is exceeded.

   :::answer{tests="why-kinematic"}
   B is right: gravity and the jump own the vertical motion, so a walk velocity with gravity on keeps only its horizontal part. A and D concern ledges and slopes, which are not involved. C is wrong because a capsule never collides with its own presence body. Use a jump, or set the gravity scale to zero.
   :::

3. A capsule stands on a 50 degree slope. Which ground state does `GetGroundState` report, and why?

   :::answer{tests="ground-state"}
   Steep ground. The cosine of 50 degrees, 0.643, is below the limit's 0.707, so the contact is ground but not walkable. The capsule cannot stand, and gravity slides it down.
   :::

4. The toy's circle, radius 0.5, starts at x = 1.5 and moves by $(2, 0)$ towards a wall at x = 3 whose normal is $(-1, 0)$. Where does it stop, and how much of the move is removed?

   :::answer{tests="slide"}
   The circle ends at x = 2.5. The target would be x = 3.5, which is 1 m too far: the circle would sink 1 m into the wall, counting its radius. The push removes that 1 m of the move, the part that points into the wall, and nothing of the move along it.
   :::

5. A crate falls on a standing character's head, and a trigger volume surrounds the character. Which body does each meet?

   :::answer{tests="others"}
   Both meet the presence body. The character's own capsule is a query shape that exists only for the controller's moves, so a crate would fall through it. The presence body is in the world, so the crate lands and the trigger fires `OnTriggerEnter`.
   :::

## Exercises

1. **Basic.** The sketch below repeats the arithmetic of a slope. With the limit of 45 degrees and a walk speed of 2 m/s, predict the rise per second on a 30 degree and a 40 degree slope, and what happens at 50 degrees. Run it and compare.

   :::answer[Worked solution]{tests="slide,walker" solution="sketches/physics-character-controllers-slopes.cpp"}
   The move along a slope keeps the length $v \cos\theta$ and rises by $v \cos\theta \sin\theta$ per second. At 30 degrees that is $2 \times 0.866 \times 0.5 = 0.87$ m/s, and at 40 degrees $2 \times 0.766 \times 0.643 = 0.98$ m/s. At 50 degrees the slope is steeper than the limit, so the walking pass makes it a wall and the rise is zero.

   ```cpp sketch="physics-character-controllers-slopes.cpp"
   // What a walker does on a slope: the move along it keeps the part of the wish that does not point into the slope.
   #include <cmath>
   #include <cstdio>
   #include <initializer_list>

   int main()
   {
   	const float pi = 3.14159265f;
   	const float maxSlopeDegrees = 45.0f;
   	const float walkSpeed = 2.0f;
   	const float cosMaxSlope = std::cos(maxSlopeDegrees * pi / 180.0f);

   	for (const float degrees : { 30.0f, 40.0f, 50.0f })
   	{
   		const float angle = degrees * pi / 180.0f;
   		// A plane is walkable when the Y part of its normal, the cosine of the slope angle, reaches the limit's cosine.
   		const bool walkable = std::cos(angle) >= cosMaxSlope;
   		const float alongSlope = walkable ? walkSpeed * std::cos(angle) : 0.0f;
   		const float rise = alongSlope * std::sin(angle);
   		std::printf("%2.0f degrees: %s, %.2f m/s along the slope, rising %.2f m/s\n", degrees, walkable ? "walkable" : "a wall", alongSlope, rise);
   	}
   	return 0;
   }
   ```

   ```text output-of="physics-character-controllers-slopes.cpp"
   30 degrees: walkable, 1.73 m/s along the slope, rising 0.87 m/s
   40 degrees: walkable, 1.53 m/s along the slope, rising 0.98 m/s
   50 degrees: a wall, 0.00 m/s along the slope, rising 0.00 m/s
   ```

   1. **Line 11:** the limit's cosine, the test every normal's Y part must pass.
   2. **Line 17:** walkable means the slope's cosine reaches it.
   3. **Line 18:** a wall gives no motion along it; a walkable slope keeps the cosine part of the wish.
   4. **Line 19:** the rise is the motion along the slope times the :term[sine]{id=sine} of its angle.
   :::

2. **Medium.** A platform turns at 0.5 radians per second, and a character stands 4 m from its centre. How fast does the platform carry the character, how far in one step, and what does the character keep if it steps off?

   :::answer{tests="others"}
   The speed is $0.5 \times 4 = 2$ m/s, and a step moves the character $2 / 60 = 0.033$ m along the tangent. Standing on walkable ground, its carried velocity is the ground's, so after it steps off it keeps the 2 m/s tangent velocity, until gravity and the world change it.
   :::

3. **Hard.** Set a breakpoint in `PushBodies` and walk a controller into a crate. Find where the closing speed, the effective mass at the contact and the cap are computed.

   :::answer[Worked solution]{tests="others"}
   All three are in `PushBodies` in `Strata/src/Strata/Physics/CharacterControllers.cpp`. The closing speed is the :term[dot product]{id=dot-product} of the velocity difference and the contact normal. `inverseMassAtContact` is the body's inverse mass plus the turn term. `maxImpulse` is `PushStrength` times the :term[timestep]{id=time-step}, and the impulse is the smaller of `closingSpeed / inverseMassAtContact` and `maxImpulse`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsComponents.h`: `CharacterControllerComponent`.
- `Strata/src/Strata/Physics/CharacterControllers.h` and `Strata/src/Strata/Physics/CharacterControllers.cpp`: `CharacterControllerSet`, `ShapePlanes`, `SlideMove`, `MoveController`, `PushBodies`, `CreatePresenceBody`.
- `Strata/src/Strata/Scene/SceneServices.h`: `ICharacterControl`, `CharacterState`, `CharacterGroundState`.
- `StrataScriptCore/Include/StrataScript/CharacterController.h`: the SDK's `CharacterController`.
- Tests: `StrataTests/src/Physics/PhysicsCharacterTests.cpp`, suite `Physics.Character`.
- Inspector: the component's fields under **Character Controller**.

## Further reading

- The box3d documentation, the character mover pages: the queries Strata builds on (intermediate).
- Jolt Physics documentation, "CharacterVirtual": a kinematic character that solves contact planes (advanced).
- Unity manual, "Character Controller component": the same problem solved for game makers (beginner).
- Godot documentation, "Using CharacterBody3D": move and slide with floor and slope settings (beginner).
- Christer Ericson, "Real-Time Collision Detection": swept volumes (advanced).
