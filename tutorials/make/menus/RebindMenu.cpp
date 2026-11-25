#include "StrataScript/StrataScript.h"

#include <array>
#include <optional>
#include <string>

using namespace Strata;

// The rebinding screen: one row per action, a button that listens for the next control and a Reset button.
class RebindMenu : public Script
{
public:
	Entity Panel;
	Entity JumpButton;
	Entity JumpText;
	Entity BoostButton;
	Entity BoostText;
	Entity ResetButton;
	Entity BackButton;
	float TimeoutSeconds = 5.0f;

	void OnCreate() override
	{
		m_Rows[0] = { JumpButton, JumpText, "Gameplay/Jump" };
		m_Rows[1] = { BoostButton, BoostText, "Gameplay/Boost" };
		ShowBindings();
	}

	void OnUIClick(Entity widget) override
	{
		if (widget == ResetButton)
		{
			Input::ResetActionBindings();
			ShowBindings();
		}
		else if (widget == BackButton)
		{
			Input::CancelBindingCapture();
			Input::SaveBindings();
			Panel.SetActive(false);
		}
		else
			StartListening(widget);
	}

	void OnUpdate(float) override
	{
		if (m_Listening < 0)
			return;
		const std::optional<std::string> binding = Input::PollBindingCapture();
		if (binding)
			Input::SetActionBindings(m_Rows[m_Listening].Action, { *binding });
		else if (Time::GetRealTime() - m_ListenStart < TimeoutSeconds)
			return;
		else
			Input::CancelBindingCapture();
		m_Listening = -1;
		ShowBindings();
	}

private:
	struct Row
	{
		Entity Button;
		Entity Text;
		const char* Action;
	};

	void StartListening(Entity widget)
	{
		for (size_t i = 0; i < m_Rows.size(); i++)
		{
			if (widget != m_Rows[i].Button || !Input::BeginBindingCapture())
				continue;
			m_Listening = static_cast<int>(i);
			m_ListenStart = Time::GetRealTime();
			m_Rows[i].Text.GetUI().SetText("Press a control...");
		}
	}

	void ShowBindings()
	{
		for (const Row& row : m_Rows)
		{
			std::string text;
			for (const std::string& binding : Input::GetActionBindings(row.Action))
				text += (text.empty() ? "" : ", ") + binding;
			row.Text.GetUI().SetText(text.empty() ? "Unbound" : text);
		}
	}

	std::array<Row, 2> m_Rows;
	int m_Listening = -1;
	double m_ListenStart = 0.0;
};

ST_SCRIPT_CLASS(RebindMenu)
{
	ST_SCRIPT_FIELD(Panel);
	ST_SCRIPT_FIELD(JumpButton);
	ST_SCRIPT_FIELD(JumpText);
	ST_SCRIPT_FIELD(BoostButton);
	ST_SCRIPT_FIELD(BoostText);
	ST_SCRIPT_FIELD(ResetButton);
	ST_SCRIPT_FIELD(BackButton);
	ST_SCRIPT_FIELD(TimeoutSeconds);
}
