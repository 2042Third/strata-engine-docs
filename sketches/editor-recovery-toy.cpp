// A toy recovery journal: steps that create, remove or move no entity fold into the segment before them.
#include <cstdio>
#include <map>
#include <string>
#include <vector>

struct State
{
	int Id;
	bool Exists;
	int Parent;
	std::string Value;
};

// What one undo step left (After) and what the same entities held before it (Before).
struct Step
{
	std::vector<State> Before;
	std::vector<State> After;
};

// The latest state of every entity the segment touched, in the order of the entity ids.
using Segment = std::map<int, State>;

bool IsStructural(const Step& step)
{
	if (step.Before.size() != step.After.size())
		return true;
	for (size_t index = 0; index < step.After.size(); index++)
	{
		const State& before = step.Before[index];
		const State& after = step.After[index];
		if (after.Id != before.Id || after.Exists != before.Exists)
			return true;
		if (after.Exists && after.Parent != before.Parent)
			return true;
	}
	return false;
}

std::vector<Segment> Fold(const std::vector<Step>& steps)
{
	std::vector<Segment> segments;
	for (const Step& step : steps)
	{
		if (segments.empty() || IsStructural(step))
			segments.emplace_back();
		for (const State& state : step.After)
			segments.back()[state.Id] = state;
	}
	return segments;
}

int main()
{
	const State none1 = { 1, false, 0, "" };
	const State none2 = { 2, false, 0, "" };
	const std::vector<Step> steps = {
		{ { none1 }, { { 1, true, 0, "a0" } } },
		{ { { 1, true, 0, "a0" } }, { { 1, true, 0, "a1" } } },
		{ { { 1, true, 0, "a1" } }, { { 1, true, 0, "a2" } } },
		{ { none2 }, { { 2, true, 0, "b0" } } },
		{ { { 2, true, 0, "b0" } }, { { 2, true, 0, "b1" } } },
		{ { { 2, true, 0, "b1" } }, { { 2, true, 1, "b1" } } },
		{ { { 1, true, 0, "a2" } }, { { 1, true, 0, "a3" } } } };

	const std::vector<Segment> segments = Fold(steps);
	std::printf("%zu steps became %zu segments\n", steps.size(), segments.size());
	for (size_t index = 0; index < segments.size(); index++)
	{
		std::printf("segment %zu:", index + 1);
		for (const auto& [id, state] : segments[index])
			std::printf(" [entity %d, parent %d, %s]", id, state.Parent, state.Value.c_str());
		std::printf("\n");
	}
}
