---
id: editor-ui/shell
title: "The editor shell: host, layer, docking and panels"
description: "How the editor's window is built: the layer that draws it, the registry that owns its panels, the saved layout, and the questions it asks the person."
kind: internals
size: XL
tracks: [E]
needs: [editor-ui/widget-kit, editor/saving]
time: 110
learn:
  - id: shell-layers
    text: explain which object owns the application link, the panels and the dialogs of the editor window
  - id: panel-life
    text: trace the calls the registry makes on a panel in one frame, closed, hidden or shown
  - id: layout-version
    text: predict what the editor shows on the next start after the layout version changes
  - id: ask-person
    text: explain why a question asked from inside a modal is drawn inside it, and when it is asked again
  - id: click-trace
    text: trace a click on a menu item to the command it runs and to its entry in the journal
since: 0.3.0
status: final
---

When you open the editor you see one window with a menu bar, a toolbar, eight panels and a strip of status along the bottom. This page explains how the user interface (UI) of that window is built, for a reader who will add a panel, change the default layout or ask the person a new question. The shell, which is the code that builds the window, does three jobs.

The shell gives the panels a place to live and keeps where they live between runs. It also stands between the panels and the rest of the editor, so that a panel never reaches past a small interface. The shell holds no scene data, runs no commands of its own and writes no files. The core does that, and the shell only draws it and asks for it.

::figure{id=editor-default-layout}

## The problem and how engines solve it

An editor window is a set of tools that appear, hide, dock and come back after a restart. The program draws them every frame with [Dear ImGui](../editor-ui/imgui.md) and has no widget tree to hold their state, as [immediate mode](../editor-ui/immediate-mode.md) explains. Each frame the code asks for a window by name, and the library remembers its position under that name. That is enough for one tool. It is not enough for twelve, because someone must decide which exist, which are open, where each docks first and what happens when a saved arrangement no longer fits the program.

Engines solve this in two steps. The first is a registry of panel :term[descriptors]{id=descriptor}: one place creates the panels, lists them in a menu, saves which are open and calls their hooks. A panel is then only a class and a description. The second is :term[dependency inversion]{id=dependency-inversion}: panels talk to the window through an interface, and the window talks to the application through another. Every panel then runs in a test with fakes.

Strata uses both and adds a third rule, that the interface is a client of commands. It draws state and asks the core to change it, so a click and an agent's request take the same road.

## The map: who owns what

Four objects carry the window. `EditorApplication` is the program: it installs the theme, the :term[fonts]{id=font} and the layout file, then gives one `EditorLayer` an `EditorHost`.

The **editor shell** (`EditorShell`) is the interface that panels may ask for dialogs, for the question about unsaved changes, for other panels and for facts about the running editor. `EditorLayer` implements it.

A **panel** is one window of the editor that docks, such as the Hierarchy or the Console, and the **panel registry** (`EditorPanelRegistry`) owns every panel. The layer holds the registry, and the registry holds the panels.

```mermaid caption="From the program down to the panels, with the host as the layer's only way back to the application." alt="A stack of boxes from the editor program through the editor layer and the panel registry to the panels. Beside the layer stand the editor core and the host, which links back to the application. Below sits the engine's interface module."
flowchart TB
    App["EditorApplication: theme, fonts, layout file"] -->|"creates, with an EditorHost"| Layer["EditorLayer (is the EditorShell)"]
    Layer --> Registry["EditorPanelRegistry"]
    Registry --> Panels["Panels: Hierarchy, Inspector, Console ..."]
    Layer -->|"EditorHost"| App
    Layer --> Core["Core: EditorContext, commands, runner, automation"]
    Panels -->|"EditorPanelContext"| Core
    Panels -->|"EditorShell"| Layer
    App --> ImGuiMod["Engine ImGui module: ImGuiLayer, platform, renderer"]
```

Three arrows matter more than the boxes. The host is the only way the layer reaches the application. It closes the program, sets the :term[exit code]{id=exit-code} and reports the frame count and the time. It also handles the window title and size, the :term[UI scale]{id=ui-scale}, the :term[frame rate cap]{id=frame-rate-cap}, the last frame's :term[work time]{id=work-time} and screenshots.

`ApplicationEditorHost` implements the host in `EditorApplication.cpp`, and the UI tests supply a fake. The shell is the only way a panel reaches the window. The core is the only place state changes, through commands.

All of this is main-thread code. The registry's source comments say so, and the layer draws inside the application's frame, so nothing here is safe to call from a job. A result from a background job returns through the editor's polled queues, never through a call into the registry.

The shell also keeps the line between what a game ships and what it omits. `StrataEditorUI` is the library that holds `EditorLayer`, the registry and the panels, and no game links it. The engine's own :term[ImGui]{id=dear-imgui} module is kept out of games too: the :term[layer table]{id=layer-table} marks its `ImGui` layer as tooling.

## The contract

A panel author may rely on a few things and must keep a few rules. Each rule has a reason that costs something when ignored.

:::rule[Panels never begin windows]
A panel draws only the contents of its window. The registry begins the window, so it owns the View menu entry, the open state in the settings file, the stable window name, the focus handling and the `OnHidden` call. A panel that begins its own window loses all of these. [The widget kit](../editor-ui/widget-kit.md) lists the controls a panel draws with.
:::

:::rule[Every change goes through a command]
Panels draw state and call commands; they never write the scene, and never write, move or remove files. For continuous edits the panel uses `SceneEditTransaction` or `SetPropertyWithUndo`. The reason is that undo, the activity journal and the automation commands then see one operation, so the person, an agent and a script cannot disagree.
:::

:::rule[UI commands carry the UI origin]
A command the UI runs passes `CommandOrigin { CommandSource::UI }`, which `RunEditorCommand` does for you. The journal then says who did what, and a failure the person caused shows as a toast while an agent's failure does not.
:::

:::rule[Nothing changes the scene while its rows are drawn]
A panel that walks entities schedules the change and runs it after the loop. A command may destroy or remake entities that the rest of the frame still reads.
:::

:::rule[A modal that asks draws the question inside itself]
A dialog that asks about unsaved changes while it is open calls `DrawDiscardQuestion`. :term[ImGui]{id=dear-imgui} keeps one :term[popup]{id=popup} per level, so a question opened over the whole window closes the dialog that is open.
:::

:::rule[Focusing a panel while a modal waits is deferred]
Focusing a window closes the popups above it, so the registry holds the request until the :term[modal]{id=modal} ends.
:::

:::rule[Scripted runs never write the person's layout]
A run with `--frames` has no layout file, so a test cannot change how a person's editor looks.
:::

:::rule[A new default panel bumps the layout version]
When the default layout gains a panel that is open by default, `c_LayoutVersion` goes up by one. An old layout would otherwise show the new panel floating over the viewport.
:::

The first six rules decide what code may do in a frame. The last two decide what the saved window must survive, and the sections on the layout explain them.

## A toy version

:::question
New to classes, `std::function` or :term[smart pointers]{id=smart-pointer}? Read [classes](../basics/cpp-classes.md) and [templates and lambdas](../basics/cpp-generic.md) first.
:::

The toy below keeps the core of the registry in about a hundred lines. It validates a descriptor, creates the panel, remembers saved open states, calls `OnUpdate` for every panel and `OnHidden` for the closed ones, and repeats a focus request that a modal blocks. It omits ImGui, docking and the file: the printed text stands for the windows.

```cpp sketch="editor-ui-shell-toy.cpp"
// A toy panel registry: descriptors checked on registration, open states kept as text, and a focus request that
// waits behind a modal and is retried for at most four frames.
#include <cstdio>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>

struct Panel
{
	virtual ~Panel() = default;
	virtual void OnUpdate() {}
	virtual void OnRender(const std::string& title) = 0;
	virtual void OnHidden() {}
};

struct Label : Panel
{
	void OnRender(const std::string& title) override { std::printf("  draw %s\n", title.c_str()); }
	void OnHidden() override { std::printf("  hidden\n"); }
};

struct Descriptor
{
	std::string Id;
	std::string Title;
	bool OpenByDefault = true;
	std::function<std::unique_ptr<Panel>()> Create;
};

class Registry
{
public:
	bool Register(Descriptor descriptor, std::string& error)
	{
		if (descriptor.Id.empty() || descriptor.Id.find_first_of("=#[]") != std::string::npos)
			return error = "bad id", false;
		for (const Entry& entry : m_Entries)
			if (entry.Info.Id == descriptor.Id)
				return error = "id taken", false;
		if (!descriptor.Create)
			return error = "no factory", false;
		Entry entry { std::move(descriptor), nullptr, true, false, 0 };
		entry.Instance = entry.Info.Create();
		const auto saved = m_Saved.find(entry.Info.Id);
		entry.Open = saved != m_Saved.end() ? saved->second : entry.Info.OpenByDefault;
		m_Entries.push_back(std::move(entry));
		return true;
	}

	void Read(const std::string& id, bool open) { m_Saved[id] = open; }
	void Focus(const std::string& id)
	{
		for (Entry& entry : m_Entries)
			if (entry.Info.Id == id)
				entry.Open = entry.WantsFocus = true;
	}

	void Frame(int frame, bool modalOpen, int tabShowsFromFrame)
	{
		std::printf("frame %d%s\n", frame, modalOpen ? " (modal open)" : "");
		for (Entry& entry : m_Entries)
			entry.Instance->OnUpdate();
		for (Entry& entry : m_Entries)
		{
			if (!entry.Open)
			{
				entry.Instance->OnHidden();
				continue;
			}
			const bool focusing = entry.WantsFocus && !modalOpen;
			if (focusing)
			{
				std::printf("  focus %s\n", entry.Info.Id.c_str());
				if (frame >= tabShowsFromFrame || ++entry.Attempts >= c_MaxAttempts)
					entry.WantsFocus = false;
			}
			entry.Instance->OnRender(entry.Info.Title);
		}
	}

	void Write() const
	{
		for (const Entry& entry : m_Entries)
			std::printf("%s=%d\n", entry.Info.Id.c_str(), entry.Open ? 1 : 0);
	}

private:
	struct Entry
	{
		Descriptor Info;
		std::unique_ptr<Panel> Instance;
		bool Open;
		bool WantsFocus;
		int Attempts;
	};
	static constexpr int c_MaxAttempts = 4;
	std::vector<Entry> m_Entries;
	std::map<std::string, bool> m_Saved;
};

int main()
{
	Registry registry;
	registry.Read("Console", false);
	std::string error;
	const auto make = []() { return std::make_unique<Label>(); };
	for (const char* id : { "Hierarchy", "Console", "Bad=Id", "Hierarchy" })
		if (!registry.Register({ id, id, true, make }, error))
			std::printf("refused '%s': %s\n", id, error.c_str());
	registry.Focus("Console");
	registry.Frame(1, true, 3);
	registry.Frame(2, false, 3);
	registry.Frame(3, false, 3);
	registry.Write();
	return 0;
}
```

```text output-of="editor-ui-shell-toy.cpp"
refused 'Bad=Id': bad id
refused 'Hierarchy': id taken
frame 1 (modal open)
  draw Hierarchy
  draw Console
frame 2
  draw Hierarchy
  focus Console
  draw Console
frame 3
  draw Hierarchy
  focus Console
  draw Console
Hierarchy=1
Console=1
```

1. **Lines 37–43:** a bad name, a taken name and a missing factory are refused with a reason.
2. **Line 47:** a saved open state wins over the descriptor's default.
3. **Lines 63–64:** every panel updates every frame, open or not.
4. **Line 72:** a focus request counts only while no modal is open.
5. **Line 76:** the request ends when the tab shows or after four attempts.

The program registers four descriptors, and the registry refuses two of them: a name with `=` in it would break a settings line, and a repeated name would hide a panel. A saved state says the Console is closed, so the Console is registered closed although its descriptor opens it. Then `Focus("Console")` opens it and asks for the front.

Frame 1 has a modal open, so nothing is focused. Frame 2 focuses it and, because the tab shows only from frame 3, asks again. Frame 3 ends the request. The last call writes one `id=0|1` line per panel, as the real handler does.

The toy shows the shape and hides the hard part. The real registry must start real ImGui windows, find tabs in :term[dock nodes]{id=dock-space}, read and write `imgui.ini`, and cope with a layout built in the same frame.

## The real code, in the order a frame meets it

### The program installs the window

`EditorApplication` runs before any panel exists. In its :term[constructor]{id=constructor} it passes the Bedrock theme to the ImGui layer as the style :term[callback]{id=callback}. It loads the editor's own fonts and starts reading the system's fallback fonts for Chinese, Japanese and Korean text. It applies `--ui-scale` when the person gave it.

If the fonts are missing, it logs an error and the UI uses ImGui's default font. Then it pushes the `EditorLayer` and gives it an `ApplicationEditorHost`.

The layout file is chosen earlier, where the modules are listed. With `--layout <file.ini>` the layout lives in that file. Without it, the layout lives in `EditorLayout.ini` in the user's data folder, except in a run with `--frames`, which has no file at all. A headless editor has no ImGui module and no window, so none of this runs.

### One frame of the layer

The UI module calls `EditorLayer::OnImGuiRender` after every layer has updated, as [the editor's frame](../editor/program.md) describes. The first lines track input, let a binding capture claim the keyboard and cancel a drag when Escape is pressed. Then the frame branches.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1017-L1040"
if (IsLauncherShown())
{
	DrawLauncher(panelContext);
}
else
{
	HandleShortcuts();
	DrawDockspace();
	DockNewToolPanels();
	// A new inspection target brings its tab forward (the Asset tab for an asset, the Inspector for the entities),
	// leaving the keyboard focus where it is (e.g. in the Content Browser that was clicked).
	if (m_Context.GetInspectionVersion() != m_ShownInspectionVersion)
	{
		m_ShownInspectionVersion = m_Context.GetInspectionVersion();
		m_Panels.ShowTab(m_Context.GetInspectionTarget() == InspectionTarget::Asset ? EditorPanels::c_AssetInspector : EditorPanels::c_Inspector);
	}
	// A play whose script build failed shows its errors.
	if (m_Context.GetProblemsPanelRequests() != m_ShownProblemsRequests)
	{
		m_ShownProblemsRequests = m_Context.GetProblemsPanelRequests();
		m_Panels.Focus(EditorPanels::c_Problems);
	}
	m_Panels.OnImGuiRender(panelContext);
}
```

1. **Lines 1017–1020:** while no project is open, the launcher replaces the dock space and the panels.
2. **Lines 1023–1025:** with a project, shortcuts run first, then the dock space host, then the docking of new tool panels.
3. **Lines 1028–1032:** a new inspection target brings its tab forward with `ShowTab`, leaving the keyboard where it was.
4. **Line 1039:** the registry draws every panel; everything else on the frame draws over them.

After the panels come every dialog in a fixed order, then the modal about unsaved changes, then the toasts. ImGui's example window follows when the person opened it from the Help menu, which offers it only with `--imgui-demo`. The :term[frame rate]{id=frame-rate} update comes next, and the last step takes the screenshots that were asked for, so a picture holds everything the frame drew.

The dialogs belong to [the launcher and dialogs page](../editor-ui/launcher-dialogs.md). The toasts draw last so that they sit over everything: in the corner of the Scene or Game view, found with `GetShownWindowRect`, or above the status bar when neither view shows. [The status page](../editor-ui/status.md) describes them.

```mermaid caption="One editor frame: events first, then the update, then the panels, the dialogs, the question and the toasts." alt="A left-to-right sequence. Window events reach the layer. The update runs commands and polls. The render step draws the dock space, the panels, the dialogs, the modal about unsaved changes and the toasts. A list of finished commands ends the frame."
flowchart LR
    E["Window events (ImGuiLayer first)"] --> U["Layer update: core, runner, panel update"]
    U --> R["OnImGuiRender: shortcuts, dock space, panels"]
    R --> D["Dialogs, then the modal about unsaved changes"]
    D --> T["Toasts over everything"]
    T --> F["Frame rate update; commands finished"]
```

### The panel interface and its descriptor

Everything a panel may do is in two types. Search for the hooks the registry calls, and for the fields the registry needs to keep a panel's identity.

```cpp src="StrataEditor/src/UI/EditorPanelRegistry.h#L62-L93"
class EditorPanel
{
public:
	virtual ~EditorPanel() = default;

	// Every frame before the panels are drawn, also while the panel is closed or hidden (e.g. to collect what the status
	// bar shows about it).
	virtual void OnUpdate([[maybe_unused]] EditorPanelContext& context) {}
	// Flags and options for this frame's window, asked before it begins.
	virtual EditorPanelWindowOptions GetWindowOptions([[maybe_unused]] EditorPanelContext& context) { return {}; }
	// Draws the contents of the panel's window (between ImGui::Begin and End) while it is visible.
	virtual void OnImGuiRender(EditorPanelContext& context) = 0;
	// The window is closed, collapsed or behind another tab this frame: end interactions that hold state.
	virtual void OnHidden([[maybe_unused]] EditorPanelContext& context) {}
	// The editor is closing. ImGui may be gone already: no ImGui calls.
	virtual void OnDetach([[maybe_unused]] EditorPanelContext& context) {}
	// Whether the panel needs frames at the full rate now (a drag or an animation in progress), so the editor does not
	// throttle while it lasts.
	virtual bool IsAnimating() const { return false; }
};

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

1. **Line 69:** `OnUpdate` runs every frame, also for closed panels, so a panel can collect what the status bar shows.
2. **Line 73:** `OnImGuiRender` is the only hook a panel must write, and it runs only while the window is visible.
3. **Line 75:** `OnHidden` runs when the window is closed, collapsed or behind another tab, so a drag in progress can end.
4. **Line 85:** the `Id` is the ImGui :term[id]{id=id} of the window and the key in the settings file, so it stays stable.
5. **Line 92:** the factory is a function, so the registry creates panels and the layer never names their types.

`OnDetach` runs when the editor closes and may not call ImGui, because ImGui can be gone. `IsAnimating` lets a panel keep the editor at full speed during a drag or an animation; the idle throttle in the layer reads it through `IsAnyAnimating`. A panel gets an `EditorPanelContext` in every hook. It holds the `EditorContext`, the :term[command registry]{id=command-registry}, the runner, the frame statistics and the `Shell`, which is null where tests draw a panel without a window.

`Register` refuses a descriptor that would break something later. An empty id, or one with `=`, `#`, `[`, `]` or a line break, cannot live in the settings file. A taken id, an empty title, a missing factory, a factory that returns nothing and a second launcher panel all fail with a message the layer logs. A saved open state for the id wins over `OpenByDefault`.

The window name is the icon, two spaces and the title, then `###` and the id. Everything before `###` is only a label, and ImGui :term[hashes]{id=hash} the part after it. A panel can therefore change its title without losing its place.

:::example[One window name]
The Console is registered with the id `Console`, the title "Console" and an icon. Its window name is the icon, two spaces, "Console", then `###Console`. ImGui stores the window's position and dock node under the hash of `###Console` only. If a later version renames the title to "Output", the name changes before `###` and the hash stays, so every saved layout still finds the window.
:::

Placement has two values. A **Docked** panel is a window of the dock space with a View menu item. The **Launcher** panel is drawn in place of the whole dock space while no project is open; it has no menu item and no saved state, and only one may register. The built-in registration order is the drawing order: Scene, Game, Hierarchy, Inspector, Asset, Console, Problems, Content Browser, then the Welcome launcher, then Streaming, Performance, Activity and Project Settings, which are closed by default. The comment before the Content Browser says why the order matters: it shares its dock node with the Console and must come after it.

### Drawing the panels

The registry's own `OnImGuiRender` loops over the entries in registration order. A closed or non-docked panel gets `OnHidden` at once. An open one gets its window options, a focus or tab request if it has one, then `Begin`, then either `OnImGuiRender` or `OnHidden`, then `End`. The excerpt starts with the options and ends at `End`.

```cpp src="StrataEditor/src/UI/EditorPanelRegistry.cpp#L179-L237"
const EditorPanelWindowOptions options = entry.Panel->GetWindowOptions(context);
// Focusing a window closes the popups above it: while a modal dialog waits for the person (the unsaved-changes
// question, recovery), a panel asked for (e.g. by an agent's editor.showPanel) opens behind it and comes to the
// front once the dialog is answered.
const bool focusing = entry.FocusRequested && !ImGui::GetTopMostPopupModal();
if (focusing)
	ImGui::SetNextWindowFocus();
if (entry.ShowTabRequested)
{
	// The tab of a docked window is selected in its node's tab bar (or, before the bar exists, in the node);
	// a floating window comes to the front. Neither takes the keyboard focus. A window that does not exist yet
	// (the first frame) is shown once it does.
	if (ImGuiWindow* window = ImGui::FindWindowByName(entry.WindowName.c_str()))
	{
		entry.ShowTabRequested = false;
		if (ImGuiDockNode* node = window->DockNode)
		{
			ImGuiTabItem* tab = node->TabBar ? ImGui::TabBarFindTabByID(node->TabBar, window->TabId) : nullptr;
			if (tab)
				ImGui::TabBarQueueFocus(node->TabBar, tab);
			else
				node->SelectedTabId = window->TabId;
		}
		else
		{
			ImGui::BringWindowToDisplayFront(window);
		}
	}
}
if (options.NoPadding)
	ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0.0f, 0.0f));
bool open = true;
const bool visible = ImGui::Begin(entry.WindowName.c_str(), &open, options.Flags);
if (options.NoPadding)
	ImGui::PopStyleVar();
if (focusing)
{
	// A window docked into a layout built in this frame takes its place, and the node's tab bar the tab the layout
	// chose, only in the next frames, despite the focus: ask again until the panel's tab shows.
	const ImGuiWindow* window = ImGui::GetCurrentWindow();
	const bool docked = window->DockId != 0 || window->DockIsActive;
	const bool shown = !docked || window->DockTabIsVisible;
	if (shown || ++entry.FocusAttempts >= c_MaxFocusAttempts)
	{
		entry.FocusRequested = false;
		entry.FocusAttempts = 0;
	}
}
if (visible)
{
	const ImGuiWindow* window = ImGui::GetCurrentWindow();
	entry.ShownRect = WindowRect { window->Pos, ImVec2(window->Pos.x + window->Size.x, window->Pos.y + window->Size.y) };
	entry.Panel->OnImGuiRender(context);
}
else
{
	entry.Panel->OnHidden(context);
}
ImGui::End();
```

1. **Line 183:** a focus request counts only while no modal popup is open, because focusing closes popups above it.
2. **Line 186:** `ShowTab` selects the tab in the node's tab bar, or the node's selected tab before the bar exists, without taking keyboard focus.
3. **Line 211:** `Begin` is called here and only here; the panel never sees it.
4. **Line 221:** the request ends when the tab shows or after four attempts, so a request never loops for ever.
5. **Line 231:** the panel draws only while its window is visible, and its rectangle is stored for toasts.

A repeated focus request exists for one case. A layout built in this frame docks windows only in the following frames, so the tab the person asked for may not show yet. The registry asks again for up to `c_MaxFocusAttempts` frames, which is 4, to cover that lag. A modal does not use up attempts, because while it is open the request waits. When the person answers the modal, the panel comes to the front.

:::example[A focus request in three frames]
An agent runs `editor.showPanel` for the Activity panel while the question about unsaved changes is open. Frame 1: `Focus` opens the panel and sets the request. The modal is open, so `focusing` is false and nothing is asked of ImGui.

Frame 2: the person answers, and the modal closes, so `focusing` is true. The window begins with `SetNextWindowFocus`, but its dock node builds the tab bar only now, so `DockTabIsVisible` is false and the attempt count becomes 1. Frame 3: the tab shows, and the request ends with the count back at 0. The panel was open from frame 1, so the settings file records it as open.
:::

Tab requests differ from focus. `Focus` opens the panel and brings it to the front, which is what `editor.showPanel` and the status bar's pills want. `ShowTab` opens the panel and selects its tab without moving the keyboard.

The Inspector wants that when you click an asset in the Content Browser. The Asset tab comes forward, and you can keep typing in the browser's search field. `SelectTab` is the layout builder's version, which writes the node's selected tab before the node's tab bar exists.

The toy and the real registry differ in four ways. The real one begins ImGui windows and asks them whether they are visible, where the toy prints. It finds tabs in dock nodes, where the toy has no tabs. It keeps the saved states in ImGui's file, and a layout built in the same frame delays the focus until the tab exists. Each difference answers a failure of the plain version: a panel nobody could see, a tab that stays behind, a state lost at restart, a focus that lands too early.

```mermaid caption="The life of a panel: registered, open or closed, and what the registry calls each frame." alt="A state diagram. A panel is registered, then open or closed. Every frame it receives an update call. A visible open panel receives a draw call, and a closed, collapsed or covered one receives the hidden call. A focus request waits behind a modal and repeats for up to four frames."
stateDiagram-v2
    [*] --> Registered: Register validates and creates
    Registered --> Open: saved state or OpenByDefault
    Registered --> Closed: saved state or OpenByDefault
    Open --> Closed: tab close button or View menu
    Closed --> Open: View menu or Focus
    Open --> Shown: window visible, OnImGuiRender
    Open --> Hidden: collapsed or behind a tab, OnHidden
    Closed --> Hidden: OnHidden every frame
    Open --> FocusWaiting: Focus while a modal is open
    FocusWaiting --> Open: modal answered, retried up to 4 frames
```

### What imgui.ini holds

ImGui saves window positions and the dock tree in its settings file, and it lets a program add sections of its own. A **settings handler** is a set of functions that ImGui calls to read and write one named section of that file. The registry installs one named `StrataPanels`. ImGui calls it when the context loads its settings at the first frame and when it saves.

```cpp src="StrataEditor/src/UI/EditorPanelRegistry.cpp#L371-L383"
if (const int version = m_LayoutVersion != 0 ? m_LayoutVersion : m_SavedLayoutVersion; version != 0)
	buffer.appendf("[%s][Layout]\nVersion=%d\n\n", c_SettingsName, version);
buffer.appendf("[%s][Open]\n", c_SettingsName);
// Panels this run did not register keep their saved state.
std::map<std::string, bool> states(m_SavedOpenStates.begin(), m_SavedOpenStates.end());
for (const Entry& entry : m_Entries)
{
	if (entry.Descriptor.Placement == EditorPanelPlacement::Docked)
		states[entry.Descriptor.Id] = entry.Open;
}
for (const auto& [id, open] : states)
	buffer.appendf("%s=%d\n", id.c_str(), open ? 1 : 0);
buffer.append("\n");
```

1. **Line 371:** the layout version is written first; when this run did not set one, the saved one is kept.
2. **Lines 374–380:** panels this run did not register keep their saved state, so a panel that is only sometimes registered is not forgotten.
3. **Line 382:** one `id=0` or `id=1` line per panel, in sorted order.

The saved text has two sections: the layout version and one line per panel. A file that this code writes has this shape.

```text
[StrataPanels][Layout]
Version=5

[StrataPanels][Open]
ContentBrowser=1
Hierarchy=1
Streaming=0
```

The reader needs one entry per section. Search for what `SettingsReadOpen` returns for each name.

```cpp src="StrataEditor/src/UI/EditorPanelRegistry.cpp#L390-L395"
EditorPanelRegistry* registry = static_cast<EditorPanelRegistry*>(handler->UserData);
if (std::strcmp(name, "Open") == 0)
	return registry;
if (std::strcmp(name, "Layout") == 0)
	return &registry->m_SavedLayoutVersion;
return nullptr;
```

The `Open` section's entry is the registry, the `Layout` section's is the address of the saved version, and ImGui skips the lines of sections it gets no entry for. `ReadLine` checks the value before it trusts it. An id with a bad character or a value other than 0 or 1 is dropped, and a version must be a whole number above zero. A saved file is untrusted input.

The reading happens at the first frame, which can come after a panel was asked for. `ReadSetting` therefore keeps a panel open when its focus was requested. `SetOpen` marks the settings as changed, which makes ImGui write the file soon after a change.

### The default layout

The default layout answers one question: where does each panel go the first time, and whenever the saved layout is no good? ImGui offers **DockBuilder**, a set of functions that build a dock tree in code by splitting a node and docking named windows into the pieces. The editor splits by proportions, not pixels, so the layout fits any window.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1613-L1623"
const float width = std::max(ImGui::GetContentRegionAvail().x, 1.0f);
const auto sideShare = [width](float share, float minimumFontSizes)
{
	return std::min(std::max(share, minimumFontSizes * ImGui::GetFontSize() / width), c_MaxSideWidth);
};
const float hierarchyWidth = sideShare(c_HierarchyWidth, c_MinHierarchyFontSizes);
const float inspectorWidth = sideShare(c_InspectorWidth, c_MinInspectorFontSizes);
ImGuiID center = dockspaceId;
const ImGuiID left = ImGui::DockBuilderSplitNode(center, ImGuiDir_Left, hierarchyWidth, nullptr, &center);
const ImGuiID right = ImGui::DockBuilderSplitNode(center, ImGuiDir_Right, inspectorWidth / (1.0f - hierarchyWidth), nullptr, &center);
const ImGuiID bottom = ImGui::DockBuilderSplitNode(center, ImGuiDir_Down, c_BottomHeight, nullptr, &center);
```

1. **Lines 1614–1617:** `sideShare` takes the larger of a fixed share and a minimum measured in font sizes, then caps it at 30 % of the width.
2. **Line 1621:** the Hierarchy is cut from the left of the dock space first.
3. **Line 1622:** the Inspector's share is divided by what the first cut left, because the second cut is a share of the remaining node.
4. **Line 1623:** the bottom area is a share of the height of the middle column only.

The constants are 0.15 and 0.20 of the width, 0.22 of the height, minimums of 16 and 18 font sizes, and the 0.3 cap. The font-size minimum is the reason the layout reads well at 200 %: a Hierarchy row names an entity of about eighteen characters, and a fixed share would crop it.

:::example[The side panels at 100 % and at 200 %]
Take a dock space 1600 pixels wide. At 100 % the font size is 14 pixels. Hierarchy: 16 × 14 ÷ 1600 = 0.14 is below 0.15, so the share is 0.15 and the node is 240 pixels. Inspector: 18 × 14 ÷ 1600 = 0.1575 is below 0.20, so the share is 0.20. The second cut divides it by 1 − 0.15, which gives 0.20 ÷ 0.85 = 0.2353 of the remaining 1360 pixels, so the node is 320 pixels.

At 200 % the font size is 28 pixels. Hierarchy: 16 × 28 ÷ 1600 = 0.28 beats 0.15 and stays below the 0.3 cap, so the node is 448 pixels. Inspector: 18 × 28 ÷ 1600 = 0.315 passes the cap, so the share is 0.3, which is 480 pixels. The two side panels take 928 pixels, which is 58 % of the width, and the Scene view keeps the rest.
:::

The remaining lines dock windows by name into the pieces. The Hierarchy goes left, and the Inspector and the Asset tab go right. Six panels go into the bottom area: Console, Problems, Content Browser, Streaming, Performance and Activity. The Scene view, the Game view and the Project Settings go into the middle. `SelectTab` then puts the Content Browser, the Inspector and the Scene view in front.

```mermaid caption="The default layout is cut from the dock space in four steps, each a share of what the previous cut left." alt="A diagram of the dock space cut into regions. The Hierarchy takes the left, the Inspector and the Asset tab the right, six tabs the bottom, and the Scene, Game and Project Settings tabs the middle."
flowchart TB
    DS["Dock space"] --> L["Left 15 %, 16 font sizes or more, 30 % at most: Hierarchy"]
    DS --> C1["Rest"]
    C1 --> Rt["Right 20 % of the width, 18 font sizes or more: Inspector, Asset"]
    C1 --> C2["Center column"]
    C2 --> B["Bottom 22 % of the height: Console, Problems, Content Browser, Streaming, Performance, Activity"]
    C2 --> M["Middle: Scene, Game, Project Settings"]
```

When does the layout apply? The dock space host decides, once per run.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1696-L1709"
if (!m_LayoutChecked)
{
	const ImGuiDockNode* node = ImGui::DockBuilderGetNode(dockspaceId);
	const bool empty = !node || (node->IsLeafNode() && node->Windows.Size == 0);
	m_ResetLayout |= empty || m_Panels.GetSavedLayoutVersion() != c_LayoutVersion;
	m_LayoutChecked = true;
}
if (m_ResetLayout)
{
	m_Panels.ResetOpenStates();
	BuildDefaultLayout(dockspaceId);
	m_Panels.SetLayoutVersion(c_LayoutVersion);
	m_ResetLayout = false;
}
```

1. **Line 1696:** the check runs once, so a person who removes every panel from the dock keeps that choice for the run.
2. **Line 1700:** an empty dock space or a saved version unlike `c_LayoutVersion` asks for the default layout.
3. **Lines 1705–1707:** a reset resets the open states, builds the layout and records the version.

Version 0, which means no saved section, differs from every real version, so a first run takes the default layout too. The **View ▸ Reset Layout** item sets the same flag by hand. `ResetOpenStates` opens every panel that is open by default and closes the rest, except one that was asked for with `Focus`, so a command run before the first frame survives.

The version rule has a history. `c_LayoutVersion` is 5. The comment in `EditorLayer.h` says that 4 added the Problems panel with Activity beside it, and that 5 put the Game view beside the Scene view and widened the Hierarchy. A layout from before such a change would show the new panels floating over the viewport.

A different case needs no version. A panel that is closed by default and later given a place, such as the Streaming panel, is handled by `DockNewToolPanels`.

```cpp src="StrataEditor/src/EditorLayer.cpp#L2402-L2416"
	const auto dockNew = [this](const char* id, const ImGuiWindow* beside)
	{
		const std::string name = m_Panels.GetWindowName(id);
		if (beside && beside->DockId != 0 && m_Panels.IsOpen(id) && !ImGui::FindWindowByName(name.c_str())
			&& !ImGui::FindWindowSettingsByID(ImHashStr(name.c_str())))
		{
			ImGui::DockBuilderDockWindow(name.c_str(), beside->DockId);
		}
	};
	const ImGuiWindow* console = ImGui::FindWindowByName(m_Panels.GetWindowName(EditorPanels::c_Console).c_str());
	for (const char* id : { EditorPanels::c_Problems, EditorPanels::c_Streaming, EditorPanels::c_Performance, EditorPanels::c_Activity })
		dockNew(id, console);
	// The Project Settings' pages need room: beside the Scene view.
	dockNew(EditorPanels::c_ProjectSettings, ImGui::FindWindowByName(m_Panels.GetWindowName(EditorPanels::c_Viewport).c_str()));
}
```

1. **Line 2405:** only a window the layout knows nothing about is docked: no existing window, no saved settings for its name.
2. **Line 2412:** the instruments dock beside the Console.
3. **Line 2415:** the Project Settings dock beside the Scene view, where pages of fields have room.

### The dock space host and the status bar

`DrawDockspace` draws two windows. The first, `EditorDockspace`, fills the work area above the status bar. It has no title bar, and it cannot be moved, collapsed or docked into another window; its size follows the editor's window. Inside it the menu bar, the main toolbar and the dock space are drawn in that order.

The second window, `StatusBar`, is a separate strip below the first, as tall as the caption text plus padding, with no docking. Splitting them keeps the dock tree from ever swallowing the status bar. The pills inside it are the subject of [the status page](../editor-ui/status.md). While no project is open, `DrawLauncher` draws a similar full window named `EditorLauncher` with the menu bar and the launcher panel instead.

### The menu bar and the main toolbar

The menu bar has File, Edit, View, Entity, Scripts and Help. Every item is written by hand in `EditorLayer::DrawMenuBar`, except the View menu's panel toggles, which `DrawMenuItems` makes from the registry. Panels without a menu path come first, then one menu per path in sorted order. The full list of items is in [the editor reference](../reference/editor.md). The main toolbar below it holds the :term[gizmo]{id=gizmo-start} tools, the space and snap controls, the play controls and the script build and export buttons.

Menu items follow one pattern. Look at the File menu's scene items, where a menu item either runs a command through the UI path or first asks the person.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1771-L1780"
if (ImGui::MenuItem("New Scene", nullptr, false, !m_Context.IsPlaying()))
	RequestDiscardChanges([this]() { RunEditorCommand(m_Context, m_Commands, "scene.new", { { "force", true } }); });
UI::ItemProbe::Record("Menu.File.NewScene", !m_Context.IsPlaying());
const bool canOpenScene = m_Context.HasProject() && !m_Context.IsPlaying();
if (ImGui::MenuItem("Open Scene...", "Ctrl+O", false, canOpenScene))
	ShowOpenSceneDialog();
UI::ItemProbe::Record("Menu.File.OpenScene", canOpenScene);
if (ImGui::MenuItem("Save Scene", "Ctrl+S", false, !m_Context.IsPlaying()))
	SaveScene();
UI::ItemProbe::Record("Menu.File.SaveScene", !m_Context.IsPlaying());
```

1. **Line 1772:** **New Scene** hands its action to `RequestDiscardChanges`, so the action runs once the person decided, and it passes `force: true`.
2. **Line 1778:** **Save Scene** is disabled while playing, and calls `SaveScene` itself.

### Window events, commands and the title

`OnEvent` handles what the window sends. A close request asks first when anything could be lost: the scene is modified, saves are in flight, or project settings or preferences are unwritten. Then it keeps running and asks through `RequestQuit`, and closes the host from the dialog.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1087-L1097"
dispatcher.Dispatch<WindowCloseEvent>([this](WindowCloseEvent&)
{
	if (!m_Context.IsSceneModified() && !m_Context.HasSavesInFlight() && !m_Context.HasUnwrittenProjectSettings()
		&& !m_Context.HasUnwrittenPreferences())
	{
		return false;
	}
	// Keep running and ask first (after the saving dialog while saves write); closing happens from the dialog.
	RequestQuit([this]() { m_Host->Close(); });
	return true;
});
```

1. **Lines 1089–1093:** with nothing to lose, returning false lets the close continue.
2. **Line 1095:** otherwise the layer asks, and the question's answer calls `Close` on the host.

Files dropped on the window follow two paths. A `.stproj` file opens that project through `RequestReleaseProject`, also from the launcher. Other files go to the Content Browser's import, and without a project they only report an error. The window title is "Strata Editor", the project's name, the scene's name, a star while the scene is modified and the play state in brackets while playing; the launcher's title is plain.

The layer registers two commands that only a window can run. `editor.showPanel` takes a panel id, or "Scene" for the Scene view, and focuses that panel with `Focus`. It can also switch the Content Browser to its scripts or fill the Hierarchy's search field. It fails with a message in a headless editor and while the launcher shows.

`editor.showDialog` opens a dialog for the person, such as export or preferences. Both are session commands: they change what the window shows and record no :term[undo step]{id=undo-step}. Agents use them as people use the menu.

Two more window facts belong here. When a command script ends, the layer logs it and sets the exit code to 1 if a step failed. With `--screenshot` the last frame is saved as a PNG, but only together with `--frames` or `--quit-after-commands`.

### What the shell does not do

Two absences are deliberate. The first is panels torn out into windows of their own. The ImGui platform backend has a single main viewport, with no platform windows of ImGui's own, and the engine's plan lists multi-viewports as later work. Docked and floating panels stay inside the one editor window.

The second is editor extensions written by a game project. Only the editor registers panels, in `EditorLayer::RegisterBuiltinPanels`. Games link no :term[tooling layer]{id=tooling-layer}, so a game has no way to ship a panel. A game draws its own interface with the game UI.

## Asking the person

Some actions replace what the person has: opening another scene, closing the project, quitting. The shell asks before it lets them run, and this section is the home of how it asks. The core guards the commands, as [saving](../editor/saving.md) teaches: a command that would replace unsaved work refuses unless it carries `force`. The UI is where a person can answer, so it adds `force` solely for the question the person answered.

`RequestDiscardChanges` is the front door. It takes an action, which is a function that runs the command with `force: true`.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1271-L1289"
void EditorLayer::RequestDiscardChanges(std::function<void()> action)
{
	// A save in flight is never lost: the action waits for it in the saving dialog, then asks about what is still unsaved.
	if (m_Context.HasSavesInFlight())
	{
		m_ActionAfterSaves = std::move(action);
		m_OpenSavingModal = true;
		return;
	}
	if (m_Context.IsSceneModified())
	{
		m_PendingDiscardAction = std::move(action);
		m_DiscardQuestionVersion = m_Context.GetUndoStack().GetVersion();
		m_SceneChangedSinceQuestion = false;
		m_OpenUnsavedChangesModal = true;
		return;
	}
	action();
}
```

1. **Lines 1274–1278:** a save in flight is never lost: the action waits in the Saving modal.
2. **Lines 1280–1286:** with unsaved changes, the layer stores the action and the :term[undo stack's]{id=undo-stack} version, and opens the modal.
3. **Line 1288:** with nothing to lose, the action runs at once.

`RequestReleaseProject` wraps it. After the scene's question, it asks about project settings that could not be written, and offers to write them again through `project.save`. `RequestQuit` wraps that. It also asks about unwritten preferences, with the same offer through `preferences.save`. Each step asks the earlier question again if the scene changed meanwhile.

The layer draws each of these questions as a modal of its own. The Saving modal lists a progress bar for every save in flight, and its **Cancel** button stops the action that waits, never a save. The two modals about settings and preferences show the file's error and offer a write again, a discard and a cancel.

The modal has three buttons. **Save** saves the scene and then asks again about whatever changed in between. **Cancel** drops the action. `Don't Save` is the subtle one, because the world can change while the person reads.

```cpp src="StrataEditor/src/EditorLayer.cpp#L2764-L2781"
if (UI::DialogButton("UnsavedChanges.DontSave", "Don't Save"))
{
	// The answer is for the changes the person was asked about: changes made since (an agent's, a script's) are asked
	// about again rather than discarded unseen. Without unsaved changes left, nothing is discarded either way.
	const uint64_t version = m_Context.GetUndoStack().GetVersion();
	if (m_Context.IsSceneModified() && version != m_DiscardQuestionVersion)
	{
		m_DiscardQuestionVersion = version;
		m_SceneChangedSinceQuestion = true;
	}
	else
	{
		ImGui::CloseCurrentPopup();
		if (m_PendingDiscardAction)
			m_PendingDiscardAction();
		m_PendingDiscardAction = nullptr;
	}
}
```

1. **Line 2769:** the stored version is compared with the undo stack's version now.
2. **Lines 2771–2772:** when it moved, the question stays open and says that the scene changed while the person was asked.
3. **Lines 2776–2779:** only an answer for the changes that were asked about runs the action.

An agent can edit the scene while the question is open. If `Don't Save` discarded what the person never saw, work would vanish. The version check turns that into a second question, with a warning that `Don't Save` discards the new changes too.

```mermaid caption="The question: saves in flight first, then the modal, with a second ask when the scene changed meanwhile." alt="A flow chart. A request first checks for saves in flight and waits in the saving dialog. Then it checks whether the scene is modified and shows the question. Save, discard and Cancel follow. Discard with a changed undo version asks again; otherwise the action runs with force."
flowchart TD
    A["RequestDiscardChanges(action)"] --> B{"Saves in flight?"}
    B -->|yes| S["Saving dialog, then ask again"]
    B -->|no| M{"Scene modified?"}
    M -->|no| X["Run action with force: true"]
    M -->|yes| Q["Unsaved Changes modal"]
    Q -->|Save| V["Save, then ask again"]
    Q -->|Cancel| N["Drop the action"]
    Q -->|Don't Save| W{"Undo version moved?"}
    W -->|yes| Q
    W -->|no| X
```

::figure{id=unsaved-changes-dialog}

The question must also work from inside other dialogs. The project dialogs and the recovery dialog are modals, and each may need to ask about unsaved changes. Search for how the question guards itself against a second call in one frame.

```cpp src="StrataEditor/src/EditorLayer.cpp#L2666-L2677"
void EditorLayer::DrawUnsavedChangesModal()
{
	// A dialog that asked draws the question over itself before the window's own call comes (popups belong to the level
	// they are opened at: opened over the whole window, the question would close that dialog).
	if (m_UnsavedChangesModalFrame == ImGui::GetFrameCount())
		return;
	m_UnsavedChangesModalFrame = ImGui::GetFrameCount();
	if (m_OpenUnsavedChangesModal)
	{
		UI::OpenModal(c_UnsavedChangesModal);
		m_OpenUnsavedChangesModal = false;
	}
```

1. **Lines 2670–2672:** a call that already drew this frame returns at once, so the window's own call after the dialog's does not draw twice.
2. **Lines 2673–2676:** the modal is opened once, when a request set the flag.

ImGui keeps one popup per level. A popup opened from inside another popup's `Begin` and `End` is one level deeper and leaves its parent open. A popup opened over the whole window is at level 0 and closes every other one. `DrawDiscardQuestion` is the shell's way for a dialog to ask the question at its own level. The dialog calls it between the begin and the end of its modal every frame, and the layer's own call later in the frame then returns at once.

The sketch below counts levels in a stack, which is the same rule in miniature. Predict the two lines before you read the output.

```cpp sketch="editor-ui-shell-popups.cpp"
// A toy of ImGui's popup levels: opening a popup at a level closes every popup at that level and deeper.
#include <cstdio>
#include <string>
#include <vector>

class PopupStack
{
public:
	void Open(const std::string& name, size_t level)
	{
		if (m_Open.size() > level)
			m_Open.resize(level);
		m_Open.push_back(name);
	}

	void Print(const char* what) const
	{
		std::printf("%s:", what);
		for (const std::string& name : m_Open)
			std::printf(" [%s]", name.c_str());
		std::printf("\n");
	}

private:
	std::vector<std::string> m_Open;
};

int main()
{
	// The Recovery dialog is a modal opened over the whole window: level 0.
	PopupStack wrong;
	wrong.Open("Recovery", 0);
	wrong.Open("Unsaved Changes", 0);
	wrong.Print("question over the window");

	// Drawn between the dialog's Begin and End, the question is one level deeper.
	PopupStack right;
	right.Open("Recovery", 0);
	right.Open("Unsaved Changes", 1);
	right.Print("question inside the dialog");
	return 0;
}
```

```text output-of="editor-ui-shell-popups.cpp"
question over the window: [Unsaved Changes]
question inside the dialog: [Recovery] [Unsaved Changes]
```

1. **Lines 11–12:** opening at a level cuts every popup at that level and deeper.
2. **Lines 31–34:** opened at level 0, the question replaces the dialog.
3. **Lines 37–40:** opened at level 1, the question stays beside the dialog's own popup.

The first line shows a question opened over the window: the Recovery dialog is gone. The second shows the question drawn inside the dialog: both stay. The Saving, Project Settings Not Written and Preferences Not Written modals use the same function, in a fixed order, and each returns right after it draws.

:::why
Why not a callback that the dialog gives the layer? A modal waits for the person, and a callback would have to wait too, or draw later. Drawing the question inside the dialog keeps the order of the person's attention: the dialog stays, the question sits over it, and the answer runs one action.
:::

## Tracing a click

The shell ends where the core begins. Take **File ▸ Save Scene** and follow it. The menu item stands at line 1778 of `EditorLayer.cpp`, and the line after it calls `SaveScene`.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1439-L1455"
bool EditorLayer::SaveScene(std::function<void(bool saved)> then)
{
	if (m_Context.IsPlaying())
	{
		ST_WARN("Stop playing before saving: changes made while playing are discarded");
		return false;
	}
	if (!m_Context.GetSceneHandle().IsValid())
		return SaveSceneAs(std::move(then));
	// The save writes in the background: its outcome comes in a later frame (failures as a notification of their own).
	m_CommandRunner.Run(m_Context, m_Commands, "scene.save", nlohmann::json::object(), [then = std::move(then)](const EditorCommandResult& result)
	{
		if (then)
			then(result.Success);
	}, CommandOrigin { CommandSource::UI });
	return true;
}
```

1. **Lines 1441–1445:** playing a scene refuses the save with a warning, because play changes are discarded.
2. **Line 1447:** a scene with no file yet goes to Save As.
3. **Lines 1449–1453:** the runner starts `scene.save` with the UI origin; the save writes in the background, and the callback reports the outcome.

The :term[command runner]{id=command-runner} executes `scene.save` in the core. It snapshots the scene in the frame and writes it on a job, as [saving](../editor/saving.md) explains. The journal records an entry whose source is the UI, which the Activity panel lists. Nothing in the shell wrote a file or a scene field. That is the contract working: the menu is a client of commands.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Each panel begins its own window | Small tools and many ImGui samples | Less code per panel | The View menu, saved open states, stable names, focus handling |
| Layout saved only by the ImGui file, without a version | ImGui's default | No bump to remember | A new default panel would float over the viewport in old layouts |
| Floating platform windows (multi-viewports) | ImGui's docking branch, large editors | Panels on a second monitor | One main viewport that every backend and test can rely on |
| Panels as add-ons loaded from a game project | Engines with editor extension systems | Games add tools | Crash containment and a stable C interface for editor code |
| The panel layer calls the application directly | Quick prototypes | No host or shell interfaces | UI tests that run without a window, a :term[graphics card]{id=gpu} or an application |

The sources are in Further reading.

## How it is tested

The suite `Editor.UI` in `StrataTests/src/Editor/EditorUITests.cpp` draws the whole layer in an `ImGuiHarness` against a fake host (`FakeEditorHost`), so it needs no window and no graphics card. Its test "The default layout is viewport first, with the Content Browser showing" checks two facts. The side panels take about their shares, and the viewport keeps at least 45 % of a 3840 × 2054 window at 150 %. The test also checks which tab shows in each node.

The test "Panels close and reopen, and :term[imgui.ini]{id=imgui-ini} remembers which are open" saves the settings text and reads it into a new editor. "The panel registry checks what registers and draws open panels in their windows" covers the validation. The layout-version test named in the last section covers the version rule.

:::tip
A test starts a `HarnessEditor` with a display size and a scale, runs `Frames(n)` and finds a window with `FindPanelWindow`. It reads positions and tabs from ImGui itself, so a layout test checks what the person would see.
:::

The suite `Editor.UI.Source` scans the sources. "Panels draw through the panel registry" fails when a panel begins its own window, and "Panels change files only through commands" fails when a panel writes a file. The suite `Editor.DataSafety` covers the question. Its test "The UI still asks about unsaved changes, and its answer discards them" clicks through the modal, and another test checks that opening a scene asks first. Run them with `StrataTests --test-suite=Editor.UI*` and `--test-suite=Editor.DataSafety`.

## Changing it safely

To add a panel, write a class with `OnImGuiRender`, give `RegisterBuiltinPanels` a descriptor and a factory, and decide `OpenByDefault`. A panel that is open by default and docked changes the default layout: dock it in `BuildDefaultLayout` and raise `c_LayoutVersion`. A panel that is closed by default is placed by `DockNewToolPanels` if it should dock with a neighbor. Writing one step by step is the job of [the panel tutorial](../editor-ui/tutorial-panel.md).

Keep to the rules above. Do not begin a window yourself, because the scan test fails. Pass a command, not a write. Keep costly work out of `OnImGuiRender`, and let `OnUpdate` collect what a closed panel must show.

If a panel animates without input, report `IsAnimating`, or the idle throttle will slow it. Before a commit, run `Editor.UI*`, `Editor.UI.Source` and `Editor.DataSafety`, and the whole suite as the engine's guide asks. A regression test for a layout bug must fail without the fix, as the test below did.

## What went wrong before

A new default panel shipped without a version bump is a mistake that has a test now. Version 4 added the Problems and Activity panels, and a layout saved before it had no place for them. The test "A layout saved before the Problems and Activity panels gives way to the default layout, which docks them with the Console" starts an editor, takes its settings text and strips the two panels. It writes version 3 into that text and starts a second editor from it.

The test then checks that Problems is open and docked with the Console, that Activity is closed until asked for and then joins them, and that the saved text records the current version. The last rule of the contract came out of it.

## Summary

- The shell has four parts. `EditorApplication` installs the theme, the fonts and the layout file and gives the layer an `EditorHost`; `EditorLayer` is the `EditorShell`; the registry owns the panels.
- The registry calls `OnUpdate` for every panel each frame, `OnImGuiRender` while a window shows and `OnHidden` otherwise, and it asks again for a focus request for up to four frames, after a modal.
- The default layout is cut from proportions with font-size minimums, and its version replaces any layout saved with another version, including no version, and resets the open states.
- A modal that asks while it is open draws the question inside itself, because ImGui keeps one popup per level, and `Don't Save` asks again when the undo version moved.
- A menu item calls a command through the UI origin, so the core, the journal and the undo stack see one operation.

## Check yourself

1. Which object does a panel call when it needs the question about unsaved changes? (a) `EditorHost`; (b) `EditorShell`, reached through the panel context; (c) `EditorApplication`; (d) the command registry.

   :::answer{tests="shell-layers"}
   (b). The shell is the interface for dialogs and questions. (a) is wrong because the host offers window and frame services to the layer, not to panels. (c) is wrong because no panel may reach the application. (d) is wrong because the question needs a dialog, and commands never draw.
   :::

2. A panel is open, but its tab is behind another tab. Which hooks run this frame: `OnUpdate`, `OnImGuiRender`, `OnHidden`?

   :::answer{tests="panel-life"}
   `OnUpdate` and `OnHidden`. `OnUpdate` runs for every panel every frame, and `OnHidden` runs because `Begin` returned false. `OnImGuiRender` runs only while the window is visible.
   :::

3. The default layout gains an Audio panel that is open by default, and `c_LayoutVersion` stays 5. What does a person with a saved version-5 layout see?

   :::answer{tests="layout-version"}
   The saved layout is kept, because its version equals `c_LayoutVersion`. The Audio panel has no saved window, so it floats over the viewport, which is the failure the version rule prevents. The fix is to raise the version to 6.
   :::

4. The recovery dialog is open and it wants to ask about unsaved changes. Where is the question drawn, and why?

   :::answer{tests="ask-person"}
   Inside the dialog, through `DrawDiscardQuestion`. A question opened over the whole window sits at level 0, and ImGui would close the recovery dialog because it keeps one popup per level.
   :::

5. The person sees the question, an agent adds an entity, and the person presses `Don't Save`. What happens next?

   :::answer{tests="ask-person"}
   The undo version moved, so the modal stays, warns that the scene changed and says that `Don't Save` discards those changes too. Only a second answer runs the action.
   :::

6. Which command does **File ▸ Save Scene** run, with which origin, and where does the entry appear?

   :::answer{tests="click-trace"}
   The menu item runs `scene.save` with `CommandOrigin { CommandSource::UI }`, started by `EditorLayer::SaveScene` through the runner. The entry appears in the Activity panel as an action of the UI.
   :::

## Exercises

1. **Basic.** A person saved a layout with `c_LayoutVersion` at 5. You raise it to 6 and they start the new build. What do they see, and what does the settings file say afterwards?

   :::answer[Worked solution]{tests="layout-version"}
   The saved version 5 differs from 6, so `m_ResetLayout` becomes true on the first frame. `ResetOpenStates` opens every panel that is open by default and closes the others, `BuildDefaultLayout` replaces the dock tree, and `SetLayoutVersion(6)` records the version. The person loses their arrangement and their open panels. The next save writes a version line of 6 under `[StrataPanels][Layout]`.
   :::

2. **Medium.** Trace **File ▸ Save Scene** with breakpoints. Name the file and function where the UI starts the command, and find the entry in the Activity panel.

   :::answer[Worked solution]{tests="click-trace"}
   Set a breakpoint at the `MenuItem("Save Scene", ...)` line in `EditorLayer::DrawMenuBar`, then in `EditorLayer::SaveScene`, then at the start of the `scene.save` handler. The call stack shows `EditorCommandRunner::Run` from `SaveScene` with `CommandSource::UI`. After the save, open **View ▸ Activity**: the newest entry is `scene.save` from the UI.
   :::

3. **Hard.** Write the `Don't Save` decision as a function of the version asked about, the undo version now and whether the scene is modified. Run it for three cases and read the output.

   :::answer[Worked solution]{tests="ask-person" solution="sketches/editor-ui-shell-dontsave.cpp"}
   The function returns true when the action may run. It compares the versions only while the scene is modified, because without unsaved changes nothing is discarded either way.

   ```cpp sketch="editor-ui-shell-dontsave.cpp"
   // The Don't Save decision: the answer counts only for the changes the person was asked about.
   #include <cstdint>
   #include <cstdio>

   struct Question
   {
   	uint64_t AskedVersion = 0;
   	bool ChangedSince = false;
   };

   // Returns true when the pending action may run.
   bool DontSave(Question& question, uint64_t undoVersion, bool modified)
   {
   	if (modified && undoVersion != question.AskedVersion)
   	{
   		question.AskedVersion = undoVersion;
   		question.ChangedSince = true;
   		return false;
   	}
   	return true;
   }

   int main()
   {
   	Question quiet { 7, false };
   	std::printf("nothing changed: runs=%d\n", DontSave(quiet, 7, true));

   	Question edited { 7, false };
   	const bool firstRuns = DontSave(edited, 8, true);
   	std::printf("an agent edited: runs=%d warning=%d\n", firstRuns, edited.ChangedSince);
   	std::printf("second answer: runs=%d\n", DontSave(edited, 8, true));

   	Question undone { 7, false };
   	std::printf("edited, then undone and saved: runs=%d\n", DontSave(undone, 9, false));
   	return 0;
   }
   ```

   ```text output-of="editor-ui-shell-dontsave.cpp"
   nothing changed: runs=1
   an agent edited: runs=0 warning=1
   second answer: runs=1
   edited, then undone and saved: runs=1
   ```

   1. **Lines 14–19:** with a moved version the question stays open and records the new version.
   2. **Line 20:** otherwise the answer is for what was asked, and the action may run.
   3. **Lines 29–31:** after the warning, a second answer runs the action.

   The first case runs at once. The second refuses, records the new version and sets the warning, and the second answer then runs. The third runs, because the changes were undone and saved.
   :::

## Where it lives in Strata

- `StrataEditor/src/EditorApplication.cpp`: `EditorApplication`, `ApplicationEditorHost`, the option table `c_Arguments`.
- `StrataEditor/src/EditorHost.h`: `EditorHost`. `StrataEditor/src/UI/EditorShell.h`: `EditorShell`.
- `StrataEditor/src/EditorLayer.cpp`: `EditorLayer`, `BuildDefaultLayout`, `DrawDockspace`, `DrawMenuBar`, `DrawUnsavedChangesModal`, `DockNewToolPanels`; `EditorLayer.h`: `c_LayoutVersion`.
- `StrataEditor/src/UI/EditorPanelRegistry.h` and `.cpp`: `EditorPanel`, `EditorPanelDescriptor`, `EditorPanelRegistry`.
- Commands: `editor.showPanel`, `editor.showDialog`, `scene.save`. Options: `--layout`, `--ui-scale`, `--screenshot`, `--frames`.
- Tests: the suites `Editor.UI`, `Editor.UI.Source` and `Editor.DataSafety`.

## Further reading

- The Dear ImGui documentation on docking and settings handlers: the library's own account of dock nodes and ini sections (intermediate).
- Game Programming Patterns, "Service Locator" and "Observer": the patterns behind a small interface between a tool and its host (intermediate).
- Game Engine Architecture, the chapter on tools: how studios structure an editor's windows (advanced).
