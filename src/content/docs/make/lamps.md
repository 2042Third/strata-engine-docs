---
id: make/lamps
title: "Lamps: point, spot and area lights and their shadows"
description: "Light a night yard with point, spot and rectangle lights in real units, give the lamps shadows, size their glints and keep their cost down."
kind: tutorial
size: L
tracks: [G]
needs: [make/project-coin-run]
time: 120
learn:
  - id: lamp-units
    text: compute a lamp's candela from its lumens, and the lux it gives a surface at a distance
  - id: lamp-fields
    text: explain what a lamp's range, cone angles and source radius change, and what they leave alone
  - id: lantern-prefab
    text: build a lantern prefab with a point light, a bulb and a housing, and place it four times
  - id: lamp-shadows
    text: set shadows on lamps, fit their filter and biases, and keep a lamp out of its own shadow
  - id: lamp-cost
    text: predict which lamps draw their shadow views again each frame and read the count on the Stats chip
since: 0.3.0
status: final
---

## What you will make

A small yard at night: a hut, a sign and four lantern posts, lit by lamps in real units. The lanterns cast shadows, one swings on an arm and a key switches it off, and the hut has a panel of light in its roof.

::figure{id=result}

## What you need

- The yard: a new project from the Basic 3D template with the scene `Scenes/Yard.stscene` as its :term[start scene]{id=start-scene}, which every checkpoint opens. The scene holds a ground, a hut of cubes with a gap for a door, a sign, four posts and an arm on one of them. It has no light but the template's sun. No download holds the yard before the first section: Checkpoint 1 holds it with that section's moon and exposure set. Open its project, or make a Basic 3D project (`project.create` with the template `basic3d`) and run Checkpoint 1's commands.
- The chapters on [lighting](lighting.md) (lux, nits and exposure in stops), [prefabs](prefabs.md), [your first script](first-script.md) and [input](input.md).
- About two hours. You write one small script.

## Make the yard dark

A lamp shows only against darkness, so you first build the night. The moon is a **Directional Light** like the sun, with a small number: a full moon gives 0.1 to 0.3 lux, and you take 0.2. The template sun gives 120,000 lux. The ratio is 600,000, about $2^{19}$, so the night is 19 stops darker than the day.

A screen cannot show both, so you set the exposure by hand. The reference table of the [lighting chapter](lighting.md) suits a scene under the moon with an **Exposure** of +3.5 to +5. You take +4.

:::::steps

1. Open the yard scene.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Open Scene...** and pick `Scenes/Yard.stscene`.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/Yard.stscene" } }
   ```

   :::
   ::::

   **You should see:** the hut, the sign, four posts and a bar on one of them. In Checkpoint 1 steps 2 and 3 are already done.

   **If you do not see it:** open Checkpoint 1's project first.

2. Turn the sun into the moon. Select `Sun` and set **Intensity** to 0.2.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click `Sun` in the Hierarchy, type `0.2` into **Intensity** of its **Directional Light** and press **Enter**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sun>", "component": "DirectionalLight", "values": { "Intensity": 0.2 } } }
   ```

   A command takes an entity's identifier (ID), not its name: every `<the ID of …>` on this page is the ID that `entity.find` returns for that name, as on [Scenes and entities](scenes-entities.md).
   :::
   ::::

   **You should see:** the picture turns almost black, then the automatic exposure lifts it. The sky takes its light from the sun, so it lost the same 19 stops.

   **If you do not see it:** the value stays at 120000 when you leave the field before **Enter**. Type it again.

3. Take the exposure into your hands. Select `Post Process`, clear **Auto Exposure** and set **Exposure** to 4.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click `Post Process`, clear **Auto Exposure**, type `4` into **Exposure** and press **Enter**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AutoExposure": false, "Exposure": 4 } } }
   ```

   :::
   ::::

   **You should see:** a yard like a dull day, blue sky and gray ground: the exposure gives back the stops the moon lost. The moon casts sharp shadows.

   **If you do not see it:** the picture is white. **Auto Exposure** is still on, or the sun still has its day value.

:::::

::checkpoint{stage=1}

::figure{id=night-yard}

## Light the yard with one lamp

Lamp boxes give lumens, and Strata asks for :term[candela]{id=candela}. A lumen (lm) counts all the light a lamp sends out, and a candela (cd) says how bright the lamp looks from one direction. A point light shines equally in every direction, and the directions of a sphere add up to a factor of 12.57. So the lumens of a point light are 12.57 times its candela, and a box that says 800 lumens gives $800 / 12.57 = 63.6$, about 64 cd.

The candela becomes light on a surface by the inverse square law. A surface that faces a lamp of $I$ candela at a distance of $d$ metres gets $I / d^2$ lux. For 64 cd that is 64 lux at 1 m, 16 lux at 2 m and 4 lux at 4 m. Each doubling of the distance costs two stops.

:::example[The lamp at the top of a post]
A lantern hangs 3.34 m above the ground. The ground right below it gets $64 / 3.34^2 = 5.7$ lux. The moon gives 0.2 lux, so the pool is $5.7 / 0.2 = 29$ times brighter, almost 5 stops. At your exposure of +4 the pool is far above middle gray and turns white. A lower exposure such as +1 keeps the pool and drops the ground under the moon to dark gray.
:::

A lamp that lit everything at any distance would cost every pixel, so every point light has a **Range**, the distance where its light ends. Strata multiplies the inverse square law by a window that is 1 near the lamp and falls smoothly to 0 at the range. The sketch computes the lux for 64 cd and a range of 8 m at five distances: first the plain law, then the windowed one.

```cpp sketch="make-lamps-falloff.cpp"
// The light a lamp puts on a surface that faces it: the inverse square law and Strata's window to the range.
#include <algorithm>
#include <cstdio>

float GetLux(float candela, float range, float distance)
{
	const float ratio = (distance * distance) / (range * range);
	const float window = std::clamp(1.0f - ratio * ratio, 0.0f, 1.0f);
	return candela * window * window / (distance * distance);
}

int main()
{
	const float candela = 64.0f;
	const float range = 8.0f;

	std::printf("distance  plain lux  windowed lux\n");
	for (float distance : { 1.0f, 2.0f, 4.0f, 6.0f, 8.0f })
		std::printf("%5.0f m  %9.2f  %12.2f\n", distance, candela / (distance * distance), GetLux(candela, range, distance));
	return 0;
}
```

```text output-of="make-lamps-falloff.cpp"
distance  plain lux  windowed lux
    1 m      64.00         63.97
    2 m      16.00         15.88
    4 m       4.00          3.52
    6 m       1.78          0.83
    8 m       1.00          0.00
```

1. **Line 7:** the squares of the distance and the range make a ratio, so no square root is needed.
2. **Line 8:** the window is 1 near the lamp and falls to 0 where the ratio reaches 1, at the range.
3. **Line 9:** the plain inverse square law times the square of the window.
4. **Lines 18–19:** one row for each distance, the plain value beside the windowed one.

At 4 m the lamp gives 3.52 lux, not 4: the window has cut 12 %. At 6 m it gives 0.83 lux, less than half of the plain 1.78. At 8 m it gives nothing.

The range is not a brightness knob. A range of 40 m would give 4.00 lux at 4 m, and the lamp would look nearly the same close by. What it changes is where the light stops and what it costs: the engine asks only the pixels inside the range whether the lamp reaches them. Give a lamp the range that its light needs, as a lamp 3.34 m above the ground needs more than 3.34 m.

:::why
A real lamp has no range: its light only gets thin. A game cannot add up thousands of lamps that reach everywhere, so each lamp ends at a range. The window hides the end, at the cost of a little brightness near it. [Lights and their range](../light/lights.md) explains the :term[shader]{id=shader} side.
:::

:::::steps

1. Add a point light above the first post.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **+** in the Hierarchy and choose **Point Light**. Rename it `Lamp`. In its Transform set **Translation** to -4, 3.34, 1.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Lamp", "components": { "PointLight": {}, "Transform": { "Translation": [-4, 3.34, 1] } } } }
   ```

   :::
   ::::

   **You should see:** a pool of light on the ground around the first post, from the default 10 cd and 10 m of range, and the **Point Light** component in the Inspector.

   **If you do not see it:** the light is under the ground when its **Translation** has a negative second number. Check the 3.34.

   ::figure{id=point-light-inspector}

2. Give the lamp the numbers of a household bulb: 64 cd, a warm color, a range of 8 m.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `64` into **Intensity** and `8` into **Range**. Click the color box of **Color** and set it to 1, 0.85, 0.6.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Lamp>", "component": "PointLight", "values": { "Intensity": 64, "Range": 8, "Color": [1, 0.85, 0.6] } } }
   ```

   :::
   ::::

   **You should see:** a brighter, warmer pool, nearly white at your exposure of +4, as the example predicted.

   **If you do not see it:** the pool is still the old one when **Intensity** shows 10. Press **Enter** after you type.

3. Lower the exposure so that the pool and the ground under the moon both show. Select `Post Process` and set **Exposure** to 1.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `1` into **Exposure** of `Post Process`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "Exposure": 1 } } }
   ```

   :::
   ::::

   **You should see:** the pool keeps its warm gray, and the ground beyond it is darker than before.

   **If you do not see it:** the whole picture is still bright. The value is in stops: each step down halves the light on screen.

4. Shorten the range below the lamp's height and look at the ground. Set **Range** to 3, then back to 8.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `3` into **Range**, look, then type `8`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Lamp>", "component": "PointLight", "values": { "Range": 3 } } }
   ```

   Send the same command with `"Range": 8` to return.
   :::
   ::::

   **You should see:** at 3 m the ground below the lamp stays dark. The lamp hangs 3.34 m up, so its light ends before it arrives. At 8 m the pool returns.

   **If you do not see it:** the pool stays when the range is still above 3.34. Check that you typed 3 and not 30.

5. Add a bulb. A bulb is a small sphere with an emissive material, so that a viewer sees the lamp. Make the material, then the sphere.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Content Browser create a material `Materials/Bulb.stmat`. Set **Emissive Color** to 1, 0.8, 0.5 and **Emissive Intensity** to `2000`. Click **+**, open **Mesh only** and choose **Sphere**. Rename it `Bulb`, set **Translation** to -4, 3.34, 1 and **Scale** to 0.08 in each field, and drop the material on its **Material** field.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.create", "parameters": { "path": "Materials/Bulb.stmat" } }
   { "command": "material.set", "parameters": { "material": "Materials/Bulb.stmat", "properties": { "EmissiveColor": [1, 0.8, 0.5], "EmissiveIntensity": 2000 } } }
   { "command": "entity.create", "parameters": { "name": "Bulb", "components": { "MeshRenderer": { "Mesh": "Builtin/Sphere", "Material": "Materials/Bulb.stmat" }, "Transform": { "Translation": [-4, 3.34, 1], "Scale": [0.08, 0.08, 0.08] } } } }
   ```

   :::
   ::::

   **You should see:** a small, glowing, orange-white ball in the lamp's place. A sphere of scale 0.08 has a radius of 0.04 m, the size of a lantern bulb.

   **If you do not see it:** the ball is gray when the material is not set. Its **Emissive Color** must not be black.

:::::

The bulb is a picture of light, not a source. It lights nothing: the `Lamp` does, because the **Global Illumination** of the **Post Process**, the one effect that lets a glowing surface light its neighbours, is off by default. You match the two by hand: the bulb shows 2,000 nits, and the lamp gives the 64 cd of the bulb it stands for.

::checkpoint{stage=2}

::figure{id=one-lamp}

## Aim a spot light at the sign

A **Spot Light** is a point light that shines in a cone. It shines along the entity's forward direction, which is its minus Z axis. Its **Inner Cone Angle** and **Outer Cone Angle** are half angles: the light is full inside the inner one and falls to zero at the outer one. A new spot light has 20 cd, a range of 15 m and angles of 20 and 30 degrees, so it lights a cone 60 degrees wide.

Between the two angles the light falls smoothly. At an angle $a$ off the axis the spot light's share is $t^2$, where $t = (\cos a - \cos \text{outer}) / (\cos \text{inner} - \cos \text{outer})$, clamped between 0 and 1. For an inner angle of 14 degrees and an outer of 22, the share at 18 degrees is $t = (0.951 - 0.927) / (0.970 - 0.927) = 0.55$, so $t^2 = 0.31$. A point 18 degrees off the axis gets 31 % of the light.

The candela of a spot light is the brightness along its axis. A narrower cone does not make it brighter: the cone only cuts the light that lies outside it.

The sign board lies 2.5 m ahead of the spot light and 1.4 m below it, 2.87 m away. The beam must turn down by $\arctan(1.4 / 2.5)$, which is 29 degrees. A rotation of -29 around the X axis does it.

:::::steps

1. Add the spot light and aim it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **+** and choose **Spot Light**. Rename it `Sign Spot`. Set **Translation** to -1.8, 3, 5 and **Rotation** to -29, 0, 0.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Sign Spot", "components": { "SpotLight": {}, "Transform": { "Translation": [-1.8, 3, 5], "Rotation": [-29, 0, 0] } } } }
   ```

   :::
   ::::

   **You should see:** a cone of light that lands on the sign board and the ground below it.

   **If you do not see it:** the light falls elsewhere when the rotation has the wrong sign. A plus sign tilts the beam upward.

2. Set the numbers: 60 cd, an inner angle of 14 and an outer angle of 22.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `60` into **Intensity**, `14` into **Inner Cone Angle** and `22` into **Outer Cone Angle**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sign Spot>", "component": "SpotLight", "values": { "Intensity": 60, "InnerConeAngle": 14, "OuterConeAngle": 22 } } }
   ```

   :::
   ::::

   **You should see:** the board lit by a patch of light that is full in the middle and fades at its rim.

   **If you do not see it:** the patch has a hard edge when the inner angle equals the outer one. Keep the inner angle smaller.

3. Narrow the cone: set **Inner Cone Angle** to 8 and **Outer Cone Angle** to 12.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `12` into **Outer Cone Angle** first, then `8` into **Inner Cone Angle**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sign Spot>", "component": "SpotLight", "values": { "InnerConeAngle": 8, "OuterConeAngle": 12 } } }
   ```

   :::
   ::::

   **You should see:** the patch shrinks to about half its width, from a radius of $2.87 \tan 22° = 1.16$ m to $2.87 \tan 12° = 0.61$ m. The middle stays as bright as before: a surface that faces the lamp gets $60 / 2.87^2 = 7.3$ lux either way.

   **If you do not see it:** the patch looks dimmer when you look at its rim. Compare the centers.

:::::

::checkpoint{stage=3}

::figure{id=sign-spot}

## Make the lantern a prefab

Four lanterns share one design, so you save one as a prefab, as with the coin in [Prefabs](prefabs.md). Its root `Lantern` has three children: the `Housing`, a short cylinder that holds the lamp, the `Bulb` on top of it, and the `Light`, the lamp you already made. The root stands at the bulb's center, 0.34 m above the housing's bottom edge, so that the housing rests on the post.

:::::steps

1. Make the root and move the lamp and the bulb under it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **+ ▸ Empty**, rename it `Lantern` and set its **Translation** to -4, 3.34, 1. Drag `Lamp` and then `Bulb` onto `Lantern` in the Hierarchy. Rename `Lamp` to `Light`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Lantern", "components": { "Transform": { "Translation": [-4, 3.34, 1] } } } }
   { "command": "entity.setParent", "parameters": { "entities": [ "<the ID of Lamp>", "<the ID of Bulb>" ], "parent": "<the ID of Lantern>" } }
   { "command": "entity.rename", "parameters": { "entity": "<the ID of Lamp>", "name": "Light" } }
   ```

   :::
   ::::

   **You should see:** `Lantern` with the children `Light` and `Bulb`, and the pool unchanged. Both keep their place in the world, where the root stands, so each **Translation** reads 0, 0, 0: a child's numbers count from its parent.

   **If you do not see it:** the root is not at -4, 3.34, 1. Correct it, then set the children's **Translation** to 0, 0, 0.

2. Add the housing. Right-click `Lantern`, open **Create Child ▸ Mesh only** and choose **Cylinder**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Rename the new entity `Housing`. Set **Translation** to 0, -0.19, 0 and **Scale** to 0.3 in each field.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Housing", "parent": "<the ID of Lantern>", "components": { "MeshRenderer": { "Mesh": "Builtin/Cylinder" }, "Transform": { "Translation": [0, -0.19, 0], "Scale": [0.3, 0.3, 0.3] } } } }
   ```

   :::
   ::::

   **You should see:** a short gray cylinder of 0.3 m under the bulb, resting on the first post. Its top is 0.04 m below the lamp.

   **If you do not see it:** the cylinder is a tall column when you typed one number only. Set all three fields of **Scale**.

3. Save the lantern as a prefab.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `Lantern` and choose **Create Prefab**.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.create", "parameters": { "entities": ["<the ID of Lantern>"], "path": "Prefabs/Lantern.stprefab" } }
   ```

   :::
   ::::

   **You should see:** `Prefabs/Lantern.stprefab` in the Content Browser, and the badge of an instance on `Lantern`.

   **If you do not see it:** the menu is gray while the game plays. Stop it first.

4. Place the lantern on the other posts. Drag `Prefabs/Lantern.stprefab` into the Scene view twice and set the **Translation** of the new roots to -4, 3.34, -5 and 4, 3.34, -5.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select each new `Lantern (1)` and `Lantern (2)` and type the numbers.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Lantern.stprefab", "components": { "Transform": { "Translation": [-4, 3.34, -5] } } } }
   ```

   Send it again with `4, 3.34, -5`.
   :::
   ::::

   **You should see:** two more lamps on the back posts, each with its own pool.

   **If you do not see it:** a lantern floats or sinks when its **Translation** is wrong. The post tops stand at 3 m.

5. Put the fourth lantern on the arm. Drag a third instance onto `Arm` in the Hierarchy and set its **Translation** to 1.2, 0.38, 0.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag `Prefabs/Lantern.stprefab` into the Scene view. Drag the new `Lantern (3)` onto `Arm`. Type the numbers.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Lantern.stprefab", "parent": "<the ID of Arm>", "components": { "Transform": { "Translation": [1.2, 0.38, 0] } } } }
   ```

   Under `Arm` it is named `Lantern`, as the first. Rename it:

   ```json
   { "command": "entity.rename", "parameters": { "entity": "<the ID of the new instance>", "name": "Lantern (3)" } }
   ```

   :::
   ::::

   **You should see:** a lamp at the end of the bar on the second front post, 1.2 m from the post.

   **If you do not see it:** the lantern is far off when it keeps its :term[world position]{id=world-position}. A child's **Translation** counts from `Arm`.

:::::

::checkpoint{stage=4}

::figure{id=four-lanterns}

## Give the lanterns shadows

Lamps cast no shadows until you ask. A lamp draws its shadow into a shadow map, a picture of the depth of everything near it, seen from the lamp. A point light shines in every direction, so it draws six pictures, one for each face of a cube. A spot light draws one.

Strata gives shadows to a limited number of lamps in view at once, and the Graphics Quality preset sets the number. The lowest preset allows four, so your four lanterns always fit. The lamps around the camera come first, then those whose range looks largest on screen, the brighter before the dim. A lamp that loses its shadow fades it out over a fifth of a second and keeps shining. [Graphics quality](quality.md) teaches the presets.

A shadow costs drawing. A still lamp over a still room keeps its views and draws nothing after the first frame. A lamp that moves, or a lamp with something moving inside its range, draws its views again every frame: six for a point light, one for a spot light.

```mermaid caption="How a lamp gets its shadow: the preset chooses the lamps, and movement decides whether their views are drawn again." alt="A flow chart. A lamp in view with shadows on meets the limit of the preset: with no room, it lights the scene without a shadow. With room, it keeps its old views when nothing moved and draws them again when it or something in its range moved."
flowchart TD
	A["Lamp in view, Cast Shadows on"] --> B{"Room for it in the preset?"}
	B -- no --> C["Lights the scene, no shadow"]
	B -- yes --> D{"Did the lamp or something in its range move?"}
	D -- no --> E["Keeps its old views: nothing drawn"]
	D -- yes --> F["Draws its views again: 6 for a point light, 1 for a spot light"]
```

Two fields shape a shadow's edge. **Shadow Filter Radius** softens it: 0 is sharp and 8 is the softest. Both biases move the lookup so that a surface does not shadow itself.

**Shadow Bias** pushes the lookup toward the lamp: raise it when lit surfaces show dark stripes, called `acne`. **Shadow Normal Bias** pushes it along the surface's normal, the direction straight out of the surface: raise it against acne on surfaces that the light meets at a grazing angle. Too much of either detaches a shadow from its object and opens a gap of light at its foot. All three count in texels, the pixels of the lamp's shadow map, and you leave the biases alone until you see one of the two faults.

:::::steps

1. Turn shadows on for the lantern's light.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Expand `Lantern` and select `Light`. Check **Cast Shadows** in its **Point Light**. Open the `Overrides` menu of the prefab bar and choose **Apply All to Prefab**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Light>", "component": "PointLight", "values": { "CastShadows": true } } }
   { "command": "prefab.apply", "parameters": { "entity": "<the ID of Lantern>" } }
   ```

   A `box` around the first lantern makes `entity.find` return only its `Lantern`, `Light` or `Housing`:

   ```json
   { "command": "entity.find", "parameters": { "name": "Light", "box": { "min": [-4.2, 3, 0.8], "max": [-3.8, 3.5, 1.2] } } }
   ```

   :::
   ::::

   **You should see:** the yard around the lanterns turns almost dark, though the lamps are on and the bulbs glow. The sign's pool stays.

   **If you do not see it:** the other three lanterns stay lit when the apply did not run. Check that the `Overrides` chip reads 0.

2. Find the cause. The light is 0.04 m above the housing. The housing is a solid mesh, and meshes cast shadows by default. Every ray that goes down from the lamp meets the housing, so the lamp shadows itself. Turn **Cast Shadows** off on the housing.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Housing`. Clear **Cast Shadows** in its **Mesh Renderer**. Choose **Apply All to Prefab** again.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Housing>", "component": "MeshRenderer", "values": { "CastShadows": false } } }
   { "command": "prefab.apply", "parameters": { "entity": "<the ID of Lantern>" } }
   ```

   :::
   ::::

   **You should see:** the pools return, and the hut, the sign and the posts throw shadows away from each lantern.

   **If you do not see it:** the yard is still dark when the apply missed `Housing`. Select it in the first lantern and search for the override mark.

3. Compare the filter. Set **Shadow Filter Radius** of the first `Light` to 0, look at the edge of the hut's shadow, then set 8.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `0`, look, type `8`, look, and type `1.5` to return.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Light>", "component": "PointLight", "values": { "ShadowFilterRadius": 8 } } }
   ```

   :::
   ::::

   **You should see:** a sharp edge at 0 and a wide, soft one at 8. The default of 1.5 is in between.

   **If you do not see it:** the field is gray when **Cast Shadows** is off. Enable it.

4. Count the shadowed lamps. Click **Stats** in the top bar of the viewport.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **Stats**. Find the line that starts with the count of shadowed lights. Near its end it reads `views drawn`.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "stats": true } }
   { "command": "viewport.capture", "parameters": {} }
   ```

   The capture's `renderStats` holds the line's numbers: `localShadowLights`, `localShadowViewsDrawn` and `localShadowViewsPending`.
   :::
   ::::

   **You should see:** a line that starts `4 of 4 shadowed lights` and ends with the number of views drawn this frame and the number still waiting. The number is 0 once the lanterns' shadows are drawn and nothing moves.

   **If you do not see it:** the chip belongs to the view you look at. The Game view has its own.

:::::

::checkpoint{stage=5}

::figure{id=lantern-shadows}

## Size the bulb for its glint

A shiny surface mirrors a lamp as a bright glint, which the surface's roughness spreads; on a mirror the glint has the size of the lamp. A **Source Radius** of 0, the default, makes the lamp a point. The field is the radius of the bulb or flame in metres. It widens the glint on shiny and wet ground, and only the glint: it does not soften the shadow, which the filter radius does, and it spreads no light.

Give the lamp its real size: a lantern bulb has a radius of 0.03 to 0.06 m, a fire pit's flames about 0.2 to 0.3. A larger value does not make the light softer. It makes the glint wrong.

:::::steps

1. Make the ground wet. Select `Materials/Ground.stmat` and set **Roughness** to 0.1.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the material in the Content Browser, then type `0.1` into **Roughness** of the Asset tab.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/Ground.stmat", "properties": { "Roughness": 0.1 } } }
   ```

   :::
   ::::

   **You should see:** the ground mirrors the lamps and the bulbs as glints.

   **If you do not see it:** the ground is still dull when the value stays at 0.9. Press **Enter**.

2. Set **Source Radius** of the first `Light` to 0.04 and search for its glint. Then set 0 and 0.3.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `0.04` into **Source Radius**. Turn the view until the lamp's reflection lies on the ground in front of you, then type `0`, look, and `0.3`, look.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Light>", "component": "PointLight", "values": { "SourceRadius": 0.04 } } }
   ```

   :::
   ::::

   **You should see:** at 0 and 0.04 the same soft glint, which the roughness spreads to about half a metre, and at 0.3 a wider patch. The pool and the shadows look the same in all three.

   **If you do not see it:** the glint lies where the ground mirrors the lamp to your eye, the mirror image of the lamp below the ground. Move the view until you find it.

3. Keep 0.04 for the real bulb and apply it to the prefab.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `0.04` into **Source Radius**, then choose **Apply All to Prefab**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Light>", "component": "PointLight", "values": { "SourceRadius": 0.04 } } }
   { "command": "prefab.apply", "parameters": { "entity": "<the ID of Lantern>" } }
   ```

   :::
   ::::

   **You should see:** all four lanterns with the same small glint.

   **If you do not see it:** a lantern that keeps another value shows an override. Apply again.

:::::

::checkpoint{stage=6}

::figure{id=wet-glint}

## Move a lamp and switch it

A script reaches the light by name, as it reaches any component. `SetProperty("PointLight", "Intensity", 64.0f)` writes the candela of a point light, as [Scripting the scene](scripting-scene.md) taught. You use it for a switch. The arm turns with the `Spinner` script that the template wrote, and a new :term[input action]{id=input-action}, `Lamp`, tells the switch when to flip.

:::question
What are inheritance, `virtual` and `override`? See [C++ classes](../basics/cpp-classes.md).
:::

The script flips a flag when the action is pressed and writes the lamp's candela.

```cpp src="book:tutorials/make/lamps/LanternSwitch.cpp#L5-L28"
class LanternSwitch : public Script
{
public:
	Entity Lamp;
	float OnCandela = 64.0f;

	void OnUpdate([[maybe_unused]] float deltaTime) override
	{
		if (!Lamp.IsValid() || !Input::IsActionPressed("Gameplay/Lamp"))
			return;

		m_On = !m_On;
		Lamp.SetProperty("PointLight", "Intensity", m_On ? OnCandela : 0.0f);
	}

private:
	bool m_On = true;
};

ST_SCRIPT_CLASS(LanternSwitch)
{
	ST_SCRIPT_FIELD(Lamp);
	ST_SCRIPT_FIELD(OnCandela);
}
```

1. **Line 8:** `Lamp` is an entity field: you pick the light to switch in the Inspector.
2. **Line 13:** the script does nothing when no lamp is picked or when the action was not pressed in this frame.
3. **Lines 16–17:** the flag flips, and `SetProperty` writes the candela of the `PointLight` by name: 64 or 0.
4. **Line 21:** `m_On` is a plain member, not a field, so a rebuild during play sets it to on again.
5. **Lines 26–27:** the registration lists the two fields.

:::::steps

1. Make the action `Lamp` in the map `Gameplay`, bound to the L key.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Project Settings...** and **Input Actions**. Press **Add Map**, name it `Gameplay`, press **Add Action**, name it `Lamp` with kind `Button`, and bind **L**.
   :::
   :::tab[With a command]

   ```json
   [
     { "command": "inputActions.setMap", "parameters": { "map": "Gameplay" } },
     { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Lamp", "kind": "Button", "bindings": [ "Key/L" ] } }
   ]
   ```

   :::
   ::::

   **You should see:** the action `Lamp` in `Gameplay` with one binding, `Key/L`.

   **If you do not see it:** the key did not bind. [Input](input.md) shows how the page listens for a key.

2. Make the script `LanternSwitch`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **Scripts ▸ New Script...**, type `LanternSwitch` and click **Create**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "LanternSwitch" } }
   ```

   :::
   ::::

   **You should see:** `Scripts/LanternSwitch.cpp` and the status bar's "Building". Keep its comment lines, the `#include` and the `using` line, and replace the rest, from `class LanternSwitch`, with the code above.

   **If you do not see it:** the dialog refuses a name that is not a valid C++ name.

3. Build, then attach `Spinner` and `LanternSwitch` to `Arm`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+B**. Select `Arm`. Choose **Add Component ▸ Script** and pick `Spinner`, then again for `LanternSwitch`. Set `Degrees Per Second` of `Spinner` to 40. Expand `Arm ▸ Lantern (3)` and drag `Light` onto the field `Lamp`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<the ID of Arm>", "class": "Spinner", "fields": { "DegreesPerSecond": 40 } } }
   { "command": "script.add", "parameters": { "entity": "<the ID of Arm>", "class": "LanternSwitch" } }
   { "command": "entity.find", "parameters": { "name": "Light", "box": { "min": [5.1, 3.3, 0.9], "max": [5.3, 3.5, 1.1] } } }
   { "command": "script.setField", "parameters": { "entity": "<the ID of Arm>", "class": "LanternSwitch", "field": "Lamp", "value": "<the ID it returned>" } }
   ```

   :::
   ::::

   **You should see:** two Script components on `Arm`, and the field `Lamp` showing `Light`.

   **If you do not see it:** the list holds only built classes. Build again.

4. Play with the **Stats** chip of the Game view on.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**. Click **Stats** in the Game view's top bar. Watch the last words of the shadow line.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   { "command": "viewport.capture", "parameters": { "camera": "scene" } }
   ```

   Read `localShadowViewsDrawn` in the capture's `renderStats`, as in the shadow section.
   :::
   ::::

   **You should see:** the arm turns once every nine seconds, the lantern's shadows swing, and the number of views drawn is six or more in every frame.

   **If you do not see it:** the count is 0 when the arm does not turn. Check that `Spinner` is on `Arm` and its speed is not 0.

5. Make the lamp still, then switch it. While playing, set `Degrees Per Second` to 0, then press **L** twice.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `0` into the field of the running copy. Press **L** and press it again.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setField", "parameters": { "entity": "<the ID of Arm>", "class": "Spinner", "field": "DegreesPerSecond", "value": 0 } }
   { "command": "input.key", "parameters": { "key": "L" } }
   { "command": "input.key", "parameters": { "key": "L" } }
   ```

   :::
   ::::

   **You should see:** with the arm still, the views drawn fall to 0, as the lantern's shadows are kept. **L** turns the lamp off and then on again.

   **If you do not see it:** the key does nothing when the viewport has no focus in the editor. Click the Game view first.

:::::

The switch reads the action `Lamp`, and a player could rebind it as [Input](input.md) explains. The edit of step 5 changed the running copy only: stop the game and the arm turns again.

::checkpoint{stage=7}

::figure{id=moving-lamp}

## Light the hut with a rectangle

A point light is a dot, and a ceiling panel is not. A **Rect Light** is a glowing rectangle that shines along its forward direction and lights every pixel with its true shape: wide soft light below it, a rectangle mirrored on wet ground. You give it a luminance in nits, the unit of an emissive material, or with **Units** set to **Lumens** a power. A new one has 25 nits, 1 by 0.5 m, and one side.

The two units tell the same story. A face of area $A$ square metres that emits $P$ lumens shines with $P / (\pi A)$ nits. For the 800 lumens of your bulb on a panel of 0.8 by 0.4 m, $A = 0.32$ and the face shines with $800 / (3.14 \times 0.32) = 796$ nits. A panel sends its light into one half of space, brightest straight down, where its candela is its nits times its area: $796 \times 0.32 = 255$ cd, four times the bulb's 64 cd. At 2.5 m below it the floor gets $255 / 2.5^2 = 41$ lux, against the bulb's 10 lux.

The panel's shadows are soft: sharp where an object meets the floor and wider farther away. A shadowed rect light draws six shadow pictures, as a point light does, or five when it shines one way, and four rect lights at most cast shadows at once. A scene with any rect light draws every surface with costlier shaders, so keep rect lights for places where they matter.

A mesh with an emissive material shows a glow but lights nothing. **Make Area Light** closes the gap. It gives the panel a child rect light that has the panel's size and brightness. It also tags the panel **Light Surface**, so that reflections and the light's own shadows leave the glow out.

:::::steps

1. Make the panel in the roof: a thin cube with an emissive material of 796 nits.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create a material `Materials/Panel.stmat` with **Emissive Color** 1, 0.95, 0.85 and **Emissive Intensity** `796`. Click **+ ▸ Mesh only ▸ Cube**, rename it `Ceiling Panel`, set **Translation** to 0, 2.48, -3.5 and **Scale** to 0.8, 0.04, 0.4, and drop the material on it.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Ceiling Panel", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube", "Material": "Materials/Panel.stmat" }, "Transform": { "Translation": [0, 2.48, -3.5], "Scale": [0.8, 0.04, 0.4] } } } }
   ```

   Make and set the material first, as for the bulb.
   :::
   ::::

   **You should see:** a glowing strip under the roof, seen through the gap in the front wall. The floor inside stays dark, as the glow lights nothing.

   **If you do not see it:** the panel is gray when its material is not set.

2. Make it a light. Right-click `Ceiling Panel` and choose **Make Area Light**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click the entity in the Hierarchy and choose **Make Area Light**.
   :::
   :::tab[With a command]

   ```json
   { "command": "lighting.makeAreaLight", "parameters": { "entity": "<the ID of Ceiling Panel>" } }
   ```

   :::
   ::::

   **You should see:** a child `Ceiling Panel Light` with a **Rect Light** of 796 nits, 0.8 by 0.4 m, and a lit floor patch under the panel. At your exposure of +1 the patch is white, because the room is far brighter than the moon.

   **If you do not see it:** the command fails on a mesh with a black emission. Check the material.

3. Give the exposure back to automatic. Select `Post Process`, check **Auto Exposure** and set **Exposure** to 0.25.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Check **Auto Exposure** and type `0.25` into **Exposure**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AutoExposure": true, "Exposure": 0.25 } } }
   ```

   :::
   ::::

   **You should see:** the picture settles within a second or two. Automatic exposure meters the whole picture, so the yard looks brighter than at +1: it aims at middle gray and does not know it is night.

   **If you do not see it:** the picture is far too bright or dark when **Exposure** keeps your old value. With automatic exposure it is a correction in stops, and the template used 0.25.

4. Keep the night dark. Raise **Auto Exposure Min EV** until the yard darkens again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Raise **Auto Exposure Min EV** of `Post Process` from -4 toward 0 in steps of 1 and look.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AutoExposureMinEV": 0 } } }
   ```

   :::
   ::::

   **You should see:** each stop above the scene's own brightness darkens it by one stop, as the lighting chapter taught.

   **If you do not see it:** the picture does not change when the limit is below the scene's brightness. Raise it more.

:::::

A script reaches a rect light like any component: `SetProperty("RectLight", "Intensity", 400.0f)`. The software development kit (:term[SDK]{id=sdk}) has no class of its own for it.

### What Strata does not do here

Strata has no light cookies, no profile files of the Illuminating Engineering Society (IES), no light linking and no lighting channels. Every light lights every surface within its range: you cannot make a lamp skip one object. What a lamp has instead is a spot light's cone, its **Range** and **Cast Shadows** on the meshes that should block it.

::checkpoint{stage=8}

::figure{id=result}

## Summary

- A lamp of $P$ lumens gives about $P / 12.57$ cd as a point light, and a surface at $d$ metres gets $I / d^2$ lux, ended smoothly at the range.
- The range ends the light and bounds its cost, and does not set its brightness. A spot light's candela is along its axis, so a narrower cone is not brighter. The source radius widens only the glint.
- A lantern is a prefab of a housing, a bulb and a light, placed four times and changed through one apply.
- A lamp shadows itself unless the mesh around it has **Cast Shadows** off. A still lamp's shadow views are kept; a moving lamp draws six again each frame, and the **Stats** chip shows the count.
- A rect light is a glowing rectangle in nits or lumens, and **Make Area Light** turns an emissive panel into one.

## Check yourself

1. A box says 1,600 lumens and the lamp has a range of 10 m. What is its candela as a point light, and what does a surface 5 m away get?

   :::answer{tests="lamp-units"}
   The candela is $1600 / 12.57 = 127$. The plain law gives $127 / 25 = 5.1$ lux at 5 m. The window is $(1 - 0.5^4)^2 = 0.879$, so the surface gets $5.1 \times 0.879 = 4.5$ lux.
   :::

2. A spot light of 60 cd has an outer angle of 30. You set it to 15. What changes on a wall 3 m away, and what does not?

   :::answer{tests="lamp-fields"}
   The lit circle shrinks from a radius of 1.7 m to 0.8 m. The brightness on the axis stays $60 / 9 = 6.7$ lux, because the candela is along the axis.
   :::

3. A designer gives a lantern bulb a **Source Radius** of 0.5 to get softer shadows. What happens?

   :::answer{tests="lamp-fields"}
   The shadows do not change, because the radius sizes only the glint. The glint on wet ground becomes a wide patch that no bulb of a lantern would make. **Shadow Filter Radius** softens the shadow.
   :::

4. You edit the `Housing` of one lantern and the other three do not follow. Why, and what do you do?

   :::answer{tests="lantern-prefab"}
   The edit is an override on that instance, and the prefab still holds the old value. Choose **Apply All to Prefab**, or the command `prefab.apply`, and the others follow.
   :::

5. A lantern throws no light with **Cast Shadows** on and a lot with it off. Which mesh do you check, and why?

   :::answer{tests="lamp-shadows"}
   The housing or any mesh around the light. A solid mesh that casts shadows blocks the rays that leave the lamp, so the lamp lies in its own shadow. Clear **Cast Shadows** on that mesh.
   :::

6. A point light and a spot light both move. Which draws more shadow views per frame, and where do you read the count?

   :::answer{tests="lamp-cost"}
   The point light draws six and the spot light one. The viewport's **Stats** chip shows `views drawn` in its shadowed lights line.
   :::

## Exercises

1. **Basic.** A candle gives 1 cd. At 0.5 m a page gets how many lux, and how many stops separate that from the 800 lumen lamp 2 m away?

   :::answer{tests="lamp-units"}
   The candle gives $1 / 0.25 = 4$ lux. The lamp gives $64 / 4 = 16$ lux, four times more, two stops.
   :::

2. **Medium.** Light the hut inside for the night: a table with a 1 cd candle on it and a lamp of 800 lumens at the door. Fit each range to the room, set the exposure by hand and read the result in the **Luminance** debug view.

   :::answer[Worked solution]{tests="lamp-units lamp-fields" solution="tutorials/make/lamps/exercise-2.tutorial.json"}
   First clear the active box of `Ceiling Panel`: its rect light would make the hut a bright room. The candle gets a range of 1.5 m and the lamp 3 m, enough for a hut 3 m deep. The lamp gives about 18 lux on the table and the candle 11 lux 0.3 m away. The exposure for 18 lux is about $-7 + \log_2(400 / 18) = -2.5$, so you set -2. In the **Luminance** view nearly the whole hut lies in the lowest band; only the table near the candle climbs higher.
   :::

3. **Hard.** Give the panel two sides and **Units** Lumens with 800 lumens. How bright is each face, and why?

   :::answer{tests="lamp-units"}
   A two-sided light in lumens shares its power between the faces. Each face gets 400 lumens and shines with $400 / (3.14 \times 0.32) = 398$ nits, half of the one-sided face.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RendererComponents.h`: the point, spot and rect light components with their defaults.
- `Strata/src/Strata/Renderer/RendererComponents.cpp`: the Inspector's labels and hints for the lights.
- `Strata/shaders/Include/PBR.slang`: the windowed falloff and the spot cone.
- `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp`: which lamps get shadows and which views are drawn.
- `Strata/src/Strata/Renderer/RendererQuality.cpp`: the preset rows of shadowed lamps.
- `StrataEditor/src/Panels/ViewportToolbar.cpp`: the overlay of the viewport's **Stats** chip and its shadowed lights line.
- `StrataEditor/src/Editor/EditorLightingCommands.cpp`: the command `lighting.makeAreaLight`.
- `Docs/Manual/Lighting.md`: the engine's own guide to lights and shadows.

## Further reading

- Wikipedia, "Inverse-square law": why light falls with the square of the distance (beginner).
- Wikipedia, "Luminous intensity": candela, lumen and the sphere's factor of 12.57 (intermediate).
- Lagarde and de Rousiers, "Moving Frostbite to Physically Based Rendering": the windowed falloff of punctual lights (advanced).
