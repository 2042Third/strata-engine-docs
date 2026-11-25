// A default argument fills a parameter the call leaves out; two functions may share a name.
#include <iostream>

float Scale(float value, float factor = 2.0f)
{
	return value * factor;
}
void Show(int number)
{
	std::cout << "int " << number << '\n';
}
void Show(float number)
{
	std::cout << "float " << number << '\n';
}

int main()
{
	std::cout << Scale(5.0f) << '\n';       // factor is 2
	std::cout << Scale(5.0f, 3.0f) << '\n'; // factor is 3
	Show(7);
	Show(7.5f);
	return 0;
}
