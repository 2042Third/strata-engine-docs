// A variant holds one of its types; std::visit calls the lambda with whichever it holds.
#include <iostream>
#include <string>
#include <variant>
using Value = std::variant<int, float, std::string>;
std::string Describe(const Value& value)
{
	return std::visit([](const auto& item) -> std::string
	{
		using T = std::decay_t<decltype(item)>;
		if constexpr (std::is_same_v<T, int>)
			return "int " + std::to_string(item);
		else if constexpr (std::is_same_v<T, float>)
			return "float " + std::to_string(item);
		else
			return "text " + item;
	}, value);
}
int main()
{
	const Value values[] = { 7, 2.5f, std::string("gold") };
	for (const Value& value : values)
		std::cout << value.index() << ": " << Describe(value) << '\n';
}
