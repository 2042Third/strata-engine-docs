---
id: reference/physics
title: "Physics reference"
description: "The units, body types, shapes, limits, scene services and statistics of Strata's physics, in tables for looking things up."
kind: reference
size: M
tracks: []
needs: [physics/bodies-colliders]
status: final
---

This page holds the facts of physics in one place, for a reader who tunes a body or reads a number from `physics.stats`. Each table has one short introduction that names the page teaching its subject. Read a table row by row: the first column names a thing, the others say what it measures, in which unit and within which limits.

Other reference pages hold the full rows of what physics adds to the editor. The six physics components are in [Components](../reference/components.md): `RigidBody`, `BoxCollider`, `SphereCollider`, `CapsuleCollider`, `MeshCollider` and `CharacterController`. The `Physics.Simulation` section is in [Settings](../reference/settings.md), the `physics.*` commands are in [Commands](../reference/commands.md), and the physics functions of the script software development kit (SDK) are in [the script reference](../reference/script-api.md). This page adds what those rows omit: units, limits, services and statistics.

## Units

A body is a thing that the simulation moves, and a collider is the shape that gives it a surface (see [Bodies and colliders](../physics/bodies-colliders.md)). Their numbers are only useful when you know the unit. The table lists every physics property and setting field that has one. A collider size is in the units of the entity's world scale, so a box of half extent 0.5 on an entity scaled by 2 is 2 m wide.

Distances are metres, masses are kilograms, times are seconds, and a force is in newtons, the force that speeds one kilogram up by one metre per second each second. An impulse is a force applied for a time, so it is in newton-seconds.

| Name | Unit | Note |
| --- | --- | --- |
| `RigidBody` `Mass` | kilograms | At least 0.001; smaller values count as 0.001 |
| `RigidBody` `LinearDamping`, `AngularDamping` | damping factor, 0 to 100 | Slows motion; box3d warns that large values make the effect depend on the step |
| `RigidBody` `GravityScale` | factor, -100 to 100 | Multiplies the scene's gravity; negative values push up |
| `RigidBody` `Friction` | coefficient, 0 to 10 | No unit |
| `RigidBody` `Restitution` | coefficient, 0 to 1 | 0 stops a bounce, 1 keeps all its speed |
| `RigidBody` `Layer` | index, 0 to 31 | The collision layer of the body |
| `BoxCollider` `HalfExtents` | metres | Half the size along each axis, times the entity's world scale |
| `SphereCollider` `Radius` | metres | Times the largest axis of the world scale |
| `CapsuleCollider` `Radius` | metres | Times the larger of the world scale's X and Z |
| `CapsuleCollider` `HalfHeight` | metres | The straight part only, times the Y scale |
| Collider `Offset` | metres | In the entity's space: rotated and scaled with the entity |
| `CharacterController` `Height`, `Radius`, `StepHeight` | metres | Scale and rotation of the entity never change the shape |
| `CharacterController` `MaxSlopeDegrees` | degrees | From the horizontal, 0 to 89 |
| `CharacterController` `GravityScale` | factor | Times the scene's gravity |
| `CharacterController` `PushStrength` | newtons | The largest force on a :term[dynamic body]{id=dynamic-body} |
| Linear velocity | metres per second | :term[World space]{id=world-space} |
| :term[Angular velocity]{id=angular-velocity} | :term[radians]{id=radian} per second | Around each world axis |
| Force, torque | newtons, newton-metres | Act for the next step only |
| Impulse, angular impulse | newton-seconds | Change the velocity at once |
| `ContactRecycleDistance` | metres | 0 to 1; 0 turns recycling off |
| `SleepThreshold` | metres per second | 0 to 1 |
| `ContactHertz` | hertz (Hz) | 1 to 240 |
| `ContactDampingRatio` | ratio | 0 to 100 |
| `ContactPushSpeed` | metres per second | 0.01 to 100 |
| `SceneSettings::Gravity` | metres per second, per second | A vector; default 0, -9.81, 0 |
| `SceneSettings::FixedTimestep` | seconds | Default 1/60 |
| `FixedRate` of `Scene.Timing` | steps per second | Scene, 30, 60, 120 or 240 |
| `MaxBodies`, `MaxContactConstraints` | counts | 0 sizes the room from the scene |

## Gravity and the fixed step

Two numbers that every body depends on are not physics properties. Gravity is `SceneSettings::Gravity` of the scene, and the fixed step is `SceneSettings::FixedTimestep`, unless the project's `Scene.Timing` section sets a rate, which then wins in every scene. Code reads the step through `Scene::GetFixedTimestep`. [The fixed step](../core/time.md) explains why a simulation runs in equal steps, and [Scene services](../world/systems.md) explains the services below.

## Body types and shapes

A body has one of three types, and a collider has one of four shapes. The tables name each choice as the `RigidBodyType` enum and the collider components write them in `PhysicsComponents.h`. [Bodies and colliders](../physics/bodies-colliders.md) teaches what each choice does in a game.

| Body type | Moves | Takes forces |
| --- | --- | --- |
| `Static` | Never | No |
| `Dynamic` | By forces, impulses and contacts | Yes |
| `Kinematic` | Only where gameplay puts it | No |

A collider entity with no `RigidBody` on itself or on an ancestor is a :term[static body]{id=static-body} of its own. Colliders of the entity and of its descendants that have no `RigidBody` of their own join the body of the nearest ancestor that has one. A `CharacterController` is used instead of a `RigidBody`, never beside it: an entity with both is simulated as the :term[rigid body]{id=rigid-body}, and its controller does nothing.

| Shape | Component | Size fields | Rule |
| --- | --- | --- | --- |
| Box | `BoxCollider` | `HalfExtents` | Each axis has a smallest size of 0.001 m |
| Sphere | `SphereCollider` | `Radius` | Radius at least 0.001 m |
| Capsule | `CapsuleCollider` | `Radius`, `HalfHeight` | Stands along the entity's local Y axis |
| Mesh | `MeshCollider` | `Mesh`, `Convex` | A :term[convex hull]{id=convex-hull}, or a triangle mesh on static bodies only |

A mesh collider with `Convex` off on a body that is not static has no effect: the engine skips it and logs a warning. A mesh collider with no mesh uses the one of the `MeshRenderer`.

## Limits

A limit is a number the engine refuses to pass. Some come from box3d, the physics library, and some from Strata. [Scale and streaming](../physics/scale-streaming.md) gives the reasons and [Tuning](../physics/tuning.md) says how to read them. The first table, generated from the source, lists the constants of scenes and worlds. The physics ones are `c_MaxBodyCoordinate`: a body farther than that from the origin waits until it comes back.

Next come `c_MaxRaycastDistance`, which cuts a longer ray, and the two capacity limits `PhysicsCapacitySettings::c_MaxBodiesLimit` and `PhysicsCapacitySettings::c_MaxContactConstraintsLimit`. The last is `PhysicsWorld::c_MaxBodiesReservedAtCreation`.

::include{file="limits.md"}

The room of a world is the number of bodies and contacts it has space for. A scene that asks for 0 gets an automatic room: the bodies it has, doubled and rounded up to a power of two, and never fewer than 1,024. The contact room is twice the bodies, never fewer than 2,048.

For 10,000 bodies, doubling gives 20,000 and the next power of two is 32,768 bodies of room. The contact room is 20,000. The memory estimate is 32,768 :term[bytes]{id=byte}, plus 2,120 times 32,768 bodies, plus 250 times 20,000 contacts: 74,500,928 bytes, which `reservedMB` shows as 71.05 MB. The room grows while bodies come, up to the growth limit, the most bodies a world may grow to, so the number is a floor and not a cap.

The next table lists the limits that no generated table holds yet.

| Limit | Value | Meaning |
| --- | --- | --- |
| Worlds | 128 | box3d holds at most this many worlds at once; a scene that cannot get one plays without physics |
| Contacts reserved at creation | 262,144 (2^18) | `PhysicsWorld::c_MaxContactsReservedAtCreation`; the room beyond it grows while the game plays |
| Reserved memory | 32 KiB, plus 2,120 :term[bytes]{id=byte} a body, plus 250 bytes a contact | The estimate behind `reservedMB` |
| Smallest automatic room | 1,024 bodies | The least a world sizes itself for when the scene asks for 0 |
| Hull vertices | 64 preferred, 44 safe | See the note below |
| Hull size in box3d | 128 vertices, 128 faces, 128 edges | A hull made of triangles with V vertices has 2V - 4 faces and 3V - 6 edges |
| Shared box hulls | 4,096 | Boxes of one size and placement share a hull |
| Mesh wait | 10 seconds | `PhysicsSettings::MeshWaitTimeout`: the first step waits this long for the meshes of mesh colliders |
| Rounds of changes | 16 | After 16 rounds without settling, the engine logs an error and drops the rest |
| Steps per update | 1 | `PhysicsSettings::CollisionSteps`: box3d steps for each fixed step |

A convex hull cooked from a mesh starts with at most 64 vertices. A round hull of 64 vertices has about 186 edges, more than box3d's 128, so box3d refuses it and the engine cooks again with 44 vertices, which has 126 edges at most and always fits.

## Scene services

A scene service is an interface that one system offers and other code finds through the scene, so that code never includes the physics module. Physics offers the seven below, all declared in `SceneServices.h`. [The world step](../physics/world-step.md), [Contacts and triggers](../physics/contacts-triggers.md), [Queries](../physics/queries.md) and [Character controllers](../physics/character-controllers.md) teach how they work. Entities name bodies: a function that takes one returns false, zero or nothing when the entity owns no body.

| Service | Function | What it does |
| --- | --- | --- |
| `ICollisionEventSource` | `AddCollisionListener` | Registers a :term[callback]{id=callback} for contact events with a scope: all entities, or watched ones |
| `ICollisionEventSource` | `RemoveCollisionListener` | Removes a listener, also in the middle of a dispatch |
| `ICollisionEventSource` | `WatchCollisions`, `UnwatchCollisions` | Ask for an entity's contacts to be tracked; watches add up |
| `IBodyMotionQuery` | `HasBody` | True when the entity owns a body in the simulation |
| `IBodyMotionQuery` | `GetLinearVelocity`, `GetAngularVelocity` | Velocities in metres and radians per second |
| `IBodyMotionQuery` | `GetPointVelocity` | The velocity of a world point that moves with the body |
| `IBodyMotionQuery` | `IsSleeping` | False for static bodies and entities without a body |
| `IBodyMotionQuery` | `GetSimulatingBody` | The entity or nearest ancestor with a `RigidBody` |
| `IBodyMotionQuery` | `IsDynamicBody` | True only for a dynamic `RigidBody` |
| `IBodyControl` | `SetLinearVelocity`, `SetAngularVelocity` | Change the speed of a dynamic body |
| `IBodyControl` | `AddForce`, `AddForceAtPosition`, `AddTorque` | Act during the next step only |
| `IBodyControl` | `AddImpulse`, `AddImpulseAtPosition`, `AddAngularImpulse` | Change the velocity at once |
| `IBodyControl` | `SetGravityScale` | Changes the body and its component |
| `IBodyControl` | `WakeUp` | Wakes a sleeping body |
| `IBodyControl` | `Teleport` | Moves the body and entity at once, keeping velocities |
| `IPhysicsQueries` | `Raycast` | The closest hit of a ray; a ray that starts inside a :term[convex]{id=convex} collider misses it |
| `IPhysicsQueries` | `RaycastAll` | Every body the ray hits, nearest first |
| `IPhysicsQueries` | `OverlapSphere`, `OverlapBox` | The entities whose bodies overlap a sphere or an oriented box |
| `ICharacterControl` | `HasCharacterController` | True for an enabled controller without a `RigidBody` |
| `ICharacterControl` | `MoveCharacter` | Sets the walking velocity until the next call |
| `ICharacterControl` | `JumpCharacter` | Moves up at a speed at the next fixed step |
| `ICharacterControl` | `TeleportCharacter` | Moves it at once and drops its vertical speed |
| `ICharacterControl` | `AddCharacterMotion` | Adds a displacement that collides like walking |
| `ICharacterControl` | `GetCharacterState` | Ground state, normal, ground velocity, velocity and ground entity |
| `IPhysicsCapacity` | `GetCapacityInfo` | The room, the growth limit and the waiting entities |
| `IPhysicsCapacity` | `Reserve` | Asks for room for a number of bodies; the last call counts |
| `IPhysicsDiagnostics` | `GetStepInfo` | The last fixed step as numbers, in :term[constant time]{id=constant-time} |
| `IPhysicsDiagnostics` | `SetDetailedStats`, `IsDetailedStats` | Turn box3d's island and contact counters on or off, and ask |

The queries have no shape sweep: a ray and two overlap tests are all the interface offers. A query layer mask has one bit for each of the 32 layers, and [Collision layers](../physics/collision-layers.md) explains the matrix behind it. `IPhysicsQueries` skips triggers unless a call asks for them.

## Statistics

`physics.stats` answers while a game plays. Its result is a group of numbers for each part of the world, and the groups are in the table. The result is `{running: false}` while you edit, and `simulating` is false while the running scene has no physics world: it has no physics components, or box3d had no free world for it. [Tuning and measuring](../physics/tuning.md) shows how to read the numbers.

| Group | Keys | Unit | Meaning |
| --- | --- | --- | --- |
| `bodies` | `total`, `static`, `dynamic`, `kinematic` | bodies | Bodies in the simulation by type |
| `bodies` | `active`, `characters`, `parked`, `slotsUsed` | bodies | Awake bodies, controllers, static bodies leaving the simulation, slots in use |
| `capacity` | `maxBodies`, `growthLimit`, `maxContactConstraints` | counts | The room as it grew, its largest size, the contact room |
| `capacity` | `reservedMB` | MB | Memory the room takes; 1 MB is 1,048,576 bytes |
| top level | `waitingForSlot`, `pendingOther` | entities | Waiting at the growth limit, or for other reasons |
| top level | `addedLastFrame`, `removedLastFrame` | bodies | Built and destroyed in the last update |
| top level | `changeMsLastFrame`, `lastStepMs` | milliseconds | Time of applying changes, and of the last step |
| top level | `preparedSlices`, `steps`, `heldSteps` | counts | Load slices, steps run, steps held for meshes |
| top level | `waitingForMeshes` | flag | The last step was held because meshes of mesh colliders were not ready |
| `growths` | `count`, `lastMs`, `from`, `to` | count, ms, bodies | How often the room grew, and the last growth |
| `demand` | `bodies`, `contactConstraints` | counts | What the world needed beyond its first room |
| `step` | `ms`, `libraryMs`, `strataMs` | milliseconds | The last step, box3d's part and Strata's part |
| `step` | `parts` | milliseconds | Apply, sync, characters, `checkedPairs`, events, `writeBack`, pairs, instruments |
| `step` | `library` | milliseconds | Stages pairs, collide, solve, sensors; parts of solve; `splitIslands` |
| `step` | `workers`, `totalMs`, `totalLibraryMs` | count, ms | box3d's workers; totals since the world was created |
| `sleep` | `awake`, `sleeping`, `moving`, `islands` | bodies, islands | Sleep state of the moving bodies |
| `contacts` | `total`, `awake`, `recycled`, `recycledShare` | contacts, share | box3d's contacts; the share of awake ones used again |
| `contacts` | `detailed`, `tracked`, `capacity`, `peak` | flag, contacts | Counters read, pairs listened to, the room, the peak |
| `contacts` | `roomGrowths`, `lastGrowthStepMs` | count, ms | Growths of box3d's contact storage |
| `settling` | `maxSpeed`, `settling`, `restingJitterMm` | m/s, bodies, mm | The fastest body, those above the sleep threshold, the jitter of the rest |
| `settings` | `contactRecycleDistance` and the others | as the settings | The tuning in use; `effectiveContactHertz` is what box3d applies |
| `interpolation` | `enabled`, `stepAlpha`, `entities`, `blended`, `composed`, `exact` | flag, fraction, count | What is drawn between the last two steps |

An island is a group of bodies that touch each other, which box3d wakes and puts to sleep together. The contact counters are null until detailed statistics are on or a call passes `detail`. The jitter is the root mean square (RMS) of the displacement of the bodies that are not settling, in mm. The library times add up: its stages sum to `libraryMs`, and the parts of solve lie inside it.

A few readings help. When `waitingForSlot` is above 0, bodies wait because the world reached `growthLimit`, so raise the limit or build fewer bodies. When `recycledShare` is near 1, box3d takes most resting contacts from before and spends little on collision work. When `settling` stays above 0 for a long time, bodies still move faster than `SleepThreshold` and keep their islands awake. Two reads of `totalMs` give the time spent between them, because the totals start from 0 with each new world.

::include{file="commands-physics.md"}

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsComponents.h`: the body type enum and the components, with their defaults.
- `Strata/src/Strata/Physics/PhysicsTypes.h`: `PhysicsSettings`, `PhysicsStats`, `PhysicsLibraryProfile` and `PhysicsLibraryCounters`.
- `Strata/src/Strata/Physics/PhysicsWorld.h`: the room reserved at creation and the 128 worlds.
- `Strata/src/Strata/Physics/PhysicsMeshShapes.h`: the hull vertex counts.
- `Strata/src/Strata/Scene/SceneServices.h`: the seven services and their types.
- `Strata/src/Strata/Scene/Scene.h`: `SceneSettings`, gravity, the fixed step and the capacity limits.
- `StrataEditor/src/Editor/EditorWorldCommands.cpp`: the keys of `physics.stats`.
