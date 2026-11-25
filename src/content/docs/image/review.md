---
id: image/review
title: "Review: the image"
description: "The questions of every page of the part on the image, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part, so try each one before you open its worked solution.

1. **Basic.** A desert scene has an average luminance of 2,048 nits, a glint of 1,000,000 nits and a shaded crack of 0.3 nit. Strata draws the first frame with a pre-exposure P of 1, and automatic exposure meters it. Assume that the metered exposure factor equals the one a manual `Exposure` gives for the average, and that the exposure key is 0.

   (a) What exposure value at sensitivity 100 (EV100) does a meter with K = 12.5 read, and which exposure factor puts the average at middle gray?

   (b) What does the glint store in the first frame, and how much too dark do the later passes see it?

   (c) Which P does Strata choose when the first metering returns?

   (d) With that P, what do the glint, the average and the crack store? Which of them is a problem for a half float?

   (e) A cloud halves the average to 1,024 nits. Does P step?

   :::answer[Worked solution]
   (a) $\log_2 2048 = 11$, and adding 3 gives EV100 14. The factor that puts the average at 0.18 is 0.18 / 2048, which is $2^{-13.47}$.

   (b) The value 1,000,000 × 1 is above the limit, so `SanitizeHDR` writes 65,000. Every later pass sees a glint 1,000,000 / 65,000, about 15 times too dark.

   (c) The target is the factor in stops minus 2 stops of headroom: -13.47 - 2 = -15.47. P is 1, which is stop 0, so the distance is 15.47, more than one stop, and P steps to the nearest power of two, $2^{-15}$. The frame is not settled until a readback of a frame drawn with $2^{-15}$ arrives.

   (d) The glint stores 1,000,000 × $2^{-15}$ = 30.5, which fits. The average stores 2,048 × $2^{-15}$ = 0.0625. The crack stores 0.3 × $2^{-15}$ = $9.2 \times 10^{-6}$, which is below the smallest normal value, 0.000061, so it is subnormal and keeps less precision. After the exposure it is 0.3 × $2^{-13.47}$ = $2.6 \times 10^{-5}$, which the display shows as black, so no visible detail is lost.

   (e) The factor doubles to $2^{-12.47}$, so the target is -14.47. That is 0.53 stop from -15, inside the dead band of one stop, so P stays.
   :::

2. **Basic.** A scene has **Anti Aliasing** on, and its `AntiAliasingMethod` is temporal anti-aliasing (TAA). Four players start it. Each has a different value in the `AntiAliasing` row: (a) `Scene`; (b) `FXAA`; (c) `Morphological`, on a graphics processing unit (GPU) that cannot make the textures of that method; (d) `Off`. For each player, say which method smooths the edges and which shader adds the dither.

   (e) Fast approximate anti-aliasing (FXAA) walks along an edge and stops after 1 pixel on one side and after 5 on the other. What is its edge offset?

   :::answer[Worked solution]
   (a) The row says `Scene`, so the scene's TAA runs in the chain. No spatial pass follows, so `Tonemap.frag.slang` writes the display image and adds the grain and the dither.

   (b) The row sets the method, so the frame uses FXAA, not TAA. The tone mapping writes a bare 10-bit image, and `FXAA.frag.slang` adds the grain and the dither. The grain must come last, because FXAA would read it as edges.

   (c) The morphological method is wanted, but its resources fail, so `RenderPostDisplay` finds `morphological` false, and the line `const bool fxaa = antiAliased && !morphological;` draws FXAA. The frame is marked degraded, and `FXAA.frag.slang` dithers.

   (d) The row `Off` leaves no method and no spatial pass, so `Tonemap.frag.slang` dithers.

   (e) The offset is 0.5 minus the nearer distance over the sum: 0.5 - 1 / (1 + 5) = 0.5 - 0.167 = 0.333.
   :::

3. **Medium.** A gray pixel is exposed to 0.36, one stop above middle gray. The scene uses the Filmic curve at its default look, a white balance of 6,500 K with tint 0, Contrast 1 and Saturation 1, and no lookup. A designer sets the slope of the grade to 2 on all channels, with offset 0 and power 1.

   (a) Which value reaches the curve, and how many stops above middle gray is it?

   (b) The Filmic table of the tone mapping page gives 0.5068 for that value. What does `Reinhard` give?

   (c) The sRGB curve turns 0.5068 into 0.7398. Which code of 255 is that? A rectangular dither stores it: what are the mean and the noise power? What does a triangular dither give?

   (d) The designer adds a lookup of 33 points on each axis, made in another tool, at intensity 1. At which texture coordinate does the shader sample for 0.7398, and between which points does the read mix?

   :::answer[Worked solution]
   (a) The slope multiplies scene-linear light before the curve, so 0.36 × 2 = 0.72. That is 0.72 / 0.18 = 4 times middle gray, two stops above it. The white balance is the identity, and a gray pixel is untouched by Saturation, so nothing else changes it.

   (b) `Reinhard` gives 0.72 / (1 + 0.72) = 0.4186. Filmic shows 0.5068, a brighter result at the same exposure, because it keeps more of the mid-tones.

   (c) The code is 0.7398 × 255 = 188.65. A rectangular dither stores 189 with the probability 0.65 and 188 with 0.35, so the mean stays at 188.65 and the noise power is $f(1 - f)$ = 0.65 × 0.35 = 0.23. A triangular dither has the power 0.25 at every value, and plain rounding would store 189 in every pixel, which is an error of 0.35 and a band.

   (d) The lookup holds display values, so it acts after the curve and the encoding, on the value 0.7398, and before the grain and the dither. The coordinate is $e (N-1)/N + 1/(2N)$ = 0.7398 × 32 / 33 + 1 / 66 = 0.71738 + 0.01515 = 0.7325. In points, the position is 0.7398 × 32 = 23.67: the read mixes point 23 with the weight 0.33 and point 24 with 0.67, per axis.
   :::

4. **Medium.** A game draws 3,000 rows with the default `BloomRadius`, a threshold of 2 and a knee of half the threshold. At one moment the pre-exposure P is $2^{-12}$ and the metered exposure factor is $2^{-10}$. A lamp pixel stores 0.625 in each channel of the high dynamic range (HDR) target.

   (a) How many levels does the bloom chain use, and with which weight on the deepest?

   (b) What is `BloomScale`?

   (c) Which brightness does the lamp pass into the chain?

   (d) What would a bloom pass that forgot to divide P out see for the lamp, and what would the player notice?

   :::answer[Worked solution]
   (a) The default radius is 64 / 1080 of the height, which is 177.8 pixels at 3,000 rows. The span is $\log_2 177.8$ = 7.47, so the chain uses 8 levels, the largest chain, and the deepest counts 7.47 - 7 = 0.47.

   (b) `BloomScale` is 1 divided by the span: 1 / 7.47 = 0.134.

   (c) The threshold acts on the exposed color: the stored value times the exposure factor over P. That is 0.625 × $2^{-10}$ / $2^{-12}$ = 0.625 × 4 = 2.5. The brightness 2.5 lies inside the knee, which is 1 wide on both sides of 2. The soft term is the square of clamp(2.5 - 2 + 1, 0, 2) over 4 × 1, which is 1.5 × 1.5 / 4 = 0.5625, and it beats the excess of 0.5. The pixel passes with the brightness 0.5625.

   (d) The pass would see 0.625 × $2^{-10}$ = 0.0006, far below the threshold, so the lamp would scatter nothing. The glow would vanish whenever P is small, as in a bright scene, and would return in a dim one. The same scene would bloom differently as P steps.
   :::

5. **Medium.** A game draws 1,440 rows with TAA, depth of field and motion blur on. Its component has `MotionBlurShutterAngle` 270 and `MotionBlurMaxLength` 0.03.

   (a) How long is the blur, in pixels, of a point that moves 50 pixels a frame? Answer again for 80 pixels and for 1.6 pixels.

   (b) What tile size does the tile pass use?

   (c) In one frame the camera jumps 12 world units. Which of the three passes run, what does the TAA history do, and which texture does the exposure read?

   (d) In a later frame the camera has moved 0.1 unit and the motion history exists. Which texture does the exposure read now?

   :::answer[Worked solution]
   (a) The shutter share is 270 / 360 = 0.75. For 50 pixels the blur is 37.5, which is below the clamp of 0.03 × 1,440 = 43.2, so it stays 37.5. For 80 pixels it is 60, which the clamp cuts to 43.2. For 1.6 pixels it is 1.2, below the floor of 1,440 / 1,080 = 1.33 pixels, so the pass drops it and the pixel keeps its color.

   (b) The tile is the larger of 8 and half the clamp rounded up: ceil(21.6) = 22 pixels.

   (c) A jump of more than 10 units is a camera cut. TAA still resolves the frame, but its history starts again with the weight 1, so the pixels show only the new frame's samples. Depth of field runs, because it needs only a lens and a perspective view. Motion blur does not run, because a cut makes the motion meaningless. The source starts at the TAA history and becomes the depth of field's output, so the exposure reads the depth of field image.

   (d) With no cut and a motion history, motion blur runs after depth of field, and its output becomes the source. The exposure reads the motion blur image.
   :::

6. **Medium.** A scene camera has `DepthOfField` on, a field of view of 40 degrees, the default sensor height of 24 mm, `Aperture` 2.8 and `FocusDistance` 4 m. The view has 1,080 rows.

   (a) Which focal length does `CameraLens::FromEntity` compute?

   (b) What is the circle of confusion, in pixels, of the sky, of a wall 8 m away and of a post 2 m away?

   (c) Between which distances is a point so sharp that the lens leaves it bit for bit as it was?

   (d) Does the blur show in the exported game with the player's `DepthOfField` row `Off`, in the same game with the row `Scene`, and in the editor's Scene view through the editor's own camera?

   :::answer[Worked solution]
   (a) Half the sensor over the tangent of half the field of view: 12 / tan 20° = 12 / 0.364 = 32.97 mm.

   (b) The first fraction is $f^2 / (N (z_f - f))$ = 1087 / (2.8 × 3967) = 0.0979 mm on the sensor, which is 0.0979 / 24 × 1,080 = 4.40 pixels. The sky takes this scale itself, 4.40. The wall has $(z - z_f)/z$ = 4 / 8 = 0.5, so 2.20 pixels. The post has (2 - 4) / 2 = -1, so -4.40 pixels, negative because it is nearer than the focus. All three lie under the limit of 2 % of the rows, 21.6 pixels.

   (c) The circle must be under one pixel across: $4.40 \cdot |1 - 4/z| < 1$, so $|1 - 4/z| < 0.227$. Then 4 / z lies between 0.773 and 1.227, and z lies between 3.26 m and 5.18 m.

   (d) With the row `Off`, no: the players' row always wins. With `Scene`, yes, because the game's renderer asks for a lens from the primary camera. In the editor's Scene view through its own camera, no, because that camera gives no lens, so `RenderFrame` runs no depth of field passes.
   :::

7. **Hard.** A project keeps the section's default preset, `High`. Its scene camera has motion blur on and anti-aliasing set to TAA. A player's script makes these calls in order, and the choices are saved.

   1. `Graphics::Set` of `MotionBlur` to `Off`.
   2. `Graphics::Set` of `AntiAliasing` to `FXAA`.
   3. `Graphics::Set` of `ShadowCascades` to 3.

   Then the designer changes the project's preset to `Ultra`, and the player starts the game again. The script then makes two more calls.

   <!-- markdownlint-disable MD029 -->
   4. `Graphics::SetPreset` with `QualityPreset::Low`.
   5. A reset of the option `Preset`.
   <!-- markdownlint-enable MD029 -->

   After each call, what is the preset in effect? Which method smooths the edges, which shader dithers and does the blur show, at the start and after calls 1 to 5? Does the restart change anything?

   :::answer[Worked solution]
   At the start the preset is `High` from the project. TAA resolves the frame, no spatial pass follows, so the tone mapping dithers, and the scene's blur shows.

   Call 1 changes a comfort row, which only disables: the preset stays `High` and the blur is off, although the scene asks for it. Call 2 sets the row `AntiAliasing`, a preference that may choose a method, so FXAA replaces TAA. The preset stays `High`, and now the tone mapping writes a bare image and FXAA adds the grain and the dither.

   Call 3 sets a cost row that follows the preset, so the service first switches the player to `Custom`, starting from the look in effect, and then sets 3 cascades. The preset in effect reads `Custom`.

   The player's choices lie over the project's value. After the project moves to `Ultra` and the game restarts from the saved file, the preset is still `Custom`, with the look of High and 3 cascades, and nothing of `Ultra` shows.

   Call 4 picks the preset `Low`. It drops the `Custom` values and keeps the comfort choices, so the blur stays off and FXAA stays. Call 5 removes the player's choice of the preset, together with the cost rows that follow it, so the project's `Ultra` applies again. The call names only the preset, so the blur stays off and FXAA stays as the method. FXAA dithers from call 2 to the end.
   :::

8. **Hard.** A colleague extends the letterbox of the tutorial with a bar color, a push constant of red, (1, 0, 0). The pass clamps the color to 0 to 1 and writes it into the bars as it is.

   His GPU test uses `ExactSpecification()`, a pre-exposure of 1 and an exposure factor of 1. The test reads a bar pixel, finds 255, 0, 0, 255 and passes. In a game the pre-exposure is $2^{-15}$ and the exposure factor is $2^{-13.47}$.

   (a) Why does the test pass and the game fail?

   (b) The tone mapping multiplies the stored value by the exposure factor over P. What red value does it compute for the bar in the game, and what should it compute? What is the ratio?

   (c) Name the fix, and say where the pass joins the chain.

   (d) Change the test so that it finds the fault.

   (e) In the game the pass cannot make its target once. What does the viewer see, and what does the renderer do?

   :::answer[Worked solution]
   (a) A writer of the HDR image must multiply by P. The pass does not, and the image is wrong only when P is not 1. The test draws with P equal to 1 and an exposure factor of 1, so the missing factor hides: the stored 1 gives exposed 1.

   (b) The tone mapping computes 1 × $2^{-13.47}$ / $2^{-15}$ = $2^{1.53}$ = 2.9 for the bar in the game. A bar that stores 1 × P = $2^{-15}$ gives $2^{-15}$ × $2^{-13.47}$ / $2^{-15}$ = $2^{-13.47}$, which is 0.000088. The ratio is $2^{15}$ = 32,768, which is 1 over P.

   (c) `RenderLetterbox` multiplies the clamped color by the pre-exposure before the color enters the push constants. The shader writes the bar through `SanitizeHDR`, as every writer does, because P can reach $2^{24}$ and the product could pass 65,000. It joins the chain after the motion blur and before the exposure, takes its parameters by push constants, reads the post source and becomes the next one. A new field of `FrameConstants` is not allowed.

   (d) Draw with a pre-exposure that is a power of two other than 1, say $2^{-3}$, with an exposure factor of 1, and give the bars the color 0.25. The right value is 0.25 after the exposure. Without the factor the value is 0.25 × 8 = 2, which differs. A test at P equal to 1, or with a bar color of 1 that the display clamps, cannot tell the two apart.

   (e) The target's creation reports the error and returns false, so `RenderLetterbox` returns false. `RenderFrame` keeps the old post source and marks the frame degraded. The viewer sees the frame without bars and otherwise complete. The log shows the error once, and the first frame without a failure clears it.
   :::
