// Exercise 2: places the coins, switches the group off after five seconds and on again after eight.

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
		m_CoinPrefab = Assets::Find("Prefabs/Coin.stprefab");
		Assets::RequestLoad(m_CoinPrefab);
	}

	void OnUpdate(float deltaTime) override
	{
		if (!m_Placed)
		{
			if (!Assets::IsLoaded(m_CoinPrefab))
				return;
			const glm::quat noTurn(1.0f, 0.0f, 0.0f, 0.0f);
			for (const glm::vec3& position : c_CoinPositions)
				Scene::Instantiate(m_CoinPrefab, position, noTurn, glm::vec3(1.0f), GetEntity());
			m_Placed = true;
			m_PlacedAt = static_cast<float>(Time::GetElapsedTime());
		}

		// Switch the children off, not GetEntity(): an inactive CoinPlacer would get no more updates.
		const float age = static_cast<float>(Time::GetElapsedTime()) - m_PlacedAt;
		if (!m_Off && age > 5.0f)
		{
			SetCoinsActive(false);
			m_Off = true;
		}
		else if (m_Off && !m_On && age > 8.0f)
		{
			SetCoinsActive(true);
			m_On = true;
		}
	}
private:
	void SetCoinsActive(bool active)
	{
		for (Entity coin : GetEntity().GetChildren())
			coin.SetActive(active);
	}

	AssetHandle m_CoinPrefab;
	bool m_Placed = false;
	bool m_Off = false;
	bool m_On = false;
	float m_PlacedAt = 0.0f;
};

ST_SCRIPT_CLASS(CoinPlacer) {}
