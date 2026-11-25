# Notes: make/quality

## New terms

None proposed. Defined on the page: anti-aliasing, Graphics Quality preset (the brief's glossary homes), and in passing FXAA, TAA and toggle group.

## Since

0.7.0: Graphics Quality and the players' options arrived in 0.7.0 (Docs/Manual/Graphics.md, SDK Graphics.h comment "before 0.7.0 return nothing").

## Requests

- A generated presets table (W8r, no number beside a preset name): the page's table is qualitative, so the section needs the generated one with memory and GPU time rows.
- A figure layout `layouts/make-quality.ini` for the `graphics-page` figure (waits for tier 2: editor screenshot).
- Further reading entries cite the manual and a general source without links.

## Movable claims

Reviewed at v0.8.0 (319075e3) against `Docs/Releases/0.8.0.md` ("What High and Ultra draw", "Many lamps with shadows").

- Lamps with shadows 4, 16, 64, 256 by preset (table), 64 and 256 new in 0.8.0:
  `Strata/src/Strata/Renderer/RendererQuality.cpp:45`.
- Lamp shadows drawn each frame 12, 12, 24, 48 by preset (table), the row new in 0.8.0:
  `Strata/src/Strata/Renderer/RendererQuality.cpp:46`.
- Ultra's larger lamp tiles (2048 against 1024): `Strata/src/Strata/Renderer/RendererQuality.cpp:42`.
- Sun shadow row: 1024 with three cascades, 2048 with four, `AutoFine` with five, 8192 with five:
  `Strata/src/Strata/Renderer/RendererQuality.cpp:39-40`.
- Reflections Off, Checkerboard (half resolution), Spatial, SpatialHigh: `Strata/src/Strata/Renderer/RendererQuality.cpp:55`.
- Global illumination Off, Off, High, High: `Strata/src/Strata/Renderer/RendererQuality.cpp:57`.
- Five players' rows that no preset changes: `Strata/src/Strata/Renderer/RendererQuality.cpp:181-185`.
- TAA's eight jitter positions: `Strata/src/Strata/Renderer/SceneRenderer.h:247`.
- Sharp is the default TAA preset: `Strata/src/Strata/Renderer/RendererComponents.h:339`.
- The log line `Graphics quality: Low (--quality)`: `Strata/src/Strata/Runtime/GameRenderer.cpp:86-89`.
- No render scale: `Docs/Manual/Graphics.md`, "Why there is no render scale".

## Not verified

- The Physics Playground scene has an entity named Post Process (checked in its scene file); the Coin Run project's Post Process entity name was not checked.
- Commands `ui.create` with `"type": "toggle"` and `script.setField` for the toggle row: names exist, parameters were not checked.
- The `component.set` and `project.setSettings` parameter shapes follow the manual's examples.
- The exported game's `--quality` log line text was taken from the inventory (`Graphics quality: <preset> (<source>)`), the source word `command line` was not checked.
- That toggle groups need the toggles to share a group is described only as make/menus teaches it.
- That Graphics::Save returns false when the game has nowhere to keep files: from the SDK comment.

## Findings not applied

- The brief's SettingsMenu.cpp lines 26-39 are lines 28-36 at the pin; quoted by symbol.
- The brief's open findings list was not present as separate rows beyond the three not-done items, which the page carries (no command sets options; no MSAA or supersampling; sRGB only).

## Clerk

- No term or word asked.
- Left for the planner: the generated presets table, `layouts/make-quality.ini`.

## Figures

- `aa-compare` (published, round 2). Round 1, the recipe's wide view from (0, 6, 14) at fov 60 and 1280 x 720: FXAA and TAA alike at page width, even enlarged. Round 2: camera (-1, 3, -3) toward the crate pyramid (-9, 2, -12), fov 35, 960 x 540, so the crates' outlines against the sky and the seams between crates fill the frame at larger pixels; FXAA leaves them slightly harder and stepped, TAA smoother and a little softer. The difference stays small in a still frame, as step 3 of the page says; the caption says so.
- `quality-compare` (published, round 3). Round 1, `showcase.shot2`: High differs from Low mainly by its screen-space reflections on the asphalt; shadow edges alike at that size. Round 2, a wide view toward the tyre stack: same, and the Low take was nondeterministic (3943 channels off by 1), so it was retaken alone. Round 3: camera (14.5, 1.6, -12.5) toward the rocks on the sand slope, fov 14: the large rock's long shadow is blurred with a rounded tip at Low (1024-texel, 3 cascades) and crisp with a sharp tip at High, and only High reflects in the puddles. Deterministic. The caption names both; "far detail" (the level of detail error) shows no visible difference and was dropped from the caption.
- `graphics-page`: waits for tier 2 (editor screenshot); not taken.
- `graphics-page` (editor, 2026-11-18): cannot, recipe left as written, `waitsFor` kept, not taken. The Project
  Settings panel always opens on its first page, Game (`SettingsBrowser` lists Game, then Export, then the settings
  sections, and falls back to the first entry: `StrataEditor/src/UI/SettingsPages.cpp:456` and `:497`). The page it
  shows is not saved in the layout, and no command selects another page. `editor.showPanel` takes no page in the
  provisional build either (its description names only `scripts` and `search`), and `editor.showDialog` opens only
  Preferences at a section, not Project Settings. `ProjectSettingsPanel::Select` is called by nothing, and the
  "Graphics Quality..." links (Inspector, Scene view) need a click. The make/export photographer's provisional take of
  the same panel showed the Game page, so a take here would picture the Game page, not the caption's chips and table.
  What the page gets: nothing until a command selects a Project Settings page. Then the recipe needs that step (page
  `Renderer.Quality`), `"panel": "ProjectSettings"` so the panel reads at its own pixels, and a layout of about
  800 × 700 for the panel (`first-game.ini` docks it at about 800 × 500, which may cut the table's lower rows), in
  place of the missing `layouts/make-quality.ini`. The caption's words match the source: chips Low, Medium, High,
  Ultra and Custom above a table with one column per preset (`StrataEditor/src/UI/GraphicsQualityPage.cpp:44`).
  Nearest honest picture meanwhile: none; the page's steps already name the page's controls in bold.
- `aa-compare`, round 3 (a viewer's faults). Outlines against the sky look the same under FXAA and TAA; the difference is in the thin vertical seams between the pyramid's crates (crisp dark and light lines with light specks along the tiers' edges under FXAA, faint under TAA), about one pixel wide, so the full frames look alike at page size (mean difference 1.7 of 255). Caption, alt and shows now name the seams and drop "against the sky" and "stepped". The recipe gained the crop `seams` ([0.396, 0.352, 0.729, 0.778] of the frame, x 380-700, y 190-420, scale 3), taken and published; the full frames are unchanged (same bytes). The page does not show the crop yet: it needs `::figure{id=aa-compare variant=fxaa crop=seams}` and `::figure{id=aa-compare variant=taa crop=seams}` after the two full frames (a writer's change; this pass edits no page text), and the caption could then say "enlarged below".
- `quality-compare`, words only (a viewer's faults). The High puddles do not mirror the sky: the two left puddles turn pale and the near one mirrors the sand slope; the sunlit right puddle stays orange in both. The near asphalt's shadow also differs (Low: a dark band across the whole bottom; High: only the lower left, the asphalt below the right puddle lit), and High shows faint orange streaks of the sunlit sand along the asphalt's far edge. Caption and alt now say all of this; the picture is unchanged.
- `graphics-page` (pin move to v0.8.0): `waitsFor` removed, since the pin has `editor.screenshot` (figures.py asks
  for it). `editor.showPanel` at the pin still takes only a panel, so a take may still show the Game page; check the
  take against the caption before publishing.
- Pin v0.8.0 (319075e3), 2026-11-23. `aa-compare` and `quality-compare` taken again at the pin build: `compare`
  finds all four frames identical to the published originals (0 differing pixels), and both crops too; `publish`
  leaves the six files and their stamps as they are (`unchanged`: same original). Looked at again: the seams crop
  still shows crisp seams with light dots under FXAA and faint ones under TAA; Low and High still differ in the rock's
  shadow tip, the near asphalt's shadow and the puddles, as the captions say. Nothing changed in the recipes.
- `graphics-page` at v0.8.0: blocked, not taken, recipe left. `editor.showPanel` still takes only `panel`, `scripts`
  and `search` (`StrataEditor/src/EditorLayer.cpp:288-292`); `EditorLayer::ShowProjectSettings(page)` is reached only
  from clicks (Inspector `InspectorPanel.cpp:1528`, Scene view `ViewportPanel.cpp:752`, Export dialog), and the
  selected page is not kept in the layout. A take would show the Game page, not the caption's preset chips and table.
  What the page needs: a command (or an `editor.showPanel` parameter) that opens Project Settings at a page; then the
  recipe gains it (page `Renderer.Quality`), `"panel": "ProjectSettings"`, and a layout `layouts/make-quality.ini`
  of about 800 x 700 for the panel. Nearest honest picture meanwhile: none; step 1 names the page's controls in bold.
- `graphics-page`, last pass (2026-11-24, pin 319075e3): checked again, still no command selects a Project Settings
  page (`editor.showPanel` at `StrataEditor/src/EditorLayer.cpp:275-292`), so not taken. The entry is `blocked` with
  that reason (the request for a later edition) and names `standIn` `graphics-page-drawing`, a new `diagram`: the five
  chips with High chosen, and five of the table's sixteen cost rows (Shadow cascades, Shadowed point and spot lights,
  Ambient occlusion quality, Screen-space reflections, Global illumination) with their values at the pin, the High
  column tinted and the Custom column drawn as fields showing High's values in secondary text, as
  `GraphicsQualityPage.cpp:389-476` draws them; a note says that editing a Custom cell switches to Custom (Variations).
  Rows chosen to avoid the shadow resolution cell, whose Custom widget text was not read. Memory, GPU line, player
  banner and Reset to Defaults are left out of the drawing; the caption says "some of its rows". The page places the
  drawing in the old figure's place, after a new lead-in sentence that refers to step 5.

## Tutorial run

Added after walk G-final-9 (2026-11-24): `tutorials/make/quality.tutorial.json` starts from `make/menus` (the project
of its Checkpoint 7) and runs the page's command tabs: anti-aliasing Morphological, then TAA Original, on the course's
`Post Process`; `project.settings` and `project.setSettings` of `Renderer.Quality` (Low, then High); the Scene view's
quality `ultra` and back to `project`; in `MainMenu` the row `GraphicsRow` in `SettingsColumn` with four toggles
(group `GraphicsRow`, event target `SettingsPanel`, off); the page's `tutorials/make/quality/SettingsMenu.cpp` (the
Menus script with the four fields, `GetGraphicsPreset` and the preset shown in `OnCreate`) copied at the stage's start;
the build, the four fields, `prefab.apply` and a play that checks `GraphicsHigh` on at the start and `GraphicsLow` on,
`GraphicsHigh` off after a click; `graphics.resetPlayerOptions` answers one choice, then none. Passed with the pin
build and the v0.8.0 package. The page's step 3 capture and the `--quality` run of step 7 are not in the file (a
capture needs the GPU, step 7 an exported game).
