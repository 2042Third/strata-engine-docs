---
id: gpu/coordinates
title: "Coordinate systems and the camera: clip space, reversed depth, UVs"
description: "How a cube placed in the editor reaches a pixel and a depth value, and which conventions Strata fixes for axes, clip space, depth, UVs and winding."
kind: concept
size: M
tracks: [E]
needs: [basics/math-projection, basics/numbers, core/math, world/scene-graph, gpu/how-a-gpu-frame-works]
time: 40
learn:
  - id: chain-of-spaces
    text: trace a point through the spaces from object to pixel and back from a pixel and its depth
  - id: strata-conventions
    text: name Strata's conventions for axes, clip space, UVs and front faces, and the reason for each
  - id: depth-precision
    text: compute the distance step of a float depth buffer for standard and reversed depth
  - id: camera-types
    text: explain what CameraComponent, GetProjection and SceneCamera each hold
  - id: fullscreen-triangle
    text: compute the three corners of the fullscreen triangle from the vertex index
since: 0.3.0
status: final
---

You place a cube in the editor, 4.5 meters in front of the camera and a little up and to the right. The cube appears on some pixels, and the engine stores a depth value for each of them. Which pixels, and which depth?

The answer is a chain of conversions, and every link of it is a convention that someone had to choose. A tutorial written for another graphics system may choose differently. Copy its formulas into Strata and the image turns upside down, or distant surfaces flicker and fight. This page shows the chain, the choices Strata made and the price of each.

## Textbook formulas fail in two ways

Two failures show how much hangs on the conventions.

The first is a flipped image. Most older tutorials turn a position into a texture coordinate with `uv = ndc * 0.5 + 0.5`. That formula assumes that the bottom of the screen has the smallest Y. Strata's images store their first row at the top, so the same formula draws every fullscreen effect upside down.

The second is flicker in the distance. A :term[depth buffer]{id=depth-buffer} stores a number for each pixel, and a number has only so many digits. If the spread of those digits is wrong, two surfaces 0.2 meters apart at 500 meters get the same stored value. The :term[graphics processing unit]{id=gpu} (GPU) cannot tell which is in front, and the two fight from frame to frame. Strata's depth convention exists to prevent that.

## The idea: a chain of spaces

A **space** is a way of measuring where things are: an origin, three axes and a unit. The same cube corner has different numbers in each space. The :term[renderer]{id=renderer} moves a point from one space to the next with a matrix, and the chain below is the same for every object. The mathematics of each step, with the view and projection matrices, is in [Cameras and projection](../basics/math-projection.md); this page names Strata's version of each space.

```mermaid caption="The chain of spaces. Each arrow is one transformation; the last two arrows are the only ones that depend on the graphics interface." alt="Seven boxes in a row: object, world, camera, clip, device coordinates, pixel and texture coordinates, joined by arrows labeled model, view, projection, divide and viewport."
flowchart LR
    A["Object"] -->|"model"| B["World"]
    B -->|"view"| C["Camera"]
    C -->|"projection"| D["Clip"]
    D -->|"divide by w"| E["NDC"]
    E -->|"viewport"| F["Pixel"]
    E -->|"x 0.5 + 0.5"| G["Texture coordinates"]
```

The diagram shows what the next paragraphs name.

- **Object space** holds the mesh as its artist made it, around the origin of the model.
- **World space** is the scene's one shared space. Strata is :term[right-handed]{id=handedness}, +Y points up and the camera looks along −Z.
- **Camera space** (also view space) puts the camera at the origin, looking down −Z.
- **Clip space** holds the four-component positions the projection makes, before the divide by the fourth component, $w$.
- **Normalized device coordinates** (NDC) are the three numbers after the divide. Everything inside the view lies in a box: X and Y from −1 to 1, depth from 0 to 1.
- The **framebuffer** space counts pixels, and **texture coordinates** count the same image from 0 to 1.

### Worked example: the cube corner

Take one corner of the cube, at (0.5, 0.5, −0.5) in object space, on the face that looks at the camera. The cube's entity stands at (0, 0, −4) in the world, with no rotation and a scale of 1. The camera stands at the origin and has no rotation. It has a vertical :term[field of view]{id=field-of-view} of 60 degrees, a :term[near plane]{id=near-plane} at 0.1 meters, a :term[far plane]{id=far-plane} at 1000 meters, and the image is 1920 by 1080 pixels.

1. :term[World space]{id=world-space}: add the entity's position. The corner is at (0.5, 0.5, −4.5).
2. Camera space: the camera sits at the origin without rotation, so the numbers stay (0.5, 0.5, −4.5). The corner is 4.5 meters ahead.
3. :term[Clip space]{id=clip-space}: the focal length is $1 / \tan(30°) = 1.732$ and the aspect ratio is $16 / 9 = 1.778$. Clip X is $1.732 / 1.778 \times 0.5 = 0.487$ and clip Y is $1.732 \times 0.5 = 0.866$. The fourth component $w$ is the distance, 4.5.
4. NDC: divide by $w$. X is 0.108 and Y is 0.192. The depth is 0.0221, which the section on depth derives.
5. Texture coordinates: $u = 0.108 \times 0.5 + 0.5 = 0.554$ and $v = 0.5 - 0.192 \times 0.5 = 0.404$.
6. Pixel: multiply by the size. The pixel is at (1063.9, 436.1), a little right of the center and a little above it.

The path back needs the same steps in reverse. A pixel and its depth give NDC, and the inverse of the projection gives a camera-space position: from depth 0.0221 the distance is $nf / (d(f - n) + n) = 4.5$ meters, which fixes X and Y from the NDC values. The effects that read a stored depth, such as ambient occlusion, rebuild positions like this. The code that turns a pixel into a ray is in [the math chapter](../core/math.md).

## Right-handed, Y up and Z forward

In a right-handed system, when the fingers of your right hand curl from +X to +Y, the thumb points along +Z. The other choice, left-handed, mirrors every scene. Neither is more correct, and Strata picks the glTF convention: +Y is up and an entity looks along its own −Z. This choice means a glTF model needs no conversion, and `Strata/src/Strata/Math/Math.h` states it at the top as the convention of all engine math.

## Direct3D-style clip space and the viewport flip

The graphics interface Strata draws with is Vulkan, and Vulkan chose a clip space in which +Y points down. Direct3D chose +Y up, and so did OpenGL, but OpenGL counts pixel rows from the bottom. The matrices of the textbooks assume +Y up. Strata keeps the textbook form, a clip space with +Y up, depth from 0 to 1 and pixel row 0 at the top of the image.

Two ways exist to reconcile that with Vulkan. The :term[shader]{id=shader} :term[compiler]{id=compiler} can flip Y in every vertex shader.

Or the **viewport flip** can do it: the program gives Vulkan a viewport with a negative height, which turns the whole image over when it leaves the vertex stage. NVRHI, the layer Strata draws through, does the second, in its Vulkan function `VKViewportWithDXCoords`. Strata does not ask the shader compiler to flip, and the comment in `CMake/StrataShaders.cmake` says why: the compile flags `-fvk-invert-y` and `-fvk-use-dx-position-w` stay off because NVRHI already flips the viewport. Both flips together would cancel.

:::why[Why not flip in the shaders?]
One flip at one place keeps every shader in the same convention as the C++ math, and a shader author never meets a Vulkan sign. A second flip would be a bug that only shows on the screen. The cost is that the engine trusts NVRHI to flip on every backend, and a shader written for plain Vulkan formulas draws upside down.
:::

### Texture coordinates and the fullscreen triangle

An image's row 0 is its top row, and V grows downward. From NDC, where +Y is up, the conversion is the one formula of the shader include `Strata/shaders/Include/Common.slang`: $u = x \times 0.5 + 0.5$ and $v = 0.5 - y \times 0.5$. The V formula has a minus, and that minus is what the formula of the opening lacks. The inverse is $x = 2u - 1$ and $y = 1 - 2v$.

Many effects only need to visit every pixel of the image once: tone mapping, blur, fog. For them Strata draws a **fullscreen triangle**: one triangle, larger than the image, that covers the whole viewport. A rectangle would need two triangles and a diagonal seam. One oversize triangle has no seam and needs no vertex buffer, because the vertex shader makes the three corners from the vertex number alone.

The shader `Strata/shaders/PostProcess/Fullscreen.vert.slang` does it in a few lines. Look at how the vertex index becomes a corner, then at the call of `NDCToUV`:

```slang src="Strata/shaders/PostProcess/Fullscreen.vert.slang#L8-L13" symbol="st_Main"
void st_Main()
{
	float2 ndc = float2(float((st_VertexIndex << 1) & 2), float(st_VertexIndex & 2)) * 2.0 - 1.0;
	v_UV = NDCToUV(ndc);
	st_Position = float4(ndc, 0.0, 1.0);
}
```

The shift `<< 1` moves the bits left by one, which doubles the index $i$. So $i$ gives $x_0 = (2i) \,\&\, 2$ and $y_0 = i \,\&\, 2$, where & is a bitwise and that keeps bit 1. For $i = 0, 1, 2$ the pairs are (0, 0), (2, 0) and (0, 2). Doubling and subtracting 1 gives the NDC corners (−1, −1), (3, −1) and (−1, 3).

The triangle's long edge runs from (3, −1) to (−1, 3), along $x + y = 2$, and the image's far corner (1, 1) lies exactly on it. The visible square, from −1 to 1, is covered whole, and the GPU clips away the rest. The texture coordinates of the corners are (0, 1), (2, 1) and (0, −1), and the GPU blends them to the right value at every pixel.

## Front faces are counter-clockwise

A triangle has two sides, and a closed mesh shows only the outer one. The **winding order** is the direction, clockwise or counter-clockwise, in which a triangle's corners run on the screen. The side where they run counter-clockwise is the front face, and the GPU can skip triangles that show the other side (back-face culling).

The rule for which direction means "front" is the **winding** of a mesh, and every engine fixes one.

Strata follows glTF: front faces are counter-clockwise. `SceneRenderer.cpp` builds its pipelines with `setFrontCounterClockwise(key.Mirrored == backFacePass)`: counter-clockwise is the front for an instance that does not mirror, in a pass that draws front faces. The `Mirrored` flag marks instances whose transform mirrors, such as a negative scale on one axis; such a transform turns the triangle's direction around on the screen, so the pipeline turns the rule around too. A pass that draws the back faces turns it around as well. How that works, and the tangents it affects, is the subject of [mirrors and camera-relative space](../draw/mirrors-camera-relative.md).

## Depth: why Strata clears to zero

Depth is where the conventions matter most. The projection stores the camera-space distance $z$ as a depth $d$. The stored values do not spread evenly over the distances. Standard depth maps the near plane to 0 and the far plane to 1. The spread is steep near the camera and flat far away, so most of the numbers between 0 and 1 serve the first few meters.

A :term[floating-point number]{id=floating-point-number} is the opposite: it has the most precision near 0 and the least near 1. Standard depth pairs the crowded end of the distances with the sparse end of the numbers, and the two weaknesses add up. **Reversed Z** swaps the planes, so near is 1 and far is 0, and the two imbalances cancel. For a camera that sees 0.1 to 10,000 meters, the table gives the distance step: how far apart two surfaces must be to receive different stored values in a 32-bit float. Exercise 2 computes it with a sketch.

| Distance | Standard depth | Reversed depth |
| --- | --- | --- |
| 1 m | 0.0006 mm | 0.00007 mm |
| 10 m | 0.06 mm | 0.0009 mm |
| 100 m | 6 mm | 0.012 mm |
| 1,000 m | 0.6 m | 0.07 mm |
| 9,000 m | 48 m | 0.09 mm |

At 1,000 meters the standard mapping cannot tell apart two surfaces closer than about 0.6 meters, and at 9,000 meters not closer than 48 meters. The reversed mapping stays below 0.1 mm across the whole range, and the rows near the camera show that it costs nothing there.

### The approaches engines use

Each answer to the depth problem fixes a flaw of the one before.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Standard depth, near 0, far 1, test `Less` | None | Far surfaces fight, whatever the format | Lowest | Most older tutorials |
| :term[Reversed Z]{id=reversed-z}, float depth | None: only the clear and the test change | Near-even precision over the range | Low; every clear, test and projection must agree | Strata's scene |
| Reversed Z, infinite far plane | None; the far plane is lost | Slightly better still; nothing is cut off far away | Low; no far distance to tune | Strata's math code offers it; no camera uses it |
| Log depth | The pixel shader writes depth, which disables early depth tests | Even over huge ranges | High; every shader must write it | Special-purpose renderers |

The sources of Further reading describe all four. The **infinite far plane** is the limit of the far distance going to infinity. The projection's depth becomes $n / z$ for the near distance $n$ and the camera distance $z$, so the far end clips nothing.

`PerspectiveReverseZInfinite` in `Strata/src/Strata/Math/Math.cpp` builds that projection. At the pin only math tests and debug-draw tests call it, and the camera keeps its finite far plane.

:::example[The depth of the cube corner]
The corner is $z = 4.5$ meters ahead, with $n = 0.1$ and $f = 1000$. The reversed depth is $n(f - z) / (z(f - n)) = 0.1 \times 995.5 / (4.5 \times 999.9) = 0.0221$. A corner at the near plane gives 1, and a corner at the far plane gives 0. The standard depth for the same corner is $f(z - n) / (z(f - n)) = 0.9779$: the same corner sits at the crowded end of the floats.
:::

## Strata's choice and its rules

Strata chose reversed Z with a 32-bit float depth buffer (`D32`) and a finite far plane. Four rules follow, and every pass keeps all four:

- The renderer clears the depth buffer to 0, which is the far plane. `SceneRenderer.cpp` does so, and clears each shadow map to 0.0 as well.
- The test passes when the new depth is larger. The **depth test functions** are the choices of how the GPU compares a new depth with the stored one (`Less`, `Equal`, `GreaterOrEqual` and more). The prepass uses `GreaterOrEqual`, and the opaque pass that follows uses `Equal`, because the prepass has already written the nearest depth.
- Anything that stays at depth 0 is the sky or background: shaders such as `Strata/shaders/Effects/GTAO.comp.slang` start with `if (depth <= 0.0)` to skip it.
- Every projection that `GetProjection` builds follows this convention, so code that reads a camera's matrices can rely on it.

:::why[Why a float buffer and reversed Z?]
An :term[integer]{id=integer} depth buffer spreads its values evenly, so reversing it gains little; the gain comes from the float format. A 32-bit float costs more memory than 24 bits, and Strata pays that so that far surfaces hold still. The cost of reversing is discipline: copying the clear value 1 and the test `Less` from a tutorial draws far surfaces over near ones.
:::

## The camera component and what the renderer receives

A camera in a scene is an entity with a `CameraComponent`. Its fields are the projection type (`Perspective` or `Orthographic`) and the vertical field of view in degrees (default 60). Then come the near and far planes (0.1 and 1000), the orthographic size (10 world units of height) and its own near and far planes. Then come the `Primary` flag (set by default), the `ClearColor` and the depth-of-field fields.

The **primary camera** is the camera that renders the game view: the first active entity in hierarchy order whose `Primary` flag is set. How the scene finds it is in [the scene graph](../world/scene-graph.md), and the depth-of-field fields are the subject of the image chapter.

The Inspector marks a property that does nothing as inactive, with a reason. The perspective fields say "The camera's projection is Orthographic" when the projection is orthographic, and the orthographic fields say the reverse. The method `GetProjection` takes the aspect ratio and builds the matrix. Read how it protects against bad values:

```cpp src="Strata/src/Strata/Scene/Components.cpp#L7-L24" symbol="CameraComponent::GetProjection"
glm::mat4 CameraComponent::GetProjection(float aspectRatio) const
{
	if (!(aspectRatio > 0.0f) || !std::isfinite(aspectRatio))
		aspectRatio = 1.0f;

	if (Projection == ProjectionType::Perspective)
	{
		const float nearClip = std::max(PerspectiveNear, 1e-4f);
		const float farClip = std::max(PerspectiveFar, nearClip + 1e-3f);
		const float fov = glm::radians(std::clamp(PerspectiveFOV, 1.0f, 179.0f));
		return Math::PerspectiveReverseZ(fov, aspectRatio, nearClip, farClip);
	}

	const float halfHeight = std::max(OrthographicSize, 1e-4f) * 0.5f;
	const float halfWidth = halfHeight * aspectRatio;
	const float farClip = std::max(OrthographicFar, OrthographicNear + 1e-3f);
	return Math::OrthographicReverseZ(-halfWidth, halfWidth, -halfHeight, halfHeight, OrthographicNear, farClip);
}
```

1. **Lines 9–10:** an aspect ratio that is zero, negative or not a number becomes 1.
2. **Lines 14–16:** the near plane has a floor of 0.0001 and the far plane stays at least 0.001 beyond it. The field of view stays between 1 and 179 degrees, so no matrix divides by zero.
3. **Line 17:** the perspective case calls the reversed-Z function of the math code.
4. **Lines 20–23:** the orthographic case makes a box from the size and the aspect ratio; its near plane may even be negative.

The renderer never reads the component. Every renderer receives a `SceneCamera`, declared in `Strata/src/Strata/Renderer/SceneRenderer.h`. It holds the :term[view matrix]{id=view-matrix}, the projection in Strata's clip space, the position and the near and far distances. It also holds a vertical field of view for choosing levels of detail (the size, for an orthographic camera), an orthographic flag and the clear color.

`SceneCamera::FromEntity` builds it from an entity. The function uses the entity's translation and rotation but never its scale, so a scaled camera does not distort the image.

The lens settings for depth of field live in a separate :term[struct]{id=struct}, `CameraLens`, and not in `SceneCamera`. The reason is in the header: the whole value of `SceneCamera` is the cache key of the shadow cascades, so a change to the camera draws the shadows again, and focusing must not.

The clear color deserves care. The component stores it as an :term[sRGB]{id=srgb} color, the way a color picker shows it. The renderer converts it to linear light and multiplies by the pre-exposure before it fills the :term[high dynamic range]{id=high-dynamic-range} (HDR) image.

Exposure and tone mapping then change it like any other pixel, so a clear color of (0.05, 0.05, 0.07) looks darker or lighter than the picker shows. Only the neutral post-processing setup (manual exposure 0, no tone curve, no vignette) shows it unchanged.

## What these choices cannot do

Reversed Z with a finite far plane still has limits. Two surfaces at the same depth, such as a sticker mesh laid on a wall, still fight and need a bias. The far plane cuts off everything beyond it. A shader that rebuilds a far position from a stored depth loses digits when it subtracts.

Rendering far from the origin has its own precision problem, covered in [mirrors and camera-relative space](../draw/mirrors-camera-relative.md). Strata also has no log depth and no left-handed mode; see [what Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **Clearing depth to 1 or testing `Less`.** Symptom: far surfaces draw over near ones. Fix: clear to 0 and test `GreaterOrEqual`.
- **Using the GLSL texture coordinate formula.** Symptom: a post effect appears upside down. Fix: use `NDCToUV`, with $v = 0.5 - y \times 0.5$.
- **Flipping Y in a shader because Vulkan does.** Symptom: the image is upside down only in the shader you changed. Fix: leave the flip to NVRHI.
- **Taking a matrix from a standard-depth source.** Symptom: far surfaces fight, or the depth test keeps the wrong surface. Fix: build matrices with `PerspectiveReverseZ`.
- **Treating the clear color as final.** Symptom: the color differs from the picker. Fix: expect exposure and tone mapping to change it.

## Summary

- Each point crosses object, world, camera, clip, NDC and pixel spaces, and the pixel with its depth leads back through the inverse projection.
- Strata is right-handed with +Y up and −Z forward, uses Direct3D-style clip space through NVRHI's viewport flip, has texture coordinates with row 0 at the top, and front faces counter-clockwise.
- A float depth buffer is most precise near 0, so reversed Z gives far surfaces precision: 0.07 mm against 0.6 meters at 1,000 meters.
- `CameraComponent` holds the lens fields and builds the projection with `GetProjection`; `SceneCamera` is the plain view that each renderer receives.
- The fullscreen triangle's corners come from the vertex index: (−1, −1), (3, −1) and (−1, 3).

## Check yourself

1. Far surfaces cover near ones after you port a depth setup from a tutorial, but the shaders are right. Which setting is the most likely cause?
   - A. The depth buffer is cleared to 1 and the test is `Less`.
   - B. The depth buffer is 32-bit float.
   - C. The viewport is flipped by NVRHI.
   - D. The camera has `Primary` set.

   :::answer{tests="strata-conventions"}
   A. Strata stores near as 1 and far as 0, so with a clear of 1 and the test `Less` the smaller, farther depth wins. B is Strata's own format, C is the intended flip, and D is only the choice of camera.
   :::

2. A camera sees 0.1 to 10,000 meters. About how far apart must two surfaces at 100 meters be for the standard float depth to tell them apart, and what does reversed Z give?

   :::answer{tests="depth-precision"}
   The table gives 0.006 meters (6 mm) for standard depth and 0.0000116 meters (about 0.012 mm) for reversed depth. Reversed Z is about 500 times finer there.
   :::

3. A vertex index of 1 enters the fullscreen shader. What are its NDC position and its texture coordinates?
   :::answer{tests="fullscreen-triangle"}
   $x_0 = (1 \ll 1) \,\&\, 2 = 2$ and $y_0 = 1 \,\&\, 2 = 0$. The NDC corner is (2 × 2 − 1, 0 × 2 − 1) = (3, −1). The texture coordinates are $(3 \times 0.5 + 0.5,\ 0.5 - (-1) \times 0.5) = (2, 1)$.
   :::

4. A point has NDC (0.5, 0.5). Which pixel of a 1000 by 500 image does it land on, and which of these mistakes would move it to the bottom half?
   :::answer{tests="chain-of-spaces"}
   $u = 0.75$ and $v = 0.5 - 0.25 = 0.25$, so the pixel is (750, 125), in the top half. Using $v = y \times 0.5 + 0.5$ gives 0.75 and the pixel (750, 375): the image is turned upside down.
   :::

5. A designer says that changing a camera's `ClearColor` to a mid-gray gives a darker gray on screen. Which piece of the pipeline explains it, and what happens to the cached shadow cascades?
   :::answer{tests="camera-types"}
   The clear color becomes linear and pre-exposed :term[HDR]{id=high-dynamic-range} light, so exposure and tone mapping change it. The whole `SceneCamera`, its clear color too, is the cascades' cache key, so the change draws them once again. Only the lens fields stay out, in `CameraLens`.
   :::

## Exercises

1. **Basic.** Derive the corners for vertex indices 0 to 2 and show that the triangle covers the visible square.

   :::answer[Worked solution]{tests="fullscreen-triangle"}
   Index 0 gives (−1, −1), index 1 gives (3, −1) and index 2 gives (−1, 3), as in the text. The edges are the line $y = -1$, the left line $x = -1$ and the long edge $x + y = 2$. The square's corners (±1, ±1) satisfy $y \ge -1$, $x \ge -1$ and $x + y \le 2$, with the corner (1, 1) on the long edge. All of the square is inside.
   :::

2. **Hard.** Measure the float depth step of both mappings from 0.2 meters to 9,000 meters, and check the 1,000 meter row by hand.

   :::answer[Worked solution]{tests="depth-precision" solution="sketches/gpu-coordinates-depthstep.cpp"}
   The sketch has one function for each depth and one for the step: the gap between a float and the next one up, divided by the slope of depth.

   ```cpp sketch="gpu-coordinates-depthstep.cpp"
   #include <cmath>
   #include <cstdio>

   // Depth of a point z meters ahead of the camera, with a [0, 1] projection (near n, far f).
   double StandardDepth(double z, double n, double f)
   {
   	return f * (z - n) / (z * (f - n));
   }

   double ReversedDepth(double z, double n, double f)
   {
   	return n * (f - z) / (z * (f - n));
   }

   // Meters between two neighbouring float depth values near z: the float spacing divided by the slope of depth.
   double DistanceStep(double depth, double z, double n, double f)
   {
   	const float stored = static_cast<float>(depth);
   	const double spacing = static_cast<double>(std::nextafter(stored, 2.0f)) - static_cast<double>(stored);
   	const double slope = n * f / (z * z * (f - n));
   	return spacing / slope;
   }

   int main()
   {
   	const double nearClip = 0.1;
   	const double farClip = 10000.0;
   	const double distances[] = { 0.2, 1.0, 10.0, 100.0, 1000.0, 9000.0 };

   	std::printf("%8s %14s %14s\n", "z (m)", "standard (m)", "reversed (m)");
   	for (const double z : distances)
   	{
   		const double standardStep = DistanceStep(StandardDepth(z, nearClip, farClip), z, nearClip, farClip);
   		const double reversedStep = DistanceStep(ReversedDepth(z, nearClip, farClip), z, nearClip, farClip);
   		std::printf("%8.1f %14.3g %14.3g\n", z, standardStep, reversedStep);
   	}
   	return 0;
   }
   ```

   ```text output-of="gpu-coordinates-depthstep.cpp"
      z (m)   standard (m)   reversed (m)
        0.2       2.38e-08       1.19e-08
        1.0       5.96e-07       7.45e-08
       10.0       5.96e-05       9.31e-07
      100.0        0.00596       1.16e-05
     1000.0          0.596       7.28e-05
     9000.0           48.3       9.21e-05
   ```

   1. **Lines 5–13:** the two depth formulas of the text.
   2. **Lines 16–21:** the spacing of the next float over the slope.
   3. **Lines 30–35:** one row per distance, for both mappings.

   By hand at $z = 1000$: the slope is $0.1 \times 10000 / (10^6 \times 9999.9) = 10^{-7}$. The standard depth is 0.99991, where floats are $2^{-24} = 6 \times 10^{-8}$ apart, so the step is 0.6 meters. The reversed depth is $9 \times 10^{-5}$, between $2^{-14}$ and $2^{-13}$, where floats are $2^{-37} = 7 \times 10^{-12}$ apart, so the step is $7 \times 10^{-5}$ meters.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Math/Math.h` and `Math.cpp`: the conventions comment, `PerspectiveReverseZ`, `PerspectiveReverseZInfinite`, `OrthographicReverseZ`.
- `Strata/src/Strata/Scene/Components.h` and `Components.cpp`: `CameraComponent` and `GetProjection`.
- `Strata/src/Strata/Scene/ComponentRegistration.cpp`: the properties the Inspector shows for a camera, and their inactive reasons.
- `Strata/src/Strata/Renderer/SceneRenderer.h` and `SceneRenderer.cpp`: `SceneCamera`, `SceneCamera::FromEntity`, the depth clear and the pipelines' depth and winding state.
- `Strata/shaders/Include/Common.slang`: `NDCToUV` and `UVToNDC`; `Strata/shaders/PostProcess/Fullscreen.vert.slang`.
- `CMake/StrataShaders.cmake`: the compile flags that stay off because of the viewport flip.
- In the editor: the **Camera** component in the Inspector, under the Rendering category.

## Further reading

- Nathan Reed, "Depth Precision Visualized": why float depth and reversed Z fit together (intermediate).
- The Microsoft Direct3D documentation on depth buffers and the viewport transform (intermediate).
- Brano Kemen, "Logarithmic Depth Buffer" (advanced).
- The glTF 2.0 specification, on its coordinate system and the winding of triangles (beginner).
