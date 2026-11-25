---
id: make/gameplay-math
title: "The math of moving things: vectors, directions, angles and smoothing"
description: "Measure a distance, tell front from behind, turn toward a target, smooth a motion at any frame rate and aim through the cursor, with a turret and a ball."
kind: how-to
size: L
tracks: [G]
needs: [make/project-coin-run, make/transforms-units|basics/math-vectors]
time: 75
learn:
  - id: distance-direction
    text: compute the distance and the unit direction from one position to another
  - id: dot-product
    text: predict from a dot product whether a target is in front, behind, left or right
  - id: turn-toward
    text: compute the yaw that turns a thing toward a target, and explain why a glTF model needs the other sign
  - id: smooth-rate
    text: write a smoothing step that looks the same at 30 and 60 frames per second
  - id: pointer-ray
    text: build the ray through the cursor from the camera's forward, right and up and its field of view
since: 0.3.0
status: final
---

Every game moves things: a turret turns, a camera follows, a ball flies where you click. Under each of them sits a little arithmetic on positions and directions, and a few formulas serve for all. This page gives you those formulas as recipes, one at a time, on a small example, a turret that watches a ball. Each recipe is a line or two of C++, what it computes, when to use it and a step that shows the result. Before you start:

- A new project from the Basic 3D template, with its camera, sun, sky and ground, where the scripts build with **Ctrl+B** as in [Your first script](first-script.md). Make it with **New Project** in the launcher, as [A tour of the editor](editor-tour.md) made Coin Run, or with this command:

  ```json
  { "command": "project.create", "parameters": { "directory": "<a new folder>/GameplayMath", "name": "GameplayMath", "template": "basic3d" } }
  ```

  The page offers no download of its steps: each section adds to the scene and the script of the section before it.
- Positions and directions as three numbers, degrees and radians, and the rotation of an entity, from [Positions, rotations and units](transforms-units.md).
- A :term[script class]{id=script-class} with an `OnUpdate` function that receives the frame's `deltaTime`, from [the script loop](script-loop.md).

## What you will build

The scene holds a turret and a ball. The turret is a cylinder with a block on one side, its barrel. The ball circles round it, and the turret script reads where the ball is and reacts. Each section below adds a few lines to that script. Strata measures in metres, and an entity's forward is its -Z direction: a turret that is not turned points away from the default camera.

```mermaid caption="Each question a moving thing asks, and the recipe of this page that answers it." alt="A flow chart. A question about a target splits into six: how far, which way, in front or behind, how to turn toward it, how to follow it smoothly, and where the cursor points. Each leads to its recipe."
flowchart TD
    Q["A target at some position"] --> A["How far away is it?"]
    Q --> B["Which way is it?"]
    Q --> C["In front, behind, left or right?"]
    Q --> D["How do I turn toward it?"]
    Q --> E["How do I follow it smoothly?"]
    Q --> F["Where does the cursor point?"]
    A --> A2["length of the offset"]
    B --> B2["normalize the offset"]
    C --> C2["dot product with forward or right"]
    D --> D2["atan2 for the yaw, or LookAt"]
    E --> E2["mix with 1 - exp(-k dt), or SmoothDamp"]
    F --> F2["forward + right * x + up * y"]
```

## Place the turret and the ball

The turret stands at (-3, 0.5, 0). The ball circles the point (0, 0.5, 0) at a radius of 4 m. So the distance between them changes from 1 m to 7 m during one lap, and the ball passes in front of the turret and behind it.

:::::steps

1. Make the turret: a cylinder with a barrel as its child.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **+ ▸ Cylinder** in the Hierarchy, name it `Turret` and set its position to -3, 0.5, 0. Choose **+ ▸ Cube**, name it `Barrel`, and drag it onto `Turret` in the Hierarchy. Then set the position of `Barrel` to 0, 0.25, -0.8 and its scale to 0.2, 0.2, 1.
   :::
   :::tab[With a command]

   The first command makes the cylinder.

   ```json
   { "command": "entity.create", "parameters": { "name": "Turret", "components": { "MeshRenderer": { "Mesh": "Builtin/Cylinder" }, "Transform": { "Translation": [-3, 0.5, 0] } } } }
   ```

   The second makes the barrel, with the cylinder as its parent. A parent is named by its identifier (ID), the `id` that the first command answered, never by its name.

   ```json
   { "command": "entity.create", "parameters": { "name": "Barrel", "parent": "<id of Turret>", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "Transform": { "Translation": [0, 0.25, -0.8], "Scale": [0.2, 0.2, 1] } } } }
   ```

   :::
   ::::

   **You should see:** `Barrel` under `Turret` in the Hierarchy. The editor's camera looks at the turret from the front, so the barrel stands behind the cylinder: only a thin edge of it shows above the cylinder's top. Look from above, and a block sticks out of the far side of the cylinder, 0.8 m long. To look from above, hold the Alt key and drag with the left button in the Scene view until you look down on the turret, or run `{ "command": "camera.set", "parameters": { "position": [-3, 6, 2], "target": [-3, 0.5, 0] } }`.

   **If you do not see it:** from above, the barrel is inside the cylinder or on the near side. Check that its position Z is -0.8, not 0.8. A command that answers that `parent` must be an ID got the name `Turret`: give it the ID.

2. Make the ball and the script that moves it round the circle.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **+ ▸ Sphere** and name it `Ball`. Choose **Scripts ▸ New Script...**, create `Orbit`, and replace its text with the listing below, keeping the template's first line. Press **Ctrl+B**, then select `Ball` and choose **Add Component ▸ Script** with `Orbit`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Ball", "components": { "MeshRenderer": { "Mesh": "Builtin/Sphere" }, "Transform": { "Translation": [4, 0.5, 0] } } } }
   ```

   Run `script.create` with the class `Orbit`, replace the text of the file with the listing, then run `script.build` and `script.add` with the entity `Ball` and the class `Orbit`.

   :::
   ::::

   :::question
   The class below is derived from `Script`, and its function says `override`. What does that mean? See [classes and inheritance](../basics/cpp-classes.md).
   :::

   The listing keeps an angle in a member and moves the ball to the point of the circle at that angle: the cosine gives X and the sine gives Z.

   ```cpp src="book:tutorials/make/gameplay-math/Orbit.cpp#L3-L27"
   #include <cmath>

   using namespace Strata;

   // Moves the entity round a circle of the given radius, about the point (0, 0.5, 0).
   class Orbit : public Script
   {
   public:
   	float Radius = 4.0f;
   	float Speed = 0.5f; // Radians per second

   	void OnUpdate(float deltaTime) override
   	{
   		m_Angle += Speed * deltaTime;
   		GetTransform().SetTranslation(glm::vec3(std::cos(m_Angle) * Radius, 0.5f, std::sin(m_Angle) * Radius));
   	}
   private:
   	float m_Angle = 0.0f;
   };

   ST_SCRIPT_CLASS(Orbit)
   {
   	ST_SCRIPT_FIELD(Radius);
   	ST_SCRIPT_FIELD(Speed);
   }
   ```

   1. **Line 12:** `Speed` is in radians per second, so a lap of $2\pi$ radians takes about 12.6 s.
   2. **Line 16:** the angle grows by `Speed` times `deltaTime`, so it tracks the clock, not the frame count.
   3. **Line 17:** the point of a circle of radius $r$ at angle $a$ is $(r \cos a, r \sin a)$, here in X and Z.

   **You should see:** after **Ctrl+P**, the ball circles the turret's area and passes in front of the camera.

   **If you do not see it:** the ball stays at 4, 0.5, 0. The script is not attached, or the build failed: open **Scripts ▸ Show Problems**.

:::::

## Measure the distance

The first question a turret asks is how far the ball is. The **offset** from one position to another is the target's position minus your own: a vector that, laid from you, ends on the target. Its length is the distance, and `glm::length(offset)` computes it. Strata's positions are in metres, so the result is in metres.

By hand: with the ball at (0, 0.5, 4) and the turret at (-3, 0.5, 0), the offset is (3, 0, 4). Its length is $\sqrt{3^2 + 0^2 + 4^2} = \sqrt{25} = 5$ m. The same distance holds in any direction, which is the point: the length does not depend on where the offset points. It is never negative, and it is 0 only when the two positions coincide.

Use it for ranges: a turret that fires within 6 m, a pickup that opens at 1.5 m, a sound that fades with distance. The mathematics of vectors is in [Vectors](../basics/math-vectors.md).

:::::steps

1. Create the `Turret` script, attach it to `Turret`, and make it report the distance once a second.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ New Script...** and create `Turret`. Replace the `OnUpdate` function with the listing below, add `Entity Target;` before it and `private:` with `float m_Countdown = 0.0f;` after it, and add `ST_SCRIPT_FIELD(Target);` to the registration. Press **Ctrl+B**. Select `Turret`, choose **Add Component ▸ Script** with `Turret`, and set `Target` to `Ball`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "Turret", "fields": { "Target": "Entity" } } }
   ```

   Edit the file as the editor tab says, then run `script.build` and `script.add` with the entity `Turret`, the class `Turret` and `"fields": { "Target": "<id of Ball>" }`.

   :::
   ::::

   The listing takes the three positions, subtracts them, measures the offset and writes it to the Console once a second. Look at how the timer shrinks by `deltaTime` each frame.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-1.cpp#L13-L26"
   void OnUpdate(float deltaTime) override
   {
   	if (!Target)
   		return;
   	const glm::vec3 position = GetTransform().GetWorldPosition();
   	const glm::vec3 targetPosition = Target.GetTransform().GetWorldPosition();
   	const glm::vec3 offset = targetPosition - position;
   	const float distance = glm::length(offset);
   	m_Countdown -= deltaTime;
   	if (m_Countdown > 0.0f)
   		return;
   	m_Countdown = 1.0f;
   	Log::Info("The ball is ", distance, " metres away");
   }
   ```

   1. **Lines 15–16:** with the `Target` field empty there is no ball to measure, so the function ends at once.
   2. **Lines 21–24:** `m_Countdown` falls by `deltaTime` each frame, and only when it reaches 0 does the log line run and the timer start again at 1 s.

   **You should see:** after **Ctrl+P**, a line "The ball is 7 metres away" or close to it. The numbers fall for about six seconds toward 1 and then rise again.

   **If you do not see it:** no line appears. The `Target` field is empty, so the script returns at once: set it to `Ball`.

:::::

## Find a direction

The distance says how far, not which way. A **unit vector** is a vector of length 1, and `glm::normalize(offset)` divides the offset by its length to make one. With the offset (3, 0, 4) and length 5, the direction is (0.6, 0, 0.8). Its length is $\sqrt{0.36 + 0.64} = 1$.

A direction of length 1 is the common currency of movement: multiply it by a speed to move, by a distance to place something, and compare it with another direction. Its why is short: the offset mixes how far with which way, and normalizing keeps only the way.

:::caution
Never normalize a vector of length 0. The division is 0 by 0, so every component becomes `NaN` (not a number), and `NaN` spreads into every number computed from it. Measure the length first, and return when it is below a small limit such as 0.001.
:::

:::::steps

1. Add the guard and the direction after the line that measures the distance, as the listing shows.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit `Scripts/Turret.cpp`, press **Ctrl+B** and then **Ctrl+P**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   The new lines return when the ball is on the turret and otherwise make the unit direction. Change the log line to `Log::Info("Distance ", distance, ", direction ", direction.x, " ", direction.y, " ", direction.z);` so that it prints the direction too.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-2.cpp#L19-L23"
   const glm::vec3 offset = targetPosition - position;
   const float distance = glm::length(offset);
   if (distance < 0.001f) // The ball is on the turret: there is no direction
   	return;
   const glm::vec3 direction = glm::normalize(offset);
   ```

   **You should see:** at the start "Distance 7, direction 1 0 0": the ball is straight to the right, and the Y part is 0 because both stand at the same height.

   **If you do not see it:** the numbers differ slightly at the first line, because the ball has already moved a little. A direction of length far from 1 means the guard line was lost.

:::::

## Tell front from behind with the dot product

Is the ball in front of the turret or behind it, and on which side? The **dot product** of two vectors multiplies their parts in pairs and adds the results: $a \cdot b = a_x b_x + a_y b_y + a_z b_z$. For two unit vectors it is the cosine of the angle between them. So it is 1 when they point the same way, -1 when they point opposite ways, and 0 when they are square to each other. In code it is `glm::dot(a, b)`.

By hand: the ball is at (0, 0.5, 4), so the direction is (0.6, 0, 0.8). The turret's forward is (0, 0, -1), and the dot is $0.6 \cdot 0 + 0 \cdot 0 + 0.8 \cdot (-1) = -0.8$. It is negative, so the ball is behind. With the turret's right, (1, 0, 0), the dot is 0.6: the ball is on the right side.

At the limits: a ball straight ahead gives exactly 1, straight behind gives -1, and exactly beside gives 0. Both vectors must have length 1, or the answer is scaled by their lengths and no longer a cosine. The sign still tells the side.

Use it for a field of view: a guard sees you when `ahead > 0.8`, a cone of about 37 degrees on each side of its forward. The mathematics is in [Vectors](../basics/math-vectors.md).

:::::steps

1. Ask for the two dot products and log them.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit `Scripts/Turret.cpp` as the listing shows, press **Ctrl+B** and **Ctrl+P**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   The listing asks the transform for its forward and right directions and takes a dot product with each. Add its last two lines after the direction, and change the log line to `Log::Info("Ahead ", ahead, ", side ", side);`. The two directions come from the rotation of the entity, which a later section explains.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-3.cpp#L21-L25"
   if (distance < 0.001f) // The ball is on the turret: there is no direction
   	return;
   const glm::vec3 direction = glm::normalize(offset);
   const float ahead = glm::dot(direction, GetTransform().GetForward());
   const float side = glm::dot(direction, GetTransform().GetRight());
   ```

   **You should see:** at the start "Ahead 0, side 1". Then Ahead is negative for about six seconds, while the ball is nearer the camera than the turret, and positive for the next six.

   **If you do not see it:** Ahead and Side look swapped. You used the right where the code needs the forward, or the reverse.

:::::

## Turn toward the ball with atan2

To face the ball the turret must turn around the up axis by some angle. That angle is the **yaw**: the turn around the vertical axis, in radians. You find it from the direction with `std::atan2(y, x)`, which gives the angle of the point (x, y) from the x axis, in radians, between $-\pi$ and $\pi$, for every quadrant. A plain division y over x loses the sign of both, which is why `atan2` takes them apart.

For a yaw $\theta$, the forward of an entity is $(-\sin\theta, 0, -\cos\theta)$. The turret must face the direction $d$, so its forward must equal $d$, and the yaw is `atan2(-d.x, -d.z)`. By hand: for $d = (0.6, 0, 0.8)$ this is `atan2(-0.6, -0.8)`, which is -2.498 radians, or -143.13 degrees. Check: $-\sin(-143.13°) = 0.6$ and $-\cos(-143.13°) = 0.8$, as wanted.

The limits agree. A ball straight ahead, $d = (0, 0, -1)$, gives `atan2(0, 1) = 0`: no turn. A ball to the right, $d = (1, 0, 0)$, gives `atan2(-1, 0) = -90°`, and a turn of -90 degrees points the forward to +X.

`SetEulerAngles` takes radians in the order pitch, yaw, roll, so the call is `SetEulerAngles(glm::vec3(0.0f, yaw, 0.0f))`. The Inspector shows degrees, and [Positions, rotations and units](transforms-units.md) taught the conversion. Euler angles set the local rotation: the turret has no parent, so local and world agree.

:::why
Every entity in Strata faces -Z, so cameras and directional lights need no exception: a light shines along its forward. The cost is the models. A glTF model is made facing +Z, so a model that must face a direction $d$ turns by `atan2(d.x, d.z)`, the same formula without the two minus signs. For $d = (0.6, 0, 0.8)$ that is 36.87 degrees. Forget this and the model walks backwards.
:::

:::::steps

1. Turn the turret to the ball every frame.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit `Scripts/Turret.cpp` as the listing shows, press **Ctrl+B** and **Ctrl+P**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   Add the listing's last two lines after the direction, before the dot products: they make the yaw and set it, and the dot products then measure again. After the turn the ball must be dead ahead.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-4.cpp#L21-L25"
   if (distance < 0.001f) // The ball is on the turret: there is no direction
   	return;
   const glm::vec3 direction = glm::normalize(offset);
   const float yaw = std::atan2(-direction.x, -direction.z);
   GetTransform().SetEulerAngles(glm::vec3(0.0f, yaw, 0.0f));
   ```

   **You should see:** the barrel points at the ball all the time, and the log says "Ahead 1", with a side of 0 or a tiny rounding error such as "side -5.96046e-08". The Console writes such a small number with an exponent: `e-08` means times $10^{-8}$, so the number is -0.0000000596, which is 0 for every use.

   **If you do not see it:** the barrel points away from the ball. The two minus signs of the `atan2` line are missing.

:::::

## Forward, right and up

Each entity knows three directions: `GetForward()` is its -Z turned by its world rotation, `GetRight()` its +X and `GetUp()` its +Y. They are unit vectors, they stand square to each other, and they are what the dot products above used. They let a script say "ahead" without knowing the angles.

To walk along the ground, a script flattens the forward: it sets Y to 0 and normalizes. A character with the camera tilted up must not walk into the sky. The first-person controller of the Strata game guide does this in one script. The mouse and the stick change a yaw and a pitch, in degrees; the yaw turns the player, the pitch turns the camera, a child at eye height, and the pitch is clamped.

```cpp src=".claude/skills/strata-make-a-game/SKILL.md#L173-L183"
  		const glm::vec2 look = Input::GetActionValue("Gameplay/Look");   // +Y: pushed up looks up
  		Yaw -= Input::GetMouseDelta().x * MouseSensitivity + look.x * StickTurnSpeed * deltaTime;
  		Pitch = glm::clamp(Pitch - Input::GetMouseDelta().y * MouseSensitivity + look.y * StickTurnSpeed * deltaTime, -85.0f, 85.0f);
  		GetTransform().SetEulerAngles(glm::vec3(0.0f, glm::radians(Yaw), 0.0f));
  		if (Camera)
  			Camera.GetTransform().SetEulerAngles(glm::vec3(glm::radians(Pitch), 0.0f, 0.0f));

  		const glm::vec2 move = Input::GetActionValue("Gameplay/Move");   // +Y forward, at most 1 long
  		const glm::vec3 forward = GetTransform().GetForward(), right = GetTransform().GetRight();
  		CharacterController controller = GetEntity().GetCharacterController();
  		controller.Move((glm::normalize(glm::vec3(forward.x, 0.0f, forward.z)) * move.y + right * move.x) * Speed);
```

1. **Line 174:** the mouse's movement in pixels times a sensitivity, and the stick times its turn speed and `deltaTime`, change the yaw. The stick is a rate, so it needs `deltaTime`; the mouse delta is already per frame. The minus sign is there because a positive yaw turns left, and moving the mouse right must turn right.
2. **Line 175:** the pitch changes the same way, and `glm::clamp` keeps it between -85 and 85 degrees. At 90 the camera would look straight up and flip over.
3. **Lines 176–178:** the angles become radians with `glm::radians`; the entity gets the yaw and the camera gets the pitch.
4. **Lines 181–183:** the flat forward times the Move action's Y, plus the right times its X, times the speed, goes to the character controller. `CharacterController` is the subject of [Characters and cameras](characters-cameras.md); copy these lines until then.

The quote runs in one script. You need no step here: the next section puts the same two directions to work in a mover that follows a camera.

## Walk relative to the camera

In a third-person game the stick's "up" means away from the camera, not along the world's -Z. So the mover takes the camera's forward, flattens it, finds its right, and adds the two scaled by the stick. The right comes from a **cross product**: `glm::cross(a, b)` is a vector square to both, and `glm::cross(forward, up)` is the right of a forward. For the flat forward (0, 0, -1) and up (0, 1, 0), the parts are $(0 \cdot 0 - (-1) \cdot 1,\ (-1) \cdot 0 - 0 \cdot 0,\ 0 \cdot 1 - 0 \cdot 0) = (1, 0, 0)$.

```mermaid caption="How a stick push becomes a walk in a third-person game, and a turn of the body toward the walk." alt="A flow chart. The camera's forward is flattened and normalized; its right comes from a cross product with up. The stick's two values scale the two vectors, and their sum is the walk direction. The character moves along it and its body turns by an atan2 of that direction."
flowchart LR
    A["camera forward"] --> B["flatten and normalize"]
    B --> C["right = cross(forward, up)"]
    B --> D["direction = forward * y + right * x"]
    C --> D
    S["stick x and y"] --> D
    D --> E["controller moves along it"]
    D --> F["body yaw = atan2(x, z)"]
```

The body then turns to face where it walks. The model faces +Z, so the yaw is `atan2(direction.x, direction.z)`, the formula of the box above. The turn happens only while the direction is longer than 0.01, because with the stick released the direction is 0, `atan2(0, 0)` gives 0, and the body would snap to face +Z.

```cpp src=".claude/skills/strata-make-a-game/SKILL.md#L213-L223"
  		const glm::vec2 input = Input::GetActionValue("Gameplay/Move");   // +Y forward, at most 1 long
  		// The camera's forward and right, flattened onto the ground.
  		glm::vec3 forward = Camera ? Camera.GetTransform().GetForward() : glm::vec3(0.0f, 0.0f, -1.0f);
  		forward = glm::normalize(glm::vec3(forward.x, 0.0f, forward.z));
  		const glm::vec3 right = glm::cross(forward, glm::vec3(0.0f, 1.0f, 0.0f));
  		const glm::vec3 direction = forward * input.y + right * input.x;
  		CharacterController controller = GetEntity().GetCharacterController();
  		controller.Move(direction * Speed);
  		// Face the walking direction. glTF models face +Z: yaw = atan2(x, z) turns +Z onto it.
  		if (glm::length(direction) > 0.01f)
  			GetTransform().SetEulerAngles(glm::vec3(0.0f, std::atan2(direction.x, direction.z), 0.0f));
```

1. **Lines 215–216:** the camera's forward, flattened and normalized. If there is no camera, the world's -Z stands in.
2. **Line 217:** the right of that flat forward.
3. **Line 218:** the stick's Y scales the forward and its X scales the right. Both are unit vectors square to each other, so the result is never longer than the stick.
4. **Lines 222–223:** the guard, then the yaw set in radians for a +Z model.

## Look at a point

Often the angle itself is not needed, only the rotation that faces a point. The :term[SDK's]{id=sdk} `Motion::LookAt(from, to)` gives it: the rotation that turns forward (-Z) toward `to` and keeps +Y as close to up as it can. It tilts too, not only yaws, so it suits cameras and a turret on a slope. It returns no turn when the two points coincide, so it needs no guard.

Choose `atan2` when only the yaw matters, as for a character on the ground. Choose `LookAt` when the target may be above or below.

:::::steps

1. Replace the body of `OnUpdate` with the listing and play. Then, while the game plays, set the position Y of `Turret` to 3 in the Inspector.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit `Scripts/Turret.cpp`, press **Ctrl+B**, and play with **Ctrl+P**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   The listing sets the world rotation from the two positions. The sample has no log line any more.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-5.cpp#L15-L19"
   if (!Target)
   	return;
   const glm::vec3 position = GetTransform().GetWorldPosition();
   const glm::vec3 targetPosition = Target.GetTransform().GetWorldPosition();
   GetTransform().SetWorldRotation(Motion::LookAt(position, targetPosition));
   ```

   **You should see:** the turret faces the ball as before. At Y 3 the whole cylinder tilts down toward the ball.

   **If you do not see it:** nothing turns. The script ran before the build finished, or `Target` is empty.

:::::

## Smooth a motion at any frame rate

An aim that snaps to the ball looks mechanical, and a camera that snaps to a player is hard to watch, so you want a delay. The beginner's recipe moves a fixed fraction each frame: `aim = glm::mix(aim, target, 0.1f)`, where `glm::mix(a, b, w)` gives $a + (b - a) w$. It breaks on frame rate. After one second it leaves $0.9^{60} = 0.18\ \%$ of the gap at 60 frames per second and $0.9^{30} = 4.2\ \%$ at 30. The same code follows tightly on one machine and loosely on another.

The fix is to base the weight on time. Let $k$ be the sharpness, in 1/s. A fraction $e^{-k t}$ of the gap should remain after $t$ seconds, however the seconds divide into frames. So one frame of $dt$ seconds uses the weight $w = 1 - e^{-k\,dt}$. In code it is `1.0f - std::exp(-k * deltaTime)`.

By hand, with $k = 8$: at 60 frames per second $dt = 1/60$ and $w = 0.1248$. At 30 it is $dt = 1/30$ and $w = 0.2341$. Two frames at 60 leave $0.8752^2 = 0.7660$ of the gap, and one frame at 30 leaves $1 - 0.2341 = 0.7659$: the same. Check the limits: with $dt = 0$ the weight is 0 and nothing moves, and for a huge $dt$ it tends to 1, so the aim arrives and never overshoots. After $1/k$ seconds about 63 % of the gap is covered.

Strata's sample follow camera does exactly this, and it adds one more thing: a jump of more than 8 m, such as a teleport, moves the camera at once.

```cpp src="Samples/ThirdPerson/Scripts/FollowCamera.cpp#L75-L79"
// A respawn or a teleport moves the camera at once; walking is followed smoothly.
if (glm::length(pivot - m_Pivot) > 8.0f)
	m_Pivot = pivot;
else
	m_Pivot = glm::mix(m_Pivot, pivot, 1.0f - std::exp(-FollowSharpness * deltaTime));
```

The exponential and its mathematics are in [Numbers](../basics/numbers.md) and [Interpolation](../basics/math-interpolation.md).

:::::steps

1. Make the turret aim at a point that follows the ball with this weight.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit `Scripts/Turret.cpp` as the listing and the notes below say, press **Ctrl+B** and **Ctrl+P**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   Add the field `float Sharpness = 4.0f;` with its `ST_SCRIPT_FIELD` line, and the member `glm::vec3 m_Aim`. Give `m_Aim` the ball's position in an `OnCreate` function, so that the aim does not start at the origin. The lines below make the weight, move the aim and look at it.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-6.cpp#L22-L26"
   if (!Target)
   	return;
   const float weight = 1.0f - std::exp(-Sharpness * deltaTime);
   m_Aim = glm::mix(m_Aim, Target.GetTransform().GetWorldPosition(), weight);
   GetTransform().SetWorldRotation(Motion::LookAt(GetTransform().GetWorldPosition(), m_Aim));
   ```

   **You should see:** the barrel trails the ball and catches up on the straight parts. Set `Sharpness` to 20 and the barrel catches the ball almost at once; set it to 1 and it lags far behind.

   **If you do not see it:** the barrel never moves. The weight is 0 when `deltaTime` is 0, so check that the `deltaTime` parameter of `OnUpdate` is named and used.

:::::

## Smooth with a spring

The exponential follows at full speed at the first frame and slows as it arrives. Sometimes you want a start that is gentle too. `Motion::SmoothDamp(current, target, velocity, smoothTime, deltaTime)` moves like a critically damped spring: smoothly, without overshooting the target, and arriving in about `smoothTime` seconds. It has overloads for a `float`, a `glm::vec2` and a `glm::vec3`. A call with a `deltaTime` of 0 or less changes nothing, and an optional last argument limits the speed in units per second.

The spring has a state, its velocity, and the function updates it. So you keep the velocity in a member between frames, start it at 0, and pass it by reference each call. A velocity that you reset every frame stops the spring from working: it never builds up speed.

:::::steps

1. Replace the aim line with `SmoothDamp` and keep the velocity in a member.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit `Scripts/Turret.cpp`, press **Ctrl+B** and **Ctrl+P**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   Add the field `float SmoothTime = 0.4f;` and the member `glm::vec3 m_AimVelocity`. The call below takes the place of the weight and the `mix`.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-7.cpp#L22-L26"
   	if (!Target)
   		return;
   	m_Aim = Motion::SmoothDamp(m_Aim, Target.GetTransform().GetWorldPosition(), m_AimVelocity, SmoothTime, deltaTime);
   	GetTransform().SetWorldRotation(Motion::LookAt(GetTransform().GetWorldPosition(), m_Aim));
   }
   ```

   **You should see:** the barrel starts to move gently, trails the ball by about 0.4 s, and never swings past it.

   **If you do not see it:** the barrel moves in fits. The velocity is a :term[local variable]{id=local-variable} of the function, so it starts again at 0 in every frame.

:::::

## Smooth a turn

You can smooth a yaw the same way, but an angle has an edge: +180 degrees and -180 degrees are the same direction. If the turret's yaw is 170 degrees and the ball passes behind it, so that the target becomes -170, a plain `mix` runs through 0 and swings 340 degrees the long way. The fix is to turn the difference into the shortest one: `std::remainder(difference, full turn)` returns it between a half turn each way. With 360 degrees, `remainder(-340, 360)` is 20: the short way.

The loop is then: `wanted` is the `atan2` yaw, the difference is wrapped, and the yaw moves by the weight times the wrapped difference. A full turn in radians is $2\pi$, written `2.0f * glm::pi<float>()`. The sample's follow camera wraps in degrees with 360 instead.

There is a second way that needs no wrap. Smooth the rotation itself: `glm::slerp(current, wanted, weight)`, where `wanted` is what `Motion::LookAt` gave. It blends two rotations along the shorter arc, and it handles pitch too. Use the yaw form for a turret on the ground, and the `slerp` form when the aim tilts.

:::::steps

1. Replace the aim code with a smoothed yaw.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit `Scripts/Turret.cpp`. Add `#include <glm/gtc/constants.hpp>`, the field `float Sharpness = 4.0f;` and the member `float m_Yaw = 0.0f;`. Press **Ctrl+B** and **Ctrl+P**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   The listing measures the offset again, wraps the difference between the wanted yaw and the current one, and moves a share of it. The weight is the frame-rate-independent one.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-8.cpp#L19-L25"
   const glm::vec3 offset = Target.GetTransform().GetWorldPosition() - GetTransform().GetWorldPosition();
   if (glm::length(offset) < 0.001f)
   	return;
   const float wanted = std::atan2(-offset.x, -offset.z);
   const float weight = 1.0f - std::exp(-Sharpness * deltaTime);
   m_Yaw += std::remainder(wanted - m_Yaw, 2.0f * glm::pi<float>()) * weight;
   GetTransform().SetEulerAngles(glm::vec3(0.0f, m_Yaw, 0.0f));
   ```

   **You should see:** the barrel turns smoothly, and when the ball passes behind it, it takes the short way without a full spin.

   **If you do not see it:** it spins the long way once per lap. The `std::remainder` call is missing, or it uses degrees where the angles are radians.

:::::

## Aim through the cursor

A click on the screen is a pixel, and the game needs a direction in the world. The idea: the screen is a window onto the world. Put an imaginary window one metre in front of the camera. The cursor is a point on that window, and the direction goes from the camera through the point.

Three steps give the point. First, the pixel becomes a number from -1 to 1 across the view: $2 m_x / w - 1$ for $x$, and $1 - 2 m_y / h$ for $y$, flipped because pixel rows grow downward. Here $m$ is the cursor in pixels and $w$, $h$ are the view's width and height in pixels. Second, the window's half height at one metre is $\tan(f/2)$ for a vertical field of view $f$, and its half width is that times the aspect, $w / h$. Third, the point is `forward + right * x + up * y`, with the scaled numbers, and normalizing it makes the direction.

By hand: the view is 1280 by 720 pixels, $f = 60°$, so $\tan 30° = 0.5774$ and the aspect is 1.7778. The cursor at (960, 180) gives the numbers 0.5 and 0.5. Then $x = 0.5 \cdot 0.5774 \cdot 1.7778 = 0.5132$ and $y = 0.5 \cdot 0.5774 = 0.2887$. For a camera that looks along -Z, the vector is (0.5132, 0.2887, -1), its length is 1.1605, and the direction is (0.442, 0.249, -0.862). At the limits: a cursor in the middle gives 0 and 0, so the direction is the camera's forward.

```mermaid caption="How the cursor's pixel becomes a direction in the world." alt="A flow chart. The mouse position and the view size give two numbers between minus one and one. The field of view and the aspect scale them. The camera's right and up, scaled by them and added to its forward, give a vector that is normalized into the direction of the ray."
flowchart LR
    M["mouse pixels and view size"] --> N["two numbers from -1 to 1"]
    N --> S["scale by tan(fov / 2) and the aspect"]
    S --> P["forward + right * x + up * y"]
    P --> D["normalize: the ray's direction"]
```

The Physics Playground sample builds the ray exactly so. It asks the camera for its three directions. It reads the size of the view in pixels with `Game::GetWindowSize()` and the cursor with `Input::GetMousePosition()`, which counts pixels from the top left of the game view. The field of view comes by name from the camera, in degrees.

```cpp src="Samples/PhysicsPlayground/Scripts/Playground.cpp#L193-L205" from="const glm::uvec2 window" to="outDirection = glm::normalize(forward + right * x + up * y);" symbol="Playground::GetPointerRay"
const glm::uvec2 window = Game::GetWindowSize();
const glm::vec2 mouse = Input::GetMousePosition();
if (window.x == 0 || window.y == 0 || mouse.x < 0.0f || mouse.y < 0.0f)
{
	outDirection = forward;
	return true;
}
// The cursor's place on the camera's image plane (vertical field of view in degrees).
const float fov = glm::radians(camera.GetProperty<float>("Camera", "PerspectiveFOV").value_or(45.0f));
const float aspect = static_cast<float>(window.x) / static_cast<float>(window.y);
const float x = (2.0f * mouse.x / static_cast<float>(window.x) - 1.0f) * std::tan(fov * 0.5f) * aspect;
const float y = (1.0f - 2.0f * mouse.y / static_cast<float>(window.y)) * std::tan(fov * 0.5f);
outDirection = glm::normalize(forward + right * x + up * y);
```

1. **Lines 193–194:** the size of the view and the cursor's place in it.
2. **Lines 195–199:** with a view of 0 pixels, or a cursor left of or above the view, the ray is the camera's forward.
3. **Line 201:** the field of view in degrees becomes radians; `value_or(45.0f)` is the number to use if the property is missing.
4. **Lines 203–204:** the cursor's place on the window one metre away, with the sign flip for $y$.
5. **Line 205:** the point, normalized.

The sample's camera is the `Scene::GetPrimaryCamera()` of the scene. A ray alone shows nothing: to learn what it hits, give its origin and direction to `Physics::Raycast`, which [Physics for game makers](physics.md) uses for the ground check. Here you do the geometry yourself, so that you see it work: the turret aims at the point where the ray meets the ground.

The ground is the plane $y = 0$. From the camera at height $h_0$ and a direction $d$ that goes down, the ray reaches it after the length $-h_0 / d_y$: with $h_0 = 2$ and $d_y = -0.5$ that is 4 units of the direction, since $2 - 0.5 \cdot 4 = 0$.

:::::steps

1. Replace the whole `Turret` script with one that aims at the cursor.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace the class with the listing, add the second listing, the `GetPointerRay` function, after `OnUpdate`, and keep the registration without fields. Press **Ctrl+B**. Select `Turret`, click the **X** in the header of its `Turret` entry, and add `Turret` again with **Add Script...**. Press **Ctrl+P**, and move the cursor over the Game view.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "script.remove", "parameters": { "entity": "<id of Turret>", "class": "Turret" } }
   { "command": "script.add", "parameters": { "entity": "<id of Turret>", "class": "Turret" } }
   ```

   :::
   ::::

   The scene still stores the value of `Target`, a field the new class no longer has. Removing the script and adding it again clears the stored value. Without that, each play writes the warning `script 'Turret' has no field 'Target'; the stored value is ignored` to the Console. The warning does no harm: the value is not used.

   The listing asks for the ray, returns when the ray goes up, and aims at the point where it meets the ground. The second listing, after it, builds the ray.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-9.cpp#L11-L20"
   void OnUpdate(float) override
   {
   	glm::vec3 origin, direction;
   	if (!GetPointerRay(origin, direction) || direction.y > -0.001f)
   		return; // No camera, or the ray never reaches the ground
   	const float rayLength = -origin.y / direction.y;
   	const glm::vec3 hit = origin + direction * rayLength;
   	const glm::vec3 position = GetTransform().GetWorldPosition();
   	GetTransform().SetWorldRotation(Motion::LookAt(position, glm::vec3(hit.x, position.y, hit.z)));
   }
   ```

   1. **Line 14:** no camera, or a ray that points up or flat, ends the frame.
   2. **Line 16:** the length along the ray to the ground.
   3. **Line 19:** the target keeps the turret's own height, so the barrel stays level.

   The second listing is the sample's function, made shorter: it gives no ray without a camera or a view, and it returns the camera's position as the origin.

   ```cpp src="book:tutorials/make/gameplay-math/Turret-9.cpp#L22-L38"
   // The ray from the camera through the cursor, in the world.
   bool GetPointerRay(glm::vec3& outOrigin, glm::vec3& outDirection) const
   {
   	Entity camera = Scene::GetPrimaryCamera();
   	const glm::uvec2 window = Game::GetWindowSize();
   	const glm::vec2 mouse = Input::GetMousePosition();
   	if (!camera || window.x == 0 || window.y == 0)
   		return false;
   	TransformComponent transform = camera.GetTransform();
   	const float fov = glm::radians(camera.GetProperty<float>("Camera", "PerspectiveFOV").value_or(60.0f));
   	const float aspect = static_cast<float>(window.x) / static_cast<float>(window.y);
   	const float x = (2.0f * mouse.x / static_cast<float>(window.x) - 1.0f) * std::tan(fov * 0.5f) * aspect;
   	const float y = (1.0f - 2.0f * mouse.y / static_cast<float>(window.y)) * std::tan(fov * 0.5f);
   	outOrigin = transform.GetWorldPosition();
   	outDirection = glm::normalize(transform.GetForward() + transform.GetRight() * x + transform.GetUp() * y);
   	return true;
   }
   ```

   1. **Lines 25–29:** the camera, the view size and the cursor; without a camera or a view there is no ray.
   2. **Lines 35–36:** the origin is the camera's position, and the direction is the point on the window, normalized.

   **You should see:** the barrel follows the cursor over the ground.

   **If you do not see it:** the barrel points away from the cursor, or beside it. Check that the cursor is over the Game view, and that the camera's **Perspective FOV** is the number the script reads. The ray divides the cursor by the view size, so on a scaled display check that the barrel lands under the cursor.

:::::

## Result

You now have a turret script that measures how far a ball is, finds its direction and tells front from behind. It turns toward the ball with `atan2` or `Motion::LookAt`, follows it smoothly at any frame rate with an exponential weight or a spring, and aims at the cursor. Each of these is a few lines you can copy into a game of your own, and each depends only on positions, directions and `deltaTime`.

## Variations

The same goals under other conditions:

- **Aim with the stick, not the cursor.** The project's Look action gives a vector of two numbers from -1 to 1. The sample's follow camera changes its yaw by the stick's X times a turn speed times `deltaTime`. The stick is a turn rate, so it needs `deltaTime`; the mouse delta is a distance, so it does not. Apply it to the turret's yaw and the target is no longer needed.
- **A turret that turns at a limited speed.** The exponential weight turns fast when the angle is large. To cap it, wrap the difference as before, then clamp it to the most the turret may turn in this frame: `maxStep = TurnSpeed * deltaTime`. The turret then turns at a steady rate until it faces the target.
- **A model that faces +Z.** Use `atan2(d.x, d.z)`, without the minus signs, as in the third-person mover.

## Summary

- You compute the distance with `glm::length` of the offset, and the direction with `glm::normalize`, after a guard against the zero vector.
- A dot product of two unit vectors is 1 ahead, -1 behind and 0 beside, so the dot with the forward and the right tells where a target is.
- The yaw for -Z forward is `atan2(-d.x, -d.z)`, in radians, and a glTF model uses `atan2(d.x, d.z)` because it faces +Z.
- Smoothing with the weight `1 - exp(-k * deltaTime)` leaves the same share of the gap after the same time at any frame rate; `Motion::SmoothDamp` is the spring form.
- The ray through the cursor is `forward + right * x + up * y`, with $x$ and $y$ from the cursor, the aspect and the `tan` of half the field of view, normalized.

## Check yourself

1. The ball is at (6, 0, 0) and the turret at (2, 0, 3). How far is it, and in which direction?

   :::answer{tests="distance-direction"}
   The offset is (4, 0, -3), its length is $\sqrt{16 + 9} = 5$ m, and the direction is (0.8, 0, -0.6).
   :::

2. Why must a script never call `glm::normalize` on the offset without a check, and what check is enough?

   :::answer{tests="distance-direction"}
   When the two positions coincide, the offset is 0 and the division gives `NaN`, which spreads into every later number. Measure the length first and return when it is below a small limit such as 0.001.
   :::

3. A dot product of the unit direction to a guard's target with the guard's forward is -0.3. Where is the target? What if the direction was not of length 1?

   :::answer{tests="dot-product"}
   Behind the guard, at about 107 degrees from the forward. With a longer vector the sign is still right, but the number is no longer a cosine, so a limit such as 0.8 would not mean the same.
   :::

4. An entity with forward -Z must face (0, 0, 1). What yaw does it need, and what yaw does a glTF model need?

   :::answer{tests="turn-toward"}
   The entity needs `atan2(-0, -1)`, which is 180 or -180 degrees ($\pi$ or $-\pi$ radians, by the sign of the zero): the same direction. The glTF model already faces +Z, and `atan2(0, 1)` is 0: no turn.
   :::

5. With $k = 8$ and 20 frames per second, what weight does the smoothing use?

   :::answer{tests="smooth-rate"}
   Here $dt = 0.05$, so $w = 1 - e^{-0.4} = 1 - 0.6703 = 0.3297$: about a third of the gap each frame.
   :::

6. Where does the ray go when the cursor is at the middle of the view, and at its top left corner?

   :::answer{tests="pointer-ray"}
   In the middle both numbers are 0, so the direction is the camera's forward. At the top left they are -1 and 1, so the ray leans left and up by the full half width and half height of the window.
   :::

## Exercises

1. **Basic.** The turret is at (2, 0, -1) and the target at (-2, 0, -4). Compute the distance, the direction, the two dot products with the forward and the right of a turret that has not turned, and the yaw of the turret and of a glTF model.

   :::answer{tests="distance-direction dot-product turn-toward"}
   The offset is (-4, 0, -3): distance 5, direction (-0.8, 0, -0.6). The dot with the forward (0, 0, -1) is 0.6, so the target is ahead, and with the right (1, 0, 0) it is -0.8, so it is on the left. The turret's yaw is `atan2(0.8, 0.6)` = 53.13 degrees, and a glTF model's is `atan2(-0.8, -0.6)` = -126.87 degrees.
   :::

2. **Medium.** Give the turret of the yaw step a field `TurnSpeed` in degrees per second and make it turn no faster. Predict how long a half turn takes at 90.

   :::answer{tests="smooth-rate turn-toward"}
   Wrap the difference with `std::remainder`, then clamp it to plus or minus `glm::radians(TurnSpeed) * deltaTime` before you add it to `m_Yaw`. A half turn of 180 degrees at 90 degrees per second takes 2 s.
   :::

3. **Hard.** Shoot balls through the cursor along the ray, count the balls that land in a goal trigger, and let the balls pass a glass wall on a Ghost layer. Use a new Basic 3D project.

   Make a `Shot` ball :term[prefab]{id=prefab-make}, a `Goal` trigger and a `GlassWall`, name two layers `Shot` and `Ghost` in **File ▸ Project Settings... ▸ Physics ▸ Collision Layers**, and clear the pair of the two. Write a `Shooter` script that spawns a ball on a left click and gives it its speed along the ray, and a `GoalCounter` for the goal. The sounds of the impacts, with a budget, are the exercise of [Recipes](recipes.md).

   :::answer[Worked solution]{tests="pointer-ray distance-direction" solution="tutorials/make/gameplay-math/exercise-3.tutorial.json"}
   The download holds the two scripts and `stage-1.commands.json`, the steps of the solution as a command script. To run it, make a new Basic 3D project, copy the download's `Scripts` files into the project's `Scripts` folder, and run the file from the project's folder with the editor's `--commands` option. On Windows the line is `& "C:\Strata\StrataEditor.exe" --project . --commands stage-1.commands.json --quit-after-commands --no-gpu | Write-Output`, with your Strata folder in place of `C:\Strata`. [Automated play-tests](automated-playtests.md) teaches command scripts and gives the line for each system. The editor ends with the exit code 0 when every step passed.

   The command file creates the layers, the prefab, the goal, the wall and the two scripts. The `Shooter` takes the pointer ray as in the aiming step and creates the prefab at the camera plus 1.5 m along the ray. The speed is the ray's direction times 14 m/s.

   A ball made by `Scene::Instantiate` has its physics body only from the next :term[fixed step]{id=fixed-step}. A call of `SetLinearVelocity` in the same update fails, and the Console says "'Shot' has no body in the physics simulation", and the ball drops. So the script keeps the new ball in a member and offers the speed in `OnFixedUpdate` until the call succeeds, as the Physics Playground does.

   ```cpp src="book:tutorials/make/gameplay-math/Shooter.cpp#L16-L28"
   void OnUpdate(float) override
   {
   	glm::vec3 origin, direction;
   	if (Input::IsMouseButtonPressed(Mouse::ButtonLeft) && Assets::IsLoaded(Prefab) && GetPointerRay(origin, direction))
   		Shoot(origin, direction);
   }

   void OnFixedUpdate(float) override
   {
   	// A new ball has its body from the next fixed step: offer the speed until the call succeeds.
   	if (m_Shot && m_Shot.GetRigidBody().SetLinearVelocity(m_Velocity))
   		m_Shot = Entity();
   }
   ```

   1. **Line 19:** a click shoots only when the prefab is loaded and the pointer ray exists.
   2. **Lines 25–27:** the call returns true once the body exists, and then the member is emptied.

   The spawn itself gives the ball its place, a turn of none and a scale of 0.3.

   ```cpp src="book:tutorials/make/gameplay-math/Shooter.cpp#L30-L37"
   void Shoot(const glm::vec3& origin, const glm::vec3& direction)
   {
   	Entity ball = Scene::Instantiate(Prefab, origin + direction * 1.5f, glm::quat(1.0f, 0.0f, 0.0f, 0.0f), glm::vec3(0.3f));
   	if (!ball)
   		return;
   	m_Shot = ball;
   	m_Velocity = direction * Speed;
   }
   ```

   The goal counts a ball that enters, logs the number and removes the ball. The glass wall's layer, `Ghost`, does not collide with `Shot`, so the ball passes through it and reaches the goal.
   :::

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/Entity.h`: `TransformComponent`, with the Euler angles in radians, the :term[world position]{id=world-position} and rotation, and `GetForward`, `GetRight` and `GetUp`.
- `StrataScriptCore/Include/StrataScript/Gameplay.h`: the `Motion` helpers, `LookAt` and `SmoothDamp`.
- `StrataScriptCore/Include/StrataScript/Input.h`: `Input::GetMousePosition` and `Input::GetMouseDelta`.
- `StrataScriptCore/Include/StrataScript/Game.h`: `Game::GetWindowSize`.
- `Samples/ThirdPerson/Scripts/FollowCamera.cpp`: the smoothing weight and the wrapped yaw.
- `Samples/PhysicsPlayground/Scripts/Playground.cpp`: `GetPointerRay`, and the shot that waits for its body.

## Further reading

- [Vectors](../basics/math-vectors.md), [Rotations](../basics/math-rotations.md), [Projection](../basics/math-projection.md) and [Interpolation](../basics/math-interpolation.md): the mathematics behind each recipe (beginner to intermediate).
- The GLM manual, which lists `length`, `normalize`, `dot`, `cross`, `mix` and `slerp` (intermediate).
