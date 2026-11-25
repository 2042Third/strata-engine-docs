---
id: ui/contract
title: "The UI contract"
description: "How the game's user interface learns what changed, redoes only that work, and checks itself against a complete calculation."
kind: internals
size: M
tracks: [E]
needs: [ui/layout]
time: 60
learn:
  - id: signal-rule
    text: explain why every direct write to a user interface component must be signaled, and which writers already signal
  - id: change-cost
    text: predict which work counters a given change moves, from its kind and the rect's fit settings
  - id: layout-cache
    text: explain how layouts are kept per size in canvas units and why a window change at the same aspect lays out nothing
  - id: validation
    text: trace how validation finds a write without a signal and why Release builds do not
since: 0.4.0
status: final
---

The game's user interface (UI) keeps, for every canvas, the boxes of its elements, their shaped texts, their quads, their
:term[clip rects]{id=clip-rect} and the grids that find the element under a pointer. The **UI contract** is the promise between the code that
changes UI components and `GameUIScene`. Every direct write to a component is signaled, and in return the scene redoes
only the work that the change needs. The page covers how a signal becomes work, the rules for writers, and the check that
catches a broken promise. It omits how quads reach the :term[graphics card]{id=gpu}, how a pointer finds an element, and how the
editor undoes edits.

## The problem and how engines solve it

A retained interface keeps its results between frames, so it must learn which input changed. The scene's [transform
contract](../world/scene-graph.md) has the same shape: writers signal, the scene marks what is stale and computes it again
once. Engines solve the problem by polling, by redoing everything, or by observing changes; the table near the end of the
page compares them, and the sections between show the choice Strata made.

## The map

Everything starts with a write to a component and ends with a range of changed quads. The diagram follows one change from
the signal to the work it causes.

```mermaid caption="A signaled write marks an element; the update climbs to a root, lays the subtree out and marks the quads of boxes that moved." alt="A flow chart. A signaled write marks an element for layout, quads or both, and each mark climbs to the highest ancestor whose rect depends on its children. The subtree is laid out again, the boxes are compared, and quads of moved boxes are marked with a range in the journal."
flowchart LR
    Write["Write to a component"] -->|"MarkModified or registry.patch"| Signal["Registry signal"]
    Signal --> Mark["Mark: layout, quads or both"]
    Mark --> Walk["Walk up to the re-layout root"]
    Walk --> Layout["Lay the subtree out again"]
    Layout --> Compare["Compare old and new boxes"]
    Compare -->|"moved or resized"| Quads["Mark quads, bump the hit stamp"]
    Quads --> Journal["Range in the quad journal"]
    Journal --> Upload["Partial upload (ui/drawing)"]
```

Two threads of work run beside this chain. The hierarchy, activity and asset journals tell the scene about changes that
no component signal reports, and `Validate` compares the whole cache with a fresh calculation. All of it runs on the :term[main
thread]{id=main-thread}, inside `GameUIScene` in `Strata/src/Strata/GameUI/GameUIScene.cpp`, with the layout passes in
`Strata/src/Strata/GameUI/GameUILayout.cpp`.

## The contract

The rules are few, and each has a reason.

1. **Signal every direct write.** Code that writes a field of a UI component in place calls `Entity::MarkModified` or
   `registry.patch`. The reason: `GameUIScene` keeps its results and learns of a change only through the registry's
   `on_update`, `on_construct` and `on_destroy` signals, so a write without a signal leaves a stale result.
2. **A value written right after `AddComponent` needs no signal.** The construct signal already marked the element, and
   the scene's own [transform contract](../world/scene-graph.md) says the same.
3. **Change the hierarchy through `Scene`.** `SetParent` and its relatives write every form of the hierarchy and its
   version together, and the UI reads the version's change log. Moving plain entities, which hold no :term[UI element]{id=ui-element}, costs
   the UI nothing.
4. **Do not make an idle frame cost per element.** The UI system runs in every scene, so a menu that costs a few
   comparisons when nothing changes must not become a loop over its elements. Games that set their heads-up display
   (HUD) every frame rely on this.

:::rule[Signal what you write in place]
A direct write to a UI component field is followed by `MarkModified` or `registry.patch`. The reason: `GameUIScene`
computes again only what it was told, and Debug builds check the cache against a fresh calculation that names the
culprit. The engine's `AGENTS.md` states the rule under "Game UI".
:::

Several writers already signal for you. `ComponentAccess::SetProperty` ends with the component's `MarkModified`, and the
editor's property edits go through it. The script application programming interface (API) reaches components through the
UI system, whose writers patch the component with `registry.patch`.

One writer deserves a closer look. `GameUISystem::SetText`, behind the script function that sets a text, patches the text
only when it differs from the text already there. Games set their HUD every frame, and a signal for an unchanged text
would shape it again for nothing. On an input field the function writes one line, cut to the character limit, and patches
only when that line differs.

:::why[Why signals and not a version per component?]
A version number that every writer must bump is a signal too, only one that cannot say which entity changed. The registry
already offers a signal per entity, so the scene learns exactly which element to mark and can leave the rest alone. The
cost is the rule itself: a writer that forgets it gets no error in Release, only a picture that does not follow.
:::

## A toy version

The toy caches the area of a rect behind a :term[dirty flag]{id=dirty-flag}, the pattern the scene applies to boxes. The program makes one write
with a signal and one without. Watch how often the area is computed and what `Validate` answers.

```cpp sketch="ui-contract-toy.cpp"
// A toy UI contract: a cached area behind a dirty flag, a writer that signals and a writer that does not.
#include <cstdio>

struct Rect
{
	float Width = 10.0f;
	float Height = 5.0f;
};

class AreaCache
{
public:
	explicit AreaCache(const Rect& rect)
		: m_Rect(rect)
	{
	}

	// The signal: the rect changed, so the cached area is stale.
	void MarkModified() { m_Dirty = true; }

	float GetArea()
	{
		if (m_Dirty)
		{
			m_Area = m_Rect.Width * m_Rect.Height;
			m_Dirty = false;
			m_Computations++;
		}
		return m_Area;
	}

	// The full recomputation: the cache is true when it agrees with the rect.
	bool Validate() const { return m_Area == m_Rect.Width * m_Rect.Height; }

	int GetComputations() const { return m_Computations; }

private:
	const Rect& m_Rect;
	float m_Area = 0.0f;
	bool m_Dirty = true;
	int m_Computations = 0;
};

int main()
{
	Rect rect;
	AreaCache cache(rect);
	std::printf("first area %.0f, idle frames add 2 reads: %.0f %.0f\n", cache.GetArea(), cache.GetArea(), cache.GetArea());
	std::printf("computations %d\n", cache.GetComputations());

	rect.Width = 20.0f;
	cache.MarkModified();
	const float signaledArea = cache.GetArea(); // Read before Validate: printf's arguments have no fixed order
	std::printf("signaled write: area %.0f, valid %d\n", signaledArea, cache.Validate());
	rect.Height = 8.0f; // No MarkModified
	std::printf("unsignaled write: area %.0f, valid %d\n", cache.GetArea(), cache.Validate());
	std::printf("computations %d\n", cache.GetComputations());
	return 0;
}
```

```text output-of="ui-contract-toy.cpp"
first area 50, idle frames add 2 reads: 50 50
computations 1
signaled write: area 100, valid 1
unsignaled write: area 100, valid 0
computations 2
```

1. **Line 19:** the signal only sets a flag; the work waits for the next read.
2. **Lines 21–30:** a read computes only when the flag is set, so a quiet read costs one comparison.
3. **Line 33:** the one reader that does not trust the flag: it computes the area from the rect and compares.
4. **Line 53:** the area is read into a variable first, because C++ fixes no order for a call's arguments.
5. **Lines 55–56:** the height changes without a signal, so the cache returns the old area and `Validate` reports false.

The three reads after the first compute nothing: the flag stayed false. The write with a signal computes once and the
cache agrees with the rect. The write without a signal changes the height, but the flag stays false, so `GetArea` returns
the old area. Nothing notices except `Validate`, which computes the area again and compares. The real scene works the
same way, with more kinds of mark and more kinds of result.

## The real code

The real code is read in the order a change flows. The running example is the Play label of the Third-Person sample's
main menu: a `UIText` whose text is "Play", under the Play button, with a rect that stretches over the button and fits no
content.

### The signals

The :term[constructor]{id=constructor} of `GameUIScene` connects the registry's signals of every UI component. The connections are never
released, because the scene object lives exactly as long as the storages that hold them.

```cpp src="Strata/src/Strata/GameUI/GameUIScene.cpp#L112-L142" from="registry.on_construct<UICanvasComponent>()" to="registry.on_destroy<UIInputFieldComponent>().connect<&GameUIScene::OnInputFieldAddedOrRemoved>(*this);" symbol="GameUIScene::GameUIScene"
registry.on_construct<UICanvasComponent>().connect<&GameUIScene::OnCanvasAddedOrRemoved>(*this);
registry.on_update<UICanvasComponent>().connect<&GameUIScene::OnCanvasChanged>(*this);
registry.on_destroy<UICanvasComponent>().connect<&GameUIScene::OnCanvasAddedOrRemoved>(*this);
registry.on_construct<UIRectComponent>().connect<&GameUIScene::OnStructureChanged>(*this);
registry.on_update<UIRectComponent>().connect<&GameUIScene::OnLayoutChanged>(*this);
registry.on_destroy<UIRectComponent>().connect<&GameUIScene::OnStructureChanged>(*this);
registry.on_construct<UILayoutComponent>().connect<&GameUIScene::OnLayoutChanged>(*this);
registry.on_update<UILayoutComponent>().connect<&GameUIScene::OnLayoutChanged>(*this);
registry.on_destroy<UILayoutComponent>().connect<&GameUIScene::OnLayoutChanged>(*this);
registry.on_construct<UIImageComponent>().connect<&GameUIScene::OnVisualChanged>(*this);
registry.on_update<UIImageComponent>().connect<&GameUIScene::OnVisualChanged>(*this);
registry.on_destroy<UIImageComponent>().connect<&GameUIScene::OnImageDestroyed>(*this);
registry.on_construct<UITextComponent>().connect<&GameUIScene::OnTextChanged>(*this);
registry.on_update<UITextComponent>().connect<&GameUIScene::OnTextChanged>(*this);
registry.on_destroy<UITextComponent>().connect<&GameUIScene::OnTextDestroyed>(*this);
registry.on_construct<UISelectableComponent>().connect<&GameUIScene::OnVisualChanged>(*this);
registry.on_update<UISelectableComponent>().connect<&GameUIScene::OnVisualChanged>(*this);
registry.on_destroy<UISelectableComponent>().connect<&GameUIScene::OnSelectableDestroyed>(*this);
registry.on_construct<UIToggleComponent>().connect<&GameUIScene::OnToggleChanged>(*this);
registry.on_update<UIToggleComponent>().connect<&GameUIScene::OnToggleChanged>(*this);
registry.on_destroy<UIToggleComponent>().connect<&GameUIScene::OnToggleChanged>(*this);
registry.on_construct<UISliderComponent>().connect<&GameUIScene::OnSliderChanged>(*this);
registry.on_update<UISliderComponent>().connect<&GameUIScene::OnSliderChanged>(*this);
registry.on_destroy<UISliderComponent>().connect<&GameUIScene::OnSliderChanged>(*this);
// A mask added or removed changes which clip rect each element of its subtree has: the canvas is rebuilt.
registry.on_construct<UIMaskComponent>().connect<&GameUIScene::OnStructureChanged>(*this);
registry.on_update<UIMaskComponent>().connect<&GameUIScene::OnMaskChanged>(*this);
registry.on_destroy<UIMaskComponent>().connect<&GameUIScene::OnStructureChanged>(*this);
registry.on_construct<UIInputFieldComponent>().connect<&GameUIScene::OnInputFieldAddedOrRemoved>(*this);
registry.on_update<UIInputFieldComponent>().connect<&GameUIScene::OnInputFieldChanged>(*this);
registry.on_destroy<UIInputFieldComponent>().connect<&GameUIScene::OnInputFieldAddedOrRemoved>(*this);
```

1. **Lines 112–114:** a canvas added or removed makes the scene find its list of :term[root canvases]{id=root-canvas} again.
2. **Lines 115–117:** a changed rect marks layout and quads; an added or removed rect changes structure.
3. **Lines 121–123:** an image change marks quads only.
4. **Lines 136–139:** a mask added or removed rebuilds the canvas, because the clip rects of its :term[subtree]{id=subtree} change.

Each component has its own handlers, and their cost follows the kind of change. A rect or layout change marks the
element for layout and for quads. An image or a selectable marks quads only. Adding or removing a rect, a mask or a
canvas changes structure, which the next update handles by finding the element's canvas again.

| Component | Handler | Work it marks |
| --- | --- | --- |
| Rect, layout | `OnLayoutChanged` | Layout and quads of the element |
| Image, selectable | `OnVisualChanged` | Quads of the element, and of its tint target |
| Text | `OnTextChanged` | A reshape, quads, and a layout only when the rect fits its text |
| Mask, rect added or removed | `OnStructureChanged` | The canvas is rebuilt at the next update |
| Canvas | `OnCanvasChanged` | Every layout of a :term[root canvas]{id=root-canvas} |

The text handler shows why one signal can cost one thing or another.

```cpp src="Strata/src/Strata/GameUI/GameUIScene.cpp#L225-L242" symbol="GameUIScene::OnTextChanged"
void GameUIScene::OnTextChanged(entt::registry&, entt::entity entity)
{
	const ElementRef* ref = FindRef(entity);
	if (!ref)
		return;
	Canvas& canvas = m_Canvases[ref->Canvas];
	for (Layout& layout : canvas.Layouts)
	{
		if (ref->Element < layout.Texts.size())
			layout.Texts[ref->Element].Valid = false;
	}
	MarkElementQuadsDirty(ref->Canvas, ref->Element);
	UpdateRaycastTarget(entity);
	// Only a rect that fits its text measures it.
	const UIRectComponent* rect = m_Registry->try_get<UIRectComponent>(entity);
	if (rect && rect->FitContent != UIFitContent::None)
		MarkElementLayoutDirty(ref->Canvas, ref->Element);
}
```

1. **Lines 231–235:** every layout of the canvas drops the shaped text, because each size shapes its own.
2. **Line 236:** the element's quads are marked; nothing else is yet.
3. **Lines 238–241:** only a rect that fits its text depends on the shaped width, so only then is layout marked.

When the Play label's text changes, the handler finds its element, drops the shaped text of every layout, marks the
quads and looks at the rect. The rect's `FitContent` is `None`, so nothing is marked for layout: the label's box does not
depend on its text. If the rect fitted its content, the box would be marked and its parents might follow.

### The journals

Some changes no component signal reports: an entity moves to another parent, a parent becomes inactive, a font finishes
loading. `ProcessChanges` reads three journals, each a log with a version that the scene remembers: the hierarchy moves of
the scene, the :term[world transform]{id=world-transform} changes and the asset content changes.

The hierarchy journal lists the entities that moved. For each one, the scene finds the canvases it left and entered and
rebuilds only those. An entity that no canvas holds as an element costs nothing, which is why moving a mesh to a hand is
free for the UI.

Activity comes from the world transform change log, filtered by the element index. Every moving body costs the UI one
table lookup, and only an element whose active flag flipped marks its quads and, when its parent places children, the
parent's layout. The asset journal says which fonts and textures loaded, reloaded or went. Texts that use a font that
arrived are shaped again, because the default font that shaped them before is replaced.

A journal has a limit. When the log no longer reaches back to the version the scene remembers, the scene stops trusting
its list of changes. For the hierarchy it finds the canvas list again and rebuilds every canvas, keeping the layouts of
elements that stay. For the transform log it checks the activity of every element. The work is larger but correct, and it
happens only after a long gap, such as a scene that was not updated for many frames.

### The walk up

`UpdateLayout` turns marks into laid-out boxes. A canvas whose layout is marked wholly dirty lays out every element once
and counts a full rebuild. Otherwise each marked element climbs to the highest ancestor whose rect depends on its
children, and only then is a :term[subtree]{id=subtree} laid out.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L121-L157" from="// Each marked element's subtree, from the highest ancestor whose rect depends on its children; nested roots are" to="roots.clear();" symbol="GameUIScene::UpdateLayout"
// Each marked element's subtree, from the highest ancestor whose rect depends on its children; nested roots are
// covered by the root above them.
std::vector<uint32_t>& roots = layout.Dirty;
for (uint32_t& root : roots)
{
	layout.DirtyMarks[root] = 0;
	while (canvas.Elements[root].Parent != c_NoElement && DependsOnChildren(canvas.Elements[root].Parent, canvas))
		root = canvas.Elements[root].Parent;
}
std::sort(roots.begin(), roots.end());
roots.erase(std::unique(roots.begin(), roots.end()), roots.end());
uint32_t coveredEnd = 0;
for (const uint32_t root : roots)
{
	if (root < coveredEnd)
		continue;
	const uint32_t end = canvas.Elements[root].SubtreeEnd;
	coveredEnd = end;
	m_BoxScratch.assign(layout.Boxes.begin() + root, layout.Boxes.begin() + end);
	LayOutSubtree(canvas, layout, root, layout.Boxes);
	m_Stats.ElementsLaidOut += end - root;
	// Only the quads of elements that moved or resized follow.
	for (uint32_t element = root; element < end; element++)
	{
		const UIBox& before = m_BoxScratch[element - root];
		const UIBox& after = layout.Boxes[element];
		if (before.Min != after.Min || before.Size != after.Size)
		{
			markQuads(element);
			layout.HitStamp = m_HitStamp + 1;
			// A mask's clip rect follows its box (and those of masks inside it follow it).
			if (!canvas.Masks.empty())
				layout.ClipsDirty = true;
		}
	}
}
roots.clear();
```

1. **Lines 124–129:** each mark climbs while the parent depends on its children, so the root is the highest ancestor whose box can change.
2. **Lines 132–136:** a root inside the subtree laid out before it is skipped.
3. **Lines 139–141:** the old boxes are saved, the subtree is laid out and the counter grows by its size.
4. **Lines 143–150:** only a box that moved or changed size marks quads and bumps the hit stamp.

An element depends on its children when it carries a :term[layout group]{id=layout-group} or when its rect fits its content: `DependsOnChildren`
in `GameUIScene.cpp` says exactly this. The climb finds the root of each mark, sorting and removing duplicates leaves each
root once, and a root inside a subtree already laid out is skipped. Before laying out, the code copies the old boxes into
a scratch array. Afterwards it compares each box with its old copy, marks quads only for boxes that moved or changed
size, and bumps the layout's hit stamp, which the [input page](../ui/input.md) reads to rebuild its grid.

### Layouts per size

A canvas measures its elements in :term[canvas units]{id=canvas-unit}, not in pixels. A screen of 1920 by 1080 pixels under the scale mode
that follows the screen, `ScaleWithScreen`, has a size in units. A screen of 3840 by 2160 has the same size, because the aspect matches.
`EnsureLayout` computes the unit size and asks `GetLayout` for the layout of that size.

```cpp src="Strata/src/Strata/GameUI/GameUIScene.cpp#L995-L1001" from="Layout& layout = GetLayout(canvas, unitSize, layoutIndex);" to="view.Canvas = canvas.Entity;" symbol="GameUIScene::EnsureLayout"
Layout& layout = GetLayout(canvas, unitSize, layoutIndex);
layout.LastUsed = m_LayoutStamp;
UpdateLayout(canvas, layout);
UpdateClips(canvas, layout);

UICanvasView& view = m_Views.emplace_back();
view.Canvas = canvas.Entity;
```

A canvas holds at most four **layouts (cached)**: each is the boxes, texts and marks computed for one size in canvas
units. `GetLayout` returns the one whose size matches, or makes a new one marked all dirty. At four layouts, it replaces
the one used least recently, judged by `LastUsed`. A window dragged between sizes of the same aspect therefore lays out
nothing, and only a new aspect pays a full layout. World-space canvases ignore the screen: their unit size is the
reference size.

Marks go to every layout of the canvas, so all four stay true. After the loop, the views are sorted by :term[sort order]{id=sort-order}, with a
:term[stable sort]{id=stable-sort} so that equal orders keep the hierarchy order. Layout is lazy: a canvas is laid out when a pass or the system
asks for a screen, not when its component changes.

## The check

A cache that is hard to see is hard to trust. **Validation** is a fresh, full calculation of what the scene caches,
compared with the cache itself. `Validate` checks three things for each canvas that is up to date. Every element's
activity, raycast flag and input field emptiness must agree with the scene. Every layout without pending marks must have
the boxes that a fresh `LayOutSubtree` computes, and the clip rects of the masks must follow the boxes.

```cpp src="Strata/src/Strata/GameUI/GameUIScene.cpp#L1426-L1438" from="for (Layout& layout : canvas.Layouts)" to="layout.UnitSize.x, layout.UnitSize.y));" symbol="GameUIScene::Validate"
for (Layout& layout : canvas.Layouts)
{
	if (!valid || layout.AllDirty || !layout.Dirty.empty())
		continue;
	std::vector<UIBox> boxes = layout.Boxes;
	LayOutSubtree(canvas, layout, 0, boxes);
	for (uint32_t index = 0; index < boxes.size() && valid; index++)
	{
		if (!SameBox(boxes[index], layout.Boxes[index], 1e-4f))
		{
			valid = fail(canvas.Elements[index].Entity, fmt::format("cached rect ({}, {}) {}x{}, recomputed ({}, {}) {}x{} (layout {}x{})",
				layout.Boxes[index].Min.x, layout.Boxes[index].Min.y, layout.Boxes[index].Size.x, layout.Boxes[index].Size.y, boxes[index].Min.x,
				boxes[index].Min.y, boxes[index].Size.x, boxes[index].Size.y, layout.UnitSize.x, layout.UnitSize.y));
```

1. **Lines 1428–1429:** a layout with pending marks is known to be stale and is skipped.
2. **Lines 1430–1431:** a copy of the boxes is laid out again from the root.
3. **Lines 1434–1438:** a box that differs by more than 0.0001 fails, with a message that names the entity.

Layouts with pending marks are skipped: they are known to be stale and will be brought up to date. What is left must
agree to within a tolerance of 0.0001. The failure message names the scene, the entity by name and its identifier, the
cached and the fresh rects, and asks whether a UI component was written without a signal. In Debug builds,
`EnsureLayout` ends with `Validate` and asserts on a failure, so a missing signal stops the developer at the frame that
shows it. In Release the check does not run: the same write leaves a stale box, and nothing says so.

`GameUISceneStats` counts the elements laid out, the texts shaped, the quads built and the full rebuilds since the last
`TakeStats`, which reads and clears them. A change that costs one element moves few counters, and an idle frame moves none.

:::example[Counting the work of a change]
In the test scene, the first frame lays out 10,001 elements: one full rebuild and 4,800 texts shaped. A second frame with
no change moves all four counters by zero.

Now one label's text changes. The rect has no fit, so no layout is marked: the counters read one text shaped, zero
elements laid out and eight quads built, one per character of "Changed!". A button made inactive costs more, because its
panel places children. The panel lays out again with its 12 buttons and 12 labels: 1 + 12 × 2 = 25 elements.

A window of 3840 by 2160 keeps the aspect and lays out zero elements. A screen of 1280 by 1024 is a new aspect and lays
out all 10,001, and the next frame at the old size lays out none, because both layouts stay.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Lay out every frame | Small libraries and many prototypes | No contract, no stale state | A cost per element per frame, wasted on an idle menu |
| Immediate mode | Dear ImGui, which the editor itself uses | No retained state to keep true | Widgets that are described again every frame, and no cache of boxes between frames |
| Poll component versions | Engines that stamp each component with a counter | A signal-free write that still works | A scan of every element each frame, and writers that must bump the counter anyway |
| Observe changes (Strata) | Retained libraries and engines with change events | Work proportional to the change | A rule for every writer, and a check to enforce it |

## How it is tested

The suite `GameUI.Dirty` of `StrataTests/src/GameUI/GameUILayoutTests.cpp` pins the contract. The idle test lays out a
scene of 10,001 elements, then runs a quiet frame and checks that all counters stay at zero. It then changes one label's
text and expects exactly one shaping and eight quads.

```cpp src="StrataTests/src/GameUI/GameUILayoutTests.cpp#L485-L512"
TEST_CASE("An idle frame lays out, shapes and builds nothing; a change costs its element")
{
	Scene scene("Widgets");
	const Tests::Perf::UIWidgets widgets = Tests::Perf::CreateUIWidgets(scene);
	GameUIScene& ui = GameUIScene::Get(scene);
	Frame(ui);
	GameUISceneStats stats = ui.TakeStats();
	CHECK(stats.ElementsLaidOut == 10'001);
	CHECK(stats.FullRebuilds == 1);
	CHECK(stats.TextsShaped == 4'800);
	CHECK(stats.QuadsBuilt > 4'800 + 5'200);

	Frame(ui);
	stats = ui.TakeStats();
	CHECK(stats.ElementsLaidOut == 0);
	CHECK(stats.TextsShaped == 0);
	CHECK(stats.QuadsBuilt == 0);
	CHECK(stats.FullRebuilds == 0);

	// A label's text: shaped again and its quads rewritten; its rect does not depend on its text, so nothing is laid out.
	Entity label = widgets.Labels[1234];
	label.GetComponent<UITextComponent>().Text = "Changed!";
	label.MarkModified<UITextComponent>();
	Frame(ui);
	stats = ui.TakeStats();
	CHECK(stats.TextsShaped == 1);
	CHECK(stats.ElementsLaidOut == 0);
	CHECK(stats.QuadsBuilt == 8);
```

1. **Lines 490–495:** the first frame lays out every element once, in one full rebuild.
2. **Lines 497–502:** the second frame changes nothing, and every counter stays at zero.
3. **Lines 505–512:** a text change with a signal shapes one text and builds eight quads, with no layout.

The test continues with a button's color, a moved leaf, an inactive button, a button moved to another panel and a screen
of another size, each with the counts of the example. Another test pins the case where the label and its button fit their
content: a text change then lays out the panel, 25 elements.

The failing case is the one the contract exists for.

```cpp src="StrataTests/src/GameUI/GameUILayoutTests.cpp#L575-L585"
TEST_CASE("A write without a signal makes validation fail, naming the entity")
{
	UITestScene ui;
	Entity box = ui.Add(ui.Canvas, "Unsignaled", PointRect({ 0.5f, 0.5f }, { 0.5f, 0.5f }, { 0.0f, 0.0f }, { 10.0f, 10.0f }));
	Frame(ui.GetUI());
	std::string error;
	CHECK(ui.GetUI().Validate(&error));
	box.GetComponent<UIRectComponent>().Size = { 20.0f, 10.0f }; // No MarkModified
	CHECK_FALSE(ui.GetUI().Validate(&error));
	CHECK(error.find("Unsignaled") != std::string::npos);
	CHECK(error.find(box.GetUUID().ToString()) != std::string::npos);
```

1. **Lines 581–583:** validation passes before the write and fails after the size changes without a signal.
2. **Lines 584–585:** the message names the entity by its name and by its identifier.

The test writes a rect's size without `MarkModified` and expects `Validate` to fail and to name the entity both by name
and by identifier. A further test moves plain entities and asserts that no quads are built and no element is laid out.
Run the suite directly with `build/windows/bin/Debug/StrataTests.exe --test-suite="GameUI.Dirty"`.

Four perf tests state the cost, at 10,000 elements. The metric `Layout10k` of the `Perf.GameUI` suite measures a full
layout at 0.41 ms against a budget of 0.61 ms. The metric `IdleFrame10k` measures an idle frame at 0.00027 ms against
0.000405 ms: the comparisons of rule 4. In the `PerfGPU.GameUI` suite, `Render10k` measures the UI pass at 0.10 ms
against 0.15 ms.

`RenderIdle10k` of the same suite checks that the UI pass of an idle frame uploads nothing; its budget is provisional,
with no measured value yet. The reference machine and the rule that budgets only go down are in the [performance
laboratory](../engineering/perf-lab.md).

## Changing it safely

A new UI component connects its signals in the constructor of `GameUIScene` and states what each costs: a layout, a quad
range, a reshape or a rebuild. Its test belongs in `GameUI.Dirty`. Build the scene in one frame, run an idle frame whose
counters are zero, make one change with the counters it should move, and write without a signal to see `Validate` reject
it. Extend `Validate` when the component caches a result that the existing checks do not compare.

Keep three habits. Write to a component and signal in the same function, or write through `ComponentAccess`. Never edit
the hierarchy components; call `SetParent`. And never make a handler walk elements: a handler marks, and the next update
works.

## Summary

- Every direct write to a UI component is signaled with `MarkModified` or `registry.patch`; `ComponentAccess`, the script
  API and the UI system already do, and `SetText` skips a text that did not change.
- The kind of change sets its cost: a rect marks layout and quads, an image marks quads, a text reshapes and lays out only
  when the rect fits its text.
- A canvas holds at most four layouts keyed by the size in canvas units, so a change of window size at the same aspect lays out nothing.
- `Validate` computes the layout again and compares it; Debug builds assert after every `EnsureLayout`, and Release
  builds do not check, so a write without a signal stays stale there.

## Check yourself

1. Engine code sets a button's `UIImage` color in place and does not signal. Which counter moves in the next
   frame in Release, and what happens in Debug?

   :::answer{tests="signal-rule validation"}
   In Release, no counter moves and the button keeps its old color: the quads were never marked. In Debug,
   `EnsureLayout` ends with `Validate`, but its checks compare activity, boxes and clip rects, and a color is none of
   them; the stale color stays unnoticed in both builds. The signal is the only protection, so write through
   `ComponentAccess` or call `MarkModified`.
   :::

2. A label's rect has `FitContent` set to `Width` and its parent is a layout group. The label's text changes. Which work
   follows?

   :::answer{tests="change-cost"}
   The text handler reshapes the text and marks quads, and since the rect fits its text, it marks the element for
   layout. The update climbs to the layout group, the highest ancestor whose rect depends on its children, and lays that
   subtree out again. Boxes that changed mark their quads.
   :::

3. The window changes from 1920 by 1080 pixels to 2560 by 1440 under a scale mode that follows the screen, with a
   reference of 1920 by 1080. How many elements are laid out?

   :::answer{tests="layout-cache"}
   Both screens have the aspect 16 to 9, so the size in canvas units is the same, 1920 by 1080, and the layout is
   found in the cache: zero elements are laid out. Only the scale, pixels per unit, changes, and the draw uses it.
   :::

4. Why does `Validate` skip layouts that still have pending marks?

   :::answer{tests="validation"}
   A layout with pending marks is known to be stale: the next update will bring it up to date. Comparing it would report
   an error that is not a missing signal. Only a layout that claims to be current is compared.
   :::

## Exercises

1. **Basic.** Run `GameUI.Dirty` and read the counters of the idle test. Predict the counters of one more step: a label
   moved by a tiny offset under a plain parent.

   :::answer[Worked solution]{tests="change-cost"}
   The rect handler marks layout and quads of the label. Its parent is a plain element, so the climb stops at the label,
   and one element is laid out. The box moved, so its quads are marked. The test checks the count of laid out elements:
   one.
   :::

2. **Medium.** Write a program that finds the re-layout roots of a set of marked elements in a small tree, given which
   elements depend on their children. Use a canvas, a panel, two buttons, a label and a plain sibling.

   :::answer[Worked solution]{tests="change-cost" solution="sketches/ui-contract-roots.cpp"}
   The climb follows parents while the parent depends on its children. Marks 4 and 3 reach the panel, element 1, and
   mark 5 stays where it is. Sorting and removing duplicates leaves the roots 1 and 5.

   ```cpp sketch="ui-contract-roots.cpp"
   // Finds the re-layout roots of a set of marked elements: each mark climbs to the highest ancestor that depends on its children.
   #include <algorithm>
   #include <cstdio>
   #include <vector>

   struct Element
   {
   	int Parent;
   	bool DependsOnChildren;
   };

   int FindRoot(const std::vector<Element>& elements, int marked)
   {
   	int root = marked;
   	while (elements[root].Parent >= 0 && elements[elements[root].Parent].DependsOnChildren)
   		root = elements[root].Parent;
   	return root;
   }

   int main()
   {
   	// 0 canvas, 1 panel (a layout group), 2 and 3 buttons (fit their text), 4 a label under 2, 5 a plain sibling of the panel.
   	const std::vector<Element> elements = { { -1, false }, { 0, true }, { 1, true }, { 1, true }, { 2, false }, { 0, false } };
   	const std::vector<int> marks = { 4, 3, 5 };

   	std::vector<int> roots;
   	for (const int marked : marks)
   		roots.push_back(FindRoot(elements, marked));
   	std::sort(roots.begin(), roots.end());
   	roots.erase(std::unique(roots.begin(), roots.end()), roots.end());

   	for (const int root : roots)
   		std::printf("root %d\n", root);
   	return 0;
   }
   ```

   ```text output-of="ui-contract-roots.cpp"
   root 1
   root 5
   ```

   1. **Lines 14–17:** the climb moves to the parent while the parent depends on its children.
   2. **Line 23:** the tree holds a canvas, a panel, two buttons, a label and a plain sibling.
   3. **Lines 26–30:** the roots are collected, sorted and made unique.

   The real code also skips a root inside the subtree of another root, by comparing with the end of the last subtree.
   :::

3. **Medium.** Trace a frame yourself: with a debugger attached, stop in `GameUISystem::OnUpdate` and in
   `GameUIRenderer::Prepare`, change one label, and write down which counters of `TakeStats` move.

   :::answer[Worked solution]{tests="change-cost validation"}
   The function that sets the label's text is `GameUISystem::SetText`, which patches the component and fires
   `OnTextChanged` in `Strata/src/Strata/GameUI/GameUIScene.cpp`. The next `EnsureLayout` calls `UpdateLayout`, which
   finds no marks, and the pass later builds the quads. The text counter moves by one; elements laid out stay zero when the
   rect fits no content.
   :::

4. **Hard.** Break the contract on purpose in a test: write a `UIRect` field without `MarkModified`, call `Validate` and
   read the message. Then call `EnsureLayout` in a Debug build.

   :::answer[Worked solution]{tests="signal-rule validation"}
   Create a scene with a canvas and one element, run a frame, change `Size` in place and call `Validate` with a string
   pointer. It returns false, and the message names the scene, the entity and both rects. In a Debug build, the next
   `EnsureLayout` ends with the same check and asserts with the same message; in Release nothing is checked.
   The test `A write without a signal makes validation fail, naming the entity` does exactly this.
   :::

## Where it lives in Strata

- `Strata/src/Strata/GameUI/GameUIScene.h` and `GameUIScene.cpp`: `GameUIScene`, its signals, `ProcessChanges`,
  `EnsureLayout`, `GetLayout`, `DependsOnChildren`, `Validate`, `TakeStats`, `GameUISceneStats`,
  `c_MaxLayoutsPerCanvas`.
- `Strata/src/Strata/GameUI/GameUILayout.cpp`: `UpdateLayout`, `LayOutSubtree`.
- `Strata/src/Strata/GameUI/GameUIComponents.h`: the statement of the contract.
- `Strata/src/Strata/Scene/ComponentAccess.cpp`: `SetProperty`, which signals.
- `Strata/src/Strata/GameUI/GameUISystem.cpp`: `GameUISystem::SetText`.
- `StrataTests/src/GameUI/GameUILayoutTests.cpp`: the suite `GameUI.Dirty`.
- `StrataTests/src/Perf/GameUIPerfTests.cpp`: the perf tests of 10,000 elements.

## Further reading

- [Game Programming Patterns, "Dirty Flag"](https://gameprogrammingpatterns.com/dirty-flag.html): the pattern the scene
  applies, with its costs; beginner.
- [Game Programming Patterns, "Observer"](https://gameprogrammingpatterns.com/observer.html): the idea behind signals;
  beginner.
- [Dear ImGui FAQ](https://github.com/ocornut/imgui/blob/master/docs/FAQ.md): immediate mode compared with retained
  mode; intermediate.
