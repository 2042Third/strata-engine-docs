---
id: capstone/land
title: "Capstone III: tests, the feature test, a budget, the review and CI"
description: "Make the WindZone change ready to land: unit tests, the feature test, a perf metric, the documents, a review, a clean worktree and a green CI branch."
kind: tutorial
size: L
tracks: [E]
needs: [capstone/build, engineering/feature-test, engineering/perf-lab, engineering/ci]
time: 180
learn:
  - id: unit-tests
    text: write the unit tests of a new component, each seen failing without the line it guards
  - id: feature-test
    text: change the feature project so that its coverage checks pass for the new component
  - id: perf-metric
    text: add a perf metric with a provisional budget entry and explain the ratchet
  - id: review
    text: run the review checklist over a staged change, split it into commits and verify it in a clean worktree
  - id: ci-branch
    text: run a change through a CI branch and read a failure from its annotations
status: final
---

## What you will make

You will make the `WindZone` change of the last two capstones ready to land, and then land it. Ready means that it has passed every gate that Strata sets for a change. The gates are unit tests, a :term[feature test]{id=feature-test} that still passes, a perf metric, the documents and a review. Two more follow: a check in a clean copy of the :term[repository]{id=repository} and a green run of :term[continuous integration]{id=ci} (CI) on a branch of its own. Then you land the change as commits.

```mermaid caption="The way a change lands. Each gate catches what the earlier ones cannot see, and only a green run of the CI branch lets the change move on." alt="A chain of seven boxes from left to right: unit tests, feature test, perf metric, documents, review, clean worktree and CI branch. An arrow leads from the last box to the main branch."
flowchart LR
  A[Unit tests] --> B[Feature test] --> C[Perf metric] --> D[Documents] --> E[Review] --> F[Clean worktree] --> G[CI branch] --> H[main]
```

## Why one change passes so many gates

Your `WindZone` works. You pushed bodies with it in the editor, and its first tests pass. Why not push it?

Because each gate of Strata catches a different kind of mistake, and a change that skips one leaves that kind in the engine for the next person. A unit test checks one behaviour in a small scene. It cannot tell you that a new property never reaches a saved file, or that a new script function is never called by any game. The **feature test** is the engine's one real project: it fails when something registered goes unused, and so it finds both.

A perf metric guards a cost. The review catches what no program checks, such as a missing document. A clean copy of the repository proves that the change works without the other files in your working tree. CI builds the change with three :term[compilers]{id=compiler} and without the optional modules, which finds what the compilers on your machine accept and others reject.

Here is one example. The wind adds one :term[host function]{id=host-function}, a function the engine gives to script code, so scripts can read the wind. The feature test fails until a feature script calls it, and the failure names the function. You need the call; your first test run does not.

Each gate also has a cost, and you pay it in time: the whole sequence of this page takes about three hours the first time. Strata accepts that cost because a failure found by a person after the merge costs every person who builds the engine that day. Section by section, you will pay each cost once.

## What you need

- The end state of [the capstone that built the change](build.md): the chain's patches and the `WindZone` change applied to your clone of the engine, built in Debug and in Release. The perf step needs Release.
- A repository whose `origin` is your own fork on GitHub with GitHub Actions enabled. Clone the fork, or point `origin` at it, because `Tools/CIStatus.py` reads the runs of the repository that `origin` names. In a clone whose `origin` is the engine's own repository, it asks that repository and finds no run of yours.
- The GitHub command-line tool `gh`, signed in, or a token in the :term[environment variable]{id=environment-variable} `GH_TOKEN`, so that `CIStatus.py` can read your runs.
- No file to import and no editor project. About three hours, most of them builds.

## Write the unit tests

The tests of the `WindZone` live in one suite, in `WindZoneTests.cpp` in the Physics folder of the tests: the file already holds the system's first cases. A suite is named after its module, and the wind suite is named like this.

```pseudocode
TEST_SUITE("Physics.WindZone")
```

The name follows a rule. `StrataTests/CoreShards.json` gives the :term[shard]{id=shard} called Systems every suite that starts with `Physics`, and a shard is one :term[CTest]{id=ctest} entry that runs a group of suites. The suite `Testing.Shards` fails when a test case stands outside a suite or a suite belongs to no shard. A test written outside these rules never runs.

The tests follow two more rules. They count game time in :term[fixed steps]{id=fixed-step}, never in frames, because a step has a fixed length and a frame does not. Tests that need Physics live in files that a build without the module omits: the folder `StrataTests/src/Physics/` is on the list `STRATA_TESTS_OF_PHYSICS`. A test case in any other file takes `#if ST_WITH_PHYSICS`.

:::::steps

1. Open `WindZoneTests.cpp` and read its first cases. Add the new ones to the same suite, after them. Build the tests and run only this suite.

   ```sh
   build/linux/bin/Debug/StrataTests --test-suite=Physics.WindZone
   ```

   Use the folder of your :term[preset]{id=preset}: `build/windows/bin/Debug/StrataTests.exe` on Windows. A :term[doctest]{id=doctest} filter such as `--test-suite=Physics*` runs the whole Systems group.

   **You should see:** a summary that counts the cases of the suite and ends with `Status: SUCCESS!`.

   **If you do not see it:** the filter matches no suite when one letter is wrong, and doctest then reports zero test cases. Compare the name with the one in the file.

2. Test the force function first, because everything else rests on it. The function takes the zone, the zone's :term[world transform]{id=world-transform} and a position, and gives the force on a body there, with no scene and no physics. Write one case per row of this table, and compute each expected number by hand before you run the test.

   | Case | Zone | Position | Expected force |
   | --- | --- | --- | --- |
   | Directional, inside | Strength 12 N, Radius 5 m | 3 m from the centre | 12 N along the zone's axis |
   | Spherical, inside | Strength 12 N, Radius 5 m | at (3, 0, 0) | 12 N along +X, away from the centre |
   | The centre | Spherical, Strength 12 N | at the centre | 0 N, a finite force, never not-a-number (:term[NaN]{id=nan}) |
   | Outside | Spherical, Radius 5 m | 6 m from the centre | 0 N; a Directional zone still pushes |
   | Calm | Strength 0 N | anywhere inside | 0 N |
   | Scaled | Spherical, Radius 5 m, scale (1, 2, 1) | 6 m from the centre | 0 N, because the radius never follows the scale |
   | Degenerate | Directional, scale 0 | any | a finite force, 0 N, no division by zero |

   Each row guards one decision. The centre row exists because "away from the centre" has no direction there, and code that divides by the distance gives NaN, which would poison a body's pose. The scaled row exists because the :term[gizmo]{id=gizmo-start}, the force, the overlap query and the command use one rule for the radius. A zone drawn with one radius and pushing with another would mislead everyone who tuned it by eye.

   **You should see:** seven new cases that pass, and no NaN in any message.

   **If you do not see it:** a case of the table that fails shows the real value next to your number. Decide which one is right before you change either, because a wrong expectation is as likely as a wrong function.

3. Test the system in a real scene. The engine already has the pattern, in the test of mass and damping of the suite `Physics.Simulation`. A force acts over one step, so the speed it gives is the force divided by the mass, times the length of the step.

   ```cpp src="StrataTests/src/Physics/PhysicsSimulationTests.cpp#L223-L250"
   TEST_CASE("Mass and damping shape the response to impulses and forces")
   {
   	Scene scene;
   	scene.GetSettings().Gravity = glm::vec3(0.0f);
   	Entity light = CreateDynamicBox(scene, "Light", glm::vec3(0.0f, 0.0f, 0.0f));
   	Entity heavy = CreateDynamicBox(scene, "Heavy", glm::vec3(0.0f, 5.0f, 0.0f));
   	Entity damped = CreateDynamicBox(scene, "Damped", glm::vec3(0.0f, 10.0f, 0.0f));
   	Entity pushed = CreateDynamicBox(scene, "Pushed", glm::vec3(0.0f, 15.0f, 0.0f));
   	heavy.GetComponent<RigidBodyComponent>().Mass = 4.0f;
   	pushed.GetComponent<RigidBodyComponent>().Mass = 2.0f;
   	for (Entity entity : { light, heavy, pushed })
   		entity.GetComponent<RigidBodyComponent>().LinearDamping = 0.0f;
   	damped.GetComponent<RigidBodyComponent>().LinearDamping = 2.0f;

   	scene.OnRuntimeStart();
   	PhysicsSystem& physics = GetPhysics(scene);

   	// Impulses change the velocity immediately by impulse / mass.
   	CHECK(physics.AddImpulse(light, glm::vec3(4.0f, 0.0f, 0.0f)));
   	CHECK(physics.AddImpulse(heavy, glm::vec3(4.0f, 0.0f, 0.0f)));
   	CHECK(physics.GetLinearVelocity(light).x == doctest::Approx(4.0f));
   	CHECK(physics.GetLinearVelocity(heavy).x == doctest::Approx(1.0f));

   	// A force acts over one step: dv = F / m * dt.
   	CHECK(physics.AddForce(pushed, glm::vec3(12.0f, 0.0f, 0.0f)));
   	CHECK(physics.SetLinearVelocity(damped, glm::vec3(4.0f, 0.0f, 0.0f)));
   	StepScene(scene, 1);
   	CHECK(physics.GetLinearVelocity(pushed).x == doctest::Approx(12.0f / 2.0f / 60.0f));
   ```

   1. **Line 226:** gravity is zero, so only the force moves a body.
   2. **Lines 232–234:** the pushed box weighs 2 kg and has no damping, so nothing hides its speed.
   3. **Line 246:** the comment states the rule that the wind test uses again: one step of force gives a change of speed.
   4. **Line 247:** a force of 12 N along X.
   5. **Lines 249–250:** one step through `StepScene`, then the speed 12 / 2 / 60 = 0.1 m/s.

   The wind test has the same shape, with the zone in the place of `AddForce`. In the :term[pseudocode]{id=pseudocode} below, a box of mass 2 kg stands inside a zone of Strength 12 N, with gravity off. One step must give it 12 / 2 / 60 = 0.1 m/s along the axis, because the fixed step is 1/60 s.

   ```pseudocode
   scene.gravity = 0
   box = dynamic box, mass 2, damping 0, inside the zone
   outside = dynamic box beyond the radius
   wall = static box inside the zone
   sleeper = dynamic box inside the zone, put to sleep
   start the scene; step it once
   check box velocity along the axis == 12 / 2 / 60
   check outside velocity == 0, wall did not move
   check sleeper is awake and moving
   ```

   Four more cases follow from the same scene. A body outside the radius is not pushed. A :term[static body]{id=static-body} is not pushed, because a force on it means nothing. A sleeping box wakes, since a force that leaves it asleep would be silent. And a scene started in :term[Simulate mode]{id=simulate-mode}, the editor's physics-only mode, pushes too: the system must run there as it does in Play.

   **You should see:** the four cases pass, and the first one checks the speed 0.1 m/s with the tolerance of `doctest::Approx`.

   **If you do not see it:** a speed of exactly 0 means the system never ran. Check that the scene started with `OnRuntimeStart` and that the step went through `OnUpdateRuntime`, as `StepScene` does.

4. Test :term[determinism]{id=determinism} with a twin run. Physics results must be identical with any number of threads, so the wind must not change that. The twin pattern of the physics suite runs the same scene twice, once with no worker threads and once with three, and compares the poses bit for bit.

   ```pseudocode
   first = simulate the zoned scene on one thread
   second = simulate it again
   check poses of first and second are identical
   open a job system with 3 workers
   third = simulate it again
   check poses of first and third are identical
   ```

   The comparison is exact, with no tolerance, because a force that depends on the order of the threads shows as a difference in the last digit.

   **You should see:** all three runs agree.

   **If you do not see it:** poses that differ only with the workers mean the system adds forces in an order that depends on the threads. Gather the zones in a fixed order, as the system does each step.

5. Test the gizmo without a :term[graphics card]{id=gpu} (GPU). A gizmo is a drawing the editor adds to show a component, here the sphere or the arrow of the zone. The scene draws its gizmos into a `DebugDraw`, a list of coloured lines, and the test reads the lines back. The test of the character controller's gizmo is the model.

   ```cpp src="StrataTests/src/Renderer/DebugDrawTests.cpp#L252-L284"
   TEST_CASE("Character controllers show an upright capsule standing on their origin")
   {
   	Scene scene;
   	Entity character = scene.CreateEntity("Character");
   	TransformComponent& transform = character.GetComponent<TransformComponent>();
   	transform.Translation = glm::vec3(5.0f, 1.0f, 0.0f);
   	// Neither rotation nor scale changes a controller's shape.
   	transform.Rotation = glm::angleAxis(glm::radians(90.0f), glm::vec3(1.0f, 0.0f, 0.0f));
   	transform.Scale = glm::vec3(3.0f);
   	CharacterControllerComponent& controller = character.AddComponent<CharacterControllerComponent>();
   	controller.Height = 2.0f;
   	controller.Radius = 0.5f;
   	scene.UpdateWorldTransforms();

   	DebugDraw debugDraw;
   	SceneGizmoSettings settings;
   	settings.Lights = false;
   	settings.Cameras = false;
   	DrawSceneGizmos(debugDraw, scene, settings);
   	const std::span<const DebugLineVertex> lines = debugDraw.GetLines(DebugDrawDepth::Tested);
   	REQUIRE_FALSE(lines.empty());
   	glm::vec3 low(1.0e9f);
   	glm::vec3 high(-1.0e9f);
   	for (const DebugLineVertex& vertex : lines)
   	{
   		low = glm::min(low, vertex.Position);
   		high = glm::max(high, vertex.Position);
   	}
   	CHECK(low.y == doctest::Approx(1.0f));
   	CHECK(high.y == doctest::Approx(3.0f));
   	CHECK(low.x == doctest::Approx(4.5f));
   	CHECK(high.x == doctest::Approx(5.5f));
   	CHECK(high.z == doctest::Approx(0.5f));
   ```

   1. **Lines 256–260:** a known place: a position, a turn and a scale.
   2. **Line 264:** the world transforms are brought up to date, because no frame runs.
   3. **Lines 266–270:** the scene draws its gizmos into a `DebugDraw`; no graphics card is involved.
   4. **Lines 271–279:** the lines are read back, and a loop keeps the lowest and highest corner.
   5. **Lines 280–284:** the extent is compared with numbers computed by hand.

   Your test gives the zone a known position, rotation and scale, draws, and checks the extent of its lines against numbers you computed. The Spherical zone must stay within its radius on every axis. The Directional zone's arrow must start at the centre and point along the axis. It sits in `DebugDrawTests.cpp` behind `#if ST_WITH_PHYSICS`, as the model does, because that file also serves builds without the module.

   **You should see:** lines between the numbers you computed, and a count of lines that does not change when you draw twice.

   **If you do not see it:** an empty list of lines means the zone's gizmo group is off in the settings of your test. Enable the group that the registration names.

6. Test the :term[inactive reason]{id=inactive-reason}. A property that another property can disable carries an inactive reason, the text the Inspector shows beside it, set with `ComponentRegistry::SetInactiveReason`. In each mode, ask the component registry for the reason of the property that the mode switches off, and check its words. Check that the other mode returns none.

   **You should see:** two cases that pass, one per mode.

   **If you do not see it:** a reason that is empty in the mode that needs it means the registration names the wrong property. Compare it with the component's registration.

7. Test the host function. Add a case to the suite `Scripting.API`, guarded by `#if ST_WITH_PHYSICS`, in which the test module of the application programming interface (API) calls the function. Add a second case in which the module makes the call on an older engine, whose host table ends before the new member, and gets the fallback of 0.

   **You should see:** both cases pass, and the older engine gives 0 without a crash.

   **If you do not see it:** a crash in the second case means the software development kit (:term[SDK]{id=sdk}) function reads a member that the older table does not hold. It must check for that member first.

8. Test the command. `wind.sample`, tested in the wind command suite of the editor, must answer in the editing scene and refuse a position that is not finite, with nothing changed. It must appear in the lists of kinds. Add a case with `component.add` and `component.set` through the :term[command registry]{id=command-registry}: a Radius outside its range is refused as invalid with nothing changed, and undo restores the state.

   **You should see:** each case passes. The suite of kinds names `wind.sample` once, in the list of queries.

   **If you do not see it:** the suite of kinds names the command and the list that lacks it. Add the name to the list that matches the kind in the registration.

9. Watch every new test fail. A test that never failed proves nothing, because it may check nothing. For each case, remove or break the single line it guards, build, run the suite and read the failure. Then restore the line.

   ```sh
   build/linux/bin/Debug/StrataTests --test-suite=Physics.WindZone
   ```

   Break one line per run, not all at once, so that each failure names one line.

   **You should see:** a failing check for each of the cases, naming the value it expected, for example a speed of 0 where it expected 0.1. After the restore, the suite passes again.

   **If you do not see it:** a case that still passes without its line checks something else, or too loosely. Tighten it until the broken line fails it. Do this now: a loose test is cheaper to repair than to explain in the review.

:::::

The golden rules of the engine ask for this: new behaviour ships with tests, and a regression test is seen failing without its fix. A test of the `WindZone` that you never saw fail is a test that may be wrong.

## Keep the feature test current

A unit test runs the code you thought of. The feature test runs the engine's one real project and fails on what you forgot.

The feature test checks three things. Every registered component sits on an entity of `Feature.stscene`, and each of its properties differs from its default on at least one entity. Every host function is called during a run. The run logs no warning it does not expect.

Your `WindZone` therefore has to appear in that scene, in each mode, with each property changed on some zone.

:::::steps

1. Run the feature test now, before you change anything, to see what the engine asks.

   ```sh
   ctest --preset linux-debug -R "^StrataTests.FeatureTest$"
   ```

   The pattern selects the in-process run of the feature test by its name.

   **You should see:** a pass. `Gust`, the Spherical zone of the earlier tutorials, already gives each property a value away from its default, and its script calls both wind functions.

   **If you do not see it:** a failure that names the `WindZone` means a step of [the last capstone](build.md) is missing. Continue: the next steps still add the Directional mode.

2. Give `Feature.stscene` a zone of each mode, with every property away from its default. Change the scene in a copy of the feature project through the editor and copy the saved file back, or change the :term[JSON]{id=json} directly. The Directional zone stands on an inactive entity, as the light called Moon holds alternate values. The scene has active :term[dynamic bodies]{id=dynamic-body}, and the physics probes of `PhysicsFeatures.cpp` expect each to fall straight down and come to rest on the :term[collider]{id=collider} below it. An active zone that reaches them moves them and fails the test.

   **You should see:** two entities with a `WindZone`, one of them carrying the `Inactive` component, with a Strength, Radius and Mode that differ from the defaults.

   **If you do not see it:** when a property is still the default on every zone, the coverage check names it. Change its value on the inactive entity.

3. Keep the active Spherical zone, `Gust`, away from the seven bodies, and add one dynamic body of its own inside it. Then extend the feature script that only called the :term[SDK's]{id=sdk} force function so that it expects the body pushed away from the zone's centre, not along an axis. The script checks the push in its `OnFixedUpdate`, as `PhysicsFeatures.cpp` checks its bodies falling, and calls `Expect`.

   ```pseudocode
   OnFixedUpdate:
       position = transform.world position
       force = Wind::GetForceAt(position)
       Expect(force points away from the zone's centre)
       Expect(this body moved away from the centre)
   ```

   The script reads the force and the motion in the same step, so one run shows whether the zone and the function agree.

   **You should see:** the feature script passes, and no other probe moved.

   **If you do not see it:** a failure of another probe, such as a body that no longer comes to rest on the collider below it, means the active zone reaches it. Move the zone or shrink its Radius.

4. Add `wind.sample` to the editor's feature :term[command script]{id=command-script}, with an `expect`, so that the real editor exercises the command. The script is a list of commands with expected answers. Its first entries ask the editor for its commands and :term[asset types]{id=asset-type}; read the ones after them, which open the feature scene and read it, then add yours beside them.

   ```json src="StrataTests/Editor/FeatureCommands.json.in#L7-L11"
   { "command": "scene.open", "parameters": { "scene": "Scenes/Feature.stscene" } },
   { "command": "script.load", "parameters": { "path": "$<TARGET_FILE:StrataTestScriptsFeatureTest>" },
   	"expect": { "/classes": { "min": 1 } } },
   { "command": "component.get", "parameters": { "entity": "F7E0000000000012", "component": "RigidBody" },
   	"expect": { "/values/Type": { "equals": "Dynamic" } } },
   ```

   Your entry samples the position of the zone's body and expects a force within a range, with `/force/0` and its siblings under `min` and `max`.

   **You should see:** the entry runs in `StrataEditor.FeatureTest`, which prints no failure.

   **If you do not see it:** a command with a wrong parameter name fails with the name of the parameter. Compare with the schema in the command's description.

5. Write the component schema snapshot again. The test `Reflection.ComponentSchema` compares the registry with `StrataTests/Architecture/ComponentSchema.json`, so a registration that changed (a new property or a new reason) fails it. The test program has a helper that rewrites the file.

   ```sh
   build/linux/bin/Debug/StrataTests --strata-test-helper=write-component-schema StrataTests/Architecture/ComponentSchema.json
   ```

   Read the :term[diff]{id=diff} before you keep it: the only changes should be the `WindZone`'s.

   **You should see:** a diff that touches only the `WindZone` entry.

   **If you do not see it:** a diff in other components means your build differs from the repository's, for example another set of modules. Rebuild with every module.

6. Run everything with the label `feature`.

   ```sh
   ctest --preset linux-debug -L feature
   ```

   The label gathers every run of the feature project, the one you ran first among them.

   **You should see:** every test of the label passes, among them the in-process feature test, the editor's and the exported game's.

   **If you do not see it:** read the first failure only. The feature test reports the first failed check of each scenario; later ones are often consequences.

:::::

## Measure what the wind costs

A game with a thousand bodies inside zones needs the wind to be cheap. A perf test turns that wish into a number and a limit. The pattern is the engine's test of 1,000 character controllers. A scene steps for a number of fixed steps and each step is timed. The median of the samples is checked against a budget, with up to three attempts when the machine is busy.

```cpp src="StrataTests/src/Perf/PhysicsPerfTests.cpp#L478-L515"
TEST_CASE("1,000 character controllers walking over steps")
{
	// A crowd: 1,000 controllers in a grid walk along +X over a ground crossed by 0.3 m steps every 4 m (each walks up and
	// down steps, its stairs and floor queries run every step), with nobody listening to contacts. The median scene update
	// of one fixed step (60 Hz) against Perf.Physics.Characters1000Step (the workstream's acceptance limit is 2 ms).
	Perf::ScopedApplicationJobSystem jobs;
	Perf::CheckBudgetConfirmed("Perf.Physics.Characters1000Step", [&]
	{
		constexpr uint32_t c_Characters = 1'000;
		Scene scene;
		const SettleScene crowd = CreateCharacterCrowd(scene, c_Characters);
		const Entity first = scene.FindEntityByName("Character 0");
		REQUIRE(first);
		scene.OnRuntimeStart();
		REQUIRE(scene.GetService<ICharacterControl>() != nullptr);
		crowd.BeforeStep(scene, 0); // Every character walks along +X at 2 m/s

		constexpr uint32_t c_Warmup = 10;
		constexpr uint32_t c_Steps = 60;
		std::vector<double> samples;
		for (uint32_t step = 0; step < c_Warmup + c_Steps; step++)
		{
			const Clock::time_point start = Clock::now();
			scene.OnUpdateRuntime(scene.GetSettings().FixedTimestep);
			const double elapsed = MillisecondsSince(start);
			if (step >= c_Warmup)
				samples.push_back(elapsed);
		}
		const PhysicsStats stats = GetPhysics(scene).GetStats();
		CHECK(stats.CharacterControllerCount == c_Characters);
		// They walked on: past the first step at x = 2..4 for the first rows.
		CHECK(GetWorldPosition(scene, first).x > 1.5f);
		const Perf::Measurement step = Perf::Summarize(samples);
		MESSAGE("1,000 characters: median step ", step.MedianMs, " ms (p95 ", step.P95Ms, " ms); controllers ", stats.CharacterTime, " ms, library ",
			stats.LibraryStepTime, " ms");
		scene.OnRuntimeStop();
		return step.MedianMs;
	});
```

1. **Lines 480–482:** the comment names the scene, the metric and the step it measures.
2. **Line 484:** the check takes the metric's name, and its function is one attempt.
3. **Lines 495–505:** 10 steps of warm-up, then 60 timed fixed steps.
4. **Lines 506–509:** the test proves that the work happened, so a fast scene is not an empty one.
5. **Lines 510–514:** the median of the samples is the value the check compares.

Your test has the same shape and measures two numbers. One is the median of the scene's fixed step with bodies inside zones. The other is the wind system's own part of it: a time the system keeps for its fixed update, read through `GetSystem<WindZoneSystem>`, beside the scene update's median. A median is the middle sample once they are sorted: a few slow steps cannot move it.

:::::steps

1. Write the test in `StrataTests/src/Perf/PhysicsPerfTests.cpp`, inside the suite `Perf.Physics`, A build without Physics omits this file, because it is on the module's list. Fill a scene with bodies, place zones over them, warm up for 10 steps, time 60 and return both medians.

   ```pseudocode
   scene = 2,000 boxes, 40 zones over them
   warm up: 10 steps
   for 60 steps: time the scene's step; read the wind system's time
   return { step: median of the first, wind: median of the second }
   ```

   The test measures with the engine's own steps, so the numbers are what a game would pay.

   **You should see:** a test that compiles in Release and records two values.

   **If you do not see it:** a :term[link error]{id=link-error} that names the system means the include of its :term[header]{id=header} is missing.

2. Give each metric its own entry in `StrataTests/Perf/Budgets.json`. The file's comment is its specification: every metric a test checks or records needs an entry, or the test fails. On a machine that is not the :term[reference machine]{id=reference-machine}, which the file names, the entry is provisional: a unit and `"Provisional": true`, and no numbers.

   ```diff src="book:tutorials/capstone/land.patch#hunk-1"
    	"Perf.Physics.Create10kBodies": { "Measured": 15.76, "Budget": 23.64, "Unit": "ms", "Target": 7.995 },
    	"Perf.Physics.Characters1000Step": { "Measured": 0.8108, "Budget": 1.2, "Unit": "ms", "Target": 0.70 },
   +	"Perf.Physics.WindZoneStep": { "Unit": "ms", "Provisional": true },
   +	"Perf.Physics.WindZoneSystem": { "Unit": "ms", "Provisional": true },
    	"PerfGPU.Editor.ImportSettings4kMaxFrame": { "Measured": 3.866, "Budget": 5.799, "Unit": "ms" },
   ```

   A provisional metric is measured and recorded, and never checked. Numbers from other machines never go into an entry, because a budget compares one machine's cost with itself.

   **You should see:** the entries in the file, with two names that the test uses exactly.

   **If you do not see it:** the test fails with the name of a metric that has no entry. Compare the names letter by letter.

3. Run the perf tests in the Release build. A Debug build multiplies every cost and proves nothing about the shipped engine.

   ```sh
   ctest --preset linux-release -L perf
   ```

   Do this on a quiet machine. A failure on a busy one says nothing about the code, because the attempts of a check follow each other within about a minute, and a build that lasts longer slows all of them.

   **You should see:** the test passes and prints its two medians, in milliseconds.

   **If you do not see it:** a run that fails on a provisional metric is a bug of the test, since such a metric never fails. Read the message.

4. Read the result. The perf tests write their measurements to a results file of the build, `PerfResults`. Note the two medians. On your machine they stay in your notes and in the message of the commit, never in `Budgets.json`.

   **You should see:** two numbers, each a fraction of the frame's 16.7 ms.

   **If you do not see it:** values near 0 mean the zones reached no body. Check the scene of the test.

:::::

Who sets the numbers? Only the reference machine. On it, the entry gets `Measured`, the median, and a `Budget` of at most 1.5 times that, rounded down. `Tools/PerfStability.py --runs 5` runs the perf tests five times before the commit merges.

The tool shows which metrics were unstable, how busy the machine was, and how often a check needed more than one attempt. The rule behind it is the **ratchet**: budgets only go down. A change that makes the wind cheaper measures it again. It lowers `Measured` and `Budget` in the same commit. A metric over its budget is a regression to fix, never a reason to raise the budget.

## Update the documents

A change is not finished while the next person must read the code to learn it. Strata keeps its explanations in a few places, and each part of the change goes to the one that describes it. `AGENTS.md` changes only when a rule changes. Your change adds no rule, so the file stays as it is, and the test `Docs.AgentGuide` still checks that it stays under its limit of 40,000 characters.

:::::steps

1. Add the component and its system to the section "Physics" of `Docs/DeveloperGuide.md`: what the zone does, its modes, and the system that applies the forces in each fixed step.

   **You should see:** a paragraph and a line in the section's list of parts.

   **If you do not see it:** a section named differently means the guide changed; search for "Physics" at the level of a chapter.

2. Add the SDK's two wind functions, the strength and the force at a position, to the guide's "Gameplay API". Add the wind group to its line "Host function order" too. That line names each appended group in the order of the list `ST_SCRIPT_HOST_FUNCTIONS`, part of the binary interface with script modules, and your change appended to it.

   **You should see:** both functions in the gameplay list, and the wind group at the end of the host function order.

   **If you do not see it:** a function absent from the guide fails nothing, so check by reading the SDK's wind functions against your text.

3. Write a paragraph in `Docs/Manual/Scripting.md`, for people who make games, with the two functions and what they return when no zone is there. Add the two functions to the "API cheat sheet" of the skill `strata-scripting`. Add one line for the wind to the wave's draft release notes, `Docs/Plans/Wave8/ReleaseNotes.md`: the notes of a release in `Docs/Releases/` are written from that file when the release is made.

   **You should see:** four small edits in four files, each with the part it describes.

   **If you do not see it:** nothing fails when a document is missing. The review is the only gate that notices.

:::::

## Review the change

The unit tests, the feature test and the perf test check your change. The full run checks the whole engine against it. Run it now, with every suite, because a change can break a suite that its patch never names.

One example is `CLI.McpToolsets`. It fails for a command that belongs to no toolset of the table. It passes for `wind.sample`, because the command capstone gave the `wind.` group its toolset. A toolset is a named group of commands that an agent loads together.

```cpp src="StrataTests/src/Editor/EditorMcpToolsetsTests.cpp#L56-L60"
std::set<std::string> known;
for (const McpToolsets::ToolsetInfo& toolset : McpToolsets::GetKnownToolsets())
	known.insert(std::string(toolset.Name));
for (const RpcMethodInfo& method : methods)
	CHECK_MESSAGE(known.contains(McpToolsets::GetGroupToolset(method.Name)), method.Name, " is in no toolset of the table");
```

The test asks the table for the toolset of every registered command and fails for one that has none. Your command passes without a line of yours, but only because an earlier change prepared the table.

:::::steps

1. Run every suite of your platform in Debug, side by side.

   ```sh
   ctest --preset linux-debug -j 8 -LE gpu
   ```

   The option `-LE gpu` omits the tests that need a graphics card, which a CI machine lacks too.

   **You should see:** every test passes, in a few minutes.

   **If you do not see it:** a failure in a suite your patch never names is the point of this step. Read it before you run it again: unreliable runs hide real ones.

2. Walk the pre-commit checklist over the staged diff. Stage everything, then read `git diff --staged` from the top, with the six items beside you: correctness (empty inputs, zero sizes, resources released), tests, style, portability, documentation and commit hygiene. Fix every finding before you commit, not after.

   ```sh
   git add -A
   git diff --staged
   ```

   The first command stages every change, the second shows exactly what a commit would hold.

   **You should see:** the whole change, test files and documents included, and nothing that is not yours.

   **If you do not see it:** files in the diff that are not yours, such as a build folder, mean the ignore rules differ. Take them out of the next commit with `git restore --staged <path>`.

3. Check the compilers you do not have. `Tools/CompatLint.py` compiles the changed files with the compilers closest to CI's, so that a missing include that your compiler tolerates appears before the push.

   ::::tabs{sync=os}
   :::tab[Windows]
   The tool does not run on Windows: it reads the Debug compile commands of a Ninja tree of the `linux` or `macos` preset and needs GCC 14 and LLVM 16. The run of the CI branch is your check, in the last section.
   :::
   :::tab[Linux]
   Install GCC 14 and LLVM 16 with its :term[standard library]{id=standard-library}, and configure and build the `linux` preset in Debug once. The tool's default compiler paths are Homebrew's, so name yours. Then compile the files changed since your starting commit; `HEAD` is that commit while nothing is committed.

   ```sh
   python3 Tools/CompatLint.py --changed-since HEAD --gcc g++-14 --clang clang++-16 --libcxx /usr/lib/llvm-16/include/c++/v1
   ```

   The tool compiles each changed `.cpp` file with its own flags and writes no object. A changed header is not compiled alone: name the files that include it.
   :::
   :::tab[macOS]
   Install the compilers with Homebrew (`brew install gcc@14 llvm@16`), build the `macos` preset in Debug once, then run the same command.

   ```sh
   python3 Tools/CompatLint.py --changed-since HEAD
   ```

   :::
   ::::

   Use the commit your chain started from, never `main`: in a clone, `main` is the engine's main, which is past your start, and the tool would also compile files you never touched.

   **You should see:** :term[exit code]{id=exit-code} 0 and no warning.

   **If you do not see it:** a failure names the file and the error. A missing include is the usual cause: add the include to the file that uses the name.

4. Split the change into commits, one logical change each, and make every commit pass on its own. The rule is golden: all tests pass before each commit. The feature test fails at any commit that adds a host function or a property without its call or its scene value. A last commit that holds all the tests would make every earlier commit fail. Each commit carries the tests it needs.

   | Commit | Carries |
   | --- | --- |
   | The specification | the document that names the decisions, already committed on [the first capstone page](plan.md) |
   | The forces | the force function, the system, their unit tests, the zones of the feature scene |
   | The arrow kind | the gizmo and its test |
   | The inactive reason | the reason and its test |
   | The host function | the function, its SDK function, the API test module, the `Scripting.API` cases, the feature script |
   | The command | `wind.sample`, the wind command suite of the editor, the kind lists, the feature command step |
   | The perf test | the test and its provisional entries; the message states the measured values |
   | The documents | each document with the part it describes |

   Use `git add <paths>` for each commit, and an imperative subject under 72 characters, with a body that says what and why. The perf commit's message states the two medians you measured, so a reader can compare them with the reference machine later.

   **You should see:** a short list of commits, each one explaining one idea.

   **If you do not see it:** a commit that holds two ideas hides them from a reader. Split it with `git reset` and stage the files again, in pieces.

5. Verify exactly what is committed in a clean :term[worktree]{id=worktree}, in Debug and in Release. Your working tree holds other files, such as build products and notes, and a change can pass only because of them. A worktree is a second copy of the repository, with its own folder and its own files.

   ```sh
   git worktree add ../strata-verify HEAD
   cd ../strata-verify && git submodule update --init --recursive --depth 1
   cmake --preset linux
   cmake --build build/linux --config Debug --parallel
   ctest --preset linux-debug -j 8 -LE gpu
   ```

   The worktree starts at your last commit. Check out each earlier commit in turn with `git checkout <commit>` and test it too, or at least the last one, then build and test in Release: `cmake --build build/linux --config Release --parallel`, then `ctest --preset linux-release -LE "gpu|perf"`. The first build is slow because the worktree has no cache.

   **You should see:** the same results as in your own tree, in both configurations.

   **If you do not see it:** a failure only in the clean tree means a file is missing from the commit, for example a new source or a document. Add it to the right commit.

:::::

## Run the change through CI

The last gate runs on machines you do not control. CI starts on a push to `main`, on a pull request, and on a push to a branch named `ci/<name>`. The branch name is a request to the system: build and test this before it reaches `main`. A change that lands many commits goes to such a branch first, and `main` moves only after a green run.

:::::steps

1. Make the branch and push it to your fork.

   ```sh
   git switch -c ci/windzone
   git push -u origin ci/windzone
   ```

   The first command makes the branch where you stand, and the second sends it to your fork and remembers it.

   **You should see:** :term[git]{id=git} reports a new branch on your fork, and the Actions tab of the fork shows a run called CI for it.

   **If you do not see it:** a branch name that does not start with `ci/` starts no run. Rename it. Also check that GitHub Actions is enabled in your fork.

2. Know what the run builds. The matrix has five jobs: Windows in Release and in Debug, Linux, macOS, and a Linux job without Audio, Physics and :term[GLFW]{id=glfw} (the window library) and without the editor. A sixth job builds every target in :term[Dist]{id=dist} on Windows. All of them build with warnings as errors.

   The last job proves what the other four cannot: that nothing a build without Physics compiles names the `WindZone`. The Scene layer's service, the host function and the guarded tests compile without the module. The editor's `wind.*` commands do name the component. The editor builds only with every module, so the other jobs build them.

   **You should see:** each job as a line in the run, with its name.

   **If you do not see it:** a run that never starts for a push means GitHub holds it for approval, or CI is disabled in your fork.

3. Wait for the result, and read it with the tool, not by hand. Logs need rights over the repository, while :term[annotations]{id=annotation} are public. The tool reads the state of the run and its annotations through the GitHub API, with the token that `gh` holds.

   ```sh
   python3 Tools/CIStatus.py status ci/windzone
   ```

   The command prints one line per run and one per job. Its exit code is 3 while a job still runs or none has started, so a script can wait on it.

   **You should see:** the jobs finish and the exit code becomes 0. It is 0 for a failed run too.

   **If you do not see it:** when a job fails, ask for its annotations.

   ```sh
   python3 Tools/CIStatus.py annotations ci/windzone
   ```

   Each annotation names the job, the file and the line, so you can read a failure without opening a log.

4. Fix what the annotations say. A :term[compiler error]{id=compile-error} shows the file, the line and the message, as the failed job found it; a failed test names the check. A common failure is a header that your compiler found through the :term[precompiled header]{id=precompiled-header} and another one does not. Fix it in the right commit, push again, and read the new run.

   **You should see:** a green run for every job.

   **If you do not see it:** a failure of one platform only usually names a difference of the compiler or the library. Search the annotation's message for the word that is new to you.

5. Decide what landing means for you. The tutorial ends at the green run of the branch. Whether you merge into the main branch of your fork is your choice, because that branch may be past the commit your chain started from. In the engine's own repository, the owner merges when the run is green.

   **You should see:** all six jobs green on the last commit of the branch.

   **If you do not see it:** a job that stays red for a reason you cannot read needs the annotations again with `--all`, which adds the notices.

:::::

You have walked one feature from its design to a green CI run. The same sequence lands every change of Strata, and you can follow it for the next one.

## Summary

- You wrote the unit tests of the `WindZone` in the wind suite, in fixed steps, and saw each fail without the line it guards.
- You changed the feature project so that its coverage checks pass, with a zone of each mode and the schema snapshot written again.
- You added a perf metric with provisional entries and explained why only the reference machine sets numbers and why budgets only go down.
- You reviewed the staged change, split it into commits that pass alone and verified it in a clean worktree.
- You ran the change on a CI branch and read its failures from annotations.

## Check yourself

1. Why does the Systems shard run the wind suite without you naming it anywhere?

   :::answer{tests="unit-tests"}
   The shard `Systems` in `StrataTests/CoreShards.json` takes every suite that starts with `Physics`, and the suite `Testing.Shards` fails when a suite belongs to no shard. A suite named after its module needs no extra entry.
   :::

2. A box of 4 kg stands in a zone of Strength 20 N, gravity off. What speed does it have after one fixed step of 1/60 s?

   :::answer{tests="unit-tests"}
   The speed is the force divided by the mass, times the step: 20 / 4 / 60 = 0.083 m/s, about 0.0833. A test checks it with a tolerance, since the float is not exact.
   :::

3. The feature test fails after you add a host function. Name two causes it checks.

   :::answer{tests="feature-test"}
   The function is never called by a feature script during the run, and the public SDK function that wraps it is not used by the feature scripts. A property with its default value on every entity also fails it.
   :::

4. Your machine measures the wind step at 0.40 ms. May the entry in `Budgets.json` say so?

   :::answer{tests="perf-metric"}
   No. Only the reference machine measures numbers for the file; elsewhere the entry stays provisional. Your number goes into your notes and the commit message.
   :::

5. Why does the Directional zone of the feature scene stand on an inactive entity?

   :::answer{tests="feature-test review"}
   The active bodies of the scene must come to rest where their feature scripts expect them. An active zone would push them and fail the test, and an inactive entity still gives the zone every property a value.
   :::

6. A job of the run fails and you cannot read its log. What do you run?

   :::answer{tests="ci-branch"}
   `python3 Tools/CIStatus.py annotations ci/windzone`: the failures are written as annotations, which are public, while logs need rights over the repository.
   :::

## Exercises

1. **Basic.** A later commit makes the wind cheaper. By the :term[ratchet's]{id=ratchet} rule, what must it change in `Budgets.json`, and why can your own machine not set the numbers?

   :::answer{tests="perf-metric"}
   The commit measures the metric again on the reference machine and lowers `Measured` and `Budget` in the same commit, and its message states the values. Your machine cannot set the numbers because the file holds the reference machine's measurements and a budget compares a machine with itself. On any other machine the entry stays provisional.
   :::

2. **Medium.** The reference machine measures the step with zones at 0.62 ms and the wind's part at 0.09 ms. Write the entries and the commit message.

   Hint: a budget is at most 1.5 times the measurement, rounded down.

   :::answer{tests="perf-metric" solution="tutorials/capstone/land/exercise-1.patch"}
   The budgets are 0.62 times 1.5 = 0.93 ms and 0.09 times 1.5 = 0.135 ms. The patch turns the two provisional entries, after the entry of the character crowd, into measured ones: each gets `Measured` and `Budget` and loses `"Provisional": true`. The message states the values: the step median 0.62 ms and the wind's part 0.09 ms, with their budgets.
   :::

3. **Hard.** Land the Falloff property of the exercise of [the capstone that built the change](build.md) the way you landed the `WindZone`. Give it its unit test, seen failing first, a value away from its default in `Feature.stscene`, the schema snapshot written again, its own commit and a green run of a new CI branch.

   :::answer{tests="unit-tests feature-test review ci-branch"}
   The commit holds the property, its unit test, the scene value on an inactive zone, the new `ComponentSchema.json` and the document line. Run the test without the property's effect to see it fail. Build in a clean worktree, push `ci/falloff`, and read it with `CIStatus.py`.
   :::

## Where it lives in Strata

- `WindZoneTests.cpp` in the Physics folder of the tests: the wind suite.
- `StrataTests/CoreShards.json`: the shards, with the Systems shard that runs `Physics*`.
- `StrataTests/CMakeLists.txt`: `STRATA_TESTS_OF_PHYSICS`, the tests that a build without Physics omits.
- `StrataTests/FeatureTest/` and `StrataTests/Editor/FeatureCommands.json.in`: the feature project and the editor's command script.
- `StrataTests/Perf/Budgets.json`: the budgets, and `StrataTests/src/Perf/PhysicsPerfTests.cpp`: the suite `Perf.Physics`.
- `Tools/PerfStability.py`, `Tools/CompatLint.py` and `Tools/CIStatus.py`: the tools of this page.
- `.github/workflows/ci.yml`: the jobs of CI.

## Further reading

- [doctest, "Command line"](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): every filter and option of the test program. Beginner.
- [Pro Git, "Git Branching"](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell): branches, the base of the CI branch. Beginner.
- [GitHub Actions documentation](https://docs.github.com/en/actions): how a workflow runs and how annotations appear. Intermediate.
