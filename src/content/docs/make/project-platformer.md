---
id: make/project-platformer
title: "Project: a third-person platformer"
description: "Build a small Sky Islands game: a robot that runs and jumps over floating islands, coins, jump pads, a moving platform, menus and a pruned export."
kind: tutorial
size: XL
tracks: [G]
needs: [make/designing-a-game, make/animation, make/levels-saves, make/commands]
time: 420
learn:
  - id: player-controls
    text: build a character controller that walks where the camera looks, turns toward its walk, jumps with a short coyote time and returns when it falls
  - id: animator-driven
    text: set an animator's parameters from the movement of a character and play footsteps from its events
  - id: one-state
    text: write one script that coins, jump pads and the goal report to, and keep a best time in a save file
  - id: scene-fields
    text: explain why a game passes scenes as asset fields and carries state between scenes only in save files
  - id: ship-pruned
    text: export the game pruned with a loading scene and run it from its folder
since: 0.5.0
status: final
---

## What you will make

You build a small version of Sky Islands, the game of the Third-Person Adventure sample. A robot runs and jumps over floating islands, bounces on jump pads, collects coins, rides a moving platform and races for the best time to a flag. The game has a main menu, a pause menu and a loading screen, and you export it as a folder that runs without the editor.

::figure{id=result}

## The plan

[Designing a game](designing-a-game.md) taught you to write one paragraph and a list of what you omit. Here they are for this game.

The design: you play a robot on four floating islands. You run, jump over gaps, bounce on a jump pad to the highest island, ride a moving platform across a wide gap, collect eight coins and touch the flag at the end. The clock runs from the start, and the best time is kept between runs. A main menu opens the game, a pause menu stops it, and a loading screen shows while the game starts.

The :term[cut list]{id=cut-list}: lanterns with shadows, reflection probes, the sky's own sun and the settings screen. Also cut are the crate that the player pushes into a pit and the mode in which the game plays itself when nobody touches the menu. Each belongs to a later page, and two come back as exercises.

The game is a few entities that each know one thing. The diagram shows who talks to whom. Read the arrows as "reports to" or "reads from".

```mermaid caption="The entities of the course and the scripts on them: the coins, the pads and the goal report to the game's state, and the camera and the player read each other." alt="Boxes show the player with a controller and a script, and the robot below it with an animation component and a script. Further boxes show the camera, an entity for the game's state with two scripts, and groups for the coins, the pads, the goal and the platform. Arrows run from the coins and the goal to that entity, from the pads to the player, and between the camera and the player."
flowchart LR
	Player["Player: Character Controller, ThirdPersonPlayer"] --> Robot["Robot: Animator, Footsteps"]
	Camera["Camera: FollowCamera"] -->|"follows"| Player
	Player -->|"walks where it looks"| Camera
	Coins["Coins: Coin"] -->|"AddCoin"| Game["Game: CourseState, PauseMenu"]
	Goal["Goal: Goal"] -->|"Complete"| Game
	Pads["Jump pads: JumpPad"] -->|"Launch"| Player
	Platform["Platform: MovingPlatform"] -.->|"carries"| Player
```

The next sections build it in nine stages. Each stage ends with a checkpoint: a project state you can download if you lose your way.

## What you need

- A new project named `Platformer` from the Basic 3D template. Create it in the launcher. [Project files](project-files.md) shows how.
- A copy of the sample beside it: press **Open Sample...** in the launcher and choose Third-Person Adventure. Compare with it whenever your game looks different.
- The checkpoint downloads, each a whole project named `ProjectPlatformer`. A stage copies its script files from the folder `Scripts` of the download at the end of its section.
- Files to import, all from the release's `Samples/ThirdPerson/Assets/` folder. The robot `Models/Robot/RobotExpressive.glb`. The models `block-grass-large-tall.glb`, `coin-gold.glb`, `spring.glb`, `flag.glb` and `platform.glb` of `Models/Platformer/`. The sounds `Jump.ogg`, `Land.ogg`, `Coin.ogg`, `Bounce.ogg` and `Complete.ogg` of `Sounds/`, and `Grass1.ogg` to `Grass4.ogg` of `Sounds/Footsteps/`.
- The robot, the kit and the sounds are in the public domain under Creative Commons Zero (:term[CC0]{id=cc0}). The sample's `CREDITS.md` names their authors, and you copy it in the first stage.
- About seven hours, in several sittings. Every stage ends in a state that you can leave and return to.

## Import the assets and start the project

Before you build, you bring in what the game is made of. Importing is a skill of [Assets](assets.md); this stage only applies it, to files that you then keep in tidy folders.

:::::steps

1. Create the project and open the course scene under its own name. Make it the :term[start scene]{id=start-scene} for now, so that the editor opens it when you come back; stage 8 changes it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the launcher choose **New Project**, pick the Basic 3D template and name it `Platformer`. When the editor opens, choose **File ▸ Save Scene As...** and type `Scenes/Course.stscene`. Then choose **File ▸ Set as Start Scene**.
   :::
   :::tab[With a command]
   Create the project in a folder you choose. Then save the template's scene under the new name and make it the start scene.

   ```json
   { "command": "project.create", "parameters": { "directory": "<a folder>", "name": "Platformer", "template": "basic3d" } }
   { "command": "scene.saveAs", "parameters": { "path": "Scenes/Course.stscene" } }
   { "command": "project.setStartScene", "parameters": { "scene": "Scenes/Course.stscene" } }
   ```

   :::
   ::::

   **You should see:** the template's camera, sun, sky, ground and post process in the Hierarchy, and `Course` in the title of the Scene view.

   **If you do not see it:** the editor shows the welcome window. The project did not open: choose **File ▸ Open Project...** and pick its folder.

2. Import the robot, the five kit models and the sounds listed under What you need.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag the files from your file manager into the Content Browser, into the folders `Models/Robot`, `Models/Platformer`, `Sounds` and `Sounds/Footsteps`. Wait until the import bar of the editor is empty.
   :::
   :::tab[With a command]
   One command for each folder of the project's assets, the `directory`. Write the release's folder `Samples/ThirdPerson/Assets` in full where `<A>` stands.

   ```json
   { "command": "asset.import", "parameters": { "file": "<A>/Models/Robot/RobotExpressive.glb", "directory": "Models/Robot" } }
   { "command": "asset.import", "parameters": { "files": [ "<A>/Models/Platformer/block-grass-large-tall.glb", "<A>/Models/Platformer/coin-gold.glb", "<A>/Models/Platformer/spring.glb", "<A>/Models/Platformer/flag.glb", "<A>/Models/Platformer/platform.glb" ], "directory": "Models/Platformer" } }
   { "command": "asset.import", "parameters": { "files": [ "<A>/Sounds/Jump.ogg", "<A>/Sounds/Land.ogg", "<A>/Sounds/Coin.ogg", "<A>/Sounds/Bounce.ogg", "<A>/Sounds/Complete.ogg" ], "directory": "Sounds" } }
   { "command": "asset.import", "parameters": { "files": [ "<A>/Sounds/Footsteps/Grass1.ogg", "<A>/Sounds/Footsteps/Grass2.ogg", "<A>/Sounds/Footsteps/Grass3.ogg", "<A>/Sounds/Footsteps/Grass4.ogg" ], "directory": "Sounds/Footsteps" } }
   ```

   :::
   ::::

   **You should see:** each model with an arrow beside it that opens its parts, and each sound with a waveform. A kit model that reads a texture lands with it in a folder of its own name, such as `Models/Platformer/coin-gold/coin-gold.glb`.

   **If you do not see it:** a file shows an error badge. Open the Console: the message names the file. A model that is not a glTF file, or a sound in a format the engine does not read, cannot be imported.

3. Copy `CREDITS.md` of the release's folder `Samples/ThirdPerson` into the project's folder, next to the file with the extension `.stproj`. Your copy of the sample holds the same file.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Use your file manager. The project's folder is the one you chose in the launcher.
   :::
   :::tab[With a command]
   This step has no menu or button: copy the file with your file manager or a terminal command.
   :::
   ::::

   **You should see:** the file `CREDITS.md` beside `Platformer.stproj`, with the robot, the kit and the sounds named.

   **If you do not see it:** the file sits inside the `Assets` folder. Move it out: it is a note for people, not an asset.

:::::

::checkpoint{stage=1}

::figure{id=s1-assets}

## Lay out the course

The course is a set of islands: blocks of grass floating in the sky, with gaps between them. A player falls through a gap, so every gap is a jump that you design. This section gives you the numbers for the layout.

The block of the kit is 2 m wide at its own size. You place it at twice its size, so one block is 4 m wide and the blocks sit on a grid of 4 m. A block at x = 0 and the next at x = 4 touch, and a missing block leaves a gap of 4 m. The block's origin is at its base, and at twice its size it is 4 m tall. A block at y = -4 has its top at y = 0, and a block at y = 2 has its top at y = 6.

How wide may a gap be? The player jumps up at 5.5 m/s, and gravity pulls at 9.81 m/s². The jump takes 2 × 5.5 / 9.81 = 1.12 s to come back to the same height. Walking at 3 m/s the player covers 3 × 1.12 = 3.4 m in the air, and running at 6.5 m/s covers 7.3 m. So a 4 m gap needs a run, and a gap of 8 m or 12 m needs help: a moving platform and a jump pad.

:::example
The jump pad throws the player up at 12 m/s. The player rises 12² / (2 × 9.81) = 7.3 m, which clears the 6 m of the highest island. The player is back at 6 m after (12 + √(12² - 2 × 9.81 × 6)) / 9.81 = 1.75 s. In that time a runner covers 6.5 × 1.75 = 11.4 m, enough for an 8 m gap, while a walker covers 5.2 m and falls short.
:::

The course has four islands. Each row of the table is a set of blocks at the grid positions (x, z), at the height y of the block's base.

| Island | Blocks at (x, z) | y | Top | What happens there |
| --- | --- | --- | --- | --- |
| A | (0, 0), (4, 0), (0, -4), (4, -4) | -4 | 0 | The start |
| B | (0, -12), (4, -12) | -4 | 0 | A gap of 4 m before it; a checkpoint |
| C | (0, -28), (4, -28) | -4 | 0 | Across 12 m on a moving platform; a checkpoint and the pad |
| D | (0, -40), (4, -40) | 2 | 6 | Over an 8 m gap by the pad; the flag |

All the blocks are static and have a mesh :term[collider]{id=collider}. A **mesh collider** is a collider that follows the triangles of the mesh, so it fits the model exactly; it is the right shape for scenery that never moves. Physics allows such a shape only on a static body.

:::::steps

1. Delete the template's ground, so that nothing holds the player under the islands.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Ground` in the Hierarchy and press **Delete**.
   :::
   :::tab[With a command]
   Find the entity by its name, then delete it with the id that the first command lists.

   ```json
   { "command": "entity.find", "parameters": { "name": "Ground" } }
   { "command": "entity.delete", "parameters": { "entities": [ "<the id>" ] } }
   ```

   :::
   ::::

   **You should see:** a sky and a sun, and no `Ground` in the Hierarchy. The pale brown plain below the horizon is the sky's picture of its planet's ground: nothing stands on it.

   **If you do not see it:** the ground is still there. It may be another entity of the same name: search the Hierarchy for `Ground`.

2. Make one block as a :term[prefab]{id=prefab-make}. Drag `block-grass-large-tall.glb` into the Scene view, rename the new entity `BlockTall`, and set its scale to 2.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Inspector set **Scale** to 2, 2, 2. Then select its child `block-grass-large-tall`, the entity with the mesh. Choose **Add Component ▸ Rigid Body** and set **Type** to **Static**. Choose **Add Component ▸ Mesh Collider** and clear **Convex**.
   :::
   :::tab[With a command]
   Place the model at twice its size and name it with the `id` that `asset.place` returns. Add the components to its child.

   ```json
   { "command": "asset.place", "parameters": { "asset": "Models/Platformer/block-grass-large-tall/block-grass-large-tall.glb", "point": [0, 0, 0], "scale": 2 } }
   { "command": "entity.rename", "parameters": { "entity": "<the id>", "name": "BlockTall" } }
   { "command": "entity.find", "parameters": { "name": "block-grass-large-tall" } }
   { "command": "component.add", "parameters": { "entity": "<the child's id>", "component": "RigidBody", "values": { "Type": "Static" } } }
   { "command": "component.add", "parameters": { "entity": "<the child's id>", "component": "MeshCollider", "values": { "Convex": false } } }
   { "command": "selection.set", "parameters": { "entities": [ "<the child's id>" ] } }
   { "command": "viewport.capture" }
   ```

   Collider shapes show for the selection only, in the Scene view and in `viewport.capture`.
   :::
   ::::

   **You should see:** a green outline that follows the block's shape in the Scene view.

   **If you do not see it:** there is no outline, or a plain box. The components sit on `BlockTall`, which has no mesh, or **Convex** is still on: a convex shape ignores the hollows of the mesh.

3. Turn the entity into a prefab, so that every block is a copy of one.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag `BlockTall` from the Hierarchy into the Content Browser, into a new folder `Prefabs/Course`. Make an empty entity named `Course` with **+ ▸ Empty**, and keep it at the origin.
   :::
   :::tab[With a command]
   Save the entity as a prefab, then make the `Course` entity that will hold the blocks.

   ```json
   { "command": "prefab.create", "parameters": { "entities": [ "<the id>" ], "path": "Prefabs/Course/BlockTall.stprefab" } }
   { "command": "entity.create", "parameters": { "name": "Course" } }
   ```

   :::
   ::::

   **You should see:** `BlockTall` in the folder, and its Hierarchy name in a different colour: the entity is now an instance of the prefab.

   **If you do not see it:** the folder shows a file with no preview. Wait for the import bar to finish.

4. Lay out the ten blocks of the table. Delete the first `BlockTall`, then place the others under `Course`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag the prefab ten times from the Content Browser onto `Course` in the Hierarchy. Select each copy and type its **Position** from the table: for island A, (0, -4, 0), (4, -4, 0), (0, -4, -4) and (4, -4, -4), and so on.
   :::
   :::tab[With a command]
   This step has no menu or button for ten copies at once: delete the first block, then run `prefab.instantiate` with the list `instances`, one entry for each block. The example makes the four blocks of island A.

   ```json
   { "command": "entity.delete", "parameters": { "entities": [ "<the id>" ] } }
   { "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Course/BlockTall.stprefab", "instances": [
     { "parent": "<Course id>", "components": { "Transform": { "Translation": [0, -4, 0] } } },
     { "parent": "<Course id>", "components": { "Transform": { "Translation": [4, -4, 0] } } },
     { "parent": "<Course id>", "components": { "Transform": { "Translation": [0, -4, -4] } } },
     { "parent": "<Course id>", "components": { "Transform": { "Translation": [4, -4, -4] } } } ] } }
   ```

   :::
   ::::

   **You should see:** four islands in a row, with their gaps. Island D stands higher than the others.

   **If you do not see it:** a block floats or sinks. Check its y against the table: the blocks at -4 have their tops at 0, and the blocks at 2 have their tops at 6.

5. Press **Play** and look at the camera. Nothing moves, because the player does not exist yet.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, wait for the game to start and press it again to stop.
   :::
   :::tab[With a command]
   `physics.stats` waits for the colliders.

   ```json
   { "command": "play.start" }
   { "command": "physics.stats", "expect": { "/waitingForMeshes": { "equals": false } }, "until": { "seconds": 60 } }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the Scene view of the course, then a pause of a moment. Play holds the simulation until the colliders of the ten meshes are cooked, at most 10 s, and a warning in the Console names any that are missing.

   **If you do not see it:** the Console says a collider waited for its mesh. The import is not finished: wait for the import bar and press **Play** again.

:::::

::checkpoint{stage=2}

::figure{id=s2-course}

## Make the player walk and jump

A character in a game is an invisible shape that the engine moves, with a model attached. The shape is a **capsule**, a cylinder with round ends, and the component that moves it is the :term[character controller]{id=character-controller}. You tell the controller where to go, and it walks, falls, climbs small steps and slides along walls.

Three ideas make the controls feel right. Each has a number that you can check by hand.

The first idea is that the player walks where the camera looks. Pressing up must move the character away from the screen, whichever way the camera points. The script flattens the camera's forward onto the ground and turns the input into a direction on that plane. The right side is the cross product $f \times u$, where $f$ is the flat forward, $u$ is up (0, 1, 0) and $\times$ is the cross product. A camera that looks along -Z has the forward (0, 0, -1) and the right (1, 0, 0), so an input of (0.71, 0.71) gives the walk (0.71, 0, -0.71), at 3 m/s.

The second idea is that the body turns toward its walk, and the angle of a walk (x, z) is `atan2(-x, -z)` in degrees, with 0 meaning "facing -Z". Turning by the plain difference of two angles goes the long way round at the seam of 360 degrees. The function `std::remainder` returns the difference in the range from -180 to 180. From a yaw of 350 degrees to a target of 90 degrees the plain difference is -260, and `std::remainder(-260, 360)` is 100, the short way. The body turns at most 720 degrees a second, so one frame at 60 frames per second turns it 12 degrees at most.

The third idea is the :term[coyote time]{id=coyote-time}. A player who walks off a ledge and presses Jump a moment late should still jump. The script keeps the seconds since the player stood on the ground, and a jump counts while they are at most 0.15 s. At 3 m/s that is a grace of 0.45 m, and 9 frames at 60 frames per second.

:::question
The script uses `std::atan2`, `glm::normalize` and calls such as `controller.Move(...)`. [Classes and the rest of C++ for games](../basics/programming-3.md) teaches calling a function of another class and the `::` of a name.
:::

The script has a header and a :term[source file]{id=source-file}. The header lists the fields that you tune in the Inspector. The source starts with the part you read first: the walk and the turn.

```cpp src="book:tutorials/make/project-platformer/ThirdPersonPlayer.step3.cpp#L48-L63"
// The Move action: +Y walks forward, and its length is at most 1, a diagonal of keys too.
const glm::vec2 input = Input::GetActionValue("Gameplay/Move");
const glm::vec3 forward = GetViewForward();
const glm::vec3 right = glm::normalize(glm::cross(forward, c_Up));
const glm::vec3 move = forward * input.y + right * input.x;
const float speed = Input::IsActionDown("Gameplay/Run") ? RunSpeed : WalkSpeed;
controller.Move(move * speed);
if (glm::length(move) > 0.05f)
{
	// The controller moves the position; the script turns the body toward where it walks.
	const float target = glm::degrees(std::atan2(-move.x, -move.z));
	const float difference = std::remainder(target - m_Yaw, 360.0f);
	const float maxTurn = TurnSpeed * deltaTime;
	m_Yaw += std::clamp(difference, -maxTurn, maxTurn);
	transform.SetWorldRotation(glm::angleAxis(glm::radians(m_Yaw), c_Up));
}
```

1. **Lines 49-52:** the Move action gives a vector, and the camera's flat forward and right side turn it into a direction in the world.
2. **Lines 53-54:** the Run action picks the speed, and the controller moves the player at that velocity.
3. **Line 58:** the angle of the walk, in degrees.
4. **Lines 59-61:** the short way round, limited to the turn of one frame.
5. **Line 62:** only the script sets the rotation: the controller never turns the body.

The jump and the fall come next. A fall below a height and the `Respawn` action both call `Respawn`, which puts the player back at the last checkpoint or at the start.

```cpp src="book:tutorials/make/project-platformer/ThirdPersonPlayer.step3.cpp#L65-L71"
if (Input::IsActionPressed("Gameplay/Jump") && m_JumpCooldown <= 0.0f && m_AirSeconds <= CoyoteSeconds)
	StartJump(JumpSpeed, position, true);
if (Input::IsActionPressed("Gameplay/Respawn"))
	Respawn();

if (position.y < FallHeight)
	Respawn();
```

Sending the player to a checkpoint is a teleport of the controller. A teleport tells the engine that the player did not travel, so the drawn picture does not slide across the course.

```cpp src="book:tutorials/make/project-platformer/ThirdPersonPlayer.step3.cpp#L79-L86"
void ThirdPersonPlayer::Respawn()
{
	const bool atCheckpoint = Checkpoint > 0 && Checkpoint <= static_cast<int32_t>(m_Checkpoints.size());
	const glm::vec3 target = atCheckpoint ? m_Checkpoints[static_cast<size_t>(Checkpoint - 1)] : StartPosition;
	GetEntity().GetCharacterController().Teleport(target + glm::vec3(0.0f, 0.05f, 0.0f));
	m_AirSeconds = 0.0f;
	Log::Info("Platformer: back to checkpoint ", Checkpoint);
}
```

Now you make the controls, the entity and the robot. The Gameplay map holds six actions.

| Action | Kind | Bindings |
| --- | --- | --- |
| `Move` | Vector2 | `2D:Key/W,Key/S,Key/A,Key/D`, `2D:Key/Up,Key/Down,Key/Left,Key/Right`, `Gamepad/LeftStick` |
| `Look` | Vector2 | `Gamepad/RightStick` |
| `Jump` | Button | `Key/Space`, `Gamepad/A` |
| `Run` | Button | `Key/LeftShift`, `Gamepad/RightBumper` |
| `Respawn` | Button | `Key/R` |
| `Pause` | Button | `Key/Escape`, `Gamepad/Start` |

:::::steps

1. Make the project's Gameplay map with the six actions of the table. [Input and input actions](input.md) taught how.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Project Settings...**, open the page **Input Actions**, add the map `Gameplay` and add the six actions with their bindings.
   :::
   :::tab[With a command]
   Add the map, then each action with its kind and bindings from the table.

   ```json
   { "command": "inputActions.setMap", "parameters": { "map": "Gameplay" } }
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Move", "kind": "Vector2", "bindings": [
     "2D:Key/W,Key/S,Key/A,Key/D", "2D:Key/Up,Key/Down,Key/Left,Key/Right", "Gamepad/LeftStick" ] } }
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Look", "kind": "Vector2", "bindings": [ "Gamepad/RightStick" ] } }
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Jump", "kind": "Button", "bindings": [ "Key/Space", "Gamepad/A" ] } }
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Run", "kind": "Button", "bindings": [ "Key/LeftShift", "Gamepad/RightBumper" ] } }
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Respawn", "kind": "Button", "bindings": [ "Key/R" ] } }
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Pause", "kind": "Button", "bindings": [ "Key/Escape", "Gamepad/Start" ] } }
   ```

   :::
   ::::

   **You should see:** six actions in the map, with one chip for each binding.

   **If you do not see it:** an action is missing its map name. Write `Gameplay/Move`, the map, a slash and the action.

2. Make the player: an empty entity named `Player` at (2, 0.1, -2), with a character controller and the tag `Player`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **+ ▸ Empty** and rename it `Player`. Set **Position** to 2, 0.1, -2. Choose **Add Component ▸ Character Controller** and set **Height** to 1.8 and **Radius** to 0.4. Choose **Add Component ▸ Tag** and type `Player`.
   :::
   :::tab[With a command]
   Create the entity with its components at once.

   ```json
   { "command": "entity.create", "parameters": { "name": "Player", "components": {
     "Transform": { "Translation": [2, 0.1, -2] },
     "CharacterController": { "Height": 1.8, "Radius": 0.4 },
     "Tag": { "Tag": "Player" } } } }
   { "command": "selection.set", "parameters": { "entities": [ "<the player's id>" ] } }
   { "command": "camera.focus", "parameters": { "entities": [ "<the player's id>" ] } }
   { "command": "viewport.capture" }
   ```

   :::
   ::::

   **You should see:** a wire capsule on island A, with its bottom on the grass.

   **If you do not see it:** the capsule stands in the grass or hangs high. The entity's origin is the bottom of the capsule: its y must equal the block's top, plus a little.

3. Add the robot as a child of the player, turned and scaled. Drag `RobotExpressive.glb` into the Scene view, then onto `Player` in the Hierarchy, and rename it `Robot`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the robot and set **Position** to 0, 0, 0, **Rotation** Y to 180 and **Scale** to 0.4, 0.4, 0.4.
   :::
   :::tab[With a command]
   Place the model turned and scaled, then move it under the player and name it.

   ```json
   { "command": "asset.place", "parameters": { "asset": "Models/Robot/RobotExpressive.glb", "point": [0, 0, 0], "rotation": [0, 180, 0], "scale": 0.4 } }
   { "command": "entity.setParent", "parameters": { "entity": "<the robot's id>", "parent": "<the player's id>", "keepWorldTransform": false } }
   { "command": "entity.rename", "parameters": { "entity": "<the robot's id>", "name": "Robot" } }
   { "command": "viewport.capture" }
   ```

   :::
   ::::

   **You should see:** the robot standing inside the capsule, with its face toward -Z, away from the editor camera, and its head under the capsule's top.

   **If you do not see it:** the robot is about four metres tall, or it looks backwards. A glTF model faces +Z while forward is -Z: it needs a turn of 180 degrees about Y ([Positions, rotations and units](transforms-units.md)). At its import scale the model is larger than a person, so it needs the scale 0.4: 0.4 × 4.08 m is 1.63 m.

4. Add the script files `ThirdPersonPlayer.h` and `ThirdPersonPlayer.cpp` of this checkpoint, the folder `Scripts` of checkpoint 3's download, to the project's `Scripts` folder and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy the two files into `Scripts`. Press **Ctrl+B** and wait for the build to finish.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the Console reporting a successful build, and `ThirdPersonPlayer` in the script picker.

   **If you do not see it:** the build lists errors. Read the first: a missing file of the two is the usual cause.

5. Attach the script to `Player` and fill its fields.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Player`, choose **Add Component ▸ Script** and pick `ThirdPersonPlayer`. Drag `Robot` onto `Robot`, drag `Jump.ogg` onto `Jump Sound` and `Land.ogg` onto `Land Sound`. Leave `Camera` empty: the script then uses the scene's main camera.
   :::
   :::tab[With a command]
   Attach it with the field `Robot`; the sounds take their asset paths.

   ```json
   { "command": "script.add", "parameters": { "entity": "<the player's id>", "class": "ThirdPersonPlayer", "fields": {
     "Robot": "<the robot's id>", "JumpSound": "Sounds/Jump.ogg", "LandSound": "Sounds/Land.ogg" } } }
   ```

   :::
   ::::

   **You should see:** the script's fields with their defaults: `Walk Speed` 3, `Run Speed` 6.5 and `Jump Speed` 5.5.

   **If you do not see it:** the picker is empty. The build failed or has not finished.

6. Press **Play**, hold **W**, press **Space** and press **R**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The camera is still the template's fixed camera, so you walk away from it. Walk to the edge of island A and over it.
   :::
   :::tab[With a command]
   After play and the wait of stage 2, use `input.key` with the key `W` and a number of `steps` to hold it.

   ```json
   { "command": "input.key", "parameters": { "key": "W", "steps": 60 } }
   ```

   :::
   ::::

   **You should see:** the capsule walks, and the robot slides along, dancing: its :term[Animator]{id=animator} plays the file's first clip, with no controller yet. A jump lifts it about 1.5 m. Over the edge it falls, and 15 m below the start it is back at the start.

   **If you do not see it:** the player walks the wrong way. The view of the template's camera looks along the course; a camera that looks along +Z reverses the walk. Stage 4 replaces the camera.

:::::

::checkpoint{stage=3}

::figure{id=s3-player}

## Follow with a camera

[Characters and cameras](characters-cameras.md) built a camera that stays behind the player, turns with the mouse and never hides the player in a wall. This stage only uses it again.

:::::steps

1. Copy `FollowCamera.cpp` from this checkpoint into `Scripts`. It is the file of the final step of the camera tutorial. Build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy the file, then press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the class `FollowCamera` in the script picker.

   **If you do not see it:** the build has errors. A file of the earlier tutorial that you copied too is the usual cause: keep only the final `FollowCamera.cpp`.

2. Attach it to `Main Camera` and point it at the player.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Main Camera`, choose **Add Component ▸ Script** and pick `FollowCamera`. Drag `Player` onto `Target`.
   :::
   :::tab[With a command]
   Run `script.add` with the camera's `id` and the player's `id` as the field `Target`.

   ```json
   { "command": "script.add", "parameters": { "entity": "<the camera's id>", "class": "FollowCamera", "fields": { "Target": "<the player's id>" } } }
   ```

   :::
   ::::

   **You should see:** the Game view looks at the player from 6.5 m behind and a little above.

   **If you do not see it:** the camera stays at the template's place. `Target` is empty: the script does nothing without a target.

3. Press **Play**, move the mouse and walk.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The cursor is locked while you play, and the mouse turns the camera. Walk toward the camera's far side and turn it: the player always walks away from the screen.
   :::
   :::tab[With a command]
   Turn the camera with the field `Yaw` while the game plays, and hold **W**.

   ```json
   { "command": "script.setField", "parameters": { "entity": "<the camera's id>", "class": "FollowCamera", "field": "Yaw", "value": 90 } }
   ```

   :::
   ::::

   **You should see:** with a yaw of 90 degrees the camera looks along -X, and holding **W** walks the player along -X. Near a wall the camera moves in, so that the wall never hides the player.

   **If you do not see it:** the mouse does not turn the camera. The window does not have the focus: click it once.

:::::

::checkpoint{stage=4}

::figure{id=s4-camera}

## Bring the robot to life

The robot is a skeleton and a set of clips, and the :term[animator]{id=animator} plays the clip of the state it is in. [Animation for game makers](animation.md) built a controller for this very robot in the Asset tab. Here you make the whole controller with one command, because no menu creates one.

The controller has three parameters, four states and seven transitions. `Speed` is the ground speed in m/s, `Grounded` says whether the player stands, and `Jump` is a trigger. The script writes them. Idle becomes Walk above 0.1 m/s, and Walk becomes Run above 4.5 m/s. The walk speed of 3 m/s and the run speed of 6.5 m/s lie on two sides of 4.5, so each settles in one state.

The new lines of the script write the parameters once per update.

```cpp src="book:tutorials/make/project-platformer/ThirdPersonPlayer.step5.cpp#L70-L76"
if (Robot.IsValid())
{
	const glm::vec3 velocity = controller.GetVelocity();
	Animator animator = Robot.GetAnimator();
	animator.SetFloat("Speed", glm::length(glm::vec2(velocity.x, velocity.z)));
	animator.SetBool("Grounded", Grounded);
}
```

The jump is a trigger, so the script sets it only when it jumps; `StartJump` has the line `Robot.GetAnimator().SetTrigger("Jump")`. A trigger stays set until a transition uses it, so the press and the animation do not have to meet in the same frame.

:::question
The footstep script is a class with `override` and `virtual` functions. [Classes and inheritance](../basics/cpp-classes.md) teaches both.
:::

The footstep script is short. Read its event handler.

```cpp src="book:tutorials/make/project-platformer/Footsteps.cpp#L28-L37"
void OnAnimationEvent(std::string_view name) override
{
	if (name != "Footstep")
		return;
	const std::array<AssetHandle, 4> clips = GetClips();
	const AssetHandle clip = clips[static_cast<size_t>(m_Random.Range(0, 3))];
	if (clip.IsValid())
		Audio::PlayOneShotAt(clip, GetTransform().GetWorldPosition(), Volume, m_Random.Range(0.9f, 1.1f));
	Steps++;
}
```

1. **Lines 30-31:** every event name but `Footstep` is ignored.
2. **Lines 32-33:** one of the four clips, chosen by a random index.
3. **Line 35:** the clip plays at the robot's position, at a pitch between 0.9 and 1.1.

The random pitch hides that only four clips exist.

:::::steps

1. List the robot's clips.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Expand the robot model in the Content Browser: each clip is a :term[sub-asset]{id=sub-asset} below it. Note the clips named Idle, Walking, Running and Jump.
   :::
   :::tab[With a command]
   This step has no menu or button for the handles: run the command. Each clip in the answer has an `asset` of 16 hexadecimal digits, its handle.

   ```json
   { "command": "animation.info", "parameters": { "asset": "Models/Robot/RobotExpressive.glb" } }
   ```

   :::
   ::::

   **You should see:** about a dozen clips, with Idle, Walking, Running and Jump among them.

   **If you do not see it:** the list is empty. The model is not imported yet.

2. Make the controller with one command.

   ::::tabs{sync=how}
   :::tab[In the editor]
   This step has no menu or button: run the command. The Content Browser's **New** menu has no :term[animation controller]{id=animation-controller}. [Commands](commands.md) shows how to run a command from a file: save the text below as `controller.json`, with your four handles, and run `StrataCLI call animation.createController '@controller.json'`.
   :::
   :::tab[With a command]
   The parameters list the parameters, the states with the times of their footstep events, and the transitions. Replace the four handles with those of step 1.

   ```json
   { "path": "Animations/Robot.stanimator",
     "parameters": [ { "Name": "Speed", "Type": "Float", "Default": 0 }, { "Name": "Grounded", "Type": "Bool", "Default": true }, { "Name": "Jump", "Type": "Trigger" } ],
     "states": [ { "Name": "Idle", "Clip": "<Idle handle>" },
       { "Name": "Walk", "Clip": "<Walking handle>", "Events": [ { "Name": "Footstep", "Time": 0.02 }, { "Name": "Footstep", "Time": 0.5 } ] },
       { "Name": "Run", "Clip": "<Running handle>", "Events": [ { "Name": "Footstep", "Time": 0.28 }, { "Name": "Footstep", "Time": 0.76 } ] },
       { "Name": "Jump", "Clip": "<Jump handle>", "Loop": false } ],
     "transitions": [
       { "AnyState": true, "CanTransitionToSelf": true, "To": "Jump", "Duration": 0.1, "Conditions": [ { "Parameter": "Jump", "Mode": "Set" } ] },
       { "From": "Idle", "To": "Walk", "Duration": 0.15, "Conditions": [ { "Parameter": "Speed", "Mode": "Greater", "Threshold": 0.1 } ] },
       { "From": "Walk", "To": "Idle", "Duration": 0.2, "Conditions": [ { "Parameter": "Speed", "Mode": "Less", "Threshold": 0.1 } ] },
       { "From": "Walk", "To": "Run", "Duration": 0.2, "Conditions": [ { "Parameter": "Speed", "Mode": "Greater", "Threshold": 4.5 } ] },
       { "From": "Run", "To": "Walk", "Duration": 0.2, "Conditions": [ { "Parameter": "Speed", "Mode": "Less", "Threshold": 4.5 } ] },
       { "From": "Jump", "To": "Walk", "Duration": 0.15, "ExitTime": 0.4, "Conditions": [ { "Parameter": "Grounded", "Mode": "True" }, { "Parameter": "Speed", "Mode": "Greater", "Threshold": 0.1 } ] },
       { "From": "Jump", "To": "Idle", "Duration": 0.2, "ExitTime": 0.4, "Conditions": [ { "Parameter": "Grounded", "Mode": "True" }, { "Parameter": "Speed", "Mode": "Less", "Threshold": 0.1 } ] } ] }
   ```

   1. **Line 2:** the three parameters, with their types and defaults.
   2. **Lines 4-5:** the footstep events of Walk and Run, in seconds into the clip.
   3. **Line 8:** from any state to Jump when the trigger is set.
   4. **Lines 11-12:** the speed threshold 4.5 between Walk and Run, tested in both directions.
   5. **Lines 13-14:** Jump leaves after 0.4 of its clip, when the player is grounded.

   :::
   ::::

   **You should see:** the new file `Animations/Robot.stanimator` in the Content Browser. Select it: the Asset tab shows the three parameters, four states and seven transitions.

   **If you do not see it:** the command says a state has no clip, or a clip handle is not a clip. Take the handles from the `asset` of each clip, not of the model.

3. Select the `Robot` entity and set the **Controller** field of its Animator to `Animations/Robot.stanimator`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Robot`, find the Animator in the Inspector and drag the controller onto **Controller**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the robot's id>", "component": "Animator", "values": { "Controller": "Animations/Robot.stanimator" } } }
   ```

   :::
   ::::

   **You should see:** the robot in its rest pose until play starts it in Idle.

   **If you do not see it:** the robot dances in play. The Animator's **Controller** is empty, or **Play On Start** is off.

4. Replace `ThirdPersonPlayer.cpp` by the file of this checkpoint. It sets the controller's parameters. Press **Ctrl+B**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy the file over the old one and build.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** a successful build.

   **If you do not see it:** the build fails on `Animator`. The file is the old one: check that you replaced it.
5. Add the script `Footsteps` of [Animation for game makers](animation.md) to the `Robot` entity and set its four step sounds.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy `Footsteps.cpp` from this checkpoint, build, select `Robot`, choose **Add Component ▸ Script**, pick `Footsteps` and drag `Grass1.ogg` to `Grass4.ogg` onto `Step1` to `Step4`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<the robot's id>", "class": "Footsteps", "fields": {
     "Step1": "Sounds/Footsteps/Grass1.ogg", "Step2": "Sounds/Footsteps/Grass2.ogg", "Step3": "Sounds/Footsteps/Grass3.ogg", "Step4": "Sounds/Footsteps/Grass4.ogg" } } }
   ```

   :::
   ::::

   **You should see:** the field `Steps` counting up while the robot walks.

   **If you do not see it:** the count stays 0. The states Walk and Run have no `Footstep` events: look at the Asset tab.

6. Press **Play** and walk, run and jump.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Walk with **W**, run by holding the `Shift` key and jump with **Space**. Select `Robot` while you play and read the state in the Inspector.
   :::
   :::tab[With a command]
   After play and the wait of stage 2, jump first: the game pauses, because a jump is too short to catch while it runs.

   ```json
   { "command": "play.pause", "parameters": { "paused": true } }
   { "command": "input.key", "parameters": { "key": "Space" } }
   { "command": "play.step", "parameters": { "steps": 10 } }
   { "command": "animation.info", "parameters": { "entity": "<the robot's id>" } }
   { "command": "play.pause", "parameters": { "paused": false } }
   { "command": "input.key", "parameters": { "key": "W", "action": "press" } }
   { "command": "animation.info", "parameters": { "entity": "<the robot's id>" } }
   { "command": "input.key", "parameters": { "key": "LeftShift", "action": "press" } }
   { "command": "animation.info", "parameters": { "entity": "<the robot's id>" } }
   { "command": "input.releaseAll" }
   ```

   1. **Lines 1–4:** pause, tap **Space**, run ten :term[fixed steps]{id=fixed-step} and read the state in the air.
   2. **Lines 5–7:** let the game run, hold **W** and read the state of the walk.
   3. **Lines 8–10:** hold the `Shift` key as well, read the run, and let every key go.

   `animation.info` answers the `state`. A change of state fades over 0.15 to 0.2 s: read again if the answer names the old one. The steps you cannot hear, `Steps` of `Footsteps` counts.
   :::
   ::::

   **You should see:** Idle at rest, Walk below the run threshold, Run with the `Shift` key held, and Jump in the air, with a step sound at each foot.

   **If you do not see it:** the robot stays in Idle while it walks. `Speed` never exceeds 0.1: the player script is the old one.

:::::

::checkpoint{stage=5}

::figure{id=s5-robot}

## Make a course to finish

Now the game needs something to do: coins to collect, a pad to bounce on, checkpoints, a flag and a clock. Each of these is a small thing that knows one fact, and the game needs one place that adds them up.

That place is the `Game` entity with the script `CourseState`. A coin that the player touches finds the `Game` entity by name and calls `AddCoin`, and the goal calls `Complete`. Neither keeps the script: one kept across frames may be gone after a scene change or a :term[hot reload]{id=hot-reload}, and a find at each touch costs almost nothing.

A **trigger** is a collider that reports overlaps and does not push. The coin is a sphere and the pad a box, each on a static body. A trigger sees every shape of a body that moves, such as the player's capsule. A static trigger never reports a static body, so the coins do not notice the islands they float beside, which is what you want.

The heads-up display (HUD) shows the time. The sample writes it with `std::snprintf`. This page writes minutes and seconds with integer division and the remainder operator, so you can read every step. The sketch runs the function on four times.

```cpp sketch="make-project-platformer-time.cpp"
// The course's clock text: minutes, seconds and tenths from a count of seconds, with integer division and the
// remainder operator only.

#include <algorithm>
#include <cstdio>
#include <string>

std::string FormatTime(float seconds)
{
	// Count whole tenths first: one rounding, then every other step is exact integer arithmetic.
	const int tenths = static_cast<int>(std::max(0.0f, seconds) * 10.0f + 0.5f);
	const int wholeSeconds = (tenths / 10) % 60;
	std::string text = std::to_string(tenths / 600) + ":";
	if (wholeSeconds < 10)
		text += "0";
	return text + std::to_string(wholeSeconds) + "." + std::to_string(tenths % 10);
}

int main()
{
	const float samples[] = { 0.0f, 9.96f, 65.3f, 600.0f };
	for (const float seconds : samples)
		std::printf("%7.2f seconds read %s\n", seconds, FormatTime(seconds).c_str());
	return 0;
}
```

```text output-of="make-project-platformer-time.cpp"
   0.00 seconds read 0:00.0
   9.96 seconds read 0:10.0
  65.30 seconds read 1:05.3
 600.00 seconds read 10:00.0
```

1. **Lines 10-11:** the time becomes a whole number of tenths, rounded once.
2. **Line 12:** the seconds that remain after whole minutes.
3. **Lines 13-16:** the text is minutes, a colon, the seconds with a leading zero and the tenth.

The output shows the rounding: 9.96 seconds is 99.6 tenths plus the half that rounds it up, which is 100 tenths, so the text reads `0:10.0` and not `0:09.10`.

The new part of the player script finds the markers by name and remembers the last one reached. The helper starts from `Checkpoint1` and continues until a number has no entity.

```cpp src="book:tutorials/make/project-platformer/ThirdPersonPlayer.cpp#L17-L28"
std::vector<glm::vec3> FindCheckpoints()
{
	std::vector<glm::vec3> positions;
	for (int32_t index = 1; index <= c_MaxCheckpoints; index++)
	{
		const Entity marker = Scene::FindEntityByName("Checkpoint" + std::to_string(index));
		if (!marker.IsValid())
			break;
		positions.push_back(marker.GetTransform().GetWorldPosition());
	}
	return positions;
}
```

1. **Line 22:** the name is `Checkpoint` and a number.
2. **Lines 23-24:** the search stops at the first number that no entity has.
3. **Line 25:** the marker's :term[world position]{id=world-position} is all the player keeps.

The check runs every update, and only while the player stands. Only the markers after the last one reached are tested, so the order of the course is kept.

```cpp src="book:tutorials/make/project-platformer/ThirdPersonPlayer.cpp#L128-L139"
void ThirdPersonPlayer::UpdateCheckpoints(const glm::vec3& position)
{
	if (!Grounded)
		return;
	for (size_t index = static_cast<size_t>(std::max(Checkpoint, 0)); index < m_Checkpoints.size(); index++)
	{
		const glm::vec3& checkpoint = m_Checkpoints[index];
		const glm::vec2 offset(position.x - checkpoint.x, position.z - checkpoint.z);
		if (glm::length(offset) < c_CheckpointRadius && std::abs(position.y - checkpoint.y) < 2.5f)
			Checkpoint = static_cast<int32_t>(index) + 1;
	}
}
```

1. **Lines 130-131:** a marker counts only while the player stands on the ground.
2. **Line 132:** the loop starts after the last marker reached.
3. **Lines 135-137:** within 3 m on the ground plane and 2.5 m in height, the marker becomes the last one reached.

:::question
The pad's script keeps a pointer, `ThirdPersonPlayer* player`, and calls `player->Launch`. [Pointers and memory](../basics/cpp-memory.md) teaches pointers and the arrow.
:::

The pad's script is the short example of a trigger that talks to another script.

```cpp src="book:tutorials/make/project-platformer/JumpPad.cpp#L18-L28"
void OnTriggerEnter(const Collision& collision) override
{
	if (!collision.Other.IsValid() || collision.Other.GetTag() != "Player")
		return;
	ThirdPersonPlayer* player = collision.Other.GetScript<ThirdPersonPlayer>();
	if (!player)
		return;
	player->Launch(LaunchSpeed);
	if (BounceSound.IsValid())
		Audio::PlayOneShotAt(BounceSound, GetTransform().GetWorldPosition(), 0.8f);
}
```

1. **Line 20:** only the player, found by its tag, launches the pad.
2. **Lines 22-24:** the player's script, found on the other entity; a missing script ends the call.
3. **Line 25:** `Launch` throws the player up.
4. **Lines 26-27:** the bounce sound plays at the pad.

The completion of the course is the longest handler of `CourseState`. Read it for the order of its steps.

```cpp src="book:tutorials/make/project-platformer/CourseState.cpp#L72-L95"
void CourseState::Complete()
{
	if (Completed)
		return;
	Completed = true;
	const bool best = BestSeconds <= 0.0f || ElapsedSeconds < BestSeconds;
	if (best)
	{
		BestSeconds = ElapsedSeconds;
		if (!Game::WriteSaveFile(c_BestTimeFile, std::to_string(BestSeconds)))
			Log::Warn("Platformer: the best time could not be saved");
	}
	if (CompleteSound.IsValid())
		Audio::PlayOneShot(CompleteSound, 0.8f);
	if (CompletePanel.IsValid())
		CompletePanel.SetActive(true);
	if (CompleteTimeText.IsValid())
		CompleteTimeText.GetUI().SetText("Time  " + FormatTime(ElapsedSeconds) + "    Coins  " + std::to_string(Coins) + " / " + std::to_string(TotalCoins));
	if (CompleteBestText.IsValid())
		CompleteBestText.GetUI().SetText(best ? "A new best time!" : "Best  " + FormatTime(BestSeconds));
	if (PlayAgainButton.IsValid())
		PlayAgainButton.GetUI().Focus();
	Input::SetCursorMode(CursorMode::Normal);
}
```

1. **Lines 74-76:** a second call does nothing, so the goal may report many times.
2. **Lines 77-83:** a time below the best, or no best yet, is saved to the file.
3. **Lines 86-91:** the panel opens and its two texts get the time and the best time.
4. **Lines 92-94:** the first button gets the focus, and the cursor is free for the mouse.

:::::steps

1. Make the HUD: a canvas named `HUD` with two texts, `CoinsText` at the top left and `TimeText` at the top right.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+**, choose **UI**, then `Canvas`, and rename it `HUD`. Clear **Receives Input** in its **UI Canvas**, so that it never blocks a click. Add two `Text` entities below it and rename them. Set each text's **Text** to `0 / 8` and `0:00.0`. [Text, score and bars](hud.md) shows how to anchor them.
   :::
   :::tab[With a command]
   Create the canvas and clear its **Receives Input**, then create the texts with their anchors.

   ```json
   { "command": "ui.create", "parameters": { "type": "canvas", "name": "HUD" } }
   { "command": "component.set", "parameters": { "entity": "<HUD id>", "component": "UICanvas", "values": { "ReceivesInput": false } } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<HUD id>", "name": "CoinsText", "text": "0 / 8", "anchor": "topLeft", "position": [24, 24], "size": [240, 48] } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<HUD id>", "name": "TimeText", "text": "0:00.0", "anchor": "topRight", "position": [-24, 24], "size": [240, 48] } }
   ```

   :::
   ::::

   **You should see:** the two texts in the corners of the Game view.

   **If you do not see it:** the texts are outside the view. Check the canvas: it must be a **Screen Space** canvas.

2. Make the completion panel: an image named `Complete` under `HUD` with two texts, `CompleteTime` and `CompleteBest`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add a `Panel` under the canvas, rename it `Complete`, and add two texts below it with the names. The script hides the panel when the course starts.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "panel", "parent": "<HUD id>", "name": "Complete", "anchor": "middleCenter", "size": [640, 360] } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<Complete id>", "name": "CompleteTime", "text": "Time", "anchor": "topCenter", "position": [0, 90], "size": [600, 60] } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<Complete id>", "name": "CompleteBest", "text": "Best", "anchor": "topCenter", "position": [0, 170], "size": [600, 60] } }
   ```

   :::
   ::::

   **You should see:** a panel with two lines of text in the middle of the view.

   **If you do not see it:** the texts are beside the panel. Check that their parent is the panel, not the canvas.

3. Make the `Game` entity and give it `CourseState`: copy `CourseState.h` and `CourseState.cpp` into `Scripts`, build, attach and fill the fields.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **+ ▸ Empty** and rename it `Game`. Press **Ctrl+B**, then choose **Add Component ▸ Script** and pick `CourseState`. Drag `CoinsText` onto `Coins Text`, `TimeText` onto `Time Text`, `Complete` onto `Complete Panel`, the two texts onto `Complete Time Text` and `Complete Best Text`, and the sounds `Coin.ogg` and `Complete.ogg` onto `Coin Sound` and `Complete Sound`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "entity.create", "parameters": { "name": "Game" } }
   { "command": "script.add", "parameters": { "entity": "<Game id>", "class": "CourseState", "fields": {
     "CoinsText": "<CoinsText id>", "TimeText": "<TimeText id>", "CompletePanel": "<Complete id>",
     "CompleteTimeText": "<CompleteTime id>", "CompleteBestText": "<CompleteBest id>",
     "CoinSound": "Sounds/Coin.ogg", "CompleteSound": "Sounds/Complete.ogg" } } }
   ```

   :::
   ::::

   **You should see:** when you press **Play**, the coin text reads `0 / 0` and the time text counts up from `0:00.0`. The panel stays hidden.

   **If you do not see it:** the texts stay as you typed them. A field is empty: the script writes only into the texts it knows.

4. Make the coin prefab: an entity `Coin` with a sphere trigger, the tag `Coin` and the script `Coin`, whose child is the coin model.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy `Coin.cpp` and `Goal.cpp` into `Scripts` and build. Choose **+ ▸ Empty**, name it `Coin`, and add **Sphere Collider** (Radius 0.7), **Rigid Body** (**Type** Static, **Is Trigger** on), **Tag** `Coin` and the script `Coin`. Drag `coin-gold.glb` onto it as a child. Drag `Coin` into `Prefabs`.
   :::
   :::tab[With a command]
   Build, then create the entity with its components, move the model under it with `asset.place` and `entity.setParent` as in stage 3, and save the prefab.

   ```json
   { "command": "script.build" }
   { "command": "entity.create", "parameters": { "name": "Coin", "components": {
     "SphereCollider": { "Radius": 0.7 }, "RigidBody": { "Type": "Static", "IsTrigger": true }, "Tag": { "Tag": "Coin" } } } }
   { "command": "script.add", "parameters": { "entity": "<Coin id>", "class": "Coin" } }
   { "command": "prefab.create", "parameters": { "entities": [ "<Coin id>" ], "path": "Prefabs/Coin.stprefab" } }
   ```

   :::
   ::::

   **You should see:** a gold coin with a wire sphere around it.

   **If you do not see it:** the coin does not spin when you play. The model is not a child of the entity: the script spins the first child.

5. Delete the first `Coin`, which would be a ninth. Then place the eight coins at (2, 1, 0), (0, 1, -12), (4, 1, -12), (2, 1, -21), (0, 1, -28), (4, 1, -28), (0, 7, -40) and (4, 7, -40).

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Coin` in the Hierarchy and press **Delete**. Drag the prefab eight times into the Scene view and type each **Position**.
   :::
   :::tab[With a command]
   One call then places them all. The example holds two of the eight.

   ```json
   { "command": "entity.delete", "parameters": { "entities": [ "<Coin id>" ] } }
   { "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Coin.stprefab", "instances": [
     { "components": { "Transform": { "Translation": [2, 1, 0] } } },
     { "components": { "Transform": { "Translation": [0, 1, -12] } } } ] } }
   ```

   :::
   ::::

   **You should see:** the coin text reads `0 / 8` when you press **Play**, and a coin that the player touches vanishes with a sound and raises the count.

   **If you do not see it:** the count stays 0 when you touch a coin. The coin's collider is not a trigger, or the player has no tag `Player`.

6. Make the jump pad prefab: a box trigger with the tag `JumpPad` and the script `JumpPad`, whose child is the spring model. Place it at (2, 0, -29).

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy `JumpPad.cpp` and build. Make an empty entity `JumpPad` and set its **Position** to 2, 0, -29. Give it a **Box Collider** (**Half Extents** 0.8, 0.5, 0.8, **Offset** 0, 0.5, 0), a static **Rigid Body** with **Is Trigger** on, the tag `JumpPad` and the script. Drag `spring.glb` onto it and `Bounce.ogg` onto `Bounce Sound`. Drag `JumpPad` into `Prefabs`: the entity becomes the prefab's one copy.
   :::
   :::tab[With a command]
   Build, make the pad, move the spring under it as for the coin and save the prefab.

   ```json
   { "command": "script.build" }
   { "command": "entity.create", "parameters": { "name": "JumpPad", "components": { "Transform": { "Translation": [2, 0, -29] },
     "BoxCollider": { "HalfExtents": [0.8, 0.5, 0.8], "Offset": [0, 0.5, 0] }, "RigidBody": { "Type": "Static", "IsTrigger": true }, "Tag": { "Tag": "JumpPad" } } } }
   { "command": "script.add", "parameters": { "entity": "<JumpPad id>", "class": "JumpPad", "fields": { "BounceSound": "Sounds/Bounce.ogg" } } }
   { "command": "prefab.create", "parameters": { "entities": [ "<JumpPad id>" ], "path": "Prefabs/JumpPad.stprefab" } }
   ```

   :::
   ::::

   **You should see:** a spring on island C near its far edge, with a box of 1 m height around it.

   **If you do not see it:** the player walks through the spring and is not thrown up. The pad's box is smaller than the player's path: the capsule must reach inside 0.8 m of the pad's centre.

7. Make the checkpoints and the goal. The checkpoints are two empty entities, `Checkpoint1` at (2, 0, -12) and `Checkpoint2` at (2, 0, -28). The goal is an entity `Goal` at (2, 6, -40) with a box trigger, the tag `Goal`, the script `Goal` and the flag model as its child.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **+ ▸ Empty** for each marker and type the position and name. Make `Goal` with a **Box Collider** (**Half Extents** 1.4, 1.5, 1.4, **Offset** 0, 1.5, 0) and a static **Rigid Body** with **Is Trigger** on. Drag `flag.glb` onto it and add the script `Goal` with **Add Component ▸ Script**.
   :::
   :::tab[With a command]
   Create the three entities, move the flag under the goal with `asset.place` and `entity.setParent`, and attach the script.

   ```json
   { "command": "entity.create", "parameters": { "name": "Checkpoint1", "components": { "Transform": { "Translation": [2, 0, -12] } } } }
   { "command": "entity.create", "parameters": { "name": "Checkpoint2", "components": { "Transform": { "Translation": [2, 0, -28] } } } }
   { "command": "entity.create", "parameters": { "name": "Goal", "components": { "Transform": { "Translation": [2, 6, -40] },
     "BoxCollider": { "HalfExtents": [1.4, 1.5, 1.4], "Offset": [0, 1.5, 0] }, "RigidBody": { "Type": "Static", "IsTrigger": true }, "Tag": { "Tag": "Goal" } } } }
   { "command": "script.add", "parameters": { "entity": "<Goal id>", "class": "Goal" } }
   ```

   :::
   ::::

   **You should see:** the flag at the far end on island D.

   **If you do not see it:** the flag is under the island. Island D's top is at y = 6, and the goal's y must be 6.

8. Replace `ThirdPersonPlayer.cpp` by the final file of this checkpoint, so that the player knows the checkpoints, and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy the file over the old one and press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** a successful build.

   **If you do not see it:** the build fails on `Launch` or on a checkpoint. The old file is still there: check that you replaced it.

9. Play the course from start to goal.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**. Run over the first gap, take the checkpoint, jump off the island and press **R**. Finish the course if you can; to reach the flag now, move the player with **Position** to island D.
   :::
   :::tab[With a command]
   Start the game and wait for the colliders as in stage 2. Then move the player to each place, run a few steps and read.

   ```json
   { "command": "play.pause", "parameters": { "paused": true } }
   { "command": "component.set", "parameters": { "entity": "<the player's id>", "component": "Transform", "values": { "Translation": [0, 0.1, -12] } } }
   { "command": "play.step", "parameters": { "steps": 30 } }
   { "command": "script.get", "parameters": { "entity": "<Game id>", "class": "CourseState" } }
   { "command": "component.set", "parameters": { "entity": "<the player's id>", "component": "Transform", "values": { "Translation": [2, -20, -12] } } }
   { "command": "play.step", "parameters": { "steps": 5 } }
   { "command": "component.get", "parameters": { "entity": "<the player's id>", "component": "Transform" } }
   { "command": "component.set", "parameters": { "entity": "<the player's id>", "component": "Transform", "values": { "Translation": [2, 0.1, -29] } } }
   { "command": "play.step", "parameters": { "steps": 30 } }
   { "command": "component.get", "parameters": { "entity": "<the player's id>", "component": "Transform" } }
   { "command": "component.set", "parameters": { "entity": "<the player's id>", "component": "Transform", "values": { "Translation": [2, 6.1, -40] } } }
   { "command": "play.step", "parameters": { "steps": 30 } }
   { "command": "script.get", "parameters": { "entity": "<Game id>", "class": "CourseState" } }
   ```

   1. **Lines 2–4:** a coin and the first checkpoint: `Coins` reads 1.
   2. **Lines 5–7:** below the fall height of -15 m: back at the checkpoint, near (2, 0, -12).
   3. **Lines 8–10:** the pad: the player is about 5 m up.
   4. **Lines 11–13:** the goal: `Completed` is true.
   :::
   ::::

   **You should see:** the coin count rising, the player back at the first checkpoint after a fall, and at the goal the panel with the time and the line `A new best time!`. The best time is in a :term[save file]{id=save-file}: play again and the panel shows the old best.

   **If you do not see it:** the panel never opens. The player's tag is not `Player`, or the goal's box does not reach the player.

:::::

::checkpoint{stage=6}

::figure{id=s6-course}

## Add a moving platform

Island B and island C are 12 m apart, and no jump crosses that. A platform that moves between them does. The sample has no such platform; the one you make uses the script of [Characters and cameras](characters-cameras.md).

Physics treats a moving platform specially: a kinematic body follows its entity with a velocity that reaches the new place in one step, and a character that stands on it takes on that velocity. So the player rides without sliding. The platform moves in the :term[fixed step]{id=fixed-step}, `OnFixedUpdate`, for the same reason: the physics world and the platform then move together, and the camera stays steady because it tracks the drawn position.

The script moves the platform along a path. With `Travel` of (0, 0, -6) and `Period` of 8 s, the platform goes to the far end and back in 8 s, with a smooth start and stop at each end.

:::example
The position is the start plus Travel times $0.5 - 0.5\cos(2\pi t / 8)$. At t = 0 the factor is 0, and the platform stands at z = -18. At t = 2 s the factor is 0.5, so the platform is at -18 - 3 = -21. At t = 4 s the factor is 1, and the platform is at -24, where its edge meets island C at -26.
:::

:::::steps

1. Make the platform: a cube of 4 by 0.5 by 4 m with a box collider and a kinematic body, at (2, -0.25, -18).

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+**, choose a `Cube` from the meshes, rename it `Platform`, set **Position** to 2, -0.25, -18 and **Scale** to 4, 0.5, 4. Choose **Add Component ▸ Box Collider**, then **Add Component ▸ Rigid Body** and set **Type** to **Kinematic**.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Platform", "components": {
     "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "RigidBody": { "Type": "Kinematic" },
     "Transform": { "Translation": [2, -0.25, -18], "Scale": [4, 0.5, 4] } } } }
   ```

   :::
   ::::

   **You should see:** a flat slab between islands B and C, its top level with the grass.

   **If you do not see it:** the slab is a sphere. The mesh is not the built-in cube.

2. Copy `MovingPlatform.cpp` from this checkpoint, build, and attach it to `Platform` with `Travel` (0, 0, -6) and `Period` 8.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy the file, press **Ctrl+B**, select `Platform`, choose **Add Component ▸ Script** and pick `MovingPlatform`. Set `Travel` and `Period`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<Platform id>", "class": "MovingPlatform", "fields": { "Travel": [0, 0, -6], "Period": 8 } } }
   ```

   :::
   ::::

   **You should see:** the fields `Travel` (0, 0, -6) and `Period` 8 on the script.

   **If you do not see it:** the script is missing from the picker. The build failed: read the Console.

3. Play: run across the platform to island C.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Run from island B onto the platform, stand still for a moment and step off at the far end.
   :::
   :::tab[With a command]
   Start the game paused, step it a fixed number of steps and read the platform's position.

   ```json
   { "command": "play.start", "parameters": { "paused": true } }
   { "command": "play.step", "parameters": { "steps": 240 } }
   { "command": "component.get", "parameters": { "entity": "<Platform id>", "component": "Transform" } }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the platform at z = -24 after 4 s, which is 240 steps at 60 steps a second. The player rides it without sliding, and the camera does not shake.

   **If you do not see it:** the player slides back. The platform's body is not **Kinematic**, or a script moves it in `OnUpdate`.

:::::

::checkpoint{stage=7}

::figure{id=s7-platform}

## Add menus

A game needs a front door, a main menu with Play and Quit, then a pause menu and a way to leave the finished course. These are three scenes and three scripts, and they follow one rule.

The rule: a script that loads a scene holds the scene as an **asset field**, never as a path in a string. An asset field is a reference that the editor can see, so a :term[pruned export]{id=pruned-export} keeps the scene. A path in a string is invisible to the export, which leaves the file out, and the game loads nothing. The menu holds the course, the course holds the menu, and neither writes a path.

When the game switches scenes, every entity of the old scene is gone with its scripts' values, so the best time lives in a save file.

:::::steps

1. Make the main menu scene. Save the course, then choose **File ▸ New Scene** and save it as `Scenes/MainMenu.stscene` with **File ▸ Save Scene As...**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S**, then choose **File ▸ New Scene** and **File ▸ Save Scene As...**.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   { "command": "scene.new" }
   { "command": "scene.saveAs", "parameters": { "path": "Scenes/MainMenu.stscene" } }
   ```

   :::
   ::::

   **You should see:** an empty scene named `MainMenu`.

   **If you do not see it:** the editor asks about changes that you did not save. Save the course first.

2. Build the menu: a canvas `Menu`, a panel with a vertical layout and a title text and two buttons `Play` and `Quit`. [Menus](menus.md) taught this layout.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+**, choose **UI** and add the canvas, the panel, the vertical layout, one text and two buttons, and rename the buttons.
   :::
   :::tab[With a command]
   Each `ui.create` answers the `entity` it made, the `parent` of the next ones.

   ```json
   { "command": "ui.create", "parameters": { "type": "canvas", "name": "Menu" } }
   { "command": "ui.create", "parameters": { "type": "panel", "parent": "<Menu id>", "name": "Buttons", "anchor": "middleCenter", "size": [480, 360] } }
   { "command": "ui.create", "parameters": { "type": "verticalLayout", "parent": "<Buttons id>", "name": "Column", "anchor": "stretch" } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<Column id>", "name": "Title", "text": "Platformer", "size": [400, 80] } }
   { "command": "ui.create", "parameters": { "type": "button", "parent": "<Column id>", "name": "Play", "text": "Play", "size": [320, 64] } }
   { "command": "ui.create", "parameters": { "type": "button", "parent": "<Column id>", "name": "Quit", "text": "Quit", "size": [320, 64] } }
   ```

   This layout stretches its children across the panel; a `UILayout` added with `component.add` leaves them at the top left.
   :::
   ::::

   **You should see:** the title and the two buttons in a column on a dark scene, as wide as the panel.

   **If you do not see it:** a button sits outside the panel, or at its left edge. Drag it onto the layout, and make the layout with the **+** button, not with **Add Component**.

3. Copy `MainMenu.cpp` into `Scripts`: the script of [Menus](menus.md), in the folder `Scripts` of checkpoint 8's download. Build and attach it to the canvas. Set `Level` to the course scene, `Scenes/Course.stscene`, and set `Play Button` and each button's **Event Target**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Add Component ▸ Script** on the canvas and pick `MainMenu`. Drag the scene `Course` from the Content Browser onto `Level`, and `Play` onto `Play Button`. Select each button and set **Event Target** of its **UI Button** to the canvas.
   :::
   :::tab[With a command]
   Build, attach the script with the scene as an asset field, and set both buttons' :term[event target]{id=event-target}.

   ```json
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<Menu id>", "class": "MainMenu", "fields": { "Level": "Scenes/Course.stscene", "PlayButton": "<Play id>" } } }
   { "command": "component.set", "parameters": { "entities": [ "<Play id>", "<Quit id>" ], "component": "UIButton", "values": { "EventTarget": "<Menu id>" } } }
   ```

   :::
   ::::

   **You should see:** the field `Level` showing `Course`.

   **If you do not see it:** a click on **Play** does nothing. A button's **Event Target** is empty: the click then reaches only the button's own scripts.

4. Make the main menu the :term[start scene]{id=start-scene} of the game. With the menu open, choose **File ▸ Set as Start Scene**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Set as Start Scene**.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.setStartScene", "parameters": { "scene": "Scenes/MainMenu.stscene" } }
   ```

   :::
   ::::

   **You should see:** **Start Scene** on the page **Game** of **File ▸ Project Settings...** naming `MainMenu`.

   **If you do not see it:** the start scene is still `Course`. Open the settings page and choose it there.

:::::

The menu works with a gamepad as well. With nothing focused, the first direction press or Submit only focuses the first button. `MainMenu` focuses **Play** when the scene starts, so the first press already acts.

<!-- markdownlint-disable MD029 -->
:::::steps

5. Return to the course and make the pause menu: a second canvas with the sort order 10, a panel `PausePanel` and three buttons `Resume`, `Restart` and `MenuButton`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S** to save the menu, then open `Scenes/Course.stscene`. Add a canvas `Pause`, set **Sort Order** to 10, and add the panel with three buttons. Name the buttons with the names above, and set the **Text** of each button.
   :::
   :::tab[With a command]
   Save the menu, open the course, and make the canvas, the panel and its three buttons, one under the other.

   ```json
   { "command": "scene.save" }
   { "command": "scene.open", "parameters": { "scene": "Scenes/Course.stscene" } }
   { "command": "ui.create", "parameters": { "type": "canvas", "name": "Pause" } }
   { "command": "component.set", "parameters": { "entity": "<Pause id>", "component": "UICanvas", "values": { "SortOrder": 10 } } }
   { "command": "ui.create", "parameters": { "type": "panel", "parent": "<Pause id>", "name": "PausePanel", "anchor": "middleCenter", "size": [480, 360] } }
   { "command": "ui.create", "parameters": { "type": "button", "parent": "<PausePanel id>", "name": "Resume", "text": "Resume", "anchor": "topCenter", "position": [0, 60], "size": [320, 64] } }
   { "command": "ui.create", "parameters": { "type": "button", "parent": "<PausePanel id>", "name": "Restart", "text": "Restart", "anchor": "topCenter", "position": [0, 150], "size": [320, 64] } }
   { "command": "ui.create", "parameters": { "type": "button", "parent": "<PausePanel id>", "name": "MenuButton", "text": "Main Menu", "anchor": "topCenter", "position": [0, 240], "size": [320, 64] } }
   ```

   :::
   ::::

   **You should see:** the panel with three buttons over the HUD.

   **If you do not see it:** the pause panel hides behind the HUD. Its canvas needs the higher sort order.

6. Add `PauseMenu.cpp` of checkpoint 8's download to `Scripts`, build, and attach it to the `Game` entity with its fields. Set the **Event Target** of the three buttons to `Game`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Game`, choose **Add Component ▸ Script**, pick `PauseMenu`, and fill `Panel`, `Resume Button`, `Restart Button`, `Menu Button` and `Main Menu Scene`.
   :::
   :::tab[With a command]
   Then set the buttons' event target.

   ```json
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<Game id>", "class": "PauseMenu", "fields": { "Panel": "<PausePanel id>",
     "ResumeButton": "<Resume id>", "RestartButton": "<Restart id>", "MenuButton": "<MenuButton id>", "MainMenuScene": "Scenes/MainMenu.stscene" } } }
   { "command": "component.set", "parameters": { "entities": [ "<Resume id>", "<Restart id>", "<MenuButton id>" ], "component": "UIButton", "values": { "EventTarget": "<Game id>" } } }
   ```

   :::
   ::::

   **You should see:** the fields filled, and the scene `MainMenu` in `Main Menu Scene`.

   **If you do not see it:** the buttons do nothing. Each button needs **Event Target** set to `Game`, the entity with the script.

7. Give the completion panel two buttons, `PlayAgain` and `CompleteMenu`, and fill the fields of `CourseState`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add the two buttons under `Complete`, set **Event Target** to `Game`, and drag them onto `Play Again Button` and `Complete Menu Button` of `CourseState`. Drag the scene `MainMenu` onto `Main Menu Scene`.
   :::
   :::tab[With a command]
   Make the two buttons at the bottom of the panel, aim them at `Game`, then fill the three fields.

   ```json
   { "command": "ui.create", "parameters": { "type": "button", "parent": "<Complete id>", "name": "PlayAgain", "text": "Play Again", "anchor": "bottomCenter", "position": [-160, -40], "size": [280, 64] } }
   { "command": "ui.create", "parameters": { "type": "button", "parent": "<Complete id>", "name": "CompleteMenu", "text": "Main Menu", "anchor": "bottomCenter", "position": [160, -40], "size": [280, 64] } }
   { "command": "component.set", "parameters": { "entities": [ "<PlayAgain id>", "<CompleteMenu id>" ], "component": "UIButton", "values": { "EventTarget": "<Game id>" } } }
   { "command": "script.setField", "parameters": { "entity": "<Game id>", "class": "CourseState", "field": "PlayAgainButton", "value": "<PlayAgain id>" } }
   { "command": "script.setField", "parameters": { "entity": "<Game id>", "class": "CourseState", "field": "CompleteMenuButton", "value": "<CompleteMenu id>" } }
   { "command": "script.setField", "parameters": { "entity": "<Game id>", "class": "CourseState", "field": "MainMenuScene", "value": "Scenes/MainMenu.stscene" } }
   ```

   :::
   ::::

   **You should see:** a panel at the goal with two buttons, and the `Play Again` button focused.

   **If you do not see it:** the buttons do not react. Check the :term[event target]{id=event-target} again: it is the usual cause.

8. Play the menu and the course. Press **Esc** in the course and use the three buttons.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open `MainMenu`, press **Play**, click `Play`, press **Esc**, click `Resume`, press **Esc** again and click `Restart`.
   :::
   :::tab[With a command]
   Hold the Pause key with `press`, read the pause script and let go: a tap ends after fixed steps, and the paused game runs none.

   ```json
   { "command": "input.key", "parameters": { "key": "Escape", "action": "press" } }
   { "command": "script.get", "parameters": { "entity": "<Game id>", "class": "PauseMenu" } }
   { "command": "input.key", "parameters": { "key": "Escape", "action": "release" } }
   ```

   :::
   ::::

   **You should see:** the pause panel with the cursor free and the world still, the clock stopped, and `Resume` carrying the game on. `Restart` starts the course again, and the menu button returns to the main menu.

   **If you do not see it:** the world does not stop. The pause menu sets the :term[time scale]{id=time-scale} to 0 and the player script returns early when the delta time is 0.

:::::
<!-- markdownlint-enable MD029 -->

::checkpoint{stage=8}

::figure{id=s8-menus}

## Ship the game

An exported game starts in its start scene, the main menu, and loading a scene takes time. A :term[loading scene]{id=loading-scene} is a small scene that the game shows while the start scene loads. You make one with a bar that fills with the progress.

:::::steps

1. Make the scene `Scenes/Loading.stscene` with a canvas, a text `Label` and a filled image `Bar`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ New Scene**, then **File ▸ Save Scene As...** with `Scenes/Loading.stscene`. Add a canvas, an `Image` named `Bar` with **Type** `Filled` and a `Text` named `Label`.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.new" }
   { "command": "scene.saveAs", "parameters": { "path": "Scenes/Loading.stscene" } }
   { "command": "ui.create", "parameters": { "type": "canvas", "name": "Loading" } }
   { "command": "ui.create", "parameters": { "type": "image", "parent": "<Loading id>", "name": "Bar", "anchor": "bottomStretch", "position": [0, -60], "size": [-200, 24] } }
   { "command": "component.set", "parameters": { "entity": "<Bar id>", "component": "UIImage", "values": { "Type": "Filled", "FillAmount": 0 } } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<Loading id>", "name": "Label", "text": "Loading", "anchor": "bottomCenter", "position": [0, -100], "size": [600, 48] } }
   ```

   :::
   ::::

   **You should see:** a bar and a text on a dark scene.

   **If you do not see it:** the bar is a full rectangle. Its **Type** must be `Filled`, with the fill amount below 1.

2. Attach the script `LoadingScreen`: copy `LoadingScreen.cpp` from the folder `Scripts` of checkpoint 9's download (the same script as in [Levels, loading screens and save files](levels-saves.md)). Build, and set `Bar` and `Label`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy `LoadingScreen.cpp`, press **Ctrl+B**, add the script to the canvas and drag the two entities onto its fields.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<Loading id>", "class": "LoadingScreen", "fields": { "Bar": "<Bar id>", "Label": "<Label id>" } } }
   ```

   :::
   ::::

   **You should see:** the two fields filled. The script reads the progress of the scene switch and writes the bar and the text; the other page explains it.

   **If you do not see it:** the bar never moves in the editor. That is right: the editor plays one scene, and the bar moves only while a scene loads.

3. Choose it as the Export dialog's loading scene, and enable pruning.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the main menu, then choose **File ▸ Export Game...**. Pick a folder outside the project, choose `Loading` in **Loading scene**, tick `Leave out unused assets` and press **Export**.
   :::
   :::tab[With a command]
   Set the loading scene, then export pruned.

   ```json
   { "command": "project.setExportSettings", "parameters": { "loadingScene": "Scenes/Loading.stscene" } }
   { "command": "project.export", "parameters": { "directory": "<a folder outside the project>", "prune": true } }
   ```

   :::
   ::::

   **You should see:** the export bar reaching **Done**, and a folder with the program `Platformer`, its `.stgame` file, a pack, the :term[script module]{id=script-module} and `ThirdPartyNotices.md`.

   **If you do not see it:** the export refuses. A build runs, the folder lies inside the project, or the scene has changes that you did not save: the message names which.

4. Run the exported game from its folder.

   ::::tabs{sync=os}
   :::tab[Windows]

   Run the game windowed from PowerShell in the export folder.

   ```powershell
   .\Platformer.exe --windowed
   ```

   The game opens a window and runs until you close it.

   :::
   :::tab[Linux]

   ```sh
   ./Platformer --windowed
   ```

   The same call in a terminal opens the same window.

   :::
   :::tab[macOS]

   ```sh
   ./Platformer --windowed
   ```

   :::
   ::::

   **You should see:** the loading scene for a moment, then the main menu. Play, finish the course and see your best time again after you restart the game.

   **If you do not see it:** the game quits at once, or Play does nothing. A pruned export drops what no scene references: the game's log, `Game.log`, names a missing asset. Scenes held as asset fields stay in the pack.

:::::

::checkpoint{stage=9}

::figure{id=s9-export}

## Summary

- A character controller walks where the camera looks, turns the short way with `std::remainder`, jumps within the coyote time and teleports back to the last checkpoint after a fall.
- The script writes `Speed` and `Grounded` to the animator every update and sets `Jump` when it jumps; `Footsteps` plays a clip at each `Footstep` event.
- Coins, the goal and the pads find the `Game` entity or the player at each event, and `CourseState` keeps the count, the clock and the best time in a save file.
- A scene the game loads is an asset field, never a path: a pruned export keeps only what scenes and fields reference.
- A pruned export with a loading scene runs without the editor.

## Check yourself

1. The player stands at yaw 350 degrees and walks toward a target of 90 degrees. What does `std::remainder(target - yaw, 360.0f)` return, and why is it better than the plain difference?

   :::answer{tests="player-controls"}
   The call returns 100 degrees. The plain difference is -260, which turns the long way round through 180. The remainder gives the difference in the range from -180 to 180, so the body turns the short way.
   :::

2. A player walks off a ledge at 3 m/s and presses Jump 0.1 s later. Does the jump work, and how far did the player walk?

   :::answer{tests="player-controls"}
   The jump works, because 0.1 s is less than the coyote time of 0.15 s. The player walked 3 × 0.1 = 0.3 m past the edge.
   :::

3. The robot walks in the air above the island and never leaves the Idle pose on the ground. Which two parameters does the player script write every update, and which one is set only at a jump?

   :::answer{tests="animator-driven"}
   The script writes `Speed` and `Grounded` every update. `Jump` is a trigger that it sets only when the player jumps, and the controller consumes it when its transition fires.
   :::

4. A coin script keeps a pointer to `CourseState` in a member, found once in `OnCreate`. After a hot reload the pointer points to memory that moved. What does the page do instead, and why?

   :::answer{tests="one-state"}
   The coin finds the `Game` entity by name and its script at each event, and keeps nothing. A found script is valid at that moment, and a kept one may be stale after a reload or a scene change.
   :::

5. The menu stores the course scene as the string `"Scenes/Course.stscene"` and loads it by that path. The game works in the editor and shows a black window when exported pruned. Why, and what is the fix?

   :::answer{tests="scene-fields,ship-pruned"}
   The pruning follows references of scenes and fields, and a string is no reference, so the pack omits the scene. Make the scene an asset field of the script, as `Level` is, or add it to the list of assets that the export settings :term[always include]{id=always-include}.
   :::

## Exercises

1. **Basic.** Add a lantern with shadows to the course: a point light of a warm colour over the first gap, that casts shadows. Why does the light need a short range?

   :::answer[Worked solution]{tests="one-state" solution="tutorials/make/project-platformer/exercise-1.tutorial.json"}
   The solution opens the course and makes an entity with a `PointLight` whose `CastShadows` is on, at (2, 2.5, -9). A shadow-casting light costs more than one without shadows, and its range bounds what it must draw, so a range of 12 m keeps the cost small.
   :::

2. **Medium.** Add the Graphics row of the sample's settings screen to the pause menu: four toggles in one group that set the quality preset. Which two calls does a click make?

   :::answer{tests="scene-fields"}
   A click on a toggle that switches on calls `Graphics::SetPreset` with the preset of that toggle, then `Graphics::Save` to keep it for the next run. The script reads the change in `OnUIValueChanged(Entity widget, float value)` and ignores a value of 0, because switching the others off sends events too.

   ```cpp pseudocode
   void OnUIValueChanged(Entity widget, float value) override
   {
   	if (value == 0.0f)
   		return;
   	Graphics::SetPreset(PresetOf(widget));
   	Graphics::Save();
   }
   ```

   The return skips the toggles that switch off.

   :::

3. **Hard.** Write a :term[command script]{id=command-script} that plays the course. It waits for the colliders and runs the player forward for a time. It places the player at a coin and at the goal, and expects the coin counted and the course completed. Why must it wait before its first input?

   :::answer{tests="ship-pruned"}
   Play holds the simulation until the course's meshes are cooked: input sent earlier runs while nothing moves. The script pauses and repeats `physics.stats` until `/waitingForMeshes` is false.

   ```json
   [ { "command": "play.start" },
     { "command": "play.pause", "parameters": { "paused": true } },
     { "command": "physics.stats", "expect": { "/waitingForMeshes": { "equals": false } }, "until": { "seconds": 300 } },
     { "command": "entity.find", "parameters": { "name": "Player" }, "bind": { "player": "/entities/0" } },
     { "command": "entity.find", "parameters": { "name": "Game" }, "bind": { "game": "/entities/0" } },
     { "command": "input.sequence", "parameters": { "steps": 40, "events": [ { "step": 0, "action": "Gameplay/Move", "mode": "press", "value": [0, 1] }, { "step": 30, "action": "Gameplay/Move", "mode": "release" } ] } },
     { "command": "component.set", "parameters": { "entity": { "$ref": "player" }, "component": "Transform", "values": { "Translation": [0, 1, -12] } } },
     { "command": "script.get", "parameters": { "entity": { "$ref": "game" }, "class": "CourseState" }, "expect": { "/scripts/0/fields/Coins": { "min": 1 } }, "until": { "steps": 60 } },
     { "command": "play.stop" } ]
   ```

   The goal works alike, at (2, 6.1, -40), with `/scripts/0/fields/Completed` true.

   :::

## Where it lives in Strata

- The player and the sample's other scripts: `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp`, `JumpPad.cpp`, `Coin.cpp`, `Goal.cpp` and `CourseState.cpp`.
- The sample's scenes and prefabs: `Samples/ThirdPerson/Assets/Scenes/` and `Samples/ThirdPerson/Assets/Prefabs/`.
- The command that makes a controller: `StrataEditor/src/Editor/EditorAnimationCommands.cpp`.
- The input map and the pruned export: `Samples/ThirdPerson/ThirdPerson.stproj` and `StrataEditor/src/Editor/GameExport.cpp`.
- The regression of the sample, a command script that plays the menu and the course: `StrataTests/Editor/ThirdPersonCommands.json.in`.

## Further reading

- The README of the sample, `Samples/ThirdPerson/README.md`: the controls and how the sample was made (beginner).
- Kenney's asset pages, kenney.nl: the kit and the sounds in the public domain (beginner).
- Game Programming Patterns by Robert Nystrom: the chapters on the game loop and the state pattern (intermediate).
