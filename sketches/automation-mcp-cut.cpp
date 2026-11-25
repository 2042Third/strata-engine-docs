// Cuts a sentence to a length in bytes at a space, or inside a word but never inside a UTF-8 sequence.
#include <iostream>
#include <string>

std::string Cut(const std::string& text, size_t maxLength)
{
	if (text.size() <= maxLength)
		return text;
	size_t length = text.rfind(' ', maxLength - 1);
	if (length == std::string::npos || length == 0)
	{
		length = maxLength - 1;
		// A byte of the form 10xxxxxx continues a character: step back to the byte that starts it.
		while (length > 0 && (static_cast<unsigned char>(text[length]) & 0xC0) == 0x80)
			length--;
	}
	return text.substr(0, length) + "\xE2\x80\xA6";
}

int main()
{
	std::cout << Cut("A rather long sentence", 12) << "\n";
	std::cout << Cut("Unbroken", 4) << "\n";
	std::cout << Cut("\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9", 5) << "\n";
	std::cout << Cut("\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9", 4) << "\n";
	return 0;
}
