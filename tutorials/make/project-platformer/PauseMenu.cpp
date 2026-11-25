// The pause menu, on the "Game" entity: the Pause action opens it at time scale 0 with the cursor free; its three
// buttons resume, restart the course or return to the main menu.

#include "StrataScript/StrataScript.h"

using namespace Strata;

class PauseMenu : public Script
{
public:
	AssetHandle MainMenuScene;
	Entity Panel;
	Entity ResumeButton;
	Entity RestartButton;
	Entity MenuButton;
	bool Paused = false;

	void OnCreate() override
	{
		Paused = false;
		if (Panel.IsValid())
			Panel.SetActive(false);
	}

	void OnUpdate(float) override
	{
		if (Input::IsActionPressed("Gameplay/Pause"))
			SetPaused(!Paused);
	}

	void OnUIClick(Entity widget) override
	{
		if (widget == ResumeButton)
		{
			SetPaused(false);
		}
		else if (widget == RestartButton)
		{
			Time::SetTimeScale(1.0f);
			Game::ReloadScene();
		}
		else if (widget == MenuButton)
		{
			Time::SetTimeScale(1.0f);
			Game::LoadScene(MainMenuScene);
		}
	}

private:
	void SetPaused(bool paused)
	{
		Paused = paused;
		Time::SetTimeScale(paused ? 0.0f : 1.0f);
		Panel.SetActive(paused);
		if (paused)
		{
			Input::SetCursorMode(CursorMode::Normal);
			ResumeButton.GetUI().Focus();
		}
		else
		{
			Input::SetCursorMode(CursorMode::Locked);
			UI::ClearFocus();
		}
	}
};

ST_SCRIPT_CLASS(PauseMenu)
{
	ST_SCRIPT_FIELD(MainMenuScene);
	ST_SCRIPT_FIELD(Panel);
	ST_SCRIPT_FIELD(ResumeButton);
	ST_SCRIPT_FIELD(RestartButton);
	ST_SCRIPT_FIELD(MenuButton);
	ST_SCRIPT_FIELD(Paused);
}
