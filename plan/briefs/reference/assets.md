# Brief: `reference/assets`

| Field | Value |
| --- | --- |
| Title | Asset types, file formats, importer versions, budgets and statistics |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `assets/handles-meta` |
| From | assets ch. 14 "Reference"; `AssetResidencyBudgets`, `AssetManagerStats`; importer versions parsed from each importer's `GetVersion` |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/assets` — Asset types, file formats, importer versions, budgets and statistics

**Covers.** The paragraph on top says what the page is: the asset types, the importers with their versions, the stored
forms, the residency budgets with their defaults and the statistics the asset manager reports, parsed at the pin. The
generated tables, in this order: (1) the asset types of `enum class AssetType`, in their stored order (append only),
each with its name, its native extension where the engine writes the type itself (`.stscene`, `.stprefab`, `.stmat`,
`.stanimator`, `.stworld`), the module that registers its loader and the importer that makes it; (2) the importers,
each with the source extensions it reads and `GetVersion()` as `:value{key="importer.<type>.version"}`, so no version
is typed (a bump of a version re-imports every asset of the importer); (3) the residency budgets of
`AssetResidencyBudgets`: the pools (GPU textures, GPU buffers, CPU), the default shares of the device's memory budget,
the bytes in flight, the upload and finalization budgets per frame and the staging budget, with `c_AssetUploadStepBytes`;
(4) the fields of `AssetManagerStats`, which `asset.stats` returns and the Streaming panel shows. Hand-written: a
hand-checked table of the stored forms, each with its version constant, its reader and the page that teaches it: the
`.meta` sidecar, the cooked texture "STTX" v2 and its block sizes, the asset pack "STPK" v2 with its v1 still read,
patch packs, the cooked mesh "STMH" v3 with its versions 1 and 2 still read (`Mesh::c_CookedVersion`;
`assets/models-gltf`), the cooked color lookup "STLU" v1 (`ColorLookup::c_FormatVersion`; `image/grading`) and the
import records file `ImportRecords.log` v1 in the project's cache folder (`ImportRecordStore::c_Version`;
`assets/importing`); two more rows name the cooked audio clip "STAU" and the cooked scene "STSC" and link the rows of
`reference/audio-input` and `reference/scene` that state them; one sentence on how budgets are changed
(`asset.setBudget` in the editor, `--asset-budget-mb` in the runtime); a short table of the Streaming panel's columns,
checked against `StreamingPanel.cpp`; the erratum on where the budgets come from (`new:3`); and `## Where it lives in
Strata`: `AssetTypes.h`, `AssetImporters.cpp`, each importer's header, `AssetResidency.h`, `AssetManager.h`,
`AssetPack.h`, `CookedTexture.h`, `Mesh.h`, `ColorLookup.h`, `ImportRecordStore.h`, `StreamingPanel.cpp`. The tool is
`tools/reference.py parse`, route "asset types and importers", and from v0.8.1 the command `asset.types`.

**Leaves out.**

- What an asset is, handles and `.meta` files → `assets/what-is-an-asset`, `assets/handles-meta`
- Importing, the import cache and settings → `assets/importing`
- How textures are cooked and compressed → `assets/texture-cooking`
- Residency, eviction and pins → `assets/residency`
- Budgeted uploads → `assets/uploads`
- Packs and export → `assets/packs-export`
- The `asset.*` commands with their parameters → `reference/commands`
- The runtime's options → `reference/worlds-runtime`
- Bringing assets into a game, for game makers → `make/assets`

**Fit.** `fits`: about 1,150 words against M (3,000). The generated tables give the page its size: the 13 asset types,
the importers with their versions, the residency budgets and the fields of `AssetManagerStats`, about 1,500 words. The
prose is the paragraph on top (250 words), four table introductions (200), the stored-forms table with its introduction
(seven rows and two that link, 290), the sentence on budgets (40), the Streaming panel's eight columns (135), the
erratum (100) and the strip (130).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:3` | erratum | home | `../pipelines.md` §7.1 takes the asset budgets from "the asset settings sections of the settings dump", but no asset settings section exists at the pin: the budgets are the defaults of `AssetResidencyBudgets`, shares of the device's memory budget, changed by `asset.setBudget` and the runtime's option, and the statistics are `AssetManagerStats`, which `asset.stats` returns. The page parses them from the headers and says so. Evidence: `Strata/src/Strata/Asset/AssetResidency.h:34-71` (the struct and its defaults); `Strata/src/Strata/Asset/AssetResidency.cpp:31-40` (`FromDeviceBudget`: 50% and 15% of the device's budget); `Strata/src/Strata/Asset/AssetManager.cpp:218-222` (the defaults from the device's memory budget); `Strata/src/Strata/Asset/AssetManager.h:31` (`AssetManagerStats`); `StrataEditor/src/Editor/EditorStreamingCommands.cpp:164`, `:218` (`asset.stats`, `asset.setBudget`); `StrataRuntime/src/RuntimeApplication.cpp:349` (`--asset-budget-mb`); `git grep -n "section.Id = " 822a7a46 -- Strata/src StrataEditor/src` finds the eight sections the engine and the editor register, none of them an asset section |
| `assets:38-48` | feature | link | Handles, the 13 types, native extensions, states, the base class, metadata, `.meta` sidecars, sub-assets, derived handles, built-in assets and duplicate handles |
| `assets:101` | feature | link | `AssetResidencyBudgets` and its defaults |
| `assets:108` | feature | link | `AssetManagerStats` |
| `assets:110` | feature | link | The budget controls |
| `assets:132` | feature | link | The import record store's file `ImportRecords.log` and its version, a row of the stored-forms table |
| `assets:152-161` | feature | link | The importers, from the native importer to the color lookup importer |
| `assets:162-163` | feature | link | The cooked texture "STTX" v2 and the block sizes |
| `assets:172` | feature | link | The pack format v2 |
| `assets:175` | feature | link | Packs of version 1, still read |
| `assets:180` | feature | link | Patch packs |
| `assets:199` | feature | link | The upload step and `c_AssetUploadStepBytes` |
| `assets:212-214` | feature | link | The asset commands, the Streaming panel and the asset debug views |
| `render-core:246` | feature | link | The asset types the renderer registers |
| `render-image:131` | feature | link | The cooked color lookup "STLU" v1, a row of the stored-forms table |
| `audio-input:50` | feature | link | The cooked clip "STAU", a row of the stored-forms table that links `reference/audio-input` |
| `scene-ecs:161` | feature | link | The cooked scene "STSC", a row of the stored-forms table that links `reference/scene` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an asset is; handles and `.meta` files | `assets/handles-meta` | must |
| Importing and import versions | `assets/importing` | helps |
| Residency pools, budgets and eviction | `assets/residency` | helps |
| Bytes, KiB and MiB | `basics/numbers` | helps |
| Texture block compression | `assets/textures` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-3 | should | missing-item | new item on `reference/assets` | No page lists the material's properties: the 29 reflected properties of `Material` (from `BaseColor` to `AttenuationDistance`) with their types, ranges, units (`EmissiveIntensity` in nits, `Thickness` in mesh units), options (`AlphaMode`) and defaults, which `material.create`, `material.set` and the Inspector take by name. The `.stmat` document (Format "Material", Version 1) has no row in any formats table, and the dump runs no `material.get`, so no generated table holds them. | `reference/assets` adds a generated table of the material properties from `material.get {material: "Builtin/DefaultMaterial"}` (each property's type, range or options, and the default material's value), with an introduction that names `light/materials` and `make/materials`, and a `.stmat` row in the stored-forms table that links `light/material-data`. About 80 words. `../pipelines.md` §7.2 adds the step to `dump`. | `allocation/reference.md:385-406`; `../pipelines.md:1120-1125`; `allocation/light.md:268`; `Strata/src/Strata/Renderer/Material.cpp:13-87`, `:102`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:1089-1113`; `Strata/src/Strata/Asset/AssetTypes.cpp:51` |
| critic-reference-4 | should | missing-item | `reference/assets`: the importers table and the `.meta` row | The importers table gives each importer's extensions and version only. No page lists the import settings of the four importers that have them (texture: `Usage`, `Compression`, `Quality`, `GenerateMips`, `Filter`, `Wrap`, `MaxSize`, `FlipVertically`, `FlipGreen`, `RemoveSun`; model: `Scale`, `GenerateLODs`, `LODCount` and eight more; audio; color lookup: `Size`) with their types, options, defaults and inactive reasons, though `asset.setImportSettings` and every `.meta` file use them by name. | The importers table gains each importer's settings as generated rows (name, type, range or options, default, inactive reason), from a parse of each `GetSettingsProperties` or from `asset.info` on one fixture per importer (a route the planner adds); the `.meta` row of the stored-forms table names its keys. About 60 words of introduction, naming `assets/texture-cooking`, `assets/models-gltf` and `audio/clips-voices-sources`. | `allocation/reference.md:389-391`, `:395-397`; `Strata/src/Strata/Asset/AssetImporter.h:104-114`; `Strata/src/Strata/Asset/TextureImporter.cpp:377`; `Strata/src/Strata/Asset/GltfImporter.cpp:2067`; `Strata/src/Strata/Asset/AssetImporters.cpp:102`; `Strata/src/Strata/Asset/ColorLookupImporter.cpp:342`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:1053-1057` |
| critic-reference-8 | should | missing-item | new items on `reference/assets`, `reference/renderer`, `reference/script-api` | The other area pages have a parsed table of limits, and `appendix/not-in-strata` sends "caps and limits of the features Strata has" to `reference/renderer`, but these three pages have none. Unlisted at the pin: a texture's longest side of 16,384 texels and 2^28 decoded pixels, a glTF scale of at most 10,000, 8 levels of detail, a hierarchy depth of 1,024 and a 64 MiB document, 4,096 joints per mesh, built-in handles 1 to 255; 32,768 bindless textures, 256 GPU timestamps a frame, a 2 GiB geometry pool, the draw key's submesh and LOD bits, 8,192-texel cascades, the font limits; save file names of 64 characters and files of 64 MiB, 65,536 script classes, 4,096 fields a class, names of 1,024 bytes and strings of 256 MiB. | Each of the three pages adds a parsed limits table through `tools/reference-limits.json`, as `reference/physics` and `reference/ui` have, with one introduction that names the teaching page. About 40 words each. | `allocation/reference.md:385-406`, `:460-485`, `:5-28`; `allocation/appendix.md:48`; `Strata/src/Strata/Asset/TextureImporter.h:84`; `Strata/src/Strata/Asset/TextureImporter.cpp:24`; `Strata/src/Strata/Asset/GltfImporter.cpp:68-74`; `Strata/src/Strata/Asset/GltfImporter.h:54`; `Strata/src/Strata/Renderer/Mesh.h:46`; `Strata/src/Strata/Asset/Asset.h:36`; `Strata/src/Strata/Renderer/GraphicsDevice.h:135`; `Strata/src/Strata/Renderer/GPUProfiler.h:95`; `Strata/src/Strata/Renderer/GeometryPool.h:87`; `Strata/src/Strata/Renderer/SceneDrawKey.h:28-29`; `Strata/src/Strata/Renderer/RendererQuality.h:191`; `Strata/src/Strata/Renderer/FontValidation.h:47-58`; `Strata/src/Strata/Core/SaveFiles.h:23-24`; `Strata/src/Strata/Scripting/ScriptModule.cpp:55-57`, `:957`, `:1046`; `Strata/src/Strata/Scripting/ScriptValue.h:17` |
