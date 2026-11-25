---
id: editor/review
title: "Review: the editor's core"
description: "The questions of every page of the part on the editor's core, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** A scene has three edits with serials 1, 2 and 3 that do not merge, and a save takes its point while all three are applied. While the job writes, you make edit 4, and then the save ends. You press undo twice and make a new edit 5. Is the scene modified when the save ends, after the first undo, after the second undo and after edit 5?

   :::answer[Worked solution]
   The save point names position 3 and serial 3. When the save ends, `MarkSaved` finds serial 3 and stores the saved position 3. Four actions are applied, and 4 differs from 3, so the scene is modified. That is true, because edit 4 is not in the file.

   The first undo removes edit 4. The position is 3 again, so the scene is clean. The second undo removes edit 3, the position is 2, and the scene is modified again.

   Edit 5 comes at position 2. The saved position 3 is greater than the position, so the history drops the redo branch and stops pointing at a save point. The history now holds actions 1, 2 and 5 at position 3. The number 3 matches the old saved position, but action 3 is gone, so no state of the history equals the file. The scene stays modified, and only a new save can make it clean.
   :::

2. **Basic.** A game runs at 60 fixed steps in each second, and 12 steps have run when a command script pauses it. The script runs `play.step` with 30 steps, and then a query that returns the fixed step count, with an `until` and an `expect` that the count has a `min` of 50. How many attempts does the query make, how many fixed steps run while it waits, and how much game time has passed at the end? What changes if the step's bound is `{ "steps": 5 }`?

   :::answer[Worked solution]
   After the pause and the 30 stepped steps, the count is 12 + 30 = 42. Attempt 1 sees 42 and misses. In a paused game the runner then runs one fixed step before the next attempt, so attempts 2, 3 and so on see 43, 44 and up to 50. Attempt 9 sees 50 and meets the condition, so the query makes 9 attempts and 8 fixed steps run while it waits.

   The game has now run 50 fixed steps, which is 50 / 60 = 0.83 s of game time. The number is the same on a machine that draws 30 frames in each second and on one that draws 300, because the wait counts fixed steps. The journal holds one entry for the step, the final attempt, and it records `attempts` as 9.

   With the bound of 5 steps, the wait ends after 6 attempts, which see 42 to 47, when 5 fixed steps have run. The condition still misses at 47, so the step fails and the script is marked failed. The later steps still run, and the editor ends with exit code 1.
   :::

3. **Medium.** A project is open, the scene's journal file does not exist, and the last write was long ago. At 0 s you create `Crate`, and from 1 s to 25 s you change its color once in every second. You also move `Rock` under `Crate` at 12 s and `Lamp` under `Crate` at 23 s. When does the editor write the journal, and what does the file hold if power fails at 26 s?

   :::answer[Worked solution]
   The creation at 0 s is written within a frame, because the last write is more than 10 s old. While you work without a pause, the next writes come 10 s after each write, at 10 s and at 20 s. You stop at 25 s, and the journal then waits 2 s of quiet, so the last write comes at 27 s. The writes are therefore at 0, 10, 20 and 27 s.

   At 26 s the newest file is the one written at 20 s. A color change moves no entity, so it folds into the segment before it. The creation at 0 s starts segment 1, and the move at 12 s starts segment 2. The file holds 2 segments.

   Lost are the steps after the write at 20 s: the color changes at 21 to 25 s and the move of `Lamp` at 23 s, which would have started a third segment. A crash costs about 10 s of continuous work, and here it costs 6 s. Had power failed at 28 s, the file would hold 3 segments and no step would be lost.
   :::

4. **Medium.** The editor camera has the target $(0, 0, 0)$, the distance 10, yaw 0 and pitch -30 degrees. The scene holds only the grid plane at $y = 0$, and you drop a 1 m cube prefab, whose origin is at its center, on the center of the Scene view. Where is the camera, and where does the crate land? Then you point at a pixel above the horizon, whose ray has the direction $(0, 0.6, -0.8)$: where does the crate go, and how many undo steps do `camera.set` and the two drops record?

   :::answer[Worked solution]
   Yaw 0 looks along -Z, and a negative pitch looks down. The forward direction is $(0, \sin(-30°), -\cos(-30°)) = (0, -0.5, -0.866)$. The position is the target minus the forward direction times the distance, which is $(0, 5, 8.66)$.

   The ray through the center of the view starts at the camera and runs along the forward direction. No surface is in the scene, so `Place` tries the grid plane. The ray reaches $y = 0$ when $5 - 0.5t = 0$, so at $t = 10$ m, which is within 500 m. The point is $(0, 0, 0)$, and the normal is $(0, 1, 0)$. The lift is $|n| \cdot e - n \cdot c = 0.5 - 0 = 0.5$, so the translation is $(0, 0.5, 0)$.

   The second ray climbs, so it never meets the plane. Nothing is hit, and `placedOn` is `inFront`. With the default fallback of 10 m, the point is $(0, 5, 8.66) + 10 \cdot (0, 0.6, -0.8) = (0, 11, 0.66)$, and the center of the crate goes there.

   The camera command records no undo step, because a view change is no edit. Each drop is one `asset.place` command and records one step, and the hovering ghost records none. The total is 2 steps, and **Ctrl+Z** removes the last crate, never a camera move.
   :::

5. **Medium.** An agent runs `entity.create` for `Crate`, `selection.set`, `play.start`, `entity.create` for `Bullet`, `play.stop`, and then `entity.rename` of `Crate` to `Box`. Between `play.stop` and the rename, you drag `Crate` with the gizmo in the Scene view. What does an export of the session hold, how does it count what it omits, and what does the undo history hold?

   :::answer[Worked solution]
   Only `Edit` commands that did not act on the running copy are repeated. `entity.create` for `Crate` and `entity.rename` are such commands, so the script has 2 steps and 2 edits. The rename refers to the identifier (ID) that the creation returned, so the export binds that ID in the first step and uses a reference in the second.

   `selection.set` and the `play.*` commands are `Session` commands, and no replay repeats them. `entity.create` for `Bullet` is an `Edit`, but it ran on the running copy, and the copy is gone after `play.stop`. The export omits it and counts it in `skippedWhilePlaying`, which is 1.

   The drag recorded its undo step outside a command, so the journal counts it in `editsOutsideCommands`, which is 1, and warns that the script does not repeat it. `unrepeatableEdits` is 0, because no other kind of command recorded a step.

   The history holds 3 steps: the creation of `Crate`, the drag and the rename. Edits to the running copy are not recorded, so `Bullet` has no step.
   :::

6. **Hard.** A project has `Textures/Rust.png`, which `Materials/Rusty.stmat` uses, and an open scene `Scenes/Main.stscene`, to which you added an entity `Lamp` that uses `Materials/Glow.stmat` without saving. An agent calls `asset.delete` on `Rust.png`, on `Glow.stmat`, on `Main.stscene` with `force`, and on `Glow.stmat` with `force`. Say what each call does. Then a colleague's version control writes a different file to the path of `Glow.stmat`: what does **Ctrl+Z** do, and does the history keep the step?

   :::answer[Worked solution]
   Call 1 asks `AssetReferences::Find` for the users of `Rust.png`. The index of recorded referencers holds `Rusty.stmat`, and there is no `force`, so the call fails with the list in `referencedBy`. Nothing moves, and no step is recorded.

   Call 2 has no recorded referencer, but the search also reads the open scene from memory, and the unsaved `Lamp` uses the material. The call fails with a message that names the scene and `Lamp`. A search of the file alone would have missed it and deleted a material that the scene needs.

   Call 3 fails although `force` is set, because the open scene can never be deleted.

   Call 4 passes `force`, so the users no longer stop it. The files, the `.meta` and the cached import go to the trash, and one step is recorded. `Lamp` keeps a missing reference. The step does not change the scene, so it never marks the scene modified. The person gets a message that an agent deleted an asset, because the call did not come from the interface.

   When the colleague's file sits at the path, undo fails, because it restores the same handle only if nothing else is there. Strata never writes over a file. The history keeps the step, so you can undo again after the file is gone. A failed redo is different: it drops the step and all after it.
   :::

7. **Hard.** A layer has cells of 64 m, and a top-level `Crate` stands at $(60, 0, 10)$ in the cell $(0, 0)$. Both $(0, 0)$ and $(1, 0)$ are loaded, and you run `component.set` with the translation $(70, 0, 10)$ and save. You then fly the camera far away, so the streamer unloads both cells, and you press **Ctrl+Z**. Say what happens, which cells are dirty at each point, and what the second **Ctrl+Z** does once the cells have loaded.

   :::answer[Worked solution]
   The target cell is $(\lfloor 70 / 64 \rfloor, \lfloor 10 / 64 \rfloor) = (1, 0)$. It is loaded, so `Recell` runs inside `CommitEdit` and moves the crate into it. The move and the edit are one undo step. The step marks the cells of its states before and after, so $(0, 0)$ and $(1, 0)$ are dirty.

   The save is two requests. The first writes the two dirty cells from one snapshot, and the marks clear when it begins. The persistent scene stays out, because it is not dirty and a cell is. The second writes the World document, and the scene counts as saved after it. The cells stay pinned while the save writes them, and after it nothing keeps them loaded.

   Both cells are now unloaded. Before undo runs, `CheckCells` asks whether the cells of the step's states are loaded. They are not, so `RequestCell` pins both and the undo fails with a notice that says to undo again once they are in. The step stays in the history.

   After both cells load, the second **Ctrl+Z** works. The crate returns to $(60, 0, 10)$ in the cell $(0, 0)$, and both cells are dirty again. Marks stay after an undo, even back to the saved state, so the next save writes both cells with the same data again. The cost of a repeated write is smaller than comparing every cell with its file on every step.
   :::

8. **Hard.** A designer wants to test that a game spawns a second crate 30 fixed steps after the first. The game is playing and paused, and the designer sends one `editor.batch` with `entity.create` for `A`, `play.step` with 30 steps, and `entity.create` for `B`. What does the editor do, which command script tests the idea, what does `Stop` leave behind, and why would a wait of 30 frames be wrong?

   :::answer[Worked solution]
   `play.step` waits through a poll function, so it carries `MayDefer`. A batch runs in one frame as one undo group and cannot wait, so `editor.batch` refuses the command before it runs anything. Neither crate is made, and no step is recorded.

   A script runs its steps one after another, and a step that waits holds the later ones back. It runs from the start, so it starts and pauses the game itself. The steps are `play.start`, `play.pause` with `paused` set to true, and `entity.create` for `A`. Then come `play.step` with 30 steps and an `expect` of 30 on `/stepsRun`, and `entity.create` for `B`. Each step is a separate journal entry, and the script fails with exit code 1 when an `expect` misses.

   The two crates exist only in the running copy. Commands act on the active scene, so they change the copy, record no undo step and carry a warning. `Stop` releases the copy, and both crates vanish. Pressing undo afterward removes nothing, because the history never held them.

   A wait of 30 frames would be wrong twice. The game is paused, so frames run no fixed step at all unless a step is asked for. In a running game a frame may run no fixed step or several, so the game time would differ between machines. The fixed step is the game's own time base. That is why `play.step` and `until` count steps: the same steps give the same state on every machine.
   :::
