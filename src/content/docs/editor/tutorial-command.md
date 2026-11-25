---
id: editor/tutorial-command
title: "Tutorial: adding a command"
description: "Give the wind zone two editor commands, one that lists the zones and one that sets several in one undo step, with their tests and a run from the terminal."
kind: tutorial
size: L
tracks: [E]
needs: [editor/undo, scripting/tutorial-host-function, core/first-change]
time: 180
learn:
  - id: command-home
    text: name the three places a new group of commands must be listed, and predict which test fails when one is missing
  - id: query-command
    text: write a command that only reads, with a complete schema, an answer and the kind Query
  - id: edit-command
    text: write a command that checks every input before one transaction changes anything, signals the change and ends with FinishEdit
  - id: command-tests
    text: add a test suite for a command that covers success, one undo step, refusals without side effects and the running copy
  - id: run-command
    text: run a new command from a terminal, undo it and read its entry in the activity journal
since: 0.8.0
status: final
---

## What you will make

You will give the wind zone two commands: `wind.list`, which tells what every zone holds, and `wind.set`, which changes several zones in one :term[undo step]{id=undo-step}. People, agents and tests call them like every other command of the editor.

```mermaid caption="Two new commands join the registry: one that only reads the wind zones, and one that changes several of them in one undo step." alt="Three callers on the left, an agent, a terminal and a unit test, point to one box, the command registry. From the registry two arrows lead to two boxes, a command that lists the zones and a command that sets them. The second box also points to the undo history and to the scene."
flowchart LR
    U["Agent"] --> R["Command registry"]
    T["Terminal"] --> R
    X["Unit test"] --> R
    R --> L["List the zones"]
    R --> S["Set the zones"]
    L --> W["Scene"]
    S --> W
    S --> H["Undo history"]
```

## Why the wind zone needs commands

The wind zone of [the component tutorial](../world/tutorial-component.md) has a strength, a radius and a mode. You can change them in the Inspector, one zone at a time. A scene with forty zones in a forest turns that into forty edits, and a person who wants all of them at 40 N has no better way. An agent that has no mouse has no way at all. A test that wants to prove the change must write to the components by hand.

Strata answers this for every part of the editor with one rule: the commands are the application programming interface (API) of the editor. Each is one named operation with one schema for its input and one handler. You already know what a command is and how the registry runs one. This page adds two commands to the registry and follows the rules that [the commands page](commands.md) gave, so that the new commands behave like the old ones. The tutorials before it gave the wind zone a system, a :term[host function]{id=host-function} for scripts and a :term[callback]{id=callback}; these commands give people and agents a way in.

Take two zones. The `Breeze` has a strength of 10 N and a radius of 5 m. The `Gust` has 25 N and 8.5 m.

One call of `wind.set` with both zones, a strength of 40 N and the mode `Spherical` should leave both zones at 40 N and `Spherical`, with their radii of 5 m and 8.5 m untouched. One call of `edit.undo` should bring back 10 N and 25 N and the mode `Directional` of both, because the call made one step. A second `edit.undo` should find nothing to undo.

A call with a strength of 5000 N should be refused, because the property allows at most 1000 N, and then no zone may change. These sentences are the whole specification, and you turn them into tests before you finish.

Every command has a kind, one of `Edit`, `Query` or `Session`, that says what the command touches. An `Edit` changes the scene or the project. A `Query` changes nothing. A `Session` changes only the editor's own state, such as the selection or the camera. A recorded script repeats the edits and leaves the others out, so the kind is part of what a command means.

:::why[A list of kinds that a test keeps]
A command that you forget to mark counts as an edit, because the safe guess is that it changed something. A command that only reads would then be repeated by every replay. Strata therefore keeps three lists of every command's name in a test, and the test fails until you place a new command in one of them. The failure is the reminder, and it costs you one line.
:::

## What you need

- The source build of [your first engine change](../core/first-change.md): a clone at the book's commit, its :term[submodules]{id=submodule} and a `Debug` build of your system's :term[CMake preset]{id=cmake-preset}. Every command below writes `<preset>` for that preset: `windows`, `linux` or `macos`.
- The end state of [the host function tutorial](../scripting/tutorial-host-function.md), which already holds the wind zone, its system and the tests. The patch of this page applies on top of it and touches none of its files.
- A project to call the commands on, such as the one you made from the Basic 3D template. The last section starts the editor with it and creates two zones in it, so no scene needs to be ready.
- Time: about three hours. The first build compiles the editor, the command-line client and the tests again, and that is the longest wait.
- No file to import. You change three files, add two, and change two lists of a test.

:::files[The files of the change]

- `StrataEditor/src/Editor/`
  - `Commands/WindCommands.cpp`: new, the two commands
  - `EditorCommands.h`, `EditorCommands.cpp`: the declaration and the call that registers them
- `StrataCLI/src/CLI/McpToolsets.cpp`: the group's place among the toolsets
- `StrataTests/src/Editor/`
  - `CommandJournalTests.cpp`: the two kinds
  - `EditorWindCommandTests.cpp`: new, the suite of the wind commands

:::

## Give the commands a home

Commands live in groups: all `entity.*` commands are in one file, all `audio.*` commands in another. The registry does not search for them. Its :term[constructor]{id=constructor} calls one function per group, and a group that no one calls does not exist. You add the group `wind`, wire it, and meet the two tests that guard the wiring.

:::::steps

1. Read the constructor of the registry. Every built-in command comes from a call in this list.

   ```cpp src="StrataEditor/src/Editor/EditorCommands.cpp#L43-L64" from="RegisterSceneCommands(*this);" to="RegisterPlacementCommands(*this);" symbol="EditorCommandRegistry::EditorCommandRegistry"
   RegisterSceneCommands(*this);
   RegisterEntityCommands(*this);
   RegisterPrefabCommands(*this);
   RegisterAssetCommands(*this);
   RegisterProjectSettingsCommands(*this);
   RegisterPreferencesCommands(*this);
   RegisterInputActionsCommands(*this);
   RegisterGraphicsCommands(*this);
   RegisterEditorStateCommands(*this);
   RegisterPlayCommands(*this);
   RegisterViewportCommands(*this);
   RegisterScriptCommands(*this);
   RegisterInputCommands(*this);
   RegisterStreamingCommands(*this);
   RegisterAnimationCommands(*this);
   RegisterWorldCommands(*this);
   RegisterLightingCommands(*this);
   RegisterAudioCommands(*this);
   RegisterUICommands(*this);
   RegisterUIInputCommands(*this);
   RegisterBatchCommands(*this);
   RegisterPlacementCommands(*this);
   ```

   1. **Line 43:** the first group, the commands of scenes.
   2. **Lines 44–63:** one call for each other group, so that every prefix has a function of its own.
   3. **Line 64:** the last built-in group; the wind group takes one more line after it.

   The registry never searches for groups: a function that no line calls adds no command.

   **You should see:** twenty-two calls, from `RegisterSceneCommands` to `RegisterPlacementCommands`.

   **If you do not see it:** the file differs when your clone is not at the book's commit. Return it there, as the first change does.

2. Declare the function of the new group in `StrataEditor/src/Editor/EditorCommands.h`, after the last declaration. The comment names the file it will live in, as the comments of the other groups do.

   ```diff src="book:tutorials/editor/tutorial-command.patch#hunk-4"
    	void RegisterAudioCommands(EditorCommandRegistry& registry); // audio.* (Commands/AudioCommands.cpp)
    	void RegisterUICommands(EditorCommandRegistry& registry);      // ui.create, ui.layout, ui.hitTest (EditorUICommands.cpp)
    	void RegisterUIInputCommands(EditorCommandRegistry& registry); // input.click, input.type (EditorInputCommands.cpp)
   +	void RegisterWindCommands(EditorCommandRegistry& registry);    // wind.list, wind.set (Commands/WindCommands.cpp)
    
    }
   ```

   **You should see:** one new line after `RegisterUIInputCommands`.

   **If you do not see it:** a :term[compiler error]{id=compile-error} about `RegisterWindCommands` later means the declaration is missing or sits in another :term[namespace]{id=namespace}. It belongs inside `namespace Strata`, as its neighbors do.

3. Call the function from the constructor, after the last group, in `StrataEditor/src/Editor/EditorCommands.cpp`.

   ```diff src="book:tutorials/editor/tutorial-command.patch#hunk-3"
    		RegisterUIInputCommands(*this);
    		RegisterBatchCommands(*this);
    		RegisterPlacementCommands(*this);
   +		RegisterWindCommands(*this);
    
    		Register({ "editor.commands",
    			"Every editor command with its description, the JSON Schema of its parameters and its kind: \"Edit\" (changes the scene, its assets or "
   ```

   **You should see:** one new call before the registration of `editor.commands`.

   **If you do not see it:** if the call comes after the registration of `editor.commands`, nothing breaks, but the group is no longer next to its peers. Keep the order of the file.

4. Create the new file `WindCommands.cpp` in the folder `StrataEditor/src/Editor/Commands/`. It starts with the includes that the whole file needs and the helper namespace of the editor's commands. The block lists them for the finished file, so write all of it now.

   ```cpp src="book:tutorials/editor/tutorial-command/WindCommands.cpp#L1-L24"
   #include "Editor/CommandUtils.h"
   #include "Editor/EditorCommands.h"
   #include "Editor/EditorContext.h"
   #include "Editor/SceneEdit.h"

   #include <Strata/Physics/PhysicsComponents.h>
   #include <Strata/Reflection/ComponentRegistry.h>
   #include <Strata/Reflection/PropertyJson.h>
   #include <Strata/Scene/Scene.h>

   #include <nlohmann/json.hpp>

   #include <optional>
   #include <string>
   #include <string_view>
   #include <unordered_set>
   #include <vector>

   // The wind.* commands: what the scene's wind zones hold, and a change of several of them at once.

   namespace Strata
   {

   	using namespace CommandUtils;
   ```

   1. **Lines 1–4:** the editor's own :term[headers]{id=header}: the helpers that every command uses, the registry, the context and the transaction.
   2. **Lines 6–9:** the engine's headers: the component, the registry of reflected components, the :term[JSON]{id=json} form of values and the scene.
   3. **Line 19:** one comment says what the file is for, as the other command files do.
   4. **Line 24:** `using namespace CommandUtils` brings the schema helpers, `ObjectSchema` and its neighbors, into reach.

   **You should see:** a new file that holds no function yet.

   **If you do not see it:** the file is not part of the build until you configure again, as the next steps do.

5. Add the function that registers the group, with the first command. This command has a name, a description written for an agent, an empty schema, a handler and a kind. For now the handler answers an empty list; the next section writes the real one. Write the handler's body as `return EditorCommandResult::Ok({ { "zones", nlohmann::json::array() } });` and end the call with `}, EditorCommandKind::Query });` as the quote at the end of the next section shows.

   ```cpp src="book:tutorials/editor/tutorial-command/WindCommands.cpp#L76-L81"
   void RegisterWindCommands(EditorCommandRegistry& registry)
   {
   	registry.Register({ "wind.list",
   		"Lists every entity with a WindZone component, active or not: {zones: [{entity, name, active (the entity's own flag), strength "
   		"(newtons), radius (meters), mode (\"Directional\" or \"Spherical\")}]}. Changes nothing; while playing it lists the running copy.",
   		ObjectSchema({}),
   ```

   The description says what the :term[command lists]{id=command-list} and what the answer holds, because an agent sees only the description and the schema. The schema has no property, so `ObjectSchema({})` is complete: a call with a parameter would be refused.

   **You should see:** one function, `RegisterWindCommands`, with one `registry.Register` call.

   **If you do not see it:** a brace that is not closed gives an error far below the real mistake. Count the braces of the `Register` call first.

6. Configure again, because a new :term[source file]{id=source-file} needs it, then build everything.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --parallel
   ```

   **You should see:** a build without warnings.

   **If you do not see it:** an unknown name `PropertyInfo` or `ComponentInfo` means a header of the list in step 4 is missing. Compare with the quote.

7. Run the two tests that know every command.

   ```sh
   build/<preset>/bin/Debug/StrataTests --test-suite=Editor.Journal
   build/<preset>/bin/Debug/StrataTests --test-suite=CLI.McpToolsets
   ```

   **You should see:** both suites fail. The first stops at a `REQUIRE` that expects the sum 1 and finds 0, with the context `command->Name := "wind.list"`: no list of kinds names the command. The second reports that `wind.list` is in no toolset of the table.

   **If you do not see it:** the second suite exists only when the tests are built with the command-line client. A build that omits it shows one failure, and you meet the second one in step 9 by reading.

   **Why:** a failing test is the checklist. Two decisions were never made, and the tests refuse to let you skip them: what the command means for a replay, and which group of tools an agent finds it in.

8. Make the first decision. List `wind.list` among the queries in `StrataTests/src/Editor/CommandJournalTests.cpp`, in the list that keeps the names in the order of the alphabet.

   ```diff src="book:tutorials/editor/tutorial-command.patch#hunk-6"
    		"selection.get",
    		"ui.hitTest", "ui.layout",
    		"viewport.capture", "viewport.getSettings",
   +		"wind.list",
    		"world.info", "world.status",
    	};
    	constexpr std::string_view c_SessionCommands[] = {
   ```

   The list of kinds exists so that nobody has to remember. The test checks both ways: the command must be in one list, and the kind in its registration must match the list. A command that is in the `Edit` list but registered as a `Query` fails the second check.

   **You should see:** the new name between `viewport.getSettings` and `world.info`. Run `Editor.Journal` again: it passes.

   **If you do not see it:** the test fails with `0 == 1` when the name has a wrong letter and `2 == 1` when you put it into two lists.

9. Make the second decision. An agent does not see every command by default, because a client takes only so many tool definitions. The commands are sorted into toolsets, named groups of tools, by the prefix of their name, and a table in the command-line client maps each prefix to its set. The `wind.` prefix joins the `world` set, next to `world.` and `physics.`, because zones are part of the simulated world. The Model Context Protocol (MCP) is how agents reach the tools; [the MCP page](../automation/mcp.md) tells why the sets exist.

   ```diff src="book:tutorials/editor/tutorial-command.patch#hunk-1"
    			{ "viewport.", "viewport" }, { "camera.", "viewport" },
    			{ "editor.", "editor" }, { "log.", "editor" },
    			{ "ui.", "ui" },
   -			{ "world.", "world" }, { "physics.", "world" },
   +			{ "world.", "world" }, { "physics.", "world" }, { "wind.", "world" },
    			{ "preferences.", "settings" }, { "inputActions.", "settings" }, { "graphics.", "settings" } };
    
    		constexpr ToolsetInfo c_Toolsets[] = {
   ```

   The patch names `CLI.McpToolsets` among its tests, so that no later page starts from a failing suite.

   **You should see:** one changed line. Build and run `CLI.McpToolsets`: it passes.

   **If you do not see it:** a command whose prefix no row names fails the same test, and the message names the command.

:::::

The group is wired and its first command is registered, with its kind and its set. Two tests that you did not write told you what was missing; the rule they enforce is the last rule of the commands page: every command declares its kind.

## List the zones with wind.list

A command that only reads should still answer in a form that a program can use. The answer of `wind.list` holds the entity's identifier (ID), because every other command takes IDs, and the values in the units of the component. A caller can feed an ID of this answer straight into `wind.set`.

:::::steps

1. Replace the handler with the real one. The handler asks the active scene for every entity with a `WindZone` and builds one :term[JSON object]{id=json-object} for each.

   ```cpp src="book:tutorials/editor/tutorial-command/WindCommands.cpp#L82-L93"
   [](EditorContext& context, const nlohmann::json&)
   {
   	Scene& scene = *context.GetActiveScene();
   	nlohmann::json zones = nlohmann::json::array();
   	for (const auto [handle, zone] : scene.GetRegistry().view<WindZoneComponent>().each())
   	{
   		const Entity entity(handle, &scene);
   		zones.push_back({ { "entity", UUIDToJson(entity.GetUUID()) }, { "name", entity.GetName() }, { "active", entity.IsActive() },
   			{ "strength", zone.Strength }, { "radius", zone.Radius }, { "mode", ToString(zone.Mode) } });
   	}
   	return EditorCommandResult::Ok({ { "zones", std::move(zones) } });
   }, EditorCommandKind::Query });
   ```

   1. **Line 84:** `GetActiveScene` is the scene the person sees: the edited scene, or while the game plays, its running copy.
   2. **Line 86:** the view visits each entity that holds the component, with the component beside it.
   3. **Lines 89–90:** one object for each zone. The entity's ID goes through `UUIDToJson`, the one form of an ID in every command.
   4. **Line 92:** the answer is an object with the key `zones`, so that a later version can add keys without breaking callers.
   5. **Line 93:** the kind `Query` closes the registration.

   **You should see:** the handler reads the scene and never writes it.

   **If you do not see it:** a handler that calls `MarkModified` or opens a transaction does not belong to a query. A reading command that changes something breaks every replay that leaves queries out.

2. Add the small function that turns the mode into the text that the component's registration uses. Place it in the namespace without a name in the file, before the function that registers the group.

   ```cpp src="book:tutorials/editor/tutorial-command/WindCommands.cpp#L26-L32"
   namespace
   {

   	const char* ToString(WindZoneMode mode)
   	{
   		return mode == WindZoneMode::Spherical ? "Spherical" : "Directional";
   	}
   ```

   The text `Directional` and `Spherical` is the same text that scene files hold, so a caller sees one spelling everywhere.

   **You should see:** one helper of two lines in the namespace without a name.

   **If you do not see it:** the :term[compiler]{id=compiler} reports an unused function in a build with warnings as errors if you forget the call in the handler. The handler of step 1 calls it.

3. Build and run the journal test again.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Editor.Journal
   ```

   **You should see:** a build without warnings and a passing suite. The command now answers with real data; its test comes in the fourth section.

   **If you do not see it:** an error about `WindZoneComponent` means the include of `PhysicsComponents.h` is missing. Line 6 of the file has it.

:::::

Consider what the kind buys. An agent that plans a change calls `wind.list` first, and a replay of the session leaves the call out, because it changed nothing. The activity journal, the editor's record of every command that ran, keeps the call with `mutating` false. The next command has the opposite property, and everything that the Query avoided, it has to do.

## Set several zones with wind.set

An edit has three duties that a query does not have. It checks every input before anything changes. It records one undo step for the whole call. It tells the scene what it wrote. You write the command in four steps, in the order in which a call meets them.

:::::steps

1. Register the command with its schema. The schema names `entities` as required and the three values as optional, so a caller changes only what it names.

   ```cpp src="book:tutorials/editor/tutorial-command/WindCommands.cpp#L95-L105"
   registry.Register({ "wind.set",
   	"Sets the strength, radius or mode of the WindZone of one or more entities in one undo step (while playing it changes the "
   	"running copy only). Values left out stay as they are; at least one is required. Refuses, changing nothing, an entity without a "
   	"WindZone and a value outside its property's range. Returns {entities}.",
   	ObjectSchema({
   		{ "entities", EntityArraySchema("Entities with a WindZone component") },
   		{ "strength", NumberSchema("Force of the wind on a body, in newtons (within the range of the Strength property)") },
   		{ "radius", NumberSchema("How far the zones reach from their center, in meters (within the range of the Radius property)") },
   		{ "mode", { { "type", "string" }, { "enum", { "Directional", "Spherical" } },
   			{ "description", "Directional zones blow one way through their radius, spherical zones outward from their center" } } } },
   		{ "entities" }),
   ```

   1. **Lines 96–98:** the description says what changes, that a playing scene changes its running copy only, what is refused and what is returned.
   2. **Line 100:** `entities` is an array of IDs. The registry refuses a call without it before the handler runs.
   3. **Lines 101–102:** the numbers have descriptions that name the range of the property, which the schema does not repeat.
   4. **Lines 103–104:** the mode is a string with its two options in an `enum`, so that a client lists them.

   **You should see:** a schema with four properties and one required name.

   **If you do not see it:** a property without a description is a gap that agents notice: the description is all they read.

2. Write the two helpers that read values through the component's reflection. The component registered a range for each property; the command asks the registration instead of repeating the numbers.

   ```cpp src="book:tutorials/editor/tutorial-command/WindCommands.cpp#L34-L72"
   // The wind zone's registered properties: commands check values against them, so that a command accepts what the
   // Inspector accepts and refuses what lies outside a property's range.
   struct WindProperties
   {
   	const PropertyInfo* Strength = nullptr;
   	const PropertyInfo* Radius = nullptr;
   	const PropertyInfo* Mode = nullptr;
   };

   std::optional<WindProperties> FindWindProperties()
   {
   	const ComponentInfo* info = ComponentRegistry::Find<WindZoneComponent>();
   	if (!info)
   		return std::nullopt;
   	const WindProperties properties { info->FindProperty("Strength"), info->FindProperty("Radius"), info->FindProperty("Mode") };
   	if (!properties.Strength || !properties.Radius || !properties.Mode)
   		return std::nullopt;
   	return properties;
   }

   // An optional parameter, read through the property it sets. A value of the wrong type, outside the range or not one of
   // an enum's options is recorded as the first problem of the arguments.
   std::optional<PropertyValue> ReadValue(CommandArguments& arguments, const nlohmann::json& parameters, const char* name, const PropertyInfo& property)
   {
   	if (!arguments.Has(name))
   		return std::nullopt;
   	std::string error;
   	std::optional<PropertyValue> value = PropertyValueFromJson(property, parameters.at(name), &error);
   	if (value && property.Type == PropertyType::Enum && !property.FindEnumValue(std::get<int32_t>(*value)))
   	{
   		error = "is not one of the options";
   		value.reset();
   	}
   	if (value && !property.IsInRange(*value, &error))
   		value.reset();
   	if (!value)
   		arguments.SetError(fmt::format("Parameter '{}' {}", name, error));
   	return value;
   }
   ```

   1. **Lines 36–52:** the properties of the registered component. The function returns nothing when the component is missing, and the handler turns that into an internal error.
   2. **Lines 56–72:** the value of one optional parameter, read through its property. A wrong type, a value outside the range or an unknown option becomes the first problem of the arguments.
   3. **Line 62:** an :term[integer]{id=integer} for the mode is accepted by the :term[parser]{id=parser}, so the helper checks that it is one of the options.
   4. **Line 67:** `IsInRange` writes a message that names the range, such as "must be between 0 and 1000".

   **You should see:** two helpers, the second one built on the first one's properties.

   **If you do not see it:** a handler that compares `strength` with a number written in the command would work now and break when the component's range changes. The reflection is the one place that knows the range.

   **Why:** the Inspector clamps a value that you drag beyond the range, because a slider cannot refuse. A command refuses, because an agent that sends 5000 must learn that its value was not taken, and not find another number in the scene.

3. Write the first half of the handler: read everything, then check everything. Nothing in this half changes the scene.

   ```cpp src="book:tutorials/editor/tutorial-command/WindCommands.cpp#L106-L126"
   [](EditorContext& context, const nlohmann::json& parameters)
   {
   	Scene& scene = *context.GetActiveScene();
   	const std::optional<WindProperties> properties = FindWindProperties();
   	if (!properties)
   		return EditorCommandResult::Fail("The WindZone component is not registered", EditorCommandError::Internal);

   	CommandArguments arguments(parameters);
   	const std::vector<Entity> entities = arguments.GetEntities(scene, "entities");
   	const std::optional<PropertyValue> strength = ReadValue(arguments, parameters, "strength", *properties->Strength);
   	const std::optional<PropertyValue> radius = ReadValue(arguments, parameters, "radius", *properties->Radius);
   	const std::optional<PropertyValue> mode = ReadValue(arguments, parameters, "mode", *properties->Mode);
   	if (!arguments.IsValid())
   		return arguments.Fail();
   	if (!strength && !radius && !mode)
   		return EditorCommandResult::InvalidParameters("Give at least one of 'strength', 'radius' and 'mode'");
   	for (const Entity entity : entities)
   	{
   		if (!entity.HasComponent<WindZoneComponent>())
   			return EditorCommandResult::InvalidParameters(fmt::format("Parameter 'entities': '{}' has no WindZone component", entity.GetName()));
   	}
   ```

   1. **Lines 113–117:** `CommandArguments` reads the array and the three values. Each reader records the first problem and returns a fallback, so the handler does not stop in the middle.
   2. **Lines 118–119:** one check ends the call with `InvalidParameters` if any argument was wrong. Nothing has changed yet.
   3. **Lines 120–121:** a call with no value would be a quiet no-op, so it is refused.
   4. **Lines 122–126:** an entity without a `WindZone` is refused by name. The check runs for every entity before the first write.

   **You should see:** every way a call can fail ends in a `return` before line 128.

   **If you do not see it:** a check that sits inside the loop that writes would leave the first zones changed when the third fails. That is the half-applied state that the rule forbids.

4. Write the second half: one transaction over every entity, the writes, the signal and `FinishEdit`.

   ```cpp src="book:tutorials/editor/tutorial-command/WindCommands.cpp#L128-L153"
   	// Everything is checked: from here on the command changes the scene.
   	std::vector<UUID> ids;
   	std::unordered_set<UUID> seen;
   	for (const Entity entity : entities)
   	{
   		if (seen.insert(entity.GetUUID()).second)
   			ids.push_back(entity.GetUUID());
   	}
   	SceneEditTransaction transaction(scene, ids.size() == 1 ? fmt::format("Set the wind of {}", SceneEdit::QuoteName(entities.front().GetName())) :
   		fmt::format("Set the wind of {} entities", ids.size()), ids);
   	nlohmann::json changed = nlohmann::json::array();
   	for (const UUID id : ids)
   	{
   		Entity entity = scene.GetEntityByUUID(id);
   		WindZoneComponent& zone = entity.GetComponent<WindZoneComponent>();
   		if (strength)
   			zone.Strength = std::get<float>(*strength);
   		if (radius)
   			zone.Radius = std::get<float>(*radius);
   		if (mode)
   			zone.Mode = static_cast<WindZoneMode>(std::get<int32_t>(*mode));
   		entity.MarkModified<WindZoneComponent>();
   		changed.push_back(UUIDToJson(id));
   	}
   	return FinishEdit(context, transaction, { { "entities", std::move(changed) } });
   } });
   ```

   1. **Lines 129–135:** each entity once, because a caller may list an ID twice, and `entity.delete` keeps each entity once for the same reason.
   2. **Lines 136–137:** the name of the undo step, which the History shows: "Set the wind of Breeze" for one entity, "Set the wind of 2 entities" for two.
   3. **Lines 143–148:** only the values that the call gave are written; the others stay.
   4. **Line 149:** `MarkModified` tells the scene that the component changed, as the rule for component writes demands.
   5. **Line 152:** `FinishEdit` commits the transaction and records the step. While the game plays, it adds the warning about the running copy.

   **You should see:** the transaction is made after the last check and before the first write.

   **If you do not see it:** a transaction records a step only for the entities it tracks, so a call that tracks none leaves `edit.undo` nothing to undo. The list of IDs is what makes the step.

   **Why:** `SceneEditTransaction` stores the "before" state of the tracked entities when it is made and compares it with the "after" state at the commit. Making it after the checks means a refused call never opens one, and a transaction without a change records nothing.

5. List `wind.set` among the edits in the test of kinds, build and run the suite.

   ```diff src="book:tutorials/editor/tutorial-command.patch#hunk-5"
    		"scene.loadAdditive", "scene.new", "scene.open", "scene.save", "scene.saveAs", "scene.setSettings", "scene.unloadAdditive",
    		"script.add", "script.build", "script.create", "script.init", "script.load", "script.reload", "script.remove", "script.setField",
    		"ui.create",
   +		"wind.set",
    		"world.cook", "world.create", "world.moveEntities", "world.setLayers",
    	};
    	constexpr std::string_view c_QueryCommands[] = {
   ```

   **You should see:** the name between `ui.create` and `world.cook`, a build without warnings and a passing `Editor.Journal`.

   **If you do not see it:** the test fails when the kind in a registration and the list that holds its name disagree. `wind.set` needs no kind in its registration, because `Edit` is the default; say it only when you want to.

:::::

The command follows the conventions of `entity.rename`, which you can read beside it. Its handler reads its arguments, validates, opens a transaction, writes, signals and finishes, in the same order.

```cpp src="StrataEditor/src/Editor/Commands/EntityCommands.cpp#L514-L528" command="entity.rename"
registry.Register({ "entity.rename", "Renames an entity (undoable; while playing it changes the running copy only). Returns {entity, name}.",
	ObjectSchema({ { "entity", EntitySchema("Entity") }, { "name", StringSchema("New name") } }, { "entity", "name" }),
	[](EditorContext& context, const nlohmann::json& parameters)
	{
		Scene& scene = *context.GetActiveScene();
		CommandArguments arguments(parameters);
		Entity entity = arguments.GetEntity(scene, "entity");
		const std::string name = arguments.GetString("name");
		if (!arguments.IsValid())
			return arguments.Fail();
		SceneEditTransaction transaction(scene, fmt::format("Rename {} to {}", SceneEdit::QuoteName(entity.GetName()), SceneEdit::QuoteName(name)), { entity.GetUUID() });
		entity.GetComponent<NameComponent>().Name = name;
		entity.MarkModified<NameComponent>();
		return FinishEdit(context, transaction, { { "entity", UUIDToJson(entity.GetUUID()) }, { "name", name } });
	} });
```

1. **Lines 514–515:** the name, a description written for agents, and the schema with its required names.
2. **Lines 519–523:** both arguments are read, then one check ends the call before anything changes.
3. **Line 524:** the transaction tracks the entity and names the step.
4. **Lines 525–526:** the write, then the signal that the name changed.
5. **Line 527:** `FinishEdit` records the step.

The two handlers differ in size, not in shape. `entity.rename` has one entity and one value. `wind.set` has a list of entities and three :term[optional values]{id=optional-value}, so it needs a loop and a helper to read values.

:::rule[Every change goes through a command]
The rule is in the engine's guide for its developers: every change to the scene or the project goes through a command, so that the interface, agents and tests all do the same thing. The command also gives the change one undo step and one entry in the activity journal. See [commands](commands.md) for the full list of conventions.
:::

## Test the commands

Golden rule 2 of the engine says that new behavior ships with tests. The sentences of the introduction are the first three cases, and the running copy is the fourth. You write them in a new file, and the file needs a harness, because a command runs inside an editor context.

:::::steps

1. Create the new file `EditorWindCommandTests.cpp` in the folder `StrataTests/src/Editor/`, with the harness. It owns an `EditorContext` and a registry, runs a command to the end, and makes a zone straight in the scene so that no undo step records its creation.

   ```cpp src="book:tutorials/editor/tutorial-command/EditorWindCommandTests.cpp#L19-L59"
   namespace
   {

   	struct WindHarness
   	{
   		EditorContext Context;
   		EditorCommandRegistry Commands;

   		EditorCommandResult Execute(std::string_view name, const nlohmann::json& parameters = nlohmann::json::object())
   		{
   			return Tests::CompleteCommand(Context, Commands.Execute(Context, name, parameters));
   		}

   		Scene& GetScene() { return *Context.GetActiveScene(); }

   		// A zone made directly in the scene: no undo step records it.
   		Entity AddZone(const char* name, float strength, float radius)
   		{
   			Entity zone = GetScene().CreateEntity(name);
   			WindZoneComponent& wind = zone.AddComponent<WindZoneComponent>();
   			wind.Strength = strength;
   			wind.Radius = radius;
   			return zone;
   		}

   		// A JSON array of entity IDs, as the entities parameter takes them.
   		static nlohmann::json Ids(std::initializer_list<UUID> ids)
   		{
   			nlohmann::json array = nlohmann::json::array();
   			for (const UUID id : ids)
   				array.push_back(UUIDToJson(id));
   			return array;
   		}

   		const WindZoneComponent& Wind(UUID id)
   		{
   			return GetScene().GetEntityByUUID(id).GetComponent<WindZoneComponent>();
   		}
   	};

   }
   ```

   1. **Lines 24–25:** a context without a project has an empty scene, and the registry has every command, including yours.
   2. **Lines 27–30:** `CompleteCommand` waits for a command that answers in a later frame; yours answers at once.
   3. **Lines 35–42:** a zone made through the scene. The test setup is not an edit of the editor, so the history stays empty.
   4. **Lines 45–51:** the entities parameter as a :term[JSON array]{id=json-array}, built from IDs.

   **You should see:** a :term[struct]{id=struct} and no test yet.

   **If you do not see it:** the file is part of the build only after you configure again. Run `cmake --preset <preset>` once more after saving it.

2. Test the query with the zones of the introduction. The test also adds an entity without a zone, which must not appear, and checks that nothing was recorded.

   ```cpp src="book:tutorials/editor/tutorial-command/EditorWindCommandTests.cpp#L61-L90"
   TEST_SUITE("Editor.WindCommands")
   {
   	TEST_CASE("wind.list answers every zone with its values, and changes nothing")
   	{
   		WindHarness harness;
   		const Entity breeze = harness.AddZone("Breeze", 10.0f, 5.0f);
   		harness.AddZone("Gust", 25.0f, 8.5f);
   		harness.GetScene().CreateEntity("Rock");

   		const EditorCommandResult result = harness.Execute("wind.list");
   		REQUIRE(result.Success);
   		const nlohmann::json& zones = result.Value["zones"];
   		REQUIRE(zones.size() == 2);
   		for (const nlohmann::json& zone : zones)
   		{
   			CAPTURE(zone);
   			if (zone["name"] == "Breeze")
   			{
   				CHECK(zone["entity"] == UUIDToJson(breeze.GetUUID()));
   				CHECK(zone["strength"] == 10.0);
   				CHECK(zone["mode"] == "Directional");
   			}
   			else
   			{
   				CHECK(zone["name"] == "Gust");
   				CHECK(zone["radius"] == 8.5);
   			}
   		}
   		CHECK_FALSE(harness.Execute("edit.undo").Success);
   	}
   ```

   1. **Lines 66–68:** two zones and a rock.
   2. **Lines 72–73:** the rock is not listed, so two zones are in the answer.
   3. **Lines 77–82:** the Breeze keeps its ID, its 10 N and its mode `Directional`.
   4. **Line 89:** a query leaves no undo step, so `edit.undo` fails.

   **You should see:** a test of 28 lines with a name that states the behavior.

   **If you do not see it:** if the loop compares `zone["strength"]` with `10` and the test fails, check that the numbers in your handler come from the component, not from literals.

3. Test the edit with the numbers of the introduction: both zones at 40 N and `Spherical`, the radii kept, one undo that restores everything, and no second step.

   ```cpp src="book:tutorials/editor/tutorial-command/EditorWindCommandTests.cpp#L92-L116"
   TEST_CASE("wind.set changes several zones in one undo step")
   {
   	WindHarness harness;
   	const UUID breeze = harness.AddZone("Breeze", 10.0f, 5.0f).GetUUID();
   	const UUID gust = harness.AddZone("Gust", 25.0f, 8.5f).GetUUID();

   	const EditorCommandResult result = harness.Execute("wind.set", { { "entities", WindHarness::Ids({ breeze, gust }) },
   		{ "strength", 40.0 }, { "mode", "Spherical" } });
   	REQUIRE(result.Success);
   	CHECK(result.Value["entities"].size() == 2);
   	for (const UUID id : { breeze, gust })
   	{
   		CHECK(harness.Wind(id).Strength == doctest::Approx(40.0f));
   		CHECK(harness.Wind(id).Mode == WindZoneMode::Spherical);
   	}
   	CHECK(harness.Wind(breeze).Radius == doctest::Approx(5.0f)); // Left out: unchanged
   	CHECK(harness.Wind(gust).Radius == doctest::Approx(8.5f));

   	REQUIRE(harness.Execute("edit.undo").Success);
   	CHECK(harness.Wind(breeze).Strength == doctest::Approx(10.0f));
   	CHECK(harness.Wind(gust).Strength == doctest::Approx(25.0f));
   	CHECK(harness.Wind(gust).Mode == WindZoneMode::Directional);
   	// One step held both zones: nothing is left to undo.
   	CHECK_FALSE(harness.Execute("edit.undo").Success);
   }
   ```

   1. **Lines 98–99:** one call with both zones, a strength and a mode, and no radius.
   2. **Lines 102–108:** both zones have 40 N and the mode `Spherical`; the radii are as before.
   3. **Lines 110–113:** one `edit.undo` restores 10 N, 25 N and `Directional`.
   4. **Line 115:** the second `edit.undo` fails, which proves that the call made one step, not two.

   **You should see:** the second undo is the line that tells one step from two.

   **If you do not see it:** if the second undo succeeds, the command made one transaction for each entity. The transaction has to be one object for the whole list.

4. Test the refusals. Each refused call must fail with `InvalidParameters`, and afterwards the zone must be as before and the history empty.

   ```cpp src="book:tutorials/editor/tutorial-command/EditorWindCommandTests.cpp#L118-L144"
   TEST_CASE("wind.set refuses invalid input and changes nothing")
   {
   	WindHarness harness;
   	const UUID breeze = harness.AddZone("Breeze", 10.0f, 5.0f).GetUUID();
   	const UUID rock = harness.GetScene().CreateEntity("Rock").GetUUID();
   	const nlohmann::json one = WindHarness::Ids({ breeze });
   	const nlohmann::json both = WindHarness::Ids({ breeze, rock });

   	const auto refused = [&harness](const nlohmann::json& parameters)
   	{
   		CAPTURE(parameters);
   		const EditorCommandResult result = harness.Execute("wind.set", parameters);
   		CHECK_FALSE(result.Success);
   		CHECK(result.ErrorKind == EditorCommandError::InvalidParameters);
   	};
   	refused({ { "entities", one }, { "strength", 5000.0 } });                  // Above the range
   	refused({ { "entities", one }, { "strength", 20.0 }, { "radius", 0.0 } });  // The second value is invalid
   	refused({ { "entities", one }, { "mode", "Sideways" } });                  // Not an option
   	refused({ { "entities", one }, { "strength", "strong" } });                // Not a number
   	refused({ { "entities", one } });                                          // No value to set
   	refused({ { "entities", both }, { "strength", 20.0 } });                   // One entity has no zone
   	refused({ { "strength", 20.0 } });                                         // No entities

   	CHECK(harness.Wind(breeze).Strength == doctest::Approx(10.0f));
   	CHECK(harness.Wind(breeze).Radius == doctest::Approx(5.0f));
   	CHECK_FALSE(harness.Execute("edit.undo").Success);
   }
   ```

   1. **Lines 126–132:** one small function runs a call and checks the failure and its kind.
   2. **Lines 133–139:** seven bad calls. A strength of 5000 is above the range, and a radius of 0 in the second call is below it. `Sideways` is no option, and `strong` is no number. The last three give no value, an entity without a zone, and no entities.
   3. **Lines 141–143:** after all seven calls the Breeze is as it was and the history is empty.

   **You should see:** the second call carries a good strength and a bad radius. A command that applied values one by one would leave the 20 N in the scene.

   **If you do not see it:** if the Breeze shows 20 N afterwards, the checks run after the first write. Move them before it.

5. Test the running copy. While the game plays, an edit changes the copy and says so; stopping the game throws the copy away.

   ```cpp src="book:tutorials/editor/tutorial-command/EditorWindCommandTests.cpp#L146-L161"
   TEST_CASE("wind.set while playing changes the running copy and says so")
   {
   	WindHarness harness;
   	const UUID breeze = harness.AddZone("Breeze", 10.0f, 5.0f).GetUUID();
   	REQUIRE(harness.Execute("play.start").Success);

   	const EditorCommandResult result = harness.Execute("wind.set", { { "entities", WindHarness::Ids({ breeze }) },
   		{ "strength", 40.0 } });
   	REQUIRE(result.Success);
   	CHECK(result.RunningCopy);
   	CHECK(result.Value.contains("warning"));
   	CHECK(harness.Wind(breeze).Strength == doctest::Approx(40.0f));

   	REQUIRE(harness.Execute("play.stop").Success);
   	CHECK(harness.Wind(breeze).Strength == doctest::Approx(10.0f));
   }
   ```

   1. **Line 150:** `play.start` makes the running copy of the scene.
   2. **Lines 155–157:** the result is flagged `RunningCopy`, holds a `warning`, and the copy shows 40 N.
   3. **Lines 159–160:** after `play.stop` the edited scene still has 10 N.

   **You should see:** three claims about one call: the flag, the warning and the discarded change.

   **If you do not see it:** if the result has no warning, the handler ends without `FinishEdit`. In this handler, it is the function that adds the warning.

6. Configure again, build, and run the new suite.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Editor.WindCommands
   ```

   **You should see:** the four test cases pass and no case fails.

   **If you do not see it:** read the first failed check and the `CAPTURE` lines above it; they print the parameters of the call that failed.

7. Prove that the refusals test guards something. Comment out the range check in `ReadValue`, the two lines that read `if (value && !property.IsInRange(*value, &error))` and `value.reset();`. Build and run the suite again, then put the lines back.

   **You should see:** `wind.set refuses invalid input and changes nothing` fails, because the 5000 N call succeeds and the zone changes.

   **If you do not see it:** if the suite still passes, the build did not rebuild the :term[editor core]{id=editor-core}. Run the build once more and read its last line before you trust the result.

:::::

The suite now holds the sentences of the introduction. A test that has never failed has not proved that it can; the last step made it fail once, for the reason it exists.

:::note[Why the tests use no mouse]
Every test of this suite runs through the registry, as a client would. A test that clicked in the Inspector would be slow and would hide the thing under test. Because the editor's panels call the same commands, the tests also cover what the panels do when they use them.
:::

## Run the commands from a terminal

The last section runs your commands in a real editor. This is the proof that you have an interface for people and agents, not only a function that a test calls. Every step here has no menu or button: it is a call from the terminal.

:::::steps

1. This step has no menu or button: run the command. Start an editor with your project and no window. It waits until the project is ready and prints its progress.

   ```sh
   build/<preset>/bin/Debug/StrataCLI launch --headless --project <project>
   ```

   **You should see:** the command returns when the project's assets are scanned and its start scene is open.

   **If you do not see it:** if `StrataCLI` reports that the editor failed to launch, no `StrataEditor` stands beside `StrataCLI`. Build everything once more, or name the editor with `--editor <path>`.

2. This step has no menu or button: run the command. Create the two zones. The call reads its parameters from a file, because quotes in JSON are error-prone in a shell. Write `breeze.json` and `gust.json`, then call `entity.create` with each.

   ```json
   { "name": "Breeze", "components": { "WindZone": { "Strength": 10, "Radius": 5 } } }
   ```

   The second file has the name `Gust`, a strength of 25 and a radius of 8.5. The calls are `StrataCLI call entity.create @breeze.json --project <project>` and the same for `gust.json`.

   **You should see:** each call answers with the ID of the new entity.

   **If you do not see it:** an error that names the component means the editor does not know `WindZone`: it was built before the component tutorial. Build again and restart it.

3. This step has no menu or button: run the command. Ask for the zones. The command needs no parameters, so the call is short.

   ```sh
   build/<preset>/bin/Debug/StrataCLI call wind.list --project <project>
   ```

   **You should see:** an object with the key `zones` that holds two objects. Each one has `entity`, `name`, `active`, `strength`, `radius` and `mode`: the Breeze with 10 and 5, the Gust with 25 and 8.5, both `Directional`. Note the two values of `entity`.

   **If you do not see it:** an answer with an empty list means the zones were created in another editor. Pass `--project` on every call, as here, so that the client does not pick the newest editor.

4. This step has no menu or button: run the command. Set both zones in one call. Write `wind.json` and replace the two placeholders with the IDs from the last answer.

   ```json
   { "entities": [ "<the Breeze's entity>", "<the Gust's entity>" ], "strength": 40, "mode": "Spherical" }
   ```

   Then run `StrataCLI call wind.set @wind.json --project <project>`, and `wind.list` again.

   **You should see:** `wind.set` answers with the two IDs. The list now shows 40 for both zones and `Spherical`, with the radii 5 and 8.5.

   **If you do not see it:** an error with the text `no entity` and an ID means a placeholder is still in the file or an ID has a wrong letter.

5. This step has no menu or button: run the command. Try a call that must fail: change the strength in `wind.json` to 5000 and call `wind.set` again.

   **You should see:** an error that says that the parameter `strength` must be between 0 and 1000, and a non-zero :term[exit code]{id=exit-code}. The list still shows 40.

   **If you do not see it:** if the zones changed, the range check that you commented out in the section on tests is still out. Put it back and build.

6. This step has no menu or button: run the command. Undo the edit and read the journal. The first call is the one you know; the second asks for the latest entries of the group.

   ```sh
   build/<preset>/bin/Debug/StrataCLI call edit.undo --project <project>
   build/<preset>/bin/Debug/StrataCLI call editor.activity '{"command":"wind.","newest":true}' --project <project>
   ```

   **You should see:** after the undo, a call of `wind.list` shows 10 and 25 and `Directional` again. The journal answers newest first, so the failed `wind.set` comes before the good one, with its error as its `summary`. The good `wind.set` has `mutating` true and the `summary` "Set the wind of 2 entities", the name of its undo step. The `wind.list` calls, one of them between the two, have `mutating` false.

   The source of each entry is `Automation`.

   **If you do not see it:** on Windows the single quotes of the second call may not reach the program as you wrote them. Put the JSON in a file and pass `@activity.json`, as in the earlier steps.

   **Why:** the `mutating` flag is the kind at work. The journal sets it for every `Edit` call, the failed one too, and leaves it false for the `Query`. A replay reads the same kind to decide what to repeat.

7. This step has no menu or button: run the command. Stop the editor.

   ```sh
   build/<preset>/bin/Debug/StrataCLI call editor.quit --project <project>
   ```

   **You should see:** the editor ends and the command returns.

   **If you do not see it:** a headless editor runs until it is told to stop. Use `editor.quit` or end the process.

:::::

You have a complete command pair. Two tests guard its place, a suite proves its behavior, and the editor serves it to a terminal. The same two commands are what an agent finds in the `world` toolset of [the MCP server](../automation/mcp.md). A game that relies on a command goes one step further, and [the feature test page](../engineering/feature-test.md) shows how it keeps that command exercised. A command that waits for frames needs [deferred commands](deferred-commands.md).

## Summary

- You named the three places of a new group: the call in the registry's constructor, the list of kinds in the journal test and the row of the toolset table. You predicted which test fails for each.
- You wrote `wind.list` as a Query with a complete schema and an answer that holds IDs and values.
- You wrote `wind.set` so that every input is checked before one transaction changes anything, the change is signaled and `FinishEdit` ends the call.
- You tested success, one undo step, refusals without side effects and the running copy, and made the refusals test fail once on purpose.
- You ran the commands from a terminal, undid the edit and read the journal entries.

## Check yourself

1. You add `RegisterWindCommands` and the file, build, and run all tests. Which two suites fail, and what does each one want?

   :::answer{tests="command-home"}
   `Editor.Journal` fails because no list of kinds names `wind.list`: it wants the command in exactly one list and its registered kind to match. `CLI.McpToolsets` fails because the prefix `wind.` is in no row of the toolset table: it wants a row that maps the prefix to a set. The second one runs only when the tests are built with the command-line client.
   :::

2. Why does `wind.list` declare the kind `Query` and not leave the default?

   :::answer{tests="query-command"}
   A command without a kind counts as an edit, so a replay of a session would repeat the listing and the journal would mark it as `mutating`. The kind says that the call changes nothing. The test of kinds also fails for a command that is in the list of queries but registered with the default.
   :::

3. A call lists the Breeze, the Gust and a rock, with a good strength of 20 N. What happens, and why does it matter that the check does not sit inside the writing loop?

   :::answer{tests="edit-command"}
   The call fails with `InvalidParameters`, because the rock has no `WindZone`, and no zone changes. The check runs for every entity before the transaction is made. If the check sat in the loop that writes, the Breeze and the Gust might be at 20 N when the rock stops the call, and no undo step would describe that scene.
   :::

4. The test of one undo step calls `edit.undo` twice. What does the second call prove?

   :::answer{tests="command-tests"}
   The second call fails because the history holds nothing. If `wind.set` made one transaction for each zone, the first undo would restore only the last zone and the second would succeed. A failing second undo shows that one call made one step.
   :::

5. In the journal, `wind.list` has `mutating` false and `wind.set` has `mutating` true. Where does the flag come from?

   :::answer{tests="run-command"}
   The journal derives it from the command's kind: `Edit` sets the flag, `Query` does not, and a call that changed the running copy sets it as well. A replay of the session reads the same kind to decide what to repeat, so the kind in the registration decides what it does.
   :::

## Exercises

1. **Basic.** Change the kind of `wind.list` in its registration to `Edit`, without changing the lists. Predict which test fails and with what message, then check it. Put the kind back.

   Hint: the test compares the registered kind with the list that holds the name.

   :::answer{tests="command-home query-command" }
   `Editor.Journal` fails on the check that the registered kind equals the kind of the list. The name is in the list of queries, so the test expects `Query` and finds `Edit`. The command-line toolsets are not affected, because they sort by prefix and not by kind. The case shows that the list and the registration are two copies of one decision, and the test keeps them equal.
   :::

2. **Medium.** Add `wind.reset`, an edit that sets the strength, the radius and the mode of the given zones back to the component's defaults in one undo step. Write its test with the numbers of this page.

   Hint: the defaults are the values of a fresh `WindZoneComponent`; build one and read its fields.

   :::answer{tests="edit-command command-tests"}
   Register the command in the same function with the schema `entities` only and the kind `Edit`, and add it to the list of edits. In the handler, read the entities, refuse a missing component, make one transaction over the IDs, assign `WindZoneComponent()` to each component and call `MarkModified`, then `FinishEdit`. The test sets the Breeze and the Gust to 40 N, calls `wind.reset`, expects 10 N and a radius of 5 m on both, undoes once and expects 40 N again.
   :::

3. **Hard.** Make `wind.set` name every entity without a `WindZone` in the data of its error, so that a client can fix the whole call at once. Check it with a test that lists two bad entities.

   Hint: `EditorCommandResult::Fail` has a form with a JSON value for the error's data.

   :::answer{tests="edit-command command-tests" solution="tutorials/editor/tutorial-command/exercise-3.patch"}
   The solution collects every entity without the component into a JSON array of IDs and names, and fails once with `InvalidParameters` and that array as the error's data. The test makes the Breeze, a rock and a lamp, calls with all three and expects two entries in `withoutWindZone`, in the order of the call. The Breeze keeps its 10 N, so the refusal still has no side effect.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorCommands.h` and `EditorCommands.cpp`: `EditorCommand`, the kinds, `CommandArguments` and the registry's constructor with one call for each group.
- `StrataEditor/src/Editor/CommandUtils.h`: `ObjectSchema` and the other schema helpers, `FinishEdit`, `RollBackEdit` and the warning of the running copy.
- `StrataEditor/src/Editor/SceneEdit.h`: `SceneEditTransaction`, which records one undo step for the entities it tracks.
- `StrataEditor/src/Editor/Commands/EntityCommands.cpp`: `entity.rename`, the model of a command that changes the scene.
- `StrataTests/src/Editor/CommandJournalTests.cpp`: the lists of kinds and the test that every command is in one.
- `StrataCLI/src/CLI/McpToolsets.cpp`: the table from a command's prefix to its toolset.
- `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp`: `CLI.McpToolsets`, the check that every command is in a toolset.

## Further reading

- The doctest documentation on `CAPTURE` and `REQUIRE` (github.com/doctest/doctest): what the context lines of a failed check print: beginner.
- The JSON Schema specification (json-schema.org): how a schema describes an object with required and optional properties: intermediate.
- Martin Fowler, "Command Query Separation": why a function either changes state or answers, never both: intermediate.
