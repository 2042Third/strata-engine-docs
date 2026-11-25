// An if chain, comparisons joined by && and ||, and a variable that lives only inside its braces.
#include <iostream>

int main()
{
	std::cout << std::boolalpha;
	const int coins = 12;
	if (coins == 0)
		std::cout << "none\n";
	else if (coins < 10)
		std::cout << "few\n";
	else
		std::cout << "many\n";

	const bool isGold = false;
	const bool nearPlayer = true;
	std::cout << "gold and near: " << (isGold && nearPlayer) << '\n';
	std::cout << "gold or near: " << (isGold || nearPlayer) << '\n';
	std::cout << "not gold: " << !isGold << '\n';
	if (nearPlayer)
	{
		const int bonus = 5; // exists only between these braces
		std::cout << "bonus: " << bonus << '\n';
	}
}
