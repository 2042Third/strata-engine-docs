// A toy editor world: crates live in cells, an edit moves a crate into the cell of its new position and
// marks the cells it left and joined, and a save writes the marked cells first and the index second.
#include <cmath>
#include <compare>
#include <cstdio>
#include <set>
#include <string>
#include <vector>

struct CellKey
{
	int X = 0;
	int Z = 0;
	auto operator<=>(const CellKey& other) const = default;
};

struct Crate
{
	std::string Name;
	float X = 0.0f;
	float Z = 0.0f;
	CellKey Cell;
};

class ToyWorld
{
public:
	void Add(const std::string& name, float x, float z)
	{
		m_Crates.push_back({ name, x, z, CellAt(x, z) });
		m_Dirty.insert(m_Crates.back().Cell);
	}

	void Move(const std::string& name, float x, float z)
	{
		for (Crate& crate : m_Crates)
		{
			if (crate.Name != name)
				continue;
			m_Dirty.insert(crate.Cell); // the cell it leaves changes
			crate.X = x;
			crate.Z = z;
			crate.Cell = CellAt(x, z); // re-celling: the cell of the new position
			m_Dirty.insert(crate.Cell); // the cell it joins changes
		}
	}

	void Save()
	{
		std::printf("save: %zu dirty cell(s) of %zu crates\n", m_Dirty.size(), m_Crates.size());
		for (const CellKey& key : m_Dirty)
			std::printf("  write cell (%d, %d)\n", key.X, key.Z);
		std::printf("  write the world index\n"); // second, once the cell files exist
		m_Dirty.clear(); // saved only now
	}

private:
	static CellKey CellAt(float x, float z)
	{
		return { static_cast<int>(std::floor(x / c_CellSize)), static_cast<int>(std::floor(z / c_CellSize)) };
	}

	static constexpr float c_CellSize = 64.0f;
	std::vector<Crate> m_Crates;
	std::set<CellKey> m_Dirty;
};

int main()
{
	ToyWorld world;
	world.Add("A", 10.0f, 10.0f);
	world.Add("B", 70.0f, 10.0f);
	world.Add("C", 200.0f, 200.0f);
	world.Save();
	world.Move("A", 66.0f, 10.0f);
	world.Save();
	world.Move("B", 80.0f, 10.0f);
	world.Save();
	return 0;
}
