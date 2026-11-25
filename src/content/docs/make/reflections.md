---
id: make/reflections
title: "Sky light, ambient occlusion and reflections in your game"
description: "Light a courtyard with the sky, darken its creases, give a room a reflection probe and a floor wet reflections, and turn the sun through a day."
kind: how-to
size: L
tracks: [G]
needs: [make/project-coin-run]
time: 90
learn:
  - id: sky-light
    text: explain what lights a shaded surface besides the sun and read that light in the Indirect debug view
  - id: ambient-occlusion
    text: set the radius, intensity and multi-bounce of ambient occlusion and predict which corner darkens most
  - id: reflection-probe
    text: add a reflection probe, fit its box to a room by the room's sizes and bake it until its pictures settle
  - id: wet-floor
    text: set a wet floor with screen-space reflections and name three things it cannot reflect
  - id: times-of-day
    text: write a day script that turns the sun and switch a set of probes for each time of day
since: 0.6.0
status: final
---

Lamps are not the only light in a game. This page makes the shaded sides of a room, its creases and its shiny floor look right with the light that comes from the sky and from the surroundings. You work on one example, a small courtyard, and you end with a script that turns the sun across it through a day. Before you start:

- You have a sky from [the lighting chapter](lighting.md): a `Sky` entity with the Atmosphere source and the **Clear** preset, a `Sun`, and a `Post Process` entity.
- You have the courtyard described below. It is the starting project of this page, offered as a download beside it.
- You can select an entity, rename it, and change its position and scale in the Inspector ([entities](scenes-entities.md)), and you can change the values of a material ([materials](materials.md)).
- You can attach a script to an entity and build it ([scripts in the scene](scripting-scene.md)).

## The courtyard and what is wrong with it

The courtyard is built from the cubes that Strata ships with. A room of plaster walls stands on the ground, with a doorway in its front wall. Inside, a soil bed fills the back right corner and a polished metal sphere stands near the door. Here are the sizes, in meters, that the later steps use.

| Part | Size and place |
| --- | --- |
| Room, inside | 6 wide, 3 high, 4 deep, centered on the origin, walls 0.2 thick, with a roof |
| Doorway | 1.2 wide and 2 high, in the front wall, facing the camera |
| Soil bed | 2 by 0.3 by 1, against the back wall and the right wall |
| Metal sphere | 1 across, **Metallic** 1, **Roughness** 0.1, near the doorway |
| Floor | the `Ground` of the Basic 3D template, dark stone, **Roughness** 0.9 |
| Sun | in front of the doorway, so its light falls through it: turned 70 degrees from +X toward +Z |

Put the Scene view in the doorway, looking in: fly it there, or send the command below.

```json
{ "command": "camera.set", "parameters": { "position": [0, 1.5, 2.6], "target": [0, 0.9, -2] } }
```

Three things look wrong. The inside of the room is as bright as the outside, although a roof covers it. The corners and the foot of the soil bed look flat. The sphere and the floor reflect a sky that the room hides.

Each problem has a tool, and the tools stack. The sky lights every surface from all around. **Ambient occlusion** darkens the sky's light where a corner hides part of the sky.

A **reflection probe** replaces the sky with a picture of the room. **Screen-space reflections** add what the screen shows on top of both. The diagram shows the order in which a shiny surface chooses what it reflects.

```mermaid caption="A shiny surface reflects what the screen shows when it can, then the nearest probe, then the sky." alt="A flow from left to right. The first box is the screen-space reflection of the picture. Where it finds nothing, the flow continues to the box of the reflection probe whose box holds the surface. Where there is none, the flow ends in the sky."
flowchart LR
	S["What the screen shows"] -->|"nothing found"| P["The probe whose box holds the surface"]
	P -->|"no probe"| K["The sky"]
```

## Read the light of the sky

The sun lights a surface from one direction, and a surface that the sun does not reach would be black. The sky fixes that, because it lights every surface from all around. The first active **Sky Light** of the scene is that light. The :term[renderer]{id=renderer} calls it indirect light, since it did not come straight from the sun or a lamp.

:::::steps

1. Show only the indirect light. Open the debug view chip at the top of the Scene view and choose **Indirect**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the chip, which says **Lit**, and choose **Indirect: sky, probe and reflected light only**. A legend appears.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "indirect" } }
   ```

   :::
   ::::

   **You should see:** the picture without the sun. The walls and the ground show the blue-white light of the sky and no shadow of the sun. The inside of the room is lit too, although the roof covers it, because the sky's light does not know where the walls stand.

   **If you do not see it:** the chip still says **Lit**. Open it again and choose the view from its list.

2. Remove the sky and put it back. Select `Sky` and clear the check box beside its name in the Inspector's header.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Clear the box, look at the picture in the **Indirect** view and in the lit view, and tick the box again.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.setActive", "parameters": { "entity": "<the ID of Sky>", "active": false } }
   ```

   A command takes an entity's identifier (ID), not its name: each `<the ID of …>` on this page is what `entity.find` returns for that name.
   :::
   ::::

   **You should see:** with the sky gone, the shaded side of every wall turns almost black and the **Indirect** view loses its light. The sun alone leaves hard black shadows. Enable the sky again before the next step.

   **If you do not see it:** nothing changes. Another active `Sky Light` may exist in the scene, and the first active one is used.

:::::

## Darken the creases with ambient occlusion

Sky light reaches a flat wall from half the sky. A corner sees less of the sky, because the other wall hides part of it, so it should be darker. **Ambient occlusion** (AO) darkens the sky's light by how much of the sky a surface sees. The **Post Process** has it on by default, with three values.

- **Ambient Occlusion Radius**: how far around a surface a hiding object darkens it, in meters. The default is 1.
- **Ambient Occlusion Intensity**: how strongly. The default 1 is the value as measured, 0 is none and a value above 1 darkens more.
- **Ambient Occlusion Multi Bounce**: on by default. A bright surface sends light into its own corner, so white plaster stays light there, while dark soil darkens fully.

<!-- markdownlint-disable MD029 -->
:::::steps

3. Look at the occlusion alone. Open the debug view chip and choose **AO**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **AO: the occlusion that darkens indirect light**. White means nothing hides the sky.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "ao" } }
   ```

   :::
   ::::

   **You should see:** gray bands in every corner of the room, around the foot of the soil bed and under the sphere, and white on open walls. The vertical corner at the back left of the room is a pale gray band, and the foot of the soil bed is darker.

   **If you do not see it:** the whole picture is white. Select `Post Process` and check that **Ambient Occlusion** is on.

   ::figure{id=ao-views variant=ao}

   ::figure{id=ao-views variant=lit}

4. Shrink and enlarge the radius. Select `Post Process` and set **Ambient Occlusion Radius** to 0.25, then to 3, and watch the bands.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type the value in the field and press **Enter**. Return to 1 at the end.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AmbientOcclusionRadius": 0.25 } } }
   ```

   :::
   ::::

   **You should see:** at 0.25 the bands hug the corners tightly. At 3 they spread across the floor and the walls. The engine keeps the radius on screen between 0.3 % and 12 % of the view's height. In a view 1,080 pixels high the band is never thinner than about 3 pixels and never wider than about 130.

   **If you do not see it:** nothing changes. The three fields below **Ambient Occlusion** are inactive when it is off, and the Inspector says so.

5. Compare the plaster corner with the soil corner. Open the **Lit (no debug view)** view, then switch **Ambient Occlusion Multi Bounce** off and on.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Look at the back left corner of the plaster and at the soil bed against the back wall, with the box off and on. Set **Ambient Occlusion Intensity** to 2 and then back to 1.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AmbientOcclusionMultiBounce": false } } }
   ```

   :::
   ::::

   **You should see:** with multi-bounce off, the plaster corner turns darker and looks dirty. With it on, the plaster stays light, and the soil stays dark. Intensity 2 darkens both corners further.

   **If you do not see it:** the two corners look alike. Soil needs a dark base color: check that its **Base Color** is near 0.08, and plaster near 0.8.

:::::
<!-- markdownlint-enable MD029 -->

Two limits matter. AO darkens only the indirect light: the sun has its own shadows, and AO never touches them. And AO is computed from the picture, so it sees only what is on screen. A wall behind the camera darkens nothing. How the engine computes it without history is in [ambient occlusion](../indirect/ao.md).

## Give the room a reflection probe

A shiny surface reflects its surroundings. With the sky as the only source, it reflects the sky everywhere, even inside a room.

A **reflection probe** is an entity that holds a picture of the scene around it. The surfaces inside its box take their light and their reflections from that picture instead of from the sky. To **bake** is to take that picture once, in the editor, and store it as a file. The picture is never a view of the running game. The file is one flat `.hdr` picture of the whole sphere around the probe: Strata has no cube texture asset, and the renderer turns the picture into a cube while the game runs.

The probe has a box, its **Extents**, and the box is not drawn in the Scene view. Strata has no :term[gizmo]{id=gizmo-start} for it, so you fit the box by numbers. **Extents** are half sizes, along the entity's axes, multiplied by the entity's scale. The default 5, 5, 5 is a box 10 m on each side. A room 6 m wide, 3 m high and 4 m deep needs half of each: 3, 1.5 and 2.

The probe's weight falls to zero at the box's faces and grows to full over the **Blend Distance** inside them. A box fitted to the walls would leave the floor and the walls with the sky. So grow each half size by the blend distance: with 0.3, the room needs 3.3, 1.8 and 2.3.

<!-- markdownlint-disable MD029 -->
:::::steps

6. Add the probe. Create an empty entity named `Room Probe` at the center of the room, 1.5 m above the floor, and give it a **Reflection Probe**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **+ ▸ Empty** in the Hierarchy and press **F2** to rename it. Set its **Translation** to 0, 1.5, 0. In the Inspector click **Add Component** and choose **Reflection Probe**. No menu of the Hierarchy creates a probe.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Room Probe", "components": { "Transform": { "Translation": [0, 1.5, 0] }, "ReflectionProbe": {} } } }
   ```

   :::
   ::::

   **You should see:** a **Reflection Probe** section with an empty **Capture**, **Extents** 5, 5, 5, **Blend Distance** 1, **Box Projection** on, **Intensity** 1 and **Priority** 0. The picture does not change, because a probe without a capture does nothing.

   **If you do not see it:** the section is missing. Select the entity again, and check that you added the component to it and not to a wall.

7. Fit the box to the room. Set **Extents** to 3.3, 1.8, 2.3 and **Blend Distance** to 0.3.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type the three numbers in the three fields of **Extents**, then 0.3 in **Blend Distance**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Room Probe>", "component": "ReflectionProbe", "values": { "Extents": [3.3, 1.8, 2.3], "BlendDistance": 0.3 } } }
   ```

   :::
   ::::

   **You should see:** nothing yet. You check the fit after the bake: the reflections show it. A box too large lights the yard outside with the room's picture, and a box too small leaves a strip of wall that reflects the sky.

   **If you do not see it:** the fields refuse a value. **Extents** cannot go below 0.01 m on an axis.

8. Bake the probe. Click **Bake** in the probe's section.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **Bake** and wait a moment. With nothing selected, **Bake Reflection Probes** in the Sky section of the Inspector bakes every active probe at once. Both buttons are disabled while the game plays, because a bake renders the edited scene.
   :::
   :::tab[With a command]

   ```json
   { "command": "lighting.bakeProbes" }
   ```

   :::
   ::::

   **You should see:** **Capture** names a new `.hdr` picture, in a folder of `Assets/Lighting` named after the scene file. The inside of the room is darker and shows the walls' own light, and the sphere and the floor reflect the room. One **Ctrl+Z** undoes the whole bake.

   **If you do not see it:** the button is gray. Stop the game first; a bake needs the edited scene and a :term[graphics card]{id=gpu} (GPU) that draws.

9. Turn **Box Projection** off and on. Walk the Scene view across the doorway while you look at the sphere.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Clear **Box Projection**, move the view left and right, then enable it again.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Room Probe>", "component": "ReflectionProbe", "values": { "BoxProjection": false } } }
   ```

   :::
   ::::

   **You should see:** with the box projection on, the doorway and the walls in the sphere stay where they are as you move, as walls do in a room. Off, the picture reads as if it were infinitely far, and the doorway slides across the sphere.

   **If you do not see it:** both look alike. The sphere is too small on screen: come closer.

10. Cover the yard with a second probe. Create `Yard Probe` at 0, 1.5, 4.2 with **Extents** 4, 1.8, 2.5, **Blend Distance** 0.5 and **Priority** 0. Give `Room Probe` **Priority** 1, and bake both.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Repeat steps 6 and 7 with the new numbers, set the room's **Priority**, select both probes, and press **Bake** or **Bake Reflection Probes**.
    :::
    :::tab[With a command]
    The command below creates the yard probe. Set the room probe's `Priority` with `component.set` as in step 7, and bake with `lighting.bakeProbes`.

    ```json
    { "command": "entity.create", "parameters": { "name": "Yard Probe", "components": { "Transform": { "Translation": [0, 1.5, 4.2] }, "ReflectionProbe": { "Extents": [4, 1.8, 2.5], "BlendDistance": 0.5 } } } }
    ```

    :::
    ::::

    **You should see:** the two boxes overlap by 0.6 m at the doorway. There the room's probe wins, because its **Priority** is higher, and it fades out over its last 0.3 m into the yard's picture. The ground outside the door reflects the yard.

    **If you do not see it:** a seam shows at the door. Raise **Blend Distance** of the room's probe; two probes blend at most.

:::::
<!-- markdownlint-enable MD029 -->

A probe omits two things on purpose: the sun's disk and the highlights of lamps. The sun and the lamps shade every surface themselves, with their shadows. A highlight seen from the probe's center would land in the wrong place on a shiny floor. How probes are gathered, blended and converted is in [reflection probes](../indirect/probes.md).

## Bake again until the light settles

A bake draws what is in the scene now, and the probes' present pictures are part of it, the probe's own included. The first bake saw a room with no probe, so the room's light came from the sky alone. The second bake sees the first picture, which holds light bounced from the walls, and adds one more bounce. The pictures change less with each bake, and they stop changing after a few. The Showcase sample bakes eight times.

<!-- markdownlint-disable MD029 -->
:::::steps

11. Bake both probes a second time.

    ::::tabs{sync=how}
    :::tab[In the editor]
    With nothing selected, click **Bake Reflection Probes** in the Sky section of the Inspector. Compare the room in the **Indirect** view before and after.
    :::
    :::tab[With a command]

    ```json
    { "command": "lighting.bakeProbes" }
    ```

    :::
    ::::

    **You should see:** the room's light changes visibly, brighter in the shaded corners. The earlier pictures go to the project's trash, because a bake replaces only the probe's own capture.

    **If you do not see it:** the room is unchanged. A bake of one probe changes only that probe: bake both.

12. Repeat until two bakes look alike. Compare each result with the one before, in the **Indirect** view.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Bake, look, and bake again. Three to five bakes settle a room of this size.
    :::
    :::tab[With a command]

    ```json
    { "command": "lighting.bakeProbes" }
    ```

    :::
    ::::

    **You should see:** the change shrinks with each bake, until two pictures look alike. Stop there.

    **If you do not see it:** the pictures keep changing. Check that no light or sun is moving while you bake, because a bake takes the scene as it is.

:::::
<!-- markdownlint-enable MD029 -->

After any large change of light, bake again. A moved sun, a new lamp or a changed wall makes the old pictures wrong, and the game never takes them again by itself. The editor takes them, never the running game.

## Make the floor wet

A wet floor is a smooth floor under a thin layer of water. Two numbers of the material make it. The material's `IOR` says how strongly it bends light; for water it is 1.33, and the roughness of a smooth wet surface lies between 0.02 and 0.06.

The `IOR` also sets how much light a surface reflects when you look straight at it. That share is $((n - 1) / (n + 1))^2$, where $n$ is the `IOR`: the square of the difference over the sum. It gives 0.04 for the default 1.5 and about 0.02 for water. Then **Screen Space Reflections** add the things that stand on the floor.

<!-- markdownlint-disable MD029 -->
:::::steps

13. Make the ground wet. Open the material of `Ground` and set `Roughness` to 0.04 and `IOR` to 1.33.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Select `Ground`, open its material in the Inspector and change the two values.
    :::
    :::tab[With a command]

    ```json
    { "command": "material.set", "parameters": { "material": "Materials/Ground.stmat", "properties": { "Roughness": 0.04, "IOR": 1.33 } } }
    ```

    :::
    ::::

    **You should see:** the floor reflects the probe's picture: a smeared copy of the room as the probe saw it from its center. The sphere in it does not sit where the sphere stands, and it stays put when you move the sphere, because a probe's picture holds the scene as baked.

    **If you do not see it:** the floor still looks dull. Check that the roughness is 0.04 and not 0.4.

14. Enable the reflections. Select `Post Process` and enable **Screen Space Reflections**.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Tick **Screen Space Reflections** in the **Reflections** group of the Post Process.
    :::
    :::tab[With a command]

    ```json
    { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "ScreenSpaceReflections": true } } }
    ```

    :::
    ::::

    **You should see:** the sphere and the soil bed appear in the floor, upside down and sharp, and they move when you move the sphere. A new view has no earlier picture to reflect from, so the reflections appear from its second frame.

    **If you do not see it:** the floor is unchanged. At the quality preset Low there are none; use the quality chip of the Scene view.

    ::figure{id=wet-floor variant=off}

    ::figure{id=wet-floor variant=on}

15. Find the roughness limit. Set the floor's `Roughness` to 0.3, 0.45 and 0.6.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Change the value in the material, one number at a time, and watch the sphere's reflection.
    :::
    :::tab[With a command]

    ```json
    { "command": "material.set", "parameters": { "material": "Materials/Ground.stmat", "properties": { "Roughness": 0.45 } } }
    ```

    :::
    ::::

    **You should see:** **Screen Space Reflections Max Roughness** is 0.5 by default, and the reflection fades over the last quarter below it, from 0.375 to 0.5. At 0.3 the reflection is full. At 0.45 it has a share of (0.5 − 0.45) ÷ 0.125, which is 0.4. At 0.6 there is none, and the probe alone reflects. Return to 0.04.

    **If you do not see it:** the reflection stays at 0.6. Check **Screen Space Reflections Max Roughness** of the `Post Process`: it may be above 0.6.

16. Meet the limits. Move the Scene view low over the floor, beside the sphere, and then until the sphere leaves the picture.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Fly the camera down and to the side, then look away from the sphere.
    :::
    :::tab[With a command]
    The first command looks at the sphere from low beside it, and the second turns the view away from it, toward the left wall.

    ```json
    { "command": "camera.set", "parameters": { "position": [-2.5, 0.4, 1.5], "target": [-1.2, 0.3, 0.8] } }
    { "command": "camera.set", "parameters": { "position": [-2.5, 0.4, 1.5], "target": [-3, 0.3, 0] } }
    ```

    :::
    ::::

    **You should see:** from the side, the sphere's reflection is a crescent. The screen holds only the part of the sphere that the camera sees, and the probe or the sky fills the place of its back. Turned to the left wall, the picture holds no sphere, and the floor reflects only the walls: its reflection is gone with it. A glass window would get no screen reflection at all.

    **If you do not see it:** the reflection of the sphere stays whole. The sphere is still on screen, perhaps through the doorway: move further.

17. Compare Medium with High. Open the quality chip of the Scene view and choose **Medium**, then **High**.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Click the chip, which names the preset, choose **Medium**, look, and choose **High**.
    :::
    :::tab[With a command]

    ```json
    { "command": "viewport.setSettings", "parameters": { "quality": "high" } }
    ```

    :::
    ::::

    **You should see:** Medium traces at half the resolution and needs temporal anti-aliasing (TAA), so edges of reflections look softer. High traces every pixel and needs no history. The [quality chapter](quality.md) teaches the presets and TAA. Return the chip to **Project**.

    **If you do not see it:** at Medium no reflection appears. The `Post Process` must use TAA for Medium.

:::::
<!-- markdownlint-enable MD029 -->

Only what is on screen can be reflected. That is the cost of the method, and the reason for the fallback in the diagram: where the screen has nothing to show, the probe and the sky reflect as before. AO never darkens what a screen reflection found, because the ray already saw what blocks the light.

## Give the courtyard a day

A probe's picture is fixed, and a day moves the sun. A game that shows several times of day gives each time its own set of probes and switches between the sets. First, learn how a script turns the sun. The `OpenWorld` sample's `DayNight.h` does it, and you read it in parts.

:::question
The excerpts use classes, `override` and calls such as `std::fmod(`: read [classes](../basics/programming-3.md) and [inheritance](../basics/cpp-classes.md) first if they are new.
:::

The first part is the frame update. It advances the hour by the frame's delta time and asks `Apply` to move the sun.

```cpp src="Samples/OpenWorld/Scripts/DayNight.h#L31-L35" symbol="DayNight::OnUpdate"
void OnUpdate(float deltaTime) override
{
	TimeOfDay = std::fmod(TimeOfDay + deltaTime * 24.0f / std::max(DayLengthSeconds, 1.0f), 24.0f);
	Apply(false);
}
```

The day is `DayLengthSeconds` long, 600 by default. An hour passes in 25 seconds, and the sun's elevation changes by 15 degrees per hour, so 0.6 degrees per second.

The next part turns the sun. The function `GetElevation` computes the elevation: the hour minus 6, divided by 12 and multiplied by 180 degrees. That gives 45 degrees at 9 o'clock and 90 at noon. The script moves the light only when the angle has moved by `StepDegrees`, 0.25 degrees: at 0.6 degrees per second that is about every 0.4 seconds. The sun's shadow cascades are drawn again only when the light moved, so the steps save work.

```cpp src="Samples/OpenWorld/Scripts/DayNight.h#L40-L59"
void Apply(bool force)
{
	const float angle = GetElevation();
	if (!force && std::abs(angle - m_AppliedAngle) < StepDegrees)
		return;
	m_AppliedAngle = angle;

	const float height = std::sin(glm::radians(angle)); // The sun's: 1 at noon, below 0 at night
	// By day the sun, at night the moon across the sky from it (its elevation the sun's depth below the horizon): half a
	// turn on, rising after sunset (the sun at 180 to 270 degrees) and setting before sunrise (the sun at -90 to 0).
	const bool night = height < 0.0f;
	const float lightAngle = night ? std::fmod(angle + 180.0f, 360.0f) : angle;
	// The light shines along its -Z: turned toward the azimuth, then down by the elevation. It stays at least 2 degrees
	// up (its shadows stay short enough to draw) and fades out from there to the horizon instead, where the atmosphere
	// has already turned it a dim red, and the sky, lit by it, darkens with it.
	const glm::quat rotation = glm::angleAxis(glm::radians(Azimuth), glm::vec3(0.0f, 1.0f, 0.0f))
		* glm::angleAxis(glm::radians(-std::clamp(lightAngle, 2.0f, 178.0f)), glm::vec3(1.0f, 0.0f, 0.0f));
	GetTransform().SetRotation(rotation);
	const float fade = std::clamp(std::sin(glm::radians(lightAngle)) / 0.035f, 0.0f, 1.0f);
	GetEntity().SetProperty("DirectionalLight", "Intensity", (night ? MoonIntensity : SunIntensity) * fade);
```

1. **Lines 43–45:** a change smaller than a step returns at once, so most frames do nothing here.
2. **Lines 50–51:** below the horizon the same light becomes the moon, opposite the sun.
3. **Lines 55–57:** the light is turned toward the azimuth and then down by the elevation, and never lower than 2 degrees above the horizon, so its shadows stay short enough to draw.
4. **Lines 58–59:** near the horizon the intensity fades, and `SetProperty` writes it into the `DirectionalLight` component.

Under the Atmosphere source the sky follows the light by itself. The sky's own light refreshes at every half degree of the sun, computed over a few frames. The last part lights the fires, found by their tag.

```cpp src="Samples/OpenWorld/Scripts/DayNight.h#L61-L69"
const bool lit = height < 0.1f; // From just before sunset to just after sunrise
if (lit != CampfiresLit || force)
{
	CampfiresLit = lit;
	for (Strata::Entity fire : Strata::Scene::FindEntitiesByTag("Campfire"))
		fire.SetProperty("PointLight", "Intensity", lit ? CampfireIntensity : 0.0f);
	if (!force)
		Strata::Log::Info("OpenWorld: campfires ", lit ? "lit" : "out", " at ", static_cast<int32_t>(TimeOfDay), ":00");
}
```

`FindEntitiesByTag("Campfire")` returns every entity with that tag, and the loop sets the intensity of each `PointLight`. The fires burn from shortly before sunset to shortly after sunrise, while the sun's height is below 0.1.

The sample's values are small: a sun of 3 :term[lux]{id=lux}, a moon of 0.05 lux and a fire of 6 :term[cd]{id=candela}. They agree with one another. Automatic exposure and the atmosphere, which follow the sun, hide the scale.

The courtyard has the real sun of 120,000 lux. The exercise at the end of this page sets the sun to 120,000, the moon to about 0.2 lux in the code, and the fire in candela as [the lamps chapter](lamps.md) teaches.

Now the probes. The Showcase sample's `Outpost` script switches sets of probes. It first reads the capture of each probe and asks for its load progress. The first call loads the whole picture and keeps it while the scene plays, so a switch never waits.

```cpp src="Samples/Showcase/Scripts/Outpost.cpp#L154-L172" symbol="Outpost::RequestCaptures"
void Outpost::RequestCaptures()
{
	CapturesFound = 0;
	CapturesResident = 0;
	for (size_t index = 0; index < c_ProbeFields.size(); index++)
	{
		const Entity probe = GetProbe(static_cast<StationId>(index / 2), index % 2 == 1);
		m_Captures[index] = AssetHandle();
		if (!probe.IsValid())
		{
			Log::Warn("Showcase: no entity '", c_ProbeFields[index], "'");
			continue;
		}
		m_Captures[index] = probe.GetProperty<AssetHandle>("ReflectionProbe", "Capture").value_or(AssetHandle());
		// The first call loads all of the capture and keeps it while the scene plays, so a switch never waits for a load.
		if (m_Captures[index] && Assets::GetLoadProgress(m_Captures[index]) >= 0.0f)
			CapturesFound++;
	}
}
```

1. **Line 167:** the probe's `Capture` property is read as an :term[asset handle]{id=asset-handle}.
2. **Lines 168–169:** `Assets::GetLoadProgress` starts the load and returns a number from 0 to 1, or less than 0 for an unknown asset.

`SetProbes` switches one station's probes on or off and writes their priority.

```cpp src="Samples/Showcase/Scripts/Outpost.cpp#L205-L218" symbol="Outpost::SetProbes"
void Outpost::SetProbes(StationId station, bool active, bool raised)
{
	for (const bool hut : { false, true })
	{
		Entity probe = GetProbe(station, hut);
		if (!probe.IsValid())
			continue;
		probe.SetActive(active);
		// While both stations are on, the new one's captures win where they are converted; until then the old one lights
		// the boxes, so they never fall to the sky.
		const int32_t priority = (hut ? c_HutPriority : c_YardPriority) + (raised ? 1 : 0);
		probe.SetProperty("ReflectionProbe", "Priority", priority);
	}
}
```

1. **Line 212:** `SetActive` enables or disables the probe entity.
2. **Lines 213–216:** a raised station gets one more priority, so its pictures win where both stations' boxes overlap.

`SwitchProbes` keeps the old probes on for a second.

```cpp src="Samples/Showcase/Scripts/Outpost.cpp#L247-L267" symbol="Outpost::SwitchProbes"
void Outpost::SwitchProbes(StationId station, bool immediately)
{
	const int32_t index = static_cast<int32_t>(station);
	if (!immediately && index == Station)
		return;
	// At most two stations are on: a switch while another one's hold runs ends that hold first.
	EndProbeHold();
	if (immediately)
	{
		for (const StationId other : { StationId::Dawn, StationId::Golden, StationId::Dusk })
			SetProbes(other, other == station, false);
	}
	else
	{
		m_HoldStation = Station;
		m_HoldLeft = ProbeHoldSeconds;
		SetProbes(station, true, true);
	}
	Station = index;
	Log::Info("Showcase: station ", GetStationName(station));
}
```

1. **Lines 254–258:** an immediate switch turns every other station off.
2. **Lines 259–264:** a normal switch remembers the old station and `ProbeHoldSeconds` (1), and turns the new probes on with a raised priority.

The renderer prepares a probe's picture over a frame or two, and it leaves a probe out while that runs. With the old probes still on, the boxes never fall back to the sky. When the second ends, the old probes go off.

Now make the second set. A set needs its own baked pictures, taken with the sun, the fog and the lamps of its time, and with only its own probes active. A bake renders the scene as it is and draws every active probe's picture, so a second set that stays active leaks its light into the first. The day script does not run while you bake, because a bake is refused while the game plays: you turn the sun by hand.

<!-- markdownlint-disable MD029 -->
:::::steps

18. Name the first set and copy it. Rename the probes `Room Noon` and `Yard Noon`, select both and press **Ctrl+D**, and name the copies `Room Dusk` and `Yard Dusk`.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Select a probe in the Hierarchy, press **F2** and type the name. Duplicate both with **Ctrl+D**, and rename the copies.
    :::
    :::tab[With a command]

    ```json
    { "command": "entity.duplicate", "parameters": { "entities": [ "<id of Room Noon>", "<id of Yard Noon>" ] } }
    ```

    :::
    ::::

    **You should see:** four probes in the Hierarchy. The copies name the same capture as the originals, which is fine until the next bake gives them their own.

    **If you do not see it:** the copies are named `Room Noon (1)` and `Yard Noon (1)`. Rename them: the day script finds them by name.

19. Turn the sun to dusk and disable the noon set. Select nothing and press **Golden Hour** in the Sky section, then clear the check boxes of `Room Noon` and `Yard Noon`.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Press **Golden Hour**, and clear the active boxes of the two noon probes.
    :::
    :::tab[With a command]

    ```json
    { "command": "lighting.applySkyPreset", "parameters": { "preset": "GoldenHour" } }
    ```

    :::
    ::::

    **You should see:** a low warm sun and long shadows, and only the dusk probes lit by the bake to come.

    **If you do not see it:** the sun stays high. The preset keeps the azimuth and sets the elevation to 6 degrees: look at the `Sun` entity.

20. Bake the dusk set until it settles, as in steps 11 and 12, then reverse the two sets.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Click **Bake Reflection Probes** until the pictures settle. Press **Clear** in the Sky section, enable the noon probes, disable the dusk probes, and bake the noon set the same way.
    :::
    :::tab[With a command]

    ```json
    { "command": "lighting.bakeProbes" }
    ```

    :::
    ::::

    **You should see:** each set has its own pictures. Switch the sets by hand with the active boxes: the noon set under the **Clear** sun, the dusk set under **Golden Hour**.

    **If you do not see it:** the noon room looks orange. A dusk probe was still active when you baked noon: disable it and bake again.

:::::
<!-- markdownlint-enable MD029 -->

## Result

You have a courtyard whose room is lit by its own surroundings, whose creases darken, whose floor is wet and whose probes follow the time of day. The day script from the exercise below moves the sun, and the probe sets switch with it.

Put the Scene view in the doorway at noon and at dusk, as the pictures show.

::compare{id=result}

## Variations

- **An open yard.** Turn **Box Projection** off and give the box generous **Extents**: what the probe saw is far away, and a box fitted to nothing would mislead the reflections.
- **A cave.** Fit the box to the cave's walls with **Box Projection** on, and bake with the cave's lamps lit, because a bake draws the lamps' light but not their highlights.
- **A probe for each room of a house.** One probe per room with its own box, bake all of them together, and give the smaller rooms a higher **Priority** where the boxes overlap. The smaller box wins on a tie.
- **Global illumination.** Bounce light traced in the world, instead of baked, is the subject of [global illumination](gi.md).

## Summary

- The first active sky light lights every surface from all around, and the **Indirect** view shows that light alone.
- Ambient occlusion darkens only the indirect light, sees only the screen, and with multi-bounce keeps white plaster light while soil darkens.
- A reflection probe is a picture baked in the editor: fit its **Extents**, which are half sizes, bake until the pictures settle, and use **Box Projection** in rooms.
- A wet floor is **IOR** 1.33, **Roughness** 0.02 to 0.06 and **Screen Space Reflections**, which reflect only what the screen shows and nothing on transparent surfaces.
- A day script turns the sun in steps, and each time of day has its own probe set, switched with `SetActive` while the old set stays on for a second.

## Check yourself

1. In the **Indirect** view the shaded side of a wall is bright. What lights it?

   :::answer{tests="sky-light"}
   The sky. The first active **Sky Light** lights every surface from all around, so a side the sun does not reach still gets light, and the view shows that light without the sun.
   :::

2. A room is 8 m wide, 2.5 m high and 5 m deep, with a probe at its center. What are its **Extents**, if the entity's scale is 1? What if the scale is 2?

   :::answer{tests="reflection-probe"}
   **Extents** are half sizes: 4, 1.25 and 2.5. With a scale of 2 the box doubles, so the fields must be halved again: 2, 0.625 and 1.25.
   :::

3. Why does a white corner look lighter than a soil corner with the same shape?

   :::answer{tests="ambient-occlusion"}
   Multi-bounce lets a bright surface send light into its own corner, so plaster keeps its light there. Dark soil sends little, so it darkens fully.
   :::

4. The sun's shadow on a wall is not darkened any further by AO. Why?

   :::answer{tests="ambient-occlusion"}
   AO darkens only the indirect light. The sun's light has its own shadows, so ambient occlusion never touches it.
   :::

5. A floor has **Roughness** 0.5 and **Max Roughness** is 0.5. Does it show a screen reflection? Name two other things it cannot reflect.

   :::answer{tests="wet-floor"}
   No: the fade runs from 0.375 to 0.5, and at 0.5 it reaches zero. A screen reflection also cannot show what is off screen or behind another object, and glass gets none.
   :::

6. You bake a dusk set while the noon probes are active. What goes wrong?

   :::answer{tests="times-of-day reflection-probe"}
   A bake draws every active probe's picture, so the noon light leaks into the dusk captures. Bake each set with the sun turned to its hour and only its own probes active.
   :::

## Exercises

1. **Basic.** The yard probe has **Extents** 4, 1.8, 2.5 and sits at 0, 1.5, 4.2. Between which values of z does its box reach?

   :::answer{tests="reflection-probe"}
   The box is 2.5 m deep to each side of the entity: 4.2 − 2.5 = 1.7 and 4.2 + 2.5 = 6.7. The room's box ends at z = 2.3, so they overlap from 1.7 to 2.3, which is 0.6 m.
   :::

2. **Medium.** The day script's hour 15 gives which elevation, and which light does the script write at hour 21?

   :::answer{tests="times-of-day"}
   At hour 15 the elevation is (15 − 6) ÷ 12 × 180 = 135 degrees, the sun on its descending side. At hour 21 it is 225 degrees, below the horizon, so the script writes the moon's intensity, with the light across the sky from the sun.
   :::

3. **Hard.** Port the day and night script to the courtyard. Put `DayNight` on the `Sun`, set the sun to 120,000 lux, the moon to about 0.2 lux in the code, and tag a point light `Campfire` with 100 cd.

   :::answer[Worked solution]{tests="times-of-day" solution="tutorials/make/reflections/exercise-1.tutorial.json"}
   The solution creates the class, replaces its file with the port, builds it, attaches it to the `Sun`, adds the tagged fire and steps the game. Its download holds two commands files and the port, `Scripts/DayNight.cpp`. The commands write no file: run the first, copy the port over the same file of your project, then run the second. The port changes three values of `DayNight.h`: `SunIntensity` is 120000, the moon is a constant of 0.2 in the code, and `CampfireIntensity` is 100. At 21:00 the moon is at 45 degrees on the far side, and the fire is on.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RendererComponents.h`: the `ReflectionProbe` component and the ambient occlusion and reflection fields of the `PostProcess`.
- `StrataEditor/src/Editor/EditorLightingCommands.cpp`: the command `lighting.bakeProbes`.
- `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp`: how the renderer gathers, ranks and converts probes.
- `Strata/shaders/Effects/ScreenSpaceReflectionsSpatial.comp.slang`: the screen-space trace of the High preset.
- `Samples/OpenWorld/Scripts/DayNight.h` and `Samples/Showcase/Scripts/Outpost.cpp`: the two scripts of this page.
- `Docs/Manual/Lighting.md`: the engine's own guide to probes, reflections and ambient occlusion.

## Further reading

- Jimenez, Wu, Pesce and Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion": the ground-truth ambient occlusion the engine follows; advanced.
- Lagarde and Zanuttini, "Local Image-based Lighting With Parallax-corrected Cubemaps": the box projection of a probe; advanced.
- The Strata manual on lighting, in the `Docs/Manual` folder of the engine: every value of this page in one place; beginner.
