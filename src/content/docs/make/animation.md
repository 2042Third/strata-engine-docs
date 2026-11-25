---
id: make/animation
title: "Animation for game makers"
description: "Bring the Third-Person robot into your course: idle, walk, run, jump, footsteps and a flag in its hand, all driven by a controller and a script."
kind: tutorial
size: L
tracks: [G]
needs: [make/characters-cameras]
time: 120
learn:
  - id: anim-words
    text: explain what a skeleton, a clip, a skin, an animator and an animation controller each do for a character
  - id: build-controller
    text: build a controller with parameters, states and transitions in the Asset tab and read its live state in the Inspector
  - id: drive-script
    text: write a script that drives an animator's parameters from a character's movement
  - id: events-attach
    text: add animation events for footsteps and attach an entity to a joint
  - id: motion-culling
    text: choose when to use root motion and when to let an animator skip unseen characters
since: 0.3.0
status: final
---

## What you will make

Your player is still a capsule that slides over the course. You replace it with the robot of the Third-Person sample. The robot idles, walks, runs, jumps, plays a sound at each step and holds a flag.

::figure{id=result}

## Skeletons, clips and skins

A character that moves is made of three things that work together. Each has a name, and the rest of the page uses all three.

A **skeleton** is a tree of named points that stand for the body: a hip, a spine, an arm, a hand.

Each point of a skeleton is a **joint**. A joint has a position, a rotation and a size relative to the joint above it, so turning the shoulder carries the elbow and the hand with it. The robot has dozens of joints.

A **clip** is a recorded motion: for every joint, a list of poses at moments in time. One clip is a walk, another a jump. The clip lasts a fixed number of seconds, and the game plays it forward, and again from the start if it loops.

A **skin** ties the mesh to the skeleton: each vertex of the mesh follows one or more joints. When the joints move, the skin bends the mesh with them, as a sleeve follows an arm. Without a skin the mesh would stay rigid.

## Animators and controllers

Something has to choose which clip plays now. The **Animator** is the component that does so, on the entity at the top of the model. It holds the skeleton, and it plays either one clip or the states of a controller.

An **animation controller** is an asset, a file with the extension `.stanimator`, that lists what the Animator may play and when it changes.

A **state** is one thing the character can be doing, such as Idle or Walk. A state plays one clip, loops or not, at a speed.

A **transition** is a rule to leave one state for another when conditions hold. For example, leave Idle for Walk when the speed is above 0.1 metres a second.

## Parameters and cross-fades

The conditions of a transition test values that your code sets. A **parameter** is a named value the controller keeps: a float such as `Speed`, an on-off value such as `Grounded`, or a trigger.

A **trigger parameter** is a parameter that you set once like a button press, and that stays set until a transition uses it. Jump is a good example: the press happens in one frame, and the jump may start a frame later.

A **cross-fade** is the blend that a transition performs. During it the weight of the new state grows from 0 to 1 while the old one shrinks, so the pose never jumps.

:::example
A transition from Idle to Walk with a cross-fade of 0.15 s starts when `Speed` rises above 0.1. After 0.075 s the weights are 0.5 and 0.5, so the pose is half Idle and half Walk. After 0.15 s the weights are 0 and 1, and Idle stops. At 60 frames per second the fade takes 9 frames.
:::

```mermaid caption="The controller you build: Idle, Walk and Run change on the speed, and a Jump trigger leads from any state to Jump, which returns by exit time." alt="Boxes for Idle, Walk, Run and Jump. Arrows connect Idle and Walk and Walk and Run, labelled with speed tests. An arrow from a box named Any State to Jump is labelled Jump trigger, and arrows from Jump return to Idle and Walk."
flowchart LR
	I[Idle] -->|"Speed > 0.1"| W[Walk]
	W -->|"Speed < 0.1"| I
	W -->|"Speed > 4.5"| R[Run]
	R -->|"Speed < 4.5"| W
	A[Any State] -->|"Jump trigger"| J[Jump]
	J -->|"exit time, grounded"| I
	J -->|"exit time, grounded, moving"| W
```

## What you need

- The end of the [characters and cameras tutorial](characters-cameras.md): the course, the player and the follow camera.
- The robot model `RobotExpressive.glb` (Creative Commons Zero, credited in `Samples/ThirdPerson/CREDITS.md`) and the four step sounds, which you import from the release in the first step.
- The controller `Animations/Player.stanimator`, which only the downloads of this page hold. Download Checkpoint 1, at the end of the first section, and copy the folder `Assets/Animations` of its project, with the controller and its `.meta` file, into your project's `Assets` folder. Copy nothing else: the first section's steps make the rest.
- The file `flag.glb` and its folder `Textures` from the release's `Samples/ThirdPerson/Assets/Models/Platformer/` (Kenney, Creative Commons Zero (:term[CC0]{id=cc0})). You import the file in the seventh section, and the import takes the folder along.
- About two hours.

Each checkpoint offers the project as it is at that point, and the editor commands that lead there from the checkpoint before. Use one or the other. A commands file writes no file: before you run one, copy the script file that its section names from that checkpoint's project into your `Scripts` folder. A commands file that imports from the release names the folder `<release folder>`: replace it with the folder you unpacked Strata into.

No menu or button of the editor creates an animation controller. The command `animation.createController` made `Player.stanimator` for the checkpoint. The page [Commands](commands.md) shows how you run such a command yourself.

## Put the robot under the player

The model you imported holds the skeleton, the clips and the skin as :term[sub-assets]{id=sub-asset} below the model file. Placing the model makes an entity tree, and its root gets an Animator that plays the first clip of the file. You place it under the player, so that the :term[character controller]{id=character-controller} moves the robot with the capsule.

:::::steps

1. Import the folder `Robot` of the release's `Samples/ThirdPerson/Assets/Models/` into your `Models` folder, and the folder `Footsteps` of `Samples/ThirdPerson/Assets/Sounds/` into `Sounds`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Import each folder as in [Assets](assets.md), and wait for the import bar to finish.
   :::
   :::tab[With a command]
   Replace `<release folder>` with the folder you unpacked Strata into. Each command answers when its import is done.

   ```json
   { "command": "asset.import", "parameters": { "directories": [ "<release folder>/Samples/ThirdPerson/Assets/Models/Robot" ], "directory": "Models" } }
   { "command": "asset.import", "parameters": { "directories": [ "<release folder>/Samples/ThirdPerson/Assets/Sounds/Footsteps" ], "directory": "Sounds" } }
   ```

   :::
   ::::

   **You should see:** `Models/Robot/RobotExpressive.glb` and the folder `Sounds/Footsteps` with four sounds in the Content Browser.

   **If you do not see it:** the import failed, and the Console names the file. Check the folder you named.

2. Open the Content Browser, find `Models/Robot/RobotExpressive.glb` and expand it with the arrow beside its name.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The sub-assets appear below the model: a skeleton, a clip for each motion and the meshes.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command. It lists the clips and the skeleton of the model.

   ```json
   { "command": "animation.info", "parameters": { "asset": "Models/Robot/RobotExpressive.glb" } }
   ```

   :::
   ::::

   **You should see:** clips named Idle, Walking, Running and Jump among about a dozen others.

   **If you do not see it:** the model is not imported yet. Do step 1, and wait for the import bar to finish.

3. Drag the model into the Scene view, then drag the new entity onto `Player` in the Hierarchy.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the entity and set **Position** to 0, 0, 0, **Rotation** Y to 180 and **Scale** to 0.4 in the Inspector. Rename it `Robot` and delete the capsule below the player.
   :::
   :::tab[With a command]
   Place the model turned and scaled. The command returns the new entity's `id`.

   ```json
   { "command": "asset.place", "parameters": { "asset": "Models/Robot/RobotExpressive.glb", "point": [0, 0, 0], "rotation": [0, 180, 0], "scale": 0.4 } }
   ```

   A parameter such as `parent` takes an `id`, not a name: `entity.find` with the name `Player` returns the player's. Move the robot under it, then rename it.

   ```json
   { "command": "entity.setParent", "parameters": { "entity": "<the id from asset.place>", "parent": "<the player's id>", "keepWorldTransform": false } }
   ```

   The rename gives the name that later commands find.

   ```json
   { "command": "entity.rename", "parameters": { "entity": "<the id from asset.place>", "name": "Robot" } }
   ```

   The capsule below the player is named `Body`: `entity.find` with that name returns its `id`. Delete it.

   ```json
   { "command": "entity.delete", "parameters": { "entities": [ "<the capsule's id>" ] } }
   ```

   :::
   ::::

   **You should see:** the robot stands where the capsule stood, with its feet on the ground and its back to the camera. The Inspector may then read the rotation as X 180, Y 0, Z 180: the same turn, written another way.

   **If you do not see it:** the robot is far larger than the player. The model is about four metres tall, so a scale of 0.4 is needed, as in the sample.

4. Select the Robot entity and find its **Animator** component in the Inspector.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The **Skeleton** field holds the model's skeleton, and **Clip** holds the first clip of the file.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.get", "entityName": "Robot", "parameters": { "component": "Animator" } }
   ```

   :::
   ::::

   **You should see:** a robot in a rest pose, arms out, because nothing plays while you edit. Open the camera menu of the Scene view and choose **First frame of their animation** under **Characters while editing**: the robot now shows the first frame of its Clip, a dance start.

   **If you do not see it:** the robot is a heap of parts at the origin. The entity has no **Skeleton**; place the model again.

:::::

The robot's face has three expressions made of morph targets. The importer does not import morph targets, so the face stays neutral.

::checkpoint{stage=1}

::figure{id=robot-placed}

## Give it a controller and watch it

The Animator in step 4 plays one clip in a loop. A controller gives it states. The file `Animations/Player.stanimator`, which you copied from the checkpoint, has one state, Idle, that plays the robot's Idle clip, and no parameters.

:::::steps

1. Select the Robot entity and set the **Controller** field of its Animator to `Animations/Player.stanimator`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag the file from the Content Browser onto the field, or click the field and choose the file. The **Clip** field turns grey, because the controller's states choose the clips.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "entityName": "Robot", "parameters": { "component": "Animator", "values": { "Controller": "Animations/Player.stanimator" } } }
   ```

   :::
   ::::

   **You should see:** the field holds `Player`, and **Clip** is grey with a reason in its tooltip.

   **If you do not see it:** you chose the clip or the model instead of the controller. Only a file of the type animation controller fits the field.

2. Press **Play** and select the Robot entity.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Below the Animator's fields the Inspector draws its live state: the **State**, the **Time** and, when a controller has parameters, a list of **Parameters**.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   ```

   Then `animation.info` with the Robot's `entity` answers what the Inspector draws: `state`, and `normalizedTime` for **Time**. Its `clip` still names the component's **Clip**, which is unused while a controller plays.
   :::
   ::::

   **You should see:** the robot breathes and shifts in its Idle loop. **State** reads `Idle`, and **Time** counts up past 1.00 and keeps counting, one for each loop.

   **If you do not see it:** the robot stays in its rest pose. A character shows what is available: until the skeleton, the controller and the clips are loaded it stands in the bind pose, the pose the mesh was made in. If the skeleton fails to load it stays there for good and the log says why once. If the controller fails to load the component's **Clip** plays instead, and a state whose clip fails to load shows the rest pose.

:::::

The sample's robot has a larger controller than yours. Read it as data, because it is the one you are about to rebuild by hand. The first part is its Walk state, a clip that loops at normal speed with two events at 0.02 s and 0.5 s into the clip.

```json src="Samples/ThirdPerson/Assets/Animations/Robot.stanimator#L36-L51"
{
	"Clip": "57D5825B3AB8DCFD",
	"Events": [
		{
			"Name": "Footstep",
			"Time": 0.019999999552965164
		},
		{
			"Name": "Footstep",
			"Time": 0.5
		}
	],
	"Loop": true,
	"Name": "Walk",
	"Speed": 1.0
},
```

1. **Line 37:** the clip the state plays, as an :term[asset handle]{id=asset-handle}.
2. **Lines 38–47:** the two Footstep events, in seconds into the clip.
3. **Line 48:** the clip loops.
4. **Line 49:** the state's name, which scripts and transitions use.

The sample's controller has five parameters: `Speed` and `Grounded`, and the triggers `Jump`, `Wave` and `Dance`. The next section builds `Speed`; the sections after it add `Grounded` and `Jump`.

::checkpoint{stage=2}

::figure{id=controller-live}

## Make it walk and run

You add everything in the Asset tab. Select `Player.stanimator` in the Content Browser, and the Asset tab shows three tables: **Parameters**, **States** and **Transitions**.

:::::steps

1. Click **Add Parameter** above the Parameters table, and rename the new row `Speed`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   A new row called `Parameter` appears, of type Float with a default of 0. Edit its **Name** cell to `Speed`.
   :::
   :::tab[With a command]
   The command `animation.setController` replaces whole sections of a controller. This one gives it the float parameter.

   ```json
   { "command": "animation.setController", "parameters": { "controller": "Animations/Player.stanimator",
     "parameters": [ { "Name": "Speed", "Type": "Float", "Default": 0 } ] } }
   ```

   :::
   ::::

   **You should see:** one row, `Speed`, in the Parameters table.

   **If you do not see it:** the Asset tab shows a model instead. Select the file `Player.stanimator`, not the Robot entity.

2. Click **Add State** twice and name the new states `Walk` and `Run`. Choose a clip in each **Clip** cell: Walking for Walk and Running for Run.

   ::::tabs{sync=how}
   :::tab[In the editor]
   **Add State** adds a state without a clip, named `State`. Each row has a **Name**, a **Clip**, a **Speed**, a **Loop** box and an **Events** cell.
   :::
   :::tab[With a command]
   Run the states as one command. Take the clip handles from the `animation.info` listing of step 2 of the first section.

   ```json
   { "command": "animation.setController", "parameters": { "controller": "Animations/Player.stanimator",
     "states": [ { "Name": "Idle", "Clip": "<Idle clip handle>" },
       { "Name": "Walk", "Clip": "<Walking clip handle>" },
       { "Name": "Run", "Clip": "<Running clip handle>" } ] } }
   ```

   :::
   ::::

   **You should see:** three rows, Idle, Walk and Run, with the clips named in their cells and **Loop** ticked.

   **If you do not see it:** a state has no clip. A state without a clip plays the rest pose, so the robot would stand stiffly while the state is active.

3. Click **Add Transition**, then set **From** to `Idle`, **To** to `Walk`, **Conditions** to `Speed > 0.1` and **Fade** to 0.15.

   ::::tabs{sync=how}
   :::tab[In the editor]
   **Add Transition** adds a row between the first two states, with no condition and a fade of 0.25. The **Conditions** cell takes text: you compare a float (`Speed > 0.1`), write an on-off value by its name (`Grounded`, or `!Grounded` for false), and separate several conditions with `,`.
   :::
   :::tab[With a command]
   Run the transitions as one command.

   ```json
   { "command": "animation.setController", "parameters": { "controller": "Animations/Player.stanimator",
     "transitions": [
       { "From": "Idle", "To": "Walk", "Duration": 0.15, "Conditions": [ { "Parameter": "Speed", "Mode": "Greater", "Threshold": 0.1 } ] },
       { "From": "Walk", "To": "Idle", "Duration": 0.2, "Conditions": [ { "Parameter": "Speed", "Mode": "Less", "Threshold": 0.1 } ] },
       { "From": "Walk", "To": "Run", "Duration": 0.2, "Conditions": [ { "Parameter": "Speed", "Mode": "Greater", "Threshold": 4.5 } ] },
       { "From": "Run", "To": "Walk", "Duration": 0.2, "Conditions": [ { "Parameter": "Speed", "Mode": "Less", "Threshold": 4.5 } ] } ] } }
   ```

   :::
   ::::

   **You should see:** one row, `Idle` to `Walk`, with the condition text `Speed > 0.1` and a fade of 0.15.

   **If you do not see it:** the robot walks as soon as you press **Play**, with no speed at all. A transition with no condition and no exit time fires in the first update of its state, so the state it leaves hardly plays. The new row has no condition until you type one.

4. Click **Add Transition** three more times. Set each row to match the diagram above: Walk to Idle on `Speed < 0.1`, Walk to Run on `Speed > 4.5`, Run to Walk on `Speed < 4.5`, each with a fade of 0.2.

   **You should see:** four rows in the Transitions table. Walk leaves in two directions, so the speed test decides.

   **If you do not see it:** a row sits between Idle and Walk twice. **Add Transition** always starts from the first two states, so change **From** and **To** after each click.

:::::

The thresholds suit the sample's player: it walks at 3 m/s and runs at 6.5 m/s. The value 4.5 lies between the two speeds, so each speed settles in one state.

::checkpoint{stage=3}

::figure{id=tables-walk-run}

## Drive it from a script

Nothing sets `Speed` yet, so the robot idles forever. A script does it. The script sets the parameters from what the character controller of the player does, every frame, as the Third-Person player does.

:::question
The script is C++, a language this page does not teach. The pages [Classes and objects](../basics/programming-3.md) and [Classes and inheritance](../basics/cpp-classes.md) explain what each line below means.
:::

The script belongs on the Player entity, not on the robot. The robot has the Animator, so the script keeps a field that names the robot. This listing reads the speed of the player on the ground, ignoring up and down, and passes it with the grounded state to the Animator.

```cpp src="book:tutorials/make/animation/PlayerAnimation.cpp#L5-L18"
class PlayerAnimation : public Script
{
public:
	Entity Robot; // The model with the Animator

	void OnUpdate(float) override
	{
		const CharacterController controller = GetEntity().GetCharacterController();
		const glm::vec3 velocity = controller.GetVelocity();
		Animator animator = Robot.GetAnimator();
		animator.SetFloat("Speed", glm::length(glm::vec2(velocity.x, velocity.z)));
		animator.SetBool("Grounded", controller.IsGrounded());
	}
};
```

1. **Line 5:** `Script` is the :term[base class]{id=base-class} of every script, and `OnUpdate` runs every frame.
2. **Line 8:** `Entity Robot` is a field of type entity: you choose its value in the Inspector.
3. **Lines 12–13:** the controller reports its velocity, and the script keeps the horizontal part of it.
4. **Lines 14–16:** `GetAnimator()` gives the animator of the robot, and `SetFloat` and `SetBool` write the parameters by name.

:::::steps

1. Add a script named `PlayerAnimation` to the project and replace its code with the file `PlayerAnimation.cpp` of this page's checkpoint download.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Content Browser choose **New** and make a script named `PlayerAnimation`, replace its code, and press **Play** to build.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** a build without errors in the :term[Problems panel]{id=problems-panel}.

   **If you do not see it:** the Problems panel names a line. A mistake in one name, such as `SetFlaot`, shows there.

2. Select the Player entity, add the script `PlayerAnimation` and set its `Robot` field to the Robot entity. Set the `WalkSpeed` of its `PlayerController` to 3, the walking speed of the sample's player. At the 5 m/s of the last page the player moves faster than 4.5 m/s, and the robot would run at once.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Add Component** and **Script**, pick the class, and drag the Robot entity from the Hierarchy onto the `Robot` field. Type 3 into the `WalkSpeed` field of `PlayerController`.
   :::
   :::tab[With a command]
   `entity.find` with the name `Robot` returns the robot's `id`, which the field takes.

   ```json
   { "command": "script.add", "entityName": "Player", "parameters": { "class": "PlayerAnimation", "fields": { "Robot": "<the Robot's id>" } } }
   ```

   The script is on the player now, with its field set. The second command slows the player to a walk.

   ```json
   { "command": "script.setField", "entityName": "Player", "parameters": { "class": "PlayerController", "field": "WalkSpeed", "value": 3 } }
   ```

   :::
   ::::

   **You should see:** the field shows `Robot`. Until step 3 adds `Grounded`, the log reports that the animator has no parameter `Grounded`; `Speed` works already. In Play mode, the robot idles while you stand and walks while you move, and the Inspector's **State** changes between `Idle` and `Walk`.

   **If you do not see it:** the robot never walks and the log says `'Player' has no Animator component`. The field is empty or names the player, so `GetAnimator()` asked an entity without an Animator. Name the Robot entity.

3. Add the parameter `Grounded` for the next section: in the Asset tab click **Add Parameter**, name it `Grounded`, set its **Type** to `Bool` and tick its default.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The default of a `Bool` is a check box in the **Default** column.
   :::
   :::tab[With a command]
   Add it to the parameter list with `animation.setController`, repeating `Speed`.

   ```json
   { "command": "animation.setController", "parameters": { "controller": "Animations/Player.stanimator",
     "parameters": [ { "Name": "Speed", "Type": "Float", "Default": 0 }, { "Name": "Grounded", "Type": "Bool", "Default": true } ] } }
   ```

   :::
   ::::

   **You should see:** two parameters in the table, and in Play mode both appear in the Inspector's **Parameters** list.

   **If you do not see it:** the log reports a problem with `SetBool`. A call for a parameter the controller lacks, or one of another type, fails and logs.

:::::

Walk on the course. Run only appears when the player moves faster than 4.5 m/s, so raise its **WalkSpeed** to 6.5 to see the second fade, and set it back to 3.

::checkpoint{stage=4}

::figure{id=speed-live}

## Jump from any state

A jump can start while walking or standing, so a transition from Any State leads to it. The jump is a trigger, and the robot leaves the Jump state by an exit time rather than by a condition on a parameter alone.

:::::steps

1. Add a trigger parameter `Jump` and a state `Jump` that plays the Jump clip with **Loop** off.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **Add Parameter** and set the new row's **Type** to Trigger. Click **Add State**, name it `Jump`, choose the Jump clip and clear **Loop**.
   :::
   :::tab[With a command]
   The command `animation.setController` replaces each list you give, so give the complete lists.

   ```json
   { "command": "animation.setController", "parameters": { "controller": "Animations/Player.stanimator",
     "parameters": [ { "Name": "Speed", "Type": "Float" }, { "Name": "Grounded", "Type": "Bool", "Default": true }, { "Name": "Jump", "Type": "Trigger" } ],
     "states": [ { "Name": "Idle", "Clip": "<Idle clip handle>" }, { "Name": "Walk", "Clip": "<Walking clip handle>" },
       { "Name": "Run", "Clip": "<Running clip handle>" }, { "Name": "Jump", "Clip": "<Jump clip handle>", "Loop": false } ] } }
   ```

   :::
   ::::

   **You should see:** a fourth state, Jump, with **Loop** cleared.

   **If you do not see it:** a jump that loops repeats until its exit time fires. The sample's Jump state does not loop.

2. Add a transition with **From** `Any`, **To** `Jump`, **Conditions** `Jump` and **Fade** 0.1. Add two more from `Jump`: to `Idle` with conditions `Grounded, Speed < 0.1`, and to `Walk` with `Grounded, Speed > 0.1`, each with **Exit** ticked at 0.4 and a fade of 0.15.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Any** in the **From** cell of the first new row. The exit box and its **Exit** time sit between **Conditions** and **Fade**; ticking the box sets the time to 1, so type 0.4.
   :::
   :::tab[With a command]
   The command replaces the whole list, so give the four transitions of the last section with the three new ones. `"AnyState": true` stands for **From** `Any`.

   ```json
   { "command": "animation.setController", "parameters": { "controller": "Animations/Player.stanimator",
     "transitions": [
       { "AnyState": true, "To": "Jump", "Duration": 0.1, "Conditions": [ { "Parameter": "Jump", "Mode": "Set" } ] },
       { "From": "Idle", "To": "Walk", "Duration": 0.15, "Conditions": [ { "Parameter": "Speed", "Mode": "Greater", "Threshold": 0.1 } ] },
       { "From": "Walk", "To": "Idle", "Duration": 0.2, "Conditions": [ { "Parameter": "Speed", "Mode": "Less", "Threshold": 0.1 } ] },
       { "From": "Walk", "To": "Run", "Duration": 0.2, "Conditions": [ { "Parameter": "Speed", "Mode": "Greater", "Threshold": 4.5 } ] },
       { "From": "Run", "To": "Walk", "Duration": 0.2, "Conditions": [ { "Parameter": "Speed", "Mode": "Less", "Threshold": 4.5 } ] },
       { "From": "Jump", "To": "Idle", "Duration": 0.15, "ExitTime": 0.4, "Conditions": [ { "Parameter": "Grounded", "Mode": "True" }, { "Parameter": "Speed", "Mode": "Less", "Threshold": 0.1 } ] },
       { "From": "Jump", "To": "Walk", "Duration": 0.15, "ExitTime": 0.4, "Conditions": [ { "Parameter": "Grounded", "Mode": "True" }, { "Parameter": "Speed", "Mode": "Greater", "Threshold": 0.1 } ] } ] } }
   ```

   :::
   ::::

   **You should see:** the Transitions table lists the Any State row and the two rows from Jump, each with its exit box ticked.

   **If you do not see it:** the robot stays in Jump for good. A transition leaves Jump only when all its conditions hold and 0.4 of the clip has passed. A condition that never holds keeps the robot there.

3. Replace the script's code with the file `PlayerAnimationJump.cpp` of the checkpoint, build, and press **Play**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The new lines set the trigger on the frame the player leaves the ground while moving up.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** when the player jumps, the robot plays its jump. The Inspector's **State** shows the old state, an arrow and `Jump` during the fade, then `Jump`, then the state it returns to.

   **If you do not see it:** the robot jumps again and again after one press. A trigger stays set until a transition that tests it fires. Set it once, on the frame of the jump, and never every frame.

:::::

The lines that changed compare this update's grounded state with the last one's, and set the trigger only on the update that leaves the ground.

```cpp src="book:tutorials/make/animation/PlayerAnimationJump.cpp#L14-L19"
const bool grounded = controller.IsGrounded();
Animator animator = Robot.GetAnimator();
// Set the trigger once, on the update the player leaves the ground going up.
if (m_WasGrounded && !grounded && velocity.y > 0.5f)
	animator.SetTrigger("Jump");
m_WasGrounded = grounded;
```

Without the `m_WasGrounded` memory the script would set the trigger in every update of the jump.

::checkpoint{stage=5}

::figure{id=jump-live}

## Add footsteps

A footstep must sound when a foot touches the ground, and that moment sits inside the clip. An **animation event** is a named marker at a time in a state's clip. The Animator reports it to the scripts of its entity when the clip's time passes the marker.

:::::steps

1. In the Asset tab, set the **Events** cell of Walk to `Footstep@0.02, Footstep@0.5` and the cell of Run to `Footstep@0.28, Footstep@0.76`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The text is a list of `Name@seconds`. The times are those of the sample's controller, which were read off the clips' foot keys.
   :::
   :::tab[With a command]
   The events are part of the states in `animation.setController`, so give the four states again with the events of Walk and Run.

   ```json
   { "command": "animation.setController", "parameters": { "controller": "Animations/Player.stanimator",
     "states": [ { "Name": "Idle", "Clip": "<Idle clip handle>" },
       { "Name": "Walk", "Clip": "<Walking clip handle>", "Events": [ { "Name": "Footstep", "Time": 0.02 }, { "Name": "Footstep", "Time": 0.5 } ] },
       { "Name": "Run", "Clip": "<Running clip handle>", "Events": [ { "Name": "Footstep", "Time": 0.28 }, { "Name": "Footstep", "Time": 0.76 } ] },
       { "Name": "Jump", "Clip": "<Jump clip handle>", "Loop": false } ] } }
   ```

   :::
   ::::

   **You should see:** the two cells show the text you typed.

   **If you do not see it:** an event never fires. A time past the length of its clip is never reached, and nothing warns: a 1.2 s clip never fires an event at 2 s.

2. Add the script `Footsteps` to the Robot entity: add the file `Footsteps.cpp` of this page's checkpoint download to your `Scripts` folder, build, and fill its four fields `Step1` to `Step4` with the step sounds.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the Robot entity, choose **Add Component**, **Script**, `Footsteps`, and drag a clip from `Sounds/Footsteps` into each field.
   :::
   :::tab[With a command]

   Build first with `script.build`, then add the script with its four fields.

   ```json
   { "command": "script.add", "entityName": "Robot", "parameters": { "class": "Footsteps", "fields": {
     "Step1": "Sounds/Footsteps/Grass1.ogg", "Step2": "Sounds/Footsteps/Grass2.ogg",
     "Step3": "Sounds/Footsteps/Grass3.ogg", "Step4": "Sounds/Footsteps/Grass4.ogg" } } }
   ```

   :::
   ::::

   **You should see:** in Play mode a step sound at each foot contact, at a slightly different pitch every time.

   **If you do not see it:** nothing sounds because the script is on the player. Only scripts on the animator's own entity receive its events, so the script on the player hears nothing, and nothing warns.

:::::

The script is short. It asks for its four clips in `OnCreate`, so none is missing at the first step, and it picks one at random with a random pitch in `OnAnimationEvent`.

```cpp src="Samples/ThirdPerson/Scripts/Footsteps.cpp#L22-L37"
void OnCreate() override
{
	for (const AssetHandle clip : GetClips())
		Assets::RequestLoad(clip);
}

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

1. **Lines 24-25:** `OnCreate` requests the four clips at once, so that they are loaded before the first step.
2. **Line 28:** `OnAnimationEvent` runs for each event of the robot's Animator, with the name of the event.
3. **Line 30:** an event with another name returns at once.
4. **Lines 33-35:** one of four clips is chosen, and `Audio::PlayOneShotAt` plays it at the robot's position with a pitch from 0.9 to 1.1.

::checkpoint{stage=6}

::figure{id=footsteps-script}

## Hold a flag

A character may hold an object. **AttachToJoint** is a component that keeps its entity at a joint of an animator's skeleton, so the object follows the hand. It writes the entity's translation, rotation and scale every update, so a shift, a turn or a size of your own would be replaced.

For that reason you build two entities: a holder that is attached with no offset, and a child that carries the offset. The sample's menu robot does the same.

:::::steps

1. Import `flag.glb` into `Models`, then place the flag in the scene away from the robot. The import makes the folder `Models/flag` for the model and copies its `Textures` folder into it, because the model reads its colours from there.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag the file from the release's folder into the `Models` folder of the Content Browser, then drag `Models/flag/flag.glb` into the Scene view.
   :::
   :::tab[With a command]
   Import the file from the release, with `<release folder>` replaced, then place it. The import answers once it is done, so the place finds the model.

   ```json
   { "command": "asset.import", "parameters": { "file": "<release folder>/Samples/ThirdPerson/Assets/Models/Platformer/flag.glb", "directory": "Models" } }
   { "command": "asset.place", "parameters": { "asset": "Models/flag/flag.glb", "point": [3, 0, 0] } }
   ```

   A file that you copy into `Assets` by hand is found a moment later, not at once: until then `asset.place` answers that there is no such asset. Run `asset.info` with the file's path until it answers without an error, then place it.
   :::
   ::::

   **You should see:** a small flag on a pole in the Scene view.

   **If you do not see it:** the flag is black or blue. Its colours come from `Textures/colormap.png`, which lies beside `flag.glb` in the release, so import the release's file and not a copy without the folder.

2. Create an empty entity `FlagHolder` and add the **Attach To Joint** component: **Animator** is the Robot entity and **Joint** is "Palm2.R", the right palm. Leave its transform at its default.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create an empty entity in the Hierarchy, rename it, then choose **Add Component** and **Attach To Joint**. Drag the Robot entity onto **Animator** and type the joint name.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "FlagHolder", "components": { "AttachToJoint": { "Animator": "<the Robot's id>", "Joint": "Palm2.R" } } } }
   ```

   :::
   ::::

   **You should see:** in Play mode the empty entity moves with the right hand of the robot.

   **If you do not see it:** the holder stays where it is. The **Joint** field is a typed name that nothing checks, so a wrong name leaves the entity in place with no warning. Copy the name from the skeleton in the Asset tab.

3. Make the flag a child of `FlagHolder` and set its **Position** to 0, 0.008, 0, its **Rotation** X to 180 and its **Scale** to 0.035.

   **You should see:** in Play mode the robot holds the flag in its right hand, and the flag follows the hand during a walk.

   **If you do not see it:** the flag sticks out or lies at a strange angle. The offset, the turn and the scale belong on the child; the update replaces the holder's own values.

:::::

A script reaches the same place with `GetJointTransform`, which returns the position, rotation and scale of a joint. The component is the better choice for two reasons. A script runs before the Animation system in the update, so it reads the pose of the update before. A joint that gameplay reads also depends on the camera: while an Animator on **When Visible** is unseen, its pose stands still. The last section returns to that.

::checkpoint{stage=7}

::figure{id=flag-hand}

## Let the animation move the character

**Root motion** is the movement that a clip itself carries, such as the steps of a walk that moves the root joint forward. With **Apply Root Motion** on, the Animator moves its entity by that movement, instead of a script moving it at a fixed speed.

The movement reaches a character controller only when the Animator and the controller are on the same entity. The course's robot sits below the player, so root motion on it does not move the capsule. You build a second robot whose root carries a controller.

The robot's clips carry no travel, though. In every one of them the root joint ends where it starts, so the robot can only walk on the spot. You build the setup that a moving clip needs and see what the setting does with a clip that stays in place. The page [Root motion](../animation/root-motion.md) follows a clip that travels.

:::::steps

1. Duplicate the Robot entity, move the copy out from below the player to a free place of the course, and add a **Character Controller** to it with the player's settings.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the Robot, press **Ctrl+D**, drag the copy out of the Player in the Hierarchy and set its **Position**. Choose **Add Component** and **Character Controller**.
   :::
   :::tab[With a command]
   `entity.duplicate` with the Robot's `id` returns the copy's `id`; the copy is named `Robot (1)`. Move it to the top level, set its position, and add the component.

   ```json
   { "command": "entity.duplicate", "parameters": { "entity": "<the Robot's id>" } }
   ```

   The copy hangs below the player beside the Robot. A `parent` of `null` moves it to the top level.

   ```json
   { "command": "entity.setParent", "parameters": { "entity": "<the copy's id>", "parent": null } }
   ```

   The point -3, 0, 5 lies between the crate and the wall, away from the player's path.

   ```json
   { "command": "component.set", "entityName": "Robot (1)", "parameters": { "component": "Transform", "values": { "Translation": [-3, 0, 5] } } }
   ```

   The controller takes the player's height, radius and step height.

   ```json
   { "command": "component.add", "entityName": "Robot (1)", "parameters": { "component": "CharacterController", "values": { "Height": 1.8, "Radius": 0.3, "StepHeight": 0.35 } } }
   ```

   :::
   ::::

   **You should see:** a second robot with a capsule outline in the Scene view.

   **If you do not see it:** the copy still hangs below the player and moves with it. The controller must be on the root of the second robot, the entity with the Animator.

2. In the Animator of the second robot, clear **Controller**, set **Clip** to the Walking clip and tick **Apply Root Motion**. Press **Play**.

   **You should see:** the second robot walks on the spot. Its legs step, but its root joint ends each loop where it began, so the clip gives the controller no distance to walk.

   **If you do not see it:** the robot idles instead of walking. **Controller** still names a controller, and while it does, the controller's states play and **Clip** is unused; clear it.

:::::

With a clip that travels, the second robot would walk forward, and its controller would stop it at a wall. On the player's robot the same clip would move only the model, away from its capsule and through walls, because that robot has no controller of its own.

Leave root motion off when a script decides where the character goes, as the Third-Person sample does. The player there moves by input at a speed the designer chose, and the animation only follows it. Use root motion when the clip's own steps should set the distance, so that feet do not slide.

::checkpoint{stage=8}

::figure{id=second-robot}

## Animate only what is seen

A hundred characters on screen cost a hundred poses every frame. The **culling mode** of an Animator is its setting for that. **Always Animate**, the default, poses the skeleton every frame. **When Visible** poses it only while a :term[renderer]{id=renderer} draws its mesh or its shadow. Time, events, transitions and root motion continue, so gameplay does not depend on the camera; only the pose stands still.

:::::steps

1. Set **Culling Mode** of the second robot to "When Visible", keeping its Walking clip and root motion.

   **You should see:** the field reads "When Visible".

   **If you do not see it:** you changed the first robot. That robot cannot show the effect: the follow camera looks at it all the time, so it is always seen.

2. Press **Play**, turn the follow camera away from the second robot so that it and its shadow leave the view, wait a few seconds, then turn back.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Turn the camera with the Look action of your project.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command to let game time pass while you hold the camera away.

   ```json
   { "command": "play.step", "parameters": { "steps": 120 } }
   ```

   :::
   ::::

   **You should see:** when you turn back, the robot is posed again and walks on. Its clip's time ran while it was out of view; only its pose stood still.

   **If you do not see it:** the robot is posed all the time. The robot or its shadow is still in the view, and a seen shadow counts.

:::::

### What Strata's animation does not do

Strata's animation plays states with cross-fades. It has no blend trees, which mix clips by a parameter, and no animation layers, which play two parts of the body at once. It has no inverse kinematics, which places a hand on a given point, and the importer skips the morph targets that a face uses. It does not compress clips. The page [Limits of animation](../animation/limits.md) lists these in full.

The pages [Skeletons](../animation/skeletons.md), [Clips](../animation/clips.md), [Skinning](../animation/skinning.md), [State machines](../animation/state-machines.md), [Blending](../animation/blending.md), [Time and events](../animation/time-events.md) and [Root motion](../animation/root-motion.md) describe how the engine does each part.

::checkpoint{stage=9}

::figure{id=culling}

## Summary

- A skeleton of joints, clips that move them and a skin that bends the mesh make a character; an Animator plays a controller's states.
- You built a controller in the Asset tab with parameters, states and transitions, and read its live state in the Inspector.
- A script drives the parameters from the character controller every frame, through the animator of the robot entity.
- Animation events play the footsteps on the robot's own entity, and AttachToJoint holds a flag on a holder entity.
- Root motion needs a clip that travels and the controller on the Animator's entity, and When Visible poses only what is seen.

## Check yourself

1. A character has a skeleton, a clip and a skin. What does each one do?

   :::answer{tests="anim-words"}
   The skeleton is the tree of joints. The clip stores the motion of those joints over time. The skin ties the mesh to the joints so that it bends with them.
   :::

2. A transition from Idle to Walk has no condition and no exit time. When does the robot leave Idle?

   :::answer{tests="build-controller"}
   In the first update of the state, so Idle hardly plays. Give the transition a condition such as `Speed > 0.1`.
   :::

3. Your script calls `GetAnimator()` on the player, and the log says `'Player' has no Animator component`. What is wrong?

   :::answer{tests="drive-script"}
   The Animator is on the robot, below the player. Add an entity field that names the robot, and call `GetAnimator()` on it.
   :::

4. The footsteps are silent. The script `Footsteps` is on the player, and the events are set. Why?

   :::answer{tests="events-attach"}
   Only scripts on the animator's own entity receive its events. Move the script to the robot.
   :::

5. The second robot has its own controller and **Apply Root Motion** ticked, yet it walks on the spot. Why?

   :::answer{tests="motion-culling"}
   The Walking clip carries no travel: its root joint ends each loop where it began. Root motion moves the entity only as far as the root joint travels, so the clip itself must move forward.
   :::

## Exercises

1. **Basic.** Add a Crouch state to your controller. It plays a clip of your choice while a `Bool` parameter `Crouching` is true. Undo the change with **Ctrl+Z**.

   :::answer[Worked solution]{tests="build-controller" solution="tutorials/make/animation/exercise-1.tutorial.json"}
   Click **Add Parameter**, name it `Crouching` and set its type to `Bool`. Click **Add State**, name it `Crouch`, choose the clip, and add two transitions with the conditions `Crouching` and `!Crouching`. **Ctrl+Z** removes each step in turn.

   The download's commands file makes the whole change with one `animation.setController`, which is one undo step. Its `edit.undo` then removes that step only, the latest edit, and the controller has three parameters, four states and seven transitions again. The earlier steps of the course stay, and the command `edit.history` still lists them.
   :::

2. **Medium.** Make the robot wave when you press a key and the robot stands still. Which parameter type do you use, and what does a parameter that stays set cause?

   :::answer[Answer]{tests="drive-script"}
   Use a trigger parameter `Wave`, a transition from Idle on it, and an exit time back to Idle. A trigger that nobody consumes stays set and fires later, so reset it with `ResetTrigger` where the wave must not start.
   :::

## Where it lives in Strata

The components are in `Strata/src/Strata/Animation/AnimationComponents.h`, and the controller's data in `Strata/src/Strata/Animation/AnimationController.h`. The script's `Animator` is in `StrataScriptCore/Include/StrataScript/Animator.h`. The sample's controller, scripts and scenes are in `Samples/ThirdPerson/`. The Asset tab's tables are in `StrataEditor/src/UI/AnimationAssetViews.cpp`.

## Further reading

- The glTF 2.0 specification, sections on skins and animations: how a model file stores joints and clips (advanced).
- Quaternius' free model packs: the source of the robot (beginner).
