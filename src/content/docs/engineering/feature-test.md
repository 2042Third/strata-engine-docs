---
id: engineering/feature-test
title: "The feature test"
description: "One project that must use everything Strata registers, and the runners that play it, so a feature without its entry cannot land."
kind: internals
size: M
tracks: [E]
needs: [engineering/test-kinds, world/reflection, scripting/abi-sdk]
time: 60
learn:
  - id: coverage-by-construction
    text: explain why a check that walks the registries finds untested features that line coverage cannot
  - id: contract-checks
    text: name the checks the feature test makes and the thing each one demands of a new feature
  - id: script-side
    text: trace how a feature script reports a failed check, a journal entry and a host function call to the runner
  - id: extend-project
    text: add the entries a new component, host function, callback, field type or asset type needs in the feature project
since: 0.3.0
status: final
---

Strata ships many components, settings, script functions and :term[asset types]{id=asset-type}, and a change can break one of them without any test noticing. The **feature test** is one real project, `StrataTests/FeatureTest/`, that must use every registered thing with values other than the defaults, plus the runners that play it. It exists for golden rule 6 of the engine's guide: keep the feature test current. It does not replace the unit tests of each module; it proves that nothing the engine offers goes unused.

## The problem and how engines solve it

Suppose a teammate adds a component and writes unit tests for it. A year later someone changes how scenes store components, and the component stops saving one of its properties. Each unit test still passes, because each builds its own tiny scene. Nobody ever put the component in a real scene and saved it.

The usual answer is **line coverage**: a tool counts which lines of code ran during the tests and reports a percentage. Line coverage says that a line ran. It does not say that anything checked the result, and it says nothing about code that does not exist yet. A new property that no test touches adds lines, and the percentage barely moves.

Strata uses a different idea, **coverage by construction**. The engine keeps registries, lists of everything it offers (components, :term[settings sections]{id=settings-section-world}, host functions, asset types). A test walks each registry and demands one use per entry. The list of "every feature" is no longer in a person's head; the engine itself holds it. A new entry in a registry fails the walk until the project uses it.

Other engines lean on smoke scenes or sample levels that people keep current by habit. Strata turns the habit into a failing test. The cost is a large project that every feature change must also edit. The page [Test kinds](../engineering/test-kinds.md) describes the other kinds of tests this one stands beside.

## The coverage loop

Read the picture from the registries on the left to the runners on the right. Every registry has a check that compares it with the project. The project holds the scene, the settings file, the assets and the script module. The runners then play that one project in five ways.

```mermaid caption="The registries on the left each have a check that compares them with the one feature project, which several runners then play." alt="A flow chart. Six registries lead into the checks. The checks compare them with the feature project, which holds a scene, a settings file, assets and scripts. The runners play the project: headless, in the editor, as an exported game, as real programs and on the graphics card."
flowchart LR
  A[Components] --> C[Coverage checks]
  B[Settings sections] --> C
  D[Host functions] --> C
  E[SDK names] --> C
  F[Script field types] --> C
  G[Asset types] --> C
  C --> P[Feature project]
  P --> S[Feature.stscene]
  P --> T[FeatureTest.stproj]
  P --> U[Assets]
  P --> V[Scripts]
  P --> R1[Headless]
  P --> R2[In-process editor]
  P --> R3[Exported game]
  P --> R4[Real programs]
  P --> R5[GPU]
```

The project is a real one. `FeatureTest.stproj` is its settings file, `Assets/` holds an asset of every type with a committed `.meta` file, and `Scripts/` is a script module built for the test. The scene `Feature.stscene` lives in `Assets/Scenes/`. The check code lives in `StrataTests/src/FeatureTest/`.

## The contract: what counts as covered

The feature test fails when any of these eight things holds. Each rule has a reason, which is what a new feature must supply.

1. **A component is missing from the scene, or a property is default everywhere.** Every registered component must sit on some entity, and each of its properties must differ from a default-made instance on at least one entity. A property that is non-default also proves that it survives saving and loading. Asset and entity references must resolve.
2. **A settings section is default.** Every project settings section must be stored in `FeatureTest.stproj` with a value other than its default.
3. **A script field type is not overridden.** Every type a script field can have needs a field of that type, registered with `ST_SCRIPT_FIELD`, whose value the scene overrides.
4. **A callback never ran.** Every value of the engine's `ScriptCallback` list (`OnCreate`, `OnUpdate`, `OnFixedUpdate` and the others) must appear in the journal described below this list.
5. **A host function was never called.** Every entry of the host table needs at least one call during the run.
6. **An SDK name is unused.** Every public class, function and :term[macro]{id=macro} of the script software development kit (SDK) must appear in the feature scripts.
7. **An asset type has no asset, or an asset misbehaves.** Each asset of the project must import without warnings, and importing must leave its `.meta` file untouched.
8. **The run logs something unexpected.** Any warning or error that the scripts did not log on purpose fails the run, and so does a script check that fails or never completes.

A **journal** (feature test) is a text the feature scripts append events to, in a scene entity named `Journal`, so the runner can check events of instances that no longer exist. A script writes `<Class>.<Event>@<Entity>;` to it. The runner reads it after play and demands that every script class created itself and that every :term[callback]{id=callback} appears.

:::rule
Golden rule 6 of the engine's guide says: keep the feature test current. Every new component, host function, SDK name, callback and field type must be exercised by it. The reason is the contract above: the test fails on what the project leaves unused, so a feature without its entry cannot land. The steps for a component are in [the component tutorial](../world/tutorial-component.md), and for a host function in [its tutorial](../scripting/tutorial-host-function.md).
:::

## A toy version

Before the real code, a toy. It has a registry of two components, each with properties and defaults, and a feature scene reduced to a list of values. The check demands what the real one demands: every component present, and every property non-default somewhere.

:::question
New to C++? The toy uses variables, loops, functions and structs from [programming 2](../basics/programming-2.md), and classes and calls such as `std::cout <<` from [programming 3](../basics/programming-3.md).
:::

The toy builds a scene that misses a camera and leaves one value at its default, runs the check, repairs the scene and runs it again. Look at the two kinds of failure message.

```cpp sketch="engineering-feature-test-toy.cpp"
#include <iostream>
#include <string>
#include <vector>

struct Property
{
	std::string Name;
	int Default = 0;
};

struct Component
{
	std::string Name;
	std::vector<Property> Properties;
};

// One property value of one entity of the feature scene.
struct SceneValue
{
	std::string Component;
	std::string Property;
	int Value = 0;
};

int CheckCoverage(const std::vector<Component>& registry, const std::vector<SceneValue>& scene)
{
	int failures = 0;
	for (const Component& component : registry)
	{
		bool present = false;
		for (const SceneValue& value : scene)
			present |= value.Component == component.Name;
		if (!present)
		{
			std::cout << "FAIL " << component.Name << ": no entity has it\n";
			failures++;
			continue;
		}
		for (const Property& property : component.Properties)
		{
			bool nonDefault = false;
			for (const SceneValue& value : scene)
				nonDefault |= value.Component == component.Name && value.Property == property.Name && value.Value != property.Default;
			if (!nonDefault)
			{
				std::cout << "FAIL " << component.Name << "." << property.Name << ": default on every entity\n";
				failures++;
			}
		}
	}
	return failures;
}

int main()
{
	const std::vector<Component> registry = { { "Light", { { "Intensity", 1 }, { "Range", 10 } } }, { "Camera", { { "Fov", 60 } } } };
	std::vector<SceneValue> scene = { { "Light", "Intensity", 5 }, { "Light", "Range", 10 } };

	std::cout << "Run 1: " << CheckCoverage(registry, scene) << " failures\n";
	scene = { { "Light", "Intensity", 5 }, { "Light", "Range", 25 }, { "Camera", "Fov", 90 } };
	std::cout << "Run 2: " << CheckCoverage(registry, scene) << " failures\n";
	return 0;
}
```

```text output-of="engineering-feature-test-toy.cpp"
Run 1: FAIL Light.Range: default on every entity
FAIL Camera: no entity has it
2 failures
Run 2: 0 failures
```

1. **Lines 28–32:** the loop over the registry; the toy asks first whether any entity has the component.
2. **Lines 33–38:** a component on no entity fails once, and the check moves on to the next component.
3. **Lines 41–43:** a property passes when some entity holds a value that differs from its default.
4. **Lines 56–57:** the first scene misses the camera and leaves `Range` at its default 10.

The first run shows both failures: a component that no entity has, and a property that equals its default on every entity. The second run passes.

The real check differs in three ways. It reads the registries instead of a typed-in list. It reads a loaded scene. It finds defaults by making a default instance of each component, not by keeping a table of numbers.

## The real code, in the order data flows

The data flows from the project's files, through the loaded scene, to the checks. The first check loads the project and looks at assets.

The test case "The feature project imports and loads without warnings" collects every non-built-in asset, demands a clean import, and compares each committed `.meta` file with the one the engine kept. A loop over asset types then asks for one asset per type. The loop stops at the type whose name is `None`, so a new type is included without an edit to the test.

Now the component check, the heart of the page. It walks `ComponentRegistry`, makes a default instance of each component in a spare registry, and compares every property of every owner with it.

```cpp src="StrataTests/src/FeatureTest/FeatureTests.cpp#L152-L196"
TEST_CASE("The feature scene contains every component with non-default values")
{
	FeatureProject project;
	const Ref<Scene> scene = project.LoadStartScene();
	entt::registry& registry = scene->GetRegistry();
	const std::vector<Entity> entities = scene->GetEntitiesInHierarchyOrder();

	for (const ComponentInfo* info : ComponentRegistry::GetAll())
	{
		INFO("Component ", info->Name, ": the feature scene (StrataTests/FeatureTest/Assets/Scenes/Feature.stscene) must contain it, and "
			"every property must have a non-default value on at least one entity");

		// A default-constructed instance to compare with.
		entt::registry defaults;
		const entt::entity defaultEntity = defaults.create();
		const void* defaultComponent = info->Add(defaults, defaultEntity);

		std::vector<entt::entity> owners;
		for (const Entity entity : entities)
		{
			if (info->Has(registry, entity.GetHandle()))
				owners.push_back(entity.GetHandle());
		}
		CHECK_FALSE(owners.empty());

		for (const PropertyInfo& property : info->Properties)
		{
			INFO("Property ", property.Name);
			const PropertyValue defaultValue = property.GetValue(defaultComponent);
			bool nonDefault = false;
			for (const entt::entity owner : owners)
			{
				const PropertyValue value = property.GetValue(info->Get(registry, owner));
				nonDefault |= value != defaultValue;

				// References resolve: assets are registered, entities exist.
				if (property.Type == PropertyType::Asset && std::get<UUID>(value).IsValid())
					CHECK(project.GetAssetManager()->IsHandleValid(std::get<UUID>(value)));
				if (property.Type == PropertyType::Entity && std::get<UUID>(value).IsValid())
					CHECK(scene->GetEntityByUUID(std::get<UUID>(value)).IsValid());
			}
			CHECK(nonDefault);
		}
	}
}
```

1. **Line 159:** the walk over every registered component, so a new one is included without an edit.
2. **Lines 164–167:** the default instance, made in a spare registry, is what each value is compared with.
3. **Line 175:** a component on no entity fails once.
4. **Line 185:** one owner with a different value is enough for a property.
5. **Lines 187–191:** an :term[asset handle]{id=asset-handle} must be registered and an entity reference must exist.

The default instance is the reference. The test never lists components or properties itself, so adding a property to a component adds a `CHECK(nonDefault)` to the run. The message printed on failure names the component and tells you which file to edit. Chapter [Reflection](../world/reflection.md) explains `ComponentInfo` and `PropertyInfo`.

The next quote is the headless play, the test that runs scripts. It creates the services a game would have, plays the scene and then asks the call counters about every host function.

```cpp src="StrataTests/src/FeatureTest/FeatureTests.cpp#L229-L281"
TEST_CASE("The feature scene plays headless with every script check passing")
{
	// Audio without an output device, as headless games have it, so that the scripts' sounds play.
	ScopedAudioEngine audio;
	REQUIRE(audio.Initialized);
	FeatureProject project;
	LoadAllAssets(*project.GetAssetManager());
	const Ref<Scene> scene = project.LoadStartScene();
	ScopedScriptEngine engine(GetFeatureScriptModule());
	// The game's shell as a headless game has it: a window service without a window, and saves in a directory of its own.
	GameWindowService window(nullptr);
	EngineServices::ScopedProvider<IGameWindow> windowProvider(window);
	SaveDirectory saves(CreateTemporaryDirectory("FeatureSaves"));
	EngineServices::ScopedProvider<IGameSaves> savesProvider(saves);
	// Its graphics options over the project's quality, kept in the same directory.
	GameGraphicsService graphics(EngineServices::Get<IProjectSettings>(), &saves);
	EngineServices::ScopedProvider<IGameGraphics> graphicsProvider(graphics);

	ScopedScriptLogLevel scriptLogLevel;
	LogCapture log;
	ResetScriptHostCallCounts();

	// Drawn between fixed steps, as games are (the feature scripts check what they see of it).
	scene->SetInterpolation(true);
	scene->OnRuntimeStart();
	const auto advanceFrame = [&]()
	{
		project.GetAssetManager()->Update();
		scene->OnUpdateRuntime(c_FeatureFrameTime);
	};
	PlayFeatureScene(*scene, *engine, advanceFrame);
	CHECK(engine->GetLoadCount() == 2);
	CheckFeatureResults(*scene, *engine);

	// The game asks to quit after the scenario; headless, nobody acts on it, so the scene keeps the requests (the quit,
	// and the restart that replaced the earlier loads).
	const int32_t exitCode = PlayFeatureQuitFrame(*scene, *engine, advanceFrame);
	CHECK(scene->GetQuitRequest() == exitCode);
	CHECK(scene->GetSceneLoadRequest() == UUID::Null());
	CHECK(GetField<std::string>(GetScriptSystem(*scene), scene->FindEntityByName("Game Features"), "GameFeatures", "Failure").empty());

	// Every host function of the script API was called.
	for (const ScriptHostFunctionCalls& function : GetScriptHostCallCounts())
	{
		INFO("Host function ", std::string(function.Name), " was never called: exercise it in a feature script (StrataTests/FeatureTest/Scripts)");
		CHECK(function.Calls > 0);
	}

	// Stopping destroys every instance (OnDestroy is journaled).
	scene->OnRuntimeStop();
	CheckFeatureJournal(*scene, *engine);
	CheckFeatureLog(log.GetEntries());
}
```

1. **Lines 231–233:** audio on the null device, so that the scripts' sounds play.
2. **Lines 238–245:** the services a game provides: a window service without a window, saves in a folder of the test, and graphics options.
3. **Line 249:** the counters start at zero, so earlier tests cannot satisfy the check.
4. **Line 252:** :term[interpolation]{id=interpolation} is on, as in games.
5. **Lines 270–275:** every host function needs at least one call.

The test uses audio without an output device, a window service without a window, and saves in a temporary folder, because the scripts call audio, window and save functions that need something to answer. It turns :term[interpolation]{id=interpolation} on, as games do, so the scripts can check what they see between :term[fixed steps]{id=fixed-step}. Then `PlayFeatureScene` runs 200 frames, and the hot reload of the script module comes after frame 100. After every frame it demands that the scene's cached :term[world transforms]{id=world-transform}, hierarchy and interpolation match what a fresh count gives.

The loop over `GetScriptHostCallCounts()` is check 5. The host application programming interface (API) and its counters are in [the host API page](../scripting/host-api.md), and the reload in [the hot reload page](../scripting/hot-reload.md).

In :term[Dist]{id=dist} builds the counters do not exist: `GetScriptHostCallCounts()` returns an empty list, so check 5 has nothing to check there. The runner expects the log to hold only the messages of `c_ExpectedLogMessages`, which are the lines the log scripts print on purpose, including a warning, an error and a deliberate exception in `OnUpdate`.

The SDK coverage check reads text rather than running code. `SDKReader` parses the :term[headers]{id=header} of `StrataScriptCore` to learn every public class, function and macro, and parses the feature scripts to learn what they use.

```cpp src="StrataTests/src/FeatureTest/SDKCoverageTests.cpp#L381-L404"
TEST_CASE("The feature scripts use every function of the script SDK")
{
	const SDKSurface surface = ReadSDKSurface();
	const ScriptUsage usage = AnalyzeScripts(surface, ReadFeatureScripts());

	for (const std::string& className : surface.Classes)
	{
		INFO("SDK class ", className, " is not used by the feature scripts (StrataTests/FeatureTest/Scripts)");
		CHECK(usage.Identifiers.contains(className));
	}
	for (const SDKFunction& function : surface.Functions)
	{
		const std::string name = function.GetQualifiedName();
		INFO("SDK function ", name, " is not used by the feature scripts (StrataTests/FeatureTest/Scripts). ",
			function.Static || function.Class.empty() ? "Call it qualified (" + name + ")." : "Call it on a receiver whose type is declared (see "
			"StrataTests/src/FeatureTest/SDKReader.h); calls of this name on receivers of unknown type: " + DescribeUntypedAccesses(usage, function.Name));
		CHECK(usage.Functions.contains(name));
	}
	for (const std::string& macro : surface.PublicMacros)
	{
		INFO("SDK macro ", macro, " is not used by the feature scripts (StrataTests/FeatureTest/Scripts)");
		CHECK(usage.Identifiers.contains(macro));
	}
}
```

1. **Lines 386–390:** every SDK class must appear in the scripts.
2. **Lines 391–398:** every function must be called, and the failure text tells the writer how.
3. **Lines 399–403:** every public macro must appear.

A function counts as used only when a script calls it on its own class. A static function counts when called as `Class::Name`. A :term[member function]{id=member-function} counts when called on a variable whose type the reader can tell. A call on a receiver of unknown type does not count, and the failure message lists such calls to help you find the cause. The reader is itself tested against sample headers, so that a reader mistake cannot make these checks pass by emptiness; one test demands at least 80 functions from the real SDK.

The script :term[application binary interface]{id=abi} (ABI) and the SDK are the subject of [the SDK page](../scripting/abi-sdk.md).

The script side is the last piece. Every feature script derives from `FeatureScript`, which counts checks and keeps the first failure.

```cpp src="StrataTests/FeatureTest/Scripts/FeatureScript.h#L77-L90"
class FeatureScript : public Strata::Script
{
public:
	int32_t Checks = 0;
	std::string Failure;    // The first failed check
	bool Completed = false; // The scenario ran to its end
protected:
	void Expect(bool condition, std::string_view description)
	{
		Checks++;
		if (!condition && Failure.empty())
			Failure = std::string(description);
	}
};
```

1. **Lines 80–82:** the three values the runner reads from every live instance.
2. **Lines 84–89:** `Expect` counts every check and keeps only the first failure.

`Expect` is the only way a script reports. After play, the runner demands from each live instance that `Completed` is true and `Failure` is empty, and names the class, entity and failed check otherwise. State that spans frames lives in fields, because the hot reload recreates every instance and keeps only field values.

:::example
Add a component `Fog` with three properties to the engine, and run the headless suite without touching the scene. The component test fails four times.

One failure is `CHECK_FALSE(owners.empty())`, since no entity has `Fog`. Three more are `CHECK(nonDefault)`, one per property, because the loop over owners never runs and `nonDefault` stays false. The message names `Fog` and the property, and points to `Feature.stscene`. You add one entity with `Fog` and three non-default values, and the four failures disappear. If one property is an asset reference, the test also demands that its handle is valid.
:::

## The runners

One project is played by several programs, because each finds different mistakes. The first is `StrataTests.FeatureTest`, which runs the suites `FeatureTest` and `Editor.FeatureTest` without a :term[graphics processing unit]{id=gpu} (GPU). It plays the project headless, through editor commands in the editor process, and as an exported game in `GameRuntime`. For the test program and its shards see [the test program page](../engineering/test-program.md).

The suite `GPU.FeatureTest` runs with the other GPU suites in the :term[CTest]{id=ctest} `StrataTests.GPU`. It draws the scene for four frames, with no scripts, and checks which entities the identifier (ID) buffer holds, the text and the statistics. `StrataEditor.FeatureTest` and `StrataRuntime.FeatureTest` start the real :term[executables]{id=executable} on a copy of the project: they load the scripts, step the physics, click and type, export the game and run it. Each must exit with success and print the lines its scripts log.

`StrataRuntime.FeatureTestQuality` runs the exported game in a window with `--quality low`, and its scripts must see the :term[preset]{id=preset} as the :term[command line's]{id=terminal-command}. `StrataEditor.InputSequence` drives the editor with :term[simulated input]{id=simulated-input}. The executables' tests form a chain of :term[CTest]{id=ctest} fixtures, the pattern that [Test kinds](../engineering/test-kinds.md) describes.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Line coverage with a threshold | Most large projects | A number for every file, with no project to maintain | No check that results were verified, and none for features that do not exist yet |
| A sample level kept current by habit | Engines with sample games | Real content, little code | A feature can land without an entry; nothing fails |
| Unit tests per feature only | Small libraries | Fast, local failures | No test of a feature inside a saved, loaded, running scene |
| Generated tests from the registries | Tools that try random inputs | Less to write by hand | Values chosen by a program rarely exercise real gameplay |

The feature test chooses a scene written by people because the scripts must play a scenario, not only round-trip values.

## How it is tested

The suites are `FeatureTest` (headless, in `StrataTests/src/FeatureTest/`) and `Editor.FeatureTest`, both under the CTest name `StrataTests.FeatureTest` with the label `feature`. Run the headless one directly:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=FeatureTest
ctest --preset windows-debug -L feature
```

The first line runs only the `FeatureTest` suite; the second runs every test with the label, including the executables' tests and the quality test, which also carries the label `gpu`. The checks guard themselves: a test feeds `SDKReader` a sample header and demands the exact names it finds, and another demands that the real SDK holds known classes. The asset test loads every asset, and any log line at warning level or above fails it.

## Changing it safely

What to add depends on what you changed.

| You added | The feature project needs |
| --- | --- |
| A component | A new entity, or a place on an existing one, in `Feature.stscene`, with every property non-default |
| A property | A non-default value on some entity that has the component |
| A settings section | A stored, non-default value in `FeatureTest.stproj` |
| A host function | A call from a feature script that uses `Expect`, and an entry in `ST_SCRIPT_HOST_FUNCTIONS` |
| An SDK name or callback | A call in a script of `Scripts/*Features.cpp`; for a callback, a journal entry of its first call |
| A script field type | A new script field of that type, registered by `ST_SCRIPT_FIELD`, with a value the scene sets |
| An asset type | A small asset with a committed `.meta` file under `Assets/` |

Change the scene file by hand. The other way is to open a copy of the project in the editor, save the change there and copy the scene back. Messages your scripts log on purpose go into `c_ExpectedLogMessages`.

The tiny binary assets come from a generator. Its path is `StrataTests/FeatureTest/Tools/GenerateAssets.py`, and its outputs are committed. The engine's developer guide omits the folders in front of that path, and the top-level `Tools/` folder holds no such file. See [generated code](../engineering/generated-code.md) for the process of generators.

Never disable a check to make the test pass, and never widen what `c_ExpectedLogMessages` tolerates for a message you do not understand: the unexpected warning is the finding. After a change, run the suites above, then the full `ctest` for your platform.

## Summary

- Line coverage says which lines ran; a check that walks the registries demands one use per registered thing, so new features fail until the project holds them.
- The feature test checks components and properties, settings sections, script field types, callbacks, host functions, SDK names, asset types and the run's log.
- Scripts derive from `FeatureScript`, report through `Expect`, `Checks`, `Failure` and `Completed`, and leave events in the journal.
- A new feature adds its entry to the matching part of the project: scene, settings file, scripts or assets.

## Check yourself

1. A teammate adds a property `Radius` to a component and its unit test passes. Which of these makes the feature test fail, and why do the others not?
   - (a) the property exists but is not in the docs
   - (b) the property is default on every entity of the feature scene
   - (c) the unit tests ran in a different order
   - (d) the property is saved in the wrong folder

   :::answer{tests="contract-checks"}
   (b). The component check demands a non-default value on some entity. Documentation, test order and folders are not read by it.
   :::

2. The check for host functions reads `GetScriptHostCallCounts()` after the play. A script calls `Time::SetTimeScale` only before `ResetScriptHostCallCounts()` runs. Does the check pass?

   :::answer{tests="contract-checks,script-side"}
   No. The counters are reset before play, so a call made earlier is not counted, and the check reports `SetTimeScale` as never called.
   :::

3. Why does the SDK coverage test demand at least 80 functions from the real headers?

   :::answer{tests="coverage-by-construction"}
   A reader that stopped finding functions would make every later check pass with nothing to demand. The floor makes that mistake fail.
   :::

4. A feature script runs, but one of its `Expect` calls fails on frame 40 and a later one passes. What does the runner report?

   :::answer{tests="script-side"}
   `Failure` keeps only the first failed description, so the runner names the class, the entity and that first check.
   :::

5. A teammate adds the callback `OnSomethingNew` to the engine. The unit tests pass, but the feature test fails. What must the teammate add?

   :::answer{tests="extend-project,contract-checks"}
   A feature script that implements the callback and journals its first call. The journal check searches for an entry of every callback, and names the one it did not find.
   :::

## Exercises

1. **Basic.** Run the toy's idea on references: complete the check that every entity a property names must exist.

   :::answer[Worked solution]{tests="coverage-by-construction,extend-project" solution="sketches/engineering-feature-test-references.cpp"}
   The sketch skips the value 0, which means no reference, and reports every other number the set of entities lacks. It mirrors the component test, where an invalid id is ignored and a valid id must name an existing entity.

   ```cpp sketch="engineering-feature-test-references.cpp"
   #include <iostream>
   #include <set>
   #include <string>
   #include <vector>

   // A property that names another entity by number; 0 means "no reference".
   struct EntityReference
   {
   	std::string Property;
   	int Target = 0;
   };

   int CheckReferences(const std::set<int>& entities, const std::vector<EntityReference>& references)
   {
   	int failures = 0;
   	for (const EntityReference& reference : references)
   	{
   		if (reference.Target == 0)
   			continue;
   		if (!entities.contains(reference.Target))
   		{
   			std::cout << "FAIL " << reference.Property << ": entity " << reference.Target << " does not exist\n";
   			failures++;
   		}
   	}
   	return failures;
   }

   int main()
   {
   	const std::set<int> entities = { 1, 2, 3 };
   	const std::vector<EntityReference> references = { { "Follow.Target", 2 }, { "Door.Opener", 7 }, { "Light.Parent", 0 } };
   	std::cout << CheckReferences(entities, references) << " failures\n";
   	return 0;
   }
   ```

   ```text output-of="engineering-feature-test-references.cpp"
   FAIL Door.Opener: entity 7 does not exist
   1 failures
   ```

   1. **Lines 18–19:** the value 0 means no reference, so the check skips it.
   2. **Lines 20–24:** a reference to a missing entity fails with its property name.
   3. **Lines 31–32:** the door's opener names entity 7, which the set lacks.
   :::

2. **Medium.** Add a component to the engine and watch the feature test fail until `Feature.stscene` holds it with non-default values.

   :::answer[Worked solution]{tests="extend-project"}
   Add the component by the steps of the component tutorial. Run `StrataTests.exe --test-suite=FeatureTest`: the component test fails with the message that names the component and the scene file. Open a copy of `StrataTests/FeatureTest/` in the editor, add an entity with the component, change every property, save, and copy `Feature.stscene` back. Run the suite again; the failures are gone. If the component has an asset property, point it at an asset of the project.
   :::

3. **Hard.** Trace it yourself: follow `Time::SetTimeScale` from the SDK to the feature script that calls it and the check that fails when no script does.

   :::answer[Worked solution]{tests="script-side,contract-checks"}
   Search for `SetTimeScale`. The SDK function is in `StrataScriptCore/Include/StrataScript/Time.h`; it calls `host->SetTimeScale`, a member of `StrataScriptHostAPI` in `StrataScriptCore/Include/StrataScript/ScriptABI.h`. The engine implements it as `HostSetTimeScale` in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` and lists it as `X(SetTimeScale)` in `ST_SCRIPT_HOST_FUNCTIONS`. The feature script `StrataTests/FeatureTest/Scripts/TimeFeatures.cpp` calls it in `OnUpdate` on the slow frame. The check is the loop over `GetScriptHostCallCounts()` in `StrataTests/src/FeatureTest/FeatureTests.cpp`, in the test case that plays the scene headless.
   :::

## Where it lives in Strata

- Project: `StrataTests/FeatureTest/` (`FeatureTest.stproj`, `Assets/`, `Scripts/`), and its generator `StrataTests/FeatureTest/Tools/GenerateAssets.py`.
- Checks: `StrataTests/src/FeatureTest/FeatureTests.cpp`, `SDKCoverageTests.cpp`, `SDKReader.cpp`, `FeatureTestUtils.cpp`, `GPUFeatureTests.cpp`.
- Script side: `StrataTests/FeatureTest/Scripts/FeatureScript.h`.
- Runners: the suite `GPU.FeatureTest` (run by `StrataTests.GPU`), and the CTests `StrataTests.FeatureTest`, `StrataEditor.FeatureTest`, `StrataRuntime.FeatureTest`, `StrataRuntime.FeatureTestQuality` and `StrataEditor.InputSequence`, defined in `StrataTests/CMakeLists.txt`.

## Further reading

- Martin Fowler, "Test Coverage": what line coverage can and cannot tell you (beginner).
- The engine's developer guide, section "Feature test": the full list of runners and checks (intermediate).
