// Three ways to pass a number: a copy, the caller's variable and a read-only view.
#include <iostream>

void AddByValue(int number) { number += 5; }
void AddByReference(int& number) { number += 5; }
int Twice(const int& number) { return number * 2; }

int main()
{
	int coins = 10;
	AddByValue(coins);
	std::cout << "after AddByValue: " << coins << '\n';
	AddByReference(coins);
	std::cout << "after AddByReference: " << coins << '\n';
	std::cout << "Twice: " << Twice(coins) << ", coins is " << coins << '\n';
	return 0;
}
