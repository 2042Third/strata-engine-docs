---
id: make/review
title: "Review: making games"
description: "The questions of every page of the part on making games, and exercises that use several of its pages together."
tracks: [G, B]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part, so try each one before you open its worked solution.

1. **Basic.** Five coin instances stand under an entity `Course`, which has the Translation (5, 0, 0), a yaw of 90 degrees and a scale of 1. The third coin has the local position (0, 0, 3). The second coin overrides its material with a silver one, and the other four use the gold material of the prefab.

   (a) Where is the third coin in the world?

   (b) You set the scale of `Course` to 2 on all three axes. Where is the coin now, and what does the Inspector show for the coin's own Translation?

   (c) You move the root of the fourth coin and rename it. How many overrides does the prefab bar show for it?

   (d) You give the third coin an orange material and press **Apply to Prefab**. Which coins are orange, and which material does the second coin have?

   :::answer[Worked solution]
   (a) Turn the local position by the parent's yaw first: a yaw of +90 degrees around Y turns (0, 0, 3) to (3, 0, 0). Then add the parent's Translation: (3, 0, 0) plus (5, 0, 0) is (8, 0, 0).

   (b) The scale is the same on every axis, so scaling and turning give one result in either order. The scale doubles the local offset to (0, 0, 6), the yaw turns it to (6, 0, 0), and the move gives (11, 0, 0). The Inspector still shows (0, 0, 3), because a child's numbers count from its parent.

   (c) None. The root's transform and name belong to the instance, so moving and renaming a coin never counts as an override.

   (d) The apply writes the orange material into the prefab, and every instance without an override of the material follows. The first, third, fourth and fifth coins are orange. The second coin keeps its own override, so it stays silver.
   :::

2. **Basic.** A scene has a sun of 120,000 lux and a room that a lamp lights to 400 lux. **Auto Exposure** is off, **Exposure** is 0 and the tone curve is Filmic.

   (a) What do you see, and which value do you set for **Exposure**?

   (b) You change the curve to the Academy Color Encoding System (ACES) curve. Which **Exposure** keeps the brightness, and by which factor does the light scale?

   (c) By about how many stops do the sun and the room differ?

   (d) A night scene with a 0.25 lux moon looks like a gray day under **Auto Exposure**. Which setting do you change, and why is the tone curve the wrong place?

   :::answer[Worked solution]
   (a) A real sun is far above what a screen shows at no correction, so the picture is almost white. Set **Exposure** near -15, or turn **Auto Exposure** on again.

   (b) ACES shows middle gray about 0.8 stops darker, so you add +0.8: -15 + 0.8 = -14.2. A change of 0.8 stops scales the light by $2^{0.8} = 1.74$.

   (c) The ratio is 120,000 divided by 400, which is 300. A stop is a doubling: $2^8 = 256$ and $2^9 = 512$, so 300 lies a little above 8 stops, about 8.2.

   (d) Raise **Auto Exposure Min EV** above the brightness of the scene, so that the automatic exposure cannot add back the missing stops. In the camera's order, exposure comes first and the curve works on what exposure made. A curve cannot repair a scene that exposure delivered too bright.
   :::

3. **Medium.** A ball of mass 2 floats in a room with no friction. The fixed step is 1/60 s, the cap never binds and the accumulator starts empty. The game draws four frames of 0.04 s each. A script pushes the ball with a force of 10 newtons.

   (a) How many fixed steps does each frame run, and what stays in the accumulator after each frame?

   (b) The script applies the force in `OnFixedUpdate`, every step. What velocity does the ball gain?

   (c) Another script applies the same force in `OnUpdate`, once a frame. How many steps get the force, and what does the ball gain?

   (d) The time scale is 0.5 and the same four frames follow, with the script of (b). How many steps run, and what does the ball gain?

   :::answer[Worked solution]
   (a) The step is 1/60 s, which is 0.0167 s. Frame 1 adds 0.04 s: 2 steps run and 0.0067 s stay. Frame 2 holds 0.0467 s: 2 steps, and 0.0133 s stay.

   Frame 3 holds 0.0533 s: 3 steps, and 0.0033 s stay. Frame 4 holds 0.0433 s: 2 steps, and 0.0100 s stay. The counts are 2, 2, 3 and 2, which makes 9 steps.

   (b) The acceleration is 10 / 2 = 5 m/s². Each step changes the velocity by 5 / 60 = 0.0833 m/s. Nine steps give 9 × 0.0833 = 0.75 m/s.

   (c) A force acts during the next fixed step only. One call a frame therefore reaches one step of each frame, 4 steps of the 9, and the ball gains 4 × 0.0833 = 0.333 m/s. The result depends on the frame rate, which is why a push belongs in `OnFixedUpdate`.

   (d) The time scale multiplies the game time of each frame: 0.04 × 0.5 = 0.02 s. The accumulator holds 0.02 s, then 0.0233, 0.0267 and 0.03 s after the next frames, and each frame runs 1 step. The four steps give 4 × 0.0833 = 0.333 m/s, less than half of (b), although the script is the same.
   :::

4. **Medium.** A lift is a platform that your code moves up and down. A ball with a script `Thud` falls onto it, and the script plays an impact sound with a full-volume speed of 10 m/s and a minimum speed of 0.5 m/s. A looping source `Fountain` stands 9 m from the listener, with Min Distance 1 m, Max Distance 50 m and Rolloff 2.

   (a) Which body type does the lift need, and why not Dynamic?

   (b) When the contact starts, the ball moves down at 5 m/s along the normal and the lift moves up at 1 m/s. What volume does the script play?

   (c) The same ball later touches still ground at 0.5 m/s along the normal. What volume does the script play?

   (d) The first impact on a new level is silent, and the Console shows a warning. The script plays the clip as a one-shot and never requests it. What is the cause, and what is the fix?

   (e) What gain does the inverse model give for `Fountain`?

   :::answer[Worked solution]
   (a) The lift needs a Kinematic body: your code moves it along its path, gravity cannot pull it down, and it still pushes the ball. A Dynamic lift would sag under the ball and fall.

   (b) The ball and the lift move against each other, so the separating speed along the normal is 5 + 1 = 6 m/s. The faster body moves at 5 m/s, and half of that is 2.5. The speed is 6 + 2.5 = 8.5 m/s, and the volume is 8.5 / 10 = 0.85.

   (c) The separating speed is 0.5 m/s and half the larger speed adds 0.25, so the speed is 0.75 m/s. That is above the minimum speed of 0.5 m/s, so the touch makes a sound. The speed divided by 10 is 0.075, below the lowest volume of 0.1 that the clamp allows, so the script plays the impact at 0.1. A minimum speed above 0.75 m/s would leave the touch silent.

   (d) The clip loads in the background. A one-shot waits at most 0.25 s of game time for it, then drops it and warns. Request the clip in `OnCreate`, so that it is ready at the first impact.

   (e) The distance 9 m lies between the minimum and the maximum, so it stays. The gain is 1 / (1 + 2 × (9 - 1)) = 1 / 17, about 0.059.
   :::

5. **Medium.** The heads-up display (HUD) of Coin Run lives on a canvas that scales with the screen. Its reference resolution is 1920 by 1080 and its **Match Width Or Height** is 0.5. The time bar has the anchors 0 and 1 across the canvas and a size of -80 along that axis. A script sets its fill from the time left divided by the time limit of 40 s, and a text in the corner is 48 units high.

   (a) The window is 2560 by 1440. How long is the bar in canvas units and in pixels, and how many pixels high is the text?

   (b) The window is 2520 by 1080. What are the scale, the canvas in units and the bar's length in units?

   (c) The round has run for 10 s. Which fill amount does the script write, and how long is the filled part on the screen of (a), in pixels?

   (d) The player pauses with a time scale of 0. What does the bar show after 5 s of real time, and does the restart key still work?

   :::answer[Worked solution]
   (a) The window is 4/3 of the reference in both directions, so the scale is 1.333 and the canvas still measures 1920 by 1080 units. The bar is 1920 - 80 = 1840 units long, which is 1840 × 1.333 = 2453 pixels. The text is 48 × 1.333 = 64 pixels high.

   (b) The width asks for a scale of 2520 / 1920 = 1.3125 and the height for 1.0. A match of 0.5 takes the middle, the square root of 1.3125 × 1.0, which is 1.146. The canvas measures 2520 / 1.146 = 2200 by 1080 / 1.146 = 943 units, and the bar is 2200 - 80 = 2120 units long.

   (c) The time left is 40 - 10 = 30 s, and the fill is 30 / 40 = 0.75. The script writes it with `SetProperty("UIImage", "FillAmount", fraction)`, because the bar is an image and `SetValue` moves only a slider or a toggle. The filled part is 0.75 × 2453 = 1840 pixels.

   (d) The delta time of `OnUpdate` is 0, so the time left does not change and the bar stays at its fill. The update still runs every frame and the input arrives unscaled, so the restart reads its key and works.
   :::

6. **Medium.** In the Tetris of the project page, `KeyRepeat` has `RepeatDelay` 0.17 s and `RepeatInterval` 0.05 s, and the game runs at 100 frames per second.

   (a) A player holds **Left** for 0.5 s. How many times does the piece move, and at which times?

   (b) The start level is 1 and `LinesPerLevel` is 4. Which level shows after 8 cleared lines?

   (c) A play-test plays 26 steps with `input.sequence` on a computer that draws 30 frames per second, and again on one that draws 144. Do the scores differ? How many seconds of game time does the sequence cover at the fixed rate of 60 steps per second?

   (d) A play-test clears one line, but its author dropped the `script.setField` step that sets `LinesPerLevel` to 1. It expects the text `Level: 2`. What does the error line say, how does the script end, and why does the level stay at 1?

   :::answer[Worked solution]
   (a) The piece moves once at the press, then at 0.17 s and every 0.05 s after: at 0.22, 0.27, 0.32, 0.37, 0.42 and 0.47 s. The next repeat, at 0.52 s, lies after 0.5 s. That makes 1 + 7 = 8 moves, provided that no wall stops the piece. Each repeat falls on a frame of 0.01 s.

   (b) The level is the start level plus the lines divided by `LinesPerLevel`: 1 + 8 / 4 = 3.

   (c) No. The sequence plays exactly one fixed step per frame, so both computers run the same 26 steps with the same keys, and a seed fixes the pieces. The computer with 30 frames per second only needs more time. The sequence covers 26 / 60 = 0.43 s of game time.

   (d) The error line reads `expected '/values/Text' to be "Level: 2", but it is "Level: 1"`. The later steps still run, and the editor logs `Command script finished with errors` and exits with code 1. The field keeps its default of 10, and 1 + 1 / 10 rounds down to level 1.
   :::

7. **Medium.** You work with an artificial intelligence (AI) agent. The Activity panel shows three rows in this order. Row 1: you rename `Ground` to `Floor` in the Hierarchy.

   Then you drag the Sun with the gizmo in one long movement. Row 2: the agent calls `prefab.instantiate` with 200 `instances`. Row 3: the agent runs an `editor.batch` of five steps, and every step works.

   (a) How many undo steps does this work leave, and how many does **Undo to here** on row 1 take back?

   (b) Later the agent runs another batch of five steps, and its fourth step fails. What does the scene hold afterwards, and what would change with `"atomic": false`?

   (c) You have unsaved changes when the agent opens another scene with `"force": true`, without asking you. What do you see, and how do you get your changes back?

   :::answer[Worked solution]
   (a) The rename is one step, and the whole drag is one step however long it takes. The 200 coins are one step, and an atomic batch is one step, so the work leaves 4 steps. The drag has no row, but it is a step of the history. **Undo to here** on row 1 undoes each step after that row: the drag, the coins and the batch, 3 steps, and it keeps the rename.

   (b) The batch is atomic by default, so the editor undoes steps 1 to 3 and records no undo step. The scene is as before step 1. With `"atomic": false` every step runs and the first three stay, so a failed batch leaves half of its work.

   (c) A toast names the agent, says that its command replaced the scene and offers **Recover...**. Without `force` the editor would have refused. The editor keeps your changes as recovery data of the project, so **File ▸ Recover Unsaved Changes...** brings them back.
   :::

8. **Hard.** In a third-person game the camera looks along -X, and the player pushes the stick up only. The body faces the yaw 350 degrees. The wanted yaw follows `atan2(-d.x, -d.z)` for the direction `d`. The body turns with `m_Yaw += std::remainder(wanted - m_Yaw, 360.0f) * weight`, where the weight is $1 - e^{-k\,dt}$ with $k = 8$, at 20 frames per second.

   (a) In which direction does the player walk, and which yaw does the body want?

   (b) By how many degrees does the body turn in the first frame, and which yaw does it hold then? How far would a plain `mix` of the two numbers have turned it?

   (c) The camera follows `GetWorldPosition()` at 30 steps a second while the player walks at 6 m/s, and the picture shakes. By how much does the position jump, and what do you change?

   (d) A ray from the camera's pivot hits a wall at 3.0 m, the arm is 6.5 m and the margin is 0.3 m. What is the arm now?

   (e) The player runs at 6 m/s off a ledge and presses jump 0.2 s later, with a coyote time of 0.25 s. Does the jump start, and how far from the edge is the player?

   :::answer[Worked solution]
   (a) The forward direction of the camera is (-1, 0, 0), so the player walks along -X. The yaw is $\operatorname{atan2}(1, 0) = 90$ degrees, because $-d.x$ is 1 and $-d.z$ is 0.

   (b) The plain difference is 90 - 350 = -260. `std::remainder(-260, 360)` is 100, the short way. The weight is $1 - e^{-8 \times 0.05} = 1 - e^{-0.4} = 0.3297$. The body turns 100 × 0.3297 = 33 degrees and holds the yaw 383, which is 23 degrees. A plain `mix` would add -260 × 0.3297 = -86 degrees and turn the body the long way round, to 264 degrees.

   (c) The position of a body that moves in fixed steps changes once a step, and the frames between read the same value. Each step moves the player 6 / 30 = 0.2 m, so the position jumps by 0.2 m. Read `GetDrawnPosition()` in `OnLateUpdate`, because the drawn position lies between the last two steps.

   (d) The ray shortens the arm at once: the arm is max(0.4, 3.0 - 0.3) = 2.7 m. It grows back smoothly toward 6.5 m when nothing is in the way.

   (e) The jump starts, because 0.2 s is at most the coyote time of 0.25 s. The player has run 6 × 0.2 = 1.2 m past the edge. The longest jump that still starts comes at 6 × 0.25 = 1.5 m.
   :::

9. **Hard.** An exported game runs at 50 frames per second on a display with a cap of 60. The Performance panel says GPU-bound. The graphics processing unit (GPU) is busy for 19 ms (114 % of a frame at 60 frames per second) of each frame. The central processing unit (CPU) is busy for 8 ms (48 %).

   (a) How long is a frame, and how much of a frame at 60 frames per second is that?

   (b) You save 3 ms (18 %) of script work. What is the new rate?

   (c) You choose a lower quality preset, and the GPU's time falls to 15 ms (90 %). What is the rate, and what does the panel say?

   (d) You add motion blur at 12 samples and depth of field, which cost 0.18 ms (1.1 %) and 0.20 ms (1.2 %) on the page about the look. What is the rate now?

   (e) You give 5,000 rocks ten different materials. Do the opaque draw calls rise?

   :::answer[Worked solution]
   (a) A frame lasts 1000 / 50 = 20 ms, which is 120 % of a frame at 60 frames per second. A frame at 60 frames per second lasts 16.7 ms (100 %).

   (b) Nothing changes: the rate stays at 50 frames per second. The GPU is the slower worker, and cutting script work does nothing for a GPU-bound game. The CPU's time falls from 8 ms (48 %) to 5 ms (30 %), and the GPU still needs 19 ms (114 %).

   (c) The CPU needs 8 ms (48 %) and the GPU 15 ms (90 %), so the work would fit in 15 ms, which is about 67 frames per second. The cap lets the display show only 60, so each frame lasts 16.7 ms (100 %) and the panel says **Capped**. Both workers finish early and the game waits.

   (d) The GPU now needs 15 + 0.18 + 0.20 = 15.38 ms (92 %), which is below 16.7 ms. The cap still sets the pace, so the rate stays at 60 frames per second. The costs of the look page come from a fast graphics card, and a slower GPU takes longer for the same effects. The two effects are free here until the work would pass the cap.

   (e) No. Draws follow the mesh, its submesh, its level of detail and the pipeline state, so ten materials make no new batch.
   :::

10. **Hard.** You export the project `SkyHop`, titled `Sky Hop`, pruned, to Linux. A menu script loads the course with the text `"Scenes/Course.stscene"`, and a win script finds the clip `Sounds/Win.ogg` by its path. A script keeps the best time in `best-time.txt`, and a coin counter lives in a variable of the course's script. On the exported game, the window turns black after **Play**, and no win sound comes.

   (a) Why does the game work in the editor and not in the export, for the scene and for the sound? What do you change for each?

   (b) Where do you search for the log, and what does it show for the sound?

   (c) You rename the title to `Sky Hop 2`. Do players keep their saves?

   (d) A level change must carry the counter of 5 coins to the next scene. Where does it live, and why does the variable fail?

   (e) The file `best-time.txt` holds `12:30`. What does `ParseWhole` return, and what could `std::stoi` do?

   :::answer[Worked solution]
   (a) A pruned export packs only what a scene or a field references. The editor holds every asset of the project, so a path works there. The course scene is named by a text, so no field references it, and the pack omits it: the game finds nothing and shows a black window. Make the scene an asset field of the menu script. The clip has the same fault, since no scene uses it: add `Sounds` or `Sounds/Win.ogg` to **Always Include** on the page **Export** of **Project Settings**, and export again.

   (b) In `~/.local/share/SkyHop/Logs/Game.log`, the data folder named after the project. The log holds a `FindAsset` warning that names the missing path of the clip.

   (c) Yes. Saves and logs live in a folder named after the project, `SkyHop`, and not after the title.

   (d) No entity survives `Game::LoadScene`, so the variable of the course's script is gone in the next scene. Keep the number in module state if it must last only while the game runs, or in a save file if it must survive the end of the game.

   (e) The colon is no digit, so `ParseWhole` returns nothing and the script can ignore the line. `std::stoi` would read 12 and ignore the rest, and for a text such as `abc` it would throw and turn the script off.
   :::
