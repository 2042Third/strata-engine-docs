# Brief: `assets/what-is-an-asset`

| Field | Value |
| --- | --- |
| Title | What an asset is |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `basics/data-formats`, `core/layers-registries`, `world/ecs` |
| From | assets; sources and cooked forms, the editor's side and the game's side, the pipeline at a glance (registries and seams) |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `asset-manager` | Asset manager | - |
| `cook` | Cook | - |
| `cooked-asset` | Cooked asset | - |
| `engine-native-asset` | Engine-native asset | - |
| `import` | Import | - |
| `importer` | importer | - |
| `stored-form` | Stored form | - |
