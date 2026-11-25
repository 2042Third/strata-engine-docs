---
id: make/project-files
title: "Projects, saving, undo and recovery"
description: "Learn what Coin Run's project folder holds, and keep your work with saving, undo and the recovery that follows a crash."
kind: how-to
size: M
tracks: [G, B]
needs: [make/editor-tour]
time: 35
learn:
  - id: project-folder
    text: name the files and folders of a project and say which ones the editor rebuilds
  - id: hand-edit
    text: explain why project, scene, material and handle files change only in the editor
  - id: undo-save
    text: predict the name that the Edit menu shows for an undo step and which changes need a save
  - id: recover-work
    text: find the changes of a crashed session in the recovery dialog and apply or discard them
since: 0.3.0
status: final
---

Your game lives in one folder on your disk. This page shows you what is inside it, so that you can move it, copy it and keep it under version control without breaking it. You also learn the four ways Strata protects your work: saving, undo, a question before anything is discarded, and recovery after a crash. Before you start:

- The Coin Run project of [the editor tour](editor-tour.md) is open in the editor, with its scene shown.
- You have a plain text editor that can open a file.

The page changes nothing in Coin Run. Every change a step makes, you undo, discard or never save, so the project ends as it began.

## Why a project is a folder

A **project** is one folder that holds everything of one game: the project file, the assets, the scripts and the files the editor makes for itself. Strata keeps your work as plain text documents. A scene, a material and the project's settings are each one text file that a person or a tool can read.

Next to every asset file sits a small file ending in `.meta`. It stores the asset's **handle**, a long number that never changes. A scene refers to a material by that number, never by its file name. The editor keeps an index of handles and references, so it can rename a file and the scene still finds it.

That index is the reason for one rule of this page. If you rename, move or delete a file in your file browser, the index does not hear about it, and a scene can point at nothing. The editor also records every change it makes, which is what undo needs. A change you make by hand in a text editor leaves no record.

:::rule
Never edit `.stscene`, `.stmat`, `.stproj` or `.meta` files by hand, and move, rename and delete them only in the editor. The editor indexes handles and references, and a hand edit bypasses undo. The rule is in the engine's guide for developers, and it holds for game makers too. Reading these files is always safe: this page opens two of them only to look.
:::

## Look at the project and keep your work

:::::steps

1. Close the project to see the launcher, the window with one card for each project you opened lately.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Close Project**. If the scene has changes you did not save, the editor asks about them first. The launcher appears with a card for `CoinRun`. Right-click the card to open a menu with **Open**, **Show in Folder**, **Copy Path** and **Remove from List**. Choose **Copy Path**.
   :::
   :::tab[With a command]

   ```json
   { "command": "editor.recentProjects" }
   ```

   The command closes nothing: it lists the launcher's cards, each with the `path` of its project file and when you opened it last. Copy the `path` of `CoinRun` from the answer, in place of **Copy Path**.

   :::
   ::::

   **You should see:** the launcher with the card `CoinRun`, showing the folder it lives in and when you opened it. The list keeps the last 12 projects, and a project whose project file is gone is hidden. **File ▸ Open Recent** lists the same projects while a project is open.

   **If you do not see it:** the menu item is grey when no project is open. If the card is missing, the list lost it: choose **Open Project...** and pick `CoinRun.stproj`.

   Paste the copied path into a text editor. A path names a file by the folders that lead to it. On Windows it looks like `C:\Users\you\Documents\CoinRun\CoinRun.stproj`: a drive letter, then folders separated by backslashes. On Linux and macOS it looks like `/home/you/CoinRun/CoinRun.stproj`, or `/Users/you/` on macOS: it starts at the root `/`, and a slash separates the folders.

   The last part is the file, and the folder before it is the project's folder. Now click the card to open Coin Run again, or choose **Show in Folder** to see the folder in your file browser.

2. Make your file browser show file extensions and hidden files.

   An extension is the end of a file name after its last dot: `.stproj` marks a project, `.stscene` a scene and `.stmat` a material. The system hides extensions by default, but you need them to tell `CoinRun.stproj` from other files. On Linux and macOS a name that starts with a dot, such as `.strata`, is hidden by convention, because such files belong to programs rather than to you. On Windows hiding is an attribute of the file, so `.strata` may show even with the box cleared.

   ::::tabs{sync=os}
   :::tab[Windows]
   In File Explorer open the "View" menu, then "Show", and tick "File name extensions" and "Hidden items".
   :::
   :::tab[Linux]
   In the Files app press **Ctrl+H** to show hidden files. Extensions show already.
   :::
   :::tab[macOS]
   In Finder press **Cmd+Shift+.** to show hidden files. Open "Finder" then "Settings" then "Advanced" and tick "Show all file name extensions".
   :::
   ::::

   **You should see:** names such as `CoinRun.stproj` with their endings, and a folder called `.strata`.

   **If you do not see it:** the key toggles, so press it again if the files vanish. Press it while the window of the project's folder is the active one.

3. Read the folder against this tree.

   :::files[The folder of the project `CoinRun`]

   - `CoinRun/` the project's folder
     - `CoinRun.stproj` the project file: its name, start scene and settings
     - `Assets/` the game's assets
       - `Scenes/Main.stscene` the scene you edit, with `Main.stscene.meta` beside it
       - `Materials/Ground.stmat` the material of the ground, with its `.meta` file
       - one `.meta` file beside every asset
     - `Scripts/` the game's code
       - `CMakeLists.txt` how the editor builds the scripts
       - `Spinner.cpp` the example script
       - `CMakePresets.json` the build settings for this computer, written by the editor once it has found your :term[build tools]{id=build-tools}
       - `.gitignore` keeps `CMakePresets.json` out of version control, written with it
     - `.strata/` what the editor makes for itself: the import cache, script builds, thumbnails, recovery files, saves made while playing and the trash of deleted assets
     - `.gitignore` keeps `.strata/` out of version control

   :::

   Everything outside `.strata/` is your work. The editor makes `.strata/` again when it is missing, so you can delete that folder to free space. Deleted assets wait in its trash, though, and recovery files live there too: both are gone for good once you delete it.

   Git is a tool that keeps every version of the files you save with it. It reads a `.gitignore` file to learn which files to omit. [Git and version control](../basics/git.md) teaches it, and you can read it later.

   **You should see:** each file of the tree in your file browser, with the `.meta` files beside the assets.

   **If you do not see it:** `.strata` and the `.gitignore` files are hidden until step 2 works. A new project may have no `CMakePresets.json` and no `.gitignore` in `Scripts` yet. The editor writes both once it has found your :term[build tools]{id=build-tools}, at the latest at the first build of the scripts, which [Your first script](first-script.md) makes.

4. Open `CoinRun.stproj` in a text editor, only to look.

   The file is JSON, the text format you met in [How to read this book](../start/how-to-read.md): objects in braces, names with values. The Tetris sample's project file shows the shape. The editor starts each line of its files with tab characters, and the book draws each tab as two spaces, so your text editor may show wider steps.

   ```json src="Samples/Tetris/Tetris.stproj#L1-L22"
   {
   	"Project": {
   		"AssetDirectory": "Assets",
   		"Game": {
   			"Company": "",
   			"Copyright": "",
   			"Icon": "F8DFB22B97ABAE5B",
   			"Title": "Tetris",
   			"Version": "1.0.0"
   		},
   		"Name": "Tetris",
   		"Scripts": {
   			"ModuleName": "TetrisScripts",
   			"SourceDirectory": "Scripts"
   		},
   		"StartScene": "BD75622ED18E84E4"
   	},
   	"Strata": {
   		"Format": "Project",
   		"Version": 3
   	}
   }
   ```

   1. **Line 2:** the `Project` part describes the game and where its files are.
   2. **Lines 4–10:** `Game` holds what the exported game says about itself. Coin Run's file writes it only after you change the Game page.
   3. **Lines 11–15:** the name, and the folder and module of the scripts.
   4. **Line 16:** `StartScene` is a handle, the number in the scene's `.meta` file.
   5. **Lines 18–20:** the `Strata` part names the format and its version, so that future editors read the file correctly.

   Coin Run's file has the same shape. A part named `Settings` appears in it once a Project Settings page holds a value other than its default: it has one member for each page, with names such as `Scene.Timing`. The editor writes the file in the background whenever a setting changes.

   **You should see:** a short file of braces and names, with `"Name": "CoinRun"`.

   **If you do not see it:** you opened another project's file. Close it without saving, and never save a change to it.

5. Open the settings pages with **File ▸ Project Settings...**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Project Settings...**. A list of pages appears on the left, and the chosen page on the right.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.settings" }
   ```

   The answer's `sections` are the pages under Input, Physics and Rendering, each with its `title` and `category`: `Renderer.Quality` has the title `Graphics Quality`. The **Game** and **Export** pages show the project's own fields, which the answer holds under `project`.

   :::
   ::::

   **You should see:** the pages in four groups: **Game** and **Export** under Project, **Input Actions** under Input, **Collision Layers**, **Timing** and **Simulation** under Physics, and **Graphics Quality** under Rendering. **Game** names the start scene, the game's title, version, company and icon. [Exporting a game](export.md) uses **Game** and **Export**, [Input](input.md) uses **Input Actions**, [Physics](physics.md) uses the layers and **Simulation**, [the script loop](script-loop.md) uses **Timing**, and [Graphics quality](quality.md) uses **Graphics Quality**.

   ::figure{id=project-settings}

   **If you do not see it:** the menu item is grey while no project is open. Open Coin Run first.

   **Why:** a settings change is one undo step, named after its page, such as `Set Timing`, and it does not mark the scene as changed.

6. Save the scene with **Ctrl+S**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S**, or choose **File ▸ Save Scene**. **File ▸ Save Scene As...** writes a copy under another name.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   ```

   The command answers once the file is written, with its size in bytes. The pill shows only in the window.

   :::
   ::::

   **You should see:** a pill in the status bar reading `Saving 'Main'` with a percentage, for a moment. A small scene is written so fast that you may miss it.

   **If you do not see it:** the save finished before the pill drew. The editor writes a save in the background, so you can keep working while it runs, and edits you make meanwhile wait for the next save. Quitting waits until the save is written.

7. Change two things, then undo them one at a time.

   Rename the Ground in the hierarchy: select it, press **F2**, type `Floor` and press **Enter**. Then select the Sun and drag its arrow in the scene view a short way.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the **Edit** menu. The menu names the step it would undo. Choose it, or press **Ctrl+Z**. Press **Ctrl+Z** again for the second change. **Ctrl+Y** and **Ctrl+Shift+Z** redo.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.rename", "parameters": { "entity": "<the Ground's ID>", "name": "Floor" } }
   { "command": "component.set", "parameters": { "entity": "<the Sun's ID>", "component": "Transform", "values": { "Translation": [0, 10, 0] } } }
   { "command": "edit.history" }
   { "command": "edit.undo" }
   { "command": "edit.undo" }
   ```

   A command's step has its own name: `edit.history` lists `Rename 'Ground' to 'Floor'` and `Set Translation of 'Sun'`, where a drag gives `Move Entity`. The two `edit.undo` calls undo both changes.

   :::
   ::::

   **You should see:** first `Undo Move Entity`, then `Undo Rename 'Ground' to 'Floor'`, and the entity names return as you undo. The whole drag is one step, however many frames it took. Undo and redo are unavailable while the game plays. The drawing shows the menu after both changes, with the Sun still selected.

   ::figure{id=edit-menu-drawing}

   **If you do not see it:** an item in **Edit** is grey when there is nothing to undo. Undo both steps before you continue, so Coin Run is as before.

8. Meet the question before changes are lost.

   Rename the Ground again, so that the scene has a change you did not save. Then choose **File ▸ Open Scene...** and pick `Main.stscene` in the dialog.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Open Scene...** and pick the scene's file. A dialog named **Unsaved Changes** asks whether to save the scene. Choose **Cancel**.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/Main.stscene" } }
   ```

   The command opens no dialog. It refuses and names the two ways on: save first with `scene.save`, or pass `"force": true`, which discards the change. Pass neither here: a discarded change is kept as recovery data, and step 9 would then show it as a second entry.

   :::
   ::::

   **You should see:** the question `Save changes to 'Main'?` with **Save**, `Don't Save` and **Cancel**. The command refuses and tells you why. **File ▸ New Scene**, **File ▸ Close Project** and closing the window ask the same question.

   **If you do not see it:** you made no change since the last save. Rename the entity and try again. Press **Ctrl+Z** afterwards to undo the rename.

9. End the editor from outside, as a crash would, and recover.

   Rename the Ground once more and wait ten seconds. The editor wrote a **recovery journal**: a file under `.strata/Recovery` that records the scene changes you have not saved, so that a crash does not lose them. It writes the file two seconds after your edits stop, and at least every ten seconds while you keep editing.

   ::::tabs{sync=os}
   :::tab[Windows]
   Open the Task Manager, find `StrataEditor.exe` on its "Details" page, select it and choose "End task", or run `taskkill /F /IM StrataEditor.exe` in a terminal. The command ends every Strata editor that runs. With more than one, read the process identifier (PID) in the "PID" column of your editor's row and run `taskkill /F /PID <that number>`.
   :::
   :::tab[Linux]
   Run `pkill -KILL StrataEditor` in a terminal, or use Kill in the System Monitor. The command ends every Strata editor that runs; with more than one, use the System Monitor.
   :::
   :::tab[macOS]
   Press **Cmd+Option+Esc**, select Strata Editor and choose "Force Quit", or run `pkill -KILL StrataEditor` in a terminal. The command ends every Strata editor that runs; with more than one, use the window.
   :::
   ::::

   Start the editor and open Coin Run from its card. The dialog **Recover Unsaved Changes** opens by itself.

   Choose **Discard**, so Coin Run stays as it was. **Later** closes the dialog and keeps the changes, **Recover** applies them as one undo step, and **File ▸ Recover Unsaved Changes...** opens the dialog again. As commands, `scene.recoveryStatus` lists what is kept, newest first, each entry with its `id`. `scene.recover` applies or discards one entry: it takes that `id` as `scene` and `"apply"` or `"discard"` as `action`.

   ::figure{id=recovery-dialog}

   **You should see:** an entry with the scene's name and its change, and Coin Run opens with the Ground's old name. Changes you discarded on purpose earlier, with `Don't Save` or a command's `force`, are kept too and stand in the list as more entries, each marked as discarded on purpose; discard them as well.

   **If you do not see it:** the editor closed in order, and then it asked about the change instead. An ordinary quit, or a plain `kill`, is no crash. Without a crash, nothing was kept to recover.

:::::

## Result

You can name every file of Coin Run's folder, and you know which ones the editor rebuilds. You keep your work in four ways: a save, an undo, a question before a discard and a recovery after a crash. Coin Run is unchanged, so [Scenes and entities](scenes-entities.md) starts from the same project.

## Variations

**A project from an older release.** Open it in the new editor and the editor migrates it. Projects of release 0.5.0 keep their collision layers in each scene. Release 0.6.0 and later read the layers of the scenes when they open such a project, and make them the project's. Then the editor saves the project file in the new format, version 3.

Release 0.5.0 cannot open the new file, so copy the folder first. A scene file changes only when you save the scene. The notes of 0.6.0, in "Upgrading from 0.5.0", say more.

**A folder that a cloud drive syncs.** The editor writes each save as a whole file at once, so a sync tool sees an old file or a new one. Leave `.strata/` out of the sync if the tool allows it: the editor rebuilds it, and its files change all the time. Open a synced project on one computer at a time.

**A scene under version control.** A `.stscene` holds one entity on each line, so files compare entity by entity. Put the project in Git and save the scene. Then move one entity in the editor and save again.

A diff of `Assets/Scenes/Main.stscene` shows one removed line and one added line, for the entity that moved. Read such a diff in a text editor or in Git. Never edit the scene to fix a conflict: the rule above holds there too.

## Summary

- A project is one folder: `CoinRun.stproj`, `Assets/` with a `.meta` file beside every asset, `Scripts/`, and `.strata/`, which the editor rebuilds and Git omits.
- Project, scene, material and `.meta` files change only in the editor, because it keeps the index of handles and references and records every change for undo.
- Each action is one undo step that **Edit** names, a whole drag is one step, and a project settings change is a step that does not mark the scene as changed.
- Saves run in the background, the editor asks Save, `Don't Save` or Cancel before it discards changes, and the recovery journal keeps changes you did not save for **Recover Unsaved Changes** after a crash.

## Check yourself

1. A friend deletes `.strata` from their project to save space. What happens when they open it?

   :::answer{tests="project-folder"}
   The editor makes the folder again, with its import cache and script builds, so the game itself is safe. The friend loses the recovery files and the trash: assets they deleted earlier can no longer come back.
   :::

2. You rename `Grass.stmat` in your file browser. Why does the scene that uses it break, and what should you have done?

   :::answer{tests="hand-edit"}
   The scene refers to the material by the handle in its `.meta` file, and the editor's index of handles and files does not know about the rename. Rename it in the editor's asset browser instead, which updates the index and can be undone.
   :::

3. You drag the Sun in one long movement, then press **Ctrl+Z** once. How much comes back?

   :::answer{tests="undo-save"}
   The whole drag. The editor records one undo step for the drag, however long it takes, and the **Edit** menu names it `Undo Move Entity`.
   :::

4. You change the Timing page and look at the scene's title. Do you need to save the scene now?

   :::answer{tests="undo-save"}
   No. A settings change is an undo step that writes the project file in the background and leaves the scene saved. You need to save only after an edit of the scene itself.
   :::

5. The editor was killed ten seconds after your last edit. What do you do next, and what if the editor had quit normally?

   :::answer{tests="recover-work"}
   Open the project. The dialog **Recover Unsaved Changes** offers the kept changes: **Recover** applies them, **Discard** drops them. After a normal quit the editor had asked Save, `Don't Save` or Cancel, so nothing was left to recover.
   :::

## Exercises

1. **Basic.** Rename the Ground to `Floor`, move the Sun, and change the **Fixed Rate** on the Timing page to 120. Predict the three names that **Edit ▸ Undo** shows in turn, then undo all three to check.

   :::answer[Worked solution]{tests="undo-save" solution="tutorials/make/project-files/exercise-1.tutorial.json"}
   The names, newest first, are `Undo Set Timing`, then `Undo Move Entity`, then `Undo Rename 'Ground' to 'Floor'`. After the third undo, **Edit** has nothing to undo. The command file does the same with `entity.rename`, `component.set` and `project.setSettings`, and reads with `scene.info` that the scene now runs the project's 120 steps a second. It reads `edit.history`, undoes the three steps with `edit.undo`, and checks that the scene's own rate and the name `Ground` are back. The names depend on how you move the Sun: a drag of the :term[gizmo]{id=gizmo-start} is `Move Entity`, a value typed in the Inspector `Edit Transform Translation`, and the command's `component.set` is `Set Translation of 'Sun'`, which the file checks.

   The settings change as a command takes the section and its whole `value`:

   ```json
   { "command": "project.setSettings", "parameters": { "section": "Scene.Timing", "value": { "FixedRate": "120" } } }
   ```

   The rate is a choice, written as text: `"120"`, one of `Scene`, `30`, `60`, `120` and `240`. A number such as 120 without quotes is refused.
   :::

2. **Medium.** With a change you did not save, predict which of **File ▸ New Scene**, **File ▸ Open Scene...** and closing the window ask Save, `Don't Save` or Cancel first. Try each, and answer **Cancel**.

   :::answer[Worked solution]{tests="undo-save, recover-work"}
   All three ask, since each would discard the change. **Cancel** keeps the scene and the change, so you can save it or undo it afterwards.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Project/Project.cpp` creates the project folder and writes and reads `.stproj`.
- `StrataEditor/src/Editor/ScriptProject.cpp` writes the script files of a new project.
- `StrataEditor/src/Editor/SceneRecovery.h` keeps the recovery journal; `StrataEditor/src/UI/RecoveryDialog.h` draws its dialog.
- `StrataEditor/src/EditorLayer.cpp` draws the **File** and **Edit** menus, the saving pill and the question about changes.
- `Strata/src/Strata/Scene/SceneDocumentWriter.h` writes a scene one entity to a line.

## Further reading

- The engine's release notes for 0.6.0, section "Upgrading from 0.5.0": what changes when an old project opens. Beginner.
- Pro Git, the chapter "Getting Started": what version control is and why it helps. Beginner.
