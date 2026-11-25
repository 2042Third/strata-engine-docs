---
id: reference/animation
title: "Animation reference"
description: "The animation controller format, the cooked skeleton and clip forms, the limits, the condition operators and the animation services of Strata."
kind: reference
size: M
tracks: []
needs: [animation/state-machines]
status: final
---

This page holds the facts of animation that no other reference page holds. They are the :term[file format]{id=file-format} of an :term[animation controller]{id=animation-controller-state-machine}, the two binary forms of skeletons and clips, the numeric limits, the condition operators and the scene services.
You read it to write a controller by hand, to check why a file is refused, or to find the number behind a message. Each table has a short introduction that names the page teaching its subject. A row names one thing, and the other columns say what it is, its type and the rule that the engine enforces.

Three catalogue pages hold the rest. The `Animator`, `Skin` and `AttachToJoint` components, with the culling mode of the `Animator` and the reason its `Clip` property is inactive, are in [Components](../reference/components.md). The four `animation.*` commands and the `editPose` setting of `viewport.setSettings` are in [Commands](../reference/commands.md). The host functions of the script software development kit (SDK) that control an animator, the SDK's `Animator` class and the `OnAnimationEvent` :term[callback]{id=callback} are in [the script reference](../reference/script-api.md). The measured costs of animation are in [Measured costs and their budgets](../reference/performance.md).

## The animation controller format

An animation controller is a file that holds a state machine: a list of states, each playing one clip, and the transitions that move an animator from one state to the next. [State machines](../animation/state-machines.md) teaches what these parts do in a game. The file has the extension `.stanimator` and is a JavaScript Object Notation (JSON) document, a text format of named values, objects and lists that [Data formats](../basics/data-formats.md) explains.

The editor writes the file for you, and the `animation.createController` command makes one from the same keys, so you rarely type it.
You read the format when a file fails to load or a script builds a controller.

A document has two objects at its top. The `Strata` object names the format, and the `AnimationController` object holds the content. The engine reads the content and then checks it as a whole, and a document that fails any check is refused with the first problem found.

The names in the file refer to states and parameters by their text, never by number. The engine turns the names into numbers when it loads the file and writes the names again when it saves.

The table lists every key. The first column gives the path of the key from the top, with `[]` for one item of a list. A key marked "required" must be present, and every other key may be omitted and then takes the value in the last column.

| Key | Type | Meaning | Rule or default |
| --- | --- | --- | --- |
| `Strata`: `Format` | string | Names the document type | Required; the text `AnimationController` |
| `Strata`: `Version` | whole number | The format version | Required; 1 is the only version; 0 or a greater number is refused |
| `AnimationController.Parameters[]` | list of objects | The named values that conditions test | Optional; at most 256 |
| `Parameters[].Name` | string | The parameter's name | Required; unique; 1 to 256 characters without control characters |
| `Parameters[].Type` | string | The kind of the parameter | Required; `Float`, `Bool` or `Trigger` |
| `Parameters[].Default` | number or true or false | The value when the animator starts | Float: 0; `Bool`: false; a trigger refuses a default |
| `AnimationController.States[]` | list of objects | The states | Required; 1 to 1,024 |
| `States[].Name` | string | The state's name | Required; unique; same rule as a parameter name |
| `States[].Clip` | string or null | The :term[asset handle]{id=asset-handle} of the clip, 16 :term[hexadecimal]{id=hexadecimal} digits | Null or omitted: the state shows the :term[rest pose]{id=rest-pose} |
| `States[].Speed` | number | The rate at which the state plays | 1; from -100 to 100; a negative speed plays backwards |
| `States[].Loop` | true or false | Whether the clip repeats | true |
| `States[].Events[]` | list of objects | Named moments of the state's clip | Optional; at most 256 a state |
| `Events[].Name` | string | The name that scripts receive | Required; same rule as a parameter name |
| `Events[].Time` | number | Seconds from the start of the clip | 0; never negative |
| `AnimationController`: `DefaultState` | string or null | The state that starts first | Omitted or null: the first state |
| `AnimationController.Transitions[]` | list of objects | The moves between states | Optional; at most 4,096 |
| `Transitions[].From` | string | The state the transition leaves | Required unless `AnyState` is true; never both |
| `Transitions[].AnyState` | true or false | The transition leaves whatever state is playing | false |
| `Transitions[].To` | string | The state the transition enters | Required |
| `Transitions[].Conditions[]` | list of objects | Tests that must all hold | Optional; at most 16 a transition |
| `Conditions[].Parameter` | string | The parameter to test | Required; must exist |
| `Conditions[].Mode` | string | The operator | Required; `Greater`, `Less`, `True`, `False` or `Set` |
| `Conditions[].Threshold` | number | The number a float is compared with | 0; read by `Greater` and `Less` only |
| `Transitions[].ExitTime` | number or null | The normalized time of the source state to wait for | Null or omitted: no wait; never negative |
| `Transitions[].Duration` | number | The cross-fade length in seconds | 0.25; from 0 to 60; 0 switches at once |
| `Transitions[].CanTransitionToSelf` | true or false | Whether an any-state transition fires while its target plays | false; used by any-state transitions only |

A few rules stand behind the table. A number must be finite and at most 1e30 in size. The engine sorts the events of each state by time before it stores them, and events with equal times keep their order in the file. The saved form writes `Default` only for floats and true or false values, `Threshold` only for float modes, and `CanTransitionToSelf` only for any-state transitions. It writes `ExitTime` as null when there is none.

The next fence shows one transition of `Samples/ThirdPerson/Assets/Animations/Robot.stanimator`, with its numbers rounded. It leaves the state `Idle`, enters `Walk` and waits for the float `Speed` to pass 0.1, then cross-fades for 0.15 seconds.

```json
{
	"From": "Idle",
	"To": "Walk",
	"Conditions": [ { "Parameter": "Speed", "Mode": "Greater", "Threshold": 0.1 } ],
	"ExitTime": null,
	"Duration": 0.15
}
```

In the engine, the transitions are grouped by source after the checks pass. Each state owns the list of the transitions that leave it, in the order of the file, and one more list holds the any-state transitions. An animator tests the any-state list first, then the list of the state it is in, and the first transition whose conditions hold and whose exit time was reached fires. At most one transition fires in an update.

An any-state transition that leads to the state already playing is skipped unless `CanTransitionToSelf` is true. [Blending](../animation/blending.md) teaches the cross-fade that follows, and [Time and events](../animation/time-events.md) teaches loops and events.

An exit time is a fraction of the source state's clip, counted with loops. With an exit time of 0.75 on a clip of 2 seconds, the transition may fire from 1.5 seconds on. A looping state with an exit time below 1 fires once in every loop, at that point of the loop. A state without a loop fires once its time has reached the exit time. A transition without an exit time fires as soon as its conditions hold.

## Parameter kinds and condition operators

A parameter is a named value that scripts and commands set and that conditions read. The engine stores every parameter as one number, and the kind decides which operators may test it. The first table lists the three kinds, and the second lists the five operators. The kinds come from the enum `AnimationParameterType` and the operators from `AnimationConditionMode`, both in `AnimationController.h`.

| Kind | Starts as | How it is set | Tested by |
| --- | --- | --- | --- |
| `Float` | its `Default` | `SetFloat` | `Greater`, `Less` |
| `Bool` | its `Default` | `SetBool` | `True`, `False` |
| `Trigger` | cleared | `SetTrigger`, cleared by `ResetTrigger` | `Set` |

A trigger is a true-or-false value that a transition resets by itself when the transition fires. A trigger that no transition tests stays set until a script resets it.

| Operator | Tests a | Holds when |
| --- | --- | --- |
| `Greater` | float | the value is above `Threshold` |
| `Less` | float | the value is below `Threshold` |
| `True` | `Bool` | the value is set |
| `False` | `Bool` | the value is cleared |
| `Set` | trigger | the trigger is set; the firing transition resets it |

An operator tests one kind only. A condition that tests a `Bool` parameter with `Greater`, or a float with `Set`, is refused when the file loads, with a message that names both kinds. The values equal to a threshold hold neither `Greater` nor `Less`. A transition with several conditions fires only when all hold, and it resets the triggers that it tests when it fires.

## The cooked forms

An :term[importer]{id=importer} turns a model file into skeletons and clips, and stores them in a compact binary form that loads quickly. [Skeletons](../animation/skeletons.md) and [Clips](../animation/clips.md) teach what the two assets hold, and [Importing animated models](../animation/importing.md) teaches how they are made. The writer copies each number in the :term[byte order]{id=endianness} of its machine. A text is a length of 4 :term[bytes]{id=byte}, then that many bytes of text.

A cooked file starts with a four-letter tag and a version. The tag is "`STSK`" for a skeleton and `STAC` for a clip, and the version of both is 1. A reader refuses a file with another tag or version, with a message that names the asset.

The readers are `Skeleton::Deserialize` and `AnimationClip::Deserialize`. Each checks every count against its limit and against the bytes that remain before it allocates anything, so a damaged file fails and never crashes. A file with bytes left after the last field is refused as well.

The skeleton form has three parts in this order:

| Part | Size | Content |
| --- | --- | --- |
| Start | 16 bytes | Tag `STSK`, version 1, joint count, the index of the root motion joint |
| Joints | 44 bytes each | Parent index (65535 for a root joint), translation (3 numbers), rotation (4 numbers: x, y, z, w), scale (3 numbers) |
| Names | text each | One name for each joint, in joint order, up to 1,024 bytes |

The reader checks that the joint count is from 1 to 4,096, that the root motion joint exists, and that every parent comes before its child. The rest pose must be finite, the reader :term[normalizes]{id=normalization} each rotation to length 1, and the names must be unique.

The clip form has five parts:

| Part | Size | Content |
| --- | --- | --- |
| Start | 40 bytes | Tag `STAC`, version 1, channel count, target count, key time count, value count, duration, a reserved number |
| Name and targets | text each | The clip's name, then the name of each joint a channel moves |
| Channels | 20 bytes each | Target index, path, interpolation, a reserved pair of bytes, key count, first time, first value |
| Key times | 4 bytes each | Seconds, shared by channels that have the same times |
| Values | 4 bytes each | The numbers of every key of every channel |

A channel path is 0 for translation, 1 for rotation and 2 for scale. An interpolation is 0 for a step, 1 for a straight line (rotations: a spherical line) and 2 for a cubic curve, the three samplers of glTF. A key holds 3 numbers for a translation or scale and 4 for a rotation, and a cubic curve stores three of these for each key: the incoming :term[tangent]{id=tangent}, the value and the outgoing tangent.

The reader checks that each channel lies inside the shared arrays, that its times increase strictly, and that no two channels move the same part of the same joint. It checks that the stored duration equals the latest key time of any channel. Targets with no joint of the same name in a skeleton are skipped when the clip plays on it.

## Limits

A limit is a number that the engine refuses to pass. Load checks use them, and so do the commands that build controllers. [What Strata's animation does not do yet](../animation/limits.md) names the features beyond these limits. The table lists the constants as they stand in the source, with the type that holds them.

| Constant | Value | What it limits |
| --- | --- | --- |
| `Skeleton::c_MaxJoints` | 4,096 | Joints of one skeleton; joint indices are 16 bits wide in meshes and clips, and 65535 means no joint |
| `Skeleton::c_MaxNameLength` | 1,024 | Bytes of a joint name |
| `AnimationClip::c_MaxChannels` | 196,605 (3 × 65,535) | Channels of one clip: translation, rotation and scale of each possible joint |
| `AnimationClip::c_MaxKeys` | 16,777,216 (2^24) | Key times over all channels |
| `AnimationClip::c_MaxValues` | 67,108,864 (2^26) | Numbers over all channels |
| `AnimationClip::c_MaxNameLength` | 1,024 | Bytes of the clip's name and of each target |
| `AnimationController::c_MaxParameters` | 256 | Parameters of one controller |
| `AnimationController::c_MaxStates` | 1,024 | States of one controller |
| `AnimationController::c_MaxTransitions` | 4,096 | Transitions of one controller |
| `AnimationController::c_MaxConditions` | 16 | Conditions of one transition |
| `AnimationController::c_MaxEventsPerState` | 256 | Events of one state |
| `AnimationController::c_MaxNameLength` | 256 | Characters of a parameter, state or event name |
| `AnimationController::c_MaxSpeed` | 100 | The size of a state's speed, in either direction |
| `AnimationController::c_MaxDuration` | 60 | Seconds of a cross-fade |
| `AnimatorInstance::c_MaxPlaying` | 4 | Clips that one animator blends at once during cross-fades |
| `AnimatorInstance::c_MaxEventLoops` | 4 | Loops of one clip that one update fires events for |

The clip's key limits show how a cap can be derived. A clip with 100 joints that animates all three paths has 300 channels, far below 196,605. If each channel has 1,000 keys, the clip holds 300,000 key times if none are shared, which is below 16,777,216. Real clips stay far from these caps, and the caps exist to stop a damaged file from asking for huge amounts of memory.

The limit of 4 playing clips matters during rapid changes. A cross-fade adds the new state to the clips already blending, and the target's weight rises while the others share the rest. The weights always add up to 1. When four clips already blend, a new fade drops the faintest one, and the others share its weight. [Blending](../animation/blending.md) shows how the weights share.

## Scene services

A scene service is an interface that one system offers and other code finds through the scene, so that code never includes the animation module. The :term[renderer]{id=renderer}, the script host and tests reach animation only through the three services below, all declared in `Strata/src/Strata/Scene/SceneServices.h`. [The animation system](../animation/system.md) teaches how the module implements them.

Several functions share one failure rule. They return false, nothing or 0 for an entity without an `Animator`, for an unknown state or parameter and for a wrong value. They log nothing, so the caller reports the misuse in its own way.

| Service | Function | What it does |
| --- | --- | --- |
| `ISkinningPoses` | `GetPose` | Fills the current pose of an animator; false while it has none, as when no skeleton has loaded yet |
| `ISkinningPoses` | `GetPosesVersion` | A number that changes whenever any pose changes, so a renderer that saw it has seen every pose |
| `ISkinningPoses` | `ReportVisible` | A renderer tells that it drew a mesh of this animator; the answer says whether the drawn pose is older than the animator's time |
| `ISkinningPoses` | `GetRenderTransforms` | The entities that renderers draw at a transform other than the scene's, as the editor's pose preview does for attachments; none by default |
| `ISkinningPoses` | `GetRenderTransformsVersion` | A number that changes whenever that list changes |
| `IAnimatorControl` | `Play` | Jumps to a state of the controller, from its start |
| `IAnimatorControl` | `PlayClip` | Plays a clip without the controller's transitions until a state is played again |
| `IAnimatorControl` | `CrossFade` | Blends to a state over a number of seconds |
| `IAnimatorControl` | `SetFloat`, `SetBool` | Set a parameter by name and kind |
| `IAnimatorControl` | `SetTrigger`, `ResetTrigger` | Set a trigger, which stays set until a transition consumes it or the reset clears it |
| `IAnimatorControl` | `SetSpeed` | Writes the `Speed` of the `Animator` component |
| `IAnimatorControl` | `GetCurrentState` | The target of the latest transition or command; an empty name while a clip plays directly or before anything plays |
| `IAnimatorControl` | `GetNormalizedTime` | The state's time over its clip's duration, counting loops |
| `IAnimatorControl` | `IsInTransition` | True while a cross-fade runs |
| `IAnimatorControl` | `GetJointTransform` | A joint's :term[world transform]{id=world-transform} in the current pose, for attaching things to a hand; nothing without a pose or for an unknown joint |
| `IAnimatorControl` | `HasAnimator` | Whether the entity has an `Animator` component |
| `IAnimationEventSource` | `AddAnimationEventListener` | Registers a function that receives every event the playhead passes |
| `IAnimationEventSource` | `RemoveAnimationEventListener` | Removes a listener, which is not called again |

An event reaches a listener as an `AnimationEventInfo`: the animator entity and its identifier, the event's name, the state and the time of the event in its clip. The name is valid only during the call. Events are sent on the :term[main thread]{id=main-thread} after all animators were evaluated, animator by animator, and each animator's events come in the order they happened. A listener added while events are sent hears the events of the next update.

The pose service explains why renderers never depend on the animation module. A pose lives in the animation system, not in entities, and a skinned mesh names the entity of its animator. `ReportVisible` is also how an animator that sets its culling mode to `WhenVisible` learns that a camera or a shadow saw its mesh.

## The importer's version

Animated models enter the project through the glTF importer. The importer reports the version number :value{key="importer.Model.version"}, and the importer lives in `GltfImporter.h`. [Importing animated models](../animation/importing.md) teaches what the importer does with skins, joints and animations.

## What animation does not do

The module has no blend trees, layers, masks, additive clips, inverse kinematics, ragdolls, morph targets or node-graph editor; [What Strata's animation does not do yet](../animation/limits.md) lists them with what to use instead.

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimationController.h` and `AnimationController.cpp`: the controller format, the enums, the limits and the checks.
- `Strata/src/Strata/Animation/Skeleton.h` and `Skeleton.cpp`: the `STSK` form, its reader and `Skeleton::c_MaxJoints`.
- `Strata/src/Strata/Animation/AnimationClip.h` and `AnimationClip.cpp`: the `STAC` form, its reader and the clip limits.
- `Strata/src/Strata/Animation/AnimatorInstance.h` and `AnimatorInstance.cpp`: `c_MaxPlaying`, the order of transitions and the exit times.
- `Strata/src/Strata/Scene/SceneServices.h`: `ISkinningPoses`, `IAnimatorControl` and `IAnimationEventSource`.
- `Strata/src/Strata/Asset/GltfImporter.h`: the importer's version.
- `Samples/ThirdPerson/Assets/Animations/Robot.stanimator`: a complete controller that the format table can be checked against.
