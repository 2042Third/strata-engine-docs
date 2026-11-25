#include <cstdio>
#include <initializer_list>
#include <map>
#include <string>

struct DependencyState
{
	bool Exists = false;
	size_t Size = 0;
};

using Files = std::map<std::string, std::string>;
using Record = std::map<std::string, DependencyState>;

// Notes a file's state, also when the file is missing: creating it later must count as a change.
DependencyState Observe(const Files& files, const std::string& path)
{
	const auto it = files.find(path);
	if (it == files.end())
		return { false, 0 };
	return { true, it->second.size() };
}

Record Import(const Files& files)
{
	Record record;
	for (const char* path : { "Crate.bin", "Crate.png" })
		record[path] = Observe(files, path);
	return record;
}

bool IsCurrent(const Record& record, const Files& files)
{
	for (const auto& [path, state] : record)
	{
		const DependencyState now = Observe(files, path);
		if (now.Exists != state.Exists || now.Size != state.Size)
			return false;
	}
	return true;
}

int main()
{
	Files files;
	files["Crate.bin"] = "1234";
	const Record record = Import(files);
	std::printf("unchanged: %s\n", IsCurrent(record, files) ? "current" : "import again");
	files["Crate.png"] = "pixels";
	std::printf("png created: %s\n", IsCurrent(record, files) ? "current" : "import again");
	files.erase("Crate.png");
	files["Crate.bin"] = "123456";
	std::printf("bin grew: %s\n", IsCurrent(record, files) ? "current" : "import again");
	return 0;
}
