// A toy range allocator: first fit, free ranges that merge, and a compaction that moves blocks down into holes.
#include <cstdint>
#include <cstdio>
#include <map>
#include <vector>

struct Move
{
	uint32_t From;
	uint32_t To;
	uint32_t Size;
};

class ToyAllocator
{
public:
	explicit ToyAllocator(uint32_t capacity)
		: m_Capacity(capacity)
	{
		m_Free[0] = capacity;
	}

	// The lowest offset whose free range holds `size` units, or ~0u when none does.
	uint32_t Allocate(uint32_t size)
	{
		for (const auto& [offset, freeSize] : m_Free)
		{
			if (freeSize < size)
				continue;
			const uint32_t start = offset;
			const uint32_t rest = freeSize - size;
			m_Free.erase(start);
			if (rest > 0)
				m_Free[start + size] = rest;
			m_Used[start] = size;
			return start;
		}
		return ~0u;
	}

	void Free(uint32_t offset)
	{
		uint32_t size = m_Used.at(offset);
		m_Used.erase(offset);
		const auto next = m_Free.find(offset + size);
		if (next != m_Free.end())
		{
			size += next->second;
			m_Free.erase(next);
		}
		auto previous = m_Free.lower_bound(offset);
		if (previous != m_Free.begin() && (--previous)->first + previous->second == offset)
			previous->second += size;
		else
			m_Free[offset] = size;
	}

	// The free units outside the largest free range, as a share of the capacity.
	float GetScatteredFreeShare() const
	{
		uint32_t total = 0;
		uint32_t largest = 0;
		for (const auto& [offset, size] : m_Free)
		{
			total += size;
			largest = size > largest ? size : largest;
		}
		return static_cast<float>(total - largest) / static_cast<float>(m_Capacity);
	}

	// Moves the highest block into the lowest hole that holds it, until no block can move down.
	std::vector<Move> Compact()
	{
		std::vector<Move> moves;
		for (bool moved = true; moved;)
		{
			moved = false;
			for (auto block = m_Used.rbegin(); block != m_Used.rend() && !moved; ++block)
			{
				const uint32_t from = block->first;
				const uint32_t size = block->second;
				Free(from);
				const uint32_t to = Allocate(size);
				if (to != from)
				{
					moves.push_back(Move { from, to, size });
					moved = true;
				}
			}
		}
		return moves;
	}

private:
	uint32_t m_Capacity;
	std::map<uint32_t, uint32_t> m_Free; // Offset to size
	std::map<uint32_t, uint32_t> m_Used; // Offset to size
};

int main()
{
	ToyAllocator allocator(1024);
	uint32_t offsets[8];
	for (uint32_t index = 0; index < 8; index++)
		offsets[index] = allocator.Allocate(128);
	for (uint32_t index = 1; index < 8; index += 2)
		allocator.Free(offsets[index]);
	std::printf("scattered share before: %.3f\n", allocator.GetScatteredFreeShare());
	for (const Move& move : allocator.Compact())
		std::printf("move %u units from %u to %u\n", move.Size, move.From, move.To);
	std::printf("scattered share after: %.3f\n", allocator.GetScatteredFreeShare());
}
