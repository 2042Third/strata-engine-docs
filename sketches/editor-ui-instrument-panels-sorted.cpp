#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

struct Asset
{
	std::string Name;
	int Bytes = 0;
};

// Rows are sorted only when the data version or the sort column changes.
class SortedPanel
{
public:
	void OnUpdate(const std::vector<Asset>& assets, uint64_t version, bool byBytes)
	{
		if (version == m_Version && byBytes == m_ByBytes)
			return;
		m_Version = version;
		m_ByBytes = byBytes;
		m_Rows = assets;
		std::sort(m_Rows.begin(), m_Rows.end(), [&](const Asset& left, const Asset& right)
		{
			m_Comparisons++;
			return byBytes ? left.Bytes > right.Bytes : left.Name < right.Name;
		});
	}

	size_t GetComparisons() const { return m_Comparisons; }
	const std::vector<Asset>& GetRows() const { return m_Rows; }

private:
	uint64_t m_Version = UINT64_MAX;
	bool m_ByBytes = false;
	std::vector<Asset> m_Rows;
	size_t m_Comparisons = 0;
};

int main()
{
	std::vector<Asset> assets = { { "rock", 300 }, { "tree", 900 }, { "bush", 120 }, { "sky", 500 } };
	SortedPanel panel;
	for (int frame = 0; frame < 100; frame++)
		panel.OnUpdate(assets, 1, false);
	const size_t afterIdle = panel.GetComparisons();
	panel.OnUpdate(assets, 1, true);
	std::printf("100 frames, one sort: %zu comparisons in total\n", afterIdle);
	std::printf("after the sort changed: %zu more, first row %s\n", panel.GetComparisons() - afterIdle, panel.GetRows()[0].Name.c_str());
	return 0;
}
