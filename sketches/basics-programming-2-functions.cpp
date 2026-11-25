// A function with two parameters and a return value, and a void function that changes only its copy.
#include <iostream>

int Add(int a, int b) // a and b are parameters
{
	return a + b;
}

void ReportDouble(int value) // void: gives nothing back
{
	value = value * 2; // changes the copy
	std::cout << "inside: " << value << '\n';
}

int main()
{
	int coins = 4;
	int total = Add(coins, 3); // the arguments are 4 and 3
	std::cout << "total: " << total << '\n';
	ReportDouble(coins);
	std::cout << "outside: " << coins << '\n';
	return 0;
}
