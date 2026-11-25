// Would Visual Studio's file tracker accept a build folder and a module name?
#include <algorithm>
#include <iostream>
#include <string>

constexpr size_t c_MaxPath = 259;
constexpr size_t c_ConfigureLog = 104;

// The deepest tracking log of the module's own build, for the Debug configuration.
size_t GetModuleLog(const std::string& module)
{
	const size_t trackingName = std::min<size_t>(module.size(), 17);
	return 1 + module.size() + 5 + 5 + 1 + trackingName + 5 + 27;
}

void Check(size_t folderLength, const std::string& module)
{
	const size_t longest = folderLength + std::max(c_ConfigureLog, GetModuleLog(module));
	std::cout << "folder " << folderLength << ", module of " << module.size() << " characters: longest path " << longest
			  << (longest <= c_MaxPath ? ", fits" : ", too deep") << "\n";
}

int main()
{
	Check(150, std::string(20, 'M'));
	Check(156, std::string(20, 'M'));
	Check(30, std::string(60, 'M'));
	return 0;
}
