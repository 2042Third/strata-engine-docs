---
id: reference/settings
title: "Project settings and preferences"
description: "Every settings section a project or the editor can hold, with each field, its default and its range, as the engine describes it."
kind: reference
size: L
tracks: []
needs: [world/projects-settings]
status: final
---

A **settings section** is a named block of values that one part of the engine owns, with a description of which values are allowed. This page lists every section of the engine at the pin: :value{key="settings.count"} sections that belong to a project and :value{key="preferences.count"} that belong to the person who runs the editor. [Projects and settings](../world/projects-settings.md) teaches what a section is, how its value is checked and how a scene reads it. This page is for a reader who has a section id, such as one found in a project file, and needs its fields.

Read a section like this. Its id has the form `<Module>.<Name>`, and the module is the part of the engine that registered it; its scope is **Project** or **User**. A Project section is stored in the project file and ships with the game. A User section is one of the person's preferences: it holds for every project and is never shipped. The title and category are the words the settings windows show, and the version is the number of its stored layout.

A simple section has a table with one row per field: its name, its title, its type, its default and a description that lists the allowed range or options. A :term[complex section]{id=complex-section} holds data too large for a field table, such as lists and maps. Its table shows the top-level keys, followed by its default value and its JSON schema (the description of every allowed shape) in closed blocks. Each table uses the `default` the schema states for a field and never a stored value, so nothing of the machine that made the tables appears here.

## What each section is for

The table below names, for each section, the page that teaches its subject and the page of the settings window that edits it. A section without its own page appears in the generic page, which draws one row per field from the schema, as [Settings windows from schemas](../editor-ui/settings-windows.md) explains.

| Section | Scope | Taught in | Edited in the editor by |
| --- | --- | --- | --- |
| `Input.Actions` | Project | [Input actions](../input/actions.md) | its own Input Actions page |
| `Physics.Simulation` | Project | [Tuning physics](../physics/tuning.md) | the generic page |
| `Renderer.Quality` | Project | [Quality settings](../image/quality-settings.md) | its own Graphics Quality page |
| `Scene.CollisionLayers` | Project | [Collision layers](../physics/collision-layers.md) | its own Collision Layers page |
| `Scene.Timing` | Project | [Time](../core/time.md) | the generic page |
| `Editor.ExternalEditor` | User | [Projects, saving, undo and recovery](../make/project-files.md) | its own External Editor page |
| `Editor.FrameRate` | User | [Settings windows from schemas](../editor-ui/settings-windows.md) | the generic page |
| `Editor.Interface` | User | [Settings windows from schemas](../editor-ui/settings-windows.md) | the generic page |

Project sections appear in the Project Settings window, which **File ▸ Project Settings...** opens, and preference sections in the dialog that **Preferences...** opens. `Editor.FrameRate` sets how fast the editor draws its window: some seconds after the last input, it counts as idle and draws fewer :term[frames per second]{id=frame-rate}.

## Project sections

The tables come from `project.settings` on a new project created from the `empty` template. They list the sections in the order the command returns them, which is the order the modules register them. For `Renderer.Quality`, the four values that each preset gives to each quality row are not repeated here, because they stand in the quality table of [the rendering tables](../reference/renderer.md); this page shows only the section's fields. The default value of `Input.Actions` is exactly the reserved map of the user interface (UI), which the table of [Audio and input reference](../reference/audio-input.md) explains row by row.

::include{file="settings.md"}

## Preference sections

These tables come from `preferences.get`, which works without a project. Preferences live in the person's own preferences file, apart from any project, and a game never reads them. `Editor.Interface` holds the interface scale, and the `--ui-scale` command-line option wins over it for its session. When `STRATA_EXTERNAL_EDITOR` is set in the environment, it wins over the command stored in `Editor.ExternalEditor`.

::include{file="preferences.md"}

## Changing a section

Commands change sections; the settings windows call the same ones.

- `project.setSettings` sets one project section to a whole new value, or with `reset: true` back to its default. It is one undo step, and an invalid value changes nothing and names the first bad field.
- `project.setCollisionLayers` sets the names and the matrix of `Scene.CollisionLayers`.
- `inputActions.setMap` and `inputActions.setAction` change the maps and actions of `Input.Actions`; `inputActions.resetPlayerBindings` deletes the bindings that players saved.
- `preferences.set` sets one preference section, or with `reset: true` resets it. It is no undo step and leaves the project alone. `preferences.get` reads the sections and `preferences.save` waits until the file is written.

The project file keeps the keys that are not sections, such as the game's title and the export list, in the table of [the tables of exported games](../reference/worlds-runtime.md).

The value of a section may hold at most 512 KiB of :term[JSON]{id=json}. A field has one of six types. `Bool` is true or false, and `Int` and `Float` are numbers from a minimum to a maximum. `String` is text of a limited length, `Enum` is one of listed options and `Asset` names an asset of one type. For changing settings as a game maker, read [Projects, saving, undo and recovery](../make/project-files.md).

## Where it lives in Strata

- `Strata/src/Strata/Core/SettingsRegistry.h`: the section and field types and the registry that holds the sections.
- `Strata/src/Strata/Core/ProjectSettings.h`: the service that keeps a project's section values.
- `Strata/src/Strata/Input/InputRegistration.cpp`: registers `Input.Actions`, made in `Strata/src/Strata/Input/InputActionSet.cpp`.
- `Strata/src/Strata/Physics/PhysicsRegistration.cpp`: registers `Physics.Simulation`.
- `Strata/src/Strata/Renderer/RendererRegistration.cpp`: registers `Renderer.Quality`.
- `Strata/src/Strata/Scene/SceneRegistration.cpp`: registers `Scene.CollisionLayers` and `Scene.Timing`.
- `StrataEditor/src/Editor/EditorPreferences.cpp`: registers the three `Editor.*` sections.
- `StrataEditor/src/Editor/EditorPreferencesCommands.cpp`: the `preferences.*` commands.
- `StrataEditor/src/UI/SettingsPages.cpp`: the pages of the settings windows.
- `StrataEditor/src/UI/PreferencesDialog.cpp`: the Preferences dialog.
- `StrataEditor/src/Panels/ProjectSettingsPanel.cpp`: the Project Settings window.
- `tools/reference.py`: the dump that makes the two tables, with the routes `settings` and `preferences`.
