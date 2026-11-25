// Practice 4: operator+ and a defaulted == for a small Money struct.
#include <iostream>

struct Money
{
	int Cents = 0;

	Money operator+(const Money& other) const { return Money { Cents + other.Cents }; }
	bool operator==(const Money& other) const = default;
};

int main()
{
	const Money sum = Money { 150 } + Money { 275 };
	std::cout << sum.Cents << " cents\n";
	std::cout << std::boolalpha << (sum == Money { 425 }) << " " << (sum == Money { 150 }) << "\n";
}
