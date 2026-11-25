// Joining and comparing text, and turning numbers into text and back.
#include <iostream>
#include <string>

int main()
{
	std::cout << std::boolalpha;
	std::string name = "Coin";
	std::string label = name + " " + std::to_string(3); // + joins
	std::cout << label << '\n';
	std::cout << (name == "Coin") << '\n';  // compares the letters
	std::cout << (name == "coin") << '\n';  // capitals count
	std::cout << std::to_string(2.5f) << '\n';

	int score = std::stoi("42");
	std::cout << score + 1 << '\n';
	std::cout << std::stoi("12 coins") << '\n'; // reads the digits, stops at the space
	return 0;
}
