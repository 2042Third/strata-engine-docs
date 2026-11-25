// A toy of the engine's error policy: an assert that a Dist build removes, a verify that stays,
// a returned error, and a logger with two levels.
#include <cstdio>
#include <optional>
#include <string>
#include <vector>

namespace
{
	enum class LogLevel
	{
		Info,
		Error
	};

	int s_FailedChecks = 0;

	void Log(LogLevel level, const std::string& message)
	{
		std::printf("[%s] %s\n", level == LogLevel::Info ? "info" : "error", message.c_str());
	}

	void ReportCheck(const char* kind, const char* condition)
	{
		s_FailedChecks++;
		Log(LogLevel::Error, std::string(kind) + " '" + condition + "' failed");
	}
}

// A failed check calls the report; do-while makes the macro one statement.
#define TOY_CHECK(kind, condition) \
	do \
	{ \
		if (!(condition)) \
			ReportCheck(kind, #condition); \
	} while (false)

#if defined(TOY_DIST)
	#define TOY_ASSERT(condition) ((void)0)
#else
	#define TOY_ASSERT(condition) TOY_CHECK("Assertion", condition)
#endif
#define TOY_VERIFY(condition) TOY_CHECK("Verify", condition)

namespace
{
	// A recoverable failure: the caller receives "no value", and the log says why.
	std::optional<int> ParseCount(const std::string& text)
	{
		if (text.empty() || text.size() > 6 || text.find_first_not_of("0123456789") != std::string::npos)
		{
			Log(LogLevel::Error, "ParseCount: '" + text + "' is no count");
			return std::nullopt;
		}
		return std::stoi(text);
	}
}

int main()
{
	for (const char* line : { "42", "4x2" })
	{
		const std::optional<int> count = ParseCount(line);
		if (count)
			Log(LogLevel::Info, "count " + std::to_string(*count));
	}

	const std::vector<int> values = { 10, 20, 30 };
	const size_t index = 3;
	TOY_ASSERT(index < values.size()); // a programmer error: the caller asked past the end
	const int* registry = nullptr;
	TOY_VERIFY(registry != nullptr); // a start-up step that must have run, in every build

	int checks = 0;
	TOY_ASSERT(++checks > 0); // a side effect inside an assert
	std::printf("failed checks %d, side effect ran %d time(s)\n", s_FailedChecks, checks);
	return 0;
}
