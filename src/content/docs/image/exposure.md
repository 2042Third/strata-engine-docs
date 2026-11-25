---
id: image/exposure
title: "Exposure: camera, eye and meter"
description: "How Strata turns the light of the HDR image into one multiplier: set by hand in stops, or measured by a histogram that adapts like an eye."
kind: internals
size: L
tracks: [E]
needs: [gpu/compute, gpu/coordinates, light/measuring-light, image/why-post]
time: 75
learn:
  - id: camera-model
    text: compute the EV100 a meter reads and the manual Exposure that puts a scene's average luminance at middle gray
  - id: histogram-meter
    text: explain how a histogram, a weight map and a percentile window turn a frame into one number
  - id: adaptation
    text: explain why adaptation uses a fraction of one minus an exponential and why light and dark have separate speeds
  - id: key
    text: predict the exposure key's stops for a scene and say why the key only darkens
  - id: trace-mode
    text: trace a metering mode from the component to the shader and name what a new mode changes
since: 0.3.0
status: final
---

An image of :term[high dynamic range]{id=high-dynamic-range} (HDR) holds real light: a wall in the sun is thousands of times brighter than a lamp-lit corner, and no screen shows both. Exposure is the step that chooses which part of that range the screen will show. It reduces to one number, the multiplier M, which the :term[tone mapping]{id=tone-mapping-image} applies to every pixel. You can set M by hand, in stops, or let Strata measure the frame and adapt M over time, as a camera's meter or an eye does. The page covers both and the passes between them, and it omits the light units, the tone curve that follows and the pre-exposure that the metered value chooses.

## The problem and how engines solve it

Start from a photograph. A camera collects light for a short time, and the film or sensor can record only a limited range between black and white. Too much light and everything turns white. Too little and everything turns black. **Exposure** is the amount of light that reaches the sensor, and you change it with the opening of the lens and the time it stays open.

Photographers count exposure in stops: one stop doubles or halves the light. Closing the lens opening by one stop, or halving the time, halves the exposure. Because stops are powers of two, the standard measure is a :term[logarithm]{id=logarithm}: $V = \log_2 (N^2 / t)$.

$$V = \log_2 \frac{N^2}{t}$$

In the formula, $V$ is the exposure value, in stops, $N$ is the lens opening written as an f-number, and $t$ is the open time, in seconds. Take f/16 and 0.01 s: $N^2$ is 256, divided by $t$ gives 25,600, and $\log_2$ of that is about 14.6. A larger $V$ means less light reaches the sensor. The same value is reached by many pairs of opening and time, which is why a camera can trade one for the other.

One more factor remains: the sensor's sensitivity. Photographers fix it at 100 and write the value as **EV100**: the exposure value that a scene needs at a sensor sensitivity of 100. A bright scene needs a high exposure value at sensitivity 100 (EV100), and a dim one a low EV100. The sunny sixteen rule says that on a clear day, f/16 and a time of one over the sensitivity give a good picture. Its EV100 is about 15.

A camera does not know the EV100 of a scene. It has a reflected-light meter, which measures the light that comes back from the scene and assumes the scene is average. The assumed average is **middle gray**: a surface that reflects 18 % of the light, about the average of many real scenes.

A **gray card** is a card of that gray that a photographer holds in the light to read it. A meter reads the card and says "this light is this bright", then sets the exposure so that the card comes out as a middle gray in the photo.

The meter's formula has a constant, $K = 12.5$, fixed by the makers of meters. With $L$ the average :term[luminance]{id=luminance}, in :term[nits]{id=lux}, a meter reads the following.

$$V_{100} = \log_2 \frac{100 L}{K}$$

Here $V_{100}$ is the EV100 and $L$ is the average luminance of the scene, in nits. The number 100 is the sensitivity, and $K$ is the constant. Because $100 / 12.5$ is 8, which is $2^3$, the formula reduces to $\log_2 L + 3$. A scene in full sun with an average luminance of 4,096 nits ($2^{12}$) reads EV100 15, the sunny sixteen again.

The camera is done. A game has the same problem, with a twist: its image is a table of numbers, not a chemical film. Engines choose among a few answers.

- Fixed exposure. The game maker picks one number. It is cheap and predictable, and it fails when the scene changes: a cave and a beach cannot share one number.
- Average of the log luminance. The engine halves the image again and again (a :term[mip chain]{id=mip-chain}, which gives a chain of smaller copies) until one pixel is left, taking the average of the logarithms. It is fast, but one bright lamp or a patch of sky moves the average as much as a large wall does, and it cannot weigh the center more than the edges.
- A histogram. The engine counts how many pixels fall into each of many brightness bins. Counting lets it ignore black, cut off the brightest and darkest shares, and weigh pixels by where they are. It costs a compute pass and a small shared buffer.
- A camera's settings. The game maker gives the opening, the time and the sensitivity, and the engine converts. It suits physical cameras and film pipelines, and it still needs the light in real units.

An eye does a fourth thing: it adapts. Walking out of a dark tunnel, you are blind for a moment, then the world dims to a comfortable level. Engines copy it with a smoothing step, so that the exposure moves toward the measured value over some time. Strata chose a histogram with weights, a percentile window and adaptation with separate speeds for brighter and darker scenes. A game maker who wants no automatic behavior sets the stops by hand, and the rest of the page builds the chosen model from numbers.

### Strata's model

Strata's model has no hidden factor. The scene's luminance $L$, in nits, is multiplied by M, and the tone mapping receives $L \cdot M$. By hand, $M = 2^{E}$, where $E$ is the `Exposure` property of the `PostProcessComponent`, in stops, registered between -16 and 16. A positive value brightens, a negative one darkens, and `Exposure` is the only exposure when `AutoExposure` is off. In the editor the component's name is **Post Process**.

Which $E$ puts a scene's average luminance at middle gray? You need $L \cdot 2^{E} = 0.18$, so $E = \log_2 (0.18 / L)$. Since $\log_2 0.18$ is about $-2.47$ and $\log_2 L = V_{100} - 3$, the result is $E = 0.53 - V_{100}$. Strata's guide rounds it to about $0.5 - V_{100}$. The sunny-sixteen scene with $V_{100}$ of 15 needs an `Exposure` of about -14.5, and an office at EV100 8 needs about -7.5.

One trap follows. The properties `AutoExposureMinEV` and `AutoExposureMaxEV` are named for the exposure value (EV), but they are the log2 of a luminance in nits, which is EV100 minus 3. So a limit of 16 means 65,536 nits, EV100 19. The names measure from a different zero than a photographer's EV100, and the page uses "EV100" only for the photographer's number.

:::note
Where does the default `Exposure` of 0 put a scene in the sun? A scene of 4,096 nits times $2^0$ is 4,096, far above the display's white of 1. The picture turns white, which is why the Basic 3D template meters automatically. The luminance view of [Measuring light](../light/measuring-light.md) shows such numbers in bands.
:::

::figure{id=exposure-sweep variant=minus16}

::figure{id=exposure-sweep variant=minus14}

::figure{id=exposure-sweep variant=minus12}

## The map

**Metering** is measuring a frame's light to choose the exposure, and it is the job of the passes below. Automatic exposure is two small compute passes, a buffer between them and a function of the :term[central processing unit]{id=processor} (CPU) that drives them. The CPU's `UpdateExposure` runs once per frame, after the :term[HDR]{id=high-dynamic-range} scene is drawn and before bloom and tone mapping. With manual exposure it only writes the buffer and stops.

```mermaid caption="The path of one frame's exposure: the scene color is counted into a histogram, one group reads the histogram into the exposure buffer, and the tone mapping reads the buffer." alt="A flow from the scene color through the histogram pass into a histogram buffer, then through the exposure pass into the exposure buffer, which feeds the tone map. The processor writes the parameters, and a copy of the buffer returns to it frames later."
flowchart LR
	A[SceneRenderer::UpdateExposure on the CPU] -->|parameters, clear| B[Histogram.comp, 16x16 groups]
	S[HDR scene color] --> B
	B --> H[(histogram, 256 counters)]
	H --> C[Exposure.comp, one group]
	C --> E[(exposure buffer, 4 floats)]
	E --> T[tone mapping]
	E -.->|readback, frames later| A
	A -->|manual: writes 2 to the power of Exposure| E
```

The exposure buffer holds four floats; three are used. Float 0 is the adapted log2 luminance, float 1 is the multiplier M that the tone mapping applies, and float 2 is the exposure key's stops, which a later section explains. The :term[readback]{id=readback} in the diagram brings the metered values back to the CPU a few frames later; the CPU uses them to choose the pre-exposure, which belongs to [Pre-exposure](pre-exposure.md) and stays outside this page.

The files are few. `Strata/shaders/Include/Exposure.slang` holds the bin math shared by both :term[shaders]{id=shader}. `Strata/shaders/PostProcess/Histogram.comp.slang` counts and `Strata/shaders/PostProcess/Exposure.comp.slang` reduces. `Strata/src/Strata/Renderer/SceneRendererPost.cpp` holds `UpdateExposure`, and `Strata/src/Strata/Renderer/PostProcessData.h` holds the constants both sides share. Everything runs on the :term[main thread's]{id=main-thread} :term[command list]{id=command-list}; the :term[graphics processing unit]{id=gpu} (GPU) does the counting and the CPU never reads the histogram.

## The contract

Callers of automatic exposure may assume the following, each with its reason.

- The multiplier is in float 1 of the exposure buffer, and the tone mapping reads it there, not from the CPU. The reason: the GPU computes it, and a CPU copy would arrive frames late.
- Black pixels do not count. A lit object on an empty black background must not be over-exposed to fill the frame.
- Adaptation takes time in seconds, not frames. The reason: a game at 30 :term[frames per second]{id=frame-rate} and one at 144 must adapt alike.
- A pause cannot cause a jump. The step's length is capped at 0.25 s, so a breakpoint or a minimized window does not make one huge step.
- The exposure key only darkens, and a scene without a directional light has no key.
- Tests and tools that compare exact colors turn automatic exposure off, or set the step's time themselves.

:::rule
:term[NVRHI]{id=nvrhi} places barriers only when :term[binding sets]{id=binding-set} change, and the two exposure dispatches share one set. Between them the code states the histogram's new use itself. The reason: without it, the second pass may read counts that are not final.
:::

## A toy version

The toy shows the job on the CPU, with the real constants. It builds a histogram of log2 luminance with 256 bins, takes the mean of the part between two percentiles, and smooths one step. It omits the weights, the key and the GPU.

:::question
Do I need to know C++ for the toy? It uses [variables and conditions](../basics/programming-1.md), [loops and functions](../basics/programming-2.md), [calls and references](../basics/programming-3.md), [lambdas](../basics/cpp-generic.md) and [constexpr](../basics/cpp-modern.md).
:::

A **histogram** is a table that counts how many values fall into each of a set of equal ranges, called bins. Here the bins are ranges of log2 luminance, so that every bin is the same number of stops wide. In the code, search for bin 0, which collects black, and for the mean, which uses only bins 1 to 255.

```cpp sketch="image-exposure-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

// A CPU version of automatic exposure: a histogram of log2 luminance, a mean inside a percentile window,
// and one step of smoothing. The numbers match Strata's: 256 bins over log2 [-12, 16], bin 0 for black.
constexpr int c_Bins = 256;
constexpr float c_MinLog2 = -12.0f;
constexpr float c_MaxLog2 = 16.0f;

int LuminanceToBin(float luminance)
{
	if (!(luminance > std::exp2(c_MinLog2)))
		return 0;
	float t = std::clamp((std::log2(luminance) - c_MinLog2) / (c_MaxLog2 - c_MinLog2), 0.0f, 1.0f);
	return 1 + static_cast<int>(t * static_cast<float>(c_Bins - 2));
}

float BinToLog2(int bin)
{
	return c_MinLog2 + (static_cast<float>(bin - 1) + 0.5f) / static_cast<float>(c_Bins - 2) * (c_MaxLog2 - c_MinLog2);
}

// The mean log2 luminance of the pixels between the two percentiles, black ignored.
float MeterLog2(const std::vector<float>& luminances, float lowShare, float highShare)
{
	std::vector<float> bins(c_Bins, 0.0f);
	for (float luminance : luminances)
		bins[LuminanceToBin(luminance)] += 1.0f;

	float total = 0.0f;
	for (int bin = 1; bin < c_Bins; bin++)
		total += bins[bin];

	float low = total * lowShare;
	float high = total * highShare;
	float accumulated = 0.0f;
	float sum = 0.0f;
	float weight = 0.0f;
	for (int bin = 1; bin < c_Bins; bin++)
	{
		float inside = std::max(std::min(accumulated + bins[bin], high) - std::max(accumulated, low), 0.0f);
		sum += inside * BinToLog2(bin);
		weight += inside;
		accumulated += bins[bin];
	}
	return weight > 0.0f ? sum / weight : 0.0f;
}

// One frame of smoothing: the same fraction of the way, however long the frames are.
float Adapt(float previous, float target, float speed, float seconds)
{
	return previous + (target - previous) * (1.0f - std::exp(-seconds * speed));
}

int main()
{
	// 10 black pixels, 60 at 4 nits, 20 at 16 nits and 10 of a lamp at 4096 nits.
	std::vector<float> pixels(10, 0.0f);
	pixels.insert(pixels.end(), 60, 4.0f);
	pixels.insert(pixels.end(), 20, 16.0f);
	pixels.insert(pixels.end(), 10, 4096.0f);

	float everything = MeterLog2(pixels, 0.0f, 1.0f);
	float windowed = MeterLog2(pixels, 0.1f, 0.9f);
	std::printf("mean of all lit pixels: %.2f, multiplier %.4f\n", everything, 0.18f / std::exp2(everything));
	std::printf("mean inside the window: %.2f, multiplier %.4f\n", windowed, 0.18f / std::exp2(windowed));

	float oneStep = Adapt(0.0f, windowed, 3.0f, 0.1f);
	float tenSteps = 0.0f;
	for (int step = 0; step < 10; step++)
		tenSteps = Adapt(tenSteps, windowed, 3.0f, 0.01f);
	std::printf("one step of 0.1 s: %.3f, ten steps of 0.01 s: %.3f\n", oneStep, tenSteps);
	return 0;
}
```

```text output-of="image-exposure-toy.cpp"
mean of all lit pixels: 3.60, multiplier 0.0149
mean inside the window: 2.74, multiplier 0.0269
one step of 0.1 s: 0.711, ten steps of 0.01 s: 0.711
```

1. **Line 14:** a reversed test, so black and :term[NaN]{id=nan} both go to bin 0.
2. **Lines 36–37:** the percentile shares become counts of pixels.
3. **Line 43:** the part of a bin that lies inside the window; zero when the bin is outside.
4. **Line 54:** the fraction of the gap closed in one step grows with the step's seconds.

The percentile window is the idea to read in `MeterLog2`. A **percentile window** is the range of pixels between two shares of the sorted brightness: with 0.1 and 0.9, the darkest tenth and the brightest tenth are dropped. The loop does not sort anything. It walks the bins from dark to bright, and for each bin it counts only the part that lies between `low` and `high`.

:::example[A frame by hand]
Take 100 pixels: 10 black, 60 at 4 nits, 20 at 16 nits, and 10 at 4,096 nits (a lamp). Black is dropped, so 90 pixels count. In log2, the three groups sit at 2, 4 and 12.

Without a window the mean is $(60 \cdot 2 + 20 \cdot 4 + 10 \cdot 12) / 90$, which is 3.56. The multiplier is $0.18 / 2^{3.56}$, about 0.015. Without the lamp the mean would be 2.5, so its 10 pixels pulled the average up by about one stop and darkened the whole scene.

With the window 0.1 to 0.9, the cuts fall at pixel 9 and pixel 81 of the 90. The dark group contributes 51 pixels, the 16-nit group all 20, and the lamp 1 pixel. The mean is $(51 \cdot 2 + 20 \cdot 4 + 1 \cdot 12) / 72$, which is 2.69, and the multiplier is about 0.028. The program prints 3.60 and 2.74, because each bin's center sits a little off the exact log2.
:::

The last lines of the toy show the adaptation step. A fraction of the way to the target is taken each frame, and the fraction is $1 - e^{-s \, t}$, where $s$ is the speed and $t$ the frame's seconds. One step of 0.1 s and ten steps of 0.01 s land on the same value, which is the reason to write the fraction like that and not as a fixed 5 % per frame.

## The real code, in the order data flows

### Counting into bins

The histogram counts luminance, so the first function turns a luminance into a bin. Look at the first test: it asks whether the luminance is above the limit, and returns 0 when it is not.

```slang src="Strata/shaders/Include/Exposure.slang#L23-L30"
uint LuminanceToHistogramBin(float luminance)
{
	// The negated comparison also sends NaN to bin 0.
	if (!(luminance > exp2(ST_HISTOGRAM_MIN_LOG2)))
		return 0u;
	float t = clamp((log2(luminance) - ST_HISTOGRAM_MIN_LOG2) / (ST_HISTOGRAM_MAX_LOG2 - ST_HISTOGRAM_MIN_LOG2), 0.0, 1.0);
	return 1u + uint(t * float(ST_HISTOGRAM_BINS - 2u));
}
```

The range is log2 -12 to 16, which is 28 stops, cut into 254 steps, so a bin is about 0.11 of a stop wide. A value below $2^{-12}$ goes to bin 0 with black. The reversed comparison `!(luminance > ...)` is true for :term[NaN]{id=nan}, because every comparison with NaN is false. A broken pixel therefore lands in the ignored bin and cannot poison the average.

### Counting and the weights

A weight says how many counts one pixel adds. With `Average` every pixel adds 1. With `CenterWeighted` the weight comes from a Gaussian bump, a smooth hill, centered on the image.

```slang src="Strata/shaders/PostProcess/Histogram.comp.slang#L42-L50"
uint MeteringWeight(int2 pixel, int2 size)
{
	if (u_Parameters.Metering != ST_METERING_CENTER_WEIGHTED)
		return 1u;
	float2 uv = (float2(pixel) + 0.5) / float2(size);
	float2 offset = (uv - 0.5) * float2(u_Parameters.MeteringAspect, 1.0);
	float falloff = exp(-dot(offset, offset) / (2.0 * 0.25 * 0.25));
	return uint(round(16.0 * (0.25 + 0.75 * falloff)));
}
```

The distance is measured in image heights, and the aspect ratio keeps the bump round. The weight is 16 at the center and falls toward 4 at the corners, because the formula is $16 (0.25 + 0.75 e^{-r^2 / 0.125})$ with $r$ the distance from the center. At a distance of 0.25 image heights the weight is about 11. A camera's center-weighted meter works the same way, so the middle of the frame decides and the edges still count a quarter.

At 3,840 by 2,160 pixels the largest possible total is 8.3 million pixels times 16, far below the largest 32-bit :term[integer]{id=integer}, so the counters cannot overflow. That bound is why the weights are small whole numbers and not floats.

The shader that fills the bins is a compute shader. Each group of 16 by 16 threads counts its pixels into group-shared memory, which is fast and private to the group, then adds the group's counts to the global histogram.

```slang src="Strata/shaders/PostProcess/Histogram.comp.slang#L54-L71"
void st_Main()
{
	s_Bins[st_LocalInvocationIndex] = 0u;
	GroupMemoryBarrierWithGroupSync();

	int2 pixel = int2(st_GlobalInvocationID.xy);
	int2 size = TextureSize(u_SceneColor, 0);
	if (all((pixel < size)))
	{
		uint bin = LuminanceToHistogramBin(Luminance(u_SceneColor.Load(int3(pixel, 0)).rgb) * u_Parameters.InversePreExposure);
		InterlockedAdd(s_Bins[bin], MeteringWeight(pixel, size));
	}
	GroupMemoryBarrierWithGroupSync();

	uint count = s_Bins[st_LocalInvocationIndex];
	if (count > 0u)
		InterlockedAdd(u_Histogram[st_LocalInvocationIndex], count);
}
```

1. **Line 63:** the pixel's luminance is divided by the pre-exposure, because the HDR target holds light multiplied by it; the division is exact for a power of two.
2. **Line 64:** `InterlockedAdd` is an atomic addition, so two threads of the group that land in the same bin do not lose a count.
3. **Line 66:** every thread must have finished its counting before any thread reads the shared bins.
4. **Lines 68–70:** each of the 256 threads owns one bin and adds its group's count to the global histogram, skipping empty bins to save atomics on memory shared by all groups.

The local counting is the reason for the shared bins. Without it, every pixel of the image would add to one of 256 global counters, and thousands of threads would queue on the same few addresses.

### The percentile window and the mean

The second pass is a single group of 256 threads, and only thread 0 does the work after loading the bins. The work is small: 255 bins.

```slang src="Strata/shaders/PostProcess/Exposure.comp.slang#L59-L71"
float low = total * u_Parameters.LowPercentile;
float high = total * u_Parameters.HighPercentile;
float accumulated = 0.0;
float sum = 0.0;
float weight = 0.0;
for (uint index = 1u; index < ST_HISTOGRAM_BINS; index++)
{
	float count = float(s_Bins[index]);
	float inside = max(min(accumulated + count, high) - max(accumulated, low), 0.0);
	sum += inside * HistogramBinToLog2(index);
	weight += inside;
	accumulated += count;
}
```

1. **Lines 59–60:** the cuts are counts, the window's shares times the total of bins 1 to 255; black is not in the total.
2. **Line 67:** `inside` is the overlap of the bin's range of counts with the window, never below zero. A bin that lies half in the window adds half its count.
3. **Line 68:** the weighted sum of the bins' centers in log2 units; the final mean is this sum divided by `weight`.

The overlap trick is why the window can cut a bin in two. Without it the average would jump when a few pixels moved from one bin to the next. A target of the mean is `sum / weight`, then clamped to `AutoExposureMinEV` and `AutoExposureMaxEV`, the range in log2 nits.

On the CPU side `UpdateExposure` keeps the window sane. It clamps the low share to 0 to 0.49 and the high share to 0.51 to 1. The high share is at least 0.02 above the low one, so at least two in a hundred of the pixels always stay in the window. A NaN setting falls back to 0.1 and 0.9. Dropping the brightest tenth keeps lamps and the sun's disk from deciding the exposure, and dropping the darkest tenth does the same for deep shadows.

### Adaptation

**Light/dark adaptation** is the eye's habit of following a brighter scene at one rate (light) and a darker scene at another (dark). Real eyes adapt to light faster than to dark, and Strata does the same: `AutoExposureLightSpeed` is 3 per second and `AutoExposureSpeed`, the dark one, is 1.5.

Which speed applies is decided by comparing the target with the previous value, and the fraction itself comes from the CPU. The helper that supplies the time is short.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L79-L87"
float SceneRenderer::StepSeconds(std::optional<std::chrono::steady_clock::time_point>& last, const SceneRenderOptions& options)
{
	const auto now = std::chrono::steady_clock::now();
	float seconds = last ? std::clamp(std::chrono::duration<float>(now - *last).count(), 0.0f, c_MaxStepSeconds) : 0.0f;
	if (options.AdaptationSeconds)
		seconds = std::isfinite(*options.AdaptationSeconds) ? std::max(*options.AdaptationSeconds, 0.0f) : 0.0f;
	last = now;
	return seconds;
}
```

The step is the wall-clock time since the last frame, clamped to the range 0 to `c_MaxStepSeconds`, which is 0.25. A tool that steps time itself passes `AdaptationSeconds` in the render options, and the function uses that value instead, after replacing a NaN or negative number by 0. The first frame has no earlier time and gets 0.

The speeds become fractions in the :term[lambda]{id=lambda} `adapt` at the top of the parameters. The next quote shows it with the clamps of the range. A speed of 0 or less, or any frame after a reset, gives a fraction of 1: the exposure jumps.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L937-L944"
auto adapt = [&](float speed) { return m_ResetExposure || !(speed > 0.0f) ? 1.0f : 1.0f - std::exp(-deltaTime * std::min(speed, 1000.0f)); };
RenderData::ExposureParameters parameters = {};
parameters.MinLog2 = std::clamp(settings.AutoExposureMinEV, RenderData::c_HistogramMinLog2, RenderData::c_HistogramMaxLog2);
parameters.MaxLog2 = std::clamp(settings.AutoExposureMaxEV, parameters.MinLog2, RenderData::c_HistogramMaxLog2);
// Light adaptation (toward a brighter scene) and dark adaptation (toward a darker one) at their own speeds.
parameters.AdaptLight = adapt(settings.AutoExposureLightSpeed);
parameters.AdaptDark = adapt(settings.AutoExposureSpeed);
parameters.Compensation = compensation;
```

At 3 per second and a step of 0.25 s the fraction is $1 - e^{-0.75}$, about 0.53, so a long pause closes about half the gap and never more. The speeds are limited to 1,000 so that the :term[exponent]{id=exponent} stays finite.

The shader then uses the fraction.

```slang src="Strata/shaders/PostProcess/Exposure.comp.slang#L84-L97"
float adapt = target > previous ? u_Parameters.AdaptLight : u_Parameters.AdaptDark;
float adapted;
if (u_Parameters.AdaptLight >= 1.0 && u_Parameters.AdaptDark >= 1.0)
	adapted = target;
else if (metered)
	adapted = lerp(previous, target, adapt);
else
	adapted = previous;
float keyStops = u_Parameters.KeyStrength > 0.0
	? clamp(u_Parameters.KeyStrength * (adapted - u_Parameters.KeyReferenceLog2), u_Parameters.KeyMinStops, u_Parameters.KeyMaxStops)
	: 0.0;
u_Exposure[ST_EXPOSURE_LOG_LUMINANCE] = adapted;
u_Exposure[ST_EXPOSURE_MULTIPLIER] = u_Parameters.Compensation * c_MiddleGray / exp2(adapted) * exp2(keyStops);
u_Exposure[ST_EXPOSURE_KEY] = keyStops;
```

1. **Line 84:** the speed is chosen by direction, light when the target is brighter than the current value.
2. **Lines 86–87:** both fractions at 1 mean a jump to the target, so a buffer that holds no value yet never leaks into the result.
3. **Lines 88–91:** a black image (nothing metered) keeps the current value; otherwise `lerp` moves the fraction of the way.
4. **Line 96:** the multiplier: compensation times 0.18 divided by $2^{a}$, then times $2^{k}$ for the key.

In symbols, the multiplier of the automatic case is a product of three factors.

$$M = 2^{E} \cdot \frac{0.18}{2^{a}} \cdot 2^{k}$$

Here $M$ is the multiplier, $E$ the `Exposure` property used as a compensation, $a$ the adapted log2 average luminance and $k$ the key's stops. **Exposure compensation** is that offset: the stops you add to what the meter chose, as a photographer turns a dial to make a snowy scene brighter. With $E = 0$ and $k = 0$ the average lands exactly on 0.18.

### The CPU and the barrier

The remaining lines of `UpdateExposure` clear the histogram, dispatch the two passes and keep them in order.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L962-L976"
commandList->clearBufferUInt(m_HistogramBuffer, 0);
nvrhi::ComputeState state;
state.pipeline = m_HistogramPipeline;
state.bindings = { bindingSet };
commandList->setComputeState(state);
commandList->setPushConstants(&parameters, sizeof(parameters));
commandList->dispatch((m_ViewportSize.x + 15) / 16, (m_ViewportSize.y + 15) / 16, 1);

// NVRHI places barriers only when the binding sets change: the histogram must be complete before it is read.
commandList->setBufferState(m_HistogramBuffer, nvrhi::ResourceStates::UnorderedAccess);
commandList->commitBarriers();
state.pipeline = m_ExposurePipeline;
commandList->setComputeState(state);
commandList->setPushConstants(&parameters, sizeof(parameters));
commandList->dispatch(1, 1, 1);
```

1. **Line 962:** the histogram is cleared to zero before each frame's counting.
2. **Line 968:** one group for every 16 by 16 tile of the viewport, rounded up.
3. **Lines 971–972:** the explicit state change and `commitBarriers`; both passes use one binding set, so NVRHI does not see a reason to place a barrier by itself.
4. **Line 976:** one group of 256 threads is enough for 256 bins.

The histogram dispatch writes with atomics, and the exposure dispatch reads the result. The barrier is the contract's rule: a unit test that passes by luck on one GPU can fail on another when it is missing.

Frames later, the buffer is copied back for the pre-exposure. A copy that is still under way is not started again, so the frame's readback is skipped. The pre-exposure itself is the next page's topic.

### The exposure key

Automatic exposure puts every scene at middle gray, so a dark cellar and a beach in the sun look equally bright. That is not what the eye or a good picture does. The **exposure key** is a setting that lets a scene darker than direct sunlight read darker than middle gray, by a share of the difference.

The reference is a gray card facing the sun. Strata computes its luminance in `SceneRenderer.cpp`.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3819-L3826"
// The exposure key's reference: the luminance of a gray card (albedo 0.18) facing the directional light, as Forward.frag
// lights it (the atmosphere's transmittance included); none without a light.
std::optional<float> keyReferenceLog2;
const float sunLuminance = glm::dot(glm::vec3(frame.DirectionalLightColor), glm::vec3(0.2126f, 0.7152f, 0.0722f)) * 0.18f / glm::pi<float>();
if (frame.DirectionalLightDirection.w > 0.0f && sunLuminance > 0.0f && std::isfinite(sunLuminance))
	keyReferenceLog2 = std::log2(sunLuminance);
if (postProcess.AutoExposure)
	m_Stats.ExposureKeyReferenceLog2 = keyReferenceLog2;
```

The card's luminance is the sun's color times 0.18 divided by $\pi$, which is what a dull card of that gray sends back under that light. Without a directional light the reference is empty and the key is off. The shader then multiplies the difference between the metered log2 luminance $a$ and the card's log2 luminance $r$ by the key $c$, and clamps the result to the range from -2 to 0: $k = \mathrm{clamp}(c \, (a - r), -2, 0)$. Lines 92 to 94 of `Exposure.comp.slang`, in the quote above, do exactly that.

Take the look-dev room of the engine's own measurements: it meters at EV100 14.040 and its card sits at 15.191. The difference is -1.151 stops and with the default key of 0.12 the result is $-0.138$ stops: the room is shown a seventh of a stop darker than middle gray. A cellar five stops below the card at the same key gets $-0.6$, and no scene gets less than $-2$ stops.

Why does the key never brighten? The card measures the sun alone. A scene above the card gets more light than the sun gives, from the sky, from bounces or from emission. Brightening it would clip a white wall in the sun, so the code clamps the key at 0. A game maker who wants such a scene brighter gives a positive `Exposure`, as a photographer would, and the exposure buffer's third float is what `renderStats.exposure.keyStops` reports.

### Reset, jump and the limits

A new scene should start at its own brightness, not adapt from the last scene. `GameRenderer::Render` in `Strata/src/Strata/Runtime/GameRenderer.cpp` calls `ResetExposureAdaptation` when the scene changes, and again when a :term[primary camera]{id=primary-camera} returns after a message. The reset sets a flag so that the next frame's fractions are 1, which is the jump, and it also restarts the pre-exposure. `JumpExposureAdaptation` only does the jump and keeps the pre-exposure. Turning automatic exposure off sets the same flag, so enabling it again starts at the scene's brightness.

The two limits are `AutoExposureMinEV` (default -4) and `AutoExposureMaxEV` (default 16), both log2 nits. They stop a black frame from brightening without end and a sun from darkening the image to nothing. The percentiles, speeds, key and metering mode exist only while `AutoExposure` is on; the editor shows them inactive otherwise.

### Judging exposure with the luminance view

Numbers beat opinions. The luminance debug view, whose drawing belongs to [Measuring light](../light/measuring-light.md), colors every pixel by its EV100 in bands one stop wide. Count the bands between the brightest and the darkest part you care about: that is the range your exposure must fit into the display. A frame whose content fills only the top bands tells you that the exposure or the lights are wrong.

For one number, the command `editor.perf` returns `renderStats.exposure` with `ev100` (what the meter read, frames late), `keyStops` and `cardEv100`; the value is null with manual exposure.

::compare{id=metering-modes}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Average of log luminance from a mip chain | Engines and tutorials that average a chain of smaller copies | No atomics, no shared counters, a simpler shader | Black cannot be ignored, no percentile window, and one lamp moves the average |
| Fixed exposure only | :term[Renderers]{id=renderer} whose scenes keep one brightness | Exact, predictable images, no adaptation to explain | A scene that changes in brightness needs a person to turn a dial |
| Camera settings (opening, time, sensitivity) | Physically based pipelines that follow a real camera | A language photographers already know | A second set of properties and a conversion for what stops already say |
| Spot metering as the only mode | Camera systems that follow one subject | A precise reading of the subject | No reading of the whole scene; a spot in the sky or a shadow gives a bad exposure |
| Eye adaptation with one speed | Engines with a single speed property | One property fewer | A dark room after the sun takes as long to brighten as a sunny day to darken, which does not feel real |

## How it is tested

The cases live in the suite `GPU.SceneRenderer.PostProcess` of `StrataTests/src/Renderer/GPUScenePostProcessTests.cpp`. They need a GPU, so they carry the label `gpu`. Each case ends by checking that the device logged no new error.

- `Automatic exposure maps the average brightness to middle gray and adapts over time`: renders a wall that gives off light, dim and then bright, and expects the displayed value to land on middle gray, then shows the exposure compensation shifting it by stops.
- `Automatic exposure meters the lit content, not the black background around it`: checks that an empty black background does not pull the exposure.
- `Automatic exposure adapts to brighter scenes faster than to darker ones`: sets `AdaptationSeconds` to 0.1 and compares both directions.
- `Center-weighted metering favors the middle of the image`: a dark surround with a bright central ninth must meter at least half a stop brighter than the average, and a CPU copy of the metering must agree within 0.06.
- `The exposure key darkens what meters below the sun's gray card` and `The exposure key never brightens: a dim sun under a bright sky, and a sun fading out over a lit scene`.

Run the suite by name, for example `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.PostProcess`, or the whole label through `ctest --preset windows-debug -L gpu`.

## Changing it safely

The extension points are few. A new metering mode adds a value to the enum `ExposureMetering` and a branch in `MeteringWeight`. A new property of the meter goes into `ExposureParameters` on both sides, and the two copies of that :term[struct]{id=struct} must stay the same size.

- Enum values are appended and never change. The reason: they are part of the script and file interface, and a saved scene stores the number.
- The barrier between the two dispatches stays. The reason: NVRHI would not place one.
- Tests set `AdaptationSeconds`, and never wait for the wall clock to adapt. The reason: a test that depends on :term[frame times]{id=frame-time} fails on a slow machine.
- A change to the shader's constants updates `PostProcessData.h` and `Exposure.slang` together; the :term[header]{id=header} says they are kept in sync.
- Check before committing: the suite above, then the whole `gpu` label, since the pre-exposure follows the metering.

## What went wrong before

Up to version 0.5.0 the default `AutoExposureMaxEV` was 12, but a scene lit by a real sun meters above 12 in log2 nits: the look-dev overview reads EV100 15.6, which is 12.6. The change that raised the limit names scenes in the sun near $2^{15}$ nits. The limit of 12 clipped such a scene: the meter saw it as darker than it was, and the picture came out too bright, up to white. The fix, in 0.6.0, raised the default to 16, and files that store 12 keep it, so an old scene with a real sun needs its limit raised by hand. The test `A 100,000 lux sun with its disk in view reaches no HDR clamp once the pre-exposure settled` sets `AutoExposureMaxEV` to 16 for that reason.

The key once also brightened scenes above the card. It now stops at 0, and the last test of the list above keeps it so.

## Summary

- Compute $V_{100} = \log_2 L + 3$ for a luminance $L$ in nits, and the manual `Exposure` that gives middle gray: $\log_2 (0.18 / L)$, about $0.5 - V_{100}$.
- A histogram of log2 luminance, with black in an ignored bin, a weight per pixel and a percentile window, gives one robust average of a frame.
- Adaptation moves a fraction $1 - e^{-s\,t}$ of the way each frame, at one speed toward brighter scenes and another toward darker ones, with the step capped at 0.25 s.
- The exposure key lowers the exposure by a share of how far the scene is below the sun's gray card, from 0 to -2 stops, and never raises it.
- A metering mode travels from the `AutoExposureMetering` property through `UpdateExposure` into the :term[push constants]{id=push-constants} and `MeteringWeight`; a new mode appends an enum value and changes those places.

## Check yourself

1. A scene's average luminance is 2,048 nits. What EV100 does a meter with K = 12.5 read, and what manual `Exposure` puts that average at middle gray?

   - A. EV100 11 and `Exposure` -10.5
   - B. EV100 14 and `Exposure` -13.5
   - C. EV100 14 and `Exposure` 13.5
   - D. EV100 11 and `Exposure` -13.5

   :::answer{tests="camera-model"}
   B. $\log_2 2048 = 11$ and adding 3 gives 14; the manual value is $0.5 - 14$, about -13.5 ($\log_2 (0.18 / 2048)$ is -13.47). A and D forget the 3. C has the wrong sign: a bright scene needs a negative exposure.
   :::

2. Why does the histogram pass put black pixels into bin 0 and the exposure pass ignore that bin?
   - A. Black pixels cannot be counted by `InterlockedAdd`.
   - B. They say nothing about the lit content, and counting them would over-expose a small lit object on a dark background.
   - C. Bin 0 is the brightest bin.
   - D. The GPU cannot take the logarithm of zero, so the pass crashes.

   :::answer{tests="histogram-meter"}
   B. A is wrong: atomics add any count. C reverses the order, since bin 0 is the darkest. D is wrong too: the reversed comparison sends black (and NaN) to bin 0 before any logarithm is taken.
   :::

3. The light speed is 3 per second and a window is minimized for 5 seconds. The renderer then draws a frame with a brighter target. What fraction of the gap does it close in that frame?

   :::answer{tests="adaptation"}
   About 0.53. The step is capped at 0.25 s, so the fraction is $1 - e^{-3 \cdot 0.25} = 1 - e^{-0.75}$, which is 0.53. Without the cap the fraction would be 1 and the exposure would jump.
   :::

4. A scene meters at EV100 11 and the sun's card is at EV100 15.5. What are the key's stops at the default key of 0.12, and what are they for a scene at EV100 17?

   :::answer{tests="key"}
   The difference is $-4.5$ stops, so $k = 0.12 \cdot (-4.5) = -0.54$: slightly more than half a stop darker. For EV100 17 the difference is $+1.5$ and the product is $+0.18$, which the clamp raises to 0. The key never brightens, since a scene above the card is lit by more than the sun.
   :::

5. You add the value `Spot` to `ExposureMetering`. Which statement is true?
   - A. Give it the value 1, after `Average`, and move `CenterWeighted` to 2.
   - B. Append it with the value 2 and add a branch to `MeteringWeight`.
   - C. Only the shader changes; the component stays as it is.
   - D. Replace the enum by a float.

   :::answer{tests="trace-mode"}
   B. Existing values never change because scripts and saved files store the numbers, so A is wrong. C is wrong because the component's enum property list needs the new name as well. D breaks the :term[file format]{id=file-format}.
   :::

## Exercises

1. **Basic.** Open a Basic 3D project, switch **Auto Exposure** off and find the manual `Exposure` that looks right. Then switch it on and compare with the metered EV100.

   :::answer[Worked solution]{tests="camera-model"}
   Start from the formula: the ground in the sun meters near EV100 15, so $0.5 - 15$ gives about -14.5. Set `Exposure` to -14.5 on the **Post Process** component and adjust by half a stop to taste. With **Auto Exposure** on, run the command `editor.perf` and read `renderStats.exposure.ev100`, which should lie near 15. Putting that number into $0.5 - V_{100}$ returns your manual value within half a stop; the difference is the template's own `Exposure` of 0.25, a compensation the meter adds, then the key and the window.
   :::

2. **Medium.** Write a program that prints, for four average luminances, the EV100, the manual `Exposure` and the key's stops under a 100,000 lux sun.

   :::answer[Worked solution]{tests="camera-model,key"}
   The card's luminance is $100000 \cdot 0.18 / \pi$ nits, and its EV100 is $\log_2$ of that plus 3. For each scene, `ev100 = log2(L) + 3`, `exposure = log2(0.18 / L)` and `key = clamp(0.12 * (ev100 - cardEv100), -2, 0)`.

   ```cpp sketch="image-exposure-table.cpp"
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   // For a scene's average luminance in nits and the sun's illuminance in lux: the EV100 a meter reads, the manual
   // Exposure that puts the average at middle gray, and the exposure key's stops for a key of 0.12.
   int main()
   {
   	const float luminances[] = { 4096.0f, 1000.0f, 30.0f, 0.5f };
   	const float sunLux = 100000.0f;
   	const float cardNits = sunLux * 0.18f / 3.14159265f;
   	const float cardEv100 = std::log2(cardNits) + 3.0f;
   	for (float luminance : luminances)
   	{
   		float ev100 = std::log2(luminance) + 3.0f;
   		float exposure = std::log2(0.18f / luminance);
   		float key = std::clamp(0.12f * (ev100 - cardEv100), -2.0f, 0.0f);
   		std::printf("%8.1f nits: EV100 %5.2f, Exposure %6.2f, key %5.2f\n", luminance, ev100, exposure, key);
   	}
   	return 0;
   }
   ```

   ```text output-of="image-exposure-table.cpp"
     4096.0 nits: EV100 15.00, Exposure -14.47, key -0.06
     1000.0 nits: EV100 12.97, Exposure -12.44, key -0.30
       30.0 nits: EV100  7.91, Exposure  -7.38, key -0.91
        0.5 nits: EV100  2.00, Exposure  -1.47, key -1.62
   ```

   1. **Line 11:** the card's luminance under a sun of 100,000 lux.
   2. **Line 12:** its EV100, the same $\log_2 + 3$ as for any luminance.
   3. **Line 16:** the manual `Exposure` that puts the scene's average at 0.18.
   4. **Line 17:** the key's stops, clamped to the range from -2 to 0.

   The key grows with the distance below the card, from -0.06 for the brightest scene to -1.62 for the dimmest.
   :::

3. **Medium.** Trace it yourself: follow `AutoExposureMetering` from its registration to the shader with a search or a debugger.

   :::answer[Worked solution]{tests="trace-mode"}
   Search for the property's name. `Strata/src/Strata/Renderer/RendererComponents.cpp` registers it with `EnumProperty` and the names Average and Center Weighted. `SceneRenderer::UpdateExposure` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp` copies it into `parameters.Metering` and sends the struct as push constants. In `Strata/shaders/PostProcess/Histogram.comp.slang` the function `MeteringWeight` reads `u_Parameters.Metering` and returns the weight.
   :::

4. **Hard.** Plan a `Spot` metering mode that weighs only a small circle in the middle, and say which tests you add.

   :::answer[Worked solution]{tests="trace-mode,histogram-meter"}
   Append the value 2, named `Spot`, to `ExposureMetering` in `RendererComponents.h` and add it to the property's name list in `RendererComponents.cpp`. In `MeteringWeight` add a branch for 2 that returns a weight from a narrow Gaussian, for example a width of 0.05 image heights. Nothing in `UpdateExposure` changes, since it copies the enum. A GPU test next to the center-weighted one puts a bright patch in the middle and a dark surround, and expects the spot value to be above the center-weighted value. The CPU copy of the metering in the test file gets the same branch.
   :::

## Where it lives in Strata

- Shaders: `Strata/shaders/Include/Exposure.slang`, `Strata/shaders/PostProcess/Histogram.comp.slang`, `Strata/shaders/PostProcess/Exposure.comp.slang`.
- CPU: `SceneRenderer::UpdateExposure` and `SceneRenderer::StepSeconds` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp`; the key's reference in `Strata/src/Strata/Renderer/SceneRenderer.cpp`; the buffer's layout in `Strata/src/Strata/Renderer/PostProcessData.h`.
- Properties: `PostProcessComponent` in `Strata/src/Strata/Renderer/RendererComponents.h`, `Exposure` and the `AutoExposure` properties.
- Reset: `GameRenderer::Render` in `Strata/src/Strata/Runtime/GameRenderer.cpp`.
- Tests: the suite `GPU.SceneRenderer.PostProcess`.
- Command: `editor.perf` reports `renderStats.exposure`.

## Further reading

- The Frostbite course notes on physically based units and exposure (beginner to intermediate): the same camera model, with the photographic constants.
- The Filament documentation, section on exposure (intermediate): a clear derivation of EV100 from lens settings.
- A photography primer on the sunny sixteen rule (beginner): why f/16 works.
