// Values of four types, kept in variables, and what a chain of << prints for each.
#include <cstdint>
#include <iostream>

int main()
{
	std::cout << std::boolalpha; // print true and false as words, as Log::Info does

	int32_t coins = 3;   // a whole number
	float speed = 90.0f; // a number with a fraction; the f makes it a float
	double exact = 0.1;  // a number with a fraction, kept with more digits
	bool isGold = true;  // true or false

	coins = coins + 1; // assignment: the right side is computed first, then stored in coins
	speed = 2.5f;      // a new value replaces the old one

	std::cout << "Coins: " << coins << '\n';
	std::cout << "Speed: " << speed << '\n';
	std::cout << "Exact: " << exact << '\n';
	std::cout << "Gold: " << isGold << '\n';
	return 0;
}
