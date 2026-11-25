// A key press goes to the first owner that wants it: a modal, the game, a text field, the focused panel, then global shortcuts.
#include <cstdio>
#include <string>

enum class Owner
{
	Modal,
	Game,
	TextField,
	FocusedPanel,
	Global,
	Nobody
};

struct Situation
{
	bool Modal;
	bool GameInput;
	bool TextFocus;
	bool PanelFocus;
	bool KeyIsGlobal;
};

Owner Route(const Situation& situation)
{
	if (situation.Modal)
		return Owner::Modal;
	if (situation.GameInput)
		return Owner::Game;
	if (situation.TextFocus)
		return Owner::TextField;
	if (situation.PanelFocus)
		return Owner::FocusedPanel;
	return situation.KeyIsGlobal ? Owner::Global : Owner::Nobody;
}

std::string Name(Owner owner)
{
	switch (owner)
	{
		case Owner::Modal:        return "modal";
		case Owner::Game:         return "game";
		case Owner::TextField:    return "text field";
		case Owner::FocusedPanel: return "focused panel";
		case Owner::Global:       return "global shortcut";
		case Owner::Nobody:       return "nobody";
	}
	return "nobody";
}

int main()
{
	const Situation delete1 = { false, false, false, true, false };
	const Situation delete2 = { false, false, true, true, false };
	const Situation delete3 = { false, true, false, false, false };
	const Situation save = { false, false, false, false, true };
	const Situation saveInDialog = { true, false, false, false, true };
	std::printf("Delete in the Hierarchy: %s\n", Name(Route(delete1)).c_str());
	std::printf("Delete while renaming: %s\n", Name(Route(delete2)).c_str());
	std::printf("Delete while the game plays: %s\n", Name(Route(delete3)).c_str());
	std::printf("Ctrl+S: %s\n", Name(Route(save)).c_str());
	std::printf("Ctrl+S in a dialog: %s\n", Name(Route(saveInDialog)).c_str());
	return 0;
}
