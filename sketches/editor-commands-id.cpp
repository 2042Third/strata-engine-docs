#include <cstdio>
#include <string_view>

namespace Exercise
{

	// Exactly 16 hexadecimal digits, either case, and not all zeros.
	bool IsEntityId(std::string_view text)
	{
		if (text.size() != 16)
			return false;
		bool anyNonZero = false;
		for (const char c : text)
		{
			const bool digit = c >= '0' && c <= '9';
			const bool lower = c >= 'a' && c <= 'f';
			const bool upper = c >= 'A' && c <= 'F';
			if (!digit && !lower && !upper)
				return false;
			if (c != '0')
				anyNonZero = true;
		}
		return anyNonZero;
	}

}

int main()
{
	const std::string_view samples[] = { "0123456789abcdef", "0123456789ABCDEF", "0000000000000000", "0123456789abcde", "0123456789abcdeg", "" };
	for (const std::string_view sample : samples)
		std::printf("'%.*s' -> %s\n", static_cast<int>(sample.size()), sample.data(), Exercise::IsEntityId(sample) ? "valid" : "refused");
	return 0;
}
