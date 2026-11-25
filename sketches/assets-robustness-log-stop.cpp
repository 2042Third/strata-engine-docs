// The log of assets-robustness-log.cpp, changed so that a damaged line ends the load. A record log in the style of the import record store: one line per record, "<crc> <text>", the last line possibly torn.
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

// CRC-32C (Castagnoli), bit by bit: slow and short.
uint32_t Crc32c(const std::string& text)
{
	uint32_t crc = 0xFFFFFFFFu;
	for (char character : text)
	{
		crc ^= static_cast<uint8_t>(character);
		for (int bit = 0; bit < 8; bit++)
			crc = (crc >> 1) ^ ((crc & 1u) != 0 ? 0x82F63B78u : 0u);
	}
	return ~crc;
}

std::string FormatLine(const std::string& text)
{
	char prefix[16];
	std::snprintf(prefix, sizeof(prefix), "%08x ", Crc32c(text));
	return std::string(prefix) + text + "\n";
}

struct LoadResult
{
	std::vector<std::string> Records;
	int Skipped = 0;
	size_t KeptBytes = 0;
};

LoadResult Load(const std::string& file)
{
	LoadResult result;
	const size_t lastFeed = file.rfind('\n');
	const size_t whole = lastFeed == std::string::npos ? 0 : lastFeed + 1;
	if (whole < file.size())
		result.Skipped++; // a last line without its line feed was torn: it is cut
	result.KeptBytes = whole;

	size_t position = 0;
	while (position < whole)
	{
		const size_t end = file.find('\n', position);
		const std::string line = file.substr(position, end - position);
		position = end + 1;
		const bool shaped = line.size() > 9 && line[8] == ' ';
		const std::string text = shaped ? line.substr(9) : std::string();
		char expected[16];
		std::snprintf(expected, sizeof(expected), "%08x", Crc32c(text));
		if (shaped && line.compare(0, 8, expected) == 0)
			result.Records.push_back(text);
		else
		{
			result.Skipped++;
			break; // a damaged line ends the load: everything after it is lost
		}
	}
	return result;
}

int main()
{
	std::string file = FormatLine("asset 1 imported") + FormatLine("asset 2 imported") + FormatLine("asset 3 imported");
	const size_t cuts[] = { file.size(), file.size() - 5, file.size() - 25 };
	for (size_t cut : cuts)
	{
		const LoadResult result = Load(file.substr(0, cut));
		std::printf("cut at %zu of %zu: %zu records, %d skipped, %zu bytes kept\n", cut, file.size(), result.Records.size(),
			result.Skipped, result.KeptBytes);
	}
	std::string flipped = file;
	flipped[12] = 'X'; // a changed byte inside the first record's text
	const LoadResult result = Load(flipped);
	std::printf("one byte changed: %zu records, %d skipped\n", result.Records.size(), result.Skipped);
	return 0;
}
