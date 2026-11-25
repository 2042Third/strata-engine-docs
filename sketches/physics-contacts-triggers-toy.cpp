// A toy of Strata's contact folding: shape contacts are counted per entity pair, and a pair begins
// with its first contact and ends with its last one. Events wait in a list until the step is over.

#include <cstdio>
#include <map>
#include <utility>
#include <vector>

struct Event
{
	bool IsBegin = true;
	int First = 0;
	int Second = 0;
};

class PairCounter
{
public:
	void CountBegin(int a, int b)
	{
		const auto key = MakeKey(a, b);
		if (m_Counts[key]++ == 0)
			m_Pending.push_back({ true, key.first, key.second });
	}

	void CountEnd(int a, int b)
	{
		const auto key = MakeKey(a, b);
		const auto it = m_Counts.find(key);
		if (it == m_Counts.end())
			return;
		if (--it->second == 0)
		{
			m_Pending.push_back({ false, key.first, key.second });
			m_Counts.erase(it);
		}
	}

	// The step is over: hand out the events and start a new list.
	std::vector<Event> Take()
	{
		std::vector<Event> events = std::move(m_Pending);
		m_Pending.clear();
		return events;
	}

private:
	static std::pair<int, int> MakeKey(int a, int b) { return a < b ? std::make_pair(a, b) : std::make_pair(b, a); }

	std::map<std::pair<int, int>, int> m_Counts;
	std::vector<Event> m_Pending;
};

int main()
{
	// Entity 0 is the ground, entity 1 a bench with two legs, entity 2 a ball.
	PairCounter counter;
	const int ground = 0;
	const int bench = 1;
	const int ball = 2;

	counter.CountBegin(bench, ground); // First leg lands.
	counter.CountBegin(ground, bench); // Second leg lands: same pair, no new event.
	counter.CountBegin(ball, ground);
	for (const Event& event : counter.Take())
		std::printf("step 1: %s %d-%d\n", event.IsBegin ? "Begin" : "End  ", event.First, event.Second);

	counter.CountEnd(bench, ground); // One leg lifts: the pair still touches.
	counter.CountEnd(ground, ball);
	for (const Event& event : counter.Take())
		std::printf("step 2: %s %d-%d\n", event.IsBegin ? "Begin" : "End  ", event.First, event.Second);

	counter.CountEnd(bench, ground); // The last leg lifts.
	for (const Event& event : counter.Take())
		std::printf("step 3: %s %d-%d\n", event.IsBegin ? "Begin" : "End  ", event.First, event.Second);
	return 0;
}
