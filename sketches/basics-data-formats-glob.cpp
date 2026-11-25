// A glob turned into a regular expression: the dot of a glob is a plain dot, so the pattern escapes it.
#include <iostream>
#include <regex>
#include <string>

std::string GlobToPattern(const std::string& glob)
{
	std::string pattern = "^";
	for (const char character : glob)
	{
		if (character == '.')
			pattern += '\\';
		if (character == '*')
			pattern += '.';
		pattern += character;
	}
	return pattern + "$";
}
int main()
{
	const std::regex pattern(GlobToPattern("*.cpp"));
	const std::string names[] = { "Hash.cpp", "Hash.h", "cpp", "a.cpp.bak" };
	for (const std::string& name : names)
		std::cout << name << ": " << std::regex_match(name, pattern) << '\n';
}
