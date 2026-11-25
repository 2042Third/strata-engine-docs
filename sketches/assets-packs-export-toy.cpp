// A toy asset pack: a header, the entries' bytes, one table at the end guarded by one checksum, and mounts.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <utility>
#include <vector>

namespace
{
	using Bytes = std::vector<uint8_t>;
	using Source = std::pair<std::string, std::string>;

	constexpr uint32_t c_Magic = 0x4B505453;

	struct Header
	{
		uint32_t Magic = 0;
		uint32_t EntryCount = 0;
		uint64_t TablesOffset = 0;
		uint32_t TablesChecksum = 0;
		uint32_t Reserved = 0;
	};

	struct Record
	{
		uint64_t Offset = 0;
		uint64_t Size = 0;
		char Name[24] = {};
	};

	uint32_t Crc32c(const uint8_t* data, size_t size)
	{
		uint32_t crc = 0xFFFFFFFFu;
		for (size_t index = 0; index < size; index++)
		{
			crc ^= data[index];
			for (int bit = 0; bit < 8; bit++)
				crc = (crc >> 1) ^ (0x82F63B78u & (0u - (crc & 1u)));
		}
		return ~crc;
	}

	Bytes WritePack(const std::vector<Source>& sources)
	{
		Bytes file(sizeof(Header));
		std::vector<Record> records;
		for (const Source& source : sources)
		{
			Record record;
			record.Offset = file.size();
			record.Size = source.second.size();
			std::memcpy(record.Name, source.first.data(), std::min(source.first.size(), sizeof(record.Name) - 1));
			file.insert(file.end(), source.second.begin(), source.second.end());
			records.push_back(record);
		}
		const uint8_t* tables = reinterpret_cast<const uint8_t*>(records.data());
		const size_t tableBytes = records.size() * sizeof(Record);
		Header header;
		header.Magic = c_Magic;
		header.EntryCount = static_cast<uint32_t>(records.size());
		header.TablesOffset = file.size();
		header.TablesChecksum = Crc32c(tables, tableBytes);
		file.insert(file.end(), tables, tables + tableBytes);
		std::memcpy(file.data(), &header, sizeof(header));
		return file;
	}

	bool ReadTables(const Bytes& file, std::vector<Record>& outRecords)
	{
		Header header;
		if (file.size() < sizeof(Header))
			return false;
		std::memcpy(&header, file.data(), sizeof(header));
		const size_t tableBytes = header.EntryCount * sizeof(Record);
		if (header.Magic != c_Magic || header.TablesOffset + tableBytes != file.size())
			return false;
		if (Crc32c(file.data() + header.TablesOffset, tableBytes) != header.TablesChecksum)
			return false;
		outRecords.resize(header.EntryCount);
		std::memcpy(outRecords.data(), file.data() + header.TablesOffset, tableBytes);
		return true;
	}
}

int main()
{
	const Bytes game = WritePack({ { "Level.scene", "ground,tree,hero" }, { "Hero.mat", "red" }, { "Tree.mat", "green" } });
	const Bytes patch = WritePack({ { "Hero.mat", "blue" } });
	std::printf("game pack: %zu bytes, patch pack: %zu bytes\n", game.size(), patch.size());

	std::map<std::string, std::string> mounted;
	for (const Bytes* pack : { &game, &patch })
	{
		std::vector<Record> records;
		if (!ReadTables(*pack, records))
			return 1;
		for (const Record& record : records)
			mounted[record.Name] = std::string(pack->begin() + record.Offset, pack->begin() + record.Offset + record.Size);
	}
	for (const auto& [name, content] : mounted)
		std::printf("%s = %s\n", name.c_str(), content.c_str());

	Bytes damaged = game;
	damaged[damaged.size() - 5] ^= 0x01;
	std::vector<Record> records;
	std::printf("damaged table accepted: %s\n", ReadTables(damaged, records) ? "yes" : "no");
	return 0;
}
