---
id: draw/review
title: "Review: drawing a scene"
description: "The questions of every page of the part on drawing a scene, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part, so try each one before you open its worked solution.

1. **Basic.** A scene holds 200,000 mesh entities, and each has two instances. Their proxies have the indices 0 to 199,999.

   (a) The entities of proxies 41 and 7 are destroyed, in this order. Then two new mesh entities appear. Which proxy indices do they get?

   (b) How many bytes does the scene's instance array hold, and how many MiB?

   (c) The whole scene is new, so its proxies upload within the frame's budget for new proxies. How many frames does the upload take, and how many proxies does each frame upload?

   (d) After the first frame, which key of `renderStats` is above 0, and what does a picture of that frame lack? What does the key show after the last frame?

   (e) Can a draw list entry name every instance of this scene? How many proxies of two instances fill the limit?

   :::answer[Worked solution]
   (a) `DestroyProxy` pushes the freed index on the free list, and `CreateProxy` takes the newest free index. The list received 41 and then 7, so the first new entity gets 7 and the second gets 41. Nothing moves, so the other 199,998 proxies keep their indices.

   (b) An instance is 64 bytes. There are 200,000 × 2 = 400,000 instances, which is 400,000 × 64 = 25,600,000 bytes, or 24.41 MiB.

   (c) A new proxy costs its record, 64 bytes, plus its two instances, 128 bytes: 192 bytes in all. The budget is 16 MiB, which is 16,777,216 bytes, and 16,777,216 / 192 = 87,381.3, so 87,381 proxies fit in a frame. Then 200,000 / 87,381 = 2.29 needs 3 frames: 87,381, 87,381 and 25,238 proxies.

   (d) After the first frame 200,000 − 87,381 = 112,619 proxies still wait with records of zeros, and they draw nothing. The key `deferredInstanceBytes` is above 0, and the picture lacks more than half of the scene. After the third frame nothing waits, so the key is 0.

   (e) A draw list entry names an instance in 27 bits, so a scene holds at most 134,217,728 instances. The 400,000 instances are far below the limit. Proxies of two instances fill it at 134,217,728 / 2 = 67,108,864.
   :::

2. **Basic.** A camera has a vertical field of view of 60 degrees, and its viewport is 1,080 pixels high. The tangent of 30 degrees is 0.577.

   A mesh has a bounding sphere of radius 1.5. Proxy P of this mesh stands in view 20 units from the camera, and proxy Q of the same mesh stands in view 80 units away.

   Strata uses its defaults: the threshold for High priority is a screen fraction of 0.05, and the prefetch distance is 100 units.

   (a) What are the screen fraction and the height in pixels of P and of Q?

   (b) Which priority does each proxy ask for, and which does the mesh get?

   (c) Beyond which distance does a lone proxy of this mesh stop asking for High priority?

   (d) A second mesh has a proxy 70 units behind the camera. What does the frame request for it? And for a proxy at 130 units?

   (e) In the first frame nothing is loaded. What does the frame draw for the first mesh and for its material?

   :::answer[Worked solution]
   (a) The screen fraction is the radius over the distance times the tangent of half the field of view. For P it is 1.5 / (20 × 0.577) = 0.130, which is 0.130 × 1,080 = 140 pixels. For Q it is 1.5 / (80 × 0.577) = 0.0325, which is 35 pixels.

   (b) P is above 0.05, so it marks its slot High. Q is below, so it marks the slot for Normal. The two proxies share one slot, marks only merge and a bit once set stays set, so the mesh is requested at High.

   (c) The fraction falls to 0.05 at d = 1.5 / (0.05 × 0.577) = 52 units. Past 52 units a lone proxy asks for Normal only.

   (d) A proxy behind the camera is out of view. At 70 units it lies within the prefetch distance, so the frame prefetches the mesh: a request at Low priority for an asset that nothing draws yet. At 130 units it lies outside, and the frame requests nothing.

   (e) A mesh that is not loaded is skipped. A material that is not loaded draws as the default material. A frame that used the default material cannot be replayed, so the next frame looks every handle up again.
   :::

3. **Medium.** A mesh in slot 9 has three levels without errors, and its halving threshold is 0.4. Look at its submesh 1, opaque, single-sided, not mirrored, not skinned and drawn in the view (cascade 0). Instance P has the screen fraction 0.15 and material slot 7. Instance Q has the fraction 0.5 and material slot 8.

   (a) Which level does each instance get?

   (b) Give both sort keys, in hexadecimal, when batching does not cross materials.

   (c) How many passes does the radix sort make for these two keys, and how many when batching does cross materials?

   (d) A second mesh has the relative errors 0.01 and 0.04 for its levels 1 and 2. The budget is 1.5 pixels and the viewport is 1,200 pixels high. Which level does it get at the fractions 0.1 and 0.05?

   (e) In frame t, Q shows level 0 with no fade. In frame t + 1 its fraction falls to 0.15 and the target becomes level 2. Give the fade codes of its two entries in frames t + 1 and t + 4, and the share of pixels of a tile that each level draws in frame t + 4.

   :::answer[Worked solution]
   (a) Level 1 starts below the threshold 0.4, and each doubling that stays below it adds a level, up to the last. P has 0.15, so level 1 applies. The doubled fraction 0.30 is below 0.4 and a level 2 exists, so level 2 applies. The next doubling, 0.60, is not below 0.4, so P draws level 2. Q has 0.5, which is not below the threshold, so Q draws level 0.

   (b) The key holds the mesh from bit 37, the submesh from bit 21, the level from bit 16 and the material in the low 16 bits. P is 9 × 2^37 + 1 × 2^21 + 2 × 2^16 + 7, which is `0x12000220007`. Q is 9 × 2^37 + 2^21 + 0 + 8, which is `0x12000200008`.

   (c) The sort makes one pass for each byte in which some key differs. The two keys differ by `0x2000F`: byte 0 holds the materials 7 and 8, and byte 2 holds the levels. That makes 2 passes. When batching crosses materials, the material bits are 0, the keys differ only in byte 2 and the sort makes 1 pass. Both cases still make 2 batches, because the levels differ.

   (d) The error rule scans from the coarsest level down. Its threshold is the budget divided by half the viewport height: 1.5 / 600 = 0.0025. At the fraction 0.1, level 2 projects 0.04 × 0.1 = 0.004, which is above the threshold. Level 1 projects 0.01 × 0.1 = 0.001, which fits, so the mesh draws level 1. At 0.05, level 2 projects 0.002, which fits, so the mesh draws level 2.

   (e) In frame t + 1 the step is 1. The entry of level 2 has the code 1 and the entry of level 0, the level that fades out, has 1 + 16 = 17. Each frame moves the step on by one, so frame t + 4 has the step 4: codes 4 and 20. The new level draws where the dither threshold is below 4, which is 4 pixels of 16, a quarter. The old level draws the other 12, three quarters.
   :::

4. **Medium.** A mesh instance has the scale (−2, 1, 1) and no rotation. Every mesh below has one submesh and one level, is single-sided and not skinned, and draws in the view.

   (a) Does the proxy get the `Mirrored` flag, and when is that decided?

   (b) What does `TransformNormal` return for the normal (1, 1, 1) before the caller normalizes it? What is the unit normal?

   (c) A triangle has the corners (0, 0, 0), (1, 0, 0) and (0, 1, 0), counter-clockwise seen from the +z side. Which winding does it have on screen after the scale, and which pipeline draws it?

   (d) A scene holds 500 instances of one mesh: 350 plain and 150 mirrored. The plain ones use 5 materials, and the mirrored ones use 3 of them. How many opaque draws does the scene make with `BatchAcrossMaterials` off, and how many with it on?

   (e) A plain instance with the scale 1 stands at x = 100,000, and the camera stands at x = 99,990. Two vertices lie at the local x of 0 and 0.003. Say what a world position in float does to them, and what the shader's subtraction does.

   :::answer[Worked solution]
   (a) The determinant of the upper 3 by 3 part is −2 × 1 × 1 = −2, which is negative, so the instance mirrors. The renderer sets the flag when it places the proxy, so no later code computes the determinant again.

   (b) The shader adds up three cross products of the matrix's columns, weighted by the normal's parts.

   The columns are (−2, 0, 0), (0, 1, 0) and (0, 0, 1). The products give (1, 0, 0), (0, −2, 0) and (0, 0, −2), so the sum for (1, 1, 1) is (1, −2, −2). The instance is mirrored, so the function flips the sign: (−1, 2, 2). Its length is 3, so the unit normal is (−1/3, 2/3, 2/3). The inverse transpose of the scale gives (−0.5, 1, 1), which points the same way.

   (c) The corners go to (0, 0), (−2, 0) and (0, 1). The step from the first to the second corner points left and the step to the third points up, and a turn from left to up is clockwise. So the triangle is clockwise on screen, and a mirrored draw uses the pipeline with clockwise fronts, which counts it as a front face.

   (d) A mirrored draw has its own key bit and pipeline, so it never shares a batch with a plain one. With the option off, a batch also splits by material: 5 + 3 = 8 draws. With it on, the material leaves the key, so the two groups each make one draw: 2 draws.

   (e) The spacing of floats between 65,536 and 131,072 is 2^16 / 2^23 = 2^−7 = 0.0078 units. The offset 0.003 is below half a step, 0.0039, so a world position rounds both vertices to the same value, and the 3 mm vanish. The shader subtracts first: the translation 100,000 and the camera 99,990 are whole numbers, so the difference 10 is exact. Between 8 and 16 the spacing is about 0.00000095, so 10.003 keeps the detail. The same rule makes the central processing unit (CPU) subtract in double before it uploads a light or a line.
   :::

5. **Medium.** A texture has 4,096 texels on a side and 13 levels, and the material tiles it twice.

   A cube of half size 1 faces the camera, and its centre is 6.4 units away. Its bounding sphere has a radius of 1.73, and the nearest point of its bounds is 5.4 units away. The camera has a vertical field of view of 90 degrees and a viewport of 1,080 pixels.

   One unit of the texture coordinates spans one world unit, and the instance's scale is 1. Only the levels 9 to 12 of the texture are resident.

   (a) Which priority does the cube's mesh ask for?

   (b) How many pixels does one unit of the coordinates span, and which level does the texture want?

   (c) The streamer queues a read for the missing levels at the coverage 0.4. Three other reads wait: B has 1 level at coverage 0.9, C has 2 levels at 0.5, and D has 1 level at 0.02 and comes from a camera cut. In which order are the four served?

   (d) The cube moves away until one unit spans 1 pixel. Which level does the texture want?

   (e) A developer stores the texture's bindless slot in the cube's draw record, when the cube loads. What goes wrong after the read of (c) finishes?

   :::answer[Worked solution]
   (a) The screen fraction is 1.73 / (6.4 × 1) = 0.27, because the tangent of 45 degrees is 1. That is above 0.05, so the mesh is High.

   (b) One world unit at distance 1 spans 1,080 / (2 × 1) = 540 pixels. At the nearest distance of 5.4 it spans 540 / 5.4 = 100 pixels, and the coordinates and the scale change nothing.

   The texels of one unit are 4,096 × 2 = 8,192. The wanted level is the largest whole number below log2(8,192 / 100) = log2(81.9) = 6.36, which is 6.

   (c) The texture has the levels 9 to 12, so it lacks 6, 7 and 8: 3 levels. The score is the missing levels times the coverage: 3 × 0.4 = 1.2. B scores 0.9, C scores 1.0 and D scores 0.02. A camera cut raises the priority of a read to Normal, and the others ask at Low, so D goes first. The order is D, then A (1.2), C (1.0) and B (0.9).

   (d) A unit drawn no larger than one pixel wants the coarsest level, which is level 12.

   (e) The raise makes a new graphics texture, copies the resident levels into it and swaps the bindless slot. The record keeps the old slot, so the cube reads a texture that no longer holds the newest data, or one that is gone. The fix is to resolve the slot every frame with `Texture::GetBindlessSlot`.
   :::

6. **Hard.** A frame renders a depth buffer of 9 by 5 pixels with the GPU-driven path. The depth pyramid's level 0 is half the buffer. Its depths, in reversed Z, are:

   | Row | Column 0 | Column 1 | Column 2 | Column 3 | Column 4 |
   | --- | --- | --- | --- | --- | --- |
   | 0 | 0.30 | 0.20 | 0.50 | 0.40 | 0.45 |
   | 1 | 0.35 | 0.25 | 0.60 | 0.55 | 0.15 |
   | 2 | 0.70 | 0.80 | 0.90 | 0.65 | 0.60 |

   (a) What are the sizes of level 0, level 1 and level 2, and what are the depths of level 1?

   (b) A box covers the pixels x from 2 to 7 and y from 1 to 3. Which level and which texels does the test read? Is the box hidden when its nearest depth is 0.18, and when it is 0.12?

   (c) The box of 0.12 belongs to proxy B, which has 2 instances. Proxy A has 3 instances and proxy C has 5, and both stay visible. What are the starting offsets of the three records, and the length of the draw list?

   (d) In frame 100 the camera cuts to a new place. What does phase 1 draw, and does the frame still show every visible object? Which path chooses the asset requests of frame 100 if the newest ready feedback is from frame 98?

   :::answer[Worked solution]
   (a) Level 0 is the buffer's size halved and rounded up: 5 by 3. Each later level is half the one above, rounded down, and at least 1: level 1 is 2 by 1 and level 2 is 1 by 1. A texel of level 1 keeps the smallest depth, the farthest, of the level-0 texels it covers.

   A texel of the last row or column also reaches over what lies past the halved size. The only row is the last, so it covers all three rows. Texel 0 covers the columns 0 and 1: its smallest depth is 0.20. Texel 1 is the last column, so it covers the columns 2 to 4, and its smallest depth is 0.15, from column 4. Level 1 holds 0.20 and 0.15.

   (b) Level 0 texels are 2 pixels wide, so the pixels x 2 to 7 and y 1 to 3 fall on the texels 1 to 3 and 0 to 1. That spans 3 texels across, which is more than 2, so the test climbs to level 1.

   There the pixels shift twice: x runs from 0 to 1 and y stays 0. Both fit in level 1's two texels, so the test reads the texels 0 and 1, four reads in all. Its farthest depth is the smallest, 0.15. A box with the nearest depth 0.18 is not below 0.15, so it is kept. A box with 0.12 is below 0.15, so it is hidden.

   The 0.15 comes from column 4, which the box does not touch: the test is conservative and may keep a hidden box, never hide a visible one.

   (c) The counting pass gives A 3, B 0 and C 5, because the hidden proxy keeps no instance. Each record starts where the counts before it end: A at 0, B at 3 and C at 3. The draw list has 3 + 0 + 5 = 8 entries.

   (d) After a cut no visibility bit is set, so phase 1 draws nothing. The pyramid is empty, so phase 2 keeps everything inside the frustum and draws it in the same frame. Nothing is missing, and the frame only costs more. For the requests, feedback must be newer than the last cut, so the feedback of frame 98 does not count, and the CPU walks the view. Requests follow feedback again once a frame at or after the cut has written its own, which reaches the CPU two to three frames later.
   :::

7. **Hard.** A renderer that asks for motion vectors draws a scene of 4,000 instance slots. Five robots of 40 joints each stand in it, so the palette holds 200 matrices, and the rest are crates. Assume that the renderer's history buffers hold exactly these numbers of elements and that no crate is the parent of a robot.

   (a) How many bytes does the history hold in all?

   (b) In one frame nothing changes. What does `UpdateSkinnedPoses` do, and how many elements does the history copy?

   (c) In the next frame one crate moves. Do the robots get new palettes? What does the history copy?

   (d) Assume that an animating robot rewrites its 40 palette entries and changes nothing else. How many robots must animate in one frame before the history copies the whole palette?

   (e) How many crates must move in one frame before the history copies all instance slots?

   (f) A capture renderer draws this scene for the first time with motion vectors on. Does that frame have motion, and what does it do to the viewport's history?

   :::answer[Worked solution]
   (a) The history costs 64 bytes for each instance slot and 48 bytes for each joint matrix: 4,000 × 64 = 256,000 and 200 × 48 = 9,600. The total is 265,600 bytes.

   (b) The versions of the poses, transforms, hierarchy and drawn transforms equal the saved ones and the dirty flag is clear, so the function returns before it visits a proxy. The write log has no entry after the history's version, so the history copies no element.

   (c) The transform version changed, so the function walks the skin proxies. Each robot has the same pose version, binding, joint count and animator-to-proxy matrix, so each is skipped and gets no new palette. The write log lists the crate's slot only, so the history copies 1 instance and no joint matrix.

   (d) A list of more than half of a buffer copies no faster than the buffer, so the history drops it for a whole copy. For the palette that is more than 100 of 200 entries. Two robots write 80 entries, which stay a list. Three robots write 120, which is over 100, so 3 robots make the palette copy whole.

   (e) The same rule for 4,000 slots: a list is dropped when twice its length is above 4,000. At 2,000 moving crates, 4,000 is not above 4,000, so the list stays. At 2,001 crates, 4,002 is above 4,000, so 2,001 crates make the copy whole.

   (f) A frame has a previous frame only if the renderer's last frame also asked for motion and drew the same scene. The capture renderer has no last frame, so its first frame has no motion, and `MotionHistory` of its statistics says so. The viewport's history is untouched: each renderer owns its copy and remembers its own write version, so the capture's draw changes nothing the viewport reads.
   :::

8. **Hard.** A teammate changes the forward pass so that it reads the fade's dither table with its rows and columns swapped.

   The pixel at row r and column c uses the entry at row c and column r. The depth prepass keeps the old reading. The table is

   | 0 | 8 | 2 | 10 |
   | --- | --- | --- | --- |
   | 12 | 4 | 14 | 6 |
   | 3 | 11 | 1 | 9 |
   | 15 | 7 | 13 | 5 |

   A rock changes from level 1 to level 2 in frame 40 and then fades, and the viewport shows holes in it. A thumbnail of the same rock shows none.

   (a) Which rule does the change break, and why does the equal depth test turn it into holes?

   (b) At step 3 the new level draws where the threshold is below 3. Which pixels of a tile do the prepass and the forward pass choose, and how many pixels disagree? Give the pixels as (row, column).

   (c) At which steps of the fade do the passes agree on every pixel, and in which frames does the rock show holes? In which step are the holes largest?

   (d) Why does the thumbnail show none?

   (e) Which test of the part's suites is built to catch this change, and what is the fix?

   (f) A skinned robot stands beside the rock in a frame that has motion. Another teammate proposes that the forward pass draw the robot with the plain variant of `Mesh.vert`, because the prepass already wrote its depth and its motion. Which variant must both passes use, and what does the viewer see with the proposal?

   :::answer[Worked solution]
   (a) The depth prepass and the forward pass must discard the same pixels of a cross-fade. The prepass wrote the depth of the new level where its table says so, and the other pixels hold the old level's depth. Where the forward pass chooses the other level, it draws a level at a depth that the prepass did not write. The equal test rejects the pixel, and nothing draws there.

   (b) The thresholds below 3 are 0, 1 and 2. The prepass has them at (0, 0), (2, 2) and (0, 2). The swapped reading puts them at (0, 0), (2, 2) and (2, 0), so the first two agree. At (0, 2) the prepass draws the new level and the forward pass the old one, and at (2, 0) the reverse. That makes 2 pixels of 16 that disagree.

   (c) Counting the same way for each step gives the pixels of 16 that disagree. The passes disagree on 0 pixels at the steps 1, 2, 4 to 6 and 8. They disagree on 2 pixels at the steps 3, 7, 9 and 15, and on 4 at the steps 10 and 14. They disagree on 6 at the steps 11 and 13, and on 8 at the step 12.

   Only the steps 3, 7 and 9 to 15 show holes. Step s falls in frame 39 + s, so the holes are in the frames 42, 46 and 48 to 54. The step 16 of frame 55 returns the code 0, and no mask applies. The holes are largest at step 12, frame 51, where 8 of 16 pixels disagree: half.

   (d) A renderer that makes single images, such as the thumbnail, turns fading off. Every code is 0 there, so no pass applies a mask and the passes cannot disagree.

   (e) The suite `GPU.SceneRenderer.LODFade` checks that levels covering the same pixels fade by the same mask in the forward pass. The fix is to read the table as the prepass does: both passes call `IsLODFadeDrawn` with the entry's code and the pixel's position.

   (f) Both passes must use the same vertex module, which for the robot is the skinned velocity variant of `Mesh.vert`. Every pass of a skinned mesh uses the skinned variant, and in a frame with motion the prepass and the forward pass both use the velocity variant. The plain variant places the vertices without the palette, so the forward pass computes positions that differ from those of the prepass. The `EQUAL` test accepts only a depth equal to the last bit, so the robot's pixels fail it, and the robot shows holes in every frame, not only during a fade.
   :::
