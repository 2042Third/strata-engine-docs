#include <cstdint>
#include <cstdio>
#include <iterator>
#include <list>
#include <string>
#include <unordered_map>

namespace
{

	struct Entry
	{
		std::string Name;
		uint64_t Bytes = 0;
	};

	// Keeps named things within a byte budget: the one requested longest ago goes first.
	class LruCache
	{
	public:
		explicit LruCache(uint64_t budget)
			: m_Budget(budget)
		{
		}

		void Request(const std::string& name, uint64_t bytes)
		{
			auto found = m_Lookup.find(name);
			if (found != m_Lookup.end())
			{
				// A hit moves the node to the back of the list; no node is copied.
				m_Order.splice(m_Order.end(), m_Order, found->second);
				return;
			}
			m_Order.push_back(Entry { name, bytes });
			m_Lookup[name] = std::prev(m_Order.end());
			m_Resident += bytes;
			EvictToFit();
		}

		void Print() const
		{
			std::printf("resident %llu of %llu:", static_cast<unsigned long long>(m_Resident), static_cast<unsigned long long>(m_Budget));
			for (const Entry& entry : m_Order)
				std::printf(" %s", entry.Name.c_str());
			std::printf("\n");
		}

	private:
		void EvictToFit()
		{
			// The newest entry stays even when it alone is over the budget.
			while (m_Resident > m_Budget && m_Order.size() > 1)
			{
				const Entry& oldest = m_Order.front();
				std::printf("evict %s (%llu)\n", oldest.Name.c_str(), static_cast<unsigned long long>(oldest.Bytes));
				m_Resident -= oldest.Bytes;
				m_Lookup.erase(oldest.Name);
				m_Order.pop_front();
			}
		}

	private:
		uint64_t m_Budget = 0;
		uint64_t m_Resident = 0;
		std::list<Entry> m_Order; // Least recently requested first
		std::unordered_map<std::string, std::list<Entry>::iterator> m_Lookup;
	};

}

int main()
{
	LruCache cache(10);
	cache.Request("A", 4);
	cache.Request("B", 4);
	cache.Request("A", 4);
	cache.Request("C", 4);
	cache.Print();
	cache.Request("D", 4);
	cache.Print();
	return 0;
}
