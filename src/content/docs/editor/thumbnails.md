---
id: editor/thumbnails
title: "Thumbnails"
description: "How the editor makes small pictures of assets and of whole projects, keeps them on disk by content, and never stalls a frame to read them."
kind: internals
size: M
tracks: [E]
needs: [editor/projects, gpu/frame-tour, gpu/readback-timing, assets/residency]
time: 60
learn:
  - id: choose-key
    text: explain what the thumbnail key hashes and why each part of it is there
  - id: compute-reads
    text: compute how many bytes a texture thumbnail reads against the whole texture
  - id: never-stall
    text: explain how one render at a time and a polled readback keep frames short
  - id: bump-version
    text: choose which changes need a new `ThumbnailCache::c_Version`
  - id: trace-flow
    text: trace a saved material edit from the changed file to the new picture
since: 0.3.0
status: final
---

Open a project with five hundred assets and the Content Browser shows each one as a small picture: a sphere for a material, a framed model, a shrunk texture. Strata makes those pictures in the background, keeps them in a folder of the project, and draws them again at the next start without rendering anything. The part that does this is `ThumbnailCache`, with two smaller helpers: `DisplayImage` puts the pixels on the :term[graphics processing unit]{id=gpu} (GPU), and `ProjectThumbnail` makes the one picture the launcher shows for the whole project. This page does not cover how the Content Browser lays its tiles out, how the :term[content stamp]{id=content-stamp} is built, or how the preview light looks.

## The problem and how engines solve it

A picture of a material is not a file you can shrink: nobody stored one. The editor has to draw the material on a sphere with the real renderer, and that takes GPU time and a frame of waiting. Five hundred assets at one picture per frame would take about 8 seconds at 60 :term[frames per second]{id=frame-rate}, even when nothing else runs. Rendering them all again at every start would repeat that work for pictures that did not change.

One answer is to render every picture at start, which makes a slow start that grows with the project. Another is to render each picture when it is first shown and keep it in memory, but exit loses the memory and the cost comes back at the next start.

The third answer keeps the pictures on disk, and then a new question appears: when is a stored picture still right? A file name or a modified time is a weak answer. A material can look different because a texture it uses changed, although the material's own file did not. A cache of derived data on disk therefore stores a record of what the picture was made from, and compares the record before it uses the picture again. Strata keeps one number per picture, a **key**.

A key is a :term[hash]{id=hash} of everything that decides how the picture looks. If any input changes, the key changes, and the stored picture is stale. The cost of this choice is that the key must name every input. An input the key misses gives a picture that looks wrong and is never refreshed. An input the key names without need only costs an extra render.

The last question is how to read the finished picture back from the GPU. The :term[central processing unit]{id=processor} (CPU) needs the pixels to write a file, and asking for them at once would stop the frame until the GPU finishes. Strata polls a readback once per frame instead, as [Readback without stalls](../gpu/readback-timing.md) describes.

A **thumbnail cache** is the part of the editor that makes small pictures of assets and keeps them on disk under a key of the assets' content. It hands the editor's user interface (UI) a texture to draw. Strata's cache has two lifetimes: pictures live in memory while they are shown, and as files between sessions.

## The map

The cache runs on the :term[main thread]{id=main-thread}, and its jobs run elsewhere. The editor calls `Request` for each tile it draws, and `Update` once per frame moves the work along.

```mermaid caption="Where a thumbnail request goes: the cache either reads a file, decodes a texture on a worker thread, or renders a scene on the main thread, and the UI draws the uploaded result." alt="A flow from the Content Browser's request to a queue. The queue leads to three paths: reading a stored picture, decoding a texture's mip tail on an input and output thread, and rendering one scene at a time. All three end in an upload to the GPU, which the browser draws."
flowchart LR
  UI["Content Browser: Request every frame"] --> Q["ThumbnailCache queue"]
  Q -->|"key matches a file"| Disk["read the PNG file"]
  Q -->|"texture"| Tex["read mip tail by byte range, decode"]
  Q -->|"material, mesh, model, prefab"| Scene["SceneRenderer, one scene at a time"]
  Scene --> RB["TextureReadback, polled"]
  Disk --> Up["Upload: DisplayImage"]
  Tex --> Up
  RB --> Up
  Up --> UI
  RB -.->|"PNG written on an input and output job"| Files[".strata/Thumbnails"]
  Tex -.-> Files
```

`ThumbnailCache` owns the entries, the queue and the one running scene job. The :term[asset manager]{id=asset-manager} owns the :term[stored forms]{id=stored-form} of assets and the content stamps, `SceneRenderer` draws, `TextureReadback` brings the pixels back, and `DisplayImage` makes the texture.

`ProjectThumbnail` is separate: the editor's context asks it after every scene save, and it uses no queue, file or key of the cache.

## The contract

Callers of the cache may assume the following, and must do their part.

- **Ask every frame, for what is on screen.** `Request(handle)` returns a texture or null, and it also asks for the picture. An entry that nobody asks for during 3 frames leaves the queue, and one idle for 600 frames may be forgotten. The reason is that the cache never knows what the UI shows, so the request is the only signal.
- **Null means draw the type's icon.** A picture is null while it is pending, and also for assets that get none: a type without pictures, a :term[built-in asset]{id=built-in-asset}, a failed import, or an editor without a GPU. The caller never waits.
- **Pictures are drawn as they are.** A thumbnail is a texture of display colors with 8 bits for each of red, green, blue and alpha (RGBA8), at most 128 pixels on a side. The picture was tone mapped and encoded when it was made, so the UI draws it as it is.
- **One scene renders at a time.** The reason is the renderer's targets and the :term[frame time]{id=frame-time}: a second render would double both.
- **The key decides.** A picture is made again only when its key changed. A load, which also counts as a content change, never makes one again.

:::rule
Bump `ThumbnailCache::c_Version` when thumbnails would look different. The key sees content stamps and the version, not the renderer. A change in how pictures are drawn stays invisible unless the version moves, and every project then keeps the old appearance for assets that never change. Section [Changing it safely](#changing-it-safely) lists what counts.
:::

The key hashes the [content stamp](../assets/importing.md) of the asset and of everything it depends on. A content stamp is a fingerprint of an asset's stored form that lasts across sessions; this page uses it as a black box.

## A toy version

The toy keeps the idea and drops everything else: no GPU, no threads, one level of dependencies. Assets have a stamp and a list of what they depend on. The cache hashes a version and the stamps into a key, compares it with the key it stored for the name, and "renders" when they differ.

```cpp sketch="editor-thumbnails-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <map>
#include <string>
#include <utility>
#include <vector>

namespace Toy
{

	// The same hash Strata uses for its keys: FNV-1a over the bytes of a text, continued from a seed.
	uint64_t Fnv1a(const std::string& text, uint64_t seed = 14695981039346656037ull)
	{
		uint64_t hash = seed;
		for (char character : text)
		{
			hash ^= static_cast<uint8_t>(character);
			hash *= 1099511628211ull;
		}
		return hash;
	}

	struct Asset
	{
		uint64_t Stamp = 0;                  // Changes when the file or its import settings change
		std::vector<std::string> DependsOn;  // One level of dependencies is enough for the toy
	};

	class ThumbnailCache
	{
	public:
		ThumbnailCache(uint32_t version, std::map<std::string, uint64_t> index)
			: m_Version(version), m_Index(std::move(index)) {}

		void Request(const std::map<std::string, Asset>& assets, const std::string& name)
		{
			const uint64_t key = ComputeKey(assets, name);
			auto found = m_Index.find(name);
			if (found != m_Index.end() && found->second == key)
			{
				std::printf("%s: read from its file\n", name.c_str());
				return;
			}
			std::printf("%s: rendered again\n", name.c_str());
			m_Index[name] = key;
		}

		const std::map<std::string, uint64_t>& GetIndex() const { return m_Index; }

	private:
		uint64_t ComputeKey(const std::map<std::string, Asset>& assets, const std::string& name) const
		{
			uint64_t key = Fnv1a("Thumbnail " + std::to_string(m_Version));
			const Asset& asset = assets.at(name);
			key = Fnv1a(name + ":" + std::to_string(asset.Stamp) + ";", key);
			for (const std::string& source : asset.DependsOn)
				key = Fnv1a(source + ":" + std::to_string(assets.at(source).Stamp) + ";", key);
			return key;
		}

		uint32_t m_Version;
		std::map<std::string, uint64_t> m_Index;
	};

}

int main()
{
	std::map<std::string, Toy::Asset> assets;
	assets["Rust.png"] = { 100, {} };
	assets["Rusty.stmat"] = { 200, { "Rust.png" } };

	Toy::ThumbnailCache first(1, {});
	std::printf("First session\n");
	first.Request(assets, "Rusty.stmat");
	first.Request(assets, "Rusty.stmat");

	std::printf("The texture changes\n");
	assets["Rust.png"].Stamp = 101;
	first.Request(assets, "Rusty.stmat");

	std::printf("Next session, same version\n");
	Toy::ThumbnailCache second(1, first.GetIndex());
	second.Request(assets, "Rusty.stmat");

	std::printf("Next session, version bumped\n");
	Toy::ThumbnailCache third(2, second.GetIndex());
	third.Request(assets, "Rusty.stmat");
	return 0;
}
```

```text output-of="editor-thumbnails-toy.cpp"
First session
Rusty.stmat: rendered again
Rusty.stmat: read from its file
The texture changes
Rusty.stmat: rendered again
Next session, same version
Rusty.stmat: read from its file
Next session, version bumped
Rusty.stmat: rendered again
```

1. **Lines 12–21:** the hash folds the :term[bytes]{id=byte} of a text into one number, as Strata's key does.
2. **Lines 35–46:** `Request` compares the new key with the stored one and renders only when they differ.
3. **Lines 51–59:** the key starts from the version, then adds the stamp of the asset and of each source.

The first request renders, because the index is empty, and the second reads the file. A new stamp on the texture changes the material's key, so the material renders again although its own file did not change. A session with another version hashes another text, so every key differs.

## The real code

The real code follows the data. A request becomes a key, a key picks a path (file, texture job or scene job), and the result becomes a texture.

### The key

`ComputeKey` turns an asset into one number. Look at what enters the hashed text: the version, the image size, and the handle and stamp of every source.

```cpp src="StrataEditor/src/Editor/ThumbnailCache.cpp#L1127-L1134" symbol="ThumbnailCache::ComputeKey"
uint64_t ThumbnailCache::ComputeKey(AssetHandle handle, std::vector<AssetHandle>& outSources) const
{
	outSources = m_Assets->GetDependencyClosure(handle);
	uint64_t key = Hash::FNV1a(fmt::format("Thumbnail {} {}", c_Version, c_Size));
	for (AssetHandle source : outSources)
		key = Hash::FNV1a(fmt::format("{}:{:016X};", source.ToString(), m_Assets->GetContentStamp(source)), key);
	return key != 0 ? key : 1;
}
```

`ComputeKey` has the toy's shape with three differences. The sources are the whole dependency closure of the asset, not one level, so a texture two steps away still counts. The seed text holds the image size `c_Size` (128) as well as the version, so a change of the size would change every key without a bump. A key of zero means "no key" in the entries, so the function never returns it.

Each source adds its handle and its stamp in :term[hexadecimal]{id=hexadecimal}, with a `;` after each, to the running hash. The stamp is 0 for :term[built-in assets]{id=built-in-asset}, so a material drawn on the built-in sphere depends on the sphere only through the version.

The files are named by the asset's handle, not by the key, with a PNG extension, in `<project>/.strata/Thumbnails`. An index file next to them records, for each handle, the key its picture was made under, and a version field that must equal `c_Version`. A reader of the folder therefore finds one file per asset, replaced when the key changes. When the index's version differs, the index is read as empty, and every picture is made again.

### From a change to a new picture

The cache learns of changes without checking every asset every frame. Each entry lists its sources, and a reverse map from a source to the entries that show it lets `WatchSources` find the affected entries when the asset manager reports changed content.

```cpp src="StrataEditor/src/Editor/ThumbnailCache.cpp#L526-L533" from="if (entry.DirtySince != 0 && !entry.Queued" to="m_Queue.push_back(handle);" symbol="ThumbnailCache::StartQueued"
if (entry.DirtySince != 0 && !entry.Queued && !entry.Working && m_Frame - entry.DirtySince >= m_Specification.SettleFrames
	&& m_Frame - entry.LastRequest <= m_Specification.RequestFrames)
{
	// DirtySince stays until the work starts: an entry that leaves the screen first is made again when it is back.
	entry.Queued = true;
	if (entry.State != ThumbnailState::Ready)
		entry.State = ThumbnailState::Pending;
	m_Queue.push_back(handle);
```

`WatchSources` computes the key again of only those entries and sets `DirtySince` when it differs. The code above runs in `StartQueued` and queues an entry once its sources stayed unchanged for `SettleFrames` (20) frames and the entry was asked for in the last 3 frames. The old picture shows meanwhile. A burst of saves therefore renders once, and a tile that scrolled away renders only when it comes back.

### Textures: the mip tail by byte range

A texture's picture needs a small level, never the large one. A cooked texture stores its levels smallest first, right after a :term[header]{id=header}, so the small levels are the first :term[bytes]{id=byte} of the stored form. `StartTextureJob` runs on the main thread and hands the reads and the decoding to an input and output job, whose code follows.

```cpp src="StrataEditor/src/Editor/ThumbnailCache.cpp#L652-L669" from="else if (read(0, std::min(storedSize, c_TextureHeaderBytes), data))" to="view = ParseCookedTexture(data, &result.Error);" symbol="ThumbnailCache::StartTextureJob"
else if (read(0, std::min(storedSize, c_TextureHeaderBytes), data))
{
	std::optional<uint64_t> end;
	for (uint32_t dimension = c_Size; !end && dimension <= c_MaxCookedTextureSize; dimension *= 2)
		end = GetCookedTexturePrefixSize(data, storedSize, dimension);
	if (end && *end > c_MaxTextureReadBytes)
	{
		result.Error = "The texture has no level small enough to read for a thumbnail";
	}
	else if (end)
	{
		if (*end <= data.size() || read(0, *end, data))
			view = ParseCookedTexturePrefix(std::span<const uint8_t>(data).first(static_cast<size_t>(*end)), storedSize, &result.Error);
	}
	else if (storedSize <= c_MaxTextureReadBytes)
	{
		if (read(0, storedSize, data))
			view = ParseCookedTexture(data, &result.Error);
```

1. **Lines 652–656:** the first read is the header, and the loop asks how many leading bytes hold levels of 128 pixels, then 256 and upward.
2. **Lines 657–665:** a prefix over 64 MiB is refused; otherwise a second read happens only when the first held too little.
3. **Lines 666–669:** a texture without such a prefix is read whole when it is small enough.

The job first reads 4,096 bytes, enough for the header and the table of levels. `GetCookedTexturePrefixSize` then tells how many leading bytes hold the levels that fit in 128 pixels, trying 128, 256 and upward. If the first read already holds them, no second read happens. An old cooked form with the large levels first, and a texture with no small level, are read whole, but never more than 64 MiB. Otherwise the job stops with an error and the tile shows the icon.

The decoded level becomes RGBA8: block-compressed levels are decoded, one channel shows as gray, normal maps get their Z rebuilt, and :term[high dynamic range]{id=high-dynamic-range} values are tone mapped.

A thumbnail follows the residency rule: it never loads the texture, as [Residency](../assets/residency.md) describes.

### Scenes: one render at a time

Materials, meshes, models and :term[prefabs]{id=prefab-world} have no stored picture, so the cache renders one. `Start` refuses a second scene job while one runs. It also waits while an import of the asset is pending, since that import would make the picture stale at once. `BuildScene` makes a scene of its own with only the asset in it. That is a sphere with the material, a mesh, or a model or prefab built in the scene, whose skinned characters stand in their rest pose.

`UpdateSceneJob` then runs once per frame and does a little each time, so no frame waits on it. It frames the asset's bounds from a fixed view, renders with a `SceneRenderer` of its own under the preview lighting, and waits until the picture is complete.

```cpp src="StrataEditor/src/Editor/ThumbnailCache.cpp#L871-L888" from="if (stats.PendingAssets > 0" to="job.Readback = TextureReadback::Create(m_Renderer->GetOutputTexture(), {}, &error);" symbol="ThumbnailCache::UpdateSceneJob"
if (stats.PendingAssets > 0 || stats.PendingTextGlyphs > 0 || stats.DeferredProxies > 0 || !loadingMeshes.empty()
	|| (job.Poses && job.Poses->HasWaitingRestPoses()))
{
	job.QuietFrames = 0;
	return;
}
// A texture counts as loaded with its mip tail; the levels this image needs stream in over the next frames.
if (job.MipWaitFrames < m_Specification.MaxMipWaitFrames && HasTexturesBelowWanted())
{
	job.MipWaitFrames++;
	m_Stats.MipWaitFrames++;
	job.QuietFrames = 0;
	return;
}
if (++job.QuietFrames < c_QuietFrames)
	return;
std::string error;
job.Readback = TextureReadback::Create(m_Renderer->GetOutputTexture(), {}, &error);
```

1. **Lines 871–876:** anything still loading or uploading restarts the count of quiet frames.
2. **Lines 877–884:** the job waits for finer texture levels, at most 120 frames, then draws what is resident.
3. **Lines 885–888:** after two quiet frames the copy starts, and nothing is read in that frame.

The wait has three parts: nothing pending on the GPU, the finer levels of the textures streamed in (at most 120 frames), and two quiet frames so that shadows and the environment settle. Only then does the job start a `TextureReadback`. The job never reads the pixels in the frame that started the copy.

```cpp src="StrataEditor/src/Editor/ThumbnailCache.cpp#L782-L799" from="if (job.Readback)" to="FinishScene(true, std::move(image));" symbol="ThumbnailCache::UpdateSceneJob"
if (job.Readback)
{
	if (!job.Readback->IsReady())
		return;
	ReadbackImage pixels;
	if (!job.Readback->GetResult(pixels) || pixels.BytesPerPixel != 4)
	{
		FinishScene(false, nullptr);
		return;
	}
	Ref<ThumbnailImage> image = CreateRef<ThumbnailImage>();
	image->Width = pixels.Width;
	image->Height = pixels.Height;
	image->Pixels = std::move(pixels.Pixels);
	// The sky fills the image: opaque.
	for (size_t pixel = 3; pixel < image->Pixels.size(); pixel += 4)
		image->Pixels[pixel] = 255;
	FinishScene(true, std::move(image));
```

1. **Lines 784–785:** the poll: until the copy is ready, the function returns and the frame continues.
2. **Lines 787–790:** a failed readback drops the picture, and the tile keeps its icon.
3. **Lines 796–799:** the alpha channel is forced to 255 before the picture is finished.

On the frames after, `IsReady` is polled and the function returns while it is false. The pixels arrive as a `ThumbnailImage`; the alpha channel is forced to 255, because the sky fills the picture. `FinishScene` then queues the upload and a job that encodes a PNG and writes it, and the index records the key once the file exists.

`Upload` makes at most 8 GPU textures per frame through `DisplayImage::Upload`, which creates an RGBA8 texture in the shader-resource state and writes the pixels through the open :term[command list]{id=command-list}. Those textures are not :term[sRGB]{id=srgb} views: the pixels are already display colors, so the UI draws them as they are.

### The project's picture

`ProjectThumbnail` follows the same pattern at a larger scale, with a longer list of things to wait for. After a scene save it renders the scene from its :term[primary camera]{id=primary-camera} with the viewport's capture renderer at 1,440 by 810 pixels, 3 times the 480 by 270 it writes. The size is that of a game window, so the game's text keeps its share of the picture. The render is averaged down by blocks of 3 by 3 pixels, which is an exact box filter, and written as `<project>/.strata/Thumbnail.png`.

```cpp src="StrataEditor/src/Editor/ProjectThumbnail.cpp#L169-L191" from="const bool incomplete = stats.PendingAssets > 0" to="m_Readback = TextureReadback::Create(renderer->GetOutputTexture(), {}, &error);" symbol="ProjectThumbnail::Update"
const bool incomplete = stats.PendingAssets > 0 || stats.PendingTextGlyphs > 0 || stats.Overlays.PendingGlyphs > 0 || stats.DeferredProxies > 0
	|| stats.LocalShadowViewsPending > 0 || stats.ReflectionProbesPending > 0 || renderer->CountTexturesBelowWanted() > 0;
const bool waiting = incomplete && ++m_Frames < c_MaxFrames;
const bool exposureWaiting = !stats.PreExposureSettled && ++m_ExposureFrames < c_MaxExposureFrames;
const bool giWaiting = !stats.GlobalIlluminationSettled && ++m_GIFrames < c_MaxGIFrames;
if (waiting || exposureWaiting || giWaiting)
{
	renderer->GetSceneRenderer().ResetHistory();
	return;
}
// Spatial screen-space reflections (Graphics Quality High and Ultra) read the previous frame's color, which the view's
// first frame and every frame after a reset lack: rendered again, keeping the history, for at most
// c_MaxReflectionFrames, as captures do. Without temporal anti-aliasing nothing else would render the view again.
if (stats.ScreenSpaceReflectionsPending && m_ReflectionFrames < c_MaxReflectionFrames)
{
	m_ReflectionFrames++;
	return;
}
const bool unsettled = stats.TemporalAntiAliasing && stats.TemporalFrames < c_TemporalSettleFrames;
if (unsettled && ++m_TemporalFrames < c_MaxTemporalFrames)
	return;
std::string error;
m_Readback = TextureReadback::Create(renderer->GetOutputTexture(), {}, &error);
```

1. **Lines 169–172:** each wait counts its frames, and stops waiting at its limit.
2. **Lines 174–178:** while waiting, the history is reset so that no frame of an incomplete view stays in it.
3. **Lines 182–186:** reflections that read a previous frame get one more rendered frame, at most twice.
4. **Lines 187–191:** temporal anti-aliasing settles its history, and then the copy starts.

The picture waits for what a still image needs, each wait with its own limit in frames. Loads and glyphs get 120 frames, the pre-exposure 8, global illumination 54, reflections that read a previous frame 2, and temporal anti-aliasing's history 16 more. Each limit exists because a wait must end: a texture budget can keep levels out for good.

Play mode cancels the request, since the saved scene is what the picture shows, and the next save asks again. A request that arrives while a picture is being made is made after it.

:::example
You edit the material `Rusty` and save it.

The material's closure is `Rusty` and its texture `Rust`. Its key text starts with `Thumbnail 11 128` and continues with the pair `<handle of Rusty>:<stamp>;` and the pair for `Rust`, each stamp a 16-digit hexadecimal number. Saving rewrites the file of `Rusty`, so its stamp changes, the text changes, and the key changes. The key of `Rust` and of every other material stays the same.

The asset manager reports the changed content. `WatchSources` finds the entries that show `Rusty` (its own tile, and the tile of a prefab that uses it), sees that their keys differ and marks them. Twenty frames pass without another save. `StartQueued` queues the tile, `Start` finds no file under the new key, and the scene job renders the sphere: a few frames of loading, two quiet frames, one readback. The old picture shows all that time.

The new texture replaces the old one and the file under the handle of `Rusty` is replaced. You restart the editor. The index holds the new key, `ComputeKey` gives the same number, and the tile appears from the file without a render. The statistics count one `LoadedFromDisk` instead of one `ScenesRendered`.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Render all pictures at start | Simple tools and small asset browsers | No stale state and no key | A start that grows with the project |
| Key by file name and modified time | :term[Operating system]{id=operating-system} file browsers | A cheap key | A material stays wrong when its texture changes |
| Render on the main frame without a job | Quick prototypes | Less code | A stalled frame at every picture |

## How it is tested

The tests live in `StrataTests/src/Editor/ThumbnailTests.cpp` (suite `Editor.Thumbnails`, no GPU) and `StrataTests/src/Editor/GPUThumbnailTests.cpp` (suite `GPU.Editor.Thumbnails`, label `gpu`).

The first suite checks texture thumbnails: the largest level that fits, block-compressed levels decoded, textures without a small level made smaller, and which :term[asset types]{id=asset-type} get a picture. The suite also checks that content stamps last across sessions and change with a source and its settings, and that the project's picture is averaged down exactly.

The second suite uses the shared GPU device and checks the behavior: pictures render from mip tails and small scenes, are kept on disk and are read back by the next session. A saved change of a material renders its picture again, once, and a failed import shows the icon. The Asset tab's preview renders at the size it covers. The project's picture waits for glyphs, exposure, history and global illumination.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Thumbnails
ctest --preset windows-debug -R Thumbnails
```

The first command runs the suite without a GPU, and the second runs both.

## Changing it safely

Extension points: a new kind of picture adds its type to `HasThumbnail` and a case to `BuildScene`. A different look changes the renderer's options or the preview lighting.

- Bump `ThumbnailCache::c_Version` for any change that makes an existing picture look different: scene drawing, the view, texture decoding or the preview light. The constant's comment lists the past bumps. A needless bump makes every user render everything again.
- Name every input of the look in the key or the version. The image size is hashed already; an option you add to the scene renderer is not.
- Keep the request path cheap: it runs for every visible tile every frame, and must not walk the scene or the asset folder.
- Never block on a load or on the GPU: scene jobs return and continue next frame.
- Leave rendering to the main thread. Jobs read, decode and encode; they never touch the cache, and the :term[destructor]{id=destructor} waits for reads under way, so the cache must go before the asset manager.
- Check with `Editor.Thumbnails` and `GPU.Editor.Thumbnails`, and add a regression test that fails without your change. A change to the project's picture needs a test scene for each of its waits.

## Summary

- The key hashes the version, the image size and, for the asset and everything it depends on, each handle with its content stamp, so any input change makes the picture again.
- A texture thumbnail reads a 4,096-byte header and the small mip levels by byte range; for a 4,096 pixel texture that is about a thousand times fewer bytes than the chain.
- One scene renders at a time, in steps over frames, and a polled readback means no frame waits for the GPU.
- Bump `ThumbnailCache::c_Version` when pictures would look different, and not otherwise.
- A saved edit marks entries dirty through `WatchSources`; after a settling delay `StartQueued` queues them and `UpdateSceneJob` renders and reads back the new picture.

## Check yourself

1. In the toy, the first session ends with the index holding the key of `Rusty.stmat`. A new session with the same version starts, and the stamp of `Rust.png` has changed to 102 meanwhile. What does the request print?

   :::answer{tests="choose-key"}
   The request prints `Rusty.stmat: rendered again`. The key hashes the stamps of the material and of its texture, the texture's stamp differs, so the key differs from the stored one. Reading the file would show a picture of the old texture.
   :::

2. A 4,096 by 4,096 RGBA8 texture has levels down to 1 by 1 pixel and 4 bytes per pixel. About how many bytes does the thumbnail job read for the levels that fit in 128 pixels, and how many does the whole chain hold?

   :::answer{tests="compute-reads"}
   The levels from 128 down to 1 hold 4 × (4^7 + 4^6 + ... + 1) = 4 × 21,845 = 87,380 bytes. The chain from 4,096 down holds 4 × 22,369,621 = 89,478,484 bytes. The job reads about 87,000 bytes plus the header, roughly a thousand times fewer.
   :::

3. Why does the scene job start a `TextureReadback` in one frame and use its pixels in a later one?

   - A. The pixels are encoded as PNG in the later frame.
   - B. The copy needs the GPU to finish, and the CPU would wait for it if it asked in the same frame.
   - C. The renderer draws a thumbnail over two frames.
   - D. The cache may use only one frame in 60.

   :::answer{tests="never-stall"}
   B. Asking for GPU results in the frame that made them stops the frame until the GPU is done. A is a later step on a job. C and D describe nothing in the code.
   :::

4. Which of these needs a new `ThumbnailCache::c_Version`? (a) The preview sun gets a wider penumbra. (b) The Content Browser draws tiles larger. (c) `c_Size` changes from 128 to 160. (d) A new asset type gets a thumbnail.

   :::answer{tests="bump-version"}
   Only (a). Pictures of existing assets look different but their keys do not change. (b) changes the drawing of tiles, not the pictures. (c) is already in the key text, so keys change without a bump. (d) adds pictures for assets that had none.
   :::

5. Put these in order after a saved material edit: the scene job renders; `WatchSources` marks the entry; the file is replaced; `StartQueued` queues the entry; the readback finishes.

   :::answer{tests="trace-flow"}
   `WatchSources` marks the entry; `StartQueued` queues it after the settling frames; the scene job renders; the readback finishes; the file is replaced. The file comes last because the PNG is encoded and written from the finished picture on an input and output job.
   :::

## Exercises

1. **Basic.** The cache keeps at most 512 GPU textures by default. How many bytes do 512 full-size thumbnails of 128 by 128 pixels hold in video memory?

   :::answer[Worked solution]{tests="compute-reads"}
   One thumbnail holds 128 × 128 × 4 = 65,536 bytes. Times 512 is 33,554,432 bytes, which is 32 MiB. Pictures of non-square textures are smaller, so this is the upper bound.
   :::

2. **Medium.** Extend the toy so that the key covers the whole dependency closure: a prefab depends on a material that depends on a texture. Change the texture's stamp and show that the prefab's key changes.

   :::answer[Worked solution]{solution="sketches/editor-thumbnails-closure.cpp" tests="choose-key"}
   The function `CollectClosure` walks the `DependsOn` lists, skips names already seen, and so ends on cycles. `ComputeKey` hashes every name and stamp it collects. The prefab's own stamp does not change, but the texture two levels down does, so the key changes.

   ```cpp sketch="editor-thumbnails-closure.cpp"
   #include <cstdint>
   #include <cstdio>
   #include <map>
   #include <string>
   #include <vector>

   namespace Toy
   {

   	struct Asset
   	{
   		uint64_t Stamp = 0;
   		std::vector<std::string> DependsOn;
   	};

   	// The asset and everything it depends on, each name once, in the order the walk meets them.
   	void CollectClosure(const std::map<std::string, Asset>& assets, const std::string& name, std::vector<std::string>& closure)
   	{
   		for (const std::string& seen : closure)
   		{
   			if (seen == name)
   				return;
   		}
   		closure.push_back(name);
   		for (const std::string& source : assets.at(name).DependsOn)
   			CollectClosure(assets, source, closure);
   	}

   	uint64_t ComputeKey(const std::map<std::string, Asset>& assets, const std::string& name)
   	{
   		std::vector<std::string> closure;
   		CollectClosure(assets, name, closure);
   		uint64_t key = 14695981039346656037ull;
   		for (const std::string& source : closure)
   		{
   			for (char character : source + ":" + std::to_string(assets.at(source).Stamp) + ";")
   			{
   				key ^= static_cast<uint8_t>(character);
   				key *= 1099511628211ull;
   			}
   		}
   		return key;
   	}

   }

   int main()
   {
   	std::map<std::string, Toy::Asset> assets;
   	assets["Rust.png"] = { 100, {} };
   	assets["Rusty.stmat"] = { 200, { "Rust.png" } };
   	assets["Barrel.stprefab"] = { 300, { "Rusty.stmat" } };

   	const uint64_t before = Toy::ComputeKey(assets, "Barrel.stprefab");
   	assets["Rust.png"].Stamp = 101;
   	const uint64_t after = Toy::ComputeKey(assets, "Barrel.stprefab");
   	std::printf("The prefab's picture is %s\n", before == after ? "kept" : "rendered again");

   	std::vector<std::string> closure;
   	Toy::CollectClosure(assets, "Barrel.stprefab", closure);
   	std::printf("Closure size: %zu\n", closure.size());
   	return 0;
   }
   ```

   ```text output-of="editor-thumbnails-closure.cpp"
   The prefab's picture is rendered again
   Closure size: 3
   ```

   1. **Lines 17–27:** the walk adds a name once and follows its dependencies, so a cycle ends.
   2. **Lines 29–43:** the key hashes every name and stamp of the closure in walk order.
   3. **Lines 47–63:** the texture's stamp changes, and the prefab, two steps away, gets another key.
   :::

3. **Hard.** Trace it yourself. Start the editor in a debugger with a project open, set a breakpoint in `ThumbnailCache::ComputeKey`, edit a material and save. Which functions call `ComputeKey` before the picture renders again, and which source of the material's closure made the key change?

   :::answer[Worked solution]{tests="trace-flow,never-stall"}
   The breakpoint stops first in `ThumbnailCache::WatchSources` in `StrataEditor/src/Editor/ThumbnailCache.cpp`, which compares the new key with `Entry::Key`. After the settling frames, `ThumbnailCache::Start` calls it again for the key of the new work. Watch `outSources`: the entry of the saved material has a changed stamp from `EditorAssetManager::GetContentStamp`. Then step into `UpdateSceneJob` and watch `job.Readback` until `IsReady` is true.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/ThumbnailCache.h` and `ThumbnailCache.cpp`: the cache, `ComputeKey`, `UpdateSceneJob`, `StartTextureJob`, `MakeTextureThumbnail`.
- `StrataEditor/src/Editor/DisplayImage.h` and `DisplayImage.cpp`: `DisplayImage::Upload`.
- `StrataEditor/src/Editor/ProjectThumbnail.h` and `ProjectThumbnail.cpp`: the launcher's picture.
- `Strata/src/Strata/Asset/EditorAssetManager.h`: `GetContentStamp`; `Strata/src/Strata/Asset/AssetManager.h`: `GetDependencyClosure`, the dependency closure.
- `StrataTests/src/Editor/ThumbnailTests.cpp` and `GPUThumbnailTests.cpp`: the suites.
- Files: `<project>/.strata/Thumbnails` (pictures and index), `<project>/.strata/Thumbnail.png` (the project's picture).

## Further reading

- FNV hash, by Landon Curt Noll: the hash family of the key; intermediate.
- The engine's Docs/Architecture.md, the Thumbnails entry: the same part from the engine's side; advanced.
