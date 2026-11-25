# Critique `complete-rendering-a`: completeness against render-core, render-scene and render-image

Lens: every item of `inventory/render-core.md`, `inventory/render-scene.md` and `inventory/render-image.md` (sections
1, 2, 5 and 8) walked against the outline; page sizes; merged or dropped chapters; prerequisites and order of parts 6,
7 and 10; the one-home table; "What Strata does not do"; W8 marks. Engine evidence is at `822a7a46` unless a branch is
named (branches were read with `git log`/`git diff`, nothing was changed or run).

Verdict: the three inventories map onto parts 6, 7 and 10 almost row for row, so little content is lost outright. What
would hurt the book is in the seams: three foundations every rendering page assumes have no home (GPU compute, floating
point, sampling and aliasing); the internals page shape has no slot for "how engines solve it", which the inventories
supply for some 35 concepts; several concepts are homed twice or in a later part than their first use (exposure,
shadow caches, uploads, screen fraction); the prerequisites of parts 6, 7 and 10 omit pages their material needs; and
wave 8 changes pages that carry no W8 mark (`image/quality-settings`, `gpu/frame-tour`, `make/look`). The first thing
to change is to add the missing primers and the compute page (findings M1, M2), because every later rendering page
links to them.

Severity: **blocker** (the book fails its goal or the process breaks), **major** (a reader or the process is clearly
hurt), **minor** (worth fixing). There are no blockers.

---

## Major findings

### M1. GPU compute programming has no home

- **Where**: `outline-2.md` part 6 table (lines 49-61); `book.md` one-home table.
- **Problem**: no page teaches the compute model (dispatches, thread groups, group-shared memory, GPU atomics, UAV
  writes and barriers), yet the material of three areas is built on it:
  - render-scene ch. 9 lists "compute shaders and atomics" as a prerequisite, and code #24 (`CullBuild.comp.slang:49-110`)
    is prefix allocation by atomics;
  - render-image code #6 (`Histogram.comp.slang:39-71`, group-shared bins and `InterlockedAdd`) lists "Compute shaders,
    workgroups" as what the reader must know first;
  - render-direct ch. 5 lists "compute shaders" as a prerequisite, and render-indirect code #4 and #12 need group-shared
    reductions.
  - render-core concept 13 names compute only as a stage. Rule 2 and rule 5 (barriers on the same binding set, the
    first transition of a compute-written texture) presuppose the model. The curricula checklist (`research/curricula.md`
    line 230) has "Compute shaders, dispatches, UAV barriers **[S]**".
- **Proposal**: add after `gpu/shaders` the row
  `| gpu/compute | Compute shaders: dispatches, thread groups, shared memory and atomics | I | M | render-core concepts 9, 13; render-scene concept 14 (prefix allocation); toy: a histogram and a prefix sum |`.
  List it as a page prerequisite of `draw/gpu-driven`, `draw/occlusion`, `image/exposure`, `light/many-lights` and
  `indirect/ao`.

### M2. Floating point has no home in Foundations

- **Where**: `outline-1.md` part 2 (lines 71-80: `basics/computer`, `basics/bytes` and the rest).
- **Problem**: the rendering areas lean on floating point everywhere, and no primer teaches it:
  - render-core concept 20 (reversed-Z exists because of float precision) and concept 22 (float32 has about 7 digits,
    7.8 mm steps at 100 km);
  - render-image concept 2 (half floats: 65504, subnormals, NaN and Inf spreading) and rule 2 (pre-exposure is exact
    only because powers of two are exact);
  - render-scene concept 20; render-direct ch. 1 lists "floating point" as a prerequisite; foundation concept 25 has the
    FMA mistake.
  - The curricula checklist (`research/curricula.md` line 72) marks "Floating point: representation, rounding,
    precision far from the origin" **[S] [gap]**.
  - No basics row mentions numbers: `basics/bytes` is "Bytes, files, text and hashes", needed by assets, packs and
    automation.
- **Proposal**: retitle `basics/bytes` to "Bytes, numbers, files, text and hashes", make it L, and allocate to it
  integers, IEEE 754 float32, half and double, rounding, precision against magnitude, NaN and Inf, and why multiplying
  by 2^n is exact. Or add `basics/numbers` (C, M) after `basics/computer`. List the page in the prerequisites of
  parts 6 and 10.

### M3. The internals shape has no place for "how engines solve it"

- **Where**: `style.md` line 60 (the internals shape). The kinds in outline-2 lines 69-81 and outline-3 lines 49-60.
- **Problem**: part 7 has one concept page (`draw/entities-to-draws`, M) for 12 internals pages, and part 10 has one
  (`image/why-post`, S) for 11. The inventories give "approaches engines use" for some 35 concepts that are homed on
  internals pages. Examples:
  - occlusion: hardware queries, software-rasterized occluders, HZB reprojection, two-phase HZB (render-scene
    concept 16);
  - LOD transitions: popping, dithered fade, geomorphing (concept 8);
  - spatial structures (concept 6); tone curves: Reinhard, Hable, ACES, AgX, GT (render-image concept 7);
  - TAA: UE TAA/TSR, Frostbite, DLAA (concept 15); AA: SSAA, MSAA, MLAA, SMAA (concepts 12-13).
  - render-image proposed 9 of its 11 chapters, and render-scene 3 of its chapters, as "concept + internals".
  - The internals shape goes job → map → contract → toy → code → tests → changing it, and `:::elsewhere` is only an
    aside. So the general teaching the owner asked for ("a … textbook on strata engine and engines in general") has
    no section to live in on exactly the pages that carry most of it.
- **Proposal**: in `style.md` change the internals shape to "the job in one paragraph → **the problem and how engines
  solve it (the approaches with their costs, at most a fifth of the page; the inventory's 'Concepts to teach' entry)**
  → a map → …". Also require each part brief to name which internals pages carry such a section.

### M4. Exposure, HDR and sRGB are each claimed by two or three pages

- **Where**: the `book.md` one-home table (lines 56-83) has no row for them. The pages are outline-3 `light/units-exposure`
  (line 12), `image/exposure` (50), `image/pre-exposure` (51), `image/why-post` (49), `image/encoding` (54), and
  outline-1 `basics/color` (77).
- **Problem**:
  - render-direct ch. 1 ("pick an exposure from EV100, and say why the HDR target needs a pre-exposure") goes to
    `light/units-exposure`. render-image 1.2 (manual exposure, the EV100 conversion and table, light units feeding
    exposure, pre-exposure) goes to `image/exposure` and `image/pre-exposure`.
  - The HDR target, half floats and `SanitizeHDR` are claimed by `basics/color` ("linear, sRGB, HDR"),
    `light/units-exposure` ("units, HDR and exposure") and `image/why-post` (render-image 1.1, concept 2).
  - The sRGB transfer is claimed by `basics/color`, `image/encoding` (render-image 1.4 "sRGB encoding", concept 8) and
    `assets/textures` ("color spaces").
- **Proposal**: add these rows to the one-home table.

  | Concept | Home | Others link |
  | --- | --- | --- |
  | Light units, EV100, the camera exposure model | `light/units-exposure` | `image/exposure`, `make/lighting`, `make/look` |
  | Metering, adaptation, exposure key | `image/exposure` | `light/units-exposure` |
  | Pre-exposure (the mechanism) | `image/pre-exposure` | `light/units-exposure` (one paragraph on why) |
  | HDR target, half-float limits, `SanitizeHDR` | `image/why-post` | `basics/color` (the idea), light |
  | The sRGB transfer function | `basics/color` | `image/encoding` (quantization, dither), `assets/textures` (sRGB textures) |

### M5. Shadow casters, shadow caches and cascade occlusion are homed in two parts, and part 7 would need part 8

- **Where**: `book.md` line 67 ("Shadow casters, light records | `light/*` shadow chapters | draw"). Outline-2
  `draw/bounds-culling` (line 71) and `draw/occlusion` (line 78). Outline-3 `light/sun-shadows-1` (line 19).
- **Problem**:
  - `light/*` names no page.
  - render-scene ch. 10 gives `draw/occlusion` "cascades' occlusion and 'runs while it pays', the shadow cascade cache"
    (render-scene 1.8, `PrepareShadowCache`/`CommitShadowCache`, rule 12). render-scene 1.2 gives the CPU part
    `FindShadowCasters`, sub-texel casters and `CanShadowView`. Meanwhile render-direct ch. 7 gives
    `light/sun-shadows-1` "caster selection and caching".
  - Per `outline-1.md` line 10, writers read the whole inventory, so both writers will teach both.
  - Part 7 lists no shadow page as a prerequisite (outline-2 line 65), and render-scene ch. 10 needs "shadow cascades
    (shadows area)".
  - Local shadow views' culling (`CullLocalShadowViews`, render-scene section 9) and the light records
    (`RenderLights`, render-scene 1.1) are left undecided by the inventory. Both are W8 subjects.
- **Proposal**: replace row 67 with these rows.

  | Concept | Home | Others link |
  | --- | --- | --- |
  | Sun caster selection (`FindShadowCasters`, sub-texel, `CanShadowView`), the cascade cache and its versions | `light/sun-shadows-1` | `draw/bounds-culling`, `draw/occlusion` (one sentence each) |
  | Cascade occlusion (HZB per cascade, runs while it pays) | `light/sun-shadows-1`, as an application of `draw/occlusion` | |
  | Light records (`RenderLights`) | `light/many-lights` | `draw/render-scene` |
  | Local shadow views' culling and caches | `light/local-shadows` | `draw/gpu-driven` |

  This keeps part 7 free of shadow prerequisites and of W8 subjects.

### M6. The upload chapter is claimed twice, and part 5 comes before the GPU primer it needs

- **Where**: `book.md` line 64. Outline-2 `assets/uploads` (line 37), `gpu/upload-queue` (55) and the part 5
  prerequisites (25). `process.md` line 77 (wave 3 writes `assets`) and line 79 (wave 5 writes `gpu`).
- **Problem**:
  - assets ch. 9 ("Getting bytes to the GPU: … steps, `PlanStep`, staging pool and fences, transfer queue") and
    render-core ch. 7 ("staging pool, budgeted steps (`PlanStep`), tickets, transfer queue trade-off") propose the same
    chapter. The plan keeps both as M pages, split into "mechanism" and "what is queued and when".
  - The mechanism's home is written two waves after the page that links to it. Two thin pages describing one 646-line
    class invite repetition.
  - Part 5 also has no GPU prerequisite, while assets ch. 4 needs "texture sampling from the rendering primer", ch. 5
    "meshes from the rendering chapters" and ch. 9 "GPU command submission basics".
  - Sampling and filtering (bilinear, trilinear, anisotropic, mips) have no named home at all; render-image code #23
    needs bilinear filtering.
- **Proposal**:
  - (a) Move `gpu/how-a-gpu-frame-works` into Foundations as `basics/gpu` (C, L: the pipeline at a glance, textures,
    sampling and filtering, buffers, command submission, frames in flight). List it in the prerequisites of part 5 and
    part 6.
  - (b) Merge `gpu/upload-queue` into `assets/uploads` (I, L, "Getting bytes to the GPU: staging and budgeted uploads",
    from render-core 1.5 and assets "Budgeted uploads and staging"). Delete row 64, or point it at `assets/uploads`.
  - If the split is kept instead, move `gpu/resources-lifetimes` and `gpu/upload-queue` into wave 3.

### M7. Wave 8 changes pages of these areas that carry no W8 mark

- **Where**: `outline-1.md` line 11 (the definition of W8). The rows `make/look` (outline-1 line 37) and
  `make/big-scenes-fast` (line 54). Outline-2 `gpu/frame-tour` (line 58) and `draw/gpu-driven` (77). Outline-3
  `image/quality-settings` (59). `process.md` Phase B step 7.
- **Problem**: the evidence is in unmerged branches dated 2026-11-09 and 2026-11-10.
  - `agent/wave8-local-lights` (20 commits) changes `RendererQuality.h`/`.cpp`: a new row `LocalShadowViewsPerFrame`
    moves there from `SceneRendererSpecification`, the default of `MaxShadowedLocalLights` becomes 16, and
    `c_SectionVersion` goes from 6 to 7. It also changes:
    - `SceneRenderer.h` (+126 lines: new stats, `SpreadLightingUpdates` semantics, and `AdaptationSeconds` now also
      drives shadow fades, which `image/exposure` describes) and `SceneRenderer.cpp`;
    - `SceneRendererGPUDriven.cpp` and `Cull.comp.slang`;
    - `EditorStateCommands.cpp`, with new `renderStats` keys such as `localShadowRequested` and
      `localShadowTileSizeCounts`.
  - `agent/wave8-rc-world` changes `RendererQuality.h` (the GI row's memory) and `SceneRenderData.h`.
  - The Roadmap (1621, 1632) plans more frame passes: the GI "join" in tranche 2 (shading from the gathers) and
    volumetric fog in tranche 3.
  - The excerpt tool will catch moved quotes, but not prose: tables of rows, lists of passes and stats keys that were
    written by hand.
- **Proposal**:
  - Add a mark `W8r` ("written in phase A, revised in phase B step 7 together with the W8 pages") on `gpu/frame-tour`,
    `image/quality-settings`, `make/look` and `make/big-scenes-fast`.
  - Make the `reference/renderer` tables generated-only.
  - Allocate local shadow views' culling to `light/local-shadows` (M5) so that `draw/gpu-driven` needs no mark.
  - Change step 7 to "The W8 pages are written and the W8r pages revised".
  - Marked W8 but not needing to wait, in these three areas: none. The Slang conversion (`gpu/shaders`) landed in step 0
    (Roadmap 1572), and the HZB fix of `draw/occlusion` and the drawn transforms of `draw/render-scene` are on main.

### M8. The W8 scope omits wave 8 streams that may land in 0.8.0, and one "does not do" claim depends on them

- **Where**: `README.md` line 28; `book.md` line 96.
- **Problem**: README says wave 8 still changes "local lights, area lights, global illumination". The Roadmap also
  plans:
  - tranche 2 `animation-graph` (line 1616: "Blend1D, masked layers and state machines as nodes", the "first claim on
    the tranche");
  - tranche 3 `volumetric` (line 1632, a froxel fog pass) and `showcase-engine` (line 1634, material layers).
  - If tranche 2 lands, `book.md`'s "blend trees, animation layers" becomes false. Volumetric fog would change
    `light/fog` and `gpu/frame-tour`.
- **Proposal**: in README decision 5, write "local lights, area lights, global illumination, and, if they land, the
  animation graph, volumetric fog and material layers". In `book.md`, mark the "does not do" items that touch these
  streams "re-check at v0.8.0" and add them to the pin tool's list for step 6.

### M9. The prerequisites of parts 6 and 7 omit pages their material needs

- **Where**: outline-2 lines 45 and 65.
- **Problem**:
  - Part 7 takes "part `gpu` up to `gpu/frame-tour`", which leaves out `gpu/readback-timing`. Yet:
    - `draw/gpu-driven` reads `CullCounters` back 2-3 frames late (render-scene 1.7);
    - `draw/visibility-feedback` is a readback (1.9);
    - `draw/render-scene` places proxies at drawn transforms (1.1, which needs `world/interpolation`);
    - extraction runs in parallel chunks on the job system (code #9: `core/jobs`);
    - `draw/skinned` needs `animation/skinning` (book.md line 74's own split) and WhenVisible animators (1.10:
      `animation/culling`);
    - `draw/asset-requests` publishes the sizes mip streaming reads (1.3: `assets/mip-streaming`).
  - Part 6 omits:
    - `basics/build` (`gpu/shaders`: `strata_add_shaders`, re-running configure, custom commands);
    - `basics/threads` (event queries as fences, frames in flight);
    - `basics/bytes` (`gpu/text` parses untrusted binary and UTF-8; std140 alignment);
    - `core/engine-modules` (`GraphicsModule`, render-core code #9);
    - `core/layers-registries` (`RegisterRendererModule`, `SceneOverlayRegistry`, `IAssetGraphics`).
- **Proposal**:
  - Part 6 prerequisites: add `basics/build`, `basics/threads`, `basics/bytes`, `core/engine-modules` and
    `core/layers-registries`.
  - Part 7 prerequisites: "part `gpu` up to `gpu/readback-timing`, `world/scene-graph`, `world/interpolation`,
    `core/jobs`, `assets/residency`".
  - Page prerequisites: `draw/skinned` gets `animation/skinning` and `animation/culling`; `draw/asset-requests` gets
    `assets/mip-streaming`.

### M10. Part 10's prerequisites miss motion vectors and readback, and its engine tutorial needs part 20

- **Where**: outline-3 line 45; `image/tutorial-post-effect` (line 60); `process.md` lines 79-80.
- **Problem**:
  - `image/taa` and `image/motion-blur-dof` need `draw/motion-vectors` (render-image ch. 9-10 prerequisites, concept 14:
    "taught in the render-scene area"). Part 10 lists no part 7 page.
  - `image/pre-exposure` needs the asynchronous `BufferReadback` ring (1.2), which is `gpu/readback-timing`, a page
    after `gpu/frame-tour`.
  - `image/exposure` needs compute (M1).
  - `image/tutorial-post-effect` needs the GPU test conventions (`Tests::GPUContext`, `GetNewErrorCount`,
    `ExactSpecification`, `AddNeutralPostProcess`; engine hands-on 5) and the feature test (`engineering/feature-test`,
    outline-4 line 118). Both are in part 20, which wave 6 writes after wave 5 writes part 10.
- **Proposal**:
  - Part 10 prerequisites: "`gpu/readback-timing`, `gpu/compute`, `draw/motion-vectors`, `light/units-exposure`".
  - Give `image/tutorial-post-effect` the page prerequisites `engineering/feature-test` and the GPU-test home (M13),
    and move the page to wave 6, after `engineering`.

### M11. `reference/renderer` lost the render-scene and render-core references: switches, statistics, services

- **Where**: outline-4 line 137 (`reference/renderer` "Passes, bindings, debug views, quality rows"); `pipelines.md`
  line 130 (generated "renderer: debug view names, quality rows and presets, GPU stages").
- **Problem**:
  - render-scene ch. 15 ("every `SceneRendererSpecification` field of this area, every stat and `renderStats` key") and
    render-core ch. 14 ("the `Renderer` services, fallback textures, samplers, every rule of section 5 in one place")
    were folded into a page whose title and generator cover neither.
  - Lost: the specification switches (`GPUDriven`, `OcclusionCulling`, `VisibilityFeedback`, `FadeLevelsOfDetail`,
    `BatchAcrossMaterials`, `IndirectMode`, `CacheShadowCascades`, `DitherOutput`, `TemporalAntiAliasing`,
    `NewInstanceBytesPerFrame`, `PrefetchDistance`, `HighPriorityScreenFraction`) and the 26+ `renderStats` keys
    (render-scene 1.12, `EditorStateCommands.cpp:228-292`). `renderStats` is a public surface: `viewport.capture` and
    `editor.state` return it to agents, and `make/big-scenes-fast` reads it.
  - Also lost: the device requirements (render-core 1.1) and the fallback textures and samplers (1.3).
- **Proposal**:
  - Retitle the row to "Passes, bindings, switches, statistics, debug views, quality rows, device requirements".
  - Add to `pipelines.md`'s renderer row: "`renderStats` keys (parsed from `EditorStateCommands.cpp`),
    `SceneRendererSpecification` and `SceneRendererStats` fields with their comments (parsed from `SceneRenderer.h`)".
  - Add a hand-checked table of the renderer's rules, each linking its home page.

### M12. `image/why-post` is S, but it is the hub of part 10

- **Where**: outline-3 line 49 (`image/why-post`, C, S).
- **Problem**:
  - The inventory proposed M (ch. 1). The page holds all of render-image 1.1: the HDR target, `SanitizeHDR`,
    `c_MaxExposedValue`, the HDR alpha convention (rule 19), the chain order with `PostSource`/`SelectPostSet`,
    `HDROutput` frames, the fullscreen-pass machinery, `PostProcessData`, the `TonemapConstants` volatile buffer, the
    CPU twins (`PostProcessMath`), GPU stages and stats. It also holds concepts 1-2 and code #1-3.
  - Every later page of the part relies on `PostSource`, the CPU twins and the chain order, the way part 7 relies on
    `gpu/frame-tour`. 1,500 words cannot carry a chain of 15 passes plus the half-float discussion.
- **Proposal**: change the row to
  `| image/why-post | Why images need post-processing, and Strata's post chain | C | M | render-image ch. 1; 1.1 whole; code #1-3 |`
  and say in the part brief that later pages link to it for `PostSource`, the fullscreen pass and the CPU twins.

### M13. Engine-change tutorials have no check, and the GPU-test conventions are homed after their first use

- **Where**: outline-2 `gpu/first-triangle` (line 51); outline-3 `image/tutorial-post-effect` (60); `pipelines.md`
  lines 106-113; `process.md` "Not interfering with the engine's work".
- **Problem**:
  - The tutorial pipeline runs only editor command scripts. Pages "through the UI only" are walked by hand. Nothing
    builds the engine change and runs the test that a tutorial in C++ writes:
    - the triangle tutorial "write[s] a GPU test" (render-core ch. 3);
    - the post-effect tutorial adds a pass, a feature-test value and GPU tests.
  - A textbook tutorial whose code does not compile fails its reader, and the definition of done ("its tutorial has a
    current stamp") cannot be met for these pages.
  - The conventions these tutorials teach (one shared device, zero new validation errors, exact specification) are
    first needed in part 6, but their natural home is `engineering/test-kinds` in part 20.
- **Proposal**:
  - Add an "Engine tutorials" section to `pipelines.md`. The tutorial's change lives as
    `tutorials/<part>/<chapter>.patch` with the doctest names it adds. `tools/tutorials.py run-patch` applies it at the
    pin in the docs project's own clone, configures, builds and runs the named tests, then stamps the result. This
    runs in phase B with the GPU.
  - Add a one-home row: "Writing a GPU test (shared `GPUContext`, error count, pixel readback) | `gpu/first-triangle` |
    `engineering/test-kinds`, `image/tutorial-post-effect`".

### M14. Live figures can never pass the "captured twice, identical" rule

- **Where**: `pipelines.md` line 44 (the Live render kind) and lines 77-78 ("captures twice and requires the two files
  to be identical").
- **Problem**:
  - `research/captures.md` line 444: "Live captures: the jitter phase differs between runs". Live captures need a
    windowed editor and `atFixedStep`/`frames` (captures.md 264-274; `viewport.capture` schema,
    `EditorViewportCommands.cpp:1277-1279`).
  - The affected figures are among the ones that matter most for these areas:
    - TAA in motion and trails (render-image screenshots 20-22);
    - motion blur, `tp.live.*.mb180` (screenshot 24), and adaptation leaving a tunnel (screenshot 6);
    - the LOD cross-fade mid-transition (render-scene screenshot 2: "Single captures turn fades off").
- **Proposal**: in `pipelines.md`, exempt live figures from the identical-twice rule. Instead, take three, require
  the same `fixedSteps` and camera in their stats, and have the photographer judge them by eye, as whole-editor pictures
  are judged. Add `atFixedStep` and `frames` to the recipe.

### M15. The figure rule for parts 8-10 asks for pictures that cannot exist, and a release build would fail on them

- **Where**: outline-3 lines 3-4 ("Every page of parts 8 to 10 has … the effect off and on, its debug view, and a sweep
  of its main setting"); `site.md` plugin "figures" (unshot figures fail a release build).
- **Problem**:
  - `image/pre-exposure` changes no image by design (render-image rule 2; the inventory proposes "0 screenshots
    (diagrams)").
  - Of the 11 debug views (`EditorViewportCommands.cpp:1263-1270`: streaming, lod, mip, motion, shadows, lighting, ao,
    indirect, luminance, albedo, voxels), part 10 has only luminance and motion. None exists for grading, encoding,
    lens effects, spatial AA or DoF.
  - Dither "off" exists only as a code switch (`DitherOutput`, captures.md 660).
  - `image/quality-settings` and `image/tutorial-post-effect` have no single "effect".
- **Proposal**: reword to "Every page of parts 8 to 10 that teaches a visible effect has figures rendered by the
  engine: the effect off and on where it has a switch, its debug view where one exists, and a sweep of its main
  setting; the part brief lists which page gets which". Exempt `image/pre-exposure` (diagrams 3-4 of render-image
  instead).

### M16. The one-home table misses further concepts of these areas that two pages claim

- **Where**: `book.md` lines 56-83.
- **Problem**: besides M4, M5 and M13, each of the following is claimed twice by the inventories, and no row decides it:
  - The depth prepass, the `EQUAL` test and bit-identical positions: render-core concept 26 and rule 22 (frame tour,
    invariant decoration in `gpu/shaders`), render-scene rule 8 (LOD fades in `draw/lod`, velocity in
    `draw/motion-vectors`, skinned in `draw/skinned`).
  - Forward vs deferred vs visibility buffer: render-core concept 26 (frame tour) vs render-direct ch. 5
    (`light/many-lights`, W8, so it would be written last).
  - Mirrored transforms and winding, and float precision with camera-relative rendering: render-core concepts 21-22
    (in its ch. 5 = `gpu/coordinates`) vs render-scene concepts 19-20 (ch. 7 = `draw/mirrors-camera-relative`). Worlds
    pages also claim precision (the 20 km limit).
  - Projection matrices, NDC, reversed-Z, frustum planes, bounding volumes and culling tests: foundation concept 25
    (`basics/math-vectors`, `core/math`) vs render-core concept 20 (`gpu/coordinates`) vs render-scene concepts 4-5
    (`draw/bounds-culling`).
  - The geometry pool: render-core ch. 9 (`gpu/geometry-pool`) vs render-scene ch. 5 (`draw/batching`).
  - Pipeline state objects and the `PipelineKey` cache: render-core 1.6 and concept 18 vs render-scene 1.4.
  - The change logs: render-scene 1.1 (`draw/render-scene`) vs 1.6 (`draw/render-scene-gpu`).
  - GPU stages: foundation `ST_PROFILE_STAGE`/`FrameProfiler` with "GPU stages attached late" (`core/profiling`) vs
    render-core 1.12 (`gpu/readback-timing`).
  - Picking: editor-ui concept 18 (`editor/scene-view`) vs render-core 1.11 (`ReadEntityIDAsync`).
  - The players' graphics options: gamedev 1.15 (`make/levels-saves`), scripting "Graphics options" (`make/gameplay-*`),
    render-image 1.9 and ch. 12 ("and a Graphics menu", `make/look`, `image/quality-settings`).
  - The transparent pass (back-to-front sort, glass first, alpha as transmittance): render-scene 1.4, render-direct
    ch. 12 ("transparent pass basics" as a prerequisite) and render-image 1.1 (the HDR alpha convention).
  - Jitter only on the frame's camera copy: render-core 1.10, render-image rule 14, render-direct (the shadows' fixed
    noise).
- **Proposal**: add these rows.

  | Concept | Home | Others link |
  | --- | --- | --- |
  | Depth prepass, `EQUAL`, invariant positions | `gpu/frame-tour` | `gpu/shaders`, `draw/lod`, `draw/skinned`, `draw/motion-vectors` |
  | Forward, deferred, visibility buffer | `gpu/frame-tour` | `light/many-lights` (owns tiled vs clustered light culling) |
  | Mirrored transforms; float precision and camera-relative rendering | `draw/mirrors-camera-relative` | `gpu/coordinates` (states the CCW convention only), `worlds/*`, `make/large-worlds` |
  | Projection and depth conventions | math: `basics/math-vectors`; GPU conventions and reversed-Z: `gpu/coordinates` | |
  | Frustum planes, bounding volumes, culling tests | `draw/bounds-culling` | `core/math` (the types only) |
  | Geometry pool | `gpu/geometry-pool` | `draw/batching` |
  | Pipelines and the `PipelineKey` cache | `gpu/binding` (retitle "Pipelines and binding: …") | `gpu/frame-tour`, `draw/batching` |
  | Render scene change logs | `draw/render-scene` | `draw/render-scene-gpu`, shadow caches |
  | GPU timestamps and stages | `gpu/readback-timing` | `core/profiling` (shows them) |
  | Picking | `editor/scene-view` | `gpu/readback-timing` (the one-pixel async readback) |
  | Players' graphics options | use: `make/levels-saves`; mechanism: `image/quality-settings` | `make/look`, `make/gameplay-*` |
  | Transparent pass | `draw/batching` | `light/clearcoat-transmission`, `image/taa` (reactive mask) |
  | Jitter on the frame's camera copy only | `image/taa` | `gpu/frame-tour`, `gpu/debug-drawing`, shadows |

### M17. "What Strata does not do" misses the rendering absences readers will look for

- **Where**: `book.md` lines 93-99.
- **Problem**: the existing rendering items were checked and are right:
  - no particle, decal, water or terrain code in `Strata/src` (grep for `Particle`, `Decal`, `Water`, `Terrain`,
    `HeightField`: none);
  - no HLOD or origin rebasing (none; Roadmap "Later" 1690-1694 lists `vfx`, HLOD and `world-environment`).

  Missing, each verified at `822a7a46`:
  - **MSAA**: `SceneRenderer.cpp:2767` refuses targets with `sampleCount != 1`; no other sample count exists; Roadmap 944
    and 1670 list MSAA as later.
  - **HDR display output** (HDR10, scRGB): `VulkanGraphicsDevice.cpp:1131-1136` picks only
    `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR`.
  - **Rendering below native, dynamic resolution, temporal upscalers** (DLSS, FSR, TSR): a policy (Roadmap 1642). It
    is stated in book.md's decisions, but readers look for it under "does not do".
  - **Post-process volumes** (local, blended): `SceneRenderer.cpp:1447-1455`. The first active `PostProcessComponent`
    wins; it has no shape and no blending.
  - **Hardware ray tracing, mesh shaders and meshlets, virtual texturing, a render graph**: none in `Strata/src` (grep
    for `rayQuery`, `AccelerationStructure`, `Meshlet`, `sparseBinding`, `RenderGraph`/`FrameGraph`: none). Passes
    are ordered by hand in `RenderFrame`.
  - **Complex-script text shaping and CFF fonts**: render-core 1.14 ("no complex scripts"); `FontValidation` rejects CFF.
  - **Compute or dual-quaternion skinning**: Roadmap 675 ("compute skinning … is later work").
  - **Per-LOD mesh streaming**: Roadmap 1691 (`mesh-streaming`).
  - **Volumetric fog and light shafts**: Roadmap 948 (tranche 3, may land; see M8).
  - **Debug drawing from scripts**: no host function in `StrataScriptCore/Include/StrataScript/*.h`. render-core's
    game hands-on 2 assumes it.
- **Proposal**: add these items to the list, each with its evidence line, and keep the check-at-pin-move note.

---

## Minor findings

### m1. `image/motion-blur-dof` packs two multi-pass algorithms into one L page

- **Where**: outline-3 line 58; `book.md` line 72.
- **Problem**:
  - Motion blur is 3 compute shaders (tile max, neighbor max, gather), a CPU profile model, shutter-angle and cut rules
    (render-image 1.7, concept 16, diagram 19).
  - Depth of field is 5 shaders (prepare, tiles, dilate, gather, composite), thin-lens CoC math, `CameraLens::FromEntity`,
    five `CameraComponent` fields and the composite's stability under TAA (concept 17, diagram 20).
  - TAA alone gets XL. Beginners must also learn optics for DoF.
- **Proposal**: split the page into `| image/motion-blur | Motion blur | I | M |` and
  `| image/depth-of-field | Depth of field | I | L |`. Point the one-home row "Depth of field" at `image/depth-of-field`.

### m2. `image/grading` is M for a page of color science

- **Where**: outline-3 line 53.
- **Problem**:
  - The inventory proposed L (ch. 5). Its content: CIE 1931 xy and 1960 uv, the Planckian and daylight loci, mireds,
    CAT02 von Kries in double, ASC-CDL slope/offset/power on scene-linear light, 3D LUT domain and half-texel addressing.
  - It also holds the `ColorLookup` asset: the `STLU` format, the `.cube` importer with its `Size` setting, and
    asynchronous binding through dummies (render-image 1.4, concept 9, diagram 8, rule 25).
  - `basics/color` (line 77) promises only "linear, sRGB, HDR", so the page must teach chromaticity from zero.
- **Proposal**: make it L. Add "chromaticity, white point and gamut" to `basics/color`'s learn lines.

### m3. The debug-views row homes all debug views on a lighting page

- **Where**: `book.md` line 71.
- **Problem**: four of the 11 views are not about light: `streaming`, `lod`, `mip` and `motion`
  (`EditorViewportCommands.cpp:1263-1266`, tints from `StreamingView.cpp`; render-scene 1.12; render-core
  screenshot 4: "overlay-based debug views").
- **Proposal**: split the row.

  | Concept | Home | Others link |
  | --- | --- | --- |
  | Lighting views (lighting, ao, indirect, luminance, albedo, shadows, voxels) | `indirect/measuring-light` | |
  | Drawing views, the mechanism | `gpu/debug-drawing` | |
  | Drawing views, how to read each | `draw/lod`, `assets/mip-streaming`, `draw/motion-vectors` | |

### m4. Sampling and aliasing are homed in part 10 but needed in parts 7-9

- **Where**: outline-3 `image/spatial-aa` (line 56) and `indirect/energy` (line 34: "specular anti-aliasing").
- **Problem**: render-image concept 12 (pixels as samples, Nyquist, geometric, shading and temporal aliasing) is the
  first teaching of aliasing. Yet `light/shadow-basics` (shadow aliasing), `indirect/energy` (specular AA) and
  `draw/lod` (distant meshes "waste triangles and alias", render-scene concept 8) all come earlier.
- **Proposal**: home "pixels as samples and the kinds of aliasing" in `gpu/how-a-gpu-frame-works` (or `basics/gpu`,
  M6), next to rasterization. `image/spatial-aa` then keeps the AA techniques and links back.

### m5. Screen fraction is homed after the pages that use it first

- **Where**: outline-2 `draw/lod` (line 74), with `draw/bounds-culling` (71) and `draw/asset-requests` (72) before it.
- **Problem**:
  - render-scene ch. 6 puts the screen fraction first in `draw/lod`.
  - Size culling (`MinProjectedPixels`, 1.2) in `draw/bounds-culling` and request priorities by screen fraction (1.3)
    in `draw/asset-requests` use it two and one pages earlier.
  - Concept 7 says the fraction serves LOD, priority, size culling and texture streaming.
- **Proposal**: home the screen fraction (`GetScreenFraction`) in `draw/bounds-culling` in a section "How big does it
  look?". `draw/lod`, `draw/asset-requests` and `assets/mip-streaming` link to it.

### m6. Strata's design decisions have no named homes, and one omits the engine's own exception

- **Where**: `book.md` lines 85-91.
- **Problem**:
  - "Stated once … on its home page", but no page is named for any decision.
  - "nothing may need history (TAA) to look right" omits the named exception the engine documents: Medium's
    Checkerboard screen-space reflections need TAA (Roadmap 951-953, kept in wave 8). The book would state something
    false, against style.md's "Never promise what the engine does not do".
- **Proposal**: add a column of homes:
  - no history: `image/taa`, with the Checkerboard exception and a link to `indirect/ssr`;
  - never below native: `image/quality-settings`;
  - off is bit-for-bit invisible and free: `gpu/frame-tour`;
  - real units and pre-exposure: `light/units-exposure`;
  - deterministic parallel work: `core/jobs`;
  - fixed steps: `core/time`;
  - GI traces the world: `indirect/problem`;
  - measured trade-offs: `engineering/perf-lab`.

### m7. Numbers in figures have no source in the recipe

- **Where**: `pipelines.md` lines 49-71 (the recipe).
- **Problem**: several figures of these areas are numbers, not pixels:
  - render-scene screenshots 4, 5, 8 and 9: `opaqueDraws` = 1 for 1,000 materials, `occludedProxies`, `cachedCascades`;
  - render-image screenshot 4 (`exposure.keyStops`);
  - captures.md line 375 says GPU-driven figures "quote `renderStats`".
  - The recipe records only images and hashes, so caption numbers go unchecked against the engine.
- **Proposal**:
  - Add a recipe field `"stats": ["renderStats.opaqueDraws", …]`. The tool stores the values in `taken.stats`, and
    captions write `{stats.opaqueDraws}`, which the figures plugin fills.
  - Add a check that fails when a caption has a number with no stats source and no reference-machine note.

### m8. The renderer's `TextComponent` has no use-side home, and the text row splits the wrong way

- **Where**: outline-1 `make/ui` (line 51); `book.md` line 73 ("`ui/text` (layout only)").
- **Problem**:
  - World-space sign text and screen HUD text without a canvas (`TextComponent`, `TextRenderer`; render-core 1.14 and
    game hands-on 3) are in neither the gamedev nor the gameui inventory (`make/ui` has only `UITextComponent`).
  - `ShapeText`/`LayoutText`, which do the line breaking, alignment and ellipsis, live in the renderer
    (`R/TextLayout.h`, render-core 1.14). So "layout" belongs to `gpu/text`, not to `ui/text`.
- **Proposal**:
  - Add "render-core 'Text and fonts' (`TextComponent`: text without a canvas)" to `make/ui`'s From column.
  - Reword the row to "`gpu/text` (fonts, `ShapeText` layout, atlas, SDF) | `ui/text` (how rects, sizes and overflow
    modes drive `ShapeText`), editor".

### m9. The Renderer's service hub and frame debugging have no home

- **Where**: outline-2 `gpu/vulkan-nvrhi` (line 50).
- **Problem**:
  - render-core 1.3 (the `Renderer` static hub: samplers, fallback textures with the flat-normal half-float story,
    `BeginFrame`, `PrepareBackBuffer`, the frame number) and 1.2 (`GraphicsModule`, back-buffer capture) name no page.
    Code #9-11 are listed as worth showing.
  - Reading a frame in RenderDoc or Nsight (render-core hands-on 12; markers exist in `RenderFrame`) has no page. The
    curricula checklist marks "Validation layers, debug names, GPU debuggers (RenderDoc), reading a frame capture" as
    **[gap]**.
- **Proposal**:
  - Retitle `gpu/vulkan-nvrhi` to "Vulkan, NVRHI, the graphics device and the Renderer's services" and allocate 1.2-1.3
    to it.
  - Add a section "Looking inside a frame: validation messages, markers and a frame capture" to `gpu/frame-tour`. A
    reviewer checks it in phase B on the GPU.

---

## Further notes (file only)

- **Generated tables of the engine have no named home.** `outline-4.md` line 115 (`engineering/generated-code`: "shaders,
  embedded files, version stamps") does not name the committed generator outputs of render-image 1.11 and rule 11:
  `Tools/FitFilmic.py`, `GenerateWhiteBalance.py`, `GenerateAreaTable.py`, `GenerateBlueNoise.py`, and the LTC
  conversion on the area-lights branch. Retitle it to "Generated code: shaders, embedded files, committed tables,
  version stamps".
- **`image/encoding` runs before `image/spatial-aa`.** But the encoding page must say that FXAA or the morphological
  pass dithers and adds grain when it follows the tone map, and that the 10-bit intermediate exists for them (1.5).
  Keep the order (FXAA needs encoded luma), and give the encoding page a forward sentence. No change to the outline.
- **`draw/visibility-feedback` (M) is thin** (four feature rows, 0 screenshots in the inventory). It is still worth a
  page, because it needs `draw/gpu-driven` first and cannot merge into `draw/asset-requests`. It could be S.
- **The ImGui NVRHI backend** (render-core section 9) is the second real NVRHI example; `editor/imgui-backends` should
  link `gpu/vulkan-nvrhi` as its prerequisite.
- **Thumbnails force the CPU path** (`SceneRenderer.cpp:248-251`, render-scene section 9), and the shadow cascade
  cache works on the GPU path only (Roadmap 675-677). Both facts belong on `draw/gpu-driven` and
  `light/sun-shadows-1`, and both affect the figures: a figure of the cache must be taken on the GPU path.
- **The GPU-driven path has not run on CI GPUs** (render-scene section 9: Releases 0.4.0 and 0.5.0). The figure
  machine's GPU must be named in `reference/figures`.

---

## Coverage walk (condensed)

Legend: page = the item's plausible home; **gap** = no home; **2x** = two homes; **order** = home after first use.

### render-core

| Section | Home | Note |
| --- | --- | --- |
| 1.1 device, swapchain, pacing, validation, MoltenVK, memory budget | `gpu/vulkan-nvrhi`; timestamps → `gpu/readback-timing`; queue transfers → `gpu/upload-queue` | |
| 1.2 `GraphicsModule`, back-buffer capture, frame order | `gpu/vulkan-nvrhi`, `gpu/readback-timing`, `core/frame-loop` | m9 |
| 1.3 `Renderer` hub, samplers, fallback textures | **gap** | m9, M11 |
| 1.4 command lists, barriers, deferred release, event queries | `gpu/resources-lifetimes`; command lists → `gpu/how-a-gpu-frame-works` | |
| 1.5 uploads and staging | **2x** `gpu/upload-queue` / `assets/uploads` | M6 |
| 1.6 pipelines, layouts, bindless, texture table | `gpu/binding`; PSO/`PipelineKey` **2x** | M16 |
| 1.7 textures, meshes, geometry pool, `MeshFactory` | `gpu/geometry-pool` (**2x** `draw/batching`); textures → `assets/textures` | M16 |
| 1.8 shaders | `gpu/shaders`; compute model **gap** | M1 |
| 1.9 coordinates | `gpu/coordinates`; mirrored, camera-relative **2x** `draw/mirrors-camera-relative` | M16 |
| 1.10 the frame | `gpu/frame-tour` (W8r) | M7 |
| 1.11 readback, picking | `gpu/readback-timing`; picking **2x** `editor/scene-view` | M16 |
| 1.12 GPU timing | `gpu/readback-timing` (**2x** `core/profiling`) | M16 |
| 1.13 overlays, gizmos, overlay registry | `gpu/debug-drawing`; `LODSelection` → `draw/lod` | |
| 1.14 text and fonts | `gpu/text`; `TextComponent` use **gap** | m8 |
| 1.15 registration | `core/layers-registries` (as the example) | |
| Concepts 1-32 | all mapped; 18 (PSO) weak; compute **gap**; float precision **gap** | M1, M2 |
| Rules 1-37 | all mapped; 31 (GPU tests) **order** | M13 |
| Ch. 14 reference | **lost** in `reference/renderer` | M11 |

### render-scene

| Section | Home | Note |
| --- | --- | --- |
| 1.1 render scene | `draw/render-scene`; light records → `light/many-lights` | M5 |
| 1.2 spatial index, CPU culling | `draw/bounds-culling`; shadow casters **2x** | M5 |
| 1.3 requests, resolve cache | `draw/asset-requests` | m5 |
| 1.4 batching | `draw/batching`; geometry pool **2x**; transparent pass **no row** | M16 |
| 1.5 LOD | `draw/lod`; screen fraction **order** | m5 |
| 1.6 GPU copy | `draw/render-scene-gpu` | |
| 1.7 GPU-driven | `draw/gpu-driven`; local shadow views → `light/local-shadows` (unassigned) | M5, M7 |
| 1.8 occlusion | `draw/occlusion`; cascade occlusion and cache **2x** | M5 |
| 1.9 feedback | `draw/visibility-feedback` | |
| 1.10 skinned | `draw/skinned`; prerequisites missing | M9 |
| 1.11 mirrors, camera-relative, motion | `draw/mirrors-camera-relative`, `draw/motion-vectors` | |
| 1.12 `renderStats`, debug views, quality rows | use: `make/big-scenes-fast`; reference **lost**; debug views misassigned | M11, m3 |
| Concepts 1-22 | mapped; 7 **order**; 22 (determinism) decision without home | m5, m6 |
| Rules 1-24 | mapped; 12 (shadow cache versions) **2x** | M5 |
| Ch. 15 reference | **lost** | M11 |

### render-image

| Section | Home | Note |
| --- | --- | --- |
| 1.1 HDR and chain | `image/why-post` (too small) | M12 |
| 1.2 exposure | `image/exposure`, `image/pre-exposure`; EV100 and units **2x** `light/units-exposure` | M4 |
| 1.3 tone curves | `image/tone-mapping` | |
| 1.4 color, LUT asset | `image/grading` (thin); sRGB **2x** | m2, M4 |
| 1.5 display output | `image/encoding` | |
| 1.6 lens and film | `image/lens-effects`; grain → `image/encoding` | |
| 1.7 motion blur, DoF | `image/motion-blur-dof` (two algorithms) | m1 |
| 1.8 AA, TAA | `image/spatial-aa`, `image/taa`; aliasing concept **order** | m4 |
| 1.9 quality, players' options | `image/quality-settings` (W8r); players' options **2x/3x** | M7, M16 |
| 1.10 component, test helpers | `reference/components`; helpers → `image/tutorial-post-effect` | |
| 1.11 generators | `engineering/generated-code` (not named), `engineering/look-dev` | note |
| Concepts 1-18 | mapped; 2 (floats) **gap**; 3 **2x**; 12 **order** | M2, M4, m4 |
| Rules 1-26 | mapped; 24 (native resolution) decision without home | m6 |
| Ch. 1 M→S, ch. 5 L→M, ch. 10 two topics, ch. 14 → generated reference | | M12, m2, m1 |

---

## W8 for these areas (summary of M7 and M8)

| Page | Marked | Should be | Evidence |
| --- | --- | --- | --- |
| `gpu/frame-tour` | no | W8r | `agent/wave8-local-lights`: `SceneRenderer.cpp`/`.h`; Roadmap 1621, 1632 (GI join, volumetric) |
| `image/quality-settings` | no | W8r | local-lights: `RendererQuality.h` new row, `c_SectionVersion` 7; rc-world: GI row |
| `make/look` | no | W8r | presets table follows `RendererQuality` |
| `make/big-scenes-fast` | no | W8r | local-lights: new `renderStats` keys in `EditorStateCommands.cpp` |
| `draw/gpu-driven` | no | none, if local shadow culling goes to `light/local-shadows` | local-lights: `Cull.comp.slang`, `SceneRendererGPUDriven.cpp` |
| `image/exposure` | no | none (one sentence re-check) | local-lights: `AdaptationSeconds` also drives shadow fades |
| `reference/renderer` | n/a | generated at v0.8.0 | — |
| `gpu/shaders` | no | none | Slang landed in step 0 (Roadmap 1572) |
| `draw/occlusion` | no | none | the HZB fix is on main (render-scene 1.8) |
