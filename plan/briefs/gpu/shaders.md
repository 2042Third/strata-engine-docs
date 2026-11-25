# Brief: `gpu/shaders`

| Field | Value |
| --- | --- |
| Title | Shaders: Slang, the build and the dialect |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `gpu/vulkan-nvrhi`, `basics/build`, `core/first-change` |
| From | render-core; writing and registering a shader, the dialect and its checks (the CMake custom commands and the generated registry are `engineering/generated-code`'s) |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/shaders` — Shaders: Slang, the build and the dialect

**Covers.** The job: how a shader goes from a `.slang` file to a shader object at run time, and the rules that keep its
source portable. The problem and the approaches (GLSL to SPIR-V, HLSL through DXC, Slang; compiled while the game runs
or when the engine is built), then Strata's choice and its reasons: HLSL-syntax Slang, compiled at build time by a
pinned slangc to SPIR-V 1.5, checked, and embedded in the program as arrays, so no game ships a compiler and every
configuration runs the same bytes. The map is the build's diagram, from the source and its includes to
`ShaderLibrary::Get`. Then, in the order a writer meets them: stages, entry points, inputs, outputs and system values
(every entry is `main`, the stage comes from the registered name's suffix, the converted shaders fill `st_*` globals in
an entry wrapper); the source tree; registering a shader in `strata_add_shaders`, variants, and why configure runs again;
the slangc flags with their reasons (register shifts, column-major matrices, stated image formats, two warnings
switched off) and the flags not passed; `Include/Common.slang` and its one `__target_switch`.

The dialect comes next, each rule with the bug it prevents: `mul` only with a matrix, comparisons through `all()` and
`any()`, matrix constructors that take rows, `select`'s order, `SV_VulkanInstanceID`, derivatives before the first
`discard`, nothing target-specific outside `Common.slang`. The real case is told here: a `mul` of two vectors collapsed
a shadow filter and passed every GPU test. Then the checks that guard the dialect (`Architecture.Shaders`,
`Renderer.ShaderModules`, `Renderer.ShaderTool`, the GPU suite, CI's HLSL target, `spirv-val`, the Metal conversion),
how a conversion slip is found with the look-dev compare, and what a Direct3D target would still need. The toy is a
fullscreen gradient shader with its one CMake line; loading it is the last excerpt. The exercise traces a registered
name to the bytes `ShaderLibrary` returns.

**Leaves out.**

- The CMake custom commands, StrataShaderTool's SPIR-V patch and the generated registry → `engineering/generated-code`
- Slang's pinned download and its cache → `engineering/third-party`
- The CI's shader steps → `engineering/ci`
- Registers, binding layouts and push constants → `gpu/binding`
- Compute shaders, `SampleLevel` in compute and storage image formats → `gpu/compute`
- The invariant position decoration and why the prepass needs it → `gpu/frame-tour`
- `SanitizeHDR`, which the first pass that writes HDR values calls → `light/brdf`
- The look-dev harness itself → `engineering/look-dev`
- Writing a pixel test that catches a dialect slip → `gpu/first-triangle`

**Fit.** `fits`: about 5,950 words against L (5,000). The dialect with its real bug, four excerpts and the checks that
guard the dialect take the most words; the build's internals stay with `engineering/generated-code`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:354` | concept | home | Shading languages and offline compilation; why build time and embedding; the mistake of adding a file without listing it |
| `render-core:350` | concept | home | Stages, entry points, inputs and outputs, system values; `main` and the suffix; the `SV_InstanceID` mistake named, its rule linked to `draw/batching` |
| `render-core:360` | concept | home | HLSL against GLSL: `mul`, `*`, row constructors, `select` against `mix`, vector comparisons, `Sample` in compute; the real bug |
| `render-core:119`, `render-core:120` | feature | home | The shader source tree, its file counts given by a generated value, never typed (40 files in `Include/` at the pin, `GeometryTables.slang` among them; the inventory's 39 is a slip); the entry list in `strata_add_shaders` with variants and `INVARIANT_POSITION` |
| `render-core:122` | feature | home | slangc's flags and the reason for each, and the flags not passed |
| `render-core:125`, `render-core:126` | feature | home | `EmbeddedShaders` and `ShaderLibrary`; `Include/Common.slang` |
| `render-core:128`, `render-core:129` | feature | home | The dialect's rules; the checks that guard them |
| `render-core:130`, `render-core:131` | feature | home | Finding a conversion slip with a signed compare against 0.7.0's look-dev set; what other targets would need |
| `render-core:143` | feature | home | Column-major matrices: glm's bytes, `floatNxN(...)` takes rows, `mul(M, v)` |
| `render-core:457` | code | home | `Strata/src/Strata/Renderer/ShaderLibrary.cpp:47-87`: lookup by registered name, the stage from the suffix, the thread-safe cache (with `Strata/src/Strata/Renderer/EmbeddedShaders.h`) |
| `render-core:458` | code | home | `CMake/StrataShaders.cmake:64-86`: the flags with their reasons; the custom commands later in the file are `engineering/generated-code`'s |
| `render-core:459` | code | home | `Strata/shaders/Include/Common.slang:4-46`: the register convention, `NDCToUV`, the sRGB transfer; `SanitizeHDR`, the next lines of the file (48-57), is named in one sentence with a link to `light/brdf`, its home |
| `render-core:460` | code | home | `Strata/shaders/Include/Common.slang:194-215`: the only `__target_switch` and `spirv_asm`, and why `PackHalf2x16` is wrapped |
| `render-core:502` | figure | home | The shader build: source and includes, slangc, `.raw.spv`, StrataShaderTool, `.spv` and `.h`, the registry, `ShaderLibrary::Get`; the variants' fan-out |
| `render-core:576` | rule | home | Every shader entry is listed in `strata_add_shaders`; re-run configure |
| `render-core:578`, `render-core:580` | rule | home | `mul` only with a matrix; comparisons, constructors and `select` |
| `render-core:587` | rule | home | Derivatives before the first `discard` |
| `render-core:590` | rule | home | `__target_switch` and `spirv_asm` only in `Include/Common.slang`; no generics, modules or interfaces |
| `render-core:719`, `render-core:720`, `render-core:721`, `render-core:722`, `render-core:723` | term | home | Entry point; SPIR-V; Slang and slangc; HLSL and GLSL; shader variant |
| `render-core:726`, `render-core:727` | term | home | Derivative; discard |
| `render-core:121`, `render-core:124` | feature | link | The build's custom commands and StrataShaderTool, one sentence each |
| `render-core:123` | feature | link | The Slang pin, one sentence |
| `render-core:603` | rule | link | `SanitizeHDR` appears in `Common.slang`; its rule is taught where the first HDR writer calls it |
| `build-test:78` | feature | home | The same flags, from the build's side: the same subject as `render-core:122` and its excerpt `render-core:458`, taught once with them |
| `build-test:80` | feature | home | `EmbeddedShaders::GetAll` and `Find`, the run-time lookup in the embedded registry, taught with `ShaderLibrary` (`render-core:125`) |
| `build-test:171` | feature | home | `StrataShaders.TargetHLSL`: `slangc -target hlsl` over every entry, with no label so every CI job that runs the tests runs it; one of the dialect's checks (`render-core:129`) and a first step of what a Direct3D target would need (`render-core:131`) |
| `build-test:185` | feature | home | `Architecture.Shaders` (derivatives before the first `discard`, Slang only, HLSL syntax), one of the checks that guard the dialect (`render-core:129`) |
| `build-test:480` | rule | home | "Shaders are listed, not globbed", from the build's side: the same rule as `render-core:576`, taught once with it |
| `build-test:644`, `build-test:645` | term | home | Slang and slangc; SPIR-V, as the build's glossary words them; one entry each with `render-core:721` and `render-core:720`; SPIR-V's word layout is linked to `engineering/generated-code` |
| `new:31` | hands-on | home | Exercise ("trace it yourself"): `PostProcess/Fullscreen.vert` from its line in `strata_add_shaders` to the bytes `ShaderLibrary::Get` returns: a breakpoint in `Get`, the step into `EmbeddedShaders::Find`, the stage read from the name's suffix, and the generated header found in the reader's own build directory. Evidence: `Strata/CMakeLists.txt:136`; `Strata/src/Strata/Renderer/ShaderLibrary.cpp:29, 47, 60` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| How a C++ program is built: compiling, linking, CMake, configure and build | `basics/build` | must |
| The short source build and one test case | `core/first-change` | must |
| The pipeline at a glance: vertex and fragment shaders, interpolants | `gpu/how-a-gpu-frame-works` | must |
| NVRHI's device and shader objects | `gpu/vulkan-nvrhi` | must |
| Matrices and matrix order | `basics/math-matrices` | must |
| Floating point and half floats | `basics/numbers` | helps |
| The sRGB transfer function | `basics/color` | helps |
| The look-dev harness (captures and signed compares) | `engineering/look-dev` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `discard` | Discard | - |
| `entry-point-gpu` | Entry point (gpu) | - |
| `glsl` | GLSL | - |
| `hlsl` | HLSL | - |
| `slang` | Slang | slangc |
| `spir-v` | SPIR-V | - |
| `variant-shader` | Variant (shader) | - |
