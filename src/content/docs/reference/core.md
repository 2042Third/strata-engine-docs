---
id: reference/core
title: "Core utilities"
description: "The small helpers of the Core layer that engine code calls everywhere: what each header offers, and which page teaches the idea behind it."
kind: reference
size: M
tracks: []
needs: [basics/programming-3]
status: final
---

This page lists the small helpers of the `Core` layer that engine code calls in many places: identifiers, hashes, byte streams, text functions, sorting and memory helpers. You use it when you meet a name in code, such as `Base64::Decode` or `Prefetch`, and want to know what it does. Each table below belongs to one header of `Strata/src/Strata/Core/`. A row is one function, type or constant of that header, and the right column says what it does, using the header's own comments. The tables summarize the headers at the pin; a header's comment wins over this page if they ever differ.

Under each table stands one sentence that names the page that uses or teaches the helper. Where that sentence says that this page is the home, no other page explains the helper. A name with `::` is a function of a class (`Hash::Combine` is the function `Combine` of the class `Hash`). A function marked static belongs to the class itself and needs no object. A span is a view of values that another object holds, without a copy.

## The first include

Every engine `.cpp` file starts with `#include "stpch.h"`, then its own header. The file `Strata/src/stpch.h` is the **precompiled header** of the engine: one header that the compiler reads once and keeps for every :term[source file]{id=source-file}, which makes builds faster. It holds only the standard library, the vendor headers of EnTT and `nlohmann`, and the Core basics: `PlatformDetection.h`, `Base.h`, `Log.h`, `Assert.h` and `Profiling.h`. It never holds a header that changes often, because every engine object would rebuild with it. Headers still include what they use themselves: the build also works with precompiled headers switched off.

## Identifiers and hashes

The class `UUID` is a 64-bit number that names an entity or an asset. The :term[constructor]{id=constructor} without arguments draws a random number and never returns zero, because zero means "no identifier". The text form is 16 upper-case hexadecimal digits.

| Name | What it does |
| --- | --- |
| `UUID()` | Makes a new random, non-zero identifier. |
| `UUID(uint64_t)` | Wraps a number you already hold, for example one read from a file. |
| `operator uint64_t` | Reads the identifier as a plain 64-bit number. |
| `IsValid()` | True when the number is not zero. |
| `ToString()` | Writes the 16 hexadecimal digits. |
| `UUID::FromString(text)` | Reads those digits back; returns nothing when the text is not valid. |
| `UUID::Null()` | The reserved value zero. |
| `std::hash<UUID>` | Lets an identifier be a key of an unordered map or set. |

The page [Entities, components and the registry](../world/ecs.md) teaches identifiers as stable names of things.

The class `Hash` turns bytes into a number that stays the same on every platform. Its main function, `FNV1a`, is a fast hash of text or bytes; the header says it is suitable for identifiers saved to disk and is not cryptographic.

| Name | What it does |
| --- | --- |
| `Hash::FNVOffsetBasis`, `Hash::FNVPrime` | The two constants of the 64-bit `FNV1a` hash. |
| `Hash::FNV1a(text, seed)` | Hashes a string, at :term[compile time]{id=compile-time} when it can; the seed lets you chain. |
| `Hash::FNV1a(bytes, seed)` | The same for a span of bytes. |
| `Hash::Combine(seed, value)` | Mixes a second number into a first one, a stronger form of the combine step of the Boost libraries. |
| `Hash::CRC32C(bytes, previous)` | A cyclic redundancy check (CRC) that detects damaged data such as the blocks of an asset pack. It chains, and uses the processor's CRC instructions where they exist. |
| `Hash::CRC32CPortable(bytes, previous)` | The portable version alone; tests compare it with the fast one. |

The header gives a check value: the `CRC32C` of the nine characters "123456789" is `0xE3069283`. The page [Data formats](../basics/data-formats.md) teaches how Strata hashes and checks bytes.

The header `Crypto.h` holds the secure hash and the message code that protect the editor's automation connection.

| Name | What it does |
| --- | --- |
| `Sha256Digest` | An array of 32 bytes: the result of a hash. |
| `Sha256` | The secure hash function with a 256-bit result. Feed data with `Update`, then call `Finalize` for the digest; `Finalize` also resets the object. |
| `Sha256::Hash(data)` | Static: the digest of one piece of data. |
| `Crypto::HmacSha256(key, message)` | A hash-based message authentication code (HMAC) that proves the sender knows a shared secret. |
| `Crypto::ConstantTimeEquals(left, right)` | Compares without stopping at the first difference, so the time taken does not show how much of a secret matched. Inputs of different lengths are unequal. |
| `Crypto::ToHex(bytes)` | Writes bytes as lower-case hexadecimal. |

The page [Security of the automation server](../automation/security.md) uses these functions when a client first connects.

## Bytes and text

The class `Base64` writes binary data as text, for example to carry an image inside a JavaScript Object Notation (JSON) result. This page is the home of its facts. It uses the standard alphabet with `=` padding. Three bytes become four characters, so `GetEncodedSize` of 6 bytes is 8. The decoder is strict: every byte sequence has exactly one accepted text.

| Name | What it does |
| --- | --- |
| `Base64::Encode(data)` | Static: the text of a span of bytes. |
| `Base64::Decode(text)` | Static: the bytes, or nothing when the text has a character outside the alphabet (white space too), missing or misplaced padding, or non-zero bits in the padding. |
| `Base64::GetEncodedSize(size)` | The length of the text of `size` bytes: `(size + 2) / 3 * 4`. |

The editor's viewport capture command uses `Encode` for the picture it returns.

The classes `BinaryWriter` and `BinaryReader` save and load the cooked asset formats. Everything is little-endian: a number's lowest byte comes first, as on every supported platform. A reader never trusts a length that it reads from the data.

| Name | What it does |
| --- | --- |
| `BinaryWriter::Write(value)` | Appends the bytes of a value; only for types that can be copied as raw bytes. |
| `BinaryWriter::WriteArray(values)` | Appends a 64-bit count, then the values. |
| `BinaryWriter::WriteString(text)` | Appends a 32-bit length, then the characters. |
| `BinaryWriter::WriteBytes(data, size)` | Appends raw bytes; a size of zero does nothing. |
| `BinaryWriter::GetSize()`, `GetData()`, `TakeData()` | Read the size, view the buffer, or move the buffer out. |
| `BinaryReader(data)` | Reads from a span of bytes. |
| `BinaryReader::Read<T>()` | Reads one value; past the end it fails and returns a zeroed value. |
| `BinaryReader::ReadArray(values, maxCount)` | Reads an array that `WriteArray` wrote; `maxCount` (default 4,294,967,295) and the bytes left guard against a corrupt count. |
| `BinaryReader::ReadString(maxLength)` | Reads a string; the default limit is 1,048,576 characters. |
| `BinaryReader::ReadBytes(destination, size)` | Copies bytes, or zeroes the destination and fails. |
| `BinaryReader::ReadView(size)` | A view of the next bytes without copying; empty and failed when out of range. |
| `BinaryReader::Seek(position)` | Moves the position; a position past the end fails. |
| `BinaryReader::IsValid()`, `GetPosition()`, `GetRemaining()` | Tell whether all reads worked, where the reader stands and how many bytes are left. |

The failure is **sticky**: once a read fails, the reader stays failed and every later read returns zero, so you check `IsValid()` once after reading a whole structure. The page [Robust loading of untrusted data](../assets/robustness.md) teaches how loaders use this.

The class `JsonUtils` wraps the `nlohmann` library so that bad input gives an error, never a crash. The library throws on a wrong type, and when it writes text that is not valid UTF-8; engine code does not throw, so it calls these functions.

| Name | What it does |
| --- | --- |
| `JsonParseProgress` | A callback and an `Interval` (default 1,048,576 bytes): how a long read of a document reports how far it got. |
| `JsonUtils::Parse(text, error)` | Reads JSON text; returns nothing and fills the error text when the text is invalid. |
| `JsonUtils::Parse(text, progress, error)` | The same, calling the callback about every interval and once at the end. |
| `JsonUtils::Dump(json, indent, indentCharacter)` | Writes JSON as text; invalid UTF-8 becomes `U+FFFD`. An `indent` below zero gives one compact line. |
| `JsonUtils::AppendString(out, text)` | Appends one JSON string exactly as `Dump` would write it, without building a JSON value. |
| `JsonUtils::GetString`, `GetBool`, `GetInt`, `GetUInt`, `GetFloat` | Read a member; return the fallback when the key is missing or holds another type. |
| `JsonUtils::Find(object, key)` | A pointer to the member, or null. |

The header `JsonEvents.h` offers `ParseJsonEvents(text, handler, progress)`. The function runs the event reader of the `nlohmann` library: strict (one value and nothing after it) and without exceptions, calling your handler for each piece of the document. A handler that returns false stops the reading, and the function returns false. The scene document reader uses it: a scene of a million entities gives about a hundred million events. `JsonProgressInput` is the reader of characters that makes the progress reports cheap.

The page [Conventions](../core/conventions.md) teaches why engine code does not throw.

The functions of `StringUtils` are free functions in the :term[namespace]{id=namespace} `Strata::StringUtils`. This page is their home, and [Your first change](../core/first-change.md) adds one.

| Name | What it does |
| --- | --- |
| `StringUtils::ToLower(text)` | Lower-cases the letters of the American Standard Code for Information Interchange (ASCII); bytes outside ASCII are unchanged. |
| `StringUtils::EqualsIgnoreCase(a, b)` | Compares two texts, ignoring the case of ASCII letters. |
| `StringUtils::StartsWith(text, prefix)` | True when the text begins with the prefix. |
| `StringUtils::EndsWith(text, suffix)` | True when the text ends with the suffix. |
| `StringUtils::FormatThousands(value)` | Writes a count with commas: 12345 becomes "12,345". |
| `StringUtils::MakeValidUTF8(text)` | Replaces every invalid byte sequence with `U+FFFD`, so messages from other libraries are safe for logs, JSON and the interface. Valid text returns unchanged. |

## Sorting and allocation

The header `RadixSort.h` sorts keys faster than a comparison sort. The page [Batching](../draw/batching.md) teaches how the renderer uses it.

| Name | What it does |
| --- | --- |
| `SortItem` | A 64-bit key with a 32-bit value, 16 bytes in all. |
| `RadixSort(items, scratch)` | Stable sort by key, one byte per pass, least significant byte first. A byte equal in every key costs no pass. The scratch vector keeps its capacity between calls. |
| `SortIndices(values, items, scratch)` | Sorts 32-bit values ascending: short lists by comparison, sorted lists not at all, longer ones by `RadixSort`. |

The class `RangeAllocator` hands out ranges of units inside a buffer that you own, such as vertices or indices. It holds no memory itself. It takes the lowest fitting offset of the smallest size class that has a free range, and joins a freed range with its free neighbours. It is not thread-safe.

| Name | What it does |
| --- | --- |
| `RangeAllocator(capacity)` | Creates an allocator over the units from 0 up to the capacity. |
| `RangeAllocator::c_InvalidOffset` | The value returned when nothing fits. |
| `Allocate(size, alignment)` | The offset of `size` units, aligned to a power of two; the invalid offset when nothing fits, the size is zero or the alignment is not a power of two. |
| `Free(offset)` | Frees the allocation that starts there; false and no change when none does. |
| `Grow(capacity)` | Adds free units at the end; never shrinks. |
| `GetSize`, `GetCapacity`, `GetUsedUnits`, `GetFreeUnits`, `GetAllocationCount` | Read sizes and counts. |
| `GetLargestFree`, `GetFragmentation`, `GetScatteredFreeShare`, `GetHighWaterMark` | Measure how scattered the free space is, and where the highest allocation ends. |
| `PlanCompaction(maxUnits, movable)` | Moves allocations to lower offsets and returns the moves in the order to make them; each call moves at most `maxUnits` units, but its first move whatever its size. |
| `Validate()`, `GetFreeRanges()` | Check that the records are consistent, and list the free ranges (tests and statistics). |

The page [The geometry pool](../gpu/geometry-pool.md) teaches how the renderer uses it.

The class `AmortizedCheck` paces a check whose cost grows with the size of what it checks, such as the validation of a whole structure in Debug builds. Each call earns a budget of `elementsPerCall` elements, and the check is due once the budget covers the elements there are now. With a budget of 500, a structure of 10,000 elements is checked at every 20th call. The first call always checks.

| Name | What it does |
| --- | --- |
| `AmortizedCheck(elementsPerCall)` | Sets the budget per call; zero becomes one. |
| `IsDue(elements)` | True when to check now; true also starts the next budget. |
| `GetElementsPerCall()` | Reads the budget. |

The check counts calls, never time, and the call that checks still pays for the whole structure, so do not pace work that a frame deadline must bound. The scene and the render scene use it for their cache checks; no page teaches it beyond this one.

## Memory and copying

The function `Prefetch` is the helper of this section whose facts only this page holds.

| Name | What it does |
| --- | --- |
| `Prefetch(address)` | Asks the central processing unit (CPU) to start loading the cache line of that address, so that a read a little later does not wait for memory. |

The function is only a hint: it never faults and has no other effect, whatever the address (null, freed or not mapped). A cache line is the small block of memory, often 64 bytes, that the CPU loads at once. The script system uses `Prefetch` in its loop over script objects, each in a memory block of its own. The `Prefetch` function of the asset resolve cache is another function: it asks for an asset to load.

The function `CloneWithParallelMembers` copies an object member by member, and copies the members that hold large arrays side by side on the job system. This page is its home. The render scene uses it when it copies its large arrays.

| Name | What it does |
| --- | --- |
| `CloneWithParallelMembers(source, makeCopy, members...)` | Moves the listed members out of the source, makes the copy with `makeCopy` (the copy constructor), copies the large members in parallel, and moves them back. A member omitted from the list is still copied, only not in parallel. Nothing else may use the source meanwhile. |

Call it where the members and the copy constructor are accessible: inside the class's own :term[member functions]{id=member-function}. The page [Jobs](../core/jobs.md) teaches the job system, and [The render scene](../draw/render-scene.md) its use.

## Program start

The classes `CommandLine` and `CommandLineOptions` read the arguments that start a program. Options take the forms `--name value`, `--name=value` and `--flag`. The page [The editor program](../editor/program.md) lists the options of each program.

| Name | What it does |
| --- | --- |
| `CommandLine(argc, argv)` | Holds the UTF-8 arguments; the program name is at index 0. |
| `HasFlag(name)` | True when the flag is present. |
| `GetOption(name)` | The text after the option, or nothing. |
| `GetIntOption(name)` | The option as a whole number, or nothing. |
| `GetSizeOption(name)` | A size written width, the letter x, height, such as 1920x1080; each part is a whole number from 1 to `c_MaxSizeOption` (65,535); nothing when missing or invalid. |
| `CommandLineOption` | A table row: the `Name`, the `Value` placeholder (null for flags) and the `Description`. |
| `CommandLineOptions::FindUnknownArgument(commandLine, options)` | Says what is wrong: an argument the table lacks, a flag given a value, or an option without its value. |
| `CommandLineOptions::FormatUsage(program, options)` | Writes the usage text, one option per line. |
| `CommandLineOptions::c_UsageExitCode` | The exit code 3 of a command line the program does not understand. |

The header `EmbeddedFiles.h` holds data compiled into the engine. Its one function, `EmbeddedFiles::GetDefaultFont`, returns the bytes of the default text font. The generated header `Version.h` holds `ST_VERSION_MAJOR`, `ST_VERSION_MINOR`, `ST_VERSION_PATCH`, `ST_VERSION_STRING`, `c_EngineName`, `c_EngineVersion` and `c_EngineCommit`, the short hash of the commit that the build came from ("unknown" outside a git clone). The page [Generated code](../engineering/generated-code.md) teaches both.

## Base macros and pointer names

The header `Base.h` holds the basics that nearly every file uses. The page [Conventions](../core/conventions.md) teaches the ownership names and the assertions.

| Name | What it does |
| --- | --- |
| `Scope<T>`, `CreateScope<T>(args)` | The short name of `std::unique_ptr` and its maker: one owner. |
| `Ref<T>`, `CreateRef<T>(args)` | The short name of `std::shared_ptr` and its maker: shared ownership. |
| `WeakRef<T>` | The short name of `std::weak_ptr`: a reference that does not keep the object alive. |
| `ST_ENABLE_ASSERTS` | Defined in every build except Dist. |
| `ST_DEBUGBREAK()` | Stops in the debugger: `__debugbreak` on Windows, a trap elsewhere. |
| `ST_EXPAND_MACRO(x)`, `ST_STRINGIFY_MACRO(x)` | Help macros that expand or quote a macro argument. |
| `ST_BIT(x)` | The number with only bit `x` set. |
| `ST_BIND_EVENT_FN(fn)` | A function that calls the member function `fn` of the current object. |
| `ST_DEFINE_ENUM_FLAG_OPERATORS(EnumType)` | Defines the bitwise operators and `HasFlag` for an `enum class` used as a set of flags. |

## Where it lives in Strata

- `Strata/src/Strata/Core/`: the headers that the tables above read, among them `UUID.h`, `Hash.h`, `Crypto.h`, `Base64.h`, `BinaryStream.h`, `JsonUtils.h`, `JsonEvents.h`, `StringUtils.h`, `RadixSort.h`, `RangeAllocator.h`, `AmortizedCheck.h`, `Prefetch.h`, `ParallelClone.h`, `CommandLine.h`, `CommandLineOptions.h`, `EmbeddedFiles.h`, `Version.h.in` and `Base.h`.
- `Strata/src/stpch.h`: the precompiled header that every engine source file includes first.
- `CMake/StrataEmbeddedFiles.cmake` and `CMake/StrataVersionCommit.cmake`: the build steps that produce the embedded font and the commit hash.
- `StrataTests/src/Core/`: the unit tests of most of these helpers (`CoreTests.cpp` and one file per helper, such as `Base64Tests.cpp`); `StrataTests/src/Asset/AssetPackTests.cpp` also tests `CRC32C`.
