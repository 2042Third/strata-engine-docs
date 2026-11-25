---
id: make/look
title: "The camera's image"
description: "Give a scene a camera look by day and by night: exposure, tone, color, a lookup, lens effects, height fog and lens blur, and what each costs."
kind: tutorial
size: L
tracks: [G]
needs: [make/project-coin-run]
time: 150
learn:
  - id: image-order
    text: name the order in which a camera turns light into a picture and place each Post Process setting in it
  - id: set-look
    text: set exposure, the tone curve, color and a color lookup on purpose and predict what each changes
  - id: add-lens
    text: choose bloom, vignette, lens flare, grain and chromatic aberration with restraint and compare what each costs
  - id: lay-fog
    text: compute how far a Height Fog hides the view and how thick its layer is, and lay one in a scene
  - id: set-camera
    text: set the Camera's field of view, planes, projection, clear color, depth of field and motion blur
since: 0.3.0
status: final
---

## What you will make

A copy of the Third-Person Adventure's course with a camera look of your own: first a bright day, then a night. You set the exposure, the tone curve, the color, a lookup, the lens, fog and blur, and you can say what each choice costs.

::figure{id=result}

## How a camera makes a picture

A real camera sees light and records a picture. A game does the same in a fixed order, and knowing the order tells you which setting to touch for which problem.

The :term[renderer]{id=renderer} first computes light in real units: :term[lux]{id=lux} for the sun, nits for the sky. A sunny street gives hundreds of times more light than a room with lamps, and a screen cannot show that range.

Strata does this in one order for every frame. The first active **Post Process** component in the scene sets the look, and a scene without one uses the defaults, which a new component also gets.

```mermaid caption="The camera's order, from light to screen. Blur comes first, exposure scales the light, the lens adds glow and a darker rim, color and the tone curve follow, and the lookup, grain and the screen come last." alt="A flow chart in nine boxes joined by arrows. The scene's light flows to lens blur, then exposure, then bloom, flare and vignette on the light, then white balance and grading, then the tone curve, then the color lookup, then grain, then the screen."
flowchart LR
  A[Scene light] --> B[Lens blur]
  B --> C[Exposure]
  C --> D[Bloom, flare and vignette]
  D --> E[White balance and grading]
  E --> F[Tone curve]
  F --> G[Color lookup]
  G --> H[Grain]
  H --> I[Screen]
```

Exposure comes before the tone curve, so a scene that is far too bright reaches the curve already too bright, and no curve repairs it.

A fix at the wrong step costs effort. If the picture is too dark, change exposure, not the curve. If it looks cold, change white balance, not a lookup.

**Tone mapping** is the step that does this: it maps light of any brightness onto the screen's range, so bright colors roll off to white instead of cutting off.

The sections below follow the same order. Each ends with a checkpoint: the editor commands that lead there from the checkpoint before. Your copy of the sample is the project, so no checkpoint offers one.

## What you need

- A copy of the Third-Person Adventure made with **File ▸ Open Sample**, with `Scenes/Course.stscene` open. You made such a copy in [the first game](../start/first-game.md). The command is `project.openSample` with the sample `ThirdPerson` and an empty folder as `directory`.
- The file `warm-look.cube`, a small warm color lookup made for the book, which the section on color imports. No download holds it: save the lines below in a text editor under that name.
- Exposure in stops and the **Luminance** view from [the lighting tutorial](lighting.md), and importing a file from [the assets tutorial](assets.md).
- About 150 minutes. Every step works in the editor you already have.

```text
LUT_3D_SIZE 2
0.01 0.005 0
1.07 0.005 0
0.01 1 0
1.07 1 0
0.01 0.005 0.88
1.07 0.005 0.88
0.01 1 0.88
1.07 1 0.88
```

The table has two points along each color, and each line after the first is the color that one corner becomes: a little more red, a little less blue and the blacks lifted.

## Start from the course

Read the defaults first: every later step changes one of them.

:::::steps

1. Open `Scenes/Course.stscene` in your copy and select the entity `Post Process` in the **Hierarchy**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click `Post Process` in the **Hierarchy**. The **Inspector** shows its **Post Process** component, in groups of settings named for tone, exposure, bloom and the lens.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.get", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess" } }
   ```

   A command takes an entity's identifier (ID), not its name: each `<the ID of …>` is what `entity.find` returns for that name.
   :::
   ::::

   **You should see:** **Tonemapper** is Filmic, **Exposure** is 0, **Auto Exposure** is on, and **Bloom** is on at 0.04.

   **If you do not see it:** you may have selected the `Camera` entity. The look sits on the entity named `Post Process`, not on the camera.

2. Look at the scene and note the sky's brightness, the color of the grass and the lanterns.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Use the Scene view to look along the course. Change nothing yet.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.get", "parameters": { "entity": "<the ID of Camera>", "component": "Camera" } }
   ```

   :::
   ::::

   **You should see:** a bright daylight course, the picture that every later step changes.

   **If you do not see it:** you may have another scene open. Open `Scenes/Course.stscene` from the **Content Browser**.

:::::

::checkpoint{stage=1}

::figure{id=start-course}

## Set the exposure

**Exposure** scales the light before anything else happens, as the lens opening and the shutter of a camera do. You count it in stops: +1 shows the scene twice as bright and -1 half as bright.

With **Auto Exposure** on, the camera meters the picture and maps its average brightness to middle gray, the gray that looks halfway between black and white. **Exposure** then adds stops on top. A metered picture of a snowy field and of a pile of coal would both come out middle gray, so you correct it by hand: +1 for the snow, -1 for the coal.

### Metering, adaptation and the key

Four ideas decide how the meter behaves.

**Metering** says which pixels count. **Center Weighted** gives the middle of the image full weight and its edges a quarter of it, so a bright sky at the top moves the exposure less. **Average** gives every pixel the same weight. Both ignore the 10 % darkest and the 10 % brightest pixels, so deep shadows and bare light sources do not move the exposure.

**Adaptation** says how fast the exposure follows a change. The exposure follows a brighter scene at 3 per second and a darker one at 1.5 per second, the way eyes recover from glare faster than they adjust to the dark. In each frame it covers the fraction $1 - e^{-k\,\Delta t}$ of the distance that remains, so the result does not depend on the frame rate.

The symbols: $k$ is the speed in 1 per second, $\Delta t$ is the time of a frame in seconds, and $e$ is the number 2.718, so $e^{-x}$ shrinks as $x$ grows. A speed of 0 jumps at once.

:::example
A frame at 60 frames per second lasts $\Delta t = 0.0167$ seconds. With the light speed $k = 3$, the exponent is $0.05$ and each frame covers $1 - e^{-0.05} = 0.049$, about 5 % of what remains. After one second, 60 frames, the exposure has covered $1 - e^{-3} = 0.95$, so 95 %.
:::

The **key** is the setting that lets an interior read darker than the street. If a camera metered every scene to middle gray, a dim room would look as bright as a sunny street. Strata compares the metered brightness with a gray card: a flat middle-gray surface lit by the scene's directional light. **Auto Exposure Key** (0.12) is the share of the difference that the picture keeps. A room five stops under the card shows $0.12 \times 5 = 0.6$ stops darker, and no scene shows more than 2 stops darker.

The key never brightens, and it needs a directional light.

Two limits bound the metered average, which counts in exposure value (EV), the stops of nits: **Auto Exposure Min EV** and **Auto Exposure Max EV**. Real sunlight needs the default **Auto Exposure Max EV** of 16: a cap near 12 shows a sunny scene darker than it is. A scene whose average lies under the Min EV floor is not brightened further, so a raised floor keeps a dark scene dark.

:::::steps

1. Open the **Luminance** debug view so you judge the real brightness, not the picture's.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the debug view chip of the Scene view and choose **Luminance**.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "luminance" } }
   ```

   :::
   ::::

   **You should see:** one flat dark blue, the legend's lowest band, `EV <6`. The bands start at 4 nits, a dim room, and the sample lights the course with a sun of about 3 lux, so the whole course lies below them. The meter lifts that dim light to a bright picture.

   **If you do not see it:** the chip shows another view. Choose **Luminance** from its menu.

2. Choose the view **None** again, then set **Exposure** to 1 and to -1 to see two stops.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Post Process`. In the Exposure group drag **Exposure** to `1`, look, then to `-1`, look, then back to `0`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "Exposure": 1 } } }
   ```

   First the view's command with `"none"`. Then this one with `-1`, and last with `0`.
   :::
   ::::

   **You should see:** a picture a full stop brighter at +1 and darker at -1. The meter does not pull it back, because **Exposure** adds on top of what it metered.

   **If you do not see it:** the change is small on a screen that already looks bright. Compare two screenshots, not your memory.

3. Compare the two metering modes.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Auto Exposure Metering** to **Average**. Tilt the Scene view up toward the sky, then down toward the ground, and watch the brightness. Set it back to **Center Weighted**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AutoExposureMetering": "Average" } } }
   ```

   Then set `"CenterWeighted"` again.
   :::
   ::::

   **You should see:** under **Average**, a sky that fills the top of the view moves the exposure more than under **Center Weighted**.

   **If you do not see it:** the fields are grey. They are inactive while **Auto Exposure** is off, so enable it.

4. Slow the adaptation to see it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Auto Exposure Light Speed** and **Auto Exposure Speed** to `0.3`. Look at the sky, then swing the view down at the ground. Set the two back to `3` and `1.5`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AutoExposureLightSpeed": 0.3, "AutoExposureSpeed": 0.3 } } }
   ```

   Then the same command with `3` and `1.5`.
   :::
   ::::

   **You should see:** the picture needs several seconds to settle after the swing, since a speed of 0.3 covers only 26 % of the distance in one second.

   **If you do not see it:** the two views have almost the same brightness. Face the sky, then a dark corner.

5. Read the effect of the key.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Auto Exposure Key** to `0`, then to `0.12`, and compare a dark corner of the course.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AutoExposureKey": 0 } } }
   ```

   Then the same command with `0.12`.
   :::
   ::::

   **You should see:** at 0 every scene meters to middle gray; at 0.12 a dark corner reads a little darker. Where the course meters near the sun's card, the key changes nothing.

   **If you do not see it:** the scene is already bright, and the key only darkens. A dark scene shows the effect.

:::::

::checkpoint{stage=2}

::figure{id=exposure-luminance}

## Choose the tone curve

The tone curve decides how light far brighter than white lands on the screen. Without a curve every bright color would cut off at the same flat white.

**Filmic** is the default. It shows a metered middle gray as middle gray, rolls highlights off to white over six and a half stops, and keeps the hue of a bright saturated color: a red light stays red.

**Toe** (0.5) sets how deep the shadows go. A higher value crushes the darkest tones toward black and a lower one keeps more detail. **Shoulder** (0.5) sets how gently the highlights approach white. At 0 the curve reaches white 5 stops over middle gray, at 0.5 after 6.5 stops and at 1 after 8 stops.

Academy Color Encoding System (ACES) is the film industry's curve, and Strata offers one fitted to it. It shows middle gray about 0.8 stops darker, so you set **Exposure** to +0.8 for the same brightness, and it moves bright reds toward orange. The gain of 0.8 stops is $2^{0.8} = 1.74$, almost twice as bright.

The slider shows the course under both curves, Filmic at 0 and ACES at +0.8.

::compare{id=tone-curves before=filmic after=aces}

**Contrast** (1) widens or narrows the gap between dark and light around middle gray, and it acts before the curve. **Saturation** (1) makes colors stronger or weaker, after the curve.

:::::steps

1. Make a test lamp: a very bright red light. Select the material `Materials/LanternGlow.stmat` and set its emission.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the file in the **Content Browser**. In the **Inspector** set **Emissive Color** to a pure red and **Emissive Intensity** to `4000`.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/LanternGlow.stmat", "properties": { "EmissiveColor": [1, 0.05, 0.02], "EmissiveIntensity": 4000 } } }
   ```

   :::
   ::::

   **You should see:** the glow of the lanterns, now red and far above white.

   **If you do not see it:** you may be looking away from a lantern. Select `Lantern A` in the **Hierarchy** and press **F** to look at it.

2. Compare the curves on the lamp. Start with Filmic, then use ACES at +0.8.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Post Process`. In **Tonemapper** choose **ACES** and set **Exposure** to `0.8`. Look at the lamp, then choose **Filmic** and set **Exposure** to `0`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "Tonemapper": "ACES", "Exposure": 0.8 } } }
   ```

   Then the same command with `"Filmic"` and `0`.
   :::
   ::::

   **You should see:** under **Filmic** the lamp stays red toward its edge; under **ACES** the bright red turns toward orange and the scene shows stronger color.

   **If you do not see it:** you may still be at **Exposure** 0 under **ACES**. The scene then looks darker, as the 0.8 stops explain.

3. Shape the Filmic curve. Return to Filmic, then move **Toe** and **Shoulder**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Toe** to `0.8` and look at the dark corners, then to `0.2`. Set **Shoulder** to `1` and look at the sky near the sun, then to `0`. Return both to `0.5`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "Toe": 0.8, "Shoulder": 1 } } }
   ```

   Then `0.2` and `0`, and last `0.5` and `0.5`.
   :::
   ::::

   **You should see:** a higher **Toe** blackens the shadows, and a higher **Shoulder** keeps detail in the brightest parts.

   **If you do not see it:** **Toe** and **Shoulder** are grey. They work only under **Filmic**.

4. Set **Contrast** and **Saturation**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Contrast** to `1.2` and **Saturation** to `0.8`, look, then return both to `1`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "Contrast": 1.2, "Saturation": 0.8 } } }
   ```

   Then the same command with `1` and `1`.
   :::
   ::::

   **You should see:** a firmer picture with less vivid color.

   **If you do not see it:** the change is small. Compare screenshots.

5. Restore the lanterns.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set the material's **Emissive Color** back to `1, 0.72, 0.4` and **Emissive Intensity** to `12`.
   :::
   :::tab[With a command]

   ```json
   { "command": "material.set", "parameters": { "material": "Materials/LanternGlow.stmat", "properties": { "EmissiveColor": [1, 0.72, 0.4], "EmissiveIntensity": 12 } } }
   ```

   :::
   ::::

   **You should see:** the lanterns glow warm orange again.

   **If you do not see it:** type the two values again, or press **Ctrl+Z** while the scene view has focus.

:::::

::checkpoint{stage=3}

::figure{id=tone-curves variant=filmic}

## Grade the color and use a lookup

Color acts on the light after exposure, ahead of the curve. **White Balance Temperature** (6500 K, neutral) is the color of light that the camera shows as white. Kelvin (K) counts the color of a light: candles are near 2000 K and daylight near 6500 K. At 3200 K, walls under warm bulbs look white and things in daylight turn blue, and a higher value warms the picture. **White Balance Tint** moves between green and pink: a positive value adds pink and a negative one green.

**Color Slope** is a gain per channel, **Color Offset** adds light per channel and tints the shadows most, and **Color Power** is a contrast per channel around middle gray. A slope of 1, an offset of 0 and a power of 1 on every channel change nothing.

A **color lookup** is a table that maps every color of the finished picture to another color. A person who grades color makes one in a grading tool and saves it as a `.cube` file. It acts on the finished picture, so you make it from a capture of the game.

The import setting **Size** sets the grid of the stored table: 17, 33 (the default) or 65 points along each color. More points follow fine changes more closely and use more memory. A lookup loads in the background, and nothing applies until it is in.

:::::steps

1. Warm the picture with the white balance.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **White Balance Temperature** to `8000`, look, then to `4500`, look, then to `6500`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "WhiteBalanceTemperature": 8000 } } }
   ```

   Then `4500`, and last `6500`.
   :::
   ::::

   **You should see:** 8000 K warms the picture and 4500 K cools it, because the camera takes the light for a warmer or a cooler one.

   **If you do not see it:** the number names the light that shows as white, so a low value cools the picture and a high one warms it.

2. Grade the shadows with **Color Offset**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Color Offset** to `0.02, 0, 0.03`, look at the shadows, then return it to `0, 0, 0`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "ColorOffset": [0.02, 0, 0.03] } } }
   ```

   Then the same command with `[0, 0, 0]`.
   :::
   ::::

   **You should see:** a violet cast in the darkest parts and little change in the bright ones.

   **If you do not see it:** the offset counts in fractions of middle gray, so it is small. Raise it to `0.05`.

3. Import the lookup file.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag `warm-look.cube` from the download into the **Content Browser**, into a folder named `Lookups`. Select it and check that its **Size** is `33`.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "file": "<download folder>/warm-look.cube", "directory": "Lookups" } }
   ```

   Then `asset.info` on `Lookups/warm-look.cube` shows `Size` `33` in `importSettings`. Checkpoint 4's commands start with that check, so import the file before you run them.

   :::
   ::::

   **You should see:** the file in the **Content Browser** with the type Color Lookup.

   **If you do not see it:** the file may not be a 3D table. The import reports the line where it went wrong.

4. Use the lookup on the Post Process.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Post Process`. Drag the lookup onto **Color Lookup**, or choose it in the field. Set **Color Lookup Intensity** to `0`, then `0.5`, then `1`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "ColorLookup": "Lookups/warm-look.cube", "ColorLookupIntensity": 0 } } }
   ```

   Then `0.5`, and last `1`.

   :::
   ::::

   **You should see:** at 0 the plain picture, at 0.5 a halfway grade and at 1 the full warm grade.

   **If you do not see it:** the lookup is still loading, and nothing shows until it is in. Wait a moment.

:::::

::checkpoint{stage=4}

::figure{id=lookup-intensity variant=half}

## Add the lens

A lens has flaws that make a picture feel photographed. Use them with restraint: the first two are on by default and small, the last three are off.

**Bloom** spreads a small share of the light into a soft glow. **Bloom Intensity** (0.04) is that share. **Bloom Radius** (0.059) is how far the glow reaches as a fraction of the image height. **Bloom Threshold** (0) keeps the glow to light above that brightness.

**Vignette** (0.12) darkens the corners as a real lens does: at 0.12 the corners of a 60 degree view lose about 10 %. **Lens Flare** (0) adds faint ghosts and a starburst around very bright light, and only light far brighter than white makes them. **Film Grain** (0) adds fine noise that changes every frame, and 0.1 to 0.3 reads as texture. **Chromatic Aberration** (0) draws red and blue apart toward the corners.

:::::steps

1. Raise the bloom.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Bloom Intensity** to `0.15`, look at the lanterns and the sky, then back to `0.04`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "BloomIntensity": 0.15 } } }
   ```

   Then the same command with `0.04`.
   :::
   ::::

   **You should see:** a softer glow around the lanterns and bright edges, and a less clear picture overall.

   **If you do not see it:** **Bloom Intensity** is grey. It works only while **Bloom** is on.

2. Set the vignette.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Vignette** to `0.5`, look at the corners, then back to `0.12`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "Vignette": 0.5 } } }
   ```

   Then the same command with `0.12`.
   :::
   ::::

   **You should see:** darker corners that draw the eye to the middle.

   **If you do not see it:** raise it to `1` for the full fall-off of a lens.

3. Search for a flare with the sun in view.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Lens Flare** to `0.4`. Turn the Scene view toward the sun until its disk is in view and nothing covers it.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "LensFlare": 0.4 } } }
   ```

   :::
   ::::

   **You should see:** faint ghosts across the picture and rays around the sun's disk.

   **If you do not see it:** the sun may be hidden. The rays need its disk in view and uncovered.

4. Try grain and color fringes, then keep them small.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Film Grain** to `0.2` and **Chromatic Aberration** to `0.3`, look at the corners, then set both to `0`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "FilmGrain": 0.2, "ChromaticAberration": 0.3 } } }
   ```

   Then the same command with `0` and `0`.
   :::
   ::::

   **You should see:** fine noise in the mid-tones and red and blue edges toward the corners.

   **If you do not see it:** the effect is small on a small screen. Look at the corners of the Game view.

:::::

::checkpoint{stage=5}

::figure{id=lens-effects}

## Lay height fog

Fog hides what is far away, and the eye reads the haze as depth. **Height Fog** is fog that is thickest at one height and thins above it. **Density** (0.02) is how much it hides at the base, **Base Height** is the world height where the density has that value, and **Height Falloff** (0.2) is how fast it thins with height, per meter.

Two formulas read the fog. Light that crosses fog of constant density $d$ over a distance $s$ keeps the share $e^{-d\,s}$, so $1 - e^{-d\,s}$ is hidden. With $d = 0.02$ and $s = 35$ m, $d\,s = 0.7$ and about half is hidden.

The density at a height $h$ above the base is $d\,e^{-f\,h}$, where $f$ is the **Height Falloff**. It shrinks by the factor $e$ every $1/f$ meters: every 5 m at 0.2 and every 50 m at 0.02. The symbols: $d$ is the density per meter, $s$ the distance in meters, $h$ the height in meters, $f$ the thinning per meter.

**Color From Sky** lights the fog with the colors of the sky, which hides the line between fog and horizon. **Sun Scattering** makes it glow toward the sun. **Height Falloff** must stay above 0, since with none the density is the same at every height and the fog never ends toward the sky. And Height Fog is no volume: it shows no light shafts, and lamps do not light it.

Fog also fits how far the world is drawn. At constant density 0.02 the hidden share at 230 m is $1 - e^{-4.6} = 0.99$. A camera that draws to 1000 m draws 770 m that nobody sees, so match the far plane to the fog.

:::::steps

1. Add the fog from the Inspector.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click an empty place in the **Hierarchy** so that nothing is selected. In the Sky section of the **Inspector** press **Add Height Fog**.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Height Fog", "components": { "HeightFog": {} } } }
   ```

   :::
   ::::

   **You should see:** a new entity `Height Fog`, and the far islands fading toward the color of the sky.

   **If you do not see it:** the button is missing because the scene already has fog. Edit the entity that holds it.

2. Set the density and the base.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Height Fog`. Set **Density** to `0.01`, **Base Height** to `-2` and **Height Falloff** to `0.1`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Height Fog>", "component": "HeightFog", "values": { "Density": 0.01, "BaseHeight": -2, "HeightFalloff": 0.1 } } }
   ```

   :::
   ::::

   **You should see:** haze that thickens toward the end of the course, with the near ground clear.

   **If you do not see it:** raise **Density** to `0.03` to see the effect, then tune it back.

3. Compare **Color From Sky** and **Sun Scattering**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Disable **Color From Sky**, look at the color of the fog itself, then enable it. Set **Sun Scattering** to `1`, look toward the sun, then back to `0.5`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Height Fog>", "component": "HeightFog", "values": { "ColorFromSky": false, "SunScattering": 1 } } }
   ```

   Then `true` and `0.5`.
   :::
   ::::

   **You should see:** without the light of the sky the fog has a flat color of its own and may show a seam at the horizon; with it the fog meets the sky.

   **If you do not see it:** the sun may be behind you. The glow shows only toward it.

4. Match the far plane of the camera to the fog.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Camera`. In its **Camera** component set **Perspective Far** to `300`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Camera>", "component": "Camera", "values": { "PerspectiveFar": 300 } } }
   ```

   :::
   ::::

   **You should see:** no change where the fog is dense.

   **If you do not see it:** you see a hard edge in the distance. The fog is too thin at 300 m, so raise **Density** or **Perspective Far**.

:::::

::checkpoint{stage=6}

::figure{id=height-fog}

## Add motion blur

A film camera exposes each frame for only part of the time between two frames, so moving things smear along their path. **Motion Blur** is off by default, because slow and precise games read better without it.

**Motion Blur Shutter Angle** is the share of the frame in which the shutter is open, in degrees of 360. At 180 degrees the shutter is open for half a frame, and at 90 degrees for a quarter, so the blur halves. **Motion Blur Max Length** caps the blur as a fraction of the image height: 0.02 is 21.6 pixels at 1080 rows.

Only what moves on screen blurs, and a character that the camera follows stays sharp. The first frame and camera cuts never blur, and neither do menus and text. Editor views never blur: only the Game view, or a Scene view that looks through the game's camera, shows it while the game plays.

:::::steps

1. Enable the blur and play.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Post Process` and enable **Motion Blur**. Press **Play**, run and turn the camera with the mouse.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "MotionBlur": true } } }
   ```

   Then start the game with `play.start`.
   :::
   ::::

   **You should see:** in the Game view the islands streak as you turn, and the robot stays sharp.

   ::figure{id=motion-blur-turn crop=far}

   **If you do not see it:** you are looking through the editor camera, which never blurs. Open the Game view.

2. Compare 180 degrees with 90.

   ::::tabs{sync=how}
   :::tab[In the editor]
   While you play, set **Motion Blur Shutter Angle** to `90`, turn the camera, then set it to `180`. Press **Stop**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "MotionBlurShutterAngle": 90 } } }
   ```

   Then the same command with `180`, and `play.stop`.
   :::
   ::::

   **You should see:** at 90 degrees the streaks are about half as long.

   **If you do not see it:** turn the camera faster. A blur shorter than a pixel is dropped.

:::::

::checkpoint{stage=7}

::figure{id=motion-blur-turn}

## Use the Camera as a lens

The picture comes through a **Camera** component, which is a lens too. **Primary** marks the camera that the game draws through: the first active primary camera renders the Game view. **Perspective FOV** (60 degrees) is the vertical field of view. **Perspective Near** and **Perspective Far** bound what is drawn, and the far one belongs with the fog.

**Projection** chooses Perspective or Orthographic. An orthographic camera has no depth, so far things are as large as near things, which suits a 2D, top-down or puzzle game. **Orthographic Size** is the height of the view in meters, so 10 shows a strip ten meters tall. The fields that the projection does not use turn grey, and their tooltip says why.

**Clear Color** shows wherever no sky is drawn: in a scene without a sky, or under a Sky Light with **Show Background** off.

**Depth Of Field** blurs what lies nearer or farther than the focus, and **Focus Entity** keeps one entity sharp. **Sensor Height** (24 mm, full frame) and the field of view set the focal length, the distance from the lens to its sharp image. Half the sensor, 12 mm, divided by the tangent of half the view gives it: $f = 12 / \tan(30^\circ) = 20.8$ mm at 60 degrees.

**Aperture** (2.8) is the f-number, and the opening of the lens is the focal length divided by it: 10.4 mm at f/2 and 2.6 mm at f/8. A lower f-number blurs more.

:::::steps

1. See the inactive fields of an orthographic camera.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Camera`. Set **Projection** to **Orthographic**, hover over the grey **Perspective FOV**, then set **Projection** back to **Perspective**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Camera>", "component": "Camera", "values": { "Projection": "Orthographic" } } }
   ```

   Then the same command with `"Perspective"`.
   :::
   ::::

   **You should see:** the course drawn without depth, the perspective fields grey, and a tooltip that names the reason.

   **If you do not see it:** hover longer over the grey field. The tooltip says that the camera's projection is Orthographic.

2. Show the clear color.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Sky` and disable **Show Background**. Select `Camera` and set **Clear Color** to a deep blue. Then enable **Show Background** again.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sky>", "component": "SkyLight", "values": { "ShowBackground": false } } }
   ```

   Then the same on `Camera` with `"ClearColor": [0.05, 0.1, 0.4, 1]`, and last `true` on the sky.
   :::
   ::::

   **You should see:** a flat color where the sky was while **Show Background** is off.

   **If you do not see it:** the sky draws its background while **Show Background** is on, so the clear color stays hidden.

3. Enable depth of field with the robot in focus.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Camera`. Enable **Depth Of Field**, then drag the `Robot` entity from the **Hierarchy** into **Focus Entity**.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.find", "parameters": { "name": "Robot" } }
   ```

   Then set `DepthOfField` to `true` and `FocusEntity` to the id this command returned, on the `Camera` component.
   :::
   ::::

   **You should see:** the robot sharp, with the islands near and far softened.

   **If you do not see it:** you look through the editor camera, which never blurs. Look through the game's camera in the Game view.

4. Compare the lens openings.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Set **Aperture** to `2`, look, then to `8`, look, then back to `2.8`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Camera>", "component": "Camera", "values": { "Aperture": 2 } } }
   ```

   Then `8`, and last `2.8`.
   :::
   ::::

   **You should see:** f/2 blurs the islands more than f/8, and at f/8 almost everything is sharp.

   **If you do not see it:** at 60 degrees the far background blurs little, as with a wide lens. Narrow **Perspective FOV** to `30` to see the blur grow.

:::::

### What each effect costs

The numbers below come from the engine's own guide: medians at 3840x2160 on a fast :term[graphics card]{id=gpu}, not new measurements.

| Effect | Cost and share of a frame at 60 frames per second |
| --- | --- |
| Exposure, bloom, the tone curve, color and vignette together | 0.18 ms, 1.1 %, without anti-aliasing |
| Motion blur at 12 samples, the camera turning | 0.18 ms, 1.1 % |
| Motion blur, the camera still | 0.11 ms, 0.7 % |
| Depth of field, everything far blurred at the largest circle | 0.20 ms, 1.2 % |
| Lens flare, the sun in view | 0.035 ms more, 0.2 % |

When off, motion blur, depth of field and lens flare cost nothing, since no pass runs. Grain, color fringes and a lookup belong to the tone mapping and add a few operations per pixel.

Players can disable some effects. The graphics quality settings have the rows **Motion blur**, **Depth of field**, **Film grain** and **Chromatic aberration**, each **Scene** or **Off**, the same at every preset. A row disables what your scene enables and never enables what it lacks.

The row **Motion blur samples** sets the samples per pixel of the blur: more samples show less streak noise along fast edges for more time. [The quality rows](../image/quality-settings.md) list its value for each preset, and [the quality tutorial](quality.md) explains presets.

Strata does not do two things here. It has no system for particles and trails, such as fire, smoke and sparks, and none for marks laid on surfaces, such as skid marks and bullet holes. It has no post-process volumes, so a game changes its look by turning one Post Process off and another on.

::checkpoint{stage=8}

::figure{id=camera-lens}

## Give the course a night look

A night is a mood, not only a darker picture. The recipe has five values, each with a reason: **Exposure** -1.5, because a night should look dark and not like a dim day. **Auto Exposure Min EV** -2.5, a raised floor, because the meter would otherwise lift the course under the moon to a day's brightness. **White Balance Temperature** 4500, which a camera reads as a warmer light, so the picture turns cool. **Toe** 0.6 lets the shadows go deeper, and **Bloom Intensity** 0.06 lets lamps glow.

On a scene that is lit like day, the recipe only dims the day. You first make faint moonlight: a weak sun and a weak sky.

:::::steps

1. Make moonlight.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Sun` and set **Intensity** to `0.2`. Select `Sky` and set **Intensity** to `0.001`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Sun>", "component": "DirectionalLight", "values": { "Intensity": 0.2 } } }
   ```

   Then the same on the `SkyLight` of `Sky` with `Intensity` `0.001`.
   :::
   ::::

   **You should see:** a dark course; with **Auto Exposure** on it may still look like a gray day.

   **If you do not see it:** the meter is at work, and the next step raises its floor.

2. Set the recipe on the Post Process.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Post Process`. Set **Exposure** to `-1.5`, **Auto Exposure Min EV** to `-2.5`, **White Balance Temperature** to `4500`, **Toe** to `0.6` and **Bloom Intensity** to `0.06`.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "Exposure": -1.5, "AutoExposureMinEV": -2.5, "WhiteBalanceTemperature": 4500, "Toe": 0.6, "BloomIntensity": 0.06 } } }
   ```

   :::
   ::::

   **You should see:** a dark, cool picture: a dim blue-green course under a black sky. A lantern glows white where one is in view: select `Lantern A` and press **F**, or send `camera.focus` with its ID in `entities`.

   **If you do not see it:** the picture is still bright. Lower the **Intensity** of `Sky` by a factor of 10.

3. Check the look in the **Luminance** view, then choose **None**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Luminance** in the debug view chip and read the legend. Then choose **None**.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "luminance" } }
   { "command": "viewport.capture", "parameters": { "debugView": "luminance" } }
   { "command": "viewport.setSettings", "parameters": { "debugView": "none" } }
   ```

   :::
   ::::

   **You should see:** the same flat dark blue as by day. The course lay below the first band already, and the night is darker still: the median `surfaceEv100` of a capture falls from about 2 to about 1.

   **If you do not see it:** you may be in another view. Open the chip's menu.

:::::

::checkpoint{stage=9}

::figure{id=night-look}

## Summary

- A camera turns light into a picture in a fixed order: blur, exposure, bloom and vignette, white balance and grading, the tone curve, the lookup, grain and the screen. The first active Post Process sets the look.
- You set exposure in stops, the Filmic curve with **Toe** and **Shoulder** or ACES at +0.8, white balance in kelvin, and a lookup mixed in by its intensity.
- Bloom, vignette, flare, grain and color fringes stay small. Each costs about 1 % of a frame at 60 frames per second or less and nothing when off.
- A Height Fog hides the share $1 - e^{-d\,s}$ of the view and thins by the factor $e$ every $1/f$ meters, needs a **Height Falloff** above 0 and is no volume.
- The Camera sets the projection, the planes, the clear color and depth of field, and motion blur shows only through the game's camera while the game plays.

## Check yourself

1. A scene is too dark. Which step of the camera's order do you change first, and why not the tone curve?

   :::answer{tests="image-order"}
   Change exposure, which comes first and scales the light. The curve works on what exposure made, so it cannot repair a scene that arrives too dark.
   :::

2. A room meters 5 stops under the gray card of the sun, and the key is 0.12. How much darker does it show, and what if it meters 20 stops under?

   :::answer{tests="set-look"}
   $0.12 \times 5 = 0.6$ stops darker. At 20 stops the product is 2.4, so the result stops at 2, the most the key gives.
   :::

3. You switch from Filmic to ACES. What do you add to **Exposure** to keep the brightness, and which factor is that?

   :::answer{tests="set-look"}
   Add +0.8 stops, a factor of $2^{0.8} = 1.74$, because ACES shows middle gray about 0.8 stops darker.
   :::

4. Which lens effects do you keep small, and what do they cost when off?

   :::answer{tests="add-lens"}
   Grain, chromatic aberration and lens flare, which are off by default. When off, the flare runs no pass and grain and fringes add nothing; when on, grain and fringes add a few operations per pixel.
   :::

5. Fog of density 0.04 stands between you and a mountain 50 m away. What share does it hide at constant density?

   :::answer{tests="lay-fog"}
   $d\,s = 0.04 \times 50 = 2$, so $1 - e^{-2} = 0.86$: 86 % is hidden.
   :::

6. A game is 2D and top-down. Which two **Camera** fields do you change, and which fields turn grey?

   :::answer{tests="set-camera"}
   Set **Projection** to **Orthographic** and **Orthographic Size** to the height of the view in meters. The perspective fields turn grey, and their tooltip says why.
   :::

## Exercises

1. **Basic.** Lay a fog whose density shrinks by the factor $e$ every 50 m. Which **Height Falloff** do you set?

   :::answer{tests="lay-fog"}
   The value is $1/50 = 0.02$ per meter, since the density shrinks by $e$ every $1/f$ meters.
   :::

2. **Medium.** A camera has a field of view of 30 degrees and a 24 mm sensor. Compute its focal length and the opening of the lens at f/2.

   :::answer{tests="set-camera"}
   $f = 12 / \tan(15^\circ) = 12 / 0.268 = 44.8$ mm. The opening is $44.8 / 2 = 22.4$ mm. A narrower view means a longer lens, which blurs the background more at the same f-number.
   :::

3. **Hard.** Lay valley fog under the islands, a layer 50 m thick, and tune its density so that it hides half of what lies 20 m away at its base.

   :::answer[Worked solution]{tests="lay-fog set-look" solution="tutorials/make/look/exercise-3.tutorial.json"}
   Set **Base Height** to `-2` and **Height Falloff** to `0.02`, so the density shrinks by $e$ every 50 m. Half is hidden when $d \times 20 = 0.69$, so **Density** is $0.69 / 20 = 0.035$. Look from the first island: the fog reads as a sea below the course.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RendererComponents.h`: the Post Process and Height Fog components, with their defaults and limits.
- `Strata/src/Strata/Renderer/RendererComponents.cpp`: the Inspector's groups and tooltips for them.
- `Strata/src/Strata/Scene/Components.h`: the Camera component, with its planes, clear color and lens fields.
- `Strata/shaders/PostProcess/Tonemap.frag.slang`: the order of bloom, vignette, grading, the tone curve, the lookup and grain.
- `Docs/Manual/Camera.md`: the engine's own guide to the camera's image, its costs and its three recipes.

## Further reading

- Wikipedia, "Exposure value": the photographers' scale of stops (intermediate).
- Wikipedia, "Tone mapping": why bright light needs a curve (intermediate).
- Wikipedia, "Color grading": what a person who grades color does with a lookup (beginner).
