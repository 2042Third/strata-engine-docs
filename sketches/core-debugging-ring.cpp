// A ring of log entries with sequence numbers, and a reader that asks for what came after the last number it saw.
#include <cstdint>
#include <cstdio>
#include <deque>
#include <string>
#include <vector>

struct Entry
{
	uint64_t Sequence = 0;
	std::string Message;
};

class Ring
{
public:
	explicit Ring(size_t capacity)
		: m_Capacity(capacity)
	{
	}

	void Push(const std::string& message)
	{
		if (m_Entries.size() >= m_Capacity)
			m_Entries.pop_front(); // the oldest entry is overwritten
		m_Entries.push_back({ m_NextSequence++, message });
	}

	std::vector<Entry> GetEntries(uint64_t afterSequence) const
	{
		std::vector<Entry> result;
		for (const Entry& entry : m_Entries)
		{
			if (entry.Sequence > afterSequence)
				result.push_back(entry);
		}
		return result;
	}
private:
	std::deque<Entry> m_Entries;
	size_t m_Capacity;
	uint64_t m_NextSequence = 1;
};

int main()
{
	Ring ring(3);
	for (const char* message : { "one", "two", "three", "four", "five" })
		ring.Push(message);

	const uint64_t lastSeen = 1; // the reader has shown entry 1 and nothing after it
	const std::vector<Entry> entries = ring.GetEntries(lastSeen);
	for (const Entry& entry : entries)
		std::printf("%llu %s\n", static_cast<unsigned long long>(entry.Sequence), entry.Message.c_str());
	const uint64_t missed = entries.front().Sequence - lastSeen - 1;
	std::printf("entries lost between two reads: %llu\n", static_cast<unsigned long long>(missed));
	return 0;
}
