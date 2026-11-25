---
id: draw/render-scene
title: "The render scene: persistent proxies"
description: "How the renderer keeps its own record of every mesh in a scene, updates only what changed, and tells its readers what that was."
kind: internals
size: L
tracks: [E]
needs: [world/interpolation, world/sub-scenes, core/jobs]
time: 110
learn:
  - id: proxy-contents
    text: explain what a render proxy holds and why the renderer keeps proxies in arrays with stable indices
  - id: signal-rule
    text: explain why a write to a mesh renderer without a signal is a bug and how Validate finds it
  - id: log-readers
    text: predict from a reader's version, the floor and the log which proxies the reader must read
  - id: bounds-choice
    text: predict which bounds a proxy has from the state of its mesh
  - id: instance-size
    text: compute the memory of the instance array of a scene and the largest scene a draw list entry can name
since: 0.3.0
status: final
---

A scene stores a mesh as a component on an entity, and a frame needs that mesh as a row of numbers a :term[renderer]{id=renderer} can read fast. The **render scene** is the renderer's own copy of every mesh in one scene: one record per mesh entity, kept between frames and updated only where the scene changed. It also keeps the 64-byte records the :term[graphics processing unit]{id=gpu} (GPU) draws from, and a log of what changed that its readers follow. It does not cut away what is out of view, and it does not draw. Those jobs belong to [culling](bounds-culling.md) and to the passes that read the render scene.

## The problem and how engines solve it

A renderer needs, every frame, the world matrix, the bounds, the mesh and the material of each mesh in the scene. The scene holds them in components, spread over memory and changing rarely. [From entities to draws](entities-to-draws.md) compares the ways engines gather this data: walk the scene each frame, or keep a persistent copy and update it from change reports. Strata keeps the copy, because a scene of 100,000 cubes in which one cube moves should cost one update and not 100,000 reads. The price is a contract: the copy knows only what the scene reports, so code that changes the scene must report it.

## The map: one render scene, three kinds of reader

A **render proxy** is the renderer's record of one entity that has a `MeshRendererComponent`: its world matrix, its bounds, its mesh and material, some flags and its entity. The diagram shows where proxies come from and who reads them.

```mermaid caption="Signals and the scene's transform log feed the sync. The sync updates the proxies and the instances, and records each change in a log that the readers follow by version." alt="A diagram. Component signals fill a queue of pending entities. The queue, the scene's transform log and the asset manager's changes feed the sync. The sync writes the proxies, the instances and the lights, and records changes in three logs. Three readers follow the logs: the GPU copy, the shadow cache and the culling."
flowchart TD
	comp["MeshRendererComponent, SkinComponent"] -->|"on_construct, on_update, on_destroy"| pending["pending queue"]
	pending --> sync["RenderScene::Sync"]
	transforms["Scene world transform log"] --> sync
	assets["asset manager content changes"] --> sync
	sync --> proxies["proxy arrays"]
	sync --> instances["instance array"]
	sync --> lights["light records"]
	proxies --> logs["three change logs"]
	instances --> logs
	logs --> gpu["GPU copy"]
	logs --> shadows["shadow cache"]
	proxies --> culling["spatial index"]
```

One `RenderScene` exists per scene. `RenderScene::Get` makes it on first use and stores it in the registry's context, the place where an EnTT registry keeps one object of a type. Every renderer of that scene, whether it draws the editor's viewport, a capture or a thumbnail, shares it, so the work of a sync is done once. The :term[main thread]{id=main-thread} owns it: no job touches it, and no other thread calls `Sync`.

## The contract: what callers may assume and must do

The render scene reads two things: the entities whose mesh renderer was signaled, and the scene's log of changed :term[world transforms]{id=world-transform}. Everything else it does follows from them. The rules below state what that means for your code.

1. Code that writes fields of a `MeshRendererComponent`, or of a transform, signals the change. Use `Entity::MarkModified<T>()` or `registry.patch`. The reason is the one above: a write without a signal reaches neither source, so the proxy keeps the old values.
2. An entity that is created, changed through a signal or destroyed is read at the next sync, not when it is written. Values written right after `AddComponent` in the same frame are therefore seen.
3. Readers of the logs follow them by version and handle a refusal. A log answers "read everything" when the reader is too far behind.
4. A proxy index and an instance index are stable while their proxy lives, and they pass to another proxy when it is destroyed. Code that stores one across frames stores the entity with it.
5. Everything happens on the main thread.

:::rule[Signal every write]
`AGENTS.md` says that code writing `TransformComponent` fields, names, tags, `MeshRendererComponent` and light fields must signal the change. The reason is that the scene caches what it derives from them, and the render scene is one cache. Debug builds check it: after a sync, `Validate` rebuilds the proxies from the scene and compares. See [the scene graph](../world/scene-graph.md) for the transform contract itself.
:::

## A toy version: a proxy store

Before the real code, a small version does the same job for one field, a position. The toy keeps a dense array indexed by proxy, a list of free proxy indices, a queue of entities whose signal came, and a log of changed proxies. Read `MarkDirty` and `Sync` first: they are the signal and the sync. Then read `RecordChange`, which keeps the log's size bounded.

The toy introduces three words. A **change log** is a bounded list of version-stamped entries, each naming something that changed, which readers read to learn what changed since they last looked.

A **version** is a counter that grows by one with every logged change; a reader remembers the version it has read up to.

The **floor** is the newest version that the log may no longer hold: a reader whose version is below the floor missed entries and must read everything.

```cpp sketch="draw-render-scene-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <vector>

namespace Toy
{

	constexpr uint32_t c_Invalid = ~0u;
	constexpr size_t c_MaxChanges = 8;

	struct Change
	{
		uint64_t Version;
		uint32_t Proxy;
	};

	// Keeps its own copy of one field per entity, in a dense array indexed by proxy.
	class ProxyStore
	{
	public:
		void MarkDirty(uint32_t entity)
		{
			if (entity >= m_Queued.size())
				m_Queued.resize(entity + 1, false);
			if (m_Queued[entity])
				return;
			m_Queued[entity] = true;
			m_Pending.push_back(entity);
		}

		uint32_t Sync(const std::vector<float>& scene)
		{
			uint32_t updates = 0;
			for (const uint32_t entity : m_Pending)
			{
				m_Queued[entity] = false;
				uint32_t proxy = FindProxy(entity);
				if (proxy == c_Invalid)
					proxy = CreateProxy(entity);
				else if (m_Positions[proxy] == scene[entity])
					continue;
				m_Positions[proxy] = scene[entity];
				RecordChange(proxy);
				updates++;
			}
			m_Pending.clear();
			return updates;
		}

		void Destroy(uint32_t entity)
		{
			const uint32_t proxy = FindProxy(entity);
			m_ByEntity[entity] = c_Invalid;
			m_Entities[proxy] = c_Invalid;
			m_FreeProxies.push_back(proxy);
			RecordChange(proxy);
		}

		uint32_t FindProxy(uint32_t entity) const { return entity < m_ByEntity.size() ? m_ByEntity[entity] : c_Invalid; }
		uint64_t GetVersion() const { return m_Version; }

		bool GetChanges(uint64_t since, std::vector<uint32_t>& out) const
		{
			if (since < m_Floor)
				return false;
			for (const Change& change : m_Changes)
			{
				if (change.Version > since)
					out.push_back(change.Proxy);
			}
			return true;
		}
	private:
		uint32_t CreateProxy(uint32_t entity)
		{
			uint32_t proxy = static_cast<uint32_t>(m_Entities.size());
			if (!m_FreeProxies.empty())
			{
				proxy = m_FreeProxies.back();
				m_FreeProxies.pop_back();
			}
			else
			{
				m_Entities.push_back(c_Invalid);
				m_Positions.push_back(0.0f);
			}
			m_Entities[proxy] = entity;
			if (entity >= m_ByEntity.size())
				m_ByEntity.resize(entity + 1, c_Invalid);
			m_ByEntity[entity] = proxy;
			return proxy;
		}

		void RecordChange(uint32_t proxy)
		{
			m_Changes.push_back(Change { ++m_Version, proxy });
			if (m_Changes.size() > c_MaxChanges)
			{
				m_Floor = m_Changes.front().Version;
				m_Changes.erase(m_Changes.begin());
			}
		}

		std::vector<uint32_t> m_Entities;
		std::vector<float> m_Positions;
		std::vector<uint32_t> m_FreeProxies;
		std::vector<uint32_t> m_ByEntity;
		std::vector<bool> m_Queued;
		std::vector<uint32_t> m_Pending;
		std::vector<Change> m_Changes;
		uint64_t m_Version = 0;
		uint64_t m_Floor = 0;
	};

}

int main()
{
	std::vector<float> scene = { 0.0f, 2.0f, 4.0f, 6.0f, 8.0f, 10.0f };
	Toy::ProxyStore store;
	for (uint32_t entity = 0; entity < 5; entity++)
		store.MarkDirty(entity);
	std::printf("first sync: %u updates\n", store.Sync(scene));
	std::printf("still sync: %u updates\n", store.Sync(scene));

	const uint64_t seen = store.GetVersion();
	scene[3] += 1.0f;
	store.MarkDirty(3);
	store.MarkDirty(3);
	std::vector<uint32_t> changed;
	std::printf("one move, signaled twice: %u update\n", store.Sync(scene));
	const bool followed = store.GetChanges(seen, changed);
	std::printf("reader at version %llu: followed %d, changed %zu, proxy %u\n", static_cast<unsigned long long>(seen), followed, changed.size(), changed[0]);

	store.Destroy(1);
	store.MarkDirty(5);
	store.Sync(scene);
	std::printf("entity 5 took the proxy of entity 1: proxy %u\n", store.FindProxy(5));

	for (int move = 0; move < 8; move++)
	{
		scene[0] += 1.0f;
		store.MarkDirty(0);
		store.Sync(scene);
	}
	changed.clear();
	std::printf("version %llu: the reader at %llu %s\n", static_cast<unsigned long long>(store.GetVersion()), static_cast<unsigned long long>(seen),
		store.GetChanges(seen, changed) ? "follows the log" : "must read everything");
}
```

1. **Lines 21–29:** `MarkDirty` queues an entity once, however often its signal comes. The `m_Queued` flags do this.
2. **Lines 37–44:** `Sync` creates a proxy for an entity that has none, and skips a proxy whose value did not change. That comparison is why a still scene updates nothing.
3. **Lines 64–65:** `GetChanges` refuses when `since` lies below the floor. It appends nothing and the reader reads everything.
4. **Lines 77–80:** `CreateProxy` takes the newest free index before it grows the arrays, so indices stay dense.
5. **Lines 96–101:** `RecordChange` raises the version and drops the oldest entry when the log is full. The floor becomes the version of the entry it dropped.

```text output-of="draw-render-scene-toy.cpp"
first sync: 5 updates
still sync: 0 updates
one move, signaled twice: 1 update
reader at version 5: followed 1, changed 1, proxy 3
entity 5 took the proxy of entity 1: proxy 1
version 16: the reader at 5 must read everything
```

The output follows the signals. Five signals build five proxies; a second sync finds nothing to do. Two signals for entity 3 cause one update, and the reader that stood at version 5 learns of one changed proxy, number 3. Entity 5 takes the proxy that entity 1 freed. After eight more changes the log holds only its newest eight entries, so the reader at version 5 sits below the floor and must read everything.

## The real code: proxies as columns

The class comment is the whole design in prose. Read it once now; the sections below follow it in the order that data flows. It names the contract (lines 80 to 83), mesh layouts and unknown bounds (85 to 98), skinning (100 to 108) and the three logs (110 to 112).

```cpp src="Strata/src/Strata/Renderer/RenderScene.h#L75-L115"
// The renderer's persistent view of a scene's mesh renderers: one render proxy per entity with a MeshRendererComponent,
// kept in structure-of-arrays form (world transform, world bounds, mesh, material override, flags, entity ID) and in a
// spatial index, plus the GPU instance data of every proxy submesh whose mesh layout is known. Sync updates only what
// changed since the previous sync: entities whose MeshRendererComponent was created, signaled (on_update) or destroyed,
// and entities whose world transform or activity changed (Scene::GetWorldTransformChanges; a full comparison when the
// scene no longer knows). The contract is the transform contract's: code that writes MeshRendererComponent fields of an
// entity created before the last sync must signal it (Entity::MarkModified, registry.patch; ComponentAccess does);
// Debug builds validate the proxies after syncs (Validate): after every one for render scenes of up to
// c_ValidatedProxiesPerSync proxies, every few for larger ones.
//
// Mesh layouts (bounds, submeshes and their materials) are learned from loaded meshes (SetMeshLayout) and kept when
// a mesh is evicted, so proxies keep their bounds and instance slots. Sync keeps them current with the asset manager
// whatever the renderers see: the meshes whose objects or sources changed since the previous sync (the manager's
// content changes, read against the render scene's own content version, so a scene that was not rendered for a while
// catches up) and the meshes new to the scene are compared with their loaded objects. A mesh that is not loaded keeps
// its layout while its source is the one the layout was learned from (AssetSourceRevisions); one reimported while it
// was not loaded loses it, so its new bounds are not culled with the old ones. Until a mesh's layout is known, the
// bounds the asset database recorded for it stand in (ResolveUnloadedBounds: imported meshes and the meshes of packs
// have them). A mesh with neither (a mesh the manager does not know, a record without bounds) has unknown bounds
// (GetMeshesWithoutBounds): its proxies sit in the spatial index with placeholder bounds around their entities, which
// say nothing about where the mesh is, so renderers request such a mesh as if it were in view while any of its proxies
// is active (GetIndexedUserCount) - a terrain whose origin is out of view may well fill it. Its layout follows once it
// loads. Materials and meshes get dense slots shared by all proxies that use them; instance data refers to material
// slots, whose GPU data each renderer resolves per frame.
//
// Skinned meshes: a proxy whose entity has a SkinComponent and whose mesh layout has a skin binding is posed when the
// scene's ISkinningPoses service (Scene/SceneServices.h: the animation system, the editor's pose preview) has a pose for
// its animator. Sync then computes its palette - per joint of the mesh's skin, the inverse of the proxy's world
// transform times the animator's, times the joint's model-space transform, times its inverse bind matrix - into a
// palette range of its own (GetPalette, logged by version like the instances, so renderers upload only what changed),
// and its posed bounds: the union of each joint's bind-pose extent (MeshSkinBinding::JointBounds) transformed by its
// palette entry. Palettes are recomputed only when the pose's version or the transform from the animator to the proxy
// changes, in parallel chunks. Posed proxies carry RenderProxyFlags::Skinned and their instances c_InstanceSkinned with
// the palette's first joint (InstanceData::SkinPalette); the skinned pipelines blend it in the vertex shader.
//
// Readers follow the scene through three bounded change logs, by version: the instances (GetInstanceChanges), the
// palettes (GetPaletteChanges) and the proxies themselves (GetProxyChanges: placement, flags, mesh slot, instance range,
// creation and destruction), which the GPU's culling mirrors.
//
// One per scene, created on first use (Get) in the scene's registry context and shared by every renderer of the scene
// (the viewport and capture renderers). Main thread only.
```

1. **Lines 75–77:** one render proxy per mesh renderer, kept in structure-of-arrays form and in a spatial index.
2. **Lines 78–80:** a sync updates only the signaled entities and the entities whose transform or activity changed, and falls back to a full comparison when the scene no longer knows.
3. **Lines 80–83:** the contract is the transform contract's, and Debug builds validate after syncs.
4. **Lines 114–115:** one per scene, shared by its renderers, main thread only.

A proxy lives in many arrays that share one index. `m_Entities`, `m_Flags`, `m_Transforms`, `m_WorldBounds`, `m_MeshSlots`, `m_FirstInstances` and a dozen more each hold one field, and the proxy index is the row. Compare an :term[array of structs]{id=array-of-structs}, one record per proxy with every field inside. A pass that tests bounds would then read the matrix, the handles and the flags of every proxy to reach the 24 :term[bytes]{id=byte} it needs. With columns, it reads the bounds array and nothing else.

| Proxy | Entity | Flags | Mesh slot | First instance | Instance count |
| --- | --- | --- | --- | --- | --- |
| 0 | 12 | active, indexed | 0 | 0 | 1 |
| 1 | 31 | active, indexed | 0 | 1 | 1 |
| 2 | none (free) | none | none | none | 0 |
| 3 | 40 | inactive | 1 | 2 | 3 |

The table shows four proxies of one scene. Proxy 2 is free: its entity is null and its index waits in `m_FreeProxies`. `CreateProxy` takes the newest free index and, only when none is free, appends a row to every array. `DestroyProxy` does the reverse: it frees the proxy's instances and its slots, clears the row and pushes the index on the :term[free list]{id=free-list}. Nothing moves, so the indices of other proxies hold.

The cost of stable indices is that an index changes hands. Proxy 2 may serve entity 77 next frame. A cache that stores a proxy index must therefore store the entity it belongs to and compare. The level-of-detail fade state does this: `LODSelection.cpp` continues a fade only when `state.EntityID == entityID`.

Each proxy has flags. `Active` is set when the entity is active in the hierarchy; `CastShadows` copies the component's field. `Mirrored` marks a negative determinant and `Indexed` marks membership in the spatial index. `MeshBounds` says the bounds come from the mesh and not a placeholder, and `Skin` and `Skinned` mark an entity with a skin and a posed one. [Skinned meshes](skinned.md) take the last two further.

A **slot** is a small dense :term[integer]{id=integer} that stands for one asset handle the scene uses. Every distinct mesh and every distinct material in use gets one, shared by all proxies that use it. `AcquireMesh` finds the handle's slot or takes a free one, and `ReleaseMesh` removes the proxy from the mesh's list of users with a :term[swap-remove]{id=swap-remove}: the last user moves into the hole. When the last user leaves, the slot is cleared and joins the free list. `GetSlotsVersion` changes whenever a slot is taken or let go, so a cache keyed by slot knows to compare handles again.

In the test of 100,000 cubes that this page reads at its end, all share the cube mesh, so the render scene holds one mesh slot with 100,000 users. A scene of 100,000 different meshes holds 100,000 slots. The instance data stores the 4-byte material slot, not the handle, and each renderer resolves the slot to its GPU data once per frame.

## The real code: from signal to proxy

The scene tells the render scene about changes through EnTT's signals. `ConnectListeners` connects `on_construct`, `on_update` and `on_destroy` of `MeshRendererComponent`, and the same three of `SkinComponent`. The connections are never released: the registry's context is destroyed after the storages and their signals, so nothing is left to disconnect from.

A construct or update signal queues the entity. A destroy signal drops it from the queue and destroys its proxy at once, because the component is about to disappear. The queue is the part to read closely.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L219-L246"
void RenderScene::QueuePending(entt::entity entity)
{
	const size_t index = static_cast<size_t>(entt::to_entity(entity));
	if (index >= m_PendingPositions.size())
		m_PendingPositions.resize(index + 1, c_InvalidIndex);
	const uint32_t position = m_PendingPositions[index];
	if (position != c_InvalidIndex)
	{
		// Queued already. An entity's index is queued for one entity at a time: the one that holds it now.
		m_Pending[position] = entity;
		return;
	}
	m_PendingPositions[index] = static_cast<uint32_t>(m_Pending.size());
	m_Pending.push_back(entity);
}

void RenderScene::DropPending(entt::entity entity)
{
	const size_t index = static_cast<size_t>(entt::to_entity(entity));
	if (index >= m_PendingPositions.size() || m_PendingPositions[index] == c_InvalidIndex)
		return;
	const uint32_t position = m_PendingPositions[index];
	const entt::entity moved = m_Pending.back();
	m_Pending[position] = moved;
	m_PendingPositions[static_cast<size_t>(entt::to_entity(moved))] = position;
	m_Pending.pop_back();
	m_PendingPositions[index] = c_InvalidIndex;
}
```

1. **Lines 221–224:** `m_PendingPositions` is indexed by the entity's index and holds its place in `m_Pending`, or the invalid value.
2. **Lines 225–230:** an entity that is queued already is not queued again; an index that another entity now holds replaces the old entity in its place.
3. **Lines 235–245:** `DropPending` removes in :term[constant time]{id=constant-time}: the last entry moves into the hole and its recorded position is updated.

The effect is that a scene changed a thousand times between two syncs queues each entity once. The test `Signals queue each entity once, however often they come before the next sync` signals 10 cubes in 1,000 rounds, adds and destroys a cube each round, and ends with a queue of 10.

### Sync, in order

`Sync` is the heart. It runs these steps in order. The scene updates its world and :term[drawn transforms]{id=drawn-transform}, and the pose provider's render transforms are applied. The pending entities are read. Then the world-transform log is read, or every proxy is compared.

Next the :term[interpolated]{id=interpolation} entities are placed again if the drawn matrices changed. Lights, mesh layouts, skinned poses and the spatial index are refreshed, and Debug builds validate. The first quote holds the first half.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L326-L371"
uint32_t RenderScene::Sync(const Ref<AssetManagerBase>& assets, uint32_t maxPending)
{
	ST_PROFILE_FUNCTION();
	// The world transforms, then the drawn ones (a scene that interpolates: Scene::UpdateDrawnTransforms), which every proxy
	// write below reads through GetDrawnTransform.
	m_Scene->UpdateDrawnTransforms();
	m_SyncCount++;
	m_SyncUpdates = 0;
	entt::registry& registry = m_Scene->GetRegistry();
	UpdateRenderTransforms(m_Scene->GetService<ISkinningPoses>());

	m_PendingScratch.clear();
	if (m_Pending.size() <= maxPending)
	{
		m_PendingScratch.swap(m_Pending);
	}
	else
	{
		// The latest queued, so that the others keep their places in the queue.
		m_PendingScratch.assign(m_Pending.end() - maxPending, m_Pending.end());
		m_Pending.resize(m_Pending.size() - maxPending);
	}
	for (const entt::entity entity : m_PendingScratch)
		m_PendingPositions[static_cast<size_t>(entt::to_entity(entity))] = c_InvalidIndex;
	for (const entt::entity entity : m_PendingScratch)
		UpdateProxyFromEntity(entity);

	m_ChangeScratch.clear();
	const bool transformsLogged = !m_RefreshTransforms && m_Scene->GetWorldTransformChanges(m_TransformsVersion, m_ChangeScratch);
	if (transformsLogged)
	{
		for (const entt::entity entity : m_ChangeScratch)
		{
			const uint32_t proxy = FindProxy(entity);
			if (proxy == c_InvalidIndex)
				continue;
			const WorldTransformComponent& world = registry.get<WorldTransformComponent>(entity);
			UpdateProxyTransform(proxy, GetDrawnTransform(entity, world), world.ActiveInHierarchy, false);
		}
	}
	else
	{
		FullRefresh();
		m_RefreshTransforms = false;
	}
	m_TransformsVersion = m_Scene->GetTransformsVersion();
```

1. **Lines 338–351:** the pending queue is swapped out, or only its latest `maxPending` entries are taken. `Prepare` uses the limit. Each entity is read by `UpdateProxyFromEntity`.
2. **Lines 354–365:** the render scene asks the scene for the world-transform changes since its own transforms version. Each changed entity with a proxy is placed again at its drawn transform.
3. **Lines 366–370:** when the scene answers that it no longer knows, `FullRefresh` compares every proxy. The statistics count these as `FullRefreshes`.

`UpdateProxyFromEntity` creates a proxy for a new entity, and compares the mesh handle, the material override, the shadow flag and the skin with what the proxy holds. When nothing differs, it only tries the transform. When something differs, the proxy is placed again and its instances are rebuilt. A changed mesh releases its old slot first. A changed material override acquires its new slot before it releases the old one, so a slot that both use survives.

A proxy is placed where the scene draws the entity. `GetDrawnTransform` looks first at the render transforms of a pose provider, then at the scene's drawn transform, then at the world matrix. The first covers a provider that may not write the scene, such as the editor's pose preview, which can draw an attachment at a joint. The second is [interpolation](../world/interpolation.md).

Between two :term[fixed steps]{id=fixed-step} a moving entity is drawn between its last two poses. The proxies of the :term[interpolated set]{id=interpolated-set} are therefore placed again on every frame in which the drawn matrices change, step or no step.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L372-L411"
	// What the fixed steps moved is drawn between their poses: placed again whenever the drawn matrices changed (on every
	// frame while something moves, also without a step). Unchanged matrices compare equal (UpdateProxyTransform).
	const bool drawnChanged = m_Scene->GetDrawnTransformsVersion() != m_DrawnVersion;
	if (drawnChanged)
	{
		for (const entt::entity entity : m_Scene->GetInterpolatedEntities())
		{
			if (!registry.valid(entity))
				continue;
			const uint32_t proxy = FindProxy(entity);
			if (proxy == c_InvalidIndex)
				continue;
			const WorldTransformComponent& world = registry.get<WorldTransformComponent>(entity);
			UpdateProxyTransform(proxy, GetDrawnTransform(entity, world), world.ActiveInHierarchy, false);
		}
		m_DrawnVersion = m_Scene->GetDrawnTransformsVersion();
	}
	m_Lights.Sync(*m_Scene, m_ChangeScratch, !transformsLogged, drawnChanged);
	UpdateMeshLayouts(assets);
	UpdateSkinnedPoses();
	m_Index.Refresh();
	m_Stats.LastSyncUpdates = m_SyncUpdates;
	m_Stats.TotalUpdates += m_SyncUpdates;

#ifdef ST_DEBUG
	// Entities a partial sync left queued have no proxies yet (or older ones): the proxies match the scene once all are read.
	// Paced by the render scene's size (c_ValidatedProxiesPerSync).
	if (m_Pending.empty() && m_ValidationCheck.IsDue(m_Entities.size()))
	{
		m_ValidationCount++;
		std::string error;
		if (!Validate(&error))
		{
			ST_CORE_ASSERT(false, "The render proxies of scene '{}' differ from the scene (was a MeshRendererComponent written without a signal?): {}",
				m_Scene->GetName(), error);
		}
	}
#endif
	return m_SyncUpdates;
}
```

1. **Lines 374–388:** the interpolated set is walked only when the scene's drawn-transforms version moved. Matrices that did not change compare equal and cost no update.
2. **Lines 389–393:** lights, mesh layouts, skinned poses and the spatial index follow, and the statistics take the update count.
3. **Lines 399–408:** in Debug builds, when no entity is still queued and the paced check is due, `Validate` runs, and a difference stops the program with a message that names the likely cause.

The check is paced because it costs about as much as rebuilding every proxy. `AmortizedCheck` counts calls, not time: every sync validates a scene of up to `c_ValidatedProxiesPerSync` (1,024) proxies, and a larger scene validates at the first sync and then once enough budget has gathered. For the 100,000-cube scene, that is every 98th sync.

## The real code: placement and bounds

`UpdateProxyPlacement` turns a world matrix into flags and bounds. Its first lines take the matrix's determinant, a number whose sign says whether the matrix mirrors space. A negative sign sets `Mirrored`; [mirrors and camera-relative space](mirrors-camera-relative.md) teaches what follows. A zero or non-finite determinant, below $10^{-12}$ in absolute value, gives a proxy that cannot be drawn: it shows nothing and does not enter the spatial index.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L663-L700"
void RenderScene::UpdateProxyPlacement(uint32_t proxy)
{
	RecordProxyChange(proxy);
	const glm::mat4 world = m_Transforms[proxy].ToMatrix();
	const float determinant = glm::determinant(glm::mat3(world));
	const bool active = (m_Flags[proxy] & RenderProxyFlags::Active) != 0;
	const uint32_t meshSlot = m_MeshSlots[proxy];
	const MeshEntry* mesh = meshSlot != c_InvalidIndex ? &m_Meshes[meshSlot] : nullptr;

	uint32_t flags = m_Flags[proxy] & (RenderProxyFlags::Active | RenderProxyFlags::CastShadows | RenderProxyFlags::Skin | RenderProxyFlags::Skinned
		| RenderProxyFlags::LightSurface);
	if (determinant < 0.0f)
		flags |= RenderProxyFlags::Mirrored;
	if (mesh && (mesh->LayoutKnown || mesh->RecordedBounds))
		flags |= RenderProxyFlags::MeshBounds;
	if ((flags & RenderProxyFlags::Skinned) != 0)
		m_LocalBounds[proxy] = m_Skins[m_SkinIndices[proxy]].PosedBounds; // Posed: where its joints put the vertices
	else if (mesh && mesh->LayoutKnown)
		m_LocalBounds[proxy] = mesh->Bounds;
	else if (mesh && mesh->RecordedBounds)
		m_LocalBounds[proxy] = *mesh->RecordedBounds;
	else
		m_LocalBounds[proxy] = GetPlaceholderBounds();

	// Zero scale and non-finite transforms show nothing.
	const bool drawable = active && mesh && std::isfinite(determinant) && std::abs(determinant) >= c_MinDeterminant && IsFiniteMatrix(world);
	m_WorldBounds[proxy] = drawable ? m_LocalBounds[proxy].Transformed(world) : AABB();
	const bool indexed = drawable && m_WorldBounds[proxy].IsValid() && IsFiniteBox(m_WorldBounds[proxy]);
	// The mesh counts its indexed users: a proxy counts for the mesh it has while it carries the Indexed flag
	// (ReleaseMesh takes it away from the mesh it leaves).
	const bool wasIndexed = (m_Flags[proxy] & RenderProxyFlags::Indexed) != 0;
	if (indexed != wasIndexed)
	{
		ST_CORE_ASSERT(meshSlot != c_InvalidIndex, "RenderScene: proxy {} is counted as indexed without a mesh", proxy);
		if (indexed)
			m_Meshes[meshSlot].IndexedUsers++;
		else
			m_Meshes[meshSlot].IndexedUsers--;
```

1. **Lines 674–675:** the sign of the determinant sets `Mirrored`.
2. **Lines 678–685:** the local bounds come from the pose, else from the mesh layout, else from the recorded bounds, else from a placeholder.
3. **Lines 688–690:** a proxy can be drawn only when it is active, has a mesh, and its transform is finite and not flat. Then its world bounds are the local bounds transformed by the matrix.

The choice of bounds needs three terms. A **mesh layout** is what the render scene learns from a loaded mesh: its bounds, its submeshes and the material of each.

**Recorded bounds** are the bounds the asset database stored for a mesh at import time or in a pack's table, which place a mesh before it ever loads.

**Placeholder bounds** are a box from $-1$ to $1$ on each axis around the entity's origin, moved and scaled with it, that stand in when a mesh has neither.

:::example[Which bounds does a cube proxy have?]
Take the 100,000 cubes of the page's test, first synced with no asset manager. The cube mesh is not loaded, so the mesh has no layout and no recorded bounds. Each proxy gets placeholder bounds: a box from $-1$ to $1$ on each axis around its entity. A cube at height 0.5 gets a world box that spans $y$ from $-0.5$ to 1.5.

The mesh has unknown bounds, so the render scene lists its slot in `GetMeshesWithoutBounds`, and the test reads that the list holds one slot. Renderers request such a mesh as if it were in view while any proxy of it is active. A terrain whose origin lies out of view still loads and appears.

Then `SetMeshLayout` learns the cube's real bounds, a box of 1 unit. It returns 100,000, the number of proxies updated. The same cube now has a world box that spans $y$ from 0 to 1, the list is empty, and the proxies hold their instances. After the test moves one cube up by 1.0, that cube's box spans $y$ from 1.0 to 2.0. Calling `SetMeshLayout` again with the same mesh returns 0: nothing differs.
:::

```mermaid caption="The proxy's bounds come from the first source that has them. A mesh with no source stays visible through placeholder bounds." alt="A decision list from top to bottom. A posed proxy takes the bounds of its pose. Otherwise a known mesh layout gives the mesh bounds. Otherwise recorded bounds give the recorded box. Otherwise the proxy gets a placeholder box of one unit around the entity, and its mesh is requested as if in view."
flowchart TD
	a{"posed?"} -->|"yes"| pose["bounds of the pose"]
	a -->|"no"| b{"layout known?"}
	b -->|"yes"| layout["bounds of the layout"]
	b -->|"no"| c{"recorded bounds?"}
	c -->|"yes"| recorded["recorded bounds"]
	c -->|"no"| placeholder["placeholder box; mesh requested as if in view"]
```

### Layouts follow the asset manager

A layout is learned from a loaded mesh by `SetMeshLayout`, and it stays when the mesh is dropped from memory, so the proxies keep their bounds and their instances. Each sync compares the layouts with the asset manager. It reads the manager's content version and asks which assets changed since. If the manager no longer remembers that far back, it checks every layout. A render scene that was not rendered for a while catches up this way.

One case needs care. A mesh that is not loaded keeps its layout only while its source is the one the layout came from. If the mesh was imported again while it was not loaded, its new bounds may differ. Keeping the old layout would hide the mesh with the wrong box. `CheckMeshLayout` compares the source revision, forgets the layout, and falls back to recorded bounds or placeholders until the mesh loads again.

## The real code: instances

An **instance** is one drawn submesh of a proxy: a 64-byte `InstanceData` record in one persistent array. A mesh with three submeshes gives a proxy three consecutive instances; a proxy whose mesh layout is unknown has none, and the layout's arrival creates them.

```cpp src="Strata/src/Strata/Renderer/SceneRenderData.h#L198-L227"
// One drawn submesh of a render proxy (RenderScene). The buffer of instances persists between frames; draws read
// it through the frame's draw list, which holds an entry (MakeDrawEntry) per drawn instance.
struct InstanceData
{
	AffineTransform World;
	uint32_t MaterialIndex; // Material slot (RenderScene::GetMaterialHandle), index into the material buffer
	uint32_t EntityID;      // Entity identifier + 1 (0 = none)
	uint32_t Flags;         // c_Instance*
	// Posed instances (c_InstanceSkinned): the first joint matrix of the proxy's palette in the joint buffer
	// (RenderScene::GetPalette, uploaded where it changed), one per joint of the mesh's skin; 0 otherwise.
	uint32_t SkinPalette;
};
static_assert(sizeof(InstanceData) == 64);

// A draw list entry (the u_DrawList the scene's vertex shaders read): the instance in the low c_DrawEntryInstanceBits, and
// above them the level-of-detail cross-fade code of the draw (LODSelection::UpdateLODFade): 0 draws every pixel, 1 to
// c_LODFadeFrames - 1 the level fading in (on the pixels whose LODSelection::GetLODFadeThreshold is below the code), the
// same plus c_LODFadeOutgoing the level fading out (on the others). Render scenes hold at most c_MaxRenderInstances
// instances.
constexpr uint32_t c_DrawEntryInstanceBits = 27;
constexpr uint32_t c_DrawEntryInstanceMask = (1u << c_DrawEntryInstanceBits) - 1;
constexpr uint32_t c_MaxRenderInstances = 1u << c_DrawEntryInstanceBits;
constexpr uint32_t c_LODFadeFrames = 16; // A fade's steps: the 4x4 dither's 16 thresholds
constexpr uint32_t c_LODFadeOutgoing = 16;
static_assert(c_LODFadeOutgoing + c_LODFadeFrames <= (1u << (32 - c_DrawEntryInstanceBits)));

constexpr uint32_t MakeDrawEntry(uint32_t instance, uint32_t fadeCode)
{
	return instance | (fadeCode << c_DrawEntryInstanceBits);
}
```

1. **Lines 200–209:** three rows of an affine matrix (48 bytes), then four 32-bit fields: material slot, entity identifier (ID) plus one, flags and the skin palette's first joint.
2. **Line 210:** the size is checked at :term[compile time]{id=compile-time}. Every pass reads this record per instance, so growth costs bandwidth everywhere.
3. **Lines 217–219:** a draw list entry holds the instance in its low 27 bits, so a scene holds at most $2^{27}$ instances.
4. **Lines 224–227:** the five bits above carry the level-of-detail fade code.

```mermaid caption="An instance record is 48 bytes of matrix rows and four fields of 4 bytes. A draw list entry splits one 32-bit number into the instance and a fade code." alt="Two bars. The first bar, 64 bytes, holds three matrix rows of 16 bytes each, then the material slot, the entity identifier, the flags and the skin palette of 4 bytes each. The second bar, 32 bits, holds a 5-bit fade code above a 27-bit instance number."
flowchart LR
	subgraph record["InstanceData, 64 bytes"]
		direction LR
		r0["row 0: 16"] --- r1["row 1: 16"] --- r2["row 2: 16"] --- m["material slot: 4"] --- e["entity ID: 4"] --- f["flags: 4"] --- s["skin palette: 4"]
	end
	subgraph entry["draw list entry, 32 bits"]
		direction LR
		fade["fade code: 5 bits"] --- inst["instance: 27 bits"]
	end
```

The numbers decide the limits. A 4 by 4 float matrix alone is 64 bytes, so the 3 by 4 form saves the matrix's fourth row, which is always (0, 0, 0, 1), and leaves room for four fields. The array for the 100,000 cubes holds $100\,000 \times 64 = 6\,400\,000$ bytes, 6.4 MB. The largest scene is $2^{27} = 134\,217\,728$ instances of 64 bytes each, which is $2^{33}$ bytes, 8 GiB. `AllocateInstances` logs once and gives a proxy none when its instances would not fit; `SetInstanceLimit` lets a test lower the limit, and clamps a higher one to the format's.

Instances of one proxy are allocated as a range. `FreeInstances` pushes a range's first index on a list keyed by the range's length, and `AllocateInstances` takes from the list for the same length before it grows the array. A proxy that changes mesh may therefore take the range that a destroyed one left.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L1123-L1151"
void RenderScene::WriteInstances(uint32_t proxy)
{
	const uint32_t count = m_InstanceCounts[proxy];
	if (count == 0)
		return;
	const uint32_t first = m_FirstInstances[proxy];
	const MeshEntry& mesh = m_Meshes[m_MeshSlots[proxy]];
	const uint32_t overrideSlot = m_OverrideSlots[proxy];
	RenderData::InstanceData data = {};
	data.World = m_Transforms[proxy];
	data.EntityID = m_EntityIDs[proxy];
	data.Flags = (m_Flags[proxy] & RenderProxyFlags::Mirrored) != 0 ? RenderData::c_InstanceMirrored : 0u;
	if ((m_Flags[proxy] & RenderProxyFlags::Skinned) != 0)
	{
		data.Flags |= RenderData::c_InstanceSkinned;
		data.SkinPalette = m_Skins[m_SkinIndices[proxy]].PaletteFirst;
	}
	if ((m_Flags[proxy] & RenderProxyFlags::LightSurface) != 0)
		data.Flags |= RenderData::c_InstanceLightSurface;
	for (uint32_t index = 0; index < count; index++)
	{
		data.MaterialIndex = overrideSlot != c_InvalidIndex ? overrideSlot : mesh.SubmeshMaterialSlots[index];
		RenderData::InstanceData& instance = m_Instances[first + index];
		if (SameBytes(instance, data))
			continue;
		instance = data;
		RecordInstanceChanges(first + index, 1);
	}
}
```

1. **Lines 1131–1141:** one record is built for the proxy: matrix, entity, and the mirrored, skinned and `LightSurface` flags.
2. **Lines 1144–1146:** the material slot is the override's, or the submesh's own. `SameBytes` compares the new bytes with the stored ones, and an equal instance is skipped.
3. **Line 1149:** only a changed instance is logged. A sync that finds the same matrix writes nothing and tells no reader.

The rule behind line 210 is this: `InstanceData` stays 64 bytes. A per-instance addition goes to a parallel buffer indexed by the instance, as the level-of-detail fade state is.

## The real code: change logs

Readers need to know what changed without comparing everything. Two obvious designs exist. A :term[dirty flag]{id=dirty-flag} per item is cheap to set and works for one reader, but each reader needs its own flags and must clear them. A log with versions serves many readers: each remembers a version and reads the entries after it. Strata keeps three bounded logs, for instances, proxies and palettes, each holding at most 65,536 entries.

The proxy log shows the idea best. `RecordProxyChange` is called for every placement, flag, mesh slot, instance range, creation and destruction. It raises the proxy version, appends an entry, and when the log is full, drops the oldest entries and sets the floor to the newest version dropped. `GetProxyChanges(since, out)` returns false, with nothing appended, when `since` is below the floor.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L1213-L1247"
void RenderScene::RecordProxyChange(uint32_t proxy)
{
	if (m_ProxyLoggedVersions.size() <= proxy)
		m_ProxyLoggedVersions.resize(proxy + 1, 0);
	// Logged and not read by anyone since: the entry already tells its readers.
	if (m_ProxyLoggedVersions[proxy] > m_ProxyChangesRead)
		return;
	m_ProxyVersion++;
	m_ProxyLoggedVersions[proxy] = m_ProxyVersion;
	const size_t live = m_ProxyChanges.size() - m_ProxyChangesStart;
	if (live + 1 > c_MaxProxyChanges)
	{
		// Readers further behind than the oldest change kept read everything.
		m_ProxyChangesStart += live + 1 - c_MaxProxyChanges;
		m_ProxyChangesFloor = m_ProxyChanges[m_ProxyChangesStart - 1].Version;
	}
	m_ProxyChanges.push_back(InstanceChange { m_ProxyVersion, proxy });
	if (m_ProxyChangesStart >= c_MaxProxyChanges)
	{
		m_ProxyChanges.erase(m_ProxyChanges.begin(), m_ProxyChanges.begin() + static_cast<ptrdiff_t>(m_ProxyChangesStart));
		m_ProxyChangesStart = 0;
	}
}

bool RenderScene::GetProxyChanges(uint64_t sinceVersion, std::vector<uint32_t>& outProxies) const
{
	m_ProxyChangesRead = m_ProxyVersion;
	if (sinceVersion >= m_ProxyVersion)
		return true;
	if (sinceVersion < m_ProxyChangesFloor)
		return false;
	for (size_t index = m_ProxyChanges.size(); index > m_ProxyChangesStart && m_ProxyChanges[index - 1].Version > sinceVersion; index--)
		outProxies.push_back(m_ProxyChanges[index - 1].Instance);
	return true;
}
```

1. **Lines 1218–1219:** an entry logged since the last read already tells its readers; a second change of the same proxy adds nothing.
2. **Lines 1223–1228:** a full log drops its oldest entries and moves the floor to the version of the last one dropped.
3. **Lines 1240–1243:** a reader that is up to date gets nothing; a reader below the floor gets false.

:::example[A reader of the proxy log]
A reader takes version 7 with `GetProxyVersion`. That also marks version 7 as read. Proxy 3, last logged at version 2, changes: the entry is older than the mark, so version 8 is logged for proxy 3.

Proxy 3 changes again. Its newest entry, version 8, is newer than the mark, so nothing is added. Proxy 5 changes and gets version 9. The reader calls `GetProxyChanges(7, out)` and receives proxies 5 and 3, each once, and sets its version to 9.

Now suppose the log holds 65,536 entries and one more change comes. The oldest entry is dropped, say version 120 of a log whose newest is 65,656, and the floor becomes 120. A reader at version 119 is below the floor and gets false: it must read every proxy. A reader at version 120 or later is served from the log.
:::

The instance log works the same way, with two differences. It logs every change, also a repeat, so an instance may appear more than once in an answer. A single call that records more than the log's size clears the log and sets the floor to the current version. The palette log records ranges of joints instead of single entries. A renderer that falls behind a log uploads everything, which is slow once but never wrong.

## The scene's life: loads, clones and lights

A scene that is loaded builds its proxies in a burst. The code's comment says a first sync takes about 36 ms for 100,000 mesh renderers, more than two frames at 60 :term[frames per second]{id=frame-rate}. `RenderScene::Prepare` avoids the hitch. It calls `Sync` with `c_PrepareChunk`, 2,048 queued entities at a time, until none is left or the budget of the call is spent, at least one chunk per call.

`PrepareLoadedScene` calls it with the time left of the frame's `SceneWorkBudget`, as [sub-scenes](../world/sub-scenes.md) describes for loads. The code's comment puts a frame's 4 ms at about 10,000 mesh renderers. The GPU half of the preparation, which fills the GPU's copy, is in [the render scene's GPU copy](render-scene-gpu.md).

Play mode copies the scene. A **clone** of a render scene is the copy that `Scene::Copy` makes of it when play starts, so that the first frame of the play copy builds no proxy. `CopyIntoScene` copies the render scene member by member, the big arrays in parallel jobs, and the copy keeps the same indices: its entities have the source's identifiers. The clone records the versions its source's logs stood at, connects its listeners to the copy's registry, and starts with every proxy compared once if the source had transform changes that it had not read. A scene that nothing rendered has no render scene to clone, and the copy builds its proxies when it is rendered.

Lights are render scene records too, kept in `RenderLights` with their own log and synced with the proxies. What a light record holds is the subject of [lights](../light/lights.md).

The perf tests measure what the scene's life costs, and say it in numbers. The test `Starting play on 1,000,000 rendered cubes clones their render scene and its GPU copy` measures the clone's time plus the first frame's extra cost, and its target in `StrataTests/Perf/Budgets.json` is 5.0 ms. The test `32,768 moving cubes cost a step frame's proxy work in every interpolated frame` compares an interpolated frame with a step frame; its target ratio is 1.15. Both budgets are provisional at the pin: they are targets, not limits measured on the reference machine.

`RenderSceneStats` closes the walk. It counts proxies, indexed proxies, instance slots, meshes, materials, the updates of the latest sync and in total, full refreshes, mirrored, skin and posed proxies, palette joints and the time of the latest clone. The editor and the tests read these numbers to learn what a sync did.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Walk the scene each frame and build draw data | A renderer of a small scene | No contract: a missed signal cannot make a stale copy | Cost proportional to the scene every frame, not to the changes |
| Array of structs per proxy | Code that keeps one object per mesh | One :term[cache line]{id=cache-line} holds a whole proxy; simpler code | Loops that read one field drag every other field through the cache |
| One dirty flag per proxy | A renderer with a single reader | No log to bound and no floor | Every reader needs its own flags, and the flags must be cleared |
| :term[Callbacks]{id=callback} from the scene into the renderer | Code built on events | Updates at once, no queue | Work in the middle of scene code, and renderer state touched from many places |
| Rebuild the proxies on every change | A first, simple version | Nothing to keep consistent | The 100,000-cube scene would cost a full build for one moved cube |

The sources are in Further reading. The choice of Strata is the left half of each cost: a persistent copy, columns, logs, and a queue instead of callbacks. The price is the contract and the checks that enforce it.

## How it is tested

The suite is `Renderer.RenderScene`, in `StrataTests/src/Renderer/RenderSceneTests.cpp`. Its test `A static sync updates nothing; moving one of 100,000 cubes updates one proxy and one instance` reads like a specification. Read it from the top: build, sync, learn the layout, sync again, move one cube, then write without a signal.

```cpp src="StrataTests/src/Renderer/RenderSceneTests.cpp#L390-L440"
TEST_CASE("A static sync updates nothing; moving one of 100,000 cubes updates one proxy and one instance")
{
	Scene scene("Cubes");
	for (int index = 0; index < 100'000; index++)
		AddCube(scene, glm::vec3(static_cast<float>(index % 316) * 2.0f, 0.5f, static_cast<float>(index / 316) * 2.0f));
	RenderScene& renderScene = RenderScene::Get(scene);
	CHECK(renderScene.Sync(nullptr) == 100'000);
	CHECK(renderScene.GetStats().Proxies == 100'000);
	CHECK(renderScene.GetStats().IndexedProxies == 100'000);
	REQUIRE(renderScene.GetMeshesWithoutBounds().size() == 1);

	// The cube's layout arrives: every proxy gets bounds from the mesh and an instance.
	const Ref<Mesh> cube = MeshFactory::CreateCube();
	const uint32_t slot = renderScene.GetMeshesWithoutBounds()[0];
	CHECK(renderScene.GetIndexedUserCount(slot) == 100'000);
	CHECK(renderScene.SetMeshLayout(slot, *cube) == 100'000);
	CHECK(renderScene.GetMeshesWithoutBounds().empty());
	CHECK(renderScene.GetStats().InstanceSlots == 100'000);
	CHECK(renderScene.SetMeshLayout(slot, *cube) == 0); // The same layout again changes nothing
	CheckProxies(renderScene);

	uint64_t version = renderScene.GetInstanceVersion();
	std::vector<uint32_t> changes;
	CHECK(renderScene.Sync(nullptr) == 0);
	CHECK(renderScene.GetInstanceVersion() == version);
	CHECK(renderScene.GetInstanceChanges(version, changes));
	CHECK(changes.empty());

	Entity moved(renderScene.GetEntity(1234), &scene);
	moved.GetComponent<TransformComponent>().Translation.y += 1.0f;
	moved.MarkModified<TransformComponent>();
	CHECK(renderScene.Sync(nullptr) == 1);
	CHECK(renderScene.GetStats().LastSyncUpdates == 1);
	REQUIRE(renderScene.GetInstanceChanges(version, changes));
	REQUIRE(changes.size() == 1);
	CHECK(changes[0] == renderScene.GetFirstInstance(1234));
	CHECK(renderScene.GetWorldBounds(1234).Min.y == doctest::Approx(1.0f));
	CHECK(renderScene.GetInstances()[changes[0]].World.Rows[1].w == doctest::Approx(1.5f));
	CheckProxies(renderScene);

	// A write that is not signaled is noticed by the validation (Debug builds assert it after syncs).
	version = renderScene.GetInstanceVersion();
	moved.GetComponent<MeshRendererComponent>().CastShadows = false;
	std::string error;
	CHECK_FALSE(renderScene.Validate(&error));
	CHECK(error.find("shadow") != std::string::npos);
	moved.MarkModified<MeshRendererComponent>();
	CHECK(renderScene.Sync(nullptr) == 1);
	CHECK((renderScene.GetProxyFlags(1234) & RenderProxyFlags::CastShadows) == 0);
	CheckProxies(renderScene);
}
```

1. **Lines 396–399:** the first sync updates all 100,000 proxies and indexes them, and the mesh has unknown bounds.
2. **Lines 405–408:** the layout arrives, 100,000 proxies update at once, and the same layout again changes nothing.
3. **Lines 413–416:** a second sync updates nothing, and the instance log is empty.
4. **Lines 418–427:** one signaled move changes one proxy and one instance, and the cube's box moves up.
5. **Lines 432–439:** a write without a signal fails `Validate` with a message about the shadow setting; the signal repairs it.

Other tests cover the rest of this page. They check the queue, the instance limit, unknown bounds and slots shared by users. They check layouts kept when a mesh leaves memory and lost when its file is imported again, content changes the manager forgets, clones, and the proxy log until it overflows. A random test makes 5,000 edits and compares the proxies with a rebuild. Run them with:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.RenderScene
```

The command is run from the engine's folder after a Debug build; `ctest --preset windows-debug -R Renderer` also finds them.

## Changing it safely

The extension points are few. A new field of a proxy is a new array. Add it to `CreateProxy`, clear it when an index is used again, and copy it in `CopyIntoScene`'s member list. Compare it in `Validate`, and log changes of it through `RecordProxyChange`.

A new per-instance field goes to a parallel buffer, never into `InstanceData`. A new kind of change that readers must see goes through one of the logs.

Three rules of `AGENTS.md` apply, each with its reason. Signal every write, because the render scene learns only from signals and the transform log. Keep `InstanceData` at 64 bytes, because every pass reads it for every instance. Read a mesh's geometry only through the geometry pool, every frame, because compaction moves it; the render scene holds layouts and slots, not buffers.

Before you commit, run `Renderer.RenderScene`, the GPU suites of the renderer, and a Debug build of a scene with many entities: `Validate` is the check that finds a missed log entry or a stale proxy. A change that forgets to copy a member in `CopyIntoScene` shows as a difference in the test of clones.

## Summary

- A render proxy is the renderer's record of one mesh entity: matrix, bounds, mesh and material slots, flags, entity and instance range, kept in arrays with stable indices and a free list.
- A write to a mesh renderer or a transform without a signal is a bug, because the render scene reads only signals and the transform log; Debug builds find it with `Validate`.
- A reader follows a change log by version; below the floor, or after an overflow, it reads everything, and a proxy changed twice between reads is logged once.
- A proxy's bounds come from its pose, its mesh layout, the recorded bounds or a placeholder, in that order, and a mesh without bounds is requested as if in view.
- An instance is 64 bytes and a draw list entry names one in 27 bits, so a scene holds at most 134,217,728 instances, 8 GiB.

## Check yourself

1. A scene has proxies 0, 1 and 2 with entities A, B and C. B is destroyed, and then entity D gets a mesh renderer. Which proxy index does D get?

   - (a) 3, because indices are never used again.
   - (b) 1, because the free list gives the newest freed index.
   - (c) 0, because the arrays are compacted after a destroy.

   :::answer{tests="proxy-contents"}
   (b). `DestroyProxy` pushes index 1 on the free list and `CreateProxy` takes the newest free index. Answer (a) is wrong: freed indices are used again, and that is why a cache must store the entity. Answer (c) is wrong: nothing moves, so the other indices hold.
   :::

2. Code sets `CastShadows = false` on a mesh renderer of a cube created two syncs ago and does not signal. What happens at the next sync in a Release build, and in a Debug build of a 10-proxy scene?

   :::answer{tests="signal-rule"}
   In a Release build nothing is detected: the proxy still casts shadows, and the shadow cache and the GPU copy follow the stale proxy. In a Debug build a scene of up to 1,024 proxies is validated after every sync. So `Validate` finds the difference in the shadow setting. The assertion stops the program with a message that asks whether a component was written without a signal.
   :::

3. A proxy log has a floor of 120 and a version of 200. Reader X is at version 119 and reader Y at 150. What does each get from `GetProxyChanges`?

   :::answer{tests="log-readers"}
   X is below the floor, so it gets false and appends nothing: it reads every proxy. Y is above the floor and below the version, so it gets true and the proxies logged with versions 151 to 200, each proxy at most once for the entries logged after the last read.
   :::

4. A mesh was loaded, then dropped from memory, and its file was imported again while it was out of memory. Which bounds do its proxies have at the next sync?

   :::answer{tests="bounds-choice"}
   The layout is forgotten, because the source's revision differs from the one the layout was learned from. The proxies take the recorded bounds if the asset database has them, and placeholder bounds if it has none. In the second case renderers request the mesh as if in view until it loads and a new layout is learned.
   :::

5. How many bytes does the instance array of 250,000 single-submesh cubes hold, and how many cubes could a draw list entry name at most if each had one instance?

   :::answer{tests="instance-size"}
   $250\,000 \times 64 = 16\,000\,000$ bytes, 16 MB. The entry's 27 bits name $2^{27} = 134\,217\,728$ instances, so at most that many single-submesh cubes.
   :::

## Exercises

1. **Basic.** Trace it yourself: find where a signal of a changed `MeshRendererComponent` enters the render scene's queue, and where the queue is read. Name the files and functions.

   :::answer[Worked solution]{tests="signal-rule"}
   Search `Strata/src/Strata/Renderer/RenderScene.cpp` for `on_update<MeshRendererComponent>`. It is in `RenderScene::ConnectListeners`, which connects `RenderScene::OnMeshRendererChanged`. That :term[function calls]{id=function-call} `RenderScene::QueuePending`. The queue is read in `RenderScene::Sync`, which swaps `m_Pending` into a scratch list and calls `UpdateProxyFromEntity` for each entity.
   :::

2. **Medium.** In a test of your own, change a mesh renderer's material without `MarkModified`, then call `Validate`. What do you expect, and how do you fix the test?

   :::answer[Worked solution]{tests="signal-rule"}
   Follow the pattern of the page's test. Change `Material` on the component, then call `renderScene.Validate(&error)` and expect false, with an error saying that the proxy has another mesh, material or shadow setting than its component. The proxy still holds the old override. Call `MarkModified<MeshRendererComponent>()` on the entity, call `Sync`, and expect one update and a passing `Validate`.
   :::

3. **Hard.** Write a function that takes a log of (version, proxy) entries, its floor and a reader's version, and returns the proxies the reader must read, each once, or reports that the reader must read everything.

   :::answer[Worked solution]{tests="log-readers" solution="sketches/draw-render-scene-follow.cpp"}
   The function refuses when the version is below the floor. Otherwise it collects the proxies of every entry with a newer version, sorts them and removes duplicates.

   ```cpp sketch="draw-render-scene-follow.cpp"
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>
   #include <vector>

   struct Change
   {
   	uint64_t Version;
   	uint32_t Proxy;
   };

   // Returns false when the reader is below the floor and must read everything.
   bool Follow(const std::vector<Change>& log, uint64_t floor, uint64_t since, std::vector<uint32_t>& out)
   {
   	if (since < floor)
   		return false;
   	for (const Change& change : log)
   	{
   		if (change.Version > since)
   			out.push_back(change.Proxy);
   	}
   	std::sort(out.begin(), out.end());
   	out.erase(std::unique(out.begin(), out.end()), out.end());
   	return true;
   }

   int main()
   {
   	const std::vector<Change> log = { { 8, 3 }, { 9, 5 }, { 10, 3 }, { 11, 7 } };
   	for (const uint64_t since : { 7ull, 9ull, 11ull, 4ull })
   	{
   		std::vector<uint32_t> proxies;
   		if (Follow(log, 5, since, proxies))
   			std::printf("since %llu: %zu proxies\n", static_cast<unsigned long long>(since), proxies.size());
   		else
   			std::printf("since %llu: read everything\n", static_cast<unsigned long long>(since));
   	}
   }
   ```

   ```text output-of="draw-render-scene-follow.cpp"
   since 7: 3 proxies
   since 9: 2 proxies
   since 11: 0 proxies
   since 4: read everything
   ```

   1. **Lines 15–16:** a reader below the floor gets false and nothing else.
   2. **Lines 17–21:** every entry newer than the reader's version names a proxy to read.
   3. **Lines 22–23:** sorting and removing neighbors that are equal leaves each proxy once.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RenderScene.h` and `RenderScene.cpp`: the class, its arrays and the logs.
- `Strata/src/Strata/Renderer/SceneRenderData.h`: `AffineTransform`, `InstanceData` and the draw list entry.
- `Strata/src/Strata/Core/AmortizedCheck.h`: the pacing of Debug validation.
- `StrataTests/src/Renderer/RenderSceneTests.cpp`: the suite `Renderer.RenderScene`.
- `StrataTests/Perf/Budgets.json` and `StrataTests/src/Perf/RendererPerfTests.cpp`: the two perf tests of the scene's life.

## Further reading

- Robert Nystrom, "Game Programming Patterns", chapters "Dirty Flag" and "Data Locality" (beginner): why a copy updates from changes and why columns are fast.
- Mike Acton, "Data-Oriented Design and C++" (CppCon 2014) (intermediate): the case for arrays of fields.
- Christer Ericson, "Real-Time Collision Detection", the chapter on bounding volumes (advanced): why a box around an object is enough for most tests.
