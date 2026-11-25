// A while loop and a for loop that each run three turns.
#include <iostream>

int main()
{
	int turn = 0;
	while (turn < 3) // checked before every turn
	{
		std::cout << "while " << turn << '\n';
		turn = turn + 1; // without this line the condition never becomes false
	}

	for (int i = 0; i < 3; i++) // start; condition; step
		std::cout << "for " << i << '\n';
	return 0;
}
