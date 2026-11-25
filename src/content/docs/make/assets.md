---
id: make/assets
title: "Bringing in assets"
description: "Import a coin model into Coin Run, check its size, put it where the placeholder stands, and learn to rename and delete assets safely."
kind: how-to
size: M
tracks: [G, B]
needs: [make/transforms-units, make/project-files]
time: 45
learn:
  - id: licenses
    text: choose which downloaded assets a project may use and record them in a credits table
  - id: import-model
    text: name the sub-assets and the handle of a model imported into a project folder
  - id: check-size
    text: compare an imported model with a known size and change its Scale import setting
  - id: safe-moves
    text: change a folder's name and delete an asset without breaking the scene that uses it
since: 0.3.0
status: final
---

You will bring a coin model into Coin Run and put it where the placeholder coin stands, then credit its author. The
model is a file someone else made, so the page also teaches where such files may come from and how to keep them safe.

Before you start:

- Coin Run is at the end of [Scenes, entities and components](scenes-entities.md): the ground, four walls, the ball and a placeholder coin tagged `Coin`.
- You have the release folder of Strata at hand. Its `Samples/` folder holds the file `Samples/ThirdPerson/Assets/Models/Platformer/coin-gold.glb`.
- You know the project's folders and `.meta` files from [Projects, saving, undo and recovery](project-files.md), and that one unit in the scene is one metre ([Positions, rotations and units](transforms-units.md)).

## Where assets come from

A game needs models, pictures and sounds, and most makers do not draw them all. Before you use a file made by someone else, you need the right to use it. Every file has a **license**, the author's statement of what you may do with it, and a file without a clear license stays out of your project.

Two licenses cover almost everything a small game needs: Creative Commons Zero (CC0) and CC-BY. **CC0** is a license that drops all claims: you may use, change and sell the work with no conditions and no credit.

**CC-BY** is a license that lets you use the work if you name its author and say where it comes from. Anything else, or a license you cannot find, is a reason to skip the file.

```mermaid caption="The question to ask of every downloaded file: a CC0 file may be used, a CC-BY file may be used with credit, and any other file stays out." alt="A flow chart. The first question is whether the file has a clear license. If not, omit the file. If yes, a second question asks which license: CC0 leads to use it, CC-BY leads to use it and credit the author, anything else leads to omit the file."
flowchart TD
    A[A file you want to use] --> B{Is its license clear?}
    B -- No --> X[Omit the file]
    B -- Yes --> C{Which license?}
    C -- CC0 --> U[Use it]
    C -- CC-BY --> V[Use it and credit the author]
    C -- Any other --> X
```

Four sites publish CC0 assets for games: Kenney (models, sounds and interface art), Poly Haven (skies and textures), `Quaternius` (characters and props) and `ambientCG` (surface textures). Each page of these sites states the license of its download, so read it before you take the file. Strata's own samples use the same rule: their content is CC0 or CC-BY, and each sample lists it in a `CREDITS.md` file.

Keep what you download in a folder of its own, outside the project, and copy into the project only the files you use. A pack holds many files, and a project that holds all of them is slow to open and hard to credit. The folder also keeps files you have not yet checked away from the game.

The credits table is a Markdown file named `CREDITS.md` at the project's root, with one row for each group of files. Strata's samples use six columns, and you will write this row in the last step of the next section:

```text
| Files | Source | Author | License | Attribution | Changes |
| --- | --- | --- | --- | --- | --- |
| `Assets/Models/coin-gold/` | https://kenney.nl/assets/platformer-kit | Kenney | CC0-1.0 | | none |
```

Read the row from the left: which files, the page they came from, who made them, under which license, the credit text a CC-BY license asks for (empty for CC0), and what you changed.

## What Strata reads

Strata imports the file types below. Models must be glTF 2.0, a format that stores a model's shapes, materials and node tree. A `.gltf` file keeps its data in a `.bin` file and image files beside it, and a `.glb` packs the model into one file. Strata does not read `.obj` or `.fbx` models; convert such a model to glTF in a modelling program first.

| Kind | File types |
| --- | --- |
| Models | `.gltf` (with its `.bin` and images), `.glb` |
| Images | `.png`, `.jpg`, `.jpeg`, `.tga`, `.bmp`, `.psd`, `.gif`, `.hdr` |
| Sounds | `.wav`, `.mp3`, `.flac`, `.ogg` |
| Fonts | `.ttf`, `.otf` |
| Color lookup tables for a grade | `.cube` (see [The look of the game](look.md)) |

Models carry a lot of detail: lights, cameras, skins and animations. The table of what the glTF importer supports, what it skips and what it clamps, each with the warning the editor shows, is in [Models and glTF](../assets/models-gltf.md).

## Four words for the steps

The steps use four words. Each names something the editor does for you, and the steps show every one at work.

An **import** reads a source file, such as a `.glb`, and makes from it the data the game loads. The source stays as you got it, so the game never reads the file you downloaded directly.

**Import settings** are the options of one import, such as a model's scale; the editor stores them with the asset and applies them each time the file is imported.

A **sub-asset** is an asset that an import makes from a part of a file. A model gives a mesh for each mesh in the file, a material for each material and a texture for each image.

An **asset handle** is the stable identity of an asset, a number the editor stores in the asset's `.meta` file. Scenes name an asset by its handle and never by its path, so a rename or a move breaks nothing.

The import is the one step that changes data. A bigger or smaller model needs a change in the import settings, not in the scene, because the settings stay with the asset and every copy placed in a scene follows them.

## Import the coin and put it in the level

The coin is a Kenney model, about 0.4 m wide by 0.4 m high, standing on its edge with its origin at the bottom. Your ball is 1 m wide, so the coin should look 40 % as wide as the ball.

:::::steps

1. Make a folder for models and bring the file in. In the Content Browser choose **New ▸ Folder**, name it `Models`, and open it. Then drag `coin-gold.glb` from your file browser into the folder, or choose **Import ▸ Files...** and pick the file. Files dropped anywhere on the editor's window import into the folder the Content Browser shows.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Use **New ▸ Folder** and name it `Models`, then drop the file on the Content Browser.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.createFolder", "parameters": { "path": "Models" } }
   { "command": "asset.import", "parameters": { "file": "<release folder>/Samples/ThirdPerson/Assets/Models/Platformer/coin-gold.glb", "directory": "Models" } }
   ```

   :::
   ::::

   **You should see:** a folder `coin-gold` inside `Models`, holding the model `coin-gold.glb` and a `Textures` folder with `colormap.png`. The import runs in the background: the assets item in the status bar counts it as importing until it is done, and the editor stays usable. Strata copied the image because the model names it, and it keeps the place of the image relative to the model.

   **If you do not see it:** a broken file or an image the importer refuses posts one toast titled "Import failed". The toast names the file and the reason, with **Show Asset** and a line in the Console. The Asset tab shows the same reason above the import settings, and a setting there may fix it. Check the path of the file if the toast says it does not exist.

2. Open the model's folder in the Content Browser and expand the model with the arrow beside it. Click the model and read the Asset tab.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the arrow beside `coin-gold.glb`, then click its name.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.info", "parameters": { "asset": "Models/coin-gold/coin-gold.glb" } }
   ```

   :::
   ::::

   **You should see:** the model's sub-assets on tinted tiles that follow it to its right in the grid. They are the mesh `coin-gold`, the material `colormap` and the texture `colormap (Color)`, each an asset of its own with a thumbnail. The command lists the same three under `subAssets`. In the Asset tab the model's summary lists meshes, triangles, materials and textures, and the import settings follow it.

   **If you do not see it:** the arrow is missing while the import runs. Wait until the status bar no longer counts it as importing.

   **Why:** the material and the texture are separate assets so that several models can share them and you can replace one without touching the others ([Handles and `.meta` files](../assets/handles-meta.md) explains how Strata names them).

3. Look at the files beside the model in your file browser, where `make/project-files` taught you to look. Do not open or edit them.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the project's `Assets/Models/coin-gold/` folder in your file manager.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command that shows the handle.

   ```json
   { "command": "asset.info", "parameters": { "asset": "Models/coin-gold/coin-gold.glb", "bounds": false } }
   ```

   :::
   ::::

   **You should see:** `coin-gold.glb.meta` beside `coin-gold.glb`. The `.meta` file holds the asset's handle and its import settings. With a command, the answer's `asset` field holds the same handle; `"bounds": false` only omits the model's size.

   **If you do not see it:** your file manager hides some files. Enable "show hidden files"; the `.meta` files are ordinary files, and a missing one means the import did not finish.

   **Why:** the handle lives in that file, so you must move and rename assets in the editor, never in the file manager, or the file and its handle part ways.

4. Place the model in the level. Drag `coin-gold.glb` from the Content Browser into the Scene view, onto the ground.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag the model from the Content Browser onto the ground in the Scene view and release.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.place", "parameters": { "asset": "Models/coin-gold/coin-gold.glb", "point": [2, 0, 2] } }
   ```

   The answer's `id` is the identifier (ID) of the new root entity; keep it for the step that replaces the placeholder.

   :::
   ::::

   **You should see:** in the Hierarchy a new entity named `coin-gold` with one child, also named `coin-gold`, and the coin standing on the ground where you released it. In the Inspector the parent shows a bar that links it to the model, and one section, the Transform. The Mesh :term[Renderer]{id=renderer}, the component that draws the mesh, is on the child, so select the child to see it in the Inspector. A command such as `entity.get` also lists `Name` and `PrefabInstance` on both: the Inspector shows the name in its header and the link as that bar.

   **If you do not see it:** the coin is missing while its mesh loads. Wait a moment; Strata draws nothing for a model that is not loaded yet. If it hangs in the air, you dropped it on empty space: press **Ctrl+Z** and drop it again on the ground. Linked groups and the ghost the drop shows are the subject of [Prefabs](prefabs.md).

5. Check the size against the ball. Put the ball and the coin side by side in the Scene view and compare their widths.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Look at the ball and the coin from the same side: the coin should be 40 % of the ball's width, with the ball 1 m wide.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.info", "parameters": { "asset": "Models/coin-gold/coin-gold.glb" } }
   ```

   :::
   ::::

   **You should see:** a coin about two fifths as wide as the ball. The command's `bounds.size` reads about 0.4, 0.4 and 0.175 metres. The editor has no button for a model's bounds, which is why you compare with the ball. Kenney's models use metres, so this one needs no change.

   **If you do not see it:** a coin as wide as the ball, or much smaller, means the model came with another unit. Select the model in the Content Browser, set **Scale** in the Asset tab and press **Apply**. A model made in centimetres needs 0.01. The import runs again in the background, and the placed coin follows, because its root keeps scale 1.

6. Read the other import settings of a model and a texture. Select the model, then the texture below it, and look at the settings the Asset tab offers. You change none of them for the coin.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the texture `colormap (Color)` in the Content Browser, read its settings, then click the model again.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.info", "parameters": { "asset": "Models/coin-gold/coin-gold.glb", "bounds": false } }
   ```

   :::
   ::::

   **You should see:** for the model, **Scale**, `BaseColorFactorsAreSRGB` and more, such as `GenerateLODs`; for the texture, **Usage**, **Quality** and others. The command's `importSettingsProperties` lists every setting with its range.

   **If you do not see it:** a setting is grey when another setting makes it useless. Hover the grey setting: its hint says why.

   **Why:** each setting answers a mistake makers meet. `BaseColorFactorsAreSRGB` fixes colors that look too light or too dark, because some exporters, Kenney's among them, write colors in the wrong encoding. A texture's **Usage** is guessed from its file name: names with `_normal` or `_nor` give a normal map, and `_rough` or `_ao` give data. **Quality** is Fast or High, a choice between import time, stored size and the look of color. `RemoveSun` is for skies ([Lighting](lighting.md)).

7. Replace the placeholder. Move the `Coin` tag to the new model, delete the cylinder, and name the model's root `Coin`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the cylinder `Coin`, press **Delete**, select the model's root, choose **Add Component ▸ Tag** and type `Coin`, then press **F2** and name it `Coin`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.delete", "parameters": { "entities": ["<the id of the cylinder>"] } }
   { "command": "component.add", "parameters": { "entity": "<the id asset.place returned>", "component": "Tag", "values": { "Tag": "Coin" } } }
   { "command": "entity.rename", "parameters": { "entity": "<the id asset.place returned>", "name": "Coin" } }
   ```

   :::
   ::::

   **You should see:** one `Coin` in the Hierarchy, the model, with the tag `Coin` in its Inspector, and the cylinder gone.

   **If you do not see it:** two entities are named `Coin`. Select each and look at its icon and children: the model's root has a child, the cylinder has none. If you removed the wrong one, press **Ctrl+Z** to bring it back, then delete the cylinder.

8. Rename the folder and see that nothing breaks. Select `Models`, press **F2**, type `Props` and press **Enter**. Then rename it back to `Models`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click `Models` in the Content Browser, press **F2**, type `Props` and press **Enter**.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.moveFolder", "parameters": { "path": "Models", "to": "Props" } }
   { "command": "asset.info", "parameters": { "asset": "Props/coin-gold/coin-gold.glb", "bounds": false } }
   { "command": "asset.moveFolder", "parameters": { "path": "Props", "to": "Models" } }
   ```

   :::
   ::::

   **You should see:** the folder with its new name, the model and its `.meta` file inside it, and the coin still in the Scene view.

   **If you do not see it:** the name is taken, and the editor refuses to replace the other folder. Pick another name. A rename back fails too while the moved model is imported again: wait until the status bar no longer counts it as importing, or until `asset.info` answers `importing: false`.

   **Why:** the scene names the coin by its handle, which the rename keeps, so the scene does not need to change.

9. Try to delete the model, then credit it. Select `coin-gold.glb`, press **Delete** or choose **Delete...** in its context menu, read the dialog and press **Cancel**. Then add the credits row of the section above to `CREDITS.md` in the project folder.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Delete...** on the model, read the list in the **Delete Asset** dialog, and press **Cancel**.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.findReferences", "parameters": { "asset": "Models/coin-gold/coin-gold.glb" } }
   ```

   :::
   ::::

   **You should see:** the dialog says the asset moves to the project's trash, and lists the scene that uses it. Its confirm button reads **Delete Anyway**, a warning that the scene would lose the coin. The command `asset.delete` goes further and fails until you pass `force`.

   **If you do not see it:** the dialog shows no list and a **Delete** button when nothing uses the model. Then the delete is safe: the asset goes to the project's trash, and **Ctrl+Z** brings it back with the same handle.

   **Why:** a delete that leaves a scene without its coin is almost never what you want, so the editor shows who is hurt before it acts. The files stay in the trash, so you can undo ([The trash and references](../editor/trash-references.md) has the rules).

:::::

## Result

The coin model is in the project, in the level, tagged `Coin` and credited. In the Hierarchy a placed model is a root that holds its Transform and a child for each node of the file; the mesh is on the child.

```mermaid caption="What the Hierarchy holds once the placeholder is replaced: the root, placed with the name of the file and renamed Coin, with one child for the file's only node, which carries the Mesh Renderer." alt="A tree. The root entity Coin, which holds a Transform and the tag Coin, has one child entity named coin-gold, which holds a Transform and a Mesh Renderer."
flowchart TD
    R["Coin (root): Transform, Tag Coin"] --> C["coin-gold (child): Transform, Mesh Renderer"]
```

::figure{id=content-browser-models}

You made no new feature: you moved a file from someone else's folder into yours. The credits file is part of that, and it travels with the project.

## Variations

**A model in centimetres.** Suppose a model arrives 40 units wide, meant as 40 cm. It shows 40 m wide in the level, a hundred times too big. Set **Scale** to 0.01 and apply: 40 units times 0.01 is 0.4 m. The **Scale** field runs from 0.0001 to 10000.

**A texture that changes on disk.** When you save a new `colormap.png` over the file in the project's folder, the editor notices, imports it again in the background and the models that use it show the new texture, with no menu. Use **Reimport** in the Asset tab when a change does not show.

**A model from a downloaded pack.** Unpack the pack into your download folder and look at the license file before any file. Import one model, not the pack, with **Import ▸ Files...**, and add one row to `CREDITS.md`. For a whole folder of a pack that you want, `asset.import` accepts `directories` and keeps the tree.

The coin still has the plain look of the model's own material. Giving it another look with the imported texture is the subject of [Materials](materials.md).

## Summary

- Use only CC0 files, or CC-BY files with their credit, and keep every file you use in the project's `CREDITS.md`.
- Importing copies a model and the images it names into a folder of the project, in the background, and gives it sub-assets and a handle.
- Check an imported model's size against a known one and fix a wrong unit with the **Scale** import setting.
- Rename and move assets in the editor so handles hold, and delete through the dialog: used assets warn you, and the trash lets **Ctrl+Z** bring a deleted asset back.

## Check yourself

1. A site offers a free sword model with no license text. May you use it?

   :::answer{tests="licenses"}
   No. A file with no clear license stays out of the project, because you have no right to use it. Ask the author, or choose a CC0 file.
   :::

2. You import `crate.glb`, which names an image `Textures/wood.png`. Where do the model and the image finish in the project?

   :::answer{tests="import-model"}
   Strata makes a folder named `crate` in the target folder and puts the model in it, with `Textures/wood.png` beside it at the same relative place.
   :::

3. A pack's model measures 250 units in the Scene view, and you expect 2.5 m. What do you change, and to what?

   :::answer{tests="check-size"}
   Set the model's **Scale** import setting to 0.01 and press **Apply**: 250 times 0.01 is 2.5 m. Entities already placed follow it.
   :::

4. You rename the folder `Models` to `Props`. The scene still shows the coin. Why?

   :::answer{tests="safe-moves import-model"}
   The scene stores the coin's asset handle, and the rename keeps the handle in the `.meta` file. Only the path changed.
   :::

## Exercises

1. **Basic.** Import `barrel.glb` from the same folder of the `ThirdPerson` sample (Kenney's Platformer Kit, CC0), place it beside the ball and check its size. The barrel should be about 0.5 m wide.

   :::answer[Worked solution]{tests="import-model check-size" solution="tutorials/make/assets/exercise-1.tutorial.json"}
   Drop `barrel.glb` on the Content Browser's `Models` folder, wait for the import, then drag it from there next to the ball. The ball is 1 m wide, so the barrel is about half as wide; `asset.info` reports `bounds.size` of about 0.52, 0.48 and 0.52 metres.
   :::

2. **Medium.** Place one barrel. Predict whether **Delete...** on `barrel.glb` is refused, try it and read who uses it in the **Delete Asset** dialog. Then delete the barrel entity, delete the model and bring it back with **Ctrl+Z**.

   :::answer[Worked solution]{tests="safe-moves"}
   The dialog does not delete at once: it lists your scene as a user and offers **Delete Anyway**, and the command refuses without `force`. Cancel, delete the barrel entity, then choose **Delete...** again: the list is empty and the button reads **Delete**. After you press it, **Ctrl+Z** returns the model with its handle.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetImporters.cpp`: the importers registered at start, which decide the file types the page lists.
- `Strata/src/Strata/Asset/GltfImporter.cpp`: the model importer, its import settings and the model's root entity.
- `Strata/src/Strata/Asset/TextureImporter.cpp`: the texture importer, its settings and the usage guessed from names.
- `StrataEditor/src/Editor/EditorAssetCommands.cpp`: `asset.import`, `asset.moveFolder` and `asset.delete`.
- `StrataEditor/src/UI/DeleteAssetDialog.cpp`: the dialog that lists the users of an asset.

## Further reading

- [Creative Commons, "About CC0"](https://creativecommons.org/publicdomain/zero/1.0/): what the CC0 dedication says, for beginners.
- [Kenney, "Platformer Kit"](https://kenney.nl/assets/platformer-kit): the pack the coin comes from, for beginners.
