# Brief: `make/animation`

| Field | Value |
| --- | --- |
| Title | Animation for game makers |
| Kind | T |
| Size | L |
| Tracks | G |
| Needs | `make/characters-cameras` |
| From | gamedev "Animation for game makers" (§1.12, concept 18); animation "Tutorial: an animated character from import to footsteps"; the how-to half of animation "Animation in the editor: previews, edit poses and commands" (the Asset tab's tables, the Inspector's live state, the preview chip; the `animation.*` commands in the command tab); no menu or button creates an animation controller at the pin (`StrataEditor/src/Panels/ContentBrowserPanel.cpp:564-580`; only `animation.createController`, `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153`), so the tutorial's starting checkpoint holds a minimal controller and the reader edits it in the Asset tab with **Add Parameter**, **Add State** and **Add Transition** (`StrataEditor/src/UI/AnimationAssetViews.cpp:532, 659, 791`); the page says so in one sentence and names `make/commands`, where the command is run; scripting "The gameplay API, part 2": `Animator`, `JointTransform`, `OnAnimationEvent` |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/animation` — Animation for game makers

**Covers.** A tutorial: the player of `make/characters-cameras` becomes the Third-Person sample's robot, which idles,
walks, runs, jumps, steps with sounds and holds a flag. It opens with the words, each from zero and on the robot: a
skeleton of joints, clips that move them, a skin that bends the mesh with them; an animator that plays an animation
controller, a state machine of states, transitions, parameters (float, bool, trigger) and cross-fades. The step
sections, each ending in a checkpoint:

1. What the import made: the robot's model was imported into the checkpoint; placed under the player, its root has an
   `Animator`, and the model's skeleton, clips and skin are sub-assets. In edit mode it stands in its rest pose; the
   Scene view's camera chip shows the first frame of its clip instead. Its morph targets (the face) are not imported.
2. The controller: the checkpoint holds `Animations/Player.stanimator`, made by the command
   `animation.createController`, because no menu or button makes one (one sentence and a link to `make/commands`, where
   the command is run). The steps assign it to the Animator's Controller field, play, and watch the Inspector's live
   state: the state, `from -> to` during a fade, the normalized time and the parameters. The robot's own controller is
   read as data, its parameters, states and footstep events. The step's "If you do not see it" reads the table of
   `animation/system` of what a character shows while something is missing: the bind pose until the skeleton, the
   controller and the clips are in (for good, with one warning, when the skeleton does not load), the component's Clip
   when the controller does not load, the rest pose for a state whose clip does not load.
3. Walk and run: in the Asset tab, **Add Parameter** (Speed), **Add State** (Walk, Run, each with its clip) and **Add
   Transition** (Idle to Walk on `Speed > 0.1`, Walk to Run, and back), with the condition text; a cross-fade's duration.
   The pitfall: a transition with no condition and no exit time fires in the first update of its state, so that state
   hardly plays.
4. Drive it from the script: `GetAnimator()` and `SetFloat("Speed", ...)` and `SetBool("Grounded", ...)` from the
   controller's velocity, every frame, as the Third-Person player does.
5. Jump from any state: a trigger parameter, a transition from Any State on it, an exit time back to Idle; a trigger
   stays set until a transition uses it.
6. Footsteps: Footstep events on the Walk and Run states, and a `Footsteps` script on the robot, the entity with the
   Animator, as the sample has it, whose `OnAnimationEvent` plays one of four step sounds at the robot with a random
   pitch. Only the scripts on the animator's own entity receive its events, so the same script on the player hears
   nothing, and nothing warns. The pitfall: an event whose time is past its clip's duration never fires, and nothing
   warns.
7. Hold a flag: an `AttachToJoint` component keeps an entity on the hand's joint. It writes the entity's translation,
   rotation and scale every update, so the step builds a holder and its child, as the sample does: the holder is
   attached with no offset, and the flag under it carries the offset, the turn and the scale. The Joint field is a typed
   name that nothing checks: a misspelt name leaves the entity where it is, with no warning. Then the same in a script
   with `GetJointTransform`, and why the component is the better choice: a script reads the previous update's pose,
   since Animation runs after Scripting. A joint that gameplay reads also depends on the camera, unlike time, events
   and root motion: while a WhenVisible animator is unseen, it is a stale pose.
8. Root motion: the move of a clip reaches a character controller only on the animator's own entity, and the course's
   robot sits under the player, as in the sample. So the step places a second robot in the course and gives its root,
   the entity with the Animator, a `CharacterController`; with `ApplyRootMotion` on, the controller walks what the clip
   travels and collides as it walks. The step's "If you do not see it" is the drift: `ApplyRootMotion` on the player's
   robot moves the model away from its capsule, through walls, while the capsule stays. Then when to leave it off and let
   the script move the character, as the Third-Person sample does.
9. Animate only what is seen: the Animator's culling mode, WhenVisible, on the second robot, with the follow camera
   turned away from it and back, and what the robot does meanwhile. The player's robot cannot show it: the follow
   camera always looks at it, so it is always seen.

It ends with what Strata's animation does not do (blend trees, animation layers, IK, morph targets, clip compression) and
links `animation/limits`. The exercise, done in the editor, is G8 on the page's robot: a Crouch state on a bool, edited
in the Asset tab and undone. At the end the reader can bring a rigged model into a game, give it a controller, drive it
from a script and react to its events.

**Leaves out.**

- Importing models and their settings in general → `make/assets`
- Skeletons, clips and skinning as the engine does them → `animation/skeletons`, `animation/clips`, `animation/skinning`
- State machines, cross-fades, events and root motion inside → `animation/state-machines`, `animation/blending`,
  `animation/time-events`, `animation/root-motion`
- Showing a pose without playing (`animation.preview` and its chip) → `make/commands`
- Running `animation.createController` → `make/commands`
- Measuring many animated characters → `make/performance`
- The character controller and the follow camera → `make/characters-cameras`
- Everything Strata's animation does not do, in full → `animation/limits`

**Fit.** `over`: about 7,600 words against L (5,000). The words of animation for a reader who has none (about 1,500)
and nine step sections of about 25 steps (about 4,900 words with their three excerpts, rules, pitfalls and figures)
reach L's top; the next size is XL (8,000) by S2, and the split of the earlier line stays the other way:
`make/animation` "Animation for game makers: models, controllers and parameters" (sections 1 to 5 and 9) and
`make/animation-events` "Animation events, attachments and root motion" (sections 6 to 8). The wave 8 animation graph is
not at the pin (`plan/inventory/gamedev.md:174`); the page describes the controller of 822a7a46 only.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:335` | concept | home | Animation for makers: skeletons, clips, state machines, parameters against triggers, cross-fades, events, root motion, attachments; the mistakes of setting a trigger every frame and of feet that slide |
| `gamedev:167-172` | feature | home | The import of a skinned glTF (the root becomes an Animator); `.stanimator` controllers with parameters, states and transitions; the script API; `AttachToJoint`, root motion and the culling mode; the rest pose and first frame in edit mode; what is not imported (morph targets) |
| `gamedev:630-635` | term | home | Skeleton, joint, clip, skin; animator, animation controller, state, transition, parameter, trigger parameter; cross-fade; animation event; root motion; `AttachToJoint` |
| `animation:177` | feature | home | The SDK's `Animator`, from `Entity::GetAnimator()`: parameters, play and cross-fade, the current state, normalized time, joints |
| `animation:191` | feature | home | The Asset tab's views: the skeleton's joints, a clip's channels, and the controller as tables with **Add Parameter**, **Add State** and **Add Transition** and the condition and event texts |
| `animation:192` | feature | home | The Inspector's live state while playing: the state, `from -> to` during a fade, normalized time, parameters |
| `gamedev:381` | code | home | `Samples/ThirdPerson/Assets/Animations/Robot.stanimator:1-51`: a controller as data: its five parameters, the Idle state, and the Walk state with its two Footstep events |
| `animation:363` | code | home | `Samples/ThirdPerson/Scripts/Footsteps.cpp:12-42`: `OnAnimationEvent` playing one of four clips with a random pitch, the clips asked for in `OnCreate`; with `ThirdPersonPlayer.cpp` 129-133, where the player sets Speed and Grounded each frame |
| `animation:514-519` | hands-on | home | G1 to G6: import and rest pose, a two-state controller driven by Speed, footstep events, an any-state jump with exit times, a flag on a joint, root motion with and without a character controller |
| `animation:521` | hands-on | home | G8, the page's exercise, done on its robot: a Crouch state on a bool, edited in the Asset tab and undone |
| `audio-input:559` | hands-on | home | Footsteps from animation events, with a random pitch |
| `render-scene:561` | hands-on | home | The culling mode WhenVisible on a second robot placed in the course: turn the follow camera away from it and back, and watch the pose catch up (the player's robot is always in view, so it cannot show this) |
| `new:5` | not-done | home | No blend trees, animation layers, IK, morph targets or clip compression. Evidence: `git grep -nilE -e "blend ?tree" -e "inverse kinematics" -e morph -e compress 822a7a46 -- Strata/src/Strata/Animation` finds nothing; `Strata/src/Strata/Asset/GltfImporter.cpp:1031` (weight channels skipped); `Docs/Roadmap.md:1649-1652` |
| `new:6` | not-done | home | No menu or button creates an animation controller; only the command `animation.createController` does. Evidence: `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153`; the Content Browser's New menu makes folders, materials, worlds and scripts only (`StrataEditor/src/Panels/ContentBrowserPanel.cpp:564-580`); `git grep -n "createController" 822a7a46 -- StrataEditor/src` finds only `EditorAnimationCommands.cpp` |
| `new:25` | rule | home | Root motion walks a character controller only when the Animator and the `CharacterController` are on one entity; otherwise the move is written to the animator's own transform, and a model under its player leaves the capsule. Step 8 is done on a second robot whose root carries the controller, with the drift as its "If you do not see it". Evidence: `Strata/src/Strata/Animation/AnimationSystem.cpp:801-826` (`AddCharacterMotion(animator, move)`, else the animator's transform moves); `Strata/src/Strata/Physics/CharacterControllers.cpp:816-822, 1050-1056` (the controller is looked up on that entity alone); `Samples/ThirdPerson/Assets/Scenes/Course.stscene:151-152` (Player with the CharacterController, Robot with the Animator as its child) |
| `new:34` | rule | home | Step 7: `AttachToJoint` writes the entity's translation, rotation and scale every update, so an offset, a turn or a scale goes on a child: the holder is attached with no offset, and the flag under it carries the offset, the turn and the scale, as the sample's FlagHolder and Flag do. The Joint field is a typed name that nothing checks: a misspelt name leaves the entity where it is, with no warning. Evidence: `Strata/src/Strata/Animation/AnimationComponents.h:39-45` (the world transform becomes the animator's times the joint's; children keep their offsets); `Strata/src/Strata/Animation/AnimationSystem.cpp:849-851` (a joint the skeleton lacks is skipped, and nothing is logged), `:877-880` (the three fields written); `Strata/src/Strata/Animation/AnimationComponents.cpp:52` (Joint, a plain text property); `Samples/ThirdPerson/Assets/Scenes/MainMenu.stscene:72-73` (FlagHolder on `Palm2.R` with an identity transform; its child Flag with the offset, the turn and the scale 0.035) |
| `new:35` | rule | home | The pitfall lines of steps 3 and 6: a transition with no condition and no exit time fires in the first update of its source state, so that state hardly plays; an event whose time is past its clip's duration never fires, and nothing warns (the internals are on `animation/state-machines` and `animation/time-events`). Evidence: `Strata/src/Strata/Animation/AnimationController.h:77-80` ("None: it fires as soon as they hold"); `Strata/src/Strata/Animation/AnimatorInstance.cpp:426-444` (no condition holds as all conditions holding), `:734-737` (no exit time counts as reached), `:480-503` (an event fires when the playhead crosses its time), `:505-511` (a clip that does not loop stops at its duration), `:514-516` (a looping one wraps there); `Strata/src/Strata/Animation/AnimationController.cpp:187-188` (validation refuses only a negative or non-finite time) |
| `animation:74` | feature | use | `AnimatorComponent`'s fields (Skeleton, Controller, Clip, Speed, Loop, Play On Start, Apply Root Motion, Culling Mode) |
| `animation:76` | feature | use | `AnimatorCullingMode`: AlwaysAnimate and WhenVisible |
| `animation:78` | feature | use | `AttachToJointComponent` |
| `animation:84-88` | feature | use | Simple mode against a state machine; conditions; triggers consumed; exit times |
| `animation:90` | feature | use | Cross-fades |
| `animation:97-98` | feature | use | Events; the rest pose when nothing plays; with the table of `animation/system` of what a character shows while its skeleton, controller or clips are missing, which step 2's "If you do not see it" reads |
| `animation:178` | feature | use | `OnAnimationEvent` reaches only the active scripts on the animator's own entity, so `Footsteps` goes on the robot (its home is `scripting/script-system`) |
| `animation:111` | feature | use | Root motion through a character controller |
| `animation:129` | feature | use | WhenVisible culling, in a game maker's words, shown on the second robot of step 9 |
| `animation:450` | rule | use | WhenVisible keeps time, events, transitions and root motion but not the pose: in step 7, a joint that gameplay reads while the animator is unseen is a stale pose, placed at the entity's current transform, and a script reads the previous update's pose, since Animation runs after Scripting (both beside this rule on `animation/culling`) |
| `animation:166-167` | feature | use | Rest poses and the first frame of the clip in edit mode |
| `animation:185` | feature | use | `animation.createController`, the command that made the checkpoint's controller |
| `animation:212` | feature | use | The Third-Person robot: its model and licence, its controller and its scripts |
| `animation:283` | concept | use | State machines for animation (their home is `animation/state-machines`) |
| `animation:296` | concept | use | Animation events |
| `animation:300` | concept | use | Root motion |
| `animation:305` | concept | use | Attachments (sockets) |
| `animation:387`, `gamedev:422` | figure | use | The robot's controller as a state machine: Idle, Walk and Run on Speed, Jump from any state on a trigger, Wave and Dance, the Footstep event times. One file, drawn once and homed on `animation/state-machines`, which this page shows (R34, D42); gamedev figure 14 is the same figure |
| `animation:416` | figure | use | The Inspector of the playing robot during a fade |
| `animation:418`, `gamedev:458` | figure | use | The controller's tables in the Asset tab with `Robot.stanimator` open. One screenshot, taken once and homed on `animation/state-machines`, which this page shows (R34, D42); gamedev screenshot 20 is the same picture. The robot's pose is shown in play mode, since a pose preview needs a command (`make/commands`) |
| `animation:421` | figure | use | The menu robot holding the flag |
| `animation:485` | rule | use | Triggers stay set until consumed |
| `animation:487` | rule | use | A walk-to-run cross-fade without phase matching slides the feet |
| `scripting:128` | feature | home | `Animator` and `JointTransform` in the SDK, one entry with `animation:177`: states, clips, cross-fade, parameters, speed, state queries, joints; `reference/script-api` lists the declarations and links here |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Importing a glTF model; sub-assets | `make/assets` | must |
| Models as entity templates; placing a model in the scene | `make/prefabs` | must |
| The character controller and the player's script | `make/characters-cameras` | must |
| Input actions in a script | `make/input` | must |
| One-shot sounds at a position, and asking for clips early | `make/sound` | must |
| Asset fields set in the Inspector | `make/script-fields` | must |
| Reading JSON | `start/how-to-read` | must |
| Undo | `make/project-files` | must |
| Random numbers in a range | `make/recipes` | helps |
| Running a command | `make/commands` | helps |

**Starting state.** A downloadable checkpoint of the obstacle course: the end checkpoint of `make/characters-cameras`
(the course, the player and the follow camera), with three additions made for this page: the
Third-Person sample's robot (`RobotExpressive.glb`, CC0, Tomás Laulhé (Quaternius), modified by Don McCurdy) imported,
its four footstep sounds (Kenney, CC0) imported, and `Animations/Player.stanimator`, a minimal controller made by
`animation.createController` (one state, Idle, playing the robot's Idle clip; no parameters), which the reader edits in the
Asset tab. The page says in one sentence that a command made the controller.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `animation-controller` | animation controller | - |
| `animation-event` | Animation event | - |
| `attachtojoint` | AttachToJoint | - |
| `clip` | clip | - |
| `joint` | joint | - |
| `skeleton` | Skeleton | - |
| `skin` | skin | - |
| `transition-make` | transition (make) | - |
| `trigger-parameter` | trigger parameter | - |
| `parameter` | parameter (use) | - |
| `animator` | Animator (use) | - |
| `state` | State (use) | - |
| `cross-fade` | Cross-fade (use) | - |
| `root-motion` | Root motion (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b1-13 | should | missing-item | step 4 (`animation:363`) on `make/animation` | The robot with its Animator sits under the player, and the player's script drives it. The sample's player reaches it through an entity field, `Robot`, and calls `Robot.GetAnimator()`. The Covers says only "`GetAnimator()`". Called on the player itself, it fails and logs "'Player' has no Animator component", so the robot never walks, and the step does not say why. | Step 4 adds an `Entity` field `Robot` to the player's script, set in the Inspector to the robot, and calls `Robot.GetAnimator()`; the step's "If you do not see it" quotes the message (about 60 words). | `allocation/make-b1.md:643-644`, `:704`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.h:8`, `:26`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:72`, `:129-133`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1983-1992` |
