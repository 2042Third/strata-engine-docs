---
id: basics/review
title: "Review: foundations"
description: "The questions of every page of the part on foundations, and exercises that use several of its pages together."
tracks: [G, B, E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** A file has a 16-byte header, records of 24 bytes and a size of 200 bytes. The 4 bytes at offset 8 of the header are `00 01 00 00`, and the format is little-endian. Which count do they hold, and does the reader accept it?

   :::answer[Worked solution]
   Little-endian puts the lowest byte first, so the number is read from the last byte to the first: `00 00 01 00`. That is 0x0100, which is 1 × 256 = 256. Read as big-endian, the same bytes would give 0x00010000 = 65,536, so the byte order changes the count a lot.

   The reader bounds the count by what the file holds. The room after the header is 200 − 16 = 184 bytes, and 184 / 24 drops its remainder to 7. A count of 256 is more than 7, so the reader refuses the file before it allocates anything. The division form is the safe one, because a product of the count and the record size can wrap.
   :::

2. **Basic.** A dynamic array starts with capacity 1 and doubles whenever an append finds it full. You append 100 items. Which capacity does it end with, how many times did it grow, and how many items did the growths copy in all?

   :::answer[Worked solution]
   The capacity is always a power of two: 1, 2, 4, 8, 16, 32, 64, 128. An append grows the block when it finds the block full, so the appends number 2, 3, 5, 9, 17, 33 and 65 each start a growth: 7 growths. After the 65th item the capacity is 128, which holds all 100 items, and 128 = $2^7$ matches the 7 doublings.

   A growth copies the items of the full block: 1 + 2 + 4 + 8 + 16 + 32 + 64 = 127. For 100 appends that is 1.27 copies per append, which shows why doubling keeps the cost of an append constant on average.
   :::

3. **Medium.** A parent's world matrix scales by 2 and then moves by (0, 0, 3). A child sits at the local position (1, 0.5, 0) of the parent. The camera is at (0, 0, 8) without rotation, looks along -Z and sees 90 degrees from top to bottom; the window is 800 by 400 pixels. At which pixel is the child's center drawn?

   :::answer[Worked solution]
   First the world position: scale (1, 0.5, 0) by 2 to get (2, 1, 0), then move by (0, 0, 3) to get (2, 1, 3).

   The view matrix is the inverse of the camera's world transform, so it moves the world by (0, 0, -8). The view-space position is (2, 1, -5), and the distance in front of the camera is d = 5.

   The image plane position is (2 / 5, 1 / 5) = (0.4, 0.2). The aspect ratio is 800 / 400 = 2 and tan(45 degrees) = 1, so the half-height is 1 and the half-width is 2. The normalized device coordinates (NDC) are (0.4 / 2, 0.2 / 1) = (0.2, 0.2). Both lie between -1 and 1, so the child is inside the picture.

   The pixel is column (0.2 × 0.5 + 0.5) × 800 = 480 and row (0.5 − 0.2 × 0.5) × 400 = 160. The child is a little right of the middle and above it.
   :::

4. **Medium.** A camera follows its target with a smoothing rate of k = 6 per second. Find the weight of one frame at 60 and at 30 frames per second, and the number of frames each needs to close 99 % of a gap. Then say what the weight `k * deltaTime` does in a frame of 0.5 s.

   :::answer[Worked solution]
   The weight that does not depend on the frame rate is $1 - e^{-k \, \Delta t}$. At 60 frames per second $k \, \Delta t = 6 / 60 = 0.1$, so the weight is 1 − $e^{-0.1}$ = 0.095. At 30 frames per second $k \, \Delta t = 0.2$ and the weight is 1 − $e^{-0.2}$ = 0.181.

   Each frame keeps the share $r = e^{-k \, \Delta t}$ of the gap, and the gap is below 1 % when $n \ge \ln 0.01 / \ln r = 4.605 / (k \, \Delta t)$. That is 4.605 / 0.1 = 46.05, so 47 frames at 60 per second, and 4.605 / 0.2 = 23.03, so 24 frames at 30 per second. In time both are about 4.605 / 6 = 0.77 s: 0.78 s and 0.80 s once rounded up to whole frames. The frame rate changes the number of frames and not the time.

   In a frame of 0.5 s the product is 6 × 0.5 = 3. A lerp with the weight 3 multiplies the gap by 1 − 3 = −2. The camera lands on the other side of the target at twice the distance, and the next large frame repeats it. This is the explosion of a step that is too large. The exponential weight is 1 − $e^{-3}$ = 0.95, always between 0 and 1, so the camera lands near the target.
   :::

5. **Medium.** A row of pixels stores the sRGB values 0.2, 0.2, 0.8, 0.8. A blur with the kernel 1, 2, 1 divided by 4 is applied at the second pixel. Which stored value does the pixel get when you blur the stored values, and which when you blur light? Then do the same for a mip texel that averages the block 0.8, 0.8, 0.2, 0.2.

   :::answer[Worked solution]
   The weights 1/4, 2/4 and 1/4 add to 1, so a flat area keeps its value. The second pixel has the neighbors 0.2 on the left and 0.8 on the right.

   Blurring the stored values gives (0.2 + 2 × 0.2 + 0.8) / 4 = 0.35. This mixes encoded numbers, and filtering needs linear values.

   For light, decode first: 0.2 gives 0.0331 and 0.8 gives 0.6038. The blur is (0.0331 + 2 × 0.0331 + 0.6038) / 4 = 0.1758. Encoding that gives 1.055 × 0.1758^(1/2.4) − 0.055 = 0.456. So the pixel should store 0.456, not 0.35, and the blur of stored values is too dark.

   The mip texel averages four texels at once. The decoded values 0.6038, 0.6038, 0.0331 and 0.0331 have the mean 0.3185, and the stored value is 1.055 × 0.3185^(1/2.4) − 0.055 = 0.60. The average of the stored numbers, 0.5, would show too little light.
   :::

6. **Medium.** A game moves a ball on a spring with the acceleration −x, starting at x = 1 and v = 0, and uses each frame's `deltaTime` as the step of the semi-implicit Euler method. After the player switches windows, one frame lasts 2.5 s and the ball vanishes. Compute two steps of 2.5 s, that frame and one more like it, name the cause, and say which fix keeps every machine on the same result.

   :::answer[Worked solution]
   The semi-implicit step changes the velocity first. With h = 2.5, the first step gives v = 0 + (−1) × 2.5 = −2.5 and x = 1 + (−2.5) × 2.5 = −5.25. The acceleration is now 5.25, so the second step gives v = −2.5 + 5.25 × 2.5 = 10.625 and x = −5.25 + 10.625 × 2.5 = 21.3. The distance from the center grows from 1 to 5.25 to 21.3 and keeps growing.

   The cause is the size of the step: for this spring the limit is a step of 2 s, and 2.5 s is above it, so the simulation explodes. In the six steps of debugging this is the guess. You observe it by logging x, v and `deltaTime` each frame, and you test it with one change: limit the step to 1/60 s and check that the ball stays near 1.

   The fix is a fixed step of 1/60 s with a cap on the steps of one frame, as Strata does with `FixedTimestep` and `MaxFixedStepsPerFrame`. A frame of 2.5 s then runs 8 steps, 0.133 s of game time; Strata keeps one more step for the next frame and drops the rest. Every machine runs the same steps, so the result is the same. Last, keep the check as a test that feeds a frame of 2.5 s.
   :::

7. **Hard.** A culling loop reads only the 8-byte `Radius` of 100,000 proxies. The struct is `struct Proxy { uint8_t Visible; float Center[3]; uint16_t Layer; double Radius; uint32_t Id; };`. Give its `sizeof` and the offset of `Radius`, and find an order of the members with a smaller size. Then compare the 64-byte cache lines that the loop loads for the original array, the array with the new order and an array that holds only the radii.

   :::answer[Worked solution]
   Place the members in order. `Visible` takes byte 0. `Center` needs a multiple of 4, so it takes bytes 4 to 15. `Layer` takes bytes 16 and 17.

   `Radius` needs a multiple of 8, so 6 bytes of padding come first and it takes bytes 24 to 31. `Id` takes bytes 32 to 35. The struct's alignment is 8, so its size rounds 36 up to 40, and the offset of `Radius` is 24.

   Largest first: `Radius` at 0 to 7, `Center` at 8 to 19, `Id` at 20 to 23, `Layer` at 24 and 25, `Visible` at 26. The size 27 rounds up to 32. A `static_assert` on `sizeof(Proxy) == 32` keeps the layout from changing.

   A cache line is 64 bytes. With the 40-byte struct, a radius lies every 40 bytes, which is less than a line, so every line of the array holds one: 100,000 × 40 / 64 = 62,500 lines. With 32 bytes it is 100,000 × 32 / 64 = 50,000 lines. A struct of arrays holds the radii alone: 100,000 × 8 / 64 = 12,500 lines, five times fewer than the original.
   :::

8. **Hard.** Four jobs run on four worker threads and produce 3, 0, 2 and 4 results. All results go into one array with no gaps, and each worker adds 1 to a counter `finished` when its job ends. The counter starts at 0, and the main thread reads the array when `finished` reaches 4. Design where each worker writes, which tool each shared value needs, and why the main thread may read the array safely then.

   :::answer[Worked solution]
   A prefix sum of the counts gives the starts: 0, then 0 + 3 = 3, then 3 + 0 = 3, then 3 + 2 = 5. The total is 5 + 4 = 9. Job 0 writes places 0 to 2, job 1 nothing, job 2 places 3 and 4, and job 3 places 5 to 8. The array has 9 places and exists before the workers start.

   Each place has exactly one writer, so no two threads touch the same data and the array needs no lock. Data that only one thread touches needs no tool.

   The counter is shared. With the plain line `finished = finished + 1`, two workers can both read 2 and both write 3, so a count is lost and the main thread waits for a 4 that never comes. The page on threads shows the same: a counter at 5 with two adds ends at 6, not 7. A counter needs an atomic: `finished.fetch_add(1)` is one step that no thread sees half done.

   The main thread reads `finished` with an atomic load. Each worker wrote its results before its add, and a release store and an acquire load carry the earlier writes with the value. The default order of an atomic gives that promise, so when the load shows 4, all nine results are visible. A relaxed add would be atomic but would carry no writes, and the main thread could read old results.
   :::
