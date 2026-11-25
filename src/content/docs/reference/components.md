---
id: reference/components
title: "Components and their properties"
description: "Every component the engine registers, with each property's type, range, options, default and the case where another property disables it."
kind: reference
size: XL
tracks: []
needs: [world/what-a-world-is]
status: final
---

You have a property name from a script, a scene file or a command, and you want its type, its range, its default and the page that explains it. This page lists every component of the engine with all of its properties, and the tables below it are generated from the engine itself. A dump of the editor's `component.list` command gives the names, types, ranges and descriptions. A second dump makes an entity, adds the component and reads it back with `entity.get`, which gives the default of each property.

## How to read an entry

Each component has a heading with its registered name. The **registered name** is the one that scripts, commands and scene files use, such as `PointLight`. Under it stand a one-line description and a line with the **display name**, the words the Inspector shows (`Point Light`), whether people and tools can add it, and whether they can remove it.

A component that people and tools cannot add has no defaults, because the dump could not add it. `PrefabInstance` is the only one: the engine adds it itself when you make an entity from a prefab. A line under a component may also say that adding it adds another component: adding any user interface (UI) component whose name starts with `UI`, except `UIRect` itself, also adds `UIRect`.

Below that, one row describes each property. The columns are:

- **Property**: the registered name, as a script or a scene file writes it.
- **Display name**: what the Inspector shows.
- **Type**: one of the property types `Bool`, `Int`, `UInt`, `Float`, `Vec2`, `Vec3`, `Vec4`, `Quat`, `Color3`, `Color4`, `String`, `Enum`, `Asset` and `Entity`. They are taught in [the scene reference](scene.md).
- **Default**: the value `entity.get` reports on a new entity. An `Asset` or `Entity` default of all zeros means no asset and no entity.
- **Range**: the minimum and the maximum, the asset type of an `Asset` property, or the options of an `Enum`. It also says when a property is read-only, and when it names a collision layer.
- **Description**: what the property does, and, after the words "Inactive (it has no effect) when", the case where another property disables it.

A default can look odd. `Name` shows `Defaults` because the dump named its entity so. A range such as `0.10000000149011612` is the stored number: the nearest value of a 32-bit float to 0.1.

How the engine registers a component once and shares that registration with files, panels and commands is taught in [Reflection](../world/reflection.md). How the Inspector draws a property and its inactive reason is taught in [Inspectors](../editor-ui/inspectors.md). A property of type `Asset` holds an asset handle, taught in [Handles and meta files](../assets/handles-meta.md). A property that names a collision layer is explained in [Collision layers](../physics/collision-layers.md).

## Where each category is taught

The generated part groups the components by their registered category, in the order of their names. Each category has a part of the book that explains what its components do.

- **Animation** (`Animator`, `Skin`, `AttachToJoint`): [how animation works as a system](../animation/system.md), with the clip, controller and culling facts in [the animation reference](animation.md).
- **Audio** (`AudioSource`, `AudioListener`): [clips, voices and sources](../audio/clips-voices-sources.md), and [spatial sound](../audio/spatial.md) for the distance fields.
- **Core** (`Name`, `Transform`, `Tag`, `PrefabInstance`): [the scene graph](../world/scene-graph.md) for the transform, and [prefabs](../world/prefabs.md) for the prefab link.
- **Lighting** (`DirectionalLight`, `PointLight`, `SpotLight`, `RectLight`, `LightSurface`, `SkyLight`): [lights](../light/lights.md), [the sky](../light/sky.md) and [shadows](../light/shadow-basics.md). `LightSurface`, new in 0.8.0 with `RectLight`, has no properties: it marks the glowing mesh that shows a rect light's face.
- **Physics** (`RigidBody`, the four colliders, `CharacterController`): [bodies and colliders](../physics/bodies-colliders.md) and [character controllers](../physics/character-controllers.md), with units and limits in [the physics reference](physics.md).
- **Rendering** (`Camera`, `MeshRenderer`, `HeightFog`, `ReflectionProbe`, `PostProcess`): [from entities to draws](../draw/entities-to-draws.md), [fog](../light/fog.md), [probes](../indirect/probes.md), [ambient occlusion](../indirect/ao.md), [screen-space reflections](../indirect/ssr.md) and [anti-aliasing](../image/spatial-aa.md).
- **Scripting** (`Script`, which shows no properties in the table, because its own code stores its list of script classes and their fields): [the script system](../scripting/script-system.md).
- **UI** (`Text` and eleven components whose names start with `UI`): [what game UI does](../ui/what-game-ui-does.md), with the enums in [the UI reference](ui.md).
- **World** (`World`, `StreamingSource`): [the streamer](../worlds/streamer.md).

`Text` stands among the UI components, but the :term[renderer]{id=renderer} registers it, in `Strata/src/Strata/Renderer/RendererComponents.cpp`. [Drawing text](../gpu/text.md) is where its drawing is taught. A game maker meets all of these components in [scenes and entities](../make/scenes-entities.md).

::include{file="components.md"}

## What the list omits

The command `component.list` omits a component that is hidden or that a scene file does not store as a component (the flag `NoSerialize`). It also omits each hidden or transient property of the others. The last two tables of the generated part name them: `ID`, `Relationship` and `Inactive`, and two hidden properties of `PrefabInstance`. Each row says why: the flags of the component or the property. Those flags are explained in [the scene reference](scene.md).

Runtime-only components that the engine never registers are not in any table: `HierarchyComponent`, `WorldTransformComponent`, `SubSceneComponent` and `UnknownComponentsComponent`. The scene computes the first three itself. The fourth keeps the components of a file that this build does not know, so that saving writes them back. The editor shows none of them.

The count is :value{key="components.count"} for the components the list returns, of which :value{key="components.addable.count"} can be added. The engine registers three more, the hidden ones, and the file `StrataTests/Architecture/ComponentSchema.json` pins the whole set. A change of the set fails a test until that file changes too.

Some properties carry the flag for collision layers, or a flag that limits a number to the powers of two. The range column says so in words; the flags themselves are in [the scene reference](scene.md).

## Where it lives in Strata

- `Strata/src/Strata/Reflection/ComponentRegistry.h`: the registry, the component flags and `SetInactiveReason`, the source of the inactive reasons.
- `Strata/src/Strata/Reflection/Property.h`: `PropertyType` and `PropertyFlags`.
- `Strata/src/Strata/Scene/ComponentRegistration.cpp`: the components of the scene module, from `ID` to `PrefabInstance`.
- `Strata/src/Strata/Animation/AnimationComponents.cpp`, `Strata/src/Strata/Audio/AudioComponents.cpp`, `Strata/src/Strata/GameUI/GameUIComponents.cpp`, `Strata/src/Strata/Physics/PhysicsComponents.cpp`, `Strata/src/Strata/Scripting/ScriptingComponents.cpp` and `Strata/src/Strata/World/WorldRegistration.cpp`: the components of the other modules.
- `Strata/src/Strata/Reflection/PropertyJson.cpp`: how a property value becomes the JSON that the dumps read.
- `Strata/src/Strata/Renderer/RendererComponents.cpp`: the renderer's components, including `Text`.
- `StrataEditor/src/Editor/Commands/EntityCommands.cpp`: `component.list`, which omits hidden components and those the scene stores itself, and `component.add`.
- `StrataTests/Architecture/ComponentSchema.json`: the set of components and properties the engine must register, checked by `StrataTests/src/Reflection/ComponentSchemaTests.cpp`.
