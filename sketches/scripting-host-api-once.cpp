#include <cstddef>
#include <cstdio>
#include <set>
#include <string>

constexpr size_t c_MaxProblems = 3;
static std::set<std::string> s_Reported;

// Reports a problem once per text, and stops at c_MaxProblems distinct texts.
static void ReportProblem(const std::string& function, const std::string& message)
{
	const std::string text = function + ": " + message;
	if (s_Reported.size() >= c_MaxProblems)
		return;
	if (!s_Reported.insert(text).second)
		return;

	std::printf("warning: %s\n", text.c_str());
	if (s_Reported.size() == c_MaxProblems)
		std::printf("further problems are not reported\n");
}

int main()
{
	ReportProblem("SetTimeScale", "negative");
	ReportProblem("SetTimeScale", "negative");
	ReportProblem("Instantiate", "not loaded");
	ReportProblem("Raycast", "zero direction");
	ReportProblem("GetProperty", "no such property");
	return 0;
}
