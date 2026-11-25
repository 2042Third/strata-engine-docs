---
id: editor-ui/settings-windows
title: "Settings windows from schemas"
description: "How Strata draws its two settings windows: pages made from each section's fields, hand-written pages for the complex ones, and binding capture."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/inspectors, world/projects-settings, physics/collision-layers, input/rebinding, image/quality-settings]
time: 85
learn:
  - id: map
    text: explain how the settings registry, the page registry and the settings browser make a window
  - id: choose
    text: choose a generated page or a registered page for a new settings section
  - id: trace-edit
    text: trace one edit from a widget to its command and to the refreshed copy of the values
  - id: capture-rules
    text: explain how binding capture takes the keyboard from ImGui and when it ends
  - id: refused-value
    text: predict what a generated page shows for a stored value its section refuses
since: 0.6.0
status: final
---

Strata has two windows for settings: the Project Settings panel, which holds what belongs to one game, and the Preferences dialog, which holds what belongs to the person using the editor. Neither window has a list of hand-drawn forms. Each draws a page for every settings section that the engine's modules registered, and the page comes from the section's fields. A few sections are too complex for that, and the editor registers a page for each of them.

This page shows how the pieces fit, how an edit travels to a command, and how a page that listens for a key press keeps the rest of the editor from reacting to it. It does not teach what a section holds, what a quality row costs, or how players rebind controls: those have their own pages, linked where they matter.

## The problem and how engines solve it

Imagine a game with twenty settings sections. One holds the fixed rate of the physics step and a switch for :term[interpolation]{id=interpolation}. Another holds a sound volume. A third holds the names of the :term[collision layers]{id=collision-layer}. A programmer who adds a section must also add a way to edit it, or the only editor is a text file.

The first answer is a hand-written page per section. A page with two fields costs about forty lines: a label, a widget, a range check, a call that writes the value, and a reset button. Twenty sections cost eight hundred lines, and each page can drift from its section. When a module raises a limit from 240 to 480, a page that copied the old limit still refuses the new values.

The second answer is one generic page for everything, drawn from a description of the data. A section lists its fields: a name, a title, a type and a range. The page loops over the fields and picks a widget by type. A new section then needs no user interface code.

The limit is the shape of the data. A table of layers that collide with each other, or a list of actions with bindings, is not a flat list of fields. A generic page for it is of no use.

Strata takes the third answer: generate where the data allows it and register a hand-written page where it does not. The registry records whether a section is simple, which means it lists fields, or complex, which means it has none and brings its own schema and checks. A simple section gets a generated page for free. A :term[complex section]{id=complex-section} needs a page, and a test fails when one lacks it. A simple section may still ask for its own page when the generated one would hide too much, and Graphics Quality does that.

The cost is a second path. Two kinds of pages must follow the same rules about commands and refreshing, and the rules cannot live in the generated page alone. The contract below states them for both.

## The map

A **settings browser** is the part of a settings window that lists the pages, grouped by category, with a search field, and shows the selected page beside the list. A **settings page** is what the browser draws for one section: a form the person edits. The two windows draw the same browser class with a different kind: `SettingsWindowKind::Project` or `SettingsWindowKind::Preferences`. The kind decides which sections the browser lists. A section of :term[project scope]{id=project-scope} belongs to the project file, and a section of :term[user scope]{id=user-scope} belongs to the preferences file.

```mermaid caption="Sections come from the settings registry, custom pages from the page registry, and both feed the browser that the two windows draw." alt="A diagram of four boxes. The settings registry and the page registry feed the settings browser. The browser is drawn by the Project Settings panel and by the Preferences dialog. Pages send commands to the editor, and the commands change the stored values."
flowchart LR
  SR["SettingsRegistry: sections"] --> SB["SettingsBrowser"]
  PR["EditorSettingsPageRegistry: pages by section id"] --> SB
  SB --> PSP["Project Settings panel"]
  SB --> PD["Preferences dialog"]
  SB --> PG["SettingsPage"]
  PG -->|"project.setSettings, preferences.set"| CMD["Command"]
  CMD --> VAL["Stored values and their version"]
  VAL -->|"version changed"| PG
```

The files are few. `StrataEditor/src/UI/SettingsPages.h` and `StrataEditor/src/UI/SettingsPages.cpp` hold the page interface `SettingsPage`, the registry `EditorSettingsPageRegistry`, the `SettingsBrowser` and the generated page. `StrataEditor/src/UI/SettingsFieldProperty.cpp` turns a field into a property that the widget code of the Inspector can draw. `StrataEditor/src/Panels/ProjectSettingsPanel.cpp` and `StrataEditor/src/UI/PreferencesDialog.cpp` are the two windows. The custom pages are `GraphicsQualityPage`, `CollisionLayersPage`, `InputActionsPage` and `ExternalEditorPage`, and `StrataEditor/src/UI/BindingCapture.cpp` serves the third.

Everything here runs on the :term[main thread]{id=main-thread}, inside an :term[ImGui]{id=dear-imgui} frame. A page is drawn every frame while it shows, so a page must be cheap: that is the reason for the refresh rule in the contract.

## The contract

A page author may assume these things, and must do these things.

- **A page draws, and a command changes.** Every edit runs a command with the origin `CommandOrigin { CommandSource::UI }`: `project.setSettings` for a project section, `preferences.set` for a user section, or the command that owns the data, such as `project.setCollisionLayers` for the :term[layer table]{id=layer-table}. The page never writes a value itself. The reason: a command checks the value and appears in the activity journal, a project command records one :term[undo step]{id=undo-step} (`preferences.set` records none), and an agent that calls the same command gets the same checks.
- **A page keeps copies and reads again when the version changes.** The values of the project and of the preferences each carry a version number that grows with every change. A page stores a copy and the version it read. Each frame it compares the version and reads nothing unless the number moved. The reason: a form with a hundred fields drawn at 60 :term[frames per second]{id=frame-rate} would otherwise read the same :term[JSON]{id=json} text 6,000 times each second.
- **A page is made again when its project changes.** The project generation is a number that changes whenever a project opens or closes. The browser keeps the page object while the selection and the generation stay the same, and makes a new one otherwise. The Preferences dialog also drops its page when it opens again, so it shows no edit that was typed but never applied.
- **A complex section has a page.** The test `Every registered section has a page` in the suite `Editor.UI.ProjectSettings` walks the process registry and fails for a complex section without one. A simple section needs none.
- **A refused value is shown with its reason.** A command that refuses an edit changes nothing, and the page reads again to show the value that stayed.

:::rule
Every change to the scene or the project goes through a command, and panels only draw state and call commands. The settings pages are panels: they hold no write path of their own. See [Commands](../editor/commands.md) for what a command promises.
:::

:::example
Take the Timing page of the project, a generated page for the section `Scene.Timing`. It has two fields, **Fixed Rate** and **Interpolation**. The page opens with a copy of the value, say `{"FixedRate":"Scene","Interpolation":true}` at version 7.

You click the check box of **Interpolation**. The page puts `false` into a copy of the whole value and runs `project.setSettings` with `section` and `value`. The command validates, sets the value, records the undo step "Set Timing" and moves the version to 8. The page sees 8 against its 7, reads again, and draws the box with its mark off. Press **Ctrl+Z** and the same path runs backward: the version moves again and the page follows.
:::

## A toy version

The toy below has the same four parts in about a hundred lines. It has a section with fields, a store with a version, a generated page, and a registry that lets a custom page replace the generated one. The store changes only through `SetValue`, the toy's command. That command refuses a value outside its range and changes nothing then. The page keeps a copy and counts how often it reads the store.

:::question
The toy uses classes, references and calls such as `store.Values.count(...)`. If these are new, read [Programming 3](../basics/programming-3.md) first; the classes with `virtual` and `override` are taught in [C++ classes](../basics/cpp-classes.md).
:::

The program draws two sections over four frames. Watch which frames read the store, and what the refused edit in the last frame does.

```cpp sketch="editor-ui-settings-windows-toy.cpp"
// A toy settings window: a generic page drawn from a section's fields, custom pages by section id,
// edits that run one command, and a copy of the values read again only when their version changed.
#include <cstdio>
#include <functional>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <vector>

struct Field
{
	std::string Name;
	float Default;
	float Min;
	float Max;
};

struct Section
{
	std::string Id;
	std::vector<Field> Fields;
};

struct Store
{
	std::map<std::string, float> Values;
	unsigned Version = 0;
};

// The only way to change the store: a refused value changes nothing and says why.
bool SetValue(Store& store, const Section& section, const std::string& name, float value)
{
	for (const Field& field : section.Fields)
	{
		if (field.Name != name)
			continue;
		if (value < field.Min || value > field.Max)
		{
			std::printf("  command refused: %s %.2f is outside %.2f to %.2f\n", name.c_str(), value, field.Min, field.Max);
			return false;
		}
		store.Values[name] = value;
		store.Version++;
		std::printf("  command: set %s.%s = %.2f\n", section.Id.c_str(), name.c_str(), value);
		return true;
	}
	return false;
}

using Edits = std::map<std::string, float>; // The edits that finished this frame

class Page
{
public:
	virtual ~Page() = default;
	virtual void Draw(Store& store, const Edits& finished) = 0;
};

class GenericPage final : public Page
{
public:
	explicit GenericPage(const Section& section)
		: m_Section(section)
	{
	}

	void Draw(Store& store, const Edits& finished) override
	{
		if (!m_Seen || *m_Seen != store.Version)
		{
			m_Seen = store.Version;
			m_Copy.clear();
			for (const Field& field : m_Section.Fields)
				m_Copy[field.Name] = store.Values.count(field.Name) ? store.Values[field.Name] : field.Default;
			m_Reads++;
		}
		for (const Field& field : m_Section.Fields)
			std::printf("  %s = %.2f\n", field.Name.c_str(), m_Copy[field.Name]);
		for (const auto& edit : finished)
		{
			if (SetValue(store, m_Section, edit.first, edit.second))
				m_Seen.reset(); // Read again: the value the command applied
		}
	}

	int GetReads() const { return m_Reads; }
private:
	const Section& m_Section;
	std::map<std::string, float> m_Copy;
	std::optional<unsigned> m_Seen;
	int m_Reads = 0;
};

class CustomPage final : public Page
{
public:
	void Draw(Store&, const Edits&) override { std::printf("  (a page drawn by hand)\n"); }
};

int main()
{
	const Section audio { "Audio.Mixer", { { "Volume", 0.8f, 0.0f, 1.0f }, { "Pitch", 1.0f, 0.5f, 2.0f } } };
	const Section layers { "Scene.Layers", {} };
	std::map<std::string, std::function<std::unique_ptr<Page>(const Section&)>> custom;
	custom["Scene.Layers"] = [](const Section&) { return std::make_unique<CustomPage>(); };

	Store store;
	for (const Section* section : { &audio, &layers })
	{
		const auto found = custom.find(section->Id);
		std::unique_ptr<Page> page = found != custom.end() ? found->second(*section) : std::make_unique<GenericPage>(*section);
		std::printf("%s\n", section->Id.c_str());
		const std::vector<Edits> frames = { {}, {}, { { "Volume", 0.5f } }, { { "Volume", 3.0f } } };
		for (size_t frame = 0; frame < frames.size(); frame++)
		{
			std::printf(" frame %zu\n", frame + 1);
			page->Draw(store, frames[frame]);
		}
		if (const auto* generic = dynamic_cast<const GenericPage*>(page.get()))
			std::printf(" reads of the store: %d\n", generic->GetReads());
	}
	return 0;
}
```

```text output-of="editor-ui-settings-windows-toy.cpp"
Audio.Mixer
 frame 1
  Volume = 0.80
  Pitch = 1.00
 frame 2
  Volume = 0.80
  Pitch = 1.00
 frame 3
  Volume = 0.80
  Pitch = 1.00
  command: set Audio.Mixer.Volume = 0.50
 frame 4
  Volume = 0.50
  Pitch = 1.00
  command refused: Volume 3.00 is outside 0.00 to 1.00
 reads of the store: 2
Scene.Layers
 frame 1
  (a page drawn by hand)
 frame 2
  (a page drawn by hand)
 frame 3
  (a page drawn by hand)
 frame 4
  (a page drawn by hand)
```

1. **Lines 32–49:** `SetValue` is the toy's command: it checks the range first, so a refused value changes nothing, and it raises the version only on success.
2. **Lines 68–77:** `Draw` compares the version it saw with the store's and copies the values only when they differ; `m_Reads` counts the copies.
3. **Lines 80–84:** a finished edit runs the command, and `m_Seen.reset()` makes the next frame read again.
4. **Lines 95–98:** `CustomPage` stands for a page drawn by hand and ignores the store.
5. **Lines 111–112:** the registry is asked first, and the generated page is the fallback.

The toy shows four things. The generated page reads the store in frame 1 and again only after a change moved the version, never in frame 2. An edit runs the command once, in the frame where the edit finishes. The refused edit in frame 4 changes nothing, so the version stays and the page does not read again. The section without fields never reaches the generic page at all: the registry hands its :term[id]{id=id} to the custom factory first.

## The real code

The real code differs from the toy in what a field is, in how the form is drawn, and in how many things can go wrong. It also adds the browser, which the toy omits.

### The registry and the browser

`EditorSettingsPageRegistry` maps a section id to a factory, a function that makes the page. `Register` refuses an empty factory and an id that already has one, and logs the reason. `CreatePage` is the choice between the two paths.

```cpp src="StrataEditor/src/UI/SettingsPages.cpp#L420-L427"
Scope<SettingsPage> EditorSettingsPageRegistry::CreatePage(EditorContext& context, const SettingsSection& section, SettingsWindowKind window) const
{
	if (const auto it = m_Factories.find(section.Id); it != m_Factories.end())
		return it->second(context, section, window);
	if (section.IsSimple())
		return CreateScope<GenericSettingsPage>(section, window);
	return nullptr;
}
```

The editor registers its four pages in the :term[constructor]{id=constructor} of `EditorLayer`, next to the panels. The id of the External Editor section, `Editor.ExternalEditor`, is the only user section among them.

```cpp src="StrataEditor/src/EditorLayer.cpp#L222-L238"
m_SettingsPages.Register(ExternalEditor::c_SettingsSection, [](EditorContext& context, const SettingsSection&, SettingsWindowKind)
{
	return CreateScope<ExternalEditorPage>(context);
});
m_SettingsPages.Register(ProjectCollisionLayers::c_SectionId, [](EditorContext&, const SettingsSection&, SettingsWindowKind)
{
	return CreateScope<CollisionLayersPage>();
});
m_SettingsPages.Register(InputActionSet::c_SectionId, [](EditorContext&, const SettingsSection&, SettingsWindowKind)
{
	return CreateScope<InputActionsPage>();
});
// A simple section with a page of its own: the presets side by side with each row's costs.
m_SettingsPages.Register(std::string(RendererQuality::c_SectionId), [](EditorContext&, const SettingsSection& section, SettingsWindowKind)
{
	return CreateScope<GraphicsQualityPage>(section);
});
```

1. **Lines 222–225:** the External Editor page is registered for its section id, and the factory hands the context to the page.
2. **Lines 235–238:** a simple section registers a page too: the factory passes the section, so the page can read its fields.

`SettingsBrowser` builds its list once for a registry. It lists the project's own pages first, **Game** and **Export**, then the sections of the browser's scope. The sections are grouped by category in the order in which each category first registered. The search field matches in lower case against the title, the category and the titles of the fields, so a search for "rate" finds a section by a field it holds.

The browser makes the page again when the selection changes or the project generation moves. With no project open, the Project Settings page says that project settings belong to a project. A section without a page shows a warning that names `project.setSettings` and `preferences.set` as the way to set it.

### The generic page

The generic page is the code the toy imitates. `SettingsFieldProperty` first turns each field into a `PropertyInfo`, the same description the Inspector uses. `DrawPropertyWidget` then draws it by type: a check box for a `Bool`, a drag or text box for numbers with the field's range, a list for an `Enum`, a picker for an `Asset`. The page draws these properties in a table.

```cpp src="StrataEditor/src/UI/SettingsPages.cpp#L94-L130"
void Draw(EditorPanelContext& context, float width) override
{
	Refresh(context.Context);
	const UI::ThemeColors& colors = UI::GetThemeColors();
	const std::string prefix = fmt::format("{}.{}", SettingsBrowser::GetProbePrefix(m_Kind), m_Section.Id);
	if (!m_Problem.empty())
		Caption(fmt::format("The stored value is not used (its default applies until it is changed): {}", m_Problem), colors.Warning, width);

	std::optional<size_t> edited;
	if (UI::BeginPropertyTable("Fields"))
	{
		for (size_t index = 0; index < m_Section.Fields.size(); index++)
		{
			const std::string probe = fmt::format("{}.{}", prefix, m_Section.Fields[index].Name);
			UI::PropertyLabel(m_Properties[index].DisplayName, m_Properties[index].Tooltip, probe);
			PropertyWidgetOptions options;
			options.ProbeKey = probe;
			ImGui::PushID(static_cast<int>(index));
			const PropertyEditResult result = DrawPropertyWidget(m_Properties[index], m_Values[index], *context.Context.GetActiveScene(), options);
			ImGui::PopID();
			// A drag or a text edit shows its value as it goes and runs the command once, when it ends.
			if (result.Finished)
				edited = index;
		}
		UI::EndPropertyTable();
	}
	if (edited)
	{
		nlohmann::json value = m_Value;
		value[m_Section.Fields[*edited].Name] = UI::PropertyToFieldValue(m_Section.Fields[*edited], m_Properties[*edited], m_Values[*edited]);
		Apply(context, { { "section", m_Section.Id }, { "value", std::move(value) } });
	}

	ImGui::Spacing();
	if (UI::DialogButton(fmt::format("{}.Reset", prefix).c_str(), "Reset to Defaults", false, m_Stored))
		Apply(context, { { "section", m_Section.Id }, { "reset", true } });
}
```

1. **Lines 99–100:** a stored value that the section refuses shows its warning, with the reason kept in `m_Problem`.
2. **Lines 114–116:** only a finished edit counts, so a drag runs no command until its end.
3. **Lines 120–125:** the command gets the whole value: a copy with the one edited field replaced.
4. **Lines 128–129:** **Reset to Defaults** works only when a value is stored.

Search for the line that sets `edited`. A drag or a text edit changes the widget's value on every frame, so the page cannot run a command on every change: that would write an undo step per pixel. The widget reports `Finished` when the drag ends or the text is confirmed, and the page runs one command then.

The refresh half of the page keeps the copies.

```cpp src="StrataEditor/src/UI/SettingsPages.cpp#L132-L169"
void Refresh(const EditorContext& context)
{
	const SectionSource source = ReadSection(context, m_Kind, m_Section.Id);
	if (m_Version && *m_Version == source.Version)
		return;
	m_Version = source.Version;
	m_Stored = source.Stored;
	m_Value = source.Value ? *source.Value : m_Section.GetDefault();
	m_Problem.clear();
	if (source.Stored && !source.Value)
		m_Problem = FindProblem(context);
	m_Values.clear();
	for (size_t index = 0; index < m_Section.Fields.size(); index++)
	{
		const nlohmann::json* member = JsonUtils::Find(m_Value, m_Section.Fields[index].Name);
		m_Values.push_back(UI::FieldToPropertyValue(m_Section.Fields[index], m_Properties[index], member ? *member : m_Section.Fields[index].Default));
	}
}

// Why the stored value is refused (read when the values change, not per frame).
std::string FindProblem(const EditorContext& context) const
{
	if (m_Kind == SettingsWindowKind::Preferences)
		return context.GetPreferences().FindProblem(m_Section.Id).value_or(std::string());
	const nlohmann::json entry = context.GetProject()->GetSettings().GetStoredEntry(m_Section.Id);
	std::string error;
	if (entry.is_object() && entry.contains("Value") && entry.contains("Version") && entry["Version"].is_number_unsigned())
		m_Section.Validate(entry["Value"], entry["Version"].get<uint32_t>(), &error);
	return error;
}

void Apply(EditorPanelContext& context, const nlohmann::json& parameters)
{
	const char* command = m_Kind == SettingsWindowKind::Project ? "project.setSettings" : "preferences.set";
	RunEditorCommand(context.Context, context.Commands, command, parameters);
	// Read again: the value the command applied, or the one that stayed when it refused.
	m_Version.reset();
}
```

1. **Lines 134–136:** the page returns at once while the version it read is still the current one.
2. **Lines 139–142:** a missing value falls back to the default, and the reason is asked only for a stored value that was refused.
3. **Lines 165–168:** the window's kind picks the command, and the reset of `m_Version` makes the next frame read again.

The step that reads again is `m_Version.reset()` in `Apply`. The page does not guess whether the command accepted the edit. It reads again, and the next frame shows the value that applies: the new one when the command accepted the edit, the old one when it refused.

A stored value that the section refuses is a different case. `Refresh` finds it when the file holds a section entry that the validation refuses, so `source.Value` is empty. The page then shows the default and the caption "The stored value is not used (its default applies until it is changed)" with the reason from `FindProblem`, which runs the section's own validation again. That read happens in `Refresh`, so it runs once per version change and not every frame.

A user section has a similar path, and `EditorPreferences` supplies its own reason. The **Reset to Defaults** button runs the same command with `reset` set to true; it is enabled only when a stored value exists.

### The project's own pages

**Game** and **Export** are not sections, so no registry feeds them. The Game page holds the start scene and the loading scene, then the title, the version, the company, the copyright line and the icon. Each field runs its own command: `project.setStartScene` for the start scene, `project.setExportSettings` for the loading scene and `project.setGameInfo` for the text and the icon.

The start scene refuses "none", because a game needs a start scene. The text fields keep what you type until the edit ends. They read the project again when its values changed or when a command refused the text.

The Export page lists the paths that a pruned export always keeps. Each row has a remove button, and a text field adds a path. `project.setExportSettings` checks the path and leaves a refused one in the field.

### Graphics quality

A simple section may register a page. `Renderer.Quality` is simple, yet its page `GraphicsQualityPage` shows the presets side by side. The page starts with five chips for the presets named **Low**, **Medium**, **High**, **Ultra** and **Custom**. A table follows, with a row for each quality row that follows the preset and a column for each preset. The chosen column is highlighted, and you can edit the **Custom** column: under a named preset it shows the values that a switch to Custom would start from.

The cells' tooltips also show the memory of each row at 1920 x 1080 and at 3840 x 2160. They also show the time that the row's stage on the :term[graphics processing unit]{id=gpu} (GPU) takes now in the Scene view. Under the rows, two lines give each column's total memory at 1920 x 1080 and at 3840 x 2160. The rows that the presets leave alone are the players' choices, and they stand below in their own list. Every edit is one `project.setSettings`, so one undo step.

While a running game's players have chosen their own options, or the players' file holds some, a banner says what they set. A "Player" pill marks each row they set, and a button, **Reset Player Options**, runs `graphics.resetPlayerOptions`. What each row does and costs is taught in [Quality settings](../image/quality-settings.md). This page only needs the shape: a table that reads the engine's option model, so a row that another change adds appears here without new interface code.

The drawing below shows the page under the default preset, **High**, with the first five of its 16 rows, as the page's code draws them.

::figure{id=graphics-quality-table}

### Collision layers

`CollisionLayersPage` is for `Scene.CollisionLayers`, a complex section. The page lists the names of the layers, edited in place: a name applies when its field is left or **Enter** is pressed. Below the names stands the matrix of which layers collide.

The matrix shows the first layer, the named layers and the layers that have a pair that does not collide. A project with three named layers therefore does not draw a table of thirty-two rows. Each edit is one `project.setCollisionLayers`. While the project is not ready for edits, the page shows the refusal with its reason. [Collision layers](../physics/collision-layers.md) teaches the table and the filter bits.

The drawing shows the page for a project with three named layers and two pairs that pass through each other.

::figure{id=collision-layers-table}

### Input actions

`InputActionsPage` is for `Input.Actions`, also complex. It lists the maps, then the selected map's actions with their name, kind, :term[dead zone]{id=dead-zone} and bindings as chips. A binding is added from lists of controls, as a composite built part by part, or by pressing the control.

The page marks the actions that the :term[players' bindings]{id=players-bindings} replace with "In play". A button, **Reset Player Bindings**, runs `inputActions.resetPlayerBindings`. Every edit is one `inputActions.setMap` or `inputActions.setAction`. The meaning of maps, kinds and composites is in [Input actions](../input/actions.md); players' rebinding is in [Rebinding](../input/rebinding.md).

The remaining piece is the one that makes "press the control" work.

### Binding capture

Pressing a key to bind it has a trap. The editor reads that same key press for its own work: **Ctrl+Z** undoes, and arrow keys and **Tab** move the focus. If the page only asked which key was pressed, the captured key would also run a shortcut, move the focus or type into a field.

`BindingCapture` is the class that prevents this. Its comment calls it the capture that the editor's user interface (UI) runs. The engine's `InputActions` listens to the devices, and `BindingCapture` keeps ImGui from using the same input.

The calls follow one life. `Begin(owner)` starts listening for an owner, which is an id naming what asked, and ends one that another owner ran. `IsListening(owner)` answers whether that capture still listens, and counts as asking. `Take(owner)` returns the binding text once, after the capture ended. `Cancel(owner)` ends it with no binding.

`BeginFrame()` runs at the start of the editor's UI each frame, before any shortcut or window.

The first rule is key ownership. ImGui lets a caller own a key: while one owns it with the flag `ImGuiInputFlags_LockUntilRelease`, no widget, shortcut or navigation sees it.

```cpp src="StrataEditor/src/UI/BindingCapture.cpp#L41-L47"
// Locks every keyboard and gamepad key for this frame and, for those pressed in the next one, until they are released:
// ImGui updates the locks after it read the next frame's key events and before its navigation reads them.
void HoldKeyboard()
{
	for (int key = ImGuiKey_Keyboard_BEGIN; key < ImGuiKey_Gamepad_END; key++)
		ImGui::SetKeyOwner(static_cast<ImGuiKey>(key), GetOwnerId(), ImGuiInputFlags_LockUntilRelease);
}
```

`HoldKeyboard` marks every keyboard key and gamepad key as owned by the capture. The lock holds for a key pressed in the next frame until its release, because ImGui updates the locks after it reads the next frame's key events and before its navigation reads them. A key that was already down is locked for this frame.

The second rule concerns time and owners.

```cpp src="StrataEditor/src/UI/BindingCapture.cpp#L138-L165"
void BindingCapture::BeginFrame()
{
	if (!s_Capture.Owner.empty())
	{
		// The owner asks every frame it draws: one that skipped a frame is gone (another page, a closed panel).
		const bool abandoned = ImGui::GetFrameCount() - s_Capture.AskedFrame > 1;
		const bool timedOut = ImGui::GetTime() - s_Capture.StartTime >= c_TimeoutSeconds;
		if (abandoned || (timedOut && !s_Capture.Ended && IsOwnCapture() && InputActions::IsCapturing()))
		{
			// Also a binding taken but never collected: nobody will.
			if (!s_Capture.Ended && IsOwnCapture())
				InputActions::CancelCapture();
			ClearCapture();
		}
		else
		{
			Collect();
		}
	}
	if (!s_Capture.KeyboardHeld)
		return;
	if (s_Capture.Owner.empty() && !IsAnyKeyDown())
	{
		s_Capture.KeyboardHeld = false;
		return;
	}
	HoldKeyboard();
}
```

1. **Lines 143–144:** the capture is abandoned when more than one frame passed since its owner asked, and timed out after `c_TimeoutSeconds`.
2. **Lines 145–150:** either case cancels the engine's capture and clears the state.
3. **Lines 152–154:** otherwise `Collect` finds what a finished capture took.
4. **Lines 157–164:** the keyboard stays held while a capture runs and until every key is up.

A capture can end in four ways: the first control pressed, the timeout, **Cancel**, or an owner that stopped asking. The timeout is `c_TimeoutSeconds`, 10 seconds. The owner rule matters more than it looks: the page that asked must call `IsListening` every frame it draws. When the owner skips one frame, because the person selected another page or closed the panel, `BeginFrame` sees that more than one frame passed since the last ask, calls `InputActions::CancelCapture` and clears the state. Without that rule, a capture could keep the keyboard locked for ten seconds under a page nobody sees.

The third rule is about the end. After the capture is over, `KeyboardHeld` stays true and `BeginFrame` keeps calling `HoldKeyboard` until `IsAnyKeyDown` reports that every key is up.

Suppose you hold **Ctrl** and it is the captured control. Releasing the keyboard at that moment would let a following **Z** reach the editor as **Ctrl+Z** and undo something you did not intend. Holding the keyboard until all keys are up prevents that. A captured mouse button gets the same lock in `Collect`, so the press that ended the capture clicks nothing.

Two cases remain. A game's own rebinding menu may begin another capture while the editor plays it. The editor notices that `InputActions::GetCaptureId` is no longer its own id, takes nothing from the other capture and ends its own without a binding. A capture also ends when play starts or stops, and `Take` returns nothing once in that case.

The drawing shows the page while a capture listens for the **Jump** action of the `ThirdPerson` sample.

::figure{id=capture-listening-line}

The page itself, `InputActionsPage::DrawCaptureListening`, draws the line "Press a key, mouse button or gamepad control to bind" with the seconds left and a **Cancel** button. Because the capture also hears the mouse, a click on **Cancel** is itself a press. The page remembers where the button was, and a press inside its rectangle cancels instead of binding the left mouse button.

### External Editor

`ExternalEditorPage` is the page of the user section `Editor.ExternalEditor`, a complex section: its value is a :term[command line]{id=terminal-command}. The page shows the command field with **Apply**, which runs `script.setExternalEditor` and shows the command's refusal under the field. It says which program the command would start, or why it cannot ("Cannot start: ..."). It finds that program again only when the text changed, because the search reads the file system.

The page lists the :term[code editors]{id=code-editor} that it finds on the machine, once per page, and a click puts one into the field. When the :term[environment variable]{id=environment-variable} `STRATA_EXTERNAL_EDITOR` is set, it wins over the setting, and the page says so. [Script builds](../editor/script-builds.md) teaches the same section from the script side.

### The dialog for preferences

The Preferences dialog is a :term[modal]{id=modal} window drawn by `EditorLayer`, so that it works on the launcher, where docked panels are not drawn. It draws a `SettingsBrowser` of kind `Preferences` with the user sections **External Editor**, **Interface** and **Frame Rate**. The last two are simple sections, so the dialog generates their pages.

A change applies at once through `preferences.set`, and **Close** or **Escape** closes the dialog. **Scripts ▸ External Editor...** opens it at the External Editor page. [UI scale](ui-scale.md) teaches the scale that **Interface** sets, and [Status and frame rate](status.md) the idle frame rates of **Frame Rate**.

::figure{id=preferences-interface}

::figure{id=preferences-frame-rate}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A hand-written page for every section | Unity's settings providers draw their own interface | Full control of every page | A page per section, and limits that drift from the data |
| One generated page for every section | Unreal's developer settings and Godot's project settings list declared properties | No user interface code for any section | The layer matrix and the binding lists, which are not flat fields |
| A form from a :term[JSON Schema]{id=json-schema} alone | Form libraries for JSON Schema | Complex sections drawn without a hand-written page | Layout, the matrix and live memory columns: a schema describes data, not a screen |
| A modal window that owns all input during capture | Many games' rebinding menus | A simpler capture with no key ownership | A frozen editor: play could not stay paused and visible while you bind |

## How it is tested

The suites sit in `StrataTests/src/Editor/EditorSettingsUITests.cpp`. The Graphics Quality page has its own file, `StrataTests/src/Editor/EditorGraphicsQualityPageTests.cpp`.

The suite `Editor.UI.ProjectSettings` opens the panel from the menu and checks that the Game and Export pages run their commands. It edits a generated field and checks that `project.setSettings` runs with the whole value, as one undo step, and that a drag moves a float by the field's drag speed. It also holds the test that every registered section has a page.

The suite `Editor.UI.Preferences` opens the dialog from the launcher and from a project, and opens it at the External Editor page. It checks that a command typed but never applied is gone when the dialog opens again.

The suite `Editor.UI.InputActions` drives capture. The next key binds, and keys pressed during a capture run no shortcut. **Cancel** and the timeout end a capture, and a capture that a game starts replaces the page's. A mouse press that a capture took clicks nothing, and a paused game still captures.

The harness draws frames with a set clock and clicks items by their probe keys. A probe key is a name, such as `ProjectSettings.Test.Simple.Enabled`, that the interface records for an item. Run one suite directly with `build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.UI.InputActions`.

## Changing it safely

To add a settings section, register it in its module's registration function with an id, a title, a category, a scope, a version and its fields. The page then appears in the window of its scope with no interface code. The feature test and the check that every registered section has a page keep it honest.

To write a custom page, derive from `SettingsPage` and register a factory with `EditorSettingsPageRegistry::Register` in `EditorLayer`. Then keep the contract. Draw from copies that you refresh by version, and run commands with the UI origin. Show a refusal with its reason. Read the file system only in a refresh step, never per frame.

:::rule
Panels never write, move or remove files, and UI code never walks the scene or the asset folder per frame. A page reads only the values that the settings registry and the project's settings give, and it caches what it formats.
:::

Three checks fail first when you break the contract. The test of the whole value catches a page that sends only the changed field: the section would reset the others to their defaults. The capture suite catches a page that forgets to call `IsListening`. The probe-key checks catch a renamed key, so keep the names stable: tests and agents find items by them.

## Summary

- The registry's sections, the page registry and the browser make a window: the browser lists sections by category and draws a page from the registry or the generated one.
- A simple section is drawn from its fields, and a complex section, or one that asks, gets a page registered by its id.
- An edit runs one command when it finishes, and the page reads again when the version changes and not every frame.
- :term[Binding capture]{id=binding-capture} owns every key, ends on a control, **Cancel**, a 10 second timeout or an owner that stopped asking, and holds the keyboard until all keys are up.
- A stored value that the section refuses is not used: the page shows the default and the reason until an edit replaces it.

## Check yourself

1. A module registers a complex section and the editor registers no page for it. What does the Project Settings window show for that section?
   - A. A generated page with no fields.
   - B. The section in the list, and a warning in place of the page.
   - C. A crash when the section is selected.
   - D. Nothing: the list omits the section.

   :::answer{tests="map,choose"}
   B. The browser lists every section of its scope, and `DrawPage` shows a warning that names `project.setSettings` and `preferences.set`. A and C are wrong: a complex section has no fields to draw, and the code returns null and handles it. D is wrong: the entry comes from the registry, not from the registered pages. The test that every registered section has a page keeps this state from shipping.
   :::

2. A page like the toy's draws five frames. In frame 2 an edit sets Volume to 0.3, which is in range. In frame 4 an edit sets Pitch to 5, and the range ends at 2. How often does the page read the store?

   :::answer{tests="trace-edit"}
   Twice. Frame 1 reads because the page has no version yet. The edit of frame 2 succeeds, the version grows and the page resets its own, so frame 3 reads again. The edit of frame 4 is refused, so the two versions agree, and frame 5 reads nothing.
   :::

3. You press and hold **Ctrl** while a capture listens, so the capture takes **Ctrl**. You keep it down and press **Z**. Why does nothing undo?

   :::answer{tests="capture-rules"}
   `BeginFrame` keeps the keyboard locked after the capture ended, until `IsAnyKeyDown` finds every key up. While **Ctrl** is still down, the capture owns **Z**, so no shortcut sees it. Without the rule, the capture would end at the first control and **Ctrl+Z** would reach the editor.
   :::

4. Which command does an edit on the generated Frame Rate page run, and with which origin?

   :::answer{tests="map"}
   `preferences.set`, with `CommandOrigin { CommandSource::UI }`. A project section runs `project.setSettings`. The page picks the command from the window's kind.
   :::

5. The project file holds a value for a simple section that its validation refuses. What does the generated page show?
   - A. The stored value, with a mark on the bad field.
   - B. The default values and a warning with the reason.
   - C. An empty page.
   - D. The last valid value from the :term[undo stack]{id=undo-stack}.

   :::answer{tests="refused-value"}
   B. `Refresh` finds no usable value for a stored section, takes the defaults and asks the section's validation for the reason. A is wrong: the page never uses the refused value. C is wrong: the fields still draw. D is wrong: the undo stack plays no part in reading.
   :::

## Exercises

1. **Basic.** A section's validation reports the first bad field in the order of its fields. Write a small program with three fields, where the first and the second are out of range, and print the reason for each of three states: both bad, only the second bad, none bad.

   :::answer[Worked solution]{solution="sketches/editor-ui-settings-windows-first-bad.cpp" tests="refused-value"}
   The function loops over the fields in order and returns at the first one outside its range, so the second field's problem stays hidden until the first is fixed. Fixing `Rate` moves the reason to `Steps`; fixing both returns an empty string.

   ```cpp sketch="editor-ui-settings-windows-first-bad.cpp"
   // Exercise: a section's validation reports the first bad field in the order of its fields.
   #include <cstdio>
   #include <string>
   #include <vector>

   struct Field
   {
   	std::string Name;
   	float Min;
   	float Max;
   	float Value;
   };

   std::string FindProblem(const std::vector<Field>& fields)
   {
   	for (const Field& field : fields)
   	{
   		if (field.Value < field.Min || field.Value > field.Max)
   			return field.Name + " must be from " + std::to_string(static_cast<int>(field.Min)) + " to " + std::to_string(static_cast<int>(field.Max));
   	}
   	return std::string();
   }

   int main()
   {
   	std::vector<Field> fields = { { "Rate", 1.0f, 240.0f, 500.0f }, { "Steps", 1.0f, 8.0f, 20.0f }, { "Scale", 0.0f, 1.0f, 0.5f } };
   	std::printf("1: %s\n", FindProblem(fields).c_str());
   	fields[0].Value = 60.0f;
   	std::printf("2: %s\n", FindProblem(fields).c_str());
   	fields[1].Value = 4.0f;
   	std::printf("3: [%s]\n", FindProblem(fields).c_str());
   	return 0;
   }
   ```

   ```text output-of="editor-ui-settings-windows-first-bad.cpp"
   1: Rate must be from 1 to 240
   2: Steps must be from 1 to 8
   3: []
   ```

   1. **Lines 16–21:** the loop returns at the first field outside its range, so a later problem waits until the earlier one is fixed.
   2. **Lines 26–31:** the three states: Rate fixed, then Steps fixed, with the output above for each.
   :::

2. **Medium.** Trace it yourself: find where a drag on a generated field becomes a command, and where the page reads the new value again.

   :::answer[Worked solution]{tests="trace-edit"}
   The file is `StrataEditor/src/UI/SettingsPages.cpp`. In `GenericSettingsPage::Draw`, `DrawPropertyWidget` returns a result whose `Finished` is true when the drag ends, and the page calls `Apply`. `Apply` runs `RunEditorCommand` with `project.setSettings` or `preferences.set` and then resets `m_Version`, so the next `Draw` calls `Refresh`. Put a breakpoint in `Apply`: during the drag it never hits, and it hits once when you release the mouse button.
   :::

3. **Hard.** The project file holds a value for `Scene.Timing` that the section refuses, for example a fixed rate that is not one of the options. Predict what the Timing page shows and what **Reset to Defaults** does, then check in the editor.

   :::answer[Worked solution]{tests="refused-value,choose"}
   `ReadSection` returns no value but reports the section as stored, so `Refresh` takes the default value for the fields and asks `FindProblem` for the reason. The fields show the defaults, and a warning line reads "The stored value is not used (its default applies until it is changed)" followed by the validation message. **Reset to Defaults** is enabled because a stored entry exists; it runs `project.setSettings` with `reset` true, which removes the entry, and the warning goes. Editing one field instead sends a whole valid value made from the defaults and that edit, which replaces the refused entry too.
   :::

## Where it lives in Strata

- The page interface, registry, browser and generic page: `StrataEditor/src/UI/SettingsPages.h` and `StrataEditor/src/UI/SettingsPages.cpp`.
- Fields as properties: `StrataEditor/src/UI/SettingsFieldProperty.cpp`; the widget: `DrawPropertyWidget` in `StrataEditor/src/UI/PropertyWidgets.cpp`.
- The windows: `StrataEditor/src/Panels/ProjectSettingsPanel.cpp` and `StrataEditor/src/UI/PreferencesDialog.cpp`.
- The custom pages: `StrataEditor/src/UI/GraphicsQualityPage.cpp`, `StrataEditor/src/UI/CollisionLayersPage.cpp`, `StrataEditor/src/UI/InputActionsPage.cpp` and `ExternalEditorPage` in `StrataEditor/src/UI/ScriptDialogs.cpp`; their registration in `EditorLayer`.
- Binding capture: `StrataEditor/src/UI/BindingCapture.cpp`.
- Tests: the suites `Editor.UI.ProjectSettings`, `Editor.UI.Preferences`, `Editor.UI.InputActions` and `Editor.UI.GraphicsQuality`.
- Commands: `project.setSettings`, `preferences.set`, `project.setGameInfo`, `script.setExternalEditor`.
- Menus: **File ▸ Project Settings...**, **File ▸ Preferences...**, **Scripts ▸ External Editor...**.

## Further reading

- Dear ImGui, the comments of `imgui.h` on key ownership and `SetKeyOwner` (advanced): what the lock flags promise.
- Unity Manual, "Settings Providers" (intermediate): a hand-written settings page in another editor.
- Godot documentation, "ProjectSettings" (intermediate): settings declared with property information and listed from it.
- Unreal Engine documentation, "Developer Settings" (intermediate): a settings class whose properties become a page.
- JSON Schema, the specification (advanced): the description from which forms can be generated.
