// Practice 4: a switch on a whole number whose case 2 has no break, so the output shows the missing break.
#include <iostream>

int main()
{
	const int level = 2;
	switch (level)
	{
		case 1:
			std::cout << "one\n";
			break;
		case 2:
			std::cout << "two\n";
			[[fallthrough]]; // the missing break
		case 3:
			std::cout << "three\n";
			break;
		default:
			std::cout << "other\n";
			break;
	}
	return 0;
}
