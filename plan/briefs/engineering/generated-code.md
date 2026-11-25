# Brief: `engineering/generated-code`

| Field | Value |
| --- | --- |
| Title | Generated code: shaders, embedded files, version stamps and committed generators |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `engineering/cmake`, `gpu/shaders` |
| From | build-test ch. 6, §1.4 and §1.13 (`strata_add_shaders`, StrataShaderTool's SPIR-V patch, the registry, `strata_embed_file`, version and commit headers; `GenerateBlueNoise.py`, `FitFilmic.py`, `FitAOMultiBounce.py`, `GenerateAreaTable.py`, `GenerateWhiteBalance.py`, `GenerateBrandAssets.py`, `GenerateShowcase*.py`, `GenerateIslandTerrain.py`, `GenerateIconHeader.py`, the feature test's `GenerateAssets.py`); render-image §1.11 |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/generated-code` — Generated code: shaders, embedded files, version stamps and committed generators

**Covers.** The job: the code and data the build writes instead of people (compiled shaders and their registry,
embedded files, version stamps, the samples copied beside the programs) and the generators whose outputs are
committed. The problem: the approaches for shaders (compiled at run time, compiled offline and loaded from files,
compiled offline and embedded in the binary) and for other data. Strata embeds everything, so a game is one executable
and its pack, and the bytes do not depend on the configuration. The rule that keeps generated headers cheap: write a
file only when its content changed (`file(CONFIGURE)`), or everything that includes it recompiles every build. The
map: the shader pipeline from a `.slang` source and its includes through slangc (which validates what it writes) to
`<name>.raw.spv`, StrataShaderTool to `<name>.spv` and `<name>.h`, and the generated registry compiled into
`Strata_Renderer`, with the side branches that `ShaderEntries.txt` feeds (spirv-val on Linux, the Metal conversion on
macOS, the HLSL target check). The real code, in the order a build runs it: the two custom commands of every entry and
its line in the manifest; the generated `EmbeddedShaderRegistry.cpp`; StrataShaderTool, with the SPIR-V word layout
first (a five-word header; each instruction's word count in the high 16 bits and its opcode in the low 16),
`ParseSpirv`'s defensive checks, `DecoratePositionInvariant`, which collects every insertion before it inserts and
inserts from the back (why the depth prepass needs the decoration is linked), and `WriteFileAtomically`, so that a
failed build leaves no output a later build would take as current; `strata_embed_file`, a configure-time hex dump of
the default font into a function that returns a `std::span`; the version header, made at configure, and the commit
header, rewritten at build time only when the commit changes; the target that copies the samples beside the programs.
Committed generators: one table of every generator with what it writes, how it is checked and the page that explains
its output (`GenerateBlueNoise.py`, `FitFilmic.py`, `FitAOMultiBounce.py`, `GenerateAreaTable.py`,
`GenerateWhiteBalance.py`, `GenerateBrandAssets.py`, `GenerateIslandTerrain.py`, `GenerateShowcaseTerrain.py`,
`GenerateShowcaseProps.py`, `StrataTests/FeatureTest/Tools/GenerateAssets.py` and
`StrataEditor/Tools/GenerateIconHeader.py`); checks are `--check` run by hand, or the CTests
`StrataTools.ShowcaseTerrain` and `.ShowcaseProps` that compare committed outputs with regenerated ones, with `PythonMissing.cmake` standing in
when Python 3.10 or newer is absent; every tool uses only the standard library and is run with `python -I` where the
documents say so. Where the page quotes a generator's Python, the paragraph that introduces its first Python fence
says in one or two sentences what differs from C++ in it: no page of the book teaches reading Python, so the page
supplies it (R45). The page
never types the number of shader entries: it reads it from a build's `ShaderEntries.txt`. How it is tested:
`Renderer.ShaderTool` and `Renderer.ShaderModules`, named, and the Showcase checks. Exercises: add a shader variant and
find its `.raw.spv`, `.spv`, `.h` and manifest line; write a small SPIR-V inspector with `SpirvModule.h`; trace it
yourself: follow one name the renderer looks up, by a search or a debugger, from `EmbeddedShaders::Find` in
`ShaderLibrary` back to its entry in the generated `EmbeddedShaderRegistry.cpp`, the header of words it includes and the
custom command that wrote them. At the end
the reader can follow a shader from its source to the bytes the renderer looks up, patch a binary format safely, and
change a committed generator's output the right way.

**Leaves out.**

- Writing and registering a shader, slangc's flags and the dialect's checks → `gpu/shaders`
- Why the depth prepass needs invariant positions → `gpu/frame-tour`
- The Slang pin and its fetch → `engineering/third-party`
- The CI's shader steps → `engineering/ci`
- What the Filmic fit is → `image/tone-mapping`
- The morphological area table → `image/spatial-aa`
- The white-balance locus → `image/grading`
- The blue noise of the sun's shadow filter → `light/sun-shadows-2`
- The ambient-occlusion fit → `indirect/ao`
- The icon header and the editor's fonts → `editor-ui/design-system`
- Atomic writes in general → `core/files`

**Fit.** `fits`: about 4,310 words against L (5,000). Seven short excerpts in the order a build runs them, the table of
eleven committed generators, two figures, one concept and three exercises take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:313` | concept | home | Code generation in the build: embedding binary data, version headers that change only when their content changes, shaders compiled at build time, generated registries; the mistake of regenerating a header every build |
| `build-test:77`, `build-test:79` | feature | home | `strata_add_shaders`' two commands per entry, the manifest, the stage from the suffix, every entry depending on every include; StrataShaderTool, standard library only, built into `build/<preset>/tools` |
| `render-core:121`, `render-core:124` | feature | home | The build pipeline and StrataShaderTool as the render-core inventory lists them: taught with `build-test:77` and `build-test:79` |
| `build-test:82-85` | feature | home | `strata_embed_file`; the version header; the build commit header; the sample copy |
| `foundation:165`, `foundation:166` | feature | home | `EmbeddedFiles` (the default font) and `Version.h`, as the foundation inventory lists them |
| `build-test:172` | feature | home | The `StrataTools.*` CTests (label `tools`): the Showcase checks compare committed outputs with regenerated ones, the look-dev ones are named for `engineering/look-dev`; `PythonMissing.cmake` |
| `build-test:227-237` | feature | home | The table of committed generators: what each writes, how it is checked, the page that explains its output |
| `build-test:240` | feature | home | Every Python tool uses only the standard library and is run with `python -I` (isolated mode) where the documents say so |
| `build-test:388` | code | home | `CMake/StrataShaders.cmake:170-191`: slangc with `SLANG_RUN_SPIRV_VALIDATION=1`, then StrataShaderTool, then the registry and manifest lines; the flags above them are `gpu/shaders`' |
| `build-test:389` | code | home | `CMake/StrataShaders.cmake:198-221`: the manifest file and the generated registry source |
| `build-test:390` | code | home | `CMake/StrataShaderTool/SpirvModule.cpp:27-65`: `ParseSpirv`, a binary format read defensively (magic number, header, word counts) |
| `build-test:391` | code | home | `CMake/StrataShaderTool/SpirvModule.cpp:101-166`: `DecoratePositionInvariant`, insertions collected first and made from the back |
| `build-test:392` | code | home | `CMake/StrataShaderTool/StrataShaderTool.cpp:83-116`: `WriteFileAtomically`, a temporary file renamed into place |
| `build-test:394` | code | home | `CMake/StrataVersionCommit.cmake:1-24`: a header that changes only when the commit changes; its target is `Strata/CMakeLists.txt:31-42` |
| `build-test:395` | code | home | `CMake/StrataEmbeddedFiles.cmake:8-46`: a file embedded as a byte array with two regular expressions |
| `build-test:429` | figure | home | The shader pipeline with the side branches of `ShaderEntries.txt` (spirv-val, Metal, the HLSL target) |
| `build-test:432` | figure | home | SPIR-V's word layout: the header, word count and opcode, and the inserted `OpDecorate %v Invariant` after `OpDecorate %v BuiltIn Position` |
| `build-test:568` | hands-on | home | Add a `VARIANTS` line with a define, configure, find the new outputs and the manifest line |
| `build-test:570` | hands-on | home | A tiny SPIR-V inspector with `ParseSpirv`: list opcodes, find the decorations of an embedded module |
| `new:29` | hands-on | home | Trace it yourself, by a search or a debugger: one name the renderer looks up, from `EmbeddedShaders::Find` in `ShaderLibrary` back to its entry in the generated `EmbeddedShaderRegistry.cpp`, the header of words it includes, and the two custom commands that wrote the module and the header (about 200 words). Evidence: `Strata/src/Strata/Renderer/ShaderLibrary.cpp:12`, `:60`; `CMake/StrataShaders.cmake:172-191`, `:202-221` |
| `build-test:650`, `build-test:698` | term | home | Embedded shader registry; committed generator |
| `build-test:760` | open | home | The number of shader entries is read from a build's `ShaderEntries.txt` and never typed (the inventories count about 113 and 114) |
| `build-test:769` | open | home | Which generators have a CTest: only the two Showcase ones; `GenerateBlueNoise.py --check` and `FitFilmic.py --check` run by hand |
| `render-core:502` | figure | link | The shader build as a writer of shaders sees it, `gpu/shaders`' figure |
| `render-image:278`, `render-image:280`, `render-image:281`, `render-image:282` | feature | link | The outputs of the Filmic, white-balance, area-table and blue-noise generators, each explained on its page |
| `editor-ui:66` | feature | link | `Icons.h`, explained on `editor-ui/design-system` |
| `build-test:78` | feature | link | slangc's flags, taught on `gpu/shaders` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Writing and registering a shader; slangc and its flags | `gpu/shaders` | must |
| CMake targets, custom commands, `file(CONFIGURE)` and script mode | `engineering/cmake` | must |
| Binary and hexadecimal numbers, bit fields and 32-bit words | `basics/numbers` | must |
| Bytes and binary file formats | `basics/bytes` | must |
| `std::span`, `std::optional` and `std::vector` | `basics/cpp-modern` | must |
| The depth prepass, its `EQUAL` test and invariant positions | `gpu/frame-tour` | must |
| Atomic writes | `core/files` | must |
| Regular expressions | `basics/data-formats` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `committed-generator` | Committed generator | - |
| `embedded-shader-registry` | Embedded shader registry | - |
