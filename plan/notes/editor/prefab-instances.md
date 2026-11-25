# Notes: editor/prefab-instances

## New terms

None proposed. The six terms of the brief (baseline, catch-up, outdated, outdated instance, part version, synced hash) are defined in bold on the page.

## Since

0.3.0: linked instances and prefab sync (inventory editor-core, `PrefabSync` row, 0.3.0); the version and hash catch-up and the override lists arrived in 0.4.0 (same rows). The page covers the pin's whole behavior, so it takes the earliest value.

## Requests

- Layout `layouts/prefab-instances.ini`: Hierarchy and Inspector docked, the OpenWorld sample, one `Fox` instance selected.
- Figures `hierarchy-marks` and `prefab-bar`: their setup steps only instantiate the prefab. To show a modified and an outdated mark, the planner must add steps that edit a property of one instance; an outdated instance needs a scene written without override lists, which no command makes.
- Hosts: none new. The Further reading entries are docs.unity3d.com pages.

## Not verified

- The Unity Manual page names and addresses in Further reading were not opened.
- That Unity has a "Prefab Mode" with no apply step (the Alternatives table).
- The sizes behind `DragInPrefabInstance5kMedian` (what the 5k counts) were not read in the test.
- The Hierarchy mark labels as drawn: only the enum `PrefabBadge` (`Linked`, `Modified`, `Outdated`) was read.

## Findings not applied

- The brief says a modified instance becomes outdated in the catch-up. At the pin (`PrefabSync::CatchUp`, test `A prefab applied in another scene reaches its instances when their scene opens...`), an instance with an override list takes the new version except its overrides; only a modified instance without a list is outdated. The page teaches the code.
- The brief's example (change an instance in scene B, close it, apply from A, open B) ends with an outdated B instance. At the pin that holds only for an instance without a list, so the example uses three instances (unchanged, with a list, without a list).
- No "What went wrong before" section: no regression with a history was found in the pin's documents.
- The inspector's prefab bar is only requested as a figure; how it is drawn belongs to `editor-ui/inspectors`.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Taken with the provisional build (engine 5b975ad2831e), one round, both kept with `waitsFor` until the pin moves. Layout `layouts/prefab-instances.ini` (960 × 440, Hierarchy 300 px, Inspector 380 px) is a copy of `layouts/hierarchy-short.ini`. Both recipes now use the template `basic3d` and build the page's example: a prefab `Crate` with a child `Lid`, the original linked by `prefab.create`, one more instance `Crate (1)` at (3, 0.5, 0), whose lid is raised to (0, 1.5, 0).

- `hierarchy-marks`, round 1, good: the Hierarchy panel with a blue mark on `Crate` and a yellow one on `Crate (1)`. The recipe's two Fox instances with no edit could show only linked marks. The page's three distinct marks cannot be shown: at the pin, `SceneHierarchyPanel.cpp` gives a modified and an outdated root the same icon and the same Warning color; only the hover tooltip differs, and no command shows a tooltip. No command makes an outdated instance either (it needs a scene written without override lists). The caption now says that an outdated instance keeps the yellow mark and only its tooltip tells it apart. The page's sentence "The Hierarchy draws such an instance with the outdated mark" (section on catch-up) suggests a mark of its own; the writer may want "with the modified mark, and its tooltip says it is outdated".
- `prefab-bar`, round 1, good: the Inspector of the raised lid. The recipe's root of a Fox instance has no overridden property, because a root's transform and name are never overrides; the lid, a child, shows the bar (Crate, Select, Open, Overrides (1)) and the bold Translation label with its orange bar.
- Round 2, words only (a viewer's report; steps unchanged, so no retake: the round 1 pictures stand). `hierarchy-marks`: both Crate rows have a blue cube icon and a blue name, so "the mark beside an instance root" did not say which mark; caption, alt and shows now name the package mark at the right end of the row, left of the eye. `prefab-bar`: the caption did not say how the override is marked nor whose lid it is; it now names the Lid of Crate (1), the bold Translation label with the orange bar at its left, and the same bar on the Transform header (checked enlarged: the Mesh Renderer header has none). The caption's "Crate (1)" and "one override" are explained in `numbers`.
- Pin v0.8.0 (319075e3), one round, both published: `check` asked to remove the `waitsFor` lines (the pin has `editor.screenshot`), and the take without `--provisional` shows the same states as the provisional one: blue package mark on `Crate`, yellow on `Crate (1)`; the Lid's Inspector with the bar (Crate, Select, Open, Overrides (1)), Y 1.5, the bold Translation label and the orange bars on the row and the Transform header. Recipes and words unchanged. The remark above on the page's "outdated mark" sentence still stands.
