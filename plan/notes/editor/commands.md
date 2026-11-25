# Notes: editor/commands

## New terms

None proposed. The eight terms the brief names are defined in bold on the page: command, command registry, JSON Schema, command kind, session results, InvalidParameters, Failed, status provider.

## Requests

None. Further reading cites three sources without links (design-pattern books, the JSON Schema and JSON-RPC 2.0 specifications); their hosts may be requested by the planner if links are wanted.

## Since

0.3.0: `editor-core` inventory lists `EditorCommand` and `editor.commands` as 0.3.0 (kinds and flags later).

## Not verified

- The text of the error example in the terminal section is derived from `CheckParameters`, `EditorAutomation::ToRpcResult` and `CliApplication.cpp`; no editor was run. The `data` object is abbreviated.
- The answer of `entity.rename` (keys `entity` and `name`) and of `entity.find` (an `entities` array) come from the handlers, not from a run.
- The group table's "where taught" links use the planned page ids of the briefs; the pages did not exist when this page was written.
- The `ui.*` row links `ui/input`; `input.*` links `input/simulated` and `make/automated-playtests` (the brief puts `ui/input` beside `make/automated-playtests` on the `ui` row).

## Findings not applied

- Brief: `editor.commands` "lists each command's kind and flags". Before v0.8.0 it listed name, description, parameters and kind only. At v0.8.0 it also reports `mayDefer`, `waitsForAssets` (true for every Edit too, `WaitsForAssetScan`) and `results` (`EditorCommands.cpp`, the handler of `editor.commands`); the page now says so beside the marks.
- v0.8.0 move: the UI registers three commands (`EditorLayer.cpp`: `editor.showPanel`, `editor.screenshot`, `editor.showDialog`); the `editor.*` row adds screenshots. Groups rechecked against the v0.8.0 dump (156 commands; new: `asset.types`, `editor.screenshot`, `lighting.makeAreaLight`; no group added or removed).
- Brief: the hands-on "Hierarchy preset through `entity.create`" (`gamedev:556`, `SceneHierarchyPanel.cpp` `CreatePreset`) is not on the page: the page is at its length budget; the file is not quoted. The page shows the UI calling the registry in prose only.
- Brief: `entity.paste`'s `EntityCommands.cpp` line ranges are not quoted; the clipboard is described from the registered descriptions.
- Brief: the figures "three clients, one registry" and "command lifecycle" are Mermaid diagrams on the page, so there is no figures file.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
