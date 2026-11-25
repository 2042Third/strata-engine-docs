// A toy command script runner: steps with expect, bind and a reference to a bound value.
#include <cstdio>
#include <limits>
#include <map>
#include <string>
#include <vector>

namespace
{
	constexpr double c_Infinity = std::numeric_limits<double>::infinity();

	// A result maps a JSON pointer to a number: a stand-in for a JSON document.
	using Result = std::map<std::string, double>;

	struct Step
	{
		std::string Command;
		std::string Ref;         // The name of a bound value this step uses; empty for none
		double Number = 0.0;     // Another parameter, such as the count of steps
		std::string Pointer;     // Where to look in the result for the expectation
		double Min = -c_Infinity;
		double Max = c_Infinity;
		std::string BindName;    // A name for the "/id" of the result; empty for none
	};

	// A fake world: every entity starts 10 m up and falls under gravity as steps run.
	Result RunCommand(const Step& step, int& nextId, int& stepsRun)
	{
		if (step.Command == "create")
			return { { "/id", nextId++ } };
		if (step.Command == "step")
		{
			stepsRun += static_cast<int>(step.Number);
			return { { "/stepsRun", stepsRun } };
		}
		const double seconds = stepsRun / 60.0;
		return { { "/y", 10.0 - 0.5 * 9.81 * seconds * seconds } };
	}

	bool RunScript(const char* title, const std::vector<Step>& steps)
	{
		std::printf("%s\n", title);
		std::map<std::string, int> bindings;
		bool failed = false;
		int nextId = 100;
		int stepsRun = 0;
		for (size_t index = 0; index < steps.size(); index++)
		{
			const Step& step = steps[index];
			if (!step.Ref.empty())
			{
				if (bindings.find(step.Ref) == bindings.end())
				{
					std::printf("  step %zu %s: no value for the reference '%s', not run\n", index + 1, step.Command.c_str(), step.Ref.c_str());
					failed = true;
					continue;
				}
			}
			const Result result = RunCommand(step, nextId, stepsRun);
			bool met = true;
			if (!step.Pointer.empty())
			{
				const double value = result.at(step.Pointer);
				met = value >= step.Min && value <= step.Max;
				std::printf("  step %zu %s: %s = %.2f %s\n", index + 1, step.Command.c_str(), step.Pointer.c_str(), value, met ? "ok" : "FAILED");
			}
			if (!met)
				failed = true;
			if (!step.BindName.empty())
			{
				if (met)
					bindings[step.BindName] = static_cast<int>(result.at("/id"));
				else
					bindings.erase(step.BindName); // Later steps must not use a value of a failed step
			}
		}
		return !failed;
	}
}

int main()
{
	const bool first = RunScript("Script 1: a ball falls for one second", {
		{ "create", "", 0.0, "/id", 100.0, 100.0, "ball" },
		{ "step", "", 60.0, "/stepsRun", 60.0, 60.0, "" },
		{ "get", "ball", 0.0, "/y", 4.0, 6.0, "" },
		{ "get", "ball", 0.0, "/y", 9.0, 11.0, "" },
		{ "get", "ball", 0.0, "/y", 4.0, 6.0, "" } });
	const bool second = RunScript("Script 2: the step that binds fails", {
		{ "create", "", 0.0, "/id", 500.0, 500.0, "ball" },
		{ "get", "ball", 0.0, "/y", 9.0, 11.0, "" } });
	std::printf("exit code %d\n", first && second ? 0 : 1);
	return 0;
}
