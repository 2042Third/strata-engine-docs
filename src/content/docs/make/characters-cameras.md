---
id: make/characters-cameras
title: "Characters and cameras"
description: "Make a player who walks, jumps, climbs and rides a platform on an obstacle course, and a camera that follows it smoothly at any frame rate."
kind: tutorial
size: L
tracks: [G]
needs: [make/gameplay-math, make/script-fields]
time: 150
learn:
  - id: controller-not-body
    text: explain why a game character is a character controller and not a rigid body
  - id: walk-jump
    text: write a script that walks a character relative to the camera and jumps with coyote time
  - id: drawn-camera
    text: explain why a follow camera reads the drawn position in OnLateUpdate
  - id: camera-arm
    text: build a camera arm that a raycast shortens at walls and that the mouse turns
  - id: platform-cameras
    text: set up a moving platform, a return after a fall and a second camera that the game switches to
since: 0.3.0
status: final
---

## What you will make

You will make a player who walks an obstacle course, and a camera that follows it. The player climbs a low step, stops at a high one, slides down a steep ramp, rides a moving platform and starts again after a fall.

::figure{id=result}

## What you need

- The obstacle course, in Checkpoint 1 with the first section's player: a project from the Basic 3D template, with its dark grey ground. Its cubes are two steps of 0.3 m and 0.5 m, two ramps of 40 and 50 degrees, a wall, a ledge, a crate and a kinematic platform.
- The input map `Gameplay` with the actions `Move`, `Look` and `Jump`, as [Input and input actions](input.md) made them, also in Checkpoint 1.
- The tools of [Gameplay math](gameplay-math.md): normalize, a forward flattened onto the ground, the angle of a direction and smoothing that does not depend on the frame rate.
- The way to point a :term[script field]{id=script-field} at an entity from [Script fields](script-fields.md), and the fixed step from [the script loop](script-loop.md).
- About two and a half hours.

Each checkpoint offers the project as it stands at that point, and the editor commands that lead there from the checkpoint before. To build the course yourself, make a Basic 3D project (**New Project** in the launcher, or `project.create` with the template `basic3d`). Then run Checkpoint 1's commands: they build the blocks, the input map and the player.

The commands write no file: before a later checkpoint's commands, copy the scripts its section names from that checkpoint's project into yours.

## Make the player

A game character walks, jumps and climbs stairs. Your first idea may be a :term[rigid body]{id=rigid-body}, as for the ball, pushed by forces. Think what happens. A capsule on the ground falls over when you push it, it slides down a slope instead of standing, and a step the height of your hand stops it like a wall.

You can fix some of this by locking the rotation or adding friction. Each fix changes the body everywhere, and a game wants the opposite: a character that does what the player meant, whatever the physics would do.

A **character controller** is an upright capsule that your code moves by a walking velocity, and that physics only stops, never tips over. Every fixed step it falls with gravity, slides along walls, walks up steps, stops at slopes that are too steep, follows the ground down a small drop and pushes crates away. It moves with a platform it stands on, and keeps that motion when it leaves.

The controller writes its entity's position and never its rotation: turning the body toward where it walks is your job, as the next section shows.

:::caution
An entity has a Rigid Body or a Character Controller, never both. With both, Strata simulates the entity as the rigid body, the controller does nothing, and the Console warns that the entity has both. Remove one of them.
:::

The component has these fields.

| Field | Default | What it sets |
| --- | --- | --- |
| **Height** | 1.8 | Total height of the capsule, in metres |
| **Radius** | 0.3 | Radius of the capsule, in metres |
| **Step Height** | 0.35 | The highest step it walks up, in metres |
| **Max Slope Degrees** | 45 | The steepest slope it walks up, in degrees from the horizontal |
| **Push Strength** | 200 | The largest force on a crate it pushes, in newtons |
| **Layer** | 0 | The :term[collision layer]{id=collision-layer}, as for a rigid body |

The capsule's bottom is the entity's origin, so a player at height 0 stands with its feet on the ground. Rotation and scale of the entity never change the capsule. The controller has no mesh: the player's visible body is a child entity with a capsule mesh.

A built-in capsule mesh is 2 m tall and 1 m wide, centred on its origin. For a body of 1.8 m by 0.6 m, scale it by 0.9 in height and 0.6 in width. To put its feet on the player's origin, lift it by half its new height: 0.9 m.

:::::steps

1. Create the player at the start of the course.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **+ ▸ Empty** in the Hierarchy and name the entity `Player`. In the Inspector set its Translation to (0, 0, 2). Choose **Add Component ▸ Character Controller**.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Player", "components": {
       "Transform": { "Translation": [0, 0, 2] }, "CharacterController": { "Height": 1.8, "Radius": 0.3 } } } }
   ```

   :::
   ::::

   **You should see:** a Character Controller section with the fields of the table, and a wire capsule around the player in the Scene view, its bottom on the ground.

   **If you do not see it:** the wire capsule needs the entity selected. Select `Player` in the Hierarchy.

2. Give the player a body.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `Player` and choose **Create Child ▸ Empty**. Name it `Body`, add a Mesh :term[Renderer]{id=renderer} with the mesh `Builtin/Capsule`, set its Translation to (0, 0.9, 0) and its Scale to (0.6, 0.9, 0.6).
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Body", "parent": "<the Player's ID>", "components": {
       "MeshRenderer": { "Mesh": "Builtin/Capsule" }, "Transform": { "Translation": [0, 0.9, 0], "Scale": [0.6, 0.9, 0.6] } } } }
   ```

   :::
   ::::

   **You should see:** a grey capsule standing on the ground, as tall as the wire capsule.

   **If you do not see it:** the body sinks or floats. Its Translation must be 0.9 in Y.

3. Play and watch.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play** or **Ctrl+P**. Stop the game after a moment.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "build": false } }
   ```

   :::
   ::::

   **You should see:** nothing moves. The controller found the ground and rests on it.

   **If you do not see it:** the player falls through the ground. Check that its `Layer` is 0 like the ground's.

:::::

::checkpoint{stage=1}

::figure{id=player-capsule}

## Walk relative to the camera

The player does not walk yet. A script reads the `Move` action and tells the controller where to go. A person who pushes up on the stick wants to walk away from the camera, not toward minus Z of the world, so the direction comes from the camera.

Take the camera's forward direction and flatten it onto the ground: set its Y to 0 and normalize, as [Gameplay math](gameplay-math.md) taught. The right side is the flat forward turned by a quarter turn: for a forward of $(f_x, 0, f_z)$ the right is $(-f_z, 0, f_x)$. Here $f_x$ and $f_z$ are the flat components of the forward. A camera that looks along minus Z has the forward $(0, 0, -1)$ and the right $(1, 0, 0)$, so a stick pushed up and right, $(1, 1)$, walks along $(1, 0, -1)$.

Turn the camera a quarter turn to look along plus X. Its forward is $(1, 0, 0)$ and its right is $(0, 0, 1)$. The push up on the stick now walks along $(1, 0, 0)$: still away from the camera.

The walking velocity is that direction times a speed. You call `Move` with it, in metres per second and in world space. The controller keeps the velocity until your next call, so a call every frame is fine, and `Move` with a zero vector stops.

Then the body turns. A body that looks along minus Z and turns by $\theta$ about Y looks along $(-\sin\theta, 0, -\cos\theta)$. So for a direction $(m_x, 0, m_z)$ the target angle is $\theta = \operatorname{atan2}(-m_x, -m_z)$, where $m_x$ and $m_z$ are the components of the walking direction. For $(1, 0, 0)$ it is $\operatorname{atan2}(-1, 0) = -90$ degrees. The body does not snap to it: each frame it covers the share $1 - e^{-k\,\Delta t}$ of the remaining angle, with $k$ = 12 per second.

:::question
The quote below uses `virtual` and `override`: a :term[script class]{id=script-class} replaces functions of its parent. See [classes and inheritance](../basics/cpp-classes.md).
:::

The first quote is the work of one frame: the direction, the call and the turn.

```cpp src="book:tutorials/make/characters-cameras/step2/PlayerController.cpp#L14-L25"
void OnUpdate(float deltaTime) override
{
	const glm::vec3 move = GetMoveDirection();
	GetEntity().GetCharacterController().Move(move * WalkSpeed);
	if (glm::length(move) > 0.05f)
	{
		// Forward is -Z, so a turn of yaw radians about Y points the body along (-sin, 0, -cos).
		const float target = std::atan2(-move.x, -move.z);
		m_Yaw += std::remainder(target - m_Yaw, 6.2831853f) * (1.0f - std::exp(-TurnSharpness * deltaTime));
		GetTransform().SetWorldRotation(glm::angleAxis(m_Yaw, glm::vec3(0.0f, 1.0f, 0.0f)));
	}
}
```

1. **Line 16:** the direction on the ground, from the helper below.
2. **Line 17:** one `Move` call. The controller keeps the velocity until the next frame.
3. **Line 18:** a push too small to mean anything leaves the body as it is.
4. **Line 22:** the turn takes the short way round: `std::remainder` wraps the difference into half a turn each way.

The helper is the flattening and the quarter turn of the example.

```cpp src="book:tutorials/make/characters-cameras/step2/PlayerController.cpp#L29-L42"
glm::vec3 GetMoveDirection() const
{
	const Entity camera = Scene::GetPrimaryCamera();
	if (!camera.IsValid())
		return glm::vec3(0.0f);
	glm::vec3 forward = camera.GetTransform().GetForward();
	forward.y = 0.0f;
	if (glm::length(forward) < 0.001f)
		return glm::vec3(0.0f);
	forward = glm::normalize(forward);
	const glm::vec3 right(-forward.z, 0.0f, forward.x);
	const glm::vec2 input = Input::GetActionValue("Gameplay/Move");
	return right * input.x + forward * input.y;
}
```

1. **Lines 31–33:** a game without a primary camera has nothing to walk relative to, so the player stands.
2. **Lines 36–37:** a camera that looks straight down has no flat forward, so the player stands too.
3. **Line 39:** the right side, the quarter turn of the example.

:::::steps

1. Add the script to the player.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy `Scripts/PlayerController.cpp` from the checkpoint, or type the code. Press **Ctrl+B**, select `Player` and choose **Add Component ▸ Script**, then pick `PlayerController`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<the Player's ID>", "class": "PlayerController" } }
   ```

   :::
   ::::

   **You should see:** a Script section with the fields `WalkSpeed` and `TurnSharpness`, and no error in the :term[Problems panel]{id=problems-panel}.

   **If you do not see it:** the class is missing from the list. Build again and read the first error.

2. Play and walk.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, click into the Game view and hold **W**, then add **D**. Then hold **S** alone.
   :::
   :::tab[With a command]
   Start paused and hold **W** for 30 fixed steps; then hold **S** the same way.

   ```json
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "input.key", "parameters": { "key": "W", "steps": 30 } }
   { "command": "play.step", "parameters": { "steps": 31 } }
   ```

   `component.get` of the `Transform` shows where it stands.
   :::
   ::::

   **You should see:** the capsule walks away from the camera at 5 m/s, turns toward the right when you add **D**. With **S** it walks back toward the camera, under it, and stops at the `Wall`.

   **If you do not see it:** the capsule stays still. The game needs a primary camera: check that `Main Camera` has Primary on.

:::::

::checkpoint{stage=2}

::figure{id=walk-vectors}

## Jump and know the ground

`Jump` gives the player an upward speed in metres per second at the next fixed step. It works in the air too, so your script decides when a jump is allowed. With 5 m/s and a gravity of 9.81 m/s², the player rises $5^2 / (2 \times 9.81) = 1.27$ m and stays in the air $2 \times 5 / 9.81 = 1.02$ s.

The controller knows what it stands on. `GetGroundState` returns one of four states:

- **on ground**: ground not steeper than the slope limit. `IsGrounded` is true only then.
- **on steep ground**: ground too steep to stand on, so the player slides down it.
- **not supported**: touching something that does not hold it up, such as a wall in the air.
- **in air**: touching nothing.

A ledge asks for care. A player who runs off a ledge and presses jump 0.05 s later was not late in their own mind. **Coyote time** is a short time after the player leaves the ground during which a jump still counts. At 5 m/s a window of 0.15 s is 0.75 m of path.

The script counts the seconds since the player last stood on the ground, and allows a jump while the count is at most the window. One detail needs care: `Jump` acts at the next fixed step, so for a frame or two the player still looks grounded. Without a guard the player jumps twice. The script refuses new jumps for 0.2 s after one, and starts the count above the window.

```cpp src="book:tutorials/make/characters-cameras/step3/PlayerController.cpp#L30-L41"
GroundStateNumber = static_cast<int>(controller.GetGroundState());
m_JumpCooldown = std::max(0.0f, m_JumpCooldown - deltaTime);
if (controller.IsGrounded() && m_JumpCooldown <= 0.0f)
	m_AirSeconds = 0.0f;
else
	m_AirSeconds += deltaTime;
if (Input::IsActionPressed("Gameplay/Jump") && m_AirSeconds <= CoyoteSeconds && m_JumpCooldown <= 0.0f)
{
	controller.Jump(JumpSpeed);
	m_JumpCooldown = 0.2f; // The jump starts at the next fixed step: until then the ground still counts
	m_AirSeconds = CoyoteSeconds + 1.0f;
}
```

1. **Line 30:** the state as a number to watch in the Inspector: 0 on ground, 1 on steep ground, 2 not supported, 3 in air.
2. **Lines 32–35:** the count is 0 on the ground once the lock is over, and grows otherwise.
3. **Line 36:** a jump needs this frame's press, a count within the window and no lock.
4. **Lines 38–40:** the jump, the lock, and a count above the window so that a second press in the air does nothing.

:::::steps

1. Replace the script with the jump version.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace `Scripts/PlayerController.cpp` with the code of this stage and press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the new fields `JumpSpeed`, `CoyoteSeconds` and `GroundStateNumber`.

   **If you do not see it:** the old fields remain. Stop the game, build again and select `Player` once more.

2. Jump on the ground, then off the ledge.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Play and press **Space** on flat ground. Walk to the `Ledge` on the right, climb it with a jump and walk off its edge, pressing **Space** a moment after the edge.
   :::
   :::tab[With a command]
   Tap **Space** once the player stands: 32 steps later it is at the top.

   ```json
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "play.step", "parameters": { "steps": 30 } }
   { "command": "input.key", "parameters": { "key": "Space", "steps": 1 } }
   { "command": "play.step", "parameters": { "steps": 32 } }
   ```

   `component.get` of the `Transform` shows the height, `script.get` the `GroundStateNumber`.
   :::
   ::::

   **You should see:** a jump of about 1.3 m. `GroundStateNumber` shows 0 on the ground and 3 in the air, and a press a moment after the edge still jumps.

   **If you do not see it:** you cannot climb the ledge. It is 1 m high and the jump rises 1.27 m, so start the jump close to it.

:::::

::checkpoint{stage=3}

::figure{id=jump-states}

## Climb stairs and meet slopes

Two numbers decide what the player climbs. `Step Height`, 0.35 m, is the highest step it walks up as if it were flat. `Max Slope Degrees`, 45, is the steepest ground that counts as ground. Predict before you walk.

The step of 0.3 m is below 0.35 m: the player walks up it without a jump. The step of 0.5 m is above: the player walks into it like a wall and stops. A ramp of 40 degrees is below 45, so the state stays 0 and the player walks up. A ramp of 50 degrees is above: the player walks into its foot like a wall and stops on the flat ground, the state still 0. Jump onto it and the state is 1: the player slides back down.

The limits belong to the capsule, not to the mesh. The controller meets the :term[colliders]{id=collider} of the boxes, and the numbers act at once when you change them.

:::::steps

1. Walk at the steps.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Play. Walk toward `Step03` at the left, then toward `Step05` beside it.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "build": false } }
   ```

   :::
   ::::

   **You should see:** the player climbs the first step in one smooth movement and stops at the second.

   **If you do not see it:** the player climbs both. Check that `Step Height` is 0.35.

2. Walk at the ramps.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Walk to `Ramp40`, then to `Ramp50`, and watch `GroundStateNumber`. At the foot of `Ramp50`, keep walking at it and press **Space**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.get", "entityName": "Player", "parameters": { "class": "PlayerController" } }
   ```

   :::
   ::::

   **You should see:** the player climbs the 40 degree ramp and stops at the foot of the 50 degree ramp with `GroundStateNumber` at 0. After the jump it lands on the 50 degree ramp and slides back down to its foot, `GroundStateNumber` at 1 while it slides.

   **If you do not see it:** it climbs both. Check that `Max Slope Degrees` is 45.

:::::

::checkpoint{stage=4}

::figure{id=stairs-slopes}

## Make the camera follow

The camera still stands where the template put it. A follow camera is a script on the camera that moves it behind the player every frame. It keeps a point, the pivot, 1.5 m above the player's feet, and puts the camera on an arm of 7 m behind and above the pivot.

The pivot follows the player with the smoothing of [Gameplay math](gameplay-math.md): each frame covers the share $1 - e^{-k\,\Delta t}$ of the gap. With $k$ = 14 per second, a frame of 1/60 s covers 0.21 of the gap and a frame of 1/30 s covers 0.37. Two frames of 1/60 s leave $0.79 \times 0.79 = 0.63$ of the gap, the same as one frame of 1/30 s.

The script runs in `OnLateUpdate`, after all `OnUpdate` calls of the frame, so the camera sees where everything ended. The target is an entity field that you set in the Inspector. The first version reads the player's position the plain way, `GetWorldPosition()`.

```cpp src="book:tutorials/make/characters-cameras/step5/FollowCamera.cpp#L24-L31"
void OnLateUpdate(float deltaTime) override
{
	if (!Target.IsValid())
		return;
	const glm::vec3 pivot = Target.GetTransform().GetWorldPosition() + glm::vec3(0.0f, PivotHeight, 0.0f);
	m_Pivot = glm::mix(m_Pivot, pivot, 1.0f - std::exp(-FollowSharpness * deltaTime));
	Place();
}
```

The code reads the player, moves the pivot a share of the way and places the camera. Walking itself runs in the fixed steps, 60 each second by default, and a frame between two steps reads the position the latest step left. To see the problem, run fewer steps than the screen has frames: at 30 steps a second the player moves 5 / 30 = 0.167 m per step. On a screen of 144 frames a second, about 4.8 frames read the same position, and then it jumps by 0.167 m.

:::::steps

1. Put the script on the camera and point it at the player.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy `Scripts/FollowCamera.cpp` from the checkpoint and press **Ctrl+B**. Select `Main Camera`, choose **Add Component ▸ Script**, pick `FollowCamera` and drag `Player` from the Hierarchy onto the field `Target`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<the camera's ID>", "class": "FollowCamera", "fields": { "Target": "<the Player's ID>" } } }
   ```

   :::
   ::::

   **You should see:** the field `Target` showing `Player`.

   **If you do not see it:** the field is empty and the camera stays. Drag again.

2. Slow the steps to see the problem.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Project Settings...**, the category **Physics**, the page **Timing**, and set **Fixed Rate** to 30. Play and walk in a circle.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.setSettings", "parameters": { "section": "Scene.Timing", "value": { "FixedRate": "30" } } }
   ```

   :::
   ::::

   **You should see:** at the start the camera stands at the end of its 7 m arm, which slopes down by 20 degrees. It is 6.6 m behind the player (Z 8.6 for a player at Z 2) and 3.9 m above its feet, behind the `Wall`, which hides the player. Walk forward with **W**: the camera follows, and the capsule shakes a little against the picture while it walks.

   **If you do not see it:** the shake is small. Set `WalkSpeed` to 10 and watch the capsule's edge.

:::::

The shake has a cause. The player's body is not drawn where the :term[world position]{id=world-position} says. Strata draws what moves in fixed steps between its last two poses, so the body moves along a smooth line. The world position the camera reads moves in stairs: still for a few frames, then a jump.

The position and rotation at which Strata draws an entity in this frame are its **drawn pose**. For what moves in fixed steps, the drawn pose lies between the entity's last two poses.

**Interpolation** is the drawing of a moving entity between its last two poses, so that motion looks smooth at any frame rate.

The **step alpha** is the fraction of the way from the older pose to the newer that the frame draws, from 0 to 1. Take the player at 5 m/s and 60 steps a second: poses 0.0833 m apart, the last two at 0.2500 m and 0.3333 m. With a step alpha of 0.4 the drawn position is $0.2500 + 0.4 \times 0.0833 = 0.2833$ m, while the world position says 0.3333 m. The world position is where physics left the player, and the drawn position is where the player is seen.

A camera must track the drawn position, or it tracks a place where the player is not. Change one word in each of the two places that read the target.

```cpp src="book:tutorials/make/characters-cameras/step5b/FollowCamera.cpp#L24-L31"
void OnLateUpdate(float deltaTime) override
{
	if (!Target.IsValid())
		return;
	const glm::vec3 pivot = Target.GetTransform().GetDrawnPosition() + glm::vec3(0.0f, PivotHeight, 0.0f);
	m_Pivot = glm::mix(m_Pivot, pivot, 1.0f - std::exp(-FollowSharpness * deltaTime));
	Place();
}
```

`OnLateUpdate` now reads `GetDrawnPosition()`, and so does `OnCreate`, which places the camera when the game starts: the camera sees the player on the line, not on the stairs.

:::::steps

1. Follow the drawn position.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace `GetWorldPosition()` by `GetDrawnPosition()` in `OnCreate` and `OnLateUpdate`, and press **Ctrl+B**. Play with **Fixed Rate** at 30 and walk in a circle.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the shake is gone, even at 30 steps a second.

   **If you do not see it:** it remains. Check both lines, and that **Interpolation** on the same page is on.

:::::

::checkpoint{stage=5}

::figure{id=follow-judder}

## Feel the fixed rate

The Timing page has two controls that decide how motion feels. With **Interpolation** on, the picture is one step behind the game. At 30 steps a second that is 33 ms, 200 % of a frame at 60 frames per second. At 60 steps it is 17 ms, 100 %, and at 120 steps 8 ms, 50 %. This is the price of smooth motion, and the camera has the same delay as the player, so nothing shakes.

With **Interpolation** off, the picture shows each step as it is, with a delay between 0 and one step. At 30 steps the player moves in jumps of 0.167 m and the camera shakes with it. At 120 steps the jumps are 0.042 m and are much harder to see. A higher rate costs more physics work: 120 steps do twice the work of 60.

Choose with these numbers. A game with fast bodies wants a higher rate. A game that wants smooth motion needs only Interpolation on, and most games keep 60 steps with it on, as the course does.

:::::steps

1. Try the settings and return to the default.

   ::::tabs{sync=how}
   :::tab[In the editor]
   On the Timing page set **Fixed Rate** to 30, play and walk, then 120. Turn **Interpolation** off and repeat. End with **Fixed Rate** set to **Scene** and **Interpolation** on.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.setSettings", "parameters": { "section": "Scene.Timing", "reset": true } }
   ```

   :::
   ::::

   **You should see:** the least shake at 120 with Interpolation on, the most at 30 with it off, and the controls answering a little sooner at 120.

   **If you do not see it:** nothing differs. A screen of 60 frames a second and 60 steps agree: use 30 or 120 to see a difference.

:::::

::checkpoint{stage=6}

::figure{id=timing-felt}

## Give the camera an arm

A camera behind a player meets walls. A wall between the camera and the player hides the player, and a camera inside a wall shows the back of its mesh. The arm should shorten as a wall comes in, and grow again once the way is free.

Cast a ray, as [Physics for game makers](physics.md) did for the ground. It starts at the pivot and goes toward where the camera would be. If it hits something, the camera goes to the hit, a little in front. The call returns an optional hit: it holds a hit or it is empty, so you test it first. Its fifth argument is an entity to ignore, here the player.

Take the numbers. The pivot is 1.5 m above the feet and the arm is 6.5 m. The ray is as long as the arm plus a margin of 0.3 m: 6.8 m. A wall 4.0 m away is hit, so the free arm is $\max(0.4,\ 4.0 - 0.3) = 3.7$ m: the margin keeps the camera off the wall, and the floor of 0.4 m keeps it from crossing the pivot.

Then two speeds. A free arm shorter than the current arm is taken at once, so a wall never hides the player. A longer one is reached smoothly with $k$ = 6 per second: the arm covers $1 - e^{-6 \times 0.5} = 95\ \%$ of the gap in half a second. A view that jumps back the moment something passes is nervous, so in is fast and out is slow.

The mouse turns the camera around the pivot. A mouse move of 300 pixels at 0.12 degrees each turns the view by 36 degrees, and the `Look` action does the same with a stick, in degrees each second. The cursor is locked while the course plays: hidden and kept in the window, with the mouse movement still reported.

The first quote is the frame: look, follow the drawn pivot and place the camera.

```cpp src="book:tutorials/make/characters-cameras/step7/FollowCamera.cpp#L39-L56"
void OnLateUpdate(float deltaTime) override
{
	const glm::vec2 mouse = Input::GetMouseDelta();
	const glm::vec2 look = Input::GetActionValue("Gameplay/Look");
	Yaw -= mouse.x * MouseDegreesPerPixel + look.x * StickDegreesPerSecond * deltaTime;
	Pitch -= mouse.y * MouseDegreesPerPixel - look.y * StickDegreesPerSecond * deltaTime;
	Pitch = std::clamp(Pitch, MinPitch, MaxPitch);

	if (Target.IsValid())
	{
		const glm::vec3 pivot = Target.GetTransform().GetDrawnPosition() + glm::vec3(0.0f, PivotHeight, 0.0f);
		if (glm::length(pivot - m_Pivot) > 8.0f)
			m_Pivot = pivot; // A respawn: no slide across the course
		else
			m_Pivot = glm::mix(m_Pivot, pivot, 1.0f - std::exp(-FollowSharpness * deltaTime));
	}
	Place(deltaTime);
}
```

1. **Lines 41–44:** the mouse and the stick change yaw and pitch. A mouse move to the right turns the view to the right, so the yaw falls.
2. **Line 45:** the pitch stays between its limits.
3. **Line 49:** the pivot follows the drawn position, as before.
4. **Lines 50–51:** a move of more than 8 m, a return after a fall, is followed at once.

:::question
The quote below uses `std::optional` and `hit->Distance`. An optional holds a value or nothing; `->` reads a member through it. See [pointers and memory](../basics/cpp-memory.md) and [modern C++](../basics/cpp-modern.md).
:::

The second quote places the camera along its arm.

```cpp src="book:tutorials/make/characters-cameras/step7/FollowCamera.cpp#L60-L74"
void Place(float deltaTime)
{
	const glm::quat rotation = glm::angleAxis(glm::radians(Yaw), glm::vec3(0.0f, 1.0f, 0.0f)) * glm::angleAxis(glm::radians(Pitch), glm::vec3(1.0f, 0.0f, 0.0f));
	const glm::vec3 back = rotation * glm::vec3(0.0f, 0.0f, 1.0f);
	float free = Distance;
	if (const std::optional<RaycastHit> hit = Physics::Raycast(m_Pivot, back, Distance + WallMargin, Physics::c_AllLayers, Target))
		free = std::max(0.4f, hit->Distance - WallMargin);
	if (free <= m_ArmLength || deltaTime <= 0.0f)
		m_ArmLength = free; // In at once, so that a wall never hides the player
	else
		m_ArmLength += (free - m_ArmLength) * (1.0f - std::exp(-ArmReturnSharpness * deltaTime));
	TransformComponent transform = GetTransform();
	transform.SetWorldPosition(m_Pivot + back * m_ArmLength);
	transform.SetWorldRotation(rotation);
}
```

1. **Line 63:** the direction from the pivot to the camera.
2. **Lines 65–66:** the ray, with the player ignored. A hit shortens the free arm.
3. **Lines 67–68:** in at once, or at the first frame.
4. **Line 70:** out smoothly, with its own sharpness.

:::::steps

1. Replace the follow camera with the orbit and arm version.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace `Scripts/FollowCamera.cpp` with the code of this stage and press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the new fields `Yaw`, `Pitch` and `WallMargin` on the camera's script.

   **If you do not see it:** `Target` is empty after the build. Drag `Player` onto it again.

2. Orbit and meet the wall.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Play. Move the mouse to turn the view, then turn the camera toward the `Wall` behind the start.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "build": false } }
   ```

   :::
   ::::

   **You should see:** the view orbits the player, the camera comes in at once against the wall and goes out slowly when you turn away.

   **If you do not see it:** the camera passes through the wall. The wall needs its collider, which the ray reads.

:::::

::checkpoint{stage=7}

::figure{id=camera-arm}

## Ride a moving platform

A moving platform is a kinematic body: your code moves it, and it pushes whatever stands in its way. A character controller on top is carried: the controller reads the platform's velocity and adds it to its own walk, and it keeps that motion when it steps off. `GetGroundVelocity` and `GetGroundEntity` tell a script what it stands on.

The platform and its rider must move on the same clock. The controller moves in the fixed steps, so the platform moves in `OnFixedUpdate`. A platform moved in `OnUpdate`, once a frame, would be drawn at other times than its rider. Writing the transform of a kinematic body acts at the next fixed step, which suits it.

Take a platform that travels 6 m in a period of 8 s, there and back. Its position along the way is $6 \times (0.5 - 0.5\cos(2\pi t / 8))$, where $t$ is the time in seconds. At $t = 2$ s it is at 3 m, at 4 s at 6 m and at 6 s at 3 m again. Its top speed, in the middle, is $6\pi / 8 = 2.4$ m/s.

```cpp src="book:tutorials/make/characters-cameras/step8/MovingPlatform.cpp#L19-L26"
void OnFixedUpdate(float fixedDeltaTime) override
{
	if (Period <= 0.0f)
		return;
	m_Time += fixedDeltaTime; // Counting steps, never frames
	const float phase = 0.5f - 0.5f * std::cos(6.2831853f * m_Time / Period); // 0 to 1 and back
	GetTransform().SetWorldPosition(m_Start + Travel * phase);
}
```

The time is a sum of step lengths, never a count of frames, so the platform moves the same at every frame rate.

:::::steps

1. Add the platform's script.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy `Scripts/MovingPlatform.cpp` from the checkpoint, press **Ctrl+B** and add the script to `Platform`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<the Platform's ID>", "class": "MovingPlatform" } }
   ```

   :::
   ::::

   **You should see:** the fields `Travel` (6, 0, 0) and `Period` 8 on `Platform`.

   **If you do not see it:** the platform does not move. Its Rigid Body must have the type Kinematic.

2. Ride it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Play. Walk onto the platform at the back left of the course, stand still, then walk off.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "build": false } }
   ```

   :::
   ::::

   **You should see:** the player stands still on the platform and rides with it, without sliding or shaking.

   **If you do not see it:** the player slides back. The platform is not Kinematic, or something moves it in `OnUpdate`.

:::::

::checkpoint{stage=8}

::figure{id=platform-ride}

## Start again after a fall

The ground of the course ends, and a player who walks off its edge falls forever. When the player's height is below a limit, the script calls the controller's `Teleport` with the spawn point. It moves the feet and the entity at once, and the game draws the player where it lands. A fall of 8 m takes $\sqrt{2 \times 8 / 9.81} = 1.28$ s.

Never write the player's transform to move it: the controller owns the position, and `Teleport` is the move. The camera of the last section follows a jump of more than 8 m at once, so it does not slide across the course.

A second case is an entity that a script moves far by writing its transform in `OnFixedUpdate`, as the platform does. Strata would draw it sliding across the gap between the old and the new pose. `ResetInterpolation` on the transform draws the entity where it is until the next step. The platform has a `Loop` mode for it: it travels 6 m and jumps back to its start.

```cpp src="book:tutorials/make/characters-cameras/step9/MovingPlatform.cpp#L24-L32"
const float before = m_Time;
m_Time += fixedDeltaTime;
TransformComponent transform = GetTransform();
if (Loop)
{
	transform.SetWorldPosition(m_Start + Travel * (std::fmod(m_Time, Period) / Period));
	if (std::floor(m_Time / Period) > std::floor(before / Period))
		transform.ResetInterpolation(); // It jumped back: do not draw it sliding there
}
```

1. **Line 24:** the time before this step, to know when a trip ended.
2. **Line 29:** the position along the trip, from 0 to the full travel.
3. **Lines 30–31:** when the trip number grew, the platform jumped back: draw it where it is.

:::::steps

1. Replace the two scripts with the checkpoint's.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace `Scripts/PlayerController.cpp` and `Scripts/MovingPlatform.cpp` with the code of this stage and press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the field `FallHeight` of -8 on `Player` and the field `Loop` on `Platform`.

   **If you do not see it:** the fields are missing. Select the entities again after the build.

2. Walk off the edge.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Play. Walk off the edge of the ground and wait about a second.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "build": false } }
   ```

   :::
   ::::

   **You should see:** the player falls, then stands at its spawn point, and the camera is there at once.

   **If you do not see it:** the player falls forever. `FallHeight` must be below the ground.

3. Try the loop with and without the call.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Stop the game, turn `Loop` on for `Platform`, play and watch the platform at the end of its trip. Then delete the `ResetInterpolation` line, build and watch again.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setField", "entityName": "Platform", "parameters": { "class": "MovingPlatform", "field": "Loop", "value": true } }
   ```

   :::
   ::::

   **You should see:** with the call, the platform appears at its start; without it, it flies back across the course for one step.

   **If you do not see it:** one step is short. Set **Fixed Rate** to 30 to make it longer. If `script.setField` answers that the field is unknown, run `script.build` and the command again.

:::::

::checkpoint{stage=9}

::figure{id=respawn-path}

## Look from a second camera

A game is drawn from one camera: the first active entity, in the Hierarchy's order, whose Camera has Primary on. A script finds it with `Scene::GetPrimaryCamera()`. Strata draws no second view at once: no split screen, no picture in a picture, and no camera that draws into a texture for a mirror or a map.

To use another camera, clear Primary on the first and set it on the second, or switch the first one's entity off. `SetProperty("Camera", "Primary", false)` writes the flag. The change is a cut: the next frame is drawn from the other camera, with no blend.

The walking code reads the primary camera every frame, so the walk follows the new view. The top camera looks down by 70 degrees, so its flat forward still points up the course. A camera that looked straight down would have no flat forward, and the player would stand still: the guard of the walking section.

```cpp src="book:tutorials/make/characters-cameras/step10/CameraSwitch.cpp#L11-L21"
void OnUpdate(float) override
{
	if (!Input::IsKeyPressed(Key::C) || !Other.IsValid())
		return;
	// The game is drawn from the first active camera that is Primary: clear the flag on one, set it on the other.
	const bool viewingThis = Scene::GetPrimaryCamera() == GetEntity();
	Entity from = viewingThis ? GetEntity() : Other;
	Entity to = viewingThis ? Other : GetEntity();
	from.SetProperty("Camera", "Primary", false);
	to.SetProperty("Camera", "Primary", true);
}
```

1. **Line 13:** the press of **C**, and a camera to switch to.
2. **Line 16:** which camera is the game's now.
3. **Lines 19–20:** clear the flag on one camera and set it on the other.

:::::steps

1. Add the second camera.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **+ ▸ Empty**, name it `Top Camera`, add a Camera component with Primary off, and set its Translation to (0, 20, 6) and its Rotation to (-70, 0, 0).
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Top Camera", "components": { "Camera": { "Primary": false }, "Transform": { "Translation": [0, 20, 6], "Rotation": [-70, 0, 0] } } } }
   ```

   :::
   ::::

   **You should see:** a camera above the course in the Scene view, looking down.

   **If you do not see it:** two cameras with Primary on would use the first in the Hierarchy. Only `Main Camera` has it on.

2. Add the switch and try it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy `Scripts/CameraSwitch.cpp` from the checkpoint, press **Ctrl+B**, add it to `Main Camera` and drag `Top Camera` onto its field `Other`. Play and press **C** twice.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<the Main Camera's ID>", "class": "CameraSwitch", "fields": { "Other": "<the Top Camera's ID>" } } }
   ```

   :::
   ::::

   **You should see:** the view cuts to the view from above, and on the second press back behind the player.

   **If you do not see it:** nothing changes. The field `Other` is empty, or the Game view has no focus.

:::::

### Read the finished camera

The Third-Person sample has a camera that grew from yours, with a zoom, the game's settings and an attract mode. Read the two parts you wrote, in its form.

```cpp src="Samples/ThirdPerson/Scripts/FollowCamera.cpp#L71-L81"
if (Target.IsValid())
{
	// Where the player is drawn this frame: between its last two physics steps while the game interpolates.
	const glm::vec3 pivot = Target.GetTransform().GetDrawnPosition() + glm::vec3(0.0f, PivotHeight, 0.0f);
	// A respawn or a teleport moves the camera at once; walking is followed smoothly.
	if (glm::length(pivot - m_Pivot) > 8.0f)
		m_Pivot = pivot;
	else
		m_Pivot = glm::mix(m_Pivot, pivot, 1.0f - std::exp(-FollowSharpness * deltaTime));
}
Place(deltaTime);
```

1. **Line 74:** the drawn position again.
2. **Lines 76–79:** a return after a fall is followed at once, walking smoothly.

The sample reads `Time::GetUnscaledDeltaTime()` and stops turning when the :term[time scale]{id=time-scale} is 0, so a pause menu does not move the camera. The arm:

```cpp src="Samples/ThirdPerson/Scripts/FollowCamera.cpp#L85-L101"
void Place(float deltaTime)
{
	const glm::quat rotation = glm::angleAxis(glm::radians(Yaw), glm::vec3(0.0f, 1.0f, 0.0f)) * glm::angleAxis(glm::radians(Pitch), glm::vec3(1.0f, 0.0f, 0.0f));
	const glm::vec3 back = rotation * glm::vec3(0.0f, 0.0f, 1.0f);
	float free = Distance;
	if (const std::optional<RaycastHit> hit = Physics::Raycast(m_Pivot, back, Distance + WallMargin, Physics::c_AllLayers, Target))
		free = std::max(0.4f, hit->Distance - WallMargin);
	// In at once, so that a wall never hides the player; out smoothly once nothing is in the way, so that the view does not
	// jump back when something passed between them.
	if (free <= ArmLength || deltaTime <= 0.0f)
		ArmLength = free;
	else
		ArmLength += (free - ArmLength) * (1.0f - std::exp(-ArmReturnSharpness * deltaTime));
	TransformComponent transform = GetTransform();
	transform.SetWorldPosition(m_Pivot + back * ArmLength);
	transform.SetWorldRotation(rotation);
}
```

1. **Line 90:** the ray of your arm, with all layers and the player ignored.
2. **Lines 94–97:** in at once, out smoothly.

Camera moves and cuts are scripts: Strata has no film tool.

::checkpoint{stage=10}

::figure{id=top-camera}

## Summary

- A character is a character controller, not a rigid body: it walks, climbs steps and stops at slopes, and an entity has one of the two.
- A script walks the controller with `Move` relative to the primary camera, turns the body with the angle of the direction and jumps with `Jump`, allowed for a coyote time after the ground.
- A follow camera reads the drawn position in `OnLateUpdate`, because what moves in fixed steps is drawn between its last two steps.
- The camera's arm is shortened at once by a ray that ignores the player, let out smoothly, and turned by the mouse and the `Look` action.
- A platform moves in `OnFixedUpdate`, `Teleport` brings the player back, `ResetInterpolation` follows a far move, and the Primary flag switches cameras.

## Check yourself

1. A friend gives the player a rigid body as well as a character controller. What happens, and where do you see it?

   :::answer{tests="controller-not-body"}
   The entity is simulated as the rigid body and the controller does nothing. The Console warns that the entity has both. Remove one of them.
   :::

2. The camera looks along plus X and the player pushes the stick up. Which way does the player walk, and to what yaw does the body turn?

   :::answer{tests="walk-jump"}
   Forward is (1, 0, 0), so the player walks along plus X. The yaw is $\operatorname{atan2}(-1, 0) = -90$ degrees.
   :::

3. The player walks at 4 m/s off a ledge and coyote time is 0.25 s. How far past the edge can a jump still start?

   :::answer{tests="walk-jump"}
   $4 \times 0.25 = 1$ m of path, as long as the count of seconds in the air is at most 0.25.
   :::

4. A camera follows `GetWorldPosition()` at 30 steps a second and the player walks at 6 m/s. By how much does the position jump, and what do you change?

   :::answer{tests="drawn-camera"}
   The position jumps by $6 / 30 = 0.2$ m each step, and the frames between read the same value. Read `GetDrawnPosition()` in `OnLateUpdate`.
   :::

5. A ray from the pivot hits a wall at 3.0 m, the arm is 6.5 m and the margin is 0.3 m. What is the arm, and how does it come back?

   :::answer{tests="camera-arm"}
   The arm is $\max(0.4, 3.0 - 0.3) = 2.7$ m at once. It grows back smoothly toward 6.5 m once nothing is in the way.
   :::

6. Why does the platform move in `OnFixedUpdate`, and what does `ResetInterpolation` add?

   :::answer{tests="platform-cameras"}
   The rider moves in the fixed steps, so the platform must too, or they are drawn at different times. `ResetInterpolation` stops a far jump from being drawn as a slide.
   :::

## Exercises

1. **Basic.** Set `CoyoteSeconds` to 0.3 and find how far past the ledge a jump still starts at 5 m/s. Predict first.

   :::answer{tests="walk-jump"}
   $5 \times 0.3 = 1.5$ m. Walk off the `Ledge` and press **Space** late: a press within 0.3 s of the edge jumps, a later one does not.
   :::

2. **Medium.** Make a double jump: one more `Jump` in the air once the first is used, because `Jump` works off the ground too. Add an `ExtraJumps` field and count the jumps.

   :::answer[Worked solution]{tests="walk-jump" solution="tutorials/make/characters-cameras/exercise-2.tutorial.json"}
   Keep the extra jumps left, refill them when the player is grounded, and take one for each press outside the coyote window. The command file builds the script, jumps and presses **Space** again a quarter of a second later. It checks that the player rises to about 2.2 m instead of 1.3 m, and that a third press in the air does nothing.
   :::

3. **Hard.** The arm is 2.8 m short of its free length of 6.5 m. How long does it take to come within 0.1 m with `ArmReturnSharpness` 6, and with 12? Check by playing.

   :::answer{tests="camera-arm"}
   The gap falls as $e^{-kt}$, so it is 0.1 m when $2.8 e^{-kt} = 0.1$, that is $t = \ln(28)/k$. That is 0.56 s for $k$ = 6 and 0.28 s for $k$ = 12.
   :::

## Where it lives in Strata

- The character controller: `Strata/src/Strata/Physics/CharacterControllers.cpp`, with its fields in `Strata/src/Strata/Physics/PhysicsComponents.h`. How it moves inside belongs to the physics part.
- The script side: `StrataScriptCore/Include/StrataScript/CharacterController.h`, and the drawn pose in `StrataScriptCore/Include/StrataScript/Entity.h`.
- The primary camera: `Scene::GetPrimaryCameraEntity` in `Strata/src/Strata/Scene/Scene.cpp`.
- The finished camera: `Samples/ThirdPerson/Scripts/FollowCamera.cpp`.

## Further reading

- The engine's manual, section "Following moving things": the rule of this page in a few lines (beginner).
- The scripting skill's part on character controllers: every call of the controller (intermediate).
