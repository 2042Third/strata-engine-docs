// The toy start with a failure that tells the person why: the started steps end first, then the report is made.
#include <cstdio>
#include <string>
#include <vector>

namespace
{
	struct Step
	{
		std::string Name;
		bool Works = true;
		std::string Problem; // What the person reads when this step fails
		std::string Advice;
	};

	// The engine writes the message so: the problem, a blank line, the advice. The toy prints it instead of showing a dialog.
	void ReportFatalError(const std::string& title, const std::string& problem, const std::string& advice)
	{
		std::printf("  dialog titled '%s': %s", title.c_str(), problem.c_str());
		if (!advice.empty())
			std::printf(" | %s", advice.c_str());
		std::printf("\n");
	}

	// Starts the steps in order. A step that fails ends the ones before it, in reverse, and only then is the report made.
	int StartProgram(const std::string& name, const std::vector<Step>& steps)
	{
		std::vector<std::string> started;
		for (const Step& step : steps)
		{
			if (step.Works)
			{
				std::printf("  started %s\n", step.Name.c_str());
				started.push_back(step.Name);
				continue;
			}
			std::printf("  %s failed\n", step.Name.c_str());
			for (size_t index = started.size(); index > 0; index--)
				std::printf("  stopped %s\n", started[index - 1].c_str());
			ReportFatalError(name, step.Problem, step.Advice);
			return 1;
		}
		return 0;
	}
}

int main()
{
	const std::vector<Step> steps = { { "jobs", true, "", "" }, { "window", true, "", "" },
		{ "audio", false, "Toy cannot start: no sound device was found.", "Plug in speakers or start it with --no-audio." }, { "project", true, "", "" } };
	const int exitCode = StartProgram("Toy", steps);
	std::printf("  exit code %d\n", exitCode);
}
