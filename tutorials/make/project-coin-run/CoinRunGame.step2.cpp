// The round of Coin Run: its state, the time left, the HUD, the two end panels and the restart.
// Attach it to the empty entity Game.

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
		// A restart loads the scene again; the time scale of the finished round must not follow it.
		Time::SetTimeScale(1.0f);
		m_TimeLeft = TimeLimit;
		m_WinSound = Assets::Find("Sounds/Complete.ogg");
		Assets::RequestLoad(m_WinSound);
		FindParts();
		// The panels stay visible in the editor while you lay them out; the round hides them at its start.
		m_WinPanel.SetActive(false);
		m_LosePanel.SetActive(false);
	}

	void OnReload() override { FindParts(); }

	void OnUpdate(float deltaTime) override
	{
		// Read before the state check: the frozen game still hears the action.
		if (Input::IsActionPressed("Gameplay/Restart"))
		{
			Game::ReloadScene();
			return;
		}
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
		// The finds see inactive entities too, so a hidden panel is found by its name.
		m_WinPanel = Scene::FindEntityByName("WinPanel");
		m_LosePanel = Scene::FindEntityByName("LosePanel");
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
		// Scale 0 stops the ball, the coins and the timer; Update still runs, so Restart still works.
		Time::SetTimeScale(0.0f);
		if (state == RoundState::Won)
		{
			m_WinPanel.SetActive(true);
			Audio::PlayOneShot(m_WinSound);
		}
		else
			m_LosePanel.SetActive(true);
	}

	RoundState m_State = RoundState::Playing;
	float m_TimeLeft = 0.0f;
	bool m_CoinsSeen = false;
	AssetHandle m_WinSound;
	Entity m_CoinText;
	Entity m_TimerText;
	Entity m_TimeBar;
	Entity m_WinPanel;
	Entity m_LosePanel;
};

ST_SCRIPT_CLASS(CoinRunGame)
{
	ST_SCRIPT_FIELD(TimeLimit);
}
