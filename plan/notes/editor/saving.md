# Notes: editor/saving

## New terms

None proposed. The page defines the six glossary terms of its brief (snapshot (save), document claim, publish (editor), coalescing, unwritten settings, discard scope); it also defines "save point" in bold (a term of editor/undo's closure, defined here in one sentence as a local explanation).

## Since

0.4.0: background saves, `Strata/src/Strata/...` and `StrataEditor/src/Editor/DocumentSaver.cpp`; the 0.4.0 release notes (`Docs/Releases/0.4.0.md`, "Background saves and large projects").

## Requests

- Figure: the saving status pill and the saving dialog while a large scene saves (brief item editor-core:517) is not drawn; the page has no figures file. The pin's UI code was not searched for the pill's label, so the page says only that the status bar shows a save in flight (tested by `Editor.UI.Saves`). An editor figure needs a layout and a project with a large world scene.
- Mermaid diagrams drawn: the files and threads of a scene save; the guard's decision tree. The background save timeline (editor-core:476) is covered by the worked example's numbered steps, not a diagram.
- Further reading names three sources without links (Redis persistence documentation, Kleppmann's book, the 0.4.0 release notes): hosts not requested.

## Not verified

- The Redis claim in the Alternatives table (fork-based snapshots on systems that have fork) is general knowledge, not checked against its documentation.
- The 22 s freeze is quoted from `Docs/Releases/0.4.0.md`, not measured.
- That Strata's job system has one background worker in the editor (the page says it only of the tests' `GatedJobSystem`).
- Which other callers of `AssetEdit::ApplyDocument` exist besides `prefab.apply` (the release notes name the Asset tab's editors); the page names only `prefab.apply`.

## Findings not applied

None: the brief's one open item (editor-core:804) was checked and holds at the pin: `prefab.apply` calls `AssetEdit::ApplyDocument` (`StrataEditor/src/Editor/EditorPrefabCommands.cpp:570`), which saves in the frame through `SaveNativeAsset` (`StrataEditor/src/Editor/AssetEdit.cpp:95`). It is stated on the page.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
