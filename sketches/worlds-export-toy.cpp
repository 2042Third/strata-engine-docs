// A toy export: checks before work, a state per frame, and every failure before the first write.
#include <cstdio>
#include <string>
#include <vector>

enum class State
{
	WaitingForImports,
	Packing,
	Succeeded,
	Failed
};

struct Project
{
	bool SceneSaved = true;
	int PendingImports = 2;
	bool IconDecodes = true;
};

const char* ToString(State state)
{
	switch (state)
	{
		case State::WaitingForImports: return "WaitingForImports";
		case State::Packing: return "Packing";
		case State::Succeeded: return "Succeeded";
		case State::Failed: return "Failed";
	}
	return "Unknown";
}

// Start reads no file and writes nothing: a refusal leaves the disk as it was.
bool Start(const Project& project, std::string& error)
{
	if (!project.SceneSaved)
	{
		error = "The open scene has unsaved changes";
		return false;
	}
	return true;
}

// The write job: whatever can fail comes before the first write.
bool Write(const Project& project, std::vector<std::string>& folder)
{
	if (!project.IconDecodes)
		return false;
	folder.push_back("Game.stpak");
	folder.push_back("Game.stgame");
	folder.push_back("Game.exe");
	return true;
}

// One call per frame: each state does a little work and names the next state.
State Update(State state, Project& project, std::vector<std::string>& folder)
{
	if (state == State::WaitingForImports)
	{
		if (project.PendingImports > 0)
		{
			project.PendingImports--;
			return state;
		}
		return State::Packing;
	}
	if (state == State::Packing)
		return Write(project, folder) ? State::Succeeded : State::Failed;
	return state;
}

void Run(const char* name, Project project)
{
	std::string error;
	std::vector<std::string> folder;
	std::printf("%s\n", name);
	if (!Start(project, error))
	{
		std::printf("  refused: %s\n", error.c_str());
		return;
	}
	State state = State::WaitingForImports;
	for (int frame = 1; state != State::Succeeded && state != State::Failed; frame++)
	{
		state = Update(state, project, folder);
		std::printf("  frame %d: %s\n", frame, ToString(state));
	}
	std::printf("  files written: %zu\n", folder.size());
}

int main()
{
	Run("Good project", Project { true, 2, true });
	Run("Unsaved scene", Project { false, 0, true });
	Run("Broken icon", Project { true, 0, false });
	return 0;
}
