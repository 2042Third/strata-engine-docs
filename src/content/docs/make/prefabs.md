---
id: make/prefabs
title: "Prefabs"
description: "Turn Coin Run's coin into a prefab, place five copies, give one its own look, change them all at once and take a change back."
kind: tutorial
size: M
tracks: [G, B]
needs: [make/materials]
time: 60
learn:
  - id: make-prefab
    text: create a prefab from an entity in the scene and explain what an instance is
  - id: place-instances
    text: add instances of a prefab with the drop ghost, snapping and dropping to the ground
  - id: override
    text: find the overridden property of an instance and predict which instances a change reaches
  - id: apply-revert
    text: change a prefab through an instance with Apply to Prefab and take a change back with Revert
  - id: unpack
    text: change an instance into plain entities with Unpack and undo it
since: 0.3.0
status: final
---

## What you will make

Coin Run needs many coins, and you will not copy and edit each by hand. You turn the one gold coin into a **prefab**. A prefab is an entity, with the entities below it, saved as an asset. You can place it in scenes as often as you like, and here you fill the level with five coins.

::figure{id=result}

Each placed copy is an **instance**. It keeps a link to the prefab, so one change of the prefab reaches every copy. A copy can still keep a value of its own. Such a value is an **override**: for example, one silver coin among gold ones. The picture shows the idea before you try it.

```mermaid caption="One prefab file, three instances. The first instance overrides the material and keeps silver, while a change of the scale reaches all three." alt="A box for the prefab Coin points to three boxes for instances. The first instance has a note: material silver, its own. All three take the scale from the prefab."
flowchart TD
	P["Prefab Coin: scale 1, material gold"] -->|"link"| A["Instance 1: material silver (override)"]
	P -->|"link"| B["Instance 2: no override"]
	P -->|"link"| C["Instance 3: no override"]
	E["You change the scale to 1.5 and apply"] -->|"writes"| P
```

Read the diagram as a rule with one exception. A value that an instance did not touch follows the prefab, and a value it did touch stays its own until you revert it. Making a prefab costs one click, and you keep it afterwards for every coin the game needs.

:::why
Strata links an instance to its prefab instead of copying the prefab's values into the scene. A copy would be simpler, but a change of the coin then needs a hand edit of every coin, and you would miss one. The link costs you something too: a scene holds only the differences of each instance, and you must learn the rule above to predict what a change reaches.
:::

## What you need

You start from the end state of the Materials page: the level with the gold coin and the metal ball. If you skipped it, download its checkpoint. The coin is the model `coin-gold.glb` placed in the level and named `Coin`, with the `Coin` tag on its root and `Materials/Gold.stmat` on its mesh child.

You need no new files. The whole page takes about an hour. Remember how the Assets page left the coin: a placed model is a root entity named after its file, with one child entity for each part of the file. The root holds the transform, with the position, and the name. The **Mesh Renderer** that draws the coin sits on the child, and you select that child whenever a step changes the look.

## Make the prefab

You start by saving the coin as a prefab. The coin in the scene becomes the first instance of it, so you lose nothing.

:::::steps

1. Select the `Coin` root in the Hierarchy and save it as a prefab.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `Coin` in the Hierarchy and choose **Create Prefab**. Or drag `Coin` from the Hierarchy into a folder of the Content Browser.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.create", "parameters": { "entities": ["<id of Coin>"], "path": "Prefabs/Coin.stprefab" } }
   { "command": "prefab.status", "parameters": { "entity": "<id of Coin>" } }
   ```

   Take the identifier (ID) of `Coin` from `entity.find` with the name `Coin`, and the ID of every other entity of this page the same way. The badge and the chip are drawn in the window; `prefab.status` answers what they show. Its `linked` stands for the badge, and its `overrides` lists what the chip counts.
   :::
   ::::

   **You should see:** the file `Prefabs/Coin.stprefab` in the Content Browser, and the Asset tab shows the new prefab. The `Coin` row in the Hierarchy has a small package icon at its right end, the badge. Select `Coin` again: the Inspector now starts with the prefab bar: the prefab's name, **Select**, **Open** and a chip that reads `Overrides (0)`. The answer of `prefab.status` reads `"linked": true`, the path of the prefab and an empty `overrides` list.

   **If you do not see it:** the Hierarchy menu is grey while the game plays. Stop the game and try again.

   **Why:** you drop nothing and lose nothing, because creating the prefab also links the coin in the scene to it. One undo step removes the file and the link together.

2. Look at the badge and the bar once more.

   **You should see:** hovering over the badge shows "An instance of Coin: click to show it in the Asset tab". The chip `Overrides (0)` says that this coin differs from the prefab in no value.

   **If you do not see it:** hover over the small package icon at the right end of the row. The tip appears only while the pointer rests on the icon.

:::::

::checkpoint{stage=1}

::figure{id=made}

## Place four more coins

A prefab is useful when you place it often, so you place four more coins on the level.

:::::steps

1. Drag `Prefabs/Coin.stprefab` from the Content Browser into the Scene view and hold the mouse button down.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Move the pointer over the ground. A box ghost sits on the surface below the pointer, and a label beside the pointer reads "Coin on 'Ground'". Release the button to place the coin. One undo step undoes the placement.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.place", "parameters": { "asset": "Prefabs/Coin.stprefab", "ray": { "origin": [-2, 10, 0], "direction": [0, -1, 0] } } }
   ```

   The command places the coin where a ray lands, as the drop does with the ray through the pointer: here straight down onto the ground at x = -2. With `viewport` instead of `ray` it takes a pixel of the Scene view. The answer's `placedOn` reads `surface`.
   :::
   ::::

   **You should see:** a coin on the ground where you released the button, named `Coin (1)` in the Hierarchy. Strata numbers instances that share a name and a parent.

   **If you do not see it:** if the label names another surface, such as a wall, the pointer was over that surface. Move it and watch the label change. To cancel a drag, press **Escape** before you release.

2. Drag another coin to a place where there is nothing under the pointer, such as the sky past the edge of the ground, and press **Escape** before you release.

   **You should see:** the ghost is dimmed, and the label reads "Coin on the grid (nothing under the pointer)". The coin would land on the grid. That is a flat plane at height 0, searched up to 500 metres from the camera. Where the grid lies farther away, the coin lands in front of the camera.

   **If you do not see it:** if the ghost stays solid, the pointer still rests on a surface. Move it past the edge of the ground, where nothing lies under it.

3. Enable the magnet button in the row of buttons above the Scene view, and drag a third coin onto the ground.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag `Coin.stprefab` over the ground and release the button.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.place", "parameters": { "asset": "Prefabs/Coin.stprefab", "ray": { "origin": [2.3, 10, 0.2], "direction": [0, -1, 0] }, "snap": 1 } }
   ```

   The ray lands at (2.3, 0.2), and the grid step of 1 metre moves the coin to (2, 0): the answer reads `"snapped": true`.
   :::
   ::::

   **You should see:** the ghost jumps from one grid step to the next along the surface, instead of following the pointer smoothly. Holding the Ctrl key inverts the snapping, as it does for the :term[gizmo]{id=gizmo-start}.

   **If you do not see it:** open the arrow beside the magnet to see the grid step. A very small step looks like no snapping at all.

4. Place two more coins without a drag, with a menu or with one command that makes many.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `Coin.stprefab` in the Content Browser and choose **Add to Scene**. It places the coin where the view looks. Do this once more, so the level holds five coins.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Coin.stprefab", "instances": [ { "components": { "Transform": { "Translation": [3, 1, 0] } } }, { "components": { "Transform": { "Translation": [-3, 1, 0] } } } ] } }
   ```

   :::
   ::::

   **You should see:** five coins in the Hierarchy: `Coin`, `Coin (1)` up to `Coin (4)`, each with the badge.

   **If you do not see it:** a coin that floats in the air is fine for now. Select it and press **End**, which drops the selection onto the surface below it. The command `entity.dropToGround` does the same.

:::::

The ghost, the label and the snap come from one placement rule, which the Placement page explains. A drop and the command `asset.place` use the same rule, so a script or an agent places a coin exactly where you would.

::checkpoint{stage=2}

::figure{id=placed}

## Give one coin its own look

Now one coin should be silver. You change a value on that instance only, and you watch the editor mark it.

:::::steps

1. Make the silver material first, as you made the gold one. Name it `Silver`. Give it a light grey base color, a metallic value of 1 and a roughness of 0.25.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the Content Browser's `Materials` folder, choose **New ▸ Material**, name it `Silver` and edit it in the Asset tab.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/Silver.stmat", "properties": { "BaseColor": [0.8, 0.8, 0.82, 1], "Metallic": 1, "Roughness": 0.25 } } }
   ```

   :::
   ::::

   **You should see:** `Materials/Silver.stmat` in the folder.

   **If you do not see it:** the file is made in the folder that is open, so open `Materials` first.

2. Give `Coin (1)` the silver material. The Mesh Renderer is on its child, so expand `Coin (1)`, select the child that holds the mesh, and set the **Material** field of its **Mesh Renderer**. A shortcut: drag `Silver` from the Content Browser onto the coin in the Scene view.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Expand `Coin (1)`, select its child with the Mesh Renderer and choose `Silver` as **Material**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<id of the mesh child>", "component": "MeshRenderer", "values": { "Material": "Materials/Silver.stmat" } } }
   { "command": "prefab.status", "parameters": { "entity": "<id of the mesh child>" } }
   ```

   `entity.get` on `Coin (1)` lists the ID of its child under `children`.
   :::
   ::::

   **You should see:** `Coin (1)` turns silver. In the Inspector the label **Material** is bold, with a bar in the accent color on the left of its row. The chip reads `Overrides (1)`. The badge of `Coin (1)` changes its color, because the instance now differs from its prefab. The `overrides` of `prefab.status` hold one entry, the `Material` of `MeshRenderer`.

   **If you do not see it:** with the root selected you find no Mesh Renderer, because the root holds the transform and the name, not the look. Select the child.

3. Move and rename the root of `Coin (1)`: change its **Translation** a little in the Inspector and give it a new name in the Hierarchy, such as `Silver Coin`. Then rename it back to `Coin (1)`, the name the next steps use.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type a new **Translation** in the Inspector. Double-click the row of `Coin (1)` in the Hierarchy to rename it.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<id of Coin (1)>", "component": "Transform", "values": { "Translation": [-2, 0, 0.3] } } }
   { "command": "entity.rename", "parameters": { "entity": "<id of Coin (1)>", "name": "Silver Coin" } }
   { "command": "prefab.status", "parameters": { "entity": "<id of Coin (1)>" } }
   { "command": "entity.rename", "parameters": { "entity": "<id of Coin (1)>", "name": "Coin (1)" } }
   { "command": "prefab.status", "parameters": { "entity": "<id of Coin (1)>" } }
   ```

   :::
   ::::

   **You should see:** the count stays at `Overrides (1)` after each change, and both answers of `prefab.status` still list one override.

   **If you do not see it:** if the count grew, you changed a child and not the root. The root's transform and name belong to the instance, so they never count as overrides. You must be able to place and name a coin without marking it.

:::::

::checkpoint{stage=3}

::figure{id=overridden}

## Change the prefab for every coin

You now change the prefab through another coin. The rule you saw in the diagram predicts the result, so write down your guess first: which coins grow?

:::::steps

1. Select the child with the mesh of `Coin (2)` and set its **Scale** to 1.5 in each field of its **Transform**. Open the `Overrides` menu of the prefab bar.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit the child's **Scale**. The chip now reads `Overrides (1)`. Click it to see the list: the child's scale.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<id of the mesh child of Coin (2)>", "component": "Transform", "values": { "Scale": [1.5, 1.5, 1.5] } } }
   { "command": "prefab.status", "parameters": { "entity": "<id of Coin (2)>" } }
   ```

   :::
   ::::

   **You should see:** only `Coin (2)` is larger. The other coins have not changed, because the scene still holds the old values of the prefab. The `overrides` of `prefab.status` hold one entry, the `Scale` of `Transform`.

   **If you do not see it:** a scale of 1 in all three fields means your edit did not take. Press **Enter** after each field.

2. Apply the change to the prefab.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the `Overrides` menu choose **Apply All to Prefab**. Or right-click the **Scale** label and choose **Apply to Prefab**.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.apply", "parameters": { "entity": "<id of Coin (2)>" } }
   { "command": "prefab.status", "parameters": { "entity": "<id of Coin (2)>" } }
   { "command": "prefab.status", "parameters": { "entity": "<id of Coin (1)>" } }
   ```

   :::
   ::::

   **You should see:** every coin is larger now, `Coin (1)` included, and it stays silver, because it overrides only its material. The prefab file `Prefabs/Coin.stprefab` holds the new scale. The chip of `Coin (2)` returns to `Overrides (0)`, since it now agrees with the prefab. The first `prefab.status` lists no override, and the second still lists the `Material` of `Coin (1)`.

   **If you do not see it:** if `Coin (1)` turned gold, you reverted the material instead of applying the scale. Undo with **Ctrl+Z** and try again.

   **Why:** the apply writes a value into the prefab, and Strata passes that value to each instance that has not overridden it. The whole change, the file and all instances, is one undo step.

:::::

The coin model of the Assets page was already a linked group before you made the prefab. A model's instance offers **Revert** only, because models are not edited in the editor. The prefab you made from the model has no such limit.

::checkpoint{stage=4}

::figure{id=applied}

## Take a change back and unpack

The reverse of Apply is Revert. It gives the instance the prefab's value again.

:::::steps

1. Select the child of `Coin (1)` and right-click its **Material** label.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Revert**. To revert every override of an instance at once, open the `Overrides` menu of the prefab bar and choose **Revert All**.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.revert", "parameters": { "entity": "<id of the mesh child of Coin (1)>", "component": "MeshRenderer", "property": "Material" } }
   { "command": "prefab.status", "parameters": { "entity": "<id of the mesh child of Coin (1)>" } }
   ```

   :::
   ::::

   **You should see:** `Coin (1)` is gold again, its label is no longer bold, and the chip says `Overrides (0)`, as the empty `overrides` of `prefab.status` do. **Revert** is the action that gives an instance the prefab's value again. Undo brings the silver back.

   **If you do not see it:** if the menu has no **Revert** entry, the property is not overridden. Only marked properties offer it.

2. Unpack `Coin (4)`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `Coin (4)` in the Hierarchy and choose **Unpack Prefab**.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.unpack", "parameters": { "entity": "<id of Coin (4)>" } }
   { "command": "prefab.status", "parameters": { "entity": "<id of Coin (4)>" } }
   ```

   :::
   ::::

   **You should see:** the badge and the prefab bar disappear, and `prefab.status` answers `"linked": false`. **Unpack** ends the link and leaves the entities in the scene as plain entities. The coin looks the same, but a later change of the prefab no longer reaches it.

   **If you do not see it:** if the menu has no **Unpack Prefab**, you right-clicked an entity that belongs to no instance.

3. Undo the unpack with **Ctrl+Z**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+Z** with the pointer over the Scene view or the Hierarchy.
   :::
   :::tab[With a command]

   ```json
   { "command": "edit.undo" }
   { "command": "prefab.status", "parameters": { "entity": "<id of Coin (4)>" } }
   ```

   :::
   ::::

   **You should see:** the badge and the bar return, and `Coin (4)` is an instance again: `prefab.status` answers `"linked": true`.

   **If you do not see it:** undo steps back one edit at a time. If you made another edit after the unpack, undo that one first.

4. Save the scene with **File ▸ Save Scene** (**Ctrl+S**).

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Save Scene**.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   ```

   :::
   ::::

   **You should see:** the scene is saved and no error appears in the Console.

   **If you do not see it:** while the game plays, the menu item is grey. Stop the game first.

:::::

### What a prefab does not do here

Two limits are worth knowing before you plan a larger game.

First, Strata has no nested prefabs and no prefab variants. A prefab you make from linked entities keeps no inner links. Your `Coin.stprefab` came from a placed model, and creating it replaced the coin's link to `coin-gold.glb` with a link to the prefab. You change the coins through the prefab now.

Second, Strata has no prefab edit mode. You do not open a prefab like a scene. You change an instance and apply it, as you did when you changed the prefab for every coin.

### Outdated instances

An instance has a second way to differ from its prefab. Suppose two scenes hold the coin, and in scene A you apply a new scale to the prefab. Scene B is not open, so its coins cannot follow. When you open B, a coin that you never changed takes the new scale at once. A coin that you changed in B keeps its values.

The Hierarchy marks that coin as an **outdated instance**: a changed instance made from an older version of its prefab, which missed the prefab's later changes.

Applying such an instance would write its older values over the newer ones, so the editor warns you. The Hierarchy menu then offers **Apply to Prefab (Over Its Newer Changes)**, and the command refuses unless it gets `force`. Revert the instance to take the newer values, and then make your own changes again.

::checkpoint{stage=5}

::figure{id=finished}

## Summary

- You create a prefab from an entity with **Create Prefab**, and the entity becomes its first instance.
- You place instances with the drop ghost, the snap, **Add to Scene** and **End**.
- An override is a bold property with an accent bar; the root's transform and name never count.
- **Apply to Prefab** writes an instance's value into the prefab, and every instance without an override follows.
- **Revert** takes an override back, and **Unpack Prefab** turns an instance into plain entities, which undo can restore.

## Check yourself

1. You have five coins and apply a new scale from the third. The second coin overrides its material only. Which coins change their scale, and which material has the second coin?

   :::answer{tests="override,apply-revert"}
   All five coins take the new scale, because no coin overrides the scale. The second coin stays silver, since the apply passes a value on only where an instance has no override of that value.
   :::

2. You move the root of an instance and rename it. How many overrides does the prefab bar show?

   :::answer{tests="override"}
   None from those two edits. The root's transform (its position, rotation and scale) and name belong to the instance, so placing and naming a coin never counts as a change. Only a change of a value of another component or of a child counts.
   :::

3. You hold the dragged prefab over the empty sky and the ghost looks dimmed. Where does the coin land if you release?

   :::answer{tests="place-instances"}
   On the grid, the ground plane at height 0, when it lies within 500 metres of the camera. When the grid is farther away, the coin lands in front of the camera.
   :::

4. You unpack a coin, then apply a new scale from another coin. Does the unpacked coin change, and how do you get its link back?

   :::answer{tests="unpack"}
   No: unpacking ended the link, so the coin is a plain entity that no prefab change reaches. Undo the unpack with **Ctrl+Z** right after it, and the coin is an instance again.
   :::

5. Why does an instance of the imported coin model offer only **Revert**?

   :::answer{tests="make-prefab,apply-revert"}
   Models are not edited in the editor, so **Apply to Prefab** is missing for them. A prefab that you made from the model has both **Apply** and **Revert**.
   :::

## Exercises

1. **Basic.** Place a sixth coin at a height of 3 metres with `prefab.instantiate`, then drop it to the ground with `entity.dropToGround`. Hint: the command takes `components` with a `Transform`.

   :::answer[Worked solution]{tests="place-instances" solution="tutorials/make/prefabs/exercise-1.tutorial.json"}
   Make the coin with a Translation of 0, 3, 0, keep the returned `id`, and run `entity.dropToGround` with it in `entities`. The result lists the coin under `moved`. In the editor, select the coin and press **End**.
   :::

2. **Medium.** Make a second scene, add one coin instance, and change that coin's scale there. Switch to the first scene, apply a new scale to the prefab and return to the second scene. Is the coin outdated? What do you do?

   :::answer{tests="apply-revert"}
   Yes: it was changed, and the prefab changed after it took its values. The Hierarchy marks it. Choose **Revert All**, which gives it the new scale, and make your own change again.
   :::

3. **Hard.** `Coin (1)` overrides its material. You disable **Cast Shadows** on the mesh child of `Coin (3)` and apply it, then revert the material of `Coin (1)`. Which coins cast shadows, and which material has each coin?

   :::answer{tests="override,apply-revert"}
   No coin casts shadows, because no coin overrides that property, so all five follow the prefab. All five coins are gold: the revert took the silver away, and the others never left gold.
   :::

## Where it lives in Strata

The prefab commands are in `StrataEditor/src/Editor/EditorPrefabCommands.cpp` and `StrataEditor/src/Editor/EditorAssetCommands.cpp`. The prefab bar is in `StrataEditor/src/Panels/InspectorPanel.cpp`, and the badge and the Hierarchy menu are in `StrataEditor/src/Panels/SceneHierarchyPanel.cpp`. The rule that the root's transform and name never count is in `Strata/src/Strata/Scene/PrefabOverrides.cpp`. The prefab as data, with how copies are made and how a change travels, is the subject of the World part's prefab page.

## Further reading

- The engine's own manual, `Docs/Manual/Prefabs.md` in the Strata release: the same steps in short form (beginner).
- Unity and Unreal manuals describe prefab variants and blueprints, which Strata lacks (intermediate).
