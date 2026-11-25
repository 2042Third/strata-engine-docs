#include <cstdint>
#include <cstdio>
#include <functional>
#include <string>
#include <unordered_map>

struct SourceFile
{
	std::string Bytes;
	int64_t Time = 0;
};

struct Record
{
	uint32_t ImporterVersion = 0;
	size_t SettingsHash = 0;
	size_t Size = 0;
	int64_t Time = 0; // 0: unknown, the contents are compared
	size_t ContentHash = 0;
};

class ToyImportCache
{
public:
	void Get(const std::string& path, const SourceFile& source, uint32_t version, const std::string& settings, int64_t now)
	{
		const size_t settingsHash = std::hash<std::string> {}(settings);
		const char* reason = "no record";
		auto it = m_Records.find(path);
		if (it != m_Records.end())
			reason = FindStaleReason(it->second, source, version, settingsHash, now);
		if (!reason)
		{
			std::printf("%s: current\n", path.c_str());
			return;
		}
		std::printf("%s: import (%s)\n", path.c_str(), reason);
		m_ImportCount++;
		Record record;
		record.ImporterVersion = version;
		record.SettingsHash = settingsHash;
		record.Size = source.Bytes.size();
		record.Time = GetRecordableTime(source.Time, now);
		record.ContentHash = std::hash<std::string> {}(source.Bytes);
		m_Records[path] = record;
	}

	int GetImportCount() const { return m_ImportCount; }
private:
	// A time within two ticks of now cannot vouch for the contents: the file may change again in the same tick.
	static int64_t GetRecordableTime(int64_t time, int64_t now) { return now - time < 2 ? 0 : time; }

	static const char* FindStaleReason(Record& record, const SourceFile& source, uint32_t version, size_t settingsHash, int64_t now)
	{
		if (record.ImporterVersion != version)
			return "importer version";
		if (record.SettingsHash != settingsHash)
			return "settings";
		if (record.Size != source.Bytes.size())
			return "size";
		if (record.Time == source.Time)
			return nullptr;
		if (record.ContentHash != std::hash<std::string> {}(source.Bytes))
			return "contents";
		record.Time = GetRecordableTime(source.Time, now); // Only the time changed: compare contents once
		return nullptr;
	}
private:
	std::unordered_map<std::string, Record> m_Records;
	int m_ImportCount = 0;
};

int main()
{
	ToyImportCache cache;
	SourceFile file { "AAAA", 10 };
	cache.Get("Wall.png", file, 1, "mips=on", 100);
	cache.Get("Wall.png", file, 1, "mips=on", 101);
	cache.Get("Wall.png", file, 1, "mips=off", 102);
	file.Time = 50; // Touched: a copy or a checkout
	cache.Get("Wall.png", file, 1, "mips=off", 103);
	file = { "BBBB", 200 }; // Edited at tick 200
	cache.Get("Wall.png", file, 1, "mips=off", 200);
	file = { "CCCC", 200 }; // Edited again in the same tick, same size
	cache.Get("Wall.png", file, 1, "mips=off", 200);
	cache.Get("Wall.png", file, 2, "mips=off", 300);
	std::printf("imports: %d\n", cache.GetImportCount());
	return 0;
}
