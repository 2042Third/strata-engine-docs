#include <cstdint>
#include <cstdio>
#include <string>

constexpr float c_CharacterWidth = 10.0f;
constexpr float c_BoxWidth = 50.0f;
constexpr float c_CaretWidth = 2.0f;

struct ToyField
{
	std::string Text;
	uint32_t Caret = 0; // A byte offset, always on a character boundary
	float Scroll = 0.0f;
};

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

// Where the caret stands on the line: every character is the same width here.
float CaretX(const ToyField& field)
{
	float x = 0.0f;
	for (uint32_t index = 0; index < field.Caret; index++)
	{
		if (!IsContinuationByte(field.Text[index]))
			x += c_CharacterWidth;
	}
	return x;
}

void KeepCaretInView(ToyField& field)
{
	const float caret = CaretX(field);
	if (caret < field.Scroll)
		field.Scroll = caret;
	if (caret + c_CaretWidth - c_BoxWidth > field.Scroll)
		field.Scroll = caret + c_CaretWidth - c_BoxWidth;
}

void Insert(ToyField& field, const std::string& typed)
{
	field.Text.insert(field.Caret, typed);
	field.Caret += static_cast<uint32_t>(typed.size());
	KeepCaretInView(field);
}

void Backspace(ToyField& field)
{
	const uint32_t start = PreviousBoundary(field.Text, field.Caret);
	field.Text.erase(start, field.Caret - start);
	field.Caret = start;
	KeepCaretInView(field);
}

void Print(const char* step, const ToyField& field)
{
	std::printf("%-12s text=\"%s\" bytes=%zu caret=%u scroll=%.0f\n", step, field.Text.c_str(), field.Text.size(), field.Caret, field.Scroll);
}

int main()
{
	ToyField field;
	Insert(field, "ab");
	Insert(field, "\xC3\xA9"); // e with an acute accent: two bytes, one character
	Print("type ab, e'", field);
	Backspace(field);
	Print("backspace", field);
	Insert(field, "cdefg");
	Print("type cdefg", field);
	return 0;
}
