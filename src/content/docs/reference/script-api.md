---
id: reference/script-api
title: "The complete script API"
description: "Every name a game script can call: the C++ software development kit, the script callbacks, the host functions and the C types behind them."
kind: reference
size: XL
tracks: []
needs: [basics/programming-3]
status: final
---

This page lists every name that a game script can call: the script application programming interface (API). A game script is a C++ class that Strata runs for you. The tables below come from the headers of the software development kit (SDK) and from the C table that the engine fills, so they never drift from the code. Read a row from left to right: a name, its declaration, the comment its header gives it, and the file and line where it stands.

A script has two layers. Game code includes only `StrataScript.h` and calls the C++ SDK: `Input`, `Physics`, `Time` and the other classes of the first tables. Most SDK functions wrap one member of `StrataScriptHostAPI`, a table of plain C function pointers that the engine fills when it loads the script module; the helpers of `Gameplay.h` call none. The wrapping is why a script never links the engine: it only calls through the table. Game code reaches the game's user interface (UI), physics, input and sound the same way.

The fixed layout of that table is the application binary interface (ABI).

The SDK header `StrataScriptCore/Include/StrataScript/Host.h` holds the code that reaches the table.

A declaration such as `bool Play(std::string_view state)` reads like this. The word before the name is what the function returns, the names between the brackets are its parameters with their types. The word `const` after them promises that the call changes nothing in the object. Where a comment says "False" or "Nothing", that is the failure value: a function reports a problem by returning it and never by stopping the game. [Reading C++ declarations](../basics/programming-3.md) teaches the rules.

The engine has :value{key="hostFunctions.count"} host functions at the pin, and the SDK has :value{key="sdkClasses.count"} classes. The callback table has :value{key="scriptCallbacks.count"} rows. Four of them (`Create`, `Destroy`, `GetField` and `SetField`) belong to the SDK, so a script sees fifteen virtual functions, listed in the order of `StrataScriptClassDesc`.

## The generated tables

The next sections are one generated file. First come the host functions in declaration order, which is also the order in which releases appended them, with the release that added each ("Added in"). Then the script class callbacks, then one section for each SDK class, and last the macros.

::include{file="script-api.md"}

## The SDK groups and the pages that teach them

The headers of the SDK group the classes. Each group below has a page that teaches how to use it; this page only lists what exists.

| Header | Classes and enums | Taught by |
| --- | --- | --- |
| `Entity.h` | `Entity`, `Component`, `TransformComponent` | [Scripting the scene](../make/scripting-scene.md) |
| `Scene.h` | `Scene`, `Assets`, `SubScene` | [Scripting the scene](../make/scripting-scene.md) |
| `Input.h` | `Input`, the key codes of `Key` and `Mouse`, gamepads, input actions, binding capture | [Devices and their state](../input/devices-state.md) |
| `Time.h` | `Time` | [Timers and events](../make/timers-events.md) |
| `Log.h` | `Log` | [Programming, part 1](../basics/programming-1.md) |
| `Physics.h` | `RigidBody`, `Physics`, `RaycastHit`, `Collision` | [The world step](../physics/world-step.md) |
| `CharacterController.h` | `CharacterController`, `GroundState` | [The world step](../physics/world-step.md) |
| `Audio.h` | `AudioSource`, `Audio` | [The audio scene system](../audio/scene-system.md) |
| `Animator.h` | `Animator`, `JointTransform` | [Animation](../make/animation.md) |
| `Game.h` | `Game`, `WindowMode` | [Levels and saves](../make/levels-saves.md) |
| `Graphics.h` | `Graphics`, `GraphicsOption`, `QualityPreset` | [Quality settings](../image/quality-settings.md) |
| `UI.h` | `UIElement`, `UI`, `UIAction` | [UI input](../ui/input.md) |
| `World.h` | `World`, `WorldCellRequest` | [Physics and scripts in worlds](../worlds/physics-scripts.md) |
| `Gameplay.h` | `Random`, `Timer`, `KeyRepeat`, `Motion` | [Recipes](../make/recipes.md), [Timers and events](../make/timers-events.md), [Gameplay math](../make/gameplay-math.md) |
| `Value.h` | `AssetHandle` and the value traits | [Script fields](../make/script-fields.md) |
| `Script.h` | `Script`, `ScriptClassBuilder` and the field macros | [The script loop](../make/script-loop.md), [Script fields](../make/script-fields.md) |

The helpers of `Gameplay.h` live in the module and not in the engine. [The ABI and the SDK](../scripting/abi-sdk.md) says why. The same page explains how the SDK turns the virtual callbacks into the C calls of the next table.

## The script base class and its callbacks

Your script class inherits `Script`. Each callback is a virtual function with an empty body, so you write only the ones you need. The table gives the order of `StrataScriptClassDesc` and when the engine calls each one. [The script loop](../make/script-loop.md) teaches where they fall within a frame.

| Callback | Arguments | When it runs |
| --- | --- | --- |
| `OnCreate` | none | After the instance exists and its saved fields are set |
| `OnUpdate` | delta time | Every frame |
| `OnFixedUpdate` | fixed delta time | Once for each fixed step of the simulation |
| `OnLateUpdate` | delta time | Every frame, after the fixed steps |
| `OnDestroy` | none | When the entity is destroyed, the script is removed or the scene stops playing |
| `OnReload` | none | After hot reload, instead of `OnCreate`; fields are already restored |
| `OnCollisionEnter` | `Collision` | After a fixed step in which two bodies began touching |
| `OnCollisionExit` | `Collision` | After a fixed step in which they parted, or one left the simulation |
| `OnTriggerEnter` | `Collision` | Like `OnCollisionEnter`, where one of the bodies is a trigger |
| `OnTriggerExit` | `Collision` | Like `OnCollisionExit`, where one of the bodies is a trigger |
| `OnAnimationEvent` | event name | When the playhead of the animator's current state passes a named event |
| `OnUIClick` | widget entity | When the player clicks a button |
| `OnUIValueChanged` | widget entity, new value | When a slider or toggle changes (a toggle gives 0 or 1) |
| `OnUIFocusChanged` | widget entity, focused | When a selectable gains or loses the focus |
| `OnUISubmit` | widget entity | When the player submits the text of an input field |

`GetEntity` returns the entity the script is attached to, and `GetTransform` returns that entity's transform. Both are in the generated `Script` section above. The collision and animation callbacks were appended after the first set of the ABI, and the UI callbacks after them. The engine reads such a callback only when the `StructSize` of the class record covers it.

## Script fields

A field is a public data member that the editor shows, the scene saves and hot reload keeps. Two macros declare them, and both are in the generated macro table. Use `ST_SCRIPT_CLASS(Type)` once in a `.cpp` file to register the class, and one `ST_SCRIPT_FIELD(Member)` inside it for each field.

A field has one of ten types, the ones that `c_IsFieldType` in `Script.h` accepts: `bool`, `int32_t`, `float`, `glm::vec2`, `glm::vec3`, `glm::vec4`, `glm::quat`, `std::string`, `Entity` and `AssetHandle`. Any other type fails to compile, with a `static_assert` whose message lists the types it accepts. The table shows which C value type carries each one across the ABI.

| Field type | Value type in the table |
| --- | --- |
| `bool` | `StrataScriptValueType_Bool` |
| `int32_t` | `StrataScriptValueType_Int` |
| `float` | `StrataScriptValueType_Float` |
| `glm::vec2` | `StrataScriptValueType_Vec2` |
| `glm::vec3` | `StrataScriptValueType_Vec3` |
| `glm::vec4` | `StrataScriptValueType_Vec4` |
| `glm::quat` | `StrataScriptValueType_Quat` |
| `std::string` | `StrataScriptValueType_String` |
| `Entity` | `StrataScriptValueType_Entity` |
| `AssetHandle` | `StrataScriptValueType_Asset` |

## The C types a module sees

These tables are hand-written from `StrataScriptCore/Include/StrataScript/ScriptABI.h`, because the generator does not read types. Only plain data crosses the boundary: strings are a pointer and a size in UTF-8, entities and assets are 64-bit numbers, and math is arrays of floats. Quaternions are always in the order x, y, z, w.

| Name | What it is |
| --- | --- |
| `StrataScriptContext` | An opaque handle to a scene, passed to every scene-related host function |
| `StrataScriptInstance` | An opaque pointer to a script instance that the module made |
| `StrataScriptEntityID` | A 64-bit entity identifier; 0 is the null entity |
| `StrataScriptAssetHandle` | A 64-bit asset identifier; 0 is the null asset |
| `StrataScriptString` | `Data` and `Size`; not necessarily ended by a zero byte, and `Data` may be null when `Size` is 0 |
| `StrataScriptValue` | A `Type` and a union of a flag, an integer, float, a vector of four floats, an identifier or a string |
| `StrataScriptTransform` | Translation (3 floats), rotation (a unit quaternion) and scale (3 floats) |
| `StrataScriptFieldDesc` | One field of a class: `StructSize`, `Type`, `Name` and `DefaultValue` |
| `StrataScriptClassDesc` | One script class: its name, its fields and its callbacks; starts with `StructSize` |
| `StrataScriptModuleAPI` | What the module returns from loading: its name, the class records and `Unload`; starts with `StructSize` |

A call into the module returns a `StrataScriptResult`, stored as 32 bits.

| Enum | Values |
| --- | --- |
| `StrataScriptResult` | `Ok` 0, `Exception` 1 (the message went to `ReportException`), `ABIMismatch` 2, `InvalidArgument` 3 |
| `StrataScriptLogLevel` | `Trace` 0, `Info` 1, `Warn` 2, `Error` 3 |
| `StrataScriptValueType` | `Empty` 0, then `Bool`, `Int`, `Float`, `Vec2`, `Vec3`, `Vec4`, `Quat`, `String`, `Entity`, `Asset` |
| `StrataScriptTransformPart` | Bit mask: `Translation` 1, `Rotation` 2, `Scale` 4, `All` 7 |
| `StrataScriptGroundState` | `OnGround` 0, `OnSteepGround` 1, `NotSupported` 2, `InAir` 3 |
| `StrataScriptCursorMode` | `Normal` 0, `Hidden` 1, `Locked` 2 |
| `StrataScriptWindowMode` | `Windowed` 0, `Fullscreen` 1, `Borderless` 2 |
| `StrataScriptUIAction` | `Submit` 0, `Cancel` 1, `Up` 2, `Down` 3, `Left` 4, `Right` 5 |
| `StrataScriptInputDevices` | Bit mask: `Keyboard` 1, `Mouse` 2, `Gamepad` 4 |
| `StrataScriptGraphicsOptionType` | `Bool` 0, `Int` 1, `Float` 2, `Choice` 3 |
| `StrataScriptGraphicsOptionSource` | `Project` 0, `Player` 1, `CommandLine` 2 |

:term[Structs]{id=struct} come in two kinds. A **frozen** struct has a layout fixed for the ABI version. Modules pass arrays or buffers of it for the engine to fill, and a member added later would make the engine write past the end of an older module's buffer. A **sized** struct starts with `StructSize`, so each side can tell whether the other knows a later member. A static assertion in the header checks each frozen size.

| Struct | Kind | Size in bytes | What it holds |
| --- | --- | --- | --- |
| `StrataScriptRaycastHit` | Frozen | 40 | The entity, the world point, the surface normal and the distance of a ray hit |
| `StrataScriptCharacterState` | Frozen | 56 | Ground state, ground entity, ground normal and velocity, and the controller's own velocity |
| `StrataScriptCollision` | Sized | 40 | The other entity, the contact point and the normal, in world space |
| `StrataScriptGraphicsOptionInfo` | Sized | 80 on 64-bit systems | One graphics option: type, name, title, description, range, number of choices and source |

The first sizes hold for the first version of each struct. Read a member of a sized struct only after `ST_SCRIPT_HAS_MEMBER` says its `StructSize` covers it.

## The macros of the ABI header

`ScriptABI.h` defines a few more macros than the generated table shows, because they belong to the C header and not to the SDK classes. Game code written against the SDK never uses them; a module written against the C ABI directly does.

| Macro | Meaning |
| --- | --- |
| `ST_SCRIPT_ABI_VERSION` | The ABI version, 1 at the pin |
| `ST_SCRIPT_EXPORT` | Marks a function the module exports: a dynamic library export on Windows, default visibility elsewhere |
| `ST_SCRIPT_GET_ABI_VERSION_SYMBOL` | The name of the first entry point, `StrataScript_GetABIVersion` |
| `ST_SCRIPT_LOAD_SYMBOL` | The name of the second entry point, `StrataScript_Load` |
| `ST_SCRIPT_HAS_MEMBER(type, pointer, member)` | True when the struct behind the pointer is large enough to hold the member |
| `ST_SCRIPT_ABORT_EXCEPTION_CODE` | On Windows, the structured exception a module raises when its code calls `abort`, so that the engine reports a crash of one call |

A module built through CMake gets all of this from the function `strata_add_script_module(<target>)`. Its options are in the next table, and [Building and shipping a script module](../make/script-builds.md) teaches its use. The file is `<name>.dll` on Windows, `<name>.so` on Linux and `<name>.dylib` on macOS, and the table comes from `StrataScriptCore/CMake/StrataScriptModule.cmake`.

| Option | Meaning |
| --- | --- |
| `SOURCE_DIR` | Every `.cpp`, `.h` and `.hpp` file below the folder belongs to the module, except folders whose names start with a dot and build trees |
| `SOURCES` | Additional :term[source files]{id=source-file} |
| `OUTPUT_NAME` | The file name without its extension; the default is the target name |
| `OUTPUT_DIRECTORY` | The output folder; a multi-configuration generator appends the configuration |
| `NO_SDK_ENTRY` | The sources define the two entry points themselves, written against the C ABI and not the SDK |

The function builds the module with debug information in every configuration, so that a breakpoint in a script binds in a Release build too. With MSVC the information goes into a program database. With GCC and Clang it stays in the module, or on macOS in the object files that the module names; before 0.8.0 these compilers wrote none in Release and Dist.

## Three notes

**Failure values.** The engine that runs a game can be older than the SDK the game was built with. A host function appended after the first set of its ABI version is missing from an older engine. Before every such call the SDK checks the host table with `ST_SCRIPT_DETAIL_HOST_WITH`. When the engine lacks the member, the SDK function does nothing and returns its failure value: `false`, zero, an empty string or an empty optional.

**The ABI version.** `ST_SCRIPT_ABI_VERSION` stays 1 while functions are only appended. The engine refuses a module built against another version. A changed signature or layout, or a removed or moved member, bumps it. Every module exports the two entry points of the macro table above.

[The ABI and the SDK](../scripting/abi-sdk.md) teaches the rules in full.

**The engine's list.** The macro `ST_SCRIPT_HOST_FUNCTIONS` is the engine's own list of the host functions, in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`; it is not part of the SDK. A static assertion there fails the engine build when the list misses a member of `StrataScriptHostAPI` or lists one out of order. [The host API](../scripting/host-api.md) shows how the engine implements a host function, and [Adding a host function](../scripting/tutorial-host-function.md) walks through adding one.

For the history of releases see [the release history](../appendix/history.md).

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/`: the SDK headers; each class above is declared in the header named in its row.
- `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the C table `StrataScriptHostAPI`, the class and module records, the C types and the ABI macros.
- `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`: `ST_SCRIPT_HOST_FUNCTIONS`, the engine's list of host functions.
- `StrataScriptCore/CMake/StrataScriptModule.cmake`: `strata_add_script_module` and its options.
- `StrataTests/src/FeatureTest/SDKReader.cpp`: the reader that parses the SDK headers and their comments for the feature test.
- `StrataTests/src/FeatureTest/SDKCoverageTests.cpp`: the test that fails when an SDK name is not used by a feature script.
