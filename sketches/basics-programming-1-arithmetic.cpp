// The order of operations, a division of whole numbers, a mixed division and the shortcuts += and ++.
#include <iostream>

int main()
{
	std::cout << "2 + 3 * 4 = " << 2 + 3 * 4 << '\n';
	std::cout << "(2 + 3) * 4 = " << (2 + 3) * 4 << '\n';
	std::cout << "10 - 4 - 3 = " << 10 - 4 - 3 << '\n';

	const int coins = 7;
	const int players = 2;
	std::cout << "7 / 2 = " << coins / players << '\n';
	std::cout << "7 / 2.0f = " << coins / 2.0f << '\n';

	float share = 1 / 2;   // 1 / 2 is a division of whole numbers: the 0 is stored as 0.0f
	float fixedShare = 1 / 2.0f;
	std::cout << "share = " << share << ", fixedShare = " << fixedShare << '\n';

	int total = 5;
	total += 2; // the same as total = total + 2
	total++;    // the same as total = total + 1
	std::cout << "total = " << total << '\n';
	return 0;
}
