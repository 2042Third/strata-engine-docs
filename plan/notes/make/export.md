# Notes: make/export

## Since

0.3.0: the export, its runtime options and the pack appear in release 0.3.0; the game identity came in 0.6.0 (plan/inventory/gamedev.md:236, :206).

## New terms

None. The page defines export, manifest, pack, game identity, start scene, loading scene, headless, pruned export and always include, which the glossary homes here.

## Requests

- Hosts: the Desktop Entry Specification (freedesktop.org) and Microsoft's SmartScreen documentation are cited without a link; add `specifications.freedesktop.org` and `learn.microsoft.com` to tools/external-hosts.txt if links are wanted.
- Figures: `result` and `game-running` are runtime figures on the basic3d template as a stand-in (a tutorial project is no recipe form); the editor figures reuse `layouts/first-game.ini` and wait for `tier 2: editor screenshot`; the dialog, the Export page entries and the Game page values have no setup steps yet.
- Tutorial file: the export itself needs an absolute folder, so no stage runs `project.export`; stages 2 and 3 and the solution of exercise 1 hold only `project.exportStatus`. The icon is `Samples/ThirdPerson/Assets/Icon.png`, not a file of `tutorials/assets/`, which does not exist yet.
- Step 3 of "Export the game" (the refusal while a build runs) depends on timing; its "If you do not see it" says so.
- The sidebar and other pages are linked by file name (`levels-saves.md`, `large-worlds.md`, `performance.md`, `quality.md`, `../start/install.md`, `../appendix/not-in-strata.md`) before they exist.

## Not verified

- The Game page's red fields on a refused value (the page says the editor refuses the value; the field's color was not read).
- That the folder `<project folder> Build` is the default folder on every start (read in ExportDialog.cpp:21 only).
- That `Scenes/Main.stscene` and the assets `Prefabs/Coin.stprefab`, `Materials/GoldGlow.stmat`, `Sounds/Coin.ogg` exist in the end state of make/play-test-debug (taken from the neighbouring pages' tutorial scripts).
- The Linux and macOS file names of the script library (`.so`, `.dylib`) are from `DynamicLibrary::GetFileExtension`, not read.
- The exact wording of the message of a build in flight: the page paraphrases `Script build N is running and may be writing the script module`.

## Findings not applied

- critic-make-a-16: applied (labels `Leave out unused assets`, page **Export**); the page does not name a box **Prune**.
- critic-make-a-27: applied in step 1 of "Export the game" (window size, **Fullscreen**, loading scene, identity link, **Copy the runtime**, **Copy the script symbols**).
- critic-make-a-28: applied (the three paths and the `FindAsset` warning); `Complete.ogg` of make/project-coin-run is covered by the folder `Sounds`.
- Not covered: the credits screen is named in one sentence, not built (the brief asks for a sentence).

## Clerk

- No term or word asked.
- Admitted to external-hosts.txt: specifications.freedesktop.org (learn.microsoft.com was already there).
- Left for the planner: the figures, the export folder of the stages, the icon file.

## Figures

- game-page, export-dialog, export-settings (editor, 2026-11-18): recipes written from the page's steps and taken with
  the provisional build (`--provisional`); nothing published, `waitsFor` kept. The project is basic3d with the files of
  the tutorial's stage 1 (the ThirdPerson icon as `Assets/Icon.png`); the steps run stage 1's `project.setGameInfo`.
  - game-page: round 1 good. The Project Settings panel (layout `first-game.ini`, the panel at its own pixels, about
    800 × 500) opens on its first page, Game: Start Scene Main, Loading Scene None, Title Coin Run, Version 1.0.0,
    Company Your Name, Copyright (c) 2026 Your Name, the Icon field and its preview under it. Shows and alt now name
    those values.
  - export-dialog: round 1 good for the dialog's fields (whole window 960 × 540, `first-game-960.ini`,
    `editor.showDialog export`). No command starts an export from the dialog, so the progress bar and its stage line
    cannot be pictured; caption, alt and shows now describe the dialog before the run, the moment of step 1. The
    folder field and the summary line show the take's folder under `G:\GameEngineAI\.worktrees\docs-work\...\01 Build`
    (no user name, but a machine path, and the project copy is named 01): retake from a neutral folder or crop the
    field before publishing when the pin moves.
    Round 2 (2026-11-18, a viewer's report: the path names the take machine and the folder 01, not `CoinRun Build`):
    the fault stands, and no recipe can mend it, so there was no retake. The dialog fills the folder once, from the
    open project's folder plus " Build" (`ExportDialog::Open`, `ExportDialog.cpp:120`; only Browse's native dialog
    changes it, line 275). `figures.py take` makes the project copy as `<work>/projects/<NN>` (`'%02d'`, line 2142),
    and no recipe field names that folder. The commands that could make the project elsewhere (`project.create`,
    `project.openSample`, `project.export`) take only absolute directories. Such a path in a recipe would tie it to
    one machine, and it would still show the take's long root. `editor.showDialog` has no folder parameter. Cropping
    the path out cannot be done in the recipe either: `crops` publish extra pictures beside the whole window, which
    still shows the field and the summary line. What the figure needs, beyond this page: a `figures.py` option that
    names the project copy's folder (here `CoinRun`) under a short neutral root (for example a drive mapped with
    `subst` to the work folder), or an editor command that sets the dialog's folder. Until then the picture is not
    publishable as taken. Nearest honest picture: the same take with the path's two places masked when it is
    published, and the caption kept, since it names "the folder" and not its path.
  - export-settings: cannot. The Project Settings panel always opens on its first page, Game, and no command selects
    another page (`editor.showPanel` has no page parameter; the panel's `Select` is called by nothing), so the Export
    page with its three entries cannot be shown; the round-1 take shows the Game page. Recipe left as written. The page
    gets nothing until a command selects a Project Settings page; then the steps are stage 4's
    `project.setExportSettings` (with the tutorial's prefab, material and sound folder copied by `files`) and the page
    `Export`. Nearest honest picture meanwhile: none (the command tab's JSON already lists the three paths).
- Pin v0.8.0 (319075e3, 2026-11-23), Release build, without `--provisional`; `check` asked to drop the three
  `waitsFor "tier 2: editor screenshot"` lines.
  - game-page: published (round 2). Round 1 failed: `files: [{"stage": 1}]` copied nothing, since the tutorial's stage 1
    now imports the icon with `asset.import @RELEASE@/...` instead of copying it, so `project.setGameInfo` refused
    `icon: Icon.png`. A recipe may copy only `book:` files, and no `tutorials/` image exists, so the project is now the
    Tetris sample (start scene Main, no loading scene, an `Icon.png`); the steps set the identity as before. The panel
    shows Start Scene Main, Loading Scene None, Coin Run, 1.0.0, Your Name, (c) 2026 Your Name and the icon's preview,
    which is the Tetris icon, not the ThirdPerson one the page imports: the alt now names "a picture of falling blocks".
    The Game page also lists Export below it, as the page says. To picture the reader's own icon: a stage file copying
    `Samples/ThirdPerson/Assets/Icon.png` in the tutorial, or an image under `tutorials/`.
  - export-dialog: not published, `waitsFor` tier 3 (the path). Round 1 failed as game-page did; round 2 dropped the
    icon from the steps (basic3d holds no image) and took the dialog: the folder field and the summary line read
    `G:\GameEngineAI\.worktrees\docs-work\photo\make-export\projects\02 Build`, the fault of 2026-11-18 unchanged (the
    take machine's path, and `02 Build` where the page teaches `CoinRun Build`); without an icon the identity line
    also reads "Coin Run 1.0.0 by Your Name, without an icon of its own". Needs a `figures.py` option that names the
    project copy (CoinRun, under a short neutral root) or a command that sets the dialog's folder; then the project
    Tetris (for the icon) or a copied icon, and alt as before. Nearest honest picture: none publishable as taken.
  - export-settings: still cannot, `waitsFor` now tier 3 (no command selects a Project Settings page at v0.8.0:
    `editor.showPanel` has no page parameter; `ShowProjectSettings(page)` is reached only from Inspector links to
    Collision Layers, Timing and Graphics Quality). Not taken.
- 2026-11-23, a viewer's report on game-page, pin v0.8.0 Release:
  - The icon was Tetris's (falling blocks), not the ThirdPerson robot that step 2 imports. A recipe's own `files` copy
    only `book:` files (the schema refuses `Samples/...` outside a stage), and stage 1 imports the icon with
    `asset.import @RELEASE@/...` instead of copying it. So the project is now the ThirdPerson sample, whose
    `Assets/Icon.png` is that robot. New steps save its opened start scene as `Scenes/Main.stscene`, make that the
    start scene and clear the loading scene (`project.setExportSettings {loadingScene: null}`), then set the identity
    as before. Round 1 is good: Start Scene Main, Loading Scene None, Coin Run, 1.0.0, Your Name,
    (c) 2026 Your Name, and the preview is the robot in a garden. The alt says so now. Published.
  - Start Scene reads `Main`, and step 1's "You should see" promises `Scenes/Main.stscene`. The field shows the asset's
    name, not its path, and no recipe changes that. For the writer: step 1's line should read "the scene Main in
    **Start Scene**". This take does not edit the page's words.

- 2026-11-24, final pin v0.8.0 (319075e3) Release, the tool with runtime takes and neutral paths; one hold for the
  page (`--kinds runtime,editor`).
  - result: published. A recipe cannot rebuild Coin Run (its tutorial starts from make/play-test-debug's chain, and a
    recipe copies no other page's stages), so the nearest honest picture is the ThirdPerson sample, whose course has
    coins and a counter like Coin Run's: setup steps make `Scenes/Course.stscene` the start scene and `project.save`,
    then the export runs 6 s at 1280 by 720, high. Round 1 good: the robot on its island, coins up the course, the box
    COINS 0 / 12, TIME 0:06.0, the controls along the bottom. Caption and alt name the third-person sample; the page's
    lead-in sentence now says the picture is that sample.
  - game-running: published. The Tetris sample exported and run 10 s (a different game from result, and one whose
    frame shows game time passing). Round 1 good: the first piece halfway down the well, its ghost at the bottom,
    Score 0, Level 1, Lines 0, the next piece. The caption says it is Tetris and that the reader's file shows Coin Run.
  - export-dialog: published, `waitsFor` removed. The tool now maps the window's folder to `S:` and names a sample's
    copy after the sample, so the field reads `S:\Projects\ThirdPerson Build`; no recipe names the copy CoinRun. The
    project is the ThirdPerson sample (for its icon), the steps clear the loading scene and set Coin Run's identity.
    Round 1 good: the folder, 1280 x 720, Fullscreen empty, Loading scene None, "Coin Run 1.0.0 by Your Name, with the
    icon Icon.png", the two ticked boxes and the empty one. The caption says the folder is that sample's plus Build.
  - export-settings: still not takeable (no command selects a Project Settings page at v0.8.0); `waitsFor` kept as the
    request, `standIn` is the drawing `pruned-pack`, which the page places after checkpoint 4: the scenes' references
    and the always include list (the three entries of step 4) leading into the pruned pack. Drawn, rendered (both
    themes looked at), `drawings.mjs check` passes.
  - game-page was retaken in the same hold and not republished (the published one stands).

## Track walk G, final, segment 6 (2026-11-24)

Answers to `plan/walks/G-final-6.md`, WK12 to WK15, and the window size of WK20:

- WK12: `make/play-test-debug` is a how-to, so it has no checkpoints; its end state is the box at the end of its Result
  (`src/plugins/checkpoint.mjs`, `resultBox`: the last stage's zip, `stage-7.zip`). What you need now says so.
- WK13: `GameExport` refuses a modified scene with no save in flight: "The open scene has unsaved changes; save it first
  (the export uses the saved files)" (`StrataEditor/src/Editor/GameExport.cpp:180-182` at the pin). The command tab
  starts with `scene.save`, the editor steps say **Ctrl+S**, and the red message is quoted. The file's stage 2 runs
  `scene.save` too (the export itself still cannot run in a tutorial: commands take no placeholder for a folder
  outside the project).
- WK14: the sentence "Exported N assets ... N unused assets were left out." is the dialog's
  (`StrataEditor/src/UI/ExportDialog.cpp:93-97`); `project.export` answers JSON (`assetCount`, `excludedAssets`).
  Both tabs now say what each shows.
- WK15: the `Coin.cpp` of `make/physics` (step 4) and of `make/sound` no longer swaps in `GoldGlow.stmat`; only
  `tutorials/make/scripting-scene/Coin.cpp` loaded it by path. `Bump` loads `Sounds/Impacts/Soft.ogg` by path
  (`tutorials/make/sound/Bump.cpp:32`). The page now names the two places (prefab, Bump) and the two `FindAsset` lines
  in the order the walker read them, says why GoldGlow writes none, and keeps GoldGlow in the list for a Coin that
  glows again (the drawing `pruned-pack` and stage 4 keep their three entries). For physics's fixer: its step 4
  drops the glow that scripting-scene taught, and `make/project-coin-run` said the glow was still there.
- WK20 (on project-coin-run): a windowed game without `--resolution` sizes its window in screen coordinates scaled by
  the monitor's content scale (`Strata/src/Strata/Core/Window.h:65-67`, `GLFW_SCALE_TO_MONITOR` in
  `Strata/src/Platform/GLFW/GLFWWindow.cpp:168-169`; `--resolution` sets `SizeInPixels`,
  `StrataRuntime/src/RuntimeApplication.cpp:494-501`). The walker's 1920 by 1080 is 1280 by 720 at 150 %. The dialog
  item now says so.
- Runs, 2026-11-24: the tutorial and its exercises pass with the pin build (Release) and with the official v0.8.0 package.

## Tutorial run

- 2026-11-18, pin Release: the tutorial and exercise 1 pass (round 2). Added checks of the page's values to the thin
  file: stage 1's identity (title, version, company, copyright, an icon handle), stage 4's three always-include
  entries and no loading scene. `project.setStartScene` answers a handle, so the start scene's path is not checked.
- Not run: the export itself and the runs of the exported game (stages 2 and 3, exercise 1's solution). Commands take
  no placeholder, and `project.export` needs an absolute folder outside the project; the game's command lines are no
  editor commands. Those stages hold only `project.exportStatus` (`{running: false, state: null}`).
- 2026-11-23, pin v0.8.0 (319075e3) Release: the tutorial and exercise 1 pass as written (round 1). The commands the
  files use changed between the pins only in their metadata (mayDefer, results, waitsForAssets), not in what they do.
  pagecheck's figures check fails on two `waitsFor "tier 2: editor screenshot"` entries now that the pin has
  `editor.screenshot`: that is the figures' work, not the tutorial's.
- 2026-11-24, final runs: the pin-build stamps were current; the official v0.8.0 package
  (Strata-0.8.0-windows-x64.zip) runs the tutorial and exercise 1 as written (round 1), and
  `tutorials.py check --release` finds nothing.
