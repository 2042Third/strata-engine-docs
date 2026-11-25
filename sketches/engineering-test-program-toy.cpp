// A test runner whose program is also the child process its tests start: one helper mode, selected by an argument.
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <string>
#include <string_view>
#include <vector>

struct TestCase
{
	std::string Suite;
	std::string Name;
	std::function<bool()> Body;
};

static std::string s_Self;

// The helper mode: stands in for an outside program and ends with the exit code it is told.
static int RunHelperMode(std::string_view mode, int argc, char** argv)
{
	if (mode == "exit-code" && argc > 2)
		return std::atoi(argv[2]);
	std::fprintf(stderr, "unknown helper mode '%s'\n", std::string(mode).c_str());
	return 99;
}

// A test starts the helper as a child: this program again, with the helper argument.
static int RunHelper(const std::string& arguments)
{
	return std::system(("\"" + s_Self + "\" --toy-helper=" + arguments).c_str());
}

int main(int argc, char** argv)
{
	constexpr std::string_view helperPrefix = "--toy-helper=";
	if (argc > 1 && std::string_view(argv[1]).substr(0, helperPrefix.size()) == helperPrefix)
		return RunHelperMode(std::string_view(argv[1]).substr(helperPrefix.size()), argc, argv);
	s_Self = argv[0];

	const std::vector<TestCase> tests = {
		{ "Math", "Addition", []() { return 1 + 1 == 2; } },
		{ "Process", "A child that succeeds", []() { return RunHelper("exit-code 0") == 0; } },
		{ "Process", "A child that fails", []() { return RunHelper("exit-code 7") != 0; } },
	};
	int failures = 0;
	for (const TestCase& test : tests)
	{
		const bool passed = test.Body();
		std::printf("[%s] %s / %s\n", passed ? "passed" : "FAILED", test.Suite.c_str(), test.Name.c_str());
		failures += passed ? 0 : 1;
	}
	return failures;
}
