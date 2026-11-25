---
id: editor/prefab-instances
title: "How prefab instances stay linked"
description: "How the editor keeps the override lists of prefab instances current while you edit, and how scenes that were closed catch up with prefabs that changed."
kind: internals
size: L
tracks: [E]
needs: [editor/saving, world/prefabs]
time: 90
learn:
  - id: states
    text: explain why an instance is synced, modified or outdated, and which stored numbers decide it
  - id: upkeep
    text: trace how an edit that goes through CommitEdit updates the override list of the instance root it touched
  - id: apply
    text: explain how prefab.apply writes the file and the scene as one undo step without a second propagation
  - id: catchup
    text: predict what the catch-up does to each instance of a scene that opens after its prefab changed
  - id: rules
    text: name the rules that code follows when it writes a prefab or records a scene step outside CommitEdit
since: 0.3.0
status: final
---

A level holds forty crates, all made from one :term[prefab]{id=prefab-world}. You make the crate lid thicker, and you expect the forty crates to follow, except the three where you moved a lid on purpose. This page is about the editor code that makes that true while you keep editing. It keeps each instance's list of differences current after every edit. It also brings a scene up to date when the scene was closed while its prefab changed.

This page does not teach what a link, an instance root or an override is, which [Prefabs: the data model](../world/prefabs.md) does, and it does not draw the Inspector's prefab bar.

## The problem and how engines solve it

Take two scenes, A and B, that use the prefab `Crate`. Scene A has one crate and scene B has three. You open A, change the crate's lid, and apply the change to the prefab.

The editor holds only one scene open, so B is a file on disk. Nobody has to open B for the prefab to change, and nobody may rewrite B's file behind your back. Yet when B opens, its crates must show the new lid, except where you changed the lid of a crate in B.

Three things can go wrong. A copy can stay stale and miss the change. A copy can lose a value that you set on purpose. A change can arrive twice, once from the command that wrote the file and once from the editor noticing the file changed.

Undo adds a fourth demand: pressing **Ctrl+Z** must put the file and every scene back, in one step.

An engine can answer in three ways. It can compare every instance with its prefab whenever it must know the difference, which costs a walk over every instance at each question. It can keep a list of differences on each instance and update the list after each edit, which costs care at every place that edits.

For closed scenes it can stamp each instance with the version of what it last took, and compare the stamp when the scene opens. Strata uses the second and the third. [Prefabs: the data model](../world/prefabs.md) compares the approaches of other engines; this page starts from Strata's choice and keeps its records exact.

## The map

Everything on this page runs on the :term[main thread]{id=main-thread}, because the main thread owns the scene. Four parts take part.

The commands in `StrataEditor/src/Editor/EditorPrefabCommands.cpp` change the scene and the prefab. `EditorContext` in `StrataEditor/src/Editor/EditorContext.cpp` records finished edits and keeps override lists current. `PrefabSync` in `StrataEditor/src/Editor/PrefabSync.cpp` watches the prefab files and catches scenes up. The scene layer's `PrefabInstances` and `PrefabOverrides` do the computing and know nothing of the editor.

```mermaid caption="The commands, the edit context and the sync of the editor call the functions of the scene layer, and the sync reads the source revision of each prefab from the asset manager." alt="A diagram of four boxes. The commands and the edit context call the scene layer. The sync is called by the edit context every frame and when a scene opens, calls the scene layer, and reads prefab revisions from the asset manager."
flowchart LR
  Cmd["Prefab commands"] -->|"records steps, SetBaseline"| Ctx["EditorContext"]
  Ctx -->|"CommitEdit: UpdatePrefabOverrides"| Scene["PrefabInstances and PrefabOverrides"]
  Ctx -->|"every frame in edit mode; OnSceneOpened"| Sync["PrefabSync"]
  Sync -->|"Propagate, Replace, MarkSynced"| Scene
  Sync -->|"source revisions"| Assets["EditorAssetManager"]
  Cmd --> Scene
```

An instance root keeps three things for this page, all in its `PrefabInstanceComponent`. `Overrides` is the list of differences that [Prefabs: the data model](../world/prefabs.md) teaches. The two other fields, `PrefabVersion` and `SyncedHash`, are numbers written when the instance last took its prefab's values.

The **part version**, stored in `PrefabVersion`, is a :term[hash]{id=hash} of the prefab's part for this root, without the root's transform and name: the same part gives the same number.

A **synced hash** is the hash of the instance's own values, in the same form, at the moment it last took its prefab's values. Both are 0 when nothing was recorded, as in scenes saved before the numbers existed and in instances that game code makes.

:::why
Why two numbers and a list? The part version says which prefab the instance saw. The synced hash says whether the instance changed since. The list says what changed. A version alone cannot tell a modified instance from an untouched one, and a list alone cannot tell which prefab it was made from.
:::

The numbers decide the state of an instance, and `prefab.status` reports it.

```mermaid caption="An instance is synced, modified or outdated. Edits and reverts move it between synced and modified; a prefab change that the instance could not take makes a modified instance outdated." alt="A state diagram with three states: synced, modified and outdated. Edit moves synced to modified, revert and apply move modified to synced, and a prefab change while modified without a list moves modified to outdated, from which revert returns to synced."
stateDiagram-v2
  [*] --> Synced: instantiate or create
  Synced --> Modified: edit
  Modified --> Synced: revert or apply
  Modified --> Outdated: prefab changed, no list known
  Outdated --> Synced: revert
  Synced --> Synced: prefab changed, instance takes it
```

An instance is modified when it differs from its prefab. Its override list is then not empty, or, with no list, a comparison finds a difference.

An instance is **outdated** when its part version differs from the version of the part stored now, and it was modified, so it did not take the later change.

Such an instance is an **outdated instance**. Applying it would write its older values over the newer ones in the prefab.

The Hierarchy shows the state beside each instance root, and the Inspector's prefab bar shows the link and its overrides.

::figure{id=hierarchy-marks}

::figure{id=prefab-bar}

## The contract

Callers may assume three things. After any edit that goes through `CommitEdit`, the override list of each touched instance root matches the instance, and undo restores the old list with the old values. After `prefab.apply`, the file, the scene and the sync agree on the new prefab. When a scene opens, its instances have caught up before `scene.open` answers. Callers must follow these rules, each with its reason.

1. **Code that writes a prefab for the editor sets the sync's baseline and marks instances synced.** The sync compares a file it reads with its baseline, its own copy of the prefab as it last saw it. A write without `SetBaseline` looks like a change on disk, and the sync would give the same change to the instances a second time. A write without `MarkSynced` leaves the instance's version old, so the next catch-up would treat it as one that missed a change.
2. **Code that records a scene step outside `CommitEdit` keeps the override lists current.** It calls `UpdatePrefabOverrides` for its transaction, or commits with `OverrideUpkeep::Current` when the edit already worked the lists out. Otherwise undo restores a list that no longer matches the values.
3. **Never apply an outdated instance without `force`.** Its old values would replace the prefab's newer changes, and nothing would say so afterwards.
4. **An instance root's transform and name are never overrides.** Placing an instance moves its root, and that must not count as a change.
5. **Nothing here blocks a frame.** The sync reads at most one new prefab file per frame while a scene is edited, and the catch-up of an opened scene runs in the frame that swaps the scene in.

:::rule
The engine's guide asks that every piece of code that writes a prefab, updates its instances or records a scene :term[undo step]{id=undo-step} keeps the numbers and lists exact, through `PrefabSync::SetBaseline`, `PrefabInstances::MarkSynced` and `UpdatePrefabOverrides`. The reason is the first two rules above: a second propagation, a stale list, or a catch-up that judges an instance wrongly. The data model that these rules protect is in [Prefabs: the data model](../world/prefabs.md).
:::

## A toy version

The toy keeps a prefab part as a few named numbers. An instance holds its own values, a set of override names, a part version and a synced hash. `MarkSynced` records the version and the hash. `CatchUp` follows the real decision.

A current instance stays, and an instance with a list takes everything it does not override. An instance with no list takes every value when it did not change, and is outdated when it did. Notice that the hash of the values is the only way the toy tells the last two apart.

```cpp sketch="editor-prefab-instances-toy.cpp"
// A toy catch-up: three instances of one prefab part meet a prefab that changed while their scene was closed.
#include <cstdint>
#include <cstdio>
#include <functional>
#include <map>
#include <set>
#include <string>

using Values = std::map<std::string, int>;

uint64_t HashValues(const Values& values)
{
	uint64_t hash = 1469598103934665603ull;
	for (const auto& [name, value] : values)
	{
		hash = (hash ^ std::hash<std::string>{}(name)) * 1099511628211ull;
		hash = (hash ^ static_cast<uint64_t>(value)) * 1099511628211ull;
	}
	return hash;
}

struct Instance
{
	Values Own;
	std::set<std::string> Overrides; // Names of the values this instance keeps different
	uint64_t PartVersion = 0;        // The version of the prefab's part when the instance last took its values
	uint64_t SyncedHash = 0;         // The hash of the instance's own values at that moment
};

void MarkSynced(Instance& instance, const Values& part)
{
	instance.PartVersion = HashValues(part);
	instance.SyncedHash = HashValues(instance.Own);
}

const char* CatchUp(Instance& instance, const Values& part)
{
	if (instance.PartVersion == HashValues(part))
		return "current";
	if (!instance.Overrides.empty())
	{
		for (const auto& [name, value] : part)
		{
			if (!instance.Overrides.contains(name))
				instance.Own[name] = value;
		}
		MarkSynced(instance, part);
		return "took all but its overrides";
	}
	if (HashValues(instance.Own) == instance.SyncedHash)
	{
		instance.Own = part;
		MarkSynced(instance, part);
		return "took every value";
	}
	return "outdated";
}

int main()
{
	Values part = { { "Intensity", 3 }, { "Range", 6 } };
	Instance plain;
	Instance listed;
	Instance legacy;
	for (Instance* instance : { &plain, &listed, &legacy })
	{
		instance->Own = part;
		MarkSynced(*instance, part);
	}

	listed.Own["Intensity"] = 4;
	listed.Overrides.insert("Intensity");
	legacy.Own["Range"] = 9; // Edited, but no list was kept for it

	part = { { "Intensity", 9 }, { "Range", 8 } }; // Applied from another scene
	const char* names[] = { "plain", "listed", "legacy" };
	Instance* instances[] = { &plain, &listed, &legacy };
	for (int index = 0; index < 3; index++)
	{
		const char* verdict = CatchUp(*instances[index], part);
		std::printf("%-6s intensity %d range %d: %s\n", names[index], instances[index]->Own["Intensity"], instances[index]->Own["Range"], verdict);
	}
	return 0;
}
```

```text output-of="editor-prefab-instances-toy.cpp"
plain  intensity 9 range 8: took every value
listed intensity 4 range 8: took all but its overrides
legacy intensity 3 range 9: outdated
```

1. **Lines 22–34:** An instance keeps its values, the names it overrides and the two stored numbers, which `MarkSynced` writes.
2. **Lines 38–39:** A part version equal to the prefab's means the instance missed no change.
3. **Lines 40–49:** With a list, the instance takes every value it does not override.
4. **Lines 50–56:** With no list, a matching hash replaces the values, and a different hash means outdated.
5. **Lines 71–75:** The three cases are built, and the prefab changes.

The three results show the whole policy. The real code has the same three branches. It also keeps lists current after every edit, works on :term[JSON]{id=json} parts instead of small maps, and undoes as one step. The sections below add each of these.

## Commands: what makes an instance and what reads it

The commands come first because every state starts in one. `prefab.create` captures entities into a `.stprefab` file and, unless you pass `link: false`, links them as an instance of it. The file and the link are one undo step: undo removes the links and moves the file to the trash. The command strips links from the snapshot it compares with, because a prefab file stores none, and it marks each root synced against that snapshot.

`prefab.instantiate` makes one instance, or many with `instances: [{parent?, components?}]`. It checks every request before it makes anything and records one undo step. It makes names unique: a second `Crate` under the same parent becomes `Crate (1)`. The root's name is the instance's own, so the number is no change.

The command marks each root synced with the part version and content hash of the stored prefab, before it applies any components you gave for the root, so those components show as overrides. With many instances, it works the version and hash out once per template root.

`prefab.status` reads without changing: it answers whether the entity is part of an instance and whether the instance is `modified` or `outdated`. It lists the entities that `changed`, were `added` (the prefab lacks them) or were `removed` (the instance lacks them), and the `overrides`. `prefab.revert` gives an instance its prefab's values again, keeping each entity's :term[universally unique identifier]{id=uuid} (:term[UUID]{id=uuid}), or reverts one component or one property. A whole revert marks the instance synced. `prefab.unpack` removes the links and `prefab.select` selects the root.

The command `prefab.apply` is the only one that changes the prefab file, and it gets its own section below.

## Keeping the lists current

`CommitEdit` is the editor's function that turns a finished edit into one undo step. Inside it, `UpdatePrefabOverrides` runs before the step is committed, so the list change belongs to the same step as the value change. It first returns at once when the scene has no linked entity, so scenes without prefabs pay nothing.

The first job is to find which instances the edit touched. An entity belongs to the instance of its nearest linked ancestor, so an entity added inside an instance still finds its instance. The transaction remembers the state of every changed entity before the edit. For each, the function asks whether the entity was reshaped: made, destroyed, moved to another parent, or given a different link. A reshaped entity also touches the instance it left.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1937-L1955"
for (const EntityState& state : transaction.GetBefore())
{
	const Entity entity = scene.GetEntityByUUID(state.ID);
	const Entity parent = entity ? entity.GetParent() : Entity();
	const bool reshaped = !state.Exists || !entity || (parent ? parent.GetUUID() : UUID::Null()) != state.Parent || !sameLink(state, entity);
	if (TouchedInstance* instance = touch(entity))
	{
		if (reshaped)
			instance->Reshaped = true;
		else
			instance->Entities.push_back(entity);
	}
	// The instance it left, or was destroyed in.
	if (reshaped && state.Parent.IsValid())
	{
		if (TouchedInstance* instance = touch(scene.GetEntityByUUID(state.Parent)))
			instance->Reshaped = true;
	}
}
```

1. **Lines 1939–1941:** The state before the edit is compared with the entity now; any change of existence, parent or link makes the entity reshaped.
2. **Lines 1942–1948:** The touched instance gets the entity: a reshaped one marks the whole instance, any other joins the list of entities to look at again.
3. **Lines 1949–1954:** An entity that left an instance or was destroyed in it also marks the instance it came from.

The second job updates each touched root against its part of the baseline, the prefab as the sync last saw it. An edit that only changed component values asks `UpdateOverrides` to work out the entries of the changed entities alone. A reshaped instance gets its whole list from `ComputeOverrides`. The context counts both in `GetOverrideUpkeepStats`, so tests can see which path ran.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1957-L1980"
// Each against its part of the prefab as the sync knows it; the list changes with the edit (and undo restores it).
for (const TouchedInstance& instance : instances)
{
	Entity root = instance.Root;
	// Tracked whether its list changes or not: the steps of a gizmo drag or a slider then all have the same entities and
	// merge into one, also when only some of them change the list.
	transaction.Track(root.GetUUID());
	const PrefabInstanceComponent& link = root.GetComponent<PrefabInstanceComponent>();
	const PrefabOverrides::IndexedPart* part = m_PrefabSync.GetBaselinePart(*this, link.Prefab, link.PrefabEntityID);
	if (!part)
		continue;
	std::vector<PrefabOverride> overrides = link.Overrides;
	if (!instance.Reshaped && PrefabOverrides::UpdateOverrides(root, *part, instance.Entities, overrides))
	{
		m_OverrideUpkeep.Entities += instance.Entities.size();
	}
	else
	{
		overrides = PrefabOverrides::ComputeOverrides(scene, root, part->Part);
		m_OverrideUpkeep.WholeLists++;
	}
	if (overrides != link.Overrides)
		root.GetComponent<PrefabInstanceComponent>().Overrides = std::move(overrides);
}
```

1. **Lines 1961–1963:** The root is tracked whether its list changes or not. The steps of a drag all name the same entities and so merge into one undo step, also when only some of them change the list.
2. **Lines 1965–1967:** With no baseline part the prefab cannot be read, and the list stays as it is.
3. **Lines 1969–1977:** The incremental update when it applies, otherwise the whole list; the counters tell the two apart.
4. **Lines 1978–1979:** The list is written only when it changed, so an edit that leaves it equal does not mark the component.

:::why
Why is the root tracked even when its list does not change? A drag records a step every frame. Steps merge only when they track the same entities. If the root joined only some of the steps, the drag would break into several undo steps.
:::

An edit of an instance root alone that names no entity, such as moving a placed model, does not walk the instance for its prefab ids: its transform is never an override.

## The sync: baselines, watching and settling

`PrefabSync::Update` runs once per frame in edit mode, and not while a scene is being opened, because the edited scene is read-only then. It keeps a **baseline** for each prefab that the scene's instances use: the editor's copy of the prefab's snapshot, as it was when the sync last looked, which instances are compared with.

First it finds the set of prefabs in use by walking the links. A walk is work, so it repeats only when the number of links changes, or when edits pause. Then, for each watched prefab, it asks the :term[asset manager]{id=asset-manager} for the prefab's current source revision, a counter that grows when the file changes. A prefab without a baseline gets one read from disk, at most one per frame.

```cpp src="StrataEditor/src/Editor/PrefabSync.cpp#L158-L202"
bool readOne = false;
for (const AssetHandle prefab : m_Watched)
{
	const uint64_t revision = assets->GetSourceRevisions(prefab).Current;
	if (revision == 0)
		continue; // No asset of the project (deleted, a built-in)
	auto found = m_Baselines.find(prefab);
	if (found == m_Baselines.end())
	{
		// The template instances are compared with when the prefab changes, read before it does (one per frame).
		if (readOne)
			continue;
		readOne = true;
		std::optional<nlohmann::json> snapshot = PrefabSyncUtils::ReadTemplate(*assets, prefab);
		found = m_Baselines.emplace(prefab, Baseline { snapshot ? std::move(*snapshot) : nlohmann::json(), revision }).first;
	}
	// Once per prefab and scene, with the first look at it: instances that missed a change of it while their scene was
	// closed.
	if (!found->second.CaughtUp)
	{
		found->second.CaughtUp = true;
		if (!found->second.Snapshot.is_null())
			CatchUp(context, prefab, found->second, PrefabInstances::FindInstanceRoots(*scene, prefab));
	}
	if (found->second.SourceRevision == revision)
		continue;
	found->second.SourceRevision = revision;
	std::string error;
	std::optional<nlohmann::json> snapshot = PrefabSyncUtils::ReadTemplate(*assets, prefab, &error);
	if (!snapshot)
	{
		ST_WARN("The prefab {} changed but cannot be read, so its instances keep their values: {}", prefab.ToString(), error);
		continue;
	}
	// The editor's own writes (prefab.apply and its undo) set the baseline before the file's revision follows.
	if (*snapshot == found->second.Snapshot)
		continue;
	nlohmann::json previous = std::move(found->second.Snapshot);
	found->second.Snapshot = *snapshot;
	found->second.PartVersions.Clear();
	found->second.Parts.Clear();
	m_BaselineVersion++;
	if (!previous.is_null())
		Propagate(context, prefab, previous, *snapshot);
}
```

1. **Lines 164–173:** The first look at a prefab reads its template as the baseline, one file per frame at most.
2. **Lines 176–181:** The first look also catches up the instances that missed a change while their scene was closed, once per prefab and scene.
3. **Lines 182–184:** An unchanged revision ends the work for this prefab.
4. **Lines 192–194:** If the file holds what the baseline holds, the editor wrote it itself and set the baseline first; nothing :term[propagates]{id=propagate}.
5. **Lines 195–201:** Otherwise the new snapshot becomes the baseline, the part versions are forgotten, and `Propagate` gives every instance the change except where it overrides.

`Propagate` collects the instance roots and calls `UpdateInstances` in one undo step called `Update Instances of <prefab name>`. Each root gets `PrefabOverrides::Propagate`, then `MarkSynced` with the new version and the content hash that the propagation worked out, so the instance counts as current. The step commits with `OverrideUpkeep::Current`, because propagation already works the lists out. A model whose import scale moved into its content needs one more step, which this page leaves to [Models and glTF](../assets/models-gltf.md).

The marks that the Hierarchy draws also come from the sync. `IsModified` returns true at once when the root's list is not empty; only instances with no list are compared, by writing them out as JSON text. A cache keeps the answer for each root until the undo history or the baseline changes.

Comparing writes entities out as JSON text, which is work for an edit and too much for every frame of a drag. So the sync has a **settling** rule: while edits follow each other within `c_SettleFrames` frames, which is 12, the marks and the watched prefabs stay as they were. They are worked out when the edits pause. The first edit after a pause is looked at at once.

## Applying one instance to the prefab

`prefab.apply` first checks everything that can fail. It needs an open project, the edit mode (not while playing), and a scene that is not being opened. It refuses a model, which comes from an import and cannot be changed, and says to unpack it or create a prefab. It refuses an outdated instance unless `force` is true, and the message says the instance was made from an older version.

Then it builds the new prefab file in memory, without touching the disk. The instance becomes a part with `MakeTemplate`, using the prefab's own root transform and name, and `ReplaceTemplate` puts it into the snapshot. With `component` and `property`, only that override goes in, through `ApplyToPart`. The text is laid out as `prefab.create` writes prefabs, and `Prefab::FromJson` checks that the result is valid before anything is written.

The scene work and the file write follow. The listing shows the scene side, then the file, then the one undo step.

```cpp src="StrataEditor/src/Editor/EditorPrefabCommands.cpp#L523-L580"
SceneEditTransaction transaction(scene, fmt::format("Apply Prefab {}", metadata->Name), {});
transaction.TrackSubtree(root.GetUUID());
std::vector<UUID> others;
for (const Entity instance : PrefabInstances::FindInstanceRoots(scene, prefab))
{
	if (instance != root)
		others.push_back(instance.GetUUID());
}
uint32_t linked = 0;
for (const auto& [id, templateId] : ids)
{
	Entity entity = scene.GetEntityByUUID(id);
	const PrefabInstanceComponent* link = entity.TryGetComponent<PrefabInstanceComponent>();
	if (!link || link->Prefab != prefab || link->PrefabEntityID != templateId)
	{
		entity.AddOrReplaceComponent<PrefabInstanceComponent>(PrefabInstanceComponent { prefab, templateId });
		linked++;
	}
}
// The instance is the prefab's new version now: synced, and without overrides.
PrefabInstances::MarkSynced(scene, root, newSnapshot);
Entity applied = root;
applied.GetComponent<PrefabInstanceComponent>().Overrides = PrefabOverrides::ComputeOverrides(scene, root,
	PrefabInstances::ExtractTemplate(newSnapshot, templateRoot));
size_t updated = 0;
PrefabOverrides::PartChangeCache parts(&snapshot, newSnapshot);
for (const UUID other : others)
{
	Entity instance = scene.GetEntityByUUID(other);
	if (!instance)
		continue; // Inside an instance an update before removed
	const PrefabOverrides::PartChangeCache::Parts& otherPart = parts.Get(instance.GetComponent<PrefabInstanceComponent>().PrefabEntityID);
	PrefabOverrides::PropagateResult result;
	if (!PrefabOverrides::Propagate(scene, instance, otherPart.Previous, otherPart.Next, result, [&transaction](UUID id) { transaction.Track(id); },
		&error))
	{
		transaction.Rollback();
		return EditorCommandResult::Fail(fmt::format("Updating another instance failed: {}", error));
	}
	for (const UUID entity : result.Created)
		transaction.TrackCreated(entity);
	transaction.Track(other);
	PrefabInstances::MarkSynced(instance, otherPart.NextVersion, result.ContentHash);
	updated += !result.Changed.empty() || !result.Created.empty() ? 1 : 0;
}

// The file, then one undo step for both.
if (!AssetEdit::ApplyDocument(*assets, prefab, after, &error))
{
	transaction.Rollback();
	return EditorCommandResult::Fail(error);
}
Scope<EditorActionGroup> group = CreateScope<EditorActionGroup>(fmt::format("Apply Prefab {}", metadata->Name));
group->Add(CreateScope<AssetDocumentAction>(*assets, prefab, fmt::format("Apply Prefab {}", metadata->Name), std::move(before), std::move(after)));
group->Add(transaction.TakeAction());
context.GetUndoStack().Record(CreateScope<PrefabApplyAction>(context, std::move(group), prefab, snapshot, newSnapshot));
context.GetPrefabSync().SetBaseline(context, prefab, newSnapshot);
context.PruneSelection();
```

1. **Lines 531–541:** Entities added to the instance get a link to the prefab, so they belong to it from now on.
2. **Lines 543–546:** The applied instance is synced with the new version, and its list is worked out against the new part; it is usually empty.
3. **Lines 548–567:** Each other instance in the scene gets `Propagate` with the old and new part, so it takes the change except where it overrides, and is marked synced. A failure rolls the whole transaction back.
4. **Lines 570–574:** The file is written only after the scene side succeeded; a failed write rolls the scene back.
5. **Lines 575–579:** One group holds the document's step and the scene's step, a `PrefabApplyAction` records it, and `SetBaseline` makes the new snapshot the baseline now.

The group alone would restore the file and the scene on undo. The sync would still hold the new snapshot as its baseline, and the next frame would see a file that differs from it. `PrefabApplyAction` closes that gap: it forwards every call to the group, then sets the baseline to the snapshot after the apply, or, for undo, the snapshot before it.

```cpp src="StrataEditor/src/Editor/EditorPrefabCommands.cpp#L39-L73"
class PrefabApplyAction final : public EditorAction
{
public:
	PrefabApplyAction(EditorContext& context, Scope<EditorActionGroup> group, AssetHandle prefab, nlohmann::json before, nlohmann::json after)
		: m_Context(context), m_Group(std::move(group)), m_Prefab(prefab), m_Before(std::move(before)), m_After(std::move(after))
	{
	}

	const std::string& GetName() const override { return m_Group->GetName(); }
	bool ChangesScene() const override { return m_Group->ChangesScene(); }
	SceneChangeKind GetSceneChange() const override { return m_Group->GetSceneChange(); }
	Ref<const std::vector<EntityState>> GetEntityStates(bool undone) const override { return m_Group->GetEntityStates(undone); }

	bool Execute(std::string* outError) override
	{
		if (!m_Group->Execute(outError))
			return false;
		m_Context.GetPrefabSync().SetBaseline(m_Context, m_Prefab, m_After);
		return true;
	}

	bool Undo(std::string* outError) override
	{
		if (!m_Group->Undo(outError))
			return false;
		m_Context.GetPrefabSync().SetBaseline(m_Context, m_Prefab, m_Before);
		return true;
	}
private:
	EditorContext& m_Context;
	Scope<EditorActionGroup> m_Group;
	AssetHandle m_Prefab;
	nlohmann::json m_Before;
	nlohmann::json m_After;
};
```

1. **Lines 52–58:** Redo and the first execution run the group, then make the new snapshot the baseline.
2. **Lines 60–66:** Undo runs the group backwards and puts the old snapshot back as the baseline, so the file's return is not mistaken for a change on disk.

Because the apply tells the sync, the sync does not propagate the file's change a second time. The same holds for the other direction: a file that changes on disk, for example through an import, reaches the sync only, which then propagates.

```mermaid caption="Two ways a change reaches instances: from the apply command, which sets the baseline first, and from a file changed on disk, which the sync finds by its revision." alt="A sequence of messages. In the first path the apply writes the file, sets the baseline and updates the other instances. In the second path a file changes on disk, the sync sees a new revision, finds a snapshot that differs from the baseline and propagates."
sequenceDiagram
  participant U as You
  participant A as prefab.apply
  participant S as PrefabSync
  participant I as Other instances
  U->>A: apply instance
  A->>I: Propagate, MarkSynced
  A->>S: SetBaseline (new snapshot)
  Note over S: file revision changes, snapshot equals baseline: nothing to do
  U->>S: file changed on disk
  S->>S: revision differs, snapshot differs from baseline
  S->>I: Propagate in one undo step
```

## The catch-up when a scene opens

Instances in a closed scene cannot be updated, so they are updated when the scene opens. **Catch-up** is the update of the instances of a prefab that changed while their scene was closed. `EditorContext` calls `PrefabSync::OnSceneOpened` right after the opened scene replaces the edited one, before `scene.open` answers. A command that runs in the same frame, such as a script of commands, then never sees an instance that missed a change.

`OnSceneOpened` forgets every baseline, finds the prefabs in use, reads each one's template (one file each), and calls `CatchUp` with the instance roots of that prefab. The decision for one root is the part you saw in the toy.

```cpp src="StrataEditor/src/Editor/PrefabSync.cpp#L355-L382"
std::vector<Entity> missed;
std::vector<Entity> overridden;
std::vector<RootRescale> rescaled;
for (const Entity root : roots)
{
	m_CatchUpCheckCount++;
	if (!PrefabInstances::IsOutdated(root, baseline.Snapshot, baseline.PartVersions))
		continue;
	// An instance whose overrides are known takes the new version except them; one without a list takes it only
	// when unmodified since it last synced.
	if (!root.GetComponent<PrefabInstanceComponent>().Overrides.empty())
		overridden.push_back(root);
	else if (PrefabInstances::IsUnchangedSinceSync(scene, root))
		missed.push_back(root);
	if (!importScale)
		continue;
	const glm::vec3 scale = root.GetComponent<TransformComponent>().Scale;
	const std::optional<glm::vec3> templateScale = FindTemplateRootScale(baseline.Snapshot, root.GetComponent<PrefabInstanceComponent>().PrefabEntityID);
	if (templateScale == std::optional<glm::vec3>(glm::vec3(1.0f)) && IsNear(scale.x, *importScale) && IsNear(scale.y, *importScale) && IsNear(scale.z, *importScale))
		rescaled.push_back(RootRescale { root, glm::vec3(1.0f) });
}
if (!rescaled.empty())
{
	const std::optional<AssetMetadata> metadata = assets.GetMetadata(prefab);
	ST_INFO("{} instance{} of {} kept {} size: the import scale is now part of the model", rescaled.size(), rescaled.size() == 1 ? "" : "s",
		metadata ? metadata->Name : prefab.ToString(), rescaled.size() == 1 ? "its" : "their");
}
UpdateInstances(context, prefab, missed, overridden, nullptr, baseline.Snapshot, rescaled);
```

1. **Lines 361–362:** An instance is considered only when its part version differs from the stored part's. Versions are worked out once per part by `PartVersions`; hashing writes the part out as JSON text, so the cache matters.
2. **Lines 365–368:** An instance with a list is propagated: it takes the new version except where it overrides. One without a list takes the values only when its hash still matches `SyncedHash`, and is replaced.
3. **Lines 369–374:** The model import-scale case; it keeps old model instances from taking the scale twice.
4. **Lines 376–382:** One `UpdateInstances` call does the work as a single undo step.

An instance that lands in neither list stays as it is. That is the way to an outdated instance: it is modified, it has no list because its scene was written before lists were kept, and the prefab moved on. The Hierarchy draws such an instance with the same yellow mark as a modified one, and only the mark's tooltip says that it missed a change. An instance that records no version, such as one that game code made, is never outdated.

The versions also have an edge. A prefab can change and change back while a scene is closed. Then the part version equals the recorded one again, the instance counts as current, and nothing happens; that is right, because the values are the same.

:::example[Crates in two scenes]
The prefab `Crate` holds a root `Crate` and a child `Lid`. In the prefab the lid's `Transform` has `Translation` (0, 1, 0) and `Scale` (1, 1, 1). Scene A has one crate.

Scene B has three. B1 is untouched. B2 has its lid raised to (0, 1.5, 0), so its list has one entry, the lid's `Translation`. B3 has its lid at (0, 2, 0) and comes from a scene saved before lists existed, so it has no list. All three record the version V1 of the part, and each records the hash of the values it had when it last synced.

1. Close B. Open A, raise A's lid to (0, 1.2, 0) and scale it to (1.1, 1, 1.1), and run `prefab.apply` on A's crate. The command answers `updatedInstances` 0, because A holds no other instance. The file now holds version V2. B is a file and does not change.
2. Open B. Before `scene.open` answers, `OnSceneOpened` reads the prefab and finds V2. B1 has V1 and an empty list, and its hash still matches, so it takes every value: lid at (0, 1.2, 0), scale (1.1, 1, 1.1). B2 has a list, so it takes all but the translation: lid at (0, 1.5, 0), scale (1.1, 1, 1.1).

   B3 has no list and its hash does not match, so it keeps (0, 2, 0) and scale (1, 1, 1). The step on the :term[undo stack]{id=undo-stack} is `Update Instances of Crate`, and it holds B1 and B2.
3. Read `prefab.status` for each. B1: `modified` false, `outdated` false. B2: `modified` true, `outdated` false, one entry in `overrides`: the lid's `Transform`, `Translation`, kind `Property`. B3: `modified` true and `outdated` true.
4. Apply B3 with `prefab.apply`. It fails: B3 was made from an older version, and its scale (1, 1, 1) would replace the new 1.1. With `force: true` it succeeds and the prefab's scale returns to 1. Reverting B3 instead gives it translation (0, 1.2, 0) and scale 1.1 and marks it synced.

:::

## From the toy to the real code

The toy has no JSON parts, no undo and no second source of change. What it shows is true of the real code, with these differences. The real version is a hash of the part written as JSON text, and it ignores the root's transform and name.

The real list holds entries, each with an entity, component, property and kind. `Propagate` applies the difference between the old and new part, so a value that the prefab did not change is not copied. The real catch-up goes through `UpdateInstances` and one undo step, and the real sync watches files and the editor's own writes, which the toy cannot.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Compare each instance with its prefab whenever the state is needed | Strata itself, for instances without a list | No list to keep right | A walk and a :term[serialization]{id=serialization} per instance at every question, too slow for a drag |
| A revision counter on the prefab instead of a content hash | :term[Version control]{id=version-control} and file synchronization tools | A number that costs nothing to work out | A file rewritten with the same values would count as a change |
| Rewrite every scene of the project when a prefab changes | Batch tools that run outside an editor | No catch-up code | Reading and writing every scene at each apply, and a closed scene that changes without you opening it |
| Edit the prefab in a mode of its own | Unity | No apply step, no outdated instances | A second editing context with its own undo and a way to leave it |

## How it is tested

The suite `Editor.Prefab` in `StrataTests/src/Editor/PrefabWorkflowTests.cpp` runs the commands through a harness. Run it with `build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Prefab`. These tests carry the page's claims:

- `prefab.apply writes the instance into the prefab and updates unmodified instances, in one undo step` covers the one step and its undo.
- `A prefab applied in another scene reaches its instances when their scene opens, except their overrides; ones without a list are outdated` is the example above, with the count of catch-up checks and the step name.
- `A run of edits, one per frame, compares instances and walks the links once it pauses, not every frame` covers the settling.
- `A gizmo or Inspector drag on an instance's child is one undo step, and its override follows it` and `Edits of an instance work out the entries of the entities they change, not the whole instance` cover how the lists are kept.

The `Perf.Editor` suite, in `StrataTests/src/Editor/EditorPerfTests.cpp`, closes the section with the cost of keeping the lists. The metrics `DragInPrefabInstance5kMedian` (a drag inside an instance of 5,000 entities), `DragPrefabInstanceRoot5kMedian` and `Drag100PrefabInstancesMedian` keep a frame of a drag under 2 ms. `PrefabApply10kInstances` and `SceneOpen10kPrefabInstancesMaxFrame` limit an apply and a scene open with 10,000 instances. Run them with `ctest --preset windows-release -L perf`; the limits live in `StrataTests/Perf/Budgets.json`.

## Changing it safely

The extension points are the functions that decide, not the callers. A new kind of override changes `PrefabOverrides` together with its update function and its propagation; the editor code here then keeps working. A new command that writes a prefab sets the baseline and marks instances synced. A new edit path outside `CommitEdit` calls `UpdatePrefabOverrides`.

Check three more things before a change lands. Does the step still hold the file and the scene as one? Does undo set the baseline back? Does a drag still merge into one step, which means the root is still tracked?

Run the suite above, the perf tests when the list keeping changed, and the feature test of the engine, which the engine's rules require for every new feature. Write a regression test and check that it fails without your fix.

## Summary

- The part version says which prefab an instance saw, the synced hash says whether it changed since, and the list says what changed. An instance is outdated when it was modified and missed a later change of its prefab.
- `UpdatePrefabOverrides` runs inside `CommitEdit`, tracks every touched root so that drags merge, and updates entries incrementally unless the instance was reshaped.
- `prefab.apply` writes the file and the scene as one undo step. `PrefabApplyAction` sets the sync's baseline on redo and on undo, so the sync never propagates the editor's own write.
- When a scene opens, `CatchUp` replaces instances that did not change, propagates to instances with a list except their overrides, and leaves modified ones without a list outdated.
- Code that writes a prefab sets the baseline and marks instances synced; code that records a step outside `CommitEdit` keeps lists current; nobody applies an outdated instance without `force`.

## Check yourself

1. An instance has `PrefabVersion` equal to the stored part's version, and its values differ from the prefab's. What is its state?

   :::answer{tests="states"}
   The instance is modified and not outdated. The version says the instance saw the current prefab, and the differences are its own changes, which its list records.
   :::

2. Why does `UpdatePrefabOverrides` call `Track` on the root even when the list does not change?
   (a) So that the root is saved. (b) So that the steps of a drag name the same entities and merge. (c) So that undo restores the prefab. (d) So that the sync sees a change.

   :::answer{tests="upkeep"}
   The answer is (b). Steps merge when they track the same entities. Option (a) is wrong: saving needs no tracking. Option (c) is wrong: the prefab file is no part of an ordinary edit. Option (d) is wrong: the sync reads the undo history's change count, not the tracking.
   :::

3. After `prefab.apply`, the sync reads the changed file. Why does it not propagate?

   :::answer{tests="apply"}
   `prefab.apply` already called `SetBaseline` with the new snapshot. The sync reads the file, finds it equal to the baseline and stops, so the other instances are not updated twice.
   :::

4. Scene B opens. An instance has an old version, an empty list and a hash that still matches. A second instance has an old version, one list entry and a changed value. A third has an old version, an empty list and a hash that differs. What happens to each?

   :::answer{tests="catchup"}
   The first takes every value of the part. The second takes every value except the one on its list. The third keeps its values and is outdated. All three changes are one undo step.
   :::

5. You write a command that edits an instance's child and records its own undo step without `CommitEdit`. What must it do, and what happens if it does not?

   :::answer{tests="rules"}
   The command must call `EditorContext::UpdatePrefabOverrides` for its transaction, or commit through `CommitEdit`. If it does not, the list on the root keeps the old entries, and undo or a later catch-up works from a list that does not match the values.
   :::

6. A prefab changes from V1 to V2 and back to V1 while a scene is closed. What does the catch-up do to the scene's instances?

   :::answer{tests="catchup,states"}
   Nothing. The stored part's version is V1 again, equal to the recorded version, so no instance counts as missing a change.
   :::

## Exercises

1. **Basic.** Run the toy mentally with a prefab that changes only `Range`, from 6 to 8, with `Intensity` staying 3. What do `plain`, `listed` and `legacy` hold after `CatchUp`?

   :::answer{tests="catchup"}
   `plain` takes both values: intensity 3, range 8. `listed` keeps its intensity 4, because it overrides it, and takes range 8. `legacy` has a range of 9 and no list, so its hash differs: it keeps intensity 3 and range 9 and is outdated. The toy copies every value that is not overridden; the real code applies only the difference.
   :::

2. **Medium.** Trace it yourself: find where an edit updates the override list of the instance it touched. Put a breakpoint in `EditorContext::UpdatePrefabOverrides`, drag a value of an instance's child in the Inspector, and watch the touched root. Then add an entity under the instance and watch again.

   :::answer{tests="upkeep"}
   The function is `EditorContext::UpdatePrefabOverrides` in `StrataEditor/src/Editor/EditorContext.cpp`, called from `CommitEdit`. A drag step lists one entity in `instances[...].Entities`, `Reshaped` stays false, and `UpdateOverrides` runs, adding to `m_OverrideUpkeep.Entities`. Adding an entity under the instance makes it a new entity, so `Reshaped` becomes true, `ComputeOverrides` works the whole list out, and `WholeLists` grows.
   :::

3. **Hard.** Write a small program of the settling rule. A mark is worked out again when the undo history changed and the edits are not continuing. Edits arrive in each of frames 10 to 15, and the window is 12 frames. At which frames is the mark worked out?

   :::answer[Worked solution]{tests="states" solution="sketches/editor-prefab-instances-settle.cpp"}
   The program keeps the frames of the last two changes. At frame 10 there is no earlier change, so the mark is worked out at once. Frames 11 to 15 follow within 12 frames of the earlier change, so the mark waits. After frame 15 it waits until 12 frames have passed, which is frame 27.

   ```cpp sketch="editor-prefab-instances-settle.cpp"
   // A toy of PrefabSync::AreEditsContinuing: when is a mark worked out again during a run of edits?
   #include <cstdint>
   #include <cstdio>

   constexpr uint64_t c_SettleFrames = 12;

   struct EditClock
   {
   	uint64_t LastChangeFrame = 0;
   	uint64_t PreviousChangeFrame = 0;

   	void SeeChange(uint64_t frame)
   	{
   		PreviousChangeFrame = LastChangeFrame;
   		LastChangeFrame = frame;
   	}

   	bool AreEditsContinuing(uint64_t frame) const
   	{
   		return PreviousChangeFrame != 0 && LastChangeFrame - PreviousChangeFrame < c_SettleFrames && frame - LastChangeFrame < c_SettleFrames;
   	}
   };

   int main()
   {
   	EditClock clock;
   	uint64_t changes = 0;
   	uint64_t markChanges = 0;
   	for (uint64_t frame = 1; frame <= 40; frame++)
   	{
   		if (frame >= 10 && frame <= 15)
   		{
   			changes++;
   			clock.SeeChange(frame);
   		}
   		if (markChanges != changes && !clock.AreEditsContinuing(frame))
   		{
   			markChanges = changes;
   			std::printf("frame %llu: the mark is worked out again\n", static_cast<unsigned long long>(frame));
   		}
   	}
   	return 0;
   }
   ```

   ```text output-of="editor-prefab-instances-settle.cpp"
   frame 10: the mark is worked out again
   frame 27: the mark is worked out again
   ```

   1. **Lines 8–23:** The clock keeps the frames of the last two changes and says whether edits continue.
   2. **Lines 32–42:** A change counts when it arrives; a mark is renewed only when edits are not continuing.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorPrefabCommands.cpp`: `prefab.instantiate`, `prefab.status`, `prefab.apply`, `prefab.revert`, `prefab.unpack`, `prefab.select` and `PrefabApplyAction`.
- `StrataEditor/src/Editor/EditorAssetCommands.cpp`: `prefab.create`.
- `StrataEditor/src/Editor/EditorContext.cpp`: `EditorContext::CommitEdit` and `EditorContext::UpdatePrefabOverrides`; `EditorContext::GetOverrideUpkeepStats` counts them.
- `StrataEditor/src/Editor/PrefabSync.h` and `PrefabSync.cpp`: `PrefabSync`, its baselines, `CatchUp` and the marks.
- `Strata/src/Strata/Scene/PrefabInstances.h` and `Strata/src/Strata/Scene/PrefabOverrides.h`: `MarkSynced`, `IsOutdated`, `Propagate`, `UpdateOverrides`.
- Tests: the suites `Editor.Prefab` and `Perf.Editor`.

## Further reading

- Unity Manual, "Prefabs" (docs.unity3d.com/Manual/Prefabs.html): instances, overrides, apply and revert in another engine; beginner.
- Unity Manual, "Editing a prefab in Prefab Mode" (docs.unity3d.com/Manual/EditingInPrefabMode.html): the prefab edit mode that Strata does not have; intermediate.
