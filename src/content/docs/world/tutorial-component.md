---
id: world/tutorial-component
title: "Tutorial: adding a component and a system"
description: "Add a wind zone component and its scene system to Strata, with the tests and the feature scene entry that the engine's own checks demand."
kind: tutorial
size: L
tracks: [E]
needs: [core/first-change, start/first-game, world/systems, world/serialization]
time: 150
learn:
  - id: declare-register
    text: write a component with defaults and units in its module's header and register it under a stable name with ranges, tooltips and an enum
  - id: system
    text: add a scene system that overrides one function and reads zones from the world transform cache
  - id: order
    text: predict where a system runs from its soft constraints and read the order the engine logs
  - id: tests
    text: write the reflection test, the round trip test and the system test of a new component
  - id: feature
    text: explain what the feature scene and the schema snapshot demand of a new component, and what a renamed component does to a saved scene
since: 0.3.0
status: final
---

## What you will make

You will add a wind zone to Strata. It is a component that marks a region of wind, with a strength, a radius and a mode, and a system that gathers every active zone in each :term[fixed step]{id=fixed-step}. The zone will push rigid bodies in a later change, [the capstone](../capstone/build.md); here you build the data, the system and every check that the engine demands of a new component.

```mermaid caption="The change in five parts: the data, its registration, the system that reads it, the tests and the feature scene entry, which together make the engine's checks pass." alt="Boxes for the component data, the registration, the system and the tests stand in a row, joined by arrows. A box for the feature scene hangs under the registration. Arrows from the tests and from the feature scene lead to a last box that reads engine checks pass."
flowchart LR
    D["Component data"] --> R["Registration"]
    R --> S["System"]
    S --> T["Tests"]
    R --> F["Feature scene"]
    T --> C["Engine checks pass"]
    F --> C
```

## What you need

- The source build of [your first engine change](../core/first-change.md): a clone at the book's commit, its :term[submodules]{id=submodule} and a `Debug` build of your system's :term[CMake preset]{id=cmake-preset}. Every command below writes `<preset>` for that preset: `windows`, `linux` or `macos`.
- The editor, built in that tree, for the checks in the second and third sections. It opens a project made from the Basic 3D template, as [your first game](../start/first-game.md) makes one.
- Time: about two and a half hours. The first build after the first section compiles again every file that includes the physics :term[header]{id=header}, and the full test run at the end is the longest wait.
- No file to import and no stage to download: you start from that clone, with or without your first change, which touches none of the files below. You change the engine: eleven existing files and three new ones, shown in this page as blocks of one patch.

The engine keeps its own checklist for a new component in the skill `strata-add-component`. It has five parts, and the sections of this page follow them: declare the data, register it, add the behavior, test it, and satisfy the feature test. The fifth part, the documentation, is one line here.

:::files[The files of the change]

- `GameEngine/` your clone
  - `Strata/src/Strata/Physics/`
    - **PhysicsComponents.h**: the component's data; you add the :term[struct]{id=struct} here
    - **PhysicsComponents.cpp**: the registration of the physics components; you add one here
    - **WindZoneSystem.h**, **WindZoneSystem.cpp**: the new system
    - **PhysicsRegistration.cpp**, **PhysicsRegistration.h**: where the physics module registers its systems, and the comment that names them
  - `StrataTests/`
    - `src/Physics/WindZoneTests.cpp`: the new tests of the system
    - `src/Scene/`: tests of reflection, :term[serialization]{id=serialization} and systems, which you extend
    - `src/Engine/BuiltinModulesTests.cpp`: tests of what each build registers
    - `FeatureTest/Assets/Scenes/Feature.stscene`: the scene that must hold every component
    - `Architecture/ComponentSchema.json`: the snapshot of every component's registration

:::

## Declare the wind zone's data

A wind zone needs three facts: how hard the wind pushes, how far from the zone's center it reaches, and whether it blows one way through the whole radius or outward from the center. The first two are numbers and the third is a choice between two named values. A component is a plain struct that holds such facts, and nothing else: the code that acts on them lives in a system.

Each member needs a default and a unit. The default is what a person sees when they add the component, so it should work at once. The unit goes in a comment, because a bare 10 could be newtons, meters or percent, and a reader cannot know which. A newton is the force that speeds a 1 kg mass by 1 m/s each second. Gravity pulls a 1 kg crate down with 9.81 N, so a default strength of 10 N almost balances one crate's weight and moves nothing dramatic.

:::::steps

1. Open `Strata/src/Strata/Physics/PhysicsComponents.h` and go to the end of the file, where `CharacterControllerComponent` stands. Read how its members look.

   **You should see:** one default value on every member, and a comment after it that says what the member means and in which unit: `float Radius = 0.3f; // World units`.

   **If you do not see it:** you opened another header. The path starts at the clone's folder: `Strata`, `src`, `Strata`, `Physics`.

2. Add the mode and the component after `CharacterControllerComponent`, inside the :term[namespace]{id=namespace}. Copy the lines that start with `+`.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-1"
    		bool Enabled = true;           // A disabled controller neither moves nor collides; its entity moves freely
    	};
    
   +	// How a wind zone blows: one way through its whole radius, or outward from its center.
   +	enum class WindZoneMode : uint8_t
   +	{
   +		Directional = 0,
   +		Spherical
   +	};
   +
   +	// A region of wind that pushes rigid bodies. WindZoneSystem gathers the active zones every fixed step.
   +	struct WindZoneComponent
   +	{
   +		float Strength = 10.0f; // Force of the wind on a body, in newtons
   +		float Radius = 5.0f;    // How far the zone reaches from its center, in meters
   +		WindZoneMode Mode = WindZoneMode::Directional;
   +	};
   +
    }
   ```

   1. **Lines 4–9:** the mode is an `enum class` with one :term[byte]{id=byte} of storage, like `RigidBodyType` above it. The values 0 and 1 are the numbers the registration writes next to the names.
   2. **Line 12:** the component is a plain `struct`: no :term[base class]{id=base-class}, no function. Components of this kind need no help from the engine to be copied, saved or compared.
   3. **Lines 14–16:** a default and a unit on every member. The comment names the unit that the tooltip repeats in the next section.

   **You should see:** the new lines between `CharacterControllerComponent` and the closing brace of the namespace, with tabs at the start of each line, like their neighbors.

   **If you do not see it:** when the build in the next step reports an unknown type, the new lines landed outside `namespace Strata`. Move them inside.

3. Build the engine, with the command of the first change.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   ```

   On Windows the editor must not run while the build writes it.

   **You should see:** the build ends without an error. Every file that includes the physics header compiles again, so this build takes longer than the next ones.

   **If you do not see it:** read the first error line. A missing `;` after a closing brace of the `struct` is the usual cause.

:::::

:::why[The module's header, not `Scene/Components.h`]
`Scene/Components.h` holds the scene's own components, and the few types that two sibling modules both must read. Nothing else in the engine reads a wind zone yet, so it belongs to the module that will act on it. The module is also optional: a build without physics leaves its folder out, and a component declared there leaves with it, while a scene that holds one still loads and keeps it. The cost is that no other module may include the physics header; when the script software development kit (SDK) needs wind later, it reaches it through a :term[scene service]{id=scene-service} instead.
:::

You should now have a struct that compiles and that nothing yet knows about.

## Register the component

The engine does not find components by looking at your struct. It finds them in a table of registrations, and one registration describes a component to every part of the engine at once: the files, the Inspector, the commands, undo and scripts. [Reflection](../world/reflection.md) explains how one registration fills all of them. What you write is the description: a name, a category, a text, and for each member a range, a tooltip and a kind.

Choose the ranges so that a bad state cannot exist. A strength below 0 would push the wrong way. The upper limit 1000 N would lift a crate of 1000 / 9.81 = 102 kg, a strong storm in a game. A radius of 0 would make the reach empty, and a later calculation that divides a distance by the radius would divide by zero, so the lowest radius is 0.01 m, a very small distance. The upper end of the radius is `c_Unbounded`, the engine's constant 1,000,000 for a bound that only keeps a value finite.

:::::steps

1. Add the registration at the end of `RegisterPhysicsComponents`, in `Strata/src/Strata/Physics/PhysicsComponents.cpp`, after the one of `CharacterControllerComponent`.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-2"
    				WithTooltip(Range(0.0f, c_Unbounded, 1.0f), "Largest force with which it pushes dynamic bodies, in newtons"))
    			.Property("Enabled", &CharacterControllerComponent::Enabled, WithTooltip({}, "A disabled controller neither moves nor collides"))
    			.Gizmo(ComponentGizmoGroup::Collider, CharacterControllerGizmo);
   +
   +		ComponentRegistry::Register<WindZoneComponent>("WindZone")
   +			.DisplayName("Wind Zone")
   +			.Category("Physics")
   +			.Description("A region of wind that pushes rigid bodies: directional zones blow one way through their radius, "
   +				"spherical zones blow outward from their center")
   +			.Property("Strength", &WindZoneComponent::Strength, WithTooltip(Range(0.0f, 1000.0f, 0.1f), "Force of the wind on a body, in newtons; 0 is calm"))
   +			.Property("Radius", &WindZoneComponent::Radius, WithTooltip(Range(0.01f, c_Unbounded, 0.05f), "How far the zone reaches from its center, in meters"))
   +			.EnumProperty("Mode", &WindZoneComponent::Mode, { { "Directional", 0 }, { "Spherical", 1 } });
    	}
    
    }
   ```

   1. **Line 5:** `"WindZone"` is the stable name. Scene files, commands and scripts all use it, so it never changes once a file holds it.
   2. **Lines 6–9:** the display name and the category fill the **Add Component** menu, and the description is the text that people and agents read.
   3. **Line 10:** `Range(0.0f, 1000.0f, 0.1f)` is the lowest value, the highest and the step of a drag. `WithTooltip` adds the text, with its unit, that the Inspector shows beside the label.
   4. **Line 11:** the lowest radius is 0.01, so that no zero or negative radius can be stored.
   5. **Line 12:** `EnumProperty` stores the enum as a number and shows it by name; the names are what files hold.

   **You should see:** the registration inside the function, before its closing brace.

   **If you do not see it:** the build reports that the name `WindZoneComponent` is unknown when the struct is in another header. The file already includes `PhysicsComponents.h`, so check the spelling of the struct.

2. Build again, then start the editor and create a project from the Basic 3D template (**File ▸ New Project...**, as in your first game).

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   ```

   **You should see:** a project with the template's scene open.

   **If you do not see it:** the editor refuses to start when the build failed. Read the build's last lines first.

3. Select the cube or any other entity, press **Add Component** in the Inspector, type `wind` in the search field and choose `Wind Zone` under the Physics heading.

   **You should see:** a `Wind Zone` component with three properties, `Strength`, `Radius` and `Mode`, holding 10, 5 and Directional. Hold the pointer over `Strength` to read the tooltip.

   **If you do not see it:** the entry is missing from the menu when the editor still runs the old build. Close it and start the new one.

4. Try the range. Type `-3` into `Radius`, and `5000` into `Strength`.

   **You should see:** the Inspector does not keep either value: the stored radius is 0.01 and the stored strength is 1000, the ends of the ranges. A scene file that holds such a value is clamped the same way, without a warning, as the test of the fourth section shows.

   **If you do not see it:** when the field keeps a number outside the range, the registration of that member has no `Range`. Check lines 10 and 11 of the block above.

:::::

:::rule[A registered name is never renamed]
The name `WindZone` is written into every scene, prefab and command script, and agents use it through the automation commands. Renaming it makes every older file hold a component that the engine no longer knows. The last exercise of this page does exactly that, so that you see what the engine does with such a file.
:::

You should now have a component that people can add and edit, and no behavior yet.

## Add the system

A component holds data; a system acts on it. Strata runs the systems of a playing scene in one fixed order, and each frame it calls the functions that a system overrides, as [Systems, phases and fixed steps](../world/systems.md) teaches. The wind will push bodies, and bodies move in fixed steps, so the wind's system takes part in the fixed step only.

At this stage the system does one thing: it gathers the active zones, with the world position of each, so that the later change can apply forces from that list. That keeps this change small, and a test can read the list through `GetSystem<T>`. The physics module already registers a system, so its registration shows where yours goes.

:::::steps

1. Read `RegisterPhysicsModule`, the function that registers the physics module with the engine.

   ```cpp src="Strata/src/Strata/Physics/PhysicsRegistration.cpp#L12-L27" symbol="RegisterPhysicsModule"
   void RegisterPhysicsModule()
   {
   	RegisterPhysicsComponents();
   	const bool sectionRegistered = SettingsRegistry::GetProcessRegistry().Register(PhysicsSimulationSettings::MakeSection());
   	ST_CORE_VERIFY(sectionRegistered, "The physics module could not register its settings section");

   	// Physics simulates what the scripts moved this frame (another module's system: a soft constraint). It also runs in the
   	// editor's simulate mode.
   	SceneSystemDescriptor descriptor = MakeSceneSystemDescriptor<PhysicsSystem>("Physics", true, [](Scene& scene) { return CreateScope<PhysicsSystem>(scene); });
   	descriptor.AfterIfPresent = { "Scripting" };
   	descriptor.ProfileStage = "Scene.Physics";
   	// A loaded scene's bodies are built while its load prepares it, so that the frame it starts in builds none.
   	descriptor.PrepareLoadedScene = &PhysicsSystem::PrepareLoadedScene;
   	const bool registered = SceneSystemRegistry::Register(std::move(descriptor));
   	ST_CORE_VERIFY(registered, "The physics module could not register its scene system");
   }
   ```

   1. **Line 14:** the module first registers its components. Your registration from the last section runs here.
   2. **Lines 20–22:** the descriptor of the physics system: a name, a flag that lets it run in the editor's simulate mode, and a :term[soft constraint]{id=soft-constraint} to run after the scripts.
   3. **Lines 25–26:** the result of `Register` is checked, because the registry refuses a descriptor with a cycle or a bad name.

   **You should see:** a function of sixteen lines that ends with the check of the result.

   **If you do not see it:** the file has changed from this description when your clone is not at the book's commit. Move it there, as the first change does.

2. Create the file `WindZoneSystem.h` in the folder `Strata/src/Strata/Physics/`, with these lines.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-3"
   +#pragma once
   +
   +#include "Strata/Physics/PhysicsComponents.h"
   +#include "Strata/Scene/SceneSystem.h"
   +
   +#include <glm/glm.hpp>
   +
   +#include <vector>
   +
   +namespace Strata
   +{
   +
   +	class Scene;
   +
   +	// One wind zone as WindZoneSystem read it in the last fixed step.
   +	struct WindZoneSample
   +	{
   +		entt::entity Handle = entt::null;
   +		glm::vec3 Position = { 0.0f, 0.0f, 0.0f }; // The zone's center in world space
   +		float Strength = 0.0f;                     // Newtons
   +		float Radius = 0.0f;                       // Meters
   +		WindZoneMode Mode = WindZoneMode::Directional;
   +	};
   +
   +	// Gathers the scene's active wind zones once per fixed step, with the world position of each. It writes no transform and
   +	// no component: the forces on bodies come in a later change. Main thread only.
   +	class WindZoneSystem : public SceneSystem
   +	{
   +	public:
   +		explicit WindZoneSystem(Scene& scene);
   +
   +		void OnFixedUpdate(float timestep) override;
   +
   +		// The zones of the last fixed step; empty before the first one.
   +		const std::vector<WindZoneSample>& GetZones() const { return m_Zones; }
   +
   +	private:
   +		Scene& m_Scene;
   +		std::vector<WindZoneSample> m_Zones;
   +	};
   +
   +}
   ```

   1. **Lines 16–23:** one gathered zone: its entity handle, the position of its center in :term[world space]{id=world-space} and a copy of the three values.
   2. **Line 27:** the system derives from `SceneSystem`, like every system.
   3. **Line 32:** it overrides `OnFixedUpdate` only, and the function is public, so that `MakeSceneSystemDescriptor` sees the override.
   4. **Line 35:** a read-only view of the last step's list, for tests and for the later change.

   **You should see:** a header of 42 lines that includes the physics header and `SceneSystem.h`.

   **If you do not see it:** a missing `#pragma once` makes the :term[compiler]{id=compiler} report that a type is defined twice. Add it to the first line.

3. Create the file `WindZoneSystem.cpp` in the same folder.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-4"
   +#include "stpch.h"
   +#include "Strata/Physics/WindZoneSystem.h"
   +
   +#include "Strata/Scene/Entity.h"
   +#include "Strata/Scene/Scene.h"
   +
   +namespace Strata
   +{
   +
   +	WindZoneSystem::WindZoneSystem(Scene& scene)
   +		: m_Scene(scene)
   +	{
   +	}
   +
   +	void WindZoneSystem::OnFixedUpdate(float)
   +	{
   +		ST_PROFILE_FUNCTION();
   +
   +		// Gathered anew every step, so that a zone that was destroyed, deactivated or moved needs no bookkeeping.
   +		m_Zones.clear();
   +		for (const auto [handle, zone] : m_Scene.GetRegistry().view<WindZoneComponent>().each())
   +		{
   +			const Entity entity(handle, &m_Scene);
   +			if (!m_Scene.IsActiveInHierarchy(entity))
   +				continue;
   +
   +			// Reading the world transform changes nothing, so the transform contract asks for no signal.
   +			m_Zones.push_back({ handle, glm::vec3(m_Scene.GetWorldTransform(entity)[3]), zone.Strength, zone.Radius, zone.Mode });
   +		}
   +	}
   +
   +}
   ```

   1. **Lines 19–20:** the list is built again in every step, so a zone that was destroyed or made inactive needs no extra handling.
   2. **Lines 23–25:** a zone whose entity or one of whose ancestors is inactive does not count; the scene answers `IsActiveInHierarchy` in :term[constant time]{id=constant-time}.
   3. **Lines 27–28:** `GetWorldTransform` returns the cached matrix when nothing changed, and computes it when something did. The fourth column of the matrix is the position.

   **You should see:** a :term[source file]{id=source-file} whose first line is `#include "stpch.h"`, as every engine source starts.

   **If you do not see it:** the build of the next step reports an unknown `ST_PROFILE_FUNCTION` when the first line is missing.

4. Register the system in `RegisterPhysicsModule`. Add the include `#include "Strata/Physics/WindZoneSystem.h"` below the include of `PhysicsSystem.h`, then the lines of this block below the check of the physics system. In `PhysicsRegistration.h`, change the comment above `RegisterPhysicsModule` so that it names both systems, `Physics` and `WindZone`.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-6"
    		descriptor.PrepareLoadedScene = &PhysicsSystem::PrepareLoadedScene;
    		const bool registered = SceneSystemRegistry::Register(std::move(descriptor));
    		ST_CORE_VERIFY(registered, "The physics module could not register its scene system");
   +
   +		// Wind reads what the scripts moved this frame and runs before the step that physics takes (both are soft constraints,
   +		// so that the engine runs without either system). It also runs in the editor's simulate mode.
   +		SceneSystemDescriptor windDescriptor = MakeSceneSystemDescriptor<WindZoneSystem>("WindZone", true, [](Scene& scene) { return CreateScope<WindZoneSystem>(scene); });
   +		windDescriptor.AfterIfPresent = { "Scripting" };
   +		windDescriptor.BeforeIfPresent = { "Physics" };
   +		const bool windRegistered = SceneSystemRegistry::Register(std::move(windDescriptor));
   +		ST_CORE_VERIFY(windRegistered, "The physics module could not register the wind zone scene system");
    	}
    
    }
   ```

   1. **Line 7:** `MakeSceneSystemDescriptor<WindZoneSystem>` records the class, so that `GetSystem` finds it, and reads which functions it overrides. The `true` lets it run in simulate mode, like physics.
   2. **Lines 8–9:** two soft constraints: after the scripts, which may move a zone this frame, and before physics, which will use the wind in its step.
   3. **Lines 10–11:** the result is checked, as for the physics system.

   **You should see:** two registrations in one function, with the wind system's second.

   **If you do not see it:** the build reports that `WindZoneSystem` is unknown when the include is missing.

5. Run the :term[configure step]{id=configure-step} again, because you added two source files, then build.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --parallel
   ```

   **You should see:** the build compiles the two new files and links without an error.

   **If you do not see it:** when the :term[linker]{id=linker} reports an undefined `WindZoneSystem`, the configure step did not run. The build collects its sources at that step, and the new `.cpp` is not on its list yet.

6. Start the editor and open the **Console**. Type `Engine modules` into its **Search** field, and keep **Info** checked.

   **You should see:** one line that ends with `Scene systems update in the order UI, Scripting, WindZone, Animation, World, Physics, Audio`.

   **If you do not see it:** the editor started before the build finished when the line lacks `WindZone`. Close it and start the new build.

:::::

Why does the wind system stand between the scripts and Animation? The physics module registers first, so the registration order is `Physics`, `WindZone`, `Audio`, `Animation`, `Scripting`, `World` and `UI`. The constraints say that `WindZone` runs after `Scripting` and before `Physics`, and `Animation` and `World` also lie between the same two. Among systems that the constraints leave free, registration order decides, and the physics module registered `WindZone` before both. So the line reads `Scripting`, `WindZone`, `Animation`, `World`, `Physics`.

:::why[Soft constraints toward Physics too]
Physics belongs to the same module, so a hard `Before` would also work. The engine's own test asks for soft constraints on every built-in system, so that a build or a test can omit or replace the other system and the registration still succeeds. The cost: nothing refuses a wrongly spelled name. A wrongly spelled `Scripting` would let the wind system run first of all, as the first exercise shows, and only the log line of step 6, which lists absent soft constraints, would show it.
:::

You should now have a system that runs in every fixed step between the scripts and physics, and a log line that proves where.

## Test the component and the system

Strata ships every behavior with tests, and a new system changes what other tests expect. The suites `Scene.Systems` and `Engine.Modules` name the six built-in systems; your seventh breaks them. This section lets them fail, repairs them, and then adds the three tests that belong to a new component.

:::::steps

1. Run the two suites that list the built-in systems. The test program has the same folder as the editor.

   ```sh
   build/<preset>/bin/Debug/StrataTests --test-suite=Scene.Systems,Engine.Modules
   ```

   On Windows write `StrataTests.exe`. The flag `--test-suite` runs the suites whose names it lists.

   **You should see:** doctest prints failed checks with their file and line, from `SceneSystemTests.cpp` and `BuiltinModulesTests.cpp`, and ends with a count of failed test cases above zero.

   **If you do not see it:** the suites pass when the test program is older than your change. Build the target `StrataTests` again.

2. Update the expectations. Every list of system names gains `WindZone` after `Scripting`, and the count of built-in systems becomes seven. One of the four changes of `BuiltinModulesTests.cpp` is this one.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-22"
    		CHECK(result.Output.find("the Renderer module cannot be excluded (every engine has it); it is registered") != std::string::npos);
    		CHECK(result.Output.find("'Teleportation' is no engine module of this build and cannot be excluded") != std::string::npos);
    		CHECK(result.Output.find("modules: Input Scene Renderer Physics Animation Scripting World GameUI\n") != std::string::npos);
   -		CHECK(result.Output.find("systems: UI Scripting Animation World Physics\n") != std::string::npos);
   +		CHECK(result.Output.find("systems: UI Scripting WindZone Animation World Physics\n") != std::string::npos);
    	}
    #endif
    
   ```

   Five test cases of `SceneSystemTests.cpp` change in the same way. The first one now names the wind system, checks its two soft constraints and checks that it runs in simulate mode. The test of per-frame calls now counts ten calls in an idle frame: your system adds the tenth, in `OnFixedUpdate`.

   **You should see:** the same command now ends with no failed test case.

   **If you do not see it:** a list that is still wrong shows the order the engine built. Copy that order only after you have understood why it differs from your expectation.

3. Create the file `WindZoneTests.cpp` in the folder `StrataTests/src/Physics/`. Its two test cases check the system. The first reads the descriptor, as the `Spinner` exercise of the systems page does; the second steps a real scene.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-8"
   +#include <doctest/doctest.h>
   +
   +#include "Physics/PhysicsTestUtils.h"
   +#include "Strata/Physics/WindZoneSystem.h"
   +
   +using namespace Strata;
   +using namespace Strata::Tests;
   +
   +TEST_SUITE("Physics.WindZone")
   +{
   +	TEST_CASE("The system takes part in fixed steps only")
   +	{
   +		for (const SceneSystemDescriptor& descriptor : SceneSystemRegistry::GetAll())
   +		{
   +			if (descriptor.Name == "WindZone")
   +				CHECK((!descriptor.CallsUpdate && descriptor.CallsFixedUpdate && !descriptor.CallsLateUpdate));
   +		}
   +	}
   +
   +	TEST_CASE("Each fixed step gathers the active zones with their world positions and writes no transform")
   +	{
   +		Scene scene;
   +		Entity parent = scene.CreateEntity("Parent");
   +		parent.GetTransform().Translation = { 10.0f, 0.0f, 0.0f };
   +		parent.MarkModified<TransformComponent>();
   +		Entity gust = scene.CreateChildEntity(parent, "Gust");
   +		gust.GetTransform().Translation = { 0.0f, 2.0f, 0.0f };
   +		gust.MarkModified<TransformComponent>();
   +		WindZoneComponent& wind = gust.AddComponent<WindZoneComponent>();
   +		wind.Strength = 40.0f;
   +		wind.Radius = 3.0f;
   +		wind.Mode = WindZoneMode::Spherical;
   +		Entity calm = scene.CreateEntity("Calm");
   +		calm.AddComponent<WindZoneComponent>();
   +		calm.SetActive(false);
   +
   +		scene.OnRuntimeStart();
   +		const WindZoneSystem* system = scene.GetSystem<WindZoneSystem>();
   +		REQUIRE(system != nullptr);
   +		CHECK(system->GetZones().empty());
   +
   +		StepScene(scene, 1);
   +		REQUIRE(system->GetZones().size() == 1);
   +		const WindZoneSample& sample = system->GetZones()[0];
   +		CHECK(sample.Handle == gust.GetHandle());
   +		CHECK(glm::distance(sample.Position, glm::vec3(10.0f, 2.0f, 0.0f)) == doctest::Approx(0.0f));
   +		CHECK(sample.Strength == doctest::Approx(40.0f));
   +		CHECK(sample.Radius == doctest::Approx(3.0f));
   +		CHECK(sample.Mode == WindZoneMode::Spherical);
   +
   +		StepScene(scene, 3);
   +		CHECK(gust.GetTransform().Translation == glm::vec3(0.0f, 2.0f, 0.0f));
   +		gust.RemoveComponent<WindZoneComponent>();
   +		StepScene(scene, 1);
   +		CHECK(system->GetZones().empty());
   +		scene.OnRuntimeStop();
   +	}
   +}
   ```

   1. **Lines 11–18:** `MakeSceneSystemDescriptor` set `CallsUpdate` to false because the class overrides no `OnUpdate`; the test pins that.
   2. **Lines 23–28:** a parent at (10, 0, 0) and a child at (0, 2, 0) under it. Both transforms are written, so both writes are signaled with `MarkModified`, as the :term[transform contract]{id=transform-contract} demands.
   3. **Lines 33–35:** a second zone on an inactive entity, which the system must skip.
   4. **Lines 42–46:** one step gathers one zone, at the child's world position (10, 2, 0): the parent's position plus the child's offset.
   5. **Lines 51–56:** after three more steps nothing moved, and a removed component leaves the list.

   **You should see:** a new test file of 58 lines.

   **If you do not see it:** when the suite is missing from the run of the next steps, the file is not on the list of sources. Run the configure step again.

4. Add the reflection test to `StrataTests/src/Scene/ReflectionTests.cpp`, inside the first `TEST_SUITE("Reflection")`, and add `"WindZone"` to the list of built-in names at the top of the same file.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-10"
    		CHECK(ComponentAccess::AddComponent(entity, prefabInstance, &error));
    		CHECK(ComponentAccess::RemoveComponent(entity, prefabInstance, &error));
    	}
   +
   +#if ST_WITH_PHYSICS
   +	TEST_CASE("Wind zones register under their stable name with ranges and tooltips, and refuse invalid values")
   +	{
   +		const ComponentInfo* info = ComponentRegistry::Find<WindZoneComponent>();
   +		REQUIRE(info);
   +		CHECK(info->Name == "WindZone");
   +		CHECK(info->DisplayName == "Wind Zone");
   +		CHECK(info->Category == "Physics");
   +		CHECK_FALSE(info->Description.empty());
   +
   +		const PropertyInfo* strength = info->FindProperty("Strength");
   +		const PropertyInfo* radius = info->FindProperty("Radius");
   +		const PropertyInfo* mode = info->FindProperty("Mode");
   +		REQUIRE(strength);
   +		REQUIRE(radius);
   +		REQUIRE(mode);
   +		CHECK(strength->Tooltip.find("newtons") != std::string::npos);
   +		CHECK(radius->Tooltip.find("meters") != std::string::npos);
   +
   +		WindZoneComponent zone;
   +		CHECK(strength->SetValue(&zone, 5000.0f)); // Clamped to the range
   +		CHECK(zone.Strength == doctest::Approx(1000.0f));
   +		CHECK(strength->SetValue(&zone, -1.0f));
   +		CHECK(zone.Strength == 0.0f);
   +		CHECK(radius->SetValue(&zone, -3.0f)); // No negative or zero radius
   +		CHECK(zone.Radius == doctest::Approx(0.01f));
   +		CHECK_FALSE(radius->SetValue(&zone, std::numeric_limits<float>::quiet_NaN()));
   +		CHECK(zone.Radius == doctest::Approx(0.01f));
   +
   +		REQUIRE(mode->EnumValues.size() == 2);
   +		CHECK(mode->SetValue(&zone, int32_t(1)));
   +		CHECK(zone.Mode == WindZoneMode::Spherical);
   +		CHECK_FALSE(mode->SetValue(&zone, int32_t(2)));
   +		CHECK(zone.Mode == WindZoneMode::Spherical);
   +	}
   +#endif
    }
    
    TEST_SUITE("Scene.InactiveProperties")
   ```

   1. **Lines 10–13:** the registration keeps its name, display name and category, and has a description.
   2. **Lines 21–22:** the tooltips carry the units, so an agent that reads `component.list` learns them.
   3. **Lines 25–32:** a value above the range is clamped, a negative radius becomes 0.01, and `NaN` is refused.
   4. **Lines 34–38:** the mode accepts 0 and 1, and refuses 2.

   **You should see:** the test case inside `#if ST_WITH_PHYSICS`, because a build without physics has no such component.

   **If you do not see it:** when `WindZoneComponent` is unknown to the compiler, the file does not include `PhysicsComponents.h`; it does, under the same condition, at its top.

5. Add the round trip test to `StrataTests/src/Scene/SerializationTests.cpp`, before the test case `Hand-written entity data without ids is accepted`.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-11"
    		CHECK(loaded.Intensity == 1.0f);
    	}
    
   +#if ST_WITH_PHYSICS
   +	TEST_CASE("Wind zones keep every value through a save and a load, load their defaults for keys they lack, clamp out-of-range values and warn about the rest")
   +	{
   +		const auto load = [](const nlohmann::json& zone, std::vector<std::string>& warnings)
   +		{
   +			const nlohmann::json document = {
   +				{ "Strata", { { "Format", "Scene" }, { "Version", 1 } } },
   +				{ "Scene", { { "Name", "Windy" }, { "Entities", { { { "ID", "00000000000000AD" }, { "Components", {
   +					{ "Name", { { "Name", "Gust" } } }, { "WindZone", zone } } } } } } } }
   +			};
   +			Scene scene;
   +			std::string error;
   +			REQUIRE_MESSAGE(SceneSerializer::Deserialize(scene, document, &error, &warnings), error);
   +			return scene.GetEntityByUUID(UUID(0xAD)).GetComponent<WindZoneComponent>();
   +		};
   +		std::vector<std::string> warnings;
   +		WindZoneComponent loaded = load(nlohmann::json::object(), warnings);
   +		CHECK(warnings.empty());
   +		CHECK(loaded.Strength == doctest::Approx(10.0f));
   +		CHECK(loaded.Radius == doctest::Approx(5.0f));
   +		CHECK(loaded.Mode == WindZoneMode::Directional);
   +		// Out of range: clamped, as every ranged property is.
   +		loaded = load({ { "Strength", 5000 }, { "Radius", -2 } }, warnings);
   +		CHECK(warnings.empty());
   +		CHECK(loaded.Strength == doctest::Approx(1000.0f));
   +		CHECK(loaded.Radius == doctest::Approx(0.01f));
   +		// Another type or an unknown name: a warning, and the default.
   +		loaded = load({ { "Strength", "strong" }, { "Direction", { 0, 0, 1 } } }, warnings);
   +		CHECK(CountWarnings(warnings, "Strength") == 1);
   +		CHECK(CountWarnings(warnings, "Direction") == 1);
   +		CHECK(loaded.Strength == doctest::Approx(10.0f));
   +
   +		// A zone with every value changed comes back whole, and saves the same text again.
   +		Scene scene;
   +		WindZoneComponent& wind = scene.CreateEntity("Gust").AddComponent<WindZoneComponent>();
   +		wind.Strength = 25.0f;
   +		wind.Radius = 8.5f;
   +		wind.Mode = WindZoneMode::Spherical;
   +		const nlohmann::json saved = SceneSerializer::Serialize(scene);
   +		Scene reloaded;
   +		std::string error;
   +		warnings.clear();
   +		REQUIRE_MESSAGE(SceneSerializer::Deserialize(reloaded, saved, &error, &warnings), error);
   +		CHECK(warnings.empty());
   +		const WindZoneComponent& again = reloaded.FindEntityByName("Gust").GetComponent<WindZoneComponent>();
   +		CHECK(again.Strength == 25.0f);
   +		CHECK(again.Radius == 8.5f);
   +		CHECK(again.Mode == WindZoneMode::Spherical);
   +		CHECK(SceneSerializer::Serialize(reloaded) == saved);
   +	}
   +#endif
   +
    	TEST_CASE("Hand-written entity data without ids is accepted")
    	{
    		nlohmann::json snapshot = { { "Entities", {
   ```

   1. **Lines 7–18:** a loader that puts one zone's :term[JSON]{id=json} into a scene document and returns the loaded component.
   2. **Lines 19–24:** a zone with no keys loads the defaults, and loading warns of nothing.
   3. **Lines 25–29:** values out of range are clamped and give no warning, because files are clamped like the Inspector.
   4. **Lines 30–34:** a value of another type and a name that does not exist each give one warning, and the default stays.
   5. **Lines 36–52:** a zone with all three values changed is saved, loaded and saved again: the values and the text are the same.

   **You should see:** a test case whose name says what it keeps, loads, clamps and warns about.

   **If you do not see it:** a loaded `Mode` of Directional after the round trip means the enum was stored as a number and read as a name; check that `Mode` is registered with `EnumProperty`.

6. Run the configure step again, build the tests, and run the four suites that you touched.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --target StrataTests --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Physics.WindZone,Reflection,Scene.Serialization,Scene.Systems
   ```

   Before you run, predict the summary of `Physics.WindZone` alone: how many test cases, and how many assertions?

   **You should see:** no failed test case. The run of `--test-suite=Physics.WindZone` alone reports 2 test cases and 11 assertions, all passed: one check in the first test case and ten in the second.

   **If you do not see it:** a failed check prints the two values it compared. A position of (0, 2, 0) instead of (10, 2, 0) means the system read the :term[local transform]{id=local-transform} instead of the :term[world transform]{id=world-transform}.

7. Break the system on purpose. Delete the two lines `if (!m_Scene.IsActiveInHierarchy(entity))` and `continue;` in `WindZoneSystem.cpp`, build, and run `--test-suite=Physics.WindZone`.

   **You should see:** the second test case fails at the check that the list holds one zone: it holds two, because the inactive zone now counts. Restore the two lines and run the suite again.

   **If you do not see it:** when the test still passes, the test program is older than your edit. Build the target `StrataTests` again, then run the suite.

:::::

A test that passes with and without the code proves nothing, so the break in the last step matters: it shows that the test catches the mistake it is for.

You should now have a component and a system with tests that fail when either breaks.

## Pass the engine's feature test

The engine has one more check that no other part of this page satisfies. The feature test project holds a scene that must contain every registered component, with every property at a value other than its default on at least one entity. It exists so that no component ships without a real scene that loads it, saves it and plays it. A new component fails that test until you add it.

:::::steps

1. Run the feature test, which `ctest` knows by its name, `StrataTests.FeatureTest`.

   ```sh
   ctest --preset <preset>-debug -R "^StrataTests\.FeatureTest$"
   ```

   **You should see:** one test, `Failed`. The doctest output above the summary names the check `The feature scene contains every component with non-default values` and the message `Component WindZone: the feature scene (StrataTests/FeatureTest/Assets/Scenes/Feature.stscene) must contain it`.

   **If you do not see it:** when the test passes, the build is older than your registration. Build all targets again.

2. Add an entity with a wind zone to the feature scene, `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene`, as the last entity of the list.

   ```diff src="book:tutorials/world/tutorial-component.patch#hunk-25"
    					}
    				},
    				"ID": "F7E000000000006A"
   +			},
   +			{
   +				"Components": {
   +					"Name": {
   +						"Name": "Gust"
   +					},
   +					"Transform": {
   +						"Rotation": [
   +							0,
   +							0,
   +							0,
   +							1
   +						],
   +						"Scale": [
   +							1,
   +							1,
   +							1
   +						],
   +						"Translation": [
   +							8,
   +							1,
   +							-7
   +						]
   +					},
   +					"WindZone": {
   +						"Mode": "Spherical",
   +						"Radius": 8.5,
   +						"Strength": 25
   +					}
   +				},
   +				"ID": "F7E00000000000A0"
    			}
    		],
    		"Name": "Feature",
   ```

   1. **Lines 5–9:** a new entity named `Gust`. The file sorts the keys of each object by their letters, so `Name`, `Transform` and `WindZone` come in that order.
   2. **Lines 22–26:** its position, away from the other entities.
   3. **Lines 28–32:** every property differs from its default: 25 instead of 10, 8.5 instead of 5, and Spherical instead of Directional. The mode is written by name.
   4. **Line 34:** the entity's identifier, which must differ from all others in the file.

   **You should see:** the new entity between the last entity of the file and the closing bracket of the entity list.

   **If you do not see it:** when the next run reports a JSON error, a `,` is missing after the closing brace of the entity before yours.

3. Write the component schema snapshot again. The snapshot lists every component's name, texts and properties, so that a later change that renames them or changes their order fails a test.

   ```sh
   build/<preset>/bin/Debug/StrataTests --strata-test-helper=write-component-schema StrataTests/Architecture/ComponentSchema.json
   git diff --stat StrataTests/Architecture/ComponentSchema.json
   ```

   **You should see:** one changed file, with 207 added lines and none removed. The entry of `WindZone` takes 57 of them, after the one of `CharacterController`. The other 150 are the entry of `RectLight`, a light the engine added after its snapshot was last written; the schema test accepts a component that the snapshot lacks, so keep both.

   **If you do not see it:** a :term[diff]{id=diff} that changes or removes lines of other components means your registration changed one of them, which it must not do.

4. Run the feature test and the layering check.

   ```sh
   ctest --preset <preset>-debug -R "^StrataTests\.FeatureTest$"
   build/<preset>/bin/Debug/StrataTests --test-suite=Architecture.Layering,Reflection.ComponentSchema
   ```

   **You should see:** the feature test `Passed`, and no failed test case in the second command. The layering check passes because the new files include only the scene and the physics module, which the :term[layer table]{id=layer-table} of the engine allows.

   **If you do not see it:** a failure of the schema test names the component and prints both versions of its description. Run step 3 again.

5. Name the component in the engine's documentation: add `WindZone` to the list of the physics module's components in `Docs/Architecture.md`. Then run every test that needs no :term[graphics card]{id=gpu}.

   ```sh
   ctest --preset <preset>-debug -j 8 -LE gpu
   ```

   **You should see:** all tests passed. The run takes the longest of this page.

   **If you do not see it:** read the first failed test. A test outside this page's list that fails after your change counts a built-in system or a component: update its expectation, as you did in the fourth section.

:::::

The wind zone is complete as the engine counts it: declared, registered, behaving, tested and part of the feature scene. The capstone adds the forces, and the host function [that gives scripts the wind](../scripting/tutorial-host-function.md) and the [`wind.*` commands](../editor/tutorial-command.md) come in their own tutorials.

Track E continues with the graphics processing unit (GPU), at [How a GPU works and draws a frame](../gpu/how-a-gpu-frame-works.md). The strip below also offers [the review of this part](review.md), which is not on track E: take it as extra practice.

## Summary

- You declared a component in its module's header, with a default and a unit on every member, and you saw why the scene's own header is the wrong place.
- You registered it under a stable name, with a category, a description, ranges, tooltips and an enum, and you saw the Inspector clamp what the ranges forbid.
- You added a system that overrides only `OnFixedUpdate`, reads the world transform cache, writes nothing and registers with two soft constraints, and you read its place in the order the engine logs.
- You wrote a reflection test, a round trip test and a system test, repaired the tests that name the built-in systems, and broke the system on purpose to see a test fail.
- You added the component to the feature scene with every property at a non-default value, wrote the schema snapshot again, and learned what a renamed component does to an old scene.

## Check yourself

1. The struct `WindZoneComponent` could go in `Scene/Components.h`, where every other module can include it. Why does the engine's checklist send it to `Physics/PhysicsComponents.h`?

   :::answer{tests="declare-register"}
   `Scene/Components.h` holds the scene's own components and the types that two sibling modules must both read. Only the physics module acts on a wind zone, so it owns the type. The module is optional: a build without it leaves the folder out, and a scene with a zone still loads there, keeping the component unchanged. The price is that another module cannot include the header and needs a scene service.
   :::

2. A scene file holds `"Radius": -2` for a zone. What does the engine load, does it warn, and which line of the test proves it?

   :::answer{tests="declare-register tests"}
   The engine loads 0.01, the lowest value of the range, and gives no warning: a file is clamped like the Inspector. The check `CHECK(warnings.empty())` after the load of `{ "Strength", 5000 }, { "Radius", -2 }` proves it, and the check on `loaded.Radius` pins the clamped value. A name the component does not have, or a value of another type, does warn, once each.
   :::

3. You add `void OnUpdate(Timestep) override` to `WindZoneSystem` and register it as before. What changes in the descriptor, and what does the scene do differently?

   :::answer{tests="system"}
   `MakeSceneSystemDescriptor` sets `CallsUpdate` to true, because it reads which functions the class overrides. The scene then calls the system once per frame, in the update phase, as well as in every fixed step. The test `The system takes part in fixed steps only` fails, which is its job. A system that overrides nothing it uses costs nothing in an idle frame; one that overrides too much pays on every frame.
   :::

4. A build has no scripting module. In which position does `WindZone` run, and why?

   :::answer{tests="order"}
   `WindZone` runs first: the line reads `WindZone`, `Animation`, `World`, `Physics`, `Audio`, `UI`. The engine ignores a soft constraint that names an absent system, so `WindZone` keeps one constraint, to run before `Physics`. Registration order decides the rest, and the physics module registers `WindZone` second, ahead of every system but Physics. The updated test `Without the scripting module the game UI module registers and orders its system` expects exactly this line.
   :::

5. You add a component and run all tests. Which test fails first, what does its message say, and what two changes fix it?

   :::answer{tests="feature"}
   The feature test fails, with the message that the feature scene must contain the component and give every property a non-default value on one entity. Add an entity with the component to `Feature.stscene`, with each value changed. The schema test passes without a change, because it allows components that its snapshot lacks, but you write the snapshot again so that later changes to the component are checked.
   :::

## Exercises

1. **Basic.** Remove the line `windDescriptor.AfterIfPresent = { "Scripting" };`. Predict the order that the engine logs, then check it with the line in the **Console**. Restore the line.

   Hint: the first registered system runs as early as its constraints allow, then the second, and so on.

   :::answer{tests="order"}
   The order becomes `WindZone`, `UI`, `Scripting`, `Animation`, `World`, `Physics`, `Audio`. `Physics` is registered first and must follow `Scripting`, so it stays late. The wind system is registered second and has only the constraint to run before `Physics`, so it runs as early as it can: ahead of everything else. The tests of `Scene.Systems` that name the order fail on it, which shows that the constraint is part of the system's contract, not a detail.
   :::

2. **Medium.** Change the registered name `WindZone` to `WindArea`, in the registration only, and leave the file `Feature.stscene` as it is. Predict what the engine does with the scene, and which tests fail, then build and run the suites of this page and the feature test. Then migrate the name so that every test passes again. The display name stays `Wind Zone`.

   Hint: look at the warning that `Scene.Serialization` expects for a name that no module registers.

   :::answer{tests="feature declare-register" solution="tutorials/world/tutorial-component/exercise-2.patch"}
   The scene file still holds `"WindZone"`, a name that no component has now. The engine loads the scene, warns once, `Unknown component 'WindZone' (1 entity) kept unchanged`, and keeps the JSON in a runtime-only holder on the entity. The entity gets no wind zone component, so the system gathers no zone, and saving the scene writes the old JSON back unchanged: no data is lost, but nothing acts on it.

   With the rename alone, six test cases of the page's suites fail. Two are in `Reflection`: its list of built-in components and the wind zone's own test name `WindZone`. `Reflection.ComponentSchema` finds the `WindZone` of its snapshot no longer registered. `Engine.Modules` fails once, because its build without the module of the game's user interface (UI) now lists `WindZone` among the feature scene's :term[unknown components]{id=unknown-component}.

   `Scene.Serialization` fails twice. Its check that every committed scene loads without warnings meets the feature scene's warning. Its round trip test loads a document that names `WindZone`, finds no component and stops the program with `test case CRASHED: SIGABRT`, so the test cases after it do not run. The feature test fails too: each of its test cases that loads the feature scene meets the warning, and no entity holds `WindArea`.

   The rule behind it is the one of the second section: a registered name is the :term[file format]{id=file-format}, so a rename needs a migration of every file. The worked solution is that migration. It renames in five places: the registration, two tests, the feature scene and the snapshot. It adds a test that loads an old document and checks the warning, the kept JSON and the empty list, so `Physics.WindZone` then passes with three test cases.
   :::

3. **Hard.** Add a fourth property, `Turbulence`, a float with a slider from 0 to 1 and a tooltip, default 0. Make every test of this page pass again. Which tests fail if you change only the struct and the registration?

   Hint: the registration order of properties matters to files and :term[cooked scenes]{id=cooked-scene}: add the new one last.

   :::answer{tests="tests feature"}
   Add the member to the struct. Add a `Property` with `Slider(0.0f, 1.0f)` and a tooltip after the others in the registration. Give `Gust` a value other than 0, add the property to the reflection test, and write the snapshot again.

   With only the struct and the registration, two tests fail. The feature test fails because no entity has a non-default `Turbulence`. `Reflection.ComponentSchema` fails because the snapshot compares a listed component whole, so a property it lacks counts as a difference. The round trip test needs no change.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsComponents.h` and `PhysicsComponents.cpp`: the physics components and their registration, where the wind zone joins `RigidBody` and the colliders.
- `WindZoneSystem.h` and `WindZoneSystem.cpp`, in `Strata/src/Strata/Physics/`: the system that gathers the zones.
- `Strata/src/Strata/Physics/PhysicsRegistration.cpp`: `RegisterPhysicsModule`, which the engine's module table calls.
- `Strata/src/Strata/Engine/BuiltinModules.cpp`: the :term[composition root]{id=composition-root}, which freezes the registries and logs the update order.
- `Strata/src/Strata/Scene/SceneSystem.h`: the descriptor, the constraints and `MakeSceneSystemDescriptor`.
- `WindZoneTests.cpp` in `StrataTests/src/Physics/`, `ReflectionTests.cpp` and `SerializationTests.cpp` in `StrataTests/src/Scene/`: the tests of the component.
- `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene` and `StrataTests/Architecture/ComponentSchema.json`: the feature scene and the snapshot.
- `.claude/skills/strata-add-component/SKILL.md`: the engine's own checklist, which this page follows.

## Further reading

- The EnTT documentation on the author's pages (skypjack.github.io), for the registry that stores the components and the views that visit them: intermediate.
- Robert Nystrom, "Game Programming Patterns", chapter "Component", on gameprogrammingpatterns.com: why games split data into components: beginner.
- [doctest's documentation of its command line](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): `--test-suite` and the other filters: beginner.
