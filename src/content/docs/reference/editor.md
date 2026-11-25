---
id: reference/editor
title: "Editor reference: panels, shortcuts, arguments"
description: "The editor's command-line options, exit codes, panels, menus, shortcuts, chips, status pills, drag payloads and the files it keeps outside a project's assets."
kind: reference
size: M
tracks: []
needs: [editor-ui/shell]
status: final
---

This page lists the editor's surfaces as facts to find: the option you pass at start, the :term[id]{id=id} a panel answers to, the key that runs an action. Each section holds one table with a short introduction that says how to read it and where the subject is taught. The tables that no generator makes are written by hand from the engine's code, and the introduction of each names the files it comes from. Preferences are on [the settings reference](settings.md); the :term[environment variables]{id=environment-variable} that steer automation are on the automation reference.

## Command line

A row is one option of the `StrataEditor` program. The first column is the option, the second the value it takes (empty for a flag), the third what it does. Options that take a value are written `--option value`. An option that the table lacks, a flag given a value, or a value the option refuses ends the start with :term[exit code]{id=exit-code} 3. How the editor program is built is taught on [the editor program](../editor/program.md), and the command scripts that `--commands` runs on [command scripts](../editor/command-scripts.md).

::include{file="options-editor.md"}

### Three ways the editor runs

The options combine into three ways to run the editor. A **window** run is the default: a person works in a window, maximized unless `--windowed` asks for 1600 by 900 or `--window-size` for an exact count of pixels, at least 640 by 360. A **headless** run has no window (`--headless`), and rendering stays available for captures; `--no-gpu` also drops the graphics device and implies headless. A **scripted** run starts with `--commands` and ends when the script has finished (`--quit-after-commands`), at the frame count of `--frames`, or when a client sends `editor.quit`.

The `--window-size` option serves pictures that compare across machines, so it refuses `--headless` and `--no-gpu`, and a display that cannot make that exact size ends the start with code 1. A headless editor needs something that can end it. Without `--frames` it runs until a client tells it to quit, so a headless start whose automation cannot start exits at once with code 1. The values `--help` and `--version` are answered before anything else starts: no log file, no window and no automation.

### Exit codes

A program reports how it ended with an exit code: 0 means success, any other value a failure. Scripts in a continuous integration job and agents read the code, so the editor sets it with care. A later success never lowers a code that was set earlier.

| Code | When the editor ends with it |
| --- | --- |
| 0 | A normal close, `--help` or `--version` |
| 1 | The command script cannot be read, or it finished with a failed command |
| 1 | The script has not finished at the last frame of `--frames`, or when `editor.quit` runs |
| 1 | A screenshot asked for by `--screenshot` could not be saved |
| 1 | A headless editor without `--frames` could not start its automation |
| 1 | The window could not be opened, or the display could not make the window of `--window-size` at exactly that size |
| 1 | An exception left a frame (thrown by third-party code), unless the run had failed before |
| 3 | An unknown option, a flag given a value, an option without its value, or a value it refuses, such as `--window-size` beside `--headless` (`c_UsageExitCode`) |
| 130 | An interrupt (**Ctrl+C**, a terminate signal), unless the run had failed before |

## Panels

A **panel** is a window of the editor that can be docked beside others; how the shell draws, docks and registers them is taught on [the editor shell](../editor-ui/shell.md). The table lists the built-in panels in the order the editor registers them, which is the order it draws them. It is written by hand from `EditorLayer::RegisterBuiltinPanels`, the `EditorPanels` ids in `EditorLayer.h` and `BuildDefaultLayout`.

The columns are the columns of `EditorPanelDescriptor`. **Id** is what `editor.showPanel` takes and the key of the panel's open state in the layout file; `Scene` also works there for `Viewport`. **Menu path** is the menu inside **View** that holds the panel's toggle: it is empty for every built-in panel, so all of them sit directly in **View**.

**Opens** says whether the panel is open in a new layout. **Docks** is where the default layout puts it. The launcher panel has no **View** item, and `editor.showPanel` refuses it.

| Id | Title | Icon | Menu path | Opens | Docks |
| --- | --- | --- | --- | --- | --- |
| `Viewport` | Scene | `Box` | | yes | center |
| `Game` | Game | `Gamepad2` | | yes | center, behind the Scene tab |
| `Hierarchy` | Hierarchy | `ListTree` | | yes | left |
| `Inspector` | Inspector | `SlidersHorizontal` | | yes | right |
| `AssetInspector` | Asset | `FileBox` | | yes | right, beside the Inspector |
| `Console` | Console | `Terminal` | | yes | bottom |
| `Problems` | Problems | `CircleAlert` | | yes | bottom |
| `ContentBrowser` | Content Browser | `FolderOpen` | | yes | bottom, the first tab |
| `Welcome` | Welcome | `House` | | launcher | no dock: it replaces the :term[dock space]{id=dock-space} while no project is open |
| `Streaming` | Streaming | `HardDrive` | | no | bottom |
| `Performance` | Performance | `ChartColumnStacked` | | no | bottom |
| `Activity` | Activity | `History` | | no | bottom |
| `ProjectSettings` | Project Settings | `Settings2` | | no | center, with the views |

The default layout gives the Hierarchy 15 % of the width, at least 16 text heights and at most 30 %. The right column gets 20 % of the width, at least 18 text heights, and the bottom area 22 % of the height. The editor builds it again when the saved layout has another version (`c_LayoutVersion`) or when you choose **View ▸ Reset Layout**. In a layout saved before a panel existed, the editor docks that panel beside the Console, and the Project Settings beside the Scene view. The panels are taught as instruments on [the instrument panels](../editor-ui/instrument-panels.md).

## Menus

The menu bar is drawn by `EditorLayer::DrawMenuBar`. Each row is one item, with the shortcut shown beside it. Without a project open, the launcher shows only **File** and **Help**, and the project items of **File** are hidden. An item that cannot run now is drawn disabled: most of them while the scene plays.

| Menu | Items |
| --- | --- |
| **File** | **New Project...**, **Open Project...**, **Open Recent**, **Open Sample** |
| **File** | **Close Project**, **Show Launcher** (enabled only when no project is open) |
| **File** | **New Scene**, **Open Scene...** (**Ctrl+O**), **Save Scene** (**Ctrl+S**), **Save Scene As...** (**Ctrl+Shift+S**) |
| **File** | **Recover Unsaved Changes...**, **Set as Start Scene** |
| **File** | **Export Game...**, **Project Settings...** |
| **File** | **Preferences...**, **Exit** |
| **Edit** | **Undo** and **Redo**, each followed by the name of its step (**Ctrl+Z**, **Ctrl+Y**) |
| **Edit** | **Cut** (**Ctrl+X**), **Copy** (**Ctrl+C**), **Paste** (**Ctrl+V**), **Duplicate** (**Ctrl+D**) |
| **Edit** | **Rename** (**F2**), **Delete** (**Del**), **Drop to Ground** (**End**), **Select All** (**Ctrl+A**) |
| **View** | One toggle per docked panel, then **Reset Layout** |
| **Entity** | The create menu of the Hierarchy |
| **Scripts** | **Build Scripts** (**Ctrl+B**), **Reload Scripts**, **Create Script Build** |
| **Scripts** | **New Script...**, **Open Scripts Folder** |
| **Scripts** | **External Editor...**, **Show Problems** |
| **Help** | **About Strata**, and **ImGui Demo** only with `--imgui-demo` |

The context menu of a row of the Hierarchy is no part of the menu bar; its **Make Area Light** runs `lighting.makeAreaLight` on an entity with a mesh, and is disabled while the scene plays. The window commands `editor.showPanel`, `editor.showDialog` and `editor.screenshot` are registered by the editor's user interface (UI), not by its core, and `editor.showPanel` and `editor.screenshot` fail in a run without a window. Their parameters are in [the commands of the editor group](../editor/commands.md).

## Shortcuts

A shortcut has a **route**: the rule that says when the editor hears the key. A global route works whatever has the keyboard focus. A focused route works only while the panel, or a window inside it, has the focus.

A panel-local key is read by the panel's own code. Two rules hold for the global and focused routes. Nothing runs behind a :term[modal]{id=modal} dialog, and nothing that edits runs while the running game has the input, because the game would receive the same key. Who owns the keyboard, and why, is taught on [the Game view](../editor-ui/game-view.md).

The rows come from `EditorLayer::HandleShortcuts`, `EditorActions::HandleSelectionShortcuts` and `ViewportPanel::HandleShortcuts`. The menu items and the shortcuts call the same functions of `EditorActions`, so a menu click and a key press do the same thing.

| Key | Route | What it does | Refused when |
| --- | --- | --- | --- |
| **Ctrl+P** | Global | Starts play, or stops it | A modal dialog is open |
| **Ctrl+Z** | Global | Runs `edit.undo` | Behind a modal, while the game has the input, while the scene plays, or with nothing to undo |
| **Ctrl+Y**, **Ctrl+Shift+Z** | Global | Runs `edit.redo` | The same cases, or with nothing to redo |
| **Ctrl+S** | Global | Saves the scene | Behind a modal or while the game has the input |
| **Ctrl+Shift+S** | Global | Saves the scene under a new name | The same cases |
| **Ctrl+O** | Global | Opens the scene dialog | The same cases |
| **Ctrl+B** | Global | Builds the scripts | The same cases, or while a build runs |
| **Delete** | Focused: Hierarchy, Scene view | Deletes the selection | Behind a modal or while the game has the input |
| **Ctrl+D** | Focused: Hierarchy, Scene view | Duplicates the selection | The same cases |
| **Ctrl+C**, **Ctrl+X**, **Ctrl+V** | Focused: Hierarchy, Scene view | Copies, cuts, pastes the selection as :term[JSON]{id=json} text | The same cases |
| **End** | Focused: Hierarchy, Scene view | Drops the selection to the ground | The same cases |
| **Ctrl+A** | Focused: Scene view | Selects every entity | The same cases |
| **F2** | Focused: Hierarchy, Scene view | Renames the primary selection | The same cases |
| **Q**, **W**, **E**, **R** | Scene view, under the pointer or focused | :term[Gizmo]{id=gizmo-start}: none, move, rotate, scale | Typing, a camera fly, a gizmo drag, or **Ctrl**, **Alt** or the system key held |
| **F** | Scene view | Frames the selection | The same cases, or **Shift** held |
| **Home** | Scene view | Frames every entity | The same cases |
| **F8** | Scene view | Looks through the scene's :term[primary camera]{id=primary-camera} | The same cases |
| Arrows, **Enter**, **F2**, **Delete**, **Backspace** | Content Browser | Moves, opens, renames, deletes, goes to the parent folder | No selection, for the keys that need one |
| **Space** | Performance panel | Pauses or resumes the measurements | The navigation cursor is visible |
| **Shift+F1** | Game view | Gives the keyboard back to the editor without stopping the game | The view is not focused |
| **Escape** | Any drag | Cancels the drag in progress | No drag is active |

The **Ctrl+A** key is handled by the Scene view only, although the Hierarchy handles the other selection keys. The Hierarchy renames also on a double click, and its rename field ends with **Enter** or cancels with **Escape**. The arrow keys of the Content Browser come from :term[ImGui's]{id=dear-imgui} navigation; the code of the panel itself reads the other four keys of its row.

## Scene view chips and status pills

A **chip** is a small toggle or button in the strip above the Scene view's image. A **pill** is a colored label in the status bar, below the panels. Both are written by hand from `ViewportPanel::DrawChips` and the draw functions of `EditorLayer`. The design of the Scene view is taught on [the Scene view](../editor-ui/scene-view.md), and the status bar on [the status bar](../editor-ui/status.md).

The first table gives the chips in the order they are drawn. A toggle chip lights while its setting is on. Two chips lead somewhere: the debug view chip and the quality chip open a choice.

| Chip | What it shows or switches | Where it leads |
| --- | --- | --- |
| **Camera** | :term[Field of view]{id=field-of-view}, clip planes, fly speed and framing | A :term[popup]{id=popup} of camera settings, and the pose skinned characters show while you edit |
| **Grid** | The ground grid | Toggles |
| **Outline** | The outline of the selection | Toggles |
| **Gizmos** | The shapes of lights, cameras and colliders | Toggles |
| **Cells** | The squares of a world's cells around the camera, only while a world is open | Toggles |
| **Stats** | :term[Frame time]{id=frame-time}, draw calls and loading assets | Toggles an :term[overlay]{id=overlay-core} |
| **Preview lighting** | A preview sun and sky for scenes with no light of their own | Toggles; the game stays without light |
| **Game UI** | The game's screen-space UI in the editor view | Toggles |
| **2D** | The selected UI canvas at its reference aspect ratio | Toggles |
| Debug view | The active debug view: **Lit** when none is active, else its own label, such as **Streaming**, **LOD** (level of detail), **AO** (ambient occlusion) or **GI** (global illumination) | A menu of the :value{key="debugViews.count"} views, with a legend of entity counts per color |
| **Quality** | The preset the view draws with: the project's or its own | A menu of **Project**, **Low**, **Medium**, **High** and **Ultra**, and **Graphics Quality...** |
| **Game camera** | The view through the scene's primary camera (**F8**) | Toggles |
| **Animation preview** | The poses that `animation.preview` shows, only while one runs | A click stops the preview |
| **Agent** | The latest command of an automation client and its age, at the right | A click shows it in the Activity panel |

Pills sit in the status bar in the order below. In a narrow window the pills switch to compact texts, and they grow back once the full texts fit with a margin of two text heights. The tooltip of a pill always holds the details.

| Pill | What it shows | Where a click leads |
| --- | --- | --- |
| Play state | Editing, Playing, Simulating or Paused | Nowhere |
| Frame | The time a frame takes to run, :term[frames per second]{id=frame-rate} and jobs in flight, with `idle` while the editor draws less often | The Performance panel |
| Assets | Assets ready and streaming, imports, scene opening progress and the memory of the fullest pool | The Streaming panel |
| Saving | Saves in flight | The Activity panel |
| Physics | Bodies without collision; shown only when a world is at its growth limit | The Streaming panel, physics section |
| Automation | The port and the connected agents, or that automation is off or failed | The Console, when it failed |
| Scripts | A build running, a failed build or a crash, or scripts not built, unused or absent | Cancels a running build; opens the Problems panel after a failure or a crash; builds scripts not built yet |
| Holds | The keys a tool holds down in the running game; only while some are held | Releases them all |
| Errors | The count of errors logged since the Console was last viewed; only when above zero | The Console |

## Drag payloads and probe keys

This section is for contributors. A **drag payload** is the named packet that ImGui moves between a drag source and a drop target; a target accepts only the names it knows. The names are `STRATA_ENTITIES` (the :term[universally unique identifiers]{id=uuid} (UUID) of one or more entities of the active scene, in hierarchy order), `STRATA_ASSET` (an :term[asset handle]{id=asset-handle}) and `STRATA_ASSET_FOLDER` (a folder of the Content Browser). They are declared in `StrataEditor/src/UI/PropertyWidgets.h` and `StrataEditor/src/Panels/ContentBrowserPanel.h`.

A **probe key** is the name under which a widget of the editor records its rectangle every frame, so that a UI test can find the widget and click it. The conventions are in `StrataEditor/src/UI/ItemProbe.h`, and the tests that use them are taught on [testing a UI without a screen](../editor-ui/ui-testing.md). Four forms exist, shown here with keys that the code records:

```text
Menu.File.SaveScene          a menu item: Menu.<Menu>.<Item>
Viewport.Grid                a chip: Viewport.<Chip>
Status.Frame                 a pill: Status.<Pill>
Menu.File.Recent.0           a numbered row: <prefix>.<number>
```

A key longer than 40 characters before its number is cut. A widget drawn twice in one frame under one key is marked as a duplicate, which tells a test that the key does not name one widget. A pill also records its color and its text, so a test can check what the person sees.

## Files outside the assets

The editor and the games it plays keep files that are not assets. The first table lists the files of the :term[user data folder]{id=user-data-folder}: `%LOCALAPPDATA%/Strata` on Windows, `$XDG_DATA_HOME/Strata` (default `~/.local/share/Strata`) on Linux and `~/Library/Application Support/Strata` on macOS. The second lists the files of a project's `.strata` folder. Both are written by hand from `Strata/src/Strata/Core/Platform.h`, `Strata/src/Strata/Project/Project.h` and the sources named in the last section.

| Path in the user data folder | Written by | Holds | Moved by |
| --- | --- | --- | --- |
| `Logs/StrataEditor.log` | The editor | The editor's log | Nothing |
| `Preferences.json` | The editor | The person's preferences, for every project | Nothing |
| `EditorSettings.json` | An old editor | Settings of release 0.5.0, read once and imported, never written | Nothing |
| `RecentProjects.json` | The editor | The recent projects of the launcher | `STRATA_RECENT_PROJECTS` |
| `Sessions/` | The editor | The session files that tools use to find a running editor | `STRATA_SESSION_DIR` |
| `Builds/` | The editor | The script builds of projects too deep for their :term[toolchain]{id=build-tools} | `STRATA_SCRIPT_BUILDS_DIR` |
| `<Name>/Logs/Game.log` | An exported game | The game's log, in the folder named for the game | Nothing |
| `<Name>/Saves/` | An exported game | The game's save files and the players' `GraphicsOptions.json` and `InputBindings.json` | Nothing |

| Path in `<project>/.strata/` | Written by | Holds |
| --- | --- | --- |
| `Cache/` | The asset pipeline | The :term[cooked assets]{id=cooked-asset}, and `ImportRecords.log`, what each asset's last import produced |
| `Scripts/Build/`, `Scripts/Bin/` | The script build | The :term[CMake]{id=cmake} build tree, and the module that the editor loads |
| `Saves/` | A game that plays in the editor | The game's save files, and the players' `GraphicsOptions.json` and `InputBindings.json` |
| `Trash/` | The editor | Deleted assets, kept for 30 days, and removed when the project opens after that |
| `Recovery/` | The editor | The changes of the scene that are not saved yet, in `.strecovery` files |
| `Bake/` | The lighting bake | Staging folders of a bake in progress |
| `Thumbnails/`, `Thumbnail.png` | The editor | Asset thumbnails, and the project's picture in the launcher |
| `EditorSession.json` | The editor | A pointer for tools started in the project: process id and project path, never the port or the token |
| `EditorViewport.json` | The editor | The Scene view's camera and chips, saved when the project closes |

A third, private folder per user, that of `Platform::GetUserRuntimeDirectory`, keeps files that matter only while a program runs, such as private copies of the libraries it loads; `STRATA_RUNTIME_DIR` moves it. How these folders are taught: [projects](../editor/projects.md) for the folder layout, [recovery](../editor/recovery.md) for `Recovery/` and [the trash](../editor/trash-references.md) for `Trash/`.

## Where it lives in Strata

- `StrataEditor/src/EditorApplication.cpp`: the `c_Arguments` table, the value checks, `--help`, `--version`, the exit code of a bad argument and the exact size of `--window-size`.
- `Strata/src/Strata/Core/CommandLineOptions.h`: `c_UsageExitCode`, the exit code 3.
- `Strata/src/Strata/Core/Application.h`: `c_InterruptedExitCode`, the exit code 130, and `c_UnhandledExceptionExitCode`, the exit code 1 of an exception.
- `StrataEditor/src/EditorLayer.cpp`: the built-in panels, the menu bar, the global shortcuts, the status bar and the exit codes of a scripted run.
- `StrataEditor/src/UI/EditorActions.cpp`: the selection actions that menus and focused shortcuts share.
- `StrataEditor/src/Panels/ViewportPanel.cpp`: the chips and the Scene view's keys.
- `StrataEditor/src/Panels/SceneHierarchyPanel.cpp`: the context menu of a row, with **Make Area Light**.
- `StrataEditor/src/UI/EditorPanelRegistry.h`: `EditorPanelDescriptor`, the columns of the panels table.
- `StrataEditor/src/UI/ItemProbe.h`: the probe keys.
- `StrataEditor/src/Editor/RecentProjects.cpp`, `StrataEditor/src/Editor/EditorPreferences.cpp` and `StrataEditor/src/Editor/ScriptBuild.cpp`: the files of the user data folder and the variables that move them.
- `StrataEditor/src/Editor/EditorContext.cpp`: the Trash, Thumbnails and `EditorViewport.json` names.
- `Strata/src/Strata/Network/EditorSession.cpp`: `Sessions/` and `EditorSession.json`.
- `Strata/src/Strata/Core/SaveFiles.cpp`: the `Saves` folder of an exported game.
- `StrataRuntime/src/RuntimeApplication.cpp`: `Logs/Game.log` of an exported game.
