---
id: animation/limits
title: "What Strata's animation does not do yet"
description: "The animation features other engines offer and Strata lacks, how engines build them, and what Strata gives instead."
kind: concept
size: S
tracks: [E]
needs: [animation/system]
time: 20
learn:
  - id: absences
    text: name the animation features Strata does not provide and what it offers in their place
  - id: phase
    text: compute where a run clip must start to match the foot of a walk clip it fades from
  - id: morph
    text: find the importer's warning about skipped morph targets in the Console and in the code
  - id: additive
    text: add an additive flag to states on paper and place its work in the evaluation
since: 0.3.0
status: final
---

You have used an engine where a character walks, jogs and sprints smoothly as you push a stick further. The speed
is one number, and the animation follows it. You open Strata's :term[animation controller]{id=animation-controller-state-machine} and search for the same thing: a
blend tree, a place to put a speed number and have walk and run mixed for you. You find states, transitions and
:term[cross-fades]{id=cross-fade}, and nothing else.

This page lists what you will not find, one absence at a time. Each paragraph says what the feature is, how engines
usually provide it, and what Strata offers now.

## Where a feature hides when it is missing

The first guess is that every engine has every feature somewhere, under a different name. You search for "blend",
"layer" or "kinematics" in the editor and in the documents. When nothing turns up, you suspect your own search.

At the pin, a search of the folder `Strata/src/Strata/Animation/` for blend trees, blend spaces, inverse kinematics,
compression and masks finds nothing. A search for "layer" finds one comment about the Scene layer. Searches for
additive clips, :term[sync markers]{id=sync-markers}, curves, :term[inertialization]{id=inertialization}, motion matching, :term[retargeting]{id=retargeting} and dual :term[quaternions]{id=quaternion} find nothing
either. The code, not the interface, tells you what is missing.

## The shape of what Strata does

Strata's animation is a short chain. An animator plays up to four clips at once. Each clip is sampled at its own
time, the samples are summed with weights that add up to one, and the result is a pose for the skeleton. The vertex
:term[shader]{id=shader} then moves each vertex with that pose.

```mermaid caption="Each absence on this page is a missing stage, or a fixed choice inside a stage that exists." alt="A chain of five boxes: clips, sampling, weighted sum, skeleton pose and skinning in the vertex shader, with the absences named under the stage where they would enter."
flowchart LR
    A["Clips: raw keys, binding by name"] --> B["Sample each playing entry, at most four"]
    B --> C["Weighted sum, weights add to 1"]
    C --> D["Skeleton pose"]
    D --> E["Skinning in the vertex shader"]
    N1["No compression"] -.-> A
    N2["No sync markers, no curves"] -.-> B
    N3["No trees, layers, additive clips"] -.-> C
    N4["No IK, no ragdoll"] -.-> D
    N5["No morph targets, no compute or dual quaternion skinning"] -.-> E
```

A feature other engines add sits on one dashed line, and the main chain stays as
it is. The function that does the middle stages is `Evaluate`, and the last exercise of this page changes it.

## How engines build each feature

Engines solve each problem in a few well-known ways. The table gives the usual answer, what it costs and where it
appears. Further reading lists the sources.

| Feature | The usual answer | Cost | Seen in |
| --- | --- | --- | --- |
| Blend trees | A node mixes clips by one or two parameters | Several samples per animator | Unity, Godot, Unreal |
| Layers and masks | Each layer is its own blend; a mask of joints limits it | One more pose per layer | Unity, Godot, Unreal |
| Additive clips | A clip stores the difference from a reference pose | A reference, and care with rotations | Unity, Unreal |
| Inverse kinematics (IK) | A routine bends a joint chain to reach a target | Needs the ground or target from the world | Unity, Unreal, open libraries |
| Morph targets | Stored vertex offsets mixed by weights | Memory per target, a vertex pass | glTF files, major engines |
| :term[Clip compression]{id=clip-compression} | Keys are rounded to fewer bits or fitted by curves | Error to measure and control | open libraries, Unreal |
| Compute skinning | One compute pass skins each mesh once per frame | A buffer per skinned mesh | Many engines |

## What Strata's choice cannot do

Controllers are state machines whose transitions cross-fade, and a cross-fade mixes up to four clips (`c_MaxPlaying`
in `AnimatorInstance`).

:::why[Why a short chain first?]
A pose that is a weighted sum of samples is simple to test, and each animator can be evaluated on its own in a job.
Layers or IK mix poses in other ways, and need rules about order and about what each stage sees. Strata built the part
every game needs first, and listed the rest as later work.
:::

### Blend trees and blend spaces

A blend tree turns one number, such as speed, into weights over several clips. Strata has no such node. A transition
starts a cross-fade between two states with a duration you choose, and the weights move over time, not with a
parameter. For a character that must change pace smoothly, use one state per pace with short cross-fades, or write a
script that picks the state.

### Layers and masks

In other engines an upper-body layer can aim a rifle while the legs run. Strata has one state machine per animator and
no joint masks. Its cross-fade mixes whole poses. To act on the upper body alone, a game needs clips that already hold
the whole motion.

### Additive clips, sync markers, curves, inertialization and motion matching

An additive clip stores a difference, such as a breathing sway, to add on any pose. Sync markers name a moment in a
cycle, such as a foot landing, so two cycles can line up. A float curve is a value over time that belongs to no joint,
such as a door's glow.

Inertialization hides a jump by letting the difference decay. Motion matching picks the best frame
of a large library every few frames. Strata has none of these.

The walk-to-run slide shows why they matter. Suppose a walk cycle lasts 1.0 s, with the left foot landing at 0.0 s,
and a run cycle lasts 0.6 s, with the left foot landing at 0.0 s too. A transition fires when the walk is at 0.25 s, a
quarter of the way through its cycle. The run starts at 0.0 s, so one clip lifts the foot while the other plants it, and
the feet slide for the length of the fade.

Phase matching starts the run at the same share of its cycle: 0.25 of 0.6 s
is 0.15 s, and the feet agree. Strata starts every state at its beginning, so the slide stays unless you cut the clips
to line up. The Third-Person sample's robot shows it between its walk and its run.

### Inverse kinematics

**Inverse kinematics** finds the joint angles that put a hand or foot at a target, which keeps feet on sloped
ground. Strata has no such routine. Poses come from clips and nothing corrects them against the world.

### Ragdolls

A **ragdoll** turns a character into physics bodies joined by constraints, so it falls limp. Strata's physics has no
joints at all (see [Why games need physics](../physics/why.md)), so nothing can join the bodies.

### Morph targets

A morph target is a stored set of vertex offsets, mixed by weights, that moves a face without bones. The glTF :term[file
format]{id=file-format} carries them. Strata's :term[importer]{id=importer} reports them as skipped, both on meshes and as animated weights, and the robot's
faces do not arrive. A face has to move through joints or through separate meshes.

### Clip compression

Strata keeps keys as raw 32-bit floats. It removes keys that :term[interpolation]{id=interpolation} of their neighbours reproduces (keyframe
reduction, see [Clips](../animation/clips.md)) and shares key times between channels. It does not round keys to fewer
bits or fit curves. The plan document lists compressed clips for later, if measured to help.

### Retargeting beyond names

A clip binds to a skeleton by joint name, and a joint of the skeleton that no channel of the clip names keeps its :term[rest pose]{id=rest-pose}.
Strata has no mapping between differently named or proportioned skeletons. Clips for another character need matching
joint names.

### Compute and dual quaternion skinning

Strata skins in the vertex shader of each draw with linear blend skinning (see [Skinning](../animation/skinning.md)). It
has no pass that skins a mesh once per frame, which would help when the mesh is drawn many times. It has no dual
quaternion skinning either, which avoids the pinched volume at twisted joints.

### A skeleton overlay

The viewport draws no bones. Only the Asset tab's joint tree shows the joints, as a list. To see a skeleton in the
scene you draw lines yourself (see [Debug drawing](../gpu/debug-drawing.md)).

### What the plan lists

The wave 9 entries of `Docs/Roadmap.md` name the next steps for animation. They are plans, not promises, and no date
stands behind them.

The entry `animation-runtime-2` names, among other items, a blend by two parameters (Blend2D), additive clips, float
curves, IK for two-bone chains and feet grounded through `IPhysicsQueries`, and compressed clips if measured to help.
The same list names `animation-tools` (a node canvas, a clip editor for events and sync markers, a mask editor).
It also names nodes for ragdolls, which wait for work on physics joints. At the pin the code holds none of it. The general list of what
Strata omits is in [What Strata does not do](../appendix/not-in-strata.md).

:::example[Find the skipped morph targets]
Import the robot, open the **Console** and search for "Not imported". You read two warnings: one for morph targets and
one for morph target animation. In `Strata/src/Strata/Asset/GltfImporter.cpp` the importer collects each feature it
skips and reports every one as "Not imported: ...". The lines that note the skipped morph targets are 1378 and 1379,
and the weight channels of an animation stop at 1637 to 1640. Exercise 1 does this step by step.
:::

## Common mistakes

- **Searching the interface for a feature under another name.** Symptom: an hour in the editor without a result. Fix:
  search the folder for the technique, as the second section did.
- **Expecting a cross-fade to line up feet.** Symptom: sliding feet in a walk-to-run transition. Fix: cut the clips so
  their cycles start in step, or choose a shorter fade so the slide lasts less time.
- **Taking the plan for a schedule.** Symptom: a game design that needs IK next month. Fix: treat wave 9 entries as
  ideas, and build what you need from what exists.

## Summary

- Strata offers cross-fades of up to four entries, keyframe reduction, binding by name and vertex shader skinning;
  blend trees, layers, masks, additive clips, IK, ragdolls, morph targets and compression are absent.
- A cross-fade starts every state at its beginning, so clips of different cycles slide: a walk 0.25 s into its 1.0 s
  cycle needs a 0.6 s run that starts at 0.15 s.
- The importer warns "Not imported: morph targets" and "Not imported: morph target animation" in the Console.
- An additive state needs a flag, a reference pose, a place after the weighted sum in `Evaluate`, and a rule that keeps
  it out of the weights that add up to one.

## Check yourself

1. A game needs the legs to keep running while the arms aim. Which Strata feature does that?
   - A. An animation layer with an arm mask.
   - B. A blend tree.
   - C. None of them: Strata has one state machine per animator and no masks.

   :::answer{tests="absences"}
   C. Layers with masks and blend trees belong to other engines, so A and B name features Strata lacks.
   :::

2. A walk cycle lasts 1.2 s and a run cycle 0.8 s. A transition fires with the walk at 0.3 s. Where must a phase-matched
   run clip start?

   :::answer{tests="phase"}
   The walk is at 0.3 of 1.2 s, which is 0.25 of its cycle. The run starts at 0.25 of 0.8 s, which is 0.2 s. Strata
   itself starts it at 0.0 s.
   :::

3. After importing a character you see no "Not imported" warning in the Console. What does that tell you?

   :::answer{tests="morph"}
   The importer found no morph targets and no weight animation, because it warns for each skipped feature it meets.
   :::

4. Why does an additive clip need a reference pose?

   :::answer{tests="additive"}
   An additive clip stores a difference, and a difference means nothing without the pose it was measured from. The
   evaluation subtracts the reference from each sample first.
   :::

## Exercises

1. **Basic.** Import a copy of the robot's model into a project and find the importer's two warnings about morph
   targets, then the two code lines that cause them.

   :::answer[Worked solution]{tests="morph" solution="tutorials/animation/limits/exercise-1.tutorial.json"}
   Import `Samples/ThirdPerson/Assets/Models/Robot/RobotExpressive.glb` with the **Import** button of the **Content
   Browser**, open the **Console**, and type "Not imported" into its search field. Two warnings appear. Then search the
   code for "morph target" and find the two lines in `GltfImporter.cpp`: the importer adds the feature to a set of
   skipped features, and a later loop turns each one into a warning. The tutorial file does the same with commands.
   :::

2. **Hard.** Design an additive flag for states: the reference pose, and where the work enters `Evaluate`.

   :::answer[Worked solution]{tests="additive"}
   Step 1: add `Additive` to each state of the controller and save it there. Step 2: take the clip's first key as the
   reference. Step 3: in `Evaluate`, after the weighted sum and the
   :term[normalization]{id=normalization} of rotations and before the model transforms, add each additive entry to the blended pose. Translation
   gains weight times difference, rotation turns by the difference scaled by its weight. Step 4: keep additive entries
   out of the weights that add up to one, and out of the :term[root motion]{id=root-motion} loop, which would move the entity twice.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimatorInstance.h`: `c_MaxPlaying`, the four entries of a cross-fade.
- `Strata/src/Strata/Animation/AnimatorInstance.cpp`: `AnimatorInstance::Evaluate`, the weighted sum.
- `Strata/src/Strata/Animation/AnimationClip.h`: binding by name and `ReduceKeys`.
- `Strata/src/Strata/Asset/GltfImporter.cpp`: the skipped features and their warnings.
- `Strata/shaders/Scene/Mesh.vert.slang`: skinning in the vertex shader.
- `StrataEditor/src/Panels/AssetInspectorPanel.cpp`: the Asset tab's joint tree.
- `Docs/Roadmap.md`: the wave 9 entries.

## Further reading

- Unity manual, "Blend Trees" (<https://docs.unity3d.com/Manual/class-BlendTree.html>): blend trees by parameter; beginner.
- Unity manual, "Animation layers" (<https://docs.unity3d.com/Manual/AnimationLayers.html>): layers and masks; beginner.
- Godot documentation, "Using AnimationTree" (<https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html>): blend spaces and trees; beginner.
- Khronos, glTF 2.0 specification, morph targets (<https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#morph-targets>): how files store them; intermediate.
- ozz-animation (<https://github.com/guillaumeblanc/ozz-animation>): an open library with additive blending, IK and compression; advanced.
- Esoterica (<https://github.com/BobbyAnguelov/Esoterica>): an open animation system with graphs and sync tracks; advanced.
- Simon Clavet, "Motion Matching and The Road to Next-Gen Animation", GDC 2016: motion matching; intermediate.
- Unreal Engine documentation on Animation Blueprints, layered blends and IK Rig: the same features in Unreal; beginner.
