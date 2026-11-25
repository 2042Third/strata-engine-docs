#include "Pickup.h"

using namespace Strata;

// Drops a crate from above the room every Period seconds of game time and gives it its Pickup behaviour.
class Dropper : public Script
{
public:
	float Period = 2.0f;

	void OnCreate() override
	{
		m_Crate = Assets::Find("Prefabs/Crate.stprefab");
		Assets::RequestLoad(m_Crate);
		m_Timer.Start(Period, true);
	}

	void OnReload() override { OnCreate(); }

	void OnUpdate(float deltaTime) override
	{
		for (int32_t i = m_Timer.Update(deltaTime); i > 0; i--)
		{
			if (!Assets::IsLoaded(m_Crate))
				continue;
			const float x = static_cast<float>(m_Count % 5 - 2) * 3.0f;
			Entity crate = Scene::Instantiate(m_Crate, glm::vec3(x, 6.0f, 0.0f));
			if (crate.IsValid())
				crate.AddScript<Pickup>();
			m_Count++;
		}
	}

private:
	AssetHandle m_Crate;
	Timer m_Timer;
	int32_t m_Count = 0;
};

ST_SCRIPT_CLASS(Dropper)
{
	ST_SCRIPT_FIELD(Period);
}
