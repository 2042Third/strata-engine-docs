---
id: make/gi
title: "Trying global illumination"
description: "Build a closed room, enable Strata's experimental bounce light, read its four debug views and learn where it fails, to decide if your interiors use it."
kind: how-to
size: M
tracks: [G]
needs: [make/reflections]
time: 60
learn:
  - id: bounce-views
    text: compare a room with and without global illumination and read its four debug views
  - id: thin-walls
    text: predict the thinnest wall that keeps light out at each voxel size and find it with the Voxels view
  - id: settling
    text: compute how many bounces the light of a closed room needs to settle and watch it settle
  - id: limits
    text: name what global illumination cannot do yet and choose whether a game's scenes use it
since: 0.8.0
status: final
---

Strata can trace bounce light: the sunlight that a floor sends on to the walls and the ceiling. This page builds a closed room, enables that light and shows what it adds and where it fails. The feature is experimental in this release. Before you start:

- You have a new project from the Basic 3D template, saved with nothing added: **New Project** in the launcher, or `project.create` with `directory`, `name` and the template `basic3d`. Its Graphics Quality is High, and only High and **Ultra** draw this light: Low and Medium draw none. [The quality chapter](quality.md) teaches the presets.
- You know the sky light, ambient occlusion and probes of [the reflections chapter](reflections.md).
- You can create a cube from the Hierarchy's **+** menu and set its position and scale in meters ([entities](scenes-entities.md), [units](transforms-units.md)).
- You can find the Post Process component and the debug view chip ([lighting](lighting.md)).

## Why a room needs bounce light

The sun lights only what it reaches, yet the shaded part of a real room is not black. Lit surfaces send part of their light on, and the surfaces they reach send part of that on again. The sky light of [the reflections chapter](reflections.md) fakes this: it lights every surface as if no roof covered it. Ambient occlusion darkens creases only where the screen shows them.

Global illumination (GI) is the name for all indirect light, bounces between surfaces included. Take a closed room whose surfaces send on 0.73 of the light they receive: that share is their albedo, and 0.73 is a bright white paint. The sun lights a patch of floor. The first bounce carries 0.73 of that light to the walls, and each next bounce carries 0.73 of the one before.

| Bounce | Light it adds, as a share of the first bounce |
| --- | --- |
| 1 | 1.00 |
| 2 | 0.73 |
| 3 | 0.53 |
| 4 | 0.39 |
| 5 | 0.28 |

The bounces never stop, but they fade. For an albedo $k$ they add up to $1 / (1 - k)$, which reads "one divided by one minus $k$". With $k$ of 0.73 that is 3.7 times the first bounce, so the first bounce carries only 27 % of the light the room finally holds. A bright room is mostly bounce light.

Strata calculates one bounce each frame. After 15 bounces the next one adds less than a quarter of one percent of the total, and two spare frames make 17. A room of this white therefore settles in 17 frames, which is 0.3 seconds at 60 frames per second. A plaster room of albedo 0.58 needs 12 frames, and the brightest whites need up to 38.

A voxel is a small cube of space, a pixel with a third dimension. Strata keeps a copy of the world around the camera in voxels and traces the light through it. A probe of this light is a point in the air, 0.5 m from the next at High, that gathers the light arriving from every direction. Each surface takes its bounce light from the probes beside it. [How the world becomes voxels](../indirect/gi-voxels.md) has its own chapter.

```mermaid caption="The light is traced through a copy of the world made of small cubes, and each surface reads it from the probes beside it. The picture of the screen is never used." alt="A flow from left to right. The triangles of the scene feed a copy made of small cubes around the camera. The sun, the sky and glowing surfaces light that copy. Probes gather the light from it, and each surface of the image reads the probes near it. A note says the screen is never an input."
flowchart LR
	T["Triangles of the scene"] --> V["Voxel copy around the camera"]
	L["Sun, sky and glowing surfaces"] --> V
	V --> P["Probes gather the light"]
	P --> S["Each surface reads nearby probes"]
	X["The screen"] -.->|"never used"| P
```

:::why[Why the world and never the screen]
GI traces the world and never the screen. Light from a surface behind the camera still counts, and Strata blends nothing over frames, so a moving camera leaves no smear. The price is the copy's coarseness: its cubes are 10 cm wide at High, and thin things blur, as the steps show. [Why the screen fails](../indirect/problem.md) explains the choice, and [how the probes gather the light](../indirect/gi-cascades.md) follows it.
:::

## The room you build

The room stands on the Basic 3D ground. The sun of that template stands 40 degrees above the horizon and shines mostly from the +X side, so the window is in the +X wall. The table gives the sizes in meters.

| Part | Material | Translation | Scale |
| --- | --- | --- | --- |
| `Floor` | `RedFloor` | 0, 0.15, 0 | 4.6, 0.3, 4.6 |
| `Ceiling` | `Plaster` | 0, 2.95, 0 | 4.6, 0.3, 4.6 |
| `Wall North` | `Plaster` | 0, 1.55, -2.15 | 4.6, 2.5, 0.3 |
| `Wall South` | `Plaster` | 0, 1.55, 2.15 | 4.6, 2.5, 0.3 |
| `Wall West` | `Plaster` | -2.15, 1.55, 0 | 0.3, 2.5, 4 |
| `Wall East Low` | `Plaster` | 2.15, 0.65, 0 | 0.3, 0.7, 4 |
| `Wall East High` | `Plaster` | 2.15, 2.4, 0 | 0.3, 0.8, 4 |

The inside is 4 m by 4 m and 2.5 m high. The two east pieces leave a window slot 1 m high, from 1 m to 2 m above the ground. A band of sun about 0.8 m wide lights the floor, from 0.8 m to 1.6 m inside the window wall. Every face lies on a multiple of 10 cm, which is the voxel size at High.

## Build the room

:::::steps

1. Make two materials: `Plaster`, a bright gray, and `RedFloor`, a red.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Content Browser press **New ▸ Material**, type `Plaster` and press **Enter**. Click the color box of `Base Color` and type 0.73, 0.73, 0.73. Make `RedFloor` the same way with 0.6, 0.05, 0.04. Set `Roughness` of both to 0.9.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/Plaster.stmat", "properties": { "BaseColor": [0.73, 0.73, 0.73, 1], "Roughness": 0.9 } } }
   { "command": "material.create", "parameters": { "path": "Materials/RedFloor.stmat", "properties": { "BaseColor": [0.6, 0.05, 0.04, 1], "Roughness": 0.9 } } }
   ```

   :::
   ::::

   **You should see:** two materials with a palette icon in the Content Browser, a gray one and a red one.

   **If you do not see it:** a material is missing. Press **New ▸ Material** again in the folder where you want it.

2. Build the seven parts of the table.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+ ▸ Cube** in the Hierarchy, press **F2**, type `Floor` and press **Enter**. Type its **Translation** and **Scale** from the table and pick its material in the **Mesh Renderer**. Press **Ctrl+D** on its row to duplicate it for the next part, and rename and change the copy.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Floor", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/RedFloor.stmat" }, "Transform": { "Translation": [0, 0.15, 0], "Scale": [4.6, 0.3, 4.6] } } } }
   { "command": "entity.create", "parameters": { "name": "Ceiling", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Plaster.stmat" }, "Transform": { "Translation": [0, 2.95, 0], "Scale": [4.6, 0.3, 4.6] } } } }
   { "command": "entity.create", "parameters": { "name": "Wall North", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Plaster.stmat" }, "Transform": { "Translation": [0, 1.55, -2.15], "Scale": [4.6, 2.5, 0.3] } } } }
   { "command": "entity.create", "parameters": { "name": "Wall South", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Plaster.stmat" }, "Transform": { "Translation": [0, 1.55, 2.15], "Scale": [4.6, 2.5, 0.3] } } } }
   { "command": "entity.create", "parameters": { "name": "Wall West", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Plaster.stmat" }, "Transform": { "Translation": [-2.15, 1.55, 0], "Scale": [0.3, 2.5, 4] } } } }
   { "command": "entity.create", "parameters": { "name": "Wall East Low", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Plaster.stmat" }, "Transform": { "Translation": [2.15, 0.65, 0], "Scale": [0.3, 0.7, 4] } } } }
   { "command": "entity.create", "parameters": { "name": "Wall East High", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Plaster.stmat" }, "Transform": { "Translation": [2.15, 2.4, 0], "Scale": [0.3, 0.8, 4] } } } }
   ```

   :::
   ::::

   **You should see:** a closed box on the ground, white outside, with a long slot in its +X wall.

   **If you do not see it:** the box has holes or sticks out. Compare each **Translation** and **Scale** with the table.

3. Put the Scene view inside the room, looking toward the window wall.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Hold the right button over the Scene view and press **W**, **A**, **S** and **D** to fly through the south wall to the room's southwest corner, then turn the view toward the slot. The editor camera passes through walls.
   :::
   :::tab[With a command]

   ```json
   { "command": "camera.set", "parameters": { "position": [-1.7, 1.5, 1.7], "target": [1.0, 0.7, -0.8] } }
   ```

   :::
   ::::

   **You should see:** the inside of the room: the red floor, the gray walls and ceiling, the slot, and a band of bright red sunlight on the floor. This is the room without global illumination.

   **If you do not see it:** you see the outside of a wall. The camera is not inside the room: move it between the walls.

:::::

## Enable global illumination and read it

:::::steps

1. Enable global illumination. Select `Post Process`. In the Inspector's section named Global illumination, enable **Global Illumination**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click `Post Process` in the Hierarchy, find the section, and click the check box of **Global Illumination**. **Global Illumination Intensity** below it becomes active.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "GlobalIllumination": true } } }
   ```

   A command takes an entity's identifier (ID), not its name: `<the ID of Post Process>` is what `entity.find` returns for that name.
   :::
   ::::

   **You should see:** for a few frames the room looks as before, because the engine builds its voxels first. Then the light rises. The floor, lit by the sun, lights the walls and the ceiling, and the red floor tints the parts of the walls near it. The walls and the ceiling are brightest beside the band of sun.

   **If you do not see it:** nothing changes. Check that the quality chip of the Scene view names **High** or **Ultra**, and that `Post Process` is the first active Post Process of the scene.

2. Read the bounce light alone. Open the debug view chip and choose **GI: indirect light on white**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the chip at the top of the Scene view and choose **GI: indirect light on white**.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "gi" } }
   ```

   :::
   ::::

   **You should see:** every surface white and lit by indirect light only. The light is strongest near the band of sun, reaches the ceiling, and takes a red tint near the floor.

   **If you do not see it:** the view is black. Wait a second for the voxels, and check step 1.

3. Read how much of the sky each surface sees. Choose **Open: the share of sky each surface sees**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose the entry in the same chip.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "open" } }
   ```

   :::
   ::::

   **You should see:** gray values, brighter beside the slot, where surfaces see a part of the sky, and darkest where the roof hides it. The legend names the median.

   **If you do not see it:** the view is flat. Fly nearer to the slot.

4. Read the voxels. Choose **Voxels: the scene as the GI sees it**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose the entry in the same chip.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "voxels" } }
   ```

   :::
   ::::

   **You should see:** the room made of cubes, each in the albedo of its surface: red floor, gray walls, the slot as a gap. The legend says "Two-sided: no bounce", and the note names four levels, "10-80 cm", from the finest cubes near the camera to the coarsest farther away.

   **If you do not see it:** the room is smooth. The Scene view is not at High, or the scene does not ask for global illumination.

5. Read the probes. Choose **Probes: the GI's probes, dead ones red**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose the entry in the same chip.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "probes" } }
   ```

   :::
   ::::

   **You should see:** a grid of probes 0.5 m apart, none dark red: the legend counts 0 dead. A probe inside the floor, the ceiling or a wall moves off into open space. Only one deep inside a thick solid, such as a cube 2 m wide, is dead: it sends nothing and shows dark red.

   **If you do not see it:** you see no probes. Fly the camera into the room, because the probes shown are the ones near it.

:::::

## Push the light to its limits

:::::steps

1. Make one wall too thin. Select `Wall East Low` and set its **Scale** X to 0.06 and its **Translation** X to 2.05, so that both of its faces lie inside the voxel from x = 2 to x = 2.1. Choose the **Voxels** view again. When you finish, set the wall back to a **Scale** X of 0.3 and a **Translation** X of 2.15.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type the two numbers in the Inspector's **Transform**, then choose **Voxels: the scene as the GI sees it** in the chip.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Wall East Low>", "component": "Transform", "values": { "Translation": [2.05, 0.65, 0], "Scale": [0.06, 0.7, 4] } } }
   { "command": "viewport.setSettings", "parameters": { "debugView": "voxels" } }
   { "command": "component.set", "parameters": { "entity": "<the ID of Wall East Low>", "component": "Transform", "values": { "Translation": [2.15, 0.65, 0], "Scale": [0.3, 0.7, 4] } } }
   ```

   :::
   ::::

   **You should see:** the wall in the error color, the color of the legend's "Two-sided: no bounce". One voxel holds both faces of the wall, and the engine cannot tell them apart, so that wall sends no bounce light.

   **If you do not see it:** the wall keeps its gray. The view shows the lit image, or the numbers are not in the **Transform** of `Wall East Low`. A 10 cm wall with its faces on the grid stays gray: each face has a voxel of its own.

2. Watch the light settle. Clear **Global Illumination** of `Post Process`, choose the **GI** view, and enable it again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **GI: indirect light on white** in the chip. Clear the check box of **Global Illumination**, and click it again.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "gi" } }
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "GlobalIllumination": false } } }
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "GlobalIllumination": true } } }
   ```

   A command takes an entity's identifier (ID), not its name: `<the ID of Post Process>` is what `entity.find` returns for that name.
   :::
   ::::

   **You should see:** the engine drops the voxels when the scene stops asking and builds them again. The light then rises within about 17 frames, a third of a second at 60 frames per second, because each bounce arrives one frame after the one before. A camera cut or a scene that opens does the same.

   **If you do not see it:** the change is too fast to follow. Players see the same brief rise after a cut in your game.

3. Turn the sun. Choose the **Lit (no debug view)** view and move the sun toward the south.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Lit (no debug view)**. Select `Sun`, press **E** with the pointer over the Scene view and drag the ring that turns it around the vertical axis by about 50 degrees.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "none" } }
   { "command": "lighting.applySkyPreset", "parameters": { "preset": "Clear", "sunElevation": 40, "sunAzimuth": 70 } }
   ```

   :::
   ::::

   **You should see:** the band of sun slides along the floor, and the bounce light on the walls moves with it in the same frame, with no delay and no trail.

   **If you do not see it:** the light stays. Check that you turned the `Sun` and not another entity.

4. Change the strength of the bounce. Set **Global Illumination Intensity** to 2, then to 0.5, then back to 1.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Ctrl+click the slider to type a value. Compare the three values in the **GI** view.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "GlobalIlluminationIntensity": 2 } } }
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "GlobalIlluminationIntensity": 0.5 } } }
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "GlobalIlluminationIntensity": 1 } } }
   ```

   :::
   ::::

   **You should see:** at 2 the traced light shades the surfaces twice as strongly, at 0.5 half as strongly. The **GI** view shows the change best, because automatic exposure hides part of it in the lit image.

   **If you do not see it:** the field is gray and you cannot change it. The Inspector says that Global Illumination is off: enable it first.

5. Compare with Medium. Choose Medium in the quality chip of the Scene view, look, and then return to the project's own preset.

   ::::tabs{sync=how}
   :::tab[In the editor]
   With the **Lit (no debug view)** view open, click the quality chip and choose **Medium**. Then choose the first entry of the chip, which names the project's preset.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "quality": "medium" } }
   { "command": "viewport.setSettings", "parameters": { "quality": "project" } }
   ```

   :::
   ::::

   **You should see:** the image exactly as it was before you enabled global illumination, bit for bit, because Medium draws none. The chip changes only the Scene view, never the project.

   **If you do not see it:** the light stays. Check that the chip names Medium, and that the Scene view does not look through the scene's camera, where the game's own preset applies.

:::::

## What it cannot do yet

The room already showed some limits. The notes of the release list the rest, and you design your interiors around them.

- **Thin walls and gaps.** Keep walls two voxels thick: 20 cm at High, 40 cm at Low, a level that only a Custom quality chooses. A thinner wall sends no bounce light where one voxel holds both of its faces. Gaps, ledges and recesses of that size go dark, darker than without global illumination.
- **Range.** At High the light fades out between 7.5 m and 9.5 m around the camera, and between 5.5 m and 7.5 m above and below it. Outdoors the edge of that bubble shows.
- **Low is a poor copy.** At the Low level light bounces once and the picture is too dark: a room lit by a ceiling panel keeps a dark ceiling.
- **Round objects.** A ball reads a few percent too dark at its sides.
- **Cost.** At 3840 x 2160 pixels the High level takes about 4.2 ms of :term[graphics processing unit]{id=gpu} (GPU) time, which is 25 % of the 16.7 ms of a frame at 60 frames per second. It also takes about 156 MiB of graphics memory for each view.
- **Moving objects** take part as boxes of their size: a ball or a hollow object shades and bounces light as its box would until it rests. When more than 64 parts move at once, the bounce light ignores the others until they stop. Animated characters receive bounce light but neither block it nor bounce it.
- **Lamps.** Point and spot lights add no bounce light, and glowing surfaces do. The light of a rect light counts twice if its panel also glows, so leave global illumination off in such scenes for now.
- **Mirrors.** The bounce light is diffuse only and never shows in reflections.

Five more things do not exist yet: an **Ultra** level, a color of each voxel from its texture, hardware ray queries, nested fields of probes and denser probes near surfaces. A texture counts only by its mean color. [The limits chapter](../indirect/gi-limits.md) gives the evidence for each.

## Result

You have a closed room whose floor lights its walls and whose red floor tints them, with the four views of its light. The pictures show the room without and with global illumination.

::compare{id=result before=off after=on}

The thin wall of the Voxels view looks like this.

::figure{id=thin-wall}

## Variations

- **A ceiling panel.** Clear the check box of the `Sun`, and add a cube `Panel` of **Scale** 1.6, 0.2, 1.6 at **Translation** 0, 2.7, 0 under the ceiling. Give it a material whose **Emissive Color** is 1, 0.9, 0.75 and whose **Emissive Intensity** is 800. At High the panel lights the ceiling around it and the walls, and at Low the ceiling stays dark. Do not use **Make Area Light** on this panel: its light would count twice.
- **An outdoor yard.** Disable the room's parts and put a few boxes on the ground. In the **GI** view, fly more than 10 m away from the boxes. The field ends around the camera, and the light of the ground changes where it fades: this edge is why the page recommends interiors.
- **Only interiors.** The Post Process of each scene decides. Enable global illumination in the interior scenes, and leave it off in the outdoor ones, which then spend no memory on it. A player who chooses Low or Medium gets none anywhere, so every interior must also look right without it ([quality](quality.md)).

## Summary

- Global illumination needs a Post Process that enables it and a quality of High or **Ultra**. It traces the world, never the screen. Its four views show the bounce light (**GI**), the sky each surface sees (**Open**), the voxel copy (**Voxels**) and the probes (**Probes**).
- Keep walls two voxels thick: 20 cm at High, 40 cm at Low. A thinner wall turns two-sided in the **Voxels** view and sends no bounce light where one voxel holds both of its faces.
- Each bounce takes a frame, and a closed room settles in about 12 to 38 frames: the first bounce of albedo $k$ carries $1 - k$ of the final light.
- Global illumination cannot yet light with lamps, show in reflections or reach farther than about 9.5 m, so use it for interiors with thick walls.

## Check yourself

1. You enable **Global Illumination** and nothing changes. The quality chip says Medium. Why?

   :::answer{tests="bounce-views"}
   At Low and Medium the quality draws no global illumination, so the image is exactly the one without it. Choose High or **Ultra**, or change the project's Graphics Quality.
   :::

2. In the **Probes** view some probes are dark red. What does that mean?

   :::answer{tests="bounce-views"}
   A dead probe lies inside a solid, such as a wall or the floor, and sends no light. Probes in the air of the room are alive.
   :::

3. Your walls are 15 cm thick. Are they safe at High, and would 30 cm walls be safe at Low?

   :::answer{tests="thin-walls"}
   Neither is safe: 15 cm is under two 10 cm voxels, and 30 cm under two 20 cm voxels. The **Voxels** view marks such a wall only where one voxel holds both faces, so it can still look one-sided.
   :::

4. A closed room of albedo 0.5 is lit by a patch of sun. What share of its final light does the first bounce carry?

   :::answer{tests="settling"}
   The bounces add up to $1 / (1 - 0.5)$, which is 2 times the first bounce, so the first carries 50 %. A darker room has less bounce light and settles sooner.
   :::

5. Why does a lamp post's point light add nothing to the bounce light of a yard, and a glowing sign does?

   :::answer{tests="limits"}
   The voxels are lit by the sun, the sky and glowing surfaces. Point and spot lights are not in the voxels yet, so only their direct light shows.
   :::

6. What do you gain from tracing the world instead of the screen, and what does it cost?

   :::answer{tests="limits"}
   Light from what is off screen counts, and nothing smears when the camera moves. The cost is the coarse copy: thin things blur, and the light fades out about 9.5 m from the camera.
   :::

## Exercises

1. **Basic.** A closed room has every surface at albedo 0.73. What share of its final light do the first two bounces carry together?

   :::answer{tests="settling"}
   The first adds 1 and the second 0.73 of the first, 1.73 in all. The total is 3.7, so the two carry 1.73 ÷ 3.7, which is 47 %.
   :::

2. **Medium.** You want your room to work at the Low level of the GI. How thick must a wall be there, and do the 30 cm walls of this page pass?

   :::answer{tests="thin-walls"}
   Low has 20 cm voxels, so a wall needs two of them, 40 cm. The 30 cm walls are too thin there: thicken them to 40 cm, with each face on a multiple of 20 cm.
   :::

3. **Hard.** Find the thinnest wall that stays one-sided at High. Set `Wall East Low` to a thickness of 0.25 m, then 0.20, 0.15, 0.10 and 0.05, with its inner face at x = 2.02, off the grid, and read the **Voxels** view each time. Then try 0.05 with the inner face at x = 2.

   :::answer[Worked solution]{tests="thin-walls" solution="tutorials/make/gi/exercise-3.tutorial.json"}
   The solution sets the six walls in turn. Only the 0.05 m wall at 2.02 turns to the error color: its faces, at 2.02 and 2.07, share the voxel from 2 to 2.1. At x = 2 its inner face lies on a grid line and counts only in the voxel in front of it, so it stays gray. The view marks only walls whose faces share a voxel, so the guide's 20 cm stays the rule.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RendererComponents.h`: the two Post Process fields, `GlobalIllumination` and `GlobalIlluminationIntensity`.
- `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp`: the voxel sizes, the probe spacing, the reach of the field and the settling frames of each level.
- `Strata/src/Strata/Renderer/RendererQuality.cpp`: the Graphics Quality row that disables it at Low and Medium.
- `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp`: the frame's work and the debug views.
- `Strata/shaders/GI/VoxelFinalize.comp.slang`: where a thin wall becomes two-sided.
- `StrataEditor/src/Panels/ViewportPanel.cpp`: the debug view chip and the quality chip.
- `Docs/Manual/Lighting.md` and `Docs/Releases/0.8.0.md`: the engine's own guide and the known issues of this release.

## Further reading

- Docs/Manual/Lighting.md in the engine, "Global illumination (experimental)": every value of this page in one place (beginner).
- The 0.8.0 release notes of Strata, "Known issues": the measured limits (intermediate).
- Majercik, Guertin, Nowrouzezahrai and McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, 2019: the probe fields that Strata's design follows in part (advanced).
- Alexander Sannikov, "Radiance Cascades": the method that gathers the light in Strata (advanced).
