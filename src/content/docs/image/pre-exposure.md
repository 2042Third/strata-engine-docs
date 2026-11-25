---
id: image/pre-exposure
title: "Pre-exposure"
description: "How Strata keeps bright light inside the half-float range with a power of two that every pass multiplies in and divides out, and why no pixel changes."
kind: internals
size: M
tracks: [E]
needs: [image/exposure, basics/numbers, gpu/readback-timing]
time: 50
learn:
  - id: power-of-two
    text: explain why a change of a power-of-two pre-exposure changes no pixel, and what breaks with another factor
  - id: choose-step
    text: compute the pre-exposure that Strata chooses from a metered exposure factor, and decide whether it steps
  - id: async-epoch
    text: explain why the metered exposure comes back frames later, and what an epoch and the settled flag protect
  - id: writers-readers
    text: find every pass that multiplies by or divides out the pre-exposure, and say where a new pass joins
since: 0.6.0
status: final
---

A scene lit in real units holds numbers that no :term[half-float]{id=half-float} image can store, and the screen needs only a small part of them. The **pre-exposure** is a power of two that Strata multiplies into every write of the scene's :term[high dynamic range]{id=high-dynamic-range} (HDR) values and divides out of every read, so the numbers stay in range. The picture stays the same. This page covers the choice of that factor, the :term[readbacks]{id=readback} that feed it, and the passes that must agree with it. It does not cover how the forward :term[shader]{id=shader} computes light, how the metering works, or the anti-aliasing history beyond its change of scale.

Strata measures light in real units, and a pre-exposure keeps the HDR values in range. The reasons for that decision stand in the design aside of [Light units and exposure](../light/units-exposure.md), and this page is its mechanism.

## The problem and how engines solve it

A half float is a number stored in 16 bits. Its largest value is 65,504, and its smallest normal value is about 0.000061. Strata draws the scene into an image of half floats, because blending, bloom and the exposure all need values above 1. Read [Numbers](../basics/numbers.md) for the exponent and significand that give a half float this range.

Real light is far larger than that. A sun of 100,000 :term[lux]{id=lux} lights a white surface to about 31,800 nits (the unit of :term[luminance]{id=luminance}, :term[candela]{id=candela} per square metre). A specular highlight, the sun's bright disk, or the sum of sun and sky passes 65,504 quickly. Storing the number would overflow, and Strata clamps an overflowing value to 65,000, which turns a bright highlight flat and loses what bloom needs.

The screen has the opposite need. [Exposure](exposure.md) multiplies the scene by a small exposure factor, for a bright day about 0.00001, before the tone map. The image that the viewer sees uses only values near 1 after that exposure factor. So the large numbers are needed only until the exposure divides them down again.

Engines solve this by multiplying the shading result by a scale before it is written, and by undoing the scale when it is read. Two approaches are common:

- **Scale by the previous frame's exposure.** The :term[renderer]{id=renderer} uses last frame's exposure as the scale, as Frostbite does. The scale follows the scene closely, but it is a free number, so it must be undone exactly in every reader.
- **Scale by a fixed number.** The scale never changes, so nothing needs undoing during the frame. A fixed number cannot serve a sun at noon and a room at night.

Strata takes a third route, between them. It multiplies by a power of two that follows the exposure, changes it rarely, and divides it out exactly. A power of two only moves the exponent of a :term[floating-point number]{id=floating-point-number}, so a change of the scale changes no stored significand. The rest of this page builds that route.

## How the pre-exposure moves through frames

Each frame draws its :term[HDR image]{id=hdr-image} with one value, P, kept in `FrameConstants::TemporalParams.y`. Writers multiply by P; readers divide by it. The metering that decides the next P runs on the :term[graphics processing unit]{id=gpu} (GPU) and comes back to the :term[central processing unit]{id=processor} (CPU) several frames later, so a frame never waits for it.

```mermaid caption="Frame N is metered on the GPU; the value returns frames later through the ring, the CPU may step P, and the history is multiplied by the new P over the old." alt="Four boxes in time order. Frame N draws with P and meters the exposure. The metered value is copied into a ring of readback buffers. Several frames later the CPU reads the newest ready value and chooses a new P. The temporal history is multiplied by the new P over the old P in that frame's resolve."
flowchart LR
	A["Frame N: draw with P, meter the exposure on the GPU"] --> B["Copy into a slot of the ring of readbacks"]
	B --> C["Frame N+k: the CPU reads the newest ready slot and chooses P"]
	C --> D["Frame N+k: the temporal history is rescaled by P over the old P"]
```

The metering is the histogram and exposure passes of [Exposure](exposure.md). Their result is three numbers in a small buffer: the log of the average luminance, the key in stops, and the exposure factor. The copy waits in one of six slots, so up to six frames of metering can be :term[in flight]{id=in-flight}; [Readback and timing](../gpu/readback-timing.md) explains how such a buffer is polled without a stall.

The states of the renderer's choice follow from how exposure is set. Manual exposure and a forced value settle at once. Automatic exposure is unsettled until a readback of a frame drawn with the current P arrives and keeps it. A lighting view of values holds P, and a reset returns to 1.

```mermaid caption="The pre-exposure is settled at once under manual exposure, held during a value view, and unsettled after a reset until a readback of a frame drawn with the current value arrives." alt="A state diagram with four states: manual or forced, automatic and unsettled, automatic and settled, and held for a value view. A reset leads to automatic and unsettled with P equal to 1. A readback that keeps P leads from unsettled to settled. A step of P leads from settled back to unsettled."
stateDiagram-v2
	[*] --> AutomaticUnsettled: reset, P is 1
	AutomaticUnsettled --> AutomaticSettled: a readback of a frame drawn with P keeps it
	AutomaticSettled --> AutomaticUnsettled: P steps
	AutomaticUnsettled --> Manual: exposure set by hand or forced
	AutomaticSettled --> Manual: exposure set by hand or forced
	Manual --> AutomaticUnsettled: automatic exposure again
	AutomaticSettled --> Held: a value view starts
	AutomaticUnsettled --> Held: a value view starts
	Held --> AutomaticSettled: the view ends, a new epoch starts
	AutomaticUnsettled --> AutomaticUnsettled: reset, P is 1
```

## The contract

The rules below keep the image the same at any P. Each rule has its reason.

1. **Every writer of the HDR image multiplies by P.** The forward shader writes `color * u_Frame.TemporalParams.y`, and the sky does the same in `Strata/shaders/Scene/Skybox.frag.slang`. Fog is added inside those two shaders before the multiplication, and `SceneRenderer.cpp` multiplies the clear color by P on the CPU. A writer that forgets stores a value P times too large or too small, and the image is wrong only when P is not 1, in a daylight scene.
2. **Every reader divides P out, or reads the exposure factor divided by P.** The histogram, the bloom threshold and the temporal weights use `InversePreExposure`; the tone map multiplies by the exposure factor over P. A reader that forgets sees the image at the wrong brightness.
3. **P is a power of two.** A power of two moves only the exponent, so a change of P is exact while no value overflows or becomes :term[subnormal]{id=subnormal-number}. Any other factor rounds the significand, and the image changes in its last bits.
4. **The history is multiplied by P over the previous P.** The temporal history holds values at its frame's P; without that multiplication, a step of P is a flash.
5. **The metered exposure is never read back synchronously.** Waiting for the GPU in the middle of a frame stalls the frame; Strata uses the value from frames earlier, and accepts that P lags the scene.
6. **A value view is written without P.** A lighting view that shows values, not light, stores them without exposure, so the forward shader skips the multiplication there and P is held.
7. **A frame counts as settled only when its P was chosen from a measurement of a frame drawn with it.** Until then the brightest and darkest values may have overflowed or lost precision, and captures wait.

Two numbers bound the choice. The pre-exposure stays within 2 to the power of plus or minus 24, and the automatic value keeps 2 stops of headroom: P is a quarter of the metered exposure factor. Both live in `Strata/src/Strata/Renderer/SceneRenderer.h` as `c_MaxPreExposureStops` and `c_PreExposureHeadroomStops`.

## A toy version

The toy below chooses P from metered values that arrive two frames late. The scene is daylight with an exposure factor of 2 to the power of -14.3, then a dark cave from frame 6 with 2 to the power of -9. It keeps the same three ideas as the engine: a power of two within a range, 2 stops of headroom, and a change only beyond one stop. That dead band stops P from stepping back and forth.

```cpp sketch="image-pre-exposure-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr int c_HeadroomStops = 2;
constexpr int c_MaxStops = 24;
constexpr int c_ReadbackDelay = 2;

// The power of two nearest 2^stops, within the range of the pre-exposure.
float PowerOfTwoFor(float stops)
{
	const float limit = static_cast<float>(c_MaxStops);
	return std::ldexp(1.0f, static_cast<int>(std::round(std::clamp(stops, -limit, limit))));
}

// The log2 of the exposure multiplier that a frame meters: daylight, then a dark cave from frame 6.
float MeteredStops(int frame)
{
	return frame < 6 ? -14.3f : -9.0f;
}

int main()
{
	float preExposure = 1.0f;
	for (int frame = 0; frame < 12; frame++)
	{
		// The newest metering that has come back belongs to an earlier frame.
		const int metered = frame - c_ReadbackDelay;
		if (metered >= 0)
		{
			const float target = MeteredStops(metered) - static_cast<float>(c_HeadroomStops);
			// Change only when the current value is more than one stop off.
			if (std::abs(std::log2(preExposure) - target) > 1.0f)
				preExposure = PowerOfTwoFor(target);
		}
		std::printf("frame %2d is drawn with 2^%d\n", frame, static_cast<int>(std::log2(preExposure)));
	}
	return 0;
}
```

```text output-of="image-pre-exposure-toy.cpp"
frame  0 is drawn with 2^0
frame  1 is drawn with 2^0
frame  2 is drawn with 2^-16
frame  3 is drawn with 2^-16
frame  4 is drawn with 2^-16
frame  5 is drawn with 2^-16
frame  6 is drawn with 2^-16
frame  7 is drawn with 2^-16
frame  8 is drawn with 2^-11
frame  9 is drawn with 2^-11
frame 10 is drawn with 2^-11
frame 11 is drawn with 2^-11
```

1. **Line 13:** The target is rounded to a whole number of stops and clamped to 24 stops each way, so P is always a power of two in range.
2. **Line 28:** The metering that has arrived describes a frame two frames back, as a readback does.
3. **Line 31:** The target is the metered exposure in stops minus the 2 stops of headroom, so P is a quarter of the factor.
4. **Line 33:** P changes only when it is more than one stop from the target.

The output shows P staying at 1 for two frames, because no metering has arrived. At frame 2 the first value arrives and P falls to 2 to the power of -16, the power of two nearest the target of -16.3. It holds there until the cave is metered, then jumps to 2 to the power of -11. The small differences between target and P, here 0.3, never cause a change.

The toy has no epochs, no settled flag, no manual mode and no choice of the newest readback. The real code needs those, because the ring holds several frames at once and the scene can reset under it.

## The real code

The real choice lives in three functions of `Strata/src/Strata/Renderer/SceneRenderer.cpp`. Two helpers come first. Search for the rounding to a whole number of stops and for what an epoch clears.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1572-L1586"
float SceneRenderer::GetPreExposureFor(float stops)
{
	if (!std::isfinite(stops))
		return 1.0f;
	const float rounded = std::round(std::clamp(stops, static_cast<float>(-c_MaxPreExposureStops), static_cast<float>(c_MaxPreExposureStops)));
	return std::ldexp(1.0f, static_cast<int>(rounded));
}

void SceneRenderer::StartPreExposureEpoch()
{
	m_PreExposureEpoch++;
	// The stats report what this stretch metered: nothing until its first readback arrives, not the previous stretch's (a
	// scene metered before a reset or a stretch of manual exposure).
	m_MeteredLog2Luminance.reset();
	m_MeteredKeyStops = 0.0f;
```

1. **Line 1574:** A value that is not finite gives a pre-exposure of 1.
2. **Line 1576:** The stops are clamped to plus or minus 24 and rounded to a whole number.
3. **Line 1577:** `std::ldexp` builds 2 to that power exactly.
4. **Line 1582:** A new epoch makes every readback still in flight stale.
5. **Line 1585:** The statistics forget what the old stretch metered until a new readback arrives.

The next part of `ChoosePreExposure` handles every case but a fresh automatic measurement: the reset, the manual exposure or a forced value, and the held view. Search for the settled flag in each.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1589-L1622"
void SceneRenderer::ChoosePreExposure(const PostProcessComponent& settings, const SceneRenderOptions& options, bool hold)
{
	if (m_ResetPreExposure)
	{
		m_ResetPreExposure = false;
		m_PreExposure = 1.0f;
		m_PreExposureSettled = false;
		StartPreExposureEpoch();
	}
	const bool automatic = !options.PreExposure && settings.AutoExposure;
	if (!automatic)
	{
		// Readbacks of the automatic exposure before this stretch say nothing about the frames after it.
		if (m_PreExposureAutomatic)
			StartPreExposureEpoch();
		m_PreExposureAutomatic = false;
		if (options.PreExposure)
			m_PreExposure = *options.PreExposure > 0.0f ? GetPreExposureFor(std::log2(*options.PreExposure)) : 1.0f;
		else
			m_PreExposure = GetPreExposureFor(std::clamp(settings.Exposure, -20.0f, 20.0f)); // The power of two nearest 2^Exposure
		m_PreExposureSettled = true;
		return;
	}
	// A lighting view of values (not light) meters nothing worth following: the pre-exposure keeps its value until the view
	// ends (BeginLightingViewFrame starts a new epoch then), settled, since the values it writes are unexposed.
	if (hold)
	{
		m_PreExposureSettled = true;
		return;
	}
	if (!m_PreExposureAutomatic)
	{
		m_PreExposureAutomatic = true;
		m_PreExposureSettled = false; // Until a readback of this stretch arrives
```

1. **Lines 1591–1597:** A reset returns P to 1, marks it unsettled and starts a new epoch.
2. **Lines 1599–1610:** Manual exposure or a forced value gives P at once and counts as settled; leaving automatic exposure starts an epoch.
3. **Line 1606:** A forced value of zero or less gives 1; any other is rounded in stops.
4. **Line 1608:** Manual exposure is limited to plus or minus 20 stops and rounded to the nearest power of two.
5. **Lines 1614–1617:** A value view holds P and counts as settled.

The last part takes the newest readback of the current epoch and decides whether P steps.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1626-L1654"
ExposureReadback* newest = nullptr;
for (ExposureReadback& entry : m_ExposureReadbacks)
{
	if (entry.Readback->IsPending() && entry.Epoch == m_PreExposureEpoch && entry.Render > m_ExposureReadbackSeen && entry.Readback->IsReady()
		&& (!newest || entry.Render > newest->Render))
		newest = &entry;
}
if (!newest)
	return;
m_ExposureReadbackSeen = newest->Render;
float values[3] = {};
if (!newest->Readback->Read(values, sizeof(values)))
	return;
m_MeteredLog2Luminance = values[RenderData::c_ExposureLogLuminance];
m_MeteredKeyStops = values[RenderData::c_ExposureKeyStops];
const float multiplier = values[RenderData::c_ExposureMultiplier];
if (!(multiplier > 0.0f) || !std::isfinite(multiplier))
	return; // Nothing to follow (an image that metered nothing keeps its exposure)
// A target beyond the pre-exposure's range keeps the limit it reached.
const float target = std::log2(multiplier) - static_cast<float>(c_PreExposureHeadroomStops);
const float candidate = GetPreExposureFor(target);
if (std::abs(std::log2(m_PreExposure) - target) > 1.0f && candidate != m_PreExposure)
{
	m_PreExposure = candidate;
	m_PreExposureSettled = false;
}
else if (newest->PreExposure == m_PreExposure)
{
	m_PreExposureSettled = true;
```

1. **Lines 1626–1632:** The choice reads the newest readback that is of the current epoch, ready and not yet read.
2. **Lines 1642–1643:** An image that metered nothing, with no positive and finite factor, leaves P as it is.
3. **Line 1645:** The target is the log of the factor minus the 2 stops of headroom.
4. **Line 1647:** P steps only beyond one stop, and only to a different value; the flag turns false.
5. **Lines 1652–1654:** Otherwise a readback of a frame drawn with the current P makes the flag true.

Another function records the readback into the ring, after the exposure pass has written its three numbers. The slot is used only if its earlier copy has finished, and it remembers the frame, the epoch and the P that drew it.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L980-L987"
ExposureReadback& readback = m_ExposureReadbacks[m_ExposureReadbackIndex];
if (readback.Readback->IsPending() && !readback.Readback->IsReady())
	return;
readback.Readback->Record(commandList, m_ExposureBuffer, 0, 3 * sizeof(float));
readback.Render = m_RenderCount + 1;
readback.Epoch = m_PreExposureEpoch;
readback.PreExposure = m_PreExposure;
m_ExposureReadbackRecorded = true;
```

The ring has six slots (`c_GPURecordCount`), and `SubmitExposureReadback` advances to the next slot after the submit. A slot whose earlier copy is still under way skips the frame's metering, so P waits for a later one.

Finally the temporal resolve builds the history's scale and the inverse for its luminance weights.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1748-L1753"
parameters.CurrentWeight = 1.0f / static_cast<float>(m_TemporalFrames);
parameters.MinWeight = 1.0f / static_cast<float>(settings.HistoryFrames);
parameters.MotionWeightScale = settings.MotionResponse;
parameters.MaxMotionWeight = settings.MaxMotionWeight;
parameters.HistoryScale = parameters.CurrentWeight < 1.0f ? m_PreExposure / m_HistoryPreExposure : 1.0f;
parameters.InversePreExposure = 1.0f / m_PreExposure;
```

The history's scale is the new P over the previous one, and is 1 on the first frame, which has no history. The weights read the inverse of P. The resolve ends by storing P as the history's own, `m_HistoryPreExposure`.

An **epoch** is a counter that `ChoosePreExposure` raises whenever earlier readbacks stop describing the frames to come: a reset, a stretch of manual exposure, or the end of a value view. Each readback carries the epoch of the frame that recorded it, and only readbacks of the current epoch are read.

:::example[Settling a daylight scene]
A wall of 20,000 nits meets automatic exposure. This case is the one tested in the engine.

1. Frame 0 draws with P equal to 1. The metered exposure factor is 2 to the power of -16.8, so the :term[middle gray]{id=middle-gray} of the screen is 20,000 times 2 to the power of -16.8, about 0.17.
2. The first readback arrives. The target is -16.8 - 2 = -18.8 stops. The distance from the current exponent 0 is 18.8, more than 1, so the candidate is 2 to the power of -19, the nearest power of two, and P steps there. Settled turns false.
3. A second readback, of a frame still drawn with P equal to 1, gives the same target. The distance from -19 is now 0.2, so P stays. That readback was drawn with 1, not with 2 to the power of -19, so the flag stays false.
4. A readback of a frame drawn with 2 to the power of -19 arrives. P stays and the drawn value equals the current one, so settled turns true. The test needs at most 3 frames after the first.

The wall now stores 20,000 times 2 to the power of -19, about 0.038, where a pre-exposure of 1 would store 20,000. A highlight a million times brighter than the wall still fits: stored, it is about 38,000, under the clamp of 65,000.
:::

Each difference from the toy has a reason. The ring exists because one frame's metering is still in flight when the next frame starts. The epoch and the settled flag exist because readbacks from before a reset must not steer after it. The held branch exists because a value view writes numbers without exposure, so metering them would feed back nonsense.

## What callers may force

`SceneRenderOptions::PreExposure` forces the frame's value. Another number is rounded to the nearest power of two in stops, and zero, negative or non-finite numbers become 1. Tests, bakes and renderers whose images are compared with each other set it, so their HDR values match without each one waiting for its own metering. The reflection probe bake sets it for that reason; [Reflection probes](../indirect/probes.md) covers the bake.

The editor does the reverse for pictures. Its `viewport.capture` command and the project's picture render again, at most 8 frames, while `SceneRendererStats::PreExposureSettled` is false. A capture of a daylight scene therefore waits for the readbacks of the example above.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Scale by the previous frame's exposure, any number | Frostbite (see Further reading) | A scale that follows the scene every frame, with no dead band | The exactness: a free number rounds, and the image changes with it |
| A fixed scale | Engines whose scenes stay within a narrow range of brightness | No readback, no epochs, no scaling of the history | The sun at noon and a room at night cannot share one range |
| Read the metering back at once | Tools that can afford a stall | P that is never behind the scene | A stalled frame on every readback |
| No pre-exposure: store exposed values | Engines that expose in the shader | No divide in the readers | Highlights above the clamp are lost, and the values change with each exposure step |

## How it is tested

The cases live in the suite `GPU.SceneRenderer.PostProcess` in `StrataTests/src/Renderer/GPUScenePostProcessTests.cpp`. They need a GPU, so they carry the label `gpu`. Run them directly with:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.PostProcess
```

The program reports the test cases that passed and failed. These cases are the ones that matter here:

- `The pre-exposure is a power of two that changes no image: forced values, the clear color and the sky` renders one scene with pre-exposures 8 and 16 and checks that the pixels are equal, and that every HDR texel at 16 is exactly twice the texel at 8. It also checks that 11 rounds to 8 and 0 to 1.
- `A 100,000 lux sun with its disk in view reaches no HDR clamp once the pre-exposure settled` checks the problem this page started with.
- `A fresh renderer settles its pre-exposure within a few frames, and starts again from 1 after a reset` checks the example above: the value 2 to the power of -19, manual exposure that settles at once, and the reset to 1.
- `The temporal history follows a pre-exposure step without a flash` compares a renderer whose P steps from 1 to a sixteenth with one whose P stays, frame by frame, and requires a difference of 0.

## Changing it safely

A new pass that writes the HDR image multiplies by `u_Frame.TemporalParams.y` and clamps with `SanitizeHDR` after the multiplication, as the forward shader does. A new pass that reads the HDR image divides by P, or takes `InversePreExposure` in its constants as the histogram, bloom and temporal passes do. A pass that reads the scene color to draw what lies behind glass divides by `u_Frame.TemporalParams.y`, as `Forward.frag.slang` does.

Keep P a power of two: never write a new rule that chooses another factor, and never read the metered value back in the middle of a frame. Add a test that renders the new pass at two forced pre-exposures and requires equal pixels. Run the suite above and the feature test before the commit; [Light units and exposure](../light/units-exposure.md) and [Measuring light](../light/measuring-light.md) cover what the value views show.

## Summary

- A power-of-two pre-exposure moves only the exponent of every stored number, so a change of P changes no pixel while no value overflows or becomes subnormal; another factor rounds and changes the image.
- Strata chooses the power of two nearest the metered exposure factor minus 2 stops, within 2 to the power of plus or minus 24. It steps only when the current value is more than one stop off.
- The metering comes back through a ring of readbacks frames later; epochs discard readbacks that describe another stretch, and the settled flag tells captures when to stop waiting.
- Writers multiply by `TemporalParams.y`; the histogram, bloom, temporal weights and tone map divide it out; the history is multiplied by P over the previous P.

## Check yourself

1. Why does a step from P equal to 8 to P equal to 16 change no pixel?

   - A. The tone map hides all differences.
   - B. Multiplying by a power of two changes only the exponent, so the stored values and what the readers recover are the same, bit for bit.
   - C. The history is thrown away at every step.

   :::answer{tests="power-of-two"}
   B. A is wrong: the tone map is exact here and hides nothing, which is why the test compares pixels. C is wrong: the history is kept and multiplied by P over the previous P.
   :::

2. Frame 40 is drawn with P equal to 2 to the power of -12. A readback of the current epoch reports an exposure factor of 2 to the power of -13.4. Does P step, and to what?

   :::answer{tests="choose-step"}
   The target is -13.4 - 2 = -15.4. The distance from -12 is 3.4, more than 1, so P steps to the power of two nearest, 2 to the power of -15. Settled turns false. An exposure factor of 2 to the power of -10.6 would give a target of -12.6, only 0.6 from -12, and P would stay.
   :::

3. Why does Strata not wait for the metered exposure inside the frame that needs it?

   - A. The metering is not known on the GPU.
   - B. The wait stalls the frame; a value from frames earlier is enough, because P need be only within a stop of the target.
   - C. The CPU cannot read a buffer.

   :::answer{tests="async-epoch"}
   B. A is wrong: the GPU computes the metering in the exposure pass. C is wrong: the ring of readbacks reads a buffer, only later.
   :::

4. The user disables automatic exposure for ten seconds and enables it again. What stops the readbacks recorded before the pause from steering P?

   :::answer{tests="async-epoch"}
   Leaving automatic exposure starts a new epoch, and each readback keeps the epoch of the frame that recorded it. Only readbacks of the current epoch are read, so the old ones are ignored.
   :::

5. A new pass blends fog into the HDR image after the forward pass. Does it multiply by P, divide by P, or neither?

   :::answer{tests="writers-readers"}
   The new pass multiplies. The pass writes the HDR image, and the image holds luminance times P. A pass that only reads the image to compute something in real units divides instead.
   :::

## Exercises

1. **Basic.** Run `sketches/image-pre-exposure-exact.cpp` and explain its result. What do the two powers of two have in common that 10 lacks?

   :::answer[Worked solution]{tests="power-of-two" solution="sketches/image-pre-exposure-exact.cpp"}
   The sketch stores a luminance times P, then multiplies by the exposure factor over P, as the tone map does. For 8 and 16 every one of 100,000 values is equal to the value at P equal to 1, because the product by a power of two and its inverse are exact. For 10, the inverse of 10 is not exact, so some values differ in the last bit.

   ```cpp sketch="image-pre-exposure-exact.cpp"
   #include <cstdint>
   #include <cstdio>

   // What the display sees of a luminance: stored at the pre-exposure, then divided out with the multiplier.
   float Displayed(float luminance, float preExposure, float multiplier)
   {
   	const float stored = luminance * preExposure;
   	return stored * (multiplier * (1.0f / preExposure));
   }

   int main()
   {
   	const float multiplier = 0.000013f;
   	const float factors[] = { 8.0f, 16.0f, 10.0f };
   	for (const float factor : factors)
   	{
   		uint32_t state = 12345;
   		uint32_t different = 0;
   		for (int sample = 0; sample < 100000; sample++)
   		{
   			state = state * 1664525u + 1013904223u;
   			const float luminance = 0.01f + static_cast<float>(state >> 8) * 0.01f;
   			different += Displayed(luminance, factor, multiplier) != Displayed(luminance, 1.0f, multiplier) ? 1u : 0u;
   		}
   		std::printf("pre-exposure %4.0f: %u of 100000 pixels differ from pre-exposure 1\n", factor, different);
   	}
   	return 0;
   }
   ```

   ```text output-of="image-pre-exposure-exact.cpp"
   pre-exposure    8: 0 of 100000 pixels differ from pre-exposure 1
   pre-exposure   16: 0 of 100000 pixels differ from pre-exposure 1
   pre-exposure   10: 32276 of 100000 pixels differ from pre-exposure 1
   ```

   1. **Line 7:** The pixel stores the luminance times the pre-exposure.
   2. **Line 8:** The display multiplies by the exposure factor times the inverse, as the tone map does.
   3. **Line 14:** Two powers of two and the number 10 are tried.
   4. **Line 23:** Each value is compared bit for bit with the same value at a pre-exposure of 1.
   :::

2. **Medium.** The metered target jumps between -16.4 and -16.6 on alternate frames, around the boundary between 2 to the power of -16 and -17 (target -16.5). How many steps happen with the one-stop dead band, and how many if P always followed the rounding?

   :::answer[Worked solution]{tests="choose-step"}
   With the dead band, the first readback steps P to -16 (from 0 it is more than one stop off). Every later target is within 0.6 of -16, so there are no more steps. Without the dead band, P would take the rounding of each target, -16 for -16.4 and -17 for -16.6, and step on every readback. Every step makes the settled flag false, so captures would wait without end.
   :::

3. **Hard.** Trace it yourself: find every pass that multiplies by or divides out the pre-exposure, and the place where the CPU writes it. Which list does a new bloom-like pass that reads the HDR image join?

   :::answer[Worked solution]{tests="writers-readers"}
   Search the engine for `InversePreExposure` and `TemporalParams.y`. The CPU writes `TemporalParams` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`, with `m_PreExposure` in the `y` component. The readers that divide are `Strata/shaders/PostProcess/Histogram.comp.slang`, `Bloom.comp.slang`, `TAA.comp.slang`, `Tonemap.frag.slang` and `Strata/shaders/Include/LightingView.slang`, fed in `Strata/src/Strata/Renderer/SceneRendererPost.cpp` and `SceneRenderer.cpp`. The writers that multiply are `Strata/shaders/Scene/Forward.frag.slang` and `Skybox.frag.slang`, and the global illumination's debug views, `Strata/shaders/GI/ProbeView.frag.slang` and `VoxelView.frag.slang`, multiply their light by P too. A bloom-like pass that reads the image joins the readers: it takes `InversePreExposure` in its constants.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `GetPreExposureFor`, `StartPreExposureEpoch`, `ChoosePreExposure`, `ResolveTemporal`.
- `Strata/src/Strata/Renderer/SceneRendererPost.cpp`: the readback into the ring and `SubmitExposureReadback`.
- `Strata/src/Strata/Renderer/SceneRenderer.h`: `c_PreExposureHeadroomStops`, `c_MaxPreExposureStops`, `SceneRenderOptions::PreExposure`, `SceneRendererStats::PreExposure`.
- `Strata/shaders/Scene/Forward.frag.slang`, `Strata/shaders/Scene/Skybox.frag.slang`: the writers.
- `Strata/shaders/PostProcess/Histogram.comp.slang`, `Bloom.comp.slang`, `TAA.comp.slang`, `Tonemap.frag.slang`, `Strata/shaders/Include/LightingView.slang`: the readers.
- `StrataTests/src/Renderer/GPUScenePostProcessTests.cpp`: the suite `GPU.SceneRenderer.PostProcess`.
- `StrataEditor/src/Editor/EditorViewportCommands.cpp`: the capture's wait, `c_MaxCaptureExposureFrames`.

## Further reading

- Sebastien Lagarde and Charles de Rousiers, "Moving Frostbite to Physically Based Rendering" (SIGGRAPH 2014 course notes): the previous-frame exposure scale in a production engine; intermediate.
- Wikipedia, "Half-precision floating-point format": the range and precision of the 16-bit format; beginner.
