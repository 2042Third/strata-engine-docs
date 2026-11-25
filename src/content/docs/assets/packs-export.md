---
id: assets/packs-export
title: "Asset packs, export and patches"
description: "How Strata puts every asset of a game into one checked file that the runtime reads by byte range, and how later packs patch it."
kind: internals
size: L
tracks: [E]
needs: [assets/references]
time: 90
learn:
  - id: layout
    text: explain how an asset pack is laid out and why its tables end the file
  - id: order
    text: predict the order of a pack's entries and which assets pruning keeps
  - id: compression
    text: explain why a block is stored as it is when compression saves less than an eighth
  - id: reading
    text: trace which blocks a range read covers and what happens to each
  - id: patching
    text: write down what a patch pack holds and how the runtime mounts it
since: 0.3.0
status: final
---

A game on a player's disk must not depend on the folders of the person who made it. Strata puts every asset the game ships into one file, the **asset pack**, a file with the extension `.stpak`. The :term[runtime]{id=runtime} reads that file by :term[byte]{id=byte} range, so it can fetch one texture without reading the rest. Every part of the file carries a :term[checksum]{id=checksum}, the entries lie in the order a scene needs them, and a second pack can replace entries of the first.

The page teaches the format, the code that plans and writes a pack, the code that reads it, and the way a patch is applied. It does not teach how a pack is checked when it is opened, which [Robustness](robustness.md) covers, or the export as a whole, which [Export](../worlds/export.md) covers.

## The problem and how engines solve it

Your project holds thousands of files: pictures, meshes, sounds, scenes, materials. A game that ships them as they are meets three problems. Thousands of small files are slow to open, slow to copy and slow to check on a disk. Nothing detects a file that is cut short or damaged, so the game loads garbage and fails far from the cause. Nothing tells the game which files a scene needs, so a level that loads reads the disk in a scattered order.

A fourth problem comes after release. You fix one material, and the player should not download 20 GB again. The game needs a way to say "use this version of that asset instead".

Engines answer with an archive. Table 1 compares the approaches; each row names what it costs.

| Approach | What it does | What it costs |
| --- | --- | --- |
| Loose files | Ship the folders as they are. | Many file opens, no integrity check, no order, a patch replaces whole files by hand. |
| A zip archive | One file; each member is compressed on its own; a list of members ends the file. | One compressed stream per member, so a read in the middle of a big member expands everything before it. |
| Unreal `.pak` and `IoStore` | An archive with an index; the newer container format also keeps a separate table of contents. | A format with many features; reading it well needs the engine's own :term[loader]{id=loader}. |
| Unity asset bundles | Bundles of assets in the engine's own format, compressed whole or in chunks. | The game chooses bundles and their dependencies; a mistake duplicates or loses assets. |
| Strata's pack | One file; entries cut into blocks; tables at the end; later packs override. | One format to maintain, and a write that must know the whole game. |

: Table 1. Ways to ship assets.

:::elsewhere
A zip file ends with a list of its members, which is the same trick as Strata's tables at the end. Unreal's `.pak` and `IoStore` containers and Unity's asset bundles are described in the documents listed under Further reading; the table above states only what those documents say.
:::

Strata keeps the zip idea of one file with a list at the end, and changes the unit of compression. A zip member is one stream. A Strata entry is cut into pieces of 256 KiB, called blocks, and each block stands alone. A read of 64 KiB from the middle of a 90 MB entry then decodes one or two blocks, not the first 45 MB.

## The map

Five pieces of code share the job. The editor's :term[asset manager]{id=asset-manager} decides what goes in and in which order.

The writer turns that plan into a file. The reader opens the file and decodes ranges of it. The runtime asset manager mounts one or more readers and answers the loads of a running game. The game's manifest names the patch packs to mount.

```mermaid caption="Who plans, writes, reads and mounts a pack. The editor side runs only while you export; the game links only the reader and the runtime side." alt="Two columns. On the editor side, the asset manager plans, the cook step rewrites scenes, and the writer writes a pack file. On the game side, the manifest names the packs, the runtime asset manager mounts them, and the reader decodes blocks from the files."
flowchart LR
    subgraph Editor["Editor, at export"]
        Plan["EditorAssetManager::PlanAssetPack"] --> Write["EditorAssetManager::WriteAssetPack"]
        Write --> Cook["AssetPackCook: CookForPack"]
        Write --> Writer["AssetPackWriter::Write"]
    end
    Writer --> File[("Game.stpak")]
    Patch[("Patch.stpak, written from code")]
    subgraph Game["Game, at run time"]
        Manifest["GameManifest: PatchPacks"] --> Runtime["RuntimeAssetManager::Mount"]
        Runtime --> Reader["AssetPack: reader"]
    end
    File --> Reader
    Patch --> Reader
```

The files live in `Strata/src/Strata/Asset/`: `AssetPack.h` and `AssetPack.cpp` (format and reader), `AssetPackWriter.h` and `AssetPackWriter.cpp` (writer), `AssetPackCook.h` and `AssetPackCook.cpp` (cooking), `EditorAssetManager.cpp` (plan and write) and `RuntimeAssetManager.cpp` (mounts). The writer links the zstd code that compresses; a shipped game links only the code that expands blocks, so the game stays small.

Threads matter here. Planning runs on the :term[main thread]{id=main-thread}, because it reads the editor's registry. The write runs on an input and output (I/O) thread, and its compression work runs on the job system's background workers, so the editor's frames stay smooth. At run time, a read runs on whatever thread asks for the data, usually a loading job, and helper jobs decode blocks in parallel.

## The contract

A pack makes promises to the code that reads it, and demands things of the code that writes it. Each rule has a reason.

- **Entries are ordered by first use.** The first scene's assets come first, then the next scene's. A level that loads then reads the file from front to back, which disks and caches like.
- **Every entry is a run of consecutive blocks of 256 KiB**, and starts on a 4 KiB boundary. The format fixes both sizes, so a range read finds its blocks with one division.
- **A block is compressed with zstd, or stored as it is when compression saves less than an eighth.** A stored block costs a read and a check; a compressed block also costs a buffer and a decode step. The next section shows the numbers.
- **Checksums guard every part.** A checksum is a number computed from bytes, and the same bytes always give the same number. The :term[header]{id=header}, the tables and each block carry a :term[CRC-32C]{id=crc-32c}. A reader checks a block's checksum before it decodes the block, so a damaged byte becomes an error, never a wrong texture.
- **The tables end the file.** The writer does not know the size of the data before it writes it, so it writes the data, then the tables, then returns to the start and writes the header. One pass, no second file.
- **The plan is a snapshot, and the write checks it.** The editor keeps working while an export writes. If a document now references something the plan omitted, the write fails and names the document.
- **Later packs replace earlier entries by handle**, and the assets that were loaded reload from the new entry. Built-in handles are never replaced, because the engine itself provides those assets.

Words you need before the rest. An **asset pack** is the one file of a game that holds every asset in its :term[stored form]{id=stored-form}, read by byte range. A **block** of a pack is a piece of up to 256 KiB of an entry's stored form that is compressed and checked on its own.

## A toy pack

The toy below keeps four ideas of the real format and drops the rest: a header, the entries' bytes, one table at the end, and one checksum. It also mounts a second pack over the first. It keeps the pack in memory, so the code stays short and the file input and output do not hide the format.

:::question
The sketch uses loops, :term[structs]{id=struct}, functions, pointers, a map and a few library calls. Review them in [Programming 1](../basics/programming-1.md), [Programming 2](../basics/programming-2.md) and [Programming 3](../basics/programming-3.md), then [memory](../basics/cpp-memory.md), [generic code](../basics/cpp-generic.md) and [modern C++](../basics/cpp-modern.md).
:::

The program writes a game pack and a patch pack, mounts them in order, and then flips one byte of the table. Search for three things as you read. The header is written first as a blank space and completed last. The table sits after the data. The reader refuses the file when the table's checksum does not match.

```cpp sketch="assets-packs-export-toy.cpp"
// A toy asset pack: a header, the entries' bytes, one table at the end guarded by one checksum, and mounts.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <utility>
#include <vector>

namespace
{
	using Bytes = std::vector<uint8_t>;
	using Source = std::pair<std::string, std::string>;

	constexpr uint32_t c_Magic = 0x4B505453;

	struct Header
	{
		uint32_t Magic = 0;
		uint32_t EntryCount = 0;
		uint64_t TablesOffset = 0;
		uint32_t TablesChecksum = 0;
		uint32_t Reserved = 0;
	};

	struct Record
	{
		uint64_t Offset = 0;
		uint64_t Size = 0;
		char Name[24] = {};
	};

	uint32_t Crc32c(const uint8_t* data, size_t size)
	{
		uint32_t crc = 0xFFFFFFFFu;
		for (size_t index = 0; index < size; index++)
		{
			crc ^= data[index];
			for (int bit = 0; bit < 8; bit++)
				crc = (crc >> 1) ^ (0x82F63B78u & (0u - (crc & 1u)));
		}
		return ~crc;
	}

	Bytes WritePack(const std::vector<Source>& sources)
	{
		Bytes file(sizeof(Header));
		std::vector<Record> records;
		for (const Source& source : sources)
		{
			Record record;
			record.Offset = file.size();
			record.Size = source.second.size();
			std::memcpy(record.Name, source.first.data(), std::min(source.first.size(), sizeof(record.Name) - 1));
			file.insert(file.end(), source.second.begin(), source.second.end());
			records.push_back(record);
		}
		const uint8_t* tables = reinterpret_cast<const uint8_t*>(records.data());
		const size_t tableBytes = records.size() * sizeof(Record);
		Header header;
		header.Magic = c_Magic;
		header.EntryCount = static_cast<uint32_t>(records.size());
		header.TablesOffset = file.size();
		header.TablesChecksum = Crc32c(tables, tableBytes);
		file.insert(file.end(), tables, tables + tableBytes);
		std::memcpy(file.data(), &header, sizeof(header));
		return file;
	}

	bool ReadTables(const Bytes& file, std::vector<Record>& outRecords)
	{
		Header header;
		if (file.size() < sizeof(Header))
			return false;
		std::memcpy(&header, file.data(), sizeof(header));
		const size_t tableBytes = header.EntryCount * sizeof(Record);
		if (header.Magic != c_Magic || header.TablesOffset + tableBytes != file.size())
			return false;
		if (Crc32c(file.data() + header.TablesOffset, tableBytes) != header.TablesChecksum)
			return false;
		outRecords.resize(header.EntryCount);
		std::memcpy(outRecords.data(), file.data() + header.TablesOffset, tableBytes);
		return true;
	}
}

int main()
{
	const Bytes game = WritePack({ { "Level.scene", "ground,tree,hero" }, { "Hero.mat", "red" }, { "Tree.mat", "green" } });
	const Bytes patch = WritePack({ { "Hero.mat", "blue" } });
	std::printf("game pack: %zu bytes, patch pack: %zu bytes\n", game.size(), patch.size());

	std::map<std::string, std::string> mounted;
	for (const Bytes* pack : { &game, &patch })
	{
		std::vector<Record> records;
		if (!ReadTables(*pack, records))
			return 1;
		for (const Record& record : records)
			mounted[record.Name] = std::string(pack->begin() + record.Offset, pack->begin() + record.Offset + record.Size);
	}
	for (const auto& [name, content] : mounted)
		std::printf("%s = %s\n", name.c_str(), content.c_str());

	Bytes damaged = game;
	damaged[damaged.size() - 5] ^= 0x01;
	std::vector<Record> records;
	std::printf("damaged table accepted: %s\n", ReadTables(damaged, records) ? "yes" : "no");
	return 0;
}
```

```text output-of="assets-packs-export-toy.cpp"
game pack: 168 bytes, patch pack: 68 bytes
Hero.mat = blue
Level.scene = ground,tree,hero
Tree.mat = green
damaged table accepted: no
```

1. **Lines 18–25:** the header holds the counts, where the table starts and one checksum of the table.
2. **Lines 34–44:** `Crc32c` computes the CRC-32C bit by bit; the constant is the number that defines CRC-32C.
3. **Lines 46–69:** `WritePack` leaves room for the header, appends each entry, then the table, and returns to write the header last.
4. **Lines 71–85:** `ReadTables` refuses a wrong :term[magic number]{id=magic-number}, a table that does not end the file and a checksum that does not match.
5. **Line 101:** a later pack replaces the earlier entry of the same name, which is how a patch works.

The patch's `Hero.mat` replaced the game's, while `Level.scene` and `Tree.mat` stayed. The flipped byte made the reader refuse the pack.

The real format differs in four ways. It cuts each entry into blocks and compresses them. It aligns entries to 4 KiB. It adds a header checksum and a checksum per block, not one for the tables alone. It reads from a file by range, never from memory in one piece.

## The real code

The sections below follow the data: the format, the plan, the write with its checks, the read, and the mount.

### The format

The file begins with a 64-byte header. Its comment in `AssetPack.h` is the format's specification:

```cpp src="Strata/src/Strata/Asset/AssetPack.h#L69-L88"
// Version 2 layout (little endian):
//   header (64 bytes): "STPK", version, flags (none defined; packs with unknown flags are refused), header size, block
//     size, the counts of entries, strings, blocks and dependencies, the size of the string bytes, where the tables
//     start, a CRC-32C of the tables and one of the header
//   entry data: every entry starts at a 4 KiB boundary and is a run of consecutive blocks: its stored form cut into
//     pieces of BlockSize (256 KiB; the last one shorter), each compressed with zstd, or stored as it is when compression
//     saves less than an eighth (c_MinCompressionSaving). Entries are ordered by first use (see
//     EditorAssetManager::BuildAssetPack), so loading a scene reads the file front to back.
//   tables (they end the file, so a pack is written in one pass, and are read with one read):
//     entries (88 bytes each): handle, parent, stored size, content hash, type, flags (bit 0: has bounds), the string
//       indices of path, sub-asset key and name, first block and block count, first dependency and dependency count,
//       bounds minimum and maximum
//     strings: per string its offset and size in the string bytes, then the string bytes (shared paths are stored once)
//     blocks (24 bytes each): file offset, stored size, decoded size, CRC-32C of the stored bytes, codec
//     dependencies: asset handles, 8 bytes each; an entry names its range
// Open validates the header and every table completely (sizes, ranges, overlapping blocks, checksums) and reads; reads
// check each block's checksum before decoding it, so corrupt files fail with an error, never a crash. Packs are untrusted
// input whose tables may point at shared targets, so Open also bounds what it builds by the file's size: entries may not
// name more blocks or dependencies than the tables hold (so no entry claims more bytes than its blocks decode to), and
// the strings they name, counted per entry, stay within AssetPackFormat::GetMaxNameBytes; running out of memory fails
```

1. **Lines 69–72:** the header has 64 bytes: a :term[magic number]{id=magic-number}, the version, the sizes and counts, where the tables start and two checksums.
2. **Lines 73–76:** entries start on 4 KiB boundaries and are runs of 256 KiB blocks, each compressed or stored by the rule of an eighth.
3. **Lines 77–83:** the tables end the file, so one pass writes it; they hold entries, strings, blocks and dependencies.
4. **Lines 84–88:** a reader checks every block's checksum before it decodes the block, so a corrupt file fails with an error.

The comment names what each part is for. The structs that the writer and the reader share follow, and their sizes are fixed by assertions that the :term[compiler]{id=compiler} checks.

```cpp src="Strata/src/Strata/Asset/AssetPack.h#L177-L194"
struct Header
{
	uint32_t Magic = 0;
	uint32_t Version = 0;
	uint32_t Flags = 0;
	uint32_t HeaderSize = 0;
	uint32_t BlockSize = 0;
	uint32_t EntryCount = 0;
	uint32_t StringCount = 0;
	uint32_t BlockCount = 0;
	uint32_t DependencyCount = 0;
	uint32_t Reserved = 0;
	uint64_t StringBytes = 0;
	uint64_t TablesOffset = 0;
	uint32_t TablesChecksum = 0; // CRC-32C of everything from TablesOffset to the end of the file
	uint32_t HeaderChecksum = 0; // CRC-32C of the header's bytes before this field
};
static_assert(sizeof(Header) == 64, "The header layout is part of the pack format");
```

1. **Lines 179–188:** the magic number, the version, the flags, the sizes and the counts that describe the tables.
2. **Lines 189–192:** the string bytes, where the tables start, and the two checksums.
3. **Line 194:** the assertion turns a change of the layout into a :term[compile error]{id=compile-error}.

Each `static_assert` makes a change of the layout a :term[compile error]{id=compile-error}, because a pack written by one build must read in another. The tables hold three kinds of record: 88 bytes per entry, 24 bytes per block and 8 bytes per dependency handle. Strings (paths, names) are stored once, in a string table, and shared, because all :term[sub-assets]{id=sub-asset} of a model share the model's path.

Take a pack with four entries of 600,000, 100, 0 and 262,144 bytes, all blocks stored. The header takes bytes 0 to 63. The first entry is not empty, so it starts at the next 4 KiB boundary, byte 4,096. It needs `600000 / 262144 = 2.29`, which rounds up to 3 blocks, so its blocks are 262,144, 262,144 and 75,712 bytes.

The data of the first entry ends at 604,096, and the second entry starts at the next boundary, 606,208. The empty entry takes no blocks and no padding. Exercise 1 asks you to finish the sum.

```mermaid caption="A pack from front to back: the header, entries each starting on a 4 KiB boundary and cut into blocks, then the tables and their checksum at the end." alt="A horizontal strip. The header is at the left, followed by a gap, then the blocks of the first scene's entries, then the blocks of later scenes, and at the right the tables with their checksum."
flowchart LR
    H["Header 64 B"] --> E1["Start scene: block, block, block"]
    E1 --> E2["Next scene and its assets: block, block"]
    E2 --> E3["The rest by path: block"]
    E3 --> T["Tables: entries, strings, blocks, dependencies"]
```

The content :term[hash]{id=hash} of an entry is another part of the tables. `AssetPack::HashContent` takes an :term[FNV-1a]{id=fnv-1a} hash of each 256 KiB piece, combines the hashes in order, and combines the result with the size. The writer computes it from the decoded bytes while it writes, so it needs no second pass. The hash lets tools tell whether an asset changed without reading the whole pack.

### Why block-compressed textures are stored

The threshold for compression is `c_MinCompressionSaving = 8`: a block is compressed only when the result is at least an eighth smaller. The writer gives zstd an output buffer of `size - size / 8 - 1` bytes. For a full block of 262,144 bytes that is 229,375 bytes. If the compressed data does not fit, zstd reports failure, and the writer stores the block as it is.

The numbers explain the choice. Texture data in the block compression 7 (BC7) format is already compact, and zstd saved about 7 % of it. Seven percent of 262,144 bytes is about 18,350 bytes, which is less than the 32,768 needed. Such a block is stored. A compressed block must be read into a buffer and then expanded.

A stored block is read straight into the place where the data goes, checked there and never copied. The header's comment reports a measurement. With a twentieth as the threshold, most BC7 blocks of the stress world were compressed, and the world streamed about 10 % slower than from the older format. With an eighth, the pack was about as fast.

:::rule[Do not compress what does not compress]
A compression step that saves little costs more than it saves: a buffer, a copy and processor time at every read. Strata stores a block unless compression saves at least an eighth. The reason is in the comment quoted above, and the test `Blocks that compress by less than an eighth are stored, and stored blocks are read straight into the destination` pins it.
:::

:term[JSON]{id=json}, scene documents and :term[shader]{id=shader} code compress well, often to a third or less, so those blocks are compressed. Exercise 2 asks you to measure the difference yourself.

### Planning: which assets, in which order

`EditorAssetManager::PlanAssetPack` decides what the pack holds. It takes the project's assets, without the built-in ones, and builds an order in which each asset appears where it is first needed.

```cpp src="Strata/src/Strata/Asset/EditorAssetManager.cpp#L4211-L4265" from="// First use: each root's dependency closure" to="plan.Assets.reserve(order.size());" symbol="EditorAssetManager::PlanAssetPack"
// First use: each root's dependency closure, breadth first, appended where it is first reached.
std::vector<size_t> order;
std::vector<bool> included(all.size(), false);
auto addClosure = [&](AssetHandle root)
{
	for (AssetHandle member : GetDependencyClosure(root))
	{
		auto it = indices.find(member);
		if (it != indices.end() && !included[it->second])
		{
			included[it->second] = true;
			order.push_back(it->second);
		}
	}
};
if (options.StartScene.IsValid())
	addClosure(options.StartScene);
for (const AssetMetadata& metadata : all)
{
	if (metadata.Type == AssetType::Scene && !metadata.IsSubAsset())
		addClosure(metadata.Handle);
}

// What AlwaysInclude names: assets by path (with their sub-assets) and folders.
for (const std::string& entry : options.AlwaysInclude)
{
	const std::string path = NormalizeIncludePath(entry);
	bool matched = false;
	for (const AssetMetadata& metadata : all)
	{
		if (IsIncludedByPath(path, metadata))
		{
			matched = true;
			addClosure(metadata.Handle);
		}
	}
	if (!matched && options.Prune)
	{
		if (outError)
			*outError = DescribeUnmatchedInclude(entry);
		return false;
	}
}

AssetPackBuildPlan plan;
for (size_t index = 0; index < all.size(); index++)
{
	if (included[index])
		continue;
	if (options.Prune)
		plan.Excluded.push_back(all[index]);
	else
		order.push_back(index);
}
plan.Assets.reserve(order.size());
```

1. **Lines 4214–4225:** `addClosure` takes the `All` scope, the default of `GetDependencyClosure`. It walks the closure of a root breadth first and appends each member not yet in the order; the flags in `included` stop an asset from appearing twice.
2. **Lines 4226–4227:** the start scene goes first, so its level reads the front of the file.
3. **Lines 4228–4232:** every other scene follows with its closure.
4. **Lines 4234–4254:** each `AlwaysInclude` entry is matched against asset paths, and a match adds its closure; with pruning, no match fails.
5. **Lines 4255–4265:** what no scene reached is appended to the order, or put in `plan.Excluded` when pruning.

The code is the idea of **first-use order**: the order in which a game first needs its assets, where each one is placed at the first point that reaches it. The plan builds it from closures, the sets that [References](references.md) teaches.

**Pruning** is omitting from the pack the assets that no scene uses and `AlwaysInclude` does not name. It is off by default, because a script can load an asset by a path text, and no scan of the scenes can see that.

:::example[Which assets the plan keeps]
A project has three scenes and four materials. `Level1` uses `A`, `Level2` uses `B` and `A`, and `Menu` uses `B`. `Unused` is used by nothing. A prefab `Enemy` uses the material `ForScripts`, and no scene uses the prefab. A script spawns the enemy with `Assets::Find("Prefabs/Enemy.stprefab")`.

With `Level2` as the start scene and no pruning, the order is `Level2`, `B`, `A`, `Level1`, `Menu`, then the rest by path: `ForScripts`, `Unused`, `Enemy`. Eight entries. The start scene's closure comes first (`Level2`, then its dependencies `B` and `A` in the order the scene records them), and the other scenes follow by path.

With pruning and an empty `AlwaysInclude`, the pack holds the first five entries and omits three. The script's enemy would not exist in the game. With `AlwaysInclude` set to `Prefabs/`, the folder entry matches the prefab, the plan adds the prefab's closure, `ForScripts` joins, and only `Unused` stays out.
:::

An entry of `AlwaysInclude` is a path relative to the asset folder. The plan accepts backslashes, a leading `./` and a trailing slash, and it names a file or a folder: `Pref` does not match the folder `Prefabs`, because whole names must match. With pruning, an entry that matches nothing fails the plan with `Export.AlwaysInclude names 'X', which is no asset or folder of the project`, so a spelling mistake does not silently drop an asset.

The export adds two kinds of entries to the project's list before it plans. It adds the path of the loading scene, which the game shows while the start scene loads and which [Export](../worlds/export.md) explains. It adds the path of every asset that the project's settings sections name (a settings section can hold an asset such as a default sky), except :term[built-in assets]{id=built-in-asset}, which every game has. If the settings name an asset that is not in the project, the export stops and tells you to set them again. With pruning, it then checks the whole list up front, without planning, so a mistake fails at once.

:::note
`AlwaysInclude` is a setting of the project, edited through the command `project.setExportSettings` or the Export page of the project settings. The export's `prune` option turns pruning on for one export; the result lists `excludedAssets`, what the pack omitted.
:::

### Writing: checks and cooked documents

`EditorAssetManager::WriteAssetPack` receives the plan and writes it, possibly on another thread. Its comment explains the danger: the plan is a snapshot, and the files are not. While the export writes, the editor may save a scene that now uses a new material. A pack that held that scene but not the material would load with a missing asset.

The write therefore reads each document again, collects its references in the same read and compares them with what the plan recorded.

```cpp src="Strata/src/Strata/Asset/EditorAssetManager.cpp#L4322-L4344" from="const auto source = planned.find(metadata.Handle);" to="}, options, outStats, outError);" symbol="EditorAssetManager::WriteAssetPack"
	const auto source = planned.find(metadata.Handle);
	const bool entityDocument = metadata.Type == AssetType::Scene || metadata.Type == AssetType::Prefab || metadata.Type == AssetType::Model;
	const bool rewrite = entityDocument && (cook.Cook || (metadata.Type == AssetType::Scene && cook.AdjustSceneSettings));
	if (!rewrite && (!AssetDependencies::CanReference(metadata.Type) || source == planned.end()))
		return true;

	std::vector<AssetHandle> references;
	std::string scanError;
	const bool read = rewrite ? CookForPack(metadata, outData, cook, references, &scanError) : AssetDependencies::Scan(metadata.Type, outData, references, &scanError);
	if (!read)
		return fail(fmt::format("it cannot be read as a document ({}); fix it and export again", scanError));
	if (source == planned.end())
		return true;
	// Compared as recorded references are made: a document that names itself (a scene whose script loads it again)
	// depends on nothing for that.
	const std::unordered_set<AssetHandle> recorded(source->second->Dependencies.begin(), source->second->Dependencies.end());
	for (AssetHandle reference : NormalizeReferences(metadata.Handle, references))
	{
		if (!recorded.contains(reference))
			return fail(fmt::format("it changed after the export started and now references {}, which the export did not plan for; export again", describe(reference)));
	}
	return true;
}, options, outStats, outError);
```

1. **Line 4322:** the lookup finds what the plan recorded for the asset being written.
2. **Lines 4323–4326:** documents of entities are rewritten when cooking is on; types that cannot reference anything pass unchanged.
3. **Lines 4327–4332:** `CookForPack` rewrites the document and returns its references from the same read; a document that cannot be read fails the export.
4. **Lines 4337–4342:** a reference the plan did not record fails the write with a message that names it.

The scan and the cook share one read of the document. That keeps the check cheap and makes sure the references checked are the references written.

**Cooking** a scene, a prefab or a model means writing it as the binary form `CookedScene` that a load reads without parsing text. `CookForPack` in `AssetPackCook.cpp` reads the document as a stream, builds the entities, writes them with `CookedSceneWriter`, and keeps the scene's settings in a form the loader accepts. Writing a scene as bytes is :term[serialization]{id=serialization}, and the cooked format itself belongs to [the scene format page](../world/serialization.md). A document that is already cooked is refused, because a project's documents never are.

The exporter can turn cooking off, which keeps the JSON. It can also pass a function that changes each scene's settings between the read and the write, which the export uses to store the capacity a world needs.

### The writer: one pass

`AssetPackWriter::Write` makes the file. It first refuses what cannot work: a null handle, a handle used twice, an unknown type, a version other than 1 and 2, or a compression level that zstd does not have. It then writes `Game.stpak.<random id>.tmp` next to the final path, and renames it into place only when all went well. A failure or a cancel removes the temporary file, so an old pack is never replaced by half a new one; the random name lets two builds write the same pack at once.

For each entry the writer asks the provider for its bytes, pads the file to the next 4 KiB boundary when the entry is not empty, and cuts the bytes into blocks. It handles up to 64 blocks, 16 MiB, at a time: `EncodeBlocks` compresses them in parallel on the background workers, then the writer appends them in order. The batch bounds the memory of a write, and it lets the progress bar move inside a large asset. The tables go last, then the header is written at the start with the counts, the offsets and the two checksums.

The default compression level is 9. A higher level writes a smaller pack more slowly, and reading costs the same, because the work of expanding a block does not depend on the level.

### Reading: the block decode

A read asks for a range of an entry: an offset and a size. `AssetPack::ReadRange` first checks that the range lies inside the entry, then finds the covered blocks by dividing the offsets by the block size. The diagram below shows the path.

```mermaid caption="A range read: find the blocks, group them into chunks, read the chunks ahead, and decode in parallel while the reading continues." alt="A flow from the range of the read through the covered blocks and chunks of up to 2 MiB to three buffers read ahead. Stored blocks are read straight into the destination. Other blocks are decoded by helper jobs. Each block is checked first."
flowchart TD
    R["Range: offset and size"] --> B["Covered blocks"]
    B --> C["Chunks of up to 2 MiB of stored bytes"]
    C --> D{"Stored and wholly inside the range?"}
    D -- yes --> P["Read straight into the destination"]
    D -- no --> Q["Read into a lent buffer, up to three ahead"]
    P --> K["Check the CRC, then done"]
    Q --> K2["Check the CRC, then decompress"]
    K2 --> J["Helper jobs decode while the reader reads on"]
```

Consecutive blocks merge into chunks of up to 2 MiB of stored bytes, which gives few system calls for many blocks. The size was chosen by measurement: 8 MiB chunks streamed the stress world 10 % slower, because the data had left the processor's cache by the time it was decoded. The reader reads up to three chunks ahead into buffers the pack lends and keeps for later reads.

Helper jobs decode while the reading thread reads on. The reading thread never runs unrelated jobs while it waits: a texture decode that it chose could stall the reads behind it. It decodes blocks of its own read, or sleeps until its helpers finish.

Each block ends in `DecodeBlock`. The first lines check the checksum, and only then does anything decode.

```cpp src="Strata/src/Strata/Asset/AssetPack.cpp#L684-L737" from="const AssetPackBlock& current" to="m_BytesDecompressed.fetch_add(current.Size, std::memory_order_relaxed);" symbol="AssetPack::DecodeBlock"
const AssetPackBlock& current = m_Blocks[entry.FirstBlock + block];
if (Hash::CRC32C(stored) != current.Checksum)
{
	outError = fmt::format("block {} is corrupt (checksum mismatch)", entry.FirstBlock + block);
	return false;
}

// The part of the block the range covers: decoded in place when it is the whole block, else through a block of its
// own (only the first and the last block of a range can be partial; stored blocks are copied from directly).
const uint64_t blockStart = static_cast<uint64_t>(block) * m_BlockSize;
const uint64_t copyStart = std::max(blockStart, offset);
const uint64_t copyEnd = std::min(blockStart + current.Size, end);
const bool whole = copyStart == blockStart && copyEnd == blockStart + current.Size;
std::vector<uint8_t> partial;
const uint8_t* decoded = nullptr;
if (current.Codec == AssetPackCodec::Stored)
{
	// A block ReadBlocks read straight into the destination is there already.
	decoded = stored.data();
	if (whole && stored.data() == destination + (blockStart - offset))
		m_BlocksReadInPlace.fetch_add(1, std::memory_order_relaxed);
	else if (whole)
		std::memcpy(destination + (blockStart - offset), stored.data(), current.Size);
}
else
{
	uint8_t* output = destination + (blockStart - offset);
	if (!whole)
	{
		try
		{
			partial.resize(current.Size);
		}
		catch (const std::bad_alloc&)
		{
			outError = "out of memory";
			return false;
		}
		output = partial.data();
	}
	decoded = output;
	if (!t_Decompression.Context)
	{
		outError = "out of memory (decompression context)";
		return false;
	}
	const size_t result = ZSTD_decompressDCtx(t_Decompression.Context, output, current.Size, stored.data(), stored.size());
	if (ZSTD_isError(result) || result != current.Size)
	{
		outError = fmt::format("block {} is corrupt ({})", entry.FirstBlock + block, ZSTD_isError(result) ? ZSTD_getErrorName(result) : "wrong decompressed size");
		return false;
	}
	m_BlocksDecompressed.fetch_add(1, std::memory_order_relaxed);
	m_BytesDecompressed.fetch_add(current.Size, std::memory_order_relaxed);
```

1. **Lines 684–688:** the checksum of the stored bytes is compared first, so a damaged block fails before anything decodes it.
2. **Line 696:** `whole` tells whether the range covers the entire block; only the first and last block of a range can be partial.
3. **Lines 699–707:** a stored block is already in place when the read put it straight into the destination, and the read counters count it as read in place.
4. **Lines 708–737:** a compressed block expands into the destination, or into a block of its own when partial, and must have exactly the size the table promises.

:::example[A range read, by hand]
The first entry of the layout above is 600,000 bytes: blocks 0 to 2. A read of 64 KiB at offset 300,000 ends at byte 365,536. Block 1 covers bytes 262,144 to 524,287, so the read needs that block only. It is partial, so the reader reads the whole block into a buffer, checks it and copies the 65,536 bytes needed; a compressed block would first expand into a block of its own.

A read of 30,000 bytes at offset 250,000 ends at 280,000 and crosses the boundary at 262,144. It needs blocks 0 and 1, both partial: the reader reads and checks two blocks of 262,144 bytes to deliver 30,000. A read of the whole entry covers all three blocks, and each whole stored block is read in place. The test `A 64 KiB range of a 90 MB entry decompresses at most two blocks` checks the same property on a large entry.
:::

Version 1 packs still read. Their header has 32 bytes, their data is stored raw and their entry table is read whole, with no blocks and no checksums. `ReadRange` on such a pack reads the file at the entry's offset. The writer can still write version 1 for old runtimes, and the test `A version 1 pack written by the retained writer reads like version 2` compares the two.

### Mounting and patch packs

A game opens its pack with `RuntimeAssetManager::Create`, and then calls `Mount` for each patch pack the manifest lists. `Mount` opens the pack and calls `AddPack`.

```cpp src="Strata/src/Strata/Asset/RuntimeAssetManager.cpp#L71-L86" from="std::unique_lock<std::shared_mutex> lock(m_PacksMutex);" to="registered.emplace_back(index, metadata);" symbol="RuntimeAssetManager::AddPack"
std::unique_lock<std::shared_mutex> lock(m_PacksMutex);
m_Packs.push_back(std::move(pack));
const std::vector<AssetPackEntry>& entries = added->GetEntries();
for (size_t index = 0; index < entries.size(); index++)
{
	const AssetMetadata& metadata = entries[index].Metadata;
	// Built-in assets always come from the engine itself; a pack cannot replace them.
	if (BuiltinAssets::IsBuiltin(metadata.Handle))
	{
		ST_CORE_WARN("Asset pack entry '{}' uses a built-in asset handle; ignored", metadata.Path);
		continue;
	}
	auto [it, inserted] = m_PackEntries.insert_or_assign(metadata.Handle, EntryLocation { added, index });
	if (!inserted)
		replaced.push_back(metadata.Handle);
	registered.emplace_back(index, metadata);
```

1. **Line 71:** the pack list changes under a lock, because loads on other threads read it.
2. **Lines 77–82:** a built-in handle is skipped with a warning.
3. **Lines 83–86:** `insert_or_assign` makes the new entry win, a handle that existed already is recorded as replaced, and the entry is queued for registration.

A **patch pack** is a pack that a game mounts after its own, whose entries replace the entries with the same handles. After the lock the manager registers each entry and takes its dependencies and bounds from the pack's tables, without opening any document. Then `Mount` calls `ReloadAsset` for every replaced handle: an asset that was loaded or loading reads its new entry, and a load of the old entry is discarded. The old object serves until the new one arrives.

The game's startup mounts the patches in the order the manifest lists them, before anything loads.

```cpp src="Strata/src/Strata/Runtime/GameRuntime.cpp#L73-L84"
// Patches replace the game's assets before anything loads; one that is missing or broken stops the game, which
// would otherwise run with assets the patch was meant to replace.
for (const std::string& patch : runtime->m_Manifest.PatchPacks)
{
	std::string error;
	if (!runtime->m_AssetManager->Mount(manifestPath.parent_path() / FileSystem::FromUTF8(patch), &error))
	{
		if (outError)
			*outError = fmt::format("Mounting the patch pack '{}' failed: {}", patch, error);
		return nullptr;
	}
}
```

1. **Lines 73–74:** patches replace assets before anything loads, and a missing one stops the game.
2. **Line 75:** the packs mount in the order the manifest lists them.
3. **Lines 78–83:** a failed mount returns no runtime and an error that names the pack.

A missing or broken patch pack stops the game with the message `Mounting the patch pack` followed by its name, because a game that ran without the fix would be worse than one that did not start. The manifest accepts at most 256 names, and each must be a file next to the manifest.

:::caution
No tool writes patch packs. The export writes none and lists none in the manifest's `PatchPacks`, so a patch is a pack that you write from code with `AssetPackWriter::Write`, and name in the manifest by hand. The test `Mounted packs replace the entries of earlier packs and reload what they replace` shows the code, and `Games mount the patch packs their manifest lists over their pack` shows a game that uses it.
:::

A patch entry has the handle of the asset it replaces, and its own type, path and dependencies. A patch that changes a material to name another texture should include that texture, or the game must have it already, because the replaced entry's dependencies come from the patch.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One compressed stream per file (zip) | Zip archives | A format that every tool opens | Range reads inside a big entry; decoding in parallel |
| Whole-pack compression | Installers | Smaller files | Random access: every read would start from a stream's beginning |
| Compress everything, ignoring the gain | Simple archive tools | A simpler writer | Faster loads of textures that do not shrink; direct reads in place |
| Chunked containers with a separate table file | Unreal's `IoStore` | A table of contents kept apart from the data | One file per game that is simple to copy and to patch |
| Bundles that the game builds and loads by name | Unity asset bundles | Small downloads of parts of a game | Handle-based loading: the game never chooses what to load from where |
| Binary patch files (differences of bytes) | Programs that update games | Very small downloads | Simple mounting; a patch pack needs no tool to apply |

## How it is tested

The suite `Asset.Pack` in `StrataTests/src/Asset/AssetPackTests.cpp` is the format's home. Its tests write packs of 200 entries of 0 to 3 MB, some that shrink well and some that do not, and check that they read back byte for byte. They check that a range decodes only the blocks that cover it. They check that blocks which compress by less than an eighth are stored and read in place. Eight threads that read random ranges must get their own bytes.

The tests also check progress and cancel, version 1, and truncated or corrupt packs that must fail with an error, never a crash. The suite `Asset.Pack.Sweep` truncates a pack at every length and changes single bytes.

Planning has its tests in `AssetDependencyTests.cpp`: the test `Packs are ordered by first use, and pruning keeps what scenes and AlwaysInclude use` is the example above, and `Mounted packs replace the entries of earlier packs and reload what they replace` covers mounts. `GameManifestTests.cpp` covers the manifest's patch list. `EditorExportTests.cpp` covers the export: a pruned export keeps what the scenes use and what the `AlwaysInclude` list names, and keeps an asset that a settings section names. `EditorAssetManagerTests.cpp` checks that exported packs hold :term[cooked scenes]{id=cooked-scene} that load equal to their JSON.

Run them with a doctest filter, `StrataTests --test-suite=Asset.Pack*`, or with `ctest --preset windows-debug -R Asset`. The perf tests that stream the stress world from a pack check that it streams at most 10 % slower than from the older format. The tests need a :term[graphics processing unit]{id=gpu} (GPU) and run only in Release and :term[Dist]{id=dist} builds.

## Changing it safely

The extension points are few. A new :term[asset type]{id=asset-type} needs no change here: the writer takes any known type, and the stored form is bytes. A new document type that references assets records its references, so the plan includes them. A change of the format has more rules.

:::rule[A pack format change extends the corruption tests]
A pack is read from a file the player may have damaged, so a reader that accepts a new field must refuse every broken form of it. Strata's rule says that a change of the pack format extends the corruption tests of `AssetPackTests.cpp`, and a change of the cooked scene format extends those of `CookedSceneTests.cpp`.
:::

- Keep the structs' sizes: the `static_assert` lines exist so that an edit fails to compile, not to load.
- Raise the version when old readers must refuse the new file, and keep reading the old versions, as version 1 shows.
- Keep the check before the decode in `DecodeBlock`, and keep every error a returned value, never an assertion: packs are input that cannot be trusted.
- A new input of the plan that changes what a game holds goes into the consistency check, or the write may ship a pack that disagrees with its plan.
- Mounting never touches built-in handles, and a replaced asset always reloads.

## Summary

- A pack is one file: a header, entries cut into 256 KiB blocks from 4 KiB boundaries, and tables that end the file, so one pass writes it.
- Entries follow first-use order; pruning keeps the scenes' closures and what `AlwaysInclude` names, which the export extends with the loading scene and the settings' assets.
- A block is compressed with zstd only when that saves an eighth; the rest are stored and read in place.
- A range read decodes only the covered blocks, checks each checksum first, and uses chunks, buffers and helper jobs.
- A patch pack replaces entries by handle when mounted; no tool writes one, so you write it from code and list it in the manifest.

## Check yourself

1. A block of 262,144 bytes would compress to 240,000 bytes. What does the writer do, and why?

   :::answer{tests="compression"}
   The writer stores the block as it is. The limit is `262144 - 32768 - 1 = 229375` bytes, and 240,000 is above it, so compression saves less than an eighth. A stored block costs a read and a check, while a compressed one costs a buffer and a decode step as well.
   :::

2. A project has scenes `Menu` and `Level1`, and `Level1` is the start scene. A material `Gold` is used by both scenes. Where does it appear in the pack?

   :::answer{tests="order"}
   After `Level1` and before `Menu`, in the closure of the start scene. The plan adds each asset where it is first reached, and `Level1` goes first, so `Gold` lies with the first level. `Menu` then adds only what is new.
   :::

3. Which statement about the tables is right? (a) They come first so a reader finds them fast. (b) They end the file so the writer needs one pass. (c) They are compressed with zstd. (d) They need no checksum.

   :::answer{tests="layout"}
   Statement (b). The writer learns the offsets and the sizes only after it writes the data, so the tables follow it, and the header at the start is completed last. Statement (a) is wrong: the reader finds them from the header. Statement (c) is wrong: the tables are read with one read as they are. Statement (d) is wrong: the header holds the CRC-32C of the tables.
   :::

4. A read of 100 bytes at offset 262,100 of an entry of three blocks. Which blocks does it decode, and are they whole?

   :::answer{tests="reading"}
   The read ends at byte 262,200 and crosses the boundary at 262,144, so it needs blocks 0 and 1. Both are partial, because the read covers 44 bytes of block 0 and 56 bytes of block 1. Each block's checksum is checked first.
   :::

5. A pack mounted over the game's pack holds an entry whose handle is a built-in handle. What happens?

:::answer{tests="patching"}
The entry is ignored with a warning, and the engine's own asset stays. The mount loop skips built-in handles, so a pack cannot replace what the engine provides.
:::

## Exercises

1. **Basic.** For the entries of 600,000, 100, 0 and 262,144 bytes, find where each starts, how many blocks it has and how large the tables are when all blocks are stored. Check your result with a program.

   :::answer[Worked solution]{tests="layout" solution="sketches/assets-packs-export-layout.cpp"}
   The sketch repeats the writer's rule: pad to 4,096 when the entry is not empty, count blocks by rounding up, then add the size.

   ```cpp sketch="assets-packs-export-layout.cpp"
   // Lays out entries of a pack the way the writer does, assuming every block is stored as it is.
   #include <cstdint>
   #include <cstdio>
   #include <vector>

   int main()
   {
   	constexpr uint64_t c_BlockSize = 256 * 1024;
   	constexpr uint64_t c_EntryAlignment = 4096;
   	const std::vector<uint64_t> sizes = { 600000, 100, 0, 262144 };

   	uint64_t position = 64; // The header
   	uint64_t blockTotal = 0;
   	for (size_t index = 0; index < sizes.size(); index++)
   	{
   		const uint64_t blocks = (sizes[index] + c_BlockSize - 1) / c_BlockSize;
   		if (sizes[index] > 0)
   			position = (position + c_EntryAlignment - 1) / c_EntryAlignment * c_EntryAlignment;
   		std::printf("entry %zu: %llu bytes, %llu blocks, starts at %llu\n", index, static_cast<unsigned long long>(sizes[index]),
   			static_cast<unsigned long long>(blocks), static_cast<unsigned long long>(position));
   		position += sizes[index];
   		blockTotal += blocks;
   	}
   	const uint64_t tables = sizes.size() * 88 + blockTotal * 24;
   	std::printf("data ends at %llu, tables (without strings) take %llu bytes\n", static_cast<unsigned long long>(position),
   		static_cast<unsigned long long>(tables));
   	return 0;
   }
   ```

   ```text output-of="assets-packs-export-layout.cpp"
   entry 0: 600000 bytes, 3 blocks, starts at 4096
   entry 1: 100 bytes, 1 blocks, starts at 606208
   entry 2: 0 bytes, 0 blocks, starts at 606308
   entry 3: 262144 bytes, 1 blocks, starts at 610304
   data ends at 872448, tables (without strings) take 472 bytes
   ```

   1. **Line 16:** the block count rounds up, so a size of one byte needs one block.
   2. **Lines 17–18:** only a non-empty entry is padded to the next 4 KiB boundary.
   3. **Line 24:** the tables take 88 bytes per entry and 24 per block, without the strings and the dependencies.

   The first entry starts at 4,096 and has three blocks. The second pads from 604,096 to 606,208. The empty entry has no blocks and no padding. The last entry has one block, because 262,144 bytes fill exactly one. The tables take 88 bytes per entry and 24 per block, plus strings and dependencies.
   :::

2. **Medium.** Measure how well zstd compresses a BC7 texture and a JSON document, and relate the result to the eighth.

   :::answer[Worked solution]{tests="compression"}
   Export a project and open its pack with a short test or tool that calls `AssetPack::Open` and reads `GetBlocks()`: compare `StoredSize` with `Size` per block, and count blocks whose codec is stored. A BC7 texture block will usually show a saving under an eighth and stay stored, while repetitive text such as JSON shows a much larger saving. The write's statistics hold the same numbers: `CompressedBlocks` against `Blocks`.
   :::

3. **Medium.** Export a project with pruning and find the asset that only `Assets::Find` names. Make the pack keep it with the `AlwaysInclude` list of the export settings.

   :::answer[Worked solution]{tests="order"}
   First export with the command `project.export` and `prune` set to true. The result lists `excludedAssets`, and the asset that a script finds by path is in that list, because no scene references it. Then run `project.setExportSettings` with `alwaysInclude` holding the asset's path (or its folder) and export again. The list no longer holds the asset, and the entries the asset uses came with it. A path that names nothing fails the export with the message the plan gives, which is the test of the spelling.
   :::

4. **Hard.** Write a patch pack from code that replaces one material of an exported game, and list it in the manifest. Then trace which blocks a range read covers: set a breakpoint in `DecodeBlock` while the game loads a scene.

:::answer[Worked solution]{tests="patching reading"}
In a test, build an `AssetPackSource` for the material with the handle of the original. Write the pack with `AssetPackWriter::Write`, and add its file name to the `PatchPacks` array of the manifest next to the game's pack. Start the game: the log line from `AddPack` reports "1 replacing earlier entries".

For the trace, the function is `AssetPack::DecodeBlock` in `AssetPack.cpp`. In a debugger, `block`, `offset` and `end` show the covered blocks, the checksum test runs first, and `current.Codec` tells stored blocks from compressed ones. A search for `PatchPacks` in the editor's sources finds nothing, which confirms that no tool writes patches.
:::

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetPack.h` and `AssetPack.cpp`: the format, `AssetPack`, `DecodeBlock`, `HashContent`.
- `Strata/src/Strata/Asset/AssetPackWriter.h` and `AssetPackWriter.cpp`: `AssetPackWriter::Write`, `EncodeBlocks`.
- `Strata/src/Strata/Asset/AssetPackCook.cpp`: `CookForPack`.
- `Strata/src/Strata/Asset/EditorAssetManager.cpp`: `PlanAssetPack`, `CheckAlwaysInclude`, `WriteAssetPack`, `BuildAssetPack`.
- `Strata/src/Strata/Asset/RuntimeAssetManager.cpp`: `Mount`, `AddPack`.
- `Strata/src/Strata/Project/GameManifest.h` and `Strata/src/Strata/Runtime/GameRuntime.cpp`: `PatchPacks` and their mounting.
- `Strata/src/Strata/Project/Project.h`: `ProjectExportSettings`.
- Tests: the suites `Asset.Pack` and `Asset.Pack.Sweep`; commands `project.export` and `project.setExportSettings`.

## Further reading

- The zip file format specification (PKWARE), for the way a zip file ends with its list of members: advanced.
- The zstd manual and format document (Meta): what the compressor does and how its frames look: intermediate.
- Unreal Engine's documentation of pak files and IoStore: intermediate.
- Unity's manual on asset bundles and their compression: beginner.
