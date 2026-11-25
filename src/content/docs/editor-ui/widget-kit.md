---
id: editor-ui/widget-kit
title: "The widget kit"
description: "How Strata's editor draws its own controls on ImGui, why a chip strip decides its layout one frame late, and how the item probe lets tests find widgets."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/design-system]
time: 75
learn:
  - id: anatomy
    text: explain the steps a kit widget takes to behave as an ImGui item while drawing its own look
  - id: vivid
    text: explain why a disabled button that shows a state is drawn with colors that skip the fade
  - id: two-frames
    text: trace how a chip strip decides from the previous frame which chips become icons and where rows wrap
  - id: probe
    text: explain what the item probe records, what it costs and how it flags an id used twice
  - id: write-widget
    text: write a new kit widget with probe keys and a test that clicks it
since: 0.3.0
status: final
---

The controls of the editor's user interface (UI) come from one library, the **widget kit** (`StrataEditor/src/UI/Widgets.h`): buttons, chips, pills, cards, dialogs and a few dozen more. Each takes its size from the :term[font]{id=font}, takes its colors from the theme and writes its place into a table that tests read. This page teaches how such a widget is built on an immediate-mode library, using three pieces of real code: the button, the strip of chips and the table of rectangles.

This page does not teach how tests click widgets, what the status bar's pills say, what each chip of the Scene view does, or how a :term[modal]{id=modal} asks the person a question. Other pages of the editor part teach those, and this page links them.

## The problem and how engines solve it

:term[ImGui]{id=dear-imgui}, the library under the editor, gives you buttons, text fields and menus. Draw one and you get a rectangle with ImGui's own look, sized by ImGui's own style numbers.

The editor needs more. A toolbar button has an icon and a label, an accent fill while its mode is on, and a rounded shape. A chip floats over the picture of the scene. A status pill is tinted with the color of its message.

There are three ways to get such controls. The first is to change the look of ImGui's widgets through its style stack: push colors and sizes, call the stock widget, pop them again. This works for colors and fails for shape and layout, since the stock button cannot hold an icon and a label of two colors.

The second is to write a widget as a function that does the arithmetic by hand: read the mouse, compare it with a rectangle, remember who was pressed. It gives every freedom, but it loses what ImGui does for free: item identity, keyboard navigation, disabled fading, clipping, the tooltip delay and the order in which overlapping items win the mouse.

The third, Strata's choice, is a hybrid. The widget reserves a real ImGui item, so all of that work stays, and then draws its own look over the item with the window's draw list. A draw list is the list of shapes ImGui paints for that window.

:::why
A stock widget with a new look cannot change its shape, and a hand-written one must rebuild ImGui's rules. The hybrid costs a little more code per widget, a few dozen lines, and it keeps every item behaving as the rest of the editor expects. Its other cost is discipline: ImGui no longer draws the widget, so the widget must remember each part of the look itself, such as the keyboard focus ring.
:::

A second need comes from tests. A test that wants to press **Play** must know where the button is on the screen. ImGui keeps no list of items by name. Strata therefore adds one: each kit widget writes down its rectangle when it draws. This is the item probe, and it is the third piece of this page.

## The anatomy of a kit widget

Start with the button, since every other widget repeats its steps. Seven things happen, in order. The widget reserves an item, reads whether the mouse is over it and whether it is held, and picks colors from the theme. Then it draws, renders the keyboard cursor, shows the tooltip and records the item in the probe.

```mermaid caption="A kit widget reserves an item first, then reads its states, draws on the window's draw list and last records itself. Every arrow leads to the next step in the same frame." alt="Seven boxes in a row: reserve the item, read hovered and held, pick theme colors, draw background icon and label, render the navigation cursor, show the tooltip, record in the item probe."
flowchart LR
    A[Reserve item] --> B[Read hovered and held]
    B --> C[Pick theme colors]
    C --> D[Draw fill, icon, label]
    D --> E[Render nav cursor]
    E --> F[Show tooltip]
    F --> G[Record in probe]
```

The first step uses an **InvisibleButton**, an ImGui item that has a size and answers the mouse and the keyboard but draws nothing. ImGui treats it as a real item. It has an identity, it can be hovered, pressed and reached with the arrow keys, and it returns true in the frame where the person releases the mouse over it. Everything the stock button does apart from drawing is therefore available, and the widget fills the empty rectangle with whatever look it wants.

You now know enough to write one. The sketch below is a toggle button in :term[pseudocode]{id=pseudocode}, about forty lines, which has the anatomy and none of the kit's variety. Its job is to show every step on one page; read it for the order of calls.

```cpp pseudocode
bool ToggleButton(const char* id, const char* label, bool* value)
{
    const Theme& colors = GetThemeColors();
    const float height = FrameHeight();
    const float width = FramePadding.x * 2 + TextWidth(label);

    // 1. Reserve an item: identity, hit testing, keyboard focus.
    const bool pressed = InvisibleButton(id, Vec2(width, height));
    if (pressed)
        *value = !*value;

    // 2. Read what the item reports.
    const bool hovered = IsItemHovered();
    const bool held = IsItemActive();
    const Vec2 min = ItemRectMin();
    const Vec2 max = ItemRectMax();

    // 3. Pick colors from the theme, never from literals.
    Color fill = Transparent(colors.Control);
    if (*value)
        fill = WithAlpha(colors.Accent, held ? 0.34 : (hovered ? 0.26 : 0.18));
    else if (held)
        fill = colors.Border;
    else if (hovered)
        fill = colors.Control;
    const Color text = *value ? colors.Accent : colors.Text;

    // 4. Draw on the window's draw list, centered in the item.
    DrawList* drawList = WindowDrawList();
    drawList->AddFilledRect(min, max, fill, FrameRounding);
    drawList->AddText(Vec2(min.x + FramePadding.x, min.y + (height - FontSize()) * 0.5), text, label);

    // 5. The keyboard cursor is ours to draw now.
    RenderNavCursor(min, max, ItemId());

    // 6. A short help text, only while due.
    if (IsTooltipDue())
        SetTooltip("Toggles the setting");

    // 7. Tell the item probe where this widget is.
    ItemProbe::Record(id);
    return pressed;
}
```

1. **Line 8:** The reserved item gives the click, so the toggle flips here and the widget needs no mouse arithmetic.
2. **Lines 13-16:** The states and the rectangle are read right after the item, while it is still the last item.
3. **Lines 19-26:** Every color is a theme token, and the held state wins over hovered.
4. **Lines 30-31:** The widget draws the fill and the label itself, on the window's draw list.
5. **Line 34:** The keyboard cursor is drawn by hand, since the invisible item draws nothing.

Look at three things in it. The size is computed from the font and the style (`FrameHeight()`, `FramePadding`), never from pixel counts, so the widget grows with the :term[UI scale]{id=ui-scale}. The colors are theme tokens. And step 5 exists only because the widget draws itself: ImGui's stock button draws its own navigation cursor, the outline that shows which item the keyboard has reached, and an invisible one has none. Leave step 5 out and a person who tabs through the editor sees the focus vanish at your widget.

## The contract

A kit widget keeps these rules. Each has a reason, and the reasons are what lets you decide a new case.

1. **The id is the identity.** The text passed as `id` is an ImGui id, unique within the current id scope, and also the key of the probe entry. Give a widget that a test must find a unique, stable id made of a group, a dot and a name. Two widgets with one id in one scope fight for the mouse.
2. **Sizes come from the font.** The button's height is `ImGui::GetFrameHeight()` and its width is built from `CalcTextSize` and the style's paddings. The UI scale then needs no code in the widget.
3. **Colors come from `ThemeColors`.** A literal color does not follow a change of the theme, and the source scan of the design system fails it.
4. **The widget draws what ImGui no longer draws for it.** That is the navigation cursor, the tooltip and the disabled look.
5. **The widget records itself in the probe, every frame, in every build configuration.** Tests then see what users get.
6. **Work that is not needed this frame is not done.** A tooltip is formatted only while it will show.

:::rule
**Controls come from the widget kit.** UI code uses the kit's controls and not raw ImGui ones, so that every control behaves the same and appears in the probe. The reason is consistency and tests: a raw button is invisible to them. The rule is in the Editor section of `AGENTS.md`, and [the design system page](../editor-ui/design-system.md) teaches the tokens such controls draw with.
:::

## Reading the real button

The kit's button is the function `DrawButton` in `StrataEditor/src/UI/Widgets.cpp`. Two public functions call it: `IconButton` (a square button with only an icon) and `ToolbarButton` (an icon and a label). The function takes the toy's steps with the real details.

The first quote shows how it begins. Notice the order: the disabled scope opens before the item exists.

```cpp src="StrataEditor/src/UI/Widgets.cpp#L64-L76"
const ImGuiStyle& imguiStyle = ImGui::GetStyle();
const ThemeColors& colors = GetThemeColors();
const float height = ImGui::GetFrameHeight();
const bool hasLabel = label && *label;
const ImVec2 iconSize = ImGui::CalcTextSize(icon);
const float width = GetToolbarButtonWidth(icon, label);

ImGui::BeginDisabled(!style.Enabled);
const bool pressed = ImGui::InvisibleButton(id, ImVec2(width, height));
const bool hovered = ImGui::IsItemHovered();
const bool held = ImGui::IsItemActive();
const ImVec2 min = ImGui::GetItemRectMin();
const ImVec2 max = ImGui::GetItemRectMax();
```

1. **Line 69:** The width comes from a function, `GetToolbarButtonWidth`, so a caller can measure a button before it draws.
2. **Line 71:** A disabled scope opens before the item, so the item cannot be clicked.
3. **Line 72:** The button reserves the item and returns whether it was pressed.
4. **Lines 73-76:** The two states and the rectangle are read before anything else is submitted.

The second quote is the drawing, in the order the colors are chosen and used. Notice `vivid`, which is the difference that the toy has no use for.

```cpp src="StrataEditor/src/UI/Widgets.cpp#L100-L121"
// An active state stays vivid while the button cannot be clicked (e.g. Play while playing): it shows a state.
const bool vivid = style.Active && !style.Enabled;
ImDrawList* drawList = ImGui::GetWindowDrawList();
if (background.w > 0.0f)
	drawList->AddRectFilled(min, max, ToDrawColor(background, vivid), imguiStyle.FrameRounding);
const float textY = min.y + (height - ImGui::GetFontSize()) * 0.5f;
if (hasLabel)
{
	const float iconX = min.x + imguiStyle.FramePadding.x;
	AddText(drawList, ImVec2(iconX, textY), foreground, icon, vivid);
	AddText(drawList, ImVec2(iconX + iconSize.x + imguiStyle.ItemInnerSpacing.x, textY), style.Primary ? foreground : colors.Text, label, vivid);
}
else
{
	AddText(drawList, ImVec2(min.x + (width - iconSize.x) * 0.5f, textY), foreground, icon, vivid);
}
ImGui::RenderNavCursor(ImRect(min, max), ImGui::GetItemID());
ImGui::EndDisabled();

ShowTooltip(tooltip);
ItemProbe::Record(id, style.Enabled);
return pressed;
```

1. **Line 101:** The button is vivid when it shows a state and cannot be clicked.
2. **Line 104:** The fill uses the style's rounding, and the vivid flag skips the fade.
3. **Lines 106-115:** With a label, the icon and the text take separate colors; without one, the icon is centered.
4. **Line 116:** The navigation cursor is drawn inside the disabled scope, over the same rectangle.
5. **Lines 119-120:** The tooltip and the probe entry come after the scope ends; the probe records the enabled state.

Compare the real button with the toy, since the differences are the reasons a kit exists.

- The toy has one style. The real button has a `ButtonStyle` with four switches: `Enabled`, `Active`, `ActiveColor` and `Primary`. A primary button is the main action of a group and is filled with the accent. An active one shows a state, such as a toggle that is set.
- The toy draws with the plain draw list. The real one draws through `ToDrawColor`, which fades a color like ImGui's own items while the button is disabled.
- The toy has no disabled state. The real button opens `BeginDisabled` before the item and closes it after the drawing, so the item cannot be clicked and its colors fade.

### Why a disabled button can stay vivid

Take **Play** while the game plays. Its job is to show that the game runs, and it cannot be clicked again. The disabled fade would dim exactly the state the person wants to read. The button is `Active` and not `Enabled`, which is the case the line `vivid` names.

ImGui's `GetColorU32` multiplies a color's alpha by the style's alpha, and `BeginDisabled` scales that alpha by `DisabledAlpha`, which the editor's theme sets to 0.5. `ToDrawColor` takes a second argument that skips the multiplication and converts the color as it is. Say the active tint is a green with alpha 0.18 at rest. With the fade the fill would reach alpha $0.18 \times 0.5 = 0.09$, which is barely a tint; the vivid path keeps 0.18. The same flag keeps the icon and label at full strength.

The fade applies to the draw list only because the widget uses its own draw calls. A stock widget inside `BeginDisabled` fades by itself, and cannot make an exception. A custom widget can, and that is the reason the kit draws its buttons by hand. The price is that every color of such a widget passes through `ToDrawColor`, or the widget drifts out of step with the rest.

## Layout that depends on its own result

Here the immediate-mode style meets a problem. A row of chips floats above the Scene view. When the window is wide, each chip shows an icon and a label. When it narrows, the chips should shrink to icons, and when even the icons do not fit, the row should wrap.

To decide, the strip must know how wide all its chips are. But in an immediate-mode library you learn a widget's width by drawing it, and by then the first chips are already on the screen.

You have met this shape of problem: an answer is known only after the work that needed it. Retained-mode libraries solve it with a layout pass before the drawing pass. ImGui has none. Strata's answer is to let the strip measure its chips in one frame and use the result in the next. A **chip** is a rounded toggle or menu button that floats on a viewport's image.

A **chip strip** is a row of chips that decides together which of them show only an icon and where the row breaks.

```mermaid caption="Frame N draws with the decision of frame N minus one while it measures. The strip ends, its destructor decides, and frame N plus one draws with the new decision." alt="Two columns for two frames. In frame N, three steps: each chip reports its widths, the chips draw with the old decision, the strip's destructor stores a new decision. An arrow carries the stored decision to frame N plus one, whose chips draw as the decision says."
flowchart LR
    subgraph N[Frame N]
        A[Each chip reports its widths] --> B[Chip draws by the stored decision]
        B --> C[Destructor stores FirstIcon and RowStarts]
    end
    subgraph M[Frame N plus one]
        D[Chip draws by the stored decision]
    end
    C --> D
```

The strip's state lives between frames in a `ChipStripState` owned by the panel. It holds three things. The first is each chip's two widths, with its label and as an icon alone. The second is `FirstIcon`, the index from which the chips draw as icons. The third is `RowStarts`, the indexes of the chips that begin a new row.

A `ChipStrip` object lives for one frame, for the length of a scope: its :term[constructor]{id=constructor} registers it, each chip asks it `NextIsIcon`, and its :term[destructor]{id=destructor} does the deciding.

### A toy of the two frames

The sketch below is the decision without ImGui. It keeps the widths and the first icon in a state, takes five chips with the widths the Scene view's chips might have, and draws them for seven frames while the strip narrows. A `[]` stands for a chip drawn as an icon alone. Read it for the one thing that matters: what frame 3 draws.

```cpp sketch="editor-ui-widget-kit-strip.cpp"
// A toy chip strip: the widths measured while chips draw decide, when the strip ends, what the next frame draws as icons.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <vector>

struct ChipSize
{
	float Labeled = 0.0f;
	float Icon = 0.0f;
};

struct StripState
{
	std::vector<ChipSize> Sizes;
	size_t FirstIcon = SIZE_MAX;
};

class Strip
{
public:
	Strip(StripState& state, float available)
		: m_State(state), m_Available(available)
	{
	}

	~Strip()
	{
		m_State.Sizes.resize(m_Count);
		float width = m_Count > 0 ? c_Spacing * static_cast<float>(m_Count - 1) : 0.0f;
		for (const ChipSize& size : m_State.Sizes)
			width += size.Labeled;
		size_t firstIcon = m_Count;
		while (firstIcon > 0 && width > m_Available)
		{
			firstIcon--;
			width -= m_State.Sizes[firstIcon].Labeled - m_State.Sizes[firstIcon].Icon;
		}
		m_State.FirstIcon = firstIcon < m_Count ? firstIcon : SIZE_MAX;
	}

	bool NextIsIcon(float labeled, float icon)
	{
		const size_t index = m_Count++;
		if (m_State.Sizes.size() < m_Count)
			m_State.Sizes.resize(m_Count);
		m_State.Sizes[index] = { labeled, icon };
		return index >= m_State.FirstIcon;
	}

private:
	static constexpr float c_Spacing = 8.0f;

	StripState& m_State;
	float m_Available;
	size_t m_Count = 0;
};

void DrawFrame(StripState& state, int frame, float available)
{
	const char* names[] = { "Grid", "Outline", "Gizmos", "Preview lighting", "Game UI" };
	const ChipSize sizes[] = { { 90.0f, 36.0f }, { 110.0f, 36.0f }, { 104.0f, 36.0f }, { 170.0f, 36.0f }, { 110.0f, 36.0f } };
	std::printf("frame %d, %3.0f wide:", frame, available);
	{
		Strip strip(state, available);
		for (size_t index = 0; index < 5; index++)
			std::printf(" %s", strip.NextIsIcon(sizes[index].Labeled, sizes[index].Icon) ? "[]" : names[index]);
	}
	std::printf("\n");
}

int main()
{
	StripState state;
	const float widths[] = { 700.0f, 700.0f, 480.0f, 480.0f, 480.0f, 200.0f, 200.0f };
	for (int frame = 1; frame <= 7; frame++)
		DrawFrame(state, frame, widths[frame - 1]);
	return 0;
}
```

```text output-of="editor-ui-widget-kit-strip.cpp"
frame 1, 700 wide: Grid Outline Gizmos Preview lighting Game UI
frame 2, 700 wide: Grid Outline Gizmos Preview lighting Game UI
frame 3, 480 wide: Grid Outline Gizmos Preview lighting Game UI
frame 4, 480 wide: Grid Outline Gizmos [] []
frame 5, 480 wide: Grid Outline Gizmos [] []
frame 6, 200 wide: Grid Outline Gizmos [] []
frame 7, 200 wide: [] [] [] [] []
```

1. **Lines 30-32:** The destructor sums the labeled widths and the gaps, as the real one does.
2. **Lines 34-38:** The loop walks back from the last chip and counts how much each icon saves.
3. **Line 39:** The decision is stored for the next frame; `SIZE_MAX` means no chip is an icon.
4. **Line 47:** Each chip stores its widths while it draws.
5. **Line 48:** The answer comes from the stored decision, which the previous frame made.

The strip is 700 wide in frames 1 and 2. All five chips need 616 together (the labeled widths 90, 110, 104, 170 and 110, plus four gaps of 8), so every label shows.

In frame 3 the strip shrinks to 480, but the frame draws with the decision stored by frame 2, which said all labels. The chips overflow for one frame. Only the destructor of frame 3 sees the new width, and frame 4 draws the last two chips as icons. The same lag follows the drop to 200 wide in frame 6, and frame 7 draws every chip as an icon.

### The real strip

The real destructor does two jobs: it picks `FirstIcon` and it breaks rows. Notice the loop that walks backward from the last chip, and for what happens when the icons do not fit either.

```cpp src="StrataEditor/src/UI/Widgets.cpp#L225-L259"
ChipStrip::~ChipStrip()
{
	s_ChipStrip = nullptr;
	// The chips the next frame draws as icons: from the last one back, as few as make the strip fit.
	m_State.Widths.resize(m_Count);
	const float spacing = ImGui::GetStyle().ItemSpacing.x;
	float width = m_Count > 0 ? spacing * static_cast<float>(m_Count - 1) : 0.0f;
	for (const auto& [labeled, icon] : m_State.Widths)
		width += labeled;
	size_t firstIcon = m_Count;
	while (firstIcon > 0 && width > m_Available)
	{
		firstIcon--;
		width -= m_State.Widths[firstIcon].first - m_State.Widths[firstIcon].second;
	}
	m_State.FirstIcon = firstIcon < m_Count ? firstIcon : SIZE_MAX;

	// When even the icons do not fit, the chips that would pass the strip's width start rows under it.
	m_State.RowStarts.clear();
	float rowWidth = 0.0f;
	for (size_t index = 0; index < m_Count; index++)
	{
		const float chipWidth = index >= firstIcon ? m_State.Widths[index].second : m_State.Widths[index].first;
		if (rowWidth > 0.0f && rowWidth + spacing + chipWidth > m_Available)
		{
			m_State.RowStarts.push_back(index);
			rowWidth = chipWidth;
		}
		else
		{
			rowWidth += (rowWidth > 0.0f ? spacing : 0.0f) + chipWidth;
		}
	}
	m_State.Rows = static_cast<uint32_t>(m_State.RowStarts.size()) + 1;
}
```

1. **Line 229:** The state keeps only as many widths as chips drew this frame, so a removed chip leaves no stale entry.
2. **Lines 231-233:** The labeled widths and the gaps sum to the strip's natural width.
3. **Lines 235-239:** The walk runs back from the last chip while the strip is too wide.
4. **Line 240:** `SIZE_MAX` records that no chip becomes an icon.
5. **Lines 244-258:** The rows loop starts a row at each chip that would pass the strip's width, and `Rows` counts them.

Read the quote against the toy. The widths sum (lines 231 to 233) and the backward walk are the same. What the toy lacks is the row logic after them.

When `FirstIcon` has reached 0 and the sum still exceeds the strip, every chip is an icon and the row is still too wide. The rows loop then walks the chips with their current widths (labels before `FirstIcon`, icons from it) and starts a new row at each chip that would pass the strip's width. `Rows` tells the toolbar how much height to reserve.

Which side draws the new row? The chip does, through `NextIsIcon`, which every chip calls as it draws.

```cpp src="StrataEditor/src/UI/Widgets.cpp#L261-L279"
bool ChipStrip::NextIsIcon(float labeledWidth, float iconWidth)
{
	const size_t index = m_Count++;
	if (m_State.Widths.size() < m_Count)
		m_State.Widths.resize(m_Count);
	m_State.Widths[index] = { labeledWidth, iconWidth };
	// The previous frame's rows: a chip that starts one goes to its left end, under the row before.
	if (m_NextRowStart < m_State.RowStarts.size() && m_State.RowStarts[m_NextRowStart] == index)
	{
		m_NextRowStart++;
		m_Row++;
		const ImGuiStyle& style = ImGui::GetStyle();
		ImGui::SetCursorScreenPos(ImVec2(m_Start.x, m_Start.y + static_cast<float>(m_Row) * (ImGui::GetFrameHeight() + style.ItemSpacing.y)));
		// The chip starts a line of the window: a SameLine before it (the strip's chips are drawn one beside the other)
		// would keep the row above as the line, and the next chip's SameLine would go back to it.
		ImGui::GetCurrentWindow()->DC.IsSameLine = false;
	}
	return index >= m_State.FirstIcon;
}
```

1. **Line 266:** The chip stores its two widths for the next frame's decision.
2. **Lines 268-277:** If the previous frame's `RowStarts` names this chip, the cursor moves to the next row.
3. **Line 276:** The window's same-line flag is cleared, so the next chip's `SameLine` stays on the new row.
4. **Line 278:** The answer comes from the stored `FirstIcon`.

Look at what the function does to the cursor: it moves it to the left end of a row below, one frame height plus the item spacing down, and it sets `IsSameLine` to false. The kit's chips are placed with `SameLine`, the ImGui call that puts the next item beside the last one, so the next chip after the moved one would otherwise jump back to the row above. A custom widget has to know details of ImGui's internals like this one.

:::example[The Scene view's chips, wide and narrow]
Take the five chips of the toy: labeled widths 90, 110, 104, 170 and 110, icon width 36, gap 8.

At 480 wide. Total labeled width $90 + 110 + 104 + 170 + 110 + 4 \times 8 = 616$. That is over 480, so walk back from the last chip.

Chip 4 (index 4) as an icon saves $110 - 36 = 74$: 542, still over. Chip 3 saves $170 - 36 = 134$: 408, which fits. `FirstIcon` is 3. The rows pass: 90, then 208, 320, 364 and 408, all within 480, so `Rows` is 1.

At 200 wide. Continue the walk: chip 2 saves 68 (340), chip 1 saves 74 (266), chip 0 saves 54 (212). The loop ends with `FirstIcon` at 0 and the sum still over 200. Now the rows use icon widths: 36, 80, 124, 168. The fifth icon would make $168 + 8 + 36 = 212$, which passes 200, so it starts a row: `RowStarts` is {4} and `Rows` is 2.

The check at the limits: with a strip wider than 616 nothing is converted and `FirstIcon` is `SIZE_MAX`; a strip of zero chips has width 0 and never enters the loop.
:::

The Scene view's toolbar shows the result with its own chips. The pictures below show that toolbar in a wide and in a narrow Scene view, both inside a window 1280 pixels wide.

::figure{id=scene-toolbar variant=wide}

::figure{id=scene-toolbar variant=narrow}

:::note
Icons take the place of labels without losing anything. A chip drawn as an icon puts its label in front of its tooltip, and the probe keeps the label as the item's text, so tests and agents still find "Grid" by name.
:::

## The item probe

Tests need to find widgets. The **item probe** is a table in which each kit widget writes its rectangle, its enabled state and, for some, a meaning color and text, under a key made from its id. The table is read by `Find`, which tests call to learn where to click. How tests click is the subject of [the UI testing page](../editor-ui/ui-testing.md); this page covers the writing side.

The code is short because the job is small. Notice the three things it keeps true.

```cpp src="StrataEditor/src/UI/ItemProbe.cpp#L30-L51"
void ItemProbe::RecordRect(std::string_view key, const ImVec2& min, const ImVec2& max, bool enabled, ImU32 color, std::string_view text)
{
	const int frame = ImGui::GetFrameCount();
	Item& item = s_Items[HashKey(key)];
	item.Duplicate = item.Frame == frame;
	item.Min = min;
	item.Max = max;
	item.Frame = frame;
	item.Enabled = enabled;
	item.Color = color;
	// Reuses the item's storage: recording the same widget every frame allocates nothing once its text fits.
	item.Text.assign(text);
}

std::optional<ItemProbe::Item> ItemProbe::Find(std::string_view key)
{
	if (!ImGui::GetCurrentContext())
		return std::nullopt;
	const auto it = s_Items.find(HashKey(key));
	if (it == s_Items.end() || it->second.Frame != ImGui::GetFrameCount())
		return std::nullopt;
	return it->second;
```

1. **Lines 32-34:** The frame number is read, and the entry for the key is created or found in a :term[hash map]{id=hash-map}. If the entry already holds this frame's number, the key was recorded twice in one frame, and `Duplicate` is set. A test that asks for a key that names two widgets would click the wrong one, so the harness refuses a duplicate.
2. **Line 41:** The text goes into the entry's own string with `assign`. The string keeps its storage between frames, so recording the same widget every frame allocates nothing once the text fits.
3. **Lines 44-51:** `Find` answers only for entries of the latest frame. A widget that was drawn two frames ago and is hidden now is not found, so a test cannot click what the person cannot see.

The cost is one hash-map write per widget and frame. A hash map finds an entry by hashing the key and jumping to a bucket, so the time hardly depends on how many widgets exist.

The probe runs in every :term[build configuration]{id=build-configuration}, including `Dist`, which ships to users. The reason is stated in the :term[header]{id=header}: tests then see what users get. A probe present only in test builds would let the user's build differ from the tested one.

:::why
Strata could have kept the probe out of shipping builds and saved its map writes. It keeps them because the editor is tested as it ships. The cost is small, and an empty probe in `Dist` would turn every test of `Dist` into a test of something else.
:::

Rows of a long list need keys too. `NumberedProbeKey` builds one from a prefix and a number, such as `Problems.Row.3`, in a buffer inside the object, so a list that draws every frame records its rows without allocating. A prefix longer than 40 characters is cut. Entries stay until `Clear`, so use a fixed set of key names, never one made from changing text.

## Buttons, pills and banners

The kit holds more than the button. The first group covers what you click and what you read at a glance.

A **pill** is a small status label: an icon and text in a color on a tint of that color, sized to its text. It can lead somewhere when clicked.

A **banner** is a notice across the available width, with an icon and wrapped text in a color. The probe records its color and text.

| Widget | What it is for |
| --- | --- |
| `ButtonStyle` with `ToolbarButton`, `IconButton` | Toolbar and inline buttons; styles `Enabled`, `Active`, `ActiveColor` and `Primary` |
| `Chip`, `ToggleChip`, `ChipStrip` | Rounded buttons over an image; a toggle chip shows on and on-but-not-in-effect |
| `Pill`, `CalcPillWidth` | Status labels, tinted by their meaning color |
| `Banner`, `CenteredText` | A wrapped notice; a centered hint for empty states |
| `SearchField` | A text field with a search icon and a clear button |
| `TextField` | A text field with its caption above |
| `ActionButton` | A large button, 1.6 frame heights tall, for the main actions of a page |
| `LinkButton` | Text that acts as a link, underlined while hovered |
| `DialogButton`, `DialogButtonWidth` | Buttons of equal width for dialogs, the primary one filled |
| `OpenModal`, `BeginModal`, `EndModal` | A dialog centered in the viewport with a title and a close button |
| `PushSelectionColors`, `PopSelectionColors` | A selected row keeps the accent while the mouse is over it |

## Cards, headers and drawing helpers

The second group holds widgets that hold other things, and small drawing helpers.

A **card** is a raised tile that you click, with an icon (or a picture), a title and a description.

An **entry card** is the list form of a card: a badge or picture at the left, then a title, a subtitle and a detail line.

A **section header** is a collapsing header in the `SemiBold` font on a raised surface, which can show a short summary at its right end.

| Widget | What it is for |
| --- | --- |
| `Card`, `CardPicture`, `GetCardHeight` | Tiles such as project templates |
| `EntryCard`, `EntryCardContent` | Rows of a list of recent projects |
| `SectionHeader`, `Heading` | Sections that fold; titles in the :term[type scale]{id=type-scale} |
| `CopyableCode` | Fixed-width code with a copy button that shows a check mark for 1.5 seconds |
| `ElideStart`, `ElideEnd` | Text shortened with an ellipsis to fit a width |
| `Legend` | Color squares, labels and right-aligned counts drawn over an image |
| `StrataProgressBar`, `BrandMark` | The progress bar and the mark in the editor's motif |
| `TextureImage` | A texture drawn as its content looks |
| `CancelDragDropOnEscape` | Escape cancels a drag, once per frame |

Two entries repay a closer look. `ElideEnd` cuts text by characters, never by :term[bytes]{id=byte}, because the text is :term[UTF-8]{id=utf-8} and a character may take up to four bytes. The code walks forward from a probable cut past any continuation byte (a byte whose top two bits are `10`).

The code finds the longest fitting start by halving the range: the width only grows as the end moves right, so about $\log_2 n$ measurements suffice for $n$ bytes. `TextureImage` draws a texture the way its content looks, which needs :term[sRGB]{id=srgb} colors encoded and normal maps shown with their Z. UI code draws textures through this function for that reason, and [the ImGui backends page](../editor-ui/imgui-backends.md) teaches the display modes.

## Helpers and native dialogs

The kit's last group is helpers that draw nothing themselves. `TextFormat` turns data into text people read: a path written as the system writes it, "5 minutes ago", short ages such as "12 s ago", and initials for a badge. `Markdown` splits a Markdown text into blocks (headings, paragraphs, list items and tables) and draws them; the About window shows the third-party notices with it.

`FileDialogs` wraps **nfd**, the native file dialog library that opens the :term[operating system's]{id=operating-system} own file and folder dialogs.

A native dialog blocks. While the picker is open the call does not return, so it must run on the :term[main thread]{id=main-thread}, and the :term[frame loop]{id=game-loop} waits. The editor therefore keeps its file dialogs out of anything that runs per frame, and calls `FileDialogs::Init` once before any use. When the person cancels or the dialog fails, the functions return nothing and log the failure.

## Rules that keep the kit sound

Four more rules complete the contract. Each has a reason you can test against a new widget.

:::note
**Chips never take focus.** `DrawChip` passes `ImGuiButtonFlags_NoFocus` and `ImGuiButtonFlags_NoNavFocus` to its `InvisibleButton`. A chip floats over the Game view, and clicking it must not hand the game the keyboard. The flags stand in `DrawChip` in `Widgets.cpp`.
:::

:::note
**Write costly tooltips only while due.** A widget drawn every frame must not format statistics every frame for nothing. `UI::IsTooltipDue()` answers whether the last item's tooltip shows now, so the caller writes the text after the widget only then. The function accepts hovering a disabled item too, since disabled widgets keep their tooltips.
:::

:::note
**An active text input keeps its own copy of the text.** ImGui's `InputText` copies the caller's string when the field becomes active and writes it back each frame. Text replaced from outside, for example by an undo while the field is active, is replaced by the stale copy unless the field is told to read the caller's string again. `SearchField` takes a `reload` argument that calls `ReloadUserBufAndMoveToEnd` on the field's state before drawing.
:::

:::note
**Textures go through `TextureImage`.** The reason, display modes and sampler state, belongs to the page on the ImGui backends, which this page links above.
:::

The first rule does not apply to every widget of the kit: buttons take focus, as people expect of a button. Chips are different because of where they sit. When you write a new widget, ask where it sits and what it must not disturb.

:::analogy
A kit widget is like a window frame bought as a bare timber frame. The carpenter (ImGui) supplies the frame, with its hinges and its place in the wall; the owner (the widget) paints it and fits the glass. The painted frame still opens, because the carpenter's part is untouched.

**Where it breaks:** a real frame cannot forget to be painted, and a widget that forgets the navigation cursor still compiles and runs, only with a missing outline.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Change the look of ImGui's own widgets through the style stack | Most ImGui tools | Less code per widget; no custom drawing | Icons with labels, state fills, rounded chips and the vivid disabled state |
| Write widgets with no ImGui item, by hand | Games that draw their own menus | Full control of every pixel | Keyboard navigation, identity, clipping and overlap rules |
| A layout pass before drawing | Retained libraries, such as web pages | The strip decides in the same frame, with no one-frame lag | A second walk over every chip each frame, and a different library |
| A probe only in test builds | Many test setups | A little less work in shipping builds | Tests that no longer test what ships |
| Find widgets in tests by their screen text | UI test tools | No keys to maintain | Tests that break when a label changes |

## How it is tested

The kit is tested through the same harness that tests the panels. The suite lives in `StrataTests/src/Editor/EditorUITests.cpp`, and its test `The widget kit: buttons, chips, pills, cards and dialogs` draws a window of kit widgets inside a headless :term[ImGui context]{id=imgui-context}. The test finds each by its probe key and presses it with the harness's mouse. It checks that a toggle chip flips, that a disabled button does not count a click, that a key used twice is flagged `Duplicate`, and that a pill is as tall as a frame.

The strip has its own test, `A Scene view too narrow for its chips' labels shows the last ones as icons, every one in reach`. The test narrows the Scene view and checks that every chip ends inside the image's width, sits in the toolbar and covers no other chip. It also checks that the Grid chip keeps its label in the probe.

You run them like every unit test, from the build's test program, with a doctest filter on the name:

```sh
build/windows/bin/Debug/StrataTests.exe --test-case="*widget kit*"
```

The filter keeps the tests whose names contain the words between the stars, which here selects the kit's test.

## Changing it safely

Add a widget in `StrataEditor/src/UI/Widgets.h` and `StrataEditor/src/UI/Widgets.cpp`, next to the group it belongs to, and walk the contract of this page. A short list helps:

- The widget reserves an item with an id, and the id is the probe key.
- The widget takes sizes from the font and colors from `ThemeColors`.
- The widget draws the navigation cursor, shows its tooltip only while due, and records itself.
- A widget over a viewport image passes the no-focus flags.
- A widget that can look disabled and must stay clear to read uses `ToDrawColor` with `vivid`.
- A new widget that tests will click needs a test in the harness that clicks it by key.

Changing an existing widget carries one more risk: the widgets are used by many panels, and a size change moves layouts everywhere. Run the whole `Editor.UI` suite and the other editor suites, not only the kit's test. The rule `AGENTS.md` gives for the editor's UI, colors from theme tokens, sizes relative to the font and the editor's own widget kit, is the contract these checks protect.

## Summary

- A kit widget reserves an `InvisibleButton`, reads hovered and held, draws with the window's draw list in theme colors, renders the navigation cursor, shows its tooltip and records itself.
- A button that shows a state stays vivid while disabled because its colors skip ImGui's fade through `ToDrawColor`.
- A chip strip measures its chips in one frame, decides `FirstIcon` and `RowStarts` in its destructor, and draws with the decision in the next frame.
- The item probe is one hash-map write per widget and frame in every build; `Duplicate` flags an id recorded twice, and `Find` sees only the latest frame.
- A new widget needs an id that is also its probe key, font-based sizes, theme colors, the navigation cursor, and a harness test that clicks it.

## Check yourself

1. A strip is 300 wide. Its three chips have labeled widths 100, 120 and 90 and an icon width of 36, with a gap of 8. Which chips are icons after the strip's destructor?

   :::answer{tests="two-frames"}
   The sum is $100 + 120 + 90 + 2 \times 8 = 326$, over 300. Chip 2 as an icon saves $90 - 36 = 54$, giving 272, which fits. `FirstIcon` is 2, so only the last chip is an icon, and it takes effect in the next frame.
   :::

2. A button is `Active` and not `Enabled`. Which statement is right: (a) its colors fade; (b) its colors skip the fade; (c) it is not drawn; (d) it answers clicks?

   :::answer{tests="vivid"}
   (b) is right. (a) is wrong because `ToDrawColor` with `vivid` converts the color without the disabled alpha. (c) is wrong because the draw calls still run. (d) is wrong because `BeginDisabled` is still open, so the item cannot be clicked.
   :::

3. A widget records its probe key twice in one frame. What does `Find` return, and what does a harness click do?

   :::answer{tests="probe"}
   `Find` returns the entry with `Duplicate` set to true, holding the rectangle written last. The harness's `ClickItem` refuses a duplicate or disabled entry and sends no input, so a test cannot press the wrong widget.
   :::

4. Why does the first frame of a chip strip with a new chip draw with the old widths?

   :::answer{tests="two-frames"}
   A chip's width is known only once it draws, and the decision comes from the destructor at the end of the strip. The next frame uses it. A strip that changes width or chips therefore settles in one frame, and the frame in between may overflow.
   :::

5. Which of these does an `InvisibleButton` not supply: (a) hit testing, (b) the keyboard focus ring, (c) item identity, or (d) hovered and held states?

   :::answer{tests="anatomy"}
   (b). The item takes part in keyboard navigation, but it draws nothing, so the widget calls `RenderNavCursor` to show the ring. The other three come with the item.
   :::

6. You add a segmented toggle of three options to a panel. Which steps must each option take in every frame, and how does a test press one?

   :::answer{tests="write-widget"}
   Each option reserves an `InvisibleButton` with its own id, reads hovered and held, draws from theme colors, renders the navigation cursor, shows a tooltip only while due and records itself under its probe key. A test finds the key with `ItemProbe::Find` and clicks it with the harness over three frames; a key shared by two options would be flagged `Duplicate` and refused.
   :::

## Exercises

1. **Basic.** Write on paper the probe keys a segmented toggle of three options, `Wire`, `Solid` and `Both`, should record in a panel named `Shading`. Say when each key is recorded.

   :::answer[Worked solution]{tests="probe"}
   One key per option: Shading.Wire, Shading.Solid and Shading.Both. Each option records its rectangle every frame it draws, since `Find` answers only for the latest frame. A key for the whole group is needed only when a test must find the group; keys name what a test would click.
   :::

2. **Medium.** Trace it yourself: find where the item probe sets `Duplicate`, and where the chips ask not to take focus. Name the files and functions.

   :::answer[Worked solution]{tests="probe"}
   Search for `Duplicate` in `StrataEditor/src/UI/ItemProbe.cpp`: it is set in `ItemProbe::RecordRect`, as `item.Duplicate = item.Frame == frame;`. Put a breakpoint there while the Scene view's toolbar draws: each chip hits it once per frame. Search for `ImGuiButtonFlags_NoFocus` and the hit is in `DrawChip` in `StrataEditor/src/UI/Widgets.cpp`, in the call that makes the chip's `InvisibleButton`.
   :::

3. **Hard.** Extend the toy strip with rows: when every chip is an icon and the strip is still too narrow, record the indexes that start a new row. Run the toy with a width of 100 and report the rows.

   :::answer[Worked solution]{tests="two-frames"}
   After the backward walk, loop over the chips with their current widths, as the real destructor does. Keep a row width. When the row is not empty and the row width plus the gap plus the chip's width passes the strip, record the index and restart the row at that chip's width.

   With five icons of 36 and a gap of 8, a width of 100 gives a first row of 36 and 80; the third icon would make 124, so chip 2 starts a row. Chips 2 and 3 make 80, and chip 4 would reach 124, so it starts a third row. The indexes are {2, 4} and `Rows` is 3.
   :::

## Where it lives in Strata

- `StrataEditor/src/UI/Widgets.h` and `StrataEditor/src/UI/Widgets.cpp`: every widget and helper of the kit, `ChipStrip` and `ChipStripState`.
- `StrataEditor/src/UI/ItemProbe.h` and `StrataEditor/src/UI/ItemProbe.cpp`: `ItemProbe` and `NumberedProbeKey`.
- `StrataEditor/src/UI/TextFormat.h`, `StrataEditor/src/UI/Markdown.h` and `StrataEditor/src/UI/FileDialogs.h`: the helpers.
- `StrataTests/src/Editor/EditorUITests.cpp`: the tests of the kit and of the narrow Scene view.
- `StrataEditor/src/Panels/ViewportPanel.h` and `StrataEditor/src/Panels/ViewportToolbar.h`: the Scene view's panel, which owns a `ChipStripState`, and the code that lays out its chips.

## Further reading

- Dear ImGui's own documentation and its wiki on custom widgets: what an item, an id and the draw list are (intermediate).
- Game Programming Patterns, "Game Loop" and "Dirty Flag": how work moves between frames (beginner).
