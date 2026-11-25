---
id: capstone/build
title: "Capstone II: from component to pixel"
description: "Turn the wind zone into a feature: forces on bodies, an arrow in the Scene view, a reason in the Inspector, a script call and a command."
kind: tutorial
size: L
tracks: [E]
needs: [physics/world-step, gpu/debug-drawing, editor-ui/inspectors, capstone/plan]
time: 240
learn:
  - id: wind-force
    text: compute the force that a directional and a spherical wind zone apply at a position
  - id: push-bodies
    text: explain why the wind system adds its forces in every fixed step and runs before physics
  - id: extension-points
    text: name the extension point that each layer of the wind feature uses
  - id: trace-edit
    text: trace one Strength edit from the Inspector to the pixels of the next frame
  - id: sample-command
    text: run wind.sample from a terminal and predict its answer
status: final
---

## What you will make

You will finish the wind zone. Wind will push bodies in Play and Simulate, and the Scene view will show each selected zone. The Inspector will say why `Radius` does nothing in a directional zone. Scripts will read the wind at a point, and agents will ask for it with a command. The drawing shows the first from above.

::figure{id=wind-pushes}

## One feature, seven layers

A component that only holds numbers is not yet a feature. The wind zone has a strength, a radius and a mode, and a system that gathers the zones. Nothing moves, nothing shows where the wind blows, and no script or agent can ask what it feels. One feature has to reach several parts of the engine, and each part has its own door.

Strata keeps these doors on purpose. The Physics module does not know the :term[renderer]{id=renderer}, and the renderer does not know the wind zone. The editor does not know how the force is computed. Each part offers one place where a module can plug in, and the feature uses each place once. You learned all of them on earlier pages; this page uses them together, in the order a force travels.

A small case shows what you build. A spherical zone of 20 newtons stands at the origin with a radius of 5 meters. A crate of 2 kilograms lies at (3, 0, 4), exactly 5 meters away. The force on the crate is 20 newtons along the :term[unit vector]{id=unit-vector} (0.6, 0, 0.8), so it is (12, 0, 16) newtons. That force accelerates the crate by 10 meters per second squared, so its speed grows by 0.167 meters per second in each :term[fixed step]{id=fixed-step} of 1/60 second.

Now turn a directional zone of 20 newtons by 90 degrees around the Y axis. The zone blows along its local -Z, Strata's forward, and the rotation sends -Z to -X. The force on every :term[dynamic body]{id=dynamic-body} is (-20, 0, 0) newtons, wherever the body stands. You turn the entity, and the wind turns with it. These two cases are the specification of the first section, and you will check the code against them.

The seven sections follow the path of the feature. First one function computes the wind at a point. Then a system applies it to bodies, a :term[gizmo]{id=gizmo-start} draws it, a reason explains it, a :term[host function]{id=host-function} gives it to scripts, and a command gives it to agents. The last section follows one edit to the pixels.

:::note[The patch is not yet a commit]
All changes of this page form one patch, `tutorials/capstone/build.patch`. It lands, with its unit tests, on [the next page](land.md). Here you build it and run the tests that already exist.
:::

## What you need

- The end state of [the first capstone page](plan.md): the chain's patches applied, the sphere gizmo of [the debug drawing page](../gpu/debug-drawing.md) among them, and a `Debug` build of your system's :term[CMake preset]{id=cmake-preset}. Every command writes `<preset>` for that :term[preset]{id=preset}.
- A project with the checkpoint scene of [the command tutorial](../editor/tutorial-command.md): two wind zones, one of each mode, a floor and a row of dynamic crates. No step creates them.
- No file to import. You add two files and change sixteen.
- Time: about four hours. The builds are the longest wait.

:::files[The files of the change]

- `Docs/Architecture.md`: the wind service's row
- `Strata/src/Strata/Physics/`
  - `WindForce.h`, `WindForce.cpp`: new, the wind at a point
  - `WindZoneSystem.h`, `WindZoneSystem.cpp`: the system pushes bodies
  - `PhysicsComponents.cpp`: the gizmo for both modes and the :term[inactive reason]{id=inactive-reason}
  - `PhysicsRegistration.cpp`: the profile stage
- `Strata/src/Strata/Reflection/ComponentGizmo.h`: the arrow shape
- `Strata/src/Strata/Renderer/SceneGizmos.cpp`: drawing the arrow
- `Strata/src/Strata/Scene/SceneServices.h`: the wind service gives a force
- `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`, `StrataScriptCore/Include/StrataScript/`: the host function and the call of the script software development kit (:term[SDK]{id=sdk})
- `StrataEditor/src/Editor/`
  - `Commands/WindCommands.cpp`: `wind.sample`
- `StrataTests/`: the feature scene, one feature script, the gizmo test and the list of :term[command kinds]{id=command-kind}

:::

## Compute the wind at a point

The system and the command both need one answer: which force does the wind apply at this position? If each wrote its own formula, they would drift apart, and a script would read a wind that bodies never feel. You therefore write the answer once, as a function that knows no :term[scene system]{id=scene-system} and no physics world.

Two decisions come first. A zone's `Radius` never follows its entity's scale. The gizmo, the force and the overlap query all use the number as typed, so a scaled zone cannot draw a sphere where it does not push. And a zone pushes bodies of every :term[collision layer]{id=collision-layer}; a mask property can come later.

:::::steps

1. Create `WindForce.h` in `Strata/src/Strata/Physics/`. It holds the sample of one zone, which now also keeps the :term[world transform]{id=world-transform}, and the three functions you write next.

   ```cpp src="book:tutorials/capstone/build/WindForce.h#L14-L43"
   	class Scene;

   	// One wind zone as the wind code reads it: the component's values and where the zone stands in the world.
   	struct WindZoneSample
   	{
   		entt::entity Handle = entt::null;
   		glm::vec3 Position = { 0.0f, 0.0f, 0.0f }; // The zone's center in world space
   		glm::mat4 World = glm::mat4(1.0f);         // The zone's world transform: its rotation turns a directional zone's wind
   		float Strength = 0.0f;                     // Newtons
   		float Radius = 0.0f;                       // Meters, never scaled by the entity's scale
   		WindZoneMode Mode = WindZoneMode::Directional;
   	};

   	// The scene's zones that are active in the hierarchy, in the order of the registry. Reads the world transforms the scene
   	// caches: call Scene::UpdateWorldTransforms first when the scene was edited.
   	std::vector<WindZoneSample> GatherWindZones(Scene& scene);

   	// The force, in newtons, that one zone applies at a world position.
   	// Directional: Strength along the zone's local -Z (Strata's forward) turned by its world rotation, everywhere.
   	// Spherical: Strength away from the center within Radius of it, and nothing at the center itself or outside.
   	// A zone whose transform has no direction, a zone without strength and a position that is not finite give no force.
   	glm::vec3 GetWindForce(const WindZoneSample& zone, const glm::vec3& position);

   	// The sum of the forces of the zones at a world position.
   	glm::vec3 GetWindForceAt(std::span<const WindZoneSample> zones, const glm::vec3& position);

   	// The same sum over the active zones of a scene, read now: it works while the scene is edited, when no system runs.
   	glm::vec3 GetWindForceAt(Scene& scene, const glm::vec3& position);

   }
   ```

   1. **Lines 16–25:** the sample holds the component's values and the world matrix, whose rotation turns a directional zone.
   2. **Lines 27–29:** the zones of a scene, read from the cache of world transforms.
   3. **Lines 31–35:** the force of one zone, with the rules of both modes in the comment.
   4. **Lines 37–41:** two sums: over zones that the system gathered, and over a scene read now.

   The sample keeps the world matrix because the rotation of the entity decides where a directional zone blows. The two overloads of `GetWindForceAt` differ in where the zones come from: a list that the system gathered, or a scene read right now.

   **You should see:** a :term[header]{id=header} with `WindZoneSample` and the functions `GatherWindZones`, `GetWindForce` and two `GetWindForceAt`.

   **If you do not see it:** `WindZoneSample` exists already in `WindZoneSystem.h` from the earlier tutorial. The patch moves it here, so you remove it there in a later step.

2. Create `WindForce.cpp` beside it. Its first function reads the scene: it visits each wind zone, skips the zones that are not active, and keeps the position and the world matrix.

   ```cpp src="book:tutorials/capstone/build/WindForce.cpp#L25-L39"
   std::vector<WindZoneSample> GatherWindZones(Scene& scene)
   {
   	std::vector<WindZoneSample> zones;
   	for (const auto [handle, zone] : scene.GetRegistry().view<WindZoneComponent>().each())
   	{
   		const Entity entity(handle, &scene);
   		if (!scene.IsActiveInHierarchy(entity))
   			continue;

   		// Reading the world transform changes nothing, so the transform contract asks for no signal.
   		const glm::mat4 world = scene.GetWorldTransform(entity);
   		zones.push_back({ handle, glm::vec3(world[3]), world, zone.Strength, zone.Radius, zone.Mode });
   	}
   	return zones;
   }
   ```

   1. **Lines 28–32:** each entity with the component is visited, and one that is inactive in its hierarchy is skipped.
   2. **Lines 34–36:** the cached world matrix gives the center and the direction of the zone.

   Reading a world transform changes nothing, so the :term[transform contract]{id=transform-contract} asks for no signal here.

   **You should see:** a function of about fifteen lines.

   **If you do not see it:** a zone of an inactive entity must be absent. The call `IsActiveInHierarchy` checks the entity and its parents.

3. Add the force of one zone to the same file. This is the specification of the page in code, so read it against the two cases of the introduction.

   ```cpp src="book:tutorials/capstone/build/WindForce.cpp#L41-L61"
   glm::vec3 GetWindForce(const WindZoneSample& zone, const glm::vec3& position)
   {
   	if (!(zone.Strength > 0.0f) || !std::isfinite(zone.Strength) || !IsFinite(position))
   		return glm::vec3(0.0f);

   	if (zone.Mode == WindZoneMode::Directional)
   	{
   		// -Z is forward. Dividing by the axis' length keeps the scale of the entity out of the strength.
   		const glm::vec3 axis = -glm::vec3(zone.World[2]);
   		const float length = glm::length(axis);
   		if (!IsFinite(axis) || !(length > c_MinAxisLength))
   			return glm::vec3(0.0f);
   		return axis / length * zone.Strength;
   	}

   	const glm::vec3 offset = position - zone.Position;
   	const float distance = glm::length(offset);
   	if (!(distance > 0.0f) || !(distance <= zone.Radius) || !std::isfinite(distance))
   		return glm::vec3(0.0f);
   	return offset / distance * zone.Strength;
   }
   ```

   1. **Lines 43–44:** the guards: a zone without strength or a value that is not finite gives no force.
   2. **Lines 46–54:** a directional zone returns its flipped Z axis, divided by its length, times the strength.
   3. **Lines 56–60:** a spherical zone returns the direction away from the center times the strength, except at the center and beyond the radius.

   **You should see:** two branches and four guards that return the zero vector.

   **If you do not see it:** the guards are the point. Every case without a strength or a direction gives the zero vector, also the center of a spherical zone, where "away from the center" has no direction.

   **Why:** dividing the axis by its own length keeps the entity's scale out of the strength. A zone scaled to twice its size still blows with the strength typed in the Inspector.

4. Check the function by hand with the cases of the introduction before you build. The crate at (3, 0, 4) has the offset (3, 0, 4) from the zone at the origin and a distance of 5, which is not more than the radius. The force is the offset divided by 5 and multiplied by 20.

   **You should see:** (12, 0, 16) newtons. At the center the offset has length 0, and the guard `distance > 0` returns the zero vector. A crate at (6, 0, 8) lies 10 meters away, beyond the radius of 5, and gets nothing.

   **If you do not see it:** the directional case needs the matrix. The Z column of a matrix that turns 90 degrees around Y is (1, 0, 0), and the code flips its sign, which gives (-1, 0, 0) and a force of (-20, 0, 0).

:::::

The function reads no scene system and writes nothing. That makes it cheap to test, and [the next page](land.md) writes its tests: scaled zones, rotated zones, a zone at the origin and a position that is not finite.

## Push the bodies

A force that nobody applies does nothing. The wind system already runs once in every fixed step, so it applies the forces. Two services of the scene do the work, and you met both on [the physics page](../physics/world-step.md): `IPhysicsQueries` answers where the bodies are, and `IBodyControl` changes how they move.

Read the second one first. Its comment holds the rules that shape the system.

:::::steps

1. Open `Strata/src/Strata/Scene/SceneServices.h` and read `IBodyControl`.

   ```cpp src="Strata/src/Strata/Scene/SceneServices.h#L135-L157"
   // Changing the motion of the simulated bodies (PhysicsSystem). Velocities, forces and impulses act on dynamic bodies
   // only; functions return false for entities without such a body and for non-finite values.
   class IBodyControl
   {
   public:
   	virtual ~IBodyControl() = default;

   	virtual bool SetLinearVelocity(Entity entity, const glm::vec3& velocity) = 0;
   	virtual bool SetAngularVelocity(Entity entity, const glm::vec3& velocity) = 0;
   	// Forces and torques act during the next step only; impulses (linear and angular) change the velocity immediately.
   	virtual bool AddForce(Entity entity, const glm::vec3& force) = 0;
   	virtual bool AddForceAtPosition(Entity entity, const glm::vec3& force, const glm::vec3& worldPosition) = 0;
   	virtual bool AddImpulse(Entity entity, const glm::vec3& impulse) = 0;
   	virtual bool AddImpulseAtPosition(Entity entity, const glm::vec3& impulse, const glm::vec3& worldPosition) = 0;
   	virtual bool AddTorque(Entity entity, const glm::vec3& torque) = 0;
   	virtual bool AddAngularImpulse(Entity entity, const glm::vec3& impulse) = 0;
   	// Updates the body and the entity's RigidBodyComponent::GravityScale (any simulated body).
   	virtual bool SetGravityScale(Entity entity, float gravityScale) = 0;
   	virtual bool WakeUp(Entity entity) = 0;
   	// Moves the body and its entity instantly (any simulated body; keeping velocities and the entity's world scale).
   	// False also when the entity's parent is scaled to (nearly) zero, so the pose cannot be written.
   	virtual bool Teleport(Entity entity, const glm::vec3& position, const glm::quat& rotation) = 0;
   };
   ```

   1. **Lines 135–136:** forces act on dynamic bodies only, and a value that is not finite makes the call fail.
   2. **Lines 144–145:** a force lasts one step, so you add it again in every step.

   **You should see:** the comment before `AddForce`: forces act during the next step only.

   **If you do not see it:** search the file for `class IBodyControl`. No patch of the chain changes this interface, so your copy matches the quote.

   **Why:** a force is not a state. After the step that used it, the physics world forgets it. The system must add the force again in every fixed step, or the body drifts for one step and then stops accelerating.

2. Make the system's fixed update take its zones from your function. Then add a member `PushBodies`, which the update calls after the change events. Remove the old `WindZoneSample` from `WindZoneSystem.h`, which now includes `WindForce.h`.

   ```diff src="book:tutorials/capstone/build.patch#hunk-10"
    			changes.push_back({ entity, entity.GetUUID(), zone.Strength });
    		}
    		DispatchChanges(changes);
   +		PushBodies();
   +	}
   +
   +	void WindZoneSystem::PushBodies()
   +	{
   +		// Looked up in every step: the Physics system is created after this one, and a scene without it has no bodies to push.
   +		IPhysicsQueries* queries = m_Scene.GetService<IPhysicsQueries>();
   +		IBodyControl* bodies = m_Scene.GetService<IBodyControl>();
   +		if (!queries || !bodies)
   +			return;
   +
   +		// A force wakes its body, so a calm zone pushes nothing at all.
   +		const auto push = [&](const WindZoneSample& zone, Entity body)
   +		{
   +			const glm::vec3 force = GetWindForce(zone, glm::vec3(m_Scene.GetWorldTransform(body)[3]));
   +			if (force != glm::vec3(0.0f))
   +				bodies->AddForce(body, force);
   +		};
   +
   +		for (const WindZoneSample& zone : m_Zones)
   +		{
   +			if (!(zone.Strength > 0.0f))
   +				continue;
   +			if (zone.Mode == WindZoneMode::Spherical)
   +			{
   +				// Triggers do not feel wind: they are no bodies that move.
   +				for (const Entity body : queries->OverlapSphere(zone.Position, zone.Radius, c_AllPhysicsLayers, false))
   +					push(zone, body);
   +			}
   +			else
   +			{
   +				for (const auto [handle, rigidBody] : m_Scene.GetRegistry().view<RigidBodyComponent>().each())
   +				{
   +					if (rigidBody.Type == RigidBodyType::Dynamic)
   +						push(zone, Entity(handle, &m_Scene));
   +				}
   +			}
   +		}
    	}
    
    	WindChangeListenerID WindZoneSystem::AddWindChangeListener(WindChangeCallback callback)
   ```

   1. **Lines 9–13:** the system finds the services in every step; a scene without them has nothing to push.
   2. **Lines 15–21:** the one place where a force reaches a body. A body at the exact center of a spherical zone has a zero force, and the code skips it, because a force wakes a body.
   3. **Lines 25–26:** a zone of strength 0 is skipped before any query runs.
   4. **Lines 27–32:** a spherical zone asks `OverlapSphere` for the bodies inside it, with every layer and without triggers, in the :term[deterministic]{id=determinism} order of the query.
   5. **Lines 33–40:** a directional zone has no reach, so it visits every dynamic body.

   **You should see:** the system pushes bodies and still writes no transform and no component.

   **If you do not see it:** search your change for `Translation` and `MarkModified`; the wind system calls neither, because it only adds forces.

3. Check the order. The component tutorial already gave the system the :term[soft constraints]{id=soft-constraint} that run it after `Scripting` and before `Physics`, and the flag `RunsInSimulateMode`. Add one line to the :term[descriptor]{id=descriptor} in `PhysicsRegistration.cpp`, which gives the system its own stage in the frame profiler.

   ```diff src="book:tutorials/capstone/build.patch#hunk-4"
    		SceneSystemDescriptor windDescriptor = MakeSceneSystemDescriptor<WindZoneSystem>("WindZone", true, [](Scene& scene) { return CreateScope<WindZoneSystem>(scene); });
    		windDescriptor.AfterIfPresent = { "Scripting" };
    		windDescriptor.BeforeIfPresent = { "Physics" };
   +		windDescriptor.ProfileStage = "Scene.Wind";
    		const bool windRegistered = SceneSystemRegistry::Register(std::move(windDescriptor));
    		ST_CORE_VERIFY(windRegistered, "The physics module could not register the wind zone scene system");
    	}
   ```

   **You should see:** one new line after `BeforeIfPresent` that names the stage. The stages of the other systems start with `Scene`, and so does this one.

   **If you do not see it:** the profiler times a system only when its descriptor names a stage. Without the line, the wind's time counts for the stage around the scene's update.

   **Why:** the order is the whole point. The system adds forces and physics steps the world; if wind ran after Physics, its forces would wait in the queue and act one step late. :term[Simulate mode]{id=simulate-mode} runs the system as well because wind is physics, not gameplay: the editor's Simulate shows what Play shows.

4. The feature scene holds a zone, `Gust`, from the earlier tutorials. Until now it pushed nothing, but it would now push the `Compound` body, which stands 6.2 meters from it, and break scripts that expect that body at rest. Move it out of reach in `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene`: set its `Translation` to `[8, 1, -40]`.

   **You should see:** no dynamic body of the scene lies within 8.5 meters of the new position. The scripts that read `Gust` use its position, so they follow it.

   **If you do not see it:** the feature scene has seven dynamic bodies, and each of their scripts expects exact motion. A directional zone in this scene would push all of them, so this scene keeps none; a later page adds the zones that push on purpose.

5. In `WindZoneTests.cpp`, give the zone of the gizmo case the spherical mode, because a directional zone now draws an arrow. Then configure again, because two files are new, build, and run the suite that already knows the wind.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Physics.WindZone
   ```

   **You should see:** a build without warnings, and the suite passes: its five cases never check forces, and the gizmo case still finds its sphere.

   **If you do not see it:** a :term[compile error]{id=compile-error} about `WindZoneSample` means a second definition is left in `WindZoneSystem.h`.

:::::

The system now moves the crates, and you cannot see why. The next section lets the Scene view say where the wind blows.

## Draw the arrow

The wind zone already has a gizmo from [the debug drawing page](../gpu/debug-drawing.md): a sphere of its radius, drawn with the :term[colliders]{id=collider} in the collider group. A directional zone has no radius, so a sphere says nothing true about it. It needs an arrow along its -Z.

The renderer must not learn the wind zone, so you extend the vocabulary instead. The reflection layer gets a new shape, `Arrow`; the renderer learns to draw any arrow; and the Physics module fills it. Lower layers learn a shape, never a wind zone.

:::::steps

1. Add the kind and its length to `ComponentGizmoShape` in `Strata/src/Strata/Reflection/ComponentGizmo.h`.

   ```diff src="book:tutorials/capstone/build.patch#hunk-15"
    			Box,       // A box of HalfExtents around Transform's origin, along its axes
    			Sphere,    // A sphere of Radius around Transform's origin
    			Capsule,   // A capsule of Radius along Transform's Y axis, its cylinder 2 * HalfHeight long
   -			MeshBounds // The bounds of Mesh (when it is loaded: gizmos never load assets), placed by Transform
   +			MeshBounds, // The bounds of Mesh (when it is loaded: gizmos never load assets), placed by Transform
   +			Arrow       // An arrow of Length from Transform's origin along its -Z axis (forward)
    		};
    
    		Kind Type = Kind::Box;
   ```

   1. **Lines 4–6:** a comma makes room for the new kind `Arrow`, and its comment names the axis of the arrow.

   **You should see:** `Arrow` after `MeshBounds`, and a `Length` field of the shape.

   **If you do not see it:** the second change of this file, the `Length` field, sits in the next part of the patch. The shape holds both.

2. Draw the new kind in `DrawShape`, in `Strata/src/Strata/Renderer/SceneGizmos.cpp`. The function already draws four kinds the same way: it skips what the view cannot see and calls one `DebugDraw` function.

   ```diff src="book:tutorials/capstone/build.patch#hunk-17"
    						debugDraw.Capsule(shape.Transform, shape.Radius, shape.HalfHeight, settings.ColliderColor, settings.Depth);
    					return;
    				}
   +				case ComponentGizmoShape::Kind::Arrow:
   +				{
   +					const glm::vec3 from(shape.Transform[3]);
   +					const glm::vec3 forward = -glm::normalize(glm::vec3(shape.Transform[2]));
   +					if (view.IsVisible(from + forward * (shape.Length * 0.5f), shape.Length * 0.5f))
   +						debugDraw.Arrow(from, from + forward * shape.Length, settings.ColliderColor, settings.Depth);
   +					return;
   +				}
    				case ComponentGizmoShape::Kind::MeshBounds:
    				{
    					const Ref<Mesh> mesh = assets && assets->GetAssetState(shape.Mesh) == AssetState::Ready ? assets->PeekLoadedAsset<Mesh>(shape.Mesh) : nullptr;
   ```

   1. **Line 7:** the arrow points along the shape's -Z axis, :term[normalized]{id=normalization}, so a scale of the entity changes no length.
   2. **Line 8:** the visibility test uses the middle of the arrow and half its length as a sphere.
   3. **Line 9:** `DebugDraw::Arrow` draws the shaft and the head in the collider color.

   **You should see:** one new `case` between `Capsule` and `MeshBounds`.

   **If you do not see it:** a compiler error about a shape kind without a case means the `switch` lacks it. The function has no `default`, so that the :term[compiler]{id=compiler} finds each new kind.

3. Fill the shape for a directional zone, in the function of the wind zone's gizmo in `PhysicsComponents.cpp`. The same part of the patch also holds the reason function of the next section.

   ```diff src="book:tutorials/capstone/build.patch#hunk-2"
    			return true;
    		}
    
   -		// A wind zone shows its reach: a sphere of its radius around the entity's origin. Not scaled, like the zone itself.
   +		// How long a directional zone's arrow is drawn, in meters: it shows the direction, not the strength.
   +		constexpr float c_WindArrowLength = 2.0f;
   +
   +		// The Radius of a directional zone does nothing: the wind blows everywhere (PropertyInfo::InactiveReason).
   +		std::string WithoutRadius(const WindZoneComponent& zone)
   +		{
   +			return zone.Mode == WindZoneMode::Directional ? "Directional zones have no radius" : std::string();
   +		}
   +
   +		// A spherical zone shows its reach: a sphere of its radius around the entity's origin, not scaled like the zone itself. A
   +		// directional zone shows an arrow along the entity's -Z, where the wind blows.
    		bool WindZoneGizmo(const entt::registry&, entt::entity, const void* component, const glm::mat4& world, ComponentGizmoShape& outShape)
    		{
    			const WindZoneComponent& zone = *static_cast<const WindZoneComponent*>(component);
   +			if (zone.Mode == WindZoneMode::Directional)
   +			{
   +				const glm::vec3 axis = glm::vec3(world[2]);
   +				if (!std::isfinite(glm::length(axis)) || !(glm::length(axis) > 1.0e-6f))
   +					return false;
   +				outShape.Type = ComponentGizmoShape::Kind::Arrow;
   +				outShape.Transform = world;
   +				outShape.Length = c_WindArrowLength;
   +				return true;
   +			}
    			if (!std::isfinite(zone.Radius) || zone.Radius <= 0.0f)
    				return false;
    			outShape.Type = ComponentGizmoShape::Kind::Sphere;
   ```

   1. **Lines 5–6:** the arrow's length is fixed at 2 meters. It shows the direction and not the strength.
   2. **Lines 19–28:** a directional zone returns an arrow made from the world matrix, or no shape when its Z axis has no length.
   3. **Lines 29–31:** a spherical zone keeps the sphere of the chain; its guard for a bad radius now applies to this mode only.

   **You should see:** the function returns `false` for an arrow with a :term[degenerate transform]{id=degenerate-transform}, so nothing is drawn and nothing breaks.

   **If you do not see it:** the radius guard used to stand first, and a directional zone with the default radius passed it by luck. Put the directional branch before it.

4. Build the editor, open the checkpoint scene, and select both wind zones.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the first zone in the Hierarchy, then click the second while you hold the `Ctrl` key.
   :::
   :::tab[With a command]

   ```json
   { "command": "selection.set", "parameters": { "entities": [ "<the directional zone's ID>", "<the spherical zone's ID>" ] } }
   ```

   :::
   ::::

   **You should see:** a green sphere around the spherical zone and a green arrow at the directional zone, along its -Z.

   **If you do not see it:** the editor draws the collider group only for the selected entities and their children. A zone that is not selected shows nothing, because the :term[viewport]{id=viewport-input} setting that draws every collider is off. Enable it for all entities with `viewport.setSettings` and `{"allColliders": true}`; [the commands page](../editor/commands.md) shows how to run a command.

   The drawing shows the two shapes that the renderer receives.

   ::figure{id=wind-gizmos}

:::::

The arrow and the sphere show the wind, and the colliders keep their color. The gizmo costs nothing at :term[runtime]{id=runtime}: it exists only in the editor's :term[overlay]{id=overlay-core}.

## Say why the radius is off

A directional zone has a `Radius` that does nothing. A person who changes it sees no effect and concludes that the editor is broken. The engine's rule is that a property that another property disables gets an **inactive reason**, a sentence that the Inspector shows as a tooltip on the disabled row.

Look at how the Animation module does it, because your change copies the pattern.

:::::steps

1. Open `Strata/src/Strata/Animation/AnimationComponents.cpp` and read the function that gives the reason and the call that registers it.

   ```cpp src="Strata/src/Strata/Animation/AnimationComponents.cpp#L17-L45"
   	// The Animation system plays Clip only without a controller (PropertyInfo::InactiveReason).
   	std::string WithoutController(const AnimatorComponent& animator)
   	{
   		return animator.Controller.IsValid() ? "The controller's states choose the clips (Controller is set)" : std::string();
   	}

   }

   void RegisterAnimationComponents()
   {
   	ComponentRegistry::Register<SkinComponent>("Skin")
   		.Category("Animation")
   		.Description("Poses the entity's skinned mesh with an animator's joints")
   		.EntityProperty("Animator", &SkinComponent::Animator, { .Tooltip = "The entity with the Animator whose pose moves this mesh" });

   	// Speeds are bounded like a controller state's (AnimationController::c_MaxSpeed, which the Scene layer cannot include).
   	ComponentRegistry::Register<AnimatorComponent>("Animator")
   		.Category("Animation")
   		.Description("Plays a skeleton's animations: an animation controller's states, or one clip")
   		.AssetProperty("Skeleton", &AnimatorComponent::Skeleton, AssetType::Skeleton, { .Tooltip = "The joints the animations move (a model's Skeleton)" })
   		.AssetProperty("Controller", &AnimatorComponent::Controller, AssetType::AnimationController, { .Tooltip = "States, transitions and parameters; without one the animator plays Clip" })
   		.AssetProperty("Clip", &AnimatorComponent::Clip, AssetType::AnimationClip, { .Tooltip = "The clip played without a controller" })
   		.Property("Speed", &AnimatorComponent::Speed, WithTooltip(Range(-100.0f, 100.0f, 0.01f), "Playback rate; negative plays backwards"))
   		.Property("Loop", &AnimatorComponent::Loop, WithTooltip({}, "Whether the clip (without a controller) repeats"))
   		.Property("PlayOnStart", &AnimatorComponent::PlayOnStart, WithTooltip({}, "Starts playing when the scene starts"))
   		.Property("ApplyRootMotion", &AnimatorComponent::ApplyRootMotion, WithTooltip({}, "Moves the entity by the root joint's horizontal motion and turn"))
   		.EnumProperty("CullingMode", &AnimatorComponent::CullingMode, { { "AlwaysAnimate", 0, "Always Animate" }, { "WhenVisible", 1, "When Visible" } },
   			{ .Tooltip = "When Visible poses the skeleton only while a renderer draws a mesh it skins or its shadow; one that skins no mesh but moves attached parts poses always" });
   	ComponentRegistry::SetInactiveReason<AnimatorComponent>("Clip", &WithoutController);
   ```

   1. **Lines 17–20:** the reason function returns text while the property is off and an empty string while it works.
   2. **Line 45:** `SetInactiveReason` names the property and the function, after the component's registration.

   **You should see:** the reason function, and `SetInactiveReason` called after the registration.

   **If you do not see it:** the call must come after the component's `Register` call, while the registry is still open, because the registry freezes at the end of module registration.

2. Register the same pattern for the wind zone. The function itself is in the part of the patch that the last section quoted; this part of the patch adds the call.

   ```diff src="book:tutorials/capstone/build.patch#hunk-3"
    			.Property("Radius", &WindZoneComponent::Radius, WithTooltip(Range(0.01f, c_Unbounded, 0.05f), "How far the zone reaches from its center, in meters"))
    			.EnumProperty("Mode", &WindZoneComponent::Mode, { { "Directional", 0 }, { "Spherical", 1 } })
    			.Gizmo(ComponentGizmoGroup::Collider, WindZoneGizmo);
   +		ComponentRegistry::SetInactiveReason<WindZoneComponent>("Radius", &WithoutRadius);
    	}
    
    }
   ```

   **You should see:** one new line after the gizmo call.

   **If you do not see it:** the text must be exactly "Directional zones have no radius", as the engine's own guide for new components writes it. A test of a later page compares it.

   **Why:** the reason is data, not code of the user interface (UI). The Inspector draws the row disabled with the text as a tooltip, and `component.get` lists the same text under `inactive`, so an agent learns what a person sees.

3. Build, open a directional zone in the Inspector, and look at `Radius`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the directional zone and read the `Radius` row. Hold the pointer over it.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.get", "parameters": { "entity": "<the directional zone's ID>", "component": "WindZone" } }
   ```

   :::
   ::::

   **You should see:** the `Radius` row is dimmed and cannot be changed, and resting the pointer on its label shows the tooltip "Directional zones have no radius". The command answers with `values` and `"inactive": { "Radius": "Directional zones have no radius" }`. Change `Mode` to `Spherical`, and the row is enabled and `inactive` is gone.

   **If you do not see it:** if the row stays enabled, the editor still runs the old build. Close it and start the new one.

   Your row will look like the `Clip` row of the third-person sample's robot, whose Animator has a controller.

   ::figure{id=robot-clip}

:::::

## Give scripts the force

A script that wants to steer a leaf or a paper plane needs the wind at a point. The service of the earlier tutorial gives the strength as a number, which has no direction. You append a second function that gives the force as a vector, and follow the rules of [the host function tutorial](../scripting/tutorial-host-function.md) again.

:::::steps

1. Add `GetForceAt` to `IWindZones` in `Strata/src/Strata/Scene/SceneServices.h`, and implement it in `WindZoneSystem` by calling `GetWindForceAt` on the zones of the last fixed step. Update the service's row in `Docs/Architecture.md` to match.

   **You should see:** one new pure function in the interface, with a comment that says "as of the last fixed step".

   **If you do not see it:** another class that implements `IWindZones` fails to build. Only `WindZoneSystem` does at the pin.

   **Why:** the service answers from the last step, as the strength does, so a script sees the wind that the bodies felt. The command of the next section reads the scene instead, because while you edit, no system runs.

2. Append the function to the table of the host application programming interface (API), at the end of `StrataScriptHostAPI` in `StrataScriptCore/Include/StrataScript/ScriptABI.h` and of the list `ST_SCRIPT_HOST_FUNCTIONS` in `ScriptHostAPI.cpp`. Never insert it in the middle: the table is a contract with modules built earlier.

   **You should see:** a new member `GetWindForce` after `GetWindStrength`, which takes a position and writes three floats. It returns `false` and writes the zero vector when it fails.

   **If you do not see it:** the :term[application binary interface]{id=abi} (ABI) keeps its :term[ABI version]{id=abi-version}. Appending is compatible, and a module built before checks for the member before it calls.

3. Write the function that the table points to.

   ```diff src="book:tutorials/capstone/build.patch#hunk-19"
    			});
    		}
    
   +		bool HostGetWindForce(StrataScriptContext* context, const float* position, float outForce[3])
   +		{
   +			// The failure value is the zero vector, written before anything can go wrong.
   +			if (outForce)
   +				WriteVector3(glm::vec3(0.0f), outForce);
   +			return HostCall("GetWindForce", false, [&]()
   +			{
   +				ScriptSystem* system = ResolveContext(context, "GetWindForce");
   +				if (!system)
   +					return false;
   +				if (!outForce)
   +				{
   +					system->ReportProblem("GetWindForce", "the output pointer is null");
   +					return false;
   +				}
   +				const std::optional<glm::vec3> point = ReadVector3(*system, position, "position", "GetWindForce");
   +				if (!point)
   +					return false;
   +				const IWindZones* wind = system->GetScene().GetService<IWindZones>();
   +				if (!wind)
   +				{
   +					system->ReportProblem("GetWindForce", c_WithoutWind);
   +					return false;
   +				}
   +				WriteVector3(wind->GetForceAt(*point), outForce);
   +				return true;
   +			});
   +		}
   +
    		////////////////////////////////////////////////////////////////////////////////
    		// The table
    		////////////////////////////////////////////////////////////////////////////////
   ```

   1. **Lines 6–8:** the zero vector is the failure value, written before anything can go wrong, so that the caller reads a safe vector whatever happens.
   2. **Lines 9–11:** `HostCall` guards the whole body, and `ResolveContext` finds the scene system of the calling script.
   3. **Lines 14–18:** a null output pointer is a script's mistake, so the function reports it with `ReportProblem` and returns.
   4. **Lines 19–21:** a position that is null or not finite is refused with a report.
   5. **Lines 22–28:** a scene without the wind service reports that, and otherwise the force is written.

   **You should see:** no `assert` and no exception: every misuse is a report and a failure value.

   **If you do not see it:** a function that asserts on a script's mistake can crash the game from a script. Strata contains script crashes, but a report is cheaper and kinder.

4. Add the call to the SDK, in `Wind.h` of the SDK.

   ```diff src="book:tutorials/capstone/build.patch#hunk-24"
    			const StrataScriptHostAPI* host = ST_SCRIPT_DETAIL_HOST_WITH(GetWindStrength);
    			return host ? host->GetWindStrength(Detail::GetContext(), &position.x) : 0.0f;
    		}
   +
   +		// The force, in newtons, that the active wind zones add up to at a world position: a directional zone blows along its
   +		// entity's -Z, a spherical one away from its center. The zero vector where none reaches it, for a position that is not
   +		// finite, and with an engine that has no wind forces.
   +		static glm::vec3 GetForceAt(const glm::vec3& position)
   +		{
   +			glm::vec3 force(0.0f);
   +			const StrataScriptHostAPI* host = ST_SCRIPT_DETAIL_HOST_WITH(GetWindForce);
   +			if (host)
   +				host->GetWindForce(Detail::GetContext(), &position.x, &force.x);
   +			return force;
   +		}
    	};
    
    }
   ```

   1. **Line 12:** `ST_SCRIPT_DETAIL_HOST_WITH` finds the function only when the engine's table is large enough and the member is not null.
   2. **Lines 13–15:** with an older engine the call is skipped, and the force stays the zero vector: the SDK's fallback.

   **You should see:** the new call returns a `glm::vec3`.

   **If you do not see it:** scripts include `StrataScript/StrataScript.h`, which already includes `Wind.h` from the earlier tutorial.

5. Call the new function once from a feature script, so that the :term[feature test]{id=feature-test} of the patch runner passes. The script `WindFeatures` already reads the strength around `Gust`; add three checks to it.

   **You should see:** zero at the center. At 8 meters along +X the force is (25, 0, 0) newtons. At 9 meters, beyond the radius of 8.5, it is zero again.

   **If you do not see it:** the feature test fails when a registered host function is never called. That is the check that this step answers.

6. Build and run the feature test and the earlier script suite.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Scripting.Wind
   ```

   **You should see:** the suite passes. Run the feature test the way [the feature test page](../engineering/feature-test.md) says; it passes and logs no warning.

   **If you do not see it:** a warning about a host function that is never called names the function. Check the spelling in the script.

:::::

## Ask for the wind with a command

A script reads the wind of a running game. An agent that builds a scene wants the same answer while it edits, with no game running. A command gives it, and that needs no system: it calls the function of the first section on the scene as it stands.

The command is a query. It changes nothing, so a replay of a session omits it. It has a description written for an agent, a complete schema and one entry in the list of kinds.

:::::steps

1. Register `wind.sample` in `WindCommands.cpp`, beside `wind.list`.

   ```diff src="book:tutorials/capstone/build.patch#hunk-22"
    				return EditorCommandResult::Ok({ { "zones", std::move(zones) } });
    			}, EditorCommandKind::Query });
    
   +		registry.Register({ "wind.sample",
   +			"Gives the force, in newtons, that the active WindZone components of the scene add up to at a world position: {position, force "
   +			"([x, y, z]), strength (the length of the force)}. A directional zone blows along its entity's -Z everywhere, a spherical zone "
   +			"away from its center within its radius, and nothing blows at a center or outside it. Reads the scene as it stands, so it answers "
   +			"while editing and, while playing, for the running copy. Changes nothing.",
   +			ObjectSchema({ { "position", Vec3Schema("World position, in meters") } }, { "position" }),
   +			[](EditorContext& context, const nlohmann::json& parameters)
   +			{
   +				CommandArguments arguments(parameters);
   +				const std::optional<glm::vec3> position =
   +					arguments.Has("position") ? ReadVec3(parameters["position"]) : std::nullopt;
   +				if (!position)
   +					return EditorCommandResult::InvalidParameters("Parameter 'position' must be three finite numbers");
   +
   +				Scene& scene = *context.GetActiveScene();
   +				scene.UpdateWorldTransforms();
   +				const glm::vec3 force = GetWindForceAt(scene, *position);
   +				return EditorCommandResult::Ok({ { "position", { position->x, position->y, position->z } },
   +					{ "force", { force.x, force.y, force.z } }, { "strength", glm::length(force) } });
   +			}, EditorCommandKind::Query });
   +
    		registry.Register({ "wind.set",
    			"Sets the strength, radius or mode of the WindZone of one or more entities in one undo step (while playing it changes the "
    			"running copy only). Values left out stay as they are; at least one is required. Refuses, changing nothing, an entity without a "
   ```

   1. **Lines 4–8:** the description says what the answer holds and what the command does while playing, because an agent sees only the description and the schema.
   2. **Line 9:** the schema requires one `position` of three numbers.
   3. **Lines 12–16:** `Has` tells whether a position was given, and `ReadVec3` accepts three finite numbers only; anything else is refused before the scene is touched.
   4. **Lines 18–20:** the world transforms are brought up to date, then the sum over the active zones is read.
   5. **Lines 21–23:** the answer holds the position, the force and its length, and the kind is `Query`.

   **You should see:** the command never opens a transaction.

   **If you do not see it:** a handler that marks anything as modified does not belong to a query.

2. List the command among the queries in `CommandJournalTests.cpp`, next to `wind.list`. The toolset table needs no change: the prefix `wind.` already maps to its set.

   **You should see:** the journal test passes again, and fails if you leave the name out.

   **If you do not see it:** the test checks both ways: every command is in one list, and the registered kind matches the list.

3. Build, and start a headless editor with your project. This step has no menu or button: run the command. Make an empty scene so that the numbers below hold: `scene.new` with `{"force": true}`.

   **You should see:** the editor answers, and the scene holds no entity.

   **If you do not see it:** an editor that is not headless opens a window; close it and start again with the headless option, as the command tutorial did.

4. Create two zones with `entity.create`. This step has no menu or button: run the command. The breeze is directional with 10 newtons at the origin: `{"name": "Breeze", "components": {"WindZone": {"Strength": 10}}}`. The gust is spherical with 25 newtons and a radius of 8.5 meters, at (20, 0, 0).

   ```json
   { "name": "Gust", "components": { "Transform": { "Translation": [20, 0, 0] }, "WindZone": { "Strength": 25, "Radius": 8.5, "Mode": "Spherical" } } }
   ```

   Both calls answer with the identifier (:term[ID]{id=id}) of the new entity.

   **You should see:** two answers, each with an ID.

   **If you do not see it:** an error that names a component means the editor was built before this change of the tutorials. Build again and restart it.

5. Sample the wind at three points. Write `sample.json` with `{ "position": [24, 0, 0] }` and run the call; then change the position.

   ```sh
   build/<preset>/bin/Debug/StrataCLI call wind.sample @sample.json --project <project>
   ```

   **You should see:** at (24, 0, 0), 4 meters from the gust, the force is (25, 0, -10) and the strength about 26.93. The gust blows away from its center along +X, and the breeze blows along its -Z. At (20, 0, 0), the center of the gust, only the breeze counts: (0, 0, -10) and a strength of 10. At (40, 0, 0), beyond the gust's radius, the answer is again (0, 0, -10).

   **If you do not see it:** if the breeze shows a force along another axis, its entity is turned. A directional zone blows along its own -Z after the turn.

6. Try a position that is not three numbers: `{ "position": [1, 2] }`.

   **You should see:** the call fails with an error that names the parameter `position`, and a non-zero :term[exit code]{id=exit-code}. The scene is unchanged.

   **If you do not see it:** the schema check of the registry may refuse the call first, with its own message about the array. Both are refusals without side effects.

7. Undo the two creations and open the checkpoint scene again with `scene.open`, so that the next section finds its crates.

   **You should see:** `edit.undo` answers twice; the scene is empty; the checkpoint scene opens.

   **If you do not see it:** `scene.open` fails while the scene holds changes that are not saved. The two undo calls leave none, or pass `force`.

:::::

The command shows the layers' last rule. A feature reaches agents by registering a command, and no remote code is written: the registry makes it a method, a tool and a line of the journal.

## From component to pixel

You have written each door. Now watch the whole feature work, then follow what happens, name by name, from one edit to the frame.

:::::steps

1. Start the checkpoint scene.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press the Play button.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": {} }
   ```

   :::
   ::::

   **You should see:** the crates drift. Those in the directional zone slide along the arrow's direction, and those near the spherical zone are pushed away from its center. The floor stays still, and a crate that is pushed stays awake.

   **If you do not see it:** if nothing moves, check that the zones are active and have a strength above 0, and that the crates are dynamic bodies. The command `play.simulate` shows the same motion: wind is physics.

2. Change `Strength` of the directional zone while the game plays.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the zone and drag the `Strength` value in the Inspector.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the directional zone's ID>", "component": "WindZone", "values": { "Strength": 80 } } }
   ```

   :::
   ::::

   **You should see:** the crates accelerate within a few frames.

   **If you do not see it:** check that you changed the directional zone and that the crates stand in it. A value above 1000 is clamped to 1000, the end of the property's range.

   **Why:** an edit while playing changes the :term[running copy]{id=running-copy}. It gets no :term[undo step]{id=undo-step}, and `play.stop` discards it. The same edit made while editing is kept, can be undone, and acts from the next Play. [The play mode page](../editor/play-mode.md) tells why the two copies exist.

3. Stop the game and read the zone again.

   **You should see:** the strength is the one from before the edit.

   **If you do not see it:** you edited the scene before you pressed Play. Undo it with **Ctrl+Z**.

:::::

Here is the path of that one edit. Each hop belongs to a page you have read, and each uses the extension point of its layer.

The Inspector calls `SetPropertyWithUndo`. Read it: it checks that the scene may be edited, opens a transaction with a key that merges a drag into one step, and writes through `ComponentAccess`.

```cpp src="StrataEditor/src/Editor/PropertyEdit.cpp#L135-L155"
bool SetPropertyWithUndo(EditorContext& context, Entity entity, const ComponentInfo& component, const PropertyInfo& property, const PropertyValue& value,
	std::string* outError)
{
	if (!entity)
	{
		if (outError)
			*outError = "The entity does not exist";
		return false;
	}
	if (!context.CheckSceneEditable(outError))
		return false;
	const std::string mergeKey = fmt::format("Property/{}/{}/{}", entity.GetUUID().ToString(), component.Name, property.Name);
	SceneEditTransaction transaction(*entity.GetScene(), fmt::format("Edit {} {}", component.DisplayName, property.DisplayName), { entity.GetUUID() }, mergeKey);
	if (!ComponentAccess::SetProperty(entity, component, property, value, outError))
	{
		transaction.Rollback();
		return false;
	}
	context.CommitEdit(transaction);
	return true;
}
```

1. **Lines 144–145:** a scene that is being opened refuses the edit before anything changes.
2. **Lines 146–147:** the :term[merge key]{id=merge-editor} joins the steps of one drag into one undo step.
3. **Lines 148–150:** `ComponentAccess::SetProperty` validates and writes; a failure rolls the transaction back.
4. **Line 153:** `CommitEdit` records the undo step.

`ComponentAccess::SetProperty` is the one validated path into a component. It refuses a read-only property and a value of the wrong type, clamps a number to its range, writes the value and calls `MarkModified`, which is the signal of the transform contract's family. Nothing in the wind code polls the Inspector.

Then time passes. At its next fixed step the wind system gathers the zones again, reads the new strength and adds one force to each body it reaches. The Physics system steps the world, and the queued forces act inside that step.

Physics writes the new poses to the entities and calls `Scene::MarkTransformsChanged`, so the cached world transforms know they are stale. The scene computes them again, and the render scene follows the signals and takes the new matrices. When the scene :term[interpolates]{id=interpolation}, the renderer draws the pose between the last two steps, which is the :term[drawn transform]{id=drawn-transform}. The frame shows the crate a little further on.

The gizmo has a shorter path. The registry holds the wind zone's gizmo function from its registration. Each frame, `ViewportRenderer` hands the selection to `DrawSceneGizmos`, which calls the function for each selected zone and passes the shapes to `DrawShape`. `DebugDraw` collects the lines, and the renderer draws them as an overlay over the finished image.

```mermaid caption="Two paths to the pixels: an edit of Strength reaches the crates through physics, and the zone's gizmo reaches the screen through the debug draw list." alt="Two rows of boxes. The first row runs from the Inspector through the property write, the change signal, the wind system and the force on a body. It continues through the physics step, the write back of poses, the transform cache, the render scene and the drawn transform to the frame. The second row runs from the gizmo function through the scene gizmos, the debug lines and the overlay to the same frame."
flowchart LR
    I["Inspector"] --> P["SetPropertyWithUndo"] --> C["ComponentAccess and signal"] --> W["Wind system, next fixed step"]
    W --> F["AddForce"] --> S["Physics step"] --> B["Write back and MarkTransformsChanged"] --> T["Transform cache"] --> R["Render scene sync"] --> D["Drawn transform"] --> X["Frame"]
    G["Gizmo function"] --> H["DrawSceneGizmos"] --> L["DebugDraw lines"] --> O["Overlay"] --> X
```

:::why[One door for each layer]
Every hop passes through a registry, a service or a signal and never through a direct call across layers. The price is that a feature needs several small edits in several places, as this page did. The gain is that each layer can change or go missing: an engine without Physics still runs, a renderer never includes the wind zone, and a game without the editor still has the force.
:::

The wind feature now crosses Physics, Scene, Reflection, the Renderer, Scripting, the SDK and the editor. Each part used one extension point and no other: a system and its descriptor, a service, a gizmo shape, an inactive reason, an appended host function and a command.

## Summary

- You wrote the wind at a point once, as a function of the Physics module, and computed a directional and a spherical case by hand.
- You made the system push dynamic bodies in every fixed step, before physics, in Play and Simulate, with a profile stage.
- You named the extension point of each layer: the gizmo shape, the inactive reason, the appended host function with its SDK call and the query command.
- You traced a `Strength` edit from the Inspector to the pixels, and the gizmo's own path.
- You ran `wind.sample` and predicted its answers at three points.

## Check yourself

1. A spherical zone of 30 newtons stands at (0, 2, 0) with a radius of 4 meters. What force does it apply at (0, 2, 3), at (0, 2, 0) and at (0, 2, 5)?

   :::answer{tests="wind-force"}
   At (0, 2, 3) the offset is (0, 0, 3), the distance is 3 and not more than 4, so the force is (0, 0, 30) newtons, directed away from the center. At the center the distance is 0 and the direction is undefined, so the force is zero. At (0, 2, 5) the distance 5 is beyond the radius, so it is zero too.
   :::

2. A directional zone of 50 newtons is turned by 180 degrees around the Y axis. Along which axis does it blow?

   :::answer{tests="wind-force"}
   Without a turn, it blows along -Z. A turn of 180 degrees around Y sends -Z to +Z, so the force is (0, 0, 50) newtons. The zone's radius plays no part.
   :::

3. Why does the system call `AddForce` in every fixed step, and what happens when it runs after Physics?

   :::answer{tests="push-bodies"}
   A force acts during the next step only and is forgotten after it, so a body is pushed only in steps where the system adds a force. Run after Physics, the forces added in a step would wait for the next step and act one step late, always. The soft order before `Physics` keeps each force in the step it belongs to.
   :::

4. Which extension point does each layer use: the renderer, the Inspector and an agent?

   :::answer{tests="extension-points"}
   The renderer draws a new gizmo shape, `Arrow`, that the Physics module fills through its registered gizmo function; it never learns the wind zone. The Inspector shows an inactive reason that `SetInactiveReason` registered. An agent uses a command, `wind.sample`, which is a method and a tool as soon as it is registered.
   :::

5. In Play you change `Strength` from 10 to 80, and after `play.stop` it is 10 again. Why, and which edit would stay?

   :::answer{tests="trace-edit"}
   An edit while playing changes the running copy of the scene, which `play.stop` discards, and it has no undo step. The same edit made while editing changes the :term[edited scene]{id=edited-scene}, so it stays, can be undone, and acts from the next Play.
   :::

6. You call `wind.sample` at (20, 0, 0) in the empty scene of the last section, with the gust at (20, 0, 0). What is the answer, and why?

   :::answer{tests="sample-command"}
   The force is (0, 0, -10) and the strength is 10. The gust gives nothing at its own center, because the direction away from the center is undefined, so only the breeze counts. The directional breeze blows along its -Z everywhere.
   :::

## Exercises

1. **Basic.** Change `c_WindArrowLength` to 4 meters and look at the arrow in the Scene view. Then say which layer you changed and which two you did not.

   :::answer{tests="extension-points"}
   You changed the Physics module's gizmo function. The renderer still draws any arrow it receives, and Reflection still only describes the shape. This is why the shape carries a length and not the wind zone.
   :::

2. **Medium.** Add a `Falloff` property for spherical zones: the force falls from its full strength at the center to nothing at `Radius`. Give it its own inactive reason in directional mode, and say where the unit test of the first section changes.

   Hint: the factor is 1 minus the distance over the radius, mixed by the property.

   :::answer{tests="wind-force extension-points"}
   Add a float member and its `Property` line with a range from 0 to 1, a tooltip, and a second `SetInactiveReason` for it that returns "Directional zones have no radius" for the directional mode. In `GetWindForce` multiply the spherical force by one minus `Falloff` times the distance over the radius. The test of the 5-meter case keeps its result at `Falloff` 0 and gives 6 newtons for a crate at 2 meters in a zone of 10 newtons, a radius of 5 and `Falloff` 1. Write the component schema snapshot again, because you added a property.
   :::

3. **Hard.** Make the wind gust: its strength should change with the fixed steps run, never with frames, so that a run repeats.

   Hint: `Scene::GetFixedStepCount` is the game's own time base. Keep the gust out of the strengths that events report.

   :::answer{tests="push-bodies" solution="tutorials/capstone/build/exercise-3.patch"}
   The solution adds `GetGustFactor`, a factor between 0.5 and 1.5 that repeats every 120 steps and depends on the step count alone. `PushBodies` multiplies a copy of each zone's strength by it. The service, the events and the command keep reporting the component's strength, which is a cost: a script reads the steady wind, and the bodies feel the gust. Two runs with the same start give the same motion.
   :::

## Where it lives in Strata

- The folder `Strata/src/Strata/Physics/`: `WindForce.h` holds the wind at a point, and `WindZoneSystem.cpp` the forces and the service.
- `Strata/src/Strata/Scene/SceneServices.h`: `IBodyControl`, `IPhysicsQueries` and the wind service.
- `Strata/src/Strata/Reflection/ComponentGizmo.h` and `Strata/src/Strata/Renderer/SceneGizmos.cpp`: the gizmo shapes and `DrawShape`.
- `Strata/src/Strata/Animation/AnimationComponents.cpp`: the model of an inactive reason.
- `StrataEditor/src/Editor/PropertyEdit.cpp`: `SetPropertyWithUndo`.
- The folder `StrataEditor/src/Editor/Commands/`: `WindCommands.cpp` holds the wind commands.

## Further reading

- Glenn Fiedler, "Fix Your Timestep!": why forces and motion count in fixed steps, not frames: intermediate.
- The box3d documentation: how a physics library applies forces and wakes bodies: intermediate.
- Robert Nystrom, "Game Programming Patterns", chapter "Game Loop": the loop that these fixed steps belong to: beginner.
