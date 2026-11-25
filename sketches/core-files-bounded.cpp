// Reads a source to its end with a cap, trusting a size hint for nothing but the first buffer.
#include <algorithm>
#include <cstdio>
#include <sstream>
#include <string>

enum class Status
{
	Complete,
	TooLarge
};

Status ReadAll(std::istream& source, size_t sizeHint, size_t maxSize, std::string& contents)
{
	contents.clear();
	std::string buffer(std::min(sizeHint, maxSize) + 1, '\0');
	size_t total = 0;
	while (true)
	{
		if (total == buffer.size())
			buffer.resize(std::min(buffer.size() * 2, maxSize + 1));
		if (total == buffer.size())
			break; // one byte past the cap is held: the source is too large
		source.read(buffer.data() + total, static_cast<std::streamsize>(buffer.size() - total));
		const size_t count = static_cast<size_t>(source.gcount());
		if (count == 0)
			break;
		total += count;
	}
	if (total > maxSize)
		return Status::TooLarge;
	contents.assign(buffer, 0, total);
	return Status::Complete;
}

int main()
{
	const std::string data = "0123456789"; // ten bytes
	for (const size_t hint : { size_t(0), size_t(3), size_t(500) })
	{
		for (const size_t cap : { size_t(10), size_t(9) })
		{
			std::istringstream source(data);
			std::string contents;
			const Status status = ReadAll(source, hint, cap, contents);
			std::printf("hint %3zu, cap %2zu: %s, %zu bytes kept\n", hint, cap, status == Status::Complete ? "complete" : "too large", contents.size());
		}
	}
}
