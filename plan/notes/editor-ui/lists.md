# Notes: editor-ui/lists

## New terms

None. The seven glossary terms of the brief are defined in bold on the page.

## Requests

- Layouts for the editor figures: `layouts/hierarchy.ini` (the Hierarchy panel large, Scene view small) and `layouts/content-browser.ini` (the Content Browser large).
- Figures `hierarchy-expanded`, `hierarchy-searched`, `hierarchy-drag` and `content-grid` are not taken yet (`tier 2: editor screenshot`). `hierarchy-drag` needs a drag held in progress; the recipe has no step for it, the planner must choose how to take it. The brief's list view and Scripts root pictures are not requested (the page shows one Content Browser figure).
- The three links `../editor/program.md`, `../editor/trash-references.md` and `../editor-ui/instrument-panels.md` point at pages written elsewhere.

## Not verified

- The Content Browser's list view (`DrawList`) and the asset picker list were not read; the page names them only in the list of clipped lists, from the inventory and a grep of `ImGuiListClipper` uses.
- That the Scripts root lists its files on an I/O thread is from the header comment of `UI/ScriptBrowser.h`, not from running it.
- The pixel numbers of the Content Browser example (16 pixel font, 8 pixel spacing, 800 pixel panel) are assumptions stated as such on the page.

## Since

`since: 0.3.0`: `HierarchyView` (commit 63fa332b, 2026-10-10) and `AssetBrowserView` (c68b16f9, 2026-10-11) first appear in the tag `v0.3.0-rc1`.

## Findings not applied

- The brief names no open findings.
- The brief's picture of the Content Browser's list view and the Scripts root, and the box-select and Ctrl+A gestures as pictures, are not drawn: the page has one grid figure.
- The page has no "What went wrong before" section: the history holds no bug with a regression test for these lists that I could verify.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

2026-11-23, at the pin v0.8.0 (319075e3): `hierarchy-expanded`, `hierarchy-searched` and `content-grid` taken once with the release build (no `--provisional`) and published; each shows what the provisional takes below showed (the same rows, badge colors, dimmed rows and tiles), so the recipes and captions stand. `hierarchy-drag` stays unpublished for the reason in its line below.

Earlier, with the provisional build (engine 5b975ad2831e, `--provisional`):

- `hierarchy-expanded`, round 1: good. The Hierarchy at 300 × 642 pixels shows Props and LanternA expanded, the prefab badges on the instance roots, blue prefab parts, and LanternA.Wick dimmed with a crossed eye.
- `hierarchy-expanded`, round 2 (a viewer's fault): the badges have two colors, blue on Bus, OilTank, FuelTank and Hut, yellow on CoveredCar, FirePit, LanternA, LanternB and Drum0 to Drum6, and the caption did not say why. `SceneHierarchyPanel.cpp` draws the badge `colors.Warning` when `PrefabSync::IsModified` holds and `colors.Info` otherwise, so the caption and alt now say blue when the instance matches its prefab and yellow when its values differ, and name the dimmed row as a part of the first lantern (LanternA.Wick; engine names and the word "wick" fail the caption lint). Retaken: the same picture.
- `hierarchy-searched`, round 1: the rows filled only the top third of the 642 pixel panel. Round 2: new layout `layouts/hierarchy-short.ini` (960 × 440, the Hierarchy 300 pixels wide), `windowSize` [960, 440]; good. Sky and Sun white, Fire and the two lantern lights blue, their groups dimmed. The caption now says the search finds every kind of light component, as the page's search paragraph says of `c:light`.
- `content-grid`, round 1: good. The Content Browser at 797 × 380 pixels: the folder tree on the left, seven folder tiles and the Icon picture with its thumbnail in the grid.
- `hierarchy-drag`: not taken; commands cannot show it. No command holds a drag in progress, so the drop line and the framed row of a drop inside never appear in a take. The recipe is left as written. What the page can get instead: a diagram of one Hierarchy row with its drop zones as the page's drop section describes them, or a picture of the Hierarchy after `entity.setParent` with the moved entity selected under its new parent.

2026-11-24, finishing the figures at the pin v0.8.0 (319075e3): `hierarchy-drag` is marked `blocked` (no command holds a drag in progress, so no take at the pin shows the drop line or the framed row; its reason stays as the request for a later edition) with the stand-in `hierarchy-drop-zones`, a drawing. The drawing shows the rows A, B, X, Y and C of the page's example with B expanded, and three drops of A as `SceneHierarchyPanel::AcceptRowDrops` draws them (`StrataEditor/src/Panels/SceneHierarchyPanel.cpp`, lines 1057 to 1069 at the pin): before C (a line on top of C's row at depth 0, top level, index 1, the example's answer), inside C (the row framed in the accent on a pale fill, parent C, index 0) and after the expanded B (a line under B's row indented to the depth of X, parent B, index 0, as `HierarchyView::GetDropTarget` puts it in front of the first shown child). Below them, one row split into its quarter, half and quarter zones. The page places it after the example "A drop, by hand", with a sentence that introduces it, instead of among the pictures after the Content Browser's thumbnails, since it teaches the drop zones. Drawn, rendered in both themes, looked at and checked (`drawings.mjs check` passes); `pagecheck` passes.
