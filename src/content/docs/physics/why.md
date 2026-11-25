---
id: physics/why
title: "Why games need physics"
description: "What a physics engine does for a game, why hand-written collision breaks, and why Strata builds on box3d."
kind: concept
size: S
tracks: [E]
needs: []
time: 20
learn:
  - id: need-physics
    text: explain which problems of a game a physics engine solves and which questions about space it answers
  - id: naive-breaks
    text: compute where hand-written collision fails for fast objects, tall stacks and many objects
  - id: box3d-role
    text: name what box3d does in Strata and what Strata adds around it
  - id: body-not-transform
    text: predict what happens to a crate when its body type, collider or transform changes
since: 0.3.0
status: final
---

Open the Physics Playground sample in the editor and press Play. A tower of crates stands on a floor, a row of 64 standing blocks waits on a winding path, and a pit holds 500 balls of four materials. A goal counts what falls into it, and ghost boxes sink through the balls as if the balls were not there. About 600 bodies move, and nobody animated one of them.

::figure{id=overview}

::figure{id=ball-pit}

Click, and a ball flies from the cursor and knocks a crate over. This page explains why a game needs a separate system for that, what the system is, and which one Strata uses.

## Questions a game asks about space

A game asks two kinds of questions. The first kind is about motion: does this crate fall, does it stop on the floor, does it stay on the stack or slide off, what happens when a ball hits it? The second kind is about space: what lies below the cursor, is the player standing on the ground, which enemies are within 5 m of the explosion?

A card game with a click on a card still asks "which card is here?". Both kinds need the same ingredient: a description of the shapes in the world that is separate from how they are drawn.

## Hand-written collision breaks quickly

The first answer most people try is to write collision in game code. Each frame you move an object, test whether it overlaps another one, and if it does, push it back. For one ball and one floor that works.

Three cases break it. Take a game that draws 60 frames per second, so a frame lasts 16.7 ms.

:::example[A fast ball meets a thin wall]
A ball flies at 30 m/s towards a wall 0.2 m thick that spans 5.0 m to 5.2 m from the ball's start. In one frame the ball moves 30 × 0.0167 = 0.5 m. Its positions are 4.9 m in one frame and 5.4 m in the next. Neither position overlaps the wall, so the overlap test never fires and the ball passes through. Engineers call this **tunneling**.

A stack fails differently. Ten crates of 20 kg each stand on each other. The bottom crate carries nine crates, or 180 kg, which is a force of 180 × 9.81 = 1,766 N. If your code pushes one overlapping pair apart at a time, each push moves another pair into overlap, and the tower shakes or collapses. A correct answer solves all contacts of the stack together.

Many objects fail by cost. Testing every pair of 500 balls means 500 × 499 / 2 = 124,750 tests each frame, before any ball touches the floor. Real engines first find which pairs could touch at all.
:::

None of this is impossible to write, but each fix is a large piece of work, and you need all of them at once.

## A second simulation beside the scene

A **physics engine** is a library that keeps its own simulated copy of the world, made of bodies with shapes, and advances it in small equal steps of time. Your scene holds entities with transforms, meshes and scripts. The physics engine holds one **rigid body** (a shape that never bends) for every entity that should take part, and a **collider** (the shape used for touching, not for drawing) on it.

The two worlds must agree. Before each step the physics engine learns where you moved things, and after the step it writes the new poses back to the entities. The step has a fixed length, so the result does not depend on how fast the computer draws; [the time page](../core/time.md) explains why.

```mermaid caption="Each fixed step reads moved transforms into the physics world, simulates, and writes poses back to the scene; drawing and queries then use the result." alt="A loop of four boxes: scene transforms, physics step, poses written back, drawing and queries."
flowchart LR
    A["Scene transforms"] --> B["Physics step"]
    B --> C["Poses written back"]
    C --> D["Drawing and queries"]
    D --> A
```

A drawn crate and its body are different things. The mesh renderer draws the crate, the collider gives it a shape to hit, and the rigid body gives it mass and motion. A rigid body also has a type: a dynamic body falls and is pushed, a static body never moves, and a kinematic body moves only where code puts it. Remove one of the three parts and the crate does something different; the last section of this page returns to that.

## How engines get physics

Engines choose among three approaches. Code written by hand for the game is the one you saw: cheap and exact for simple games, and not enough once stacks or many bodies appear. The second approach is a third-party library; the third is a physics library the engine's makers write themselves, which costs years of work.

The licence column names the Massachusetts Institute of Technology (MIT) licence, which allows free use if the notice stays.

| Approach | Cost | Quality | Licence | Used by |
| --- | --- | --- | --- | --- |
| Hand-written | Low at first, high later | Fails on stacks and fast objects | Yours | Card games, simple 2D games |
| PhysX | Free to use | Mature, stable | BSD-3-Clause | Unity (3D), older Unreal |
| Havok | Paid for most uses | Mature, very stable | Commercial | Many large commercial games |
| Jolt | Free | Modern, fast | MIT | Godot (option), large studios |
| Bullet | Free | Good, older | zlib | Blender, research |
| Box2D | Free | 2D only | MIT | Many 2D games |
| box3d | Free | New, fast, steady stacks | MIT | Strata |

:::elsewhere[Other engines]
Unity uses PhysX for 3D bodies and Box2D for 2D bodies, and Godot offers Jolt beside its own solver. Read each project's own documents before you rely on this table; licences change between versions.
:::

## Strata uses box3d behind its own components

Strata uses **box3d**, a library for 3D rigid bodies by Erin Catto, who also wrote Box2D. It carries the MIT licence, and `ThirdPartyNotices.md` pins its version. box3d does the heavy work: shapes, contacts, stacking and the solver, the part that computes how touching bodies push each other. Strata adds what a game needs around it:

- components (`RigidBody`, `BoxCollider` and others), so bodies are made in the editor like any other part of an entity;
- scene services for raycasts, overlaps and collision events, so scripts never touch box3d;
- the fixed step and the transform exchange of the picture above;
- its own character controller, which moves a capsule with box3d's mover queries (questions about how far a shape can move) instead of the solver, so a player climbs steps and rides platforms.

:::why[Why box3d, not Jolt?]
Strata used Jolt until 0.5.0. Release 0.5.0 moved to box3d behind the same components, the same scripting interface and the same commands. The Playground's crate tower settled with about 1 cm of drift, where it drifted 11 to 15 cm on Jolt, and busy steps took about 40 % less time on one test machine. The cost: creating or removing many bodies at once takes longer, because box3d adds them one at a time, and triggers no longer see triangle-mesh colliders.
:::

Details of the setup are on [the bodies and colliders page](bodies-colliders.md); how the solver moves bodies is on [the dynamics page](dynamics.md).

## What Strata does not do

Strata has no joints, ragdolls or vehicles; its plans for later releases list them on box3d's joints. Strata has no cloth, soft bodies, destruction, fluids or buoyancy. Its public scripting interface has no shape sweeps (moving a shape along a line to find what it hits); raycasts and overlaps exist, and only the character controller sweeps. Bodies must stay within 1e5 m of the origin, because box3d works in single precision. [The list of absences](../appendix/not-in-strata.md) keeps the current state.

## Common mistakes

The main mistake is to think the physics body is the transform. The transform places an entity; the body is a second record in another world, joined to the entity by the exchange above.

- **Symptom:** you lift a crate in the Scene view during Play and it falls again at once. **Fix:** a moved transform teleports a dynamic body, and gravity then pulls it down; to hold it in place, change its type to static or kinematic.
- **Symptom:** a visible object has no effect on anything. **Fix:** the mesh only draws; add a collider.
- **Symptom:** engine code writes a transform field and the body ignores it. **Fix:** signal the change, as the scene's rules require; without a signal the body never learns of it.
- **Symptom:** a fast bullet passes through a moving door or another body. **Fix:** enable `ContinuousCollision` on the bullet's body, which also sweeps it against moving bodies; every dynamic body is already swept against static ones, so a static wall stops it without the setting.

## Summary

- A physics engine answers motion questions (fall, collide, stack) and space questions (which body lies below the cursor, is the player on the ground) from shapes kept apart from drawing.
- Hand-written collision fails for fast objects (0.5 m per frame passes a 0.2 m wall), stacks (all contacts at once) and many objects (124,750 pairs for 500 balls).
- box3d simulates; Strata adds components, scene services, the fixed step and its own character controller.
- The body is not the transform: the mesh draws, the collider touches, and only a dynamic body falls.

## Check yourself

1. A ball moves at 45 m/s at 60 frames per second. How far does it move in one frame, and can it pass a wall 0.5 m thick without any overlap test firing?

   :::answer{tests="naive-breaks"}
   The ball moves 45 / 60 = 0.75 m per frame. That is more than 0.5 m, so one frame can put it before the wall and the next behind it, and the test never fires. This is tunneling.
   :::

2. Which of these is a question about space and not about motion? (a) Does the crate slide off the stack? (b) Is the player on the ground? (c) How hard does a ball hit the floor?

   :::answer{tests="need-physics"}
   (b). A query about space asks what is where and needs no motion. (a) and (c) ask what motion does, which the simulation answers.
   :::

3. Which of these does box3d do, and which does Strata add? (a) Solving contacts of a stack. (b) The `RigidBody` component. (c) The character controller.

   :::answer{tests="box3d-role"}
   box3d does (a). Strata adds (b) and (c); its controller uses box3d's mover queries.
   :::

4. A crate has a mesh, a box collider and a dynamic body. You remove the collider and play. What do you expect?

   :::answer{tests="body-not-transform"}
   The crate is still drawn, but it has no shape, so it is not simulated and hangs where it stands. The log warns that it has a body but no collider, and a ball passes through it. The mesh draws, and the collider is what touches.
   :::

## Exercises

1. **Basic.** In a copy of the Physics Playground, lift one crate 3 m in the Scene view and press Play. Then set its **Rigid Body** type to `Static` and play again. Last, remove its **Box Collider** and shoot a ball at it with a left click. Say what you see each time.

   :::answer[Worked solution]{tests="body-not-transform,need-physics" solution="tutorials/physics/why/exercise-1.tutorial.json"}
   First the crate falls back onto its stack, because a dynamic body obeys gravity. Second it hangs in the air, because a static body never moves. Third the ball passes through it, because a mesh without a collider is only drawn; the log warns that it is not simulated. The file checks each result but the ball's.
   :::

2. **Hard.** Three games: a stacking puzzle, a top-down shooter whose bullets are rays, a card game. For each, decide whether it needs bodies, needs only queries, or needs no physics engine, and say why.

   :::answer[Worked solution]{tests="need-physics,naive-breaks"}
   The stacking puzzle needs bodies: stacks must settle, which hand-written code does badly. The shooter needs only queries: a ray tells what it hits at once and nothing has to move. The card game needs none: a click on a card is a rectangle test.
   :::

## Where it lives in Strata

The Playground is `Samples/PhysicsPlayground/`, with scripts in `Samples/PhysicsPlayground/Scripts/Playground.cpp`. The components are in `Strata/src/Strata/Physics/PhysicsComponents.h`, the body world in `Strata/src/Strata/Physics/PhysicsWorld.h`, and the scene service and queries in `Strata/src/Strata/Physics/PhysicsSystem.h`. The character controller is in `Strata/src/Strata/Physics/CharacterControllers.h`. The editor command `physics.stats` reports what the simulation holds.

## Further reading

- Erin Catto, the box3d repository and the Box2D documents: how a solver for rigid bodies works (intermediate).
- Ian Millington, "Game Physics Engine Development": a full book on a simple engine (intermediate).
- Glenn Fiedler, "Fix Your Timestep": why steps have fixed length (beginner).
- Christer Ericson, "Real-Time Collision Detection": finding which pairs touch (advanced).
