# Notes: editor-ui/inspectors

## New terms

- live line: a line of text in an Inspector section that describes the state of the renderer or project in words, not a property (the sun's "Shadow maps" line); home: this page.
- draft (import settings): the panel's copy of an asset's import settings that collects edits until Apply or Revert; home: this page.

## Requests

- Layouts for the figures: `layouts/inspectors.ini` (Inspector large), `layouts/inspectors-prefab.ini` (Inspector, prefab instance, Overrides menu open), `layouts/inspectors-ui.ini` (Inspector with a UI Rect, anchor grid open), `layouts/inspectors-asset.ini` (Asset tab large).
- Figures not taken (11, all `tier 2: editor screenshot`): the prefab-instance, ui-rect-drawer and the three Asset tab figures have no setup steps; they need a selection or an inspected asset that the planner chooses (`selection.set` with an asset).
- No new words requested.

## Not verified

- The Inspector title block's ID with a copy button (from the inventory; the code read shows the name, count and active toggle).
- The theme's axis color names (Cinnabar, Malachite, Azurite) are from a header comment and are not named on the page.
- That the two rotation regression tests fail without the fix: not run.
- The page does not say what `Extract Sun`, `Add Height Fog` and `Bake Reflection Probes` do; the scene-settings sky block is described only in outline.

## Findings not applied

- The brief's exercise "a light's color temperature as a gradient bar" names a property the pin does not have; the exercise uses the post-process `WhiteBalanceTemperature` (range 2000 to 15000) instead.
- The brief lists the UI Rect drawer's "rect kept in place while its anchors change"; only the preset grid, the toggles, the margins and the overrides are on the page (the keep-in-place rule is `UIRectEdit`'s `ApplyPreset`, not read in detail).
- The brief's pictures of a camera in Orthographic with Depth Of Field greying Aperture: only the orthographic part is requested.

## Since

0.3.0: the Inspector and Asset tab existed from the first release (inventory assets:215, "0.3.0 onward").

## Clerk

- Admitted the terms live line (alias live lines) and Draft (editor-ui), homed here.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Taken at the pin 319075e3 (release 0.8.0), one hold, round 1 for all eleven (the recipes were settled with a provisional
build of this release); nine published, `waitsFor "tier 2: editor screenshot"` removed from all eleven. The page
places the nine published ones (2026-11-24; inactive-property also with its crop `lookup`); the two that wait for tier 3 have drawn stand-ins in their places (below). Panels at 1:1, 380 px wide; layouts `layouts/materials.ini`,
`layouts/make-look.ini`, `layouts/make-sound-short.ini` and this page's `layouts/inspectors-asset.ini` (1280 x 940).

- one-entity (published): Lamp's ID with its copy button, Transform behind red, green and blue axis labels, Point
  Light with Cast Shadows off and its three shadow rows dim, Add Component below.
- mixed-values (published): header "3 entities", Intensity "--", Translation X "--", and the line that components only
  some entities have are not shown.
- prefab-instance (published): `LanternA.Light`: the bar Lantern, Select, Open, Overrides (7); Source Radius bold with
  the orange bar; Point Light and Script headers barred. Cannot show: the open Overrides menu (no command opens a
  menu); the page would need a diagram for it.
- inactive-property (published): Color Lookup None, Color Lookup Intensity gray with a dim slider. The label "White
  Balance Temperat..." is cut by the 380 px column (not the figure's subject). Cannot show: the reason's tooltip.
  Round 2 (a viewer: the gray row is one row near the bottom, nothing points to it): crop `lookup` (Color Lookup and
  Color Lookup Intensity, enlarged 2 times); caption and alt now say "at the end of the Tone and color group". The
  ellipsis stays: it is the behavior the page describes for a name wider than its column.
- ui-rect-drawer (published): `Frame` under Tetris's HUD: Anchors "Stretch", Left, Right, Top, Bottom at 24.0, On
  Screen "17, 17 639 x 475". Cannot show: the grid of presets (a popup). Round 2 (a viewer: 24 and 17 read as a
  contradiction): the caption explains On Screen (pixels at the game's screen after the canvas scales its units; the
  editor prints the box times the canvas scale, `UIRectDrawer.cpp`). The page's words never explain On Screen.
- camera-orthographic (published): the three perspective rows gray, the orthographic rows bright, the five depth of
  field rows from Depth Of Field to Sensor Height gray. Round 2 (a viewer: with Depth Of Field off the lens rows would
  be gray anyway): the recipe sets `DepthOfField: true`; the box shows checked yet gray, so the projection is what
  turns the rows off (`WithLens` checks the projection first, `ComponentRegistration.cpp`).
- asset-material (published): Planks, "Material · Materials/Planks.stmat", handle, Reimport, the Material section with
  colors, sliders, check boxes and four texture slots.
- asset-normal-map (published): Usage Normal Map, the preview purple and blue with the boards' edges in light and dark
  lines, and the line "1024 x 1024 · BC5 · 11 mips · 341.4 KB on the GPU". Cannot show: a raw view beside it.
- asset-audio (published): Clear, Load Mode Decompressed, Play, "0:00.4 · 22050 Hz · mono", the orange waveform of
  short bursts.
- taa-preset-drawer (waits, `waitsFor` tier 3 kept as the request): the 1280 x 1360 window shows the Post Process
  section down to Ambient Occlusion; the TAA Preset row is below, and no command scrolls a panel or folds its groups.
  Stand-in (2026-11-24): the drawing `taa-preset-row`, the Anti-aliasing group's last three rows with TAA Preset at
  Sharp, a bracket under the label cell (what `PropertyLabel` draws: name, tooltip, bold and accent bar of an
  override, gray and reason of an inactive row, "Anti Aliasing is off") and one under the value cell (the generic
  drop-down Sharp, Original, Custom; one `component.set` with the preset and, for Custom, the start values). Placed
  after the drawer's code notes (a figure between the paragraph and the fence fails `code-intro`); the paragraph's
  second sentence now ends "as the preset's row below shows".
- add-component (waits, `waitsFor` tier 3 kept as the request): no command opens a popup or types into its filter.
  Stand-in (2026-11-24): the drawing `add-component-popup`, two lamps selected (Lamp A: Transform, Point Light; Lamp B:
  also Audio Listener) and the popup with li typed: Audio (Audio Listener), Lighting (Directional, Spot, Rect Light,
  Light Surface, Sky Light; no Point Light), Physics (Box, Sphere, Capsule, Mesh Collider), UI (UI Slider), read from
  `DrawAddComponentPopup` and the pin's registrations (Rect Light, Light Surface and Wind Zone are newer than the
  822a7a46 dump). The paragraph gained "The drawing shows the list for two lamps with two letters typed."

Problems of the page's words that the pictures show:

- "A raw view of the same normal map would look flat purple-blue, and the `NormalXY` mode shows the surface": the
  `NormalXY` preview is itself purple-blue (it shows n * 0.5 + 0.5). A raw view of the BC5 texture would have no blue at
  all (reds and greens). The sentence needs rewording to that.
