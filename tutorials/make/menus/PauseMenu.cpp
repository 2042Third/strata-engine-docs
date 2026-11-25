#include "StrataScript/StrataScript.h"

using namespace Strata;

// The pause menu: the Pause action opens it, Resume closes it.
class PauseMenu : public Script
{
public:
	Entity Panel;
	Entity ResumeButton;

	void OnCreate() override
	{
		m_Paused = false;
		if (Panel.IsValid())
			Panel.SetActive(false);
	}

	void OnUpdate(float) override
	{
		if (Input::IsActionPressed("Gameplay/Pause"))
			SetPaused(!m_Paused);
	}

	void OnUIClick(Entity widget) override
	{
		if (widget == ResumeButton)
			SetPaused(false);
	}

private:
	void SetPaused(bool paused)
	{
		m_Paused = paused;
		Time::SetTimeScale(paused ? 0.0f : 1.0f);
		Panel.SetActive(paused);
		if (paused)
		{
			m_CursorBefore = Input::GetCursorMode();
			Input::SetCursorMode(CursorMode::Normal);
			ResumeButton.GetUI().Focus();
		}
		else
		{
			Input::SetCursorMode(m_CursorBefore);
			UI::ClearFocus();
		}
	}

	bool m_Paused = false;
	CursorMode m_CursorBefore = CursorMode::Normal;
};

ST_SCRIPT_CLASS(PauseMenu)
{
	ST_SCRIPT_FIELD(Panel);
	ST_SCRIPT_FIELD(ResumeButton);
}
