# Brief: `assets/robustness`

| Field | Value |
| --- | --- |
| Title | Corruption, crash safety and cancellation |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `assets/importing`, `assets/packs-export` |
| From | assets; I→C; home of untrusted input (validate before use, checksums, bounded sizes) and of write-ahead ordering; corruption sweeps and fuzzing are `engineering/test-program`'s |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/robustness` — Corruption, crash safety and cancellation

**Covers.** The problem as a reader meets it: a pack truncated by a failed download; a glTF file whose accessors claim
a billion vertices; the power cut while an import writes its cache; a project closed while 17 imports run. The naive
answers are to trust the sizes a file states, to write the record and then the data, and to join every thread on close;
the page shows where each breaks. The idea: files are untrusted input, so they are checked before use, sizes are bounded
by what the file holds, and each block is checksummed before it is decoded; write-ahead ordering keeps any record from
naming data that is not there yet; and every long job checks a cancel flag, so nothing waits. The approaches of engines
and databases (checksums against cryptographic hashes, validation passes, fuzzing and sweeps; journals, atomic renames,
copy-on-write) end in a table.

Strata's choice, shown on its own code: the pack's checks on open (header and tables checksummed, entries that may not
share blocks, blocks that cover their entry exactly, names bounded by the file's size); the glTF importer's limits
(decoded bytes, accessor elements, a geometry budget relative to the buffers, hierarchy depth); every loader rejects
truncated or garbage bytes; the import record store (one line per record with its CRC-32C, a torn last line skipped and
cut, compaction from memory); cache files renamed into place before their record (the code is on `assets/importing`);
cancel flags checked per block, and jobs that share only `BackgroundWork`. The tests that keep it true: the "any single
changed byte" sweep of packs, and the corrupt-bytes tests of every loader; sweeps and fuzzing in general are
`engineering/test-program`'s. What the choice cannot do: a CRC finds accidents, not an attacker, and Strata does not sign
exports (`worlds/export`). Common mistakes: allocating what a size field says, checking after use, joining threads on
close. The exercise corrupts a pack in a test and reads each failure's message.

**Leaves out.**

- Corruption sweeps and fuzzing as test machinery → `engineering/test-program`
- Atomic writes, private files and TOCTOU → `core/files`
- Font files as untrusted input → `gpu/text`
- The game manifest as untrusted input → `worlds/game-identity`
- Untrusted clients of the editor's automation server → `automation/security`
- Saves that never lose data in the editor → `editor/saving`

**Fit.** `fits`: about 4,500 words against L (5,000). Three concepts from zero, a table and four short excerpts take the
most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:351` | concept | home | Untrusted input and corruption |
| `assets:355` | concept | home | Crash-safe bookkeeping: write-ahead ordering |
| `assets:359` | concept | home | Cancellation and editor responsiveness |
| `assets:173` | feature | home | The pack's validation on open, sizes bounded by the file |
| `foundation:158` | feature | home | `BinaryReader` and `BinaryWriter`: little-endian, bounds-checked reads whose failure sticks, the pattern loaders of cooked data use (`ParseCookedTexture` reads through it) |
| `assets:430` | code | home | `Strata/src/Strata/Asset/AssetPack.cpp:271-292`: header and table checksums, with the block checks at 388-405 |
| `assets:444` | code | home | `StrataTests/src/Asset/AssetPackTests.cpp:1008-1030`: the "any single changed byte" sweep |
| `new:20` | code | home | `Strata/src/Strata/Asset/ImportRecordStore.h:31-48`: the record store's design, append-only and crash-safe |
| `new:21` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:57-68`: the limits that keep hostile files from exhausting memory, time or the stack |
| `assets:552` | rule | home | Every loader rejects truncated or garbage bytes; format changes extend the corruption tests |
| `assets:600` | hands-on | home | Corrupt a pack and read the failures |
| `assets:132` | feature | use | The import record store (taught in `assets/importing`) |
| `assets:138` | feature | use | Import cancellation (taught in `assets/importing`) |
| `assets:395` | code | use | Cache files published before their record (home `assets/importing`) |
| `assets:535` | rule | use | Cache before record |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Packs, blocks and their tables | `assets/packs-export` | must |
| Import records, and how cache files are published | `assets/importing` | must |
| CRC checksums | `basics/data-formats` | must |
| Atomic writes and TOCTOU | `core/files` | must |
| Atomic flags, and joining threads | `basics/threads` | must |
| Writing and running one test case | `core/first-change` | must |
| Corruption sweeps and fuzzing in general | `engineering/test-program` | helps |
| Untrusted fonts | `gpu/text` | helps |
| Signed exports, and the manifest as untrusted input | `worlds/game-identity` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
