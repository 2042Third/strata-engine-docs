// Which documents does an undo step make dirty? A state names the cell of its entity, or -1 for the persistent scene.
#include <cstdio>
#include <set>
#include <vector>

struct State
{
	bool Exists = false;
	int Cell = -1;
};

struct Step
{
	const char* Name = "";
	std::vector<State> Before;
	std::vector<State> After;
};

static void MarkStates(const std::vector<State>& states, std::set<int>& dirtyCells, bool& persistentDirty)
{
	for (const State& state : states)
	{
		if (state.Cell >= 0)
			dirtyCells.insert(state.Cell);
		else
			persistentDirty = true;
	}
}

int main()
{
	const std::vector<Step> steps = {
		{ "move a crate from cell 0 to cell 1", { { true, 0 } }, { { true, 1 } } },
		{ "create a crate in cell 2", { { false, 2 } }, { { true, 2 } } },
		{ "move the persistent camera", { { true, -1 } }, { { true, -1 } } },
	};
	std::set<int> dirtyCells;
	bool persistentDirty = false;
	for (const Step& step : steps)
	{
		MarkStates(step.Before, dirtyCells, persistentDirty);
		MarkStates(step.After, dirtyCells, persistentDirty);
		std::printf("after \"%s\": %zu dirty cell(s), persistent %s\n", step.Name, dirtyCells.size(), persistentDirty ? "dirty" : "clean");
	}
	return 0;
}
