---
id: draw/entities-to-draws
title: "From entities to draw calls"
description: "How Strata turns the entities of a scene into a few draw calls each frame, and how to read the frame's numbers in the **Stats** overlay and in renderStats."
kind: concept
size: M
tracks: [E]
needs: [gpu/frame-tour, world/scene-graph]
time: 45
learn:
  - id: stage-chain
    text: name the stages that turn an entity with a mesh into draw calls, in order, and the data each one owns
  - id: draw-cost
    text: explain why a draw call costs time on the CPU and on the GPU, and why fewer is not always faster
  - id: retained-proxy
    text: explain why a retained record per object beats walking the scene every frame
  - id: read-stats
    text: find the stage and the page behind each line of the **Stats** overlay and each group of renderStats
since: 0.3.0
status: final
---

Open the Showcase sample in the editor and enable the **Stats** chip of the Scene view. A dark box appears in a corner of the picture, and it counts what the last frame did. Some lines say how many draw calls and instances the frame issued. Others say how many proxies were visible, how many changed and how many :term[bytes]{id=byte} went to the :term[graphics processing unit]{id=gpu} (GPU). Stand still, and the line about uploaded bytes drops to nothing: a still frame sends no instance data at all.

::figure{id=stats-overlay}

Those numbers pose a question. The Showcase holds hundreds of entities and a large game many thousands, and the GPU needs a short list of commands. What has to happen between the two, every frame, without the cost growing with every entity you add? This page answers it in outline and gives each stage a home on the pages of this part.

## The naive answer breaks twice

The first plan is the one you would write on day one. Each frame, visit every entity of the scene. If it has a mesh, tell the GPU to draw that mesh with that entity's transform. One entity, one draw.

The plan breaks in two places. The first is the walk itself.

Take an invented scene of 100,000 entities with meshes, of which the camera sees 4,000. The walk reads 100,000 components every frame, so its cost grows with the whole scene, not the view. For scale, Strata's own first build of a proxy for each of 100,000 mesh :term[renderers]{id=renderer} takes about 36 ms in a Release build, according to `Docs/Architecture.md`. A frame at 60 :term[frames per second]{id=frame-rate} lasts 16.7 ms, so a walk of that size would not fit even before any drawing.

The second break is the draws. Each draw makes the :term[central processing unit]{id=processor} (CPU) work and the GPU change what it is doing. The next section looks at both costs.

## A draw call costs both processors

A **draw call** is one command that asks the GPU to draw a range of vertices and indices with one pipeline and one set of bindings. You met the command in [How a GPU frame works](../gpu/how-a-gpu-frame-works.md). The CPU pays to record it: the driver checks the state, translates it and appends it to a :term[command list]{id=command-list}. The GPU pays when two draws differ in pipeline or bindings, because it must switch its state before the next one.

Triangles are only half of the bill. A frame with one million triangles in 10 draw calls usually costs less to submit than the same triangles in 10,000 calls. That is why the count of draw calls appears in the **Stats** overlay beside the triangle count.

Engines reduce the count in a few ways. Each way removes the flaw of the one before it.

- Draw each object with its own call. This is simple and correct, and the count equals the object count.
- **Instancing** is one draw call that draws the same mesh many times, each copy with its own record of data such as its transform. Copies of one mesh now cost one call, but each different mesh still costs its own.
- Merged geometry copies the vertices of many static meshes into one big buffer, so one call draws them. This works for scenery that never moves, but it breaks culling, because one call is all or nothing, and it breaks moving objects.
- An **indirect draw** reads its arguments (which range, how many instances) from a buffer instead of from the CPU. The CPU then records one call for a whole group of batches, and a :term[shader]{id=shader} on the GPU can write the arguments.

Strata uses three of these together. It groups visible objects into instanced batches, keeps all meshes in a shared geometry pool (the subject of [The geometry pool](../gpu/geometry-pool.md)), and draws each group of batches with an indirect call where the device can. It does not merge scenery into one mesh, so every entity stays an object that can move, hide or leave the view alone.

:::example[Counting the calls of a small view]
Take the ten objects of the sketch below. Each has a mesh, a :term[submesh]{id=submesh}, a level of detail and a material. Drawn one by one they cost 10 calls. Strata's batch key is the pipeline state, the mesh, the submesh and the level, but not the material, because the shader reads each instance's material. All ten objects share one pipeline state, so five groups remain.

The code groups the list in a map and prints one line for each group. Look at the first two lines of output: ten calls become five, and the largest group holds three instances.

```cpp sketch="draw-entities-to-draws-batches.cpp"
// Counts the draw calls of a visible set drawn one by one and drawn as instanced batches.
// A batch is every drawable that shares a mesh, a submesh and a level of detail: the material is not in the key.
#include <cstdio>
#include <map>
#include <tuple>
#include <vector>

namespace
{
	struct Drawable
	{
		int Mesh;
		int Submesh;
		int Lod;
		int Material;
	};
}

int main()
{
	const std::vector<Drawable> visible = {
		{ 0, 0, 0, 1 }, { 0, 0, 0, 2 }, { 0, 0, 0, 1 }, { 0, 0, 1, 1 }, { 1, 0, 0, 3 },
		{ 1, 1, 0, 3 }, { 1, 0, 0, 3 }, { 1, 1, 0, 4 }, { 2, 0, 0, 1 }, { 2, 0, 0, 1 }
	};

	std::map<std::tuple<int, int, int>, int> batches;
	for (const Drawable& drawable : visible)
		batches[{ drawable.Mesh, drawable.Submesh, drawable.Lod }]++;

	std::printf("one draw per drawable: %zu draw calls\n", visible.size());
	std::printf("instanced batches: %zu draw calls\n", batches.size());
	for (const auto& [key, count] : batches)
		std::printf("  mesh %d submesh %d level %d: %d instances\n", std::get<0>(key), std::get<1>(key), std::get<2>(key), count);
	return 0;
}
```

```text output-of="draw-entities-to-draws-batches.cpp"
one draw per drawable: 10 draw calls
instanced batches: 5 draw calls
  mesh 0 submesh 0 level 0: 3 instances
  mesh 0 submesh 0 level 1: 1 instances
  mesh 1 submesh 0 level 0: 2 instances
  mesh 1 submesh 1 level 0: 2 instances
  mesh 2 submesh 0 level 0: 2 instances
```

1. **Line 26:** the map is the batch table; its key holds the three values that choose a batch.
2. **Lines 27-28:** each visible object adds one to its batch's count, and the material is not part of the key.
3. **Lines 30-31:** drawn one by one the count is the number of objects; batched it is the number of keys.

Scale this up. A forest of 4,000 trees made of 12 distinct meshes at the same level needs 4,000 calls drawn one by one and 12 batched, in every pass that draws it. The saving grows with the repetition in the scene, not with its size.
:::

## Where the list of objects lives

Before the GPU can batch anything, the engine needs the list of things to draw. Where that list lives gives three designs. Each one answers the weakness of the one before.

An **immediate representation** builds the list again every frame by walking the scene's own data. Nothing is stored between frames, so nothing can be stale. The cost is the walk: it grows with the size of the scene every frame, whether anything changed or not. Unity's older built-in pipeline does its culling and gathering this way, according to its documentation.

A **retained representation** keeps one persistent record per object, owned by the renderer, and updates it only when the scene says that something changed. A frame then reads records instead of components, and a still scene costs almost nothing to prepare. The price is a second copy of the data that must stay current. If a change is missed, the record is stale and the picture is wrong. Unreal Engine keeps a render-side object per primitive for this reason.

A **GPU scene** keeps the retained records in GPU memory too. The CPU uploads only what changed, and the GPU does the culling and builds its own draws from the records. The CPU now does less per frame. The design needs a device that can draw from buffers it filled itself, and the CPU cannot see what the GPU decided without waiting for a late read.

| Design | CPU cost per frame | Stale data | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Immediate walk | Follows the whole scene | Never | Low | Unity's built-in pipeline, small engines |
| Retained proxies | Follows what changed and what is seen | If a change is missed | Medium | Unreal Engine, Strata's CPU path |
| GPU scene | Follows what changed only | Same, in two copies | High | Unreal Engine's GPU scene, Strata's GPU-driven path |

All three serve one rule: the cost should follow what changed and what is in view, never the size of the scene.

## Strata keeps render proxies and draws on two paths

Strata chose the second and third rows together. A **render proxy** is the renderer's own record of one entity that has a `MeshRendererComponent`: its world matrix, its bounds, its mesh, an optional replacement material, some flags and the entity's identifier. Proxies live in a `RenderScene`, which belongs to the scene, so the editor's viewport, a capture and a thumbnail share one. The next page, [The render scene](render-scene.md), takes the records apart.

The scene's change signals keep the proxies current. When a component is created or marked as modified, or when a :term[world transform]{id=world-transform} changes, the render scene reads the entity at its next `Sync`. This is the transform contract you know from [The scene graph](../world/scene-graph.md), extended to mesh renderers: code that writes a field of the component must signal, or the proxy stays stale. In a Debug build the engine compares the proxies with the scene after syncs, so a missed signal is reported.

```mermaid caption="Who owns which data from an entity to the pixel. The main thread owns the first four boxes; the GPU owns the last two." alt="A chain of six boxes from left to right. Components lead through change signals to render proxies, then to instances, then to the copy in GPU memory, then to the draw list, then to the vertex shader."
flowchart LR
    A["Components in the registry (main thread)"] -->|"signals and transform log"| B["Render proxies in RenderScene (main thread)"]
    B -->|"culling, sorting"| C["Instances and batches (main thread, parallel chunks)"]
    C -->|"incremental upload"| D["GPU copy: RenderSceneGPU"]
    D --> E["Draw list and indirect arguments"]
    E --> F["Vertex shader reads the instance"]
```

Read the chain from the left. The proxy is the renderer's view of it, in arrays so that loops over thousands of proxies read memory in a straight line. Instances are what a frame decides to draw, and the GPU copy holds them so that an unchanged one is never sent again. The vertex shader finally picks its instance out of that buffer.

Strata draws these instances on two paths that share the proxies:

- The **CPU path** finds the visible proxies on the CPU, gathers draws, sorts them into batches and writes the draw lists. It is the reference: its pixels define what the right picture is, and it is the fallback.
- The **GPU-driven path** lets a compute shader test every proxy and write the draws. It is the default where the device can draw indirectly with a first-instance offset (the first instance record a draw reads), and the setting `GPUDriven` (mode `Auto`) chooses it. Mode `Off` forces the CPU path, and a frame also falls back when its pipelines or buffers cannot be created. [The GPU-driven path](gpu-driven.md) owns that switch.

:::why[Why keep two paths?]
The GPU path moves cost off the CPU, but not every device supports it, and a compute shader is harder to debug than a loop. A CPU path that stays in the engine gives a reference to compare against, a fallback for old devices and a way to learn whether a bug lives in the rule or in the shader. The price is real: every rule of culling or batching exists twice and must be changed in both places.
:::

## Both paths must agree, whatever the thread count

Two implementations of one rule drift apart unless something stops them. Strata states the constraint for the whole part: the CPU path and the GPU-driven path draw the same pixels, and the result never depends on how many threads ran. A test suite named `GPU.SceneRenderer.GPUDriven` renders scenes both ways and compares the images pixel for pixel.

The second half follows from how parallel work is arranged. Gathering draws splits the proxies into chunks of 2,048 and gives each chunk to a job. The results are merged in chunk order, and the sort that follows is stable. The same input then gives the same list on 2 threads or 32, as the [jobs page](../core/jobs.md) explains for ordered parallel work in general.

A rule changed in one path only breaks the first half. A "fix" in the CPU extraction code alone makes the two paths disagree, and the test fails. Treat the pair as one rule written twice.

## One frame of extraction in two lanes

A frame starts with the scene and the camera and ends with commands for the GPU. The diagram shows the stages in order, with the two lanes where the paths differ. The shared stages come first; then the CPU lane decides draws on the CPU, and the GPU lane hands the decisions to compute shaders.

```mermaid caption="The extraction stages of one frame. Both paths share the first stages and the last one; the middle differs between the lanes." alt="A diagram. A shared top row runs through five stages. Below it two lanes: the CPU lane tests visibility and gathers draws, sorts them and builds arguments, while the GPU lane prepares culling, uploads and runs the culling shaders. Both lanes end in the passes and the release of the frame's assets."
flowchart TB
    S1["Sync"] --> S2["BeginFrame of the asset cache"] --> S3["RenderSceneGPU Update"]
    S3 --> C1
    S3 --> G1
    subgraph CPU["CPU path"]
        C1["CullView"] --> C2["FindShadowCasters"] --> C3["ResolveAssets"] --> C4["GatherDraws and sort"] --> C5["BuildDrawArguments"] --> C6["UploadSceneData"]
    end
    subgraph GPU["GPU-driven path"]
        G1["CullView or ApplyFeedback"] --> G2["FindShadowCasters"] --> G3["ResolveAssets"] --> G4["GatherDraws: transparent only"] --> G4b["BuildDrawArguments"] --> G5["PrepareGPUCulling"] --> G6["UploadSceneData"] --> G7["RunGPUCulling"]
    end
    C6 --> P["Passes draw"]
    G7 --> P
    P --> R["ReleaseFrameAssets"]
```

On the GPU lane, two further stages run inside the passes: the occlusion phases, which test again against the depth the first phase drew. The diagram omits them; [Occlusion culling](occlusion.md) covers them. Both lanes end in the same passes of [A frame of the scene renderer](../gpu/frame-tour.md).

Each stage has a page that teaches it:

| Stage | What it does | Page |
| --- | --- | --- |
| `Sync` | Reads signaled mesh renderers and changed transforms into proxies | [The render scene](render-scene.md) |
| `RenderSceneGPU::Update` | Uploads what changed to the GPU copy, within a budget | [The GPU copy](render-scene-gpu.md) |
| `CullView` and `FindShadowCasters` | Find the proxies in view and the casters of each shadow cascade | [Bounds and culling](bounds-culling.md), [Sun shadows](../light/sun-shadows-1.md) |
| `ResolveAssets` | Finds each mesh and material once per frame | [Asset requests](asset-requests.md) |
| `GatherDraws`, sort and `BuildDrawArguments` | Make batches, sorted by key, and their indirect arguments | [Batching](batching.md) |
| `PrepareGPUCulling` and `RunGPUCulling` | Let compute shaders test visibility and write the draws | [The GPU-driven path](gpu-driven.md) |
| The passes | Draw the batches in the depth prepass, shadows and forward pass | [A frame of the scene renderer](../gpu/frame-tour.md) |

## Reading the frame's numbers

The overlay is a report on those stages. Each line below belongs to one of them, so a number that looks wrong points at a stage and a page. The overlay's values come from a `SceneRendererStats` record of the frame; this table groups the lines that matter here.

| Overlay line | What it counts | Stage that makes it | Page |
| --- | --- | --- | --- |
| `N draw calls (a opaque, b shadow), M instances` | Calls of the forward passes (opaque and transparent), of the opaque ones also the prepass's, calls into the shadow cascades, and drawn submesh instances | Batching | [Batching](batching.md) |
| `N draw commands` | Every draw command the CPU recorded for scene meshes in all passes | The passes | [A frame of the scene renderer](../gpu/frame-tour.md) |
| `N occluded, M occluded casters` | Proxies and shadow casters hidden by nearer surfaces | Occlusion phases | [Occlusion](occlusion.md) |
| `N triangles, lights, materials` | Triangles drawn, lights used and distinct materials | Batching and the passes | [Batching](batching.md) |
| `N visible of M proxies, K updated` | Proxies whose bounds meet the :term[frustum]{id=view-frustum}, the total, and proxies changed since the last frame | Culling and `Sync` | [Bounds and culling](bounds-culling.md) |
| `extract X ms, sort Y ms` | CPU time of culling, assets and gathering, without the sort; CPU time of the sort | Extraction | [Batching](batching.md) |
| `N KB instances, M KB materials uploaded` | Bytes sent to the GPU copy this frame | `RenderSceneGPU::Update` | [The GPU copy](render-scene-gpu.md) |
| `N assets requested, M prefetched, K loading` | Requests the view made and assets not yet ready | `ResolveAssets` | [Asset requests](asset-requests.md) |

Two lines need care. On the GPU-driven path the GPU draws most of the scene, so the CPU's own counts shrink to the transparent surfaces. The overlay then adds the GPU's counts, which arrive two or three frames late, and the line `draw commands` adds a note that the GPU did the culling. Second, `extract` and `sort` time only the CPU's share. The GPU's time sits in its own line near the top, with its three largest stages.

Agents read the same numbers as data. The command `viewport.capture` renders a picture of the Scene view and returns it with the frame's `renderStats`. It needs an editor with a GPU and a project open. Run it from a terminal:

```sh
StrataCLI call viewport.capture '{"camera": "editor"}'
```

The command waits for loading assets, renders, and answers with the image and the `renderStats` object. The command `editor.perf` returns the same `renderStats` for the viewport's latest frame without a new picture. [Editor commands](../editor/commands.md) teaches how commands work as the editor's interface.

The keys of `renderStats` fall into groups that match the stages:

| Group | Keys | Stage |
| --- | --- | --- |
| Which path | `gpuDriven`, `gpuCulled`, `gpuCounts`, `feedbackRequests` | Mode switch |
| Draws | `draws`, `opaqueDraws`, `shadowDraws`, `drawCommands`, `instances`, `triangles`, `instancesPerLod` | Batching |
| What was seen | `visibleProxies`, `culledProxies`, `occludedProxies`, `occludedCasters`, `sizeCulledProxies`, `shadowCasters` | Culling |
| What changed | `proxyUpdates`, `instanceBytesUploaded`, `deferredInstanceBytes` | `Sync` and update |
| CPU time | `extractMs`, `sortMs` | Extraction |
| Assets | `materials`, `pendingAssets`, `geometryPool`, `sceneMirrorMB` | `ResolveAssets` and the pool |

The full list, with every field of the record, is in the [renderer reference](../reference/renderer.md).

:::example[Reading a still frame]
Suppose you capture the Scene view twice without touching anything. If the second capture's `proxyUpdates` and `instanceBytesUploaded` are 0, the retained design is working: nothing changed, so nothing moved. If `proxyUpdates` is large on a still scene, something writes components every frame, often a script that moves an entity. If `deferredInstanceBytes` is above 0, new proxies still wait for their :term[upload budget]{id=upload-budget-gpu}, and a picture taken now would lack them.
:::

## What Strata's choice cannot do

Retained proxies cost memory and care. The renderer holds a second copy of every object, and a GPU copy beside it. While a scene plays, its playing copy has its own GPU copy, which doubles `sceneMirrorMB` while both live. Every code path that edits a mesh renderer must signal, and the engine can only warn about a missed signal in Debug builds.

Batching by mesh, submesh and level also has a limit. Transparent surfaces stay one draw each, because they must draw from far to near. The GPU-driven path needs a device with indirect draws that set their first instance; elsewhere the CPU path runs. Strata does not merge static scenery into one mesh, does not bake draws into a cache you could replay, and does not draw by hardware occlusion queries. The engine omits more, and the list is in [What Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **Thinking triangles are the only cost.** The symptom is a frame that is slow with few triangles, because thousands of small draws or many state changes keep the CPU busy. Read `draws` and `extractMs` beside `triangles` before you decide that a mesh is too heavy.
- **Thinking fewer draw calls is always faster.** The symptom is a scene merged into one mesh that now draws everything even when only a corner is visible, and a GPU that shades the unseen part. Culling needs objects small enough to be skipped, so batch repeated meshes, not the whole world.
- **Writing a component field without a signal.** The symptom is a picture that shows the old transform or material while the inspector shows the new one. Use `MarkModified`, `registry.patch` or the scene's own functions, as the transform contract says.
- **Fixing a rule in one path only.** The symptom is a test that renders the two paths and finds different pixels. Change the CPU extraction and the culling shader together, and run the suite named above.

## Summary

- An entity with a mesh becomes a render proxy in the render scene, then an instance in a batch, then an entry of a draw list. The GPU's copy of the data changes only where something changed.
- A draw call costs the CPU to record it and the GPU to switch state, so Strata groups objects into instanced batches, but it keeps every entity separate so that culling still works.
- A retained record per object follows changes and the view instead of the size of the scene, at the price of a second copy that signals must keep current.
- Each line of the **Stats** overlay and each group of `renderStats` belongs to one stage, so a surprising number points to one page of this part.

## Check yourself

1. A scene has 50,000 entities with meshes and the camera sees 800 of them. Which cost does a retained design avoid that an immediate walk pays every frame?

   - A. Reading the components of all 50,000 entities.
   - B. Drawing the 800 visible meshes.
   - C. Uploading the textures of the scene.

   :::answer{tests="retained-proxy"}
   A. Retained proxies change only when signals say so, and culling touches the proxies, not every component. B is wrong because both designs must draw the visible meshes. C is wrong because textures follow the asset system, not the choice of scene representation.
   :::

2. Two frames draw the same 1 million triangles. One uses 20 draw calls, the other 20,000. Which statement is right?

   - A. They cost the same, because the triangles are equal.
   - B. The second costs more CPU time and more state changes.
   - C. The first must be slower, because each call holds more.

   :::answer{tests="draw-cost"}
   B. Each call is recorded by the CPU, and a change of pipeline or bindings makes the GPU switch state. A is the mistake of counting only triangles. C is wrong in general, because a large call is not slower than the same work in many calls; the exception is a merge that loses culling.
   :::

3. In the **Stats** overlay of a still scene you read "0 updated" and "0.0 KB instances uploaded". What does this tell you?

   :::answer{tests="retained-proxy,read-stats"}
   Nothing changed since the last frame, so no proxy was updated and no instance data reached the GPU copy. That is the retained design doing its job. The two lines come from `Sync` ([The render scene](render-scene.md)) and the GPU copy's update ([The GPU copy](render-scene-gpu.md)).
   :::

4. List the stages from a signaled mesh renderer to the first draw of the frame, with the owner of each datum.

   :::answer{tests="stage-chain"}
   The component sits in the registry. `Sync` reads it into a proxy in the render scene, on the :term[main thread]{id=main-thread}. `CullView` and the gathering turn visible proxies into instances and batches. The GPU copy holds the instances, and the draw list and arguments feed the pass. On the GPU-driven path, the culling shaders write the list.
   :::

## Exercises

1. **Basic.** A view shows 600 trees of 3 meshes at one level of detail and 100 rocks of 1 mesh with 2 submeshes. Count the draw calls of one pass drawn one submesh at a time and drawn as batches.

   :::answer[Worked solution]{tests="draw-cost"}
   One by one: the trees are 600 draws and the rocks are 100 objects with 2 submeshes each, so 200 draws, 800 in all. Batched: the three tree meshes give 3 batches, and the rock mesh gives one batch for each submesh, 2, so 5 batches. The material is not in the key, so trees with different materials still share a batch.
   :::

2. **Medium.** Change the sketch of this page so that the list holds a second level of detail for the mesh 2 and prints the total instance count. Predict the new number of batches, then run it.

   :::answer[Worked solution]{tests="stage-chain,draw-cost" solution="sketches/draw-entities-to-draws-lod.cpp"}
   Add two entries with `Lod` 1 for mesh 2. They share no key with the entries at level 0, so the batches grow from 5 to 6, and the instances from 10 to 12. The program sums the counts of the map for the total.

   ```cpp sketch="draw-entities-to-draws-lod.cpp"
   // The batching sketch with a second level of detail for mesh 2, and the total of the instances.
   #include <cstdio>
   #include <map>
   #include <tuple>
   #include <vector>

   namespace
   {
   	struct Drawable
   	{
   		int Mesh;
   		int Submesh;
   		int Lod;
   		int Material;
   	};
   }

   int main()
   {
   	const std::vector<Drawable> visible = {
   		{ 0, 0, 0, 1 }, { 0, 0, 0, 2 }, { 0, 0, 0, 1 }, { 0, 0, 1, 1 }, { 1, 0, 0, 3 },
   		{ 1, 1, 0, 3 }, { 1, 0, 0, 3 }, { 1, 1, 0, 4 }, { 2, 0, 0, 1 }, { 2, 0, 0, 1 },
   		{ 2, 0, 1, 1 }, { 2, 0, 1, 1 }
   	};

   	std::map<std::tuple<int, int, int>, int> batches;
   	for (const Drawable& drawable : visible)
   		batches[{ drawable.Mesh, drawable.Submesh, drawable.Lod }]++;

   	int instances = 0;
   	for (const auto& [key, count] : batches)
   		instances += count;

   	std::printf("instanced batches: %zu draw calls\n", batches.size());
   	std::printf("instances: %d\n", instances);
   	return 0;
   }
   ```

   ```text output-of="draw-entities-to-draws-lod.cpp"
   instanced batches: 6 draw calls
   instances: 12
   ```

   1. **Lines 21-23:** the visible list now holds two instances of mesh 2 at level 1.
   2. **Lines 26-28:** the key is unchanged, so the new level makes a new batch.
   3. **Lines 30-32:** the total adds the counts of every batch.
   :::

3. **Hard.** A designer sees `proxyUpdates` of 3,000 on a scene where nothing seems to move, while `visibleProxies` is 400. Name three possible causes, say which stage each points to and what you would read next.

   :::answer[Worked solution]{tests="read-stats,retained-proxy"}
   First, a script writes transforms every frame, which `Sync` reads again: look at `proxyUpdates` against the script's entities. Second, code marks a component as modified every frame without a real change: read what signals it. Third, a hierarchy parent moves, so every child's world transform changes: look at the scene's transform changes. In each case, `visibleProxies` says nothing, because updates are about proxies, and culling is about the view.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RenderScene.h`: the render scene, its proxies and `Sync`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: the frame's stages, in the order of the diagram.
- `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`: gathering draws in chunks, merged in order.
- `Strata/src/Strata/Renderer/SceneRenderer.h`: `GPUDrivenMode` and `SceneRendererStats`.
- `StrataEditor/src/Panels/ViewportToolbar.cpp`: `DrawStatsOverlay`, the lines of the overlay.
- `StrataEditor/src/Editor/EditorStateCommands.cpp`: the `renderStats` of `editor.perf`.
- Tests: the suite `GPU.SceneRenderer.GPUDriven` compares the two paths.
- Commands: `viewport.capture`, `editor.perf` and `viewport.setSettings`.

## Further reading

- Unity documentation, "Scriptable Render Pipeline": how culling and drawing are organized outside the built-in pipeline (intermediate).
- Unreal Engine documentation, "Rendering architecture": the render thread and the scene proxy of a primitive (intermediate).
- NVIDIA, "Vulkan Dos and Don'ts": the cost of state changes and draw calls on the GPU (advanced).
- Wihlidal, "Optimizing the Graphics Pipeline with Compute": GPU-driven culling, GDC 2016 (advanced).
