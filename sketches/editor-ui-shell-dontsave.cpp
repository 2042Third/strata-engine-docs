// The Don't Save decision: the answer counts only for the changes the person was asked about.
#include <cstdint>
#include <cstdio>

struct Question
{
	uint64_t AskedVersion = 0;
	bool ChangedSince = false;
};

// Returns true when the pending action may run.
bool DontSave(Question& question, uint64_t undoVersion, bool modified)
{
	if (modified && undoVersion != question.AskedVersion)
	{
		question.AskedVersion = undoVersion;
		question.ChangedSince = true;
		return false;
	}
	return true;
}

int main()
{
	Question quiet { 7, false };
	std::printf("nothing changed: runs=%d\n", DontSave(quiet, 7, true));

	Question edited { 7, false };
	const bool firstRuns = DontSave(edited, 8, true);
	std::printf("an agent edited: runs=%d warning=%d\n", firstRuns, edited.ChangedSince);
	std::printf("second answer: runs=%d\n", DontSave(edited, 8, true));

	Question undone { 7, false };
	std::printf("edited, then undone and saved: runs=%d\n", DontSave(undone, 9, false));
	return 0;
}
