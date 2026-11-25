---
id: assets/references
title: "References, closures, prefetch and loading screens"
description: "How Strata knows what each asset uses, and how loads, exports, delete checks, prefetches and loading bars follow those references."
kind: internals
size: L
tracks: [E]
needs: [assets/residency, world/serialization]
time: 75
learn:
  - id: record
    text: explain how Strata finds the references of an asset and what a new document type loses when it records none
  - id: closure
    text: compute the closure of a small asset graph in both scopes
  - id: prefetch
    text: explain why a prefetch never removes assets from memory, never chains and skips documents
  - id: progress
    text: predict a group load's progress by stored bytes while its members finish
  - id: fit
    text: predict which part of a scene's closure loads with the scene and which part the scene requests itself
since: 0.3.0
status: final
---

A mesh is no use without its material, a material is no use without its textures, and a scene is no use without all of them. This page is about how Strata knows that. It records what each asset uses, in the editor and in an exported game alike, and answers questions about it from one table. Loads, exports, delete checks, prefetches and loading bars all follow that table. The page does not cover when assets leave memory ([residency](../assets/residency.md)), how a scene switch runs ([sub-scenes](../world/sub-scenes.md)) or what the :term[renderer]{id=renderer} asks for each frame ([asset requests](../draw/asset-requests.md)).

## The problem and how engines solve it

A game ships hundreds of files, and the files point at each other. If the engine does not know the pointers, it fails in three places. An export omits a texture that a material uses, and the game shows a pink surface. A delete removes a mesh that a scene still places. A level loads its meshes first and learns of their materials only when each mesh has finished, so every step waits for the one before it.

An asset that another asset uses is a **dependency** of it.

The asset together with everything it uses, and what those use in turn, is its **dependency closure**. Each engine has to answer one question: where does the list of dependencies come from? Three answers are common.

| Approach | When it works | What it costs |
| --- | --- | --- |
| Scan at load time | The engine opens each asset and reads its pointers | Nothing is known before the read, so a delete check or an export plan must read every file |
| Record at import time | The import step writes the list beside the asset | The list can go stale, and every new file type must record |
| A hand-written manifest | A person lists what each level needs | Cheap to build, and it fails the moment a person forgets |

Strata records, and it answers the same way in the editor and in a game. In the editor, the import of an asset stores its list. In a game, the pack that an export writes carries the lists as a table. Documents that Strata itself writes (scenes, materials) are scanned for references, and the result is recorded like an import's.

:::example[A pink surface]
Suppose a scene places one tower. The tower mesh uses the material `Stone`, and `Stone` uses a 4,000 KB texture. An export that lists only the scene and the mesh ships 40 KB and 600 KB. The material and the texture stay behind, and the game cannot draw the tower. A recorded closure ships all four assets, and nobody has to remember the texture.
:::

## The map

Five parts share the work. The scanner finds references in documents, and :term[importers]{id=importer} record what their sources reference. The manager keeps one table per asset: its direct dependencies and, for a mesh, its bounds, which queries, prefetch and group loads read. `SceneLoader` chooses which part of a closure a scene load takes. In the editor, an index answers the opposite question: who uses this asset?

```mermaid caption="References enter the table from scans and imports; loads, prefetches, exports and the editor read it." alt="Document scans and importer records feed one table per asset. A closure query on the table serves group loads, scene loads and export planning. Prefetch and the renderer's bounds lookup also read it. The editor keeps an inverse index that answers which assets use an asset."
flowchart LR
    Doc["AssetDependencies::Scan of documents"] --> Table["Manager table: dependencies and bounds"]
    Imp["ImportResult::References and Bounds"] --> Table
    Table --> Closure["GetDependencyClosure"]
    Closure --> Group["AssetGroupRequest"]
    Closure --> SceneLoad["SceneLoader"]
    Closure --> Export["Export planning"]
    Table --> Prefetch["PrefetchDependencies"]
    Table --> Bounds["RenderScene::ResolveUnloadedBounds"]
    Table --> Index["EditorAssetManager::GetReferencers"]
```

The code lives in `Strata/src/Strata/Asset/`. `AssetDependencies.cpp` holds the scanner, `AssetImporter.h` the records that importers return, and `AssetManager.cpp` the table and everything that reads it. `SceneLoader.cpp` in `Strata/src/Strata/Scene/` chooses what a scene load takes. The editor's index is in `EditorAssetManager.h`; `StrataEditor/src/Editor/AssetReferences.cpp` adds to it the uses in the edited scene and the project.

## The contract

A caller may assume that the table holds each asset's direct dependencies, and that the manager keeps the table the same way in the editor and in a game. The rules below follow from that.

- References are recorded at import, or found in a document. Either way they are :term[normalized]{id=normalization}: only valid handles, each once, never the asset itself. An asset that names itself (a scene whose script loads the scene again) depends on nothing for that.
- A closure has one of two scopes, and callers pick the scope that fits the job.
- A prefetch loads only direct dependencies, only into spare room, and it never removes anything from memory.
- Prefetches do not chain, documents that place entities prefetch nothing, and scenes are never prefetched.
- A group load pins its whole closure. Its progress counts stored :term[bytes]{id=byte} and never goes down.

:::rule[Record references for any new document type]
A new document type, or a :term[stored form]{id=stored-form} that points at assets, must record its references with `AssetDependencies::Scan` or `ImportResult::References`. Only records tell an export, a delete check or a prefetch what an asset uses. Without them, a pruned export omits the asset's references, and a delete of one gives no warning.
:::

The rules about prefetch come from measurements, which the section on prefetch gives.

## A toy version

The toy holds eight assets in a small graph: the scene `Outpost` uses a prefab, a texture and a second scene `Intro`, which has a mesh of its own. It walks the graph breadth first in two scopes. Then it finishes the members of the `Load` closure one by one and prints the progress by count and by stored bytes. Note the two lists, and the gap between the two percentages.

```cpp sketch="assets-references-toy.cpp"
// A toy dependency graph: a breadth-first closure in two scopes, and a group's progress by count and by bytes.
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

struct Asset
{
	std::string Name;
	bool IsScene = false;
	uint64_t Kilobytes = 0;
	std::vector<size_t> Dependencies;
};

// The list itself is the queue: the loop reads at the head while the end grows.
std::vector<size_t> GetClosure(const std::vector<Asset>& assets, size_t root, bool loadScope)
{
	std::vector<size_t> closure = { root };
	std::vector<bool> visited(assets.size(), false);
	visited[root] = true;
	for (size_t head = 0; head < closure.size(); head++)
	{
		for (size_t dependency : assets[closure[head]].Dependencies)
		{
			if (visited[dependency] || (loadScope && assets[dependency].IsScene))
				continue;
			visited[dependency] = true;
			closure.push_back(dependency);
		}
	}
	return closure;
}

int main()
{
	const std::vector<Asset> assets = {
		{ "Outpost", true, 40, { 1, 5, 6 } },
		{ "Tower", false, 8, { 2, 3 } },
		{ "TowerMesh", false, 600, { 3 } },
		{ "Stone", false, 2, { 4 } },
		{ "StoneTexture", false, 4000, {} },
		{ "MossTexture", false, 2000, {} },
		{ "Intro", true, 30, { 7 } },
		{ "IntroMesh", false, 1000, {} },
	};

	for (bool loadScope : { false, true })
	{
		std::cout << (loadScope ? "Load:" : "All: ");
		for (size_t index : GetClosure(assets, 0, loadScope))
			std::cout << ' ' << assets[index].Name;
		std::cout << '\n';
	}

	const std::vector<size_t> group = GetClosure(assets, 0, true);
	uint64_t totalKilobytes = 0;
	for (size_t index : group)
		totalKilobytes += assets[index].Kilobytes;

	uint64_t doneKilobytes = 0;
	for (size_t finished = 0; finished < group.size(); finished++)
	{
		doneKilobytes += assets[group[finished]].Kilobytes;
		std::cout << assets[group[finished]].Name << ": " << (finished + 1) * 100 / group.size() << "% by count, "
			<< doneKilobytes * 100 / totalKilobytes << "% by bytes\n";
	}
}
```

```text output-of="assets-references-toy.cpp"
All:  Outpost Tower MossTexture Intro TowerMesh Stone IntroMesh StoneTexture
Load: Outpost Tower MossTexture TowerMesh Stone StoneTexture
Outpost: 16% by count, 0% by bytes
Tower: 33% by count, 0% by bytes
MossTexture: 50% by count, 30% by bytes
TowerMesh: 66% by count, 39% by bytes
Stone: 83% by count, 39% by bytes
StoneTexture: 100% by count, 100% by bytes
```

1. **Lines 21–30:** The loop reads the list at `head` while `push_back` grows its end, so the list is the queue.
2. **Line 25:** An asset is skipped when it was seen, or, in the load scope, when it is a scene.
3. **Lines 37–44:** The graph is a table; each asset lists the positions of what it uses.
4. **Lines 63–65:** The same finished members give two shares: the count is flat, the bytes follow stored size.

The lists show the scope at work. `All` reaches `Intro` and its mesh, because a pack that ships `Outpost` needs them. `Load` skips `Intro` and everything only it uses, because a level that is loading does not load the next level. The progress shows why a bar counts bytes. After five of six members the count says 83 %, but the one missing member is the 4,000 KB texture, so bytes say 39 %.

## The real code

Strata does what the toy does, with four differences. The references come from documents and imports instead of a literal. The closure runs under the manager's lock, and prefetch and loads have budgets. The editor needs the inverse table too. The sections below follow the data from its source to its readers.

### Finding references in documents

`AssetDependencies::Scan` takes the stored form of a document and returns its references, each once, in the order they first appear. Scenes, prefabs and models are read as streams through `SceneDocumentReader` (the page on [scene documents](../world/serialization.md) describes it), so a scene of a million entities costs its text and one entity's tree at a time. A sink named `ReferenceSink` receives each entity and calls `ScanEntityInto`.

The function below does the work for one entity. Look at how little it knows: it asks the component registry for each component's properties, and the registry knows which properties hold assets.

```cpp src="Strata/src/Strata/Asset/AssetDependencies.cpp#L62-L85" symbol="ScanEntityInto"
// The references of one entity object of a document.
void ScanEntityInto(const nlohmann::json& entity, ReferenceList& references)
{
	const nlohmann::json* components = JsonUtils::Find(entity, "Components");
	if (!components || !components->is_object())
		return;
	for (const auto& [name, component] : components->items())
	{
		// Components this build does not register are kept, but what they reference is unknown.
		const ComponentInfo* info = ComponentRegistry::Find(name);
		if (!info || !component.is_object())
			continue;
		ScanProperties(info->Properties, component, references);
		// Data the properties cannot express (script fields): its references, as the component reads them.
		if (info->ExtraReferences.VisitJson)
		{
			info->ExtraReferences.VisitJson(component, [&references](PropertyType type, UUID value)
			{
				if (type == PropertyType::Asset)
					references.Add(value);
			});
		}
	}
}
```

1. **Lines 71–73:** The registry maps a component's name to its description; a name this build does not register is skipped, because what it references is unknown.
2. **Line 74:** Every property of :term[asset type]{id=asset-type} found in the registry is read, so a new component needs no scanner change.
3. **Lines 76–82:** Script fields do not fit the property list, so the component's own function reports them, and only values of asset type count.
4. **Line 81:** `Add` is the `ReferenceList` call that keeps each valid handle once.

Every registered component is scanned the same way, so a new component with an asset property needs no scanner change. A component that this build does not register is kept in the file, but what it references is unknown. Script fields do not fit the property list, so a component can supply a function `VisitJson` in its `ExtraReferences`, which the script component uses to report its fields of :term[asset type]{id=asset-type}. Materials get their texture maps, animation controllers the clips of their states, and worlds their persistent scene and the scene of every cell; the same scan rules cover them.

Importers record what their sources reference. `ImportResult` and each `ImportedSubAsset` carry `References` and `Bounds`. A glTF import records the default materials of a mesh and the local bounds of the mesh. A mesh's stored bytes show none of this, so only the importer can say.

### Normalizing and storing

`SetAssetReferences` normalizes the list and stores it in the asset's entry together with its bounds. `NormalizeReferences` keeps a handle only if it is valid, differs from the asset itself and has not been seen. Bounds that are invalid or not finite are dropped. When the bounds change, the manager publishes a content change, so renderers that placed a mesh by old bounds learn of the new ones.

### The closure and its scope

The **closure scope** says how far a closure reaches: `All` follows every reference, and is what a pack plan needs; `Load` stops at other scenes, and is what a load needs. A scene that names another scene (a script field holding the next level, or a world listing its cells) must not load it along with itself. Scenes load as levels of their own.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L1450-L1473" symbol="AssetManagerBase::GetDependencyClosureLocked"
std::vector<AssetHandle> AssetManagerBase::GetDependencyClosureLocked(AssetHandle handle, AssetClosureScope scope) const
{
	std::vector<AssetHandle> closure;
	if (m_Entries.find(handle) == m_Entries.end())
		return closure;
	std::unordered_set<AssetHandle> visited { handle };
	closure.push_back(handle);
	// Breadth first: the list itself is the queue.
	for (size_t index = 0; index < closure.size(); index++)
	{
		const AssetEntry& entry = m_Entries.at(closure[index]);
		for (AssetHandle dependency : entry.Dependencies)
		{
			auto dependencyIt = m_Entries.find(dependency);
			if (dependencyIt == m_Entries.end())
				continue;
			if (scope == AssetClosureScope::Load && dependencyIt->second.Metadata.Type == AssetType::Scene)
				continue;
			if (visited.insert(dependency).second)
				closure.push_back(dependency);
		}
	}
	return closure;
}
```

1. **Lines 1452–1456:** An unknown root gives an empty list; otherwise the root comes first and counts as visited.
2. **Line 1458:** The loop index walks the list while the end grows: the list is the queue.
3. **Lines 1463–1465:** A dependency the manager does not know is skipped.
4. **Lines 1466–1467:** In the `Load` scope a scene is never entered, so what only it uses stays out.
5. **Lines 1468–1469:** A set insert says whether the asset is new, so each asset joins once.

The loop reads the list at index `index` while its end grows, so the list is the queue and no second container is needed. The visited set makes each asset appear once even if two paths reach it, as `Stone` does in the toy. An unknown dependency is skipped, so a deleted asset does not break a closure. The caller holds the manager's :term[mutex]{id=mutex}; `GetDependencyClosure` takes it first.

:::example[Both scopes by hand]
Take scene `A` that uses prefab `P` and scene `B`. `P` uses mesh `M` and material `X`, `M` uses `X`, `X` uses texture `T`, and `B` uses mesh `N`. Breadth first from `A` gives `A`, then `P` and `B`, then `M`, `X` and `N`, then `T`. That is the `All` closure: seven assets. In the `Load` scope the check skips `B`, so `N` is never reached, and the closure is `A`, `P`, `M`, `X`, `T`.
:::

### Bounds before a mesh loads

`GetBounds` answers from the table, so it is known before the mesh loads. The render scene reads it (`RenderScene::ResolveUnloadedBounds`) to place a mesh that has not arrived. A mesh with recorded bounds can be skipped when it is outside the view, and requested only when it is inside. Without a record the renderer has only a placeholder box of two units on each side, and cannot tell what is visible. What the renderer does each frame is the topic of [asset requests](../draw/asset-requests.md).

### Prefetch

Loading a material's textures after the material arrives doubles the wait. To avoid it, Strata uses **prefetch**: when the read of a requested asset completes, the manager queues the asset's direct dependencies at the same priority, behind direct requests. A material's textures load beside the material, and a mesh's default materials beside the mesh.

Prefetch is a bet, and Strata limits the bet in four ways. The limit is **headroom**: the budget left in a pool beside what is resident, reserved for arrivals, on its way, and a window of loads still to come. A prefetch starts only if its stored size fits the headroom of every pool that has a budget.

```cpp src="Strata/src/Strata/Asset/AssetManager.cpp#L1567-L1585" symbol="AssetManagerBase::FitsPrefetchLocked"
bool AssetManagerBase::FitsPrefetchLocked(uint64_t bytes, uint64_t pendingBytes) const
{
	// Room that requested loads cannot need: beside what is resident, reserved for arrivals and on its way, a whole window
	// of loads in flight (InFlightBytes) stays free for the requests still to come. Tight budgets prefetch nothing: in the
	// stress sweep (a 128 MB texture budget), prefetching textures into the room left beside what was on its way still
	// raised the peak private memory by about 25 MB on average.
	// The in-flight budget may be set to anything: the sum saturates.
	const auto add = [](uint64_t a, uint64_t b) { return b > UINT64_MAX - a ? UINT64_MAX : a + b; };
	for (AssetMemoryPool pool : c_AssetMemoryPools)
	{
		const uint64_t budget = m_Budgets.GetPoolBudget(pool);
		if (budget == AssetResidencyBudgets::c_Unlimited)
			continue;
		const uint64_t held = add(add(add(GetPoolBytes(m_Resident, pool), GetPoolBytes(m_Reserved, pool)), pendingBytes), m_Budgets.InFlightBytes);
		if (held > budget || bytes > budget - held)
			return false;
	}
	return true;
}
```

1. **Line 1574:** The sum stops at the largest number instead of wrapping.
2. **Lines 1578–1579:** A pool without a budget never refuses.
3. **Line 1580:** The held sum is resident, reserved, pending and the window.
4. **Lines 1581–1582:** Refuse when the held sum exceeds the budget, or when the request does not fit in what is left.

The sum saturates. The window `InFlightBytes` may be set to any number, and a plain sum of large numbers wraps round to a small one, which would let a huge prefetch pass. A pool with no budget (`c_Unlimited`) never refuses. Tight budgets prefetch nothing; this is on purpose.

:::example[Headroom with numbers]
A texture pool has a 1,024 MB budget. Resident textures take 600 MB, reserved arrivals 50 MB, loads on their way 100 MB, and the window is 128 MB. The held sum is 878 MB, so the headroom is 146 MB. A 100 MB texture fits and starts, and the pending sum grows to 200 MB. The held sum is now 978 MB and the headroom 46 MB, so a 60 MB texture is refused and loads only if something requests it.
:::

Three more rules keep prefetch harmless, and each has a measurement behind it.

- A prefetch never removes anything from memory. A prefetch makes no room and records no use, so its arrivals are the first to leave until something requests them. An arrival that no longer fits when it comes is dropped before it is uploaded. In the stress sweep, with a 128 MB texture budget, prefetching textures into the room left beside the loads on their way still raised the peak memory by about 25 MB on average.
- Prefetches do not chain. An asset that arrived only prefetched prefetches nothing, and its finishing step requests nothing. Its own dependencies are prefetched once something requests it.
- Documents prefetch nothing. Scenes, prefabs and models place entities, and what their entities use is requested by what draws them once it is needed. Prefetching the meshes and materials of a scene raised the stress sweep's peak by 60 to 100 MB. Scenes are never prefetched at all: a world lists every cell, and prefetching them held a drive through a 10,000-cell world at 12.6 GB instead of 280 MB (the `DrivePeakPrivate` metric of the `Perf.World` suite).

:::why[Prefetch only into spare room]
A prefetch is a guess about the future, and a guess must not cost what is certain. Strata could prefetch everything and rely on :term[eviction]{id=eviction} to repair mistakes, but eviction removes assets that a frame may still need. The price is that tight budgets get no help from prefetch, and the first draw of a mesh may wait a little longer.
:::

### Group loads and their progress

A **group load** loads and pins a set of assets together and reports how far it has come. `RequestLoadWithDependencies` takes the `Load` closure of one asset; `RequestLoadGroup` takes a list the caller chose. Both return an `AssetGroupRequest`. It pins every member, so nothing of the group leaves memory while the request lives, and pinning requests the loads in breadth-first order, root first.

Its `Progress` is the share of the members' stored bytes that finished loading, whether Ready or Failed. Each member counts its stored size, and at least 1, so empty files still count. A member that has finished stays counted, even while a hot reload replaces it. A member that the manager no longer has counts as failed. So `Progress` never decreases, and a bar built on it never falls.

`IsComplete`, `HasFailed` and `Cancel` finish the interface: `Cancel` releases the pins and abandons the reads that have not started.

A texture loaded partly (its first read holds its mip tail) counts whole once it is Ready, because its finer levels stream later, as views need them. So a full bar means the group can be drawn, not that every texture is at full detail.

### Reading without loading

Sometimes code needs bytes of an asset but not the loaded asset. `ReadStoredRange` reads a range of the stored form, for example one level of a texture's mip chain, and `ReadStoredData` reads the whole form. A pack decodes only the blocks that cover the range. Both block the calling thread, so they run on an input and output job, never on the :term[main thread]{id=main-thread}.

### What a first load reads, and how a scene load fits its closure

`EstimateFirstLoadBytes` says what a load that starts now would read. Usually that is the stored size. While loads read prefixes and the type has a prefix function, it is the head only: at most `c_AssetPrefixHeadBytes`, which is 64 KB, enough for a cooked texture's :term[header]{id=header} and the mip tail of most. The queue counts it as :term[in flight]{id=in-flight}, and a scene load uses it as a guess of memory.

A scene load takes the `Load` closure of the scene, but not blindly: a load must never push a pool past its budget. `SelectLoadMembers` counts, per pool, what the not-yet-loaded members would hold, using the estimate. It compares that with the room the budget has beside what is resident.

```cpp src="Strata/src/Strata/Scene/SceneLoader.cpp#L83-L102"
const AssetManagerStats stats = manager.GetStats();
std::array<bool, c_AssetMemoryPools.size()> fits = {};
for (size_t pool = 0; pool < c_AssetMemoryPools.size(); pool++)
{
	const uint64_t budget = stats.Budgets.GetPoolBudget(c_AssetMemoryPools[pool]);
	const uint64_t resident = GetPoolBytes(stats.Resident, c_AssetMemoryPools[pool]);
	fits[pool] = budget == AssetResidencyBudgets::c_Unlimited || needed[pool] <= budget - std::min(budget, resident);
}
std::unordered_set<AssetHandle> leftOut;
for (const Candidate& candidate : candidates)
{
	for (size_t pool = 0; pool < c_AssetMemoryPools.size() && !candidate.Loaded; pool++)
	{
		if (!fits[pool] && GetPoolBytes(candidate.Usage, c_AssetMemoryPools[pool]) > 0)
		{
			leftOut.insert(candidate.Handle);
			break;
		}
	}
}
```

1. **Lines 87–89:** The room of a pool is its budget minus what is resident, and the `min` keeps the subtraction from wrapping when more is resident than the budget holds.
2. **Lines 94–99:** A member not loaded yet whose pool does not fit goes into the left-out set.

Here is the rule in words. If all of a pool's members fit, they load and are pinned with the scene. If they do not, none of that pool's members load with the scene, because the load cannot know which part the scene draws first and any other part would take its room. A member that depends directly on a left-out member is skipped too, since requesting it would prefetch the left-out one into the same room; prefetches do not chain, so one level is enough. Members that are loaded already always count.

The scene then requests the skipped assets itself once it runs; `GetSkippedAssetCount` reports how many there were. The options carry a `RequiredProgress` between 0 and 1: the share of the stored bytes that must load before the state is Ready. The default 1 waits for everything in the group; 0 waits only for the scene.

:::example[Which pool fits]
A scene closure holds 40 textures of 20 MB stored, and 30 MB of meshes. The texture budget is 512 MB with 300 MB resident, so the room is 212 MB. With partial loads on, each texture counts at most 64 KB, so the 40 textures count about 2.5 MB: they fit, and load with the scene. With partial loads off, they count 800 MB, which exceeds 212 MB, so none of the textures loads with the scene, and neither does a material that uses one. The meshes are another pool, and may still load.
:::

After the switch, the owner of the load calls `ScheduleTrim` with the load's assets as the keep list. The trim after a switch removes what only the previous scene used, and spares what the load brought in, whether it was drawn yet or not.

### The editor's index of referencers

The table answers "what does this asset use?". Delete checks need the opposite. `EditorAssetManager::GetReferencers` answers from an inverse index kept on the main thread beside the recorded references, with no document read. It lists the scenes, prefabs, models and materials that use an asset, sorted by handle. Deletes refuse while something uses the asset; [the trash and its checks](../editor/trash-references.md) show how the editor runs them.

Engine documents carry records of their own, marked `Native`, per content. When such a file changes, its search starts only after `c_ReferenceSearchDelay`, 500 ms of quiet, so a file written over seconds is searched once. One search per document runs at a time, on an input and output job, and a newer change cancels the older search. A save passes the references it already has, so it needs no search.

### The script side

A script reaches the same machinery through `Assets`. `RequestLoad` starts a load and keeps the asset loaded while the scene plays; `Release` ends that. `GetLoadProgress` is the group load, as a script sees it.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L1528-L1539" symbol="ScriptSystem::GetAssetLoadProgress"
float ScriptSystem::GetAssetLoadProgress(AssetManagerBase& manager, AssetHandle asset)
{
	auto it = m_AssetGroups.find(asset);
	if (it == m_AssetGroups.end())
	{
		AssetGroupRequest group = manager.RequestLoadWithDependencies(asset, AssetPriority::Normal);
		if (!group.IsValid())
			return -1.0f;
		it = m_AssetGroups.emplace(asset, std::move(group)).first;
	}
	return it->second.Progress();
}
```

1. **Lines 1530–1536:** The first call for an asset makes its group at normal priority and stores it; an unknown asset returns -1.
2. **Line 1538:** Every call returns the group's progress.

The first call for an asset makes a group with `RequestLoadWithDependencies` at normal priority and keeps it. Later calls only read `Progress`. A null or unknown asset returns -1, and the host function reports the misuse. The group lives until `Release` or the end of play, so the assets stay pinned meanwhile. A script that asks for everything pins everything, and then there is no budget at all.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Scan every file at load | Engines whose assets are plain files | No stale records | Delete checks and exports that read every file |
| Hand-written manifests | Many small engines and bundle builders | Full control of what ships | Missed assets that appear as pink or silent holes |
| Prefetch the whole closure | Streaming systems with a fixed budget | The fastest first draw of a large scene | Peaks of 60 to 100 MB, and 12.6 GB across a world |
| Remove assets to make room for prefetch | Caches with strict recency | More prefetches succeed | Assets in use leave memory for a guess |
| Progress by count of assets | Simple loading screens | Simpler code | A bar that jumps when one large texture is last |

## How it is tested

Two suites in `StrataTests/src/Asset/AssetDependencyTests.cpp` cover this page. `Asset.Dependencies` checks that the feature scene's dependencies match what its entities reference, in the editor and in an exported pack. It also checks that engine documents record their references per content and follow their changes, and that recorded bounds are valid and finite or none. `Asset.Groups` checks that prefetch goes only into headroom, never chains and skips scenes, prefabs and models. It also checks that a group of a model, 10 materials and 20 textures progresses by bytes to completion, that cancelling stops the queued reads, and that a deleted member counts as failed.

Run them from the build folder with a doctest filter:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Asset.Dependencies,Asset.Groups
```

A regression test of a bug in these parts must fail without the fix, so write it first and run it against the old code.

## Changing it safely

A new asset type that stores references (a document) must record them: add its key to the scanner's document table, or have its importer return `References`. Then extend the tests so that the pruned export keeps the asset's references. A new component with an asset property needs nothing more than the property itself, because the scanner asks the registry.

Keep the table's meaning when you change code that reads it. A closure always lists the root first and each asset once, in breadth-first order, because group loads request in that order. A prefetch must never remove assets from memory, so any new path that starts one goes through `FitsPrefetchLocked`. Code that adds budgets must keep the saturating sum. Bounds that change are content changes, so go through `SetAssetReferences`, and run the two suites and `GPU.SceneRenderer.GPUDriven` after a change to what the renderer sees.

## Summary

- Strata records each asset's direct dependencies at import, or finds them by scanning documents as streams, and normalizes them: valid, once, never the asset itself. A type that records none loses its assets from pruned exports, and its deletes do not warn.
- A closure lists an asset and everything it uses, breadth first, each once. The `All` scope ships everything; the `Load` scope stops at other scenes.
- A prefetch loads direct dependencies into spare room only. It never removes assets from memory, never chains, skips documents, and never touches scenes.
- A group load pins its closure, and its progress counts stored bytes, so it never decreases.
- A scene load counts each pool with `EstimateFirstLoadBytes`; a pool whose share fits loads with the scene, and a pool that does not is left to the scene itself.

## Check yourself

1. Scene `A` uses prefab `P` and scene `B`. `P` uses mesh `M` and material `X`; `M` uses `X`; `X` uses texture `T`. `B` uses a mesh `N`. List the `Load` closure of `A` in order.

   :::answer{tests="closure"}
   `A`, `P`, `M`, `X`, `T`. The scan starts at `A`, adds `P` and skips `B` because it is a scene. `P` adds `M` and `X`, `M` finds `X` seen, and `X` adds `T`. `N` is never reached because only `B` uses it.
   :::

2. A group has three members of 10 KB, 30 KB and 60 KB stored. The 60 KB member finishes first, then the 10 KB one. What is the progress? What if the 30 KB member is deleted at that moment?

   :::answer{tests="progress"}
   70 %, since 70 KB of 100 KB finished. If the 30 KB member is deleted, it counts as failed, which counts as finished, so the progress becomes 100 % and `HasFailed` is true. The progress never goes down.
   :::

3. A pool has a 400 MB budget, 200 MB resident, 20 MB reserved and 60 MB on its way, and a 64 MB window. A 50 MB prefetch is tried, then a 10 MB one. What happens to each?

   :::answer{tests="prefetch"}
   The held sum is 200 + 20 + 60 + 64 = 344 MB, so the headroom is 56 MB. The 50 MB prefetch fits, and the pending sum grows to 110 MB. Now the held sum is 394 MB and the headroom 6 MB, so the 10 MB prefetch is refused.
   :::

4. A mesh is requested and its read completes. Its material uses a texture. Which assets does the manager prefetch?

   :::answer{tests="prefetch"}
   Only the material, its direct dependency. The material arrives only prefetched, so it prefetches nothing, and its texture waits until something requests the material. Prefetches do not chain.
   :::

5. A team adds a new document type for dialogue trees that name audio clips. They never record the references. Which follows: (a) the game crashes at load; (b) pruned exports omit the clips, and deleting a clip gives no warning; (c) the editor refuses to open the file?

   :::answer{tests="record"}
   (b). Only records tell exports, delete checks and prefetches what an asset uses. (a) is wrong because loading needs no record, and (c) is wrong because nothing checks it. The clips go missing at run time.
   :::

6. A scene's closure holds 30 textures of 10 MB stored and 100 MB of other assets. The texture pool has a 256 MB budget with 100 MB resident, and partial loads are on. Do the textures load with the scene?

   :::answer{tests="fit"}
   Yes. The room is 156 MB. Each texture counts at most 64 KB, so the 30 textures count under 2 MB. Without partial loads they would count 300 MB, which does not fit, so none would load with the scene.
   :::

## Exercises

1. **Basic.** In the toy, change `Intro` from a scene to an ordinary asset. Predict the `Load` closure, its order and its total stored size.

   :::answer[Worked solution]{tests="closure"}
   `Intro` no longer stops the walk. The order is `Outpost`, `Tower`, `MossTexture`, `Intro`, `TowerMesh`, `Stone`, `IntroMesh`, `StoneTexture`. The total is 40 + 8 + 2,000 + 30 + 600 + 2 + 1,000 + 4,000 = 7,680 KB.
   :::

2. **Medium.** Write a loading screen script that fills a bar by `Assets::GetLoadProgress` of a prefab, and places the prefab once the progress reaches 1. Say what limits how fast the bar fills.

   :::answer[Worked solution]{tests="progress"}
   The script is :term[pseudocode]{id=pseudocode}, because the engine's script classes need the engine:

   ```pseudocode
   class PrefabLoader : Script
       Prefab: asset field
       Bar: entity field
       Placed: bool, starts false

       OnUpdate(deltaTime):
           progress = Assets::GetLoadProgress(Prefab)
           if progress < 0:
               return
           set the Bar's fill amount to progress
           if progress >= 1 and not Placed:
               Scene::Instantiate(Prefab)
               Assets::Release(Prefab)
               Placed = true
   ```

   1. **Lines 7–9:** The first call starts the group load and pins the closure; a negative value means a null or unknown asset.
   2. **Lines 11–14:** At 1 the instance draws complete in its first frame; `Release` then ends the pin of the group.

   How fast the bar fills depends on the read speed, and on the upload steps and staging memory that [uploads](../assets/uploads.md) describes, and on the budgets a game cannot raise.
   :::

3. **Medium.** Trace it yourself. Learn which assets `Samples/Showcase/Assets/Scenes/Outpost.stscene` brings into a `Load` closure, and where that closure stops at another scene.

   :::answer[Worked solution]{tests="closure"}
   Set a breakpoint in `AssetManagerBase::GetDependencyClosureLocked` in `Strata/src/Strata/Asset/AssetManager.cpp` and open the sample. The list `closure` grows at the end while `index` moves along it, so the list is the queue. The `continue` for a scene dependency does not fire for `Outpost`: no component of it names another scene by handle, and the loading scene is set in the project. To see the scope stop, add a script field of asset type to the sample copy and point it at `Loading.stscene`. The check then skips it.
   :::

4. **Hard.** Show what goes wrong if the headroom sum does not saturate. Write a program that sets the window to the largest 64-bit number and compares a plain sum with a saturating one.

   :::answer[Worked solution]{tests="prefetch" solution="sketches/assets-references-saturate.cpp"}
   The plain sum of 600 and the largest number wraps round to 599, so a 100 request seems to fit in a budget of 1,000. The saturating sum stays at the largest number, and nothing fits. The program and its output:

   ```cpp sketch="assets-references-saturate.cpp"
   // A window set to the largest number: a plain sum wraps round to a small one, a saturating sum stays at the limit.
   #include <cstdint>
   #include <iostream>

   uint64_t SaturatingAdd(uint64_t a, uint64_t b)
   {
   	return b > UINT64_MAX - a ? UINT64_MAX : a + b;
   }

   // Whether `bytes` fit beside `held` in a budget.
   bool Fits(uint64_t budget, uint64_t held, uint64_t bytes)
   {
   	return held <= budget && bytes <= budget - held;
   }

   int main()
   {
   	const uint64_t budget = 1000;
   	const uint64_t resident = 600;
   	const uint64_t window = UINT64_MAX; // an in-flight window set to "anything"
   	const uint64_t request = 100;

   	const uint64_t plainHeld = resident + window;
   	const uint64_t saturatedHeld = SaturatingAdd(resident, window);
   	std::cout << "plain sum:      held " << plainHeld << ", fits " << Fits(budget, plainHeld, request) << '\n';
   	std::cout << "saturating sum: held " << saturatedHeld << ", fits " << Fits(budget, saturatedHeld, request) << '\n';
   }
   ```

   ```text output-of="assets-references-saturate.cpp"
   plain sum:      held 599, fits 1
   saturating sum: held 18446744073709551615, fits 0
   ```

   1. **Line 7:** A sum that would pass the largest number stops there.
   2. **Line 13:** The test is the engine's: refuse when the held sum is over the budget or the request exceeds what is left.
   3. **Line 20:** The window is set to the largest number on purpose.
   4. **Line 23:** The plain sum wraps round to 599.

   The wrapped sum passes the test by accident, which is the failure the saturating sum prevents.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetDependencies.h` and `AssetDependencies.cpp`: `AssetDependencies::Scan`, `ScanDocument`, `ScanEntity`, `ReferenceList`.
- `Strata/src/Strata/Asset/AssetImporter.h`: `ImportResult::References` and `Bounds`.
- `Strata/src/Strata/Asset/AssetManager.h` and `AssetManager.cpp`: `NormalizeReferences`, `SetAssetReferences`, `GetDependencyClosure`, `GetBounds`, `PrefetchDependencies`, `FitsPrefetchLocked`, `AssetGroupRequest`, `RequestLoadGroup`, `ReadStoredRange`, `EstimateFirstLoadBytes`, `ScheduleTrim`.
- `Strata/src/Strata/Scene/SceneLoader.h` and `SceneLoader.cpp`: `SceneLoadRequest`, `SceneLoadOptions::RequiredProgress`, `GetSkippedAssetCount`.
- `Strata/src/Strata/Asset/EditorAssetManager.h`: `GetReferencers`, `c_ReferenceSearchDelay`; `StrataEditor/src/Editor/AssetReferences.cpp`: what uses an asset, for delete checks.
- `StrataScriptCore/Include/StrataScript/Scene.h`: `Assets::RequestLoad`, `Release`, `GetLoadProgress`.
- Tests: `StrataTests/src/Asset/AssetDependencyTests.cpp`, suites `Asset.Dependencies` and `Asset.Groups`.

## Further reading

- Robert Nystrom, Game Programming Patterns, the chapter on the Object Pool and the Flyweight pattern (beginner): how games share and reuse loaded data.
- Jason Gregory, Game Engine Architecture, the chapter on the resource manager (intermediate): how an engine tracks the files a level needs and loads them in order.
- Thomas Cormen and others, Introduction to Algorithms, the chapter on elementary graph algorithms (intermediate): breadth-first search and its proof.
- Bruce Dawson, the blog on memory and virtual memory in games (advanced): why the peak of a prefetch matters and how to measure it.
