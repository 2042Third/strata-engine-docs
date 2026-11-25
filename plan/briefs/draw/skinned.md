# Brief: `draw/skinned`

| Field | Value |
| --- | --- |
| Title | Skinned meshes in the renderer |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `draw/gpu-driven` |
| From | render-scene; takes a list of joint matrices per mesh as given and links forward to `animation/skinning`; home of posed bounds |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/skinned` — Skinned meshes in the renderer

**Covers.** The job: draw meshes that a skeleton deforms, culled with bounds that follow the pose, at no cost to
scenes without skins. The page takes the pose's joint matrices as given and links forward to `animation/skinning`, which
explains how they are made. The problem section teaches where skinning runs: on the CPU, in the vertex shader with a
palette, or in a compute pre-pass; dual quaternions are named with a link to `animation/skinning`, which teaches the
deformation model (rigid binding, linear blend skinning, the candy wrapper, dual quaternions) and skins a vertex by
hand. Strata's choice: linear blend skinning of four influences in the vertex shader, palettes computed on the CPU only
for changed poses, on the job system. The toy blends four given palette matrices by their weights into one, as
`BlendJoints` does, in about 20 lines.

The real code. Skin proxies: a proxy whose entity has a `SkinComponent` and whose mesh has a skin binding is posed by
the scene's `ISkinningPoses` service, so the renderer never includes Animation. The palette range per proxy, named with
its product in one sentence (what the product means is `animation/skinning`'s). Posed bounds: the union of each joint's
bind-pose extent through its palette entry, why that union bounds every weighted vertex, plus the reach that animators
which pose only when seen publish, and why culling with bind-pose bounds loses a swung limb or its shadow.
`UpdateSkinnedPoses`, which skips the whole pass when poses, transforms, hierarchy, drawn transforms and layouts are
unchanged, skips unchanged proxies, and recomputes the rest in batches of 16 on the job system. The `ST_SKINNED`
variants of the mesh and shadow vertex shaders, which blend four joints from the joint buffer `t15`, with both passes of
a skinned mesh on the same variant so that the `EQUAL` test holds. Bucketing: `c_InstanceSkinned` and the palette's
first joint in the instance (so `InstanceData` does not grow), the skinned sort-key bit and the GPU geometry class.
`HasSkinProxies`, which gates every skinning check. The visibility report: renderers tell the animators which skin
proxies they saw, and which off-view casters can still shadow the view. The rules: skinning work costs unskinned scenes
nothing; posed bounds, not bind-pose bounds; both passes on the skinned variant. What Strata does not do here: compute
skinning and dual-quaternion skinning. How it is tested: `GPU.Animation`'s skinned cases and the GPU perf test
`PerfGPU.Renderer.Skinned1000` (1,000 skinned characters posed anew every frame), its measured time and budget read
through `perf.PerfGPU.Renderer.Skinned1000.Measured` and `.Budget`, as `reference/performance` lists them; the "trace it
yourself" exercise finds why a still robot costs no palette work. The page runs on the Third-Person sample's robot
mid-dance, a limb outside its bind-pose box still drawn and shadowed, and the exercise poses a two-joint arm and prints
its bounds before and after `Sync`. At the end the reader can say what the renderer computes for a skinned proxy, when,
and why its bounds follow the pose.

**Leaves out.**

- How the joint matrices of a pose are made → `animation/skinning`
- The deformation model (linear blend skinning, the candy wrapper, dual quaternions) and a vertex skinned by hand →
  `animation/skinning`
- Skeletons and joints → `animation/skeletons`
- The animation system that publishes poses → `animation/system`
- Animators that pose only what is seen → `animation/culling`
- Skinned motion vectors → `draw/motion-vectors`
- Animation features Strata lacks → `animation/limits`

**Fit.** `over`: about 4,000 words against M (3,000). Two concepts, two excerpts, eight features, three rules and two
exercises reach M's top. Make it L (5,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:311` | concept | home | Where skinning runs: on the CPU, in the vertex shader, in a compute pre-pass, and Strata's choice; dual quaternions named with a link to `animation/skinning`, which teaches the deformation model and skins a vertex by hand (critic-animation-8); posed bounds; the two mistakes |
| `animation:280` | concept | home | Posed bounds and culling of skinned meshes: why the union of transformed joint boxes bounds every weighted vertex |
| `render-scene:157` | feature | home | Skin proxies posed through `ISkinningPoses` |
| `render-scene:159-164` | feature | home | Posed bounds, recomputing only on change, the skinned variants, skinned bucketing, unskinned scenes pay nothing, visibility reports |
| `animation:152` | feature | home | Change-driven palette updates, the animation inventory's view of `render-scene:160` |
| `animation:157` | feature | home | `HasSkinProxies`, the animation inventory's view of `render-scene:163` |
| `render-scene:369` | code | home | `Strata/src/Strata/Renderer/RenderScene.cpp:1322-1339`: the posed bounds half of `ComputePalette` (the palette half is `animation:358`, on `animation/skinning`) |
| `new:8` | code | home | `Strata/src/Strata/Renderer/RenderScene.cpp:1341-1435`: `UpdateSkinnedPoses`, skipping unchanged poses and recomputing the rest in parallel |
| `render-scene:417` | figure | home | Posed bounds as the union of the joints' boxes transformed by their palette entries (the spaces of the product are `animation:381`, on `animation/skinning`) |
| `render-scene:444` | figure | home | The robot mid-dance with a limb outside its bind-pose box, drawn and shadowed |
| `animation:422` | figure | home | The same picture as `render-scene:444`, from the animation inventory: one figure serves both items |
| `render-scene:493` | rule | home | Anything that adds skinning work must cost unskinned scenes nothing |
| `animation:460` | rule | home | Unskinned scenes pay nothing, the animation inventory's form of `render-scene:493` |
| `render-scene:495` | rule | home | Cull skinned proxies with posed bounds, not bind-pose bounds |
| `animation:458` | rule | home | Prepass and forward pass agree to the bit for skinned meshes: both use the `ST_SKINNED` variant |
| `render-scene:545` | hands-on | home | Pose a two-joint arm out of its bind box and print its bounds before and after `Sync` |
| `new:20` | hands-on | home | Exercise ("trace it yourself"): with a breakpoint in `RenderScene::UpdateSkinnedPoses`, find why the robot costs no palette work in a frame where nothing it depends on changed (the versions of the poses, transforms, hierarchy and drawn transforms compare equal and the function returns), and which version changes first when it dances; `RenderSceneStats::LastSyncPoses` counts the palettes recomputed; the solution names the check and the version. Evidence: `Strata/src/Strata/Renderer/RenderScene.cpp:1341-1355` |
| `animation:202` | feature | use | The perf tests of animation, of which this page names the GPU one: `PerfGPU.Renderer.Skinned1000`, 1,000 skinned characters posed anew every frame, with its measured time and budget through `perf.PerfGPU.Renderer.Skinned1000.Measured` and `.Budget` (`StrataTests/Perf/Budgets.json:172`; `StrataTests/src/Perf/AnimationPerfTests.cpp:214`) |
| `render-scene:640` | term | home | Posed bounds |
| `animation:554` | term | home | Posed bounds, the animation inventory's entry (one glossary entry with `render-scene:640`) |
| `new:9` | not-done | home | No compute skinning and no dual-quaternion skinning: skinning runs per draw in the vertex shader. Evidence: `Docs/Roadmap.md:675`; `git grep -niE "dual.?quat" 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `animation:150-151` | feature | use | Pose inputs and the palette, homed on `animation/skinning` |
| `animation:154` | feature | use | `BlendJoints` and the skinning functions of `Include/Scene.slang`, homed on `animation/skinning` |
| `animation:156` | feature | use | The visibility report from the animation side, homed on `animation/culling` |
| `render-scene:126` | feature | use | The GPU buckets' geometry classes |
| `render-scene:158` | feature | link | The palette's formula, at `animation/skinning` |
| `render-scene:491` | rule | link | Every skin influence names a joint of the skin, at `animation/skinning` |
| `render-scene:638` | term | link | Palette, at `animation/skinning` |
| `render-scene:642` | term | link | WhenVisible animator, at `animation/culling` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Scene services and `GetService` | `world/systems` | must |
| Shader variants from one source with defines | `gpu/shaders` | must |
| Batches, sort keys and the instance's fields | `draw/batching` | must |
| Bounds and culling on the CPU | `draw/bounds-culling` | must |
| The GPU path's buckets | `draw/gpu-driven` | must |
| Deterministic parallel work on the job system | `core/jobs` | must |
| Transform hierarchies and spaces | `basics/math-matrices` | must |
| Skeletons, joints and poses | `animation/skeletons` | helps |
| How the joint matrices are made; inverse bind matrices | `animation/skinning` | helps |
| Animators that pose only what is seen | `animation/culling` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `posed-bounds` | Posed bounds | - |
