#include "StrataScript/StrataScript.h"

#include <cmath>
#include <string>

using namespace Strata;

// The HUD of Coin Run: the coins left, the seconds left and a bar for the time left.
class CoinHud : public Script
{
public:
	float TimeLimit = 60.0f; // Seconds the player has

	void OnCreate() override { FindParts(); }
	void OnReload() override { FindParts(); }

	void OnUpdate(float) override
	{
		const int coinsLeft = static_cast<int>(Scene::FindEntitiesByTag("Coin").size());
		m_CoinText.GetUI().SetText("Coins left: " + std::to_string(coinsLeft));

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
	bool m_Low = false;
};

ST_SCRIPT_CLASS(CoinHud)
{
	ST_SCRIPT_FIELD(TimeLimit);
}
