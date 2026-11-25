# Brief: `engineering/third-party`

| Field | Value |
| --- | --- |
| Title | Third-party code and pinned tools |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `engineering/flags-portability` |
| From | build-test ch. 5 (submodules, the vendor wrapper, box3d and zstd, licenses and notices, the Slang pin and its fetch) |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/third-party` — Third-party code and pinned tools

**Covers.** The job: how Strata takes in other people's code and tools, pins them, builds them its own way and ships
their notices. The problem, with the approaches in a table of cost (copies in the tree, git submodules, package
managers such as vcpkg and Conan, CMake's FetchContent, system packages) and the mistakes (code copied without its
notice; a library upgraded together with other changes). Strata's choice: 19 pinned shallow submodules in
`Strata/vendor/`, one CMake file that wraps them all, and one tool, the Slang compiler, fetched as a pinned archive;
Strata uses no package manager. The map: the vendor tree, the per-user cache, and which libraries games link and
which only tools build. The real code. The vendor wrapper's CMake ground (about 80 words): policy defaults for
third-party projects with old `cmake_minimum_required` calls (CMP0077, CMP0091 and CMP0141 set to NEW, and
`CMAKE_POLICY_VERSION_MINIMUM` 3.5, which newer CMake needs to configure them), and why the project requires CMake 3.25:
`add_subdirectory(... SYSTEM)`, which came with 3.25 and takes in every vendor library. The vendor wrapper: each library's options forced as internal cache entries,
NVRHI Vulkan-only with validation, the `nvrhi_vk` to `nvrhi` link that GNU ld's order of static libraries needs, glm's
defines kept free of layout changes because glm types cross the script ABI, spdlog with its bundled fmt, JSON without
implicit conversions; stb as one object per header so that the linker drops what games never call; the libraries only
tools build, named with a link. box3d built from its sources instead of its own CMake, with a reason for every flag
(C17 with extensions, `-ffp-contract=off` for cross-platform determinism, `/arch:AVX2` on `wide8.c` for MSVC, asserts
that follow `ST_CORE_ASSERT`, a raised limit of mesh contact triangles), and its determinism scenario compiled for the
tests. zstd split into a decoder games link and a compressor only the pack writer uses. Licenses: permissive against
copyleft and why an engine cares (games ship the notices); `ThirdPartyNotices.md` with its "shipped in games" column,
the fonts, the code derived from other projects with its license text; copyleft code is read for ideas only.
Reproducible, verified downloads: `strata_slang_fetch` walked as a state machine (the stamp's fast path with no lock
and no network, the cache folder made private to its user, a file lock against concurrent configures with its
15-minute limit, a second look after the lock, three download attempts, the SHA-256 check, extraction of only the
listed files by a child CMake, the stamp, the atomic rename, and on every failure an error message instead of a failed
configure); `STRATA_SLANG_ROOT` for machines without a network; the rule never to change the digest to match a
download. Upgrades: a submodule in a commit of its own, notices updated, every test run; box3d's golden values taken
only from box3d's own test file. How it is tested: `StrataSlang.Fetch`, which serves a fake archive over `file://`
into a private cache, and the physics golden hash. Exercises: read `ThirdPartyNotices.md` and a sample's `CREDITS.md`
and list what an exported game must credit; trace it yourself: configure a fresh build directory twice, then a third
with `STRATA_SLANG_ROOT`, and follow with a search, or `cmake --trace-source=CMake/StrataSlang.cmake`, the path each
configure takes through `strata_find_slang` and `strata_slang_fetch` (the download, the stamp's fast path, the fetch
skipped). At the end the reader can add or upgrade a dependency the way Strata
does, say which licenses a game carries, and explain why a pinned download is safe to run.

**Leaves out.**

- Warnings off for vendor code and SYSTEM includes → `engineering/flags-portability`
- The libraries only tools build, in the proof that games hold no tooling → `engineering/cmake`
- How Slang compiles the shaders and with which flags → `gpu/shaders`
- The physics golden hash and determinism of the step → `physics/world-step`
- Credits for the book's pictures and the sample assets they show → `appendix/credits`
- Linking static libraries in general → `basics/build`

**Fit.** `fits`: about 4,630 words against L (5,000). Two concepts, the long fetch algorithm walked as a state machine,
the vendor wrapper's reasons and the licenses take the most, with three excerpts, three rules and two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:305` | concept | home | Third-party dependencies: the approaches and their costs; licenses, permissive against copyleft, and why games care; the mistakes |
| `build-test:310` | concept | home | Reproducible, verified downloads: pinning by SHA-256, per-user caches, file locks for concurrent configures, atomic renames, offline overrides; the mistake of "updating the digest to match" |
| `build-test:91-99` | feature | home | The 19 submodules; the vendor wrapper; box3d from sources; the zstd split; stb one object per header; `ThirdPartyNotices.md`; the upgrade procedure; the rule for code from other projects; box3d's determinism scenario for the tests |
| `build-test:81`, `render-core:123` | feature | home | The Slang pin (2026.20, four archives with their digests, `STRATA_SLANG_ROOT`, the `slangc -v` check), as both inventories list it |
| `build-test:170` | feature | home | `StrataSlang.Fetch`: digest, cache hits, error texts, per-user folders and the host key, tested with a fake archive |
| `build-test:383` | code | home | `Strata/vendor/CMakeLists.txt:144-182`: box3d built from its sources, a reason for every flag |
| `build-test:384` | code | home | `Strata/vendor/CMakeLists.txt:184-227`: a dependency split so that shipped games get only the decoder |
| `build-test:393` | code | home | `CMake/StrataSlang.cmake:123-251`: `strata_slang_fetch`, the algorithm kept whole |
| `build-test:434` | figure | home | The Slang fetch as a state machine, every failure edge ending in an error message |
| `build-test:502` | rule | home | Never change the Slang digest to match a download: a different hash means the release was replaced; bump Slang in a commit of its own |
| `build-test:504` | rule | home | Upgrade a submodule in its own commit, update the notices, run every test; box3d's golden values only from box3d's own test |
| `build-test:506` | rule | home | Copyleft code is read for ideas only: copied copyleft code would choose Strata's license |
| `build-test:603` | hands-on | home | Read `ThirdPartyNotices.md` and a sample's `CREDITS.md`: what an exported game must credit |
| `new:28` | hands-on | home | Trace it yourself: configure a fresh build directory twice, then once with `STRATA_SLANG_ROOT`, and follow by a search or `cmake --trace-source=CMake/StrataSlang.cmake` the path of each configure: the download, the stamp's fast path with no lock and no network, the fetch skipped for `STRATA_SLANG_ROOT` (about 200 words). Evidence: `CMake/StrataSlang.cmake:128-147`, `:275-310` |
| `build-test:637-641` | term | home | Submodule (git), shallow; vendoring; permissive and copyleft license (two entries); SHA-256 pin; per-user cache |
| `new:4` | not-done | home | No package manager (vcpkg, Conan): dependencies are pinned submodules wrapped by one CMake file. Evidence: `git ls-tree -r --name-only 822a7a46 \| grep -iE "vcpkg\|conanfile"` finds nothing; `Strata/vendor/CMakeLists.txt:3-7` |
| `new:27` | feature | home | The vendor wrapper's CMake ground: policy defaults for third-party projects with old `cmake_minimum_required` calls (`CMAKE_POLICY_DEFAULT_CMP0077`, `CMP0091` and `CMP0141` set to NEW, `CMAKE_POLICY_VERSION_MINIMUM` 3.5, which newer CMake needs to configure them); the project's CMake 3.25, the version that brought `add_subdirectory(... SYSTEM)`, which takes in every vendor library (about 80 words). Evidence: `CMake/StrataConfigurations.cmake:34-38`; `CMakeLists.txt:1`; `Strata/vendor/CMakeLists.txt:32`, `:46`, `:57`, `:245` |
| `build-test:45` | feature | link | Vendor warnings off, taught on `engineering/flags-portability` |
| `build-test:71` | feature | link | The vendor libraries only tools build, taught on `engineering/cmake` |
| `foundation:628` | term | link | Atomic write, whose entry is `core/files`' |
| `build-test:642` | term | link | File lock, whose entry is `core/files`', where `FileLock` is taught |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| git: clone, commits and submodules | `basics/git` | must |
| Hashes and SHA-256 | `basics/data-formats` | must |
| File locks and atomic writes | `core/files` | must |
| CMake functions, `add_library`, `EXCLUDE_FROM_ALL`, the vendor libraries in the target graph | `engineering/cmake` | must |
| Vendor warnings off and SYSTEM includes | `engineering/flags-portability` | must |
| FMA contraction and floating-point determinism | `engineering/flags-portability` | must |
| Slang and the shader build | `gpu/shaders` | helps |
| Asset packs and their compression | `assets/packs-export` | helps |
| The order of static libraries on the link line | `basics/build` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `per-user-cache` | Per-user cache | - |
| `permissive` | Permissive | copyleft license |
| `sha-256-pin` | SHA-256 pin | - |
| `submodule-git` | Submodule (git) | - |
| `vendoring` | Vendoring | - |
