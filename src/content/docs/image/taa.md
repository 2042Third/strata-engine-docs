---
id: image/taa
title: "Temporal anti-aliasing"
description: "How Strata averages jittered frames into one sharp image: the history, reprojection, the clamp and clip, and the rules that keep trails away."
kind: internals
size: XL
tracks: [E]
needs: [image/spatial-aa, draw/motion-vectors, basics/math-projection]
time: 110
learn:
  - id: jitter-copy
    text: explain why the jitter lives only in the frame's copy of the projection and how its eight phases are made
  - id: resolve-path
    text: trace how the resolve reads the history along the motion, filters it, clamps it and blends it with the frame
  - id: artifact-rules
    text: compare the clamp, the variance clip, the reactive mask and the disocclusion test by the artifact each prevents
  - id: history-life
    text: name what starts the history again, what single images do, and which limits TAA documents
  - id: change-resolve
    text: change a resolve setting and predict the look that follows
since: 0.6.0
status: final
---

**Temporal anti-aliasing** (TAA) is the part of Strata's post chain that makes edges and thin lines smooth by looking at earlier frames. Each frame it draws the scene a little to one side, blends the result with what earlier frames showed, and hands the sum to the :term[tone mapping]{id=tone-mapping-image}. It does not make the :term[motion vectors]{id=motion-vector}, it does not blur the picture on purpose, and it is one choice among several: a scene can use the single-frame methods of the [spatial anti-aliasing page](../image/spatial-aa.md) instead. The page ends with a toy you can run, the :term[shader]{id=shader} line by line, and the rules that keep trails and ghosts out.

## The problem and how engines solve it

A game draws a pixel from one sample: the colour of the surface at the pixel's centre. An edge that cuts a pixel in two is drawn as all of one surface or all of the other, so the edge becomes stair-steps, and as the camera moves the steps crawl. The single-frame methods guess a smooth edge from one image. They cannot know what lies between the samples.

One idea gives the missing samples for free: take them in different frames. If each frame samples each pixel at a slightly different place, then eight frames hold eight samples of that pixel, and their average is close to what eight samples in one frame would give. Drawing eight samples per pixel in one frame costs eight times as much. Spread over eight frames, it costs one frame's work each.

Four problems follow, and each gives the page a section:

- First, the samples must differ. Strata moves the whole image by a fraction of a pixel each frame. That move is the **jitter**: a small sub-pixel offset of the projection, different in every frame.
- Second, the frames must be kept. The image the previous frames made, kept in a texture beside the current one, is the **history**. The newest frame is blended into it with a small weight, so older frames fade away like an exponential moving average.
- Third, the history must be read in the right place. When the camera or an object moves, the surface that shows in a pixel now showed in another pixel one frame ago. **Reprojection** moves the read position back along the motion vectors, so each pixel reads the history where its surface used to be.
- Fourth, the history can be wrong. A surface that was hidden last frame has no history, and a surface that changed colour has an old one. A blend of wrong history and the new frame is a trail behind a moving object. Most of the work in a good TAA is the rules that find wrong history and drop it.

Together, the jitter, the history, the reprojection and the rules against wrong history are what Strata calls **TAA**.

Engines solve the problem in the same four parts and differ in the rules. Published designs clamp the history to the colours of the pixel's neighbours in the new frame, or clip it toward their mean. Some also test the depth of the surface, as one well-known talk on a puzzle game did.

Temporal upscaling goes one step further. The engine draws fewer pixels than the screen shows and fills the rest from the history; Unreal Engine's Temporal Super Resolution is one such design, and the graphics vendors' libraries are others. Strata does not draw fewer pixels: its policy is to draw at the size the image is shown. Those libraries are outside this page.

Strata's design stays with plain TAA, and keeps it one choice among others. The next sections show how it is built. This page assumes you know the single-frame methods and the motion vectors; the [motion vector page](../draw/motion-vectors.md) makes them.

## The map

The jitter lives in the :term[central processing unit]{id=processor} (CPU) code of `SceneRenderer`; the rest is one compute shader and one function of the tone mapping. The diagram shows who writes what, in the order of a frame.

```mermaid caption="One frame of temporal anti-aliasing. The camera's copy is jittered, the scene is drawn with motion vectors, the resolve blends the frame with the history, and the tone mapping sharpens only what is shown." alt="A flow from a jittered projection through the scene pass and its motion vectors to the resolve. The resolve reads the history and writes a new history. The new history goes to the tone mapping, which sharpens the displayed image."
flowchart LR
	A[SceneRenderer: jitter in the frame copy] --> B[Scene pass: HDR color, depth, velocity]
	B --> C[TAA.comp resolve]
	H[(History, previous texture)] --> C
	C --> N[(History, other texture)]
	N --> T[Tonemap.frag: Sharpen on the displayed image]
	N -. next frame .-> H
```

The files are these. `Strata/src/Strata/Renderer/SceneRenderer.cpp` owns the jitter, the history's counters and the resolve's constants. `Strata/shaders/PostProcess/TAA.comp.slang` is the resolve. `Strata/shaders/PostProcess/Tonemap.frag.slang` sharpens the shown image. `Strata/src/Strata/Renderer/RendererComponents.h` holds the presets and their settings.

Two pieces of state belong to each :term[renderer]{id=renderer}, never to the scene or the application. One is the pair of history textures in the :term[half-float]{id=half-float} format with four channels (RGBA16F), which swap roles every frame (**ping-pong**: the resolve reads one and writes the other). The other is the history's frame counter. The renderer also keeps the resolve's compute :term[descriptor sets]{id=descriptor-set}; the post chain's `PostSource` hands the resolve the scene's colours in :term[high dynamic range]{id=high-dynamic-range} (HDR).

## The contract

What callers may assume and what they must do:

- The frame's jittered projection is a copy. Culling, levels of detail and the shadow cascades use the plain camera, the one without the jitter.
- The history counts frames, not time. A slow frame keeps the history; a skipped device frame ends it.
- Every writer of the :term[HDR]{id=high-dynamic-range} target before the resolve writes alpha 1; blended surfaces multiply it by one minus their alpha. After the transparent pass, alpha is the light that passes through them. Only the reactive mask reads it.
- Sharpening touches the displayed image only, never the history.
- The player's choice wins: the **Anti-aliasing** row of the graphics quality settings overrides the method that the scene's Post Process component names.
- Nothing may need history to look right.

:::rule
Jitter only the frame's copy of the camera. Culling, levels of detail and the sun's cascade cache must see the same camera every frame, or objects would pop and the cascades would re-draw every frame. See [bounds and culling](../draw/bounds-culling.md).
:::

:::why
**Nothing needs history to look right.** TAA is one anti-aliasing choice among several, and a player can choose fast approximate anti-aliasing (:term[FXAA]{id=fxaa}), the morphological method, or none. So no effect may need TAA to hide its noise. The sun's shadow filter uses a fixed noise tile, the ambient occlusion is resolved inside the frame, and the static :term[dither]{id=dither} and the motion blur's offsets look right in a single frame. Each is stable with TAA off, and TAA only improves it.

One thing bends the rule. The Checkerboard setting of Medium's reflections needs the history; [the reflections page](../indirect/ssr.md) says what happens without it. The point and spot lights' shadow filter keeps the rule: its noise is fixed per pixel, as the sun's is, so its grain stands still with or without TAA. [The local shadows page](../light/local-shadows.md) has that filter. The cost of the rule is some noise or stair-steps that an effect could have hidden behind the history; the gain is that a player never sees a broken scene for choosing another method.
:::

## A toy version

The toy is a TAA on one row: 16 pixels and a bar 3.4 pixels wide, with the four parts from the problem section. It has the Halton jitter, the history, reprojection and a clamp, and nothing else.

Before the sketch, the numbers by hand. Look at a pixel that a bar's right edge cuts, with the bar covering the left 0.3 of it. Eight samples fall at the pixel's left edge plus 0.5, 0.25, 0.75, 0.125, 0.625, 0.375, 0.875 and 0.0625 (the jitter moves the sample off the centre; the next sections say how the numbers arise). Three of the eight positions fall inside the bar: 0.25, 0.125 and 0.0625. The frames therefore read 0, 1, 0, 1, 0, 0, 0, 1.

The weights are 1/n for frame n, an even average while the history is short. Frame 1 gives 0. Frame 2 gives half of 1, so 0.5.

Frame 3 keeps two thirds of 0.5 and adds nothing: 0.333. Frame 4 keeps three quarters of 0.333 and adds a quarter of 1: 0.5. Frames 5, 6 and 7 give 0.4, 0.333 and 0.286.

Frame 8 keeps seven eighths of 0.286 and adds an eighth of 1: exactly 0.375, which is 3 of 8. The pixel now shows 37.5 % bar, close to the true 30 %: eight samples can only count in eighths.

:::note
Each step is $h_n = (1 - w)\,h_{n-1} + w\,c_n$. Here $c_n$ is the new frame's value for the pixel and $h_{n-1}$ is the history read for it. The result $h_n$ is the history written, and $w$ is the weight of the new frame, a number from 0 to 1. With $w = 1/n$ the result is the average of all n frames. With a fixed small $w$ the older frames fade by the factor $1 - w$ each frame, which makes an exponential moving average: an average in which each value weighs less than the one after it.
:::

:::question
New to C++? Read [Programming from zero 1](../basics/programming-1.md), [Programming from zero 2](../basics/programming-2.md), [Programming from zero 3](../basics/programming-3.md) and [Generic C++](../basics/cpp-generic.md) first.
:::

Here is the toy. Read `Run` first: it makes the jitter, renders a frame, resolves it and keeps the history. `Resolve` holds the reprojection, the clamp and the blend.

```cpp sketch="image-taa-toy.cpp"
// A temporal anti-aliasing toy in one dimension: a row of 16 pixels and a bar 3.4 pixels wide.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

constexpr int c_Width = 16;
constexpr int c_Phases = 8;

float RadicalInverse(int index, int base)
{
	float result = 0.0f;
	float scale = 1.0f / static_cast<float>(base);
	for (; index > 0; index /= base)
	{
		result += static_cast<float>(index % base) * scale;
		scale /= static_cast<float>(base);
	}
	return result;
}

// One sample per pixel, taken at the pixel's centre moved by the jitter: inside the bar is 1, outside it is 0.
std::vector<float> Render(float left, float jitter)
{
	std::vector<float> image(c_Width);
	for (int x = 0; x < c_Width; x++)
	{
		const float position = static_cast<float>(x) + 0.5f + jitter;
		image[x] = (position >= left && position < left + 3.4f) ? 1.0f : 0.0f;
	}
	return image;
}

// The history at a position in pixels: a linear blend of the two texels whose centres surround it.
float SampleHistory(const std::vector<float>& history, float position)
{
	const float shifted = std::clamp(position - 0.5f, 0.0f, static_cast<float>(c_Width - 1));
	const int first = static_cast<int>(std::floor(shifted));
	const int second = std::min(first + 1, c_Width - 1);
	const float fraction = shifted - static_cast<float>(first);
	return history[first] * (1.0f - fraction) + history[second] * fraction;
}

// Reproject (read where the pixel was one frame ago), clamp to the neighbours' range, blend.
std::vector<float> Resolve(const std::vector<float>& current, const std::vector<float>& history, float motion, bool clamp, float weight)
{
	std::vector<float> result(c_Width);
	for (int x = 0; x < c_Width; x++)
	{
		float low = current[x];
		float high = current[x];
		for (int offset = -1; offset <= 1; offset++)
		{
			const float neighbour = current[std::clamp(x + offset, 0, c_Width - 1)];
			low = std::min(low, neighbour);
			high = std::max(high, neighbour);
		}
		float past = SampleHistory(history, static_cast<float>(x) + 0.5f - motion);
		if (clamp)
			past = std::clamp(past, low, high);
		result[x] = past * (1.0f - weight) + current[x] * weight;
	}
	return result;
}

// Frame n (counting from 1) weighs 1 / n until the weight reaches 1/8, as the engine's frames after a reset do.
std::vector<float> Run(float left, float speed, float motion, bool clamp, int frames)
{
	std::vector<float> history;
	for (int frame = 0; frame < frames; frame++)
	{
		const float jitter = RadicalInverse(frame % c_Phases + 1, 2) - 0.5f;
		const std::vector<float> current = Render(left + speed * static_cast<float>(frame), jitter);
		const float weight = std::max(1.0f / static_cast<float>(frame + 1), 1.0f / 8.0f);
		history = frame == 0 ? current : Resolve(current, history, motion, clamp, weight);
	}
	return history;
}

void Print(const char* label, const std::vector<float>& image)
{
	std::printf("%-22s", label);
	for (const float value : image)
		std::printf("%d", static_cast<int>(std::lround(value * 9.0f)));
	std::printf("\n");
}

int main()
{
	Print("still, 1 frame", Run(4.3f, 0.0f, 0.0f, true, 1));
	Print("still, 8 frames", Run(4.3f, 0.0f, 0.0f, true, 8));
	Print("still, 40 frames", Run(4.3f, 0.0f, 0.0f, true, 40));
	Print("moving, current frame", Render(2.0f + 7.0f, RadicalInverse(8, 2) - 0.5f));
	Print("moving, motion known", Run(2.0f, 1.0f, 1.0f, true, 8));
	Print("moving, no motion", Run(2.0f, 1.0f, 0.0f, false, 8));
	Print("moving, no motion+clamp", Run(2.0f, 1.0f, 0.0f, true, 8));
	return 0;
}
```

```text output-of="image-taa-toy.cpp"
still, 1 frame        0000999900000000
still, 8 frames       0000699700000000
still, 40 frames      0000699700000000
moving, current frame 0000000009999000
moving, motion known  0000000009995000
moving, no motion     0012335353311000
moving, no motion+clamp0000000089991000
```

1. **Lines 10–20:** the radical inverse, the same loop as the engine's.
2. **Lines 23–32:** one sample per pixel at its centre plus the jitter; inside the bar the value is 1, so the edges show stair-steps.
3. **Lines 45–64:** the resolve reads the history one frame back along the motion, clamps it to the neighbours' range when asked, and blends.
4. **Lines 67–78:** the weight is 1 over the frame count until it reaches 1/8, as after a reset in the engine.

The sketch prints each row as a digit from 0 (dark) to 9 (bright). Look at three things in its output: the still bar after 1, 8 and 40 frames, the moving bar when the motion is known, and the moving bar when it is missing.

The first row is the single-frame image: four pixels, all or nothing, because each sample sits at a pixel centre. After eight frames the edge pixels show 6 and 7, close to the true coverage of 0.7 of each. Frame 40 looks the same as frame 8: the average has gone through every phase again.

In the moving rows, the current frame is the sharp bar at its last position. With the right motion, the history follows the bar and the edge pixel is soft. With no motion and no clamp, the bar leaves a trail: the old positions stay in the history. The row `0012335353311000` is that smear, called **ghosting**, 7 pixels long.

The last row adds the **neighborhood clamp**: the history is limited to the lowest and highest value of the pixel and its two neighbours in the new frame. A trail pixel is far from the colours around it in the new frame, so it is cut to the nearest value in the range. The trail shrinks from 7 pixels to about one, even though the toy knew nothing about the motion. The clamp is TAA's safety net: whatever the cause of a wrong history, it cannot move far from what the frame itself shows.

What the toy omits is most of the engine. It has no 2D jitter, no filter for reads between pixels, no :term[luminance]{id=luminance} weights, no detection of uncovered surfaces and no transparent surfaces. The real code adds each for a reason that the next sections show.

## The jitter in the frame's camera copy

The real code starts with the jitter, and the jitter has two jobs: its offsets must cover the pixel evenly, and it must not disturb anything else.

The first job belongs to the **Halton sequence**, a list of numbers in [0, 1) that fills the interval evenly without repeating a point. Strata takes the first eight numbers of two such lists, one per axis.

Each number is the **radical inverse** of an index: write the index in a base, mirror its digits across the point, and read the result as a fraction. In :term[base 2]{id=binary} the index 6 is 110; mirrored it is 0.011, which is 1/4 + 1/8 = 0.375. In base 3 the index 4 is 11, giving 1/3 + 1/9 = 4/9.

In the renderer's words, the **jitter (TAA)** is a sub-pixel offset of the projection, in pixels from the pixel's centre, different in each frame. The function below computes it for a phase; watch the loop that mirrors the digits.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2934-L2950"
glm::vec2 SceneRenderer::GetTemporalJitter(uint32_t phase)
{
	// The radical inverses of the phase's index in bases 2 and 3; the index starts at 1, since 0 is the origin of both.
	const auto radicalInverse = [](uint32_t index, uint32_t base)
	{
		float result = 0.0f;
		float scale = 1.0f / static_cast<float>(base);
		for (; index > 0; index /= base)
		{
			result += static_cast<float>(index % base) * scale;
			scale /= static_cast<float>(base);
		}
		return result;
	};
	const uint32_t index = phase % c_TemporalJitterPhases + 1;
	return glm::vec2(radicalInverse(index, 2), radicalInverse(index, 3)) - 0.5f;
}
```

1. **Lines 2941–2944:** the loop starts the scale at 1/base and divides it by the base at each digit, so each digit lands one place further right.
2. **Line 2948:** the index starts at 1, since index 0 gives 0 in every base, and the phase wraps at 8.
3. **Line 2949:** x uses base 2 and y uses base 3, minus 0.5, so the offset lies within half a pixel of the centre in each axis.

The two bases share no factor, so the eight points do not line up in rows. The eight offsets are listed in the test `The jitter's eight phases are distinct sub-pixel offsets that cover the pixel evenly`. The toy used base 2 only. The pair of bases is the same idea in two dimensions.

The jitter has to enter the projection without leaking elsewhere. The renderer builds the frame's constants from the camera, and the jitter goes into one copy of the :term[projection matrix]{id=projection-matrix}. A jitter in pixels becomes a shift in :term[clip space]{id=clip-space} of twice the offset over the viewport size: at 1920 pixels wide, an offset of 0.25 pixel is 2 × 0.25 / 1920 ≈ 0.00026. Clip space's +Y is up and the jitter's +y is down, hence the sign flip.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3229-L3251"
RenderData::FrameConstants frame = {};
frame.View = GetRelativeView(camera);
frame.Projection = camera.Projection;
if (m_TemporalFrame)
	frame.Projection = glm::translate(glm::mat4(1.0f), glm::vec3(jitterClip, 0.0f)) * camera.Projection;
frame.ViewProjection = frame.Projection * frame.View;
frame.InverseView = glm::inverse(frame.View);
frame.InverseProjection = glm::inverse(frame.Projection);
frame.InverseViewProjection = glm::inverse(frame.ViewProjection);
frame.JitterParams = glm::vec4(jitterClip, previousJitterClip);
// Built in double, from the same products, so a camera that did not move gives the same matrix twice (no motion).
frame.UnjitteredViewProjection = glm::mat4(glm::dmat4(camera.Projection) * glm::dmat4(frame.View));
frame.PreviousViewProjection = frame.UnjitteredViewProjection;
if (m_Stats.MotionHistory)
{
	const glm::dvec3 offset = glm::dvec3(camera.Position) - glm::dvec3(m_MotionCamera.Position);
	frame.PreviousViewProjection = glm::mat4(glm::dmat4(m_MotionCamera.Projection) * glm::dmat4(m_MotionCamera.RelativeView)
		* glm::translate(glm::dmat4(1.0), offset));
}
// Per-pixel noise turns by the golden ratio's fraction of a turn each frame of the history (from its reset on, so captures
// are deterministic): the frames the history averages sample the turn evenly.
const double noiseTurn = m_TemporalFrame ? std::fmod(static_cast<double>(m_TemporalFrames - 1) * 0.6180339887498949, 1.0) : 0.0;
frame.TemporalParams = glm::vec4(m_Stats.MotionHistory ? 1.0f : 0.0f, m_PreExposure, static_cast<float>(noiseTurn), 0.0f);
```

1. **Lines 3231–3233:** the frame's projection starts as the camera's and is replaced by a translated copy only when TAA runs this frame.
2. **Lines 3240–3241:** the plain view and projection feed the motion vectors. They are built in double precision from the same products, so two frames without camera motion give equal matrices.
3. **Lines 3248–3251:** the noise that other effects use is turned by a fraction of a turn each frame, written into the frame constants for every shader.

That last part is the **golden-ratio turn**: each frame of the history adds 0.618... of a turn to the per-pixel noise. The golden ratio's fraction is the number that spreads the turns most evenly, so any run of frames covers the turn's circle without bunching. The code counts from the history's reset, so a capture is the same every time. :term[Overlays]{id=overlay-gpu} such as the selection outline, the grid and the game's world-space canvas use the plain matrices, so they stay stable instead of shimmering: tests such as `With TAA the grid on a floor and text on a wall cover the same pixels in every jitter phase` pin this.

## The history's life

The **camera cut** is a frame where the view jumped: it moved more than 10 world units or turned by more than about 45 degrees between two frames, the texture streamer's test. The history of the old view is no use to the new one, so the renderer drops it. This is one of several reasons. The renderer works out in one block whether the history continues.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3144-L3177"
const bool cameraCut = IsCameraCut(camera);
const bool historyReset = m_ResetHistory; // The TAA's branch clears it; spatial reflections start again on it too
m_TemporalFrame = temporalWanted && m_MotionFrame && EnsureTemporalResources();
const bool temporalFailed = temporalWanted && !m_TemporalFrame;
m_TemporalResolved = false;
glm::vec2 jitterClip(0.0f);
glm::vec2 previousJitterClip(0.0f);
if (m_TemporalFrame)
{
	const uint64_t deviceFrame = Renderer::GetFrameNumber();
	const bool continues = m_TemporalFrames > 0 && m_TemporalRender != 0 && m_TemporalRender == m_RenderCount && !cameraCut && !m_ResetHistory
		&& (m_TemporalSceneId == renderScene.GetId() || renderScene.GetCloneSource() == m_TemporalSceneId)
		&& (deviceFrame == m_TemporalDeviceFrame || deviceFrame == m_TemporalDeviceFrame + 1);
	if (continues)
	{
		// Kept within the counter in whole cycles of the jitter, so its phases go on in order.
		constexpr uint32_t c_FramesWrap = 1u << 30;
		m_TemporalFrames = m_TemporalFrames + 1 < c_FramesWrap ? m_TemporalFrames + 1 : m_TemporalFrames + 1 - c_FramesWrap / 2;
		previousJitterClip = m_TemporalJitterClip;
	}
	else
	{
		m_TemporalFrames = 1;
		m_HistoryResets++;
	}
	m_TemporalRender = 0; // Until this frame resolved it
	m_TemporalDeviceFrame = deviceFrame;
	m_TemporalSceneId = renderScene.GetId();
	m_ResetHistory = false;
	m_Stats.Jitter = GetTemporalJitter((m_TemporalFrames - 1) % c_TemporalJitterPhases);
	// Clip space's +Y is up, the jitter's +y down.
	jitterClip = glm::vec2(2.0f * m_Stats.Jitter.x / static_cast<float>(m_ViewportSize.x), -2.0f * m_Stats.Jitter.y / static_cast<float>(m_ViewportSize.y));
	m_TemporalJitterClip = jitterClip;
}
```

1. **Lines 3144–3147:** the frame uses TAA only when it is wanted and has motion vectors and resources. Without them it is drawn with FXAA.
2. **Lines 3154–3156:** the history continues only when the last frame resolved it and no cut or reset came. The scene must be the same one or its clone source (entering Play keeps the history), and the device frame this one or the next.
3. **Lines 3159–3162:** the counter wraps in whole cycles of the jitter, so the phases carry on in order.
4. **Lines 3166–3167:** otherwise the counter starts at 1, and the history counts a reset.
5. **Line 3173:** the phase comes from the counter, so a restart always begins at the same offset.

The conditions are counted in frames, never in time: a slow frame keeps the history and a skipped device frame ends it. That fits the weights, which depend on how many frames the history holds, not on how long they took. A size change frees the textures, so it also ends the history. So do a change of scene, a view that was hidden, and a call to `ResetHistory`. The diagram shows how the weight follows the counter.

```mermaid caption="The history's life. After a start the frames are averaged evenly with weight one over the count, then the weight stays at one over the history frames. A cut, a reset or a size change returns to the start." alt="A state diagram. A reset enters the state of the first frame with weight 1. The next frames have weight 1 over n until n equals 8. After that the weight stays 1 over 8. Any cut, reset or size change returns to the first frame."
stateDiagram-v2
	[*] --> First: reset, cut, resize
	First --> Even: next frame
	Even --> Even: weight 1/n, n below 8
	Even --> Steady: n reaches 8
	Steady --> Steady: weight 1/8
	Steady --> First: cut, reset, resize, scene change
```

**Settle frames** are the frames a still view needs before its image is final: eight at the preset values, because the first eight frames average each jitter phase once. After that each new frame weighs 1/8 and older ones fade. The newest 6 frames hold $1 - (7/8)^6 \approx 0.55$ of the image, and the newest 18 hold $1 - (7/8)^{18} \approx 0.91$.

A single image, such as a capture or the project's picture, has no earlier frames. Strata draws such a view for eight frames and takes the last; thumbnails draw with FXAA instead. A single image that cannot wait should disable TAA.

## The resolve: finding the history

The resolve is one compute shader, in 8 by 8 pixel groups, that writes the new history. It begins with the neighbourhood. For each pixel it reads the 3 by 3 pixels of the new frame and keeps two things: the lowest and highest colour, and the position of the nearest surface.

```slang src="Strata/shaders/PostProcess/TAA.comp.slang#L199-L246"
float3 current = u_Current.Load(int3(pixel, 0)).rgb;
float3 low = RGBToYCoCg(current);
float3 high = low;
float2 uv = (float2(pixel) + 0.5) * u_Frame.ViewportSize.zw;
float depth = u_Depth.Load(int3(pixel, 0)).r;
// The nearest surface (reversed-Z: the largest depth) of the neighborhood, the pixel's own on ties.
float nearestDepth = depth;
int2 nearestPixel = pixel;
for (int y = -1; y <= 1; y++)
{
	for (int x = -1; x <= 1; x++)
	{
		if (x == 0 && y == 0)
			continue;
		int2 neighbor = clamp(pixel + int2(x, y), int2(0), size - 1);
		float3 color = RGBToYCoCg(u_Current.Load(int3(neighbor, 0)).rgb);
		low = min(low, color);
		high = max(high, color);
		float neighborDepth = u_Depth.Load(int3(neighbor, 0)).r;
		if (neighborDepth > nearestDepth)
		{
			nearestDepth = neighborDepth;
			nearestPixel = neighbor;
		}
	}
}

float3 result = current;
if (u_Temporal.CurrentWeight < 1.0)
{
	// Nothing drawn in the neighborhood (the sky, which has no geometry): the camera's motion of its direction.
	float2 motion = nearestDepth > 0.0 ? u_Velocity.Load(int3(nearestPixel, 0)).rg : GetCameraMotion(uv, 0.0);
	float2 previousUV = uv - motion;
	// Outside the previous frame, or uncovered since (disocclusion rejection): the current frame alone.
	bool inside = all((previousUV >= float2(0.0))) && all((previousUV <= float2(1.0)));
	if (inside && !(u_Temporal.DisocclusionThreshold > 0.0 && IsDisoccluded(previousUV, nearestPixel, nearestDepth)))
	{
		// A still pixel reads its own texel; otherwise the filter reads the history between texels by `fraction`.
		float2 fraction = float2(0.0);
		float3 history = (all(motion == float2(0.0)) ? u_History.Load(int3(pixel, 0)).rgb : SampleHistory(previousUV, fraction)) * u_Temporal.HistoryScale;
		// The luminance weights' exposure: of exposed values.
		float exposure = u_Exposure[ST_EXPOSURE_MULTIPLIER] * u_Temporal.InversePreExposure;
		// The reactive mask's coverage: from variance clipping's fetches when it runs (negative: still to be found).
		float coverage = -1.0;
		if (u_Temporal.ClampMode == 1u)
			history = ClipHistoryToVariance(history, pixel, size, exposure, coverage);
		else
			history = YCoCgToRGB(clamp(RGBToYCoCg(history), low, high));
```

1. **Lines 207–224:** the loop visits the eight neighbours. It converts each colour to YCoCg and keeps the range; it also tracks the largest depth, since :term[reversed-Z]{id=reversed-z} makes the largest depth the nearest surface.
2. **Line 230:** the motion comes from the nearest surface's pixel, so an edge moves with its foreground. Where nothing was drawn, the sky uses the camera's motion for its direction.
3. **Lines 231–234:** the pixel reads the history at its position minus the motion. Outside the previous frame, the pixel takes the new frame alone.
4. **Lines 243–246:** one of two clamps runs; the next section shows them.

Taking the motion from the nearest surface matters at edges. Picture a pixel on the border between a moving ball and a still wall, which may show the wall in the new frame. With the wall's motion (none) it would read the history where the wall was, and the ball's edge would stay hard. With the ball's motion it reads where the ball's edge was. Either choice is right for one surface; the foreground choice keeps the edge that people see.

The history is read through a **Catmull-Rom filter**: a smooth curve through four samples that passes exactly through the middle two. Its weights can be negative, so its result is sharper than a plain bilinear read.

A bilinear read blends two neighbours, so each frame that reads the history between pixels blurs it a little more. The Catmull-Rom filter needs 16 reads in two axes. The shader makes do with nine bilinear reads: the two middle weights are both positive, so one read between them gets both.

At the half-way position $f = 0.5$ the four weights, by hand, are −0.0625, 0.5625, 0.5625 and −0.0625; they sum to 1. The two middle ones merge into one read of weight 1.125 placed half-way between the two pixels, so one hardware-filtered read gets both. In two axes, that is a 3 by 3 grid of reads.

```slang src="Strata/shaders/PostProcess/TAA.comp.slang#L165-L190"
float3 SampleHistory(float2 uv, out float2 f)
{
	float2 position = uv * u_Frame.ViewportSize.xy;
	float2 center = floor(position - 0.5) + 0.5; // The texel center at or before the position
	f = position - center;
	float2 weight0 = f * (-0.5 + f * (1.0 - 0.5 * f));
	float2 weight1 = 1.0 + f * f * (-2.5 + 1.5 * f);
	float2 weight2 = f * (0.5 + f * (2.0 - 1.5 * f));
	float2 weight3 = f * f * (-0.5 + 0.5 * f);
	float2 weight12 = weight1 + weight2;
	float2 position0 = center - 1.0;
	float2 position12 = center + weight2 / weight12;
	float2 position3 = center + 2.0;

	float3 color = SampleHistoryBilinear(float2(position0.x, position0.y)) * (weight0.x * weight0.y)
		+ SampleHistoryBilinear(float2(position12.x, position0.y)) * (weight12.x * weight0.y)
		+ SampleHistoryBilinear(float2(position3.x, position0.y)) * (weight3.x * weight0.y)
		+ SampleHistoryBilinear(float2(position0.x, position12.y)) * (weight0.x * weight12.y)
		+ SampleHistoryBilinear(float2(position12.x, position12.y)) * (weight12.x * weight12.y)
		+ SampleHistoryBilinear(float2(position3.x, position12.y)) * (weight3.x * weight12.y)
		+ SampleHistoryBilinear(float2(position0.x, position3.y)) * (weight0.x * weight3.y)
		+ SampleHistoryBilinear(float2(position12.x, position3.y)) * (weight12.x * weight3.y)
		+ SampleHistoryBilinear(float2(position3.x, position3.y)) * (weight3.x * weight3.y);
	// The filter's negative lobes may undershoot next to an edge.
	return max(color, float3(0.0));
}
```

1. **Lines 168–169:** the filter works from the pixel centre at or before the position and returns the offset `f` past it; the resolve uses `f` again as the resampling term's input.
2. **Lines 170–173:** the four weights per axis are the Catmull-Rom curves; for `f = 0.5` they give the numbers above.
3. **Lines 174–176:** the middle two merge into `weight12` and a position shifted by their ratio; the outer weights stay.
4. **Line 189:** the negative lobes can pull a value below zero next to an edge, so the result is never below 0.

```mermaid caption="Nine reads for sixteen weights. Along each axis the two middle pixels share one read placed by their weight ratio, and the outer two keep a read each. The negative weights sit on the outer reads." alt="Four pixels of one axis with their weights. The two middle pixels join into one read of weight 1.125, and the outer two, of weight minus 0.0625, keep a read each. The three reads are summed and kept at 0 or above."
flowchart TB
	subgraph Axis[One axis]
		P0[Pixel 0: weight -0.0625] --> R0[Read 0]
		P1[Pixel 1: 0.5625] --> R12[Read at the ratio: 1.125]
		P2[Pixel 2: 0.5625] --> R12
		P3[Pixel 3: -0.0625] --> R3[Read 3]
	end
	R0 --> S[Sum, then the maximum with 0]
	R12 --> S
	R3 --> S
```

A still pixel (motion exactly 0) skips the filter and reads its own history pixel: the filter at weight offset 0 is the identity, and the read costs less.

## The resolve: clamping the history

What does the history hold of a surface that has moved away? Its old colour, which has no place in the new frame. The clamp rejects it by limiting the history to the colours the new frame shows around the pixel. The shader works in **YCoCg**, a colour space that splits a colour into its brightness (Y) and two colour differences (`Co`, orange against blue, and `Cg`, green against purple). Limiting each of the three components apart in YCoCg separates brightness from hue better than limiting red, green and blue, so a clamp moves a colour's brightness without turning its hue.

The **neighborhood clamp** is the range version: each component of the history goes to the lowest and highest value of the 3 by 3 pixels. Original, the softer of the two presets that the table near the end of the page lists, uses it, and so does the toy. It has a weak spot. A bright glint among dark pixels widens the range, and the old copy of a dark object may sit inside that range, so a faint trail survives beside glints.

**Variance clipping** is tighter. It computes the mean and the :term[standard deviation]{id=standard-deviation} of the 3 by 3 colours and builds a box of half-width `ClipWidth` deviations around the mean, never wider than the range. Where the history lies outside the box it is not clamped per component but moved along the line toward the mean until it touches the box, so its hue relative to the mean is kept. Sharp, the default preset, uses 1.25 deviations.

A worked example with eight pixels of brightness 0.1 and one glint of 1.0. The sum is 1.8, so the mean is 0.2. The mean of the squares is $(8 \times 0.01 + 1)/9 = 0.12$, so the variance is $0.12 - 0.2^2 = 0.08$ and the deviation is about 0.283. The box reaches $0.2 + 1.25 \times 0.283 = 0.554$ up, below the range's 1.0. An old copy of the glint with the value 1.0 passes the range clamp untouched and is pulled to 0.554 by the clip, as the figure shows on one brightness axis.

::figure{id=taa-clamp-clip-axis}

The shader below does this for one pixel; watch the sums on lines 100 to 106 and the line to the box on lines 116 to 121.

```slang src="Strata/shaders/PostProcess/TAA.comp.slang#L89-L123"
float3 ClipHistoryToVariance(float3 history, int2 pixel, int2 size, float exposure, out float coverage)
{
	float3 sum = float3(0.0);
	float3 squares = float3(0.0);
	float3 low = float3(3.0e38);
	float3 high = float3(-3.0e38);
	coverage = 0.0;
	for (int y = -1; y <= 1; y++)
	{
		for (int x = -1; x <= 1; x++)
		{
			float4 texel = u_Current.Load(int3(clamp(pixel + int2(x, y), int2(0), size - 1), 0));
			coverage = max(coverage, 1.0 - texel.a);
			float3 compressed = CompressColor(texel.rgb, exposure);
			sum += compressed;
			squares += compressed * compressed;
			low = min(low, compressed);
			high = max(high, compressed);
		}
	}
	float3 mean = sum / 9.0;
	float3 deviation = sqrt(max(squares / 9.0 - mean * mean, float3(0.0)));
	float3 boxLow = max(mean - u_Temporal.ClipWidth * deviation, low);
	float3 boxHigh = min(mean + u_Temporal.ClipWidth * deviation, high);
	float3 offset = CompressColor(history, exposure) - mean;
	// Compared with 0, not an epsilon: compressed colors scale exactly with a power-of-two pre-exposure, so the same
	// components are chosen at every pre-exposure.
	float fraction = 1.0;
	for (int component = 0; component < 3; component++)
	{
		if (offset[component] != 0.0)
			fraction = min(fraction, ((offset[component] > 0.0 ? boxHigh[component] : boxLow[component]) - mean[component]) / offset[component]);
	}
	return ExpandColor(mean + max(fraction, 0.0) * offset, exposure);
}
```

1. **Lines 100–106:** the loop sums the colours and their squares and keeps the range, once per pixel of the neighbourhood, all after `CompressColor`.
2. **Lines 109–112:** the mean and deviation give the box, and `max` and `min` keep it inside the range.
3. **Lines 116–121:** each component finds how far along the offset it can go before it leaves the box; the smallest fraction wins, which keeps the history on its line to the mean.
4. **Line 122:** the colour is expanded back from the compressed space.

The compression matters. `CompressColor` divides each colour by one plus its exposed luminance before converting to YCoCg, so a very bright texel does not stretch the deviation as it would in linear values. The comparison to 0 on line 119 is exact, not an :term[epsilon]{id=tolerance}: compressed colours scale exactly with the pre-exposure, so every pre-exposure picks the same components. The pre-exposure is a power-of-two brightness scale that keeps bright values inside the half-float range. The history is also multiplied by the ratio of the frame's pre-exposure to the history's (`HistoryScale`), as the [pre-exposure page](../image/pre-exposure.md) explains.

The diagram shows the clip as a picture of two components. The history is outside the box; the line to the mean meets the box edge, and the history lands there.

```mermaid caption="Variance clipping in two colour components. The history lies outside the box; its line to the mean meets the box edge, and the clip puts the history at that point." alt="A flow in which the history, outside the box, moves along its line to the mean and stops at the box edge. The mean and the box, set by the deviation, meet at that edge."
flowchart LR
	H[History outside the box] -->|move along the line to the mean| E[Stops at the box edge]
	M[Mean of the 3 by 3 pixels] --- E
	B[Box: mean plus or minus width times deviation, inside the range] --- E
```

## The resolve: the blend and its weights

With the history clamped, the new frame's weight is the largest of four values. The first is `CurrentWeight`, 1 over the frames in the history, which averages the first frames evenly. The second is `MinWeight`, 1 over `HistoryFrames`, the floor after that. The third is the motion term: the motion's length in pixels times `MotionResponse`, up to `MaxMotionWeight`. The fourth is the resampling term, explained below.

```slang src="Strata/shaders/PostProcess/TAA.comp.slang#L247-L272"
			float motionPixels = length(motion * u_Frame.ViewportSize.xy);
			float weight = max(max(u_Temporal.CurrentWeight, u_Temporal.MinWeight), min(motionPixels * u_Temporal.MotionWeightScale, u_Temporal.MaxMotionWeight));
			// Resampling: the filter softens what it reads between texels (most halfway, nothing at a texel), and a slow pan
			// reads every frame so; the current frame weighs more there, up to ResampleWeight halfway. Integer motion reads
			// texels and adds nothing.
			if (u_Temporal.ResampleWeight > 0.0)
			{
				float2 between = fraction * (1.0 - fraction);
				weight = max(weight, u_Temporal.ResampleWeight * 4.0 * max(between.x, between.y));
			}
			// Transparent surfaces (no motion of their own): the current frame weighs at least TransparentWeight where one covers
			// the neighborhood, a surface of alpha 0.5 or more fully (dilated over its aliased edges). Never a bypass: they would
			// alias and shimmer with the jitter.
			if (u_Temporal.TransparentWeight > 0.0)
			{
				if (coverage < 0.0)
					coverage = GetTransparentCoverage(pixel, size);
				weight = max(weight, min(1.0, 2.0 * coverage) * u_Temporal.TransparentWeight);
			}
			float currentWeight = weight / (1.0 + Luminance(current) * exposure);
			float historyWeight = (1.0 - weight) / (1.0 + Luminance(max(history, float3(0.0))) * exposure);
			result = (current * currentWeight + history * historyWeight) / max(currentWeight + historyWeight, 1e-6);
		}
	}
	o_History[pixel] = float4(SanitizeHDR(result), GetViewDistance(uv, depth));
}
```

1. **Line 248:** the weight is the largest of the even-average weight, the floor and the motion term.
2. **Lines 252–256:** the resampling term lifts the weight where the history was read between pixels.
3. **Lines 260–265:** the reactive mask raises the weight under transparent surfaces; the next section explains it.
4. **Lines 266–271:** each colour is divided by one plus its exposed luminance and the two are blended. The alpha is the pixel's view distance, the history's second job.

Take Sharp with 8 pixels of motion: $8 \times 0.0625 = 0.5$, so the new frame weighs 0.5 and the history 0.5. A surface that moves 8 pixels a frame keeps half of each frame. A still pixel keeps $1/8$.

The **resampling blur** is the softness the filter adds. A slow pan reads the history between pixels in every frame, and each read blurs a little more, because the blurred result is the next frame's history. The term counters this with a weight that peaks halfway between pixels.

The weight is `ResampleWeight` × 4 × the larger of $f(1-f)$ in the two axes, where $f$ is the read's offset past a pixel centre. At the half-way point the product is $0.25 \times 4 \times 0.25 = 0.25$. At $f = 0.25$ it is $0.1875$, and at $f = 0$ it is zero. A whole pixel of motion reads pixel centres and gains no blur.

The Manual measures the effect on a slow pan over fine texture: Original keeps about half the detail, Sharp about three quarters. The figure compares the two presets at one moment of the Showcase's camera flight over the fine grain of its wet apron.

::compare{id=taa-presets-slow-pan}

The luminance weights deserve a number. With exposed values, a new frame of luminance 0.2 and a history of 1.0, at a weight of 1/8: the new frame's share is $0.125/1.2 = 0.104$, the history's $0.875/2 = 0.4375$. The result is $(0.2 \times 0.104 + 1.0 \times 0.4375)/0.5417 = 0.846$ instead of the plain $0.9$. The weights favour dark values, so a bright sample that appears in one frame, as the jitter moves a glint in and out of a pixel, does not flicker the pixel as strongly. The alpha line stores the :term[signed distance]{id=signed-distance} along the camera's forward axis; the next section reads it.

## Transparent surfaces and uncovered surfaces

Blended transparent surfaces have no motion of their own: the velocity target holds what lies behind the glass. So the history follows the background and the glass drags its image behind it. The **reactive mask** is the rule that does not depend on motion. Where a transparent surface covers the pixel's 3 by 3 neighbourhood, the new frame weighs at least `TransparentWeight`.

Coverage is the largest of one minus alpha over the nine pixels. That is why the HDR alpha convention is load-bearing. The clear, the opaque surfaces and the sky write alpha 1; each blended draw multiplies it by one minus its own alpha, so after the transparent pass alpha is the transmittance. A surface of alpha 0.5 or more counts as fully covering, and the mask spreads over edges that show stair-steps. The mask never bypasses the history, since a weight of 1 would show stair-steps and shimmer with the jitter.

Glass drawn without blending writes its own depth and velocity, so it needs no mask.

A moving object uncovers the surface behind it. A **disocclusion** is the moment when a pixel shows a surface that was hidden in the previous frame, so the history of the pixel belongs to another, nearer surface. The clamp helps where colours differ. It fails where they match, for example a dark object leaving a dark wall. Disocclusion rejection compares depths instead.

```slang src="Strata/shaders/PostProcess/TAA.comp.slang#L130-L141"
bool IsDisoccluded(float2 previousUV, int2 nearestPixel, float nearestDepth)
{
	float expected = c_SkyDistance;
	if (nearestDepth > 0.0)
	{
		float2 nearestUV = (float2(nearestPixel) + 0.5) * u_Frame.ViewportSize.zw;
		float4 point = mul(u_Frame.InverseViewProjection, float4(UVToNDC(nearestUV), nearestDepth, 1.0));
		expected = min(dot(point.xyz / point.w, u_Temporal.PreviousForward.xyz) + u_Temporal.PreviousDepthOffset, c_SkyDistance);
	}
	float4 stored = u_History.GatherAlpha(u_LinearClampSampler, previousUV);
	float farthest = max(max(stored.x, stored.y), max(stored.z, stored.w));
	return farthest < expected - u_Temporal.DisocclusionThreshold * max(abs(expected), u_Temporal.PreviousForward.w);
```

1. **Lines 132–138:** the pixel's surface distance is moved to the previous camera's forward axis, the sky counting as the largest distance.
2. **Lines 139–140:** `GatherAlpha` returns the four stored distances around the previous position; the test takes the farthest of them.
3. **Line 141:** the pixel counts as uncovered when even the farthest stored distance is shorter than expected by more than the threshold's share.

Numbers: a wall at 10 m and a threshold of 0.05 give $10 - 0.05 \times 10 = 9.5$. A stored distance of 8 m (a hand that stood in front) is below 9.5, so the history is dropped and the pixel takes the new frame. A stored 9.8 m is above it, so the history stays. The test is one-sided and uses the farthest of four, so jitter at a still edge and the depth slope of a grazing floor do not trigger it. The distance lives in the alpha of the history texture, which is why that texture holds four channels.

```mermaid caption="The disocclusion test. The surface's expected distance is read in the previous camera's frame; the farthest of the four stored distances is compared with it, less the threshold's share." alt="A flow from the pixel's nearest surface to its expected distance, then to a comparison with the farthest of four stored distances. Two outcomes follow: the history is dropped when the stored distance is far shorter, and kept otherwise."
flowchart LR
	S[Nearest surface of the 3 by 3] --> X[Expected distance along the previous forward axis]
	G[Four stored distances around the previous position] --> F[Farthest of the four]
	X --> C{Farthest below expected minus the threshold share?}
	F --> C
	C -->|yes| D[Take the new frame alone]
	C -->|no| K[Keep the history]
```

## Sharpening the displayed image

Averaging softens the image. **Sharpening** puts back some crispness, after the resolve and only on what the player sees. The history is never sharpened: a sharpened history would be sharpened again next frame, and the overshoot would grow into halos.

```slang src="Strata/shaders/PostProcess/Tonemap.frag.slang#L95-L119"
float3 Sharpen(float3 color, float sharpening)
{
	int2 pixel = int2(st_FragCoord.xy); // The viewport starts at 0, 0: fragments line up with the scene color's texels
	int2 last = TextureSize(u_SceneColor, 0) - 1;
	float neighbors[4] = { Luminance(ExposeSceneColor(u_SceneColor.Load(int3(clamp(pixel + int2(-1, 0), int2(0), last), 0)).rgb)), Luminance(ExposeSceneColor(u_SceneColor.Load(int3(clamp(pixel + int2(1, 0), int2(0), last), 0)).rgb)), Luminance(ExposeSceneColor(u_SceneColor.Load(int3(clamp(pixel + int2(0, -1), int2(0), last), 0)).rgb)), Luminance(ExposeSceneColor(u_SceneColor.Load(int3(clamp(pixel + int2(0, 1), int2(0), last), 0)).rgb)) };
	float centerLuminance = Luminance(color);
	float center = centerLuminance / (1.0 + centerLuminance);
	float low = center;
	float high = center;
	float mean = 0.0;
	for (int index = 0; index < 4; index++)
	{
		float neighbor = neighbors[index] / (1.0 + neighbors[index]);
		low = min(low, neighbor);
		high = max(high, neighbor);
		mean += 0.25 * neighbor;
	}
	float range = high - low;
	float amount = sharpening * pow(1.0 - range, c_SharpeningContrastExponent);
	float sharpened = clamp(center + amount * (center - mean), max(low - amount * range, 0.0), min(high + amount * range, 0.5 * (1.0 + high)));
	if (centerLuminance <= 0.0)
		return color;
	// Compressed luminance this close to 1 comes from the largest exposed values only: kept finite.
	return color * ((sharpened / max(1.0 - sharpened, 1e-7)) / centerLuminance);
}
```

1. **Lines 99–111:** the pixel and its four neighbours go through luminance compressed as L over 1 + L, and their range and mean are taken.
2. **Line 113:** the amount falls steeply with the range, as one minus the range to the power 8: strong edges get almost nothing.
3. **Line 114:** the sharpened value is bounded by the range widened by the amount, and by a limit below 1.
4. **Lines 115–118:** only luminance changes, so edges get no colour fringes, and black stays black.

Sharp's amount is 0.5. With a range of 0.5 the amount is $0.5 \times (1 - 0.5)^8 \approx 0.002$, so a strong edge is left alone. With a range of 0.1 it is $0.5 \times 0.9^8 \approx 0.215$, so fine texture sharpens.

The tone mapping skips the pixels that depth of field or motion blur blurred. It reads the blur mask they write in the image's alpha ([the motion blur page](../image/motion-blur.md)), because sharpening a blur would cut a streak into steps. The setting is the field `Sharpening` of `RenderData::TonemapConstants`, used only on frames the TAA resolved; 0 disables it. The Developer Guide writes `TonemapParameters::Sharpening`, but no such type exists in the code.

## The presets as tables

The look is a table of ten values. `TemporalAntiAliasingSettings` holds them, `c_TAAOriginalSettings` and `c_TAASharpSettings` are the two presets, and the component's `TAAPreset` chooses Sharp (the default), Original or Custom, whose values come from the component's own fields.

| Setting | Original | Sharp | What it does |
| --- | --- | --- | --- |
| `History Frames` | 8 | 8 | The new frame weighs at least 1 over this number |
| `Motion Response` | 0.03125 | 0.0625 | Weight the new frame gains per pixel of motion |
| `Max Motion Weight` | 0.5 | 0.5 | The most that the motion term can add |
| `Resample Weight` | 0 | 0.25 | Least weight where the history is read between pixels |
| `History Clamp` | Range | Tight (variance) | Which of the two limits runs |
| `Clip Width` | not used | 1.25 | Half width of the box, in deviations |
| `Transparent Weight` | 0 | 0.5 | Least weight under blended transparent surfaces |
| `Disocclusion Rejection` | off | on | Drops the history where a surface was uncovered |
| `Disocclusion Threshold` | not used | 0.05 | How much nearer counts as covered, as a share of the distance |
| `Sharpening` | 0 | 0.5 | Amount of the sharpening of the displayed image |

A setting that the chosen modes do not read is 0 in a **normalized** table: `NormalizeTemporalAntiAliasingSettings` clamps each value to its range and zeroes the unused ones. Two looks that differ only in unused fields then compare equal, and the shader's :term[push constants]{id=push-constants} are equal :term[bytes]{id=byte}. Original resolves exactly as Custom with Original's values; the test `Original resolves exactly as Custom with Original's values, whatever Custom's unused fields hold` checks it. Choosing Custom starts from the look in effect, unless the fields already hold your own tuning: then it keeps them.

## What it cannot do

The Manual documents three limits, and each follows from a rule above.

- A surface that recedes faster than the disocclusion threshold each frame looks uncovered, so it loses its history while it recedes. With 0.05 at 10 m, that is about half a metre a frame.
- A band that a moving object uncovers starts from one frame, then averages in, and stays less smooth for about 17 frames. A rough check: 17 frames of weight 1/8 hold $1 - (7/8)^{17} \approx 0.90$ of the image.
- Original keeps about half of the fine texture in slow pans; Sharp keeps about three quarters. Where slow camera motion over detailed textures matters, prefer Sharp or a higher **Resample Weight**.

TAA also needs the motion vectors: a frame without them is drawn with FXAA.

:::example[A pixel through one frame]
Trace a pixel through one frame. Take a pixel at the edge of a ball under Sharp, with the ball moving 4 pixels to the right. The pixel's 3 by 3 neighbourhood holds the ball's depth, so the motion is the ball's: (4, 0) pixels. The history is read 4 pixels to the left, an :term[integer]{id=integer} offset with $f = 0$, so the resampling term is 0.

The variance clip pulls the old value into the box. The stored distances there are the ball's, so disocclusion finds nothing uncovered. The weight is the largest of 1/8 and $4 \times 0.0625 = 0.25$, so the new frame weighs 0.25. The result is blended with luminance weights, stored with the ball's distance in alpha, and sharpened on its way to the screen.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Several samples per pixel (:term[MSAA]{id=msaa}) | Many forward renderers | Sharp edges without history or trails | Costs per sample in memory and :term[bandwidth]{id=bandwidth}; does not smooth shader noise or thin lines inside surfaces |
| Single-frame filters (FXAA, morphological) | Most engines as a fallback | No history, no trails, cheap | Softer, and flickers on thin lines; they stay available as Strata's other choices |
| Temporal super resolution | Unreal Engine; the graphics vendors' libraries | Fewer pixels drawn for the same shown size | Policy: the image is drawn at the size it is shown; the vendors' parts need their code |
| Range clamp only | Early temporal designs | Simpler, fewer reads | Faint trails beside glints (Original keeps it) |
| Transparent surfaces drawn after the resolve | Several engines | No ghosts of glass | Their edges show stair-steps; Strata uses the reactive mask instead |

## How it is tested

The suite `GPU.SceneRenderer.TAA` draws small scenes on the :term[graphics processing unit]{id=gpu} (GPU) and measures the result. Its tests check, among other things:

- The eight jitter phases differ and cover the pixel, and culling, levels of detail and the cached cascades follow the camera.
- A still edge equals the mean of its eight jittered frames, then stays near it.
- The history starts again on cuts, other scenes, size changes, a skipped device frame and `ResetHistory`, and slow frames do not restart it.
- A moving object leaves no trail beyond two pixels once it stops, and variance clipping leaves at most half of the range clamp's trail where glints widen the neighbourhood.
- Disocclusion rejection leaves no ghost on the wall or the sky that a box uncovers.
- Both render paths resolve the same image over sixteen frames of a moving scene.

Run it on a machine with a GPU: `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.TAA`. The suite `Renderer.TAASharpening` needs no GPU. It checks that Sharp's amount overshoots a black-to-white edge by at most 2 % of its range, and 5 % at the amount 1. It also checks that texture detail of 3 to 6 pixels gains at least 8 % of its amplitude. The flicker metrics that several of these tests use are taught in [test kinds](../engineering/test-kinds.md).

## Changing it safely

Extension points: a new setting is a field of `TemporalAntiAliasingSettings`, its range constants, a property of the component, a push constant, a :term[normalization]{id=normalization} line, and a preset value; the shader reads it behind a branch. A new effect that needs noise reads the golden-ratio turn from the frame constants, never from its own state.

The rules that apply, each with its reason:

- Jitter only the frame's copy of the camera, or culling and levels of detail would change every frame.
- Keep the history in frames, not time, so slow frames keep it and the weights stay right.
- Keep sharpening off the history, or the overshoot grows into halos.
- Keep the HDR alpha convention, or the reactive mask reads nonsense.
- Make every new effect look right without TAA; the design decision above is the reason.

Check a change with `GPU.SceneRenderer.TAA` and `Renderer.TAASharpening`, and read it against the pre-exposure scaling: the history's scale and the luminance weights both depend on it.

## Summary

- The jitter moves only the frame's copy of the projection, in eight Halton phases, so culling, levels of detail and the cascades follow the plain camera.
- The resolve reads the history along the nearest surface's motion through a Catmull-Rom filter, limits it by a clamp or a variance clip, and blends it with luminance weights.
- The clamp, the clip, the reactive mask and the disocclusion test each stop one artifact: wrong colours, hue-keeping trails, transparent ghosts and uncovered surfaces.
- The history counts frames, belongs to the renderer, and restarts on cuts, resets, size changes and scene changes; single images settle for eight frames or use FXAA; TAA keeps limits the Manual names.
- Settings live in preset tables, normalized so equal looks compare equal; each changes one of the weights or rules above.

## Check yourself

1. Why does the jitter go into a copy of the projection and not into the camera?

   :::answer{tests="jitter-copy"}
   The camera feeds culling, levels of detail and the cascade cache's key. A jittered camera would change them every frame, so objects would pop and the cascades would be drawn again. The copy changes only what the shaders draw with.
   :::

2. A pixel's samples over four frames read 1, 0, 0, 1. With weights 1/n, what does it show after frame 4?

   :::answer{tests="resolve-path"}
   Frame 1: 1. Frame 2: half of 1 is 0.5. Frame 3: two thirds of 0.5 is 0.333. Frame 4: three quarters of 0.333 plus a quarter of 1 is 0.5. That is the mean of the four samples.
   :::

3. Which rule stops each artifact: a dark object's trail over a bright wall, the drag of a sheet of glass, the ghost behind a moving hand?

   :::answer{tests="artifact-rules"}
   The clamp or clip stops the trail, since its colour lies outside the neighbours' colours. The reactive mask stops the drag of the glass, since the glass has no motion. Disocclusion rejection stops the hand's ghost, since depths differ even where colours match.
   :::

4. A slow frame takes 100 ms. Does the history restart? And a size change?

   :::answer{tests="history-life"}
   No for the slow frame: the history counts frames, not time. Yes for the size change: it frees the textures, so the counter starts at 1.
   :::

5. You raise **Resample Weight** from 0.25 to 0.5. What changes in a slow pan?

   :::answer{tests="change-resolve"}
   Texture stays crisper, since the new frame weighs more halfway between pixels. Edges get less anti-aliasing while they move, and at 0.5 their stair-steps show again.
   :::

## Exercises

1. **Basic.** Start Custom from Sharp and raise **Resample Weight** until the stair-steps of an edge return in a slow pan. Find the line of the resolve that does it.

   :::answer[Worked solution]{tests="change-resolve"}
   Choose Custom in the Post Process inspector, then raise **Resample Weight** while the camera pans slowly. At about 0.5 the edges show steps. The line is `weight = max(weight, u_Temporal.ResampleWeight * 4.0 * max(between.x, between.y));` in `Strata/shaders/PostProcess/TAA.comp.slang`: a weight near 0.5 halfway between pixels leaves little history to smooth an edge.
   :::

2. **Medium.** Trace it yourself: find where the CPU writes the golden-ratio turn, then every shader that reads it. Say what each looks like without TAA.

   :::answer[Worked solution]{tests="jitter-copy,history-life"}
   `SceneRenderer.cpp` writes `noiseTurn` into the third component of `TemporalParams` (lines 3250 and 3251). A search for `TemporalParams.z` in `Strata/shaders` finds one reader, the screen-space reflections (`ScreenSpaceReflections.comp.slang`), and a comment in `Strata/shaders/Include/Common.slang` that names it. Without TAA the turn stays 0, so the reflections' start noise stands still. The reflections are the rule's named exception, since Medium's Checkerboard needs the history. The shadow filters are not in the list: the sun's uses a fixed noise tile, and the point and spot lights' a fixed noise per pixel.
   :::

3. **Hard.** On a temporary branch, turn the clamp off in the resolve and watch a moving object. Then write a variance clip of your own for the toy's three neighbours and compare it with `ClipHistoryToVariance`.

   :::answer[Worked solution]{tests="artifact-rules,resolve-path"}
   Without the clamp, a moving object leaves a trail as long as the history holds it: the toy's `moving, no motion` row. The clip below follows the shader: mean and deviation, a box never wider than the range, and a move along the line to the mean.

   ```cpp sketch="image-taa-clip.cpp"
   // Variance clipping in one dimension: a box around the mean of three neighbours; the history moves toward the mean until inside.
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   float ClipToVariance(float history, const float (&neighbours)[3], float width)
   {
   	float sum = 0.0f;
   	float squares = 0.0f;
   	float low = neighbours[0];
   	float high = neighbours[0];
   	for (const float value : neighbours)
   	{
   		sum += value;
   		squares += value * value;
   		low = std::min(low, value);
   		high = std::max(high, value);
   	}
   	const float mean = sum / 3.0f;
   	const float deviation = std::sqrt(std::max(squares / 3.0f - mean * mean, 0.0f));
   	// The box is never wider than the plain range of the neighbours.
   	const float boxLow = std::max(mean - width * deviation, low);
   	const float boxHigh = std::min(mean + width * deviation, high);
   	const float offset = history - mean;
   	if (offset == 0.0f)
   		return mean;
   	const float limit = (offset > 0.0f ? boxHigh : boxLow) - mean;
   	return mean + std::min(1.0f, limit / offset) * offset;
   }

   int main()
   {
   	const float smooth[3] = { 0.4f, 0.5f, 0.6f };
   	const float glint[3] = { 0.0f, 0.0f, 1.0f };
   	std::printf("smooth, history 0.55: %.3f\n", ClipToVariance(0.55f, smooth, 1.25f));
   	std::printf("smooth, history 1.00: %.3f\n", ClipToVariance(1.0f, smooth, 1.25f));
   	std::printf("smooth, history 0.00: %.3f\n", ClipToVariance(0.0f, smooth, 1.25f));
   	std::printf("glint,  history 0.95: %.3f\n", ClipToVariance(0.95f, glint, 1.25f));
   	std::printf("glint,  history 0.95, width 0.5: %.3f\n", ClipToVariance(0.95f, glint, 0.5f));
   	return 0;
   }
   ```

   ```text output-of="image-taa-clip.cpp"
   smooth, history 0.55: 0.550
   smooth, history 1.00: 0.600
   smooth, history 0.00: 0.400
   glint,  history 0.95: 0.923
   glint,  history 0.95, width 0.5: 0.569
   ```

   1. **Line 20:** the deviation is the square root of the mean of the squares minus the square of the mean.
   2. **Lines 22–23:** the box is the mean plus or minus width times deviation, kept inside the range.
   3. **Lines 27–28:** the fraction of the way to the box edge is at most 1, so a history inside the box stays.

   The first row stays inside. The next two land on the box edge, 0.6 and 0.4, where the range limits the box. The glint's box reaches 0.923 at width 1.25 and only 0.569 at width 0.5, and the history moves along the line to the mean until it fits. The shader does the same for each of three components and takes the smallest fraction.
   :::

## Where it lives in Strata

- Jitter and history rules: `SceneRenderer::GetTemporalJitter` and the frame setup in `Strata/src/Strata/Renderer/SceneRenderer.cpp`; the phase count is `c_TemporalJitterPhases`.
- The resolve: `Strata/shaders/PostProcess/TAA.comp.slang`; sharpening: `Strata/shaders/PostProcess/Tonemap.frag.slang`.
- Presets and settings: `Strata/src/Strata/Renderer/RendererComponents.h` and `RendererComponents.cpp`.
- Tests: `GPU.SceneRenderer.TAA`, `Renderer.TAASharpening`.
- Settings: the Post Process component's TAA Preset and its settings.

## Further reading

- Brian Karis, "High Quality Temporal Supersampling" (SIGGRAPH 2014): the clamp and the first temporal designs in a major engine. Intermediate.
- Marco Salvi, "An Excursion in Temporal Supersampling" (GDC 2016): variance clipping. Advanced.
- Lasse Jon Fuglsang Pedersen, "Temporal Reprojection Anti-Aliasing in INSIDE" (GDC 2016): reprojection, clamping and their artifacts. Intermediate.
- Strata's anti-aliasing manual, `Docs/Manual/AntiAliasing.md`: the presets, settings and limits for game makers. Beginner.
