// Handles made of an index and a version, recycled after destruction as an EnTT identifier is (20 bits and 12 bits).
#include <cstdint>
#include <cstdio>
#include <vector>

namespace
{
	constexpr uint32_t c_IndexBits = 20;
	constexpr uint32_t c_IndexMask = (1u << c_IndexBits) - 1;
	constexpr uint32_t c_VersionMask = 0xFFF;

	class Handles
	{
	public:
		uint32_t Create()
		{
			uint32_t index = 0;
			if (m_Free.empty())
			{
				index = static_cast<uint32_t>(m_Versions.size());
				m_Versions.push_back(0);
			}
			else
			{
				index = m_Free.back();
				m_Free.pop_back();
			}
			return (m_Versions[index] << c_IndexBits) | index;
		}

		void Destroy(uint32_t handle)
		{
			const uint32_t index = handle & c_IndexMask;
			uint32_t next = m_Versions[index] + 1;
			if (next == c_VersionMask) // the largest version stays unused, as in EnTT
				next = 0;
			m_Versions[index] = next;
			m_Free.push_back(index);
		}

		bool Valid(uint32_t handle) const
		{
			const uint32_t index = handle & c_IndexMask;
			return index < m_Versions.size() && m_Versions[index] == (handle >> c_IndexBits);
		}
	private:
		std::vector<uint32_t> m_Versions; // the current version of each index
		std::vector<uint32_t> m_Free;     // indices waiting to be reused
	};
}

int main()
{
	Handles handles;
	const uint32_t first = handles.Create();
	const uint32_t second = handles.Create();
	handles.Destroy(first);
	const uint32_t third = handles.Create();
	std::printf("first %u, second %u, third %u\n", first, second, third);
	std::printf("first is valid: %d, third is valid: %d\n", handles.Valid(first), handles.Valid(third));

	uint32_t latest = third;
	for (int round = 0; round < 4094; round++)
	{
		handles.Destroy(latest);
		latest = handles.Create();
	}
	std::printf("after 4095 reuses of index 0, first is valid again: %d\n", handles.Valid(first));
	return 0;
}
