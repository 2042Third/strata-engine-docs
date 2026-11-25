# Brief: `core/windows-events`

| Field | Value |
| --- | --- |
| Title | Windows, events and layers |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/frame-loop` |
| From | foundation "Windows, events and layers" (§1.4; `Layer` and `LayerStack` of §1.2) |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/windows-events` — Windows, events and layers

**Covers.** The job: how what happens to a window reaches the engine as events, how the polled input state is filled
first, and how a program is cut into layers. The problem in a short section: events against polling (callbacks from the
window system, an object per happening, dispatch by type, a flag that stops it; polling for keys held down), and stacked
layers with overlays (updates from the bottom up, events from the top down). The map is the path of an event. The
contract: the `Window` interface and `WindowSpecification` (events, the framebuffer's size, the content scale taught
from zero as its home: the OS's factor of display density, 2 on a Retina display, whose window of 1600 by 900 points has
3200 by 1800 pixels, one value for both axes, which the window reports and raises an event for; vsync; the Windowed,
Fullscreen and Borderless modes and what each does: Fullscreen switches the display to the resolution asked for,
Borderless covers the display at the desktop's mode, Windowed restores the last windowed place and size, and a window
made with `WindowSpecification::Fullscreen` starts Borderless; the resolution, which sets the framebuffer in Windowed
and the display mode in Fullscreen; the cursor's shape, the clipboard, layout keys, the icon, and the Vulkan
presentation it hands the device); the GLFW backend (GLFW started with the first window, with the engine's Vulkan
loader; each callback feeds `Input::Process*` first and then makes an event; `ProcessEvents` is `glfwPollEvents`, so
events run inside it, at once, never queued); the backend without a window (`STRATA_WITH_GLFW` off: `Window::Create`
returns null with an error) and a window handed in (`WindowFactory`, `Tests::StubWindow`); the event classes (15 types,
the categories as bit flags in a plain enum that avoids X11's `None`, the macros, `Handled`); `EventDispatcher`;
propagation (the application's own bookkeeping, the modules in their order, the layers from the top down with overlays
first, stopping at `Handled`; a window close that nobody handles ends the loop, so a layer can veto it, as the editor
does to ask about unsaved changes); `Layer` and `LayerStack` (one insert index between layers and overlays; the stack
owns the raw `Layer*` it is given and deletes them from the top down). The toy is an event type, a dispatcher and a
stack of two layers in 40 lines; the real code is `Event.h`, the GLFW callbacks of the window's size and close (the key
callback is named and linked to `input/devices-state`, which quotes it), `Application::OnEvent` and `LayerStack.cpp`.
The page's example: a key press followed from GLFW to the editor's layer, and a window close that the editor's layer
vetoes. The exercises: who sees an event first, predicted; a close followed from GLFW's callback to the veto; a test
layer fed by `Tests::StubWindow`. At the end the reader can add an event type or a layer and predict who sees an event
first.

**Leaves out.**

- Input devices, key states and edges → `input/devices-state`
- How input reaches a game: events, polling and intents → `input/how-input-works`
- The cursor and the game view's mouse → `input/mouse-cursor`
- The swapchain and presentation → `gpu/vulkan-nvrhi`
- ImGui's overlay and its backends → `editor-ui/imgui-backends`
- The editor's layer and its unsaved-changes question → `editor-ui/shell`
- The module hooks other than `OnEvent` → `core/engine-modules`

**Fit.** `fits`: about 4,950 words against L (5,000). The window's contract, now with the modes and content scale taught
from zero, and the path of an event with four quotes take the most; the key callback's quote left for
`input/devices-state` (about 120 fewer), and the three exercises take about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:239` | concept | home | Events against polling: callbacks, an event hierarchy, dispatch by type, `Handled`; Strata's events run at once, beside the polled `Input` that the window fills first; the mistakes (game input through events, events thought to be queued) |
| `foundation:245` | concept | home | Layers and overlays: updates from the bottom up, events from the top down; the editor and the runtime each push one layer, ImGui's module an overlay; the stack deletes the raw pointers it was given |
| `foundation:77` | feature | home | The event classes |
| `foundation:78` | feature | home | `EventDispatcher` |
| `foundation:79` | feature | home | Event propagation and the close veto |
| `foundation:80` | feature | home | The `Window` interface and `WindowSpecification`, with the modes' contract (about 120 words): Fullscreen switches the display to the resolution asked for, Borderless covers the display at the desktop's mode without a switch, Windowed restores the last windowed place and size; a window made with `WindowSpecification::Fullscreen` starts Borderless, so a game whose manifest says `Fullscreen` starts borderless; `SetResolution` sets the framebuffer in Windowed and the display mode in Fullscreen (`Strata/src/Strata/Core/Window.h:45-51`, `:93-99`); `make/menus` uses one sentence of it |
| `foundation:81` | feature | home | The GLFW backend, with how it carries out the modes: the Borderless start of a Fullscreen specification and the switches between modes (`Strata/src/Platform/GLFW/GLFWWindow.cpp:180-188`, `:466-513`) |
| `gameui:624` | term | home | Content scale (DPI scale): the display's density as a factor, 2 on a Retina display (`Docs/Architecture.md:543`); taught from zero in the window's contract (`GetContentScale`, one value for both axes, the larger, and `WindowContentScaleEvent`: `Strata/src/Strata/Core/Window.h:86-87`, `Strata/src/Platform/GLFW/GLFWWindow.cpp:277-283`), passed by `ui` (R31, D33); `ui/layout` says it in one sentence and links |
| `editor-ui:721` | term | home | Content scale, the OS's factor for display density: one entry with `gameui:624`, passed by `editor-ui` (R31, D33); `editor-ui/ui-scale` uses it with a link |
| `foundation:82` | feature | home | The backend without a window |
| `foundation:83` | feature | home | `WindowFactory` and `Tests::StubWindow` |
| `foundation:53` | feature | home | `Layer` and `LayerStack` |
| `audio-input:187` | feature | home | The event classes of `Strata/src/Strata/Events/` that the GLFW callbacks emit beside the polled state, the same classes as `foundation:77`; `input/how-input-works` uses them to set events against polling |
| `foundation:350` | code | home | `Strata/src/Strata/Events/Event.h:15-81`: types without RTTI, categories as bit flags, the templated dispatcher |
| `foundation:352` | code | home | `Strata/src/Platform/GLFW/GLFWWindow.cpp:230-249`: C callbacks with a user pointer turned into engine events (the window's size and close); the key callback, which feeds the polled `Input` before its event (286-319), is named and linked to `input/devices-state`, which quotes it (the merge "GLFW key callback", about 120 words fewer) |
| `audio-input:379` | code | link | The key callback, `GLFWWindow.cpp:286-319`, named where the polled `Input` is fed first; its excerpt is `input/devices-state`'s |
| `foundation:347` | code | home | `Strata/src/Strata/Core/Application.cpp:202-224`: propagation with `Handled`, and the close veto |
| `foundation:351` | code | home | `Strata/src/Strata/Core/LayerStack.cpp:7-54`: layers and overlays with one insert index; detaching from the top down |
| `foundation:404` | figure | home | The path of an event from the window's callback to the layers, with the veto's branch |
| `foundation:560` | term | home | Overlay |
| `foundation:584` | term | home | Event |
| `foundation:585` | term | home | Dispatcher |
| `foundation:586` | term | home | Handled flag |
| `foundation:620` | term | home | GLFW |
| `foundation:621` | term | home | Window backend |
| `foundation:710` | open | home | The page does not say where the design of `Layer`, `LayerStack`, `Event` and `ST_BIND_EVENT_FN` came from: no document of the engine says so, and `AGENTS.md` names "Hazel conventions" for the code style only |
| `foundation:84` | feature | use | `VulkanLoader` and `VulkanPresentation`, as what `GetVulkanPresentation` hands the device; their home is `gpu/vulkan-nvrhi` |
| `foundation:587` | term | link | Polling input, whose entry is `input/how-input-works`' |
| `new:25` | hands-on | home | Exercises: Basic, predict who sees a key press first, the editor's layer or ImGui's overlay, and where it stops when one sets `Handled`; Medium, trace it yourself: a window close from GLFW's close callback through `Application::OnEvent` to the editor's veto, with breakpoints; Hard, done on the source build: a test layer that counts resize and content-scale events, fed by `Tests::StubWindow` through `WindowFactory`. Evidence: `Strata/src/Strata/Core/Application.cpp:202-224`; `Strata/src/Platform/GLFW/GLFWWindow.cpp:243-249`; `StrataTests/src/StubWindow.h:20-37`; `StrataTests/src/Core/WindowBackendTests.cpp:64-74` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame loop and its Input stage | `core/frame-loop` | must |
| Virtual functions, inheritance and interfaces | `basics/cpp-classes` | must |
| Templates and lambdas | `basics/cpp-generic` | must |
| Bit flags and masks | `basics/numbers` | must |
| Raw pointers and who deletes them | `basics/cpp-memory` | must |
| Macros | `basics/cpp-modern` | must |
| C callbacks: function pointers and a user pointer | `basics/cpp-generic` | helps |
| How input reaches a game | `input/how-input-works` | helps |
| X11's `None` and the rule that keeps platform headers in their folders | `core/platform` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `content-scale` | Content scale | DPI |
| `dispatcher` | Dispatcher | - |
| `dpi-scale` | DPI scale | - |
| `event` | Event | - |
| `glfw` | GLFW | - |
| `handled-flag` | Handled flag | - |
| `overlay-core` | Overlay (core) | - |
| `window-backend` | Window backend | - |
