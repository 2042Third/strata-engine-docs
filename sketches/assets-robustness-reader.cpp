// Two readers of a count-prefixed array: one trusts the count, one compares it with the bytes that are left.
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>

struct Reader
{
	const uint8_t* Data = nullptr;
	size_t Size = 0;
	size_t Position = 0;
	bool Valid = true;

	size_t GetRemaining() const { return Size - Position; }

	uint32_t ReadCount()
	{
		uint32_t count = 0;
		if (!Valid || GetRemaining() < sizeof(count))
		{
			Valid = false;
			return 0;
		}
		std::memcpy(&count, Data + Position, sizeof(count));
		Position += sizeof(count);
		return count;
	}
};

// The naive reader: the count decides how much memory is asked for.
uint64_t NaiveBytesRequested(Reader& reader, size_t elementSize)
{
	return static_cast<uint64_t>(reader.ReadCount()) * elementSize;
}

// The bounded reader: the count must fit in what the file still holds, else the reader fails and stays failed.
bool ReadBounded(Reader& reader, size_t elementSize, std::vector<uint8_t>& out)
{
	const uint64_t count = reader.ReadCount();
	if (!reader.Valid || count > reader.GetRemaining() / elementSize)
	{
		reader.Valid = false;
		return false;
	}
	out.assign(reader.Data + reader.Position, reader.Data + reader.Position + count * elementSize);
	reader.Position += count * elementSize;
	return true;
}

int main()
{
	// A 12-byte file: a count, then 8 bytes of data.
	const uint32_t claims[] = { 2, 3, 1'000'000'000 };
	for (uint32_t claim : claims)
	{
		uint8_t file[12] = {};
		std::memcpy(file, &claim, sizeof(claim));
		Reader naive { file, sizeof(file) };
		Reader bounded { file, sizeof(file) };
		std::vector<uint8_t> out;
		const bool accepted = ReadBounded(bounded, 4, out);
		std::printf("claim %u: naive asks for %llu bytes, bounded %s\n", claim,
			static_cast<unsigned long long>(NaiveBytesRequested(naive, 4)), accepted ? "accepts" : "refuses");
	}
	return 0;
}
