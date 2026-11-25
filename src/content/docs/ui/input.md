---
id: ui/input
title: "UI input"
description: "How Strata finds what the pointer is over, decides who owns a click, moves the focus and turns presses into events for scripts."
kind: internals
size: XL
tracks: [E]
needs: [ui/layout, input/actions, input/mouse-cursor, scripting/script-system, basics/math-geometry]
time: 125
learn:
  - id: trace-click
    text: trace one click from the pointer to a script's OnUIClick
  - id: hit-test
    text: explain which element a press reaches and why the elements under it do not
  - id: gestures
    text: predict whether the UI or the game owns a press and its release
  - id: navigation
    text: compute where a direction press moves the focus
  - id: events
    text: explain why values set by code raise no events and how events reach scripts
since: 0.4.0
status: final
---

A game menu must answer one question many times a second: what did the player do to the interface a moment ago? The answer has parts. The engine finds which element lies under the pointer and decides whether the press belongs to the menu or to the game. It keeps track of the focus for keyboards and gamepads. It turns presses into widget events and hands the events to scripts.

In Strata all of this happens in one :term[scene system]{id=scene-system}, the user interface (UI) system, on :term[unscaled time]{id=unscaled-time} and before the scripts run. It does not draw anything (that is the :term[renderer's]{id=renderer} job) and it does not edit text in an input field (that is the job of [Text and text fields](../ui/text.md)).

This page follows the system's update in order. It explains the problem and the usual solutions and shows a toy that does the core job. Then it reads the real code on one concrete screen: the main menu of the Third-Person sample. At the end you can say, for any click, which element gets it and why the game does not. You can also follow a gamepad press all the way to a script's `OnUIClick`.

## The problem and how engines solve it

Think of a main menu with a panel, three buttons and a label on each button. The player moves the mouse and clicks at pixel (560, 320). Several elements cover that pixel: the panel behind, a button, the button's icon, and maybe a label, but the player means one of them. The program that answers is a **hit test**: it takes a point and returns the element the player sees there. Every interface library needs one, and the first design choice is how it searches.

The plain method is a linear scan: test every element, remember the last drawn one that contains the point. It is correct and short. Its cost grows with the number of elements, and it runs at least once per frame, because hover must follow a moving mouse. A menu with forty elements does not notice. A game that shows an inventory of two thousand slots, or an editor with long lists, does.

The second method is a **uniform grid**: cut the screen into equal cells, record in each cell the elements that overlap it, and for a point test only the elements of its cell. The cost per query depends on how many elements share a cell, not on how many exist. The price is memory, and a rebuild when elements move.

The third method is a tree, such as a quadtree or a hierarchy of :term[bounding boxes]{id=bounding-box}. Trees adapt to uneven layouts, where a grid wastes cells on empty areas, but they cost more to build and to walk. Strata uses the grid, because interface rects are spread over a canvas fairly evenly and rebuilds are rare.

The second problem is routing: after the hit test, who hears about the click? Browsers use bubbling: the event goes to the innermost element and then up through its parents, and any of them may handle it or stop it. Unity's event system asks a list of ray sources, such as one per canvas and one per camera, sorts their answers and sends the event to the best one. Both designs let a click on a button's icon count as a click on the button. Strata does this with a walk up from the element hit to its nearest selectable, described below, and then queues one event per widget.

The third problem is keys and gamepads, for a television has no mouse and a player may sit on a couch with a controller. The interface must show one element as active, the focus, and move it when a direction is pressed. Deciding where the focus goes is **spatial navigation**: from the focused element, find the element that lies in the pressed direction. Designers can wire the neighbours by hand, which is exact and tedious, or the engine can compute them from the layout, which is automatic and sometimes surprising. Strata offers both, per element.

:::note
Web pages, Unity and Godot all handle these three problems in some form. The names differ, so the further reading names a source for each. This page only describes what Strata does.
:::

## The map: one update, in order

The "UI" system is registered to run before the "Scripting" system. The order is soft: it applies only when a "Scripting" system exists, so a game without the script module still has a UI. The reason for the order is that a script's `OnUpdate` then sees this frame's events, and it sees the pointer already captured by a menu. The system's update has nine steps.

```mermaid caption="The nine steps of the UI system's update, from the input actions to the dispatch of events. Scripts run after the last step." alt="A flow chart of nine boxes in a column: actions, layout for the input screen, hit grids, drop a focus that cannot be used, pointer, editing, navigation, visual states, dispatch. An arrow leaves the last box towards the scripts."
flowchart TD
  A1["1. UI actions follow the input"] --> A2["2. Layout for the input screen"]
  A2 --> A3["3. Hit grids rebuilt if needed"]
  A3 --> A4["4. Drop a focus that cannot be used"]
  A4 --> A5["5. Pointer: hover, gestures, clicks, drags"]
  A5 --> A6["6. Editing an input field"]
  A6 --> A7["7. Navigation: directions, Submit, Cancel"]
  A7 --> A8["8. Visual states and their fades"]
  A8 --> A9["9. Dispatch the queued events"]
  A9 --> A10["Scripts run: OnUpdate sees the events"]
```

Each step has a reason for its place.

1. The actions come first because everything after reads them. The UI map has the actions `UI/Submit`, `UI/Cancel` and four directions, and their :term[key repeat]{id=key-repeat} is the subject of [Input actions](../input/actions.md). The system updates them even when no canvas exists, a detail the last section explains.
2. The layout is computed for the game's **input screen**: the window's size in rendered pixels, with the :term[content scale]{id=content-scale} of the display. Hit tests need the same rects that the renderer will draw.
3. The hit grids are rebuilt only for canvases whose layout or hit stamp changed (the stamps are the subject of the UI contract page).
4. A focus that can no longer be used is dropped: the element was disabled, hidden or destroyed since the last update.
5. The pointer step finds the hover, starts and ends gestures, presses, clicks and drags a slider.
6. Editing an input field comes next and belongs to [Text and text fields](../ui/text.md).
7. Navigation turns the direction actions, Submit and Cancel into focus changes and clicks.
8. Visual states are computed last among the state changes, so that they show this update's hover, press and focus.
9. Dispatch sends every event queued so far to the listeners, in the order the inputs happened.

A **selectable** is an element with a `UISelectableComponent`: it can be hovered, pressed, focused and disabled, and it holds the colors or images of those states. A button, a toggle, a slider and an input field are selectables with more data next to them. When a scene has no canvas, the system does one cheap check of the canvas storage, releases any capture it held, and returns after the actions are updated.

## The contract

The system has rules that callers and writers of widgets keep. Each has a reason, and most of them exist because a past bug or a surprising result showed the need.

:::rule
The engine's developer guide gives the UI its own scene system for input. Widgets write their values with `registry.patch` and report through `IUIEvents`, and elements in the world are hit through the camera's ray. The aim is that no second system grows its own pointer handling. See [Layout](../ui/layout.md) for the elements these rules act on.
:::

1. **Only this system reads the pointer for the UI and sets capture.** If two places set the :term[pointer capture]{id=pointer-capture}, the last writer wins and a click could reach both menu and game. One owner makes the state simple to reason about.
2. **Hit tests use the game's input screen, in rendered pixels.** On a display with a content scale, or a Game view with a fixed resolution, the window's logical size differs from what is drawn. A hit test against the wrong size misses what the player sees.
3. **Code that asks where an element is shown uses the visible box.** The visible box is the rect after the masks above the element have cut it. What a mask hides is never clicked, and tests, the `input.click` command and the editor's picking then agree with the player.
4. **Widgets write with `registry.patch` and make no undo step.** Play mode runs on a copy of the scene, and a player's click is no edit. `registry.patch` also signals the change, so caches that follow the component stay right.
5. **Values set by code raise no events.** When a script sets a slider's value, no `OnUIValueChanged` follows. Otherwise a script that mirrors a slider into a setting and a slider that mirrors a setting would call each other forever.
6. **Navigation reads the UI map, not raw keys.** Players rebind keys, and the qualified action names keep a game's own `Left` action apart from the UI's `UI/Left`.
7. **The system runs before the scripts.** Scripts then see this frame's events and a pointer that menus have already captured, so a button click does not also fire the gun.
8. **The UI runs on unscaled time.** A pause menu that sets the :term[time scale]{id=time-scale} to 0 must still fade its buttons, repeat held keys and blink a caret.
9. **Disabled selectables still block.** A disabled button is drawn and hit like any element, so a click on it does not fall through to what lies below.
10. **Images are raycast targets by default and texts are not.** A label must not take the click of the button below it, and a panel must block the game.
11. **For a world-space canvas, intersect the ray; never divide pixels by a scale.** Perspective has no single scale for a plane that is seen at an angle.

Two terms appear in these rules. A **gesture** is one press of the pointer from its first button down to the moment every button is up; the UI system decides at the start who owns it.

An **event target** is a second entity that receives a widget's events, for example one script on a menu root that handles every button.

## A toy version

The toy below holds the core of the pointer step in one short program. It keeps a list of rects in draw order. A **half-open rect** includes the points of its minimum edges and excludes the points of its maximum edges, so two rects that touch never both contain the shared edge. The hit test walks the list from the end. The toy also keeps a gesture and a pressed element, and reports a click on release only when the press and the release hit the same button.

```cpp sketch="ui-input-toy.cpp"
// A toy of the UI's pointer input: rects in draw order, a hit test from the last drawn, and a gesture.
#include <glm/glm.hpp>

#include <cstdio>
#include <optional>
#include <string>
#include <vector>

struct Rect
{
	std::string Name;
	glm::vec2 Min;
	glm::vec2 Size;
	bool Button;
};

// Half-open: the minimum edges are inside, the maximum edges are not.
static bool Contains(const Rect& rect, glm::vec2 point)
{
	return point.x >= rect.Min.x && point.y >= rect.Min.y && point.x < rect.Min.x + rect.Size.x && point.y < rect.Min.y + rect.Size.y;
}

// The rects are in draw order, so the last one that contains the point is on top.
static std::optional<size_t> HitTest(const std::vector<Rect>& rects, glm::vec2 point)
{
	for (size_t index = rects.size(); index-- > 0;)
	{
		if (Contains(rects[index], point))
			return index;
	}
	return std::nullopt;
}

enum class Gesture { None, UI, Game };

class ToyUI
{
public:
	explicit ToyUI(std::vector<Rect> rects)
		: m_Rects(std::move(rects))
	{
	}

	void Update(glm::vec2 position, bool down)
	{
		const std::optional<size_t> hit = HitTest(m_Rects, position);
		const bool pressed = down && !m_WasDown;
		const bool released = !down && m_WasDown;
		if (pressed && m_Gesture == Gesture::None)
		{
			m_Gesture = hit ? Gesture::UI : Gesture::Game;
			m_Pressed = hit && m_Rects[*hit].Button ? hit : std::nullopt;
		}
		if (released && m_Pressed && m_Pressed == hit)
			std::printf("  click on %s\n", m_Rects[*hit].Name.c_str());
		if (released)
			m_Pressed.reset();
		// The game hides its mouse buttons during a UI gesture, and while the pointer is over the UI between gestures.
		const bool hidden = m_Gesture == Gesture::UI || (m_Gesture == Gesture::None && hit);
		std::printf("(%3.0f,%3.0f) down=%d hit=%-6s game sees the button: %s\n", position.x, position.y, down ? 1 : 0,
			hit ? m_Rects[*hit].Name.c_str() : "none", hidden ? "no" : "yes");
		if (!down)
			m_Gesture = Gesture::None;
		m_WasDown = down;
	}

private:
	std::vector<Rect> m_Rects;
	std::optional<size_t> m_Pressed;
	Gesture m_Gesture = Gesture::None;
	bool m_WasDown = false;
};

int main()
{
	ToyUI ui({ { "Panel", { 0.0f, 0.0f }, { 200.0f, 100.0f }, false }, { "Button", { 20.0f, 20.0f }, { 60.0f, 30.0f }, true } });
	std::printf("Press the button, drag onto the panel, release:\n");
	ui.Update({ 30.0f, 30.0f }, false);
	ui.Update({ 30.0f, 30.0f }, true);
	ui.Update({ 150.0f, 80.0f }, true);
	ui.Update({ 150.0f, 80.0f }, false);
	std::printf("Press and release on the button:\n");
	ui.Update({ 30.0f, 30.0f }, true);
	ui.Update({ 30.0f, 30.0f }, false);
	std::printf("Press in the game, drag over the button, release:\n");
	ui.Update({ 300.0f, 300.0f }, true);
	ui.Update({ 30.0f, 30.0f }, true);
	ui.Update({ 30.0f, 30.0f }, false);
	return 0;
}
```

```text output-of="ui-input-toy.cpp"
Press the button, drag onto the panel, release:
( 30, 30) down=0 hit=Button game sees the button: no
( 30, 30) down=1 hit=Button game sees the button: no
(150, 80) down=1 hit=Panel  game sees the button: no
(150, 80) down=0 hit=Panel  game sees the button: no
Press and release on the button:
( 30, 30) down=1 hit=Button game sees the button: no
  click on Button
( 30, 30) down=0 hit=Button game sees the button: no
Press in the game, drag over the button, release:
(300,300) down=1 hit=none   game sees the button: yes
( 30, 30) down=1 hit=Button game sees the button: yes
( 30, 30) down=0 hit=Button game sees the button: yes
```

1. **Line 20:** the comparison is half-open: the minimum edge is inside and the maximum edge is outside.
2. **Lines 26–29:** the loop runs from the last rect to the first, so the rect drawn last wins.
3. **Lines 49–52:** only a press with no gesture running chooses the owner, and the pressed element is remembered.
4. **Lines 54–55:** a click needs a release over the element that was pressed.
5. **Lines 58–59:** the game's buttons are hidden during a UI gesture and while the pointer is over the UI between gestures.

Read the output in three parts. In the first run the press starts on the button, so the gesture is the UI's, and the pointer is dragged onto the panel. The panel is a hit, but the pressed element is the button, so the release over the panel produces no click. In the second run the press and the release are on the button, and one click appears.

In the third run the press starts outside every rect. The gesture is the game's, and it stays the game's while the pointer crosses the button: the game keeps seeing its button until every button is up.

The toy omits the grid, masks, canvases with :term[sort orders]{id=sort-order}, world-space canvases, focus, widgets other than buttons and the queue of events. The real code has all of these. The rest of the page adds them in the order of the update.

## The real code

The examples use the main menu of the Third-Person sample: a canvas with a panel, a column of buttons (Play, Settings, Credits, Quit) and a credits panel that opens beside it. Each button has an image, a `UISelectableComponent` and a `UIButtonComponent`, and a text child as its label. A script, `MainMenu`, is attached to one entity and is the event target of every button.

### What the pointer can hit

Not every element takes part in hit tests. A **raycast target** is an element that blocks and receives the pointer. An image is one by default, a text is not, and every selectable is one whatever its image says. The contract gives the reason: a label on a button must not take the click, because the button should get it, and a panel must stop the click from reaching the game.

When a hit test builds its list for a canvas, it keeps only visible raycast targets, and it stores for each one the visible box, the rect left after masks cut it. An element whose visible box has no area, because a mask hides it, is dropped from the list.

Look at how a canvas's list becomes a grid. The first quote is the start of `Build`: it collects the targets in draw order, then picks the size of the grid. The number of cells per axis is the square root of the target count divided by two, rounded up, and at most 64. So the grid has about two targets per cell where they spread evenly.

```cpp src="Strata/src/Strata/GameUI/GameUIHitTest.cpp#L56-L73"
grid.Targets.clear();
const uint32_t count = ui.GetElementCount(view);
for (uint32_t element = 0; element < count; element++)
{
	if (!ui.IsElementVisible(view, element) || !ui.IsRaycastTarget(view, element))
		continue;
	// What the masks above it leave of it: the pointer hits only what is drawn.
	const UIBox box = ui.GetVisibleBox(view, element);
	if (box.Size.x > 0.0f && box.Size.y > 0.0f)
		grid.Targets.push_back(Target { element, ui.GetElementEntity(view, element), box });
}

// Cells over the canvas's size in units, about c_TargetsPerCell targets each where they are spread evenly.
const glm::vec2 extent = glm::max(view.UnitSize, glm::vec2(1.0f));
const float cellsPerAxis = std::ceil(std::sqrt(static_cast<float>(grid.Targets.size()) / c_TargetsPerCell));
const uint32_t cells = std::clamp(static_cast<uint32_t>(cellsPerAxis), 1u, c_MaxCellsPerAxis);
grid.Cells = glm::uvec2(cells);
grid.CellSize = extent / glm::vec2(grid.Cells);
```

1. **Line 60:** an invisible element or one that is no raycast target never enters the list.
2. **Line 63:** the box is the visible box, so a masked-out part cannot be hit.
3. **Lines 69–71:** the grid is `cells` by `cells`, with `cells` from the target count, clamped between 1 and 64.
4. **Line 73:** each cell is the canvas's size in units divided by the cell count, so cells are not always square.

The second half sorts targets into cells with a counting sort. A counting sort is used when you know the number of buckets: count how many items go into each bucket, turn the counts into start positions by adding them up, then place each item. This builds one flat array and an array of starts, with no per-cell allocation.

```cpp src="Strata/src/Strata/GameUI/GameUIHitTest.cpp#L76-L99"
auto cellRange = [&](const UIBox& box, glm::uvec2& outMin, glm::uvec2& outMax)
{
	const glm::vec2 min = glm::floor(box.Min / grid.CellSize);
	const glm::vec2 max = glm::floor((box.GetMax() - glm::vec2(1e-4f)) / grid.CellSize);
	const glm::vec2 last = glm::vec2(grid.Cells) - 1.0f;
	outMin = glm::uvec2(glm::clamp(min, glm::vec2(0.0f), last));
	outMax = glm::uvec2(glm::clamp(max, glm::vec2(0.0f), last));
};
const uint32_t cellCount = grid.Cells.x * grid.Cells.y;
grid.CellStarts.assign(cellCount + 1, 0);
for (const Target& target : grid.Targets)
{
	glm::uvec2 min;
	glm::uvec2 max;
	cellRange(target.Box, min, max);
	for (uint32_t y = min.y; y <= max.y; y++)
	{
		for (uint32_t x = min.x; x <= max.x; x++)
			grid.CellStarts[y * grid.Cells.x + x + 1]++;
	}
}
for (uint32_t cell = 0; cell < cellCount; cell++)
	grid.CellStarts[cell + 1] += grid.CellStarts[cell];
grid.CellTargets.assign(grid.CellStarts[cellCount], 0);
```

1. **Lines 78–79:** the cell range of a rect. The maximum edge is shifted back by a tiny amount, so a rect that ends exactly on a cell border does not enter the next cell.
2. **Lines 81–82:** a rect that reaches beyond the canvas is put in the border cells.
3. **Lines 86–95:** the first pass counts, for every cell, how many rects overlap it.
4. **Lines 97–99:** the running sum turns counts into start positions and sizes the flat array of target indexes.

The next pass, which the quote omits, repeats the loop and writes each target's index into the next free slot of each cell. Because targets are visited in draw order, every cell holds its targets in draw order too. That is the property the query uses.

:::example[A grid for the main menu]
Take a canvas of 1280 by 720 units with four elements in draw order. The panel starts at (0, 0) and has size 1280 by 720. The Play button starts at (540, 300) with size 200 by 60. The Play icon is a child of the button, starts at (550, 310) and has size 40 by 40; the sample's buttons have no icon, so this example adds one to show the walk up. The fourth element is the label text of the button.

The label is no raycast target, so three targets remain. The grid has $\lceil\sqrt{3/2}\rceil = 2$ cells per axis, so each cell is 640 by 360 units.

The panel overlaps all four cells. The button's x range is 540 up to, not including, 740, so it reaches cells 0 and 1 across; its y range 300 to 360 stays in row 0. The icon (x 550 to 590, y 310 to 350) lies in cell (0, 0) only. The counts are 3, 2, 1 and 1, the starts are 0, 3, 5, 6, 7, and the flat array holds seven entries.

Now the pointer is at pixel (560, 320). It falls in cell (0, 0), whose list is panel, button, icon. The query reads from the end: the icon contains the point (550 ≤ 560 < 590 and 310 ≤ 320 < 350), so the icon is the hit after one comparison. At (740, 330) the cell is (1, 0). The button's range ends before 740, because the rect is half-open, so the button does not contain that point and the panel is the hit.
:::

Here is the query itself, one cell and one backward loop.

```cpp src="Strata/src/Strata/GameUI/GameUIHitTest.cpp#L114-L129"
std::optional<UIHitResult> GameUIHitTester::HitTestGrid(uint32_t viewIndex, const glm::vec2& point) const
{
	const CanvasGrid& grid = m_Grids[viewIndex];
	// Points beyond the canvas fall in its border cells, which hold the rects that reach out of it.
	const glm::uvec2 cellPosition = glm::uvec2(glm::clamp(glm::floor(point / grid.CellSize), glm::vec2(0.0f), glm::vec2(grid.Cells) - 1.0f));
	const uint32_t cell = cellPosition.y * grid.Cells.x + cellPosition.x;
	// The last drawn first: the cell's targets are in draw order.
	for (uint32_t index = grid.CellStarts[cell + 1]; index-- > grid.CellStarts[cell];)
	{
		m_LastCandidates++;
		const Target& target = grid.Targets[grid.CellTargets[index]];
		if (target.Box.Contains(point))
			return UIHitResult { target.Entity, viewIndex, target.Element };
	}
	return std::nullopt;
}
```

1. **Line 118:** the point's cell, clamped so a point outside the canvas falls in the border cells.
2. **Line 121:** the loop runs from the last entry to the first of the cell: the last drawn is tried first.
3. **Line 123:** a counter of candidates, which the tests and perf checks read.
4. **Line 125:** the test is `Contains`, half-open, on the visible box.

A test in `GameUI.HitTest` checks that a query compares at most 64 candidates among 10,000 elements, and that it finds what a full search finds. The grid is rebuilt only when the canvas's layout id or hit stamp changes, which the UI contract page explains.

A scene has more than one canvas, and `HitTest` combines them.

```cpp src="Strata/src/Strata/GameUI/GameUIHitTest.cpp#L145-L169"
std::optional<UIHitResult> GameUIHitTester::HitTest(const glm::vec2& pixel, bool anyCanvas, const UIPointerRay* ray) const
{
	m_LastCandidates = 0;
	// From the topmost screen-space canvas down.
	for (size_t viewIndex = m_Grids.size(); viewIndex-- > 0;)
	{
		const CanvasGrid& grid = m_Grids[viewIndex];
		if (grid.WorldSpace || (!grid.ReceivesInput && !anyCanvas) || grid.Targets.empty())
			continue;
		if (const std::optional<UIHitResult> hit = HitTestGrid(static_cast<uint32_t>(viewIndex), pixel / grid.Scale))
			return hit;
	}
	// Then the canvases in the scene, the nearest first.
	if (!ray)
		return std::nullopt;
	FindWorldCrossings(*ray, anyCanvas);
	for (const WorldCrossing& crossing : m_Crossings)
	{
		if (m_Grids[crossing.View].Targets.empty())
			continue;
		if (const std::optional<UIHitResult> hit = HitTestGrid(crossing.View, crossing.Point))
			return hit;
	}
	return std::nullopt;
}
```

1. **Line 149:** the canvases are sorted by their sort order, higher drawn later; the loop starts from the topmost.
2. **Line 152:** world-space canvases, canvases that receive no input and empty ones are skipped here.
3. **Line 154:** the pixel is divided by the canvas's scale to get :term[canvas units]{id=canvas-unit}, and the first canvas with a hit wins.
4. **Lines 158–160:** screen-space canvases come first; only then does the code look at canvases in the scene, if a ray was given.

The result is an element, the one drawn. It is not always the element that gets pressed. `FindSelectable` starts at the element and walks up the hierarchy to its nearest ancestor that has a `UISelectableComponent`, and stops at the canvas.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L330-L343"
entt::entity GameUISystem::FindSelectable(entt::entity element) const
{
	const entt::registry& registry = m_Scene.GetRegistry();
	for (entt::entity current = element; current != entt::null && registry.valid(current);)
	{
		if (registry.all_of<UISelectableComponent>(current))
			return current;
		if (registry.all_of<UICanvasComponent>(current))
			break; // Not beyond the canvas
		const HierarchyComponent* hierarchy = registry.try_get<HierarchyComponent>(current);
		current = hierarchy ? hierarchy->Parent : entt::null;
	}
	return entt::null;
}
```

1. **Lines 333–336:** the element itself is tried first, then each parent: the icon finds the button.
2. **Lines 337–338:** the walk never leaves the canvas, so an element of one canvas can never press a widget of another.
3. **Lines 339–340:** the parent comes from the hierarchy component; a root has none and the walk ends with no selectable.

Tools see the same two answers. The editor command `ui.hitTest` runs this very `HitTest` with the ray of the game camera, and reports the element hit and the selectable a click would press. With `all` it calls `HitTestAll`, which lists every visible element whose box contains the point, topmost first, raycast target or not. In the example above, `ui.hitTest` at (560, 320) reports the icon as the entity and the Play button as the selectable.

Two mistakes follow from these rules. A designer who masks a list and clicks on a row that is scrolled out of the mask finds that nothing happens. That is correct, because the hit test uses the visible box. A text made a raycast target by hand still presses its own button, since the walk up finds the button, but a label that covers another widget hides that widget.

### Canvases in the world

A world-space canvas is a plane in the 3D scene, such as a sign or a screen. The pointer is a pixel, so the engine needs the point where the line of sight through that pixel meets the plane. First it builds a ray from the game's :term[primary camera]{id=primary-camera}. Then it finds where the ray meets the plane of each canvas. Last it asks the canvas's grid about the crossing point in the canvas's own units.

Building the ray means undoing the camera's projection. Strata uses :term[reversed-Z]{id=reversed-z} depth: a depth of 1 is the :term[near plane]{id=near-plane}, 0 is far. The pixel becomes :term[normalized device coordinates]{id=normalized-device-coordinates} (NDC), $x_{ndc}$ and $y_{ndc}$, with +Y up. The code turns two points back to :term[world space]{id=world-space} with the inverse of the view-projection matrix: one at depth 1, the near point, and one at depth 0.5. The second point is taken at depth 0.5 instead of 0, because with an :term[infinite far plane]{id=infinite-far-plane} the point at depth 0 has no finite position.

The ray runs from the first point towards the second, with unit length.

```cpp src="Strata/src/Strata/GameUI/GameUIHitTest.cpp#L208-L226"
std::optional<UIPointerRay> MakeRay(const glm::mat4& viewProjection, const glm::vec2& screenSize, const glm::vec2& pixel)
{
	if (!(screenSize.x > 0.0f && screenSize.y > 0.0f))
		return std::nullopt;
	// Pixel centers to normalized device coordinates (+Y up); reversed-Z: depth 1 is near, 0 far.
	const glm::vec2 ndc((pixel.x / screenSize.x) * 2.0f - 1.0f, 1.0f - (pixel.y / screenSize.y) * 2.0f);
	const glm::mat4 inverse = glm::inverse(viewProjection);
	glm::vec4 nearPoint = inverse * glm::vec4(ndc, 1.0f, 1.0f);
	glm::vec4 farPoint = inverse * glm::vec4(ndc, 0.5f, 1.0f); // Halfway: finite also for infinite far planes
	if (!(std::abs(nearPoint.w) > 1e-12f) || !(std::abs(farPoint.w) > 1e-12f))
		return std::nullopt;
	const glm::vec3 from = glm::vec3(nearPoint) / nearPoint.w;
	const glm::vec3 to = glm::vec3(farPoint) / farPoint.w;
	const glm::vec3 direction = to - from;
	const float length = glm::length(direction);
	if (!(length > 1e-12f) || !std::isfinite(length))
		return std::nullopt;
	return UIPointerRay { from, direction / length };
}
```

1. **Line 213:** pixel to normalized device coordinates: $x$ from 0 to the width maps to −1 to 1, and $y$ is flipped because the pixel row grows downward.
2. **Lines 215–216:** the near point at depth 1 and the halfway point at depth 0.5, both multiplied by the :term[inverse matrix]{id=inverse-matrix}.
3. **Lines 219–221:** the homogeneous divide by `w` gives world positions; their difference is the direction.
4. **Lines 223–225:** a degenerate or infinite direction returns no ray; otherwise the direction has unit length.

The second step meets the canvas plane. In the canvas's own space the plane is $z = 0$, with $x$ and $y$ in canvas units. The code transforms the ray into that space with the inverse of the canvas's matrix, finds the parameter $t$ where the ray's $z$ reaches 0, and reads the point there.

```cpp src="Strata/src/Strata/GameUI/GameUIHitTest.cpp#L228-L243"
std::optional<std::pair<glm::vec2, float>> IntersectCanvas(const glm::mat4& canvasToWorld, const UIPointerRay& ray)
{
	// In the canvas's own space the plane is z = 0, x and y its units.
	const glm::mat4 worldToCanvas = glm::inverse(canvasToWorld);
	const glm::vec3 origin = glm::vec3(worldToCanvas * glm::vec4(ray.Origin, 1.0f));
	const glm::vec3 direction = glm::vec3(worldToCanvas * glm::vec4(ray.Direction, 0.0f));
	if (!(std::abs(direction.z) > 1e-12f) || !std::isfinite(origin.z))
		return std::nullopt;
	const float t = -origin.z / direction.z;
	if (!(t >= 0.0f))
		return std::nullopt;
	const glm::vec3 point = origin + direction * t;
	// The distance along the world ray (direction keeps its length through the inverse's scale).
	const float distance = glm::length(glm::vec3(canvasToWorld * glm::vec4(point, 1.0f)) - ray.Origin);
	return std::pair<glm::vec2, float>(glm::vec2(point), distance);
}
```

1. **Lines 231–233:** the origin is moved with `w` of 1 (a point) and the direction with `w` of 0 (a vector, so no translation).
2. **Lines 236–237:** $t = -z_{origin} / z_{direction}$; a crossing behind the ray's start is rejected.
3. **Line 241:** the distance is measured in the world, back from the crossing point, so canvases can be sorted by how far they are.

:::example[A ray through a pixel]
The screen is 1280 by 720 pixels and the pointer is at pixel (960, 180). Then $x_{ndc} = 960/1280 \cdot 2 - 1 = 0.5$ and $y_{ndc} = 1 - 180/720 \cdot 2 = 0.5$. Say the camera stands at (0, 0, 4) and the matrices give the world direction (0.25, 0.125, −1), which has length about 1.038 and unit form (0.241, 0.120, −0.963).

The canvas is a plane through the world origin facing the camera, scaled by 0.01: one canvas unit is 0.01 world units. In canvas space the origin becomes (0, 0, 400) and the direction (24.1, 12.0, −96.3). The ray's $z$ reaches 0 at $t = 400 / 96.3 \approx 4.15$, and the point is $(100, 50)$ in canvas units. In the world the point is (1, 0.5, 0), and its distance from the camera is $\sqrt{1 + 0.25 + 16} \approx 4.15$ units. The grid of that canvas is then asked about (100, 50), and a button there gets the hover.

The example keeps the canvas's matrix a plain scale. A real canvas's matrix also flips y, because canvas units grow downward, and starts at the canvas's :term[pivot]{id=pivot-ui} point: there the crossing lies 100 units right of the pivot and 50 units above it.
:::

The step back, from a canvas point to a pixel, is `ProjectCanvasPoint`: it multiplies by the canvas matrix and the view-projection, divides by `w` and maps the result to pixels.

When a world canvas and a screen canvas both cover the pointer, the screen canvas wins, because it is always in front of the scene. Among world canvases the nearest crossing wins. One limit matters for designers: the game does not test for scene geometry between the camera and the canvas, so a wall in front of a sign does not stop a click on it. The editor's picks do check geometry. This is a known gap in the game, noted in the release notes.

### Who owns a press

The pointer step answers a harder question than a hit test: when the player presses a button, does the menu get it, or the game? A bad answer gives the classic bug where a click on Play also fires the gun. Strata solves it with gestures, and with the pointer capture that the input module offers.

Look at the hover first. Hover is found again only when something that changes it changed. That means the pointer moved, the layout changed, or a button was pressed or released. It also means a canvas stands in the scene, since the camera may move every frame.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L272-L279"
if (moved || layoutChanged || pointer.Pressed != 0 || pointer.Released != 0 || worldCanvases)
{
	const std::optional<UIHitResult> hit = m_HitTester.HitTest(pixel, false, m_PointerRay ? &*m_PointerRay : nullptr);
	m_HoveredTarget = hit ? hit->Entity : entt::null;
	m_PointerOverUI = hit.has_value();
	const entt::entity selectable = hit ? FindSelectable(hit->Entity) : entt::null;
	m_Hovered = selectable != entt::null && IsInteractable(selectable) ? selectable : entt::null;
}
```

Hover stores two things. `m_HoveredTarget` is the element hit. `m_Hovered` is the selectable found by `FindSelectable`, and only when its `Interactable` field is true. A disabled button is hit, so it blocks, but it is never hovered.

Now the press. A press that starts over the UI belongs to the UI until every button is up. A press that starts elsewhere belongs to the game until every button is up. The gesture is decided once, at the first press.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L281-L311"
constexpr uint32_t c_Left = 1u << Mouse::ButtonLeft;
// A left press a binding capture took (a rebinding menu's "press a control") is the binding: it presses no widget, as
// it moves no action, which would start the capture again with the menu's button still under the pointer.
const std::optional<InputControl>& captured = InputActions::GetCapturedControl();
const bool leftCaptured = captured && captured->Type == InputControlType::MouseButton && captured->Code == Mouse::ButtonLeft;
// A press starts a gesture: the UI's when it is over the UI, else the game's, each until every button is released.
if (pointer.Pressed != 0 && m_Gesture == Gesture::None)
{
	m_Gesture = m_PointerOverUI ? Gesture::UI : Gesture::Game;
	if (m_Gesture == Gesture::UI && (pointer.Pressed & c_Left) != 0 && m_Hovered != entt::null && !leftCaptured)
	{
		m_Pressed = m_Hovered;
		Focus(m_Pressed); // A click on a selectable focuses it
		if (m_Scene.GetRegistry().all_of<UISliderComponent>(m_Pressed))
			m_Dragging = m_Pressed;
		// A click on an input field puts its caret at the character nearest the pointer.
		if (m_Editing != entt::null && m_Editing == m_Pressed)
		{
			UIBox fieldBox;
			UICanvasView fieldView;
			const std::optional<glm::vec2> point = FindOnScreen(ui, m_Editing, fieldBox, &fieldView) ? GetPointerOn(ui, fieldView) : std::nullopt;
			if (const std::optional<uint32_t> caret = point ? ui.FindInputFieldCaret(m_Editing, screen.Screen, *point) : std::nullopt)
			{
				m_FieldState.Caret = *caret;
				m_FieldState.Anchor = *caret;
				m_CaretBlink = 0.0f;
				ShowFieldState();
			}
		}
	}
}
```

1. **Lines 284–285:** a binding capture, such as a rebinding menu waiting for a control, may take the left button. That press is the new binding and presses no widget.
2. **Lines 287–289:** the first press with no gesture running starts one: the UI's if the pointer is over the UI, else the game's.
3. **Lines 290–295:** only the left button presses widgets. The pressed widget takes the focus, and a slider starts a drag at once.
4. **Lines 297–309:** a press on an input field moves its caret; [Text and text fields](../ui/text.md) explains it.

The right and middle buttons over the UI still start a UI gesture, so the game never sees them, but they press no widget. The release part completes the picture.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L313-L328"
	if (m_Dragging != entt::null && (pointer.Down & c_Left) != 0)
		DragSlider(ui, m_Dragging);
	if ((pointer.Released & c_Left) != 0)
	{
		// A click is a release over what was pressed: a press dragged off and released elsewhere clicks nothing.
		if (m_Pressed != entt::null && m_Pressed == m_Hovered && m_Pressed != m_Dragging)
			Click(m_Pressed);
		m_Pressed = entt::null;
		m_Dragging = entt::null;
	}

	// The UI's gestures and the scrolling over it are hidden from the game, also in the frame of the release.
	Input::SetPointerCapture(m_Gesture == Gesture::UI || (m_Gesture == Gesture::None && m_PointerOverUI));
	if (pointer.Down == 0)
		m_Gesture = Gesture::None;
}
```

1. **Lines 313–314:** a slider follows the pointer while the left button is down, also outside its rect.
2. **Lines 318–319:** a click is a release over the widget that was pressed; a slider that was dragged is not clicked.
3. **Line 325:** capture is on during a UI gesture, and between gestures while the pointer is over the UI. It hides mouse buttons and scroll from the game.
4. **Lines 326–327:** when no button is down, the gesture ends.

The capture is set at the end of the step and stays on through the frame of the release. So the game cannot see the release as a click either. A script reads the same state through `UI::IsPointerOverUI` and through the input class, which honors the capture.

```mermaid caption="The gesture states. A press chooses the owner, and the owner keeps the gesture until every button is up." alt="A state diagram with three states: no gesture, UI gesture and game gesture. From no gesture, a press over the UI leads to the UI gesture and a press elsewhere leads to the game gesture. Both return to no gesture when all buttons are up."
stateDiagram-v2
  [*] --> NoGesture
  NoGesture --> UIGesture: press over the UI
  NoGesture --> GameGesture: press elsewhere
  UIGesture --> NoGesture: every button up
  GameGesture --> NoGesture: every button up
```

Compare the three cases of the toy with the real rules. A player presses the Play button, drags away and releases. The gesture is the UI's from the press, so the game saw nothing. No click happens, because the release is not over the pressed button.

A player presses in the game world and drags over a menu panel: the gesture stays the game's, and the game keeps its button until release. A player moves over the menu with no button down: no gesture exists, but the capture is on while the pointer is over the UI, so scroll over a menu does not zoom the camera.

The same rule covers keys. Only this system sets the keyboard capture, and it does so while an input field is edited, so a player who types a name does not also walk around. A key that ends editing, such as Escape, stays the UI's until the end of that frame. Without this, the key would end editing and also reach the game in the same frame.

### From a press to a widget

A click on a selectable does different things for different widgets. `Click` runs for a release over the pressed widget, and for Submit on the focused one.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L384-L415"
void GameUISystem::Click(entt::entity selectable)
{
	entt::registry& registry = m_Scene.GetRegistry();
	if (registry.all_of<UIButtonComponent>(selectable))
		QueueEvent(UIEventType::Click, selectable);
	if (const UIToggleComponent* toggle = registry.try_get<UIToggleComponent>(selectable))
		SetToggle(selectable, !toggle->IsOn);
}

void GameUISystem::SetToggle(entt::entity toggle, bool on)
{
	entt::registry& registry = m_Scene.GetRegistry();
	const UIToggleComponent& component = registry.get<UIToggleComponent>(toggle);
	if (component.IsOn == on)
		return;
	const UUID group = component.Group;
	if (group.IsValid())
	{
		// One of a group is on at a time: switching the one that is on off does nothing, switching another on turns it off.
		if (!on)
			return;
		for (const auto [other, otherToggle] : registry.view<UIToggleComponent>().each())
		{
			if (other == toggle || !otherToggle.IsOn || otherToggle.Group != group)
				continue;
			registry.patch<UIToggleComponent>(other, [](UIToggleComponent& value) { value.IsOn = false; });
			QueueEvent(UIEventType::ValueChanged, other, 0.0f);
		}
	}
	registry.patch<UIToggleComponent>(toggle, [on](UIToggleComponent& value) { value.IsOn = on; });
	QueueEvent(UIEventType::ValueChanged, toggle, on ? 1.0f : 0.0f);
}
```

1. **Lines 387–388:** a button queues a click event.
2. **Lines 389–390:** a toggle flips; this works in the same call as the button, so one entity may be both.
3. **Lines 402–404:** in an exclusive group, switching on the one that is on does nothing and switching off is refused.
4. **Lines 405–411:** switching one on turns the others of the group off with `registry.patch`, each with its own event of value 0.
5. **Lines 413–414:** the toggle itself is patched and queued with value 1 or 0.

A slider is not clicked. When the left press lands on one, it becomes the dragged widget. While the button is down, each update maps the pointer to a fraction of the slider's rect along its direction, clamps it between 0 and 1, and turns it into a value. The value is clamped to the range and, with `WholeNumbers`, rounded. A value that did not change raises no event.

:::example[Dragging a volume slider]
The slider's rect spans x from 100 to 300 (200 units wide), its range is 0 to 10, its direction is `LeftToRight` and `WholeNumbers` is on. The pointer is at x = 250: the fraction is (250 − 100) / 200 = 0.75, so the raw value is 7.5, which rounds to 8. The pointer then moves to x = 400, outside the rect. The fraction is clamped to 1, and the value is 10.

The release does not click the slider, since it was dragged. For `RightToLeft` the fraction is turned around: at x = 250 the value would be 2.5, rounded to 3.
:::

A focused slider also moves with the keys. A direction along its axis changes the value by `KeyboardStep`, or by a tenth of the range when that is 0 (at least 1 with whole numbers). A direction across the axis moves the focus on, as for any selectable.

### Visual states

A selectable shows what is happening to it with colors or images. A **visual state** is one of Normal, Hover, Pressed, Focused and Disabled, chosen by priority from the system's own state.

A **transition** (in the UI) is how the look changes from one state to the next: none, a color tint that fades, or an image swap.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L867-L878"
UIVisualState GameUISystem::GetDesiredState(entt::entity selectable) const
{
	if (!IsInteractable(selectable))
		return UIVisualState::Disabled;
	if (selectable == m_Pressed && selectable == m_Hovered)
		return UIVisualState::Pressed;
	if (selectable == m_Hovered)
		return UIVisualState::Hover;
	if (selectable == m_Focused)
		return UIVisualState::Focused;
	return UIVisualState::Normal;
}
```

1. **Lines 869–870:** Disabled wins over everything.
2. **Lines 871–872:** Pressed needs both: the widget is pressed and the pointer is still over it, so dragging off lets the button rise again.
3. **Lines 873–876:** then Hover, then Focused, and Normal when nothing applies.

A tint does not jump. `UpdateVisualStates` keeps one fade record for each selectable that is hovered, pressed, focused or still fading. When the desired state changes, the fade starts from the color shown now and runs to the new state's color over `FadeDuration`, which defaults to 0.1 seconds of unscaled time. When the fade has ended in Normal or Disabled, the record is removed, so a menu of a hundred buttons at rest costs nothing here.

For a fade at 60 :term[frames per second]{id=frame-rate}, 0.1 seconds is six frames of 16.7 ms. Take a button whose Normal color is (1, 1, 1, 1) and Hover color (0.9, 0.9, 0.9, 1). After 0.05 seconds the shown color is (0.95, 0.95, 0.95, 1). If the pointer leaves now, the new fade starts from 0.95 and runs back to 1 over a full 0.1 seconds.

An important detail follows from the contract: the fades count unscaled time, so the buttons of a pause menu still fade at time scale 0. Test `GameUI.Events` has one case for exactly that.

### Focus and navigation

The focus is stored in the system as one entity, `m_Focused`. A click gives it to the pressed selectable, and `SetFocus` (used by scripts) gives it to any selectable that is enabled and shown on a canvas that receives input. Every change queues `FocusChanged` events: one with `Focused` false for the old widget, one with true for the new.

The common mistake is a menu that shows no focus. At the start of the scene nothing has the focus. The first direction press, or the first Submit, focuses the start selectable, and that press only focuses: nothing moves and nothing clicks. A gamepad player's first press then looks like nothing happened, because nothing was drawn as focused before it.

The start selectable is the `FirstSelected` of the topmost canvas that receives input, if it is set and usable. Otherwise it is the top-left selectable of that canvas, the one with the smallest top edge and then the smallest left edge. Screen canvases come before canvases in the scene. For a menu, set `First Selected` or call `Focus()` from the script when the menu opens, as `MainMenu` does.

The directions are the UI map's actions, so held keys repeat. `UpdateNavigation` reads them one by one.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L512-L538"
for (const UIAction direction : c_Directions)
{
	if (!m_Actions.IsRepeated(direction))
		continue;
	// An edited field's caret moves left and right (a gamepad's: the keyboard is the field's meanwhile).
	if (editing && (direction == UIAction::Left || direction == UIAction::Right))
	{
		if (const UIInputFieldComponent* field = m_Scene.GetRegistry().try_get<UIInputFieldComponent>(m_Editing))
		{
			MoveCaret(field->Text, direction == UIAction::Left ? -1 : 1, false, false);
			ShowFieldState();
		}
		continue;
	}
	// Navigating without a focus starts it.
	if (m_Focused == entt::null)
	{
		Focus(FindStartSelectable(ui, views));
		continue;
	}
	// A focused slider steps along its direction instead of navigating.
	if (m_Scene.GetRegistry().all_of<UISliderComponent>(m_Focused) && StepSlider(m_Focused, direction))
		continue;
	const entt::entity next = Navigate(ui, views, m_Focused, direction);
	if (next != entt::null)
		Focus(next);
}
```

1. **Line 514:** an action counts when it was pressed or when its repeat fires (see [Input actions](../input/actions.md) for 0.4 s then 0.1 s).
2. **Lines 517–524:** while a text field is edited, left and right move its caret instead.
3. **Lines 527–530:** with no focus, a direction press focuses the start selectable and does nothing else.
4. **Lines 533–534:** a focused slider takes the directions along its axis as value steps.
5. **Lines 535–537:** otherwise `Navigate` finds the next selectable, and the focus moves there.

Submit works in the same function. With no focus it focuses the start selectable. With an edited field it submits the field. Otherwise it calls `Click` on the focused widget, so a button queues its click and a toggle flips.

Cancel only stops editing a field; the UI raises no event for it, and scripts read it themselves with `UI::IsActionPressed`, as `MainMenu` does to close panels. The default bindings of the UI map are Enter, the Enter key of the number pad, Space or gamepad A for Submit, and Escape or gamepad B for Cancel. The directions are the arrow keys, the d-pad and the left stick.

`Navigate` depends on each selectable's `Navigation` mode. With `None`, the element is skipped and cannot be left. With `Explicit`, the neighbour is the entity named by the field for that direction, and the move happens only if it is usable.

With `Automatic`, the system scores every other selectable. In screen pixels, take the offset from the focused element's center to the candidate's center. The part along the pressed direction must be above zero, since the candidate must lie ahead. The part across is the distance sideways. The score is $along + 2 \cdot across$ (read: the along part plus twice the across part), and the lowest score wins.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L827-L860"
UIBox fromBox;
UICanvasView fromView;
if (!FindOnScreen(ui, from, fromBox, &fromView))
	return entt::null;
const glm::vec2 origin = fromBox.GetCenter() * fromView.Scale;
const glm::vec2 axis = GetDirectionVector(direction);
entt::entity best = entt::null;
float bestScore = std::numeric_limits<float>::max();
for (const UICanvasView& view : views)
{
	if (!view.ReceivesInput || view.WorldSpace != fromView.WorldSpace || (view.WorldSpace && view.CanvasIndex != fromView.CanvasIndex))
		continue;
	for (uint32_t element = 0; element < ui.GetElementCount(view); element++)
	{
		const entt::entity entity = ui.GetElementEntity(view, element);
		if (entity == from)
			continue;
		const UISelectableComponent* candidate = registry.try_get<UISelectableComponent>(entity);
		if (!candidate || candidate->Navigation == UINavigation::None || !IsInteractable(entity) || !ui.IsElementVisible(view, element))
			continue;
		const glm::vec2 offset = ui.GetElementBox(view, element).GetCenter() * view.Scale - origin;
		const float along = glm::dot(offset, axis);
		if (along <= 1e-3f * view.Scale) // Ahead by more than 1e-3 canvas units
			continue;
		const float across = std::abs(offset.x * axis.y - offset.y * axis.x);
		const float score = along + 2.0f * across;
		if (score < bestScore)
		{
			bestScore = score;
			best = entity;
		}
	}
}
return best;
```

1. **Line 831:** the origin is the focused element's center, converted to screen pixels so canvases of different scales compare fairly.
2. **Line 837:** only canvases that receive input and are of the same kind count; a canvas in the scene navigates only within itself.
3. **Lines 848–850:** the along part is a :term[dot product]{id=dot-product} with the direction's :term[unit vector]{id=unit-vector}; a candidate not ahead is skipped.
4. **Lines 851–852:** the across part is the absolute value of a :term[cross product]{id=cross-product}, and the score weighs it twice.

:::example[Which button gets Right?]
The focus is on A at (200, 300), and Right is pressed. Candidate B is at (500, 300): along 300, across 0, score 300. Candidate C is at (400, 380): along 200, across 80, score 200 + 160 = 360. Candidate D is at (350, 200): along 150, across 100, score 150 + 200 = 350. Candidate E is at (100, 300): along −100, so it is behind and skipped.

B wins, although D is closer in a straight line (distance about 180 against 300).

The weight of 2 makes the focus prefer the element in the row over a nearer one off to the side, which is what a player expects from "right".
:::

The weight is a design choice. With a weight of 1, D would win here. With a larger weight the focus sticks to rows and columns, and an off-grid button may be hard to reach. An exercise below asks you to check both.

### Events and the script bridge

When something happens, the system calls `QueueEvent`. An event is a `UIEventInfo`: its type (`Click`, `ValueChanged`, `FocusChanged`, `Submit`), the widget, the widget's identifier, the event target if the widget names another entity, the value, and whether the widget gained the focus. Events wait in one queue in the order of the update's steps: the pointer's first, then the input field's, then navigation's. A click on a button therefore gives its events in a stable order: the press queued the focus changes, if the focus moved, and the release queues the click.

Dispatch happens once, at the end of the update. The listeners are a list that code may change while it runs, so `DispatchEvents` takes a copy of the list before it starts.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L1196-L1213"
void GameUISystem::DispatchEvents()
{
	if (m_PendingEvents.empty())
		return;
	// Listeners may add listeners, remove them and change the UI: each event goes to the listeners there were when the
	// dispatch started, unless they were removed meanwhile.
	std::vector<UIEventInfo> events;
	events.swap(m_PendingEvents);
	const std::vector<Ref<EventListener>> listeners = m_Listeners;
	for (const UIEventInfo& event : events)
	{
		for (const Ref<EventListener>& listener : listeners)
		{
			if (!listener->Removed)
				listener->Callback(event);
		}
	}
}
```

1. **Lines 1202–1204:** the pending events and the listeners are both copied out first, so a listener may add events or listeners safely.
2. **Lines 1207–1210:** each event goes to every listener of the copy, unless a listener was removed meanwhile.

A listener added during a dispatch gets the next events, and one removed is never called again. That is tested in `GameUI.Events`.

The scripting module is one such listener, registered when the scene starts to play. It must map engine events to script :term[callbacks]{id=callback}. The callbacks are `OnUIClick`, `OnUIValueChanged`, `OnUIFocusChanged` and `OnUISubmit`. They sit at the end of the script class description, and the engine reads them only when the module's `StructSize` covers them, so older modules keep working. The routing is a small function.

```cpp src="Strata/src/Strata/Scripting/ScriptSystem.cpp#L415-L450"
void ScriptSystem::OnUIEvent(const UIEventInfo& event)
{
	if (!m_Running || !GetUsableModule())
		return;
	ScriptCallback callback = ScriptCallback::OnUIClick;
	switch (event.Type)
	{
		case UIEventType::Click: callback = ScriptCallback::OnUIClick; break;
		case UIEventType::ValueChanged: callback = ScriptCallback::OnUIValueChanged; break;
		case UIEventType::FocusChanged: callback = ScriptCallback::OnUIFocusChanged; break;
		case UIEventType::Submit: callback = ScriptCallback::OnUISubmit; break;
	}

	// The widget's scripts, then its target's: a copy of each list, since the callbacks may add or remove scripts
	// (removed instances are flagged and skipped). An instance on both is called once (the target is never the widget).
	const uint64_t widget = static_cast<uint64_t>(event.WidgetID);
	for (const Entity receiver : { event.Widget, event.Target })
	{
		if (!receiver || !m_Scene.GetRegistry().valid(receiver.GetHandle()))
			continue;
		auto it = m_Instances.find(receiver.GetUUID());
		if (it == m_Instances.end())
			continue;
		const std::vector<Ref<Instance>> instances = it->second;
		for (const Ref<Instance>& instance : instances)
		{
			if (instance->Removed || instance->Disabled || !instance->Created || !instance->Handle || !instance->Class->Implements(callback))
				continue;
			ScriptModule* module = GetUsableModule();
			if (!module)
				return;
			const ScriptCallSite site = MakeCallSite(*instance, ScriptCallbackToString(callback));
			HandleCallResult(*instance, callback, module->InvokeUIEventCallback(site, instance->Handle, callback, widget, event.Value, event.Focused));
		}
	}
}
```

1. **Line 417:** no module or not running: the event is dropped.
2. **Lines 419–426:** the event type picks the callback.
3. **Lines 430–436:** the receivers are the widget and then its event target; each has its list of script instances.
4. **Lines 438–447:** the list is copied because a callback may add or remove scripts, and each instance is called inside the crash guard.

The widget's scripts run first and the target's second. If one instance is attached to both, the call happens once, because the target is never the widget.

```mermaid caption="From a pointer to a script. The system queues events during its update, dispatches them at the end, and the scripting module routes each one to the widget's scripts and then to its event target's scripts." alt="A sequence diagram with four participants: the pointer, the UI system, the scripting module and a script. The pointer presses and releases. The UI system queues a focus event on press and a click on release, then dispatches at the end of the update. The scripting module calls the script's click callback for the widget, then for the event target."
sequenceDiagram
  participant P as Pointer
  participant U as UI system
  participant S as Scripting
  participant M as MainMenu
  P->>U: press on Play button
  U->>U: queue FocusChanged if the focus moves
  P->>U: release on Play button
  U->>U: queue Click
  U->>S: dispatch at the end of the update
  S->>M: OnUIClick(widget)
```

A script reaches the other half of the bridge, the control of widgets, through `IUIControl`: text, image, color, whether it is enabled, value, focus, whether the pointer is over the UI and the action state. The script :term[application binary interface]{id=abi} (ABI) has 15 UI host functions for this, appended at the end of the host table. The software development kit (:term[SDK]{id=sdk}) wraps them in two classes.

`UIElement` comes from `entity.GetUI()` and offers `SetText`, `SetValue`, `Focus` and more. `UI` has the static functions `GetFocused`, `ClearFocus`, `IsPointerOverUI`, `IsActionPressed` and `IsActionDown`, and the enum `UIAction` names the six actions. Values written through these functions raise no events, as contract rule 5 says: the callbacks report the player's input only. A call such as `entity.GetUI().SetValue(7)` clamps and snaps the value as input would.

### The main menu, end to end

`MainMenu` shows the bridge at work. Its `OnCreate` focuses the Play button, so a gamepad player sees the focus at once. Its `OnUpdate` reads `UI::IsActionPressed(UIAction::Cancel)` and closes the settings or credits panel, because the UI itself does nothing on Cancel. It also scrolls the credits text on unscaled time. One `OnUIClick` handles every button, since the menu entity is the event target of all of them.

```cpp src="Samples/ThirdPerson/Scripts/MainMenu.cpp#L85-L115"
void OnUIClick(Entity widget) override
{
	if (widget == PlayButton || widget == SettingsButton || widget == CreditsButton || widget == QuitButton || widget == CreditsBackButton)
		ThirdPerson::PlayInterfaceSound(ClickSound);
	if (widget == PlayButton && !Loading)
	{
		Loading = true;
		Log::Info("ThirdPerson: starting the course");
		Game::LoadScene(CourseScene);
	}
	else if (widget == SettingsButton)
	{
		ShowCredits(false);
		if (SettingsMenu* settings = GetEntity().GetScript<SettingsMenu>())
			settings->Toggle(SettingsButton);
	}
	else if (widget == CreditsButton)
	{
		if (SettingsMenu* settings = GetEntity().GetScript<SettingsMenu>(); settings && settings->IsOpen())
			settings->Close();
		ShowCredits(!(CreditsPanel.IsValid() && CreditsPanel.IsActive()));
	}
	else if (widget == CreditsBackButton)
	{
		ShowCredits(false);
	}
	else if (widget == QuitButton)
	{
		Game::Quit();
	}
}
```

1. **Lines 87–88:** the click sound plays for any of the five buttons.
2. **Lines 89–93:** Play starts loading the course; the `Loading` flag keeps a double click from starting it twice.
3. **Lines 95–110:** the other buttons open or close panels, and `ShowCredits` moves the focus into the panel.
4. **Lines 111–114:** Quit asks the game to stop.

Now the trace of one click can be told in full. The player moves to Play and presses. The pointer step hits the button itself, since its label is no raycast target, and `FindSelectable` returns it at once. Hover is set, and the first press starts a UI gesture. The button already has the focus from `OnCreate`, so no focus event is queued, and capture hides the press from the game.

On release over the same button, `Click` queues a `Click` event. At the end of the same update `DispatchEvents` runs the scripting listener. The listener finds the `MainMenu` script on the event target and calls `OnUIClick` with the Play button. The script's `OnUpdate` for this frame runs after all of it.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Linear scan of all elements | Small interface libraries | No grid to build, no stale grid to fear | Cost per query grows with the element count |
| Tree of bounding boxes | Web browsers, large editors | Good for uneven or nested layouts | A more complex build, and no gain for evenly spread rects |
| Event bubbling through the parents | Web pages | Any parent may handle or stop an event | Events would reach many handlers, and scripts could stop each other's events |
| Ray sources per canvas and camera | Unity's event system | One mechanism for UI and for 3D objects | Scene geometry would block clicks, but the game then needs a physics query per frame |
| Hand-wired focus only | Console games with fixed menus | Exact control of every move | Every menu needs wiring, and a menu that changes needs new wiring |
| Callbacks stored on widgets | Many immediate-mode and retained libraries | Handler next to the widget | Widgets would hold code, which a scene file cannot save, and hot reload would break them |

## How it is tested

The suite `GameUI.HitTest` (file `StrataTests/src/GameUI/GameUIInputTests.cpp`) checks the order of canvases and elements, raycast targets, half-open edges, grid rebuilds and the 64 candidate bound. `GameUI.Capture` checks gestures, capture, the content scale and a binding capture's left press.

`GameUI.Events` holds the widgets: clicks on release, toggles and groups, a slider, disabled widgets, listeners, fades and image swaps. `GameUI.Navigation` checks the 3x3 grid, an irregular menu, explicit neighbours, the start selectable, repeat, the d-pad and stick, slider steps, Submit and Cancel and rebinding. `GameUI.WorldSpace` checks the ray, the pixel of a canvas point, navigation within a canvas and clicks through the camera. `GameUI.InputField` belongs to the text page.

The suite `Scripting.UI` (in `StrataTests/src/Scripting/ScriptUITests.cpp`) checks the script side. Host functions refuse misuse harmlessly. Events reach the widget's scripts and then the event target's, once each and before `OnUpdate`. Callbacks are read only from class descriptions large enough to hold them.

The feature script `UIFeatures` in `StrataTests/FeatureTest/Scripts/UIFeatures.cpp` is a player that goes frame by frame: it clicks, toggles, drags a slider, navigates, types and edits. Run a suite directly with `StrataTests.exe --test-suite=GameUI.Navigation`, or all of them with `ctest`.

## Changing it safely

The extension points are few. A new widget is a component plus a case in `Click`, `QueueEvent` and, if it has an event target, in the target lookup. A new kind of navigation goes into `Navigate`. A new event goes into `UIEventType`, `QueueEvent` and `ScriptSystem::OnUIEvent`, with a callback appended at the end of the class description.

Keep the contract. Do not read the pointer for the UI anywhere else, do not set the captures from another system, and do not test hits against the window's size. Write widget values with `registry.patch`, and keep the system before the scripts.

Whatever you change in the hit test, check `GameUI.HitTest`, `GameUI.Capture`, `GameUI.WorldSpace` and the feature test. Run the perf tests of the UI in a Release build when a change can affect the cost of a query.

## What went wrong before

A script that read `UI::IsActionPressed` kept being told that Submit was pressed after the last canvas was destroyed. The reason was that the actions were updated inside the canvas branch, so with no canvas the press from the last update was never cleared. The fix updates the actions first in every update, canvas or not (the first lines of `OnUpdate`). The regression test is "UI actions do not stay pressed while no canvas exists" in `GameUI.Navigation`. It destroys the canvas while Enter is held and checks that the press is no longer reported but the key is still down.

## Summary

- A click travels from the pointer step through the hit test, the walk to the nearest selectable, the click on release and the queue to the dispatch of `OnUIClick`.
- A hit test takes the topmost canvas, then the last drawn visible raycast target in the point's grid cell, with half-open rects; the press goes to the nearest selectable ancestor in the same canvas.
- A gesture belongs to the UI or the game from its first press until every button is up, and the pointer capture hides it from the game.
- Automatic navigation scores candidates ahead by the along part plus twice the across part, in screen pixels, and the lowest score gets the focus.
- Events queue in input order and dispatch once at the end of the update, to the widget's scripts and then to its event target's; values set by code raise none.

## Check yourself

1. The player presses the left button over the panel behind the Play button's icon, but outside the button, drags onto the button and releases. What happens? (a) The button is clicked. (b) The panel is hit, which is no selectable, so no widget is pressed and no click happens, while the game still sees nothing. (c) The game receives the press.

   :::answer{tests="gestures"}
   Answer (b). A press over the UI starts a UI gesture even when no widget is pressed, so the game does not see it. The release over the button cannot click, because the pressed widget was none. Answer (a) is wrong because a click needs the press on the button, and answer (c) is wrong because the gesture belongs to the UI until every button is up.
   :::

2. A button has a 40 by 40 icon child, and the child's image is a raycast target. The player clicks the icon. Which entity does `HitTest` return, and which one is pressed?

   :::answer{tests="hit-test"}
   `HitTest` returns the icon, the last drawn target under the point. `FindSelectable` walks up from it and finds the button, which is pressed. The walk stops at the canvas, so an icon outside any button presses nothing.
   :::

3. The focus is on A at (200, 300). Candidate F is at (320, 360). Right is pressed. What are the along part, the across part and the score?

   :::answer{tests="navigation"}
   The offset is (120, 60). Along the direction (1, 0) the part is 120, the across part is 60, and the score is 120 + 2 × 60 = 240. Compare that number with the other candidates before deciding: the lowest score wins.
   :::

4. A script calls `SetValue(5)` on a slider and has an `OnUIValueChanged` handler. Is the handler called?

   :::answer{tests="events"}
   No. Values set by code raise no events; the callbacks report the player's input only. This stops loops between scripts and widgets. If the script needs to know, it already knows: it made the change.
   :::

5. A gamepad player opens a menu with no `First Selected` and presses Down once. What happens?

   :::answer{tests="trace-click, navigation"}
   The press only focuses the start selectable, which is the top-left selectable of the topmost input canvas. Nothing else moves. A second press then navigates. A menu should set `First Selected` or call `Focus()` when it opens.
   :::

## Exercises

1. **Basic.** Trace it yourself: find where one click is decided. Put breakpoints in `UpdatePointer`, `FindSelectable`, `Click` and `DispatchEvents` while the Play button of the Third-Person main menu is clicked.

   :::answer[Worked solution]{tests="trace-click"}
   In `GameUISystem::UpdatePointer` in `Strata/src/Strata/GameUI/GameUISystem.cpp`, the hit test returns the icon or button and `FindSelectable` walks up to the button. The first press starts the UI gesture and focuses the button. On release, `Click` queues the click when the release is over the pressed widget. `DispatchEvents` then runs the listeners, and `ScriptSystem::OnUIEvent` calls `OnUIClick` of `MainMenu` in `Samples/ThirdPerson/Scripts/MainMenu.cpp`.
   :::

2. **Medium.** Predict, then run, the choice of the focus for the example candidates. Use the sketch to print each score.

   :::answer[Worked solution]{tests="navigation" solution="sketches/ui-input-navigate.cpp"}
   By hand B scores 300, C 360 and D 350, and E is skipped. The sketch repeats the engine's scoring on those four candidates.

   ```cpp sketch="ui-input-navigate.cpp"
   // Exercise: which selectable gets the focus when Right is pressed, by the score along + 2 x across.
   #include <glm/glm.hpp>

   #include <cmath>
   #include <cstdio>
   #include <limits>
   #include <string>
   #include <vector>

   struct Candidate
   {
   	std::string Name;
   	glm::vec2 Center;
   };

   // Returns the index of the best candidate, or -1 when none lies ahead.
   static int Navigate(glm::vec2 origin, glm::vec2 axis, const std::vector<Candidate>& candidates)
   {
   	int best = -1;
   	float bestScore = std::numeric_limits<float>::max();
   	for (size_t index = 0; index < candidates.size(); index++)
   	{
   		const glm::vec2 offset = candidates[index].Center - origin;
   		const float along = glm::dot(offset, axis);
   		if (along <= 1e-3f)
   			continue;
   		const float across = std::abs(offset.x * axis.y - offset.y * axis.x);
   		const float score = along + 2.0f * across;
   		std::printf("%s: along %.0f, across %.0f, score %.0f\n", candidates[index].Name.c_str(), along, across, score);
   		if (score < bestScore)
   		{
   			bestScore = score;
   			best = static_cast<int>(index);
   		}
   	}
   	return best;
   }

   int main()
   {
   	const std::vector<Candidate> candidates = { { "B", { 500.0f, 300.0f } }, { "C", { 400.0f, 380.0f } }, { "D", { 350.0f, 200.0f } },
   		{ "E", { 100.0f, 300.0f } } };
   	const int best = Navigate({ 200.0f, 300.0f }, { 1.0f, 0.0f }, candidates);
   	std::printf("Right moves the focus to %s\n", best >= 0 ? candidates[static_cast<size_t>(best)].Name.c_str() : "nothing");
   	return 0;
   }
   ```

   ```text output-of="ui-input-navigate.cpp"
   B: along 300, across 0, score 300
   C: along 200, across 80, score 360
   D: along 150, across 100, score 350
   Right moves the focus to B
   ```

   1. **Line 24:** the along part is the dot product of the offset with the direction.
   2. **Lines 25–26:** a candidate that is not ahead is skipped.
   3. **Lines 27–28:** the across part is the sideways distance, and the score adds it twice to the along part.
   4. **Lines 30–33:** the lowest score is kept.
   :::

3. **Medium.** Change the weight of 2 in `Navigate` to 1 and then to 4. For the example candidates, which one wins each time? Which test of `GameUI.Navigation` would you expect to notice, and why?

   :::answer[Worked solution]{tests="navigation"}
   With weight 1 the scores are B 300, C 280 and D 250, so D wins. With weight 4 they are B 300, C 520 and D 550, so B wins, and more strongly. The test with "by along + 2 x across" in its title states the weight, so it is the one to expect. Run `GameUI.Navigation` to see which tests fail in fact.
   :::

4. **Hard.** The Play sign is a world-space canvas whose matrix scales by 0.01 and which lies at z = −2 instead of 0. The camera is at (0, 0, 4) and the ray's direction is proportional to (0.25, 0.125, −1). Where does the ray cross the canvas, in canvas units, and how far is the crossing from the camera?

   :::answer[Worked solution]{tests="hit-test"}
   The ray reaches z = −2 after a parameter of 6 along (0.25, 0.125, −1): the point is (1.5, 0.75, −2) in the world. Dividing by the scale 0.01 gives (150, 75) canvas units, taken from the canvas origin at (0, 0, −2). The length of the direction is about 1.038, so the distance is 6 × 1.038 ≈ 6.23 world units. The distance only orders canvases; the point is what the grid is asked about. With a real canvas's matrix, which flips y, the point lies 150 units right of the pivot and 75 units above it.
   :::

## Where it lives in Strata

- `Strata/src/Strata/GameUI/GameUISystem.cpp`: the "UI" system, its pointer, focus, navigation, visual states and events.
- `Strata/src/Strata/GameUI/GameUIHitTest.cpp`: `GameUIHitTester`, the grids, and `GameUIPointer`, the ray and its intersection.
- `Strata/src/Strata/Scene/SceneServices.h`: `UIEventType`, `UIEventInfo`, `IUIEvents` and `IUIControl`.
- `Strata/src/Strata/Scripting/ScriptSystem.cpp`: `OnUIEvent`, the route from events to scripts.
- `StrataScriptCore/Include/StrataScript/UI.h`: the SDK's `UIElement`, `UI` and `UIAction`.
- `StrataEditor/src/Editor/EditorUICommands.cpp`: the command `ui.hitTest`.
- Tests: `GameUI.HitTest`, `GameUI.Capture`, `GameUI.Events`, `GameUI.Navigation`, `GameUI.WorldSpace` and `Scripting.UI`; the feature script `UIFeatures`.

## Further reading

- The DOM event flow on MDN (developer.mozilla.org), "Event bubbling": the web's routing by bubbling and capture; beginner.
- Unity's manual page on the Event System (docs.unity3d.com): raycasters, input modules and the selection of the target; intermediate.
- "Game Programming Patterns" by Robert Nystrom, the chapters on the observer and the command pattern (gameprogrammingpatterns.com): queued events and decoupling; beginner.
- "Real-Time Collision Detection" by Christer Ericson, the chapter on uniform grids: the grid that the hit test is built on; advanced.
