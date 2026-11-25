# Brief: `engineering/releasing`

| Field | Value |
| --- | --- |
| Title | Packaging and releasing |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `engineering/ci` |
| From | build-test ch. 13 (the install layout, the marker, CPack, versions, the release workflow and procedure, verifying an archive) |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/releasing` — Packaging and releasing

**Covers.** The job: how a build becomes the archive a person downloads, and how a release is cut and checked. The
problem: packaging, installation and releases; install trees, relocatable installs and a marker; archives; versions
with pre-release suffixes; dry runs; checksums; checking the artifact as a person gets it; release notes; one
publishing job with the right to write; the mistake of testing the build tree instead of the installed layout. The
map: the release workflow (the version job; three build jobs that build Dist, run the Dist tests, pack, unpack and run
the archive and write its checksum; the publish job, which runs only for a tag `vX.Y.Z`) and the installed layout as a
tree. The contract: install rules exist only when the editor, the runtime and the CLI are all built; a file that
releases must ship gets an install rule and an entry in the layout `StrataEditor.Install` checks; release tests run
Dist, and a test whose expectation differs there says so with `#if defined(ST_DIST)`. The toy: `install()` rules and
`include(CPack)` for a program of two files. The real code: `StrataPackaging.cmake` (the executables at the top,
because an export copies the runtime from beside the editor and the launcher finds the samples there; the
`StrataInstall.json` marker, which makes the editor build scripts against the installation's SDK; the README made from
`PackageReadme.md`; the notices; the samples without `.strata`; the script SDK with glm's headers and license; the
manual and the agent skills; CPack's ZIP on Windows and TGZ elsewhere, named `Strata-<version>-<platform>` with that
folder at the top, Linux executables stripped); `strata_resolve_package_version`, which accepts only the project's
version with an optional pre-release suffix; the release workflow's version gate (the tag against
`project(Strata VERSION)`, `Docs/Releases/X.Y.Z.md` present, a run without a tag as a dry run that is never
published); the package step, which unpacks the archive into a fresh folder, checks its files and runs `--version`,
with CMake's own `cpack` because Chocolatey's comes first on the Windows runners; `SHA256SUMS.txt`, checked, and
`gh release create --verify-tag`. The procedure at the end of every wave: bump the version, write the notes, run
`ctest --preset <platform>-dist -LE "gpu|perf"`, push `v<version>-rc1` as a dry run, then the real tag. Strata's
archives are not signed and there are no installers. One sentence on the samples an archive carries:
`Samples.Content` bounds how much they grow it (linked to `engineering/contributing`). How it is tested: `StrataPackaging.Version` in script mode, and
`StrataEditor.Install`, linked. Exercises: make a local package and compare its tree with the install test's list;
dry-run a release on a fork; install a release archive, run `StrataEditor --version` and open a sample; trace it
yourself: follow `StrataInstall.json` by a search from the rule that writes and installs it to the editor's code
that looks for it, and say what changes for script builds when it is there. At the end the
reader can add a file to the release correctly, cut a dry run, and check an archive the way a person would get it.

**Leaves out.**

- Exporting a game and what its folder holds → `worlds/export`
- The install test's steps and the other package tests → `engineering/test-kinds`
- Release notes as the history of features → `appendix/history`
- Building scripts against the installed SDK → `editor/script-builds`
- The CI workflow → `engineering/ci`

**Fit.** `fits`: about 4,295 words against L (5,000). One concept, three excerpts, three figures, three rules, three
exercises and the trace take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:365` | concept | home | Packaging, installation and releases: install trees and markers, archives, pre-release versions, dry runs, checksums, the artifact checked as a person gets it, one job that may publish; the mistakes |
| `build-test:208-215` | feature | home | The install rules; the installation marker; CPack; the package version; the release workflow; the release notes; the release procedure; expectations that differ in Dist |
| `build-test:169` | feature | home | `StrataPackaging.Version`, the test of the package version in script mode |
| `worlds-runtime:169` | feature | home | The installed layout that puts the editor, the runtime and the CLI side by side, as the worlds inventory lists it |
| `build-test:409` | code | home | `.github/workflows/release.yml:45-93`: the version gate: the tag against the project's version, the notes present, a dry run without a tag |
| `new:20` | code | home | `.github/workflows/release.yml:175-226`: the archive unpacked into a fresh folder, its files checked, its programs run for their version, its checksum written |
| `build-test:410` | code | home | `CMake/StrataPackaging.cmake:54-107`: the install rules and CPack; with `CMake/StrataPackageVersion.cmake:7-24`, the version check |
| `build-test:448` | figure | home | The release workflow: the version job, three build jobs, publish only for `vX.Y.Z`; the tags of a dry run |
| `build-test:450` | figure | home | The installed layout as a tree, from the comment of `StrataPackaging.cmake` |
| `build-test:471` | figure | home | The installed folder of a release archive in a file browser |
| `build-test:534` | rule | home | Release tests run Dist; expectations that differ say `#if defined(ST_DIST)`: CI tests Release, only the release steps test Dist |
| `build-test:536` | rule | home | A file that releases must ship needs an install rule and an entry in `StrataEditor.Install`'s layout |
| `build-test:538` | rule | home | Use CMake's own `cpack` on the Windows runners |
| `build-test:586` | hands-on | home | Make a local package with `cmake --install` and `cpack`, and compare the tree with the install test's expected entries |
| `build-test:589` | hands-on | home | Dry-run a release on a fork with a `-rc1` tag of the project's version, and read the version job's checks |
| `build-test:595` | hands-on | home | Install a release archive and check it: unpack, run `StrataEditor --version`, open a sample from the launcher |
| `new:40` | hands-on | home | Trace it yourself, by a search: `StrataInstall.json` from the rule that writes and installs it to the editor's code that looks for it beside its executable; what changes for script builds when it is there (about 150 words). Evidence: `CMake/StrataPackaging.cmake:57-63`; `StrataEditor/src/Editor/ScriptToolchain.h:22`; `StrataEditor/src/Editor/ScriptToolchain.cpp:566` |
| `new:41` | feature | link | One sentence: `Samples.Content` bounds how much the samples grow a release archive; the check and its budgets are taught on `engineering/contributing` |
| `build-test:690-695` | term | home | Install tree and prefix (two entries); CPack; installation marker; pre-release suffix and release candidate (two entries); dry run; checksum file |
| `new:21` | not-done | home | Strata's release archives are not signed or notarized, and there are no installers: CPack writes a ZIP on Windows and a TGZ elsewhere. Evidence: `git grep -niE "signtool\|codesign\|notari" 822a7a46 -- .github CMake CMakeLists.txt` finds nothing; `CMake/StrataPackaging.cmake:95-99` |
| `build-test:168` | feature | use | `StrataEditor.Install`, which checks the layout this page makes; `engineering/test-kinds` teaches it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| CI workflows: jobs, matrices, steps and annotations | `engineering/ci` | must |
| The Dist configuration | `core/first-change` | must |
| SHA-256 checksums | `basics/data-formats` | must |
| CMake targets and options | `engineering/cmake` | must |
| git tags and pushes | `basics/git` | helps |
| The install test | `engineering/test-kinds` | helps |
| An export copies the runtime from beside the editor | `worlds/export` | helps |
| Script builds and the SDK the editor finds | `editor/script-builds` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `checksum-file` | Checksum file | - |
| `cpack` | CPack | - |
| `dry-run` | Dry run | - |
| `install-tree` | Install tree | - |
| `installation-marker` | Installation marker | - |
| `pre-release-suffix` | Pre-release suffix | - |
| `release-candidate` | release candidate | rc |
