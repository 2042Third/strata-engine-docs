// A toy audio system: one record per entity, a comparison with the values applied last, pruning by the update
// that last saw the entity. No sound is made; the "source" only prints what the system tells it.
#include <bit>
#include <cstdint>
#include <cstdio>
#include <limits>
#include <map>
#include <vector>

namespace
{

	struct Component
	{
		int Id = 0;
		float Volume = 1.0f;
		bool Loop = false;
	};

	struct Record
	{
		Component Applied;
		uint64_t SeenUpdate = 0;
	};

	bool IsSameFloat(float a, float b)
	{
		return std::bit_cast<uint32_t>(a) == std::bit_cast<uint32_t>(b);
	}

	class ToyAudioSystem
	{
	public:
		void Update(const std::vector<Component>& components)
		{
			m_UpdateIndex++;
			for (const Component& component : components)
			{
				auto it = m_Records.find(component.Id);
				if (it == m_Records.end())
				{
					std::printf("update %llu: create source %d (volume %.2f)\n", static_cast<unsigned long long>(m_UpdateIndex), component.Id, component.Volume);
					it = m_Records.emplace(component.Id, Record { component, m_UpdateIndex }).first;
					continue;
				}
				Record& record = it->second;
				record.SeenUpdate = m_UpdateIndex;
				if (!IsSameFloat(component.Volume, record.Applied.Volume))
					std::printf("update %llu: source %d volume %.2f\n", static_cast<unsigned long long>(m_UpdateIndex), component.Id, component.Volume);
				if (component.Loop != record.Applied.Loop)
					std::printf("update %llu: source %d loop %d\n", static_cast<unsigned long long>(m_UpdateIndex), component.Id, component.Loop ? 1 : 0);
				record.Applied = component;
			}
			std::erase_if(m_Records, [this](const auto& entry)
			{
				const bool gone = entry.second.SeenUpdate != m_UpdateIndex;
				if (gone)
					std::printf("update %llu: release source %d\n", static_cast<unsigned long long>(m_UpdateIndex), entry.first);
				return gone;
			});
		}
	private:
		std::map<int, Record> m_Records;
		uint64_t m_UpdateIndex = 0;
	};

}

int main()
{
	ToyAudioSystem system;
	const float notANumber = std::numeric_limits<float>::quiet_NaN();
	system.Update({ { 1, 1.0f, false }, { 2, 0.5f, false } });
	system.Update({ { 1, 0.4f, true }, { 2, 0.5f, false } });
	system.Update({ { 1, notANumber, true }, { 3, 1.0f, false } });
	system.Update({ { 1, notANumber, true }, { 3, 1.0f, false } });
	return 0;
}
