// A pointer to a coin, the check before use and a null pointer.
#include <iostream>

struct Coin
{
	int Value = 5;
};

int main()
{
	Coin gold;
	Coin* found = &gold;
	Coin* missing = nullptr;
	if (found != nullptr)
		std::cout << "found, value " << found->Value << '\n';
	if (missing == nullptr)
		std::cout << "missing points to nothing\n";
	return 0;
}
