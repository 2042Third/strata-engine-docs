// A toy of the ownership loop of strata_add_layer_libraries: globs become regular expressions, and every source
// file must match exactly one layer.
#include <iostream>
#include <regex>
#include <string>
#include <vector>

struct Layer
{
	std::string Name;
	std::vector<std::string> Paths;
	std::vector<std::string> Exclude;
};

// '**/' is any directories or none, '**' anything, '*' and '?' stay within one path component.
static std::string GlobToRegex(const std::string& glob)
{
	std::string regex = "^";
	for (size_t i = 0; i < glob.size(); i++)
	{
		if (glob.compare(i, 3, "**/") == 0)
		{
			regex += "(.*/)?";
			i += 2;
		}
		else if (glob.compare(i, 2, "**") == 0)
		{
			regex += ".*";
			i += 1;
		}
		else if (glob[i] == '*')
			regex += "[^/]*";
		else if (glob[i] == '?')
			regex += "[^/]";
		else if (std::string("\\.+^$()[]{}|").find(glob[i]) != std::string::npos)
			regex += std::string("\\") + glob[i];
		else
			regex += glob[i];
	}
	return regex + "$";
}

static bool AnyMatches(const std::vector<std::string>& globs, const std::string& file)
{
	for (const std::string& glob : globs)
	{
		if (std::regex_match(file, std::regex(GlobToRegex(glob))))
			return true;
	}
	return false;
}

int main()
{
	const std::vector<Layer> layers = {
		{ "Core", { "Strata/Core/**" }, { "Strata/Core/Application.*" } },
		{ "App", { "Strata/Core/Application.*" }, {} },
		{ "Audio", { "Strata/Audio/**" }, {} },
		{ "Extra", { "Strata/Audio/*.h" }, {} },
	};
	const std::vector<std::string> files = {
		"Strata/Core/StringUtils.h", "Strata/Core/Application.cpp", "Strata/Audio/Mixer.cpp",
		"Strata/Audio/AudioClip.h", "Strata/Video/Player.cpp",
	};

	std::cout << GlobToRegex("Strata/Core/Application.*") << "\n";
	for (const std::string& file : files)
	{
		std::string owners;
		int count = 0;
		for (const Layer& layer : layers)
		{
			if (AnyMatches(layer.Paths, file) && !AnyMatches(layer.Exclude, file))
			{
				owners += (count == 0 ? "" : ", ") + layer.Name;
				count++;
			}
		}
		if (count == 0)
			std::cout << file << " is in no layer\n";
		else if (count > 1)
			std::cout << file << " is in several layers (" << owners << ")\n";
		else
			std::cout << file << " belongs to " << owners << "\n";
	}
	return 0;
}
