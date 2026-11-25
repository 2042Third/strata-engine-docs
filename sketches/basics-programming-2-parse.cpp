// Practice 6: what std::stoi makes of text that starts with digits.
#include <iostream>
#include <string>

int main()
{
	std::cout << std::stoi("42") << '\n';
	std::cout << std::stoi("42 coins") << '\n';
	std::cout << std::stoi("-7") << '\n';
	return 0;
}
