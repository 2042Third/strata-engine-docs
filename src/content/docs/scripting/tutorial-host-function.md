---
id: scripting/tutorial-host-function
title: "Tutorial: adding a host function and a callback"
description: "Let scripts read the wind of a wind zone through a new host function, and hear when it changes through a callback, with the tests the engine demands."
kind: tutorial
size: L
tracks: [E]
needs: [scripting/host-api, world/tutorial-component, core/first-change]
time: 240
learn:
  - id: scene-service
    text: explain why a script reaches the Physics module through a scene service, and build one that the module's system offers
  - id: host-function
    text: write a host function end to end, from the table member to the SDK wrapper and its tests
  - id: append-only
    text: predict what the build and an older engine do after a member is appended to the table, and after one is inserted
  - id: callback
    text: add a callback to the class descriptor, the SDK and the dispatch, read only when the descriptor covers it
  - id: feature-demand
    text: explain what the feature test demands of a new host function, SDK function and callback
since: 0.3.0
status: final
---

## What you will make

You will let scripts read the wind of the wind zones that [the component tutorial](../world/tutorial-component.md) added. A new :term[host function]{id=host-function} behind the function `GetStrength` of a new class `Wind` answers how strong the wind is at a place, and a new :term[callback]{id=callback}, `OnWindChanged`, tells a zone's script when its strength changes.

```mermaid caption="The change in two halves: a question that flows from the script to the wind zones, and an answer that flows back to the script." alt="Two rows of boxes. In the top row a script module asks, the table of host functions forwards the question, a scene service passes it on and the wind zone system answers. In the bottom row the wind zone system notices a change, the scene service tells the script system, and the script system calls the script."
flowchart LR
    S["Script module"] -->|"Wind::GetStrength"| T["Host function table"]
    T --> V["Scene service"]
    V --> W["Wind zone system"]
    W -->|"strength changed"| V
    V --> Y["Script system"]
    Y -->|"OnWindChanged"| S
```

## Why a script cannot see the wind yet

A zone has a strength, a radius and a center, and a system gathers the zones in every :term[fixed step]{id=fixed-step}. A script, though, lives in another program unit: a script module, a library that the engine loads and that never links against the engine. Its code builds only against a small software development kit (:term[SDK]{id=sdk}) of :term[headers]{id=header}. The module knows the engine only through plain data of the C language, behind an :term[application binary interface]{id=abi} (ABI), so it cannot call `WindZoneSystem`.

Two kinds of door connect the module and the engine. A host function is a function the engine hands to the module, which the script calls to ask something of the engine. A callback is a function the module hands to the engine, which the engine calls to tell a script something.

Take two zones. The `Breeze` sits at the origin with a strength of 10 N and a radius of 5 m. The `Gust` sits 3 m along the x axis with 25 N and 8.5 m. A script at (4, 0, 0) is 4 m from the Breeze and 1 m from the Gust, so both reach it and it should read 10 + 25 = 35 N. At (7, 0, 0) the Breeze is 7 m away, beyond its 5 m, and only the Gust reaches, so the answer is 25 N.

Two problems stand in the way. The first is compatibility. A game ships a script module built once, and players run it on many engine versions, so the table of host functions must change in a way that old and new meet safely. Strata solves it by appending: a new function goes at the end of the table, an old module never reads that far, and a new module checks that the table it received is long enough. Inserting in the middle would shift every later function, and an old module would call the wrong one.

The second problem is the layers. The wind zone belongs to the Physics module, and the table of `StrataTests/Architecture/Layers.json` lets the Scripting layer include only Core, Input, Asset, Reflection and Scene. Scripting must not include the physics header, and the test `Architecture.Layering` fails if it does.

The way out is the one that the engine already uses for bodies and contacts. The Scene layer defines an interface. The Physics module's system offers it for as long as it exists. The Scripting layer asks the scene for it, and gets nothing back when no system offers it. That interface is a scene service; [the systems page](../world/systems.md) teaches the idea, and you build one here.

:::why[A service instead of an include]
An include would let the host function read the zones directly and save you an interface. It would also make a game that leaves physics out fail to build its script layer, and it would let any future module reach into any other. The service costs one interface and one lookup, and in return a scene that plays without physics gives the script the failure value and a log line instead of a crash.
:::

The callback has the same two problems. Its descriptor, `StrataScriptClassDesc`, also grows only at its end, and the engine reads a new callback only when the module's descriptor is large enough to hold it. The wind system also raises the event, so the same service idea applies in the other direction: the system offers a place to listen, and the script system listens.

## What you need

- The source build of [your first engine change](../core/first-change.md): a clone at the book's commit, its :term[submodules]{id=submodule} and a `Debug` build of your system's :term[CMake preset]{id=cmake-preset}. Every command below writes `<preset>` for that preset: `windows`, `linux` or `macos`.
- The wind zone chain: [the component tutorial](../world/tutorial-component.md) and then the :term[gizmo]{id=gizmo-start} that [the debug drawing page](../gpu/debug-drawing.md) asks for in its exercise. A reader who skipped that exercise applies its solution patch first. The patch of this page applies on top.
- Time: about four hours. The first build compiles again every file that includes the script header, and the last full test run is the longest wait.
- No file to import and no editor to run: every step is a code change, a build or a test run in a terminal. You change or add about twenty files, shown as blocks of one patch.

:::files[The files of the change]

- `Strata/src/Strata/`
  - `Scene/SceneServices.h`: the two new interfaces
  - `Physics/WindZoneSystem.h`, `WindZoneSystem.cpp`: the system offers them and raises the change
  - `Scripting/ScriptHostAPI.cpp`: the host function and its table entry
  - `Scripting/ScriptModule.cpp`, `ScriptModule.h`, `ScriptTypes.h`, `ScriptTypes.cpp`, `ScriptSystem.cpp`, `ScriptSystem.h`: the callback
- `StrataScriptCore/Include/StrataScript/`
  - `ScriptABI.h`: the C table and the :term[class descriptor]{id=class-descriptor}
  - `Wind.h`, `StrataScript.h`, `Script.h`: the :term[SDK]{id=sdk}
- `StrataTests/`
  - `src/Physics/WindZoneTests.cpp`, `src/Scripting/ScriptWindTests.cpp`, `src/Scripting/ScriptWindEventTests.cpp`: the tests; `src/Scripting/ScriptModuleTests.cpp`: the classes the test module holds
  - `Scripts/API/` and `Scripts/Invalid/Malformed.cpp`: the test modules
  - `FeatureTest/`: the feature scripts and the feature scene
- `Docs/Architecture.md`: two rows of its table of scene services

:::

## Offer the wind through a scene service

The Physics module's system will offer a small interface with one question: how strong is the wind at this position? You write the interface in the Scene layer, where the Scripting layer may see it, and let the wind zone system offer it.

:::::steps

1. Read how the physics system offers its services. The model has the rule you follow: register in the :term[constructor]{id=constructor}, then undo it in the :term[destructor]{id=destructor}, in the opposite order.

   ```cpp src="Strata/src/Strata/Physics/PhysicsSystem.cpp#L58-L80"
   PhysicsSystem::PhysicsSystem(Scene& scene)
   	: m_Scene(scene), m_Settings(GetDefaultSettings())
   {
   	m_Scene.RegisterService<ICollisionEventSource>(*this);
   	m_Scene.RegisterService<IBodyMotionQuery>(*this);
   	m_Scene.RegisterService<IBodyControl>(*this);
   	m_Scene.RegisterService<IPhysicsQueries>(*this);
   	m_Scene.RegisterService<ICharacterControl>(*this);
   	m_Scene.RegisterService<IPhysicsCapacity>(*this);
   	m_Scene.RegisterService<IPhysicsDiagnostics>(*this);
   }

   PhysicsSystem::~PhysicsSystem()
   {
   	OnRuntimeStop();
   	m_Scene.UnregisterService<IPhysicsDiagnostics>(*this);
   	m_Scene.UnregisterService<IPhysicsCapacity>(*this);
   	m_Scene.UnregisterService<ICharacterControl>(*this);
   	m_Scene.UnregisterService<IPhysicsQueries>(*this);
   	m_Scene.UnregisterService<IBodyControl>(*this);
   	m_Scene.UnregisterService<IBodyMotionQuery>(*this);
   	m_Scene.UnregisterService<ICollisionEventSource>(*this);
   }
   ```

   1. **Lines 61–67:** each `RegisterService` call names an interface and hands over the system itself, which implements it.
   2. **Lines 72–79:** the destructor first stops the system's own work, then removes the services in the reverse order of the registration.

   **You should see:** two functions of the physics system, a constructor with seven registrations and a destructor with seven calls that undo them.

   **If you do not see it:** the file differs from this description when your clone is not at the book's commit. Move it there, as the first change does.

2. Declare the interface in `Strata/src/Strata/Scene/SceneServices.h`. Add the block after the :term[animation event]{id=animation-event-notify} source, before the physics capacity banner. The comment above the file names the providers; add the wind zone system to its list as well.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-10"
    	};
    
   +	//////////////////////////////////////////////////////////////////////////
   +	// Wind
   +	//////////////////////////////////////////////////////////////////////////
   +
   +	// The wind of a playing scene (the Physics module's WindZoneSystem).
   +	class IWindZones
   +	{
   +	public:
   +		virtual ~IWindZones() = default;
   +
   +		// The strength, in newtons, that the active zones reaching a world position add up to, as of the last fixed step: a
   +		// zone reaches the positions within its radius of its center. 0 where no zone reaches, and before the first step.
   +		virtual float GetStrengthAt(const glm::vec3& position) const = 0;
   +	};
   +
    	//////////////////////////////////////////////////////////////////////////
    	// Physics capacity
   ```

   1. **Lines 7–8:** the interface lives in the Scene layer, so every layer that may include the scene may use it.
   2. **Line 11:** a virtual destructor, as for every service, because the system owns the object.
   3. **Lines 13–15:** one query, `const`, with the unit in its comment: newtons, and the rule that a zone reaches a position within its radius.

   **You should see:** a class with one :term[pure virtual function]{id=pure-virtual-function} between the animation and physics capacity services.

   **If you do not see it:** the build of the next step reports an unknown `IWindZones` when the block landed outside `namespace Strata`. Move it inside.

3. Let `WindZoneSystem` offer it. In the header, include `SceneServices.h`, derive from `IWindZones` next to `SceneSystem`, declare `~WindZoneSystem() override;` and declare `GetStrengthAt` with `override`. In the :term[source file]{id=source-file}, write the lines of this block of the patch, but omit lines 4 and 9, which add and remove a second service that the callback section adds.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-3"
    		: m_Scene(scene)
    	{
   +		m_Scene.RegisterService<IWindZones>(*this);
   +		m_Scene.RegisterService<IWindEventSource>(*this);
   +	}
   +
   +	WindZoneSystem::~WindZoneSystem()
   +	{
   +		m_Scene.UnregisterService<IWindEventSource>(*this);
   +		m_Scene.UnregisterService<IWindZones>(*this);
   +	}
   +
   +	float WindZoneSystem::GetStrengthAt(const glm::vec3& position) const
   +	{
   +		float strength = 0.0f;
   +		for (const WindZoneSample& zone : m_Zones)
   +		{
   +			// Both modes reach the same sphere; the mode decides only the direction of the push, which comes later.
   +			if (glm::distance(position, zone.Position) <= zone.Radius)
   +				strength += zone.Strength;
   +		}
   +		return strength;
    	}
    
   ```

   1. **Lines 3–10:** the constructor registers the service on line 3 and the destructor removes it on line 10, so it exists for exactly as long as the system.
   2. **Lines 13–22:** the answer adds the strength of every gathered zone whose center lies within its radius of the position; the comparison `<=` makes the edge of a zone belong to it.
   3. **Line 18:** both modes reach the same sphere. The mode decides only the direction of a later push, so the query ignores it.

   **You should see:** the system class with a destructor and a query, and `GetStrengthAt` reading `m_Zones`, the list that the last fixed step gathered.

   **If you do not see it:** the :term[linker]{id=linker} reports an undefined destructor of `WindZoneSystem` when the destructor is declared but not written. Add it to the source file.

4. Test the service with the numbers of the introduction. Add this test case to `WindZoneTests.cpp` in `StrataTests/src/Physics/`, after the first two test cases, then build and run the suite.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-49"
    	}
    
   +	TEST_CASE("The service adds up the strengths of the zones that reach a position")
   +	{
   +		Scene scene;
   +		const auto addZone = [&scene](const char* name, const glm::vec3& position, float strength, float radius)
   +		{
   +			Entity zone = scene.CreateEntity(name);
   +			zone.GetTransform().Translation = position;
   +			zone.MarkModified<TransformComponent>();
   +			WindZoneComponent& wind = zone.AddComponent<WindZoneComponent>();
   +			wind.Strength = strength;
   +			wind.Radius = radius;
   +			return zone;
   +		};
   +		addZone("Breeze", { 0.0f, 0.0f, 0.0f }, 10.0f, 5.0f);
   +		addZone("Gust", { 3.0f, 0.0f, 0.0f }, 25.0f, 8.5f);
   +
   +		scene.OnRuntimeStart();
   +		const IWindZones* wind = scene.GetService<IWindZones>();
   +		REQUIRE(wind != nullptr);
   +		CHECK(wind->GetStrengthAt({ 4.0f, 0.0f, 0.0f }) == doctest::Approx(0.0f)); // Before the first step
   +
   +		StepScene(scene, 1);
   +		CHECK(wind->GetStrengthAt({ 4.0f, 0.0f, 0.0f }) == doctest::Approx(35.0f));  // Both reach it
   +		CHECK(wind->GetStrengthAt({ 5.0f, 0.0f, 0.0f }) == doctest::Approx(35.0f));  // On the Breeze's edge: inside
   +		CHECK(wind->GetStrengthAt({ 7.0f, 0.0f, 0.0f }) == doctest::Approx(25.0f));  // Only the Gust reaches it
   +		CHECK(wind->GetStrengthAt({ 20.0f, 0.0f, 0.0f }) == doctest::Approx(0.0f));  // Neither does
   +		scene.OnRuntimeStop();
   +	}
   +
    	TEST_CASE("A wind zone shows a sphere of its radius around its origin, and none for a zone without reach")
    	{
   ```

   1. **Lines 16–17:** the two zones of the introduction, built by one small :term[lambda]{id=lambda} so that each line says only what differs.
   2. **Line 22:** before any fixed step nothing is gathered, so the wind is 0.
   3. **Lines 25–28:** 35 N where both reach, 35 N exactly on the Breeze's edge at 5 m, 25 N where only the Gust reaches, 0 N far away.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Physics.WindZone
   ```

   **You should see:** no failed test case, and the new case among those that ran. The first build compiles again every file that includes `SceneServices.h`.

   **If you do not see it:** a result of 25 at (4, 0, 0) means the Breeze was not gathered: check that the lambda marks the transform as modified, as the :term[transform contract]{id=transform-contract} demands.

:::::

## Add the host function

A host function is one member of a table of C :term[function pointers]{id=function-pointer}, `StrataScriptHostAPI`. Adding one touches five places: the table, the implementation, the list that checks the table, the SDK function that scripts call, and the tests. The newest group in the table, `GetStepAlpha` and its neighbors, is your model at every place.

:::::steps

1. Append the member at the end of `StrataScriptHostAPI` in `StrataScriptCore/Include/StrataScript/ScriptABI.h`, after `ResetInterpolation` and before the comment that says new functions are appended there.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-37"
    		bool (*ResetInterpolation)(StrataScriptContext* context, StrataScriptEntityID entity);
    
   +		/*
   +		 * Wind (added after ResetInterpolation, ABI version 1: check ST_SCRIPT_HAS_MEMBER before use). GetWindStrength is the
   +		 * strength, in newtons, that the active wind zones reaching the world position (x, y, z; three floats) add up to: 0 where
   +		 * no zone reaches. It also returns 0 for a null or non-finite position and while the scene plays without wind zones.
   +		 */
   +		float (*GetWindStrength)(StrataScriptContext* context, const float* position);
   +
    		/* New functions are appended here (see the compatibility rules above). */
    	} StrataScriptHostAPI;
   ```

   1. **Lines 3–7:** the comment says since when the function exists and what it returns for each failure. A script author reads this and nothing else.
   2. **Line 8:** the position travels as a pointer to three floats, plain C data, and the result is a `float`, so no engine type crosses the boundary.

   Build now, before you write anything else.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   ```

   **You should see:** the build stops in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` at a `static_assert`, with the message `ST_SCRIPT_HOST_FUNCTIONS must list every member of StrataScriptHostAPI after ABIVersion, in declaration order`.

   **If you do not see it:** you placed the member before an older one or in a copy of the :term[struct]{id=struct}. The member must be the last one, and the failure shows that the engine refuses a table and a list that disagree.

   **Why:** the engine builds its table from a list, `ST_SCRIPT_HOST_FUNCTIONS`, and checks at :term[compile time]{id=compile-time} that the list covers the struct exactly, in order, without a gap. A forgotten entry would leave a :term[null pointer]{id=null-pointer} in the table that a script calls.

2. Write the implementation next to the model, in `ScriptHostAPI.cpp`. The model is the smallest host function there, with its comment and its failure value.

   ```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L3378-L3386"
   float HostGetStepAlpha(StrataScriptContext* context)
   {
   	// Without a context: the latest pose, what a scene that does not interpolate draws.
   	return HostCall("GetStepAlpha", 1.0f, [&]()
   	{
   		ScriptSystem* system = ResolveContext(context, "GetStepAlpha");
   		return system ? system->GetScene().GetStepAlpha() : 1.0f;
   	});
   }
   ```

   Then add yours, before the banner of the table, and a constant for the message above it, next to `c_WithoutAnimation`.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-13"
    		}
    
   +		////////////////////////////////////////////////////////////////////////////////
   +		// Wind (IWindZones)
   +		////////////////////////////////////////////////////////////////////////////////
   +
   +		float HostGetWindStrength(StrataScriptContext* context, const float* position)
   +		{
   +			// Without a context, a usable position or the service: no wind.
   +			return HostCall("GetWindStrength", 0.0f, [&]()
   +			{
   +				ScriptSystem* system = ResolveContext(context, "GetWindStrength");
   +				const std::optional<glm::vec3> point = system ? ReadVector3(*system, position, "position", "GetWindStrength") : std::nullopt;
   +				const IWindZones* wind = point ? system->GetScene().GetService<IWindZones>() : nullptr;
   +				if (point && !wind)
   +					system->ReportProblem("GetWindStrength", c_WithoutWind);
   +				return wind ? wind->GetStrengthAt(*point) : 0.0f;
   +			});
   +		}
   +
    		////////////////////////////////////////////////////////////////////////////////
    		// The table
   ```

   1. **Line 10:** `HostCall` runs the body and catches any exception, so none reaches the module; the second argument is the failure value, 0 here.
   2. **Line 12:** `ResolveContext` checks the caller: a valid context, the :term[main thread]{id=main-thread}, a script call in progress and a module that has not crashed. Otherwise it returns null, and it logs why unless the module crashed.
   3. **Line 13:** `ReadVector3` rejects a null or non-finite position and reports it with `ReportProblem`; a script cannot make the engine read garbage.
   4. **Lines 14–17:** the function asks the scene for the service at each call. Where no system offers it, the function reports the absent module once and answers 0.

   **You should see:** the function between the :term[interpolation]{id=interpolation} functions and the table, and the constant `c_WithoutWind` beside the other three messages.

   **If you do not see it:** the build reports an unknown `IWindZones` when the file does not include the scene services header. It does already; check that the interface from the first section is spelled the same.

3. List it at the end of the table. The model shows the end of the list.

   ```cpp src="Strata/src/Strata/Scripting/ScriptHostAPI.cpp#L3590-L3596"
   X(GraphicsSetOption) \
   X(GraphicsGetOptionChoice) \
   X(GraphicsResetOptions) \
   X(GraphicsSaveOptions) \
   X(GetStepAlpha) \
   X(GetDrawnTransform) \
   X(ResetInterpolation)
   ```

   Give the line `X(ResetInterpolation)` a trailing backslash and add the line `X(GetWindStrength)` below it, with none. Build.

   **You should see:** the build passes the `static_assert`. In non-Dist builds the same list also makes a counter for each function, which the feature test reads.

   **If you do not see it:** when the assertion still fails, the order of the list differs from the struct. Both end with `ResetInterpolation` and then `GetWindStrength`.

4. Wrap the function in the SDK, so that scripts never touch the table. Create `Wind.h` in `StrataScriptCore/Include/StrataScript/`, and add `#include "StrataScript/Wind.h"` to `StrataScript.h`, between `Value.h` and `World.h`. The model is `Time::GetStepAlpha`.

   ```cpp src="StrataScriptCore/Include/StrataScript/Time.h#L72-L76"
   static float GetStepAlpha()
   {
   	const StrataScriptHostAPI* host = ST_SCRIPT_DETAIL_HOST_WITH(GetStepAlpha);
   	return host ? host->GetStepAlpha(Detail::GetContext()) : 1.0f;
   }
   ```

   The new header follows the model: one static function that checks the table, calls through it and falls back to 0.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-40"
   +#pragma once
   +
   +#include "StrataScript/Host.h"
   +
   +#include <glm/glm.hpp>
   +
   +namespace Strata
   +{
   +
   +	// The wind of the scene's wind zones.
   +	class Wind
   +	{
   +	public:
   +		// The strength, in newtons, that the active wind zones reaching a world position add up to; 0 where none reaches it,
   +		// and with an engine that has no wind zones.
   +		static float GetStrength(const glm::vec3& position)
   +		{
   +			const StrataScriptHostAPI* host = ST_SCRIPT_DETAIL_HOST_WITH(GetWindStrength);
   +			return host ? host->GetWindStrength(Detail::GetContext(), &position.x) : 0.0f;
   +		}
   +	};
   +
   +}
   ```

   1. **Line 18:** `ST_SCRIPT_DETAIL_HOST_WITH` returns the table only when it is long enough to hold `GetWindStrength` and the entry is not null.
   2. **Line 19:** with an older engine the answer is the fallback, 0, and the script keeps running.

   **You should see:** a header with one class and one static function.

   **If you do not see it:** a script that includes `StrataScript.h` and cannot find `Wind` has no include line for the new header.

5. Test the function with a script module of the tests, which mimics a game. The model checks what an older engine gives.

   ```cpp src="StrataTests/Scripts/API/TransformScripts.cpp#L96-L103"
   StrataScriptHostAPI older = *Detail::GetHost();
   older.StructSize = static_cast<uint32_t>(offsetof(StrataScriptHostAPI, GetStepAlpha));
   CheckUnavailable(older, "an older engine");
   StrataScriptHostAPI missing = *Detail::GetHost();
   missing.GetStepAlpha = nullptr;
   missing.GetDrawnTransform = nullptr;
   missing.ResetInterpolation = nullptr;
   CheckUnavailable(missing, "null entries");
   ```

   Create `WindScripts.cpp` in `StrataTests/Scripts/API/`. The suite `Scripting.Module` compares the classes of this module with a list, so add `"WindProbe"` at the end of `expectedClasses` in `ScriptModuleTests.cpp` of the folder `StrataTests/src/Scripting/`.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-46"
   +// Wind API test scripts.
   +
   +#include "TestScripts.h"
   +
   +#include <cstddef>
   +
   +using namespace Strata;
   +using namespace ScriptTests;
   +
   +// Wind::GetStrength: on the entity of a wind zone it reads the wind at the zone's center in OnLateUpdate, and checks once
   +// what an older engine gives.
   +class WindProbe : public CheckingScript
   +{
   +public:
   +	float Strength = -1.0f; // Wind::GetStrength at the entity's world position in the latest OnLateUpdate
   +
   +	void OnLateUpdate(float) override
   +	{
   +		Strength = Wind::GetStrength(GetTransform().GetWorldPosition());
   +		if (!m_OlderChecked)
   +		{
   +			m_OlderChecked = true;
   +			StrataScriptHostAPI older = *Detail::GetHost();
   +			older.StructSize = static_cast<uint32_t>(offsetof(StrataScriptHostAPI, GetWindStrength));
   +			CheckUnavailable(older, "an older engine");
   +			StrataScriptHostAPI missing = *Detail::GetHost();
   +			missing.GetWindStrength = nullptr;
   +			CheckUnavailable(missing, "a null entry");
   +		}
   +	}
   +private:
   +	// Without the function: no wind.
   +	void CheckUnavailable(const StrataScriptHostAPI& host, const char* what)
   +	{
   +		const ScopedHost scoped(&host);
   +		Expect(Wind::GetStrength(glm::vec3(0.0f)) == 0.0f, what);
   +	}
   +
   +	bool m_OlderChecked = false;
   +};
   +
   +ST_SCRIPT_CLASS(WindProbe)
   +{
   +	ST_SCRIPT_FIELD(Checks);
   +	ST_SCRIPT_FIELD(Failure);
   +	ST_SCRIPT_FIELD(Strength);
   +}
   ```

   1. **Line 19:** the script reads the wind at its own position and keeps the answer in a field, which the test reads back.
   2. **Lines 23–25:** the copy of the table gets a `StructSize` that ends before the new member: that is an older engine.
   3. **Lines 26–28:** a copy with a null entry: an engine that has the member but no function. Both must give 0, not a crash.

   **You should see:** a class that derives from `CheckingScript`; its `Expect` counts each check.

   **If you do not see it:** the module compiles every file of the folder, so the new file needs no :term[CMake]{id=cmake} change, but only a configure run finds it: run `cmake --preset <preset>` once.

6. Add the test that plays a scene with the script. Create `ScriptWindTests.cpp` in `StrataTests/src/Scripting/`, run the :term[configure step]{id=configure-step} again because you added files, build and run the suite.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-53"
   +#include <doctest/doctest.h>
   +
   +#include "Scripting/ScriptTestUtils.h"
   +#include "Strata/Physics/PhysicsComponents.h"
   +#include "TestHelpers.h"
   +
   +using namespace Strata;
   +using namespace Strata::Tests;
   +
   +#if ST_WITH_PHYSICS
   +TEST_SUITE("Scripting.Wind")
   +{
   +	TEST_CASE("Wind API: a script reads the wind at its zone's center, also after the strength changed")
   +	{
   +		ScopedScriptEngine engine(GetTestScriptModule(STRATA_TEST_SCRIPTS_API));
   +		Scene scene;
   +		Entity gust = scene.CreateEntity("Gust");
   +		gust.AddComponent<WindZoneComponent>().Strength = 25.0f;
   +		AddScriptEntry(gust, "WindProbe");
   +		scene.OnRuntimeStart();
   +		ScriptSystem& system = GetScriptSystem(scene);
   +
   +		RunFrames(scene, 5);
   +		CHECK(GetField<float>(system, gust, "WindProbe", "Strength") == doctest::Approx(25.0f));
   +
   +		gust.GetComponent<WindZoneComponent>().Strength = 40.0f;
   +		RunFrames(scene, 5);
   +		CHECK(GetField<float>(system, gust, "WindProbe", "Strength") == doctest::Approx(40.0f));
   +		CheckScriptChecks(system, gust, "WindProbe", 2);
   +		scene.OnRuntimeStop();
   +	}
   +}
   +#endif
   ```

   1. **Lines 17–19:** a zone of 25 N with the default radius, and the probe script on the same entity, so the probe stands at the center of the zone.
   2. **Lines 23–24:** after five frames the script read 25 N.
   3. **Lines 26–28:** change the strength, play five more frames, and the script reads 40 N.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Scripting.Wind,Scripting.API,Scripting.Module
   ```

   **You should see:** no failed test case. The checks of the probe count too: `CheckScriptChecks` demands at least two.

   **If you do not see it:** a failure named `an older engine` means the SDK called the function through a table that did not hold it: check the use of `ST_SCRIPT_DETAIL_HOST_WITH` in `Wind.h`.

7. Run the feature test before you touch it. The feature test demands that every host function and every SDK function is used by a script of its project, and yours is not yet.

   ```sh
   ctest --preset <preset>-debug -R "^StrataTests\.FeatureTest$"
   ```

   **You should see:** the test fails and prints two messages among others: `Host function GetWindStrength was never called` and `SDK class Wind is not used by the feature scripts`.

   **If you do not see it:** when it passes, the run used an older build. Build all targets again.

   **Why:** [the feature test page](../engineering/feature-test.md) teaches the whole check. The part that matters here is that the engine counts calls of each table entry during the run, and reads the SDK headers to find functions that no feature script calls.

8. Call the function from a feature script. Create `WindFeatures.cpp` in `StrataTests/FeatureTest/Scripts/`, and give the feature scene an entity that carries it.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-44"
   +// Wind::GetStrength, read at "Gust", the feature scene's wind zone (25 newtons within 8.5 meters of its center).
   +
   +#include "FeatureScript.h"
   +
   +using namespace Strata;
   +using namespace FeatureTest;
   +
   +class WindFeatures : public FeatureScript
   +{
   +public:
   +	static constexpr int32_t c_CheckFrame = 5;
   +
   +	void OnCreate() override
   +	{
   +		Journal(*this, "WindFeatures", "OnCreate");
   +	}
   +
   +	void OnLateUpdate(float) override
   +	{
   +		if (GetFrame() != c_CheckFrame)
   +			return;
   +		const Entity gust = Scene::FindEntityByName("Gust");
   +		if (!gust)
   +		{
   +			Expect(false, "the feature scene has the wind zone Gust");
   +			return;
   +		}
   +		const glm::vec3 center = gust.GetTransform().GetWorldPosition();
   +		Expect(Near(Wind::GetStrength(center), 25.0f), "the wind at the center of a zone is its strength");
   +		Expect(Near(Wind::GetStrength(center + glm::vec3(8.0f, 0.0f, 0.0f)), 25.0f), "the wind reaches 8 meters from the center");
   +		Expect(Wind::GetStrength(center + glm::vec3(9.0f, 0.0f, 0.0f)) == 0.0f, "no wind 9 meters from the center, beyond the radius");
   +		Completed = true;
   +	}
   +};
   +
   +ST_SCRIPT_CLASS(WindFeatures)
   +{
   +	ST_SCRIPT_FIELD(Checks);
   +	ST_SCRIPT_FIELD(Failure);
   +	ST_SCRIPT_FIELD(Completed);
   +}
   ```

   1. **Lines 22–28:** the script finds the `Gust` that the component tutorial put in the feature scene and reads its center.
   2. **Lines 29–31:** 25 N at the center and at 8 m, inside the radius of 8.5 m, and 0 N at 9 m, outside it.
   3. **Line 32:** `Completed` tells the runner that the scenario ran to its end.

   Add the entity with this block to `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene`, after the `Gust` entity.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-42"
    				},
    				"ID": "F7E00000000000A0"
   +			},
   +			{
   +				"Components": {
   +					"Name": {
   +						"Name": "Wind Features"
   +					},
   +					"Script": {
   +						"Scripts": [
   +							{
   +								"Class": "WindFeatures",
   +								"Fields": {}
   +							}
   +						]
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
   +							0,
   +							42,
   +							0
   +						]
   +					}
   +				},
   +				"ID": "F7E00000000000A1"
    			}
    		],
   ```

   1. **Lines 6–16:** the name of the entity and its `Script` component with the class name `WindFeatures`.
   2. **Line 36:** the identifier is new: no other entity of the file may share it.

   Build and run the feature test again.

   **You should see:** the feature test passes. The two messages are gone, and the run has one more script that completed.

   **If you do not see it:** a :term[JSON]{id=json} error means a comma is missing after the closing brace of the `Gust` entity.

:::::

The host function works end to end. You changed one table and one list at their ends, and you kept the number `ST_SCRIPT_ABI_VERSION` at 1, because appending is compatible.

## Add the callback

A callback runs the other way: the engine calls the script. The descriptor that a module gives the engine for each class, `StrataScriptClassDesc`, lists the callbacks the class implements. The newest ones are the game user interface (UI) callbacks, ending with `OnUISubmit`, and they are your model.

:::::steps

1. Append the member to the end of `StrataScriptClassDesc`, in `ScriptABI.h`, after `OnUISubmit`.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-38"
    		uint32_t (*OnUISubmit)(StrataScriptInstance instance, StrataScriptEntityID widget);
    
   +		/*
   +		 * The strength of the wind zone on the script's entity changed between two fixed steps (added after OnUISubmit and
   +		 * read only when StructSize covers it); `strength` is the new one, in newtons. Called during the fixed step that saw it.
   +		 */
   +		uint32_t (*OnWindChanged)(StrataScriptInstance instance, float strength);
   +
    		/* New callbacks are appended here. */
    	} StrataScriptClassDesc;
   ```

   1. **Lines 3–6:** the comment says that the engine reads the member only when `StructSize` covers it, and what the argument means.
   2. **Line 7:** the first argument is always the script instance; the second is the new strength.

   Then add `OnWindChanged` to the enum `ScriptCallback` in `Strata/src/Strata/Scripting/ScriptTypes.h`, as its last value, and move the count with it.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-29"
    		OnUIValueChanged,
    		OnUIFocusChanged,
   -		OnUISubmit
   +		OnUISubmit,
   +		// The strength of the wind zone on the entity changed (see StrataScriptClassDesc and ScriptSystem).
   +		OnWindChanged
    	};
    
    	// How many callbacks there are: code that lists or counts every callback (script.status) goes up to this, so callbacks
    	// appended to the enum are included without edits there. Defined from the last value: keep it pointing at the last one.
   -	constexpr size_t c_ScriptCallbackCount = static_cast<size_t>(ScriptCallback::OnUISubmit) + 1;
   +	constexpr size_t c_ScriptCallbackCount = static_cast<size_t>(ScriptCallback::OnWindChanged) + 1;
    
    	const char* ScriptCallbackToString(ScriptCallback callback);
   ```

   1. **Lines 4–6:** the new value goes last, with a comment, never in the middle.
   2. **Line 12:** `c_ScriptCallbackCount` is defined from the last value, so the lists that go up to it include the new callback without more edits. The test `c_ScriptCallbackCount counts every callback` fails if you forget this line.

   Add the name to `ScriptCallbackToString` in `ScriptTypes.cpp`, as `"OnWindChanged"`.

   **You should see:** the enum with one more value and the count pointing at it.

   **If you do not see it:** a warning about a `switch` that names every callback, in `ScriptModule.cpp`, is expected now. The :term[compiler]{id=compiler} warns about each place that must know the new value, and the next steps fix them.

2. Give scripts the :term[virtual function]{id=virtual-function}. Seven places in `StrataScriptCore/Include/StrataScript/Script.h` change, each next to the same place of `OnUISubmit`. The comment of callbacks at the top gains a line, and the class `Script` gains the virtual function `OnWindChanged(float strength)`. The rest are the :term[thunk]{id=thunk}, a flag `CallbackFlag_OnWindChanged = 1u << 15`, a check that a class overrides it, the line of `GetCallbackFlags` that sets the flag, and the slot in the class record. The thunk is the piece that crosses the boundary.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-32"
    		}
    
   +		inline uint32_t WindChangedThunk(StrataScriptInstance instance, float strength)
   +		{
   +			Script* script = ToScript(instance);
   +			if (!script)
   +				return StrataScriptResult_InvalidArgument;
   +			return InvokeScript(ScriptAccess::GetInstanceContext(*script), [&]() { script->OnWindChanged(strength); });
   +		}
   +
    		// Per script class: its registered name and, while the module is loaded, its record.
    		template<typename T>
   ```

   1. **Line 3:** a thunk is a plain function with the C signature of the descriptor member; the descriptor holds its address.
   2. **Lines 5–7:** it turns the opaque instance back into a `Script`, and refuses a null one.
   3. **Line 8:** it calls the virtual function inside `InvokeScript`, which catches an exception of the script and turns it into a result code.

   The check that a class overrides the callback is a function named `OverridesOnWindChanged`, copied from `OverridesOnUISubmit` with the parameter type `float`. The class record sets `desc.OnWindChanged` to the thunk only for classes whose flags hold the new flag, and to null for the others, so the engine skips them entirely.

   **You should see:** seven small blocks in `Script.h`, one for each place; the thunk is the third.

   **If you do not see it:** a class that overrides the function but is never called has no flag: check the line `flags |= CallbackFlag_OnWindChanged` in `GetCallbackFlags`.

3. Read the new member in the engine, only when the module's descriptor holds it. The model is the end of the chain of reads in `ScriptModule.cpp`.

   ```cpp src="Strata/src/Strata/Scripting/ScriptModule.cpp#L1007-L1016"
   if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnAnimationEvent))
   	functions.OnAnimationEvent = descriptor->OnAnimationEvent;
   if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnUIClick))
   	functions.OnUIClick = descriptor->OnUIClick;
   if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnUIValueChanged))
   	functions.OnUIValueChanged = descriptor->OnUIValueChanged;
   if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnUIFocusChanged))
   	functions.OnUIFocusChanged = descriptor->OnUIFocusChanged;
   if (ST_SCRIPT_HAS_MEMBER(StrataScriptClassDesc, descriptor, OnUISubmit))
   	functions.OnUISubmit = descriptor->OnUISubmit;
   ```

   1. **Lines 1007–1008:** `ST_SCRIPT_HAS_MEMBER` compares the descriptor's `StructSize` with the end of the member. A module built before the member existed has a smaller size, and its memory is never read there.
   2. **Lines 1015–1016:** the last read is yours to follow: add the same two lines for `OnWindChanged`.

   In `ScriptModule.h`, add the member `OnWindChanged` to the struct `ClassFunctions`, which copies the functions out of the module while it is read under the crash guard. Add a line `{ ScriptCallback::OnWindChanged, functions.OnWindChanged != nullptr }` to the table of implemented callbacks, then write the call.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-17"
    	}
    
   +	ScriptCallResult ScriptModule::InvokeWindChangedCallback(const ScriptCallSite& site, StrataScriptInstance instance, float strength)
   +	{
   +		const ClassFunctions* functions = GetFunctions(site);
   +		if (!functions || !instance)
   +			return ScriptCallResult::Rejected;
   +		const auto function = functions->OnWindChanged;
   +		return function ? Call(site, [&]() { return function(instance, strength); }) : ScriptCallResult::Unavailable;
   +	}
   +
    	ScriptCallResult ScriptModule::InvokeUIEventCallback(const ScriptCallSite& site, StrataScriptInstance instance, ScriptCallback callback, uint64_t widget,
    		float value, bool focused)
   ```

   1. **Lines 5–7:** the function table was copied under the guard, so the call reads no module memory outside it.
   2. **Line 9:** `Call` runs the function under the crash guard. A module without the function gives `Unavailable`, not a failure.

   Declare `InvokeWindChangedCallback` in `ScriptModule.h`, and add the case `OnWindChanged` to the three `switch` statements that list every callback, in the calls for plain callbacks, contacts and UI events. Build.

   **You should see:** the build passes, with no warning about a missing enum value.

   **If you do not see it:** a warning that a `switch` does not handle `OnWindChanged` names the line. Add the case there and return `Rejected`.

4. Dispatch the callback from the system that raises it. The script system listens, and the wind zone system raises the event, through the second interface. Declare it at the end of `SceneServices.h`, after the audio output.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-11"
    	};
    
   +	// A wind zone whose strength differs from the one it had in the step before (WindZoneSystem), dispatched on the main thread
   +	// during the fixed step that saw the change.
   +	struct WindChangeInfo
   +	{
   +		Entity Zone;
   +		UUID ZoneID = UUID::Null();
   +		float Strength = 0.0f; // Newtons, after the change
   +	};
   +
   +	using WindChangeCallback = std::function<void(const WindChangeInfo&)>;
   +	using WindChangeListenerID = uint64_t;
   +
   +	// The strength changes of a playing scene's wind zones (the Physics module's WindZoneSystem). Listeners added while changes
   +	// are dispatched receive the next step's; a removed one is not called again.
   +	class IWindEventSource
   +	{
   +	public:
   +		virtual ~IWindEventSource() = default;
   +
   +		virtual WindChangeListenerID AddWindChangeListener(WindChangeCallback callback) = 0;
   +		virtual bool RemoveWindChangeListener(WindChangeListenerID id) = 0;
   +	};
   +
    }
   ```

   1. **Lines 5–10:** the event: the zone's entity and identifier and the new strength.
   2. **Lines 12–13:** a callback type and a listener identifier, the shapes of the animation events.
   3. **Lines 17–24:** an interface of two functions, to add a listener and to remove it; a removed listener is not called again.

   Give both new interfaces a row in the table of scene services of `Docs/Architecture.md`, after the row of `IAnimationEventSource`. Each row names the interface, `WindZoneSystem` as the system that offers it and `ScriptSystem` as its user.

   **You should see:** the event source interface at the end of the file, after the audio output, with its own comment.

   **If you do not see it:** a build error about `std::function` means the file lacks `#include <functional>`; it already has it.

5. Let the wind zone system raise it. In `WindZoneSystem.h`, derive also from `IWindEventSource`, declare its two functions, the private `Listener` struct, `DispatchChanges`, and the members `m_Listeners` and `m_NextListenerID`. In the source file, register the second service in the constructor and remove it first in the destructor: these are lines 4 and 9 of the block you omitted. Then change `OnFixedUpdate` and add the listener functions.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-5"
    			m_Zones.push_back({ handle, glm::vec3(m_Scene.GetWorldTransform(entity)[3]), zone.Strength, zone.Radius, zone.Mode });
    		}
   +
   +		// A zone that was gathered before and now holds another strength. The comparison is exact: a strength changes only
   +		// when someone writes it. A zone seen for the first time did not change.
   +		std::vector<WindChangeInfo> changes;
   +		for (const WindZoneSample& zone : m_Zones)
   +		{
   +			const auto before = std::find_if(previous.begin(), previous.end(), [&](const WindZoneSample& old) { return old.Handle == zone.Handle; });
   +			if (before == previous.end() || before->Strength == zone.Strength)
   +				continue;
   +			const Entity entity(zone.Handle, &m_Scene);
   +			changes.push_back({ entity, entity.GetUUID(), zone.Strength });
   +		}
   +		DispatchChanges(changes);
   +	}
   +
   +	WindChangeListenerID WindZoneSystem::AddWindChangeListener(WindChangeCallback callback)
   +	{
   +		if (!callback)
   +			return 0;
   +		const WindChangeListenerID id = m_NextListenerID++;
   +		m_Listeners.push_back({ id, std::move(callback) });
   +		return id;
   +	}
   +
   +	bool WindZoneSystem::RemoveWindChangeListener(WindChangeListenerID id)
   +	{
   +		const auto it = std::find_if(m_Listeners.begin(), m_Listeners.end(), [id](const Listener& listener) { return listener.ID == id; });
   +		if (it == m_Listeners.end())
   +			return false;
   +		m_Listeners.erase(it);
   +		return true;
   +	}
   +
   +	void WindZoneSystem::DispatchChanges(const std::vector<WindChangeInfo>& changes)
   +	{
   +		for (const WindChangeInfo& change : changes)
   +		{
   +			// A copy: a listener may add or remove listeners. One removed meanwhile is not called.
   +			const std::vector<Listener> listeners = m_Listeners;
   +			for (const Listener& listener : listeners)
   +			{
   +				const bool present = std::any_of(m_Listeners.begin(), m_Listeners.end(), [&](const Listener& entry) { return entry.ID == listener.ID; });
   +				if (present)
   +					listener.Callback(change);
   +			}
   +		}
    	}
    
   ```

   1. **Lines 4–5:** a change is a zone seen before whose strength differs now. The exact comparison is right because a strength changes only when someone writes it.
   2. **Line 10:** a zone seen for the first time did not change, so a scene that starts plays no change.
   3. **Lines 18–25:** adding a listener returns an identifier, and a null callback returns 0.
   4. **Lines 40–46:** the dispatch walks a copy of the list, so a listener may add or remove listeners, and skips one that was removed meanwhile.

   In `OnFixedUpdate`, before the gathering loop, keep the last step's list: `const std::vector<WindZoneSample> previous = std::move(m_Zones);`, then `m_Zones.clear();` as before. Include `<algorithm>`.

   **You should see:** the system with four new functions and a list of changes built at the end of the fixed step.

   **If you do not see it:** the linker names a missing `AddWindChangeListener` when a function is declared and not written.

6. Hook the script system to the event source. In `ScriptSystem.h`, declare `OnWindChanged(const WindChangeInfo& event)` and the member `m_WindListener`. In `ScriptSystem.cpp`, add the listener when the scene starts to run, and remove it when it stops, next to the UI listener, then write the function that finds the zone's scripts.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-25"
    	}
    
   +	////////////////////////////////////////////////////////////////////////////////
   +	// Wind
   +	////////////////////////////////////////////////////////////////////////////////
   +
   +	void ScriptSystem::OnWindChanged(const WindChangeInfo& event)
   +	{
   +		if (!m_Running || !GetUsableModule())
   +			return;
   +		auto it = m_Instances.find(event.ZoneID);
   +		if (it == m_Instances.end() || !event.Zone || !m_Scene.IsActiveInHierarchy(event.Zone))
   +			return;
   +
   +		// A copy: the callbacks may add or remove scripts (removed instances are flagged and skipped).
   +		const std::vector<Ref<Instance>> instances = it->second;
   +		for (const Ref<Instance>& instance : instances)
   +		{
   +			if (instance->Removed || instance->Disabled || !instance->Created || !instance->Handle || !instance->Class->Implements(ScriptCallback::OnWindChanged))
   +				continue;
   +			ScriptModule* module = GetUsableModule();
   +			if (!module)
   +				return;
   +			const ScriptCallSite site = MakeCallSite(*instance, ScriptCallbackToString(ScriptCallback::OnWindChanged));
   +			HandleCallResult(*instance, ScriptCallback::OnWindChanged, module->InvokeWindChangedCallback(site, instance->Handle, event.Strength));
   +		}
   +	}
   +
    	////////////////////////////////////////////////////////////////////////////////
    	// Change tracking
   ```

   1. **Lines 9–13:** nothing to do when play stopped, the module crashed, the zone has no scripts or it is inactive.
   2. **Lines 15–16:** a copy of the list of scripts, since a callback may add or remove scripts.
   3. **Lines 19–20:** a script is skipped when it was removed, disabled or not yet created, or when its class does not implement the callback.
   4. **Lines 24–25:** the call goes through `InvokeWindChangedCallback`, and `HandleCallResult` disables a script whose callback threw an exception.

   Build, then run the suite of the system and the script tests.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Physics.WindZone,Scripting*
   ```

   **You should see:** no failed test case yet, and no new test that exercises the callback: you add them next.

   **If you do not see it:** a crash at the end of a play means the listener was not removed before the services went away; check the stop path.

7. Test the callback, with a module that lacks it. The model for the descriptor is the existing case for `OnUISubmit`: a test module describes two classes, and the first has a descriptor size that ends before the new member. In the folder `StrataTests/Scripts/Invalid/`, add `CountWindChanged` and the case `OlderWindClass` to `Malformed.cpp`. Create the script `WindEventProbe` in `WindEventScripts.cpp` of the folder `StrataTests/Scripts/API/`, add `"WindEventProbe"` after `"WindProbe"` in `expectedClasses`, and write `ScriptWindEventTests.cpp` in `StrataTests/src/Scripting/` with two test cases.

   The first test case plays a zone with a probe, changes its strength from 25 N to 40 N and expects one call that carries 40. The second loads the broken module and expects that the first class does not implement `OnWindChanged` and the second does. Add a listener test case to `WindZoneTests.cpp` too: it expects no call at the first steps, one call after a change, and none after the listener is removed.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Physics.WindZone,Scripting*
   ```

   **You should see:** no failed test case. The second test case guards the `HAS_MEMBER` check of the callback: without it, the engine would read the first class's member beyond its short descriptor.

   **If you do not see it:** the module reports no class `First` when the :term[environment variable]{id=environment-variable} of the case is missing: the test sets it itself, so check the spelling of `OlderWindClass` in both files.

8. Call the callback from a feature script. Create `WindEventFeatures.cpp` in `StrataTests/FeatureTest/Scripts/`. It raises the strength of its zone from 25 N to 40 N at frame 10 and counts the calls of `OnWindChanged`. It journals the first call, and at frame 20 it checks that it heard one change carrying 40. Attach it to the `Gust` entity in `Feature.stscene`, in the `Script` component that you add to it.

   ```diff src="book:tutorials/scripting/tutorial-host-function.patch#hunk-41"
    						"Name": "Gust"
    					},
   +					"Script": {
   +						"Scripts": [
   +							{
   +								"Class": "WindEventFeatures",
   +								"Fields": {}
   +							}
   +						]
   +					},
    					"Transform": {
    						"Rotation": [
   ```

   1. **Lines 3–10:** the `Script` component lists the class, with no :term[field overrides]{id=field-override}.

   Run the feature test.

   **You should see:** the feature test passes. Before you attached the script, it failed with the message `Script callback OnWindChanged never ran`, which names the call that its runners search for in the journal.

   **If you do not see it:** when the callback never arrives, the strength did not change in a fixed step. The script writes it in `OnUpdate`, and the wind zone system compares at its next fixed step.

:::::

The callback works end to end. Every place that knows the callbacks gained the new one at its end: the enum, the descriptor, the thunk table of the SDK and the module's function table.

## Check the whole change

Two checks remain that no single step ran. The :term[layering test]{id=layer-table} confirms that the Scripting layer includes only what its row allows, and the full run confirms that nothing else broke.

:::::steps

1. Run the layering test and read the version of the ABI.

   ```sh
   build/<preset>/bin/Debug/StrataTests --test-suite=Architecture.Layering
   ```

   **You should see:** no failed test case. No file of `Strata/src/Strata/Scripting/` includes a Physics header: the host function reaches the zones through `Scene/SceneServices.h`. The :term[macro]{id=macro} `ST_SCRIPT_ABI_VERSION` in `ScriptABI.h` is still 1, because you only appended.

   **If you do not see it:** the test names the file and the header it includes. Replace the include with the service.

2. Run every test that needs no :term[graphics card]{id=gpu}.

   ```sh
   ctest --preset <preset>-debug -j 8 -LE gpu
   ```

   **You should see:** all tests passed, among them the wind zone tests, the new script tests, the feature test and the layering test.

   **If you do not see it:** read the first failed test and the check it names. A test outside this page that counts the engine's callbacks or host functions needs its expectation updated.

   **Why:** the order of the steps matters less than the habit: each new member of the table or the descriptor is paired with a test that fails without it.

:::::

You have a patch that adds two scene services, one host function and one callback, and keeps the :term[ABI version]{id=abi-version} at 1. It passes the layering test, the wind zone tests, the new tests and the feature test. A later change can use the same service to apply forces to bodies, which [the capstone](../capstone/build.md) does.

## Summary

- You offered the wind through a scene service that the Physics module's system adds to the scene and removes from it, so that the Scripting layer reaches it without a Physics include.
- You added a host function at the end of the table and the list, and saw the `static_assert` refuse a table that disagrees with its list. You wrapped the function in the SDK with a fallback and tested it against an older engine.
- You predicted why appending keeps old modules working and inserting would not, and kept `ST_SCRIPT_ABI_VERSION` at 1.
- You added a callback to the descriptor, the enum, the SDK and the module, read only when the descriptor covers it, and dispatched it from the system that raises it.
- You used the feature test's demands as the check: a host function called, an SDK function used and a callback journaled.

## Check yourself

1. The Scripting layer may include Core, Input, Asset, Reflection and Scene. How does the host function still reach the wind zones, and what does it return in a scene without the Physics module?

   :::answer{tests="scene-service"}
   The host function asks the scene for the service `IWindZones`, defined in the Scene layer and offered by the Physics module's system while it exists. Without that module, the lookup returns null, the function reports the absent module with `ReportProblem` and returns the failure value 0. The layering test stays green because no script file includes a Physics header.
   :::

2. You insert `GetWindStrength` between `GetStepAlpha` and `GetDrawnTransform` in the struct, and in the list. The build passes. Why is it still wrong?

   :::answer{tests="append-only host-function"}
   The build passes because the list and the struct agree. An old module, built before, calls `GetDrawnTransform` by the offset it knew, and the offset now holds the new function: it calls the wrong code with the wrong arguments. Appending moves no old member, which is why it keeps the ABI version, and anything else needs a new version.
   :::

3. A module built against this SDK runs on an engine from before this change. What does `GetStrength` of `Wind` return, and which test of this page checks it?

   :::answer{tests="append-only host-function"}
   The call returns 0. The table of the older engine is shorter, so `ST_SCRIPT_DETAIL_HOST_WITH` sees that its `StructSize` does not cover the member and gives the null table; the SDK function returns its fallback. The test module of the application programming interface (API) checks this with a copy of the table cut before the member, and with a copy holding a null entry.
   :::

4. A module built against an SDK without `OnWindChanged` runs on this engine. Why does the engine not read garbage?

   :::answer{tests="callback"}
   The engine reads the callback only when `ST_SCRIPT_HAS_MEMBER` says that the descriptor's `StructSize` covers it. A descriptor from the older SDK is smaller, so the engine keeps the member null and calls nothing. The case `OlderWindClass` tests it with a module that says "First" was built before the member existed.
   :::

5. You finish the callback but write no feature script for it. Which check fails, and what must the new script do?

   :::answer{tests="feature-demand"}
   The feature test fails with the message that the script callback `OnWindChanged` never ran. A feature script must implement it, run in the feature scene, and journal its call, so that the journal holds an entry of the callback. The same test also fails for a host function that no script called and for an SDK function that no script used.
   :::

## Exercises

1. **Basic.** Swap the lines `X(GetWindStrength)` and `X(ResetInterpolation)` at the end of the list. Predict the build's result, then check it. Put them back.

   Hint: the check compares the offsets of the members, in order.

   :::answer{tests="append-only"}
   The build stops at the same `static_assert`. The check walks the list and expects the offset of each entry to follow the previous one's end; after the swap the offset of `GetWindStrength` is not the one that comes next. The list is not a set but a copy of the struct's order, which is what lets the engine build the table and the counters from it.
   :::

2. **Medium.** Write a test that proves that a zone that was made inactive, and a zone that lost its component, add nothing to the wind. Make sure that it fails when the system gathers inactive zones.

   Hint: build on the test of the first section; read `GetStrengthAt` after each change and a fixed step.

   :::answer{tests="scene-service" solution="tutorials/scripting/tutorial-host-function/exercise-2.patch"}
   The solution adds a test case with two zones of 12 N and 30 N at the origin. Before any change the wind there is 42 N. After `SetActive(false)` on the first zone and a step it is 30 N, and after removing the component of the second and another step it is 0 N. To see it fail, remove the lines of `OnFixedUpdate` of the wind zone system that skip inactive zones: the second reading becomes 42.
   :::

3. **Hard.** Add a second host function of your own, `GetLanguage` of the class `Game`, that returns the player's language as text, in the same five places. Decide what it returns without a game service, and which test shows it.

   Hint: copy the places of `GetWindStrength`; a function that returns text takes a buffer and its capacity, as the graphics functions of the table do.

   :::answer{tests="host-function feature-demand"}
   Append the member after `GetWindStrength` with a comment that says what it returns, with a buffer and a capacity like `GraphicsGetOption`. Write `HostGetLanguage` with `HostCall`, `ResolveContext` and a failure value of an empty text, list it last in the macro, wrap it in `Game` with `ST_SCRIPT_DETAIL_HOST_WITH` and a fallback of an empty text. Test it in the API module with the older engine copy, in a `Scripting.*` test, and call it from a feature script, or the feature test fails with the message that it was never called.
   :::

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the table of host functions and the class descriptor, with the compatibility rules in its first comment.
- `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`: the host functions, `HostCall`, `ResolveContext` and the list `ST_SCRIPT_HOST_FUNCTIONS` with its `static_assert`.
- `Strata/src/Strata/Scripting/ScriptModule.cpp`: the copy of the class descriptor under the crash guard, and the calls of the callbacks.
- `Strata/src/Strata/Scripting/ScriptSystem.cpp`: the listeners of the scene's event sources and the dispatch to scripts.
- `Strata/src/Strata/Scene/SceneServices.h`: the service interfaces and the rule for how systems offer them and find them.
- `StrataScriptCore/Include/StrataScript/Script.h` and `Time.h`: the SDK's :term[base class]{id=base-class}, thunks and the SDK function that serves as the model.
- `StrataTests/Architecture/Layers.json`: the layer table that makes the service necessary.
- `StrataTests/FeatureTest/Scripts/` and `StrataTests/src/FeatureTest/`: the feature scripts and the checks that read the call counters and the SDK headers.

## Further reading

- The doctest documentation on its command line (github.com/doctest/doctest): the filters that this page uses to run one suite: beginner.
- Scott Meyers, "Effective Modern C++", on item 'virtual functions that override': why `override` catches a signature that drifted: intermediate.
- Ulrich Drepper, "How To Write Shared Libraries": how a stable binary interface survives the growth of a library: advanced.
