---
id: light/review
title: "Review: light and materials"
description: "The questions of every page of the part on light and materials, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part, so try each one before you open its worked solution.

1. **Basic.** A big lamp of 30,000 lumens is a point light with a range of 20 m. A wall of base color 0.8, with no metal, faces it 5 m away. You look at the wall in the Luminance view.

   (a) How many candela does the light have?

   (b) Which factor $A$ does the wall get, and how many lux?

   (c) How many nits does the wall show?

   (d) Which exposure value (EV100), which bin and which color band does a pixel of the wall get?

   (e) Which manual exposure shows a mid-gray surface under the same light as middle gray?

   :::answer[Worked solution]
   (a) A point light spreads its power over the whole sphere, so $I = 30{,}000 / 4\pi = 2{,}387$ cd.

   (b) The window is $w = 1 - (5/20)^4 = 0.9961$. The factor is $A = w^2 / d^2 = 0.9922 / 25 = 0.03969$, and the wall gets $2{,}387 \times 0.03969 = 94.7$ lux.

   (c) A diffuse surface under $E$ lux shows $\rho E / \pi$ nits, so the wall shows $0.8 \times 94.7 / \pi = 24.1$ nits.

   (d) The EV100 is $\log_2(24.1) + 3 = 4.59 + 3 = 7.59$. The bin position is $(7.59 + 8) \times 4 = 62.4$, so the pixel counts in bin 62. The band is the whole part of $7.59 - 5$, which is 2.

   (e) The exposure is $\log_2(\pi / E) = \log_2(3.1416 / 94.7) = \log_2(0.0332) = -4.91$.
   :::

2. **Basic.** A surface has base color 0.6 in one channel, `Metallic` 0.25 and perceptual roughness 0.5. A light of radiance 1 stands straight above it, and the eye looks straight down. Ignore the energy compensation: treat `SpecularEnergy` as 1.

   (a) What is $F_0$ of the channel?

   (b) What does `EvaluateLightWeighted` return for the channel?

   (c) The eye moves until $\cos\theta$ between the view and the half vector is 0.5. What is $F$ then?

   (d) You set `Metallic` to 1. What does the function return now?

   :::answer[Worked solution]
   (a) $F_0 = (1 - m) \times 0.04 + m\,c = 0.75 \times 0.04 + 0.25 \times 0.6 = 0.03 + 0.15 = 0.18$.

   (b) The roughness is above the floor, so the alpha is $0.5^2 = 0.25$. With every cosine at 1, D is $1 / (\pi \alpha^2) = 1 / (\pi \times 0.0625) = 5.093$ and V is 0.25. F is $F_0 = 0.18$, so the specular lobe is $5.093 \times 0.25 \times 0.18 = 0.2292$.

   The diffuse lobe keeps $1 - F$ and $1 - m$: $0.82 \times 0.75 \times 0.6 / \pi = 0.1175$. The sum, times radiance 1 and a cosine of 1, is 0.3466.

   (c) Schlick gives $F = 0.18 + 0.82 \times (1 - 0.5)^5 = 0.18 + 0.82 \times 0.03125 = 0.2056$.

   (d) A metal has no diffuse lobe, and its $F_0$ is the base color, 0.6. The specular lobe is $5.093 \times 0.25 \times 0.6 = 0.764$, so the function returns 0.764. The same light gives more than twice as much, because the metal keeps all its light in the highlight.
   :::

3. **Basic.** A normal map has a texel of bytes (191, 128, 255). The surface has $T = (1, 0, 0)$, $B = (0, 1, 0)$ and $N = (0, 0, 1)$, and `NormalScale` is 1.

   (a) Which world normal does the texel give?

   (b) A second material has no normal map, and its glow map is still loading. Which table index does `Build` write for each?

   (c) Suppose the engine stored the flat normal as an 8-bit texel of (128, 128, 255). By how many degrees would every such surface tilt, and what does Strata store instead?

   (d) You add one field of four floats to the material record. How many bytes does it have, and what must change with it?

   :::answer[Worked solution]
   (a) The decode gives $n_x = 2 \times 191/255 - 1 = 0.498$ and $n_y = 2 \times 128/255 - 1 = 0.0039$. Then $n_z = \sqrt{1 - 0.248 - 0.00002} = 0.867$. The world normal is $n_x T + n_y B + n_z N = (0.498, 0.004, 0.867)$, which has length 1.

   (b) A missing normal map reads the flat normal, index 2. A glow map that is still loading reads black, index 1. Only the glow map separates "absent" from "loading": absent it would read white.

   (c) The byte 128 decodes to 0.00392, not 0. Both X and Y lean, so the tangent of the tilt is $\sqrt{2} \times 0.00392 = 0.00554$, and the tilt is 0.32 degrees. Strata stores the texel as the half floats (0.5, 0.5, 1), where 0.5 is exact, so the decode gives 0 and the normal stays the vertex normal.

   (d) Four floats are 16 bytes, one more row, so the record has 160 bytes in ten rows. The field goes into `MaterialProperties`, the C++ struct, the Slang struct in the same place and order, and `Build`. The number in the `static_assert` and the tests that check the size change with them. A field added on one side only makes the shader read every later field in the wrong place.
   :::

4. **Medium.** A copper channel has $F_0 = 0.64$, and the surface has roughness 1. A light of radiance 2 stands straight above it and the eye looks straight down. At roughness 1 and `NoV` 1, the directional albedo is $E = 0.3078$.

   (a) What does the specular lobe return without any compensation?

   (b) Which factor restores the lost light, and what does the lobe return with it?

   (c) A white metal ($F_0 = 1$) of roughness 1 sits in a white furnace. What does its center show with and without the factor?

   (d) What does the copper channel show in the furnace with the factor?

   :::answer[Worked solution]
   (a) At roughness 1 the alpha is 1, so D is $1/\pi$ at every angle, and with every cosine at 1 the visibility V is 0.25. The lobe is $(1/\pi) \times 0.25 \times 0.64 = 0.0509$ per unit of radiance, and with radiance 2 it returns 0.1019.

   (b) The factor is $1 + F_0 (1/E - 1) = 1 + 0.64 \times (3.249 - 1) = 2.439$. The lobe returns $0.1019 \times 2.439 = 0.2485$.

   (c) Without the factor the center shows $E = 0.3078$: single scattering loses 69 % of the light. For $F_0 = 1$ the factor is $1/E = 3.249$, and it is exact, so the center shows 1.

   (d) The copper channel shows $F_0 E + F_0^2 (1 - E) = 0.197 + 0.284 = 0.481$. Each bounce inside the surface absorbs 36 % of the light it reaches, so copper keeps less than 1 where the white metal keeps 1.
   :::

5. **Medium.** A shop has a one-sided rect light of 1.5 by 0.8 m with Intensity 900 and Units Lumens. A lantern hangs 3 m from a polished mirror. Its bulb has a `SourceRadius` of 0.2 m.

   (a) What luminance does the panel's face have, and what if the panel were two-sided?

   (b) How many candela does the panel give along its axis, compared with a point light of 900 lumens?

   (c) What alpha squared does the bulb add to the mirror's highlight? Take the smallest roughness spread, $0.045^4 = 4.1 \times 10^{-6}$, from the added value. What is the lobe's alpha, and how far does the peak of D fall against a point light of no size?

   (d) Which light type do you choose for the lantern's flame, and which for a ceiling panel above a desk?

   :::answer[Worked solution]
   (a) The area is $1.5 \times 0.8 = 1.2$ m$^2$, so $L = P / (\pi A) = 900 / (\pi \times 1.2) = 238.7$ nits. A two-sided light shares its power between two faces, so each face shows 119.4 nits.

   (b) The candela along the axis is $L \times A = 238.7 \times 1.2 = 286.5$. A point light of 900 lumens has $900 / 4\pi = 71.6$ cd. The panel is four times as strong on its axis, because it sends all its light into one half space and not evenly into the sphere.

   (c) The bulb spans an angle with $\sin\theta = 0.2 / 3 = 0.0667$, so $\sin^2\theta = 0.004444$ and $\tan^2\theta = 0.004444 / 0.995556 = 0.004464$. Divide by $1.287^2 = 1.657$ to get 0.002694, and take away $4.1 \times 10^{-6}$: the bulb adds 0.00269.

   The mirror's lobe has the alpha squared $4.1 \times 10^{-6} + 0.00269 = 0.002694$, so the alpha is 0.0519. The peak of D is $1 / (\pi \times 0.002694) = 118$, against $1 / (\pi \times 4.1 \times 10^{-6}) = 77{,}600$ for a point light. The peak falls about 660 times, and the lobe keeps its energy.

   (d) A flame is small and its highlight matters, so a point light with a source radius fits. A ceiling panel has a shape, and the diffuse light near it matters, so a rect light fits.
   :::

6. **Medium.** A view of 1,920 by 1,080 pixels uses the default grid of 16 by 9 by 24 clusters, a near of 0.1, a far of 1,000 and 256 lights per cluster.

   (a) Which cluster does the pixel (1000, 270) read at a view depth of 20 m, and where does its entry start?

   (b) How many numbers and bytes does the cluster buffer hold?

   (c) Three lights reach that cluster, in record order B, A, C. A light has the relevance $r / (d - r)$ for its range $r$ and distance $d$. B has $r$ = 5 m at 30 m, A has 2 m at 10 m and C has 1 m at 3 m. The cluster holds two lights. Which stay on the central processing unit (CPU) path and on the graphics processing unit (GPU) path, and in which order are they listed?

   (d) Light A has 100 candela. How many lux does it give a surface 1.5 m away?

   :::answer[Worked solution]
   (a) The tile along the row is $\lfloor 1000/1920 \times 16 \rfloor = \lfloor 8.33 \rfloor = 8$, and down it is $\lfloor 270/1080 \times 9 \rfloor = \lfloor 2.25 \rfloor = 2$. The scale is $24 / \ln(10{,}000) = 2.606$, and the offset is $-2.606 \times \ln(0.1) = 6.0$. The slice is $\lfloor \ln(20) \times 2.606 + 6.0 \rfloor = \lfloor 13.8 \rfloor = 13$. The index is $(13 \times 9 + 2) \times 16 + 8 = 1{,}912$, and its entry starts at $1{,}912 \times 257 = 491{,}384$.

   (b) There are $16 \times 9 \times 24 = 3{,}456$ clusters, each with a stride of 257 numbers. That makes 888,192 numbers, and at 4 bytes each, 3,552,768 bytes, about 3.4 MiB.

   (c) The relevances are B: $5/25 = 0.2$, A: $2/8 = 0.25$ and C: $1/2 = 0.5$. The CPU path sorts by relevance, C then A then B, and lists the first two in buffer order: C, A. The GPU path packs in record order, and a full cluster keeps the two most relevant by its search: A and C. It lists them in record order, A, C. Both paths keep the same two lights.

   (d) The window is $1 - (1.5/2)^4 = 1 - 0.3164 = 0.6836$. The factor is $A = 0.6836^2 / 1.5^2 = 0.4673 / 2.25 = 0.2077$, so the surface gets $100 \times 0.2077 = 20.8$ lux.
   :::

7. **Medium.** A bottle stands on a table whose top has a clear coat of strength 0.8. The bottle is glass with the attenuation color (0.2, 0.6, 0.3) at the distance 0.5 and a `Thickness` of 0.3.

   (a) The eye sees the coat at $\cos\theta = 0.3$. What share does the coat reflect, and what share reaches the wood?

   (b) A plain sheet of glass with an index of refraction (IOR) of 1.5 reflects what share head-on? Compare it with the coat.

   (c) What share of each channel does the bottle's glass keep?

   (d) The maker doubles the `Thickness` to 0.6. What does the red channel keep, and how does it relate to part (c)?

   :::answer[Worked solution]
   (a) The coat reflects $F = s\,(0.04 + 0.96\,(1 - \cos\theta)^5) = 0.8 \times (0.04 + 0.96 \times 0.7^5)$. The fifth power is 0.168, so the bracket is $0.04 + 0.161 = 0.201$ and $F = 0.161$. The wood keeps $1 - F = 0.839$.

   (b) The reflectance of a non-metal head-on is $((n - 1)/(n + 1))^2 = (0.5 / 2.5)^2 = 0.04$. The coat's own value is the same 0.04, which is the IOR 1.5, scaled by the strength: 0.032 head-on for a strength of 0.8.

   (c) The rate of a channel is minus the natural logarithm of its color, divided by the distance. For red it is $-\ln(0.2) / 0.5 = 3.219$. After a thickness of 0.3 the red channel keeps $e^{-3.219 \times 0.3} = e^{-0.966} = 0.381$. This equals $0.2^{0.3/0.5} = 0.2^{0.6}$, so green keeps $0.6^{0.6} = 0.736$ and blue keeps $0.3^{0.6} = 0.486$.

   (d) The doubled thickness doubles the optical depth, so red keeps $e^{-1.932} = 0.145$. That is the square of 0.381. As on a path through air, twice the path squares the transmittance.
   :::

8. **Medium.** A scene uses the Atmosphere source. The sun's Intensity is 120,000 lux, and it stands 20 degrees above the horizon. At that elevation red keeps 0.863 of the sun's light, green 0.722 and blue 0.460.

   (a) How many lux does the sun give a level floor in red and in blue?

   (b) A friend lowers the Intensity to 40,000 lux to make the sunset warmer. What changes, and what does the ratio of red to blue become?

   (c) At 1 degree red keeps 0.253 and blue 0.0011. What is the ratio of red to blue now?

   (d) The same scene has a valley fog with the base at the floor, a layer about 20 m thick, and a camera 3 m above the base. A level view must hide half of a wall 60 m away. Which `HeightFalloff` and `Density` do you set?

   (e) With `MaxOpacity` 0.8, which opacity do walls at 120 m and 200 m get, and the sky below the horizon?

   :::answer[Worked solution]
   (a) The intensity is the illuminance above the air, so a level floor gets $120{,}000 \times \sin 20° = 41{,}042$ lux before the air. Red keeps 0.863: 35,400 lux. Blue keeps 0.460: 18,900 lux.

   (b) The air dims every channel by its own transmittance, and the intensity multiplies all of them. A third of the intensity gives a third of every channel: 11,800 lux red and 6,290 lux blue. The ratio stays $0.863 / 0.460 = 1.88$, so the sun is darker and not warmer. The color comes from the path through the air.

   (c) At 1 degree the sun's direct light is $120{,}000 \times 0.01745 = 2{,}094$ lux, with 530 lux in red and 2.3 lux in blue. The ratio is $0.253 / 0.0011 = 230$, so the light is deep red.

   (d) A layer 20 m thick means that the density falls by the factor $e$ over 20 m, so `HeightFalloff` is $1/20 = 0.05$. Half hidden means $e^{-\tau} = 0.5$, so $\tau = \ln 2 = 0.693$. A level ray has $\tau = \rho D e^{-kh}$, with $h = 3$, so $0.693 = \rho \times 60 \times e^{-0.15}$. That gives $\rho = 0.693 / (60 \times 0.861) = 0.0134$.

   (e) At 120 m the depth doubles to 1.386, which leaves 0.25 of the wall's color, an opacity of 0.75. That is below the cap, so the wall gets 0.75. At 200 m the depth is 2.31 and the opacity 0.90, so the cap gives 0.8. The sky below the horizon never leaves the fog, its opacity is 1 and the cap gives 0.8.
   :::

9. **Hard.** A sun shines on a scene seen through a 60 degree lens of aspect 16:9, with maps of 2,048 texels and the default biases. A cascade covers the slice that ends at 12 m, and its sphere lies at the far end of the slice. The sun stands 10 degrees above the horizon, and its disk is 0.53 degrees across ($\tan 0.265° = 0.004625$).

   (a) What are the cascade's radius and texel size? Round the radius up to 1/16 m, and use 1,980 usable texels.

   (b) How many metres do the default depth bias and the normal offset move the comparison?

   (c) What is the largest error of the center sample on flat ground, in texels and metres? Does the depth bias alone cover it, and which fix do you try first for stripes?

   (d) Two edges cast shadows on flat ground: the top of a pole lies 1.5 m from the ground along the sun's rays, and a roof edge 6 m along them. How wide is each penumbra across the rays, and which filter does each get?

   (e) The camera turns by 90 degrees. What changes in this cascade?

   :::answer[Worked solution]
   (a) The sphere sits at the far end, so its radius is the distance from the axis to a corner of the far plane. The half height is $\tan 30° = 0.5774$ times the distance, and the half width is $0.5774 \times 16/9 = 1.0264$ times it. The corner lies $\sqrt{1.0264^2 + 0.5774^2} = 1.1776$ times 12 m away, which is 14.13 m, and rounding up to 1/16 m gives 14.1875 m. The texel is $2 \times 14.1875 / 1{,}980 = 0.01433$ m, which is 14.3 mm.

   (b) The depth bias is 1.0 texel: 14.3 mm. The normal offset is 1.5 texels: 21.5 mm.

   (c) The depth of the ground changes by $\cot 10° = 5.67$ texels over one texel of the map. The center sample is half a texel from the edge, so its largest error is 2.84 texels, or 40.7 mm. The depth bias of 1 texel does not cover it. The rasterizer's slope bias and the receiver plane carry the rest, so you do not raise the depth bias: it would detach shadows from their casters. For stripes you raise the normal offset first.

   (d) The filter reads the separation $s$ from the depths of the map, which run along the sun's rays. The disk's radius for a blocker at the separation $s$ is $s \tan a$, and the penumbra across the rays is twice that. For the pole it is $1.5 \times 0.004625 = 6.9$ mm, so the penumbra is 13.9 mm wide, and the radius in texels is $6.9 / 14.33 = 0.48$. The weight of the disk is the radius less 1, limited to 0 to 1, so it is 0 and the pole gets the tent filter alone.

   For the roof edge the radius is $6 \times 0.004625 = 27.8$ mm, the penumbra is 55.5 mm wide and the radius is 1.94 texels. The disk weight is 0.94, so the roof edge gets the tent and nearly the whole disk.

   (e) Nothing changes in the radius and the texel size. They depend on the lens alone, and the turn moves only the places of the spheres.
   :::

10. **Hard.** A street has point lamps of 400 candela with a range of 15 m. The view is 1,080 pixels high with a field of view of 60 degrees. All lamps cast shadows through one atlas of 2,048 texels each way, with a smallest tile of 128 texels, and each point light takes six tiles.

    (a) Which tile size does a lamp 40 m away ask for, and which one a lamp 80 m away?

    (b) A lamp at 80 m holds a tile of 512. A lamp at 40 m holds a tile of 256. Which sizes do they have after the frame?

    (c) Three lamps at 40 m all ask for 512. Do their tiles fit? What does the fitter do, and how much memory do the atlas and three cube maps of 1,024 texels take?

    (d) A lamp's shadow fades in on a machine at 30 frames a second. How many frames and seconds does the fade take, and how many at 60 frames a second?

    (e) How many lux does a lamp give the street 6 m below it, and how many 15 m away?

    :::answer[Worked solution]
    (a) The range spans $15 / (40 \times \tan 30°) = 0.650$ of the half height, which is 540 pixels, so the radius is 351 pixels. The next power of two is 512. At 80 m the radius is 175 pixels, and the next power of two is 256.

    (b) A lamp that holds a size keeps it while the pixels stay between 0.4 and 1.25 times that size. For the lamp at 80 m with a tile of 512 the band is 205 to 640 pixels, and 175 lies below it, so the tile shrinks to 256. For the lamp at 40 m with a tile of 256 the band is 102 to 320 pixels, and 351 lies above it, so the tile grows to 512.

    (c) The budget is seven eighths of the atlas: $2048^2 / 8 \times 7 = 3{,}670{,}016$ texels. Three lamps of 512 with six tiles each need $3 \times 6 \times 512^2 = 4{,}718{,}592$ texels, which is too much. The fitter halves sizes from the least relevant light: one lamp goes to 256, and the three need $2 \times 1{,}572{,}864 + 393{,}216 = 3{,}538{,}944$ texels, which fits.

    The atlas holds $2048^2 \times 4 = 16$ MiB of depth. Three cube maps of 1,024 texels take $3 \times 24 = 72$ MiB.

    (d) The fade steps by the frame time over 0.2 s, but at most one eighth. At 30 frames a second the step is $(1/30) / 0.2 = 0.167$, so the cap of 0.125 applies: 8 frames, which take $8/30 = 0.27$ s. At 60 frames a second the step is 0.083, so the fade takes 12 frames and 0.2 s.

    (e) The window at 6 m is $1 - (6/15)^4 = 1 - 0.0256 = 0.9744$. The factor is $A = 0.9744^2 / 6^2 = 0.9495 / 36 = 0.02637$, so the street gets $400 \times 0.02637 = 10.5$ lux. At 15 m the window is 0, so the lamp gives no light there, and its shadow has nothing to darken beyond its range.
    :::
