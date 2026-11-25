# Brief: `reference/core`

| Field | Value |
| --- | --- |
| Title | Core utilities |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `basics/programming-3` |
| From | foundation ch. 13 "Core utilities reference" |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/core` — Core utilities

**Covers.** The paragraph on top says what the page is: the small utilities of the Core layer that engine code calls
everywhere, generated from their headers at the pin, each with its functions and the header's comments, for a
contributor who meets a name in code. The tables, one per header, in this order: `UUID` (64 bits, random, never zero);
`Hash` (FNV-1a, `Combine`, CRC-32C); `Crypto` (SHA-256, HMAC, the constant-time compare); `Base64`; `BinaryWriter` and
`BinaryReader` (bounds-checked, with a sticky failure); `JsonUtils` and `JsonEvents`; `StringUtils`; `RadixSort` and
`SortIndices`; `RangeAllocator`; `AmortizedCheck`; `Prefetch`; `ParallelClone`; `CommandLine` and
`CommandLineOptions`; `EmbeddedFiles` and `Version.h`; the base macros and the `Ref`, `Scope` and `WeakRef` aliases.
Hand-written: one sentence per header naming the page that uses or teaches it, where one does, and the rule that
engine code includes `stpch.h` first; `## Where it lives in Strata` (`Strata/src/Strata/Core/`). The tool is
`tools/reference.py parse` (the parse of the Core headers that the answer to reference-q3 adds to `../pipelines.md`
§7.1). The page is the home of the facts of the utilities that no other page teaches: `Base64`, `StringUtils`,
`Prefetch` and `ParallelClone`.

**Leaves out.**

- Ownership, errors and logging → `core/conventions`
- The math toolkit → `core/math`
- Jobs and `ParallelFor` → `core/jobs`
- Files and paths → `core/files`
- UUIDs as stable identities → `world/ecs`
- How Strata hashes and checks bytes (FNV-1a, `Combine`, CRC-32C) → `basics/data-formats`
- SHA-256 and HMAC in the handshake → `automation/security`
- Binary reading of untrusted data → `assets/robustness`
- The radix sort's use → `draw/batching`
- The range allocator's use → `gpu/geometry-pool`
- Embedded files and the version header → `engineering/generated-code`

**Fit.** `fits`: about 850 words against M (3,000). The generated tables give the page its size: the functions and
comments of about 15 headers, about 2,500 words. The prose is the paragraph on top (250 words), one sentence per header
naming the page that uses or teaches it (450), the rule on `stpch.h` (50) and the strip (100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:111` | feature | home | `ParallelClone`, a small helper the render scene uses: its function and comment |
| `foundation:155` | feature | link | `Hash`: FNV-1a, `Combine` and CRC-32C, linked to `basics/data-formats`, which teaches them; the generated table keeps the whole header |
| `foundation:157` | feature | home | `Base64` |
| `foundation:160` | feature | home | `StringUtils`; `core/first-change` changes it |
| `foundation:164` | feature | home | `Prefetch`, a one-line hint the script system uses |
| `foundation:56` | feature | link | `CommandLine` and `CommandLineOptions` |
| `foundation:152-154` | feature | link | The ownership aliases, the base macros and `UUID` |
| `foundation:156` | feature | link | `Crypto` |
| `foundation:158-159` | feature | link | The binary streams, `JsonUtils` and `JsonEvents` |
| `foundation:161-163` | feature | link | `RadixSort`, `RangeAllocator` and `AmortizedCheck` |
| `foundation:165-167` | feature | link | `EmbeddedFiles`, `Version.h` and `stpch.h` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Reading a C++ declaration | `basics/programming-3` | must |
| Bytes, text, JSON and hashes | `basics/data-formats` | helps |
| Ownership, errors and logging in Strata | `core/conventions` | helps |
| Smart pointers | `basics/cpp-memory` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-16 | could | thin-home | `reference/core` | The generated tables cover about 18 of the 50 headers of `Strata/src/Strata/Core/` and none of `Strata/src/Strata/Math/`. A contributor who meets `FileSystem::FromUTF8`, `Platform::EnsurePrivateDirectory`, `JobSystem`, `ErrorThrottle`, `SequenceLock`, `AtomicFileWriter` or a helper of `Math.h` finds no declaration with its comment on a reference page, while `reference/scene` gives the whole API of `Scene`. | The parse covers every public header of the two folders, each with one sentence that names its teaching page (`core/files`, `core/platform`, `core/jobs`, `core/math`, `core/conventions` and the others). About 30 more sentences, about 450 words. | `allocation/reference.md:984-993`, `:997-1007`; `Strata/src/Strata/Core/` (50 headers at the pin); `Strata/src/Strata/Math/` (`AABB.h`, `Frustum.h`, `Math.h`, `Random.h`, `Ray.h`) |
