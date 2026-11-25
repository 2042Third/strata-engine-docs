#include <cstdint>
#include <cstdio>
#include <iterator>
#include <list>
#include <memory>
#include <string>
#include <unordered_map>
#include <utility>

namespace
{

	struct Entry
	{
		std::string Name;
		uint64_t Bytes = 0;
		uint64_t LastFrame = 0;
		uint32_t Pins = 0;
		std::shared_ptr<int> Data = std::make_shared<int>(0);
	};

	// The toy cache with Strata's protections: a grace window, pins and objects held outside.
	class ProtectedCache
	{
	public:
		ProtectedCache(uint64_t budget, uint64_t graceFrames)
			: m_Budget(budget), m_GraceFrames(graceFrames)
		{
		}

		std::shared_ptr<int> Request(const std::string& name, uint64_t bytes, uint64_t frame)
		{
			auto found = m_Lookup.find(name);
			if (found != m_Lookup.end())
			{
				found->second->LastFrame = frame;
				m_Order.splice(m_Order.end(), m_Order, found->second);
				return found->second->Data;
			}
			Entry entry;
			entry.Name = name;
			entry.Bytes = bytes;
			entry.LastFrame = frame;
			m_Order.push_back(std::move(entry));
			m_Lookup[name] = std::prev(m_Order.end());
			m_Resident += bytes;
			return m_Order.back().Data;
		}

		void Pin(const std::string& name)
		{
			m_Lookup.at(name)->Pins++;
		}

		void EvictToFit(uint64_t frame)
		{
			for (auto it = m_Order.begin(); it != m_Order.end() && m_Resident > m_Budget;)
			{
				if (frame - it->LastFrame <= m_GraceFrames)
					break; // Every later entry was requested even more recently
				const bool protectedEntry = it->Pins > 0 || it->Data.use_count() > 1;
				if (protectedEntry)
				{
					++it;
					continue;
				}
				std::printf("frame %llu: evict %s\n", static_cast<unsigned long long>(frame), it->Name.c_str());
				m_Resident -= it->Bytes;
				m_Lookup.erase(it->Name);
				it = m_Order.erase(it);
			}
		}

	private:
		uint64_t m_Budget = 0;
		uint64_t m_GraceFrames = 0;
		uint64_t m_Resident = 0;
		std::list<Entry> m_Order;
		std::unordered_map<std::string, std::list<Entry>::iterator> m_Lookup;
	};

}

int main()
{
	ProtectedCache cache(8, 1);
	cache.Request("A", 4, 1);
	std::shared_ptr<int> held = cache.Request("B", 4, 1);
	cache.Request("C", 4, 1);
	cache.Pin("A");
	for (uint64_t frame = 1; frame <= 3; frame++)
		cache.EvictToFit(frame);
	return 0;
}
