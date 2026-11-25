# Notes: make/hud

## New terms

None proposed. The terms nine-slice, scale mode, canvas and reference resolution are the glossary's.

## Since

0.4.0: `Docs/Releases/0.4.0.md:52` lists the Game UI (canvases, rects, anchors, HUDs) as new in that release.

## Requests

- Extra word: `HUD` (22 uses; expanded once as "heads-up display (HUD)"). Glossary homes `hud` elsewhere or the word list should admit it.
- Figure layout file `layouts/hud.ini` for the four editor figures (canvas-2d, corner-texts, panel-and-bar, hud-playing); made by the photographer on 2026-11-18.
- Tutorial stage 1 to 4 start from the end state of `make/sound`; `button_square_flat.png` is imported in stage 1's setup (into `UI/`), as "What you need" asks.

## Tutorial run

- 2026-11-18, pin build (Release): the tutorial and exercise 1 passed as written in round 1, but the file was thinner
  than the page. Round 2 passed with the page's own values added: stage 1 imports `button_square_flat.png` in setup,
  sets canvas mode and checks the reference resolution, the pivot, and the rects at 1280 by 720 (16, 16, 240, 32; the
  timer at x 1024); stage 2 makes the backdrop Sliced with the texture and borders 12, checks it draws first, that the
  band is hit before Receives Input is cleared and not after, and the bar's 40 and 1840 at 1920 by 1080; stage 3 runs
  `script.create` then `script.build` as the tab does and, after 90 fixed steps, reads `Coins left: 5`, `Time: 59` and
  a fill of 0.975; stage 4 sets the three Game view modes, checks the table's margins at 4:3 (20.8) and 21:9 (27.5) and
  the bar's 40 units, and creates `StartSign` with the page's Euler rotation (-55, 0, 0), read back as the quaternion
  (-0.4617, 0, 0, 0.887). Exercise 1 checks the timer's middle at 4:3 and 21:9.
- Verified by the run: the coins carry the tag `Coin` (five, placed by `CoinPlacer`); the 21:9 canvas measures 2200 by
  943 units, as the table says; the enum strings `Left`, `Right`, `Center`, `Sliced`, `Filled`; `/entity` of
  `ui.create` and `/entities/0` of `entity.find`.

- 2026-11-24, final runs at pin 319075e3: exercise 1 passed with the pin build (Release); the tutorial and exercise 1
  passed as written with the official v0.8.0 package (`Strata-0.8.0-windows-x64.zip`). The tutorial's pin-build run
  of 2026-11-23 stayed current.

## Track walk G, final, segment 6 (2026-11-24)

Answers to `plan/walks/G-final-6.md`, WK1 to WK6:

- WK1: the Sound checkpoint's scene holds no coin in edit mode (`CoinPlacer` makes them during play; the tag comes from
  `Prefabs/Coin.stprefab`, whose root carries `Tag: Coin`). What you need now has a coin item that checks the tag during
  play.
- WK2: the import names its folder (`UI`, as the tutorial file's setup imports it) and gives `asset.import` with
  `directory`.
- WK3: canvas mode shows the selection's canvas through the scene's camera (`viewport.setSettings` description,
  `StrataEditor/src/Editor/EditorViewportCommands.cpp:1132`), drawn by the Scene view's panel only; `viewport.capture`
  renders the editor camera. The tab now selects `HUD` (`selection.set`) and sets `gameUI` too, as the editor tab's two
  chips do; the file runs and checks both. "You should see" now says what the figure `canvas-2d` shows: the level
  through the game's camera in a 16:9 rectangle between dark bands, no element yet.
- WK4: the listing starts at line 1 (a fence of lines 1-8, then 9-32), and both tabs say to replace the file's text in a
  text editor (no command writes it) and that checkpoint 3's zip holds the whole file.
- WK5: the tab adds the four `ui.layout` calls the file already ran, and says what they answer; `gameView.mode` changes
  only the window's picture, and its answer's `width` and `height` belong to the mode `custom`.
- WK6: the play step's tab rolls the ball (`play.start` paused, `input.sequence` S for 150 steps over 180, then
  `play.step` 2910 to 51.5 s), and the editor tab names the key. The file runs it and checks `Coins left: 4`,
  `Time: 58` after 180 steps (the frame's `OnUpdate` reads the time before its fixed step, 179 steps), the fill 0.95,
  and `Time: 9` in red (1, 0.3, 0.2) at 3090 steps. Stage 3's old 90-step play, which the page did not show, went.
- To stay within size M (4,000 words) the page lost the Backdrop step's Why (its "If you do not see it" says the same),
  the list of the SDK's types in the note, a sentence on clicks in the corner and the 2D view's outline sentence.
- Runs, 2026-11-24: the tutorial and exercise 1 pass with the pin build (Release, round 2; round 1 expected `Time: 57`)
  and with the official v0.8.0 package.

## Engine

- None found: every command did what its description says.

## Not verified

- That the coins at the end of `make/sound` carry the tag `Coin` (the brief says so; the page tells the reader to check the Tag component).
- That `button_square_flat.png` (64 by 64) suits Slice Borders of 12: the ThirdPerson sample uses 12 on its panel texture, not read back to this file.
- The pixel sizes of the Game view's 4:3 and 21:9 modes: the table uses 1440 by 1080 and 2520 by 1080 as examples; scales are computed from `GameUIScene::ComputeScale`.
- That a text turned by the camera's own rotation faces the camera (derived from the +Z rule in `RendererComponents.h`); the camera rotation (-55 on X) is the one proposed by critic-make-a-19 for `make/project-coin-run`.
- The command results' pointers (`/entity` of `ui.create`, `/entities/0/id` of `entity.find`) and the string form of enum values (`Alignment`, `Type`) in the tutorial file: not run.

## Findings not applied

- critic-make-a-19 (camera framing): belongs to `make/scenes-entities` and `make/project-coin-run`; the page only names the rotation as an example in step 9.
- critic-make-a-29 (planted bug in `make/play-test-debug`): not this page's; `CoinHud` counts in `OnUpdate`, as the finding says.
- Applied: critic-make-a-6 (the note on `SetProperty` types), -7 (Create Child), -8 (Position tick, Left and Right margins), -9 (Screen Space cleared, Font Size 1, rotation, `Text` as the name).

## Clerk

- Admitted to extra-words.txt: HUD and HUDs (G0 has 5); asked by this page and make/project-coin-run.
- Left for the planner: `layouts/hud.ini`, the tutorial's start.

## Figures

- `result`, `screen-4x3`, `screen-21x9` (scene): taken in round 1 (basic3d template, scene camera) and published as
  the recipes stood. The 70 % fill (42 of 60 seconds) ends the bar at about two thirds of the width, so only its left
  margin shows; the captions and alt texts now say so. Measured margins match the page's table: the bar starts at
  27, 35 and 46 pixels (40 units at scales 0.667, 0.866 and 1.146).
- `screen-4x3` is in the manifest but no `::figure{id=screen-4x3}` places it on the page.
- Step 1 of "Check every screen" promises "the bar along the bottom with equal margins". After the tutorial's Fill Amount
  of 0.6, the right margin is not visible: only a full bar shows equal margins.
- Round 2 (viewer's report): `result`, `screen-4x3` and `screen-21x9` drew `Backdrop` as a dark navy plain panel
  (Color 0.1, 0.12, 0.18, 0.85), while step 1 builds it Sliced with `button_square_flat`, Slice Borders 12 and Color
  white. The recipes now import `Samples/ThirdPerson/Assets/UI/button_square_flat.png` into `UI/` and set the page's
  values. The band is now light grey with a thin grey rim. The white texts on it are faint: to make them readable, the
  page's step 1 would need a darker tint (for example Color 0.1, 0.12, 0.18, 0.85 on the sliced image) or darker texts.
  The editor figure `panel-and-bar` and `hud-playing` still carry the dark plain color (not mine to take).
- Placement, for the writer: `screen-4x3` still has no `::figure` on the page, and `screen-21x9` stands alone after
  checkpoint 4. Both belong after the table of "Check every screen" (a `::compare` of the two) or after its step 1.
- Editor figures `canvas-2d`, `corner-texts`, `panel-and-bar`, `hud-playing`: settled with the provisional build
  (2026-11-18, two rounds), not published; each keeps `waitsFor: tier 2: editor screenshot`. They picture one panel
  at its own pixels in `layouts/hud.ini` (new: `layouts/first-game.ini` made 1280 by 800, the Scene view 797 by 600,
  so the 16:9 canvas shows between dark bands). Round 1 in `first-game.ini` filled the view with the canvas, so its
  edges did not show; the Game UI chip was off, now `gameUI: true` beside `canvasMode` as step 2 asks.
  - `canvas-2d`: the state of step 2 (only `HUD`, selected), not the texts the old recipe made.
  - `corner-texts`: tutorial stage 1 (`Coins left: 5`, `Time: 60`, not the old 3 and 42), `CoinText` selected; the
    Scene view, not the whole window: the Inspector would not read at the column's width.
  - `panel-and-bar`: stage 2 as the page's step 1 builds it (Sliced `button_square_flat`, borders 12, white; Fill
    Amount 0.6), not the old dark plain panel and 0.7; `TimeBar` selected. The band has no side margins (Left and
    Right 0), so the caption no longer says "each with margins".
  - `hud-playing`: the Game view after stage 3's `CoinHud.cpp` (`files: [{"stage": 3}]`), `script.build`,
    `script.add`, and 1080 fixed steps of paused play: `Time: 43`, bar at seven tenths. The coins of `make/sound`
    are not in the basic3d copy: five entities with only the tag `Coin` stand in, so the count reads 5.
- For the writer: in the editor pictures too, the white texts on the light band of step 1 are faint (enlarged:
  barely readable), while the section says the panel makes the texts easier to read. A dark tint on the sliced
  image (Color 0.1, 0.12, 0.18, 0.85) or dark texts would make it true; the recipes would follow.
- For the writer: `tutorials/make/hud.tutorial.json` stage 2 still sets the dark plain Color and Fill Amount 0.7,
  while the page's step 1 and step 3 say Sliced white and 0.6.
- Round 3 (viewer's report on the provisional editor pictures, 2026-11-18):
  - `panel-and-bar` and `hud-playing`, faint texts on the light band: the fault stands, but the recipes picture the
    page's step 1 as written (`Color` white on `button_square_flat`, lines 215 and 222), so a dark band would contradict
    the step the figure shows. No retake. Writer: give step 1 (both tabs) a dark tint, for example `Color` (0.1, 0.1,
    0.12, 0.8), or drop "Text over a bright level can be hard to read" as the panel's reason. Once the step changes,
    the five recipes that build `Backdrop` (`result`, `panel-and-bar`, `hud-playing`, `screen-4x3`, `screen-21x9`)
    take the same `Color` and are retaken together, so the published scene pictures and the editor pictures agree;
    alt and shows then say "dark band" instead of "light grey" and "faint".
  - `hud-playing`, no ball and no coins: the book cannot build Coin Run's project for a figure. A recipe's project is
    a template, a sample or a lab (`labs/` has none), and `files: [{"stage": n}]` copies only this page's tutorial
    files; the scene of the end of `make/sound` comes from eleven chained tutorials (about 180 commands with their
    assets). Caption, alt and shows now say that the picture is a bare scene where five entities tagged `Coin` stand
    in for the coins. A Coin Run picture needs a lab that replays the chain (`labs/coin-run.json`), for the planner.
- Pin v0.8.0 (319075e3, 2026-11-23), one hold for all seven, hud-playing retaken alone:
  - The five recipes that build `Backdrop` now take step 1's Color (0.1, 0.12, 0.18, 0.85): the band is dark blue gray
    and the white texts read on it; alt and shows say so. Compared with the pictures published at 822a7a46, the three
    scene pictures differ (mean 12.7 to 16.7 of 255) only by that band, and by the next change.
  - `screen-4x3` and `screen-21x9` show Fill Amount 0.6 and `Time: 36` (was 0.7 and 42), as the paragraph before
    `screen-4x3` speaks of 0.6. Measured: the bar starts at 35 and 46 px and fills three fifths. `result` keeps 0.7
    and `Time: 42` (the script's state at 42 of 60 seconds).
  - Editor figures published, `waitsFor` removed (the pin has `editor.screenshot`). `hud-playing`'s
    `files: [{"stage": 3}]` copied no file (stage 3 attaches `CoinHud.cpp` to its `script.build` step), so
    `script.add` found no `CoinHud`: the recipe now copies `book:tutorials/make/hud/CoinHud.cpp` itself. Picture:
    `Time: 43`, bar 533 of 762 px.

## Settled with the editor (2026-11-18)

- Step 1 now tints the sliced `button_square_flat` band dark blue gray (Color 0.1, 0.12, 0.18, alpha 0.85) in both tabs, so the white texts read on it, and its You should see says "dark band". For the photographers: the five recipes that build `Backdrop` (`result`, `panel-and-bar`, `hud-playing`, `screen-4x3`, `screen-21x9`) should take this Color and be retaken; their alts then say a dark band, not a light grey one with faint texts.
- Tutorial stage 2 sets and checks Fill Amount 0.6, as step 3 says. Its `Backdrop` keeps the plain dark Color without the texture, since the stage imports nothing (see Requests).

## Figures mended (2026-11-23)

- `result`: a viewer found the opening picture bare (the HUD over an empty floor, no ball, no coins). The recipe now
  places a grey metal ball and three gold coins (built-in sphere and cylinders, stand-ins for the Coin Run stage, which
  no figure project can load) in front of the template's scene camera; caption, alt and shows name them. A custom
  camera was tried first and dropped: with it the capture draws no game UI, so the recipe keeps `camera: "scene"`.
