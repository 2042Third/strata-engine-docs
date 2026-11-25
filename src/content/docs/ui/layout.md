---
id: ui/layout
title: "Rects, anchors and layout"
description: "How Strata turns the UI components of a canvas into one box per element for a screen: scale, anchors, pivots, groups and clips."
kind: internals
size: L
tracks: [E]
needs: []
time: 90
learn:
  - id: compute-box
    text: compute the box of any UI element by hand from its anchors, pivot, position, size, its canvas and the screen
  - id: scale-log
    text: explain why a canvas keeps its scale on a screen twice as wide and half as tall
  - id: two-passes
    text: trace the width pass and the height pass over a layout group, and say why widths come first
  - id: find-code
    text: find the function in Strata that performs each step of the layout
since: 0.4.0
status: final
---

A game's menus, health bars and score counters must sit in the right place on every screen. Strata's layout code does that job: it turns the user interface (UI) components of one canvas into one box per element, for one screen size, in canvas units. It draws nothing, shapes no text and reads no mouse. Drawing and input read the boxes that this page makes, so a wrong box is wrong everywhere.

## The problem and how engines solve it

A game ships to screens of many sizes: a laptop at 1280 by 720 pixels, a monitor at 2560 by 1440, a phone held upright, a wide television. A health bar that must sit in the bottom left corner needs a rule that works on all of them. The oldest rule is a pixel position for each element. It works on the one screen you tested. On the next, the bar covers a quarter of the area it covered before, or falls off the edge.

The first fix is an **anchor**: a point on the parent rectangle, written as a fraction of its width and height, that an element is pinned to. The point (0, 1) is the bottom left corner of the parent, and (0.5, 0.5) is its center. An element pinned to a corner stays there whatever the parent's size, and a small offset from the point places it. Unity's `RectTransform`, Unreal's anchors and Godot's anchors with offsets work this way. Two anchor points, one on each side, let a rectangle stretch with its parent.

Anchors are cheap and predictable, but each places one element alone. A menu of five buttons in a column needs a second tool that places siblings by their sizes. Engines offer three families.

- A **constraint solver** takes equations such as "the left edge of B is 8 units right of the right edge of A" and finds sizes that satisfy all of them. Apple's Auto Layout is built on such a solver. The approach is general. Its cost is a solver in every frame and errors that read "these constraints conflict".
- The **flexible box** layout of the web, and Yoga (the layout library of React Native), let the children of a row or column share its space by weights. They grow, shrink and wrap. They fit lists well, and they cost a long list of rules for how items shrink.
- **Measure and arrange** is the model of Microsoft's Windows Presentation Foundation, and Flutter uses a close relative. A parent asks each child how big it wants to be (measure), then tells each child where it is (arrange). Sizes travel up the tree and positions travel down.

Strata combines the first and the last. Every element has anchors, a pivot, a position and a size, as in Unity and Unreal. A parent that holds a **layout group** places its children by measure and arrange. Strata has no solver and no shrinking: the rules fit on one page, and you can compute any box by hand. The cost is that children cannot share a lack of space by weight.

## The map

The layout code lives in `Strata/src/Strata/GameUI/`. One `GameUIScene` exists per scene, kept in the scene registry's context and created on first use. It holds the canvases, their elements and their boxes, and nothing that belongs to the :term[graphics processing unit]{id=gpu} (GPU): only asset handles, because a scene may be released on a background thread.

A **root canvas** is a canvas component with no other canvas among its ancestors: the top of one screen of UI. A canvas inside another canvas is a plain element of the outer one, and its scale settings are ignored.

```mermaid caption="Four callers ask the game UI scene for the layout of one screen. The scene keeps elements and boxes per root canvas, and drawing and input read the boxes." alt="Four boxes for the UI system, the UI render pass, the editor commands and the editor canvas mode point to a group named game UI scene. Inside it, root canvases lead to element arrays and then to layouts per screen size. Arrows lead from the layouts to drawing and input."
flowchart LR
  SYS["UI system (input screen)"] -->|EnsureLayout| SCN
  PASS["UI render pass (its view)"] -->|EnsureLayout| SCN
  CMD["editor: ui.layout, input.click"] -->|EnsureLayout| SCN
  MODE["editor: canvas mode"] -->|EnsureLayout| SCN
  subgraph SCN["GameUIScene (one per scene, handles only)"]
    CV["root canvases (hierarchy order)"] --> EL["elements: depth-first array"]
    EL --> LY["layouts: boxes per screen size"]
  end
  LY --> DRAW["drawing (ui/drawing)"]
  LY --> INP["input (ui/input)"]
```

The UI system asks for the screen the player sees, to route input. The UI render pass asks for the view it draws. The editor's `ui.layout` and `input.click` commands ask for a size a tool names, and the viewport's canvas mode asks for the Game view's screen. The scene holds at most four layouts per canvas, keyed by the canvas size in units, so a window changed to the same aspect ratio finds its layout waiting.

How a change to a component reaches the layout belongs to [the UI contract](../ui/contract.md).

## The contract

Callers and writers of components follow these rules.

- An entity is a :term[UI element]{id=ui-element} when it has a rectangle component and a root canvas is the entity or one of its ancestors. UI components outside a canvas, or without a rectangle, draw nothing, because every box comes from a rectangle.
- Coordinates are canvas units with +Y down and (0, 0) at the top left, like the mouse position. The world is the other way: its +Y is up, so a number copied from a transform to a UI rectangle is upside down.
- Boxes stay in canvas units and become pixels by one multiplication with the canvas's scale. The same layout then serves every window of one shape.
- Code that asks where an element is shown uses its visible box, which masks may cut. [UI input](../ui/input.md) uses this rule for hit tests.

:::rule[A new UI component goes in its module, and the scene holds handles]
A UI component is declared in `GameUIComponents.h` and requires the rectangle component, never in `Scene/Components.h`: the module can be removed, and a component without a rectangle draws nothing. `GameUIScene` holds handles, never `Ref` pointers or GPU objects, because scenes are released on background threads.
:::

## A toy version

The toy lays out one axis only. The idea carries over because Strata computes each axis alone: the x boxes of the whole tree, then the y boxes. A rectangle has five numbers per axis: two anchors, a pivot, a position and a size.

:::question
New to C++? The sketches use numbers, a `struct`, functions, references and calls such as `std::max(...)`: read [the first programming chapter](../basics/programming-1.md), [the second](../basics/programming-2.md) and [the third](../basics/programming-3.md) first.
:::

The first sketch computes the box of the Third-Person sample's menu panel on a 1920 by 1080 canvas. Search for the lines that find the two anchor points, the size and the pivot point; the numbers in `main` are the sample's own.

```cpp sketch="ui-layout-axis.cpp"
// One axis of a rect: anchors, pivot, position and size, the way the engine states its rect model.
#include <algorithm>
#include <cstdio>

struct AxisRect
{
	float AnchorMin, AnchorMax, Pivot, Position, Size;
};

void Anchored(float parentMin, float parentSize, const AxisRect& rect, float& outMin, float& outSize)
{
	const float anchor0 = parentMin + rect.AnchorMin * parentSize;
	const float anchor1 = parentMin + rect.AnchorMax * parentSize;
	outSize = std::max(anchor1 - anchor0 + rect.Size, 0.0f);
	const float pivotPoint = anchor0 + (anchor1 - anchor0) * rect.Pivot + rect.Position;
	outMin = pivotPoint - outSize * rect.Pivot;
}

int main()
{
	float x = 0.0f, width = 0.0f, y = 0.0f, height = 0.0f;
	Anchored(0.0f, 1920.0f, { 0.0f, 0.0f, 0.0f, 110.0f, 380.0f }, x, width);
	Anchored(0.0f, 1080.0f, { 0.5f, 0.5f, 0.5f, 90.0f, 400.0f }, y, height);
	std::printf("menu x=%.0f y=%.0f w=%.0f h=%.0f\n", x, y, width, height);
}
```

```text output-of="ui-layout-axis.cpp"
menu x=110 y=430 w=380 h=400
```

1. **Lines 12–13:** the two anchor points, fractions of the parent's length from its start.
2. **Lines 14–16:** the size adds to the span, and the pivot point decides where the box starts.
3. **Lines 22–23:** x anchors 0 and 0 pin the panel to the left edge, y anchors 0.5 and 0.5 to the middle line. Equal anchors have no span, so 380 and 400 are the panel's own size.

The second sketch stacks four buttons in the group that holds them; the main menu example further down computes the group's box that the sketch starts from. Each child gets its preferred height, one spacing below the last, starting at the group's top edge plus the padding.

```cpp sketch="ui-layout-stack.cpp"
// A vertical stack: children at their preferred heights, one spacing apart, inside the padding.
#include <cstdio>

int main()
{
	const float groupX = 140.0f, groupWidth = 320.0f; // The group's box from the anchored pass
	const float groupY = 466.0f;
	const float padding = 8.0f;
	const float spacing = 18.0f;
	const float preferred[] = { 64.0f, 64.0f, 64.0f, 64.0f };

	float y = groupY + padding;
	for (const float height : preferred)
	{
		// Stretched children take the padded width; the others keep their own.
		std::printf("button x=%.0f y=%.0f w=%.0f h=%.0f\n", groupX + padding, y, groupWidth - 2.0f * padding, height);
		y += height + spacing;
	}
	std::printf("block ends at y=%.0f\n", y - spacing);
}
```

```text output-of="ui-layout-stack.cpp"
button x=148 y=474 w=304 h=64
button x=148 y=556 w=304 h=64
button x=148 y=638 w=304 h=64
button x=148 y=720 w=304 h=64
block ends at y=784
```

1. **Line 12:** the stack starts at the top edge plus the padding.
2. **Lines 15–17:** stretched children take the padded width, 320 minus 16, so the buttons are 304 wide, not 320. After each child the position moves by its height and one spacing.

The buttons end at y = 784, inside a group that ends at 806. The real code differs from the toy in four ways. It runs x and y as two passes over the whole tree, asks each child for its preferred size, handles grids, alignment and fitted sizes, and repairs bad numbers.

## Coordinates and scale

The unit of layout is the **canvas unit**: one step of the canvas's own :term[coordinate space]{id=coordinate-space}, which becomes pixels through the canvas's scale. A canvas has no pixels of its own. Its elements live in a space of, for example, 1920 by 1080 units, and the screen decides how many pixels each unit covers. The axes are fixed: x grows to the right, y grows downward, and the origin is the top left corner. Colors are display (sRGB) colors.

The number that turns units into pixels is the **scale**: the pixels one canvas unit covers, written $s$ in the formulas. A canvas on a screen of $W \times H$ pixels covers $W / s$ by $H / s$ units. At the scale 2, a 100-unit button is 200 pixels wide, and the same screen holds half as many units.

The canvas component chooses how the scale is found with its scale mode. Three modes exist.

- **Constant Pixel Size:** the scale is the component's scale factor. A button of 304 units is 304 pixels on every screen. On a 3840-pixel monitor it covers 7.9 % of the width, where it covered 15.8 % of a 1920-pixel one: the mistake of a tiny UI at 4K.
- **Constant Physical Size:** the scale is the factor times the window's content scale, the ratio of its pixels to those of a 96-dots-per-inch display. A window on a display at 200 % has the content scale 2. [The windows and events page](../core/windows-events.md) shows where Strata reads that number.
- **Scale With Screen:** the canvas keeps the proportions of a design screen, and the scale follows the real screen.

The design screen of the last mode is the **reference resolution**: the screen size, in pixels, that the layout was designed for, 1920 by 1080 by default. A menu built at that size looks the same on a screen of 2560 by 1440, because the scale is 1.333 and the units still count 1920 by 1080.

A screen may have another shape than the design screen. The canvas has a **match width or height** value from 0 to 1: at 0 the scale follows the width ratio, at 1 the height ratio, and between them both count. The quote shows how.

```cpp src="Strata/src/Strata/GameUI/GameUIScene.cpp#L80-L104" symbol="GameUIScene::ComputeScale"
float GameUIScene::ComputeScale(const UICanvasComponent& canvas, const UIScreen& screen)
{
	const float factor = std::clamp(canvas.ScaleFactor, 0.01f, 100.0f);
	float scale = 1.0f;
	switch (canvas.ScaleMode)
	{
	case UICanvasScaleMode::ConstantPixelSize:
		scale = factor;
		break;
	case UICanvasScaleMode::ScaleWithScreen:
	{
		const glm::vec2 reference = glm::clamp(canvas.ReferenceResolution, glm::vec2(1.0f), glm::vec2(16384.0f));
		const glm::vec2 size = glm::max(screen.Size, glm::vec2(1.0f));
		const float match = std::clamp(canvas.MatchWidthOrHeight, 0.0f, 1.0f);
		const float logWidth = std::log2(size.x / reference.x);
		const float logHeight = std::log2(size.y / reference.y);
		scale = std::exp2(logWidth + (logHeight - logWidth) * match);
		break;
	}
	case UICanvasScaleMode::ConstantPhysicalSize:
		scale = std::max(screen.ContentScale, 0.01f) * factor;
		break;
	}
	return std::isfinite(scale) && scale > 0.0f ? scale : 1.0f;
}
```

1. **Lines 91–93:** the reference size, the screen and the match value are clamped, so a bad value cannot divide by zero.
2. **Lines 94–96:** `exp2` of an interpolated `log2` is the weighted geometric mean of the two ratios, not their ordinary average.
3. **Line 103:** a result that is not finite or not positive becomes 1 instead of spreading through the layout.

Apply it to a screen of 3840 by 540 pixels against 1920 by 1080, with the match value 0.5. The width ratio is 2, and its base-2 :term[logarithm]{id=logarithm} is 1. The height ratio is 0.5, and its logarithm is -1. Halfway between them is 0, and two to the power 0 is 1. The scale stays 1, and the canvas covers 3840 by 540 units.

At match 0 the scale would be 2, and at match 1 it would be 0.5.

The logarithms matter because a doubling and a halving are mirror images: their logarithms, 1 and -1, average to 0, which is the scale 1. The ordinary average of 2 and 0.5 is 1.25. That scale would grow the UI on a screen that has less room for it.

The **safe area** is the margin, in canvas units, that keeps UI away from the screen's edges, where a television or a phone's camera notch may cut the picture. The canvas keeps four insets: left, top, right and bottom. The root box is the screen in units minus the insets, never below zero. On a 1920 by 1080 canvas with the insets (48, 27, 48, 27), it starts at (48, 27) and measures 1824 by 1026.

:::example[One menu on three screens]
The Third-Person main menu has a root canvas on Scale With Screen with the reference 1920 by 1080 and the match 0.5.

| Screen in pixels | Width ratio | Height ratio | Scale | Size in units |
| --- | --- | --- | --- | --- |
| 1920 by 1080 | 1 | 1 | 1 | 1920 by 1080 |
| 2560 by 1440 | 1.333 | 1.333 | 1.333 | 1920 by 1080 |
| 2560 by 1080 | 1.333 | 1 | 1.155 | 2217 by 935 |

The first two rows have the same units, so the layout is identical and only the pixels change. On the wide screen half the logarithm of 1.333 is 0.2075, and two to the power 0.2075 is the scale 1.155. The menu's left edge still sits 110 units from the left, but the middle line of the screen is at 467.6 units and not at 540.
:::

## The rect

The rectangle component of an element places it in its parent's box. The engine states the model in a comment above the type.

```cpp src="Strata/src/Strata/GameUI/GameUIComponents.h#L74-L88"
// The rect of a UI element in its parent element's rect (the root rect for a canvas's children). Anchor points are
// A0 = parent.min + AnchorMin * parent.size and A1 = parent.min + AnchorMax * parent.size; the size is
// max(A1 - A0 + Size, 0) and the pivot point A0 + (A1 - A0) * Pivot + Position, around which the rect lies by Pivot.
// Point anchors with Size (200, 50) are a 200x50 rect; stretched anchors (0, 0)-(1, 1) with Size (-20, -20) inset the
// parent by 10. A parent with a UILayoutComponent places its children itself (unless IgnoreLayout).
struct UIRectComponent
{
	glm::vec2 AnchorMin = { 0.5f, 0.5f };
	glm::vec2 AnchorMax = { 0.5f, 0.5f };
	glm::vec2 Pivot = { 0.5f, 0.5f };
	glm::vec2 Position = { 0.0f, 0.0f }; // The pivot's offset from the anchor point, in canvas units
	glm::vec2 Size = { 100.0f, 100.0f }; // Added to the anchored span, in canvas units
	UIFitContent FitContent = UIFitContent::None; // The rect takes its content's size on these axes (its text, or its layout's children)
	bool IgnoreLayout = false; // A layout-group parent leaves it where its anchors put it
};
```

1. **Lines 74–78:** the whole model in five lines, with the two examples that this page computes by hand.
2. **Line 85:** the size is added to the anchored span; this one rule makes point and stretched anchors work.

A rectangle has two anchors: `AnchorMin` and `AnchorMax`, each a pair of fractions of the parent's box. On one axis, let $p$ be the parent's start and $L$ its length, $a_0$ and $a_1$ the two anchor fractions, $v$ the pivot fraction, $o$ the position and $z$ the size field. The engine finds:

$$A_0 = p + a_0 L, \qquad A_1 = p + a_1 L$$

Here $A_0$ and $A_1$ are the two anchor points, in canvas units.

$$\text{size} = \max(A_1 - A_0 + z,\ 0), \qquad P = A_0 + (A_1 - A_0)\,v + o, \qquad \text{start} = P - \text{size}\cdot v$$

Read $\max(x, 0)$ as "the larger of x and 0". Then $P$ is the pivot point, $\text{size}$ is the length of the box on that axis and $\text{start}$ is where the box begins.

The **pivot** is the point of the element that sits on the pivot point: a pair of fractions of the element's own size. The pair (0, 0) is its top left corner and (0.5, 0.5) its center. Growing the size keeps that point still.

- Point anchors, where the two anchors are equal: the span is 0, so the size field is the box's size. Point anchors with the size (200, 50) give a 200 by 50 box.
- Stretched anchors, where they differ: the span is the parent's length times the difference, and the size field adds to it. The anchors (0, 0) and (1, 1) with the size (-20, -20) give a box 20 units smaller than the parent on each axis.

A **margin** is the gap between an element's edge and its parent's edge on a stretched axis. The size field holds the sum of the two margins with its sign flipped. The size -20 leaves 10 on each side when the pivot is in the middle. The position moves the box and so changes how the 20 divides: a position of +10 gives a left margin of 20 and a right margin of 0.

:::caution
A stretched rectangle does not want its full width as size. A child of a 1920-unit parent with the anchors 0 and 1 and the size 1920 is 3840 wide, because the span already is 1920. On a stretched axis the size 0 fills the parent, and a negative size leaves margins.
:::

:::example[Two boxes by hand]
Take a canvas of 1920 by 1080 units. The first child has the anchors (0.5, 0.5), the pivot (0.5, 0.5), the position (10, -20) and the size (200, 50). On x: $A_0 = 960$, the pivot point is $960 + 10 = 970$, and the start is $970 - 100 = 870$. On y: $A_0 = 540$, the pivot point is 520, and the start is $520 - 25 = 495$. The box starts at (870, 495) and measures 200 by 50.

The second child has the anchors (0, 1) to (1, 1), the size (-40, 60), the pivot (0.5, 1) and the position (0, -8). On x: $A_0 = 0$, $A_1 = 1920$, the size is $1920 - 40 = 1880$, the pivot point is 960 and the start is 20. On y the anchors are equal, so the size is 60, the pivot point is $1080 - 8 = 1072$ and the start is $1072 - 60 = 1012$. A bar of 1880 by 60 sits at (20, 1012), with its bottom edge 8 units above the screen's.
:::

The Inspector's anchor presets are shortcuts for these numbers, as [the inspectors page](../editor-ui/inspectors.md) shows. Placing a heads-up display (HUD) with them is the work of [the HUD tutorial](../make/hud.md).

## The tree as an array

The elements of a canvas are not stored as a tree of nodes. A depth-first walk of the hierarchy writes them into one array, and each element keeps the index of its parent and the index where its descendants end.

**Depth-first order** visits a tree so that a node comes first and then each of its children's :term[subtrees]{id=subtree}, one after the other, from the first child to the last. [The trees and graphs chapter](../basics/trees-graphs.md) teaches the walk. In an array in this order every parent comes before its children, so the array is also the draw order: a later sibling covers an earlier one, and a child covers its parent.

The walk uses an explicit stack, not a function that calls itself, so a deep hierarchy cannot overflow the call stack. An entity becomes an element when it has a rectangle component; the canvas always does. An entity without one is skipped, but its children are still visited, and their parent is the nearest ancestor that is an element.

```cpp src="Strata/src/Strata/GameUI/GameUIScene.cpp#L568-L592" from="stack.clear();" to="std::reverse(stack.begin() + static_cast<std::ptrdiff_t>(first), stack.end());" symbol="GameUIScene::RebuildCanvas"
stack.clear();
stack.push_back({ canvas.Entity, c_NoElement });
while (!stack.empty())
{
	const WalkFrame frame = stack.back();
	stack.pop_back();
	uint32_t parentElement = frame.ParentElement;
	const bool isElement = frame.Entity == canvas.Entity || m_Registry->all_of<UIRectComponent>(frame.Entity);
	if (isElement)
	{
		const uint32_t index = static_cast<uint32_t>(canvas.Elements.size());
		Element& element = canvas.Elements.emplace_back();
		element.Entity = frame.Entity;
		element.Parent = frame.ParentElement;
		element.RaycastTarget = ComputeRaycastTarget(frame.Entity);
		const WorldTransformComponent* world = m_Registry->try_get<WorldTransformComponent>(frame.Entity);
		element.Active = !world || world->ActiveInHierarchy;
		parentElement = index;
	}
	// Children pushed in reverse, so the first child is walked first.
	const HierarchyComponent& hierarchy = m_Registry->get<HierarchyComponent>(frame.Entity);
	const size_t first = stack.size();
	for (entt::entity child = hierarchy.FirstChild; child != entt::null; child = m_Registry->get<HierarchyComponent>(child).NextSibling)
		stack.push_back({ child, parentElement });
	std::reverse(stack.begin() + static_cast<std::ptrdiff_t>(first), stack.end());
```

1. **Line 581:** the element's `Parent` is the frame's parent element, so the array stores a tree without pointers.
2. **Lines 587–592:** children are pushed in reverse, so the stack pops the first child first.

The **subtree range** of an element is the half-open range of indices from the element itself to one past its last descendant, written $[i, \text{end})$. Every element stores its end, and its descendants are exactly the elements in that range. A walk over the children of a group jumps from child to child with the end of each, and a test "is this index inside that subtree" is two comparisons.

The ends are found back to front. Each element starts with an end one past itself, and going backwards each element raises its parent's end to its own.

```cpp src="Strata/src/Strata/GameUI/GameUIScene.cpp#L595-L602" from="const uint32_t count = static_cast<uint32_t>(canvas.Elements.size());" to="canvas.Elements[element.Parent].SubtreeEnd = std::max(canvas.Elements[element.Parent].SubtreeEnd, element.SubtreeEnd);" symbol="GameUIScene::RebuildCanvas"
const uint32_t count = static_cast<uint32_t>(canvas.Elements.size());
for (uint32_t index = count; index-- > 0;)
{
	Element& element = canvas.Elements[index];
	if (element.SubtreeEnd < index + 1)
		element.SubtreeEnd = index + 1;
	if (element.Parent != c_NoElement)
		canvas.Elements[element.Parent].SubtreeEnd = std::max(canvas.Elements[element.Parent].SubtreeEnd, element.SubtreeEnd);
```

The last descendant of a parent is the last element to raise its end, so the parent's end is the largest.

:::example[A menu as an array]
A canvas holds a Title and a Menu, and the Menu holds a group Buttons with two buttons, each with a label. The walk writes eight elements.

| Index | Element | Parent | Subtree range |
| --- | --- | --- | --- |
| 0 | canvas | none | [0, 8) |
| 1 | Title | 0 | [1, 2) |
| 2 | Menu | 0 | [2, 8) |
| 3 | Buttons | 2 | [3, 8) |
| 4 | Play | 3 | [4, 6) |
| 5 | Play label | 4 | [5, 6) |
| 6 | Quit | 3 | [6, 8) |
| 7 | Quit label | 6 | [7, 8) |

Going backwards, element 7 raises the end of its parent 6 to 8, element 6 raises that of 3 to 8, and so on up to the canvas. The children of Buttons are found by starting at index 4 and jumping to the end of its range, 6, which is the next child.
:::

The **sort order** is a whole number on a root canvas that decides which canvas draws on top: a higher number draws later and so covers lower ones, and equal numbers keep hierarchy order. Only root canvases have one. Inside a canvas the hierarchy order is the draw order.

Widgets name their parts by universally unique identifier (UUID), and the scene resolves each to an element of the same canvas. A slider's fill and handle count only when they come after the slider in array order. A part that is the slider itself or one of its ancestors would move what places it, so the scene ignores it.

## Two passes

A layout group needs the sizes of its children before it can place them, and a child's box needs its parent's box. The two needs point in opposite directions. Strata therefore runs each axis in two parts: sizes go up the tree, then boxes go down it.

**Measure** is the question a parent asks a child: how large do you want to be along this axis? Arrange is the answer in the other direction: the parent tells the child its box.

The **preferred size** of an element on an axis is the length it asks for: its content size when it fits its content on that axis, and otherwise the size field of its rectangle. The sizes are found bottom up, and each is remembered when found, so a child that two callers ask is measured once.

The two axes do not run together. The width pass covers the whole subtree, and then the height pass does. The reason is text: a text that wraps has a height that depends on the width it is given. The height of a label is known only after the width pass has placed the label. If heights came first, the label would have no width to wrap at.

The driver is short. It clears the tables for the range of elements it will lay out, and it runs one axis at a time.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L202-L214" symbol="GameUIScene::LayOutSubtree"
void GameUIScene::LayOutSubtree(const Canvas& canvas, Layout& layout, uint32_t root, std::vector<UIBox>& boxes)
{
	const uint32_t count = canvas.Elements[root].SubtreeEnd - root;
	m_PreferredMemo.assign(count, 0.0f);
	m_PlacedPosition.assign(count, 0.0f);
	m_PlacedSize.assign(count, 0.0f);
	for (int axis = 0; axis < 2; axis++)
	{
		m_PreferredKnown.assign(count, 0);
		m_Placed.assign(count, 0);
		LayOutAxis(canvas, layout, root, axis, boxes);
	}
}
```

1. **Lines 205–207:** the tables for the whole range are cleared once.
2. **Lines 210–212:** the tables of one axis are cleared before the axis runs, so no width leaks into the height pass.

The function that lays out one axis walks the array in order, which gives parents before children. For each element it finds a start and a size, in one of three cases. The canvas takes the root box. A child that its parent's group has placed takes the group's answer. Every other element is anchored in its parent's box.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L222-L244" from="float position = 0.0f;" to="float anchorMax = values.AnchorMax[axis];" symbol="GameUIScene::LayOutAxis"
float position = 0.0f;
float size = 0.0f;
if (element == 0)
{
	// The canvas: the root rect.
	const UIBox rootBox = GetRootBox(canvas, layout.UnitSize);
	position = rootBox.Min[axis];
	size = rootBox.Size[axis];
}
else if (element != root && m_Placed[element - root])
{
	position = m_PlacedPosition[element - root];
	size = m_PlacedSize[element - root];
}
else
{
	// Anchored in the parent's box.
	const UIBox& parent = boxes[data.Parent];
	const UIRectComponent* rect = m_Registry->try_get<UIRectComponent>(data.Entity);
	const UIRectComponent defaults;
	const UIRectComponent& values = rect ? *rect : defaults;
	float anchorMin = values.AnchorMin[axis];
	float anchorMax = values.AnchorMax[axis];
```

1. **Lines 224–229:** the canvas, element 0, takes the root box of the safe area.
2. **Lines 231–235:** the group stored this child's position and size when its own box became known, so the answer waits.
3. **Line 239:** the parent's box is ready, because parents come before their children.

Only the anchored case computes the rectangle model. The second piece of the function holds the formula in code, the repair of bad numbers and the call that lets a group place its children.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L264-L283" from="const float anchor0 = parent.Min[axis] + anchorMin * parent.Size[axis];" to="PlaceGroupChildren(canvas, layout, root, element, axis, boxes);" symbol="GameUIScene::LayOutAxis"
	const float anchor0 = parent.Min[axis] + anchorMin * parent.Size[axis];
	const float anchor1 = parent.Min[axis] + anchorMax * parent.Size[axis];
	if (FitsAxis(values.FitContent, axis))
		size = std::max(GetContentSize(canvas, layout, root, element, axis, boxes), 0.0f);
	else
		size = std::max(anchor1 - anchor0 + values.Size[axis], 0.0f);
	const float pivotPoint = anchor0 + (anchor1 - anchor0) * values.Pivot[axis] + values.Position[axis];
	position = pivotPoint - size * values.Pivot[axis];
}
if (!std::isfinite(position) || !std::isfinite(size))
{
	position = 0.0f;
	size = 0.0f;
}
boxes[element].Min[axis] = position;
boxes[element].Size[axis] = size;

// A layout group places its children once its own box is known on this axis.
if (m_Registry->all_of<UILayoutComponent>(data.Entity))
	PlaceGroupChildren(canvas, layout, root, element, axis, boxes);
```

1. **Lines 266–271:** the size, the pivot point and the start: the formula of the previous section. A fitted axis takes the content size instead of the span plus the size.
2. **Lines 273–277:** a position or size that is not finite becomes 0, so a bad number cannot reach the children.
3. **Lines 281–283:** once its own box is known on this axis, a layout group places its children.

:::example[A label that wraps]
A group has padding 10 on every side, spacing 10 and stretched children, and it fits its height. Its rectangle has the size (320, 0). It holds a wrapping label that fits its height, with the font size 20, and a button of the size (100, 64). Suppose that at the width 300 units, which is 15 em at this font size, the text takes two lines of 1.2 em. The line height is an invented number; [the text page](../ui/text.md) teaches shaping.

Width pass: the group is 320 wide. Across the stack, stretched children take the padded width, $320 - 20 = 300$, so the label's width is known.

Height pass: the group asks for its content height. The button prefers 64. The label's preferred height is its text at the width it has: $2.4 \times 20 = 48$. The content is $48 + 64 + 10 = 122$, so the group is $122 + 20 = 142$ high. The stack puts the label at the group's top plus 10 and the button at the top plus 68.
:::

## Groups, grids and fit content

A **layout group** is an element with a layout component: it places its active children itself, in sibling order, instead of leaving each to its anchors. It stacks them vertically or horizontally, or fills a grid of fixed cells. A child with `IgnoreLayout` set keeps the place its own anchors give it.

The mistake that costs an hour: a child's anchors, position and size field do nothing under a group, because the group replaces its box. Only the preferred size of the child is read. Set `IgnoreLayout` on the child if its anchors must count.

A stack measures each placed child, adds the spacings between them, and starts the block at the padded box's start plus the free space times the alignment, which is 0, 0.5 or 1.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L335-L353" from="const int mainAxis = settings.Type == UILayoutType::Horizontal ? 0 : 1;" to="position += size + spacing;" symbol="GameUIScene::PlaceGroupChildren"
const int mainAxis = settings.Type == UILayoutType::Horizontal ? 0 : 1;
if (axis == mainAxis)
{
	// Stacked at their preferred sizes, the block aligned in the padded rect.
	float block = 0.0f;
	for (uint32_t child = group + 1; child < end; child = canvas.Elements[child].SubtreeEnd)
	{
		if (IsPlacedByGroup(canvas, child))
			block += std::max(GetPreferredSize(canvas, layout, root, child, axis, boxes), 0.0f);
	}
	block += spacing * static_cast<float>(placedCount - 1);
	float position = innerStart + (innerSize - block) * alignment;
	for (uint32_t child = group + 1; child < end; child = canvas.Elements[child].SubtreeEnd)
	{
		if (!IsPlacedByGroup(canvas, child))
			continue;
		const float size = std::max(GetPreferredSize(canvas, layout, root, child, axis, boxes), 0.0f);
		place(child, position, size);
		position += size + spacing;
```

1. **Lines 340–345:** the block is every placed child at its preferred size plus the spacings between them.
2. **Line 346:** the free space, which may be negative, is shared by the alignment: 0 puts the block at the start, 1 at the end.
3. **Lines 351–353:** each child gets its preferred size, and the position moves by the size and the spacing.

The nine alignment names reduce to two numbers. Count the value from `TopLeft` as 0: the x step is the remainder of dividing by 3, the y step is the result of the division rounded down, and each step is multiplied by 0.5. `TopCenter` is 1, so x is 0.5 and y is 0. `MiddleRight` is 5, so x is 1 and y is 0.5.

Across the stack, a child takes the padded length when the group stretches its children, and its preferred size otherwise. Then it is aligned in the padded box. On the Third-Person menu the buttons have the size 320 and the group stretches them, so they come out 304 wide: stretching beats the size field.

A group never shrinks its children. If their preferred sizes add up to more than the box, the block overflows it: the free space is negative, and the alignment moves the block. A flexible box layout would shrink the children instead.

:::example[The main menu's buttons]
The Third-Person main menu has a root canvas on Scale With Screen, 1920 by 1080, so the scale is 1 on a 1920 by 1080 screen. Its panel Menu has the anchors (0, 0.5), the pivot (0, 0.5), the position (110, 90) and the size (380, 400). The group Buttons inside it has the anchors (0.5, 0), the pivot (0.5, 0), the position (0, 36) and the size (320, 340). It is vertical, with padding 8, spacing 18, stretch on and the alignment `TopCenter`. It holds four buttons of the size (320, 64), named `Play`, `SettingsOpen`, `Credits` and `Quit` in the sample.

Menu: on x, $A_0 = 0$, the pivot point is 110, the start is 110. On y, $A_0 = 540$, the pivot point is 630, the start is $630 - 200 = 430$. The box is at (110, 430) with the size 380 by 400.

Buttons: on x, $A_0 = 110 + 190 = 300$, the start is $300 - 160 = 140$. On y, $A_0 = 430$, the pivot point is 466 and the start is 466, because the pivot is 0. The box is at (140, 466) with the size 320 by 340.

Width pass for the four buttons: the padded width is $320 - 16 = 304$, and they stretch, so each starts at $140 + 8 = 148$ and is 304 wide. Height pass: the block is $4 \times 64 + 3 \times 18 = 310$, and the padded height is $340 - 16 = 324$. The alignment is 0 on y, so the block starts at $466 + 8 = 474$, and the buttons start at y = 474, 556, 638 and 720.

The label of Play has the anchors (0, 0) to (1, 1) and the size (0, 0), so it fills its button: (148, 474) with the size 304 by 64. The toy sketches printed the same numbers.
:::

A **grid** places children in rows of equal cells. Its settings are the cell size, the spacing and the number of columns, where 0 asks for as many columns as the width holds. That count is $\lfloor (w + s) / (c + s) \rfloor$, at least 1, for the padded width $w$, the cell width $c$ and the column spacing $s$. Read $\lfloor x \rfloor$ as "x rounded down".

With a width of 350, a cell of 100 and a spacing of 10, the count is $\lfloor 360 / 110 \rfloor = 3$, so seven children fill 3 rows. The block of cells is aligned in the padded box like a stack.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L316-L330" from="const uint32_t columns = GetGridColumns(settings, innerWidth, placedCount);" to="index++;" symbol="GameUIScene::PlaceGroupChildren"
const uint32_t columns = GetGridColumns(settings, innerWidth, placedCount);
const uint32_t usedColumns = std::min(columns, placedCount);
const uint32_t rows = (placedCount + columns - 1) / columns;
const float cell = std::max(settings.CellSize[axis], 1.0f);
const uint32_t cellsAlong = axis == 0 ? usedColumns : rows;
const float block = static_cast<float>(cellsAlong) * cell + static_cast<float>(cellsAlong - 1) * spacing;
const float start = innerStart + (innerSize - block) * alignment;
uint32_t index = 0;
for (uint32_t child = group + 1; child < end; child = canvas.Elements[child].SubtreeEnd)
{
	if (!IsPlacedByGroup(canvas, child))
		continue;
	const uint32_t cellIndex = axis == 0 ? index % columns : index / columns;
	place(child, start + static_cast<float>(cellIndex) * (cell + spacing), cell);
	index++;
```

1. **Lines 316–322:** the column count, the rows and the size of the block of cells, which the alignment places in the padded box.
2. **Lines 328–330:** child $i$ takes column $i \bmod \text{columns}$ and row $\lfloor i / \text{columns} \rfloor$, and every cell has the cell size.

**Fit content** is the setting that makes a rectangle take its size from its content on the chosen axes: the width, the height or both. The content of a text is the text, and the content of a layout group is its children plus the padding. The preferred size of an element asks for it.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L369-L384" symbol="GameUIScene::GetPreferredSize"
float GameUIScene::GetPreferredSize(const Canvas& canvas, Layout& layout, uint32_t root, uint32_t element, int axis, const std::vector<UIBox>& boxes)
{
	const uint32_t slot = element - root;
	if (m_PreferredKnown[slot])
		return m_PreferredMemo[slot];
	const UIRectComponent* rect = m_Registry->try_get<UIRectComponent>(canvas.Elements[element].Entity);
	float size = 0.0f;
	if (rect && FitsAxis(rect->FitContent, axis))
		size = GetContentSize(canvas, layout, root, element, axis, boxes);
	else
		size = rect ? rect->Size[axis] : 0.0f;
	size = std::isfinite(size) ? std::max(size, 0.0f) : 0.0f;
	m_PreferredMemo[slot] = size;
	m_PreferredKnown[slot] = 1;
	return size;
}
```

1. **Lines 372–373:** the memo: a size is found once per axis.
2. **Lines 376–379:** an element that fits its content on this axis asks its content, and any other asks its size field.
3. **Line 380:** a size that is not finite becomes 0, and a negative one becomes 0.

The text module shapes a text; here only two rules matter. A width is the text on one line. A height is the text's at the width the element has, and the wrapping applies only when the text wraps and the element does not fit its width.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L394-L403" from="const float fontSize = std::clamp(text->FontSize, 1.0f, 1024.0f);" to="return (axis == 0 ? shaped.Width : shaped.Height) * fontSize;" symbol="GameUIScene::GetContentSize"
const float fontSize = std::clamp(text->FontSize, 1.0f, 1024.0f);
const UIRectComponent* rect = m_Registry->try_get<UIRectComponent>(entity);
const bool fitsWidth = rect && FitsAxis(rect->FitContent, 0);
const bool fieldText = canvas.Elements[element].FieldTextOf != c_NoElement;
const float wrapWidth = axis == 1 && text->Wrap && !fitsWidth && !fieldText ? boxes[element].Size.x / fontSize : 0.0f;
TextShapeOptions options = GetMeasureOptions(*text, wrapWidth);
if (fieldText)
	options.Overflow = TextOverflowMode::Overflow; // As GetElementShapeOptions shapes a field's line
const ShapedText& shaped = ShapeElementText(layout, element, *text, GetShownText(canvas, element, *text), options);
return (axis == 0 ? shaped.Width : shaped.Height) * fontSize;
```

1. **Line 398:** the wrap width is the box's width in em, on the height axis only: the width pass has already run.
2. **Line 403:** the shaped size is in em, so the font size scales it into canvas units.

The content of a group follows the measure rule. On the stacking axis it is the sum of the children's preferred sizes plus the spacings; across it, the largest child; for a grid, the cells. A group with no placed children asks for its padding alone.

## Slider parts, bad numbers and clips

A slider's fill and handle are ordinary elements whose anchors the layout replaces. On the slider's axis the fill spans from the start to the value and the handle sits at the value; a slider that runs the other way uses $1 - v$. The other axis keeps the anchors of the part.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L245-L260" from="if (data.SliderOf != c_NoElement)" to="anchorMax = reversed ? 1.0f : fraction;" symbol="GameUIScene::LayOutAxis"
if (data.SliderOf != c_NoElement)
{
	// A slider's fill spans from the slider's start to its value along its direction, its handle sits at the value.
	const UISliderComponent* slider = m_Registry->try_get<UISliderComponent>(canvas.Elements[data.SliderOf].Entity);
	if (slider && GetDirectionAxis(slider->Direction) == axis)
	{
		const float fraction = GetSliderFraction(*slider);
		const bool reversed = IsReversed(slider->Direction);
		if (data.SliderHandle)
		{
			anchorMin = anchorMax = reversed ? 1.0f - fraction : fraction;
		}
		else
		{
			anchorMin = reversed ? 1.0f - fraction : 0.0f;
			anchorMax = reversed ? 1.0f : fraction;
```

1. **Lines 253–256:** a handle's two anchors are one point, the value, so its own size field gives its size.
2. **Lines 257–260:** a fill's anchors run from the start to the value.

The Third-Person settings panel has a slider whose size field says 400, but its group stretches it to 384 units, the padded width. Its fill is anchored (0, 0) to (1, 1), and its handle has the size (18, 32). At the value 0.25 the fill's x anchors become 0 and 0.25, so the fill is 96 units wide. The handle's two anchors become 0.25, so its center is 96 units from the slider's left edge and it covers 87 to 105.

A position or a size that is not finite, such as the result of a division by zero, becomes 0 in the axis function, and the preferred size has its own guard. The box is then empty, and its neighbors are not affected.

A **clip rect** is the rectangle that a mask component cuts its descendants to: the mask's box inset by the mask's padding, met with the clip rects of the masks above it. Outside it, nothing is drawn or hit by the pointer. Masks nest, so a descendant of two shows only where both overlap.

```cpp src="Strata/src/Strata/GameUI/GameUILayout.cpp#L187-L197" from="glm::vec2 min = box.Min + glm::vec2(padding.x, padding.y);" to="outClips[slot].Rect = glm::vec4(min, max);" symbol="GameUIScene::ComputeClips"
glm::vec2 min = box.Min + glm::vec2(padding.x, padding.y);
glm::vec2 max = box.GetMax() - glm::vec2(padding.z, padding.w);
// Within the clip rect of the masks above it (their slots come first).
const uint32_t outer = canvas.Elements[element].Clip;
if (outer != 0 && outer - 1 < slot)
{
	const glm::vec4& rect = outClips[outer - 1].Rect;
	min = glm::max(min, glm::vec2(rect.x, rect.y));
	max = glm::min(max, glm::vec2(rect.z, rect.w));
}
outClips[slot].Rect = glm::vec4(min, max);
```

1. **Lines 189–196:** the clip rect of the mask above is already computed, because its slot comes first, and it narrows this one.
2. **Line 197:** the result is stored for the drawing pass and for hit tests.

Clip rects are found again only when a box under a mask moved or changed size, or a mask changed. [The drawing page](../ui/drawing.md) teaches how pixels are cut to them, and [the input page](../ui/input.md) what the pointer hits inside.

Other code reads the result through queries on a view of a root canvas. They give the element count, an element's entity, its box in canvas units, the end of its subtree, whether it is visible and whether the pointer can hit it. They also give its clip, its visible box (what the masks leave of its box) and, through `FindElement`, the view and element of an entity.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Absolute pixel positions | Small tools and first prototypes | No layout code at all | A UI that breaks on every screen except the tested one |
| A constraint solver | Apple's Auto Layout | Relations between any two elements, such as aligned edges | A solver in every frame, and conflict errors that a game maker cannot read |
| Flexible boxes | Web browsers, Yoga in React Native | Children that grow and shrink by weight | A long rule list, and boxes that are hard to compute by hand |
| One pass for both axes | Simple stack panels | Less code, one walk | Wrapped text whose height needs its width |
| A layout repeated every frame | Immediate-mode UI such as :term[ImGui]{id=dear-imgui} | No stored boxes | Work for every element every frame, and no cache that keeps idle frames free |

## How it is tested

The suites of `StrataTests/src/GameUI/GameUILayoutTests.cpp` need no GPU. `GameUI.Layout` checks rectangles against exact boxes on four screens, the safe area, stacks with every alignment, groups that skip inactive children, grids, fitted sizes, slider parts and nested canvases. `GameUI.Scale` checks the three scale modes over screens, match values and content scales against the formula of this page. `GameUI.Mask` checks clip rects, nested masks and hit tests. The suite `GameUI.Dirty` belongs to [the UI contract](../ui/contract.md).

The GPU test `The Tetris HUD covers the same fraction of the screen at 1280x720 and 2560x1440`, in the suite `GPU.GameUI`, renders the HUD of the Tetris sample at both sizes. It checks that its lit pixels cover the same box within 1 % of the screen. A HUD of fixed pixel sizes would cover half the fraction at the larger size. Run the layout suites with `StrataTests.exe --test-suite=GameUI*`; the GPU test needs a machine with a GPU.

## Changing it safely

- A new UI component goes in `GameUIComponents.h` and requires the rectangle component, as the rule above says. A component that changes a box, such as a new layout mode, adds its case to both the measure and the arrange code.
- Keep measure and arrange in step. `PlaceGroupChildren` and `GetGroupContentSize` compute the same block of children twice: once to place it, once to size the group that fits it. A change to one, such as a new spacing rule, changes the other, and a layout test checks that a fitted group has the size its children need.
- Never read a box before its axis is laid out. A function that needs a width, as the text height does, runs in the height pass.
- Hold handles, not `Ref` pointers, in the scene, which a background thread may release.
- After a change, run the three layout suites. Debug builds also check the cached layout each time they list the canvases for a screen.

## Summary

- A box is computed per axis: the anchor points are fractions of the parent's box, the size is added to their span, and the pivot and the position place the result.
- A canvas keeps its scale by interpolating the logarithms of the two screen ratios, so a screen twice as wide and half as tall keeps the scale 1.
- Each axis runs sizes bottom up and boxes top down, and the width pass runs before the height pass because a wrapped text's height depends on its width.
- The layout lives in `GameUILayout.cpp` (passes, groups, fit content), `GameUIScene.cpp` (scale, element array) and `GameUIComponents.h` (the rectangle model).

## Check yourself

1. A canvas has the reference resolution 1920 by 1080 and the match value 1. What is its scale on a screen of 1280 by 540, and how many canvas units high is the screen?

   :::answer{tests="compute-box,scale-log"}
   Match 1 follows the height: the scale is 540 / 1080 = 0.5, and the screen is 540 / 0.5 = 1080 units high. The width ratio is not used.
   :::

2. A child of a 1000-unit-wide parent has the anchors 0 and 1 on x and the size 1000. How wide is the child, and which size makes it fill the parent?

   :::answer{tests="compute-box"}
   The child is 2000 wide: the span 1000 plus the size 1000. The size 0 fills the parent, and the size -40 leaves 20 on each side with a centered pivot.
   :::

3. Why does Strata lay out all widths of a subtree before any height?

   - A. Because widths are cheaper to compute than heights.
   - B. Because the height of a wrapped text depends on the width the text has.
   - C. Because a group stacks its children along x first.

   :::answer{tests="two-passes"}
   B. A is false: neither pass is cheaper by design. C is false: a vertical group stacks along y. A wrapped label asks for its preferred height at the width it has, and that width is known only after the width pass.
   :::

4. Which function explains why a button inside a group is 304 units wide when its size field says 320?

   :::answer{tests="find-code"}
   `GameUIScene::PlaceGroupChildren` in `GameUILayout.cpp`. On the axis across the stack, a group that stretches its children gives each the padded length, here $320 - 2 \times 8 = 304$.
   :::

## Exercises

1. **Basic.** The Third-Person settings panel has the anchors (0, 0.5), the pivot (0, 0.5), the position (520, 90) and the size (460, 618). Find its box on a 1920 by 1080 screen with the scale 1.

   :::answer[Worked solution]{tests="compute-box"}
   On x: $A_0 = 0$, the pivot point is 520, the start is 520. On y: $A_0 = 540$, the pivot point is 630, the start is $630 - 309 = 321$. The box starts at (520, 321) and measures 460 by 618.
   :::

2. **Medium.** Trace it yourself: put breakpoints in `LayOutAxis` and `GetPreferredSize` while the Third-Person main menu is laid out. Find where the width and the height of the Play button are found.

   :::answer[Worked solution]{tests="two-passes,find-code"}
   Both are in `Strata/src/Strata/GameUI/GameUILayout.cpp`. `LayOutSubtree` runs `LayOutAxis` for x and then for y. In the x pass, `PlaceGroupChildren` of the Buttons group stores the width 304 for each button before the walk reaches it. In the y pass, `GetPreferredSize` runs once per button and the answer is remembered, and `PlaceGroupChildren` places the four buttons at 474, 556, 638 and 720.
   :::

3. **Hard.** Place seven cells of 100 by 100 in a grid with the column spacing 10 and the row spacing 20 in a width of 350. Write a program that prints the column count, the rows and the start of each cell.

   :::answer[Worked solution]{tests="compute-box,two-passes" solution="sketches/ui-layout-grid.cpp"}
   The column count is $\lfloor 360 / 110 \rfloor = 3$, so there are 3 rows. Cell $i$ takes column $i \bmod 3$ and row $\lfloor i / 3 \rfloor$, and each step along y is the cell plus the row spacing, 120.

   ```cpp sketch="ui-layout-grid.cpp"
   // A grid: as many columns as the width holds, fixed cells, and a row spacing that differs from the column spacing.
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   int main()
   {
   	const float width = 350.0f;
   	const float cell = 100.0f;
   	const float spacingX = 10.0f;
   	const float spacingY = 20.0f;
   	const int children = 7;

   	const int columns = std::max(1, static_cast<int>(std::floor((width + spacingX) / (cell + spacingX) + 1e-4f)));
   	std::printf("columns=%d rows=%d\n", columns, (children + columns - 1) / columns);
   	for (int index = 0; index < children; index++)
   	{
   		const float x = static_cast<float>(index % columns) * (cell + spacingX);
   		const float y = static_cast<float>(index / columns) * (cell + spacingY);
   		std::printf("cell %d at x=%.0f y=%.0f\n", index, x, y);
   	}
   }
   ```

   ```text output-of="ui-layout-grid.cpp"
   columns=3 rows=3
   cell 0 at x=0 y=0
   cell 1 at x=110 y=0
   cell 2 at x=220 y=0
   cell 3 at x=0 y=120
   cell 4 at x=110 y=120
   cell 5 at x=220 y=120
   cell 6 at x=0 y=240
   ```

   1. **Line 14:** the column count, as the engine finds it.
   2. **Lines 18–19:** the column spacing steps along x and the row spacing along y.
   :::

## Where it lives in Strata

- The rectangle model: `Strata/src/Strata/GameUI/GameUIComponents.h` (`UIRectComponent`, `UICanvasComponent`, `UILayoutComponent`, `UIMaskComponent`).
- Scale, element array and queries: `Strata/src/Strata/GameUI/GameUIScene.cpp`, `GameUIScene.h`, `GameUISceneData.h`.
- The passes, groups, grids, fit content and clips: `Strata/src/Strata/GameUI/GameUILayout.cpp`.
- Tests: `StrataTests/src/GameUI/GameUILayoutTests.cpp` (`GameUI.Layout`, `GameUI.Scale`, `GameUI.Mask`) and the Tetris HUD test in `StrataTests/src/Renderer/GPUGameUITests.cpp`.
- Command: `ui.layout` returns the boxes of the elements for a screen size.

## Further reading

- Unity manual, "Basic Layout" (beginner): anchors and pivots of a rect transform in a widely used editor.
- Unreal Engine documentation, UMG "Anchors" (beginner): the same idea with presets.
- Badros, Borning and Stuckey, "The Cassowary linear arithmetic constraint solving algorithm" (advanced): the solver behind Auto Layout.
- Yoga documentation (intermediate): the flexible box rules that a game UI would need to implement.
- Microsoft, "Layout" overview of WPF (intermediate): measure and arrange as a pair of passes.
- Flutter documentation, "Understanding constraints" (beginner): constraints go down, sizes go up, the parent sets the position.
