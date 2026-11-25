// A free folder name, as the New Project dialog suggests it: "My Project", "My Project 2", and so on.
#include <cstdio>
#include <set>
#include <string>

std::string MakeUniqueName(const std::set<std::string>& taken, const std::string& base)
{
	for (int number = 1; number <= 999; number++)
	{
		const std::string name = number == 1 ? base : base + " " + std::to_string(number);
		if (taken.count(name) == 0)
			return name;
	}
	return base; // 999 names taken: give up and let the dialog show the problem
}

int main()
{
	const std::set<std::string> taken = { "My Project", "My Project 2", "My Project 4" };
	std::printf("free in a folder with three: %s\n", MakeUniqueName(taken, "My Project").c_str());
	std::printf("free in an empty folder: %s\n", MakeUniqueName({}, "My Project").c_str());
	return 0;
}
