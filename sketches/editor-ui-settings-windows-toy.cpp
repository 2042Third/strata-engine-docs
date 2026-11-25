// A toy settings window: a generic page drawn from a section's fields, custom pages by section id,
// edits that run one command, and a copy of the values read again only when their version changed.
#include <cstdio>
#include <functional>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <vector>

struct Field
{
	std::string Name;
	float Default;
	float Min;
	float Max;
};

struct Section
{
	std::string Id;
	std::vector<Field> Fields;
};

struct Store
{
	std::map<std::string, float> Values;
	unsigned Version = 0;
};

// The only way to change the store: a refused value changes nothing and says why.
bool SetValue(Store& store, const Section& section, const std::string& name, float value)
{
	for (const Field& field : section.Fields)
	{
		if (field.Name != name)
			continue;
		if (value < field.Min || value > field.Max)
		{
			std::printf("  command refused: %s %.2f is outside %.2f to %.2f\n", name.c_str(), value, field.Min, field.Max);
			return false;
		}
		store.Values[name] = value;
		store.Version++;
		std::printf("  command: set %s.%s = %.2f\n", section.Id.c_str(), name.c_str(), value);
		return true;
	}
	return false;
}

using Edits = std::map<std::string, float>; // The edits that finished this frame

class Page
{
public:
	virtual ~Page() = default;
	virtual void Draw(Store& store, const Edits& finished) = 0;
};

class GenericPage final : public Page
{
public:
	explicit GenericPage(const Section& section)
		: m_Section(section)
	{
	}

	void Draw(Store& store, const Edits& finished) override
	{
		if (!m_Seen || *m_Seen != store.Version)
		{
			m_Seen = store.Version;
			m_Copy.clear();
			for (const Field& field : m_Section.Fields)
				m_Copy[field.Name] = store.Values.count(field.Name) ? store.Values[field.Name] : field.Default;
			m_Reads++;
		}
		for (const Field& field : m_Section.Fields)
			std::printf("  %s = %.2f\n", field.Name.c_str(), m_Copy[field.Name]);
		for (const auto& edit : finished)
		{
			if (SetValue(store, m_Section, edit.first, edit.second))
				m_Seen.reset(); // Read again: the value the command applied
		}
	}

	int GetReads() const { return m_Reads; }
private:
	const Section& m_Section;
	std::map<std::string, float> m_Copy;
	std::optional<unsigned> m_Seen;
	int m_Reads = 0;
};

class CustomPage final : public Page
{
public:
	void Draw(Store&, const Edits&) override { std::printf("  (a page drawn by hand)\n"); }
};

int main()
{
	const Section audio { "Audio.Mixer", { { "Volume", 0.8f, 0.0f, 1.0f }, { "Pitch", 1.0f, 0.5f, 2.0f } } };
	const Section layers { "Scene.Layers", {} };
	std::map<std::string, std::function<std::unique_ptr<Page>(const Section&)>> custom;
	custom["Scene.Layers"] = [](const Section&) { return std::make_unique<CustomPage>(); };

	Store store;
	for (const Section* section : { &audio, &layers })
	{
		const auto found = custom.find(section->Id);
		std::unique_ptr<Page> page = found != custom.end() ? found->second(*section) : std::make_unique<GenericPage>(*section);
		std::printf("%s\n", section->Id.c_str());
		const std::vector<Edits> frames = { {}, {}, { { "Volume", 0.5f } }, { { "Volume", 3.0f } } };
		for (size_t frame = 0; frame < frames.size(); frame++)
		{
			std::printf(" frame %zu\n", frame + 1);
			page->Draw(store, frames[frame]);
		}
		if (const auto* generic = dynamic_cast<const GenericPage*>(page.get()))
			std::printf(" reads of the store: %d\n", generic->GetReads());
	}
	return 0;
}
