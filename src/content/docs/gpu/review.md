---
id: gpu/review
title: "Review: the gpu and the renderer's core"
description: "The questions of every page of the part on the graphics card and the renderer's core, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** A test draws a triangle with the clip-space corners $(-1, 1)$, $(1, 1)$ and $(0, -1)$ into a 64 by 64 target.
   Are the pixels $(40, 10)$ and $(40, 60)$ covered? What would you see if Strata's clip space had +Y pointing down?

   :::answer[Worked solution]
   The page on coordinates gives the mapping $x_{pix} = 64 \cdot (0.5 \cdot x + 0.5)$ and $y_{pix} = 64 \cdot (0.5 - 0.5 \cdot y)$.
   The corners become $(0, 0)$, $(64, 0)$ and $(32, 64)$: the base lies on the top edge, row 0, and the tip is at the middle
   of the bottom edge.

   A pixel is tested at its center. The pixel $(40, 10)$ has its center at $(40.5, 10.5)$. At row 10.5 the left edge of the
   triangle is at column $10.5 / 2 = 5.25$ and the right edge at $64 - 5.25 = 58.75$, so the center is inside and the
   pixel is covered. The pixel $(40, 60)$ has its center at $(40.5, 60.5)$. There the edges are at 30.25 and 33.75, so the
   center is outside and the pixel is not covered.

   With +Y down, the corners would become $(0, 64)$, $(64, 64)$ and $(32, 0)$: the tip would point up. At row 10.5 the edges
   would be at 26.75 and 37.25, so $(40, 10)$ would be empty. At row 60.5 they would be at 1.75 and 62.25, so $(40, 60)$
   would be covered. Both results flip, which is why the triangle test checks pixels in both halves.
   :::

2. **Basic.** A laptop has an integrated graphics card with 12,288 `MiB` of device-local memory and a discrete card with
   4,096 `MiB`; both have every required feature. Which card does Strata select? On that card the central processing unit
   (CPU) needs 2 ms to record a frame and the card 6 ms to draw it, with two frames in flight.

   When does the CPU begin frame 2, and how long after the CPU begins frame 3 is its image finished? With a surface that needs at least 2
   images, how many swap chain images does the device ask for?

   :::answer[Worked solution]
   The scores are 12,288 + 100,000 = 112,288 for the integrated card and 4,096 + 1,000,000 = 1,004,096 for the discrete
   one. The discrete card wins, although it has a third of the memory, because the kind of card counts more than the memory.

   For the schedule, frame 0 is recorded from 0 to 2 ms and drawn from 2 to 8 ms. Frame 1 is recorded from 2 to 4 ms and
   drawn from 8 to 14 ms, because the card is busy until 8. Two frames are outstanding, so frame 2 waits for the fence of
   frame 0 and begins at 8 ms. It is recorded from 8 to 10 ms and drawn from 14 to 20 ms.

   Frame 3 waits for the fence of frame 1 at 14 ms, is recorded from 14 to 16 ms and drawn from 20 to 26 ms. Its image is finished
   12 ms after its recording began. A frame finishes every 6 ms: the card sets the pace, and the CPU waits 4 ms of each 6.

   The image count is the larger of the surface's minimum plus one and the frames in flight plus one: max(2 + 1, 2 + 1) = 3
   images.
   :::

3. **Medium.** A compute pass counts the lights of a 1000 by 600 view with groups of 16 by 16 threads. How many groups does
   the dispatch start, and how many threads lie outside the image?

   Four groups find 5, 0, 2 and 4 lights, and a second dispatch gives each group a range of an output array. Which ranges
   does it give? Both dispatches use one binding set, so who places the barrier between them, and how?

   :::answer[Worked solution]
   Each axis needs $\lceil \text{size} / 16 \rceil$ groups, written as $(\text{size} + 15) / 16$ with whole numbers: $(1000 +
   15) / 16 = 63$ across and $(600 + 15) / 16 = 38$ down, so 63 × 38 = 2,394 groups. They hold 2,394 × 256 = 612,864
   threads for 600,000 pixels, so 12,864 threads lie outside the image and do nothing.

   The scan turns the counts 5, 0, 2, 4 into start offsets: 0, then 5, then 5 + 0 = 5, then 5 + 2 = 7. The total is 11. Group
   0 writes slots 0 to 4, group 1 writes none, group 2 writes slots 5 and 6, and group 3 writes slots 7 to 10. No two ranges
   overlap, and the result never depends on timing.

   The second dispatch reads what the first wrote. NVRHI places a barrier by itself only when the binding set changes, and
   here the set stays the same. You therefore place it: call `setBufferState` with `UnorderedAccess` on the buffer, then
   `commitBarriers()`, between the two dispatches.

   Without it the scan may read half-finished counts, and the offsets differ from run to run. A group barrier would not
   help, because it covers only the threads of one group.
   :::

4. **Medium.** You add `Effects/Glint.comp.slang` to `Strata/shaders`. It reads `register(t5, space0)` and
   `register(s2, space0)`, a constant buffer at `register(b3, space0)`, and writes `register(u1, space0)`. The buffer holds
   `float Strength; float3 Tint; float Radius; float3 Offset;`. Give the Vulkan binding of each register, the std140 offsets
   and size of the buffer, and the fields that a C++ mirror with `glm::vec3` misplaces.

   After the build, the renderer logs that the shader is not part of the embedded set: what did you forget? Later a test
   of the effect, on the graphics processing unit (GPU), fails at `CHECK(gpu.GetNewErrorCount() == 0)` with a count of 1.
   Where do you stop in the debugger?

   :::answer[Worked solution]
   A register adds 0, 128, 256 or 384 to its slot for `t`, `s`, `b` or `u`, and the space is the set. In set 0 the four
   bindings are 5 for `t5`, 130 for `s2`, 259 for `b3` and 385 for `u1`.

   Under std140 a `float3` starts on a 16-byte boundary. `Strength` sits at 0, `Tint` at 16 and `Radius` at 28, in the 4
   bytes left after `Tint`. `Offset` starts at 32, and the 44 bytes round up to a size of 48. A C++ mirror with `glm::vec3`,
   which is 12 bytes with a 4-byte alignment, puts `Tint` at 4, `Radius` at 16 and `Offset` at 20, for a size of 32. Every
   field after `Strength` is misplaced, and nothing fails: the shader reads wrong numbers.

   The log means that `strata_add_shaders` has no line for the shader, or that you did not run the configure step after
   adding it. A new shader changes the list, so it needs a line, a new configure step and then a build. An edit inside a
   listed shader needs only the build.

   A validation error adds to the count that the test compares with zero. Put a breakpoint on `ErrorCount.fetch_add(1);` in
   both message callbacks, `message` for NVRHI and `DebugUtilsCallback` for Vulkan. When the error arrives, the call that
   caused it is on the stack.
   :::

5. **Medium.** The static vertex buffers of the geometry pool hold 65,536 vertices and are full, and the index arena has
   room. A mesh of 40,000 vertices and 90,000 indices arrives. How many bytes do its two ranges take?

   To what capacity does the pool grow, and how many bytes do the new vertex streams hold? What must a pass do that bound
   the old buffers, and what happens to those buffers?

   :::answer[Worked solution]
   A vertex range rounds up to a multiple of 16: 40,000 is one already. An index range rounds up to a multiple of 64:
   90,000 / 64 = 1,406.25, so 1,407 × 64 = 90,048 indices. A vertex takes 48 bytes and an index 4, so the ranges take
   40,000 × 48 = 1,920,000 and 90,048 × 4 = 360,192 bytes: 2,280,192 in all.

   No free range holds the mesh, so the pool grows. The new capacity is the larger of the doubled capacity, 131,072, and the
   capacity plus the request, 65,536 + 40,000 = 105,536. The larger is 131,072, and it is a multiple of 16. The streams hold
   131,072 × 12 = 1,572,864 bytes of positions and 131,072 × 36 = 4,718,592 bytes of attributes, 6 `MiB` in all.

   The pool copies the old data across on the graphics card and bumps the version of the buffers. A pass keeps its binding
   set only while the version stays the same: it remakes the set when the version changes, because the old set names the
   old buffers. The pool does not free the old buffers at once, because a submitted frame may still read them. It hands them
   to `Renderer::ReleaseDeferred`, so that they wait for the graphics card, then wait for their turn in the destruction
   budget.
   :::

6. **Medium.** A level load needs a texture of 67,108,864 bytes (64 `MiB`) in the same frames in which the editor drops 20
   textures. The upload budget is 1 ms a frame, the speed is 4,000,000 bytes per millisecond and the granule is 64 `KiB`.

   Destroying a texture costs 0.1 ms, and the destruction budget is 0.25 ms a frame. The pool holds idle staging of every
   size, and you may ignore the lag of the graphics card.
   How many frames does each job need?

   :::answer[Worked solution]
   The queue keeps a tenth of the frame in reserve, 0.1 ms, so the first step has 1 − 0.1 = 0.9 ms. That buys 0.9 ×
   4,000,000 = 3,600,000 bytes, below the limit of 4 `MiB`. Rounding down to whole granules of 65,536 bytes gives 54
   granules, 3,538,944 bytes, which cost about 0.885 ms.

   The second step finds 1 − 0.885 − 0.1 = 0.015 ms, which buys about 61,000 bytes, below one granule of 65,536. It plans
   zero bytes and the call stops. Only the first step of a frame is exempt.

   A frame therefore moves 3,538,944 bytes, and 67,108,864 / 3,538,944 = 18.96, so the texture needs 19 frames: 18 full
   frames, then 3,407,872 bytes. Destruction stops after the destruction that reaches the budget: 0.1, 0.2 and 0.3 ms, so
   three textures per frame. Twenty textures take 7 frames: six of three and one of two.

   The budgets are separate, so the two jobs overlap and neither slows the other. For the first 7 frames a frame spends
   about 0.885 ms on the upload and at most 0.3 ms on destruction. After that only the upload remains, for 12 more frames.
   The load takes 19 frames, about 317 ms at 60 frames per second, and no frame is long.
   :::

7. **Hard.** You add a pass named Dust to the scene renderer. It draws between the opaque and the transparent passes, and only
   when a switch is on. Say where its code goes in a frame, what the frame must look like when the switch is off, and which
   edits time the pass.

   On a device with 32 valid timestamp bits and 2 ns per tick, the begin timestamp of the pass reads 4,294,967,200 and the
   end reads 100. What is its time? The pass ran in frame 40: at the start of which frames can the frame profiler report it,
   and how many slots does its ring have with two frames in flight?

   :::answer[Worked solution]
   In `RenderFrame` the pass belongs after the opaque pass and before the transparent pass, inside an `if` on the switch.
   The frame tour shows the pattern: a marker, a stage and a switch, as the aerial perspective pass has them.

   With the switch off, the frame must equal the frame without the pass, bit for bit, and cost nothing. The renderer makes no
   target for the pass, starts no timer for its stage, and binds a dummy where a shader would read its output. A test
   compares the off image with the image from before the pass.

   To time the pass, add a member `Dust` to `RendererGPUStages`, register its stage after the opaque stage and before the
   transparent one in `RendererGPUStages::Get`, and call `gpuTimer.Next` with it where the pass begins. Where the pass ends,
   call `Next` with the stage whose work follows, so that no other pass's time lands in `Dust`. Then add the stage to the five lists that name the stages, so that
   the profiler's tables and the perf logs show it.

   The unsigned difference of the ticks is huge, because the counter wrapped. Masking it to 32 bits leaves 4,294,967,296 −
   4,294,967,200 + 100 = 196 ticks. At 2 ns per tick that is 392 ns, or 0.000392 ms. A plain signed subtraction would
   give a negative time.

   The ring closes the slot of frame 40 at the start of frame 41, and the answer comes two to three frames after the pass
   ran. The profiler can therefore report it at the start of frame 42 if the card is quick, or of frame 43. The ring has
   one slot for each frame in flight plus two: 4 slots.
   :::

8. **Hard.** A sign in the world has 80 different glyphs, each with a distance field of 90 texels wide and 60 tall. The
   text pass and then the game's user interface ask for glyphs of the same font, and the interface needs 10 new ones. Each
   frame's rasterization budget is 32 glyphs, and you may ignore the cost.

   How many cells does one glyph take, and how many pages does the sign need at best? In which frames does the sign
   complete, and in which does the interface get its glyphs?

   :::answer[Worked solution]
   A glyph takes $(\text{size} + 1 + 41) / 42$ cells per axis with whole numbers, because a cell is 42 texels wide and one
   gutter texel is added. Across: $(90 + 1 + 41) / 42 = 3$. Down: $(60 + 1 + 41) / 42 = 2$. A glyph takes a block of 3 by 2
   cells, 6 cells.

   A page of 512 by 512 texels holds 12 cells across and 12 down, 144 cells. At best it holds 144 / 6 = 24 glyphs, and the
   sign's 80 glyphs need 80 / 24 = 3.33, so 4 pages. That is below the limit of 8 pages, so no glyph is freed.

   The atlas rasterizes at most 32 glyphs a frame, so the sign appears in pieces: 32 glyphs in the first frame, 32 in the
   second and 16 in the third. A glyph that waits is pending: it keeps its advance and gets no quad.

   The overlay order puts the world text before the screen text and the passes that modules add, and the game's interface
   draws after the scene's text. The renderer lends the one budget of the frame to each pass in turn, and the pass takes
   back what is left. In frames 1 and 2 the sign spends all 32, so the interface's 10 glyphs stay pending. In frame 3 the
   sign needs 16 and 16 are left, so the interface gets its 10 glyphs in frame 3.
   :::
