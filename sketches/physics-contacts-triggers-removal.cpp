// The toy with one more rule: an entity that leaves the simulation ends every pair it is in,
// so every Begin still gets exactly one End.

#include <cstdio>
#include <map>
#include <utility>
#include <vector>

class PairCounter
{
public:
	void CountBegin(int a, int b)
	{
		const auto key = MakeKey(a, b);
		if (m_Counts[key]++ == 0)
			std::printf("Begin %d-%d\n", key.first, key.second);
	}

	void CountEnd(int a, int b)
	{
		const auto key = MakeKey(a, b);
		const auto it = m_Counts.find(key);
		if (it == m_Counts.end())
			return;
		if (--it->second == 0)
		{
			std::printf("End   %d-%d\n", key.first, key.second);
			m_Counts.erase(it);
		}
	}

	// The entity is destroyed while touching: its contacts will never report an end.
	void Remove(int entity)
	{
		for (auto it = m_Counts.begin(); it != m_Counts.end();)
		{
			if (it->first.first == entity || it->first.second == entity)
			{
				std::printf("End   %d-%d (removed)\n", it->first.first, it->first.second);
				it = m_Counts.erase(it);
			}
			else
				++it;
		}
	}

private:
	static std::pair<int, int> MakeKey(int a, int b) { return a < b ? std::make_pair(a, b) : std::make_pair(b, a); }

	std::map<std::pair<int, int>, int> m_Counts;
};

int main()
{
	PairCounter counter;
	counter.CountBegin(0, 5); // Entity 5 touches the trigger 0 with two shapes.
	counter.CountBegin(5, 0);
	counter.CountBegin(0, 6);
	counter.Remove(5);
	counter.CountEnd(0, 6);
	counter.CountEnd(0, 5); // A late End of the removed entity finds no pair and is ignored.
	return 0;
}
