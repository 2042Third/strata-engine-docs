---
id: editor/camera-viewport
title: "The editor camera and viewport state"
description: "How the editor camera orbits, pans, dollies and frames a selection, which camera each view draws with, and how a capture renders a picture."
kind: internals
size: L
tracks: [E]
needs: [gpu/coordinates, basics/math-rotations, draw/bounds-culling, editor/commands]
time: 75
learn:
  - id: camera-model
    text: explain how a target, a distance, a yaw and a pitch fix the editor camera's position, and what pan and dolly change
  - id: framing
    text: compute the distance that Focus and FitBounds choose for a box
  - id: view-choice
    text: explain which camera the Scene view, the Game view and a capture draw with
  - id: capture-wait
    text: explain what a capture waits for before it reads the picture, and what it leaves unmoved
since: 0.3.0
status: final
---

A person who edits a scene must look at any part of it within a second, and must find each scene as they left it. The editor camera is the camera that makes this possible. It is not a game object: no scene saves it, and no game ever sees it. It belongs to the editor, and the editor keeps one for each scene.

This page covers the camera's data and its mathematics, the state of the viewport around it, the rule for which camera each view draws with, and the commands that read and change all of it. It also covers how a capture turns the viewport into a picture, because every picture in this book comes from one. The mouse drags and the cursor handling that feed the camera belong to the Scene view's page, and picking and :term[gizmos]{id=gizmo-start} belong there too.

## The problem and how engines solve it

A scene is a place with no natural "up close". A person who builds a level looks at one crate, then at the whole street, then at a lamp behind a wall. Three needs follow. The person wants to turn around the thing they look at without losing it, to slide sideways and move closer, and to jump to a chosen object and see all of it.

Editors answer the first need with an **editor camera**: the camera the person moves to look at the scene while they edit it, which no game contains. A free camera, as in a game, takes little code but loses the object: one slip of the mouse and it is out of view.

Most editors therefore add an **orbit camera**: a camera that always looks at one point and turns around it at a fixed distance, like a person walking around a statue.

To **orbit** is to turn the camera around its target at the same distance, so the object stays in the middle of the view.

The orbit camera describes itself with a point, a distance and two angles. The point is the **pivot**, here called the target. The distance says how far the camera stands from it. :term[Yaw]{id=yaw-angle} turns the camera around the vertical axis and pitch tilts it up or down. Spherical coordinates (two angles and a radius) are exactly this description, and the camera's position follows from them.

Three more moves complete the set. A pan slides the camera and its target together, parallel to the screen. A dolly moves the camera along its line of sight, nearer to the target or farther. Fly mode drops the target's role: the mouse turns the camera in place and keys move it, as in a game. The table at the end of this page lists the options Strata did not take.

The second need is framing. A tool must compute a camera that shows a box, and every answer costs something. A :term[bounding sphere]{id=bounding-sphere} is cheap and safe but backs off too far for a long thin box. The eight corners of the box give a tight fit but need more work, and the person may then orbit away to a view that cuts a corner. Strata offers both: a sphere for the Focus command and corners for the first view of a scene.

The third need is memory. A person who leaves a scene and returns expects the same view, so the editor stores one camera for each scene in the project. The fourth is a question of choice: the Scene view, the Game view and a picture taken by a command are all views of one scene, and each must know which camera it draws with.

## The map

The viewport state has one owner. `EditorViewport` holds the editor camera, the saved camera of each scene, the viewport settings and three :term[renderers]{id=renderer}. `EditorContext` owns it, so a command, the interface and a test reach it the same way. Nothing in this state needs the interface: a headless editor holds it too, without the renderers until the first view asks for one.

```mermaid caption="The viewport state: the editor camera and the settings feed one function that chooses the camera of a view, and each of the three renderers draws the result." alt="A diagram. Input and commands change the editor camera and the settings. The scene's own camera and the editor camera enter a function that chooses a view. Three renderers draw the chosen view: the Scene view, the Game view and the capture renderer."
flowchart LR
    Input[Panel input] --> Camera[EditorCamera]
    Commands[camera and viewport commands] --> Camera
    Commands --> Settings[ViewportSettings]
    Camera --> Resolve[ResolveViewportView]
    SceneCam[Scene's primary camera] --> Resolve
    Settings --> Resolve
    Resolve --> SV[Scene view renderer]
    Resolve --> GV[Game view renderer]
    Resolve --> CR[Capture renderer]
    Store[Camera of each scene] <--> Camera
    File[EditorViewport.json] <--> Store
```

An **editor view** is an image of the edited scene that the editor draws for the person's work, through the editor camera. It may add :term[overlays]{id=overlay-core} such as the grid, the selection outline and the shapes of lights and colliders. The Scene view is the main editor view. The Game view is never one, because it shows the game as the player sees it.

Each renderer keeps render targets and a history of its own: the earlier frames that effects such as temporal anti-aliasing blend into the new one. The Scene view's renderer and the Game view's renderer draw into panels. The third renderer serves captures, so a capture never disturbs the history of a panel and the panel never disturbs the capture's.

## The contract

The code of the editor camera and viewport follows rules that callers may rely on. Each has a reason.

1. **The camera never holds an invalid value.** Every function that sets a value checks that it is finite. It then clamps the value into a range: pitch to 89 degrees either way, the distance to 0.01 to 1,000,000 units, the :term[field of view]{id=field-of-view} to 1 to 170 degrees. Callers pass anything, including numbers from a command or a file, and the camera stays usable. A function that can fail returns false and changes nothing.
2. **The position is derived.** The camera stores the target and the distance, and the position is the target minus the forward direction times the distance. Two copies of the same fact would drift apart.
3. **A view change is not an edit.** The commands `camera.get`, `camera.set`, `camera.focus`, `viewport.getSettings`, `viewport.setSettings` and `viewport.capture` record no undo step and leave the scene unchanged. A person who presses **Ctrl+Z** undoes work on the scene, never a walk around it.
4. **A capture never moves the person's view.** A capture with a camera of its own works on a copy. The person's camera stays where they left it.
5. **Main thread only.** The viewport is state of the editor's main thread; the capture's encoding runs on a job, and the result returns through the command's poll.
6. **Views never wait for assets.** A view skips or substitutes what loads. Only a capture waits, and only by drawing again in later frames.

:::rule
Edits to a scene or project run as commands, so that a person can undo them and an agent can replay them. View changes are the exception: they record no undo step. Read [the command conventions](commands.md) for the kinds and the reason each exists.
:::

## A toy version: an orbit camera in numbers

Before the real code, build the camera from the numbers. The example is small enough to check by hand, and the sketch below does the same sums, so the reader can compare.

:::question
This page shows C++ code. If you have not met structs, functions and calls such as `std::pow(`, read [functions and structs](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md) first.
:::

The toy stores a target, a distance, a yaw, a pitch and a field of view. It computes the forward direction, the position, the world size of one pixel and the distance that frames a sphere. Notice the way the position comes out of the forward direction, and for the single line that makes a wheel step.

```cpp sketch="editor-camera-viewport-toy.cpp"
#include <cmath>
#include <cstdio>

constexpr double c_Pi = 3.14159265358979323846;

struct Vec3
{
	double X = 0.0;
	double Y = 0.0;
	double Z = 0.0;
};

// An orbit camera: a target, a distance and two angles in degrees. Nothing else is stored.
struct OrbitCamera
{
	Vec3 Target;
	double Distance = 10.0;
	double Yaw = 45.0;
	double Pitch = -30.0;
	double FOV = 60.0;
};

double ToRadians(double degrees)
{
	return degrees * c_Pi / 180.0;
}

// Yaw 0 looks along -Z; a positive pitch looks up.
Vec3 GetForward(const OrbitCamera& camera)
{
	const double yaw = ToRadians(camera.Yaw);
	const double pitch = ToRadians(camera.Pitch);
	return { -std::sin(yaw) * std::cos(pitch), std::sin(pitch), -std::cos(yaw) * std::cos(pitch) };
}

// The position is the target minus the forward direction times the distance.
Vec3 GetPosition(const OrbitCamera& camera)
{
	const Vec3 forward = GetForward(camera);
	return { camera.Target.X - forward.X * camera.Distance, camera.Target.Y - forward.Y * camera.Distance,
		camera.Target.Z - forward.Z * camera.Distance };
}

// World units one pixel covers at the target's depth.
double GetUnitsPerPixel(const OrbitCamera& camera, double viewportHeight)
{
	return 2.0 * camera.Distance * std::tan(ToRadians(camera.FOV) * 0.5) / viewportHeight;
}

// Each wheel step toward the target keeps 85 percent of the distance.
void Dolly(OrbitCamera& camera, double steps)
{
	camera.Distance *= std::pow(0.85, steps);
}

// The distance at which the bounding sphere of radius `radius` fits the narrower half field of view, with 10 percent room.
double GetFocusDistance(const OrbitCamera& camera, double radius, double aspectRatio)
{
	const double halfVertical = ToRadians(camera.FOV) * 0.5;
	const double halfHorizontal = std::atan(std::tan(halfVertical) * aspectRatio);
	return radius * 1.1 / std::sin(std::fmin(halfVertical, halfHorizontal));
}

int main()
{
	OrbitCamera camera;
	const Vec3 position = GetPosition(camera);
	std::printf("position: %.3f %.3f %.3f\n", position.X, position.Y, position.Z);
	std::printf("units per pixel at 720 pixels: %.4f\n", GetUnitsPerPixel(camera, 720.0));
	Dolly(camera, 5.0);
	std::printf("distance after 5 wheel steps: %.3f\n", camera.Distance);
	const double radius = std::sqrt(3.0);
	std::printf("focus distance, 16:9 view: %.3f\n", GetFocusDistance(camera, radius, 16.0 / 9.0));
	std::printf("focus distance, 1:2 view: %.3f\n", GetFocusDistance(camera, radius, 0.5));
	return 0;
}
```

```text output-of="editor-camera-viewport-toy.cpp"
position: 6.124 5.000 6.124
units per pixel at 720 pixels: 0.0160
distance after 5 wheel steps: 4.437
focus distance, 16:9 view: 3.811
focus distance, 1:2 view: 6.869
```

1. **Lines 29–34:** the forward direction from the yaw and pitch, the formula of the next section.
2. **Lines 37–42:** the position: the target minus the forward direction times the distance.
3. **Line 47:** the size of one pixel at the target's depth.
4. **Line 53:** one wheel step keeps 85 percent of the distance.
5. **Lines 57–62:** the sphere's framing distance against the narrower half angle.

The first line is the default view. The target is the origin, the distance is 10 units, the yaw is 45 degrees and the pitch is -30 degrees. The camera stands to the right, behind and above the origin: 6.124 units along +X, 5 units up and 6.124 units along +Z, and it looks back at the origin.

### The geometry, step by step

Start with the direction. Yaw 0 looks along $-Z$, as in the engine's :term[coordinate system]{id=coordinate-space}. Yaw 90 degrees looks along $-X$. Pitch tilts the line of sight: a positive pitch raises it and a negative pitch lowers it. With yaw $y$ and pitch $p$, both in degrees, the forward direction is:

$$f = (-\sin y \cos p,\ \sin p,\ -\cos y \cos p)$$

$f$ is the :term[unit vector]{id=unit-vector} the camera looks along; $\sin$ and $\cos$ are the :term[sine]{id=sine} and :term[cosine]{id=cosine} of an angle in degrees; $y$ is the yaw and $p$ the pitch. For the default $y = 45$ and $p = -30$, $\sin p = -0.5$ and $\cos p = 0.866$, so $f$ is about $(-0.612, -0.5, -0.612)$. The camera looks toward $-X$ and $-Z$ and downward, so it looks back at the origin from the $+X$, $+Z$ side and from above.

The position follows. The camera looks at the target, so it stands behind the target by the distance, against the forward direction:

$$c = t - d f$$

$c$ is the camera's position, $t$ is the target and $d$ is the distance, in world units; $d f$ is the forward vector scaled by $d$. With $t$ at the origin and $d = 10$, $c = (6.124, 5.0, 6.124)$, the line the sketch printed.

The orbit uses this formula in reverse: the target stays, the angles change, and the position moves on a sphere around the target. A drag of $n$ pixels turns the camera by $0.3 n$ degrees (the engine's constant is 0.3 degrees per pixel), and dragging right moves the scene with the mouse. The pitch stops at 89 degrees. At exactly 90 degrees the forward direction would point along the :term[up axis]{id=up-axis}, and the camera could not tell which way is right, so the view would flip. The clamp keeps one degree of margin.

:::analogy
The orbit camera is a person holding a lamp on a pole of fixed length and walking around a statue while looking at it. The yaw is the direction they stand in, the pitch is how high they lift the pole, and the length of the pole is the distance.

**Where it breaks:** a real pole has a fixed length, while the camera's distance changes with every wheel step and with every focus.
:::

To **pan** is to slide the camera and its target together, parallel to the screen. A pan needs the size of a pixel in the world. Imagine a vertical slice through the view at the target's depth. Its height in world units is $2 d \tan(\phi / 2)$, where $\phi$ is the vertical field of view, because the half angle $\phi / 2$ and the distance form a right triangle. Divide by the viewport's height in pixels $h$ and one pixel covers:

$$u = \frac{2 d \tan(\phi / 2)}{h}$$

$u$ is the world units one pixel covers at the target's depth, $d$ the distance, $\phi$ the vertical field of view and $h$ the viewport's height in pixels. The default $d = 10$ and $\phi = 60$ degrees at $h = 720$ give $u = 2 \cdot 10 \cdot 0.5774 / 720 = 0.016$ units. A drag of 100 pixels moves the target by 1.6 units, so the point under the mouse at the target's depth follows the mouse exactly. Points nearer or farther follow at other speeds, which is how perspective works. The effect of the distance is natural: the closer the camera, the finer the pan.

To **dolly** is to move the camera along its line of sight, nearer to the target or farther. The wheel scales the distance: one step toward the target keeps 85 percent of it, so $n$ steps give $d \cdot 0.85^n$. Five steps from 10 units end at 4.437 units. A scale gives the same feel at every distance: a step at 1,000 units moves the camera 150 units, and a step at 1 unit moves it 0.15 units.

Last, the framing distance. A sphere of radius $r$ centred on the target fits inside a cone of half angle $\alpha$ when the camera is $r / \sin \alpha$ away. The 10 percent margin gives:

$$d = \frac{1.1\, r}{\sin \alpha}$$

$d$ is the camera's distance, $r$ the sphere's radius in world units and $\alpha$ the narrower of the vertical and horizontal half fields of view. A tall view has the narrow horizontal angle. The sketch's last line shows the price: the same sphere needs 6.869 units in a view half as wide as it is tall, against 3.811 units in a 16:9 view.

Check the limits. With $\alpha$ near 90 degrees, $\sin \alpha$ is 1 and the camera stands at $1.1 r$, outside the sphere. With $\alpha$ near 0, the distance grows without bound, which is why the field of view stops at 1 degree. A radius of 0 would put the camera on the target; the engine raises the radius to at least 0.1 units.

:::example[Focus, turn and capture]
A scene holds one box from $(-1, 0, -1)$ to $(1, 2, 1)$. Its centre is $(0, 1, 0)$ and its half extents are $(1, 1, 1)$, so the bounding sphere has radius $\sqrt{3} = 1.732$. The Scene view is hidden, so the aspect ratio is the default 1280 by 720, which is 1.778.

The half vertical angle is 30 degrees. The half horizontal angle is $\arctan(\tan 30° \cdot 1.778) = 45.7°$. The narrower one is 30 degrees, so the distance is $1.732 \cdot 1.1 / 0.5 = 3.811$ units.

Frame the whole scene by running `camera.focus` with empty parameters. The target moves to $(0, 1, 0)$ and the distance becomes 3.811; the yaw and pitch stay as they were.

```json
{}
```

Turn the camera to look straight along the scene with `camera.set`, giving only the angles. The target and the distance stay, so the position moves.

```json
{ "yaw": 0, "pitch": -20 }
```

The forward direction is now $(0, -0.342, -0.940)$, so the position is $(0, 1, 0) - 3.811 \cdot (0, -0.342, -0.940) = (0, 2.303, 3.581)$. A call of `camera.get` returns this position, the target, the forward direction, the yaw, the pitch and the distance.

Take the picture with `viewport.capture`, giving the camera by name.

```json
{ "camera": "editor" }
```

The result holds the PNG, its size and the name of the camera. Since the scene has no light of its own, the result also says `previewLighting: true`, and the picture shows the box lit by the editor's preview sun and sky.
:::

## The real code

The code follows the toy in every formula. The differences are the guards, the double precision, the second framing method and the state around the camera.

### The camera's controls

`EditorCamera` stores exactly the toy's five numbers and adds the near and :term[far planes]{id=far-plane} and a fly speed, but never the position. Its `Update` function takes one frame of input and chooses one move. Fly mode wins while the right button is down; otherwise the camera orbits (**Alt** and the left button) or pans (middle button). The wheel then scales the distance, unless fly mode is on. The Scene view's page explains how the drags start and how the cursor is locked.

**Fly** mode turns the camera in place with the mouse and moves it with the keys. `Look` changes the yaw and pitch, and the target moves so the position stays.

The keys **W** and **S** move along the line of sight and **A** and **D** sideways, and **E** moves up and **Q** down along the world's up axis. The wheel does not change the distance in this mode; it multiplies the fly speed by 1.25 per step. **Shift** makes the flight four times faster. A diagonal move is scaled to length 1, so flying forward and right is as fast as flying forward. Starting from the default speed of 5 units per second, two wheel steps give 7.8 units per second, and with **Shift** held, 31.25 units per second.

The next quote holds the two moves whose formulas the toy derived. Notice the unit conversion in `Pan`, the sign of its two terms and the arithmetic in `Dolly`.

```cpp src="StrataEditor/src/Editor/EditorCamera.cpp#L84-L100"
void EditorCamera::Pan(const glm::vec2& deltaPixels, float viewportHeight)
{
	if (!(viewportHeight > 0.0f))
		return;
	// World units per pixel at the target's depth.
	const float unitsPerPixel = 2.0f * m_Distance * std::tan(glm::radians(m_FOV) * 0.5f) / viewportHeight;
	SetTarget(m_Target - GetRight() * (deltaPixels.x * unitsPerPixel) + GetUp() * (deltaPixels.y * unitsPerPixel));
}

void EditorCamera::Dolly(float steps)
{
	if (!std::isfinite(steps))
		return;
	// In double precision and clamped there: many steps overflow to infinity, which clamps to the limit.
	const double distance = static_cast<double>(m_Distance) * std::pow(static_cast<double>(c_DollyPerStep), static_cast<double>(steps));
	m_Distance = static_cast<float>(std::clamp(distance, static_cast<double>(c_MinDistance), static_cast<double>(c_MaxDistance)));
}
```

1. **Line 89:** the toy's formula for one pixel, in `float`. The guard at line 86 stops a zero-height viewport from producing infinity.
2. **Line 90:** the target moves against the mouse's horizontal drag and with its vertical drag, so the scene follows the mouse. The result goes through `SetTarget`, which rejects non-finite values and clamps to a billion units.
3. **Line 98:** the distance is computed in `double`. Many steps in a row would overflow a smaller number; the double overflows to infinity instead, and the clamp turns infinity into the maximum.
4. **Line 99:** the clamp to 0.01 and 1,000,000 units. The camera never reaches its target and never travels beyond a million units from it.

### Framing

**Framing** is moving the camera so that chosen bounds fill the view, without changing the direction it looks in. `Focus` is the toy's sphere formula with two additions. The radius never drops below 0.1 units, so a point-like object still gets a usable distance. And if the far end of the sphere would lie beyond the far plane, the far plane moves out to 1.1 times that, so the whole object stays visible.

`FitBounds` does not use the sphere. It tests every corner of the box against the view, and the bit tests (`corner & 1`) in its loop pick the minimum or maximum of the box on each axis. The best distance is the largest one that any corner demands.

Measure a corner from the box's centre: $x$ sideways, $y$ up and $z$ along the view, positive away from the camera. The corner lies inside the view, with the margin, when $1.1 |x| \le t_h (d + z)$, where $t_h$ is the tangent of the half horizontal angle and $d$ is the distance. The same holds for $y$ with the vertical tangent. The camera must also keep the nearest corner beyond twice the :term[near plane]{id=near-plane}.

```cpp src="StrataEditor/src/Editor/EditorCamera.cpp#L151-L161"
float distance = c_MinFocusRadius * c_FocusMargin / std::min(tanVertical, tanHorizontal);
float farthest = 0.0f;
for (int corner = 0; corner < 8; corner++)
{
	const glm::vec3 point((corner & 1) ? bounds.Max.x : bounds.Min.x, (corner & 2) ? bounds.Max.y : bounds.Min.y, (corner & 4) ? bounds.Max.z : bounds.Min.z);
	const glm::vec3 offset = point - center;
	const float x = std::abs(glm::dot(offset, right));
	const float y = std::abs(glm::dot(offset, up));
	const float z = glm::dot(offset, forward);
	distance = std::max({ distance, c_FocusMargin * x / tanHorizontal - z, c_FocusMargin * y / tanVertical - z, m_Near * 2.0f - z });
	farthest = std::max(farthest, z);
```

1. **Line 151:** the starting distance is a floor, so an almost empty box still gets a distance.
2. **Lines 155–156:** each of the eight corners, taken from the bits of the loop counter, as an offset from the centre.
3. **Lines 157–159:** the corner's position in the camera's own axes: sideways and up as absolute values, and `z` signed along the view.
4. **Line 160:** the largest of four requirements: the current best, the sideways fit, the vertical fit and the near plane. A corner closer to the camera than the centre has a negative `z`, which raises the distance.
5. **Line 161:** the largest `z` remembers how far behind the centre the box reaches, for the far plane.

The result is a tight fit, and it costs a property: after the camera orbits, a corner can leave the view. `Focus` never has this problem, because a sphere looks the same from every side. Strata therefore uses `FitBounds` for the first view of a scene, where the direction is fixed. It uses `Focus` for the commands, the **F** key (the selection) and the **Home** key (the whole scene), because the person will orbit next. In the example of exercise 2, the box 20 units wide needs 11.22 units with `FitBounds` and 22.05 with `Focus`.

### Which camera each view uses

A view needs a camera before it needs anything else, and three views need three answers. The function that gives them is short, and its main cases follow the state of the editor. The quote shows `ResolveViewportView`. Notice the two reasons to use the scene's camera, the fallback when it does not exist and the flag that says whether the result is an editor view.

```cpp src="StrataEditor/src/Editor/ViewportRenderer.cpp#L27-L52"
Scene& scene = *context.GetActiveScene();
ViewportView view;
const bool wantsSceneCamera = source == ViewportCameraSource::Scene || (source == ViewportCameraSource::Automatic && context.GetSceneState() == SceneState::Play);
if (wantsSceneCamera)
{
	if (Entity camera = scene.GetPrimaryCameraEntity())
	{
		view.Camera = SceneCamera::FromEntity(scene, camera, aspectRatio);
		view.Lens = CameraLens::FromEntity(scene, camera);
		view.FromScene = true;
		return view;
	}
	if (source == ViewportCameraSource::Scene)
	{
		if (outError)
			*outError = "The scene has no active entity with a Camera component marked Primary";
		return std::nullopt;
	}
	view.Notice = "The scene has no primary camera: showing the editor camera";
}
view.Camera = context.GetViewport().GetCamera().GetSceneCamera(aspectRatio);
view.EditorOverlays = true;
// The editor camera asked for by name is always a view for working on the scene (the Scene view while the game
// plays); the automatic choice's fallback while playing shows the running game as it is.
view.EditorView = source == ViewportCameraSource::Editor || context.GetSceneState() != SceneState::Play;
return view;
```

1. **Line 29:** the scene's camera is wanted when the caller says so, or when the source is automatic and the game plays.
2. **Lines 32–38:** a :term[primary camera]{id=primary-camera} exists, so the view takes it, and its lens settings. The result is not an editor view, and it carries no editor overlays.
3. **Lines 39–44:** the caller asked for the scene's camera and there is none, so the function fails with a message. An automatic choice does not fail.
4. **Line 45:** the fallback, and the notice that says why the editor camera is on screen.
5. **Line 51:** the editor camera asked for by name is always an editor view; the automatic fallback while the game plays is not, so the running game shows as it is.

The three views build on this function.

| View | What it asks | When there is no primary camera |
| --- | --- | --- |
| Scene view | The editor camera; with **Game camera** on (key **F8**), the scene's camera dressed in editor overlays | Shows the editor camera, with a notice |
| Game view | Always the scene's camera | Draws only the game's user interface (UI) over black, or a notice that the scene has no camera |
| Capture | Whatever the command asks for: automatic, the editor, the scene, or a camera of its own | The editor camera with a notice, or a failure when the scene's camera was named |

`ResolveSceneView` adds the **Game camera** switch. This setting, called `PilotGameCamera` in the code, lets a person look through the game camera while the editor's grid and gizmos stay on. `ResolveGameView` is the strictest: it never uses the editor camera, because the Game view's job is to show what the player will see. A scene without a camera but with a user interface still produces an image, a default camera over black with the interface drawn over it.

`GetViewportRenderOptions` turns a view into renderer options. An editor view gets the preview environment when the setting `PreviewLighting` is on, and the game's screen-space text and canvases only when `ShowGameUI` is on. So a scene without lights is lit in the editor, and its heads-up display (HUD) does not cover the work. The game's own views get neither: what you see in the Game view is what the player sees.

```mermaid caption="How a view chooses its camera: the scene's primary camera when one exists and is wanted, otherwise the editor camera, and a failure only when the scene's camera was demanded." alt="A diagram. A view first asks whether it wants the scene's camera. If it does and a primary camera exists, it uses that camera. If none exists, a view that demanded it fails, and any other view falls back to the editor camera with a notice. A view that does not want the scene's camera uses the editor camera."
flowchart TD
    A{Wants the scene's camera?} -- no --> E[Editor camera]
    A -- yes --> B{Primary camera exists?}
    B -- yes --> S[Scene's camera]
    B -- no --> C{Demanded by name?}
    C -- yes --> F[Fail with a message]
    C -- no --> E
```

### State saved with the project

`ViewportSettings` holds the view's options. Some switch overlays: the grid, the selection outline, the shapes of lights and colliders (for every collider, or only the selection's), frame statistics, the game's UI and the cell bounds of a world. Some change what the view draws: preview lighting, the debug view, the canvas mode for UI work, the pose skinned characters show while editing and a quality preset for the Scene view. The rest belong to tools: the gizmo mode and space, the snap steps, the Game view's mode and size and the game-camera switch. The theme sets some colours, such as the outline's, and they are not saved.

`EditorViewport` stores, next to the settings, the camera of every scene the person has shown. When the project closes, the whole state is written to `<project>/.strata/EditorViewport.json`, and it is restored when the project opens. The file holds a `Camera` (the current one), a `Cameras` map from a scene's handle to its camera, and the `Settings`. An older file without `Cameras` keeps its single camera for the first scene that opens without one. The camera's loader reads each number as a `double` and checks the range before anything changes, so a damaged file cannot leave a half-applied camera.

A scene shown for the first time has no stored camera. `FinishOpenScene` then calls `FrameScene`. It orients the camera along the scene's primary camera, the direction its author chose to show the scene from, and fits the scene's content with `FitBounds`. Meshes that still load stand in as placeholder boxes, so the first framing may be wrong.

The editor remembers which meshes were pending, and `UpdatePendingFrame` frames the scene again once they have loaded. It does so only while the person has not touched the camera, the scene is still the open one and the time limit has not passed. A person who moves the camera first keeps their view.

### The view commands

Six commands expose all of this. `camera.get` reads the camera: position, target, forward direction, yaw, pitch, distance, field of view, clip planes and fly speed. `camera.set` changes it on a copy and applies the copy only if every part is valid. A `position` with a `target` looks from one to the other, and the angles and the distance may not come with them.

`camera.focus` frames the given entities, or the whole scene when none are named, and fails with a message when the scene is empty. `viewport.getSettings` and `viewport.setSettings` read and change the options of the viewport, and `viewport.setSettings` applies all or none. None of the six records an undo step.

### Captures

A **capture** is a picture of the edited scene that a command renders and returns; it is not a screenshot of the viewport. The difference matters because a screenshot shows whatever the panel happened to hold, at the panel's size, with the history of the panel. A capture renders on purpose, through the capture renderer, which keeps a history of its own, so asking for a picture never disturbs a panel.

The command `viewport.capture` is deferred: it starts, and a poll runs in each following frame until the picture is ready ([Deferred commands](deferred-commands.md) explains polls). The command picks the size before its first poll. It is the `width` and `height` given, or else the Scene view's size, 1280 by 720 while the view is hidden. A capture through the scene's camera takes the Game view's size when that view keeps an aspect ratio.

The command also picks the camera: the editor camera, the scene's, or a camera of its own built from `position`, `target` and `fov`. A camera of its own is a copy of the editor camera with those changes, so the person's view stays where it was.

The first poll renders. If something in the image is still incomplete, the next polls render again, and the renderer's history starts over each time, so the final picture blends complete frames only. The quote shows the tests, one for each reason to wait. Notice the frame limit that each reason carries.

```cpp src="StrataEditor/src/Editor/EditorViewportCommands.cpp#L784-L810"
const bool textPending = progress.PendingTextGlyphs + progress.UI.PendingGlyphs > 0 && progress.TextFrames < c_MaxCaptureTextFrames;
const bool assetsPending = request.WaitForAssets && progress.PendingAssets > 0 && progress.AssetFrames < c_MaxCaptureAssetFrames;
const bool mipsPending = request.WaitForAssets && progress.TexturesBelowWanted > 0 && progress.MipFrames < c_MaxCaptureMipFrames;
const bool posesPending = request.WaitForAssets && progress.StalePoses > 0 && progress.PoseFrames < c_MaxCapturePoseFrames;
const bool instancesPending = request.WaitForAssets && progress.DeferredProxies > 0 && progress.InstanceFrames < c_MaxCaptureInstanceFrames;
// The motion view shows the motion since the capture renderer's previous frame, which its first frame lacks.
const bool motionPending = progress.DebugView == ViewportDebugView::Motion && !stats.MotionHistory && progress.MotionFrames == 0;
// Probes wait only for their captures to load (the capture renderer converts every one at once): an asset wait.
const uint32_t probesPending = request.WaitForAssets ? progress.ReflectionProbesPending : 0u;
const bool lightingPending = progress.LocalShadowViewsPending + probesPending > 0 && progress.LightingFrames < c_MaxCaptureLightingFrames;
// Until its pre-exposure settled the frame's brightest and darkest values may have clamped or lost bits.
const bool exposurePending = !stats.PreExposureSettled && progress.ExposureFrames < c_MaxCaptureExposureFrames;
// Global illumination's voxels: until nothing is left to voxelize.
const bool giPending = !stats.GlobalIlluminationSettled && progress.GIFrames < c_MaxCaptureGIFrames;
const bool contentPending = textPending || assetsPending || mipsPending || posesPending || instancesPending || motionPending || lightingPending
	|| exposurePending || giPending;
// Temporal anti-aliasing: the mean of the jitter's phases of the complete view, as the viewport shows a still view once it
// settled. A frame still incomplete starts the history again (the capture's targets are released after each picture,
// so each one starts it anyway), so the picture blends complete frames only.
const bool temporalPending = !contentPending && stats.TemporalAntiAliasing && stats.TemporalFrames < c_TemporalSettleFrames
	&& progress.TemporalFrames < c_MaxCaptureTemporalFrames;
// Spatial screen-space reflections read the previous frame's color, which a view's first frame lacks.
const bool reflectionsPending = !contentPending && stats.ScreenSpaceReflectionsPending && progress.ReflectionFrames < c_MaxCaptureReflectionFrames;
if (contentPending || temporalPending || reflectionsPending)
{
	if (contentPending)
		renderer->GetSceneRenderer().ResetHistory();
```

1. **Line 784:** glyphs of text still waiting to be turned into pixels: up to 120 frames.
2. **Line 785:** meshes, materials and textures still loading, when the command waits for assets: up to 300 frames, about five seconds at 60 :term[frames per second]{id=frame-rate}.
3. **Lines 786–788:** textures drawn coarser than the view wants (120 frames), animators showing an old pose (8) and new mesh renderers not yet uploaded (120).
4. **Line 797:** global illumination still settling. Its limit is 54 frames, the 38 frames the renderer needs plus 16.
5. **Lines 803–810:** temporal anti-aliasing and reflections settle only after the content is complete, and only content that is still incomplete resets the history.

Shadow views of point and spot lights and the pre-exposure (the brightness scale the renderer settles on) add two more reasons, with limits of 16 and 8 frames. Temporal anti-aliasing may take up to 16 more frames, and spatial reflections 2. The limits bound the wait: a scene that never finishes loading still produces a picture, and the result says what it lacked.

When the waits end, the renderer's output is read back with a `TextureReadback`, polled once a frame without a stall ([readback timing](../gpu/readback-timing.md) explains why). A job encodes the pixels as PNG, so compressing a large image does not hitch the frame, and an input and output job saves the file when the caller gave a path. The command fails after 30 seconds if the :term[graphics processing unit]{id=gpu} (GPU) never finishes. The result reports what it knows about the picture: `waitedFrames`, `pendingAssets`, `texturesBelowWanted`, `previewLighting`, and the hidden canvases and text. A caller that sees `pendingAssets` above zero knows the picture is incomplete.

A live capture (`live: true`, with `atFixedStep` and `frames` up to 16) renders nothing. It reads back what a view presented, to see motion exactly as it played. It reads the view's last frame, because every command poll runs before the views render in that frame. Armed after `play.start` with a pause, it takes frames at chosen :term[fixed steps]{id=fixed-step}. The picture of a live capture is exactly the player's frame, trails and smearing included, which a fresh render would not reproduce.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Free camera only, no target | The camera of a game | Fewer fields; one move | The object leaves the view after a slip; no orbit, no focus point |
| Orbit angles as a rotation (a :term[quaternion]{id=quaternion}) | A tool that keeps an orientation | No limit near the poles; roll | A person can roll the camera and lose the horizon; the pitch limit is simple to explain |
| Framing with a sphere only | A tool with one formula | One formula | A long thin box backs off twice as far as it needs |
| One camera for the whole project | A tool with little state | Less state to save | Every scene opens at the wrong place; a person must find it again |
| Dolly by a fixed distance per step | A simple viewer | Linear and simple to predict | Too slow far away and too fast close to the target |
| Capture by reading the panel's image | A screenshot tool | No second render | The picture has the panel's size, history and unfinished loading |

## How it is tested

Three suites cover the page's code. `Editor.Camera` tests the camera without a GPU. It checks the default view, the direction of yaw and pitch, orbit against look, panning and the wheel with its limits. It also checks the mapping from input to moves, `Focus` and `FitBounds`, `LookAt` and the :term[JSON]{id=json} round trip with its invalid documents.

`Editor.Viewport` tests the state around it. It checks `camera.get`, `camera.set` and `camera.focus`, the view following the play state and the settings' round trip. It also checks the camera stored for each scene with the first framing, editor views against the game's views, and `viewport.setSettings` as an atomic change. `GPU.Editor.Viewport` runs captures on a real device. It checks the size and camera of a capture, encoding on job threads, saving to the project and replacing files only on request.

Run them directly from the build with a doctest filter.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite="Editor.Camera"
build/windows/bin/Debug/StrataTests.exe --test-suite="Editor.Viewport"
ctest --preset windows-debug -L gpu
```

The first two lines need no GPU. The third runs every GPU test, which include the capture tests. A regression test for this code starts from the camera's contract: a value that cannot be set, set anyway, must leave the camera unchanged.

## Changing it safely

New view state goes into `ViewportSettings` and its JSON, with a name in `viewport.getSettings` and `viewport.setSettings`, so that a person and an agent reach it the same way. A new camera move goes into `EditorCamera` with a test in `Editor.Camera`, and the panel only maps input to it. A new reason for a capture to wait gets a named constant for its limit, with a comment. It also gets a field in the progress record and a field in the result. A wait without a limit hangs a command.

:::rule
A command that has to wait returns a deferred result. Its poll keeps its own data and allocates nothing per frame. `viewport.capture` follows this with its poll, and a new wait extends that poll, never a loop inside the command. See [Deferred commands](deferred-commands.md).
:::

Keep these rules in mind. Never write the camera's fields from outside; use the functions that check. Never store the position, and never let a view change record an undo step. Never create a renderer for a capture inside a panel: the capture renderer keeps the two histories apart. Run `Editor.Camera`, `Editor.Viewport` and the GPU viewport tests before merging.

## Summary

- The editor camera is a target, a distance, a yaw and a pitch; its position is the target minus the forward direction times the distance. Pan moves target and camera by the world size of a pixel at the target's depth, and dolly scales the distance by 0.85 per wheel step.
- `Focus` fits the bounding sphere at 1.1 times its radius over the sine of the narrower half angle; `FitBounds` tests the eight corners and is tighter.
- The Scene view uses the editor camera (or the game camera on **F8**), the Game view always the scene's camera, and a capture the camera its command names. `ResolveViewportView` is the one place that decides.
- A capture renders on purpose with a renderer of its own, waits with a limit for each unfinished thing, reads back without a stall and leaves the person's view where it was.

## Check yourself

1. The camera has target $(0, 0, 0)$, distance 20, yaw 0 and pitch 0. Where is it, and which way does it look?

   :::answer{tests="camera-model"}
   Forward is $(0, 0, -1)$, so the position is $(0, 0, 0) - 20 \cdot (0, 0, -1) = (0, 0, 20)$. The camera stands 20 units along +Z and looks toward the origin along $-Z$.
   :::

2. A person drags with the middle button 50 pixels to the right, in a viewport 500 pixels high with a 90 degree field of view and the camera 10 units from the target. How far does the target move, and in which direction? (a) 1 unit along the camera's right; (b) 1 unit against the camera's right; (c) 2 units against the camera's right; (d) 0.5 units against the camera's right.

   :::answer{tests="camera-model"}
   (c). One pixel covers $2 \cdot 10 \cdot \tan 45° / 500 = 0.04$ units, and $50 \cdot 0.04 = 2$ units. The target moves against the right direction, so the scene follows the mouse. Option (a) has the wrong sign and the wrong size, (b) has the right sign and the wrong size, and (d) forgets the factor of 2 in the height of the slice.
   :::

3. The view is 1:2 (twice as tall as wide) with a vertical field of view of 60 degrees. For a sphere of radius 1, does `Focus` use the vertical or the horizontal angle, and is the distance larger or smaller than in a 16:9 view?

   :::answer{tests="framing"}
   The horizontal half angle is $\arctan(0.5774 \cdot 0.5) = 16.1°$, smaller than 30°, so the horizontal angle limits and $d = 1.1 / \sin 16.1° = 3.97$ units. In a 16:9 view the vertical angle limits and $d = 1.1 / 0.5 = 2.2$ units. The tall view needs a larger distance.
   :::

4. The Game view's scene has no primary camera and no UI canvas. What does the Game view show? And what does a `viewport.capture` with `camera: "scene"` do?

   :::answer{tests="view-choice"}
   `ResolveGameView` asks for the scene's camera and gets none. With no overlay content either, it returns nothing, so the Game view draws a message that the scene has no camera instead of an image. The capture asks for the scene's camera by name, so it fails with a message that the scene has no active entity with a Camera component marked Primary. An automatic capture would instead fall back to the editor camera with a notice.
   :::

5. A capture runs on a scene whose textures load slowly. After 300 frames, assets still load. What does the command return? (a) an error; (b) a picture of what had loaded, with `pendingAssets` above zero and `waitedFrames` reporting the extra frames; (c) it waits forever; (d) the picture of the previous capture.

:::answer{tests="capture-wait"}
(b). The wait has a limit: 300 frames for assets. After it, the poll reads the picture back anyway and reports what was still pending. A partial picture still helps, so it is not an error, and every reason to wait has a limit, so the command never waits forever. The capture renderer starts its history again, so the picture never comes from an earlier capture.
:::

## Exercises

1. **Basic.** The default camera has a vertical field of view of 60 degrees and a distance of 10. The viewport is 1080 pixels high. Compute the world units one pixel covers, and the distance after the camera dollies three steps toward the target.

   :::answer[Worked solution]{tests="camera-model"}
   One pixel covers $2 \cdot 10 \cdot \tan 30° / 1080 = 20 \cdot 0.57735 / 1080 = 0.01069$ units. Three steps keep $0.85^3 = 0.614$ of the distance, so $10 \cdot 0.614 = 6.141$ units. Closer to the target a pixel covers less: $0.01069 \cdot 0.614 = 0.00656$ units.
   :::

2. **Medium.** A box 20 units wide and 1 unit deep and tall is seen by a camera with yaw 0 and pitch 0, a 60 degree vertical field of view and a 16:9 view. Compute the distances that `Focus` and `FitBounds` choose. The sketch is yours to run and compare.

   :::answer[Worked solution]{tests="framing"}
   `Focus` uses the bounding sphere. Its radius is $\sqrt{10^2 + 0.5^2 + 0.5^2} = 10.025$. The narrower half angle is 30 degrees, so $d = 10.025 \cdot 1.1 / 0.5 = 22.05$ units. `FitBounds` tests each corner: the sideways requirement of a corner at $x = 10$ is $1.1 \cdot 10 / 1.0264 = 10.717$, and a corner on the near side ($z = -0.5$) adds 0.5, so the camera needs 11.217 units. The sketch repeats the loop for all eight corners.

   ```cpp sketch="editor-camera-viewport-fit.cpp"
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   // A camera looking along -Z (yaw 0, pitch 0) with a 60 degree vertical field of view, at a 16:9 view.
   constexpr double c_Margin = 1.1;
   constexpr double c_Near = 0.1;

   int main()
   {
   	const double tanVertical = std::tan(30.0 * 3.14159265358979323846 / 180.0);
   	const double tanHorizontal = tanVertical * 16.0 / 9.0;
   	// A box 20 units wide and 1 unit deep and tall, centered on the origin.
   	const double half[3] = { 10.0, 0.5, 0.5 };

   	// Focus: the bounding sphere against the narrower half field of view (30 degrees: sin = 0.5).
   	const double radius = std::sqrt(half[0] * half[0] + half[1] * half[1] + half[2] * half[2]);
   	std::printf("focus distance: %.3f\n", radius * c_Margin / 0.5);

   	// FitBounds: every corner must lie inside the view, so the camera backs off as far as the worst corner needs.
   	double distance = 0.0;
   	for (int corner = 0; corner < 8; corner++)
   	{
   		const double x = std::fabs(corner & 1 ? half[0] : -half[0]);
   		const double y = std::fabs(corner & 2 ? half[1] : -half[1]);
   		const double z = (corner & 4) ? half[2] : -half[2]; // Along the view: positive is away from the camera
   		distance = std::max({ distance, c_Margin * x / tanHorizontal - z, c_Margin * y / tanVertical - z, c_Near * 2.0 - z });
   	}
   	std::printf("fit distance: %.3f\n", distance);
   	return 0;
   }
   ```

   ```text output-of="editor-camera-viewport-fit.cpp"
   focus distance: 22.055
   fit distance: 11.217
   ```

   1. **Line 17:** the sphere's radius from the three half extents.
   2. **Line 18:** the sphere's distance with the sine of the narrower half angle.
   3. **Lines 22–28:** the corner loop: the sideways and vertical requirements, the near plane and the running maximum.

   The box is long and thin, so the corners need half the distance that the sphere needs.
   :::

3. **Hard.** Trace it yourself. Select an entity, run `camera.focus` with a breakpoint in `EditorCamera::Focus`, and check the distance it sets against the radius times 1.1 over the sine of the narrower half angle.

:::answer[Worked solution]{tests="framing"}
Search the engine for the command: `camera.focus` is registered in `StrataEditor/src/Editor/EditorViewportCommands.cpp`, and its handler calls `EditorViewport::Focus` in `StrataEditor/src/Editor/EditorViewport.cpp`. That function gets the bounds from `SceneBounds::GetEntitiesBounds` and calls `EditorCamera::Focus` in `StrataEditor/src/Editor/EditorCamera.cpp`. At the breakpoint, read the bounds, compute the radius as the length of the half extents, and compute the half angles from `m_FOV` and the aspect ratio. After the step over `SetDistance`, the value of `m_Distance` equals the formula, except where the clamp to 0.01 and 1,000,000 units applies.
:::

## Where it lives in Strata

- Camera: `StrataEditor/src/Editor/EditorCamera.h` and `EditorCamera.cpp`.
- Viewport state, settings and renderers: `StrataEditor/src/Editor/EditorViewport.h` and `EditorViewport.cpp`.
- Which camera a view uses: `StrataEditor/src/Editor/ViewportRenderer.cpp`.
- View commands and captures: `StrataEditor/src/Editor/EditorViewportCommands.cpp`.
- The first framing: `EditorContext::FinishOpenScene` and `EditorContext::UpdatePendingFrame` in `StrataEditor/src/Editor/EditorContext.cpp`.
- Tests: the suites `Editor.Camera`, `Editor.Viewport` and `GPU.Editor.Viewport`.
- Saved state: `<project>/.strata/EditorViewport.json`.

## Further reading

- The Unity Manual, "Scene view navigation": the orbit, pan, zoom and fly moves of another editor; beginner.
- Physically Based Rendering: From Theory to Implementation, the chapter on camera models: how a perspective camera relates to the field of view; intermediate.
- Game Programming Patterns, the chapter "Game Loop": why input is read once per frame; beginner.
