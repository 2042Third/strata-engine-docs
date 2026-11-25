#pragma once

#include "StrataScript/StrataScript.h"

#include <cstdint>

// The course's state, on its "Game" entity: the coins collected (the coins call AddCoin), the time, and the completion
// panel with the best time, kept in a save file, once the player reaches the goal (the goal calls Complete).
class CourseState : public Strata::Script
{
public:
	Strata::AssetHandle MainMenuScene;
	Strata::AssetHandle CoinSound;
	Strata::AssetHandle CompleteSound;
	Strata::Entity CoinsText;        // "3 / 8"
	Strata::Entity TimeText;
	Strata::Entity CompletePanel;    // Shown when the player reaches the goal
	Strata::Entity CompleteTimeText;
	Strata::Entity CompleteBestText;
	Strata::Entity PlayAgainButton;
	Strata::Entity CompleteMenuButton;

	// What happened, to watch in the Inspector
	int32_t Coins = 0;
	int32_t TotalCoins = 0;          // The scene's entities tagged "Coin"
	float ElapsedSeconds = 0.0f;
	bool Completed = false;
	float BestSeconds = 0.0f;        // 0: no best time yet

	void OnCreate() override;
	void OnUpdate(float deltaTime) override;
	void OnUIClick(Strata::Entity widget) override;

	void AddCoin(const glm::vec3& position);
	void Complete();
private:
	void ReadBestTime();
	void ShowHud();
};
