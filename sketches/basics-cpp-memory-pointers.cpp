// A pointer holds an address: & takes one, * follows it, -> follows it to a member.
#include <iostream>

struct Coin
{
	int Value = 5;
};

int main()
{
	int coins = 3;
	int* where = &coins; // where holds the address of coins
	*where = 10;         // follow the address and store 10 there
	std::cout << "coins: " << coins << ", through the pointer: " << *where << '\n';
	Coin gold;
	Coin* p = &gold;
	p->Value = 8; // the same as (*p).Value = 8
	std::cout << "gold.Value: " << gold.Value << '\n';
	int row[3] = { 7, 8, 9 };
	int* second = row + 1; // one int along the row, not one byte
	std::cout << "second: " << *second << ", elements apart: " << second - row << '\n';
	int* none = nullptr;
	std::cout << "none is null: " << std::boolalpha << (none == nullptr) << '\n';
}
