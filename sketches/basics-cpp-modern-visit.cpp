// Practice 3: a variant of an int and a string, written out through std::visit.
#include <iostream>
#include <string>
#include <variant>

int main()
{
	const std::variant<int, std::string> values[] = { 42, std::string("gold") };
	for (const auto& value : values)
	{
		std::visit([](const auto& item) { std::cout << "holds " << item << '\n'; }, value);
	}
	return 0;
}
