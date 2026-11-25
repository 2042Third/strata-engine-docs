// A toy editor in three parts: a core with no UI, a UI that only calls and draws it, and a host the UI asks for the window.
#include <cstdio>
#include <string>
#include <vector>

namespace
{

	class Host
	{
	public:
		virtual ~Host() = default;
		virtual bool IsRunning() const = 0;
		virtual void Close() = 0;
		virtual int GetFrameCount() const = 0;
	};

	// All state and logic: no printing of its own, no host.
	class Core
	{
	public:
		void Queue(const std::string& name) { m_Queue.push_back(name); }

		void Poll()
		{
			for (const std::string& name : m_Queue)
			{
				m_Selection.push_back(name);
				++m_SelectionVersion;
			}
			m_Queue.clear();
		}

		const std::vector<std::string>& GetSelection() const { return m_Selection; }
		int GetSelectionVersion() const { return m_SelectionVersion; }

	private:
		std::vector<std::string> m_Queue;
		std::vector<std::string> m_Selection;
		int m_SelectionVersion = 0;
	};

	// Draws the core and calls it; it never changes the core's data itself.
	class Ui
	{
	public:
		explicit Ui(Host& host)
			: m_Host(host)
		{
		}

		void Update(Core& core)
		{
			core.Poll();
			std::printf("frame %d: polls done\n", m_Host.GetFrameCount());
		}

		void Render(const Core& core)
		{
			std::printf("frame %d: draw %zu selected, version %d\n", m_Host.GetFrameCount(), core.GetSelection().size(),
				core.GetSelectionVersion());
			if (m_Host.GetFrameCount() == 2)
				m_Host.Close();
		}

	private:
		Host& m_Host;
	};

	// A host without a window, as a test supplies it.
	class FakeHost : public Host
	{
	public:
		bool IsRunning() const override { return m_Running; }
		void Close() override { m_Running = false; }
		int GetFrameCount() const override { return m_Frames; }
		void EndFrame() { ++m_Frames; }

	private:
		bool m_Running = true;
		int m_Frames = 0;
	};

}

int main()
{
	Core core;
	FakeHost host;
	Ui ui(host);
	core.Queue("Cube");
	while (host.IsRunning())
	{
		if (host.GetFrameCount() == 1)
			core.Queue("Lamp");
		ui.Update(core);
		ui.Render(core);
		host.EndFrame();
	}
	return 0;
}
