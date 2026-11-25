# Brief: `basics/data-formats`

| Field | Value |
| --- | --- |
| Title | JSON, Base64, hashes and UUIDs |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/bytes` |
| From | new by split of `basics/bytes`, which could not hold both lessons at a primer's size; foundation concept 26; numbers written as text and read back exactly, JSON (objects, arrays, strings, numbers, a format header with a version, reading text into tokens by hand, strict against lenient readers), Base64, stable hashes (FNV-1a in `Hash.h`) against `std::hash`, checksums (CRC-32C), cryptographic hashes (SHA-256; HMAC is `automation/security`'), UUIDs |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/data-formats` — JSON, Base64, hashes and UUIDs

**Covers.** The page goes on from `basics/bytes` to the formats written in text and to the numbers made from data to
check it or to name it. Numbers written as text and read back, with enough digits to give the same float again. JSON:
objects, arrays, strings, numbers, `true`, `false` and `null`, quotes and commas; comparing two JSON values; a format
header with a version, read on the Tetris sample's project file (whose start scene is a handle of 16 hexadecimal
digits); reading text by hand, a character at a time into tokens, as the start of a parser, and why a strict reader
refuses what a lenient one forgives. Regular expressions, in about 350 words, because pages of track E quote patterns
that no earlier page teaches (`critique/rulings-7.md`, R31): literal characters, `.`, `*`, `+`, `?`, classes such as
`[a-z]`, the anchors `^` and `$`, groups and escaping; a glob such as `*.cpp` turned into a pattern; and why JSON needs
a parser and not a pattern. Base64: three bytes written as four safe characters. Hashes: the hash function of
`basics/data-structures` recalled, a stable hash against `std::hash`, FNV-1a in Strata's own ten lines (`Hash.h`), and
in one sentence `Hash::Combine`, which mixes one hash into another. Checksums: CRC-32C catches damaged data; in one
sentence, Strata computes it with the processor's CRC instructions where it has them and gets the same result
everywhere; a checksum is no protection against someone who changes the data on purpose. Cryptographic hashes: SHA-256,
why it cannot be undone or forged, a digest written in hexadecimal, and a keyed hash and a comparison in constant time
named with a link to `automation/security`, which teaches HMAC. UUIDs: random identifiers so large that two never meet;
the standard's UUID has 128 bits written as 32 hexadecimal digits, while Strata's has 64 bits written as 16 (`world/ecs`
uses it). The Test out box asks the reader to find the error in a broken JSON text, to say what a checksum catches and
what it does not, and to tell how many hexadecimal digits Strata's UUID takes. The Practice reads, tokenizes and hashes
small texts and ends with the optional item on the reader's Coin Run: open its `.stproj` in the code editor without
changing it, and find its format header, its version and the handle of its start scene.

**Leaves out.**

- Byte order, binary layouts and UTF-8 → `basics/bytes`
- Hash maps, buckets and collisions → `basics/data-structures`
- Radix sort and the offset allocator of the utilities → `basics/trees-graphs`, `gpu/geometry-pool`
- Scene documents, streams and their formats → `world/serialization`
- Strata's UUID as the identity of entities and assets → `world/ecs`, `assets/handles-meta`
- HMAC, the challenge and the constant-time compare → `automation/security`
- JSON as a game maker writes it in command scripts → `make/automated-playtests`

**Fit.** `fits`: about 4,700 words against L (5,000). Nine ideas from zero at B0's length, the hash function recalled
rather than taught and `Hash::Combine` and the CRC instructions in a sentence each (about 3,100), two excerpts with what
to look for, the Tetris project file and FNV-1a in `Hash.h` (about 500), and the primer's fixed parts with the Test out
box, the Practice and the Coin Run item (about 1,100); JSON with reading text into tokens takes the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:183` | concept | home | Numbers written as text and read back exactly. General knowledge. |
| `new:184` | concept | home | JSON: objects, arrays, strings, numbers, `true`, `false`, `null`; comparing values; a format header and versions. General knowledge. |
| `new:185` | code | home | `Samples/Tetris/Tetris.stproj:1-22`: a JSON document with a format header (`"Format": "Project"`, `"Version": 3`) and handles as 16 hexadecimal digits |
| `new:186` | concept | home | Reading text by hand into tokens, the start of a parser; strict and lenient readers. General knowledge. |
| `new:209` | concept | home | Regular expressions in about 350 words: literal characters, `.`, `*`, `+`, `?`, classes such as `[a-z]`, the anchors, groups and escaping; a glob turned into a pattern; why JSON needs a parser and not a pattern. `editor-ui/ui-testing`, `engineering/cmake` and `engineering/generated-code` use it (`critique/rulings-7.md`, R31). General knowledge. |
| `new:187` | concept | home | Base64: three bytes as four characters. General knowledge. |
| `new:188` | concept | use | Hash functions as `basics/data-structures` teaches them (its home row `new:108`), recalled before a stable hash against `std::hash`. General knowledge. |
| `new:189` | code | home | `Strata/src/Strata/Core/Hash.h:11-28`: FNV-1a, a stable 64-bit hash in ten lines |
| `new:190` | concept | home | Checksums: CRC-32C for damaged data, with `CRC32C("123456789")` as the worked check value. Evidence: `Strata/src/Strata/Core/Hash.h:49-53` |
| `new:191` | concept | home | Cryptographic hashes: SHA-256, digests in hexadecimal; a keyed hash and a constant-time compare named. General knowledge. |
| `new:192` | concept | home | UUIDs: the standard's 128 bits in 32 hexadecimal digits, Strata's 64 bits in 16. Evidence: `Strata/src/Strata/Core/UUID.h:13-14` |
| `new:193` | hands-on | home | Optional practice on Coin Run: its `.stproj` read in the code editor, its format header, version and start scene's handle found. Evidence: `Samples/Tetris/Tetris.stproj:1-22` |
| `automation:728` | term | home | JSON |
| `automation:745` | term | home | Hash (SHA-256) |
| `foundation:643` | term | home | FNV-1a, CRC-32C and SHA-256 taught here; HMAC named with a link to `automation/security`, which teaches it |
| `scene-ecs:664` | term | home | CRC-32C, a checksum that catches damaged data: one glossary entry with `foundation:643`'s CRC-32C; `world/serialization` links it for the cooked scene's header |
| `foundation:332` | concept | home | Utilities engines need: stable hashes against `std::hash`, UUIDs, CRCs, cryptographic hashes, constant-time compares, Base64; its binary layouts and untrusted lengths are taught on `basics/bytes`, radix sort on `basics/trees-graphs`, the offset allocator on `gpu/geometry-pool`, HMAC on `automation/security` |
| `foundation:155` | feature | home | Strata's `Hash`: FNV-1a (the excerpt `new:189`), `Combine`, which mixes one hash into another (`Strata/src/Strata/Core/Hash.h:41-47`), and CRC-32C, computed with the processor's CRC instructions where it has them and with the same result everywhere (`new:190`; `Hash.h:49-53`); `Combine` and the hardware path take a sentence each; `reference/core` keeps the header's generated table and links here |
| `foundation:156` | feature | link | `Crypto` (SHA-256, HMAC, the constant-time compare), linked to `automation/security` |
| `foundation:154` | feature | link | Strata's `UUID`, linked to `world/ecs` |
| `scene-ecs:342` | concept | link | Serialization formats, linked to `world/serialization` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Bytes, byte order, binary layouts and UTF-8 | `basics/bytes` | must |
| Binary, hexadecimal, bits and shifts, floating point | `basics/numbers` | must |
| Loops, functions and `std::string`, for reading text a character at a time | `basics/programming-2` | must |
| Files and a code editor | `basics/tools` | must |
| Hash maps, which use hash functions | `basics/data-structures` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `base64` | Base64 | - |
| `checksum` | checksum | - |
| `crc-32c` | CRC-32C | - |
| `cryptographic-hash` | cryptographic hash | - |
| `fnv-1a` | FNV-1a | - |
| `hash-sha-256` | Hash (SHA-256) | - |
| `hmac-basics` | HMAC (basics) | - |
| `json` | JSON | JavaScript Object Notation |
| `json-array` | JSON array | - |
| `json-object` | JSON object | - |
| `sha-256` | SHA-256 | - |
| `uuid` | UUID | universally unique identifier, GUID |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-10 | should | missing-item | `basics/debugging` | The VS Code path is "VS Code's 'Attach' entry with the C++ debugger", but nothing makes that entry. The editor writes no `.vscode/launch.json`; VS Code needs Microsoft's C/C++ extension for it; on Linux the extension needs `gdb`, which `start/install`'s package line does not install. A B0 reader on VS Code, the only code editor `start/install` gives Linux and macOS, cannot attach, and JSON is taught only on `basics/data-formats`. | The VS Code tab gives the steps: install the C/C++ extension, `sudo apt install gdb` on Linux, and paste a complete `.vscode/launch.json` with one attach configuration into the `Scripts` folder (a folder whose name starts with a dot, which the module neither compiles nor watches), with one sentence that it is a JSON file shown whole (about 150 words). | `allocation/basics-a.md:394-396`; `Docs/Manual/Scripting.md:202-203`; a search of `StrataEditor/src`, `Docs/Manual` and `.claude/skills` at the pin for "launch.json" and ".vscode" finds nothing; `allocation/start.md:157-160`; `StrataScriptCore/CMake/StrataScriptModule.cmake:2-5` |
| critic-basics-a-21 | should | shape | `basics/computer`, `basics/tools`, `basics/git`, `basics/data-structures`, `basics/trees-graphs`, `basics/bytes`, `basics/data-formats` | A primer has a "Common mistakes" section: each mistake, its symptom and its fix. These seven pages list none: no Covers, row or Fit line of theirs names a mistake, while the other eleven pages of the unit do. | Each page's Covers names three or four mistakes with their symptoms (about 250 words a page). For example: tools, a path with a space not quoted, a program run from the wrong folder, Ctrl+C taken for copy; git, a commit without `git add`, conflict markers left in a file, build output committed (the editor's `.gitignore` keeps `.strata/` out); data-structures, an index kept across a swap-remove, a hash map's order relied on; trees-graphs, a recursive walk of a deep tree that overflows the stack, a graph walk without a visited set; bytes, a length read from a file and used unbounded, UTF-8 cut by bytes; data-formats, a float written with too few digits, `std::hash` stored in a file, a trailing comma in JSON; computer, memory taken for storage, more cores taken for a faster single task. | `style.md:476`; `allocation/basics-a.md:5-46`, `:82-120`, `:459-485`, `:607-639`, `:677-701`, `:1088-1114`, `:1152-1186`; `Strata/src/Strata/Project/Project.cpp:198-199` |
| critic-basics-a-23 | should | stale-item | `basics/data-formats` (`new:192`) | The page says that UUIDs are "so large that two never meet". Strata's are 64-bit, and two can meet: for n random values the chance is about n² / 2^65, which is about 1 in 37 million for a million handles and one half near five billion. A page about exactness should give the number, not "never". | State the birthday bound with Strata's numbers as a worked example, and why 64 bits is enough for a project's entities and assets (about 80 words). | `allocation/basics-a.md:1166-1167`, `:1202`; `Strata/src/Strata/Core/UUID.h:13-14` |
