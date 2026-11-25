---
id: animation/problem
title: "The animation problem"
description: "Why a game cannot store every vertex of every frame, the four ways engines animate a model, and why Strata chose skeleton animation plus rigid parts."
kind: concept
size: S
tracks: [E]
needs: [world/scene-graph]
time: 25
learn:
  - id: name-kinds
    text: name the four kinds of animation and what each one stores
  - id: choose-strata
    text: choose the kind Strata uses for a character and explain why it fits
  - id: compute-price
    text: compute the bytes of a clip stored per vertex against stored as joint keys
  - id: trace-pose
    text: trace a pose from the model file to the screen on the map of the part
since: 0.3.0
status: final
---

Open the Third-Person sample and run the robot across the course of floating islands. In one second it plants a foot, swings an arm, bends a knee and lands again. The entity that is the robot barely moves: its transform changes by a few numbers each frame. Yet thousands of vertices are in new places. The animation problem is to produce those new places for every frame, cheaply and from data an artist can make.

## Storing every vertex of every frame is too large

The first idea is to record the answer: save the position of every vertex for every frame of the clip, and replay the frames. The robot's meshes hold 7,214 vertex positions. A position is three numbers of 4 :term[bytes]{id=byte}, so 12 bytes, and one frame of the robot costs 86,568 bytes. A one-second run at 24 :term[frames per second]{id=frame-rate} costs 2,077,632 bytes, about 2 MB, for one clip of one character.

The sample uses six clips, and a game has many characters. The data also cannot react: a robot that turns its head toward you needs a new recording for every angle. Recording the result is the wrong thing to store. Store the cause: a few numbers per frame, and a rule that turns them into vertex positions.

## Animation changes the shape, not the place

Moving the entity is the part you already know. Your scene graph (see [the scene graph](../world/scene-graph.md)) gives each entity a transform, and a child follows its parent. Animation is different: it bends a model in place, while the entity stays where the :term[game logic]{id=game-logic} put it. In the sample, the character controller moves the robot and the animation never does.

The mental model has three parts. Data, a clip or a set of weights, changes with time. A rule turns that data into a pose, the shape of the model for this frame. The :term[renderer]{id=renderer} draws the pose. Strata keeps the three apart, and each approach below differs in what the data is.

```mermaid caption="Animation turns a small amount of changing data into the many vertex positions that are drawn in one frame." alt="A flow from a few numbers that change with time, through a rule, to thousands of vertex positions and then to the drawn frame."
flowchart LR
    A["Few numbers per frame"] --> B["Rule: build a pose"]
    B --> C["Thousands of vertex positions"]
    C --> D["Drawn frame"]
```

The diagram shows why the problem is about data size: the left box must stay small while the right box stays large.

## Four approaches, each from the flaw of the one before

**Vertex animation** is the naive answer made practical: store baked vertex positions per frame, in a file or in a texture the vertex :term[shader]{id=shader} reads. It plays back exactly what an artist or a simulation made, and it costs the bytes computed above. Games use it where the cost is acceptable or the motion cannot be described by joints: crowds that share one baked loop, and cloth or water recorded from a simulation.

The flaw is size, so the next approach stores a few shapes. A **morph target** (also called a **blend shape**) is a copy of a mesh with some vertices moved, stored as offsets from the base mesh. The game blends targets with weights: 0.0 is the base, 1.0 the full target, and the result is the base plus each weight times its offsets. A face needs only a few targets (smile, frown, blink). The flaw is that morphing cannot rotate a limb: halfway between "arm up" and "arm down" is a shrunken arm, not a swinging one.

Rotation is what a hierarchy does well. A **rigid hierarchy** splits the character into parts, such as a head, a torso and an upper arm, and puts each part on a node of a tree, the way the scene graph does. Animating the tree animates the parts. The flaw shows at a joint: the parts do not bend, so an elbow either leaves a gap or shows the two parts cutting through each other.

**Skeleton animation** fixes the flaw. A skeleton is a tree of joints, a few dozen of them. The clip stores keys for the joints only: a key is a joint's rotation or position at one moment, and between two keys the engine blends the values. Each vertex follows several joints, each with a weight, so the surface bends smoothly. [Skeletons](skeletons.md) and [skinning](skinning.md) teach the two halves.

| Approach | Memory | Quality | Authoring work | Used for |
| --- | --- | --- | --- | --- |
| Vertex animation | Largest: every vertex of every frame | Exact replay | A bake from a tool or a simulation | Crowds, cloth bakes |
| Morph targets | Small: a few offset copies | Good for faces, wrong for limbs | Sculpting each target | Faces |
| Rigid hierarchy | Smallest: keys of a few nodes | Visible seams at joints | Modeling parts that overlap at joints | Robots, vehicles, props |
| Skeleton animation | Small: keys of a few dozen joints | Smooth bending | Rigging, with weights per vertex | Characters, creatures |

:::example[Pricing the robot's run with joint keys]
The robot's file stores the running clip as keys as 336 rotation keys and 72 translation keys, over 24 frames. A key holds a time of 4 bytes and a value. A rotation is four numbers of 4 bytes, so a rotation key is 20 bytes; a translation has three, so 16 bytes.

The clip costs $336 \times 20 + 72 \times 16 = 6{,}720 + 1{,}152 = 7{,}872$ bytes, under 8 KB. The recorded frames cost 2,077,632 bytes. The ratio is $2{,}077{,}632 / 7{,}872 \approx 264$: the keys are about 264 times smaller, and they can still be blended and changed by code.
:::

## Strata uses skeleton animation and rigid parts on joints

Strata animates models with skeletons and clips, and lets a rigid part ride on a joint. The robot is both: most of its parts, the torso, the arms and the legs, are rigid meshes, and only its hands are skinned to joints. Strata keeps the rigid parts as entities that follow a joint through an `AttachToJoint` component. The menu robot holds its flag the same way.

:::why[Why skeletons and not morph targets?]
A character needs rotating limbs, and skeletons give them at a small cost in memory. Morph targets would add a second system for faces only. The glTF importer reports morph targets among the features it skipped, so the robot's three face expressions are not played and its face stays neutral. The cost is real: no facial animation until a later version.
:::

The robot is the running example of this part. Its model is `RobotExpressive.glb`, released as CC0 (public domain). Its controller, `Robot.stanimator`, has the parameters Speed, Grounded, Jump, Wave and Dance and six states: Idle, Walk, Run, Jump, Wave and Dance. The Walk and Run states carry Footstep events at the foot contacts.

Three scripts drive it. `ThirdPersonPlayer.cpp` sets Speed and Grounded every frame and triggers Wave, Dance and Jump from input. `Footsteps.cpp` plays a step sound when a Footstep event arrives. `MenuRobot.cpp` alternates the Dance and Wave triggers for the menu robot.

The course's chests also animate: each plays one looping clip without a controller, and its body and lid ride on two joints. The Open World sample's foxes use the controller `Fox.stanimator`.

### The map of the part

The next diagram follows one pose from the file to the screen. Each box is a page of this part, and the two side branches leave the main path at the Animation system.

```mermaid caption="The path of a pose: a file is imported, a controller picks clips, the Animation system builds a pose and a shader moves the vertices, while root motion and events leave as side branches." alt="A chain of boxes from the glTF file to the vertex shader. Root motion and events branch off at the Animation system."
flowchart LR
    F["glTF file"] --> I["Importer"]
    I --> S["Skeleton and clips"]
    S --> C["Controller (.stanimator)"]
    C --> A["Animation system"]
    A --> P["Pose service"]
    P --> R["Render scene palettes"]
    R --> V["Vertex shader"]
    A -. "root motion" .-> T["Transform or character control"]
    A -. "events" .-> E["Scripts: OnAnimationEvent"]
```

Read the pages in the order of the boxes. [Importing animated models](importing.md) covers the importer, [clips](clips.md) the clips, and [state machines](state-machines.md) the controller. [The Animation system](system.md) builds the pose and hands it to the pose service, which other parts of the engine ask for it. A palette is the list of a pose's joint matrices that the vertex shader reads, and [skinning](skinning.md) turns palettes into moved vertices, [root motion](root-motion.md) moves the entity, and [time, loops and events](time-events.md) covers the events.

## What this choice cannot do

Strata does not play morph targets, so faces stay neutral. Its other absences, such as blend trees and inverse kinematics, are in [what Strata's animation does not do yet](limits.md) and [what Strata does not do](../appendix/not-in-strata.md). To animate a character in the editor step by step, follow [animating a character](../make/animation.md).

## Common mistakes

- **Thinking that animation means moving the entity.** Symptom: you write code that changes the robot's transform to swing its arm, and nothing bends. Fix: the entity moves through physics or the character controller, and the animation changes the pose of the joints.
- **Storing a clip as vertex positions because it is the simplest.** Symptom: one clip takes millions of bytes and cannot blend with another. Fix: store keys for joints.
- **Expecting a model's face to change.** Symptom: the robot never smiles. Fix: Strata skips morph targets; the importer says so.

## Summary

- The four kinds are vertex animation (baked positions), morph targets (offsets blended by weights), rigid hierarchies (parts on nodes) and skeleton animation (joints that move vertices).
- Strata uses skeleton animation, plus rigid parts that follow joints, because characters need rotating limbs at a small size; morph targets are not imported.
- A clip as joint keys is hundreds of times smaller than the same clip as vertex positions.
- A pose travels from the file through the importer, the controller, the Animation system, the pose service and the palettes to the vertex shader.

## Check yourself

1. Which approach stores offsets from a base mesh and blends them with weights?
   (a) Vertex animation. (b) Morph targets. (c) A rigid hierarchy. (d) Skeleton animation.

   :::answer{tests="name-kinds"}
   (b). Vertex animation (a) stores whole positions per frame, not offsets blended by weights. A rigid hierarchy (c) and skeleton animation (d) store transforms of nodes or joints.
   :::

2. A friend says the robot should run by changing its entity's transform each frame. What is wrong?

   :::answer{tests="choose-strata"}
   The transform places the whole entity, and nothing inside it bends. Running needs the legs and arms to change shape in place, which a skeleton's joints do; Strata moves the entity through the character controller.
   :::

3. A clip has 100 rotation keys and no translation keys. How many bytes do its keys take, with the sizes of this page?

   :::answer{tests="compute-price"}
   A rotation key is 4 bytes of time plus 16 bytes of value, 20 bytes. 100 keys take 2,000 bytes.
   :::

4. In the map, which box comes directly before the vertex shader?

   :::answer{tests="trace-pose"}
   The render scene's palettes. The pose service gives the palettes their joint transforms, and the shader reads the palettes to move the vertices.
   :::

## Exercises

1. **Basic.** Choose an approach for each: a crowd of 500 identical pedestrians walking one loop, a face that blinks, a car's wheels, a human-shaped enemy.

   :::answer[Worked solution]{tests="name-kinds,choose-strata"}
   The crowd can use vertex animation, because one baked loop is shared and the cost is paid once. The blink fits a morph target. The wheels are rigid parts on nodes of the car. The enemy needs skeleton animation, since its limbs rotate.
   :::

2. **Medium.** Price two clips of the robot, once as every vertex of every frame and once as joint keys. The sketch holds the counts that the file gives; run it, then change a clip's numbers and predict the output.

   :::question
   The sketch uses loops, a struct and function calls: see [programming 1](../basics/programming-1.md), [programming 2](../basics/programming-2.md) and [programming 3](../basics/programming-3.md).
   :::

   The program multiplies the positions by the frames for the naive price, and adds up the keys for the joint price. Look at the ratio.

   :::answer[Worked solution]{tests="compute-price" solution="sketches/animation-problem-pricing.cpp"}
   The program below prices each clip both ways and prints the sizes and their ratio; look at how the two prices grow with the frame count.

   ```cpp sketch="animation-problem-pricing.cpp"
   // Prices two of the robot's clips: every vertex of every frame, against the keys of its joints.
   #include <cstdio>

   struct ClipKeys
   {
   	const char* Name = "";
   	int Frames = 0;
   	int RotationKeys = 0;
   	int TranslationKeys = 0;
   };

   int main()
   {
   	const long long positionBytes = 7214 * 12; // 7,214 positions of three 4-byte floats
   	const ClipKeys clips[] = { { "Walking", 24, 336, 120 }, { "Idle", 81, 405, 81 } };
   	for (const ClipKeys& clip : clips)
   	{
   		const long long naiveBytes = positionBytes * clip.Frames;
   		// A key holds its time (4 bytes) and a value: 4 floats for a rotation, 3 for a translation.
   		const long long keyBytes = clip.RotationKeys * (4 + 16) + clip.TranslationKeys * (4 + 12);
   		const double ratio = static_cast<double>(naiveBytes) / static_cast<double>(keyBytes);
   		std::printf("%s: naive %lld bytes, keys %lld bytes, ratio %.1f\n", clip.Name, naiveBytes, keyBytes, ratio);
   	}
   	return 0;
   }
   ```

   ```text output-of="animation-problem-pricing.cpp"
   Walking: naive 2077632 bytes, keys 8640 bytes, ratio 240.5
   Idle: naive 7012008 bytes, keys 9396 bytes, ratio 746.3
   ```

   1. **Line 14:** one position is three floats of 4 bytes, so 12 bytes for every vertex.
   2. **Line 15:** the counts are the transform keys the glTF file holds for each clip.
   3. **Line 18:** the naive price grows with the frame count.
   4. **Line 20:** the joint price grows with the key count only, not with the vertex count.

   Walking prices 86,568 bytes by 24 frames against 8,640 bytes of keys. Idle has more frames, 81, so the naive price grows to about 7 MB, while its keys stay near 9 KB.
   :::

## Where it lives in Strata

- `Samples/ThirdPerson/Assets/Models/Robot/RobotExpressive.glb` is the robot, and `Samples/ThirdPerson/Assets/Animations/Robot.stanimator` its controller.
- `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp`, `Samples/ThirdPerson/Scripts/Footsteps.cpp` and `Samples/ThirdPerson/Scripts/MenuRobot.cpp` drive it.
- `Samples/OpenWorld/Assets/Animations/Fox.stanimator` is the foxes' controller.
- `Strata/src/Strata/Asset/GltfImporter.cpp` reports morph targets as skipped.
- `Strata/src/Strata/Animation/AnimationSystem.h` is the Animation system.
- The command `animation.info` reports a model's joints and a clip's duration, channels and keys.

## Further reading

- The glTF 2.0 specification, sections on skins, animations and morph targets (intermediate): the file format the robot comes in.
- Jason Gregory, Game Engine Architecture, the chapter on animation systems (advanced): rigid, morph and skeleton animation in engines.
