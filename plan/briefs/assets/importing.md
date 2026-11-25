# Brief: `assets/importing`

| Field | Value |
| --- | --- |
| Title | Importing: from source files to engine data |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `assets/handles-meta`, `world/reflection`, `core/jobs`, `core/files` |
| From | assets; import records, cache validity, dependencies, settings as properties, background imports, cancellation, hot reload of assets |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `asset-scan` | Asset scan | - |
| `cancellation-flag` | Cancellation flag | - |
| `content-stamp` | Content stamp | - |
| `dependency-import` | Dependency (import) | - |
| `file-watcher` | File watcher | - |
| `import-cache` | Import cache | - |
| `import-memory-admission` | Import memory admission | - |
| `import-record` | Import record | - |
| `import-record-store` | Import record store | - |
| `import-settings` | Import settings | - |
| `importer-version` | Importer version | - |
| `racily-clean` | Racily clean | - |
