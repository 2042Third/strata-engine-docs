---
id: editor-ui/lists
title: "Lists that scale"
description: "How the Hierarchy and the Content Browser stay fast with 100,000 entities and 10,000 assets: cached views, clipped lists, stable identities and drag and drop."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/shell, editor/thumbnails]
time: 105
since: 0.3.0
learn:
  - id: cost-follows-screen
    text: explain why the cost of a list per frame must follow the rows on screen and not the size of the data
  - id: rebuild-by-version
    text: trace when HierarchyView rebuilds its rows and when an idle or renaming frame leaves them alone
  - id: selection-identity
    text: explain why selection and drops name entities by handle or UUID and never by row index
  - id: drop-mapping
    text: compute the parent and the index that a drop on a Hierarchy row sends to entity.setParent
  - id: add-filter
    text: write a new Hierarchy filter term with its tests and measure what the clip saves
status: final
---

The Hierarchy and the Content Browser are lists of whatever the project holds, and a project can hold a great deal. This page explains how both stay as fast with 100,000 entities or 10,000 assets as with ten. The core of each list is a model without any drawing, `HierarchyView` and `AssetBrowserView`. A panel draws that model, shows only the rows the window needs, and sends every change through a command. The page omits how thumbnails are made, what moving an entity to a new parent does to the scene, and how the Content Browser moves and deletes files, which other pages cover.

## The problem and how engines solve it

Picture a scene with 100,000 entities that the Hierarchy panel shows as rows, one line each. The simplest panel loops over all entities every frame and draws a row for each one. Suppose one row costs 2 microseconds to lay out and draw; the figure is a round number for the sum, not a measurement. Then 100,000 rows cost 200 ms. A game at 60 :term[frames per second]{id=frame-rate} has 16.7 ms for a frame, so the editor would run at about 5 frames per second, even though the window shows only 30 rows.

The window is the clue. The panel is 600 pixels high and a row is 20 pixels, so a person sees 30 rows at once. Drawing 31 rows costs 62 microseconds, which is 0.4 % of a frame. The cost then follows the screen, not the data. The same holds for a project of 10,000 assets drawn as a grid of tiles: the window shows a few dozen tiles, so the panel should pay for a few dozen.

Engines meet this with four ideas, and Strata uses all four.

**Virtualization** is drawing only the items that are in view and skipping the rest, while the list still behaves as if every item were there. The scroll bar has the length of the whole list, and a row that is off screen is never laid out.

The second idea is a cached view. Drawing 31 rows is cheap, but finding which 31 rows to draw is not, if it means walking the whole scene every frame. A cached view keeps a flat list of the rows and rebuilds it only when something it shows has changed. It compares a version number each frame: a counter that the scene or the :term[asset manager]{id=asset-manager} increases when it changes. An unchanged frame compares two numbers and stops.

The third idea is a stable identity. Rows come and go as people expand folders, search and create entities. A selection that stored "row 7" would point at another entity after a row appeared above it. So a selection and a drop name the entity itself, by its handle or its :term[universally unique identifier]{id=uuid} (:term[UUID]{id=uuid}), and ask the view where that entity is now.

The fourth idea is background work. Some tables are too big to build in one frame, even once: sorting tens of thousands of rows is the example. They are built by a job and shown when ready, and the panel keeps drawing meanwhile.

Each idea has a price. A cached view is a second copy of data the scene already holds, and a stale copy shows wrong rows. Virtualization means rows that are not drawn cannot react: a row that must stay alive, such as one being renamed, needs special care. Identities need a lookup from entity to row, and background work shows results a little late. The rest of the page shows how Strata pays each price.

## The map

Two models and two panels carry the page. A panel is a class that draws one window of the editor ([panels and the registry](../editor-ui/shell.md)). `HierarchyView` reads the active scene and holds the rows, and `SceneHierarchyPanel` draws them. `AssetBrowserView` reads the asset manager's folder index and holds folders and items, and `ContentBrowserPanel` draws them. Both models are plain C++ without any drawing code, so tests can drive them.

```mermaid caption="The two cached views. Each model reads one source, and each panel draws its rows and sends changes through commands." alt="A flow from the scene to the hierarchy model and its panel. A second flow runs from the asset manager to the asset model and the content browser panel. Commands lead back to the sources."
flowchart LR
	Scene[Scene: hierarchy version] --> HV[HierarchyView: rows]
	HV --> SHP[SceneHierarchyPanel]
	Assets[EditorAssetManager: change version] --> ABV[AssetBrowserView: items]
	ABV --> CBP[ContentBrowserPanel]
	Thumbs[ThumbnailCache] --> CBP
	SHP -- "entity.setParent" --> Scene
	CBP -- "asset.move" --> Assets
```

Everything in the figure runs on the :term[main thread]{id=main-thread}, as the engine's threading model requires ([the program's threads](../editor/program.md)). The thumbnail cache is the exception in what it does but not in who calls it: panels ask it for a picture every frame, and its own work happens elsewhere ([thumbnails](../editor/thumbnails.md)). The folder index that `AssetBrowserView` reads is kept by the asset manager, so the view never lists the disk ([handles and sub-assets](../assets/handles-meta.md)).

## The contract

The three rules below hold for every list in the editor. Each has a reason, and each was learned from a list that broke it.

:::rule
Code of the user interface (UI) never walks the scene or the folders of assets in a frame. It draws cached views that rebuild when a version changes, and it clips long lists. The reason is the arithmetic of the problem section: a walk costs the size of the data, and a frame has room for the size of the window. The rule is in `AGENTS.md` ([the editor rules](../editor-ui/shell.md)).
:::

:::rule
Rows identify themselves by entity handle or UUID, never by row index. Rows appear and disappear between the frame that reads a selection and the frame that applies it, so an index can name another entity by then.
:::

:::rule
Thumbnails are requested every frame the tile shows, and the type icon is drawn until the picture is ready. A waiting picture that nobody asks for leaves the queue within a few frames. A full cache forgets the pictures asked for longest ago. So a request every frame is how a tile says that it is still on screen.
:::

Three smaller promises support them. `HierarchyView::Update` is called once per frame before rows are read, and returns whether it rebuilt. A row's `Handle` is valid only until the hierarchy changes, which makes the view rebuild at its next update. And all of it runs on the main thread only.

## A toy version

The first sketch is the clip, the core of virtualization. Given how far the window is scrolled, it computes which rows are in view and draws those, plus a pinned row that must be drawn whatever the scroll. Look at how the visible range comes from two divisions and nothing else: the list is never searched.

```cpp sketch="editor-ui-lists-toy.cpp"
// A clipped list: only the rows in view are drawn, plus rows that must be drawn whatever the scroll.
#include <algorithm>
#include <cstdio>
#include <vector>

namespace
{

	constexpr int c_RowCount = 100000;
	constexpr float c_RowHeight = 20.0f;
	constexpr float c_WindowHeight = 600.0f;

	struct RowRange
	{
		int Start = 0;
		int End = 0; // One past the last row
	};

	// Which rows the window shows when it is scrolled down by scrollY pixels.
	RowRange GetVisibleRows(float scrollY)
	{
		const int first = std::max(0, static_cast<int>(scrollY / c_RowHeight));
		const int end = std::min(c_RowCount, static_cast<int>((scrollY + c_WindowHeight) / c_RowHeight) + 1);
		return { first, end };
	}

}

int main()
{
	const float scrollY = 1000000.0f;
	const RowRange visible = GetVisibleRows(scrollY);

	// A row that must stay alive (a rename field, a selection anchor) is added to what the loop draws.
	std::vector<int> drawn;
	const int pinned = 3;
	drawn.push_back(pinned);
	for (int row = visible.Start; row < visible.End; row++)
		drawn.push_back(row);

	std::printf("rows in the list: %d\n", c_RowCount);
	std::printf("visible: rows %d to %d\n", visible.Start, visible.End - 1);
	std::printf("drawn with the clip: %zu\n", drawn.size());
	std::printf("drawn without it: %d\n", c_RowCount);
	return 0;
}
```

```text output-of="editor-ui-lists-toy.cpp"
rows in the list: 100000
visible: rows 50000 to 50030
drawn with the clip: 32
drawn without it: 100000
```

1. **Lines 22–23:** the first and the last visible row come from two divisions of the scroll by the row height, kept inside the list.
2. **Lines 36–37:** a pinned row is added to the drawn rows first, whatever the scroll.
3. **Lines 38–39:** the loop runs over the visible range only, so its cost does not depend on `c_RowCount`.

The sketch prints the range for a scroll of one million pixels. Rows 50,000 to 50,030 are visible, so 31 rows are drawn, plus the pinned row. Without the clip the loop would draw 100,000. The real one is **ImGuiListClipper**, a helper of the :term[ImGui]{id=dear-imgui} library that, given the number of rows and the height of one, tells the loop which rows to draw. Its loop is `while (clipper.Step())`, and each step gives a range of rows to draw ([ImGui's items and loops](../editor-ui/imgui.md)).

The second sketch builds the flat list of rows from a tree. Each entity keeps the index of its first child and of its next sibling. The walk goes depth first, enters an entity only when it is expanded, and keeps a stack of where to resume when a :term[subtree]{id=subtree} ends.

```cpp sketch="editor-ui-lists-walk.cpp"
// The Hierarchy's walk: depth first along sibling links, into expanded entities only, with a resume stack.
#include <cstdio>
#include <vector>

namespace
{

	constexpr int c_None = -1;

	struct Node
	{
		const char* Name = "";
		int FirstChild = c_None;
		int NextSibling = c_None;
		int Depth = 0;
		bool Expanded = false;
	};

}

int main()
{
	// Root1 > [Lamp, Box > [Bulb]], Root2 > [Crate], Camera. Root2 stays collapsed.
	std::vector<Node> nodes = {
		{ "Root1", 1, 4, 0, true },
		{ "Lamp", c_None, 2, 1, false },
		{ "Box", 3, c_None, 1, true },
		{ "Bulb", c_None, c_None, 2, false },
		{ "Root2", 5, 6, 0, false },
		{ "Crate", c_None, c_None, 1, false },
		{ "Camera", c_None, c_None, 0, false },
	};

	std::vector<int> resume; // The next sibling of each expanded ancestor
	int current = 0;
	int visited = 0;
	while (current != c_None)
	{
		const Node& node = nodes[current];
		std::printf("%*s%s\n", node.Depth * 2, "", node.Name);
		visited++;
		if (node.Expanded && node.FirstChild != c_None)
		{
			resume.push_back(node.NextSibling);
			current = node.FirstChild;
			continue;
		}
		current = node.NextSibling;
		while (current == c_None && !resume.empty())
		{
			current = resume.back();
			resume.pop_back();
		}
	}
	std::printf("visited %d of %zu entities\n", visited, nodes.size());
	return 0;
}
```

```text output-of="editor-ui-lists-walk.cpp"
Root1
  Lamp
  Box
    Bulb
Root2
Camera
visited 6 of 7 entities
```

1. **Line 34:** the resume stack holds the next sibling of each expanded ancestor.
2. **Lines 42–47:** an expanded entity with children pushes its next sibling and continues at its first child.
3. **Lines 48–53:** otherwise the walk moves to the next sibling, and pops the stack while a chain has ended.

Root2 is collapsed, so its child Crate is never visited: the walk costs the number of rows shown, not the number of entities. The resume stack is what replaces the parent pointer: when Bulb has no next sibling, the stack holds Box's next sibling (none), and under it Root1's next sibling, Root2. The real code does exactly this, with flags and handles added.

## The real code: the rows

### The version gate

`HierarchyView::Update` runs first each frame. Notice the two ways it can end without work.

```cpp src="StrataEditor/src/Editor/HierarchyView.cpp#L134-L151"
bool HierarchyView::Update(const Ref<Scene>& scene)
{
	if (m_Scene.lock() != scene)
		Bind(scene);
	if (!scene)
	{
		if (m_Rows.empty())
			return false;
		m_Rows.clear();
		m_RowIndexValid = false;
		m_RebuildCount++;
		return true;
	}
	if (!m_Dirty && scene->GetHierarchyVersion() == m_HierarchyVersion)
		return false;
	Rebuild(*scene);
	return true;
}
```

1. **Lines 136–137:** a scene other than the one the rows were built for, such as play mode's copy, binds first and rebuilds.
2. **Lines 138–145:** with no scene at all, the rows are cleared once, and later calls return false.
3. **Lines 147–148:** the gate: when nothing is dirty and the :term[hierarchy version]{id=hierarchy-version} is the same, the call returns before any work.
4. **Line 149:** every other path rebuilds the whole list in one call.

The model rebuilds for three reasons: a new scene, a scene's :term[hierarchy version]{id=hierarchy-version} that moved, or a :term[dirty flag]{id=dirty-flag}.

The dirty flag is set by expansion changes, by a filter change and, while a filter reads names, tags or components, by the scene's signals ([the scene's signals](../world/scene-graph.md)). Names are not watched when no search is typed. The row holds a handle and an identifier, and the panel reads the name from the scene when it draws, so a rename needs no rebuild. The test `With 100,000 top-level entities, unchanged frames rebuild no rows` checks this: a thousand idle frames, a rename, and the count stays at one.

### The walk

`BuildTree` is the toy's walk with the real fields. A row records the handle, the identifier, the depth the scene already stores, and flags that say whether the entity has children and shows them.

```cpp src="StrataEditor/src/Editor/HierarchyView.cpp#L230-L264"
void HierarchyView::BuildTree(const Scene& scene)
{
	// Depth first along the scene's sibling links, into expanded entities only: the cost is the visible rows.
	const entt::registry& registry = scene.GetRegistry();
	std::vector<entt::entity> resume; // Where to continue once a subtree is done: the next sibling of each expanded ancestor
	entt::entity current = GetFirstRoot(scene);
	while (current != entt::null)
	{
		const HierarchyComponent& hierarchy = registry.get<HierarchyComponent>(current);
		HierarchyRow row;
		row.Handle = current;
		row.ID = registry.get<IDComponent>(current).ID;
		row.Depth = hierarchy.Depth;
		const bool hasChildren = hierarchy.FirstChild != entt::null;
		const bool expanded = hasChildren && m_Expanded.contains(row.ID);
		if (hasChildren)
			row.Flags |= HierarchyRowFlags::HasChildren;
		if (expanded)
			row.Flags |= HierarchyRowFlags::Expanded;
		m_Rows.push_back(row);

		if (expanded)
		{
			resume.push_back(hierarchy.NextSibling);
			current = hierarchy.FirstChild;
			continue;
		}
		current = hierarchy.NextSibling;
		while (current == entt::null && !resume.empty())
		{
			current = resume.back();
			resume.pop_back();
		}
	}
}
```

1. **Line 244:** an entity shows its children only if it has some and its UUID is in the expanded set.
2. **Lines 253–255:** descending: the next sibling is pushed on the resume stack, and the walk continues at the first child.
3. **Lines 257–262:** otherwise the walk moves to the next sibling, and when a chain ends it pops the stack to resume after the subtree.

The difference from the toy is small. The nodes are entities in an EnTT registry, so the links are handles and a null handle ends a chain, and the expansion state is a set of UUIDs kept in the view. That set survives rebuilds and even the play-mode copy of the scene, since entities keep their UUIDs. New entities start collapsed.

```mermaid caption="From the scene to the screen. The walk follows the tree and skips collapsed subtrees, the rows are a flat list with depths, and only the window's rows are drawn." alt="Three columns. The left column shows a tree with some nodes expanded and one collapsed. The middle column shows the flat rows with their depths. The right column shows a window covering a few of the rows."
flowchart LR
	subgraph Tree
		R1[Root1 expanded] --> L[Lamp]
		R1 --> B[Box expanded]
		B --> Bu[Bulb]
		R2[Root2 collapsed] -.-> C[Crate skipped]
		Cam[Camera]
	end
	subgraph Rows
		r0["0 Root1 depth 0"] --> r1["1 Lamp depth 1"] --> r2["2 Box depth 1"] --> r3["3 Bulb depth 2"] --> r4["4 Root2 depth 0"] --> r5["5 Camera depth 0"]
	end
	subgraph Screen
		w["window: rows 2 to 4"]
	end
	Tree --> Rows
	r2 --> w
	r3 --> w
	r4 --> w
```

When the cost of a rebuild matters, remember what it is made of. It touches each visible row once and nothing else, and `FindRow`, the lookup from an entity to its row, is a :term[hash map]{id=hash-map} that is built on its first use after a rebuild.

### Filters

The search box takes terms separated by spaces, and an entity must satisfy all of them. A plain word is part of the name. `c:` names a component, so `c:light` finds every kind of light, and `t:` names a tag. In a world, `l:` names a layer and `cell:` gives a cell's coordinates. A prefix typed alone, such as `c:`, asks for nothing yet.

The shown rows are the matches and their ancestors. An ancestor is drawn dimmed, because without it a match would hang in the air with no parent. The naive way to find ancestors walks from every match up to the root. In a chain of 1,000 entities that all match, this takes 499,500 steps. The real code marks each ancestor once and stops walking when it meets one that is already marked.

```cpp src="StrataEditor/src/Editor/HierarchyView.cpp#L269-L291"
// The matches, then their ancestors: each ancestor is marked once (a walk stops at one marked before), so marking
// is linear in the scene.
std::vector<entt::entity> matches;
size_t slots = 0;
for (const entt::entity entity : registry.view<HierarchyComponent>())
{
	slots = std::max(slots, GetSlot(entity) + 1);
	if (Matches(registry, entity))
		matches.push_back(entity);
}
m_Marks.assign(slots, 0);
for (const entt::entity match : matches)
{
	m_Marks[GetSlot(match)] |= c_MarkMatch;
	for (entt::entity parent = registry.get<HierarchyComponent>(match).Parent; parent != entt::null;
		parent = registry.get<HierarchyComponent>(parent).Parent)
	{
		uint8_t& mark = m_Marks[GetSlot(parent)];
		if (mark & c_MarkShownDescendant)
			break;
		mark |= c_MarkShownDescendant;
	}
}
```

1. **Lines 273–278:** one pass over every entity collects the matches and the highest slot number.
2. **Line 279:** the marks are a :term[byte]{id=byte} per slot, so a mark is a lookup and no search.
3. **Lines 286–289:** an ancestor that is already marked ends the walk, since everything above it was marked then.

The loop is linear in the scene. Matches are collected in one pass, and each ancestor is visited once, however many matches lie below it. The sketch in the exercises counts the steps of both ways. After the marking, a second walk like the one above goes through the scene and emits the marked entities, and an entity with a marked descendant counts as expanded.

## The real code: selection and the Hierarchy panel

`SceneHierarchyPanel::DrawRows` draws the rows. It must do four things at once: draw only the visible rows, let a person select many rows, let rows be dragged, and keep the selection correct when rows move. The selection part is where most of the difficulty lies, so the terms come first.

**Multi-select (BeginMultiSelect)** is the protocol of :term[Dear ImGui]{id=dear-imgui} by which a list lets a person select several items with the mouse and keyboard. The program opens a scope with `BeginMultiSelect`, draws its items, closes it with `EndMultiSelect`, and ImGui answers with a list of requests to apply, such as "select this range". ImGui does not store the selection. The program applies each request to the selection it keeps, which for the editor is the `EditorContext` ([the selection's storage](../editor/program.md)).

Each item must tell ImGui who it is, because requests name items. That name is the item's **selection user data**: a 64-bit number the program attaches to an item with `SetNextItemSelectionUserData`, which ImGui hands back in requests. A program that stores row indexes there gets indexes back. The Hierarchy stores the entity's handle instead, as a plain :term[integer]{id=integer}.

The gestures are the familiar ones. A click selects one row. **Ctrl** and a click toggles a row. **Ctrl+A** selects all, and a click on empty space, or **Esc**, clears the selection. A drag from empty space draws a box that selects the rows it touches.

**Shift** and a click makes a **range selection**: every row between an anchor, the row of the last plain click, and the clicked row is selected. Dear ImGui also calls the box a box select.

The **primary selection** is the entity that was selected last, which the Inspector shows and the :term[gizmo]{id=gizmo-start} moves. The editor keeps it as the last entry of the selection list.

```cpp src="StrataEditor/src/Panels/SceneHierarchyPanel.cpp#L689-L715"
const ImGuiMultiSelectFlags flags = ImGuiMultiSelectFlags_ClearOnEscape | ImGuiMultiSelectFlags_ClearOnClickVoid | ImGuiMultiSelectFlags_BoxSelect1d
	| ImGuiMultiSelectFlags_SelectOnClickRelease;
// The selection has a focus scope of its own (its ID): the rename field after it is outside the selection.
ImGui::PushID("Selection");
ImGuiMultiSelectIO* io = ImGui::BeginMultiSelect(flags, static_cast<int>(context.GetSelection().size()), static_cast<int>(rows.size()));
ApplySelectionRequests(context, scene, *io);

ImGuiListClipper clipper;
clipper.Begin(static_cast<int>(rows.size()), rowHeight);
// The row a range selection starts from and the row being renamed are drawn even when out of view.
if (const std::optional<size_t> source = FindSelectionRow(scene, io->RangeSrcItem))
	clipper.IncludeItemByIndex(static_cast<int>(*source));
if (m_Rename.Entity.IsValid())
{
	// An entity the rows do not show (the filter hides it) is not renamed.
	if (const std::optional<size_t> renamed = m_View.FindRow(m_Rename.Entity))
		clipper.IncludeItemByIndex(static_cast<int>(*renamed));
	else
		m_Rename = RenameState();
}
while (clipper.Step())
{
	for (int row = clipper.DisplayStart; row < clipper.DisplayEnd; row++)
		DrawRow(context, commands, runner, scene, static_cast<size_t>(row));
}
io = ImGui::EndMultiSelect();
ApplySelectionRequests(context, scene, *io);
```

1. **Lines 689–690:** the flags choose the gestures: clear on `Esc`, clear on a click in the void, box select along one axis, and selecting on release so that a row can be dragged first.
2. **Line 693:** `BeginMultiSelect` receives the selection's size and the row count, and returns the requests so far.
3. **Lines 696–700:** the clip skips rows off screen, but ImGui needs the anchor row of a range even when it has scrolled away, so `IncludeItemByIndex` forces it in.
4. **Lines 701–708:** the row being renamed is also forced in, because a text field that is not drawn would lose the person's typing. A renamed entity that a filter hides is no longer renamed.
5. **Lines 714–715:** the requests from the clicks of this frame are applied after `EndMultiSelect`.

Both `ApplySelectionRequests` calls matter. The first handles requests made before the items are drawn, such as **Ctrl+A** or clearing. The second handles requests from the clicks and box selects of this frame, which arrive only after ImGui has seen every drawn item. The figure shows the flow.

```mermaid caption="The request flow of a multi-select scope. ImGui names items by user data, and the panel turns the names into entities." alt="A sequence between ImGui, the panel and the editor's selection. The person clicks, ImGui returns a range request, and the panel finds the rows of both ends. The panel applies the request and sets the selection, which the next frame draws."
sequenceDiagram
	participant P as Person
	participant G as ImGui
	participant H as Panel
	participant C as EditorContext
	P->>G: Shift and click on a row
	G->>H: SetRange request with two user data values
	H->>H: FindSelectionRow for each end
	H->>H: Build the range of entity UUIDs
	H->>C: SetSelection with the new list
	C-->>H: IsSelected answers while drawing
```

The stored number is converted to a row only now, in `FindSelectionRow`. That is the reason for the stable-identity rule: between the click and this call the rows can change, and the handle still finds the entity.

```cpp src="StrataEditor/src/Panels/SceneHierarchyPanel.cpp#L1173-L1198"
// The ends are entities: their rows now (rows may have appeared above the first since it was clicked). An end
// whose row is gone (collapsed away, deleted) leaves the range at the other one.
std::optional<size_t> first = FindSelectionRow(scene, request.RangeFirstItem);
std::optional<size_t> last = FindSelectionRow(scene, request.RangeLastItem);
if (!first && !last)
	continue;
if (!first)
	first = last;
if (!last)
	last = first;
const size_t begin = std::min(*first, *last);
const size_t end = std::max(*first, *last);
std::vector<UUID> range;
range.reserve(end - begin + 1);
for (size_t row = begin; row <= end; row++)
{
	if (!filtering || rows[row].IsMatch() || begin == end)
		range.push_back(rows[row].ID);
}
// Selected rows move to the end in the order the range was made, so the row clicked last is the primary selection.
if (request.RangeDirection < 0)
	std::reverse(range.begin(), range.end());
const std::unordered_set<UUID> inRange(range.begin(), range.end());
std::erase_if(selection, [&inRange](UUID id) { return inRange.contains(id); });
if (request.Selected)
	selection.insert(selection.end(), range.begin(), range.end());
```

1. **Lines 1175–1176:** the two ends of the range become rows again at this moment, not rows from an earlier frame.
2. **Lines 1177–1182:** an end that has no row now, because it was collapsed away or deleted, leaves the range at the other end.
3. **Lines 1187–1191:** while a filter is on, a range takes the matches only, so a search by component selects exactly the entities to edit together.
4. **Lines 1193–1194:** a backward Shift range is reversed, so that the row the person clicked last stays last, as the primary selection.
5. **Lines 1195–1198:** old entries of the range are removed first, so a row is never listed twice, and then the range is added.

The panel never lets the selection change anything else. It ends with `context.SetSelection`, and the Inspector, the gizmo and the commands read the selection from the context. When something else selects an entity, such as a pick in the Scene view, the panel asks `HierarchyView::Reveal` to expand the ancestors and scrolls to the row.

## The real code: drag and drop

A person changes the order of the scene by dragging rows. The tools here are small and the order of events matters.

**A drag and drop payload** is a block of :term[bytes]{id=byte} with a type name that a drag carries from its source to a target. The source sets it with `SetDragDropPayload`. A target asks for a type with `AcceptDragDropPayload` and receives the bytes only if the type matches. The editor has three payload types.

| Payload name | Bytes | Source | Targets |
| --- | --- | --- | --- |
| `STRATA_ENTITIES` | UUIDs of entities, in hierarchy order | A Hierarchy row | Hierarchy rows and background, a Content Browser folder (makes a :term[prefab]{id=prefab-world}), Inspector fields |
| `STRATA_ASSET` | One :term[asset handle]{id=asset-handle} | A Content Browser tile | Hierarchy rows, the Scene view, folders (moves the asset), Inspector fields |
| `STRATA_ASSET_FOLDER` | A folder path, not ended by a zero | A Content Browser folder | Folders (moves the folder) |

The source is short. It decides what is dragged and sets the payload once.

```cpp src="StrataEditor/src/Panels/SceneHierarchyPanel.cpp#L780-L790"
if (ImGui::BeginDragDropSource())
{
	if (m_Dragged.empty())
		m_Dragged = selected ? HierarchyView::GetTopmostInHierarchyOrder(scene, context.GetSelection()) : std::vector<UUID> { id };
	ImGui::SetDragDropPayload(DragDrop::c_Entities, m_Dragged.data(), m_Dragged.size() * sizeof(UUID), ImGuiCond_Once);
	if (m_Dragged.size() == 1)
		ImGui::Text("%s  %s", UI::GetEntityIcon(registry, row.Handle), registry.get<NameComponent>(row.Handle).Name.c_str());
	else
		ImGui::Text("%s  %zu entities", Icons::Layers, m_Dragged.size());
	ImGui::EndDragDropSource();
}
```

1. **Lines 782–783:** dragging a selected row drags the whole selection, reduced to its topmost entities in hierarchy order, and dragging a row that is not selected drags only that row.
2. **Line 784:** the payload holds UUIDs, never handles or row numbers, and `ImGuiCond_Once` means ImGui copies it at the start of the drag.
3. **Lines 785–788:** the small label that follows the pointer names one entity or counts many.

`GetTopmostInHierarchyOrder` drops every entity whose ancestor is also listed, since an entity moves, copies and deletes with its ancestor. It sorts the others in hierarchy order, so the first dropped entity ends at the first position.

A target acts only on delivery, which is the moment the mouse button is released. Before that, a Hierarchy row wants to draw a line that shows where the drop will land, and for that it needs the payload while the pointer is still moving. So `AcceptRowDrops` passes `ImGuiDragDropFlags_AcceptBeforeDelivery`, which makes `AcceptDragDropPayload` return the payload on every frame of the hover, and it draws the line or the frame itself. Only when `payload->IsDelivery()` is true does it run the command.

```cpp src="StrataEditor/src/Panels/SceneHierarchyPanel.cpp#L1071-L1078"
if (target && payload->IsDelivery())
{
	const nlohmann::json parameters = { { "entities", ToJson(dragged) },
		{ "parent", target->Parent.IsValid() ? UUIDToJson(target->Parent) : nlohmann::json(nullptr) }, { "index", target->Index } };
	// Dropped into a collapsed entity: open it, so the entities stay in view.
	if (target->Parent.IsValid())
		m_View.SetExpanded(target->Parent, true);
	m_Deferred.push_back([&context, &commands, parameters]() { RunEditorCommand(context, commands, "entity.setParent", parameters); });
```

The command is `entity.setParent`, and it is run through the deferred list after drawing, never in the middle of the row loop. A drop into a collapsed entity first expands it, so the dropped entities stay in view.

### Drop zones

A row has three drop zones. The top quarter of the row's height means before the row's entity, the bottom quarter means after it, and the middle half means inside it, as its last child. A drop is described in the terms of the command: a parent, which is null for the top level, and an index among that parent's children.

:::example[A drop, by hand]
The scene has A, B with children X and Y, and C, and B is expanded. The rows are A, B, X, Y, C. The person drags A to the top quarter of C's row.

The zone is Before, so the parent is the top level, and the landing position is C's :term[sibling index]{id=sibling-index}, which is 2 as A, B, C stand at 0, 1, 2. But A itself leaves the list in front of that position when it moves. After A leaves, C stands at 1, so the index is 2 minus 1, which is 1. The result is B, A, C, with A right before C. The unit test checks exactly this case.
:::

The figure draws this drop and two others of A in the same scene, as the row shows each while the pointer moves, and the three zones of one row.

::figure{id=hierarchy-drop-zones}

`HierarchyView::GetDropTarget` does this arithmetic. Look at how each zone picks a parent and how the entities that leave lower the index.

```cpp src="StrataEditor/src/Editor/HierarchyView.cpp#L576-L609"
const bool showsChildren = m_Rows[row].IsExpanded() && row + 1 < m_Rows.size() && m_Rows[row + 1].Depth > m_Rows[row].Depth;
if (result.Zone == HierarchyDropZone::Inside)
{
	parent = target;
	insertion = scene.GetRegistry().get<HierarchyComponent>(target.GetHandle()).ChildCount;
}
else if (result.Zone == HierarchyDropZone::After && showsChildren)
{
	// The line after an expanded entity lies above its first shown child: the entities go in front of that child.
	parent = target;
	const Entity next = scene.GetEntityByUUID(m_Rows[row + 1].ID);
	insertion = next ? scene.GetSiblingIndex(next) : 0;
}
else
{
	parent = target.GetParent();
	insertion = scene.GetSiblingIndex(target) + (result.Zone == HierarchyDropZone::After ? 1 : 0);
}

// The entities that move: none may become its own ancestor, and those that leave the list in front of the
// insertion point move it forward.
const std::vector<UUID> moving = GetTopmostInHierarchyOrder(scene, dragged);
size_t leaving = 0;
for (const UUID id : moving)
{
	const Entity entity = scene.GetEntityByUUID(id);
	if (parent && (parent == entity || scene.IsDescendantOf(parent, entity)))
		return std::nullopt;
	if (entity.GetParent() == parent && scene.GetSiblingIndex(entity) < insertion)
		leaving++;
}
result.Parent = parent ? parent.GetUUID() : UUID::Null();
result.Index = insertion - leaving;
return result;
```

1. **Lines 577–581:** a drop inside puts the entities after the last child, so the landing position is the child count.
2. **Lines 582–588:** the line after an expanded entity lies above its first shown child, so the entities go in front of that child and not after the whole subtree.
3. **Lines 589–593:** otherwise the target's parent receives them, at the row's sibling index, plus one for After.
4. **Lines 599–606:** a dropped entity may not become its own ancestor, so the function returns nothing then, and a dragged sibling in front of the landing point counts as leaving.
5. **Lines 607–608:** the index is the final position, the landing point minus the entities that left in front of it.

```mermaid caption="From pointer position to a command. The fraction of the row's height picks a zone, and the zone picks a parent and a position." alt="A flow from the pointer's position on a row to one of three zones. The zone gives a parent and a position. A check for cycles then refuses the drop or sends the index to the command."
flowchart TD
	Pointer[Fraction of the row height] --> Zone{Zone}
	Zone -- "below 0.25" --> Before[Before the row's entity]
	Zone -- "0.25 to 0.75" --> Inside[Inside, as last child]
	Zone -- "above 0.75" --> After[After the row's entity]
	After --> Expanded{Row expanded with shown children}
	Expanded -- yes --> First[Before its first child]
	Expanded -- no --> Sibling[One past the row's sibling index]
	Before --> Cycle{Parent is a dragged entity or below one}
	Inside --> Cycle
	First --> Cycle
	Sibling --> Cycle
	Cycle -- yes --> Refuse[Refuse: no-entry cursor]
	Cycle -- no --> Send["entity.setParent with parent and index"]
```

What `SetParent` does to the scene (:term[world transforms]{id=world-transform} are kept, signals are sent) is the subject of [the scene graph](../world/scene-graph.md). Here it is enough that the command takes a parent and an index and that the Hierarchy computes both from what it draws.

The Content Browser's targets are simpler. A folder accepts `STRATA_ASSET` and runs `asset.move`, accepts `STRATA_ASSET_FOLDER` and runs `asset.moveFolder`, and accepts `STRATA_ENTITIES` to make a prefab of the entities ([files and the trash](../editor/trash-references.md)). Each target checks what it is given: an asset already in the folder, a :term[built-in asset]{id=built-in-asset} and a sub-asset (which moves with its file) are skipped.

## The real code: assets and their browser

`AssetBrowserView` is the Hierarchy's twin for assets. `Update` takes the asset manager and compares five things with the last build: the manager's change version, the :term[current folder]{id=current-folder}, the search words, the type filter and the expansion state. When none moved, the call returns at once. A rebuild lists the folder tree depth first, with a stack of pending folders. Then it lists the items: folders first, then assets by name, and the sub-assets of an expanded model right after it.

The view reads the folder index of the asset manager: `GetFolders`, `ListAssets` and `GetChangeVersion` ([the asset manager's index](../assets/handles-meta.md)). It never lists the disk, which is why the editor can show a project of 10,000 assets with no file system calls per frame. A search lists the assets below the current folder instead of its direct items, and filters them by name words and type.

The panel keeps text of its own with each item: the icon, the title with no extension, the name column of the list and the type name. They are made when the view rebuilds, by `RebuildLabels`, since formatting 10,000 strings each frame would be the walk again. The shortened titles, cut to the tile's width, are made on demand and kept until the width changes or the labels are rebuilt.

A grid is clipped by rows of tiles. The panel computes how many tiles fit in a row from the width, takes the number of rows, and gives the clip the rows.

```cpp src="StrataEditor/src/Panels/ContentBrowserPanel.cpp#L893-L910"
ImGuiListClipper clipper;
clipper.Begin(rowCount, rowHeight);
while (clipper.Step())
{
	for (int row = clipper.DisplayStart; row < clipper.DisplayEnd; row++)
	{
		for (int column = 0; column < columns; column++)
		{
			const size_t index = static_cast<size_t>(row) * static_cast<size_t>(columns) + static_cast<size_t>(column);
			if (index >= items.size())
				break;
			if (column > 0)
				ImGui::SameLine(0.0f, spacing);
			const AssetBrowserItem& item = items[index];
			const bool selected = item.Kind == AssetBrowserItemKind::Folder ? item.Path == m_SelectedFolder
				: item.Handle == m_Selected || item.Handle == m_Revealed;
			const bool subAsset = item.Kind == AssetBrowserItemKind::SubAsset;
			ImGui::PushID(static_cast<int>(index));
```

1. **Lines 893–894:** the clip counts rows of tiles, not tiles, and every row has the same height.
2. **Lines 897–899:** inside one visible row, the loop draws one tile for each column.
3. **Line 910:** the widget identity is the item's index, which is fine for a widget that lives one frame; selection is stored by asset handle, not by this number.

For example, suppose the :term[font]{id=font} is 16 pixels, so a tile 6.5 font sizes wide is 104 pixels, and with 8 pixels of spacing a panel 800 pixels wide holds 7 tiles per row. A project of 10,000 assets then has 1,429 rows of tiles. A tile is taller than it is wide, since its name stands under the picture: with ImGui's usual spacing a row of tiles takes about 136 pixels. A panel 400 pixels high shows three rows and part of a fourth, so 28 tiles are drawn, and 28 thumbnails are asked for, not 10,000.

The thumbnail is asked for in the loop, where the tile draws its picture.

```cpp src="StrataEditor/src/Panels/ContentBrowserPanel.cpp#L933-L938"
nvrhi::ITexture* thumbnail = item.Kind != AssetBrowserItemKind::Folder && thumbnails ? thumbnails->Request(item.Handle) : nullptr;
if (thumbnail)
{
	const nvrhi::TextureDesc& desc = thumbnail->getDesc();
	const float side = std::min(squareMax.x - squareMin.x, squareMax.y - squareMin.y);
	const float scale = side / static_cast<float>(std::max(desc.width, desc.height));
```

`Request` is called for every tile drawn, and returns null until the picture is ready, when the tile draws the type's icon in its place. A tile that scrolls away stops asking: a picture still waiting leaves the queue, and a finished one is among the first forgotten when the cache is full. That is the third rule of the contract at work. The cache and its limits are in [the thumbnails page](../editor/thumbnails.md).

::figure{id=content-grid}

::figure{id=hierarchy-expanded}

::figure{id=hierarchy-searched}

## Other cached and clipped lists

The same ideas appear in the editor's other lists, and the details are in [instrument panels](../editor-ui/instrument-panels.md). The Activity panel rebuilds its rows when the command journal's version changes. The Problems panel rebuilds when the build or the crash changes, so an idle frame compares one number and one string. The Console, the Activity rows, the Problems rows, the Streaming table, the script browser, the joint tree of animation assets and the picker for assets all draw through an `ImGuiListClipper`.

Two lists use background work. The Streaming table is read at most every `c_TableRefreshSeconds` while the panel is visible. The main thread copies the samples, and a job names, sorts and filters the rows, so no frame sorts tens of thousands of rows. The Scripts root of the Content Browser lists the files on an I/O thread when it is first drawn, and again every second while it is drawn ([jobs](../core/jobs.md)). In both, the panel draws the last finished rows until new ones arrive.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Draw every row every frame | Small tools and early prototypes | The least code, no cache to go stale | A frame cost that grows with the scene: 200 ms at 100,000 rows in the example |
| Let ImGui own the selection (`ImGuiSelectionBasicStorage`) | Programs whose items have a stored selected flag | Less code in the panel | The editor's selection is shared with the Inspector, gizmo and commands, so it has to live in `EditorContext` |
| Store selection as row indexes | Simple list widgets | No lookup from entity to row | A selection that names the wrong entity as soon as a row appears above it |
| Rebuild the rows every frame, then clip | Many immediate-mode tools | No versions to track | The cost of the walk each frame, for every panel that shows the scene |
| Sort and filter on the main thread | Small lists | No job and no late results | A frame that stalls on tens of thousands of rows |

## How it is tested

The suite `Editor.HierarchyView` drives the model with no window. One test checks the rows follow the expansion and rebuild only when what they show changed. One checks that 100,000 top-level entities rebuild no rows over idle frames, and that a rename rebuilds only while a name search is on. Others cover the filters, the `l:` and `cell:` terms, revealing an entity 50 levels deep, the drop zones with their parents and indexes, and the topmost entities of a selection. The suite `Editor.AssetBrowserView` and the suite `Editor.UI.ContentBrowser` check the view's order and its rebuilds, and the panel's reveal, drops and tiles.

The metrics `HierarchyIdleUpdate100kRoots` and `HierarchyRebuild100kRoots` of the `Perf.Editor` suite hold the cost of an idle update and of a rebuild against budgets, and run only in :term[optimized]{id=optimization} builds with the label `perf`. To run a suite, name it:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.HierarchyView
```

Run that from the engine's root after a build. A regression test for this area counts rebuilds, as the tests above do. A count that stays at one over a thousand frames is an exact claim, where a timing is only a hope.

## Changing it safely

To add a filter term, extend `HierarchyFilter::Parse` and add the field that holds the term. Include it in `IsEmpty`, test it in `Matches`, and connect the signals that can change its answer in `ConnectFilterSignals`, only while it is in use. Add a test to `Editor.HierarchyView` that parses the term and that checks a change of the scene's data is seen at the next update. A term that reads data without a signal shows stale rows.

To add a list of your own, follow the contract in order. Put the rows in a model without UI, rebuild it by a version, draw it through a `clipper`, identify rows by UUID or handle, and ask for pictures every frame they show. Check that the model's rebuild count stays at one over idle frames. Never write to the scene from a panel: send a command.

Other rules apply. Hierarchy changes go through `Scene`, never by editing the links. Code that writes a transform signals it. A drop that changes the scene is one command, so one :term[undo step]{id=undo-step} restores it. Before a commit, run the suites above and the `Perf.Editor` metrics if the change can move them.

## Summary

- The cost of a list per frame must follow the rows on screen, so a list is cached, clipped and identified by entity, never by position.
- `HierarchyView` rebuilds its rows only when the scene, the hierarchy version, the expansion or the filter changed, and a rename rebuilds them only while a name search is typed.
- Selection requests from ImGui name items by :term[user data]{id=user-pointer}, which is the entity handle, and the panel turns them into rows at the moment it applies them.
- A drop's zone gives a parent and an index, corrected for entities that leave the list first, and a cycle refuses the drop.
- A filter term needs a field that holds it, a match, a signal and a test, and the clip's saving shows by counting the rows drawn.

## Check yourself

1. A scene has 100,000 entities and the Hierarchy window shows 30 rows. Which cost is right for one frame with nothing changed? (a) 100,000 rows drawn, (b) 30 rows drawn and the rows rebuilt, (c) 30 rows drawn and no rebuild, (d) no rows drawn.

   :::answer{tests="cost-follows-screen"}
   (c). The `clipper` draws the rows of the window and the version gate finds nothing changed, so no rebuild happens. (a) is the walk the page rejects. (b) would be right only for the frame after a change. (d) is wrong because the rows still draw each frame.
   :::

2. In a scene without a search, you rename an entity in the Hierarchy. How many times does `HierarchyView` rebuild its rows? What changes if a search for a name is typed?

   :::answer{tests="rebuild-by-version"}
   None without a search: rows keep a handle and an identifier, and the name is read when drawing. With a name search, the view listens to name changes and rebuilds once at the next update, since the matches may change.
   :::

3. A person selects rows 3 to 6 by clicking row 3 and then Shift and clicking row 6. Before the request is applied, a script creates an entity at the top. Why is the selection still right? What would break if the user data were the row index?

   :::answer{tests="selection-identity"}
   The user data is the entity's handle, and `FindSelectionRow` finds the rows at apply time, so the new top row shifts both ends by one and the range still holds the same entities. With indexes, the range would name rows 3 to 6 of the new list, one entity off at each end.
   :::

4. The rows are A, B (expanded, with children X and Y), C. You drag C onto the bottom quarter of B's row. What are the parent and the index?

   :::answer{tests="drop-mapping"}
   The zone is After and B is expanded with shown children, so the entities go in front of its first child: the parent is B and the landing position is X's sibling index, 0. C is not a child of B, so nothing leaves in front. The index is 0, and the result is C, X, Y under B.
   :::

5. Why does a Hierarchy row pass `AcceptBeforeDelivery` when it accepts a drag?

   :::answer{tests="drop-mapping"}
   Without the flag the payload is returned only on the release, so the row could not draw the drop line while the pointer moves. With it, the row sees the payload every frame and draws, and it runs the command only when `IsDelivery()` is true.
   :::

6. You add the term `a:` that shows inactive entities. A person switches an entity's eye while `a:` is typed, and the rows do not change. What is missing?

   :::answer{tests="add-filter"}
   The view listens only to what the filter reads. Connect the construct and destroy signals of `InactiveComponent` in `ConnectFilterSignals`, so a switch sets the dirty flag and the next `Update` rebuilds. A filter without a signal shows stale rows until something else rebuilds them.
   :::

## Exercises

1. **Basic.** The marking loop stops at an ancestor that is already marked. Write a program that counts the steps of marking a chain of 1,000 entities that all match, with and without the stop, and report both counts.

   :::answer[Worked solution]{tests="cost-follows-screen" solution="sketches/editor-ui-lists-marks.cpp"}
   Each entity's parent is the one before it. Without the stop every match walks to the root, so the steps are 0 + 1 + ... + 999. With the stop a match walks at most two steps: its parent is marked in the step before, and the next ancestor is already marked.

   ```cpp sketch="editor-ui-lists-marks.cpp"
   // Marking the ancestors of matches: walking to the root for every match, and stopping at a marked ancestor.
   #include <cstdio>
   #include <vector>

   namespace
   {

   	constexpr int c_ChainLength = 1000;

   }

   int main()
   {
   	// A chain: entity 0 is the root and entity i is the child of entity i - 1. Every entity matches.
   	std::vector<int> parents(c_ChainLength);
   	for (int entity = 0; entity < c_ChainLength; entity++)
   		parents[entity] = entity - 1;

   	long everyStep = 0;
   	for (int match = 0; match < c_ChainLength; match++)
   	{
   		for (int parent = parents[match]; parent >= 0; parent = parents[parent])
   			everyStep++;
   	}

   	long onceStep = 0;
   	std::vector<bool> marked(c_ChainLength, false);
   	for (int match = 0; match < c_ChainLength; match++)
   	{
   		for (int parent = parents[match]; parent >= 0; parent = parents[parent])
   		{
   			onceStep++;
   			if (marked[parent])
   				break;
   			marked[parent] = true;
   		}
   	}

   	std::printf("steps without the stop: %ld\n", everyStep);
   	std::printf("steps with the stop: %ld\n", onceStep);
   	return 0;
   }
   ```

   ```text output-of="editor-ui-lists-marks.cpp"
   steps without the stop: 499500
   steps with the stop: 1997
   ```

   1. **Lines 19–25:** without the stop, every match walks all the way to the root.
   2. **Lines 33–34:** with the stop, a walk ends at the first ancestor that is marked.

   The first count is 499,500, the sum of 0 to 999. The second is about twice the number of entities, so marking is linear.
   :::

2. **Medium.** Trace it yourself. In a scene of many entities, learn in a debugger when `HierarchyView::Update` returns early, when it calls `Rebuild` after a move to a new parent, and when a rename rebuilds the rows. Name the file and the lines.

   :::answer[Worked solution]{tests="rebuild-by-version"}
   The file is `StrataEditor/src/Editor/HierarchyView.cpp`. Put a breakpoint in `HierarchyView::Update`. On an idle frame the dirty flag is false and the version matches, so it returns false before `Rebuild`. A move to a new parent moves the hierarchy version, so the check fails and `Rebuild` runs once. A rename does not reach `Rebuild` unless a name search is typed, when `OnComponentChanged` sets the dirty flag.
   :::

3. **Hard.** Add the filter term `a:` that shows inactive entities, with tests in `Editor.HierarchyView`. State what to change in `HierarchyView.h` and `HierarchyView.cpp`, and which signals it needs.

   :::answer[Worked solution]{tests="add-filter"}
   Add a flag to `HierarchyFilter` for the term, set it in `Parse`, and include it in `IsEmpty`. In `Matches`, return false when the entity lacks `InactiveComponent`. In `ConnectFilterSignals`, connect `on_construct` and `on_destroy` of `InactiveComponent` to `OnComponentChanged`, as the code does for `SubSceneComponent`, so switching the eye rebuilds the rows. The tests give `a:` to `HierarchyFilter::Parse`, build a scene with one inactive entity and check the rows and the ancestors, then switch the entity's eye and expect a rebuild at the next update. To measure the clip, change the loop in `DrawRows` in a scratch build to draw every row, time the panel with 100,000 entities, and do not commit the change.
   :::

## Where it lives in Strata

- Models: `StrataEditor/src/Editor/HierarchyView.h`, `HierarchyView.cpp`, `AssetBrowserView.h`, `AssetBrowserView.cpp`.
- Panels: `StrataEditor/src/Panels/SceneHierarchyPanel.cpp` and `StrataEditor/src/Panels/ContentBrowserPanel.cpp`.
- Payload names: `StrataEditor/src/UI/PropertyWidgets.h` (`DragDrop`) and `ContentBrowserPanel::c_FolderPayload`.
- Tests: `StrataTests/src/Editor/HierarchyViewTests.cpp`, `ContentBrowserUITests.cpp` and `EditorPerfTests.cpp`.
- Command: `entity.setParent`, and `editor.showPanel` with its `search` for the Hierarchy.

## Further reading

- Dear ImGui, the multi-select section of its header and its wiki page on multi-selection: the protocol of requests, intermediate.
- Robert Nystrom, Game Programming Patterns, the chapter on dirty flags: why a cached value is rebuilt only after a change, beginner.
- Sedgewick and Wayne, Algorithms, the chapter on stacks and queues: the data structure behind the resume stack, beginner.
