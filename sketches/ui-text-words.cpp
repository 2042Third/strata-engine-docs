#include <cstdint>
#include <cstdio>
#include <string>

bool IsContinuationByte(char byte)
{
	return (static_cast<uint8_t>(byte) & 0xC0) == 0x80;
}

uint32_t PreviousBoundary(const std::string& text, uint32_t position)
{
	if (position == 0)
		return 0;
	uint32_t index = position - 1;
	while (index > 0 && IsContinuationByte(text[index]))
		index--;
	return index;
}

uint32_t NextBoundary(const std::string& text, uint32_t position)
{
	const uint32_t size = static_cast<uint32_t>(text.size());
	if (position >= size)
		return size;
	uint32_t index = position + 1;
	while (index < size && IsContinuationByte(text[index]))
		index++;
	return index;
}

// Spaces are the only word breaks here; every step is a whole character.
uint32_t PreviousWord(const std::string& text, uint32_t position)
{
	while (position > 0 && text[PreviousBoundary(text, position)] == ' ')
		position = PreviousBoundary(text, position);
	while (position > 0 && text[PreviousBoundary(text, position)] != ' ')
		position = PreviousBoundary(text, position);
	return position;
}

uint32_t NextWord(const std::string& text, uint32_t position)
{
	const uint32_t size = static_cast<uint32_t>(text.size());
	while (position < size && text[position] != ' ')
		position = NextBoundary(text, position);
	while (position < size && text[position] == ' ')
		position = NextBoundary(text, position);
	return position;
}

int main()
{
	const std::string text = "h\xC3\xA9llo w\xC3\xB6rld"; // "héllo wörld": 13 bytes, 11 characters
	uint32_t caret = static_cast<uint32_t>(text.size());
	for (int step = 0; step < 3; step++)
	{
		caret = PreviousWord(text, caret);
		std::printf("Ctrl+Left  -> caret %u\n", caret);
	}
	for (int step = 0; step < 3; step++)
	{
		caret = NextWord(text, caret);
		std::printf("Ctrl+Right -> caret %u\n", caret);
	}
	return 0;
}
