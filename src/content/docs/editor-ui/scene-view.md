---
id: editor-ui/scene-view
title: "The Scene view"
description: "How the Scene view draws a 3D image inside a panel, finds the entity under a click without stalling, and turns a gizmo drag into one undo step."
kind: internals
size: XL
tracks: [E]
needs: [editor-ui/shell, editor/camera-viewport, editor/placement, gpu/frame-tour, gpu/readback-timing]
time: 100
learn:
  - id: image-and-gizmo
    text: explain how the Scene view renders at the panel's pixel size and why the image becomes a Dummy while the pointer is over the gizmo
  - id: pick-timeline
    text: trace a click on the image to the selection, and name what drops a late result
  - id: gizmo-undo
    text: explain how a gizmo drag becomes one undo step computed from its start state
  - id: around-the-image
    text: name what the chips, the agent chip and flash, the load card and canvas mode add around the image
since: 0.3.0
status: final
---

A person who builds a scene must see it in 3D, click on a thing to select it, and drag a handle to move it. The Scene view is the panel that does all three, and it must do them inside a window system that knows only rectangles, buttons and text. This page follows one click and one drag through the code. It does not cover the camera's mathematics ([the editor camera](../editor/camera-viewport.md)), how a dropped asset finds its place ([placing content](../editor/placement.md)), the list of debug views ([debugging](../gpu/debugging.md)) or the Scene view's shortcuts ([the Game view](game-view.md)).

## The problem and how engines solve it

The **Scene view**, also called the viewport, is the editor panel that shows the open scene in 3D and lets you select and move what you see. The window system of the editor, :term[Dear ImGui]{id=dear-imgui}, draws flat items: text, buttons and images. The scene comes from the :term[renderer]{id=renderer} of [the tour of a frame](../gpu/frame-tour.md), which draws into a texture and not into a window. The first problem is to put one inside the other.

Every editor with a 3D view meets the same three problems, and the answers are almost the same across engines. The first is the image. The renderer draws into a **render target**, an image in graphics memory that is not the window, and the panel then shows that image as an item. Drawing into a target and showing it later is also called render to texture.

The size of the target must match the panel, in the pixels of the screen and not in points. A panel that is 960 points wide on a display that doubles its pixels needs a target 1,920 pixels wide, or the picture is blurred.

Take an image area of 640 by 360 points on a display with two pixels per point. The target must be 1,280 by 720 pixels, which is 921,600 pixels. Drawing 640 by 360 and stretching it fills four screen pixels from one rendered pixel, and every edge looks soft. Drawing more than the screen has wastes time. Only the exact size is both sharp and cheap, and it changes whenever the person drags the panel's border.

The second problem is **picking**: finding which entity lies under the pointer. An engine has two good answers. The first casts a ray from the camera through the pointer and tests it against the entities' boxes or triangles on the :term[central processing unit]{id=processor} (CPU). The second gives every entity an identifier (:term[ID]{id=id}), a number, draws the scene once more with the number as the color, and reads the color of the pixel under the pointer. That image is the **entity-ID buffer**, a texture in which each pixel holds the number of the entity drawn there.

Each answer has a price. A ray against boxes is cheap but wrong at the edges. The box of a tree is a block, and a click in the gap between two branches selects the tree although the pixel shows the wall behind it. A ray against triangles is exact, but it needs the triangles of every entity in their current pose, and a skinned character's triangles move on the :term[graphics processing unit]{id=gpu} (GPU). The ID buffer is exact by construction, because it is the picture itself, but its answer lives in graphics memory.

| Approach | Where it runs | Right at the edges | Cost of a click |
| --- | --- | --- | --- |
| Ray against boxes | The CPU | No: a box is larger than its object | One test per entity, no :term[readback]{id=readback} |
| Ray against triangles | The CPU | Yes, for the pose the CPU knows | The posed triangles of every entity |
| Entity-ID buffer | The GPU, read back | Yes: it is the picture | One pixel of 4 :term[bytes]{id=byte}, copied back later |

Reading it costs time you have already met. [Reading from the GPU without stalls](../gpu/readback-timing.md) explains that a copy waits behind the frames already handed to the graphics card. A blocking read can therefore freeze the window for about 30 ms, two frames at 60 :term[frames per second]{id=frame-rate}.

The editor asks for one pixel instead, polls each frame, and applies the answer two or three frames later. That is 33 to 50 ms at 60 frames per second, which a person does not notice as delay. It creates a new problem: the world can change before the answer returns.

:::example
A 1,280 by 720 image holds 921,600 pixels. With 4 bytes for each identifier, the whole ID buffer is 3,686,400 bytes, about 3.5 MB. A click needs one pixel: 4 bytes, about 0.0001 % of the buffer.

A click at frame 100 gets its answer at frame 102 or 103. A frame lasts 16.7 ms at 60 frames per second, so the person waits 33 to 50 ms. A blocking read would freeze the window for about 30 ms on every click, and the polled read never freezes it.
:::

The third problem is moving things. A **gizmo** is a set of handles drawn over the selected object that turns pointer motion on the screen into a translation, a rotation or a scale. The handles are not in the scene. They live in :term[screen space]{id=screen-space}, drawn after the image, and the code behind them must turn flat motion into a change of a 3D matrix. Most editors use a library for this, and Strata does too.

Three decisions follow from these answers, and the rest of the page shows how Strata makes them. The image is an item inside a window system that has opinions about who owns the mouse, and the gizmo wants the mouse at the same place. The answer of a pick comes late, so it must not be trusted blindly. The code below decides who owns the pointer, which frame an answer belongs to, and what one drag means to the undo history.

## The map

All of the Scene view runs on the :term[main thread]{id=main-thread}, one frame at a time. The panel is `ViewportPanel`, in `StrataEditor/src/Panels/ViewportPanel.cpp`. It sits on top of `EditorViewport` (the state: camera, settings, the pending pick), `ViewportRenderer` (the view's own renderer) and `TransformDrag` (a gizmo drag). The gizmo library is **ImGuizmo**, a small open-source library for Dear ImGui that draws and handles the translate, rotate and scale handles. The editor's user interface (UI) library, `StrataEditorUI`, links it privately: only the panel draws gizmos, and no game or core library can include it.

The panel stacks four layers. At the top is a strip of chips, the toolbar, and the image never lies under it. The image comes from the view's renderer, drawn with the camera that the view shows. Over the image come the :term[overlays]{id=overlay-core} that the panel draws itself: the gizmo, the selection flash, the legend, the statistics, the ghost's label and a loading card.

```mermaid caption="Four layers of the Scene view, from the strip at the top to the cards over the image, and what feeds each. Clicks and drags go down, from the image item to the pick request and the gizmo drag." alt="A diagram of the Scene view. A toolbar strip with chips and the agent chip stands above an image drawn by the view's renderer. Overlays, among them the gizmo, the flash, the legend and the load card, are drawn over the image. The image item feeds a pick request and a camera drag, and the gizmo feeds a transform drag."
flowchart TD
    Strip["Toolbar strip: chips, agent chip"]
    Image["Image item: the view's renderer output, at the panel's pixel size"]
    Over["Overlays: gizmo, flash, legend, stats, ghost label, load card"]
    Pick["EditorViewport::RequestPick then UpdatePicking"]
    Cam["EditorCamera::Update"]
    Drag["TransformDrag: Begin, Update, End"]
    Strip -->|"never covers"| Image
    Image --> Over
    Image -->|"click"| Pick
    Image -->|"drag with Alt, middle or right button"| Cam
    Over -->|"ImGuizmo::Manipulate"| Drag
```

The strip is the reason chips never cover the game's own heads-up display (HUD). A HUD, the text and bars a game draws on its screen, belongs to the image. If the chips floated over it, the person would see the editor's controls where the game's controls will be. The strip takes as many rows as its chips need and the image gets the rest.

::figure{id=scene-view-layers}

## The contract

The panel makes promises to the code around it and keeps three rules in return. Each rule has a reason, and each reason is a bug that the rule prevents.

**The image is an item only while no gizmo is under the pointer.** ImGuizmo starts a drag only while Dear ImGui reports no hovered or active item. The image is the largest item of the panel, so left alone it would take every click, and the gizmo would never move. Over the gizmo the panel therefore replaces the image button by a `Dummy`, a block of space that is not an item and takes no click. The same condition forbids the window to move with the mouse.

**One drag leaves one undo step, and every value comes from the start.** The drag records the transforms of the dragged entities when it begins, and every frame computes the new values from that record and the gizmo's total offset. It never adds a frame's small change to the previous result. Adding would drift by rounding, and every frame of the drag would be a step in the undo history. A drag of two seconds at 60 frames per second would need 120 undo presses to reverse.

**Picking never stalls, and a late answer never selects in another scene.** The click only asks. The answer is applied in a later frame, and only if the scene that was drawn when the person clicked is still the open scene. A scene can be replaced during that wait: a person opens another one, or the game starts.

:::rule
**Every change to the scene goes through a command, or through `SceneEditTransaction` for edits that continue over frames.** The gizmo drag uses a transaction with one :term[merge key]{id=merge-editor} per drag. The reason is the undo history and the activity journal, which see only what passes through them. See [undo and redo](../editor/undo.md).
:::

Two more words matter before the code. **Snapping** rounds a drag to steps, so that a crate moves by 0.5 m at a time and lines up with its neighbors. The editor's main toolbar, not the :term[chip strip]{id=chip-strip}, has a snap toggle and steps for each operation: 0.5 for translate, 15 degrees for rotate and 0.1 for scale at the pin. Holding **Ctrl** inverts the toggle for as long as it is held.

The gizmo's axes can follow the world or the entity. In **World** mode the handles point along the world's axes, which stay the same for every entity. In Local mode they point along the entity's own axes, so a tilted ramp gets a handle that runs up its slope. Scaling always uses the entity's axes.

ImGuizmo has colors of its own, and the panel replaces them before each gizmo call from the editor's theme. The axis handles take the theme's X, Y and Z axis colors, the plane handles take the same colors with the library's own transparency, and the highlighted handle takes the theme's hover accent. A theme change therefore changes the gizmo, and no gizmo color is written into the code.

## A toy version

The toy has a one-row image of 20 pixels, two crates drawn into its ID buffer and a pick that answers two frames after the click, as a graphics card would. It has no renderer and no window. What it keeps is the shape of the real thing: a pending pick with a scene version and a timeout, and a drag that always computes from its start.

Read `RequestPick` and `Update` first, then the three drag functions. Notice that nothing in the drag adds a small change to a position that an earlier frame changed.

```cpp sketch="editor-ui-scene-view-toy.cpp"
// A toy Scene view: a pick that finishes frames later, and a gizmo drag that leaves one undo step.
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <optional>
#include <vector>

class ToyView
{
public:
	ToyView()
	{
		// The ID buffer of a one-row image, 20 pixels wide: entity index + 1 where a crate is drawn, 0 where nothing is.
		m_IdBuffer.assign(20, 0);
		for (size_t crate = 0; crate < m_Positions.size(); crate++)
			for (int pixel = static_cast<int>(m_Positions[crate]); pixel < static_cast<int>(m_Positions[crate]) + 4; pixel++)
				m_IdBuffer[static_cast<size_t>(pixel)] = static_cast<uint32_t>(crate + 1);
	}

	void RequestPick(int pixel)
	{
		// One pending pick: a newer click replaces it. The answer is ready two frames later, as a GPU readback would be.
		m_Pick = Pick { pixel, m_Frame + 2, m_Frame + 300, m_SceneVersion };
	}

	void ReplaceScene() { m_SceneVersion++; }

	void Update()
	{
		m_Frame++;
		if (!m_Pick || m_Frame < m_Pick->ReadyFrame)
		{
			if (m_Pick && m_Frame > m_Pick->TimeoutFrame)
				m_Pick.reset(); // The readback never finished: give up.
			return;
		}
		const Pick pick = *m_Pick;
		m_Pick.reset();
		if (pick.SceneVersion != m_SceneVersion)
		{
			std::printf("frame %d: the pick belongs to another scene, dropped\n", m_Frame);
			return;
		}
		const uint32_t id = m_IdBuffer[static_cast<size_t>(pick.Pixel)];
		m_Selected = id == 0 ? std::optional<size_t>() : std::optional<size_t>(id - 1);
		std::printf("frame %d: pixel %d selects %s\n", m_Frame, pick.Pixel, id == 0 ? "nothing" : "a crate");
	}

	void BeginDrag() { m_DragStart = m_Positions[*m_Selected]; }

	void UpdateDrag(float offset, float step)
	{
		// Always from the start state, so the result never drifts.
		const float snapped = step > 0.0f ? std::round(offset / step) * step : offset;
		m_Positions[*m_Selected] = *m_DragStart + snapped;
	}

	void EndDrag()
	{
		if (m_Positions[*m_Selected] != *m_DragStart)
			m_Undo.push_back({ *m_DragStart, m_Positions[*m_Selected] });
		m_DragStart.reset();
	}

	void Report() const
	{
		std::printf("position %.2f, undo steps %zu\n", m_Positions[*m_Selected], m_Undo.size());
	}

private:
	struct Pick
	{
		int Pixel = 0;
		int ReadyFrame = 0;
		int TimeoutFrame = 0;
		int SceneVersion = 0;
	};
	struct UndoStep
	{
		float Before = 0.0f;
		float After = 0.0f;
	};

	std::vector<uint32_t> m_IdBuffer;
	std::vector<float> m_Positions = { 2.0f, 10.0f };
	std::optional<Pick> m_Pick;
	std::optional<size_t> m_Selected;
	std::optional<float> m_DragStart;
	std::vector<UndoStep> m_Undo;
	int m_SceneVersion = 1;
	int m_Frame = 0;
};

int main()
{
	ToyView view;
	view.RequestPick(11);
	for (int frame = 0; frame < 3; frame++)
		view.Update();

	view.BeginDrag();
	for (const float offset : { 0.3f, 0.8f, 1.3f })
		view.UpdateDrag(offset, 0.5f);
	view.EndDrag();
	view.Report();

	view.RequestPick(3);
	view.ReplaceScene();
	for (int frame = 0; frame < 3; frame++)
		view.Update();
	return 0;
}
```

```text output-of="editor-ui-scene-view-toy.cpp"
frame 2: pixel 11 selects a crate
position 11.50, undo steps 1
frame 5: the pick belongs to another scene, dropped
```

1. **Line 23:** a pending pick keeps the frame at which its answer is ready, a frame at which it stops, and the version of the scene that was drawn.
2. **Line 39:** the scene check: an answer for another version of the scene selects nothing.
3. **Line 54:** every drag frame computes from the start position and the total offset, snapped as a whole, so the result never drifts.
4. **Line 60:** a drag that ends where it started records no :term[undo step]{id=undo-step}.

The program clicks pixel 11, which lies inside the second crate, and the pick completes two frames later. It then drags that crate with offsets of 0.3, 0.8 and 1.3, snapped to steps of 0.5, and the position ends at 11.5 although the crate started at 10. Last, it clicks pixel 3 and replaces the scene before the answer arrives, so the answer is dropped.

The toy omits everything that makes the real code long. That is the pixel scale of the display, the camera, the other mouse buttons, undo that merges frames into one step, parents, and the :term[UI elements]{id=ui-element} that a click can hit before the scene. Each of those is a section below.

## The real code

The real panel runs once per frame from `ViewportPanel::OnImGuiRender`. In this order it computes the image's rectangle, handles clicks and the camera, asks the renderer for the image, draws it, and then draws everything over it. The sections follow that order.

### The image, and how it shares the mouse

The first function runs before the panel's window opens and sets the window's flags. Look at how `ImGuizmo::IsOver` of the last frame decides whether the window may move.

```cpp src="StrataEditor/src/Panels/ViewportPanel.cpp#L150-L163" symbol="ViewportPanel::GetWindowOptions"
EditorPanelWindowOptions ViewportPanel::GetWindowOptions(EditorPanelContext&)
{
	ImGuizmo::BeginFrame();

	// ImGuizmo starts a drag only while no ImGui item is hovered or active, so over the gizmo (as of the last frame)
	// the image is not an item; the window then must not move with the mouse either (when it floats).
	m_OverGizmo = ImGuizmo::IsOver();
	EditorPanelWindowOptions options;
	options.NoPadding = true;
	options.Flags = ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse;
	if (m_OverGizmo)
		options.Flags |= ImGuiWindowFlags_NoMove;
	return options;
}
```

1. **Line 152:** ImGuizmo needs one call to `BeginFrame` before any gizmo call of the frame.
2. **Line 156:** the answer is the one of the previous frame, because the gizmo is drawn later in this one. The panel keeps it in `m_OverGizmo`.
3. **Line 161:** a floating window that is dragged by its body would move when the person drags a handle, so the flag `NoMove` is set while the pointer is over the gizmo.

Then the panel makes the image an item. The rectangle comes from the toolbar's layout and has a size in pixels (`ViewportImageArea::ChoosePixelScale` picks the scale that turns points into pixels). The next quote shows the item.

```cpp src="StrataEditor/src/Panels/ViewportPanel.cpp#L206-L217" from="if (m_OverGizmo)" to="AcceptAssetDrops();" symbol="ViewportPanel::OnImGuiRender"
if (m_OverGizmo)
{
	ImGui::Dummy(available);
}
else
{
	ImGui::SetNextItemAllowOverlap();
	ImGui::InvisibleButton("SceneImage", available, ImGuiButtonFlags_MouseButtonLeft | ImGuiButtonFlags_MouseButtonRight | ImGuiButtonFlags_MouseButtonMiddle);
}
m_Hovered = ImGui::IsItemHovered(ImGuiHoveredFlags_AllowWhenBlockedByActiveItem);
UI::ItemProbe::RecordRect("Viewport.Image", imageMin, ImVec2(imageMin.x + available.x, imageMin.y + available.y));
AcceptAssetDrops();
```

1. **Line 208:** over the gizmo the image is a `Dummy`: space that takes no click.
2. **Line 213:** elsewhere the image is a button for all three mouse buttons.
3. **Line 215:** the hover answer feeds the camera, the picks and the shortcuts of the frame.

:::caution
The answer of ImGuizmo is one frame old. A press in the very frame in which the pointer reaches a handle can still hit the image button. The tests of the gizmo therefore hover over it for a few frames before they press.
:::

The invisible button takes the left, right and middle buttons, and `SetNextItemAllowOverlap` lets items placed later, such as the chips, sit over it. Over the gizmo `Dummy` stands in. The hover test uses `AllowWhenBlockedByActiveItem`, so the image still counts as hovered while another item, such as a dragged asset, holds the mouse. A little earlier the panel passes the image's size to `EditorViewport::SetSize`. When the size is zero in either direction, it resets every held interaction and returns, so a collapsed panel renders nothing.

### Camera drags, from the panel

The camera's mathematics (orbit, pan and fly speed) are on [the editor camera's page](../editor/camera-viewport.md). The panel has the other half of the job: it decides which mouse motion belongs to the camera and feeds it in. A drag starts on the image, never on the gizmo, and continues wherever the pointer goes until its button comes up. The right button flies, the middle button pans, and **Alt** with the left button orbits.

```cpp src="StrataEditor/src/Panels/ViewportPanel.cpp#L935-L950" from="// Fly mode hides the cursor" to="input.MouseDelta = glm::vec2(0.0f);" symbol="ViewportPanel::UpdateCamera"
// Fly mode hides the cursor and frees it from the screen edges; it comes back where it was.
if (m_CameraDrag == CameraDrag::Fly && !m_CursorLocked)
{
	Input::SetCursorMode(CursorMode::Locked);
	m_CursorLocked = true;
}

EditorCameraInput input;
// The first frame of a drag has no meaningful delta (the mouse may just have entered the window).
if (m_CameraDrag != CameraDrag::None && !ImGui::IsMouseClicked(ImGuiMouseButton_Left) && !ImGui::IsMouseClicked(ImGuiMouseButton_Right)
	&& !ImGui::IsMouseClicked(ImGuiMouseButton_Middle))
{
	input.MouseDelta = glm::vec2(io.MouseDelta.x, io.MouseDelta.y);
}
if (!std::isfinite(input.MouseDelta.x) || !std::isfinite(input.MouseDelta.y))
	input.MouseDelta = glm::vec2(0.0f);
```

1. **Lines 937–940:** flying locks the cursor, so the pointer cannot hit the edge of the screen.
2. **Lines 943–946:** the delta counts only after the first frame of a drag.
3. **Lines 949–950:** a delta that is not finite becomes zero before the camera sees it.

Two guards protect the camera. The first frame of a drag carries no delta, because the pointer may have entered the window only now and its last position is old. A delta that is not a finite number, which a faulty device can produce, becomes zero, so the camera never receives a value that would spread through every matrix. Flying also locks the cursor with `Input::SetCursorMode`. `EndCameraDrag` frees it where it was.

### Asynchronous picking

A plain click on the image is the third kind of mouse use. The panel treats it as a pick only when the image is hovered and the click is left. **Alt** must not be held, because that is an orbit, and the gizmo must be neither under nor used by the pointer. **Ctrl** makes the pick a toggle, **Shift** makes it an addition, and otherwise it replaces the selection.

Game UI comes first. The game's screen-space canvases are drawn in front of the scene, so a click on one of their elements selects it at once, without the GPU. The element test uses the center of the clicked pixel, at the pixel plus 0.5. Only when no element is there does the panel ask for a pick of the scene.

```cpp src="StrataEditor/src/Panels/ViewportPanel.cpp#L251-L265" from="if (m_Hovered && ImGui::IsMouseClicked(ImGuiMouseButton_Left)" to="viewport.RequestPick(*pixel, size, mode);" symbol="ViewportPanel::OnImGuiRender"
if (m_Hovered && ImGui::IsMouseClicked(ImGuiMouseButton_Left) && !io.KeyAlt && !ImGuizmo::IsOver() && !ImGuizmo::IsUsing())
{
	const ViewportPickMode mode = io.KeyCtrl ? ViewportPickMode::Toggle : (io.KeyShift ? ViewportPickMode::Add : ViewportPickMode::Replace);
	if (const std::optional<glm::uvec2> pixel = m_Image.ToPixel(glm::vec2(io.MousePos.x, io.MousePos.y)))
	{
		// The game UI the view shows is in front of the scene (its screen-space canvases while Game UI is on, the
		// canvases in the scene always): a click on one of its elements selects it.
		const UIScreen screen { glm::vec2(size), context.GetGameWindow().GetState().ContentScale };
		const glm::mat4 viewProjection = view ? view->Camera.Projection * view->Camera.View : glm::mat4(1.0f);
		const Entity element = UIRectEdit::PickElement(*context.GetActiveScene(), screen, glm::vec2(*pixel) + glm::vec2(0.5f),
			settings.ShowGameUI, view ? &viewProjection : nullptr);
		if (element)
			EditorViewport::ApplyPick(context, element, mode);
		else
			viewport.RequestPick(*pixel, size, mode);
```

1. **Line 251:** a pick needs a hover, a left click, no **Alt** and no gizmo.
2. **Line 253:** the key state chooses the mode of the pick.
3. **Lines 260–261:** UI elements are asked first, with the camera's matrices for canvases in the scene.
4. **Lines 262–265:** an element is applied at once; otherwise the pick of the scene is requested.

`RequestPick` is the start of the sequence. It refuses when the renderer's size differs from the image's size, which happens in the frame in which the person changed the panel's size. The pixel that was clicked belongs to a picture that no longer exists. Otherwise it asks the scene renderer for a one-pixel :term[readback]{id=readback} of the ID buffer. It remembers three things: the scene that was drawn, the mode and the time.

```cpp src="StrataEditor/src/Editor/EditorViewport.cpp#L427-L440" symbol="EditorViewport::RequestPick"
bool EditorViewport::RequestPick(const glm::uvec2& pixel, const glm::uvec2& imageSize, ViewportPickMode mode)
{
	if (!m_Renderer || m_Renderer->GetSize() != imageSize)
		return false;
	Scope<TextureReadback> readback = m_Renderer->GetSceneRenderer().ReadEntityIDAsync(pixel.x, pixel.y);
	if (!readback)
		return false;
	m_Pick = CreateScope<PendingPick>();
	m_Pick->Readback = std::move(readback);
	m_Pick->PickedScene = m_Renderer->GetRenderedScene();
	m_Pick->Mode = mode;
	m_Pick->Requested = std::chrono::steady_clock::now();
	return true;
}
```

1. **Line 429:** a picture of another size means the pixel belongs to nothing: no request.
2. **Line 431:** the readback copies one pixel of the ID buffer, and the caller does not wait for it.
3. **Lines 434–438:** the pending pick keeps the readback, the drawn scene, the mode and the time.

A newer click replaces an older pending pick, since only the latest click matters. The weak reference to the drawn scene does not keep the scene alive: a scene that is closed in the meantime cannot be found again.

```mermaid caption="A click at frame N starts a one-pixel readback. The answer is polled each frame and is checked against the open scene before it selects anything, or it is dropped when the time runs out." alt="A sequence of frames. At frame N the click asks for a one-pixel readback and stores the scene and the mode. In each frame up to N plus k the poll finds the readback not ready. At frame N plus k the readback is ready, the scene check passes, and the pick is applied to the selection. Two other exits drop the pick: a different open scene, and a timeout of five seconds."
flowchart LR
    Click["Frame N: click, RequestPick stores pixel, scene, mode, time"]
    Poll["Frames N+1 to N+k-1: UpdatePicking, not ready"]
    Ready["Frame N+k: readback ready"]
    Check{"Same scene still open?"}
    Apply["ApplyPick: Replace, Toggle or Add"]
    Drop["Dropped"]
    Time["Five seconds without an answer: warning, dropped"]
    Click --> Poll --> Ready --> Check
    Check -->|"yes"| Apply
    Check -->|"no"| Drop
    Poll -->|"too long"| Time
```

:::why
Why not wait for the readback in the frame of the click? The CPU would wait until the GPU finished all the frames in front of the copy, about 30 ms in the example above, and a person who clicks often would feel the editor stall. Strata trades that stall for a delay of two or three frames that nobody sees. It pays with the pending state and the scene check that this section shows.
:::

`UpdatePicking` runs once per frame from the editor context's update, not from the panel, so a pick still finishes when the panel is hidden for a frame. Follow its three exits.

```cpp src="StrataEditor/src/Editor/EditorViewport.cpp#L442-L466" symbol="EditorViewport::UpdatePicking"
void EditorViewport::UpdatePicking(EditorContext& context)
{
	if (!m_Pick)
		return;
	if (!m_Pick->Readback->IsReady())
	{
		if (std::chrono::steady_clock::now() - m_Pick->Requested > c_PickTimeout)
		{
			ST_WARN("Picking in the viewport timed out: the GPU did not finish the readback");
			m_Pick.reset();
		}
		return;
	}

	const Scope<PendingPick> pick = std::move(m_Pick);
	ReadbackImage image;
	if (!pick->Readback->GetResult(image) || image.Pixels.size() != sizeof(uint32_t))
		return;
	const Ref<Scene> scene = pick->PickedScene.lock();
	if (!scene || scene != context.GetActiveScene())
		return; // The clicked image showed another scene
	uint32_t id = 0;
	std::memcpy(&id, image.Pixels.data(), sizeof(id));
	ApplyPick(context, SceneRenderer::GetEntityFromID(*scene, id), pick->Mode);
}
```

1. **Lines 448–452:** not ready means come back next frame, unless five seconds (`c_PickTimeout`) have passed. Then a warning is logged and the pick is dropped, so a hung graphics card never leaves a pick pending forever.
2. **Line 458:** a failed or wrongly sized result is dropped without a message, because the image may have changed.
3. **Lines 460–462:** the scene check, the center of the safety: the weak reference must lock, and it must equal the active scene.
4. **Line 465:** the pixel holds the entity's handle plus 1, with 0 meaning nothing was drawn, and `ApplyPick` turns it into a selection.

`ApplyPick` itself checks again that the entity belongs to the active scene. A Replace with no entity clears the selection, which is how a click on empty space clears it. A Toggle or an Add with no entity does nothing, so a missed **Ctrl** click never loses the selection.

### The gizmo drag

The gizmo draws every frame for the primary selection, which is the entity that was selected last. Nothing is drawn without one, nor when the operation is none, nor while a scene is opening, because that scene is read-only. If the selection changed under a running drag, for example by a late pick or by an agent's command, the drag ends first. The gizmo's matrix belongs to the old entity, and applying it to another would make that one jump.

```cpp src="StrataEditor/src/Panels/ViewportPanel.cpp#L1006-L1028"
const float snapStep = settings.Gizmo == GizmoOperation::Translate ? settings.TranslateSnap
	: (settings.Gizmo == GizmoOperation::Rotate ? settings.RotateSnap : settings.ScaleSnap);
const float snap[3] = { snapStep, snapStep, snapStep };
// Ctrl inverts the snap toggle for as long as it is held.
const bool snapping = settings.Snap != ImGui::GetIO().KeyCtrl;
glm::mat4 world = context.GetActiveScene()->GetWorldTransform(primary);
const ImGuizmo::MODE mode = settings.Space == GizmoSpace::World ? ImGuizmo::WORLD : ImGuizmo::LOCAL;
const bool changed = ImGuizmo::Manipulate(&view.Camera.View[0][0], &view.Camera.Projection[0][0], ToImGuizmo(settings.Gizmo), mode, &world[0][0], nullptr,
	snapping ? snap : nullptr);

// The frame the mouse is released still carries the last movement (and snap step): apply it, then end the drag.
const bool dragging = ImGuizmo::IsUsing();
if ((dragging || changed) && !m_GizmoDrag)
	m_GizmoDrag = TransformDrag::Begin(context, settings.Gizmo);
std::string error;
if (changed && m_GizmoDrag && !m_GizmoDrag->Update(context, world, &error))
{
	ST_WARN("Transform gizmo: {}", error);
	EndGizmoDrag(context);
	return;
}
if (!dragging)
	EndGizmoDrag(context);
```

1. **Line 1010:** the snap flag is the toolbar's toggle compared with **Ctrl**: the key inverts it.
2. **Line 1013:** `Manipulate` changes the world matrix while the person drags, and reports whether it did.
3. **Lines 1018–1019:** the first frame of use or change begins the drag from the state of that frame.
4. **Lines 1021–1026:** a failed update logs its reason and ends the drag.
5. **Line 1027:** when the mouse is up, the drag ends, after its last update.

Everything about snapping and space is read here, once per frame. The snap flag is the toolbar's toggle compared with **Ctrl**, and the space is a switch between two ImGuizmo modes. `Manipulate` takes the camera's matrices, the operation, the mode, the primary's world matrix and the snap steps, and it changes the matrix when the person drags. It also reports whether anything changed.

Three details of the end matter. A drag begins at the first frame in which ImGuizmo is in use or reports a change. The frame in which the mouse is released still carries the last movement, so `Update` runs before `End`. And if `Update` fails, a warning names the reason and the drag ends without a half-applied change.

The class `TransformDrag` is what turns the matrix back into entity values. `Begin` records, for every selected entity that has no selected ancestor, its world matrix and its :term[local transform]{id=local-transform}. Children of selected parents do not appear in the list, because they follow their parents. It also makes the merge key, which is unique per drag.

```cpp src="StrataEditor/src/Editor/TransformEdit.cpp#L201-L216"
// Back at the start, everything returns exactly to where it was (so a drag back to its start records no step).
const bool atStart = primaryWorld == m_PrimaryStart;

// Computed for every entity before anything is written, so a failure changes nothing.
std::vector<std::pair<Entity, TransformComponent>> results;
for (const DraggedEntity& dragged : m_Entities)
{
	Entity entity = scene->GetEntityByUUID(dragged.ID);
	if (!entity)
		continue; // Deleted during the drag (e.g. by a running script)
	Entity parent = entity.GetParent();
	const glm::mat4 parentWorld = parent ? scene->GetWorldTransform(parent) : glm::mat4(1.0f);

	TransformComponent local = dragged.StartLocal;
	switch (atStart ? GizmoOperation::None : m_Operation)
	{
```

1. **Line 202:** a drag back at its start restores the exact start values, so it leaves no step.
2. **Line 205:** results are computed for all entities before anything is written.
3. **Line 210:** an entity deleted during the drag, for example by a running script, is skipped.
4. **Line 212:** the parent's world matrix turns the world offset into the entity's :term[local space]{id=local-space}.

The drag is at its start when the gizmo's matrix equals the start matrix. Then every entity returns exactly to the recorded values, so a drag back to the start records no step at all. For a translation, the world offset is turned into the parent's space with the inverse of the parent's world matrix. The offset goes in as a vector of four numbers whose fourth, w, is 0, because an offset is a direction and a parent's position does not apply to it. That is how a crate under a scaled parent moves by the right amount.

Rotation turns the entities around the gizmo's origin and keeps their local scale. A reflection in the result stays on the axes it had at the start, so a mirrored entity does not flip when it turns. Scaling multiplies the start scale by the gizmo's factor along the entity's own axes.

Every result is computed before anything is written, so a failure changes nothing. Then the results go into one `SceneEditTransaction`.

```cpp src="StrataEditor/src/Editor/TransformEdit.cpp#L258-L268"
for (const auto& [entity, local] : results)
	ids.push_back(entity.GetUUID());
SceneEditTransaction transaction(*scene, m_Name, ids, m_MergeKey);
for (auto& [entity, local] : results)
{
	entity.GetComponent<TransformComponent>() = local;
	// The registry's update signal tells systems (physics) about the move.
	entity.MarkModified<TransformComponent>();
}
context.CommitEdit(transaction);
return true;
```

1. **Line 260:** one transaction holds every dragged entity, with the drag's name and merge key.
2. **Lines 263–265:** the new local values are written and announced, so physics and the caches follow.
3. **Line 267:** `CommitEdit` records the change as part of the step with that key.

The transaction has the same name and the same merge key in every frame of the drag. The :term[undo stack]{id=undo-stack} merges the steps that share a key, so the whole drag is one step whose "before" is the state at the drag's start. `Begin` also calls `BreakMerge`, and so does `End`, so that the next drag never merges into this one even if it moves the same entity. While the game plays, a drag changes the running scene, and `play.stop` discards the change; `Begin` logs a warning for it.

```mermaid caption="One gizmo drag, from the first handle press to the last one. Frames in the middle apply the gizmo's total offset to the start state and merge into the same undo step." alt="A sequence from the first frame of a drag to its end. Manipulate reports a change, Begin records the start state and a merge key, each following frame calls Update with the gizmo's matrix, and the transaction merges by key into one undo step. When the mouse is released, End breaks the merge."
sequenceDiagram
    participant P as ViewportPanel
    participant G as ImGuizmo
    participant D as TransformDrag
    participant U as Undo stack
    P->>G: Manipulate with the primary's world matrix
    G-->>P: changed, in use
    P->>D: Begin: record start states, new merge key
    loop each frame of the drag
        P->>D: Update with the new matrix
        D->>U: CommitEdit with the same merge key
    end
    G-->>P: not in use
    P->>D: Update with the last matrix, then End
    D->>U: BreakMerge
```

::figure{id=scene-view-gizmos}

The handles are small beside the view, so the enlarged part below shows the green arrow leaning with the drum.

::figure{id=scene-view-gizmos crop=gizmo}

### The chips

The chips are in the toolbar strip, drawn by the kit's chip strip from [the widget kit](widget-kit.md). The last chips that do not fit with their labels become icons, with the labels in their tooltips, and those that still do not fit move to a second row. The strip remembers how many rows it used last frame, so the image's rectangle is always computed from a known height.

The camera chip opens a :term[popup]{id=popup} with the :term[field of view]{id=field-of-view}, the clip planes, the fly speed, the frame commands and the characters' pose while editing. Grid, outline and gizmos are toggles for the ground grid, the selection's outline and the shapes of lights, cameras and colliders. A statistics toggle draws the frame's numbers at the image's top left. Preview lighting lights a scene that has no light of its own, in this view only.

The Game UI chip shows the game's screen-space UI in the :term[editor view]{id=editor-view}, and a click then selects an element. The 2D chip starts canvas mode, taught below, and a quality chip sets this view's own quality setting. While a world is open, a Cells chip also shows the squares of its cells around the camera.

The gizmo's own controls are not chips. The operation buttons, the World and Local toggle and the snap toggle sit in the editor's main toolbar. Their shortcuts, **Q**, **W**, **E** and **R**, work while the pointer is over the Scene view or it has the keyboard focus. The shortcut keys are on [the Game view's page](game-view.md).

The **debug view** chip colors the image by one property, such as the level of detail, texture streaming or shadows. The list of views and what each shows belongs to [debugging](../gpu/debugging.md). The panel adds to it the legend: while a view is on, the key to its colors stands at the image's bottom left, with a line of text under it in some views.

```cpp src="StrataEditor/src/Panels/ViewportPanel.cpp#L772-L778" from="else if (settings.DebugView == ViewportDebugView::LOD)" to="std::to_string(stats.EntitiesPerLOD[level]) });" symbol="ViewportPanel::DrawDebugViewLegend"
else if (settings.DebugView == ViewportDebugView::LOD)
{
	for (size_t level = 0; level < settings.DebugColors.LOD.size(); level++)
	{
		const bool last = level + 1 == settings.DebugColors.LOD.size();
		lines.push_back({ toColor(settings.DebugColors.LOD[level]), GetLODLegendName(level, last, stats.MaxErrorPixelsPerLOD[level]),
			std::to_string(stats.EntitiesPerLOD[level]) });
```

The legend asks the renderer for numbers that it already counted, and does not walk the scene. In the level-of-detail view each line holds a color, a name of the level and the number of entities drawn at it. The counts are entities, not area. One large entity, such as the ground, can color most of the picture while the line of another color counts the most.

The other views fill the same box in their own ways. The `mip` view counts entities by how many texture levels they lack, and the `culled` view counts the objects omitted as too small or hidden behind others. The `luminance` and `clusters` views list bands of color without counts, and `albedo` gives the share of the image above and below its range.

Views with nothing to count show only the line of text. The `wireframe` view names the number of triangles drawn, `voxels` the levels and their sizes, and `probes` the number of probes with the dead ones in red. The light views, among them `specular`, `diffuse` and `gi`, show the ratio of sun to sky light on flat ground.

::figure{id=scene-view-lod-legend}

A **game camera**, also called the pilot, is the scene's :term[primary camera]{id=primary-camera} used as the Scene view's own camera: the **Game camera** chip or **F8** looks through it with the editor's overlays on. The editor camera stays where it was, and its controls are left alone while piloting. A last chip, shown only while an animation preview is active and the game is not playing, names the preview and stops it on a click through the `animation.preview` command.

### The agent chip and the flash

An agent, an artificial intelligence (AI) client that drives the editor through [commands](../editor/commands.md), changes the scene while the person looks at it. The person must see that. The agent chip sits at the strip's right end and reads like "Agent: entity.create · 3 s ago". It shows while an automation client is connected, and for 60 seconds after the last command when none is.

A click shows the command's entry in the Activity panel, which [the journal's page](../editor/journal.md) describes. The chip's text is made again at most once a second, since the age changes at that rate.

The flash answers the question "what did it touch?". When a new command appears, the panel takes the bounds of at most 64 entities that the command changed, once. It draws their screen rectangles in the accent color over the image for 0.6 s, while the alpha falls from 1 to 0. Boxes that reach behind the camera are skipped.

The fade is timed from the command's finish by the clock and not by counting draws. A view that stops being drawn therefore cannot keep the editor at full frame rate. The panel reports itself as animating only while the clock says the flash is alive.

::figure{id=scene-view-agent-flash}

### The drop, and the load card

An asset dragged from the Content Browser over the image is accepted before the release, so the view can show where it would land. The panel builds the pointer's ray through the camera that the view shows, uses the toolbar's snap step when snapping is on (inverted by **Ctrl**), and hands it to the placement preview. The ghost is drawn by the renderer, and the panel draws only the label beside the pointer, kept inside the image. How the place is decided is on [the placement page](../editor/placement.md).

On release, the panel runs the same request that the ghost used, through `asset.place`. When the asset is a material and the pointer is over a mesh, `component.set` writes the material onto that mesh renderer instead. Both are commands, so each is one :term[undo step]{id=undo-step}. Every asset is accepted over the view, so a release always ends the drag here. Those that cannot be placed do nothing, and the label said why.

A scene opens in the background and is read-only while it does. The panel then draws a card in the middle of the image with the scene's name over a progress bar and the step that is running. Before the scene's own reading, a project's first scene waits for the scan of the project's assets, and the card shows that progress instead. The gizmo is hidden during the whole time.

### Canvas mode

A game's screen-space UI is laid out for a screen of a known shape, and a 3D view of any other shape cannot show that layout truthfully. **Canvas mode** is the Scene view's second way to show the scene. The 2D chip shows the selection's UI canvas flat, at its reference aspect ratio, so that the person places and sizes its elements with handles. It works only while the game is not playing, and only for screen-space canvases. A world-space canvas stands in the scene and is edited there.

The mode picks the canvas of the selection, going up to the outermost canvas, or else the first screen-space canvas of the scene in draw order. The image is letterboxed: the canvas keeps its aspect ratio, and bars fill the rest of the area under the toolbar. While the mode is on, the panel forces the game UI on, switches the editor overlays and the gizmo off, and ends any camera drag. The scene is drawn behind the canvas through its camera, or the editor camera if it has none.

Inside the mode, a press on a handle of the selection changes its size, a press on its rectangle moves it and a press elsewhere selects what is there. Dragging snaps when the snap toggle differs from **Ctrl**, as the gizmo does. The wheel zooms about the pointer, the middle button pans, **F** frames the selection and **Home** returns to the whole canvas. Zoom and pan do not move any entity: they are the [screen view](../gpu/debug-drawing.md) that the overlay pass applies, and the layout's rules are on [the layout page](../ui/layout.md).

What the view reports as the game's screen is the canvas at its fit, however it is zoomed. The Inspector's pixel values and the captures therefore agree with the layout that the person sees.

::figure{id=scene-view-canvas-mode}

The enlarged part below shows the selected slider's outline and its square handles.

::figure{id=scene-view-canvas-mode crop=slider}

::figure{id=scene-view-game-ui-chip}

## A worked example

:::example
A crate is a child of a parent that stands at x = 4 and has scale 2. The crate's local x is 3, so its world x is 4 + 2 × 3 = 10. The person selects the crate and drags the Translate handle. The panel's image is 1,280 pixels wide at 60 frames per second.

At frame 100 the person clicks on the crate's pixel. `RequestPick` stores the scene and the pixel and starts a one-pixel readback. In frame 101, and in frame 102 when the answer is late, `UpdatePicking` finds the readback not ready. It is ready at frame 102 or 103, the scene check passes and the pixel's value minus 1 is the crate's handle, so `ApplyPick` selects it: 33 to 50 ms after the click.

Then the person drags the handle to a world offset of 1.3 m with snapping on and a step of 0.5. ImGuizmo snaps the offset to 1.5 m. `TransformDrag::Update` converts it: the inverse of the parent turns 1.5 m of the world into 0.75 m of the parent's space. The crate's local x becomes 3 + 0.75 = 3.75, and its world x is 4 + 2 × 3.75 = 11.5, which is 10 + 1.5. Every frame of the drag computes this from the start values, and the whole drag leaves one undo step that returns the local x to 3.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| CPU ray against boxes or triangles | Many editors, for physics-style picking and for tools without a GPU | An answer in the same frame and no readback to manage | Wrong at edges (boxes), or the cost of posed triangles of skinned and fading things; a second description of what is drawn |
| Blocking readback of the ID buffer | Tools and tests | One function, no pending state, no scene check | A stall of two or more frames at every click |
| A larger readback, the whole image or a region | Box selection and some editors for hover highlights | Hover and box selection from one read | :term[Bytes]{id=byte} copied per click (3.5 MB for a full 1,280 by 720 image) and a slower answer |
| Drawing the gizmo as scene geometry | Engines whose editors are part of the game's renderer | Depth tests and one drawing path | A second set of :term[shaders]{id=shader} and picking for handles; the gizmo would not cooperate with the window system |
| A gizmo that adds each frame's change | Simple tools | Less state | Drift by rounding and one undo step per frame |

## How it is tested

The picking tests are in the GPU suite `GPU.Editor.Viewport`, run with the label `gpu` and a graphics card. The case "Clicks in the viewport pick entities without blocking" clicks the image and checks that the click does not wait and that the selection follows in later frames. The case "While the game plays, the Scene view's editor camera picks the running scene's entities" checks the running copy.

The gizmo's case lives in `StrataTests/src/Editor/EditorUITests.cpp`. The case "Gizmo drags snap per the toolbar's snap toggle, inverted while Ctrl is held" puts an entity under the gizmo's center handle and drags it with the mouse of a test harness. It checks that the movement snaps to whole steps only when the toggle and **Ctrl** differ, and that one undo returns the entity to where it started.

Canvas mode and its picking are covered by `EditorGameUITests`, `EditorUICommandTests` and `GPUCanvasEditTests`. Run a suite or one case directly with a doctest filter:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.Editor.Viewport
build/windows/bin/Debug/StrataTests.exe --test-case="Gizmo drags*"
```

The first line runs the whole suite, which needs a graphics card, and the second runs the gizmo case alone. Continuous integration (CI) skips the tests with the label `gpu` on machines that have no card.

## Changing it safely

New chips go in `ViewportPanel::DrawChips`, as `UI::ToggleChip` or `UI::Chip` items that the strip can shrink to icons. The setting lives in `ViewportSettings`, so that it is saved and can be set with `viewport.setSettings`. A new overlay goes after the image is drawn, inside `DrawOverlays`, and draws only. If it needs the mouse, it takes an item or follows the gizmo's rule.

Keep these rules, each of which a bug of this kind of panel taught:

- Colors come from the theme's tokens, which is how ImGuizmo receives the axis colors, so a theme change changes the colors of the gizmo.
- Never block on a readback: use `TextureReadback` and poll.
- Never change the scene from the panel except through a command or a `SceneEditTransaction`.
- Keep the gizmo library inside the editor's UI library.
- Hold nothing about a scene except a weak reference, and compare it again when the answer returns.

Before a commit, run `GPU.Editor.Viewport`, the gizmo case of `EditorUITests` and the editor's Game UI tests. Check a new overlay with the Scene view at a narrow width, where the chips wrap, and with a scene that is opening.

## Summary

- The Scene view renders at the panel's pixel size into a target and shows it as an item; over the gizmo the item is a `Dummy`, so ImGuizmo owns the mouse.
- A click asks for a one-pixel readback of the ID buffer; `UpdatePicking` applies it frames later only if the same scene is open, or drops it after five seconds.
- A gizmo drag computes every frame from the state at its start, converts into the parent's space and merges into one undo step through one merge key.
- Chips, the legend, the agent chip and flash, the load card and canvas mode add what the person needs around the image, without ever covering the game's own screen.

## Check yourself

1. A panel is 800 by 450 points on a display with 2 pixels per point. How large is the render target, and what happens if the code renders 800 by 450 instead?

   :::answer{tests="image-and-gizmo"}
   The target is 1,600 by 900 pixels. At 800 by 450 each rendered pixel covers four screen pixels, so the image is blurred and every edge is soft.
   :::

2. The person clicks the crate and, one frame later, presses a key that opens another scene. The readback finishes two frames after the click. Which statement is right?
   - A. The crate of the old scene is selected, because the click was valid.
   - B. Nothing is selected, because the weak reference no longer equals the active scene.
   - C. The pick waits five seconds, then selects.
   - D. The editor stalls until the readback finishes.

   :::answer{tests="pick-timeline"}
   B. `UpdatePicking` compares the stored scene with the active scene and drops the pick. A would select an entity that does not exist in the open scene. C confuses the scene check with the timeout, and D describes a blocking readback, which the editor never uses.
   :::

3. A drag is applied each frame as the offset since the previous frame, and snapping is on at 0.5 m. Why would the result be wrong, even though each frame is correct?

   :::answer{tests="gizmo-undo"}
   Each small offset is snapped on its own, so most round to 0 and the crate would hardly move; :term[rounding errors]{id=rounding-error} also add up. The real code snaps the total offset and computes from the start state.
   :::

4. Where does the legend's count for each color come from?

   :::answer{tests="around-the-image"}
   From statistics that the renderer counted while it drew the view. The panel does not walk the scene to count.
   :::

5. A person clicks on an empty pixel while holding **Ctrl**. What happens to the selection?

   :::answer{tests="pick-timeline"}
   Nothing changes. A Toggle with no entity does nothing. Without **Ctrl**, the click would clear the selection.
   :::

6. Why does the panel replace the image button by a `Dummy` while the pointer is over the gizmo?

   :::answer{tests="image-and-gizmo"}
   ImGuizmo accepts a drag only when Dear ImGui reports no hovered item. The image button would be that item and would take the click, so the gizmo would never move. A `Dummy` is space that takes no click.
   :::

## Exercises

1. **Basic.** A crate has local x = 3 under a parent at x = 4 with scale 2. The gizmo reports a world offset of 1.3 m with a snap step of 0.5. Write a program that prints the local and world x before and after.

   :::answer[Worked solution]{tests="gizmo-undo" solution="sketches/editor-ui-scene-view-drag.cpp"}
   The snapped offset is 1.5 m. A direction ignores the parent's translation, so the inverse of the parent's matrix halves it.

   ```cpp sketch="editor-ui-scene-view-drag.cpp"
   // A gizmo's world offset, turned into a local translation under a parent that moves and scales.
   #include <glm/glm.hpp>
   #include <glm/gtc/matrix_transform.hpp>

   #include <cmath>
   #include <cstdio>

   int main()
   {
   	// The parent sits at x = 4 and is twice as large. The crate's local x is 3, so its world x is 4 + 2 * 3 = 10.
   	glm::mat4 parentWorld = glm::translate(glm::mat4(1.0f), glm::vec3(4.0f, 0.0f, 0.0f));
   	parentWorld = glm::scale(parentWorld, glm::vec3(2.0f));
   	const glm::vec3 startLocal(3.0f, 0.0f, 0.0f);
   	const glm::vec3 startWorld = glm::vec3(parentWorld * glm::vec4(startLocal, 1.0f));

   	// The drag's raw offset in world metres, with the snap step of 0.5 m.
   	const float step = 0.5f;
   	const float raw = 1.3f;
   	const float snapped = std::round(raw / step) * step;

   	// An offset is a direction, so w is 0: the parent's translation must not apply to it.
   	const glm::vec3 worldOffset(snapped, 0.0f, 0.0f);
   	const glm::vec3 localOffset = glm::vec3(glm::inverse(parentWorld) * glm::vec4(worldOffset, 0.0f));
   	const glm::vec3 endLocal = startLocal + localOffset;
   	const glm::vec3 endWorld = glm::vec3(parentWorld * glm::vec4(endLocal, 1.0f));

   	std::printf("start: local %.2f, world %.2f\n", startLocal.x, startWorld.x);
   	std::printf("snapped offset: %.2f m in the world, %.2f in the parent's space\n", snapped, localOffset.x);
   	std::printf("end: local %.2f, world %.2f\n", endLocal.x, endWorld.x);
   	return 0;
   }
   ```

   ```text output-of="editor-ui-scene-view-drag.cpp"
   start: local 3.00, world 10.00
   snapped offset: 1.50 m in the world, 0.75 in the parent's space
   end: local 3.75, world 11.50
   ```

   1. **Line 12:** `glm::scale` multiplies on the right, so the parent's matrix scales a local point first and then moves it by 4.
   2. **Line 19:** the raw offset is snapped as a whole, in whole steps of 0.5 m.
   3. **Line 23:** w is 0, so the inverse of the parent turns the world offset into the parent's space without its translation.
   4. **Line 25:** the world position after the drag is the start plus the snapped offset, as the example says.
   :::

2. **Medium.** Trace a click: put breakpoints in `EditorViewport::RequestPick` and `EditorViewport::UpdatePicking`, click an entity in a Debug build of the editor, and count the frames from the request to the selection. Name the file and function that decide whether the pick is applied.

   :::answer[Worked solution]{tests="pick-timeline"}
   Expect the request at frame N and the readback ready at frame N plus 2 or 3. `UpdatePicking` in `StrataEditor/src/Editor/EditorViewport.cpp` decides: it compares the stored scene with the active scene, and `ApplyPick` applies the mode.
   :::

3. **Hard.** A scene holds 2,000 skinned characters and 50,000 foliage cards. Argue for the ID buffer against a CPU ray against bounds.

   :::answer[Worked solution]{tests="pick-timeline"}
   A skinned character's bounds in the rest pose do not match its animated pose, and foliage cards are thin: a ray against their boxes selects a card whose pixels are transparent. The ID buffer holds what the prepass drew, so the animated pose is right, and the cost is one pixel per click plus a few frames of delay.
   :::

## Where it lives in Strata

- `StrataEditor/src/Panels/ViewportPanel.cpp`: `ViewportPanel`, its chips, the gizmo, the flash and the load card.
- `StrataEditor/src/Editor/EditorViewport.cpp`: `RequestPick`, `UpdatePicking`, `ApplyPick`.
- `StrataEditor/src/Editor/TransformEdit.cpp`: `TransformDrag` and `WorldToLocal`.
- `StrataEditor/src/Panels/CanvasModeView.cpp` and `StrataEditor/src/Editor/CanvasEdit.cpp`: canvas mode.
- `StrataTests/src/Editor/GPUEditorViewportTests.cpp`: the suite `GPU.Editor.Viewport`.
- `StrataTests/src/Editor/EditorUITests.cpp`: the gizmo snapping case.

## Further reading

- ImGuizmo, the library's README and header: how its handles and snapping work (intermediate).
- Real-Time Rendering, Akenine-Moller, Haines and Hoffman: picking and selection buffers (intermediate).
