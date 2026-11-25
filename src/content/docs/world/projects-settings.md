---
id: world/projects-settings
title: "Projects and settings"
description: "How a project file is read and written, and how modules register settings sections that are stored, checked, versioned and handed to scenes."
kind: internals
size: L
tracks: [E]
needs: [world/systems, world/reflection, core/files]
time: 100
learn:
  - id: file
    text: explain how Project::Load reads a project file, what it refuses and what it keeps as read
  - id: section
    text: write a simple settings section with fields, defaults and a version, and choose when a complex section is needed
  - id: upgrade
    text: predict what validation returns for stored values of version 1, 2 and 3 of a section
  - id: handover
    text: explain why scenes built on worker threads never read the project's settings and when the main thread applies them
  - id: trace
    text: trace a change of the fixed rate from the command to the running scene and compute the steps its cap allows
since: 0.3.0
status: final
---

A game is more than its scenes and assets. The engine must also keep the facts that belong to the whole game: its name, where its assets live, which scene starts and how fast the simulation steps. Strata keeps them in a project: a folder with one project file, an asset folder, a script folder and a folder of working files. This page teaches how the project file is read and written, and how modules register settings that are stored, checked, upgraded and handed to scenes. The game's manifest and identity, the project folder as a game maker uses it, and the windows that draw settings belong to other pages.

## The problem and how engines solve it

Take three numbers that a game maker wants to change: the physics steps per second, the strength of gravity and the quality of the picture. Where do they live? The first answer is constants in code. The physics code says `60`, and a change means editing code and building again. The editor has no description of such a number to draw a field from, and an agent cannot ask which numbers exist.

The second answer is a file that each module reads in its own way. The physics module finds its numbers in the project file and reads them by hand, and so does the :term[renderer]{id=renderer}. Suppose a newer Strata saved a project with a section Game.Tuning at version 3, holding a field `Wave` that your build has never heard of. A hand-written reader takes the four fields it knows. When the maker changes the start scene, the build writes the file from what it understood, and `Wave` is gone with three hours of tuning.

The third answer is **registered data**. Each module describes its settings once: the name of each field, its type, its range, its default and a text for people.

The engine then checks every value and fills the defaults. It writes a JSON Schema (a :term[JSON]{id=json} text that says which values are allowed) for agents, draws a settings page and keeps what it does not understand. The cost is a fixed set of field types and a registry that freezes at startup. A group that does not fit the fields must bring its own reading function.

Two more questions decide where a value is stored. The steps per second belong to the game: they are committed with the project and travel into the exported game. Strata calls this **project scope**.

The size of the editor's font belongs to the person: it must not be committed and must not ship. That is **user scope**, and the editor keeps it in the person's preferences.

:::elsewhere
Godot keeps project settings in one text file, Unreal Engine reads layered `.ini` files, where a later layer overrides an earlier one, and Unity keeps asset files in a `ProjectSettings` folder. Strata sits nearest to Godot, but adds a registered description for every group of values.
:::

A **settings section** is one group of settings, registered by the module that owns it, with an id, a scope, a version and a way to check its value. `Renderer.Quality` is one: the renderer registers it, the project stores its value and the renderer reads it back. Each section has an id of the form `<Module>.<Name>`, so two modules never collide.

## The map

A setting passes through several places before a scene sees it. Modules register sections into one process registry, and the engine freezes that registry. The project file's `Settings` object is read and checked against it. The checked values wait behind a service, and a reader in a module asks the service when its version changes. A scene takes the result.

```mermaid caption="How a setting travels from a module's registration through the project file and a service to the scene." alt="A flow of seven boxes. Module registration fills a frozen registry. The project file's settings are checked against the registry. The checked values are offered by a service. A section reader asks the service and a scene takes what the reader made."
flowchart LR
    REG["Module registration"] --> RF["Frozen settings registry"]
    PF["Project file: Settings"] --> VAL["Checked values"]
    RF --> VAL
    VAL --> SVC["Service: IProjectSettings"]
    SVC --> RD["Section reader with a cache"]
    RD --> SC["Scene, on the main thread"]
```

Each part has one owner. The modules own their sections' descriptions. `Project` owns the file: it reads and writes `.stproj`, and holds a `ProjectSettingsValues` object with every stored section. The program owns the service: the editor provides it while a project is open, and the game :term[runtime]{id=runtime} provides it from its manifest. The scene owns nothing of the project; it only takes the numbers it needs, on the :term[main thread]{id=main-thread}.

## The contract

The rules below are what a module may assume and what it must do. Each has a reason.

1. **Register during module registration, once, under a valid id.** The id is two names that start with a capital, joined by a dot, at most 64 :term[bytes]{id=byte}. A section registers before the registry freezes; after that the registry never changes, and any thread may read it. A refused registration logs an error and the section does not exist.
2. **Check every value through `SettingsSection::Validate`.** Values come from files and from agents, and both are wrong sometimes. One check means one answer, one error message and one upgrade path for every caller.
3. **Never assert on a settings value.** A bad value is a failure you return and log. The engine must keep running with the default.
4. **Read the service on the main thread, and keep what you made of it until `GetVersion` changes.** Like every :term[engine service]{id=scene-service}, `IProjectSettings` belongs to the main thread. A cache keyed by version makes the read free on every frame that nothing changed.
5. **Keep what you do not understand.** Sections no module claims, sections their owner refuses and members of the project file from a later version are written back as read.
6. **A version only grows.** A value of an older version is upgraded; a value of a newer one is refused, never guessed.
7. **Scenes built on worker threads never read the service.** The main thread applies the project's values when it takes the scene.

:::rule[Read settings on the main thread, check only through Validate]
A module reads `IProjectSettings` on the main thread only, caches by version, validates only through `SettingsSection::Validate` and never asserts on a value from a file or an agent. A second reader of the same text would disagree with the first, and a worker thread would read a value that is changing.
:::

:::rule[Keep unknown data]
Sections that no module claims and members of the project file that this version does not know are written back as read. A build without the module, or an older engine, would otherwise erase data that it cannot read.
:::

## A toy version

The toy below has the whole idea in plain C++: sections made of whole-number fields, a version for each section, one check, and a table of stored entries that keeps every entry as read. It uses a map of names to numbers instead of :term[JSON]{id=json}, but the steps are the engine's. Notice what happens to the three stored entries: one is upgraded, one is refused and kept, and one belongs to nobody.

```cpp sketch="world-projects-settings-toy.cpp"
// A toy of project settings: sections of whole-number fields with versions, and stored values that are kept as read.
#include <cstdio>
#include <map>
#include <optional>
#include <string>
#include <vector>

using Value = std::map<std::string, int>;

struct Field
{
	std::string Name;
	int Min = 0;
	int Max = 0;
	int Default = 0;
};

struct Section
{
	std::string Id;
	unsigned Version = 1;
	std::vector<Field> Fields;
};

// The single validation: the version first, then each field in order. The first problem is the reason.
std::optional<Value> ValidateValue(const Section& section, const Value& stored, unsigned version, std::string& error)
{
	if (version == 0 || version > section.Version)
	{
		error = "version " + std::to_string(version) + " is newer than this build reads";
		return std::nullopt;
	}
	Value result;
	for (const Field& field : section.Fields)
	{
		const auto found = stored.find(field.Name);
		if (found == stored.end())
		{
			result[field.Name] = field.Default; // A field added since the stored version
			continue;
		}
		if (found->second < field.Min || found->second > field.Max)
		{
			error = field.Name + " must be from " + std::to_string(field.Min) + " to " + std::to_string(field.Max);
			return std::nullopt;
		}
		result[field.Name] = found->second;
	}
	return result;
}

struct Entry
{
	unsigned Version = 1;
	Value Stored;
	bool Valid = false;
};

// What a project keeps: every stored section, valid or not.
struct Values
{
	std::map<std::string, Entry> Entries;
	std::vector<std::string> Validate(const std::vector<Section>& registry)
	{
		std::vector<std::string> problems;
		for (auto& [id, entry] : Entries)
		{
			const Section* section = nullptr;
			for (const Section& candidate : registry)
			{
				if (candidate.Id == id)
					section = &candidate;
			}
			std::string error;
			std::optional<Value> value;
			if (section)
				value = ValidateValue(*section, entry.Stored, entry.Version, error);
			if (!value)
			{
				if (section) // A section nobody claims is kept silently
					problems.push_back(id + ": " + error);
				continue; // Kept as stored: written back unchanged, its default applies
			}
			entry.Stored = *value;
			entry.Version = section->Version;
			entry.Valid = true;
		}
		return problems;
	}
};

int main()
{
	const std::vector<Section> registry = {
		{ "Game.Tuning", 2, { { "MaxEnemies", 1, 50, 10 }, { "SpawnDelay", 0, 10, 2 } } },
		{ "Game.Audio", 1, { { "Volume", 0, 10, 5 } } } };

	Values values;
	values.Entries["Game.Tuning"] = { 1, { { "MaxEnemies", 20 } }, false };
	values.Entries["Game.Audio"] = { 1, { { "Volume", 99 } }, false };
	values.Entries["Fan.Bonus"] = { 1, { { "Level", 3 } }, false };

	for (const std::string& problem : values.Validate(registry))
		std::printf("refused %s\n", problem.c_str());
	for (const auto& [id, entry] : values.Entries)
	{
		std::printf("%s v%u %s:", id.c_str(), entry.Version, entry.Valid ? "provided" : "kept");
		for (const auto& [name, number] : entry.Stored)
			std::printf(" %s=%d", name.c_str(), number);
		std::printf("\n");
	}
	return 0;
}
```

1. **Lines 26–50:** `ValidateValue` checks the version first, then walks the fields in order. A missing field takes its default, which is how a field added in a later version reaches an old value.
2. **Lines 52–57:** an `Entry` keeps the version it was stored at, the stored numbers as read and a flag that says whether a registry accepted it.
3. **Lines 78–83:** `Validate` visits every stored entry, and here a refused entry keeps its stored numbers with the flag false. An entry that no section claims is kept without a message.
4. **Lines 84–86:** an accepted entry is replaced by the checked value at the section's version, so the next save writes it upgraded.

The program prints this.

```text output-of="world-projects-settings-toy.cpp"
refused Game.Audio: Volume must be from 0 to 10
Fan.Bonus v1 kept: Level=3
Game.Audio v1 kept: Volume=99
Game.Tuning v2 provided: MaxEnemies=20 SpawnDelay=2
```

Game.Tuning was stored at version 1 with only `MaxEnemies`. The section is at version 2, so the value becomes version 2 with `SpawnDelay` at its default of 2. Game.Audio holds `Volume=99`, outside 0 to 10: the section reports why, the entry stays at 99 and the default applies. Fan.Bonus is no registered section, so it stays unchanged and silent. The real code omits none of this and adds a size cap, field types, complex sections, user scope, JSON and versions that are unique across the process.

## The project file

A project is a folder, and the folder's heart is one file named after the project. `Project::Create` makes the asset folder and `.strata/Cache`. The editor's `EditorContext::CreateProject` then writes `Scripts/` with an example script, and the other :term[working folders]{id=current-folder} appear as the editor builds and plays.

:::files[A project folder named Coin Run]

- `Coin Run/` the project's folder
  - `Assets/` every asset, each with a `.meta` file beside it
  - `Scripts/` the script sources, with their `CMakeLists.txt`
  - `.strata/` the folder of working files, never committed
    - `Cache/` the imported assets
    - `Scripts/Build/` the :term[CMake]{id=cmake} build tree of the script module
    - `Scripts/Bin/` the built script module that the editor loads
    - `Saves/` the save files of the editor's play mode
  - `Coin Run.stproj` the project file
  - `.gitignore` written by `Project::Create`, naming `/.strata/`

:::

The folder `.strata/` holds what the engine can rebuild from the rest: caches, builds and play-mode saves. :term[Version control]{id=version-control} must not carry it, which is why `Create` writes a `.gitignore` for it. The rest of the folder is the project proper, and a person commits it.

`Project::Create` makes the asset folder, `.strata/Cache` and the `.gitignore`, then writes the project file. The file's name is the project's name plus `.stproj`, and `IsValidName` guards the name:

- at most 128 bytes and no control characters;
- none of the nine characters `<>:"/\|?*`, which Windows forbids in file names;
- no space at either end and no trailing dot;
- no device name that Windows reserves, such as `CON`, with any extension.

The rule is the strictest platform's, so a project made on Linux opens on Windows. `Create` refuses other names, and so does the command `project.create`.

The file is JSON in format 3, with the project's configuration, the settings and a :term[header]{id=header}. The writer sorts the keys and puts a tab before each level, so the header comes last:

```json
{
	"Project": {
		"AssetDirectory": "Assets",
		"Name": "Coin Run",
		"Scripts": {
			"ModuleName": "CoinRunScripts",
			"SourceDirectory": "Scripts"
		},
		"StartScene": "00000000000000AB"
	},
	"Settings": {
		"Scene.Timing": {
			"Value": {
				"FixedRate": "120",
				"Interpolation": true
			},
			"Version": 1
		}
	},
	"Strata": {
		"Format": "Project",
		"Version": 3
	}
}
```

1. **Lines 11–19:** each section stores its value and the version it was written in.
2. **Lines 20–23:** the header, which `Load` reads first wherever it stands.

The `Project` object may also hold `Export` and `Game`, which other pages teach. The script settings name the source folder and the module, a C identifier of at most 64 characters, because it becomes a CMake target and a file name. When the field is empty, `MakeScriptModuleName` derives it from the project's name: the letters and digits in `PascalCase`, then `Scripts`. So `my game!` becomes `MyGameScripts`, and `2D` becomes `Game2DScripts`. New projects store the derived name, so renaming the project keeps the module's name.

### Load

`Project::Load` is defensive, because the file comes from disk, from version control and sometimes from a newer engine. The first quote holds the size cap, the JSON read and the header and version checks.

```cpp src="Strata/src/Strata/Project/Project.cpp#L217-L234"
const std::optional<std::vector<uint8_t>> bytes = FileSystem::ReadBytesPrefix(projectFile, c_MaxFileBytes + 1);
if (!bytes)
	return fail("cannot read the project file");
if (bytes->size() > c_MaxFileBytes)
	return fail(fmt::format("the project file is larger than the {} MiB a project file may take", c_MaxFileBytes / (1024 * 1024)));
const std::string_view text(reinterpret_cast<const char*>(bytes->data()), bytes->size());

std::string parseError;
std::optional<nlohmann::json> document = JsonUtils::Parse(text, &parseError);
if (!document || !document->is_object())
	return fail(fmt::format("invalid JSON ({})", parseError));

const nlohmann::json* header = JsonUtils::Find(*document, "Strata");
if (!header || JsonUtils::GetString(*header, "Format") != "Project")
	return fail("not a Strata project file");
const uint64_t version = JsonUtils::GetUInt(*header, "Version", 0);
if (version == 0 || version > c_FormatVersion)
	return fail(fmt::format("unsupported project version {} (this engine reads up to {})", version, c_FormatVersion));
```

1. **Line 217:** the read asks for one byte more than the cap, so a file of any size is found too large without reading all of it.
2. **Lines 220–221:** more than `c_MaxFileBytes`, which is 1 MiB, is refused with a message that names the cap.
3. **Lines 229–231:** the header must say `Format` is `Project`; a scene file or a random JSON file is not a project.
4. **Lines 232–234:** version 0 and any version above 3 are refused, naming what this engine reads.

:::example[A file from the future]
A maker opens a project whose header says `"Version": 4`. Line 233 sees 4 above `c_FormatVersion`, which is 3, and the load fails with `unsupported project version 4 (this engine reads up to 3)`, after the file's path. Nothing is opened and nothing is rewritten. A build that rewrote the file as version 3 would destroy whatever version 4 added.
:::

The rest of `Load` reads each member with a default and a check. Asset and script folders must be relative paths inside the project, with no `..` and no folder whose name starts with a dot. Names and paths may hold no control characters, which could inject lines into the generated `CMakeLists.txt` and the logs. The second quote holds the end of the function.

```cpp src="Strata/src/Strata/Project/Project.cpp#L302-L323"
for (const auto& [name, member] : config->items())
{
	if (std::find(c_KnownProjectMembers.begin(), c_KnownProjectMembers.end(), name) == c_KnownProjectMembers.end())
		(*project->m_UnknownMembers)[name] = member;
}

// Versions 1 and 2 have no settings.
if (const nlohmann::json* settings = JsonUtils::Find(*document, "Settings"))
{
	std::string settingsError;
	std::optional<ProjectSettingsValues> values = ProjectSettingsValues::FromJson(*settings, &settingsError);
	if (!values)
		return fail(settingsError);
	project->m_Settings = std::move(*values);
}
project->m_SettingsProblems = project->m_Settings.Validate(registry ? *registry : SettingsRegistry::GetProcessRegistry());
for (const SettingsProblem& problem : project->m_SettingsProblems)
{
	ST_CORE_WARN("{}: the project's settings section '{}' is invalid, so its default applies (the stored value is kept): {}",
		FileSystem::ToUTF8(projectFile), problem.Section, problem.Message);
}
return project;
```

1. **Lines 302–306:** a member of `Project` that is not one of the six known names goes into a side object. `Save` puts it back, so a member that a later version added survives this build.
2. **Lines 309–316:** the stored `Settings` object is read by `FromJson`, which checks only its shape, and a bad shape refuses the file. Versions 1 and 2 have no `Settings`, and load without it.
3. **Line 317:** the values are then checked against the registry, the process's unless a test passes its own.
4. **Lines 318–322:** a section that fails is logged as a warning, and the project still opens. Its stored value stays and its default applies.

`Save` goes the other way. `MakeFileText` checks the fields again, writes the header with the current version, puts the unknown members back and writes `Settings` only while some section is stored. It refuses text over the cap, so the editor tests a change of settings against the cap first. The editor writes the file in the background, and `project.save` waits for that write.

### The active project

`Project::SetActive` and `GetActive` name the project that the editor or the runtime works on, and many engine parts find it there. `ProjectModule`, the :term[engine module]{id=engine-module} of the project, lets it go in its `OnRelease`: it clears the active asset manager and the active project after the program's layers are gone. The job system and the graphics device still exist then, which matters because the asset manager waits for its load jobs and assets own :term[graphics processing unit]{id=gpu} (GPU) resources. The editor and the runtime both list `ProjectModule::Factory()` among their modules.

## Settings sections

The section model has two forms. A **simple section** is described entirely by its fields. Each field has a name, a title, a description for agents, a type and a default, and the engine does the checking, defaulting, schema and settings page from them.

A **complex section** has no fields. It supplies a JSON Schema, a function that makes the default, a function `Read` that checks and upgrades a value and, when the value names assets, a function `References`. The collision layers are a complex section: their value is a table of 32 names and a matrix that says which layers collide.

The field types are `Bool`, `Int`, `Float`, `String`, `Enum` and `Asset`. `Int` and `Float` take a range from `Min` to `Max`. `String` holds at most `MaxLength` bytes of :term[UTF-8]{id=utf-8}, `Enum` one of its `Options`, and `Asset` the handle of an asset of the named type, or null. The next quote is the section's description.

```cpp src="Strata/src/Strata/Core/SettingsRegistry.h#L66-L102"
struct SettingsSection
{
	std::string Id;
	std::string Title;       // What the settings windows show
	std::string Category;    // The group the windows list the section under
	std::string Description; // Written for agents: what the section changes
	SettingsScope Scope = SettingsScope::Project;
	// Stored with the value. A value of an older version is upgraded by Read (simple sections: fields added since take
	// their defaults, members of removed fields are dropped); a newer version than this is refused.
	uint32_t Version = 1;

	std::vector<SettingsField> Fields;

	// Complex sections only.
	nlohmann::json Schema;                    // JSON Schema of the value, for commands and agents
	std::function<nlohmann::json()> MakeDefault;
	// The value checked and upgraded to Version from the stored `version`; nullopt with the reason in `error` (which may be
	// null) when it is invalid. Never asserts: values come from files and agents.
	std::function<std::optional<nlohmann::json>(const nlohmann::json& value, uint32_t version, std::string* error)> Read;
	// The asset handles a valid value names (the project's references: deletes and pruned exports follow them).
	std::function<std::vector<UUID>(const nlohmann::json& value)> References;

	bool IsSimple() const { return !Fields.empty(); }

	// The single validation of a value stored with `version`: its size (c_MaxValueBytes, compact), its version (1 to
	// Version), then the fields or Read. Returns the value at Version (simple sections: with every field), or nullopt with
	// the reason (for a simple section the first bad field's, in the order of Fields).
	std::optional<nlohmann::json> Validate(const nlohmann::json& value, uint32_t version, std::string* outError = nullptr) const;
	// The value of a section nobody set.
	nlohmann::json GetDefault() const;
	// The JSON Schema of the value: Schema, or one made from the fields.
	nlohmann::json GetValueSchema() const;
	// The valid asset handles a validated value names (a simple section's Asset fields, a complex section's References),
	// each once, in the order named.
	std::vector<UUID> FindReferences(const nlohmann::json& value) const;

	static constexpr size_t c_MaxValueBytes = 512 * 1024;
```

1. **Line 72:** the scope: `Project` for what is committed and exported, `User` for the person's preferences, which the editor stores in its own file.
2. **Line 75:** the version. A value is stored with the version it was written at.
3. **Line 77:** the fields. `IsSimple` on line 88 is true when there are fields.
4. **Lines 80–86:** the four members of a complex section: schema, default, `Read` and `References`.
5. **Line 93:** `Validate`, the single check, and line 102, the cap of 512 KiB for one value.

`Validate` does the same steps in the same order for every section. The next quote shows them.

```cpp src="Strata/src/Strata/Core/SettingsRegistry.cpp#L190-L225"
if (version == 0)
	return fail("version 0 is no version of the section");
if (version > Version)
	return fail(fmt::format("the value is of version {} of the section, newer than this engine reads (up to {})", version, Version));
if (const size_t bytes = JsonUtils::Dump(value).size(); bytes > c_MaxValueBytes)
	return fail(fmt::format("the value takes {} bytes, more than the {} KiB a section may hold", bytes, c_MaxValueBytes / 1024));

if (!IsSimple())
{
	if (!Read)
		return fail("the section cannot read values");
	std::string error;
	std::optional<nlohmann::json> result = Read(value, version, &error);
	if (!result)
		return fail(error.empty() ? std::string("the value is invalid") : error);
	if (const size_t bytes = JsonUtils::Dump(*result).size(); bytes > c_MaxValueBytes)
		return fail(fmt::format("the value takes {} bytes, more than the {} KiB a section may hold", bytes, c_MaxValueBytes / 1024));
	return result;
}

if (!value.is_object())
	return fail("the value must be an object of the section's fields");
nlohmann::json result = nlohmann::json::object();
for (const SettingsField& field : Fields)
{
	const nlohmann::json* member = JsonUtils::Find(value, field.Name);
	if (!member)
	{
		result[field.Name] = field.Default;
		continue;
	}
	std::optional<nlohmann::json> fieldValue = ValidateField(field, *member);
	if (!fieldValue)
		return fail(fmt::format("'{}' must be {}", field.Name, DescribeExpected(field)));
	result[field.Name] = std::move(*fieldValue);
}
```

1. **Lines 190–192:** version 0 is no version, and a version above the section's own is refused. A newer value is never guessed.
2. **Lines 194–195:** the compact JSON text of the value may take at most 512 KiB.
3. **Lines 197–208:** a complex section hands the value and its stored version to `Read`, which returns the value at the current version or a reason. The result is checked against the cap again.
4. **Lines 210–225:** a simple section must get an object and checks its fields in the order of `Fields`; a missing field takes its default, and the first bad field is the reason.

A simple section upgrades by itself. A value of an older version gets the defaults of the fields added since, and the members of fields removed since are dropped. Only a value at the current version refuses a member that names no field, because there it is a mistake. A change this rule cannot express, such as a renamed field, needs a complex section whose `Read` maps the old shape to the new.

:::example[Game.Tuning at version 2]
A section Game.Tuning has `MaxEnemies`, a whole number from 1 to 50 that defaults to 10, and `SpawnDelay`, from 0 to 10, which version 2 added with the default 2. A file stored at version 1 holds `{ "MaxEnemies": 20 }`. The check gives `{ "MaxEnemies": 20, "SpawnDelay": 2 }` at version 2. A file at version 2 holding `{ "MaxEnemies": 60 }` is refused: `'MaxEnemies' must be a whole number from 1 to 50`. A file at version 3 is refused as newer than this build reads, whatever it holds.
:::

### The registry

`SettingsRegistry` holds the sections in a `std::deque`, so the pointer that `Find` returns stays valid as later sections register. The process has one registry. Module registration functions fill it, and the editor and games add theirs through `ModuleRegistrationOptions::Extra`. `Engine::RegisterBuiltinModules` freezes it right after the component registry. While it is open only the registering thread may use it, and once frozen it never changes.

`Register` refuses, and logs the reason, when the registry is frozen, the id is invalid or taken, a title, category or description is missing, or the version is 0. It also refuses a section that contradicts itself. A simple section may not give `Read` or a schema, and each field needs a name, a title, a description, a valid range and a default that its own check accepts. Float and asset defaults are kept in the stored form, a float as `2.0` and an asset as its handle's sixteen digits, so a missing field validates to the same value as a given one.

Tests cannot register into the process registry, which is frozen by the time they run. They build a local `SettingsRegistry` and pass it to the code that checks, as `Project::Load` and `ProjectSettingsValues::Validate` allow.

The user scope has its own sections, registered by the editor: `Editor.Interface`, `Editor.ExternalEditor` and `Editor.FrameRate`. They live in the person's preferences file. A project that stores one of them is told so: the check reports that it is a preference of the user, not a project setting.

## A complete simple section: `Scene.Timing`

`Scene.Timing` has two fields. `FixedRate` is an `Enum` with the options `Scene`, `30`, `60`, `120` and `240`, and defaults to `Scene`, which keeps each scene's own :term[fixed step]{id=fixed-step}. Any other choice replaces the step in every scene of the project and in its exported game. `Interpolation` is a `Bool`, true by default: running scenes draw motion between their last two fixed poses. [Drawing between fixed steps](../world/interpolation.md) teaches why.

The section is registered with the title Timing and the category Physics, so its page stands under Physics in the Project Settings window. **File ▸ Project Settings...** opens the window on its **Game** page. On the **Timing** page, drawn below, a field's description is its name's tooltip.

::figure{id=timing-page-drawing}

The descriptions are written for agents and read by people. The text of `FixedRate` says what runs at the rate and what `Scene` keeps. It also says that an update then runs at most 2/15 s of steps, and what each choice costs: 240 runs four times the steps of 60.

The cap is the engine's own rule. At a project rate, an update runs at most the steps of 2/15 s, which is $\lceil r \times 2 / 15 \rceil$ (round up) for $r$ steps per second, from 1 to 64. That is 4 steps at 30, 8 at 60, 16 at 120 and 32 at 240: the same 133 ms of simulated time at every rate. A fixed cap of 8 would let 240 steps per second simulate only 33 ms per frame, and every longer frame would lose time. [Systems, phases and fixed steps](../world/systems.md) teaches what the cap does to a slow frame.

Reading the section is the part to copy. The quote shows `Find`, which every scene calls.

```cpp src="Strata/src/Strata/Scene/ProjectSceneTiming.cpp#L90-L116"
const Timing* Find()
{
	const IProjectSettings* settings = EngineServices::Get<IProjectSettings>();
	if (!settings)
		return nullptr;
	const uint64_t version = settings->GetVersion();
	if (s_Cache.Valid && s_Cache.SettingsVersion == version)
		return &s_Cache.Parsed;

	// The provider holds validated values only (a value its section refuses is not provided: the default applies).
	uint32_t rate = 0;
	bool interpolation = true;
	if (const nlohmann::json* value = settings->FindSection(c_SectionId))
	{
		rate = ParseRate(JsonUtils::GetString(*value, c_FixedRateField, c_SceneRate));
		interpolation = JsonUtils::GetBool(*value, c_InterpolationField, true);
	}
	if (!s_Cache.Valid || rate != s_Cache.Parsed.FixedRate || interpolation != s_Cache.Parsed.Interpolation)
	{
		s_Cache.Parsed.FixedRate = rate;
		s_Cache.Parsed.Interpolation = interpolation;
		s_Cache.Parsed.Version = s_Cache.NextVersion++;
	}
	s_Cache.Valid = true;
	s_Cache.SettingsVersion = version;
	return &s_Cache.Parsed;
}
```

1. **Lines 92–94:** with no provider, as in tools and tests, the result is null and scenes keep their own steps.
2. **Lines 95–97:** if the provider's version is the one cached, the parsed result is returned without reading JSON.
3. **Lines 102–106:** the provider holds only checked values, so the reader trusts the shape and falls back to the defaults where the section is not set.
4. **Lines 107–112:** `Timing::Version` moves only when the rate or the interpolation changes. A change of another section changes the provider's version, but a scene that compares `Timing::Version` does nothing.

Why does Scene own this section and the collision layers, and not Physics? The layers' type, the code that reads it and every reader of the layer names are Scene's. The step drives scripts and animation as well as physics, so a build or a game without physics keeps both. The comment of `RegisterSceneModule` in `SceneRegistration.h` names only the collision layers, but `SceneRegistration.cpp` registers both. Other modules register their own sections, such as `Input.Actions`, `Renderer.Quality` and `Physics.Simulation`; [Every settings section](../reference/settings.md) lists them all.

## The project's values and the service

`ProjectSettingsValues` is the project's store of sections: a map from each id to an entry with the stored version, the stored value and a flag that says whether a registry accepted it. It is also the engine's one implementation of `IProjectSettings`, which has two functions: `FindSection`, the checked value or null, and `GetVersion`. The next quote is its `Validate`.

```cpp src="Strata/src/Strata/Core/ProjectSettings.cpp#L125-L156"
std::vector<SettingsProblem> ProjectSettingsValues::Validate(const SettingsRegistry& registry)
{
	std::vector<SettingsProblem> problems;
	bool changed = false;
	for (auto& [id, entry] : m_Data->Entries)
	{
		const SettingsSection* section = registry.Find(id);
		std::string error;
		std::optional<nlohmann::json> value;
		if (section && section->Scope != SettingsScope::Project)
			error = "it is a preference of the user, not a project setting";
		else if (section)
			value = section->Validate(entry.Value, entry.Version, &error);

		if (!value)
		{
			// Kept as stored: written back unchanged, and its default applies.
			if (section)
				problems.push_back({ id, std::move(error) });
			changed |= entry.Valid;
			entry.Valid = false;
			continue;
		}
		changed |= !entry.Valid || entry.Version != section->Version || *value != entry.Value;
		entry.Value = std::move(*value);
		entry.Version = section->Version;
		entry.Valid = true;
	}
	if (changed)
		m_Data->Version = MakeVersion();
	return problems;
}
```

1. **Lines 134–135:** a user section stored in a project is an error; it is refused with that reason.
2. **Line 137:** the section's own `Validate` does the work, with the stored version.
3. **Lines 139–146:** when the value is refused, the entry keeps its stored value and is no longer provided. Only a section that exists adds a problem; one that no module claims is kept silently.
4. **Lines 148–151:** an accepted value replaces the stored one, at the section's version, and the entry is provided.
5. **Lines 153–154:** the values get a new version only when something changed.

The entries are why the file never loses data. `FindSection` returns only entries that are valid, so a module that asks for a refused section gets null and uses its default. `ToJson` writes every entry, valid or not, at the version and value it holds. A refused value therefore returns to disk as it came, until a person sets the section again.

`Set` checks a new value at the section's current version. It refuses the value when the registry has no such project section, when the value is invalid or when the stored form would pass 1 MiB. On failure nothing changes: `Set` builds the new data aside and swaps it in. `Reset` removes the entry.

For undo, `GetStoredEntry` returns an entry as stored, valid or not. `RestoreStoredEntry` puts it back and validates it as a load does, so undoing a step on a refused section restores the refused text.

The version is unique across the process: every change draws a number from one counter, and a copy of the object draws a fresh one. Two providers never share a version. A module that caches by version therefore notices when the editor closes a project and opens another.

The editor's provider, `OpenProjectSettings`, answers from the open project, or from an empty object when none is open. `GameRuntime` provides its manifest's settings. The runtime checks every section when it starts and refuses to start when one is invalid, because a game must not run on settings it cannot read. The editor opens a damaged project anyway, so the maker can repair it.

## The hand-over to scenes

A scene may be built on a worker thread: a load job reads and prepares a scene asset so that a big scene does not stop a frame. The job must not read `IProjectSettings`, which belongs to the main thread. So the scene is built with its own document's values, and the main thread applies the project's values when it takes the scene. The **hand-over** is that step: applying the project's settings to a scene, on the main thread, when the scene becomes live and after every change of the settings.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L229-L242"
bool Scene::ApplyProjectTiming()
{
	const ProjectSceneTiming::Timing* timing = ProjectSceneTiming::Find();
	if (!timing || timing->Version == m_ProjectTimingVersion)
		return false;
	const uint32_t previousRate = m_ProjectFixedRate;
	m_ProjectFixedRate = timing->FixedRate;
	m_ProjectTimingVersion = timing->Version;
	m_ProjectInterpolation = timing->Interpolation;
	// Turned off: every entity is drawn where it is from the next read.
	if (!m_ProjectInterpolation)
		ClearInterpolation();
	return previousRate != m_ProjectFixedRate;
}
```

1. **Lines 231–232:** no provider, or the same `Timing::Version` as last time: nothing to do, and the function returns false.
2. **Lines 235–237:** the scene copies the rate and the interpolation flag, and remembers the version it took them from.
3. **Lines 239–240:** with interpolation off, the stored poses are cleared, so every entity is drawn where it is.
4. **Line 241:** the :term[return value]{id=return-value} says only whether the rate the scene runs at changed.

`ApplyProjectTiming` is called wherever a scene arrives: by `SceneAsset::TakePreparedScene` and `CreateScene` for a scene asset, by `SceneLoadRequest::TakeScene` for a load request and by the editor for every scene it adopts. The editor also calls it after every change of the project's settings, for the edited scene and the running one, in `EditorContext::ApplyProjectLayers`. The scene's `GetFixedTimestep` then returns 1 divided by the project's rate, and `GetMaxFixedSteps` returns the cap above. Code reads the step there and never from the scene's settings, because the project's rate wins.

With nothing selected, the Inspector shows the effect. At a project rate of 120 the physics line ends with "120 steps/s (project)", and the line "Fixed rate: the project's, 120 steps/s" stands beside a **Project Settings** link. Without a window, `scene.info` reports it under `fixedRate`: source `project`, 120 steps per second, a cap of 16. Inside **Physics**, closed in the figure, the step rows are dimmed; their tooltips name the override.

::figure{id=inspector-project-rate}

:::example[Changing the rate while the game plays]
A game plays at the default `Scene` rate: the step is 1/60 s, 16.7 ms, and the cap is 8 steps. The maker sets `FixedRate` to `120` with `project.setSettings`. At the next call of `ApplyProjectTiming`, `Find` reads `"120"`, the scene takes rate 120 and the step becomes 8.3 ms with a cap of 16. The running game reads the change at once, and the project keeps it after the game stops.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Constants and command-line options in code | Small engines and prototypes | The least code, nothing to store | Changes need a build; no editor page and no description for agents |
| Each module reads its own file or file part | Engines with layered `.ini` files, such as Unreal Engine | Modules stay independent, and layers can override by platform | One checking rule per module; a file written back by a build that lacks a module loses its data |
| One key-value store without types, with defaults in code | Godot's project settings | Any module adds a key at once, with no registration step | No shared version, range or error message; values are checked where they are used |
| Settings as asset objects edited in the editor | Unity's project settings assets | The ordinary asset tools, merge and undo, apply | Settings become asset types with their own loaders and no single check |

## How it is tested

Four suites cover the area. `Project` (`StrataTests/src/Project/ProjectTests.cpp`) creates a project and reloads it, rejects invalid names and files, and finds the project file only when one stands in the folder. It also checks the script settings, control characters, version 1 files and derived module names. `Project.Settings` (`ProjectSettingsTests.cpp`) checks the round trip of sections, and that unknown sections and unknown members survive a save. It also checks that a refused section keeps its text and is reported, that versions 1 and 2 load, that a save writes version 3 and that a file over 1 MiB is refused.

`Core.Settings` (`StrataTests/src/Core/SettingsRegistryTests.cpp`) checks the fields one by one with the first bad field reported, the upgrade by `Read`, the frozen registry and the id rule. It also checks asset references, unique versions and the restore of a stored entry. `Scene.Timing` (`StrataTests/src/Scene/SceneTimingTests.cpp`) checks the override of the step, the cap, the reset, the copy and the hand-over.

Run a suite directly with a doctest filter, or run all with the preset.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Project*
build/windows/bin/Debug/StrataTests.exe --test-suite=Core.Settings
ctest --preset windows-debug -j 8
```

The first line runs both `Project` suites, the second the registry's, and the third every test. Tests build their own registries from `SettingsTestUtils.h`, which holds a simple and a complex test section.

## Changing it safely

To add a section, write a `SettingsSection` in your module with fields, or with a schema and a `Read`, and register it in the module's registration function. Read it through a cached `Find` like the one in `ProjectSceneTiming`. Give every field a description that tells an agent what the value changes and when, because the description is the only manual an agent has. Test the limits, the upgrade path of every version you ship and a refused value. The feature test fails when nothing in it uses a registered settings section, so extend it too.

Three rules protect the data. Bump `Version` when the meaning of a stored value changes, and give old versions an upgrade: a simple section only adds defaults and drops removed fields, so anything else needs `Read`. Never read a section on a worker thread, and never keep a pointer from `FindSection` past a change of `GetVersion`. Never assert on a stored value: return a reason, so the project still opens and the maker can repair the value.

:::history
Before 0.6.0 the collision layers were stored in every scene document, and a project file had no settings. Version 3 of the project file came with them. The editor migrates a project saved by 0.5.0 or older once when it opens it: the scenes' layers become the project's, and the file is saved as the current version. A scene that still stores layers of its own gets a warning, because the project's layers apply.
:::

## Summary

- `Project::Load` refuses what it cannot read safely, such as a file over 1 MiB, a wrong header or a version above 3. It keeps what it does not understand: unknown members, sections no module claims and refused values return to disk as read.
- A settings section is registered data: an id `<Module>.<Name>`, a scope, a version and either fields (simple) or a schema, a default and a `Read` (complex). One `Validate` checks every value, and the registry freezes with the components.
- A simple section upgrades itself: added fields take their defaults, removed members are dropped and a newer version is refused. A refused value keeps its stored text, and the default applies.
- Scene loading on workers cannot read the service. The main thread applies the project's values at the hand-over and after every change, caching by the provider's version.
- A change of `FixedRate` travels from `project.setSettings` through the project's stored entry to `Scene::ApplyProjectTiming`, and the scene's step and cap follow.

## Check yourself

1. Two project files differ only in the header: one says `"Version": 4` and the other `"Version": 3`, and both hold a member `Cloud` in `Project`. This engine reads up to 3, so what happens to each? (a) The first is refused and nothing is written; the second opens and `Cloud` survives a save. (b) Both open, and `Cloud` is dropped. (c) The first opens with defaults, and the second is refused.

   :::answer{tests="file"}
   Option (a). `Load` refuses a version above 3 before it reads anything else, so nothing is rewritten. In the second file `Cloud` is not one of the six known members, so it goes into the side object and `Save` writes it back. Option (b) is the data loss the rules prevent; option (c) mixes up the two cases.
   :::

2. You need a section that holds a list of up to 8 named presets, each with its own list of asset handles. Simple or complex?

   :::answer{tests="section"}
   Complex. A simple section is an object with one member per field of a fixed type; a list of presets is not a field. The section gives a schema, a default, a `Read` that checks every preset and a `References` that returns the handles, so that deletes and pruned exports follow them.
   :::

3. Game.Tuning is at version 2 with `MaxEnemies` from 1 to 50 and `SpawnDelay` from 0 to 10, defaulting to 2. What does validation return for `{ "MaxEnemies": 20 }` at version 1, `{ "MaxEnemies": 60 }` at version 2 and `{ "MaxEnemies": 5 }` at version 3?

   :::answer{tests="upgrade"}
   The first returns `{ "MaxEnemies": 20, "SpawnDelay": 2 }` at version 2: the added field takes its default. The second is refused with `'MaxEnemies' must be a whole number from 1 to 50`, so the stored 60 is kept and the default applies. The third is refused as newer than the section reads, because the section is at version 2.
   :::

4. A scene asset loads on a worker thread while the maker sets `FixedRate` to 240. Which rate does the scene have after the hand-over, and which thread read the project's settings?

   :::answer{tests="handover"}
   The scene has 240 steps per second, and the main thread read the setting. The worker built the scene from its document and never touched the service. When the main thread took the scene, `ApplyProjectTiming` read `Find`, which sees the provider's newest version.
   :::

5. A running scene has `FixedRate` 60, and the maker switches `Interpolation` from on to off. Does `ApplyProjectTiming` return true? What else happens?

   :::answer{tests="trace,handover"}
   The function returns false: the return value reports only a change of the rate, and the rate is still 60. The scene still takes the new flag and clears its stored poses, so every entity is drawn where it is from the next read.
   :::

## Exercises

1. **Basic.** A frame takes 190 ms. Predict how many steps run and how many are dropped at 60 and at 120 steps per second, then check with a sketch of the :term[accumulator]{id=accumulator} loop.

   :::answer[Worked solution]{tests="trace"}
   At the cap, with more than one step of time left, the scene keeps one step for the next frame and drops the rest, so a slow frame cannot make the next one slower. At 60 the step is 16.7 ms and the cap is 8, so 8 steps run (133 ms) and 56.7 ms remain; the loop drops $\lfloor (56.7 - 16.7) / 16.7 \rfloor = 2$ steps and carries one step. At 120 the step is 8.3 ms and the cap is 16: 16 steps run, 56.7 ms remain and 5 steps are dropped. The sketch prints all four rates.

   ```cpp sketch="world-projects-settings-steps.cpp"
   // The fixed steps one slow frame runs at each project rate, and what the cap drops: the accumulator loop alone.
   #include <algorithm>
   #include <cmath>
   #include <cstdint>
   #include <cstdio>

   // The most steps one update runs: the steps of 2/15 s at the rate, from 1 to 64.
   uint32_t GetMaxSteps(uint32_t stepsPerSecond)
   {
   	const uint32_t steps = (stepsPerSecond * 2 + 14) / 15;
   	return std::clamp(steps, 1u, 64u);
   }

   void RunFrame(uint32_t stepsPerSecond, float frameSeconds)
   {
   	const float step = 1.0f / static_cast<float>(stepsPerSecond);
   	const uint32_t maxSteps = GetMaxSteps(stepsPerSecond);
   	float accumulator = frameSeconds;
   	uint32_t steps = 0;
   	while (accumulator >= step && steps < maxSteps)
   	{
   		accumulator -= step;
   		steps++;
   	}
   	uint32_t dropped = 0;
   	if (steps == maxSteps && accumulator > step)
   	{
   		dropped = static_cast<uint32_t>(std::floor((accumulator - step) / step));
   		accumulator = step;
   	}
   	std::printf("%3u steps/s: cap %2u, ran %2u, dropped %2u, carried %.1f ms\n", stepsPerSecond, maxSteps, steps, dropped,
   		accumulator * 1000.0f);
   }

   int main()
   {
   	for (const uint32_t rate : { 30u, 60u, 120u, 240u })
   		RunFrame(rate, 0.19f);
   	return 0;
   }
   ```

   ```text output-of="world-projects-settings-steps.cpp"
    30 steps/s: cap  4, ran  4, dropped  0, carried 33.3 ms
    60 steps/s: cap  8, ran  8, dropped  2, carried 16.7 ms
   120 steps/s: cap 16, ran 16, dropped  5, carried 8.3 ms
   240 steps/s: cap 32, ran 32, dropped 12, carried 4.2 ms
   ```

   1. **Lines 8–12:** the cap is the ceiling of rate times 2/15, kept from 1 to 64.
   2. **Lines 20–24:** the loop runs steps while time is owed and the cap allows.
   3. **Lines 26–30:** at the cap, with more than a step left, the owed time is dropped and one step is carried.
   :::

2. **Medium.** Register the simple section Game.Tuning of the example above in a local `SettingsRegistry`. Write the three checks of question 3 in a test case of `Core.Settings`, in a new file `GameTuningTests.cpp` in `StrataTests/src/Core/` of your clone from [your first engine change](../core/first-change.md), then configure, build and run it.

   :::answer[Worked solution]{tests="section,upgrade" solution="tutorials/world/projects-settings/exercise-2.patch"}
   The section needs an id, a title, a category and a description, version 2 and two `Int` fields, each with a title and a description. Registration refuses a section without them, so the file starts with a helper `MakeIntField` that fills `Name`, `Title`, `Description`, `Type`, `Min`, `Max` and `Default`. The test case follows it.

   ```diff src="book:tutorials/world/projects-settings/exercise-2.patch#L40-L70"
   +	TEST_CASE("Game.Tuning upgrades version 1, refuses a value out of range and refuses version 3")
   +	{
   +		SettingsSection section;
   +		section.Id = "Game.Tuning";
   +		section.Title = "Tuning";
   +		section.Category = "Gameplay";
   +		section.Description = "How many enemies a wave holds and how long the spawner waits.";
   +		section.Version = 2;
   +		section.Fields = { MakeIntField("MaxEnemies", 1, 50, 10), MakeIntField("SpawnDelay", 0, 10, 2) };
   +		SettingsRegistry registry;
   +		REQUIRE(registry.Register(std::move(section)));
   +		const SettingsSection* tuning = registry.Find("Game.Tuning");
   +		REQUIRE(tuning);
   +
   +		const std::optional<nlohmann::json> upgraded = tuning->Validate({ { "MaxEnemies", 20 } }, 1);
   +		REQUIRE(upgraded);
   +		CHECK(*upgraded == nlohmann::json { { "MaxEnemies", 20 }, { "SpawnDelay", 2 } });
   +
   +		std::string error;
   +		CHECK_FALSE(tuning->Validate({ { "MaxEnemies", 60 } }, 2, &error));
   +		CHECK(error == "'MaxEnemies' must be a whole number from 1 to 50");
   +		CHECK_FALSE(tuning->Validate({ { "MaxEnemies", 5 } }, 3, &error));
   +		CHECK(error == "the value is of version 3 of the section, newer than this engine reads (up to 2)");
   +
   +		// A member that names no field: dropped from an older version, refused at the current one.
   +		const std::optional<nlohmann::json> dropped = tuning->Validate({ { "Legacy", 1 } }, 1);
   +		REQUIRE(dropped);
   +		CHECK(*dropped == nlohmann::json { { "MaxEnemies", 10 }, { "SpawnDelay", 2 } });
   +		CHECK_FALSE(tuning->Validate({ { "Legacy", 1 } }, 2, &error));
   +		CHECK(error == "'Legacy' is no field of the section (its fields: 'MaxEnemies', 'SpawnDelay')");
   +	}
   ```

   1. **Lines 42–48:** the section's id, title, category, description, version 2 and two fields; `SpawnDelay` is the field that version 2 added.
   2. **Line 50:** registration refuses a section that is incomplete or contradicts itself.
   3. **Lines 54–62:** a version 1 value is upgraded, a value out of range is refused, and version 3 is refused as newer.
   4. **Lines 65–69:** a member `Legacy` is dropped at version 1 and refused at version 2 as no field of the section.
   :::

3. **Medium.** A complex section has a `Read` that refuses more than 4 names. A project file stores 5 names for it at version 2. Predict what `Load` does, what `FindSection` returns, what a save writes, and how an undo step of a later `Set` restores the text.

   :::answer[Worked solution]{tests="file,section"}
   The project opens, and `Load` logs one warning. `GetSettingsProblems` lists the section with the reason of `Read`, and `FindSection` returns null, so the default applies. A save writes the 5 names back at version 2, as read. A later `Set` with a valid value replaces the entry; before it, `GetStoredEntry` captured the old entry, and `RestoreStoredEntry` puts it back and validates it again, so it is refused again and keeps its text. The test `A section that fails Read keeps its stored value and reports it` checks this for a simple and a complex section.
   :::

4. **Hard.** Trace it yourself. The editor plays a game and a command sets `Scene.Timing` to `{ "FixedRate": "120" }` with `project.setSettings`. Follow the call from the command to the moment the running scene's `GetFixedTimestep` changes. Name each file and function.

   :::answer[Worked solution]{tests="trace,handover"}
   The command is registered in `StrataEditor/src/Editor/EditorProjectSettingsCommands.cpp`. Its handler copies the project's values and calls `ProjectSettingsValues::Set`, which validates the value with `SettingsSection::Validate`. It then calls `ChangeProjectSection` in `StrataEditor/src/Editor/ProjectSettingsAction.cpp`, which tests the change on a copy, including the file's size bound, and executes a `ProjectSettingsAction` on the undo stack.

   `ProjectSettingsAction::Apply` calls `RestoreStoredEntry` on the open project, which draws a new version, then `SaveProjectFile`, then `EditorContext::ApplyProjectLayers` in `EditorContext.cpp`. The context calls `Scene::ApplyProjectTiming` on the edited scene and on the running one. In `Scene.cpp` it calls `ProjectSceneTiming::Find` in `ProjectSceneTiming.cpp`, which sees a new provider version, parses `"120"` and returns a new `Timing::Version`. The scene stores the rate, and `Scene::GetFixedTimestep` now returns 1/120 s. All of it runs on the main thread, inside the command.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Project/Project.h` and `Project.cpp`: `Project`, `ProjectConfig`, `ProjectScriptSettings`, `Create`, `Load`, `Save`, `MakeFileText`, `IsValidName`, `MakeScriptModuleName`, `SetActive`; `Strata/src/Strata/Project/ProjectModule.cpp`: `ProjectModule`.
- `Strata/src/Strata/Core/SettingsRegistry.h` and `SettingsRegistry.cpp`: `SettingsSection`, `SettingsField`, `SettingsScope`, `SettingsRegistry`; `Strata/src/Strata/Core/ProjectSettings.h` and `ProjectSettings.cpp`: `IProjectSettings`, `ProjectSettingsValues`, `SettingsProblem`.
- `Strata/src/Strata/Scene/ProjectSceneTiming.h` and `ProjectSceneTiming.cpp`: the section `Scene.Timing`, `Find`, `GetMaxSteps`; `Strata/src/Strata/Scene/Scene.cpp`: `ApplyProjectTiming`, `GetMaxFixedSteps`; `Strata/src/Strata/Scene/SceneRegistration.cpp`: the registration of both Scene sections.
- `StrataEditor/src/Editor/EditorProjectSettingsCommands.cpp`: `project.settings` and `project.setSettings`; `StrataEditor/src/Editor/ProjectSettingsAction.cpp`: the undo step; `StrataEditor/src/Editor/EditorContext.cpp`: `ApplyProjectLayers`.
- Tests: `Project` and `Project.Settings` in `StrataTests/src/Project/`, `Core.Settings` in `StrataTests/src/Core/SettingsRegistryTests.cpp`, `Scene.Timing` in `StrataTests/src/Scene/SceneTimingTests.cpp`.
- Other pages: [The game's identity](../worlds/game-identity.md), [The project folder](../make/project-files.md), [Collision layers](../physics/collision-layers.md), [Settings windows](../editor-ui/settings-windows.md), [Projects in the editor](../editor/projects.md) and [Every settings section](../reference/settings.md).

## Further reading

- Godot's documentation of project settings, cited without a link: one text file for a project's settings (beginner).
- Unreal Engine's documentation of configuration files, cited without a link: layered `.ini` files and their overrides (intermediate).
- Unity's manual of project settings, cited without a link: settings stored as assets in the project (beginner).
- The JSON Schema specification, cited without a link: the language `GetValueSchema` writes in (intermediate).
- Martin Kleppmann, "Designing Data-Intensive Applications", the chapter on encoding and evolution, cited without a link: why old readers must survive new data (advanced).
