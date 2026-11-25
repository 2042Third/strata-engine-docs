# Brief: `editor-ui/imgui`

| Field | Value |
| --- | --- |
| Title | Dear ImGui from first principles |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `core/windows-events`, `editor-ui/immediate-mode` |
| From | editor-ui ch. 3 (frames, windows, items, IDs, popups, docking; exercises in a scratch layer) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/imgui` — Dear ImGui from first principles

**Covers.** Dear ImGui from first principles, on a scratch layer the reader adds to a source build: one `Layer` whose
`OnImGuiRender` draws a window with a counter. The order: the frame (`NewFrame`, the widget calls, `Render` and the
draw data it produces, and that Strata's ImGui module makes these calls); windows (`Begin` and `End`, the bool `Begin`
returns, `End` always called) and child windows; items (a call draws and returns the interaction, and "last item"
queries such as `IsItemHovered` and `GetItemRectMin`); IDs (hashes of labels and pushed scopes, the ID stack, the `##`
and `###` suffixes), with Strata's examples: Hierarchy rows push their entity's UUID bytes as their ID
(`StrataEditor/src/Panels/SceneHierarchyPanel.cpp:742`) and panel windows are named `<icon> <title>###<id>`. Then
hovered, active and focused, and keyboard navigation with its nav cursor; popups and modals, and the rule that ImGui
keeps one popup per level, so a modal opened at the top closes the open one; layout and containers (the cursor and
`SameLine`, the content region and item widths, tables with their flags and sort specs, the menu bar and its menus,
context popups, combos), with the Streaming panel's sortable table as the example; style, style variables and style
colors with their push and pop; the ImGui context; docking as a person sees it (dock spaces, nodes, tab bars) and the
`imgui.ini` file.

The approaches table puts Dear ImGui beside other immediate-mode libraries (Nuklear, microui, egui). Strata's choice:
Dear ImGui 1.92.9 on its docking branch, built from its core only and without its obsolete functions, with one main
viewport. Common mistakes: two "OK" buttons in one scope share an ID; a window renamed without `###` loses its place in
the dock; `End` skipped when `Begin` returns false; a "last item" query read after another call. The exercises grow
the scratch layer: a counter, a list whose rows push their IDs, a modal. At the end the reader can write a small tool
window, give its widgets unique IDs and open a modal.

**Leaves out.**

- How ImGui's input and draw data reach the window and the GPU → `editor-ui/imgui-backends`
- How the editor builds a default layout and keeps panels' open states → `editor-ui/shell`
- Writing custom widgets on `InvisibleButton` → `editor-ui/widget-kit`
- Clipped lists and multi-selection → `editor-ui/lists`
- Shortcut routing → `editor-ui/game-view`
- Why the editor's UI is immediate → `editor-ui/immediate-mode`

**Fit.** `fits`: about 5,250 words against L (5,000). Twelve terms taught from zero in one scratch layer take the most,
with layout and containers (about 450 words, `new:26`) and three exercises in the same layer.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:299` | concept | home | ImGui's model: the frame, windows and child windows, popups and modals (one popup per level), the last item, the ID stack, `##` and `###`, hovered, active and focused, keyboard navigation; Strata's examples and pitfalls |
| `new:1` | feature | home | Dear ImGui 1.92.9, docking branch, built from its core only (Strata writes both backends) with `IMGUI_DISABLE_OBSOLETE_FUNCTIONS`, linked only by tools. Evidence: `Strata/vendor/imgui/imgui.h:32`; `Strata/vendor/CMakeLists.txt:89-100` |
| `editor-ui:702-709` | term | home | Dear ImGui, the ImGui context, ID and ID stack, `##` and `###`, item, window and child window, popup and modal, dock space, dock node and tab bar |
| `editor-ui:711` | term | home | `imgui.ini` (Strata's is `EditorLayout.ini`, with sections of its own taught on `editor-ui/shell`) |
| `editor-ui:726` | term | home | Style, style variable and style color, with their push and pop stacks |
| `editor-ui:732-733` | term | home | Nav cursor; hovered, active and focused |
| `editor-ui:132` | feature | use | Panel windows named `<icon> <title>###<id>`, as the example of a stable window ID |
| `editor-ui:619` | rule | link | One popup per level, which is why the editor draws nested questions inside the open modal (`editor-ui/shell`) |
| `editor-ui:35` | feature | link | The ImGui module calls `NewFrame` and `Render` each frame (`editor-ui/imgui-backends`) |
| `new:6` | not-done | link | One main viewport: ImGui's multi-viewports are not used |
| `new:26` | concept | home | Layout and containers (critic-editor-ui-1, about 450 words): the cursor and `SameLine`, the content region and item widths, tables with their flags and sort specs, the menu bar, menus and menu items, context popups, combos; the dock's tab bars are taught with docking, since the editor draws no tab bar of its own; drag and drop is `editor-ui/lists`'. Evidence: `StrataEditor/src/Panels/StreamingPanel.cpp:857-877` (a sortable, resizable table sized from the content region); `StrataEditor/src/EditorLayer.cpp:1449-1628` (`DrawMenuBar`); `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:648`, `:925` (context popups), `:512` (a combo); `grep -rn BeginTabBar StrataEditor/src` finds nothing |
| `new:27` | hands-on | home | Exercises (D27), in the page's scratch layer: a counter whose button and text share a line (Basic, done); a list of ten rows, each with a "Delete" button, whose clicks all reach the first row until each row pushes its own ID, as the Hierarchy pushes an entity's UUID (Medium, predict then run); a modal opened from a menu item that asks a question and closes on its answer (Hard, extend). The solutions are patches against the pin. Evidence: `Strata/src/Strata/Core/Layer.h:23` (`OnImGuiRender`); `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:742`; `StrataEditor/src/UI/Widgets.h:150-156` (the kit's modals) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Windows, events, layers and the layer stack (`OnImGuiRender`) | `core/windows-events` | must |
| Building Strata from source and running a change | `core/first-change` | must |
| Classes, inheritance and virtual functions (a `Layer` subclass) | `basics/cpp-classes` | must |
| Hashes (an ID is a hash of a string) | `basics/data-formats` | helps |
| The immediate-mode idea: code describes the UI every frame | `editor-ui/immediate-mode` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `active` | active | - |
| `child-window` | child window | - |
| `dear-imgui` | Dear ImGui | - |
| `dock-space` | Dock space | dock node, tab bar |
| `focused` | focused | - |
| `hovered` | Hovered | - |
| `id` | ID | ID stack |
| `imgui-context` | ImGui context | - |
| `imgui-ini` | imgui.ini | - |
| `item` | Item | - |
| `modal` | modal | - |
| `nav-cursor` | Nav cursor | - |
| `popup` | Popup | - |
| `style` | Style | style var, style color |
| `window` | Window | - |
