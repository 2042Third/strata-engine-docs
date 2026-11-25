// A source-scan rule with its self-test: no fixed pixel width given to SetNextItemWidth.
#include <cstdio>
#include <regex>
#include <string>

int CountFixedWidths(const std::string& code)
{
	static const std::regex fixedWidth(R"(\bSetNextItemWidth\s*\(\s*\d)");
	int count = 0;
	for (std::sregex_iterator it(code.begin(), code.end(), fixedWidth), end; it != end; ++it)
		count++;
	return count;
}

int main()
{
	std::printf("fixed: %d\n", CountFixedWidths("ImGui::SetNextItemWidth(120.0f);"));
	std::printf("scaled: %d\n", CountFixedWidths("ImGui::SetNextItemWidth(ImGui::GetFontSize() * 8.0f);"));
	std::printf("fill: %d\n", CountFixedWidths("ImGui::SetNextItemWidth(-FLT_MIN);"));
	std::printf("two: %d\n", CountFixedWidths("SetNextItemWidth(4);\nSetNextItemWidth(9);"));
	return 0;
}
