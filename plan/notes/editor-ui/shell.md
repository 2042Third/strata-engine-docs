# Notes: editor-ui/shell

## New terms

None proposed. Defined in bold: editor shell (EditorShell), panel (panel registry), DockBuilder, settings handler (glossary homes).

## Requests

- Words for tools/data/extra-words.txt: "toolbar" (4 uses, the main toolbar of the editor window) and "unsaved" (13 uses, "unsaved changes"). Both fail word-list.
- Figures (src/content/figures/editor-ui/shell.json): editor-default-layout needs the layout layouts/editor-shell-default.ini (default layout, ThirdPerson copy, 1600x900 at 100 %, annotated with panel names); unsaved-changes-dialog needs the same layout, an edit, then File > Open Scene. Both waitsFor tier 2: editor screenshot.
- The Mermaid diagrams (architecture, frame, panel life, default layout, the question) are not rendered by me.
- Further reading names books and the Dear ImGui documentation without links.
- Brief item new:35 Hard exercise (predict then run, a patch): not done as a patch; exercise 3 is a standalone sketch (Don't Save decision) because the pin's tutorials folder has no patch tooling in this task.

## Not verified

- At 200 % the editor's font size is 28 pixels and the dock space is 1600 pixels wide (worked example): derived from body text size 14 pixels, not measured.
- The text fence of a settings file (`[StrataPanels]` sections with ContentBrowser, Hierarchy, Streaming) is a constructed example from WriteSettings, not a captured file.
- That ImGui keeps one popup per level is taken from the engine's comments (EditorShell.h, EditorLayer.cpp), not from ImGui's source.
- The Alternatives table's "Who uses it" column is general knowledge; no source cited.
- The claim that the Bedrock theme is the style callback's theme: UI::ApplyTheme, with `c_Bedrock` in Theme.cpp; ApplyTheme's body was not read.

## Findings not applied

None open in the brief. Not on the page: the status bar pills, toasts, idle throttling and frame stats (other pages), the full menu contents (reference/editor), the launcher panel's contents. The Hard exercise's patch (new:35) is replaced by a sketch.

## Figures

Taken once with the provisional build (engine 5b975ad2831e), not published; both keep `waitsFor: tier 2: editor screenshot`.

- editor-default-layout: the recipe asked for 1600 by 900 with each panel named; nothing labels panels beyond their
  tabs, and a window that large reads badly in the 768 px column. Now 960 by 540 with `layouts/editor-shell-default.ini`
  (a copy of `layouts/dialogs.ini`, the default layout at that size), ThirdPerson copy, start scene MainMenu. Round 1
  good: Hierarchy, Scene and Game, Inspector and Asset, Console, Problems and Content Browser, status bar, all readable.
  The default layout opens only three of the six bottom panels (Streaming, Performance, Activity are docked there but
  closed), so the caption names the three shown. The Content Browser's grid is cut by the short bottom area.
  Mend (viewer: the alt's "file browser" shows no files): the status bar cuts the Content Browser's tiles below its
  search box and filter buttons. The layout stays, since it is the true default; the alt now names only the search box
  and filter buttons. No retake: the recipe did not change, so the picture is the same.
- unsaved-changes-dialog: the recipe had no steps; File, Open Scene opens a native file dialog, which commands cannot
  drive. Now `entity.create` (Crate), then `editor.showDialog {dialog: "newProject"}`, which asks about the unsaved
  change first. Round 1 good: "Unsaved Changes", "Save changes to 'MainMenu'?", Save, Don't Save, Cancel.

Published at the pin v0.8.0 (319075e3), never published before, so nothing to compare; recipes unchanged, one round
each, taken without `--provisional`.

- editor-default-layout: as at the provisional take: every named panel, the toolbar and status bar readable; the
  Content Browser shows its search box and filter buttons, its tiles cut by the status bar, as the alt says.
- unsaved-changes-dialog: "Unsaved Changes", "Save changes to 'MainMenu'?", Save (orange), Don't Save, Cancel over the
  darkened window; Crate last in the Hierarchy.

## Since

0.3.0: Docs/Releases/0.3.0.md line 31 lists dockable panels (Viewport, Hierarchy and others) among the first release's features.

## Clerk

- Admitted to extra-words.txt: toolbar, unsaved.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
