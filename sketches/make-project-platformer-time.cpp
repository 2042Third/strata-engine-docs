// The course's clock text: minutes, seconds and tenths from a count of seconds, with integer division and the
// remainder operator only.

#include <algorithm>
#include <cstdio>
#include <string>

std::string FormatTime(float seconds)
{
	// Count whole tenths first: one rounding, then every other step is exact integer arithmetic.
	const int tenths = static_cast<int>(std::max(0.0f, seconds) * 10.0f + 0.5f);
	const int wholeSeconds = (tenths / 10) % 60;
	std::string text = std::to_string(tenths / 600) + ":";
	if (wholeSeconds < 10)
		text += "0";
	return text + std::to_string(wholeSeconds) + "." + std::to_string(tenths % 10);
}

int main()
{
	const float samples[] = { 0.0f, 9.96f, 65.3f, 600.0f };
	for (const float seconds : samples)
		std::printf("%7.2f seconds read %s\n", seconds, FormatTime(seconds).c_str());
	return 0;
}
