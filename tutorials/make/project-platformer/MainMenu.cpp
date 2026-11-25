#include "StrataScript/StrataScript.h"

#include <string>

using namespace Strata;

// The main menu: one script for the whole menu, which the buttons name as their Event Target.
class MainMenu : public Script
{
public:
	AssetHandle Level;
	Entity PlayButton;

	void OnCreate() override
	{
		if (PlayButton.IsValid())
			PlayButton.GetUI().Focus();
	}

	void OnUIClick(Entity widget) override
	{
		const std::string name = widget.GetName();
		if (name == "Play")
			Game::LoadScene(Level);
		else if (name == "Quit")
			Game::Quit(0);
	}
};

ST_SCRIPT_CLASS(MainMenu)
{
	ST_SCRIPT_FIELD(Level);
	ST_SCRIPT_FIELD(PlayButton);
}
