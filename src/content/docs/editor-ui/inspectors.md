---
id: editor-ui/inspectors
title: "Inspectors from reflection"
description: "How one generic panel edits every component from its property list, how it handles several entities at once, and how the Asset tab edits assets."
kind: internals
size: XL
tracks: [E]
needs: [editor-ui/shell, editor/prefab-instances, world/reflection]
time: 110
learn:
  - id: generic
    text: explain how one panel draws and edits every component from its property list
  - id: multi
    text: predict what a drag writes when several entities with different values are selected
  - id: undo
    text: trace how a drag becomes one undo step and where the merge ends
  - id: drawer
    text: write a property drawer and register it for one property
  - id: inactive
    text: add an inactive reason to a property and predict what the Inspector shows
since: 0.3.0
status: final
---

Strata has dozens of component types and hundreds of properties, and the Inspector edits all of them. A single panel reads each component's property list and builds the rows from it, for one selected entity or for thirty. Nobody wrote a screen for the light, one for the camera and one for the rigid body. This page is about that panel (`InspectorPanel`), the functions that draw one value (`DrawPropertyWidget`), the helpers that turn an edit into an :term[undo step]{id=undo-step}, and the Asset tab, which edits assets with the same parts. It does not cover how a property is registered ([Reflection](../world/reflection.md)), how undo steps are stored ([Undo and redo](../editor/undo.md)) or how overrides are kept exact ([Prefab instances](../editor/prefab-instances.md)).

## The problem and how engines solve it

Count the work. A camera has about a dozen properties, a light about ten, and a post-process component has dozens. If each needed its own drawing code, every new property would mean editing a screen, and every screen would drift from the others. One screen would show a slider that clamps, the next a field that does not, and a third would forget to record undo.

Engines answer in three ways, and most use all three together.

- **One generic inspector driven by metadata.** The engine keeps a description of each type's fields (their names, types, limits and help text), and one piece of code draws a widget for each field type. This is cheap to extend: a new field appears the moment it is registered. Its cost is that the layout is the same for everything.
- **Hand-written editors per type.** A programmer writes the screen for one component. The result can be as good as the type deserves, such as an anchor grid for a layout rectangle. The cost is code that must change with the type, and that nobody updates when there are hundreds of components.
- **Custom drawers as escape hatches.** The generic panel stays in charge, and a registered drawer takes over one property, or one whole component, where the generic widget is not enough.

:::elsewhere
Unity's `CustomEditor` replaces the whole inspector of a type, and its `PropertyDrawer` replaces one field (Unity Manual, "Custom Editors"). Unreal's detail panel is generic, with `IDetailCustomization` for whole classes and `IPropertyTypeCustomization` for one property type (Unreal Engine documentation, the page on the details panel). Godot offers `EditorInspectorPlugin`, which adds or replaces rows for matching objects (Godot documentation, the class reference of `EditorInspectorPlugin`). All three have the same shape: generic by default, hooks for the exceptions.
:::

How an engine learns the fields in the first place is a separate question: generated code, :term[macros]{id=macro}, or a run-time registration. [Reflection](../world/reflection.md) compares them and shows Strata's choice. Here the descriptions already exist, and the question is what a panel does with them.

Strata takes the first and third ways. The Inspector is generic, a component drawer and a property drawer are the escape hatches, and there is exactly one hand-written editor of the second kind, for the user interface (UI) rectangle. The choice has a price. A property that needs a richer editor than a number box must have a drawer written, and until then it looks plain. The reward is that the Inspector, the commands an agent sends and a scene file all agree on what a property is.

## The map

The pipeline has one direction. The registry holds a description of each component. The Inspector groups the properties of that description by section once per type, then draws each row. A row draws its label, then either a property drawer or the generic widget. Whatever the person changes goes to an undo helper, and the :term[undo stack]{id=undo-stack} merges the steps of one drag.

```mermaid caption="From the registry to the undo stack: the property list becomes groups once, each row draws a label and a value, and a drag becomes one undo step." alt="A flow from the component registry through the property list and the groups to a row. The row draws a label, then a property drawer or the generic widget. Both lead to an undo helper and the undo stack."
flowchart LR
	R[ComponentRegistry] --> P[ComponentInfo::Properties]
	P --> G[GetPropertyGroups: once per type]
	G --> Row[DrawPropertyRow]
	Row --> L[PropertyLabel: mark and reason]
	Row --> D{drawer?}
	D -->|yes| PD[property drawer]
	D -->|no| W[DrawPropertyWidget]
	PD --> U[SetPropertyWithUndo and others]
	W --> U
	U --> S[undo stack: merge until the edit ends]
```

Four files hold the parts, and each owns one thing.

| File | Owns |
| --- | --- |
| `StrataEditor/src/Panels/InspectorPanel.cpp` | The panel: selection, top block, prefab bar, component sections, groups and rows |
| `StrataEditor/src/UI/PropertyWidgets.cpp` | One widget per property type, the property table and the label |
| `StrataEditor/src/Editor/PropertyEdit.cpp` | Shared values across entities and the edits that write them with undo |
| `StrataEditor/src/UI/ComponentDrawers.cpp` | The registries of component drawers and property drawers |

All of this runs on the :term[main thread]{id=main-thread}, in the frame's UI pass. The panel keeps no copy of the scene: every frame it reads the selected entities and draws what it finds. The only state it keeps is a cache of groups per type, a few caches for prefab overrides and the edit of a rotation that is in progress.

## The contract

The panel and the code around it follow a few rules, each with a reason.

1. **Every edit goes through an undo helper.** The panel never writes a component field. It calls `SetPropertyWithUndo` or one of its siblings, which record a step in a `SceneEditTransaction`. The reason is that an edit that skips the helper cannot be undone, is not marked in the scene's saved state, and does not signal the scene's caches that a transform or a name changed.
2. **A drag is one step.** Consecutive edits of the same property merge into one undo step until the code calls `UndoStack::BreakMerge`. The panel calls it when the widget reports that the edit finished.
3. **Prefab commands run after drawing.** A button that applies or reverts a prefab change does not run its command in the middle of the frame. It stores the command with `SchedulePrefabCommand`, and the panel runs it after the last row is drawn. The reason: the command rebuilds entities and their overrides, and rows still waiting to be drawn would read a scene that changed under them.
4. **A property that another property can switch off gets an inactive reason.** The row is drawn disabled and its tooltip says why. The registration of the reason belongs to [Reflection](../world/reflection.md); the Inspector only shows it.
5. **A multi-selection writes only what changed.** If thirty lights are selected and the person drags one axis of a vector, only that axis is written. The other axes of each entity stay as they were.
6. **The panel shows only components that every selected entity has.** Components that only some have are omitted, and a line under the sections says so.

:::rule
The engine's guide says that every change of the scene or project goes through a command, or through the undo helpers for edits that continue over many frames. The reason is that one path then gives undo, the activity journal and agents the same view of the change. Details: [Undo and redo](../editor/undo.md).
:::

Rule 3 is the least obvious, so here is the failure it prevents. Say the Overrides menu runs `prefab.revert` the moment it is clicked, while the properties of the same component are still being drawn. The revert recreates the instance. The loop over rows then holds an entity that no longer exists, and the next row reads a component of nothing. By storing the command and running it after the loop, the panel makes the order of one frame simple: draw from a scene that does not change, then change it once.

## A toy version

The toy below keeps the core of the idea in 87 lines: a light has three fields, and a list of property descriptions is the only knowledge the drawing code has. A description holds a name, a function that reads, a function that sets and an optional :term[inactive reason]{id=inactive-reason}. One function draws a row for any property of any list of lights, and one function edits and merges drag frames into one undo step. The program draws two lights that differ in softness, simulates a three-frame drag of the intensity, ends the drag and switches shadows off. Notice that `DrawRow` never mentions `Intensity` or `Softness`, and that a row is disabled only when its reason holds for every light.

```cpp sketch="editor-ui-inspectors-toy.cpp"
// A toy generic inspector: one list of property descriptions draws and edits every light, with mixed values,
// an inactive reason and one undo step per drag.
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

struct Light
{
	bool CastShadows = true;
	float Intensity = 1.0f;
	float Softness = 0.5f;
};

struct Property
{
	std::string Name;
	std::function<float(const Light&)> Get;
	std::function<void(Light&, float)> Set;
	std::function<std::string(const Light&)> InactiveReason; // empty function: always active
};

struct UndoStep
{
	size_t Property = 0;
	std::vector<float> Before;
	float After = 0.0f;
};

static const std::vector<Property> s_Properties = {
	{ "Cast Shadows", [](const Light& light) { return light.CastShadows ? 1.0f : 0.0f; }, [](Light& light, float value) { light.CastShadows = value != 0.0f; }, {} },
	{ "Intensity", [](const Light& light) { return light.Intensity; }, [](Light& light, float value) { light.Intensity = value; }, {} },
	{ "Softness", [](const Light& light) { return light.Softness; }, [](Light& light, float value) { light.Softness = value; },
		[](const Light& light) { return light.CastShadows ? std::string() : std::string("Cast Shadows is off"); } },
};

static std::vector<UndoStep> s_Undo;
static bool s_MergeOpen = false;

static void DrawRow(const std::vector<Light>& lights, size_t index)
{
	const Property& property = s_Properties[index];
	bool mixed = false;
	std::string reason;
	for (const Light& light : lights)
	{
		mixed = mixed || property.Get(light) != property.Get(lights.front());
		std::string own = property.InactiveReason ? property.InactiveReason(light) : std::string();
		if (own.empty())
			reason.clear(); // active on one entity: the row stays active
		else if (&light == &lights.front() || !reason.empty())
			reason = own;
	}
	std::printf("%-13s %s%s\n", property.Name.c_str(), mixed ? "--" : std::to_string(property.Get(lights.front())).substr(0, 4).c_str(),
		reason.empty() ? "" : ("   (disabled: " + reason + ")").c_str());
}

static void Edit(std::vector<Light>& lights, size_t index, float value)
{
	if (!s_MergeOpen || s_Undo.empty() || s_Undo.back().Property != index)
	{
		UndoStep step;
		step.Property = index;
		for (const Light& light : lights)
			step.Before.push_back(s_Properties[index].Get(light));
		s_Undo.push_back(step);
		s_MergeOpen = true;
	}
	s_Undo.back().After = value; // a merged edit keeps its first "before" and updates its last value
	for (Light& light : lights)
		s_Properties[index].Set(light, value);
}

int main()
{
	std::vector<Light> lights(2);
	lights[1].Softness = 0.9f;
	for (size_t index = 0; index < s_Properties.size(); index++)
		DrawRow(lights, index);
	for (const float value : { 2.0f, 3.0f, 4.0f })
		Edit(lights, 1, value); // three frames of one drag
	s_MergeOpen = false;        // the drag ends: the next edit starts a new step
	std::printf("undo steps after the drag: %zu\n", s_Undo.size());
	Edit(lights, 0, 0.0f);
	for (size_t index = 0; index < s_Properties.size(); index++)
		DrawRow(lights, index);
}
```

```text output-of="editor-ui-inspectors-toy.cpp"
Cast Shadows  1.00
Intensity     1.00
Softness      --
undo steps after the drag: 1
Cast Shadows  0.00
Intensity     4.00
Softness      --   (disabled: Cast Shadows is off)
```

1. **Line 15:** a description holds all the drawing code knows of a property: its name, how to read it, how to set it and when it is inactive.
2. **Line 47:** a row is mixed when any light differs from the first.
3. **Line 50:** one light without a reason makes the row active, as in the real panel.
4. **Lines 58-69:** an edit opens a step when no merge is open and keeps the first before values; later frames update only the last value.
5. **Line 82:** ending the drag closes the merge, so the next edit starts a new step.

The toy shows four things the real code also does. The softness shows as "--" because the two lights differ. After three frames of dragging there is one undo step, because the merge stayed open until the drag ended. The softness row becomes disabled only once both lights have shadows off, and no line of the drawing code names a property.

The toy differs from the real code in two ways. A value has one number type in the toy, and Strata has a variant of several kinds, so a widget must be chosen by type. The toy also writes straight into the lights, where Strata writes through a transaction so that undo can restore each entity.

## The real code: groups and rows

### Groups, made once per type

Properties carry a section name, a short text such as "Shadows" that groups related rows. A **section** is a heading in a component's list of properties that gathers the rows with the same section name. The panel needs the groups on every frame, but the list of a type never changes after startup, so it builds the groups once per type and keeps them.

The function below walks the properties in registration order. The first group has an empty name and holds the properties without a section. Each new section name opens a group, and each property joins the group of its name.

```cpp src="StrataEditor/src/Panels/InspectorPanel.cpp#L925-L943"
const std::vector<InspectorPanel::PropertyGroup>& InspectorPanel::GetPropertyGroups(const ComponentInfo& info)
{
	if (const auto it = m_PropertyGroups.find(&info); it != m_PropertyGroups.end())
		return it->second;
	std::vector<PropertyGroup> groups;
	groups.push_back({});
	for (size_t index = 0; index < info.Properties.size(); index++)
	{
		const std::string& section = info.Properties[index].Section;
		auto group = std::find_if(groups.begin(), groups.end(), [&section](const PropertyGroup& candidate) { return candidate.Section == section; });
		if (group == groups.end())
		{
			groups.push_back({ section, fmt::format("Inspector.{}.Section.{}", info.Name, section), {} });
			group = std::prev(groups.end());
		}
		group->Properties.push_back(index);
	}
	return m_PropertyGroups.emplace(&info, std::move(groups)).first->second;
}
```

1. **Line 925:** the groups of a type are found by the address of its `ComponentInfo`, which stays the same while the registry holds it.
2. **Line 930:** the first group, with an empty name, holds the properties with no section; it draws without a heading.
3. **Lines 934-938:** a section is found by name in a short list, and a new one is created at the end, so groups follow the order of first appearance.
4. **Line 942:** the result is stored and returned by reference. Nothing is rebuilt on the next frame.

`DrawProperties` then visits each group. It skips hidden and transient properties and those a component drawer already drew, and it skips a group with no row to draw, heading included. It draws a heading for a named section, and puts the rows in a **property table**: the two-column layout of the Inspector, with the label on the left and the editing widget on the right. Every table of the window has the same identifier, so :term[ImGui]{id=dear-imgui} treats them as one table. The line the person drags between the columns then moves in all of them, and ImGui keeps its place in the layout file.

### One row

`DrawPropertyRow` draws one property for all selected entities. It first asks for the shared value, then draws the label, then either hands the row to a property drawer or draws the generic widget.

```cpp src="StrataEditor/src/Panels/InspectorPanel.cpp#L990-L1011"
const std::optional<SharedPropertyValue> shared = GetSharedProperty(entities, info, property);
if (!shared)
	return;

const std::string probe = fmt::format("Inspector.{}.{}", info.Name, property.Name);
const std::string inactive = GetSharedInactiveReason(entities, info, property);
UI::PropertyLabelOptions labelOptions;
labelOptions.Overridden = prefab && prefab->IsOverridden(info.Name, property.Name);
labelOptions.InactiveReason = inactive;
UI::PropertyLabel(property.DisplayName, property.Tooltip, probe, labelOptions);
if (labelOptions.Overridden)
{
	const std::string_view name = property.Name;
	DrawPropertyOverrideMenu(*prefab, info, std::span(&name, 1), probe);
}
// A row whose edit means more than setting the property draws its own value.
if (const UI::PropertyDrawer* drawer = UI::PropertyDrawers::Find(info.TypeId, property.Name))
{
	const UI::PropertyDrawContext row { commands, entities, info, property, shared->Value, shared->Mixed, property.IsReadOnly() || !inactive.empty(), probe };
	(*drawer)(context, row);
	return;
}
```

1. **Line 990:** `GetSharedProperty` returns the first entity's value, a flag saying whether another entity differs, and which components of a vector differ. It returns nothing, and the row is skipped, when an entity lacks the component.
2. **Lines 995-998:** the label gets two facts: whether the property is an override in a prefab instance, and the inactive reason shared by the selection.
3. **Line 1006:** a property drawer registered for this component type and property name takes the whole value cell.
4. **Line 1008:** the drawer receives everything it needs in one context, including whether the row must be drawn disabled.

The label is more than text. `PropertyLabel` draws the display name and puts the property's tooltip on it. A name wider than its column ends in an ellipsis and the full name appears in the tooltip. An overridden property gets a bold label and a bar of the accent color at the row's left edge. An inactive property gets the disabled color, and the reason becomes part of the tooltip.

::figure{id=inactive-property}

::figure{id=inactive-property crop=lookup}

One property can also switch off a whole group of rows, as a camera's projection mode does.

::figure{id=camera-orthographic}

### Mixed values

Select three lights with intensities 2, 5 and 5. The row cannot show one number. A **mixed value** is a property that differs among the selected entities; the Inspector shows it as "--".

::figure{id=mixed-values}

`GetSharedProperty` computes this. It takes the first entity's value as the one to show, compares every other entity's value to it, and sets a flag at the first difference. For vectors and colors it also records which components differ, so that the row can mark only the X field as mixed when only X differs. For rotations it compares Euler angles, which are the angles the widget shows, and not the quaternions (the four numbers that store a rotation; see [Rotations](../basics/math-rotations.md)).

The inactive reason has a similar rule for several entities, shown below. A multi-selection shows a property as inactive only when it is inactive on every entity. If one light has shadows on, its softness matters, and disabling the row would block a useful edit.

```cpp src="StrataEditor/src/Editor/PropertyEdit.cpp#L157-L170"
std::string GetSharedInactiveReason(std::span<const Entity> entities, const ComponentInfo& component, const PropertyInfo& property)
{
	if (!property.InactiveReason || entities.empty())
		return {};
	std::string first;
	for (const Entity entity : entities)
	{
		std::string reason = ComponentAccess::GetInactiveReason(entity, component, property);
		if (reason.empty())
			return {};
		if (first.empty())
			first = std::move(reason);
	}
	return first;
```

1. **Lines 159-160:** a property without a reason function is always active, and an empty selection has no reason.
2. **Lines 164-166:** the first active entity ends the search with an empty result, which means active.
3. **Lines 167-168:** the text of the first reason is kept and returned if no entity was active.

### Writes of only the changed axes

Now the edit. The widget changes a copy of the value, `value`, and reports the result. Three kinds of write follow from what is selected and what changed.

```cpp src="StrataEditor/src/Panels/InspectorPanel.cpp#L1019-L1044"
ImGui::BeginDisabled(property.IsReadOnly() || !inactive.empty());
const PropertyEditResult result = DrawPropertyWidget(property, value, scene, options);
ImGui::EndDisabled();
if (result.Changed)
{
	// Several entities: the components (axes) the edit changed are written, each entity keeps its own others.
	std::string error;
	const bool partial = std::any_of(result.ChangedComponents.begin(), result.ChangedComponents.end(), [](bool changed) { return changed; });
	bool set = false;
	if (entities.size() == 1)
		set = SetPropertyWithUndo(context, entities.front(), info, property, value, &error);
	else if (partial && property.Type == PropertyType::Quat)
		set = UpdateRotationEdit(context, entities, info, property, result, &error);
	else if (partial)
		set = SetPropertyComponentsWithUndo(context, entities, info, property, value, result.ChangedComponents, &error);
	else
		set = SetPropertyWithUndo(context, entities, info, property, shared->Value, value, &error);
	if (!set)
		ST_WARN("{}.{}: {}", info.Name, property.Name, error);
}
if (result.Finished)
{
	context.GetUndoStack().BreakMerge();
	// The next edit reads the entities' angles again, as the fields show them then.
	m_RotationEdit.reset();
}
```

1. **Line 1019:** the widget is drawn inside a disabled scope when the property is read-only or inactive, so the person cannot change what has no effect.
2. **Line 1028:** with one entity the edit is a plain `SetPropertyWithUndo`.
3. **Lines 1030-1033:** with several entities and an edit that changed only some components, rotations go through the rotation edit. Other vectors go through `SetPropertyComponentsWithUndo`, which writes the changed components and keeps each entity's other ones.
4. **Lines 1039-1043:** when the widget says the edit finished, the merge is broken and the rotation edit forgets its angles.

Take the sketch below, which does what `SetPropertyComponentsWithUndo` does for one vector. Three entities share a position row, with positions (1, 5, 0), (2, 5, 0) and (3, 7, 0), and the row shows the first one's value. The person types 4 in X, so each entity keeps its own Y. The first block of output is the result of that edit, and the second shows what happens when the person then types 9 in Y.

```cpp sketch="editor-ui-inspectors-axes.cpp"
// Writing only the axes an edit changed: three entities share one Position row.
#include <array>
#include <cstdio>
#include <vector>

using Vec3 = std::array<float, 3>;

static void Write(std::vector<Vec3>& positions, const Vec3 shown, const Vec3& edited)
{
	for (Vec3& position : positions)
	{
		for (size_t axis = 0; axis < 3; axis++)
		{
			if (shown[axis] != edited[axis])
				position[axis] = edited[axis]; // only an axis the edit changed
		}
	}
}

static void Print(const std::vector<Vec3>& positions)
{
	for (const Vec3& position : positions)
		std::printf("(%g, %g, %g)\n", position[0], position[1], position[2]);
}

int main()
{
	std::vector<Vec3> positions = { { 1.0f, 5.0f, 0.0f }, { 2.0f, 5.0f, 0.0f }, { 3.0f, 7.0f, 0.0f } };
	// The row shows the first entity's value; Y and X differ among the three, Z does not.
	const Vec3 shown = positions.front();
	Write(positions, shown, { 4.0f, 5.0f, 0.0f }); // the person types 4 in X
	Print(positions);
	std::printf("--\n");
	Write(positions, positions.front(), { 4.0f, 9.0f, 0.0f }); // then types 9 in Y
	Print(positions);
}
```

```text output-of="editor-ui-inspectors-axes.cpp"
(4, 5, 0)
(4, 5, 0)
(4, 7, 0)
--
(4, 9, 0)
(4, 9, 0)
(4, 9, 0)
```

1. **Lines 8-15:** an axis is written only where the value shown and the value edited differ. `shown` is a copy, because the first entity's value changes during the loop, and a reference to it would hide the edit from the others.
2. **Line 31:** the first edit changes X alone, so each entity keeps its own Y.
3. **Line 34:** the second edit starts from what the row shows now, and Y differs there, so every entity gets the new Y.

After the first edit the three positions are (4, 5, 0), (4, 5, 0) and (4, 7, 0): X was replaced everywhere, and the third entity kept its Y of 7. After the second edit every Y is 9. Writing whole vectors would have given all three entities the first entity's Y of 5 on the first edit, and destroyed the 7. The partial write is the reason a multi-selection can be edited safely at all.

One more case: clicking an axis label (the colored X, Y or Z beside a field) resets that axis to the component's default. For a mixed row the shown value may already equal the default on that axis, so comparing before and after would find no change. The widget therefore reports which components the click touched, in `ChangedComponents`, and the write uses that list.

### Rotations and the angles the widget showed

A rotation is stored as a quaternion but shown as three Euler angles (pitch, :term[yaw]{id=yaw-angle}, roll, in degrees). Reading the angles back from the quaternion after each drag frame gives wrong results for two reasons. A rotation has two sets of angles with yaw between -90 and 90 and others outside it, so dragging yaw past 90 degrees would fold back. At a yaw of exactly 90 degrees, only the difference of pitch and roll matters, so a drag through 90 would lose them.

`RotationAnglesEdit` avoids the read-back. It starts when the first frame of a drag arrives, with the angles the widget showed before the edit. It reads each entity's own angles once, and every later frame it replaces only the edited angles in those stored values and builds the rotations from them. It continues while the entities still hold the rotations it gave them last; after an undo or a command it starts again from what the fields show.

### The merge, ended

The last lines of `DrawPropertyRow` :term[break the merge]{id=break-the-merge} when the widget says `Finished`. Each widget decides this by its kind. A drag field, a text box and a :term[color channel]{id=color-channel} are continuous: `Finished` becomes true on the frame the control is released after an edit. A check box, a drop-down or a picker is discrete: the click is the whole edit, so `DrawPropertyWidget` sets `Finished` on the same frame as `Changed`.

## From type to widget

`DrawPropertyWidget` is a `switch` on `PropertyType`. The panel, the material editor and the :term[import settings]{id=import-settings} all call it, so every place that edits a property looks the same. The :term[unsigned integer]{id=unsigned-integer} case shows how a general widget takes special cases from the property's flags.

```cpp src="StrataEditor/src/UI/PropertyWidgets.cpp#L921-L954"
case PropertyType::UInt:
{
	uint32_t& number = std::get<uint32_t>(value);
	if (HasFlag(property.Flags, PropertyFlags::PowerOfTwoLimit))
	{
		result = DrawPowerOfTwoLimit(property, number, options);
		break;
	}
	if (HasFlag(property.Flags, PropertyFlags::PhysicsLayer))
	{
		result = DrawPhysicsLayer(number, scene, options);
		break;
	}
	const uint32_t min = property.HasRange() ? static_cast<uint32_t>(std::max(property.Min, 0.0f)) : 0u;
	const uint32_t max = property.HasRange() ? static_cast<uint32_t>(property.Max) : std::numeric_limits<uint32_t>::max();
	// A format without a conversion shows as it is; ImGui types and parses the number with its own format then.
	std::string zeroLabel;
	if (number == 0 && !options.Mixed)
	{
		for (const char character : options.ZeroLabel)
			zeroLabel += character == '%' ? std::string("%%") : std::string(1, character);
	}
	ImGui::SetNextItemWidth(-FLT_MIN);
	result.Changed = ImGui::DragScalar("##Value", ImGuiDataType_U32, &number, GetSpeed(property, 0.2f), &min, &max,
		options.Mixed ? c_MixedText : (zeroLabel.empty() ? "%u" : zeroLabel.c_str()));
	result.Finished = ImGui::IsItemDeactivatedAfterEdit();
	if (!options.ProbeKey.empty())
	{
		const std::string shown = options.Mixed ? std::string(c_MixedText) : (zeroLabel.empty() ? std::to_string(number) : std::string(options.ZeroLabel));
		UI::ItemProbe::Record(options.ProbeKey, true, 0, shown);
	}
	continuous = true;
	break;
}
```

1. **Line 924:** a property flagged `PowerOfTwoLimit` is drawn as a list of sizes (a capacity of 1024 or 2048) and not as a free number.
2. **Line 929:** a property flagged `PhysicsLayer` is drawn as a list of the project's collision layer names.
3. **Lines 937-942:** a zero can carry a label such as "Auto", for capacities the engine sizes itself; a percent sign in the label is escaped so that ImGui does not read it as a format.
4. **Line 946:** the drag field reports `Finished` when ImGui says the item was released after an edit.

The other types follow the same pattern. A check box handles a mixed state through ImGui's mixed flag. An :term[integer]{id=integer} is a drag field limited by the property's range when it has one. A float goes through `DrawFloat`, which writes numbers as people do: "0.8" and "-4", up to three decimals, with no sign on zero.

Vectors and rotations draw one field per component behind an axis label in the theme's axis colors. A color draws channel fields and a small square of the color that opens a picker. A string is a text box, or a multi-line box with a flag. An enum is a drop-down that shows "--" when mixed. An asset or an entity reference is a button that opens a list with a search box, and accepts something dragged from the Content Browser or the Hierarchy.

:::why
The widgets take the value and options by reference and report a result :term[struct]{id=struct}, and know nothing about entities or undo. That keeps `DrawPropertyWidget` usable by the material editor and the import settings, where the value lives in an asset and not in a component. The cost is that each caller must write the result back, and the callers share the logic through the helpers of `PropertyEdit.cpp`.
:::

## The material editor

A mesh :term[renderer]{id=renderer} has a material, and a material has its own properties: colors, numbers and texture slots. The Inspector shows them under the mesh renderer, and the Asset tab shows the same ones for a material asset. Both use `MaterialEditor`. A material edit differs from a component edit in two ways. The value lives in a file, and the viewport should follow the drag at once without writing the file on every frame.

So the editor previews while the person drags, and saves once, when the drag ends. Check what each branch does in the code below.

```cpp src="StrataEditor/src/UI/MaterialEditor.cpp#L113-L128"
if (result.Changed && !result.Finished)
{
	// While dragging: only the loaded material changes, so the viewport follows the value.
	if (AssetEdit::SetMaterialProperty(context, material, property, value, true, &error))
		m_Pending = PendingPreview { material, property.Name };
	else
		ST_WARN("{}: {}", property.Name, error);
}
if (result.Finished)
{
	// The value as the widget left it (a drag's last frame may change nothing): saved, one undo step per edit.
	if (!AssetEdit::SetMaterialProperty(context, material, property, value, false, &error))
		ST_WARN("{}: {}", property.Name, error);
	context.GetUndoStack().BreakMerge();
	m_Pending.reset();
}
```

1. **Lines 113-119:** while the drag continues (`Changed` but not `Finished`), only the loaded material changes, so the viewport follows, and the editor remembers which property is pending.
2. **Lines 121-125:** on release, the value as the widget left it is saved, because a drag's last frame may change nothing.
3. **Line 126:** the merge breaks, so the next edit makes a new undo step.
4. **Line 127:** the pending preview is cleared.

One drag therefore makes one undo step and one write of the file. A click on a check box or a texture picker finishes in the frame it changes, and saves at once. If the panel hides or another material appears while a drag is open, `CommitPending` saves the preview, so a half-finished edit is never lost.

A material that a model's import made is rewritten on every import, so the editor shows its values disabled and says to give the mesh a project material through **New Material**. The editor also checks each texture slot against how the texture was imported. A color texture in the normal map slot gets a warning row with a button, **Import as Normal Map**, which imports the texture again with the usage the slot reads.

## The rest of the Inspector

### Sections and their title block

At the top the title block shows the entity's icon, its name (edit it in place), a toggle that makes it active or inactive, and its identifier (:term[ID]{id=id}) with a button that copies it. With several entities, the :term[header]{id=header} shows their count, and the toggle applies to all of them. A banner above the panel says "Playing" or "Paused" and that changes are discarded when play stops. While a scene is being opened, the whole panel is drawn disabled.

Below the title block, `DrawSelection` visits every registered component in registration order. It skips hidden components, internal ones, the name (the title block shows it) and the prefab link (the prefab bar shows it). It draws a section for each component that all selected entities have. A :term[section header]{id=section-header} shows the component's icon and name, and hovering it shows the component's description. A button with three dots opens the component menu, and a cross removes the component when it may be removed.

::figure{id=one-entity}

A component with no properties shows "No properties", or "Edited in its own section" when a special section draws it. The script component has its own drawing, covered below.

### Component drawers and property drawers

Some components need more than rows. A UI rectangle has anchors, margins and a pivot, and a table of numbers hides what they mean. A **component drawer** is a function registered for one component type that draws extra UI above the generic rows and can replace some of them. The only one the editor ships is the UI rectangle's.

The UI rectangle's drawer draws a grid of 16 anchor presets with toggles for the pivot and the position, and shows the rect in pixels at the game's screen size. When the selection stretches along an axis, it draws the left and right margins of that axis in place of the generic position and size rows. It names the replaced properties in its result, so `DrawProperties` skips them. Its rows still show prefab overrides.

::figure{id=ui-rect-drawer}

A **property drawer** is a function registered for one property of one component type that draws the value cell instead of the generic widget. The row's label, its override mark and its inactive reason still come from the panel, as the preset's row below shows. The editor ships one: the temporal anti-aliasing (TAA) preset of the post-process component. Choosing a preset there is not one property write, because the preset also decides what the tuning values mean. The drawer calls the generic widget for the choice, then sends one `component.set` command that carries the preset and, for the Custom choice, the start values, so the whole choice is one undo step.

```cpp src="StrataEditor/src/UI/ComponentDrawers.cpp#L131-L147"
void DrawTemporalAntiAliasingPreset(EditorContext& context, const PropertyDrawContext& row)
{
	if (row.Entities.empty())
		return;
	PropertyWidgetOptions options;
	options.Mixed = row.Mixed;
	options.ProbeKey = row.ProbeKey;
	PropertyValue value = row.Value;
	ImGui::BeginDisabled(row.Disabled);
	const PropertyEditResult result = DrawPropertyWidget(row.Property, value, *row.Entities.front().GetScene(), options);
	ImGui::EndDisabled();
	if (!result.Changed || !std::holds_alternative<int32_t>(value))
		return;
	const auto preset = static_cast<TemporalAntiAliasingPreset>(std::get<int32_t>(value));
	RunEditorCommand(context, row.Commands, "component.set", { { "entities", EntitiesToJson(row.Entities) }, { "component", row.Info.Name },
		{ "values", GetTemporalAntiAliasingPresetValues(row.Entities, row.Info, row.Property, preset) } });
}
```

1. **Line 140:** the drawer uses the generic widget, so its look matches the other rows.
2. **Lines 142-143:** it does nothing until the widget reports a change.
3. **Lines 145-146:** the change becomes a command with all the values it implies, not a single field.

::figure{id=taa-preset-row}

Both kinds are stored in registries keyed by the component's type id (and by property name for property drawers). `ComponentDrawers::Register` and `PropertyDrawers::Register` add to them, and `PropertyDrawers::Find` is what `DrawPropertyRow` calls for every row. The map is searched by `string_view`, because the panel asks once for each row it draws, in each frame.

### The component menu, Add Component and missing requirements

The three dots of a section open a menu. **Reset** sets every property a command can set to the value a new component has, with one `component.set`. **Copy Values** reads the primary (last selected) entity's values with `component.get` and puts them on the clipboard as :term[JSON]{id=json} that names its format and the component. **Paste Values** writes that JSON to all selected entities.

Its label counts them ("Paste Values to 3 Entities"), and it is disabled while the clipboard holds no values for this component. **Remove** runs `component.remove`, and it is missing for components the engine adds itself, such as the prefab link. Reset, Copy and Paste exist only when the component has a property a command can set.

The **Add Component** button below the sections opens a :term[popup]{id=popup}. A search field has the keyboard focus, and typing filters the list by display name. The list shows the components that some selected entity lacks, grouped by category, with the component's description as tooltip. Choosing one runs `component.add` for the selected entities. The drawing shows the list for two lamps with two letters typed.

::figure{id=add-component-popup}

A component can require another one, such as a UI image that needs a UI rect. Removing the required one is allowed, and the dependent component then has no effect. The section says so in a warning banner, and offers an **Add** button that adds the missing component to the entities without it.

### The prefab bar and overrides

When the selection is part of a prefab instance, a bar appears under the title block. A link names the prefab and shows its asset, then come three chips. **Select** selects the instance's root, and **Open** shows the prefab in the Asset tab and the Content Browser.

The **Overrides** chip shows a count and opens a menu with **Apply All to Prefab** and **Revert All**, then one entry for each override under its entity and component. Each entry has **Apply to Prefab** and **Revert**. A model instance has no Apply, because the model file is rebuilt on import.

The rows of that menu are found once and kept, until the undo version, the :term[hierarchy version]{id=hierarchy-version} or the list of overrides changes, so the menu does not walk the scene each frame. Overridden properties are marked in the rows themselves: the label is bold, an accent bar stands at the row's left edge, and a right click opens the same Apply and Revert for that one property. Whole components that differ are marked on their section header, and their menu gets Apply to Prefab and Revert to Prefab. How the engine decides what counts as an override, and keeps the list exact, is the work of [Prefab instances](../editor/prefab-instances.md).

::figure{id=prefab-instance}

Every button on the bar and the menus schedules its command. The panel runs the scheduled command after the last row, as rule 3 says.

### Scene settings when nothing is selected

With no entity selected, the panel shows the scene instead: its name and entity count, then closed sections that sum up what they hold in their headers. The sections cover physics, streaming, a link to the collision layers, a link to the fixed rate and a link to Graphics Quality. A second block shows the sky. The sections start closed on purpose: their rows are live widgets that cost :term[frame time]{id=frame-time} while drawn, so they are drawn only when the person opens them.

Some rows hold a **live line**, a line of text that describes the state of the renderer or the project in words, not a property. The directional light's section ends with one: "Shadow maps: 5 x 8192 (Graphics Quality: High)" says how many cascades and what size the Scene view's last frame used, and which quality preset is in effect. When the light casts no shadows it says "No shadow maps: Cast Shadows is off". The quality itself is a project setting ([Quality settings](../image/quality-settings.md)), so a link button beside the line opens Project Settings.

### Scripts, the animator and the target switch

A script component draws its own way. Each attached script shows its fields as rows made from the script's field list, and a prefab instance marks overridden fields in the same way as properties. When no script module is loaded, the panel says to build the scripts first. It edits scripts only for one entity at a time; with several selected it says "Select one entity to edit its scripts". See [The script system](../scripting/script-system.md) for the fields.

The animator section adds the state of the animator below its rows, but only while the scene plays and one entity is selected ([Animation in the editor](../animation/editor.md)).

When the person clicks an asset in the Content Browser, the inspection target becomes that asset. The editor brings the Asset tab forward, and when entities are selected again it brings the Inspector forward. It does this without moving the keyboard focus, so a click in the Content Browser keeps the focus there.

## The Asset tab

The Asset tab (`AssetInspectorPanel`) answers a different question: not "what is this entity" but "what is this file and how is it imported". It shows a header, the actions, the sections that fit the asset's type, the import settings, and the details. With nothing inspected it shows an empty state that says to click an asset.

### Header and actions

The top block shows a badge with the type's icon, the asset's name, the type's name and its path (or "Built-in"). It also shows the handle, the :term[universally unique identifier]{id=uuid} (UUID) that commands and scripts use, with a button that copies it. Under it stand the actions that fit the type: buttons such as **Open**, **Cook**, **Add to Scene** and **Reimport**. **Reimport** runs in the background and the panel waits for the result through the :term[command runner]{id=command-runner}, not on the main thread.

### Import settings: a draft with Apply and Revert

An :term[importer]{id=importer} describes its settings as a property list, like a component does (`GetSettingsProperties`). The panel draws that list with the same table and the same `DrawPropertyWidget`. The edits go to a **draft**, a copy of the settings that belongs to the panel. Nothing is imported while the person edits.

Why a draft? An import can take seconds or minutes: a large texture is compressed, a model is rebuilt. If every drag frame started an import, the editor would import again hundreds of times.

So the draft collects the edits, the title line says "Not applied", and two buttons wait at the right. **Revert** copies the saved settings back into the draft. **Apply** sends the settings that changed to `asset.setImportSettings`, which merges them into the others and starts one background import.

While it runs, the rows are disabled and the panel says "Importing...". If the command fails, the error is shown in red under the rows.

Only the changed settings are sent. A `.meta` file written by another engine version may hold a setting the importer does not know, and sending the whole draft would make the command refuse every Apply. The draft follows the asset's real settings while it has no edits of its own, so a change by a command appears at once.

Inactive reasons work here too, with a different mechanism. The importer answers `GetInactiveReason` for a setting name and the current draft. Quality of a texture that is not compressed is an example: it has no effect then. The row is disabled, and the tooltip adds "No effect now:" and the reason. A texture's usage and compression are covered by [Texture cooking](../assets/texture-cooking.md).

### Material section, previews and the rest

For a material asset, the Material section holds the same `MaterialEditor` that the mesh renderer shows. Models get a summary of what the import found, and worlds a summary of their cells. Animation controllers, skeletons and clips get their own views (`AnimationAssetViews`), which [Animation in the editor](../animation/editor.md) describes.

::figure{id=asset-material}

A texture gets a preview. The panel asks the texture streamer for the mip level that the preview's pixel height needs, so a large texture does not load all its levels for a thumbnail. It draws the image through `UI::TextureImage`, which chooses a display mode from the texture's format. Colors are shown as stored or encoded to :term[sRGB]{id=srgb}, a one-channel texture as gray, and a two-channel normal map through the `NormalXY` mode. That mode rebuilds the third component the way a material does.

The caption below gives the texture's size and format. A raw view of the same normal map would show only red and green, because the third component is not stored. The `NormalXY` mode rebuilds it, so the preview has the purple-blue of a normal map and shows the surface as the material reads it. The modes themselves belong to [ImGui and its backends](imgui-backends.md).

::figure{id=asset-normal-map}

An audio clip gets a Play button, a time line and a waveform. A **waveform** is a picture of a clip's loudness over time: for each column of the picture, the lowest and highest sample value of the stretch of sound it stands for, drawn as one bar. `AudioPreview` owns one preview source outside any scene, so playing a clip does not touch the game. It computes the waveform on a job, in 256 columns, and the panel draws it only when the result arrives. Clips longer than 600 seconds get no waveform.

While the clip plays, a line moves over the picture. The preview stops when the inspected asset changes.

::figure{id=asset-audio}

Last comes the import outcome. If the import failed, a red line shows the error. Warnings of the import show in yellow. A :term[sub-asset]{id=sub-asset}, such as a material a model made, says that it is imported with the file it comes from and offers a button that inspects that file.

:::example
Walk through one drag. A scene holds three point lights with intensities 2, 5 and 5, and all three are selected.

1. `GetSharedProperty` finds that the second light differs from the first, so the Intensity row is mixed and shows "--". No inactive reason applies.
2. The person starts dragging the field. ImGui reports a change on the first frame, with the value 6. The panel sees several entities and no partial vector, so it takes the last branch and calls `SetPropertyWithUndo` with the shown value and 6. A new undo step is made, with the before values 2, 5 and 5.
3. Each of the next frames reports 7, 8 and 9. Each call finds the open merge on the same property of the same entities and only updates the step's final value. The stack holds one step.
4. The person lets go. `Finished` is true, so the panel calls `BreakMerge`. All three lights now hold 9, and one **Ctrl+Z** returns them to 2, 5 and 5, not to 9, 8 and 7.

If the same drag were made on a vector with only X dragged, step 2 would take the partial branch, and the other axes of each light would keep their own values.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A hand-written editor per component | Unity custom editors, Unreal detail panel classes | The best layout for each type | A screen to write and update for every component and property |
| Generated inspectors from a header tool | Unreal's property system, Qt's meta-object :term[compiler]{id=compiler} | Types known at build time, with no separate registration | A build step and a generator, and a registration that lives in a macro |
| A scripting-language UI description | Godot's editor extensions | Editors that change without a rebuild | A second language in the editor, and slower rows |
| Apply each import-settings edit at once | Some asset tools | No draft, no Apply button | An import for every drag frame |
| Write each drag frame as its own undo step | Simple editors | No merge state to keep | A hundred steps for one drag, and an undo that is useless |

The first row is the real alternative: it is the best-looking result, and the one that scales worst. Strata keeps it for the UI rectangle only, because there the generic rows hide the meaning of the numbers. Everything else is generic until a person finds it unclear, and then one drawer is written.

## How it is tested

The tests drive the real panel and read it through probes. The panel records the name and the text of each item it draws under a key such as `Inspector.<Component>.<Property>`. A test clicks or drags an item and then reads the scene and the undo stack.

- The suite `Editor.UI.Inspector` holds the generic panel's cases. One case checks that properties another property disables show disabled with the reason, on every selected entity only. Others check that clicking the X label resets only X. They also check that editing the intensity of 30 selected lights is one undo step, and that Paste Values onto three entities is one undo step.
- The suite `Editor.UI.AssetInspector` covers the material editor's warning under a slot whose texture is imported for another use. It also covers the button that imports the texture right, and how a click in the Content Browser brings the Asset tab forward.
- The hierarchy suite `Editor.UI.Hierarchy` holds the prefab bar cases: the Overrides menu, marks, Revert All, and the stretched UI rect's rows.
- `Editor.Audio` covers the preview voice, `Editor.UI.AssetInspector` the clip's Play button and waveform, and `Editor.Thumbnails` the waveform's lowest and highest sample per column.
- The rotation edit has unit cases in `StrataTests/src/Editor/EditorEntityCommandTests.cpp`.

To run one suite, use the doctest filter on the test program, as in `build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.UI.Inspector`. The panel's tests are plain tests with no :term[graphics processing unit]{id=gpu} (GPU) label.

## Changing it safely

The extension points are the registries, and each has a rule.

- **To show a new property**, register it with its type, range and tooltip. The Inspector draws it with no change in the editor. A property of an existing type needs no code here.
- **To disable a property under a condition**, add an inactive reason next to the property's registration. The panel needs no change: `GetSharedInactiveReason` finds it, disables the row and adds the reason to the tooltip. Write the reason in words a person can act on ("Bloom is off"), and make it empty when the property has an effect.
- **To draw a value in a special way**, register a property drawer. Draw the value cell only, use `DrawPropertyWidget` where it fits, and make your edit through the helpers, a `component.set` command or `SetPropertyWithUndo`.
- **To draw a whole component specially**, register a component drawer. Name each generic row it replaces through its result, so the panel skips them, and show prefab overrides with the :term[callbacks]{id=callback} it gets.
- **To add a new property type**, add a `switch` case in `DrawPropertyWidget`, and set `Finished` correctly for continuous and discrete edits.

Four rules of the engine apply to every such change.

:::rule
The engine's guide says that UI code takes its colors from theme tokens, its sizes from the :term[font]{id=font} and its panels from the panel registry. A panel that draws its own colors breaks the themes. Details: [The shell](shell.md).
:::

:::rule
The engine's guide says that a property another property can disable gets an inactive reason. A disabled row without a reason is a puzzle for the person. Details: [Reflection](../world/reflection.md).
:::

:::rule
The engine's guide forbids walking the scene or the asset folder in every frame of UI code: panels draw cached views that are rebuilt when a version changes. The groups are cached per type, and the override rows by version. Details: [The shell](shell.md).
:::

:::rule
The engine's guide says that a command that replaces the edited scene first checks whether changes are saved. The prefab bar's buttons run `prefab.apply` and `prefab.revert` through the same :term[command registry]{id=command-registry}, so they get these checks and one undo step; they are scheduled for the reason of rule 3. Details: [Commands](../editor/commands.md).
:::

The checks to pass are the `Editor.UI.Inspector` and `Editor.UI.AssetInspector` suites, the feature test (a new component or property must be exercised there) and the whole `ctest` set.

## What went wrong before

Rotations were once edited by reading the angles back from the quaternion after each drag frame. Dragging the yaw of several entities past 90 degrees made them fold back, and a drag through exactly 90 degrees lost the pitch and the roll of each entity. The fix, in the commits "Edit the Euler angles of several entities' rotations directly" and "Keep each entity's Euler angles through a rotation edit", is `RotationAnglesEdit`.

Its regression tests are in `Editor.UI.Inspector`. One is named "Dragging the yaw of several entities past 90 degrees turns them past 90 degrees". The other is named "Dragging the yaw of several entities through exactly 90 degrees keeps each one's pitch and roll". Each drags the field and compares every entity's rotation with the expected one.

## Summary

- One panel draws every component: it groups a type's properties by section once, draws a label and a value for each, and uses a property drawer or the generic widget by type.
- With several entities selected, a differing value shows "--", an edit writes only the components that changed, and a rotation drag uses the angles the widget showed.
- A drag merges into one undo step, and the widget's finished flag breaks the merge; the material editor previews while dragging and saves once on release.
- A component drawer replaces rows with a special layout, such as the UI rectangle's anchor grid, and a property drawer replaces one value cell, such as the TAA preset.
- A property that another property can switch off gets an inactive reason, and the Inspector disables the row and shows the reason, for the selection only when it holds on every entity.

## Check yourself

1. Three lights have a Softness of 0.2, 0.2 and 0.8, and the person drags the field to 0.5. What does the row show before the drag, and what do the lights hold after it?

   :::answer{tests="multi"}
   Before the drag the row shows "--", because the values differ. A float is a single component, so the edit is not partial: the last branch writes 0.5 to all three lights, as one undo step with the before values 0.2, 0.2 and 0.8. One undo restores all three values.
   :::

2. A light has shadows off, and its softness row is drawn disabled. A second light with shadows on is added to the selection. What does the softness row do now, and why?

   :::answer{tests="inactive"}
   The row becomes active. `GetSharedInactiveReason` returns an empty text as soon as one entity has no reason, and a multi-selection shows a property inactive only when every selected entity says so. Disabling the row would stop the person from editing the light for which softness matters.
   :::

3. Why does the Inspector run a prefab command after the last row, and not when the menu item is clicked?

   :::answer{tests="generic"}
   The command rebuilds the instance, and the rows still to be drawn hold entities and components of the old state. Storing the command with `SchedulePrefabCommand` and running it after the loop means every row of a frame reads a scene that does not change in the middle of it.
   :::

4. Two entities have the rotations of yaw 80 and yaw 100 degrees. The person drags yaw to 120 over many frames. Why would reading the angles back from the quaternions each frame go wrong?

   :::answer{tests="multi"}
   A rotation has two angle sets, and the read-back gives the one with yaw within -90 to 90. At 100 or 120 degrees the read-back returns the other set, with a different pitch and roll and a yaw that folds back. `RotationAnglesEdit` reads each entity's angles once at the start and edits only the changed angle in the stored values.
   :::

5. A person drags a material's roughness for two seconds and releases. How many writes of the material file happen, and how many undo steps?

   :::answer{tests="undo"}
   One write and one undo step. During the drag only the loaded material changes, so the viewport follows. On release the value is saved with `SetMaterialProperty`, and the merge breaks.
   :::

6. The editor ships a drawer for the TAA preset and another for the UI rectangle. Which kind is each, and why can the preset not be a plain generic row?

   :::answer{tests="drawer"}
   The TAA preset is a property drawer, because it replaces one value cell. The UI rectangle's is a component drawer, because it draws a grid above the rows and replaces several of them. The preset is not a plain row because choosing it must also write tuning values, and a single property write cannot do that in one undo step.
   :::

## Exercises

1. **Basic.** In the toy, a third property `Radius` is wanted, with an inactive reason "Shadows are off" while the light has no shadows. Write the list entry, and say what the output shows when one light has shadows on and the other off.

   :::answer[Worked solution]{tests="inactive"}
   The entry repeats the three functions of the Softness entry for a new `Radius` field of `Light`, and its reason function returns "Shadows are off" when `CastShadows` is false. With one light on and one off, the row shows no reason. The loop clears the reason at the light with shadows on, and a later light with a reason does not bring it back. The row is active, as in the real panel.
   :::

2. **Medium.** Extend the axes sketch so that clicking the Y label resets Y to 0 for the three positions, even when the shown Y already is 0. Say what the function needs that `Write` does not have.

   :::answer[Worked solution]{tests="multi"}
   Comparing the shown and edited values finds no change, because both Y values are 0, so the other entities keep their Y. The function needs the list of axes the click touched. The widget reports it as `ChangedComponents`, and `SetPropertyComponentsWithUndo` takes it as a mask: `Write` becomes `Write(positions, edited, mask)`, and an axis is written when its mask entry is true. With a mask of `{ false, true, false }` and an edited value of `(0, 0, 0)`, only Y changes, so the three positions become (1, 0, 0), (2, 0, 0) and (3, 0, 0).
   :::

3. **Medium.** Register a property drawer that draws the post-process white balance temperature (`WhiteBalanceTemperature`, range 2000 to 15000) as a gradient bar from warm to cool. Write the registration and the drawer's skeleton, and name the registry and the key.

   :::answer[Worked solution]{tests="drawer"}
   The registry is `PropertyDrawers`, the key the component's type :term[hash]{id=hash} and the property name. The editor UI calls `UI::PropertyDrawers::Register(entt::type_id<PostProcessComponent>().hash(), "WhiteBalanceTemperature", &DrawTemperatureBar);` once at startup. The drawer has the signature `void DrawTemperatureBar(EditorContext& context, const UI::PropertyDrawContext& row)`.

   The drawer draws a gradient from `row.Property.Min` to `row.Property.Max`, inside a disabled scope when `row.Disabled` is true, so an inactive row still looks inactive. A click or drag on the bar computes the value from the position and sends `component.set` for `row.Entities`, as the TAA drawer does. The label, the override mark and the inactive reason come from the panel.
   :::

4. **Hard.** Trace it yourself: find where a drag of a light's Intensity writes the value, and where the merge ends. Use a breakpoint or a search, then say which function runs for one selected light and which for three.

   :::answer[Worked solution]{tests="undo"}
   Put a breakpoint in `InspectorPanel::DrawPropertyRow` in `StrataEditor/src/Panels/InspectorPanel.cpp`, at the `SetPropertyWithUndo` calls at lines 1029 and 1035, and drag the intensity of one light. Each changed frame calls `SetPropertyWithUndo(context, entity, ...)` for one entity, and the undo stack keeps one step. The frame when the mouse is released has `result.Finished` true, and execution reaches `context.GetUndoStack().BreakMerge()` at line 1041. With three lights selected the same drag takes the branch for several entities, the last `SetPropertyWithUndo` call with the shown and edited values. An intensity is one float, so no partial write happens, and the stack still holds one step.
   :::

## Where it lives in Strata

- `StrataEditor/src/Panels/InspectorPanel.cpp` and `InspectorPanel.h`: `InspectorPanel`, `GetPropertyGroups`, `DrawProperties`, `DrawPropertyRow`, `DrawComponentMenu`, `DrawAddComponentPopup`, `DrawPrefabBar`, `DrawSceneSettings`.
- `StrataEditor/src/UI/PropertyWidgets.cpp` and `PropertyWidgets.h`: `DrawPropertyWidget`, `PropertyEditResult`, `PropertyWidgetOptions`, `BeginPropertyTable`, `PropertyLabel`, `PropertyGroupHeading`.
- `StrataEditor/src/Editor/PropertyEdit.cpp` and `PropertyEdit.h`: `GetSharedProperty`, `GetSharedInactiveReason`, `SetPropertyWithUndo`, `SetPropertyComponentsWithUndo`, `RotationAnglesEdit`.
- `StrataEditor/src/UI/ComponentDrawers.cpp`, `ComponentDrawers.h` and `UIRectDrawer.cpp`: `ComponentDrawers`, `PropertyDrawers`, `DrawTemporalAntiAliasingPreset`, `DrawUIRect`.
- `StrataEditor/src/UI/MaterialEditor.cpp`: `MaterialEditor`.
- `StrataEditor/src/Panels/AssetInspectorPanel.cpp`, `StrataEditor/src/Editor/AudioPreview.cpp`: the Asset tab and `AudioPreview`.
- Tests: `StrataTests/src/Editor/EditorAuthoringUITests.cpp` (suites `Editor.UI.Inspector`, `Editor.UI.AssetInspector`), `EditorEntityCommandTests.cpp`, `EditorAudioTests.cpp`, `ThumbnailTests.cpp`.
- Commands: `component.set`, `component.get`, `component.add`, `component.remove`, `prefab.apply`, `prefab.revert`, `asset.setImportSettings`, `selection.set`.

## Further reading

- Unity Manual, "Custom Editors" and "Property Drawers": how another engine layers hand-written editors over a generic inspector (intermediate).
- Unreal Engine documentation, "Details panel customization": the same layering with detail and property type customizations (intermediate).
- Godot documentation, "Inspector plugins" (`EditorInspectorPlugin`): replacing rows for matching objects (intermediate).
- Dear ImGui's repository and its wiki, section on tables: the table that the property table is built on (intermediate).
