#include <cassert>
#include <iostream>

int main()
{
	int coins = 0;
	std::cin >> coins;

	// Stops a Debug build for a negative number; a Release build removes this line.
	assert(coins >= 0 && "coins cannot be negative");

	std::cout << "coins: " << coins << "\n";
	return 0;
}
