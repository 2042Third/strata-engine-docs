---
id: image/motion-blur
title: "Motion blur"
description: "How Strata blurs what moves while a camera's shutter is open: tile maxima, a depth-aware gather, and the frames and views that never blur."
kind: internals
size: M
tracks: [E]
needs: [image/taa]
time: 55
learn:
  - id: predict-length
    text: predict the length of a blur in pixels from the shutter angle, the motion and the clamp
  - id: reconstruction
    text: explain how the tile max and the neighbor max let a gather of few samples reach far enough
  - id: depth-weights
    text: explain how depth weights keep a moving foreground over a background, and a still one sharp
  - id: never-blurred
    text: name the frames, views and pixels that never blur and find the line that decides each
since: 0.7.0
status: final
---

A film camera does not take snapshots. Its shutter stays open for part of each frame, and whatever moves in that time leaves a streak. Motion blur is the :term[post pass]{id=post-pass} that puts the streaks back into a rendered frame. It reads each pixel's motion since the last frame, averages the colors along that motion, and stops there. It never blurs the user interface, the first frame, a :term[camera cut]{id=camera-cut}, or the view of the editor's own camera, and it does not make the :term[motion vectors]{id=motion-vector} it reads.

## The problem and how engines solve it

A :term[renderer]{id=renderer} draws one instant per frame, with a shutter that opens and closes in no time. A moving object is then drawn sharp at one spot, and at 60 :term[frames per second]{id=frame-rate} it jumps from spot to spot. The eye reads the jumps as :term[judder]{id=judder}. A camera film instead keeps the shutter open for a part of the :term[frame time]{id=frame-time}. The **shutter angle** is that part, written in degrees of a full turn of 360: 180 degrees means half of the frame time, 90 degrees a quarter.

:::question
Our eyes already blur things, so why add more?
:::

The screen does part of the work. A **sample-and-hold blur** is the smear that a display adds when your eye follows a moving object. The picture stays still for the whole frame while the eye moves, so the image slides over the back of your eye.

A renderer cannot remove that blur. It can add its own where the eye does not follow, for example in the background behind a character you track. It must not add so much that a slow pan turns soft.

To blur by the shutter's share of the motion, a renderer needs to know how each pixel moved. The motion vectors give that (see [Motion vectors](../draw/motion-vectors.md)). Three families of method then turn the vectors into a blur.

- **Accumulate sub-frames.** Draw the frame several times at times inside the shutter and average them. The result is exact, and it costs several frames of work.
- **Scatter.** Each pixel spreads its color along its own motion. Pixels that overlap must be sorted by depth, and the sort is the hard part on a :term[graphics processing unit]{id=gpu} (GPU).
- **Gather.** Each pixel looks along the motion near it and collects colors. Gathering suits a GPU, but a pixel needs the motion of its neighbors, not only its own, because a fast neighbor can smear over a still pixel.

A published gather filter (cited at the end of the page) solves this in two steps. First it cuts the image into tiles and keeps, per tile, the longest blur. A **tile max** is that longest blur of one tile; the **neighbor max** of a tile is the longest blur among the tile and the eight tiles around it. A pixel gathers along its neighborhood's longest blur, so the gather reaches as far as anything that can blur over it. Second, each sample gets a weight from its depth: a nearer sample that blurs over the pixel counts, a farther one counts only when the pixel's own blur reaches it.

The last choice is how to place the samples. Random positions that change each frame look like noise that crawls. Strata uses one fixed offset per pixel and spreads the samples evenly over the blur, a :term[stratified]{id=stratified-sampling} pattern. The noise stays, but it holds still and does not shimmer. Strata's variant of the filter, designed here, adds a rule for diagonal tiles, a second gather direction, and a floor that drops blurs under one pixel at 1080 rows.

## The map

The pass runs between the anti-aliasing and depth of field passes before it and the bloom and :term[tone mapping]{id=tone-mapping-image} after it. Three compute :term[shaders]{id=shader} do the work, and the :term[central processing unit]{id=processor} (CPU) only decides whether to run them and sets their constants.

```mermaid caption="The motion blur reads velocity, depth and the previous pass's color, finds each tile's longest blur, then each neighborhood's, gathers, and hands its color and the blur mask to the next passes." alt="A flow from velocity, depth and color into the tile pass, which writes tile maxima and a pixel target. The neighbor pass reads the tile maxima. The gather reads the neighbor maxima, the pixel target and the color, and writes the blurred color with a mask in alpha for bloom and tone mapping."
flowchart LR
	V[velocity + depth] --> T[MotionBlurTiles: tile max, pixel target]
	T --> N[MotionBlurNeighbors: neighbor max]
	N --> G[MotionBlur: gather]
	T --> G
	C[color from TAA or depth of field] --> G
	G --> B[blurred color, mask in alpha]
	B --> P[exposure, bloom, tone mapping]
```

The :term[main thread]{id=main-thread} runs `RenderMotionBlur` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp` and records the three dispatches. The files `MotionBlurTiles.comp.slang`, `MotionBlurNeighbors.comp.slang` and `MotionBlur.comp.slang` in `Strata/shaders/PostProcess/` hold the passes, and `Strata/shaders/Include/MotionBlur.slang` holds what they share. The renderer owns four targets: the blurred image, the tile maxima, the neighbor maxima and a per-pixel target that stores each pixel's blur radius and distance from the camera.

## The contract

The Post Process component has three fields: `MotionBlur` (off by default), `MotionBlurShutterAngle` (180 degrees) and `MotionBlurMaxLength` (0.02, a share of the image's height). The renderer clamps the angle to 0 to 360 and the length to 0.005 to 0.05.

- **Only the game's camera blurs, and only while the game plays.** The editor camera never blurs, because moves made by editing are not the game's. Captures and thumbnails never blur either, because a capture renders a view again while a running game moves. The line is in `StrataEditor/src/Editor/ViewportRenderer.cpp`.
- **Depth of field is different.** It is a property of a lens, not of a moment, so every view and capture through a scene camera with depth of field shows it, playing or not.
- **The first frame, a resize and a camera cut never blur.** On each of them the :term[motion history]{id=motion-history} is missing or its motion spans the jump, so a blur would smear the whole image along a false line.
- **The interface never blurs.** The pass works on the scene's color, and the interface and the :term[overlays]{id=overlay-gpu} are not part of it. A blurred health bar would only look broken.
- **Blurred pixels are not sharpened.** The pass writes 1 into the alpha of each pixel it blurred, and the tone mapping scales its sharpening by one minus that alpha.

:::rule
A post effect sits after the anti-aliasing resolve and before the tone mapping, adds no `FrameConstants` field, and is off in `AddNeutralPostProcess`. The reason: every effect shares one block of frame constants and one neutral test setup, so a new field or a hidden default would change every other picture ([Post chain](../image/why-post.md)).
:::

## A toy version

Before the real filter, take the plain idea: every pixel averages samples along its own motion. Take one row of 32 pixels with an edge at pixel 16, black to the left and white from pixel 16 on. A blur of 12 pixels with 8 samples puts the samples 1.5 pixels apart, from 5.25 pixels behind to 5.25 ahead.

The toy below does exactly that. Read `Blur`: it places samples at evenly spaced positions between minus one and one, scales them by the radius, which is half the length, and averages the colors there.

```cpp sketch="image-motion-blur-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdio>

namespace
{
	constexpr int c_Width = 32;
	constexpr int c_EdgeColumn = 16;

	// An ideal edge: black left of the edge column, white from it.
	float ReadColor(int pixel)
	{
		const int clamped = std::clamp(pixel, 0, c_Width - 1);
		return clamped >= c_EdgeColumn ? 1.0f : 0.0f;
	}

	// The blur of one pixel: the average of samples spread evenly along its own motion, centered on the pixel.
	float Blur(int pixel, float lengthPixels, int sampleCount)
	{
		const float radius = 0.5f * lengthPixels;
		float sum = 0.0f;
		for (int index = 0; index < sampleCount; index++)
		{
			const float position = -1.0f + (2.0f * static_cast<float>(index) + 1.0f) / static_cast<float>(sampleCount);
			const int samplePixel = static_cast<int>(std::floor(static_cast<float>(pixel) + 0.5f + position * radius));
			sum += ReadColor(samplePixel);
		}
		return sum / static_cast<float>(sampleCount);
	}
}

int main()
{
	const float lengthPixels = 12.0f;
	const int sampleCount = 8;
	for (int pixel = 9; pixel <= 22; pixel++)
		std::printf("pixel %2d: %.3f\n", pixel, Blur(pixel, lengthPixels, sampleCount));
	return 0;
}
```

```text output-of="image-motion-blur-toy.cpp"
pixel  9: 0.000
pixel 10: 0.000
pixel 11: 0.125
pixel 12: 0.250
pixel 13: 0.250
pixel 14: 0.375
pixel 15: 0.500
pixel 16: 0.500
pixel 17: 0.625
pixel 18: 0.750
pixel 19: 0.750
pixel 20: 0.875
pixel 21: 1.000
pixel 22: 1.000
```

1. **Line 13:** a sample past the end of the row reads the last pixel.
2. **Line 20:** the radius is half the blur's length.
3. **Line 24:** the sample positions are evenly spaced between minus one and one.
4. **Line 25:** the sample pixel is the pixel's center plus the offset, rounded down.
5. **Line 28:** the blur is the plain average of the samples.

Work one pixel by hand first. At pixel 15 the samples read offsets of -5.25, -3.75, -2.25, -0.75, 0.75, 2.25, 3.75 and 5.25. A sample reads white when the pixel plus a half plus its offset reaches 16, which needs an offset of 0.5 or more. Four offsets pass, so the pixel shows 4 over 8, one half.

The printed row agrees. It shows a ramp from pixel 11 to pixel 20: ten pixels for a blur that is 12 long. The outermost samples stop 0.75 pixels short of the span's ends, so the ramp is a little shorter than the blur.

The toy has no depth, no neighbors and only one direction. It blurs a pixel along its own motion only, so a still pixel next to a fast one stays sharp, and a foreground that moves with the camera smears like the rest. The real code fixes each of these.

## The real code

The real code follows the data. First every pixel gets a blur velocity. The function below turns the motion in :term[screen fractions]{id=screen-fraction} into pixels, multiplies by the shutter's share, clamps and drops short blurs.

```slang src="Strata/shaders/Include/MotionBlur.slang#L29-L39"
float2 GetBlurVelocity(float2 velocityUV, float depth, float2 uv)
{
	float2 motion = depth > 0.0 ? velocityUV : GetCameraMotion(uv, 0.0);
	float2 velocity = motion * u_Frame.ViewportSize.xy * u_MotionBlur.ShutterFraction;
	float speed = length(velocity);
	if (!(speed > 0.0))
		return float2(0.0);
	float clamped = min(speed, u_MotionBlur.MaxLength);
	float kept = clamped * smoothstep(u_MotionBlur.MinLength, 2.0 * u_MotionBlur.MinLength, clamped);
	return velocity * (kept / speed);
}
```

1. **Line 31:** a pixel where nothing was drawn, the sky, has no velocity of its own and takes the camera's motion.
2. **Line 32:** the motion in screen fractions becomes pixels and is scaled by the shutter's share.
3. **Lines 36–37:** the length is clamped, and a blur shorter than the floor is dropped by a smooth fade.
4. **Line 38:** the direction of the motion is kept while its length changes.

The length of the blur follows one formula:

$$L = \min\left(d \cdot \frac{a}{360},\; m \cdot H\right)$$

Here $L$ is the blur length in pixels. $d$ is the motion of the pixel since the last frame, in pixels. $a$ is the shutter angle in degrees. $m$ is `MotionBlurMaxLength`, and $H$ is the viewport's height in pixels. The sign "min" picks the smaller of its two arguments.

:::example
A camera turn moves a far tree 24 pixels per frame, in a view 1080 rows high. At a shutter of 180 degrees, $L$ is 24 times 180 over 360, which is 12 pixels. At 90 degrees it is 6 pixels.

The clamp is 0.02 times 1080, which is 21.6 pixels. A tree that moves 60 pixels per frame would be cut from 30 pixels to 21.6. A slow pan that moves a point 3 pixels gives 1.5 at 180 degrees. The floor is 1080 over 1080, which is 1 pixel, and blurs fade in from 1 to 2 pixels. The :term[smoothstep]{id=smoothstep} reads 0.5 at 1.5, so the kept blur is 0.75 pixels, its radius is under half a pixel, and the pixel keeps its color exactly.
:::

The tile pass then reads the blur velocity of every pixel in a tile. One :term[thread group]{id=thread-group} of 64 threads scans a tile, each thread takes a share of its pixels, and the threads reduce their results in :term[shared memory]{id=shared-memory} to the longest blur. The tile size is the larger of 8 and half the clamp length rounded up, so it is 11 pixels at 1080 rows (the exercises compute it at other heights). A tile is at least as wide as the longest sample reach.

```slang src="Strata/shaders/PostProcess/MotionBlurNeighbors.comp.slang#L31-L39"
	if (any(neighbor != tile + int2(x, y)))
		continue;
	float2 velocity = tileMax.xy;
	float speed = length(velocity);
	if (x != 0 && y != 0 && speed > 0.0 && abs(dot(velocity / speed, float2(x, y) * 0.70710678)) < 0.70710678)
		continue;
	if (dot(velocity, velocity) > dot(largest, largest))
		largest = velocity;
}
```

The neighbor pass picks, for each tile, the longest blur among nine tiles. The edge neighbors always count. A diagonal neighbor counts only when its blur runs toward the center tile, within 45 degrees of the diagonal: a blur that runs along the tile boundary never reaches in. The table shows the nine tiles.

| Row | Left | Middle | Right |
| --- | --- | --- | --- |
| Above | counts if its blur runs toward the center | always counts | counts if its blur runs toward the center |
| Same row | always counts | the tile itself | always counts |
| Below | counts if its blur runs toward the center | always counts | counts if its blur runs toward the center |

The pass also stores a spread in the z channel: how far any blur of the neighborhood lies from the longest one. When the spread is small, a surface moves as one piece, and the gather can read colors only and skip the depth work. A turning camera is that case: every point on screen moves alike whatever its depth.

The gather then runs for each pixel. It takes the neighbor max and spreads the samples over its span with the pixel's static offset. Even samples follow the neighborhood's direction. Odd ones follow the pixel's own direction when that pixel moves 1.5 pixels or more. The weight of each sample is the heart of the pass.

```slang src="Strata/shaders/PostProcess/MotionBlur.comp.slang#L37-L43"
float SampleWeight(float distance, float sampleDistance, float sampleRadius, float centerDistance, float centerRadius)
{
	float inFront = clamp(1.0 - (sampleDistance - centerDistance) / (c_DepthTolerance * centerDistance), 0.0, 1.0);
	float behind = clamp(1.0 - (centerDistance - sampleDistance) / (c_DepthTolerance * centerDistance), 0.0, 1.0);
	return inFront * Cover(distance, sampleRadius) + behind * Cover(distance, centerRadius)
		+ 2.0 * Span(distance, sampleRadius) * Span(distance, centerRadius);
}
```

The first term counts a sample that lies in front of the pixel and whose blur covers it. The second counts a sample behind the pixel when the pixel's own blur covers the sample. The third term lets two samples of one surface blur together. The factor `inFront` is 1 for a sample nearer than the pixel and falls to 0 when the sample lies 5 % farther; `behind` is its mirror. Within that tolerance both are 1, so two points at nearly the same depth count as one surface.

Take a character running with the camera in front of a fence that slides by. For a character pixel, the fence samples lie behind it, so only the second term can count them. That term uses the character's own radius, the half-pixel minimum, so it is zero for any sample farther than half a pixel. The character stays sharp.

For a fence pixel next to it, the character samples lie in front, so only the first term can count them. That term uses the radius of the sample, which is small, so it is zero too. No sharp color smears into the fence.

The CPU model in `Strata/src/Strata/Renderer/PostProcessMath.cpp` repeats this weight for one surface, so the tests can compute the profile of an edge without a GPU.

```cpp src="Strata/src/Strata/Renderer/PostProcessMath.cpp#L231-L237" from="auto cover = [](float distance, float r)" to="auto weight = [&](float distance)" symbol="PostProcessMath::GetMotionBlurProfile"
auto cover = [](float distance, float r) { return std::clamp(1.0f - distance / r, 0.0f, 1.0f); };
auto span = [](float distance, float r)
{
	const float t = std::clamp((distance - 0.95f * r) / (0.1f * r), 0.0f, 1.0f);
	return 1.0f - t * t * (3.0f - 2.0f * t);
};
auto weight = [&](float distance) { return 2.0f * cover(distance, sampleRadius) + 2.0f * span(distance, sampleRadius) * span(distance, sampleRadius); };
```

The CPU side decides whether the three passes run. It reads the conditions of the quality row and the component, sets the constants and dispatches.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L665-L672" from="const float shutter =" to="parameters.SourceMask =" symbol="SceneRenderer::RenderMotionBlur"
const float shutter = std::isfinite(postProcess.MotionBlurShutterAngle) ? std::clamp(postProcess.MotionBlurShutterAngle, 0.0f, 360.0f) : 180.0f;
const float maxLength = std::isfinite(postProcess.MotionBlurMaxLength) ? std::clamp(postProcess.MotionBlurMaxLength, 0.005f, 0.05f) : 0.02f;
parameters.ShutterFraction = shutter / 360.0f;
parameters.MaxLength = maxLength * static_cast<float>(height);
parameters.MinLength = static_cast<float>(height) / 1080.0f;
parameters.TileSize = std::max(RenderData::c_MotionBlurMinTileSize, static_cast<uint32_t>(std::ceil(parameters.MaxLength * 0.5f)));
parameters.SampleCount = RendererQuality::GetMotionBlurSampleCount(m_Specification.Quality.MotionBlurQuality);
parameters.SourceMask = source == PostSource::DepthOfField ? 1u : 0u;
```

The conditions live in `SceneRenderer.cpp`. The pass is wanted when the view's option is on, the output is not :term[high dynamic range]{id=high-dynamic-range}, the component's field is on and its shutter angle is above zero. It runs when it is wanted, the frame has a motion history and the camera did not cut.

A camera cut is a move of more than 10 world units since the previous frame, or a turn of more than 45 degrees, or the first frame.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3808-L3817"
if (motionBlurWanted && m_Stats.MotionHistory && !cameraCut)
{
	gpuTimer.Next(gpuStages.MotionBlur);
	commandList->beginMarker("MotionBlur");
	if (RenderMotionBlur(commandList, postProcess, postSource))
		postSource = PostSource::MotionBlur;
	else
		degraded = true;
	commandList->endMarker();
}
```

1. **Line 3808:** the three conditions: the view and the component want the blur, the frame has a motion history, and the camera did not cut.
2. **Lines 3812–3813:** when the pass succeeds, the later passes read its output as their source.
3. **Line 3815:** when it fails, the frame is marked degraded and carries on without the blur.

If the pass fails to make its resources, the frame carries on without it and notes the failure. The players' row, `MotionBlurQuality`, picks 8, 12 or 16 samples, or turns the passes off. More samples cost more gather time and give less noise: the CPU model's streak noise at 16 samples is smaller than at 8. [Quality settings](../image/quality-settings.md) teaches how the rows work as a system.

The figures show the effect during a fast camera turn around the robot on the Third-Person course. Without the pass every edge is sharp. With it the far course and the pine at the left streak sideways, and the streak doubles from 90 to 180 degrees. The robot stays sharp, because the camera turns around it and keeps it still on the screen, and so do the near trees beside it.

::figure{id=turn-off}

::figure{id=turn-mb90}

::figure{id=turn-mb180}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Accumulating sub-frames | Film renderers that do not run in real time | Exact streaks, with correct hidden surfaces | Several frames of work for each frame shown |
| Scatter of each pixel along its motion | Papers on motion blur for games | Streaks that start at the moving object | A depth sort or :term[atomic writes]{id=atomic-write} on a GPU |
| A per-object blur by geometry smearing | Older real-time engines | Blur of objects with no motion vectors | Extra geometry, and a failure on skinned meshes and meshes that bend |
| Random sample offsets that change each frame | Temporal renderers | Less banding, with noise averaged away by history | A noise that crawls when the history is reset |
| No depth weights | Cheap blur passes | Fewer reads | Foreground colors smeared over sharp objects, or the reverse |

## How it is tested

Two suites check the pass. `Renderer.PostProcessMath` holds the CPU model's tests. A still edge stays exact, and blurs of 6, 12 and 24 pixels cover about their length. The profile never goes down along an edge, and more samples give less noise. `GPU.SceneRenderer.MotionBlur` renders a wall with an edge on a GPU and checks the cases below.

- A still camera and a shutter of 0 render bit for bit like motion blur off.
- A moving camera blurs an edge over the shutter's share, at 180 and 90 degrees, and the width matches the model within a pixel.
- A foreground that moves with the camera stays sharp over a blurred background.
- Camera cuts and frames without history do not blur, and both draw paths blur equally.
- Blurred pixels are not sharpened.

Run the CPU suite with `StrataTests --test-suite=Renderer.PostProcessMath`, and the GPU suite with `StrataTests --test-suite=GPU.SceneRenderer.MotionBlur` on a machine with a :term[Vulkan]{id=vulkan} driver.

## Changing it safely

Three rules protect the pass.

- The pass reads the motion history and adds no `FrameConstants` field, because post effects add none ([Post-processing](../image/why-post.md)).
- A shader that writes the high dynamic range target clamps its output, which the gather does with `c_MaxHDRValue`.
- A new costly knob is a row of the quality settings with a line for each preset.

To change the weights, change `GetMotionBlurProfile` with them: the GPU test compares the two within 2 of 255 in each column of the edge, averaged over its rows. To change what moves a blur, remember the order. The longest blur of a tile feeds the neighbor pass, which feeds the gather. A new input must reach all three, or the gather's reach falls short of the blur.

## Summary

- The blur length in pixels is the motion times the shutter angle over 360, clamped to a share of the image's height, with blurs under one pixel dropped at 1080 rows.
- The tile max and the neighbor max tell each pixel how far anything can blur over it, so eight to sixteen samples are enough.
- Depth weights let a nearer moving surface spread over a background and keep a still foreground sharp.
- The first frame, a camera cut, a missing motion history, the editor camera, captures and the user interface never blur.

## Check yourself

1. A view is 1080 rows high. A point moves 40 pixels per frame at a shutter angle of 270 degrees and a maximum length of 0.02. How long is its blur?

   :::answer{tests="predict-length"}
   40 times 270 over 360 is 30 pixels, but the clamp is 0.02 times 1080, which is 21.6 pixels. The blur is 21.6 pixels, and its direction stays as it was.
   :::

2. Why does the neighbor pass exist? (a) The tile maxima are too noisy. (b) A fast tile can blur over a still tile next to it, so each pixel needs the longest blur of its neighborhood. (c) The gather cannot read the tile maxima directly.

   :::answer{tests="reconstruction"}
   Answer (b). The gather of a still pixel must reach as far as the fastest blur that can cover it. Answer (a) is wrong, because maxima carry no noise. Answer (c) is wrong, because the gather does read a tile texture; it reads the neighbor maxima.
   :::

3. A runner in front of a sliding fence is sharp while the fence blurs. Which part of the weight keeps the runner's color out of the fence?

   :::answer{tests="depth-weights"}
   The depth terms. A sample nearer than the pixel counts only when its own blur radius reaches the pixel, and the runner's radius is near zero, so it does not reach the fence.
   :::

4. The editor camera turns while the game plays in a Scene view. Does it blur? Which line decides?

   :::answer{tests="never-blurred"}
   No. In `ViewportRenderer.cpp` the option is true only for a view from a scene camera, while the game plays, and not for single images. The editor camera is not a scene camera.
   :::

## Exercises

1. **Basic.** Predict the length of a streak that the Third-Person course's camera turn leaves at a shutter of 180 and at 90 degrees, with a motion of 24 pixels per frame. Then run the look-dev shots `tp.live.turn.mb180` and `tp.live.turn.mb90`, measure the streaks, and look at the same turn through the editor camera.

   :::answer[Worked solution]{tests="predict-length,never-blurred"}
   The lengths are 12 and 6 pixels in a view 1080 rows high. A measured streak is within a pixel of them. Through the editor camera the turn stays sharp, because only the game's camera blurs, and only while the game plays.
   :::

2. **Medium.** Write a program that prints, for views of 720, 1080 and 2160 rows, the longest blur, the shortest blur and the tile size.

   :::answer[Worked solution]{tests="predict-length" solution="sketches/image-motion-blur-sizes.cpp"}
   The longest blur is 0.02 times the height, the shortest is the height over 1080, and the tile is the larger of 8 and half the longest, rounded up.

   ```cpp sketch="image-motion-blur-sizes.cpp"
   #include <algorithm>
   #include <cmath>
   #include <cstdio>
   #include <initializer_list>

   int main()
   {
   	const float maxLengthShare = 0.02f;
   	for (const int height : { 720, 1080, 2160 })
   	{
   		const float maxLength = maxLengthShare * static_cast<float>(height);
   		const float minLength = static_cast<float>(height) / 1080.0f;
   		const int tileSize = std::max(8, static_cast<int>(std::ceil(maxLength * 0.5f)));
   		std::printf("%d rows: longest %.1f px, shortest %.2f px, tile %d px\n", height, maxLength, minLength, tileSize);
   	}
   	return 0;
   }
   ```

   ```text output-of="image-motion-blur-sizes.cpp"
   720 rows: longest 14.4 px, shortest 0.67 px, tile 8 px
   1080 rows: longest 21.6 px, shortest 1.00 px, tile 11 px
   2160 rows: longest 43.2 px, shortest 2.00 px, tile 22 px
   ```

   1. **Line 11:** the longest blur is the share times the height.
   2. **Line 12:** the shortest blur grows with the height over 1080.
   3. **Line 13:** the tile is at least 8 pixels and otherwise half the longest blur, rounded up.
   :::

3. **Hard.** Trace it yourself: find every condition under which a frame does not blur, and the line that decides each.

   :::answer[Worked solution]{tests="never-blurred"}
   In `SceneRenderer.cpp`, `motionBlurWanted` combines the view's option, a non-HDR output, the component's field and a shutter above zero. `IsCameraCut` decides the cut, `m_Stats.MotionHistory` the history, and the `if` that calls `RenderMotionBlur` joins the three. `ViewportRenderer.cpp` sets the view's option, and in `SceneRendererPost.cpp` a quality row set to Off clears the component's field.
   :::

## Where it lives in Strata

- Passes: `Strata/shaders/PostProcess/MotionBlurTiles.comp.slang`, `MotionBlurNeighbors.comp.slang`, `MotionBlur.comp.slang`, and `Strata/shaders/Include/MotionBlur.slang`.
- CPU: `RenderMotionBlur` and `EnsureMotionBlurResources` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp`; the model `GetMotionBlurProfile` in `Strata/src/Strata/Renderer/PostProcessMath.cpp`.
- Fields: `MotionBlur`, `MotionBlurShutterAngle`, `MotionBlurMaxLength` of the Post Process; the quality row `MotionBlurQuality`.
- Tests: `Renderer.PostProcessMath` and `GPU.SceneRenderer.MotionBlur`.

## Further reading

- McGuire, Hennessy, Bukowski and Osman, "A Reconstruction Filter for Plausible Motion Blur", 2012: the tile and neighbor maxima and the depth-aware gather; advanced.
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", 2014: a production gather filter; intermediate.
