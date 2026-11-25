---
id: reference/assets
title: "Asset types, file formats, importer versions, budgets and statistics"
description: "The asset types, importers with versions, stored file formats, residency budgets and statistics of Strata's asset manager, in tables to consult."
kind: reference
size: M
tracks: []
needs: [assets/handles-meta]
status: final
---

This page holds the facts of the asset system in one place, for a reader who needs a name, a version or a default and does not want to read the code. An asset is a file the engine loads for a game, and every asset has a handle that stays the same when the file moves (see [Handles and meta files](../assets/handles-meta.md)). Each table has a short introduction that names the page teaching its subject.

There are five groups of tables. The :term[asset types]{id=asset-type} come first, then the :term[importers]{id=importer}, which turn :term[source files]{id=source-file} into assets. The :term[stored forms]{id=stored-form} follow: the :term[file formats]{id=file-format} the engine writes and reads, each with its version. The last two groups are the residency budgets, which limit how much memory assets may hold, and the statistics, which report what the :term[asset manager]{id=asset-manager} does. A row is one thing; the columns name it, say what it is and give the number you want to find.

## Asset types

An asset has one of :value{key="assetTypes.count"} types. The type is stored as a number in packs and in import records, so the engine adds a type only at the end of the list. It never changes the number of an old one. Read the table by its value: a row says what that number means. The type decides which loader reads the asset and which importer makes it (see [What is an asset](../assets/what-is-an-asset.md)).

::include{file="asset-types.md"}

The next table adds what the generated one does not say. A native extension is the file extension of a type that the engine writes itself, such as `.stscene`. Other types have no native extension: their files come from other programs, such as a texture painted elsewhere, and the engine keeps its own cooked copy in a cache. A loader is the code that turns stored :term[bytes]{id=byte} into an asset; each :term[engine module]{id=engine-module} registers the loaders of its own types, which is why the table names a module.

This table is written by hand from `Strata/src/Strata/Asset/AssetTypes.cpp` and from the registration files of the modules; the sources are in the strip at the end of the page.

| Type | Native extension | Loader registered by | Made by |
| --- | --- | --- | --- |
| `Scene` | `.stscene` | the scene module | the native importer |
| `Prefab` | `.stprefab` | the scene module | the native importer |
| `Model` | none | the scene module | the glTF importer |
| `Mesh` | none | the :term[renderer]{id=renderer} module | the glTF importer, as a :term[sub-asset]{id=sub-asset} of a model |
| `Material` | `.stmat` | the renderer module | the native importer, or the glTF importer as a sub-asset |
| `Texture` | none | the renderer module | the texture importer, or the glTF importer as a sub-asset |
| `AudioClip` | none | the audio module | the audio clip importer |
| `Font` | none | the renderer module | the font importer |
| `Skeleton` | none | the animation module | the glTF importer, as a sub-asset of a model |
| `AnimationClip` | none | the animation module | the glTF importer, as a sub-asset of a model |
| `AnimationController` | `.stanimator` | the animation module | the native importer |
| `World` | `.stworld` | the world module | the native importer |
| `ColorLookup` | none | the renderer module | the color lookup importer |

The value `None` is no asset: it marks a handle that names nothing. A sub-asset is an asset that lives inside another asset's file and has its own handle, such as one mesh of a model. It has no file and no importer of its own.

## Importers

An importer reads a source file and writes the stored form of one or more assets. Each importer has a version number. The engine bumps it whenever the importer's output changes, and every asset of that importer is then imported again, because its stored copy no longer matches what the importer would write today. That is why a version is a fact worth finding: a bump costs every user of the importer a re-import. The importer settings, such as a texture's compression, are taught in [Importing](../assets/importing.md) and [Texture cooking](../assets/texture-cooking.md).

The generated table above lists each importer with its version. The versions are values of the file `values.json`: the glTF importer is at version :value{key="importer.Model.version"} and the texture importer at version :value{key="importer.Texture.version"}. The table lists no extensions for the texture importer, because it declares them in `TextureImporter.cpp`, and the generator reads only the importer's `.h` file. It reads `.png`, `.jpg`, `.jpeg`, `.tga`, `.bmp`, `.psd`, `.gif` and `.hdr` files (`Strata/src/Strata/Asset/TextureImporter.cpp`).

A running editor gives the same facts without the code. The command `asset.types` lists every type with its native extension, or `null` when the type is only imported. For each type it also lists the importers, each with its name, version and extensions, so the texture importer's extensions appear there. The command needs no open project; its parameters are in [Commands](../reference/commands.md).

The native importer is one class, `NativeAssetImporter`, that the engine registers once for each of five types, with that type's native extension (`.stscene`, `.stprefab`, `.stmat`, `.stanimator`, `.stworld`). The generated table shows no extension for it, because each registration passes the extension in as a value. It stores the file as it is, because the file is already in the engine's own format and only needs a handle.

## Stored forms

A stored form is the byte layout in which the engine keeps an asset or a record on disk. Each has a magic, four letters at the start of the file that tell a reader which format it holds, and a version, a number the reader checks before it trusts the rest. A reader accepts the versions it knows and refuses the rest with an error; some formats still read their older versions, because files written long ago must keep working.

This table is written by hand from the constants named in its second column. Check it again when the engine changes.

| Form | Magic and version | Constant | Reads older | Taught in |
| --- | --- | --- | --- | --- |
| The `.meta` sidecar next to an asset file | `Format` `AssetMeta`, `Version` 1 | `c_AssetMetaVersion` | no | [Handles and meta files](../assets/handles-meta.md) |
| Cooked texture | `STTX`, 2 | `c_CookedTextureVersion` | version 1 | [Texture cooking](../assets/texture-cooking.md) |
| Asset pack | `STPK`, 2 | `AssetPack::c_Version` | version 1 | [Packs and export](../assets/packs-export.md) |
| Cooked mesh | `STMH`, 3 | `Mesh::c_CookedVersion` | versions 1 and 2 | [Models and glTF](../assets/models-gltf.md) |
| Cooked color lookup | `STLU`, 1 | `ColorLookup::c_FormatVersion` | none yet | [Color grading](../image/grading.md) |
| Import records file `ImportRecords.log` | version 1 | `ImportRecordStore::c_Version` | the older layout is migrated | [Importing](../assets/importing.md) |
| Cooked audio clip | `STAU`, 1 | `c_CookedVersion` of the clip asset | no | [Audio and input reference](../reference/audio-input.md) |
| Cooked scene | `STSC`, 1 | `c_Version` of the cooked scene format | no | [Scene reference](../reference/scene.md) |

A few numbers help to read these formats. A cooked texture stores its levels in blocks. A block is a square of 4 by 4 texels, and a level of a block-compressed texture always holds whole blocks. A block of the format `BC1` takes 8 bytes, and one of `BC7` takes 16 bytes.

A 2048 by 2048 `BC7` level is 512 by 512 blocks of 16 bytes, which is 4,194,304 bytes, 4 MiB. The same level with four plain bytes a texel is 16 MiB. The engine computes every level's size through `GetMipByteSize` and never from bytes per pixel, so an odd size such as 5 by 5 texels rounds up to 2 by 2 blocks.

An asset pack cuts the stored form of each asset into blocks of 256 KiB, compresses each block on its own and starts every entry at a 4 KiB boundary. A block whose compression saves less than an eighth is stored as it is. A pack of version 1 has no blocks: it holds the stored forms in plain bytes, and the reader still accepts it, so games exported before version 2 keep running.

A game can also list patch packs in its manifest: extra pack files that carry assets with the same handles as the main pack, for fixes and added content. The manifest names at most 256 of them (`GameManifest::c_MaxPatchPacks`), as files next to the manifest.

:::why
The stored forms carry versions and the importers carry versions for one reason: a project folder lasts longer than the engine build that made it. A reader that sees an unknown version fails with an error that names the file. The alternative, guessing, risks a crash in the middle of a game. The cost is that a format change needs a version bump and, for readers of old files, code that still reads the old layout.
:::

## Residency budgets

Residency is the question of which assets are in memory right now. The asset manager keeps three pools: asset memory on the :term[central processing unit]{id=processor} (CPU), memory for textures and memory for buffers on the :term[graphics processing unit]{id=gpu} (GPU). A pool has a budget, a limit in bytes. Over budget after an update, a pool loses its least recently requested assets, except those pinned, in use elsewhere or requested very recently, which can hold it over budget. Residency, eviction and pins are taught in [Residency](../assets/residency.md), and the upload limits in [Uploads](../assets/uploads.md).

The table below lists the fields of the :term[struct]{id=struct} `AssetResidencyBudgets` with their defaults. The default of a GPU pool is a share of the memory the graphics device reports as available to the program. On a machine with 8 GiB of available device memory, GPU textures get 4 GiB (50 %) and GPU buffers about 1.2 GiB (15 %). When no device exists, for example in a headless run, both pools are unlimited. The CPU pool is unlimited in every case.

Two words of the table need a meaning first. The finishing step runs on the :term[main thread]{id=main-thread}. It turns the bytes of a finished load into an asset the game can use and copies its GPU data to the device. Staging memory is memory that the processor writes and the GPU copies from during an upload.

This table is written by hand from `Strata/src/Strata/Asset/AssetResidency.h` and `AssetResidency.cpp`.

| Field | Default | What it limits |
| --- | --- | --- |
| `GpuTextures` | 50 % of the device's memory budget | Resident GPU texture memory |
| `GpuBuffers` | 15 % of the device's memory budget | Resident GPU buffer memory, mostly mesh data |
| `Cpu` | unlimited | Resident CPU memory of asset data |
| `InFlightBytes` | 128 MiB | Stored bytes of loads that are dispatched and not yet finalized |
| `UploadBytesPerFrame` | 16 MiB | GPU bytes that the finishing step uploads in one frame |
| `FinalizeMsPerFrame` | 4 ms | Main-thread time the finishing step may take in one frame |
| `UploadMsPerFrame` | 2 ms | Main-thread time of the frame's upload steps |
| `StagingBytes` | 32 MiB | Staging memory that texture and mesh uploads may hold at once |

The two times are limits on a frame of 16.7 ms at 60 :term[frames per second]{id=frame-rate}: 4 ms is 24 % of it and 2 ms is 12 %. A constant sets the size of one upload step, `c_AssetUploadStepBytes` in `Strata/src/Strata/Asset/Asset.h`. It is 4 MiB, so a texture of 16 MiB goes up in four steps, over as many frames if the frame budget allows only one step each.

Each default has a reason. The shares leave room for the renderer's own targets, which are not assets. The in-flight limit stops a fast disk from filling memory with loads that wait for the :term[main thread]{id=main-thread}. The staging budget is a high-water mark: the driver keeps freed staging memory committed for a while, so a process pays for the most it ever held.

The budgets of a running project change with the command `asset.setBudget`, which takes sizes in MB per pool and the other fields, and `reset: true` returns to the defaults. They last until the project closes, and an undo does not revert them. A :term[runtime]{id=runtime} game takes `--asset-budget-mb <megabytes>` for the GPU texture pool. The command parameters follow, generated from the command's own description; the full list of commands is in [Commands](../reference/commands.md) and the runtime's options in [Worlds and runtime](../reference/worlds-runtime.md).

::include{file="asset-budgets.md"}

:::caution
No asset settings section exists in a project's settings, and the generated text above says so. The budgets are the defaults of `AssetResidencyBudgets` (shares of the device's memory budget), and the commands change them for a session only, so a project cannot store a budget in its settings.
:::

## Statistics

The asset manager counts what it does. The struct `AssetManagerStats` holds the counts, the command `asset.stats` returns them, and the Streaming panel of the editor shows them. Read them as a health check: a large `FailedAssets` means loads break, a rising `Evictions` with a flat `LoadedAssets` means a budget is too small, and `EvictionChecks` shows what keeping the budgets costs. The statistics are taught in [Residency](../assets/residency.md).

This table is written by hand from `Strata/src/Strata/Asset/AssetManager.h`. A window is the last 120 frames (`c_StatsWindowFrames`).

| Field | Meaning |
| --- | --- |
| `RegisteredAssets`, `LoadedAssets`, `LoadingAssets`, `FailedAssets` | How many assets are known, loaded, queued or in flight, and failed |
| `PinnedAssets` | Assets with at least one pin |
| `LoadedMemory`, `Resident` | Resident bytes of all pools, and per pool |
| `Budgets` | The budgets in effect, as in the table above |
| `TotalLoadsCompleted`, `GetAssetCalls` | Loads finished, and requests for assets since the manager began |
| `Frame` | The manager's own frame counter |
| `QueuedLoads` | Loads waiting, by priority: high, normal and low |
| `InFlightLoads`, `OutstandingReads`, `InFlightBytes`, `InFlightBytesHighWater` | The loads being read or decoded, and the most bytes they ever held |
| `UploadedBytesLastFrame`, `UploadedBytesWindowMax` | GPU bytes uploaded in the last frame and at most in one frame of the window |
| `FinalizeMsLastFrame`, `FinalizeMsWindowMax` | Main-thread time of the finishing step, in the same two views |
| `UploadMsLastFrame`, `UploadMsWindowMax` | The part of that time spent in upload steps |
| `Evictions`, `EvictionChecks` | Assets dropped from memory, and resident assets that the drop examined |
| `Cancellations`, `StagingReleases` | Loads abandoned, and idle staging memory returned |
| `DependencyPrefetches`, `DependencyPrefetchesDropped` | Loads of referenced assets started early, and those dropped for lack of room |
| `PartialLoads`, `RangeReads`, `RangeReadsCompleted` | Loads of only a prefix of an asset, and reads of byte ranges |
| `Detail` | What the mip streaming extension did: levels raised and dropped, bytes streamed, textures below the level they need |

A worked reading: a scene shows 900 registered assets, 640 loaded, 12 loading and 0 failed, with 40 evictions and 9,000 eviction checks in the last minute. The loads work and nothing is broken. The ratio of 225 checks for each eviction shows that eviction examines many assets and may drop few of them. Most of the assets it looks at are pinned or were requested recently, so a pool stays over its budget: raise that budget or pin fewer assets.

## The Streaming panel

The Streaming panel of the editor lists the resident assets in a table, one row per asset. A click on a row reveals the asset in the Content Browser when it has a file. The table sorts by **GPU MB** first, with the largest on top. These columns are checked against `StrataEditor/src/Panels/StreamingPanel.cpp`.

| Column | What it shows |
| --- | --- |
| **Asset** | The asset's path, or its parent's path with the sub-asset key added |
| **Type** | The asset's type |
| **State** | Unloaded, Loading, Ready or Failed |
| **GPU MB** | GPU memory the asset holds, in MB with two decimals |
| **Mip** | For a streaming texture, the finest level resident and the level its views want, written as resident / wanted; level 0 is full resolution |
| **CPU MB** | CPU memory the asset holds, in MB with two decimals |
| **Last used** | Frames since the asset was last requested: "this frame", "never" or a count |
| **Pins** | How many pins hold the asset in memory |

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetTypes.h` and `AssetTypes.cpp`: the `AssetType` enum and the native extensions.
- `Strata/src/Strata/Asset/AssetImporters.cpp`: the native, audio clip and font importers and their versions.
- `Strata/src/Strata/Asset/TextureImporter.h`, `GltfImporter.h` and `ColorLookupImporter.h`: the other importers and their versions.
- `Strata/src/Strata/Animation/AnimationRegistration.cpp`, `Strata/src/Strata/Audio/AudioRegistration.cpp`, `Strata/src/Strata/Renderer/RendererRegistration.cpp`, `Strata/src/Strata/Scene/SceneRegistration.cpp` and `Strata/src/Strata/World/WorldRegistration.cpp`: the loaders each module registers.
- `Strata/src/Strata/Asset/AssetResidency.h` and `AssetResidency.cpp`: `AssetResidencyBudgets` and its defaults.
- `Strata/src/Strata/Asset/AssetManager.h`: `AssetManagerStats`.
- `Strata/src/Strata/Asset/AssetPack.h`: the pack format and its version.
- `Strata/src/Strata/Renderer/CookedTexture.h`, `Mesh.h` and `ColorLookup.h`: the cooked formats of textures, meshes and color lookups.
- `Strata/src/Strata/Asset/ImportRecordStore.h`: the import records file.
- `StrataEditor/src/Panels/StreamingPanel.cpp`: the Streaming panel's columns.
- `StrataEditor/src/Editor/EditorStreamingCommands.cpp`: the commands `asset.stats` and `asset.setBudget`.
- `StrataEditor/src/Editor/EditorAssetCommands.cpp`: the command `asset.types`.
- `StrataRuntime/src/RuntimeApplication.cpp`: the runtime option `--asset-budget-mb`.
- `tools/reference.py`: the :term[parser]{id=parser} that generates the tables of this page.
