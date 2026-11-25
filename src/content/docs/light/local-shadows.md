---
id: light/local-shadows
title: "Shadows of point and spot lights"
description: "How Strata gives hundreds of point and spot lights shadows from one atlas: tiles, a view cache, a budget of views per frame and fades."
kind: internals
size: L
tracks: [E]
needs: [light/sun-shadows-1, light/many-lights, light/area-lights]
time: 85
learn:
  - id: atlas-idea
    text: explain why Strata cuts one depth atlas into tiles of different sizes instead of giving every light a cube map
  - id: allocator-trace
    text: trace a series of tile requests and frees through the quadtree allocator
  - id: size-and-band
    text: compute a light's tile size and the guard band of its views from the numbers the engine uses
  - id: cache-budget
    text: predict how many frames Strata needs to draw the views of moved lights again, and how long a fade lasts
  - id: sample-path
    text: trace one pixel's lookup from the choice of a cube face to the sixteen taps
since: 0.6.0
status: final
---

A point light shines in every direction and a spot light in a cone. Both can have shadows, and a street at night can hold hundreds of lamps. This part of the :term[renderer]{id=renderer} gives the lights that matter most a shadow. It draws a shadow again only when what it shows has changed, and it never lets a shadow pop in or out as the camera moves.

This part does not shade pixels: the forward pass does that ([Many lights](../light/many-lights.md)) and reads what this part drew. It does not shadow the sun ([Sun shadows I](../light/sun-shadows-1.md)), and it gives no shadow a width that follows the light's size.

Rectangle lights ([Area lights](../light/area-lights.md)) use the same atlas, tiles and cache. This page says what they change in one section near the end.

## The problem and how engines solve it

A shadow map ([Shadow basics](../light/shadow-basics.md)) is a picture of the scene seen from the light, kept as depths. The sun looks along one direction, so one picture serves. A spot light is nearly as simple, because its cone is its picture. A point light shines everywhere, and a flat picture covers only a cone of the directions around it.

The usual answer is a **cube shadow**: six square pictures, one for each face of a cube around the light, that together cover every direction. Each face has a 90 degree view. A pixel to shade reads the face that its direction from the light points at most.

Count the memory. A face of 1024 by 1024 texels (the pixels of a texture) with 4 :term[bytes]{id=byte} of depth takes 4 MiB, so a cube takes 6 × 4 MiB = 24 MiB. A street with 256 lamps then needs 6,144 MiB, which is 6 GiB, and 256 textures that every :term[shader]{id=shader} must reach. A lamp 80 m away covers a few pixels, yet it takes as much room as the lamp at your feet.

Engines answer in four ways, and most mix them.

| Idea | Pictures per point light | What it costs |
| --- | --- | --- |
| One cube map per light | Six, in one cube texture | Full size for far and near lights; one texture per light |
| Dual-paraboloid maps | Two, each a warped half of the sphere | The warp bends straight edges, so large triangles must be cut small; a seam where the halves meet |
| One shared atlas | Six tiles of any size | An :term[allocator]{id=allocator}, and lookups that must stay inside their tile |
| Cached shadows | Any | A rule that says when a kept picture is out of date |

Strata takes the third idea and the fourth together.

A **shadow atlas** is one large depth texture that holds many shadow pictures side by side.

A **tile** is one square piece of the atlas that holds the picture of one view of one light.

Tiles come in sizes from 128 texels up. A lamp that fills the screen gets a large tile and a distant lamp a small one, and the atlas is one texture to bind.

The price is three jobs that the rest of this page explains. Something must decide which lights get room. A lookup near the edge of a tile must never read the tile beside it. A kept picture must be drawn again when, and only when, it goes out of date.

## The map

One frame passes through the steps below. The choice of lights, tiles, views and casters happens on the :term[main thread]{id=main-thread}, with one job per light on worker threads for the casters. The drawing is recorded by the main thread and runs on the :term[graphics processing unit]{id=gpu} (GPU).

```mermaid caption="The steps of one frame for point and spot lights, from the lights in view to the lookup of the forward pass. The last step keeps the drawn views for the next frame." alt="Nine boxes from top to bottom: rank the lights, place tiles, track changes, schedule views, find casters, make the atlas, draw the views, sample in the forward pass, keep the drawn views."
flowchart TD
	A["RankLocalShadowLights: which lights get a shadow"] --> B["PlaceLocalShadowTiles: tile sizes and places"]
	B --> C["TrackLocalShadowChanges: which views are out of date"]
	C --> D["ScheduleLocalShadowViews: the budget of views"]
	D --> E["Casters: one job per light, or the culling shader"]
	E --> F["EnsureLocalShadowAtlas and BuildLocalShadowData"]
	F --> G["DrawLocalShadows: depth into the tiles"]
	G --> H["Forward pass: SampleLocalShadow"]
	H --> I["CommitLocalShadows: drawn views become the cache"]
```

Each part lives in one place.

| Part | Where | Runs on |
| --- | --- | --- |
| Ranking, tile sizes, change tracking, scheduling, caster search | `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp` | Main thread, caster jobs on workers |
| The tile allocator | `Strata/src/Strata/Renderer/ShadowAtlasAllocator.h` and `.cpp` | Main thread |
| Casters on the GPU-driven path | `Strata/shaders/Scene/Cull.comp.slang` | GPU |
| The lookup | `Strata/shaders/Include/LocalShadows.slang`, called by `Strata/shaders/Scene/Forward.frag.slang` | GPU |

## The contract

What the rest of the renderer may assume, and what code in this part must keep true:

- A light has a shadow only when it has `CastShadows` on, is in view, ranks among the first lights the quality allows and the atlas has room. The reason is that memory and time are finite, so the lights that matter most come first.
- A light shows its shadow only when every view of it holds a picture, and then the shadow fades in. A light with some faces drawn and some not would show a shadow with holes.
- No shadow blinks: ranks keep a margin, fades go by time, a light whose tile changes size keeps sampling its old tile until the new one is drawn, and the filter noise is fixed.
- A view's key, the list of facts its picture depends on, leaves the camera out. A view drawn once stays valid while the camera walks, and the matrices are rebuilt relative to the camera in double precision from the key the tile was drawn with.
- Code never assumes an atlas exists. When none can be made, point and spot lights cast no shadows and the renderer reports it once.

:::rule[Never blink]
The rules of `AGENTS.md` for this part start with one: a point or spot shadow never blinks. Importance gets a margin, fades follow the clock, and a light that changes its tile size samples the old tile until the new one is drawn. The filter uses fixed noise. A cache that changes its mind every frame costs more than it saves and looks worse. [Temporal anti-aliasing](../image/taa.md) cannot be the cure, because a shadow must look right without it.
:::

:::rule[Change both paths]
`AGENTS.md` says what is drawn into a shadow view is decided twice, by the :term[central processing unit]{id=processor} (CPU) path and by `Cull.comp`, and a change must keep both passing the tests `GPU.SceneRenderer.GPUDriven` and `.Feedback`. A new input of how casters are drawn must also change a version that the caches compare. Otherwise a cached view keeps showing what the old input drew.
:::

## A toy version

Before the real code, a small allocator and fitter that do the same job on paper. Take an atlas of 1024 texels each way and a smallest tile of 128. The tile sizes are 1024, 512, 256 and 128.

:::example[Four requests by hand]
Request a 512 tile. No block of 512 exists yet, so the whole atlas splits into four quarters in :term[Morton order]{id=morton-order}, which lists them as top-left, top-right, bottom-left, bottom-right. The first quarter is taken: tile (0, 0).

Request a 256 tile. The first free 512 quarter, the top-right one at (512, 0), splits into four 256 blocks and the first is taken: (512, 0). A second 256 request takes the next block in order: (768, 0).

Request a 128 tile. No 128 block exists, so the first free 256 block, (512, 256), splits and its first quarter is taken: (512, 256).

Now free the second 256 tile, the first 256 tile and the 128 tile. The four 128 blocks are free, so they merge into the 256 block at (512, 256). Its three 256 neighbours are free as well, so all four merge into the 512 quarter at (512, 0), and a request for 512 lands there.
:::

The sketch below does the same with plain vectors. Look at `Allocate`, which takes the first free block of the size, or splits a larger one, and at `Free`, which merges four free quarters. The fitter at the end halves sizes until their areas fit a budget.

```cpp sketch="light-local-shadows-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <vector>

enum class State : uint8_t
{
	Absent,
	Free,
	Split,
	Used
};

struct Tile
{
	uint32_t X = 0;
	uint32_t Y = 0;
	uint32_t Size = 0;
};

// Level 0 is the whole atlas; level L has 4^L nodes, in Morton order, so node i has the children 4i to 4i + 3.
class ToyAtlas
{
public:
	ToyAtlas(uint32_t atlasSize, uint32_t minTile)
		: m_AtlasSize(atlasSize)
	{
		size_t count = 1;
		for (uint32_t size = atlasSize; size >= minTile; size /= 2, count *= 4)
			m_Levels.emplace_back(count, State::Absent);
		m_Levels[0][0] = State::Free;
	}

	Tile Allocate(uint32_t size)
	{
		const uint32_t level = GetLevel(size);
		// The first free block of the size, else of the next larger size, and so on.
		for (uint32_t search = level + 1; search-- > 0;)
		{
			std::vector<State>& nodes = m_Levels[search];
			size_t node = 0;
			while (node < nodes.size() && nodes[node] != State::Free)
				node++;
			if (node == nodes.size())
				continue;
			for (uint32_t split = search; split < level; split++, node *= 4)
			{
				m_Levels[split][node] = State::Split;
				for (size_t child = 0; child < 4; child++)
					m_Levels[split + 1][node * 4 + child] = State::Free;
			}
			m_Levels[level][node] = State::Used;
			return GetTile(level, node);
		}
		return {};
	}

	void Free(const Tile& tile)
	{
		uint32_t level = GetLevel(tile.Size);
		size_t index = 0;
		for (uint32_t bit = 0; bit < 16; bit++)
			index |= (((tile.X / tile.Size) >> bit) & 1u) << (2 * bit) | (((tile.Y / tile.Size) >> bit) & 1u) << (2 * bit + 1);
		m_Levels[level][index] = State::Free;
		// Four free quarters make a free block again.
		for (; level > 0; level--, index /= 4)
		{
			const size_t first = index / 4 * 4;
			std::vector<State>& nodes = m_Levels[level];
			if (nodes[first] != State::Free || nodes[first + 1] != State::Free || nodes[first + 2] != State::Free || nodes[first + 3] != State::Free)
				break;
			for (size_t child = 0; child < 4; child++)
				nodes[first + child] = State::Absent;
			m_Levels[level - 1][first / 4] = State::Free;
		}
	}

private:
	uint32_t GetLevel(uint32_t size) const
	{
		uint32_t level = 0;
		for (uint32_t levelSize = m_AtlasSize; levelSize > size; levelSize /= 2)
			level++;
		return level;
	}

	Tile GetTile(uint32_t level, size_t index) const
	{
		uint32_t x = 0;
		uint32_t y = 0;
		for (uint32_t bit = 0; bit < 16; bit++)
		{
			x |= static_cast<uint32_t>((index >> (2 * bit)) & 1u) << bit;
			y |= static_cast<uint32_t>((index >> (2 * bit + 1)) & 1u) << bit;
		}
		const uint32_t size = m_AtlasSize >> level;
		return { x * size, y * size, size };
	}

	uint32_t m_AtlasSize;
	std::vector<std::vector<State>> m_Levels;
};

// Halves one size at a time, from the least relevant entry toward the most relevant, until the areas fit the budget.
void FitTileSizes(std::vector<uint32_t>& sizes, const std::vector<uint32_t>& tileCounts, uint32_t minTile, uint64_t budget)
{
	const auto getArea = [&]()
	{
		uint64_t total = 0;
		for (size_t entry = 0; entry < sizes.size(); entry++)
			total += static_cast<uint64_t>(tileCounts[entry]) * sizes[entry] * sizes[entry];
		return total;
	};
	size_t cursor = sizes.size();
	for (bool stepped = true; stepped && getArea() > budget;)
	{
		stepped = false;
		for (size_t tried = 0; tried < sizes.size() && !stepped; tried++)
		{
			cursor = cursor == 0 ? sizes.size() - 1 : cursor - 1;
			if (sizes[cursor] > minTile)
			{
				sizes[cursor] /= 2;
				stepped = true;
			}
		}
	}
}

int main()
{
	ToyAtlas atlas(1024, 128);
	const Tile a = atlas.Allocate(512);
	const Tile b = atlas.Allocate(256);
	const Tile c = atlas.Allocate(256);
	const Tile d = atlas.Allocate(128);
	for (const Tile& tile : { a, b, c, d })
		std::printf("tile %u at (%u, %u)\n", tile.Size, tile.X, tile.Y);
	atlas.Free(c);
	atlas.Free(b);
	atlas.Free(d);
	const Tile merged = atlas.Allocate(512);
	std::printf("after the frees, a 512 tile lands at (%u, %u)\n", merged.X, merged.Y);

	// A 512 atlas fits 7/8 of its area: 229376 texels.
	std::vector<uint32_t> spots = { 256, 256, 256, 256 };
	FitTileSizes(spots, { 1, 1, 1, 1 }, 128, 229376);
	std::printf("four spot lights: %u %u %u %u\n", spots[0], spots[1], spots[2], spots[3]);
	std::vector<uint32_t> mixed = { 256, 256, 256 };
	FitTileSizes(mixed, { 6, 1, 1 }, 128, 229376);
	std::printf("a point light and two spot lights: %u %u %u\n", mixed[0], mixed[1], mixed[2]);
	return 0;
}
```

```text output-of="light-local-shadows-toy.cpp"
tile 512 at (0, 0)
tile 256 at (512, 0)
tile 256 at (768, 0)
tile 128 at (512, 256)
after the frees, a 512 tile lands at (512, 0)
four spot lights: 256 256 256 128
a point light and two spot lights: 128 128 128
```

1. **Line 37:** the search starts at the level of the size and moves to larger blocks, so a split happens only when no block of the size is free.
2. **Lines 47–51:** a split marks the block as split and its four children as free; the last block is used.
3. **Lines 65–73:** four free quarters become one free block again.
4. **Lines 104–127:** the cursor starts past the least relevant entry and moves toward the most relevant, halving one size per step.

The output matches the hand trace. In the fitter's two examples, the budget is seven eighths of a 512 atlas, which is 229,376 texels. Four spot lights that want 256 take 262,144 texels, so only the least relevant one halves. A point light with six tiles that wants 256, beside two spot lights, takes 524,288 texels: all three halve once, since the six tiles of the point light weigh most.

The real allocator differs in three ways. It keeps one bit per free node, so a search reads a few words instead of walking nodes. Its `FitTileSizes` also reports how many entries fit when even the smallest sizes do not. And it never moves a tile once handed out, which is what lets the atlas keep shadows from frame to frame.

A **quadtree allocator** is a tile allocator that splits a square into four quarters again and again, and merges four free quarters back into the square that held them.

## The real code

### The atlas and its failure path

The atlas is one 32-bit depth texture, made with the first shadowed light and kept until the renderer releases its targets. Its side is the quality row `LocalShadowAtlasSize`, which the four presets set to 2048, 4096, 4096 and 8192 texels. That is 16 MiB, 64 MiB, 64 MiB and 256 MiB. Tile sizes run from 128 texels to the row `LocalShadowMaxTile`, at most the atlas side.

A device may refuse 256 MiB. The code below tries again at half the side, down to 2048, rather than lose every shadow.

```cpp src="Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp#L1426-L1457"
nvrhi::TextureHandle atlas = createAtlas();
// Large atlases (Ultra's 8192: 256 MiB) may not fit the device's memory: half the size each way, down to 2048, rather
// than no shadows.
while (!atlas && desc.width > c_MinFallbackLocalShadowAtlasSize)
{
	desc.width /= 2;
	desc.height /= 2;
	atlas = createAtlas();
}
nvrhi::FramebufferHandle framebuffer = atlas ? m_Device->createFramebuffer(nvrhi::FramebufferDesc().setDepthAttachment(atlas)) : nullptr;
if (!atlas || !framebuffer)
{
	m_Errors.Report(fmt::format("failed to create the {0}x{0} shadow atlas of point, spot and rect lights; they cast no shadows", m_LocalShadowAllocator.GetAtlasSize()));
	return false;
}
m_LocalShadowAtlas = std::move(atlas);
m_LocalShadowFramebuffer = std::move(framebuffer);
m_LocalShadowAtlasCleared = false;
if (desc.width != m_LocalShadowAllocator.GetAtlasSize())
{
	// The frame's tiles were placed for the larger atlas (FindLocalShadowCasters ran before): this frame draws no local
	// shadows, as a failure does, and the next places its tiles in the atlas made. Released targets try the
	// quality's size again.
	if (!m_LocalShadowAtlasFallbackReported)
	{
		m_LocalShadowAtlasFallbackReported = true;
		m_Errors.Report(fmt::format("the {}-texel shadow atlas of point, spot and rect lights could not be allocated; using {}",
			m_LocalShadowAllocator.GetAtlasSize(), desc.width));
	}
	m_LocalShadowAllocator.Reset(desc.width, c_MinLocalShadowTile);
	ResetLocalShadows();
	return false;
```

1. **Line 1429:** the loop halves the side while the device refuses it and the side is above 2048.
2. **Line 1436:** when no atlas can be made, the error is reported and the lights cast no shadows.
3. **Lines 1444–1447:** a smaller atlas than asked is a success that still draws nothing this frame, because tiles were placed for the larger one.
4. **Lines 1455–1457:** the allocator starts again at the new side, every view is forgotten and the next frame places tiles in the atlas that exists.

The fallback is reported once, so a device that cannot give 256 MiB does not fill the log.

### Which lights get tiles

`RankLocalShadowLights` keeps the shadowed lights inside the :term[frustum]{id=view-frustum} and gives each an importance. The first factor is how big its range looks. With `d` the distance to the light divided by its range, a camera outside the range gets `1 / (d - 1)`, but never more than 10 as the camera nears the edge.

Inside the range the factor grows to 20 at the centre. The second factor is the square root of the light's :term[luminance]{id=luminance}, colour times intensity, because a dim light's shadow shows less.

:::example[Two lamps]
Lamp A has white light of 10 :term[cd]{id=candela} and the camera stands 3 ranges away: `1 / (3 - 1)` = 0.5, times the square root of 10, 3.16, gives 1.58. Lamp B has 45 cd and stands 6 ranges away: 0.2 times 6.71 gives 1.34. A ranks above B, although B is 4.5 times brighter.

Suppose B already holds a shadow. A holder ranks as if 1.25 times as important (`c_LocalShadowKeepRatio`): 1.34 × 1.25 = 1.68, which beats A. A light near the cut does not trade places with its neighbour every frame.
:::

The count is limited twice: by `MaxShadowedLocalLights`, which the four presets set to 4, 16, 64 and 256 lights, and by the atlas. The atlas holds 128-texel tiles within seven eighths of its area, which leaves an eighth free for tiles that change size.

A 4096 atlas holds 32 × 32 = 1,024 tiles of 128 texels, and seven eighths of that is 896. That is 149 point lights with six tiles each, or 896 spot lights. A light that drops out of the ranks while in view keeps its tiles until its shadow has faded. A light that leaves the view gives its tiles back in the same frame, since it lights nothing in view.

### Tile sizes

`PlaceLocalShadowTiles` asks how large the light looks, then fits all sizes into the atlas.

```cpp src="Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp#L554-L568"
for (size_t index = 0; index < ranked; index++)
{
	LocalShadowLight& light = m_LocalShadowLights[index];
	const glm::vec4 bounds = records[light.Record].Bounds;
	const float pixels = GetScreenFraction(camera, glm::vec3(bounds), bounds.w) * viewportHeight * 0.5f;
	uint32_t wanted = std::clamp(CeilPowerOfTwo(pixels), minTile, maxTile);
	if (light.WantedSize != 0 && pixels > static_cast<float>(light.WantedSize) * c_TileShrinkRatio
		&& pixels <= static_cast<float>(light.WantedSize) * c_TileGrowRatio)
		wanted = std::clamp(light.WantedSize, minTile, maxTile);
	light.WantedSize = wanted;
	sizes[index] = wanted;
	tileCounts[index] = light.ViewCount;
}
const uint64_t budget = static_cast<uint64_t>(atlasSize) * atlasSize / 8 * c_LocalShadowAtlasEighths;
const size_t fit = ShadowAtlasAllocator::FitTileSizes(sizes, tileCounts, atlasSize, minTile, budget);
```

1. **Line 558:** the radius of the light's range on screen, in pixels.
2. **Lines 559–562:** the wanted size is the next power of two, within the limits, unless the pixels stay inside a band around the size the light already has.
3. **Lines 567–568:** the budget is seven eighths of the atlas, and `FitTileSizes` halves sizes in rounds from the least relevant light.

:::example[A lamp that walks away]
The view is 1080 pixels high with a :term[field of view]{id=field-of-view} of 60 degrees. A lamp with a range of 10 m stands 30 m away. Its range spans 10 / (30 × tan 30°) = 0.577 of the half height, so the radius is 0.577 × 540 = 312 pixels, and the next power of two is 512. At 60 m the radius is 156 pixels, which asks for 256.

At 45 m the radius is 208 pixels, which also rounds to 256. A lamp that had 512 keeps it, because the band is 0.4 × 512 = 205 up to 1.25 × 512 = 640 pixels, and 208 is inside. Without the band, a lamp near 256 pixels would flip between two sizes every time the camera moved a step.
:::

While a light changes size, it samples the old tiles of its views until each view is drawn into its new tile. The eighth that `FitTileSizes` left free is the room for both. No more than two lights change size at once while lighting updates are spread, which is the default. A light for which no room is left keeps its size, or waits if it is new, so the atlas is never laid out again.

### Views and the guard band

A spot light is one perspective view along its axis, with the cone's half angle, but at most 80 degrees: one flat picture cannot show a hemisphere. A point light has six views along +X, −X, +Y, −Y, +Z and −Z. The shader picks the face of the largest coordinate of the direction from the light to the pixel.

A pixel near a face's edge is filtered, and a filter reads texels around the pixel. At a face's edge those texels belong to the neighbouring tile. A **guard band** is a margin of extra texels around a view that makes every tap of a lookup land inside the face it reads. The code widens the view's field of view to fill the margin.

```cpp src="Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp#L642-L660"
const float tileSize = static_cast<float>(light.TileSize);
const float filterReach = area ? tileSize * RenderData::c_AreaShadowReach : settings.FilterRadius;
const float guard = std::ceil(filterReach + settings.NormalBias * c_NormalBiasReach) + 1.0f;
const float widen = tileSize / std::max(tileSize - 2.0f * guard, 1.0f);
// The near plane follows the light's own range (a rect light's from its face).
const float nearRange = record.PositionRange.w;
float tanHalfAngle = 1.0f; // A cube face's 45 degrees
if (light.Type == RenderData::c_LightSpot)
	tanHalfAngle = std::tan(std::clamp(std::acos(std::clamp(record.SpotAngles.y, -1.0f, 1.0f)), 0.001f, c_MaxSpotShadowHalfAngle));
for (uint32_t view = 0; view < light.ViewCount; view++)
{
	LocalShadowViewKey& key = light.Views[view].Key;
	key.Position = glm::vec3(record.PositionRange);
	key.Direction = light.Type == RenderData::c_LightSpot ? glm::vec3(record.DirectionType) : c_FaceDirections[view];
	key.Range = range;
	// Within its bounds, and below half the range for tiny lights (std::clamp would need the bounds in order).
	key.Near = std::min(std::max(nearRange * c_LocalShadowNearScale, c_MinLocalShadowNear), std::min(c_MaxLocalShadowNear, nearRange * 0.5f));
	key.TanHalfAngle = tanHalfAngle * widen;
	key.Tile = light.Tiles[view];
```

1. **Line 644:** the margin is the filter radius plus the reach of the normal bias, rounded up, plus one texel.
2. **Line 645:** `widen` is the tile over the part of it that shows the true view.
3. **Line 650:** a spot light's half angle is clamped to 80 degrees (1.396 :term[radians]{id=radian}).
4. **Line 655:** a point light's views look along the six axes.
5. **Line 659:** the tangent of the half angle grows by `widen`.

:::example[A 256 tile]
The defaults are a filter radius of 1.5 and a normal bias of 1.5, in texels. The normal bias moves a lookup by up to 1.4142 times its size: 1.5 × 1.4142 = 2.12. The margin is ceil(1.5 + 2.12) + 1 = 5 texels. For a tile of 256 texels, `widen` is 256 / (256 − 10) = 1.0407, so a cube face's tangent of 1.0 becomes 1.0407, a half angle of 46.1 degrees instead of 45.

One texel then covers 2 × 1.0407 / 256 = 0.00813 units at depth 1. At a depth of 10 m a texel is 8.1 cm wide, and the normal bias of 1.5 texels moves the lookup 12 cm off the surface.
:::

### The view cache

A view is drawn again only when what it shows changed. `LocalShadowViewKey` holds what the picture depends on in :term[world space]{id=world-space}: the light's position, the view's direction, the range, the :term[near plane]{id=near-plane}, the field of view with its band, and the tile. The world has changed also when a version moves that `LocalShadowContent` records (the scene's GPU tables, the :term[geometry pool]{id=geometry-pool}, the textures of alpha-masked materials, the level-of-detail error). Then every view is drawn again.

The third way is a caster. Strata follows the world bounds of every object within a shadowed light's range, up to 4,096 for each light the quality shadows. A change that reaches a drawn view marks it dirty. A grid of the lights' reach finds the lights a change can reach, and each drawn view keeps a box that no reaching change misses, so most changes pass most lights with one comparison.

```mermaid caption="The states of one shadow view. A view with no picture waits for a place in the budget, and a view whose picture is out of date keeps showing it until a new drawing replaces it." alt="Three states: no picture, cached, and waiting. Drawing takes a view from no picture or from waiting to cached. A changed key or a caster that reaches the view takes a cached view to waiting. A view that loses its place in the budget stays waiting."
stateDiagram-v2
	[*] --> NoPicture
	NoPicture --> Cached: drawn
	Cached --> Waiting: key changes or a caster reaches it
	Waiting --> Cached: drawn again
	Waiting --> Waiting: budget goes to other views
```

The camera is no part of the key, so a walking camera draws nothing again. A lamp that moves keeps its old shadow until the budget draws its views again. `BuildLocalShadowData` builds the matrices of a view that holds a picture from the key that drew it, so the lookup always agrees with the texels in the tile.

### The budget of views and the fades

Drawing a view costs GPU time, so a renderer that spreads lighting updates, the default, draws at most `LocalShadowViewsPerFrame` views each frame. The preset rows set it to 12, 12, 24 and 48. A renderer of single pictures, such as an asset's small preview, draws every view at once.

```cpp src="Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp#L991-L1003"
		if (cache && view.HasContent && !view.Dirty && view.Key == view.DrawnKey)
		{
			view.WaitedFrames = 0;
			continue;
		}
		if (!light.Ranked)
			continue;
		waiting.push_back(Waiting { index, face, !view.HasContent, view.WaitedFrames, light.Importance * static_cast<float>(view.WaitedFrames + 1) });
	}
}
std::vector<uint8_t> chosen(waiting.size(), 1);
const uint32_t budget = std::max(m_Specification.Quality.LocalShadowViewsPerFrame, 1u);
if (spread && waiting.size() > budget)
```

1. **Line 991:** a view with a picture, no change and the same key as its drawing waits for nothing.
2. **Line 996:** a light that lost its rank is not drawn again; it only fades.
3. **Line 998:** the score is the light's importance times the frames waited, plus one.
4. **Line 1002:** the budget is at least one view.

When more views wait than the budget allows, three groups take places in turn. First, a quarter of the budget goes to views with a picture that have waited longest, so that none starves while nearer lights change every frame. Next come views with no picture, in the order of the lights, so a light's views are drawn together and the light can appear. The rest go by score.

:::example[A gust moves four lamps]
The budget is 12 views, and a gust moves four point lights, so 24 views wait. All have pictures. In the first frame 3 places (a quarter of 12) go to the longest waiters and 9 by score. The other 12 wait one frame and are drawn in the second frame. Until then each keeps its old shadow, so a shadow trails its lamp by at most two frames.
:::

A light appears only when all its views hold pictures. Then its strength rises by a step each frame: `min(seconds / 0.2, 1/8)`, where `seconds` is the time since the previous frame.

At 60 :term[frames per second]{id=frame-rate} the step is 16.7 ms over 0.2 s, which is 0.083, so a fade takes 12 frames and 0.2 s. At 240 frames per second the step is 0.021, 48 frames and 0.2 s again. At 10 frames per second the step would be 0.5, but the cap of one eighth keeps it at 0.125: 8 frames, 0.8 s. A light that loses its rank fades out at the same speed.

### Casters and culling

A **caster** is an object that is drawn into a shadow view. `FindLocalShadowCasters` runs one job per light with drawn views, and each job starts from a sphere query of the light's range on the :term[spatial index]{id=spatial-index}.

```cpp src="Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp#L1213-L1240"
for (const uint32_t proxy : job.Candidates)
{
	const uint32_t flags = renderScene.GetProxyFlags(proxy);
	const uint32_t required = RenderProxyFlags::Active | RenderProxyFlags::Indexed | RenderProxyFlags::CastShadows | RenderProxyFlags::MeshBounds;
	if ((flags & required) != required || renderScene.GetInstanceCount(proxy) == 0 || (area && (flags & RenderProxyFlags::LightSurface) != 0))
		continue;
	const AABB& bounds = renderScene.GetWorldBounds(proxy);
	const glm::vec3 relativeMin = bounds.Min - cameraPosition;
	const glm::vec3 relativeMax = bounds.Max - cameraPosition;
	if (!BoxReachesSphere(relativeMin, relativeMax, lightRelative, range))
		continue;
	const glm::vec3 center = (bounds.Min + bounds.Max) * 0.5f;
	const float radius = glm::length((bounds.Max - bounds.Min) * 0.5f);
	bool casts = false;
	for (uint32_t offset = 0; offset < viewCount; offset++)
	{
		const LocalShadowDrawView& drawView = m_LocalShadowViews[firstView + offset];
		if (!BoxInPlanes(relativeMin, relativeMax, drawView.Planes))
			continue;
		const LocalShadowViewKey& key = light.Views[drawView.Face].Key;
		const float fraction = radius / (std::max(glm::length(center - key.Position), key.Near) * key.TanHalfAngle);
		if (fraction * static_cast<float>(key.Tile.Size) < c_MinCasterTexels)
		{
			job.SubTexelCasters++;
			continue;
		}
		job.ViewCasters[offset].emplace_back(proxy, fraction);
		casts = true;
```

1. **Line 1216:** an object must be active, indexed and a caster, and its bounds must be known.
2. **Line 1217:** an object that shows a rectangle light's own face is omitted from that light's views.
3. **Lines 1233–1234:** the object's size in the view's picture, in texels; below one texel it is not drawn.
4. **Line 1239:** the object is added to the view with its size, which later picks its :term[level of detail]{id=level-of-detail}.

The GPU-driven path leaves the exact tests to the culling shader ([GPU-driven rendering](../draw/gpu-driven.md)). The CPU still decides which views are drawn. The culling shader works in batches of at most `ST_CULL_MAX_LOCAL_VIEWS` views, which is 12. The first batch goes with the sun's cascades, and later batches use the mode `ST_CULL_MODE_LOCAL`. Each batch is drawn before the culling of the next.

:::rule[Keep the lamp out of its own shadow]
The lamp's own mesh sits at the light's position, so it would shadow everything around it. Turn **Cast Shadows** off on the lamp's mesh, or place the light outside the model. Rectangle lights do this by themselves for a mesh tagged `LightSurface`.
:::

### Drawing and the lookup

`DrawLocalShadows` visits each drawn view. A :term[fullscreen triangle]{id=fullscreen-triangle} at depth 0, the :term[far plane]{id=far-plane} in :term[reversed-Z]{id=reversed-z}, clears the view's tile, because a clear of the whole texture would also clear tiles that are cached. Then the casters are drawn with the `LocalShadowMesh` vertex shader, a perspective view without the sun's pancaking. A push constant names the view, `light * 6 + face`, which selects its matrix.

The forward pass finds a light's slot in the :term[light record]{id=light-record} (`SpotAngles.z` holds the slot plus one). Per slot, `LocalShadowData` holds six matrices, six tiles with the size of a texel, the biases and the filter radius, the light's strength and its position. It sits at scene binding `t13`.

```slang src="Strata/shaders/Include/LocalShadows.slang#L63-L96"
float SampleLocalShadow(uint slot, float3 relativePosition, float3 normal, float2 pixel)
{
	float4 parameters = u_LocalShadows[slot].Parameters;
	uint view = SelectLocalShadowView(slot, relativePosition);
	float4x4 viewProjection = u_LocalShadows[slot].ViewProjection[view];
	float4 tile = u_LocalShadows[slot].Tiles[view];
	float3 toLight = u_LocalShadows[slot].Light.xyz - relativePosition;
	float lightDistance = length(toLight);
	if (!(lightDistance > 0.0))
		return 1.0;
	float texelWorld = max((mul(viewProjection, float4(relativePosition, 1.0))).w, 0.0) * tile.w;
	float3 offsetPosition = relativePosition + normal * (parameters.y * texelWorld) + toLight * (parameters.x * texelWorld / lightDistance);
	float4 clip = mul(viewProjection, float4(offsetPosition, 1.0));
	if (!(clip.w > 0.0))
		return 1.0;
	float3 ndc = clip.xyz / clip.w;
	float2 tileUV = NDCToUV(ndc.xy);
	if (any((tileUV < float2(0.0))) || any((tileUV > float2(1.0))))
		return 1.0;
	float2 atlasTexel = 1.0 / float2(TextureSize(u_LocalShadowAtlas, 0));
	float2 uv = tile.xy + tileUV * tile.z;
	float2 lowest = tile.xy + 0.5 * atlasTexel;
	float2 highest = tile.xy + float2(tile.z) - 0.5 * atlasTexel;
	float2 radius = max(parameters.z, 0.0) * atlasTexel;
	float2x2 rotation = LocalShadowSampleRotation(pixel);
	// The comparison sampler tests reference < stored: true where a caster is nearer to the light (reversed-Z).
	float shadowed = 0.0;
	for (int index = 0; index < 16; index++)
	{
		float2 tap = clamp(uv + mul(rotation, c_LocalShadowPoissonDisk[index]) * radius, lowest, highest);
		// An explicit level: lights are shaded in non-uniform control flow, where implicit derivatives are undefined.
		shadowed += u_LocalShadowAtlas.SampleCmpLevelZero(u_ShadowCompareSampler, tap, ndc.z);
	}
	return lerp(1.0, 1.0 - shadowed / 16.0, clamp(parameters.w, 0.0, 1.0));
```

1. **Lines 66–67:** the face is chosen from the direction to the pixel, and its matrix is read.
2. **Lines 73–74:** the biases are in texels at the surface's depth: `texelWorld` is the world size of a texel there.
3. **Lines 80–81:** a lookup outside the view counts as lit.
4. **Line 92:** each tap is clamped inside its tile.
5. **Line 96:** the strength mixes the result toward lit, which makes the fade.

Take a pixel at (3, −7, 7) m from the light. The largest absolute value is 7, shared by y and z. The shader tests `magnitude.y >= magnitude.z`, so the tie goes to y. Since y is negative, the face is −Y, index 3.

The sixteen taps follow a Poisson disk (a spread of 16 points that never clump) scaled by the filter radius and turned by :term[interleaved gradient noise]{id=interleaved-gradient-noise}, a cheap :term[hash]{id=hash} of the pixel's position. The noise depends only on the pixel, so a still picture is the same every frame, with or without temporal anti-aliasing.

:::why
The noise turned from frame to frame under 0.7.0, and temporal anti-aliasing averaged it away. A shadow must look right without that history, so release 0.8.0 fixed the pattern. The price is a faint grain on soft edges under temporal anti-aliasing, which the release notes list as a known issue.
:::

### What it does not do

Strata gives no shadow of a point or spot light a width that follows the light's size. A lantern's `SourceRadius` widens only its highlights, and the softness of the shadow's edge is the filter radius, at most 8 texels. Soft shadows from the light's size, as percentage-closer soft shadows do, are not done.

Rectangle lights are the exception. Each takes six views around its face's centre, and the face behind a one-sided light is never drawn: its tile is only cleared. The guard band grows by an eighth of the tile for the soft filter, and the casters are also drawn from behind into a second atlas of the same tiles. At most four rectangle lights hold a shadow at once. [Area lights](../light/area-lights.md) teaches the filter.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One cube map per light | The textbook method of Real-Time Rendering | No allocator, no guard band, one lookup instruction | Memory in proportion to lights times the largest size, and one texture per light |
| Dual-paraboloid maps | The 2002 paper in Further reading | Two views for a point light, not six | Cut triangles to keep edges straight, and a worse fit near the seam |
| Static and dynamic maps per light | Many games with lamps that never move | Draw only the moving objects again | Two maps per light, and a rule to split casters |
| Virtual shadow maps | Unreal Engine 5 | Detail where the camera looks, with pages as the unit | A large system of page tables and feedback |
| Fixed slots, no quadtree | Simple engines | A simple allocator | One size for all lights, so far lamps waste texels |

## How it is tested

The suite `Renderer.ShadowAtlas` checks the allocator alone, with no GPU. Tiles of every size do not overlap. An atlas fills exactly, and freed tiles merge. Sizes in descending order always fit, `FitTileSizes` steps down in rounds, and the same requests give the same tiles. Run it with `StrataTests.exe --test-suite=Renderer.ShadowAtlas`.

The suites `GPU.SceneRenderer.LocalShadows` and `GPU.SceneRenderer.ManyLocalShadows` draw real frames on the shared device. They check that no atlas exists while no light has `CastShadows` on. They check that a still scene draws no view and that the budget of views holds.

A point light shows no seam between faces, and 64 and 200 shadowed lights cast shadows alike on both paths. Fades take the same time at any frame rate, and a light whose tiles change size keeps its shadow. Each suite ends by checking that the device reported no new errors.

The perf tests measure frames with 16, 64 and 256 shadowed lights, once with every view drawn and once with every view cached. One more test moves 1,000 casters under 256 lights, and its search for casters has a target of 0.5 ms that is not yet a budget. The perf tests run only in Release and :term[Dist]{id=dist} builds, with `ctest --preset windows-release -L perf`.

## Changing it safely

- A new input of how casters are drawn goes into `LocalShadowContent` or the view key. Without it a cached view keeps the old picture, and no test of one frame sees the fault.
- A change to what a view draws goes into both paths, the CPU's test in `FindLocalShadowCasters` and `Cull.comp`. The tests `GPU.SceneRenderer.GPUDriven` and `.Feedback` must pass.
- Position, direction and range of a light stay in the key in world space, never relative to the camera. A camera in the key would draw every view again whenever you walk.
- Keep every tap inside its tile. A new filter, or a larger bias, must grow the guard band by what it reaches (`c_NormalBiasReach`).
- Any new pass gets a :term[GPU stage]{id=gpu-stage-strata} with the others of the module, and a pass that reads the atlas must bind a dummy when no atlas exists.
- Run `GPU.SceneRenderer.LocalShadows` and `GPU.SceneRenderer.ManyLocalShadows`, and on a change that costs time the perf tests of the frames with many lights.

## What went wrong before

Release 0.7.0 gave 16 lights a shadow. Its shadows could pop and blink while the camera moved, and the filter noise turned from frame to frame under temporal anti-aliasing. Release 0.8.0 added the rank margin, the fades by time and the fixed noise.

The test `Walking past more lamps than have shadows, every shadow fades in and out over frames instead of popping` in `GPU.SceneRenderer.ManyLocalShadows` guards this. It walks a camera along a street of lamps where only two may have shadows. It checks that shadows move from lamp to lamp over several frames, and that no lamp without a shadow matters more than 1.25 times a lamp that keeps one.

## Summary

- One depth atlas holds all tiles, so far lamps take small tiles and memory is fixed, where a cube map per light costs 24 MiB each at 1024 texels.
- A quadtree allocator hands out power-of-two tiles in Morton order and merges free quarters, so the same requests give the same tiles.
- Tile sizes follow the pixels of a light's range and shrink from the least important light to fit seven eighths of the atlas; a guard band keeps every tap inside its face.
- Views are cached by a world-space key and the changes that reach them; a budget of views per frame draws the rest, and fades take 0.2 s but at least 8 frames.
- A lookup picks a cube face by the major axis and takes 16 clamped taps turned by fixed noise.

## Check yourself

1. Why does Strata give a far lamp a smaller tile than a near lamp?
   - (a) A far lamp covers few pixels, so a small tile gives the same sharpness and frees room.
   - (b) A tile of 128 texels draws faster than one of 1024, which is the only reason.
   - (c) A texture cannot hold two tiles of the same size.
   - (d) The guard band needs a small tile.

   :::answer{tests="atlas-idea"}
   (a). The picture only needs as many texels as the light covers pixels. (b) names a side effect, not the reason. (c) is wrong, since many tiles of one size are normal. (d) is wrong: a small tile makes the guard band a larger share.
   :::

2. In an empty 1024 atlas with a smallest tile of 128, requests for 256, 256 and 512 arrive in that order. Where does each land?

   :::answer{tests="allocator-trace"}
   The first 256 splits the first quarter and takes (0, 0). The second takes the next block, (256, 0). No free 512 block is left in the first quarter, so the 512 takes the first free quarter in Morton order: (512, 0).
   :::

3. A lamp's range spans a radius of 300 pixels. Its tile has been 128, 256 or 512. What size does it have now in each case?

   :::answer{tests="size-and-band"}
   The wanted size is 512, the next power of two above 300. For a tile of 128 the band is 51 to 160 pixels, 300 lies outside, so the size becomes 512. For 256 the band is 102 to 320, 300 lies inside, so it stays 256. For 512 the band is 205 to 640, so it stays 512.
   :::

4. A game runs at 10 frames per second on a weak machine, and a lamp's shadow fades in. A second machine runs at 120 frames per second. How long does the fade take on each?

   :::answer{tests="cache-budget"}
   At 10 frames per second the step is `min(0.1 / 0.2, 1/8)` = 0.125, so 8 frames and 0.8 s. At 120 frames per second the step is 0.00833 / 0.2 = 0.0417, so 24 frames and 0.2 s. The cap of one eighth only matters where frames are slow.
   :::

5. A point light stands at the origin. For the pixel at (3, −7, 7) m, which face and tap pattern are used?

   :::answer{tests="sample-path"}
   The face is −Y, index 3: the largest magnitude is 7, shared by y and z, and the test `magnitude.y >= magnitude.z` chooses y, which is negative. The 16 taps follow a Poisson disk, scaled by the filter radius and turned by the pixel's fixed noise angle.
   :::

## Exercises

1. **Basic.** Take a tile of 128 texels, a filter radius of 8 and a normal bias of 1.5. Find the guard band, the widened tangent and the width of one texel at a depth of 10 m.

   :::answer[Worked solution]{tests="size-and-band"}
   The normal bias reaches 1.5 × 1.4142 = 2.12 texels. The margin is ceil(8 + 2.12) + 1 = 12 texels. The widened tangent is 128 / (128 − 24) = 1.2308, a half angle of 50.9 degrees. One texel covers 2 × 1.2308 / 128 = 0.01923 units at depth 1, so 0.192 m at 10 m. A fifth of the tile is margin, and the picture shows the true view in only 104 texels.
   :::

2. **Medium.** Write a program that prints the filter's rotation angle for the pixel (3, 5) over four frames, once for the engine's rule and once for an invented rule that adds 137.5 degrees each frame. Say which rule needs temporal anti-aliasing.

   :::answer[Worked solution]{tests="sample-path" solution="sketches/light-local-shadows-rotation.cpp"}
   The engine's angle is the fraction of 52.98 times the fraction of the :term[dot product]{id=dot-product} of the pixel with two constants, times 360 degrees. Nothing in it names the frame.

   ```cpp sketch="light-local-shadows-rotation.cpp"
   #include <cmath>
   #include <cstdio>

   float Fraction(float value)
   {
   	return value - std::floor(value);
   }

   // The angle of the filter's rotation at a pixel, as LocalShadowSampleRotation works it out, in degrees.
   float GetFixedAngle(float x, float y)
   {
   	return 360.0f * Fraction(52.9829189f * Fraction(x * 0.06711056f + y * 0.00583715f));
   }

   // An invented rule that also turns by the frame: a pattern like this needs temporal anti-aliasing to average it.
   float GetTurningAngle(float x, float y, int frame)
   {
   	return std::fmod(GetFixedAngle(x, y) + 137.5f * static_cast<float>(frame), 360.0f);
   }

   int main()
   {
   	for (int frame = 0; frame < 4; frame++)
   		std::printf("frame %d: fixed %.1f, turning %.1f\n", frame, GetFixedAngle(3.0f, 5.0f), GetTurningAngle(3.0f, 5.0f, frame));
   	std::printf("neighbours: %.1f %.1f %.1f\n", GetFixedAngle(3.0f, 5.0f), GetFixedAngle(4.0f, 5.0f), GetFixedAngle(3.0f, 6.0f));
   	return 0;
   }
   ```

   ```text output-of="light-local-shadows-rotation.cpp"
   frame 0: fixed 76.9, turning 76.9
   frame 1: fixed 76.9, turning 214.4
   frame 2: fixed 76.9, turning 351.9
   frame 3: fixed 76.9, turning 129.4
   neighbours: 76.9 276.9 188.2
   ```

   1. **Line 12:** the angle is a fraction of the pixel's position alone.
   2. **Line 18:** the invented rule adds a turn per frame.
   3. **Lines 23–24:** the loop prints both rules for one pixel over four frames.

   The fixed rule prints 76.9 in every frame, so a still picture is the same with and without temporal anti-aliasing. The invented rule turns by 137.5 degrees each frame, so one pixel shows four noises. Only a history that averages them can hide that: the invented rule needs temporal anti-aliasing and the engine's rule does not.
   :::

3. **Hard.** Follow one point light with a search from its tile size to the forward pass's lookup. Name the file and the function of each step.

   :::answer[Worked solution]{tests="sample-path"}
   Search for `FitTileSizes`. It is defined in `Strata/src/Strata/Renderer/ShadowAtlasAllocator.cpp` and called by `SceneRenderer::PlaceLocalShadowTiles` in `SceneRendererLocalShadows.cpp`, which then allocates the tiles. `SceneRenderer::BuildLocalShadowData` in the same file writes the light's slot: matrices, tiles and strength. `SceneRenderer::DrawLocalShadows` draws the views into the tiles. The forward shader `Strata/shaders/Scene/Forward.frag.slang` reads the slot from `SpotAngles.z` and calls `SampleLocalShadow` in `Strata/shaders/Include/LocalShadows.slang`, which reads the slot at binding `t13`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp`: ranking, tiles, views, cache, schedule, casters, atlas and drawing.
- `Strata/src/Strata/Renderer/ShadowAtlasAllocator.h`: the allocator and `FitTileSizes`.
- `Strata/shaders/Include/LocalShadows.slang`: `LocalShadowData` and `SampleLocalShadow`.
- Tests: `Renderer.ShadowAtlas`, `GPU.SceneRenderer.LocalShadows`, `GPU.SceneRenderer.ManyLocalShadows`.
- Settings: the rows `LocalShadowAtlasSize`, `LocalShadowMaxTile`, `MaxShadowedLocalLights` and `LocalShadowViewsPerFrame` of `Renderer.Quality`, and per light `CastShadows`, `ShadowBias`, `ShadowNormalBias` and `ShadowFilterRadius`.
- Command: `editor.perf` reports `localShadowRequested`, `localShadowLights`, `localShadowFading`, `localShadowTileSizes` and `localShadowTileSizeCounts` in `renderStats`.

## Further reading

- Lance Williams, "Casting curved shadows on curved surfaces" (1978): the first shadow maps (intermediate).
- Stefan Brabec, Thomas Annen and Hans-Peter Seidel, "Shadow mapping for hemispherical and omnidirectional light sources" (2002): dual-paraboloid shadows (advanced).
- Tomas Akenine-Möller, Eric Haines and Naty Hoffman, Real-Time Rendering, the chapter on shadows (intermediate).
- Epic Games, the documentation of Unreal Engine's virtual shadow maps (intermediate).
