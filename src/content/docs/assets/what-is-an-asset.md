---
id: assets/what-is-an-asset
title: "What an asset is"
description: "Why an engine turns a picture, a model or a sound into its own stored form, and how Strata's editor and game share one way to load it."
kind: concept
size: M
tracks: [E]
needs: [basics/data-formats, core/layers-registries, world/ecs]
time: 45
learn:
  - id: stored-form
    text: explain why a game reads a stored form instead of the source file an artist made
  - id: pipeline-stages
    text: name every stage between a source file in Assets and a texture the GPU samples
  - id: seams
    text: explain how a module registers what the asset layer cannot know, and why the layer needs this
  - id: texture-bytes
    text: compute the bytes of a texture and its mip chain in RGBA8 and in BC7
since: 0.3.0
status: final
---

Open the first game's project and drag a picture into the Content Browser. A moment later you can pick it as the image of a material, and the object in the Scene view shows it. Now export the game and open the folder the export made. The picture file is not there, yet the exported game shows the picture.

Something turned the file into something else on the way. This page follows that change for one real file, the Showcase's `WeatheredSteel_arm.png`, from the project folder to a texture the :term[graphics processing unit]{id=gpu} (GPU) reads. It then explains why Strata works this way and how the same loading code serves the editor and the game.

## Loading the picture file itself breaks four ways

The plain plan is to keep the PNG in the game and to load it when the game starts. The file opens, a library decodes it, and the pixels go to the GPU. The plan works for a toy, and it breaks in four ways in a real game.

1. **Decoding is slow.** A PNG is compressed for storage. Before the GPU can use it, the processor must undo that compression, pixel by pixel, and a game has hundreds of such files.
2. **The GPU wants another form.** Distant surfaces need smaller copies of a texture, called **mip levels**, and a GPU can also read textures in a block-compressed form that takes a quarter of the memory. A PNG holds neither. Someone must build them, and building them is slow too.
3. **Paths break.** A scene that says "use `Props/WeatheredSteel_arm.png`" stops working when an artist moves the file into another folder, or when two folders hold a file of that name.
4. **Thousands of loose files ship badly.** A game with 3,000 assets would copy 3,000 files, open each of them, and expose all of them for anyone to take.

The four breaks share one cause: the file an artist makes is built for editing and exchange, while the game needs a form built for loading. The fix is to do the conversion once, ahead of time, and to name the result by an identity that does not depend on a path.

## An asset is content the engine loads by handle

An **asset** is a piece of content that the engine loads by handle, such as a texture, a mesh, a material, a sound or a scene. In code, every kind of asset is a class that derives from `Asset`. A scene never holds the file path of its texture: it holds a handle, the 64-bit identity of the kind that the entity-component-system (:term[ECS]{id=ecs-entity-component-system}) world uses, taught in [the page on the ECS](../world/ecs.md). The engine finds what the handle names. How a handle is made is the subject of [Handles and the .meta file](handles-meta.md).

An asset has two lives. The **source file** is the file in the project's `Assets/` folder: the PNG, the glTF model or the font file that a person made or bought. It stays there unchanged, and tools such as an image editor keep working on it. The second life is the form the engine reads, which the next definition names.

The **stored form** of an asset is the :term[bytes]{id=byte} that a loader reads to make the asset. The loader is a function that the module owning the asset type registers, and it turns stored bytes into a ready object. The stored form is not always different from the source. For most types it is a cooked file; for fonts and for five document types it is the source itself.

Figure 1 shows the whole path. Read it from the left. A :term[source file]{id=source-file} and its sidecar enter the importer, which writes a stored form. From there the editor and the game take different roads that meet in one loading path.

```mermaid caption="A source file becomes a stored form once, in the editor. The editor reads that form from its cache and the game reads it from a pack; both then use the same loading path." alt="A flow from left to right. A source file with its sidecar goes into an importer that runs only in the editor. The importer writes a cache file named by the handle. The editor reads the cache file, and an export copies it into a pack that the game reads. Both readers feed one loader that runs on a worker thread, and a finishing step on the main thread uploads the result to the GPU."
flowchart LR
    S["Assets/WeatheredSteel_arm.png and .meta"] --> I["Importer: editor only"]
    I --> C[".strata/Cache/handle.bin"]
    C --> E["EditorAssetManager"]
    C -- "export" --> P["Game.stpak"]
    P --> R["RuntimeAssetManager"]
    E --> L["Loader on a worker thread"]
    R --> L
    L --> F["Finish on the main thread: GPU upload"]
    F --> G["GPU texture"]
```

The two middle boxes of the figure are the two sides of one coin. The editor works with sources and keeps its stored forms in a cache; the game has no sources at all. Both read stored forms, so a texture loads the same way whichever program asks.

## Importers turn sources into stored forms

**Import** is the step that turns a source file into the form the engine stores for it.

An **importer** is a class that does this for a set of file extensions. Strata has importers for pictures (`.png`, `.jpg`, `.jpeg`, `.tga`, `.bmp`, `.psd`, `.gif`, `.hdr`), for glTF models, for audio files, for fonts, for color lookup tables, and one for each of the engine's own document types.

For most types an import is also a cook. To **cook** a source is to turn it into the engine-ready, often binary form that loading needs. Cooking holds the slow work of the four breaks: decoding, building mip levels and compressing blocks.

A **cooked asset** is a stored form that such a cook made. An audio clip, for example, is cooked into a file with its own :term[header]{id=header}.

:::example[One image, followed to the GPU]
`Samples/Showcase/Assets/Generated/Props/WeatheredSteel_arm.png` is a 1024 by 1024 picture of 1,256,600 bytes. Its name says what it holds: ambient occlusion, roughness and metallic values in the three channels, data for a material rather than a color to look at. The file next to it, `WeatheredSteel_arm.png.meta`, holds the handle `CAA58AB49C5FCF59`, the type `Texture` and the import settings: `Usage` is `Data`, `Compression` is `Auto` and `GenerateMips` is `true`.

The importer reads the PNG and follows those settings in four steps.

1. The importer decodes the file to 1024 by 1024 pixels in eight-bit red, green, blue and alpha (RGBA8) form, 4 bytes each, which is 4,194,304 bytes in memory.
2. The importer builds the mip levels: 1024, 512, 256 and on down to 1 pixel, eleven levels in all.
3. The importer compresses each level as soon as it has built it, before it builds the next. The setting's own tooltip says that `Auto` stores data of several channels in a block-compressed format called block compression 7 (BC7).
4. The importer writes the result to `.strata/Cache/CAA58AB49C5FCF59.bin`, a name made from the handle.

BC7 stores each 4 by 4 block of pixels in 16 bytes, which is 1 byte a pixel. One level is then 1,048,576 bytes, and the whole chain about 1.4 million bytes. The chain in plain pixels would take 5,592,404 bytes. The GPU reads the cooked file as it is, with no decoding and no mip building.
:::

Notice what the example does not claim. The cooked file is not smaller than the PNG here: it is about 1.4 million bytes against 1.26 million. The gain is time, memory on the GPU and a form that loads at once, not disk space.

## Five document types are their own source

Not every asset has an outside source. Scenes, prefabs, materials, animation controllers and worlds are files that the engine writes itself, and they are already in the form it reads. An **engine-native asset** is an asset of one of these types, stored as its own :term[JSON]{id=json} document under the extensions `.stscene`, `.stprefab`, `.stmat`, `.stanimator` and `.stworld`.

Their importers still run, but they do not convert: they check the file and register it, and the stored form is the source file itself. Fonts take the same shortcut, because a font file is already what the loader needs. The function that gives these five extensions is `GetNativeAssetExtension` in `Strata/src/Strata/Asset/AssetTypes.cpp`; every other type returns an empty answer, because it is always imported from another format.

Strata has 13 asset types, which the enum `AssetType` names: `Texture`, `Mesh`, `Material`, `Model`, `Font`, `AudioClip`, `ColorLookup`, `Skeleton`, `AnimationClip`, `AnimationController`, `Scene`, `Prefab` and `World`. A model file such as a glTF is an asset that owns others: its import also makes the meshes, materials and textures inside it. Packs store the number of each type, so the list only grows at its end.

## Engines cook ahead, load sources, or cook on first use

Three approaches cover most engines. Each starts from the flaw of the one before.

Loading sources at run time is the plain plan of the start of this page. It needs no tools, and a change to a file shows at once. Its flaw is the four breaks: slow starts, no block compression, fragile paths and many loose files.

Cooking ahead fixes the slowness. A build step converts every source before the game ships, and the game reads only the results. The flaw is the wait: every change to a source needs a conversion before anyone sees it, and an engine must know when a cooked file is out of date.

Cooking on first use gives the editor the best of both. The engine converts a file when something first asks for it, and keeps the result in a cache. Its flaw is the first request, which stalls unless the work happens in the background, and a game that cooks while it plays needs the importers inside it.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Load sources at run time | Decoding on every start; many files | Fine for small games; no GPU-ready forms | Lowest | Small engines and prototypes |
| Cook ahead into packages | One build step; fast starts | Best: every form is made for the GPU | A build step and a record of what is stale | Unreal's cooked packages |
| Cook on first use, cache | A wait at the first use; a cache folder | Same as cooked forms | Needs a rule for when a cache is stale, and background work | Unity's Library folder, Godot's `.import` files |

The sources of the last two rows are in the further reading. Unity and Godot keep a folder of cooked results next to the project and rebuild it when a source or a setting changes; both then pack those results for a shipped game.

## Strata cooks in the editor and reads stored forms in the game

Strata combines the last two approaches. The editor cooks on first use, in the background, into `.strata/Cache/`. An export then copies stored forms into a pack, so the game never cooks anything. The importers run only in the editor and in the test programs that need them.

An **asset manager** is the object that registers, loads and keeps the assets of one program. Strata has one :term[base class]{id=base-class}, `AssetManagerBase`, with two managers above it. `EditorAssetManager` treats every file under `Assets/` that has a known importer as an asset, imports it into the cache, watches the folder, and handles moves and deletes. `RuntimeAssetManager` reads assets from mounted packs, takes dependencies and bounds from the pack's tables, and never imports.

Because both managers share the base, the path from stored bytes to a ready asset is one path. A request goes into a queue, and a worker thread reads the bytes and runs the loader. Then the :term[main thread]{id=main-thread} finishes the asset. For a texture, that means uploading it to the GPU in small steps. [Loading without stalling a frame](loading.md) teaches that path, and [Import, cache and cancel](importing.md) teaches the editor's side.

:::why[Why must the importers stay out of the game?]
An importer needs large code: a glTF reader, a tool that tries many ways to store each block, an image decoder for eight formats. A game that carried them would grow, would load slowly, and would open a door for hostile files. Strata keeps them in a layer that games never link, so a shipped game cannot import even if it wants to. The price is that a game cannot add content from a loose file at run time; it can only read what an export packed.
:::

The registration of importers shows the rule in code. The function below is the whole list. Look at how it opens the registry first, and at the two `#if` lines: a build without the audio or animation module has no importer for them.

```cpp src="Strata/src/Strata/Asset/AssetImporters.cpp#L160-L178" symbol="RegisterAssetPipeline"
void RegisterAssetPipeline()
{
	AssetImporterRegistry::BeginRegistration();
	AssetImporterRegistry::Register(CreateScope<NativeAssetImporter>(AssetType::Scene, GetNativeAssetExtension(AssetType::Scene)));
	AssetImporterRegistry::Register(CreateScope<NativeAssetImporter>(AssetType::Prefab, GetNativeAssetExtension(AssetType::Prefab)));
	AssetImporterRegistry::Register(CreateScope<NativeAssetImporter>(AssetType::Material, GetNativeAssetExtension(AssetType::Material)));
#if ST_WITH_ANIMATION
	AssetImporterRegistry::Register(CreateScope<NativeAssetImporter>(AssetType::AnimationController, GetNativeAssetExtension(AssetType::AnimationController)));
#endif
	AssetImporterRegistry::Register(CreateScope<NativeAssetImporter>(AssetType::World, GetNativeAssetExtension(AssetType::World)));
	AssetImporterRegistry::Register(CreateScope<TextureImporter>());
	AssetImporterRegistry::Register(CreateScope<GltfImporter>());
#if ST_WITH_AUDIO
	// Audio files are sources only for an engine with the audio module.
	AssetImporterRegistry::Register(CreateScope<AudioClipImporter>());
#endif
	AssetImporterRegistry::Register(CreateScope<FontImporter>());
	AssetImporterRegistry::Register(CreateScope<ColorLookupImporter>());
}
```

1. **Line 162:** the registry opens here, so importers can register; a program that never calls this function never has one.
2. **Lines 163–169:** one `NativeAssetImporter` for each engine document type, which checks the file and stores the source itself. The animation line sits in an `#if`.
3. **Lines 170–171:** the picture importer and the glTF importer, which cook.
4. **Lines 172–175:** the audio importer exists only in a build with the audio module.
5. **Lines 176–177:** fonts, which store their source, and color lookup tables.

Only a program that passes this function to the :term[composition root]{id=composition-root} registers importers. At the pin that is the editor, in `StrataEditor/src/EditorApplication.cpp`, and the test programs. `StrataRuntime` passes none, so for it the importer registry never opens. [Registries in general](../core/layers-registries.md) explains why a registry must be open before modules fill it.

## Seams let modules register what the asset layer cannot know

The asset layer must load meshes and textures, but it may not know what a mesh is. Its row in the :term[layer table]{id=layer-table}, `StrataTests/Architecture/Layers.json`, lets it include only `Core`, and it may include no graphics headers. A `Mesh` holds GPU buffers; the asset layer cannot name it.

The way out is the pattern you saw in the composition root: the asset layer defines a registry and the module that owns the type fills it. Figure 2 shows who includes whom and who registers what.

```mermaid caption="The Renderer fills registries that the Asset layer owns, so the Asset layer never names a renderer type." alt="Four boxes stand in layers. The asset pipeline tooling layer is on top, the Renderer and Physics are in the middle, and the Asset layer, which includes only Core, is at the bottom. Arrows from the Renderer and Physics to the Asset layer name what they register or read."
flowchart TB
    AP["AssetPipeline layer: importers, cooker, EditorAssetManager. Games never link it"]
    R["Renderer: Texture, Mesh, Material, Font"]
    PH["Physics: AssetMeshProvider"]
    A["Asset layer: registries, loading, packs, RuntimeAssetManager. Includes Core only"]
    AP --> R
    AP --> A
    R -. "registers loaders, geometry reader, upload service" .-> A
    PH -- "reads mesh triangles" --> A
```

The seams are these:

- **Loaders.** `AssetLoaderRegistry` maps an asset type to a function from stored bytes to a ready asset. The :term[renderer]{id=renderer} registers `Texture`, `Mesh`, `Material`, `Font` and `ColorLookup`; the scene module registers `Prefab`, `Model` and `Scene`; audio, animation and world register theirs. Using the registry before the composition root opens it fails a check.
- **Built-in assets.** The renderer provides eight meshes, from the cube and sphere to the cone and capsule, and the default material, which have no file at all. Their handles are fixed small numbers.
- **Manager extensions.** The renderer adds a texture streamer to every manager that is made, and the asset layer runs it without knowing what it does.
- **The upload seam.** `AssetUploadContext` and the `IAssetGraphics` service let a finished asset record its GPU uploads. The renderer provides them, and the asset layer includes no NVRHI or Vulkan header.
- **Mesh geometry.** `MeshGeometryRegistry` holds, for each mesh type, a reader that gives a mesh's positions and triangle list.

The last seam is a good example because two layers that never meet use it. Physics needs the triangles of a mesh to build a collision shape, but physics must not include the renderer. The renderer registers a reader of its `Mesh` at startup, and `AssetMeshProvider` in the physics module asks the registry.

```cpp src="Strata/src/Strata/Renderer/RendererRegistration.cpp#L101-L106" from="AssetLoaderRegistry::Register(AssetType::Mesh" to="MeshGeometryRegistry::Register(AssetType::Mesh, ReadMeshGeometry);" symbol="RegisterRendererModule"
AssetLoaderRegistry::Register(AssetType::Mesh, [](const AssetMetadata&, std::span<const uint8_t> data, std::string* outError) -> Ref<Asset>
{
	return Mesh::Deserialize(data, outError);
});
// Modules that collide with meshes (physics) read their triangles without knowing the renderer's Mesh.
MeshGeometryRegistry::Register(AssetType::Mesh, ReadMeshGeometry);
```

The first call tells the asset layer how to turn stored bytes into a `Mesh`, and the second tells every module how to read triangles out of one. Neither physics nor the asset layer includes `Mesh.h`.

## What the choice cannot do

A shipped game cannot import. It cannot load a PNG the player drops into a folder, and it cannot cook a texture at run time. Content that appears after the export must come as a pack that the editor made.

Models come only as glTF; Strata has no importer for other model formats. Convert them to glTF with a tool first. Some things Strata does not do at all, and [What Strata does not do](../appendix/not-in-strata.md) lists them.

## Common mistakes

- **Thinking the PNG ships.** Symptom: you delete a source from `Assets/` after an export and expect the exported game to break, or you keep it and expect it to be in the pack. The pack holds stored forms; the export reads sources never. The fix is to change the source, then let the editor import again and export again.
- **Editing cache files.** Symptom: a change to a file in `.strata/Cache/` disappears or breaks the asset. The cache belongs to the editor, which names each file by a handle and replaces it when an import finishes. Edit the source or its import settings instead.
- **Including renderer headers in `Asset/`.** Symptom: the test `Architecture.Layering` fails with a line such as "layer Asset may not include layer Renderer". Do not widen the table. Add a registry or an interface to the asset layer and let the renderer fill it.
- **Moving a source without its sidecar.** Symptom: scenes that used the file show an empty slot. The handle lives in the `.meta` file, so both must move together; use the editor's move command, which does it.

## Summary

- A game reads a stored form because decoding sources is slow, the GPU wants mips and block compression, paths break and loose files ship badly.
- A source in `Assets/` becomes a cache file named by its handle, then a pack entry; a worker runs the loader and the main thread uploads the result.
- The asset layer includes only Core. Modules register loaders, built-in assets, manager extensions, upload services and mesh readers into its registries, so the layer never names a renderer type.
- A mip chain of a 1024 by 1024 texture takes 5,592,404 bytes in RGBA8 and about 1.4 million bytes in BC7.

## Check yourself

1. A teammate says: "Our exported game needs `WeatheredSteel_arm.png`, so I will copy the `Assets/` folder next to it." Which statement is right?

   - A. The game needs the PNG, because the loader decodes it at start.
   - B. The game needs only the pack; the PNG is a source, and the pack holds its stored form.
   - C. The game needs the `.meta` file, because the handle lives only there.

   :::answer{tests="stored-form"}
   B is right. A describes the plain plan that breaks four ways; Strata decodes in the editor. C is wrong too: the handle is also written into the pack's tables, and the game never reads sidecars.
   :::

2. Put these in order: loader on a worker, importer, GPU upload on the main thread, cache file, source file.

   :::answer{tests="pipeline-stages"}
   Source file, importer, cache file, loader on a worker, GPU upload on the main thread. In the game, a pack stands between the cache file and the loader; the export copies the stored form into it.
   :::

3. The audio module needs the asset layer to load clips. Which design obeys the layer table?

   - A. `Asset/` includes `Audio/AudioClip.h` and calls its loader.
   - B. The audio module registers its loader into `AssetLoaderRegistry`.
   - C. The row of `Asset` in `Layers.json` lists `Audio` in `MayInclude`.

   :::answer{tests="seams"}
   B is right: the lower layer owns the registry and the higher module fills it. A and C make the lower layer depend on the higher one, which the table forbids and the rule on widening rows warns against.
   :::

4. A 512 by 512 texture is stored in BC7 with its mip chain. Predict its size: the chain's levels run 512, 256, 128, 64, 32, 16, 8, 4, 2 and 1.

   :::answer{tests="texture-bytes"}
   Each level from 512 down to 4 takes its pixel count in bytes: 262,144, 65,536, 16,384, 4,096, 1,024, 256, 64 and 16, which sum to 349,520. The levels 2 and 1 each take one 16-byte block, adding 32. The total is 349,552 bytes.
   :::

## Exercises

1. **Basic.** Follow the Showcase's `WeatheredSteel_arm.png` through four places: its source path, its sidecar, its cache file and the folder of the exported game. Name what you find in each, and which one holds no PNG.

   :::answer[Worked solution]{tests="pipeline-stages"}
   The source is `Samples/Showcase/Assets/Generated/Props/WeatheredSteel_arm.png`. Its sidecar `WeatheredSteel_arm.png.meta` next to it gives the handle `CAA58AB49C5FCF59`. The cache file is `.strata/Cache/CAA58AB49C5FCF59.bin` in the project, found by that handle. The exported folder holds the :term[runtime]{id=runtime} program, its manifest and notices, and the pack, named `<name>.stpak`; the pack holds the stored form and no PNG.
   :::

2. **Medium.** Run the sketch below and compare its first line with the arithmetic in the example. Then change it so that it takes a width and a height, and predict the chain sizes of a 2048 by 1024 and a 4096 by 4096 BC7 texture before you run it.

   ```cpp sketch="assets-what-is-an-asset-texture-bytes.cpp"
   #include <cstdint>
   #include <cstdio>

   namespace
   {

   	// Bytes of one mip level: RGBA8 stores 4 bytes a pixel, BC7 stores each 4 by 4 block of pixels in 16 bytes.
   	uint64_t LevelBytes(uint32_t size, bool blockCompressed)
   	{
   		if (!blockCompressed)
   			return uint64_t(size) * size * 4;
   		const uint64_t blocks = (size + 3) / 4;
   		return blocks * blocks * 16;
   	}

   	// Every level from the full size down to one pixel, each half the size of the one before.
   	uint64_t ChainBytes(uint32_t size, bool blockCompressed)
   	{
   		uint64_t total = 0;
   		for (;; size /= 2)
   		{
   			total += LevelBytes(size, blockCompressed);
   			if (size == 1)
   				return total;
   		}
   	}

   }

   int main()
   {
   	const uint32_t size = 1024;
   	std::printf("RGBA8, one level:   %llu bytes\n", (unsigned long long)LevelBytes(size, false));
   	std::printf("RGBA8, mip chain:   %llu bytes\n", (unsigned long long)ChainBytes(size, false));
   	std::printf("BC7, one level:     %llu bytes\n", (unsigned long long)LevelBytes(size, true));
   	std::printf("BC7, mip chain:     %llu bytes\n", (unsigned long long)ChainBytes(size, true));
   	return 0;
   }
   ```

   ```text output-of="assets-what-is-an-asset-texture-bytes.cpp"
   RGBA8, one level:   4194304 bytes
   RGBA8, mip chain:   5592404 bytes
   BC7, one level:     1048576 bytes
   BC7, mip chain:     1398128 bytes
   ```

   1. **Lines 12–13:** a BC7 level counts 4 by 4 blocks of 16 bytes each; a size that is not a multiple of 4 rounds up.
   2. **Lines 20–25:** the loop adds a level, stops at one pixel and otherwise halves the size.
   3. **Line 32:** the size is the only number you change.

   :::answer[Worked solution]{tests="texture-bytes" solution="sketches/assets-what-is-an-asset-wide-chain.cpp"}
   The first line is 4,194,304, which is 1024 times 1024 times 4. The new version rounds each side up to whole blocks and halves each side down to 1.

   ```cpp sketch="assets-what-is-an-asset-wide-chain.cpp"
   #include <cstdint>
   #include <cstdio>

   namespace
   {

   	// BC7 bytes of one level: 16 bytes for each 4 by 4 block, partial blocks rounded up.
   	uint64_t LevelBytes(uint32_t width, uint32_t height)
   	{
   		return uint64_t((width + 3) / 4) * ((height + 3) / 4) * 16;
   	}

   	// A level halves each side but never goes below one pixel; the chain ends at 1 by 1.
   	uint64_t ChainBytes(uint32_t width, uint32_t height)
   	{
   		uint64_t total = 0;
   		for (;;)
   		{
   			total += LevelBytes(width, height);
   			if (width == 1 && height == 1)
   				return total;
   			width = width > 1 ? width / 2 : 1;
   			height = height > 1 ? height / 2 : 1;
   		}
   	}

   }

   int main()
   {
   	std::printf("2048 x 1024: %llu bytes\n", (unsigned long long)ChainBytes(2048, 1024));
   	std::printf("4096 x 4096: %llu bytes\n", (unsigned long long)ChainBytes(4096, 4096));
   	return 0;
   }
   ```

   ```text output-of="assets-what-is-an-asset-wide-chain.cpp"
   2048 x 1024: 2796240 bytes
   4096 x 4096: 22369648 bytes
   ```

   1. **Line 10:** each side rounds up to whole blocks before the blocks are counted.
   2. **Lines 20–21:** the chain ends only when both sides reach 1.
   3. **Lines 22–23:** a side that has reached 1 stays at 1 while the other side keeps halving.

   A chain is about four thirds of its first level. For 4096 by 4096 that is 16,777,216 times 4 over 3, near 22.4 million, and the output agrees.
   :::

3. **Medium.** Find where the renderer registers its loaders and where tools register importers, and which programs link each.

   :::answer[Worked solution]{tests="seams"}
   The renderer's loaders are registered in `RegisterRendererModule` in `Strata/src/Strata/Renderer/RendererRegistration.cpp`, which the composition root calls for every program. The importers are registered in `RegisterAssetPipeline` in `Strata/src/Strata/Asset/AssetImporters.cpp`. The editor passes that function in `StrataEditor/src/EditorApplication.cpp`, and the test programs pass it too; `StrataRuntime` does not.
   :::

4. **Hard.** Your game ships 200 textures of 1024 by 1024 and decodes the PNG files at start. Argue for or against this plan in numbers: memory, work at start and files shipped.

   :::answer[Worked solution]{tests="stored-form"}
   Decoded to RGBA8 with mips, each texture takes 5,592,404 bytes, so 200 textures take about 1.1 billion bytes of memory, where BC7 takes about 280 million. The start must decode 200 PNG files and build 200 mip chains, where the cooked game reads bytes. The game ships 200 loose files that anyone can copy. The plan wins only in simplicity, so it fits a prototype and not a shipped game.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetTypes.h` and `AssetTypes.cpp`: `AssetType` and `GetNativeAssetExtension`.
- `Strata/src/Strata/Asset/AssetManager.h`: `AssetManagerBase`, `AssetLoaderRegistry`, `AssetLoadFunction`.
- `Strata/src/Strata/Asset/EditorAssetManager.cpp` and `RuntimeAssetManager.h`: the two managers.
- `Strata/src/Strata/Asset/AssetImporter.h` and `AssetImporters.cpp`: `AssetImporterRegistry` and `RegisterAssetPipeline`.
- `Strata/src/Strata/Asset/MeshGeometry.h` and `Strata/src/Strata/Physics/AssetMeshProvider.h`: the mesh seam.
- `Strata/src/Strata/Asset/AssetUploadContext.h`: the upload seam.
- `StrataTests/Architecture/Layers.json`: the rows of `Asset` and `AssetPipeline`.

## Further reading

- Unity Manual, [Asset Database](https://docs.unity3d.com/Manual/AssetDatabase.html): how Unity imports files into its Library folder; intermediate.
- Godot Engine documentation, [Import process](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/import_process.html): how Godot keeps imported results beside the project; beginner.
- Epic Games, Unreal Engine documentation, "Cooking and Chunking": how Unreal builds cooked packages for a shipped game; advanced.
