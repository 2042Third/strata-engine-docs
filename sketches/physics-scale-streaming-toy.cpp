#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <deque>

// A pool of body slots: the room doubles while bodies arrive, up to a limit; beyond it bodies wait in order.
class BodyPool
{
public:
	BodyPool(uint32_t room, uint32_t limit)
		: m_Room(room), m_Limit(limit)
	{
	}

	// Gives the body a slot, or queues it when the pool is at its limit.
	void Create(uint32_t id)
	{
		if (m_Used >= m_Limit)
		{
			m_Waiters.push_back(id);
			return;
		}
		if (m_Used >= m_Room)
		{
			m_Room = std::min(m_Room * 2, m_Limit);
			m_Growths++;
		}
		m_Used++;
	}

	// Frees a slot and hands it to the body that waited longest.
	void Destroy()
	{
		m_Used--;
		if (m_Waiters.empty())
			return;
		const uint32_t id = m_Waiters.front();
		m_Waiters.pop_front();
		m_Used++;
		std::printf("body %u leaves the queue\n", id);
	}

	void Print() const
	{
		std::printf("used %u, room %u, growths %u, waiting %zu\n", m_Used, m_Room, m_Growths, m_Waiters.size());
	}

private:
	uint32_t m_Room;
	uint32_t m_Limit;
	uint32_t m_Used = 0;
	uint32_t m_Growths = 0;
	std::deque<uint32_t> m_Waiters;
};

int main()
{
	BodyPool pool(4, 8);
	for (uint32_t id = 0; id < 10; id++)
		pool.Create(id);
	pool.Print();
	pool.Destroy();
	pool.Destroy();
	pool.Destroy();
	pool.Print();
	return 0;
}
