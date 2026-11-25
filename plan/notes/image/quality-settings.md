# Notes: image/quality-settings

## New terms

None proposed. "Row" and "follows the preset" are used in plain prose, not bold.

## Since

0.7.0: `StrataScriptCore/Include/StrataScript/Graphics.h` says "Engines without graphics options (before 0.7.0)"; `Docs/Roadmap.md` records native resolution as the owner's direction of 2026-10-26.

## Requests

- Layout `layouts/graphics-quality.ini` for the figure `graphics-page`: Project Settings open on the Graphics Quality page and the Scene view with its quality chip visible.
- Figure `third-person-menu` waits for a picture of the Third-Person sample with its settings menu open (tier 3).
- Tool defect: `tools/lint.py` cannot match the glossary term "Players' rows": `word.key` strips the apostrophe ("players") while the glossary name keeps it ("players'"), so `term-defined` fails on any text. The page defines it in bold.

## Movable claims

Reviewed at v0.8.0 (319075e3) against `Docs/Releases/0.8.0.md` ("What High and Ultra draw").

- Shadowed point and spot lights 4, 16, 64, 256 by preset (callout of the rows' quote):
  `Strata/src/Strata/Renderer/RendererQuality.cpp:45`.
- Point and spot shadow views per frame 12, 12, 24, 48 by preset, the row new in 0.8.0 (same callout):
  `Strata/src/Strata/Renderer/RendererQuality.cpp:46`.
- Contact shadows off in every preset: `Strata/src/Strata/Renderer/RendererQuality.cpp:52`.
- Low's reflections and motion blur `Off`: `Strata/src/Strata/Renderer/RendererQuality.cpp:55-56`.
- High's shadow row `AutoFine` with five cascades: `Strata/src/Strata/Renderer/RendererQuality.cpp:39-40`.
- `AutoFine` is 4096 below 1440 output rows and 8192 from them (worked example, exercise 1):
  `Strata/src/Strata/Renderer/RendererQuality.cpp:539`, the field's description at line 745.
- Cascade memory cascades × size × size × 4 bytes (320 MiB and 192 MiB at 1080 rows; 1280 MiB at 2160):
  `Strata/src/Strata/Renderer/RendererQuality.cpp:65` (`CascadeBytes`, the count the Graphics Quality page shows).
  The release notes give High 256 MiB at 1920x1080 and 1 GiB at 3840x2160, which is four cascades; the code's row
  and `CascadeBytes` give five, so the page keeps 320 MiB and 1280 MiB (see Findings not applied).
- Five players' rows: `Strata/src/Strata/Renderer/RendererQuality.cpp:181-185`.
- Seven graphics host functions: `StrataScriptCore/Include/StrataScript/ScriptABI.h:730-737`.
- The section's version rises by one per row (exercise 3): `Strata/src/Strata/Renderer/RendererQuality.h:193`
  (`c_SectionVersion = 7` at the pin; the page states no number).

## Not verified

- That the editor's Graphics Quality page and the Scene view's chip look as the figure's alt describes (drawn from the Manual and the page's source, no picture seen).

## Findings not applied

- The Developer Guide's table says the five players' rows "only turn off what a scene uses"; at the pin the `AntiAliasing` row also enables anti-aliasing and chooses the method (`SceneRendererPost.cpp`, `ApplyQualityOverrides`). The page states what the code does.
- v0.8.0: `Docs/Releases/0.8.0.md` states High's sun shadow maps as 256 MiB at 1920x1080 and 1 GiB at 3840x2160
  (four cascades); `c_ShadowCascadesRow` is 5 at High and `CascadeBytes` multiplies by it, so the page states the
  code's 320 MiB and 1280 MiB. An engine-side question for the release notes, not a page change.
- No separate section "What went wrong before": no regression history for this part was found.
- The Manual's example is shown as pseudocode written in its style, not quoted.

## Figures

- `presets-compare`, round 1 (shot `pp.scene`, the whole playground from above with the game's HUD): the four presets differed
  only in the funnel's and dominoes' shadow edges, a few pixels at the page's width. No mesh of the sample has LODs
  (`entitiesPerLOD` all 0) and its Post Process keeps reflections off, so the caption's "level of detail" and "sky's
  reflections" could not be seen.
- Round 2, published: a camera at (16, 6.5, 17) looking at the funnel and goal box (9.5, 0.8, 8), fov 40. Low (3
  cascades, 0.012 m texels near) steps the funnel's shadow in a staircase on the box's inner wall and blurs its floor edge;
  Medium is smooth; High and Ultra are sharp and alike. EV100 15.29 to 15.31 in all four: exposure unchanged. Caption and
  alt now name only the shadow; a picture of ambient occlusion, LOD or reflections changing with the preset would need a
  scene with LOD meshes and a glossy floor.
- Round 3, published (a viewer: the Low staircase was about 2 px at the column's width and the four pictures looked
  alike and unnamed): camera (15.4, 3.5, 12.8) to (11.8, 0.6, 7.8), fov 28, the goal box filling the frame under the
  funnel. Low's staircase on the box's back inner wall now has steps of about 10 px at 1280; Medium is soft, High and
  Ultra sharp. EV100 15.03 to 15.10. The caption names the order (top to bottom Low, Medium, High, Ultra), since
  ::figure prints no variant label. Page change proposed (words not mine to edit): replace the four ::figure lines by
  `::compare{id=presets-compare before=low after=medium}` and `::compare{id=presets-compare before=high after=ultra}`,
  whose sides are labelled; a crop of the back wall (rect about [0.3, 0.3, 0.67, 0.64], scale 2) could then be added
  to the recipe and shown with ::figure{crop=…}.
- `third-person-menu` (runtime) still waits for its tier.
- `graphics-page` (editor, 2026-11-18, provisional build, round 1, not published; `waitsFor` kept). The recipe asked for
  the Graphics Quality page of Project Settings beside the Scene view's chip, with a layout `layouts/graphics-quality.ini`
  that did not exist. Commands cannot show the page: Project Settings always opens on its first page, Game, and no
  command selects another (`editor.showPanel` takes only `scripts` and `search` in the provisional build too; the
  make/quality and editor-ui/settings-windows photographers found the same). The recipe now shows the half commands can
  show, which is the half the diagram above the figure speaks of: the Scene view's chips (`panel: "Viewport"`, layout
  `layouts/scene-toolbar-wide.ini`, 1280 × 720) after `viewport.setSettings {quality: "low"}`. The picture, 950 × 120 at
  its own pixels, reads at the column's width: the quality chip reads Low in orange like the chips that are on, the
  sample's project keeps the default High (its `.stproj` sets no quality). Caption, alt and shows rewritten to it.
  What the page would need for the table: a `page` parameter of `editor.showPanel` for Project Settings
  (`Renderer.Quality`), then a second figure with `"panel": "ProjectSettings"` and a layout of about 800 × 700 for the
  panel, captioned with the chips Low, Medium, High, Ultra and Custom above the table of rows by presets and the memory
  lines. The page's words beside the figure need no change.
- Pin v0.8.0 (319075e3), 2026-11-23, one hold. `presets-compare`: taken again and compared with the published files
  (`figures.py compare`): 0 of 4 differ, bit-identical originals, so `publish` left them and their 822a7a46 stamps
  (`unchanged`; it records no `checkedAt` for an identical original). Looked at again: Low's staircase on the back
  inner wall, Medium soft; the caption holds. `graphics-page`: taken without `--provisional`, round 1, published. The
  950 × 120 strip shows the Scene and Game tabs and the chips from Camera to Game camera; the quality chip, second from
  the right, reads Low, filled orange like Grid, Outline and Gizmos. Caption, alt and shows unchanged.
- `third-person-menu` (runtime) still waits for its tier.
- 2026-11-23, a viewer: Medium and High look alike at page width (only the back inner wall's edge, a few pixels, differs);
  the alt named only that wall, though every sun-shadow edge changes. Recipe: crop `wall` added, rect
  [0.3125, 0.3056, 0.5625, 0.5556] (x 400-720, y 220-400 of 1280 × 720), scale 3. Taken again (one hold): the full
  pictures are bit-identical (`unchanged`); the four 320 × 180 crops show Low's staircase, Medium's soft edge, High's and
  Ultra's sharp one. A Low-Ultra difference map shows changed edges on the floor shadow at left, the front inner wall
  and the post's shadow too: alt now says "only the shadows' edges change, most plainly on the box's back inner wall".
  The crops show on the page only with directives (words not mine to edit): after the four ::figure lines add
  `::figure{id=presets-compare variant=medium crop=wall}` and `::figure{id=presets-compare variant=high crop=wall}`
  (or all four variants), or use the ::compare pair proposed above.

## Clerk

- Fixed the tool defect the notes name: tools/lint.py's glossary names now drop the apostrophes a page's words drop, so "Players' rows" matches the page's bold.
- `graphics-page`, pin v0.8.0: `waitsFor` removed, since the pin has `editor.screenshot` with `panel` (pagecheck's
  figures check); the recipe, caption and alt are unchanged and the picture is owed to the photographer.
- `third-person-menu` (runtime), 2026-11-24, pin v0.8.0: still not taken. The runtime kind runs the exported game with
  no input, and the sample's `SettingsMenu` hides the panel in `OnCreate`; only a click on Settings opens it (and only
  then does `ShowValues` mark the preset in effect). A setup that clears the script's `Panel` field and activates the
  panel would show a panel the game did not open, with toggles the game did not set: not taken. `waitsFor` kept as the
  request for a later edition (the menu open in the exported game); `standIn` is `third-person-settings`.
- `third-person-settings` (editor, new stand-in), 2026-11-24, pin v0.8.0, round 1: the sample in play in the Game view
  (layout `layouts/make-samples-wide.ini`, 1920 × 1080), 240 fixed steps, `input.click` on `SettingsOpen`, 60 steps.
  The panel shows, but a "Scripts built" toast covered the lower right. Round 2, published: `editor.wait` of 600 frames
  added; the toast is gone. The Game view's own note "The game asked for a window with vsync on; play mode keeps the
  editor's window" stays at the bottom over the menu's hint line (the editor draws it during play), named in the alt.
  The four preset toggles stand in two rows (Low and Medium, High and Ultra), not one row; High is checked, the project's
  preset, which `ShowValues` read through `Graphics::GetPreset`. The page now introduces the picture with one paragraph
  (the panel's toggles call `SetPreset` then `Save`, `SettingsMenu.cpp`) and places the stand-in.
- `third-person-settings`, round 3 (a viewer: the note over the game's hint line reads as a glitch): the note never
  fades and no command dismisses it at the pin (`GameViewPanel::DrawGameWindowNotice` draws it for as long as play runs
  with a request, and `ApplySettings` asks for vsync at every start). The recipe now cuts the crop `view`,
  [0, 0, 1, 0.94] at scale 1, which ends above the bottom strip; the page places that crop and the alt no longer names
  the note.
