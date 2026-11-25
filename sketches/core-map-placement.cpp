// Places files in layers: a layer owns a file that starts with its Path, unless it starts with its Exclude too.
#include <cstdio>
#include <string>
#include <vector>

struct Layer
{
	std::string Name, Path, Exclude;
};

int main()
{
	const std::vector<Layer> table = { { "Core", "Strata/Core/", "Strata/Core/Application" }, { "App", "Strata/Core/Application", "" },
		{ "Engine", "Strata/Engine/", "" }, { "Clash", "Strata/Engine/Entry", "" } };
	for (const std::string file : { "Strata/Core/JobSystem.cpp", "Strata/Core/Application.cpp", "Strata/Engine/EntryPoint.h", "Strata/Foo/Bar.cpp" })
	{
		std::string owners;
		for (const Layer& layer : table)
			if (file.starts_with(layer.Path) && (layer.Exclude.empty() || !file.starts_with(layer.Exclude)))
				owners += " " + layer.Name;
		std::printf("%-30s%s\n", file.c_str(), owners.empty() ? " none: the configure fails" : owners.c_str());
	}
}
