---
id: assets/importing
title: "Importing: from source files to engine data"
description: "How Strata keeps each asset's stored form current with its source, its settings and the files it reads, in the background and without stalls."
kind: internals
size: XL
tracks: [E]
needs: [assets/handles-meta, world/reflection, core/jobs, core/files]
time: 125
learn:
  - id: why-reimport
    text: explain why an asset is or is not imported again, key by key
  - id: record-keys
    text: name the keys of an import record and what each one protects
  - id: publish-order
    text: explain why cache files are renamed into place before their record is set
  - id: write-importer
    text: write an importer that the cache, cancellation and hot reload treat right
  - id: hot-reload
    text: trace how a changed file reaches an asset that is already loaded
since: 0.3.0
status: final
---

A person drops a photo, a model or a font into the project, and the game needs that file in a form the engine can load in a few milliseconds. The :term[importer]{id=importer} of the file's type does the conversion, and its result sits in a cache. This page is about everything around that conversion. It covers when the conversion runs, when it is skipped, how it stays off the :term[main thread]{id=main-thread} and how it stops when nobody wants it any more. The texture and model importers do the format work and have their own pages, and what the loaders do with the :term[stored forms]{id=stored-form} belongs to the loading page.

The job of the import system is narrow. It keeps every asset's stored form current with its source, its settings and the other files that the import read. It never repeats work that is current, and it never stalls the editor.

## The problem and how engines solve it

Start from what the reader sees. A project holds 3,000 :term[source files]{id=source-file}, and the average import takes 1 s. Importing all of them at every start costs 3,000 s, which is 50 minutes before the first frame. Importing none of them is no better: the first edit of a texture would show the old picture. Between these two sits one question that the system answers for every file at every start: "is the stored form I made last time still the form I would make now?"

:::example[Ten files, one edit]
A small project has 10 textures. On Monday you open it: all 10 import, and each import leaves a stored file and a note about the source, which is the **import record**.

On Tuesday you open it again and change nothing: 10 questions, 10 answers "current", 0 imports, so the project opens in the time it takes to read 10 notes. Then you set `MaxSize` of one texture to 1024. That setting changes the output, so 1 import runs and 9 stay current. Last, you edit a model that reads two textures: the model imports again, and its 2 textures do not, because their own sources did not change.
:::

A note about the last import makes the questions cheap. An **import record** is what the editor remembers of an asset's last import: the versions and :term[hashes]{id=hash} it used, the files it read and the assets the result references. The record must hold enough that a changed answer to any of these questions appears:

- Did the source file change?
- Did the person change the settings?
- Did the importer's code change, so the same source now gives another result?
- Did another file that the import read change?
- Did the last import fail, so that nothing is stored?

Other :term[build systems]{id=build-system} ask the same questions with different answers. The table shows the approaches that matter for Strata. Compare them as you read: the cost of a check is paid at every start, and the cost of a wrong answer is paid by the person who sees a stale picture.

| Technique | Who uses it | What it checks | Cost and weakness |
| --- | --- | --- | --- |
| File times | `make` | The source is newer than the output | Cheap; a file copied or moved by a branch switch has a new time without new contents, and one written within the clock's resolution may keep its time |
| Content hashes | `Bazel` | A hash of the source and of every input | Exact; the check reads every :term[byte]{id=byte} of every input at every start |
| Hashes plus a time cache | `git` index | Size and time first, a hash only when they differ | Cheap and exact, but it needs a rule for times too recent to trust |
| Import records | Strata | Importer version, settings hash, source size and time, dependencies, success | One short record per asset; the time check and the hash together; the record must be written safely |

Strata uses the third row for the source and adds the other keys from the second. File times alone fail on a branch switch: every file gets a new time, and all 3,000 assets would import again. Hashes alone fail on speed: reading 4 GB of sources at 500 MB/s takes 8 s before any work starts. The mixed rule reads a hash only when the size matches and the time does not, which is the case of a copy or a branch switch.

:::elsewhere[Time checks, hashes and git]
The `make` tool compares file times, `Bazel` keys its outputs on content hashes, and `git` keeps a size and a time per file in its index and compares contents when the two differ. The `git` documentation calls a file whose time is too recent to trust "racily clean". Strata took the term and the rule from :term[git]{id=git}, as its own code comments say.
:::

A second problem is time. A cook of one large texture takes seconds, and the editor must keep drawing frames while it runs. So the whole system works in the background, and the rest of this page is as much about doing less work on the main thread as about deciding which work to do. The first half answers "should this asset import?" and the second half answers "how does it run without anyone noticing?"

## The map

The map has five parts that own different things. The figure after the list shows how they connect. Keep the thread of each part in mind: the main thread decides and applies, and the background threads read, think and write.

- The **asset scan** is the background registration of a project's assets when it opens. A job walks the `Assets/` folder and prepares the files in batches of 256. The main thread's `Update` inserts them in slices of about 1 ms.
- The import jobs run one importer each. A job checks the record first and runs the importer only when the cached import is stale, after admission (a memory check).
- `BackgroundWork` is everything that the jobs share with the manager: the record store, the :term[file lock]{id=file-lock}, the job list, the admission counters. Jobs hold only this object, never the manager itself. The file lock has two modes: many readers hold it shared at the same time, and a step that renames, moves or deletes files holds it exclusive, alone.
- The **import record store** is the single file `ImportRecords.log` that holds the records of all assets, one line per entry.
- The **import cache** is the folder `.strata/Cache/` of the project, with one file `<HANDLE>.bin` for each asset and each :term[sub-asset]{id=sub-asset}: the stored forms of imported assets. It is derived data, never committed, and safe to delete.

```mermaid caption="The import system: the main thread decides and applies, jobs on background threads check records, import and write the cache." alt="A diagram with the main thread on the left and background threads on the right. The scan job and the import jobs read the record store and write the cache folder. The main thread's Update inserts scan results and applies finished imports."
flowchart LR
  subgraph Main["Main thread"]
    Update["EditorAssetManager::Update"]
    Watch["File watcher poll"]
  end
  subgraph Back["Background threads"]
    Scan["Scan job: walk, prepare in batches of 256"]
    Jobs["Import jobs: check record, admit, import"]
  end
  Work["BackgroundWork: shared state and file lock"]
  Store["ImportRecords.log"]
  Cache[".strata/Cache/HANDLE.bin"]
  Watch --> Update
  Update -- "queue" --> Jobs
  Update -- "slices of 1 ms" --> Scan
  Scan --> Work
  Jobs --> Work
  Work --> Store
  Work --> Cache
  Jobs -- "outcomes" --> Update
```

The map hides one more rule that shapes the code: no file work on the main thread. The scan reads the `.meta` files, hashes files and checks records on jobs, so that `Update` only inserts the results into the registry. A test compares `FileSystem::GetThreadOperationCount` before and after `Update` applies a scan, and fails when the count grows.

## The contract

An importer is a class derived from `AssetImporter`. It converts one kind of source file into the stored form that the asset loaders read, and it runs on a background thread. The rules below say what the manager assumes about it and what it may assume about the manager. Each rule comes with its reason, because a rule without one gets broken.

An importer answers these questions:

- `GetType` names the :term[asset type]{id=asset-type} it produces, and `GetExtensions` the extensions it takes, lower case with the dot (`.png`).
- `GetName` names the importer for tools: the name of its asset type unless it gives its own ("glTF", "Native").
- `GetVersion` returns a number. It goes up whenever the output format changes.
- `StoresSourceDirectly` says that the stored form is the source file itself, so nothing is cached.
- `Import` converts. It fills an `ImportResult`: the bytes, sub-assets, warnings and the dependencies it read.
- `GetDefaultSettings`, `GetSettingsProperties` and `GetInactiveReason` describe the settings.
- `EstimateImportMemory` says how much memory an import takes at its peak, and `FindExternalFiles` names the files a model brings along.

Four terms from this list need a plain definition. **Import settings** are the per-asset options of an importer, such as `MaxSize` of a texture, stored in the `ImportSettings` object of the asset's `.meta` file and merged over the importer's defaults.

The **importer version** is a number that an importer raises when its output changes, so that every cache made by the older code counts as stale.

A **dependency** (import) is another file that an import read besides its source, whose change imports the asset again: a model's buffers and images are the usual case.

The **cancellation flag** is an atomic flag in the `ImportContext` that an importer checks to learn that nobody wants its result any more.

Five rules follow from these definitions. Each is a rule of Strata's developer guide, and each has a section below that shows the code behind it.

:::rule[Bump the version when the output changes]
Raise `GetVersion()` whenever an importer's output changes. The version is a key of cache validity, so a stale cache would look current. The texture importer and the glTF importer both cook textures, so a change to the cooker raises both. [The cache validity section](#the-real-code-is-a-cached-import-current) shows the key.
:::

:::rule[Read other files through the dependency call]
An import reads its source through `ReadImportSource` and every other file through `ReadImportDependency`. The second call keeps the read inside the asset folder and records the file, so a changed image imports its model again. [The confined reads section](#the-real-code-confined-reads-and-settings) shows how.
:::

:::rule[Check for cancellation every few milliseconds]
A long importer asks `ImportContext::IsCancelled` every few milliseconds. If it does not, closing a project or moving a file must wait until the import ends. [The cancellation section](#the-real-code-cancellation-memory-and-failures) shows what waits.
:::

:::rule[No waiting, no file work on the main thread]
The editor never waits for a background import and does no file work on the main thread. Frames must stay short, so jobs prepare and `Update` only inserts. [The map](#the-map) shows the split.
:::

:::rule[Rename first, set the record second]
An import renames its cache files into place first and sets their record second. Both steps happen under the exclusive file lock, and only while someone still wants the import. A record then never names a missing file, and a cancelled import never publishes. [The publishing section](#the-real-code-publishing-an-import) shows the order.
:::

Two more promises hold for every importer. First, it touches no engine state except through its `ImportContext`: the context carries the handle, the source path, the settings, a function to resolve other files to handles and the file reader. Second, a failure returns `false` with a message in `outError`. It never asserts, because a broken file is user input, and it never throws out of the importer: the manager catches exceptions at the call site and turns them into a failed import.

## A toy version

Before the real code, a toy that holds the central idea in one short program. Its "files" are strings and its "clock" is a counter, so the program runs the same every time. The class `ToyImportCache` keeps a record per path: the importer version, a hash of the settings, the source's size and time, and a hash of the contents. `Get` asks `FindStaleReason` whether the record still matches. Look at three things: the order of the checks, the way a changed time without changed contents is accepted, and `GetRecordableTime`, which refuses to trust a time that is too recent.

```cpp sketch="assets-importing-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <functional>
#include <string>
#include <unordered_map>

struct SourceFile
{
	std::string Bytes;
	int64_t Time = 0;
};

struct Record
{
	uint32_t ImporterVersion = 0;
	size_t SettingsHash = 0;
	size_t Size = 0;
	int64_t Time = 0; // 0: unknown, the contents are compared
	size_t ContentHash = 0;
};

class ToyImportCache
{
public:
	void Get(const std::string& path, const SourceFile& source, uint32_t version, const std::string& settings, int64_t now)
	{
		const size_t settingsHash = std::hash<std::string> {}(settings);
		const char* reason = "no record";
		auto it = m_Records.find(path);
		if (it != m_Records.end())
			reason = FindStaleReason(it->second, source, version, settingsHash, now);
		if (!reason)
		{
			std::printf("%s: current\n", path.c_str());
			return;
		}
		std::printf("%s: import (%s)\n", path.c_str(), reason);
		m_ImportCount++;
		Record record;
		record.ImporterVersion = version;
		record.SettingsHash = settingsHash;
		record.Size = source.Bytes.size();
		record.Time = GetRecordableTime(source.Time, now);
		record.ContentHash = std::hash<std::string> {}(source.Bytes);
		m_Records[path] = record;
	}

	int GetImportCount() const { return m_ImportCount; }
private:
	// A time within two ticks of now cannot vouch for the contents: the file may change again in the same tick.
	static int64_t GetRecordableTime(int64_t time, int64_t now) { return now - time < 2 ? 0 : time; }

	static const char* FindStaleReason(Record& record, const SourceFile& source, uint32_t version, size_t settingsHash, int64_t now)
	{
		if (record.ImporterVersion != version)
			return "importer version";
		if (record.SettingsHash != settingsHash)
			return "settings";
		if (record.Size != source.Bytes.size())
			return "size";
		if (record.Time == source.Time)
			return nullptr;
		if (record.ContentHash != std::hash<std::string> {}(source.Bytes))
			return "contents";
		record.Time = GetRecordableTime(source.Time, now); // Only the time changed: compare contents once
		return nullptr;
	}
private:
	std::unordered_map<std::string, Record> m_Records;
	int m_ImportCount = 0;
};

int main()
{
	ToyImportCache cache;
	SourceFile file { "AAAA", 10 };
	cache.Get("Wall.png", file, 1, "mips=on", 100);
	cache.Get("Wall.png", file, 1, "mips=on", 101);
	cache.Get("Wall.png", file, 1, "mips=off", 102);
	file.Time = 50; // Touched: a copy or a checkout
	cache.Get("Wall.png", file, 1, "mips=off", 103);
	file = { "BBBB", 200 }; // Edited at tick 200
	cache.Get("Wall.png", file, 1, "mips=off", 200);
	file = { "CCCC", 200 }; // Edited again in the same tick, same size
	cache.Get("Wall.png", file, 1, "mips=off", 200);
	cache.Get("Wall.png", file, 2, "mips=off", 300);
	std::printf("imports: %d\n", cache.GetImportCount());
	return 0;
}
```

```text output-of="assets-importing-toy.cpp"
Wall.png: import (no record)
Wall.png: current
Wall.png: import (settings)
Wall.png: current
Wall.png: import (contents)
Wall.png: import (contents)
Wall.png: import (importer version)
imports: 5
```

1. **Line 31:** `Get` asks the record first; with none, the reason is "no record".
2. **Line 51:** A time less than 2 ticks old is stored as 0: the toy's form of racily clean.
3. **Line 62:** Equal size and time end the check without reading any contents.
4. **Line 65:** Only the time changed and the contents match, so the record takes the new time.

The output is the story of one file through seven calls. Call 1 has no record, so it imports. Call 2 finds every key equal: current. Call 3 changes the settings text, so the settings hash differs and the import runs again.

Call 4 only touches the file: the time is new but size and contents are not, so the record takes the new time and no import runs. In call 5 the file changes at tick 200 and is imported at tick 200. Its time is less than 2 ticks old, so the record stores the time as 0, meaning "unknown".

Call 6 shows why. The file changes again within the same tick and keeps its size and its time. A record that had stored 200 would call it current and keep the old picture. The stored 0 forces a content comparison, which finds the change. Call 7 raises the importer's version, which no source key can see.

The toy omits five things that the real code must do. It runs on the calling thread, it reads no other files, it writes nothing to disk, it never stops half way, and its record cannot be damaged by a crash. The sections below add them one by one.

## The real code: the registry and the simplest importer

Importers register in `AssetImporterRegistry`, which finds them by extension, ignoring case. Later registrations win, so a tool or a test can replace a built-in importer.

The registry opens only when a program calls `RegisterAssetPipeline`. The editor and other tools pass that function to the engine as `ModuleRegistrationOptions::AssetPipeline`. A shipped game never opens the registry, so a game contains no importer code at all: it reads the stored forms that the editor made. Using the registry before it opens fails an `ST_CORE_VERIFY`.

In the editor, a file under `Assets/` becomes an asset when an importer knows its extension. The manager that does this is `EditorAssetManager`; the [page on handles](handles-meta.md) shows what an asset's handle and `.meta` file are. The simplest importer shows the whole interface with almost no format work. Read `NativeAssetImporter` and search for what it validates and what it does not store.

```cpp src="Strata/src/Strata/Asset/AssetImporters.cpp#L35-L81"
// Assets the engine writes itself (materials, prefabs, scenes, animation controllers, worlds) are stored as their JSON source. Importing only
// validates the document with the type's loader.
class NativeAssetImporter final : public AssetImporter
{
public:
	NativeAssetImporter(AssetType type, std::string_view extension)
		: m_Type(type), m_Extension(extension)
	{
	}

	AssetType GetType() const override { return m_Type; }
	std::string GetName() const override { return "Native"; }
	std::vector<std::string> GetExtensions() const override { return { m_Extension }; }
	uint32_t GetVersion() const override { return 1; }
	bool StoresSourceDirectly() const override { return true; }

	bool Import(const ImportContext& context, ImportResult& result, std::string* outError) const override
	{
		if (!ReadSource(context, result.Data, outError))
			return false;

		const AssetLoadFunction* loader = AssetLoaderRegistry::Find(m_Type);
		if (!loader)
		{
			if (outError)
				*outError = fmt::format("No loader for asset type {}", AssetTypeToString(m_Type));
			return false;
		}

		AssetMetadata metadata;
		metadata.Handle = context.Handle;
		metadata.Type = m_Type;
		metadata.Path = FileSystem::ToUTF8(FileSystem::GetRelativePath(context.SourcePath, context.AssetDirectory));
		std::string error;
		AssetLoadData document { std::span<const uint8_t>(result.Data) }; // Validated, not taken over: it is the stored form
		if (!(*loader)(metadata, document, &error))
		{
			if (outError)
				*outError = error.empty() ? std::string("Invalid document") : error;
			return false;
		}
		return true;
	}
private:
	AssetType m_Type;
	std::string m_Extension;
};
```

1. **Line 46:** Each native type gets its own instance, but all share one name, so tools list "Native" under each of those types.
2. **Line 49:** The stored form is the source, so no cache file is written.
3. **Line 53:** The source is read through the helper that the importers share.
4. **Line 56:** The loader of the asset's type does the checking; with none, the import fails with a message.
5. **Line 69:** The loader reads the bytes but does not take them over, because they are the stored form.

The native importer handles the documents that the engine writes itself, so the stored form is the source. The importer only checks the document with the loader of its type, and a document that the loader rejects fails the import with the loader's message. Because `StoresSourceDirectly` is true, the manager never writes a cache file for these assets and never queues a background import for them. A change to such a file takes another path, which a later section shows.

The built-in importers fill one table. Texture and glTF have their own pages, the audio importer belongs to the clips page and the lookup importer to the grading page.

| Importer | Extensions | Stored form | Version |
| --- | --- | --- | --- |
| Native | `.stscene`, `.stprefab`, `.stmat`, `.stanimator`, `.stworld` | The source document, checked by its loader | 1 |
| Texture | `.png`, `.jpg`, `.jpeg`, `.tga`, `.bmp`, `.psd`, `.gif`, `.hdr` | A cooked texture with its mip levels, see [texture cooking](texture-cooking.md) | 5 |
| glTF | `.gltf`, `.glb` | A model template plus meshes, materials, textures, skeletons and clips as sub-assets, see [glTF models](models-gltf.md) | 11 |
| Audio | `.wav`, `.mp3`, `.flac`, `.ogg` | A small :term[header]{id=header} and the encoded file, see [clips and voices](../audio/clips-voices-sources.md) | 1 |
| Font | `.ttf`, `.otf` | The source file, accepted when `Font::Create` parses it | 1 |
| Color lookup | `.cube` | A cooked lookup table at the size its `Size` setting names (33 points each way by default), see [grading](../image/grading.md) | 1 |

You can also ask a running editor for this table. The command `asset.types` lists every asset type with the extension of the documents the engine writes for it, or null for a type that is only imported. Each type carries its importers, each with its name, its version and its extensions.

The command needs no open project. `Mesh`, `Skeleton` and `AnimationClip` list no importer: they are sub-assets that a model's import makes. Run it from a shell with `StrataCLI call asset.types`, or as the tool of the same name over the Model Context Protocol (MCP). Three of its entries look like this:

```json
{
  "types": [
    { "type": "Scene", "nativeExtension": ".stscene",
      "importers": [ { "name": "Native", "version": 1, "extensions": [ ".stscene" ] } ] },
    { "type": "Model", "nativeExtension": null,
      "importers": [ { "name": "glTF", "version": 11, "extensions": [ ".gltf", ".glb" ] } ] },
    { "type": "Mesh", "nativeExtension": null, "importers": [] } ]
}
```

The versions are the useful part. After an engine update, compare them with the ones you saw before: a type whose version went up imports all its files again when the project opens.

The font importer is as simple as the native one: it stores the file as it is after `Font::Create` accepts it. The check is real work, because anyone can supply a font file. A shipped game loads the stored copy, and a damaged font must fail at import time, in the editor, and not on a player's machine.

## The real code: the scan

When a project opens, `BeginScan` returns at once. A job on the background threads does the slow part in two steps. First it walks `Assets/` and lists every file and folder.

Then it prepares each file, in batches of 256. It reads the `.meta` (or makes a handle and writes one), picks the importer, checks the cached import against its record and finds the assets that documents reference. It also removes cache files that nothing uses.

`GetScanProgress` reports three phases: Walking, Registering and Applying. In the last phase the main thread works.

Each call to `Update` inserts prepared entries into the registry for about 1 ms and reads the clock once every 64 entries. A project of 100,000 assets therefore applies over many frames and never in one long frame. Both numbers are fields of `AssetRegistrationOptions`, which tests replace with a clock of their own.

:::example[A start with one stale asset]
A project has 1,200 assets and one changed texture. The scan job prepares 1,200 files in 5 batches: four of 256 files and a last one of 176. Of these, 1,199 find a current record and 1 is stale.

Applying 1,200 entries at 64 per clock read reads the clock about 19 times. The stale asset becomes a background import job. Until its import ends, a load of that asset waits for it instead of failing.
:::

The editor wants the project usable at once, so the import of stale assets runs in the background too. Tools and tests have a blocking form, `Scan`, which waits for the scan and inserts everything at once, so that their runs stay :term[deterministic]{id=determinism}.

## The real code: the cache and its records

The cache folder holds two kinds of files. The cooked data of each asset has the file name `<HANDLE>.bin`. Sub-assets have handles of their own, derived from the parent's handle and the sub-asset's key, so a model's mesh has a file next to the model's. The second kind is the record file.

The **import record store** is the single file `ImportRecords.log` that holds the records of all assets. It replaced one small file per asset, because thousands of tiny files are slow to open and likely to be left half written.

The file is an append-only log. Its first line is a header, `{"Format":"ImportRecords","Version":1}`. Every line after it has an eight-digit :term[hexadecimal]{id=hexadecimal} :term[CRC-32C]{id=crc-32c}, a space and a compact :term[JSON]{id=json} entry.

There are three kinds of entry: a record of a handle, a path of a handle and a removal of a handle. The latest entry of a handle wins. Appending a line is the only write the store makes in normal work, so a crash can damage at most the last line.

A line with a wrong :term[checksum]{id=checksum} is skipped when the file loads, and a torn last line is cut off. The asset behind a skipped line has no record, so it imports again: the worst result of damage is repeated work, never a wrong answer. When dead entries outnumber live ones and the file is larger than 1 MiB, the writer rewrites the whole file from memory with an :term[atomic write]{id=atomic-write}. Older projects with one `.import` file per asset are migrated on the first load, and the old files are removed after the store has written them.

A record is a :term[JSON object]{id=json-object}. For the texture `Wall.png` it looks like this in the log, shortened and with example numbers:

```json
{"Handle":"8A3A2A1312934026","Record":{"Format":"ImportRecord","Version":2,"Source":"Textures/Wall.png","ImporterVersion":5,"SettingsHash":"0F2B9C4E11A07D35","SourceSize":2491832,"SourceTime":133812345678901234,"SourceHash":"5D3E0A9B77C1F2E8","Success":true,"Error":"","Warnings":[],"References":[],"SubAssets":[],"Dependencies":[]}}
```

Read the keys as the answers to the questions of the problem section: `ImporterVersion`, `SettingsHash`, `SourceSize` with `SourceTime` and `SourceHash`, `Dependencies` and `Success`. The `Version` key is the record format's own version, 2 at the pin, so that a record of an older layout counts as stale too. The hashes use :term[FNV-1a]{id=fnv-1a}, a fast hash that is not safe against attackers: here the files belong to the project owner, and the hash only has to catch accidents.

## The real code: is a cached import current?

The central decision lives in two places: `IsFileCurrent` answers it for one file, and the head of `LoadCurrentImport` applies it to a whole import. The decision tree comes first, then the code.

```mermaid caption="The decision tree of cache validity: any failing check imports the asset again; only a source whose size and time or contents match stays current." alt="A flow chart that starts with the record and goes through five checks: record format, importer version and settings hash, success, source file, and each dependency. Any No answer ends in import again. A source with a new time but the same contents refreshes the recorded time and stays current."
flowchart TD
  A["Record found?"] -- no --> X["Import again"]
  A -- yes --> B["Record format, importer version, settings hash all equal?"]
  B -- no --> X
  B -- yes --> C["Last import succeeded?"]
  C -- no --> X
  C -- yes --> D["Source size equal?"]
  D -- no --> X
  D -- yes --> E["Source time equal?"]
  E -- yes --> G["Each dependency: same existence, size and time?"]
  E -- no --> F["Hash of source equal?"]
  F -- no --> X
  F -- yes --> H["Refresh recorded time"] --> G
  G -- no --> X
  G -- yes --> I["Cache file exists? Then current"]
```

First the part about times. A file system keeps times at a fixed resolution: some keep 100 ns, some 10 ms and the oldest 2 s. A file written twice inside that resolution keeps its time. The first function turns a time that is too recent into 0, and the second function compares a file with a recorded state. The word to find in the comment is the term the whole mechanism is named after.

```cpp src="Strata/src/Strata/Asset/EditorAssetManager.cpp#L162-L193"
// File systems keep times at a resolution (NTFS 100 ns, exFAT 10 ms, FAT and HFS+ 2 s): a file written again within it
// keeps its time. A record must not vouch for a time so recent that the file may still change without changing it, or
// an edit of the same size right after would pass for the recorded contents: such times are recorded as unknown (0),
// so the next check compares contents and records the time once it is old enough (as git treats racily clean files).
int64_t GetRecordableTime(int64_t time)
{
	using Clock = std::filesystem::file_time_type::clock;
	constexpr auto c_TimeResolution = std::chrono::seconds(2);
	const int64_t now = Clock::now().time_since_epoch().count();
	const int64_t window = std::chrono::duration_cast<Clock::duration>(c_TimeResolution).count();
	return now - time < window ? 0 : time;
}

// Whether a file is in the state a record noted: same size and time, or only the time changed (a checkout, a copy)
// but not the contents. A refreshed time is written into the state (outChanged), so contents are compared once (again
// while the time is too recent to vouch for, see GetRecordableTime).
bool IsFileCurrent(const std::filesystem::path& path, nlohmann::json& state, std::string_view sizeKey, std::string_view timeKey, std::string_view hashKey,
	bool& outChanged)
{
	const std::optional<uint64_t> size = FileSystem::GetFileSize(path);
	const int64_t time = FileSystem::GetLastWriteTime(path).value_or(0);
	if (!size || *size != JsonUtils::GetUInt(state, sizeKey, UINT64_MAX))
		return false;
	if (time == JsonUtils::GetInt(state, timeKey, 0))
		return true;
	const std::optional<uint64_t> hash = HashFile(path);
	if (!hash || HashToString(*hash) != JsonUtils::GetString(state, hashKey))
		return false;
	state[std::string(timeKey)] = GetRecordableTime(time);
	outChanged = true;
	return true;
}
```

1. **Line 172:** A time younger than the 2-second window is recorded as 0.
2. **Line 185:** Equal size and equal time: the file is current, and no byte is read.
3. **Line 187:** The time differs, so the contents are hashed and compared.
4. **Line 190:** The refreshed time goes into the record's state, and the caller writes the record back.

A file is **racily clean** when its modification time is too recent to prove that it has not changed again. Strata records such a time as 0, which means "unknown", and the next check compares contents. The window is 2 seconds, the coarsest resolution that the comment lists. The cost is one extra hash of a file that was imported within 2 seconds of its last edit, which is rare.

Now the whole check for one asset. Read the order: the cheap keys come first, the hash of the source comes only when size matches and time does not, and dependencies come last because they need extra reads.

```cpp src="Strata/src/Strata/Asset/EditorAssetManager.cpp#L1959-L2006"
bool EditorAssetManager::BackgroundWork::LoadCurrentImport(const ImportRequest& request, ImportOutcome& outOutcome, const std::atomic<bool>* cancel) const
{
	if (IsCancelled(cancel))
		return false;
	std::optional<nlohmann::json> record = Records.FindRecord(request.Handle);
	if (!record || !record->is_object())
		return false;
	// The source and its dependencies may be hashed: read under the shared file lock, like every read of project files
	// off the main thread (a move or delete of a file an open reader holds fails on Windows).
	std::shared_lock<std::shared_mutex> fileLock(FileMutex);

	if (JsonUtils::GetUInt(*record, "Version", 0) != c_ImportRecordVersion
		|| JsonUtils::GetUInt(*record, "ImporterVersion", 0) != request.Importer->GetVersion()
		|| JsonUtils::GetString(*record, "SettingsHash") != HashToString(HashSettings(request.Settings))
		|| !JsonUtils::GetBool(*record, "Success", false))
		return false;

	// Refreshed times are written back so the contents are compared once (IsFileCurrent).
	bool recordChanged = false;
	const std::filesystem::path sourcePath = ToAbsolute(request.Path);
	if (!IsFileCurrent(sourcePath, *record, "SourceSize", "SourceTime", "SourceHash", recordChanged))
		return false;

	ImportOutcome outcome;
	outcome.Handle = request.Handle;
	outcome.Success = true;
	outcome.FromCache = true;
	outcome.SourceSize = JsonUtils::GetUInt(*record, "SourceSize", 0);
	// The file's own time (the record may hold none for a time too recent to vouch for): the file is current.
	outcome.SourceTime = FileSystem::GetLastWriteTime(sourcePath).value_or(0);

	if (auto dependencies = record->find("Dependencies"); dependencies != record->end() && dependencies->is_array())
	{
		// Relative references resolve against the source's place: a moved model reads different files.
		if (!dependencies->empty() && JsonUtils::GetString(*record, "Source") != request.Path)
			return false;
		for (nlohmann::json& dependency : *dependencies)
		{
			const std::string path = JsonUtils::GetString(dependency, "Path");
			if (path.empty() || !dependency.is_object())
				return false;
			const std::filesystem::path dependencyPath = ToAbsolute(path);
			const bool exists = FileSystem::IsRegularFile(dependencyPath);
			if (exists != JsonUtils::GetBool(dependency, "Exists", false) || (exists && !IsFileCurrent(dependencyPath, dependency, "Size", "Time", "Hash", recordChanged)))
				return false;
			outcome.Dependencies.push_back(path);
		}
	}
```

1. **Line 1961:** A cancelled job stops at once, before it reads anything.
2. **Line 1968:** Hashing reads project files, so the job holds the shared lock.
3. **Lines 1970–1973:** The cheap keys come first: record format, importer version, settings hash and success.
4. **Line 1979:** The source file is checked with the time-then-hash rule.
5. **Line 2002:** Each dependency must exist as before and pass the same rule.

If every check passes, the rest of `LoadCurrentImport` rebuilds the outcome from the record, checks that the cache file of the asset and of each sub-asset exists, and returns it as "from cache". The record is rewritten only when a time was refreshed, and then under the exclusive lock and only while the job is not cancelled.

:::why[The importer's version is a key]
Imagine that a fix to the texture cooker changes the pixels of every normal map, and nobody raises `GetVersion()`. Every project keeps its caches, the records match on size, time and settings, and the editor calls all of them current. The old, wrong data stays until a person changes each texture by hand.

The version is the only key that sees code changes, so raising it is part of the fix. The cost is that every project imports all assets of that type again once, at the first start after an update. A change to an importer's memory estimate raises nothing, because it changes no output. Adding a key to the importer's defaults also imports everything once, because the settings hash covers the merged settings.
:::

The decision stays inside the import system. Other systems ask "did this asset's stored form change?" across sessions, and they cannot ask the record store.

The **content stamp** is the answer: a 64-bit number made from the source file's size and time, the import settings, the importer's version and whether the import succeeded. `GetContentStamp` formats these values into one string and hashes it, so equal states give equal stamps in every session. A sub-asset uses the stamp of its parent asset.

The thumbnail cache, the world cook and the asset bounds compare stamps with the ones they stored. A different stamp means their data is stale.

## The real code: confined reads and settings

An importer must not read the disk as it likes. A model names its images by relative path, and a hostile model could name `../../secret.txt`, or a symbolic link inside the project could lead out of it. `ReadImportDependency` is the single door. It refuses paths outside the asset folder, notes the file's state before reading it and records the dependency even when the file is missing. Look at how it treats a file that is missing, a file that cannot be read and a file that is fine.

```cpp src="Strata/src/Strata/Asset/AssetImporter.cpp#L317-L347" symbol="ReadImportDependency"
std::optional<std::vector<uint8_t>> ReadImportDependency(const ImportContext& context, ImportResult& result, const std::filesystem::path& path)
{
	const std::filesystem::path normalized = path.lexically_normal();
	const std::filesystem::path assetDirectory = context.AssetDirectory.lexically_normal();
	if (!FileSystem::IsInside(normalized, assetDirectory))
		return std::nullopt;

	ImportDependency dependency;
	dependency.Path = normalized;
	dependency.Exists = FileSystem::IsRegularFile(normalized);

	// The state is taken before reading: a change while reading then shows as a later modification.
	std::optional<std::vector<uint8_t>> bytes;
	if (dependency.Exists)
	{
		dependency.Size = FileSystem::GetFileSize(normalized).value_or(0);
		dependency.Time = FileSystem::GetLastWriteTime(normalized).value_or(0);
		// A link leading out of the asset directory is not read.
		if (FileSystem::IsInsideResolved(normalized, assetDirectory))
			bytes = context.ReadFile ? context.ReadFile(normalized) : FileSystem::ReadBytes(normalized);
		if (bytes)
			dependency.Hash = Hash::FNV1a(std::span<const uint8_t>(*bytes));
		else
			dependency.Size = ImportDependency::c_Unreadable; // Never current: retried until the file can be read
	}

	const bool known = std::any_of(result.Dependencies.begin(), result.Dependencies.end(), [&](const ImportDependency& existing) { return existing.Path == normalized; });
	if (!known)
		result.Dependencies.push_back(std::move(dependency));
	return bytes;
}
```

1. **Line 326:** Whether the file exists is noted first; a missing file is a state too.
2. **Line 335:** A link that leads out of the asset folder is never read.
3. **Line 340:** A file that cannot be read gets a size that never matches.
4. **Lines 343–345:** Each file is recorded once, however often the importer reads it.

The state is taken before the read, so a change during the read appears later as a newer time. A file that exists but cannot be read gets the size `c_Unreadable`, which never matches, so the import runs again at every check until the file can be read. A missing file is recorded as missing, so creating it later changes the answer of the check, which is the case of the sketch in the exercises. The read itself goes through `ImportContext::ReadFile`, which the editor implements under the shared file lock and which refuses once the import is cancelled.

:::why[Why one door for all reads]
If importers opened files themselves, three things would break. A move or delete of a file would fail on Windows while an import holds the file open. A dependency read without a record would never trigger a re-import. And a path that leaves the project would give a shared project a way to read files of the machine. One function fixes all three, so the rule is that importers have no other way to read.
:::

Settings are properties, like the properties of components. An importer lists them in `GetSettingsProperties` with an `ImportSettingsBuilder`: a name, a type, a default and a range, plus calls that add a tooltip and a display name. The Asset Inspector draws them with the same reflection that draws any component, so a new setting needs no editor code. Look at the end of the texture importer's list: the bounded number with `PowerOfTwoLimit`, and the setting `FlipGreen`.

```cpp src="Strata/src/Strata/Asset/TextureImporter.cpp#L393-L406"
.UInt("MaxSize", defaults.MaxSize, c_MaxImageDimension).PowerOfTwoLimit()
	.Tooltip("Longest side in pixels: larger images are scaled down, keeping their aspect ratio. No limit (0): only the engine's limit")
.Enum("Filter", { "Linear", "Nearest" }, TextureFilterToString(defaults.Filter))
	.Tooltip("Linear blends neighboring texels; Nearest keeps them sharp (pixel art)")
.Enum("Wrap", { "Repeat", "Clamp", "Mirror" }, TextureWrapToString(defaults.Wrap))
	.Tooltip("What texture coordinates outside 0..1 show: the texture repeated, its edge, or the texture mirrored")
.Bool("GenerateMips", defaults.GenerateMips)
	.Tooltip("Store the smaller versions of the image that keep distant surfaces from shimmering")
.Bool("FlipVertically", defaults.FlipVertically)
	.Tooltip("Store the image upside down (for images whose rows start at the bottom)")
.Bool("FlipGreen", defaults.FlipGreen).DisplayName("Flip Green (DirectX normal map)")
	.Tooltip("Invert the green channel: normal maps made for DirectX (+Y down, names with \"dx\" such as \"rocks_nor_dx_2k\") "
		"store it the other way round from the OpenGL convention Strata reads")
.Bool("RemoveSun", defaults.RemoveSun).DisplayName("Remove Sun")
```

1. **Line 393:** A bounded number that the inspector offers as "No limit" and powers of two.
2. **Line 403:** A setting with its own display name and a tooltip; its :term[inactive reason]{id=inactive-reason} lives in `GetInactiveReason`.

Three details matter. Every key of `GetDefaultSettings` needs a property. A tool that asks for a value outside the range gets a refusal with the range in the message, never a quiet clamp, because whoever asked must learn that the value was wrong. `NormalizeImportSettings` does this check.

And some settings stop mattering in some states. `GetInactiveReason` returns a sentence for such a case. For `FlipGreen` while the usage is not `NormalMap`, the sentence says that Flip Green applies to normal maps only. The inspector shows the setting disabled with that sentence, and the stored value stays valid.

## The real code: publishing an import

After the check fails, `RunImport` does the work. It first notes the source's size, time and hash, so a change during the import is still seen as a change. It builds the `ImportContext` and calls the importer inside a `try` block that turns any exception into a failed import.

Then it looks at the cancellation flag again, because a result computed for a wanted import may arrive after the import was cancelled. Last, it records the dependencies, also for failed imports, because creating a missing file must start the import again.

The next two quotes are the heart of safety. The first writes the cache files under temporary names. The second takes the exclusive lock, checks the flag one last time and renames. Read the first for where the lock is not held.

```cpp src="Strata/src/Strata/Asset/EditorAssetManager.cpp#L2147-L2189"
// Cache files are written under temporary names first: only replacing them takes the file lock, so loads are not
// blocked while a large import writes. The staged files and the record are published together under the exclusive
// lock, after a last look at the cancellation flag: a move or delete sets it before it changes files under that lock,
// so an import it cancelled never stores what it read, and nothing of a cancelled import is left.
std::vector<std::pair<std::filesystem::path, std::filesystem::path>> stagedFiles;
auto removeStaged = [&stagedFiles]()
{
	for (const auto& [stagedPath, cachePath] : stagedFiles)
		FileSystem::Remove(stagedPath);
};
bool staged = true;
if (!outcome.Success)
{
	outcome.Error = error.empty() ? std::string("Import failed") : error;
}
else
{
	const uint64_t stagingNumber = NextStagingNumber.fetch_add(1);
	auto stage = [&](AssetHandle handle, std::vector<uint8_t>& data, uint64_t& outSize)
	{
		outSize = data.size();
		// Nothing more is written once the import is cancelled.
		bool written = false;
		if (!IsCancelled(cancel))
		{
			std::filesystem::path stagedPath = GetCachePath(handle);
			stagedPath += fmt::format(".staged{}", stagingNumber);
			written = FileSystem::WriteBytes(stagedPath, data);
			stagedFiles.emplace_back(stagedPath, GetCachePath(handle));
		}
		std::vector<uint8_t>().swap(data); // Free the memory now: imports can be large
		return written;
	};
	staged = stage(request.Handle, result.Data, outcome.StoredSize);
	outcome.SubAssetStoredSizes.resize(result.SubAssets.size());
	for (size_t index = 0; index < result.SubAssets.size(); index++)
	{
		ImportedSubAsset& subAsset = result.SubAssets[index];
		// Frees every sub-asset's data
		staged = stage(DeriveSubAssetHandle(request.Handle, subAsset.Key), subAsset.Data, outcome.SubAssetStoredSizes[index]) && staged;
	}
	outcome.SubAssets = std::move(result.SubAssets);
}
```

1. **Line 2164:** The staging number makes the temporary names of each import unique.
2. **Line 2174:** The write goes to a temporary name, outside the exclusive lock, and only while the import is wanted.
3. **Line 2177:** The buffer is freed as soon as it is written, because imports can be large.

A large import can write a great deal of data. Writing under a temporary name needs no lock, so loads of other assets are not blocked while it writes. The number in the name comes from `NextStagingNumber`, so two imports of the same asset, a cancelled one that still runs and the one that replaced it, never write the same file. Each buffer is freed right after it is written, because imports can be large.

The second part publishes.

```cpp src="Strata/src/Strata/Asset/EditorAssetManager.cpp#L2191-L2234"
std::unique_lock<std::shared_mutex> fileLock(FileMutex);
if (IsCancelled(cancel))
{
	fileLock.unlock();
	removeStaged();
	return stopped();
}
if (outcome.Success)
{
	bool written = staged;
	for (const auto& [stagedPath, cachePath] : stagedFiles)
		written = written && FileSystem::Rename(stagedPath, cachePath);
	if (!written)
	{
		removeStaged();
		outcome.Success = false;
		outcome.Error = fmt::format("Could not write imported data to '{}'", FileSystem::ToUTF8(Specification.CacheDirectory));
	}
}

nlohmann::json record = nlohmann::json::object();
record["Format"] = "ImportRecord";
record["Version"] = c_ImportRecordVersion;
record["Source"] = request.Path;
record["ImporterVersion"] = request.Importer->GetVersion();
record["SettingsHash"] = HashToString(HashSettings(request.Settings));
record["SourceSize"] = outcome.SourceSize;
record["SourceTime"] = GetRecordableTime(outcome.SourceTime);
record["SourceHash"] = sourceHash ? HashToString(*sourceHash) : std::string();
record["Success"] = outcome.Success;
record["Error"] = outcome.Error;
record["Warnings"] = outcome.Warnings;
record["References"] = ReferencesToJson(outcome.References);
record["Bounds"] = BoundsToJson(outcome.Bounds);
nlohmann::json subAssets = nlohmann::json::array();
for (const ImportedSubAsset& subAsset : outcome.SubAssets)
{
	subAssets.push_back({ { "Key", subAsset.Key }, { "Name", subAsset.Name }, { "Type", AssetTypeToString(subAsset.Type) },
		{ "References", ReferencesToJson(subAsset.References) }, { "Bounds", BoundsToJson(subAsset.Bounds) } });
}
record["SubAssets"] = std::move(subAssets);
record["Dependencies"] = std::move(dependencies);
// After the cache files are in place (the record never names one that is missing), still under the exclusive lock.
Records.SetRecord(request.Handle, record);
```

1. **Line 2191:** From here the lock is exclusive.
2. **Line 2192:** The last look at the flag: a cancelled import removes its staged files and stores nothing.
3. **Line 2202:** The renames put the cache files in place.
4. **Line 2234:** The record comes last, so it never names a file that is missing.

The lock is exclusive from the first line, which also stops any other job from reading the cache folder or moving files. Under it the code checks the flag a last time. A move or a delete sets the flag before it changes files under that lock, so an import that the move cancelled finds the flag set and removes its staged files.

Then the renames come, then the record, and the record is last on purpose. If the program dies after the renames, the cache holds a file that no record names, and the next scan imports the asset again. If the order were the other way round, a crash would leave a record that names a file that does not exist, and a reader would trust it.

:::example[Crash at each step]
Take an import that writes 2 cache files, a model and a mesh, and then the record. The steps are: write staged file 1, write staged file 2, rename 1, rename 2, set record. A crash before the first rename leaves two staged files that the next scan removes, and the record does not change. A crash after rename 1 leaves a new file 1 and an old record. The record's checks still compare with the source, and the next start imports again if anything differs.

A crash during the record write leaves a torn last line, which the loader cuts. No crash point gives a record that names a missing file. The full argument about crashes belongs to [the robustness page](robustness.md).
:::

## The real code: background imports and hot reload

The **file watcher** is the :term[operating system's]{id=operating-system} service that reports which files in a folder changed. The editor starts it in `BeginScan`, before the walk, so that a file added during the scan is never missed. Its reports wait until the scan is applied. After that, `Update` polls it and handles the changes in `ProcessFileChanges`. Removals are handled last, because a move arrives as a removal plus an addition, and the addition must find the asset at its old place to keep its handle and its cache.

A change takes one of four paths, depending on which file changed:

- A `.meta` file changed: the settings are read again, and when they differ from the ones in memory the asset queues an import.
- A file that an import read changed: `GetDependents` finds every asset that listed the file and queues them.
- A new file with a known extension: it is registered, gets a handle and a `.meta`, and imports.
- A changed source: the manager compares its size and time with the ones it knows. Writes that the editor made itself were recorded already and are skipped.

The last path decides between the two kinds of asset. Read the end of the function.

```cpp src="Strata/src/Strata/Asset/EditorAssetManager.cpp#L2983-L3016"
		// Our own writes (saves, moves) were recorded already; anything else is an external modification.
		const uint64_t size = FileSystem::GetFileSize(path).value_or(0);
		const int64_t time = FileSystem::GetLastWriteTime(path).value_or(0);
		bool direct = false;
		{
			std::scoped_lock<std::mutex> lock(m_SourceMutex);
			auto it = m_Sources.find(handle);
			if (it == m_Sources.end() || (it->second.SourceSize == size && it->second.SourceTime == time))
				continue;
			direct = it->second.Importer->StoresSourceDirectly();
			if (direct)
			{
				it->second.SourceSize = size;
				it->second.SourceTime = time;
			}
		}

		ST_CORE_INFO("Asset '{}' changed; reloading", ToRelative(path));
		if (direct)
		{
			SetStoredSize(handle, size);
			QueueNativeReferences(handle);
			ReloadAsset(handle);
		}
		else
		{
			QueueImport(handle);
		}
	}
}

////////////////////////////////////////////////////////////////////////////////
// Queries and file operations
////////////////////////////////////////////////////////////////////////////////
```

1. **Line 2983:** The editor's own writes were recorded already; the size and time tell an outside change.
2. **Line 2992:** A direct source has no import.
3. **Line 3005:** A direct source reloads at once.
4. **Line 3009:** Any other source queues a background import.

A direct source, such as a material, has no import. The manager updates its size and time, queues the search for the assets it references and calls `ReloadAsset`.

Any other asset queues a background import. `SubmitImport` hands it to the job system with `Background` priority, so that imports neither take the processors from the frame nor hold the I/O threads that stream assets. The job first tries `LoadCurrentImport`, so a file that was only touched finds its record current and does no import.

When the job finishes, `Update` applies the outcome with `ApplyImportOutcome`. That function registers the new sub-assets and forgets the ones that disappeared. It calls `ReloadAsset` for the asset and its sub-assets, unless the outcome came from the cache.

Settings changes use the same route. `SetImportSettingsInBackground` writes the settings into the `.meta` and queues an import, and `ReimportAssetInBackground` queues a forced one. Their twins without "Background" in the name block, and only tools and tests call them. `IsImportPending` tells whether the import of an asset is queued or running, and `HasPendingImports` tells whether any import is.

Hot reload of assets means loading an asset again after its file changed, while the program runs. The asset must not vanish while the new version loads, because a mesh that disappears for 200 ms would flicker in the scene. `ReloadAsset` keeps the old object until the new one is ready.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L739-L763" symbol="AssetManagerBase::ReloadAsset"
void AssetManagerBase::ReloadAsset(AssetHandle handle)
{
	bool wasRequested = false;
	{
		std::scoped_lock<std::mutex> lock(m_Mutex);
		auto it = m_Entries.find(handle);
		if (it == m_Entries.end() || it->second.IsMemoryAsset)
			return;

		AssetEntry& entry = it->second;
		wasRequested = entry.State != AssetState::Unloaded;
		AbandonLoadLocked(entry); // A queued load of the old version is replaced by the new request
		// Keep serving the old object until the new one is ready, so users never see the asset disappear.
		SetStateLocked(entry, AssetState::Unloaded);
		entry.Generation = m_NextGeneration++;
		entry.SourceRevision = NextSourceRevision();
		// Without a loaded object the change is published now: unless the asset is requested, no arrival will tell caches
		// that keep data derived from it (evicted meshes' render layouts) that its source changed.
		if (!entry.Loaded)
			PublishContentChange(handle);
	}

	if (wasRequested)
		RequestLoad(handle, AssetPriority::High);
}
```

1. **Line 750:** A queued load of the old version is abandoned.
2. **Line 752:** The state is Unloaded, but the loaded object stays in the entry.
3. **Line 753:** The new generation makes late results of the old load stale.
4. **Line 762:** Only an asset that somebody requested loads again now.

Notice what the function does to the entry. A load of the old version that is still queued is abandoned, because the new request replaces it. The state returns to Unloaded, but the loaded object stays in the entry, so users keep drawing it.

The entry gets a new generation number. Every completion or range read that carries an older generation is discarded when it arrives, so a slow load of the old file can never replace the new one. Only an asset that somebody had requested loads again at once, with high priority. The others stay unloaded, and a content-change notice tells the caches that keep derived data.

Hot reload of scripts is another system with the same words: see [script hot reload](../scripting/hot-reload.md).

## The real code: cancellation, memory and failures

Every import is a `BackgroundJob` with an atomic cancellation flag. The manager cancels a job when its result would be out of date or unwanted. That happens when the file changed or moved, the settings changed, a new import replaced it, the asset was deleted or the project closed.

A queued job never starts. A running job stops at its importer's next check and stores nothing, because the publishing step looks at the flag under the lock. The manager does not wait for it: the jobs hold `BackgroundWork` only, so the manager may be gone while a cancelled job still runs.

How often must an importer check? The texture cooker checks per block of a compressed level, between mip levels and around decoding. The glTF importer checks between images, primitives and levels of detail. The rule says "every few milliseconds" because a check costs one relaxed atomic read, which is cheap, and the time a stop takes is the time between two checks. One block of a compressed texture level takes tens of microseconds, so a check per block costs next to nothing and a stop takes about a millisecond.

The loop of an importer that stops looks like this. Look at where the check stands: at the top of each unit of work, before the costly call.

```cpp pseudocode
// The shape of a cancellable loop
for (each mip level)
{
	if (context.IsCancelled())
	{
		*outError = "The import was cancelled";
		return false;
	}
	CookLevel(level);
}
```

1. **Line 4:** The check comes before the costly work of each unit.
2. **Line 9:** A unit of work runs only after the check passed.

A cancelled import fails and its result is discarded. The manager closes a project with `Close`, which cancels every job, drops results that were not applied and returns at once. Imports that did not finish run again at the next open, because their records were never written.

Memory needs a limit too. Cooking a 4096 by 4096 texture needs the decoded pixels and working copies, and 24 such imports at once need about 8 GB.

**Import memory admission** is the rule that background imports start only while the estimates of those that run fit a budget. The budget is a quarter of the physical memory, clamped between 1 GiB and 4 GiB.

`EstimateImportMemory` reads the head of the source: 64 KiB, or all of a smaller file. A texture estimates 20 bytes per pixel from the header (4 for the decoded pixel and 16 for the working copies). A glTF model estimates twice its buffers plus its images, never less than 4 times its file, and any other importer 4 times the size of the source.

:::example[Admission with 4 GiB]
A machine with 16 GiB has a budget of 4 GiB. A 4096 by 4096 texture has 16,777,216 pixels. At 20 bytes each its estimate is 335,544,320 bytes, which is 320 MiB. Twelve of them fit: 12 times 320 MiB is 3,840 MiB, and one more would make 4,160 MiB, which is more than 4,096 MiB.

So 12 run, and the other imports wait in order and hold no thread. When one finishes it gives its 320 MiB back and the next one starts. One import larger than the whole budget runs alone, because otherwise it would never run.
:::

The wait of a background import does not hold a thread: the job is put on a queue and the thread returns to the pool. A blocking import for tools and tests does wait on its thread, but only while an admitted import runs, because only running imports are sure to give their room back.

Failures need a voice. The log gets the message, and the person gets it too. Failures that nobody waited for are kept in a list of the latest 64, and the editor takes them with `TakeImportFailures`, which also reports how many failed in all.

A failed import keeps the previous sub-assets registered, so references to them survive until the source is fixed. Loading them reports the import error meanwhile.

One more flow imports files from outside the project. `ImportExternal` copies files or folders into `Assets/` on an I/O job, together with the files that a model names (`FindExternalFiles`), prepares them off the main thread and imports them in the background. A failed item is rolled back, its files removed again, unless the request says `KeepOnFailure`, and `CancelExternalImport` stops one that is running. Files that are still being copied are never imported: the watcher skips them until the copy is complete.

A last lock matters here. Background reads hold a shared file lock, and saves and moves hold an exclusive one, because Windows cannot move a file that another handle has open. The publishing step is the longest writer under the exclusive lock, which is why it does only renames and the record, never the heavy writes.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Time check only | `make` | No hashing at all | Wrong results after a copy or a branch switch, or a second edit in the same tick; or needless imports |
| Content hash of every input at every start | `Bazel` | An exact answer, also across machines | Reading every byte of every source at every start, a long wait for large projects |
| One record file per asset | Strata's own older layout | Simple to write, no log to repair | Thousands of small files, slow opens, half-written files that nothing detects |
| A shared cache across machines | Build systems with remote caches | A new machine imports nothing | A trusted server, and importers that give identical bytes everywhere |
| Import on demand when first used | Tools that convert lazily | No work for assets never used | A stall in the middle of play, and errors found late |
| Block the editor until the import ends | Simple tools | No state to manage | The behavior the cancellation work removed: the editor froze for seconds |

## How it is tested

Five suites cover this page, and each can run alone. `Asset.Editor` tests the manager, among others the scan, the hot reload of changed files and the removal of unused cache data.

`Asset.ImportRecords` tests the store: the append and reopen, the compaction, a crash cut at every byte of the last three entries and a process killed while it appends. `Asset.ImportSettings` tests how settings are described, checked and read, and the :term[inactive reasons]{id=inactive-reason} of settings.

`Asset.ImportCancellation` tests that closing, moving, deleting and new settings cancel only the jobs they should and that a cancelled import stores nothing. `Asset.ImportAdmission` tests the budget: imports wait without holding threads, one over the budget runs alone, and a bigger budget starts the waiting ones.

Run one suite with a filter, for example in the debug build on Windows:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Asset.ImportRecords
```

The cancellation tests use a gate: a test importer that holds at a gate until the test opens it, so the test knows an import is running, and then measures how long `Close` takes. A test that must wait does so by a clock or a condition, never by counting frames.

## Changing it safely

Three changes come up often, and each has a checklist.

To change an importer's output: raise `GetVersion()` in the same commit, because a stale cache looks current otherwise. Check that every consumer of the old format still reads the new one or that the loader rejects it. Run `Asset.Editor` and the importer's own suite.

To add an importer that reads other files: read them through `ReadImportDependency` only, so that the record knows them. Check `IsCancelled` between the big steps of the work. Return `false` and an error for bad input, and write a test with a truncated and a garbage file. Register the importer in `RegisterAssetPipeline`, and add the type to the feature test.

To add a setting: add the key to `GetDefaultSettings`, add its property with a range and a tooltip, and give it an inactive reason when another setting can disable it.

The settings hash covers all keys, so adding the key imports every asset of the type again once. Raise the version for a new setting only if old records without the key must be made again: the default value of a missing key already gives the old result.

The rules of the contract apply on top: no file work on the main thread, rename before the record, and no blocking waits. Before the commit run the five suites and the feature test.

## What went wrong before

Closing a project while 17 imports ran used to wait for every running cook to finish: 5.6 to 12 s on a fresh copy of the project made for stress tests. Moving or deleting an asset waited the same way. The cause was that importers had no way to learn that their work was unwanted. The fix gave them the cancellation flag in `ImportContext`, a file reader that refuses reads after cancellation and checks inside the texture cooker and the model importer, and then used these in the manager. The regression test is `Asset.ImportCancellation`: it holds imports at a gate, closes the manager and checks that the call returns at once and that nothing was stored.

## Summary

- An asset is imported again when any key of its import record differs: format version, importer version, settings hash, success, source size, time and contents, or a dependency.
- A record holds the importer version, the settings hash, the source's size, time and hash, the success flag, the references and the dependencies; each key guards one cause of a stale cache.
- Staged cache files are renamed into place and the record is set after them, under the exclusive lock and after a last look at the cancellation flag, so a record never names a missing file.
- A correct importer reads through `ReadImportSource` and `ReadImportDependency`, checks `IsCancelled` every few milliseconds, raises its version when its output changes and returns errors instead of throwing.
- A changed file reaches a loaded asset through the file watcher, a background import and `ReloadAsset`, which serves the old object until the new one is ready.

## Check yourself

1. A model imports fine on Monday. On Tuesday a teammate copies the project to a new disk, so every file has a new modification time and the same contents. Which of these happens when you open it?

   1. All assets import again, because the times differ.
   2. No asset imports again: each source's size matches, its hash matches, and the record takes the new time.
   3. Only the models import again, because they have dependencies.
   4. The editor refuses to open the project until the cache is deleted.

   :::answer{tests="why-reimport"}
   Option 2 is right. A different time with equal size sends the check to the hash, which matches, so the record's time is refreshed and the import is current. Option 1 is the weakness of a time-only check, which Strata avoids. Option 3 confuses dependencies: each dependency passes the same way, size and then hash. Option 4 invents a rule that does not exist.
   :::

2. The toy's record holds the time 0 for an edit made at tick 200 and imported at tick 200. A second edit at tick 200 keeps the size. Does the next `Get` import again, and which key finds the change?

   :::answer{tests="record-keys"}
   Yes. The record time is 0, which differs from 200, so the check compares contents, and the contents differ. The key that finds it is the content hash, reached through the time key. Without the rule that records a recent time as 0, the stored 200 would equal the file's time and the size would match, so the stale cache would count as current.
   :::

3. An import has written two staged files and holds the exclusive lock. The program is killed right after the first rename. What do the cache and the record show at the next start?

   :::answer{tests="publish-order"}
   The cache holds the first new file and an old second file or none, and the record is the old one or none, because the record is set last. The next check compares the record with the source and imports again if anything differs, or finds the cache file missing and imports. No record ever names a file that is missing. If the record had been set first, the check would trust it and load a missing or half-new set of files.
   :::

4. An importer for `.pal` palette files reads its source with `std::ifstream` and reads an image the palette names with `std::ifstream` too. Name two problems.

   :::answer{tests="write-importer"}
   The source read bypasses the context's reader: a move or delete of the file can fail on Windows while the import holds it, and the read cannot be refused after a cancellation. The fix is `ReadImportSource`. The image read is worse: no dependency is recorded, so an edit of the image never imports the palette again, and nothing keeps the path inside the asset folder. The fix is `ReadImportDependency`.
   :::

5. A person saves a new version of `Rock.png` while the scene shows it. Which sentence describes what the screen shows during the import?

   :::answer{tests="hot-reload"}
   The old texture stays on the screen. The watcher reports the file, a background import runs, and only when `Update` applies the outcome does `ReloadAsset` start the new load. During that load the old object keeps serving, and the new one replaces it when it is ready. Loads of the old version that finish late are discarded by their generation number.
   :::

## Exercises

1. **Basic.** Open a copy of a sample project, find the `.meta` file of a texture, and find the line of that texture in `.strata/Cache/ImportRecords.log`. Change one setting of the texture in the Asset Inspector, and find the new line. What differs between the two lines?

   :::answer[Worked solution]{tests="record-keys why-reimport"}
   Copy a sample with the launcher, so that the original stays unchanged, and open the project. Read the texture's handle in its `.meta` (the file next to the texture, for example `Wall.png.meta`). Search the log for that handle: the last line with `"Record"` is the current one. After the change, a new line with the same handle ends the file.

   Its `SettingsHash` differs. The size, time and hash of the source and the `ImporterVersion` stay equal, and the older line is still in the file as a dead entry. Read the files only: never edit the `.meta`.
   :::

2. **Medium.** A model reads `Crate.bin` and `Crate.png`, and `Crate.png` does not exist yet. Write a program that records the existence and the size of both files at import time. Then it says whether the import is current in three cases: nothing changed, `Crate.png` was created, and `Crate.png` was removed again while `Crate.bin` grew from 4 to 6 bytes. Predict the three answers first.

   :::answer[Worked solution]{tests="why-reimport" solution="sketches/assets-importing-dependency.cpp"}
   The program below keeps the state of each file the import read, also of the missing one, and compares the state again at each check. Look at `Observe`: it returns a state for a missing file instead of nothing.

   ```cpp sketch="assets-importing-dependency.cpp"
   #include <cstdio>
   #include <initializer_list>
   #include <map>
   #include <string>

   struct DependencyState
   {
   	bool Exists = false;
   	size_t Size = 0;
   };

   using Files = std::map<std::string, std::string>;
   using Record = std::map<std::string, DependencyState>;

   // Notes a file's state, also when the file is missing: creating it later must count as a change.
   DependencyState Observe(const Files& files, const std::string& path)
   {
   	const auto it = files.find(path);
   	if (it == files.end())
   		return { false, 0 };
   	return { true, it->second.size() };
   }

   Record Import(const Files& files)
   {
   	Record record;
   	for (const char* path : { "Crate.bin", "Crate.png" })
   		record[path] = Observe(files, path);
   	return record;
   }

   bool IsCurrent(const Record& record, const Files& files)
   {
   	for (const auto& [path, state] : record)
   	{
   		const DependencyState now = Observe(files, path);
   		if (now.Exists != state.Exists || now.Size != state.Size)
   			return false;
   	}
   	return true;
   }

   int main()
   {
   	Files files;
   	files["Crate.bin"] = "1234";
   	const Record record = Import(files);
   	std::printf("unchanged: %s\n", IsCurrent(record, files) ? "current" : "import again");
   	files["Crate.png"] = "pixels";
   	std::printf("png created: %s\n", IsCurrent(record, files) ? "current" : "import again");
   	files.erase("Crate.png");
   	files["Crate.bin"] = "123456";
   	std::printf("bin grew: %s\n", IsCurrent(record, files) ? "current" : "import again");
   	return 0;
   }
   ```

   ```text output-of="assets-importing-dependency.cpp"
   unchanged: current
   png created: import again
   bin grew: import again
   ```

   1. **Line 20:** A missing file still gives a state.
   2. **Line 28:** The import notes the state of every file it reads.
   3. **Line 37:** Existence and size are compared with the noted state.

   The first answer is "current": nothing changed. The second is "import again": `Crate.png` was missing at import time, so its state says that it does not exist, and now it exists. The third is "import again": the file is gone again, so the existence matches, but `Crate.bin` grew from 4 to 6 bytes. Because a missing file has a state, creating it counts as a change.
   :::

3. **Hard.** Trace it yourself: open a project with a debugger attached to the editor and put a breakpoint in `LoadCurrentImport`. For three assets, say which key of cache validity made each one current or imported again.

   :::answer[Worked solution]{tests="why-reimport write-importer"}
   The function is `EditorAssetManager::BackgroundWork::LoadCurrentImport` in `Strata/src/Strata/Asset/EditorAssetManager.cpp`, and `IsFileCurrent` in the same file answers for the source and each dependency.

   Step from the top. No record returns at the first lines. A difference in format version, `ImporterVersion`, `SettingsHash` or `Success` returns at the long condition.

   Then come `IsFileCurrent` of the source, `IsFileCurrent` of each dependency and the check of the cache file. The line where the function returns `false` names the key. For a current asset the function reaches the end and returns `true`. Search `LoadCurrentImport` to find the calls: `SubmitImport` is the one on the background threads.
   :::

## Where it lives in Strata

- Importer interface and registry: `Strata/src/Strata/Asset/AssetImporter.h` and `AssetImporter.cpp`; the built-in native, audio and font importers and `RegisterAssetPipeline` in `AssetImporters.cpp`.
- The manager: `Strata/src/Strata/Asset/EditorAssetManager.h` and `.cpp` (`BeginScan`, `BackgroundWork`, `LoadCurrentImport`, `RunImport`, `ProcessFileChanges`, `ApplyImportOutcome`, `GetContentStamp`, `TakeImportFailures`).
- The record store: `Strata/src/Strata/Asset/ImportRecordStore.h` and `.cpp`; the scan's options in `AssetRegistration.h`.
- Hot reload: `AssetManagerBase::ReloadAsset` in `Strata/src/Strata/Asset/AssetManager.cpp`; the watcher in `Strata/src/Strata/Core/FileWatcher.h`.
- Tests: `StrataTests/src/Asset/` (`EditorAssetManagerTests.cpp`, `ImportRecordStoreTests.cpp`, `ImportSettingsTests.cpp`, `ImportCancellationTests.cpp`, `ImportAdmissionTests.cpp`).

## Further reading

- The git documentation on racy git: what a "racily clean" entry is and how git handles it; advanced.
- The Bazel documentation on its caching and content-addressed outputs; intermediate.
- The `make` manual on how it decides that a target is out of date; beginner.
