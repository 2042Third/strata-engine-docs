// A toy manifest check: plain file names, a version of up to four parts, and the key of the data directory.
#include <cstdio>
#include <filesystem>
#include <string>

bool IsPlainFileName(const std::string& name)
{
	// "." and ".." are file names to the library, but they name a directory.
	if (name.empty() || name == "." || name == "..")
		return false;
	const std::filesystem::path path(name);
	return !path.has_parent_path() && !path.is_absolute() && path.filename() == path;
}

// Fills four numbers from a version such as "1.2"; false when the text is no version.
bool ParseVersion(const std::string& text, unsigned parts[4])
{
	for (int index = 0; index < 4; index++)
		parts[index] = 0;
	int count = 0;
	unsigned value = 0;
	bool hasDigits = false;
	for (size_t index = 0; index <= text.size(); index++)
	{
		// The end of the text closes the last part like a dot.
		const char character = index < text.size() ? text[index] : '.';
		if (character >= '0' && character <= '9')
		{
			value = value * 10 + static_cast<unsigned>(character - '0');
			hasDigits = true;
			if (value > 65535)
				return false;
		}
		else if (character == '.')
		{
			if (!hasDigits || count == 4)
				return false;
			parts[count++] = value;
			value = 0;
			hasDigits = false;
		}
		else
			return false;
	}
	return true;
}

// The folder name saves go under: the Name with path separators replaced.
std::string DataDirectoryName(std::string name)
{
	for (char& character : name)
		if (character == '/' || character == '\\')
			character = '_';
	return name;
}

int main()
{
	for (const char* file : { "Game.stpak", "../Other.stpak", "sub/Game.stpak", "/data/Game.stpak", ".." })
		std::printf("%-18s %s\n", file, IsPlainFileName(file) ? "accepted" : "refused");

	for (const char* version : { "1.2", "1.2.3.4", "1.2.3.4.5", "1.70000", "1..2" })
	{
		unsigned parts[4];
		if (ParseVersion(version, parts))
			std::printf("%-10s -> %u %u %u %u\n", version, parts[0], parts[1], parts[2], parts[3]);
		else
			std::printf("%-10s -> refused\n", version);
	}

	std::printf("Name 'Moon/Crab' keeps its saves under '%s'\n", DataDirectoryName("Moon/Crab").c_str());
	return 0;
}
