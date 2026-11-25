---
id: start/first-game
title: "Your first game"
description: "Play a finished sample, make a project from a template, drop a cube onto a ramp with physics, and turn another cube with a script you change."
kind: tutorial
size: L
tracks: [G, E, B]
needs: [start/install]
time: 90
learn:
  - id: sample
    text: run a copy of the Tetris sample, play it and stop it
  - id: project
    text: create a project from the Basic 3D template and name the five entities of its scene
  - id: physics
    text: add a cube with a physics body, a ramp and a slippery surface, and play the scene
  - id: script
    text: build the Spinner script, attach it to a cube, change its field and read the line it writes
status: final
---

## What you will make

You play a finished game first. Then you make a project of your own: a cube falls onto a ramp and slides down it, and a second cube turns because of a C++ script that you change.

::figure{id=result}

## What you need

- The editor and the C++ build tools from [Installing Strata and the C++ build tools](../start/install.md).
- A code editor for C++ files. Visual Studio Code or Visual Studio will do.
- About 90 minutes. No file needs importing: the Tetris sample comes with the editor, and the new project writes its own files.

On macOS, the editor's menus print **Ctrl**, but the key to press is **Cmd**. Every shortcut below, such as **Ctrl+B**, follows that rule.

Each step has two tabs. **In the editor** shows the menus and clicks. **With a command** shows the same action as an editor command, which is how tools and artificial intelligence (AI) agents drive the editor. [How to read this book](../start/how-to-read.md) explains both tabs.

## Play a finished game

Before you build anything, see what a finished game looks like in the editor. Strata ships five **samples**: finished games made with the editor, which the launcher offers as copies. Opening one never changes the original, so you can break your copy freely.

The launcher is the window the editor shows when no project is open. It has a button for a new project, a button for a project you made before, one for samples, and a card that connects an AI agent. You use the agent card later, on [Making a game with an AI agent](../make/with-an-agent.md).

:::::steps

1. Start the editor.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the `StrataEditor` program in the folder where you unpacked it on [the install page](../start/install.md). The launcher appears, with the title "Welcome to Strata".
   :::
   :::tab[With a command]
   In a terminal in that folder, type the line of your system: the first on Windows, the second on Linux and macOS.

   ```text
   .\StrataEditor
   ./StrataEditor
   ```

   :::
   ::::

   **You should see:** the launcher. **Recent projects** says "No recent projects yet", because you have made none, and cards under **Start something new** offer the templates and the samples.

   **If you do not see it:** a window with an error report opened. Read [the log at the end of the install page](../start/install.md) and fix what it names.

   ::figure{id=launcher}

2. Make your own copy of the Tetris sample.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Open Sample...** and choose **Tetris** in the list that opens. In the **Open Sample** dialog, leave the **Folder** name `Tetris`, keep the **Location** the dialog offers or press **Browse...** to choose another folder, and press **Copy and Open**.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.openSample", "parameters": { "sample": "Tetris", "directory": "<a new folder>/Tetris" } }
   ```

   :::
   ::::

   **You should see:** the editor leaves the launcher and shows the Tetris scene, a well drawn in the **Scene** view.

   **If you do not see it:** the dialog says the folder exists. Type a new name in **Folder** and press **Copy and Open** again.

3. Play the copy.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press the Play button, the triangle at the top of the editor, or press **Ctrl+P**.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   ```

   The command leaves the views as they are: click the **Game** tab to see the game.

   :::
   ::::

   **You should see:** the status bar at the bottom shows "Building to play" with the seconds that passed. When it ends, the **Game** view comes forward and shows the well.

   **If you do not see it:** a message, called a toast, appears in a corner and names what to install, for example the "Desktop development with C++" workload of Visual Studio. Install it, then press Play again. The toast has a **Show Problems** button, and the status bar then shows "Build failed".

4. Play Tetris, then stop it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click inside the **Game** view once, then play with the keys of the table below. To leave, press the Stop button, the square next to Play, or press **Ctrl+P** again.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.stop" }
   ```

   Playing is for your hands: a command can press a key, as [Automated play-tests](../make/automated-playtests.md) teaches, but cannot watch the blocks for you. This command only stops the game.

   :::
   ::::

   **You should see:** the blocks fall and obey your keys; after you stop, the Scene view returns.

   **If you do not see it:** the keys do nothing. The game reads the keyboard only while the **Game** view has the focus, so click inside it again.

:::::

The first **Play** did more than start a game. The Tetris copy is written in C++, and the editor had to turn that code into a program before it could run. That step is a **build**: a compiler reads the source code and writes a file the computer can run. This first build also checked the build tools you installed. If it had failed, the toast told you what was missing.

| Key | Action |
| --- | --- |
| Left, Right, or A, D | Move the piece |
| Down or S | Drop it faster |
| Space | Drop it at once |
| Up or X, Z | Turn it clockwise, or counterclockwise |
| P | Pause |
| R, or Enter after the game ends | Start again |
| Escape | Quit the game, which stops Play as the Stop button does |

::checkpoint{stage=1}

::figure{id=tetris-playing}

## Make a project

Tetris was a project, and you used it as one. A **project** is the folder of one game: its scenes, its materials and sounds, its scripts and the settings the editor needs to open it again. Your own game needs a project too. You do not start from an empty folder: a **template** is a ready-made starting point, and the Basic 3D template gives you a scene that already has a camera, light, sky and ground.

:::::steps

1. Open the dialog for a new project.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ New Project...**.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.create", "parameters": { "directory": "<a new folder>/FirstGame", "name": "FirstGame", "template": "basic3d" } }
   ```

   :::
   ::::

   **You should see:** the **New Project** dialog with two template cards, **Empty** and **Basic 3D**.

   **If you do not see it:** a dialog asks whether to save the scene you changed. Answer it first; the **New Project** dialog follows.

2. Complete the dialog and create the project.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the **Basic 3D** card. Type `FirstGame` in **Name**, keep or change the **Location**, and press **Create**.
   :::
   :::tab[With a command]
   The command of the previous step does this step too: it makes the project and opens it.
   :::
   ::::

   **You should see:** the dialog's last line, "Creates" and a path, before you press **Create**. Afterward the editor shows a scene with a grey-brown ground under a blue sky.

   **If you do not see it:** **Create** is grey and a yellow line says why, for example that the folder name already exists. Choose another name.

   ::figure{id=new-project}

:::::

Look at the **Hierarchy** panel on the left. A **scene** is one place of the game, a list of things and where they stand. Each thing in it is an **entity**: a named object that holds nothing but the components you give it. The template's scene has five entities.

**Main Camera** is the eye through which the game is shown. **Sun** is the light. **Sky** draws the sky and its air. **Ground** is a flat 20 by 20 area of grey-brown stone, and **Post Process** adjusts the picture's colors and brightness.

Press **Play** once. Nothing moves, because nothing in the scene moves yet, but the Game view shows the scene as the camera sees it. Press Stop.

::checkpoint{stage=2}

::figure{id=project-created}

## Place and move a cube

An entity is empty until you add components. A **component** is one piece of data and behavior on an entity: a position, a shape to draw, a body for physics. The **Inspector** on the right lists the components of the selected entity.

To change an entity with the mouse, you use a **gizmo**: a handle that the editor draws over the selected entity. The **Scene** view is the editor's own camera, with which you look around and edit. The **Game** view shows what a player sees, through the Main Camera.

:::::steps

1. Create a cube.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press the **+** button at the top of the **Hierarchy** and choose **Cube**.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Cube", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "Transform": { "Translation": [-0.5, 0.5, 0] } } } }
   ```

   The command answers with the new entity's `id`. Later commands name the entity by that `id`, as `<the cube's id>` shows.
   :::
   ::::

   **You should see:** a cube resting on the ground, where the Scene view looks, and selected. The Inspector lists **Transform**, **Mesh Renderer** and **Box Collider**.

   **If you do not see it:** the cube is out of the picture. Press **F** with the pointer over the Scene view to frame the selected entity.

   ::figure{id=cube-inspector}

2. Learn the three gizmos. Press **W** over the Scene view to move, **E** to rotate and **R** to scale; the buttons at the top of the editor do the same.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **W**. Drag the green arrow of the cube upward to lift it. Press **E** and drag a ring to turn it. Press **R** and drag a square handle to stretch it.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the cube's id>", "component": "Transform", "values": { "Translation": [-0.5, 3, 0], "Rotation": [0, 30, 0], "Scale": [1, 2, 1] } } }
   ```

   :::
   ::::

   **You should see:** the cube move up along the green arrow, then turn, then grow longer. The green arrow always points up.

   **If you do not see it:** nothing is selected, so no gizmo shows. Click the cube in the Hierarchy first.

3. Undo what you did.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+Z** twice, once for the stretch and once for the turn. Leave the cube lifted.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the cube's id>", "component": "Transform", "values": { "Translation": [-0.5, 3, 0], "Rotation": [0, 0, 0], "Scale": [1, 1, 1] } } }
   ```

   The command of the previous step set all three values at once, so it is one step to undo, and `edit.undo` would also take back the lift. This command sets the turn and the size back instead and keeps the cube lifted.

   :::
   ::::

   **You should see:** the cube straight again, at its normal size, and still high above the ground.

   **If you do not see it:** one drag counts as one step to undo. Press **Ctrl+Z** until the cube is straight, and move it up again.

4. Set exact numbers. In the Inspector, the **Transform** component shows **Translation**, **Rotation** and **Scale**, three numbers each.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Double-click a number to type in it, then press Enter. Set **Translation** to `-0.5`, `3`, `0`, so that every reader starts from the same place.
   :::
   :::tab[With a command]
   The command of the previous step already set these numbers.
   :::
   ::::

   **You should see:** the cube in the same place as before, three units above the ground.

   **If you do not see it:** a number was typed into the wrong field. The first number moves the cube sideways, the second up, the third toward you.

5. Play the scene.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press the Play button, look at the Game view, then press Stop.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   { "command": "play.stop" }
   ```

   The first command leaves the views as they are: click the **Game** tab to see the game, then send the second.

   :::
   ::::

   **You should see:** the Game view comes forward and shows the cube hanging in the air. Nothing falls yet. After **Stop**, the Scene view returns with the cube where you left it.

   **If you do not see it:** the cube is above the top edge of the Game view. Its place is right; look at it in the Scene view.

:::::

Why does **Stop** bring everything back? **Play** does not run your scene. It copies the scene and runs the copy, so whatever the game changes happens to the copy, and Stop throws the copy away.

:::why
A game changes its scene all the time: it moves things, destroys them and creates new ones. If Play ran the scene you edit, every test run would damage your work and you would need a way back. A copy costs a little time at each Play and a little memory. In return, you can run, stop and run again without fear, and the scene in the Hierarchy is always the one you made.
:::

Save your work now. Choose **File ▸ Save Scene**, or press **Ctrl+S**. The item is grey while the game plays, so stop first.

::checkpoint{stage=3}

::figure{id=cube-placed}

## Make it fall

The cube hangs in the air because nothing pulls it down yet. Gravity belongs to the physics, and physics moves only the entities that have a **rigid body**: a component that says an entity is a solid object, with mass, that forces can move. The ground cannot fall, yet it must stop the cube. It does so with a **collider**: an invisible shape that tells physics where an entity is solid ([Bodies and colliders](../make/physics.md) teaches both). The Ground already has one, and the **+ ▸ Cube** item gave your cube one too.

:::::steps

1. Give the cube a rigid body.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the cube. Press **Add Component** in the Inspector, type `rigid` in the search field and choose **Rigid Body** under the Physics heading.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.add", "parameters": { "entity": "<the cube's id>", "component": "RigidBody" } }
   ```

   :::
   ::::

   **You should see:** a **Rigid Body** component in the Inspector. Its **Type** reads Dynamic, which is the default: a dynamic body moves when forces act on it.

   **If you do not see it:** the list has no **Rigid Body**. The cube already has one, or no entity is selected.

   ::figure{id=rigid-body}

2. Play, and watch it fall.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press Play. Press Stop when the cube rests.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the cube drop, hit the ground and stay on it. After **Stop**, it is back in the air.

   **If you do not see it:** the cube stays in the air. Check the Inspector for a **Rigid Body** on this cube, not on another entity.

3. Make a ramp. Add a second cube and give it the shape of a ramp: long, flat and tilted. It gets no **Rigid Body**, because a collider without one is fixed in place.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+** and choose **Cube** again. Press **F2** and type `Ramp`. In the Inspector, set **Translation** to `0`, `0.8`, `0`, **Rotation** to `0`, `0`, `-35` and **Scale** to `3`, `0.2`, `2`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Ramp", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "Transform": { "Translation": [0, 0.8, 0], "Rotation": [0, 0, -35], "Scale": [3, 0.2, 2] } } } }
   ```

   :::
   ::::

   **You should see:** a flat, tilted slab, low at the right. The cube hangs above its higher left half.

   **If you do not see it:** the slab leans the wrong way or lies flat. Check that the third **Rotation** number is `-35`.

4. Play again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press Play and watch from the Scene view. Press Stop afterward.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the cube land on the ramp, slide down to the right and come to rest on the ground, perhaps after tipping over once.

   **If you do not see it:** the cube stays on the ramp. The slope is too gentle for the grip between the two surfaces; the worked example below shows why. Raise the tilt, or do the next step.

5. Change how the surfaces behave. Select the cube. In its **Rigid Body**, set **Friction** to `0.05` and **Restitution** to `0.7`, then press Play.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Double-click each number, type the value and press Enter. Press Play, watch, and press Stop.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the cube's id>", "component": "RigidBody", "values": { "Friction": 0.05, "Restitution": 0.7 } } }
   { "command": "play.start" }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the cube slide down the ramp faster than before and skid far across the ground, almost to its edge, instead of stopping close to the ramp.

   **If you do not see it:** nothing changed. Check that you edited the cube and not the ramp, which has no **Rigid Body**.

:::::

Two numbers decided that run. **Friction** says how strongly two touching surfaces grip, and **Restitution** says how much of its speed a body keeps when it hits something and bounces back. Both can be seen as numbers, so check what you saw.

:::example
Physics needs one number per pair of surfaces, but each surface has its own. Strata's physics library, box3d, combines the two **Friction** values by taking the square root of their product. The ramp has no **Rigid Body**, so its collider gets the default `0.5`. With the cube's default `0.5` the pair grips with $\sqrt{0.5 \times 0.5} = 0.5$.

A body starts to slide when the slope's rise divided by its run is larger than that number. A slope of 35 degrees rises 0.70 for every 1 of run, which is more than 0.5, so the cube slides. A slope of 15 degrees rises 0.27 per 1, which is less than 0.5, so the cube would stay on it: the ramp must be steep enough. With **Friction** at `0.05` the pair grips with $\sqrt{0.05 \times 0.5} = 0.16$, and the cube slides on slopes as gentle as 9 degrees.

**Restitution** combines differently: the pair takes the larger of the two values. The ramp's is `0`, the cube's is `0.7`, so the pair bounces with `0.7`, and you only needed to set the cube.
:::

:::why
Both surfaces take part in a contact, so the result cannot belong to one of them. The product under a root keeps a very slippery surface slippery, whatever it touches. The larger **Restitution** keeps a ball that bounces well bouncing on a floor that does not. The cost is that you cannot give one body a grip that wins against every other surface, and the physics guide of [Bodies and colliders](../make/physics.md) shows the other settings.
:::

Choose **File ▸ Save Scene** again, or press **Ctrl+S**.

::checkpoint{stage=4}

::figure{id=cube-falls}

## Make it spin with a script

Physics can move a cube, but it cannot do what you invent. For that, a game uses scripts. A **script** is a piece of C++ code that runs inside the game and decides what an entity does. Strata calls its code in a fixed order, and each script is a class, a **script class**, of which every entity that uses it has its own copy.

Every new project comes with one example, `Scripts/Spinner.cpp`, which turns its entity. You build it, attach it to a third cube and change one number in it.

:::::steps

1. Add the cube that will turn.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+** and choose **Cube**. Press **F2** and type `Top`. In the Inspector, set **Translation** to `-3`, `2`, `0`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Top", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "Transform": { "Translation": [-3, 2, 0] } } } }
   ```

   :::
   ::::

   **You should see:** a cube floating to the left of the ramp, two units above the ground.

   **If you do not see it:** the cube is not in the picture. Select it and press **F** over the Scene view.

   Why no **Rigid Body**? A body that physics moves must not also be turned by a script: the two would fight over the same position. The `Top` has a collider but no body, so physics leaves it where it is, and the script turns it.

2. Build the project's scripts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ Build Scripts**, or press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the status bar shows "Building" with the seconds, and then the word disappears. The first build in a project takes longest, because the build system must configure itself.

   **If you do not see it:** the status bar says "Build failed". Click it, and read the **Problems** panel: it lists each error with its file and line.

3. Attach the script. A script class that no entity uses does nothing. Select `Top`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Add Component** and choose **Script** under the Scripting heading. The new component shows a list named **Add Script...**; open it and choose `Spinner`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<the Top's id>", "class": "Spinner" } }
   { "command": "script.get", "parameters": { "entity": "<the Top's id>", "class": "Spinner" } }
   ```

   The `fields` of the answer of `script.add` lists only the values that this entity sets for itself, so it is empty. `script.get` answers every field with the value the entity uses: `DegreesPerSecond` is `90`, the class's default.

   :::
   ::::

   **You should see:** a `Spinner` entry in the Inspector with one field, "Degrees Per Second", set to `90`. The Inspector writes a name of the code with spaces, so the code's `DegreesPerSecond` shows as "Degrees Per Second".

   **If you do not see it:** the Inspector says "No script module is loaded: build the scripts (Scripts > Build Scripts) to edit their fields". Build the scripts first, with the step before this one.

   ::figure{id=script-attached}

4. Play.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press Play, watch the `Top` and the falling cube, and press Stop.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the `Top` turn around its vertical axis, one turn in four seconds, while the other cube falls and slides.

   **If you do not see it:** the cube does not turn. The Script component is missing from `Top`, or the field is `0`.

:::::

Now read the file that makes it turn. Reading code you do not understand yet has a method, which [How to read this book](../start/how-to-read.md) describes: find the names, say what each part is for, and ignore the rest.

:::question
New to C++? Variables and numbers are taught in [Programming 1](../basics/programming-1.md), functions in [Programming 2](../basics/programming-2.md), classes and `#include` in [Programming 3](../basics/programming-3.md), and `override` in [C++ classes](../basics/cpp-classes.md).
:::

Here is the file as the editor wrote it. It starts with a comment, lines that begin with `//` and that the program ignores. The editor wrote it for you: it says how to attach the script and where the manual for scripts is.

```cpp src="book:tutorials/start/first-game/Spinner-90.cpp#L1-L5"
// An example script. Attach it to an entity to make it spin: select the entity, Add Component > Script in the
// Inspector, and pick Spinner (or run the editor command
//   script.add {"entity": "<entity id>", "class": "Spinner", "fields": {"DegreesPerSecond": 45}}).
// Scripts see only the StrataScript SDK. How to create, build, debug and hot reload scripts, and to open them in an IDE:
// Docs/Manual/Scripting.md in the Strata engine's folder.
```

The code follows, after an empty line. Search for the class, the function that runs every frame, and the registration at the bottom. The editor starts each line with tab characters, and the book draws each tab as two spaces, so your code editor may show wider steps.

```cpp src="book:tutorials/start/first-game/Spinner-90.cpp#L7-L28"
#include "StrataScript/StrataScript.h"

using namespace Strata;

// Turns its entity around the world's Y axis.
class Spinner : public Script
{
public:
	float DegreesPerSecond = 90.0f; // A field: editable per entity, kept across hot reloads

	void OnUpdate(float deltaTime) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());
	}
};

ST_SCRIPT_CLASS(Spinner)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
}
```

1. **Line 12:** the class `Spinner`, built on `Script`, the base of every script class.
2. **Line 15:** the field, with its default of 90 degrees per second.
3. **Line 17:** the function that Strata calls every frame; `override` says that it replaces the version of `Script`.
4. **Line 20:** the turn for this frame, around the vertical axis, of `DegreesPerSecond * deltaTime` degrees.
5. **Lines 25–28:** the registration that makes the class and its field visible to the editor.

`deltaTime` is the time of the last frame, in seconds; [What an engine is](../start/what-an-engine-is.md) explains why a game needs it. `ST_SCRIPT_CLASS` with `ST_SCRIPT_FIELD` tells the editor that the class exists and that `DegreesPerSecond` is a **field**: a value the Inspector shows and each entity keeps for itself. [Your first script](../make/first-script.md) teaches these parts properly.

:::example
At 60 frames per second, one frame lasts 1/60 of a second, so the turn of one frame is $90 \times 1/60 = 1.5$ degrees. In 60 frames, one second, the cube turns $60 \times 1.5 = 90$ degrees: a quarter turn per second, one full turn in four seconds, as you saw. At 30 frames per second a frame lasts 1/30 of a second and turns 3 degrees, and a second still adds up to 90. That is why the code multiplies by `deltaTime`.
:::

Now change it. The field's default is 90. Because you did not change the field in the Inspector, the `Top` holds no value of its own, and the number in the code is the one it uses.

:::::steps

1. Choose your code editor, so that Strata knows which program opens C++ files.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ External Editor...**. Click the code editor in the list "Found on this machine", for example the entry for Visual Studio Code, and press **Apply**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setExternalEditor", "parameters": { "command": "code -g {file}:{line}:{column}" } }
   ```

   :::
   ::::

   **You should see:** the line "Starts" with the path of the program, under the command field.

   **If you do not see it:** the list is empty. Type the command of your code editor in the field and press **Apply**. Without a choice, the editor opens C++ files in the system's application for them, and may fail.

2. Open the file.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the **Content Browser**, click **Scripts** in the folder tree and double-click `Spinner.cpp`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.open", "parameters": { "file": "Scripts/Spinner.cpp" } }
   ```

   :::
   ::::

   **You should see:** the file in your code editor.

   **If you do not see it:** nothing opened, and the **Console** gives the reason. Check step 1 of this section.

3. Change the number, then build with the game stopped.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the code editor, change `90.0f` to `360.0f` and save the file. In Strata, make sure no game plays, then press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** "Building", and then no "Build failed".

   **If you do not see it:** the editor shows a build error. Read the **Problems** panel, and compare your line with the listing above.

4. Play.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press Play, watch the `Top` and press Stop.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the `Top` turn four times as fast: 360 degrees per second is one turn per second.

   **If you do not see it:** it turns at the old speed. Three causes are common. You did not save the file in the code editor. The game was playing during the build, which reloads the code but keeps the running value, 90. Or you once changed "Degrees Per Second" in the Inspector, so the entity holds its own value; press the small reset arrow beside it, "Reset to the class default".

:::::

Next, make the script write a line. Strata's script kit has `Log::Info`, which writes one line to the **Console** panel. Put it in a function named `OnCreate`, which Strata calls once, before the first update. Had you put it in `OnUpdate`, it would write a line every frame.

Change the file to match the listing below, which keeps your 360 and adds `OnCreate`. The first ten lines of the file, the comment, the `#include` and the `using` line, stay as they are.

```cpp src="book:tutorials/start/first-game/Spinner.cpp#L11-L33"
// Turns its entity around the world's Y axis.
class Spinner : public Script
{
public:
	float DegreesPerSecond = 360.0f; // A field: editable per entity, kept across hot reloads

	void OnCreate() override
	{
		Log::Info("Spinner starts with ", DegreesPerSecond, " degrees per second");
	}

	void OnUpdate(float deltaTime) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());
	}
};

ST_SCRIPT_CLASS(Spinner)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
}
```

1. **Line 15:** the field now starts at 360.
2. **Lines 17–20:** `OnCreate` runs once, when the game starts, and writes one line to the Console.
3. **Lines 22–27:** `OnUpdate` is unchanged and still turns the entity every frame.

:::::steps

1. Save the file, build with the game stopped, play and read the line.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Save the file in the code editor, press **Ctrl+B** in Strata, press Play, then open the **Console** panel and look at the last lines. Press Stop.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "play.start" }
   { "command": "log.read", "parameters": { "logger": "Script", "newest": true, "limit": 5 } }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the line `Spinner starts with 360 degrees per second` in the **Console**, among the lines that the build and Play wrote.

   **If you do not see it:** the line is missing. The build may have failed, the file may not hold your change, or the game was already playing during the build; stop it, build and play again. The Console keeps every line since the editor started, so the newest `Script` lines may still be those of the Tetris copy: then `OnCreate` did not run, and the file on disk lacks it.

:::::

Finally, save the scene with **File ▸ Save Scene**, or press **Ctrl+S**. If you close the editor with **File ▸ Exit** before you save, a dialog named **Unsaved Changes** asks whether to save the scene. Choose **Save**.

To open the project again later, start the editor. The launcher's **Recent projects** shows a card for `FirstGame`; click it. With another project open, choose **File ▸ Open Recent** instead.

You can now open a sample, make a project, place entities, give one a body, and build, change and read a script. Every track continues with [What an engine is](../start/what-an-engine-is.md), which explains what happened each time you pressed Play. When you want an AI agent to build with you, see [Making a game with an AI agent](../make/with-an-agent.md).

::checkpoint{stage=5}

::figure{id=spinner-console}

## Summary

- You opened a copy of the Tetris sample, played it after its first build, and stopped it.
- You made a project from the Basic 3D template, whose scene has Main Camera, Sun, Sky, Ground and Post Process.
- You added a cube, moved it with the gizmos, gave it a **Rigid Body**, and changed **Friction** and **Restitution** on a ramp.
- You built the `Spinner` script, attached it, raised `DegreesPerSecond` from 90 to 360, and read the line it wrote in the Console.

## Check yourself

1. Why did your first Play of the Tetris copy show "Building to play" in the status bar?

   :::answer{tests="sample"}
   The sample's game code is C++, and Play builds the scripts first so that the game runs the current code. The build also proved that your build tools work. If they were missing, a toast named what to install.
   :::

2. Which five entities does the Basic 3D scene have, and which one is solid for physics at the start?

   :::answer{tests="project"}
   Main Camera, Sun, Sky, Ground and Post Process. The Ground is solid: it has a box collider, one meter thick, whose top is at height 0.
   :::

3. You drag a cube in the Scene view during Play. After Stop, where is it, and why?

   :::answer{tests="physics"}
   The cube is back where you edited it. Play runs a copy of the scene, and Stop discards the copy.
   :::

4. A cube with default **Friction** sits on a ramp tilted by 20 degrees and does not slide. Name two ways to make it slide.

   :::answer{tests="physics"}
   Tilt the ramp more, to about 27 degrees or beyond, or lower the cube's **Friction**. The pair grips with the square root of the product of the two values, and a slope of 20 degrees rises 0.36 per unit of run, less than the grip of 0.5.
   :::

5. You change `DegreesPerSecond` in `Spinner.cpp` and build while the game plays. The cube still turns at 90. Why?

   :::answer{tests="script"}
   A build during play reloads the code but carries the running value of each field over. Stop the game, build, and play again. A value set on the entity in the Inspector would also win over the code's default.
   :::

6. Why is the `Log::Info` line in `OnCreate` and not in `OnUpdate`?

   :::answer{tests="script"}
   Strata calls `OnCreate` once, so the line is written once. It calls `OnUpdate` every frame, which at 60 frames per second would write 60 lines a second.
   :::

## Exercises

1. **Basic.** Select the falling cube and set **Gravity Scale** in its **Rigid Body** to `0.2`. Predict what changes, then play.

   :::answer{tests="physics"}
   The cube falls at one fifth of the pull of gravity, so it drops slowly, like a feather. The field accepts values from -100 to 100. Set it back to `1` afterward.
   :::

2. **Medium.** Set `DegreesPerSecond` to `-90` in `Spinner.cpp`. Predict the direction and the speed, build with the game stopped, and play.

   :::answer[Worked solution]{tests="script" solution="tutorials/start/first-game/exercise-2.tutorial.json"}
   The cube turns the other way, at a quarter of the speed you had at 360: one turn in four seconds. The sign of the number is the direction. Change `360.0f` to `-90.0f`, save, press **Ctrl+B** and play.
   :::

3. **Medium.** Move the `Log::Info` line from `OnCreate` into `OnUpdate`. Predict what the Console shows, build and play, then move the line back.

   :::answer{tests="script"}
   The Console fills with one line for every frame, at 60 frames per second 60 lines for each second, and the useful lines scroll away. `OnUpdate` is for what changes every frame; a one-time message belongs in `OnCreate`.
   :::

## Where it lives in Strata

- `StrataEditor/src/Panels/WelcomePanel.cpp`: the launcher with its cards.
- `StrataEditor/src/Editor/ProjectTemplates.cpp`: the Basic 3D template and its five entities.
- `StrataEditor/src/Editor/ScriptProject.cpp`: the example script that every new project gets.
- `Strata/src/Strata/Physics/PhysicsComponents.cpp`: the Rigid Body and the colliders with their properties.
- `StrataScriptCore/Include/StrataScript/Script.h`: the base class `Script` and its functions.

## Further reading

- Robert Nystrom, "Game Programming Patterns", chapter "Game Loop": why games run their code once per frame (beginner).
- Ian Millington, "Game Physics Engine Development": how rigid bodies, friction and restitution work (advanced).
