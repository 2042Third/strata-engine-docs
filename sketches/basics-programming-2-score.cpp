// Practice 4: a score turned into text, and text turned into a number.
#include <iostream>
#include <string>

int main()
{
	int score = 120;
	std::string line = "Score: " + std::to_string(score);
	std::cout << line << '\n';

	std::string typed = "120";
	int parsed = std::stoi(typed);
	std::cout << "Bonus score: " << parsed + 30 << '\n';
	return 0;
}
