---
id: reference/commands
title: "The command catalogue"
description: "Every command the editor registers, with its kind, flags, toolsets, parameters and JSON Schema, and the value forms its parameters accept."
kind: reference
size: XL
tracks: []
needs: [editor/commands, basics/data-formats]
status: final
---

You hold a command name, from a log, a script or an agent, and you want to know what it does, what it needs and what it returns. This page lists every command that the editor registers. A dump of the `editor.commands` command, taken from an editor started with `--no-gpu`, gives the names, descriptions, schemas, kinds and flags, so the count is :value{key="commands.count"} and the page never types it by hand. How the registry checks and runs a command is taught in [Editor commands](../editor/commands.md).

## How to read an entry

Each command has a heading with its name, written `<group>.<action>`, such as `entity.create`. Under it stands the description, shown as the engine wrote it. The engine writes descriptions for agents, so they name results, limits and failures in a few dense sentences.

Below the description, one line gives the facts that the registry stores:

- **Kind**: `Edit`, `Query` or `Session`. An `Edit` command changes the project or the scene and records one undo step; see [Undo and redo](../editor/undo.md). A `Query` command changes nothing, so a replay may run it again at any time. A `Session` command changes the editor's own state, such as the selection or a panel, and records no undo step. The [command journal](../editor/journal.md) uses the kind to decide what a replay does with each entry.
- **Results**: `Content` or `Session`. A `Session` result names things that live only in this editor run, such as a running game's entities. A replay never binds identifiers from such a result.
- **MCP toolsets**: the toolsets of the Model Context Protocol (MCP) that offer the command as a tool. Every command is a tool of its own group's toolset, and some are also in `core`; see [MCP](../automation/mcp.md).
- **Answers later (MayDefer)**: whether the command may take several frames to finish. Such a command answers when its work is done; see [Deferred commands](../editor/deferred-commands.md).
- **Waits for the asset scan**: whether the command waits for the background scan of the project's assets. `Edit` commands wait for it too, because the registry defers them.
- **Registered at**: the :term[source file]{id=source-file} and line of the registration.

A parameter table follows, with one row for each parameter: its name, its type, whether it is required, its default and its description. The parameter's :term[JSON Schema]{id=json-schema} stands in a closed block under the table. A command without parameters says so.

The engine has no schema for results. The result is whatever the description says, and where a tutorial run recorded one, a closed block shows an example result. Identifiers in an example are replaced by an ellipsis, because every run makes new ones.

## How values are written

Parameters follow a few forms of value, and no single description repeats them. The facts below come from the reflection code that reads JSON values into properties and from the command helper that finds assets; [Data formats](../basics/data-formats.md) teaches the JSON itself. Property names in `component.set` and `entity.create` are matched without regard to case.

| Form | How you write it | Example |
| --- | --- | --- |
| Identifier of an entity or an asset | A string of 16 :term[hexadecimal]{id=hexadecimal} digits | `"00000000000000AB"` |
| No entity, no asset | `null`, or an empty string | `null` |
| `Bool` | `true` or `false`; an :term[integer]{id=integer} counts as true unless it is 0 | `true` |
| `Int` | A whole number within 32 bits; a number with a zero fraction passes | `12` |
| `UInt` | A whole number from 0 up to 32 bits | `3` |
| Float | Any finite number within the range of a 32-bit float | `0.5` |
| Vector | An array of numbers, an object with the keys `x`, `y`, `z`, `w`, or one number, which every component takes | `[0, 1, 0]` |
| Color | An array or object like a vector; the alpha of a Color4 may be omitted and then is 1 | `[1, 0.5, 0, 1]` |
| Rotation | Three numbers for Euler degrees, as pitch, yaw, roll; four numbers for a quaternion `[x, y, z, w]`; or an object with an `Euler` key | `{"Euler": [0, 90, 0]}` |
| Enum | The name of an option; a plain integer is also read | `"Perspective"` |
| String | A string | `"Crate"` |
| Asset or Entity property | An identifier string, an integer or `null` | `"0000000000000010"` |
| Asset in a command parameter | An identifier, a path relative to the project's `Assets/` folder, or `Builtin/<Name>` | `"Materials/Red.stmat"` |

A value outside a property's range is refused as invalid parameters, and nothing changes: the engine never clamps it. A rotation is read back as a quaternion, whatever form you wrote. The ranges of every property are on [the components reference](components.md).

The engine itself provides nine assets in every project, with fixed handles, so a command can name them without a file. The handle `0x01` is the number 1 written in hexadecimal. Handles from 1 to 255 are reserved for them; see [Handles and meta files](../assets/handles-meta.md).

| Name | Type | Handle | Written as a reference |
| --- | --- | --- | --- |
| Cube | Mesh | `0x01` | `Builtin/Cube` |
| Sphere | Mesh | `0x02` | `Builtin/Sphere` |
| Plane | Mesh | `0x03` | `Builtin/Plane` |
| Quad | Mesh | `0x04` | `Builtin/Quad` |
| Cylinder | Mesh | `0x05` | `Builtin/Cylinder` |
| Capsule | Mesh | `0x06` | `Builtin/Capsule` |
| Cone | Mesh | `0x07` | `Builtin/Cone` |
| `Torus` | Mesh | `0x08` | `Builtin/Torus` |
| `DefaultMaterial` | Material | `0x10` | `Builtin/DefaultMaterial` |

## The step of a command script

A command script is a :term[JSON array]{id=json-array} of steps, and `editor.batch` takes the same steps. Every sample project keeps its regression script in this form. [Command scripts](../editor/command-scripts.md) teaches how to write one, and [Automated playtests](../make/automated-playtests.md) shows scripts that play a game. Only `command` is required in a step.

| Key | What it holds | Limit |
| --- | --- | --- |
| `command` | The name of the command to run | Must be registered |
| `parameters` | The command's parameters as an object | Checked against the schema before the step runs |
| `expect` | An object that maps a JSON pointer, a path such as `/id` that names one value inside the result, to a condition: `equals`, `min` or `max`, alone or together | A pointer of `""` is the whole result; a result that fails a condition fails the step |
| `bind` | An object that gives a name to a value of the result: `{"crate": "/id"}` | A later step must not use a name that no earlier step binds |
| `{"$ref": "crate"}` | Stands in a later step's parameters, at any depth, and is replaced by the bound value; `"pointer"` picks a part, as in `{"$ref": "crate", "pointer": "/entities/0"}` | A step whose binding has no value fails without running |
| `until` | An object with `steps`, `seconds` or both; the step repeats once per frame until its `expect` holds | At most 10,000,000 steps; seconds default to 300 and may not pass a day; the step must be a `Query` with an `expect` |

A step with `until` waits for the game, so `editor.batch` refuses it: a batch must finish within one frame. A batch holds at most 1,000 steps, and it refuses commands that may take frames, such as loads, builds, captures and `play.step`.

## The groups

The table lists the groups in the order in which the sections below follow. The toolset column names the toolsets that offer the group's commands; a command may also appear in `core`. The last column names the page that teaches what the group does. The `ui` group works on the game's user interface (UI).

| Group | Toolsets | Taught on |
| --- | --- | --- |
| `scene` | `scene`, `core` | [Scenes and sub-scenes](../world/sub-scenes.md) |
| `entity` | `scene`, `core` | [The scene graph](../world/scene-graph.md) |
| `component` | `scene`, `core` | [Reflection](../world/reflection.md) |
| `prefab` | `scene`, `core` | [Prefab instances](../editor/prefab-instances.md) |
| `asset` | `assets`, `streaming`, `scene`, `core` | [What an asset is](../assets/what-is-an-asset.md) |
| `material` | `assets`, `core` | [Materials](../light/materials.md) |
| `project` | `assets`, `settings`, `core` | [Projects](../editor/projects.md) |
| `edit` | `scene` | [Undo and redo](../editor/undo.md) |
| `editor` | `editor`, `perf`, `core` | [The editor program](../editor/program.md) |
| `selection` | `scene` | [The editor's status](../editor-ui/status.md) |
| `log` | `editor`, `core` | [Debugging](../core/debugging.md) |
| `play` | `play`, `core` | [Play mode](../editor/play-mode.md) |
| `input` | `play`, `core` | [Simulated input](../input/simulated.md) |
| `camera` | `viewport` | [Camera and viewport](../editor/camera-viewport.md) |
| `viewport` | `viewport`, `core` | [Camera and viewport](../editor/camera-viewport.md) |
| `script` | `scripts`, `core` | [Script builds](../make/script-builds.md) |
| `animation` | `animation` | [Animation in the editor](../animation/editor.md) |
| `world` | `world` | [Worlds in the editor](../editor/worlds.md) |
| `physics` | `world` | [Queries](../physics/queries.md) |
| `lighting` | `scene` | [Probes](../indirect/probes.md) |
| `ui` | `ui` | [What game UI does](../ui/what-game-ui-does.md) |
| `audio` | `play` | [The audio engine](../audio/engine.md) |
| `preferences` | `settings` | [Settings windows](../editor-ui/settings-windows.md) |
| `inputActions` | `settings` | [Input actions](../input/actions.md) |
| `graphics` | `settings` | [Quality settings](../image/quality-settings.md) |

### The toolsets

The :value{key="toolsets.count"} toolsets are listed first: each holds the commands of one kind of work, and an agent chooses which toolsets to load.

::include{file="commands-toolsets.md"}

## The scene commands

These commands open, save, recover and describe the edited scene, and load a second scene next to a running game. [Scenes and sub-scenes](../world/sub-scenes.md) teaches what a scene holds.

::include{file="commands-scene.md"}

## The entity commands

These commands create, copy, find, rename and move entities, and each one is a single undo step, also for many entities at once. [The scene graph](../world/scene-graph.md) teaches the entities and the hierarchy they edit.

::include{file="commands-entity.md"}

## The component commands

These commands list the registered components and add, remove, read and write them through reflection. [Reflection](../world/reflection.md) teaches how a property is described, and [the components reference](components.md) lists them all.

::include{file="commands-component.md"}

## The prefab commands

These commands make a prefab from an entity, place instances, and apply, revert or unpack their changes. [Prefab instances](../editor/prefab-instances.md) teaches how an instance stays linked to its prefab.

::include{file="commands-prefab.md"}

## The asset commands

These commands list the asset types the editor knows, list and import the project's assets, move and delete them through the trash, find who uses them, and place them in the scene. [What an asset is](../assets/what-is-an-asset.md) teaches the subject, and each command is named again on the page of its own topic, such as [importing](../assets/importing.md), [references](../assets/references.md) and [residency](../assets/residency.md), where `asset.stats` and `asset.setBudget` belong.

::include{file="commands-asset.md"}

## The material commands

These commands read, create and change material assets, and each change is an undo step that saves its own file. [Materials](../light/materials.md) teaches what the settings mean.

::include{file="commands-material.md"}

## The project commands

These commands create, open and close projects, list the templates and samples, edit the project's settings, and export the game. [Projects](../editor/projects.md) teaches how a project is made, opened and closed, [Exporting a game](../make/export.md) the export commands, and [the launcher](../editor-ui/launcher-dialogs.md) the templates and samples.

::include{file="commands-project.md"}

## The edit commands

These commands undo, redo and list the undo history. [Undo and redo](../editor/undo.md) teaches what a step records.

::include{file="commands-edit.md"}

## The editor commands

These commands report the editor's state and activity, list and run commands, wait, profile, take a screenshot of the window and run batches. [The editor program](../editor/program.md) and [the journal](../editor/journal.md) teach the session they describe.

The three commands `editor.showPanel`, `editor.showDialog` and `editor.screenshot` are not registered by the :term[editor core]{id=editor-core}. The editor's window registers them, in the class `EditorLayer`, and they open a panel or a dialog for the person at the screen, or take a picture of what that person sees. An editor started with `--no-gpu` or without a window still lists them, but they fail there, because no window exists to show anything. The count above includes all three, and a count taken from the core alone is three lower.

::include{file="commands-editor.md"}

## The selection commands

These commands read and set the selected entities, which belong to the editor's session. [The editor's status](../editor-ui/status.md) teaches how the selection shows.

::include{file="commands-selection.md"}

## The log command

This command reads the editor's log from a given sequence number. [Debugging](../core/debugging.md) teaches how the engine logs.

::include{file="commands-log.md"}

## The play commands

These commands start, simulate, pause, step and stop the game, and report its state. [Play mode](../editor/play-mode.md) teaches the modes, and [stepping a paused game](../editor/stepping.md) teaches `play.step`.

::include{file="commands-play.md"}

## The input commands

These commands press keys and buttons, move the mouse and gamepad, and run timed sequences, all counted in :term[fixed steps]{id=fixed-step}. [Simulated input](../input/simulated.md) teaches how the engine feeds a game input that no device made.

::include{file="commands-input.md"}

## The camera commands

These commands read, set and aim the editor's own camera, with no undo step. [Camera and viewport](../editor/camera-viewport.md) teaches how it moves.

::include{file="commands-camera.md"}

## The viewport commands

These commands read and change the view settings and capture the viewport as an image, and one capture may switch :term[renderer]{id=renderer} options for itself alone. [Camera and viewport](../editor/camera-viewport.md) teaches them.

::include{file="commands-viewport.md"}

## The script commands

These commands build, load, create and list the game's script classes, and attach them to entities and set their fields. [Script builds](../make/script-builds.md) teaches the build, and [the script system](../scripting/script-system.md) the loading.

::include{file="commands-script.md"}

## The animation commands

These commands create animation controllers, assign them and preview clips while editing. [Animation in the editor](../animation/editor.md) teaches them.

::include{file="commands-animation.md"}

## The world commands

These commands create, cook, inspect and edit worlds and their cells. [Worlds in the editor](../editor/worlds.md) teaches the editing, and the streaming that follows is the world :term[runtime]{id=runtime}, which [The runtime](../worlds/runtime.md) teaches.

::include{file="commands-world.md"}

## The physics commands

These two commands report physics statistics and switch on the detailed ones. [Queries](../physics/queries.md) and [tuning](../physics/tuning.md) teach what physics measures.

::include{file="commands-physics.md"}

## The lighting commands

These commands apply a sky preset, bake light probes, extract the sun from a sky and make an emissive panel a real light. [Probes](../indirect/probes.md) teaches what a bake stores.

::include{file="commands-lighting.md"}

## The ui commands

These commands create canvases and widgets, lay them out and test which element a point hits. [What game UI does](../ui/what-game-ui-does.md) teaches the module.

::include{file="commands-ui.md"}

## The audio command

This command reports what the running game plays. [The audio engine](../audio/engine.md) teaches the voices it lists.

::include{file="commands-audio.md"}

## The preferences commands

These commands read, set and save the person's preferences, which belong to the editor's session and not to the project. [Settings windows](../editor-ui/settings-windows.md) teaches the windows that show them.

::include{file="commands-preferences.md"}

## The input action commands

These commands set the project's input actions and maps, and reset the players' own bindings. [Input actions](../input/actions.md) teaches how a game reads controls through actions.

::include{file="commands-inputactions.md"}

## The graphics command

This command resets the players' graphics options during play. [Quality settings](../image/quality-settings.md) teaches the options.

::include{file="commands-graphics.md"}

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorCommands.cpp`: the registry, its checks and `editor.commands`.
- `StrataEditor/src/Editor/EditorSceneCommands.cpp`, `EditorPrefabCommands.cpp`, `EditorAssetCommands.cpp`, `EditorProjectSettingsCommands.cpp` and the other `StrataEditor/src/Editor/Editor*Commands.cpp` files: the commands of each group.
- `StrataEditor/src/Editor/Commands/`: the commands of entities and components, play, placement, audio and batches.
- `StrataEditor/src/EditorLayer.cpp`: the registration of `editor.showPanel`, `editor.showDialog` and `editor.screenshot`.
- `StrataEditor/src/Editor/CommandUtils.cpp`: the lookup of assets by handle, path or built-in name.
- `StrataEditor/src/Editor/EditorCommandRunner.h`: the keys of a script step and their limits.
- `StrataEditor/src/Editor/Commands/BatchCommands.cpp`: the limit of a batch.
- `Strata/src/Strata/Reflection/PropertyJson.cpp`: how each property type reads its JSON value.
- `Strata/src/Strata/Asset/BuiltinAssets.cpp`: the nine built-in assets.
- `StrataTests/src/Editor/CommandJournalTests.cpp`: the lists that pin the kind and flags of every command.
- `StrataCLI/src/CLI/McpToolsets.cpp`: the toolsets and which command each one offers.
