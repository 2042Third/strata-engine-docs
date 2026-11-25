# Notes: editor/placement

## New terms

None proposed. Defined in bold: support function, snapping (editor), placement ghost (glossary homes).

## Requests

- The ghost picture (brief items editor-core:526, scene-ecs:482, editor-ui:568: a prefab dragged over a surface and over empty sky) is not on the page: it needs layout and project choices that are the planner's. The page carries one Mermaid map and no figures file.

## Not verified

- The table's "Who uses it" column (selection by picking in many editors, some games' physics tools): general knowledge, no source cited.
- That the Scene view's selection picking reads an ID buffer: inventory only, not read in code.
- That the `Editor.UI.Placement` suite needs no graphics device: not checked, the page does not say.
- The 30 % hidden-edge strength is the constant c_HiddenEdgeAlpha applied to the hit color's alpha (header read, drawing code not read).

## Findings not applied

None open in the brief. The stackOn exercise is answered in prose, not as a patch (tutorials/ patches not available to this page).

## Since

0.3.0: SceneRaycast file dated 2026-10-11 (inventory editor-core:190). Placement by ray (`asset.place`, `scene.raycast`, the ghost): after 0.7.0, marked with :since[0.8.0].

## Pin move to v0.8.0

- Read again at the move (process.md step 11). `git diff 822a7a46 319075e3` touches none of SceneRaycast, EditorPlacement,
  PlacementPreview, AssetBounds, Commands/PlacementCommands.cpp or PlacementTests.cpp, and no placement lines of the
  panels; quotes, names and sketches pass at 319075e3. Docs/Releases/0.8.0.md agrees (the drop ghost is a box, not the
  mesh; Escape cancels; snapping applies). The :since[0.8.0] mark is now a released version. No page change.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
