// Exercise: the first rules of an export directory check, in the order the engine applies them.
#include <cstdio>
#include <string>

// Returns an empty string when the directory is usable, or the reason it is not.
std::string CheckDirectory(const std::string& directory, const std::string& project)
{
	if (directory.empty())
		return "Choose the directory to export the game to";
	if (directory.size() >= 2 && directory[0] == '/' && directory[1] == '/')
		return "a network or device path";
	if (directory[0] != '/')
		return "not an absolute path";
	// Whole path parts only: "/games/CoinBuild" lies beside the project, not inside it.
	if (directory == project || directory.rfind(project + "/", 0) == 0)
		return "inside the project";
	return "";
}

int main()
{
	const std::string project = "/games/Coin";
	const char* directories[] = { "", "//server/share", "Build", "/games/Coin/Build", "/games/CoinBuild" };
	for (const char* directory : directories)
	{
		const std::string reason = CheckDirectory(directory, project);
		std::printf("'%s': %s\n", directory, reason.empty() ? "usable" : reason.c_str());
	}
	return 0;
}
