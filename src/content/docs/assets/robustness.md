---
id: assets/robustness
title: "Corruption, crash safety and cancellation"
description: "How Strata survives broken files, a power cut in the middle of an import and a project closed while imports run: checks, bounds, ordering and cancel flags."
kind: concept
size: L
tracks: [E]
needs: [assets/importing, assets/packs-export]
time: 90
learn:
  - id: untrusted-input
    text: explain why a loader treats every file as untrusted and takes sizes from the bytes the file holds, never from a size field
  - id: pack-checks
    text: trace how a pack's checksums and consistency checks reject a changed byte or a wrong block count on open
  - id: write-ahead
    text: explain why cache files are renamed into place before the record that names them, and how the record log survives a torn last line
  - id: cancel-flag
    text: explain how cancel flags let a project close while 17 imports run without waiting for any of them
  - id: limits
    text: name what a checksum protects against and what it does not
since: 0.3.0
status: final
---

Four things go wrong with the files of a project, and each one has happened to a real game.

A player downloads a game pack on a bad connection. The download stops at 93 % and the file on the disk is shorter than it should be. A modeler exports a model whose buffer holds 10,000 :term[bytes]{id=byte}, but whose description says it has a billion vertex entries. A power cut falls in the middle of an import, while the engine writes the result of the work to the cache. Last, a person closes a project while 17 imports still run, and the window hangs for several seconds.

In all four cases the file or the job is not what the code expected. This page shows what Strata does about each case, and why. It does not teach how a pack or an import is built: [packs](packs-export.md) and [importing](importing.md) do. It also omits the machinery of tests that damage files on purpose, which belongs to the engineering part, and the atomic write of one file, which [Core files](../core/files.md) teaches.

## The naive answers break in four ways

The shortest code trusts the file. It reads a count from the file, makes room for that many items and reads them. It writes a record that says "this asset is imported" and then writes the data. When the project closes, it waits for every thread to finish. Each of these choices works until the day it does not.

Take the count first. A file of 12 bytes holds a 4-byte count and 8 bytes of data. If the count says 1,000,000,000 elements of 4 bytes, the naive reader asks the system for 4,000,000,000 bytes, about 4 GB, before it reads anything. The system may refuse and the program may stop, or the system may agree and the program swallows the memory of the machine for a file that is 12 bytes long. A person who wants to hurt your game needs nothing more than a text editor.

Take the order of writes next. The naive :term[importer]{id=importer} writes the record first, then the data, and the power fails between the two. After the power returns, the record says "imported", the cache file does not exist, and the engine trusts the record. The asset is missing for ever, or the engine reads a half file.

Last, take the close. A thread that has started an import of a large model does not know that the person has gone. If the close joins that thread, the close lasts as long as the import does. When the engine had this behavior, closing a project with 17 imports running took between 5.6 and 12 seconds, a hang that a person sees as a crash.

## The idea: check, bound, order, cancel

Each failure has a matching rule. A file is **untrusted input**: bytes that come from outside the running program, which may be cut, damaged by an accident or written to cause harm, so the program checks them before it uses them.

Checking has three parts. A :term[checksum]{id=checksum}, a small number computed from the bytes, tells whether the bytes changed. Consistency checks ask whether the fields agree with each other: the number of blocks must fit the size of the entry. Bounds ask that no size, count or depth is larger than what the file itself can hold. A file of 12 bytes cannot hold 1,000,000,000 elements, so any field that says so is lying.

Writing has its own rule. **Write-ahead ordering** means that a program writes the data first and the note that names the data last, so that a note never points at data that is not there yet. A crash can then leave data that no note names, which is harmless, but never a note that names nothing.

The last rule is for time. A **cancellation flag** is a yes-or-no value that the code that wants a job stopped sets, and that the job reads at the points where stopping is safe. The one who cancels never waits: it sets the flag and continues.

```mermaid caption="Four rules between a source of damage and the engine's state: checks and bounds guard what is read, ordering guards what is written, and a flag stops work nobody wants." alt="A flow from left to right. A file on disk passes checks and bounds before the engine reads it. Results pass an ordering step, data before record, before they reach the disk. A cancel flag stands over the jobs between the two."
flowchart LR
    F["File on disk"] --> C["Checksums, consistency checks, bounds"]
    C --> J["Jobs: decode and import"]
    X["Cancel flag"] -.-> J
    J --> O["Data first, record last"]
    O --> D["Cache on disk"]
```

The rest of the page takes each rule in turn, shows it in Strata's code and counts what it costs. Where the code applies a rule taught elsewhere, such as the publication of cache files, the page names the home and shows only the part that concerns robustness.

## How engines and databases guard their data

Engines have used four families of defense. Each exists because the one before it leaves a hole.

The first defense is nothing but care in the reader: check that a read stays inside the buffer. This stops a crash, but a file with a flipped byte inside a block still reads as a different texture and nobody notices.

The second defense is a checksum per block or per file, stored beside the data. The reader computes the checksum again and compares. A cyclic redundancy check (CRC) is fast, because it costs a few shifts and exclusive-or steps per byte, and it detects every error burst up to its width. A :term[cryptographic hash]{id=cryptographic-hash} such as :term[SHA-256]{id=sha-256} is slower but also resists a person who builds a second file with the same :term[hash]{id=hash}. The :term[CRC-32C]{id=crc-32c} that Strata uses is the first kind: a good detector of accidents, with no defense against an attacker.

The third defense is a validation pass: after the checksums agree, check what the fields claim. A damaged file can carry a correct checksum if the writer had a bug, and a file written by a hostile program always does. Validation catches the counts that do not add up.

The fourth defense concerns writing, not reading. A journal records what is about to change before it changes. An :term[atomic rename]{id=atomic-rename} writes a new file next to the old one and swaps the names in one step. A copy-on-write store never changes a block in place: it writes new blocks and moves one root pointer. Fuzzing and corruption sweeps, which damage files on purpose and check that the reader survives, are the way engines test all of this.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Checked reads only | Almost none | Stops crashes; changed data still reads | Low | Many small :term[loaders]{id=loader} |
| CRC per block | Under 1 ns per byte with the hardware instruction | Detects accidents, not a faked file | Low | PNG, zip, file system tables |
| Cryptographic hash | Several times a CRC | Detects a faked file when the hash itself is trusted | Medium | :term[Git]{id=git}, package managers |
| Validation pass | A walk over the tables | Catches fields that disagree | Medium | Every careful :term[parser]{id=parser} |
| Journal | One extra write of what will change | Any crash leaves a whole state | High | Databases, file systems |
| Atomic rename | One rename | Old file or new file, never half | Low | Editors, Git |
| Copy-on-write | New blocks for every change | Old state stays intact | High | Some databases and file systems |

The sources for the last column are in [Further reading](#further-reading).

:::example[A flipped byte inside a block]
A pack holds one block of 1,000 bytes with the stored CRC-32C 0x1A2B3C4D, a made-up value for the example. A damaged download turns byte 500 from 0x41 into 0x40, which is a one-bit change.

A reader that only checks bounds sees 1,000 bytes where 1,000 bytes are promised, and it passes them on. A reader that computes the CRC gets a different number, say 0x9F1E7702, which differs from 0x1A2B3C4D, and refuses the block with a message. The cost is one pass over 1,000 bytes. The gain is that the damage appears at the pack instead of as a strange texture an hour later.
:::

## Strata opens a pack by checking all of it

A pack file ends in tables that describe its contents. You met them in [packs and export](packs-export.md). Strata reads the :term[header]{id=header}, checks it, reads the tables, checks them, and only then builds the list of entries. The first excerpt is the start of that work in `AssetPack::Open`.

The question before it: what must a reader know before it trusts a number from a file? Read the excerpt for the order. Every field is checked before it is used for anything.

```cpp src="Strata/src/Strata/Asset/AssetPack.cpp#L271-L292"
Header header;
if (fileSize < sizeof(header) || !reader.ReadAt(0, std::span<uint8_t>(reinterpret_cast<uint8_t*>(&header), sizeof(header))))
	return fail("cannot read the pack header");
const std::span<const uint8_t> headerBytes(reinterpret_cast<const uint8_t*>(&header), offsetof(Header, HeaderChecksum));
if (Hash::CRC32C(headerBytes) != header.HeaderChecksum)
	return fail("corrupt pack header (checksum mismatch)");
if (header.Flags != 0)
	return fail(fmt::format("the pack uses features this engine does not know (flags {:08X})", header.Flags));
if (header.HeaderSize != sizeof(Header) || header.BlockSize < c_MinBlockSize || header.BlockSize > c_MaxBlockSize
	|| (header.BlockSize & (header.BlockSize - 1)) != 0 || header.Reserved != 0)
	return fail("corrupt pack header");
const std::optional<uint64_t> tablesSize = GetTablesSize(header);
if (!tablesSize || *tablesSize > c_MaxTablesSize || header.TablesOffset < sizeof(Header) || header.TablesOffset > fileSize
	|| *tablesSize != fileSize - header.TablesOffset)
	return fail("corrupt pack header (the tables do not end the file)");
pack->m_BlockSize = header.BlockSize;

std::vector<uint8_t> tables(static_cast<size_t>(*tablesSize));
if (!reader.ReadAt(header.TablesOffset, tables))
	return fail("cannot read the tables");
if (Hash::CRC32C(tables) != header.TablesChecksum)
	return fail("corrupt tables (checksum mismatch)");
```

1. **Line 275:** the header's own checksum is compared first, so that a changed byte in a count or an offset is caught before the count is read as a count.
2. **Lines 279–281:** the block size must be a power of two between two limits, and the header size and a reserved field must match what the format says.
3. **Lines 282–285:** the tables must end the file exactly: their size, computed from the counts, must equal the file size minus their offset. Counts that are too large fail here.
4. **Line 288:** the memory for the tables is sized only after those checks, so the size is bounded by the file's size.
5. **Line 291:** the tables have their own checksum, checked before any table is read.

The data blocks are checked later, one at a time, when something reads them. `DecodeBlock` in the same file computes the CRC-32C of the stored bytes and compares it with the block's checksum before it decodes anything. A block whose bytes changed fails with the message `block N is corrupt (checksum mismatch)`. Decoding a damaged block is where the programs that expand data fail worst, so the check sits before it.

Matching checksums are not enough. A writer with a bug, or a person who edits the file and computes both checksums again, makes a pack that passes. So `Open` also checks what the tables say. The next excerpt is the part that checks that each entry's blocks match its size.

```cpp src="Strata/src/Strata/Asset/AssetPack.cpp#L388-L405"
// The blocks cover the stored form exactly: full blocks, then the rest, consecutive in the file. (Counted without
// rounding up, which would overflow for sizes near 2^64.)
const uint64_t expectedBlocks = record.Size / header.BlockSize + (record.Size % header.BlockSize != 0 ? 1 : 0);
if (record.BlockCount != expectedBlocks)
	return fail(fmt::format("entry {} has {} blocks for {} bytes", index, record.BlockCount, record.Size));
for (uint32_t block = 0; block < record.BlockCount; block++)
{
	const AssetPackBlock& current = pack->m_Blocks[record.FirstBlock + block];
	const uint64_t expectedSize = block + 1 < record.BlockCount ? header.BlockSize : record.Size - static_cast<uint64_t>(block) * header.BlockSize;
	if (current.Size != expectedSize)
		return fail(fmt::format("entry {} has a block of the wrong size", index));
	if (block > 0)
	{
		const AssetPackBlock& previous = pack->m_Blocks[record.FirstBlock + block - 1];
		if (previous.Offset + previous.StoredSize != current.Offset)
			return fail(fmt::format("the blocks of entry {} are not consecutive", index));
	}
}
```

1. **Line 390:** the expected number of blocks is the size divided by the block size, plus one for a remainder. The comment says why it is not "round up": rounding would overflow for sizes near the top of a 64-bit number.
2. **Lines 391–392:** the entry's block count must equal the expected count, or the open fails with "entry N has M blocks for K bytes".
3. **Lines 396–398:** every block but the last must be a full block, and the last holds the remainder.
4. **Lines 402–403:** consecutive blocks of an entry must follow each other in the file.

Before this loop, other checks run. Two entries may not share blocks or dependencies: the code counts them, and a total larger than the table fails. Handles must be unique, types known, flags known, and every string, block or dependency an entry names must exist. Names are bounded too: the strings of all entries may add up to at most 16 bytes per byte of the file plus 1 MiB, the value of `GetMaxNameBytes`.

:::example[Numbers from a damaged pack]
The block size is 256 KiB, 262,144 bytes. An entry says its size is 600,000 bytes. Dividing gives 2 whole blocks (524,288 bytes) and a remainder of 75,712, so the entry needs 3 blocks: two of 262,144 bytes and one of 75,712.

A table that lists 2 blocks for this entry is refused with `entry 0 has 2 blocks for 600000 bytes`. A table with 3 blocks whose last one has size 262,144 is refused as `entry 0 has a block of the wrong size`. A table where block 2 does not start where block 1 ends is refused as `the blocks of entry 0 are not consecutive`. Each damage of the table has its own message, which is why the exercise at the end can read them.

For the names, a pack of 1,000,000 bytes may name at most 16 × 1,000,000 + 1,048,576 = 17,048,576 bytes of strings. A table that claims 4 GB of strings fails at once, before `Open` copies any of them.
:::

:::why[Why check everything on open, and not lazily?]
A pack is read many times and written once, so Strata pays for the full check once, at the door. After `Open` succeeds, every later read can rely on the tables without testing them again: a block's offset lies inside the data, and its size matches its entry. The cost is a walk over the tables when a pack opens, which grows with the number of entries and not with the size of the data. The data blocks are the exception: they are large, so each is checked when it is read.
:::

## Sizes come from the bytes the file holds

The pack's checks all share one idea: a number in a file is a claim, and the file's own size is the evidence. Strata applies the idea in every reader of binary data.

The `BinaryReader` class in `Strata/src/Strata/Core/BinaryStream.h` is the tool. Its reads are little-endian (lowest byte first) and bounds-checked. When a read goes past the end, the reader becomes invalid and stays invalid: later reads return zeros, so a loader reads a whole structure and checks `IsValid()` once at the end. The excerpt is the reader of an array with a stored count.

```cpp src="Strata/src/Strata/Core/BinaryStream.h#L76-L90"
// Reads an array written by BinaryWriter::WriteArray. maxCount guards against corrupt lengths.
template<typename T>
bool ReadArray(std::vector<T>& outValues, uint64_t maxCount = UINT32_MAX)
{
	static_assert(std::is_trivially_copyable_v<T>, "BinaryReader::ReadArray requires trivially copyable data");
	const uint64_t count = Read<uint64_t>();
	if (!m_Valid || count > maxCount || count > GetRemaining() / sizeof(T))
	{
		m_Valid = false;
		return false;
	}
	outValues.resize(static_cast<size_t>(count));
	ReadBytes(outValues.data(), static_cast<size_t>(count) * sizeof(T));
	return m_Valid;
}
```

1. **Line 81:** the count comes from the file, so it is a claim and nothing else.
2. **Line 82:** the claim must not exceed the caller's limit, and it must fit the bytes that remain: `count > GetRemaining() / sizeof(T)` fails a count of 1,000,000,000 in a file of 12 bytes. The division avoids a multiplication that could overflow.
3. **Line 87:** memory is made only after both tests passed.

The sketch below is a small model of this idea with two readers. Run it and compare what each reader does with three claims.

```cpp sketch="assets-robustness-reader.cpp"
// Two readers of a count-prefixed array: one trusts the count, one compares it with the bytes that are left.
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>

struct Reader
{
	const uint8_t* Data = nullptr;
	size_t Size = 0;
	size_t Position = 0;
	bool Valid = true;

	size_t GetRemaining() const { return Size - Position; }

	uint32_t ReadCount()
	{
		uint32_t count = 0;
		if (!Valid || GetRemaining() < sizeof(count))
		{
			Valid = false;
			return 0;
		}
		std::memcpy(&count, Data + Position, sizeof(count));
		Position += sizeof(count);
		return count;
	}
};

// The naive reader: the count decides how much memory is asked for.
uint64_t NaiveBytesRequested(Reader& reader, size_t elementSize)
{
	return static_cast<uint64_t>(reader.ReadCount()) * elementSize;
}

// The bounded reader: the count must fit in what the file still holds, else the reader fails and stays failed.
bool ReadBounded(Reader& reader, size_t elementSize, std::vector<uint8_t>& out)
{
	const uint64_t count = reader.ReadCount();
	if (!reader.Valid || count > reader.GetRemaining() / elementSize)
	{
		reader.Valid = false;
		return false;
	}
	out.assign(reader.Data + reader.Position, reader.Data + reader.Position + count * elementSize);
	reader.Position += count * elementSize;
	return true;
}

int main()
{
	// A 12-byte file: a count, then 8 bytes of data.
	const uint32_t claims[] = { 2, 3, 1'000'000'000 };
	for (uint32_t claim : claims)
	{
		uint8_t file[12] = {};
		std::memcpy(file, &claim, sizeof(claim));
		Reader naive { file, sizeof(file) };
		Reader bounded { file, sizeof(file) };
		std::vector<uint8_t> out;
		const bool accepted = ReadBounded(bounded, 4, out);
		std::printf("claim %u: naive asks for %llu bytes, bounded %s\n", claim,
			static_cast<unsigned long long>(NaiveBytesRequested(naive, 4)), accepted ? "accepts" : "refuses");
	}
	return 0;
}
```

```text output-of="assets-robustness-reader.cpp"
claim 2: naive asks for 8 bytes, bounded accepts
claim 3: naive asks for 12 bytes, bounded refuses
claim 1000000000: naive asks for 4000000000 bytes, bounded refuses
```

1. **Line 33:** the naive reader turns the claim into a request for memory at once.
2. **Line 40:** the bounded reader compares the claim with what remains, in a division, so that the test itself cannot overflow.
3. **Lines 45–46:** the data is copied only after the test.
4. **Line 53:** the claims: one that fits, one that is 4 bytes too many, and a billion.

The naive reader asks for 4,000,000,000 bytes for the last claim, from a file of 12 bytes. The bounded reader accepts the claim of 2 elements, which exactly fills the 8 bytes that remain, and refuses 3, which would need 12. It refuses the billion for the same reason, with no memory spent.

The same rule bounds the glTF importer, where the file states sizes in many places and a model of a few thousand bytes may describe a very large amount of work. Its limits are constants at the top of `GltfImporter.cpp`.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L57-L68"
// What a model's compressed buffer views may decode to, in all: hostile files must not exhaust memory.
constexpr uint64_t c_MaxDecodedBytes = 1ull << 30;

// Limits that keep hostile or broken files from exhausting memory, time or the stack. The geometry an import
// expands (vertices plus triangle corners over all primitives) is limited relative to the loaded buffers:
// accessors can describe far more data than a file holds (zero-filled accessors, accessors shared by many
// primitives).
constexpr uint64_t c_MaxAccessorElements = 1ull << 30;
constexpr uint64_t c_MinGeometryBudget = 1ull << 22;  // Elements every file may expand to
constexpr uint64_t c_GeometryBudgetPerBufferByte = 4; // Elements per loaded buffer byte beyond that
constexpr uint64_t c_MaxGeometryBudget = 1ull << 28;
constexpr uint32_t c_MaxHierarchyDepth = 1024;
```

1. **Line 58:** the compressed buffers of a model may decode to at most 1 GiB in all, so a small file that expands a thousand times over stops here.
2. **Line 64:** one `accessor` may describe at most 2^30 elements.
3. **Lines 65–67:** the geometry an import expands is limited relative to the buffers the file holds. The budget is 4 elements for each buffer byte, but never fewer than 4,194,304 or more than 268,435,456.
4. **Line 68:** a node hierarchy may be at most 1,024 levels deep, which protects the stack of a walk that calls itself and catches cycles.

:::example[A model that claims a billion vertex entries]
The file's buffers hold 10,000 bytes. Its budget is the larger of 4,194,304 and 10,000 × 4 = 40,000, so 4,194,304 elements, and the ceiling does not matter. One `accessor` claims 1,000,000,000 vertex entries. That is below the limit of one `accessor`, 2^30 = 1,073,741,824, so that test passes.

If the `accessor` reads from a buffer view, the layout check refuses it next: it reads past the end of its view. The hard case is an `accessor` with no buffer view, which glTF allows and fills with zeros.

The geometry budget catches that one. Each primitive adds its vertex entries and triangle corners to a running total, and a total above 4,194,304 fails the import with an error, before any vertex array of that size exists. A model with 2 MiB of buffers, 2,097,152 bytes, has a budget of 8,388,608; the ceiling of 268,435,456 is reached at 64 MiB of buffers. The budget grows with the file because a larger file can hold more honest geometry, but never faster than 4 elements for each byte.
:::

Every loader follows this rule. A loader that meets truncated or garbage bytes returns an error and logs it; it does not assert and does not crash. The engine's rules say it plainly, and say that a change to the pack or :term[cooked scene]{id=cooked-scene} format extends the corruption tests of those formats. The cooked texture reader, `ParseCookedTexture`, reads through the same `BinaryReader` and returns no value, with an error message, for a bad file.

:::rule[Every loader rejects truncated or garbage bytes]
The engine's guide requires that loaders reject truncated or garbage bytes without crashing, and that large documents ask the cancel flag as they go. The reason is the one of this page: a file on disk is input from outside. The pages on [importing](importing.md) and [packs](packs-export.md) show the formats.
:::

## Records survive a power cut because of their order

Checks guard what the engine reads. The next rule guards what it writes. Recall from [importing](importing.md) that an import produces cache files and a record, a small description of the import that says which cache files are current. The record is the note, and the cache files are the data.

The import's last step takes the :term[file lock]{id=file-lock}, checks the cancel flag once more, renames the staged cache files (written under temporary names) into place and only then sets the record. The excerpt shows the first half of that step.

```cpp src="Strata/src/Strata/Asset/EditorAssetManager.cpp#L2191-L2202"
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
```

1. **Lines 2191–2192:** under the exclusive lock, the import asks once more whether it is still wanted.
2. **Lines 2193–2197:** if it is not, the staged files are removed and nothing is published.
3. **Lines 2200–2202:** the staged files move to their final names, and the `written` flag records whether every rename worked.

Lower in the same function, the call `SetRecord` of the record store runs after these renames, under the same lock, with a comment that the record never names a missing file. Suppose the power fails after 2 of 3 renames. The record is still the old one, or none, so the asset is imported again at the next start. Suppose the power fails after all renames but before the record is set: the cache files are there, named by no record, and the next import replaces them. No order of crash leaves a record that names a missing file.

The record store is one file, `ImportRecords.log`, with the same care. Its first line is a header. Each later line is the CRC-32C of a :term[JSON]{id=json} text as 8 :term[hexadecimal]{id=hexadecimal} digits, a space and the compact JSON. A writer appends whole lines, one writer at a time, and flushes per batch. Reading it back is where torn writes are met.

```cpp src="Strata/src/Strata/Asset/ImportRecordStore.cpp#L307-L318"
// A last line without its line feed was torn by a crash: it goes, so that appends start on a line of their own.
const size_t lastFeed = all.rfind('\n');
const size_t whole = lastFeed == std::string_view::npos ? 0 : lastFeed + 1;
if (whole < all.size())
{
	std::error_code error;
	std::filesystem::resize_file(shared.File, whole, error);
	if (error)
		ST_CORE_WARN("Could not cut the torn end of '{}': {}", FileSystem::ToUTF8(shared.File), error.message());
	else
		stats.SkippedLines++;
}
```

1. **Lines 308–309:** a file whose last byte is not a line feed ends in a torn line, so `whole` marks the end of the last complete line.
2. **Line 313:** the torn part is cut off the file, so that the next append starts on a line of its own.
3. **Line 317:** the cut counts as one skipped line.

For the lines that remain, `CheckLine` compares the checksum with the JSON text, and a line whose checksum or JSON is bad is skipped. The asset it described is imported again, which costs time but is never wrong. The latest record of a handle wins, so a rewrite of a record is only an append. When dead lines outnumber live ones and the file exceeds 1 MiB, the writer rebuilds the file from memory through an atomic write, the technique of [Core files](../core/files.md).

:::why[Why one append-only log, not one file per asset?]
A file per asset means thousands of small writes, each with its own chance of a torn file, and a scan that opens thousands of files. An append-only log writes whole lines in one place and loses at most the last one. The price is the compaction, which has to be an atomic rewrite and which Strata starts only when it pays: more than half dead and over 1 MiB. Older projects that kept `.import` files and `AssetIndex.json` are read once and moved into the log.
:::

The sketch below is a toy of this design, with a real CRC-32C. It writes 3 records, cuts the file in three places and changes one byte. Predict the number of records that survive each case before you run it; the exercise returns to it.

```cpp sketch="assets-robustness-log.cpp"
// A record log in the style of the import record store: one line per record, "<crc> <text>", the last line possibly torn.
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

// CRC-32C (Castagnoli), bit by bit: slow and short.
uint32_t Crc32c(const std::string& text)
{
	uint32_t crc = 0xFFFFFFFFu;
	for (char character : text)
	{
		crc ^= static_cast<uint8_t>(character);
		for (int bit = 0; bit < 8; bit++)
			crc = (crc >> 1) ^ ((crc & 1u) != 0 ? 0x82F63B78u : 0u);
	}
	return ~crc;
}

std::string FormatLine(const std::string& text)
{
	char prefix[16];
	std::snprintf(prefix, sizeof(prefix), "%08x ", Crc32c(text));
	return std::string(prefix) + text + "\n";
}

struct LoadResult
{
	std::vector<std::string> Records;
	int Skipped = 0;
	size_t KeptBytes = 0;
};

LoadResult Load(const std::string& file)
{
	LoadResult result;
	const size_t lastFeed = file.rfind('\n');
	const size_t whole = lastFeed == std::string::npos ? 0 : lastFeed + 1;
	if (whole < file.size())
		result.Skipped++; // a last line without its line feed was torn: it is cut
	result.KeptBytes = whole;

	size_t position = 0;
	while (position < whole)
	{
		const size_t end = file.find('\n', position);
		const std::string line = file.substr(position, end - position);
		position = end + 1;
		const bool shaped = line.size() > 9 && line[8] == ' ';
		const std::string text = shaped ? line.substr(9) : std::string();
		char expected[16];
		std::snprintf(expected, sizeof(expected), "%08x", Crc32c(text));
		if (shaped && line.compare(0, 8, expected) == 0)
			result.Records.push_back(text);
		else
			result.Skipped++;
	}
	return result;
}

int main()
{
	std::string file = FormatLine("asset 1 imported") + FormatLine("asset 2 imported") + FormatLine("asset 3 imported");
	const size_t cuts[] = { file.size(), file.size() - 5, file.size() - 25 };
	for (size_t cut : cuts)
	{
		const LoadResult result = Load(file.substr(0, cut));
		std::printf("cut at %zu of %zu: %zu records, %d skipped, %zu bytes kept\n", cut, file.size(), result.Records.size(),
			result.Skipped, result.KeptBytes);
	}
	std::string flipped = file;
	flipped[12] = 'X'; // a changed byte inside the first record's text
	const LoadResult result = Load(flipped);
	std::printf("one byte changed: %zu records, %d skipped\n", result.Records.size(), result.Skipped);
	return 0;
}
```

```text output-of="assets-robustness-log.cpp"
cut at 78 of 78: 3 records, 0 skipped, 78 bytes kept
cut at 73 of 78: 2 records, 1 skipped, 52 bytes kept
cut at 53 of 78: 2 records, 1 skipped, 52 bytes kept
one byte changed: 2 records, 1 skipped
```

1. **Lines 37–41:** a last line without its line feed is torn, so the load counts one skipped line and keeps only whole lines.
2. **Lines 49–53:** each whole line is split into its checksum and its text, and the checksum is computed again from the text.
3. **Lines 55–56:** a line that fails the comparison is skipped, and the loop continues with the next line.
4. **Lines 63–64:** the file of 3 lines and the three cut points.
5. **Line 72:** a changed byte inside the first record's text.

A file that is not cut keeps all 3 records. A cut 5 bytes before the end tears the third line, so 2 records survive and 1 line is cut. Each line has 26 bytes, so a cut 25 bytes before the end keeps 1 byte of the third line, which is torn too. A changed byte inside the first record fails its checksum, so that record is skipped and the other 2 are kept: the damage is local.

## Cancel flags make closing instant

The third failure was the project that closed slowly. Strata's answer has no waiting in it.

Each import is a background job with an atomic flag, the `Cancel` pointer of `ImportContext`. Whoever no longer wants the import sets the flag: a move, a delete, a new setting, a re-import of the same asset, or `Close`. A queued job whose flag is set never starts. A running job reads the flag at its checks and stops at the next one. The importers check at the points where stopping is cheap: the texture cooker per block of a compressed level and between mip levels, the glTF importer between images, primitives and levels of detail.

`ImportContext::IsCancelled` in `Strata/src/Strata/Asset/AssetImporter.h` is the check. It reads the flag with relaxed ordering, the cheapest read of an atomic value, because the check only needs to see the change soon, not in order with other data. A cancelled import stores nothing, and the publication step above checks the flag again under the lock, so a cancelled import cannot publish after a move or delete changed what it read.

Closing must also not wait for the jobs to end. For that, jobs share only a small object, `BackgroundWork`, which holds the folders, the file lock, the job set and the results, and a pointer to the manager that `Close` clears. The manager and the jobs each keep that object alive.

With 17 imports of a stress project running, the close that took 5.6 to 12 seconds took 0.06 to 0.34 seconds after the change, according to `Docs/Roadmap.md`. `Close` sets every flag and returns. A job that lasts longer than the manager finishes alone, and Strata discards its result.

Tools and tests differ: `WaitForImports` and `BuildAssetPack` wait for every wanted import, because a build needs the results. The editor never calls them from a frame. The rule at the pin is that nothing in the editor waits for a background import.

:::example[Closing with 17 imports running]
Suppose the flags are set at time 0, 13 jobs are still queued and 4 are running. The queued jobs never start. A texture job is between two blocks of a level and sees the flag at its next block, perhaps 2 ms later. A glTF job is decoding a large image and sees it when the image is done.

`Close` has already returned. The four jobs stop one after another, remove their staged files and hand over nothing. The person sees the editor close at once, in about a third of a second at most. The work is wasted, but nobody wanted its result.
:::

## Tests keep the rules true

A rule that no test enforces fades with the next change of the format. Strata keeps three kinds of tests for this page, and the engineering part teaches the general method of the first two.

The pack tests in the suite `Asset.Pack` build a pack and break it in named ways: a wrong :term[magic number]{id=magic-number}, a future version, a changed header count and a changed table byte. Other cases rewrite the tables with matching checksums and wrong content. Each case names the message it expects. The suite `Asset.Pack.Sweep` truncates a pack at many lengths and flips single bytes at many offsets. It requires an error or a right read, and never a crash.

The sweep covers the bytes of the header and the tables and those around every block boundary in full, and a sample of the rest.

The sweep that flips one byte is the one to read.

```cpp src="StrataTests/src/Asset/AssetPackTests.cpp#L1020-L1029"
const std::vector<size_t> offsets = SelectSweepOffsets(smallBytes->size(), { { 0, sizeof(Header) }, { image.Data.size(), smallBytes->size() } },
	AssetPack::c_EntryAlignment);
for (size_t offset : offsets)
{
	CAPTURE(offset);
	std::vector<uint8_t> changed = *smallBytes;
	changed[offset] ^= 0xA5;
	REQUIRE(FileSystem::WriteBytes(corrupt, changed));
	OpenAndReadEverything(corrupt);
}
```

1. **Line 1022:** the loop visits each selected offset in turn.
2. **Line 1026:** it flips four bits of the byte at that offset with an exclusive-or by `0xA5`, on a fresh copy.
3. **Line 1028:** `OpenAndReadEverything` opens the pack and reads every entry; either an error with a message comes back, or the data is read, and the test only fails on a crash or a missing message.

The test allows "reads right" because some bytes in a pack do not matter, such as padding between entries. A flip there changes nothing a reader sees. Every other flip must be caught by a checksum or a consistency check.

The record store has a matching test, which cuts its file at every byte of the last three entries, and a second that flips a checksum. The corrupt-bytes tests of every loader complete the set; the engine's rule says that a change of a pack or cooked scene format extends `AssetPackTests.cpp` or `CookedSceneTests.cpp`.

## What Strata's choice cannot do

A CRC finds accidents. It is not a signature. A person who edits a pack can change the data and compute the block checksum again and both table checksums, and the pack passes every check of `Open`. The consistency checks keep such a file from crashing the engine, but they cannot tell a harmless edit from a harmful one: a modified texture is a valid texture.

Strata does not sign exports, so it cannot tell that a game pack comes from its maker. [Worlds export](../worlds/export.md) and [game identity](../worlds/game-identity.md) cover what the export does record. See also [what Strata does not do](../appendix/not-in-strata.md).

Bounds also have costs. A legitimate model above the limits fails to import, and the person must split it. The limits are set at 1 GiB of decoded bytes and 2^30 elements for one `accessor`, far above what a game file needs, but they are real. Checking everything on open costs a pass over the tables for every pack. And write-ahead ordering protects the record log from crashes of the program or the power; it does not protect it from a disk that lies about a finished flush.

## Common mistakes

- **Allocating what a size field says.** Symptom: a file of 12 bytes makes the program ask for 4 GB, and the program stops or the machine swaps. Fix: compare the count with the bytes that remain, as `ReadArray` does, before any allocation.
- **Checking after use.** Symptom: a loader uses a count in a loop and checks the total at the end, so the loop has already run past the buffer. Fix: check each field before the first use, in the order of the file.
- **Trusting a checksum alone.** Symptom: a file with a correct checksum and tables that disagree reaches the decoder. Fix: run the consistency checks too, as `Open` does for block counts, sizes and offsets.
- **Writing the record, then the data.** Symptom: after a power cut the record names a file that is not there. Fix: rename the data into place first, and set the record last.
- **Joining threads on close.** Symptom: the window hangs for as long as the slowest import. Fix: set the flags, let the jobs share only the work object, and return.
- **Checking the flag too seldom.** Symptom: a cancelled import runs for seconds more. Fix: check at each block or each step, where stopping is cheap.
- **Skipping the regression test.** Symptom: a new format version accepts a damaged file nobody tried. Fix: extend the corruption test of the format with each new field.

## Summary

- A loader treats every file as input from outside and takes every size from the bytes the file holds: a count is a claim, and the bytes that remain are the evidence.
- A pack's header and tables have checksums and are checked completely on open, entries may not share blocks, blocks must cover their entry exactly, and each block's CRC-32C is checked before it is decoded.
- Cache files are renamed into place before the record that names them, and the record log has one line per record, each with its own checksum. A crash leaves at worst a torn last line, which Strata skips and cuts.
- Every import checks a cancel flag at its steps, and jobs share only the work object, so closing a project sets flags and returns without waiting.
- A CRC finds accidents and not an attacker, and Strata does not sign exports.

## Check yourself

1. A loader reads a 4-byte count, then allocates `count * 16` bytes and reads that many. Which change makes it safe against a file that lies?

   - A. Check the checksum of the file after reading.
   - B. Compare the count with the bytes left in the file divided by 16, before allocating.
   - C. Catch the exception the allocation throws.
   - D. Read the data in a loop and stop when it ends.

   :::answer{tests="untrusted-input"}
   B. The count is a claim, and only the bytes that remain can confirm it, so the test comes before the allocation. A checks too late: the allocation has already happened. C fails because engine code does not throw, and a system may agree to a huge allocation anyway. D reads safely but the memory was already requested if the loop sizes a buffer from the count.
   :::

2. An entry is 700,000 bytes and the block size is 262,144. How many blocks must it have, and how large is the last?

   :::answer{tests="pack-checks"}
   Two whole blocks make 524,288 bytes. The remainder is 700,000 − 524,288 = 175,712, which is not zero, so the entry needs 3 blocks, and the last holds 175,712 bytes. A table with another count fails with `entry N has M blocks for 700000 bytes`.
   :::

3. A power cut happens between the rename of the last cache file and the setting of the record. What does the engine do at the next start, and why is that safe?

   :::answer{tests="write-ahead"}
   The record is the old one or none, so the engine sees the asset as not current and imports it again. The engine replaces the cache files that were renamed. Nothing wrong is read, because no record names data that is missing.
   :::

4. Why does closing a project not wait for a running import, and what does the import do when it later sees its flag?

   :::answer{tests="cancel-flag"}
   `Close` sets each job's atomic flag and returns, and the jobs keep their shared work object alive without the manager. A running job reads the flag at its next check, stops, removes its staged files and hands over nothing. Waiting would make the close last as long as the slowest import.
   :::

5. Someone edits a pack's texture and computes every checksum again. Does `Open` accept it, and what protects against such a change?

   :::answer{tests="limits"}
   Yes. A CRC finds accidents. An editor who computes the numbers again produces a pack that passes the checks, and the consistency checks only prove that the pack is safe to read. Strata does not sign exports, so nothing in it tells who made a pack.
   :::

## Exercises

1. **Basic.** The log of the sketch has 3 lines of 26 bytes each, 78 bytes in all. Predict how many records survive when the file is cut at 53, 77 and 78 bytes.

   :::answer[Worked solution]{tests="write-ahead"}
   A cut at 53 bytes holds two whole lines (52 bytes) and 1 byte of the third. The last byte is not a line feed, so that 1 byte is a torn line: it is cut, and 2 records survive. A cut at 77 bytes tears the third line one byte short of its line feed: 2 survive. A cut at 78 bytes holds all 3 lines with their line feeds: 3 survive and nothing is skipped.
   :::

2. **Medium.** Change the sketch so that a damaged line in the middle of the file ends the load instead of being skipped, and say which design the engine chose and why.

   :::answer[Worked solution]{tests="write-ahead" solution="sketches/assets-robustness-log-stop.cpp"}
   In `Load`, a failed checksum would `break` from the loop instead of counting a skipped line. The records after the damage are then lost. The engine skips: a bad line only costs one asset an import again, and the later records are still right, because each line carries its own checksum. The sketch below is the whole changed file.

   ```cpp sketch="assets-robustness-log-stop.cpp"
   // The log of assets-robustness-log.cpp, changed so that a damaged line ends the load. A record log in the style of the import record store: one line per record, "<crc> <text>", the last line possibly torn.
   #include <cstdint>
   #include <cstdio>
   #include <string>
   #include <vector>

   // CRC-32C (Castagnoli), bit by bit: slow and short.
   uint32_t Crc32c(const std::string& text)
   {
   	uint32_t crc = 0xFFFFFFFFu;
   	for (char character : text)
   	{
   		crc ^= static_cast<uint8_t>(character);
   		for (int bit = 0; bit < 8; bit++)
   			crc = (crc >> 1) ^ ((crc & 1u) != 0 ? 0x82F63B78u : 0u);
   	}
   	return ~crc;
   }

   std::string FormatLine(const std::string& text)
   {
   	char prefix[16];
   	std::snprintf(prefix, sizeof(prefix), "%08x ", Crc32c(text));
   	return std::string(prefix) + text + "\n";
   }

   struct LoadResult
   {
   	std::vector<std::string> Records;
   	int Skipped = 0;
   	size_t KeptBytes = 0;
   };

   LoadResult Load(const std::string& file)
   {
   	LoadResult result;
   	const size_t lastFeed = file.rfind('\n');
   	const size_t whole = lastFeed == std::string::npos ? 0 : lastFeed + 1;
   	if (whole < file.size())
   		result.Skipped++; // a last line without its line feed was torn: it is cut
   	result.KeptBytes = whole;

   	size_t position = 0;
   	while (position < whole)
   	{
   		const size_t end = file.find('\n', position);
   		const std::string line = file.substr(position, end - position);
   		position = end + 1;
   		const bool shaped = line.size() > 9 && line[8] == ' ';
   		const std::string text = shaped ? line.substr(9) : std::string();
   		char expected[16];
   		std::snprintf(expected, sizeof(expected), "%08x", Crc32c(text));
   		if (shaped && line.compare(0, 8, expected) == 0)
   			result.Records.push_back(text);
   		else
   		{
   			result.Skipped++;
   			break; // a damaged line ends the load: everything after it is lost
   		}
   	}
   	return result;
   }

   int main()
   {
   	std::string file = FormatLine("asset 1 imported") + FormatLine("asset 2 imported") + FormatLine("asset 3 imported");
   	const size_t cuts[] = { file.size(), file.size() - 5, file.size() - 25 };
   	for (size_t cut : cuts)
   	{
   		const LoadResult result = Load(file.substr(0, cut));
   		std::printf("cut at %zu of %zu: %zu records, %d skipped, %zu bytes kept\n", cut, file.size(), result.Records.size(),
   			result.Skipped, result.KeptBytes);
   	}
   	std::string flipped = file;
   	flipped[12] = 'X'; // a changed byte inside the first record's text
   	const LoadResult result = Load(flipped);
   	std::printf("one byte changed: %zu records, %d skipped\n", result.Records.size(), result.Skipped);
   	return 0;
   }
   ```

   ```text output-of="assets-robustness-log-stop.cpp"
   cut at 78 of 78: 3 records, 0 skipped, 78 bytes kept
   cut at 73 of 78: 2 records, 1 skipped, 52 bytes kept
   cut at 53 of 78: 2 records, 1 skipped, 52 bytes kept
   one byte changed: 0 records, 1 skipped
   ```

   1. **Lines 55–59:** the changed branch: the first damaged line ends the load, so every line after it is lost.

   The last line of the output shows 0 records after the damaged first line, where the skipping loader kept 2.
   :::

3. **Hard.** Add a test case to `AssetPackTests.cpp` that changes one byte inside the first block of the first entry. The test checks that the pack still opens and that reading the first entry fails with a message that holds `checksum mismatch`. The test also checks that the second entry still reads. Explain why the pack opens at all.

   :::answer[Worked solution]{tests="pack-checks" solution="tutorials/assets/robustness/exercise-3.patch"}
   The header and the tables are untouched, so their checksums hold and `Open` succeeds: block data is checked only when read. The test finds the byte with `image.Blocks[0].Offset`, the file offset of the first block, flips it with `0xA5`, and opens the changed file. `ReadData` of entry 0 reaches `DecodeBlock`, whose CRC-32C comparison fails before decoding, with a message that holds `checksum mismatch`. Entry 1 has other blocks and reads right.

   The patch adds the case after the single-changed-byte test, in `Asset.Pack.Sweep`. Remove the line that flips the byte, and the test must fail: that is how you know it tests the fix.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetPack.cpp`: `AssetPack::Open` (header, tables and consistency checks), `DecodeBlock` (the block checksum) and `AssetPackFormat::GetMaxNameBytes`.
- `Strata/src/Strata/Core/BinaryStream.h`: `BinaryWriter` and `BinaryReader`.
- `Strata/src/Strata/Asset/GltfImporter.cpp`: the limits at the top of the file and the geometry budget check.
- `Strata/src/Strata/Asset/ImportRecordStore.h` and `Strata/src/Strata/Asset/ImportRecordStore.cpp`: the record log, its load and its compaction.
- `Strata/src/Strata/Asset/EditorAssetManager.cpp`: the publication of cache files and the record.
- `Strata/src/Strata/Asset/AssetImporter.h`: `ImportContext::Cancel` and `ImportContext::IsCancelled`.
- `Strata/src/Strata/Renderer/CookedTexture.h`: `ParseCookedTexture`.
- Tests: the suites `Asset.Pack` and `Asset.Pack.Sweep` in `StrataTests/src/Asset/AssetPackTests.cpp`.

## Further reading

- SQLite, "Atomic Commit In SQLite" (sqlite.org): how a database uses a journal and flushes to the disk to commit in one step. Advanced.
- Dan Luu, "Files are hard" (danluu.com): what file systems promise after a crash, and where programs assume more. Intermediate.
- The specification of PNG, section on CRC: how a format protects each chunk with a CRC-32. Intermediate.
- The manual of libFuzzer, from the LLVM project: how a fuzzer finds the inputs that crash a parser. Intermediate.
- The documentation of Git's object storage: how loose objects are written to a temporary file and renamed. Intermediate.
