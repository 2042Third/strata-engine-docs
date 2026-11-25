// Random corruption of the toy cooked document: every changed byte must be refused.
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <random>
#include <set>
#include <string>
#include <vector>

namespace
{
	constexpr uint32_t c_Version = 1;
	constexpr uint32_t c_NoParent = 0xFFFFFFFFu;
	constexpr size_t c_HeaderBytes = 16;
	constexpr size_t c_RecordBytes = 12; // A u64 ID and a u32 parent index

	uint32_t Crc32C(const uint8_t* data, size_t size)
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

	struct Record
	{
		uint64_t Id;
		uint32_t Parent;
	};

	void Put(std::vector<uint8_t>& bytes, size_t offset, const void* value, size_t size)
	{
		std::memcpy(bytes.data() + offset, value, size);
	}

	std::vector<uint8_t> Write(const std::vector<Record>& records)
	{
		std::vector<uint8_t> bytes(c_HeaderBytes + records.size() * c_RecordBytes);
		for (size_t index = 0; index < records.size(); index++)
		{
			Put(bytes, c_HeaderBytes + index * c_RecordBytes, &records[index].Id, 8);
			Put(bytes, c_HeaderBytes + index * c_RecordBytes + 8, &records[index].Parent, 4);
		}
		const uint32_t count = static_cast<uint32_t>(records.size());
		const uint32_t crc = Crc32C(bytes.data() + c_HeaderBytes, bytes.size() - c_HeaderBytes);
		Put(bytes, 0, "TOYC", 4);
		Put(bytes, 4, &c_Version, 4);
		Put(bytes, 8, &count, 4);
		Put(bytes, 12, &crc, 4);
		return bytes;
	}

	// Returns an empty string when the bytes are a valid document, else the reason they are refused.
	std::string Check(const std::vector<uint8_t>& bytes)
	{
		if (bytes.size() < c_HeaderBytes)
			return "shorter than its header";
		uint32_t version = 0, count = 0, crc = 0;
		std::memcpy(&version, bytes.data() + 4, 4);
		std::memcpy(&count, bytes.data() + 8, 4);
		std::memcpy(&crc, bytes.data() + 12, 4);
		if (std::memcmp(bytes.data(), "TOYC", 4) != 0)
			return "wrong magic";
		if (version != c_Version)
			return "unsupported version";
		if ((bytes.size() - c_HeaderBytes) / c_RecordBytes != count || (bytes.size() - c_HeaderBytes) % c_RecordBytes != 0)
			return "count does not match the size";
		if (Crc32C(bytes.data() + c_HeaderBytes, bytes.size() - c_HeaderBytes) != crc)
			return "checksum does not match";
		std::set<uint64_t> seen;
		for (uint32_t index = 0; index < count; index++)
		{
			Record record {};
			std::memcpy(&record.Id, bytes.data() + c_HeaderBytes + index * c_RecordBytes, 8);
			std::memcpy(&record.Parent, bytes.data() + c_HeaderBytes + index * c_RecordBytes + 8, 4);
			if (record.Id == 0 || !seen.insert(record.Id).second)
				return "null or repeated ID";
			if (record.Parent != c_NoParent && record.Parent >= index)
				return "parent does not come before its entity";
		}
		return {};
	}
}

int main()
{
	std::vector<Record> records;
	for (uint32_t index = 0; index < 40; index++)
		records.push_back({ 100 + index, index == 0 ? c_NoParent : index / 2 });
	const std::vector<uint8_t> good = Write(records);
	std::printf("the valid document: %s\n", Check(good).empty() ? "accepted" : "refused");

	std::mt19937 random(1);
	const int trials = 20000;
	int accepted = 0;
	for (int trial = 0; trial < trials; trial++)
	{
		std::vector<uint8_t> damaged = good;
		damaged[random() % damaged.size()] ^= static_cast<uint8_t>(1 + random() % 255); // Never zero: a byte always changes
		if (Check(damaged).empty())
			accepted++;
	}
	std::printf("%d corruptions, %d accepted\n", trials, accepted);
	return 0;
}
