---
id: editor-ui/imgui-backends
title: "ImGui backends"
description: "How Strata feeds its window's events into ImGui and draws ImGui's triangles through NVRHI, from a key press to pixels."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/imgui, core/engine-modules, gpu/binding, gpu/resources-lifetimes, basics/color]
time: 95
learn:
  - id: frame-trace
    text: trace one frame of the editor's user interface from a key press to pixels
  - id: key-queue
    text: explain why a key release is queued as the key its press was queued as
  - id: push-constants
    text: compute the push constants and the scissor rectangle of a window by hand
  - id: buffer-ring
    text: predict how many buffer sets the renderer holds for a given lag of the graphics card
  - id: display-modes
    text: choose the texture display mode for a texture format and explain how a draw callback is told apart
since: 0.3.0
status: final
---

:term[ImGui]{id=dear-imgui} is a library that turns calls such as a button into lists of triangles. It never opens a window, reads a key or talks to a :term[graphics card]{id=gpu}. Two small programs of Strata do those jobs for it: the platform backend, which tells ImGui what the window's events mean, and the :term[renderer]{id=renderer} backend, which draws ImGui's triangles into a frame. This page follows one frame of the editor's user interface (UI) through both, from a key press to pixels. It does not cover the scale of the interface, the theme and fonts, or the widgets that call these backends: those are other pages.

## The problem and how engines solve it

ImGui builds a frame of draw data, the triangles of every window, from the input you give it. A backend is the code on either side of that. The platform side answers "where is the mouse, which keys are down, what did the person type". The :term[renderer]{id=renderer} side answers "how do I draw 5,000 triangles with these clip rectangles". ImGui ships with ready backends for many windowing libraries and graphics interfaces, and most engines use them as they are.

For Strata, the ready pair would be `imgui_impl_glfw` and `imgui_impl_vulkan`. The pair has three costs here. The :term[GLFW]{id=glfw} backend would pull the window library into code that the architecture seals inside `Platform/`. The :term[Vulkan]{id=vulkan} backend would draw through Vulkan calls of its own, beside the engine's device, its resource tracking and its :term[shader]{id=shader} library, which all go through :term[NVRHI]{id=nvrhi}.

The pair also does work the editor does not need. At the pin, the GLFW backend is 1,727 lines and the Vulkan one 2,378. Each frame the GLFW backend reads the cursor position and window attributes from the system, and it supports ImGui's extra platform windows.

Strata writes both backends, in `Strata/src/Strata/ImGui/`. Four reasons decided it:

- The window library stays sealed. `ImGuiPlatform` reads only the engine's `Window` and its events, so no GLFW :term[header]{id=header} reaches the editor.
- Rendering goes through NVRHI. `ImGuiRenderer` uses the engine's device, shader library and :term[deferred release]{id=deferred-release}, so the UI follows the same lifetime rules as the scene.
- The editor wants keys by keyboard layout, so that **Ctrl+Z** undoes on every layout, and wants a cursor that a running game may lock or hide.
- The engine's `Docs/Roadmap.md` records a measurement: the vendored GLFW backend spent 0.05 to 0.06 ms of every frame on multi-viewport support the editor does not use. That is about 0.3 to 0.4 % of a 16.7 ms frame, for nothing.

The price is code to keep. Strata compiles only ImGui's core (`Strata/vendor/CMakeLists.txt` says so), and every new ImGui feature that touches a backend, such as the dynamic textures below, is Strata's to write.

One more input problem decides the design. A backend that both listens to events and reads the key state each frame sees a press twice. A backend that listens only sees nothing when the window loses focus: the release never comes and the key stays down. Strata listens only, and handles the focus loss by hand, as the platform section shows.

## The map: five pieces and two flows of data

Five pieces make the path. `ImGuiModule` is the :term[engine module]{id=engine-module}. It owns nothing of ImGui itself but creates `ImGuiLayer`, pushes it as the top :term[overlay]{id=overlay-core} and draws the frame.

The layer owns the :term[ImGui context]{id=imgui-context} and the two backends. `ImGuiPlatform` carries input in. `ImGuiRenderer` carries triangles out, using the shaders `ImGui.vert` and `ImGui.frag`. Everything runs on the :term[main thread]{id=main-thread}.

```mermaid caption="Events flow down from the window to ImGui, and draw data flows out to the screen. The module owns the layer, and the layer owns both backends." alt="A diagram with two flows. In the input flow, the window's events reach the layer, which passes them to the platform backend, which queues them in ImGui. In the drawing flow, the module starts the frame, the layers draw their widgets, the layer renders ImGui, and the renderer backend draws with two shaders into the back buffer."
flowchart TD
    W["Window events"] --> L["ImGuiLayer::OnEvent"]
    L --> P["ImGuiPlatform: keys, text, mouse, focus"]
    P --> I["ImGui: queued input"]
    M["ImGuiModule::OnRenderUI"] --> B["ImGuiLayer::Begin: NewFrame"]
    B --> D["Every layer: OnImGuiRender"]
    D --> E["ImGuiLayer::End: ImGui::Render"]
    E --> R["ImGuiRenderer::Render"]
    R --> S["ImGui.vert and ImGui.frag"]
    S --> BB["Back buffer"]
    I -.-> B
```

The module needs the Graphics module and a window that the device can present into, as [engine modules](../core/engine-modules.md) explains for dependencies. If either is missing, `OnInit` logs an error and returns false, and the program does not run. A test's stand-in window, which the device cannot present into, is refused too. Games have none: only editors and tools list the module.

The module's `Specification` holds one value, the layout file. ImGui keeps the position of docked panels there, and an empty path means none is kept.

## The contract: four rules and their reasons

Four rules keep the backends sound. Each has a reason that you can check in the code.

:::rule[User textures stay alive until the frame's draw data is drawn]
An `ImTextureID` that the renderer draws is a pointer to an NVRHI texture. The :term[command list]{id=command-list} that draws it runs after the UI code returned, so the texture must stay alive until that list has been recorded. The renderer then keeps each texture alive for 8 more frames through its cached :term[binding sets]{id=binding-set}, because the graphics processing unit (GPU) may still read it. The header `Strata/src/Strata/ImGui/ImGuiRenderer.h` states the rule.
:::

:::rule[Never identify draw callbacks by function address]
A draw :term[callback]{id=callback} is a :term[function pointer]{id=function-pointer} that sits in the command list between two draws. A :term[linker]{id=linker} may merge two functions with identical code into one address, so comparing addresses can match the wrong callback. Strata gives each display mode its own piece of :term[user data]{id=user-pointer} and compares the data's address, which the linker keeps apart. A comment in `Strata/src/Strata/ImGui/ImGuiRenderer.cpp` gives the same reason.
:::

:::rule[A release repeats the ImGui key its press became, and modifiers go before keys]
Layouts can change between the press and the release of a key, for example by the person switching the language while holding it. A release queued as another key leaves the first key stuck down in ImGui. ImGui also builds a key's chord from the modifiers it received earlier, so a modifier queued after its key would make **Ctrl+S** arrive as plain **S**.
:::

:::rule[Draw textures in UI code through `UI::TextureImage`]
Textures are stored in formats that look wrong when shown as they are: :term[sRGB]{id=srgb} colors, one-channel gray images and two-channel normal maps. `TextureImage`, a widget of the kit, adds the display callback that fixes the look. The kit is in [widget kit](widget-kit.md); the engine's [Developer Guide](https://github.com/2042Third/GameEngine/blob/319075e3f92b316db5cdd30560de08c1ffe0ae26/Docs/DeveloperGuide.md) states the same rule.
:::

A caller may assume more than it must do. It may call `Render` with a :term[framebuffer]{id=framebuffer} of any color format, because the renderer builds one pipeline for each format it meets. It may assume that a texture ImGui asks to create or update is ready before the draws that use it, because both are recorded into one command list in that order. It must execute that command list before the next `Render`, because the next call writes the buffers the draws read.

## A toy version: the renderer's steps without a GPU

A renderer backend does three things every frame. It gathers the triangles of all lists into big buffers. It maps pixels to the screen's coordinates. It issues one draw for each command, with a limit on where the draw may paint. The toy below keeps the arithmetic and replaces the GPU with text output.

The toy builds two draw lists, the way two ImGui windows would, and renders them for a 1600 by 900 display and then for an 800 by 450 display with a pixel density of 2.

Read `Render` for four things: the joined vertices and indices, the scale and translate, the clamped limits, and the global offsets added to each command's own.

```cpp sketch="editor-ui-imgui-backends-toy.cpp"
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

// A toy renderer backend: the steps of a UI renderer, with a printout in place of a GPU.
struct Vertex
{
	float X;
	float Y;
	float U;
	float V;
	uint32_t Color;
};

struct Command
{
	float ClipMinX;
	float ClipMinY;
	float ClipMaxX;
	float ClipMaxY;
	uint32_t ElemCount;
	uint32_t IdxOffset;
	uint32_t VtxOffset;
};

struct DrawList
{
	std::vector<Vertex> Vertices;
	std::vector<uint16_t> Indices;
	std::vector<Command> Commands;
};

struct DrawData
{
	float DisplayWidth;
	float DisplayHeight;
	float Scale; // Framebuffer pixels per display unit
	std::vector<DrawList> Lists;
};

static void Render(const DrawData& data)
{
	const float width = data.DisplayWidth * data.Scale;
	const float height = data.DisplayHeight * data.Scale;

	// One vertex buffer and one index buffer for every list, so each list starts after the one before it.
	std::vector<Vertex> vertices;
	std::vector<uint16_t> indices;
	for (const DrawList& list : data.Lists)
	{
		vertices.insert(vertices.end(), list.Vertices.begin(), list.Vertices.end());
		indices.insert(indices.end(), list.Indices.begin(), list.Indices.end());
	}

	// Pixels with y down to NDC with y up: x * scale + translate.
	const float scaleX = 2.0f / data.DisplayWidth;
	const float scaleY = -2.0f / data.DisplayHeight;
	std::printf("scale (%.7f, %.7f) translate (-1, 1), %zu vertices, %zu indices\n", scaleX, scaleY, vertices.size(), indices.size());

	uint32_t globalVertex = 0;
	uint32_t globalIndex = 0;
	for (const DrawList& list : data.Lists)
	{
		for (const Command& command : list.Commands)
		{
			const float minX = std::max(command.ClipMinX * data.Scale, 0.0f);
			const float minY = std::max(command.ClipMinY * data.Scale, 0.0f);
			const float maxX = std::min(command.ClipMaxX * data.Scale, width);
			const float maxY = std::min(command.ClipMaxY * data.Scale, height);
			if (maxX <= minX || maxY <= minY)
				continue;
			std::printf("draw %u indices from index %u, vertex %u, scissor x %.0f to %.0f, y %.0f to %.0f\n", command.ElemCount,
				command.IdxOffset + globalIndex, command.VtxOffset + globalVertex, minX, maxX, minY, maxY);
		}
		globalVertex += static_cast<uint32_t>(list.Vertices.size());
		globalIndex += static_cast<uint32_t>(list.Indices.size());
	}
}

int main()
{
	DrawList panel;
	panel.Vertices.assign(400, Vertex { 0.0f, 0.0f, 0.0f, 0.0f, 0xFFFFFFFFu });
	panel.Indices.assign(600, 0);
	panel.Commands = { Command { 10.0f, 20.0f, 210.0f, 120.0f, 600, 0, 0 } };

	DrawList popup;
	popup.Vertices.assign(120, Vertex { 0.0f, 0.0f, 0.0f, 0.0f, 0xFFFFFFFFu });
	popup.Indices.assign(180, 0);
	popup.Commands = { Command { 1500.0f, 800.0f, 1700.0f, 1000.0f, 180, 0, 0 }, Command { 5.0f, 5.0f, 5.0f, 90.0f, 3, 0, 0 } };

	Render(DrawData { 1600.0f, 900.0f, 1.0f, { panel, popup } });
	Render(DrawData { 800.0f, 450.0f, 2.0f, { panel, popup } });
	return 0;
}
```

```text output-of="editor-ui-imgui-backends-toy.cpp"
scale (0.0012500, -0.0022222) translate (-1, 1), 520 vertices, 780 indices
draw 600 indices from index 0, vertex 0, scissor x 10 to 210, y 20 to 120
draw 180 indices from index 600, vertex 400, scissor x 1500 to 1600, y 800 to 900
scale (0.0025000, -0.0044444) translate (-1, 1), 520 vertices, 780 indices
draw 600 indices from index 0, vertex 0, scissor x 20 to 420, y 40 to 240
```

1. **Lines 47–54:** the lists are joined one after the other into one vertex array and one index array.
2. **Lines 56–58:** the scale is 2 divided by the display size, with the sign of y flipped.
3. **Lines 67–72:** each clip rectangle is scaled to pixels, clamped to the framebuffer, and skipped when empty.
4. **Lines 76–77:** the sizes of the lists drawn so far become the offsets of the next list.

The first run prints the scale 0.00125 for x and -0.0022222 for y, which is 2 divided by 1600 and minus 2 divided by 900. The second list's command starts at index 600 and vertex 400, because the panel's lists come first in the buffers. Its clip rectangle reaches past the display, so the limits cut it at the display's edge: x 1500 to 1600 and y 800 to 900. The second command of the :term[popup]{id=popup} is empty (its left and right edges are equal) and prints nothing. On the denser display, every limit doubles, and the popup falls entirely outside the 1600 by 900 pixels, so no draw is issued for it at all.

The toy omits what makes a real backend hard. A GPU may still read the buffers of the last frame. ImGui creates textures on request. One pipeline serves each output format, and textures have colors to convert. The sections below add each in the order the data meets it.

## The real code: from the module to the shader

### The module's frame

`ImGuiModule::OnRenderUI` is the whole frame of the user interface. It runs after the scene has rendered, inside the profiler's `Editor.UI` stage. Note the order: begin, every layer's drawing, `PrepareBackBuffer`, end.

```cpp src="Strata/src/Strata/ImGui/ImGuiModule.cpp#L54-L64" symbol="ImGuiModule::OnRenderUI"
void ImGuiModule::OnRenderUI(EngineFrame& frame)
{
	ST_PROFILE_STAGE("Editor.UI");
	m_Layer->Begin();
	for (Layer* layer : frame.Layers)
		layer->OnImGuiRender();

	// The back buffer: the GPU waits for the display only from here on, after the frame's uploads and offscreen rendering.
	Renderer::PrepareBackBuffer();
	m_Layer->End(m_Graphics->GetDevice()->GetBackBufferFramebuffer());
}
```

1. **Line 56:** the whole frame is one profiler stage, so the stage's time is the UI's cost.
2. **Lines 57–59:** `Begin` starts the ImGui frame, and every layer draws its widgets between `Begin` and `End`.
3. **Line 62:** the :term[back buffer]{id=back-buffer} is requested after the layers, so earlier work does not wait for the display.
4. **Line 63:** `End` renders the draw data into the back buffer's framebuffer.

The call to `PrepareBackBuffer` comes after every layer drew, not before. It marks the point where the GPU starts to wait for the display's image. Everything the frame does before it (uploads, passes into textures, the viewport render) can run while the display is still busy. A UI that asked for the :term[back buffer]{id=back-buffer} first would stall the whole frame on the display.

### The layer's capture of events

The layer sits on top of the layer stack as an overlay, so it sees each event before the layers under it, as [windows and events](../core/windows-events.md) shows. It handles the :term[content scale]{id=content-scale} event first, without marking it handled, because the other layers may lay out differently at another scale. Then it hands the event to the platform backend, and marks mouse and keyboard events handled when ImGui wants them. Note the two `WantCapture` flags and the `|=`.

```cpp src="Strata/src/Strata/ImGui/ImGuiLayer.cpp#L88-L109" symbol="ImGuiLayer::OnEvent"
void ImGuiLayer::OnEvent(Event& event)
{
	// Not handled: other layers may lay out differently at another scale too.
	EventDispatcher dispatcher(event);
	dispatcher.Dispatch<WindowContentScaleEvent>([this](WindowContentScaleEvent& scaleEvent)
	{
		SetContentScale(m_Window ? ToUIScale(scaleEvent.GetScale(), glm::uvec2(m_Window->GetWidth(), m_Window->GetHeight()), m_Window->GetFramebufferSize())
			: scaleEvent.GetScale());
		return false;
	});

	if (!m_Initialized)
		return;
	// The overlay sees events first: ImGui's input comes from them.
	m_Platform.OnEvent(event);
	if (!m_BlockEvents)
		return;

	const ImGuiIO& io = ImGui::GetIO();
	event.Handled |= event.IsInCategory(EventCategoryMouse) && io.WantCaptureMouse;
	event.Handled |= event.IsInCategory(EventCategoryKeyboard) && io.WantCaptureKeyboard;
}
```

1. **Line 96:** the scale handler returns false, so the event stays open to the layers below.
2. **Line 102:** the platform backend sees every event before anything handles it.
3. **Lines 107–108:** an event is marked handled only when ImGui wants that device.

The result is the contract between a docked editor and a game view. While the pointer is over a panel, ImGui wants the mouse, the event is handled, and the layers below never see the click. Over the viewport, ImGui does not want it, and the game gets it. `BlockEvents(false)` turns the swallowing off, but ImGui still receives every event first.

### The platform backend

`ImGuiPlatform` queues four kinds of input into ImGui's event queue: keys, typed text, the mouse and focus. It never asks the system anything.

Keys carry the most care. The window offers `GetLayoutKey`, which gives the key as the person's layout names it: on a French keyboard the key at the English position of Q is A. A shortcut named after a letter (**Ctrl+Z**) then works on every layout. `OnKey` also queues the modifier before the key and remembers which ImGui key each press became. Look at both.

```cpp src="Strata/src/Strata/ImGui/ImGuiPlatform.cpp#L162-L184" symbol="ImGuiPlatform::OnKey"
void ImGuiPlatform::OnKey(KeyCode key, bool down)
{
	ImGuiIO& io = ImGui::GetIO();
	// The modifier first: ImGui takes a key's chord from the modifiers queued before it.
	for (size_t index = 0; index < std::size(c_Modifiers); index++)
	{
		const ModifierKeys& modifier = c_Modifiers[index];
		if (key != modifier.Left && key != modifier.Right)
			continue;
		m_ModifierKeys[index * 2 + (key == modifier.Right ? 1 : 0)] = down;
		io.AddKeyEvent(modifier.Modifier, m_ModifierKeys[index * 2] || m_ModifierKeys[index * 2 + 1]);
	}
	if (key >= c_MaxKeyCode)
		return;

	// A release is the key its press was queued as, whatever the layout says now.
	ImGuiKey imguiKey = m_PressedKeys[key];
	if (down || imguiKey == ImGuiKey_None)
		imguiKey = ToImGuiKey(m_Window->GetLayoutKey(key));
	m_PressedKeys[key] = down ? imguiKey : ImGuiKey_None;
	if (imguiKey != ImGuiKey_None)
		io.AddKeyEvent(imguiKey, down);
}
```

1. **Lines 166–173:** a modifier key updates its flag and queues the modifier before the key itself.
2. **Lines 178–180:** a release uses the stored ImGui key again, and a press asks the layout.
3. **Line 181:** the table remembers the key for a press and forgets it for a release.

:::example[A layout switch while a key is held]
A person on a French layout presses the key at the English position of Q. `GetLayoutKey` says A, so `m_PressedKeys` stores A for that key and ImGui gets "A down". The person switches to an English layout while holding the key, then lets go. Now `GetLayoutKey` would say Q, but the stored value is not `ImGuiKey_None`, so the release uses A and ImGui sees "A up". Without the table, ImGui would see "Q up" and keep A down for good.
:::

Both keys of a modifier count. `m_ModifierKeys` holds eight flags, a left and a right for each of Ctrl, Shift, Alt and Super. ImGui hears that a modifier is down while either flag is set. Releasing the left Shift while the right is held keeps Shift down.

Focus is the second trap. When the window loses focus, the system stops sending the releases of keys the person holds. The window reports the releases of keys it had down. The platform clears its own tables and tells ImGui about the loss with `AddFocusEvent(false)`, which releases every key and mouse button inside ImGui. The keys pressed again after focus returns are new presses.

Typed text arrives as `KeyTypedEvent`, one :term[code point]{id=code-point} each: the characters the layout produced, dead keys applied, and also what an input method composed. An input method is a program that builds characters of a language such as Japanese from several key presses. The editor's ImGui text fields take the composed text, and on Windows ImGui places the candidate list next to the text cursor, using the window handle that `Init` hands to the main viewport.

Game UI is different: `Input::ProcessText` receives the committed characters only. The text still being composed, and the candidate window, are not shown there, because GLFW 3.4 has no callback for them. That is one of the things Strata does not do.

The cursor is a negotiation with the game. ImGui asks for a shape every frame, such as an arrow over a button, a text bar over a field or a double arrow over the border between two panels. A game in play mode may have locked or hidden the cursor. Read `UpdateCursorShape` next.

```cpp src="Strata/src/Strata/ImGui/ImGuiPlatform.cpp#L206-L221" symbol="ImGuiPlatform::UpdateCursorShape"
void ImGuiPlatform::UpdateCursorShape()
{
	const ImGuiIO& io = ImGui::GetIO();
	if ((io.ConfigFlags & ImGuiConfigFlags_NoMouseCursorChange) || m_Window->GetCursorMode() != CursorMode::Normal)
	{
		// The cursor is not ImGui's now (a game locked or hid it): it gets ImGui's shape again once it is.
		m_AppliedCursor.reset();
		return;
	}
	// While ImGui draws the cursor itself, the system's is hidden.
	const ImGuiMouseCursor cursor = io.MouseDrawCursor ? ImGuiMouseCursor_None : ImGui::GetMouseCursor();
	if (m_AppliedCursor == cursor)
		return;
	m_Window->SetCursorShape(ToCursorShape(cursor));
	m_AppliedCursor = cursor;
}
```

1. **Line 209:** a game that locked or hid the cursor, or a program that turned shape changes off, ends the function.
2. **Line 212:** the stored shape is forgotten, so the shape is applied again when the cursor returns.
3. **Lines 217–218:** an unchanged shape costs nothing.
4. **Line 219:** the window changes the system's cursor.

When the cursor mode is not `Normal`, the function forgets what it applied and sets nothing. [Mouse and cursor](../input/mouse-cursor.md) covers the modes. When the mode returns to `Normal`, `m_AppliedCursor` is empty, so the next frame sets ImGui's shape again, even if it equals the one before. In the normal case the shape is set only when it changes, so most frames cost no call to the system.

Three small services remain. The clipboard goes through the window. Mouse buttons use the first five, and the wheel takes both axes. `NewFrame` writes the display size from the window, and the pixel density from the ratio of framebuffer to window size, which is 1 where windows are measured in pixels and 2 on a Retina display.

The :term[time step]{id=time-step} is the clock's difference to the last frame, with two guards. The first frame has no frame before it, so it uses 1/60 of a second. Two frames within the clock's resolution are at least 1 microsecond apart, because ImGui requires a positive step.

### The renderer's input: draw data

After `ImGui::Render`, ImGui hands over draw data. The rest of the page uses ImGui's three words for it. Draw data is everything to draw this frame. A draw list is the triangles of one window or one layer. A draw command is a range of one list's indices that share a clip rectangle and a texture, so one command is one GPU draw.

The memory is plain. Each vertex is 20 :term[bytes]{id=byte}: a position (two floats, 8 bytes), a texture coordinate (two floats, 8 bytes) and a color (four bytes). Indices are 16 bits. Each list has its own vertex array, its own index array and its own commands, and a command's `VtxOffset` and `IdxOffset` count from the start of its own list.

```mermaid caption="Draw data holds one list for each window. The renderer copies the lists one after the other into one vertex buffer and one index buffer, and adds the size of the lists before to each command's offsets." alt="A diagram of two draw lists. List A has 400 vertices, 600 indices and commands. List B has 120 vertices, 180 indices and commands. Both are copied one after the other into one vertex buffer of 520 vertices and one index buffer of 780 indices. Commands of list B start at vertex 400 and index 600 of the buffers."
flowchart LR
    A["List A: 400 vertices, 600 indices, commands"] --> VB["Vertex buffer: A then B, 520 x 20 bytes"]
    B["List B: 120 vertices, 180 indices, commands"] --> VB
    A --> IB["Index buffer: A then B, 780 x 2 bytes"]
    B --> IB
    VB --> O["B's commands add 400 to the vertex offset and 600 to the index offset"]
    IB --> O
```

Because the lists share a buffer, every draw adds the sizes of the lists before it: `globalVertexOffset` and `globalIndexOffset` in the real code, as in the toy. The backend sets the flag `RendererHasVtxOffset`, which tells ImGui that a command may start at a vertex offset, so a list of more than 65,535 vertices can still use 16-bit indices.

### Pixels to the screen

ImGui works in pixels, with the origin at the top-left corner and y growing down. The screen's :term[normalized device coordinates]{id=normalized-device-coordinates} (NDC), as [coordinates](../gpu/coordinates.md) explains, run from -1 to 1 with +Y up. A push constant carries the conversion to the vertex shader: four floats for the scale and the translate. The renderer writes them once and the shader does one multiply and one add for each vertex. The conversion is $x_{ndc} = x \cdot s_x + t_x$, and the same with y.

```cpp src="Strata/src/Strata/ImGui/ImGuiRenderer.cpp#L458-L462" from="PushConstants pushConstants;" to="pushConstants.Translate[1] = 1.0f + drawData->DisplayPos.y * 2.0f / drawData->DisplaySize.y;" symbol="ImGuiRenderer::Render"
PushConstants pushConstants;
pushConstants.Scale[0] = 2.0f / drawData->DisplaySize.x;
pushConstants.Scale[1] = -2.0f / drawData->DisplaySize.y;
pushConstants.Translate[0] = -1.0f - drawData->DisplayPos.x * pushConstants.Scale[0];
pushConstants.Translate[1] = 1.0f + drawData->DisplayPos.y * 2.0f / drawData->DisplaySize.y;
```

In the real code, $s_x$ is `Scale[0]`, $s_y$ is `Scale[1]`, $t_x$ is `Translate[0]` and $t_y$ is `Translate[1]`. Their units are NDC per pixel for the scales and NDC for the translations.

:::example[The push constants of a 1600 by 900 window]
`DisplaySize` is (1600, 900) and `DisplayPos` is (0, 0). Then $s_x = 2 / 1600 = 0.00125$, and $s_y = -2 / 900 = -0.0022222$. The translate is $t_x = -1 - 0 \cdot s_x = -1$ and $t_y = 1 + 0 = 1$. The four corners follow:

| Pixel | x times $s_x$ plus $t_x$ | y times $s_y$ plus $t_y$ | NDC |
| --- | --- | --- | --- |
| (0, 0) top-left | -1 | 1 | (-1, 1) |
| (1600, 0) top-right | 1 | 1 | (1, 1) |
| (0, 900) bottom-left | -1 | -1 | (-1, -1) |
| (800, 450) centre | 0 | 0 | (0, 0) |

Put the window at `DisplayPos` (100, 50) and the translate changes: $t_x = -1 - 100 \cdot 0.00125 = -1.125$ and $t_y = 1 + 50 \cdot 2 / 900 = 1.1111$. The pixel (100, 50) then maps to $(100 \cdot 0.00125 - 1.125, 50 \cdot -0.0022222 + 1.1111) = (-1, 1)$, the top-left corner again. A Retina display has 800 by 450 points and 1600 by 900 pixels. Its `DisplaySize` is (800, 450), so the scales are 0.0025 and -0.0044444. The constants follow the display's units, and `FramebufferScale` only grows the viewport and the clip limits.
:::

The vertex shader does its work in one line. The push constant block also holds a fifth value, the display mode, which only the fragment shader reads. Read `st_Main` here.

```slang src="Strata/shaders/ImGui.vert.slang#L20-L25"
void st_Main()
{
	v_TexCoord = a_TexCoord;
	v_Color = a_Color;
	st_Position = float4(a_Position * u_Push.Scale + u_Push.Translate, 0.0, 1.0);
}
```

The shader passes the texture coordinate and the color through. It writes z as 0 and w as 1, because the UI is flat.

### A clip rectangle for each command

A **clip rectangle** is the pixel rectangle that a draw command may paint inside. ImGui sets one for each command, for example to cut a long list at the edge of its panel. The renderer turns it into the GPU's scissor rectangle. The pipeline has `setScissorEnable(true)`, and the command's rectangle moves by `DisplayPos`, scales by `FramebufferScale`, and is clamped to the framebuffer.

Note the empty-rectangle test, the texture lookup, and the offsets that go into the draw.

```cpp src="Strata/src/Strata/ImGui/ImGuiRenderer.cpp#L491-L512" from="const float clipMinX" to="commandList->drawIndexed(arguments);" symbol="ImGuiRenderer::Render"
const float clipMinX = std::max((command.ClipRect.x - clipOffset.x) * clipScale.x, 0.0f);
const float clipMinY = std::max((command.ClipRect.y - clipOffset.y) * clipScale.y, 0.0f);
const float clipMaxX = std::min((command.ClipRect.z - clipOffset.x) * clipScale.x, framebufferWidth);
const float clipMaxY = std::min((command.ClipRect.w - clipOffset.y) * clipScale.y, framebufferHeight);
if (clipMaxX <= clipMinX || clipMaxY <= clipMinY)
	continue;

auto* texture = reinterpret_cast<nvrhi::ITexture*>(static_cast<uintptr_t>(command.GetTexID()));
if (!texture)
	continue;

state.bindings = { GetBindingSet(texture, renderState.NearestFiltering) };
state.viewport.scissorRects[0] = nvrhi::Rect(static_cast<int>(clipMinX), static_cast<int>(clipMaxX), static_cast<int>(clipMinY), static_cast<int>(clipMaxY));
commandList->setGraphicsState(state);
pushConstants.TextureDisplay = static_cast<uint32_t>(renderState.TextureDisplay);
commandList->setPushConstants(&pushConstants, sizeof(pushConstants));

nvrhi::DrawArguments arguments;
arguments.vertexCount = command.ElemCount;
arguments.startIndexLocation = command.IdxOffset + globalIndexOffset;
arguments.startVertexLocation = command.VtxOffset + globalVertexOffset;
commandList->drawIndexed(arguments);
```

1. **Lines 491–494:** the clip rectangle moves by the display position, scales to pixels and is clamped.
2. **Line 495:** an empty rectangle draws nothing.
3. **Line 498:** the command's `ImTextureID` is an NVRHI texture pointer.
4. **Lines 502–503:** the binding set and the scissor are chosen for this command.
5. **Lines 510–512:** the list's offset is added to the command's own, then the draw is issued.

### Pipelines and binding sets

`GetPipeline` keeps one graphics pipeline for each framebuffer format it has met, found by comparing the framebuffer's info. The blend state is straight alpha: source alpha and one minus source alpha for color. Culling, depth testing and depth writing are off.

`GetBindingSet` builds a binding set of the :term[push constants]{id=push-constants}, the texture and a sampler, and caches it in a map keyed by the texture's pointer, with the low bit marking nearest filtering. A binding set holds a reference to its texture, so a cached pointer can never name a second texture. Each `Render` begins by erasing the sets whose last use is more than `c_BindingSetRetentionFrames` (8) frames old, which also releases their textures. [Pipelines and binding](../gpu/binding.md) explains why the set holds the reference. A texture therefore stays alive for 8 frames after its last use.

### A ring of mapped buffers

The :term[central processing unit]{id=processor} (CPU) copies the draw lists into the vertex and index buffers, and the GPU reads them later. If the CPU wrote the same buffers for the next frame at once, it would change triangles the GPU has not drawn. The renderer therefore keeps a ring of buffer sets, each `Vertices` and `Indices` mapped for writing once, so a frame's lists are copied straight into GPU-visible memory with no staging copy.

The ring has three states for a set. A set is free when the GPU is done with it or never used it. It is written while the current frame's lists are copied into it. It is pending once that frame was submitted and the GPU may still read it. A set returns to free when its :term[event query]{id=fence}, a marker the GPU sets when it passes a point of the queue, says it finished (see [resources and lifetimes](../gpu/resources-lifetimes.md)).

```mermaid caption="A buffer set is free, then written while a frame copies into it, then pending until the graphics card passes the frame's marker. The ring grows when no set is free, up to eight, and waits for the oldest set after that." alt="A state diagram with three states: free, written and pending. Free goes to written when a frame copies its lists in. Written goes to pending when the next frame sets the event query. Pending returns to free when the query reports done. A note says that when every set is pending, a new set is added up to eight, and after that the oldest pending set is waited for."
stateDiagram-v2
    [*] --> Free
    Free --> Written: frame copies its lists in
    Written --> Pending: next Render sets the event query
    Pending --> Free: query reports done
    Pending --> Pending: all pending, so add a set (up to 8) or wait for the oldest
```

One detail looks odd at first. A set's event query is set at the start of the next `Render`, not at the end of this one. The layer records the commands inside `Render` and executes the command list after `Render` returns. A marker set before the execution would pass before the draws were submitted. Setting it at the next call, when the draws are surely submitted, is correct.

```cpp src="Strata/src/Strata/ImGui/ImGuiRenderer.cpp#L314-L342" symbol="ImGuiRenderer::AcquireFrameBuffers"
ImGuiRenderer::FrameBuffers* ImGuiRenderer::AcquireFrameBuffers(size_t vertexCount, size_t indexCount)
{
	// The first set the GPU is done with. While every set is in use (frames in flight), another one, up to a bound: past
	// it the GPU is that many frames behind, and waiting for its oldest frame beats taking more memory.
	FrameBuffers* acquired = nullptr;
	for (FrameBuffers& buffers : m_FrameBuffers)
	{
		if (!buffers.Pending || m_Device->pollEventQuery(buffers.Done))
		{
			acquired = &buffers;
			break;
		}
	}
	if (!acquired && m_FrameBuffers.size() < c_MaxFrameBufferSets)
	{
		FrameBuffers& added = m_FrameBuffers.emplace_back();
		added.Done = m_Device->createEventQuery();
		acquired = &added;
	}
	if (!acquired)
	{
		acquired = &*std::min_element(m_FrameBuffers.begin(), m_FrameBuffers.end(),
			[](const FrameBuffers& a, const FrameBuffers& b) { return a.LastUsedFrame < b.LastUsedFrame; });
		m_Device->waitEventQuery(acquired->Done);
	}
	acquired->Pending = false;
	acquired->LastUsedFrame = m_FrameCounter;
	return ReserveFrameBuffers(*acquired, vertexCount, indexCount) ? acquired : nullptr;
}
```

1. **Line 321:** a set is free when it is not pending or its query reports done.
2. **Line 327:** with none free, the ring grows up to its bound.
3. **Lines 333–337:** at the bound, the set used longest ago is waited for.
4. **Line 341:** the set gets room for this frame's counts.

:::example[A GPU that runs three frames behind]
Frame 0 finds no set and adds set 0. At the start of frame 1, set 0 is marked pending: its marker will pass when the GPU finishes frame 0, which is two frames away. The query is not done, so frame 1 adds set 1. At frame 2, set 1 is marked pending and the query of set 0 is still not done, so set 2 is added. At frame 3, the GPU has finished frame 0, the query of set 0 reports done and set 0 returns to free, so the ring stops at 3 sets, the lag.

A GPU twelve frames behind would reach the bound of 8 and then wait for the oldest set every frame, which keeps the memory bounded and slows the CPU to the GPU's speed.
:::

A set grows by half again when a frame needs more room, so a growing UI replaces its buffers rarely. If a buffer cannot be created, the frame draws nothing and the next frame tries again.

### Dynamic textures

ImGui 1.92 changed how the font atlas reaches the GPU. Before, a backend built the atlas at start. Now **dynamic textures** are textures that ImGui asks the backend to create, update and destroy as it needs them, with a status in each `ImTextureData`: `WantCreate`, `WantUpdates` or `WantDestroy`. The font atlas is the first user; a new glyph, a character the person has not typed before, asks for an update.

The backend sets the flag `RendererHasTextures`, and `Render` walks the texture list before it draws, passing every texture whose status is not OK to `UpdateTexture`.

```cpp src="Strata/src/Strata/ImGui/ImGuiRenderer.cpp#L216-L253" symbol="ImGuiRenderer::UpdateTexture"
void ImGuiRenderer::UpdateTexture(nvrhi::ICommandList* commandList, ImTextureData* texture)
{
	if (texture->Status == ImTextureStatus_WantDestroy)
	{
		// NVRHI keeps the texture alive for command lists that still reference it.
		DestroyTexture(texture);
		return;
	}

	if (texture->Status != ImTextureStatus_WantCreate && texture->Status != ImTextureStatus_WantUpdates)
		return;

	ST_CORE_ASSERT(texture->Format == ImTextureFormat_RGBA32, "ImGui textures are expected in RGBA32");
	auto* managed = static_cast<ManagedTexture*>(texture->BackendUserData);
	if (texture->Status == ImTextureStatus_WantCreate)
	{
		if (!managed)
		{
			managed = new ManagedTexture();
			texture->BackendUserData = managed;
		}

		nvrhi::TextureDesc desc;
		desc.width = static_cast<uint32_t>(texture->Width);
		desc.height = static_cast<uint32_t>(texture->Height);
		desc.format = nvrhi::Format::RGBA8_UNORM;
		desc.debugName = "ImGuiTexture";
		desc.initialState = nvrhi::ResourceStates::ShaderResource;
		desc.keepInitialState = true;
		managed->Texture = m_Device->createTexture(desc);
		texture->SetTexID(ToTextureID(managed->Texture));
	}

	// Updates rewrite the whole texture: atlas updates are rare (new glyphs) and NVRHI uploads whole mips.
	if (managed && managed->Texture)
		commandList->writeTexture(managed->Texture, 0, 0, texture->GetPixels(), static_cast<size_t>(texture->GetPitch()));
	texture->SetStatus(ImTextureStatus_OK);
}
```

1. **Lines 218–223:** a destroy releases the engine's side of the texture.
2. **Lines 238–246:** a create makes the texture and gives ImGui its pointer as its `ImTextureID`.
3. **Lines 250–251:** a create or an update writes all pixels.
4. **Line 252:** the status returns to OK, so the texture is not visited again.

A create makes an NVRHI texture and hands ImGui its pointer as the `ImTextureID`. An update rewrites the whole texture with `writeTexture`, though only part of it changed. The reason is in the comment: atlas updates are rare, and NVRHI uploads whole mips anyway. A destroy drops the Strata texture and tells ImGui the status is destroyed; NVRHI keeps the texture alive for command lists that still use it, as the contract says.

### The two shaders and color spaces

`ImGui.frag` multiplies the texel by the vertex color. The color of a vertex is what ImGui computed from the theme, and the texel is the atlas glyph, the image or the white pixel that plain rectangles use. All of ImGui's colors are display values: they are already in the sRGB encoding that the screen expects, and the target holds display values too. A texture the UI shows has a stored format, and that decides what must be done to it. [Color](../basics/color.md) covers linear and sRGB values; the table lists the four cases.

| Stored texture | What sampling gives | Why it looks wrong as is | Display mode |
| --- | --- | --- | --- |
| UI texture, the viewport's image | Display values | Nothing: it is right | Direct |
| sRGB texture | Linear values (sampling decodes) | Too dark: linear values on a display target | `EncodeSRGB` |
| One channel standing for gray | Red only | A red picture | `Grayscale` |
| Two-channel normal map | X in red, Y in green | A picture with no blue and no meaning | `NormalXY` |

:::example[One stored byte through the four modes]
An sRGB texture stores the byte 128, or 0.502 of full range. Sampling decodes it to linear 0.2159. With Direct, that value would go to the screen unchanged and show as 55 of 255, much darker than the stored picture. `EncodeSRGB` applies `LinearToSRGB` and gets 0.502 back, the value the author stored.

A normal map texel of (128, 128) holds X and Y of 0.502. The shader maps them to $2 \cdot 0.502 - 1 = 0.004$, rebuilds Z as the square root of $1 - x^2 - y^2$, which is 1.000, and shows $(x, y, z) \cdot 0.5 + 0.5$, which is (0.502, 0.502, 1.000): the familiar blue of a flat normal map.
:::

The code of the three conversions is `st_Main` of `ImGui.frag`. Note the three branches on `TextureDisplay`.

```slang src="Strata/shaders/ImGui.frag.slang#L26-L46"
void st_Main()
{
	float4 texel = u_Texture.Sample(u_Sampler, v_TexCoord);
	if (u_Push.TextureDisplay == c_DisplayEncodeSRGB)
	{
		// Sampling an sRGB texture decodes it; the target holds display values, as ImGui's colors are.
		texel.rgb = LinearToSRGB(texel.rgb);
	}
	else if (u_Push.TextureDisplay == c_DisplayGrayscale)
	{
		texel = float4(texel.rrr, 1.0);
	}
	else if (u_Push.TextureDisplay == c_DisplayNormalXY)
	{
		// As materials read two-channel normal maps (Forward.frag): X and Y, Z reconstructed; shown as normal maps look.
		const float2 xy = texel.rg * 2.0 - 1.0;
		const float z = sqrt(max(1.0 - dot(xy, xy), 0.0));
		texel = float4(float3(xy, z) * 0.5 + 0.5, 1.0);
	}
	o_Color = v_Color * texel;
}
```

1. **Lines 29–33:** an sRGB texture is encoded again after sampling decoded it.
2. **Lines 34–37:** a one-channel texture shows its red value in all three channels.
3. **Lines 38–44:** a two-channel normal map gets its Z back and is shown as a normal map looks.
4. **Line 45:** the vertex color multiplies the result.

The shader reads the mode from the push constant, and the CPU side sets the push constant for each draw from `renderState.TextureDisplay`. A draw callback changes that state between two draws. It does so for every following draw until another callback, or ImGui's reset callback, replaces it.

The modes are an enum. The **ImGuiTextureDisplay** is the engine's set of four ways a UI draw shows a texture: Direct, `EncodeSRGB`, `Grayscale` and `NormalXY`. `GetImGuiTextureDisplay` chooses from the texture's format: one channel with the gray flag is `Grayscale`, two channels is `NormalXY`, an sRGB format is `EncodeSRGB`, and anything else is Direct. The kit's `UI::TextureImage` calls it and adds the callback, so a widget does not decide.

The callbacks of the four modes share one function. They differ in their user data, which points at the matching entry of a table of the four values. See how `AddImGuiTextureDisplay` hands the address over.

```cpp src="Strata/src/Strata/ImGui/ImGuiRenderer.cpp#L102-L107" symbol="AddImGuiTextureDisplay"
void AddImGuiTextureDisplay(ImDrawList* drawList, ImGuiTextureDisplay display)
{
	const size_t index = std::min<size_t>(static_cast<size_t>(display), std::size(c_TextureDisplays) - 1);
	// ImGui keeps the pointer (a user data size of 0) and never writes through it.
	drawList->AddCallback(DrawCallbackSetTextureDisplay, const_cast<ImGuiTextureDisplay*>(&c_TextureDisplays[index]));
}
```

A test reads draw lists with `FindImGuiTextureDisplay`, which compares each command's data address with the table's. That is the second half of the rule: addresses of data in a table are unique and stay put, while addresses of functions may be merged.

### The GPU stage

`ImGuiLayer::End` wraps the render in a `GPUPassTimer` for the stage GPU.ImGui. The stage is registered the first time a program draws UI, through a static :term[local variable]{id=local-variable}, so a game, which has no ImGui, gets no empty column in the frame profile. The time then appears with the other stages, as [timing and readback](../gpu/readback-timing.md) shows.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| The stock GLFW and Vulkan backends | ImGui's own example programs | No backend code to write or test | The sealed window library, NVRHI lifetimes, keys by layout, 0.05 to 0.06 ms of every frame |
| Stock backend for the platform side only | Programs with a renderer backend of their own | Less input code | The same sealed-library break, and the same per-frame polling |
| Multi-viewport (ImGui windows as real windows) | Programs that let panels leave the main window | Panels that leave the main window | A second :term[swapchain]{id=swapchain} and event path, and more code each frame that the editor does not use |
| A staging copy of the vertices to GPU memory | Backends that keep UI data in GPU-only memory | Faster reads for huge UI | One more copy, and one more upload step in a frame of a few hundred thousand bytes |
| One buffer set, with a wait each frame | Programs that wait for the GPU each frame | Less memory | A stall whenever the GPU is behind |

## How it is tested

Two suites check the platform backend and the layer, and a GPU suite checks the renderer. `ImGui.Platform` feeds events into a context and reads ImGui's queue. It covers keys by layout, the macOS shortcut behavior, typed text, the mouse and the wheel. It also covers the cursor shapes, the clipboard, the loss of focus, the display, the time, and the state after the backend ends. `ImGui.Layer` checks the UI scale and the content scale event.

The renderer tests are in `GPU.Renderer`, which share one device and need a GPU. One renders UI into a texture target. One checks that frames the GPU has not drawn yet keep their own vertices, with `GetFrameBufferSetCount()` between 2 and 8. One checks that the two sampler callbacks switch filtering, and one checks the sRGB, gray and normal map displays against pixels. Run them with the commands below; the second needs a GPU.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=ImGui.*
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.Renderer --test-case="ImGui*"
```

The first command runs both suites of the backends, and the second runs only the renderer tests that draw ImGui. Each ends with the summary line of doctest, which counts the test cases that passed.

## Changing it safely

The rules above are the first check. Four more follow from the code above.

- A new key needs `ToImGuiKey` to know it, and a test in `ImGui.Platform`. Keep the order: modifier before key, release as press.
- A new display mode needs an entry in the table of four values, a branch in `ImGui.frag`, a line in the guide and a test pixel. Compare data addresses, never functions.
- A new draw callback that changes render state goes through `ImGuiRenderState`, which exists only while `Render` runs.
- Do not wait for the GPU in the frame, except in the ring's bound of 8: a new wait is a stall of every frame in the editor.

After a change, run the two suites above and the GPU test. A missing shader appears as a failed `Init`: the layer then disables ImGui and logs the failure, and the program does not run.

## Summary

- A frame goes from a window event through `ImGuiLayer::OnEvent` and `ImGuiPlatform::OnEvent` into ImGui, then from `ImGuiModule::OnRenderUI` through `Begin`, the layers' drawing and `End` into `ImGuiRenderer::Render`.
- A release repeats the ImGui key its press became, and modifiers go before keys, so a layout switch or a chord never leaves ImGui with a stuck key.
- The vertex shader maps pixels to the screen with scale 2 / width and -2 / height and translate -1 and 1, shifted by the display position. Each command's clip rectangle becomes a scissor in framebuffer pixels.
- A ring of at most 8 mapped buffer sets holds the lists; a set returns when its event query is done, and the ring waits for its oldest set only at the bound.
- A format chooses a display mode, one of four, and a draw callback sets it; commands are told apart by the address of their data, because identical functions may be merged.

## Check yourself

1. A window is 1280 by 720 pixels with `DisplayPos` (0, 0) and a pixel density of 1. What are the four push constant values, and what is the NDC of the pixel (320, 180)?

   :::answer{tests="push-constants"}
   The scale is (2 / 1280, -2 / 720) = (0.0015625, -0.0027778) and the translate is (-1, 1). The pixel (320, 180) gives $(320 \cdot 0.0015625 - 1, 180 \cdot -0.0027778 + 1) = (-0.5, 0.5)$, which is the middle of the upper-left quarter.
   :::

2. A person holds the key at the English position of Q on a French layout, then switches to an English layout and releases it. What does ImGui receive?
   - A. "Q up", because the layout now says Q.
   - B. "A up", because the release uses the ImGui key the press was stored as.
   - C. Nothing, because the layout change cancels the press.

   :::answer{tests="key-queue"}
   B. The press was queued as A and stored in `m_PressedKeys`, and the release reads it. A would leave A held in ImGui; C is wrong because no event is lost: a layout change is not a focus loss.
   :::

3. The GPU runs four frames behind the CPU. After many frames, how many buffer sets does the renderer hold, and what would change at a lag of 12?
   - A. 1 in both cases.
   - B. 4, then 8 with waits for the oldest set.
   - C. 4, then 12.

   :::answer{tests="buffer-ring"}
   B. The ring grows to the lag, so 4, and stops at `c_MaxFrameBufferSets`, which is 8. A is the case of a lag of 1, and C ignores the bound; past it the renderer waits for the oldest frame instead of taking more memory.
   :::

4. A map editor shows a one-channel height map with `ImGui::Image` and no callback. What does the person see, and which mode does `GetImGuiTextureDisplay` choose for a one-channel texture with the gray flag?

   :::answer{tests="display-modes"}
   Without a callback the mode is `Direct`, so the texture shows its red channel in red, a red picture and not a gray one. The function returns `Grayscale`, which writes (r, r, r, 1). A one-channel texture without the flag still has one channel and is not two-channel, so it is `Direct`.
   :::

5. A teammate compares each command's callback pointer with the address of `DrawCallbackSetTextureDisplay` to find display commands. Why does it work in a Debug build and fail in a Release build?

   :::answer{tests="display-modes"}
   The four modes are the same function with different data. A linker may fold identical functions into one address, and :term[optimized]{id=optimization} builds do it, so a comparison by function can match other callbacks that have the same code. The data address of the table entry is unique for each mode, and `FindImGuiTextureDisplay` uses it.
   :::

6. A key press arrives while a text field of the editor has focus. Name, in order, the functions that turn it into an ImGui key event, and say what happens to the event afterwards.

   :::answer{tests="frame-trace,key-queue"}
   The window's event reaches `ImGuiLayer::OnEvent`, the overlay on top of the layer stack. It calls `ImGuiPlatform::OnEvent`, which calls `OnKey`, which calls `AddKeyEvent` with the modifier first and then the key. ImGui reads its queue at the next `NewFrame`, called from `ImGuiLayer::Begin`. Because the text field makes ImGui want the keyboard, the layer marks the event handled, and no layer below sees it.
   :::

## Exercises

1. **Basic.** Compute the push constants for a window of 1280 by 720 points on a display of pixel density 2, which has 2560 by 1440 pixels. Then compute the scissor rectangle in pixels for the clip rectangle (100, 50, 300, 250).

   :::answer[Worked solution]{tests="push-constants"}
   The constants follow `DisplaySize`, which is in points: the scale is (2 / 1280, -2 / 720) = (0.0015625, -0.0027778) and the translate is (-1, 1). The scissor uses `FramebufferScale` 2: x from 200 to 600 and y from 100 to 500, then clamped to 2560 by 1440, which changes nothing here.
   :::

2. **Medium.** Run the ring sketch below. Predict the counts for lags of 1, 2, 3 and 12 before you read the output, then change the bound to 4 and predict again.

   :::answer[Worked solution]{tests="buffer-ring" solution="sketches/editor-ui-imgui-backends-ring.cpp"}
   The ring reaches as many sets as the lag, up to the bound. The first three lags give 1, 2 and 3 sets with no waits. A lag of 12 reaches the bound of 8 and waits every frame after it fills. With a bound of 4, a lag of 3 still holds 3 sets, and a lag of 12 holds 4 and waits sooner.

   ```cpp sketch="editor-ui-imgui-backends-ring.cpp"
   #include <algorithm>
   #include <cstdio>
   #include <vector>

   // The ring of buffer sets: a set is reused once the GPU finished the frame that drew from it.
   struct BufferSet
   {
   	int DoneFrame = -1; // The frame at whose start the GPU is done with the set (-1: not pending)
   	int LastUsed = 0;
   };

   static const size_t c_MaxSets = 8;

   static void Run(int lag, int frameCount)
   {
   	std::vector<BufferSet> sets;
   	int previous = -1; // The set the previous frame drew from
   	int waits = 0;
   	for (int frame = 0; frame < frameCount; frame++)
   	{
   		// The previous frame was submitted since: the GPU finishes it `lag` frames later.
   		if (previous >= 0)
   			sets[static_cast<size_t>(previous)].DoneFrame = frame - 1 + lag;

   		int acquired = -1;
   		for (size_t index = 0; index < sets.size() && acquired < 0; index++)
   		{
   			if (sets[index].DoneFrame < 0 || sets[index].DoneFrame <= frame)
   				acquired = static_cast<int>(index);
   		}
   		if (acquired < 0 && sets.size() < c_MaxSets)
   		{
   			sets.emplace_back();
   			acquired = static_cast<int>(sets.size()) - 1;
   		}
   		if (acquired < 0)
   		{
   			auto oldest = std::min_element(sets.begin(), sets.end(), [](const BufferSet& a, const BufferSet& b) { return a.LastUsed < b.LastUsed; });
   			acquired = static_cast<int>(oldest - sets.begin());
   			waits++;
   		}
   		sets[static_cast<size_t>(acquired)].DoneFrame = -1;
   		sets[static_cast<size_t>(acquired)].LastUsed = frame;
   		previous = acquired;
   	}
   	std::printf("GPU %d frames behind: %zu sets, %d waits in %d frames\n", lag, sets.size(), waits, frameCount);
   }

   int main()
   {
   	for (int lag : { 1, 2, 3, 12 })
   		Run(lag, 40);
   	return 0;
   }
   ```

   ```text output-of="editor-ui-imgui-backends-ring.cpp"
   GPU 1 frames behind: 1 sets, 0 waits in 40 frames
   GPU 2 frames behind: 2 sets, 0 waits in 40 frames
   GPU 3 frames behind: 3 sets, 0 waits in 40 frames
   GPU 12 frames behind: 8 sets, 32 waits in 40 frames
   ```

   1. **Line 19:** the loop is the frame counter; each pass is one call of `Render`.
   2. **Lines 22–23:** the previous frame's set gets the frame at which the GPU is done with it.
   3. **Lines 25–30:** the first free or finished set is taken.
   4. **Lines 31–35:** a new set is added while the ring is below the bound.
   5. **Lines 36–41:** at the bound, the oldest set is taken and a wait is counted.
   :::

3. **Hard.** Trace it yourself: find where a key press becomes an ImGui key event, and where the pixels of that frame are drawn. Use a debugger or a search.

   :::answer[Worked solution]{tests="frame-trace"}
   Search for `AddKeyEvent`: it is called in `ImGuiPlatform::OnKey` in `Strata/src/Strata/ImGui/ImGuiPlatform.cpp`, which `ImGuiPlatform::OnEvent` calls for `KeyPressed` and `KeyReleased`, which `ImGuiLayer::OnEvent` in `ImGuiLayer.cpp` calls first. For the pixels, break in `ImGuiModule::OnRenderUI` (`ImGuiModule.cpp`), then `EditorLayer::OnImGuiRender` where the widgets are called, then `ImGuiRenderer::Render` through `ImGuiLayer::End`. The draw call is `commandList->drawIndexed`, after the push constants and the scissor are set.
   :::

## Where it lives in Strata

- `Strata/src/Strata/ImGui/ImGuiModule.h` and `.cpp`: the engine module and the frame.
- `Strata/src/Strata/ImGui/ImGuiLayer.h` and `.cpp`: the context, the events, `Begin`, `End` and the GPU.ImGui stage.
- `Strata/src/Strata/ImGui/ImGuiPlatform.h` and `.cpp`: keys, text, mouse, focus, cursor, clipboard, time.
- `Strata/src/Strata/ImGui/ImGuiRenderer.h` and `.cpp`: draw data, pipelines, binding sets, the ring, dynamic textures, display modes.
- `Strata/shaders/ImGui.vert.slang` and `Strata/shaders/ImGui.frag.slang`: the two shaders.
- `Strata/vendor/CMakeLists.txt`: the build of ImGui's core without backends.
- Tests: `ImGui.Platform`, `ImGui.Layer`, `GPU.Renderer`.

## Further reading

- Dear ImGui, the file `docs/BACKENDS.md` and the sources `imgui_impl_glfw.cpp` and `imgui_impl_vulkan.cpp` in its repository: what a backend must do, and the stock pair that Strata replaced (intermediate).
- Dear ImGui, the 1.92 release notes on dynamic fonts and the texture protocol (intermediate).
- NVRHI, the README and the header of its device interface: the calls the renderer backend makes (advanced).
