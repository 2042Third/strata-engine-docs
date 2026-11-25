// The round of Coin Run: its state, the time left, and the HUD that shows them. Attach it to the empty entity Game.

#include "StrataScript/StrataScript.h"

#include <algorithm>
#include <cmath>
#include <string>

using namespace Strata;

enum class RoundState
{
	Playing,
	Won,
	Lost
};

class CoinRunGame : public Script
{
public:
	float TimeLimit = 40.0f; // Seconds the player has

	void OnCreate() override
	{
		m_TimeLeft = TimeLimit;
		FindParts();
	}

	void OnReload() override { FindParts(); }

	void OnUpdate(float deltaTime) override
	{
		if (m_State != RoundState::Playing)
			return;

		// A coin destroyed in this frame still counts until the frame ends: the round sees it gone one frame later.
		const size_t coinsLeft = Scene::FindEntitiesByTag("Coin").size();
		// CoinPlacer adds the coins after the first frames: an empty level is not a won round.
		m_CoinsSeen = m_CoinsSeen || coinsLeft > 0;
		m_TimeLeft = std::max(0.0f, m_TimeLeft - deltaTime);
		ShowHud(coinsLeft);

		if (m_CoinsSeen && coinsLeft == 0)
			Finish(RoundState::Won);
		else if (m_TimeLeft <= 0.0f)
			Finish(RoundState::Lost);
	}

private:
	void FindParts()
	{
		m_CoinText = Scene::FindEntityByName("CoinText");
		m_TimerText = Scene::FindEntityByName("TimerText");
		m_TimeBar = Scene::FindEntityByName("TimeBar");
	}

	void ShowHud(size_t coinsLeft)
	{
		m_CoinText.GetUI().SetText("Coins left: " + std::to_string(coinsLeft));
		m_TimerText.GetUI().SetText("Time: " + std::to_string(static_cast<int>(std::ceil(m_TimeLeft))));
		m_TimeBar.SetProperty("UIImage", "FillAmount", m_TimeLeft / TimeLimit);
	}

	void Finish(RoundState state)
	{
		m_State = state;
		Log::Info(state == RoundState::Won ? "Round won" : "Round lost");
	}

	RoundState m_State = RoundState::Playing;
	float m_TimeLeft = 0.0f;
	bool m_CoinsSeen = false;
	Entity m_CoinText;
	Entity m_TimerText;
	Entity m_TimeBar;
};

ST_SCRIPT_CLASS(CoinRunGame)
{
	ST_SCRIPT_FIELD(TimeLimit);
}
