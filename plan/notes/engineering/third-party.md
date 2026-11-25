# Notes: engineering/third-party

## New terms

None. The five terms of the brief (per-user cache, permissive with its alias copyleft license, SHA-256 pin, submodule (git), vendoring) are defined in bold on the page. "Shallow" is explained in the submodule paragraph without bold.

## Requests

- Names for names.txt or code spans only: the page writes `vcpkg`, `Conan`, `FetchContent`, `spdlog`, `nlohmann/json`, `cgltf`, `nativefiledialog-extended`, `clang-cl`, `Inter`, `JetBrains Mono` and `Lucide` as code, so no word-list request is open.
- Further reading names NIST, the git documentation, the CMake documentation and the Open Source Initiative without links; hosts to admit if links are wanted.

## Since

`since: 0.8.0`: the Slang pin (2026.20) and the vendor file's box3d and zstd blocks are wave 8 work (`CMake/StrataSlang.cmake`, `Strata/vendor/CMakeLists.txt` at the pin).

## Not verified

- That the test `StrataSlang.Fetch` and the box3d determinism case fail without the flags or define named (no builds run).
- That the exporter copies `ThirdPartyNotices.md` into every export: `StrataEditor/src/Editor/GameExport.cpp` names the file (`c_NoticesFile`), its use not read in full.
- That the pack writer is the only user of `zstd_compress`: `Strata/CMakeLists.txt` links it to the AssetPipeline layer.
- The claim that MSVC does not contract under `/fp:precise` and that the decoder's assembly file needs an assembler step on GCC and Clang only: taken from the comments of `Strata/vendor/CMakeLists.txt`.

## Findings not applied

The brief lists no open findings. Left out by choice: the `slangc -v` check is described but the four archive digests are not printed in full (the page shows the first digits of the Windows one).

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
