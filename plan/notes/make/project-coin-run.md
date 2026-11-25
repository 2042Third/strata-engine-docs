# Notes: make/project-coin-run

## Since

0.3.0: the gameplay API (`Game::ReloadScene`, `Time::SetTimeScale`, `SetActive`) and the export exist in the first release line the book covers (inventory scripting and gamedev rows of this brief).

## New terms

None.

## Requests

- Words for `tools/data/extra-words.txt`: "HUD" (the acronym; the page spells "heads-up display (HUD)" at first use; the hud page needs it too) and "restart" (a verb of `verbs.txt`, used for the Restart action and the idea). The lint's `word-list` fails on both and on "HUDs" in a link text.
- Figures: `result`, `win-panel` and `polished` are scene recipes on the Basic 3D template with a HUD and panels built by commands (no coins, no ball); `round-playing` reuses `layouts/hud.ini` of the hud page; `exported` is a runtime picture of the Basic 3D template, not of the finished Coin Run, because a tutorial project is no recipe form.
- The tutorial file has `startsFrom` `make/export`. Stage 1 adds the entity `Game`, removes `CoinHud` from `HUD`, and ships `CoinRunGame.step1.cpp`; stage 2 ships `step2`; stage 3 the final file; stage 4 has commands only. The sound import path in stage 2 is the release folder placeholder, as on the sound page.
- The Basic exercise's solution file is `exercise-1/CoinRunGame.cpp` (a copy of the final script with the `BigCoin` score); its tutorial file creates `ScoreText`, a coin tagged `BigCoin` and builds.
- The page leaves `Scripts/CoinHud.cpp` in the project (unused class); a later tutorial stage could delete it if the integrator wants.

## Not verified

- The Hierarchy's menu path for an empty entity (the page says "choose the empty entity"; code: preset "Empty"/"Entity").
- Removing a script component through the Inspector's component menu with **Remove**.
- That a kinematic body follows its entity's transform written in `OnFixedUpdate` and reports `OnCollisionEnter` for the ball.
- That a new scene made by `Game::ReloadScene` starts at time scale 1 (the script sets it itself).
- The coin prefab's script fields (`DegreesPerSecond`, `BobHeight`) on the root of `Prefabs/Coin.stprefab` and the Inspector's **Apply to Prefab** entry for a script field.
- The earlier pages' final state (names `Ball`, `HUD`, `CoinText`, `TimerText`, `TimeBar`, the tag `Coin`, `Prefabs/Coin.stprefab`) comes from their pages, not from the engine.
- The music file's source and license: the page gives a table row with placeholders.
- Whether `Gamepad/Start` and `Key/Enter` are free in the project's Gameplay map (they are valid binding names at the pin).

## Findings not applied

- critic-make-a-2: applied with the coin's glow already made on scripting-scene; this page adds no glow (nothing to add).
- critic-make-a-4, -7, -11, -12, -13, -19, -28: applied (hidden panel found by name; panels by **Create Child**; velocities zeroed in the Hard solution; coin values set through a placed instance, applied, then deleted; time owned by `CoinRunGame` and the freeze by `Time::SetTimeScale`, `BigCoin` second tag; camera only checked; `Sounds` folder kept by Always Include and the `FindAsset` warning read).
- The brief's "version 1.0.0 on the Game page" and "pruned export with Always Include": the export page already did both, so this page checks them and keeps `Complete.ogg` through the `Sounds` folder.
- The brief's Basic exercise (`Points` field on the prefab, summed in the HUD) is replaced by the `BigCoin` tag, as finding critic-make-a-13 proposes (`GetScript` is not taught yet).

## Clerk

- Admitted to extra-words.txt: HUD, HUDs (G0 has 5), restart (G0 has 1).
- Left for the planner: the figures, the stages and the leftover CoinHud.cpp.
- The build's tab rules: the three systems' set is `sync=os`; the two sets of one tab became plain step text.

## Tutorial run

- 2026-11-18, pin Release, four rounds; the chain through make/export replays clean. Stages 1 and 2 pass; stage 3
  passes up to the coin's delete (difficulties, colors, `prefab.apply`) and stage 4 and exercise 1 were not reached. Round 4 stopped on the file's own check
  of `entity.delete`: it answers `count` 2 for the coin instance (its root and a child; `deleted` lists the one root).
  The check now asks `deleted` length 1 and `count` 2, as the engine answered.
- 2026-11-23, rounds 5 and 6: every stage and exercise 1 pass in the session; the reader copies of stage 2 and the
  exercise failed in part 2, which starts a fresh editor on the saved project, so the panels, `ScoreText` and the big
  coin made before the build were gone (`entity.find` empty). Each build that carries a file now follows a
  `scene.save`, in the file and in the page's tabs (stage 1 step 3, stage 2 step 4, stage 3 step 2: **Ctrl+S**).
- Mended in the page: the Sound page already made an entity `Game` (for `VolumeKeys`), so step 1 finds it instead of
  making a second `Game`; every tab names entities by `<Name id>` (entity and parent parameters take IDs only:
  `ui.create` refused `"parent": "HUD"`); stage 2's tab now makes `WinHint`, sets both font sizes and retitles the
  copy `Time's up` through `entity.get`'s `children`; `play.stop` closes the tabs that leave a game playing (stage 1
  step 4, stage 2 step 6, the table walk); stage 3 step 3 tries levels 0 and 2 by command and sets 1 back; the coin
  tuning tab sets the two fields (90, 0.25) before `prefab.apply`.
- Mended in the file: script files ride on `script.build` after `script.create`; `Complete.ogg` comes from
  `@RELEASE@`; checks of the page's values (5 coins, `Time: 39`, `Round lost`, hidden panels, `Time's up` at 8 s,
  `Time: 60` and `Time: 27`, yellow at 20, the prefab's tuned fields in play, the export list and identity). Stage 4
  checks the identity with `project.info` (the page only asks to look) and cannot run the export or the game: commands
  take no placeholder for a folder outside the project, and the game's command lines are no editor commands.
- Exercise 1 now checks the answer: deleting the five small coins while playing gives `Score: 5`, the big one
  `Score: 10` and the win panel.

## Track walk G, final, segment 6 (2026-11-24)

Answers to `plan/walks/G-final-6.md`, WK16 to WK22:

- WK16: What you need names checkpoint 4 of `make/export` and its section, and how to open the zip.
- WK17: no `CoinRunGame.step1.cpp` or `.step2.cpp` is in any download: `tools/tutorials.py` zips the project, where
  the file is `Scripts/CoinRunGame.cpp` (stage 1 the step-1 version, stage 2 the step-2 version, stages 3 and 4 the
  last). What you need and the three replace steps now name `Scripts/CoinRunGame.cpp` of checkpoints 1, 2 and 3, and the
  command tabs say no command writes a file's text.
- WK18: the step-1 tab and the step-5 tab of Win, lose and start again play both ends by command: the five coins of the
  running copy are deleted for the win (as exercise 1 does), `play.step` waits out the loss, and `input.key` Enter
  restarts. The file now runs and checks them: `Round won` after the deletion and `Round lost` after 2,490 steps in
  stage 1; in stage 2 `WinPanel` active with `Coins left: 0`, after Enter and 120 steps `WinPanel` inactive and five
  coins, and after the lost round's Enter `LosePanel` inactive and `Time: 8`.
- WK19: the warning comes from `make/input`, whose `BallControl` stored `Speed` 4 on the ball, and `make/physics`,
  whose `BallControl` has no `Speed`; `ScriptSystem::ApplyFieldOverrides` reports it at every start
  (`Strata/src/Strata/Scripting/ScriptSystem.cpp:757-761`), and the Inspector draws only the class's fields
  (`StrataEditor/src/Panels/InspectorPanel.cpp:135`), so nothing removes the value. A new step 5 of the polish section
  removes and adds `BallControl` again; the file checks the warning in the play before and the class default
  (`PushStrength` 12) after, and plays once more. No check can test that a line is absent (`contains` only), and
  `script.get` lists the class's fields, not stale values, so the run's log of that last play was read by hand: no
  `Script fields` line. The Console row and the log step say no `Script fields` line is left. For physics's fixer: its step that
  replaces `BallControl` could clear the old field there.
- WK20: the window grows with the display's scale (see export's notes); step 3's "You should see" says 1280 by 720 at
  100 % and 1920 by 1080 at 150 %, and `--resolution` for exact pixels. The export step now saves the scene first (the
  new step 5 leaves it modified).
- WK21: no download holds `CREDITS.md` (the tool writes one only for CC BY files, and `make/assets` has the reader write
  it by hand). The step says to create it beside `CoinRun.stproj` when missing. The table gains the sky (Poly Haven,
  from the Third Person sample) and `Textures/Metal/` (`ambientCG` Metal032, from the Physics Playground sample), and
  the music row became a sentence: `Sounds/Music/Complete.ogg` is the win chime again (`make/sound` imports the same
  file into `Sounds/Music`).
- WK22: the strip's "Next on your track" comes from `src/components/Pagination.astro`, one template per track that
  holds the page (G and B), and the book's script shows the chosen one; a reader of the raw page sees both. The
  closing paragraph now names both next pages by their titles: The math of moving things (G) and Version control with
  git (B, `plan/tracks.md` entry 30), where it named Numbers and data for track B.
- Also mended: the polish section said the glow of the coins was still there; the `Coin.cpp` of `make/physics` dropped
  it.
- Runs, 2026-11-24: the tutorial and its exercises pass with the pin build (Release) and with the official v0.8.0 package. The run (round 2; round 1 expected a stored `Speed` from `script.get`, which lists the class's fields) also stamped the exercises that start from this page: `make/commands` exercise 1, `make/designing-a-game` exercise 2 and `make/script-builds` exercise 1, all passing with both.

## Engine

- No command contradicted its description in the stages that ran.
- A stored script field that the class no longer has warns at every start ("Script fields: script 'BallControl' has
  no field 'Speed'; the stored value is ignored"), and neither the Inspector nor a command removes it (`script.setField`
  refuses a field the class lacks, `EditorScriptCommands.cpp:666`); only removing and adding the script clears it. The
  page says so (polish step 5). For the engine's agents: an Inspector row or a command that drops stale values.

## Figures

- `result`, `win-panel`, `polished` (scene, Basic 3D template, `camera: "scene"`): published after one round. The writer's
  recipes showed `Coins left: 3` at the win and a time bar neither short nor red for the low time; the photographer set
  the HUD texts and fills to match each moment (win: `Coins left: 0`, `Time: 23`, fill 0.575, white as the final script
  colors it above 20 s; stage-2 win: `Time: 17`, fill 0.425, the hud page's warm yellow; low time: `Coins left: 2`,
  `Time: 9`, fill 0.225, `TimerText` and `TimeBar` red 1, 0.2, 0.2 as `ShowTimeColor` writes). The ground is the
  template's plain grey plane, no coins or walls, so the captions and alt texts name no course and no frozen world (a
  still cannot show that the world stopped).
- `round-playing` (editor) and `exported` (runtime): kinds the photographer does not take; left as they are.
- `round-playing`, settled by the editor photographer (one round, provisional build, `waitsFor` kept). The writer's
  recipe typed fixed texts (`Time: 42` against a limit of 40) on a bare template and pictured the whole window, where
  the HUD reads badly. It now pictures the `Game` panel (`layouts/hud.ini`, 1280 by 800): the course of `result`
  (walls, camera), a plain ball, three gold coins tagged `Coin`, the HUD with a yellow bar, the entity `Game` running
  the tutorial's own `CoinRunGame.step1.cpp` (copied by `files`, built, `TimeLimit` 40), played paused for 720 fixed
  steps. The script writes `Coins left: 3`, `Time: 29` and a bar at about seven tenths; caption, alt and shows say so.
  No coin is collected (the ball does not move), and the Console's `Round won` belongs to a later moment.
- `result`, mended: a viewer found the empty grey plane unrecognisable as Coin Run. Its setup now builds the course of
  the scenes-entities page (four walls 1.5 m high around the 20 m ground, `Main Camera` at 0, 16, 13 pitched -55) and
  the metal ball of the materials page at 3, 0.5, 8, below the panel; no coins, since the round is won. Caption, alt
  and shows name the walls, the ball and the empty course. `win-panel` and `polished` keep the plain ground.
- 2026-11-23, pin v0.8.0 (319075e3), one round, one hold: `result`, `win-panel` and `polished` taken again; `figures.py
  compare` found the originals identical to the published ones (0 pixels differ), so publish left the files and stamps
  as they are. `round-playing` taken without `--provisional` (the pin has `editor.screenshot`; its `waitsFor` removed
  as check asked) and published: the Game panel shows `Coins left: 3`, `Time: 29`, the yellow bar at about seven
  tenths (533 of 761 px), three gold coins and the white ball inside the walls, as caption, alt and shows say.
- `exported` (runtime): the kind is not taken yet; left as it is.
- 2026-11-24, `exported` (runtime, the kind now taken): not taken. Its picture must show the exported game running the
  tutorial's `CoinRunGame.cpp`, and at the pin a runtime figure cannot carry that file: `check` lets only editor, scene and
  program text figures copy `files`, and no editor command writes a script's source (`script.create` writes only its
  template). The old recipe, a bare Basic 3D template, would show no course, no coins and no round; an export of the
  course with its HUD but no script would show the HUD's saved texts at ten seconds, not a round counting down: neither is
  honest for "the same round". The recipe now builds the course of `result` (walls, `Main Camera`, the metal ball), five
  gold coins tagged `Coin`, the HUD, `WinPanel` and `LosePanel`, the action `Gameplay/Restart` and the entity `Game` with
  `CoinRunGame` (`TimeLimit` 40), then saves; caption, alt and shows say what it would show after `--seconds 10`
  (`Coins left: 5`, `Time: 30`, the white bar at three quarters). It is `blocked` with that reason and the request (files on
  runtime figures, `files` from `book:tutorials/make/project-coin-run/CoinRunGame.cpp` to `Scripts/CoinRunGame.cpp`).
  Its stand-in is the diagram `shipped`, placed after the stage-4 checkpoint where `exported` stood (the checkpoint needs
  its "You should now have" picture): the project folder (Always Include list, `CREDITS.md`), the export folder
  (`CoinRun.stgame`, `.stpak`, `CoinRunScripts.dll`, `CoinRun.png`, `ThirdPartyNotices.md`, `CoinRun.exe`; names from
  GameExport.cpp and the export page) and the game's data folder with `Logs\Game.log`. Drawn, rendered in both themes,
  checked; one round mended a description that ran past the box.
