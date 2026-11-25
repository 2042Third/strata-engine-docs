---
id: make/lighting
title: "Lighting a scene: sun, sky and exposure"
description: "Read and set light in real units, choose a sky and its preset, set exposure on purpose and light Coin Run for play."
kind: tutorial
size: L
tracks: [G, B]
needs: [make/prefabs]
time: 90
learn:
  - id: light-units
    text: name the unit that measures a sun, a lamp and a sky, and compute the stops between two light levels
  - id: set-exposure
    text: set the exposure of a scene on purpose and predict when the picture turns white or gray
  - id: choose-sky
    text: choose a sky source and a preset and read the sun to sky ratio
  - id: turn-sun
    text: change the sun's direction and predict how long its shadows fall
  - id: preview-light
    text: compare the Scene view's preview lighting with the game of a scene that has no light
since: 0.3.0
status: final
---

## What you will make

Coin Run, the level you built in the last chapters, lit for play. It has a sun at a height you chose, a sky that matches it, an exposure you set on purpose, and coins whose shadows you can read.

The picture shows the same lighting on a plain cube and ball in place of the coins.

::figure{id=result}

## What you need

- Coin Run as the [prefabs tutorial](prefabs.md) left it: the level with five coin instances, the gold and silver materials and the lighting of the Basic 3D template. If you skipped it, download its last checkpoint.
- One image, `Samples/ThirdPerson/Assets/Environment/kloofendal_48d_partly_cloudy_puresky_1k.hdr` in the release. Poly Haven made it and shares it as Creative Commons Zero (:term[CC0]{id=cc0}), which means anyone may use it for any purpose. The `ThirdPerson` sample's `CREDITS.md` names it.
- About 90 minutes. You build nothing.

The page uses light units and powers of two. You may read [Numbers, powers and logarithms](../basics/numbers.md) first, but the tables below replace the logarithms.

## Read the light that Basic 3D gave you

Before you change a value, learn what the values mean. Each later step changes one of them, and you can then predict the result.

### Three units for light

Strata measures light in the units of the real world. A number from a lamp's box or a lighting book works in the engine as it is, with no hidden factor. Three units cover every light, and each answers a different question.

The sun lights the whole ground from one direction. The question is how much light lands on a surface that faces it. That amount is **lux** (lx). The sun on a clear day brings about 100,000 lux, and a bright office about 400. A **Directional Light** is the sun: its **Intensity** is in lux.

A lamp sends light out from one point, and what counts is how bright it looks from one direction. That brightness is **candela** (cd). A candle gives about 1 cd. A household bulb of 800 lumens, the number on its box, gives about 64 cd. Point and spot lights use candela; [the lamps chapter](lamps.md) sets them.

The sky and a glowing surface are not lit from one direction: you see them. What counts is how bright each patch looks to the eye. That brightness is **nits** (candela per square meter). A monitor shines at about 200 nits and a lit sign at about 1,000. The sky and the emission of a material, in the **Sky Light** and the material's **Emissive Intensity**, are in nits.

One scale joins all three. A sky that shines evenly at 3,000 nits puts about 3.14 times 3,000, so about 9,400, lux on flat ground. Here are real values to compare your scene against.

| Light | Value | Exposure that suits it |
| --- | --- | --- |
| Direct sunlight in the morning or at noon (clear day) | 32,000 up to 100,000 lux | between -13 and -15 |
| **Overcast** day | 1,000 up to 10,000 lux | between -12 and -8 |
| Lamps of an office | 300 up to 500 lux | -7 |
| Full moon | 0.1 up to 0.3 lux | between +3.5 and +5 |
| Household lamp of 800 lumens | 64 cd | none |
| Blue sky far from the sun | 3,000 up to 8,000 nits | -12 |
| Candle | 1 cd | none |
| Monitor | 200 nits | none |
| Lit sign | 1,000 nits | none |

The last column is the **Exposure** you meet in the next part. The three units meet at the screen as the diagram shows.

```mermaid caption="Each kind of light has its own unit. All of them reach the screen through one factor, the exposure." alt="Three boxes, the sun in lux, a lamp in candela and the sky with glowing surfaces in nits, point to one box for the light that reaches the camera. An arrow leads from it to a box for exposure and on to the screen."
flowchart LR
	S["Sun: lux"] --> L["Light that reaches the camera"]
	P["Lamp: candela"] --> L
	K["Sky and glowing surfaces: nits"] --> L
	L --> E["Exposure"] --> D["The picture on screen"]
```

### Exposure counts doublings

The sun gives about 120,000 lux and the full moon about 0.25 lux. A screen cannot show both: it spans a range of roughly one hundred to one, and these two differ by a factor of 480,000. A camera solves this with **exposure**: a factor that scales all light before the picture appears, counted in steps called stops, or exposure value (EV). One stop doubles the light, and one stop less halves it.

Counting stops is counting doublings. This table of powers of two replaces any logarithm: to find the stops between two lights, divide them and find the nearest row.

| Stops | Light multiplied by |
| --- | --- |
| 1 | 2 |
| 2 | 4 |
| 3 | 8 |
| 4 | 16 |
| 5 | 32 |
| 8 | 256 |
| 10 | 1,024 |
| 17 | 131,072 |
| 18 | 262,144 |
| 19 | 524,288 |

:::example[How many stops from the moon to the sun?]
The sun gives 120,000 lux and the full moon 0.25 lux. Divide: 120,000 divided by 0.25 is 480,000. The table has 262,144 at 18 stops and 524,288 at 19 stops, and 480,000 lies a little under the second. The sun is about 19 stops brighter than the moon.

Check with the exposure column of the table above: a sunny scene suits -14.5 and one lit by the moon suits about +4. The difference is 18.5 stops, the same answer within the rounding of the table.
:::

On the **Post Process** component, **Exposure** has the unit of stops. With **Auto Exposure** off, each +1 doubles the brightness on screen. Photographers number the same scale with the exposure value for a film speed of 100 (EV100), and the rule is that **Exposure** is about 0.5 minus EV100. A sunny day has EV100 of 15, so it suits an **Exposure** of about -14.5.

### What Basic 3D chose

The Basic 3D template does not use small test values. It uses real ones, which this page explains one by one.

- A `Sun` of 120,000 lux, the light above the air, turned 40 degrees up from the horizon. The air dims it on the way down.
- A sun 0.53 degrees across, the size the real sun has in the sky: the sun's **Angular Diameter** and the sky's **Sun Size**. A larger disk gives softer shadow edges.
- A `Sky` with the **Atmosphere** source: the physical sky of Earth, computed from the sun's direction and light. This is the **Clear** preset, which the page returns to.
- A `Post Process` with the **Filmic** tone curve, **Auto Exposure** on, and an **Exposure** of +0.25. A tone curve squeezes the wide range of light into the range a screen shows. [The image chapters](../image/tone-mapping.md) explain the Filmic curve.

The +0.25 is a quarter of a stop, a correction for this scene. Automatic exposure measures the picture, its center most, and aims at middle gray, the gray halfway between black and white to the eye. The bright sky over the dark stone ground leaves the ground a little under that gray, and the quarter stop lifts it.

:::why
Strata uses real values because they make the lights agree with each other. A 120,000 lux sun, a sky computed from it and a lamp of 64 cd all sit on one scale, so a value from a reference book works. The cost is large numbers. A real sun needs automatic exposure with the right limits, or the picture turns white, which you will see in the next part. The engine's test of the template also checks that the sun gives at least five times the light on the ground that the sky gives, so the shadows read.
:::

:::::steps

1. Open Coin Run and read the sun. Select `Sun` in the Hierarchy and look at its **Directional Light** in the Inspector.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the scene with **File ▸ Open Scene...** if it is not open. Click `Sun` in the Hierarchy. Hold the pointer over **Intensity**: the hint text names the unit.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.get", "parameters": { "entity": "<the ID of Sun>", "component": "DirectionalLight" } }
   ```

   A command takes an entity's identifier (ID), not its name: use the ID that `entity.find` returns for the name `Sun`, as on [Scenes and entities](scenes-entities.md), and so for `Post Process` and `Sky`.
   :::
   ::::

   **You should see:** **Intensity** 120000, **Angular Diameter** 0.53 and **Cast Shadows** on. The hint text says that the value is the light that lands on a surface, in lux.

   **If you do not see it:** another entity is selected. Click `Sun` in the Hierarchy again.

2. Read the exposure. Select `Post Process`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click `Post Process` in the Hierarchy. Find the Exposure part of its Inspector.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.get", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess" } }
   ```

   :::
   ::::

   **You should see:** **Auto Exposure** on, **Exposure** 0.25, **Auto Exposure Min EV** -4 and **Auto Exposure Max EV** 16.

   **If you do not see it:** you changed the values in an earlier chapter. Type the four values in.

3. Read the sky. Select nothing: click the empty area of the Hierarchy.

   ::::tabs{sync=how}
   :::tab[In the editor]
   With nothing selected, the Inspector shows the scene's settings. Open its **Sky** section.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.get", "parameters": { "entity": "<the ID of Sky>", "component": "SkyLight" } }
   ```

   :::
   ::::

   **You should see:** the closed **Sky** section's row names its source, **Atmosphere**. Opened, it shows **Source** and, after **Presets**, a row of preset buttons.

   **If you do not see it:** the Inspector still shows an entity. Click an empty place in the Hierarchy.

:::::

::checkpoint{stage=1}

::figure{id=inspector-template}

## Change the sun and break the exposure

Automatic exposure is the reason a scene of real light works. Three small experiments show what it does and where it stops.

Take the sun from 120,000 lux to 60,000 lux, one stop less. The sky is computed from the sun, so it loses a stop too, and everything on screen is half as bright. Automatic exposure adds the stop back, so the picture should look almost the same.

The second experiment turns automatic exposure off. **Exposure** is then the only factor, and at 0 the ground in the sun, thousands of nits, turns white. A real sunny day needs about -14.5, and you set -15.

The third shows where automatic exposure fails. It sees only an average and moves the picture toward middle gray, so a night scene, left alone, shows the same gray as a day. **Auto Exposure Min EV** limits how dark an average the exposure may chase: a scene darker than that stays dark.

:::::steps

1. Halve the sun. Select `Sun` and set **Intensity** to 60000.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the **Intensity** field of the **Directional Light**, type `60000` and press **Enter**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sun>", "component": "DirectionalLight", "values": { "Intensity": 60000 } } }
   ```

   :::
   ::::

   **You should see:** the picture dims for a moment and then returns to nearly the same look. The exposure takes about a second to adapt.

   **If you do not see it:** the picture stays dark. Check that **Auto Exposure** of the `Post Process` is on.

   Set **Intensity** back to `120000` before the next step.

2. Turn automatic exposure off and set the exposure by hand. Select `Post Process`, and clear **Auto Exposure**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Clear **Auto Exposure**. Type `0` in **Exposure**. Look at the Scene view. Then type `-15`. At the end set **Auto Exposure** on again and **Exposure** to `0.25`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AutoExposure": false, "Exposure": 0 } } }
   ```

   Then the same command with `-15`, and last `{ "AutoExposure": true, "Exposure": 0.25 }`.
   :::
   ::::

   **You should see:** at 0 the picture is almost all white. At -15 it is close to what automatic exposure chose, a little darker or lighter. The exposure fields of automatic exposure fade while it is off.

   **If you do not see it:** the picture at -15 is still white or far too dark. Check that the sun's **Intensity** is back at 120000, the value the -15 suits.

3. Make a dark scene gray. Set the sun's **Intensity** to 120: ten stops less, because 1,024 times less light is ten doublings and 120 is about 120,000 divided by 1,000.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Sun` and set **Intensity** to `120`. Wait two seconds. Then select `Post Process` and raise **Auto Exposure Min EV** to `8`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sun>", "component": "DirectionalLight", "values": { "Intensity": 120 } } }
   ```

   Then set `{ "AutoExposureMinEV": 8 }` on the `PostProcess` of `Post Process`.
   :::
   ::::

   **You should see:** at 120 lux the scene has lost ten stops, but the exposure adds them back, and the picture looks almost like the day again. The sky is computed from the sun, so it lost ten stops too. The scene now averages about 5 stops of nits, 15 less 10. With **Auto Exposure Min EV** 8 the exposure stops three stops short, and the picture darkens to a dusk.

   **If you do not see it:** the picture is still bright. Raise **Auto Exposure Min EV** by 1 and look again. Each stop above the scene's own brightness darkens it by one stop.

4. Restore the values and meet the other limit. Set the sun back to 120000 and **Auto Exposure Min EV** to -4. Then set **Auto Exposure Max EV** to 8.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type the values into **Intensity** of `Sun`, then into the two fields of `Post Process`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sun>", "component": "DirectionalLight", "values": { "Intensity": 120000 } } }
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AutoExposureMinEV": -4, "AutoExposureMaxEV": 8 } } }
   ```

   :::
   ::::

   **You should see:** the picture turns pale and washed toward white. The ceiling of 8 stops stops the exposure from dimming enough for a real sun.

   **If you do not see it:** nothing changes. Check that **Auto Exposure** is on, because the limits fade while it is off.

   Set **Auto Exposure Max EV** back to `16`.

:::::

Why 16? The exposure clamps the picture's average, in nits, between two to the power of each limit. A scene in the sun averages about 15 stops, so a limit of 12 (the old default) cuts it off, and 16 leaves room.

::checkpoint{stage=2}

::figure{id=exposure-sweep variant=auto}

## Choose the sky

The sky does two jobs: it is the background, and it lights the scene from every direction. The **Sky Light** has three sources, and you choose one in **Source**.

- **Procedural**: a gradient from the **Zenith Color** overhead through the **Horizon Color** to the **Ground Color**, all in nits. The sun's disk sits in the direction of the directional light.
- **Environment Map**: a photograph in high dynamic range (HDR), which holds values far above the white of a screen. **Rotation** turns it. A map taken in sunshine holds the sun too.
- **Atmosphere**: the physical sky of Earth, computed from the directional light. It is blue overhead, pale at the horizon, and orange when the sun is low.

The map has a trap. The sky lights the scene but casts no shadows, and the sun in the map lights the scene as part of the sky. If you also keep a directional light for the shadows, the sun is counted twice. **Extract Sun** makes the scene's directional light the map's sun, with its direction, color and brightness. The map's **Remove Sun** import setting then paints the sun out of the sky so that only the light remains once.

:::::steps

1. Try the procedural sky. Select nothing, and in the **Sky** section of the Inspector choose **Procedural** as the source.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Change **Source** of the sky properties to **Procedural**. Look at the Scene view.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sky>", "component": "SkyLight", "values": { "Source": "Procedural" } } }
   ```

   :::
   ::::

   **You should see:** a smooth gradient sky with the **Zenith Color** at the top and the **Horizon Color** low down. The colors, written in nits, are in the Inspector.

   **If you do not see it:** the source did not change. Make sure the **Sky** section belongs to the scene with nothing selected.

2. Import the HDR map and use it. Copy the image from the release into the project.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag `kloofendal_48d_partly_cloudy_puresky_1k.hdr` from the folder `Samples/ThirdPerson/Assets/Environment/` of the release into the Content Browser. Wait for the import. Then set **Source** to **Environment Map** and drop the map on the **Environment Map** field.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "file": "<release folder>/Samples/ThirdPerson/Assets/Environment/kloofendal_48d_partly_cloudy_puresky_1k.hdr", "directory": "Environment" } }
   ```

   Then set `Source` to `EnvironmentMap` and `EnvironmentMap` to the imported path on the `SkyLight` of `Sky`.
   :::
   ::::

   **You should see:** a photographed sky with partly cloudy air around the scene. The ground still carries the sun's shadows, which come from the `Sun`, not from the sky.

   **If you do not see it:** the sky stays black. The import has not finished: wait for the Content Browser to show the image.

3. Press **Extract Sun**. It appears under the sky's properties once a map is set.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **Extract Sun** in the **Sky** section.
   :::
   :::tab[With a command]

   ```json
   { "command": "lighting.extractSun" }
   ```

   Then `asset.setImportSettings` with `{ "RemoveSun": true }` on the map.
   :::
   ::::

   **You should see:** the `Sun` turns to point away from the sun in the picture, and its **Intensity** and color change to the values measured from the map. With this map that is about 4.4 lux: the file stores light on a scale of its own, and automatic exposure brightens the picture to match. The editor says so if the map's sun was clipped: its light is then at least that bright.

   **If you do not see it:** **Extract Sun** is disabled while the game plays. Stop the game first.

4. Return to the atmosphere. Open the preset buttons, and press **Clear**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Clear** in the row of presets of the **Sky** section.
   :::
   :::tab[With a command]

   ```json
   { "command": "lighting.applySkyPreset", "parameters": { "preset": "Clear" } }
   ```

   :::
   ::::

   **You should see:** the blue atmosphere returns, and the `Sun` has 120000 lux again. The sun still comes from the direction of the map's sun: a preset keeps its turn around the vertical axis.

   **If you do not see it:** the sun's color stays tinted. A preset writes the color too: press **Clear** once more.

:::::

### The four presets

The **Sky** section has four buttons. Each writes a whole outdoor look, a sky and a sun with real values, as one undo step. The buttons keep the direction the sun comes from around the vertical axis and set its height.

- **Clear**: the **Atmosphere** source with a 120,000 lux sun at 40 degrees. Sunny, with deep blue shadows.
- **Hazy**: more haze in thicker air, and the sun at 35 degrees. The sky is paler and the contrast softer.
- **Overcast**: an even gray procedural sky that puts about 7,700 lux on the ground, with a faint, very soft sun at 60 degrees.
- **Golden Hour**: the sun low, at 6 degrees. The light is warm and the shadows long.

A real sun turns the picture white under a manual exposure. A preset therefore turns **Auto Exposure** on, with an **Exposure** of 0, when it was off, and raises **Auto Exposure Max EV** to 16 when it was below 15. A scene that already has automatic exposure with a limit of 16 keeps its +0.25. Undo brings every old value back.

How sunny a scene looks depends most on the **sun to sky ratio**: the light that flat ground gets from the sun divided by the light it gets from the sky. This table gives the numbers.

| Kind of day | Sun to sky ratio |
| --- | --- |
| Clear midday | 6 to 10 |
| **Hazy** day | 3 to 5 |
| Low evening sun | about 1 to 2 |
| **Overcast** sky | below 0.3 |

A ratio under 3 makes a sunny scene look flat and gray, and one far over 10 turns the shadows black. The **Overcast** preset shows the low end: a sun of 1,500 lux at 60 degrees is about 1,300 lux on flat ground (1,500 times 0.87), against 7,700 lux from the sky, a ratio near 0.17.

:::simplified
Strata has no clouds, stars or moon. The atmosphere's haze is the clear haze of the air, so the **Overcast** preset is a nearly uniform procedural sky and not a computed cloud layer. The [sky chapter](../light/sky.md) explains what the sky computes.
:::

:::::steps

1. Apply each preset and read its ratio. Press **Hazy**, **Overcast**, **Golden Hour** and **Clear** in turn.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press each button. After each one, open the debug view chip at the top of the Scene view, choose **Lighting** and read the note under its legend: "Sun : sky" and a number. Choose **Lit (no debug view)** at the end.
   :::
   :::tab[With a command]

   ```json
   { "command": "lighting.applySkyPreset", "parameters": { "preset": "Hazy" } }
   { "command": "lighting.applySkyPreset", "parameters": { "preset": "Overcast" } }
   { "command": "lighting.applySkyPreset", "parameters": { "preset": "GoldenHour" } }
   { "command": "lighting.applySkyPreset", "parameters": { "preset": "Clear" } }
   ```

   The command writes **Golden Hour** as `GoldenHour`. Each result lists `groundIlluminance`, the sun's lux on a surface facing it: about 97,900 for **Clear**, 88,900 for **Hazy**, 40,900 for **Golden Hour** and 1,500 for **Overcast**. No command answers the sky's light: read the ratio in the Scene view's legend.
   :::
   ::::

   **You should see:** the ratios of the table: 6 to 10 for **Clear**, 3 to 5 for **Hazy**, 1 to 2 for **Golden Hour** and below 0.3 for **Overcast**. The **Golden Hour** picture is warm, with long shadows. The **Overcast** picture has almost no shadows.

   **If you do not see it:** the note says "Sun : sky -". The ratio needs a sun and a sky: check that both entities are active.

:::::

::figure{id=sky-presets variant=clear}

::figure{id=sky-presets variant=hazy}

::figure{id=sky-presets variant=overcast}

::figure{id=sky-presets variant=golden-hour}

::checkpoint{stage=3}

::figure{id=sky-inspector}

## Turn the sun and set its shadows

The sun's height decides how long its shadows are. A pole of height $h$ casts a shadow of $h$ divided by $\tan$ of the elevation, where $\tan$ is the tangent of the angle. The table gives the shadow of a coin 0.5 m high.

| Elevation | Tangent | Shadow of a 0.5 m coin |
| --- | --- | --- |
| 55 degrees | 1.43 | 0.35 m |
| 40 degrees | 0.84 | 0.60 m |
| 35 degrees | 0.70 | 0.71 m |
| 25 degrees | 0.47 | 1.07 m |
| 6 degrees | 0.105 | 4.8 m |

The sun shines along the forward axis of its entity, so turning the entity turns the light. The **Rotate** :term[gizmo]{id=gizmo-start}, which you used in [the transforms chapter](transforms-units.md), turns it with the rings in the Scene view.

The sun has four controls that matter for a maker.

- **Cast Shadows**: whether the sun makes shadows.
- **Shadow Distance**: how many meters from the camera the shadows reach. The same shadow detail spreads over less ground when this is smaller, so a short distance gives sharper shadows near you. Coin Run is about 20 m long, so 30 m is enough.
- **Angular Diameter** (stored as `ShadowSoftness`): the size of the sun's disk in degrees. A larger disk gives softer shadow edges that widen with the distance from the object. 0 is a hard edge.
- **Cascade Blend**: the sun's shadows come from several maps, finer near the camera. This setting hides the seams between them. The default is 0.1, and 0 switches at once.

The engine draws the sun's shadow in cascades, which [the shadow chapters](../light/sun-shadows-1.md) explain. Point and spot light shadows are for [the lamps chapter](lamps.md). Only the brightest directional light shines, so one sun is enough.

:::::steps

1. Turn the sun with the Rotate gizmo. Select `Sun`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click `Sun` in the Hierarchy and press **E** with the pointer over the Scene view. Drag the rings of the gizmo, one at a time, until the sun is about 25 degrees above the horizon. Watch the shadows of the coins and the ball.
   :::
   :::tab[With a command]

   ```json
   { "command": "lighting.applySkyPreset", "parameters": { "preset": "Clear", "sunElevation": 25, "sunAzimuth": 20 } }
   ```

   :::
   ::::

   **You should see:** the shadows turn and stretch as you drag. At 25 degrees a coin of 0.5 m casts a shadow about 1.1 m long, as the table says.

   **If you do not see it:** the shadows do not move. Check that **Cast Shadows** is on and the `Sun` is the selected entity.

2. Set the shadow controls for a level of 20 m. Select `Sun` and change **Shadow Distance** to 30, then compare two sizes of the disk.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `30` in **Shadow Distance**. Set **Angular Diameter** to `2`, look at a shadow edge, and set it back to `0.53`. Set **Cascade Blend** to `0`, search for a line across the ground, and set it back to `0.1`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sun>", "component": "DirectionalLight", "values": { "ShadowDistance": 30, "ShadowSoftness": 2 } } }
   ```

   Then the same command with `ShadowSoftness` 0.53 and `CascadeBlend` 0.1.
   :::
   ::::

   **You should see:** at 2 degrees the shadow edges are wide and soft; at 0.53 they are crisp near the object and soft only far from it.

   **If you do not see it:** the edges look alike. Look at a shadow of a tall object: the softness grows with the distance from the object.

:::::

::checkpoint{stage=4}

::figure{id=shadow-low-sun}

## Tell preview lighting from real light

A new scene has no light, so the editor lights it for you, and its shapes read in the Scene view. This help is **preview lighting**: a preview sun, 55 degrees up, and the default sky, shown only in the editor's views and never part of the scene or the game.

The game gets none of it. Without a light of its own, a scene in the game has only a faint constant light: dim gray shapes on black. The Game view shows the scene as the game will, so it stays dark.

The rule has an edge. Any light turns preview lighting off: a directional, point or spot light or a sky. A scene lit by one lamp shows as the game will.

:::::steps

1. Save Coin Run and make a new scene. Choose **File ▸ New Scene**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S** to save. Choose **File ▸ New Scene**. If the editor asks about changes you did not save, save them first: the new scene replaces Coin Run in the editor.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   ```

   Then `scene.new` with the name `Dark`.
   :::
   ::::

   **You should see:** an empty Hierarchy, and the Game view with a notice that the scene has no camera.

   **If you do not see it:** the editor refuses to continue. It waits for a save: finish saving, then choose **File ▸ New Scene** again.

2. Add a cube and a camera. Use the plus button of the Hierarchy.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+ ▸ Cube**, then **+ ▸ Camera**. A new camera is the primary one.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Cube", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" } } } }
   ```

   Then `entity.create` with a `Camera` component and a translation of `[0, 1, 5]`.
   :::
   ::::

   **You should see:** the cube lit in the Scene view, with a light side and a shade side, though the scene has no light. The Game view is dark: a dim gray cube on black.

   **If you do not see it:** the Game view still shows the camera notice. Select the camera and check that **Primary** is on.

3. Switch the preview off and add a real light. Use the **Preview lighting** chip of the Scene view.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press the **Preview lighting** chip: the Scene view turns dark too. Press it again. Then choose **+ ▸ Directional Light**.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "previewLighting": false } }
   ```

   Then the same command with `true`, and `entity.create` with a `DirectionalLight` component.
   :::
   ::::

   **You should see:** with the chip off, the cube in the Scene view is as dark as in the Game view. After you add the light the cube is lit in both views, and the chip no longer matters.

   **If you do not see it:** the Game view stays dark. The new light needs a rotation that points at the cube: select it and turn it with the Rotate gizmo.

4. Return to Coin Run. Discard the experiment.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Open Scene...**, pick Coin Run, and discard the changes of the new scene when asked.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/Main.stscene", "force": true } }
   ```

   :::
   ::::

   **You should see:** Coin Run, lit as you left it, with the sun at 25 degrees.

   **If you do not see it:** the editor shows the new scene. Open Coin Run again; nothing of it was lost, because you saved it.

:::::

::checkpoint{stage=5}

::figure{id=preview-lighting}

## Measure the light and make the coins glow

A picture lies about light: exposure and the tone curve change what you see. The **Luminance** debug view tells the truth. It colors each pixel by the real brightness of the surface in bands one stop wide, so each band is twice as bright as the one below it.

The bands carry numbers in EV100: the stops of the nits plus 3. For example: 16 nits is $2^4$, so EV 7; 128 nits is $2^7$, so EV 10; 2,048 nits is $2^{11}$, so EV 14. An interior lit by a window sits near EV 7 to 9, and a street in the sun at EV 14 to 15.

The view also checks the sun to sky ratio. With a ratio of 8, which is $2^3$, the ground in the sun lies three bands above the shaded ground. A ratio of 6 to 10 gives about 2.6 to 3.3 bands.

Light from an object itself uses the **Emissive Color** and **Emissive Intensity** of its material. The brightness is the color times the intensity, in nits. A monitor is 200 nits and a lit sign 1,000. Emission adds to the light the surface reflects. Next to a ground in the sun of several thousand nits, a glow of 200 barely shows, and in shadow it shows well.

:::::steps

1. Read the ground in the Luminance view. Choose the view and find the bands.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the debug view chip of the Scene view and choose **Luminance**. Look at the legend. Find the band of the ground in the sun, then the band of a shadow.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "luminance" } }
   ```

   :::
   ::::

   **You should see:** colored bands. The ground in the sun is two to three bands above its shadow, as the ratio of the **Clear** preset predicts.

   **If you do not see it:** the picture is the lit scene. The chip's label shows the view that runs: choose **Luminance** from its menu.

2. Make the gold glow. Choose the gold material in the Content Browser.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Materials/Gold.stmat`. Set **Emissive Color** to a warm yellow and **Emissive Intensity** to `200`. Look at a coin in the shadow of the ball. Then set `1000`.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/Gold.stmat", "properties": { "EmissiveColor": [1, 0.75, 0.3], "EmissiveIntensity": 200 } } }
   ```

   Then the same command with `{ "EmissiveIntensity": 1000 }`.

   :::
   ::::

   **You should see:** the coin brighter than before. At 200 nits the change shows in shade; at 1,000 nits it shows in the sun too. The Luminance view puts the coin in a higher band. All five coins change, because they share this material.

   **If you do not see it:** nothing changed. The coin must use this material, and **Emissive Color** must not be black.

3. Choose the glow for play and leave the debug view. Set **Emissive Intensity** to `200`, a gentle glow, and choose the lit view again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `200` in **Emissive Intensity**. Open the debug view chip and choose **Lit (no debug view)**.
   :::
   :::tab[With a command]

   First `material.set` on `Materials/Gold.stmat` with `{ "EmissiveIntensity": 200 }`, then:

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "none" } }
   ```

   :::
   ::::

   **You should see:** the normal picture, with the gold coins a little warmer than before.

   **If you do not see it:** the view stays colored. Choose **Lit (no debug view)** from the chip's menu.

:::::

The **Albedo** view in the same menu audits materials. [The materials chapter](materials.md) uses it.

::checkpoint{stage=6}

::figure{id=luminance-view}

## Light Coin Run for play

You now choose the look of the level. Clear fits a bright platform game: strong shadows, a deep blue sky. The sun's height at 35 degrees gives a shadow of 1.43 times the coin's height, long enough to read as a shape and short enough to stay near the coin.

:::::steps

1. Apply **Clear** with a sun 35 degrees up. The command also turns the sun back to 20 degrees around the vertical axis, the turn of the template.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Clear** in the **Sky** section. Select `Sun`, press **E** and lower the sun to about 35 degrees. Check **Shadow Distance** is 30.
   :::
   :::tab[With a command]

   ```json
   { "command": "lighting.applySkyPreset", "parameters": { "preset": "Clear", "sunElevation": 35, "sunAzimuth": 20 } }
   ```

   :::
   ::::

   **You should see:** in the Scene view, the coins casting shadows about one and a half times their height, and a blue sky wherever the view shows the horizon.

   **If you do not see it:** the shadows are short. The sun is still at 40 degrees: lower it more.

2. Save and play. Check the game as the player sees it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S**. Press the play button and look at the Game view. Press it again to stop.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   ```

   Then `play.start` with `"paused": true`, `play.step` with 60 steps, and `play.stop`.
   :::
   ::::

   **You should see:** the game lit as the Scene view was, because the scene has real lights. The game's camera looks down at 55 degrees, so the ground fills the picture and no sky shows.

   **If you do not see it:** the game is darker than the Scene view. Check that the `Post Process` entity is active.

:::::

::checkpoint{stage=7}

::figure{id=result}

## Summary

- Light has three units: lux for the sun, candela for lamps, and nits for the sky and for emission. One scale joins them.
- Exposure counts doublings. With automatic exposure a real sun needs **Auto Exposure Max EV** 16, and a dark scene needs a raised **Auto Exposure Min EV** to stay dark.
- The sky has three sources; **Extract Sun** moves a map's sun into the directional light, and the four presets set a sky, a sun and a safe exposure.
- A shadow is as long as the object's height divided by the tangent of the sun's elevation. **Shadow Distance**, **Angular Diameter** and **Cascade Blend** are the maker's shadow controls.
- Preview lighting lights a scene without light in the editor only; the game draws it dark.

## Check yourself

1. A clear sky, a candle and a monitor: name the unit of each.

   :::answer{tests="light-units"}
   The clear sky and the monitor are in nits, because you see them as patches of light. The candle is a source in candela, about 1 cd. Only the sun's light on the ground is in lux.
   :::

2. How many stops separate a room at 400 lux from a sunny day at 100,000 lux?

   :::answer{tests="light-units"}
   The ratio is 100,000 divided by 400, which is 250. The nearest row of the table is 256, which is $2^8$. The two differ by about 8 stops.
   :::

3. You turn **Auto Exposure** off and leave **Exposure** at 0 in a scene with a 120,000 lux sun. What do you see, and what do you set?

   :::answer{tests="set-exposure"}
   The picture is almost white, because the real sun is far above what a screen shows at no correction. Set **Exposure** near -15, or turn **Auto Exposure** on again.
   :::

4. A night scene with a 0.25 lux moon looks like a gray day. Which setting do you raise to keep it dark?

   :::answer{tests="set-exposure"}
   Automatic exposure adds back the missing stops because the scene is above its **Auto Exposure Min EV**. Raise that limit above the scene's own brightness, and the picture stays dark.
   :::

5. Why does **Extract Sun** also enable **Remove Sun** for the map?

   :::answer{tests="choose-sky"}
   A map photographed under the sun holds the sun's light. The new directional light carries it with shadows, so the map must lose it, or the sun counts twice.
   :::

6. A cube in a new scene shows lit in the Scene view and dark in the Game view. Why, and how do you fix the game?

   :::answer{tests="preview-light turn-sun"}
   The scene has no light, so the Scene view adds preview lighting for the editor only. Add a light, such as a **Directional Light**, and the game shows it lit. Turning that light toward the cube changes how long its shadow falls.
   :::

## Exercises

1. **Basic.** The **Overcast** preset has a sun of 1,500 lux, 60 degrees up, and a sky of 7,700 lux. Compute the sun to sky ratio, taking the sun's light on flat ground as 1,500 times 0.87.

   :::answer{tests="choose-sky light-units"}
   The sun gives 1,500 times 0.87, about 1,300 lux. Divide by 7,700: about 0.17. That is below the 0.3 of the table, so the sky dominates and the shadows are faint.
   :::

2. **Medium.** Make a late-afternoon Coin Run: apply **Golden Hour** with the sun's turn left at 20 degrees. Predict the shadow of a 0.5 m coin, then check it in the Scene view.

   :::answer[Worked solution]{tests="choose-sky turn-sun" solution="tutorials/make/lighting/exercise-2.tutorial.json"}
   At 6 degrees the tangent is about 0.105, so the shadow is 0.5 divided by 0.105, about 4.8 m. The solution applies the preset and checks the height of the sun: the upward part of `sunDirection` is 0.105, the sine of 6 degrees. The ratio of **Golden Hour** is about 1 to 2, so the picture is warm but the sky fills the shadows.
   :::

3. **Hard.** A new **Directional Light** starts at 3 lux, a value meant for an **Exposure** of 0. At which **Exposure** does a 120,000 lux sun look the same, with automatic exposure off?

   :::answer{tests="light-units set-exposure"}
   The sun is 120,000 divided by 3, which is 40,000 times brighter. The table has 32,768 at 15 stops and 65,536 at 16, so the gap is about 15 stops. Take 15 stops away: an **Exposure** near -15, the value of the sunny row of the reference table.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/ProjectTemplates.cpp`: the Basic 3D scene, its sun, sky and exposure of +0.25.
- `Strata/src/Strata/Renderer/SkyPresets.cpp`: the four presets and their values.
- `StrataEditor/src/Editor/EditorLightingCommands.cpp`: the commands `lighting.applySkyPreset` and `lighting.extractSun`.
- `Strata/src/Strata/Renderer/RendererComponents.h`: the light, sky and Post Process components, with their units and limits.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `SceneRenderer::NeedsPreviewLighting`, the rule behind preview lighting.
- `Docs/Manual/Lighting.md`: the engine's own guide to lights, units and exposure.

## Further reading

- Poly Haven, "Kloofendal 48d partly cloudy (pure sky)": the HDR image of this page, with its license (beginner).
- Wikipedia, "Exposure value": the photographers' scale of stops, EV100 and its reference table (intermediate).
