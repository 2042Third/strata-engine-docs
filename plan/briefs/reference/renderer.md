# Brief: `reference/renderer`

| Field | Value |
| --- | --- |
| Title | Passes, bindings, switches, statistics, debug views, quality rows, device requirements |
| Kind | R |
| Size | L |
| Tracks | - |
| Needs | `gpu/frame-tour` |
| From | the references of render-core, render-scene, render-direct, render-indirect and render-image; `renderStats` keys (`EditorStateCommands.cpp`), `SceneRendererSpecification` and `SceneRendererStats` fields (`SceneRenderer.h`), fallback textures and samplers; the renderer's rules in one hand-checked table, each linking its home page |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/renderer` — Passes, bindings, switches, statistics, debug views, quality rows, device requirements

**Covers.** The paragraph on top says what the page is: the renderer's facts that the engine can list, generated or
parsed at the pin, so that no page of `gpu`, `draw`, `light`, `image` or `indirect` holds a copy of them
(`../pipelines.md` §7.1). The tables, in this order. (1) The GPU stages in frame order (the names passed to
`RegisterGPUStage` and to `RegisterStage(…, FrameStageKind::GPU)`), each with the pass it times, the quality row that
changes its cost where a row's traits name it, and the page that teaches the pass. (2) The scene bindings: the
registers of the one scene binding layout (the constant buffer, the SRV, UAV and sampler slots and the push
constants), each with what it holds, from the slot ledger of `Include/Scene.slang`. (3) The switches: the fields of
`SceneRendererSpecification` with their defaults and comments; a note that `GPUDriven`, `OcclusionCulling`,
`VisibilityFeedback`, `FadeLevelsOfDetail` and `BatchAcrossMaterials` are switches of code only, with no command or
menu. (4) The statistics: the fields of `SceneRendererStats` and the keys of the `renderStats` object that
`viewport.capture` and `editor.perf` report, each key with its field, its unit and the page that names it
(`render-image:57`). (5) The debug views: the `debugView` values of `viewport.capture`, the count as
`:value{key="debugViews.count"}`, each with what it shows and its page. (6) The quality rows: every row of
`RendererQualitySettings` with its four presets (Low, Medium, High, Ultra) from the `c_<Row>Row` lines, its Custom
range from the `Renderer.Quality` schema, its traits (players' row, GPU stage, memory) and its page; values in prose
only as `:value{key="quality.<field>.<preset>"}`. (7) The fallback textures and the common samplers of `Renderer`.
(8) The device requirements: Vulkan 1.2, the features and extensions the device selection requires, the swapchain's
formats and present modes, and the capabilities of `GraphicsDeviceInfo` that switch paths. (9) A hand-checked table
of the renderer's rules: each rule of `AGENTS.md`'s "Renderer conventions", "Shaders", "NVRHI pitfalls" and
"Rendering" bullets, and each rule of the five rendering inventories that is not one of them, in one line each with a
link to the page that states it with its reason. Hand-written besides: one introduction per table and `## Where it
lives in Strata` (`SceneRenderer.h`, `GPUProfiler.cpp`, `RendererQuality.cpp`, `Renderer.cpp`,
`EditorStateCommands.cpp`, `EditorViewportCommands.cpp`, `VulkanGraphicsDevice.cpp`, `Include/Scene.slang`). The
tools are `tools/reference.py parse` (routes "quality rows and presets", "debug views", "GPU stages", "render
statistics", "renderer specification and statistics") and the parses of the slot ledger, the fallback textures and
samplers and the device requirements that the answer to reference-q3 adds to `../pipelines.md` §7.1.

**Leaves out.**

- The order of the passes and why → `gpu/frame-tour`
- Binding layouts, registers and bindless → `gpu/binding`
- The device, NVRHI and the `Renderer`'s services → `gpu/vulkan-nvrhi`
- GPU timing and the stages' plumbing → `gpu/readback-timing`
- What each debug view shows and how to read it → `light/measuring-light`, `gpu/debugging`
- Quality rows, presets, traits and players' options → `image/quality-settings`
- The shader dialect's rules with their reasons → `gpu/shaders`
- The editor's Performance panel → `editor-ui/instrument-panels`
- Measured costs and their budgets → `reference/performance`

**Fit.** `fits`: about 3,600 words against L (5,000). The generated tables give the page its size: the GPU stages, the
scene bindings, the switches, the statistics, the debug views, the quality rows, the fallbacks and samplers and the
device requirements, roughly 5,000 words. The prose is the paragraph on top, eight table introductions, the note on
code-only switches, the hand-checked rules table (about 100 rows of one line, some 2,000 words, checked again at each
pin move and in phase B for the rows of local lights and global illumination) and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:57` | feature | home | The statistics of the image chain (`SceneRendererStats` fields from `PreExposure` on) and their `renderStats` keys, as generated rows; each page of `image` names only its own |
| `render-core:30` | feature | link | `GraphicsDeviceInfo`, the capabilities that switch paths |
| `render-core:32-33` | feature | link | The device requirements and the swapchain |
| `render-core:62-63` | feature | link | The common samplers and the fallback textures |
| `render-core:97-98` | feature | link | The scene binding layout and push constants |
| `render-core:155-178` | feature | link | The steps of the frame, which order the stages table |
| `render-core:210-214` | feature | link | `GPUProfiler`, `GPUPassTimer`, `RendererGPUStages`, the GPU statistics and the present stage |
| `render-direct:177-180` | feature | link | The shadows and lighting debug views, the lighting statistics and their access from the editor and agents |
| `render-direct:189-196` | feature | link | The quality rows of direct light and shadows |
| `render-direct:198` | feature | home | The `SceneRendererSpecification` switches of lights (`MaxLights`, the light cluster grid and the others the item lists), as rows of the switches table; each light page uses the switches it tunes |
| `render-direct:204` | feature | link | The GPU stages of direct light |
| `render-direct:210` | feature | home | The scene bindings of direct light and shadows, as rows of the bindings table; each light page names the slots it reads |
| `render-image:55` | feature | link | The GPU stages of the image chain |
| `render-image:227-238` | feature | link | `RendererQualitySettings`, the preset table, the `Renderer.Quality` section, row traits and players' rows |
| `render-indirect:96` | feature | link | The ambient-occlusion quality samples |
| `render-indirect:128` | feature | link | Reflection probe statistics |
| `render-indirect:138` | feature | link | The `Reflections` quality row |
| `render-indirect:163` | feature | link | The global illumination quality row |
| `render-indirect:181` | feature | link | Global illumination statistics |
| `render-indirect:183` | feature | link | The global illumination GPU stage |
| `render-indirect:189-193` | feature | link | The lighting views, value views, statistics and their access |
| `render-scene:50` | feature | link | The render scene's statistics |
| `render-scene:123` | feature | link | The GPU-driven mode switch |
| `render-scene:181-184` | feature | link | `renderStats`, the viewport debug views, quality rows and the stats overlay |
| `render-scene:722` | open | use | The switches with no command or menu, in the note on code-only switches |
| `render-core:549-618` | rule | link | The rules of the renderer's core, one line each in the rules table |
| `render-scene:461-513` | rule | link | The rules of drawing a scene, one line each |
| `render-direct:571-627` | rule | link | The rules of direct light and shadows, one line each |
| `render-image:525-579` | rule | link | The rules of the image chain, one line each |
| `render-indirect:467-520` | rule | link | The rules of indirect light, one line each |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A frame of the scene renderer, pass by pass | `gpu/frame-tour` | must |
| Pipelines, binding layouts and registers | `gpu/binding` | helps |
| GPU timing and stages | `gpu/readback-timing` | helps |
| Quality rows, presets and traits | `image/quality-settings` | helps |
| The debug views and their statistics | `light/measuring-light` | helps |
| The device and its capabilities | `gpu/vulkan-nvrhi` | helps |
| Running a command (`viewport.capture`) | `editor/commands` | helps |

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
| critic-reference-8 | should | missing-item | new items on `reference/assets`, `reference/renderer`, `reference/script-api` | The other area pages have a parsed table of limits, and `appendix/not-in-strata` sends "caps and limits of the features Strata has" to `reference/renderer`, but these three pages have none. Unlisted at the pin: a texture's longest side of 16,384 texels and 2^28 decoded pixels, a glTF scale of at most 10,000, 8 levels of detail, a hierarchy depth of 1,024 and a 64 MiB document, 4,096 joints per mesh, built-in handles 1 to 255; 32,768 bindless textures, 256 GPU timestamps a frame, a 2 GiB geometry pool, the draw key's submesh and LOD bits, 8,192-texel cascades, the font limits; save file names of 64 characters and files of 64 MiB, 65,536 script classes, 4,096 fields a class, names of 1,024 bytes and strings of 256 MiB. | Each of the three pages adds a parsed limits table through `tools/reference-limits.json`, as `reference/physics` and `reference/ui` have, with one introduction that names the teaching page. About 40 words each. | `allocation/reference.md:385-406`, `:460-485`, `:5-28`; `allocation/appendix.md:48`; `Strata/src/Strata/Asset/TextureImporter.h:84`; `Strata/src/Strata/Asset/TextureImporter.cpp:24`; `Strata/src/Strata/Asset/GltfImporter.cpp:68-74`; `Strata/src/Strata/Asset/GltfImporter.h:54`; `Strata/src/Strata/Renderer/Mesh.h:46`; `Strata/src/Strata/Asset/Asset.h:36`; `Strata/src/Strata/Renderer/GraphicsDevice.h:135`; `Strata/src/Strata/Renderer/GPUProfiler.h:95`; `Strata/src/Strata/Renderer/GeometryPool.h:87`; `Strata/src/Strata/Renderer/SceneDrawKey.h:28-29`; `Strata/src/Strata/Renderer/RendererQuality.h:191`; `Strata/src/Strata/Renderer/FontValidation.h:47-58`; `Strata/src/Strata/Core/SaveFiles.h:23-24`; `Strata/src/Strata/Scripting/ScriptModule.cpp:55-57`, `:957`, `:1046`; `Strata/src/Strata/Scripting/ScriptValue.h:17` |
