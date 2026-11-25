# Brief: `basics/bytes`

| Field | Value |
| --- | --- |
| Title | Bytes in files and memory: layouts, byte order and text encodings |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/numbers`, `basics/tools`, `basics/cpp-generic` |
| From | new; foundation concept 23; assets concept 19; build-test excerpt 13; files and numbers as bytes, byte order, binary layouts and lengths that cannot be trusted, structs as bytes (`sizeof`, alignment, `offsetof`, `static_assert`), images as bytes, text encodings (Unicode, UTF-8, UTF-16 and code pages); JSON, Base64, hashes and UUIDs are `basics/data-formats`' |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/bytes` — Bytes in files and memory: layouts, byte order and text encodings

**Covers.** Files as bytes: a file format as the agreed layout of a file's bytes, text files and binary files, and the
sizes of files and buffers in bytes, KiB and MiB (the prefixes are `basics/numbers`' powers of two). Numbers as bytes:
the sizes of types, byte order (little-endian and big-endian), and a 32-bit number read from four bytes. Binary layouts:
offsets, a header with a magic number and a version, sizes and counts, and lengths read from a file that cannot be
trusted (bounded by the file's size before anything is allocated). Structs as bytes: `sizeof`, alignment and padding,
`offsetof`, standard-layout types, and a layout checked with `static_assert` (sizes, alignment and `static_assert` as
the GPU's data and the packs need them). Images as bytes: pixels, channels and rows. Text: a text character, Unicode
and its code points, ASCII. UTF-8: one to four bytes per code point, continuation bytes of the form `10xxxxxx`, why
cutting text by bytes can split a character (eliding text by characters), U+FFFD for bytes that are not valid UTF-8,
and counting characters against counting bytes. UTF-16 and code pages: Windows' wide text and its older narrow
encodings (Strata's rule at the boundary is `core/files`'). The Test out box asks for the four bytes of a 32-bit number
in little-endian order, the size of a struct with padding, and the number of bytes a character takes in UTF-8. The
Practice reads and writes bytes by hand and ends with the optional item on the reader's Coin Run: rename a coin with a
letter outside ASCII (`Münze`) and log its name's length in bytes and in code points.

**Leaves out.**

- Binary, hexadecimal and the sizes of integer types → `basics/numbers`
- JSON, Base64, hashes, checksums and UUIDs → `basics/data-formats`
- Text and paths on Windows, and Strata's conversions → `core/files`
- Corrupt and hostile files in the asset pipeline → `assets/robustness`
- Text on screen: shaping and fonts → `gpu/text`, `ui/text`
- A binary format read defensively in Strata's tools → `engineering/generated-code`

**Fit.** `fits`: about 4,300 words against L (5,000). Eight ideas from zero at B0's length, with a header's layout, a
padded struct and UTF-8's bytes drawn (about 3,200), and the primer's fixed parts with the Test out box, the Practice
and the Coin Run item (about 1,100); binary layouts and structs as bytes take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:175` | concept | home | Files as bytes, file formats, text and binary files; sizes in bytes, KiB and MiB. General knowledge. |
| `new:176` | concept | home | Numbers as bytes: sizes of types, byte order, a 32-bit number read from four bytes. General knowledge. |
| `new:177` | concept | home | Binary layouts: offsets, a header with a magic number and a version, counts, lengths that cannot be trusted. General knowledge. |
| `new:178` | concept | home | Structs as bytes: `sizeof`, alignment, padding, `offsetof`, standard layout, a layout checked with `static_assert`. General knowledge. |
| `new:179` | concept | home | Images as bytes: pixels, channels and rows. General knowledge. |
| `new:180` | concept | home | Text characters, Unicode, code points and ASCII. General knowledge. |
| `new:181` | concept | home | UTF-8: one to four bytes, continuation bytes, cutting by bytes, U+FFFD, counting characters. General knowledge. |
| `new:182` | concept | home | UTF-16 and code pages. General knowledge. |
| `new:208` | hands-on | home | Optional practice on Coin Run: a coin renamed `Münze` in the Inspector, and a script that logs the name's length in bytes and in code points, counted by skipping continuation bytes. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:43-44`, `StrataScriptCore/Include/StrataScript/ScriptABI.h:14` |
| `audio-input:666` | term | home | UTF-8 |
| `audio-input:667` | term | home | Code point; U+FFFD |
| `gameui:678` | term | home | Code point; UTF-8 continuation byte |
| `foundation:627` | term | home | UTF-8, UTF-16 and code page |
| `foundation:317` | concept | link | Text and paths in Strata, linked to `core/files` |
| `assets:351` | concept | link | Untrusted input and corruption, linked to `assets/robustness` |
| `build-test:390` | code | link | `ParseSpirv`, a binary format read defensively, linked to `engineering/generated-code` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Binary, hexadecimal, integer types and their sizes, shifts | `basics/numbers` | must |
| Files, folders and a code editor | `basics/tools` | must |
| Structs and their members | `basics/programming-2` | must |
| `static_assert` and `sizeof` in code | `basics/cpp-generic` | must |
| Renaming an entity, for the Coin Run item | `make/scenes-entities` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `ascii` | ASCII | - |
| `code-point` | code point | - |
| `endianness` | endianness | byte order |
| `file-format` | file format | - |
| `serialization` | serialization | - |
| `text-character` | text character | - |
| `text-encoding` | text encoding | character encoding |
| `unicode` | Unicode | - |
| `utf-8` | UTF-8 | UTF-16, code page |
| `utf-8-continuation-byte` | UTF-8 continuation byte | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-20 | should | order | `basics/cpp-memory` (`new:129`, `new:217`) | The Practice writes an arena that hands out memory in a row. To put objects into it, the reader needs alignment (each object at an address that is a multiple of its `alignof`) and a way to construct an object in raw memory (placement `new` or `std::construct_at`, and the destructor called by hand). Alignment is taught on `basics/bytes`, five pages later on tracks B and E, and placement `new` and `std::construct_at` are on no page. Without them the arena is undefined behavior, on the page that teaches undefined behavior. | The allocator section teaches alignment in the measure the arena needs (round the offset up to `alignof(T)` with the round-up rule of `basics/numbers`) and `std::construct_at` with `std::destroy_at`, and links `basics/bytes` for layouts and padding (about 150 words). | `allocation/basics-a.md:751-752`, `:790`, `:1092-1093`, `:1123`; `tracks.md:187-192`; a search of `allocation/*.md` for "placement new", "construct_at" and "alignof" finds nothing |
| critic-basics-a-21 | should | shape | `basics/computer`, `basics/tools`, `basics/git`, `basics/data-structures`, `basics/trees-graphs`, `basics/bytes`, `basics/data-formats` | A primer has a "Common mistakes" section: each mistake, its symptom and its fix. These seven pages list none: no Covers, row or Fit line of theirs names a mistake, while the other eleven pages of the unit do. | Each page's Covers names three or four mistakes with their symptoms (about 250 words a page). For example: tools, a path with a space not quoted, a program run from the wrong folder, Ctrl+C taken for copy; git, a commit without `git add`, conflict markers left in a file, build output committed (the editor's `.gitignore` keeps `.strata/` out); data-structures, an index kept across a swap-remove, a hash map's order relied on; trees-graphs, a recursive walk of a deep tree that overflows the stack, a graph walk without a visited set; bytes, a length read from a file and used unbounded, UTF-8 cut by bytes; data-formats, a float written with too few digits, `std::hash` stored in a file, a trailing comma in JSON; computer, memory taken for storage, more cores taken for a faster single task. | `style.md:476`; `allocation/basics-a.md:5-46`, `:82-120`, `:459-485`, `:607-639`, `:677-701`, `:1088-1114`, `:1152-1186`; `Strata/src/Strata/Project/Project.cpp:198-199` |
| critic-basics-a-22 | should | missing-item | `basics/bytes` (`new:176`, `new:208`); `basics/numbers` (`new:85`) | `Log::Info` writes each value with `<<`, so a `uint8_t` or an `int8_t` prints as a character: a byte of 65 logs "A", and 200 logs a byte that is no valid UTF-8. `basics/bytes`' practice reads and writes bytes and logs them, and `basics/numbers` teaches `int8_t` and `uint8_t` with their overflow. | Both pages' Common mistakes hold it, with the fix (log `int(value)`, or `+value`) (about 60 words each). | `StrataScriptCore/Include/StrataScript/Log.h:21-25`; `allocation/basics-a.md:517`, `:1089-1090`, `:1100` |
