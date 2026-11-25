# Notes: editor-ui/design-system

## New terms

None proposed. The page defines the eight terms of the brief (theme, token, type scale, icon font, Private Use Area, merge mode, CJK, fallback glyph).

## Requests

- Layout `layouts/design-system.ini` for the figures `default-and-bedrock` and `cjk-name`: Scene view, Hierarchy and Inspector visible.
- Figure `default-and-bedrock` needs the editor started with `--imgui-demo` for its imgui-default variant (steps cannot pass a program option); both figures wait for tier 2: editor screenshot.
- Figure `cjk-name` shows a Japanese entity name in the Hierarchy (a project name would need a recipe step to rename a project).
- Words used only in code spans: font names (Inter, Lucide, JetBrains Mono) and the sixteen token names; ask for them in `names.txt` if prose use is wanted.

## Not verified

- The Strata editor offers 1.5 and 2 as UI scales (from the page's own reasoning about even base sizes; the code comment only names 1.5x and 2x).
- That `GetGlyphGeneration` has no reader outside `EditorFonts.cpp` at the pin: grep of StrataEditor and StrataTests found none.
- Icon offset scales with the size: taken from the comment in `EditorFonts.cpp`, not measured.

## Figures

- `default-and-bedrock` (compare, two variants): no command can show it, so the recipe is left as written. The
  editor always applies Bedrock (`ApplyTheme`), and no command, preference or program option draws its panels in
  ImGui's default style. `--imgui-demo` only offers ImGui's demo window in the Help menu, and that window is drawn in
  Bedrock too. The layout `layouts/design-system.ini` it names was never made, because a recipe for the left half
  cannot exist. Not taken. What the page gets instead: one picture of Bedrock alone (the Hierarchy panel of a
  sample with a row selected, as `cjk-name` takes it), with ImGui's default style shown by a picture from ImGui's own
  documentation under its license, or by a table of the two styles' colors for a few slots. Either needs the page's
  paragraph and the compare to change, which the writer decides.
- `cjk-name`: round 1 took the Hierarchy panel of a new basic3d project with an entity named 敵の城, in
  `layouts/hierarchy-short.ini` (960 × 440): the name is drawn by the merged system font, but the panel's lower half
  was empty and the alt counted three rows where the panel has six. Round 2 used the new
  `layouts/design-system-cjk.ini` (960 × 360, the smallest window a recipe takes) and waits 120 frames for the merge;
  caption and alt now say six rows, five Latin names above the Japanese one. Passed (provisional build).
  Round 3: a viewer found that the paragraph after the figure speaks of a name of four question marks becoming four
  wide characters, while 敵の城 has three. The viewer proposed changing the paragraph to say three; the photographer
  may not change the page's words, so the recipe now names the entity 敵の城門 (four characters) and the alt says four.
  The writer may still prefer the paragraph's wording to point at the picture ("like the one pictured").
- Taken at the pin v0.8.0 (319075e3), 2026-11-23, one round, both figures published; `waitsFor` removed (the pin has
  `editor.screenshot`).
  - `default-and-bedrock`: the page shows the variant `bedrock` alone, but a recipe with variants needs two and the
    page names one, so the variant `imgui-default` (which the editor cannot draw: it would have been a second Bedrock
    picture under a false name) became `hierarchy`, the Hierarchy panel alone at 1:1, with its own shows and alt. The
    missing `layouts/design-system.ini` was replaced by `layouts/editor-shell-default.ini` (960 × 540, made for
    `editor-ui/shell`), and the Sun is selected so the orange accent of a selected row shows. `bedrock`: the whole
    window with the Showcase, dark panels, pale text, square tabs, the orange row and toggles; the Scene view looks at
    a hazy horizon from the editor's start camera, which the caption does not mention. Passed. The writer may drop the
    variants and `variant=bedrock` together, which leaves one picture; `hierarchy` then goes.
  - `cjk-name`: six rows, 敵の城門 in the last, in the same size and color as the five Latin names. Passed.

## Findings not applied

None: the brief listed no open findings.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
