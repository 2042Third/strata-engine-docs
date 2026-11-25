// The root's exclusion step: required and unknown names are refused, the others are left out.
#include <algorithm>
#include <array>
#include <cstdio>
#include <string>
#include <string_view>
#include <vector>

namespace
{

	constexpr std::array<std::string_view, 6> c_Modules = { "Input", "Scene", "Renderer", "Physics", "Audio", "Scripting" };
	constexpr std::array<std::string_view, 3> c_Required = { "Input", "Scene", "Renderer" };

	template<typename List>
	bool Contains(const List& list, std::string_view name)
	{
		return std::find(list.begin(), list.end(), name) != list.end();
	}

	std::vector<std::string_view> GetExcluded(const std::vector<std::string>& names)
	{
		std::vector<std::string_view> excluded;
		for (const std::string& name : names)
		{
			if (Contains(c_Required, name))
				std::printf("error: the %s module cannot be excluded; it is registered\n", name.c_str());
			else if (!Contains(c_Modules, name))
				std::printf("error: %s is no module of this build\n", name.c_str());
			else
				excluded.push_back(name);
		}
		return excluded;
	}

}

int main()
{
	const std::vector<std::string> exclude = { "Physics", "Scene", "Teleportation" };
	const std::vector<std::string_view> excluded = GetExcluded(exclude);

	std::printf("registered:");
	for (std::string_view module : c_Modules)
	{
		if (!Contains(excluded, module))
			std::printf(" %.*s", static_cast<int>(module.size()), module.data());
	}
	std::printf("\n");
	return 0;
}
