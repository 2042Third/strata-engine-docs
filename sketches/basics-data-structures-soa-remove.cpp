// A struct of arrays with a swap-remove: every array moves its last element into the gap.
#include <iostream>
#include <string>
#include <vector>

struct Coins { std::vector<std::string> Names; std::vector<int> Values; };

void RemoveCoin(Coins& coins, size_t index)
{
	coins.Names[index] = coins.Names.back();
	coins.Values[index] = coins.Values.back();
	coins.Names.pop_back();
	coins.Values.pop_back();
}

int main()
{
	Coins coins = { { "a", "b", "c", "d" }, { 1, 5, 10, 25 } };
	RemoveCoin(coins, 1);
	for (size_t index = 0; index < coins.Names.size(); index++)
		std::cout << coins.Names[index] << '=' << coins.Values[index] << ' ';
	std::cout << '\n';
	return 0;
}
