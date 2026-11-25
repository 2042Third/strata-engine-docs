---
id: physics/bodies-colliders
title: "Rigid bodies and colliders"
description: "How an object becomes something physics can simulate: a body with a type and a material, made of simple collider shapes, composed from an entity hierarchy."
kind: concept
size: M
tracks: [E]
needs: [world/scene-graph, basics/math-vectors]
time: 45
learn:
  - id: model
    text: explain why physics collides simple shapes and not the rendered mesh
  - id: body-types
    text: choose static, dynamic or kinematic for an object and name what goes wrong when it is moved like another type
  - id: shapes
    text: choose a collider shape for an object and explain why a triangle mesh stays on static bodies
  - id: material
    text: compute the friction and restitution of a contact from two materials
  - id: hierarchy
    text: predict which bodies an entity hierarchy gives
since: 0.3.0
status: final
---

Open the Physics Playground in the editor and press play. A crate falls, lands on the floor and tips over. The crate you see is a mesh: a list of triangles that the :term[renderer]{id=renderer} draws. Nothing in a list of triangles says how heavy the crate is, how slippery it is, or what counts as inside it. Physics needs answers to those questions before it can move anything.

This page shows what Strata adds to an object so that physics can simulate it: a body with a type and a material, made of simple shapes. You will learn how to choose them, and how Strata builds bodies from a hierarchy of entities.

## The rendered mesh is the wrong thing to collide

The obvious plan is to collide the mesh that the renderer draws. Every triangle of one crate would be tested against every triangle of the floor. That plan fails twice.

First, cost. A crate model may hold 2,000 triangles, and a floor model another 2,000. Testing every pair is 4 million tests for one contact, and a scene has hundreds of contacts in every step of the simulation.

Second, meaning. A mesh is a skin. A leaf, a flag or a wall made of open sheets has no inside. Physics cannot say whether a point is in it, how much it weighs or which way to push a body that sank into it.

Physics therefore uses its own, much simpler description of an object, drawn from a short list of shapes that are cheap to test and that always have an inside. The renderer keeps the detailed mesh, and physics keeps the simple shape. The two are separate on purpose.

## A rigid body is a pose, velocities and a mass made of colliders

A **rigid body** is an object that moves but never bends: its state is a pose (a position and a rotation), a linear velocity, an :term[angular velocity]{id=angular-velocity} and a mass.

A **collider** is a simple shape attached to a body that takes part in collisions. One body holds one or more colliders, and the colliders give the body its volume, its mass distribution and its contacts.

You see the shapes in the editor. A toggle on the viewport draws collider :term[gizmos]{id=gizmo-start} as wire frames, for the selected entity and its descendants only. The `allColliders` setting of the `viewport.setSettings` command draws the shapes of every entity; the viewport has no button for it. Compare the two pictures below: the sample's crates are built-in cubes, so each collider box lies on its crate's edges.

::compare{id=colliders-gizmos}

The next diagram shows the model in one picture. Entities carry components. The physics module reads the components and builds bodies from them, and every body owns shapes.

```mermaid caption="Components on entities describe the bodies. The physics module builds one body from a rigid body component and its colliders." alt="A flow from an entity with a rigid body component and collider components, to a body with a type, a mass and a material, to shapes. The rendered mesh sits apart from this chain."
flowchart LR
    E["Entity: RigidBody + colliders"] --> B["Body: type, mass, material"]
    B --> S["Shapes: box, sphere, capsule, hull, mesh"]
    M["Rendered mesh"] -.-> R["Renderer only"]
```

The rest of the page follows the questions you ask when you make an object. Which units does physics use? Who moves the object? Which shape fits it, and how slippery and elastic is it? How does a hierarchy of entities turn into bodies?

## Physics counts in metres, kilograms and seconds

Strata reads every length as metres, every mass as kilograms and every time as seconds. The scene's gravity is $(0, -9.81, 0)$ in metres per second squared: it pulls along the negative Y axis, and 9.81 is the pull of the Earth. The sizes in the rest of this page come from this rule.

:::example[A crate dropped from 1.25 m]
A crate starts at rest 1.25 m above the floor. With gravity $g = 9.81$ m/s², the fall lasts $t = \sqrt{2h/g} = \sqrt{2.5 / 9.81}$, which is about 0.505 s. Its speed at the floor is $g t$, about 4.95 m/s. These are the numbers you expect from a real crate, because the crate is 1 m wide and physics counts in metres.

Now build the same scene in centimetres, so that the crate is 100 units wide and starts 125 units up. Gravity still pulls at 9.81 units per second squared, so the fall still lasts 0.505 s. In 0.505 s the crate falls through 1.25 of its own 100 units. It looks as if it floats down in slow motion, and nothing in the settings tells you why.
:::

Two more limits follow from the same rule. Bodies are simulated in single precision, and the gap between two neighbouring numbers grows with the distance from the origin: near 100,000 m it is about 8 mm. A body that is more than 100,000 m from the origin, or that has a degenerate transform (a scale of zero, for example), therefore leaves the simulation until its transform is valid again. [Scale and streaming](scale-streaming.md) explains how a large world avoids the problem, and [floating-point numbers](../basics/numbers.md) shows where the gaps come from.

## The body type says who moves the body

A body has one of three types, and each answers the question: who is allowed to move this body?

A **static body** never moves by simulation. Nothing pushes it. Floors, walls and scenery are static bodies, and the simulation treats them as fixed.

A **dynamic body** is moved by the simulation under gravity, forces and contacts. Crates, balls and debris are dynamic bodies. It is the default type of a `RigidBody`.

A **kinematic body** is moved by game code through its transform (or a teleport call). Strata gives it the velocity that reaches the target pose in one step, so it pushes dynamic bodies and carries riders, and it is never pushed. It refuses the velocity, force and impulse calls that dynamic bodies accept. Moving platforms, doors and lifts are kinematic bodies.

Each type breaks in its own way when you treat it like another type.

- A static body moved every frame has no velocity, so a crate on it is not carried and gets no friction from its motion. Strata must place its body again every time it moves, and that costs work. Make it kinematic instead.
- A dynamic body moved by writing its transform is teleported: it keeps its velocity, loses the contacts it had, and can finish inside another body. Move it with forces and velocities, or make it kinematic.
- A kinematic body that must fall, or be pushed by a hit, never will. Make it dynamic.

Strata maps the three types to the three body types of box3d, the physics library inside the engine.

## Colliders come in a few shapes

Each shape answers a question that the one before leaves open.

A sphere is the cheapest: a centre and a radius. A box adds corners and flat faces. A capsule is a cylinder with rounded ends, the usual shape for a standing person, because a rounded end slides over small steps. Those three cover most objects.

When they do not fit, the next step is a **convex hull**: the smallest :term[convex]{id=convex} shape that holds a set of points. A shape is convex when a line between any two of its points stays inside it.

A hull is built from a mesh, and it loses detail. Strata reduces a hull to at most 64 vertices, and if box3d refuses it, to 44. A sphere mesh with 500 vertices therefore becomes a ball with flat facets, not a perfect ball. It also fills hollows: the hull of a doughnut-shaped ring fills the hole, so nothing can fall through it. The Create menu of the Hierarchy gives the `Cylinder`, `Cone` and `Torus` entities a mesh collider that is a hull of their own mesh, and Strata has no cylinder collider.

A **triangle mesh collider** collides against the triangles of a mesh themselves, with all their detail and all their hollows. A mesh has no inside, so physics cannot give it a mass. A triangle mesh therefore works only on static bodies. On a dynamic or kinematic body Strata ignores it and logs a warning.

A **compound** is a set of shapes that acts as one: a body with several colliders is a compound.

A **baked compound** is box3d's form of a triangle mesh that sits away from its body's origin. A trigger, which reports overlaps, cannot hold one, so a triangle mesh in a trigger works only at its body's origin.

| Shape | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| The rendered mesh | Very high | Exact, but no inside | None | No physics engine of Strata's kind |
| Box, sphere, capsule | Lowest | Rough, with exact formulas | Two numbers to eight | Strata: box, sphere, capsule colliders |
| Convex hull | Low | A cover of the shape, no hollows | A mesh and the hull reduction | Strata: mesh collider with Convex on |
| Triangle mesh | Highest | Exact surface, no volume | A static body only | Strata: mesh collider with Convex off |
| Compound | The sum of its parts | Good for complex objects | Placing the parts | Strata: any body with several colliders |

Strata has these five and no more. A mesh collider with no mesh of its own uses the mesh of the entity's `MeshRenderer`.

## Friction, restitution and damping describe a body's material

A **friction** value says how much a surface resists sliding: 0 is ice, and 1 or more is rubber on rough ground.

A **restitution** value says how much of its speed a body keeps after a bounce: 0 is a lump of clay that stops, and 1 is a perfect bounce.

Strata stores one friction and one restitution on the `RigidBody`, and every shape of the body shares them. The defaults are 0.5 and 0.

Two bodies touch each other, and each has its own values, so the engine needs one number for the contact. Strata keeps the default rule of box3d: the contact's friction is the square root of the product of the two values, and its restitution is the larger of the two. Strata installs no :term[callback]{id=callback} of its own for either.

:::example[An ice ball on a wood floor, and a rubber ball on clay]
An ice ball has friction 0.05 and the wood floor has 0.5. The product is 0.025 and the square root is about 0.158: the contact slides almost as freely as the ice alone. A rubber ball with restitution 0.8 falls on a floor with restitution 0. The larger value is 0.8, so the ball bounces back with 0.8 of its speed. The floor cannot cancel a bounce: the larger value wins.
:::

Two more fields shape the motion. **Damping** slows a body without any contact, like air drag: `LinearDamping` acts on the velocity and `AngularDamping` on the spin, both 0.05 by default. A ball that rolls on a floor slows only through damping, because Strata sets no rolling resistance.

The **gravity scale** multiplies the scene's gravity for one body: 1 is normal, 0 floats, and a negative value rises.

Strata sets friction and restitution and nothing else of box3d's surface material. A moving belt (a tangent velocity of the surface) cannot be made with a body's material, and rolling resistance does not exist.

The lock fields stop a body from turning. `LockRotationX`, `LockRotationY` and `LockRotationZ` refer to the world axes, not to the body's own axes. A pillar with X and Z locked stays upright and can still turn around Y.

## A hierarchy of entities becomes a set of bodies

An object in a scene is often an entity with children: a chest with a lid and a lock. Which parts are one body, and which parts are two? Engines answer in two ways.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| One body per component with a collider | One body each, more joints | Parts move apart unless joined | You must add joints | Engines where each component simulates alone |
| One body with child colliders (a compound) | One body, several shapes | The parts stay together | One rule for the tree | Unity, Godot, Strata |

:::elsewhere[Other engines]
A Unity `Rigidbody` governs the colliders of its children as one compound. In Godot a body node owns the shape nodes below it. See Further reading.
:::

Strata uses the second approach. A `RigidBody` makes its entity one body. The body takes the colliders of the entity and those of every descendant that has no `RigidBody` of its own, each placed by its transform relative to the owner. A lone collider, with no `RigidBody` at its entity or above it, forms a static body. Events and queries report the entity that owns the body, so a hit on the lid says "chest".

:::example[A chest, a lid, a lock and a wall]
The `Chest` has a `RigidBody` and a box collider. Its child `Lid` has a box collider. Its child `Lock` has its own `RigidBody` and a sphere collider, and the child `Pin` of `Lock` has a capsule collider. A `Wall` has a box collider and nothing else. How many bodies are there?

`Chest` is body 1, a dynamic body with two shapes: its own box and the box of `Lid`. `Lock` has its own `RigidBody`, so it is body 2, with two shapes: its sphere and the capsule of `Pin`, because `Pin` belongs to the nearest owner above it. `Wall` is body 3, a static body. In all there are three bodies and five shapes.
:::

```mermaid caption="Chest, lid, lock, pin and wall give three bodies: the lid joins the chest, the pin joins the lock, and the lone wall is static." alt="A tree of five entities on the left and three bodies on the right. Chest and Lid lead to a dynamic body. Lock and Pin lead to a second dynamic body. Wall leads to a static body."
flowchart LR
    Chest["Chest: RigidBody, box"] --> Lid["Lid: box"]
    Chest --> Lock["Lock: RigidBody, sphere"]
    Lock --> Pin["Pin: capsule"]
    Wall["Wall: box"]
    Chest -.-> B1["Body 1: dynamic, 2 shapes"]
    Lid -.-> B1
    Lock -.-> B2["Body 2: dynamic, 2 shapes"]
    Pin -.-> B2
    Wall -.-> B3["Body 3: static, 1 shape"]
```

The scale of each entity is baked into its shapes when the body is built, so a chest scaled to 2 gets a box twice as wide. The rules for each shape belong to [building bodies](building-bodies.md).

When the simulation moves a dynamic parent, a dynamic descendant with its own `RigidBody` keeps its own world pose. The lock does not ride on the falling chest unless a joint or a script says so. Kinematic and static descendants follow the parent. When your code writes a parent's transform, every descendant moves with it, and a dynamic one is teleported. [The world step](world-step.md) shows how the pose is written back.

:::rule[What a body needs]
A `RigidBody` that finds no collider at its entity or below gets no body, so it does not fall. The log warns once that it "has a Rigid Body but no collider; it is not simulated". A lone collider is a static body with the default material (friction 0.5, restitution 0) on layer 0. A wall or floor that needs another layer or material needs a `RigidBody` of type Static, because only a `RigidBody` carries a layer and a material. See [collision layers](collision-layers.md).
:::

The component is plain data. Compare each field with the Inspector below it: the editor shows the same names under the heading Rigid Body, and the collider components are listed beside it.

```cpp src="Strata/src/Strata/Physics/PhysicsComponents.h#L20-L42"
enum class RigidBodyType : uint8_t
{
	Static = 0,
	Dynamic,
	Kinematic
};

struct RigidBodyComponent
{
	RigidBodyType Type = RigidBodyType::Dynamic;
	float Mass = 1.0f;
	float LinearDamping = 0.05f;
	float AngularDamping = 0.05f;
	float GravityScale = 1.0f;
	float Friction = 0.5f;
	float Restitution = 0.0f;
	bool IsTrigger = false; // Reports overlaps without colliding
	bool ContinuousCollision = false; // Also swept against moving bodies (every dynamic body is swept against static ones)
	bool LockRotationX = false;
	bool LockRotationY = false;
	bool LockRotationZ = false;
	uint32_t Layer = 0; // Collision layer (0-31)
};
```

1. **Line 29:** the type defaults to dynamic, and the mass on line 30 is in kilograms.
2. **Lines 31-33:** the two damping fields and the gravity scale.
3. **Lines 34-35:** the material, one pair of numbers for every shape of the body.
4. **Lines 38-40:** the three lock fields, which hold the world axes.
5. **Line 41:** the collision layer, from 0 to 31.

Two fields stay out of this page. `ContinuousCollision` is [the dynamics page's](dynamics.md) topic, `IsTrigger` belongs to [triggers](contacts-triggers.md), and `Layer` to collision layers.

::figure{id=rigid-body-inspector}

## What Strata cannot do here

Strata has no height-field collider and no cylinder collider. Terrain collides as a static triangle mesh or as boxes, and a cylinder is a hull of its mesh. The material has no rolling resistance and no tangent velocity. A character that walks is not a rigid body: the [character controller](character-controllers.md) moves it. The appendix lists [what Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **A `RigidBody` on every child.** Symptom: a chest falls apart into lid, lock and base. Fix: put the `RigidBody` on the root only, and give the children colliders.
- **A triangle mesh on a dynamic body.** Symptom: the log warns that the mesh is ignored, and the shape is missing from the body (a body with no other collider is not simulated). Fix: turn Convex on, or replace the mesh with boxes.
- **A static body moved every frame.** Symptom: riders slide off and the cost grows. Fix: make the body kinematic.
- **A dynamic body moved by writing its transform.** Symptom: it teleports through walls and loses contacts. Fix: apply forces, set velocities, or use a kinematic body.
- **Building in centimetres or far from the origin.** Symptom: slow-motion falls, or jitter and a body that vanishes from the simulation. Fix: use metres and keep play near the origin.
- **Non-uniform scale under a rotated parent.** The result is a shear, which a shape cannot represent, so the shape takes the scale that remains when the pose is split into position, rotation and scale, and does not match the mesh. Fix: use uniform scale on rotated parents.
- **A wall with a collider and no body but a special layer.** The wall sits on layer 0 with the default material. Fix: give it a Static `RigidBody`.

## Summary

- Physics collides simple shapes, because a rendered mesh costs too much and has no inside; a rigid body is a pose, velocities and a mass made of colliders.
- A static body never moves, a dynamic body is moved by the simulation and a kinematic body by your code; moving a body like another type loses contacts or never works.
- Choose a sphere, box or capsule first, a convex hull for other solid objects and a triangle mesh only on static bodies.
- A contact takes the square root of the product of the two frictions and the larger restitution.
- An entity with a `RigidBody` is one body with its own colliders and those of descendants without a `RigidBody`; a lone collider is a static body.

## Check yourself

1. A designer puts a triangle mesh collider on a crate that must fall. What happens, and which option fixes it?

   A. The crate falls but tilts oddly.

   B. Strata ignores the collider with a warning, and the crate, with no usable collider, is not simulated; turning Convex on fixes it.

   C. The crate becomes static.

   D. The crate collides with a perfect surface at a higher cost.

   :::answer{tests="shapes,model"}
   B is right: a triangle mesh has no inside, so no mass, and Strata ignores it on a body that is not static. A and D describe a working mesh. C is wrong: the type stays what the `RigidBody` says.
   :::

2. A lift must carry a crate between floors on a path your code controls. Which type fits the lift, and which mistake do the other types make?

   :::answer{tests="body-types"}
   A kinematic body. Moved through its transform, it gets the velocity that reaches the target, so the crate on it is carried. A static lift gets no velocity and moves with extra work; a dynamic lift would fall and be pushed by the crate.
   :::

3. A steel ball has friction 0.2 and restitution 0.3, and a rubber mat has friction 0.8 and restitution 0.6. Compute the contact's friction and restitution.

   :::answer{tests="material"}
   Friction is $\sqrt{0.2 \times 0.8} = \sqrt{0.16} = 0.4$. Restitution is the larger value, 0.6.
   :::

4. A `Cart` has a `RigidBody` and a box. Its children `Wheel1` and `Wheel2` have sphere colliders, and `Driver` has a `RigidBody` and a capsule. How many bodies, and how many shapes does the cart's body have?

   :::answer{tests="hierarchy"}
   Two bodies: the cart and the driver. The cart's body holds three shapes: its box and the two wheels. The driver's body holds one capsule.
   :::

## Exercises

1. **Basic.** A box with friction 0.1 rests on a ramp with friction 0.9, and the ramp has a Static `RigidBody`, so that it keeps its own material. Predict on paper whether the box holds at 15 degrees and at 20 degrees, using the mixing rule and $\tan 15° \approx 0.27$ and $\tan 20° \approx 0.36$. Then run the sketch and change the numbers to your own pair.

   :::answer[Worked solution]{tests="material" solution="sketches/physics-bodies-colliders-mixing.cpp"}
   The contact's friction is $\sqrt{0.1 \times 0.9} = 0.3$. The box holds while the tangent of the angle stays below 0.3: at 15 degrees $0.27 < 0.3$, so it holds, and at 20 degrees $0.36 > 0.3$, so it slides. The sketch repeats the arithmetic.

   ```cpp sketch="physics-bodies-colliders-mixing.cpp"
   // How two touching materials combine, and the ramp angle at which a box starts to slide.
   #include <cmath>
   #include <cstdio>
   #include <initializer_list>

   namespace
   {
   	constexpr double c_Pi = 3.14159265358979323846;

   	// Friction of a contact: the square root of the product of the two materials' friction.
   	double MixFriction(double a, double b)
   	{
   		return std::sqrt(a * b);
   	}

   	// Restitution of a contact: the larger of the two values.
   	double MixRestitution(double a, double b)
   	{
   		return a > b ? a : b;
   	}

   	// A box rests on a ramp while tan(angle) stays below the friction coefficient.
   	double SlideAngleDegrees(double friction)
   	{
   		return std::atan(friction) * 180.0 / c_Pi;
   	}
   }

   int main()
   {
   	std::printf("ice on wood: friction %.3f\n", MixFriction(0.05, 0.5));
   	std::printf("rubber on floor: restitution %.2f\n", MixRestitution(0.8, 0.0));

   	const double mixed = MixFriction(0.1, 0.9);
   	std::printf("box on ramp: friction %.2f, slides above %.1f degrees\n", mixed, SlideAngleDegrees(mixed));
   	for (double angle : { 15.0, 20.0 })
   	{
   		const bool slides = std::tan(angle * c_Pi / 180.0) > mixed;
   		std::printf("ramp at %.0f degrees: the box %s\n", angle, slides ? "slides" : "holds");
   	}
   	return 0;
   }
   ```

   ```text output-of="physics-bodies-colliders-mixing.cpp"
   ice on wood: friction 0.158
   rubber on floor: restitution 0.80
   box on ramp: friction 0.30, slides above 16.7 degrees
   ramp at 15 degrees: the box holds
   ramp at 20 degrees: the box slides
   ```

   1. **Line 13:** the mixing rule for friction, a square root of the product.
   2. **Line 19:** the rule for restitution, the larger value.
   3. **Line 25:** the angle whose tangent equals the friction.
   4. **Line 34:** the ramp pair of exercise 1.
   5. **Lines 36-40:** each ramp angle is tested against the mixed friction.

   The sketch agrees with the prediction. To test your own pair, change the two arguments of `MixFriction` and the two angles in the loop.
   :::

2. **Medium.** An entity `Door` has a Kinematic `RigidBody` and a box. Its child `Handle` has a sphere collider. Its second child `Plate` has a Dynamic `RigidBody` and a box, with a child `Screw` that has a capsule, and a `Floor` has a box. Give the bodies, their types and their shapes, and say what `Plate` does when the door swings.

   :::answer[Worked solution]{tests="hierarchy,body-types"}
   Step 1: `Door` owns a Kinematic body, and the sphere of `Handle` joins it: two shapes. Step 2: `Plate` has its own `RigidBody`, so it is a second body, Dynamic, and `Screw` joins it: two shapes. Step 3: `Floor` is a static body of its own with one shape: three bodies in all. Your code swings the door by writing its transform, so the transform of its child `Plate` changes too: Strata teleports `Plate` along with the door. A dynamic child keeps its own pose only when the simulation moves a dynamic parent.
   :::

3. **Hard.** Design the bodies for a table with flippers: the table, two flippers that you turn by code, the balls, and a curved rail built from a detailed mesh. Choose a type and a shape for each, and say what would go wrong with your second choice.

   :::answer[Worked solution]{tests="body-types,shapes"}
   The table and the curved rail are static bodies. The rail uses a triangle mesh, which is allowed because it is static, and it keeps every curve. The flippers are kinematic bodies with box colliders, because your code turns them and they must push the balls without being pushed. The balls are dynamic bodies with sphere colliders and a high restitution. If the flippers were dynamic, the balls would push them away, and a dynamic rail would lose its triangle mesh.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsComponents.h`: `RigidBodyComponent`, `BoxColliderComponent`, `SphereColliderComponent`, `CapsuleColliderComponent` and `MeshColliderComponent`; `PhysicsComponents.cpp` registers them with their Inspector names.
- `Strata/src/Strata/Physics/PhysicsWorld.cpp`: `MakeBodySetup` (the material, damping, gravity scale and locks), `ToBodyType`, and the warning for a `RigidBody` with no collider.
- `Strata/src/Strata/Physics/PhysicsWorld.h`: the body rules, the baked scale and the write-back of nested bodies; `PhysicsMeshShapes.h`: the hull limits.
- `StrataEditor/src/Panels/SceneHierarchyPanel.cpp`: the Create menu's colliders; `StrataEditor/src/Editor/EditorViewportCommands.cpp`: the `viewport.setSettings` command with `allColliders`.
- `Strata/vendor/box3d/src/physics_world.c`: the default friction and restitution callbacks.
- Tests: `StrataTests/src/Physics/PhysicsHierarchyTests.cpp` (suite `Physics.Hierarchy`, case `Colliders of descendants without a rigid body belong to the ancestor's body`) and the helpers of `PhysicsTestUtils.h`.

## Further reading

- box3d documentation, the manual's pages on bodies and shapes: the library under Strata (intermediate).
- Christer Ericson, "Real-Time Collision Detection": convex hulls, bounding volumes and compound shapes (advanced).
- The Unity manual, "Compound colliders": one body with child colliders (beginner).
- The Godot documentation, "Physics introduction": body nodes with shape nodes below them (beginner).
