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
	float TimeLimit = 40.0f; // Seconds the player has on Normal
	int32_t Difficulty = 1;  // 0 Easy, 1 Normal, 2 Hard

	void OnCreate() override
	{
		// A restart loads the scene again; the time scale of the finished round must not follow it.
		Time::SetTimeScale(1.0f);
		m_TotalTime = TimeLimit * GetTimeFactor();
		m_TimeLeft = m_TotalTime;
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
		const size_t smallLeft = Scene::FindEntitiesByTag("Coin").size();
		const size_t bigLeft = Scene::FindEntitiesByTag("BigCoin").size();
		const size_t coinsLeft = smallLeft + bigLeft;
		m_SmallTotal = std::max(m_SmallTotal, smallLeft);
		m_BigTotal = std::max(m_BigTotal, bigLeft);
		// CoinPlacer adds the coins after the first frames: an empty level is not a won round.
		m_CoinsSeen = m_CoinsSeen || coinsLeft > 0;
		m_TimeLeft = std::max(0.0f, m_TimeLeft - deltaTime);
		// A small coin is worth 1 point, a big one 5.
		ShowHud(coinsLeft, (m_SmallTotal - smallLeft) + 5 * (m_BigTotal - bigLeft));

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
		m_ScoreText = Scene::FindEntityByName("ScoreText");
		// The finds see inactive entities too, so a hidden panel is found by its name.
		m_WinPanel = Scene::FindEntityByName("WinPanel");
		m_LosePanel = Scene::FindEntityByName("LosePanel");
	}

	void ShowHud(size_t coinsLeft, size_t score)
	{
		m_ScoreText.GetUI().SetText("Score: " + std::to_string(score));
		m_CoinText.GetUI().SetText("Coins left: " + std::to_string(coinsLeft));
		m_TimerText.GetUI().SetText("Time: " + std::to_string(static_cast<int>(std::ceil(m_TimeLeft))));
		m_TimeBar.SetProperty("UIImage", "FillAmount", m_TimeLeft / m_TotalTime);
		ShowTimeColor();
	}

	// Easy gives half as much time again, Hard a third less.
	float GetTimeFactor() const
	{
		static const float c_Factors[] = { 1.5f, 1.0f, 0.67f };
		return c_Factors[std::clamp(Difficulty, 0, 2)];
	}

	// White, then yellow at 20 seconds left, then red at 10; the colors change only when the stage does.
	void ShowTimeColor()
	{
		glm::vec4 color(1.0f);
		if (m_TimeLeft <= 10.0f)
			color = glm::vec4(1.0f, 0.2f, 0.2f, 1.0f);
		else if (m_TimeLeft <= 20.0f)
			color = glm::vec4(1.0f, 0.85f, 0.2f, 1.0f);
		if (color == m_TimeColor)
			return;
		m_TimeColor = color;
		m_TimerText.GetUI().SetColor(color);
		m_TimeBar.GetUI().SetColor(color);
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
	float m_TotalTime = 1.0f;
	glm::vec4 m_TimeColor = glm::vec4(1.0f);
	bool m_CoinsSeen = false;
	size_t m_SmallTotal = 0;
	size_t m_BigTotal = 0;
	AssetHandle m_WinSound;
	Entity m_CoinText;
	Entity m_TimerText;
	Entity m_TimeBar;
	Entity m_ScoreText;
	Entity m_WinPanel;
	Entity m_LosePanel;
};

ST_SCRIPT_CLASS(CoinRunGame)
{
	ST_SCRIPT_FIELD(TimeLimit);
	ST_SCRIPT_FIELD(Difficulty);
}
