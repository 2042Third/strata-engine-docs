#include <cstdint>
#include <cstdio>
#include <vector>

enum class State : uint8_t
{
	Absent,
	Free,
	Split,
	Used
};

struct Tile
{
	uint32_t X = 0;
	uint32_t Y = 0;
	uint32_t Size = 0;
};

// Level 0 is the whole atlas; level L has 4^L nodes, in Morton order, so node i has the children 4i to 4i + 3.
class ToyAtlas
{
public:
	ToyAtlas(uint32_t atlasSize, uint32_t minTile)
		: m_AtlasSize(atlasSize)
	{
		size_t count = 1;
		for (uint32_t size = atlasSize; size >= minTile; size /= 2, count *= 4)
			m_Levels.emplace_back(count, State::Absent);
		m_Levels[0][0] = State::Free;
	}

	Tile Allocate(uint32_t size)
	{
		const uint32_t level = GetLevel(size);
		// The first free block of the size, else of the next larger size, and so on.
		for (uint32_t search = level + 1; search-- > 0;)
		{
			std::vector<State>& nodes = m_Levels[search];
			size_t node = 0;
			while (node < nodes.size() && nodes[node] != State::Free)
				node++;
			if (node == nodes.size())
				continue;
			for (uint32_t split = search; split < level; split++, node *= 4)
			{
				m_Levels[split][node] = State::Split;
				for (size_t child = 0; child < 4; child++)
					m_Levels[split + 1][node * 4 + child] = State::Free;
			}
			m_Levels[level][node] = State::Used;
			return GetTile(level, node);
		}
		return {};
	}

	void Free(const Tile& tile)
	{
		uint32_t level = GetLevel(tile.Size);
		size_t index = 0;
		for (uint32_t bit = 0; bit < 16; bit++)
			index |= (((tile.X / tile.Size) >> bit) & 1u) << (2 * bit) | (((tile.Y / tile.Size) >> bit) & 1u) << (2 * bit + 1);
		m_Levels[level][index] = State::Free;
		// Four free quarters make a free block again.
		for (; level > 0; level--, index /= 4)
		{
			const size_t first = index / 4 * 4;
			std::vector<State>& nodes = m_Levels[level];
			if (nodes[first] != State::Free || nodes[first + 1] != State::Free || nodes[first + 2] != State::Free || nodes[first + 3] != State::Free)
				break;
			for (size_t child = 0; child < 4; child++)
				nodes[first + child] = State::Absent;
			m_Levels[level - 1][first / 4] = State::Free;
		}
	}

private:
	uint32_t GetLevel(uint32_t size) const
	{
		uint32_t level = 0;
		for (uint32_t levelSize = m_AtlasSize; levelSize > size; levelSize /= 2)
			level++;
		return level;
	}

	Tile GetTile(uint32_t level, size_t index) const
	{
		uint32_t x = 0;
		uint32_t y = 0;
		for (uint32_t bit = 0; bit < 16; bit++)
		{
			x |= static_cast<uint32_t>((index >> (2 * bit)) & 1u) << bit;
			y |= static_cast<uint32_t>((index >> (2 * bit + 1)) & 1u) << bit;
		}
		const uint32_t size = m_AtlasSize >> level;
		return { x * size, y * size, size };
	}

	uint32_t m_AtlasSize;
	std::vector<std::vector<State>> m_Levels;
};

// Halves one size at a time, from the least relevant entry toward the most relevant, until the areas fit the budget.
void FitTileSizes(std::vector<uint32_t>& sizes, const std::vector<uint32_t>& tileCounts, uint32_t minTile, uint64_t budget)
{
	const auto getArea = [&]()
	{
		uint64_t total = 0;
		for (size_t entry = 0; entry < sizes.size(); entry++)
			total += static_cast<uint64_t>(tileCounts[entry]) * sizes[entry] * sizes[entry];
		return total;
	};
	size_t cursor = sizes.size();
	for (bool stepped = true; stepped && getArea() > budget;)
	{
		stepped = false;
		for (size_t tried = 0; tried < sizes.size() && !stepped; tried++)
		{
			cursor = cursor == 0 ? sizes.size() - 1 : cursor - 1;
			if (sizes[cursor] > minTile)
			{
				sizes[cursor] /= 2;
				stepped = true;
			}
		}
	}
}

int main()
{
	ToyAtlas atlas(1024, 128);
	const Tile a = atlas.Allocate(512);
	const Tile b = atlas.Allocate(256);
	const Tile c = atlas.Allocate(256);
	const Tile d = atlas.Allocate(128);
	for (const Tile& tile : { a, b, c, d })
		std::printf("tile %u at (%u, %u)\n", tile.Size, tile.X, tile.Y);
	atlas.Free(c);
	atlas.Free(b);
	atlas.Free(d);
	const Tile merged = atlas.Allocate(512);
	std::printf("after the frees, a 512 tile lands at (%u, %u)\n", merged.X, merged.Y);

	// A 512 atlas fits 7/8 of its area: 229376 texels.
	std::vector<uint32_t> spots = { 256, 256, 256, 256 };
	FitTileSizes(spots, { 1, 1, 1, 1 }, 128, 229376);
	std::printf("four spot lights: %u %u %u %u\n", spots[0], spots[1], spots[2], spots[3]);
	std::vector<uint32_t> mixed = { 256, 256, 256 };
	FitTileSizes(mixed, { 6, 1, 1 }, 128, 229376);
	std::printf("a point light and two spot lights: %u %u %u\n", mixed[0], mixed[1], mixed[2]);
	return 0;
}
