---
id: indirect/review
title: "Review: indirect light"
description: "The questions of every page of the part on indirect light, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part, so try each one before you open its worked solution.

1. **Basic.** A closed room has walls of albedo 0.6 that are 30 cm thick. The sun shines in through a hole in the roof, and two torches burn inside.

   (a) What share of the room's total light do the direct light and two bounces carry?

   (b) Path tracing shows an error of 0.4 at 25 samples for each pixel. How many samples bring the error to 0.1?

   (c) Strata runs global illumination at High, and then at Low. Does each row keep the two sides of a wall apart?

   (d) Which of the room's lights feed the bounce light?

   :::answer[Worked solution]
   (a) The bounces form a series with the ratio 0.6. The total is 1 / (1 − 0.6) = 2.5 times the direct light. The direct light and two bounces give 1 + 0.6 + 0.36 = 1.96, and 1.96 / 2.5 = 78.4 % of the total.

   (b) The error falls like one over the square root of the samples. A fall to a quarter of the error, from 0.4 to 0.1, needs 16 times the samples: 16 × 25 = 400.

   (c) A wall must be thicker than two voxels to keep its sides apart. At High a voxel is 10 cm wide, so the limit is 20 cm, and the wall of 30 cm passes. At Low a voxel is 20 cm wide, so the limit is 40 cm. The wall is thinner than that, so one voxel holds both faces and the wall goes two-sided.

   (d) The sun feeds the voxels, and so do glowing surfaces. Point and spot lights add nothing, so the torches give no bounce light.
   :::

2. **Basic.** A pixel of a wall with a normal map lies outside every probe box. The scene has a sky map, and the pixel's reflection found nothing. The sky gives irradiance 0.6 and radiance 0.8, and the sky's intensity is 1.5.

   The wall has albedo 0.5, a reflectance of 0.04, a diffuse occlusion of 0.75 and a specular occlusion of 0.5. The normal map gives $R \cdot N_g = -0.1$.

   (a) Which form does the pixel take?

   (b) What share of the sky's specular light remains after the horizon fade?

   (c) What are the diffuse light, the specular light and the total?

   (d) The user then raises the sky's intensity from 1.5 to 3. What is the new total, and does the filter chain make a new cube?

   :::answer[Worked solution]
   (a) The probes' weight is 0 and no reflection was found, so the pixel takes the sky form, because the scene has an environment.

   (b) The ramp gives 1 + (−0.1 / 0.25) = 0.6, and the square is 0.36. The fade multiplies the specular occlusion, which becomes 0.5 × 0.36 = 0.18.

   (c) The diffuse light is the sky's irradiance times albedo × (1 − 0.04) = 0.48, times the diffuse occlusion: 0.6 × 0.48 × 0.75 = 0.216. The specular light is 0.8 × 0.04 × 0.18 = 0.00576. The sky form scales the composed sum by the intensity, so the total is (0.216 + 0.00576) × 1.5 = 0.333.

   (d) The total scales with the intensity, so it doubles to 0.665. The intensity works in the shader and is no parameter of the procedural sky, so the filter chain makes no new cube.
   :::

3. **Medium.** A view has 720 rows and a vertical field of view of 90 degrees. Ambient occlusion uses a radius of 1.5 m.

   (a) A surface is 3 m from the camera. What are the radius on screen and the world radius after the clamp?

   (b) Answer again for a surface 400 m away.

   (c) A pixel of the surface in (a) has no environment, a constant ambient of 0.2, albedo 0.5 and a diffuse occlusion of 0.6 from the multi-bounce fit. What light does it get?

   (d) A colleague wants to multiply the occlusion into the sun's light as well. What breaks?

   :::answer[Worked solution]
   (a) The projection scale is 1 / tan 45° = 1, so a metre at distance $d$ spans 0.5 × 720 / $d$ pixels. At 3 m that is 120 pixels, and the radius of 1.5 m spans 180 pixels. The limits are 0.003 × 720 = 2.16 pixels (above the least of 1.5) and 0.12 × 720 = 86.4 pixels. The radius is clamped to 86.4 pixels, and the world radius is 86.4 / 120 = 0.72 m.

   (b) At 400 m a metre spans 0.9 pixels, so the radius spans 1.35 pixels. That lies under 2.16, so it is raised to 2.16 pixels, and the world radius is 2.16 / 0.9 = 2.4 m.

   (c) With no environment the pixel takes the ambient form. Its diffuse light is the ambient times the albedo times the occlusion: 0.2 × 0.5 × 0.6 = 0.06. This form has no specular light, so the total is 0.06.

   (d) Occlusion darkens indirect light only, because direct light has its own visibility, the shadow. A crease that the sun lights would be darkened twice: once by the shadow map and once by the occlusion.
   :::

4. **Medium.** A reflection probe has half sizes 6, 2.5 and 3 m and a blend distance of 3 m. A surface lies at (−1, −1, 1) m from the probe's center, and its reflected ray points along (0, 0.6, 0.8). A second probe has weight 0.8 at the same place and a lower priority.

   The sky has intensity 2 and irradiance 0.4. The probes' light for the pixel is 0.6. The surface has albedo 0.5, a reflectance of 0.1 and a diffuse occlusion of 0.8.

   (a) Where does the box-projected lookup point, and how far does it rise compared with the plain lookup?

   (b) What are the probe's weight, the second probe's share and the share of the sky?

   (c) What is the pixel's diffuse light?

   :::answer[Worked solution]
   (a) The ray moves 0.6 m up for each metre and 0.8 m along z. The wall at z = 3 is (3 − 1) / 0.8 = 2.5 m away, and the ceiling at y = 2.5 is (2.5 + 1) / 0.6 = 5.83 m away. The wall is nearer, so the lookup points to (−1, −1 + 1.5, 3) = (−1, 0.5, 3). The plain lookup rises $\arcsin 0.6$ = 36.9 degrees. The projected one rises $\arcsin(0.5 / 3.20)$ = 9.0 degrees.

   (b) The depths to the faces are 5 and 7 on x, 3.5 and 1.5 on y, and 2 and 4 on z. The least is 1.5 m, so the weight is 1.5 / 3 = 0.5. The weaker probe takes its weight of what is left: 0.8 × (1 − 0.5) = 0.4. The sky fills 1 − 0.5 − 0.4 = 0.1.

   (c) The probes' form is chosen, because the weight is above 0, and the sky's share is 0.1. The pixel scatters albedo × (1 − 0.1) = 0.45 of the light. The diffuse light is (0.6 + 0.4 × 2 × 0.1) × 0.45 × 0.8 = 0.68 × 0.36 = 0.245.
   :::

5. **Medium.** A pixel lies inside a probe box with weight 0.5. The probes' radiance is 0.8, the sky's radiance 0.5 and the sky's intensity 2. The pixel's specular occlusion is 0.6, its screen occlusion 0.9 and its reflectance 0.1. Its diffuse light is 0.36.

   (a) The reflections use the Checkerboard rule. A reflected ray passes 12.0 m from the camera. The previous point lay at 11.2 m, and the surface at the new point is at 11.7 m. Does the ray hit? Answer again for a surface at 10.6 m.

   (b) Four of five neighbours of equal weight found the color 1.5 with confidence 1. What does the resolve give?

   (c) What are the pixel's specular light and its total?

   :::answer[Worked solution]
   (a) The tolerance is the ray's change in distance, 12.0 − 11.2 = 0.8, plus the larger of 0.05 m and 2 % of 12.0 m (0.24 m). That is 0.8 + 0.24 = 1.04 m. At 11.7 m the ray is 0.3 m behind the surface, which is within 1.04 m, so it hits. At 10.6 m the ray is 1.4 m behind, which is beyond the tolerance, so it passes behind the surface.

   (b) The ratio estimator adds the premultiplied light of the five and divides by their number: 4 × 1.5 / 5 = 1.2. The confidence is 4 / 5 = 0.8.

   (c) The form is probes, because the probes' weight is above 0, and the found reflection replaces only the fallback. The fallback is 0.8 + 0.5 × 2 × (1 − 0.5) = 1.3. It is darkened by the specular occlusion and kept by the share 1 − 0.8 = 0.2: 1.3 × 0.6 × 0.2 = 0.156. The found light has the screen occlusion: 1.2 × 0.9 = 1.08. The specular light is (0.156 + 1.08) × 0.1 = 0.124, and the total is 0.36 + 0.124 = 0.484.
   :::

6. **Hard.** At High, the camera stands at (5.07, 2.05, 1.05) m. The finest level has 0.1 m voxels, and its window follows the camera in steps of four voxels.

   (a) Which voxels does the window of level 0 cover on each axis?

   (b) The camera moves to x = 6.57 m. Which voxels enter, how many are they and at which texels on x do they live? Into how many regions is the slab cut?

   (c) At which texel on x does voxel −16 live at High, and at which at Low?

   (d) One view runs at High and another at Low. How much memory does global illumination take?

   (e) A wall 25 cm thick stands in the slab of (b). Do level 0's voxels keep its two sides apart? Answer again for the finest voxels of Low.

   :::answer[Worked solution]
   (a) The finest level centers 0.8 m below the camera, at y = 1.25 m. The center voxel is (50, 12, 10). Half the dimensions at High are (64, 32, 64), so the window starts at (−14, −20, −54), rounded down to a multiple of 4: (−16, −20, −56). It covers x from −16 to 111, y from −20 to 43 and z from −56 to 71.

   (b) The center voxel on x becomes 65, so the start is floor((65 − 64) / 4) × 4 = 0. The window now covers x from 0 to 127. The slab covers x from 112 to 127, with the old y and z. That is 16 × 64 × 128 = 131,072 voxels, 12.5 % of the window. Their texels are 112 to 127, the texels of the voxels at x = −16 to −1 that left.

   The slab is one piece along x. Along y it wraps at 0, so it splits into −20 to −1 and 0 to 43. Along z it wraps at 0 as well: −56 to −1 is one piece, and 0 to 71 is longer than 64, so it splits into 0 to 63 and 64 to 71. That makes 1 × 2 × 3 = 6 regions.

   (c) The remainder is never negative. At High the axis has 128 voxels, so voxel −16 lives at texel −16 + 128 = 112. At Low the axis has 64 voxels, so it lives at −16 + 64 = 48.

   (d) The views hold their layouts apart: 155.7 MiB for High and 24.9 MiB for Low, which is 180.6 MiB.

   (e) A wall keeps its sides apart only when it is thicker than two voxels. Level 0 at High has 10 cm voxels, so the limit is 20 cm, and the wall of 25 cm passes. The finest voxels of Low are 20 cm wide, so the limit is 40 cm. There the wall goes two-sided and is dark on both sides.
   :::

7. **Hard.** A wall point sees only two of its eight probes. Before the guard the eight would weigh 0.5 in all. The two weigh 0.03 and 0.02 and carry the light 10 and 6.

   A child ray of cascade 0 has $L$ = 1.5 nits and $T$ = 0.4. Its two parents have weights 0.5 and 0.25 and mean radiances of 8 and 20 nits.

   (a) What is the child ray's merged radiance?

   (b) What does the gather divide the sum by, and what light does it give? What would dividing by the visible weight give?

   (c) The point lies 7.2 m sideways from the camera. Is it inside the field's full reach at High? Answer again for Low, and for 10 m at both rows.

   (d) The field's weight is 0.6 where the point lies. Today's diffuse light is 2.0, and the field's diffuse light is the value of (b). The intensity is 1.5. What does a settled frame show, and what does a pending frame show?

   :::answer[Worked solution]
   (a) The parents' merged value is (0.5 × 8 + 0.25 × 20) / (0.5 + 0.25) = 9 / 0.75 = 12 nits. The child adds its own light and its transmittance times that value: 1.5 + 0.4 × 12 = 6.3 nits.

   (b) The sum is 0.03 × 10 + 0.02 × 6 = 0.42, and the visible weight is 0.05. The gather never divides by less than a quarter of what the probes would weigh without the guard, 0.25 × 0.5 = 0.125. It divides by max(0.05, 0.125) = 0.125 and gives 0.42 / 0.125 = 3.36. Dividing by 0.05 would give 8.4, all of the two probes' light. A step later their weights reach 0, and that light would fall to black at once: a step at the cell border.

   (c) At High the field is full to 7.5 m sideways and gone at 9.5 m, so 7.2 m lies inside the full reach. At Low the full reach is 7 m and the fade ends at 9 m, so 7.2 m lies in the fade. At 10 m the field is gone at both rows, and the point keeps today's light.

   (d) The intensity scales the field's light: 3.36 × 1.5 = 5.04. The join gives today's light times 1 − 0.6 plus the field's times 0.6: 2.0 × 0.4 + 5.04 × 0.6 = 0.8 + 3.024 = 3.82. A pending frame leaves the weight at 0 and the old expression runs, so it shows 2.0.
   :::

8. **Hard.** A closed room has a brightest albedo of 0.8, and the gain of the bounces is 1. A crate in the room stops moving. The game runs at 50 frames a second.

   (a) What share of the final light does the field hold after frame 1 and after frame 4? How many frames does the series take to settle?

   (b) The room's brightest albedo changes to 0.95. How many frames does it take now?

   (c) In which frame after the crate stops do its triangles return to the voxels, and what is the crate until then?

   :::answer[Worked solution]
   (a) After frame $k$ the light holds the first $k$ terms of the series, which is the share 1 − $r^k$ of the limit. With $r$ = 0.8, frame 1 holds 1 − 0.8 = 0.2, and frame 4 holds 1 − 0.8⁴ = 0.59. The room settles at the first $k$ where $r^k (1 − r)$ is below 0.0025. At $k$ = 19 the share is 0.0029, too much, and at $k$ = 20 it is 0.0023. So $k$ = 20, and with the margin of two frames the room settles after 22 frames.

   (b) The albedo is clamped to 0.9, so $r$ = 0.9. The share is 0.0025 at $k$ = 35, which is not below 0.0025, and 0.0022 at $k$ = 36. So $k$ = 36, and the room settles after 38 frames.

   (c) The wait is 0.25 s of the renderer's clock. A frame lasts 0.02 s, so 12 frames make 0.24 s, which is too short, and 13 frames make 0.26 s. The triangles return in frame 13. Until then the crate is an oriented box in the dynamic layer, and its voxels fade in over a further 0.25 s.
   :::

9. **Hard.** A game maker works at the highest quality and reports four faults. For each, name the cause and the page that explains it.

   (a) A probe baked in a room shows its polished floor without the crates reflected in it, although the game's own view shows those reflections.

   (b) A clear-coated car shows the street in its paint but not in its coat.

   (c) Seven new probes come into view in one frame. The sixteen slots are free, and conversions are spread. How many frames pass until all seven are converted, and what lights their boxes until then?

   (d) A scene lit by torches gets no bounce light from them, and a 10 cm rail looks like a lump.

   :::answer[Worked solution]
   (a) The bake copies the Medium row's values, so the project's quality never enters. Medium's reflections are Checkerboard, which needs temporal anti-aliasing, and a bake has none. Its global illumination is Off too. The probe page explains it.

   (b) The coat reads no screen-space light. The seam's `SampleSpecularLight` takes only the probes, the sky or the ambient light, so the coat shows the probes' room, not the street. The seam and the reflections pages explain it.

   (c) At most two conversions run in one frame, so seven captures need 2 + 2 + 2 + 1 = 4 frames. A capture that is not converted lights nothing, so the sky's light, or the ambient light, fills the box meanwhile. The probe page explains it.

   (d) Point and spot lights never enter the voxels, so torches give no bounce. A rail of 10 cm is thinner than two voxels at High (20 cm), so it blurs into whole voxels. The page on the limits of global illumination explains both.
   :::
