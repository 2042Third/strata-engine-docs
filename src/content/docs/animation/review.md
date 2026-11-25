---
id: animation/review
title: "Review: animation"
description: "The questions of every page of the part on animation, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** The robot's mesh has 7,214 vertices. A clip of 30 frames stores one position for each vertex in each frame. The same motion as joint keys has 20 rotation channels and one translation channel, each with 30 keys, and every channel has the same key times.

   How many bytes does each form take, with the key sizes of [the animation problem](problem.md), and how many bytes does sharing the key times save? Then a reduction removes 10 keys from every channel, at different times in different channels: what does the clip take now?

   :::answer[Worked solution]
   Step 1: one frame of positions is $7{,}214 \times 12 = 86{,}568$ bytes, so 30 frames take $86{,}568 \times 30 = 2{,}597{,}040$ bytes.

   Step 2: a rotation key holds 4 bytes of time and 16 bytes of value, 20 bytes; a translation key holds 4 and 12, 16 bytes. Without sharing, the keys take $20 \times 30 \times 20 + 30 \times 16 = 12{,}000 + 480 = 12{,}480$ bytes.

   Step 3: when the channels share their key times, the times are stored once: $30 \times 4 = 120$ bytes in place of $21 \times 30 \times 4 = 2{,}520$. Sharing saves 2,400 bytes, and the clip takes 10,080 bytes. Against the 2,597,040 bytes of positions, that is about 258 times smaller (about 208 times without sharing).

   Step 4: after the reduction each channel has 20 keys at its own times, so nothing is shared. The times take $21 \times 20 \times 4 = 1{,}680$ bytes and the values take $20 \times 20 \times 16 + 20 \times 12 = 6{,}640$ bytes, in all 8,320 bytes. That is still 1,760 bytes below the shared clip, because a third of the keys went.

   Step 5: if the reduction had removed the same keys from every channel, the times could stay shared, and the clip would take $6{,}640 + 80 = 6{,}720$ bytes. The price of reduction channel by channel is the lost sharing.
   :::

2. **Basic.** A two-joint arm has a shoulder at the origin, the root, and an elbow joint that stands 1 unit above it in the bind pose. The pose turns the elbow a quarter turn counterclockwise about Z, and its local pose keeps the translation (0, 1, 0).

   A vertex at (0.2, 1.3, 0) has the glTF weights 0.25 for the shoulder and 0.75 for the elbow. Which 16-bit weights does the importer store, and where does the vertex land? Use the identity for the matrix that takes animator space into the mesh's space.

   :::answer[Worked solution]
   Step 1, the weights: $0.25 \times 65{,}535 = 16{,}383.75$, which rounds to 16,384, and $0.75 \times 65{,}535 = 49{,}151.25$, which rounds to 49,151. The sum is 65,535, so the importer has no difference to give to the strongest weight.

   Step 2, the pose by forward kinematics: the shoulder's local pose is the identity, so its model transform is the identity. The elbow's local pose applies rotation first and translation last, so its model transform is the shoulder's times the translation (0, 1, 0) times the quarter turn.

   Step 3, the palette entries: the shoulder's entry is the identity, because its inverse bind matrix and its pose cancel. The elbow's entry is its model transform times its inverse bind matrix, which is the translation (0, −1, 0), so the vertex goes into the elbow's space first.

   Step 4, each joint alone: the shoulder leaves the vertex at (0.2, 1.3, 0). From the elbow, the vertex is at (0.2, 0.3, 0). A quarter turn counterclockwise sends $(x, y)$ to $(-y, x)$, giving (−0.3, 0.2, 0), and the translation adds (0, 1, 0): (−0.3, 1.2, 0).

   Step 5, the blend: x is $0.25 \times 0.2 + 0.75 \times (-0.3) = -0.175$, and y is $0.25 \times 1.3 + 0.75 \times 1.2 = 1.225$. The vertex lands at (−0.175, 1.225, 0), three quarters of the way from the shoulder's answer to the elbow's. The stored weights differ from the exact fractions by a few parts in a million, far below what the eye sees.
   :::

3. **Medium.** A controller starts in `Walk`, a looping state, in one run, and in `Wave`, a state that does not loop, in another. Both clips last 1.25 s. Each state has one transition to `Idle` with the exit time 0.75 and the condition that the trigger `Stop` is set.

   Every update lasts 0.375 s, and all speeds are 1. A script sets `Stop` before update 4. In which update does each run leave its state, and is the trigger still set after update 6?

   :::answer[Worked solution]
   Step 1, the normalized time: one update moves it by $0.375 / 1.25 = 0.3$, so after updates 1 to 7 a looping state shows 0.3, 0.6, 0.9, 1.2, 1.5, 1.8 and 2.1.

   Step 2, `Walk`: it loops and the exit time is below 1, so the transition is ready in the update that crosses 0.75, 1.75, 2.75 and so on. Update 3 crosses 0.75 (from 0.6 to 0.9), but `Stop` is not set yet. Updates 4 and 5 cross nothing. Update 6 crosses 1.75 (from 1.5 to 1.8), and `Stop` is set, so `Walk` leaves in update 6.

   Step 3, `Wave`: the state does not loop, so its normalized time stops at 1 and the test is only "reached". From update 3 on it is reached, and update 4 is the first with `Stop` set: `Wave` leaves in update 4, two updates before `Walk`.

   Step 4, the trigger: a firing transition consumes the triggers it tests, and a trigger on which nothing fired stays set. In the `Walk` run the trigger stays set through updates 4 and 5 and is consumed in update 6, so it is clear after update 6. In the `Wave` run it was consumed in update 4.
   :::

4. **Medium.** A robot's `Animator` is set to `WhenVisible`. It plays a looping clip of 1 s with footstep events at 0.3 s and 0.8 s, and each update lasts 0.25 s. The renderer draws the robot in updates 1, 2 and 3 and reports it after each, and the robot is out of view from update 4 on.

   For 12 updates: which updates pose the robot, which skip the pose, how many footsteps fire in total, and how many of them fire while the pose is skipped? How many samples does the reach of the clip take?

   :::answer[Worked solution]
   Step 1, the decision: the last report came after update 3, so `SeenUpdate` is 3. An update poses the animator while $3 + 1$ reaches its index, so update 4 still poses it. Update 5 is the first to skip, and updates 5 to 12 all skip: 8 updates. Updates 1 to 4 pose.

   Step 2, the events: skipping the pose skips only the pose, and the update keeps advancing the playhead and collecting events. Update $k$ covers the stretch $(0.25(k-1),\ 0.25k]$. The events happen at 0.3, 0.8, 1.3, 1.8, 2.3 and 2.8 s of play, so they fall in updates 2, 4, 6, 8, 10 and 12. All 6 footsteps fire.

   Step 3, the split: updates 2 and 4 pose the robot, so 2 footsteps fire with a pose. Updates 6, 8, 10 and 12 skip it, so 4 footsteps fire while the pose is skipped. The sound of a footstep must not depend on the camera, and here it does not.

   Step 4, the reach: the clip lasts 1 s, so the count is $\lceil 1 \times 15 \rceil + 1 = 16$ samples, inside the range 2 to 48. The reach lets the renderer find the robot again where the clip takes it, even though its frozen pose never overlaps the view.
   :::

5. **Medium.** In a controller, a walk cycle lasts 1.0 s and a run cycle 0.6 s, and the left foot lands at the start of both. `Walk` to `Run` has a fade of 0.25 s, and a transition from Any State to `Jump` has a fade of 0.2 s. Every update lasts 0.1 s, and the walk to run transition fires in an update that leaves the walk at 0.35 s of its cycle.

   Where does Strata start the run, and where would a phase-matched start put it? A script sets the jump trigger before the next update, and Any State to `Jump` fires in that update. What are the weights of walk, run and jump after the update that follows it?

   :::answer[Worked solution]
   Step 1, the start: a cross-fade starts the target at its first frame, so Strata starts the run at 0.0 s. The walk is at 0.35 of its cycle and the run at 0, so the feet disagree by 35 % of a cycle and slide.

   Step 2, the phase match: 0.35 of the run cycle is $0.35 \times 0.6 = 0.21$ s, so a run that starts at 0.21 s would agree with the walk. Strata has no such start, so the feet slide for the length of the fade unless you cut the clips to line up.

   Step 3, the interrupted fade: in the next update the first fade runs 0.1 s of 0.25 s, a progress of 0.4, so the walk weighs $1 \times (1 - 0.4) = 0.6$ and the run 0.4. The state machine runs after the weights, at the end of the update, so the jump fade saves these shares as its start weights.

   Step 4, the jump fade: in the update after it, 0.1 s of 0.2 s is a progress of 0.5. The old entries get their start weight times 0.5, which is 0.3 for the walk and 0.2 for the run, and the target gets 0.5. The three weights sum to 1, as they must.
   :::

6. **Medium.** In the editor, a scene holds 600 animators on two skeletons. Of them, 250 use skeleton A with no controller, 150 use skeleton B with no controller, and 200 use skeleton A with the controller C, the default clip K and the same root motion setting.

   How many poses does the preview compute in rest mode, and how many in clip-start mode? Then you import skeleton A again: how many poses have been computed in all in each mode? Why does the render scene compute every palette again when you press Play, even if the pose version numbers agree?

   :::answer[Worked solution]
   Step 1, rest mode: the key of a pose holds only the skeleton, so all animators on A share one pose and all on B share another. The preview computes 2 poses.

   Step 2, clip-start mode: the key also holds the controller, the clip and the root motion setting. The 250 animators on A with nothing form one key, the 150 on B another, and the 200 with C and K a third: 3 poses.

   Step 3, the new import of A: its source revision changes, and only that makes a pose wait again. In rest mode only the pose of A is computed again, so 3 poses in all. In clip-start mode both poses that use A are computed again, the plain one and the one with C and K, so $3 + 2 = 5$ in all. The pose of B stays.

   Step 4, Play: the play copy has its own Animation system, which is another provider of poses. Each provider counts its versions on its own, so "version 12" can mean two different poses. The render scene remembers which provider it last read and, when the provider changes, ignores the comparison and computes every palette again. A palette from the preview would otherwise stay on screen with the system's number.
   :::

7. **Hard.** A glTF file has these nodes: `Armature` with the child `Hips`; `Hips` with the children `Spine` and `Tail`; `Tail` with the child `TailTip`; and a mesh node `Body` under `Armature`. Its only skin lists `Hips` and `Spine`.

   The mesh of `Body` has morph targets. The file has four animations in this order: `Idle`, `Run`, `Run` and one without a name. `Idle` and the last one rotate `Hips`. The first `Run` rotates `Hips` and `Tail`, one channel each, and the second rotates `Spine` and has a morph target weights channel on `Body`.

   Which joints does the skeleton have, which is the root motion joint, what are the four clip keys, and which warnings appear? Then the first `Run` clip binds to a skeleton with the joints `Hips`, `Spine` and `Tail2`: how many of its channels are bound?

   :::answer[Worked solution]
   Step 1, the joints: the importer marks the joints of every skin (`Hips`, `Spine`), the animated nodes (`Hips`, `Spine`, `Tail`) and the ancestors of all of them (`Armature` above `Hips`; `Hips` above `Tail`). `TailTip` and `Body` are no joints: nothing animates or skins them, and a weights channel marks no node. The skeleton has four joints: `Armature`, `Hips`, `Spine` and `Tail`. Parents come first, so `Armature` is joint 0 and `Hips` is joint 1.

   Step 2, the root motion joint: the topmost joint of the skin, the one with the smallest number among those the skin lists. That is `Hips`, not `Armature`, which no skin lists.

   Step 3, the keys: a clip has the key `Animation/<name>`, unless the name is missing or shared, and then `Animation/<index>`. `Idle` is `Animation/Idle`. The two `Run` animations share a name, so they are `Animation/1` and `Animation/2`, and the animation without a name is `Animation/3`.

   Step 4, the warnings: the weights channel on `Body` is skipped, and the import warns "Not imported: morph target animation". The second `Run` keeps its `Spine` channel, so it still becomes a clip; an animation with only the weights channel would be skipped with a warning of its own. The morph targets of the mesh are skipped too, and the import warns "Not imported: morph targets".

   Step 5, the binding: the clip binds by name, once, and skips the names that the skeleton lacks. The clip has the channels `Hips` and `Tail`. The skeleton has `Hips` but no `Tail`, so 1 of 2 channels is bound. `Tail2` stays at its rest pose, because a clip does not adapt to other names.
   :::

8. **Hard.** A robot walks on a walk clip of 1 s whose root moves at a constant 2 m/s, with root motion. A script starts a cross-fade of 2 s to a run clip of 0.8 s whose root moves at a constant 4 m/s. After one update of 0.5 s the script starts a fade of 1 s to `Idle`, whose root does not move, and another update of 0.5 s follows.

   How far does the entity move in each update, and why does the pose not show the same distance again?

   :::answer[Worked solution]
   Step 1, update 1: the fade has run 0.5 s of 2 s, so its progress is 0.25. The weights are walk 0.75 and run 0.25. The walk's root travels $2 \times 0.5 = 1$ m, and the run, which starts at its first frame, travels $4 \times 0.5 = 2$ m. The move is $0.75 \times 1 + 0.25 \times 2 = 1.25$ m.

   Step 2, the new fade: the entries keep 0.75 and 0.25 as start weights. After 0.5 s of 1 s, the progress is 0.5: walk $0.75 \times 0.5 = 0.375$, run $0.25 \times 0.5 = 0.125$ and idle 0.5. The weights sum to 1.

   Step 3, the travel of update 2: the walk travels 1 m. The run's playhead goes from 0.5 s to 1.0 s of a 0.8 s clip, so it crosses the loop boundary. The part before it, 0.3 s, gives 1.2 m, and the part after it, 0.2 s, gives 0.8 m, in all 2.0 m. The idle travels 0 m.

   Step 4, the move: $0.375 \times 1 + 0.125 \times 2.0 + 0.5 \times 0 = 0.625$ m. The two updates move the entity $1.25 + 0.625 = 1.875$ m. The idle's share is why the move drops while the clips keep their speeds.

   Step 5, the pose: the animator weights the offset of the root from where the clips started in the same way, and holds the root's subtree back by it. The entity carries the travel. Without the hold, the mesh, which follows the entity, would run ahead of it by the same amount a second time.
   :::

9. **Hard.** A teammate imports the robot and puts its model, whose root carries the `Animator`, below an entity with a capsule and a character controller. The walk clip travels 2 m/s and root motion is on. In play, the capsule stays where it is, the model leaves it, and the model is 6 m away after 3 s.

   Find the fault, say what each part does in this case, and name the fix and what changes after it. What happens afterwards when a wall stands in the way?

   :::answer[Worked solution]
   Step 1, the travel: the animator measures the travel of the root, 2 m/s, takes it out of the pose, and hands it to `AnimationSystem::ApplyRootMotion`. After 3 s the travel is 6 m, which matches the distance of the model.

   Step 2, the branch: the apply step searches for a character controller on the animator's own entity. The animator sits on the model, a child of the capsule's entity, so the search fails and the code uses the other branch: it moves the model's own transform by the travel. The capsule never hears of it, and the model walks away from the capsule.

   Step 3, the fix: put the animator and the controller on the same entity. Then the search succeeds, the move goes to the controller, and the system writes only the turn to the entity.

   Step 4, after the fix: the controller walks the move at its next fixed step, so the capsule and the mesh travel together. The pose still holds the root back, so the mesh does not run ahead of the capsule.

   Step 5, the wall: the controller collides as it walks, so the capsule stops at the wall while the clip keeps playing. In the faulty setup, nothing collides, because the model's transform is moved directly and a wall cannot stop it.
   :::
