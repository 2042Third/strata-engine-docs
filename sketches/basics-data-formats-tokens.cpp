// Cuts a JSON text into tokens, one character at a time; a string that never ends is an error.
#include <iostream>
#include <string>

int main()
{
	const std::string text = R"({"Name": "Coin Run", "Version": 3, "Done": true})";
	const std::string punctuation = "{}[]:, ";
	for (size_t start = 0; start < text.size();)
	{
		size_t end = text.find_first_of(punctuation, start + 1);
		if (text[start] == '"')
			end = text.find('"', start + 1) + 1;
		else if (punctuation.find(text[start]) != std::string::npos)
			end = start + 1;
		if (end == 0 || end == std::string::npos)
		{
			std::cout << "error: the text ends inside a token\n";
			return 1;
		}
		if (text[start] != ' ')
			std::cout << text.substr(start, end - start) << '\n';
		start = end;
	}
}
