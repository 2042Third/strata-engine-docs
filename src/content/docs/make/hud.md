---
id: make/hud
title: "HUDs: text, score and bars"
description: "Give Coin Run a coin count, a timer and a time bar on a canvas that keeps its layout on every screen, and drive them from a script."
kind: tutorial
size: M
tracks: [G, B]
needs: [make/sound]
time: 60
learn:
  - id: canvas-scaling
    text: explain how a canvas scales a layout made for its reference resolution to any screen
  - id: anchors
    text: choose anchors, a pivot and an alignment that keep a HUD element in its corner
  - id: build-hud
    text: build a HUD from texts, a sliced panel and a Filled bar that never takes the game's clicks
  - id: drive-hud
    text: write a script that sets a text, a bar's fill amount and a color from the game's state
  - id: check-screens
    text: compare a HUD at three aspect ratios in the Game view
since: 0.4.0
status: final
---

## What you will make

Coin Run gets a heads-up display (HUD): the coins left at the top left, the seconds left at the top right, and a bar
along the bottom that shrinks while time runs out. The layout keeps its place on every window shape.

::figure{id=result}

## What you need

- The end of [Sound](sound.md): the rolling ball, the trigger coins with their sound, the bump and the music. Download
  the checkpoint of its last step, or continue your own project.
- Coins tagged `Coin`. `CoinPlacer` makes them from the coin :term[prefab]{id=prefab-make} only during play: to check,
  press **Play**, select a `Coin` in the Hierarchy and read its **Tag**, then press **Stop**.
- One image: `button_square_flat.png` from the `Samples/ThirdPerson/Assets/UI/` folder of the release. It is a square of
  64 by 64 pixels from Kenney's user interface (UI) pack, in the public domain (:term[CC0]{id=cc0}), credited in that sample's `CREDITS.md`. Import it
  into a new folder `UI`, as you did in [Assets](assets.md), so that it becomes `UI/button_square_flat.png`. The
  command is `asset.import` with
  `{"file": "<release folder>/Samples/ThirdPerson/Assets/UI/button_square_flat.png", "directory": "UI"}`.
- About an hour.

## Make the canvas and the corner texts

A window is 1280 by 720 pixels on a laptop and 2560 by 1080 on a wide monitor. A box 100 pixels wide fills 8 % of the
first and 4 % of the second. A HUD drawn in pixels would look different on each screen: too small on one, in the wrong
place on the other.

Strata draws a HUD on a **canvas**: the root of a user interface that Strata draws over the screen, or placed in the
world as a sign. Every element of the HUD is a child of the canvas.

You lay the HUD out once, on an imaginary screen of a fixed size. That size is the canvas's **reference resolution**,
1920 by 1080 canvas units by default. A canvas unit is a unit of your layout, not a pixel.

The **scale mode** of a canvas decides how canvas units turn into pixels. The default, **Scale With Screen**, picks a
scale (pixels per canvas unit) from the size of the screen, so the layout keeps its proportions.

:::example
A 1280 by 720 window is two thirds of 1920 by 1080 in both directions, so the scale is 0.667. A text 36 units high is
24 pixels high, and a text 24 units from the edge is 16 pixels from it.

A 2560 by 1080 window is wider. Its width asks for a scale of 1.333 and its height for 1.0. The canvas's **Match Width
Or Height** is 0.5 by default, which takes the middle: the square root of $1.333 \times 1.0$, which is 1.155. The canvas
then measures 2217 by 935 units, because $2560 / 1.155 = 2217$ and $1080 / 1.155 = 935$.
:::

Each element sits on a rect, a rectangle placed inside its parent's rectangle. The rect has anchors, a pivot, a position
and a size. The anchors are two points of the parent, written as fractions: (0, 0) is the top-left corner and (1, 1)
the bottom-right corner. The pivot is the point of the rect itself that lies on the anchor point: (0, 0) is its top-left
corner, (0.5, 0.5) its middle.

The position moves the pivot away from the anchor point, in canvas units, with +Y pointing down. The size is the rect's
width and height.

:::example
Anchors (0, 0), pivot (0, 0), position (24, 24) and size (360, 48) put the rect's top-left corner 24 units right of and
24 units below the canvas corner, on every screen. With the pivot at the default (0.5, 0.5), the same position puts the
rect's middle there. Then 180 of its 360 units hang out of the screen on the left, and a text centred in it is cut.
:::

:::::steps

1. Make the canvas first: it is the root of the HUD.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press the **+** button of the Hierarchy and choose **UI**, then `Canvas`. Rename it `HUD`. In the Inspector, **UI Canvas**
   shows **Render Mode** Screen Space, **Scale Mode** Scale With Screen and **Reference Resolution** 1920 by 1080:
   keep them.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "canvas", "name": "HUD" } }
   ```

   :::
   ::::

   **You should see:** the entity `HUD` in the Hierarchy. Nothing is drawn yet, because the canvas has no elements.

   **If you do not see it:** the menu closed before you chose an item. Open the **+** menu again.

2. Look at the canvas flat. The viewport can show a canvas on its own, at its reference shape, with handles to
   move its elements.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `HUD`. Enable the **2D** chip and the **Game UI** chip in the row of chips above the viewport.
   :::
   :::tab[With a command]

   ```json
   { "command": "selection.set", "parameters": { "entities": ["<HUD id>"] } }
   { "command": "viewport.setSettings", "parameters": { "canvasMode": true, "gameUI": true } }
   ```

   The flat view shows only in the editor's window, not in `viewport.capture`.

   :::
   ::::

   **You should see:** the Scene view as a 16:9 rectangle between dark bands, the canvas at its reference shape: the
   level through the game's camera, with nothing drawn on it yet.

   **If you do not see it:** no canvas is selected. Click `HUD` in the Hierarchy first.

   ::figure{id=canvas-2d}

3. Make the coin count. A new text is centred in its rect, so a count in a corner needs a left alignment.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `HUD` and choose **Create Child ▸ UI ▸ Text**. Rename it `CoinText`. A **+** menu would make a second
   canvas, because it always creates at the top level. In the Inspector, **UI Rect** has an **Anchors** button: open
   it, tick **Position** (off by default, so a preset keeps the rect where it is), keep **Pivot** ticked and choose
   `Top Left`.

   Set **Position** to 24 and 24 and **Size** to 360 and 48. In **UI Text** set **Text** to
   `Coins left: 5`, **Font Size** to 36 and **Alignment** to Left.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<HUD id>", "name": "CoinText", "text": "Coins left: 5", "anchor": "topLeft", "position": [24, 24], "size": [360, 48] } }
   { "command": "component.set", "parameters": { "entity": "<CoinText id>", "component": "UIText", "values": { "FontSize": 36, "Alignment": "Left" } } }
   ```

   :::
   ::::

   **You should see:** `Coins left: 5` in the top-left corner of the canvas, starting 24 units from the edge.

   **If you do not see it:** the text is in the middle. The preset ran with **Position** off, so the rect did not move
   onto its anchors. Choose `Top Left` again with **Position** ticked.

4. Make the timer. Do the same at the top right. The pivot of a right-hand preset is the rect's right edge, so a
   position of minus 24 keeps the same distance from the edge.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `HUD` and choose **Create Child ▸ UI ▸ Text**. Rename it `TimerText`. Tick **Position**, choose `Top Right`, and set **Position** to -24 and 24, **Size** to 360 and 48. Set **Text** to `Time: 60`, **Font Size** to 36
   and **Alignment** to Right.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<HUD id>", "name": "TimerText", "text": "Time: 60", "anchor": "topRight", "position": [-24, 24], "size": [360, 48] } }
   { "command": "component.set", "parameters": { "entity": "<TimerText id>", "component": "UIText", "values": { "FontSize": 36, "Alignment": "Right" } } }
   ```

   :::
   ::::

   **You should see:** `Time: 60` against the right edge, level with the coin count.

   **If you do not see it:** the text starts at the middle of the screen. Its **Alignment** is still Center, or the
   preset ran without **Position**.

:::::

::checkpoint{stage=1}

::figure{id=corner-texts}

## Add the panel and the time bar

Text over a bright level can be hard to read, so a panel goes behind the two texts. A panel is an image, and an image
can be stretched. A plain picture stretched to 1920 by 90 units would smear its corners.

A **nine-slice** (a sliced image) cuts the picture into nine parts with four border lines: the four corners keep their
size, and the edges and the middle stretch. A 64 by 64 square with borders of 12 texels, a texel being a pixel of the
picture, keeps four corners of 12 by 12 at any panel size.

The panel also brings a trap. An image is hit by the pointer by default, and the game's own mouse code never sees a
click that lands on the UI. A HUD never needs
clicks, so the canvas turns **Receives Input** off: it stays drawn but is never hit or navigated. The menus of
[Menus](menus.md) keep it on.

The bar for the time left is a stretched element too, along the bottom edge. Along a stretched axis the rect's size is
added to the distance between the two anchors. With anchors 0 and 1 over a canvas 1920 units wide, the distance is 1920
units. A size of 0 fills it, and a size of -80 gives a rect 1840 units wide with 40 units of margin on each side. The
editor shows the same rect as **Left** and **Right** margins of 40.

An image of type **Filled** shows only a part of itself, cut along a direction, and its **Fill Amount** from 0 to 1 says
how much: 0.25 shows the left quarter of a left-to-right bar.

:::::steps

1. Make the backdrop. The panel stretches along the top edge: the left and right anchors differ and the vertical
   one is a point.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `HUD` and choose **Create Child ▸ UI**, then `Panel`. Rename it `Backdrop`. Open **Anchors**, tick **Position**
   and choose `Top Stretch`. **UI Rect** now shows **Left** and **Right** margins instead of a position and size.

   Set both to 0, **Pos Y** to 0 and **Height** to 90. In **UI Image** set **Type** to Sliced, **Texture** to
   `button_square_flat`, **Slice Borders** to 12 in all four fields and **Color** to a dark blue gray, 0.1, 0.12, 0.18, with an alpha of 0.85. Drag `Backdrop` above
   `CoinText` in the Hierarchy.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "panel", "parent": "<HUD id>", "name": "Backdrop", "anchor": "topStretch", "size": [0, 90] } }
   { "command": "component.set", "parameters": { "entity": "<Backdrop id>", "component": "UIImage", "values": { "Type": "Sliced", "Texture": "<button_square_flat id>", "SliceBorders": [12, 12, 12, 12], "Color": [0.1, 0.12, 0.18, 0.85] } } }
   { "command": "entity.setParent", "parameters": { "entity": "<Backdrop id>", "parent": "<HUD id>", "index": 0 } }
   ```

   :::
   ::::

   **You should see:** a dark band across the top, with the white texts clear on it. Make it taller in the Inspector: the corners keep their shape.

   **If you do not see it:** the texts are hidden. Elements draw in Hierarchy order, parents before children and later
   siblings on top, so a panel below the texts covers them. Drag it to the first place.

2. Stop the HUD taking clicks. The canvas, not the panel, decides whether the HUD is hit.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `HUD` and clear **Receives Input** in **UI Canvas**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<HUD id>", "component": "UICanvas", "values": { "ReceivesInput": false } } }
   ```

   :::
   ::::

   **You should see:** no change in the picture. A click on the band now reaches the game.

   **If you do not see it:** you cleared another box. Read the label beside it: it must say **Receives Input**.

3. Make the time bar along the bottom edge.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Right-click `HUD` and choose **Create Child ▸ UI**, then `Image`. Rename it `TimeBar`. Open **Anchors**, tick **Position**
   and choose `Bottom Stretch`. Set **Left** and **Right** to 40, **Pos Y** to -20 and **Height** to 24. In **UI
   Image** set **Type** to Filled, **Fill Amount** to 0.6 and **Color** to a warm yellow.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "image", "parent": "<HUD id>", "name": "TimeBar", "anchor": "bottomStretch", "position": [0, -20], "size": [-80, 24] } }
   { "command": "component.set", "parameters": { "entity": "<TimeBar id>", "component": "UIImage", "values": { "Type": "Filled", "FillAmount": 0.6, "Color": [0.95, 0.75, 0.2, 1] } } }
   ```

   :::
   ::::

   **You should see:** a yellow bar along the bottom, 40 units from each side, filled for three fifths of its length from
   the left.

   **If you do not see it:** the bar is white and full. **Type** is still Simple. Choose Filled.

:::::

::checkpoint{stage=2}

::figure{id=panel-and-bar}

## Drive the HUD from a script

The HUD shows numbers that never change until a script writes them. A script finds each element by its name and sets
its text, its color and the fill of the bar. You write one :term[script class]{id=script-class}, `CoinHud`.

Every frame, `CoinHud` counts the entities tagged `Coin`, reads the time since play began from `Time` and writes both. Setting a
text to what it already shows costs nothing, because Strata changes the text component only when the text differs. A
HUD may therefore write all its texts every frame.

:::question
What is a class that derives from another? See [C++ classes](../basics/cpp-classes.md): `CoinHud` derives from `Script`.
:::

The file starts with its headers. The line `using namespace Strata;` lets the code write `Script` for
`Strata::Script`.

```cpp src="book:tutorials/make/hud/CoinHud.cpp#L1-L8"
#include "StrataScript/StrataScript.h"

#include <cmath>
#include <string>

using namespace Strata;

// The HUD of Coin Run: the coins left, the seconds left and a bar for the time left.
```

The script's first part keeps the field and writes the two texts and the bar.

```cpp src="book:tutorials/make/hud/CoinHud.cpp#L9-L32"
class CoinHud : public Script
{
public:
	float TimeLimit = 60.0f; // Seconds the player has

	void OnCreate() override { FindParts(); }
	void OnReload() override { FindParts(); }

	void OnUpdate(float) override
	{
		const int coinsLeft = static_cast<int>(Scene::FindEntitiesByTag("Coin").size());
		m_CoinText.GetUI().SetText("Coins left: " + std::to_string(coinsLeft));

		const float timeLeft = glm::max(TimeLimit - static_cast<float>(Time::GetElapsedTime()), 0.0f);
		m_TimerText.GetUI().SetText("Time: " + std::to_string(static_cast<int>(std::ceil(timeLeft))));
		m_TimeBar.SetProperty("UIImage", "FillAmount", timeLeft / TimeLimit);

		const bool low = timeLeft < 10.0f;
		if (low != m_Low)
		{
			m_Low = low;
			m_TimerText.GetUI().SetColor(low ? glm::vec4(1.0f, 0.3f, 0.2f, 1.0f) : glm::vec4(1.0f));
		}
	}
```

1. **Line 12:** the time the player has is a field, so you can change it in the Inspector without a build.
2. **Lines 14-15:** after a :term[hot reload]{id=hot-reload} the engine calls `OnReload` instead of `OnCreate`, so both find the parts again.
3. **Line 19:** `Scene::FindEntitiesByTag` lists the coins still in the scene, and its size is the count.
4. **Line 24:** the bar's fill is a property of the `UIImage` component, set by name.
5. **Lines 26-31:** the color changes only when the state changes, once at ten seconds left.

:::note
`SetProperty` takes its type from the value you give it, and the software development kit (:term[SDK]{id=sdk}) converts most of
them. A `double`, such as the literal `0.5` or the result of `Time::GetElapsedTime()`, does not compile. Write `0.5f`,
cast to `float`, or name the type: `SetProperty<float>(...)`.
:::

The second part keeps the entities it found, and registers the field.

```cpp src="book:tutorials/make/hud/CoinHud.cpp#L34-L51"
private:
	void FindParts()
	{
		m_CoinText = Scene::FindEntityByName("CoinText");
		m_TimerText = Scene::FindEntityByName("TimerText");
		m_TimeBar = Scene::FindEntityByName("TimeBar");
	}

	Entity m_CoinText;
	Entity m_TimerText;
	Entity m_TimeBar;
	bool m_Low = false;
};

ST_SCRIPT_CLASS(CoinHud)
{
	ST_SCRIPT_FIELD(TimeLimit);
}
```

1. **Lines 37-39:** `Scene::FindEntityByName` returns the entity with that name, so the names you gave in the Hierarchy matter.
2. **Line 45:** `m_Low` remembers whether the timer is already red.
3. **Lines 48-51:** `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD` register the class and its field, as on [Your first script](first-script.md).

`SetValue` moves only a slider or a toggle and fails on an image, so the bar is set through `SetProperty`.

:::::steps

1. Create, build and attach the script. Name the elements as the script expects: `CoinText`, `TimerText`, `TimeBar`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ New Script...** and make a class `CoinHud`. In a text editor, replace all of the new file's text
   with the three listings above and save it. Build with **Scripts ▸ Build Scripts** (Ctrl+B). Select `HUD` and use **Add Component ▸ Script** to attach `CoinHud`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "CoinHud" } }
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<HUD id>", "class": "CoinHud", "fields": { "TimeLimit": 60 } } }
   ```

   :::
   ::::

   No command writes a file's text: between the first two commands, replace the text of `Scripts/CoinHud.cpp` in a
   text editor. Checkpoint 3's download, at the end of this section, holds the whole file.

   **You should see:** the build finish without errors, and `CoinHud` on the `HUD` entity.

   **If you do not see it:** the :term[Problems panel]{id=problems-panel} lists the error. A `double` given to `SetProperty` is the usual one.

2. Play and roll the ball into a coin.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play** (Ctrl+P), click the Game view and roll the ball with the keys of [Input](input.md): **S** held for
   about a second rolls it into the first coin. Then wait until less than ten seconds are left.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "paused": true } }
   { "command": "input.sequence", "parameters": { "events": [{ "step": 0, "key": "S", "action": "tap", "steps": 150 }], "steps": 180 } }
   { "command": "component.get", "parameters": { "entity": "<CoinText id>", "component": "UIText" } }
   { "command": "play.step", "parameters": { "steps": 2910 } }
   { "command": "component.get", "parameters": { "entity": "<TimerText id>", "component": "UIText" } }
   { "command": "play.stop" }
   ```

   `input.sequence` holds **S** for 150 :term[fixed steps]{id=fixed-step} of the paused game and runs 180, 3 seconds: `CoinText` reads
   `Coins left: 4`. At 51.5 seconds `TimerText` reads `Time: 9`, in the `Color` 1, 0.3, 0.2. Find each identifier
   (ID) with `entity.find` and its name during play.

   :::
   ::::

   **You should see:** the count fall by one with each coin, the seconds count down and the bar shorten. At ten seconds
   left the timer turns red.

   **If you do not see it:** the texts keep their old words. The script did not find a name: check the spelling of
   `CoinText`, `TimerText` and `TimeBar`, and that the coins carry the tag `Coin`.

:::::

::checkpoint{stage=3}

::figure{id=hud-playing}

## Check every screen and add text in the world

The canvas works with these numbers at four screens, by the rule of the first section.

| Screen | Scale | Canvas in units | The 24-unit margin in pixels |
| --- | --- | --- | --- |
| 1920 by 1080 | 1.0 | 1920 by 1080 | 24 |
| 1280 by 720 | 0.667 | 1920 by 1080 | 16 |
| 1440 by 1080 (4:3) | 0.866 | 1663 by 1247 | 20.8 |
| 2520 by 1080 (21:9) | 1.146 | 2200 by 943 | 27.5 |

The corner texts keep their distance in units, so they stay in their corners. The bar's full length is always 80 units
shorter than the canvas is wide, so it spans about 96 % of every screen. At a **Fill Amount** of 0.6 it shows the first
60 % of that length.

::figure{id=screen-4x3}

:::::steps

1. Check three aspect ratios. The Game view shows the game as a player's screen would.

   ::::tabs{sync=how}
   :::tab[In the editor]
   At the top of the Game view, open the resolution chip and choose **16:9**, then **4:3**, then **21:9**.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "gameView": { "mode": "16:9" } } }
   { "command": "viewport.setSettings", "parameters": { "gameView": { "mode": "4:3" } } }
   { "command": "viewport.setSettings", "parameters": { "gameView": { "mode": "21:9" } } }
   { "command": "ui.layout", "parameters": { "entity": "<CoinText id>", "screen": [1440, 1080] } }
   { "command": "ui.layout", "parameters": { "entity": "<CoinText id>", "screen": [2520, 1080] } }
   { "command": "ui.layout", "parameters": { "entity": "<TimeBar id>", "screen": [1440, 1080] } }
   { "command": "ui.layout", "parameters": { "entity": "<TimeBar id>", "screen": [2520, 1080] } }
   ```

   The mode changes only the Game view's picture in the window. `ui.layout` lays the HUD out at a screen size: each
   `rect` is x, y, width and height in pixels, and `CoinText`'s x matches the table's last column.

   :::
   ::::

   **You should see:** at every ratio the count in the top-left corner, the timer in the top-right corner and the band
   across the top with equal margins. The bar along the bottom starts 40 units from the left edge.

   **If you do not see it:** a text is cut or shifted. Its pivot is not at the corner, so choose its preset again with
   **Position** ticked. A bar that shows much less than 60 % of the band has a **Size** that is not -80.

2. Add text in the world. A text can also float in the scene without any canvas. Use **+ ▸ 3D Text**, which adds a
   `Text` component. By default it is in screen space, at the middle of the screen, so change three things.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+** in the Hierarchy and choose **3D Text**. Rename it `StartSign`. Clear **Screen Space**, set **Text** to
   `Roll!` and **Font Size** to 1. In the world the size counts world units per em, the height a font is designed at, so the default 32
   would make letters about 32 m tall.

   Place it above the ball's start with **Translation** (0, 1.5, 0). The text lies in its entity's `XY` plane and
   faces +Z. It does not follow the camera, so give it the camera's **Rotation**, for example -55 on X.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "StartSign", "components": { "Text": { "Text": "Roll!", "ScreenSpace": false, "FontSize": 1 }, "Transform": { "Translation": [0, 1.5, 0], "Rotation": [-55, 0, 0] } } } }
   ```

   :::
   ::::

   **You should see:** the word `Roll!` floating above the start, drawn behind any wall that stands in front of it.

   **If you do not see it:** you see its back, or nothing. The text faces +Z: turn the entity so that +Z points at the
   camera.

:::::

:::caution
Never build a HUD from screen-space `Text`. Its **Font Size** and its offset are in pixels, so it does not scale with the screen.
A 32-pixel text is 4.4 % of a 720-pixel window and 3.0 % of a 1080-pixel one. Use a canvas.
:::

::checkpoint{stage=4}

::figure{id=screen-21x9}

## Summary

- A canvas lays its elements out for a reference resolution and scales them to the screen, so a HUD keeps its look.
- Anchors, a pivot and an alignment keep a text in its corner at every screen shape.
- A sliced panel keeps its corners, a Filled image shows a part of itself, and a HUD's canvas turns **Receives Input** off.
- A script sets texts and colors with `GetUI()`, and the bar's fill with `SetProperty`, every frame.
- The Game view's resolution chip shows the HUD at 16:9, 4:3 and 21:9.

## Check yourself

1. Why is a HUD built from screen-space `Text` a mistake?

   :::answer{tests="canvas-scaling"}
   Its size and offset are in pixels, so it covers a different share of each screen. A canvas lays out in canvas units and
   scales them, so the HUD keeps its proportions.
   :::

2. A canvas with the reference resolution 1920 by 1080 is shown in a 1280 by 720 window. How many pixels high is a text
   48 units high?

   :::answer{tests="canvas-scaling"}
   32 pixels. The window is two thirds of the reference in both directions, so the scale is 0.667 and $48 \times 0.667 = 32$.
   :::

3. A text is anchored top left with the pivot in its middle, a size of 360 units and the default alignment. What do you
   see?

   :::answer{tests="anchors"}
   Half of the rect is outside the screen, and the centred text is cut at the edge. Put the pivot at the corner, or
   choose the preset with **Pivot** ticked, and set the alignment to Left.
   :::

4. A bar has anchors 0 and 1 across the canvas and a size of -80 along that axis. How wide is it on a canvas 1920 units
   wide?

   :::answer{tests="build-hud"}
   1840 units: the size is added to the span between the anchors, 1920, so the bar leaves 40 units on each side.
   :::

5. Why does `SetValue` not set the bar, and what does?

   :::answer{tests="drive-hud"}
   `SetValue` moves only a slider or a toggle. The bar is an image, so you set its `FillAmount` through
   `SetProperty("UIImage", "FillAmount", fraction)`, where `fraction` is a `float`.
   :::

6. At 21:9 the HUD looks wider than at 16:9. What stays the same, and what changes?

   :::answer{tests="check-screens"}
   Distances in canvas units stay: the margins and the sizes of the texts. The canvas itself is wider in units, so the
   bar, which spans the canvas minus 80 units, becomes longer.
   :::

## Exercises

1. **Basic.** Move the timer to the top centre with the anchor presets, and check it at 4:3 and 21:9.

   :::answer{tests="anchors check-screens" solution="tutorials/make/hud/exercise-1.tutorial.json"}
   Choose `Top Center` for `TimerText` with **Position** ticked, set **Alignment** to Center and **Position** to 0 and
   24. At both ratios the timer stays on the middle line, because the anchor is the canvas's middle.
   :::

2. **Medium.** Add a second Filled bar that shows the part of the coins collected. Predict its fill after two of five
   coins.

   :::answer{tests="build-hud drive-hud"}
   Keep the largest count seen as the total: `CoinPlacer` places the coins a moment after Play, so a count in `OnCreate` finds none. Set `FillAmount` to the collected coins over the total, both as `float`.
   After two of five coins the value is $2 / 5 = 0.4$, so the bar is two fifths full.
   :::

## Where it lives in Strata

- `Strata/src/Strata/GameUI/GameUIComponents.h`: the canvas, rect, image and text components and their defaults.
- `Strata/src/Strata/GameUI/GameUIScene.cpp`: `ComputeScale`, the scale from the reference resolution.
- `StrataEditor/src/Editor/GameUIPresets.cpp`: the presets of **+ ▸ UI**.
- `StrataScriptCore/Include/StrataScript/UI.h`: `UIElement`, with `SetText` and `SetColor`.
- `Strata/src/Strata/Renderer/RendererComponents.h`: the `Text` component for the world.

## Further reading

- [cppreference, "to_string"](https://en.cppreference.com/w/cpp/string/basic_string/to_string): turns a number into
  text (beginner).
