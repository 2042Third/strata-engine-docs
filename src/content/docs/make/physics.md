---
id: make/physics
title: "Physics for game makers"
description: "Make Coin Run's ball roll by a force, jump by an impulse and collect coins that are triggers, and learn which body, shape and layer a thing needs."
kind: tutorial
size: L
tracks: [G, B]
needs: [make/input]
time: 70
learn:
  - id: body-types
    text: choose a body type for each thing in a game, static, dynamic or kinematic, with or without a trigger
  - id: force-impulse
    text: predict how a force and an impulse change the velocity of a body
  - id: trigger-callbacks
    text: write a script that reacts when a body enters a trigger
  - id: ground-ray
    text: build a ground check with a raycast and use it to make the ball jump
  - id: layers
    text: explain what a collision layer and the layer matrix decide
since: 0.3.0
status: final
---

## What you will make

Coin Run's ball stops sliding along the ground by magic. It becomes a heavy thing that falls, rolls when you push it, jumps, and returns to its start at a key press. The coins become triggers that the ball collects by touching them, and a wall that you can switch from solid to ghost shows what a layer does.

::figure{id=result}

## What you need

- The end state of [Input and input actions](input.md): Coin Run with a ball named `Ball` and its `BallControl` script, which moves it by writing its position.
- The `Move` and `Jump` actions in the `Gameplay` map, and the coins that `CoinPlacer` places.
- The coin :term[prefab]{id=prefab-make} `Prefabs/Coin.stprefab` with its `Coin` script, and the ground of the Basic 3D template, which already has a collider.
- The scripts, which this page quotes whole, in parts. Each checkpoint also offers the project as it should be, scripts included, and the editor commands that lead there.
- About 70 minutes. Every script is short.

You also need three ideas from earlier pages. The fixed step and `OnFixedUpdate` come from [the script loop](script-loop.md). Colliders on presets, prefabs and **Apply** come from [prefabs](prefabs.md). Reading a press in `OnUpdate` comes from [input](input.md).

## Let the ball fall

A game wants things to fall, hit each other and come to rest, and writing that by hand for every object would take months. A **physics engine** does it for you: each fixed step it moves every body a little, finds the bodies that touch and pushes them apart. Strata runs it in the fixed steps of the script loop, 60 times a second by default, so one step is 1/60 of a second.

Physics needs two things for each thing: a body and a shape. A **rigid body** is a thing the physics engine moves and that never bends: the ball, a crate, a door.

A **collider** is the invisible shape that physics uses to decide where a body ends, and it is never the drawn mesh. The shapes are Box, Sphere, Capsule and Mesh. A mesh collider is a convex hull (a shape without dents) on any body, or the exact triangles on a static body only.

Strata gives each thing one of three kinds of body. A **static** body never moves: the ground, a wall. A **dynamic** body is moved by physics: it falls, rolls and gets pushed. A **kinematic** body is moved by your code and ignores forces, but it pushes dynamic bodies out of its way, which suits a lift or a spinning coin. The trigger, a fourth choice that pushes nothing, has its own section below.

```mermaid caption="How to choose the body of a thing: ask whether it moves, then who moves it." alt="A flow chart. A thing that never moves is static, with only a collider. A thing that moves is dynamic when forces and collisions move it, and kinematic when code moves it. Any of them can also be a trigger that only reports overlaps."
flowchart TD
    A["Does the thing ever move?"] -->|No| B["Static: a collider alone"]
    A -->|Yes| C["What moves it?"]
    C -->|Forces and collisions| D["Dynamic rigid body"]
    C -->|Your code| E["Kinematic rigid body"]
    B --> F["Should it only report overlaps and push nothing?"]
    D --> F
    E --> F
    F -->|Yes| G["Add a rigid body with Is Trigger on"]
```

A thing that has a collider and no rigid body is a static body of its own, on layer 0, with friction 0.5 and restitution 0. That is why the template's ground works without one. The opposite mistake is silent: a rigid body with no collider gets no body at all. It does not fall, and the Console warns that it has a rigid body but no collider.

Here is what physics does to a falling ball, by hand. Gravity pulls with 9.81 metres per second squared, so each second the downward speed grows by 9.81 m/s. In one step of 1/60 second the speed grows by 9.81 / 60 = 0.16 m/s.

The ball will start with its centre at a height of 3 m. The ground's top is at 0 and the ball's radius is 0.5 m, so the centre falls 2.5 m. A fall of height $h$ takes $t = \sqrt{2h/g}$, where $g$ is 9.81: $t = \sqrt{5 / 9.81} = 0.71$ seconds, which is 43 steps, and the speed at the end is $9.81 \times 0.71 = 7.0$ m/s. Remember 7.0 m/s: bounces use it later.

:::::steps

1. Open the scene and select the ball.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Ball` in the Hierarchy. In the Inspector, set the Transform's **Translation** to 0, 3, 0: the ball moves from the start of the input page, z = 6, to the middle of the level, 3 m up. Choose **Add Component ▸ Rigid Body**. The type is **Dynamic** and the mass is 1 by default.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Ball>", "component": "Transform", "values": { "Translation": [0, 3, 0] } } }
   { "command": "component.add", "parameters": { "entity": "<the ID of Ball>", "component": "RigidBody" } }
   ```

   A command takes an entity's identifier (ID), not its name: use the ID that `entity.find` with `{ "name": "Ball" }` answers, here and in every later tab of this page.

   :::
   ::::

   **You should see:** a Rigid Body section in the Inspector, with Type Dynamic and Mass 1. A wire shape of the collider is drawn around the ball.

   **If you do not see it:** the ball has no collider, so no :term[gizmo]{id=gizmo-start} appears and the game would not move it. Choose **Add Component ▸ Sphere Collider** and look again.

2. Play and watch.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**. The ball falls onto the ground, does not bounce and lies still. Stop the game.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "build": false } }
   ```

   :::
   ::::

   **You should see:** the ball land after about three quarters of a second and stay there. This is the 43 steps you computed.

   **If you do not see it:** the ball floats, so its Gravity Scale may be 0. **Gravity Scale** multiplies the scene's gravity for one body, and 0 gives a body that floats. Set it to 1.

   Your `BallControl` still writes the ball's position when you press keys. Leave it for now: the next section replaces it.

:::::

The gravity belongs to the scene, not to a body or a script. With nothing selected, the Inspector shows the scene's settings.

Its Physics section starts with a summary, "Gravity 9.81 m/s² · 60 steps/s", and has **Gravity** (a direction with a strength, in metres per second squared, default 0, -9.81, 0), **Max Bodies** and **Max Contacts**. The last two stay at Auto, which is 0: set them only for scenes that create many bodies while they play. A script cannot change the scene's gravity. It changes only one body's Gravity Scale.

A change of gravity wakes every body. With a command, `scene.setSettings` takes `{ "gravity": [0, -9.81, 0] }`. The editor stores that change with the scene.

:::note
The rigid body's fields live in one component. The quote shows its defaults at the pin: mass 1, damping 0.05, friction 0.5 and restitution 0, no trigger, and layer 0.
:::

Each line of the next quote is a field the Inspector shows in the Rigid Body section. Read the names, then the defaults.

```cpp src="Strata/src/Strata/Physics/PhysicsComponents.h#L27-L42"
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

1. **Line 29:** the type, Dynamic unless you choose Static or Kinematic.
2. **Lines 30–32:** the mass and the two dampings, which slow a body a little every second.
3. **Lines 34–35:** the material: friction 0.5 and restitution 0.
4. **Lines 36–37:** the trigger switch and the sweep switch, both off.
5. **Line 41:** the layer, a number from 0 to 31.

::checkpoint{stage=1}

::figure{id=ball-falls}

## Roll the ball with a force

Moving a dynamic body by writing its position fights the physics engine: the body is moved twice, and it can pass through walls. So you move it with the three things physics understands. A **velocity** is a speed with a direction: 3 m/s to the right is a velocity, and 3 m/s alone is a speed. A **force** pushes a body and changes its velocity a little in every step, less for a heavier body. An **impulse** is a push that changes the velocity at once, in one blow.

The rule is the one from school. A force $F$ in newtons on a mass $m$ in kilograms gives an acceleration $a = F / m$ in metres per second squared. Read it as "the acceleration is the force divided by the mass".

Our ball has $m = 1$ and the script pushes with $F = 12$, so the acceleration is 12 m/s². One step is 1/60 second, so each step adds 12 / 60 = 0.2 m/s. After 40 steps the ball is at 8 m/s, the cap you will set, if nothing resists. Doubling the mass halves every one of those numbers.

An impulse $J$ gives a jump of velocity $J / m$ at once: $J = 5$ on a ball of mass 1 adds 5 m/s in that moment, and on a ball of mass 5 only 1 m/s.

A force acts during the next step only, and the step after it forgets it. So a script pushes again in every fixed step, in `OnFixedUpdate`. It still reads the player's wish in `OnUpdate`, because fixed steps run zero, one or several times per frame while the Move action is valid every frame. The two functions share the wish in a field.

The script's own entity comes from `GetEntity()`. Its rigid body comes from `GetEntity().GetRigidBody()`, so the push is `GetEntity().GetRigidBody().AddForce(...)`. The same object reads the speed with `GetLinearVelocity()`.

:::::steps

1. Replace the contents of `Scripts/BallControl.cpp` with the pushing version.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the file in your code editor from the Content Browser's **Scripts** root, replace its contents with the two parts below, one after the other, and save.
   :::
   :::tab[With a command]
   This step edits a file, which you do in your code editor. The script is the two parts below.
   :::
   ::::

   :::question
   The next code uses a class, `override` and a call such as `Input::GetActionValue(...)`: see [classes and inheritance](../basics/cpp-classes.md). Read it as two functions that Strata calls for you.
   :::

   The first part holds the two fields and the two functions. Look at which of them reads the wish and which one pushes.

   ```cpp src="book:tutorials/make/physics/step2/BallControl.cpp#L1-L25"
   #include "StrataScript/StrataScript.h"

   using namespace Strata;

   // Rolls the ball by pushing it: the Move action sets the direction, a force does the pushing.
   class BallControl : public Script
   {
   public:
   	float PushStrength = 12.0f; // Newtons at full push
   	float MaxSpeed = 8.0f;      // Metres per second along the ground

   	void OnUpdate(float) override
   	{
   		const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
   		m_Push = glm::vec3(move.x, 0.0f, -move.y);
   	}

   	void OnFixedUpdate(float) override
   	{
   		RigidBody body = GetEntity().GetRigidBody();
   		const glm::vec3 velocity = body.GetLinearVelocity();
   		const float groundSpeed = glm::length(glm::vec3(velocity.x, 0.0f, velocity.z));
   		if (groundSpeed < MaxSpeed)
   			body.AddForce(m_Push * PushStrength);
   	}
   ```

   1. **Lines 9–10:** the two fields, which the Inspector shows: the push in newtons and the speed cap.
   2. **Lines 14–15:** the Move action is a vector, length at most 1. Its Y part is forward, and forward in the world is minus Z. The wish is stored, not applied: `OnUpdate` only reads.
   3. **Lines 22–23:** the cap. The force is applied only while the ground speed is below `MaxSpeed`, so the ball stops accelerating there instead of growing without end.
   4. **Line 24:** the push, a force of 12 newtons times the wish, applied in every fixed step.

   The second part closes the class with the member that the two functions share, and registers the two fields.

   ```cpp src="book:tutorials/make/physics/step2/BallControl.cpp#L26-L34"
   private:
   	glm::vec3 m_Push = glm::vec3(0.0f);
   };

   ST_SCRIPT_CLASS(BallControl)
   {
   	ST_SCRIPT_FIELD(PushStrength);
   	ST_SCRIPT_FIELD(MaxSpeed);
   }
   ```

   The old field `Speed` of the input page is gone, and so is its line in `ST_SCRIPT_CLASS`.

   **You should see:** the file saved.

   **If you do not see it:** the build in the next step lists the error with its line.

2. Build, then attach the script to the ball again. The ball's Script component may still store a value for the old field `Speed`: the command of the input page set it to 4. The class has no such field now, so every play would then warn `script 'BallControl' has no field 'Speed'; the stored value is ignored`. The Inspector shows only the fields the class has, so it cannot clear the old value; attaching the script again clears it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ Build Scripts**. Select `Ball`, press the cross of `BallControl` in its Script component, then **Add Script...** and `BallControl`. The fields `PushStrength` and `MaxSpeed` show in the Inspector under `BallControl`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "script.remove", "parameters": { "entity": "<the ID of Ball>", "class": "BallControl" } }
   { "command": "script.add", "parameters": { "entity": "<the ID of Ball>", "class": "BallControl" } }
   ```

   :::
   ::::

   **You should see:** the build finish without problems and the fields appear. A play logs no warning.

   **If you do not see it:** the :term[Problems panel]{id=problems-panel} names the error. A common one is a missing `Gameplay/Move` action: see [input](input.md). A warning that names `Speed` means the old value is still stored: attach the script again.

3. Play and push the ball with W, A, S and D, or the left stick.

   **You should see:** the ball roll away, accelerate and level off near 8 m/s. After you release the keys it keeps rolling for a very long time.

   **If you do not see it:** keys reach the game only while the Game view has the focus. Click in it first.

:::::

The ball rolls on and on because Strata has no rolling resistance: a rolling ball slows only through its damping. **Linear Damping** and **Angular Damping** take away a share of the velocity every second, and the default 0.05 takes about 14 seconds to halve the speed. Raise both to 0.5 and the speed halves in about 1.4 seconds.

Three more fields shape the feel. **Friction** (default 0.5) is how strongly two touching surfaces grip. **Restitution** (default 0) is how much a body bounces: 0 does not bounce and 1 keeps all the speed. Strata mixes the two bodies of a contact like this: the contact's friction is the square root of the two frictions multiplied, and its restitution is the larger of the two.

A ball of restitution 0.5 dropped on the ground, whose restitution is 0, uses 0.5. It lands at 7.0 m/s and leaves at 3.5 m/s, and rises to $3.5^2 / (2 \times 9.81) = 0.62$ m. A bounce needs the landing speed above 1 m/s, so a slow ball stays down.

Fast bodies need one more setting. In each step physics moves a body by its speed times 1/60 second, and a bullet at 600 m/s moves 10 m in a step, so it can jump over a thin wall. **Continuous collision** makes physics sweep the body along its path and stop it at the first thing it meets, instead of checking only where it ends. Every dynamic body is swept against static things already. The switch adds the sweep against moving bodies too, for bullets.

A body that comes to rest costs nothing. **Sleeping** is the state of a body that has been slower than the sleep threshold (0.08 m/s) for half a second together with everything it touches: physics stops simulating it until something wakes it. The threshold is a project setting, and a later page tunes it.

:::::steps

1. Tune the ball. Select it and set **Linear Damping** and **Angular Damping** to 0.5, **Friction** to 0.6, **Restitution** to 0.3, and enable **Continuous Collision**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Change the fields in the Rigid Body section of the Inspector.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Ball>", "component": "RigidBody", "values": { "Friction": 0.6, "Restitution": 0.3, "LinearDamping": 0.5, "AngularDamping": 0.5, "ContinuousCollision": true } } }
   ```

   :::
   ::::

   **You should see:** the ball roll, slow and stop within a few seconds after you let go. A drop from 3 m bounces about 0.2 m once.

   **If you do not see it:** the ball behaves as before, so the fields were not changed on the ball. Check that `Ball` is selected.

:::::

::checkpoint{stage=2}

::figure{id=ball-rolls}

## Put the ball back and make it jump

Two more actions need care about when physics knows a change. A transform you write is copied into the body at the next fixed step only, and a ball that is still rolling keeps the speed it had. A **teleport** moves the body and its entity at once. `Teleport` keeps the velocities, so a reset key must also zero them, or the ball arrives at the start still rolling.

The final version of `BallControl.cpp` comes in three parts and one unchanged piece. The first part is the start of the file: two new fields and an `OnCreate` that keeps the start position.

```cpp src="book:tutorials/make/physics/step3/BallControl.cpp#L1-L17"
#include "StrataScript/StrataScript.h"

using namespace Strata;

// Rolls the ball with a force, puts it back with R and jumps with an impulse when it stands on something.
class BallControl : public Script
{
public:
	float PushStrength = 12.0f; // Newtons at full push
	float MaxSpeed = 8.0f;      // Metres per second along the ground
	float JumpImpulse = 5.0f;   // Added speed in metres per second for a mass of 1
	float GroundReach = 0.6f;   // How far below its centre the ball looks for ground, in metres

	void OnCreate() override
	{
		m_StartPosition = GetTransform().GetWorldPosition();
	}
```

1. **Lines 11–12:** the new fields: the jump's added speed and how far below its centre the ball searches for ground.
2. **Lines 14–17:** the position the ball has when the game starts, kept for the reset key.

The next quote is the whole `OnUpdate`: the push wish, then the reset on the rigid body, then the jump. Look at the three lines after the reset's `Teleport`.

```cpp src="book:tutorials/make/physics/step3/BallControl.cpp#L19-L33"
void OnUpdate(float) override
{
	const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
	m_Push = glm::vec3(move.x, 0.0f, -move.y);

	RigidBody body = GetEntity().GetRigidBody();
	if (Input::IsKeyPressed(Key::R))
	{
		body.Teleport(m_StartPosition);
		body.SetLinearVelocity(glm::vec3(0.0f));
		body.SetAngularVelocity(glm::vec3(0.0f));
	}
	if (Input::IsActionPressed("Gameplay/Jump") && IsOnGround())
		body.AddImpulse(glm::vec3(0.0f, JumpImpulse, 0.0f));
}
```

1. **Line 25:** pressing R once; `IsKeyPressed` is true in the frame of the press only.
2. **Line 27:** the ball goes to its start position at once, and queries see it there right away.
3. **Lines 28–29:** both velocities are set to zero. Without them the ball keeps its old speed and spin.
4. **Lines 31–32:** the jump, in the next paragraphs.

For the jump the ball needs to know that it stands on something. A **raycast** is a question to physics: "Starting here, going in this direction, what is the first body the line meets within this distance?" The answer has the entity, the point, the surface direction and the distance.

An **overlap** is a related question about a volume instead of a line: `Physics::OverlapSphere` and `Physics::OverlapBox` list the bodies that touch a sphere or a box.

By hand: the ball's centre is 0.5 m above the ground when it rests, and the ray starts at the centre and goes straight down for at most 0.6 m. The ground is 0.5 m away, so the ray hits.

In the air, with the centre 1.2 m up, the ground is 1.2 m away, the ray reaches only 0.6 m, and nothing is hit. The call names the ball as the entity to ignore, so the ray never hits the ball itself. Triggers are skipped unless you ask, so a coin under the ball does not count as ground. The argument `Physics::c_AllLayers` means every layer; the last section explains layers.

After `OnUpdate` comes `OnFixedUpdate`, lines 35 to 42: the push of the last section, unchanged. The last part follows it: the ground check below `private:`, the members and the registration of the four fields.

```cpp src="book:tutorials/make/physics/step3/BallControl.cpp#L43-L61"
private:
	bool IsOnGround() const
	{
		const glm::vec3 origin = GetTransform().GetWorldPosition();
		const glm::vec3 down = glm::vec3(0.0f, -1.0f, 0.0f);
		return Physics::Raycast(origin, down, GroundReach, Physics::c_AllLayers, GetEntity()).has_value();
	}

	glm::vec3 m_StartPosition = glm::vec3(0.0f);
	glm::vec3 m_Push = glm::vec3(0.0f);
};

ST_SCRIPT_CLASS(BallControl)
{
	ST_SCRIPT_FIELD(PushStrength);
	ST_SCRIPT_FIELD(MaxSpeed);
	ST_SCRIPT_FIELD(JumpImpulse);
	ST_SCRIPT_FIELD(GroundReach);
}
```

1. **Lines 44–49:** the ground check, a ray straight down from the ball's centre that ignores the ball.
2. **Line 51:** the start position that `OnCreate` keeps.
3. **Lines 55–61:** all four fields are registered, so the Inspector shows them.

The jump itself is an impulse upward. With `JumpImpulse` 5 on a ball of mass 1, the velocity changes by 5 m/s at once. The ball rises $5^2 / (2 \times 9.81) = 1.27$ m and is in the air for $2 \times 5 / 9.81 = 1.0$ second. The jump is applied in `OnUpdate`: an impulse works at once, so it does not have to wait for a fixed step. The press must be read there, never in `OnFixedUpdate`, because a frame can run zero fixed steps (the press is missed) or two (it is counted twice).

:::::steps

1. Replace `Scripts/BallControl.cpp` with the final version of the script, which adds the start position, the reset and the jump. Build the scripts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Write the file from its parts in order: lines 1 to 17, then `OnUpdate`, then the unchanged `OnFixedUpdate`, then lines 43 to 61. Save, and choose **Scripts ▸ Build Scripts**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** two new fields, `JumpImpulse` and `GroundReach`, on `BallControl`.

   **If you do not see it:** the build failed; the Problems panel shows why.

2. Play. Roll away, press R, then press Space or the gamepad's A.

   **You should see:** the ball return to its start and stand still after R, and jump about 1.2 m after the jump button, but only while it rests on the ground.

   **If you do not see it:** the ball never jumps, so the ray misses. Raise `GroundReach` to 0.7, because a ball with another radius needs another reach.

:::::

::checkpoint{stage=3}

::figure{id=ball-jumps}

## Turn the coins into triggers

Until now the `Coin` script collects a coin by measuring the distance to the ball. Physics can tell you better. A **trigger** is a body that reports when other bodies enter it and leave it, and pushes nothing. The ball passes through a trigger as through air, and the script of the trigger learns about it in `OnTriggerEnter`. A trigger notices only bodies with convex shapes, never a triangle mesh, and a body that code moves cannot have a triangle mesh at all, so a coin keeps a sphere.

A coin spins and bobs, so code moves it, and that makes it kinematic. A trigger needs a Rigid Body: you enable **Is Trigger** on it. So the coin gets a Sphere Collider and a Rigid Body of type Kinematic with Is Trigger. Two static things never report to each other, so a static trigger would not see a ball that is also static, but a dynamic ball does.

You make the change on the prefab. From the scripting pages on, `CoinPlacer` creates the coins while the game plays, so the edited scene holds no coin. You drag one coin prefab into the scene, change it, apply the change to the prefab, and delete the instance.

:::::steps

1. Drag `Prefabs/Coin.stprefab` from the Content Browser into the scene, at X 0, Y 1, Z 4.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag the prefab into the Scene view or the Hierarchy. Select the new coin instance.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Coin.stprefab", "components": { "Transform": { "Translation": [0, 1, 4] } } } }
   ```

   :::
   ::::

   **You should see:** a coin in the Hierarchy, linked to its prefab.

   **If you do not see it:** the prefab has another path. Right-click it in the Content Browser, choose **Copy Path**, and use that path.

2. Give the coin its shape and its body.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Add Component ▸ Sphere Collider** and **Add Component ▸ Rigid Body**. Set **Type** to **Kinematic** and enable **Is Trigger**. If the coin already has a collider, keep it.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.add", "parameters": { "entity": "<the coin's id>", "component": "SphereCollider" } }
   { "command": "component.add", "parameters": { "entity": "<the coin's id>", "component": "RigidBody" } }
   { "command": "component.set", "parameters": { "entity": "<the coin's id>", "component": "RigidBody", "values": { "Type": "Kinematic", "IsTrigger": true } } }
   ```

   :::
   ::::

   **You should see:** a wire sphere around the coin and a Rigid Body section with Is Trigger enabled.

   **If you do not see it:** the Rigid Body did not get added: choose it from **Add Component** first.

3. Apply the change to the prefab and delete the instance.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Inspector's menu for the coin choose **Apply All to Prefab**. Then delete the coin from the Hierarchy.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.apply", "parameters": { "entity": "<the coin's id>" } }
   ```

   :::
   ::::

   **You should see:** no coin in the scene, and every coin that `CoinPlacer` makes from now on has a trigger.

   **If you do not see it:** the change does not reach the prefab while the game plays. Stop the game first: Apply works in edit mode only.

4. Replace `Scripts/Coin.cpp` with the version that collects the coin on entry, and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace the text of `Scripts/Coin.cpp` with the two parts below, one after the other, save, and choose **Scripts ▸ Build Scripts**.
   :::
   :::tab[With a command]
   No command writes a file: replace its text in your code editor, then run the build.

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   This `Coin` is shorter than the one of [the scene page](scripting-scene.md): physics now decides when the ball arrives, so the distance test and the glow are gone. It turns at 120 degrees each second and bobs 0.15 m. The first part holds the fields and `OnCreate`.

   ```cpp src="book:tutorials/make/physics/step4/Coin.cpp#L1-L17"
   #include "StrataScript/StrataScript.h"

   #include <cmath>

   using namespace Strata;

   // Turns and bobs, and is collected when the ball enters its trigger.
   class Coin : public Script
   {
   public:
   	float DegreesPerSecond = 120.0f;
   	float BobHeight = 0.15f;

   	void OnCreate() override
   	{
   		m_BaseHeight = GetTransform().GetTranslation().y;
   	}
   ```

   1. **Lines 11–12:** the two fields: the speed of the turn and the height of the bob.
   2. **Lines 14–17:** the height the coin was placed at, which the bob swings around.

   The second part is the turn, the bob and the new function, then the registration.

   ```cpp src="book:tutorials/make/physics/step4/Coin.cpp#L19-L42"
   	void OnUpdate(float deltaTime) override
   	{
   		TransformComponent transform = GetTransform();
   		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
   		transform.SetRotation(turn * transform.GetRotation());
   		glm::vec3 position = transform.GetTranslation();
   		position.y = m_BaseHeight + BobHeight * std::sin(Time::GetElapsedTime() * 2.0f);
   		transform.SetTranslation(position);
   	}

   	void OnTriggerEnter(const Collision& collision) override
   	{
   		if (collision.Other.GetName() == "Ball")
   			GetEntity().Destroy();
   	}
   private:
   	float m_BaseHeight = 0.0f;
   };

   ST_SCRIPT_CLASS(Coin)
   {
   	ST_SCRIPT_FIELD(DegreesPerSecond);
   	ST_SCRIPT_FIELD(BobHeight);
   }
   ```

   1. **Lines 19–27:** the turn and the bob of the scene page, at the new speed and height.
   2. **Lines 29–33:** the new function: the coin is collected when the ball enters its trigger.

   To keep the glow, keep the `Coin` of the scene page instead and change three things. Delete the field `CollectDistance` and its `ST_SCRIPT_FIELD` line. Delete the two lines of the collect test, `if (distance < CollectDistance)` and the `GetEntity().Destroy();` below it, and keep the glow's test. Add the function of lines 29 to 33 below `OnUpdate`.

   **You should see:** the build finish without problems.

   **If you do not see it:** the Problems panel lists the error.

:::::

The function says: when something enters my trigger, and its name is `Ball`, destroy me. The `collision` holds the other entity, a point and a normal, a direction from this entity towards the other. A `Coin` that kept the scene page's collect test would be collected twice, once by each way.

`OnCollisionEnter` and `OnCollisionExit` work in the same way for bodies that touch and push: a crate that lands on the ground, a ball that hits a wall. Their `Collision` holds the other entity, the point where they touch and the normal. The sound page uses them. Strata sends no event while bodies stay in contact, and no impulse or impact speed. A script that wants the strength of a hit reads the velocities of the two bodies.

:::caution
Spawn bodies apart. Two bodies that start inside each other are pushed out at up to 3 m/s, which can be a violent jump. And `Scene::Instantiate` with a position sets the new root's scale to 1, not the prefab's scale, unless you pass a scale. A prefab made at scale 2 comes out half the size you drew.
:::

::checkpoint{stage=4}

::figure{id=coins-collected}

## Let the ball pass a ghost wall

Not everything should touch everything. A coin should not stop a ball, and a door that only a ghost passes through needs a rule. Strata sorts bodies into 32 numbered groups. A **collision layer** is one of the 32 groups, numbered 0 to 31, that a rigid body belongs to; the body's Layer field chooses it, and a layer can have a name.

The **layer matrix** is the table of the project that says, for each pair of layers, whether bodies on them collide. Everything collides at first.

A pair of bodies collides only when the table allows their two layers. A **mask** is the set of layers one thing may touch or look at, written as one number with a bit for each layer. A query that takes layers uses a mask, and the mask of layer $n$ is `1u << n`, read "1 moved $n$ places to the left", which is 2 to the power $n$: layer 3 gives 8.

The layers belong to the project, not the scene: every scene uses the same names and table. You edit them in **File ▸ Project Settings... ▸ Physics ▸ Collision Layers**. A script changes the pair for the playing scene with `Physics::SetLayersCollide`; that lasts until the scene ends or the project's table changes. A script finds a layer by the name you typed with `Physics::GetLayerIndex`, which gives -1 when the project has no such name.

The wall needs a Rigid Body of type Static, because a collider alone is a static body on layer 0 with the default material, and the layer comes only from a Rigid Body.

:::::steps

1. Name the layers `Ball` and `Ghost`, and stop the pair from colliding.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Project Settings... ▸ Physics ▸ Collision Layers**. Press **Name a Layer** twice, which names layers 1 and 2, and type `Ball` and `Ghost` as their names. In the matrix, clear the box where `Ball` and `Ghost` meet.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.setCollisionLayers", "parameters": { "layerNames": { "1": "Ball", "2": "Ghost" }, "layerCollisions": [ { "layers": ["Ball", "Ghost"], "collide": false } ] } }
   ```

   :::
   ::::

   **You should see:** the two names in the list and the pair cleared in the matrix.

   **If you do not see it:** a name that another layer has already is refused; choose another.

2. Make a wall, give it a Static Rigid Body on `Ghost`, and put the ball on `Ball`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **+ ▸ Cube** in the Hierarchy, name it `GhostWall`, set its position to 4, 1, 0 and its scale to 0.5, 2, 4. Add a **Rigid Body**, set its **Type** to **Static** and its **Layer** to `Ghost`. Select `Ball` and set its **Layer** to `Ball`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "GhostWall", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "Transform": { "Translation": [4, 1, 0], "Scale": [0.5, 2, 4] } } } }
   { "command": "component.add", "parameters": { "entity": "<the wall's id>", "component": "RigidBody" } }
   { "command": "component.set", "parameters": { "entity": "<the wall's id>", "component": "RigidBody", "values": { "Type": "Static", "Layer": "Ghost" } } }
   { "command": "component.set", "parameters": { "entity": "<the ID of Ball>", "component": "RigidBody", "values": { "Layer": "Ball" } } }
   ```

   :::
   ::::

   **You should see:** a solid-looking wall on the ground to the right of the ball.

   **If you do not see it:** the wall is out of the view. Select it and press **F** over the Scene view.

3. Add the `GhostSwitch` script to the wall, so G closes and opens the wall to the ball.

   ```cpp src="book:tutorials/make/physics/step5/GhostSwitch.cpp#L9-L20"
   void OnUpdate(float) override
   {
   	if (!Input::IsKeyPressed(Key::G))
   		return;
   	const int32_t ball = Physics::GetLayerIndex("Ball");
   	const int32_t ghost = Physics::GetLayerIndex("Ghost");
   	if (ball < 0 || ghost < 0)
   		return;
   	const uint32_t ballLayer = static_cast<uint32_t>(ball);
   	const uint32_t ghostLayer = static_cast<uint32_t>(ghost);
   	Physics::SetLayersCollide(ballLayer, ghostLayer, !Physics::GetLayersCollide(ballLayer, ghostLayer));
   }
   ```

   1. **Line 11:** the script acts only in the frame where G is pressed.
   2. **Lines 13–16:** layer numbers by name; both must exist, so a missing name changes nothing.
   3. **Line 19:** the pair is switched to the opposite of what it is now.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Save the file as `Scripts/GhostSwitch.cpp` and choose **Scripts ▸ Build Scripts**. Select the wall, choose **Add Component ▸ Script** and pick `GhostSwitch`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<the wall's id>", "class": "GhostSwitch" } }
   ```

   :::
   ::::

   **You should see:** after the build and the new Script component on the wall, the ball roll through it. Press G in the game and it hits the wall.

   **If you do not see it:** the ball stops at the wall at once. Check that the matrix box is clear and that both layer fields are set.

:::::

What Strata does not do here, so you do not search for it. Nothing links two bodies, so there are no joints, no limp characters made of linked bodies and no vehicles. Colliders are Box, Sphere, Capsule and Mesh only, and there are no height fields.

The Hierarchy's **Cylinder**, **Cone** and **Torus** get a convex hull of their own mesh, with at most 64 points, and the hull of a **Torus** fills its hole. Cloth, soft bodies, destruction, fluids and floating in water do not exist. Contacts begin and end, with no stay event. Rolling resistance and moving belts are not there either. The [index of what Strata does not have](../appendix/not-in-strata.md) lists these and more.

The picture below shows the same rule with the ball dropped onto the wall in place of rolled at it. The ball falls through the wall and rests half inside it.

::checkpoint{stage=5}

::figure{id=ghost-wall}

## Summary

- Choose the body by who moves the thing: a collider alone or a Static body for what never moves, Dynamic for what physics moves, and Kinematic for what code moves.
- A force changes the velocity by the force divided by the mass, a little in every fixed step; an impulse changes it at once by the impulse divided by the mass.
- Enable Is Trigger for a thing that only reports overlaps; its script learns of the ball in `OnTriggerEnter`, and triggers never see triangle meshes.
- A raycast down from the ball tells whether it stands on something, and an impulse makes it jump; the press is read in `OnUpdate`.
- A collision layer and the project's matrix decide which bodies collide; a script changes the pair with `Physics::SetLayersCollide`.

## Check yourself

1. A spinning lift carries the ball upward, and the ball must ride on it. Which body type does the lift need, and why not Dynamic?

   :::answer{tests="body-types"}
   Kinematic. Your code moves it along its path and gravity or the ball's weight cannot push it; it still pushes the ball. A dynamic lift would sag under the ball and fall.
   :::

2. A body of mass 2 gets a force of 10 newtons in each of 30 fixed steps, at 60 steps per second. Another body of mass 2 gets one impulse of 5. Compare their change of velocity.

   :::answer{tests="force-impulse"}
   The force acts for half a second. It gives an acceleration of 10 / 2 = 5 m/s², so the velocity changes by 5 × 0.5 = 2.5 m/s. The impulse changes it at once by 5 / 2 = 2.5 m/s. Equal in the end, but the impulse is instant.
   :::

3. You set a coin's collider to a Mesh Collider that is not convex, and the coin stops being collected. Why?

   :::answer{tests="trigger-callbacks"}
   A mesh that is not convex works only on a static body. The coin is kinematic, so physics ignores that collider, the Console warns, and the coin has no shape to be entered. Keep a sphere or enable **Convex**.
   :::

4. Why does the jump read its press in `OnUpdate`?

   :::answer{tests="ground-ray"}
   A frame runs zero or more fixed steps. A press read in `OnFixedUpdate` is missed when the frame runs none and counted twice when it runs two. `OnUpdate` runs once per frame.
   :::

5. The ball's layer is `Ball` and the wall has only a Box Collider. The matrix clears `Ball` and `Ghost`. Does the ball pass through the wall?

   :::answer{tests="layers"}
   No. A collider alone is a static body on layer 0, and layer 0 still collides with `Ball`. The wall needs a Rigid Body of type Static with its Layer set to `Ghost`.
   :::

6. Why does the push in `BallControl` go in `OnFixedUpdate`?

   :::answer{tests="force-impulse"}
   A force acts during the next fixed step only. To push the ball for as long as the key is held, the script applies the force in every fixed step.
   :::

## Exercises

1. **Basic.** Make four balls, `Wood`, `Metal`, `Rubber` and `Ice`, and drop them from 3 m onto the ground, whose friction is 0.5 and restitution 0. Give them the frictions 0.5, 0.3, 1.0 and 0.02 and the restitutions 0.1, 0.05, 0.8 and 0.1. Predict the friction the ground and each ball use, and how high the rubber ball bounces.

   :::answer[Worked solution]{tests="body-types" solution="tutorials/make/physics/exercise-1.tutorial.json"}
   The contact's friction is the square root of the product: wood √(0.5 × 0.5) = 0.5, metal 0.39, rubber 0.71, ice 0.1, so the ice ball slides on the ground. The restitution is the larger of the two, so each ball keeps its own, as the ground has 0. The rubber ball lands at 7.0 m/s, leaves at 0.8 × 7.0 = 5.6 m/s, and rises 5.6² / 19.62 = 1.6 m.
   :::

2. **Medium.** Stack ten crates, each a unit cube with a Box Collider and a Dynamic Rigid Body, with their centres 1.01 m apart. Write a script that topples the stack when you press T, with `AddImpulseAtPosition`.

   :::answer{tests="force-impulse"}
   Leave a gap of 0.01 m, so the crates do not start inside each other. Find the top crate with `Scene::FindEntityByName("Crate10")`. When T is pressed call `GetRigidBody().AddImpulseAtPosition(glm::vec3(8.0f, 0.0f, 0.0f), position + glm::vec3(0.0f, 0.4f, 0.0f))`, with `position` the crate's :term[world position]{id=world-position}. The push is off-centre, near the top, so it also turns the crate and the stack topples.
   :::

3. **Hard.** Build a trigger that counts the balls that fall into it, once each, and a launch pad that sends a ball down a ramp. The Physics Playground sample has both.

   :::answer{tests="trigger-callbacks"}
   Both are triggers with a script. The counter keeps the ids of the balls it has counted, `collision.Other.GetID()`, in a set, and adds one only when the id is new, so a ball that bounces out and in counts once. The pad's `OnTriggerEnter` calls `collision.Other.GetRigidBody().SetLinearVelocity(LaunchVelocity)` for an entity tagged `Ball`. Read `GoalBasket.cpp` and `LaunchPad.cpp` in the sample.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsComponents.h`: the rigid body and the collider components, with their defaults.
- `StrataScriptCore/Include/StrataScript/Physics.h`: `RigidBody`, `Physics`, `RaycastHit` and `Collision`, the functions of this page.
- `Strata/src/Strata/Physics/PhysicsWorld.cpp`: how bodies are built from entities, and the warning for a rigid body without a collider.
- `Samples/PhysicsPlayground/Scripts/GoalBasket.cpp`: a trigger that counts balls.

## Further reading

- [Gaffer On Games, "Fix Your Timestep!"](https://gafferongames.com/post/fix_your_timestep/): why physics runs in fixed steps (intermediate).
