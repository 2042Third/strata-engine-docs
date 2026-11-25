---
id: make/transforms-units
title: "Positions, rotations and units"
description: "What the numbers of a Transform mean: axes, metres, degrees, turns and the parent that every child counts from."
kind: concept
size: L
tracks: [G, B]
needs: [make/scenes-entities]
time: 60
learn:
  - id: read-transform
    text: explain what the Translation, Rotation and Scale numbers of a Transform mean, in metres, axes and degrees
  - id: forward-direction
    text: name the forward direction of a camera and of a glTF model, and find why a model walks backwards
  - id: convert-angles
    text: compute radians from degrees and degrees from radians
  - id: combine-turns
    text: predict where a thing points after two turns, done in either order
  - id: child-position
    text: predict the world position of a child when its parent moves or turns
since: 0.3.0
status: final
---

On the page about scenes and entities you typed numbers into the Inspector. A wall took the numbers (0, 0.5, -10). The coin needed a turn of 90 degrees before it stood up like a coin and not like a flat disc on a table. The editor accepted every number. It never told you what a number means.

The page answers that question. Is 10 a distance, and in which unit? Which way is minus? What does 90 turn, and around what? When the page ends, you can read every Transform in the Inspector.

You can predict where a child goes when its parent turns. You can change between degrees and radians, the two ways to count a turn.

The page starts from what you see: the Inspector's numbers and the :term[gizmo]{id=gizmo-start} in the Scene view. Code comes in one section near the end, and you can skip it until the page about scripting the scene sends you back to it.

## A bare number needs an origin, a direction and a unit

The first guess is short: x goes right, y goes up, and a number is how far. That guess is right for a position on a flat drawing, and it fails in a 3D scene in three places.

First, a drawing has two axes, and a scene has three. Which way does the third one point? Toward you or away from you? A wall at z = -10 is behind the ground's far edge or in front of the near edge, and the guess does not say which.

Second, the word "forward" has no number. A character that walks forward needs a direction, and a camera needs to know which way it looks. Every tool must agree on one answer, or a model made in one tool faces the wrong way in another.

Third, a turn has a direction. A turn of 90 degrees goes left or right, and it goes around some line. A number without that line is not a turn.

A last problem comes from the Hierarchy. When the four walls are children of **Walls**, does the number of a wall count from the middle of the level, or from **Walls**?

## A position is three distances along three axes

Open Coin Run's level and select the ground. Press **W**, which chooses the Move gizmo (**Q** selects without a gizmo, **E** rotates and **R** scales). Three arrows appear on the ground. The red one points along the **X axis**, the green one along the **Y axis** and the blue one along the **Z axis**. An **axis** is a straight line through the middle of the scene along which one number is counted.

The Inspector's **Transform** section holds three rows. The first row is **Translation**, which is the word the Inspector uses for position: three numbers, X, Y and Z, that say how far the entity is from the origin along each axis. The origin is the point (0, 0, 0), where all three axes meet. In a new Basic 3D project the ground is centred on it.

Strata counts in **metres**, and every number of a Translation is a distance in metres. The ball is a sphere with a radius of 0.5, so it is 1 m across. The ground is 20 m across, so its edges lie 10 m from the origin on both sides. The built-in cube is 1 m on every side.

The Y axis points up. A Translation of (0, 0, 0) puts the centre of a thing on the ground, so half of a ball would sink into it. The ball rests on the ground at a Translation of (0, 0.5, 0): its centre is one radius, 0.5 m, above the surface. The wall of the scenes page used the same idea: a cube 1 m tall at y = 0.5 stands on the ground.

:::example[Where does a wall at (0, 0.5, -10) stand?]
Read the three numbers one by one. X is 0, so the wall is in the middle from left to right. Y is 0.5, so the centre of a 1 m cube is half a metre up and the cube stands on the ground. Z is -10, so the wall is 10 m from the origin along the Z axis, in the minus direction.

The ground reaches 10 m from the origin, so the wall stands on the ground's edge at z = -10. Now drag the wall's blue arrow a little: the Z number changes while X and Y stay. The gizmo changes one number per arrow.
:::

The **Snap** button above the Scene view rounds a drag to steps. The default step for moving is 0.5 m, and for turning it is 15 degrees. Holding **Ctrl** while you drag reverses the button: with Snap on, Ctrl lets you drag freely, and with Snap off, Ctrl snaps.

```mermaid caption="The three axes of the scene: the red X axis to the right, the green Y axis up and the blue Z axis toward you, so forward is the minus direction of Z." alt="A diagram of the origin with four arrows: plus X to the right, plus Y up, plus Z toward the viewer and minus Z away from the viewer, labelled forward."
flowchart LR
    O["Origin (0, 0, 0)"] -->|"+X: right, red"| X["x grows"]
    O -->|"+Y: up, green"| Y["y grows"]
    O -->|"+Z: toward you, blue"| Z["z grows"]
    O -->|"-Z: away from you, forward"| F["z shrinks"]
```

Right, up and toward you are the plus directions, and away from you is minus Z. The next sections explain why Strata chose this map.

## Adding numbers moves a thing and multiplying scales it

Move the wall from (0, 0.5, -10) by 2 m to the right. The new place is (0, 0.5, -10) plus (2, 0, 0), which is (2, 0.5, -10): you add the move to each number. The move (2, 0, 0) is itself a triple of numbers, and adding triples works number by number. Adding a move of (0, 3, 0) lifts the wall by 3 m, and the other two numbers stay.

Multiplying works on a distance. The third row of the Transform is **Scale**. The scale of a cube is three **factors**, one for each axis: the cube is 1 m on each side, multiplied by the factor. A Scale of (4, 1, 1) makes a cube 4 m long from left to right and still 1 m tall and deep. A Scale of (4, 2, 0.5) gives a block 4 m by 2 m by 0.5 m.

Adding moves a thing and keeps its size. Multiplying changes its size. A wall that is 20 m long is a cube with a Scale of (20, 1, 1). Scale 1 means "as modelled", and Scale 0.5 means half. A factor of 0 flattens a thing to nothing along that axis, so avoid it.

## A direction is three numbers, and forward is minus Z

A direction is also three numbers, but the triple means a way, not a place. The direction (0, 1, 0) means "up", (1, 0, 0) means "to the right" and (0, 0, 1) means "toward you". Only the way matters: a step of 1 m along the direction, from where you are.

Strata needs one answer to the question "which way is forward?". The answer is the minus direction of the Z axis, written -Z. **Forward (-Z)** is the direction a camera looks along, a light shines along and a script calls forward.

Check it on the scene. Select the **Main Camera**: the page about scenes moved it to (0, 16, 13), so it stands 16 m up and 13 m toward the viewer from the origin. Its Rotation tilts it down to look at the level, which lies in the minus Z direction from it. Switch the gizmo to **Local** (the section on parents says how) and the camera's blue arrow points away from where the camera looks. The arrow shows plus Z, the camera's back, and forward is the opposite.

A **Sun** works the same way: a directional light shines along its own -Z, away from the sun. The template turns the Sun so that its -Z points down at the ground.

A model has a front too, and it is not always the same as the engine's forward. Strata imports models from **glTF** files, a common format for 3D models, and the format says a model faces +Z. A character made for glTF looks toward +Z in its own space, which is the opposite of the engine's forward. If a script moves that character along the entity's forward, the character moves backwards, tail first.

There are two fixes. A script can compute the direction for +Z. Or you can turn the model's entity 180 degrees around Y and make it a child of the entity that moves: the parent's -Z is now the model's front. Both fixes are small once you know the cause.

:::note
A **Vector2** control, like the stick of a gamepad, gives +Y when you push it up. On the ground the matching direction is -Z, not +Y. The page about input shows the one line that converts one to the other.
:::

## Handedness decides which way the third axis points

Why does Z point toward you and not away? Because Strata uses a **right-handed** system, which means the three axes follow the fingers of your right hand. Hold the hand with the thumb to the right, the index finger up and the middle finger bent toward your face. The thumb is X, the index finger is Y and the middle finger is Z. The middle finger points at you, so Z grows toward you and forward is minus Z.

A left hand does the same with a mirrored result: the middle finger points away, and Z grows away from you. A scene works in both systems, but they do not mix: a model from one arrives mirrored in the other.

The right hand also tells the way of a turn. Point your right thumb along an axis, in the plus direction. The curled fingers show the plus direction of a turn around that axis. Around Y, the thumb points up and the fingers curl counterclockwise when you look down from above. A positive turn around Y therefore turns a thing to the left, seen from above.

You can test it: with forward as (0, 0, -1), a turn of +90 degrees around Y points the thing toward (-1, 0, 0), to the left.

## Scale is three factors, and a negative factor mirrors

The Scale row has a use beyond size. A factor of -1 flips a thing along that axis, like a reflection in a mirror. Select the ball and type -1 into the X field of its Scale. A sphere is the same on both sides, so nothing seems to change, and that is the point of this check: the ball is not drawn inside out and its lighting stays right.

A drawing has an inside and an outside. For each triangle the :term[renderer]{id=renderer} decides which side is the front from the order of its three corners, and a mirror reverses that order, so the front would become the back. Strata notices a mirrored placement (the three factors of Scale multiply to a negative number, counting the parents' factors too) and draws such objects with the opposite order. It also adjusts the directions its lighting reads. A negative scale therefore works without a trick.

:::tip
To make the left half of a prop from its right half, duplicate it with **Ctrl+D** and set X of the copy's Scale to -1. You need no second model. The mirrored copy casts shadows and receives light as the original does.
:::

Mirroring a parent mirrors its children's positions too: a child at x = 2 in a parent with a Scale of (-1, 1, 1) appears at x = -2.

## A rotation is an axis and an angle

A turn needs two facts: the line it goes around and how far it goes. The line is an axis. The coin of Coin Run shows both. A cylinder stands on its end, and a coin is a cylinder that is flat and lies on its face. To stand the coin up, turn it 90 degrees around the X axis, so that its flat face looks toward +Z.

Select the coin and press **E**, which chooses the Rotate gizmo. Three rings appear: the red ring turns around X, the green around Y and the blue around Z. Watch the Inspector's **Rotation** row: the first field, X, shows the 90 you typed on the page about scenes. Drag the red ring a little, watch X change, and press **Ctrl+Z**.

The three fields of **Rotation** are three angles in degrees. X is **pitch**, a nod of the head, around the X axis. Y is **yaw**, a shake of the head, around the Y axis. Z is **roll**, a tilt of the head toward the shoulder, around the Z axis. The labels X, Y and Z carry the colours of the axes, and a click on a label resets that angle to zero.

Plus 90 around X lifts the front of a thing up: forward (0, 0, -1) turns to (0, 1, 0). Minus 90 would bend it down. Together, the three fields mean: do the turns of pitch, yaw and roll, in the order Strata fixes, and that total is the rotation.

After a coin stands, you want it to spin like a coin on a table. The spin is a turn around the vertical axis: its axis is Y and its angle grows by a few degrees each moment. The `Spinner` script of the scripting pages makes things turn this way, and the section on code shows its two lines. A spin around the world's Y axis keeps a standing coin standing, because the axis is vertical.

The hint of the Rotation row says that you edit it as angles in degrees. Keep that sentence for the section on what Strata cannot do.

## Radians count a turn by arc length

Degrees come from the old habit of dividing a full turn into 360 parts. Scripts and code libraries often count a turn in **radians**, so you meet both. A **radian** is the angle at which the arc along a circle's edge is as long as the circle's radius.

Walk the numbers by hand. The edge of a circle is 2π times its radius long, where π is about 3.1416. So a full turn holds 2π radians: about 6.283. A half turn is π, about 3.142.

A quarter turn, 90 degrees, is π divided by 2, about 1.571. A tenth of a full turn, 36 degrees, is about 0.628.

The conversion has one rule. To change degrees into radians, multiply by π and divide by 180. To go the other way, multiply by 180 and divide by π, so 1 radian is about 57.3 degrees.

:::note[The formula]
$$r = d \cdot \frac{\pi}{180}$$

$r$ is the angle in radians, $d$ is the angle in degrees, $\pi$ is about 3.1416 (a half turn, in radians), and the dot reads "times". At the limits, $d = 0$ gives $r = 0$, and $d = 360$ gives $r = 2\pi$, about 6.283.
:::

The Inspector, the gizmo and the editor's commands use degrees, because people think in them. Code works in radians, and the library function `glm::radians` converts. Mixing the two is the commonest error with turns: a script that passes 90 where radians are expected turns by about 5157 degrees, which is 14 full turns and a bit.

## A quaternion stores the turn, and order matters when turns combine

Strata does not store the three angles. It stores a rotation as a **quaternion**, which is four numbers that together hold one turn: its axis and its angle. Nobody types the four numbers. When you type 90 into the X field, the Inspector converts the three angles into a quaternion and stores that. When it draws the row, it converts back.

Why four numbers? Three angles can lose a turn when two of them line up, and four numbers cannot. Two quaternions also combine into one that holds the two turns done one after the other. The mathematics belongs to the pages of the basics part about rotations.

The operation is written as a product, and the order of a product matters for turns. Take two quarter turns of 90 degrees: A is pitch around X and B is yaw around Y. Test with a thing that looks along forward (0, 0, -1).

- A first, then B: pitch turns forward up to (0, 1, 0). Yaw around Y keeps an up direction up. The result is (0, 1, 0).
- B first, then A: yaw turns forward left to (-1, 0, 0). Pitch around X leaves a direction along X unchanged. The result is (-1, 0, 0).

The same two turns, in two orders, point the thing in two different directions. Turning is not like adding two moves, where order does not matter.

You can see this in the editor without any code. Create an empty entity **Pivot** and give it a child **Marker** (a cube). Set the Pivot's Rotation to (0, 90, 0) and the Marker's Rotation to (90, 0, 0).

The child turns first, and then its parent turns, so the Marker's own pitch comes first, then the Pivot's yaw. The Marker's forward becomes (0, 1, 0), up. Now swap the numbers: the Pivot to (90, 0, 0) and the Marker to (0, 90, 0). The Marker's forward becomes (-1, 0, 0).

:::example[Two turns in the Inspector, in both orders]
Select the Marker and switch the gizmo to **Local**. The blue arrow marks the Marker's plus Z, so forward is the opposite of that arrow.

Case one has the Pivot at (0, 90, 0) and the Marker at (90, 0, 0). The Marker's forward is up, and the blue arrow points straight down. Case two has the Pivot at (90, 0, 0) and the Marker at (0, 90, 0). The forward is the left direction, and the blue arrow points right.

The numbers on both Markers are the same two quarter turns. Only the order changed, and the result changed with it.
:::

## A child counts its position from its parent

An entity can have a parent. A child's Transform is then **relative**: its Translation counts from the parent, its Rotation turns relative to the parent's turn, and its Scale multiplies the parent's. The numbers in the Inspector are the child's own numbers.

The **local position** of an entity is its position counted from its parent.

The **world position** is its position counted from the origin of the whole scene, after all the parents have done their work. A thing without a parent has the same local and world position.

Walls give the simplest case. **Walls** holds four walls. Suppose Walls sits at (0, 0, 0) with no turn. Then each wall's local numbers equal its world numbers.

Move Walls to (5, 0, 0): each wall's local numbers stay the same, but each wall's world position is 5 m further to the right. Your four walls move together, because you changed one number.

With a turn it is less obvious. The order is: scale, then turn, then move. A child's local position is first scaled by the parent's Scale, then turned by the parent's Rotation, then moved by the parent's Translation.

:::example[A child under a turned parent]
The parent is at (10, 0, 0) with a yaw of 90 degrees. A child has the local position (2, 0, 0).

Turn the local position by the parent's yaw. Yaw +90 turns "right" (1, 0, 0) to "forward" (0, 0, -1), as the section on handedness showed. So the local (2, 0, 0) becomes (0, 0, -2). Now move by the parent's Translation: (0, 0, -2) plus (10, 0, 0) is (10, 0, -2).

The child's Inspector still shows (2, 0, 0). Its world position is (10, 0, -2), two metres in front of its parent.
:::

The Inspector shows local numbers only. The Scene view tells the rest: the gizmo stands at the child's world position, so you see where it really is. A command can tell too: `entity.get` with `"world": true` adds the world transform, with the rotation as angles in degrees.

The buttons above the Scene view hold a switch beside the gizmo buttons, labelled **World** or **Local** (it shows the one in use, and a click changes it). With **World**, the gizmo's arrows point along the scene's axes whatever the entity does. With **Local**, the arrows follow the entity's own turn, so the blue arrow of a turned crate points along its own +Z. Scaling always uses the entity's own axes.

When you drag an entity in the Hierarchy onto a new parent, Strata keeps its world placement and works out new local numbers. Drag a Moon at world (12, 0, 0) into an Earth at (10, 0, 0), and the Moon's Translation becomes (2, 0, 0). It does not jump. A command can leave the entity's local numbers alone instead: `entity.setParent` takes `"keepWorldTransform": false`.

:::example[The solar system]
Create **Sun**, **Earth** and **Moon**, nested in this order in the Hierarchy. Give Earth the local Translation (10, 0, 0) and Moon the local Translation (2, 0, 0). The Moon's world position is (12, 0, 0): 10 m plus 2 m.

Now select the Sun and type 90 into the Y field of its Rotation. Predict first: the Earth is 10 m along the X axis, and a yaw of +90 sends right to forward, so the Earth moves to (0, 0, -10). The Moon turns with it: its position is the Earth's plus its local (2, 0, 0) turned by 90 degrees, which is (0, 0, -2). Its world position is (0, 0, -12). The Moon's own numbers did not change at all.
:::

## Engines choose their conventions differently

Strata's choices are not the only ones. Four questions have no right answer, and each engine settled them its own way.

| Question | One answer | Another answer | Used by |
| --- | --- | --- | --- |
| Which axis is up? | Y up | Z up | Y up: glTF, Unity, Godot, Strata. Z up: Blender, Unreal Engine |
| Which hand? | Right-handed | Left-handed | Right: glTF, Godot, Blender, Strata. Left: Unity, Unreal Engine |
| Which unit? | Metres | Centimetres | Metres: glTF, Unity, Godot, Strata. Centimetres: Unreal Engine |
| How is a turn stored? | Angles (pitch, yaw, roll) | A quaternion | Strata and most engines store quaternions and show angles |

The conventions cost nothing at run time. The cost lies in conversions: an importer must turn each model from the convention of its file to the engine's.

A difference between two tools gives a mirrored model or one 100 times too big. Angles are simple to read but combine badly, as the section on order showed. A quaternion combines well and reads badly, so most engines store it and show angles.

## Strata follows glTF and stores quaternions

Strata uses Y up, right-handed axes, -Z forward and metres, and it stores quaternions and shows angles in degrees. Three of those choices match glTF, the format Strata imports models from: up, hand and unit.

:::why[Why take glTF's conventions?]
A model arrives from a file, and every convention that differs from the file's is a conversion. A conversion is code that can be wrong, and it makes a number in the file differ from the number in the scene. By matching glTF on up, hand and unit, a model needs no mirroring and no scaling when you import it.

The one difference is the front. glTF says a model faces +Z, but cameras and lights in Strata look along -Z, the usual forward of a camera in a right-handed system. Strata keeps -Z forward and accepts that a model must sometimes be turned by half a turn.

The price is the one you met above: the walking-backwards model. The cost is small, and it is paid once for each model.
:::

The reason for storing quaternions is in the section on order: combining two turns by multiplying is simple and exact.

## What Strata's choice cannot do

The Inspector shows angles because people can read them, but the stored value is a quaternion, and one rotation has more than one set of angles. Turn yaw by 120 degrees and the same turn is also pitch 180, yaw 60 and roll 180. The two triples mean the same turn and look different.

Strata keeps the angles you typed while the row stays unchanged. When the rotation changes some other way (a gizmo drag, a script, an undo), or the editor starts again, the Inspector works the angles out from the stored quaternion again. It always reports a yaw between -90 and 90 degrees.

Typing (0, 120, 0), saving and opening the project again later therefore shows (180, 60, 180). The entity did not move: both rows describe the same turn. The section on code shows the effect in a few lines.

A command shows the worked-out angles at once. `component.get` returns the stored four numbers, and `entity.get` with `"world": true` adds `rotation.euler` under `world`: the angles worked out from the quaternion in the same way, for an entity without a parent. After a `component.set` of (0, 120, 0), it reads about (180, 60, 180), up to the last digits.

Strata does not give you a left-handed mode, a Z-up mode or a unit setting. A model with another convention is converted on import or turned by a parent entity. Other conventions that Strata does not take are listed in [What Strata does not do](../appendix/not-in-strata.md).

## The same ideas in code

This section is for the day you read a script. The page about scripting the scene sends you back here, because it is the first page that uses these forms. If you cannot read C++ yet, read the numbered notes and skip the rest.

:::question
What do the types, calls, classes and pointers of these lines mean? See [Programming 1](../basics/programming-1.md), [Programming 2](../basics/programming-2.md), [Programming 3](../basics/programming-3.md), [C++ classes](../basics/cpp-classes.md) and [C++ memory](../basics/cpp-memory.md).
:::

A position and a direction are each a `glm::vec3`, a value that holds three numbers named x, y and z. The next lines are from the script library that games use. They read a Transform's local numbers and its turn as a quaternion (a `glm::quat`). The comment mentions radians, which is the unit code uses.

```cpp src="StrataScriptCore/Include/StrataScript/Entity.h#L171-L175"
glm::vec3 GetTranslation() const { return Detail::FromABIVector3(GetLocal().Translation); }
glm::quat GetRotation() const { return Detail::FromABIQuat(GetLocal().Rotation); }
glm::vec3 GetScale() const { return Detail::FromABIVector3(GetLocal().Scale); }
// Local rotation as Euler angles in radians (pitch, yaw, roll).
glm::vec3 GetEulerAngles() const { return glm::eulerAngles(GetRotation()); }
```

The names show a point of this page. The local position of the Inspector's **Translation** row is read with `GetTranslation` and written with `SetTranslation`. The world position has its own names, in the lines that follow.

```cpp src="StrataScriptCore/Include/StrataScript/Entity.h#L212-L229"
bool SetWorldPosition(const glm::vec3& position)
{
	StrataScriptTransform transform = {};
	Detail::ToABIVector3(position, transform.Translation);
	return SetWorld(transform, StrataScriptTransformPart_Translation);
}

bool SetWorldRotation(const glm::quat& rotation)
{
	StrataScriptTransform transform = {};
	Detail::ToABIQuat(rotation, transform.Rotation);
	return SetWorld(transform, StrataScriptTransformPart_Rotation);
}

// World-space directions of the entity's local axes (-Z is forward).
glm::vec3 GetForward() const { return GetWorldRotation() * glm::vec3(0.0f, 0.0f, -1.0f); }
glm::vec3 GetRight() const { return GetWorldRotation() * glm::vec3(1.0f, 0.0f, 0.0f); }
glm::vec3 GetUp() const { return GetWorldRotation() * glm::vec3(0.0f, 1.0f, 0.0f); }
```

1. **Lines 212–216:** `SetWorldPosition` places the entity by its world position. The parents' work is undone for you, so the local numbers change.
2. **Lines 219–224:** `SetWorldRotation` does the same for the turn.
3. **Lines 227–229:** The three directions of an entity in the world. Forward is the entity's turn applied to (0, 0, -1), the -Z of this page.

`GetWorldPosition`, a few lines above, reads the world position. Local names say Translation and world names say Position, as in the Inspector and the scene view.

A turn like the coin's is in the `Spinner` script that the editor writes for a new project. Its update function runs once for each frame with the time that the frame took. The two lines to look at build a small turn and multiply it with the current rotation.

```cpp src="StrataEditor/src/Editor/ScriptProject.cpp#L246-L251"
void OnUpdate(float deltaTime) override
{
	TransformComponent transform = GetTransform();
	const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
	transform.SetRotation(turn * transform.GetRotation());
}
```

The line with `glm::angleAxis` is the page's axis and angle in code: the angle is degrees per second times the frame's seconds, converted to radians by `glm::radians`, and the axis is `glm::vec3(0.0f, 1.0f, 0.0f)`, up. The next line writes `turn * transform.GetRotation()`: the new small turn at the left of the product, so it happens last, around the world's Y axis. This is the product of the section on order, and the reason a standing coin keeps standing.

The sketch below converts angles and shows the readback of a typed yaw. It reads the way the Inspector does: it builds a quaternion from typed degrees and asks for the angles back.

```cpp sketch="make-transforms-units-angles.cpp"
// Degrees and radians, and the angles a rotation shows when it is read back.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

int main()
{
	std::printf("180 degrees = %.4f radians\n", glm::radians(180.0f));
	std::printf("360 degrees = %.4f radians\n", glm::radians(360.0f));

	const glm::vec3 typed(0.0f, 120.0f, 0.0f); // Pitch, yaw, roll as typed
	const glm::quat rotation(glm::radians(typed));
	const glm::vec3 readBack = glm::degrees(glm::eulerAngles(rotation));
	std::printf("typed (%.0f, %.0f, %.0f)\n", typed.x, typed.y, typed.z);
	std::printf("read back (%.0f, %.0f, %.0f)\n", readBack.x, readBack.y, readBack.z);
}
```

```text output-of="make-transforms-units-angles.cpp"
180 degrees = 3.1416 radians
360 degrees = 6.2832 radians
typed (0, 120, 0)
read back (180, 60, 180)
```

1. **Lines 8–9:** the two checks of the limits: 180 degrees is π and 360 degrees is 2π, as the section on radians showed.
2. **Lines 11–13:** the typed angles become a quaternion and then angles again, in the way the Inspector does.

The last two lines of the output are the finding of the section on what Strata cannot do: the typed yaw of 120 comes back as pitch 180, yaw 60 and roll 180.

## Common mistakes

1. **A model walks backwards.** The model's front is +Z and the movement goes along -Z. The symptom: the character moves tail first, and its walk animation looks reversed. The fix: put the model under a parent turned 180 degrees around Y, or compute the facing for +Z in the script.
2. **Adding angles to a stored turn.** Adding 10 to the number of an angle is fine in the Inspector, where you replace one angle. It does not work for a turn that already exists in the world: combining two turns is a product, not a sum. The symptom: a thing flips or turns around a different line than the one you meant. The fix: build the turn as its own rotation and multiply it with the old one, as the section on code shows.
3. **A model a hundred times too large.** The model was made in centimetres, and Strata counts in metres. The symptom: a character taller than a house. The fix is an import setting, taught on [Bringing in assets](assets.md).
4. **Moving toward the camera.** A key or stick gives +Y for forward, and a script uses it as the Z of a movement. The symptom: W moves the ball toward the camera. The fix: forward is minus Z, so the movement is (right, 0, -forward).
5. **Reading a child's numbers as world numbers.** The child's Inspector shows local numbers. The symptom: a child at (2, 0, 0) is not 2 m from the origin. The fix: read the gizmo, or ask the command `entity.get` for the world transform.
6. **Degrees where radians belong.** A function of code expects radians, and the number given was degrees. The symptom: a thing spins wildly or ends in a strange place. The fix: convert with `glm::radians`.

## Summary

- A Transform holds a Translation in metres along the red X, green Y and blue Z axes (Y up), a Rotation shown as pitch, yaw and roll in degrees, and a Scale of three factors.
- Forward is -Z for cameras, lights and scripts, while glTF models face +Z, which makes a model walk backwards until it is turned.
- Radians equal degrees times π divided by 180, so a full turn is 360 degrees or about 6.283 radians.
- Strata stores a rotation as a quaternion, two turns combine by multiplying, and the order changes the result.
- A child's numbers are local, counted from its parent, and its world position follows the parent's move, turn and scale.

## Check yourself

1. The Basic 3D camera stands at (0, 2, 6) and looks at the origin. In which direction does it look, roughly?

   - A. Along +Z, toward larger z.
   - B. Along -Z, toward smaller z.
   - C. Along +Y, upward.
   - D. Along +X, to the right.

   :::answer{tests="forward-direction"}
   B is right: a camera looks along its minus Z, and from z = 6 toward the origin means smaller z. A is the mistake of the model that walks backwards: +Z is the camera's back, the direction the blue arrow shows. C and D ignore the camera's position and turn.
   :::

2. How many radians are 45 degrees, and how many degrees are 3 radians? Use π of about 3.1416.

   :::answer{tests="convert-angles"}
   45 degrees times π divided by 180 is π divided by 4, about 0.785 radians. 3 radians times 180 divided by π is about 171.9 degrees. A check: a half turn is π, about 3.14 radians, so 3 radians is a little under 180 degrees.
   :::

3. A parent stands at (5, 0, 0) with a yaw of 90 degrees. A child has the local position (0, 0, 3). Where is the child in the world?

   :::answer{tests="child-position"}
   Turn the local position by the parent's yaw: a yaw of +90 around Y turns (0, 0, 3) to (3, 0, 0), because +Z turns toward +X. Then add the parent's Translation: (3, 0, 0) plus (5, 0, 0) is (8, 0, 0). The child's Inspector still shows (0, 0, 3). Adding without turning would give (5, 0, 3), which is the mistake of forgetting the parent's rotation.
   :::

4. Two turns, pitch 90 and yaw 90, are done one after the other. Which statement holds?

   - A. The order does not matter, as with adding two moves.
   - B. Pitch first and yaw first give different directions of forward.
   - C. Both orders give forward (0, 0, -1) again.
   - D. The result is the sum of the angles: (90, 90, 0).

   :::answer{tests="combine-turns"}
   B holds: forward ends at (-1, 0, 0) for yaw first and at (0, 1, 0) for pitch first. A is the mistake of treating turns like moves. C is wrong because no turn of a quarter returns to the start. D adds angles, which does not work for combined turns in general.
   :::

5. You type (0, 150, 0) into a Rotation and save the scene. Then you close the editor and open the project again. What does the row show?

   :::answer{tests="read-transform"}
   The row shows (180, 30, 180): a yaw is read back between -90 and 90, and the second set of angles of the same turn is (x plus 180, 180 minus y, z plus 180). Both triples are one rotation, so the entity did not move. The Inspector keeps the angles you typed only until the rotation changes another way or the editor starts again.
   :::

## Exercises

Exercise 3 runs a sketch. Running it needs a C++ compiler, which [Installing Strata and the C++ build tools](../start/install.md) gives you, and the glm headers, which the Strata folder holds under `StrataScriptCore`. [How a C++ program is built](../basics/build.md) shows how to compile one file. Without them, work the lines out by hand and check them against the answer.

1. **Basic.** Coin Run's ball has a radius of 0.5 and the ground's top is at y = 0. A coin is a cylinder 1 m tall, with a Scale of (0.6, 0.05, 0.6), and it lies flat on the ground. Which Translation y puts it on the ground? Then which Rotation and which y stand it up on its edge, so that it faces +Z?

   :::answer[Worked solution]{tests="read-transform"}
   The Scale multiplies the cylinder's 1 m height by 0.05, so the flat coin is 0.05 m thick and its centre belongs 0.025 m above the ground: y = 0.025. To stand it up, turn it 90 degrees around X: Rotation (90, 0, 0). A cylinder's axis is Y, and the pitch lifts that axis toward +Z, so the face looks toward +Z. The Scale belongs to the cylinder, not to the world: the factor 0.05 stays on the cylinder's own axis, so the thin direction now points along Z. The coin is 0.6 m wide and 0.6 m tall, so its centre is 0.3 m up: y = 0.3.
   :::

2. **Medium.** Build the solar system of the example in the editor: Sun, Earth and Moon, Earth at (10, 0, 0) and Moon at (2, 0, 0). Turn the Sun by 90 degrees of yaw, and read the Moon's world position with the gizmo or the command `entity.get`.

   :::answer[Worked solution]{tests="child-position,read-transform" solution="tutorials/make/transforms-units/exercise-2.tutorial.json"}
   Create the three entities with **+** in the Hierarchy, and drag Earth onto Sun and Moon onto Earth. Type 10 into the X of Earth's Translation, and 2 into Moon's. Select Sun and type 90 into the Y of its Rotation. The Moon's world position is (0, 0, -12), and the Moon's Inspector still says (2, 0, 0).

   The command form is `entity.get` with the Moon's id and `"world": true`: its `world` field has the position. The tutorial file of this exercise checks both numbers.
   :::

3. **Hard.** Read the sketch below. It turns the right direction (1, 0, 0) by a roll of 90 degrees and a yaw of 90 degrees, in both orders. Work out both lines of output by hand, then run it.

   :::answer[Worked solution]{tests="combine-turns,convert-angles" solution="sketches/make-transforms-units-roll.cpp"}
   Roll around Z by +90 turns right (1, 0, 0) to up (0, 1, 0). Yaw around Y by +90 turns right to (0, 0, -1) and leaves up where it is. So roll first, then yaw, gives (0, 1, 0), and yaw first, then roll, gives (0, 0, -1).

   ```cpp sketch="make-transforms-units-roll.cpp"
   // Two quarter turns, one about Z (roll) and one about Y (yaw), done in both orders on the right direction.
   #include <cmath>
   #include <cstdio>
   #include <glm/glm.hpp>
   #include <glm/gtc/quaternion.hpp>

   static void Print(const char* label, const glm::vec3& direction)
   {
   	std::printf("%s (%.0f, %.0f, %.0f)\n", label, std::round(direction.x) + 0.0f, std::round(direction.y) + 0.0f, std::round(direction.z) + 0.0f);
   }

   int main()
   {
   	const glm::vec3 right(1.0f, 0.0f, 0.0f);
   	const glm::quat roll = glm::angleAxis(glm::radians(90.0f), glm::vec3(0.0f, 0.0f, 1.0f));
   	const glm::quat yaw = glm::angleAxis(glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
   	Print("roll first, then yaw:", (yaw * roll) * right);
   	Print("yaw first, then roll:", (roll * yaw) * right);
   }
   ```

   ```text output-of="make-transforms-units-roll.cpp"
   roll first, then yaw: (0, 1, 0)
   yaw first, then roll: (0, 0, -1)
   ```

   1. **Lines 15–16:** each turn is an angle and an axis, converted from degrees to radians.
   2. **Lines 17–18:** the product does the turn at its right first, so the two lines differ only in the order of the factors.
   :::

## Where it lives in Strata

- **Transform** component: the Inspector rows **Translation**, **Rotation** and **Scale**. The hint of the Rotation row says it is edited as angles in degrees.
- The buttons above the Scene view: the buttons Select, Move, Rotate and Scale (keys **Q**, **W**, **E**, **R**), the **World** and **Local** button, **Snap** and its step settings. The Rotate and Move steps start at 15 degrees and 0.5 m.
- The Hierarchy: dragging a row onto another row makes a child and keeps its world placement.
- Commands: `component.set` writes a Transform's values (a Rotation as three angles in degrees), `entity.get` with `"world": true` reads the world transform, `entity.setParent` takes `keepWorldTransform`, and `viewport.setSettings` takes the gizmo, its space and the snap steps.
- Script library: `TransformComponent` with `GetTranslation`, `SetTranslation`, `GetWorldPosition`, `SetWorldPosition`, `GetRotation`, `SetEulerAngles` (radians) and `GetForward`.

## Further reading

- Khronos Group, "glTF 2.0 Specification", the section on coordinate system and units: the +Y up, +Z front, right-handed and metres conventions that Strata follows (intermediate).
- Unity Manual, the pages about the Transform and about coordinate systems: Y up with a left-handed system, for comparison (beginner).
- Godot documentation, "Introduction to 3D": a Y up, right-handed system and metres, with -Z forward for cameras (beginner).
- Unreal Engine documentation on the coordinate system: Z up, left-handed, centimetres (beginner).
- Blender manual, the section on the 3D viewport's axes: Z up, right-handed (beginner).
