# Notes: editor/play-mode

## New terms

None proposed; the nine glossary terms of the brief are defined in bold on the page.

## Since

since 0.3.0: the brief's inventory rows (editor-core:216-220) list SceneState, Play, StartRuntime and Stop as 0.3.0.

## Requests

- Figure `scene-and-game-view` (editor, project Showcase): needs the layout `layouts/play-mode.ini` with the Scene view and the Game view side by side; waits for tier 2: editor screenshot.
- Hosts for Further reading (cited without links): docs.unrealengine.com, docs.unity3d.com, docs.godotengine.org.

## Not verified

- The statements about Unreal (world duplicated for play in editor), Unity (state stored and restored) and Godot (separate process) come from the brief, not from their documentation.
- That the Scene view and the Game view both draw the running copy while it plays was not checked in the panel code; the page states only which camera each uses.
- Which of the shell tests sit in which suite of EditorGameShellTests.cpp; the page names the file.
- The journal event name for a scene switch (play.sceneSwitched) is not named on the page: the names check refuses it as a command and the word list refuses it as text.

## Findings not applied

None: the brief lists no open findings.

## Figures

- `scene-and-game-view`: made `layouts/play-mode.ini` (960 × 540, from `editor-tour-side.ini` with a 150 px
  Hierarchy and a 180 px Inspector, so that the two views are 312 px wide each). Round 1 (paused, 120 steps): the
  views differ as the caption says, but the side panels read Paused while the caption says the game plays. Round 2
  (`play.start` unpaused, 600 frames): the Scene view shows the bus and the tank close up from a set editor camera,
  the Game view shows them from the tour's high camera; caption and alt name both. Taken only with the provisional
  build; `waitsFor` kept, nothing published.
- `scene-and-game-view`, at the pin v0.8.0 (319075e3): `waitsFor` removed (the pin has `editor.screenshot`); one
  take with the recipe unchanged. Both side panels read Playing; the Scene view shows the bus and the rusty tank
  close up over the grid with the red and blue axis lines; the Game view shows them small from above, without the
  grid. Published.

## Clerk

- Nothing to admit.
- Hosts: none admitted; the sources are cited without links, so no host is needed (docs.unrealengine.com is not on the list and is the planner's).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
