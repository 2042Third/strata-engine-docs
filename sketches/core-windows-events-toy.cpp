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
