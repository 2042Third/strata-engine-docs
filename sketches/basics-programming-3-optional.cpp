// An optional number: empty at first, then filled.
#include <iostream>
#include <optional>

int main()
{
	std::optional<float> speed;
	std::cout << "empty: " << speed.value_or(3.0f) << '\n';
	if (speed.has_value())
		std::cout << "never written\n";
	speed = 7.5f;
	if (speed.has_value())
		std::cout << "filled: " << *speed << '\n';
	return 0;
}
