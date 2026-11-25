// Writing a float as text: how many digits does it take to read back the same float?
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
#include <limits>

int main()
{
	const float value = 1.0f / 3.0f;
	for (const int digits : { 6, 8, 9 })
	{
		char text[32];
		std::snprintf(text, sizeof(text), "%.*g", digits, value);
		const float back = std::strtof(text, nullptr);
		std::printf("%d digits: %s reads back %s\n", digits, text, back == value ? "equal" : "different");
	}
	std::printf("always enough: %d digits for a float, %d for a double\n", std::numeric_limits<float>::max_digits10, std::numeric_limits<double>::max_digits10);
}
