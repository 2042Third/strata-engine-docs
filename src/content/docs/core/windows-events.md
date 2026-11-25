---
id: core/windows-events
title: "Windows, events and layers"
description: "How what happens to a window reaches Strata as events, how the polled input is filled first, and how layers and overlays decide who sees an event."
kind: internals
size: L
tracks: [E]
needs: [core/frame-loop]
time: 95
learn:
  - id: event-path
    text: trace a key press or a window close from the window system's callback to the layer that handles it
  - id: layer-order
    text: predict which layer or overlay sees an event first, and where Handled stops it
  - id: close-veto
    text: explain how a layer vetoes a window close, and what ends the loop when none does
  - id: window-modes
    text: explain what `Windowed`, `Fullscreen` and `Borderless` do, and which of them a game starts in
  - id: content-scale
    text: compute a window's framebuffer size and a panel's size in pixels from the content scale
since: 0.3.0
status: final
---

A window belongs to the :term[operating system]{id=operating-system}, not to your program. When the player presses a key, drags a border or clicks the close button, the system knows first, and the program must learn about it. This page follows that news from the window system into Strata. It then follows the news through the layers that react to it: the parts into which a program is cut, such as the editor's interface or a game.

The page covers the `Window` interface, the code behind it that talks to the window system, the event classes and the dispatcher that picks a handler. It covers the layer stack that decides who sees an event first. It also shows how the state of the keys is filled before an event is made.

The page does not teach what that state holds or how a game reads it ([input devices and their state](../input/devices-state.md), [how input reaches a game](../input/how-input-works.md)). Images reach the window through the graphics device ([Vulkan and NVRHI](../gpu/vulkan-nvrhi.md)). The editor's own layer and its question about changes not yet saved belong to [the editor's shell](../editor-ui/shell.md). The hooks of an engine module other than `OnEvent` belong to [Engine modules](engine-modules.md).

This page needs no project and no download. Its sketches are whole programs for the compiler of [How a C++ program is built](../basics/build.md#open-a-terminal-that-finds-a-compiler). Its test commands and its traces need the source build of [your first engine change](first-change.md#build-the-engine-and-start-the-editor), in `Debug`.

## The problem and how engines solve it

A program cannot watch the window by itself. The window system owns the window, and the program asks it for news. The news comes in two ways, and Strata uses both.

The first way reads a state. The program asks, whenever it likes, whether the **W** key is down right now and where the mouse is. This suits what a game does in every frame, such as moving a character while a key is held. It cannot tell the program that a key went down and up between two readings. It has nothing to say about a happening that is no state, such as a request to close the window.

The second way is the event. An **event** is an object that describes one thing that happened, such as a key press, a new window size or a close request, and that the engine hands to the program at once. The window system reports each happening by calling a function the program gave it earlier, a :term[callback]{id=callback}. Strata turns each call into an object of a class that names the happening. A key press becomes a `KeyPressedEvent`, a new size a `WindowResizeEvent`, and all of them share one :term[base class]{id=base-class}, `Event`.

Code that receives an `Event` must learn which class it holds. A **dispatcher** is code that calls the handler that matches an event's type, and ignores the event when no handler matches.

Many parts of a program want the same event, and the first to use it should be able to say so. The **Handled flag** is the mark on an event that tells the others to stop: once it is set, the engine hands the event to nobody else. Typing `W` into a text box must not also move the camera, and the flag is how the text box says so.

Many engines put events into a queue and let the program read the queue when it is ready. Strata does not. An event is handled inside the call that asked the window system for news, and the object lives on that call's stack. Two facts follow. No event is late by even one frame, and no code may keep a reference to an event after its handler returns, because the object is gone.

Two mistakes come from mixing up the two ways. The first is to move a character through key events. A key event comes once at the press, and after a pause the keyboard repeats it at its own rate, so the character would jump, wait and creep. Read the state of the key in every frame instead.

The second mistake is to think that events wait in a queue: a handler that expects to run "later" runs at once, in the middle of the Input stage of the frame. Strata fills the polled state before it makes the event, so a handler that reads the state of the key finds the press already there.

### Layers

A program has several parts that all want the same events: the editor's interface, a game, the interface library. One function with a case for each part is hard to change. Engines cut the program into **layers**, objects with the same few functions (attach, detach, update, event), and keep them in a stack. A layer does not know the others, and the stack decides the order.

Strata's order has two rules. Updates run from the bottom of the stack to the top, so the layer at the bottom has done its work when the one above it starts. Events run from the top down, so the layer drawn on top, which the player sees and clicks, gets a click before the one beneath it. Think of papers on a desk: the top one hides the others, and a pen goes to the top one first.

An **overlay** is a layer kept above all ordinary layers, so it gets events first. The editor program pushes one ordinary layer, its interface. The game :term[runtime]{id=runtime} pushes one, the game. The module that draws the interface library, ImGui, pushes an overlay. The cost of a stack is that the order is global: a layer cannot say "after that layer but before this one", and a layer that handles too much starves those below it.

## The path of an event

The diagram follows one event from the window system to the layers. Everything in it runs on the :term[main thread]{id=main-thread}, as one chain of calls inside `ProcessEvents`.

```mermaid caption="The path of an event: the callback feeds the polled state first, then makes the event, and the application hands it to modules and layers until one handles it." alt="A flow chart from top to bottom. The window system leads to a callback, which updates the polled input state and then makes an event. The application does its first step, then asks the modules and the layers, from the top down, until one handles the event. A close request that nobody handled ends the loop."
flowchart TD
	os["Window system"] --> poll["GLFWWindow::ProcessEvents calls glfwPollEvents"]
	poll --> callback["A GLFW callback in GLFWWindow.cpp"]
	callback --> state["Input::Process* fills the polled state"]
	state --> make["The callback makes an event object"]
	make --> app["Application::OnEvent"]
	app --> own["First step: a change of size sets m_Minimized"]
	own --> modules["Modules' OnEvent, in start order"]
	modules --> layers["Layers' OnEvent, top down, overlays first"]
	layers --> handled{"Handled?"}
	handled -- "yes" --> stop["Stop: nobody else sees it"]
	handled -- "no" --> next["Ask the next layer"]
	next --> layers
	layers --> last["After the last layer: a WindowClose still not handled sets m_Running to false"]
```

Four parts own the pieces:

- The window backend owns the system's window and the callbacks.
- `Application` owns the window, the modules and the layer stack, and it receives every event.
- The stack owns its layers.
- The `Input` class owns the polled state and has no idea that events exist.

The next section states what each may assume of the others.

## The contract

### The window

The `Window` interface (`Strata/src/Strata/Core/Window.h`) is the engine's whole view of a window. Code above the platform never names GLFW; it holds a `Window` and calls its functions. A **window backend** is a class that implements `Window` for one window system. Strata has two: the GLFW backend and one that makes no window.

`ProcessEvents` asks the window system for news. Each happening reaches the function set with `SetEventCallback` as an event, and the state of the keys and the mouse in `Input` has changed by then. A window also reports sizes. `GetWidth` and `GetHeight` give the window's size in screen coordinates, the unit the window system uses.

The **framebuffer** is the image that the :term[graphics card]{id=gpu} draws the window into, and `GetFramebufferSize` gives its size in pixels. The two sizes differ on some displays, and the next part explains why.

#### Content scale

A pixel is a different size on every display. A 24 inch monitor with 1920 by 1080 pixels and a 13 inch laptop screen with 2880 by 1800 pixels differ by a factor of nearly three in pixels per inch. Text 14 pixels high can be read on the first and is tiny on the second. The operating system measures the density and offers a number for it.

The **content scale** is the operating system's factor for the density of a display: how many times larger than at the platform's default density the contents of a window should be. A value of 1 is the default, 1.5 is the Windows setting of 150 %, and 2 is a Retina display, Apple's name for a display of twice the usual density.

The **DPI scale** is another name for the content scale, taken from dots per inch (DPI), the unit in which density is measured.

Window sizes are measured in one of two units. On macOS and Wayland they are points, a unit that is one pixel at scale 1 and grows with the scale. A window of 1600 by 900 points on a Retina display has 3200 by 1800 pixels. On Windows and X11 they are pixels, and the window and the framebuffer have the same size even at a scale of 1.5. Code that needs pixels reads the framebuffer, and code that lays out an interface reads the content scale and the two sizes.

:::example[A Retina window and a panel]
The window has 1600 by 900 points, and the content scale is 2. The framebuffer is 1600 × 2 = 3200 pixels wide and 900 × 2 = 1800 high. It holds 3200 × 1800 = 5,760,000 pixels, four times the 1,440,000 of a window at scale 1. A panel that is 400 points wide covers 400 × 2 = 800 pixels.

Drag the window to a display of scale 1, and the same 1600 by 900 points become 1600 by 900 pixels. At the limit of scale 1 the two sizes agree, and the formula is not needed.
:::

`GetContentScale` returns one number for both axes: the larger of the two the window system reports. When the window moves to another display or the setting changes, the callback raises a `WindowContentScaleEvent` with the new value, and `GetScale` reads it. The interface layer changes its style on that event and does not mark it handled, because other layers may lay out differently at the new scale too.

`WindowSpecification` decides what its `Width` and `Height` mean. By default they are screen coordinates scaled by the monitor's content scale, so a window takes the same share of every display. With `SizeInPixels` set they are framebuffer pixels, whatever the display, but only for a windowed window. Tools that compare screenshots across machines use the second form.

#### Modes and resolution

A window has one of three modes, set with `SetMode` and read with `GetMode`.

| Mode | What it covers | Display mode switch | What `SetResolution` does |
| --- | --- | --- | --- |
| `Windowed` | A framed window | None | Sets the framebuffer size |
| `Fullscreen` | The whole display | Yes, to the resolution asked for | Sets the display mode |
| `Borderless` | The whole display | No: the desktop's own mode stays | Is kept for a later switch |

Returning to `Windowed` restores the last windowed place and size. A window made with `WindowSpecification::Fullscreen` set starts in `Borderless`, at the desktop's resolution. A game whose manifest says Fullscreen therefore starts in `Borderless`.

`SetResolution` ignores a zero size. A resolution given while the window is `Borderless` is remembered, and the window takes it when it becomes `Fullscreen` or `Windowed`.

#### The rest of the interface

The window stores the wish for :term[vsync]{id=vsync} (`SetVSync`, `IsVSync`; the specification's `VSync` is true by default). The graphics module reads the wish and tells the graphics device, so the window does not touch the swapchain. `SetCursorShape` takes one of ten shapes, from `Arrow` to `Hidden`, and costs a call into the system when the shape changes: set it when it changes, not in every frame. `GetClipboardText` and `SetClipboardText` move UTF-8 text to and from the system's clipboard.

A key code names the place of a key, after the layout of an American keyboard. A shortcut such as **Ctrl+Z** names what the key types, so `GetLayoutKey` turns the place into the key of the layout in use. `SetIcon` takes images of several sizes, and the specification's `IconPath` names one PNG file. `GetPlatformHandle` gives the system's own handle (the `HWND` on Windows) for text input services.

`GetVulkanPresentation` hands the graphics device what it needs to draw into the window: a `VulkanPresentation`. Its three functions name the instance extensions the window system needs, tell whether a queue family can present to it, and create a surface. A window that cannot present, such as a test's stand-in, returns null, and a device made for it draws into an image that is not shown. The :term[renderer]{id=renderer} therefore never includes GLFW. [Vulkan and NVRHI](../gpu/vulkan-nvrhi.md) teaches what the device does with it.

:::rule[Platform headers stay in their folders]
The engine's rules keep GLFW, Vulkan and the operating system's headers in `Platform/` folders, and the `Window` interface is why the rest of the engine can obey. A header such as X11's defines `None` as a :term[macro]{id=macro}, so the engine never includes it outside the platform code, and its own plain enum `EventCategory` has no `None` value, only `EventCategoryNone`. [Platform seams](platform.md) explains both rules.
:::

#### Opening a window, or not

`Window::Create` opens a window of the platform's window system and returns null, with the reason in the log, when it cannot. `Application` then reports a fatal error and the program ends with :term[exit code]{id=exit-code} 1. The specification's `WindowFactory`, when set, replaces `Window::Create`: a program that hosts the engine gives its own window, and tests give a stand-in, `Tests::StubWindow`. A program started with `Headless` opens no window at all. A build with the :term[CMake]{id=cmake} option `STRATA_WITH_GLFW` off has a second backend that is no window: its `Window::Create` logs an error that says to run headless, and returns null.

### Events and the dispatcher

Strata has 15 event types. The table groups them with the categories each class carries.

| Classes | Types | Categories |
| --- | --- | --- |
| Window | `WindowClose`, `WindowResize`, `WindowFocus`, `WindowLostFocus`, `WindowMoved`, `WindowFileDrop`, `WindowContentScale` | Application |
| Keyboard | `KeyPressed`, `KeyReleased`, `KeyTyped` | Keyboard, Input |
| Mouse | `MouseMoved`, `MouseScrolled`, `MouseLeave` | Mouse, Input |
| Mouse buttons | `MouseButtonPressed`, `MouseButtonReleased` | Mouse, Input, `MouseButton` |

A category is a group an event belongs to, and an event can belong to several, so the categories are bit flags: each has one bit, and an event's flags are the sum. `EventCategoryApplication` is bit 0 (value 1), Input is 2, Keyboard 4, Mouse 8 and `MouseButton` 16.

A mouse button event carries 8 + 2 + 16 = 26. The operator `&` keeps the bits that both numbers have, so `26 & 8` is 8 and `IsInCategory(EventCategoryMouse)` is true. The same test with Keyboard gives `26 & 4 = 0`, which is false. A key event carries 4 + 2 = 6.

Each class names itself with two macros. `ST_EVENT_CLASS_TYPE` writes the type, its name and a static `GetStaticType`, and `ST_EVENT_CLASS_CATEGORY` writes the flags. `EventDispatcher` compares the event's type with the `GetStaticType` of the class the caller names. On a match it casts the event to that class, calls the handler and combines the handler's result into `Handled` with `|=`, which keeps a mark that was already set. A handler returns true to say that it used the event.

### Propagation

`Application::OnEvent` is the one function the window's callback calls. It applies these rules in order:

1. The application does its own work first. A change of size sets its minimized flag to true when the width or the height is zero, and to false otherwise. The step never sets `Handled`.
2. Each started module gets `OnEvent`, in its start order, which follows the dependencies between modules. A module that sets `Handled` stops the walk.
3. The layers get `OnEvent` from the top down, overlays first. A layer that sets `Handled` stops it.
4. A `WindowClose` that nobody handled sets the running flag to false. The frame that received it still runs to its end.

The last rule makes the close a request. A layer may refuse it, to ask the player a question first, and the application keeps running. The refusal is the layer's alone, and it must find another way to close the program later.

### Layers and the stack

`Layer` is a base class with a name for debugging and five functions that do nothing until a layer overrides them: `OnAttach`, `OnDetach`, `OnUpdate`, `OnImGuiRender` and `OnEvent`. `LayerStack` is a vector of raw `Layer*` and one number, the insert index.

`PushLayer` inserts at that index and moves it up by one, so layers keep the order they were pushed in, below every overlay. `PushOverlay` appends at the end. `Application::PushLayer` and `PushOverlay` call `OnAttach` after the insert. The ImGui module draws its interface by calling `OnImGuiRender` on every layer in the stack.

The stack owns what it was given: a layer is made with `new`, pushed once, and deleted by the stack. `PopLayer` and `PopOverlay` detach a layer and give it back to the caller. The :term[destructor]{id=destructor} and `Clear` detach and delete from the top down, so an overlay goes before the layers it decorates.

:::rule[The main thread owns events and layers]
The engine's rules let the main thread own the scene, the input and the rendering, and let background work return results only through `Application::SubmitToMainThread` or polled queues. Events follow it: they run inside the Input stage on the main thread, so a layer's `OnEvent` may touch the scene without a lock. Never call a layer's `OnEvent` from a worker thread. [Threads and the job system](jobs.md) teaches why.
:::

## The GLFW backend

**GLFW** is a C library for windows, input and Vulkan surfaces, and `GLFWWindow` is Strata's window backend on top of it. GLFW starts with the first window and stops with the last. Before it starts, the backend gives it the engine's own Vulkan loader, so that a surface GLFW creates is valid for the engine's Vulkan instance. The window asks for no graphics context, because Strata draws through Vulkan.

GLFW reports through C functions, and a C function cannot carry a C++ object. GLFW therefore lets a program store one pointer on the window, and the backend stores a small `WindowData` record there. A callback reads the record back, so it can reach the event callback of the window.

The callbacks of keys, text and the mouse do two things in a fixed order. They first tell `Input` about the change of state through `Input::Process*`, and then they make the event and pass it on. A key repeat is the exception, because it changes no state and makes only an event. The key callback is the best example, and [input devices and their state](../input/devices-state.md) quotes it.

`ProcessEvents` is `glfwPollEvents`, followed by a poll of the gamepads, which only updates the state. GLFW runs its callbacks inside `glfwPollEvents`, so every event of a frame runs at once, in the order the system reported it, before the call returns.

## A toy version

The toy shows the whole design without a window. It has two event classes, a dispatcher, a stack with two layers and one overlay, and a function that sends four events. The layers are :term[lambdas]{id=lambda}, to keep the toy short; the real layers are classes. Watch two things in the output: the order in which the layers are asked, and where the asking stops.

```cpp sketch="core-windows-events-toy.cpp"
// A toy event system: an event has a type and a Handled flag, a dispatcher runs the handler that matches the type,
// and a stack of layers and an overlay hands each event over from the top down until one handles it.
#include <cstdio>
#include <functional>
#include <string>
#include <utility>
#include <vector>

enum class EventType
{
	KeyPressed,
	WindowClose
};

class Event
{
public:
	virtual ~Event() = default;
	virtual EventType GetEventType() const = 0;
	virtual const char* GetName() const = 0;

	bool Handled = false;
};

class KeyPressedEvent : public Event
{
public:
	explicit KeyPressedEvent(char key)
		: Key(key)
	{
	}

	static EventType GetStaticType() { return EventType::KeyPressed; }
	EventType GetEventType() const override { return GetStaticType(); }
	const char* GetName() const override { return "KeyPressed"; }

	char Key;
};

class WindowCloseEvent : public Event
{
public:
	static EventType GetStaticType() { return EventType::WindowClose; }
	EventType GetEventType() const override { return GetStaticType(); }
	const char* GetName() const override { return "WindowClose"; }
};

class EventDispatcher
{
public:
	explicit EventDispatcher(Event& event)
		: m_Event(event)
	{
	}

	template<typename T, typename F>
	bool Dispatch(const F& function)
	{
		if (m_Event.GetEventType() != T::GetStaticType())
			return false;
		m_Event.Handled |= function(static_cast<T&>(m_Event));
		return true;
	}
private:
	Event& m_Event;
};

struct Layer
{
	std::string Name;
	std::function<void(Event&)> OnEvent;
};

class LayerStack
{
public:
	LayerStack() = default;
	LayerStack(const LayerStack&) = delete;
	LayerStack& operator=(const LayerStack&) = delete;
	~LayerStack()
	{
		for (auto it = m_Layers.rbegin(); it != m_Layers.rend(); ++it)
			delete *it;
	}

	void PushLayer(Layer* layer) { m_Layers.insert(m_Layers.begin() + m_InsertIndex++, layer); }
	void PushOverlay(Layer* overlay) { m_Layers.push_back(overlay); }
	std::vector<Layer*>::reverse_iterator rbegin() { return m_Layers.rbegin(); }
	std::vector<Layer*>::reverse_iterator rend() { return m_Layers.rend(); }
private:
	std::vector<Layer*> m_Layers;
	size_t m_InsertIndex = 0;
};

static void Send(LayerStack& stack, Event& event, bool& running)
{
	std::printf("%s\n", event.GetName());
	for (auto it = stack.rbegin(); it != stack.rend(); ++it)
	{
		if (event.Handled)
			break;
		std::printf("  %s is asked\n", (*it)->Name.c_str());
		(*it)->OnEvent(event);
	}
	if (event.GetEventType() == EventType::WindowClose && !event.Handled)
		running = false;
}

int main()
{
	bool typing = false;
	bool asked = false;
	LayerStack stack;
	stack.PushLayer(new Layer { "Game", [](Event& event)
	{
		EventDispatcher dispatcher(event);
		dispatcher.Dispatch<KeyPressedEvent>([](KeyPressedEvent& key)
		{
			std::printf("  Game moves with %c\n", key.Key);
			return true;
		});
	} });
	stack.PushLayer(new Layer { "Editor", [&asked](Event& event)
	{
		EventDispatcher dispatcher(event);
		dispatcher.Dispatch<WindowCloseEvent>([&asked](WindowCloseEvent&)
		{
			std::printf("  Editor %s\n", asked ? "lets it pass" : "asks about unsaved changes");
			const bool handled = !asked;
			asked = true;
			return handled;
		});
	} });
	stack.PushOverlay(new Layer { "TextBox", [&typing](Event& event)
	{
		EventDispatcher dispatcher(event);
		dispatcher.Dispatch<KeyPressedEvent>([&typing](KeyPressedEvent& key)
		{
			if (typing)
				std::printf("  TextBox types %c\n", key.Key);
			return typing;
		});
	} });

	bool running = true;
	KeyPressedEvent first('A');
	Send(stack, first, running);

	typing = true;
	KeyPressedEvent second('B');
	Send(stack, second, running);

	for (int request = 1; request <= 2; request++)
	{
		WindowCloseEvent close;
		Send(stack, close, running);
		std::printf("  running: %s\n", running ? "yes" : "no");
	}
	return 0;
}
```

```text output-of="core-windows-events-toy.cpp"
KeyPressed
  TextBox is asked
  Editor is asked
  Game is asked
  Game moves with A
KeyPressed
  TextBox is asked
  TextBox types B
WindowClose
  TextBox is asked
  Editor is asked
  Editor asks about unsaved changes
  running: yes
WindowClose
  TextBox is asked
  Editor is asked
  Editor lets it pass
  Game is asked
  running: no
```

1. **Line 33:** `GetStaticType` lets the dispatcher name a class without making an object of it.
2. **Line 61:** the handler's answer is ORed into `Handled`, so one handler cannot undo another's mark.
3. **Line 86:** layers are inserted below the overlays, at the insert index, which then moves up by one.
4. **Lines 98–101:** the walk goes from the end of the stack to its start and stops when `Handled` is set.
5. **Lines 105–106:** a close that nobody handled ends the loop, so the editor's first answer keeps it running.

The first key reached the game, because the overlay and the editor did not handle it. The second stopped at the text box, which was typing, and the editor and the game never heard of it. The first close stopped at the editor, and the second passed through every layer and ended the loop. The real code adds modules that see the event before the layers, 15 event types with categories, the `OnAttach` and `OnDetach` calls and the C callbacks of the window system.

## The real code

The real code is spread over five files. Follow the data: the event classes first, then the callbacks that make events, the mode switch, the application's walk and the stack. Start with the types the whole design rests on.

```cpp src="Strata/src/Strata/Events/Event.h#L15-L58"
enum class EventType
{
	None = 0,
	WindowClose, WindowResize, WindowFocus, WindowLostFocus, WindowMoved, WindowFileDrop, WindowContentScale,
	KeyPressed, KeyReleased, KeyTyped,
	MouseButtonPressed, MouseButtonReleased, MouseMoved, MouseScrolled, MouseLeave
};

// Plain enum used as bit flags. Deliberately avoids the identifier `None`, which X11 headers define as a macro.
enum EventCategory
{
	EventCategoryNone        = 0,
	EventCategoryApplication = ST_BIT(0),
	EventCategoryInput       = ST_BIT(1),
	EventCategoryKeyboard    = ST_BIT(2),
	EventCategoryMouse       = ST_BIT(3),
	EventCategoryMouseButton = ST_BIT(4)
};

#define ST_EVENT_CLASS_TYPE(type) \
static EventType GetStaticType() { return EventType::type; } \
virtual EventType GetEventType() const override { return GetStaticType(); } \
virtual const char* GetName() const override { return #type; }

#define ST_EVENT_CLASS_CATEGORY(category) \
virtual int GetCategoryFlags() const override { return category; }

class Event
{
public:
	virtual ~Event() = default;

	bool Handled = false;

	virtual EventType GetEventType() const = 0;
	virtual const char* GetName() const = 0;
	virtual int GetCategoryFlags() const = 0;
	virtual std::string ToString() const { return GetName(); }

	bool IsInCategory(EventCategory category) const
	{
		return (GetCategoryFlags() & category) != 0;
	}
};
```

1. **Line 15:** `EventType` lists the 15 types after a `None` of value 0. It is a scoped `enum class`, the only kind of enum in which the engine's rules allow the name `None`.
2. **Line 24:** `EventCategory` is a plain enum used as bit flags, and it has no `None` value, for the reason that the comment above it gives.
3. **Lines 34–40:** two macros write the three functions a class would otherwise repeat, so a new class names its type and its categories in two lines.
4. **Line 47:** `Handled` is a public data member, so any layer sets it without a :term[function call]{id=function-call}.

The dispatcher is the second half of the file.

```cpp src="Strata/src/Strata/Events/Event.h#L60-L81"
class EventDispatcher
{
public:
	EventDispatcher(Event& event)
		: m_Event(event)
	{
	}

	// F is deduced by the compiler: bool(T&)
	template<typename T, typename F>
	bool Dispatch(const F& function)
	{
		if (m_Event.GetEventType() == T::GetStaticType())
		{
			m_Event.Handled |= function(static_cast<T&>(m_Event));
			return true;
		}
		return false;
	}
private:
	Event& m_Event;
};
```

1. **Line 69:** `T` is the event class and `F` the handler's type, which the :term[compiler]{id=compiler} works out from the lambda that the caller passes.
2. **Line 72:** a comparison of two type ids replaces a `dynamic_cast`, so events need no run-time type information.
3. **Line 74:** `|=` keeps a mark that an earlier handler set, and the `static_cast` is safe because the types matched.

GLFW's callbacks make the events. This excerpt holds the :term[user pointer]{id=user-pointer} and the two callbacks for the size and the close.

```cpp src="Strata/src/Platform/GLFW/GLFWWindow.cpp#L230-L249"
glfwSetWindowUserPointer(m_Window, &m_Data);

glfwSetWindowSizeCallback(m_Window, [](GLFWwindow* window, int newWidth, int newHeight)
{
	WindowData& data = *static_cast<WindowData*>(glfwGetWindowUserPointer(window));
	data.Width = static_cast<uint32_t>(newWidth);
	data.Height = static_cast<uint32_t>(newHeight);

	WindowResizeEvent event(data.Width, data.Height);
	if (data.EventCallback)
		data.EventCallback(event);
});

glfwSetWindowCloseCallback(m_Window, [](GLFWwindow* window)
{
	WindowData& data = *static_cast<WindowData*>(glfwGetWindowUserPointer(window));
	WindowCloseEvent event;
	if (data.EventCallback)
		data.EventCallback(event);
});
```

1. **Line 230:** the window's user pointer points at `m_Data`, the record every callback finds again.
2. **Lines 234–236:** the size callback stores the new size in the record first, so `GetWidth` is already right when the event runs.
3. **Lines 238–240:** the event lives on the callback's stack, and the handler runs before the callback returns.
4. **Lines 246–248:** the close callback makes a `WindowCloseEvent` and never reads GLFW's own close flag, so the engine decides whether the program closes.

The modes are the other thing the backend does. `SetMode` records the windowed place before it leaves Windowed, then switches by mode.

```cpp src="Strata/src/Platform/GLFW/GLFWWindow.cpp#L482-L508"
if (m_Mode == WindowMode::Windowed)
{
	glfwGetWindowPos(m_Window, &m_WindowedX, &m_WindowedY);
	glfwGetWindowSize(m_Window, &m_WindowedWidth, &m_WindowedHeight);
}
switch (mode)
{
	case WindowMode::Windowed:
		glfwSetWindowMonitor(m_Window, nullptr, m_WindowedX, m_WindowedY, m_WindowedWidth, m_WindowedHeight, 0);
		m_Mode = mode;
		if (m_Resolution.x > 0 && m_Resolution.y > 0)
			SetFramebufferSize(static_cast<int>(m_Resolution.x), static_cast<int>(m_Resolution.y));
		return;
	case WindowMode::Fullscreen:
	{
		// The display switches to the resolution asked for, or stays at the desktop's.
		const int width = m_Resolution.x > 0 ? static_cast<int>(m_Resolution.x) : desktop->width;
		const int height = m_Resolution.y > 0 ? static_cast<int>(m_Resolution.y) : desktop->height;
		glfwSetWindowMonitor(m_Window, monitor, 0, 0, width, height, GLFW_DONT_CARE);
		break;
	}
	case WindowMode::Borderless:
		// A full screen window at the desktop's video mode does not switch the display's mode.
		glfwSetWindowMonitor(m_Window, monitor, 0, 0, desktop->width, desktop->height, desktop->refreshRate);
		break;
}
m_Mode = mode;
```

1. **Lines 482–486:** the place and size of a windowed window are saved only when the window leaves Windowed, so they are always the last windowed ones.
2. **Lines 489–494:** returning to `Windowed` takes the window off the monitor, restores the saved place and size, then applies a resolution that was set meanwhile.
3. **Lines 495–502:** `Fullscreen` asks GLFW for the resolution given, or the desktop's when none was given, and `GLFW_DONT_CARE` leaves the refresh rate to the system.
4. **Lines 503–506:** `Borderless` asks for the desktop's own video mode, so the display does not switch.

The application's walk is the heart of propagation.

```cpp src="Strata/src/Strata/Core/Application.cpp#L202-L223"
void Application::OnEvent(Event& event)
{
	EventDispatcher dispatcher(event);
	dispatcher.Dispatch<WindowResizeEvent>(ST_BIND_EVENT_FN(OnWindowResize));

	for (EngineModule* module : GetStartedModules())
	{
		if (event.Handled)
			break;
		module->OnEvent(event);
	}
	for (auto it = m_LayerStack.rbegin(); it != m_LayerStack.rend(); ++it)
	{
		if (event.Handled)
			break;
		(*it)->OnEvent(event);
	}

	// A close request goes through the layers first: one that handles it (to ask about unsaved changes, for
	// example) keeps the application running.
	if (event.GetEventType() == EventType::WindowClose && !event.Handled)
		m_Running = false;
```

1. **Lines 204–205:** the application's own dispatcher handles a change of size. `ST_BIND_EVENT_FN` turns the :term[member function]{id=member-function} `OnWindowResize` into a lambda, and `OnWindowResize` returns false, so the event continues.
2. **Lines 207–212:** the modules come first, in their start order, and a handled event ends the walk.
3. **Lines 213–218:** the layers follow from `rbegin` to `rend`, which is top down, so overlays go first.
4. **Lines 220–223:** a close that survives every layer stops the loop. The test checks the event's type first, so no other event can end the program.

The stack is the last file.

```cpp src="Strata/src/Strata/Core/LayerStack.cpp#L7-L54"
LayerStack::~LayerStack()
{
	Clear();
}

void LayerStack::Clear()
{
	// Detach top-down so overlays go before the layers they decorate.
	for (auto it = m_Layers.rbegin(); it != m_Layers.rend(); ++it)
	{
		(*it)->OnDetach();
		delete *it;
	}
	m_Layers.clear();
	m_LayerInsertIndex = 0;
}

void LayerStack::PushLayer(Layer* layer)
{
	m_Layers.emplace(m_Layers.begin() + m_LayerInsertIndex, layer);
	m_LayerInsertIndex++;
}

void LayerStack::PushOverlay(Layer* overlay)
{
	m_Layers.emplace_back(overlay);
}

void LayerStack::PopLayer(Layer* layer)
{
	auto it = std::find(m_Layers.begin(), m_Layers.begin() + m_LayerInsertIndex, layer);
	if (it != m_Layers.begin() + m_LayerInsertIndex)
	{
		layer->OnDetach();
		m_Layers.erase(it);
		m_LayerInsertIndex--;
	}
}

void LayerStack::PopOverlay(Layer* overlay)
{
	auto it = std::find(m_Layers.begin() + m_LayerInsertIndex, m_Layers.end(), overlay);
	if (it != m_Layers.end())
	{
		overlay->OnDetach();
		m_Layers.erase(it);
	}
}
```

1. **Lines 12–22:** `Clear` detaches, then deletes, from the top down, and resets the insert index.
2. **Line 26:** a layer is inserted at the insert index, which stays below every overlay.
3. **Line 32:** an overlay is appended, so the newest overlay is on top.
4. **Lines 35–44:** `PopLayer` searches only below the insert index, so it cannot find an overlay. It detaches the layer and does not delete it.

Window creation has one more piece. `Application` makes the window with `WindowFactory` when the specification has one and with `Window::Create` otherwise. It then calls `SetEventCallback` with `ST_BIND_EVENT_FN(OnEvent)` and gives `Input` the window. The tests use this to run the whole :term[frame loop]{id=game-loop} on `Tests::StubWindow`, a `Window` that delivers the events a test queued, into `Input` first and then through the event callback, as `GLFWWindow` does.

:::example[One key press and one close in the editor]
The player presses **S**. GLFW calls the key callback, which calls `Input::ProcessKey` with the code of S and true. The callback then makes a `KeyPressedEvent` (categories 4 + 2 = 6) and calls `Application::OnEvent`.

The application's own dispatcher searches for a `WindowResizeEvent` and finds none, so the module step starts. No built-in module overrides `OnEvent` at the pin, so the editor's modules do nothing. The layers follow from the top.

`ImGuiLayer`, the overlay, passes the event to ImGui. If a text field has the keyboard, ImGui reports that it wants it, and the overlay sets `Handled`: `EditorLayer` never hears of the key. If no field has it, `EditorLayer::OnEvent` runs, notes that the editor is not idle, and its dispatcher matches nothing.

Later the player clicks the window's close button. GLFW calls the close callback, and a `WindowCloseEvent` follows the same path. The overlay passes it to ImGui but does not handle it, because it is not a mouse or keyboard event. `EditorLayer` matches it.

With changes not yet saved (a scene, a setting or a save in flight) the layer asks the player, returns true, and the program runs on. The loop ends only when the player answers, and the dialog calls `Close`. With nothing to save the layer returns false, the event stays not handled, and `m_Running` becomes false.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A queue of events that the program drains when it is ready | Windows programs, with the messages the system keeps for each window, and many game libraries | A program picks the moment to read, and it can look at the events of a whole frame together | Memory for copies of events, every event at least some time late, and the order of events against the polled state is harder to state |
| Handlers that register for an event type, called in any order | The observer pattern, and the signals of libraries such as Qt | Any code can subscribe without a stack, and one event can reach several handlers | There is no top and no "someone used this" that stops the others, so the order of effects is hard to follow |
| Stages of delivery through a tree of nodes, with a call that marks an event handled | Godot, which offers a node the event in one function and then offers it to the rest of the tree in another | An event can reach the objects of the scene, not only the program's layers | A tree that must be kept in sync with the scene, and two functions to choose between in every node |

## How it is tested

Two suites cover the area, and both run without a window or a graphics card.

- `Core` (`StrataTests/src/Core/CoreTests.cpp`): one case checks that `EventDispatcher` routes by type and records the mark, and the categories of a key event. Another pushes an overlay first and two layers after it, checks that the order is both layers and then the overlay, and checks that the stack detaches and deletes from the top down.
- `Core.WindowBackend` (`StrataTests/src/Core/WindowBackendTests.cpp`): runs the frame loop on `Tests::StubWindow`. One case sends keys, mouse and a new size, and checks both the polled state and the order of events. One checks that frames while the window is minimized are not counted. One checks the close: the loop ends after a close, unless a layer handles it. One checks that a window the factory cannot make ends the start with exit code 1.

Run them on Windows, in the folder of your source build, after a `Debug` build:

```powershell
build/windows/bin/Debug/StrataTests.exe --test-suite=Core
build/windows/bin/Debug/StrataTests.exe --test-suite=Core.WindowBackend
```

The first command runs the `Core` suite, which has many other cases beside these two, and the second runs the window cases. Each prints how many cases passed. Two more cases run only where their `#if` lines allow: one on Linux with GLFW, which checks that `Window::Create` returns null without a display, and one in a build without GLFW.

## Changing it safely

Two extensions are common. To add an event type, add a value to `EventType` and a class, written with the two macros, in the header that fits its group. Then raise it in the GLFW callbacks and in `Tests::StubWindow`, so that tests can queue it. To add a layer, derive from `Layer`, make it with `new` and push it with `Application::PushLayer` or `PushOverlay`. Never keep the pointer and delete it yourself.

Keep these rules when you change the area:

- Keep the order in the callbacks: change the polled state first, then make the event, so that a handler may read either.
- Keep `Handled` set with `|=` and never reset by the walk, so a layer cannot reopen an event that another layer used.
- Keep a close request not handled by default. The editor's veto and the stop of the loop both rely on it.
- Keep GLFW in `Platform/GLFW`, and new events free of window system types.
- Keep the stack's order: updates from the bottom up, events from the top down, overlays above layers.

Then run `Core` and `Core.WindowBackend`, and add a case to the second for a new event or rule. A change to a callback also needs the same change in `Tests::StubWindow`, or the stand-in stops matching the backend.

## Summary

- The window system calls a callback, which first fills the polled `Input` state, then makes an event on its stack and hands it to `Application::OnEvent` at once.
- `OnEvent` does its own first step, then asks the modules and the layers from the top down, overlays first, until `Handled` is set.
- A close request that nobody handles ends the loop, so a layer can veto it, as the editor does to ask about changes not yet saved.
- `Windowed` restores the last place, `Fullscreen` switches the display to the resolution asked for, `Borderless` covers the display without a switch, and a Fullscreen specification starts in `Borderless`.
- The content scale is the display's density factor, and on a points display the framebuffer has the window's size times the scale.

## Check yourself

1. Put these in the order they happen when a key is pressed: the overlay's `OnEvent`, `Input::ProcessKey`, `glfwPollEvents`, a module's `OnEvent`, the construction of `KeyPressedEvent`, the editor layer's `OnEvent`.

   :::answer{tests="event-path"}
   `glfwPollEvents`, then `Input::ProcessKey`, the construction of `KeyPressedEvent`, a module's `OnEvent`, the overlay's `OnEvent` and the editor layer's `OnEvent`. The state changes before the event exists, the modules come before the layers, and the overlay comes first among the layers.
   :::

2. A program calls `PushLayer(A)`, `PushOverlay(O)` and `PushLayer(B)`. In which order do the layers update, and in which order do they get an event?

   :::answer{tests="layer-order"}
   The stack holds A, B, O: `PushLayer` inserts at the insert index, which stays below the overlay. Updates run A, B, O. Events run O, B, A. If B sets `Handled`, A never sees the event.
   :::

3. A layer sets `Handled` on the first `WindowClose` only. The player clicks close in the third and the fifth frame of a run that has no frame limit. When does the loop end?

   :::answer{tests="close-veto"}
   The first click stops at the layer, so the loop runs on. The second is not handled: the application sets its running flag to false, and the fifth frame still runs to its end. The loop ends after five frames, which is what the test `A close request ends the loop unless a layer handles it` counts. Without the veto it would end after three.
   :::

4. A game's manifest says Fullscreen. Which mode does its window start in? (a) Fullscreen, with a switch of the display's mode. (b) `Borderless`, covering the display at the desktop's mode. (c) Windowed, maximized.

   :::answer{tests="window-modes"}
   The answer is (b). A window made with `WindowSpecification::Fullscreen` set starts in `Borderless` at the desktop's resolution. Answer (a) is what `SetMode(WindowMode::Fullscreen)` does later, and it is the only mode that switches the display. Answer (c) confuses Windowed with a mode that covers the display.
   :::

5. A Retina window has 1280 by 720 points. How many pixels wide is its framebuffer, what does `GetContentScale` return, and how many pixels does a panel of 300 points cover?

   :::answer{tests="content-scale"}
   The content scale is 2, so the framebuffer is 1280 × 2 = 2560 pixels wide and 720 × 2 = 1440 high. The panel covers 300 × 2 = 600 pixels. Answering 1280 forgets that the window's size is in points; answering 300 forgets the scale.
   :::

## Exercises

1. **Basic.** In the editor, an extra layer `L` is made with `PushLayer` after the editor's layer and sets `Handled` for every key press. Which layers see a key press, in which order?

   :::answer[Worked solution]{tests="layer-order"}
   The stack holds the editor's layer, then `L`, then the overlay of ImGui. Events run from the top: the overlay sees the key first, `L` second, and `L` sets `Handled`, so the editor's layer never sees it. The modules came before all three. The overlay's own checks run first, so a text field that wants the key takes it before `L`.
   :::

2. **Medium.** A game asks for 1920 pixels of framebuffer width in Windowed mode. Write a program that prints the window width in screen coordinates to ask for on three displays: window 1600 and framebuffer 1600, window 1600 and framebuffer 3200, and window 1280 and framebuffer 1920.

   :::answer[Worked solution]{tests="content-scale" solution="sketches/core-windows-events-pixels.cpp"}
   The window's size is scaled by the ratio of the window to the framebuffer, and the result is rounded and kept at 1 or more. The program prints one line for each display.

   ```cpp sketch="core-windows-events-pixels.cpp"
   // The window width, in screen coordinates, that gives a wanted framebuffer width: the window's size is scaled by the
   // ratio of the window to its framebuffer, the way a windowed window's resolution is set.
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   struct Display
   {
   	const char* Name;
   	int WindowWidth;      // screen coordinates
   	int FramebufferWidth; // pixels
   };

   static int WindowWidthFor(int wantedPixels, const Display& display)
   {
   	if (display.WindowWidth <= 0 || display.FramebufferWidth <= 0)
   		return wantedPixels;
   	const double ratio = static_cast<double>(display.WindowWidth) / display.FramebufferWidth;
   	return std::max(1, static_cast<int>(std::lround(wantedPixels * ratio)));
   }

   int main()
   {
   	const Display displays[] = {
   		{ "pixels", 1600, 1600 },
   		{ "points", 1600, 3200 },
   		{ "odd", 1280, 1920 },
   	};
   	for (const Display& display : displays)
   	{
   		std::printf("%s: window %d, framebuffer %d: ask for %d\n", display.Name, display.WindowWidth,
   			display.FramebufferWidth, WindowWidthFor(1920, display));
   	}
   	return 0;
   }
   ```

   ```text output-of="core-windows-events-pixels.cpp"
   pixels: window 1600, framebuffer 1600: ask for 1920
   points: window 1600, framebuffer 3200: ask for 960
   odd: window 1280, framebuffer 1920: ask for 1280
   ```

   1. **Line 14:** `WindowWidthFor` is the whole job; the engine's version also scales the height.
   2. **Line 18:** the ratio is a double, so no precision is lost before the rounding.
   3. **Line 19:** `std::lround` rounds to the nearest whole number, and `std::max` keeps the result at least 1.

   The pixel display needs 1920, the Retina display needs half as many coordinates, 960, and the third display needs 1280, its own width, because 1920 pixels are all of its framebuffer.
   :::

3. **Medium.** Trace it yourself. A close request leaves GLFW's close callback and reaches the editor's veto. Set breakpoints in a `Debug` build of the editor, and write down the functions in order.

   :::answer[Worked solution]{tests="event-path close-veto"}
   Set a breakpoint in the close callback in `Strata/src/Platform/GLFW/GLFWWindow.cpp`, the lambda passed to `glfwSetWindowCloseCallback` inside `GLFWWindow::Open`. The next stops are `Application::OnEvent` in `Strata/src/Strata/Core/Application.cpp`, then `ImGuiLayer::OnEvent` in `Strata/src/Strata/ImGui/ImGuiLayer.cpp`, and last the lambda for `WindowCloseEvent` in `EditorLayer::OnEvent` in `StrataEditor/src/EditorLayer.cpp`. With changes not yet saved it calls `RequestQuit` and returns true, so `Application::OnEvent` leaves `m_Running` alone.
   :::

4. **Hard.** On a source build, write a test layer that counts the events for a new window size and for a new content scale, and feed it from `Tests::StubWindow` through `WindowFactory`.

   :::answer[Worked solution]{tests="event-path layer-order"}
   Start from `MakeStubSpecification` and `RecordingLayer` in `StrataTests/src/Core/WindowBackendTests.cpp`. Derive a layer whose `OnEvent` makes an `EventDispatcher` and counts in one handler for `WindowResizeEvent` and one for `WindowContentScaleEvent`, both returning false. Set `specification.MaxFrames` to 2, push the layer, and in `OnProcessEvents` call `QueueResize(800, 600)` and `QueueContentScale(2.0f)` at call 0. After `Run`, both counts are 1, and the stand-in's `ContentScale` is 2.

   Run `Core.WindowBackend`. Then make one handler return true, and check that a second layer below the counter no longer sees that event.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/Window.h`: `Window`, `WindowSpecification`, `WindowMode`, `CursorShape`, `WindowIconImage`.
- `Strata/src/Platform/GLFW/GLFWWindow.cpp` and `GLFWWindow.h`: `GLFWWindow`, its callbacks, `SetMode`, `SetResolution`, `ProcessEvents`; `Strata/src/Platform/NoWindow/NoWindow.cpp`: the backend without a window.
- `Strata/src/Strata/Events/`: `Event.h` (`Event`, `EventType`, `EventCategory`, `EventDispatcher`), `ApplicationEvent.h`, `KeyEvent.h`, `MouseEvent.h`.
- `Strata/src/Strata/Core/Application.cpp`: `Application::OnEvent`, `PushLayer`, `PushOverlay`, `WindowFactory` in `Application.h`.
- `Strata/src/Strata/Core/Layer.h`, `LayerStack.h` and `LayerStack.cpp`: `Layer`, `LayerStack`.
- `Strata/src/Strata/ImGui/ImGuiLayer.cpp` and `StrataEditor/src/EditorLayer.cpp`: the overlay and the editor's layer.
- Tests: `StrataTests/src/Core/CoreTests.cpp`, `StrataTests/src/Core/WindowBackendTests.cpp`, `StrataTests/src/StubWindow.h`.

## Further reading

- [Robert Nystrom, "Event Queue", in Game Programming Patterns](https://gameprogrammingpatterns.com/event-queue.html): when to put events in a queue and what it costs; beginner.
- [Robert Nystrom, "Observer", in Game Programming Patterns](https://gameprogrammingpatterns.com/observer.html): handlers that register for a happening; beginner.
- [Microsoft, About messages and message queues](https://learn.microsoft.com/en-us/windows/win32/winmsg/about-messages-and-message-queues): how Windows keeps a queue of messages for each window; intermediate.
- [Godot, Using InputEvent](https://docs.godotengine.org/en/stable/tutorials/inputs/inputevent.html): how an engine passes an input event through the nodes of a scene, and how a node marks it handled; intermediate.
- GLFW, the input guide and the window guide at glfw.org: the callbacks, polling and window modes that the backend uses; intermediate.
