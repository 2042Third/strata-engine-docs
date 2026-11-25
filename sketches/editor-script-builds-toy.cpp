// A toy script build planner: what a build must do, and where its first error is.
#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <optional>
#include <string>
#include <vector>

// What the last configure step recorded: the toolchain and the script files, sorted.
struct Stamp
{
	std::string Toolchain;
	std::vector<std::string> Files;
};

enum class Plan
{
	RemoveThenConfigure,
	ConfigureAgain,
	BuildOnly
};

std::string Describe(Plan plan)
{
	if (plan == Plan::RemoveThenConfigure)
		return "remove the tree, configure, build";
	if (plan == Plan::ConfigureAgain)
		return "configure again where it is, build";
	return "build only";
}

Plan Decide(const std::optional<Stamp>& previous, const std::string& toolchain, std::vector<std::string> files)
{
	std::sort(files.begin(), files.end());
	if (!previous || previous->Toolchain != toolchain)
		return Plan::RemoveThenConfigure;
	if (previous->Files != files)
		return Plan::ConfigureAgain;
	return Plan::BuildOnly;
}

struct Problem
{
	std::string File;
	int Line = 0;
	std::string Message;
};

// Finds the first "file:line:column: error: message" line of a GCC style log.
std::optional<Problem> FindFirstError(const std::string& log)
{
	size_t start = 0;
	while (start < log.size())
	{
		size_t end = log.find('\n', start);
		if (end == std::string::npos)
			end = log.size();
		const std::string line = log.substr(start, end - start);
		start = end + 1;

		const size_t marker = line.find(": error: ");
		if (marker == std::string::npos || marker == 0)
			continue;
		const size_t columnColon = line.rfind(':', marker - 1);
		const size_t lineColon = columnColon == std::string::npos || columnColon == 0 ? std::string::npos : line.rfind(':', columnColon - 1);
		if (lineColon == std::string::npos)
			continue;
		Problem problem;
		problem.File = line.substr(0, lineColon);
		problem.Line = std::atoi(line.substr(lineColon + 1, columnColon - lineColon - 1).c_str());
		problem.Message = line.substr(marker + 9);
		return problem;
	}
	return std::nullopt;
}

int main()
{
	const std::vector<std::string> files = { "Spinner.cpp", "CMakeLists.txt" };
	const Stamp stamp { "Visual Studio 18 2026", { "CMakeLists.txt", "Spinner.cpp" } };

	std::cout << "first build:   " << Describe(Decide(std::nullopt, "Visual Studio 18 2026", files)) << "\n";
	std::cout << "same files:    " << Describe(Decide(stamp, "Visual Studio 18 2026", files)) << "\n";
	std::cout << "new file:      " << Describe(Decide(stamp, "Visual Studio 18 2026", { "Spinner.cpp", "CMakeLists.txt", "Coin.cpp" })) << "\n";
	std::cout << "other compiler: " << Describe(Decide(stamp, "Ninja", files)) << "\n";

	const std::string log = "[1/2] Building CXX object Spinner.cpp.o\nSpinner.cpp:14:9: error: 'speed' was not declared\nninja: build stopped\n";
	if (const std::optional<Problem> problem = FindFirstError(log))
		std::cout << "first error:   " << problem->File << " line " << problem->Line << ": " << problem->Message << "\n";
	return 0;
}
