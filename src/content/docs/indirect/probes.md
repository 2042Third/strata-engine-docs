---
id: indirect/probes
title: "Reflection probes"
description: "How a baked picture of a room becomes local reflections and ambient light: the box lookup, the blend, the slot cache, the conversion and the editor's bake."
kind: internals
size: XL
tracks: [E]
needs: [indirect/seam, image/pre-exposure, assets/residency, basics/math-geometry, draw/mip-streaming]
time: 105
learn:
  - id: parallax-fix
    text: explain why a reflection taken from one point is wrong inside a room, and how box projection corrects it
  - id: lookup-blend
    text: compute a probe's weight, its box-projected lookup and the share of each of two overlapping probes by hand
  - id: gather-cache
    text: trace how a frame ranks probes, gives captures slots, holds them and converts them in steps
  - id: conversion
    text: name the steps that turn a capture into a slot's prefiltered levels and nine irradiance coefficients
  - id: bake
    text: trace one lighting.bakeProbes bake through its four stages and say what it renders, waits for and changes
since: 0.6.0
status: final
---

A **reflection probe** is a box in the scene that carries a picture of its surroundings, taken from the box's center. Surfaces inside the box use the picture for light: shiny surfaces reflect it, and dull surfaces take its ambient light. This page covers what the :term[renderer]{id=renderer} does with probes each frame, and how the editor makes the pictures. A probe does not capture anything while the game runs, so the page also covers why. The sky's own image light belongs to [image-based lighting](ibl.md), and the reflections of what is on screen belong to [screen-space reflections](ssr.md).

You meet the parts in the order the data flows. They are the component, the frame's gather and ranking, the cache of slots and the residency holds. Then come the conversion on the :term[graphics processing unit]{id=gpu} (GPU), the :term[shader]{id=shader}, and last the bake in the editor.

## The problem and how engines solve it

Stand in a small room with a polished floor and a window. A shiny surface shows what is around it, so the floor should show the walls, the lamp and the window frame. The engine does not trace rays through the room: it looks the reflection up in a stored picture of the surroundings. For a floor in the open, one picture of the sky serves every surface, because the sky is so far away that moving a few meters changes nothing you can see.

Inside a room that assumption fails. A wall 4 m away does shift when you move 3 m, and a floor lit by the sky's picture would show a blue sky where a ceiling hangs. The first fix is a hand-made picture of the room, a :term[cube map]{id=cube-map}: six square images of the room seen from its center. That picture is right from the center only. This error is the parallax problem: parallax is the shift in where a thing appears when you look at it from another place.

Engines fix it in a few ways, and each trades quality against cost. The table lists the ones this page needs. A longer comparison, with what Strata did not take, comes after the real code.

| Technique | Idea | Cost |
| --- | --- | --- |
| Static :term[cube map]{id=cube-map} | One picture for the whole scene, or one per hand-placed area | Wrong inside rooms; many pictures to place by hand |
| Box with a corrected lookup | A picture plus the room's box: the ray is tested against the box before the lookup | A box for every room; right only for roughly box-shaped rooms |
| Clustered probe lists | Many probes sorted into screen cells, so a pixel reads only its own | A build step each frame |
| Run-time capture | The probe renders its picture while the game runs | Six extra views per probe per update |
| :term[Irradiance]{id=irradiance} volumes | A grid of small probes that hold only diffuse light | No sharp reflections; a lot of memory for large scenes |

Strata takes the second row, with a bake. **Box projection**, also called parallax correction, replaces the reflected direction with the direction from the probe's center to the place where the reflected ray leaves the box. A conference talk of 2012, listed in Further reading, made it common. For a room whose walls are straight the answer is close to right, because the picture was taken inside the same box.

Four more choices complete the design, and each has a cost. Boxes can overlap, so the shader blends two probes by how deep inside each box the pixel is. A probe has a **probe priority**, an :term[integer]{id=integer} on the component: where boxes overlap, the higher number wins, and a tie goes to the smaller box. The pictures are baked, not captured during play, so a moving sun does not change their light: you bake again after a change. Last, the renderer keeps the converted pictures of up to 16 probes in one :term[cube array]{id=cube-array}, a single texture with a cube for each slot, so one shader reads them all.

## The map

The diagram shows the cache, the one structure of this page that lives longer than a frame. A probe's capture is a texture asset. The gather asks for it, holds it whole until the GPU has converted it into a slot of the cube array, and then lets it drop to its tail. At most two conversions run in a frame, and the slot that has gone longest unused is the one a new capture takes.

```mermaid caption="The probe cache. Each frame the gather ranks the probes in view and finds or takes a slot for each capture. It converts at most two new captures, and a change of resolution fills new cubes beside the shown ones before they take over." alt="A flow from the scene's probes through the gather and ranking to the slots of the cube array. Captures not yet converted wait with a hold. A conversion fills a slot and its nine coefficients. A change of resolution makes a second set of cubes that replaces the first when every probe in view is converted."
flowchart LR
	Probes["Probe entities with a capture"] --> Gather["Gather: frustum test, rank, keep 16"]
	Gather --> Slot["Slot: held capture, else free, else least recently used"]
	Slot -->|capture ready, at most 2 a frame| Convert["Conversion: cube, six levels, nine coefficients"]
	Slot -->|capture not ready| Hold["Hold the whole capture; the sky lights the box"]
	Convert --> Array["Cube array and probe buffer"]
	Array --> Shader["Forward shader: two probes blended"]
	Gather -->|new resolution| Next["New cubes beside the shown ones"]
	Next -->|every probe in view converted| Array
```

Each box on the diagram is code in `Strata/src/Strata/Renderer/`. The files hold the work as follows.

- `RendererComponents.h` holds `ReflectionProbeComponent`.
- `SceneRendererReflectionProbes.cpp` holds the gather, the cache, the holds and the conversion.
- The shaders `Strata/shaders/IBL/ProbeIrradiance.comp.slang` and `Strata/shaders/Include/ReflectionProbes.slang` hold the projection onto coefficients and the lookup.
- `StrataEditor/src/Editor/EditorLightingCommands.cpp` and `ProbeBake.h` hold the bake, which runs in the editor and never in a game.

All of it runs on the :term[main thread]{id=main-thread} except what the GPU does and the bake's encoding and writing, which run on jobs. The renderer's frame is the one the [render scene](../draw/render-scene.md) page describes.

## The contract

Six rules hold for every change to probes. Each has a reason.

1. **Bake probes in the editor and never while the game runs; a bake draws neither the sun's disk nor the lights' highlights.** A probe's picture is a still, so it cannot show a moving object. A sun disk or a highlight in the picture would light a surface a second time from the wrong place.
2. **A bake renders where the probe stands now.** The scene caches each entity's world matrix and updates it once a frame, so a command that moved a probe in the same frame has not reached the cache. The bake asks `Scene::GetWorldTransform` for the position.
3. **A bake replaces only the capture an earlier bake made, and trashes that file in the same undo step.** A texture that you chose yourself stays, and one undo brings back the old picture.
4. **A capture is held whole until it is converted, and released after.** Nothing draws a capture, so nothing would ever make the streamer load its fine levels.
5. **Conversions are spread, two a frame, in interactive renderers.** A scene with sixteen probes would otherwise convert sixteen captures in one frame. Bakes and thumbnails do not spread, because they render one frame and need every conversion in it.
6. **Nothing blocks.** A capture that is not loaded lights nothing, and only captures and bakes wait for it. Everything else draws with the sky's light meanwhile.

:::why[Baked, not captured]
A baked picture is cheap to read and wrong for a moving scene, and Strata chose cheap. A probe that captured itself would add six views of the scene for every update, in a renderer that already spends its frame on lights and shadows. The rule about never blocking a frame on an asset is in [residency](../assets/residency.md).
:::

## A toy version

Before the real code, here is box projection and the blend by hand. The toy works on one box centered at the origin, with no rotation, and it needs no graphics. It answers one question for a surface point: where do I look in the picture, and how much of this probe do I use?

:::question
Never wrote a loop, a function or a call such as `std::printf(`? Read [variables and conditions](../basics/programming-1.md), [loops and functions](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md) first.
:::

The function `GetBoxLookup` finds where the reflected ray leaves the box, and `GetWeight` gives the share that fades out over the blend distance. Look at how the loop skips an axis the ray does not move along, and at how `GetWeight` takes the smallest of the three depths. The main function uses a room 8 m wide, 4 m high and 6 m deep.

```cpp sketch="indirect-probes-toy.cpp"
#include <cmath>
#include <cstdio>

// A box centered at the origin with half sizes `extents`; `local` is a position inside it, `reflected` a unit direction.
// Returns where the reflected ray leaves the box: the point to look up in the capture, seen from the center.
void GetBoxLookup(const float extents[3], const float local[3], const float reflected[3], float lookup[3])
{
	float exitDistance = 1.0e30f;
	for (int axis = 0; axis < 3; axis++)
	{
		// A ray that does not move along an axis never reaches that axis's faces.
		if (std::fabs(reflected[axis]) < 1.0e-6f)
			continue;
		const float face = reflected[axis] > 0.0f ? extents[axis] : -extents[axis];
		exitDistance = std::fmin(exitDistance, (face - local[axis]) / reflected[axis]);
	}
	exitDistance = std::fmax(exitDistance, 0.0f);
	std::printf("exit distance %.4f m\n", exitDistance);
	for (int axis = 0; axis < 3; axis++)
		lookup[axis] = local[axis] + reflected[axis] * exitDistance;
}

// 1 deeper than `blend` meters inside the box, falling to 0 at its faces.
float GetWeight(const float extents[3], const float local[3], float blend)
{
	float depth = extents[0] - std::fabs(local[0]);
	for (int axis = 1; axis < 3; axis++)
		depth = std::fmin(depth, extents[axis] - std::fabs(local[axis]));
	if (depth <= 0.0f)
		return 0.0f;
	return blend > 0.0f ? std::fmin(depth / blend, 1.0f) : 1.0f;
}

int main()
{
	const float extents[3] = { 4.0f, 2.0f, 3.0f };
	const float local[3] = { 2.0f, -1.5f, 0.0f };
	const float reflected[3] = { 0.6f, 0.8f, 0.0f };

	float lookup[3] = {};
	GetBoxLookup(extents, local, reflected, lookup);
	std::printf("lookup direction (%.4f, %.4f, %.4f)\n", lookup[0], lookup[1], lookup[2]);
	const float rise = std::atan2(lookup[1], std::hypot(lookup[0], lookup[2])) * 57.29578f;
	std::printf("rises %.1f degrees; the plain reflection rises %.1f\n", rise, std::asin(0.8f) * 57.29578f);

	// Two probes at this position: the stronger one's weight, then the weaker one's weight of what is left.
	const float strong = GetWeight(extents, local, 1.0f);
	const float weak = 0.8f * (1.0f - strong);
	std::printf("weights %.2f and %.2f; the sky fills %.2f\n", strong, weak, 1.0f - strong - weak);
	return 0;
}
```

```text output-of="indirect-probes-toy.cpp"
exit distance 3.3333 m
lookup direction (4.0000, 1.1667, 0.0000)
rises 16.3 degrees; the plain reflection rises 53.1
weights 0.50 and 0.40; the sky fills 0.10
```

1. **Lines 9–16:** for each axis the ray moves along, the distance to the far face is the face's coordinate minus the position, over the direction; the smallest wins.
2. **Lines 26–31:** the depth is the smallest distance to a face, and the weight is that depth over the blend distance, at most 1.
3. **Lines 46–49:** the stronger probe takes its weight, the weaker one 0.8 of what is left, and the sky gets the rest.

The picture the capture holds is the room seen from the center. The plain reflected direction rises 53.1 degrees, but the ray really leaves through the wall at a point that the center sees 16.3 degrees up. The lookup moves from the ceiling to the wall.

:::example[One floor point in a room]
The room has half sizes 4, 2 and 3 m, so the box spans 8 m in x, 4 m in y and 6 m in z. A point on the floor lies at (2, -1.5, 0) m from the center, and its reflected ray points along (0.6, 0.8, 0).

The ray moves along x and y, so only those faces count. The wall at x = 4 is (4 - 2) / 0.6 = 3.333 m away. The ceiling at y = 2 is (2 - (-1.5)) / 0.8 = 4.375 m away. The smaller number wins: the ray leaves through the wall after 3.333 m, at (2 + 2, -1.5 + 2.667, 0) = (4, 1.167, 0).

Seen from the center, that point rises atan(1.167 / 4) = 16.3 degrees. The plain direction (0.6, 0.8, 0) would rise 53.1 degrees, to the ceiling, so without box projection this floor would mirror the ceiling instead of the wall.

The blend distance is 1 m. The depth of the point is the smallest of 4 - 2 = 2, 2 - 1.5 = 0.5 and 3 - 0 = 3, which is 0.5 m, so the weight is 0.5. A weaker probe with weight 0.8 here takes 0.8 of what is left: 0.8 × 0.5 = 0.4. Together they cover 0.9, and the sky fills the last 0.1.
:::

::figure{id=probe-on-off variant=probe-off}

::figure{id=probe-on-off variant=probe-on}

The pictures show the same view with the yard's probe off and on. Without the probe the polished panel reflects the sky. With it the panel reflects the scene around it. Only the panel changes: the yard's other shiny objects stand outside the probe's box.

::figure{id=box-projection variant=box-off}

::figure{id=box-projection variant=box-on}

The second pair shows a probe without box projection and with it. Without the correction the reflected objects sit in the wrong places.

The toy omits five things that the real code has. The box can turn, so positions and directions are first moved into the box's own axes. The numbers are camera-relative: meters measured from the camera, not from the world's origin.

The lookup reads a filtered cube whose level follows the surface's roughness. Several probes compete for 16 slots. A capture takes time to load and convert, so a probe may not be ready.

## The real code, in the order data flows

### The component

The component is plain data. It holds the handle of the capture, the box, and the knobs the later steps read. Look at the units in the comments and at `c_MinExtent`, the smallest half size the renderer accepts.

```cpp src="Strata/src/Strata/Renderer/RendererComponents.h#L196-L205"
struct ReflectionProbeComponent
{
	AssetHandle Capture = 0;                    // Equirectangular HDR texture of the scene around the probe (nits)
	glm::vec3 Extents = { 5.0f, 5.0f, 5.0f };   // Half extents of the influence box in meters, along the entity's axes
	float BlendDistance = 1.0f;                 // Meters inside the box's faces over which the probe fades out
	bool BoxProjection = true;                  // Reflections hit the box's faces (rooms, courtyards) rather than infinity
	float Intensity = 1.0f;                     // Multiplies the capture's luminance
	int32_t Priority = 0;                       // Higher wins where boxes overlap (then the smaller box)

	static constexpr float c_MinExtent = 0.01f; // Meters: a box of no size would reflect nothing
```

1. **Line 198:** `Capture` is an :term[asset handle]{id=asset-handle} of an :term[equirectangular]{id=equirectangular} texture of :term[high dynamic range]{id=high-dynamic-range} (HDR) values in :term[nits]{id=lux}: one wide image of all directions.
2. **Line 199:** `Extents` are half sizes in meters along the entity's own axes, and the entity's scale multiplies them.
3. **Line 200:** `BlendDistance` is the width, inside each face, over which the probe fades out.
4. **Lines 201–203:** `BoxProjection` turns the lookup correction on, `Intensity` scales the capture's brightness, and `Priority` ranks probes.
5. **Line 205:** a box of no size would reflect nothing, so the renderer raises smaller half sizes to 0.01 m.

In the editor the component is **Reflection Probe**, added with **Add Component**. Its box has no :term[gizmo]{id=gizmo-start}: the Scene view draws boxes for colliders and shapes for lights and cameras, but none for a probe's `Extents`. You fit a box by the walls' sizes and check it after a bake by looking at the reflections. Exercise 3 builds a debug view that shows a box's reach.

### The gather and the ranking

Each frame `GatherReflectionProbes` walks every entity that has a `ReflectionProbeComponent` and a :term[world transform]{id=world-transform}. It skips probes that are not active in the hierarchy or have no capture. Then it builds the box from the world matrix: each column of the upper three by three part is an axis, its length is a scale, and the half sizes are multiplied by those lengths.

A non-finite matrix, or an axis of length zero, makes the probe invalid, and the gather drops it. A probe also passes a :term[frustum]{id=view-frustum} test: the renderer tests a sphere around the box's center whose radius is the length of the half-size vector, against the camera's view. The box itself is not tested, so a probe may be kept when its sphere touches the view but its box does not. The cost of that is a conversion for a probe nobody sees, and the gain is a cheap test.

The ranking is the rule **probe priority** states. A higher priority comes first. Among equal priorities the smaller volume comes first, because a small box is the more specific place. If even that ties, the lower entity number comes first, so the order never changes from frame to frame.

```cpp src="Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp#L60-L66"
bool IsStronger(const ProbeCandidate& a, const ProbeCandidate& b)
{
	if (a.Priority != b.Priority)
		return a.Priority > b.Priority;
	if (a.Volume != b.Volume)
		return a.Volume < b.Volume;
	return a.Entity < b.Entity;
```

The volume is the product of the three scaled half sizes, which orders boxes in the same way as the true volume would. The gather sorts with this function and keeps the first `MaxReflectionProbes`, at most 16.

One more detail is the scan for `sceneHasProbes`. A probe with a capture keeps the cache alive even when it is out of view, so turning around does not free the slots. When the scene has no probe with a capture at all, the gather releases the cache. When probes exist but none is in view, it only lets go of the stale holds.

### Slots and holds

A slot is one cube of the cube array. Three small :term[lambdas]{id=lambda} inside the gather manage them. `findSlot` returns the slot that holds a capture, and `holdsConverted` also checks that the slot was converted from the texture that is loaded now. The one that gives out slots is `acquireSlot`.

```cpp src="Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp#L281-L298"
const auto acquireSlot = [gather](ReflectionProbeState& cubes, AssetHandle capture)
{
	uint32_t replaceable = c_NoSlot;
	for (uint32_t index = 0; index < static_cast<uint32_t>(cubes.Slots.size()); index++)
	{
		const ReflectionProbeSlot& candidateSlot = cubes.Slots[index];
		if (candidateSlot.Capture == capture)
			return index;
		if (candidateSlot.LastUsed == gather)
			continue;
		if (replaceable == c_NoSlot || !candidateSlot.Capture.IsValid()
			|| (cubes.Slots[replaceable].Capture.IsValid() && candidateSlot.LastUsed < cubes.Slots[replaceable].LastUsed))
			replaceable = index;
	}
	// At most as many probes as slots are kept, so a slot this gather does not use is left.
	ST_CORE_ASSERT(replaceable != c_NoSlot, "No reflection probe slot left");
	cubes.Slots[replaceable] = ReflectionProbeSlot { capture, {}, 0 };
	return replaceable;
```

1. **Lines 287–288:** a capture that already has a slot gets that slot back, so a probe in view keeps its cube from frame to frame.
2. **Lines 289–290:** a slot that this gather has already given out is never taken away from a probe in the same view.
3. **Lines 291–293:** the candidate to replace is an empty slot, or else the one with the smallest `LastUsed`, the :term[least recently used]{id=lru}.
4. **Lines 296–298:** at most as many probes as slots are kept, so a free slot always exists; the new capture starts not yet converted, with `LastUsed` 0.

The gather counts its passes, and `LastUsed` stores the pass number. That is cheaper than a clock and cannot go backward.

Next come the holds. A capture is an ordinary texture asset, and the texture streamer loads only as many levels of a texture as the screen needs. Nothing draws a capture, so no draw would ever ask for its fine levels. The conversion needs all of them, because it reads the capture's level 0 or level 1, so the gather has to ask for the whole texture itself.

```cpp src="Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp#L301-L319"
auto hold = [&](AssetHandle capture)
{
	if (!streamer)
		return;
	ReflectionProbeHold& held = m_ReflectionProbeHolds[capture];
	if (!held.Hold)
		held.Hold = CreateRef<TextureHold>(TextureHold { capture });
	held.Frame = Renderer::GetFrameNumber();
	// Again in every frame it waits: a hold placed in another manager's streamer (a project opened since) lapsed with it.
	streamer->Hold(held.Hold);
};

// Holds a capture whole until it is converted, counted as pending for the frame's resolve cache while levels are missing.
const auto holdWhole = [&](AssetHandle capture, const Ref<Texture>& texture)
{
	hold(capture);
	if (texture && texture->GetResidentLevel() > 0)
		m_Assets.CountPending(capture);
};
```

1. **Lines 305–308:** each waiting capture has a hold record with the frame number of its last renewal.
2. **Line 310:** the hold goes to the streamer again in every frame the capture waits, because a hold placed in another :term[asset manager's]{id=asset-manager} streamer lapses with it.
3. **Lines 314–318:** `holdWhole` also counts the capture as pending while any level is missing, so frames that must wait for it (a bake) do.

`ReleaseStaleReflectionProbeHolds` erases a record whose last frame is more than one frame old. The extra frame matters for a bake, which renders six views per frame: the streamer raises levels between frames, and a hold that ended inside the frame would be lost before it worked. Once a capture is converted, nobody renews its hold, and the texture drops back to its :term[mip tail]{id=mip-tail} while the slot keeps lighting.

The cost of that design is memory in two places for a moment: the whole capture and the converted slot. The gain is that the capture then leaves memory.

### The conversion

A capture is an equirectangular picture, and the shader wants a cube with a level for each roughness. `ConvertReflectionProbes` turns the one into the other on the GPU, in the reflections stage of the frame, after ambient occlusion and global illumination and before the opaque pass. It shares the sky's pipelines from [image-based lighting](ibl.md): the same equirectangular-to-cube pass and the same filter pass, with a probe's own sample counts.

The size comes from the quality row `ReflectionProbeResolution`: 128 texels on Low and Medium, 256 on High and `Ultra`. A 256 face reads the capture's level 0, and a 128 face reads level 1, so a capture never needs a re-bake for another resolution. The scratch cube holds the whole chain of levels down to 1 texel, and the cube array holds six levels, for the roughness steps 0, 0.2, 0.4, 0.6, 0.8 and 1.

```cpp src="Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp#L464-L481"
DispatchIBL(commandList, m_EquirectToCubePipeline, conversion.Source->GetGPUTexture(), nvrhi::AllSubresources, nvrhi::TextureDimension::Texture2D,
	state.Scratch, 0, nvrhi::TextureDimension::Texture2DArray, RenderData::IBLParameters { size, conversion.Source->GetWidth(), 0.0f, 1 }, 6);
for (uint32_t mip = 1; mip < scratchMips; mip++)
{
	const uint32_t mipSize = std::max(1u, size >> mip);
	DispatchIBL(commandList, m_CubeDownsamplePipeline, state.Scratch, nvrhi::TextureSubresourceSet(mip - 1, 1, 0, 6),
		nvrhi::TextureDimension::Texture2DArray, state.Scratch, mip, nvrhi::TextureDimension::Texture2DArray,
		RenderData::IBLParameters { mipSize, mipSize * 2, 0.0f, 1 }, 6);
}
// The slot's levels, one per roughness step (level 0 a copy of the capture's cube), as the sky's prefiltered map.
const nvrhi::TextureSubresourceSet wholeScratch(0, scratchMips, 0, 6);
for (uint32_t mip = 0; mip < RenderData::c_ReflectionProbeMipCount; mip++)
{
	const uint32_t mipSize = std::max(1u, size >> mip);
	const float roughness = static_cast<float>(mip) / static_cast<float>(RenderData::c_ReflectionProbeMipCount - 1);
	DispatchIBL(commandList, m_PrefilterPipeline, state.Scratch, wholeScratch, nvrhi::TextureDimension::TextureCube, state.Array, mip,
		nvrhi::TextureDimension::Texture2DArray, RenderData::IBLParameters { mipSize, size, roughness, RendererQuality::GetProbePrefilterSamples(size, mip) }, 6,
		conversion.Slot * 6);
```

1. **Lines 464–465:** the capture's pixels are copied into level 0 of the scratch cube, six faces in one dispatch.
2. **Lines 466–472:** each smaller level of the scratch cube is a shrunk copy of the one above. Filtered importance sampling reads these levels, as [image-based lighting](ibl.md) explains.
3. **Lines 475–478:** one filter pass per level of the slot; its roughness is the level number over five.
4. **Lines 479–481:** the pass writes the slot's six faces, which start at array layer `Slot * 6`.

`RendererQuality::GetProbePrefilterSamples` chooses the sample count: 256, except 128 for levels 1 and 2 when the size is above 128. Strata halves the samples there to keep the cost of the larger cubes down. Counting all levels, a conversion at 256 filters about 2.1 times the samples of one at 128, where four times the texels might suggest four times.

::figure{id=resolution variant=texels-128}

::figure{id=resolution variant=texels-256}

The mirror ball shows the gain of the larger cubes: at 256 texels the reflected detail is finer.

After the six levels comes the irradiance. The code binds the scratch cube's 32-texel level, and one work group, a batch of 64 GPU threads that run together, writes nine coefficients into the slot's part of the probe buffer. The last line marks the slot as holding this texture, so the same capture is not converted twice.

On the reference machine, two conversions take at most 0.46 ms at 128 texels and 0.38 ms at 256 in the reflections stage. That is a small part of a frame of 16.7 ms at 60 :term[frames per second]{id=frame-rate} (3 %). The GPU has idle room in these passes, so their time follows the chain of filter samples of each texel. Strata therefore spreads conversions by count, not by work.

### The irradiance projection

The cube array answers shiny surfaces. A dull surface needs the light arriving from all around, called irradiance. Strata stores it in a small form: nine numbers for each :term[color channel]{id=color-channel}. They are the coefficients of the real spherical harmonics of bands 0 to 2, a set of smooth functions on a sphere ([the sphere page](../basics/math-sphere.md) teaches them). A slot holds 27 numbers, and the shader rebuilds a smooth light from them: it multiplies each coefficient by its function's value in the direction of the surface's normal and adds the nine products.

The projection sums, over every texel of the 32-texel cube level, the texel's :term[radiance]{id=radiance} times the :term[basis function]{id=basis-function} times the texel's :term[solid angle]{id=solid-angle}. The solid angle matters because texels near a cube's corners cover less of the sphere than the ones at a face's center.

```slang src="Strata/shaders/IBL/ProbeIrradiance.comp.slang#L51-L66"
for (uint texel = thread; texel < texels; texel += ST_GROUP_SIZE)
{
	uint face = texel / (size * size);
	uint inFace = texel - face * size * size;
	uint2 xy = uint2(inFace % size, inFace / size);
	float2 st = (float2(xy) + 0.5) / float(size) * 2.0 - 1.0;
	float3 direction = FaceDirection(st, face);
	// The texel's solid angle: its area on the face over the cube of its distance from the center.
	float distanceSquared = dot(direction, direction);
	float solidAngle = (4.0 / float(size * size)) / (distanceSquared * sqrt(distanceSquared));
	float3 radiance = u_Source.Load(int4(int3(xy, face), 0)).rgb;
	float basis[9];
	ProbeSHBasis(direction * (1.0 / sqrt(distanceSquared)), basis);
	for (uint index = 0u; index < 9u; index++)
		sums[index] += radiance * (basis[index] * solidAngle);
	weight += solidAngle;
```

1. **Lines 51–55:** each of the 64 threads of the group takes every 64th texel and finds its face and pixel.
2. **Lines 56–57:** the texel's center becomes a direction on the cube's face.
3. **Lines 58–60:** the solid angle is the texel's area on the face over the cube of its distance from the center.
4. **Lines 61–66:** the texel's radiance times the nine basis values times the solid angle joins the sums, and the angles add up in `weight`.

Then the threads share their sums through group memory, and nine of them reduce one coefficient each.

```slang src="Strata/shaders/IBL/ProbeIrradiance.comp.slang#L73-L85"
if (thread < 9u)
{
	float3 sum = float3(0.0);
	float total = 0.0;
	for (uint other = 0u; other < ST_GROUP_SIZE; other++)
	{
		sum += s_Sums[other][thread];
		total += s_Weights[other];
	}
	// The texels' solid angles sum to about 4 pi: normalized to it exactly. Then the clamped cosine's band factors.
	sum *= (4.0 * PI) / max(total, 1e-6);
	float band = thread == 0u ? 1.0 : (thread < 4u ? 2.0 / 3.0 : 0.25);
	o_ProbeIrradiance[u_Parameters.Slot * ST_REFLECTION_PROBE_SH + thread] = float4(sum * band, 0.0);
```

1. **Lines 77–81:** thread `thread` adds up coefficient `thread` over all 64 partial sums, and the weights too.
2. **Lines 82–83:** the solid angles should add up to 4 pi, the area of the :term[unit sphere]{id=unit-sphere}; the sum is scaled to it exactly, so rounding in the faces cannot brighten or darken the probe.
3. **Line 84:** the band factor 1 for the first coefficient, 2/3 for the next three and 1/4 for the last five.
4. **Line 85:** the result goes to the slot's nine entries of the probe buffer.

The band factors come from a clamped :term[cosine]{id=cosine}, which is what a dull surface does to the light. The paper in Further reading gives them as pi, 2 pi / 3 and pi / 4. Strata divides each by pi, because the sky's irradiance map and the shader both work with the irradiance over pi, so reading a probe's light needs no extra division.

### The shader

The shader works with the list that the gather uploaded: up to 16 entries, strongest first. Each holds the box's camera-relative center, its three axes, its half sizes, the blend distance, the intensity, the box-projection switch and the slot. The cube array is bound as shader resource view 9, a black array of one slot when the scene has no probes, and the probe buffer as 10.

Three functions do the work. `ToProbeBox` moves a camera-relative position into the box's frame with three :term[dot products]{id=dot-product}. The next two are the weight and the lookup.

```slang src="Strata/shaders/Include/ReflectionProbes.slang#L62-L85"
float GetProbeWeight(ReflectionProbeData probe, float3 local)
{
	float3 extents = float3(probe.AxisX.w, probe.AxisY.w, probe.AxisZ.w);
	float3 inside = extents - abs(local);
	float depth = min(inside.x, min(inside.y, inside.z));
	if (depth <= 0.0)
		return 0.0;
	return probe.CenterBlend.w > 0.0 ? clamp(depth / probe.CenterBlend.w, 0.0, 1.0) : 1.0;
}

// The direction to look a reflection up in a probe's cube: with box projection, where the reflected ray from the position
// leaves the box, seen from the box's center (where the capture was taken); else the reflected direction itself.
float3 GetProbeLookup(ReflectionProbeData probe, float3 local, float3 reflected)
{
	if (probe.Parameters.y < 0.5)
		return reflected;
	float3 direction = float3(dot(reflected, probe.AxisX.xyz), dot(reflected, probe.AxisY.xyz), dot(reflected, probe.AxisZ.xyz));
	float3 extents = float3(probe.AxisX.w, probe.AxisY.w, probe.AxisZ.w);
	// The far face along each axis the ray moves along (a direction without a component never reaches that axis's faces).
	float3 safe = select((abs(direction) < float3(1e-6)), float3(1e-6), direction);
	float3 toFaces = (sign(safe) * extents - local) / safe;
	float distanceToExit = max(min(toFaces.x, min(toFaces.y, toFaces.z)), 0.0);
	float3 hit = local + direction * distanceToExit;
	return hit.x * probe.AxisX.xyz + hit.y * probe.AxisY.xyz + hit.z * probe.AxisZ.xyz;
```

1. **Lines 65–68:** the depth is the smallest distance to a face; at or beyond a face the weight is 0.
2. **Line 69:** with a blend distance the weight is the depth over it, clamped to 1; without one the weight is 1 everywhere inside.
3. **Lines 76–77:** without box projection the lookup is the reflected direction itself.
4. **Lines 78–83:** the ray's direction in the box's frame, then the distance to the far face on each axis, on the side the ray moves toward. An axis the ray does not move along gets a huge distance.
5. **Lines 84–85:** the nearest face gives the exit; the lookup is the exit point, seen from the center, turned back into world axes.

The code is your toy again, written for a box that can turn. Then `EvaluateReflectionProbes` loops over the list.

```slang src="Strata/shaders/Include/ReflectionProbes.slang#L98-L124"
ProbeLight EvaluateReflectionProbes(float3 relativePosition, float3 normal, float3 reflected, float roughness)
{
	ProbeLight light;
	light.Irradiance = float3(0.0);
	light.Radiance = float3(0.0);
	light.Weight = 0.0;
	uint count = min(u_ProbeCounts.x, ST_MAX_REFLECTION_PROBES);
	uint found = 0u;
	for (uint index = 0u; index < count && found < 2u; index++)
	{
		ReflectionProbeData probe = u_ReflectionProbes[index];
		float3 local = ToProbeBox(probe, relativePosition);
		float weight = GetProbeWeight(probe, local);
		if (weight <= 0.0)
			continue;
		// The stronger probe takes its weight, the weaker one its weight of what is left.
		float share = weight * (1.0 - light.Weight);
		float slot = probe.Parameters.z;
		float3 lookup = GetProbeLookup(probe, local, reflected);
		float3 radiance = u_ReflectionProbeCubes.SampleLevel(u_LinearClampSampler, float4(lookup, slot), roughness * (ST_REFLECTION_PROBE_MIPS - 1.0)).rgb;
		float3 irradiance = EvaluateProbeIrradiance(uint(slot + 0.5), normal);
		light.Irradiance += irradiance * probe.Parameters.x * share;
		light.Radiance += radiance * probe.Parameters.x * share;
		light.Weight += share;
		found++;
	}
	return light;
```

1. **Lines 104–106:** at most 16 boxes are tested, and the loop stops after two have held the pixel.
2. **Lines 109–112:** a probe whose weight is 0 here is skipped; the others are tried in rank order, so the strongest comes first.
3. **Lines 113–115:** the stronger probe takes its weight, and the weaker one takes its weight of what is left, `weight * (1 - light.Weight)`.
4. **Lines 116–118:** the lookup, then the radiance from the slot's level for the surface's roughness, and the irradiance from the coefficients.
5. **Lines 119–122:** both are scaled by the intensity and the share, and the shares add up to the probes' weight.

The caller adds the sky's light, times 1 minus that weight, to what the probes leave open, so a probe fades into the sky without a step. [The seam page](seam.md) shows where this join sits next to screen-space reflections. The loop reads at most two probes per pixel, not 16, so a pixel inside three overlapping boxes ignores the weakest.

### The bake

The pictures come from the editor's command `lighting.bakeProbes`. It has no game counterpart: a bake renders the scene being edited and writes files in the project. In the editor, the probe's part of the Inspector has a **Bake** button, and the Sky part has **Bake Reflection Probes** for every active probe. An agent calls the command.

This step has no menu or button for an agent: run the command. The line below bakes every active probe of the open scene, and the editor answers when the new textures are imported. [Commands in the editor](../editor/commands.md) explains the call.

```sh
StrataCLI call lighting.bakeProbes '{}'
```

A bake has four stages: render, encode, write and import. Each frame the editor polls the bake and moves it on.

```mermaid caption="The bake in four stages. Six views of each probe are rendered and read back. The images are assembled and encoded on jobs, a file is written on an input and output job, and the import and one undo step end the bake." alt="Four stages left to right. Render: a renderer of its own draws six views of each probe, one probe per frame, again until nothing is pending. Encode: readbacks, then assembly and encoding on jobs. Write: the staging file is written on an input and output job. Import: the editor copies and imports it, sets the capture, trashes the earlier capture and records one undo step."
flowchart LR
	Render["Render: six views a probe, repeated while loading"] --> Encode["Encode: readback, assemble, encode on jobs"]
	Encode --> Write["Write: staging file on an I/O job"]
	Write --> Import["Import: copy, set Capture, trash old file"]
	Import --> Undo["One undo step"]
```

The stage **Render** uses a renderer made for the bake. It draws six square views of 256 texels, each of 90 degrees, along the axes plus x, minus x, plus y, minus y, plus z and minus z, from the probe's position. The options ask for two things that a normal frame does not do. The first is HDR output: the frame ends with its :term[HDR image]{id=hdr-image}, with no exposure, bloom or :term[tone mapping]{id=tone-mapping-image}. The second is the probe-capture mode, which keeps the sun's disk and the lights' highlights out of the picture.

```cpp src="StrataEditor/src/Editor/EditorLightingCommands.cpp#L192-L225"
SceneRenderOptions options;
options.HDROutput = true;
options.PreExposure = state.PreExposure;
options.ProbeCapture = true;
bool complete = true;
for (uint32_t face = 0; face < 6; face++)
{
	SceneCamera camera = ProbeBake::GetFaceCamera(probe.Position, face);
	camera.ClearColor = state.ClearColor;
	if (!state.Renderer->Render(scene, camera, nullptr, options))
		return EditorCommandResult::Fail(fmt::format("Rendering what '{}' sees failed (the log says why)", probe.Name));
	const SceneRendererStats& stats = state.Renderer->GetStats();
	complete = complete && stats.PendingAssets == 0 && stats.DeferredProxies == 0 && stats.LocalShadowViewsPending == 0
		&& stats.ReflectionProbesPending == 0 && stats.StalePoses == 0;
	std::string error;
	probe.Readbacks[face] = TextureReadback::Create(state.Renderer->GetHDRTexture(), {}, &error);
	if (!probe.Readbacks[face])
		return EditorCommandResult::Fail(fmt::format("Reading what '{}' sees back failed: {}", probe.Name, error));
}
if (!complete && std::chrono::steady_clock::now() < state.WaitDeadline)
{
	probe.Readbacks = {};
	return std::nullopt;
}
probe.Complete = complete;
if (++state.NextProbe == state.Probes.size())
{
	// Every view is on its way back: the renderer is done.
	state.Renderer->SetViewportSize(0, 0);
	state.Renderer.reset();
	state.Stage = BakeStage::Encode;
	state.Submitted = std::chrono::steady_clock::now();
}
return std::nullopt;
```

1. **Lines 192–195:** the options: HDR output, the bake's :term[pre-exposure]{id=pre-exposure}, and the probe-capture mode.
2. **Lines 197–202:** each of the six faces is rendered with the probe's camera, and a failed render ends the bake with a message.
3. **Lines 203–205:** a face is complete only when no asset, proxy, shadow view, probe conversion or animation pose is still pending.
4. **Lines 207–209:** each face starts a :term[readback]{id=readback} of the HDR image, which the later frames poll and never wait for.
5. **Lines 211–224:** an incomplete probe is rendered again on the next frame until the wait ends; the last probe's end moves the bake to **Encode**.

The probe-capture mode is one number in the frame constants, `MaterialParams.w`. At 1 the shader function `LightSurface` weights the specular part of every light by zero, so a surface keeps the lights' diffuse light and loses their highlights. A highlight depends on where the viewer stands. One baked from the probe's center and then read from elsewhere showed as a bright patch in the wrong place. The atmosphere's background also draws without the sun's disk, which is about 1e9 nits for a 100,000 lux sun.

The pre-exposure is a power of two that brings the scene's brightest directional light to about 1: with a 120,000 lux sun, the :term[exponent]{id=exponent} is floor(log2(120,000)) = 16, so the bake multiplies by 2^-16. Surfaces lit by the sun, of tens of thousands of nits, then sit near 1, and :term[half-float]{id=half-float} colors, which end at 65,504, do not clip. The scale is a power of two, so it is exact, and the assembly divides it out again. [Pre-exposure](../image/pre-exposure.md) teaches the mechanism.

In **Encode** the editor polls the readbacks and, when all six are ready, submits a job. The job assembles the six faces into a 1024 by 512 equirectangular image: for every output texel it finds the direction, picks the face that direction lies in, and reads the face bilinearly. The values return to nits and become a Radiance `.hdr` file in memory. In **Write** an input and output job writes the file into the project's intermediate folder, `.strata/Bake/<bake>/`. In **Import** the editor copies the file into `Assets/Lighting/<scene>/<probe id>.hdr` and imports it in the background, as any texture.

Only then does anything of the project change. `ApplyBake` sets each probe's `Capture`, and the earlier capture of the same probe moves to the trash when nothing else uses it. A texture you chose yourself for the probe stays. All of it is one undo step, **Bake Reflection Probes**.

### What a bake sees and waits for

The bake's renderer is `SceneRendererSpecification::ForBake`. It takes Medium's quality values as a Custom preset, with no temporal anti-aliasing, no texture streaming, no spreading and no fades. A bake therefore never depends on what a person chose in Graphics Quality.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L263-L279"
SceneRendererSpecification SceneRendererSpecification::ForBake()
{
	// No entity IDs, temporal anti-aliasing or texture streaming (a bake waits for every level), every shadow view and
	// probe conversion in its first frame, no fades, Strata 0.6.0's cascades (a bake's views are single frames).
	SceneRendererSpecification specification;
	specification.DebugName = "ProbeBake";
	specification.EntityIDs = false;
	specification.TemporalAntiAliasing = false;
	specification.TextureStreaming = false;
	specification.SpreadLightingUpdates = false;
	specification.FadeTextureLevels = false;
	specification.FadeLevelsOfDetail = false;
	RendererQualitySettings& quality = specification.Quality;
	quality = RendererQuality::GetPreset(RendererQualityPreset::Medium);
	quality.Preset = RendererQualityPreset::Custom;
	quality.LocalShadowAtlasSize = 2048;
	return specification;
```

1. **Lines 269–274:** a bake needs every texture level at once, every conversion in its first frame and no fades between levels of detail.
2. **Lines 275–277:** Medium's row, copied and renamed Custom, so a person's own quality choice cannot enter.
3. **Line 278:** the local lights' shadow atlas at 2048 texels, half the side of Medium's 4096, which a bake fills with every shadow view in its first frame.

Two rows of Medium decide what a capture can hold. Global illumination is Off on Medium, so a capture holds no global illumination. Screen-space reflections are Checkerboard on Medium, a mode that needs temporal anti-aliasing, so a capture holds none. The picture holds the sky, the lights' diffuse light, the shadows and the earlier captures.

A view that waits is drawn again. The bake renders each probe's six views on every frame until nothing they show is pending: assets, deferred proxies, shadow views, probe conversions and animation poses. The wait ends by the clock, 120 seconds from the bake's start, whatever the frame rate, since a fresh session's imports take that long. A probe whose views still waited is baked as it is, and the result says `complete: false` for it.

The background of the views is the :term[primary camera's]{id=primary-camera} clear color, so a view that shows no sky shows what the game would show. A change of scene, or **Play**, before the import ends the bake with the message "nothing was changed", and the imported files are moved to the trash again.

### Bounces and times of day

A bake draws the probes' present captures too, its own probe's included. So each bake adds one bounce: the light that the last picture saw lands on surfaces, and the next picture sees that. The Showcase sample bakes eight times for this reason: after eight passes nothing of the first captures is left, and two runs from different starts agree.

A scene whose sun moves needs a set of probes for each time of day. You bake each set with its sun, keep only one set active, and switch sets with `SetActive`. [Reflections for a game](../make/reflections.md) teaches that pattern for game makers.

Strata does not capture probes while the game runs, so a moving sun or a moved object never changes a probe's picture until you bake again. It also draws no gizmo for a probe's box. Three mistakes follow from this, and all three appear as reflections that look wrong.

- **Expecting a probe to follow the scene.** After you move a light or an object, bake again. A picture of the old arrangement keeps lighting the room.
- **A box that does not fit the room.** Box projection assumes the picture was taken inside a box of the same shape. A box much larger than the room puts the walls too far away, and a smaller one reaches into the next room.
- **A probe outside the walls.** The probe's position is where the picture is taken from. A probe that stands inside a pillar or behind a wall sees that, and its picture holds nothing of the room.

The renderer reports what it did each frame in three statistics of `SceneRendererStats`. `ReflectionProbes` counts the probes the frame shaded with, `ReflectionProbeConversions` the conversions it ran, and `ReflectionProbesPending` the probes in view that still wait for a capture to load or convert. A pending count that stays above zero means a capture is still loading or converting.

:::example[Cost of one probe at two resolutions]
A cube array of 16 slots with six levels of half-float colors holds, at 128 texels, about 1 MiB a slot, 17 MiB in all with the scratch cube. At 256 texels a slot holds about 4 MiB, so 68 MiB with the scratch cube. Each level has a quarter of the texels of the one above, so the six levels add a third to the top level. At 128 texels the top level is 128 × 128 × 6 faces × 8 :term[bytes]{id=byte} = 0.75 MiB, and with the levels about 1 MiB.

A scene with three probes in view needs three slots, but the cache always makes the cubes for all 16. That is the price of one fixed array: a probe never waits for memory.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Run-time capture of probes | Engines with a day cycle, such as those in the Further reading | A probe that follows a moving sun and moving objects | Six more views per probe per update, and a bake's wait for loading must happen live |
| Irradiance volumes or a grid of small probes | Engines that light moving characters in large levels | Smooth diffuse light that changes across a room | No sharp reflections, and memory that grows with the volume |
| Clustered probe lists | Engines with hundreds of probes | A pixel reads only the probes that reach it | A build pass each frame; Strata keeps at most 16 per view |
| Blending every probe in range | Engines with a few probes per area | No hard choice of two | Up to 16 lookups a pixel, where Strata reads at most two |
| Spheres or other shapes for the box | Engines with round rooms | Better fit for caves and domes | A new lookup for each shape and a new editor tool |
| Flat mirror views | Engines with one large mirror | Exact reflections of a flat surface | A second view of the whole scene per mirror |

## How it is tested

The renderer's half is the suite `GPU.SceneRenderer.ReflectionProbes` in `StrataTests/src/Renderer/GPUReflectionProbeTests.cpp`. It needs a GPU and shares one device with the other GPU suites. The tests cover each rule of this page:

- `A scene without reflection probes samples a one-slot black cube array and makes nothing else` checks the idle state.
- `A probe whose capture is missing or not a texture lights nothing and waits for nothing` checks the rule that nothing blocks.
- `A mirror ball inside a probe's box reflects the probe's capture, and one outside it the sky` and `Box projection reflects a capture's walls where they are` check the lookup.
- `Two overlapping probes blend by their weights, the stronger over the weaker` checks the blend, and `With more probes in view than slots the strongest are kept` the ranking.
- `Spread over frames at most two captures convert per frame, else all in the first` checks the spreading.
- `ReflectionProbeResolution sizes the cube array, and a new one's cubes take over once the probes in view converted` checks the takeover.
- `A probe's capture is held whole until converted, then drops to its tail` checks the holds.
- `ProbeCapture draws no sun disk and changes nothing else` and `ProbeCapture leaves the lights' highlights out and keeps their diffuse light` check the capture mode.

The editor's half is `GPU.Editor.Lighting` in `StrataTests/src/Editor/GPUEditorLightingTests.cpp`. Its tests bake a probe where it stands, bake at their own quality, wait by the clock, leave nothing when a bake ends early, and trash the earlier file in one undo step. `Editor.Lighting` holds the tests that need no GPU. Run a suite with the test program's filter, for example `StrataTests.exe --test-suite=GPU.SceneRenderer.ReflectionProbes`, or with `ctest --preset windows-debug -j 8`.

## Changing it safely

- **Bake through commands.** A new way to change captures goes through `lighting.bakeProbes` or a new command, never a panel that writes files. The rule: a change to the scene goes through a command and records one undo step.
- **Keep the trash with the undo step.** A bake that replaces a capture must trash the old file in the same step, or an undo brings back a probe whose texture is gone.
- **Keep holds renewed every frame.** A new place that needs a whole capture holds it through `hold`, and ends the hold by not renewing it.
- **Keep the slot's source.** A slot remembers which texture it converted, so a reloaded texture converts again.
- **Change a limit in two places.** The shader constant `ST_MAX_REFLECTION_PROBES` and the engine's `RenderData::c_MaxReflectionProbes` must agree, and so must the buffer's layout in `SceneRenderData.h` and `ReflectionProbes.slang`.
- **Bump a quality row's traits.** A new quality row needs its line of traits.

Before a commit, run `GPU.SceneRenderer.ReflectionProbes`, `GPU.Editor.Lighting`, `Editor.Lighting` and the feature test.

## What went wrong before

Version 0.7.0's bakes drew the sun's disk and the lights' highlights into the picture. The sun's disk is about 1e9 nits for a 100,000 lux sun. In a capture it lit surfaces a second time from the probe, with no shadow and projected to the wrong place, while the directional light already lit them. The picture also held the highlight of the sun on a polished tank, seen from the probe's center. On wet ground that highlight showed as a bright blurred patch, in a place where the screen-space reflections missed.

The fix was the probe-capture mode, with two regression tests: `A bake under the atmosphere draws no sun disk into its capture` in `GPU.Editor.Lighting`, and the two `ProbeCapture` tests in `GPU.SceneRenderer.ReflectionProbes`. The drawing below shows how the old bake's highlight came to lie on the wet ground.

::figure{id=sun-in-bake}

## Summary

- A probe's picture is right from its center only; box projection moves the lookup to where the reflected ray leaves the box, which fixes the parallax of a room.
- A probe's weight is its depth over the blend distance, and of two overlapping probes the stronger takes its weight and the weaker its weight of the rest.
- Each frame the renderer ranks probes by priority, smaller box and entity, keeps 16, gives captures slots by least recent use, holds waiting captures whole and converts two a frame.
- A conversion fills a cube, six prefiltered levels and nine irradiance coefficients per slot; the coefficients carry the band factors divided by pi.
- A bake renders six views a probe at Medium's values with the probe-capture mode, waits up to two minutes, imports a file and records one undo step.

## Check yourself

1. A room has half sizes 5, 3 and 4 m. A surface lies at (1, 0, 2) m from the probe's center, and its reflected ray points along (0.6, 0.8, 0). Where does the box-projected lookup point, and what does the plain lookup give?

   :::answer{tests="parallax-fix,lookup-blend"}
   The wall at x = 5 is (5 - 1) / 0.6 = 6.667 m away, and the ceiling at y = 3 is 3 / 0.8 = 3.75 m away. The ceiling is nearer, so the lookup points to (1 + 2.25, 3, 2) = (3.25, 3, 2). Without box projection the lookup is the reflected direction (0.6, 0.8, 0), which rises 53.1 degrees, while the box-projected lookup rises only 38.2 degrees.
   :::

2. A probe's blend distance is 2 m, its half sizes are 4, 2 and 3 m, and the surface is at (1, -0.5, 0) m. A weaker probe has weight 0.6 at the same place. How much does the weaker one contribute: (a) 0.6, (b) 0.15 or (c) 0.25?

   :::answer{tests="lookup-blend"}
   Option (b). The stronger probe's depth is 1.5 m, so its weight is 1.5 / 2 = 0.75. The weaker one takes its weight of what is left: 0.6 × (1 - 0.75) = 0.15. Option (a) forgets that the stronger probe came first, and option (c) is what is left for the weaker one, not what it takes. The sky fills 1 - 0.75 - 0.15 = 0.10.
   :::

3. Probe A has priority 0 and half sizes 4, 4 and 4 m. Probe B has priority 0 and half sizes 2, 2 and 2 m. Probe C has priority 1 and half sizes 20, 20 and 20 m. A pixel lies inside all three boxes, deeper than every blend distance. Which two blend, and in which order?

   :::answer{tests="gather-cache,lookup-blend"}
   The order is C, B, A: priority comes first, then the smaller box. The shader stops after two probes, so C and B blend. C has weight 1, so it takes everything, and B's share is 1 × (1 - 1) = 0. A is never read.
   :::

4. Five captures come into view in one frame, and the renderer spreads conversions. How many frames pass until every probe is converted, and what lights a probe's box meanwhile?

   :::answer{tests="gather-cache"}
   Three frames: two, two and one. A probe whose capture is not converted yet lights nothing, so the sky, or the constant ambient light, fills its box. Captures that are not loaded yet also wait, held whole by the gather.
   :::

5. A programmer sets the quality to `Ultra` and bakes a probe, expecting reflections of nearby things from the screen-space reflections of `Ultra` in the picture. What does the picture hold, and why?

   :::answer{tests="bake"}
   The picture holds none. `ForBake` copies Medium's values as a Custom preset, so the project's quality never enters. Medium's reflections are Checkerboard, which needs temporal anti-aliasing, and a bake has none; its global illumination is Off.
   :::

6. What does a slot hold after a conversion, and which two numbers set its size?

   :::answer{tests="conversion"}
   A slot holds a cube with six levels, one for each roughness step 0, 0.2 to 1, and nine irradiance coefficients per color channel in the probe buffer. The levels are set by `ReflectionProbeResolution` (128 or 256 texels), and the number of levels is `c_ReflectionProbeMipCount`, 6. The irradiance is projected from the cube's 32-texel level.
   :::

## Exercises

1. **Basic.** Trace it yourself. Find where one `lighting.bakeProbes` bake renders a probe's six views, which function moves the bake on each frame, and on which thread each of its four stages runs.

   :::answer[Worked solution]{tests="bake"}
   Search for `lighting.bakeProbes` in `StrataEditor/src/Editor/`. It is registered in `RegisterLightingCommands` in `EditorLightingCommands.cpp` with `MayDefer`, so the handler makes a `BakeState` and returns `EditorCommandResult::Defer` with a poll. The poll calls `PollBake` on the main thread every frame, and in `PollBake` the `BakeStage` enum chooses the function.

   **Render**: `RenderNextProbe` renders one probe's six views on the main thread, with the bake's own renderer. **Encode**: `EncodeCaptures` polls the readbacks on the main thread and submits the assembly and the encoding to a job on the job system's worker threads.

   **Write**: `PollBake` checks the I/O job that `EncodeCaptures` submitted with `JobSystem::SubmitIO`, and the file is written on an I/O thread. **Import**: `EditorAssetManager::ImportExternal` copies and imports in the background, and `PollBake` on the main thread calls `ApplyBake` once the import finishes.
   :::

2. **Medium.** Write a small program that gives out slots by least recent use, and trace three gathers with three slots: captures 11, 12 and 13, then 11 and 14, then 14, 15 and 11. Which capture does the third gather remove, and why not 11?

   :::answer[Worked solution]{tests="gather-cache" solution="sketches/indirect-probes-slots.cpp"}
   The program below copies the logic of `acquireSlot`. A capture that has a slot keeps it. Otherwise the loop picks an empty slot or the one with the smallest `LastUsed` that the current gather has not touched.

   ```cpp sketch="indirect-probes-slots.cpp"
   #include <cstdio>

   struct Slot
   {
   	int Capture = 0; // 0: empty
   	unsigned LastUsed = 0;
   };

   // The slot holding `capture`, else an empty one, else the least recently used one that this gather has not used.
   int AcquireSlot(Slot* slots, int count, int capture, unsigned gather)
   {
   	int replaceable = -1;
   	for (int index = 0; index < count; index++)
   	{
   		if (slots[index].Capture == capture)
   			return index;
   		if (slots[index].LastUsed == gather)
   			continue;
   		if (replaceable < 0 || slots[index].Capture == 0 || (slots[replaceable].Capture != 0 && slots[index].LastUsed < slots[replaceable].LastUsed))
   			replaceable = index;
   	}
   	slots[replaceable] = Slot { capture, 0 };
   	return replaceable;
   }

   void Gather(Slot* slots, int count, const int* captures, int captureCount, unsigned gather)
   {
   	for (int index = 0; index < captureCount; index++)
   		slots[AcquireSlot(slots, count, captures[index], gather)].LastUsed = gather;
   	std::printf("gather %u:", gather);
   	for (int index = 0; index < count; index++)
   		std::printf(" [%d used %u]", slots[index].Capture, slots[index].LastUsed);
   	std::printf("\n");
   }

   int main()
   {
   	Slot slots[3] = {};
   	const int first[3] = { 11, 12, 13 };
   	const int second[2] = { 11, 14 };
   	const int third[3] = { 14, 15, 11 };
   	Gather(slots, 3, first, 3, 1);
   	Gather(slots, 3, second, 2, 2);
   	Gather(slots, 3, third, 3, 3);
   	return 0;
   }
   ```

   ```text output-of="indirect-probes-slots.cpp"
   gather 1: [13 used 1] [12 used 1] [11 used 1]
   gather 2: [14 used 2] [12 used 1] [11 used 2]
   gather 3: [14 used 3] [15 used 3] [11 used 3]
   ```

   1. **Lines 15–16:** a capture that already has a slot keeps it.
   2. **Lines 17–18:** a slot this gather already used is skipped.
   3. **Lines 19–20:** an empty slot, or one with an older stamp than the candidate, becomes the candidate.
   4. **Lines 22–23:** the chosen slot starts again with the new capture and a stamp of 0.

   The first gather fills the empty slots from the last one backward, because an empty slot always replaces the candidate, as in the engine. In gather 2, capture 14 needs a slot: 13 and 12 were both last used in gather 1, and the first of equal slots stays the candidate, so 13 goes. In gather 3, capture 15 removes 12, the only slot left with a gather 1 stamp. Capture 11 is safe because gather 2 used it.
   :::

3. **Hard.** Add a debug view that shows a probe's weight, as the way to see a box's reach, since the Scene view draws no box. Which files change?

   :::answer[Worked solution]{tests="lookup-blend"}
   A debug view is a value in the enum `SceneLightingView` in `Strata/src/Strata/Renderer/SceneRenderer.h` and a constant in `Strata/shaders/Include/Scene.slang`, next to `ST_LIGHTING_VIEW_OPEN_SHARE`. The shader `Strata/shaders/Scene/Forward.frag.slang` shades the view: call `EvaluateReflectionProbes` and return `float3(light.Weight)`. The functions that list the views whose values are not light, `SceneRendererLightingView.cpp` and the matching function of `Forward.frag.slang`, need the new value too, so the image is written without exposure. The editor lists views in `ViewportDebugView` in `StrataEditor/src/Editor/StreamingView.h`, its names in `StreamingView.cpp` and its menu in `StrataEditor/src/Panels/ViewportPanel.cpp`. A new GPU test renders a probe's box with the view and checks that the weight is 1 deep inside, near 0 at a face and 0 outside.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RendererComponents.h`: `ReflectionProbeComponent` and `c_MinExtent`.
- `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp`: `GatherReflectionProbes`, `IsStronger`, `EnsureReflectionProbeResources`, `ConvertReflectionProbes`, `ReleaseStaleReflectionProbeHolds`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `SceneRendererSpecification::ForBake`.
- `Strata/shaders/Include/ReflectionProbes.slang`, `Strata/shaders/IBL/ProbeIrradiance.comp.slang` and `Strata/shaders/Include/SphericalHarmonics.slang`: the lookup, the weight and the projection.
- `StrataEditor/src/Editor/EditorLightingCommands.cpp` and `ProbeBake.h`: `lighting.bakeProbes`, `RenderNextProbe`, `PollBake`, `ApplyBake`, `ChoosePreExposure`.
- Statistics: `ReflectionProbes`, `ReflectionProbeConversions` and `ReflectionProbesPending` of `SceneRendererStats`.
- Tests: `GPU.SceneRenderer.ReflectionProbes`, `GPU.Editor.Lighting`, `Editor.Lighting`.

## Further reading

- Sébastien Lagarde and Antoine Zanuttini, "Local image-based lighting with parallax-corrected cubemaps" (SIGGRAPH talk, 2012; intermediate): box projection and blending as shipped in a game.
- Ravi Ramamoorthi and Pat Hanrahan, "An efficient representation for irradiance environment maps" (SIGGRAPH paper, 2001; advanced): why nine coefficients are enough for matte light, and the band factors.
- Sébastien Lagarde and Charles de Rousiers, "Moving Frostbite to physically based rendering" (SIGGRAPH course notes, 2014; advanced): probes in a shipped engine, and the run-time capture of the Alternatives table.
