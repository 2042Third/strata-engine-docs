---
id: basics/bytes
title: "Bytes in files and memory: layouts, byte order and text encodings"
description: "How files, numbers, structs, images and text are laid out as bytes, and how to read them without trusting what a file claims."
kind: primer
size: L
tracks: [B, E]
needs: [basics/numbers, basics/tools, basics/cpp-generic]
time: 75
learn:
  - id: byte-order
    text: compute the bytes of a 32-bit number in little-endian and big-endian order, and read a number back from four bytes
  - id: offsets
    text: compute where a header field, a record or a pixel starts in a file from offsets, sizes and row lengths
  - id: untrusted-lengths
    text: write the checks that bound a length read from a file by the file's size before anything is allocated
  - id: struct-layout
    text: compute the size and member offsets of a struct from alignment and padding, and fix a layout with static_assert
  - id: utf-8
    text: explain how UTF-8 stores a code point in one to four bytes, and count characters against bytes
status: final
---

::::test-out

1. Write the four bytes of the number 300 (hex `0x0000012C`) in the order a little-endian file stores them, as hex.

   :::answer{tests="byte-order"}
   300 is 0x12C. A little-endian file stores the lowest byte first: `2C 01 00 00`. A big-endian file stores
   `00 00 01 2C`.
   :::

2. A struct has the members `uint8_t Kind;` and then `uint32_t Count;`. How many bytes does it take on a desktop
   compiler, and where does `Count` start?

   :::answer{tests="struct-layout"}
   The struct takes 8 bytes, and `Count` starts at byte 4. `Kind` takes byte 0, and three bytes of padding follow, so
   that the 4-byte `Count` starts on a multiple of 4.
   :::

3. How many bytes does the text `Müll` take in UTF-8, and how many code points does it hold?

   :::answer{tests="utf-8"}
   The text takes 5 bytes and holds 4 code points. The letter ü is U+00FC, which needs two bytes (`C3 BC`); each of the
   other three letters needs one.
   :::

4. A file of 1,000 bytes starts with a 16-byte header that says the file holds 200 records of 8 bytes. Write the
   condition that makes a reader refuse the file before it allocates anything.

   :::answer{tests="untrusted-lengths"}
   The records must fit in the bytes after the header: refuse when `count > (1000 - 16) / 8`. The limit is 123, and 200
   is more, so the reader refuses.
   :::

5. An image is 4 pixels wide and 3 high and stores 4 bytes per pixel, row after row with no gaps. How many bytes does
   the image take, and at which offset does the pixel at x = 2, y = 1 start?

   :::answer{tests="offsets"}
   The image takes 4 × 3 × 4 = 48 bytes. The pixel is the third of the second row, so it starts at (1 × 4 + 2) × 4 = 24.
   :::

::::

## Why you will need this

Every file a game loads is a row of :term[bytes]{id=byte}, and so is every block of memory the :term[graphics card]{id=gpu} reads. When a program reads
those bytes the wrong way, the symptoms are odd: a texture with the wrong colors, a name that ends in black squares, or a
crash that only a damaged file causes.

Other pages build on this one. [Files in Strata](../core/files.md) shows how the engine moves text between Windows and
the rest of the system, which needs the encodings below. [Robustness of loaders](../assets/robustness.md) shows how the
asset pipeline survives files that lie, starting from the bounded lengths of this page. [Data
formats](../basics/data-formats.md) covers the text formats that sit on top of bytes.

Each part has a small example worked by hand before the code.

## A file is bytes, and a format says what they mean

Open any file in a viewer that shows bytes, and you see numbers from 0 to 255, usually written in :term[hexadecimal]{id=hexadecimal}. A file of
8 bytes could look like this:

```text
53 54 54 58 02 00 00 00
```

The viewer cannot tell what these bytes mean, and neither can you, until someone tells you. Read the first four as
text, and they are the letters `STTX`. Read the same four as one number, and you get a large value. Read the last four as
a number, and you get 2. A **file format** is the agreement about what each byte of a file means: where each number
starts, how many bytes it takes, and in which order the parts follow.

Writing data from memory into the bytes of a file is **serialization**. Reading the bytes back into memory is the
reverse. The writer and the reader must follow the same format, or the reader builds nonsense. Most formats therefore
begin with a few bytes that name the format.

Files come in two kinds. In a text file, every byte or group of bytes stands for a letter, a digit or a symbol, so any
editor can show the file. A binary file holds anything else: numbers, pixels, tables of offsets. An editor shows a binary
file as garbage, and only a program that knows the format can read it.

The size of a file is its number of bytes. A byte is small, so sizes use the prefixes of [Numbers in a
computer](../basics/numbers.md): 1 `KiB` is 1,024 bytes, and 1 `MiB` is 1,024 `KiB`, which is 1,048,576 bytes. A buffer, a
block of memory that holds bytes for a while, has a size in the same units.

The position of a byte in a file is its offset: the number of bytes before it. The first byte has offset 0, so a file of 8
bytes has the offsets 0 to 7, and an offset equal to the size points past the end.

:::example[The 8 bytes are a texture header]
Strata starts a cooked texture file with the four bytes `53 54 54 58`, the letters `STTX`. A little-endian reader
computes 0x58545453 from them, the value of `c_CookedTextureMagic` in `Strata/src/Strata/Renderer/CookedTexture.h`. The
next four bytes, `02 00 00 00`, give the number 2, the version of the file.

So the 8 bytes are the start of a cooked texture of version 2: a magic value at offset 0 and a version at offset 4. The
next section explains why the number reads 0x58545453 although the first byte is 0x53.
:::

Try it: a file holds the 8 bytes `43 4F 49 4E 01 00 00 00`. At which offset does the number 1 start, and how many bytes
does it take?

:::answer
The number starts at offset 4 and takes 4 bytes. The first four bytes are the letters `COIN`.
:::

## A number takes several bytes, and byte order says which comes first

A byte holds 0 to 255, so larger numbers need several bytes. A `uint16_t` takes 2 bytes, a `uint32_t` and a `float` take
4, and a `uint64_t` and a `double` take 8. The operator `sizeof` gives the size of a type in bytes. The 32-bit number 300
takes four bytes, two of which are zero.

The bytes of one number can be stored in two orders. **Endianness**, also called **byte order**, is the order in which a
number's bytes are stored: a little-endian format stores the lowest byte first, and a big-endian format stores the
highest byte first. People write numbers big-endian, with the biggest digit first. Every platform Strata supports is
little-endian, and some network protocols and older file formats are big-endian.

:::example[The number 300 in four bytes]
In hexadecimal, 300 is 0x012C, and in 32 bits it is 0x0000012C. Its four bytes, highest to lowest, are `00`, `00`, `01`
and `2C`. A little-endian file stores them from the lowest: `2C 01 00 00`. A big-endian file stores them as written:
`00 00 01 2C`.

To read the little-endian bytes back, shift each byte to its place: byte 0 stays, byte 1 shifts by 8 bits, byte 2 by 16
and byte 3 by 24. Here that gives 0x2C + 0x01 × 256 = 44 + 256 = 300. The magic of the last section reads the same way:
in `53 54 54 58`, the byte `58` lands in the highest place, which gives 0x58545453.
:::

The sketch below writes 300 into four bytes with shifts and prints both orders. It then reads the number back in two ways:
with shifts, and by copying the bytes into a `uint32_t` with `std::memcpy`. Check that both reads give 300.

```cpp sketch="basics-bytes-endian.cpp"
// Writes 300 as four little-endian bytes, reads it back by shifts and by copying memory.
#include <cstdint>
#include <cstdio>
#include <cstring>

int main()
{
	const uint32_t value = 300; // 0x0000012C
	uint8_t bytes[4] = {};
	for (int index = 0; index < 4; index++)
		bytes[index] = static_cast<uint8_t>(value >> (8 * index)); // The lowest byte goes first
	std::printf("little-endian: %02X %02X %02X %02X\n", bytes[0], bytes[1], bytes[2], bytes[3]);
	std::printf("big-endian:    %02X %02X %02X %02X\n", bytes[3], bytes[2], bytes[1], bytes[0]);

	uint32_t again = 0;
	for (int index = 3; index >= 0; index--)
		again = (again << 8) | bytes[index];
	uint32_t copied = 0;
	std::memcpy(&copied, bytes, sizeof(copied)); // Reads the bytes the way this machine does
	std::printf("by shifts %u, by memcpy %u\n", again, copied);
}
```

```text output-of="basics-bytes-endian.cpp"
little-endian: 2C 01 00 00
big-endian:    00 00 01 2C
by shifts 300, by memcpy 300
```

1. **Line 11:** shifting the value right by `8 * index` brings byte number `index` to the lowest place, and the cast keeps
   only that byte.
2. **Lines 16–17:** the loop starts at the highest byte and shifts the number left by 8 bits before each new byte joins it.
3. **Line 19:** `std::memcpy` copies the bytes as they are, so the result is right only when the machine's order matches
   the file's.

:::why
Strata writes every binary format little-endian and copies numbers straight from memory. In the words of
`Strata/src/Strata/Core/BinaryStream.h`, all supported platforms are little-endian, and the formats record this by
convention. The gain is simple, fast code with no byte reversal. The cost is that a big-endian platform would need
conversion code in every reader.
:::

Try it: write 0x0A0B0C0D as four bytes in big-endian order, and read the little-endian bytes `01 02 00 00` as a number.

:::answer
The big-endian bytes are `0A 0B 0C 0D`. The little-endian number is 0x01 + 0x02 × 256 = 513.
:::

## A binary layout puts a header first and records after it

Most binary formats share one shape. A **header** is the block of fixed size at the start of a file that describes the
rest. After it come the data, often as records of equal size, or tables that say where each part lies. The reader uses
the header to find everything else.

A header usually holds a **magic number**: a fixed value at the start of a file that says which format the file claims to
be. A file without the magic is not of this format, whatever its name says. The header also holds a version, so that a
newer program can read old files and an older program can refuse new ones. Counts say how many records follow, and
sometimes offsets or sizes say where the parts lie.

:::example[A file of coin scores]
Take a format of our own with a 12-byte header and records of 16 bytes. The header holds three 32-bit numbers: the magic at
offset 0, the version at offset 4 and the count at offset 8. For three records the file has 12 + 3 × 16 = 60 bytes.

| Offset | Size | Part | Value in the example |
| --- | --- | --- | --- |
| 0 | 4 | magic | `43 4F 49 4E`, the letters `COIN` |
| 4 | 4 | version | `01 00 00 00`, which is 1 |
| 8 | 4 | count | `03 00 00 00`, which is 3 |
| 12 + 16 × i | 16 | record i | for i = 0, 1, 2 |

Record 2 starts at offset 12 + 16 × 2 = 44 and ends before offset 60, the end of the file. As a little-endian number, the
magic bytes read as 0x4E494F43.
:::

Try it: at which offset does record 0 start, and where does record 2 end?

:::answer
Record 0 starts at offset 12, right after the header. Record 2 starts at 44, takes 16 bytes and ends before offset 60.
:::

A reader follows the same steps for every format with a header:

1. Check that the file holds at least the header's size.
2. Check the magic number, and refuse the file if it differs.
3. Check the version, and refuse a version the reader does not know.
4. Check that the counts and sizes fit in the file (the next section).
5. Only then allocate memory and read the records.

Strata's asset packs, the files a game ships its assets in, follow this shape. A pack's header takes 64 bytes and starts
with the magic `STPK` and the version. The reader refuses a version other than 1 or 2, checks a checksum of the header, and
refuses any flag it does not know. The next fence quotes the :term[struct]{id=struct} that describes the header.

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

1. **Lines 179–180:** the magic and the version come first, so every reader checks them before anything else.
2. **Lines 184–187:** the counts of the tables, which a reader must never trust (see the next section).
3. **Line 188:** `Reserved` holds nothing; the next member is 8 bytes wide and must start on a multiple of 8, so this
   member fills the gap by name.
4. **Line 194:** the compiler checks the size of the header, 64 bytes, at every build.

## A length read from a file cannot be trusted

A header holds counts and sizes that the file's author wrote. A truncated file, a file from a newer program and a file made
to attack your program can all hold counts that are wrong. A reader that allocates memory for a count without checking it
asks for 4 billion records of 16 bytes, and the program crashes or reads memory that is not the file.

The rule is to bound every length by what the file holds. A file of 60 bytes cannot hold 4 records of 16 bytes after a
12-byte header, whatever the header says: 12 + 4 × 16 = 76 is more than 60.

The check has a trap. The obvious test multiplies the count by the record size, and a 32-bit multiplication can wrap
around. With the count 0x10000001 and records of 16 bytes, the product is 0x100000010, which needs 33 bits. A 32-bit
variable keeps only 0x10, which is 16, so 12 + 16 = 28 looks smaller than 60, and the check passes. The safe form divides
the room that is left by the record size: the count fits when $count \le (size - 12) / 16$.

In that formula, $count$ is the number from the header, $size$ is the file's size in bytes, 12 is the header's size and 16
is the record size. Division of :term[unsigned integers]{id=unsigned-integer} drops the remainder, which is right: a part of a record is no record.
The sketch tries three counts on the 60-byte file, first with the naive test and then with the safe one.

```cpp sketch="basics-bytes-bounds.cpp"
// A header claims some records of 16 bytes after 12 header bytes; the file has 60 bytes.
#include <cstdint>
#include <cstdio>
#include <initializer_list>

bool CountFits(uint64_t fileSize, uint32_t count)
{
	return fileSize >= 12 && count <= (fileSize - 12) / 16;
}

int main()
{
	const uint64_t fileSize = 60; // 12 + 3 * 16
	for (const uint32_t count : { 3u, 4u, 0x10000001u })
	{
		const uint32_t naiveEnd = 12 + count * 16; // 32-bit arithmetic wraps around
		std::printf("count %u: naive end %u, naive check %s, bounded check %s\n", count, naiveEnd, naiveEnd <= fileSize ? "passes" : "fails", CountFits(fileSize, count) ? "passes" : "fails");
	}
}
```

```text output-of="basics-bytes-bounds.cpp"
count 3: naive end 60, naive check passes, bounded check passes
count 4: naive end 76, naive check fails, bounded check fails
count 268435457: naive end 28, naive check passes, bounded check fails
```

1. **Line 8:** the file must hold the header, and the count must be at most the whole records in the room after it; the
   64-bit size cannot wrap here.
2. **Line 16:** the naive end is computed in 32 bits, so the product `count * 16` wraps for the last count.
3. **Line 17:** the naive check accepts the last count, and the bounded check refuses it.

Strata's reader of arrays does the same. `BinaryReader::ReadArray` reads a count and a run of items, and it refuses the
data when the count is above a limit or above what the remaining bytes can hold. Search for the division on line 82: it
divides the remaining bytes by the item's size, and it never multiplies the count.

```cpp src="Strata/src/Strata/Core/BinaryStream.h#L78-L90"
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

1. **Line 81:** the count is read as a 64-bit number, so a 32-bit wrap cannot happen on the way.
2. **Line 82:** three checks in one line: the reader is still valid, the count is within the caller's limit, and the count
   fits in the remaining bytes.
3. **Lines 83–86:** a failed check puts the reader in a failed state, so later reads return zero instead of stale data.
4. **Line 87:** only now does the reader allocate, because the count is known to fit in the file.

:::rule
Loaders must reject truncated and garbage bytes without crashing, because a game opens files that players supply.
[Robustness of loaders](../assets/robustness.md) shows the whole pipeline. The shader tool's `ParseSpirv` in
`CMake/StrataShaderTool/SpirvModule.cpp` applies the same care to a compiled shader. It refuses a missing magic number, a
file that ends inside its header, and an instruction whose word count is 0 or runs past the end.
:::

## A struct is laid out with alignment and padding

The same layout problem appears inside a program. A struct is a group of members stored one after another in memory, and
the graphics processing unit (GPU), files and other programs may read that memory byte by byte. To know what they read,
you need the offset of each member and the size of the whole.

**Alignment** is the rule that a value must start at an address that is a multiple of a number, usually the size of its
type. A `uint32_t` is aligned to 4, a `uint64_t` and a `double` to 8, and a `uint8_t` to 1. The operator `alignof` gives
the number for a type. Processors read aligned values fast, and some cannot read other values at all.

The compiler obeys the rule by inserting **padding**: unused bytes between members, or after the last one. A struct's own
alignment is the largest alignment of its members, and its size is a multiple of that, so that every element of an array
of the struct stays aligned. The operator `offsetof` gives the byte offset of a member.

:::example[Two orders of the same three members]
Take `uint8_t Kind`, `uint32_t Id` and `uint16_t Count`, in that order. `Kind` takes byte 0. `Id` needs a multiple of 4,
so three bytes of padding come first, and `Id` takes bytes 4 to 7. `Count` takes bytes 8 and 9.

The struct's alignment is 4, so 2 bytes of padding bring the size to 12. Only 7 of the 12 bytes hold data.

Now put the largest first: `Id` at 0 to 3, `Count` at 4 and 5, `Kind` at 6. The size 7 rounds up to 8. The same members
take 8 bytes instead of 12.
:::

```mermaid caption="The twelve bytes of the struct Loose in order: three bytes of padding sit before Id, and two at the end keep the size a multiple of 4." alt="A row of five blocks: Kind at byte 0, padding at bytes 1 to 3, Id at bytes 4 to 7, Count at bytes 8 and 9, and padding at bytes 10 and 11."
flowchart LR
	K["byte 0: Kind"] --> P1["bytes 1 to 3: padding"] --> I["bytes 4 to 7: Id"] --> C["bytes 8 and 9: Count"] --> P2["bytes 10 and 11: padding"]
```

The sketch below declares both orders, checks their sizes with `static_assert`, and prints the sizes and offsets that the
compiler chose. Compare them with the example.

```cpp sketch="basics-bytes-padding.cpp"
#include <cstddef>
#include <cstdint>
#include <cstdio>

struct Loose
{
	uint8_t Kind;
	uint32_t Id;
	uint16_t Count;
};
struct Tight
{
	uint32_t Id;
	uint16_t Count;
	uint8_t Kind;
};
static_assert(sizeof(Loose) == 12 && sizeof(Tight) == 8);

int main()
{
	std::printf("Loose: %zu bytes, Kind at %zu, Id at %zu, Count at %zu\n", sizeof(Loose), offsetof(Loose, Kind), offsetof(Loose, Id), offsetof(Loose, Count));
	std::printf("Tight: %zu bytes, Id at %zu, Count at %zu, Kind at %zu\n", sizeof(Tight), offsetof(Tight, Id), offsetof(Tight, Count), offsetof(Tight, Kind));
}
```

```text output-of="basics-bytes-padding.cpp"
Loose: 12 bytes, Kind at 0, Id at 4, Count at 8
Tight: 8 bytes, Id at 0, Count at 4, Kind at 6
```

1. **Lines 5–10:** `Loose` lists the small member first, so the compiler pads after `Kind` and after `Count`.
2. **Lines 11–16:** `Tight` lists the largest member first, and one padding byte remains at the end.
3. **Line 17:** `static_assert` stops the build when a size differs from the expected one, and it costs nothing at run time.

A struct is a **standard-layout type** when it obeys a few rules, among them no :term[virtual
functions]{id=virtual-function} and the same access for all members. A plain struct of numbers is one, and `offsetof` is allowed for it. A type for which `std::is_trivially_copyable` holds can be copied
byte by byte with `std::memcpy`, and `BinaryWriter::Write` asserts this for every type it writes.

Padding bytes hold whatever was in memory before. A struct written to a file with all its bytes puts that leftover data
in the file, and two runs write different files. Strata therefore chooses member orders that need no padding, and names
the padding it cannot avoid, as `Reserved` does in the pack header. The cooked texture header in
`Strata/src/Strata/Renderer/CookedTexture.cpp` is 40 bytes: seven 32-bit numbers, two 1-byte members and a 2-byte member
that fill one 4-byte slot, and a 64-bit offset on a multiple of 8.

:::why
The graphics card reads the same bytes as the C++ code, so both sides must agree on every offset. The structs in
`Strata/src/Strata/Renderer/SceneRenderData.h` have sizes in whole steps of 16 bytes and carry a `static_assert` on their size.
For example, `InstanceData` is a 48-byte transform and four 32-bit numbers, which makes 64 bytes. The cost is that you must
keep each C++ struct and its shader twin in step by hand: a member added on one side shifts every field after it.
:::

Try it: what are the size and the offsets of `struct Sample { uint8_t A; uint8_t B; uint32_t C; };`?

:::answer
`A` is at 0, `B` at 1, two bytes of padding follow, and `C` is at 4. The size is 8, and the order needs no change.
:::

## An image is bytes in rows

An image is a grid of pixels. In an 8-bit image with the channels red, green, blue and alpha, each pixel takes four bytes,
one per channel. The pixels are stored row by row, the top row first, and each row from left to right.

So the pixel at column $x$ and row $y$ in an image of width $w$ starts at the offset $(y \times w + x) \times 4$. Here $w$
is the width in pixels, 4 is the bytes per pixel, and $y \times w$ counts the pixels of all rows above. The whole image has
$w \times h \times 4$ bytes, with $h$ as the height in pixels.

Check the formula at the limits. The first pixel, x = 0 and y = 0, gives 0. The last pixel, x = w - 1 and y = h - 1, gives
$(h \times w - 1) \times 4$, which is 4 bytes before the end.

Real formats add two details. Some store extra bytes at the end of each row, so that a row starts on a multiple of a size.
Then the offset is $y \times r + x \times 4$, where $r$ is the length of a row in bytes. Compressed formats store blocks,
not single pixels, so the engine takes the size of a texture level from `GetMipByteSize`, never from the pixel count. Strata
also starts each level of a cooked texture at a multiple of 16 bytes (`c_CookedTextureAlignment`), which is alignment
applied to a file.

## Text is numbers too

A computer stores text as numbers, so it needs a table that says which number is which letter. A **text character** is one
unit of written text that a reader sees: a letter, a digit, a mark or a symbol.

A **text encoding**, also called a character encoding, is the rule that turns text into bytes and back.

The oldest table in common use has the long name American Standard Code for Information Interchange (ASCII). **ASCII** is a
table of 128 characters numbered 0 to 127: the English letters, the digits, marks and some control codes such as the line break. The letter A is 65
(0x41), and the letter a is 97 (0x61). ASCII fits into 7 bits, so each character takes one byte with the top bit 0.

## Unicode gives every character a number

Other languages need far more characters, so every region once made its own table, and a file written with one table looked
like garbage under another. **Unicode** is the single list that solves this: a numbered list of the characters of almost
every writing system, with many symbols. It does not say how to store the numbers; an encoding does.

A number of that list is a **code point**. It is written with U+ and at least four hex digits: A is U+0041, the letter ü is
U+00FC, the euro sign € is U+20AC, and a smiling face is U+1F600. The values go up to `U+10FFFF`. The first 128 code points
are the ASCII table, so ASCII text is also Unicode text.

A warning about the word "character": one thing a reader sees can be several code points, because a letter and the accent
mark after it make one visible letter. Strata counts code points. That is enough for the limits and cuts of the engine, and
it is not what a reader sees in every language.

## UTF-8 stores a code point in one to four bytes

**UTF-8** is the encoding that stores each code point in one to four bytes. The small code points take few bytes, and the
first byte of a longer one says how many bytes follow. The table shows the four patterns, where each x is a bit of the code
point.

| Code points | Bytes | Pattern of the bytes |
| --- | --- | --- |
| `U+0000 to U+007F` | 1 | `0xxxxxxx` |
| `U+0080 to U+07FF` | 2 | `110xxxxx 10xxxxxx` |
| `U+0800 to U+FFFF` | 3 | `1110xxxx 10xxxxxx 10xxxxxx` |
| `U+10000 to U+10FFFF` | 4 | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` |

Every byte of a sequence after the first is a **UTF-8 continuation byte**: a byte of the form `10xxxxxx`, with six bits of
payload. A byte that starts with 0 is a complete ASCII character, so ASCII text is also valid UTF-8, byte for byte.

:::example[Encode ü and the euro sign]
The letter ü is U+00FC, which is 252, or 1111 1100 in eight bits. It lies in the two-byte range, whose pattern has 11
payload bits, so write it as 00011 111100. The first byte is `110` and the top five bits: 110 00011, which is `C3`. The
second byte is `10` and the low six bits: 10 111100, which is `BC`. So ü is `C3 BC`.

The euro sign U+20AC is 0010 0000 1010 1100 in 16 bits. It needs the three-byte pattern with 16 payload bits: split the
bits into 0010, 000010 and 101100. The bytes are 1110 0010 = `E2`, 10 000010 = `82` and 10 101100 = `AC`. So € is
`E2 82 AC`.
:::

Try it: encode the code point U+00E9, the letter é.

:::answer
U+00E9 is 1110 1001 in binary. In the two-byte pattern the payload is 00011 101001, so the bytes are 110 00011 = `C3` and
10 101001 = `A9`.
:::

The design has two useful properties. A continuation byte is never mistaken for the start of a character, so you find the
start of the character around any byte by moving backward while the byte is a continuation byte. And counting characters
needs no table: count the bytes that are not continuation bytes.

The size of a text in bytes and its length in code points differ as soon as the text holds a non-ASCII letter. The text
`Münze` has 5 code points and 6 bytes, because ü takes two. The function `size()` of a `std::string` counts bytes. The sketch
counts code points and then cuts the text two bytes from the start, which falls in the middle of ü. In its text,
`\xC3` writes the single byte 0xC3.

```cpp sketch="basics-bytes-utf8.cpp"
#include <cstdio>
#include <string>

bool IsContinuation(char byte)
{
	return (static_cast<unsigned char>(byte) & 0xC0) == 0x80;
}

int main()
{
	const std::string name = "M\xC3\xBCnze"; // "Münze"
	size_t codePoints = 0;
	for (const char byte : name)
	{
		if (!IsContinuation(byte))
			codePoints++;
	}
	std::printf("%zu bytes, %zu code points\n", name.size(), codePoints);
	size_t cut = 2; // Keep two bytes: the second is half of the u with umlaut
	while (cut > 0 && IsContinuation(name[cut]))
		cut--;
	std::printf("the cut moves back to byte %zu and keeps \"%s\"\n", cut, name.substr(0, cut).c_str());
}
```

```text output-of="basics-bytes-utf8.cpp"
6 bytes, 5 code points
the cut moves back to byte 1 and keeps "M"
```

1. **Lines 13–17:** each byte that is not a continuation byte starts a code point, so counting them counts code points.
2. **Lines 19–21:** the cut position 2 holds a continuation byte, so the loop moves back until the byte at the cut starts a
   character, and the kept text ends before it.

A cut inside a character leaves half of it, which is not valid UTF-8. A program that reads it shows a replacement symbol or
fails. The standard replacement is `U+FFFD`, the code point for bytes that are not valid UTF-8, stored as `EF BF BD`.
Strata uses it for typed keyboard text, for messages that go into logs and JSON, and for text that the remote command server
receives.

When Strata must shorten text, it cuts at a boundary. The next quote limits the name of a save file to 64 bytes, and it
moves the cut back so that it never splits a character.

```cpp src="Strata/src/Strata/Core/SaveFiles.cpp#L158-L166"
if (name.size() > c_MaxNameLength)
{
	// Cut before the character that would not fit whole: continuation bytes are 10xxxxxx.
	size_t length = c_MaxNameLength;
	while (length > 0 && (static_cast<unsigned char>(name[length]) & 0xC0) == 0x80)
		length--;
	name.resize(length);
	name.erase(name.find_last_not_of(" .") + 1);
}
```

The loop on lines 162 and 163 is the loop of the sketch. The editor does the same when it shortens a long name with an
ellipsis: `UI::ElideEnd` in `StrataEditor/src/UI/Widgets.cpp` cuts only at a character boundary, so a name never shows half
a letter. A game's text field counts its characters by skipping continuation bytes too (`CountCharacters` in
`Strata/src/Strata/GameUI/GameUISystem.cpp`).

:::why
Strata keeps all text in `std::string` as UTF-8, and the script interface passes strings as a pointer and a size in UTF-8.
One encoding inside the program means no conversion in the middle, and ASCII code keeps working. The cost is that `size()`
is not the number of characters, so every limit must say whether it counts bytes or characters, and every cut must respect
boundaries.
:::

## UTF-16 and code pages are the other encodings you meet

**UTF-16** is the encoding that stores a code point in one or two units of 16 bits. A code point up to `U+FFFF` takes one
unit, and a larger one takes two units, a surrogate pair. For example, U+1F600 becomes the units `D83D` and `DE00`. A unit is
two bytes, so UTF-16 also has a byte order, and Windows uses little-endian.

Windows uses UTF-16 for its "wide" functions, which take `wchar_t` text. Strata converts at that boundary and nowhere else:
`Utf8ToWide` and `WideToUtf8` in `Strata/src/Platform/Windows/WindowsUtils.h`, and `FileSystem::FromUTF8` and
`FileSystem::ToUTF8` for :term[file paths]{id=path}. [Files in Strata](../core/files.md) shows where the conversion belongs, and why a path
built from a narrow string breaks on Windows.

A **code page** is an older encoding that stores one character in one byte. The byte values 0 to 127 are ASCII, and the
values 128 to 255 hold the letters of one region, which differ from page to page. The byte `FC` is ü in the Western European
page and a Russian letter in the one for Russian. Windows still uses a code page for its "narrow" functions, so UTF-8 bytes sent
to them come out as letters of the wrong region.

## Common mistakes

- **A length from a file used as it is.** Symptom: a crash or a huge allocation on a damaged file. Fix: bound every count
  by the bytes that remain, and divide the room by the record size instead of multiplying the count.
- **A multiplication that wraps.** Symptom: a size check that a wrong count passes. Fix: use 64-bit numbers for sizes, or
  divide.
- **A struct written to a file as it is.** Symptom: files that differ between runs or compilers, and fields that shift
  after a member is added. Fix: order the members to need no padding, name the rest, and check the size with
  `static_assert`.
- **Byte order forgotten.** Symptom: a number that reads as 16,777,216 when the file holds 1. Fix: write down the order of
  the format, and read each number in that order.
- **UTF-8 cut at a byte, or `size()` taken for the number of characters.** Symptom: a replacement symbol at the cut, or a
  name limit that allows fewer letters in other languages. Fix: move the cut back while the byte there is a continuation
  byte, and count code points when the limit means characters.
- **Logging a byte.** Symptom: a `uint8_t` of 65 appears as the letter A, and 200 as an invalid byte, because `Log::Info`
  writes each value with `<<`, which prints a byte as a character. Fix: log `int(value)`.

## Summary

- A little-endian format stores the lowest byte first and a big-endian format the highest. 300 is `2C 01 00 00` in
  little-endian, and reading it back shifts each byte into its place.
- An offset counts the bytes before a byte, from 0. A header's fields, a record at 12 + 16 × i and a pixel at
  (y × w + x) × 4 all follow from offsets and sizes.
- A count from a file is bounded by the file's size before anything is allocated: compare it with the room left divided by
  the record size, never with a product that can wrap.
- The compiler pads a struct so that each member is aligned. `sizeof` and `offsetof` show the layout, a good order of the
  members cuts the padding, and `static_assert` keeps a layout from changing.
- UTF-8 stores a code point in one to four bytes, and every byte after the first has the form `10xxxxxx`. Counting the bytes
  that are not continuation bytes counts code points, and a cut must not split a character.

## Check yourself

1. The bytes `10 27 00 00` are a little-endian 32-bit number. What is it?

   - A. 0x10270000
   - B. 10,000
   - C. 4,135
   - D. 16

   :::answer{tests="byte-order"}
   B. Byte 1 is `27` and byte 0 is `10`, so the number is 0x27 × 256 + 0x10 = 39 × 256 + 16 = 10,000. Answer A reads all
   four bytes as big-endian, C reads two bytes that way, and D reads only the first byte.
   :::

2. A file has a 20-byte header and records of 12 bytes, and its size is 140 bytes. At which offset does record 4 start, and
   how many records can the file hold?

   :::answer{tests="offsets"}
   Record 4 starts at 20 + 4 × 12 = 68. The room after the header is 120 bytes, which holds 120 / 12 = 10 records.
   :::

3. The header of a 100-byte file claims 10 records of 12 bytes after an 8-byte header. Which check refuses it?

   - A. `8 + count * 12 > 100`, in 32-bit arithmetic
   - B. `count > (100 - 8) / 12`
   - C. `count > 100`
   - D. None: 10 records is a small number

   :::answer{tests="untrusted-lengths"}
   B. The room is 100 - 8 = 92 bytes, which holds 7 whole records, and 10 is more. Answer C accepts 10 records and reads
   past the end. Answer A works for this count, but a 32-bit product can wrap for a large count.
   :::

4. Predict `sizeof` and the offset of `Value` for `struct Pair { uint8_t Flag; double Value; };`. Does putting `Value` first
   make the struct smaller?

   :::answer{tests="struct-layout"}
   `Flag` is at 0, seven bytes of padding follow, and `Value` is at 8, so the size is 16. With `Value` first, the size is
   still 16, because it must be a multiple of 8; the padding only moves to the end.
   :::

5. The UTF-8 bytes `E2 82 AC 41` hold how many code points? What happens if you keep only the first two bytes?

   :::answer{tests="utf-8"}
   The first three bytes are the euro sign, and `41` is the letter A, so the text holds 2 code points. Two bytes of the euro
   sign are an incomplete sequence, which valid UTF-8 never holds, and a reader shows `U+FFFD` for them.
   :::

## Practice

1. **Basic.** Write the number 0x0A0B0C0D as four bytes in little-endian order, then write the number that the bytes
   `00 00 01 00` give when read as little-endian.

   :::answer[Worked solution]{tests="byte-order"}
   The lowest byte goes first: `0D 0C 0B 0A`. In `00 00 01 00` the 1 sits in byte 2, which is worth 256 × 256, so the number
   is 65,536 (0x00010000).
   :::

2. **Basic.** Compute the size of `struct Item { uint16_t A; double B; uint8_t C; };` and the offset of each member. Then
   change the order of the members to make the struct smaller.

   :::answer[Worked solution]{tests="struct-layout"}
   `A` is at 0, then six bytes of padding, `B` at 8 and `C` at 16, and seven bytes of padding end the struct: the size is 24.
   With the order `B`, `A`, `C`, the offsets are 0, 8 and 10, and the size is 16.
   :::

3. **Medium.** A file has a 32-byte header and records of 40 bytes. The file has 1,000 bytes. Write the condition that
   accepts a count, and give the largest count it accepts.

   :::answer[Worked solution]{tests="untrusted-lengths offsets"}
   The file must hold the header, and the room after it is 1,000 - 32 = 968 bytes. The condition is
   `count <= (fileSize - 32) / 40`. The largest count is 968 / 40 = 24, because 24 × 40 = 960 and 25 × 40 = 1,000 is too much.
   :::

4. **Medium.** Encode the code point U+1F600 in UTF-8 by hand, and write its UTF-16 units.

   :::answer[Worked solution]{tests="utf-8"}
   U+1F600 is 0 0001 1111 0110 0000 0000 in 21 bits. The four-byte pattern splits it into 000, 011111, 011000 and 000000,
   which gives `F0 9F 98 80`. For UTF-16, subtract 0x10000 to get 0xF600. The top ten bits give 0xD800 + 0x3D = `D83D`, and
   the low ten bits give 0xDC00 + 0x200 = `DE00`.
   :::

5. **Hard.** Write a program that turns a valid UTF-8 text into code points and prints each one in the form `U+XXXX` with its
   length in bytes. Run it on `Münze`, a space, the euro sign, a space and the smiling face.

   :::answer[Worked solution]{tests="utf-8" solution="sketches/basics-bytes-decode.cpp"}
   The lead byte gives the length, and each continuation byte adds six bits. The program trusts its input to be valid;
   Strata's own decoders check every byte and replace the invalid ones with `U+FFFD`.

   ```cpp sketch="basics-bytes-decode.cpp"
   // Decodes valid UTF-8 into code points: the lead byte gives the length, each continuation byte six bits.
   #include <cstdint>
   #include <cstdio>
   #include <string>

   int main()
   {
   	const std::string text = "M\xC3\xBCnze \xE2\x82\xAC \xF0\x9F\x98\x80";
   	for (size_t index = 0; index < text.size();)
   	{
   		const uint8_t lead = static_cast<uint8_t>(text[index]);
   		const size_t length = lead < 0x80 ? 1 : lead < 0xE0 ? 2 : lead < 0xF0 ? 3 : 4;
   		uint32_t codePoint = lead;
   		if (length > 1)
   			codePoint &= 0x7Fu >> length; // Keep the lead byte's payload bits
   		for (size_t next = 1; next < length; next++)
   			codePoint = (codePoint << 6) | (static_cast<uint8_t>(text[index + next]) & 0x3Fu);
   		std::printf("length %zu: U+%04X\n", length, codePoint);
   		index += length;
   	}
   }
   ```

   ```text output-of="basics-bytes-decode.cpp"
   length 1: U+004D
   length 2: U+00FC
   length 1: U+006E
   length 1: U+007A
   length 1: U+0065
   length 1: U+0020
   length 3: U+20AC
   length 1: U+0020
   length 4: U+1F600
   ```

   1. **Line 12:** the lead byte gives the length: below 0x80 is one byte, below 0xE0 two, below 0xF0 three.
   2. **Lines 13–15:** a lead byte of length $n$ keeps $7 - n$ payload bits, and the mask `0x7F >> length` keeps them.
   3. **Lines 16–17:** each continuation byte shifts the result by 6 bits and adds its low six bits.
   :::

6. **Hard.** Optional, on Coin Run: your project from [Coin Run](../make/project-coin-run.md), or Checkpoint 4 at the end
   of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game), opened with **File ▸ Open
   Project...**. Its five coins appear only when the game starts, so drag one more coin, `Prefabs/Coin.stprefab`, from
   the Content Browser into the Scene view. Rename that coin to `Münze` in the Inspector. Add a script to it that logs
   the length of its name in bytes and in code points when the game starts.

   :::answer[Worked solution]{tests="utf-8" solution="sketches/basics-bytes-coin-name.cpp"}
   Make the script as the playground of [Programming 1](../basics/programming-1.md) does: choose **Scripts ▸ New
   Script...**, name the class `NameLength`, and replace the text of the new file with the one below. Build with
   **Ctrl+B** and select `Münze`. Its Script component already holds `Coin`: open **Add Script...** in that component
   and pick `NameLength`. Press **Play** and read the **Console**.

   The script reads the name with `GetEntity().GetName()`, which is UTF-8, and counts the bytes that are not
   continuation bytes.

   ```cpp pseudocode
   #include "StrataScript/StrataScript.h"

   using namespace Strata;

   // Logs the length of its entity's name in bytes and in code points.
   class NameLength : public Script
   {
   public:
   	void OnCreate() override
   	{
   		const std::string name = GetEntity().GetName();
   		int codePoints = 0;
   		for (const char byte : name)
   			codePoints += (static_cast<unsigned char>(byte) & 0xC0) != 0x80;
   		Log::Info("name bytes ", name.size(), ", code points ", codePoints);
   	}
   };

   ST_SCRIPT_CLASS(NameLength)
   {
   }
   ```

   1. **Lines 9–16:** `OnCreate` runs once when the game starts, so the line appears once, for the one coin.
   2. **Lines 19–21:** the registration tells the engine the class; it has no fields, so its braces stay empty. For
      `Münze` the **Console** shows `name bytes 6, code points 5`, and `Coins placed: 6` counts your extra coin.

   The sketch below makes the same count in a program on its own, with the name written out, so that you can run it.

   ```cpp sketch="basics-bytes-coin-name.cpp"
   // The Coin Run exercise on its own: the length of a name in bytes and in code points.
   #include <cstdio>
   #include <string>

   int main()
   {
   	const std::string name = "M\xC3\xBCnze"; // The coin's name as the engine stores it: UTF-8
   	size_t codePoints = 0;
   	for (const char byte : name)
   	{
   		if ((static_cast<unsigned char>(byte) & 0xC0) != 0x80) // Not a continuation byte
   			codePoints++;
   	}
   	std::printf("%zu bytes, %zu code points\n", name.size(), codePoints);
   }
   ```

   ```text output-of="basics-bytes-coin-name.cpp"
   6 bytes, 5 code points
   ```

   1. **Lines 9–13:** the loop counts each byte that is not a continuation byte.
   2. **Line 14:** `name.size()` counts bytes and `codePoints` counts characters, so a name with ü gives 6 and 5.
   :::

## Where the book uses it

- [Files in Strata](../core/files.md) uses UTF-8 and UTF-16 to explain the conversion at the Windows boundary.
- [Robustness of loaders](../assets/robustness.md) uses bounded lengths, magic numbers and versions to reject broken files.
- [Data formats](../basics/data-formats.md) uses bytes and byte order for :term[hashes]{id=hash}, checksums and binary encodings.
- [Generated code](../engineering/generated-code.md) uses the layout of a binary format to read compiled shaders.

## Further reading

- [learncpp.com, "Struct miscellany"](https://www.learncpp.com/cpp-tutorial/struct-miscellany/): sizes, padding and
  alignment of structs in C++; beginner.
- [cppreference, `offsetof`](https://en.cppreference.com/w/cpp/types/offsetof): the exact rules of the macro; intermediate.
- [The Unicode Consortium, "The Unicode Standard"](https://www.unicode.org/versions/latest/): the definition of code
  points and of UTF-8 and UTF-16; advanced.
- Joel Spolsky, "The Absolute Minimum Every Software Developer Absolutely, Positively Must Know About Unicode and
  Character Sets": a short introduction to encodings; beginner.
- Danny Cohen, "On Holy Wars and a Plea for Peace": the paper that named little-endian and big-endian; intermediate.
