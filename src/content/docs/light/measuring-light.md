---
id: light/measuring-light
title: "Measuring light: the debug views and their statistics"
description: "How Strata turns a frame into numbers: seven lighting views, histograms counted on the GPU, and statistics that come back frames later."
kind: internals
size: M
tracks: [E]
needs: [light/brdf, gpu/readback-timing, gpu/debug-drawing]
time: 65
learn:
  - id: read-views
    text: explain what each lighting view shows and which one finds a base color that is too dark or too bright
  - id: ev-bands
    text: compute the EV100, the histogram bin and the color band of a luminance
  - id: stats-flow
    text: trace how a frame's statistics travel from the statistics pass through the ring of readbacks to a command's result
  - id: value-views
    text: explain why the views of values are written without the pre-exposure
  - id: add-view
    text: name every place a new lighting view must change
since: 0.7.0
status: final
---

A lighting view shows light as numbers. It replaces the lit picture with a picture of one quantity, such as the light alone or the :term[base color]{id=albedo} alone. It also counts every pixel, so that a program can ask how bright a scene is and get a number back. It does not teach what exposure value (EV100) means, the shadows view, the views of ambient occlusion and global illumination, or the white furnace test.

## The problem and how engines solve it

You light a room and look at it on your monitor. It seems fine. On another monitor, or in a bright office, it looks too dark. Your eyes adapt to what they see, and a screen has a small range, so a person is a poor meter.

A second trap hides behind the first. A wall looks too bright, so you lower the camera's exposure until it looks right. The wall now looks fine, but every other surface went dark, and the real fault stays: the wall's base color was 0.95, which no real paint reaches. The fix for a wrong material is a new material, not a new exposure.

Engines meet this with four kinds of measuring tool.

- A **false-color** picture paints each pixel with a color that stands for its :term[luminance]{id=luminance}, so equal colors mean equal light and nobody has to judge brightness.
- An **albedo check** shows the base colors alone and marks those no real material has. Real surfaces reflect between about 3 % (charcoal) and 85 % (fresh snow) of their light.
- A **furnace test** puts an object in a room of uniform light and checks that it neither gains nor loses energy. It checks the shading code, not a scene: the [energy page](../light/energy.md) teaches it.
- A **density view** colors each pixel by how much detail a texture or a shadow map gives it. The shadows view does that for shadows.

A picture alone is still read by eye, so a good engine also reports numbers: the median, the dark end and the bright end. The numbers come from the :term[graphics processing unit]{id=gpu} (GPU), and the :term[central processing unit]{id=processor} (CPU) cannot wait for them. A view that changes the shading also adds a branch to the most expensive :term[shader]{id=shader} of the frame.

Strata chose the first two tools and gave them numbers. Seven views replace the lit image (Lighting, ambient occlusion, Indirect, Specular, Diffuse, Luminance, Albedo), and a compute pass counts the frame into histograms. The numbers arrive frames later through a ring of readbacks, as [readbacks that never wait](../gpu/readback-timing.md) describe. Each is one of the viewport's debug views, which the [debugging page](../gpu/debugging.md) lists.

## The map

The :term[renderer]{id=renderer} picks a view for each frame. The forward shader reads it and shades differently. An :term[overlay]{id=overlay-gpu} then draws over the finished image, and a compute pass counts. The count returns to the CPU later, and the editor draws it or a command reports it.

```mermaid caption="One frame with a lighting view: the choice of view, the forward shader, the counting pass and the overlay on the GPU, then the ring of readbacks and the two readers on the CPU." alt="A flow diagram. The viewport's debug view becomes a view number in the frame constants, and the forward shader shades with it. A counting pass reads the finished image and the depth and fills a statistics buffer, and a drawing pass replaces the image with the view's colors. The statistics buffer is copied into one of three readbacks. Later the renderer turns the newest finished readback into statistics, which the editor's legend and a capture command both read."
flowchart LR
	chip["debug view chip or capture command"] --> option["SceneRenderOptions::LightingView"]
	option --> constants["frame constants: MaterialParams.y"]
	constants --> forward["forward shader: Forward.frag"]
	forward --> hdr["HDR target and depth"]
	hdr --> stats["LightingViewStats.comp: histograms"]
	hdr --> overlay["LightingView.frag: colors"]
	stats --> ring["ring of 3 readbacks"]
	ring --> resolve["ResolveLightingViewStats"]
	resolve --> legend["editor legend"]
	resolve --> command["viewport.capture: debugView.lighting"]
```

Three files own most of the work. `Strata/src/Strata/Renderer/SceneRenderer.h` declares the enum, the colors and the statistics. `Strata/src/Strata/Renderer/SceneRendererLightingView.cpp` records the two passes and turns readbacks into statistics. The shaders `Strata/shaders/Effects/LightingViewStats.comp.slang` and `Strata/shaders/Overlay/LightingView.frag.slang` count and draw. The :term[main thread]{id=main-thread} records the commands, and the GPU does the counting.

## The contract

A caller picks a view with `SceneRenderOptions::LightingView` and reads the result with `SceneRenderer::GetLightingViewStats`. The rules that follow keep the numbers honest.

- **A value is never blended with another frame.** The first frame of a view resets the temporal history, and the overlay reads the frame's own target, never the history.
- **Value views are written without pre-exposure.** Occlusion, albedo, the open share and a cluster's count of lights are not light. The forward shader writes them without the pre-exposure (a power of two that scales the lit image), fog or what glass transmits.
- **Lighting, Indirect, Specular and Diffuse go through the scene's exposure.** They show light, so the image keeps the brightness the scene has.
- **Statistics name their frame.** Each set carries the number of the render it belongs to, and a change of view discards the old set.
- **Nothing waits.** A frame whose readback slot is still busy measures nothing, and the older statistics stay.

:::rule[Read GPU data back without blocking the frame]
`AGENTS.md` says GPU data is read back through polled readbacks, and the blocking read is for tests and tools only. The statistics follow it with three buffer readbacks, polled every frame. A wait would stall the frame for the length of the GPU's queue, and a viewport with a legend would freeze.
:::

## A toy version

The toy takes ten pixels and does on the CPU what the statistics pass does on the GPU. It turns each luminance into EV100, adds the pixel to a quarter-step bin and reads three percentiles; the row of bins is a histogram. EV100 is a scale of brightness on which one step, one exposure value (EV), doubles the light. A **percentile** is the value below which a given share of the counted pixels lie, so the 50th percentile is the median. Look at the percentile walk.

```cpp sketch="light-measuring-light-toy.cpp"
// Counts the luminance of ten pixels into quarter-EV bins and reads percentiles from the bins.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>

constexpr float c_MinEV100 = -8.0f;
constexpr float c_BinsPerEV = 4.0f;
constexpr uint32_t c_BinCount = 128;
constexpr float c_FirstBandEV100 = 5.0f;

// EV100 of a luminance in nits; black reads as a very dark value instead of minus infinity.
float GetEV100(float nits)
{
	return std::log2(std::max(nits, std::exp2(-10.0f))) + 3.0f;
}

// The value below which `fraction` of the counts lie, linear inside the bin it falls in.
float GetPercentile(const std::array<uint32_t, c_BinCount>& bins, float fraction, uint32_t total)
{
	const float target = fraction * static_cast<float>(total);
	uint32_t below = 0;
	for (uint32_t index = 0; index < c_BinCount; index++)
	{
		if (bins[index] == 0)
			continue;
		if (static_cast<float>(below + bins[index]) >= target)
		{
			const float within = (target - static_cast<float>(below)) / static_cast<float>(bins[index]);
			return c_MinEV100 + (static_cast<float>(index) + within) / c_BinsPerEV;
		}
		below += bins[index];
	}
	return c_MinEV100 + static_cast<float>(c_BinCount) / c_BinsPerEV;
}

int main()
{
	const std::array<float, 10> pixels = { 4.0f, 6.0f, 8.0f, 10.0f, 12.0f, 16.0f, 40.0f, 100.0f, 1000.0f, 16000.0f };
	std::array<uint32_t, c_BinCount> bins = {};
	for (float nits : pixels)
	{
		const float ev = GetEV100(nits);
		const uint32_t bin = static_cast<uint32_t>(std::clamp((ev - c_MinEV100) * c_BinsPerEV, 0.0f, static_cast<float>(c_BinCount - 1)));
		const int band = static_cast<int>(std::floor(ev - c_FirstBandEV100));
		bins[bin]++;
		std::printf("%7.0f nits: EV100 %6.3f, bin %3u, band %2d\n", nits, ev, bin, band);
	}
	std::printf("p05 %.3f, p50 %.3f, p95 %.3f\n", GetPercentile(bins, 0.05f, 10), GetPercentile(bins, 0.5f, 10),
		GetPercentile(bins, 0.95f, 10));
	return 0;
}
```

```text output-of="light-measuring-light-toy.cpp"
      4 nits: EV100  5.000, bin  52, band  0
      6 nits: EV100  5.585, bin  54, band  0
      8 nits: EV100  6.000, bin  56, band  1
     10 nits: EV100  6.322, bin  57, band  1
     12 nits: EV100  6.585, bin  58, band  1
     16 nits: EV100  7.000, bin  60, band  2
     40 nits: EV100  8.322, bin  65, band  3
    100 nits: EV100  9.644, bin  70, band  4
   1000 nits: EV100 12.966, bin  83, band  7
  16000 nits: EV100 16.966, bin  99, band 11
p05 5.125, p50 6.750, p95 16.875
```

1. **Line 16:** the luminance in :term[nits]{id=lux} becomes EV100, with a floor so that black reads as a very dark value and not as minus infinity.
2. **Lines 28-31:** the first bin where the running count reaches the target holds the percentile, and the position inside that bin is linear.
3. **Lines 45-46:** a pixel's bin comes from its EV100 in quarter steps, and its color band from whole steps above 5.

:::example[Ten pixels by hand]
Take the pixel of 100 nits. Its EV100 is $\log_2(100) + 3 = 6.644 + 3 = 9.644$. The bin position is $(9.644 + 8) \times 4 = 70.6$, so the pixel is counted in bin 70, which covers EV100 9.5 to 9.75. Its band is $\lfloor 9.644 - 5 \rfloor = 4$, the fifth color of the legend.

For the median of ten pixels the target is 5 counts. Four pixels lie below the bin of 12 nits (bin 58, EV100 6.5 to 6.75), and that bin holds one, so the target falls at the bin's top edge: 6.75. The pixel's true EV100 is 6.585, so the bin's error is below a quarter of a step.
:::

The real code differs in four ways. The counting runs on every pixel in parallel, and the result crosses from the GPU to the CPU without a wait. The pixels of the sky and of surfaces count apart. The value views count something other than light.

## The real code

### The views

The enum lists every view, and its order is part of the contract: the shader constants of `Strata/shaders/Include/Scene.slang` follow the same order.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.h#L346-L361"
enum class SceneLightingView : uint8_t
{
	None = 0,
	Lighting,         // Every lit surface shaded white (albedo 1, metallic and roughness kept, no emission), through the scene's exposure
	AmbientOcclusion, // The occlusion the forward pass applies to indirect light (material x screen), as gray
	Indirect,         // Only the indirect light (sky, probes, screen-space reflections), through the scene's exposure
	Luminance,        // The scene's luminance as EV100 bands (log2 nits + 3)
	Albedo,           // The base color, with values outside [RenderData::c_AlbedoLow, c_AlbedoHigh] marked
	Voxels,           // Global illumination's voxels as the GI sees the scene, lit (GI/VoxelView.frag over the lit image)
	GlobalIllumination, // Global illumination's diffuse light on white surfaces (the field, today's light beyond it), through the scene's exposure
	OpenShare,        // The cosine-weighted share of the sky each surface sees through the world, as gray (1 beyond the field)
	Probes,           // Global illumination's first cascade of probes over the lit image (GI/ProbeView.frag): live ones lit, dead ones red
	Specular,         // Only the specular light (the lights' highlights, image light's reflections), through the scene's exposure
	Diffuse,          // Only the diffuse light (the lights' and image light's, global illumination's field), through the scene's exposure
	Clusters          // The lights the pixel's light cluster lists (what its shading walks), as bands of counts
};
```

1. **Line 348:** `None` is zero, the lit image, and nothing stores these numbers on disk.
2. **Lines 349-353:** five views this page teaches, in the order of the shader constants.
3. **Lines 354-357:** the four views of global illumination, taught on the [cascades page](../indirect/gi-cascades.md).
4. **Lines 358-359:** the two views of one kind of light, taught here too.
5. **Line 360:** `Clusters` counts lights per cluster, not light, for the [many lights page](many-lights.md).

The seven views differ in what the forward shader writes and what the overlay does with it.

- **Lighting:** every lit surface is white, with metallic and roughness kept and no emission. It shows how the scene's light falls, whatever the materials are.
- **Ambient occlusion:** the share of ambient light that nearby geometry lets through, as gray. The [ambient occlusion page](../indirect/ao.md) teaches it.
- **Indirect:** only light that did not come straight from a light: the sky, probes and screen-space reflections. The shader zeroes the direct sum and the emission. The [indirect light page](../indirect/problem.md) says why that light is hard.
- **Specular and Diffuse:** one kind of light alone, without emission, fog or what glass transmits. Specular keeps the lights' highlights, a clear coat's too, and the reflections of sky and probes. Diffuse keeps the light surfaces scatter, with the field of global illumination. The two do not add up to the lit image: the sky shows in both, and each view sets its own exposure.
- **Luminance:** the lit image, drawn over by the overlay in color bands one EV wide. The first band starts at 5 (4 nits, a dim interior) and the last ends at 17 (16,000 nits, snow in the sun). Pixels beyond either end keep the end color.
- **Albedo:** the base color without light. Where its luminance is below 0.03 the overlay blends in blue at 0.7. Above 0.85 it blends in red in diagonal stripes, so the mark cannot pass for a red surface.

The bands use $\mathrm{EV100} = \log_2(L) + 3$, where $L$ is luminance in nits. The lit image carries the pre-exposure, so the overlay and the counter divide it out first.

A worked example: a wall of albedo 0.5 in full sun, 100,000 lux, has $0.5 \times 100000 / \pi = 15{,}900$ nits, so EV100 16.96 and the top band. The same wall in a room lit by 200 lux has $0.5 \times 200 / \pi = 31.8$ nits, EV100 7.99 and band 2. About nine steps, a factor of 500, separate them. The Luminance view shows that as white beside blue.

::figure{id=views-lit}

::figure{id=views-lighting}

::figure{id=views-indirect}

::figure{id=views-luminance}

::figure{id=views-albedo}

::figure{id=albedo-cubes}

### Why the value views skip the pre-exposure

The lit image is stored multiplied by a pre-exposure that keeps a bright scene inside the :term[half-float]{id=half-float} range. A scene lit by the sun can run at about $2^{-19}$. An albedo of 0.03 then becomes $0.03 \times 2^{-19} = 5.7 \times 10^{-8}$, below the smallest normal half-float number, $6.1 \times 10^{-5}$, and even below the smallest :term[subnormal]{id=subnormal-number} one, $6.0 \times 10^{-8}$. It rounds to that number, and so does an albedo of 0.02. The value views write their numbers as they are, so the Albedo view can tell 0.03 from 0.02.

While a value view runs, the pre-exposure keeps its value. When the view ends, the exposure jumps back at once instead of adapting from numbers that were not light.

### Counting every pixel

The counting shader runs in groups of 16 by 16 pixels. Each group fills its own histograms in memory its threads share, with atomic adds: additions many threads make to one number without losing any. It then adds them into the buffer in one pass, so most of the contention stays inside the group. A pixel is a surface when its depth is above zero, since the engine's depth runs from 1 at the :term[near plane]{id=near-plane} to 0 at the :term[far plane]{id=far-plane}.

```slang src="Strata/shaders/Effects/LightingViewStats.comp.slang#L37-L63"
int2 pixel = int2(st_GlobalInvocationID.xy);
int2 size = int2(u_Frame.ViewportSize.xy);
if (pixel.x < size.x && pixel.y < size.y)
{
	float3 hdr = u_HDR.Load(int3(pixel, 0)).rgb;
	bool surface = u_Depth.Load(int3(pixel, 0)).r > 0.0;
	InterlockedAdd(s_Counts[surface ? 0u : 1u], 1u);
	if (IsValueView(u_LightingView.View))
	{
		if (surface)
		{
			float value = u_LightingView.View == ST_LIGHTING_VIEW_ALBEDO ? Luminance(hdr) : hdr.r;
			uint bin = uint(clamp(value * float(ST_LIGHTING_VIEW_VALUE_BINS), 0.0, float(ST_LIGHTING_VIEW_VALUE_BINS - 1u)));
			InterlockedAdd(s_Value[bin], 1u);
			if (u_LightingView.View == ST_LIGHTING_VIEW_ALBEDO && value < ST_ALBEDO_LOW)
				InterlockedAdd(s_Counts[2], 1u);
			else if (u_LightingView.View == ST_LIGHTING_VIEW_ALBEDO && value > ST_ALBEDO_HIGH)
				InterlockedAdd(s_Counts[3], 1u);
		}
	}
	else
	{
		float position = (GetPixelEV100(hdr) - ST_LIGHTING_VIEW_MIN_EV100) * ST_LIGHTING_VIEW_BINS_PER_EV;
		uint bin = uint(clamp(position, 0.0, float(ST_LIGHTING_VIEW_EV_BINS - 1u)));
		InterlockedAdd(s_EV[(surface ? 0u : ST_LIGHTING_VIEW_EV_BINS) + bin], 1u);
	}
}
```

1. **Line 42:** a depth above zero marks a surface; the sky and the clear color count as background.
2. **Line 43:** every pixel adds to the count of surfaces or the count of background.
3. **Lines 48-49:** a value view counts the albedo's luminance, or the red channel of the occlusion, the open share or the cluster's share of lights, into 64 bins between 0 and 1.
4. **Lines 59-61:** the other views count EV100 into 128 quarter-step bins from -8 to 24, surfaces in the first half and background in the second.

### The ring of readbacks

The buffer is cleared, filled and copied into one of three readbacks. A frame whose slot is still busy skips the measure, so no frame waits.

```cpp src="Strata/src/Strata/Renderer/SceneRendererLightingView.cpp#L214-L234"
// The statistics: a readback whose earlier copy is still under way is left to finish, and the frame measures nothing.
LightingViewReadback& readback = m_LightingViewReadbacks[m_LightingViewReadbackIndex];
if (!readback.Readback->IsPending() || readback.Readback->IsReady())
{
	commandList->clearBufferUInt(m_LightingStatsBuffer, 0);
	nvrhi::ComputeState state;
	state.pipeline = m_LightingStatsPipeline;
	state.bindings = { m_LightingStatsBindingSet };
	commandList->setComputeState(state);
	commandList->setPushConstants(&parameters, sizeof(parameters));
	commandList->dispatch((m_ViewportSize.x + c_StatsGroupSize - 1) / c_StatsGroupSize, (m_ViewportSize.y + c_StatsGroupSize - 1) / c_StatsGroupSize, 1);
	readback.Readback->Record(commandList, m_LightingStatsBuffer, 0, sizeof(RenderData::LightingViewStatsData));
	readback.Render = m_RenderCount + 1;
	readback.View = view;
	// The directional light at the ground (its color is multiplied by the atmosphere's transmittance) on a surface facing
	// up, before shadows.
	readback.SunIlluminance = frame.DirectionalLightDirection.w > 0.0f
		? std::max(GetLuminance(glm::vec3(frame.DirectionalLightColor)), 0.0f) * std::max(-frame.DirectionalLightDirection.y, 0.0f)
		: 0.0f;
	m_LightingViewReadbackRecorded = true;
}
```

1. **Line 216:** a slot whose earlier copy has not finished is left alone, and this frame measures nothing.
2. **Lines 224-225:** one thread per pixel, in groups of 16 by 16, then the copy into the slot.
3. **Line 226:** the slot remembers which frame it measured.
4. **Lines 230-232:** the sun's lux come from the CPU, which has the light's color and direction already.

On flat ground facing up, the sun gives its color's luminance times the :term[sine]{id=sine} of its elevation, in lux. The sky gives $\pi$ times the :term[irradiance]{id=irradiance} map's value in the up direction, times the sky's intensity. The factor $\pi$ is there because the map stores irradiance divided by $\pi$. The [sky page](../light/sky.md) teaches the sky as a light.

### Turning counts into statistics

Each frame the renderer searches for the newest finished readback of the current view. It reads the buffer and turns the histograms into percentiles with the same walk as the toy.

```cpp src="Strata/src/Strata/Renderer/SceneRendererLightingView.cpp#L285-L313" from="LightingViewStats stats;" to="m_LightingViewStats = stats;" symbol="SceneRenderer::ResolveLightingViewStats"
LightingViewStats stats;
stats.View = newest->View;
stats.Render = newest->Render;
const uint64_t pixels = static_cast<uint64_t>(data.SurfacePixels) + data.BackgroundPixels;
stats.SurfaceShare = pixels > 0 ? static_cast<float>(static_cast<double>(data.SurfacePixels) / static_cast<double>(pixels)) : 0.0f;
const float evWidth = 1.0f / RenderData::c_LightingViewBinsPerEV;
const float valueWidth = 1.0f / static_cast<float>(RenderData::c_LightingViewValueBins);
if (IsLightingValueView(stats.View))
{
	stats.ValueMedian = GetPercentile(data.Value, 0.5f, 0.0f, valueWidth);
	stats.ValueP05 = GetPercentile(data.Value, 0.05f, 0.0f, valueWidth);
	if (stats.View == SceneLightingView::Albedo && data.SurfacePixels > 0)
	{
		stats.BelowRangeShare = static_cast<float>(static_cast<double>(data.BelowRange) / data.SurfacePixels);
		stats.AboveRangeShare = static_cast<float>(static_cast<double>(data.AboveRange) / data.SurfacePixels);
	}
}
else
{
	stats.SurfaceEV100 = glm::vec3(GetPercentile(data.SurfaceEV, 0.05f, RenderData::c_LightingViewMinEV100, evWidth),
		GetPercentile(data.SurfaceEV, 0.5f, RenderData::c_LightingViewMinEV100, evWidth),
		GetPercentile(data.SurfaceEV, 0.95f, RenderData::c_LightingViewMinEV100, evWidth));
	stats.BackgroundEV100 = GetPercentile(data.BackgroundEV, 0.5f, RenderData::c_LightingViewMinEV100, evWidth);
}
const float sky = glm::pi<float>() * GetLuminance(glm::vec3(data.SkyIrradiance));
stats.SunIlluminance = newest->SunIlluminance;
stats.SkyIlluminance = std::isfinite(sky) ? std::max(sky, 0.0f) : 0.0f;
stats.SunToSkyRatio = stats.SunIlluminance > 0.0f && stats.SkyIlluminance > 0.0f ? stats.SunIlluminance / stats.SkyIlluminance : 0.0f;
m_LightingViewStats = stats;
```

1. **Line 287:** the statistics keep the number of the frame they measured.
2. **Lines 292-295:** a value view reports the median and the 5th percentile of its values.
3. **Lines 296-299:** the Albedo view also reports the shares of surface pixels below 0.03 and above 0.85.
4. **Lines 304-307:** the light views report EV100 at the 5th, 50th and 95th percentile of surfaces, and the median of the background.
What comes back is a `LightingViewStats`. Fields a view does not measure hold :term[NaN]{id=nan}.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.h#L389-L412"
// What a lighting view measured in one frame, read back frames later (a readback, never waited for:
// SceneRenderer::GetLightingViewStats).
struct LightingViewStats
{
	SceneLightingView View = SceneLightingView::None;
	uint64_t Render = 0;       // The renderer's frame the statistics belong to (its GetRenderCount once that frame was rendered)
	float SurfaceShare = 0.0f; // Share of the image's pixels that show a surface (a depth was drawn)
	// Lighting, Indirect, Luminance: EV100 of the surfaces' pixels at the 5th, 50th and 95th percentile, and the median of the
	// background's (the sky or the clear color); NaN where there are no such pixels or the view does not measure them.
	glm::vec3 SurfaceEV100 = glm::vec3(std::numeric_limits<float>::quiet_NaN());
	float BackgroundEV100 = std::numeric_limits<float>::quiet_NaN();
	// AmbientOcclusion and Albedo (the albedo's luminance): the surfaces' median and 5th percentile; Albedo: the shares of the
	// surface pixels below RenderData::c_AlbedoLow and above c_AlbedoHigh.
	float ValueMedian = std::numeric_limits<float>::quiet_NaN();
	float ValueP05 = std::numeric_limits<float>::quiet_NaN();
	float BelowRangeShare = 0.0f;
	float AboveRangeShare = 0.0f;
	// Every view: illuminance in lux on a horizontal surface from the directional light at the ground (after the atmosphere,
	// before shadows) and from the sky (pi times the irradiance map at +Y times the sky's intensity, or pi times the constant
	// ambient without an environment), and their ratio (0 without either).
	float SunIlluminance = 0.0f;
	float SkyIlluminance = 0.0f;
	float SunToSkyRatio = 0.0f;
};
```

1. **Line 394:** the number of the render the set belongs to.
2. **Lines 398-399:** the light views' percentiles and the background's median.
3. **Lines 402-405:** the value views' median and 5th percentile, and the Albedo view's shares out of range.
4. **Lines 409-411:** the sun and the sky in lux on flat ground, and their ratio, which is 0 when either is missing.

:::example[The sun and the sky of a test scene]
The test suite `GPU.SceneRenderer.LightingViews` builds a sun of 3 lux at 55 degrees over a procedural sky. On flat ground the sun gives $3 \times \sin 55^\circ = 2.46$ lux. The sky's cosine-weighted mean :term[radiance]{id=radiance} is 0.321 nits, so it gives $\pi \times 0.321 = 1.01$ lux. The ratio is $2.46 / 1.01 \approx 2.44$: about two and a half to one.
:::

### Reading the numbers

In the editor, the Scene view's debug view chip lists the views, and the legend beside the image shows the bands or the shares of marked albedo. An agent changes the view with one command, run as the [commands page](../editor/commands.md) teaches.

```json
{ "command": "viewport.setSettings", "parameters": { "debugView": "luminance" } }
```

The next command takes a picture with the Albedo view and returns the numbers with it.

```json
{ "command": "viewport.capture", "parameters": { "debugView": "albedo" } }
```

The result holds `debugView.lighting`: `sunToSkyRatio` with its lux values `sunIlluminance` and `skyIlluminance`, then `surfaceShare`, `backgroundEv100`, `surfaceEv100` (`p05`, `p50`, `p95`), `value` (`median`, `p05`), `belowRangeShare` and `aboveRangeShare`. A capture waits for its own frame's statistics. A value the view does not measure is null, and where the statistics did not arrive in time `debugView.lighting` is null and `lightingPending` is true.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Read the whole image back and count on the CPU | Simple tools and tests | No counting shader | A copy of many MB every frame, and a CPU loop over millions of pixels |
| Wait for the GPU so the numbers match the frame | Blocking tests and tools | Statistics of the frame it drew | A stalled frame for the length of the GPU's queue |
| An average only, from a chain of smaller images | Automatic exposure in many engines | Almost no code | The dark and bright ends, which a lighting audit needs |
| Separate debug materials | Some look-development modes | No branch in the lit shader | A second set of materials that can drift from the real ones |

## How it is tested

The suite `GPU.SceneRenderer.LightingViews` in `StrataTests/src/Renderer/GPUSceneLightingViewTests.cpp` renders small scenes through both draw paths and checks pixels and statistics. The luminance case renders a quad of 100 nits, expects a median EV100 within a quarter step of 9.64, and compares the pixel with the legend's color for its band. The albedo case checks that colors outside 0.03 to 0.85 are marked. Other cases cover the occlusion, indirect and white views, a frame without a view, a change of view that resets the temporal history and keeps the exposure, and the sun to sky ratio. Run it with `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.LightingViews`.

## Changing it safely

To add a view you change the enum, the shader constants, the forward shader's branch, the overlay, the editor's names and a test. The checks that apply:

- **Keep the enum in the order of the shader constants.** The shader reads the numbers, and a disagreement shows the wrong view with no error.
- **Keep value views without pre-exposure.** A view of data that is not light goes into `IsLightingValueView`, in the forward shader and in C++, and into the counting shader's `IsValueView`. Otherwise its values drown in half-float precision.
- **Draw nothing that waits.** The overlay reads the frame's own target, and the statistics come back through the ring.
- **Name the view everywhere an agent can pick it.** The chip, the command's schema and its error message all list the views.

## Summary

- A lighting view replaces the lit image with one quantity (light on white, indirect light, one kind of light, luminance bands, base color) and a compute pass counts every pixel.
- EV100 is $\log_2$ of the luminance in nits plus 3; quarter-step bins run from -8 to 24, and the color bands are one step wide from 5 to 17.
- Statistics travel from the counting shader's buffer through a ring of three readbacks and `ResolveLightingViewStats` to `LightingViewStats`, and `viewport.capture` reports them as `debugView.lighting`.
- Value views skip the pre-exposure because a pre-exposure near $2^{-19}$ turns an albedo of 0.03 into a subnormal half-float.
- A new view changes the enum, the shader constants, the forward branch, the overlay, the names and a test.

## Check yourself

1. A pixel has a luminance of 250 nits. Compute its EV100, its bin and its band in the Luminance view.

   :::answer{tests="ev-bands"}
   EV100 is $\log_2(250) + 3 = 7.966 + 3 = 10.966$. The bin position is $(10.966 + 8) \times 4 = 75.9$, so bin 75. The band is $\lfloor 10.966 - 5 \rfloor = 5$.
   :::

2. A scene looks too bright. The Luminance view shows the walls in the top band, and the Albedo view puts red stripes on them. Which is the fault: (a) the exposure is too high, (b) the walls' base color is above 0.85, or (c) the sun is too weak?

   :::answer{tests="read-views"}
   (b). The red stripes mean the base color's luminance is above 0.85, which no real paint reaches. (a) would brighten every surface and leave the Albedo view without marks, since that view ignores exposure. (c) points the wrong way: a weak sun darkens a scene.
   :::

3. The pre-exposure is $2^{-19}$. What would an albedo of 0.03 become if it were written with it, and why does that matter?

   :::answer{tests="value-views"}
   $0.03 \times 2^{-19} \approx 5.7 \times 10^{-8}$, below even the smallest subnormal half-float, so it rounds to $6.0 \times 10^{-8}$, as 0.02 does. The view could not tell 0.03 from 0.02, so it is written without the pre-exposure.
   :::

4. A frame is recorded while the readback slot it should use is still being copied. What does the frame do, and what do the statistics show?

   :::answer{tests="stats-flow"}
   The frame measures nothing: it records no counting pass and no copy, and the slot finishes. The statistics keep the last resolved set, whose `Render` number names an older frame.
   :::

5. A new view is added to the enum before `Albedo`, and the shader constants are not changed. What does a user see?

   :::answer{tests="add-view"}
   The shader reads the view's number, so the new view shows the picture of the constant with its number, and `Albedo` shows the next one. Nothing fails, since the numbers are stored nowhere that a check could compare. The enum must follow the order of the constants.
   :::

## Exercises

1. **Basic.** Audit three materials in the Albedo view by hand: rough copper (0.955, 0.638, 0.538), polished gold (1.0, 0.766, 0.336) and wet asphalt (0.02, 0.02, 0.022), all linear base colors. Predict which the view marks, then write a program that checks it.

   :::answer[Worked solution]{tests="read-views" solution="sketches/light-measuring-light-audit.cpp"}
   The view tests the luminance of the base color, with the weights 0.2126, 0.7152 and 0.0722. Copper gives 0.698 and gold 0.785, both in range, although gold's red channel is 1.0, since one channel alone is not tested. Wet asphalt gives 0.020, below 0.03, so it takes the blue mark. The fix is a lighter base color, near 0.04, and never a higher exposure.

   ```cpp sketch="light-measuring-light-audit.cpp"
   // Audits linear base colors the way the Albedo view does: by luminance, against 0.03 and 0.85.
   #include <cstdio>

   struct Material
   {
   	const char* Name;
   	float Red;
   	float Green;
   	float Blue;
   };

   constexpr float c_AlbedoLow = 0.03f;
   constexpr float c_AlbedoHigh = 0.85f;

   float GetLuminance(const Material& material)
   {
   	return 0.2126f * material.Red + 0.7152f * material.Green + 0.0722f * material.Blue;
   }

   int main()
   {
   	const Material materials[] = {
   		{ "rough copper", 0.955f, 0.638f, 0.538f },
   		{ "polished gold", 1.000f, 0.766f, 0.336f },
   		{ "wet asphalt", 0.020f, 0.020f, 0.022f },
   	};
   	for (const Material& material : materials)
   	{
   		const float albedo = GetLuminance(material);
   		const char* verdict = albedo < c_AlbedoLow ? "marked blue (too dark)" : albedo > c_AlbedoHigh ? "marked red (too bright)" : "in range";
   		std::printf("%-14s luminance %.3f: %s\n", material.Name, albedo, verdict);
   	}
   	return 0;
   }
   ```

   ```text output-of="light-measuring-light-audit.cpp"
   rough copper   luminance 0.698: in range
   polished gold  luminance 0.785: in range
   wet asphalt    luminance 0.020: marked blue (too dark)
   ```

   1. **Line 17:** the same weights as the engine's luminance.
   2. **Lines 23-25:** the three materials of the exercise.
   3. **Line 30:** the two limits of the view decide the verdict.
   :::

2. **Medium.** Trace it yourself: follow one frame's statistics from the buffer the counting shader fills, through the ring of readbacks, to `debugView.lighting` in the result of `viewport.capture`. Name each file and function, and say what the `Render` number is for.

   :::answer[Worked solution]{tests="stats-flow"}
   `Strata/shaders/Effects/LightingViewStats.comp.slang` fills the buffer. In `Strata/src/Strata/Renderer/SceneRendererLightingView.cpp`, `SceneRenderer::RecordLightingView` clears the buffer, dispatches the shader and records the copy, and `SubmitLightingViewReadback` submits it and moves to the next slot. `ResolveLightingViewStats` takes the newest finished readback of the current view and builds `LightingViewStats`; `SceneRenderer::ResolveGPUStats` in `Strata/src/Strata/Renderer/SceneRenderer.cpp` calls it. In `StrataEditor/src/Editor/EditorViewportCommands.cpp`, `DescribeDebugView` and `DescribeLightingViewStats` write the :term[JSON]{id=json}. `Render` names the frame a set measured, so you count the frames between the two by subtracting it from the renderer's render count when the set arrives.
   :::

3. **Hard.** Add a lighting view named Roughness that shows each surface's roughness as gray, end to end. List every place you change, and say which kind of view it is.

   :::answer[Worked solution]{tests="add-view"}
   Roughness is not light, so it is a value view. Add `Roughness` to the end of `SceneLightingView` in `Strata/src/Strata/Renderer/SceneRenderer.h` and its constant to `Strata/shaders/Include/Scene.slang`.

   Add it to both `IsLightingValueView` functions and to `IsValueView` in the counting shader. In `Strata/shaders/Scene/Forward.frag.slang` return the roughness without the pre-exposure, and in `Strata/shaders/Overlay/LightingView.frag.slang` draw it as gray like the occlusion. In the editor, extend `ViewportDebugView` and its name functions in `StrataEditor/src/Editor/StreamingView.h` and `StreamingView.cpp`, the chip's list in `StrataEditor/src/Panels/ViewportPanel.cpp` and the schema in `StrataEditor/src/Editor/EditorViewportCommands.cpp`. Finish with a case in `StrataTests/src/Renderer/GPUSceneLightingViewTests.cpp` that renders a sphere of known roughness and checks the pixel and `ValueMedian`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRenderer.h`: `SceneLightingView`, `LightingViewColors` and `LightingViewStats`.
- `Strata/src/Strata/Renderer/SceneRendererLightingView.cpp`: the passes, the ring of readbacks and the percentiles.
- `Strata/shaders/Effects/LightingViewStats.comp.slang`, `Strata/shaders/Overlay/LightingView.frag.slang` and `Strata/shaders/Include/LightingView.slang`: the counting, the drawing and the shared constants.
- `Strata/shaders/Include/Scene.slang` and `Strata/shaders/Scene/Forward.frag.slang`: the view constants and the forward branch.
- `StrataEditor/src/Editor/EditorViewportCommands.cpp`: `viewport.capture` and `viewport.setSettings`; `StrataEditor/src/Panels/ViewportPanel.cpp`: the chip and the legend.
- `StrataTests/src/Renderer/GPUSceneLightingViewTests.cpp`: the suite `GPU.SceneRenderer.LightingViews`.

## Further reading

- Naty Hoffman and others, the SIGGRAPH course notes on physically based shading: why albedo is bounded and how to check it. Intermediate.
- Sébastien Lagarde and Charles de Rousiers, "Moving Frostbite to Physically Based Rendering": real units, exposure and reference albedo values in a shipped engine. Advanced.
- The documentation of the visualization modes in Unreal Engine and of the scene view draw modes in Unity: other engines' false-color and albedo views. Beginner.
