#include "StrataScript/StrataScript.h"

#include <cmath>
#include <cstdint>
#include <string>

using namespace Strata;

// The HUD of Coin Run. The planted bug: the count runs after the fixed updates, where a collected coin still exists.
class CoinHud : public Script
{
public:
	float TimeLimit = 60.0f; // Seconds the player has

	void OnLateUpdate(float) override
	{
		const size_t left = Scene::FindEntitiesByTag("Coin").size();
		if (left != m_Shown)
		{
			m_Shown = left;
			m_CoinText.GetUI().SetText("Coins left: " + std::to_string(left));
			Log::Info("HUD shows ", left, " coins in frame ", Time::GetFrameIndex());
		}
	}

	void OnCreate() override { FindParts(); }
	void OnReload() override { FindParts(); }

	void OnUpdate(float) override
	{
		const float timeLeft = glm::max(TimeLimit - static_cast<float>(Time::GetElapsedTime()), 0.0f);
		m_TimerText.GetUI().SetText("Time: " + std::to_string(static_cast<int>(std::ceil(timeLeft))));
		m_TimeBar.SetProperty("UIImage", "FillAmount", timeLeft / TimeLimit);

		const bool low = timeLeft < 10.0f;
		if (low != m_Low)
		{
			m_Low = low;
			m_TimerText.GetUI().SetColor(low ? glm::vec4(1.0f, 0.3f, 0.2f, 1.0f) : glm::vec4(1.0f));
		}
	}

private:
	void FindParts()
	{
		m_CoinText = Scene::FindEntityByName("CoinText");
		m_TimerText = Scene::FindEntityByName("TimerText");
		m_TimeBar = Scene::FindEntityByName("TimeBar");
	}

	Entity m_CoinText;
	Entity m_TimerText;
	Entity m_TimeBar;
	size_t m_Shown = SIZE_MAX;
	bool m_Low = false;
};

ST_SCRIPT_CLASS(CoinHud)
{
	ST_SCRIPT_FIELD(TimeLimit);
}
