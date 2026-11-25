---
id: world/sub-scenes
title: "Loading scenes: whole, additive and in slices"
description: "How Strata reads a scene on a worker, hands it to the main thread, prepares it, merges it into a running scene in slices and lets it go without a stall."
kind: internals
size: L
tracks: [E]
needs: [world/prefabs, world/systems]
time: 90
learn:
  - id: states
    text: trace one scene load through the six states of its request, naming who calls Update each frame and what each state waits for
  - id: handover
    text: explain which steps of reading a scene run on a worker and which on the main thread, and why the scene moves without a copy
  - id: slices
    text: predict how many updates a sub-scene of a given size needs from the entity limit and the time cap
  - id: chunks
    text: compute the next chunk size and the new cost estimate from the time left and the cost measured
  - id: unload
    text: explain why unloading a sub-scene makes its entities inactive at once, destroys them in slices and lets a replaced scene go on a job
since: 0.3.0
status: final
---

A level can hold a million entities, and a game must draw its next frame long before all of them exist. This page teaches how Strata brings a scene into memory without stopping the frame. A worker thread reads the scene, the :term[main thread]{id=main-thread} takes it, the :term[scene systems]{id=scene-system} prepare it in small shares, and a scene that joins a running one gets its entities a slice at a time. It also teaches how a scene goes away without a stall. Which assets stay in memory (residency) is taken as given, and so are the loading screens of a shipped game and the cells of a streamed world: other pages teach those.

The hands-on parts use the installed Strata, its samples and `StrataCLI` ([How to read this book](../start/how-to-read.md)). The :term[source files]{id=source-file} are in your clone of [your first engine change](../core/first-change.md).

## The problem and how engines solve it

Suppose a level has 20,000 entities and creating one takes 2 microseconds. Creating them all in one frame takes 40 ms. A frame at 60 :term[frames per second]{id=frame-rate} lasts 16.7 ms, so the picture freezes for about two and a half frames. Reading the file is slower still, and destroying the old level also costs time. A game that loads a level must hide all of this work from the player.

Engines use five techniques, and most combine several. The first is to load the whole level before play, which is simple and has no stall during play. The cost is a wait at the start, and all of the level must fit in memory. The second is a level switch behind a loading screen: the old scene stops, a screen shows progress, and the next scene is read in the background. The swap itself is still one frame, and that frame builds everything the new scene needs at once unless the engine prepares it earlier.

The third technique is a background load with a hand-over. Worker threads read and decode the file, but only one thread may touch the scene. The finished scene is therefore handed to the main thread, and the cost of the hand-over decides whether it helps: moving a pointer is cheap, and copying a million entities is not.

The fourth is the **additive load**: loading a scene into a scene that is already running, next to what it holds, instead of replacing it. A level becomes a set of parts that come and go as the player moves. Two parts can collide, because each part carries entity identifiers (IDs) from the file it was made in, and removing a part must remove exactly its entities.

The fifth technique cuts the work into slices. A **slice** is the share of a long job that one update does before it hands the frame back. The slice needs a limit on a count or on time. A count is simple to test, but entities that nobody touched for a while cost several times what recent ones do, so a fixed count can run past the frame on a cold machine. A limit on time follows the machine.

Strata uses both. A **work budget** is the most that one frame may spend on one kind of work, in time and in counts.

:::elsewhere
Unity can load a scene in additive mode, next to the scenes that are open, and Unreal Engine splits a level into smaller levels that streaming loads and unloads while the game runs. Both are additive loads. The sources are in Further reading.
:::

Strata combines all five. A scene that will run loads in the background, is prepared before the swap, and is handed over without a copy. A scene that joins a running one is compiled on a job and created in slices bounded by both a count and a time. A scene that goes away stops at once and is destroyed on a background job.

## The map of scene loading

Four kinds of things take part. A scene asset holds the scene the worker read, a load request moves it through its states, and a work budget limits the frame's loading work. The scene itself keeps the list of its sub-scenes. An owner, such as `GameRuntime` or the editor, calls the request once per frame.

```mermaid caption="The path of a scene: a worker reads the file, the main thread takes the prepared scene, the request prepares it within the frame's budget, and the owner or a running scene takes it over." alt="A left to right chain of boxes. A scene file goes to a worker thread that reads it into a prepared scene held by the scene asset. The main thread takes the prepared scene into a load request. The load request, which draws from a work budget, hands a ready scene to the owner. A second path from the load request goes to a running scene, which creates its entities in slices."
flowchart LR
    File["Scene file"] --> Read["SceneAsset::Deserialize (worker)"]
    Read --> Asset["SceneAsset holds the prepared scene"]
    Asset --> Take["TakePreparedScene (main thread)"]
    Take --> Req["SceneLoadRequest::Update (main thread, once a frame)"]
    Budget["SceneWorkBudget (one per frame)"] --> Req
    Req --> Own["TakeScene: the owner starts the scene"]
    Req --> Sub["Scene::UpdateSubScenes: a running scene creates entities in slices"]
    Budget --> Sub
```

A **prepared scene** is a scene read from its document, checked and complete in memory, that has not run yet.

A **sub-scene** is a scene merged into a running scene by an additive load, tracked so that the running scene can remove exactly its entities later. The files below own the pieces.

| Part | Where | Owns |
| --- | --- | --- |
| `SceneAsset` | `Strata/src/Strata/Scene/Prefab.h` and `Prefab.cpp` | The prepared scene, until the first take |
| `SceneLoader`, `SceneLoadRequest` | `Strata/src/Strata/Scene/SceneLoader.h` and `SceneLoader.cpp` | One load: its state, its pins and the scene in between |
| `SceneWorkBudget` | `Strata/src/Strata/Scene/SceneWorkBudget.h` and `SceneWorkBudget.cpp` | One frame's allowance of loading work |
| Sub-scenes | `Strata/src/Strata/Scene/SceneSubScenes.cpp`, `SubScene.h`, `SubSceneLoad.h` | The scene's list of additive loads |
| Owners | `Strata/src/Strata/Runtime/GameRuntime.cpp`, `StrataEditor/src/Editor/EditorContext.cpp` | The call to `Update` and the start of the taken scene |

Three threads do the work. The loading worker reads the document, computes the :term[world transforms]{id=world-transform} and estimates the memory. The job system compiles a sub-scene's entities into a prototype, which [Prefabs](../world/prefabs.md) teaches. The main thread does everything else, because it owns the scene.

## The contract

Callers of this code may rely on the rules below, and must follow them.

- Call `Update` of a request once per frame on the main thread, after the asset manager's own update. The request reads asset states that the manager changes in its update.
- `TakeScene` hands the scene over once. A second call returns null, so two owners never share one scene.
- The pins of a request, the holds that keep each asset it loads in memory, live as long as the request. The owner drops it once the scene has started, so that the scene's own requests keep its assets from then on.
- A scene that arrives from a load does not run. `BeginAdditiveLoad` asserts that its scene is not running, because a job compiles it afterwards and nothing may touch it.
- Loading work draws from the frame's `SceneWorkBudget`. Several loaders run in one frame, and separate budgets would add up beyond the frame.
- Let go of a scene with `ReleaseInBackground`, never from inside its own update. Destroying a large scene on the main thread is a stall.

:::rule[Scenes that will run load prepared and never block]
Load a scene that will run with `PrepareSystems`, and let loading work draw from the frame's budget. Otherwise the frame that swaps the scene builds its physics bodies and render proxies (the :term[renderer's]{id=renderer} records of what each entity draws) all at once. A player can then drop through ground whose bodies do not exist yet. [Preparing a scene before it runs](#preparing-a-scene-before-it-runs) shows the hooks.
:::

:::rule[Load through the loader, let go in the background]
Scenes load through `SceneLoader`, never through a blocking read of the asset, and a scene that is replaced goes through `ReleaseInBackground`. Destroying a million entities takes tens of milliseconds, which is more than a frame. [Asking the owner and letting a scene go](#asking-the-owner-and-letting-a-scene-go) shows the function.
:::

## A toy version

The toy creates 4,000 entities over several frames. A simulated clock stands in for the real one, so each run prints the same lines. The first 1,000 entities are cold and cost 6,000 ns each; the rest cost 1,500 ns. Each frame has a budget of 2 ms and a limit of 5,000 entities. Watch two things in the output: how many entities a frame creates, and how the estimate of the cost per entity moves.

```cpp sketch="world-sub-scenes-toy.cpp"
// A toy of sliced loading: a level of 4,000 entities appears over several frames.
// A simulated clock replaces the real one, so the output is the same on every run.
#include <algorithm>
#include <cstddef>
#include <cstdio>

// What creating the entity with this number costs, in nanoseconds: the first ones are cold.
static double GetRealCost(size_t number)
{
	return number < 1000 ? 6000.0 : 1500.0;
}

// The entities that fit in the time left at the estimated cost, between two limits.
static size_t FitChunk(double remainingNs, double estimateNs, size_t smallest, size_t largest)
{
	if (remainingNs <= 0.0)
		return smallest;
	const double fitting = remainingNs / std::max(estimateNs, 1.0);
	if (fitting >= static_cast<double>(largest))
		return largest;
	return std::max(smallest, static_cast<size_t>(fitting));
}

// A dearer chunk raises the estimate at once; a cheaper one lowers it halfway.
static void RecordChunkCost(double& estimateNs, double elapsedNs, size_t entities)
{
	const double measured = elapsedNs / static_cast<double>(entities);
	estimateNs = std::max(measured, 0.5 * (estimateNs + measured));
}

int main()
{
	constexpr size_t c_Total = 4000;
	constexpr size_t c_MaxPerFrame = 5000;
	constexpr double c_FrameNs = 2'000'000.0;
	double estimateNs = 2000.0;
	size_t created = 0;
	for (int frame = 1; created < c_Total; frame++)
	{
		double spentNs = 0.0;
		size_t thisFrame = 0;
		while (created < c_Total && thisFrame < c_MaxPerFrame && spentNs < c_FrameNs)
		{
			// The first chunk of a frame is whole, so that every frame makes progress.
			size_t chunk = thisFrame == 0 ? 512 : FitChunk(c_FrameNs - spentNs, estimateNs, 32, 512);
			chunk = std::min({ chunk, c_Total - created, c_MaxPerFrame - thisFrame });
			double chunkNs = 0.0;
			for (size_t i = 0; i < chunk; i++)
				chunkNs += GetRealCost(created + i);
			RecordChunkCost(estimateNs, chunkNs, chunk);
			spentNs += chunkNs;
			thisFrame += chunk;
			created += chunk;
		}
		std::printf("frame %d: %zu entities in %.2f ms, estimate %.0f ns\n", frame, thisFrame, spentNs / 1e6, estimateNs);
	}
	return 0;
}
```

```text output-of="world-sub-scenes-toy.cpp"
frame 1: 512 entities in 3.07 ms, estimate 6000 ns
frame 2: 512 entities in 2.96 ms, estimate 5895 ns
frame 3: 1356 entities in 2.03 ms, estimate 1569 ns
frame 4: 1361 entities in 2.04 ms, estimate 1504 ns
frame 5: 259 entities in 0.39 ms, estimate 1502 ns
```

1. **Line 10:** a cold entity costs four times a warm one.
2. **Lines 16–21:** `FitChunk` returns the smallest chunk when no time is left, the largest when the estimate says it fits, and else what fits.
3. **Lines 27–28:** `RecordChunkCost` raises the estimate to a dearer measurement at once and lowers it only halfway.
4. **Lines 42–46:** the clock and the counts are read between chunks, never inside one. The first chunk of a frame is whole, so every frame makes progress.
5. **Lines 50–53:** each chunk's measured cost feeds the next chunk's size.

The toy shows what a slice does. Frames 1 and 2 run past the 2 ms, because a whole first chunk of 512 cold entities costs 3 ms. Frame 3 meets warm entities and the estimate falls from 5,895 ns to 1,569 ns in a few chunks, so the frame creates 1,356 entities. The real engine does the same, on the real clock and with real entity counts.

## Reading a scene once

A scene file is read once per load. The asset loader for scenes, registered in `Strata/src/Strata/Scene/SceneRegistration.cpp`, calls `SceneAsset::Deserialize` on a loading worker. The function reads the document as a stream, one entity at a time, as [the document reader](../world/serialization.md) teaches. A scene in a game's pack is a cooked document, and the loader reads it without parsing text. A broken document fails here, at load time, and a cancelled load stops the read within a few hundred entities.

The last steps of `Deserialize` still run on the worker. The next quote shows them.

```cpp src="Strata/src/Strata/Scene/Prefab.cpp#L383-L388" from="// The world transforms too are computed here" to="return asset;" symbol="SceneAsset::Deserialize"
// The world transforms too are computed here rather than in the frame that starts the scene.
asset->m_Prepared->UpdateWorldTransforms();
asset->m_PreparedBytes = asset->m_Prepared->EstimateMemoryUsage();
if (progress)
	progress(1.0f);
return asset;
```

The worker computes the world transforms, so the frame that starts the scene does not. It also estimates the scene's memory, which the asset manager uses for accounting. While it works, the read reports progress: 80 % for the text, 12 % for linking the entities and the rest for the transforms. A loading bar can therefore move during the seconds a large scene needs.

The prepared scene stays in the asset. The main thread takes it with `TakePreparedScene`, and the next quote shows what that call does.

```cpp src="Strata/src/Strata/Scene/Prefab.cpp#L400-L416" symbol="SceneAsset::TakePreparedScene"
Ref<Scene> SceneAsset::TakePreparedScene(std::string* outError)
{
	if (!m_Prepared)
	{
		if (outError)
			*outError = fmt::format("The scene of asset {} was taken already; load the asset again", Handle.ToString());
		return nullptr;
	}
	LogWarnings(*m_Prepared);
	Ref<Scene> scene = std::move(m_Prepared);
	scene->SetSourceAsset(Handle);
	// The project's layers replace the document's here, and its fixed rate the scene's step, on the main thread: the
	// loader's worker never reads the project.
	scene->ApplyProjectLayers();
	scene->ApplyProjectTiming();
	return scene;
}
```

1. **Line 402:** a scene taken already fails with a message. The asset keeps no copy, because a copy would double the memory of a large scene.
2. **Lines 408–410:** the warnings of the read (unknown properties, components this build lacks) are logged once, and the scene moves out of the asset and learns which asset it came from.
3. **Lines 413–414:** the project's collision layers and fixed rate replace the document's. This happens on the main thread, because a worker never reads the project's settings; [Project settings](../world/projects-settings.md) teaches that pattern.

Two more facts belong here. `CreateScene` makes a copy of the prepared scene instead of moving it, for tools and tests that need several scenes from one asset. A scene keeps its :term[source asset]{id=source-file} (`GetSourceAsset`), and it has a lineage ID (`GetLineageID`) that is the source asset's handle or, for a scene made in code, an ID made when it was built. Copies share the lineage ID, so a system can recognize a scene from one play session to the next: physics remembers by it how much capacity the scene needed.

## The states of a scene load

`SceneLoader::LoadAsync` starts a load and returns a `SceneLoadRequest`. It fails at once, with a reason, when no asset manager is active or when the handle is no scene. Otherwise it requests the scene asset and the assets the scene uses as one group, and each of them is pinned, which keeps it in memory while the request lives. Which assets join the group, and how it fits each pool's memory budget, is taught in [Assets, references and dependencies](../assets/references.md).

```mermaid caption="The six states of a load. The owner calls the update once per frame, and the states move on only when their wait is over." alt="A chain of four boxes for the states loading scene, loading dependencies, preparing and ready, joined by arrows. Each arrow has a label that says what the load waits for. From the first box an arrow leads to a failed box, and from the first three, arrows lead to a cancelled box."
stateDiagram-v2
    [*] --> LoadingScene
    LoadingScene --> LoadingDependencies: the scene is taken from its asset
    LoadingDependencies --> Preparing: progress reaches the required share
    LoadingDependencies --> Ready: nothing to prepare
    Preparing --> Ready: every hook returned true
    LoadingScene --> Failed: the asset failed
    LoadingScene --> Cancelled: Cancel
    LoadingDependencies --> Cancelled: Cancel
    Preparing --> Cancelled: Cancel
```

The owner calls `Update` on the request every frame, after the asset manager's update. The request has six states: `LoadingScene`, `LoadingDependencies`, `Preparing`, `Ready`, `Failed` and `Cancelled`. The first quote shows the first state.

```cpp src="Strata/src/Strata/Scene/SceneLoader.cpp#L231-L278" from="if (m_State == SceneLoadState::LoadingScene)" to="m_State = SceneLoadState::LoadingDependencies;" symbol="SceneLoadRequest::Update"
if (m_State == SceneLoadState::LoadingScene)
{
	switch (manager->GetAssetState(m_Scene))
	{
		case AssetState::Failed:
			Fail(fmt::format("Loading scene {} failed: {}", m_Scene.ToString(), manager->GetAssetError(m_Scene)));
			return;
		case AssetState::Unloaded:
			// Unregistered meanwhile (deleted, or its file removed): nothing will ever be read.
			if (manager->GetAssetType(m_Scene) != AssetType::Scene)
			{
				Fail(fmt::format("Scene {} is no longer an asset: it was deleted or removed while it loaded", m_Scene.ToString()));
				return;
			}
			// Unloaded meanwhile (another load took and released it, or an editor reloads it): read it again.
			manager->RequestLoad(m_Scene, m_Options.Priority);
			return;
		case AssetState::Loading:
			return;
		case AssetState::Ready:
			break;
	}
	// The group counts the scene asset as loaded before it is unloaded below (its progress never decreases).
	m_Group.Progress();
	const Ref<Asset> loaded = manager->PeekLoadedAsset(m_Scene);
	if (!loaded || loaded->GetType() != AssetType::Scene)
	{
		Fail(fmt::format("{} is not a scene asset", m_Scene.ToString()));
		return;
	}
	const Ref<SceneAsset> asset = std::static_pointer_cast<SceneAsset>(loaded);
	if (asset->IsTaken())
	{
		// Another load took this copy's scene: this one reads the file again.
		manager->UnloadAsset(m_Scene);
		manager->RequestLoad(m_Scene, m_Options.Priority);
		return;
	}
	std::string error;
	m_Prepared = asset->TakePreparedScene(&error);
	// The asset is spent; its entry holds nothing until the scene is loaded again.
	manager->UnloadAsset(m_Scene);
	if (!m_Prepared)
	{
		Fail(fmt::format("Scene {} is invalid: {}", m_Scene.ToString(), error));
		return;
	}
	m_State = SceneLoadState::LoadingDependencies;
```

1. **Lines 233–252:** the request asks the asset manager for the scene asset's state. Failed ends the load. An asset that is unloaded was either deleted, which fails the load, or released by another load, which asks for a read again. Loading waits.
2. **Lines 261–268:** an asset whose scene another load took is read again, so two loads of one scene each get a scene of their own.
3. **Lines 270–272:** the first hand-over runs on the main thread, and the spent asset is unloaded.
4. **Lines 273–278:** a scene that cannot be taken fails the load with the reason, and otherwise the request moves on.

The second half of `Update` waits for the scene's assets, and then prepares the scene.

```cpp src="Strata/src/Strata/Scene/SceneLoader.cpp#L281-L297" from="if (m_State == SceneLoadState::LoadingDependencies &&" to="m_State = SceneLoadState::Ready;" symbol="SceneLoadRequest::Update"
if (m_State == SceneLoadState::LoadingDependencies && m_Group.Progress() >= m_Options.RequiredProgress)
{
	const bool prepares = m_Options.Prepare || (m_Options.PrepareSystems && HasSystemPreparation());
	m_State = prepares ? SceneLoadState::Preparing : SceneLoadState::Ready;
}
// A frame's share of the preparation, from the frame that reached the requirement on: the systems' first, then the
// owner's.
if (m_State == SceneLoadState::Preparing)
{
	SceneWorkBudget ownBudget;
	if (!budget)
	{
		ownBudget = SceneWorkBudget::ForFrame(m_Prepared->GetSettings());
		budget = &ownBudget;
	}
	if (PrepareWithSystems(*budget) && (!m_Options.Prepare || m_Options.Prepare(*m_Prepared, *budget)))
		m_State = SceneLoadState::Ready;
```

1. **Line 281:** the load moves on when the share of stored :term[bytes]{id=byte} that finished loading reaches `RequiredProgress`. The default 1 waits for everything the scene uses, and 0 waits for the scene alone.
2. **Lines 283–284:** a request with a `Prepare` hook, or with `PrepareSystems` and a system that prepares, goes to `Preparing`. Any other goes to `Ready` at once.
3. **Lines 290–295:** a caller that passes no budget gets one made from the scene's own settings.
4. **Lines 296–297:** the systems prepare first, then the owner's hook, and the request is `Ready` when both have returned true.

The progress that `GetProgress` reports never decreases. While the document is read, it counts the read's share of the scene's own bytes, so the number moves before the asset is loaded. An asset the scene uses that fails to load counts as finished, because the scene then shows a fallback for it. Only a failure of the scene asset fails the load.

`TakeScene` is the second hand-over. It works only once the request is `Ready`, and only on its first call. It also applies the project's layers and fixed rate again, because the project may have changed them since `TakePreparedScene`, which was before the preparation. `Cancel` releases every pin, abandons the loads the request started that nobody else needs, and lets a scene it already holds go through `ReleaseInBackground`. The :term[destructor]{id=destructor} of a request that is not finished calls `Cancel`.

:::example[One level switch, frame by frame]
Suppose a game switches level. Frame 1: `LoadAsync` starts, and the worker reads the scene. Frames 2 to 40: `Update` finds the asset still loading and returns; the progress bar moves with the read. Frame 41: the asset is ready, `TakePreparedScene` runs, and the state is `LoadingDependencies`.

Frames 42 to 80: textures and meshes load, and the progress counts bytes. Frame 81: the share reaches 1, so the state becomes `Preparing`, and physics builds some bodies within the 4 ms budget. Frames 82 to 90: more slices of bodies and proxies.

Frame 91: every hook returns true, the state is `Ready`, and the owner calls `TakeScene` and starts the scene. The swap frame has nothing left to build.
:::

## Preparing a scene before it runs

A scene that will run, such as a game's start scene or a scene switch, loads with `PrepareSystems`. The scene systems that you met in [Scene systems](../world/systems.md) can then carry a `PrepareLoadedScene` function. While the request is `Preparing`, `Update` calls these functions in update order, each with the scene and the frame's budget. A function returns true when it is done, and false to be called again in the next frame. The request remembers which systems finished.

A **prepared start** is a scene start whose systems built what they need (physics bodies, the first cells of a world) while the scene was still loading, so that its first frame builds nothing. The physics system shows the pattern. Its hook makes a physics world for the scene and builds bodies in slices of a fixed size, until the budget has no time left. It keeps the world in a prepared state: a slot on the scene, found by type with `SetPreparedState`, `GetPreparedState` and `TakePreparedState`, that holds what a system built before the scene runs. When the scene starts, the system takes the state instead of building.

The owner can add its own hook with the `Prepare` option. The game :term[runtime]{id=runtime} and the editor use it for the :term[renderer]{id=renderer}, which builds the render proxies of the scene so that the first drawn frame does not. Prepared states never copy: `Scene::Copy` omits them, and `ReleaseInBackground` drops them on the main thread, because a physics world must not die on a worker.

A scene that is edited, not played, loads without `PrepareSystems`, because nothing will run it. Sub-scenes load without it too: they join a scene whose systems already run, and the systems hear each new entity through its signals.

## Asking the owner and letting a scene go

A script may want to end the game or switch scenes, but only the owner of the scene can do that, so the scene offers a small mailbox. `RequestQuit` stores an :term[exit code]{id=exit-code}, and `RequestSceneLoad` stores the handle of the next scene asset (the null handle asks to start the running scene again). The owner honors them after the update in which they were made. A quit wins over a scene load, and a later request replaces an earlier one. `TakeSceneLoadRequest` returns the pending request and clears it, so an owner that cannot honor it does not ask again every frame.

The game runtime does this in `GameRuntime::HandleSceneRequests` and in `UpdateSceneLoads`, where it also calls `SetSceneLoadProgress` with the request's progress each frame. Scripts read it with `GetSceneLoadProgress` to draw a loading bar. [Worlds at run time](../worlds/runtime.md) teaches the owner's side in a shipped game, [Play mode](../editor/play-mode.md) the editor's, and [Levels and saves](../make/levels-saves.md) the loading screen.

The scene that goes away needs care too. The runtime hands it to `ReleaseInBackground`, and the next quote shows what that does.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L177-L192" symbol="Scene::ReleaseInBackground"
void Scene::ReleaseInBackground(Ref<Scene> scene)
{
	if (!scene)
		return;
	ST_CORE_ASSERT(!scene->m_IsUpdating, "Scene '{}' is released while it updates", scene->m_Name);
	scene->OnRuntimeStop();
	// Sub-scene loads hold asset requests (main thread only); a compilation still running finishes into its own result.
	scene->m_SubScenes.clear();
	scene->m_DeferredSubSceneUnloads.clear();
	// What systems prepared listens to the registry or holds engine objects (a physics world): it goes here.
	scene->m_PreparedStates.clear();
	// What is left are storages and caches nothing else reaches: component values hold no engine objects, and the registry
	// signals nothing while it is destroyed (its render scene, in the registry's context, is plain data). Whoever lets go
	// last destroys it: the job, unless someone else still holds the scene.
	JobSystem::Submit([scene = std::move(scene)]() mutable { scene.reset(); }, JobPriority::Background);
}
```

1. **Line 181:** a scene may not be released from inside its own update.
2. **Lines 182–187:** what must end on the main thread ends now: the systems stop, sub-scene loads drop their asset requests, and prepared states go, because they hold engine objects.
3. **Line 191:** the entities and caches that nothing else reaches are destroyed by a job of background priority, so the frame pays only for the stop.

The job holds the last reference to the scene, and the scene dies on the worker. If something else still holds the scene, the last holder destroys it. A million entities take tens of milliseconds to destroy, which is why this work leaves the frame.

## Sub-scenes: a scene inside a running scene

An additive load has two doors. `Scene::LoadSubScene(asset, options)` takes a scene asset, and `Scene::BeginAdditiveLoad(prepared)` takes a prepared scene that code made. Both return a `SubSceneID`, or 0 with an error. A sub-scene has five states, and its status (`SubSceneStatus`) reports its progress, its entity counts and the number of slices.

```mermaid caption="The life of a sub-scene. Loading and compiling come first, then entities appear a slice at a time, and an unload ends the life in slices too." alt="A chain of boxes for the states loading, creating and loaded. A box named failed hangs from loading and creating. From loaded, and from the other two, an arrow leads to unloading, and from there to nothing."
stateDiagram-v2
    [*] --> Loading
    Loading --> Instantiating: compiled
    Instantiating --> Loaded: every entity exists
    Loading --> Failed
    Instantiating --> Failed
    Loading --> Unloading: UnloadSubScene
    Instantiating --> Unloading: UnloadSubScene
    Loaded --> Unloading: UnloadSubScene
    Unloading --> [*]: the last entity is gone
```

`LoadSubScene` uses the load request of the previous section, with the sub-scene's priority and `RequiredProgress`, but without a preparation hook. In `Loading`, the request reads the scene and its assets, and then a job compiles the prepared scene into an entity prototype. The job also drops the prepared scene, so the main thread never pays for destroying it. The first quote shows that half.

```cpp src="Strata/src/Strata/Scene/SceneSubScenes.cpp#L367-L391"
if (status.State == SubSceneState::Loading && load.Request && !load.Compiled)
{
	SceneLoadRequest& request = *load.Request;
	request.Update();
	status.Progress = 0.5f * request.GetProgress();
	if (request.GetState() == SceneLoadState::Failed)
	{
		FailSubScene(load, request.GetError());
		return;
	}
	if (request.GetState() != SceneLoadState::Ready)
		return;
	Ref<Scene> prepared = request.TakeScene();
	if (!prepared)
	{
		FailSubScene(load, "The scene was taken by another load");
		return;
	}
	load.Compiled = CreateRef<SubSceneLoad::CompileResult>();
	load.CompileJob = JobSystem::Submit([result = load.Compiled, scene = std::move(prepared)]() mutable
	{
		result->Prototype = EntityPrototype::Compile(*scene);
		scene.reset();
	});
}
```

1. **Lines 369–371:** the sub-scene updates its own request, and its progress is half of the request's progress. The other half belongs to creating the entities.
2. **Lines 372–378:** a failed request fails the sub-scene, and any state before `Ready` ends this update.
3. **Line 379:** `TakeScene` is the second hand-over again, now from the request to the running scene.
4. **Lines 385–390:** a job compiles the scene's entities into a prototype and releases the prepared scene on its own thread.

The compile finishes at some later update. Then `StartSubSceneInstantiation` starts the creation of the entities, which keep their own IDs, so an ID that the running scene already has fails the load before any entity exists. A scene loaded again while its earlier sub-scene is still unloading waits, because the old entities still hold the IDs.

The second quote shows the slice. It runs in every update while the sub-scene is `Instantiating`.

```cpp src="Strata/src/Strata/Scene/SceneSubScenes.cpp#L410-L457"
	// A slice: chunks until the budget is spent, the time is up or every entity exists.
	PrototypeInstantiation& instantiation = *load.Instantiation;
	size_t created = 0;
	while (budget > 0 && !instantiation.IsComplete() && std::chrono::steady_clock::now() < deadline)
	{
		std::string error;
		const auto chunkStart = std::chrono::steady_clock::now();
		const size_t chunk = GetChunkWithin(deadline, m_CreateNanosecondsPerEntity, m_SlicedThisPass == 0, std::min<size_t>(budget, c_InstantiationChunk));
		const size_t count = ContinueInstantiation(instantiation, chunk, &error);
		if (count == 0)
		{
			FailSubScene(load, error.empty() ? std::string("No entity could be created") : std::move(error));
			return;
		}
		budget -= static_cast<uint32_t>(count);
		created += count;
		// The new top-level entities name their sub-scene, so that unloading finds them wherever the game moved them.
		const std::vector<Entity>& roots = instantiation.GetRoots();
		for (size_t index = load.TaggedRoots; index < roots.size(); index++)
		{
			m_Registry.emplace_or_replace<SubSceneComponent>(roots[index].GetHandle(), SubSceneComponent { status.ID, status.Scene });
			load.Roots.push_back(roots[index]);
		}
		if (roots.size() > load.TaggedRoots)
			m_SubSceneMembershipVersion++;
		load.TaggedRoots = roots.size();
		SceneWorkBudget::RecordChunkCost(m_CreateNanosecondsPerEntity, Since(chunkStart), count);
		m_SlicedThisPass += count;
	}
	if (created > 0)
		status.Slices++;
	status.CreatedEntities = instantiation.GetCreatedCount();
	status.SkippedEntities = instantiation.GetSkippedCount();
	if (!instantiation.IsComplete())
	{
		const float handled = static_cast<float>(instantiation.GetHandledCount());
		status.Progress = 0.5f + 0.5f * handled / static_cast<float>(std::max<size_t>(1, status.TotalEntities));
		return;
	}

	// Every entity exists: from now on the scene requests what they use, so the load's pins go.
	status.State = SubSceneState::Loaded;
	status.Progress = 1.0f;
	load.Instantiation.reset();
	load.Request.reset();
	ST_CORE_TRACE("Scene '{}': sub-scene {} loaded ({} entities in {} slices, {} not created because an ancestor was destroyed meanwhile)", m_Name,
		status.ID, status.CreatedEntities, status.Slices, status.SkippedEntities);
}
```

1. **Lines 413–417:** the loop continues while the budget has entities left, the prototype has entities left and the clock is before the deadline. The chunk comes from the next section.
2. **Lines 418–423:** the chunk's entities are created complete. A chunk that creates none fails the sub-scene, which destroys what it made.
3. **Lines 427–435:** the new top-level entities get a `SubSceneComponent`, and the membership version rises.
4. **Lines 436–437:** the chunk's measured cost goes into the estimate for the next chunk.
5. **Lines 450–455:** when every entity exists, the state is `Loaded`, and the request drops its pins, because from now on the scene requests the assets its entities use.

A **`SubSceneComponent`** is a runtime-only tag on each top-level entity of a sub-scene that names the sub-scene and its source asset. It is never saved, copied or shown. The tag makes unloading exact: the sub-scene owns the top-level entities that carry its ID and their descendants.

Code asks which sub-scene an entity belongs to with `GetSubSceneOf`, which walks up to the top-level ancestor. `FindSubSceneBySource` finds the latest sub-scene of an asset. `AdoptSubScene` registers existing top-level entities as a sub-scene that is `Loaded` at once, and `SetSubSceneOf` moves one top-level entity into a loaded sub-scene or out of all. The membership version changes when a top-level entity joins or leaves, so a cache of memberships can compare it.

## The frame's budget and the chunks

The owner makes one `SceneWorkBudget` per frame with `SceneWorkBudget::ForFrame`, and hands it to everything that loads. The game runtime and the editor do this at the top of their update. A **scene work budget** is that structure: a deadline, the number of entities still to create, the number still to destroy and the sub-scene time cap. The default is 4 ms of loading work, since the rest of a 60 Hz frame is for other work. The counts come from the scene's settings, `MaxEntitiesInstantiatedPerFrame` and `MaxEntitiesDestroyedPerFrame`, both 5,000 by default and clamped between 1 and 1,048,576.

The budget is shared. Scene loads draw from it while they prepare, and then `OnUpdateRuntime` passes it to `UpdateSubScenes`, which runs first in the update. The sub-scenes get a deadline that is the sooner of the budget's and 2 ms from now, so preparation that used 3.5 ms leaves 0.5 ms for slices. Unloads run before loads, because they free memory and the IDs that a reload waits for. Without a budget, the scene makes its own, for tests and tools.

Inside a slice, the work goes in chunks, and the loop looks at the clock between them. A **chunk** is the group of entities created or destroyed between two looks at the clock. The two functions in the next quote choose its size.

```cpp src="Strata/src/Strata/Scene/SceneWorkBudget.cpp#L32-L59"
SceneWorkBudget SceneWorkBudget::ForFrame(const SceneSettings& settings, double milliseconds)
{
	SceneWorkBudget budget;
	budget.Deadline = std::chrono::steady_clock::now() + ToDuration(milliseconds);
	budget.EntitiesToCreate = std::clamp<uint32_t>(settings.MaxEntitiesInstantiatedPerFrame, 1, SceneSettings::c_MaxEntitiesInstantiatedLimit);
	budget.EntitiesToDestroy = std::clamp<uint32_t>(settings.MaxEntitiesDestroyedPerFrame, 1, SceneSettings::c_MaxEntitiesDestroyedLimit);
	budget.SubSceneMilliseconds = Scene::c_MaxSubSceneMillisecondsPerFrame;
	return budget;
}

size_t SceneWorkBudget::FitChunk(std::chrono::nanoseconds remaining, double nanosecondsPerEntity, size_t smallest, size_t largest)
{
	smallest = std::min(smallest, largest);
	if (remaining.count() <= 0)
		return smallest;
	const double fitting = static_cast<double>(remaining.count()) / std::max(nanosecondsPerEntity, 1.0);
	if (fitting >= static_cast<double>(largest))
		return largest;
	return std::max(smallest, static_cast<size_t>(fitting));
}

void SceneWorkBudget::RecordChunkCost(double& nanosecondsPerEntity, std::chrono::nanoseconds elapsed, size_t entities)
{
	if (entities == 0)
		return;
	const double measured = static_cast<double>(elapsed.count()) / static_cast<double>(entities);
	nanosecondsPerEntity = std::max(measured, 0.5 * (nanosecondsPerEntity + measured));
}
```

1. **Lines 35–38:** the deadline is now plus the milliseconds, the counts are clamped to their limits, and the sub-scene cap is 2 ms.
2. **Lines 45–46:** with no time left, the chunk is the smallest allowed.
3. **Lines 47–50:** the entities that fit are the time left divided by the estimated cost per entity, at least 1 ns, and the result stays between the smallest and the largest chunk.
4. **Lines 55–58:** a chunk of no entities changes nothing. Otherwise, the estimate becomes the larger of the measurement and the mean of the old estimate and the measurement.

The sub-scene code chooses the limits: a chunk holds at most 512 entities, and a later chunk at least 32, because each chunk has fixed costs, such as the walk that collects it. The scene keeps two estimates, one for creating and one for destroying, and each starts at 2,000 ns per entity. The first chunk of a pass is whole, whatever the estimate says. Where entities cost more than the frame allows (Debug builds, slow machines), a load still progresses at the same rate, as in the first two frames of the toy.

:::example[A sub-scene of 20,000 entities]
Take the defaults and a warm cost of 1,500 ns. The first chunk has 512 entities and costs 0.77 ms, so 1.23 ms of the 2 ms remain. The estimate is $\max(1500, \tfrac{2000+1500}{2}) = 1750$ ns, so $1{,}230{,}000 / 1750 = 702$ entities fit, and the chunk is the largest, 512.

The second chunk costs 0.77 ms again; 0.46 ms remain, and the estimate is 1,625 ns, so 285 fit. That chunk leaves 0.04 ms, the estimate is 1,562 ns, 23 fit, and the smallest chunk of 32 runs. The update creates $512 + 512 + 285 + 32 = 1341$ entities in about 2.01 ms.

Twenty thousand entities need $20{,}000 / 1341 \approx 15$ updates, a quarter of a second, and no frame stalls. Without slices, the same entities freeze the game for 30 ms.
:::

The count limit rarely binds with these costs: 5,000 entities at 1,500 ns take 7.5 ms, far past the cap. The count matters in tests, which lift the time cap, and on fast machines. This is why neither limit alone is enough. Counting entities only fails on cold caches, and timing only makes tests depend on the clock.

## Unloading in slices

`UnloadSubScene(id)` works in two parts. At once, the call cancels the load, releases its pins and makes the top-level entities inactive in one batch. Inactive entities leave rendering, the scripts' updates, physics and audio in this frame. Afterwards, each update destroys a slice of them, children before parents, until the last entity is gone and the ID is unknown. The next quote shows the first part.

```cpp src="Strata/src/Strata/Scene/SceneSubScenes.cpp#L147-L161" from="// Its top-level entities as they are now leave the game at once" to="status.DestroyedEntities = 0;" symbol="Scene::BeginSubSceneUnload"
// Its top-level entities as they are now leave the game at once: inactive, they leave rendering, the scripts' updates,
// physics (in one batch) and audio in this frame, before any of them is destroyed.
std::vector<Entity> roots;
roots.reserve(load.Roots.size());
for (const Entity root : load.Roots)
{
	const SubSceneComponent* tag = root.IsValid() ? m_Registry.try_get<SubSceneComponent>(root.GetHandle()) : nullptr;
	if (tag && tag->SubScene == status.ID)
		roots.push_back(root);
}
load.DeactivatedRoots.clear();
DeactivateEntities(roots, load.DeactivatedRoots);
load.Roots = std::move(roots);
status.State = SubSceneState::Unloading;
status.DestroyedEntities = 0;
```

1. **Lines 149–156:** only the top-level entities that still carry this sub-scene's tag are collected. The game may have moved or destroyed others since.
2. **Line 158:** `DeactivateEntities` makes them inactive in one batch, and records which were active before.
3. **Lines 160–161:** the state is `Unloading`, and the destroyed counter starts at 0.

`AdvanceSubSceneUnload` then destroys chunks, each a single `DestroyEntities` call, so running systems hear `OnEntityDestroying` and scripts get `OnDestroy`. It uses the destroy budget and its own cost estimate. An entity that gameplay moved out of the :term[subtree]{id=subtree} meanwhile survives, and a top-level entity taken out of the sub-scene is active again. `FlushSubSceneUnloads` destroys the rest at once, for tools and tests, and the scene's runtime stop calls it. An unload that scripts start while `UpdateSubScenes` runs waits for that function to return.

## Watching a load from outside

The editor's command `scene.loadStatus` reports scene loads under way and the running scene's sub-scenes, and `scene.loadAdditive` starts a sub-scene in play mode. [Editor commands](../editor/commands.md) teaches commands. To see what the capture below shows, copy the sample `ThirdPerson` with **File ▸ Open Sample** and press **Play**; the first play builds its scripts. These PowerShell lines, run in the Strata folder, load its scene `Loading` into the running game and ask for the status. On Linux and macOS, pipe with `echo` and write `./StrataCLI`.

```powershell
'{"scene": "Scenes/Loading.stscene"}' | .\StrataCLI call scene.loadAdditive -
.\StrataCLI call scene.loadStatus
```

The command answers with the scene being opened, the game's pending switch, the sub-scenes and the world's cells. The capture keeps only the sub-scene part. In a world, such as the sample `OpenWorld`, the loaded cells are sub-scenes too: the list holds them, and the scene you load gets a number after theirs.

```text capture="load-status"
{
  "subScenes": [
    {
      "createdEntities": 7,
      "error": null,
      "progress": 1.0,
      "scene": "43FD467DF4593C28",
      "skippedEntities": 0,
      "slices": 1,
      "state": "Loaded",
      "subScene": 1,
      "totalEntities": 7
    }
  ]
}
```

1. **Line 2:** `subScenes` holds one entry for each sub-scene.
2. **Lines 4–5:** `createdEntities` counts the entities made so far, and `error` is `null` when nothing failed.
3. **Lines 6–7:** `progress` is 1.0 once the load has finished, and `scene` is the handle of the loaded scene's asset.
4. **Lines 8–9:** `skippedEntities` counts entities the load omitted, and `slices` the time slices it used.
5. **Lines 10–12:** `state` is `Loaded`, `subScene` is the sub-scene's number and `totalEntities` is the 7 entities the scene holds.

While a sub-scene loads, run the line in a second terminal and the state reads `Loading`, then `Instantiating` with a growing `createdEntities`.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Block until the scene is loaded | Tools and small games | The simplest code, with no states | A frozen frame for the whole load |
| A fixed count of entities per frame | Many engines' streaming code | Results that are simple to test | A frame that runs past its time on cold caches and slow machines; spare time unused on fast ones |
| Time only, with no count | :term[Frame loops]{id=game-loop} that fill a budget | Fits any machine | Tests that depend on the clock; one slice can be very large |
| Replace the scene only, no additive loads | Games with one level per scene | No ID collisions, no membership tracking | Streamed parts, rooms that come and go, world cells |
| Copy the loaded scene for every use | Tools that open one asset many times | The asset stays loaded for later uses | Double memory for a large scene; Strata copies only in `CreateScene` |
| Destroy an unloading part in one call | Simple additive loaders | Less code | A stall of tens of milliseconds for a large part |

Strata keeps a count and a time together, because the count gives tests a fixed answer and the time follows the machine. The statements about other engines come from their public documentation, listed in Further reading.

## How it is tested

The suite `Scene.Loader` in `StrataTests/src/Scene/SceneLoaderTests.cpp` checks a request. The test `A scene loads with everything it uses, read once, and becomes ready when all of it is in` checks the states and the single read, and `A load with a preparation works on its scene once per update after all it uses is in, and is ready when that is done` checks `Preparing`. Others check cancelling, failures and the progress of the read.

The suite `Scene.SubScenes` in `StrataTests/src/Scene/SubSceneTests.cpp` checks the slices. The test `Each update's first chunk is whole, so that loads progress however little time an update has` checks the first-chunk rule, and `Later chunks hold what fits in the time left at the cost measured lately` checks `FitChunk` and `RecordChunkCost` with the numbers of this page. It also holds the tests of membership and of a scene that loads again during its own unload.

The suite `Scene.Streaming` in `StrataTests/src/Scene/SceneStreamingTests.cpp` checks whole sub-scenes. The test `An additive load of 20,000 entities is created in slices of at most the per-frame limit` loads four chunks of 5,000, and `A scene released in the background stops at once and is destroyed on a background thread` checks `ReleaseInBackground`. Run a suite directly:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.Loader
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.SubScenes
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.Streaming
```

Each line runs one suite. Add a doctest filter such as `--test-case="A scene load*"` to run only the tests of a suite whose names match.

## Changing it safely

New work in a frame's loading draws from the `SceneWorkBudget` it is given and checks `HasTime` or `GetRemainingTime`. An unfinished job must be able to continue at its next call, because the frame's end can come at any moment. A system that wants a prepared start adds a `PrepareLoadedScene` hook to its description and keeps its state in a prepared state; [Scene systems](../world/systems.md) shows the description.

- Never read the project's settings on the worker. Put them in the hand-over on the main thread, as `TakePreparedScene` does.
- Never destroy a scene on the main thread. Use `ReleaseInBackground`, and keep engine objects in prepared states or sub-scene loads, which that function drops on the main thread.
- Never create or destroy sub-scene entities outside `UpdateSubScenes`; the assertions in the slice functions check that no update is running.
- A change to a limit needs a test that counts slices with the time cap lifted, as `CountedBudget` does in `SubSceneTests.cpp`.
- Run `Scene.Loader`, `Scene.SubScenes` and `Scene.Streaming`, and the feature test, before you commit.

:::caution
A test that waits for a load must wait by the clock or a condition, as `WaitUntil` does, never for a number of frames. The job that compiles a sub-scene runs on another thread, and its end falls in a different frame on each run.
:::

## Summary

- A request moves through `LoadingScene`, `LoadingDependencies`, `Preparing` and `Ready`, or ends `Failed` or `Cancelled`; the owner calls `Update` once per frame, and each state waits for one thing.
- A worker reads the scene, computes its world transforms and estimates its memory. The main thread takes it without a copy and applies the project's layers and fixed rate, because a worker never reads the project.
- A sub-scene compiles on a job and is created in slices that stop at the entity limit or the 2 ms cap, so its update count follows from its size.
- A chunk is the number of entities that fit the time left at the measured cost, between 32 and 512; the estimate rises at once and falls halfway.
- Unloading makes entities inactive at once and destroys them in slices, and a replaced scene is stopped on the main thread and destroyed on a job.

## Check yourself

1. A request has `RequiredProgress` 1. Its scene document finished reading, but a texture the scene uses is still loading. What is its state? (a) `LoadingScene`, (b) `LoadingDependencies`, (c) `Preparing` or (d) `Ready`.

   :::answer{tests="states"}
   Option (b). The read finished and `TakePreparedScene` ran, so the state left `LoadingScene` (a). `Preparing` and `Ready` need the progress to reach 1, which waits for the texture (c, d). With `RequiredProgress` 0 the request would move on in the same update.
   :::

2. Which step of loading a scene runs on the loading worker? (a) Applying the project's collision layers. (b) Computing the world transforms. (c) Calling `TakeScene`. (d) Calling `PrepareLoadedScene` of the physics system.

   :::answer{tests="handover"}
   Option (b). `SceneAsset::Deserialize` computes the transforms and the memory estimate on the worker. The project's layers are applied in `TakePreparedScene` on the main thread (a), `TakeScene` is called by the owner (c), and the preparation hooks run in `Update` on the main thread (d).
   :::

3. A sub-scene has 12,000 entities, the entity limit is 5,000 and creating an entity costs 100 ns. How many updates create entities?

   :::answer{tests="slices"}
   Three updates, of 5,000, 5,000 and 2,000 entities. At 100 ns the 5,000 entities of one update cost 0.5 ms, far below the 2 ms cap, so the count binds and $\lceil 12000 / 5000 \rceil = 3$. Updates that wait for the compile job create nothing and do not count.
   :::

4. The estimate is 1,000 ns per entity, 0.3 ms remain, and the smallest and largest chunks are 32 and 512. What is the next chunk? If it then measures 2,500 ns per entity, what is the new estimate?

   :::answer{tests="chunks"}
   The chunk has $300000 / 1000 = 300$ entities, between 32 and 512. The measurement 2,500 is dearer, so the estimate becomes $\max(2500, (1000+2500)/2) = 2500$ at once. Had it measured 400, the estimate would fall halfway, to $\max(400, 700) = 700$.
   :::

5. A script unloads a sub-scene of 12,000 entities. What is true when the call returns? (a) All entities are destroyed. (b) Its top-level entities are inactive and none are destroyed yet. (c) Exactly 5,000 are destroyed.

   :::answer{tests="unload"}
   Option (b). `BeginSubSceneUnload` makes the top-level entities inactive in one batch, and the destruction waits for the following updates. Option (a) is the stall that slices avoid, and (c) needs an update to run first.
   :::

## Exercises

1. **Basic.** Write a test that sets `MaxEntitiesInstantiatedPerFrame` to 100, loads a sub-scene of 1,000 entities with `BeginAdditiveLoad` and counts the updates until its state is `Loaded`. Predict the number before you run it. Then say what difference the per-frame deadline can make.

   :::answer[Worked solution]{tests="slices"}
   The test, in outline, follows. It counts every update and the updates that created entities.

   ```cpp pseudocode
   Scene scene("Level");
   scene.GetSettings().MaxEntitiesInstantiatedPerFrame = 100;
   SubSceneID id = scene.BeginAdditiveLoad(MakeNestedScene(1000));
   int updates = 0;
   while (scene.GetSubSceneStatus(id)->State != SubSceneState::Loaded)
   {
   	scene.OnUpdateRuntime(1.0f / 60.0f);
   	updates++;
   }
   ```

   Ten updates create 100 entities each, since $1000 / 100 = 10$. The count can be higher, because early updates may wait for the compile job and create nothing. The deadline makes no difference here: the first chunk of an update is whole, so one chunk of $\min(100, 512) = 100$ entities runs whatever the time, and the budget is then spent. Only the number of waiting updates changes from run to run.
   :::

2. **Medium.** The estimate starts at 2,000 ns. Four chunks measure 6,000, 1,500, 1,500 and 1,500 ns per entity. Write a program that prints the estimate after each chunk, and compute the four values by hand first.

   :::answer[Worked solution]{tests="chunks" solution="sketches/world-sub-scenes-estimate.cpp"}
   By hand: $\max(6000, 4000) = 6000$; then $\max(1500, 3750) = 3750$; then $\max(1500, 2625) = 2625$; then $\max(1500, 2062.5) = 2062.5$. The program computes the same.

   ```cpp sketch="world-sub-scenes-estimate.cpp"
   // How the estimate of the cost per entity follows four chunks that measure 6,000, 1,500, 1,500 and 1,500 ns.
   #include <algorithm>
   #include <cstdio>

   // A dearer chunk raises the estimate at once; a cheaper one lowers it halfway.
   static double Record(double estimateNs, double measuredNs)
   {
   	return std::max(measuredNs, 0.5 * (estimateNs + measuredNs));
   }

   int main()
   {
   	const double measured[] = { 6000.0, 1500.0, 1500.0, 1500.0 };
   	double estimateNs = 2000.0;
   	for (const double chunkNs : measured)
   	{
   		estimateNs = Record(estimateNs, chunkNs);
   		std::printf("measured %.0f ns, estimate %.1f ns\n", chunkNs, estimateNs);
   	}
   	return 0;
   }
   ```

   ```text output-of="world-sub-scenes-estimate.cpp"
   measured 6000 ns, estimate 6000.0 ns
   measured 1500 ns, estimate 3750.0 ns
   measured 1500 ns, estimate 2625.0 ns
   measured 1500 ns, estimate 2062.5 ns
   ```

   1. **Line 8:** the rule of `RecordChunkCost`: the larger of the measurement and the mean.
   2. **Lines 13–14:** the four measurements and the starting estimate.
   3. **Lines 15–18:** each chunk updates the estimate and prints it.

   The estimate takes three chunks to fall from the dear first chunk to about 2,000 ns, so a frame after a cold start stays careful.
   :::

3. **Hard.** Trace it yourself: follow the command `scene.loadAdditive` from its registration to the function that spends the budget. Name each file and function on the way.

   :::answer[Worked solution]{tests="states,slices"}
   Search the engine's code for `scene.loadAdditive`. It is registered in `StrataEditor/src/Editor/EditorSceneCommands.cpp`, and its handler calls `LoadSubSceneAndWait`. That function starts `Scene::LoadSubScene` in `Strata/src/Strata/Scene/SceneSubScenes.cpp`, which calls `SceneLoader::LoadAsync` and stores a `SubSceneLoad`. The command then returns a deferred result that polls each frame.

   Each frame, `EditorContext::Update` makes the `SceneWorkBudget` and calls `OnUpdateRuntime` of the running scene in `Scene.cpp`. That calls `UpdateSubScenes`, which calls `AdvanceSubScene` for each pending sub-scene. `AdvanceSubScene` is where the entity budget and the deadline are spent.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/SceneLoader.h` and `SceneLoader.cpp`: `SceneLoader`, `SceneLoadRequest`, `SceneLoadOptions`, `SceneLoadState`.
- `Strata/src/Strata/Scene/Prefab.h` and `Prefab.cpp`: `SceneAsset`, `Deserialize`, `TakePreparedScene`, `CreateScene`.
- `Strata/src/Strata/Scene/SceneSubScenes.cpp`, `SubScene.h`, `SubSceneLoad.h`: sub-scenes, `AdvanceSubScene`, unloading, membership.
- `Strata/src/Strata/Scene/SceneWorkBudget.h` and `SceneWorkBudget.cpp`: `SceneWorkBudget`, `ForFrame`, `FitChunk`, `RecordChunkCost`.
- `Strata/src/Strata/Scene/Scene.h` and `Scene.cpp`: `ReleaseInBackground`, `UpdateSubScenes`, the prepared states and the requests to the owner.
- `Strata/src/Strata/Runtime/GameRuntime.cpp` and `StrataEditor/src/Editor/EditorContext.cpp`: the owners that call `Update` and make the budget.
- Commands: `scene.loadStatus`, `scene.loadAdditive`, `scene.unloadAdditive`; the setting `maxEntitiesInstantiatedPerFrame` of `scene.setSettings`.
- Tests: `StrataTests/src/Scene/SceneLoaderTests.cpp` (`Scene.Loader`), `SubSceneTests.cpp` (`Scene.SubScenes`), `SceneStreamingTests.cpp` (`Scene.Streaming`).
- Other pages: [Prefabs](../world/prefabs.md), [Scene systems](../world/systems.md), [Worlds at run time](../worlds/runtime.md).

## Further reading

- Unity's scripting reference for loading scenes in additive mode, at docs.unity3d.com: the additive form in Unity (beginner).
- Unreal Engine's documentation on level streaming and sublevels, cited without a link: the same idea with streaming volumes (intermediate).
- Robert Nystrom, "Game Programming Patterns", chapter "Game Loop", on gameprogrammingpatterns.com: why work must fit the frame (beginner).
