# Notes: `editor-ui/ui-scale`

## New terms

None proposed. The page defines `pixels`, `points`, `UI scale` and `FontScaleDpi` (homed here) in bold.

## Requests

- The figure `scale-pair` (kind editor, two variants `hundred` and `double`) needs the layout `layouts/default.ini`; the `double` variant needs the editor started with `--ui-scale 2` (no setup step sets it), the other with `--ui-scale 1`.
- `tools/external-hosts.txt`: none; Further reading names Dear ImGui's documents, Apple's documentation and the Wayland protocol documents without links.

## Since

`since: 0.4.0`. `ToUIScale` first appears in commit `09e8fd08` (2026-10-14), contained in `v0.4.0`.

## Not verified

- Retina and Wayland behavior was read from the code and its comments and tests, not run (the pin's build was not made).
- That Wayland measures windows in points: taken from the brief and `ImGuiLayer.h`'s comment.
- Pixel densities named in the problem section (about 100 and 200 pixels in an inch) and the sizes in millimetres are general knowledge.
- The table's "who uses it" column is stated without naming programs; no source for any program was checked.

## Findings not applied

The brief lists no open findings.

## Figures

### scale-pair (editor, variants `hundred` and `double`)

- Round 1 (provisional build, 2026-11-18): the recipe named `layouts/default.ini`, which does not exist, in a
  1280 × 720 window. It now uses `layouts/editor-shell-default.ini` (the default layout made for 960 × 540, the one
  editor-ui/shell pictures) with `windowSize` 960 × 540, so that the scale-1 side reads at the column's width.
- Commands cannot show the `double` side. `tools/figures.py take` starts every editor figure with `--ui-scale 1`, and
  that option wins over the Interface preference (`EditorHost.h`, `EditorApplication.cpp`: "--ui-scale wins for its
  session"), so a `preferences.set` step would change nothing. It would also write the person's Preferences.json, which
  the card forbids. No editor command sets the UI scale. Both variants therefore come out at scale 1 and look the same.
  The round-1 take confirmed this: in both, the panels, text and paddings are identical at scale 1. The text reads at
  960 × 540. Only the Scene view differs: in `hundred` the Showcase was still drawing without its terrain and grid,
  and in `double` it had them.
- What the page needs: a recipe field such as `editorWindow.uiScale` that `take` passes as `--ui-scale <factor>` (a
  tools/figures.py change for the planner). With it, `double` gets `uiScale: 2`. That window should be about
  1280 × 720 and use its own layout made at that size, so the panels have room for doubled text. Then retake both sides.
- Until then the nearest honest picture is the `hundred` side alone, with a caption that says only what it shows. The
  page's sentence "The picture shows the effect of the number on a real layout" needs the pair, so the recipe stays a
  compare.
- Round 2 (pin v0.8.0, 319075e3, 2026-11-23): not taken. `check` found that the pin has `editor.screenshot`, so the
  old `waitsFor` "tier 2: editor screenshot" was met, but the block above still holds: `booklib/editor.py`
  `window_arguments` still passes `--ui-scale 1` to every editor, and the v0.8.0 command dump has no command that sets
  the UI scale. A take would give two identical scale-1 pictures, which cannot show the caption, so no take was made
  under the lock. The recipe's `waitsFor` is now "tier 3: the editor drawn at a UI scale of 2; ..." so that it is not
  taken as is. Still needed: the `editorWindow.uiScale` field described above (a tools/figures.py change), then a take
  of both sides.
- Caption to check once the pair exists: ImGui's docking sizes are pixels, so the panels keep their pixel sizes while
  text, padding and buttons double. "every panel ... keeps its place relative to the text" may not hold. Write what
  the picture shows (for example, fewer rows fit in each panel).
- Round 3 (pin v0.8.0, the final pin, 2026-11-24): still not taken, for the same reason: `tools/booklib/editor.py`
  `window_arguments` passes `--ui-scale 1` to every editor and the recipe has no field for the scale. The entry keeps
  its `waitsFor` as the request for a later edition and names the stand-in `scale-rows`, a drawing that the page now
  places. The drawing shows one panel of 304 by 248 pixels with labelled fields, to scale at 1 and 2, from the pin's
  sizes: body text 14 (`StrataEditor/src/UI/EditorFonts.h`), `WindowPadding` 8, `FramePadding` (8, 4) and
  `ItemSpacing.y` 6 (`SetBaseSizes`), so a row is 22 + 6 = 28 at 1 and 56 at 2; eight rows fit, then four. The
  panel keeps its size because dock node sizes are pixels and nothing rescales them with the UI scale. The labels are
  plain Field 1 to Field 8: the drawing is a sketch of a panel, not one panel of the editor (its first labels, light
  names such as Falloff and Softness, read as an inspector of a light component the pin does not have). The sentence before it now introduces a drawing.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
