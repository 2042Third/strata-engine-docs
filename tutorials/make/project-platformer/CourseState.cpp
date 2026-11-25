#include "CourseState.h"

#include <algorithm>
#include <cstdlib>
#include <optional>
#include <string>
#include <string_view>

using namespace Strata;

namespace
{

	// The save file that keeps the best time of the course.
	constexpr std::string_view c_BestTimeFile = "best-time.txt";

	// Minutes, seconds and tenths: 65.3 seconds read "1:05.3".
	std::string FormatTime(float seconds)
	{
		const int tenths = static_cast<int>(std::max(0.0f, seconds) * 10.0f + 0.5f);
		const int wholeSeconds = (tenths / 10) % 60;
		std::string text = std::to_string(tenths / 600) + ":";
		if (wholeSeconds < 10)
			text += "0";
		return text + std::to_string(wholeSeconds) + "." + std::to_string(tenths % 10);
	}

}

void CourseState::OnCreate()
{
	TotalCoins = static_cast<int32_t>(Scene::FindEntitiesByTag("Coin").size());
	ReadBestTime();
	Assets::RequestLoad(CoinSound);
	Assets::RequestLoad(CompleteSound);
	if (CompletePanel.IsValid())
		CompletePanel.SetActive(false);
	Input::SetCursorMode(CursorMode::Locked);
	Time::SetTimeScale(1.0f);
	ShowHud();
}

void CourseState::OnUpdate(float deltaTime)
{
	if (!Completed)
		ElapsedSeconds += deltaTime;
	ShowHud();
}

void CourseState::OnUIClick(Entity widget)
{
	if (widget == PlayAgainButton)
	{
		Time::SetTimeScale(1.0f);
		Game::ReloadScene();
	}
	else if (widget == CompleteMenuButton)
	{
		Time::SetTimeScale(1.0f);
		Game::LoadScene(MainMenuScene);
	}
}

void CourseState::AddCoin(const glm::vec3& position)
{
	Coins++;
	if (CoinSound.IsValid())
		Audio::PlayOneShotAt(CoinSound, position, 0.8f);
	ShowHud();
}

void CourseState::Complete()
{
	if (Completed)
		return;
	Completed = true;
	const bool best = BestSeconds <= 0.0f || ElapsedSeconds < BestSeconds;
	if (best)
	{
		BestSeconds = ElapsedSeconds;
		if (!Game::WriteSaveFile(c_BestTimeFile, std::to_string(BestSeconds)))
			Log::Warn("Platformer: the best time could not be saved");
	}
	if (CompleteSound.IsValid())
		Audio::PlayOneShot(CompleteSound, 0.8f);
	if (CompletePanel.IsValid())
		CompletePanel.SetActive(true);
	if (CompleteTimeText.IsValid())
		CompleteTimeText.GetUI().SetText("Time  " + FormatTime(ElapsedSeconds) + "    Coins  " + std::to_string(Coins) + " / " + std::to_string(TotalCoins));
	if (CompleteBestText.IsValid())
		CompleteBestText.GetUI().SetText(best ? "A new best time!" : "Best  " + FormatTime(BestSeconds));
	if (PlayAgainButton.IsValid())
		PlayAgainButton.GetUI().Focus();
	Input::SetCursorMode(CursorMode::Normal);
}

void CourseState::ReadBestTime()
{
	BestSeconds = 0.0f;
	const std::optional<std::string> text = Game::ReadSaveText(c_BestTimeFile);
	if (!text)
		return;
	char* end = nullptr;
	const float seconds = std::strtof(text->c_str(), &end);
	if (end != text->c_str() && seconds > 0.0f && seconds < 86400.0f)
		BestSeconds = seconds;
}

void CourseState::ShowHud()
{
	if (CoinsText.IsValid())
		CoinsText.GetUI().SetText(std::to_string(Coins) + " / " + std::to_string(TotalCoins));
	if (TimeText.IsValid())
		TimeText.GetUI().SetText(FormatTime(ElapsedSeconds));
}

ST_SCRIPT_CLASS(CourseState)
{
	ST_SCRIPT_FIELD(MainMenuScene);
	ST_SCRIPT_FIELD(CoinSound);
	ST_SCRIPT_FIELD(CompleteSound);
	ST_SCRIPT_FIELD(CoinsText);
	ST_SCRIPT_FIELD(TimeText);
	ST_SCRIPT_FIELD(CompletePanel);
	ST_SCRIPT_FIELD(CompleteTimeText);
	ST_SCRIPT_FIELD(CompleteBestText);
	ST_SCRIPT_FIELD(PlayAgainButton);
	ST_SCRIPT_FIELD(CompleteMenuButton);
	ST_SCRIPT_FIELD(Coins);
	ST_SCRIPT_FIELD(TotalCoins);
	ST_SCRIPT_FIELD(ElapsedSeconds);
	ST_SCRIPT_FIELD(Completed);
	ST_SCRIPT_FIELD(BestSeconds);
}
