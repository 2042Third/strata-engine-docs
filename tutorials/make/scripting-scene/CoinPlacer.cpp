// Places Coin Run's coins when the game starts. Attach it to the empty entity Coins, which stays at the origin.

#include "StrataScript/StrataScript.h"

using namespace Strata;

static const glm::vec3 c_CoinPositions[] =
{
	{ -4.0f, 0.8f, 0.0f },
	{ -2.0f, 0.8f, 2.0f },
	{ 0.0f, 0.8f, 3.0f },
	{ 2.0f, 0.8f, 2.0f },
	{ 4.0f, 0.8f, 0.0f },
};

class CoinPlacer : public Script
{
public:
	void OnCreate() override
	{
		// Ask early: loading takes frames, and Instantiate never waits for it.
		m_CoinPrefab = Assets::Find("Prefabs/Coin.stprefab");
		Assets::RequestLoad(m_CoinPrefab);
	}

	void OnUpdate(float deltaTime) override
	{
		if (m_Placed || !Assets::IsLoaded(m_CoinPrefab))
			return;

		const glm::quat noTurn(1.0f, 0.0f, 0.0f, 0.0f);
		for (const glm::vec3& position : c_CoinPositions)
			Scene::Instantiate(m_CoinPrefab, position, noTurn, glm::vec3(1.0f), GetEntity());
		m_Placed = true;

		Log::Info("Coins placed: ", Scene::FindEntitiesByTag("Coin").size());
	}
private:
	AssetHandle m_CoinPrefab;
	bool m_Placed = false;
};

ST_SCRIPT_CLASS(CoinPlacer) {}
