---
id: make/materials
title: "Materials"
description: "Give Coin Run a gold coin and a textured metal ball, and learn what a material is, which numbers it holds and how to check them."
kind: tutorial
size: L
tracks: [G, B]
needs: [make/assets]
time: 80
learn:
  - id: material-idea
    text: explain what a material is and what base color, metallic and roughness each control
  - id: make-material
    text: create a material, set its values and give it to an entity
  - id: texture-maps
    text: build a material from a base color map, a metal and rough map and a normal map
  - id: alpha-glow
    text: choose an alpha mode, an emission or glass for a surface
  - id: audit-albedo
    text: find base colors outside the plausible range with the Albedo view and fix them
since: 0.3.0
status: final
---

## What you will make

A gold coin that gleams and a ball of smooth grey metal, both in Coin Run's level. Along the way you meet every number a material holds and the view that tells you when a color is wrong.

::figure{id=result}

## What you need

- The end of [Assets](assets.md): the level with the coin model placed, scaled and tagged. Its root entity is named `Coin`. If you skipped that page, download its project from the box at the end of its [Result](assets.md#result). The zip holds a folder named `Assets`, after the page, and in it `CoinRun.stproj`: open that file with **File ▸ Open Project...**.
- Three texture files from the release of Strata, in `Samples/PhysicsPlayground/Assets/Textures/Metal/`: `Metal032_Color.jpg`, `Metal032_MetallicRoughness.jpg` and `Metal032_NormalGL.jpg`. They come from `ambientCG`, a source of free textures, under the Creative Commons zero license (:term[CC0]{id=cc0}), which has no conditions, and the sample's `CREDITS.md` names them.
- About 80 minutes, most of it spent trying values.

## Make a gold coin

A **material** is an asset that says how a surface answers light: which color it shows, whether it is metal, how smooth it is, and what else it adds. Every mesh in the scene points at one. Change the material and every mesh that uses it changes with it.

Strata uses one model of surface for everything, called **PBR** (physically based rendering). The values of a material describe the surface itself, so they mean the same under a bright sun, a dim lamp or a cloudy sky. You do not adjust a material for each light. The model has three main numbers, and everything else builds on them. The editor shows each property name split into words, so `BaseColor` appears as Base Color.

The first number is the base color. For a painted wall it is the color of the paint. For a metal it is the color of the reflection: gold reflects yellow light, so its base color is yellow.

The second is the metallic value, from 0 to 1. A value of 0 says the surface is paint, wood, stone or plastic, and 1 says bare metal. Real surfaces are one or the other, so you almost always type 0 or 1. The values between are for the thin border where rust meets steel in a texture.

The third is the roughness, from 0 (a mirror) to 1 (chalk). A rough surface scatters light in all directions, so the sun's highlight becomes wide and dim. A smooth one keeps the light together, so the highlight is small and bright.

::figure{id=sphere-grid}

The picture shows both rows at five roughness values. The top row has metallic 0 and the bottom row has metallic 1. Compare the highlights along a row, then compare the rows: the metal has no flat colored face, only reflections.

### Colors are numbers

A color on a screen is three numbers: how much red, green and blue light. Each runs from 0 for none to 1 for the most the screen shows. So (0, 0, 0) is black, (1, 1, 1) is white, (1, 0, 0) is pure red and (0.5, 0.5, 0.5) is grey. Strata keeps these numbers as amounts of light, not as how bright a color box looks to the eye, which [Color](../basics/color.md) explains. The editor shows exactly the stored numbers.

The color picker you meet below shows the three numbers in fields, next to the hue bar. A fourth number, alpha, says how much of the surface is there; 1 is solid. The alpha section below uses it.

Real materials reflect only part of the light that hits them. Fresh asphalt reflects about 4 % and fresh snow about 85 %, and nothing real reflects more. So base colors of paint or stone lie between about 0.03 and 0.85, and a value above 0.85 makes a surface look like plastic. The audit section below shows the view that checks this for you.

Bare metals are different: they reflect a color, and the numbers are higher. This table lists typical values for a few, taken from public tables of measured metals, not from Strata:

| Metal | Red | Green | Blue |
| --- | --- | --- | --- |
| Gold | 1.00 | 0.77 | 0.34 |
| Copper | 0.95 | 0.64 | 0.54 |
| Iron | 0.56 | 0.57 | 0.58 |
| Silver | 0.97 | 0.96 | 0.91 |

You use the gold row now.

### Make the material and give it to the coin

:::::steps

1. Make a material in the `Materials` folder. The Content Browser keeps all assets of the project, and Basic 3D already made that folder for `Ground`, the material of the ground.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Content Browser open the folder `Materials`, press **New ▸ Material**, type `Gold` and press **Enter**. The Asset tab shows the new material.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/Gold.stmat" } }
   ```

   :::
   ::::

   **You should see:** `Gold` with a palette icon in the folder, and in the Asset tab the material editor, a list of values labeled `Base Color`, `Metallic`, `Roughness`, `Emissive Color` and more.

   **If you do not see it:** the Asset tab is hidden behind another tab. Click the material once in the Content Browser to bring the tab forward.

   ::figure{id=material-editor}

2. Set the values of gold. Click the color box of `Base Color`, which opens the picker, and type the three numbers of the table's gold row into its fields. Then set `Metallic` to `1` and `Roughness` to `0.3`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Ctrl+click a slider to type a value. The viewport follows while you drag, and one change is one undo step when you release.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/Gold.stmat", "properties": { "BaseColor": [1.0, 0.77, 0.34, 1.0], "Metallic": 1.0, "Roughness": 0.3 } } }
   ```

   :::
   ::::

   **You should see:** nothing in the scene yet, because no mesh uses the material. The values stay in the editor.

   **If you do not see it:** the values are not in the material. Click `Gold` in the Content Browser and read them in the Asset tab.

3. Give the coin the material. Expand `Coin` in the Hierarchy: the model's root holds only a Transform, and its child `coin-gold` holds the mesh. Select the child and set the **Material** of its **Mesh Renderer** in the Inspector, or drag `Gold` from the Content Browser onto the coin in the Scene view.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Inspector, find **Mesh Renderer**, click the picker beside **Material** and choose `Gold`. The **New Material** button of the same section makes a material of its own instead. A drop from the Content Browser into the Scene view does the same in one gesture and one undo step.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of coin-gold>", "component": "MeshRenderer", "values": { "Material": "Materials/Gold.stmat" } } }
   ```

   Replace the placeholder with the identifier (ID) that `entity.find` returns for the name `coin-gold`, as on [Scenes and entities](scenes-entities.md). Every `<the ID of …>` on this page works the same way.
   :::
   ::::

   **You should see:** the coin turns the warm yellow of gold.

   **If you do not see it:** you selected the root `Coin`, which has no **Mesh Renderer**, so the Inspector shows no **Material**. Select its child.

4. Spread the highlight. Drag `Roughness` from `0` to `1` and watch the sun's highlight grow wider and dimmer. Then set `Metallic` to `0` and look: the coin is now yellow paint. Put both back, `0.3` and `1`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+Z** after each experiment, or drag the values back. A drag shows a preview and a release writes the file.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/Gold.stmat", "properties": { "Roughness": 1.0, "Metallic": 0.0 } } }
   { "command": "material.set", "parameters": { "material": "Materials/Gold.stmat", "properties": { "Roughness": 0.3, "Metallic": 1.0 } } }
   ```

   :::
   ::::

   **You should see:** at roughness 1 the coin is dull and flat, and at metallic 0 it has a pale reflection on a yellow face, like a painted toy.

   **If you do not see it:** the coin is small in the view. Select it and press **F** in the Scene view to frame it.

   **Why:** gold is a metal, so its color comes from its reflection. With metallic 0 the base color becomes paint under a clear coating, which is the usual mistake of "gold paint" on a metal.

:::::

::checkpoint{stage=1}

::figure{id=gold-coin}

## Make the ball's metal from textures

A flat number gives every point of the surface the same value. A **texture** is an image that gives each point its own value. A material takes up to five maps in its basic set. You use three: a base color map, a metal and rough map, and a normal map.

The numbers of a material multiply its maps. The metal and rough map holds two values per pixel, roughness in its green channel and metallic in its blue channel, and Strata multiplies them by the material's `Roughness` and `Metallic`. A new material has `Metallic` 0 and `Roughness` 0.5. With those, the map would give no metal at all and half its rough values. So once a map is in place you set both numbers to 1 and let the map decide.

:::::steps

1. Import the three files into a `Textures/Metal` folder. The files come from `Samples/PhysicsPlayground/Assets/Textures/Metal/` in the release of Strata.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Make the folders `Textures` and `Metal` with **New ▸ Folder**. Drag `Metal032_Color.jpg`, `Metal032_MetallicRoughness.jpg` and `Metal032_NormalGL.jpg` from your file browser onto the Content Browser while `Metal` is open. The status bar counts the imports while they run in the background.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "files": ["<release folder>/Samples/PhysicsPlayground/Assets/Textures/Metal/Metal032_Color.jpg", "<release folder>/Samples/PhysicsPlayground/Assets/Textures/Metal/Metal032_MetallicRoughness.jpg", "<release folder>/Samples/PhysicsPlayground/Assets/Textures/Metal/Metal032_NormalGL.jpg"], "directory": "Textures/Metal" } }
   ```

   :::
   ::::

   **You should see:** three textures in the folder, each with a small preview.

   **If you do not see it:** a toast "Import failed" names the file and the reason. Check the path of the release folder and drag the file again.

2. Look at the usage each texture got. The importer guesses it from the file name: a name with `normal` is a normal map, a name with `rough`, `metal` or `occlusion` holds data, and any other name is a color. The importer reads whole words, split at `_`, `-` and capital letters, so `Metal032` is not the word `metal`. Click each texture and read its **Usage** in the Asset tab.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click each texture in the Content Browser. The Asset tab lists its :term[import settings]{id=import-settings}.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.info", "parameters": { "asset": "Textures/Metal/Metal032_Color.jpg" } }
   { "command": "asset.info", "parameters": { "asset": "Textures/Metal/Metal032_MetallicRoughness.jpg" } }
   { "command": "asset.info", "parameters": { "asset": "Textures/Metal/Metal032_NormalGL.jpg" } }
   ```

   Each answer's `importSettings` holds the `Usage`, and `importing` is `true` while the import still runs.
   :::
   ::::

   **You should see:** `Color` for `Metal032_Color`, `Data` for `Metal032_MetallicRoughness` and `NormalMap` for `Metal032_NormalGL`.

   **If you do not see it:** the file was renamed on its way. Set **Usage** by hand in the Asset tab and press **Apply**.

3. Make the ball's material. Create `Materials/Ball.stmat`, set its base color map and its metal and rough map, set `Metallic` and `Roughness` to `1`, and set the tiling.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **New ▸ Material** in `Materials` and name it `Ball`. Click the picker of `Base Color Map` and choose the color texture, then do the same for `Metal/Rough Map`. Set `Metallic` and `Roughness` to `1` and `UV Tiling` to `2` and `2`.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/Ball.stmat", "properties": { "BaseColorMap": "Textures/Metal/Metal032_Color.jpg", "MetallicRoughnessMap": "Textures/Metal/Metal032_MetallicRoughness.jpg", "Metallic": 1.0, "Roughness": 1.0, "UVTiling": [2.0, 2.0] } } }
   ```

   :::
   ::::

   **You should see:** no warning under any map. `UVTiling` repeats the image. The texture coordinates of a mesh run from 0 to 1 across it; a tiling of 2 runs them from 0 to 2, so the image repeats twice in each direction.

   **If you do not see it:** a map is empty. Click its picker again; a drop of the texture onto the picker also works.

4. Give the ball the material. Select `Ball` and set the **Material** of its **Mesh Renderer**, as you did for the coin.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose `Ball` in the **Material** picker of the Inspector, or drag it onto the ball in the Scene view.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Ball>", "component": "MeshRenderer", "values": { "Material": "Materials/Ball.stmat" } } }
   ```

   :::
   ::::

   **You should see:** a smooth grey metal ball. The maps of this set change little across the ball, so its metal looks even.

   **If you do not see it:** the ball is plain grey. Check that `UVTiling` is not `0` and that both map slots hold their textures.

:::::

::checkpoint{stage=2}

::figure{id=ball-metal}

## Add a normal map and fix it

A mesh of a ball is smooth, but the metal on it has dents. Drawing every dent as geometry would cost millions of triangles. A **normal map** is a texture that stores, for each pixel, the direction the surface faces there. The :term[renderer]{id=renderer} lights each pixel as if the surface had that direction, so a flat face looks uneven without any extra geometry. The silhouette stays smooth: a normal map changes the light, not the shape.

A normal map holds directions, not colors, and the stored numbers must stay exactly as written. Strata stores two of the three numbers (the sideways tilts) and computes the third. If you tell the importer a normal map is a color, it treats the numbers as a picture and changes them, and every direction comes out wrong. So a texture has a **Usage**: `Color` for pictures, `Data` for numbers such as roughness and `NormalMap` for directions. The material editor checks the match for you.

:::::steps

1. Add the normal map to the ball's material. Select `Ball`, open its material under the label "Edit material (shared)" in the Inspector, and choose `Metal032_NormalGL` for `NormalMap`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the picker of `NormalMap` and choose the texture. Changes apply to every entity that uses the material.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/Ball.stmat", "properties": { "NormalMap": "Textures/Metal/Metal032_NormalGL.jpg" } } }
   ```

   :::
   ::::

   **You should see:** no warning under `NormalMap`, and a ball that looks almost as before. The normal map of this set is nearly flat, so its dents are too fine to see; a map with deeper dents shows them in the light of the sun.

   **If you do not see it:** a warning stands under `NormalMap`. Check that the slot holds the texture and that the import is done.

2. Break it on purpose. Select the texture `Metal032_NormalGL`, set its **Usage** to `Color` and press **Apply**. Then select `Ball` and look at its material again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Pick `Color` in the **Usage** list of the Asset tab and press **Apply**. The import runs again in the background.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.setImportSettings", "parameters": { "asset": "Textures/Metal/Metal032_NormalGL.jpg", "settings": { "Usage": "Color" } } }
   { "command": "material.get", "parameters": { "material": "Materials/Ball.stmat" } }
   ```

   The answer's `warnings` holds the message and, under `fix`, the command that mends it.
   :::
   ::::

   **You should see:** below `NormalMap` the material editor shows a warning, `Metal032_NormalGL is imported as Color: its normals will be wrong`, with a button **Import as Normal Map**.

   **If you do not see it:** the import is not done. Wait until the status bar's import count reaches zero.

   ::figure{id=normal-warning}

3. Fix it with the button. Press **Import as Normal Map** under the warning.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Import as Normal Map**. It sets the texture's **Usage** back and imports again.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.setImportSettings", "parameters": { "asset": "Textures/Metal/Metal032_NormalGL.jpg", "settings": { "Usage": "NormalMap" } } }
   { "command": "material.get", "parameters": { "material": "Materials/Ball.stmat" } }
   ```

   :::
   ::::

   **You should see:** the warning disappears.

   **If you do not see it:** the button is gone but the warning stays. Select the ball again so that the Inspector refreshes.

4. Meet the one convention that differs. Two normal map conventions exist: OpenGL maps, which Strata reads, and `DirectX` maps, which store the green channel upside down. A name with `dx` turns the import setting `FlipGreen` on by itself. Enable it for your map, look at the ball, and disable it again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Asset tab of `Metal032_NormalGL` tick the box of `FlipGreen`, labelled Flip Green, press **Apply**, look at the ball, then clear the box and press **Apply**.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.setImportSettings", "parameters": { "asset": "Textures/Metal/Metal032_NormalGL.jpg", "settings": { "FlipGreen": true } } }
   { "command": "asset.setImportSettings", "parameters": { "asset": "Textures/Metal/Metal032_NormalGL.jpg", "settings": { "FlipGreen": false } } }
   ```

   :::
   ::::

   **You should see:** hardly any change, because this map is nearly flat. On a map with deep dents, the setting makes the dents look like bumps and the bumps like dents, as if the light came from the other side. Off, the map reads as it was made.

   **If you do not see it:** the setting is grey. It works only while **Usage** is `NormalMap`.

   **Why:** a map from a `DirectX` tool and a map from an OpenGL tool differ only in the sign of the green numbers. The `GL` in your file name says which kind it is, so you leave the setting off.

:::::

::checkpoint{stage=3}

::figure{id=ball-normal}

## Add a glow and try the other modes

Some surfaces emit light themselves: a lamp, a screen, a coin in a fantasy game. A material gives that with an `EmissiveColor` and an `EmissiveIntensity`. The color says which color glows. The intensity says how strong the glow is, in a unit of brightness called nits, which [Lighting](lighting.md) explains. At the default color, black, nothing glows.

:::::steps

1. Make the coin glow faintly. Select the material `Gold`, set `EmissiveColor` to a warm orange, (1.0, 0.6, 0.1), and `EmissiveIntensity` to `50`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the color box of `Emissive Color`, type the three numbers, and then set `Emissive Intensity` to `50`.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/Gold.stmat", "properties": { "EmissiveColor": [1.0, 0.6, 0.1], "EmissiveIntensity": 50.0 } } }
   ```

   :::
   ::::

   **You should see:** hardly any change in the sun. Surfaces in sunlight send back far more than 50 nits, so a faint glow vanishes by day; it shows at night, which you build in [Lighting](lighting.md).

   **If you do not see it:** nothing changes at all. Check that the color is not black: a black color multiplied by any intensity stays black.

2. Prepare a scratch cube for the alpha modes; you delete it afterwards. Add a cube with **+ ▸ Cube**, name it `Scratch`, and give it a new material `Materials/Scratch.stmat` with a `BaseColor` of (0.2, 0.5, 1.0) and an alpha of `0.4`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Use **New ▸ Material**, set the base color through its picker (the picker has an alpha bar) and drop the material on the cube.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/Scratch.stmat", "properties": { "BaseColor": [0.2, 0.5, 1.0, 0.4] } } }
   { "command": "entity.create", "parameters": { "name": "Scratch", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Scratch.stmat" }, "Transform": { "Translation": [0, 1.5, 0] } } } }
   ```

   The answer of `entity.create` holds the new entity's ID under `id`. Keep it: step 5 deletes the cube with it.
   :::
   ::::

   **You should see:** a solid blue cube. The default `AlphaMode` is `Opaque`, which ignores alpha.

   **If you do not see it:** the cube is inside the ground. Lift it with the move :term[gizmo]{id=gizmo-start}.

3. Change `AlphaMode`. Set it to `Mask` and the cube vanishes: Mask keeps a pixel when its alpha is at or above `AlphaCutoff` (0.5 by default) and drops it otherwise, and 0.4 is below. Set `AlphaCutoff` to `0.3` and the cube returns, fully solid. Then set `Blend` and the cube turns see-through.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Pick the mode in the `AlphaMode` list, and drag `AlphaCutoff`.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/Scratch.stmat", "properties": { "AlphaMode": "Mask", "AlphaCutoff": 0.3 } } }
   { "command": "material.set", "parameters": { "material": "Materials/Scratch.stmat", "properties": { "AlphaMode": "Blend" } } }
   ```

   :::
   ::::

   **You should see:** Mask gives a hard edge, with no half-transparent pixels. Blend mixes the cube with what is behind it, 40 % of the cube's color to 60 % of the scene.

   **If you do not see it:** the cube stays solid in Blend. The alpha of the color is `1`: set it to `0.4` in the picker.

   **Why:** Mask suits leaves and fences, whose pixels are either there or not, and it casts exact shadows. Blend suits smoke and films, but Strata draws blended surfaces after the solid ones, sorted back to front, so they cost more and can overlap wrongly.

4. Make glass. Set `AlphaMode` to `Opaque`, `BaseColor` to white (1, 1, 1, 1), `Roughness` to `0`, `Transmission` to `1` and `IOR` to `1.5`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set the four values in the material editor. `IOR` says how much light bends when it enters the surface.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/Scratch.stmat", "properties": { "AlphaMode": "Opaque", "BaseColor": [1, 1, 1, 1], "Roughness": 0.0, "Transmission": 1.0, "IOR": 1.5 } } }
   ```

   :::
   ::::

   **You should see:** a clear cube that shows the scene behind it.

   **If you do not see it:** the cube looks white and solid. `Transmission` is still `0`.

5. Delete the scratch cube. Select `Scratch` and press **Delete**. The material stays in the folder; remove it with **Delete...** in the Content Browser if you wish, which the trash lets you bring back with Ctrl+Z.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the cube in the Hierarchy and press **Delete**.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.delete", "parameters": { "entities": ["<the ID of Scratch>"] } }
   ```

   :::
   ::::

   **You should see:** the cube gone, and the coin and the ball untouched.

   **If you do not see it:** the Hierarchy still lists it. Click an empty spot in the Hierarchy and look again.

:::::

Three more settings complete the set. `Clearcoat`, from 0 to 1, adds a thin glossy layer over the base, like coating on car paint. `Unlit` shows the base color with no lighting at all, for signs and screens. `DoubleSided` draws the back of a face too, for paper-thin things such as leaves, which have no thickness.

::checkpoint{stage=4}

::figure{id=coin-glow}

## Audit the colors

The most common mistake with materials is a base color that is too bright. A wall set to pure white reflects all the light that hits it, which no real wall does, and it glows and looks like plastic. Strata has a view that finds such colors for you.

The Albedo view paints every surface with its base color and marks colors whose luminance is outside 0.03 to 0.85. Luminance is a single brightness for a color, the sum of the three numbers weighted by how strongly the eye sees each: $0.2126 r + 0.7152 g + 0.0722 b$, where $r$, $g$ and $b$ are the red, green and blue numbers. Green counts most because the eye is most sensitive to it.

:::example
Take your gold, (1.0, 0.77, 0.34). Its luminance is $0.2126 \times 1.0 + 0.7152 \times 0.77 + 0.0722 \times 0.34 = 0.2126 + 0.5507 + 0.0245 = 0.788$. That is under 0.85, so the view accepts it. Pure white, (1, 1, 1), gives $0.2126 + 0.7152 + 0.0722 = 1.0$, which is above 0.85, so the view marks it.
:::

The view marks metals by the same rule, so a bright metal such as silver (luminance 0.96) is marked although its color is correct. A mark is a question for you to answer, not a verdict.

:::::steps

1. Make a wall too white. Make `Materials/Chalk.stmat` with a `BaseColor` of (1, 1, 1), add a cube with **+ ▸ Cube**, name it `Wall`, and give it the material. Place it at (0, 1, -1.5), behind the coin and the ball, and scale it to (4, 2, 0.2).

   ::::tabs{sync=how}
   :::tab[In the editor]
   Make the material with **New ▸ Material**, then drop it on the new cube. Set the cube's **Translation** and **Scale** in the Inspector.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/Chalk.stmat", "properties": { "BaseColor": [1, 1, 1, 1] } } }
   { "command": "entity.create", "parameters": { "name": "Wall", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Chalk.stmat" }, "Transform": { "Translation": [0, 1, -1.5], "Scale": [4, 2, 0.2] } } } }
   ```

   Keep the `id` of the answer for the delete in step 4: `entity.find` with the name `Wall` also finds the first wall under `Walls`, which has the same name.
   :::
   ::::

   **You should see:** a white slab in the scene. It looks fine at first glance, which is why the view exists.

   **If you do not see it:** the slab is inside the ground. Lift it by half its height.

2. Open the Albedo view. In the row of chips on top of the Scene view press the debug view chip and choose **Albedo: base colors, out of 0.03-0.85 marked**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press the chip with the layers icon and choose the entry. The chip shows `Albedo` while the view is on.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "albedo" } }
   ```

   Look at the Scene view of your editor's window. The legend is drawn there only: no command answers it, and a picture from `viewport.capture` shows the stripes without the legend.
   :::
   ::::

   **You should see:** the new wall striped red, and the four walls of `Walls` striped too. They have no material of their own, and the engine's default material is white, (1, 1, 1). A legend reads `Above 0.85` with the share of the image that is above it. The coin, the ball and the ground show their plain base colors.

   **If you do not see it:** nothing is marked. Check that the chip shows `Albedo`: only the Scene view has debug views, and the Game view has none.

   ::figure{id=albedo-view}

3. Fix the wall. Set the `BaseColor` of `Chalk` to (0.8, 0.8, 0.8) and watch the stripes disappear.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the picker of the material's `Base Color` and type `0.8` into the three fields.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/Chalk.stmat", "properties": { "BaseColor": [0.8, 0.8, 0.8, 1] } } }
   ```

   :::
   ::::

   **You should see:** the stripes gone from the new wall, which now shows light grey, and the legend's share smaller. The four walls of `Walls` stay striped, because they still use the default white. Leave them as they are: this tutorial keeps them, and a mark is a question you answer for your own levels. Switch the chip back to **Lit (no debug view)**: the new wall is now a realistic white paint.

   **If you do not see it:** stripes remain on a surface other than the four walls. Its base color is above 0.85 too; lower it as well.

4. Delete the wall, switch the view back and save. Select the new `Wall` at the top level of the Hierarchy, not the one under `Walls`, press **Delete**, set the chip to **Lit (no debug view)** and press **Ctrl+S**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Delete the entity, choose **Lit (no debug view)** in the chip and press **Ctrl+S**. Every material edit saves itself; the scene's save keeps the assignments to the coin and the ball.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.delete", "parameters": { "entities": ["<the ID of Wall>"] } }
   { "command": "viewport.setSettings", "parameters": { "debugView": "none" } }
   { "command": "scene.save" }
   ```

   :::
   ::::

   **You should see:** the level with the gold coin and the metal ball, as you left it.

   **If you do not see it:** the save did not run. Click the Scene view and press **Ctrl+S** again.

:::::

### Guidance for plausible values

Keep this table at hand when you invent a material. The first column lists what you are making and the second what to type.

| Surface | Value |
| --- | --- |
| Water and wet ground | `IOR` 1.33, `Roughness` 0.02 to 0.06 |
| Glass | `IOR` 1.5, `Transmission` 1 |
| Painted surfaces | `Roughness` 0.15 to 0.45 |
| Any base color of a non-metal | below 0.85 |
| Bare metal | `Metallic` 1, base color from a table of metals |

The `IOR` of a non-metal also sets how strongly it reflects at a straight view: water reflects about 2 %, and glass and most paints about 4 %.

### Common mistakes

- A near-white base color. Fix: use at most 0.85, as the Albedo view shows.
- `Metallic` above 0 on paint, plastic or wood. Fix: metallic is 0 or 1; use 1 only for bare metal.
- A normal map imported as a color. Fix: press **Import as Normal Map** in the warning.
- A metal and rough map with the numbers at their defaults. Fix: set both to 1.

### What Strata does not do here

Strata has no :term[shaders]{id=shader} as assets and no material graphs. Every surface uses the one physically based model, and the engine's shaders are compiled when the engine is built.

:::why
One model means every material works under every light, in the editor and in the game, and no artist can write a shader that breaks the lighting. The cost is that a look the model cannot make, such as a cartoon outline, is not possible through materials.
:::

A loaded material never changes while it is in use: the editor replaces it with a new one when you edit. So Strata has no per-entity tint, no hit flash and no way for a script to edit a material's values. A game gives an entity's **Mesh Renderer** another material instead, as the Tetris sample does to color its pieces. The material is a tool of the maker, not a variable of the game.

::checkpoint{stage=5}

::figure{id=final}

## Summary

- A material says how a surface answers light with a base color, a metallic value and a roughness; physically based rendering (PBR) values mean the same under any light.
- Create a material with **New ▸ Material**, set its values in the Asset tab and give it to the **Mesh Renderer** of the entity that holds the mesh.
- A material multiplies its maps, so a map-driven metal sets `Metallic` and `Roughness` to 1; normal maps are data, never color, and `FlipGreen` fits `DirectX` maps.
- Alpha modes, emission, transmission and `IOR` cover cut-outs, glow and glass.
- The Albedo view marks base colors outside 0.03 to 0.85; fix a mark by lowering the color toward the plausible range.

## Check yourself

1. A wall looks like plastic under every light. What do you check first, and where?

   :::answer{tests="material-idea,audit-albedo"}
   Check the base color of its material: above 0.85 looks plastic. Open the Albedo view in the Scene view's debug chip and see whether the wall is striped red.
   :::

2. You make a material for the ball with a metal and rough map and leave the numbers at their defaults. The ball shows no metal. Why?

   :::answer{tests="texture-maps,make-material"}
   A new material has `Metallic` 0 and `Roughness` 0.5, and the numbers multiply the map: 0 times the map's metal values stays 0. Set both to 1.
   :::

3. A normal map imported as `Color` makes a surface look wrong. Which two things in the editor show you the cause?

   :::answer{tests="texture-maps"}
   The texture's **Usage** in the Asset tab reads `Color`, and the material editor shows a warning under `NormalMap` with a button **Import as Normal Map** that fixes it.
   :::

4. A wire fence is drawn with a texture of wire and holes. Which `AlphaMode` do you pick, and what does it use to decide?

   :::answer{tests="alpha-glow"}
   `Mask`. It keeps a pixel when its alpha is at or above `AlphaCutoff` and drops it otherwise, so the cut edge is sharp.
   :::

5. Why can a script not tint a coin red when it is hit by changing its material?

   :::answer{tests="make-material"}
   A loaded material is never changed, so scripts cannot edit one. Make a second material, `Materials/CoinHit.stmat`, and give the coin's **Mesh Renderer** that asset.
   :::

## Exercises

1. **Basic.** Make a material set: `Materials/Copper.stmat` (copper's color from the table, `Metallic` 1, `Roughness` 0.4) and `Materials/Asphalt.stmat` (base color 0.05, `Roughness` 0.9, `Metallic` 0). Give each to a scratch cube and check both in the Albedo view.

   :::answer[Worked solution]{tests="make-material,audit-albedo" solution="tutorials/make/materials/exercise-1.tutorial.json"}
   Copper's luminance is $0.2126 \times 0.95 + 0.7152 \times 0.64 + 0.0722 \times 0.54 = 0.70$, inside the range. Asphalt at 0.05 is above 0.03, so neither is marked. Set the asphalt to 0.01 and the view marks it blue.
   :::

2. **Medium.** Make wet ground: a dark base color (0.05), `Roughness` 0.05 and `IOR` 1.33, on a flat cube. Predict how the reflection of the sky compares with a dry copy at `Roughness` 0.9, then compare.

   :::answer{tests="alpha-glow"}
   The wet copy shows a sharp, bright reflection of the sky, because smooth surfaces keep reflected light together. The dry copy spreads it into a dull shine.
   :::

3. **Hard.** Give the ball the same texture set but a `Roughness` of `0.5` and a `Metallic` of `1`. Predict what the metal and rough map's roughness values do, and test with `material.get`.

   :::answer{tests="texture-maps"}
   The map's roughness is multiplied by 0.5, so every pixel is half as rough as the map says: the ball looks smoother and shinier. `material.get` shows the stored values and no warning.
   :::

## Where it lives in Strata

- A material is an asset of type Material, stored as JSON in a `.stmat` file; its properties are listed in `Strata/src/Strata/Renderer/Material.h`.
- The material editor is `StrataEditor/src/UI/MaterialEditor.cpp`, shown in the Asset tab and inside the Mesh Renderer section of the Inspector.
- The commands `material.create`, `material.get` and `material.set` are in `StrataEditor/src/Editor/EditorAssetCommands.cpp`.
- The importer's guess of a texture's usage from its name is in `Strata/src/Strata/Asset/TextureImporter.cpp`.
- The Albedo view's range, 0.03 to 0.85, is in `Strata/src/Strata/Renderer/SceneRenderData.h`.

## Further reading

- Physically Based Rendering: From Theory to Implementation, by Pharr, Jakob and Humphreys: how light and surfaces are modeled; advanced.
- The glTF 2.0 specification, metallic-roughness material: the model Strata follows, in the form of a document; intermediate.
- ambientCG: free, CC0 material textures, to practice with; beginner.
