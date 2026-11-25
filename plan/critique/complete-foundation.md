# Critique: completeness against the survey (foundation, build-test, scene-ecs, assets)

Key: `complete-foundation`. Lens: for the inventories `foundation.md`, `build-test.md`, `scene-ecs.md` and `assets.md`
(read whole), does every item have a home page a reader would look in, are the pages sized for what they hold, did
merges lose material, are prerequisites and order right, does "one home per concept" hold, is "What Strata does not
do" true, and which pages depend on wave 8. Engine evidence was read at `822a7a46` (read-only).

Line numbers below are per plan file (`book.md`, `outline-1.md`... counted from 1 in each file).

## Verdict

Every item of the four inventories has a plausible home somewhere in the outline, so nothing has to be added as a new
subject. What the plan gets wrong is where the pages sit relative to each other. Part 5 (assets) and part 20
(engineering) list prerequisites that leave out pages their material needs. The writing waves write `assets` before
`gpu`, which the assets pages depend on. Part 4 pages need assets pages that come after them. Three pages are given a
kind (concept) that cannot hold the internals the inventories put in them. And about ten concepts are still claimed by
two or more pages, one of them the pilot page `core/time`. **Fix first: the prerequisites of parts 4, 5 and 20 and the
wave order in process.md.** Writers in wave 3 will otherwise re-explain staging, bindless slots and frames in flight,
which breaks the one-home rule before the editor pass can catch it.

---

## Findings (most severe first)

### F1 (major): Part 5's prerequisites leave out the GPU and color pages; the wave order writes assets before gpu

**Where:** `outline-2.md` line 25 ("Prerequisites: `basics/bytes`, `basics/threads`, `core/jobs`, `world/ecs`");
`process.md` lines 73-79 (waves 3 and 5).

**Problem.** The assets inventory's own chapter plan names GPU prerequisites: ch. 4 textures "basic graphics (texture
sampling) from the rendering primer", ch. 9 uploads "GPU command submission basics (rendering primer)", ch. 10 mip
streaming "the render scene chapter for view reports" (assets.md §8, lines 752-772). The material needs these pages
too:
- `assets/textures`: sRGB filtered in linear space and HDR RGBA16F (concept 5) need `basics/color`.
- `assets/residency`: room before arrival waits "frames in flight + 1" before allocating GPU memory (§1.5, concept 16,
  rule 21), so it needs `gpu/how-a-gpu-frame-works` and `gpu/resources-lifetimes`.
- `assets/uploads`: staging buffers, fences and the transfer queue (§1.11) need `gpu/upload-queue`, which is the
  mechanism's home in `book.md` line 64.
- `assets/mip-streaming`: bindless slots resolved every frame (rule 18, §1.11 last row) and `ReportView` from the
  render scene need `gpu/binding` and `draw/asset-requests`.

`process.md` writes `assets` in wave 3 and `gpu`/`draw` in wave 5. This breaks its own rule ("an order where
prerequisites are written before the pages that need them"). The assets writers would get only outline rows for
staging and bindless, and would explain them again.

**Proposal.**
- Change line 25 to: "Prerequisites of the part: `basics/bytes`, `basics/color`, `basics/threads`, `core/jobs`,
  `core/layers-registries`, `world/ecs`, `world/reflection`; per page: `assets/residency` and `assets/uploads` +
  `gpu/how-a-gpu-frame-works`, `gpu/resources-lifetimes`, `gpu/upload-queue`; `assets/mip-streaming` + `gpu/binding`,
  `draw/asset-requests`; `assets/references` and `assets/packs-export` + `world/serialization`."
- In `process.md` wave 3, write only `assets/what-is-an-asset` to `assets/references`, `assets/packs-export`,
  `assets/robustness` and `assets/extending`. Move `assets/textures`, `assets/uploads` and `assets/mip-streaming` to
  wave 5, after `gpu`. No cycle results: `gpu` needs no assets page (outline-2 line 45), and `draw` needs only
  `assets/residency`.

### F2 (major): Part 4 pages need assets pages and engine pages that the part does not list; the E track's order cannot hold

**Where:** `outline-2.md` line 7; `book.md` line 29 (track E: "... *Scenes*, then any subsystem part").

**Problem.**
- `world/serialization` uses `SceneAsset`, asset loaders, `AssetHandle`, and `SceneLoader` pinning a dependency
  closure. The inventory lists "asset pipeline basics (handles, loaders), job system" as prerequisites of ch. 8
  (scene-ecs.md line 722).
- `world/prefabs` is about `EntityTemplate`, an asset base class with Prefab and Model loaders (§1.10).
- `world/sub-scenes` uses `LoadSubScene(asset)` and residency (§1.8).
- Other prerequisites are missing too. Quaternions for TRS, decomposition and nlerp (concepts 6 and 24: "the book's
  math chapter must precede this") need `basics/math-rotations`. The parallel world-transform walk and the parallel
  document writer (concept 8, excerpts 8 and 28) need `core/jobs`. Ch. 4 asks for "the application frame loop chapter"
  (`core/frame-loop`). The registry freeze and scene services as dependency inversion (concepts 13-14, §1.12) need
  `core/layers-registries`. `ComposeWorldTransform` is `core/math`'s.

A reader who follows track E and reads Scenes whole before Assets meets assets terms that have not been defined.

**Proposal.**
- Change line 7 to: "Prerequisites of the part: `basics/computer`, `basics/cpp`, `basics/math-vectors`,
  `basics/math-rotations`, `basics/threads`, `core/map`, `core/frame-loop`, `core/time`, `core/layers-registries`,
  `core/jobs`, `core/math`; per page: `world/serialization`, `world/prefabs` and `world/sub-scenes` +
  `assets/handles-meta`, `assets/loading`."
- Change book.md line 29 to "*Scenes* up to `world/reflection`, *Assets* up to `assets/loading`, the rest of *Scenes*,
  then any subsystem part". No page cycle results: `assets/loading` needs only `world/ecs` from part 4.

### F3 (major): Part 20 lists only `basics/build`; its pages need architecture, GPU, editor, reflection and scripting pages

**Where:** `outline-4.md` line 107.

**Problem.** The build-test inventory names a prerequisite for each of its chapters (build-test.md lines 704-740):
- ch. 3 CMake: "the architecture chapter's layers concept" (`core/layers-registries`)
- ch. 6 generated code: "a shader primer" (`gpu/shaders`)
- ch. 8 test kinds: `GPUContext`, NVRHI, validation, "editor commands chapter for command scripts"
  (`gpu/vulkan-nvrhi`, `editor/command-scripts`)
- ch. 9 feature test: "component/registry and scripting chapters" (`world/reflection`, `scripting/abi-sdk`; it counts
  host functions and SDK names)
- ch. 10 perf lab: percentiles and frame stages (`core/profiling`)
- ch. 11 look-dev: "rendering basics" (`gpu/frame-tour`)

**Proposal.** Keep the part line, and give the pages these prerequisites:
- `engineering/cmake`: + `core/layers-registries`
- `engineering/generated-code`: + `gpu/shaders`
- `engineering/test-kinds`: + `gpu/vulkan-nvrhi`, `editor/command-scripts`
- `engineering/feature-test`: + `world/reflection`, `scripting/abi-sdk`
- `engineering/perf-lab`: + `core/profiling`
- `engineering/look-dev`: + `gpu/frame-tour`

### F4 (major): `core/time` (a pilot page) and `world/interpolation` both claim interpolation

**Where:** `outline-1.md` line 89 (title "Time: delta time, the fixed step and interpolation"); `book.md` line 59
(interpolation's home is `world/interpolation`); `style.md` line 38 uses the same title in its front-matter example.

**Problem.** The one-home table gives interpolation to `world/interpolation`, but the pilot page's title promises it.
The foundation inventory's ch. 4 also lists interpolation (foundation.md line 657). The pilot is meant to set the
pattern for every later page, so it would set this overlap too.

**Proposal.** Pick one of the two:
- (a) Retitle `core/time` "Time: delta time, the fixed step and time scale". It names interpolation in one paragraph
  and links. Fix the example in `style.md` line 38 to match.
- (b) Keep the title and reword book.md line 59 to "Interpolation: the idea (interpolate vs extrapolate, one step of
  latency) `core/time`; Strata's interpolated set, roles and drawn transforms `world/interpolation`".

(a) is cleaner.

### F5 (major): The layer table as the build, optional modules and the no-tooling proof are claimed by `core/layers-registries` and `engineering/cmake`

**Where:** `book.md` table (lines 56-79), no row; `outline-1.md` line 92; `outline-4.md` line 112.

**Problem.** Both inventories own the same subject:
- Foundation §1.10 ("Layers as the build": layer table, per-layer libraries, `Architecture.*` tests, `ExternalOwners`,
  tooling-free runtime), concepts 11-12, rules 10-11, and its ch. 7 ("`Layers.json` as the build, enforcement tests,
  ..., optional modules, tooling-free games").
- Build-test §1.3 (`strata_add_layer_libraries`, link closure, linker map), concepts 12-13, rules 8-10, and its ch. 3
  ("targets, layers and the 'no tooling in games' proof").
- Both draw the same figure: foundation figure 2 (the layer DAG) and build-test figure 3 (layer table to libraries).

**Proposal.** Add the row: "Layer table, optional modules (`ST_WITH_*`), no tooling in games | rules, the why and the
tests: `core/layers-registries`; the CMake that enforces them (`strata_add_layer_libraries`, link-closure walk, linker
map, `LayerLibraries.json`): `engineering/cmake` | scripting, worlds/export".

### F6 (major): The shader build is claimed by `gpu/shaders`, `engineering/generated-code`, `engineering/third-party` and `engineering/ci`

**Where:** `book.md` table, no row; `outline-2.md` line 49 (`gpu/shaders` "Slang, the build and the dialect");
`outline-4.md` lines 114-115, 121.

**Problem.**
- Render-core inventory rows 120-124 claim `strata_add_shaders`, the slangc to StrataShaderTool to registry pipeline
  and the Slang pin, and its ch. 4 covers "the build".
- Build-test §1.4 claims the same pipeline (shader build, slangc flags, StrataShaderTool, embedded registry), §1.5
  claims the Slang pin, and §1.11 claims the shader checks (spirv-val, Metal conversion, `StrataShaders.TargetHLSL`).

So four pages claim one pipeline.

**Proposal.** Add the row: "Shader build | writing and registering a shader, the dialect and its checks: `gpu/shaders`;
the CMake custom commands, `StrataShaderTool`'s SPIR-V patch, the generated registry: `engineering/generated-code`;
Slang's pinned download: `engineering/third-party`; the CI shader steps: `engineering/ci` | (each links the others in
one sentence)". Also add `gpu/shaders` as a prerequisite of `engineering/generated-code` (F3).

### F7 (major): Reversed Z, projections, frustums and AABBs are claimed by four pages

**Where:** `book.md` table, no row; `outline-1.md` lines 77 (`basics/math-vectors`), 97 (`core/math`); `outline-2.md`
lines 50 (`gpu/coordinates`), 68 (`draw/bounds-culling`).

**Problem.**
- Foundation §1.8 and concept 25 give `core/math` and the math primer projections, reversed Z, frustum plane
  extraction, `AABB::Transformed` and ray tests (excerpt 29: `Math.cpp` 71-91, `Frustum.cpp`).
- Render-core row 138 and concept 20 teach reversed Z from the same `Math.cpp` lines for `gpu/coordinates`.
- Render-scene lines 235-239 teach `AABB::Transformed` and the positive-vertex test for `draw/bounds-culling`.
- Neither `world` nor `draw` lists `core/math` as a prerequisite.

**Proposal.** Add the row: "Projections and reversed Z | math: `basics/math-vectors`; Strata's conventions and depth
precision: `gpu/coordinates`; the code (`PerspectiveReverseZ*`, `Ray::FromNDC`): `core/math`" and the row "Frustum
and AABB tests | `draw/bounds-culling` (plane extraction, positive vertex, `AABB::Transformed`) | `core/math` lists
them in one paragraph". Add `core/math` to the prerequisites of parts 4 and 7. The `ComposeWorldTransform`/FMA rule
(foundation rule 26) stays at `core/math`, and `world/scene-graph` links to it.

### F8 (major): Export, pack planning and cooked scenes have no single home

**Where:** `book.md` table, no row; `outline-2.md` lines 18, 39; `outline-4.md` line 168; `outline-1.md` line 57.

**Problem.**
- Pack planning and pruning (`PlanAssetPack`, first-use order, `Prune`, `AlwaysInclude`) is assets §1.9. The
  worlds-runtime ch. 8 for `worlds/export` claims "pack planning and pruning" too (worlds-runtime.md line 593), and
  assets §1.12 lists `GameExport` itself.
- The cooked scene format STSC (scene-ecs §1.9, `CookedScene.h`, its validation and the `CookedSceneTests.cpp` rule)
  is claimed by `world/serialization`. Assets §1.9 "Cooking documents for packs" (`CookForPack` writes `CookedScene`)
  pulls it into `assets/packs-export`.

**Proposal.** Add two rows:
- "Export | the pack (format, planning, pruning, `AlwaysInclude`, patches): `assets/packs-export`; the export as a
  whole (`GameExport`, manifest, executable, icon, checks): `worlds/export`; use: `make/export`".
- "Cooked scenes (STSC) | format and validation: `world/serialization`; when and why the export cooks them:
  `assets/packs-export`".

### F9 (major): Prefab overrides fall between `world/prefabs` and `editor/prefab-instances`

**Where:** `book.md` line 62.

**Problem.** Scene-ecs §1.10 and its ch. 9 claim `PrefabInstances.h` and `PrefabOverrides.h` (`ComputeOverrides`,
`UpdateOverrides`, `Propagate`, `Revert`, `ApplyToPart`, version/hash catch-up). editor-core row 179 claims the same
`PrefabOverrides.h` API. The row "data model / instance sync" does not say which page explains overrides and
propagation.

**Proposal.** Reword the row: "Prefabs | use: `make/prefabs`; data model, overrides and propagation (the Scene-layer
code: `EntityPrototype`, instantiation, `PrefabInstances`, `PrefabOverrides`): `world/prefabs`; keeping them exact while
editing (`PrefabSync`, `UpdatePrefabOverrides` in `CommitEdit`, baselines, apply/revert as undo steps):
`editor/prefab-instances`".

### F10 (major): "What Strata does not do" leaves out limits the engine's own release notes state, several in these areas

**Where:** `book.md` lines 93-99.

**Problem.** These limits are checked against the engine at `822a7a46`:
- **OBJ and FBX import:** only glTF models are imported (`Strata/src/Strata/Asset/AssetImporters.cpp:159-177`
  registers native ×5, Texture, glTF, AudioClip, Font, ColorLookup). `Docs/Releases/0.7.0.md:414` lists "OBJ and FBX
  import" as not in the release. Game makers look for this first.
- **HDR compression (BC6H):** `Docs/Releases/0.7.0.md:403` says HDR textures are stored as RGBA16F "until a BC6H encoder
  exists".
- **Prefab edit mode:** `Docs/Releases/0.7.0.md:380`.
- **Mesh streaming:** the only partial-load registration is for textures
  (`Strata/src/Strata/Renderer/RendererRegistration.cpp:93`, the only `RegisterPrefix` call).
- **Virtual texturing / sparse residency:** none in `Strata/src` (assets concept 17 names it as the alternative Strata
  did not take).
- **Custom shaders and material graphs:** there is no shader asset type (`Asset/AssetTypes.h:14-31`), and shaders are
  compiled at build time and embedded (`strata_add_shaders`, `EmbeddedShaders`).
- **Mobile, console and web targets:** `Core/PlatformDetection.h` has an `#error` for everything but 64-bit Windows,
  Linux and macOS.
- **A work-stealing or fiber job system with a frame task graph:** `Docs/Roadmap.md:1705`, "later".
- **Run-time engine plugins:** modules are compile-time (`ST_WITH_*`); only game scripts load at run time.
- **Leaving scripting out of a build:** `Docs/Releases/0.7.0.md:404`.

The claim "nested prefabs and variants" is true: a prefab made from linked entities stores no inner links
(`PrefabInstances::StripLinks`, `Strata/src/Strata/Scene/PrefabInstances.h:129-130`, called at
`StrataEditor/src/Editor/EditorAssetCommands.cpp:1216`).

**Proposal.**
- Add to the list: "OBJ/FBX import; BC6H; a prefab edit mode; mesh streaming and virtual texturing; custom shaders and
  material graphs; mobile, console and web platforms; work stealing, fibers and task graphs; run-time engine plugins".
- Add to the `appendix/not-in-strata` row (`outline-4.md` line 155) the source "`Docs/Releases/0.8.0.md` 'Known
  issues' and 'Not in this release'".

### F11 (major): Wave 8's tranche 2 may make "blend trees, animation layers" false at 0.8.0, and it touches assets pages

**Where:** `book.md` lines 94-97; `outline-3.md` part 12 (no W8 marks); `outline-2.md` line 36; `outline-4.md` line 136.

**Problem.** `Docs/Roadmap.md:1614-1626` and `Docs/Plans/Wave8/plan.md:363,386` plan `animation-graph` ("Blend1D,
masked layers and state machines as nodes", `.stanimator` version 2) as tranche 2, "intended" for wave 8, with "first
claim". Its file list includes `AssetDependencies` (`assets/references`) and `FeatureTest` (`engineering/feature-test`).
If it lands, the "does not do" claims about blend trees and layers are false. `animation/blending`,
`animation/state-machines` and `animation/limits` would describe 0.7.0, and `reference/assets` would miss `.stanimator`
v2.

**Proposal.**
- Mark `animation/state-machines`, `animation/blending` and `animation/limits` "W8 (if tranche 2 lands)".
- Qualify "blend trees, animation layers" in book.md as "checked at the 0.8.0 pin".
- Add `assets/references` and `reference/assets` to the pages re-read at the pin move whatever their quotes say.

### F12 (major): Pages about landed but unreleased wave 8 work need a re-check mark; quote checks will not catch prose

**Where:** `outline-1.md` line 11 (W8 definition); `process.md` Phase B step 6.

**Problem.** In these areas no page needs to wait (W8) for 0.8.0:
- `physics-timing` (interpolation) landed in landing 1, and its rest is deferred to wave 9 (`Docs/Roadmap.md:639-642,
  1698-1702`).
- `Scene.Timing`/`FixedRate`, Slang, the no-GLFW build, `ExternalOwners`, the high-resolution frame pacer, the
  profiler's pause and `BackgroundLogSink` all landed in step 0.

But their prose claims ("Interpolation on by default", "2.1 times, target 1.5, Provisional", Slang's open GPU-time gate
and Mac run at `Docs/Roadmap.md:627`) can change before the release without any quoted line moving. Step 6 re-reads only
pages whose quotes changed.

**Proposal.** Add a second mark "W8L: describes wave 8 work landed before 0.8.0; re-read against
`Docs/Releases/0.8.0.md` at the pin move". Put it on:
- `core/time`, `core/frame-loop`, `core/profiling`, `core/windows-events`, `core/layers-registries`,
  `core/conventions`
- `world/systems`, `world/interpolation`, `world/projects-settings`
- `gpu/shaders`
- `engineering/cmake`, `engineering/generated-code`, `engineering/third-party`, `engineering/ci`

`world/interpolation` must also teach the deferred list at `Docs/Roadmap.md:1698-1702` as its "what it does not do yet".

### F13 (major): `core/conventions` comes eighth, after the pages that quote its rules

**Where:** `outline-1.md` line 93.

**Problem.** The foundation inventory says ch. 8 "can be read early, alongside ch. 2" (foundation.md line 669), and
lists it as a prerequisite of ch. 9 and ch. 11. The code that `core/first-frame` and `core/frame-loop` quote already uses
the conventions:
- `Strata::Scope` (`Engine/EntryPoint.h` 16-41)
- `ST_CORE_VERIFY(!s_Instance, ...)` and `ST_CORE_WARN/ERROR` (`Core/Application.cpp` 67-80)
- the "Engine code does not throw" catch (`Application.cpp` 243-253)

**Proposal.** Move `core/conventions` to the second row of part 3, after `core/map`.

### F14 (major): `core/platform` is M but holds an L chapter plus five concepts

**Where:** `outline-1.md` line 96.

**Problem.** The page is meant to hold:
- Foundation §1.7 (17 rows: `Platform`'s 41 functions, private files, `FileSystem`, `AtomicFileWriter`, `FileReader`,
  `FileLock`, `FileWatcher`, `BoundedRead`, `Process`, `DynamicLibrary`, ...)
- the interrupt, GUI-subsystem and power-throttling rows of §1.2
- concepts 19 and 21-24 (scheduling and power, platform abstraction, program kinds on Windows, text and paths, safe
  file writing and trust)
- excerpts 23-27 and rules 12, 15-17, 22-24

The inventory proposed L with 2 screenshots (foundation.md line 675).

**Proposal.** Split it:
- `core/platform` "Talking to the operating system" (I, L): seams and detection, the `Platform` class, console vs GUI
  programs, signals and exit codes, dialogs, thread priorities, power and sleep precision.
- `core/files` "Files you can trust" (I, M): UTF-8 paths, `FileSystem`, atomic writes, private files and TOCTOU,
  `FileReader`, `FileLock`, `FileWatcher`, `BoundedRead`. It is the home of atomic writes (F19).

### F15 (major): `engineering/testing` is a concept page, so the internals of the test program have no internals page

**Where:** `outline-4.md` line 116.

**Problem.** Inventory ch. 7 is "concept + internals, L" (build-test.md line 720). It covers the test binary, `main`,
helper modes, fake CMake, shards and `Testing.Shards`, labels, fixtures, resource locks, sweeps and the fuzz run,
determinism rules and crash naming (§1.6, about 25 rows; excerpts 19-23). `engineering/test-kinds` takes only ch. 8 (GPU,
end-to-end, package). A concept page has no map, contract or walk-through, and the internals checks (at least three
quotes) do not apply to it.

**Proposal.** Split it:
- `engineering/testing` "Testing an engine" (C, M): test kinds, determinism and flakiness, regression tests that fail
  without the fix, coverage by construction as an idea, sweeps as an idea.
- `engineering/test-program` "Inside StrataTests" (I, L): `TestMain`, helper modes, fake CMake/editor,
  `CoreShards.json` and `Testing.Shards`, labels, fixtures, locks, `SelectSweepOffsets` and `StrataTests.Fuzz`,
  `TestCrashReporter`, test helpers. Place it before `engineering/test-kinds`.

### F16 (major): `assets/textures` is a concept page but holds the texture importer, the cooker and Strata's own BC7 encoder

**Where:** `outline-2.md` line 32.

**Problem.** Inventory ch. 4 is "concept + internals, L" (assets.md line 752). Assets §1.8 gives it:
- the texture importer (settings, defaults from name tokens, version 5), `ChooseFormat`, the Mitchell cooker
- the own BC7 encoder (`BC7Encoder.cpp`, 1,435 lines)
- `HDRSun`, `STTX` v2, `GetMipByteSize`, the BC decode fallback
- excerpts 12-15 and rules 4, 14, 15 (`GetVersion` bumps, block sizes, `ParseCookedTexture`)

All of this is code walked through, which a concept page's shape does not allow.

**Proposal.** Split it:
- `assets/textures` "Textures for the GPU: mips, color spaces, block compression" (C, M): the general problem and the
  formats.
- `assets/texture-cooking` "Cooking textures: Strata's importer, mips and BC7 encoder" (I, L): place it right after
  `assets/textures`.

### F17 (major): `world/serialization` holds both the formats and all of scene loading

**Where:** `outline-2.md` lines 18 and 20.

**Problem.** The page is meant to hold:
- scene-ecs §1.9 (DOM serializer, three-pass read, leniency, unknown components, the parallel streaming writer, the
  event-parser reader with parallel read, sinks, cooked STSC)
- §1.10's `SceneAsset` (prepared scenes read once) and §1.11 (`SceneLoader` state machine, `PrepareSystems`)
- `ReleaseInBackground` and prepared states (§1.1)
- concepts 20, 21 and 23, excerpts 26-29, figures 16-19 and 22, rules 23-26

The inventory's ch. 8 lists nine subjects for one L page. Meanwhile `world/sub-scenes` (M) already holds the slicing
and the `SceneWorkBudget` that scene loads use.

**Proposal.**
- Keep `world/serialization` "Scene documents: text, streams and the cooked form" (I, L) for the formats.
- Retitle `world/sub-scenes` "Loading scenes: whole, additive and in slices" (I, L), and move into it `SceneAsset`'s
  prepared scenes, `SceneLoader` and its states, `PrepareSystems`/`PrepareLoadedScene`, prepared states, the hand-over,
  `RequestSceneLoad` and `ReleaseInBackground`.
- Update the book.md line 63 row to name the new title.

### F18 (minor): `world/interpolation` is M although two inventory chapters merge into it

**Where:** `outline-2.md` line 15.

**Problem.** Scene-ecs §1.7 has 9 rows (the set and slot map, roles, capture and the 4-phase rebuild, the alpha
`1-(1-a/h)/n`, per-frame write rules, nlerp, lazy drawn matrices, breaks and clears, the 400 m/s safety net). Add
concept 24, rules 21-22 (including the rule for game code), excerpts 18-19, figure 13 and screenshot 10, the physics
inventory's "Interpolating fixed steps" chapter, and the deferred list (F12).

**Proposal.** Change the size to L.

### F19 (minor): Other concepts of these areas are claimed by several pages and are missing from the one-home table

**Where:** `book.md` lines 56-79.

**Proposal.** Add these rows:
- **Engine services vs scene services, dependency inversion:** `core/engine-modules` (`EngineServices`) and
  `world/systems` (`Scene::GetService`). Dependency inversion itself goes to `core/layers-registries`; assets
  concept 3 and scene-ecs concept 14 link to it.
- **Registries that open, accept and freeze:** `core/layers-registries`. `world/reflection` covers only
  `ComponentRegistry`'s builder; assets registries link.
- **Topological sort (Kahn):** `core/engine-modules`. `world/systems` covers only "built from the back".
- **Atomic writes and crash-safe file writing:** `core/files` (F14). Linked from `assets/importing`, `assets/robustness`,
  `editor/saving` and `engineering/generated-code` (StrataShaderTool, the Slang rename).
- **Corruption sweeps and fuzzing:** `engineering/test-program` (F15); `assets/robustness` links.
- **Percentiles, self time and "CPU, GPU or capped":** `core/profiling`; `engineering/perf-lab` links.
- **FMA contraction and floating-point determinism:** `engineering/flags-portability`; `core/math` and physics link.
- **Sun from an HDR sky (`HDRSun`, RemoveSun, `lighting.extractSun`):** `light/sky`; `assets/texture-cooking` gives
  the setting. Three inventories claim it: assets §1.8, render-direct row 160, render-indirect row 63.
- **Threading model and the threads of a process:** `core/jobs`; foundation figure 12 lives there.
- **UUIDs:** `world/ecs`; `assets/handles-meta` links.

### F20 (minor): Words with two meanings in these areas' glossaries need the treatment "module" and "layer" got

**Where:** `book.md` line 79.

**Problem.**
- "Registry": `entt::registry` in scene-ecs's glossary vs Strata's startup registries in foundation's glossary.
- "Prefetch": the `Core/Prefetch.h` cache-line hint vs the asset dependency prefetch.
- "Block": a pack block vs a BC block.
- "Journal": the feature-test journal vs `automation/journal`.
- "Snapshot": a scene snapshot vs the `FrameProfiler` snapshot.
- "Hot reload": assets vs scripts.
- "Service": an engine service vs a scene service.
- "Batch": a `ParallelFor` batch vs an upload batch.

**Proposal.** Extend the row to "'Module', 'layer', 'registry', 'service' (two meanings each) | `core/map`", and add to
`pipelines.md` "Glossary" (lines 137-142) the rule that a term with two meanings gets two entries with qualified names
("pack block", "BC block"...).

### F21 (minor): Reference material the inventories proposed is dropped

**Where:** `outline-4.md` lines 134-136, 145-146.

**Problem.**
- Scene-ecs ch. 12 is lost: Scene/Entity API tables, `ComponentFlags`, `PropertyType` and `PropertyFlags`,
  `SettingsField` types, the file formats `.stscene/.stprefab/.stproj/.stgame/STSC`, and limits and constants
  (`c_MaxEntities`, `c_MaxHierarchyMoves`, `c_MaxTransformChanges`, `c_ParallelTransformWidth`,
  `c_MaxInterpolatedSpeed`, the 512 KiB settings cap).
- Assets ch. 14 is lost: budget defaults, the `asset.stats` fields, runtime flags, the Streaming panel's columns.
- Build-test ch. 10's "catalogue of perf suites as a reference table" is lost (`Budgets.json`, about 248 metrics, 73
  provisional).

**Proposal.**
- Add `reference/scene` "Scene, reflection and settings: types, flags, formats, limits", generated from the headers.
- Retitle `reference/assets` to "Asset types, file formats, importer versions, budgets and statistics" (source
  `AssetResidencyBudgets`, `AssetManagerStats`).
- Add `reference/performance` "Measured costs and their budgets", generated from `StrataTests/Perf/Budgets.json`. It
  is also where `book.md` line 91's "the numbers are shown" can be checked.

### F22 (minor): Part 3 has no prerequisites line, and the book's design decisions have no home pages

**Where:** `outline-1.md` line 82; `book.md` lines 85-91.

**Problem.**
- Part 3 is the only engine part without prerequisites. Its pages need `basics/cpp` and `basics/computer`;
  `core/map` needs `basics/build` (executables vs static libraries, foundation concept 1); `core/jobs` needs
  `basics/threads`; `core/math` needs `basics/math-vectors` and `basics/math-rotations`.
- The eight design decisions are "stated once ... on its home page", but no home is named. Three of them are in these
  areas: "game time counts fixed steps" (`core/time`), "parallel work is deterministic" (`core/jobs`; the parallel
  writer's deterministic bytes are `world/serialization`'s), and "measured on the reference machine" (no concept page
  teaches how to measure: foundation concept 20 and build-test concept 21 are split between two internals pages).

**Proposal.**
- Add "Prerequisites of the part: `basics/computer`, `basics/cpp`, `basics/build`; per page: `core/jobs` +
  `basics/threads`; `core/math` + `basics/math-vectors`, `basics/math-rotations`".
- Add a "Home" column to the decisions paragraph (or rows in the table).
- Add `engineering/measuring` "Measuring performance honestly: noise, percentiles, budgets" (C, M) before
  `engineering/perf-lab`, as the home of the last decision.

### F23 (minor): The picture pipeline cannot make several figures these inventories list

**Where:** `pipelines.md` lines 39-47.

**Problem.** Foundation lists screenshots 3 (Tracy), 5 (terminal output of a headless run and Ctrl+C) and 6 (the native
fatal-error dialog). Build-test lists screenshots 1-2 and 4-7 (configure and ctest output), 3 (Visual Studio), 8
(GitHub Actions pages and annotations), 9 (LookDev's `index.html`) and 10 (an installed folder). None of the five kinds
(scene, live, whole editor, shipped game, diagram) produces them.

**Proposal.** Add two kinds:
- "Text capture": a tool runs a command at the pin and writes its output into a fenced block, re-run at the pin move.
- "Tool screenshot": a manual recipe with steps, taken per release and judged by eye like whole-editor pictures.

Say which figures may be text only.

### F24 (minor): The primers marked "new" do not name the inventory material they must teach

**Where:** `outline-1.md` lines 71-80.

**Problem.** Writers read "that inventory's whole file" (`outline-1.md` line 9), but these pages name no inventory:
- `basics/threads` is foundation concept 16.
- `basics/bytes` is foundation concepts 23 and 26, assets concept 19 and build-test excerpt 13.
- `basics/computer` holds the cache-friendly sparse sets (scene-ecs concept 4).
- `basics/cpp` names only foundation, but scene-ecs concept 17 (type erasure, CRTP, `std::variant`, pointers to
  members) and the "Reader must know first" columns of all four inventories list what it must cover.

**Proposal.** Fill the From column:
- `basics/threads`: "foundation concept 16"
- `basics/bytes`: "foundation concepts 23, 26; assets concept 19; build-test excerpt 13"
- `basics/cpp`: "foundation 'C++ for engine code'; scene-ecs concept 17; the 'Reader must know first' columns of
  foundation, scene-ecs, assets"
- `basics/computer`: "scene-ecs concept 4; foundation concepts 16-17"

### F25 (minor): `engineering/generated-code` leaves out the committed generators

**Where:** `outline-4.md` line 115.

**Problem.** Build-test §1.13 and its glossary ("Committed generator") list about ten generators whose outputs are
committed and that CI never runs, some with `--check` or a `StrataTools.*` test: `GenerateBlueNoise`, `FitFilmic`,
`FitAOMultiBounce`, `GenerateAreaTable`, `GenerateWhiteBalance`, `GenerateBrandAssets`, `GenerateShowcase*`,
`GenerateIslandTerrain`, `StrataEditor/Tools/GenerateIconHeader.py` and the feature test's `GenerateAssets.py`.
`GenerateBrandAssets` has no page at all. The page title covers only code generated at build time.

**Proposal.** Retitle it "Generated code: shaders, embedded files, version stamps and committed generators" and teach
the committed-generator rule there. Each generator's output stays with its subject page.

---

## Further findings (not in the top 25)

- **`assets/uploads` vs `gpu/upload-queue` at item level** (`book.md` line 64). Render-core ch. 7 claims `PlanStep`
  too (render-core.md line 797), and assets §1.11 holds both halves. State the split:
  - `gpu/upload-queue`: `PlanStep`, `StagingPool`, the transfer queue, `PrepareBackBuffer`.
  - `assets/uploads`: steps of `c_AssetUploadStepBytes`, the first step of a frame always goes,
    `AssetFinalizeContext`/`AssetFinalizeResult` (Pending, AwaitingGPU), `Texture::UploadLevels`, one batch per
    `Update`.

  Otherwise the M page is half a repeat.
- **`assets/robustness`** (`outline-2.md` line 40). Each of its items has another natural home: pack validation in
  packs-export, staged publication and records in importing, sweeps in testing. Make it the named home of "untrusted
  input: validate before use, checksums, bounded sizes" and "write-ahead ordering", give it kind C (the inventory says
  concept, S-M), and let the others link.
- **Per-page tracks.** The outline sets tracks per part, but book.md line 74 asks for badges per page. The inventories
  mark many engine-part chapters "both": foundation ch. 3, 4, 10, 12; scene-ecs ch. 3, 5, 9, 11; assets ch. 1-5, 7, 8,
  10, 11; build-test ch. 2, 13. `core/time`, the home of a concept every game maker meets, would get only `[engine]`
  (as `style.md` line 41 shows). Add a Track column to the outline tables.
- **`world/tutorial-component`** (`outline-2.md` line 17) comes before `world/serialization`, but the skill's §4
  requires a `SerializationTests.cpp` round trip and the feature test. Move it to the end of part 4.
- **`core/engine-modules`** lost the inventory's tutorial "write a module" (foundation ch. 6). Make the
  `FrameCounterModule` exercise one of its required exercises.
- **The CameraComponent** (scene-ecs §1.2: projection, `GetProjection` with reversed Z, DOF fields, 11 inactive
  reasons) has no named engine page. Give `GetProjection` to `gpu/coordinates`, the DOF fields to
  `image/motion-blur-dof` and the primary-camera lookup to `world/scene-graph`, and say so in the allocation.
- **`make/assets`** (H M) must hold the game-maker side of assets: import settings and their effect, normal-map
  conventions and `FlipGreen`, Fast vs High, sub-assets, safe moves and deletes, the usage warning. Consider L.
- **Docs drift for writers** (from the inventories' "Not determined"):
  - DG and the skill list 12 shards; `CoreShards.json` has 13 (`SceneTiming`).
  - `BuiltinModules.h` 21-27's comment names fewer modules than the table.
  - `SceneRegistration.h` 6-9 omits `Scene.Timing`.
  - DG names `Tools/GenerateAssets.py` for `StrataTests/FeatureTest/Tools/GenerateAssets.py`.

  Each pilot or part brief should list these so pages do not repeat the docs' mistakes (style.md "Honesty").

---

## Allocation map: where each inventory section goes (for the allocators)

This map was checked against the outline; "(F n)" marks a home that depends on a proposal above.

**foundation**
- §1.1 entry point, launch, `ProgramRun`: `core/first-frame`. The composition root, options, state machine and
  optional modules: `core/layers-registries`.
- §1.2 specification, startup, `ReportFatalError`, exit codes, `CommandLine`: `core/first-frame`. `Run`/`RunFrame`,
  skipping, work time, `SubmitToMainThread`, `FramePacer`, timers, shutdown: `core/frame-loop`. `Layer`/`LayerStack`:
  `core/windows-events`. Interrupts, GUI subsystem, power throttling: `core/platform`.
- §1.3: `core/engine-modules` (device creation in detail: `gpu/vulkan-nvrhi`).
- §1.4: `core/windows-events`.
- §1.5: logging, asserts and `ErrorThrottle` go to `core/conventions`; Tracy and `FrameProfiler` to `core/profiling`;
  `CrashGuard` and `Symbolizer` to `scripting/crash-containment`.
- §1.6: `core/jobs`; `SleepUntil` goes to `core/frame-loop`.
- §1.7: `core/platform` and `core/files` (F14). `FileWatcher` is used in `assets/importing`. `Process` and
  `DynamicLibrary` go to `scripting/loading` and `make/script-builds`; `SaveFiles` to `make/levels-saves`; the settings
  files to `world/projects-settings`; sockets to `automation/json-rpc`.
- §1.8: `core/math`, with culling in `draw/bounds-culling` and the conventions in `gpu/coordinates` (F7).
- §1.9: `reference/core`. Hashes and Base64 go to `basics/bytes`, `RadixSort` to `draw/batching`, `RangeAllocator` to
  `gpu/geometry-pool`, `AmortizedCheck` to `world/scene-graph`, `EmbeddedFiles` and `Version.h` to
  `engineering/generated-code`, `stpch.h` to `engineering/flags-portability`.
- §1.10: `core/layers-registries` and `engineering/cmake` (F5).
- §1.11: `core/time`, `world/systems`, `world/interpolation`, `editor/stepping`, and `world/projects-settings`
  (`Scene.Timing`).

**build-test**
- §1.1: `engineering/building` (options), `engineering/cmake` (project, `ST_WITH_*`, globbing, output layout) and
  `engineering/flags-portability` (warnings, codegen options, configurations, static runtime, cache, pch, manifest).
- §1.2: `engineering/building` and `reference/build`.
- §1.3: `engineering/cmake`.
- §1.4: `engineering/generated-code`, `gpu/shaders` and `engineering/third-party` (F6).
- §1.5: `engineering/third-party`.
- §1.6: `engineering/test-program` (F15); GPU helpers go to `engineering/test-kinds`, editor helpers to
  `editor/ui-testing`, `CheckSceneCaches` to `world/scene-graph`.
- §1.7: `engineering/perf-lab`, plus `reference/performance` (F21).
- §1.8: `engineering/feature-test`.
- §1.9: `engineering/test-kinds`. The tools tests go to `engineering/look-dev`, TargetHLSL to `engineering/ci`, the
  Slang fetch test to `engineering/third-party`.
- §1.10: `core/layers-registries`, `engineering/flags-portability`, `scripting/abi-sdk`, `gpu/shaders` and
  `engineering/contributing`.
- §1.11: `engineering/ci`.
- §1.12: `engineering/releasing`; the installation marker is also used in `make/script-builds`.
- §1.13: `reference/build`, with each generator on its subject page and `GenerateBrandAssets` in
  `engineering/generated-code` (F25).
- §1.14: `engineering/contributing`; the validation-layer setup goes to `engineering/building`.

**scene-ecs**
- §1.1: `world/ecs`. `Scene::Copy` is also used in `editor/play-mode`. Prepared states, `RequestSceneLoad` and
  `ReleaseInBackground` go to `world/sub-scenes` as retitled (F17).
- §1.2: `world/ecs` and `reference/components`, with the camera's pieces as in the further findings.
- §1.3 and §1.4: `world/scene-graph`.
- §1.5 and §1.6: `world/systems`.
- §1.7: `world/interpolation`.
- §1.8 and §1.11: `world/sub-scenes` (F17).
- §1.9: `world/serialization`.
- §1.10: `world/prefabs`, with editing upkeep in `editor/prefab-instances` (F9).
- §1.12 and §1.14: `world/reflection`.
- §1.13: `world/projects-settings`. Collision layers go to `physics/collision-layers`, the manifest and game info to
  `worlds/export` and `worlds/runtime`, the script settings to `make/script-builds`.
- §1.15: the editor and make parts.

**assets**
- §1.1: `assets/handles-meta`; states and the `Asset` base class go to `assets/loading`.
- §1.2: `assets/what-is-an-asset` (registries and seams at a glance), `assets/loading` (the upload seam) and
  `assets/extending`. `MeshGeometryRegistry` goes to physics, which the physics and render-core inventories also
  list.
- §1.3 and §1.4: `assets/loading`. `TouchLoadedAssets` goes to `draw/asset-requests`; `RuntimeAssetManager` mounts to
  `assets/packs-export`.
- §1.5: `assets/residency`; script pins go to `make/levels-saves`.
- §1.6: `assets/references`. The referencers index goes to `editor/trash-references`, native documents' references to
  `assets/importing`.
- §1.7: `assets/importing`. File operations go to `editor/trash-references` and `assets/handles-meta`, native document
  writes to `editor/saving`, the content stamp to `editor/thumbnails`.
- §1.8: `assets/textures` and `assets/texture-cooking` (F16) and `assets/models-gltf`. The audio importer goes to
  `audio/clips-voices-sources`, fonts to `gpu/text`, LUTs to `image/grading`, `HDRSun` to `light/sky` (F19), usage
  warnings to `make/materials`.
- §1.9: `assets/packs-export` (F8).
- §1.10: `assets/mip-streaming`.
- §1.11: `assets/uploads` and `gpu/upload-queue`.
- §1.12: `reference/commands`, `editor/instrument-panels`, `editor/thumbnails`, `worlds/export` and
  `engineering/feature-test`.

No item of the four inventories is left without a page once F5-F9, F14-F17 and F25 are applied.

## Not checked

- The other 15 inventories, except where an overlap with these areas had to be confirmed (render-core rows 112,
  120-124, 138, ch. 4-7; render-scene lines 235-239; editor-core rows 177-181; worlds-runtime ch. 8;
  render-direct/render-indirect `HDRSun` rows; physics row 61).
- `research/*.md` (the curricula checklist is the expert critic's lens).
- Whether the game-maker pages (`make/*`, gamedev inventory) take every game-dev hands-on item of these four
  inventories. The homes look plausible (for example `make/levels-saves` for loading screens and pins, `make/export`
  for `AlwaysInclude` and notices), but they were not traced item by item.
- No engine program was run, and no build was made.
