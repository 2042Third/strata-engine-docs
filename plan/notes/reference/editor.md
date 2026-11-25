# Notes: reference/editor

## New terms

None proposed. The page bolds route, panel, chip, pill, drag payload, probe key, window/headless/scripted run as local definitions; the clerk may decide whether they are terms.

## Requests

- Names or words: none.
- The page names the automation reference in words, with no link, because `reference/automation` does not exist yet; add the link when it does.

## Hand-written tables

- Panels table: `StrataEditor/src/EditorLayer.cpp` (`RegisterBuiltinPanels`, `BuildDefaultLayout`, `DockNewToolPanels`), `StrataEditor/src/EditorLayer.h` (`EditorPanels`), `StrataEditor/src/UI/EditorPanelRegistry.h`.
- Exit codes: `EditorLayer.cpp` (StartAutomation, UpdateCommandScript, screenshot, frame limit), `Strata/src/Strata/Core/CommandLineOptions.h`, `Strata/src/Strata/Core/Application.h` and `.cpp` (window, exception), `StrataEditor/src/EditorApplication.cpp` (`CheckValues`, `HasRequestedPixels`).
- Menus also: `Panels/SceneHierarchyPanel.cpp` `DrawRowContextMenu` (Make Area Light), named in prose, not in the menu table.
- Menus: `EditorLayer.cpp` `DrawMenuBar`.
- Shortcuts: `EditorLayer.cpp` `HandleShortcuts`, `UI/EditorActions.cpp`, `Panels/ViewportPanel.cpp`, `Panels/ContentBrowserPanel.cpp`, `PerformancePanel.cpp`, `GameViewPanel.cpp`, `UI/Widgets.cpp`.
- Chips and pills: `ViewportPanel.cpp` `DrawChips` and helpers; `EditorLayer.cpp` `DrawStatusBar` and the pill functions.
- Drag payloads and probe keys: `UI/PropertyWidgets.h`, `Panels/ContentBrowserPanel.h`, `UI/ItemProbe.h`.
- Files outside the assets: `Strata/src/Strata/Core/Platform.h`, `Project/Project.h`, `Editor/RecentProjects.*`, `EditorPreferences.cpp`, `ExternalEditor.cpp`, `ScriptBuild.cpp`, `EditorContext.cpp`, `Network/EditorSession.cpp`, `SceneRecovery.h`, `RuntimeApplication.cpp`.

## Not verified

- Which pills and chips exist in a narrow editor beyond the code read; the Camera chip's popup contents were not read.
- Hierarchy Ctrl+A: the code passes `selectAll=false` for the Hierarchy; the Edit menu still lists Select All.
- The Scripts pill's click target for "not built"; only failed build and crash were seen to open Problems.
- `AcceptsEditShortcuts` conditions beyond "the running game has the input" (taken from code comments).
- Content Browser arrow keys come from ImGui navigation (assumed, not read).
- The tooltip and exact click of the Saving pill were read; the Automation pill's click only for the failed state.
- Which pages (`editor/*`) cover each file row; links chosen by title only.
- Game save folder `<Name>/Saves` (critic-reference-7) not checked.

## Findings not applied

- critic-reference-2: introductions name the teaching page for panels, menus, shortcuts, chips and files; applied except the automation reference link (page absent).
- critic-reference-7: applied as two tables without the "may be deleted" and "page that teaches it" columns (not verified in code); `<Name>/Saves` omitted.
- critic-reference-10: applied (exit code table, 0/1/3/130).
- critic-reference-13: concerns another page and tools; not applied.
- Brief item (4)'s "parsed from DrawMenuBar" tables: no generated file exists, so tables are hand-written.

## Clerk

- Refused: the bold words the page defines locally (route, panel, chip, pill, drag payload, probe key, window/headless/scripted run; panel, chip and pill are homed in editor-ui) are not admitted: a reference page restates terms whose homes are their chapters, and the page proposed none. Left for the writer: the link to reference/automation, which now exists.

## Pin move v0.8.0

- Rechecked against 319075e3 (diff from 822a7a46): EditorLayer.cpp, EditorLayer.h, EditorApplication.cpp, Application.h/.cpp, ViewportPanel.cpp, ViewportToolbar.cpp, SceneHierarchyPanel.cpp; PerformancePanel.cpp, EditorActions.cpp, ItemProbe.h, Platform.h, Project.h and EditorContext.cpp unchanged.
- Changed: `--window-size` in the window run and its refusals; exit codes 1 for an exception out of a frame and for a window not opened or not of the asked size; code 3 also for a refused value; Make Area Light and `editor.screenshot` beside the menus table.
- Unchanged: panels, menu bar, shortcuts, chips (the debug view count is generated), pills, payloads, probe forms, files.
