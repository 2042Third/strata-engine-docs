#include <iostream>
#include <map>
#include <string>

struct Trashed
{
	std::string Path;
	int Handle = 0;
	bool Force = false;
};

// A redo runs only while the path holds what the step deleted and nothing uses it (unless the delete was forced).
bool CheckRedo(const std::map<std::string, int>& files, const std::map<int, int>& userCounts, const Trashed& trashed, std::string& outError)
{
	const auto file = files.find(trashed.Path);
	if (file == files.end() || file->second != trashed.Handle)
	{
		outError = "'" + trashed.Path + "' is no longer the asset this step deleted";
		return false;
	}
	const auto users = userCounts.find(trashed.Handle);
	if (!trashed.Force && users != userCounts.end() && users->second > 0)
	{
		outError = "'" + trashed.Path + "' is used now";
		return false;
	}
	return true;
}

int main()
{
	const Trashed trashed = { "Textures/Rust.png", 2, false };
	std::string error;

	std::map<std::string, int> files = { { "Textures/Rust.png", 2 } };
	std::map<int, int> userCounts;
	std::cout << "same file, no users: " << CheckRedo(files, userCounts, trashed, error) << "\n";

	files["Textures/Rust.png"] = 3; // Another asset took the path
	if (!CheckRedo(files, userCounts, trashed, error))
		std::cout << "other file: " << error << "\n";
	return 0;
}
