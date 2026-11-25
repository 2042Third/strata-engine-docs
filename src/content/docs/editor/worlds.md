---
id: editor/worlds
title: "Editing a streamed world"
description: "How the editor edits a world that is only partly loaded: pins, dirty marks, re-celling, the two-request save, the play copy and the views of a world."
kind: internals
size: L
tracks: [E]
needs: [editor/play-mode, editor/recovery, worlds/streamer]
time: 80
learn:
  - id: recell
    text: predict the cell an edit moves an entity into, and which entities never move
  - id: keep-loaded
    text: name the reasons the editor keeps a cell loaded and the steps that mark a cell dirty
  - id: two-requests
    text: trace the two requests of a world save and say when the marks clear
  - id: play-copy
    text: explain what the play copy of a world adopts, drops and pins
  - id: change-safely
    text: choose the changes to the editor world that lose no entity between cells
since: 0.4.0
status: final
---

The editor shows a world through a small window: only the cells near its camera exist in memory. You still expect to move a crate, undo the move, save and press Play, and each of these must act on the right files. `EditorWorld` makes that true. It keeps the right cells loaded, notes which cells each edit changed, moves an edited entity into the cell of its new position, and prepares the save and the play copy. It does not choose which cells stream (the streamer does), write files (the `DocumentSaver` does) or cook the world ([the page on physics and scripts](../worlds/physics-scripts.md) covers the cook).

## The problem and how engines solve it

Take a world 4,000 m on each side, cut into cells of 64 m. One layer holds 63 × 63 = 3,969 cells, and the editor holds only the cells around its camera. Four tasks now meet:

- An edit must reach the file of the right cell, although most cells are not in memory.
- Undo must know which cell an entity belonged to before and after.
- A save must write the cells that changed and no others.
- Play must copy what is loaded and nothing more.

Three simple answers each fail. Copying the whole world to play needs every cell in memory at once, the one thing streaming exists to avoid ([why worlds stream](../worlds/why-streaming.md)). Keeping edits in the :term[persistent scene]{id=persistent-scene}, which never streams out, keeps the edit but changes no cell: no cell file would hold the crate, and the game would never stream it. Saving every cell writes 3,969 files for one moved crate. At an assumed 50 ms a file, that takes 198 s, more than three minutes for a change that touched one or two cells.

Strata answers with four parts:

- The editor streams the cells around its own camera, with a streamer of its own.
- Each :term[undo step]{id=undo-step} marks what it touched. A **dirty cell** is a cell whose document changed since the last save.
- An edited entity moves into the cell of its new position inside the same undo step.
- A save has two requests: the changed cells first, then the World document that lists them.

The price is rules. An entity moves only inside its layer, a child follows its top-level ancestor, a step on a cell that is not loaded waits for a load, and marks lean toward too many. Moving one crate across a border dirties two cells, so the save writes two cell files and the World document: three writes instead of 3,969. The rest of this page teaches each rule with its reason.

## Who owns what

`EditorContext` owns one `EditorWorld`, or none. `EditorWorld::Attach` makes it when the scene you open has an entity whose `WorldComponent` names a :term[World asset]{id=world-asset} of the project. A name that is no World asset logs a warning, and the scene is edited as a plain scene. Everything runs on the :term[main thread]{id=main-thread}; only the file writes leave it, in the `DocumentSaver`.

```mermaid caption="The editor context owns the editor world and calls it each frame, at each commit, at each save and at the start of Play. The editor world drives its streamer, hears every undo step as an observer and answers requests for cells. The interface panels only read its state." alt="A flow diagram. The editor context sends update, commit, save and play calls to the editor world. The editor world drives a streamer, which loads cells into the scene. Undo steps and scene edits report to the editor world, and the editor context sends snapshots to the saving service. Panels read the editor world."
flowchart LR
  ctx["EditorContext (main thread)"]
  ew["EditorWorld"]
  st["WorldStreamer"]
  sc["Scene sub-scenes"]
  undo["UndoStack"]
  sedit["SceneEdit steps"]
  ds["DocumentSaver (worker)"]
  ui["Cell map, Hierarchy, Inspector, Cells chip"]
  ctx -->|"Update, Recell, BeginSave, PrepareRuntimeCopy"| ew
  ew -->|"pins and sources"| st
  st -->|"load and unload"| sc
  undo -->|"OnApplied"| ew
  sedit -->|"RequestCell"| ew
  ctx -->|"snapshot and items"| ds
  ui -->|"read state versions"| ew
```

The files are few. `StrataEditor/src/Editor/EditorWorld.h` and `EditorWorld.cpp` hold the class. `StrataEditor/src/Editor/EditorWorldCommands.cpp` holds the `world.*` commands. `StrataEditor/src/Editor/WorldCellIO.h` reads cell documents with the streamed reader, which asks whether to stop as it reads, and writes the documents of a new world. `StrataEditor/src/Editor/SceneEdit.h` holds the cell parts of an undo step.

## What callers may assume

Each rule has its reason.

- Call `Update` every frame with the camera and the selection. The streamer follows the camera, and the selected entities keep their cells.
- Change entities through a `SceneEditTransaction` and `EditorContext::CommitEdit`. Re-celling runs there. Code that writes a position anywhere else leaves the entity in its old cell, with no mark.
- Change cell membership only through `Scene::SetSubSceneOf` and `EditorWorld`. A second writer of membership would make the marks and the cell files disagree.
- Treat a step that fails because a cell is missing as "try again soon". The error says the cell is loading.
- Write cell documents only through `BeginSave` and the `DocumentSaver`, and mark the world saved only after the World document is written.
- Draw cached views of the world. The map and the bounds rebuild when a version changes, never by walking cells each frame.

:::rule[Never copy a whole world]
`AGENTS.md` bars `Scene::Copy` on a world of cells. Play copies the persistent scene and the cells the editor has loaded, never the rest; memory is the reason, as [why worlds stream](../worlds/why-streaming.md) shows.
:::

:::rule[Only `EditorWorld` writes cell documents]
A cell document has one writer, and its write goes through the `DocumentSaver`, never on the main thread. The reason is no silent data loss: [the saving page](../editor/saving.md) teaches the :term[save points]{id=save-point} that follow.
:::

## A toy version

The toy keeps crates in cells of 64 m. An edit moves a crate, re-cells it and marks the cell it leaves and the cell it joins. A save writes the marked cells, then the index, then clears the marks.

:::question
This page shows C++ from here on. If classes, `std::set` and `static_cast` are new, read [the classes page](../basics/cpp-classes.md) and [the page on generic code](../basics/cpp-generic.md) first.
:::

Run the program and watch the number of cells each save writes. Crate C never changes, so its cell is written once.

```cpp sketch="editor-worlds-toy.cpp"
// A toy editor world: crates live in cells, an edit moves a crate into the cell of its new position and
// marks the cells it left and joined, and a save writes the marked cells first and the index second.
#include <cmath>
#include <compare>
#include <cstdio>
#include <set>
#include <string>
#include <vector>

struct CellKey
{
	int X = 0;
	int Z = 0;
	auto operator<=>(const CellKey& other) const = default;
};

struct Crate
{
	std::string Name;
	float X = 0.0f;
	float Z = 0.0f;
	CellKey Cell;
};

class ToyWorld
{
public:
	void Add(const std::string& name, float x, float z)
	{
		m_Crates.push_back({ name, x, z, CellAt(x, z) });
		m_Dirty.insert(m_Crates.back().Cell);
	}

	void Move(const std::string& name, float x, float z)
	{
		for (Crate& crate : m_Crates)
		{
			if (crate.Name != name)
				continue;
			m_Dirty.insert(crate.Cell); // the cell it leaves changes
			crate.X = x;
			crate.Z = z;
			crate.Cell = CellAt(x, z); // re-celling: the cell of the new position
			m_Dirty.insert(crate.Cell); // the cell it joins changes
		}
	}

	void Save()
	{
		std::printf("save: %zu dirty cell(s) of %zu crates\n", m_Dirty.size(), m_Crates.size());
		for (const CellKey& key : m_Dirty)
			std::printf("  write cell (%d, %d)\n", key.X, key.Z);
		std::printf("  write the world index\n"); // second, once the cell files exist
		m_Dirty.clear(); // saved only now
	}

private:
	static CellKey CellAt(float x, float z)
	{
		return { static_cast<int>(std::floor(x / c_CellSize)), static_cast<int>(std::floor(z / c_CellSize)) };
	}

	static constexpr float c_CellSize = 64.0f;
	std::vector<Crate> m_Crates;
	std::set<CellKey> m_Dirty;
};

int main()
{
	ToyWorld world;
	world.Add("A", 10.0f, 10.0f);
	world.Add("B", 70.0f, 10.0f);
	world.Add("C", 200.0f, 200.0f);
	world.Save();
	world.Move("A", 66.0f, 10.0f);
	world.Save();
	world.Move("B", 80.0f, 10.0f);
	world.Save();
	return 0;
}
```

```text output-of="editor-worlds-toy.cpp"
save: 3 dirty cell(s) of 3 crates
  write cell (0, 0)
  write cell (1, 0)
  write cell (3, 3)
  write the world index
save: 2 dirty cell(s) of 3 crates
  write cell (0, 0)
  write cell (1, 0)
  write the world index
save: 1 dirty cell(s) of 3 crates
  write cell (1, 0)
  write the world index
```

1. **Lines 40–44:** an edit marks the cell the crate leaves, moves the crate, finds the cell of its new position and marks that cell too.
2. **Line 60:** `floor` rounds toward minus infinity, so a position on a border belongs to the cell above it, and negative positions fall into negative cells.
3. **Lines 50–52:** a save visits only the dirty cells.
4. **Lines 53–54:** the index goes second, and the marks clear only after it.

The first save writes three cells, because all three crates are new. Moving A across x = 64 dirties two cells. Moving B inside its cell dirties one. The marks cost a set of keys, and the save never looks at the other cells. The real code adds what the toy lacks: cells that are not loaded, a streamer, undo and a save that runs off the frame.

## The real code

### Attaching and the edit settings

`EditorWorld` builds a `WorldStreamer` and tells it to read cells as their files are now, not as a loaded copy remembers them. It registers as an observer of the :term[undo stack]{id=undo-stack}, an object the stack calls after each step it applies. It also registers as the scene's `ISceneCellLoader` service, which undo code asks when a step needs a cell loaded.

Three settings shape one editing session. The **edit layer** is the layer whose cell receives the new top-level entities you create; its default, `Persistent`, keeps them in the persistent scene, which suits cameras, lights and managers. The visible layers are the layers that stream; an empty list means all. The radius scale multiplies every layer's :term[streaming distance]{id=streaming-distance} around the camera, from 0.1 to 10 with a default of 1. The command `world.edit` sets all three, checks each name before it changes anything and returns the answer of `world.status`.

### Why a cell stays loaded

The streamer unloads cells away from the camera. Five reasons keep a cell anyway:

- A `world.loadCells` pin.
- A selected entity inside it.
- An undo step that asked for it, until the next save.
- A dirty cell.
- A cell that a save is still writing.

`SyncPins` merges the reasons into one set of keys and gives the streamer the difference. Search for the three sets that start it, the two loops that add to it and the final difference.

```cpp src="StrataEditor/src/Editor/EditorWorld.cpp#L477-L502"
void EditorWorld::SyncPins()
{
	std::set<WorldCellKey> wanted = m_Pinned;
	wanted.insert(m_SelectionPins.begin(), m_SelectionPins.end());
	wanted.insert(m_RequestedPins.begin(), m_RequestedPins.end());
	for (const std::unordered_set<AssetHandle>* cells : { &m_DirtyCells, &m_SavingCells })
	{
		for (const AssetHandle cell : *cells)
		{
			if (const std::optional<WorldCellKey> key = FindCellKey(cell))
				wanted.insert(*key);
		}
	}
	if (wanted == m_StreamerPins)
		return;
	for (const WorldCellKey& key : m_StreamerPins)
	{
		if (!wanted.contains(key))
			m_Streamer.UnpinCell(key);
	}
	for (const WorldCellKey& key : wanted)
	{
		if (!m_StreamerPins.contains(key))
			m_Streamer.PinCell(key);
	}
	m_StreamerPins = std::move(wanted);
```

1. **Lines 479–481:** the pins of `world.loadCells`, of the selection and of undo requests start the set.
2. **Lines 482–489:** dirty cells and cells a save writes join it, each turned from its handle into its key.
3. **Lines 490–491:** an unchanged set returns before it touches the streamer.
4. **Lines 492–502:** the streamer pins the keys it lacks and releases the keys the set dropped, and the set is kept for the next call.

A dirty cell stays pinned because an unloaded one would take its changes with it. The streamer counts pins, so `SyncPins` sends only the difference.

### Dirty marks as an undo observer

`EditorWorld` hears every undo step through `OnApplied`, after the step runs in either direction. An entity state names the document of its entity: the cell, or none for the persistent scene. Look at how the three kinds of change differ.

```cpp src="StrataEditor/src/Editor/EditorWorld.cpp#L450-L473"
if (!(m_Scene.GetSettings() == m_SavedSettings))
	m_PersistentDirty = true;
switch (action.GetSceneChange())
{
	case SceneChangeKind::None:
		return;
	case SceneChangeKind::Settings:
		m_PersistentDirty = true;
		return;
	case SceneChangeKind::Entities:
		// Both directions: an entity moved from one cell to another changes both documents.
		if (const Ref<const std::vector<EntityState>> now = action.GetEntityStates(undone))
			MarkStates(*now);
		if (const Ref<const std::vector<EntityState>> other = action.GetEntityStates(!undone))
			MarkStates(*other);
		return;
	case SceneChangeKind::Other:
		m_PersistentDirty = true;
		for (const SubSceneStatus& status : m_Scene.GetSubScenes())
		{
			if (status.State == SubSceneState::Loaded && status.Scene.IsValid())
				MarkCellDirty(status.Scene);
		}
		return;
```

1. **Lines 450–451:** settings that differ from the saved ones mark the persistent scene, whatever kind of step changed them.
2. **Lines 459–465:** an entity step marks the documents of both its states, so a move marks the cell it leaves and the cell it joins.
3. **Lines 466–473:** a step that stores a snapshot of the whole scene, not entity states, marks the persistent scene and every loaded cell.

:::why[Marks stay after an undo]
Undoing back to the saved state leaves the marks, so the next save writes the same data again. The alternative is to compare content with the file for every cell on every step. A repeated write costs far less than that, and a cell that lacks a mark it needs loses an edit.
:::

### Cells in undo steps

A state also records the cell its entity belonged to, in `EntityState::Cell`. A step that creates an entity has no "before" entity, so `SceneEdit::LinkCells` gives it the cell of the other side. Before a step runs in either direction, `SceneEdit::CheckCells` asks whether the cells its states name are loaded.

```cpp src="StrataEditor/src/Editor/SceneEdit.cpp#L293-L307"
if (missing.empty())
	return true;
ISceneCellLoader* loader = scene.GetService<ISceneCellLoader>();
for (const AssetHandle cell : missing)
{
	if (loader)
		loader->RequestCell(cell);
}
if (outError)
{
	const std::string name = loader ? loader->DescribeCell(missing.front()) : missing.front().ToString();
	*outError = loader ? fmt::format("the step changes cell {}, which is not loaded; it is loading now, undo again once it is in", name)
		: fmt::format("the step changes the sub-scene of scene asset {}, which is not loaded", name);
}
return false;
```

1. **Lines 293–294:** when every cell is loaded, the step may run.
2. **Lines 295–300:** otherwise `RequestCell` asks the world to load and pin each missing cell.
3. **Lines 301–307:** the error names the first missing cell, and the step fails without changing anything.

You see a notice, wait a moment and press undo again. The pin of a requested cell lasts until a save has written everything.

### Re-celling

**Re-celling** puts an edited entity into the cell where its new position lies. `EditorContext::CommitEdit` calls `Recell` before it records the step, so the move and the edit are one undo step. Two functions do the work. `EnsureCellSubScene` finds the :term[sub-scene]{id=sub-scene} of a cell, and `Recell` decides which entities change cell.

```cpp src="StrataEditor/src/Editor/EditorWorld.cpp#L287-L312"
if (cell.IsValid())
{
	const SubSceneID id = m_Scene.FindSubSceneBySource(cell);
	if (m_Scene.IsSubSceneLoaded(id))
		return id;
	if (known)
	{
		// It exists but is not here: it loads (and stays) for the edit to come.
		m_RequestedPins.insert(key);
		return 0;
	}
}
// A cell that does not exist yet: made in memory with its derived handle, written at the next save.
const WorldLayer* layer = world->GetData().FindLayer(key.Layer);
const WorldCellSquare square = WorldGrid::CellBounds(*layer, world->GetData().GridOrigin, key.X, key.Z);
if (std::max({ std::abs(square.Min.x), std::abs(square.Min.y), std::abs(square.Max.x), std::abs(square.Max.y) }) > WorldData::c_MaxExtent)
	return 0;
cell = DeriveCellScene(key);
const SubSceneID id = m_Scene.AdoptSubScene(cell, {});
if (id == 0)
	return 0;
m_NewCells[cell] = key;
m_CellKeys[cell] = key;
m_CellTableVersion++;
MarkCellDirty(cell);
return id;
```

1. **Lines 289–291:** a loaded cell returns its sub-scene at once.
2. **Lines 292–297:** a cell that exists but is not loaded asks for a pin and returns 0, so the caller leaves the entity where it is.
3. **Lines 299–307:** a cell that does not exist is made empty in memory with a handle derived from the world and the key, unless it lies beyond `WorldData::c_MaxExtent`, 1,000 km from the origin.
4. **Lines 308–311:** the new cell is remembered, the table version moves and the cell is dirty.

The :term[derived handle]{id=derived-handle} means two sessions that make the same cell give it the same name. `m_NewCells` remembers the cell until a save writes its file.

```cpp src="StrataEditor/src/Editor/EditorWorld.cpp#L315-L343"
void EditorWorld::Recell(const SceneEditTransaction& transaction)
{
	const Ref<WorldAsset> world = GetWorldAsset();
	if (!world)
		return;
	RefreshCellTable();
	const WorldData& data = world->GetData();
	const WorldLayer* editLayer = m_EditLayer == c_PersistentLayer ? nullptr : data.FindLayer(m_EditLayer);
	const std::vector<UUID>& entities = transaction.GetEntities();
	for (size_t index = 0; index < entities.size(); index++)
	{
		const Entity entity = m_Scene.GetEntityByUUID(entities[index]);
		if (!entity || entity.GetComponent<RelationshipComponent>().Parent.IsValid())
			continue;
		const SubSceneID current = m_Scene.GetSubSceneOf(entity);
		const SubSceneStatus* status = m_Scene.GetSubSceneStatus(current);
		const std::optional<WorldCellKey> currentKey = status ? FindCellKey(status->Scene) : std::nullopt;
		const WorldLayer* layer = nullptr;
		if (currentKey)
			layer = data.FindLayer(currentKey->Layer);
		else if (transaction.WasCreated(index) && current == 0)
			layer = editLayer;
		if (!layer)
			continue;
		const WorldCellKey target = GetCellAt(*layer, entity);
		if (currentKey && target == *currentKey)
			continue;
		if (const SubSceneID id = EnsureCellSubScene(target))
			m_Scene.SetSubSceneOf(entity, id);
```

1. **Lines 327–328:** a child is skipped, because it belongs to its top-level ancestor's cell.
2. **Lines 332–338:** the layer comes from the entity's current cell, or from the edit layer for a new entity; an entity of the persistent scene has neither and is skipped.
3. **Lines 339–341:** the target cell comes from the position, and the same cell means nothing to do.
4. **Lines 342–343:** the sub-scene of the target is found or made; 0 means the entity stays.

The rules follow from the loop. Only top-level entities change cell, so editing a child moves nothing. An entity moves only within its own layer, because its layer comes from its current cell. An entity of the persistent scene stays there.

A new entity that is in no sub-scene yet goes into the edit layer's cell. A move into a cell that exists but is not loaded leaves the entity in its old cell and loads the target, so a later edit of the entity completes the move.

The mistake to avoid is editing a child and expecting its cell to change. Drag a branch away from its tree by 200 m, and the branch stays in the tree's cell file, which now holds an entity far from its cell. Move the top-level entity instead.

One command moves an entity to another layer or to the persistent scene: `world.moveEntities`, and no menu runs it. It refuses children, checks every target cell before it moves one entity, and fails with a reason, changing nothing, when a target cell is not loaded yet. Moves into a cell that is missing make it in memory.

:::why[Position decides the cell, not the person]
The cell of an entity follows from its position and its layer's grid, so you find an entity's file from where it stands. A cell chosen by hand could hold a crate far from the cell's square, and the streamer would load the crate when the camera is near the cell, not near the crate.
:::

### The save in two requests

`EditorWorld::BeginSave` lists the top-level entities by document and the dirty cells in key order, then builds one plan. The persistent scene goes in when it is dirty or when no cell is. A cell made in memory gets its document at the world's folder, the world's name, the layer's name and `X_Z.stscene`, with its :term[derived handle]{id=derived-handle}.

The marks clear now. The cells stay pinned, so a failed write is still there to save again. Edits made while the save runs mark the documents again.

```mermaid caption="A world save in order. The first request writes the persistent scene and the changed cells from one snapshot. When it ends, the stamps of the new files exist, so the editor world builds the index entries. The second request writes the World document. The scene counts as saved only after the second request ends." alt="A sequence diagram with three actors: the editor context, the editor world and the saving service. The editor context asks the editor world to begin the save, which clears the marks. It then sends the first request to the saving service. When that ends, the editor world builds the index entries. The editor context sends the second request, the World document, and marks the scene saved when it ends."
sequenceDiagram
  participant E as EditorContext
  participant W as EditorWorld
  participant S as DocumentSaver
  E->>W: BeginSave (plan, marks clear)
  E->>S: request 1: persistent scene and dirty cells, one snapshot
  S-->>E: ended, stamps exist
  E->>W: FinishSave (index entries)
  E->>S: request 2: the World document
  S-->>E: ended
  E->>E: MarkWorldSaved
```

:::why[The World document goes second]
Its index entries hold each cell's :term[content stamp]{id=content-stamp} and size, which exist only after the cell file is written. Writing it first would record stamps of old files. Writing it last also means a crash between the two leaves cell files without index entries, which the next save repairs, rather than entries that point to files that were never written.
:::

The first request's completion builds the second. Look at what its single item holds and which function runs when it ends.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1211-L1224"
DocumentSaveRequest request;
DocumentSaveItem item;
item.Asset = m_World->GetWorld();
item.Document = *index;
item.Reload = true;
request.Items.push_back(std::move(item));
request.SavePoint = status.SavePoint;
request.Label = fmt::format("{} (index)", status.Label);
std::string error;
const std::optional<RecoverySaveToken> heldToken = written ? std::optional<RecoverySaveToken>(token) : std::nullopt;
if (m_DocumentSaver.Submit(std::move(request), [this, id = status.ID, handle, heldToken, baseHash](const DocumentSaveStatus& indexStatus)
{
	OnWorldIndexSaved(indexStatus, id, handle, heldToken ? &*heldToken : nullptr, baseHash);
}, &error) == 0)
```

1. **Lines 1211–1216:** the second request holds one item: the World document that `FinishSave` built, reloaded once it is written.
2. **Line 1217:** the request keeps the :term[save point]{id=save-point} of the first.
3. **Lines 1221–1224:** the completion `OnWorldIndexSaved` marks the scene saved, and only when this write worked.

If the document would not change, `FinishSave` returns nothing and the scene is marked saved at once. A cell that failed to write is marked dirty again. If the second request fails, the scene stays modified and the next save tries again.

### The play copy

Play copies the :term[edited scene]{id=edited-scene}, but it must not copy a whole world. `PrepareRuntimeCopy` runs on the copy and visits every cell the editor has.

```cpp src="StrataEditor/src/Editor/EditorWorld.cpp#L762-L797"
std::vector<Entity> partial;
for (const SubSceneStatus& status : m_Scene.GetSubScenes())
{
	if (!status.Scene.IsValid() || !m_CellKeys.contains(status.Scene))
		continue;
	std::vector<Entity> roots;
	for (const Entity& root : m_Scene.GetSubSceneRoots(status.ID))
	{
		if (const Entity copied = copy.GetEntityByUUID(root.GetUUID()))
			roots.push_back(copied);
	}
	if (status.State == SubSceneState::Loaded)
	{
		std::string error;
		if (copy.AdoptSubScene(status.Scene, roots, &error) == 0)
			ST_WARN("Play: the cell {} stays in the persistent scene: {}", DescribeCell(status.Scene), error);
	}
	else
	{
		partial.insert(partial.end(), roots.begin(), roots.end());
	}
}
copy.DestroyEntities(partial);

// Cells a save still writes count too: their documents may not hold their edits yet.
std::vector<WorldCellKey> dirty;
for (const std::unordered_set<AssetHandle>* cells : { &m_DirtyCells, &m_SavingCells })
{
	for (const AssetHandle cell : *cells)
	{
		if (const std::optional<WorldCellKey> key = FindCellKey(cell); key && !m_NewCells.contains(cell))
			dirty.push_back(*key);
	}
}
std::sort(dirty.begin(), dirty.end());
return dirty;
```

1. **Lines 765–766:** only cells the editor world knows are visited.
2. **Lines 773–778:** a loaded cell is adopted into the copy, and a failure is logged.
3. **Lines 779–784:** the roots of every other cell are destroyed in the copy.
4. **Lines 786–797:** the dirty cells and the cells a save writes, except new ones, are returned in key order.

A fully loaded cell is adopted: the copy takes its entities as a sub-scene of the same cell, so the game's streamer finds the cell already loaded. This is adoption, as [the streamer page](../worlds/streamer.md) defines it. A cell still loading may hold only part of its entities, so its roots are destroyed in the copy, and the game streams the cell again from its file.

The editor pins the returned cells in the game's streamer for the session, because their files are older than what plays. A new cell has no file, so it is adopted whole and never pinned.

### Recovery and cell reading

After a crash, [the recovery journal](../editor/recovery.md) holds steps whose entities lived in cells. `EditorWorld::CollectCells` lists the cells the steps name, and `PrepareRecoveredCells` pins them and waits until they load. A cell made after the last save has no document, so `EnsureCellSubScene` makes it again from the position the steps recorded. A cell that cannot load fails the recovery with its reason.

A snapshot step holds only the cells that were loaded when it was taken, and the entities of other cells stay. `WorldCellIO` reads cell documents with the streamed reader, which asks whether to stop as it reads.

## The commands

`world.create` makes a world and its persistent scene. Its layers default to Terrain, Buildings, Props and Gameplay, each with cells of `cellSize` metres (default 64) and a streaming distance of four cells. The first layer loads before a game starts. The persistent scene holds the basic3d content and an entity named `World` with its `WorldComponent`. With `open` set (the default) it opens the new world and fails when the scene holds changes not yet written, unless you pass `force`; without it, one undo step removes the files.

`world.setLayers` replaces the layer list. Removing a layer that has cells, or changing a layer's cell size, is refused unless `deleteCells` moves those cells to the trash. The reason is that content is never moved to a new grid: a crate at x = 70 would sit in the wrong cell of a new cell size. Cells loaded in the open world are refused even with `deleteCells`: hide their layer first with `world.edit`.

A rename moves the layer's cell folder and keeps the handles. The whole change, trash moves, folder moves and document, is one undo step.

The other commands read and steer. `world.status` reports the edit settings and cell counts, `world.loadCells` pins, `world.info` describes a world's layers and index, and `world.cook` belongs to [the page on physics and scripts](../worlds/physics-scripts.md).

## How a world looks in the editor

The **cell map** is the editor's 2D view of a world's cells: squares coloured by state, with outlines for cells that changed since the save, pins and the :term[streaming sources]{id=streaming-source} with their radius. You find it in **View ▸ Streaming**, section World, or with the map button of the Hierarchy's world strip. Right-click a cell to **Load and pin**, **Unpin** or **Show in Content Browser**. The map draws the cells that the world's index lists. A cell that an edit has made has no file before the save, so it gets no outline, although the Hierarchy's strip counts it as unsaved.

The **cell bounds** are the viewport :term[overlay]{id=overlay-core} that outlines the active cells around the camera, coloured by state; the **Cells** chip of the viewport enables it. Both views are cached: the map rebuilds when the streamer's state version, the dirty version, the world or the streamer changes, and the bounds rebuild when the state version changes. Nothing walks the cells while nothing moves.

The Hierarchy shows a strip when a world is open: the world's name, the counts of cells loaded, loading and `unsaved`, the map button and a drop-down list for the edit layer. Type `l:Props` in its search box to list one layer's entities, `l:persistent` for the persistent scene's and `cell:3,-1` for one cell's. The Inspector shows a line for the selected entity: `Cell: Props (3, -1)`, `Persistent scene` or `Additive scene`. The Asset panel of a World asset lists its layers with their cells, and **New ▸ World** in the Content Browser runs `world.create`.

::figure{id=world-strip}

::figure{id=cell-map}

::figure{id=cell-map crop=pinned}

## Prefab instances in cells that load later

`PrefabSync` catches an instance up with its :term[prefab]{id=prefab-world} once for each prefab and scene, at the first look at the prefab (`CaughtUp` in `StrataEditor/src/Editor/PrefabSync.cpp`). A cell that streams in after another cell already used the prefab may therefore keep old instances. A cell that was not loaded when the prefab changed keeps its old values in its file until a save writes it.

So do not count on a cell catching up when it loads. After you change a prefab, load the cells that use it and save them.

:::example[A first world]
Run `world.create` with the path `Worlds/Harbor`. The defaults give four layers of 64 m cells, each with a streaming distance of 256 m, because the distance is four cells. The answer lists the layers and the new handles, and the editor opens the persistent scene.

```json
{ "path": "Worlds/Harbor" }
```

The parameter names the world, and no other parameter changes a default. `world.status` now reads `editLayer` as `Persistent`, because the default edit layer is the persistent scene, and the cell counts are all 0, because a new world has no cells.

Run `world.edit` with `{ "editLayer": "Props" }`. Then run `entity.create` with a Transform of `[70, 0, 10]`. The position has x = 70, so the cell is floor(70 / 64) = 1, and z = 10 gives floor(10 / 64) = 0: the Props cell (1, 0). It does not exist, so `EnsureCellSubScene` makes it in memory, and the Inspector reads `Cell: Props (1, 0)`.

Now `world.status` shows one dirty cell, and the cell map shows it outlined. After `scene.save`, the status reads 0 dirty cells, and `Worlds/Harbor/Props/1_0.stscene` exists with its `.meta` file. The save wrote that cell and the World document, and left the persistent scene alone, because its marks were clean.
:::

:::example[A crate across a border]
Make a copy of `Samples/OpenWorld` with the launcher and open `Worlds/Island`. Its Landmarks layer has cells of 64 m, and the entity `Camp2 Logs` stands at (67, 19.37, 188). Its cell is x: floor(67 / 64) = 1 and z: floor(188 / 64) = 2, so the Landmarks cell (1, 2). Load it with `world.loadCells`, passing the cell and `wait`. Then `world.status` reads 0 for `cells.dirty`.

Move the logs 7 m to x = 60, the way a drag does, with `component.set`:

```json
{ "entity": "<the logs' ID>", "component": "Transform", "values": { "Translation": [60, 19.372288, 188] } }
```

The command changes one value of the Transform. At x = 60 the cell is floor(60 / 64) = 0, so `Recell` searches for the cell (0, 2). The Landmarks layer has no file for it, so it is made in memory. The Inspector now reads `Cell: Landmarks (0, 2)`, and `cells.dirty` is 2: the cell it left and the cell it joined.

Undo returns the entity to the cell (1, 2) in one step and leaves 2 cells dirty, because marks stay. Redo moves it again.

Save with `scene.save`. The save writes `Worlds/Island/Landmarks/1_2.stscene` and the new `Worlds/Island/Landmarks/0_2.stscene`, and then the World document; it does not write the persistent scene, which was clean. After it, `cells.dirty` is 0. If you had moved the child `log_stack` by the same amount instead, the cell would stay (1, 2), because a child follows its top-level ancestor.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Load the whole world in the editor | Editors of small levels | No cell rules, no pins, no re-celling | Memory: a large world does not fit |
| One file for each object | Engines with external actors or one-file-per-actor modes | A move touches only the files of the moved objects | Thousands of small files to scan, save and merge |
| Compare each cell with its file at save | Tools that :term[diff]{id=diff} on save | Exact marks: undoing back to the saved state writes nothing | A full :term[serialization]{id=serialization} of every loaded cell at each save |
| Each command names its cell | Editors whose commands record their own changes | No observer; no extra marks | Every command must know about cells, and a new command can forget |

## How it is tested

The suite `Editor.World` in `StrataTests/src/Editor/EditorWorldTests.cpp` drives a small generated world through commands. Its tests check, among others, that:

- a move across a border is one undo step, and the save writes both cells;
- an edited cell stays loaded while the camera is away;
- a save writes only the dirty cell;
- undoing an edit of an unloaded cell loads the cell and works once it is in;
- Play copies the loaded cells and keeps the dirty ones;
- discarded edits recover into their cells.

Another test in the same file checks that the viewport's cell bounds are worked out again only when cells change. Run the suite by name with the test program:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.World
```

The runner prints the count of test cases and checks that passed, and a failure names the test and the line.

## Changing it safely

The extension points are small. A new reason to keep a cell loaded is a set that `SyncPins` merges. A new source of :term[dirty marks]{id=dirty-flag} is a case of `OnApplied`. A new rule of re-celling is a branch of `Recell`, and it needs a test that fails without it.

- Keep re-celling inside `CommitEdit`, before the step is recorded. A move after the commit would be a second undo step.
- Never let a step run while a cell it names is missing: `CheckCells` is the guard, and a new kind of step must call it.
- Keep marks conservative. A missed mark is lost data; an extra mark is a repeated write.
- Ask for a cell through `RequestCell`, which pins it. A cell that is requested and not pinned can unload before the step runs again.
- Pass the checks: the suite `Editor.World`, the streamer's suites and the feature test, because a new setting or command must be exercised there.

## Summary

- A move that crosses a border makes `Recell` put the entity into the cell of its new position in the same undo step. Only top-level entities of a layer's cells move, and a child follows its ancestor.
- A cell stays loaded for a pin, a selection, a step that asked for it, a dirty mark or a running save, and every undo step marks the cells of its states before and after.
- A save is two requests: the persistent scene and the dirty cells from one snapshot, then the World document with fresh index entries. The marks clear when the first begins, and the scene counts as saved after the second.
- The play copy adopts fully loaded cells, drops cells still loading and pins the dirty cells that have a document.
- A safe change keeps re-celling in `CommitEdit`, keeps marks conservative, never copies a whole world and never lets a second writer touch a cell document.

## Check yourself

1. A layer has cells of 64 m. A crate is a top-level entity in the cell (2, 1) and moves to x = 100, z = 70. The cell (1, 1) exists but is not loaded. What happens?

   - A. The crate moves into (1, 1) at once.
   - B. The crate stays in (2, 1), and the editor loads (1, 1).
   - C. The edit fails and changes nothing.

   :::answer{tests="recell"}
   B. floor(100 / 64) = 1 and floor(70 / 64) = 1, so the target is (1, 1). A cell that exists but is not loaded cannot receive the entity, so `EnsureCellSubScene` asks for a pin and returns 0, and the entity keeps its old cell. A is wrong because the cell is not there to receive it. C is wrong because the edit itself works; only the move waits.
   :::

2. You drag a child entity 300 m away from its parent. What changes in the cell files?

   :::answer{tests="recell"}
   Nothing moves between cells. The child belongs to its top-level ancestor's cell, so the entity stays in that file at its new position. `world.moveEntities` would refuse it as well, and you would move the ancestor instead.
   :::

3. Name the five reasons a cell stays loaded, and say which step marks both the cell an entity leaves and the cell it joins.

   :::answer{tests="keep-loaded"}
   A `world.loadCells` pin, a selected entity, an undo step that asked for the cell, a dirty cell and a cell a save is writing. `OnApplied` marks the states before and after of an entity step, so a move marks both cells.
   :::

4. A save wrote its cells, and the `DocumentSaver` then failed to write the World document. Is the scene marked saved, and what does the next save do?

   :::answer{tests="two-requests"}
   No. The scene is marked saved only after the second request is written, so it stays modified and shows an error. The next save works the World document out again: it lists the cells made in memory whose files the failed save wrote, and writes the document when it differs.
   :::

5. You press Play with three cells in the editor: A is loaded and saved, B is loaded and dirty with a file, and C is still loading. What does the copy hold, and what does the game's streamer pin?

   :::answer{tests="play-copy"}
   The copy adopts A and B as sub-scenes and destroys C's roots, so the game streams C again from its file. The streamer pins only B, because B's file is older than what plays. A new dirty cell with no file would be adopted and never pinned.
   :::

6. A colleague moves the call of `Recell` from `CommitEdit` to the save, to make edits cheaper. What goes wrong?

   :::answer{tests="change-safely"}
   Between the edit and the save, every step records the old cell for an entity that has a new position. Undo restores the wrong cell, the marks cover the wrong documents, and the cell bounds and the Inspector show a cell that no longer fits the position. The move must stay in the commit, before the step is recorded.
   :::

## Exercises

1. **Basic.** In the toy, after the first save, B moves to x = 130, z = 10. How many cells does the next save write, and which?

   :::answer[Worked solution]{tests="recell"}
   B stood in (1, 0), and floor(130 / 64) = 2 now gives (2, 0). The move marks the cell it left and the cell it joined, so the save writes (1, 0) and (2, 0): two cells.
   :::

2. **Medium.** Write the function that marks the documents a step touches, given states that name a cell or the persistent scene, and show the dirty set after three steps.

   :::answer[Worked solution]{tests="keep-loaded" solution="sketches/editor-worlds-marks.cpp"}
   Each state names a cell, or a negative number for the persistent scene. The function marks the states of both sides, as `OnApplied` does, so a move marks two cells and a creation marks the cell its entity goes into.

   ```cpp sketch="editor-worlds-marks.cpp"
   // Which documents does an undo step make dirty? A state names the cell of its entity, or -1 for the persistent scene.
   #include <cstdio>
   #include <set>
   #include <vector>

   struct State
   {
   	bool Exists = false;
   	int Cell = -1;
   };

   struct Step
   {
   	const char* Name = "";
   	std::vector<State> Before;
   	std::vector<State> After;
   };

   static void MarkStates(const std::vector<State>& states, std::set<int>& dirtyCells, bool& persistentDirty)
   {
   	for (const State& state : states)
   	{
   		if (state.Cell >= 0)
   			dirtyCells.insert(state.Cell);
   		else
   			persistentDirty = true;
   	}
   }

   int main()
   {
   	const std::vector<Step> steps = {
   		{ "move a crate from cell 0 to cell 1", { { true, 0 } }, { { true, 1 } } },
   		{ "create a crate in cell 2", { { false, 2 } }, { { true, 2 } } },
   		{ "move the persistent camera", { { true, -1 } }, { { true, -1 } } },
   	};
   	std::set<int> dirtyCells;
   	bool persistentDirty = false;
   	for (const Step& step : steps)
   	{
   		MarkStates(step.Before, dirtyCells, persistentDirty);
   		MarkStates(step.After, dirtyCells, persistentDirty);
   		std::printf("after \"%s\": %zu dirty cell(s), persistent %s\n", step.Name, dirtyCells.size(), persistentDirty ? "dirty" : "clean");
   	}
   	return 0;
   }
   ```

   ```text output-of="editor-worlds-marks.cpp"
   after "move a crate from cell 0 to cell 1": 2 dirty cell(s), persistent clean
   after "create a crate in cell 2": 3 dirty cell(s), persistent clean
   after "move the persistent camera": 3 dirty cell(s), persistent dirty
   ```

   1. **Lines 22–27:** a state that names a cell marks the cell, and a state without one marks the persistent scene.
   2. **Line 34:** the "before" state of a creation holds the cell of the "after" state, as `LinkCells` arranges it.
   3. **Lines 41–42:** both sides of a step are marked, as the observer does.
   :::

3. **Medium.** Trace it yourself: in a copy of `Samples/OpenWorld`, drag the `Camp2 Logs` entity across a cell border with a breakpoint in `EditorWorld::Recell`, and name the cell it leaves and the cell it joins.

   :::answer[Worked solution]{tests="recell two-requests"}
   Set the breakpoint on the line `if (const SubSceneID id = EnsureCellSubScene(target))` in `Recell`, in `StrataEditor/src/Editor/EditorWorld.cpp`. The command `component.set` reaches it through `EditorContext::CommitEdit`. `currentKey` is the Landmarks cell (1, 2) and `target` is (0, 2). `EnsureCellSubScene` makes the new cell, and `SetSubSceneOf` moves the entity. The save then writes both cells, in `EditorWorld::BeginSave`.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorWorld.h` and `EditorWorld.cpp`: `EditorWorld`, `WorldSavePlan`, `Recell`, `SyncPins`, `OnApplied`, `PrepareRuntimeCopy`.
- `StrataEditor/src/Editor/EditorContext.cpp`: the attach, `CommitEdit`, `SubmitWorldSave`, `OnWorldSaveEnded`.
- `StrataEditor/src/Editor/SceneEdit.h` and `SceneEdit.cpp`: `EntityState::Cell`, `CheckCells`, `LinkCells`, `ISceneCellLoader`.
- `StrataEditor/src/Editor/EditorWorldCommands.cpp`: `world.create`, `world.setLayers`, `world.status`, `world.edit`, `world.loadCells`, `world.moveEntities`, `world.info`.
- Views: `StrataEditor/src/UI/CellMap.cpp`, `StrataEditor/src/Editor/CellBoundsOverlay.cpp`, the Hierarchy and Inspector panels.
- Tests: the suite `Editor.World` in `StrataTests/src/Editor/EditorWorldTests.cpp`.

## Further reading

- Epic Games, documentation of World Partition in Unreal Engine, cited without a link: how another engine cuts a world into cells and edits them (intermediate).
- Robert Nystrom, "Game Programming Patterns", chapter "Spatial Partition", on gameprogrammingpatterns.com: why a grid makes nearby queries cheap (beginner).
- Jason Gregory, "Game Engine Architecture", the chapters on resource management and tools, cited without a link: how editors keep and save large assets (advanced).
