// Practice 2: Clamp keeps a value between 0 and a top that defaults to 1.
#include <iostream>

float Clamp(float value, float top = 1.0f)
{
	if (value < 0.0f)
		return 0.0f;
	if (value > top)
		return top;
	return value;
}

int main()
{
	std::cout << Clamp(1.7f) << '\n';
	std::cout << Clamp(1.7f, 5.0f) << '\n';
	std::cout << Clamp(-2.0f) << '\n';
	return 0;
}
