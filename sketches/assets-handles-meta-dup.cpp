#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <map>
#include <string>
#include <vector>

int main()
{
	const std::vector<uint64_t> handles = { 0x11, 0x11, 0x22, 0x11 };
	const std::vector<std::string> paths = { "Brick - Copy.png", "Brick.png", "Moss.png", "Brick (1).png" };

	// For each handle, the file with the shortest path keeps it.
	std::map<uint64_t, size_t> keeper;
	for (size_t index = 0; index < handles.size(); index++)
	{
		auto found = keeper.find(handles[index]);
		if (found == keeper.end() || paths[index].size() < paths[found->second].size())
			keeper[handles[index]] = index;
	}
	for (size_t index = 0; index < handles.size(); index++)
	{
		if (keeper[handles[index]] != index)
			std::printf("%s needs a new handle; %s keeps it\n", paths[index].c_str(), paths[keeper[handles[index]]].c_str());
	}
	return 0;
}
