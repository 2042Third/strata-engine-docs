// Practice 3: a counter captured by value and by reference, read after the counter changes.
#include <iostream>

int main()
{
	int counter = 1;
	auto byValue = [counter]() { return counter * 10; };
	auto byReference = [&counter]() { return counter * 10; };
	counter = 3;
	std::cout << "by value: " << byValue() << '\n';
	std::cout << "by reference: " << byReference() << '\n';
	return 0;
}
