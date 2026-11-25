# Notes: make/sound

## Since

0.3.0: the audio module and its decoding appear in release 0.3.0 (plan/inventory/audio-input.md, "Release 0.3.0 line 36").

## New terms

None. The page defines audio source, listener and one-shot, which the glossary homes here.

## Requests

- Music file: the page names "a music file from the book's `tutorials/assets/` folder" but the folder holds none at this commit; the planner must supply a CC0 or CC-BY loop larger than 1 MiB with its credit.
- Figures use the editor layout `layouts/first-script.ini` (reused from make/first-script; the file is not in this worktree) and the samples ThirdPerson and PhysicsPlayground as projects, since a tutorial project is no recipe form. Selecting the clip in the Asset tab (asset-preview, impact-clip) has no setup step yet.
- (Settled by the tutorial run, 2026-11-18.) The tutorial file had empty commands in stages 1, 2 and 4; the run filled them, and the coin's edit is now the stage file `tutorials/make/sound/Coin.cpp`.
- Not every screen-changing step has its own editor picture: only the four checkpoints and the asset preview do.

## Not verified

- The Inspector labels "Min Distance", "Play On Start", "Load Mode" as spaced names (the registry names are PlayOnStart, MinDistance, LoadMode).
- The Hierarchy "+" button offering "Audio Source" (code: SceneHierarchyPanel presets, Hierarchy.Create).
- Where the Asset tab shows the Load Mode import setting.
- script.add accepts an entity id for "entity" (parameter exists; the value form was not read).
- That the ball's collision events reach a Bump script on a body made by the physics tutorial.

## Findings not applied

- critic-make-a-28 (export page and project-coin-run steps): they name other pages.

## Clerk

- No term or word asked.
- Left for the planner: the music file, the layout and figure setup, the empty stages.
- The build's checkpoint rule: "How a game makes sound" moved before "## What you need"; "What Strata does not do here" became a ### section of the last step section, before its checkpoint.

## Figures

- result (scene, published): round 1 with `camera: "scene"` and no scene opened the sample's start scene, the Sky Islands main menu, not the course. Round 2 added `scene: Scenes/Course.stscene`: the follow camera shows the character from behind on the first island, the coins standing in a line along the course ahead and the counter at 0 / 12. Round 3 tried a fixed camera at (3.5, 2.2, 3) toward (0, 0.8, -2.5) to put a coin beside the character; in play mode it framed a sign and flowers with no character, so the round-2 recipe was taken again and published. Caption, alt and shows now say "coins in a line ahead of the character" (the old alt's "beside a gold coin" and "stone course" were not what the picture shows). The caption's sound clause is the page's result, which no picture can show.
- result, mend round 1: a viewer found the Third Person course the wrong game (the page builds Coin Run) and its coins edge-on posts. The recipe now builds Coin Run on the basic3d template as physics.json's result does (its Ball and Gold materials): the ball dropped from (-0.9, 3, 0.6) and the five coins at CoinPlacer's c_CoinPositions (make/scripting-scene) as kinematic triggers, faces along +Z, camera (0, 2.8, 9) toward (0, 0.7, 0.8), fov 40, 120 steps. The picture shows the ball at rest and five gold discs face-on on a half circle; the ghost wall is left out because at (4, 1, 0) it would hide the fifth coin. Caption, alt and shows rewritten to match.
- Editor figures, settled with the provisional build (2026-11-18, two rounds, nothing published; every recipe keeps `waitsFor: tier 2: editor screenshot`). first-script.ini's 256 px Inspector cut labels, so two layouts were made from first-game-tall.ini: `layouts/make-sound.ini` (1280 × 800, Inspector column 380 px, bottom tabs 300 px) and `layouts/make-sound-short.ini` (1280 × 540, the same columns). Each recipe pictures one panel (`editorWindow.panel`).
  - asset-preview: the recipe had no step selecting the clip; it now runs `selection.set {asset: Sounds/Coin.ogg}` on the ThirdPerson copy. The Asset tab shows Load Mode Decompressed, Play, 0:00.3 · 44100 Hz · mono and the orange waveform. Round 1 at 1280 × 800 left half the panel empty; round 2 uses make-sound-short.ini. The page still has no `::figure{id=asset-preview}` line (step 1 of the first section would be its place).
  - inspector-source: Hum's Audio Source reads at 380 px: Clip Coin, Volume 1, Pitch 1, Loop, Play On Start and Spatial ticked, Min Distance 1, Max Distance 50, Rolloff 1, which also matches step 2's "You should see". Round 1 passed.
  - coin-console: round 0 played the ThirdPerson start scene for 60 steps and collected nothing, so "no warning" said nothing. The recipe now opens Scenes/Course.stscene and plays 240 steps holding W: the sample's CourseState requests its coin clip in OnCreate and plays it with PlayOneShotAt, as the page's Coin does, and the Console shows "coin 1 of 12", "coin 2 of 12" and no audio warning. Caption, alt and shows now name the Third Person sample, because the page's Coin edit is pseudocode and no tutorial file holds it; with a stage file of the edited Coin.cpp the figure could play Coin Run itself. Above the visible lines the Console holds two import warnings for the robot model and "scripts not built yet"; none is about sound. The App lines of the take's commands (play.start, input.sequence, editor.wait) show too, cut at the right edge.
  - impact-clip: selects Sounds/Impacts/Soft.ogg on the PhysicsPlayground copy: 0:00.1, stereo, a few large swings dying to a flat line, which the caption's "starts loud and dies away" states. Round 2 on make-sound-short.ini.
  - music-source: the Inspector shows Loop and Play On Start ticked and Spatial clear. The clip is Coin.ogg, standing in for the music file the book does not have yet (see Requests); the caption and alt do not name the clip, the shows says it stands in. With a music file under tutorials/assets/ the recipe should copy it (files) and set it as Clip.
- Editor figures, mend after a viewer's review (2026-11-18, provisional build, nothing published; `waitsFor` kept):
  - asset-preview: the viewer found the picture good but unreachable: the page has no `::figure{id=asset-preview}` line. Adding it is the page's text, which a photographer does not edit; the recipe stays. Request for the writer: put `::figure{id=asset-preview}` after step 1's "If you do not see it" paragraph of "Hear your first sounds" (line 103 today), the step that describes this panel (Asset tab, Play under Preview, waveform).
  - coin-console: the viewer counted five automation replies among twelve rows. Each step of the take's command script is logged at Info by the editor's command runner (EditorCommandRunner.cpp, `{} -> {}`), and the Console has no source filter that a command can set (editor.showPanel's search is the Hierarchy's only), so the full panel always ends with them. Round 1: the recipe's own editor.showPanel step (a duplicate of the one `panel` adds) is gone, one reply fewer; the recipe gains the crop `log`, [0, 0.3433, 1, 0.76] of the 673 × 300 panel, the rows from "Loaded script module 'ThirdPersonScripts'" to "coin 2 of 12". The crop still holds one reply, play.start's, because the runner logs it after the course script's "course loaded" line and before the coins; no recipe can move it. The page shows the crop only with `::figure{id=coin-console crop=log}` (a writer's change, requested here); until then the alt describes the full panel and says the replies are there. With crop=log in the page, the alt's second sentence becomes "One reply of the editor's command script, cut at the right edge, stands before the coin lines."
  - music-source: the caption now says "The clip shown, Coin, stands in for your music file." and the alt names the clip Coin. No retake: the picture is unchanged; tutorials/assets/ still holds no music file.
- Settled 2026-11-18 (page words): no music file exists in the release or the book, so the music step uses ThirdPerson's `Sounds/Complete.ogg` (Kenney, CC0) as a stand-in tune, imported into `Sounds/Music`; the page places `::figure{id=asset-preview}` in step 1 of the first section and `::figure{id=coin-console crop=log}` (alt changed as asked). For the photographer: music-source's recipe may set its clip to `Sounds/Complete.ogg` (the ThirdPerson copy has it); the caption now names the tune Complete and says Coin stands in for it.
- Taken at the pin v0.8.0 (319075e3, 2026-11-23, one hold, one round; all published). `check` asked for the five `waitsFor: tier 2: editor screenshot` lines to go: removed.
  - result: retaken and compared with the published file (figures.py compare): 0 differing pixels, so the published `result.avif` stays as it was (publish: unchanged; its stamp keeps pin 822a7a46).
  - asset-preview, inspector-source, impact-clip: the same panels as the provisional takes; every value the shows and alt name is in the picture.
  - coin-console: the crop `log` holds the rows from "Loaded script module 'ThirdPersonScripts'" to "coin 2 of 12", with play.start's reply between "course loaded (12 coins)" and the coins, as the alt says; the alt now names the Strata line too. The full panel shows the take's project path (the work folder, no user name) on a build line above the crop.
  - music-source: the recipe now sets the clip to `Sounds/Complete.ogg`, so the Inspector shows Complete; caption, alt and shows no longer say that Coin stands in.

## Tutorial run

2026-11-18, three rounds, pin build Release; both files pass and are stamped.

- The file was thinner than the page: stages 1, 2 and 4 had no commands. It now imports the three clips from `@RELEASE@`, creates Hum and checks the source's defaults (Play On Start, Volume 1, Pitch 1, Spatial, Min 1, Max 50, Rolloff 1), plays and checks the looping voice in `audio.state`, moves Hum to (0, 0.5, 30) and sets Max Distance 5, Rolloff 3, moves the listener to the Ball (listener position (0, y, 0), not the camera's (0, 16, 13)) and deletes Hum. Stage 2 copies the edited `Coin.cpp`, rolls the ball into the coin at (0, 0.8, 3) with S for 150 steps (oneShots played 1, dropped 0), then plays `CoinNoRequest.cpp` (no drop at the pin: the short clip loads within 0.25 s, as the page says may happen) and restores `Coin.cpp`. Stage 3 adds the import, `script.create`, the Bump build, `script.add` and a 120-step fall (one thud, none dropped). Stage 4 checks Load Mode Decompressed then Streamed, the Music voice (looping, not spatial), `VolumeKeys.cpp` (Minus 1 to 0.9, two Equal to 1.1) and that the next play starts at master volume 1 again.
- Round 1: a check compared with `{"$ref": "ball"}`; checks take no `$ref`, so the listener is checked by position. Round 2: `asset.setImportSettings` answers `importSettings`, not `settings`.
- Page: the coin is destroyed, not hidden (the physics page's Coin calls `Destroy`), and the one-shot line goes in braces with it; the command tabs of stage 1 step 4 and 5, stage 2 steps 3 and 4, stage 3 steps 1 and 2 and stage 4 steps 1 and 2 now carry the commands the file runs. Prose trimmed to stay within size M (3,997 words).
- 2026-11-24, track G walk segment 5 (WK12, WK16): the tabs pass entity IDs, not `entityName`; `VolumeKeys.cpp` is
  quoted whole. The file was not changed. Passed with the pin build and the 0.8.0 package.

## Engine

Nothing found: every command did what its description says.
