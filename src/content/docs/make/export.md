---
id: make/export
title: "Exporting and shipping"
description: "Export Coin Run into a folder that plays without the editor, run it as a player would, and find out what a pruned export loses."
kind: tutorial
size: M
tracks: [G, B]
needs: [make/project-files, make/hud]
time: 90
learn:
  - id: export-contents
    text: name the files an export writes and what each one does
  - id: set-identity
    text: set a game's title, version, company, copyright and icon in Project Settings
  - id: export-run
    text: export a game, run it from the folder and from a terminal with options
  - id: prune-export
    text: fix a pruned export that misses assets a script loads by path
  - id: read-log
    text: find a game's log and read the warning of a missing asset
since: 0.3.0
status: final
---

## What you will make

You export Coin Run to a folder outside the project, play it from that folder like a player, and then export it again without the unused assets. Like the third-person sample below, the exported game then plays in a window of its own.

::figure{id=result}

An **export** is a folder that plays your game without the editor. Strata writes into it the :term[runtime]{id=runtime} renamed after the game, the game's data and its scripts. The editor and the project stay behind.

The data is two files. The **manifest** is a small file with the extension `.stgame` that names the game, its start scene, its window and the files that belong to it.

The **pack** is one file with the extension `.stpak` that holds every asset the game uses, in the order the game first needs them. Scripts travel as a library file beside them, an icon as a picture, and on Linux a desktop entry joins them.

```mermaid caption="An export reads the project and writes a folder: the renamed runtime, the manifest, the pack, the scripts, the icon and the notices." alt="A flow chart. The project, with its scenes, assets, scripts and game identity, leads through the export to a folder. The folder holds the renamed runtime, the manifest, the pack, the script library, the icon and the notices file."
flowchart LR
  P[Project: scenes, assets, scripts, identity] --> E[File, Export Game]
  E --> R[Runtime renamed after the game]
  E --> M[Manifest]
  E --> K[Pack of the assets]
  E --> S[Script library]
  E --> I[Icon and notices]
```

## What you need

- The end of [Play, test and debug](play-test-debug.md): Coin Run with its heads-up display, its sounds and the coin bug fixed. That page is a how-to and has no checkpoints: download its project from the box at the end of its [Result](play-test-debug.md#result), or continue your own project. The zip holds a folder with `CoinRun.stproj`: open that file with **File ▸ Open Project...**. The project is named `CoinRun`.
- Built scripts. The download holds the scripts' code but no built :term[script module]{id=script-module}, and the export refuses a scene whose scripts were never built. Build them once after you open it, with **Scripts ▸ Build Scripts** or `{ "command": "script.build" }`, and wait until the build has finished.
- One image for the icon: `Icon.png` from the `Samples/ThirdPerson/Assets/` folder of the release, a picture of 256 by 256 pixels that Strata made itself, credited in that sample's `CREDITS.md`. Import it as you did in [Assets](assets.md).
- An empty folder outside the project, for example `Builds/CoinRun` beside it.
- A terminal for the last steps; [Install and start](../start/install.md) shows how to open one. About an hour and a half.

## Give the game its identity

A player never sees your project. They see the program's name, the title in the window bar, the icon in the program's window and the version in the file's details. The **game identity** is the set of these values: a title, a version, a company, a copyright line and an icon. You set them once in the project, and the export stamps them into the game.

The identity lives beside two scene choices on the same settings page. The **start scene** is the scene the exported game opens first.

The **loading scene** is a small scene that the game plays while the start scene loads. Coin Run needs none; [Levels and saves](levels-saves.md) teaches it.

:::::steps

1. Make sure the start scene is `Scenes/Main.stscene`. Basic 3D set it already; this step checks it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open `Scenes/Main.stscene`, then choose **File ▸ Set as Start Scene**. Choose **File ▸ Project Settings...** and open the page **Game**: **Start Scene** names the scene.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.setStartScene", "parameters": { "scene": "Scenes/Main.stscene" } }
   ```

   :::
   ::::

   **You should see:** the scene's name, `Main`, in **Start Scene**.

   **If you do not see it:** the scene is not open, or it has changes you have not saved. Save it with **Ctrl+S**, then repeat.

2. Import the icon and set the identity.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Import `Icon.png` into the project. On the page **Game** of **Project Settings**, set **Title** to `Coin Run`, **Version** to `1.0.0`, **Company** to your name and **Copyright** to a line such as `(c) 2026 Your Name`. Choose `Icon.png` in **Icon**.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "file": "<release folder>/Samples/ThirdPerson/Assets/Icon.png" } }
   { "command": "project.setGameInfo", "parameters": { "title": "Coin Run", "version": "1.0.0", "company": "Your Name", "copyright": "(c) 2026 Your Name", "icon": "Icon.png" } }
   ```

   :::
   ::::

   **You should see:** the icon's preview under the fields.

   **If you do not see it:** a field returned to its old text, so the editor refused the value. A title, a company and a copyright line hold up to 128 characters without control characters, and a version is one to four whole numbers from 0 to 65535 separated by dots, as in `1.2.0`.

   **Why:** the title and the icon are what the game shows, so they are not the project's name. The project's name, `CoinRun`, stays the key of the game's save and log folders, so a new title never moves a player's saves.

:::::

A script cannot read the title or the version; they are for the player and the platform, not for the game's logic.

::checkpoint{stage=1}

::figure{id=game-page}

## Export the game

The export reads the saved project and writes the folder in the background. The editor keeps running, and the dialog shows a progress bar. Before you press the button, read each field: you meet them all in one place.

:::::steps

1. Open the dialog and read its fields.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Export Game...**. The dialog has these parts, from the top:

   - The first field names the folder to write; **Browse...** opens a folder picker.
   - The window size and **Fullscreen** say how the game starts. The default is 1280 by 720, windowed. The game grows the window with the display's scale, so that it covers the same share of every screen: at a scale of 150 % the window is 1920 by 1080 pixels. A player can still pass `--windowed` to a fullscreen game, and `--resolution` asks for exact pixels.
   - **Loading scene** picks the scene the game plays while the start scene loads. Leave it at none.
   - A line under it summarizes the identity and links to the **Game** page.
   - **Copy the runtime** writes the game's program. Without it the export writes only data.
   - **Copy the script symbols** adds the module's debug file, so that a crash in a shipped script can be examined.
   - `Leave out unused assets` is the pruning switch. It is off.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   { "command": "project.export", "parameters": { "directory": "<absolute path outside the project>", "width": 1280, "height": 720 } }
   ```

   The export reads the saved files, so it refuses a scene with changes you have not saved: `scene.save` first. A project from the download needs `script.build` before both, as "What you need" says. The command answers when the export ends, with the files it wrote and `assetCount`, the number of assets in the pack.

   :::
   ::::

   **You should see:** the folder `<your project's folder> Build` as the default folder, and **Export** disabled while the folder has a problem.

   **If you do not see it:** the line under the fields is in warning color and names the problem: the folder is inside the project, is not absolute or is a file.

2. Save the scene with **Ctrl+S**: the export reads the saved files. Then type the folder you prepared into that field and press **Export**, or run the commands of the first step with your path.

   **You should see:** a progress bar and a line of text that changes. Strata names four stages: waiting for asset imports to finish, cooking worlds (only when the project has them), packing the assets and, last, writing the :term[script module]{id=script-module}, the manifest and the runtime.

   **If you do not see it:** the dialog ends with a red message. It names the reason, for example `The open scene has unsaved changes; save it first (the export uses the saved files)`, or that a build is running. Step 3 makes one on purpose.

3. Meet a refusal on purpose. Start a script build, then export at once.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ Build Scripts**, then open **File ▸ Export Game...** and press **Export** while the build runs.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** a message that script build number so-and-so is running and may be writing the script module, with the advice to wait.

   **If you do not see it:** the build finished before you pressed the button, and the export started. Let it finish; the refusal is not needed again.

   **Why:** the game ships the scripts the editor runs, exactly as it loaded them. A build in flight or a module that changed since the editor loaded it means the editor runs no module it can ship, so the export refuses before it writes anything. Scripts that were never built fail the export once it finds a scene that uses them. It also refuses a folder inside the project, a scene with changes you did not save and a game that is playing.

4. When the bar reads **Done**, press **Open Folder**.

   **You should see:** your file browser, with the game's files.

   **If you do not see it:** the dialog says it could not open the folder. Open it yourself from the path the dialog printed.

:::::

The summary line of the dialog gives the number of assets, the size of the pack and the seconds the export took. These are the files you find, written for the project `CoinRun`:

:::files[The exported folder]

- `CoinRun/` the export folder
  - `CoinRun.exe` the runtime renamed after the game (no `.exe` on Linux and macOS)
  - `CoinRun.stgame` the manifest
  - `CoinRun.stpak` the pack
  - `CoinRunScripts.dll` the script library (`.so` on Linux, `.dylib` on macOS)
  - `CoinRunScripts.pdb` the script symbols, when the box was ticked (Windows)
  - `CoinRun.png` the icon, 256 pixels square
  - `CoinRun.desktop` the desktop entry, written only on Linux
  - `ThirdPartyNotices.md` the licenses of the code inside the runtime

:::

Keep `ThirdPartyNotices.md` beside the game: the runtime contains other people's code whose licenses ask for this notice. The export refuses to start when the file is missing beside the editor's copy of the runtime.

::checkpoint{stage=2}

::figure{id=export-dialog}

## Run the game as a player

A player starts the program by double-clicking it, and the system asks its own questions first. Strata does not sign the program, so Windows and macOS warn once.

:::::steps

1. Start the game from the folder.

   ::::tabs{sync=os}
   :::tab[Windows]
   Double-click `CoinRun.exe`. `SmartScreen` may say that Windows protected your PC, because the program has no publisher's signature. Press "More info", then "Run anyway".
   :::
   :::tab[Linux]
   Double-click `CoinRun`, or run `./CoinRun` in the folder. To list the game among your applications, copy the entry into the hidden folder where desktops search for them:

   ```sh
   cp CoinRun.desktop ~/.local/share/applications/
   ```

   Open the copy in a text editor: its `Exec` and `Icon` lines hold the absolute paths of the export folder.
   :::
   :::tab[macOS]
   A program that came from a download carries a mark, and macOS refuses it. Remove the mark once, in a terminal, with the real path of your folder:

   ```sh
   xattr -dr com.apple.quarantine ~/Builds/CoinRun
   ```

   Then double-click `CoinRun`.
   :::
   ::::

   **You should see:** a window titled `Coin Run`, with the coin count, the time bar and the coins, in the icon you chose.

   **If you do not see it:** the program stops at once. On Windows and Linux on x86-64 the game needs a processor with advanced vector extensions 2 (AVX2), and nothing checks it at start, so an older processor stops without a message. Otherwise read the log of step 3.

2. Run the game from a terminal with options. Open a terminal in the export folder.

   ```sh
   ./CoinRun --windowed --resolution 1280x720 --seconds 10 --screenshot shot.png
   ```

   **You should see:** a window of 1280 by 720 pixels that closes by itself after 10 seconds of game time, and the file `shot.png` in the folder.

   **If you do not see it:** the terminal prints the problem and the usage, and the program ends with exit code 3. An exit code is the number a program reports to the terminal when it ends. On Windows write `.\CoinRun.exe` and add `| Write-Output` to the line, so that PowerShell waits for the program and gets its exit code.

3. Run the game with no window, then read its log.

   ```sh
   ./CoinRun --headless --frames 600
   ```

   **You should see:** the lines of the game in the terminal, and the exit code 0 (`$?`, or `$LASTEXITCODE` in PowerShell). At 60 frames per second, 600 frames are 10 seconds of game time. The log is the file `Logs/Game.log` in the game's data folder: `%LOCALAPPDATA%\CoinRun` on Windows, `~/.local/share/CoinRun` on Linux and `~/Library/Application Support/CoinRun` on macOS. The saves go into `Saves` in the same folder.

   **If you do not see it:** exit code 1 means the game could not start, for example for want of its manifest. Exit code 2 means a script crashed.

:::::

**Headless** means that the game runs with no window and no :term[graphics card]{id=gpu}, like a program on a server; scripts and physics still run, which makes it a check you can script. Here are the options of the game, as it prints them for `--help`:

| Option | What it does |
| --- | --- |
| `--game <file.stgame>` | plays this game; by default the one manifest next to the program |
| `--headless` | no window, no graphics, 60 frames per second |
| `--windowed` | a window even when the game asks for fullscreen |
| `--resolution <w>x<h>` | a window of exactly that many pixels |
| `--frames <n>`, `--seconds <n>` | stops after that many frames, or seconds of game time |
| `--screenshot <file.png>` | saves the last frame; needs `--frames` or `--seconds` and a window |
| `--quality <low, medium, high, ultra>` | draws with this quality preset for one run; saves nothing |
| `--save-directory <folder>` | keeps the save files in this folder |
| `--asset-budget-mb <n>`, `--perf-log <file.csv>` | memory budget and timing log; [Performance](performance.md) uses them |
| `--help` | prints this help and exits with 0 |

The exit codes are 0 for a run that ended well, 1 when the game cannot start and 2 when its scripts crashed in a headless run. Code 3 means a command line the game does not understand. Players' graphics options are the subject of [Graphics quality](quality.md).

The exported game differs from the editor in a few ways. It cannot :term[hot reload]{id=hot-reload} scripts. A windowed game keeps running without its scripts after one crashes, and the crash is in the log. It reads the project's settings from the manifest, since it has no project file, and the players' saved graphics options win over the project's.

::checkpoint{stage=3}

::figure{id=game-running}

## Prune the export and fix what it loses

A full export packs every asset of the project. A **pruned export** packs only the assets that scenes use, with what those use in turn, so the pack is smaller. The price is assets that a script finds by path. No scene shows that link, so a pruned export drops the asset.

Coin Run has two such places now. `CoinPlacer` loads `Prefabs/Coin.stprefab` by path and spawns it, and the `Bump` script of the ball loads `Sounds/Impacts/Soft.ogg` by path. You keep the whole `Sounds` folder, so that the sound a later script finds by path travels with the game too. You also keep `Materials/GoldGlow.stmat`: no scene names it, and a `Coin` that swaps in the glow of [Scripting the scene](scripting-scene.md) loads it by path. The list of paths to keep is the **always include** list: assets and folders that every pruned export packs even though no scene uses them.

:::::steps

1. Export a second time into another folder without the unused assets.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Export Game...**, set the folder field to `Builds/CoinRunPruned`, tick `Leave out unused assets` and press **Export**.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.export", "parameters": { "directory": "<absolute path of another folder>", "prune": true } }
   ```

   The command answers no sentence: its `assetCount` is smaller than the first export's, and `excludedAssets` lists each asset it omitted.

   :::
   ::::

   **You should see:** the dialog's message, which ends with a count and `unused assets were left out.`

   **If you do not see it:** the box is not ticked. The pack is then as large as the first one.

2. Run the pruned game.

   ```sh
   ./CoinRun --windowed --seconds 10
   ```

   **You should see:** the course and no coins, because the :term[prefab]{id=prefab-make} is missing.

   **If you do not see it:** you ran the first export. Check the folder.

3. Read the warning in `Game.log`.

   **You should see:** two lines that begin `FindAsset (called by script`. The first is the ball's `Bump` and ends with `there is no asset at 'Sounds/Impacts/Soft.ogg'`; the second is `CoinPlacer`'s and ends with `there is no asset at 'Prefabs/Coin.stprefab'`. Each script asked for a path, and the pack holds none. `GoldGlow.stmat` writes no line: the `Coin` script that [Physics](physics.md) gave you no longer swaps in the glow, so nothing asks for it.

   **If you do not see it:** you found the log of another run. Each start replaces the file, so run the pruned game again and read it at once.

4. Add the paths to the project and export again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Project Settings...** and open the page **Export**. Type each of `Prefabs/Coin.stprefab`, `Materials/GoldGlow.stmat` and `Sounds` into **Asset or folder**, pressing **Add** after each. A folder takes everything in it. Export into `Builds/CoinRunPruned` again, with the box ticked.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.setExportSettings", "parameters": { "alwaysInclude": [ "Prefabs/Coin.stprefab", "Materials/GoldGlow.stmat", "Sounds" ] } }
   ```

   :::
   ::::

   **You should see:** the three entries in the list, and, after the new export and a run, the coins back and no `FindAsset` line in `Game.log`.

   **If you do not see it:** the list refuses an entry that is no asset or folder of the project; check its spelling and case.

:::::

:::caution
A pruned export that runs fine on your desk can lack an asset your game needs later, such as the sound of the last level. Run every pruned export headless and read `Game.log` for `FindAsset` warnings before you give it away.
:::

Before you give the game to players, check four things. Credit what you used: Strata's samples keep a `CREDITS.md`, and a game can show the same table on a credits screen built like the display of [the page on the heads-up display](hud.md). Keep `ThirdPartyNotices.md` beside the game. An exported streamed world waits for its ground to load, which [Large worlds](large-worlds.md) checks. Tell players that an older processor without those extensions will not start the game.

:::note
Strata exports only for the system that runs the editor. It writes no macOS application bundle, signs nothing, collects no crash reports from shipped games and has no tool for patch packs. The index [What Strata does not have](../appendix/not-in-strata.md) lists all of these.
:::

::checkpoint{stage=4}

::figure{id=pruned-pack}

## Summary

- An export writes a folder with the runtime renamed after the game, the manifest, the pack, the script library, the icon and the notices.
- The identity is a title, a version, a company, a copyright line and an icon on the **Game** page; the project's name keys saves and logs.
- **File ▸ Export Game...** exports in the background, and it refuses while a build runs, with a folder inside the project or with changes you did not save.
- A pruned export packs only what scenes use, so assets that scripts load by path go into the always include list on the **Export** page.
- The log is `Logs/Game.log` in the data folder named after the game, and `FindAsset` warnings name a missing path.

## Check yourself

1. Name the files of an export of the project `Rocket` on Windows.

   :::answer{tests="export-contents"}
   `Rocket.exe`, `Rocket.stgame`, `Rocket.stpak`, `RocketScripts.dll` and its `.pdb` when symbols are copied, `Rocket.png` when the game has an icon, and `ThirdPartyNotices.md`.
   :::

2. You rename the title from `Coin Run` to `Coin Dash`. Do players keep their saves?

   :::answer{tests="set-identity"}
   Yes. Saves and logs live in a folder named after the project, `CoinRun`, and not after the title.
   :::

3. A game runs with `--headless --frames 1800`. How many seconds of game time is that, and why does the number of frames decide it?

   :::answer{tests="export-run"}
   30 seconds, because a headless run draws 60 frames per second: $1800 / 60 = 30$.
   :::

4. A pruned export shows no coins, and `Game.log` has a `FindAsset` warning. What do you do?

   :::answer{tests="prune-export read-log"}
   Add the path in the warning, or a folder that holds it, to the list on the page **Export** of **Project Settings**, and export again.
   :::

5. Where do you search for the log of a game exported from the project `CoinRun` on Linux?

   :::answer{tests="read-log"}
   In `~/.local/share/CoinRun/Logs/Game.log`, unless `XDG_DATA_HOME` is set, which then replaces `~/.local/share`.
   :::

## Exercises

1. **Basic.** Run the exported game in a window of 800 by 600 pixels for 5 seconds and save a screenshot. Open the picture.

   :::answer{tests="export-run" solution="tutorials/make/export/exercise-1.tutorial.json"}
   Run `./CoinRun --windowed --resolution 800x600 --seconds 5 --screenshot shot.png` in the export folder. The picture is 800 by 600 pixels and shows the course after 5 seconds of game time.
   :::

2. **Medium.** Predict the exit codes of `./CoinRun --speed 2` and of `./CoinRun --help`. Then run both and read the code with `$?`, or `$LASTEXITCODE` in PowerShell.

   :::answer{tests="export-run"}
   The first prints the problem with `--speed` and the usage and exits with 3; the second prints the usage and exits with 0.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/GameExport.cpp`: the checks before an export and the steps that write the folder.
- `StrataEditor/src/UI/ExportDialog.cpp`: the dialog's fields and its progress.
- `StrataEditor/src/Editor/DesktopEntry.h`: the Linux entry and why it names absolute paths.
- `StrataRuntime/src/RuntimeApplication.cpp`: the options and the exit codes of a game.
- `Strata/src/Strata/Project/GameManifest.h`: the manifest's fields.

## Further reading

- The Desktop Entry Specification of freedesktop.org: the format of the `.desktop` file (intermediate).
- Microsoft's documentation of SmartScreen: why an unsigned program is warned about (beginner).
