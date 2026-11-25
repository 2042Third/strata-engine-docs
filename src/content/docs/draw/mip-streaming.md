---
id: draw/mip-streaming
title: "Mip streaming"
description: "How Strata keeps only the texture levels the screen needs, raises them before they are missed and drops them when nothing needs them, without a frame waiting."
kind: internals
size: L
tracks: [E]
needs: [draw/asset-requests, draw/gpu-driven, assets/texture-cooking, assets/uploads, gpu/binding]
time: 75
learn:
  - id: wanted-level
    text: compute the mip level a texture wants from its size, its tiling and the pixels one texture unit spans
  - id: read-ranking
    text: compute the order in which reads of missing levels run, with and without a camera cut
  - id: raise-flow
    text: trace the raise of one texture from the view's report to its new bindless slot
  - id: slot-rule
    text: explain why a cached bindless slot is a bug and why a pixel comparison must wait for the fades
since: 0.3.0
status: final
---

A scene can hold thousands of textures, and most of them are drawn small, far away or not at all. The **mip streaming** system keeps resident only the :term[mip levels]{id=mip} the screen needs. It raises a texture's detail before the player misses it, drops detail when nothing needs it, and never makes a frame wait for a read.

This page follows the data from the first load of a texture to the new :term[bindless slot]{id=bindless} of a raised one. It does not teach mip chains, the cooked layout, budgets or the upload steps: [textures](../assets/textures.md), [texture cooking](../assets/texture-cooking.md), [residency](../assets/residency.md) and [uploads](../assets/uploads.md) own those. It also does not stream meshes, and it does not use virtual texturing.

## The problem and how engines solve it

A game shows more texture detail than a :term[graphics processing unit]{id=gpu} (GPU) can hold. A 2048 by 2048 texture with a full chain of levels needs about 5.6 MB when one :term[byte]{id=byte} holds a texel, and a scene can use thousands of them. On screen, a wall ten metres away may span only 128 pixels, so its level 0 is 16 times wider than the screen needs. The extra levels use memory for no visible gain.

Three approaches answer this. The first keeps whole textures and removes the ones used least recently. It is simple and needs no per-pixel knowledge, but every texture costs its full size while resident, so a single large texture seen from far away holds memory it cannot show. A texture that returns after an :term[eviction]{id=eviction} must be read whole again.

The second approach is virtual texturing with sparse residency. The texture is cut into tiles, and the graphics card keeps only the tiles that the screen touches. A page table maps each requested tile to memory, and a feedback pass reports which tiles are missing. This saves the most memory, because even one huge texture costs only the visible part. It costs the most complexity: the hardware needs sparse features, every sample goes through an extra lookup, and filtering across tile edges needs care.

The third approach is mip streaming, which Unreal and Unity use in a similar form. Each texture keeps a **mip tail**: the smallest levels, a few KB in total, which stay resident whatever happens. The engine raises or drops the larger levels as a whole, driven by one number per texture: the finest level the screen needs. Mip streaming saves less than tiles, since a texture visible in a corner still holds its whole level. It keeps the sampling hardware unchanged, though, and it works on every device.

Strata chooses the third approach. The reason is that its pipeline stays simple at every other point: materials sample ordinary textures by a table index, and a texture without its fine levels still draws, only coarse. A game never meets a hole. The cost is the one named above: no tiles, and so no help for a single enormous texture.

The measure behind all of this is **texel density**: how many screen pixels one unit of a texture's coordinates covers, which Strata calls `UVPixels`. A texel is one pixel of a texture. If a unit of the texture spans 128 screen pixels, and the texture has 2048 texels along that unit, each screen pixel sees 16 texels. A level 16 times smaller on each side is enough.

## The map: from a view's report to a bindless slot

The streamer is `TextureStreamer`, an extension of the :term[asset manager]{id=asset-manager}, one per manager. Its decisions live in `TextureStreamingPolicy`, a class with no graphics code, so unit tests can run it alone. Everything runs on the :term[main thread]{id=main-thread}, except the reads themselves, which run on the :term[streaming queue's]{id=streaming-queue} workers.

A load of a texture first reads only a prefix of its file. This is a **partial load**: the asset becomes ready with the :term[header]{id=header} and the mip tail, and the streamer reads the rest as the screen needs it.

The later reads are **range reads**: reads of a byte range of an asset that is already loaded. They go through the same streaming queue, and the same in-flight byte budget, as loads.

```mermaid caption="Data flow of mip streaming: each frame's views report what they drew, the policy turns reports into wanted levels, and the streamer reads, raises and drops levels." alt="A flow from the renderer's frame, to the report of drawn textures, to the policy's wanted level, to the ranked range read, to the new GPU texture with a new bindless slot and a fade-in. A second path from the policy to the drop of unused levels."
flowchart TD
	R["SceneRenderer frame: visible textures"] --> V["ReportView: size on screen and UVPixels"]
	V --> P["TextureStreamingPolicy: wanted level, rank"]
	P -->|"below wanted"| Q["RequestRange: ranked read"]
	Q --> U["OnUpdate polls the read"]
	U --> L["Texture::RaiseLevels: new GPU texture, copy, upload"]
	L --> S["new bindless slot, table entry follows"]
	S --> F["fade-in over 0.25 s"]
	P -->|"unused for 30 s, or budget pressure"| D["drop levels: new smaller GPU texture"]
	D --> S
```

The files are few. `Strata/src/Strata/Renderer/TextureStreamer.h` and its `.cpp` hold the policy and the streamer. `Strata/src/Strata/Renderer/Texture.cpp` holds the raise and the drop of a single texture. `Strata/src/Strata/Renderer/TextureTable.h` holds the table that materials index and the fades. `Strata/src/Strata/Asset/AssetManager.cpp` holds the prefix and range reads.

## The contract

What the streamer promises, and what its callers must do, comes in a few rules, each with a reason.

1. **A texture drawn always draws.** After its first load a texture has its tail, so a surface shows coarse detail, never the loading fallback. The streamer drops a texture in view only down to its tail. Reason: a frame never waits for a read.
2. **The streamer asks, the views decide.** A view reports each texture it drew with its size on screen and its `UVPixels`. The streamer never looks at the scene. Reason: reports come from the views the :term[renderer]{id=renderer} already extracted, so streaming costs no extra scene walk.
3. **Detail rises at once and falls slowly.** The **wanted level** of a texture is the coarsest level that still shows each texel at least as fine as the screen does. A finer need raises the target in the same frame. A coarser need lowers it only after the finer level was not needed for 30 s. Reason: a camera that turns back finds its detail still there.
4. **Material data keeps a stable table index.** A raise gives the texture a new bindless slot, and the :term[texture table]{id=texture-table-strata} entry follows it. Code that draws must read the slot each frame and never keep it. Reason: a stored slot names a GPU texture that the streamer may already have replaced.
5. **Every read and upload is budgeted.** Range reads use the manager's streaming queue; copies on the GPU and uploads use the frame's :term[upload budgets]{id=upload-budget-gpu}. Reason: a raise is spread over frames and cannot make one frame long.
6. **A pixel comparison waits for the fades.** Raised levels fade in over 0.25 s unless the renderer turns the fade off. A test that compares pixels while a fade runs sees a half-raised texture. Reason: the fade is a real part of the image.

The **fade-in** is the slow change of a raised texture's finest sampled level, from the level it showed before to its new finest, over 0.25 s, so that new detail does not pop into view.

:::rule[Resolve bindless slots every frame]
The engine's guide says to resolve bindless slots every frame and never to cache them, because mip streaming replaces a texture's GPU texture and slot. See [binding](../gpu/binding.md) for the table and [asking for assets at draw time](../draw/asset-requests.md) for what a frame resolves.
:::

## A toy streamer

The toy has three textures with different needs. Each frame it computes the wanted level of each, ranks the textures that are below it by missing levels times coverage, and raises one of them. The coverage is the share of the view's height that the texture's surface spans, from 0 to 1. The real streamer raises several per frame, but the order is the same idea. Watch the ranking line and the order in which the textures come in.

```cpp sketch="draw-mip-streaming-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Texture
{
	const char* Name;
	uint32_t Size;
	uint32_t MipCount;
	uint32_t Resident;
	float UVPixels;
	float Coverage;
};

uint32_t GetWantedLevel(const Texture& texture)
{
	if (!(texture.UVPixels > 1.0f))
		return texture.MipCount - 1;
	const float level = std::floor(std::log2(static_cast<float>(texture.Size) / texture.UVPixels));
	return static_cast<uint32_t>(std::clamp(level, 0.0f, static_cast<float>(texture.MipCount - 1)));
}

int main()
{
	// A first load holds the tail: the levels up to 32 texels, so level 6 of 2048 and level 5 of 1024.
	std::vector<Texture> textures = {
		{ "Wall", 2048, 12, 6, 512.0f, 0.5f },
		{ "Floor", 2048, 12, 6, 64.0f, 0.8f },
		{ "Statue", 1024, 11, 5, 1024.0f, 0.1f }
	};

	for (uint32_t frame = 1; frame <= 3; frame++)
	{
		Texture* best = nullptr;
		float bestScore = 0.0f;
		for (Texture& texture : textures)
		{
			const uint32_t wanted = GetWantedLevel(texture);
			if (texture.Resident <= wanted)
				continue;
			const float score = static_cast<float>(texture.Resident - wanted) * texture.Coverage;
			if (score > bestScore)
			{
				bestScore = score;
				best = &texture;
			}
		}
		if (!best)
			break;
		std::printf("frame %u: raise %s from level %u to %u (score %.2f)\n", frame, best->Name, best->Resident, GetWantedLevel(*best), bestScore);
		best->Resident = GetWantedLevel(*best);
	}
	return 0;
}
```

```text output-of="draw-mip-streaming-toy.cpp"
frame 1: raise Wall from level 6 to 2 (score 2.00)
frame 2: raise Floor from level 6 to 5 (score 0.80)
frame 3: raise Statue from level 5 to 0 (score 0.50)
```

1. **Line 21:** the wanted level, the formula of the real streamer without tiling.
2. **Lines 28–31:** each texture starts at its tail, the first level of at most 32 texels.
3. **Line 41:** a texture at or finer than its wanted level needs nothing.
4. **Line 43:** the rank: missing levels times coverage.
5. **Line 53:** the raise goes straight to the wanted level, as one range read of the missing levels does.

The wall is missing four levels over half the view, so it comes first. The floor is missing one level over most of the view. The statue is missing five levels, but covers a tenth of the view, so it comes last despite the largest gap. Missing levels alone would have put the statue first; coverage keeps a small object from taking the read before a large one.

## The real code, in the order data flows

### The first load reads a prefix

A texture's file is cooked with its smallest level first, so the bytes a partial load needs lie at the start. `ReadPrefix` reads the first 64 KiB (`c_AssetPrefixHeadBytes`), asks the type's prefix function how many bytes it needs, and reads more only when that is larger than the head.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L1665-L1697"
bool AssetManagerBase::ReadPrefix(const AssetMetadata& metadata, std::vector<uint8_t>& outData, uint64_t& outStoredSize, std::string* outError)
{
	outStoredSize = 0;
	const AssetPrefixFunction* prefix = AssetLoaderRegistry::FindPrefix(metadata.Type);
	const uint64_t storedSize = metadata.StoredSize;
	// The head, then what the prefix needs beyond it. A head that cannot be read (a stored size that no longer matches the
	// stored form) is no reason to fail: the whole stored form is read instead, as is one the function does not split.
	if (prefix && storedSize > 0 && ReadAssetRange(metadata, 0, std::min(storedSize, c_AssetPrefixHeadBytes), outData, nullptr))
	{
		const std::optional<uint64_t> prefixSize = (*prefix)(outData, storedSize);
		if (prefixSize && *prefixSize > 0 && *prefixSize < storedSize)
		{
			if (*prefixSize <= outData.size())
			{
				outData.resize(static_cast<size_t>(*prefixSize));
			}
			else
			{
				std::vector<uint8_t> rest;
				if (!ReadAssetRange(metadata, outData.size(), *prefixSize - outData.size(), rest, outError))
					return false;
				outData.insert(outData.end(), rest.begin(), rest.end());
			}
			outStoredSize = storedSize;
			return true;
		}
		// Nothing to split: a head that is the whole stored form is all the load needs.
		if (outData.size() == storedSize)
			return true;
	}
	outData.clear();
	return ReadAssetData(metadata, outData, outError);
}
```

1. **Line 1672:** the head read. A head that cannot be read is no failure; the code falls through to a whole read.
2. **Line 1674:** the type's prefix function answers with the size the load needs, or nothing.
3. **Lines 1677–1679:** most textures need less than the head holds, so the buffer is cut to size.
4. **Lines 1683–1686:** a larger prefix reads the rest and joins it to the head. A failed read fails the load.
5. **Lines 1691–1696:** a head that is the whole file ends the load. Any other case reads the whole :term[stored form]{id=stored-form}.

For a texture the prefix function is `Texture::GetLoadPrefixSize`. It asks `GetCookedTexturePrefixSize` for the header plus the levels up to 32 texels on their larger side (`Texture::c_ResidentTailDimension`). It returns nothing, and so the whole file is read, when the texture is block-compressed in a format the device cannot sample, because those levels are decoded at load, all at once.

The layout does the arithmetic. `GetMipTailByteRange` finds the first level whose width and height are both at most the limit, and takes the byte range from that level's offset to the end.

```cpp src="Strata/src/Strata/Renderer/CookedTexture.cpp#L230-L257"
CookedTextureByteRange CookedTextureLayout::GetMipTailByteRange(uint32_t maxDimension) const
{
	CookedTextureByteRange range;
	range.Offset = HeaderSize;
	range.FirstLevel = MipCount;
	for (uint32_t level = 0; level < MipCount; level++)
	{
		if (Levels[level].Width <= maxDimension && Levels[level].Height <= maxDimension)
		{
			range.FirstLevel = level;
			break;
		}
	}
	if (range.FirstLevel == MipCount)
		return range;

	uint64_t begin = UINT64_MAX;
	uint64_t end = 0;
	for (uint32_t level = range.FirstLevel; level < MipCount; level++)
	{
		begin = std::min(begin, Levels[level].Offset);
		end = std::max(end, Levels[level].Offset + Levels[level].Size);
	}
	range.Offset = begin;
	range.Size = end - begin;
	range.LevelCount = MipCount - range.FirstLevel;
	return range;
}
```

1. **Lines 235–244:** the first level that fits the limit; `MipCount` means none does.
2. **Lines 246–254:** the range spans from the smallest offset to the largest end of the tail's levels. With the smallest level first, this is one run of bytes.

Only version 2 of the cooked form can change levels later (`Texture::CanChangeLevels` checks it), because only version 2 stores the smallest level first. The first-load estimate that `SceneLoader` uses counts only the head while loads read prefixes (`EstimateFirstLoadBytes`).

:::example[A 2048 texture on first load]
Take a 2048 by 2048 texture with 12 levels. Level 6 is 32 by 32, so the tail holds levels 6 to 11, which is 32 texels, 16, 8, 4, 2 and 1 on a side. With one byte per texel the tail is about 1.4 KB, far less than the 64 KiB head, so the head read already holds it. The texture is ready after one small read, and the surface is drawn at 32 by 32 texels until views ask for more.
:::

### Views report what they drew

After each frame it renders, a `SceneRenderer` has a list of `VisibleTextureUse` records, one per loaded texture of a drawn material. A record holds the texture's handle, its larger side in texels, its level count, its material's pixel size on screen, its largest tiling and its `UVPixels`. [Asset requests](../draw/asset-requests.md) says how the frame collects them.

A frame drawn through the GPU-driven path takes the measure from :term[visibility feedback]{id=visibility-feedback}. `Strata/shaders/Include/TextureStreaming.slang` ports `GetWorldPixels` and `GetUVPixels`, so that the graphics card computes the same numbers as the :term[central processing unit]{id=processor} (CPU). Its comment says to keep the two in sync.

The renderer then calls `ReportView` once per view.

```cpp src="Strata/src/Strata/Renderer/TextureStreamer.cpp#L222-L232"
void TextureStreamer::ReportView(const TextureStreamingView& view, std::span<const VisibleTextureUse> textures)
{
	// The renderer resolved the textures for the frame: nothing is looked up in the manager (a frame draws up to tens of
	// thousands of materials, most of them often without textures, which the renderer leaves out).
	const float viewportHeight = std::max(view.ViewportHeight, 1.0f);
	for (const VisibleTextureUse& use : textures)
	{
		const uint32_t level = view.Streaming ? TextureStreamingPolicy::ComputeWantedLevel(use.Size, use.MipCount, use.UVScale, use.UVPixels) : 0;
		m_Policy.AddNeed(use.Texture, level, use.PixelSize / viewportHeight, view.CameraCut, !view.Streaming);
	}
}
```

1. **Line 226:** the viewport height turns a size in pixels into a coverage, a fraction of the view.
2. **Line 229:** a view that streams asks for the wanted level; a view that does not asks for level 0.
3. **Line 230:** the need is recorded with its coverage, whether the view jumped and whether it needs the texture whole.

Several uses and several views combine: `AddNeed` keeps the finest level, the largest coverage, any camera cut and any whole need.

### From density to a wanted level

The wanted level is the level whose texels are each about one pixel. Level $L$ has texels $2^L$ times larger than level 0, so the right level is the :term[base 2]{id=binary} :term[logarithm]{id=logarithm} of the ratio of texels to pixels, rounded down.

$$L = \lfloor \log_2 ( s \cdot t / p ) \rfloor$$

Here $L$ is the wanted level, $s$ the texture's larger side in texels, $t$ how many times the material tiles the coordinates, and $p$ the pixels one unit of the coordinates spans (the `UVPixels`). The brackets round down. The product $s \cdot t$ is the texels that one unit of the texture holds on screen.

```cpp src="Strata/src/Strata/Renderer/TextureStreamer.cpp#L28-L41"
uint32_t TextureStreamingPolicy::ComputeWantedLevel(uint32_t size, uint32_t mipCount, float uvScale, float pixels)
{
	if (mipCount == 0)
		return 0;
	const uint32_t coarsest = mipCount - 1;
	const float texels = static_cast<float>(size) * std::max(std::isfinite(uvScale) ? uvScale : 1.0f, 0.0f);
	// Drawn no larger than a pixel (or not at all): the coarsest level is all it shows.
	if (!(pixels > 1.0f) || !std::isfinite(pixels))
		return coarsest;
	if (!(texels > pixels))
		return 0;
	const float level = std::floor(std::log2(texels / pixels));
	return static_cast<uint32_t>(std::min(level, static_cast<float>(coarsest)));
}
```

1. **Line 33:** the texels spanned by a unit: the larger side times the tiling, where a bad tiling counts as 1 and a negative one as 0.
2. **Lines 35–36:** a unit drawn no larger than one pixel, or an invalid pixel count, wants the coarsest level.
3. **Lines 37–38:** a unit drawn with as many pixels as it has texels, or more, wants level 0.
4. **Line 39:** the formula.
5. **Line 40:** the result never exceeds the coarsest level the texture has.

:::example[Wanted levels by hand]
Take the 2048 texture of 12 levels, drawn so that one unit spans 2048 pixels and tiled once. It has 2048 texels over 2048 pixels, a ratio of 1, and the logarithm is 0: level 0. At 128 pixels the ratio is 16, the logarithm 4, so level 4.

Tile it four times, still at 128 pixels: $2048 \cdot 4 = 8192$ texels over 128 pixels is 64, and the logarithm of 64 is 6, so level 6. Tiled four times at 2048 pixels the ratio is 4 and the level 2. `TextureStreamerTests.cpp` checks these values. At the limits, a size of 1 pixel or less gives level 11, and a tiling of 0 gives level 0.
:::

How does the renderer get $p$? The policy measures the world first. `GetViewScale` turns the camera into the pixels one world unit spans at distance 1: the viewport height over twice the tangent of half the vertical :term[field of view]{id=field-of-view}. `GetWorldPixels` divides that by the distance to the nearest point of the mesh's bounds, but never by less than the :term[near plane]{id=near-plane}.

Then `GetUVPixels` turns world pixels into texture pixels, using the mesh's :term[texture coordinates]{id=texture-coordinates} per world unit along each axis and the instance's scale. Where faces look along different axes, the sparsest coordinates decide, since those spread each texel over the most pixels. A surface whose coordinates do not change gets the largest float. That asks for level 0, because the surface has no derivatives to read.

### Ranking the reads

When a texture sits below its wanted level, the streamer asks the manager for the missing bytes with a score. `RankRaise` gives the rank, and `IsCameraCut` decides whether a view jumped.

```cpp src="Strata/src/Strata/Renderer/TextureStreamer.cpp#L82-L93"
TextureStreamingPolicy::Rank TextureStreamingPolicy::RankRaise(uint32_t missingLevels, float coverage, bool cameraCut)
{
	Rank rank;
	rank.Priority = cameraCut ? AssetPriority::Normal : AssetPriority::Low;
	rank.Score = static_cast<float>(missingLevels) * std::clamp(std::isfinite(coverage) ? coverage : 0.0f, 0.0f, 1.0f);
	return rank;
}

bool TextureStreamingPolicy::IsCameraCut(const glm::vec3& previousPosition, const glm::vec3& previousForward, const glm::vec3& position, const glm::vec3& forward)
{
	return glm::distance(position, previousPosition) > c_CameraCutDistance || glm::dot(forward, previousForward) < c_CameraCutCosine;
}
```

1. **Line 85:** a normal read has priority Low, behind the loads of whole assets; a camera cut's read has Normal.
2. **Line 86:** the score is missing levels times coverage, with the coverage kept between 0 and 1.
3. **Line 92:** a jump is a move of more than `c_CameraCutDistance` (10 world units) or a turn of more than 45 degrees, where the :term[cosine]{id=cosine} of the angle falls below 0.7071.

:::example[Which read goes first]
`TextureStreamerTests.cpp` queues four reads: one missing level at coverage 0.05, one at 0.5, four levels at 0.05 and four levels at 0.5. Their scores are 0.05, 0.5, 0.2 and 2.0. The queue serves them from the highest: 2.0, 0.5, 0.2, then 0.05. A fifth read from a camera cut with one level at coverage 0.01 scores only 0.01, but its priority is Normal, so it goes before all four.
:::

A queued read rises with its texture's rank: if a view needs the texture more later, the streamer raises the read's score and does not queue it twice. The first frame of a renderer counts as a cut, since it has no previous camera (`SceneRenderer::IsCameraCut`).

### Views that need every level

A view can switch streaming off with `SceneRendererSpecification::TextureStreaming`, and the probe bake's `ForBake` does. Such a view reports level 0 and marks the need as whole. The frame's extraction then counts every texture that is not yet at level 0 as pending (`CountPending`), so a bake or an exact-pixel test knows to wait.

The whole mark also protects the levels from memory pressure. The streamer raises a whole texture without a fade, because the image should not show a half-finished state. `Hold` keeps a texture whole for as long as its owner keeps the hold. `RequestLevel` asks for one level of one texture in the current frame.

### Raising a texture

The streamer asks the manager for a range read of the missing levels and polls it in `OnUpdate`. When the data arrives, `OnUpdate` checks that the texture still has the resident level it had when the read began, then raises the texture as far as it is still wanted.

```cpp src="Strata/src/Strata/Renderer/TextureStreamer.cpp#L517-L550"
if (streamed.Read != 0 && !streamed.Changing)
{
	std::vector<uint8_t> data;
	std::string error;
	const AssetRangeStatus status = m_Manager.PollRange(streamed.Read, data, &error);
	if (status != AssetRangeStatus::Pending)
		streamed.Read = 0;
	if (status == AssetRangeStatus::Complete)
	{
		streamedBytes += data.size();
		// Raised as far as it is still wanted (a prefix of what was read: the finer levels come last), once its
		// resident levels are what they were when it was read.
		const TextureStreamingPolicy::Target* target = m_Policy.Find(handle);
		const uint32_t wanted = target ? std::max(target->Level == TextureStreamingPolicy::c_NoLevel ? streamed.ReadResident : target->Level, streamed.ReadLevel)
			: streamed.ReadResident;
		if (texture->GetResidentLevel() == streamed.ReadResident && wanted < streamed.ReadResident && texture->CanChangeLevels())
		{
			const CookedTextureByteRange range = texture->GetCookedLayout().GetLevelsByteRange(wanted, streamed.ReadResident);
			if (range.Size <= data.size())
			{
				data.resize(static_cast<size_t>(range.Size));
				// A view that needs the texture whole (exact pixels) sees its finest levels at once; the others fade them in.
				if (texture->RaiseLevels(wanted, std::move(data), !(target && target->Whole)))
				{
					streamed.Changing = true;
					streamed.ChangeForBudget = false;
					streamed.ChangeFrom = streamed.ReadResident;
					m_Manager.UpdateMemoryUsage(handle, *texture);
					if (upload)
						ContinueChange(handle, *texture, streamed, context);
				}
			}
		}
	}
```

1. **Line 521:** the streamer polls the read every frame; it never waits for it.
2. **Lines 522–523:** a read that is no longer pending is forgotten, whether it completed or failed.
3. **Lines 530–531:** the texture is raised only as far as it is still wanted, never past the levels read.
4. **Line 532:** the texture must still have the resident level it had when the read began.
5. **Lines 539–546:** the raise gets no fade for a whole need, then memory accounting follows and the change continues at once.

Then the texture takes over.

```cpp src="Strata/src/Strata/Renderer/Texture.cpp#L738-L753"
bool Texture::RaiseLevels(uint32_t firstLevel, std::vector<uint8_t> data, bool fadeIn)
{
	const uint32_t resident = GetResidentLevel();
	if (!CanChangeLevels() || firstLevel >= resident || firstLevel >= m_MipCount)
		return false;
	const CookedTextureByteRange range = m_CookedLayout.GetLevelsByteRange(firstLevel, resident);
	if (range.Size != data.size())
		return false;
	m_LevelChange = std::make_unique<LevelChange>();
	m_LevelChange->FirstLevel = firstLevel;
	m_LevelChange->Position = UploadPosition { firstLevel, resident - firstLevel, 0 };
	m_LevelChange->Data = std::move(data);
	m_LevelChange->DataOffset = range.Offset;
	m_LevelChange->FadeIn = fadeIn;
	return true;
}
```

1. **Line 741:** only a texture made from cooked data of version 2, with a GPU texture and a slot, and no change or first upload under way, can change levels.
2. **Lines 743–745:** the bytes must match the layout's range for those levels exactly, or the raise is refused.
3. **Lines 746–751:** the call only records the change: the new first level, the data and whether to fade in. The work runs in steps.

`ContinueLevelChange` does the work within the frame's upload budgets. It makes a new GPU texture with the finer levels. It copies the resident levels from the old texture on the GPU, uploads the new levels from the read's bytes and swaps in a new bindless slot. When the change ends, the table entry follows the new slot. `UpdateMemoryUsage` tells the manager that the texture grew, without replacing the asset.

### Making room

A raise adds bytes to the GPU texture pool. The streamer sums the room left, less what reads under way will add, and gives it to the textures below their level in rank order. When the next texture does not fit, `MakeRoom` takes the finest levels from textures needed less, least needed first. A texture never takes from one needed as much or more, so two textures never take levels from each other in turns. When nothing is left to take, the texture gets the finest level the room holds.

### Dropping and forgetting

Dropping is the reverse: a new, smaller GPU texture, a copy on the GPU of the levels that stay, and a new slot. The policy lowers a target only after the finer level was not needed for 30 s (`c_IdleDropSeconds`, changed with `SetIdleDropSeconds`). Under pressure on the texture budget, `ReleaseMemory` lets the least needed textures lose their finest levels at once, as many as the budget takes, before the manager removes any whole asset. Three limits keep this orderly:

- At most 8 textures drop levels per frame (`c_MaxDropsPerFrame`), since each drop is a copy on the GPU.
- A texture nobody needed for twice the idle time, 60 s, is forgotten. Its tail stays.
- A failed range read is tried again 60 frames later at the earliest (`c_RetryFrames`).

### Fades and slots

When levels are raised, `TextureTable` gives the texture's entry a minimum :term[level of detail]{id=level-of-detail} that starts at the level the texture showed before and falls to its finest over `c_FadeInSeconds`, which is 0.25 s. The material function `SampleMaterialTexture` scales the sampling gradients to that minimum, which keeps the filtering of slanted surfaces working. A renderer disables the fade with `SceneRendererSpecification::FadeTextureLevels`; captures, thumbnails and the probe bake do. A test either does the same or waits until `TextureTable::GetFadeCount()` is 0 before it compares pixels.

```pseudocode
// wrong: the slot names the GPU texture of one moment
slot = texture.GetBindlessSlot()     // stored in a draw record
// ... levels stream in, the texture is replaced ...
draw(slot)                           // names a texture that is gone

// right: material data holds the stable table index
entryIndex = texture.GetTableIndex()
// the table entry follows the slot; the frame uploads the changed entries
```

The :term[pseudocode]{id=pseudocode} shows the mistake of a cached slot. Material data stores the table index, which stays the same for the texture's life (`Texture::GetTableIndex`), and the table's entry follows the bindless slot as levels stream. Code that needs the slot itself calls `Texture::GetBindlessSlot` in every frame.

### The switch, and what is not here

`AssetManagerBase::SetPartialLoads(false)` makes every load read the whole stored form, for tests and baselines; it affects loads requested afterwards. Strata does not stream meshes, including levels of detail of meshes: only textures load in parts. The only prefix registration in the pin is the texture one (`RendererRegistration.cpp`). It also has no virtual texturing and no sparse residency.

### Seeing it: the mip debug view

The editor's **Mip** debug view tints each entity by how many levels its worst texture lacks. Green means the levels the views need are resident; blue, amber and red mean one, two, and three or more levels short (or a texture still loading). The command `viewport.setSettings` selects it with the debug view `mip`.

Fly through the Showcase and many surfaces turn blue, amber or red, as the camera asks for detail that has yet to arrive. Stop, and after a few seconds the surfaces turn green, as in this view of the Showcase after the camera stopped:

::figure{id=mip-view-settled}

A first load starts at the other end of the chain. The texture holds only its tail, and the surface stays coarse until a view asks for more levels.

::figure{id=tail-levels}

A raise ends in the fade. The finest level sampled falls from the level shown before to the new one, a little in each frame.

::figure{id=fade-in-lod}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Whole-texture residency by recency | Simple texture caches | No per-pixel measure and no level changes | Memory for detail nobody sees; whole reads after each eviction |
| Virtual texturing with sparse tiles | id Tech 5, Unreal Engine's virtual textures | Memory in proportion to the visible tiles, even for one huge texture | Sampling through a page table, tile-edge filtering and sparse support in every driver |
| Sampler feedback | `DirectX 12` hardware | Requests that come from the hardware's own sampling, not from a model | A feature of `DirectX 12` hardware, while Strata renders through :term[Vulkan]{id=vulkan} |

## How it is tested

`TextureStreamerTests.cpp` runs the policy alone, with no GPU. It checks the wanted level and its limits, world pixels, density, camera cuts, combined needs, the idle drop over 2,000 frames, the drop order and the ranking of reads in a real streaming queue.

`GPUTextureStreamingTests.cpp` runs the whole loop on the shared device. One case streams a texture from its tail to level 0 and back on a tight budget. Others cover a tiled floor seen at a grazing angle, the fade-in, a texture taking levels from one needed less, and a renderer without streaming that waits for every level. `TextureTableTests.cpp` tests the fades. Run the first set with `StrataTests.exe --test-suite=Renderer*` after a build, and the GPU ones with `ctest --preset windows-debug -L gpu`.

Tests that compare pixels turn `FadeTextureLevels` off or wait for `GetFadeCount()` to reach 0, as rule 6 of the contract asks. `ProbeBakeTests.cpp` checks that `ForBake` turns fades off.

## Changing it safely

- A new input to the wanted level goes into `TextureStreamingPolicy` and, for the GPU path, into `TextureStreaming.slang`; the two are kept in sync.
- A new way to drop or raise levels stays inside `Texture::RaiseLevels` and `DropLevels`, so the slot swap stays in one place.
- Never read a slot from a stored value; never write material data with a bindless slot.
- Never wait for a read on the main thread. Use `PollRange`.
- A new limit goes next to the others in `TextureStreamer.h` with a test in `TextureStreamerTests.cpp`.
- Every change to this path runs the Renderer suites and the GPU streaming tests.

## Summary

- A texture's wanted level is the base 2 logarithm of texels over pixels, rounded down and limited to its levels.
- Reads rank by missing levels times coverage; a camera cut's reads rank before the others.
- A raise reads a range, makes a new GPU texture, copies, uploads, swaps the bindless slot and fades in.
- Never cache a slot; resolve it every frame, and let pixel tests wait for the fades.

## Check yourself

1. A 1024 texture with 11 levels, tiled twice, is drawn so that one unit spans 64 pixels. Which level does it want?

   :::answer{tests="wanted-level"}
   The texture holds 1024 times 2 texels per unit: 2048. Divide by 64 pixels: 32. The base 2 logarithm of 32 is 5. The texture has 11 levels, so level 5 is allowed. The answer is level 5.
   :::

2. Four reads have scores: A, 2 missing levels at coverage 0.5; B, 1 level at 0.9; C, 3 levels at 0.2; D, 1 level at 0.01 from a camera cut. In which order are they served?

   :::answer{tests="read-ranking"}
   The scores are 1.0, 0.9, 0.6 and 0.01. D comes first, because a camera cut has priority Normal and the others Low. The rest follow by score: A, B, C. The order is D, A, B, C.
   :::

3. A programmer stores `texture->GetBindlessSlot()` in a draw record at load time. Why is this wrong?
   - a) The slot is a pointer and may be null.
   - b) A raise or drop gives the texture a new slot, so the stored value names a GPU texture that may be replaced.
   - c) Slots are valid only on the main thread.

   :::answer{tests="slot-rule"}
   Option b is right. Option a is wrong: the slot is an index and the function is not about null. Option c is wrong too: a slot has nothing to do with the thread. The stored slot ages the moment the streamer changes the texture's levels.
   :::

4. A test compares the pixels of a floor texture right after the camera moved, and the result changes from run to run. What is the likely cause, and how do you fix it?

   :::answer{tests="slot-rule"}
   Levels were raised after the move, and the fade-in was still running, so the texture showed a half-raised state. Disable `FadeTextureLevels` for the renderer, or wait until `TextureTable::GetFadeCount()` is 0 before comparing pixels.
   :::

5. Put the events of a raise in order. They are: a new bindless slot, the view's report, a completed poll of the read, the change recorded by `Texture::RaiseLevels`, and the range read's request.

:::answer{tests="raise-flow"}
The order is: the view reports the texture, the streamer requests a range read, `PollRange` says the read is complete, `Texture::RaiseLevels` records the change, and the change finishes with a new bindless slot.
:::

## Exercises

1. **Basic.** A 2048 texture with 12 levels is tiled four times and one unit spans 512 pixels. Compute its wanted level by hand. Then say which level it wants if the camera comes twice as close.

   :::answer[Worked solution]{tests="wanted-level"}
   The texels per unit are 2048 times 4: 8192. Divide by 512 pixels: 16. The base 2 logarithm is 4, so level 4. Twice as close doubles the pixels to 1024, the ratio becomes 8 and the level 3.
   :::

2. **Medium.** Using one byte per texel, how many bytes does a range read hold when a 2048 texture rises from the tail, level 6, to level 2? Write a sketch that sums the levels and check it.

   :::answer[Worked solution]{tests="raise-flow" solution="sketches/draw-mip-streaming-bytes.cpp"}
   Levels 2 to 5 are read: 512 squared, 256 squared, 128 squared and 64 squared texels. The sketch sums them.

   ```cpp sketch="draw-mip-streaming-bytes.cpp"
   #include <cstdint>
   #include <cstdio>

   int main()
   {
   	// One byte per texel. A range read raises a 2048 texture from its tail (level 6) to level 2.
   	const uint32_t size = 2048;
   	const uint32_t firstLevel = 2;
   	const uint32_t tailLevel = 6;
   	uint64_t total = 0;
   	for (uint32_t level = firstLevel; level < tailLevel; level++)
   	{
   		const uint64_t side = size >> level;
   		std::printf("level %u: %llu bytes\n", level, static_cast<unsigned long long>(side * side));
   		total += side * side;
   	}
   	std::printf("read: %llu bytes\n", static_cast<unsigned long long>(total));
   	return 0;
   }
   ```

   ```text output-of="draw-mip-streaming-bytes.cpp"
   level 2: 262144 bytes
   level 3: 65536 bytes
   level 4: 16384 bytes
   level 5: 4096 bytes
   read: 348160 bytes
   ```

   1. **Line 11:** the loop visits the levels from the wanted one up to, but not including, the tail's first.
   2. **Line 13:** each level halves its side, so a right shift by the level gives it.
   3. **Line 15:** the read holds the levels in one run, so the total is their sum.

   The result is 348,160 bytes, which is a read of about 340 KB.
   :::

3. **Hard.** Trace it yourself: with a debugger, follow a Showcase texture as the camera nears it. Name the functions from the report of the view to the frame where its bindless slot changes, and the levels before and after.

:::answer[Worked solution]{tests="raise-flow"}
The path starts in `TextureStreamer::ReportView` in `Strata/src/Strata/Renderer/TextureStreamer.cpp`, which records the wanted level and the need. `OnUpdate` in the same file requests the range read and later polls it with `PollRange`. When the read completes, it calls `Texture::RaiseLevels` in `Strata/src/Strata/Renderer/Texture.cpp`, which records the change. `TextureStreamer::ContinueChange` calls `Texture::ContinueLevelChange`, which ends in `Texture::SwapResidentTexture`: the slot changes there, in the frame the change ends, and `Texture::GetBindlessSlot` then returns the new value. The levels before are the resident level the read was made from; after, the wanted level.
:::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/TextureStreamer.h`, `TextureStreamer.cpp`: the policy and the streamer.
- `Strata/src/Strata/Renderer/Texture.cpp`: `RaiseLevels`, `DropLevels`.
- `Strata/src/Strata/Renderer/TextureTable.h`: the fade and `GetFadeCount`.
- `Strata/src/Strata/Asset/AssetManager.cpp`: `ReadPrefix`, range reads, `SetPartialLoads`.
- `Strata/shaders/Include/TextureStreaming.slang`: the GPU's measure.
- `StrataTests/src/Renderer/TextureStreamerTests.cpp`, `GPUTextureStreamingTests.cpp`.
- The command `viewport.setSettings` with the debug view `mip`.

## Further reading

- "Texture streaming" in the Unreal Engine documentation: how Unreal picks mip levels from screen size and a memory pool (intermediate).
- "Mipmap Streaming" in the Unity manual: how Unity budgets and requests levels (intermediate).
- "Sparse Virtual Textures" by Sean Barrett, a talk: the tile-based alternative (advanced).
- "Sampler Feedback" in the DirectX 12 specifications: the hardware feature behind feedback-driven streaming (advanced).
