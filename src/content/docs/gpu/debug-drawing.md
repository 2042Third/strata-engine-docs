---
id: gpu/debug-drawing
title: "Overlays, debug drawing and gizmos"
description: "How Strata draws what helps people see a scene over the finished image: the grid, outlines, tints, debug lines, gizmos, text and the game's UI."
kind: internals
size: L
tracks: [E]
needs: [gpu/frame-tour, world/tutorial-component]
time: 75
learn:
  - id: overlay-order
    text: explain in which order the renderer draws its overlays, and which ones need the entity-ID buffer
  - id: record-lines
    text: write code that records debug lines in both depth modes and say what the renderer does with them
  - id: gizmo-path
    text: trace a component gizmo from its registration to the lines it adds to the debug draw list
  - id: overlay-registry
    text: explain how a module adds a pass to every renderer without the renderer naming the module
  - id: jitter-bias
    text: explain why overlays placed in the scene use constants without jitter and a one pixel depth bias under TAA
since: 0.3.0
status: final
---

The scene :term[renderer]{id=renderer} makes a picture of the world as a camera sees it. People who edit that world need more than the picture. They need a grid for the floor, an outline around the selected object, a sphere that shows how far a light reaches, or a number floating over a crate. Players need their game's menus and score on top of the picture too.

This page shows how Strata draws all of that over the finished image, in exact display colors. It also shows how a module above the renderer adds its own drawing without the renderer knowing the module. Picking, the handles you drag, the quads of the game's user interface (UI), fonts, the debug views, temporal anti-aliasing (TAA) and level of detail (LOD) selection have pages of their own.

## The problem and how engines solve it

Consider what a finished frame is at the end of the renderer's work: a picture of lit surfaces, already blended, filtered and tone mapped to the values a screen shows. Now an editor wants to put a green box around a collider. The collider has no surface, so nothing in the scene draws it. The box belongs to the person's view of the scene, not to the scene.

A **gizmo** is a shape the editor draws over the scene to show something that has no surface, such as a light's reach or a collider.

Engines meet four demands here. Shapes must appear for one frame without the caller managing any object. Colors must arrive exactly as the author picked them, not lit and tone mapped. Some shapes must hide behind walls, and others must stay visible through them. And code far from the renderer, such as a game's UI, must draw into the same picture.

Four approaches solve parts of this.

- **Retained shapes.** The engine keeps a list of shape objects, each with an owner and a lifetime. The code that made a shape must remove it or move it. This fits shapes that live long, such as a light's icon, but the owner must track every change.
- **Immediate-mode lines.** Each frame, code calls a function such as `Line(from, to, color)`. The engine stores the line until the frame is drawn, and then the owner clears the list. Nothing lasts beyond the frame, so nothing needs removing. Cost: you repeat the calls every frame, even for a shape that never moves.
- **Real scene objects.** A gizmo becomes an entity with a mesh. The scene's own passes draw it, with lighting and shadows. Building this is simple, but the entity appears in the hierarchy, in saved files and in picking, and tone mapping changes its color.
- **A second drawing library.** The editor draws lines into the window with its UI library. It needs no renderer support, but it cannot test the lines against the scene's depth, so everything shows through walls.

The last demand, drawing from a higher module, needs a different tool. The renderer sits low in the engine, and the game UI sits above it. If the renderer called the UI, a low layer would depend on a high one, and the layer rules of [Layers, registries and the composition root](../core/layers-registries.md) forbid that. The usual cure is :term[dependency inversion]{id=dependency-inversion}: the renderer defines an interface and a registry, and the higher module puts an object into the registry. The renderer calls whatever it finds there and never names the module.

Strata uses the second approach and the registry. The editor and other code record immediate-mode lines into one list per frame, in two depth modes. A function turns each component's gizmo request into such lines. The renderer draws the list over the finished image, with the same code path for every line. Modules above it, such as the game UI, register passes that every renderer then makes and calls.

:::example[One green line, byte by byte]
The collider color of the editor's gizmos is a green: red 0.3, green 1.0, blue 0.45, alpha 1.0. A line stores four :term[bytes]{id=byte}, not four floats. Each channel is cut to the range 0 to 1, multiplied by 255, and rounded by adding 0.5 before the cut to a whole number.

Red is 0.3 × 255 + 0.5 = 77.0, which is 77 or 0x4D. Green is 255.5, which becomes 255 or 0xFF. Blue is 0.45 × 255 + 0.5 = 115.25, which is 115 or 0x73. Alpha is 255 or 0xFF.

Red sits in the lowest byte, so the line's color is 0xFF73FF4D. The renderer writes that value into the output as it is, so the green on your screen is the green in the code.
:::

## The map: files, owners and the overlay order

Strata keeps the pieces in a few files of `Strata/src/Strata/Renderer/`. `DebugDraw.h` and `DebugDraw.cpp` hold the line recorder. `SceneGizmos.h` and `SceneGizmos.cpp` turn lights, cameras and component gizmos into lines. `SceneOverlay.h` holds the screen view, the pass interface and the registry. `SceneRenderer.cpp` draws everything in `RenderOverlays`.

The component gizmo types live in `Strata/src/Strata/Reflection/ComponentGizmo.h`, because a module that owns a component fills them without including the renderer.

The picture below shows who calls whom in one frame of the editor's Scene view. Every arrow is a call on the :term[main thread]{id=main-thread}: the recorder is not thread-safe, and the registry of passes is for the main thread only.

```mermaid caption="The editor's viewport code fills the line recorder and passes it to the renderer, which draws it. Higher modules reach the renderer only through the registry of passes." alt="A flow diagram with the editor viewport at the left filling a line recorder through the gizmo function and other code. The recorder feeds the scene renderer. The game UI module puts a pass into the registry, and the renderer reads the registry."
flowchart LR
    V["Editor viewport"] --> G["Gizmo function"]
    G --> D["Line recorder"]
    V --> D
    P["Physics and other modules"] -. "gizmo shapes" .-> G
    D --> R["Scene renderer"]
    U["Game UI module"] -. "adds a pass" .-> Q["Registry of passes"]
    Q --> R
```

An **overlay** is something drawn over the finished image: the grid, the selection outline, tints, debug lines, text and the game's UI. The order matters because later overlays cover earlier ones. The renderer draws them after post-processing, in this order.

```mermaid caption="The order of the overlays, first to last. The views and tints color the scene itself, and the lines on top, the text of the screen and the game UI end the frame." alt="A list of steps from top to bottom: the image, views, tints, the grid, tested lines, world text, scene passes, the outline, lines on top, screen text and screen passes."
flowchart TB
    A["Image after post-processing"] --> B["Lighting, motion or shadow view"]
    B --> C["Entity tints"]
    C --> D["Grid"]
    D --> E["Debug lines, tested against depth"]
    E --> F["World text"]
    F --> G["Passes of modules, in the scene"]
    G --> H["Selection outline"]
    H --> I["Debug lines, on top"]
    I --> J["Text of the screen"]
    J --> K["Passes of modules, over the screen"]
```

The order has a logic. The views and tints change the colors of the scene, so everything else goes over them. Things that belong to the scene's space, which hide behind walls, come next. The outline comes after them, because it traces the silhouette of what is selected and should stay clear. Lines marked to stay on top come after the outline, and the screen's own text and UI come last, because nothing may cover a menu.

::figure{id=overlays-off}

::figure{id=overlays-on}

## The contract

Callers of the overlay code may assume the following, and must do the following.

1. **Overlays are drawn after post-processing, into the output.** The values written are display values, sRGB-encoded. A color you give is the color that appears, with alpha blending against the image. Do not give a linear or :term[high dynamic range]{id=high-dynamic-range} (HDR) color, and do not expect bloom or tone mapping to touch an overlay.
2. **Lines are for one frame.** The owner of a `DebugDraw` fills it, passes it in `SceneRenderOptions::DebugShapes`, and clears it before the next frame. The renderer never clears it and never keeps a pointer to it.
3. **Overlays placed in the scene use constants without jitter.** With TAA the scene's depth is drawn from a camera that moves by up to half a pixel each way. The overlays draw with the camera's own matrices, so lines and glyphs do not shimmer. Their depth tests therefore get a bias of one pixel's worth of slope.
4. **Tints and the outline need the entity-ID buffer.** A renderer made without `SceneRendererSpecification::EntityIDs` reports an error, leaves those two overlays out, draws all others, and marks the frame as degraded.
5. **The renderer reaches higher modules only through registries.** Passes of the game UI, and gizmos of physics components, reach it through `SceneOverlayRegistry` and `ComponentInfoBuilder::Gizmo`.

:::rule[The renderer includes no higher module]
`AGENTS.md` says the renderer reaches higher modules only through registries, such as `SceneOverlayRegistry` and component gizmos. The reason is the :term[layer table]{id=layer-table}: a renderer that includes the game UI makes a low layer depend on a high one. The mistake looks harmless, one include and one call, and it is exactly the mistake that the registry exists to prevent. The check is the `Architecture.Layering` test of [Layers, registries and the composition root](../core/layers-registries.md).
:::

## A toy version

Before the real code, here is a recorder that does the job in miniature. It keeps two lists of line ends, one per depth mode. It packs colors as the engine does, with red in the lowest byte. Before a pretend upload it joins the lists, tested lines first, and subtracts the camera position in double precision.

```cpp sketch="gpu-debug-drawing-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Vertex
{
	float X = 0.0f;
	float Y = 0.0f;
	float Z = 0.0f;
	uint32_t Color = 0;
};

enum class Depth : uint8_t
{
	Tested = 0,
	OnTop
};

// Red in the lowest byte, each channel clamped to [0, 1] and rounded to a byte.
uint32_t PackColor(float red, float green, float blue, float alpha)
{
	const float channels[4] = { red, green, blue, alpha };
	uint32_t packed = 0;
	for (int index = 0; index < 4; index++)
	{
		const float clamped = std::clamp(channels[index], 0.0f, 1.0f);
		packed |= static_cast<uint32_t>(clamped * 255.0f + 0.5f) << (8 * index);
	}
	return packed;
}

// Records lines during a frame; the renderer reads them once and the owner clears them.
class LineRecorder
{
public:
	void Line(const Vertex& from, const Vertex& to, Depth depth)
	{
		std::vector<Vertex>& list = m_Lists[static_cast<size_t>(depth)];
		list.push_back(from);
		list.push_back(to);
	}

	void Clear()
	{
		m_Lists[0].clear();
		m_Lists[1].clear();
	}

	const std::vector<Vertex>& GetVertices(Depth depth) const { return m_Lists[static_cast<size_t>(depth)]; }
private:
	std::vector<Vertex> m_Lists[2];
};

// What the renderer does before the upload: one list, tested lines first, positions relative to the camera.
std::vector<Vertex> PrepareUpload(const LineRecorder& recorder, double cameraX)
{
	std::vector<Vertex> upload = recorder.GetVertices(Depth::Tested);
	const std::vector<Vertex>& onTop = recorder.GetVertices(Depth::OnTop);
	upload.insert(upload.end(), onTop.begin(), onTop.end());
	for (Vertex& vertex : upload)
		vertex.X = static_cast<float>(static_cast<double>(vertex.X) - cameraX);
	return upload;
}

int main()
{
	const uint32_t orange = PackColor(1.0f, 0.5f, 0.0f, 1.0f);
	std::printf("orange packs to %08X\n", orange);

	LineRecorder recorder;
	recorder.Line({ 5000000.5f, 2.0f, 0.0f, orange }, { 5000003.0f, 2.0f, 0.0f, orange }, Depth::OnTop);
	recorder.Line({ 5000001.0f, 0.0f, 0.0f, orange }, { 5000001.0f, 4.0f, 0.0f, orange }, Depth::Tested);
	std::printf("tested vertices: %zu, on top: %zu\n", recorder.GetVertices(Depth::Tested).size(), recorder.GetVertices(Depth::OnTop).size());

	const std::vector<Vertex> upload = PrepareUpload(recorder, 5000000.0);
	for (const Vertex& vertex : upload)
		std::printf("x = %.1f\n", vertex.X);

	const float far = 5000000.5f;
	std::printf("floats near %.1f are %.7f apart\n", far, std::nextafter(far, 1.0e9f) - far);
	std::printf("floats near 2.5 are %.7f apart\n", std::nextafter(2.5f, 1.0e9f) - 2.5f);
	recorder.Clear();
	std::printf("after Clear: %zu vertices\n", recorder.GetVertices(Depth::Tested).size() + recorder.GetVertices(Depth::OnTop).size());
	return 0;
}
```

```text output-of="gpu-debug-drawing-toy.cpp"
orange packs to FF0080FF
tested vertices: 2, on top: 2
x = 1.0
x = 1.0
x = 0.5
x = 3.0
floats near 5000000.5 are 0.5000000 apart
floats near 2.5 are 0.0000002 apart
after Clear: 0 vertices
```

1. **Line 29:** each channel is clamped, scaled to a byte and shifted by eight bits per channel, so red lands in the lowest byte.
2. **Lines 38–42:** a line adds both ends to the list of its depth mode, so the two modes never mix.
3. **Lines 57–65:** the upload joins the lists, tested lines first, and moves every position relative to the camera.
4. **Line 63:** the subtraction runs in double, and only its small result returns to a float.
5. **Lines 81–83:** the spacing of floats near the world position and near the shifted one, which is the whole reason for the shift.

The sketch prints a packed orange, the counts per mode and the positions after the shift. Look at the last lines. A float near five million can only land on multiples of 0.5, but after the subtraction the same lines have small positions, where floats are fine to 0.0000002. That is the reason the real renderer makes lines relative to the camera before the upload, and why [camera-relative space](../draw/mirrors-camera-relative.md) exists at all.

## The real code, in the order the data flows

The real code differs from the toy in four ways: it draws, it has many shapes, it omits what is not in view and it has passes from other modules. The sections below follow one frame.

### Recording lines

A debug line is two end points. Each one holds a position and a color, and the :term[struct]{id=struct} is exactly 16 bytes, because the renderer uploads the array as it is.

```cpp src="Strata/src/Strata/Renderer/DebugDraw.h#L22-L27"
struct DebugLineVertex
{
	glm::vec3 Position;
	uint32_t Color; // RGBA8 (red in the lowest byte), sRGB-encoded like any display color
};
static_assert(sizeof(DebugLineVertex) == 16, "DebugLineVertex is uploaded as is");
```

The toy's `Vertex` has the same four fields. The static assertion guards the upload: a change to the struct fails the build and not the picture.

Every shape ends in `AddLine`, which drops a line whose ends are not finite numbers. A :term[NaN]{id=nan} in an end point would otherwise reach the :term[graphics processing unit]{id=gpu} (GPU) as garbage.

```cpp src="Strata/src/Strata/Renderer/DebugDraw.cpp#L88-L95" symbol="DebugDraw::AddLine"
void DebugDraw::AddLine(const glm::vec3& from, const glm::vec3& to, uint32_t color, DebugDrawDepth depth)
{
	if (!IsFinite(from) || !IsFinite(to))
		return;
	std::vector<DebugLineVertex>& lines = m_Lines[static_cast<size_t>(depth)];
	lines.push_back(DebugLineVertex { from, color });
	lines.push_back(DebugLineVertex { to, color });
}
```

The shapes are `Line`, `Box`, `Circle`, `Sphere`, `Arrow`, `Cone`, `Capsule` and `Frustum`. A `Box` takes an axis-aligned box, or half extents and a matrix that may rotate and scale it. A `Sphere` is three great circles.

An `Arrow` has a four-sided head a fifth of the length long, and at most `headSize`. A `Frustum` takes a view-projection matrix and returns false for a degenerate or infinite one, because it cannot draw the :term[far plane]{id=far-plane}. The `DebugDrawDepth` argument chooses the list: `Tested` hides the line behind scene geometry, and `OnTop` keeps it visible.

Circles are drawn with up to 32 segments for gizmos, and many are drawn per frame, so the :term[cosines]{id=cosine} and sines are not computed per segment. A table of :term[unit circles]{id=unit-circle} holds every segment count from 1 to 128, and larger counts compute directly.

```cpp src="Strata/src/Strata/Renderer/DebugDraw.cpp#L44-L49" from="if (index == segments)" to="return glm::vec2(std::cos(angle), std::sin(angle));" symbol="UnitCirclePoint"
if (index == segments)
	index = 0;
if (segments <= c_MaxTableSegments)
	return GetUnitCircleTables()[static_cast<size_t>(segments) * (segments - 1) / 2 + index];
const float angle = glm::two_pi<float>() * static_cast<float>(index) / static_cast<float>(segments);
return glm::vec2(std::cos(angle), std::sin(angle));
```

The table for n segments starts at offset n × (n − 1) / 2, since the tables of 1, 2, up to n − 1 points come before it. For 32 segments that is 496. The test `Circles close exactly on points from the unit circle tables` checks that a circle's last line ends exactly where its first starts. A circle made of sines and cosines per call could miss by a :term[rounding error]{id=rounding-error}.

Colors are packed once per shape with `PackColor`, and shapes that add many lines of one color pass the packed value to avoid packing twice.

```cpp src="Strata/src/Strata/Renderer/DebugDraw.cpp#L78-L85" from="for (int component = 0; component < 4; component++)" to="<< 24);" symbol="DebugDraw::PackColor"
for (int component = 0; component < 4; component++)
{
	if (!std::isfinite(finite[component]))
		finite[component] = 0.0f;
}
const glm::vec4 clamped = glm::clamp(finite, glm::vec4(0.0f), glm::vec4(1.0f)) * 255.0f + 0.5f;
return static_cast<uint32_t>(clamped.r) | (static_cast<uint32_t>(clamped.g) << 8) | (static_cast<uint32_t>(clamped.b) << 16)
	| (static_cast<uint32_t>(clamped.a) << 24);
```

Compare with the toy: the toy clamped, and the engine also replaces NaN and infinity by 0 first. The clamp function keeps a NaN, and turning a NaN into an :term[integer]{id=integer} is :term[undefined behavior]{id=undefined-behavior} in C++. The test `Lines go into the list of their depth mode with packed colors` pins the values, among them the orange of the toy.

### Drawing the overlays in order

`RenderOverlays` runs after post-processing and draws into one image, the renderer's output. All of its pipelines blend the source alpha over the image. The pipelines of the grid and the tested lines test depth against the scene's depth and never write it. The outline and the on-top lines test nothing.

Before them stand the views that replace the image. Lighting and global illumination views draw in the frame function, and the shadow view and the motion view draw first in `RenderOverlays`. The motion view is skipped when a lighting view is shown. Then come the tints.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L4279-L4283" from="if (options.ShowShadowView" to="DrawEntityTints(commandList, scene, options.EntityTints, viewport))" symbol="SceneRenderer::RenderOverlays"
if (options.ShowShadowView && !DrawShadowView(commandList, options, viewport))
	return false;
if (options.ShowMotionVectors && m_MotionFrame && options.LightingView == SceneLightingView::None && !DrawMotionView(commandList, viewport))
	return false;
if (entityIDs && !options.EntityTints.empty() && !DrawEntityTints(commandList, scene, options.EntityTints, viewport))
```

A tint reads the entity-ID buffer: every pixel holds the id plus one of the entity drawn there. A tint paints the pixels of its entities with a color whose alpha says how solid it is. An entity listed twice keeps its first color. The editor uses this for its streaming, LOD and mip views, which tint what the renderer drew and box what it could not draw because a mesh is missing. What each view means is the topic of [Debugging the GPU](debugging.md).

::figure{id=entity-tints}

The grid is a single triangle that covers the screen. Its :term[shader]{id=shader} casts a ray through each pixel to the grid's plane. It draws the minor, major and axis lines with anti-aliasing, and it outputs the depth of the intersection for the depth test, so geometry in front of the plane hides it. Under TAA it adds the jitter's size to its own depth bias.

Now the debug lines. Both depth modes share one buffer and one upload: tested lines first, on-top lines after them, and the second draw starts where the first ended. Positions are made relative to the camera, and the subtraction is done in double.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L4322-L4329" from="// Camera-relative, as the scene's shaders draw" to="commandList->writeBuffer(m_DebugLineBuffer" symbol="SceneRenderer::RenderOverlays"
// Camera-relative, as the scene's shaders draw (the subtraction in double for lines far from the origin).
m_DebugLineScratch.assign(tested.begin(), tested.end());
m_DebugLineScratch.insert(m_DebugLineScratch.end(), onTop.begin(), onTop.end());
const glm::dvec3 cameraPosition(camera.Position);
for (DebugLineVertex& vertex : m_DebugLineScratch)
	vertex.Position = glm::vec3(glm::dvec3(vertex.Position) - cameraPosition);
if (!m_DebugLineScratch.empty())
	commandList->writeBuffer(m_DebugLineBuffer, m_DebugLineScratch.data(), m_DebugLineScratch.size() * sizeof(DebugLineVertex), 0);
```

The code does what the toy's `PrepareUpload` does. The scratch vector is a member, so no allocation happens per frame once it has grown. The renderer counts `(testedVertices + onTopVertices) / 2` lines for its statistics.

Drawing a range chooses one of three pipelines. A tested range under TAA takes the jittered pipeline, the one with the bias.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L4142-L4149" from="// Tested against a jittered depth" to="commandList->draw(" symbol="SceneRenderer::DrawDebugLines"
// Tested against a jittered depth (temporal anti-aliasing): with its bias.
state.pipeline = depth == DebugDrawDepth::Tested && m_TemporalFrame ? m_JitteredDebugLinePipeline.Get() : m_DebugLinePipelines[static_cast<size_t>(depth)].Get();
state.framebuffer = m_OverlayFramebuffer;
state.viewport.addViewportAndScissorRect(nvrhi::Viewport(static_cast<float>(m_ViewportSize.x), static_cast<float>(m_ViewportSize.y)));
state.bindings = { m_DebugLineBindingSet };
state.vertexBuffers = { nvrhi::VertexBufferBinding { m_DebugLineBuffer, 0, 0 } };
commandList->setGraphicsState(state);
commandList->draw(nvrhi::DrawArguments().setVertexCount(vertexCount).setStartVertexLocation(firstVertex));
```

After the tested lines the order of the passes follows the picture of the map: the world text, then the world part of each registered pass.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L4334-L4342" from="if (testedVertices > 0)" to="pass->DrawWorld(commandList, m_OverlayFramebuffer);" symbol="SceneRenderer::RenderOverlays"
if (testedVertices > 0)
	DrawDebugLines(commandList, DebugDrawDepth::Tested, 0, testedVertices);
if (drawText)
	m_TextRenderer->Draw(commandList, m_OverlayFramebuffer, false, m_TemporalFrame);
// The game UI placed in the scene, with the world-space text.
if (drawOverlayPasses)
{
	for (const Scope<ISceneOverlayPass>& pass : m_OverlayPasses)
		pass->DrawWorld(commandList, m_OverlayFramebuffer);
```

The selection outline comes next. The renderer keeps the selected entities sorted as ids plus one, uploads them once, and the shader finds each pixel's id with a :term[binary search]{id=binary-search}. The upload repeats only when the selection or the hierarchy changes. The outline has a width of 1 to 8 pixels.

Under TAA the entity ids are jittered, and an outline made from them would move by a pixel from frame to frame. So the renderer first draws the selected instances without jitter into a small mask, and builds the outline from that.

The end of the function is short.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L4428-L4436" from="if (onTopVertices > 0)" to="pass->Draw(commandList, m_OverlayFramebuffer);" symbol="SceneRenderer::RenderOverlays"
if (onTopVertices > 0)
	DrawDebugLines(commandList, DebugDrawDepth::OnTop, testedVertices, onTopVertices);
if (drawText)
	m_TextRenderer->Draw(commandList, m_OverlayFramebuffer, true, false); // The HUD goes over everything
// The game UI over the HUD text.
if (drawOverlayPasses)
{
	for (const Scope<ISceneOverlayPass>& pass : m_OverlayPasses)
		pass->Draw(commandList, m_OverlayFramebuffer);
```

The text renderer draws twice: once with world-space text before the outline, and once for the screen's own text after everything else. The on-top lines come after the outline, so a gizmo that must stay visible is never hidden by it. The game UI's passes draw last, over the screen text.

The whole function returns false when it had to omit something, and the frame function then marks the frame as degraded. The image is complete, and the error is already reported once.

### Gizmos of components

`DrawSceneGizmos` turns a scene into lines. It reads the active components with their cached :term[world transforms]{id=world-transform}, so the caller calls `Scene::UpdateWorldTransforms` first. Lights come first.

A directional light is an arrow along its direction, 1.5 units long. A point light is a sphere of its range. A spot light is a cone of its outer angle, whose slant edge is as long as the range. A rectangle light is the outline of its face, a short stroke along the way it shines, and its reach where ranges show; far away it is a diamond with a small rectangle in it.

Cameras follow, as their :term[frustum]{id=view-frustum}, cut at their far plane or at `MaxCameraFrustumLength`, whichever is nearer. Colliders come last.

The renderer's module knows physics only through a registry. A module that owns a component registers a gizmo function with the component, and `DrawSceneGizmos` loops over all components that have one.

```cpp src="Strata/src/Strata/Physics/PhysicsComponents.cpp#L51-L57" from="const BoxColliderComponent& collider" to="return true;" symbol="BoxColliderGizmo"
const BoxColliderComponent& collider = *static_cast<const BoxColliderComponent*>(component);
glm::vec3 scale(1.0f);
if (!GetColliderFrame(world, collider.Offset, outShape.Transform, scale))
	return false;
outShape.Type = ComponentGizmoShape::Kind::Box;
outShape.HalfExtents = collider.HalfExtents * scale;
return true;
```

The function fills a `ComponentGizmoShape`, a small description and not a drawing: a kind (`Box`, `Sphere`, `Capsule` or `MeshBounds`), a transform, and the size of that kind. It returns false when there is nothing to draw, such as a transform without a usable shape. The collider follows the entity's scale the way the rigid body does, so the box extents are multiplied per axis.

The registration is one more call in the chain that [one registration](../world/reflection.md) describes: `.Gizmo(ComponentGizmoGroup::Collider, BoxColliderGizmo)`. The group names when the shape is drawn. The pin has one group, `Collider`, so every component gizmo is drawn with the colliders and in the collider color.

`DrawShape` turns the description into lines with the shape's matching `DebugDraw` call, after it asked the view whether the shape is visible.

```cpp src="Strata/src/Strata/Renderer/SceneGizmos.cpp#L133-L137" from="case ComponentGizmoShape::Kind::Sphere:" to="debugDraw.Sphere(center, shape.Radius, settings.ColliderColor, settings.Depth);" symbol="DrawShape"
case ComponentGizmoShape::Kind::Sphere:
{
	const glm::vec3 center(shape.Transform[3]);
	if (view.IsVisible(center, shape.Radius))
		debugDraw.Sphere(center, shape.Radius, settings.ColliderColor, settings.Depth);
```

A `MeshBounds` shape draws the bounds of its mesh only when the mesh is loaded, because gizmos never request assets. A mesh that is still loading shows nothing for a frame.

### Culling and icons

A scene with thousands of lights must not cost thousands of spheres. When the caller gives a `SceneGizmoView`, two rules apply. Shapes outside the view's frustum, or further than `MaxDistance` (500 units), are omitted. A light or camera whose shape would be smaller on screen than `MinShapePixels` (128) is drawn as an icon of `IconPixels` (24): a diamond that faces the view, with a stroke for its direction. The editor adds a third rule: only the selected lights show their range, and the others are icons.

:::example[When a point light becomes an icon]
The view is 720 pixels high with a vertical :term[field of view]{id=field-of-view} of 60°. At distance d, 128 pixels cover (128 / 720) × 2 × d × tan(30°), which is 0.2053 × d world units. A selected point light of range 4 has a shape 2 × 4 = 8 units across.

At 30 units, 128 pixels are 6.16 units, and 8 is larger, so the light shows as a sphere. At 50 units they are 10.27 units, and 8 is smaller, so the light shows as an icon. The icon is 24 pixels, which is 0.0385 × 50 = 1.92 units wide at that distance. The switch happens at 8 / 0.2053 = 39 units.
:::

The rule keeps the icon the same size on screen at any distance, and it keeps the cost to what is near and in view. The test named `Gizmos for a view leave out what is out of view or too far, draw small lights and cameras as icons, and colliders of the selection` pins the rules.

### Passes from higher modules

Everything above lives in the renderer. The game UI does not, and the renderer still draws it. The interface is small.

The registry is a list of named factories. A module adds one in its registration function, which the composition root runs before any renderer exists.

```cpp src="Strata/src/Strata/Renderer/SceneOverlay.cpp#L22-L29" from="if (name.empty()" to="entries.push_back(" symbol="SceneOverlayRegistry::Register"
if (name.empty() || !factory)
	return false;
std::vector<Entry>& entries = GetEntries();
auto existing = std::find_if(entries.begin(), entries.end(), [&](const Entry& entry) { return entry.Name == name; });
if (existing != entries.end())
	existing->Factory = std::move(factory);
else
	entries.push_back(Entry { std::move(name), std::move(factory) });
```

Registering under an existing name replaces the factory, which keeps a second call of a registration function harmless. An empty name or factory returns false and changes nothing. The game UI registers as follows.

```cpp src="Strata/src/Strata/GameUI/GameUIRenderer.cpp#L74-L78" from="const bool registered" to="ST_CORE_VERIFY(registered" symbol="RegisterGameUIRenderer"
const bool registered = SceneOverlayRegistry::Register("GameUI", [](const SceneOverlayPassContext& context) -> Scope<ISceneOverlayPass>
{
	return CreateScope<GameUIRenderer>(context);
});
ST_CORE_VERIFY(registered, "The game UI could not register its overlay pass");
```

When a `SceneRenderer` is constructed, it asks every factory for a pass, in registration order, and keeps the passes. That is the whole inversion: the renderer holds `ISceneOverlayPass` objects, and the module's class stays invisible to it.

An **overlay pass** is a pass that a module adds to every scene renderer through the registry, drawn over the finished image after the screen-space text.

A pass has four functions. `Prepare` gets a `SceneOverlayFrame` and lays out and uploads what the frame draws. It returns false when it has nothing to draw, so a scene without such overlays costs one check.

`DrawWorld` draws what is placed in the scene, depth-tested, right after the world text. `Draw` draws over the screen, over everything before. `HasScreenContent` lets the game's renderer show a scene without a camera, such as a main menu, instead of a missing-camera message.

The `SceneOverlayFrame` carries what a pass needs from the renderer. It holds the scene whose overlays are drawn, the viewport size, the screen view and the flag for screen-space drawing. It holds the camera for overlays placed in the scene, an open :term[command list]{id=command-list} for uploads, the glyph atlases, a list to append the textures the pass used, a statistics record and the GPU timer. The camera comes as a view-projection and a position, and the pass subtracts the camera from what it places, in double, before multiplying. The pass times its draws as a stage of its own, which the game UI names after itself, inside the stage of all overlays.

### The screen view

A **screen view** is the zoom and offset that say where the game's screen lies in the renderer's image.

The game's own interface is laid out for a screen of a fixed size in pixels. In the Game view the image is that screen. In the editor's 2D canvas mode the person zooms and pans, and the layout must not change while the image is magnified. So the renderer takes a `SceneScreenView` in its options: the screen's size, a zoom in image pixels per screen pixel, and an offset of the screen's top-left corner in image pixels. A point at screen position p lands at Offset + Zoom × p.

For a screen of 1280 by 720 with zoom 2 and offset (−300, −100), the center (640, 360) lands at (−300 + 1280, −100 + 720) = (980, 620). A text anchored at (20, 20) lands at (−260, −60), outside the image, and so the person has panned it away. The struct repairs bad values: a zero or non-finite screen size means the image's size, a zero zoom means 1, and a bad offset means 0. How canvas mode drives the struct is in [the Scene view](../editor-ui/scene-view.md).

### The jitter and the depth bias

With TAA the renderer shifts the camera's projection by a fraction of a pixel each frame and blends the frames. The scene's depth is drawn with that shift, up to half a pixel each way. The overlays draw with the camera's own matrices, so lines stay steady. A line that lies on a floor then differs from the floor's jittered depth by a bit. Without help it flickers, because some of its pixels fail the depth test and the set of those pixels changes every frame.

```cpp src="Strata/src/Strata/Renderer/SceneOverlay.h#L82-L90" symbol="SetJitteredDepthBias"
// With temporal anti-aliasing the scene depth that overlays test against is jittered, up to half a pixel each way from
// where the overlays, drawn with the camera's own matrices, put their surfaces. Overlays placed in the scene then give their
// depth test this bias toward the camera (reversed-Z): one pixel's worth of the depth's slope, which covers the jitter, so
// those lying on a surface (the grid on a floor, text or a canvas on a wall) do not flicker against it.
inline void SetJitteredDepthBias(nvrhi::RasterState& rasterState)
{
	// NVRHI enables a depth bias only with a constant part: one step of the depth format, negligible next to the slope's.
	rasterState.setDepthBias(1).setSlopeScaleDepthBias(1.0f);
}
```

A depth bias moves the line's depth toward the camera by a constant and by a part of the depth's slope. :term[NVRHI]{id=nvrhi} enables a bias only with a constant part. So the constant is the smallest step of the depth format, and the slope part, one pixel's worth, does the work.

The function sets this on the `rasterState` of a pipeline. The renderer uses it for tested debug lines under TAA, for the selection mask and for the world text. A pass that puts its own surfaces in the scene, such as a world-space canvas, reads the frame's `JitteredDepth` flag and does the same. The grid does not use the pipeline bias: its shader writes depth and adds the jitter's size itself.

The test `With TAA the grid on a floor and text on a wall cover the same pixels in every jitter phase` renders every jitter phase and compares the pixels.

### What Strata does not do

Games cannot draw debug lines from scripts. A search of `StrataScriptCore` for debug-draw and draw-line functions finds nothing at the pin. The reason is the shape of the data: a `DebugDraw` is a C++ object that code owns for a frame and passes to a renderer, and scripts reach the engine only through plain C data. Only C++ code of the engine or the editor can fill a list, as Exercise 1 does.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Retained gizmo entities in the scene | Editors that draw handles as scene objects | One drawing path, with picking for free | Hierarchy and file clutter, lit and tone-mapped colors |
| Lines drawn with the UI library | Tools that draw over a window | No renderer support at all | No depth test, so no hiding behind walls |
| Thick lines as camera-facing quads | Engines with debug draw of several pixels width | Clear lines on high-resolution screens | A vertex shader that builds quads, and more points |
| One :term[callback]{id=callback} list in the renderer | Small engines with one UI | Simpler than a registry of factories | The renderer would name each caller, or hold their state |
| Debug drawing that scripts can call | Engines with a scripting layer that exposes debug lines | Game makers could draw paths and ranges | A new host function and a ruling for every shape |

The sources for the engines named are in Further reading.

## How it is tested

Two suites cover the page. The suite `Renderer.DebugDraw` needs no GPU, and it checks the recorder and the gizmos:

- lines in the list of their mode, with packed colors;
- outlines of boxes, spheres, circles, cones, arrows, capsules and frustums;
- the gizmos of lights, cameras and colliders, and the upright capsule of a character controller;
- circles that close on table points, and the view's icons and omitted shapes;
- mesh colliders that show only while their mesh is loaded.

The suite `GPU.SceneRenderer.Overlays` renders and reads pixels. Its cases check these facts:

- the grid hides behind geometry and stays visible on a floor, in every TAA phase, like text on a wall;
- the outline follows silhouettes, also under TAA, on both draw paths;
- a renderer without entity ids draws the same image and omits outlines and tints;
- tints change exactly the pixels of the listed entities;
- tested lines hide behind geometry, on-top lines do not, and lines behind the camera are clipped;
- gizmos and overlays render into images that the caller owns.

Every GPU suite ends by checking that the device logged no new error.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.DebugDraw
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.Overlays
```

Both lines run a suite directly with a doctest filter. The second needs a machine with a :term[Vulkan]{id=vulkan} driver. Through CTest, the GPU suites run together as the test `StrataTests.GPU`.

## Changing it safely

To add a shape, add a function to `DebugDraw`, built from `AddLine` and `AddCircle`, and a case to `Renderer.DebugDraw` that checks its lines. To give a component a gizmo, write the function in the module that owns the component and register it with `.Gizmo(...)`; Exercise 3 does it for the `WindZone`. To add a pass, implement `ISceneOverlayPass` in the module and register a factory in its registration function.

These rules of `AGENTS.md` apply, each with its reason.

- Every pass is wrapped in a GPU stage registered with its module, so the timing view shows it.
- Never block a frame on an asset: gizmos and passes skip what is loading.
- Scene shaders work in camera-relative space: a pass that places things in the scene subtracts the camera in double.
- A test of a registry-added behavior stays in the module's own suite, because the renderer's tests must not link the module.
- Layering: never add an include from the renderer to a module above it. Invert the dependency with an interface or a registry.

Before you commit, run `Renderer.DebugDraw`, the overlay GPU suite and `Architecture.Layering`, and check that the device logged no new error.

## Summary

- The renderer draws overlays after post-processing, in a fixed order: views, tints, grid, tested lines, world text and passes, outline, on-top lines, screen text and passes. Tints and the outline need the entity-ID buffer.
- A `DebugDraw` records lines for one frame in two depth modes, packs colors as :term[sRGB]{id=srgb} bytes, and the renderer uploads them camera-relative, with the subtraction done in double.
- A component's gizmo is a function registered with `.Gizmo(...)` that fills a `ComponentGizmoShape`; `DrawSceneGizmos` and `DrawShape` turn it into lines, cut to the view and drawn as icons when small.
- A module adds a pass with `SceneOverlayRegistry::Register`; each renderer makes one pass per factory, and the renderer never names the module.
- Under TAA the overlays use the camera's own matrices and tested overlays get a depth bias of one pixel's slope, through `SetJitteredDepthBias`.

## Check yourself

1. A renderer has no entity-ID buffer, and the editor selects an entity and shows the grid. What happens?
   - A. The frame is not drawn at all.
   - B. The grid draws, the outline and tints are omitted, and an error is reported.
   - C. The outline is drawn from the :term[depth buffer]{id=depth-buffer} instead.

   :::answer{tests="overlay-order"}
   B. The outline and the tints read the entity-ID buffer, so without it they are omitted and the renderer reports the reason. The grid and the lines need nothing from it (A is wrong), and no fallback outline exists (C is wrong). The frame is marked degraded, but the image is complete.
   :::

2. In which order do these draw: on-top lines, the selection outline, the grid, world text?

   :::answer{tests="overlay-order"}
   Grid, world text, selection outline, on-top lines. The grid and tested lines come first, then world text and the world part of passes, then the outline, and the on-top lines after the outline so nothing hides them.
   :::

3. A module registers an overlay pass after a renderer is constructed. Does that renderer draw it?
   - A. Yes, on the next frame.
   - B. No, because each renderer makes its passes when it is constructed.
   - C. Only if the registry replaces a factory of the same name.

   :::answer{tests="overlay-registry"}
   B. The factories are asked once, when the renderer is made. A pass registered later appears in renderers made afterwards. The composition root registers every module before any renderer exists for this reason. A replaced factory (C) also changes only renderers made later.
   :::

4. A line lies on a floor and flickers under TAA. Name the cause and the cure.

   :::answer{tests="jitter-bias"}
   The scene's depth is jittered by up to half a pixel, and the line is drawn with the camera's own matrices, so some of its pixels fail the depth test. The cure is a depth bias toward the camera of one pixel's slope, set with `SetJitteredDepthBias` on the pipeline.
   :::

5. A camera is at x = 5,000,000. Why does the renderer subtract it from a line's end points before the upload?

   :::answer{tests="record-lines"}
   Floats near five million are 0.5 apart. After the subtraction the positions are small, and floats near them are fine to 0.0000002. The subtraction runs in double, so its own error is far smaller than a float's step.
   :::

6. You register a gizmo function for your own component, and for one entity it returns false. What does the Scene view show for that component, and what happens to the other entities?

   :::answer{tests="gizmo-path"}
   Nothing is drawn for that component on that entity, and no error is reported: false means "nothing to draw". The loop continues with the other entities and components, and each of them asks its own function.
   :::

## Exercises

1. **Basic.** The editor's `ViewportRenderer` owns a `DebugDraw`. Draw a path of four points over the Scene view, green and hidden behind walls, and again yellow and always visible. Add an arrow at its end.

   :::answer[Worked solution]{tests="record-lines"}
   Add this code in `StrataEditor/src/Editor/ViewportRenderer.cpp` after the block that draws the scene gizmos, and before the code that gives the list to the options. The list is cleared at the start of the frame, so you add the calls every frame.

   ```cpp pseudocode
   points = [ (0, 1, 0), (4, 1, 0), (4, 1, 4), (0, 1, 4) ]
   for index in 0 .. 2:
       m_DebugDraw.Line(points[index], points[index + 1], green, Tested)
       m_DebugDraw.Line(points[index], points[index + 1], yellow, OnTop)
   m_DebugDraw.Arrow(points[2], points[3], yellow, OnTop)
   ```

   The tested lines vanish where a wall stands between the camera and the path, and the yellow lines stay. Both lists upload together and draw in two ranges. A script cannot do this: it has no debug-draw function.
   :::

2. **Medium.** Trace it yourself: find where a Box Collider's gizmo becomes lines. Use a source build, a scene with a Box Collider in view, and a breakpoint.

   :::answer[Worked solution]{tests="gizmo-path"}
   Put a breakpoint in `DrawSceneGizmos` in `Strata/src/Strata/Renderer/SceneGizmos.cpp` and show colliders in the Scene view. Step to the collider part: `DrawAllColliders` loops over the entities with the component (or `DrawEntityColliders` over the selection, when only its colliders show) and calls `DrawComponentGizmo`, which calls the :term[function pointer]{id=function-pointer} in the component's info. That function is `BoxColliderGizmo` in `Strata/src/Strata/Physics/PhysicsComponents.cpp`, registered with `.Gizmo(ComponentGizmoGroup::Collider, ...)`. It fills a `ComponentGizmoShape` of kind Box. `DrawShape` then calls `DebugDraw::Box`, which calls `AddLine` twelve times.
   :::

3. **Hard.** Start from the end state of [Adding a component](../world/tutorial-component.md). Give the `WindZone` a gizmo: a sphere of its radius around the entity's origin. Add a test.

   :::answer[Worked solution]{tests="gizmo-path" solution="tutorials/gpu/debug-drawing/exercise-3.patch"}
   The gizmo is a function in `PhysicsComponents.cpp` that fills a sphere, plus one more call in the registration of the `WindZone`.

   ```cpp pseudocode
   bool WindZoneGizmo(registry, entity, component, world, outShape):
       if radius is not finite or radius <= 0: return false
       outShape.Type = Sphere
       outShape.Transform = translation of world's origin
       outShape.Radius = zone.Radius
       return true
   // in the registration: .Gizmo(ComponentGizmoGroup::Collider, WindZoneGizmo)
   ```

   The function ignores the entity's scale, like the zone does. The test, in `WindZoneTests.cpp`, draws the gizmos of a scene with one zone of radius 3 and checks 96 lines, three circles of 32, all 3 units from the center. The patch is the chain's next step: the scripting tutorials start from it.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/DebugDraw.h` and `DebugDraw.cpp`: the recorder, its shapes and `PackColor`.
- `Strata/src/Strata/Renderer/SceneGizmos.h` and `SceneGizmos.cpp`: `DrawSceneGizmos`, `SceneGizmoSettings` and `SceneGizmoView`.
- `Strata/src/Strata/Reflection/ComponentGizmo.h`: `ComponentGizmoShape` and the gizmo group.
- `Strata/src/Strata/Renderer/SceneOverlay.h` and `SceneOverlay.cpp`: `SceneScreenView`, `SceneOverlayFrame`, `ISceneOverlayPass`, `SceneOverlayRegistry` and `SetJitteredDepthBias`.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `RenderOverlays` and `DrawDebugLines`; `Strata/shaders/Overlay/` holds their shaders.
- `Strata/src/Strata/GameUI/GameUIRenderer.cpp`: the game UI's pass and its registration.
- Tests: `StrataTests/src/Renderer/DebugDrawTests.cpp` and `GPUSceneOverlayTests.cpp`.

## Further reading

- Unity manual, "Gizmos", and its scripting reference for drawing a debug line: immediate-mode debug drawing in another engine (beginner).
- Unreal Engine documentation, "DrawDebugHelpers": debug shapes drawn for a duration (intermediate).
- Robert Nystrom, "Game Programming Patterns", the chapters on the observer and service locator patterns: the ideas behind a registry (beginner).
