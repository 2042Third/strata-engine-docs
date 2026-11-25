// Practice 1: what a for loop logs from 0 while i < 3, and what <= adds.
#include <iostream>

int main()
{
	for (int i = 0; i < 3; i++)
		std::cout << "i = " << i << '\n';
	std::cout << "--\n";
	for (int i = 0; i <= 3; i++)
		std::cout << "i = " << i << '\n';
	return 0;
}
