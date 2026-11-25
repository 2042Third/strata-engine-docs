// Practice 1: a number passed by value and by reference.
#include <iostream>

void Double(int number) { number = number * 2; }
void DoubleInPlace(int& number) { number = number * 2; }

int main()
{
	int gems = 4;
	Double(gems);
	std::cout << "after Double: " << gems << '\n';
	DoubleInPlace(gems);
	std::cout << "after DoubleInPlace: " << gems << '\n';
	DoubleInPlace(gems);
	std::cout << "after a second DoubleInPlace: " << gems << '\n';
	return 0;
}
