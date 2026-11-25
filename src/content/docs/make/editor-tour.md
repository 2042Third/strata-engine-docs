---
id: make/editor-tour
title: "A tour of the editor"
description: "Create Coin Run's project, find every panel of the editor, move the Scene view, play and stop, and learn what the With a command tab of each step means."
kind: tutorial
size: M
tracks: [G, B]
needs: [start/how-to-read, start/what-an-engine-is]
time: 40
learn:
  - id: project
    text: create the CoinRun project from the Basic 3D template and name its five entities
  - id: panels
    text: find every panel, the button strip and the status bar of the default layout, and reset the layout
  - id: view
    text: change the Scene view by orbit, pan, dolly and fly, and frame the selection or the whole scene
  - id: play
    text: run the scene with Play, stop it, show the Game view beside the Scene view and read the notice of a scene without a camera
  - id: commands
    text: explain why every step has a tab With a command and read the commands the editor ran
since: 0.3.0
status: final
---

## What you will make

You create the project that the next pages grow into a game: Coin Run, a small game in which you collect coins. At the end you can find every panel of the editor, move around the scene, play and stop it, and read the command tab of any step in this book.

::figure{id=result}

## What you need

You need the launcher of an installed editor, as [Your first game](../start/first-game.md) left it. If you arrive here first, [Installing Strata and the C++ build tools](../start/install.md) gives you the editor; nothing else is needed, because the first step makes the project. No file needs importing. The tour takes about 40 minutes.

Every step has two tabs. **In the editor** names the clicks. **With a command** names the same action as a command, as [How to read this book](../start/how-to-read.md) taught; on this track you may skip that tab, and the last section says why it is there. A command answers with data, so what a step shows in the window, such as a dialog, a button or a pill, you see only on the screen. The command `editor.screenshot` returns a picture of the window to compare with the page's figures.

## Create the project and find every panel

A new editor looks crowded: a dozen panels, a strip of buttons and a bar at the bottom. You will meet each part once, in the order you need it. First you need a project, because most of the editor stays empty without one.

:::::steps

1. Open the dialog for a new project.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the launcher, press **New Project**.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.create", "parameters": { "directory": "<a new folder>/CoinRun", "name": "CoinRun", "template": "basic3d" } }
   ```

   The command opens no dialog: it makes the project and opens it at once, so it does step 2 as well.

   :::
   ::::

   **You should see:** a dialog with a row of template cards, a **Name** field and a **Location** field.

   **If you do not see it:** the editor opened with a project already, so no launcher shows. Choose **File ▸ Close Project**, answer the question about changes you have not saved, and the launcher appears.

2. Name the project and create it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the **Basic 3D** card, type `CoinRun` in **Name**, keep the default **Location** and press **Create**.
   :::
   :::tab[With a command]
   The command of step 1 does this step too: it creates the project and opens it. Its answer names the project file, and the editor then shows the scene `Scenes/Main.stscene`.
   :::
   ::::

   **You should see:** before you press **Create**, a last line that starts with "Creates" and names the folder. Afterward the editor opens on the scene `Scenes/Main.stscene`.

   **If you do not see it:** **Create** is grey and a yellow line gives the reason, for example that the folder exists. Choose another name.

:::::

The default location is a folder named `StrataProjects` in your home folder. Two other ways out of the launcher exist. **Continue without a project** opens the editor with no project, which is useful to look around. **File ▸ Show Launcher** brings the launcher back from there; it stays grey while a project is open, and then **File ▸ Close Project** is the way.

Now look at the window. The editor is a set of panels: windows that each show one part of your game, which you can drag, stack as tabs and close. The default layout puts them in four areas, between the menus and the button strip above and the status bar below.

The sizes are shares of the space between the button strip and the status bar. In a wide window the Hierarchy takes 15 % of the width, and the Inspector and Asset area 20 %. Each side column keeps room for its rows, though: at least 16 times the height of the text for the Hierarchy, and 18 times for the Inspector. In a window 960 pixels wide, as drawn, they take 23 % and 26 %. The bottom area lies under the views only and takes 22 % of the height.

::figure{id=layout-areas}

<!-- markdownlint-disable MD029 -->
:::::steps

3. Find the eight panels of the default layout.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click each tab and say its place aloud. In the middle are **Scene** and **Game**. On the left is **Hierarchy**. On the right are **Inspector** and **Asset**. At the bottom are **Console**, **Problems** and **Content Browser**.
   :::
   :::tab[With a command]

   ```json
   { "command": "editor.showPanel", "parameters": { "panel": "Console" } }
   ```

   The command opens a panel and brings it to the front. No command closes a panel or resets the layout.

   :::
   ::::

   **You should see:** the **Console** tab comes to the front. The **Hierarchy** lists five entities, and the **Content Browser** shows the folder `Assets`.

   **If you do not see it:** a panel went missing, for example because you closed it, or the window looks unlike the figure. The editor keeps the layout you left last, for your user and not for the project, so an editor you used before opens with that layout, and **Project Settings** may stand beside **Scene** and **Game**. Choose **View ▸ Reset Layout**: every panel returns to its default place.

:::::
<!-- markdownlint-enable MD029 -->

The **Scene** view shows the world from the editor's own camera, the one you move to look around. The **Game** view shows what the game's camera sees. The **Hierarchy** lists the entities, the named things the scene holds, the **Inspector** shows the selected item in detail, and the **Asset** tab does the same for a file of the project. The **Console** collects messages, the **Problems** panel the errors of script builds, and the **Content Browser** the files. The **View** menu also opens the panels that start closed: **Streaming**, **Performance**, **Activity** and **Project Settings**.

An **asset** is a file the game uses: a material, a sound, a model, a scene. The **Content Browser** shows the project's `Assets` folder with the scene `Scenes/Main.stscene` and the material `Materials/Ground.stmat` that Basic 3D made. How to bring in your own files is the subject of [Assets](../make/assets.md).

<!-- markdownlint-disable MD029 -->
:::::steps

4. Read the button strip and the menus.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Hover over each button of the strip under the menus, and open each menu once. A hint names the button and its key.
   :::
   :::tab[With a command]

   ```json
   { "command": "editor.status", "parameters": {} }
   ```

   The answer holds the state behind the strip: the project, the play state, the assets and the errors. The buttons, their keys, World or Local and Snap show only in the window, so take `editor.screenshot` to see them.

   :::
   ::::

   **You should see:** at the left the tools Select, Move, Rotate and Scale with the keys Q, W, E and R, then World or Local and Snap. In the middle you see Play, Simulate, Pause, Step and Stop. At the right you see **Build Scripts** and **Export**.

   **If you do not see it:** the window is narrow and the buttons shrink. Widen the window, or hover to read the hint.

5. Read the status bar.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Look at the bar along the bottom edge. Click the pill that shows a time in milliseconds.
   :::
   :::tab[With a command]

   ```json
   { "command": "editor.showPanel", "parameters": { "panel": "Performance" } }
   ```

   The command opens the panel that the pill opens. The pill itself shows only in the window.

   :::
   ::::

   **You should see:** the **Performance** panel opens and comes to the front.

   **If you do not see it:** the window is narrow and the pills show short texts. Click the one with the gauge icon.

:::::
<!-- markdownlint-enable MD029 -->

Each button gets its own page later: the tools in [Scenes and entities](../make/scenes-entities.md), Play and its neighbors in [Play, test, debug](../make/play-test-debug.md).

The menus hold one idea each. **File** holds projects, scenes, export and **Preferences...**. **Edit** holds undo, redo, copy, paste and delete. **View** holds the panels and **Reset Layout**.

**Entity** creates the things a scene holds. **Scripts** builds and opens the code of your game. **Help** holds the About window.

A pill is a small label in the status bar that shows one stream of work and opens the panel that explains it. The play state pill says Editing, Playing, Simulating or Paused. The frame pill shows the time of a frame and opens **Performance**. The assets pill opens **Streaming**. The automation pill names the agents connected to the editor, or says that none is.

Other pills appear only when they matter: saving, scripts building or failed, and new errors, whose pill opens the **Console**.

The editor has one look, called Bedrock: dark, quiet colors, so that your game's colors stand out. If the interface is too small for your screen, choose **File ▸ Preferences...**, open the **Interface** section and raise **Scale**, for example to 125 %. Preferences hold three sections: the external editor, the interface and the frame rate. Shortcuts cannot be rebound: their keys are written in the editor's code.

::checkpoint{stage=1}

::figure{id=result}

## Move around the Scene view

You will often need to see a scene from another side. The Scene view has its own camera, and moving it changes nothing in your game: no undo step, no change to the scene.

<!-- markdownlint-disable MD029 -->
:::::steps

6. Select the Ground.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the gray floor in the **Scene** view. Then click an empty spot to clear the selection, and click `Ground` in the **Hierarchy**.
   :::
   :::tab[With a command]

   ```json
   { "command": "selection.set", "parameters": { "entities": ["<the id that entity.find gives for Ground>"] } }
   ```

   :::
   ::::

   **You should see:** the `Ground` row highlighted in the **Hierarchy**, an outline on the floor and its components in the **Inspector**.

   **If you do not see it:** another entity took the click, or the selection is empty. Click the row in the **Hierarchy**; it always works.

7. Move the view with the mouse.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Hold the Alt key and drag with the left button to orbit. Drag with the middle button to pan. Turn the wheel to dolly. Hold the right button and press **W**, **A**, **S**, **D**, **Q** and **E** to fly; add the Shift key to go faster.
   :::
   :::tab[With a command]

   ```json
   { "command": "camera.set", "parameters": { "yaw": 45, "pitch": -30, "distance": 10 } }
   ```

   A negative `pitch` tilts the view down at the floor, and a positive one tilts it up.

   :::
   ::::

   **You should see:** the floor turn, slide and grow or shrink as you move.

   **If you do not see it:** nothing moves when the mouse is outside the **Scene** view. Move the pointer over the view before you drag.

8. Frame what you want to see.

   ::::tabs{sync=how}
   :::tab[In the editor]
   With the mouse over the **Scene** view, press **F** to frame the selection. Press **Home** to frame the whole scene.
   :::
   :::tab[With a command]

   ```json
   { "command": "camera.focus", "parameters": { "entities": ["<the id of Ground>"] } }
   ```

   Without `entities`, the command frames the whole scene, as **Home** does.

   :::
   ::::

   **You should see:** the camera backs off or moves in until the floor, or the whole scene, fits the view.

   **If you do not see it:** **F** does nothing while nothing is selected, and the keys reach the view only while the pointer is over it or it has the focus. Select `Ground` again, keep the pointer over the **Scene** view and press the key again.

:::::
<!-- markdownlint-enable MD029 -->

The editor camera orbits a pivot point, its target. **Alt** and the left button swing the camera around the target, the middle button slides camera and target together, and the wheel moves the camera toward or away from the target. Fly mode is different: the camera moves through the world like a person, and the wheel then changes the flying speed.

The dolly shows the idea with numbers. A new editor camera is 10 units from its target. Each wheel step toward the target multiplies the distance by 0.85. After one step the distance is 8.5, after two 7.225, and after three about 6.14. The steps shrink as you near the target, so you never cross it by accident.

The scene holds five entities. An entity is a named thing in a scene, and you read them in the **Hierarchy**.

**Main Camera** is the eye of the game; the Game view shows what it sees. **Sun** is the light. **Sky** draws the sky and its air. **Ground** is a floor of 20 by 20 units, and **Post Process** sets the picture's colors and brightness.

Each entity holds components, the parts that give it its look and behavior, such as the Camera component of the Main Camera; the **Inspector** lists them. [Scenes and entities](../make/scenes-entities.md) explains them.

::checkpoint{stage=2}

::figure{id=ground-selected}

## Play the scene and read the commands

Until now you only looked. The scene runs when you press Play, and the Game view then shows the game as a player sees it. The editor keeps what you edited apart from what runs: when you stop, the scene is as it was.

<!-- markdownlint-disable MD029 -->
:::::steps

9. Play the scene and put the Game view beside the Scene view.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, or the **Play** button. The **Game** tab comes to the front. Drag the **Game** tab to the right edge of the **Scene** view and release it there. Then click the **Game camera** chip at the top of the **Scene** view, or press **F8**.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": {} }
   ```

   The command plays the scene and answers with the play state. Docking a tab and the **Game camera** chip have no command: they change only the window.

   :::
   ::::

   **You should see:** the two views side by side. The **Game** view shows the scene through the Main Camera, and the **Scene** view, with the chip on, shows the same picture with the editor's overlays. The status bar says Playing.

   **If you do not see it:** the scene is still loading, or the **Play** button is grey while a script builds. Wait a moment. A drag that docks nowhere leaves the tabs as they were; try the edge again.

10. Stop, then clear the camera's **Primary** box.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Press **Ctrl+P** again. Click `Main Camera` in the **Hierarchy**, and in the **Inspector** clear the **Primary** box of the **Camera** component.
    :::
    :::tab[With a command]

    ```json
    { "command": "play.stop", "parameters": {} }
    { "command": "component.set", "parameters": { "entity": "<the id of Main Camera>", "component": "Camera", "values": { "Primary": false } } }
    ```

    To see what the **Game** view now shows, ask for its picture: `viewport.capture` with `"camera": "scene"` fails, and its message says the same as the view's text.

    :::
    ::::

    **You should see:** the scene as it was before Play. In the **Game** view the picture gives way to the text "No camera to show", which says the scene has no active entity with a Camera component marked Primary.

    **If you do not see it:** the **Camera** component sits in a collapsed section of the **Inspector**. Click its title to open it.

    ::figure{id=no-camera}

11. Undo the change and read the journal.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Press **Ctrl+Z**. Then choose **View ▸ Activity**.
    :::
    :::tab[With a command]

    ```json
    { "command": "edit.undo", "parameters": {} }
    { "command": "editor.activity", "parameters": { "source": "Automation" } }
    ```

    The second command reads the journal of your client's commands. It lists every one, oldest first, also those that only read, such as `entity.find`, so search for the rows of `play.start` and `component.set` among them.

    :::
    ::::

    **You should see:** the picture returns to the **Game** view. The **Activity** panel lists rows for the commands your steps ran, such as `play.start` and `component.set`, each with the client that ran it.

    **If you do not see it:** **Changes only** is checked. It keeps only the commands that edit the scene, its assets or the project, and so it hides `play.start`. Clear it.

:::::
<!-- markdownlint-enable MD029 -->

The **Game** view has a resolution menu, a chip at the top. It sets the shape of the picture. **Free** fills the panel, and the ratios 16:9, 16:10, 4:3 and 21:9 keep a shape. Fixed sizes such as 1920 x 1080 show the game at the pixels a player would have.

The Scene view has more chips, for debug views, quality and lighting. [Lighting](../make/lighting.md) and [Quality](../make/quality.md) explain them.

Two small rules decide which keys go where. The panel under focus gets the keys: **F2** renames in the **Hierarchy**, and **F** and **Home** work in the **Scene** view, which also takes them while the pointer is over it. A few shortcuts work in every panel: **Ctrl+S** saves, **Ctrl+Z** undoes and **Ctrl+P** plays and stops. While the game plays in a focused **Game** view, its keys go to the game instead, and a game that locks the mouse keeps it until you press **Shift+F1**. **Ctrl+P** always stops the game.

Why does every step have a command tab? Because every click you made ran a command. A command is a named action of the editor, with JSON parameters, such as `play.start` or `component.set`. A click is a command with a button on it.

The editor has one set of commands and three clients that run them. The first is the editor's own interface. The second is the command line program `StrataCLI`, which artificial intelligence (AI) agents use. The third is a command script, a file of commands that the editor runs in order. One set means that what you do by hand, an agent does the same way and a script can repeat.

The **Activity** panel lists the commands of all three clients. [With an AI agent](../make/with-an-agent.md) shows it at work, and [Commands](../make/commands.md) teaches you to run your own.

```mermaid caption="Three clients send commands to one set of commands in the editor, and the commands change the project." alt="Three boxes on the left: the editor's interface, the command line program and a command script. Each has an arrow to a box named the editor's commands, which has an arrow to a box named the scene and project."
flowchart LR
    A[Editor interface] --> R[Editor commands]
    B[Command line program] --> R
    C[Command script] --> R
    R --> S[Scene and project]
```

::checkpoint{stage=3}

::figure{id=side-by-side}

## Summary

- You create `CoinRun` from the Basic 3D template and name its five entities: Main Camera, Sun, Sky, Ground and Post Process.
- You find the eight docked panels, the button strip and the status bar, and **View ▸ Reset Layout** brings back a missing panel.
- You orbit, pan, dolly and fly the Scene view, and **F** and **Home** frame the selection and the scene.
- You play and stop with **Ctrl+P**, show the Game view beside the Scene view, and read the notice of a scene without a primary camera.
- You know that every click runs a command, which is why each step has a tab **With a command**.

## Check yourself

1. You press **Create** and the editor opens on a scene with five entities. Name two of them and say what each does.

   :::answer{tests="project"}
   Main Camera is the eye through which the game is shown. Sun is the light. Sky draws the sky and Ground is the floor. Post Process sets colors and brightness.
   :::

2. The **Hierarchy** panel has vanished from your window. Which menu entry restores it along with all other panels, and what else does that entry do?

   :::answer{tests="panels"}
   **View ▸ Reset Layout** puts every panel back in its default place and also returns each panel to its default open or closed state. **View** also lists each panel, so you can open one alone.
   :::

3. The camera sits 10 units from its target. You turn the wheel two steps toward the target. How far is it now?

   :::answer{tests="view"}
   Each step multiplies the distance by 0.85. Two steps give 10 × 0.85 × 0.85 = 7.225 units.
   :::

4. A friend says the editor shows "No camera to show" in the **Game** view. What do you check first, and where?

   :::answer{tests="play"}
   Check the **Primary** box of the Camera component of the Main Camera, in the **Inspector**. The text says the scene has no active entity with a Camera component marked Primary. **Ctrl+Z** brings the box back if you cleared it.
   :::

5. You wrote a command by hand and want to know whether the editor ran it. Where do you look?

   :::answer{tests="commands"}
   Choose **View ▸ Activity**. The panel lists every command that the interface, the command line program and command scripts ran, each with its client.
   :::

## Exercises

Exercises 1 and 2 have no command: closing a panel, **Reset Layout** and the pills work only in the editor's window.

1. **Basic.** Close the **Hierarchy** and the **Console**, open each again from the **View** menu, then choose **View ▸ Reset Layout**.

   :::answer{tests="panels"}
   Click the small cross on each tab, then tick **Hierarchy** and **Console** in **View**. Reset Layout then restores the default places. Hint: a panel closed by its tab shows an empty tick box in **View**.
   :::

2. **Medium.** Click each pill of the status bar and name the panel it opens.

   :::answer{tests="panels"}
   The frame pill opens **Performance**, the assets pill opens **Streaming**, a saving pill opens **Activity**, and an errors pill opens the **Console**. The play state pill opens nothing; it only shows the state.
   :::

3. **Hard.** Clear **Primary** and bring it back with commands only, then list the journal's entries from the command line client.

   :::answer[Worked solution]{tests="commands play" solution="tutorials/make/editor-tour/exercise-3.tutorial.json"}
   Run `component.set` on the Main Camera with the values `{ "Primary": false }`, then `edit.undo`, then `editor.activity` with the parameter `source` set to `Automation`. Hint: find the camera's id with `entity.find`.

   ```json
   { "command": "editor.activity", "parameters": { "source": "Automation" } }
   ```

   The last result lists every command your client ran in this session, oldest first, also the queries such as `entity.find`. Near its end stand the `component.set` and the `edit.undo`. Add `"command": "component.set"` to the parameters to list only that command's rows.
   :::

## Where it lives in Strata

The panels are registered in `StrataEditor/src/EditorLayer.cpp`, which also builds the default layout and draws the menus, the button strip and the status bar. The Scene view is `StrataEditor/src/Panels/ViewportPanel.cpp`, and its camera is `StrataEditor/src/Editor/EditorCamera.h`. The Game view is `StrataEditor/src/Panels/GameViewPanel.cpp`. The template that made your project is `StrataEditor/src/Editor/ProjectTemplates.cpp`.

## Further reading

- The editor's manual page on the Scene view and the Game view in the Strata documentation: a longer account of both views (beginner).
