#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

// A journal that counts its changes: every Add raises the version.
struct Journal
{
	std::vector<std::string> Entries;
	uint64_t Version = 0;

	void Add(const std::string& text)
	{
		Entries.push_back(text);
		Version++;
	}
};

// A panel in the engine's shape: OnUpdate collects, Draw only reads what OnUpdate prepared.
class ToyPanel
{
public:
	explicit ToyPanel(bool cached)
		: m_Cached(cached)
	{
	}

	void OnUpdate(const Journal& journal, const std::string& filter)
	{
		// Idle frame: one number and one short key are compared, nothing else.
		if (m_Cached && journal.Version == m_Version && filter == m_Filter)
			return;
		m_Version = journal.Version;
		m_Filter = filter;
		m_Rows.clear();
		for (size_t index = 0; index < journal.Entries.size(); index++)
		{
			m_Visited++;
			if (filter.empty() || journal.Entries[index].find(filter) != std::string::npos)
				m_Rows.push_back(index);
		}
		m_Rebuilds++;
	}

	// A clipped list draws only the rows that fit on screen.
	size_t Draw(size_t firstRow, size_t rowsOnScreen) const
	{
		const size_t last = std::min(m_Rows.size(), firstRow + rowsOnScreen);
		return last > firstRow ? last - firstRow : 0;
	}

	size_t GetVisited() const { return m_Visited; }
	size_t GetRebuilds() const { return m_Rebuilds; }
	size_t GetRowCount() const { return m_Rows.size(); }

private:
	bool m_Cached;
	uint64_t m_Version = UINT64_MAX;
	std::string m_Filter;
	std::vector<size_t> m_Rows;
	size_t m_Visited = 0;
	size_t m_Rebuilds = 0;
};

int main()
{
	Journal journal;
	for (int index = 0; index < 10000; index++)
		journal.Add(index % 100 == 0 ? "scene.save" : "entity.move");

	ToyPanel cached(true);
	ToyPanel naive(false);
	size_t drawn = 0;
	for (int frame = 0; frame < 600; frame++)
	{
		if (frame == 300)
			journal.Add("scene.save");
		const std::string filter = frame >= 450 ? "save" : "";
		cached.OnUpdate(journal, filter);
		naive.OnUpdate(journal, filter);
		drawn += cached.Draw(0, 30);
	}
	std::printf("cached: %zu rebuilds, %zu entries visited, %zu rows left, %zu rows drawn\n", cached.GetRebuilds(), cached.GetVisited(),
		cached.GetRowCount(), drawn);
	std::printf("naive:  %zu rebuilds, %zu entries visited\n", naive.GetRebuilds(), naive.GetVisited());
	return 0;
}
