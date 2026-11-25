---
id: editor-ui/imgui
title: "Dear ImGui from first principles"
description: "How one frame of Dear ImGui builds windows, items, IDs, popups, tables and docking, taught on a scratch layer you add to the editor."
kind: concept
size: L
tracks: [E]
needs: [core/windows-events, editor-ui/immediate-mode]
time: 60
learn:
  - id: frame-calls
    text: explain which calls make up one frame of Strata's ImGui module and in which order a click is seen
  - id: window-end
    text: write a window and a child window that call their end function whether or not the begin call returned true
  - id: id-stack
    text: predict whether two items share an ID from their labels, the pushed scopes and the suffixes ## and ###
  - id: popups
    text: explain why ImGui keeps one popup per level and open a modal from a menu item
  - id: layout-style
    text: build a window with items on one line, a sortable table and a pushed style that is popped again
since: 0.3.0
status: final
---

You have built the engine and made your first change. Now you want a small window inside the editor: a number, and a button that adds one to it. Nothing about the number should live anywhere except one variable of your own.

With a retained library you would create a window object, a text object and a button object, and connect the button to a function. With Dear ImGui you write the window as a few lines that run every frame. The page [Why immediate mode](immediate-mode.md) explains why Strata chose that. This page teaches how the library behaves, so that you can write such a window, give every item an identity, and open a dialog from it.

Everything here grows one scratch layer. A layer is the unit of the program's layer stack that you met in [Windows, events and layers](../core/windows-events.md): its `OnImGuiRender` function runs once per frame. The patch of Exercise 1 adds the first version to the editor, and the other two exercises extend it. You can apply it now and watch each idea work.

## One frame draws the whole interface

The naive picture of a user interface is a set of objects that live between frames. A button object remembers whether the mouse is over it. A window object remembers where it is. Dear ImGui keeps almost none of that in your code. Your code runs top to bottom once per frame and says what should be on the screen now.

**Dear ImGui** is a C++ library that builds a user interface this way: each frame, your code calls one function per window and per control, and the library turns those calls into triangles. Strata uses it for the editor and its tools.

The library keeps its own memory in an **ImGui context**: the object that holds all of the library's state for one interface, such as its windows, its queue of input and its fonts. Strata creates one context when its `ImGuiLayer` starts.

One frame has three phases. `NewFrame` starts it: the library reads the input the platform gave it, such as the mouse position and the keys, and clears what it drew last time. Then your code makes its calls. `Render` ends the frame: it sorts everything you submitted into lists of triangles, called the draw data. Another part of the engine, taught in [the backends page](imgui-backends.md), turns that draw data into pictures on the :term[graphics processing unit]{id=gpu} (GPU).

```mermaid caption="One frame of the interface: input is read, every layer submits its calls, and the library turns them into draw data for the GPU." alt="A row of steps: the platform feeds input, the frame starts, each layer submits its calls, the library renders them into draw data, and the draw data goes to the back buffer."
flowchart LR
    A["Platform input"] --> B["NewFrame"]
    B --> C["Each layer: OnImGuiRender"]
    C --> D["Render"]
    D --> E["Draw data"]
    E --> F["Back buffer"]
```

Strata's `ImGuiModule` makes these calls. Your layer never calls `NewFrame` or `Render`. The module calls `Begin` on its layer, then asks every layer of the stack to run `OnImGuiRender`, then calls `End`. Here is the module's function for that stage.

```cpp src="Strata/src/Strata/ImGui/ImGuiModule.cpp#L57-L63" from="m_Layer->Begin();" to="m_Layer->End(m_Graphics->GetDevice()->GetBackBufferFramebuffer());" symbol="ImGuiModule::OnRenderUI"
m_Layer->Begin();
for (Layer* layer : frame.Layers)
	layer->OnImGuiRender();

// The back buffer: the GPU waits for the display only from here on, after the frame's uploads and offscreen rendering.
Renderer::PrepareBackBuffer();
m_Layer->End(m_Graphics->GetDevice()->GetBackBufferFramebuffer());
```

In the layer's `Begin`, the platform reads its input and then `ImGui::NewFrame` runs. In its `End`, `ImGui::Render` runs and the draw data is drawn into the back buffer. Between them every layer is called in stack order, so your scratch layer's calls and the editor's own panels land in the same frame, in the same context.

Here is the layer you will write. Look at the order of the calls: the text comes before the button.

```cpp pseudocode
void OnImGuiRender() override
{
	ImGui::Begin("Scratch");
	ImGui::Text("Count: %d", m_Count);
	ImGui::SameLine();
	if (ImGui::Button("Add"))
		m_Count++;
	ImGui::End();
}
```

The function names one window, "Scratch", and fills it with a line of text and a button on the same line. Nothing is stored between frames except `m_Count`, which is your own variable. The example below follows this code through the frames of one click.

:::example[Five frames of one click]
Follow one click through five frames, with `m_Count` starting at 0. The table lists what the button call sees and what the window shows at the end of each frame.

| Frame | Mouse | The button call | The window shows |
| --- | --- | --- | --- |
| 1 | Outside the button | Returns false | Count: 0 |
| 2 | Over the button | Returns false (hovered) | Count: 0 |
| 3 | Left button pressed, still over it | Returns false (active) | Count: 0 |
| 4 | Left button released over it | Returns true; `m_Count` becomes 1 | Count: 0 |
| 5 | Over the button | Returns false | Count: 1 |

The click is seen in frame 4, but the text call of frame 4 ran before the button call, so it still printed 0. The 1 appears one frame later. At 60 :term[frames per second]{id=frame-rate} that is 16.7 ms, which nobody notices; it matters only when you read one value twice in a frame and expect them to agree.
:::

## Windows hold items and always end

A **window** is a rectangle of the interface with a title, a position, a size and its own list of items. Every panel of the editor is a window. You start one with `ImGui::Begin(name)` and finish it with `ImGui::End()`. Everything you submit between the two goes into that window.

`Begin` returns true or false. It returns false when the window is collapsed, or docked behind another tab, so that nothing of it is visible. Then you may skip the items to save work. You may not skip `End`: it must run every time `Begin` ran, whatever `Begin` returned.

```cpp pseudocode
if (ImGui::Begin("Scratch", &m_Open))
{
	ImGui::Text("The window is visible");
}
ImGui::End();
```

The second argument is optional. When you pass the address of a flag, the window shows a close button, and a click on it writes false into your variable. You decide what that means; the library only reports it. The editor does this for its panels: its panel registry passes the address of a flag to each `Begin`.

Most other begin calls pair the other way. Calls that open a popup, a menu, a drop-down list or a table are paired the other way: you call their `End` function only when the begin call returned true. `Begin` and `BeginChild` are the two that always need their end. Calls that miss their partner are a programmer error. With the settings Strata leaves at their defaults, :term[ImGui]{id=dear-imgui} reports it and asserts.

A **child window** is a window inside a window, with its own scrolling and clipping. You start one with `ImGui::BeginChild("List", ImVec2(0.0f, 120.0f), ImGuiChildFlags_Borders)` and end it with `ImGui::EndChild()`, again always. A size of 0 in one direction means "take what is left". Use a child window when a part of a panel must scroll by itself, such as a list under a fixed title row.

## Items answer where you call them

An **item** is anything the library lays out and draws for you: a button, a line of text, a check box, a slider. A call such as `ImGui::Button("Add")` does three things in one step. It places the item at the cursor, draws it, and tells you what the person did with it by returning a value. A button returns true on the frame its click completes. A check box takes the address of your flag, changes it, and returns true on the frame it changed.

The idea of the whole library is this: the answer comes back through the call, so the code that draws the control is also the code that reacts to it. There is no :term[callback]{id=callback} and no object to ask later.

Sometimes you need more than the :term[return value]{id=return-value}. The library remembers the last item: the item of the most recent call, which a group of functions asks about. `ImGui::IsItemHovered()` says whether the mouse is over it. `ImGui::GetItemRectMin()` and `ImGui::GetItemRectMax()` give its corners in screen coordinates. A tooltip is the typical use.

```cpp pseudocode
ImGui::Button("Add");
if (ImGui::IsItemHovered())
	ImGui::SetTooltip("Adds one");
```

The word "last" is literal. Any call that makes an item, even `ImGui::Text`, replaces the last item, so the query must stand right after the item it asks about. In the code above, a `Text` between the button and the query would make the tooltip appear over the text instead.

## IDs tell the library which item is which

The library has no objects, so how does it know that the button of frame 3 is the same button as in frame 2? It does not remember your variable. It remembers a number, an identifier (ID). The **ID** of an item is a 32-bit number: a :term[hash]{id=hash} of its label, mixed with the **ID stack**.

A hash turns any text into a number that is almost always different for different texts. The ID stack is the list of numbers your code pushed for the scopes it is inside. The library keeps "hovered" and "active" under these numbers.

Two items with the same ID are one item to the library. That is the most common surprise of a first week.

The rule has three parts. The ID of a label is its hash seeded with the top of the ID stack. `ImGui::PushID` puts a new number on the stack and `ImGui::PopID` removes it. The window's own ID is the first entry of its stack, so the same label in two windows gives two IDs.

The sketch below models the rule in plain C++, with the table the library uses for its hash. It makes the IDs of the Scratch window's items, and prints them.

```cpp sketch="editor-ui-imgui-ids.cpp"
// A model of Dear ImGui's ID stack: an ID is a CRC-32C hash of a label, seeded by the top of the stack.
// A "###" in a label restarts the hash, so only it and the text after it count. Strings stand in for PushID's values.
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace
{

	uint32_t s_Table[256];

	void BuildTable()
	{
		for (uint32_t index = 0; index < 256; index++)
		{
			uint32_t value = index;
			for (int bit = 0; bit < 8; bit++)
				value = (value & 1) ? (value >> 1) ^ 0x82F63B78u : value >> 1;
			s_Table[index] = value;
		}
	}

	uint32_t HashLabel(const std::string& label, uint32_t seed)
	{
		seed = ~seed;
		uint32_t crc = seed;
		for (size_t position = 0; position < label.size(); position++)
		{
			if (label.compare(position, 3, "###") == 0)
				crc = seed;
			crc = (crc >> 8) ^ s_Table[(crc & 0xFF) ^ static_cast<unsigned char>(label[position])];
		}
		return ~crc;
	}

	struct IdStack
	{
		std::vector<uint32_t> Ids;

		explicit IdStack(const std::string& window)
		{
			Ids.push_back(HashLabel(window, 0));
		}

		uint32_t GetID(const std::string& label) const { return HashLabel(label, Ids.back()); }
		void Push(const std::string& label) { Ids.push_back(GetID(label)); }
		void Pop() { Ids.pop_back(); }
	};

	void Print(const std::string& what, uint32_t id)
	{
		std::printf("%-26s 0x%08X\n", what.c_str(), id);
	}

}

int main()
{
	BuildTable();
	IdStack stack("Scratch");
	Print("Delete", stack.GetID("Delete"));
	Print("Delete (second call)", stack.GetID("Delete"));
	Print("Delete##2", stack.GetID("Delete##2"));
	Print("Delete###Row", stack.GetID("Delete###Row"));
	Print("Remove###Row", stack.GetID("Remove###Row"));
	for (int row = 0; row < 2; row++)
	{
		stack.Push(std::to_string(row));
		Print("row " + std::to_string(row) + ": Delete", stack.GetID("Delete"));
		stack.Pop();
	}
	return 0;
}
```

```text output-of="editor-ui-imgui-ids.cpp"
Delete                     0xE5B9FB58
Delete (second call)       0xE5B9FB58
Delete##2                  0x59E2C5E9
Delete###Row               0x89910AD1
Remove###Row               0x89910AD1
row 0: Delete              0xE633028D
row 1: Delete              0x8E302E45
```

1. **Line 19:** each of the 256 entries of the hash's table is a :term[byte]{id=byte} put through eight steps with the polynomial of :term[CRC-32C]{id=crc-32c}.
2. **Lines 30–31:** three marks in a row restart the hash from the seed, and the marks are then folded in like any other character.
3. **Line 32:** every character is folded into the running value.
4. **Line 47:** pushing a label puts its ID, under the current top, on the stack.
5. **Line 69:** each row pushes its own number before it makes its button.

Read the output line by line. The two calls of `Delete` print the same number: in one scope, the same label is the same item. `Delete##2` prints a different number, because the hash covers the whole text, including the part after the two marks. `Delete###Row` and `Remove###Row` print the same number, because the three marks restart the hash, and only they and the text after them count. The two lines for `row 0` and `row 1` differ although both labels are `Delete`: each ran under its own pushed scope.

Two suffixes matter. With `##`, the text after the marks is part of the ID but is not drawn, so `"Delete##2"` shows "Delete". With `###`, only the marks and the text after them form the ID, so the part before them can change every frame without changing the item.

The first suffix serves several items with one visible label. The second serves a window or item whose title changes.

:::question[What if two rows have the same name?]
Two entities may both be called "Cube", and the person can rename any of them while the list is on the screen. A label is therefore a poor identity. A number that never changes, one per row, is the right one.
:::

Strata's Hierarchy panel does exactly that. Every row pushes the bytes of its entity's :term[universally unique identifier]{id=uuid} (UUID), the number that names an entity for its whole life, as its scope. Two entities named "Cube" give two different IDs, and a rename changes no ID.

```cpp src="StrataEditor/src/Panels/SceneHierarchyPanel.cpp#L736-L743" from="const HierarchyRow& row = m_View.GetRows()[index];" to="ImGui::PushID(reinterpret_cast<const char*>(&id), reinterpret_cast<const char*>(&id) + sizeof(UUID));" symbol="SceneHierarchyPanel::DrawRow"
const HierarchyRow& row = m_View.GetRows()[index];
const entt::registry& registry = scene.GetRegistry();
if (!registry.valid(row.Handle))
	return;
const ImGuiStyle& style = ImGui::GetStyle();
const UI::ThemeColors& colors = UI::GetThemeColors();
const UUID id = row.ID;
ImGui::PushID(reinterpret_cast<const char*>(&id), reinterpret_cast<const char*>(&id) + sizeof(UUID));
```

The panel windows use `###` too. The panel registry names each one as the icon, two spaces, the title and `###`, then the panel's own id. The title may change without making a new window.

The registry also refuses an id that holds `=`, `#`, `[`, `]` or a line break, because the ids are keys in the layout file you will meet at the end of this page. The hidden label of the drop-down list in the Hierarchy, `"##EditLayer"`, is the other use: a control with no visible text but a name of its own.

## Hovered, active and focused are three different states

The library tracks three states per item, and each answers a different question. One click moves through all of them, so they are hard to tell apart.

An item is **hovered** when the mouse is over it and nothing blocks it, such as a popup drawn on top. A hovered button is drawn a little lighter.

A button is **active** from the moment the mouse is pressed on it until it is released, or while a text field is being edited. Only one item is active at a time, and it keeps the mouse even when the pointer leaves it.

A window or an item is **focused** when it receives the keyboard, so typed keys and the arrow keys go to it.

Strata enables keyboard navigation, so a person can also move without the mouse. The **nav cursor** is the highlight that shows which item the keyboard has selected; the arrow keys move it, and **Enter** activates the item under it. `ImGui::IsItemFocused()` says whether the last item holds it, and `ImGui::SetKeyboardFocusHere()` moves it to the next item you submit. In frame 3 of the example above, the button was hovered and active at the same time; focus is a third, separate thing.

## Popups show one thing at a time

A **popup** is a temporary window that opens on top of the others and closes when the person clicks outside it or presses **Escape**. Menus, drop-down lists and right-click menus are popups. You open one by name with `ImGui::OpenPopup` and then, every frame, call `ImGui::BeginPopup` with the same name. It returns true while the popup is open; you draw its items and call `ImGui::EndPopup`.

A **modal** is a popup that blocks everything below it: while it is open, clicks outside it do nothing, and the person must answer it. You use `ImGui::BeginPopupModal` for it, and `ImGui::CloseCurrentPopup` closes it from inside. Here is the shape of a question that closes on its answer.

```cpp pseudocode
if (openRequested)
	ImGui::OpenPopup("Reset?");
if (ImGui::BeginPopupModal("Reset?", nullptr, ImGuiWindowFlags_AlwaysAutoResize))
{
	ImGui::Text("Reset the counter?");
	if (ImGui::Button("Reset"))
		ImGui::CloseCurrentPopup();
	ImGui::EndPopup();
}
```

The library keeps a stack of open popups, one per level. The first popup is level 0. A popup opened from inside it, such as a menu inside a menu, is level 1. Opening a popup at a level replaces whatever was open at that level and closes everything above it.

So a modal opened from the top of a window, at level 0, closes a menu that is open at level 0. A question asked from inside the open modal sits at level 1 and leaves the modal alone.

For this reason Strata's editor draws its question about changes not yet saved inside the modal that is already open, through `EditorLayer::DrawDiscardQuestion`. A second modal opened at the top would close the first.

The same rule appears as a trap. `OpenPopup` hashes its name with the ID stack of the window it runs in, and a menu is a window of its own. So an `OpenPopup` inside a menu item names a different popup than the `BeginPopupModal` outside it. Exercise 3 avoids it by remembering the request in a flag and calling `OpenPopup` after the menu.

## Layout places each item at the cursor

The library lays items out with a **cursor**, a point inside the window. Each item is placed at the cursor, and then the cursor moves down by the item's height plus the spacing. That is why your items stack. `ImGui::SameLine()` returns the cursor to the line of the last item, to the right of it, so that the next item shares its line. `ImGui::SetCursorPosX` moves the cursor to a given distance from the left edge of the window; the Hierarchy uses it to move a row to the right by its depth.

How wide a window's contents may be is its content region. `ImGui::GetContentRegionAvail()` returns the size still free from the cursor to the edge. `ImGui::SetNextItemWidth(w)` sets the width of the next item: a positive number is a width in pixels, a negative number leaves that many pixels free at the right. If the content region is 400 pixels wide and a slider needs 100 pixels for its label, `SetNextItemWidth(-100.0f)` makes the slider 300 pixels wide.

A table lays its items out in rows and columns. `ImGui::BeginTable(id, columns, flags, size)` starts one. Then you declare the columns, `ImGui::TableHeadersRow()` draws the title row, and for each row you call `ImGui::TableNextRow()` and put one item in each column. You end it with `ImGui::EndTable()`, only if the begin call returned true.

Flags choose what a table can do: sort, change the size of its columns, scroll, hide a column. The Streaming panel's asset table uses seven, and sizes itself from the content region.

```cpp src="StrataEditor/src/Panels/StreamingPanel.cpp#L857-L866"
const ImGuiTableFlags flags = ImGuiTableFlags_Sortable | ImGuiTableFlags_RowBg | ImGuiTableFlags_ScrollY | ImGuiTableFlags_Resizable
	| ImGuiTableFlags_Hideable | ImGuiTableFlags_BordersInnerV | ImGuiTableFlags_NoSavedSettings;
// As many of the optional columns as leave the asset's name its least width.
int optionalColumns = static_cast<int>(c_OptionalColumns.size());
const float tableWidth = ImGui::GetContentRegionAvail().x;
while (optionalColumns > 0 && tableWidth < GetTableWidth(optionalColumns))
	optionalColumns--;
if (!ImGui::BeginTable("Assets", c_ColumnCount, flags, ImVec2(0.0f, std::max(ImGui::GetContentRegionAvail().y, ImGui::GetFrameHeight() * 4.0f))))
	return;
ImGui::TableSetupScrollFreeze(0, 1);
```

1. **Lines 857–858:** seven flags make the table sort and scroll, let the person size and hide columns, draw row backgrounds and a line between columns, and keep no settings in the layout file.
2. **Line 861:** the width is read once from the free space of the content region.
3. **Lines 864–865:** the height also comes from the free space, and the function returns early when the begin call returned false.
4. **Line 866:** the title row stays in place while the rows scroll.

A table reports what the person asked for. After a click on a title, `ImGui::TableGetSortSpecs()` returns the column and the direction, with a flag that says the order changed since you last looked. The panel reads the answer once, remembers it in two variables, and clears the flag.

```cpp src="StrataEditor/src/Panels/StreamingPanel.cpp#L877-L885"
if (ImGuiTableSortSpecs* specs = ImGui::TableGetSortSpecs(); specs && specs->SpecsDirty)
{
	if (specs->SpecsCount > 0)
	{
		m_SortColumn = static_cast<int>(specs->Specs[0].ColumnUserID);
		m_SortAscending = specs->Specs[0].SortDirection == ImGuiSortDirection_Ascending;
	}
	specs->SpecsDirty = false;
}
```

The editor's menu bar is a window with the menu bar flag. `ImGui::BeginMenuBar()` opens it, `ImGui::BeginMenu("File")` opens a menu inside it, and `ImGui::MenuItem("Open Project...")` is an item that returns true when it is chosen. A context popup, the menu on a right-click, is `ImGui::BeginPopupContextItem("RowMenu")` right after the item it belongs to, as in the Hierarchy rows. A drop-down list is `ImGui::BeginCombo("##EditLayer", preview)`, one `ImGui::Selectable` per choice, then `ImGui::EndCombo()`. Menus, context popups and drop-down lists are all popups, so each follows the rule of the last section and ends only when it began.

## Style is pushed and popped like a scope

The **style** is the set of numbers and colors that decide how everything looks: padding, spacing, rounding, and a color for every kind of part. A **style variable** is one number of it, and a **style color** is one color. You change one for a few items by pushing it, and you restore it by popping. The pushes form a stack, like the ID stack, and each push must meet its pop.

```cpp src="StrataEditor/src/UI/EditorPanelRegistry.cpp#L208-L213"
if (options.NoPadding)
	ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0.0f, 0.0f));
bool open = true;
const bool visible = ImGui::Begin(entry.WindowName.c_str(), &open, options.Flags);
if (options.NoPadding)
	ImGui::PopStyleVar();
```

In the registry's code above, a panel that asks for no padding pushes `ImGuiStyleVar_WindowPadding` as zero before `Begin` and pops it right after, so that only that window loses its padding. Colors work the same way with `ImGui::PushStyleColor` and `ImGui::PopStyleColor`. A push you forget to pop leaks into every later item of that window, until its `End` reports the missing pop, asserts by default and pops it. Strata's theme sets the global style through a callback of the ImGui layer, which runs it again whenever the size of the interface changes. The rest of the editor changes the style only with pushes.

## Docking puts windows into tabs, and imgui.ini remembers them

In the docking branch of the library, a window can be placed into a **dock space**: an area of the window of the program that holds windows as docked panels. A dock space is split into nodes. A **dock node** holds one window or several; where several share a node, the node draws a **tab bar** with one tab each, and the person chooses which shows. The editor creates one dock space that fills the program window, and every panel is docked in it.

The person can drag a panel by its tab and drop it on another node, or at an edge to split a node. The library does the hit testing, the splitting and the drawing. Your code only calls `Begin` for the panel, as always.

The name of a window must therefore stay the same. The library finds a window's saved place by the hash of its name. A window renamed without `###` is a new window to it, and appears floating with its dock place lost.

The library saves all of this in a text file, **imgui.ini**: a list of records with each window's position, size and dock node. It writes the file a few seconds after something changed, and reads it when the context starts. Strata names its file `EditorLayout.ini` and keeps it in the user's data folder; the `--layout` option picks another file, and a scripted run with `--frames` has none, so it never writes over yours. The file holds sections the editor adds to the library's own: they are taught in [the shell page](shell.md).

## Other libraries of the same style

Dear ImGui is one of several immediate-mode libraries. They share the idea that code describes the interface each frame, and differ in language, size and how much they do.

| Library | Language | Size and scope | Notable for |
| --- | --- | --- | --- |
| Dear ImGui | C++ | Large: many controls, tables, docking in a branch | Tools in games and engines |
| Nuklear | C, one :term[header]{id=header} | Medium: controls and a style system | Small, dependency free programs |
| microui | C | Tiny: about a thousand lines | Learning, and tight memory |
| egui | Rust | Large: controls, layout, web and native | Rust applications |

A library with fewer parts is simpler to read and to port; one with more parts saves you from writing the table, the dock and the text field yourself. For a tool as large as an editor, Strata took the one with the most.

## Strata's choice: one pinned version, docking, one window

Strata builds Dear ImGui 1.92.9 on its docking branch. It compiles the library's core only: `imgui.cpp`, its example window, its drawing, table and widget files, and the string helpers. The library's backends are not compiled. Strata writes its own, `ImGuiPlatform` for the window and `ImGuiRenderer` for the GPU, and the next page teaches them. The target is built with `IMGUI_DISABLE_OBSOLETE_FUNCTIONS` set, so a call under a name the library has retired does not compile.

The library is also built only for tools. Its target is omitted from the default build, so a program that does not link it, such as an exported game, contains none of it. The editor and the tests do link it. The editor runs with one main viewport: the library's option to move windows out of the main window into windows of the :term[operating system]{id=operating-system} is not enabled.

:::why[Why write both backends?]
The ready-made backends assume their own window and graphics code. Strata draws through NVRHI and owns its window through the platform layer, so a backend of the library would sit beside the engine instead of inside it. Writing two small backends keeps input, textures and timing in the engine's hands, and the library's core stays untouched.
:::

## What this choice cannot do

Windows cannot leave the main program window of the editor. The library's controls are weak for people who rely on a screen reader, and its layout is a simple flow of items, so a complicated design takes more code than in a retained library. Two items with one ID are not an error to the library, but a silent confusion; only a debug highlight warns about it. Strata's game user interface (UI) is a different system built for games: see [what Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **Two "OK" buttons in one scope.** The symptom is that one button seems dead, or both react to one click. Both buttons get the same ID. Give one of them a suffix (`"OK##Delete"`) or push a scope around each.
- **Renaming a window without `###`.** Its saved place is found by name, so the window appears new and floating, and its dock place is gone. Keep a stable part after `###` and change only the text before it.
- **Skipping `End` when `Begin` returns false.** The library finds calls without their partners at the end of the frame and asserts. Call `End` after every `Begin`, outside the `if`.
- **Reading a last-item query after another call.** The tooltip appears on the wrong item. Put the query right after the item it asks about.
- **A push without its pop.** Colors or padding leak into later items. Pop in the same function that pushed, on every path.
- **`OpenPopup` inside a menu.** The popup never appears, because the name is hashed in the menu's scope. Remember the request and open the popup outside the menu.

## Summary

- A frame is `NewFrame`, every layer's `OnImGuiRender`, then `Render`, which produces draw data; Strata's `ImGuiModule` makes the calls, and a click seen after an item's text shows one frame later.
- `Begin` and `BeginChild` always need their `End`, whatever they return; the other begin calls end only when they returned true.
- An ID is a hash of the label under the ID stack; `##` adds hidden text to it, `###` replaces what came before, and `PushID` gives each row its own scope.
- One popup stays open per level, so a modal opened at the top closes the open one; open a modal outside the menu that asks for it.
- The cursor, `SameLine`, content region, tables that sort, menus and pushed styles build a window; the editor docks its panels and keeps the layout in a file.

## Check yourself

1. In the scratch layer, the `Text("Count: %d", m_Count)` call comes before the `Button("Add")` call. The button is clicked and `m_Count` becomes 1 in frame 4. In which frame does the window first show "Count: 1"?

   :::answer{tests="frame-calls"}
   In frame 5. The text call of frame 4 ran before the button call saw the click, so it printed 0. A frame draws the calls in the order your code makes them, and the next frame is the first to start from the new value. Moving the text after the button shows 1 in frame 4.
   :::

2. A panel calls `if (ImGui::Begin("Tools")) { ... ImGui::End(); }`. What goes wrong when the panel is collapsed? (a) Nothing: a collapsed window needs no end. (b) `Begin` returns false, `End` is skipped, and the library reports the missing call. (c) The window is drawn twice.

   :::answer{tests="window-end"}
   (b) is right. A collapsed window makes `Begin` return false, and the `End` inside the `if` is then skipped, which is a programmer error that the library reports and, by default, asserts on. (a) is the common mistake: `End` is the exception, and it is needed whatever `Begin` returned. (c) describes nothing the library does. The fix is to move `End` outside the `if`.
   :::

3. Inside a window named "A", you call `Button("Go")`, then `Button("Go##2")`, then `PushID(7)`, then `Button("Go")` and `PopID()`. How many different IDs do the three buttons have?

   :::answer{tests="id-stack"}
   Three. The first two differ because the hash covers the whole text, including the hidden `##2`. The third has the same label as the first, but it runs under the pushed scope 7, which seeds its hash differently. If the third button had run without the push, it would share the first button's ID.
   :::

4. A menu item of your window should open a modal. You call `OpenPopup("Sure?")` inside the item's `if`, and `BeginPopupModal("Sure?")` later in the window. The modal never shows. What is the cause, and what is the fix?

   :::answer{tests="popups"}
   The menu is a window of its own, so the name "Sure?" is hashed with the menu's ID stack inside it, and with the window's stack outside it: the two names are different popups. Remember the request in a flag inside the item, and call `OpenPopup` after the menu has ended, in the scope that holds `BeginPopupModal`.
   :::

5. You push a style color before a button and pop it after the next button, in a function that returns early between them. What happens?

   :::answer{tests="layout-style"}
   On the early return, the pop never runs, so the color stays on the stack. Every later item of that window is drawn with that color until the window's `End`, where the library reports the missing pop, asserts by default and pops it. Pop on every path, or push and pop in one function with no return between.
   :::

## Exercises

1. **Basic.** Apply the patch of this exercise to a source build of the editor, run it, and find the window "Scratch". Click **Add** three times. Then move the `Text` call after the `Button` call and predict what the window shows in the frame of the click before you run it again.

   :::answer[Worked solution]{tests="frame-calls window-end" solution="tutorials/editor-ui/imgui/exercise-1.patch"}
   The patch adds a `ScratchLayer` to `StrataEditor/src/EditorApplication.cpp`, pushes it after the editor's layer, and its `OnImGuiRender` draws the window with `Begin`, a counter, `SameLine`, a button and `End`. After three clicks the text reads "Count: 3". With the text after the button, the frame of the click already shows the new value, so the lag of the example disappears. Rebuild the editor target and configure again only if you added files; this patch adds none.
   :::

2. **Medium.** Make the layer show ten rows, each a name and a **Delete** button. Predict what happens when you click the button of the fifth row if you do not push an ID for each row. Run it, then fix it as the Hierarchy does.

   :::answer[Worked solution]{tests="id-stack" solution="tutorials/editor-ui/imgui/exercise-2.patch"}
   Without a push, all ten buttons have the one ID `Delete` in the Scratch window, so the library cannot tell the rows apart. With its default settings it highlights the conflict when you hover a button, and a click does not reliably delete the row you meant. The patch wraps each row in `PushID` and `PopID` with the row's index, which gives ten IDs as the last lines of the sketch showed. A stable number such as an entity's UUID would be better than an index once rows can move.
   :::

3. **Hard.** Add a menu bar with a **Counter** menu and a **Reset counter** item. The item must open a modal that asks "Reset the counter?" and closes on **Reset** or **Cancel**. Use no second popup.

   :::answer[Worked solution]{tests="popups layout-style" solution="tutorials/editor-ui/imgui/exercise-3.patch"}
   The window is begun with the menu bar flag, and `BeginMenuBar`, `BeginMenu` and `MenuItem` each end only when they returned true. The item sets a flag, and after `EndMenuBar` the code calls `OpenPopup` in the window's own scope, so that `BeginPopupModal` finds the same name. The modal draws the question and two buttons, `CloseCurrentPopup` runs on either, and `Reset` also sets the count to 0. The window's `End` stays outside the `if`. The patch replaces exercise 1's layer with this version.
   :::

## Where it lives in Strata

- `Strata/vendor/imgui/imgui.h` and `Strata/vendor/CMakeLists.txt`: the pinned Dear ImGui 1.92.9 and its target.
- `Strata/src/Strata/ImGui/ImGuiModule.cpp`: the module that calls each layer's `OnImGuiRender` every frame.
- `Strata/src/Strata/ImGui/ImGuiLayer.cpp`: the context, `NewFrame`, `Render` and the layout file.
- `Strata/src/Strata/Core/Layer.h`: the `Layer` class with `OnImGuiRender`.
- `StrataEditor/src/UI/EditorPanelRegistry.cpp`: panel windows and their `###` names.
- `StrataEditor/src/Panels/SceneHierarchyPanel.cpp`: rows that push their UUID, context popups and a drop-down list.
- `StrataEditor/src/Panels/StreamingPanel.cpp`: the table that sorts.
- `StrataEditor/src/EditorLayer.cpp`: the dock space, the menu bar and `DrawDiscardQuestion`.
- `StrataEditor/src/UI/Widgets.h`: the kit's `OpenModal`, `BeginModal` and `EndModal`.

## Further reading

- Dear ImGui's repository and its frequently asked questions (github.com/ocornut/imgui): the library's own account of IDs, popups and the cursor. Beginner to intermediate.
- Dear ImGui's example window (`imgui_demo.cpp` in the repository): every control and layout call with its code beside it. Beginner.
- Nuklear (github.com/Immediate-Mode-UI/Nuklear): a single-header immediate-mode library in C. Intermediate.
- microui (github.com/rxi/microui): a very small immediate-mode library in C, short enough to read in one sitting. Intermediate.
- egui (github.com/emilk/egui): an immediate-mode library in Rust. Intermediate.
