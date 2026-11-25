---
id: editor-ui/tutorial-panel
title: "Tutorial: adding a panel"
description: "Add a Selection Summary panel to the editor: register it, draw it with the widget kit, dock it in the default layout and test it without a screen."
kind: tutorial
size: L
tracks: [E]
needs: [editor-ui/ui-testing]
time: 150
learn:
  - id: register-panel
    text: add a panel class to the editor and register it, so that the View menu, editor.showPanel and the layout file know it
  - id: draw-panel
    text: write a panel's drawing with the widget kit, theme colors and font-relative sizes, with a button that runs a command as the person
  - id: dock-layout
    text: change the default layout to dock a new panel and predict why the layout version must rise
  - id: test-panel
    text: write a harness test that selects entities, clicks the panel's button and reads the journal, and run the source scans
since: 0.3.0
status: final
---

## What you will make

You will add a panel named **Selection Summary** to the editor. It shows how many entities you selected and which components all of them have, and its button points the Scene view at them. At the end it behaves like the panels that ship with Strata: it is in the View menu, remembers whether it is open, sits in the default layout and has tests.

```mermaid caption="The new panel is a tab beside the Inspector. It shows a count, a list of shared components and one button." alt="A sketch of the editor window. The Hierarchy is at the left, the Scene view in the middle and the Inspector at the right, with two more tabs behind it: Asset and Selection Summary. The Selection Summary tab holds the text 2 entities selected, a list with three bullets and a button that frames the selection."
flowchart LR
    H["Hierarchy"] --- S["Scene view"] --- R["Inspector | Asset | Selection Summary"]
    R --> P["2 entities selected<br/>Name, Transform, Point Light<br/>Frame selection"]
```

## Why the registry owns the window

You select three entities in a large scene and want to know three things. How many did you select? What do they have in common? Where are they? A panel that answers all three at a glance is a good first panel to write, because it needs a list, a button and a command.

Take a scene with a `Lamp` and a `Torch`, which both have a `Point Light`, and a `Crate`. The `Lamp` and the `Crate` also have a `Tag`. Every entity has a `Name` and a `Transform`.

Select the `Lamp` and the `Torch`. The panel should say "2 entities selected" and list `Name`, `Transform` and `Point Light`. Select the `Lamp` and the `Crate` instead. The list becomes `Name`, `Transform` and `Tag`, because the light is no longer shared. These sentences are the specification, and the tests of the last section check them.

A panel is a window of the editor with contents. You might expect a new panel to open its own window and draw into it. Strata does not allow that: a panel only draws its contents, and the panel registry (`EditorPanelRegistry`) creates the window around them.

:::rule
**Panels never call `ImGui::Begin`.** A panel registers with the panel registry, which begins the window, tracks whether it is open and gives it a stable name. The reason is that the registry then gives every panel the View menu item, the saved open state, focus and docking for free. The rule is in the Editor section of `AGENTS.md`, and [Dear ImGui from first principles](imgui.md) explains how a window begins and ends.
:::

You describe the panel to the registry with seven fields. The registry owns the rest.

```cpp src="StrataEditor/src/UI/EditorPanelRegistry.h#L83-L93"
struct EditorPanelDescriptor
{
	std::string Id;             // Stable and unique: the ImGui id of the window and the key of its open state in imgui.ini
	std::string Title;          // Shown on the tab and in the View menu
	const char* Icon = nullptr; // An Icons:: constant shown before the title (optional)
	std::string MenuPath;       // Submenu of the View menu the toggle lives in ("" for the menu itself, "Debug" for View > Debug)
	bool OpenByDefault = true;
	// A launcher panel has no View menu item and no saved open state; at most one registers.
	EditorPanelPlacement Placement = EditorPanelPlacement::Docked;
	std::function<Scope<EditorPanel>()> Create;
};
```

1. **Line 85:** `Id` is stable and unique. It names the window to :term[ImGui]{id=dear-imgui} and keys the saved open state, so you never change it after release.
2. **Line 86:** `Title` is what the tab and the View menu show.
3. **Lines 88–89:** `MenuPath` picks a menu inside the View menu, and `OpenByDefault` says whether a fresh layout shows the panel.
4. **Line 92:** `Create` is a factory. The registry calls it once and owns the panel it returns.

Each frame the registry begins the window of every open panel, calls the panel's `OnImGuiRender` while the window is visible, and ends the window.

```mermaid caption="Each frame the registry begins the window of an open panel, asks the panel to draw its contents and ends the window." alt="A flow of four boxes from left to right. The registry begins the window with the panel's title. The registry calls the panel to draw. The panel draws its contents. The registry ends the window."
flowchart LR
    A["Registry begins the window"] --> B["Registry calls the panel"]
    B --> C["Panel draws its contents"]
    C --> D["Registry ends the window"]
```

The window's ImGui name is the icon, the title, three `#` characters and the :term[id]{id=id}. ImGui :term[hashes]{id=hash} only the part after the three characters, so you can rename a panel's title without losing the position the person gave it.

## What you need

- The source build of [your first engine change](../core/first-change.md): a clone at the book's commit, its :term[submodules]{id=submodule}, and a `Debug` build of the editor, the command-line client and `StrataTests`, with the tests passing. Below, `<preset>` stands for your system's preset: `windows`, `linux` or `macos`.
- A copy of the `ThirdPerson` sample for entities to select. Start the built editor, open **File ▸ Open Sample** and choose the sample in its list; a dialog then copies the sample to a folder you pick. The sample's scene holds many entities.
- Time: about two and a half hours. Each rebuild of the editor takes a few minutes, and the first run of the tests takes longer.
- No file to import. You add three files, change two and run one test suite.
- Knowledge of the pieces this page uses: the [widget kit](widget-kit.md), the item probe and [the test rig](ui-testing.md).

:::files[The files of the change]

- `StrataEditor/src/`
  - `Panels/SelectionSummaryPanel.h`, `Panels/SelectionSummaryPanel.cpp`: new, the panel
  - `EditorLayer.h`, `EditorLayer.cpp`: the id, the registration, the docking and the layout version
- `StrataTests/src/Editor/`
  - `SelectionSummaryUITests.cpp`: new, the suite of this page

:::

The commands of this page keep your own layout safe. The editor takes the option `--layout <file.ini>`, which keeps the window layout in a file you name, so every run below uses a scratch file and never touches the layout you use every day.

## Write the panel class

A panel is a class that derives from `EditorPanel`. Its one required function is `OnImGuiRender`. You start with the class and the part that works out what to show, and you leave the drawing for the third section.

:::::steps

1. Create the file `SelectionSummaryPanel.h` in the folder `StrataEditor/src/Panels/`, with the class. It remembers the count, the names of the shared components and the three numbers the lines were built from.

   ```cpp src="book:tutorials/editor-ui/tutorial-panel/SelectionSummaryPanel.h#L1-L36"
   #pragma once

   #include "UI/EditorPanelRegistry.h"

   #include <cstdint>
   #include <string>
   #include <vector>

   namespace Strata
   {

   	class Scene;

   	// The selected entities in one glance: how many there are, which components all of them have, and a button that
   	// frames them in the Scene view (camera.focus). The lines are rebuilt when the selection, the undo history or the
   	// scene changes; an idle frame compares three numbers.
   	class SelectionSummaryPanel : public EditorPanel
   	{
   	public:
   		void OnImGuiRender(EditorPanelContext& panelContext) override;

   		// What the last drawn frame showed (for tests).
   		size_t GetSelectedCount() const { return m_SelectedCount; }
   		const std::vector<std::string>& GetSharedComponents() const { return m_SharedComponents; }
   	private:
   		void Rebuild(EditorContext& context);
   		void FrameSelection(EditorPanelContext& panelContext) const;
   	private:
   		size_t m_SelectedCount = 0;
   		std::vector<std::string> m_SharedComponents; // Display names, in registration order

   		// What the lines were built from.
   		const Scene* m_Scene = nullptr;
   		uint64_t m_SelectionVersion = UINT64_MAX;
   		uint64_t m_HistoryVersion = UINT64_MAX;
   	};
   ```

   1. **Lines 3–12:** the registry's :term[header]{id=header} gives the :term[base class]{id=base-class} and the context. `Scene` is only declared, since the class stores a pointer and never needs its definition.
   2. **Line 20:** the one function every panel must have. It takes the context that holds the editor state, the commands and the runner.
   3. **Lines 23–24:** two read functions for the tests, since a test cannot read pixels.
   4. **Lines 33–35:** what the cached lines were built from: the scene, the selection version and the undo history version. The largest value means "nothing built yet".

   **You should see:** a header that ends with the closing brace of the :term[namespace]{id=namespace}, and no other file.

   **If you do not see it:** a :term[compiler error]{id=compile-error} about `EditorPanel` later means the include of `UI/EditorPanelRegistry.h` at the top of the :term[header]{id=header} is missing.

2. Create `SelectionSummaryPanel.cpp` in the same folder, with the includes and `Rebuild`. This function turns the selection into a count and a list. It runs only when the numbers of the header change, never on an idle frame.

   ```cpp src="book:tutorials/editor-ui/tutorial-panel/SelectionSummaryPanel.cpp#L1-L55"
   #include "Panels/SelectionSummaryPanel.h"

   #include "Editor/EditorContext.h"
   #include "Editor/UndoStack.h"
   #include "UI/EditorActions.h"
   #include "UI/Icons.h"
   #include "UI/Theme.h"
   #include "UI/Widgets.h"

   #include <Strata/Reflection/ComponentRegistry.h>
   #include <Strata/Reflection/PropertyJson.h>
   #include <Strata/Scene/Entity.h>
   #include <Strata/Scene/Scene.h>

   #include <imgui.h>
   #include <nlohmann/json.hpp>
   #include <spdlog/fmt/fmt.h>

   #include <algorithm>
   #include <utility>

   namespace Strata
   {

   	void SelectionSummaryPanel::Rebuild(EditorContext& context)
   	{
   		m_SelectedCount = 0;
   		m_SharedComponents.clear();
   		const Ref<Scene>& scene = context.GetActiveScene();
   		if (!scene)
   			return;

   		// Selected entities that no longer exist (deleted since) do not count.
   		std::vector<Entity> entities;
   		entities.reserve(context.GetSelection().size());
   		for (const UUID id : context.GetSelection())
   		{
   			if (Entity entity = scene->GetEntityByUUID(id))
   				entities.push_back(entity);
   		}
   		m_SelectedCount = entities.size();
   		if (entities.empty())
   			return;

   		const entt::registry& registry = scene->GetRegistry();
   		for (const ComponentInfo* info : ComponentRegistry::GetAll())
   		{
   			if (info->IsHidden())
   				continue;
   			const bool onAll = std::all_of(entities.begin(), entities.end(),
   				[&](const Entity& entity) { return info->Has(registry, entity.GetHandle()); });
   			if (onAll)
   				m_SharedComponents.push_back(info->DisplayName);
   		}
   	}
   ```

   1. **Line 17:** the engine takes its formatting library from the logging library, so the include is `<spdlog/fmt/fmt.h>`. A bare `<fmt/format.h>` is not on the editor's include path.
   2. **Lines 36–40:** the selection holds identifiers, and a selected entity may have been deleted since, so the code finds each one and skips the missing ones.
   3. **Line 46:** the component registry lists every component type the editor knows, hidden ones included.
   4. **Line 48:** hidden components such as the identifier and the relationship are internal, so the summary omits them.
   5. **Lines 50–53:** a component is shared when every selected entity has it. The list keeps the registry's order.

   Below the function, add an empty drawing function so that the class is complete. It is the single line `void SelectionSummaryPanel::OnImGuiRender(EditorPanelContext&) {}`, followed by the closing brace of the :term[namespace]{id=namespace}.

   **You should see:** the file ends with the empty function and `}`.

   **If you do not see it:** a warning about an unused parameter means you named the parameter. Leave it without a name until section three.

3. Configure again, then build the editor. The build collects :term[source files]{id=source-file} when it configures, so a new file is part of the build only after this step.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --target StrataEditor --parallel
   ```

   **You should see:** the build ends without errors, and its log names `SelectionSummaryPanel.cpp` among the compiled files.

   **If you do not see it:** if the log never names your file, the :term[configure step]{id=configure-step} did not run. Run the first command again.

   **Why:** nothing refers to the class yet, so the editor behaves as before. A new file compiled but unused is the safest first state.

:::::

## Register the panel

The registry knows only the panels someone registers. The editor registers its own in one function, and you add yours there.

:::::steps

1. Give the panel an id constant in `StrataEditor/src/EditorLayer.h`, next to those of the built-in panels. The id is the string that `editor.showPanel` and the layout file will use.

   ```diff src="book:tutorials/editor-ui/tutorial-panel.patch#hunk-4"
    		constexpr const char* c_Problems = "Problems";       // ProblemsPanel: script build diagnostics and crashes
    		constexpr const char* c_Activity = "Activity";       // ActivityPanel, opened from the viewport's agent chip or the View menu
    		constexpr const char* c_ProjectSettings = "ProjectSettings"; // ProjectSettingsPanel, opened from File > Project Settings...
   +		constexpr const char* c_SelectionSummary = "SelectionSummary"; // SelectionSummaryPanel: the selection's count and shared components
    		constexpr const char* c_Welcome = "Welcome"; // The launcher (WelcomePanel)
    	}
    
   ```

   **You should see:** one new line after `c_ProjectSettings`.

   **If you do not see it:** if the :term[compiler]{id=compiler} later says `c_SelectionSummary` is unknown, the line sits outside the namespace `EditorPanels`.

2. Register the panel in `RegisterBuiltinPanels` in `StrataEditor/src/EditorLayer.cpp`. First read the :term[lambda]{id=lambda} `add` that the function defines, since your line calls it.

   ```cpp src="StrataEditor/src/EditorLayer.cpp#L495-L508"
   auto add = [this](const char* id, const char* title, const char* icon, std::function<Scope<EditorPanel>()> create,
   	EditorPanelPlacement placement = EditorPanelPlacement::Docked, bool openByDefault = true)
   {
   	EditorPanelDescriptor descriptor;
   	descriptor.Id = id;
   	descriptor.Title = title;
   	descriptor.Icon = icon;
   	descriptor.Placement = placement;
   	descriptor.OpenByDefault = openByDefault;
   	descriptor.Create = std::move(create);
   	std::string error;
   	if (!m_Panels.Register(std::move(descriptor), &error))
   		ST_ERROR("Could not register the panel '{}': {}", id, error);
   };
   ```

   1. **Lines 495–496:** `add` takes an id, a title, an icon and a factory, and its last two parameters default to a docked panel that is open.
   2. **Lines 498–504:** it fills a :term[descriptor]{id=descriptor} with the fields the header showed.
   3. **Lines 505–507:** `Register` returns false with a reason, and the editor logs it. A taken id or an empty title is a failure here, never a crash.

   Then add the include of `Panels/SelectionSummaryPanel.h` among the other panel includes, and your line right after the Asset panel's. The panels are drawn in the order of these lines, and the order matters: on the first run, the window drawn last takes the focus, and its tab shows in its node. That window must stay the Content Browser, so your line goes before the Console's.

   ```diff src="book:tutorials/editor-ui/tutorial-panel.patch#hunk-2"
    		add(EditorPanels::c_Hierarchy, "Hierarchy", Icons::ListTree, []() { return CreateScope<SceneHierarchyPanel>(); });
    		add(EditorPanels::c_Inspector, "Inspector", Icons::SlidersHorizontal, []() { return CreateScope<InspectorPanel>(); });
    		add(EditorPanels::c_AssetInspector, "Asset", Icons::FileBox, []() { return CreateScope<AssetInspectorPanel>(); });
   +		// Open from the start, docked beside the Inspector by the default layout. Before the Console: the window drawn last on
   +		// first run takes the focus and shows its tab, which stays the Content Browser's.
   +		add(EditorPanels::c_SelectionSummary, "Selection Summary", Icons::Focus, []() { return CreateScope<SelectionSummaryPanel>(); });
    		add(EditorPanels::c_Console, "Console", Icons::Terminal, []() { return CreateScope<ConsolePanel>(); });
    		add(EditorPanels::c_Problems, "Problems", Icons::CircleAlert, []() { return CreateScope<ProblemsPanel>(); });
    		add(EditorPanels::c_ContentBrowser, "Content Browser", Icons::FolderOpen, []() { return CreateScope<ContentBrowserPanel>(); });
   ```

   **You should see:** `Icons::Focus` as the icon, the title "Selection Summary" and no further arguments, so the panel is docked and open by default.

   **If you do not see it:** an error that `SelectionSummaryPanel` is not declared means the include is missing. It goes next to `Panels/SceneHierarchyPanel.h`.

3. Build the editor and start it with the scratch layout. Open a project first: the editor shows its launcher, not its panels, while no project is open.

   ```sh
   cmake --build build/<preset> --config Debug --target StrataEditor --parallel
   build/<preset>/bin/Debug/StrataEditor --layout selection-summary.ini
   ```

   **You should see:** the editor starts. Open your copy of the sample with **File ▸ Open Recent**, then open the **View** menu. It lists the entry "Selection Summary" with a check mark, because the panel is open by default. A window titled "Selection Summary" with an empty body floats over the editor.

   **If you do not see it:** if the menu lacks the entry, check the log of the editor for `Could not register the panel`, which names the reason.

   **Why:** the window floats because the layout file is new and says nothing about where your panel lives. Section four fixes that.

4. Close the panel with its tab close button, then open it again through a command. The command `editor.showPanel` opens a panel and brings it to the front. Its list of panel names comes from the registry, so your panel is in it without any further change. Write the parameters to a file, because quotes in :term[JSON]{id=json} are error-prone in a shell. Save `show.json`:

   ```json
   { "panel": "SelectionSummary" }
   ```

   Then run `StrataCLI call editor.showPanel @show.json` in a second terminal, while the editor runs.

   **You should see:** the call answers with `{"panel": "SelectionSummary"}`, and the window returns.

   **If you do not see it:** an error that the editor has no such panel means the editor is an older build. Close it, build again and start it again. An error that the call needs a window means the editor runs headless.

5. Find the open state in the layout file. Quit the editor, or wait a few seconds, then open `selection-summary.ini` in a text editor.

   **You should see:** a section `[StrataPanels][Open]` that holds a line for each panel, and the line of your panel ends with 1. If you closed the panel before quitting, it ends with 0. The section `[StrataPanels][Layout]` holds the layout version, 5.

   **If you do not see it:** ImGui writes the file a few seconds after a change and when the editor quits. A file that is missing or old means ImGui has not written it yet. Quit the editor and look again.

   **Why:** the registry keeps the open states in this file through a :term[settings handler]{id=settings-handler} of its own, and the saved state of an id wins over `OpenByDefault`. Keep this file: section four needs its layout version, 5.

:::::

## Draw the panel with the widget kit

The empty function becomes the real drawing. Three rules shape it. Colors come from the theme, sizes follow the :term[font]{id=font}, and controls come from the widget kit, whose widgets record themselves in the item probe, so that tests find them by key.

:::::steps

1. Write the function that runs the button's command, `FrameSelection`, above `OnImGuiRender`. It gathers the selected identifiers as JSON and runs `camera.focus`, the command that points the editor camera at entities.

   ```cpp src="book:tutorials/editor-ui/tutorial-panel/SelectionSummaryPanel.cpp#L57-L64"
   void SelectionSummaryPanel::FrameSelection(EditorPanelContext& panelContext) const
   {
   	nlohmann::json entities = nlohmann::json::array();
   	for (const UUID id : panelContext.Context.GetSelection())
   		entities.push_back(UUIDToJson(id));
   	// RunEditorCommand runs the command as the person's: the activity journal records the UI as its source.
   	RunEditorCommand(panelContext.Context, panelContext.Commands, "camera.focus", { { "entities", std::move(entities) } });
   }
   ```

   **You should see:** eight lines, and a call of `RunEditorCommand` as the last statement.

   **If you do not see it:** a :term[link error]{id=link-error} about `FrameSelection` later means the function sits inside `Rebuild`'s braces. It stands on its own.

   **Why:** `RunEditorCommand` runs the command with the origin `CommandSource::UI`, so the activity journal records that the person clicked, and a failure shows as a toast. A panel never changes the scene itself: every change goes through a command.

2. Replace the empty `OnImGuiRender` with the real one. Its first part decides whether the lines are stale. Its second part draws.

   ```cpp src="book:tutorials/editor-ui/tutorial-panel/SelectionSummaryPanel.cpp#L66-L98"
   void SelectionSummaryPanel::OnImGuiRender(EditorPanelContext& panelContext)
   {
   	EditorContext& context = panelContext.Context;
   	const UI::ThemeColors& colors = UI::GetThemeColors();

   	const Scene* scene = context.GetActiveScene().get();
   	const uint64_t selectionVersion = context.GetSelectionVersion();
   	const uint64_t historyVersion = context.GetUndoStack().GetVersion();
   	if (scene != m_Scene || selectionVersion != m_SelectionVersion || historyVersion != m_HistoryVersion)
   	{
   		Rebuild(context);
   		m_Scene = scene;
   		m_SelectionVersion = selectionVersion;
   		m_HistoryVersion = historyVersion;
   	}

   	if (m_SelectedCount == 0)
   	{
   		UI::CenteredText("SelectionSummary.Empty", "Select entities in the Hierarchy or the Scene view to summarize them.", colors.TextSecondary);
   		return;
   	}

   	ImGui::TextUnformatted(fmt::format("{} {} selected", m_SelectedCount, m_SelectedCount == 1 ? "entity" : "entities").c_str());
   	ImGui::TextColored(colors.TextSecondary, "Components all of them have");
   	for (const std::string& name : m_SharedComponents)
   		ImGui::BulletText("%s", name.c_str());

   	ImGui::Spacing();
   	UI::ButtonStyle style;
   	style.Primary = true;
   	if (UI::ActionButton("SelectionSummary.Frame", Icons::Focus, "Frame selection", "Point the Scene view at the selected entities", style))
   		FrameSelection(panelContext);
   }
   ```

   1. **Lines 71–80:** three numbers decide whether to rebuild. An idle frame costs three comparisons, as the rule for cached views asks, and the scene's pointer joins them because play mode draws a copy of the scene.
   2. **Lines 82–86:** nothing selected: a centered hint in the theme's secondary text color, with a probe key, then an early return.
   3. **Lines 88–91:** the count and the list, drawn with ImGui's own text calls and the editor's fonts. The color is a theme token, never a number.
   4. **Lines 93–97:** the button comes from the kit: it takes a probe key, an icon, a label and a tooltip, and the primary style fills it with the accent.

   **You should see:** no `ImGui::Begin` anywhere, no color written as numbers and no size in pixels.

   **If you do not see it:** if you want a gap between two blocks, ask the style. The call `ImGui::Spacing()` scales with the font. A fixed `ImVec2(0.0f, 40.0f)` does not, and the :term[source scan]{id=source-scan} of section five would fail it.

   **Why:** the cached lines show a limit. A script can add a component to a selected entity during play without an :term[undo step]{id=undo-step}, and the lines change only when the selection or the history changes. The panel accepts that, since one comparison of three numbers is cheaper than a walk over the selection every frame.

3. Build and start the editor with the same scratch layout. In the Hierarchy, click one entity, then hold the Control key and click a second one.

   ```sh
   cmake --build build/<preset> --config Debug --target StrataEditor --parallel
   build/<preset>/bin/Debug/StrataEditor --layout selection-summary.ini
   ```

   **You should see:** with nothing selected, the hint "Select entities in the Hierarchy or the Scene view to summarize them." With two entities selected, "2 entities selected", the heading "Components all of them have" and a bullet list that starts with the shared components, such as `Name` and `Transform`.

   **If you do not see it:** if the panel stays empty although you selected entities, open it with `editor.showPanel`: it may sit behind another tab.

4. Click the button labeled `Frame selection`. Then open **View ▸ Activity**.

   **You should see:** the Scene view moves to frame the two entities. The activity panel lists a `camera.focus` entry whose source is the person at the editor, drawn with a mouse pointer icon.

   **If you do not see it:** if the camera does not move and a toast appears, read its message: the command names why it could not frame the entities.

   **Why:** the Scene view already frames the selection when you press **F**. The button exists to teach the path of a click: widget, command, journal.

:::::

:::why[A cached list, not a fresh walk]
Drawing is the hot path of the editor. A walk over every selected entity and every registered component type each frame costs one lookup for each registered component type, dozens for each entity, and a selection of 100,000 entities makes that millions. The cache costs three comparisons per frame and one rebuild per change. What it costs you is the exception above: changes outside the history do not refresh the list until the selection changes.
:::

## Dock the panel and bump the layout version

The panel floats because the saved layout says nothing about it. A fresh layout comes from the editor's default layout, built in code, and you add the panel to it. Then you meet the rule that makes the change reach people who already have a layout file.

:::::steps

1. Dock the panel in the default layout, beside the Inspector. The function `BuildDefaultLayout` assigns every panel's window to a node of the :term[dock space]{id=dock-space}, and the Asset panel already shares the Inspector's node.

   ```diff src="book:tutorials/editor-ui/tutorial-panel.patch#hunk-3"
    		ImGui::DockBuilderDockWindow(m_Panels.GetWindowName(EditorPanels::c_Hierarchy).c_str(), left);
    		ImGui::DockBuilderDockWindow(m_Panels.GetWindowName(EditorPanels::c_Inspector).c_str(), right);
    		ImGui::DockBuilderDockWindow(m_Panels.GetWindowName(EditorPanels::c_AssetInspector).c_str(), right);
   +		ImGui::DockBuilderDockWindow(m_Panels.GetWindowName(EditorPanels::c_SelectionSummary).c_str(), right);
    		ImGui::DockBuilderDockWindow(m_Panels.GetWindowName(EditorPanels::c_Console).c_str(), bottom);
    		ImGui::DockBuilderDockWindow(m_Panels.GetWindowName(EditorPanels::c_Problems).c_str(), bottom);
    		ImGui::DockBuilderDockWindow(m_Panels.GetWindowName(EditorPanels::c_ContentBrowser).c_str(), bottom);
   ```

   **You should see:** one new line, after the one that docks the Asset panel.

   **If you do not see it:** if the compiler rejects `right`, you put the line outside the function. The variable `right` exists only inside `BuildDefaultLayout`.

   **Why:** the Inspector's node already shows one tab at a time, and the layout's last lines select the Inspector's tab. That choice holds because the focused window, the Content Browser drawn last, is in another node. Had your registration line come last, the new panel would take the focus and its tab would cover the Inspector. The engine's default layout test catches that.

   The new tab waits behind the Inspector's until someone clicks it or runs `editor.showPanel`. A split below the Inspector would show both at once, but it would take height from the Inspector, which is the panel people look at most.

2. Build and start the editor with the same scratch layout, the file that holds layout version 5.

   ```sh
   cmake --build build/<preset> --config Debug --target StrataEditor --parallel
   build/<preset>/bin/Debug/StrataEditor --layout selection-summary.ini
   ```

   **You should see:** the panel still floats over the editor, exactly as before.

   **If you do not see it:** if the panel is docked, the file was new. Delete it, run section two's start again to save a layout that floats the panel, quit, then come back to this step.

   **Why:** the editor builds the default layout only when the layout file holds none, or holds another version. This file holds version 5, and the editor's version is still 5, so it keeps the layout it was given, and the file has the panel's window floating at the place it was opened.

3. Raise the version in `StrataEditor/src/EditorLayer.h`. The comment above it lists what each version added, so add yours to the list.

   ```diff src="book:tutorials/editor-ui/tutorial-panel.patch#hunk-5"
    		static constexpr double c_AutomationActivitySeconds = 1.0;
    		// Version of the default layout: a saved layout of another version is replaced by the default one. Bump it when the
    		// default layout gains a docked panel that is open by default (4: the Problems panel, and Activity beside it; 5: the
   -		// Game view beside the Scene view, a wider Hierarchy), which an older layout would show floating over the viewport.
   -		static constexpr int c_LayoutVersion = 5;
   +		// Game view beside the Scene view, a wider Hierarchy; 6: the Selection Summary beside the Inspector), which an older
   +		// layout would show floating over the viewport.
   +		static constexpr int c_LayoutVersion = 6;
    
    		EditorLayer(const EditorOptions& options, Scope<EditorHost> host);
    		~EditorLayer() override = default;
   ```

   1. **Lines 4–5:** the old end of the comment and the old number.
   2. **Lines 6–8:** the comment gains the entry for version 6, and the constant becomes 6.

   **You should see:** the constant now reads 6, and the comment names the Selection Summary.

   **If you do not see it:** a version that stays at 5 changes nothing, as the last step showed. Check the number.

   **Why:** the comparison the editor makes at its first frame is `saved version != c_LayoutVersion`. Every person whose file says 5 now gets the default layout once.

4. Build and start the editor with the same scratch layout once more.

   ```sh
   cmake --build build/<preset> --config Debug --target StrataEditor --parallel
   build/<preset>/bin/Debug/StrataEditor --layout selection-summary.ini
   ```

   **You should see:** the layout is built again: the Hierarchy at the left, the Scene view in the middle, and at the right the Inspector with the tabs Asset and Selection Summary. Click the tab named Selection Summary. After you quit, the layout file holds layout version 6.

   **If you do not see it:** if the panel still floats, the build did not finish. Wait for it, or build the editor target again.

   **Why:** the same happens to anyone who updates the editor. Their arrangement is replaced once, and that is the cost of the rule: a person who moved panels loses the arrangement a single time. The alternative is worse, since every older layout would show the new panel as a floating window over the Scene view. The menu item **View ▸ Reset Layout** rebuilds the default layout at any time.

:::::

:::caution[What the bump costs]
Bump `c_LayoutVersion` only for a docked panel that is open by default. A panel that starts closed needs no bump, because a closed window cannot float over anything. Each bump discards every person's arrangement, so do not bump for a change that cosmetic.
:::

## Test the panel

Strata ships nothing without tests, and a panel is tested the way you saw in [the testing page](ui-testing.md): the harness draws the editor in memory. A test selects entities with commands and clicks the button by its probe key. Three cases cover the three promises of this page.

:::::steps

1. Create `SelectionSummaryUITests.cpp` in the folder `StrataTests/src/Editor/`, and start with its helpers. The harness editor is an editor drawn in memory, and the feature project is a small project the tests copy into a temporary folder. The first helper makes the three entities of the specification, with an extra prefix on their names so that they do not meet the feature project's own.

   ```cpp src="book:tutorials/editor-ui/tutorial-panel/SelectionSummaryUITests.cpp#L24-L74"
   namespace
   {

   	// Entities for the summary: two lamps (a Point Light each, the first also tagged) and a tagged crate.
   	void MakeEntities(HarnessEditor& editor)
   	{
   		editor.Run("entity.create", { { "name", "SummaryLamp" }, { "components", { { "PointLight", nlohmann::json::object() }, { "Tag", { { "Tag", "Prop" } } } } } });
   		editor.Run("entity.create", { { "name", "SummaryTorch" }, { "components", { { "PointLight", nlohmann::json::object() } } } });
   		editor.Run("entity.create", { { "name", "SummaryCrate" }, { "components", { { "Tag", { { "Tag", "Prop" } } } } } });
   	}

   	// Selects entities by name and draws the panel with them.
   	void Select(HarnessEditor& editor, std::initializer_list<const char*> names)
   	{
   		nlohmann::json ids = nlohmann::json::array();
   		for (const char* name : names)
   		{
   			const Entity entity = editor.Context().GetActiveScene()->FindEntityByName(name);
   			REQUIRE(entity);
   			ids.push_back(UUIDToJson(entity.GetUUID()));
   		}
   		editor.Run("selection.set", { { "entities", std::move(ids) } });
   		editor.Frames(2);
   	}

   	bool Has(const std::vector<std::string>& names, std::string_view name)
   	{
   		return std::find(names.begin(), names.end(), name) != names.end();
   	}

   	// imgui.ini text as an editor saved it before this panel: no window and no open state of it, and layout version 5.
   	std::string WithoutSummaryPanel(const std::string& settings)
   	{
   		std::string result;
   		std::string section;
   		size_t start = 0;
   		while (start < settings.size())
   		{
   			const size_t end = settings.find('\n', start);
   			const std::string line = settings.substr(start, end == std::string::npos ? std::string::npos : end - start);
   			start = end == std::string::npos ? settings.size() : end + 1;
   			if (line.starts_with("["))
   				section = line;
   			if (section == "[Window][SelectionSummary]" || (section == "[StrataPanels][Open]" && line.starts_with("SelectionSummary=")))
   				continue;
   			result += (section == "[StrataPanels][Layout]" && line.starts_with("Version=") ? "Version=5" : line) + "\n";
   		}
   		return result;
   	}

   }
   ```

   1. **Lines 28–32:** `entity.create` takes the components as JSON, so the test builds scenes with the commands people and agents use.
   2. **Lines 36–47:** `Select` runs `selection.set` and then two frames, so the panel draws with the new selection.
   3. **Lines 55–72:** `WithoutSummaryPanel` rewrites a saved layout file as an older editor would have written it: no window, no open state of the panel, and version 5.

   Before the helpers, write the includes of the file: the harness, the panel, the journal, the JSON library and the algorithm header. Then write the two lines `using namespace Strata;` and `using namespace Strata::Tests;`.

   **You should see:** the helpers end the anonymous namespace, and no test yet.

   **If you do not see it:** `Has` needs `<algorithm>` and `<string_view>`. MSVC may accept a missing include that GCC refuses, so add both.

2. Add the first test, the specification of the introduction. The suite name starts with `Editor.UI`, so it joins the existing shard of the editor's user interface (UI) tests: the shard's filter already matches it.

   ```cpp src="book:tutorials/editor-ui/tutorial-panel/SelectionSummaryUITests.cpp#L78-L108"
   TEST_CASE("The summary counts the selection and lists the components all of it has")
   {
   	HarnessEditor editor({}, WithFeatureProject("SelectionSummary"));
   	editor.Frames(2);
   	REQUIRE(editor.Context().HasProject());
   	MakeEntities(editor);
   	editor.Run("editor.showPanel", { { "panel", "SelectionSummary" } });
   	editor.Frames(2);
   	const SelectionSummaryPanel* panel = editor.Layer->GetPanels().Get<SelectionSummaryPanel>(EditorPanels::c_SelectionSummary);
   	REQUIRE(panel);

   	editor.Run("selection.set", { { "entities", nlohmann::json::array() } });
   	editor.Frames(2);
   	CHECK(panel->GetSelectedCount() == 0);

   	Select(editor, { "SummaryLamp", "SummaryTorch" });
   	CHECK(panel->GetSelectedCount() == 2);
   	CHECK(Has(panel->GetSharedComponents(), "Transform"));
   	CHECK(Has(panel->GetSharedComponents(), "Point Light"));
   	CHECK_FALSE(Has(panel->GetSharedComponents(), "Tag"));

   	Select(editor, { "SummaryLamp", "SummaryCrate" });
   	CHECK(panel->GetSelectedCount() == 2);
   	CHECK(Has(panel->GetSharedComponents(), "Tag"));
   	CHECK_FALSE(Has(panel->GetSharedComponents(), "Point Light"));

   	// A component added through a command changes the undo history, so the lines follow it.
   	editor.Run("component.add", { { "entity", UUIDToJson(editor.Context().GetActiveScene()->FindEntityByName("SummaryCrate").GetUUID()) }, { "component", "PointLight" } });
   	editor.Frames(2);
   	CHECK(Has(panel->GetSharedComponents(), "Point Light"));
   }
   ```

   1. **Lines 84–86:** `editor.showPanel` brings the panel's tab forward, since it sits behind the Inspector, and the registry hands out the panel by its id.
   2. **Lines 93–97:** the lamp and the torch share the light, not the tag.
   3. **Lines 99–102:** the lamp and the crate share the tag, not the light.
   4. **Lines 105–107:** adding a component through `component.add` is one undo step, the history number changes and the list follows.

   **You should see:** one test case with four blocks of checks.

   **If you do not see it:** if `GetSharedComponents` returns stale values, the panel was not drawn: its tab was hidden. The test opens it with `editor.showPanel` first, and an editor must draw the panel for it to refresh.

3. Add the second test. It clicks the button the way a person does and reads what the journal recorded.

   ```cpp src="book:tutorials/editor-ui/tutorial-panel/SelectionSummaryUITests.cpp#L110-L128"
   TEST_CASE("The Frame button runs camera.focus as the person")
   {
   	HarnessEditor editor({}, WithFeatureProject("SelectionSummaryButton"));
   	editor.Frames(2);
   	MakeEntities(editor);
   	editor.Run("editor.showPanel", { { "panel", "SelectionSummary" } });
   	Select(editor, { "SummaryLamp", "SummaryTorch" });

   	const CommandJournal& journal = editor.Context().GetJournal();
   	const uint64_t before = journal.GetLatestId();
   	REQUIRE(editor.Click("SelectionSummary.Frame"));
   	editor.Frames(1);

   	const auto entry = std::find_if(journal.GetEntries().begin(), journal.GetEntries().end(),
   		[before](const CommandJournalEntry& candidate) { return candidate.Id > before && candidate.Command == "camera.focus"; });
   	REQUIRE(entry != journal.GetEntries().end());
   	CHECK(entry->Source == CommandSource::UI);
   	CHECK(entry->Parameters["entities"].size() == 2);
   }
   ```

   1. **Line 120:** `Click` takes a probe key and works over three frames, as the testing page described: move, press, release.
   2. **Lines 123–125:** the journal keeps every command with its source, so the test searches for the new `camera.focus` entry.
   3. **Lines 126–127:** the source is `UI`, and the command got both identifiers.

   **You should see:** a test that never looks at pixels.

   **If you do not see it:** if the click returns false, the probe has no entry for the button: the panel's tab is hidden or the key is spelled wrongly.

4. Add the third test. It builds an editor, saves its layout, makes the file look as if the panel never existed and opens a second editor with it.

   ```cpp src="book:tutorials/editor-ui/tutorial-panel/SelectionSummaryUITests.cpp#L130-L158"
   TEST_CASE("A layout saved before the panel gives way to the default layout, which docks it beside the Inspector")
   {
   	std::string settings;
   	{
   		HarnessEditor editor({}, WithFeatureProject("SelectionSummaryLayout"));
   		editor.Frames(3);
   		size_t size = 0;
   		settings = ImGui::SaveIniSettingsToMemory(&size);
   	}
   	REQUIRE(settings.find("[Window][SelectionSummary]") != std::string::npos);
   	const std::string older = WithoutSummaryPanel(settings);
   	REQUIRE(older.find("[Window][SelectionSummary]") == std::string::npos);
   	REQUIRE(older.find("SelectionSummary=") == std::string::npos);
   	REQUIRE(older.find("[StrataPanels][Layout]\nVersion=5\n") != std::string::npos);

   	HarnessEditor editor({}, WithFeatureProject("SelectionSummaryLayoutReopened"), older);
   	editor.Frames(3);
   	ImGuiWindow* summary = editor.FindPanelWindow(EditorPanels::c_SelectionSummary);
   	ImGuiWindow* inspector = editor.FindPanelWindow(EditorPanels::c_Inspector);
   	REQUIRE(summary);
   	REQUIRE(inspector);
   	REQUIRE(inspector->DockNode);
   	CHECK(editor.Layer->GetPanels().IsOpen(EditorPanels::c_SelectionSummary));
   	CHECK(summary->DockNode == inspector->DockNode);
   	// The current version is saved, so the default layout is built once.
   	size_t size = 0;
   	const std::string saved = ImGui::SaveIniSettingsToMemory(&size);
   	CHECK(saved.find("[StrataPanels][Layout]\nVersion=" + std::to_string(EditorLayer::c_LayoutVersion)) != std::string::npos);
   }
   ```

   1. **Lines 134–137:** the first editor runs three frames and saves its layout text from memory.
   2. **Lines 139–143:** the helper's result holds no window of the panel and the old version, which the test requires before it relies on it.
   3. **Lines 145–153:** the second editor starts with that text. The panel must sit in the Inspector's dock node.
   4. **Lines 154–157:** the editor saves the current version, so it builds the default layout once.

   **You should see:** the file ends with the closing brace of the suite.

   **If you do not see it:** `ImGui::SaveIniSettingsToMemory` needs the ImGui headers, which the harness header already includes.

5. Configure again, because the test file is new, build the test program and run your suite alone.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --target StrataTests --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Editor.UI.SelectionSummary
   ```

   **You should see:** the three `[doctest]` lines at the end. They report three test cases passed, none failed, and `Status: SUCCESS!`.

   **If you do not see it:** doctest with 0 test cases means the suite name has a spelling error. A failure that names a line of the checks shows the expected and found values.

6. Prove that the layout test guards the bump. Set `c_LayoutVersion` back to 5, build the test program and run the suite again, then put the 6 back.

   **You should see:** the third case fails on the check that the panel's dock node equals the Inspector's: the panel has no dock node. The older file says 5, the editor says 5, so no default layout is built, and the window floats.

   **If you do not see it:** if the case passes with 5, the test file did not remove the panel's window. Check that the `REQUIRE` on `[Window][SelectionSummary]` runs.

   **Why:** a test you never saw fail may test nothing. This one fails exactly when the rule of the last section is broken.

7. Run every UI suite, which includes the source scans, the tests that read the editor's code as text and enforce its rules.

   ```sh
   build/<preset>/bin/Debug/StrataTests --test-suite="Editor.UI*"
   ```

   **You should see:** all suites pass, among them `Editor.UI.Source`, with the cases "Colors come only from the theme", "Sizes scale with the font" and "Panels draw through the panel registry". Your panel passes all of them without an exception.

   **If you do not see it:** a failure names the file and the line of a finding. Fix the code and never add an exception: the scans' lists of exceptions are empty on purpose.

8. Break the scans once, to see them work. In `SelectionSummaryPanel.cpp`, change the hint's color to `ImVec4(1.0f, 0.4f, 0.35f, 1.0f)`, build and run `Editor.UI.Source`. Then restore the token.

   **You should see:** "Colors come only from the theme" fails, and its message starts with "A color literal outside" and names your line.

   **If you do not see it:** if nothing fails, the test program was not rebuilt. Build `StrataTests` again.

   **Why:** you now know that a rule of the editor is a test and not a hope. The same holds for a size such as `ImVec2(320.0f, 0.0f)`, which the size scan refuses.

:::::

You have a panel with the registry's menu item, open state and docking, drawn from the kit and tested without a screen. What the change still lacks before it lands is the review of the whole :term[diff]{id=diff} and a run of the continuous integration, which the engine's guide describes. The guide also lists the other rules of the Editor section, such as the one that keeps panels from walking the scene each frame.

## Summary

- You wrote a panel class, registered it with `EditorPanelRegistry` and saw it in the View menu, opened it with `editor.showPanel` and found its open state in the layout file.
- You drew it with the widget kit, theme colors and font-relative sizes, and made its button run `camera.focus` with the origin of the UI.
- You docked it in the default layout, saw why the saved version hides the change, and raised `c_LayoutVersion` so that older layouts are replaced once.
- You tested the panel with `HarnessEditor` and `Click`, proved that the layout test fails without the bump, and ran the `Editor.UI.Source` scans.

## Check yourself

1. You register the panel with `OpenByDefault` true, but you never dock it and never bump the version. A person with an older layout file starts the new editor. Where is the panel?

   :::answer{tests="dock-layout"}
   The panel floats over the editor. The saved version equals the editor's, so no default layout is built, and the panel has no saved window. The registry opens it because it is open by default, and ImGui places a window that has no dock wherever it likes, which is usually over the Scene view.
   :::

2. Why does the panel's `Id` stay the same after release, while its `Title` may change?

   :::answer{tests="register-panel"}
   The window name ends with `###` and the id, and ImGui hashes only that part. The layout file stores the window's position and the open state under it. A new id is a new window with no saved position and a lost open state, while a new title changes only the text on the tab.
   :::

3. The button's handler calls `RunEditorCommand`, not `Execute` on the registry. What do you lose if you call `Execute` with no origin?

   :::answer{tests="draw-panel"}
   The journal would record the source as internal and not as the person, and no toast would report a failure. The Activity panel and any agent that reads the journal would see an automatic call and not a click. `RunEditorCommand` passes the origin of the UI and shows the outcome.
   :::

4. A test selects the lamp and the torch, but `GetSharedComponents` returns the list of the previous selection. Name two causes.

   :::answer{tests="test-panel"}
   First, the panel's tab is hidden behind the Inspector, so the registry never calls `OnImGuiRender` and nothing rebuilds. The test must show the panel, for example with `editor.showPanel`. Second, the test did not run a frame after `selection.set`, so the rebuild has not happened yet.
   :::

5. A teammate writes `ImGui::SetNextItemWidth(240.0f)` in the panel. Which test fails, and how do you fix the code?

   :::answer{tests="draw-panel test-panel"}
   The case "Sizes scale with the font" in `Editor.UI.Source` fails, because 240 is a pixel size above 16. Write the width from the font, for example `ImGui::GetFontSize() * 15.0f`, so that it tracks the person's interface scale. The scan's list of exceptions stays empty.
   :::

## Exercises

1. **Basic.** Keep the button on screen while nothing is selected, but disable it and make its tooltip say why. Test it with the item probe.

   Hint: the kit's button takes a style with an `Enabled` field, and it shows a disabled button's tooltip as well.

   :::answer{tests="draw-panel test-panel" solution="tutorials/editor-ui/tutorial-panel/exercise-1.patch"}
   The solution removes the early return, draws the hint or the lines by a flag, and gives the button `Enabled` and `Primary` from that flag. Its tooltip reads "Nothing to frame: select entities first". The new test selects nothing and reads the button's probe item. Its `Enabled` field is false. The test then selects the lamp and reads the item again, and now the field is true.
   :::

2. **Medium.** List the names of the selected entities below the summary in a box of eight lines, and draw only the visible rows with `ImGuiListClipper`. Test that the names come in selection order.

   Hint: the fields `DisplayStart` and `DisplayEnd` of `ImGuiListClipper` give the rows in view. The delete dialog of the assets uses the same pattern.

   :::answer{tests="draw-panel test-panel" solution="tutorials/editor-ui/tutorial-panel/exercise-2.patch"}
   The panel keeps a vector of names, completed in `Rebuild`, and draws it in a :term[child window]{id=child-window} whose height is eight lines of the font. The `ImGuiListClipper` submits only the rows in view, so a selection of 100,000 entities costs as little per frame as one of eight. The test selects the torch, the crate and the lamp and expects those names in that order.
   :::

3. **Hard.** Add a second button that frames the whole scene with `camera.focus` and no entities, also while nothing is selected. Write a harness test that clicks it and checks that the journal entry has no `entities` parameter.

   Hint: without entities the command frames every active entity. Draw the button above the empty-state return.

   :::answer{tests="draw-panel test-panel" solution="tutorials/editor-ui/tutorial-panel/exercise-3.patch"}
   The solution adds `FrameScene`, which runs `camera.focus` with no parameters, and a second button with its own probe key, drawn before the empty state returns. The test clears the selection, clicks the new key, finds the journal entry after the latest identifier it noted, and checks that its source is the UI and that its parameters have no `entities` key.
   :::

## Where it lives in Strata

- `StrataEditor/src/UI/EditorPanelRegistry.h` and `EditorPanelRegistry.cpp`: `EditorPanel`, `EditorPanelDescriptor`, the registry, the View menu items and the settings handler of the open states and the layout version.
- `StrataEditor/src/EditorLayer.h` and `EditorLayer.cpp`: the panel ids, `RegisterBuiltinPanels`, `BuildDefaultLayout`, `c_LayoutVersion` and `editor.showPanel`.
- `StrataEditor/src/Panels/`: the panels of the editor, among them the one you added.
- `StrataEditor/src/UI/EditorActions.h`: `RunEditorCommand`, which runs a command as the person.
- `StrataTests/src/Editor/EditorUISourceTests.cpp`: the scans of the colors, the sizes and the windows.
- `StrataTests/src/Editor/EditorUITests.cpp`: the tests of the default layout and of the open states, which your layout test follows.

## Further reading

- The Dear ImGui project, the docking section of its wiki (github.com/ocornut/imgui): how windows dock, and what the DockBuilder functions do: intermediate.
- The doctest documentation on test suites and filters (github.com/doctest/doctest): how `--test-suite` selects tests: beginner.
- Kent Beck, "Test-Driven Development: By Example": the habit of seeing a test fail before it passes: beginner.
