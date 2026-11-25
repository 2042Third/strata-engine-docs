// Places Coin Run's coins when the game starts. Attach it to the empty entity Coins, which stays at the origin.

#include "StrataScript/StrataScript.h"

using namespace Strata;

class CoinPlacer : public Script
{
public:
	void OnCreate() override
	{
		// Ask early: loading takes frames, and Instantiate never waits for it.
		m_CoinPrefab = Assets::Find("Prefabs/Coin.stprefab");
		Assets::RequestLoad(m_CoinPrefab);
	}
private:
	AssetHandle m_CoinPrefab;
};

ST_SCRIPT_CLASS(CoinPlacer) {}
