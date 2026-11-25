---
id: draw/occlusion
title: "Occlusion culling"
description: "How Strata leaves out what is hidden behind other geometry: a depth pyramid, a conservative test and two phases that draw nothing a frame late."
kind: internals
size: L
tracks: [E]
needs: [draw/gpu-driven, gpu/coordinates]
time: 75
learn:
  - id: build-level
    text: compute the levels of a farthest-depth pyramid by hand, including the last row and column
  - id: find-footprint
    text: find the level and texels that a box's screen rectangle reads
  - id: explain-no-lag
    text: explain why two-phase occlusion culling draws nothing a frame late
  - id: name-rules
    text: name the rules that keep occlusion culling conservative and what breaks them
since: 0.4.0
status: final
---

A scene holds many objects inside the camera's view that you still cannot see, because something nearer covers them: a house behind a hill, a room behind a wall. **Occlusion culling** is the step that omits such objects from the frame's draws, and it runs on the :term[graphics processing unit]{id=gpu} (GPU). The job has three limits. It must never hide something that is visible, it must never draw an object a frame late, and it may only use what the :term[renderer]{id=renderer} already has: the :term[depth buffer]{id=depth-buffer} and the frame before. Strata does not do portals, the hand-made doors that tell an engine which room can see which.

## The problem and how engines solve it

:term[Frustum culling]{id=frustum-culling} keeps what lies inside the camera's view, but "inside the view" is not "visible". Picture a wall in front of a hundred boxes. Every box is in the :term[frustum]{id=view-frustum}, so each one costs a draw, and after the depth test the wall wins every pixel. The cost is wasted work, and the cost of a wrong cut is worse: an object that vanishes while you look at it is a bug anyone can see.

So every method below is conservative: when unsure, it draws. Drawing too much costs time; hiding wrongly costs correctness.

Four approaches exist, and the table compares them. The lag of a query matters more than it looks. If the answer arrives two frames later, then at 60 :term[frames per second]{id=frame-rate} (16.7 ms a frame) an object that turns a corner stays missing for 33 ms, long enough to see. Waiting for the answer instead stalls the processor, which costs the time the query was meant to save.

| Approach | How it decides | What it costs |
| --- | --- | --- |
| Hardware occlusion queries | The :term[graphics card]{id=gpu} counts the pixels of a cheap stand-in box that pass the depth test | The answer comes back frames later, so an object appears late or the program waits |
| Software drawing of a few big walls | The central processing unit (CPU) draws a few big, simple walls into a tiny depth image and tests boxes there | The CPU does the work, and someone must choose the walls |
| Last frame's depth, moved to the new camera | Last frame's depth moves to this frame's camera, and boxes are tested against it | Holes appear where the old image has no data, and moving objects fool it |
| Two-phase with a depth pyramid | Draw what was visible last frame, build a depth pyramid of that, test the rest, draw what newly shows | One extra pass and a pyramid per frame; no lag |

Strata chose the last row. A **hierarchical Z-buffer** (HZB) is a chain of ever smaller depth images in which each texel keeps the farthest depth of the texels it covers; it is also called a depth pyramid. The idea comes from Haar and Aaltonen's work on a shipped game, and Unreal Engine's Nanite uses the same two-phase shape. The pyramid answers the question "is anything farther than this box anywhere on its screen rectangle?" with at most four reads, however large the rectangle is.

Without a pyramid, a box that covers 400 by 300 pixels needs 120,000 depth reads. With one, the test finds a level where the rectangle spans two texels each way and reads four. The pyramid keeps the farthest depth, not the average, because that is the worst case: if even the farthest surface of the rectangle is nearer than the box, every pixel of it is.

**Two-phase occlusion culling** is the sequence itself. Phase 1 draws the objects the view saw in the previous frame, and a pyramid is built from that depth. Phase 2 tests every other object and draws those found visible, in the same frame. Phase 2 corrects the guess: an object phase 1 missed is drawn before the frame ends, so nothing appears a frame late. If phase 1 drew an object that is now hidden, the frame pays for one needless draw, and the next frame omits it.

:::why[Why history, and what it costs]
Last frame's visible set is a guess about this frame, and phase 2 repairs the guess in the same frame, so the guess never shows. The pyramid is built from this frame's own phase-1 depth, not from old depth, so moving objects and a moving camera leave no holes. Nobody marks walls by hand: whatever the view draws hides what lies behind it. The price is one more set of compute passes, two bits of history per proxy, and a dearer frame whenever history is missing.
:::

## The map

The pass lives in the :term[depth prepass]{id=depth-prepass} of the GPU-driven path ([GPU-driven draw](../draw/gpu-driven.md) explains the counting and write passes that phase 2 adds to). The :term[main thread]{id=main-thread} only records commands; the graphics card runs them in the order recorded.

```mermaid caption="One frame of two-phase occlusion culling, in the order the commands run, with the visibility bits each step reads and writes." alt="Boxes in order: bits of the previous frame, phase 1 into the prepass, the pyramid, phase 2 with its tests and draws, then this frame's bits and the flipped parity."
flowchart TD
	A["Bits of the previous frame (parity bit)"] --> B["Phase 1: draw objects whose bit is set, into the prepass"]
	B --> C["Build the depth pyramid from that depth"]
	C --> D["Phase 2: test every proxy in the frustum against the pyramid"]
	D --> E["Draw proxies visible now whose bit was not set"]
	D --> F["Write this frame's bit for every proxy"]
	E --> G["Flip the parity: this frame's bits are next frame's history"]
	F --> G
```

Five files hold the work, and the rest of the page follows them in the order the data flows:

- `Strata/src/Strata/Renderer/SceneRenderer.cpp` decides each frame whether there is history and calls the phases.
- `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp` creates the pyramid texture and runs `RunOcclusionPhase`.
- `Strata/shaders/Scene/HZBBuild.comp.slang` builds one level of the pyramid per dispatch.
- `Strata/shaders/Include/Culling.slang` holds `GetPyramidFootprint`.
- `Strata/shaders/Scene/Cull.comp.slang` holds `IsOccluded` and `CullSecondPhase`.

The two switches are fields of `SceneRendererSpecification`: `OcclusionCulling` (default true) and `MinimumSamplerPyramids` (default true; tests disable it to compare the two ways of building the pyramid).

## The contract

Callers may assume that a frame with occlusion culling draws everything a frame without it shows, in the same frame. They must keep three rules, each with its reason.

:::rule[The occlusion test must never hide what is visible]
Drawing too much costs time, but hiding wrongly is a visible bug. Every size in the pyramid is a mip size, the last row and column cover what lies past them, and footprints are clamped to the level. The next sections show each of these, and [What went wrong before](#what-went-wrong-before) shows what a slip costs.
:::

:::rule[New passes that read the view's depth come after phase 2]
Phase 2 adds newly visible objects to the depth buffer. A pass that reads depth earlier sees a buffer with holes where those objects belong, so record it after the second prepass draws. The passes that read the final depth are in [the frame tour](../gpu/frame-tour.md).
:::

:::rule[A test that counts draws allows for history]
A new scene has no history, so the first frames draw more than the steady state. A test of draws renders one frame more before it counts, or disables occlusion culling. A test of requests waits for :term[visibility feedback]{id=visibility-feedback} or disables it, because feedback arrives two to three frames late.
:::

A fourth fact completes the contract. Visibility feedback still marks the assets of a hidden proxy as in view: the feedback code runs before the occlusion test, because a hidden object may show next frame and its textures should be ready.

## A toy version

The toy does on the CPU what the compute :term[shaders]{id=shader} do: build a farthest-depth pyramid of a small depth array and test a pixel rectangle against it. It uses :term[reversed Z]{id=reversed-z} (near is 1, far is 0), so "farthest" is the smallest number; [coordinates](../gpu/coordinates.md) explains why Strata does this. The depth array is 9 by 5 texels: a wall of depth 0.6 on columns 0 to 5, a far background of 0.1, and one hole of depth 0.0 in the wall, like a window.

:::question
New to C++ code like this? Learn the basics in [Programming 1](../basics/programming-1.md), [loops, functions and structs](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md).
:::

Read `Reduce` first: each new texel takes the smallest depth of the source texels it covers, and the last row and column also take every texel past them. Then read `IsOccluded`, which picks a level by the rectangle's size and compares the box's nearest depth with the farthest depth it finds.

```cpp sketch="draw-occlusion-toy.cpp"
// A toy farthest-depth pyramid and an occlusion test, on the CPU. Reversed Z: 1 is near, 0 is far.
#include <algorithm>
#include <cstdio>
#include <vector>

struct Level
{
	int Width = 0;
	int Height = 0;
	std::vector<float> Depth;

	float At(int x, int y) const { return Depth[static_cast<size_t>(y) * Width + x]; }
};

// One level from its source: each texel takes the smallest (farthest) depth of the source texels it covers.
// The last row and column also cover every source texel past them.
Level Reduce(const Level& source, int width, int height, int reduction)
{
	Level level;
	level.Width = width;
	level.Height = height;
	for (int y = 0; y < height; y++)
	{
		for (int x = 0; x < width; x++)
		{
			int lastX = x == width - 1 ? source.Width - 1 : std::min(x * reduction + reduction - 1, source.Width - 1);
			int lastY = y == height - 1 ? source.Height - 1 : std::min(y * reduction + reduction - 1, source.Height - 1);
			float farthest = 1.0f;
			for (int sy = y * reduction; sy <= lastY; sy++)
				for (int sx = x * reduction; sx <= lastX; sx++)
					farthest = std::min(farthest, source.At(sx, sy));
			level.Depth.push_back(farthest);
		}
	}
	return level;
}

std::vector<Level> BuildPyramid(const Level& depth)
{
	std::vector<Level> levels;
	levels.push_back(Reduce(depth, (depth.Width + 1) / 2, (depth.Height + 1) / 2, 2));
	while (levels.back().Width > 1 || levels.back().Height > 1)
	{
		const Level& above = levels.back();
		levels.push_back(Reduce(above, std::max(above.Width / 2, 1), std::max(above.Height / 2, 1), 2));
	}
	return levels;
}

// The finest level where the pixel rectangle covers at most 2x2 texels; prints what the test reads.
bool IsOccluded(const std::vector<Level>& levels, int minX, int minY, int maxX, int maxY, float nearest)
{
	int level = 0;
	int lowX = minX >> 1, lowY = minY >> 1, highX = maxX >> 1, highY = maxY >> 1;
	while (level + 1 < static_cast<int>(levels.size()) && (highX - lowX > 1 || highY - lowY > 1))
	{
		level++;
		int lastX = std::max(levels[0].Width >> level, 1) - 1;
		int lastY = std::max(levels[0].Height >> level, 1) - 1;
		lowX = std::min(minX >> (level + 1), lastX);
		lowY = std::min(minY >> (level + 1), lastY);
		highX = std::min(maxX >> (level + 1), lastX);
		highY = std::min(maxY >> (level + 1), lastY);
	}
	const Level& texels = levels[level];
	float farthest = std::min(std::min(texels.At(lowX, lowY), texels.At(highX, lowY)), std::min(texels.At(lowX, highY), texels.At(highX, highY)));
	std::printf("rect (%d,%d)-(%d,%d): level %d, texels (%d,%d)-(%d,%d), farthest %.1f, nearest %.1f\n", minX, minY, maxX, maxY, level, lowX, lowY, highX, highY, farthest, nearest);
	return nearest < farthest;
}

int main()
{
	// A 9x5 depth buffer: a wall of depth 0.6 on columns 0 to 5, far background 0.1, one hole in the wall.
	Level depth;
	depth.Width = 9;
	depth.Height = 5;
	for (int y = 0; y < depth.Height; y++)
		for (int x = 0; x < depth.Width; x++)
			depth.Depth.push_back(x < 6 ? 0.6f : 0.1f);
	depth.Depth[2 * 9 + 2] = 0.0f;

	std::vector<Level> pyramid = BuildPyramid(depth);
	for (size_t i = 0; i < pyramid.size(); i++)
	{
		std::printf("level %zu is %d x %d:", i, pyramid[i].Width, pyramid[i].Height);
		for (float value : pyramid[i].Depth)
			std::printf(" %.1f", value);
		std::printf("\n");
	}
	std::printf("occluded: %d\n", IsOccluded(pyramid, 0, 0, 1, 1, 0.3f));
	std::printf("occluded: %d\n", IsOccluded(pyramid, 0, 0, 3, 3, 0.3f));
	std::printf("occluded: %d\n", IsOccluded(pyramid, 5, 0, 8, 4, 0.3f));
	return 0;
}
```

```text output-of="draw-occlusion-toy.cpp"
level 0 is 5 x 3: 0.6 0.6 0.6 0.1 0.1 0.6 0.0 0.6 0.1 0.1 0.6 0.6 0.6 0.1 0.1
level 1 is 2 x 1: 0.0 0.1
level 2 is 1 x 1: 0.0
rect (0,0)-(1,1): level 0, texels (0,0)-(0,0), farthest 0.6, nearest 0.3
occluded: 1
rect (0,0)-(3,3): level 0, texels (0,0)-(1,1), farthest 0.0, nearest 0.3
occluded: 0
rect (5,0)-(8,4): level 1, texels (1,0)-(1,0), farthest 0.1, nearest 0.3
occluded: 0
```

1. **Lines 26–27:** the last row and column reach to the source's end, so an odd size loses no texel.
2. **Line 41:** level 0 is half the depth buffer, rounded up; **Line 45:** every later level halves and rounds down.
3. **Line 55:** the loop climbs while the rectangle spans more than two texels, and clamps to the level's last texel.
4. **Line 66:** the answer is the smallest depth of the four corner texels, which the caller compares with the box's nearest depth.

The toy is tiny, but it already shows the three ideas of the real code. A level halves the size and never skips an odd texel. The test reads at most four texels of one level. A hole in the wall lowers a whole texel, so a box behind the hole is kept.

:::example[The toy, by hand]
Level 0 is 5 by 3, because 9 by 5 halved and rounded up gives 5 by 3. Its texel in column 2, row 0 covers pixel columns 4 and 5 and rows 0 and 1, all 0.6, so the texel holds 0.6. Its texel in column 4 covers only pixel column 8, which is 0.1.

Level 1 is 2 by 1, because 5 halved rounded down is 2 and 3 halved rounded down is 1. Its second texel is the last column, so it covers level-0 columns 2, 3 and 4, not only 2 and 3: the smallest of 0.6, 0.1 and 0.1 is 0.1. Its first texel covers columns 0 and 1 and all three rows, so it holds 0.0, the hole.

Now test three boxes with a nearest depth of 0.3. A box covering pixels (0,0) to (1,1) shifts to texel (0,0) of level 0, which holds 0.6; 0.3 is below 0.6, so the box is hidden. A box covering (0,0) to (3,3) reads texels (0,0) to (1,1), and texel (1,1) holds 0.0, so the box stays. A box covering (5,0) to (8,4) spans three texels at level 0, so the test climbs to level 1, reads texel (1,0), finds 0.1 and keeps the box.
:::

## The real code

Strata differs from the toy in five ways. The work runs on the graphics card, and the levels are mips of one texture: the smaller copies a texture keeps of itself, each about half the size of the one before. The box is eight corners projected into pixels, the pyramid may be built with a sampler, and every proxy has history bits. The data flows in that order.

### Building a level

Each dispatch builds one level; level 0 reads the depth buffer. The texture's size is `(width + 1) / 2` by `(height + 1) / 2`, and every later level is a mip of the texture. A mip is half the level above, rounded down, and at least one texel (`GetPyramidLevelSize`). Look at how `st_Main` extends the last row and column, and at `Farthest2x2`.

```slang src="Strata/shaders/Scene/HZBBuild.comp.slang#L41-L83"
// The farthest depth of the source's 2x2 texels from `base` (those past its last row and column repeat it).
float Farthest2x2(int2 base)
{
	if (u_Pyramid.UseMinimumSampler != 0u)
	{
		// The 2x2 footprint's center; clamping repeats an edge's texel, which leaves the minimum as it is. The coordinates must
		// be normalized by the source's own size: any other moves the footprint off the texels it covers, more the farther it
		// is from the origin.
		float2 uv = (float2(base) + 1.0) / float2(u_Pyramid.SourceSize);
		return ST_HZB_SAMPLE(uv);
	}
	int2 last = int2(u_Pyramid.SourceSize) - 1;
	return min(min(ST_HZB_FETCH(min(base, last)), ST_HZB_FETCH(min(base + int2(1, 0), last))),
		min(ST_HZB_FETCH(min(base + int2(0, 1), last)), ST_HZB_FETCH(min(base + int2(1, 1), last))));
}

void st_Main()
{
	uint2 texel = st_GlobalInvocationID.xy;
	if (any((texel >= u_Pyramid.DestinationSize)))
		return;
	int reduction = u_Pyramid.Reduction == 4u ? 4 : 2;
	// The source texels the texel covers: `reduction` each way, and from the last row and column to the source's end (three
	// where the source's size is odd and this level's half of it, rounded down).
	int2 sourceLast = int2(u_Pyramid.SourceSize) - 1;
	int2 first = int2(texel) * reduction;
	int2 last = min(first + reduction - 1, sourceLast);
	if (texel.x + 1u == u_Pyramid.DestinationSize.x)
		last.x = sourceLast.x;
	if (texel.y + 1u == u_Pyramid.DestinationSize.y)
		last.y = sourceLast.y;
	// In blocks of 2x2: one or two each way.
	bool wide = last.x - first.x >= 2;
	bool tall = last.y - first.y >= 2;
	float farthest = Farthest2x2(first);
	if (wide)
		farthest = min(farthest, Farthest2x2(first + int2(2, 0)));
	if (tall)
		farthest = min(farthest, Farthest2x2(first + int2(0, 2)));
	if (wide && tall)
		farthest = min(farthest, Farthest2x2(first + int2(2, 2)));
	ST_HZB_STORE(int2(texel), farthest);
}
```

1. **Line 49:** the sample's coordinates are :term[normalized]{id=normalization} by the source's own size; any other size moves the footprint off its texels.
2. **Line 52:** the fallback does four loads, each clamped to the source's last row and column.
3. **Lines 67–71:** the last texel of a row or column reaches to the source's end.
4. **Lines 73–81:** a texel covers one or two blocks of 2 by 2 texels each way, and keeps the smallest depth of them.

To see why the last row and column cover extra texels, take the toy's 9 by 5 buffer. Level 0 is 5 by 3, and 5 halved and rounded down is 2, so level 1 has two columns. If its second column covered only level-0 columns 2 and 3, column 4 would belong to no texel, and a box over pixel column 8 would read a texel that never saw its depth. Each thread builds one texel in groups of 8 by 8 threads, so a 1920 by 1080 view builds level 0, 960 by 540 texels, with 120 by 68 groups.

A **min/max sampler** (:term[Vulkan's]{id=vulkan} `samplerFilterMinmax`, a feature of the device) is a sampler whose filter returns the smallest or largest of the texels it covers instead of their average. Where the device has it, and `MinimumSamplerPyramids` is on, one sample at the centre of a 2 by 2 block returns the farthest depth of all four. Elsewhere the shader does four loads and takes the smallest. Both give the same numbers; tests build both ways and compare.

### Choosing the level

`GetPyramidFootprint` takes the pixel rectangle and returns the finest level at which it spans at most two texels each way, with the corner texels `low` and `high`. The shift is 1 for the view, because level 0 is already half the depth buffer. At each level the loop shifts the pixels once more and clamps to the level's last texel, which is the texel that also covers what lies past the mip.

```slang src="Strata/shaders/Include/Culling.slang#L236-L257"
// The texels of a depth pyramid's level that cover a rectangle of pixels [minPixel, maxPixel] of a target of `size` pixels,
// clamped to it: the finest level at which it spans at most two texels each way (corners `low` and `high`). Level 0 is the
// target's size divided by 1 << shift, rounded up, and every other level half the one above, rounded down
// (Scene/HZBBuild.comp): level m's texel covers the pixels p with p >> (m + shift) equal to it, and its last row and column
// also those past them, so a pixel's texel is clamped to them.
int GetPyramidFootprint(float2 minPixel, float2 maxPixel, float2 size, int levels, int shift, out int2 low, out int2 high)
{
	int2 lowPixel = int2(clamp(floor(minPixel), float2(0.0), size - 1.0));
	int2 highPixel = int2(clamp(floor(maxPixel), float2(0.0), size - 1.0));
	int2 levelZero = (int2(size) + (1 << shift) - 1) >> shift;
	int level = 0;
	low = lowPixel >> shift;
	high = highPixel >> shift;
	while (level + 1 < levels && any((high - low) > 1))
	{
		level++;
		int2 last = max(levelZero >> level, int2(1)) - 1;
		low = min(lowPixel >> (level + shift), last);
		high = min(highPixel >> (level + shift), last);
	}
	return level;
}
```

1. **Lines 243–244:** the rectangle is clamped to the target, so a box that reaches past the screen still reads valid texels.
2. **Line 245:** level 0 is the target's size divided by two, rounded up.
3. **Line 249:** the loop climbs while the span is more than two texels in either direction and a coarser level exists.
4. **Lines 252–254:** a level's last texel also covers what lies past the mip, so the shifted pixels clamp to it.

### Testing a box

`IsOccluded` projects the eight corners of the box, keeps the smallest and largest pixel and the nearest depth (the largest, in reversed Z), and compares it with the smallest of four reads at the footprint. The test stops and keeps the box in two cases: a corner is behind or on the camera's plane, or on or in front of the :term[near plane]{id=near-plane}. The second case is a depth of 1 or more, because near is 1.

```slang src="Strata/shaders/Scene/Cull.comp.slang#L167-L193"
bool IsOccluded(float3 boxMin, float3 boxMax)
{
	float2 size = u_Cull.OcclusionParameters.xy;
	float2 minPixel = float2(3.0e38);
	float2 maxPixel = float2(-3.0e38);
	float nearest = 0.0;
	for (uint corner = 0u; corner < 8u; corner++)
	{
		float3 position = float3((corner & 1u) != 0u ? boxMax.x : boxMin.x, (corner & 2u) != 0u ? boxMax.y : boxMin.y, (corner & 4u) != 0u ? boxMax.z : boxMin.z);
		float4 clip = mul(u_Cull.ViewProjection, float4(position, 1.0));
		if (clip.w <= 1.0e-6)
			return false;
		float3 ndc = clip.xyz / clip.w;
		if (ndc.z >= 1.0)
			return false;
		float2 pixel = float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5) * size;
		minPixel = min(minPixel, pixel);
		maxPixel = max(maxPixel, pixel);
		nearest = max(nearest, ndc.z);
	}
	int2 a;
	int2 b;
	int level = GetPyramidFootprint(minPixel, maxPixel, size, int(u_Cull.OcclusionParameters.z), 1, a, b);
	float farthest = min(min(u_DepthPyramid.Load(int3(a, level)).r, u_DepthPyramid.Load(int3(int2(b.x, a.y), level)).r),
		min(u_DepthPyramid.Load(int3(int2(a.x, b.y), level)).r, u_DepthPyramid.Load(int3(b, level)).r));
	return nearest < farthest;
}
```

1. **Lines 177–180:** a corner behind the camera's plane or in front of the near plane makes the test answer "not hidden".
2. **Line 185:** the nearest depth of the box is the largest corner depth, because near is 1.
3. **Line 189:** the footprint is chosen with a shift of 1, because level 0 is half the depth buffer.
4. **Lines 190–192:** the farthest depth is the smallest of four reads, and the box is hidden when its nearest point is still farther.

:::example[Why the rectangle keeps the test safe]
A thin box along a diagonal has a bounding rectangle from pixel (0,0) to (9,9), though the box fills only the pixels along the line. Say a wall of depth 0.6 covers the whole screen except the corner (9,0), where a far hill of depth 0.1 shows. The texel that holds the corner stores 0.1, so the farthest depth over the rectangle is 0.1, and a box with nearest depth 0.3 stays even if its own pixels are all behind the wall. The test kept a hidden box: a wasted draw, never a wrong picture. The reverse cannot happen: the farthest depth over the rectangle is never nearer than over the box's own pixels, so when it hides the box, the box is hidden.
:::

### Two phases and the bits

Visibility is two bits of one number per proxy. **Visibility parity** names which of the two bits holds the previous frame's answer: the frame reads that bit and writes the other, and flipping the parity makes today's answer tomorrow's history. At parity 0 the shader reads bit 0 and writes bit 1; after the flip it reads bit 1 and writes bit 0. Phase 1 draws a proxy only if its previous bit is set. Phase 2 writes the new bit for every proxy and draws those visible now whose previous bit was clear.

```slang src="Strata/shaders/Scene/Cull.comp.slang#L541-L579"
// The view's second phase: every proxy's visibility this frame (the frustum, size and occlusion tests; written while
// counting), and the draws of those visible now that the first phase did not draw.
void CullSecondPhase(uint proxyIndex)
{
	GPUProxy proxy = u_Proxies[proxyIndex];
	uint previousBit = 1u << u_Cull.VisibilityParity;
	uint currentBit = previousBit ^ 3u;
	bool visible = false;
	bool occluded = false;
	uint mesh = 0u;
	GeometryEntry entry = GeometryEntry(0u, 0u, 0u, 0u);
	const uint drawable = ST_PROXY_ACTIVE | ST_PROXY_INDEXED;
	bool tested = (proxy.Flags & drawable) == drawable && proxy.MeshSlot < u_Cull.MeshSlotCount && IsDrawable(proxy, mesh, entry);
	float3 center = (proxy.WorldMin + proxy.WorldMax) * 0.5;
	float3 extents = (proxy.WorldMax - proxy.WorldMin) * 0.5;
	float fraction = GetScreenFraction(center, length(extents));
	float3 relativeMin = proxy.WorldMin - u_Cull.CameraPosition.xyz;
	float3 relativeMax = proxy.WorldMax - u_Cull.CameraPosition.xyz;
	if (tested && IsBoxInFrustum(relativeMin, relativeMax)
		&& !(u_Cull.LODParameters.w > 0.0 && fraction * u_Cull.ViewParameters.x < u_Cull.LODParameters.w))
	{
		visible = !IsOccluded(relativeMin, relativeMax);
		occluded = !visible;
		if (occluded)
			Count(ST_COUNTER_OCCLUDED);
	}
	uint state = u_Visibility[proxyIndex];
	// Left out of the frame: hidden now, and not drawn by the first phase (which drew what the previous frame saw).
	if (occluded && (state & previousBit) == 0u)
		RecordCulled(proxyIndex, ST_CULLED_BY_OCCLUSION);
	if (IsCounting())
		u_Visibility[proxyIndex] = (state & ~currentBit) | (visible ? currentBit : 0u);
	if (!visible || (state & previousBit) != 0u)
		return;
	bool skinnedArena = (mesh & ST_CULL_MESH_SKINNED_ARENA) != 0u;
	uint geometry = skinnedArena ? ((proxy.Flags & ST_PROXY_SKINNED) != 0u ? ST_CULL_GEOMETRY_SKINNED : ST_CULL_GEOMETRY_SKINNED_ARENA) : ST_CULL_GEOMETRY_STATIC;
	uint mirrored = (proxy.Flags & ST_PROXY_MIRRORED) != 0u ? 1u : 0u;
	EmitViewInstances(proxy, entry, fraction, geometry, mirrored, ST_CULL_SECOND_PHASE_BUCKET);
}
```

1. **Lines 546–547:** the previous frame's bit is the one the parity names; the current bit is the other of the two.
2. **Lines 559–566:** a proxy that passes the frustum and size tests is visible unless the pyramid hides it, and a hidden one is counted.
3. **Lines 569–570:** a hidden proxy that phase 1 did not draw is omitted from the frame, so it is recorded with its reason for the debug view **Culled**.
4. **Line 572:** the new bit is written only while counting, so the write pass does not repeat it.
5. **Line 573:** a proxy is drawn in phase 2 only when it is visible now and its previous bit was clear.

On the host, `RunOcclusionPhase` builds the pyramid level by level, then runs the three passes of phase 2: count, build the buckets, write the draws. It ends by flipping the parity.

```cpp src="Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp#L1060-L1096"
void SceneRenderer::RunOcclusionPhase(nvrhi::ICommandList* commandList)
{
	ST_PROFILE_FUNCTION();
	// The depth pyramid of the first phase's depth, level by level.
	nvrhi::ComputeState pyramidState;
	pyramidState.pipeline = m_DepthPyramidPipeline;
	for (uint32_t level = 0; level < m_DepthPyramidLevels; level++)
	{
		pyramidState.bindings = { m_DepthPyramidSets[level] };
		commandList->setComputeState(pyramidState);
		DepthPyramidParameters parameters;
		parameters.SourceSize = level == 0 ? m_ViewportSize : GetPyramidLevelSize(m_DepthPyramidSize, level - 1);
		parameters.DestinationSize = GetPyramidLevelSize(m_DepthPyramidSize, level);
		parameters.UseMinimumSampler = m_Specification.MinimumSamplerPyramids && Renderer::GetGraphicsDevice().GetInfo().SupportsSamplerMinMax ? 1u : 0u;
		commandList->setPushConstants(&parameters, sizeof(parameters));
		commandList->dispatch((parameters.DestinationSize.x + 7) / 8, (parameters.DestinationSize.y + 7) / 8, 1);
	}

	// The second phase: every proxy's visibility against the pyramid, and the draws of those the first phase did not draw.
	const RenderData::CullConstants& constants = m_CullConstants;
	nvrhi::ComputeState state;
	state.bindings = { m_CullBindingSet };
	state.pipeline = m_CullViewPipeline;
	const auto pass = [&](uint32_t mode, nvrhi::IComputePipeline* pipeline, uint64_t items)
	{
		state.pipeline = pipeline;
		commandList->setComputeState(state);
		commandList->setPushConstants(&mode, sizeof(mode));
		Dispatch(commandList, items);
		CullBarrier(commandList);
	};
	pass(c_CullModeSecondPhase | c_CullModeCount, m_CullViewPipeline, constants.ProxyCount);
	pass(c_CullModeSecondPhase, m_CullBuildPipeline, static_cast<uint64_t>(constants.BucketCount) * constants.LODCapacity);
	pass(c_CullModeSecondPhase | c_CullModeWrite, m_CullViewPipeline, constants.ProxyCount);
	// This frame's visibility (the view's and the cascades') is the next one's history.
	m_VisibilityParity ^= 1u;
}
```

1. **Line 1071:** level 0 reads the depth buffer at the viewport's size; the other levels read the level above at its mip size.
2. **Line 1073:** the minimum sampler is used only when the specification asks for it and the device has it.
3. **Lines 1091–1093:** phase 2 counts, builds the buckets, then writes the draws, with a barrier after each pass.
4. **Line 1095:** the flip makes this frame's bits the next frame's history.

The prepass in `SceneRenderer.cpp` draws the first-phase buckets, calls `RunOcclusionPhase`, then draws the buckets of phase 2. The cascades' bits sit above the view's two bits, and the cascades are treated alike: [sun shadows](../light/sun-shadows-1.md) covers them and the shadow cascade cache.

### When history is dropped

Some frames have no usable history. A camera cut is a move of more than 10 world units or a turn of more than 45 degrees between two frames, the same test texture streaming uses. A camera that moves 12 units between two frames is cut; one that moves 8 units is not, unless it also turns more than 45 degrees. A renderer's first frame and a switch to another :term[render scene]{id=render-scene} also have none. Then `m_ResetVisibility` is set, and `RunGPUCulling` clears every bit: phase 1 draws nothing, the pyramid is empty, and phase 2 draws everything in the frustum, so the frame costs more and is still right.

```mermaid caption="Two frames of the test scene: the first frame after a cut draws both objects, a later frame draws only the wall." alt="Two columns. The left column is the frame of a camera cut: no bits, phase 1 draws nothing, phase 2 draws the wall and the box. The right column is a later frame: both bits set, phase 1 draws the wall and the box, the pyramid holds the wall, phase 2 hides the box and clears its bit."
flowchart LR
	subgraph Cut["Frame after a cut"]
		C1["Bits cleared"] --> C2["Phase 1: nothing"] --> C3["Pyramid: empty"] --> C4["Phase 2: wall and box drawn"]
	end
	subgraph Later["A later frame"]
		L1["Bits set"] --> L2["Phase 1: wall and box"] --> L3["Pyramid: wall's depth"] --> L4["Phase 2: box hidden, bit cleared"]
	end
	Cut --> Later
```

The test scene of `GPU.SceneRenderer.Occlusion` has a wall and a box behind it. The table follows the box through its frames.

| Frame | Phase 1 draws | The pyramid holds | Phase 2 finds |
| --- | --- | --- | --- |
| 1, no history | Nothing | Nothing | Wall and box visible and drawn: 2 instances, `OccludedProxies` 0 |
| 2 | Wall and box, whose bits are set | The wall's depth | The box hidden, so its bit is cleared |
| 3 | The wall alone | The wall's depth | The box hidden again: 1 instance, `OccludedProxies` 1, `VisibleProxies` 2 |
| 4, wall disabled | No wall | A pyramid without the wall | The box visible with a clear bit, so it is drawn in this frame |

Frame 4 is the case that matters: the box appears in the frame the wall goes, not one later.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Hardware occlusion queries | Many engines on the graphics card (see Further reading) | No pyramid and no extra depth pass | Answers arrive frames later, so objects pop in or the frame waits |
| Software drawing of a few big walls | Frostbite, in a published talk (see Further reading) | Works without the graphics card and without history | Processor time, and a person must mark the walls |
| Last frame's depth moved to the new camera | Engines before the two-phase pyramid became common | One pass fewer | Holes where old depth is missing, and moving objects need extra rules |
| Portals | Indoor engines with authored cells | Exact room-to-room visibility | Authoring work, and a world that must be cut into rooms |

## How it is tested

The suite `GPU.SceneRenderer.Occlusion` renders small scenes on the shared test device and reads the counters back. The cases are:

- A box behind a wall is omitted, and drawn in the frame the wall goes or the camera steps aside.
- A box whose rectangle reaches the last row and column is omitted, at odd and even sizes.
- Orthographic views are treated alike.
- A caster hidden from the light behind another is omitted of its cascades, and the cascades' culling pauses while it hides nothing.
- A box in plain view below a window stays drawn from cameras about the window's axis.
- Each pyramid texel holds the farthest depth of the pixels it covers, built with and without the minimum sampler, at sizes such as 960 by 540, 961 by 541 and 37 by 5.

Several cases also render the same scene with `OcclusionCulling` set to false and check that the hidden object is then drawn, which shows the culling and not the scene made the difference. Run them with `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.Occlusion`, or through `ctest` without the `-LE gpu` filter. A test that counts draws follows the third rule above.

You can also check the culling by eye. The Scene view's debug view list has the entry **Culled**, which draws a box around each mesh in view that the frame omitted, over the whole image. A yellow box marks a mesh smaller on screen than the smallest drawn size, each box grown to 6 pixels across so it shows. A red box marks a mesh hidden behind what is drawn, and only the GPU-driven path draws red boxes, from the entries `RecordCulled` wrote.

The command `viewport.setSettings` with `{"debugView":"culled"}` selects the view, and its legend counts both kinds. While the camera moves, the count of hidden meshes can run a little ahead of the red boxes. A mesh the previous frame saw is drawn once more by phase 1, so its box appears a frame later.

## Changing it safely

A change to the pyramid or the footprint has to stay conservative at every size, so extend the odd-size and last-row cases of the suite first. The CPU path and `Cull.comp.slang` decide together what is drawn and requested: a change to one is a change to both, and the GPU-driven and feedback tests must still pass. A pass that reads the view's depth is recorded after phase 2's prepass has drawn. A new input to the way casters are drawn must be part of a version that the shadow caches compare, as [sun shadows](../light/sun-shadows-1.md) explains.

## What went wrong before

During the work on release 0.8.0, occlusion culling hid a box in plain view below a window. The build stepped its level sizes rounded up, while the texture's mips round down, and passed those sizes to the shader. With the minimum sampler, the sample's coordinates were :term[normalized]{id=normalization} by the wrong size, so the 2 by 2 footprint slid off its texels, more the farther from the origin. Texels read beside the box's own pixels found it hidden. The fix passes each level's own mip size (`GetPyramidLevelSize`), and two tests guard it: the window case and the test of each texel's farthest depth, built with and without the sampler.

## Summary

- A depth pyramid halves its size per level, rounds odd sizes so the last row and column cover what lies past them, and keeps the farthest depth.
- The footprint is the finest level where the box's rectangle spans two texels or fewer; the test compares the box's nearest depth with the farthest of at most four reads.
- Phase 2 draws the newly visible in the same frame, so nothing appears late; the parity bits carry the history.
- Occlusion stays conservative: sizes are mip sizes, footprints clamp, and nothing reads depth before phase 2.

## Check yourself

1. A depth buffer is 7 by 5 texels. How large are level 0 and level 1 of its pyramid?

   :::answer{tests="build-level"}
   Level 0 is 4 by 3 (7 and 5 halved, rounded up). Level 1 is 2 by 1 (4 and 3 halved, rounded down).
   :::

2. The pyramid keeps the smallest depth of each 2 by 2 block. Why is the smallest the farthest?
   a) Reversed Z makes far 0, so the smallest number is the farthest surface.
   b) Smaller depths are always nearer.
   c) The sampler averages.

   :::answer{tests="build-level"}
   Option a. In reversed Z near is 1 and far is 0, so the farthest surface has the smallest value. Option b is the usual order of normal Z. Option c is wrong because the minimum sampler returns the smallest value, never the average.
   :::

3. A frame has no history after a camera cut. What does phase 1 draw, and does the frame still show every visible object?

   :::answer{tests="explain-no-lag"}
   Phase 1 draws nothing, because every bit is clear. The pyramid is empty, so phase 2 keeps everything in the frustum and draws it in the same frame. Nothing is missing; the frame only costs more.
   :::

4. A box's rectangle spans three texels at level 0. The box's nearest depth is 0.3 and the four texels of the next level hold 0.6, 0.4, 0.2 and 0.5. Is it hidden?

   :::answer{tests="find-footprint"}
   No. The farthest depth is the smallest of the four, 0.2, and 0.3 is not below 0.2, so the box may poke through and is kept.
   :::

5. A teammate adds a pass that reads depth before phase 2 runs. What goes wrong, and which rule is it?

   :::answer{tests="name-rules"}
   The pass sees a depth buffer without the objects phase 2 adds, so its result has holes. The rule is to record such a pass after phase 2's prepass has drawn.
   :::

## Exercises

1. **Basic.** Fill a 7 by 5 depth buffer with `1 - (x + y) / 10` for column `x` and row `y`. Build level 0, level 1 and level 2 by hand, and find the level and the texels for the pixel rectangle (4,0) to (6,2).

   :::answer[Worked solution]{tests="build-level,find-footprint"}
   Level 0 is 4 by 3; its texel in column `i`, row `j` holds the value at the largest `x` and `y` it covers, because larger sums are farther. The columns reach x = 1, 3, 5 and 6, and the rows reach y = 1, 3 and 4. So row 0 is 0.8, 0.6, 0.4, 0.3; row 1 is 0.6, 0.4, 0.2, 0.1; row 2 is 0.5, 0.3, 0.1, 0.0.

   Level 1 is 2 by 1. Its first texel covers level-0 columns 0 and 1 and all three rows, so it holds 0.3. Its second texel covers columns 2 and 3, and the last row and column, so it holds 0.0. Level 2 is 1 by 1 and holds 0.0.

   The rectangle (4,0) to (6,2) shifts by one to texels (2,0) to (3,1): a span of two texels, so level 0 is enough. Those four texels hold 0.4, 0.3, 0.2 and 0.1, so the farthest depth is 0.1.
   :::

2. **Medium.** Write a program that prints the footprint level of the rectangle from pixel column 0 to column `w - 1`, for `w` from 1 to 9 on a 9 by 5 buffer. Predict the output before you run it.

   :::answer[Worked solution]{tests="find-footprint" solution="sketches/draw-occlusion-levels.cpp"}
   The program repeats the footprint loop for the one direction that matters: the rectangle starts at column 0, so only its right end moves.

   ```cpp sketch="draw-occlusion-levels.cpp"
   // The finest pyramid level a pixel rectangle reads, for rectangles that start at column 0 of a 9x5 depth buffer.
   #include <algorithm>
   #include <cstdio>

   int main()
   {
   	const int levelZeroWidth = 5; // 9 halved, rounded up
   	const int levelCount = 3;     // 5x3, 2x1, 1x1
   	for (int width = 1; width <= 9; width++)
   	{
   		int highPixel = width - 1;
   		int level = 0;
   		int high = highPixel >> 1;
   		while (level + 1 < levelCount && high > 1)
   		{
   			level++;
   			int last = std::max(levelZeroWidth >> level, 1) - 1;
   			high = std::min(highPixel >> (level + 1), last);
   		}
   		std::printf("width %d: level %d, last texel %d\n", width, level, high);
   	}
   	return 0;
   }
   ```

   ```text output-of="draw-occlusion-levels.cpp"
   width 1: level 0, last texel 0
   width 2: level 0, last texel 0
   width 3: level 0, last texel 1
   width 4: level 0, last texel 1
   width 5: level 1, last texel 1
   width 6: level 1, last texel 1
   width 7: level 1, last texel 1
   width 8: level 1, last texel 1
   width 9: level 1, last texel 1
   ```

   1. **Line 7:** level 0 is 5 texels wide, because 9 halved is rounded up.
   2. **Line 14:** the shader's loop: climb while the rectangle spans more than two texels; the low end is always texel 0.
   3. **Lines 17–18:** the clamp to the level's last texel.

   Widths 1 to 4 fit in two level-0 texels, so they use level 0. From width 5 the rectangle spans three texels, so the loop climbs to level 1, where the clamp keeps the last texel at column 1; widths 5 to 9 all use level 1.
   :::

3. **Hard.** Trace it yourself. In `CheckOcclusion`, the camera jumps more than 10 units to a place where the wall still hides the box. What does the frame after the jump draw, and where does the engine clear the history?

   :::answer[Worked solution]{tests="explain-no-lag,name-rules"}
   Copy the wall scene of `CheckOcclusion` in `StrataTests/src/Renderer/GPUSceneOcclusionTests.cpp` and move the camera more than 10 units along its line of sight. The frame after the cut has no history, so `OccludedProxies` is 0 and the box is drawn; the next frames omit it again. Search for `m_ResetVisibility`: `SceneRenderer::RenderFrame` in `Strata/src/Strata/Renderer/SceneRenderer.cpp` sets it when `IsCameraCut` is true, and `SceneRenderer::RunGPUCulling` in `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp` clears the visibility buffer with `clearBufferUInt`.
   :::

## Where it lives in Strata

- Pyramid build: `Strata/shaders/Scene/HZBBuild.comp.slang`; level sizes: `GetPyramidLevelSize` and `CreateDepthPyramid` in `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp`.
- Footprint and test: `GetPyramidFootprint` in `Strata/shaders/Include/Culling.slang`; `IsOccluded` and `CullSecondPhase` in `Strata/shaders/Scene/Cull.comp.slang`.
- Sequence: `RunOcclusionPhase` in `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp`, called from the prepass in `Strata/src/Strata/Renderer/SceneRenderer.cpp`.
- Bits: `c_VisibilityCascadeShift` in `Strata/src/Strata/Renderer/GPUSceneData.h`.
- Settings: `SceneRendererSpecification::OcclusionCulling` and `MinimumSamplerPyramids`.
- Tests: `GPU.SceneRenderer.Occlusion` in `StrataTests/src/Renderer/GPUSceneOcclusionTests.cpp`.

## Further reading

- Haar and Aaltonen, "GPU-Driven Rendering Pipelines" (SIGGRAPH 2015): the two-phase depth pyramid in a shipped game (intermediate).
- Karis, Stubbe and Wihlidal, "Nanite virtualized geometry" (SIGGRAPH 2021): the same culling at the scale of clusters (advanced).
- Collin, "Culling the Battlefield" (GDC 2011): software-rasterized occluders (intermediate).
- Sekulic, "Efficient Occlusion Culling", GPU Gems chapter 29: hardware occlusion queries (beginner).
