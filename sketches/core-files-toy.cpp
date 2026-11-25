// A toy save: the same text written in place and through a temporary file, with the process "killed" after each step.
// A kill is a return: nothing after it runs, as when a process dies.
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>

namespace
{
	const std::string c_Old = "OLD OLD OLD OLD";
	const std::string c_New = "NEW NEW NEW NEW NEW";

	// Three steps: open the file (which empties it), write the first half, write the rest.
	void SaveInPlace(const std::filesystem::path& path, int killAfter)
	{
		if (killAfter == 0)
			return;
		const size_t half = c_New.size() / 2;
		std::ofstream stream(path, std::ios::binary | std::ios::trunc);
		if (killAfter == 1)
			return;
		stream.write(c_New.data(), static_cast<std::streamsize>(half));
		stream.flush();
		if (killAfter == 2)
			return;
		stream.write(c_New.data() + half, static_cast<std::streamsize>(c_New.size() - half));
	}

	// Four steps: open a temporary file, write both halves into it, rename it over the file.
	void SaveAtomically(const std::filesystem::path& path, int killAfter)
	{
		if (killAfter == 0)
			return;
		const size_t half = c_New.size() / 2;
		std::filesystem::path temporary = path;
		temporary += ".tmp0";
		std::ofstream stream(temporary, std::ios::binary | std::ios::trunc);
		if (killAfter == 1)
			return;
		stream.write(c_New.data(), static_cast<std::streamsize>(half));
		stream.flush();
		if (killAfter == 2)
			return;
		stream.write(c_New.data() + half, static_cast<std::streamsize>(c_New.size() - half));
		stream.close();
		if (killAfter == 3)
			return;
		std::filesystem::rename(temporary, path);
	}

	std::string Describe(const std::filesystem::path& path)
	{
		std::ifstream stream(path, std::ios::binary);
		const std::string text((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());
		if (text == c_Old)
			return "the old file";
		if (text == c_New)
			return "the new file";
		return "DAMAGED, holds \"" + text + "\"";
	}
}

int main()
{
	const std::filesystem::path directory = std::filesystem::temp_directory_path() / "strata-toy-files";
	const std::filesystem::path path = directory / "save.txt";
	for (const bool atomic : { false, true })
	{
		for (int killAfter = 0; killAfter <= (atomic ? 4 : 3); killAfter++)
		{
			std::filesystem::remove_all(directory);
			std::filesystem::create_directories(directory);
			std::ofstream(path, std::ios::binary) << c_Old;
			atomic ? SaveAtomically(path, killAfter) : SaveInPlace(path, killAfter);
			size_t entries = 0;
			for (const auto& entry : std::filesystem::directory_iterator(directory))
				entries += entry.is_regular_file() ? 1 : 0;
			std::cout << (atomic ? "atomic " : "in place ") << "killed after step " << killAfter << ": " << Describe(path) << ", " << entries << " file(s) in the folder\n";
		}
	}
	std::filesystem::remove_all(directory);
}
