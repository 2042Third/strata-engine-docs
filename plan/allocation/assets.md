# Allocation: assets

## `assets/what-is-an-asset` — What an asset is

**Covers.** The page starts from an experiment in the project of `start/first-game`: an image dropped into the
Content Browser can go on a material a moment later, yet a game exported from the project runs without that image
file. The page follows one file, the Showcase's `WeatheredSteel_arm.png`, from the project folder to a texture the GPU
samples (figure 453). The naive answer is to load the PNG itself when the game starts. It breaks four ways: decoding
is slow, the GPU wants mips and block-compressed data, a path breaks when the file moves, and thousands of loose files
ship slowly. Then the idea: an
asset is content the engine loads by handle. Its source file stays in `Assets/`. An importer cooks it into a stored
form: cooked bytes, or the source itself for the engine's own JSON documents (`.stscene`, `.stprefab`, `.stmat`,
`.stanimator`, `.stworld`). The editor caches stored forms per handle, and a game reads only stored forms, from a pack.
The approaches follow, each from the flaw of the one before: load sources at run time, cook ahead (Unreal's cooked
packages, Unity's Library folder, Godot's `.import` files), cook on first use; a table gives their costs.

Strata's choice: importers run only in the editor and in tools; there are 13 asset types; two managers share one base,
`EditorAssetManager` (files under `Assets/`) and `RuntimeAssetManager` (packs), so editor and game load the same way.
Then the pipeline at a glance as layers and seams (figure 491). The `Asset` layer includes only Core and no graphics
API. The `AssetPipeline` tooling layer holds the importers and the cooker, and games never link it. Modules register
what the asset layer cannot know: loaders, importers, built-in assets, manager extensions, and the mesh geometry reader
that lets physics read a mesh's triangles without the renderer. Where the choice stops: a game cannot import, and
models come only as glTF (one sentence and a link). Common mistakes: thinking the PNG ships, editing cache files,
including renderer headers in `Asset/`. Exercises: an image of the first game followed from its file to its `.meta`,
its cache file and the exported game's folder, which holds no PNG; a search for where the renderer registers its loaders
and where tools register importers; what loading sources at run time would cost a game. At the end the reader can name
every stage between a source file and a GPU resource, and the page of this part that teaches it.

**Leaves out.**

- How a handle and its `.meta` file are made → `assets/handles-meta`
- How imports run, are cached and are cancelled → `assets/importing`
- Loading at run time without stalling a frame → `assets/loading`
- The pack's format, and the export as a whole → `assets/packs-export`, `worlds/export`
- Registries in general, dependency inversion and the layer table → `core/layers-registries`
- Bringing assets into a game, for game makers → `make/assets`

**Fit.** `fits`: about 3,650 words against M (3,000). The idea of a stored form with the table of approaches, the
registries and seams (one section and figure 491, since their home is `core/layers-registries`) and the three exercises
take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:246` | concept | home | Sources and stored forms; why engines cook; the approaches and their table; the usual mistakes |
| `assets:260` | concept | home | Asset types and the registry pattern: modules register what the asset layer cannot know |
| `assets:40` | feature | home | The five native extensions, stored as their JSON source |
| `assets:57` | feature | home | `MeshGeometryRegistry`: physics reads a mesh's triangles without the renderer's `Mesh`, the seam's example |
| `assets:59` | feature | home | The `Asset` layer (Core only) and the `AssetPipeline` tooling layer |
| `assets:453` | figure | home | The whole pipeline, editor and game, redrawn from the ASCII figure of `Docs/Architecture.md` |
| `assets:491` | figure | home | The layer seam: the asset layer's interfaces, implemented above it |
| `assets:637` | term | home | Asset |
| `assets:640-643` | term | home | Source file, stored form, import and importer, cook |
| `assets:658-659` | term | home | Engine-native asset, asset manager |
| `audio-input:638` | term | home | Cooked asset, in general (an audio clip's `STAU` header is one example) |
| `new:23` | hands-on | home | Exercises (D27): an image of the first game's project followed from its file to its `.meta`, its cache file named by its handle and the exported game's folder, which holds no PNG (done); a search for where the renderer registers its loaders and where tools register importers, and which programs link each (trace); what loading sources at run time would cost a game (design). Evidence: `Strata/src/Strata/Asset/EditorAssetManager.cpp:707` (the cache file `<handle>.bin`); `Strata/src/Strata/Renderer/RendererRegistration.cpp:81-118`; `Strata/src/Strata/Asset/AssetImporters.cpp:159-177` |
| `assets:39` | feature | use | The 13 asset types, named (the enum is `assets/handles-meta`'s) |
| `assets:54` | feature | use | Loaders are registered by the module that owns a type |
| `assets:55` | feature | use | A shipped game contains no importer |
| `assets:58` | feature | use | The upload seam, in one sentence |
| `assets:78` | feature | use | `EditorAssetManager`, at a glance |
| `assets:79` | feature | use | `RuntimeAssetManager`, at a glance |
| `render-core:112` | feature | use | The renderer's side of the mesh geometry seam |
| `physics:61` | feature | use | The physics side of the seam (`AssetMeshProvider`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Files, bytes and JSON | `basics/data-formats` | must |
| Handles instead of pointers; UUIDs as stable identities | `world/ecs` | must |
| Registries that open and accept (the component and settings registries then freeze; the asset registries stay open); the composition root; dependency inversion | `core/layers-registries` | must |
| The layer table, and the tooling layers that games never link | `core/layers-registries` | must |
| What textures and meshes are to a GPU | `gpu/how-a-gpu-frame-works` | helps |
| Scene documents as files | `world/serialization` | helps |
| Prefabs and models as entity templates | `world/prefabs` | helps |
| The editor's Content Browser and Inspector, as the first game shows them | `start/first-game` | helps |
| What an exported game is | `worlds/export` | helps |
| Engine services | `core/engine-modules` | helps |

## `assets/handles-meta` — Handles, `.meta` files and sub-assets

**Covers.** The job: every asset gets a name that survives renames, moves, re-imports and other machines. The problem
takes one paragraph that links `assets/what-is-an-asset` and `world/ecs`, with a short table of the approaches: paths,
IDs in a sidecar file (Unity's `.meta`), IDs inside the asset (Unreal), content hashes. The map: `AssetTypes.h` (the
handle and the types), `AssetRegistration` (reading and writing `.meta` files, finding duplicates), `AssetImporter`
(derived handles), `BuiltinAssets`, `AssetMetadata`. The contract: an `AssetHandle` is a `UUID`, a random, non-zero
64-bit number written as 16 upper-case hex digits. The `.meta` sidecar holds the handle, the type and the import
settings, and it is committed with its file. An invalid `.meta` is reported and never overwritten. The type enum is
append only, because packs and import records store its numbers. Handles 1 to 255 belong to the built-in assets. A toy
of about 40 lines keeps a path-to-handle table from sidecar files and derives a child's handle by hashing.

The real code, in the order a file meets it: the handle alias and the type enum; a real `.meta` (the Showcase's
`WeatheredSteel_arm.png.meta`); `AssetMetadata` (path, parent, sub-asset key, stored size); sub-assets and their keys
(`Mesh/0`, `Material/2`, `Texture/<image>/<usage>/<sampler>`, `Skeleton`, `Animation/<name>`); `DeriveSubAssetHandle`
(FNV-1a of the key, combined with the parent, moved out of 0 to 255, so it is the same on every machine); the built-in
assets (eight primitive meshes and the default material, whose objects come from factories the renderer registers, and
which no pack can replace); and files copied with their `.meta`, which share a handle until the scan gives the copies
new ones. Four rules end as why-boxes: by handle, never by path at run time (and why `Assets::Find` needs
`AlwaysInclude`); move, rename and delete through the editor; never overwrite an invalid `.meta`; built-in handles are
reserved. Then the alternatives, the tests (`Asset.Registration`) and changing it safely (append a type; never change
the derivation, which would break every reference to a sub-asset). The "trace it yourself" exercise computes a model's
material handle from the model's handle and the key, and finds the cache file of that name in `.strata/Cache`.

**Leaves out.**

- Handles and UUIDs in general, and why handles beat pointers → `world/ecs`
- What an import writes into the cache and the record → `assets/importing`
- Moving, deleting and restoring asset files, and the trash → `editor/trash-references`
- The handles of world cells, derived the same way → `worlds/grids`

**Fit.** `fits`: about 4,605 words against L (5,000). Three excerpts and the quote of `UUID.h`, the contract and four
rules with their why-boxes take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:253` | concept | home | Identity by handle, not by path: the approaches, Strata's choice and the mistakes |
| `assets:38` | feature | home | `AssetHandle` is `UUID` |
| `assets:39` | feature | home | The 13 types; their numbers are stored in files, so the enum is append only |
| `assets:43-48` | feature | home | `AssetMetadata`, `.meta` sidecars, sub-assets and their keys, derived handles, built-in assets, duplicate handles |
| `assets:375` | code | home | `Strata/src/Strata/Asset/AssetTypes.h:11-31`: the handle alias and the type enum with its "append only" note |
| `assets:378` | code | home | `Samples/Showcase/Assets/Generated/Props/WeatheredSteel_arm.png.meta:1-20`: a real sidecar with its import settings |
| `assets:380` | code | home | `Strata/src/Strata/Asset/AssetImporter.cpp:264-271`: `DeriveSubAssetHandle`, hashing that skips the reserved range |
| `assets:456` | figure | home | A file, its `.meta`, its cache file named by the handle, sub-assets with derived handles, built-ins 1-255 |
| `assets:520` | rule | home | By handle, never by path at run time |
| `assets:522` | rule | home | Move, rename and delete through the editor, or move the `.meta` along |
| `assets:524` | rule | home | Never overwrite an invalid `.meta`: it may hold a merge conflict |
| `assets:567` | rule | home | Built-in handles are reserved |
| `assets:638-639` | term | home | Asset handle, asset type |
| `assets:644` | term | home | `.meta` file, sidecar |
| `assets:654-656` | term | home | Sub-asset, derived handle, built-in asset |
| `animation:586` | term | home | Sub-asset, as the animation part words it (a model's skeleton and clips) |
| `editor-core:687` | term | home | `.meta` file, as the editor part words it |
| `new:1` | erratum | home | The assets inventory places `ReadAssetMeta`, `WriteAssetMeta` and `FindDuplicateHandles` at `AssetRegistration.h:283-304` and `:319-330`, and the scan's types at `:233-281`, but the header has 121 lines; writers cite the places below. Evidence: `Strata/src/Strata/Asset/AssetRegistration.h:72-93` (the `.meta` status, reader and writer), `:113-120` (`FindDuplicateHandles`), `:23-70` (scan phases, options, slices) |
| `new:24` | hands-on | home | Trace it yourself (D27): a model's material handle computed from the model's handle and the key `Material/0` as `DeriveSubAssetHandle` does, then the cache file of that name found in `.strata/Cache`. Evidence: `Strata/src/Strata/Asset/AssetImporter.cpp:264-271`; `Strata/src/Strata/Asset/EditorAssetManager.cpp:707` |
| `assets:377` | code | use | `Strata/src/Strata/Core/UUID.h:13-33`, quoted for the null value and the text form; its home is `world/ecs` |
| `assets:72` | feature | use | Built-in assets are memory assets, never evicted |
| `assets:141` | feature | use | Moves and the trash keep handles (taught in `editor/trash-references`) |
| `foundation:154` | feature | use | `UUID` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an asset, a source file and a stored form are | `assets/what-is-an-asset` | must |
| Handles instead of pointers; UUIDs as 64-bit values | `world/ecs` | must |
| Hashes (FNV-1a), and numbers written in hexadecimal | `basics/data-formats` | must |
| JSON | `basics/data-formats` | must |
| Scoped enums with a fixed underlying type | `basics/cpp-modern` | must |
| Writing a file atomically | `core/files` | helps |
| Git: committing files, merge conflicts | `basics/git` | helps |
| What an import produces, and import settings | `assets/importing` | helps |
| The trash, and undoing a delete | `editor/trash-references` | helps |
| Pruned exports and `AlwaysInclude` | `assets/packs-export` | helps |
| Memory assets, which are never evicted | `assets/loading` | helps |
| Eviction | `assets/residency` | helps |

## `assets/importing` — Importing: from source files to engine data

**Covers.** The job: keep every asset's stored form current with its source, its settings and the files it reads. It
works in the background, never imports again what is current, and never stalls the editor. The problem is that of an
incremental build system, with its approaches in a table: file times (make), content hashes (Bazel), import records.
The map (figure 472): the scan job (walk the folder, prepare files in batches of 256, apply them in slices of about
1 ms), the import jobs and their admission, `BackgroundWork` (all that jobs share), `ImportRecordStore`, the cache
folder, and the main thread's `Update`. The contract of an importer (`AssetImporter`): type, extensions, version,
`StoresSourceDirectly`, `Import`, default settings and their properties, inactive reasons, a memory estimate, external
files. It reads only through `ReadImportSource` and `ReadImportDependency`, checks `IsCancelled` every few
milliseconds, and never touches files on the main thread. A toy of about 60 lines caches imports with a record of the
importer's version, a settings hash and the source's size and time.

The real code, in the order a file flows: the registry, opened only by `RegisterAssetPipeline` for tools; the simplest
importer, `NativeAssetImporter`, which checks a document with its loader and stores the source; the other importers in
one table (native, texture, glTF, audio, font, color lookup, with extensions and stored forms; texture and glTF have
their own pages, and the audio importer is taught with audio clips); the scan; the cache (`.strata/Cache/<HANDLE>.bin`)
and the record store (one append-only log, a CRC-32C on each line); cache validity (`GetRecordableTime` and "racily
clean" times, `IsFileCurrent`, the head of `LoadCurrentImport`; figure 474), and beside it the content stamp
(`GetContentStamp`: the source file's size and time, the import settings, the importer's version and whether the import
succeeded, hashed into a fingerprint that lasts across sessions, which thumbnails, the world cook and asset bounds
compare); confined reads, which record every file read, even a missing one; settings as
properties (`ImportSettingsBuilder`, checks that refuse rather than clamp, inactive reasons) and the Asset Inspector
that draws them (figure 496); publication: staged cache files renamed into place and the record set, together, under
the exclusive file lock, after a last look at the cancel flag; background imports and hot reload (the file watcher,
`ReimportAssetInBackground`, and `ReloadAsset`, which serves the previous version until the new one is ready);
cancellation; import memory admission; external imports, rolled back when they fail; failures shown to the person.
Five rules end as why-boxes, the version bump among them: an importer's version is a key of cache validity. Then the
alternatives, the tests (`Asset.Editor`, `Asset.ImportRecords`, `Asset.ImportSettings`, `Asset.ImportCancellation`,
`Asset.ImportAdmission`), changing it safely (bump `GetVersion`, record dependencies, add a setting), and what went wrong
before: closing a project while 17 imports ran took 5 to 12 seconds. Exercises: read a `.meta` and its line in
`ImportRecords.log`, change a setting and find the new line; trace it yourself: a breakpoint in `LoadCurrentImport` while
a project opens shows why each asset is or is not imported again. At the end the reader can say why an asset is or is
not imported again, and can write an importer that the cache, cancellation and hot reload treat right.

**Leaves out.**

- The texture importer and its cooker → `assets/texture-cooking`
- The glTF importer → `assets/models-gltf`
- The audio importer and the stored form of audio clips → `audio/clips-voices-sources`
- The color lookup importer and the `.cube` format → `image/grading`
- Why write-ahead ordering keeps a crash from corrupting the project → `assets/robustness`
- Hot reload of scripts, the other meaning of the words → `scripting/hot-reload`
- The editor's folder index and the Content Browser's lists → `editor-ui/lists`
- Background saves of the engine's own documents → `editor/saving`
- Importing as a game maker does it → `make/assets`

**Fit.** `fits`: about 7,135 words against XL (8,000), one page in sections. Five excerpts, cache validity with figure
474 and the content stamp beside it, and five rules take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:266` | concept | home | Importers, settings and versions as an incremental build system |
| `assets:363` | concept | home | Hot reload of assets: the watcher, a background import, the old version until the new one is ready |
| `assets:55` | feature | home | `AssetImporterRegistry` and `RegisterAssetPipeline`: only tools register importers |
| `assets:73` | feature | home | `ReloadAsset`: the previous version serves until the new one is Ready; old loads are discarded |
| `assets:78` | feature | home | `EditorAssetManager`: every file under `Assets/` with a known importer is an asset |
| `assets:130-140` | feature | home | Scan, import cache, record store, cache validity, running an import, confined reads, settings, background imports and hot reload, cancellation, memory admission, external imports |
| `assets:145` | feature | home | The content stamp (`GetContentStamp`), beside cache validity: a fingerprint that lasts across sessions, hashed from the source file's size and time, the import settings, the importer's version and whether the import succeeded (a sub-asset's is its file's); thumbnails, the world cook and asset bounds compare it to know when their data on disk is stale; about 150 words |
| `assets:144` | feature | home | `TakeImportFailures`: failures nobody watched, shown to the person |
| `assets:146` | feature | home | Shared file lock for background reads, exclusive for saves and moves |
| `assets:152` | feature | home | The native importer |
| `assets:160` | feature | home | The font importer, as a row of the importers table |
| `assets:384` | code | home | `Strata/src/Strata/Asset/AssetImporters.cpp:35-80`: `NativeAssetImporter`, the importer interface at its simplest |
| `assets:389` | code | home | `Strata/src/Strata/Asset/AssetImporter.cpp:312-342`: `ReadImportDependency`, confined reads that record their file |
| `assets:391` | code | home | `Strata/src/Strata/Asset/EditorAssetManager.cpp:162-193`: `GetRecordableTime` and `IsFileCurrent` |
| `assets:393` | code | home | `Strata/src/Strata/Asset/EditorAssetManager.cpp:1959-2006`: the head of `LoadCurrentImport`, what makes an import current |
| `assets:395` | code | home | `Strata/src/Strata/Asset/EditorAssetManager.cpp:2147-2235`: staged cache files, then the rename and the record under the exclusive lock |
| `assets:472` | figure | home | The import pipeline in the editor: scan phases, background imports, the main thread's apply |
| `assets:474` | figure | home | The cache validity decision tree |
| `assets:496` | figure | home | The Content Browser with an import running; a texture's settings in the Asset Inspector with an inactive `FlipGreen` |
| `assets:526` | rule | home | Bump `GetVersion()` whenever an importer's output changes: the version is a key of cache validity, so a stale cache would look current (textures: `TextureImporter` and `GltfImporter` both cook them) |
| `assets:529` | rule | home | Importers read other files only through `ReadImportDependency` |
| `assets:531` | rule | home | Long importers check `ImportContext::IsCancelled` every few milliseconds |
| `assets:533` | rule | home | Nothing in the editor waits for a background import; no file work on the main thread |
| `assets:535` | rule | home | Cache files are renamed into place before their record is set, under the exclusive lock |
| `assets:579` | hands-on | home | Read a `.meta` and a cache record; change a setting and see a new record |
| `assets:645-650` | term | home | Import settings, importer version, import cache, import record, import record store, dependency (import) |
| `assets:672` | term | home | Hot reload (of assets) |
| `assets:728-730` | term | home | Import memory admission, cancellation flag, racily clean |
| `assets:732` | term | home | File watcher |
| `editor-core:736`, `worlds-runtime:535` | term | home | Content stamp: one glossary entry with `assets:145`, defined as the fingerprint of an asset's stored form, built from its source file's size and time, its import settings, its importer's version and whether its import succeeded (the worlds part's "identifier of a document's content" is wrong) |
| `editor-core:740` | term | home | Asset scan, one glossary entry with the scan of `assets:130`: the background registration of a project's assets when it opens |
| `new:25` | erratum | home | The assets inventory places the import record store at `ImportRecordStore.h:85-163`, but the header has 111 lines; writers cite the places below. Evidence: `Strata/src/Strata/Asset/ImportRecordStore.h:31-50` (the design note), `:51-109` (the class) |
| `new:26` | hands-on | home | Trace it yourself (D27): a breakpoint in `LoadCurrentImport` while a project opens shows, for each asset, which key of cache validity made it current or imports it again. Evidence: `Strata/src/Strata/Asset/EditorAssetManager.cpp:1959-2006`; `:162-193` (`IsFileCurrent`) |
| `assets:359` | concept | use | Cancellation keeps the editor responsive; taught in `assets/robustness` |
| `assets:159` | feature | use | The audio importer, one row of the importers table (taught in `audio/clips-voices-sources`) |
| `assets:142` | feature | use | The folder index, in one sentence (taught in `editor-ui/lists`) |
| `assets:161` | feature | use | The color lookup importer, one row of the importers table (taught in `image/grading`) |
| `foundation:125` | feature | use | `FileWatcher` reports changed files |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an asset, a source file and a stored form are | `assets/what-is-an-asset` | must |
| Handles, `.meta` files and sub-assets | `assets/handles-meta` | must |
| The I/O and background pools of the job system; the main thread's queue | `core/jobs` | must |
| Atomic writes, file locks, symbolic links, files you can trust | `core/files` | must |
| Properties, and the reflection that draws them | `world/reflection` | must |
| Mutexes, shared and exclusive locks, atomic flags | `basics/threads` | must |
| Hashes and CRC checksums | `basics/data-formats` | must |
| Virtual functions and interfaces | `basics/cpp-classes` | must |
| Incremental builds, and how a build tool compares file times | `basics/build` | helps |
| Loaders, and how a stored form becomes an object | `assets/loading` | helps |
| Hot reload of scripts, the other meaning | `scripting/hot-reload` | helps |
| The Content Browser and the Inspector | `start/first-game` | helps |

## `assets/textures` — Textures for the GPU: mips, color spaces, block compression

**Covers.** The problem as the reader meets it: one 4096 by 4096 photo stored as RGBA8 holds 64 MiB, its mips add a
third, and a scene has hundreds of textures; far away the texture shimmers; a normal map imported as a color looks
wrong. The naive answer, RGBA8 at full size sampled at level 0, breaks on memory, on bandwidth and on aliasing. The idea
comes in three short parts, because `basics/signals` and `basics/color` teach the mathematics: mips as prefiltered
levels for a third more memory; color spaces in textures (sRGB color, filtered in linear space; linear data such as
roughness; HDR values above 1, in RGBA16F); and block compression, which stores 4x4 texels in 8 or 16 bytes at a fixed
rate, so the GPU can read any block directly. The approaches follow: uncompressed, the BC family on desktops, ASTC and
ETC on phones, and transcoding at load time (Basis Universal), with a table of bits per texel, quality, encoding cost
and who uses each.

A BC1 block is opened up (figure 478): two endpoints and a 2-bit index per texel, so the colors of one block lie on one
line through RGB space. That is why data with independent channels needs BC7, and why normal maps use BC5 (X and Y in
two channels, Z rebuilt from them). BC7's own parts are named here and taught with the encoder. Strata's choice is one
table: color BC7 (BC1 for opaque color at Fast), normal maps BC5, one-channel data BC4, other data BC7, HDR RGBA16F,
and uncompressed formats when asked; the code is `assets/texture-cooking`'s. What the choice cannot do: there is no
BC6H, so an HDR texture takes 8 bytes a texel, and there are no phone formats, because Strata runs on desktops only.
Common mistakes: sizes computed from bytes per pixel, a normal map imported as Color, the green channel of DirectX
normal maps against OpenGL ones. Figure 498 shows one texture as Color, NormalMap and Data, and at High against Fast.
Exercises: the stored size of a 4096 by 4096 texture with its mips worked out by hand as RGBA8, BC1, BC7 and RGBA16F,
then compared with the cache files that imports at those settings write; one normal map imported as Color and as
NormalMap and compared in the Scene view; four colors of one block that do not lie on a line, and what BC1 gives up for
them. At the end the reader can choose the usage and quality of any texture and say what each choice costs.

**Leaves out.**

- How Strata's importer chooses formats, cooks mips and encodes BC7 → `assets/texture-cooking`
- Sampling, aliasing and prefiltering as mathematics → `basics/signals`
- The sRGB transfer function and the half-float range → `basics/color`
- Normal maps in tangent space, and how the shader reads them → `light/materials`, `light/material-data`
- Loading only some of a texture's levels → `draw/mip-streaming`
- Import settings as a game maker uses them → `make/assets`, `make/materials`

**Fit.** `fits`: about 3,800 words against M (3,000). The idea in three short parts, the BC1 block of figure 478 and the
table of formats take the most words, then the three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:273` | concept | home | Texture data for GPUs: mips, color spaces, block compression; the BC family; why data needs BC7 |
| `assets:478` | figure | home | BC block anatomy: a 4x4 block, BC1's endpoints and indices, why data channels fail in BC1 |
| `assets:498` | figure | home | One texture at Usage Color, NormalMap and Data, and at High against Fast, zoomed |
| `assets:702` | term | home | Mip, mip level, mip chain |
| `assets:710` | term | home | Block compression (BC1-BC7) |
| `assets:713-715` | term | home | Linear data, normal map, HDR (RGBA16F) |
| `render-image:682` | term | home | Mip chain and pyramid (the bloom's pyramid links here) |
| `new:27` | hands-on | home | Exercises (D27): the stored size of a 4096 by 4096 texture with its mips worked out by hand as RGBA8, BC1, BC7 and RGBA16F, then compared with the cache files that imports at those settings write (done); one normal map imported as Color and as NormalMap and compared in the Scene view (editor task); four colors of one block that do not lie on a line, and what BC1 gives up for them (design). Evidence: `Strata/src/Strata/Renderer/TextureFormat.cpp:53-65` (`GetMipByteSize`); `Strata/src/Strata/Asset/EditorAssetManager.cpp:707` (the cache file `<handle>.bin`) |
| `assets:154` | feature | use | Strata's format per usage, as a table (the code is `assets/texture-cooking`'s) |
| `assets:165` | feature | use | Normal maps read as X and Y with Z rebuilt, in one sentence (taught in `light/material-data`) |
| `assets:547` | rule | use | Sizes come from `GetMipByteSize` (the box is `assets/texture-cooking`'s) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sampling, aliasing and mip prefiltering | `basics/signals` | must |
| Linear and sRGB values, the sRGB transfer function, the half-float range | `basics/color` | must |
| Textures, texels, sampling and filtering on a GPU; memory bandwidth | `gpu/how-a-gpu-frame-works` | must |
| Bits, bytes, and numbers packed into bits | `basics/numbers` | must |
| Vectors: length and normalizing | `basics/math-vectors` | must |
| What an asset and a stored form are | `assets/what-is-an-asset` | helps |
| Normal maps as directions in tangent space | `light/materials` | helps |

## `assets/texture-cooking` — Cooking textures: Strata's importer, mips and BC7 encoder

**Covers.** The job: turn an image file into an `STTX` cooked texture that the GPU samples and the streamer reads by
byte range, as fast as a background job allows and exactly as the settings say. The problem takes one paragraph that
links `assets/textures`. The map: `TextureImporter` (settings, defaults, `Decode`, `ChooseFormat`), `TextureCooker`
(mips), `BC7Encoder`, `HDRSun` (behind the RemoveSun setting), `CookedTexture` (`STTX`), `TextureFormat`
(`GetMipByteSize`) and `BlockCompression` (decoding for devices without BC). The contract: ten settings, four of which
grey out with an inactive reason (Compression and Quality for HDR textures, which stay 16-bit float; Quality also when
the texture is uncompressed or not color, since it only chooses how block compression encodes color; FlipGreen except on
normal maps; RemoveSun except on HDR maps); defaults guessed from tokens of the file name (`_nor`, `_rough`; a `dx`
token turns `FlipGreen` on); the image limits (a longest side of at most 16,384 texels, a larger image scaled down with
its aspect ratio kept and `MaxSize` 0 meaning that limit, at most 15 levels; only Radiance HDR files keep more than 8
bits a channel, so a 16-bit PNG is decoded to 8; a GIF gives its first frame); one format per usage; levels written
smallest first, each 16-byte aligned; sizes only from `GetMipByteSize`; cooked bytes read only through
`ParseCookedTexture`. A change of output bumps the version of `TextureImporter` and of `GltfImporter`, which cooks a
model's images the same way (the rule's box is `assets/importing`'s). A toy of about 50 lines builds a box-filtered mip
chain and a size calculator; the real code then shows where Strata differs.

The real code, in the order data flows: the settings and their defaults (version 5); `ChooseFormat`, with its comment
on why data channels need BC7; `CookLevels`, which encodes a level and then filters the next, holding two levels at a
time (a Mitchell filter, sRGB in linear space, alpha weighting, edges by wrap mode, normal maps renormalized), and the
HDR path (a box filter, values clamped to the half-float range, NaN and negative values dropped); the BC7 encoder (a
block's modes, partitions, endpoints, p-bits and indices; endpoints along the colors' principal axis, least-squares
refits, mode screening; High searches every mode, Fast modes 6 and 5; the page explains the fit itself where the
encoder uses it, in a `:::derivation` box of about 200 words: the mean of the block's colors, their spread along a
direction, the direction of the greatest spread, found by power iterations, as the line the colors are fitted to, and
least squares as the endpoints that bring the indexed colors closest to the texels; the further reading names a source
on least squares and eigenvectors, such as Strang's *Introduction to Linear Algebra*); the RemoveSun setting of HDR
skies (what `HDRSun` finds and paints out is `light/sky`'s); the `STTX` v2 layout (figure 476: header, mip table, name,
then the levels smallest first, so the mip tail is one range after the header; version 1 is still read) and
`ComputeCookedTextureLayout`; `GetMipByteSize` (a 2x2 BC7 level takes one whole 16-byte block); `ParseCookedTexture`;
the decoding of BC data on the loading worker for devices that cannot sample it; and the warning when a texture's usage
disagrees with its material slot. What Strata does not do here: BC6H, and EXR import. Then the alternatives, the tests
(`Asset.TextureImport`, `Asset.HDRSun`, the encoder's tests), and changing it safely (the version bump of two
importers). Exercises: a cooked-texture inspector; Fast against High on a large albedo; trace it yourself: a search
finds where the file name's tokens choose the defaults, then a DirectX normal map is fixed by its name; BC7's PSNR at
High and at Fast.

**Leaves out.**

- The general problem and the families of formats → `assets/textures`
- What `HDRSun` finds in a sky, and Extract Sun → `light/sky`
- How the shader reads normal maps and the grayscale bit → `light/material-data`
- The resident mip tail and the reads of finer levels → `draw/mip-streaming`
- Uploading the levels to the GPU in steps → `assets/uploads`
- The textures inside a glTF model → `assets/models-gltf`

**Fit.** `fits`: about 6,315 words against L (5,000). The BC7 encoder with its derivation box, the stored form with
figure 476, four excerpts and four exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:281` | concept | home | File layout for streaming: the smallest level first, so the tail is one read |
| `assets:153-156` | feature | home | The texture importer (settings, name tokens, version 5), the format choice, the cooker, the BC7 encoder |
| `assets:162-164` | feature | home | `STTX` v2, block sizes, the BC decode fallback |
| `render-core:109` | feature | home | The device's block-compression flag, which sends loaders to the decode fallback |
| `assets:166` | feature | home | Usage warnings with their `asset.setImportSettings` fix |
| `assets:398` | code | home | `Strata/src/Strata/Asset/TextureImporter.cpp:641-666`: `ChooseFormat`, with the comment on data channels |
| `assets:400` | code | home | `Strata/src/Strata/Asset/TextureCooker.cpp:275-309`: `CookLevels`, encode then filter, two levels held |
| `assets:402` | code | home | `Strata/src/Strata/Renderer/TextureFormat.cpp:53-65`: `GetMipByteSize` and `GetBlockRowByteSize`, rounding to whole blocks |
| `assets:404` | code | home | `Strata/src/Strata/Renderer/CookedTexture.cpp:339-360`: `ComputeCookedTextureLayout`, with the format comment of `CookedTexture.h:17-31` |
| `assets:476` | figure | home | The cooked texture layout: header, table, name, levels smallest first, the tail as the first read |
| `assets:547` | rule | home | Texture sizes come from `GetMipByteSize`, never bytes per pixel |
| `assets:550` | rule | home | Read cooked textures through `ParseCookedTexture` |
| `assets:582` | hands-on | home | A cooked-texture inspector: format, levels, offsets, the smallest-first layout |
| `assets:608` | hands-on | home | BC7's PSNR at High and at Fast, in the encoder's tests |
| `assets:615` | hands-on | home | Trace it yourself (D27): a search finds where the file name's tokens choose the defaults (`GetNameTokens`, `GetDefaults`); then a normal map is fixed by its name: tokens, `FlipGreen`, the usage warning |
| `assets:617` | hands-on | home | Fast against High: look, stored size, import time |
| `assets:711` | term | home | Endpoints, indices, partitions, p-bits and modes (BC7) |
| `assets:716-718` | term | home | Mitchell and box filters, alpha weighting, `STTX` |
| `new:2` | not-done | home | No BC6H: HDR textures are stored as RGBA16F. Evidence: `Docs/Releases/0.7.0.md:403`; `Docs/Roadmap.md:1714` |
| `new:3` | not-done | home | No EXR import: the importer reads `.png`, `.jpg`, `.jpeg`, `.tga`, `.bmp`, `.psd`, `.gif` and `.hdr`. Evidence: `Strata/src/Strata/Asset/TextureImporter.cpp:348`; `Docs/Roadmap.md:949` |
| `new:28` | feature | home | The image limits, about 80 words: the longest side is at most 16,384 texels, a larger image is scaled down with its aspect ratio kept, `MaxSize` 0 means this limit, and a cooked texture has at most 15 levels; only Radiance HDR files keep more than 8 bits a channel (a 16-bit PNG is decoded to 8 bits); a GIF imports its first frame. Evidence: `Strata/src/Strata/Asset/TextureImporter.h:59`, `:80`, `:84`; `Strata/src/Strata/Asset/TextureImporter.cpp:111-120`, `:529`, `:575`; `Strata/src/Strata/Renderer/CookedTexture.h:35-36` |
| `assets:526` | rule | use | The version bump of `TextureImporter` and `GltfImporter`, which both cook textures (the rule's box is `assets/importing`'s) |
| `assets:157` | feature | use | What `HDRSun` does, in one sentence (taught in `light/sky`) |
| `assets:165` | feature | use | The grayscale bit and the XY normal decode, named (taught in `light/material-data`) |
| `render-direct:160` | feature | use | Extract Sun and Remove Sun, the lighting side |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Mips, color spaces, block compression and the BC formats | `assets/textures` | must |
| Importers, settings, inactive reasons and versions | `assets/importing` | must |
| Filters and kernels for resampling | `basics/signals` | must |
| The sRGB transfer function; the half-float range | `basics/color` | must |
| Shifts and masks; integer division that rounds up; logarithms | `basics/numbers` | must |
| Vectors, dot products, normalizing | `basics/math-vectors` | must |
| `ParallelFor` and the job system | `core/jobs` | must |
| An HDR sky, and its sun as a light | `light/sky` | helps |
| The resident mip tail, and finer levels read by range | `draw/mip-streaming` | helps |

## `assets/models-gltf` — Models and the glTF importer

**Covers.** The job: turn a `.gltf` or `.glb` file into a model, an entity template that instantiates into scenes, and
its sub-assets: meshes with levels of detail and skins, materials, textures, a skeleton and clips. The problem takes one
paragraph: the interchange formats (glTF, FBX, OBJ, USD), and why Strata reads glTF only (it is open, its materials are
PBR, and it shares Strata's conventions: right-handed, +Y up, counter-clockwise front faces, meters). The map:
`GltfImporter` (cgltf parses, meshoptimizer decodes and simplifies), `MeshUtils` (indices and levels of detail),
`TextureImporter::Decode` (embedded and external images), `Model` (the Scene module's template), `Mesh`'s cooked form,
the material document, and the skeleton and clips of the animation part. The contract: the sub-asset keys; the settings
(Scale, GenerateLODs, LODCount, OptimizeMeshes, ImportMaterials, BaseColorFactorsAreSRGB, ImportCameras, ImportLights,
MaxTextureSize, TextureCompression, TextureQuality) and their inactive reasons; external files only inside the asset
directory, read through `ReadImportDependency`, so a changed image imports its model again; and a table of what is
supported and what is not, with the warning each gives (the Asset tab and `importWarnings` of `asset.info` show them):
the supported extensions (lights, emissive strength, unlit, clear coat, transmission, volume, IOR, texture transform,
mesh quantization, meshopt compression); a required extension outside that list fails the import; skipped or clamped
with a warning are primitives with only Draco data, KTX2 and WebP images, textures on a second UV set, texture
rotation, different wrap modes for the two axes, `EXT_mesh_gpu_instancing`, skin influences beyond the four strongest,
an IOR above 3, morph targets, vertex colors, extra scenes and specular-glossiness materials. A toy of about 50 lines
reads a one-triangle glTF (its JSON, a base64 buffer, an accessor) into positions and indices.

The real code: the header's description and its version history (11 at the pin; `Docs/Architecture.md` still says 9);
`Run`, the order of an import with its cancel checks (materials, skeleton, meshes, animations, the model);
`ImportMaterial` (factors, alpha modes, one texture sub-asset per image, usage and sampler, the clear coat and
transmission extensions, `BaseColorFactorsAreSRGB`); `ImportMesh` (the scale baked into positions before bounds and
levels of detail; what it makes when a file lacks vertex data: missing normals become flat face normals on unwelded
triangles, missing tangents with UVs become exact per-corner MikkTSpace tangents, which split vertices on UV seams and
mirror lines, and without UVs any tangent perpendicular to the normal is used; levels with their errors, where a
paragraph of about 150 words says what simplification keeps: `MeshUtils::GenerateLODs` calls meshoptimizer's
`meshopt_simplifyWithAttributes`, which removes edges while the error stays under `c_MaxLODError` (0.02 of the mesh's
extent), weighs normals and texture coordinates so that seams stay closed, keeps open borders in place, and records each
level's error; the further reading names Garland and Heckbert's paper on quadric error metrics, which the simplifier
cites); `BuildModel` (the root keeps scale 1; an animator on the root); and the cooked mesh form (`STMH` version 3). The
references and bounds the importer records are named and linked to `assets/references`. What Strata does not do: OBJ
and FBX. Then the alternatives, the tests (`Asset.Gltf`), and changing it safely (bump the version; derive new
sub-assets' handles with `DeriveSubAssetHandle`; never change a key). Exercises: import a glTF with its textures, read
its sub-assets and their keys, and place it; trace it yourself: a breakpoint in `ImportMesh` on a model without tangents
shows which branch makes them.

**Leaves out.**

- Skeletons, skins and clips as the animation system builds them → `animation/importing`
- Meshes on the GPU and the geometry pool → `gpu/geometry-pool`
- Choosing a level of detail at draw time → `draw/lod`
- Models and prefabs as entity templates → `world/prefabs`
- PBR material fields and what they mean → `light/materials`
- Importing a model as a game maker → `make/assets`

**Fit.** `fits`: about 5,070 words against L (5,000). Six excerpts carry the page, since the inventory read the importer
by its header only; the table of what the importer supports and skips comes next, and the toy stays short.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:158` | feature | home | The glTF importer: what it makes, its settings, `Scale` baked into the content, external files, version 11 |
| `assets:613` | hands-on | home | Import a model and textures, read the sub-assets, place it |
| `new:4` | code | home | `Strata/src/Strata/Asset/GltfImporter.h:8-39`: what an import makes, its keys and settings, the version history |
| `new:5` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:236-286`: `Run`, the order of the import and its cancel checks |
| `new:6` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:791-856`: `ImportMaterial`, factors, alpha modes and one texture per usage |
| `new:7` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:1538-1560`: levels of detail with their errors (the scale before them at 1427-1433) |
| `new:29` | feature | home | What `ImportMesh` makes when a glTF lacks vertex data, about 200 words: missing normals become flat face normals on unwelded triangles; missing tangents with UVs become exact per-corner MikkTSpace tangents (`MeshUtils::GenerateSeamTangents`), which split vertices on UV seams and mirror lines; without UVs any tangent perpendicular to the normal is used; `light/materials` links it where normals and tangents enter. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:1472-1531`; `Strata/src/Strata/Renderer/Mesh.h:182-192` |
| `new:30` | feature | home | What the importer supports and skips, as a table with the warning each gives (the Asset tab and `importWarnings` of `asset.info`), about 250 words: a required extension outside the supported list fails the import; primitives with only Draco data, KTX2 (basisu) and WebP images, textures on a second UV set, texture rotation, different wrap modes for the two axes, `EXT_mesh_gpu_instancing`, skin influences beyond the four strongest and an IOR above 3 are skipped or clamped; supported are lights, emissive strength, unlit, clear coat, transmission, volume, IOR, texture transform, mesh quantization and meshopt compression. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:46-53`, `:309-320`, `:733-742`, `:755`, `:844`, `:897-902`, `:1252`, `:1402-1406`, `:1795`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:703` |
| `new:31` | hands-on | home | Trace it yourself (D27): a breakpoint in `ImportMesh` on a model without tangents shows which branch makes them (MikkTSpace with UVs, any perpendicular without), and the vertex count before and after. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:1472-1531` |
| `new:8` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:1972-2007`: `BuildModel`, the model as an entity template whose root keeps scale 1 |
| `new:9` | code | home | `Strata/src/Strata/Renderer/Mesh.h:106-113`: the cooked mesh form `STMH` version 3, which no inventory surveyed |
| `new:10` | not-done | home | No OBJ or FBX import: models are glTF only. Evidence: `Strata/src/Strata/Asset/AssetImporters.cpp:159-177` (`RegisterAssetPipeline` registers no other model importer); `Docs/Releases/0.7.0.md:414-415` |
| `new:11` | erratum | home | `Docs/Architecture.md` gives the glTF importer as version 9; it returns 11. Evidence: `Docs/Architecture.md:2626`; `Strata/src/Strata/Asset/GltfImporter.h:39` |
| `new:12` | erratum | home | The assets inventory places the sub-asset keys at `GltfImporter.h:262-282`, the importer at `:262-309` and its estimate at `:303-308`, but the header has 57 lines. Evidence: `Strata/src/Strata/Asset/GltfImporter.h:10-21` (keys), `:29-55` (the class), `:49-52` (`EstimateImportMemory`) |
| `assets:45` | feature | use | The sub-asset keys a model makes |
| `assets:117` | feature | use | The references and bounds the importer records (taught in `assets/references`) |
| `assets:526` | rule | use | The version bump of both importers |
| `animation:68` | feature | use | The importer's version, as the animation part sees it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Importers, settings, confined reads and versions | `assets/importing` | must |
| Sub-assets and derived handles | `assets/handles-meta` | must |
| Texture usages, and how images are cooked | `assets/texture-cooking` | must |
| Meshes on the GPU: vertices, indices, submeshes, the geometry pool | `gpu/geometry-pool` | must |
| Entity templates: models and prefabs | `world/prefabs` | must |
| JSON and Base64 | `basics/data-formats` | must |
| Transforms, hierarchies and right-handed axes | `basics/math-matrices` | must |
| Counter-clockwise front faces | `gpu/coordinates` | helps |
| Levels of detail and their error | `draw/lod` | helps |
| Skeletons, skins and clips | `animation/skeletons` | helps |
| PBR material fields | `light/materials` | helps |
| References and bounds an import records | `assets/references` | helps |

## `assets/loading` — Loading without stalling

**Covers.** The job: turn a handle into a loaded object while no frame ever waits, and while loads are reloaded,
cancelled, evicted or failed under it. This page carries the part's full section on the problem: blocking loads behind
a loading screen, loads in the background that call back, loads in the background that code polls; Strata polls. The
map (figure 461): `AssetManagerBase` and its entries; the streaming queue; the I/O pool that reads and the workers that
decode; the completion queue behind a shared `LoadState`; `Update` on the main thread; the loader registry; the two
managers that supply the bytes. The contract: `GetAsset` never blocks. It returns the loaded object, the previous one
during a reload, or null; it stamps the request and asks for the load. Code handles "not loaded yet" every frame and
polls, never waits. Typed accessors return null for a wrong type. `LoadAssetSync` is for tools, tests and loading
screens, and never runs from a finalizer. Loaders run on workers, may take the bytes over, and check `IsCancelled`.
Every load ends in exactly one completion, and finalization and publication happen on the main thread. A toy of about
60 lines (a queue, one worker, a completion list polled each frame, a generation counter) shows four ways a simple
loader goes wrong, which Strata guards against.

The real code, in the order a load flows: `GetAsset` and `RequestLoad`; the queue (figure 464: keys of priority,
negative score and request order in a `std::map`; a repeat raises and never lowers; dispatch while the bytes in flight
stay under 128 MiB and the reads under two per I/O thread; one load always runs; `Pump` never recurses); `RunLoad`
(read on the I/O pool, dependencies prefetched when the read completes, decoding on a worker, exceptions turned into
failed loads); the loader registry and the renderer's loaders (`TakeBytes`); `ProcessCompletions`, shown in parts
(stale completions discarded by their generation; publication; the room it makes is `assets/residency`'s and the budget
it hands to finalizers `assets/uploads`'); generations and the state machine (figure 458), where a failed load stays
Failed with its error (`GetAssetError`, `loadError` of `asset.info`) and `GetAsset` returns null every frame without
trying again, until `ReloadAsset`, `UnloadAsset` or a new registration makes it Unloaded (in a game nothing does); the
`Asset` base class. Then the manager's other entry points: peeking without requesting, synchronous loads, replacing a
loaded object (a material while its value is dragged), memory assets, source revisions and content versions for caches,
the active manager and `Scene::GetAssetManager`, loads waiting for a first import, cancelling and unloading, and the
waiting helpers. Then the alternatives, the tests (`Asset`, `Asset.StreamingQueue`), and changing it safely. Exercises:
trace a load with breakpoints and note which thread runs each stage; predict the queue's dispatch order for a list of
requests.

**Leaves out.**

- Memory budgets, eviction and pins → `assets/residency`
- Dependencies, closures and prefetch rules → `assets/references`
- The upload budget a finalizer works within → `assets/uploads`
- Partial loads and range reads of textures → `draw/mip-streaming`
- What the renderer requests each frame, and the resolve cache → `draw/asset-requests`
- Loading whole scenes in slices → `world/sub-scenes`
- The job system's pools → `core/jobs`

**Fit.** `fits`: about 7,995 words against XL (8,000), one page in sections. Six excerpts (two of them long), three
concepts and the manager's other entry points take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:286` | concept | home | Asynchronous loading and the main-thread rule, with the approaches |
| `assets:292` | concept | home | Generations: stale completions are discarded at every step |
| `assets:297` | concept | home | Priority queues and backpressure: a bound on bytes, not on count |
| `assets:41-42` | feature | home | Asset states and priorities; the `Asset` base class |
| `assets:54` | feature | home | The loader registry, filled by the module that owns each type |
| `assets:65-68` | feature | home | `AssetManagerBase`, typed accessors, `GetAsset` never blocks, `PeekLoadedAsset` |
| `assets:70-72` | feature | home | `LoadAssetSync`, `ReplaceLoadedAsset`, memory assets |
| `assets:74-77` | feature | home | Generations, source revisions, content and metadata versions, the active manager facade |
| `assets:80` | feature | home | A load waits in Loading while the asset's first import runs |
| `scene-ecs:41` | feature | home | `Scene::GetAssetManager()`, the path from scene code to assets, taught with the active manager's facade |
| `assets:86-90` | feature | home | The streaming queue, reads on I/O and decoding on workers, `AssetLoadData`, the completion queue, main-thread finalization |
| `assets:92-94` | feature | home | Cancellation, exception containment, waiting helpers |
| `new:32` | feature | home | A failed load stays failed, about 100 words: `RequestLoad` starts a load only from Unloaded, so `GetAsset` returns null for a Failed asset every frame and never tries again; the error is kept (`GetAssetError`, `loadError` of `asset.info`); only `ReloadAsset` (in the editor, a changed source or a re-import), `UnloadAsset` or a new registration make it Unloaded again, and in a game nothing does. Evidence: `Strata/src/Strata/Asset/AssetManager.cpp:459-463`, `:1238-1243`, `:718-763`; `Strata/src/Strata/Asset/AssetManager.h:354`, `:358-369`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:690` |
| `assets:382` | code | home | `Strata/src/Strata/Asset/Asset.h:161-193`: the `Asset` base class, the contract of every type |
| `assets:386` | code | home | `Strata/src/Strata/Renderer/RendererRegistration.cpp:81-118`: the renderer's loaders, `TakeBytes` and the BC fallback |
| `assets:406` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:330-349`: `GetAsset`, with `RequestLoad` at 440-484 |
| `assets:408` | code | home | `Strata/src/Strata/Asset/AssetStreamingQueue.cpp:148-207`: `CanDispatchLocked` and `Pump`, with the key at `AssetStreamingQueue.h:117-120` |
| `assets:411` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:583-684`: `RunLoad`, exactly one completion on every path |
| `assets:414` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:1040-1274`: `ProcessCompletions`, shown in parts: 1088-1113 (stale completions) and 1219-1246 (publication); 1115-1169 is quoted by `assets/residency`, 1171-1217 by `assets/uploads` |
| `assets:458` | figure | home | The asset state machine, with the generation bumps and the ways out of Failed (`ReloadAsset`, `UnloadAsset`, a new registration) |
| `assets:461` | figure | home | The three-stage load timeline: main thread, I/O thread, worker |
| `assets:464` | figure | home | The queue's ordering and its backpressure |
| `assets:537` | rule | home | `GetAsset` never blocks; handle "not loaded yet" every frame |
| `assets:568` | rule | home | Polling, not waiting |
| `scene-ecs:557` | rule | home | Code that works for a scene reaches assets through `Scene::GetAssetManager()` |
| `assets:577` | hands-on | home | Trace a load and the thread of each stage |
| `assets:597` | hands-on | home | The streaming queue puzzle |
| `assets:657` | term | home | Memory asset |
| `assets:661-671` | term | home | Loader, finalize, publish, asset state, priority and score, streaming queue, in flight, backpressure, generation, source revision, content version |
| `automation:739` | term | home | Backpressure, one glossary entry with `assets:668`, taught from zero here: refusing or slowing new work while too much is pending; the automation server's form of it is `automation/rpc-server`'s |
| `assets:73` | feature | use | `ReloadAsset` serves the old version (taught in `assets/importing`) |
| `assets:91` | feature | use | The finalize contract (taught in `assets/uploads`) |
| `assets:120` | feature | use | Dependencies prefetched when a read completes (taught in `assets/references`) |
| `assets:164` | feature | use | The BC decode in the texture loader |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an asset, a source file and a stored form are | `assets/what-is-an-asset` | must |
| Handles and asset metadata | `assets/handles-meta` | must |
| The job system's pools (`Submit`, `SubmitIO`) and the main thread's role | `core/jobs` | must |
| The frame loop: an update once per frame | `core/frame-loop` | must |
| Mutexes, locks taken one at a time, atomics | `basics/threads` | must |
| `std::map` ordering, tuples, lambdas and `std::function` | `basics/cpp-generic` | must |
| Shared ownership (`Ref`) | `basics/cpp-memory` | must |
| `std::span` and `std::optional` | `basics/cpp-modern` | must |
| Virtual functions and interfaces | `basics/cpp-classes` | must |
| Exceptions caught where third-party code throws | `core/conventions` | must |
| Priority queues and the cost of their operations | `basics/trees-graphs` | helps |
| Imports in the background | `assets/importing` | helps |
| Breakpoints and threads in a debugger | `core/debugging` | helps |
| The finalize results `Pending` and `AwaitingGPU` | `assets/uploads` | helps |

## `assets/residency` — Residency, eviction and pins

**Covers.** The job: keep assets within a memory budget per pool, dropping what was requested longest ago, and never
what is in use or what the GPU still reads. The problem and how engines solve it: no budget, one budget, or budgets
per pool; LRU, LFU, priority classes or explicit unloads; with a table. The map: `AssetResidency` (budgets, pins, trims,
eviction), the manager's entries and recency orders, `IAssetGraphics` (the device's memory budget and its frames in
flight), and the manager extension seam. The contract: assets report memory per pool (`GetMemoryUsage`,
`GetFinalizedMemoryUsage`, `IsDataShared`). Code requests every frame what it uses, and holds handles, not `Ref`s.
Gameplay pins what it must keep, and releases it. No GPU memory that a frame in flight may use is freed. A toy of about
50 lines keeps an LRU cache within a byte budget (a list and a map); then come Strata's differences: pools, stamps by
request rather than by arrival, protections, room before arrival.

The real code: pools and budgets (figure 466; GPU textures 50% and GPU buffers 15% of the device's budget, CPU
unlimited); `TouchLocked`, where a request moves the asset's node to the end in constant time with `extract` and a
hinted insert (figure 468); `CanEvictLocked`, `EvictLocked` and `EvictToFitLocked` (pins, a grace window of the frames
in flight plus two, memory and built-in assets, objects held outside the manager by `use_count() == 1`, shared data);
trims after a scene switch; `MakeRoomFor` and the waiting arrivals of `ProcessCompletions` (figure 470: evict first,
reserve, wait the frames in flight plus one before allocating GPU memory, and arrivals behind wait together); memory
that changes without a new object (`UpdateMemoryUsage`); manager extensions, which free partly resident memory before
whole assets go; pins (`AssetPin`: RAII, a weak manager, one registration) and scripts' pins (`Assets::RequestLoad` and
`Release`); `TouchLoadedAssets` for still frames; the statistics and the Streaming panel (figure 504); and setting the
budgets (`asset.setBudget`, `--asset-budget-mb`). Then the alternatives, the tests (`Asset.Residency`,
`Asset.PartialResidency`), and changing it safely. Exercises: prove the LRU order with `FakeAssetManager` and show that
a held `Ref` is never evicted; watch evictions in the Showcase under a tight budget (one `asset.setBudget` line to paste,
and a link forward to `editor/commands`); keep a sound loaded from a script; trace it yourself: breakpoints in
`EvictToFitLocked` and `CanEvictLocked` under that budget show which protection keeps each asset that is not evicted.

**Leaves out.**

- Loading, finalization and generations → `assets/loading`
- Closures, group loads and prefetch → `assets/references`
- Keeping only some of a texture's levels resident → `draw/mip-streaming`
- Deferred release of GPU resources in general → `gpu/resources-lifetimes`
- How the Streaming panel draws its table cheaply → `editor-ui/instrument-panels`
- Every budget's default and every statistic, as tables → `reference/assets`
- Asking for sounds early, as a game maker → `make/sound`

**Fit.** `fits`: about 7,830 words against XL (8,000), one page in sections. Four concepts, four excerpts with four
figures, and four exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:302` | concept | home | Memory budgets and pools |
| `assets:307` | concept | home | LRU eviction with protections; the `Ref` pitfall |
| `assets:313` | concept | home | Pins; pinning everything is no budget at all (group loads are `assets/references`') |
| `assets:335` | concept | home | Room before arrival |
| `assets:56` | feature | home | Manager extensions: `ReleaseMemory` before whole assets are evicted, `OnUpdate`, `AddStats` |
| `assets:69` | feature | home | `TouchLoadedAssets`: many requests under one lock, for still frames |
| `assets:100-110` | feature | home | Pools, budgets, recency orders, eviction to budgets, protections, pins, trims, room before arrival, statistics, script pins, budget controls |
| `assets:189` | feature | home | `UpdateMemoryUsage`: totals follow a texture that gained or dropped levels |
| `assets:417` | code | home | `Strata/src/Strata/Asset/AssetResidency.cpp:325-349`: `TouchLocked`, a constant-time move with `extract` |
| `assets:419` | code | home | `Strata/src/Strata/Asset/AssetResidency.cpp:428-445`: `CanEvictLocked` and `EvictLocked`, with `EvictToFitLocked` at 523-542 |
| `assets:421` | code | home | `Strata/src/Strata/Asset/AssetResidency.cpp:544-570`: `MakeRoomFor` |
| `assets:422` | code | home | `Strata/src/Strata/Asset/AssetResidency.cpp:104-138`: `Pin` and `Unpin`, a weak manager and a registration |
| `assets:466` | figure | home | Memory pools and budgets: resident, reserved, pending, the in-flight window, headroom |
| `assets:468` | figure | home | The recency orders, one `std::map` per pool, and touch as a move to the end |
| `assets:470` | figure | home | Room before arrival, across frames |
| `assets:504` | figure | home | The Streaming panel under a 32 MB texture budget, with evictions |
| `assets:539`, `render-scene:467` | rule | home | Hold `AssetHandle`s across frames, not `Ref`s; request what you use every frame: one rule and one why-box here, since a held `Ref` keeps the asset from eviction (`draw/asset-requests` shows it applied: the resolve cache drops its references when the frame ends) |
| `assets:541` | rule | home | Pin what gameplay must keep; release it |
| `assets:543` | rule | home | Report shared data and accurate memory per pool |
| `assets:561` | rule | home | Never free GPU memory a frame in flight may use |
| `assets:594` | hands-on | home | Prove the LRU order, and the held `Ref` that is never evicted |
| `assets:619` | hands-on | home | Watch streaming in the Showcase: the Streaming panel, then a tight budget (the Mip and Streaming views are named and linked) |
| `assets:624` | hands-on | home | Keep a sound loaded with `Assets::RequestLoad` and `Release` |
| `new:33` | hands-on | home | Trace it yourself (D27): breakpoints in `EvictToFitLocked` and `CanEvictLocked` under a tight texture budget show where the walk stops at the grace window and which protection keeps each asset that is not evicted (a pin, a memory or built-in asset, a `Ref` held outside the manager, shared data). Evidence: `Strata/src/Strata/Asset/AssetResidency.cpp:428-435`, `:523-542` |
| `assets:673-681` | term | home | Residency, memory pool, budget, device memory budget, eviction, LRU, recency order, request (touch), grace window |
| `assets:683-686` | term | home | Pin, trim, room before arrival, reservation |
| `scripting:565` | term | home | `AssetPin`, one glossary entry with `assets:683`: a script's `Assets::RequestLoad` holds one until `Release` |
| `assets:414` | code | use | `ProcessCompletions` 1115-1169: room and the waiting arrivals (home `assets/loading`) |
| `assets:442` | code | use | The script side of pins (home `assets/references`) |
| `assets:58` | feature | use | `IAssetGraphics`: the device's budget and its frames in flight |
| `assets:213` | feature | use | What the Streaming panel shows (its drawing is `editor-ui/instrument-panels`') |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Loading, finalization, publication and generations; the `Asset` base class | `assets/loading` | must |
| Frames in flight | `gpu/how-a-gpu-frame-works` | must |
| Deferred release of GPU resources | `gpu/resources-lifetimes` | must |
| The device's memory and the budget it reports | `gpu/vulkan-nvrhi` | must |
| Shared and weak ownership, `use_count`, RAII and types that only move | `basics/cpp-memory` | must |
| Trees and maps, and the cost of their operations | `basics/trees-graphs` | must |
| `std::map` node handles: `extract` and an insert with a hint | `basics/cpp-generic` | must |
| Mutexes | `basics/threads` | must |
| Loading scenes, and a scene switch | `world/sub-scenes` | helps |
| Reading and running a command line | `start/how-to-read` | helps |
| Commands and the command registry | `editor/commands` | helps |
| A script's callbacks, such as `OnCreate` | `scripting/script-system` | helps |
| Textures kept partly resident | `draw/mip-streaming` | helps |

## `assets/references` — References, closures, prefetch and loading screens

**Covers.** The job: know what each asset uses, the same way in the editor and in a game, so that loads, exports,
delete checks and prefetches follow references. The problem and how engines solve it (scan at load time, record at
import time, hand-written manifests) take a short table. The map (figure 485): the scanner (`AssetDependencies`), what
importers record (`ImportResult::References` and `Bounds`), the manager's tables of dependencies and bounds, prefetch,
group requests, and the editor's index of referencers with its searches of the engine's own documents. The contract:
references are recorded at import, or found in a document, and normalized (valid handles, each once, never the asset
itself); a new document type records its references; prefetches never evict and never chain, documents prefetch
nothing, and scenes are never prefetched; a closure has one of two scopes. A toy of about 30 lines walks a small graph
breadth first and reports a group's progress by bytes.

The real code: the scanner streams scenes, prefabs and models through `SceneDocumentReader` and collects every asset
property of every registered component and of script fields, materials' textures, controllers' clips and worlds'
cells; `NormalizeReferences`; `GetDependencyClosure` ("the list itself is the queue"; `All` for packing, `Load` stops at
other scenes); bounds known before a mesh loads, so the renderer can cull and request what is not loaded yet;
dependency prefetch when a read completes, only into headroom (`FitsPrefetchLocked`), with the measured reasons (about
25 MB more peak memory for textures, 60 to 100 MB for scenes, a world's cells held at 12.6 GB instead of 280 MB); group
loads (`AssetGroupRequest` pins its closure, and its progress by stored bytes never goes down); reading stored bytes
without loading; what a first load reads now (`EstimateFirstLoadBytes`) and how a scene load fits its closure into the
budgets with it: per pool, the closure's members load and are pinned with the scene only if all of them fit in the room
beside what is resident, else none of them, and the scene requests them itself once it runs (`GetSkippedAssetCount`), so
a load never pushes a pool past its budget; `RequiredProgress`; the trim after the switch, which spares the load's
assets; the referencer index, and the searches of changed documents after 500 ms of quiet. The script side:
`Assets::RequestLoad`, `Release` and `GetLoadProgress`. Then the alternatives, the tests (`Asset.Dependencies`,
`Asset.Groups`), and changing it safely: a new document type that does not record its references loses its assets from
pruned exports, and its deletes do not warn. Exercises: a loading screen script that shows `Assets::GetLoadProgress` as
a bar, with a link to what limits how fast it fills (`assets/uploads`); trace it yourself: a breakpoint in
`GetDependencyClosureLocked` lists a Showcase scene's closure in order and shows where the `Load` scope stops at
another scene.

**Leaves out.**

- Pins, budgets and eviction → `assets/residency`
- The scene loader and its states → `world/sub-scenes`
- Delete checks and the trash, as the editor runs them → `editor/trash-references`
- What the renderer requests and culls each frame → `draw/asset-requests`
- Prefetch before a teleport in a streamed world → `worlds/physics-scripts`
- Loading screens, as a game maker builds them → `make/levels-saves`
- Graphs and breadth-first search in general → `basics/trees-graphs`

**Fit.** `fits`: about 6,075 words against L (5,000). Three concepts, three excerpts and the features of the dependency
graph take the most words; the two editor-side features (the referencer index and the searches of changed documents)
stay, since L holds them.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:318` | concept | home | Dependency graphs: scan at load, record at import, manifests |
| `assets:324` | concept | home | Prefetching without hurting, with the measured reasons |
| `assets:366` | concept | home | Bounds before load: culling and requesting meshes that are not loaded |
| `assets:116-124` | feature | home | The scanner, importer-recorded references and bounds, normalized references, dependency queries, prefetch, group loads, reading without loading, the referencer index, native documents' references |
| `assets:192` | feature | home | `EstimateFirstLoadBytes` |
| `new:34` | feature | home | How a scene load fits its closure into the budgets, about 200 words, beside `assets:121` and `assets:192`: per pool, the closure's members load and are pinned with the scene only if all of them fit in the room the budget has beside what is resident (counted with `EstimateFirstLoadBytes`); otherwise none of them load, and the scene requests them itself once it runs (`GetSkippedAssetCount`), so a load never pushes a pool past its budget; `RequiredProgress`; the trim after the switch keeps the load's assets. Evidence: `Strata/src/Strata/Scene/SceneLoader.h:31-36`, `:50-63`, `:88-92`; `Strata/src/Strata/Asset/AssetManager.h:473` (`ScheduleTrim` and what it keeps) |
| `assets:424` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:1450-1473`: the breadth-first closure and the `Load` scope |
| `assets:426` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:1567-1585`: `FitsPrefetchLocked`, headroom with saturating sums |
| `assets:442` | code | home | `StrataScriptCore/Include/StrataScript/Scene.h:18-62`: the script side, `Assets` |
| `assets:485` | figure | home | The dependency graph, closures and their scopes, prefetch edges |
| `assets:554` | rule | home | Record references for any new document type |
| `assets:559` | rule | home | Prefetches never evict and never chain; documents prefetch nothing |
| `assets:622` | hands-on | home | A loading screen with `Assets::GetLoadProgress`; it links the staging bound (`new:36`) and the budgets a game cannot raise (`new:37`) of `assets/uploads` |
| `new:35` | hands-on | home | Trace it yourself (D27): a breakpoint in `GetDependencyClosureLocked` lists a Showcase scene's closure in order (the list itself is the queue) and shows where the `Load` scope stops at another scene. Evidence: `Strata/src/Strata/Asset/AssetManager.cpp:1450-1473` |
| `assets:651-653` | term | home | Dependency (runtime), dependency closure, closure scope |
| `worlds-runtime:536` | term | home | Closure, as the worlds part words it |
| `assets:687-689` | term | home | Prefetch (of assets), headroom, group load |
| `new:13` | erratum | home | The assets inventory places the scanner at `AssetDependencies.h:349-386`, but the header has 56 lines. Evidence: `Strata/src/Strata/Asset/AssetDependencies.h:30-52` (`Scan`, `ScanDocument`, `ScanEntities`, `ReferenceList`, `ScanEntity`) |
| `assets:313` | concept | use | Pins, which group loads hold (taught in `assets/residency`) |
| `assets:109` | feature | use | Script pins (taught in `assets/residency`) |
| `scene-ecs:181` | feature | use | `SceneLoader`, which pins a scene's closure |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Residency, pins and budgets | `assets/residency` | must |
| Loading, priorities, and the read that completes | `assets/loading` | must |
| Scene documents read as streams: `SceneDocumentReader` and sinks | `world/serialization` | must |
| Asset properties of components, through reflection | `world/reflection` | must |
| Graphs and breadth-first search | `basics/trees-graphs` | must |
| C++ at the level a script calls the SDK | `basics/programming-3` | must |
| What an import records | `assets/importing` | helps |
| Loading scenes and their budget | `world/sub-scenes` | helps |
| Culling meshes the renderer has not loaded | `draw/asset-requests` | helps |
| A script's fields and its update | `scripting/script-system` | helps |

## `assets/uploads` — Budgeted uploads

**Covers.** The job: get the bytes of finalized assets to the GPU in steps that fit the frame's byte and time budgets,
so that a 90 MB texture never stalls a frame and every frame makes progress. The problem takes one paragraph (upload
rings, copy queues, caps per frame) that links `gpu/upload-queue`, which owns the mechanism: `PlanStep`, the staging
pool, the transfer queue and `PrepareBackBuffer`. The map: the asset layer's side (`AssetFinalizeContext`,
`AssetFinalizeResult`, `c_AssetUploadStepBytes`, `AssetUploadContext`, `IAssetGraphics`) and the renderer's
(`RendererUploadContext`, `GPUUploadQueue`, `Texture`). The contract: a finalizer records into the context and never
into a graphics API, which the asset layer does not include; steps are at most 4 MiB, sized to what is left of the
bytes, of the milliseconds and of the time to the deadline; the frame's first step goes whatever the byte and time
budgets say, but every step through staging, the first too, waits while the staging in flight leaves it no room (the
first within `StagingBytes`, later ones within `GetStagingRoom`); bytes are reported; `Pending` continues in a later
frame, `AwaitingGPU` when the copies run on the transfer queue; and the manager opens one batch per update and submits
it before rendering. The staging bound sets the throughput: with the default 32 MiB, sustained uploads reach about
28 MiB a frame, and about half the budget when frames come faster than the copies, unless the 16 MiB and 4 ms of a
frame stop them first; the code advises raising all three for a loading screen, which a game cannot do (no script
function and no settings section sets them). A toy of about 40 lines uploads in steps, in the shape of the tests'
`SteppedAsset`.

The real code: the contract in `Asset.h` (the step size, the results, the context and its staging room); the seam in
`AssetUploadContext.h`; the finalize part of `ProcessCompletions` (the budgets each finalizer gets; `Pending` keeps its
place in line; `AwaitingGPU` steps aside); `Texture::FinalizeOnMainThread` (the GPU texture made, the levels uploaded,
the CPU copy freed within the deadline before publication, the bindless slot and the texture-table index allocated at
publication); and `UploadLevels` (small levels stacked in one staging buffer, large ones in power-of-two runs of block
rows). Figure 489 places the steps within a frame: 4 ms of finalization, 2 ms of upload steps with a tenth kept in
reserve. Then the alternatives, the tests (`Asset.Finalize`), and changing it safely (the layering test refuses NVRHI and
Vulkan headers in `Asset/`). Exercises: drive the finalize contract without a GPU and show that no frame uploads more
than its budget; trace it yourself: a breakpoint in `Texture::FinalizeOnMainThread` while a large texture arrives shows
the frames its upload takes and the bytes each call reports.

**Leaves out.**

- `PlanStep`, the staging pool, fences, the transfer queue and `PrepareBackBuffer` → `gpu/upload-queue`
- Bindless slots that change when a texture's levels change → `draw/mip-streaming`
- How meshes reach the geometry pool → `gpu/geometry-pool`
- Room before arrival, which can hold an arrival back → `assets/residency`

**Fit.** `fits`: about 4,665 words against L (5,000). Four excerpts and the contract's many fields, with the staging
bound, take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:329` | concept | home | Budgeted GPU uploads and staging memory, from the asset side |
| `assets:58` | feature | home | The upload seam: `AssetUploadContext` and the `IAssetGraphics` engine service |
| `assets:91` | feature | home | The finalize contract: `AssetFinalizeContext` and `AssetFinalizeResult` |
| `assets:199` | feature | home | Steps of at most `c_AssetUploadStepBytes`; the frame's first step goes whatever the byte and time budgets say, within the staging bound |
| `assets:201` | feature | home | Texture uploads: levels stacked or in runs of rows, the CPU copy freed before publication |
| `assets:204` | feature | home | One batch per update, submitted before rendering |
| `render-core:108` | feature | home | The `Texture` asset's GPU side: its finalization uploads in planned steps (its level changes are `draw/mip-streaming`'s) |
| `assets:440` | code | home | `Strata/src/Strata/Renderer/Texture.cpp:584-676`: `UploadLevels` |
| `new:14` | code | home | `Strata/src/Strata/Asset/Asset.h:43-119`: `c_AssetUploadStepBytes`, `AssetFinalizeResult` and `AssetFinalizeContext` with its staging room |
| `new:15` | code | home | `Strata/src/Strata/Asset/AssetUploadContext.h:10-47`: the upload context and `IAssetGraphics`, the seam without a graphics API |
| `new:16` | code | home | `Strata/src/Strata/Renderer/Texture.cpp:464-537`: `Texture::FinalizeOnMainThread`, from upload to publication |
| `new:36` | concept | home | The staging bound and the throughput it gives, about 120 words: a step through staging waits while the staging in flight leaves it no room (the frame's first within `StagingBytes`, later ones within `GetStagingRoom`, one step less); with the default 32 MiB, sustained uploads reach about 28 MiB a frame, about half the budget when frames come faster than the copies, unless `UploadBytesPerFrame` (16 MiB) or `FinalizeMsPerFrame` (4 ms) stop them first. Evidence: `Strata/src/Strata/Asset/Asset.h:72-78`; `Strata/src/Strata/Asset/AssetResidency.h:47-64` |
| `new:37` | not-done | home | A game cannot raise its streaming budgets for a loading screen: no script function and no settings section sets the upload, finalization and staging budgets, and the runtime's `--asset-budget-mb` sets only the GPU texture budget. Evidence: `Strata/src/Strata/Asset/AssetResidency.h:56-64` (raise all three for a loading screen); `git grep -ln -e UploadBytesPerFrame -e FinalizeMsPerFrame 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataScriptCore` finds only the asset manager's files and the editor's (`StrataEditor/src/Editor/EditorStreamingCommands.cpp`, `StrataEditor/src/Panels/StreamingPanel.cpp`); `StrataRuntime/src/RuntimeApplication.cpp:56`, `:94-95` |
| `new:38` | hands-on | home | Trace it yourself (D27): a breakpoint in `Texture::FinalizeOnMainThread` while a large texture arrives shows the frames its upload takes, the bytes each call reports and where it ends `Pending`. Evidence: `Strata/src/Strata/Renderer/Texture.cpp:464-537` |
| `assets:489` | figure | home | Upload steps planned within a frame |
| `assets:545` | rule | home | Upload in steps of at most `c_AssetUploadStepBytes` within the context's budget; report bytes |
| `assets:565` | rule | home | The asset layer includes no graphics API |
| `assets:591` | hands-on | home | Drive the finalize contract without a GPU |
| `assets:690-691` | term | home | Upload, upload step |
| `assets:698-699` | term | home | Upload context, batch (of uploads) |
| `assets:414` | code | use | `ProcessCompletions` 1171-1217: the finalize part (home `assets/loading`) |
| `assets:206` | feature | use | Bindless slots resolved every frame (taught in `draw/mip-streaming`) |
| `render-core:85` | feature | use | `PlanStep` |
| `render-core:87` | feature | use | `StagingPool` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Staging, the upload queue, `PlanStep`, fences and the transfer queue | `gpu/upload-queue` | must |
| Resources, their states and deferred release | `gpu/resources-lifetimes` | must |
| Bindless slots and the texture table | `gpu/binding` | must |
| The CPU and the GPU working on different frames | `gpu/how-a-gpu-frame-works` | must |
| Finalization and publication on the main thread | `assets/loading` | must |
| Room before arrival, and the frame's budgets | `assets/residency` | must |
| Cooked textures, their levels and block rows | `assets/texture-cooking` | must |
| Engine services | `core/engine-modules` | must |
| The layer table and its test | `core/layers-registries` | must |
| Mip streaming, which changes bindless slots | `draw/mip-streaming` | helps |

## `assets/packs-export` — Asset packs, export and patches

**Covers.** The job: put every asset a game ships into one file that the runtime reads by byte range, that is checked
for corruption, that is laid out so a scene loads front to back, and that patches can override. The problem and how
engines solve it (loose files, archives like zip, Unreal's `.pak` and IoStore, Unity's bundles) take a table. The map:
`EditorAssetManager::PlanAssetPack` and `WriteAssetPack`, `AssetPackWriter`, `AssetPackCook`, `AssetPack` (the
reader), `RuntimeAssetManager` (mounts) and the game manifest's `PatchPacks`. The contract: entries are ordered by
first use; each is cut into 256 KiB blocks, compressed with zstd or stored when compression saves less than an eighth;
a CRC-32C guards each block, the header and the tables; the tables end the file, so the writer makes one pass; the plan
is a snapshot, and the write checks again that no document now references what the plan left out; later packs replace
earlier entries by handle and reload them; built-in handles are never replaced. A toy of about 60 lines writes a pack
(a header, entries, one table at the end, one checksum) and reads it back.

The real code: the format comment and the `Header` and `EntryRecord` structs with their `static_assert` sizes (figure
480); planning (the start scene's closure first, then the other scenes', then the rest, or nothing of the rest when
pruning; `AlwaysInclude` by path, to which the export adds the loading scene and every asset that the project's settings
sections name, so a pruned pack keeps them); the consistency check, and the cooking of scenes, prefabs and models into
`CookedScene` binaries during the write; the writer (one pass, a temporary file renamed into place, blocks compressed
in parallel batches of 64); `DecodeBlock` (the checksum first, stored blocks read in place, zstd, partial blocks);
range reads (figure 483: the covered blocks, chunks of up to 2 MiB, three read ahead, helper jobs that decode while the
reader reads on); version 1 packs still read; the content hash; `RuntimeAssetManager::Mount` and patch packs, which no
tool writes: the export writes none and lists none, so a patch is a pack written from code and named in the manifest's
`PatchPacks` by hand. Why BC data is stored, not compressed: zstd saves about 7% of it, for a buffer and a
decompression. The export as a whole (its state machine, its checks, the folder it writes) is `worlds/export`'s. Then
the alternatives, the tests (`Asset.Pack`), and changing it safely: a format change extends the corruption tests.
Exercises: measure compression on BC7 data and on JSON; export with pruning and find the asset only `Assets::Find` named
(`Export.AlwaysInclude`); a patch pack written by a test and listed in `PatchPacks`; trace it yourself: a breakpoint in
`DecodeBlock` while the runtime loads a scene shows which blocks a range read covers and which are stored rather than
compressed.

**Leaves out.**

- How a pack is checked on open, and untrusted input in general → `assets/robustness`
- The export's state machine, its checks and the folder it writes → `worlds/export`
- The manifest and the game's identity → `worlds/game-identity`
- The cooked scene format (STSC) → `world/serialization`
- The Export dialog's drawing → `editor-ui/launcher-dialogs`
- Exporting a game, as a game maker → `make/export`

**Fit.** `fits`: about 6,075 words against L (5,000). Five excerpts, three figures and fourteen features (four of them
passed from other areas, and close to the pack's own) take the most words, then four exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:345` | concept | home | Distribution formats: packs, compression, integrity, random access, patches |
| `assets:79` | feature | home | `RuntimeAssetManager`: assets from mounted packs, dependencies and bounds from the pack's tables |
| `assets:172` | feature | home | Pack format v2 |
| `assets:174-181` | feature | home | Range reads, version 1, the writer, planning, the consistency check, cooked documents, patch packs, the content hash |
| `worlds-runtime:159-161` | feature | home | The game's pack, pruning (off by default, `excludedAssets` listed; a pruned pack keeps the loading scene and every asset that the settings sections name, which the export adds to `AlwaysInclude`) and patch packs, as the export makes and the runtime mounts them |
| `scene-ecs:214` | feature | home | `ProjectExportSettings`: `AlwaysInclude` taught here; `LoadingScene` named and linked to `worlds/export` |
| `assets:428` | code | home | `Strata/src/Strata/Asset/AssetPack.h:66-89`: the format comment, with `Header` and `EntryRecord` at 177-216 |
| `assets:432` | code | home | `Strata/src/Strata/Asset/AssetPack.cpp:681-744`: `DecodeBlock` |
| `new:17` | code | home | `Strata/src/Strata/Asset/EditorAssetManager.cpp:4202-4270`: `PlanAssetPack`, first-use order, `AlwaysInclude` and pruning |
| `new:18` | code | home | `Strata/src/Strata/Asset/EditorAssetManager.cpp:4292-4345`: `WriteAssetPack`, the consistency check and the cooking of documents |
| `new:19` | code | home | `Strata/src/Strata/Asset/RuntimeAssetManager.cpp:42-99`: `Mount` and `AddPack`, entries replaced by handle |
| `new:39` | not-done | home | No tool writes patch packs, about 40 words: the export writes none and lists none in the manifest's `PatchPacks`, so a patch is a pack written from code and named in the manifest by hand. Evidence: `git grep -n PatchPacks 822a7a46 -- StrataEditor StrataCLI Tools` finds nothing; `Strata/src/Strata/Project/GameManifest.h:26`, `:53`; `StrataEditor/src/Editor/GameExport.cpp:298-317` (the manifest the export fills sets no `PatchPacks`) |
| `new:40` | hands-on | home | Trace it yourself (D27): a breakpoint in `DecodeBlock` while the runtime loads a scene shows which blocks a range read covers, the checksum checked first, and which blocks are stored rather than compressed. Evidence: `Strata/src/Strata/Asset/AssetPack.cpp:681-744` |
| `assets:480` | figure | home | The pack file layout, with a scene's closure laid out front to back |
| `assets:483` | figure | home | The pack read path |
| `assets:512` | figure | home | The Export dialog with pruning and `AlwaysInclude`, and the pack's size in the log: one capture set, made once with the Export dialog's figures of `editor-ui/launcher-dialogs` (`worlds-runtime:400`, `editor-ui:580`), whose caption here says what the page teaches (pruning and the pack) |
| `worlds-runtime:376` | figure | home | The pack layout, the same figure as `assets:480`: one figure on the page |
| `assets:563` | rule | home | Do not compress what does not compress |
| `worlds-runtime:442` | rule | home | Pruning is off by default; prune only with `Export.AlwaysInclude` listing what scripts load by path |
| `assets:602` | hands-on | home | Measure compression |
| `assets:626` | hands-on | home | Export pruned, and `Export.AlwaysInclude` |
| `assets:630` | hands-on | home | A patch pack |
| `worlds-runtime:483` | hands-on | home | Prune safely: the same exercise as `assets:626`, one exercise on the page |
| `assets:719-721` | term | home | Asset pack, block (of a pack), zstd |
| `assets:724-726` | term | home | First-use order, pruning and `AlwaysInclude`, patch pack and mount |
| `worlds-runtime:549`, `worlds-runtime:551`, `worlds-runtime:552` | term | home | Asset pack, pruning, patch pack, as the worlds part words them |
| `assets:173` | feature | use | The checks on open (taught in `assets/robustness`) |
| `assets:217` | feature | use | The export waits for imports, plans and writes the pack (taught in `worlds/export`) |
| `scene-ecs:161` | feature | use | Cooked scenes, STSC |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| References, closures and their scopes | `assets/references` | must |
| Residency, and loads that read by byte range | `assets/residency` | must |
| Scene documents and their cooked form (STSC) | `world/serialization` | must |
| CRC checksums and FNV-1a hashes | `basics/data-formats` | must |
| Jobs and helper jobs | `core/jobs` | must |
| Atomic writes: a temporary file renamed into place | `core/files` | must |
| Structs as bytes: sizes, alignment and `static_assert` | `basics/bytes` | helps |
| Little-endian byte order | `basics/bytes` | helps |
| What an import records | `assets/importing` | helps |
| The export as a whole | `worlds/export` | helps |
| The game manifest | `worlds/game-identity` | helps |
| Exporting a game from the editor's Export dialog | `editor-ui/launcher-dialogs` | helps |

## `assets/robustness` — Corruption, crash safety and cancellation

**Covers.** The problem as a reader meets it: a pack truncated by a failed download; a glTF file whose accessors claim
a billion vertices; the power cut while an import writes its cache; a project closed while 17 imports run. The naive
answers are to trust the sizes a file states, to write the record and then the data, and to join every thread on close;
the page shows where each breaks. The idea: files are untrusted input, so they are checked before use, sizes are bounded
by what the file holds, and each block is checksummed before it is decoded; write-ahead ordering keeps any record from
naming data that is not there yet; and every long job checks a cancel flag, so nothing waits. The approaches of engines
and databases (checksums against cryptographic hashes, validation passes, fuzzing and sweeps; journals, atomic renames,
copy-on-write) end in a table.

Strata's choice, shown on its own code: the pack's checks on open (header and tables checksummed, entries that may not
share blocks, blocks that cover their entry exactly, names bounded by the file's size); the glTF importer's limits
(decoded bytes, accessor elements, a geometry budget relative to the buffers, hierarchy depth); every loader rejects
truncated or garbage bytes; the import record store (one line per record with its CRC-32C, a torn last line skipped and
cut, compaction from memory); cache files renamed into place before their record (the code is on `assets/importing`);
cancel flags checked per block, and jobs that share only `BackgroundWork`. The tests that keep it true: the "any single
changed byte" sweep of packs, and the corrupt-bytes tests of every loader; sweeps and fuzzing in general are
`engineering/test-program`'s. What the choice cannot do: a CRC finds accidents, not an attacker, and Strata does not sign
exports (`worlds/export`). Common mistakes: allocating what a size field says, checking after use, joining threads on
close. The exercise corrupts a pack in a test and reads each failure's message.

**Leaves out.**

- Corruption sweeps and fuzzing as test machinery → `engineering/test-program`
- Atomic writes, private files and TOCTOU → `core/files`
- Font files as untrusted input → `gpu/text`
- The game manifest as untrusted input → `worlds/game-identity`
- Untrusted clients of the editor's automation server → `automation/security`
- Saves that never lose data in the editor → `editor/saving`

**Fit.** `fits`: about 4,500 words against L (5,000). Three concepts from zero, a table and four short excerpts take the
most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:351` | concept | home | Untrusted input and corruption |
| `assets:355` | concept | home | Crash-safe bookkeeping: write-ahead ordering |
| `assets:359` | concept | home | Cancellation and editor responsiveness |
| `assets:173` | feature | home | The pack's validation on open, sizes bounded by the file |
| `foundation:158` | feature | home | `BinaryReader` and `BinaryWriter`: little-endian, bounds-checked reads whose failure sticks, the pattern loaders of cooked data use (`ParseCookedTexture` reads through it) |
| `assets:430` | code | home | `Strata/src/Strata/Asset/AssetPack.cpp:271-292`: header and table checksums, with the block checks at 388-405 |
| `assets:444` | code | home | `StrataTests/src/Asset/AssetPackTests.cpp:1008-1030`: the "any single changed byte" sweep |
| `new:20` | code | home | `Strata/src/Strata/Asset/ImportRecordStore.h:31-48`: the record store's design, append-only and crash-safe |
| `new:21` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:57-68`: the limits that keep hostile files from exhausting memory, time or the stack |
| `assets:552` | rule | home | Every loader rejects truncated or garbage bytes; format changes extend the corruption tests |
| `assets:600` | hands-on | home | Corrupt a pack and read the failures |
| `assets:132` | feature | use | The import record store (taught in `assets/importing`) |
| `assets:138` | feature | use | Import cancellation (taught in `assets/importing`) |
| `assets:395` | code | use | Cache files published before their record (home `assets/importing`) |
| `assets:535` | rule | use | Cache before record |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Packs, blocks and their tables | `assets/packs-export` | must |
| Import records, and how cache files are published | `assets/importing` | must |
| CRC checksums | `basics/data-formats` | must |
| Atomic writes and TOCTOU | `core/files` | must |
| Atomic flags, and joining threads | `basics/threads` | must |
| Writing and running one test case | `core/first-change` | must |
| Corruption sweeps and fuzzing in general | `engineering/test-program` | helps |
| Untrusted fonts | `gpu/text` | helps |
| Signed exports, and the manifest as untrusted input | `worlds/game-identity` | helps |

## `assets/extending` — Tutorial: adding an asset type

**Covers.** What you will make: a new asset type in the engine, a plain text asset (`.sttxt`, stored as its source, as
the inventory's hands-on proposes), from its `AssetType` value to a file the editor imports and a game loads, with the
tests the engine's rules ask for. The sections follow the checklist of `Docs/DeveloperGuide.md`, "Adding an asset
type". Section 1, the type: append a value to `AssetType` (never insert one: packs and records store the numbers), give
it a name, and write the `Asset` subclass, whose `GetMemoryUsage` reports its bytes in the CPU pool. Section 2, the
loader: register it in the registration function of the module that owns the type, take the bytes over with
`TakeBytes`, and reject what is not valid UTF-8 or is too large; the loader runs on a worker and returns no asset when it
fails. Section 3, the importer: one that stores its source after checking it, on the model of the font importer,
registered in `RegisterAssetPipeline`, at version 1. Section 4, the tests: a round trip, and truncated and garbage
stored forms rejected without a crash, with the layering test still passing. Section 5, the feature test: an asset of
the new type with its `.meta` in `StrataTests/FeatureTest/Assets`, because the feature test fails when a registered type
has none.

Each section ends with a checkpoint of the patch, and its "You should see" is the build or the test output. The
exercises make it the reader's own: an importer setting with an inactive reason and a version bump; a manager
extension that counts its updates and adds a statistic; a document type that names other assets and records its
references. At the end the reader has changed the engine the way the part's pages describe, and has seen each rule of
the checklist hold in a test.

**Leaves out.**

- The checks of the feature test in full → `engineering/feature-test`
- Corruption sweeps and their machinery → `engineering/test-program`
- An asset type that uploads to the GPU in steps → `assets/uploads`
- A component with an asset property → `capstone/build`

**Fit.** `fits`: about 4,200 words against L (5,000). Five sections of two or three steps each, the quoted hunks of the
patch, and three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:585` | hands-on | home | Add a toy asset type: the page's example, from the type to the feature test |
| `assets:588` | hands-on | home | Exercise: an importer setting with `GetInactiveReason` and a version bump |
| `assets:606` | hands-on | home | Exercise: a manager extension that counts its updates and adds a statistic |
| `new:22` | code | home | `Strata/src/Strata/Asset/AssetImporters.cpp:140-155`: the font importer, which stores its source after checking it, the model for the page's importer |
| `assets:39` | feature | use | The type enum is append only |
| `assets:55` | feature | use | `RegisterAssetPipeline` |
| `assets:56` | feature | use | Manager extensions, for the second exercise |
| `assets:136` | feature | use | Import settings, for the first exercise |
| `assets:218` | feature | use | The feature test fails when a registered type has no asset |
| `assets:382` | code | use | The `Asset` base class |
| `assets:386` | code | use | Loaders registered by a module, `TakeBytes` |
| `assets:543` | rule | use | Report memory per pool |
| `assets:552` | rule | use | Loaders reject garbage without crashing |
| `assets:554` | rule | use | A new document type records its references, for the third exercise |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source and running one test | `core/first-change` | must |
| Adding a component, its registration and the feature test's minimum | `world/tutorial-component` | must |
| The `Asset` base class, loaders and their registry | `assets/loading` | must |
| Importers, `RegisterAssetPipeline`, settings and versions | `assets/importing` | must |
| `.meta` files and handles | `assets/handles-meta` | must |
| Loaders that reject truncated and garbage bytes | `assets/robustness` | must |
| UTF-8 | `basics/bytes` | must |
| The finalize contract | `assets/uploads` | helps |
| References a document records | `assets/references` | helps |
| The feature test in full | `engineering/feature-test` | helps |
| Corruption sweeps | `engineering/test-program` | helps |

**Starting state.** The engine's source at the pin, built as `core/first-change` teaches, with no patch applied: the
tutorial's patch starts from the pin (`startsFrom` `{"pin": true}`), not from the WindZone chain of
`world/tutorial-component`.

**Command-only steps.** none

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `assets:141` | feature | `editor/trash-references` | The asset file actions (moves, the trash, restores) are taught with the commands and undo steps that run them |
| `assets:142` | feature | `editor-ui/lists` | The folder index is what `AssetBrowserView` reads instead of the disk; a reader looks for it with the Content Browser's lists |
| `assets:143` | feature | `editor/saving` | Background saves of the engine's documents (`ClaimDocumentWrite`) belong with the `DocumentSaver` |
| `assets:216` | feature | `editor/thumbnails` | Thumbnails read the cooked header and mip tail by range; the content stamp that keys their cache is `assets/importing`'s |
| `assets:157` | feature | `light/sky` | What `HDRSun` finds and paints out is the sky page's; `assets/texture-cooking` gives the setting |
| `assets:159` | feature | `audio/clips-voices-sources` | The audio importer is taught with audio clips, beside `audio-input:52`; `assets/importing` keeps a row of its table of importers |
| `assets:161` | feature | `image/grading` | The color lookup importer and the `.cube` format are taught with lookup tables |
| `assets:165` | feature | `light/material-data` | The grayscale bit and the XY normal decode are read in the material's GPU record |
| `assets:187-188`, `assets:190-191`, `assets:193`, `assets:206` | feature | `draw/mip-streaming` | Prefix loads, range reads, the texture streamer, raising and dropping levels, the switch and slots resolved every frame are the home list of mip streaming |
| `assets:200`, `assets:202-203`, `assets:205` | feature | `gpu/upload-queue` | `PlanStep`, the staging pool, the transfer queue and `PrepareBackBuffer` are the mechanism that page owns |
| `assets:212` | feature | `reference/commands` | The asset group's commands are listed in the catalogue; each is named on the page of its subject |
| `assets:213` | feature | `editor-ui/instrument-panels` | The Streaming panel is one of the instrument panels; `assets/residency` shows what it measures |
| `assets:214` | feature | `draw/asset-requests` | The streaming view is read there; its mip view half is `draw/mip-streaming`'s |
| `assets:215` | feature | `editor-ui/inspectors` | The Content Browser's drop and the Asset Inspector's settings are drawn by the editor's UI |
| `assets:217` | feature | `worlds/export` | The export as a whole polls imports, plans and writes the pack |
| `assets:218` | feature | `engineering/feature-test` | What the feature test checks is taught there; `assets/extending` uses the asset-type check |
| `assets:339` | concept | `draw/mip-streaming` | Partial residency and mip streaming |
| `assets:377` | code | `world/ecs` | `UUID.h` is the home excerpt of UUIDs as stable identities; `assets/handles-meta` quotes it |
| `assets:434`, `assets:436` | code | `draw/mip-streaming` | `ReadPrefix` with the mip tail's range, and the wanted level's mathematics |
| `assets:438` | code | `nowhere` | Repeats `render-core:455`, the same `PlanStep` excerpt |
| `assets:487`, `assets:500`, `assets:506`, `assets:509` | figure | `draw/mip-streaming` | The mip streaming loop, the mip view, the fade-in and the resident tail against level 0 |
| `assets:502` | figure | `draw/asset-requests` | The streaming view is read where draw-time requests are taught |
| `assets:511` | figure | `light/sky` | An HDR sky with and without its sun shows what `HDRSun` does |
| `assets:513` | figure | `editor/trash-references` | A delete refused with its list of users |
| `assets:514` | figure | `editor-ui/status` | The status bar's assets pill |
| `assets:556` | rule | `draw/mip-streaming` | Bindless slots resolved every frame, because mip streaming replaces them |
| `assets:557` | rule | `nowhere` | Repeats `scene-ecs:548`, the same rule for scene documents |
| `assets:604` | hands-on | `draw/mip-streaming` | The wanted level computed by hand |
| `assets:628` | hands-on | `editor/trash-references` | A safe delete and its restore by undo |
| `assets:660` | term | `nowhere` | Repeats `foundation:551` (Registry) |
| `assets:682` | term | `nowhere` | Repeats `render-core:699` (Frames in flight) |
| `assets:692` | term | `nowhere` | Repeats `render-core:744` (upload budget, step and granule; the granule is `PlanStep`'s) |
| `assets:693` | term | `nowhere` | Repeats `render-core:743` (Staging buffer) |
| `assets:694`, `assets:697` | term | `gpu/upload-queue` | The staging pool and queue ownership transfers are that page's mechanism |
| `assets:695` | term | `nowhere` | Repeats `render-core:698` (Fence, event query) |
| `assets:696` | term | `nowhere` | Repeats `render-core:690` (Transfer queue) |
| `assets:700` | term | `nowhere` | Repeats `render-core:712` (Bindless) |
| `assets:701` | term | `nowhere` | Repeats `render-core:715` (Texture table) |
| `assets:703-709` | term | `draw/mip-streaming` | Mip tail, mip streaming, partial load, range read, wanted level, texel density, fade-in |
| `assets:712` | term | `basics/color` | sRGB's home is the color primer |
| `assets:722-723` | term | `nowhere` | Repeat `foundation:643` (FNV-1a, CRC-32C, SHA-256, HMAC) |
| `assets:727` | term | `nowhere` | Repeats `scene-ecs:663` (Cooked scene) |
| `assets:731` | term | `nowhere` | Repeats `foundation:628` (Atomic write) |
| `assets:733` | term | `nowhere` | Repeats `editor-core:714` (Referencer) |
| `assets:734` | term | `nowhere` | Repeats `editor-core:713` (Trash) |
| `assets:735` | term | `nowhere` | Repeats `foundation:561` (Layer table) |
| `assets:736` | term | `nowhere` | Repeats `foundation:549` (Composition root) |
| `assets:737` | term | `nowhere` | Repeats `foundation:565` (Service, engine service) |
| `assets:789`, `assets:795`, `assets:799`, `assets:801`, `assets:805` | open | `nowhere` | Surveyor's notes on what was not read or not dated and on the sources; the cooked mesh form they name is `new:9` on `assets/models-gltf`, and `STAU`, `STLU` and STSC are `audio-input:50`, `render-image:131` and `scene-ecs:161` |
| `assets:802` | open | `draw/gpu-driven` | Whether the GPU's visibility feedback feeds the texture streamer beyond `ReportView` is that page's to settle |

## Not taken

none

## Questions for the planner

none
