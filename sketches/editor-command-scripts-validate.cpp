// Checks the references of a script against the names earlier steps bind, before anything runs.
#include <cstdio>
#include <set>
#include <string>
#include <vector>

namespace
{
	struct Step
	{
		std::string Command;
		std::string Ref;      // A bound name this step uses; empty for none
		std::string BindName; // A name this step binds; empty for none
	};

	// Returns an empty string when every reference names a value that an earlier step binds.
	std::string CheckReferences(const std::vector<Step>& steps)
	{
		std::set<std::string> bound;
		for (size_t index = 0; index < steps.size(); index++)
		{
			const Step& step = steps[index];
			if (!step.Ref.empty() && bound.count(step.Ref) == 0)
				return "step " + std::to_string(index + 1) + " (" + step.Command + "): no earlier step binds '" + step.Ref + "'";
			if (!step.BindName.empty())
				bound.insert(step.BindName);
		}
		return "";
	}
}

int main()
{
	const std::vector<Step> good = { { "create", "", "ball" }, { "get", "ball", "" } };
	const std::vector<Step> late = { { "get", "ball", "" }, { "create", "", "ball" } };
	const std::vector<Step> typo = { { "create", "", "ball" }, { "get", "bal", "" } };
	for (const std::vector<Step>* script : { &good, &late, &typo })
	{
		const std::string error = CheckReferences(*script);
		std::printf("%s\n", error.empty() ? "ok: the script may run" : error.c_str());
	}
	return 0;
}
