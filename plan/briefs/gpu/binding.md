# Brief: `gpu/binding`

| Field | Value |
| --- | --- |
| Title | Pipelines and binding: layouts, registers and bindless |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `gpu/shaders`, `gpu/resources-lifetimes` |
| From | render-core; retitled; + pipeline state objects and the `PipelineKey` cache (render-core 1.6, concept 18; render-scene 1.4) |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/binding` — Pipelines and binding: layouts, registers and bindless

**Covers.** The job: tell the GPU which resources a draw or a dispatch reads and writes, and fix the rest of its state
in one object made ahead of time. The problem and the approaches to binding: slots (Direct3D 11), descriptor sets and
tables (Vulkan, Direct3D 12), bindless. The map is the register figure: HLSL's `tN`, `sN`, `bN`, `uN` and `spaceS` become
Vulkan bindings N + 0, 128, 256 and 384 in set S; set 0 holds the scene layout, set 1 the bindless table; push
constants sit beside them. The contract, each rule with its reason: a new scene resource takes the next free slot of
the ledger in `Include/Scene.slang` and a pass that does not run binds a dummy; a push constant's slot never equals
another layout's constant buffer slot; a scene vertex shader reads exactly its input layout; a new binding counts against
MoltenVK's limits of 31 storage buffers and 16 samplers per stage, of which the scene set already uses 12 and 9 (GPU
culling's layout 23 storage buffers). A constant buffer, the glossary's entry here, is a buffer of constants bound at a
`b` register; the volatile kind is `gpu/resources-lifetimes`' entry, linked. The layout of GPU structs:
std140 for constant buffers, std430 for structured buffers, mirrored by C++ structs whose sizes are checked
(`FrameConstants` and `InstanceData` as the CPU and GPU contract). The toy binds one texture and one constant buffer for
a fullscreen pass in about 50 lines.

Pipeline state objects: everything fixed in one object; the scene's `PipelineKey` (pass, double-sided, mirrored,
skinned, velocity, surface) and its cache, where the vertex shader is chosen by pass and key, the input layout by the
vertex shader, culling and winding, the reversed-Z depth test per pass, the shadow bias and the blending of
transparents; fullscreen pipelines cached per framebuffer; one scene binding layout shared by the passes; when pipelines
are made and what that costs (a scene pipeline on the first frame that draws its key, searched in each renderer's own
cache, with NVRHI's one in-memory pipeline cache never saved, so a new key in a running game compiles inside the frame;
compute pipelines made with the renderer's resources, a missing shader there stopping the program). Bindless last:
the problem (binding textures per material breaks batching), the approaches (texture arrays, descriptor indexing,
virtual texturing), `BindlessTextureTable` (one update-after-bind array that grows from 1,024 slots by doubling up to
32,768, three reserved slots, a slot reused only frames-in-flight + 1 frames after release, a replaced texture taking a
new slot, and what a full table does), the table's size as the device allows it, the `TextureTable` indirection that
lets streaming change slots without touching a material, and bindless reads in shaders. Alternatives, tests and
changing safely close the page; the exercise traces a texture to its bindless slot.

**Leaves out.**

- Batching, sort keys and buckets of pipeline state → `draw/batching`
- The material record and its texture table entries → `light/material-data`
- Mip streaming, which changes bindless slots every frame → `draw/mip-streaming`
- Mirrored pipelines and flipped tangents → `draw/mirrors-camera-relative`
- Skinned variants of the scene shaders → `draw/skinned`
- Resource states and constant buffer versions → `gpu/resources-lifetimes`

**Fit.** `fits`: about 6,250 words against L (5,000). Four concepts, four excerpts, when pipelines are made and the
bindless table take the most words; at 250 words below L's top the page can take nothing more.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:364` | concept | home | Binding models, registers shifted to NVRHI's Vulkan ranges, one shared layout with a ledger, push constants in C++ only |
| `render-core:374` | concept | home | Pipeline state objects; the `PipelineKey` cache; the mistake of an input attribute no shader reads |
| `render-core:406` | concept | home | GPU struct layout rules and their C++ mirrors; the mistake of a `vec3` that shifts every later field |
| `render-core:369` | concept | home | Bindless textures and the stable texture table; the mistake of overwriting a slot a frame in flight may sample |
| `render-core:94`, `render-core:95` | feature | home | Scene pipelines by key; fullscreen pipelines |
| `new:39` | feature | home | When pipelines are made, and the cost: `GetScenePipeline` makes a scene pipeline the first time a frame draws its key, while draws are recorded, after searching the renderer's own vector of keys; each `SceneRenderer` keeps its own cache; NVRHI adds one empty in-memory `VkPipelineCache` per device, never saved, so a new key in a running game compiles inside the frame; compute pipelines are made with the renderer's resources, and a missing shader there stops the program (`ST_CORE_VERIFY`) (about 150 words). Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:226-232, 2091, 2424-2430, 2523-2525`; `Strata/src/Strata/Renderer/SceneRenderer.h:2445`; `Strata/vendor/NVRHI/src/vulkan/vulkan-device.cpp:245-248`; `git grep -ni pipelinecache 822a7a46 -- Strata/src` finds nothing |
| `render-core:46` | feature | use | MoltenVK's limits in the contract: 31 storage buffers and 16 samplers per stage; the scene set uses 12 storage buffers and 9 samplers, GPU culling's layout 23 storage buffers, and a new binding counts against these (about 100 words; `Docs/DeveloperGuide.md:298-301`) |
| `render-core:97`, `render-core:98`, `render-core:99` | feature | home | The scene binding layout; push constants; the four scene vertex layouts |
| `render-core:127` | feature | home | `Include/Scene.slang` as the layout ledger and the structs shared with C++ |
| `render-core:144` | feature | home | std140 and std430, mirrored by C++ structs with checked sizes |
| `render-core:100`, `render-core:101`, `render-core:102` | feature | home | `BindlessTextureTable`; `TextureTable`; bindless reads in shaders |
| `new:40` | feature | home | A full bindless table: `Allocate` returns an invalid slot and the table logs it; a texture being finalized then fails to load, and a streaming swap keeps the levels it has (one sentence, about 60 words). Evidence: `Strata/src/Strata/Renderer/BindlessTextureTable.h:38-39`; `Strata/src/Strata/Renderer/Texture.cpp:513-518, 826-829` |
| `render-core:40` | feature | home | The bindless table's size: the support query, halving to 1,024, the MoltenVK exception |
| `render-core:461` | code | home | `Strata/shaders/Include/Scene.slang:53-133`: `FrameConstants` and `InstanceData` as the CPU and GPU contract, paired with `Strata/src/Strata/Renderer/SceneRenderData.h:113, 189-199` |
| `render-core:466` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2424-2527`: a pipeline from a key: shaders, input layout, winding, culling, depth test per pass, shadow bias, transmittance blending |
| `render-core:472` | code | home | `Strata/src/Strata/Renderer/SceneVertexLayouts.h:23-89`: `constexpr` tables that tie vertex shaders to their input layouts |
| `render-core:454` | code | home | `Strata/src/Strata/Renderer/BindlessTextureTable.cpp:23-108`: growing a partially bound table; allocating slots and recycling them after `framesInFlight + 1` frames |
| `render-core:496`, `render-core:498` | figure | home | Registers to bindings; the bindless indirection from material to slot |
| `render-core:571` | rule | home | Bindless slots are written only at allocation and recycled after frames in flight; resolve slots every frame |
| `render-core:589` | rule | home | A push constant's slot must not equal another layout's constant buffer slot |
| `render-core:595` | rule | home | A scene vertex shader reads exactly its input layout; a new one gets its line in the table |
| `render-core:611` | rule | home | A new scene resource takes the next free slot of the ledger; a pass that does not run binds a dummy |
| `render-core:703`, `render-core:704`, `render-core:705`, `render-core:707` | term | home | Descriptor and descriptor set; binding layout and binding set; register and space; push constants |
| `render-core:711`, `render-core:712`, `render-core:713`, `render-core:715` | term | home | std140 and std430; bindless; update-after-bind and partially bound; texture table |
| `editor-ui:786`, `editor-ui:789` | term | home | Binding set; push constants, as the editor's UI words them; one entry each with `render-core:704` and `render-core:707` |
| `render-core:716`, `render-core:717` | term | home | Pipeline (PSO); input layout |
| `new:41` | term | home | Constant buffer: a buffer of constants a shader reads at a `b` register, `FrameConstants` at `b0` the scene's; its own glossary entry, apart from the volatile constant buffer, which is `render-core:708` on `gpu/resources-lifetimes` (R33 D34, critic-render-core-16). Evidence: `Strata/shaders/Include/Scene.slang:121`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:359` |
| `render-core:63` | feature | use | The fallback textures a pass binds as its dummy |
| `render-core:708` | term | use | Volatile constant buffer, the kind the scene layout binds at `b0`; its entry is on `gpu/resources-lifetimes` |
| `render-scene:89` | feature | home | The pipeline cache by key, with the same subject as `render-core:94` |
| `render-scene:92` | feature | home | The scene vertex layouts, with the same subject as `render-core:99` |
| `render-scene:579` | term | home | Pipeline key |
| `render-image:725` | term | home | Push constants, as the image part words them; one entry with `render-core:707`; the volatile constant buffer the item also names is linked to `gpu/resources-lifetimes` (duplicates.md, "Volatile constant buffer") |
| `render-image:726` | term | home | std140, as the image part words it; one entry with `render-core:711` |
| `new:42` | hands-on | home | Exercise ("trace it yourself"): a material's base color texture to its bindless slot on the source build: a breakpoint in `BindlessTextureTable::Allocate` when the texture finalizes, the slot read, then the same slot found in the material's texture table entry; a second run after mip streaming swaps the texture shows the new slot. Evidence: `Strata/src/Strata/Renderer/BindlessTextureTable.cpp:39-60`; `Strata/src/Strata/Renderer/Texture.cpp:513-519, 823-829` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shaders, the register convention of `Common.slang` | `gpu/shaders` | must |
| Resources, states, constant buffers and their versions | `gpu/resources-lifetimes` | must |
| Structured buffers and UAVs | `gpu/compute` | must |
| Reversed Z and the counter-clockwise front face | `gpu/coordinates` | must |
| Frames in flight | `gpu/how-a-gpu-frame-works` | must |
| Bytes, alignment and padding | `basics/bytes` | must |
| Mip streaming, which changes slots | `draw/mip-streaming` | helps |
| Mirrored instances | `draw/mirrors-camera-relative` | helps |
| Skinned meshes in the renderer | `draw/skinned` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `binding-layout` | Binding layout | - |
| `binding-set` | binding set | - |
| `bindless` | Bindless | Bindless slot, Bindless texture |
| `descriptor` | Descriptor | - |
| `descriptor-set` | descriptor set | - |
| `input-layout` | Input layout | - |
| `pipeline-pso` | Pipeline (PSO) | - |
| `pipeline-key` | Pipeline key | PipelineKey |
| `push-constants` | Push constants | - |
| `register-and-space` | Register and space | - |
| `std140` | std140 | std430 |
| `texture-table-strata` | Texture table (Strata) | Texture table index |
| `update-after-bind` | Update-after-bind | partially bound |
