// A function that may have no answer returns std::optional; the caller checks it before use.
#include <iostream>
#include <optional>
#include <string>

std::optional<int> FindIndex(const std::string& text, char letter)
{
	const size_t position = text.find(letter);
	if (position == std::string::npos)
		return std::nullopt;
	return static_cast<int>(position);
}

int main()
{
	const std::optional<int> found = FindIndex("strata", 'a');
	const std::optional<int> missing = FindIndex("strata", 'z');
	if (found)
		std::cout << "found at " << *found << '\n';
	std::cout << "missing has a value: " << missing.has_value() << ", value_or(-1): " << missing.value_or(-1) << '\n';
	return 0;
}
