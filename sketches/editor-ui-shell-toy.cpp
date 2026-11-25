// A toy panel registry: descriptors checked on registration, open states kept as text, and a focus request that
// waits behind a modal and is retried for at most four frames.
#include <cstdio>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>

struct Panel
{
	virtual ~Panel() = default;
	virtual void OnUpdate() {}
	virtual void OnRender(const std::string& title) = 0;
	virtual void OnHidden() {}
};

struct Label : Panel
{
	void OnRender(const std::string& title) override { std::printf("  draw %s\n", title.c_str()); }
	void OnHidden() override { std::printf("  hidden\n"); }
};

struct Descriptor
{
	std::string Id;
	std::string Title;
	bool OpenByDefault = true;
	std::function<std::unique_ptr<Panel>()> Create;
};

class Registry
{
public:
	bool Register(Descriptor descriptor, std::string& error)
	{
		if (descriptor.Id.empty() || descriptor.Id.find_first_of("=#[]") != std::string::npos)
			return error = "bad id", false;
		for (const Entry& entry : m_Entries)
			if (entry.Info.Id == descriptor.Id)
				return error = "id taken", false;
		if (!descriptor.Create)
			return error = "no factory", false;
		Entry entry { std::move(descriptor), nullptr, true, false, 0 };
		entry.Instance = entry.Info.Create();
		const auto saved = m_Saved.find(entry.Info.Id);
		entry.Open = saved != m_Saved.end() ? saved->second : entry.Info.OpenByDefault;
		m_Entries.push_back(std::move(entry));
		return true;
	}

	void Read(const std::string& id, bool open) { m_Saved[id] = open; }
	void Focus(const std::string& id)
	{
		for (Entry& entry : m_Entries)
			if (entry.Info.Id == id)
				entry.Open = entry.WantsFocus = true;
	}

	void Frame(int frame, bool modalOpen, int tabShowsFromFrame)
	{
		std::printf("frame %d%s\n", frame, modalOpen ? " (modal open)" : "");
		for (Entry& entry : m_Entries)
			entry.Instance->OnUpdate();
		for (Entry& entry : m_Entries)
		{
			if (!entry.Open)
			{
				entry.Instance->OnHidden();
				continue;
			}
			const bool focusing = entry.WantsFocus && !modalOpen;
			if (focusing)
			{
				std::printf("  focus %s\n", entry.Info.Id.c_str());
				if (frame >= tabShowsFromFrame || ++entry.Attempts >= c_MaxAttempts)
					entry.WantsFocus = false;
			}
			entry.Instance->OnRender(entry.Info.Title);
		}
	}

	void Write() const
	{
		for (const Entry& entry : m_Entries)
			std::printf("%s=%d\n", entry.Info.Id.c_str(), entry.Open ? 1 : 0);
	}

private:
	struct Entry
	{
		Descriptor Info;
		std::unique_ptr<Panel> Instance;
		bool Open;
		bool WantsFocus;
		int Attempts;
	};
	static constexpr int c_MaxAttempts = 4;
	std::vector<Entry> m_Entries;
	std::map<std::string, bool> m_Saved;
};

int main()
{
	Registry registry;
	registry.Read("Console", false);
	std::string error;
	const auto make = []() { return std::make_unique<Label>(); };
	for (const char* id : { "Hierarchy", "Console", "Bad=Id", "Hierarchy" })
		if (!registry.Register({ id, id, true, make }, error))
			std::printf("refused '%s': %s\n", id, error.c_str());
	registry.Focus("Console");
	registry.Frame(1, true, 3);
	registry.Frame(2, false, 3);
	registry.Frame(3, false, 3);
	registry.Write();
	return 0;
}
