---
id: capstone/plan
title: "Capstone I: designing a feature the way Strata does"
description: "Design the finished wind zone before writing its code: place its parts in layers, find its registries, apply the rules and write its spec."
kind: tutorial
size: L
tracks: [E]
needs: [world/tutorial-component, scripting/tutorial-host-function, editor/tutorial-command, engineering/contributing, core/reading-code]
time: 150
learn:
  - id: place-parts
    text: name the layer that may hold each part of a new feature, and prove a wrong place with the layering test
  - id: find-registries
    text: find the registries a feature joins, when each opens and freezes, and the check that fails when the feature forgets one
  - id: match-rules
    text: name the rule that bites each decision of a feature and what enforces it
  - id: weigh-decisions
    text: choose between designs and write down what each choice costs
  - id: write-spec
    text: write a spec in the order of the engine's own specs and check it against the code
status: final
---

## What you will make

You will write the design of the finished wind zone before any of its code, and add it to the engine's tree. Along the way you place each part of the feature in the layer that may hold it, list the registries it joins and match every decision to a rule.

A **spec** is a written design that names the goal, the starting point, the decisions, the steps, the tests and the acceptance numbers of a change before the change begins. Strata writes one for every large piece of work, and its own specs sit in `Docs/Plans/Wave8/specs/`. Yours becomes the next file in that folder.

```mermaid caption="Where each part of the finished wind zone lives, from the component in Physics to the arrow shape in Reflection and the host function in Scripting." alt="Boxes for the layers Reflection, Scene, Renderer, Physics and Scripting, with the editor's commands and the script SDK beside them. Physics holds the component, the system and the force function, and implements a service whose interface sits in Scene. Reflection holds the arrow shape that Physics asks for and the Renderer draws. Scripting holds the host function that reads the wind through the Scene service; the SDK calls it, and the commands call the force function directly."
flowchart TB
    subgraph L1["Reflection"]
        ARROW["Arrow shape kind"]
    end
    subgraph L2["Scene"]
        SVC["Wind service interface"]
    end
    subgraph L3["Renderer"]
        DRAW["Gizmo drawing"]
    end
    subgraph L4["Physics (optional)"]
        COMP["Component and system"]
        FORCE["Force function"]
    end
    subgraph L5["Scripting"]
        HOST["Host function"]
    end
    SDK["Script SDK"]
    CMD["Editor commands"]
    COMP --> FORCE
    COMP -. implements .-> SVC
    COMP -. asks for .-> ARROW
    DRAW -. draws .-> ARROW
    HOST -. reads .-> SVC
    SDK --> HOST
    CMD --> FORCE
```

## What you need

- The end state of [the command tutorial](../editor/tutorial-command.md): the source build of [your first engine change](../core/first-change.md) with the wind zone chain applied, configured and built in `Debug`. Every command below writes `<preset>` for your system's :term[CMake preset]{id=cmake-preset}: `windows`, `linux` or `macos`.
- The method of [reading a large codebase](../core/reading-code.md): searches, jumps and writing a path down as files and lines.
- A project made from the Basic 3D template, opened in the editor of that build, for the trace in the exercises.
- Time: about two and a half hours. You write one document and build nothing new, apart from one run of a test.
- No file to import. The patch of this page adds one file to the engine.

:::files[The file of the change]

- `Docs/Plans/Wave8/specs/`
  - `wind-zone.md`: new, the spec of the finished wind zone

:::

## Say who meets the feature

Every feature of Strata has more than one audience, and each audience reaches it through another door. A design that names only the first door ships a feature that the others cannot use. This section lists the doors and turns them into a goal and an acceptance test.

:::::steps

1. Write the game maker's story. A game maker adds the component with **Add Component** and edits Strength, Radius and Mode in the Inspector. The person sees a :term[gizmo]{id=gizmo-start} of the zone in the Scene view and presses Play or Simulate to watch bodies move.

   **You should see:** four short sentences, one per thing the person does, each of which a person could check by clicking.

   **If you do not see it:** a sentence that names code ("the system gathers zones") belongs in a later section. Rewrite it as what the person sees.

2. Write the three other stories. A script asks for the wind at a point. An agent asks for the same without playing, through a command. The test suite checks the feature with unit tests, the :term[feature test]{id=feature-test} and one perf metric.

   **You should see:** four doors in all: the game maker, the script, the agent and the test suite. Each has its own place in Strata: the Inspector, the script application programming interface (API), the :term[command registry]{id=command-registry} and the tests.

   **If you do not see it:** an agent has no mouse and a script has no editor. If a story needs either, it names the wrong door.

3. Decide what the feature does, in numbers. A Directional zone has no radius and pushes every :term[dynamic body]{id=dynamic-body} along the zone entity's local -Z, which is Strata's forward, as a directional light shines along its entity's -Z. A Spherical zone pushes the bodies inside its Radius away from its centre. Strength is in newtons.

   **You should see:** an example you can predict. A 2 kg box under a Directional zone of 10 N accelerates at 10 / 2 = 5 m/s². One :term[fixed step]{id=fixed-step} lasts 1/60 s, so the box gains 5 / 60, about 0.083 m/s, each step, before damping and friction.

   **If you do not see it:** a unit is missing. Every number of a spec carries its unit: newtons, metres, seconds, milliseconds.

:::::

:::example[Two numbers a test can check]
Turn the entity of a Directional zone by 90 degrees about the Y axis, counterclockwise seen from above. Its local -Z now points along -X, so a Strength of 10 N pushes with the vector (-10, 0, 0) N. Take a Spherical zone at the origin with Radius 5 m and Strength 20 N. A body at (3, 0, 4) is 5 m away, so it is inside, and the push is 20 N along (0.6, 0, 0.8), which is (12, 0, 16) N.

Both results come from school arithmetic, and that is the point. An acceptance number you can compute by hand is one a test can compare against, and a wrong implementation cannot pass it by luck.
:::

## Place each part in its layer

Strata builds one :term[static library]{id=static-library} for each layer of `StrataTests/Architecture/Layers.json`, and a file may include only files of its own layer and of the layers its row allows. The rule protects the engine from tangles, and it decides where each part of the wind zone may live. You read the rows first, place the parts, and then break the rule on purpose to see the test that guards it.

:::::steps

1. Read the rows of Physics and Audio.

   ```json src="StrataTests/Architecture/Layers.json#L50-L60"
   	"Name": "Physics",
   	"Option": "STRATA_WITH_PHYSICS",
   	"Paths": [ "Strata/Physics/**" ],
   	"MayInclude": [ "Core", "Asset", "Reflection", "Scene" ]
   },
   {
   	"Name": "Audio",
   	"Option": "STRATA_WITH_AUDIO",
   	"Notes": "App is a proven downward dependency: the Audio module implements its EngineModule (Core/EngineModule.h), the interface App defines for the services a program runs; App includes no Audio header.",
   	"Paths": [ "Strata/Audio/**" ],
   	"MayInclude": [ "Core", "App", "Asset", "Reflection", "Scene" ]
   ```

   1. **Line 50:** the layer's name; its files live under `Strata/src/Strata/Physics/`.
   2. **Line 51:** the :term[CMake]{id=cmake} option that builds the layer, so a build can omit it.
   3. **Line 53:** Physics may include Core, Asset, Reflection and Scene, and nothing else.
   4. **Line 58:** Audio's note explains its one extra row, App, which is a proven downward dependency.

   **You should see:** that Physics does not list Scripting, :term[Renderer]{id=renderer} or Audio, and that none of them lists Physics except the :term[Runtime]{id=runtime} and Engine layers. Scripting lists Core, Input, Asset, Reflection and Scene.

   **If you do not see it:** the file differs when your clone is not at the book's commit. Return it there, as the first change does.

2. Place the parts. Each row of this table follows from the rows you read.

   | Part | Layer | Why |
   | --- | --- | --- |
   | The component, the system and the force function | Physics | They need bodies; Physics may include Scene |
   | The service interface the system offers | Scene | Scripting and Audio may include Scene but not Physics |
   | The arrow shape kind | Reflection | The Renderer may include Reflection, and Physics asks for the shape there |
   | Drawing the arrow | Renderer | It draws every shape without naming a component |
   | The :term[host function]{id=host-function} | Scripting | It reads the wind through the :term[Scene service]{id=scene-service} |
   | The script software development kit (:term[SDK]{id=sdk}) | `StrataScriptCore` | Game scripts never link the engine |
   | The commands | The editor's core | Editor code lies outside the table, and games link no tooling |

   **You should see:** that no part of a lower layer names a higher one. The Renderer never names the wind zone: Physics hands it a `ComponentGizmoShape` through `ComponentInfoBuilder::Gizmo`.

   **If you do not see it:** a part you placed in Physics but wanted to call from Scripting needs a service interface in Scene. Invert the dependency; never widen a row.

3. Break the rule on purpose. Open `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` and add the line `#include "Strata/Physics/PhysicsComponents.h"` after its other engine includes. Build the tests, then run the layering suite.

   ```sh
   build/<preset>/bin/Debug/StrataTests --test-suite=Architecture.Layering
   ```

   **You should see:** the suite fails, and its message names your file, the :term[header]{id=header} and both layers. The key line reads `includes Strata/Physics/PhysicsComponents.h, but layer Scripting may not include layer Physics`, after the file's name and your line number.

   **If you do not see it:** on Windows the program is `StrataTests.exe`. A suite that passes means the build is stale, or the include went into a file that is not under `Strata/src/Strata/Scripting/`.

4. Take the include back, then run the suite again.

   ```sh
   git checkout -- Strata/src/Strata/Scripting/ScriptHostAPI.cpp
   build/<preset>/bin/Debug/StrataTests --test-suite=Architecture.Layering
   ```

   **You should see:** `git status` without your file, and a passing suite.

   **If you do not see it:** the file was part of an earlier change of yours, so `git checkout` removes more than the include. Remove only the added line by hand.

5. Place the optional module. Physics is built only when `STRATA_WITH_PHYSICS` is on, and :term[continuous integration]{id=ci} (CI) also builds the engine without it. Nothing that a build without Physics compiles may name the wind zone: not the other layers, not the runtime, not the tests outside the Physics tests. Four places may guard code with `#if ST_WITH_PHYSICS`: the :term[composition root]{id=composition-root}, the asset pipeline, the game runner and the test code.

   **You should see:** one exception: the editor may name the wind zone. CMake refuses to configure the editor without every module, so its `wind.` commands are always built with Physics.

   **If you do not see it:** the CI job without Physics also sets `-DSTRATA_BUILD_EDITOR=OFF`. That job proves that the Scene service, the host function and the guarded tests compile without the module; the other jobs build the commands.

:::::

## Find the registries it joins

A feature reaches the engine through lists: the composition root calls each module's registration, and each registry holds one kind of thing. You find them with the searches of [reading a large codebase](../core/reading-code.md), starting from the root and following the names.

:::::steps

1. Search for the module's registration.

   ```sh
   git grep -n "RegisterPhysicsModule" -- Strata/src
   ```

   **You should see:** three files: `Strata/src/Strata/Engine/BuiltinModules.cpp`, which calls the function from a table inside `#if ST_WITH_PHYSICS`, and the header and source of `PhysicsRegistration`.

   **If you do not see it:** run the command from the root of the clone, not from a folder below it.

2. Read what the registration does for the wind zone's system. The chain added a second descriptor beside this one.

   ```cpp src="Strata/src/Strata/Physics/PhysicsRegistration.cpp#L20-L26" from="SceneSystemDescriptor descriptor = MakeSceneSystemDescriptor<PhysicsSystem>" to="ST_CORE_VERIFY(registered," symbol="RegisterPhysicsModule"
   SceneSystemDescriptor descriptor = MakeSceneSystemDescriptor<PhysicsSystem>("Physics", true, [](Scene& scene) { return CreateScope<PhysicsSystem>(scene); });
   descriptor.AfterIfPresent = { "Scripting" };
   descriptor.ProfileStage = "Scene.Physics";
   // A loaded scene's bodies are built while its load prepares it, so that the frame it starts in builds none.
   descriptor.PrepareLoadedScene = &PhysicsSystem::PrepareLoadedScene;
   const bool registered = SceneSystemRegistry::Register(std::move(descriptor));
   ST_CORE_VERIFY(registered, "The physics module could not register its scene system");
   ```

   **You should see:** the order in `AfterIfPresent`, a :term[soft constraint]{id=soft-constraint} toward the Scripting system; the profile stage that times the system; and the `true` of `MakeSceneSystemDescriptor`, which lets the system run in :term[Simulate mode]{id=simulate-mode}. The wind zone's system registers before Physics with `BeforeIfPresent`, so its forces are queued before the step that applies them.

   **If you do not see it:** a hard constraint (`After`) toward another module would stop the engine from registering without that module. Toward Physics, Audio or Scripting use the soft forms.

3. Read the services the physics system offers, because the wind zone uses two of them, `IBodyControl` to push and `IPhysicsQueries` for `OverlapSphere`, and adds an eighth.

   ```cpp src="Strata/src/Strata/Physics/PhysicsSystem.cpp#L61-L67"
   m_Scene.RegisterService<ICollisionEventSource>(*this);
   m_Scene.RegisterService<IBodyMotionQuery>(*this);
   m_Scene.RegisterService<IBodyControl>(*this);
   m_Scene.RegisterService<IPhysicsQueries>(*this);
   m_Scene.RegisterService<ICharacterControl>(*this);
   m_Scene.RegisterService<IPhysicsCapacity>(*this);
   m_Scene.RegisterService<IPhysicsDiagnostics>(*this);
   ```

   **You should see:** seven `RegisterService` lines: `ICollisionEventSource`, `IBodyMotionQuery`, `IBodyControl`, `IPhysicsQueries`, `ICharacterControl`, `IPhysicsCapacity` and `IPhysicsDiagnostics`. The comment in `Strata/src/Strata/Scene/SceneServices.h` names only six; [the page on systems](../world/systems.md) records the difference.

   **If you do not see it:** the wind zone's own service, `IWindZones`, is registered by its own system, not by this :term[constructor]{id=constructor}.

4. Match each registry to what it holds, when it is open and what fails when the feature forgets it.

   | Registry | Layer | Open until | Fails when forgotten |
   | --- | --- | --- | --- |
   | Component registry | Reflection | `RegisterBuiltinModules` freezes it after the last module | The component schema snapshot and the feature test |
   | :term[Scene system]{id=scene-system} registry | Scene | While no scene runs; a registration while one runs is refused | The tests of the descriptors' order |
   | Scene services | Scene | Only while a scene runs: constructor to :term[destructor]{id=destructor} of the system | The null the host function returns, and the unit test of the service |
   | Host function table | Scripting | :term[Compile time]{id=compile-time}: a list and a :term[struct]{id=struct} that disagree do not compile | The feature test's call counters |
   | Editor command groups | Editor | The constructor of the command registry | The command tests and the lists of kinds |
   | Model Context Protocol (MCP) toolset table | Command-line client | Compile time | The toolset test of the client |
   | Feature test | Tests | Always | It fails on anything registered that no test uses |
   | Perf budget file | Tests | Always | The perf test: a metric with no entry fails it before anything is measured |

   **You should see:** that every row has a check you can name. A feature that forgets a registry fails a check before it reaches a person.

   **If you do not see it:** if you cannot name the check, search for the registry's name in `StrataTests/src/` and read the test as a description.

:::::

## Match the rules to the decisions

Strata keeps its rules in `AGENTS.md`, and each rule has a reason and, usually, a check. The table lists the rules that bite the wind zone: where, and what enforces them. Each rule links the page that teaches it.

| Rule | Where it bites the wind zone | Enforced by |
| --- | --- | --- |
| [Includes follow the layer table](../core/layers-registries.md) | The Renderer cannot name the component | The layering suite |
| [Never widen a row to pass an include](../core/layers-registries.md) | Scripting needs the wind: invert the dependency with a service | Review, and the table's own notes |
| [Registration only through the composition root](../core/layers-registries.md) | The new registrations stay in `RegisterPhysicsModule` | The layering suite, for registration headers |
| [`#if ST_WITH_PHYSICS` only in four places](../core/layers-registries.md) | Nothing outside Physics guards for the zone | CI's build without the module |
| [Modules meet through services](../world/systems.md) | Scripts read the wind through `IWindZones` | The layering suite |
| [Systems order themselves with soft constraints](../world/systems.md) | The zone's system runs before Physics, after Scripting | The tests of the descriptors |
| [Signal every transform write](../world/scene-graph.md) | The zone writes no transform | The scene validation of the feature test |
| [Never rename a property; ranges forbid bad states](../world/reflection.md) | Strength is 0 to 1000 N | The component schema snapshot |
| [A property another disables gets an inactive reason](../editor-ui/inspectors.md) | Radius in Directional mode | Review; the feature test reads the reason |
| [Forces are applied every fixed step](../physics/world-step.md) | The system pushes in `OnFixedUpdate` | A test that runs two steps |
| [A unit of frame work is a profile stage](../core/profiling.md) | The system gets a stage of its own | A test of the stage names |
| [Append host functions; wrap them in `HostCall`](../scripting/host-api.md) | The vector form of the wind function goes at the end of the table | The compile-time list, and the feature test |
| [Commands are the API; refuse bad input; declare a kind](../editor/commands.md) | `wind.sample` is a Query, with a schema | The lists of kinds in the command tests |
| [Perf limits live in one file and only go down](../engineering/perf-lab.md) | The zone's metric starts `Provisional` | Review, and the perf run |

:::::steps

1. Pick three rows and search for the check. For the toolset table, for example, run `git grep -n "wind." -- StrataCLI/src/CLI/McpToolsets.cpp` and read the chain's change.

   **You should see:** one line in the prefix table, which is why a command group needs no remote call code of its own.

   **If you do not see it:** the chain's patch has to be applied. Without it the search finds nothing.

2. Write the three rows into the working copy of your spec, under "Rules of the machine". A rule that you cannot connect to a decision of the zone does not belong there.

   **You should see:** one line per rule: the rule, where it bites and what enforces it.

   **If you do not see it:** a rule such as the style of braces binds every file and says nothing about the wind. Leave it to the style guide.

:::::

## Decide, and write down what each choice costs

A decision is a choice between designs, and a decision without its cost is a wish. The cost names the audience that pays. Strata's specs say so in plain sentences, and so does yours.

:::::steps

1. Decide that one function gives the wind at a point. The system, the script API and the command all call it. The command runs while you edit, when no scene service exists, so it calls the Physics module's function and gathers the zones from the :term[edited scene]{id=edited-scene}.

   **You should see:** the cost beside the decision: the editor now names the Physics module. That is allowed, because the editor is built only with every module.

   **If you do not see it:** two copies of the rule are a design with a bug waiting: one of them will change alone.

2. Decide which bodies a zone visits. A Spherical zone asks `OverlapSphere` for the bodies inside its sphere. A Directional zone has no radius and visits every dynamic body. A force wakes its body, as the engine's queue shows.

   ```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L5159-L5166"
   if (!record.HasPendingForce)
   {
   	record.HasPendingForce = true;
   	data.ForcedBodies.push_back(entity.GetHandle());
   }
   record.PendingForce += force;
   record.PendingTorque += torque;
   WakeRecord(data, record);
   ```

   **You should see:** why the cost matters: a zone keeps awake what it pushes, and a sleeping body costs nothing. A box resting under 5 N that cannot move it never sleeps. A zone of Strength 0 is skipped before any query.

   **If you do not see it:** `AddPendingForce` is reached through `IBodyControl::AddForce`; the function itself sits in an anonymous :term[namespace]{id=namespace}, so the system cannot call it directly.

3. Decide how scale and layers work. The radius never follows the entity's scale, though the :term[collider]{id=collider} gizmos do, so a zone scaled by (2, 1, 1) with Radius 5 m still reaches 5 m. The query passes every :term[collision layer]{id=collision-layer}.

   **You should see:** one rule for the gizmo, the force, the query and the command. The scale rule makes a scaled zone and its sphere gizmo agree, at a cost: scaling a zone never widens it. The layer rule has a cost: a game cannot exclude a layer until a mask property is appended.

   **If you do not see it:** if the gizmo uses the radius alone and the force uses the scale, a scaled zone draws a sphere that is not where it pushes. Write the rule once and use it four times.

4. Decide the arrow, the inactive reason and the order. The shapes of a gizmo have four kinds and one group.

   ```cpp src="Strata/src/Strata/Reflection/ComponentGizmo.h#L25-L31"
   enum class Kind : uint8_t
   {
   	Box,       // A box of HalfExtents around Transform's origin, along its axes
   	Sphere,    // A sphere of Radius around Transform's origin
   	Capsule,   // A capsule of Radius along Transform's Y axis, its cylinder 2 * HalfHeight long
   	MeshBounds // The bounds of Mesh (when it is loaded: gizmos never load assets), placed by Transform
   };
   ```

   **You should see:** that a Directional zone's arrow fits none of them, so Reflection gains a fifth kind, `Arrow`, which the Renderer draws. Radius gets an inactive reason in Directional mode. Zones come in the order of the registry and bodies in the fixed order of the query or the registry, so two runs give the same poses.

   **If you do not see it:** the cost of the arrow is one more kind for every consumer of the shapes. The cost of the fixed order is that no later change may visit zones or bodies in an order that depends on threads.

:::::

## Write the spec and check it against the code

The engine's own specs share their sections, in about this order. You fill the same sections for the wind zone. The steps of the feature itself belong to the next two pages: [building the feature](build.md) and [landing it](land.md).

:::why[Why a spec comes before the code]
A mistake found in a document costs a sentence. The same mistake found in a merged change costs a revert, a new review and a new run of the tests. Strata writes the design first, so that the objections of a reviewer arrive while they are cheap and each step of the work has a goal to be checked against. The cost is the time to write it: a spec of this size takes about as long as one of the steps it plans.
:::

:::::steps

1. Create the spec in the folder `Docs/Plans/Wave8/specs/`, in a file named `wind-zone.md`, and write the goal in priority order. Put what a game maker sees first and what is cheap or the same on every run last.

   ```diff src="book:tutorials/capstone/plan.patch#L22-L35"
   +   along the zone entity's local -Z (Strata's forward, as a directional light shines), so turning the entity turns the wind. A
   +   Spherical zone pushes the dynamic bodies inside its Radius with Strength newtons, away from its centre. Play and Simulate
   +   behave alike.
   +3. **Scripts read the wind.** `Wind::GetStrength` (existing) and a new `Wind::GetForceAt(point)` that returns the vector.
   +4. **Agents read the wind without playing.** The command `wind.sample` answers for a point of the edited scene.
   +5. **Cheap.** A scene without zones pays one empty loop. A sleeping body is woken only by a zone that pushes it; a zone of
   +   Strength 0 pushes nothing and wakes nothing.
   +6. **Repeatable.** The same scene, the same steps, the same poses, bit for bit.
   +
   +Not the goal: drag that depends on a body's shape, gusts that change with time, turbulence, and wind that moves cloth, particles
   +or sound. Each of them can add a property or a service later without changing a name here.
   +
   +## 2. Where we start
   +
   ```

   1. **Line 22:** the goal's heading, numbered like the engine's specs.
   2. **Lines 24–26:** the game maker's story, in the form of something to check.
   3. **Lines 27–30:** what the zone does to a body, with the direction and the units.
   4. **Lines 31–34:** the script and the agent, each a door of the first section.

   **You should see:** goals in the order of who suffers if they fail. A feature that is smooth and wrong is worse than one that is plain and right.

   **If you do not see it:** list a "not the goal" line too: what you refuse to build, so that a reviewer cannot ask for it later.

2. Write the decisions that hold for every step, each with its cost.

   ```diff src="book:tutorials/capstone/plan.patch#L51-L64"
   +2. **Which bodies a zone visits.** A Spherical zone asks `OverlapSphere` for the bodies inside its sphere; a Directional zone
   +   visits every dynamic body. Cost: a Directional zone pays for every dynamic body of the scene, awake or not.
   +3. **A force wakes its body.** A zone keeps what it pushes awake. Cost: a body resting in a zone of 5 N that cannot move it
   +   never sleeps, and a sleeping body costs nothing. A zone of Strength 0 is skipped before any query.
   +4. **Radius is never scaled.** The radius is the number typed, whatever the entity's world scale; the collider gizmos differ.
   +   Cost: scaling a zone never widens it. The gizmo, the force, the overlap query and `wind.sample` use this one rule.
   +5. **A zone pushes every collision layer.** The query passes `c_AllPhysicsLayers`. Cost: a game cannot exclude a layer; a
   +   mask property can be appended later without renaming anything.
   +6. **Order is fixed.** Zones come in the order of the registry, and a zone's bodies in the order of the query or the registry,
   +   which is the same in every run of a scene. Cost: no later change may visit them in an order that depends on threads.
   +7. **The arrow is a new shape kind.** `ComponentGizmoShape::Kind::Arrow` joins the four in Reflection; the Renderer draws it with
   +   the debug lines. Cost: one more kind every consumer of the shapes handles.
   +8. **Radius gets an inactive reason** in Directional mode: the value changes nothing there.
   +9. **The zone writes no transform.** It only queues forces; physics moves the bodies and writes their poses.
   ```

   1. **Line 51:** one function for the wind at a point, shared by three callers.
   2. **Line 57:** which bodies a zone visits.
   3. **Line 59:** the waking of bodies, with its cost.
   4. **Line 61:** the scale rule, written once for four users.

   **You should see:** costs that name who pays: the editor, a sleeping scene, a game that wants to exclude a layer.

   **If you do not see it:** a decision that lists only benefits is not finished. Ask what a reviewer would object to, and write the answer.

3. Fill the other sections: the steps in the order they are built, the defaults and ranges, the tests with the checks that must fail, the acceptance numbers, the perf metric, the documents and the risks. List every place that documents the change. These are the Developer Guide's physics section, its gameplay chapter with the host function order, the Scripting page of the manual, the overview of the scripting skill and one line of the wave's release notes.

   **You should see:** a table of tests where each row ends in "must fail when": the test proves nothing until it is seen failing without the code it checks.

   **If you do not see it:** a test without a must-fail check can pass for the wrong reason. Name the change that makes it fail.

4. Add the first hour: what to read, and the baseline run of the wind zone's tests, the feature test and the layering suite before any change.

   **You should see:** a short list of commands and files, so that an implementer starts from a known green state.

   **If you do not see it:** a baseline that already fails belongs to someone else. Write down which tests, and their failures, before you start.

5. Review the spec against the code, as Strata's own specs do. Open every file, function and line the spec names, at the clone you work on, and write each difference under "Review corrections", ending the document.

   **You should see:** three corrections in the example spec. The force queue sits in an anonymous namespace, so the system uses `IBodyControl::AddForce`. The comment in `Strata/src/Strata/Scene/SceneServices.h` names six services, not seven. The editor is built only with every module, so the build without Physics does not prove that the commands compile.

   **If you do not see it:** a spec with no corrections was not checked. Pick the five claims that matter most and read their code again.

6. Commit the spec by itself.

   ```sh
   git add Docs/Plans/Wave8/specs/wind-zone.md
   git commit -m "Add the spec of the finished wind zone"
   ```

   **You should see:** one commit that touches one file of the documentation, which is what [the contribution checklist](../engineering/contributing.md) asks of a documentation commit.

   **If you do not see it:** a code file in the commit means an earlier change is still staged. Remove it from the commit with `git restore --staged <file>`.

:::::

## Summary

- You placed each part of the wind zone in the layer that may hold it and proved a wrong place with the layering suite.
- You found the registries the feature joins, when each opens and freezes, and the check that fails when one is forgotten.
- You matched the rules to the decisions of the zone and to what enforces them.
- You chose between designs and wrote down what each choice costs.
- You wrote the spec in the order of the engine's own specs and checked it against the code.

## Check yourself

1. Why does the interface of the wind service live in the Scene layer and not in Physics?

   :::answer{tests="place-parts"}
   Scripting and Audio may include Scene but not Physics, and the Renderer may not name the wind zone either. A service interface in Scene lets them read the wind without any include of Physics. When no Physics system runs, the service is missing and the lookup returns null, so the build without Physics still compiles.
   :::

2. Name three registries a new component joins and the check that fails when each is forgotten.

   :::answer{tests="find-registries"}
   The component registry fails the component schema snapshot and the feature test. The scene system registry fails the tests of the descriptors' order. The host function table does not compile when the list and the struct disagree. A command group missing from the toolset table fails the toolset test of the command-line client.
   :::

3. The command `wind.sample` could call the service instead of a function of the Physics module. Why does it not?

   :::answer{tests="weigh-decisions"}
   Services exist only while a scene runs, from the first start of any system to the last stop. The command answers while you edit, so no wind service exists then and the lookup would return null. The cost of the chosen design is that the editor names the Physics module, which is allowed because the editor is built only with every module.
   :::

4. Which rule does a new script function for the wind vector follow when it joins the host function table, and what enforces it?

   :::answer{tests="match-rules"}
   Host functions are appended at the end of the table and of its :term[X-macro]{id=x-macro} list, never inserted, wrapped in `HostCall` and checked by the SDK before use. The compile-time list check refuses a table and a list that disagree. The feature test refuses a host function that no feature script calls.
   :::

5. Which sections does a spec need besides the goal, the decisions and the steps?

   :::answer{tests="write-spec"}
   Where we start, settings and defaults, tests with must-fail checks, acceptance numbers, perf metrics, documents, risks, the order of delivery and the first hour. Every wave 8 spec also ends with an independent review against the code, whose corrections win over the body. The wind zone's spec has all of them.
   :::

## Exercises

1. **Medium.** Trace one click in the Scene view to a pixel, with the method of [reading a large codebase](../core/reading-code.md). Write each file and function on the path as a line of a table. Start from the click in `StrataEditor/src/Panels/ViewportPanel.cpp` and end at the outline's colour.

   :::answer{tests="find-registries match-rules"}
   The path has seven stops. Search for `RequestPick` to find the cause, or for `SelectionColor` to find the effect, and meet in the middle.

   1. `StrataEditor/src/Panels/ViewportPanel.cpp`: a left click in the hovered view, without Alt, calls `EditorViewport::RequestPick` with the pixel, the image size and the mode (replace, toggle or add by the keys).
   2. `StrataEditor/src/Editor/EditorViewport.cpp`, `RequestPick`: asks `SceneRenderer::ReadEntityIDAsync` for one pixel of the entity-ID buffer and keeps the readback in a pending pick.
   3. The same file, `UpdatePicking`, which `EditorContext` calls each frame: it waits until the readback is ready, with a timeout, and never blocks.
   4. `SceneRenderer::GetEntityFromID` turns the pixel's number into an entity of the scene that was clicked.
   5. `ApplyPick` calls `Select`, `Deselect` or `ClearSelection` of the context, by the mode.
   6. `StrataEditor/src/Editor/ViewportRenderer.cpp`: when the outline is on, `UpdateSelectionSubtrees` fills the list of entities, which becomes `SelectedEntities` of the render options.
   7. `Strata/shaders/Overlay/Outline.frag.slang`: a pixel outside a selected entity's silhouette, within the outline width of it, takes the selection colour.
   :::

2. **Hard.** The wind should make a sound. Audio may not include Physics. Decide where the sound is played, and write the decision and its cost into the risks of your spec.

   :::answer{tests="place-parts weigh-decisions" solution="tutorials/capstone/plan/exercise-2.patch"}
   The sound is played by the Audio module's system, which reads the wind through the service `IWindZones`. The interface lives in the Scene layer, which Audio may include, and the lookup returns null when no Physics system runs, so the sound is silent there. The cost: the sound follows the interface of the service, and Simulate mode has no audio, so nothing plays while simulating. The patch adds this bullet to the risks.
   :::

## Where it lives in Strata

- `StrataTests/Architecture/Layers.json`: the layers and what each may include; `StrataTests/src/Architecture/LayeringTests.cpp` enforces it.
- `Strata/src/Strata/Engine/BuiltinModules.cpp` and `Strata/src/Strata/Physics/PhysicsRegistration.cpp`: the composition root and the module's registration.
- `Strata/src/Strata/Scene/SceneServices.h`: the services, and the rule that they exist only while a scene runs.
- `Strata/src/Strata/Reflection/ComponentGizmo.h`: the gizmo shapes and their one group.
- `Docs/Plans/Wave8/specs/`: the specs of the wave, which yours joins.

## Further reading

- Strata's own specs in `Docs/Plans/Wave8/specs/` (intermediate): eleven to nineteen numbered sections each, and a review at the end.
- "Documenting Architecture Decisions" by Michael Nygard (intermediate): a short essay on writing a decision with its consequences.
