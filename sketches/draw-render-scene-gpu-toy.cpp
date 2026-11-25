#include <cstdint>
#include <cstdio>
#include <vector>

struct Change
{
	uint64_t Version = 0;
	uint32_t Index = 0;
};

// The CPU side: values, and a short log that says which index changed at which version.
class Scene
{
public:
	static constexpr size_t c_MaxLog = 4;

	void Set(uint32_t index, int value)
	{
		if (index >= m_Values.size())
			m_Values.resize(index + 1, 0);
		m_Values[index] = value;
		m_Log.push_back({ ++m_Version, index });
		if (m_Log.size() > c_MaxLog)
		{
			// The reader that is older than the dropped entry can no longer follow the log.
			m_Floor = m_Log.front().Version;
			m_Log.erase(m_Log.begin());
		}
	}

	// Appends the indices changed after sinceVersion; false when the log does not reach back that far.
	bool GetChanges(uint64_t sinceVersion, std::vector<uint32_t>& outIndices) const
	{
		if (sinceVersion < m_Floor)
			return false;
		for (const Change& change : m_Log)
		{
			if (change.Version > sinceVersion)
				outIndices.push_back(change.Index);
		}
		return true;
	}

	uint64_t GetVersion() const { return m_Version; }
	const std::vector<int>& GetValues() const { return m_Values; }

private:
	std::vector<int> m_Values;
	std::vector<Change> m_Log;
	uint64_t m_Version = 0;
	uint64_t m_Floor = 0;
};

// The "GPU" side: a copy that follows the log and counts the elements it was sent.
class Mirror
{
public:
	uint32_t Update(const Scene& scene)
	{
		if (m_Initialized && scene.GetVersion() == m_Version)
			return 0;
		std::vector<uint32_t> changes;
		const bool followed = m_Initialized && scene.GetChanges(m_Version, changes);
		if (!followed)
		{
			m_Gpu = scene.GetValues();
			m_Version = scene.GetVersion();
			m_Initialized = true;
			return static_cast<uint32_t>(m_Gpu.size());
		}
		m_Gpu.resize(scene.GetValues().size(), 0);
		for (const uint32_t index : changes)
			m_Gpu[index] = scene.GetValues()[index];
		m_Version = scene.GetVersion();
		return static_cast<uint32_t>(changes.size());
	}

	bool Matches(const Scene& scene) const { return m_Gpu == scene.GetValues(); }

private:
	std::vector<int> m_Gpu;
	uint64_t m_Version = 0;
	bool m_Initialized = false;
};

int main()
{
	Scene scene;
	Mirror mirror;
	scene.Set(0, 10);
	scene.Set(1, 20);
	scene.Set(2, 30);
	std::printf("first update sent %u elements\n", mirror.Update(scene));
	scene.Set(1, 25);
	std::printf("one change sent %u element\n", mirror.Update(scene));
	std::printf("no change sent %u elements\n", mirror.Update(scene));
	for (int value = 1; value <= 5; value++)
		scene.Set(0, value);
	std::printf("five changes, a log of four, sent %u elements\n", mirror.Update(scene));
	std::printf("the copy matches: %s\n", mirror.Matches(scene) ? "yes" : "no");
	return 0;
}
