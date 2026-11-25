# Brief: `assets/packs-export`

| Field | Value |
| --- | --- |
| Title | Asset packs, export and patches |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `assets/references` |
| From | assets; the pack: format, planning, pruning, `AlwaysInclude`, patches, cooked documents and when the export cooks them (the export as a whole is `worlds/export`'s) |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `asset-pack` | Asset pack | .stpak |
| `block-pack` | Block (pack) | - |
| `first-use-order` | First-use order | - |
| `patch-pack` | Patch pack | - |
| `pruning` | Pruning | `AlwaysInclude` |
| `zstd` | zstd | - |
