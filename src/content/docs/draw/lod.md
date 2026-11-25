---
id: draw/lod
title: "Levels of detail"
description: "How Strata draws fewer triangles on small meshes: the two selection rules, why CPU and GPU agree to the bit, and the dithered cross-fade."
kind: internals
size: M
tracks: [E]
needs: [draw/batching]
time: 60
learn:
  - id: choose-level
    text: compute the level that a screen fraction selects under the halving rule and under the error rule
  - id: exact-agreement
    text: explain why the CPU and the GPU must choose the same level, and why the rules use doublings and one multiplication
  - id: fade-states
    text: trace the fade codes that UpdateLODFade gives for a target level that changes and changes back
  - id: fade-alike
    text: explain why the depth prepass and the forward pass must discard the same pixels of a cross-fade
since: 0.3.0
status: final
---

A mesh that fills the screen needs every triangle. The same mesh far away covers a few pixels, and thousands of triangles then land on the same pixels. This part of the :term[renderer]{id=renderer} chooses, for each :term[submesh]{id=submesh} of each mesh renderer in a view, which **level of detail** (LOD) to draw: one of several versions of the mesh, each with fewer triangles.

Pure functions that the :term[central processing unit]{id=processor} (CPU) path and the :term[graphics processing unit]{id=gpu} (GPU) path share make the choice, and a short fade hides each change of level. It does not make the levels: the :term[importer]{id=importer} does that, and [Models and glTF](../assets/models-gltf.md) teaches it.

## The problem and how engines solve it

Take a rock with 20,000 triangles. Close to the camera, the triangles are large enough to see. At 200 metres, the whole rock covers four pixels, yet the graphics card still processes 20,000 triangles for it. Small triangles also shade badly, because a pixel then holds the color of many tiny pieces, and the result shimmers when the camera moves.

The cure is to keep a few simplified copies of the mesh and draw the one that matches how large it looks. Engines differ in two choices: how to measure "how large it looks", and how to change from one copy to the next.

The oldest measure is **distance**: level 1 beyond 20 metres, level 2 beyond 50. It is cheap, but it ignores size. A house and a pebble at 50 metres need very different detail, and a change of :term[field of view]{id=field-of-view} changes what the distance means.

The second measure is the screen size: the share of the viewport height that the mesh covers, the screen fraction that [bounds and culling](../draw/bounds-culling.md) teaches. A pebble and a house at the same fraction get the same level, and a zoom lens changes the level as it should. The cost is that someone must still choose the thresholds by eye.

The third measure counts the damage. Every simplified level stores its **LOD error**, also called the geometric error: the largest distance, in the mesh's own units, between its surface and the full mesh. The engine projects that error onto the screen and picks the coarsest level whose error stays within a budget of pixels. Systems for hierarchical levels of detail and Nanite, Unreal Engine's virtual geometry, rest on this idea. One budget means the same for every mesh.

Some engines go further with **continuous levels**: a mesh that can drop one triangle at a time, or clusters of triangles that the engine chooses one by one. They give the smoothest result, but they need special :term[data structures]{id=data-structure}, and choosing costs more.

The second choice is the change. A pop switches levels in one frame: it is free, and it shows whenever the two levels differ. A **LOD cross-fade** draws both levels for some frames, each on a share of the pixels, like a screen door that opens a little more each frame. Morphing moves each vertex of the finer level toward its place on the coarser one before the switch. It looks best, and it needs vertex data that links the levels.

:::elsewhere[Other engines]
Unreal Engine's documentation of Nanite describes error-driven clusters that need no level lists. A paper on progressive meshes describes the continuous approach. Both are in Further reading.
:::

Strata chooses discrete levels, by error where the levels have one, with a dithered cross-fade. The importer generates the levels and their errors, so the choice at run time is a few multiplications. Meshes whose levels carry no error, such as meshes built in code or older cooked ones, halve the screen fraction instead. The price: levels are fixed copies that cost memory, nothing morphs, and a fade draws two levels at once for 16 frames.

## The map

Three places hold the work. `LODSelection` is a set of pure functions: it reads numbers and returns numbers, and it touches no scene. `SceneRenderer` calls it while it gathers draws on the CPU. The :term[shader]{id=shader} `Include/LODSelection.slang` repeats it for `Cull.comp`, the GPU culling pass that [GPU-driven drawing](../draw/gpu-driven.md) teaches.

```mermaid caption="Where a level is chosen: the CPU path and the GPU path call the same rules, and the fade code travels in the draw list entry to the two passes that discard by it." alt="A diagram. The screen fraction and the level errors enter the selection rules. The CPU gather calls the C++ rules, and the culling pass calls the shader copy. The result and the fade state give a draw list entry with a fade code. The prepass and the forward pass both read the code."
flowchart LR
	F[screen fraction] --> R1[LODSelection.cpp]
	F --> R2[LODSelection.slang]
	E[level errors] --> R1
	E --> R2
	R1 --> G[SceneRenderer::GatherDraws]
	R2 --> C[Cull.comp]
	G --> S[UpdateLODFade]
	S --> D[draw list entry with fade code]
	C --> D
	D --> P[depth prepass]
	D --> W[forward pass]
```

A renderer also hands tools a `LODCriteria` (from `SceneRenderer::GetLODCriteria`): the halving threshold, the error threshold and the viewport height. A tool such as the editor's LOD view calls the same functions with the same criteria, so it shows the level that the renderer draws without drawing anything. The functions need no GPU, so unit tests run them anywhere.

## The contract

Callers and shaders rely on these rules. Each has a reason.

- The screen fraction is the projected diameter of the :term[bounding sphere]{id=bounding-sphere} divided by the viewport height. A perspective camera divides by the distance (at least the :term[near plane]{id=near-plane}) and by the tangent of half the field of view. Without a fixed definition the two paths would measure different sizes.
- Level 0 is full detail. A mesh with one level, or a fraction that is zero, negative or not finite, draws level 0, because there is nothing to choose or nothing to trust.
- A submesh chooses by error only when every simplified level has a positive error. A level with error 0 would always pass the test, and could be drawn at any size, so such a submesh halves instead.
- The CPU and the GPU return the same level for the same fraction and the same errors. If they differed, a mesh would change level whenever the renderer switches paths, and the two images would not match.
- The fade code in a :term[draw list]{id=draw-list} entry, and the test that reads it, are the same in the depth prepass and the forward pass.

:::rule[Both paths decide alike]
The CPU path and `Cull.comp` both decide what is drawn, so a change to one is a change to the other. The reason is the agreement above. The [GPU-driven drawing page](../draw/gpu-driven.md) shows the second path, and the [frame tour](../gpu/frame-tour.md) explains why those two passes may differ in no pixel.
:::

## A toy version

:::question
The next fences use functions, a loop, a `std::vector` and calls such as `std::printf(`, taught in [Programming 2](../basics/programming-2.md) and [Programming 3](../basics/programming-3.md).
:::

The toy takes a list of relative errors and a fraction. It holds the two rules in under 50 lines and prints what each rule picks for six fractions of a mesh with levels 0 to 3. Look at how little `ChooseByError` does.

```cpp sketch="draw-lod-toy.cpp"
// A toy level chooser: by halving the screen fraction, and by the levels' relative errors.
#include <cstdint>
#include <cstdio>
#include <initializer_list>
#include <vector>

// Level 0 is full detail; level n is chosen below threshold / 2^(n-1).
uint32_t ChooseByHalving(float fraction, float threshold, uint32_t levelCount)
{
	if (levelCount <= 1 || !(fraction > 0.0f && fraction < threshold))
		return 0;
	uint32_t level = 1;
	float doubled = fraction * 2.0f;
	while (level + 1 < levelCount && doubled < threshold)
	{
		level++;
		doubled *= 2.0f;
	}
	return level;
}

// The coarsest level whose projected error stays within the threshold. Entry 0 is never read.
uint32_t ChooseByError(float fraction, const std::vector<float>& relativeErrors, float errorThreshold)
{
	if (relativeErrors.size() <= 1 || !(fraction > 0.0f))
		return 0;
	for (size_t level = relativeErrors.size() - 1; level > 0; level--)
	{
		if (fraction * relativeErrors[level] <= errorThreshold)
			return static_cast<uint32_t>(level);
	}
	return 0;
}

int main()
{
	const float viewportHeight = 1080.0f;
	const float errorPixels = 1.0f;
	const float errorThreshold = errorPixels / (viewportHeight * 0.5f);
	const std::vector<float> relativeErrors = { 0.0f, 0.01f, 0.04f, 0.16f };
	std::printf("error threshold %.6f\n", static_cast<double>(errorThreshold));
	for (float fraction : { 0.6f, 0.2f, 0.1f, 0.05f, 0.02f, 0.005f })
	{
		const uint32_t byHalving = ChooseByHalving(fraction, 0.5f, 4);
		const uint32_t byError = ChooseByError(fraction, relativeErrors, errorThreshold);
		std::printf("fraction %.3f: halving level %u, error level %u\n", static_cast<double>(fraction), byHalving, byError);
	}
	return 0;
}
```

```text output-of="draw-lod-toy.cpp"
error threshold 0.001852
fraction 0.600: halving level 0, error level 0
fraction 0.200: halving level 2, error level 0
fraction 0.100: halving level 3, error level 1
fraction 0.050: halving level 3, error level 1
fraction 0.020: halving level 3, error level 2
fraction 0.005: halving level 3, error level 3
```

1. **Lines 13-17:** the halving loop; each pass doubles the fraction and adds a level.
2. **Lines 27-31:** the error scan from the coarsest level down.
3. **Line 39:** one pixel of a viewport 1080 pixels high, as a share of its half height.

Read the numbers by hand first. A 1080-pixel viewport and a budget of 1 pixel give the **error threshold** 1 / 540 = 0.00185: the largest product of screen fraction and relative error that stays within the budget.

The **relative error** is a level's error divided by the radius of the mesh's bounds, so it has no unit. The radius is half the diagonal of the bounds, half of the diameter that the fraction measures, which is why the threshold divides by half the height.

:::example[A rock at six fractions]
The rock has levels 1, 2 and 3 with relative errors 0.01, 0.04 and 0.16. At fraction 0.05, level 3 spans 0.05 × 0.16 × 540 = 4.3 pixels, too many. Level 2 spans 1.08 pixels, still too many. Level 1 spans 0.27 pixels, so level 1 is drawn.

At fraction 0.02 level 2 spans 0.43 pixels and level 3 spans 1.73, so the answer is level 2. At 0.005 level 3 spans 0.43 pixels, so the rock uses its coarsest level.

The halving rule, with threshold 0.5 and four levels, gives level 2 for 0.2, because 0.2 is below 0.25 but not below 0.125. It also gives level 3 for 0.05. The two rules disagree at 0.2: halving says 2, error says 0. They answer different questions, and the error rule is the one that knows the mesh.
:::

The toy hides three things: the exact agreement of CPU and GPU, the cross-fade, and the way the engine keeps errors with the mesh.

## The real code

Data flows in this order: the screen fraction, the rule, the level, the fade, the draw list entry.

### The halving rule

Level 1 starts below the threshold, and each further doubling of the fraction that still stays below it adds one level. This quote is the whole function; look at the loop and at its comment.

```cpp src="Strata/src/Strata/Renderer/LODSelection.cpp#L19-L34"
uint32_t SelectLOD(float screenFraction, float lodThreshold, uint32_t lodCount)
{
	if (lodCount <= 1 || !(screenFraction > 0.0f && screenFraction < lodThreshold))
		return 0;
	// Level 1 below the threshold, and one more for each doubling of the fraction that stays below it. Doubling a float is
	// exact, so these comparisons give the GPU's culling (Include/LODSelection.slang) the same level for the same fraction,
	// which a logarithm would not.
	uint32_t lod = 1;
	float doubled = screenFraction * 2.0f;
	while (lod + 1 < lodCount && doubled < lodThreshold)
	{
		lod++;
		doubled *= 2.0f;
	}
	return lod;
}
```

1. **Line 21:** a mesh with one level, or a fraction at or above the threshold, draws level 0.
2. **Lines 26-27:** level 1 starts below the threshold; the test looks one doubling ahead.
3. **Lines 28-31:** each doubling that still stays below the threshold adds a level, up to the last.

The natural formula is 1 plus the whole part of the base-2 :term[logarithm]{id=logarithm} of the threshold divided by the fraction. A logarithm is a library routine on the CPU and a hardware routine on the GPU, and their last digits can differ. Where the fraction is exactly the threshold over a power of two, one side could round down and the other not, and the two paths would choose different levels. Doubling is exact, so the loop agrees everywhere.

### The error rule

The error rule scans from the coarsest level down and returns the first level whose projected error fits.

```cpp src="Strata/src/Strata/Renderer/LODSelection.cpp#L60-L70"
uint32_t SelectLODByError(float screenFraction, std::span<const float> relativeErrors, float errorThreshold)
{
	if (relativeErrors.size() <= 1 || !(screenFraction > 0.0f) || !std::isfinite(screenFraction))
		return 0;
	for (size_t level = relativeErrors.size() - 1; level > 0; level--)
	{
		if (IsErrorWithin(screenFraction, relativeErrors[level], errorThreshold))
			return static_cast<uint32_t>(level);
	}
	return 0;
}
```

1. **Line 62:** a mesh with at most one level, or a fraction that is not positive or not finite, draws level 0.
2. **Lines 64-67:** the scan runs from the coarsest level down; the first level that fits wins, and entry 0 is never read.

The test itself, `IsErrorWithin` a few lines above, is one multiplication and one comparison, written alone so that nothing mixes with it. The submesh form of `SelectLOD` chooses the rule with `MeshUtils::HasLODErrors` and takes each level's relative error from `MeshUtils::GetRelativeLODError`. `LODSelection::GetErrorThreshold` divides the pixel budget by half the viewport height.

### The shader's copy

`Strata/shaders/Include/LODSelection.slang` repeats both rules. This is the error rule; look at the word `precise`.

```slang src="Strata/shaders/Include/LODSelection.slang#L23-L39"
#ifdef ST_LOD_RELATIVE_ERROR
// The coarsest level whose projected error stays within the threshold, exactly as LODSelection::SelectLODByError chooses
// it: the last level, scanning down to 1, whose relative error times the screen fraction is at most errorThreshold (one
// rounded multiplication, `precise` so that nothing fuses or reorders it), else 0; 0 for a fraction that is not positive or
// not finite. The includer defines ST_LOD_RELATIVE_ERROR(record) to read the relative error of a level, firstLOD + level.
uint SelectLODByError(float screenFraction, uint firstLOD, uint lodCount, float errorThreshold)
{
	if (lodCount <= 1u || !(screenFraction > 0.0) || isinf(screenFraction))
		return 0u;
	for (uint level = lodCount - 1u; level > 0u; level--)
	{
		precise float projected = screenFraction * ST_LOD_RELATIVE_ERROR(firstLOD + level);
		if (projected <= errorThreshold)
			return level;
	}
	return 0u;
}
```

1. **Lines 30-31:** the same guards as in C++, with `isinf` for a fraction that is not finite.
2. **Line 34:** `precise` makes the :term[compiler]{id=compiler} round this product once, as the C++ function does.

A shader :term[compiler]{id=compiler} may fuse a multiplication with a nearby addition, or change the order of operations, because it assumes that the last digit does not matter. Here it does matter, and `precise` forbids the change. The shader reads the relative error through the :term[macro]{id=macro} `ST_LOD_RELATIVE_ERROR`, which the including shader defines. In `Include/Culling.slang`, `ChooseLODFor` picks the rule by a flag of the submesh.

### The quality rows

Two quality rows feed the rules. Their four presets stand in `Strata/src/Strata/Renderer/RendererQuality.cpp`, and [quality settings](../image/quality-settings.md) teaches the rows.

| Row (as the editor shows it) | Field | **Low** | **Medium** | **High** | **Ultra** |
| --- | --- | --- | --- | --- | --- |
| Level of detail error (pixels) | `LODErrorPixels` | 2 | 1 | 1 | 0.5 |
| Smallest drawn size (pixels) | `MinProjectedPixels` | 1 | 0.5 | 0.5 | 0.25 |

The first row is the pixel budget of the error rule: a larger budget accepts coarser levels. The second row is not a level: a mesh renderer whose bounding sphere projects smaller than this many pixels is not drawn at all, by either path. A value of 0 draws full detail in the first row, and everything in the second.

### The cross-fade

When the level of a view instance changes, `UpdateLODFade` keeps both levels on screen for `c_LODFadeFrames`, 16 frames. The new level covers a growing share of the pixels, and the old one covers the rest. Only opaque draws fade, and a renderer that makes single images, such as the one that draws thumbnails or the one that bakes light probes, turns fading off.

The share is a 4×4 :term[ordered dither]{id=ordered-dither}: a table that gives every pixel of a tile of 16 a threshold from 0 to 15. Step 1 of the fade draws the new level where the threshold is below 1, that is 1 pixel of every 16. Step 8 draws it where the threshold is below 8, half of them, and step 15 draws all but one. The old level draws exactly the pixels that the new level leaves, so the two masks are complementary: no pixel is empty and none is drawn twice.

| 0 | 8 | 2 | 10 |
| --- | --- | --- | --- |
| 12 | 4 | 14 | 6 |
| 3 | 11 | 1 | 9 |
| 15 | 7 | 13 | 5 |

Each step hands the new level more pixels of every tile:

::figure{id=lod-fade-masks}

An instance keeps its state in 32 bits, with its entity in a second word. The 32 bits hold the level shown (4 bits), the level fading out (4 bits), the step (5 bits) and the frame number (19 bits). The fade code of a draw list entry is the step, from 1 to 15. The level that fades out adds 16 to it, and code 0 means no fade.

```cpp src="Strata/src/Strata/Renderer/LODSelection.cpp#L98-L144"
LODFade UpdateLODFade(LODFadeState state, uint32_t target, uint32_t lodCount, uint32_t entityID, uint32_t frame, bool enabled)
{
	constexpr uint32_t c_Frames = RenderData::c_LODFadeFrames;
	LODFade result;
	result.From = target;
	if (!enabled || target > c_MaxFadedLOD)
		return result; // No history kept: drawn at once, now and when fades start again
	uint32_t lod = state.Packed & 15u;
	uint32_t from = (state.Packed >> 4) & 15u;
	uint32_t step = (state.Packed >> 8) & 31u;
	const uint32_t last = state.Packed >> 13;
	const bool continuing = state.Packed != 0 && state.EntityID == entityID && last == ((frame - 1u) & c_FadeFrameMask) && lod < lodCount && from < lodCount
		&& step >= 1 && step <= c_Frames;
	if (!continuing)
	{
		lod = target;
		from = target;
		step = c_Frames;
	}
	else if (target != lod)
	{
		if (step < c_Frames && target == from)
		{
			// Back to the level fading out: each keeps the pixels it has.
			from = lod;
			step = c_Frames - step;
		}
		else
		{
			// From the level on more pixels now.
			from = step < c_Frames && 2 * step < c_Frames ? from : lod;
			step = 1;
		}
		lod = target;
	}
	else if (step < c_Frames)
	{
		step++;
	}
	if (from == lod)
		step = c_Frames;
	result.State.Packed = lod | (from << 4) | (step << 8) | ((frame & c_FadeFrameMask) << 13);
	result.State.EntityID = entityID;
	result.Code = step < c_Frames ? step : 0u;
	result.From = from;
	return result;
}
```

1. **Lines 108-110:** the fade continues only for the same entity, on the frame after the last one, with levels in range.
2. **Lines 113-115:** otherwise the level is drawn at once; the renderer's fade frame number skips one at a camera cut, so cuts never fade.
3. **Lines 119-123:** a target that is the level fading out swaps the roles and mirrors the step, so each level keeps its pixels.
4. **Lines 128-129:** any other new target restarts at step 1, from the level that covers more pixels now.
5. **Lines 133-135:** an unchanged target moves one step on, until 16 returns the code to 0.

The rule that makes the fade safe is the mask test of the shader:

```slang src="Strata/shaders/Include/Scene.slang#L171-L182"
// Whether a draw with this cross-fade code covers the pixel (LODSelection::IsLODFadeDrawn): the level fading in (codes 1-15)
// where the 4x4 ordered dither threshold is below the code, the level fading out (the code plus 16) on the other pixels.
// The depth prepass and the forward pass test the same, so the EQUAL depth test holds.
bool IsLODFadeDrawn(uint code, float2 fragCoord)
{
	if (code == 0u)
		return true;
	const uint bayer[16] = { 0u, 8u, 2u, 10u, 12u, 4u, 14u, 6u, 3u, 11u, 1u, 9u, 15u, 7u, 13u, 5u };
	uint2 pixel = uint2(fragCoord) & 3u;
	uint threshold = bayer[pixel.y * 4u + pixel.x];
	return code < ST_LOD_FADE_OUTGOING_CODE ? threshold < code : threshold >= code - ST_LOD_FADE_OUTGOING_CODE;
}
```

1. **Line 178:** the 4×4 table above, row by row.
2. **Line 181:** the new level where the threshold is below the code, the old one on the others.

The depth prepass and the forward pass both call this test with the pixel's position. The forward pass draws with the `EQUAL` depth test, which accepts a fragment only if its depth is exactly the one the prepass wrote. Suppose the prepass drew the new level on a pixel and the forward pass tried the old level there. The depths differ, the test fails, and a hole shows. The [frame tour](../gpu/frame-tour.md) explains the prepass and the equal test.

### The LOD debug view

The Scene view's debug view list has the entry "LOD: level of detail drawn". It tints every entity by the level it is drawn at, and the view's statistics count entities per level and report the largest error, in pixels, of each level chosen by error. An entity with several submeshes shows the most simplified level among them. The command `viewport.setSettings` with `{"debugView":"lod"}` selects it, and [Debugging](../gpu/debugging.md) teaches the debug views.

::compare{id=lod-view}

A field of props at **Low** and at **Ultra** differs in the share of entities at each level: the larger budget of the first pushes more of them to coarse levels.

:::note[What Strata does not do]
Strata has no billboards: a far object is a coarse mesh, never a flat picture of itself, and a mesh below the smallest drawn size is not drawn. Distant cells of a world are not drawn either; [why streaming](../worlds/why-streaming.md) teaches that.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Levels by distance | Many older engines | A rule an artist reads at once | Sizes and fields of view that change the meaning; two numbers per level to tune |
| Continuous levels and virtual geometry | Unreal Engine's Nanite | No visible steps, no level copies | A different mesh format, a large rewrite of culling and drawing |
| Morphing the vertices | Terrain systems | No dither grain in the transition | Vertex data that links levels; it fits terrain better than props |
| Pop at once | Simple engines | No second draw, no mask | A visible jump; shimmer at the boundary |
| Flat pictures of far objects | Forest and city renderers | Very cheap far objects | A picture per object, new passes, and a second kind of fade |

## How it is tested

The suite `Renderer.LODSelection` needs no GPU. Its cases check the screen fraction and that each halving adds a level up to the last. They also check that the level counts exact doublings as the logarithm does away from its boundaries, the error rule against `LODErrorPixels`, and the choice of rule for a submesh.

Two more cases check the fade over 16 frames with complementary masks, and that the masks cover every pixel once.

The suite `GPU.Renderer.LODSelection` runs the test shader `Debug/LODSelection.comp.slang` on 10,000 fractions, with every exact doubling onto the threshold among them. It compares the result with the CPU for both rules.

The suite `GPU.SceneRenderer.LODFade` renders. One case checks that a changed level cross-fades through complementary masks on both paths and that a camera cut switches at once. Another checks that levels covering the same pixels at the same depth fade by the same mask in the forward pass. Two cases of `GPU.Editor.StreamingView` check the LOD view. Run them like this:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.LODSelection
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.Renderer.LODSelection,GPU.SceneRenderer.LODFade
```

The first line needs no graphics card. The second needs a graphics card.

## Changing it safely

A new rule would be a new pure function in `LODSelection` with a copy in `Include/LODSelection.slang`. A mesh built in code opts into the error rule by giving every simplified level a positive `Error`.

- A change to a rule changes the C++ and the shader together; `GPU.Renderer.LODSelection` fails when they drift apart.
- A new input of the choice, such as a bias per entity, must reach `Cull.comp` and the CPU path alike, and the shadow views, which choose levels with their own criteria.
- Keep the arithmetic of the rules to doublings, comparisons and one multiplication: no logarithm and no fused product.

:::rule[Prepass and forward pass agree to the bit]
A new pass that draws opaque instances must test `IsLODFadeDrawn` with the entry's code, because the `EQUAL` depth test accepts nothing else. A pass that skips the test shows holes during every fade.
:::

## Summary

- A level is chosen from the screen fraction by the halving rule, or by the error rule when every simplified level carries an error.
- The CPU and the GPU must choose the same level, so the rules use exact doublings, one multiplication and `precise`, with no logarithm.
- A changed level fades over 16 frames with complementary dither masks, and the state machine continues, reverses or restarts the fade.
- The depth prepass and the forward pass test the same mask, or the equal depth test leaves holes.

## Check yourself

1. A submesh has three levels without errors, and the threshold is 0.5. What level does fraction 0.3 select, and what does 0.1 select?

   :::answer{tests="choose-level"}
   Level 1 for 0.3, because 0.3 is below 0.5 and its double, 0.6, is not. Level 2 for 0.1: it is below 0.25 and below 0.125, but the last level is 2, the most it may reach.
   :::

2. A mesh has relative errors 0.02 and 0.08 for levels 1 and 2, in a 1000-pixel viewport with a budget of 1 pixel. Which level does fraction 0.1 select?

   :::answer{tests="choose-level"}
   The threshold is 1 / 500 = 0.002. Level 2 projects 0.1 × 0.08 = 0.008, too large. Level 1 projects 0.1 × 0.02 = 0.002, which is at most the threshold, so level 1.
   :::

3. Which reason makes the rules avoid a logarithm?

   - A. A logarithm is too slow for the GPU.
   - B. The CPU's and the GPU's logarithms can differ in the last digits, so the paths could choose different levels at a boundary.
   - C. A logarithm cannot be written in a shader.

   :::answer{tests="exact-agreement"}
   B. A is wrong: speed is not the reason. C is wrong: shaders have a logarithm, but its digits may differ from the CPU's.
   :::

4. The forward pass used a different dither table from the prepass. What does the viewer see during a fade?

   :::answer{tests="fade-alike"}
   Holes and flicker. On pixels where the two tables disagree, the forward pass draws a level at a depth that is not the one the prepass wrote, and the `EQUAL` test rejects it.
   :::

5. A mesh renderer shows level 1 with no fade under way, and its target becomes level 2. What code does the next frame's entry carry, and which level fades out?

   :::answer{tests="fade-states"}
   Code 1, and level 1 fades out. The state continues, the target differs, and the step restarts at 1 from the level that now covers more pixels. Level 2 then covers one pixel of 16.
   :::

## Exercises

1. **Basic.** Find where the CPU and the GPU choose the level of a submesh, and show that each uses the errors where the submesh has them and halves otherwise.

   :::answer[Worked solution]{tests="exact-agreement"}
   Search for `SelectLOD`. On the CPU, `SceneRenderer::SelectLOD` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`, called by the gather code, calls `LODSelection::SelectLOD` in `Strata/src/Strata/Renderer/LODSelection.cpp`, which tests `MeshUtils::HasLODErrors`. On the GPU, `ChooseLODFor` in `Strata/shaders/Include/Culling.slang`, called by `ChooseLOD` in the same file, which `Cull.comp` calls, tests the flag of the submesh and calls `SelectLODByError` or `SelectLOD`.
   :::

2. **Hard.** Drive a fade through a target that is level 0 until frame 4, level 1 for frames 5 to 8, and level 0 again from frame 9. Predict the codes, then check them.

   :::answer[Worked solution]{tests="fade-states"}
   At frame 5 the step is 1, so the code is 1 and level 0 fades out; frames 6 to 8 give 2, 3 and 4. At frame 9 the target is the level fading out, so the roles swap and the step mirrors to 16 − 4 = 12. Frames 10 to 12 give 13, 14 and 15, and frame 13 returns to 0.

   ```cpp sketch="draw-lod-fade.cpp"
   // A standalone copy of the fade state machine, driven by a target level that changes at frame 5 and back at frame 9.
   #include <cstdint>
   #include <cstdio>

   constexpr uint32_t c_Frames = 16;

   struct Fade
   {
   	uint32_t Lod = 0;
   	uint32_t From = 0;
   	uint32_t Step = c_Frames;
   	bool Started = false;
   };

   // Returns the draw entry's code: 0 draws every pixel, 1 to 15 is the step of a fade under way.
   uint32_t Update(Fade& fade, uint32_t target)
   {
   	if (!fade.Started)
   	{
   		fade = { target, target, c_Frames, true };
   		return 0;
   	}
   	if (target != fade.Lod)
   	{
   		if (fade.Step < c_Frames && target == fade.From)
   		{
   			fade.From = fade.Lod;
   			fade.Step = c_Frames - fade.Step;
   		}
   		else
   		{
   			fade.From = fade.Step < c_Frames && 2 * fade.Step < c_Frames ? fade.From : fade.Lod;
   			fade.Step = 1;
   		}
   		fade.Lod = target;
   	}
   	else if (fade.Step < c_Frames)
   	{
   		fade.Step++;
   	}
   	if (fade.From == fade.Lod)
   		fade.Step = c_Frames;
   	return fade.Step < c_Frames ? fade.Step : 0;
   }

   int main()
   {
   	Fade fade;
   	for (uint32_t frame = 0; frame < 15; frame++)
   	{
   		const uint32_t target = frame >= 5 && frame < 9 ? 1 : 0;
   		const uint32_t code = Update(fade, target);
   		std::printf("frame %2u: target %u, code %2u, fading out level %u\n", frame, target, code, fade.From);
   	}
   	return 0;
   }
   ```

   ```text output-of="draw-lod-fade.cpp"
   frame  0: target 0, code  0, fading out level 0
   frame  1: target 0, code  0, fading out level 0
   frame  2: target 0, code  0, fading out level 0
   frame  3: target 0, code  0, fading out level 0
   frame  4: target 0, code  0, fading out level 0
   frame  5: target 1, code  1, fading out level 0
   frame  6: target 1, code  2, fading out level 0
   frame  7: target 1, code  3, fading out level 0
   frame  8: target 1, code  4, fading out level 0
   frame  9: target 0, code 12, fading out level 1
   frame 10: target 0, code 13, fading out level 1
   frame 11: target 0, code 14, fading out level 1
   frame 12: target 0, code 15, fading out level 1
   frame 13: target 0, code  0, fading out level 1
   frame 14: target 0, code  0, fading out level 1
   ```

   1. **Lines 25-28:** a target that is the level fading out mirrors the step.
   2. **Lines 32-33:** any other new target restarts at step 1.
   3. **Lines 37-39:** an unchanged target moves one step on.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/LODSelection.h` and `LODSelection.cpp`: the rules, the screen fraction and the fade.
- `Strata/shaders/Include/LODSelection.slang` and `Strata/shaders/Include/Scene.slang`: the shader copies and `IsLODFadeDrawn`.
- `Strata/src/Strata/Renderer/RendererQuality.cpp`: the rows and their presets.
- `StrataTests/src/Renderer/LODSelectionTests.cpp` and `GPUSceneRendererGPUDrivenTests.cpp`: the tests.

## Further reading

- Epic Games, documentation of Nanite virtual geometry: error-driven clusters (advanced).
- Hugues Hoppe, "Progressive meshes", SIGGRAPH 1996: continuous levels (advanced).
- Real-Time Rendering, chapter on level of detail, by Akenine-Möller, Haines and Hoffman: the approaches compared (intermediate).
