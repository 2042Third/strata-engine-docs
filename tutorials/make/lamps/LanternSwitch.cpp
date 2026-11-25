#include "StrataScript/StrataScript.h"

using namespace Strata;

class LanternSwitch : public Script
{
public:
	Entity Lamp;
	float OnCandela = 64.0f;

	void OnUpdate([[maybe_unused]] float deltaTime) override
	{
		if (!Lamp.IsValid() || !Input::IsActionPressed("Gameplay/Lamp"))
			return;

		m_On = !m_On;
		Lamp.SetProperty("PointLight", "Intensity", m_On ? OnCandela : 0.0f);
	}

private:
	bool m_On = true;
};

ST_SCRIPT_CLASS(LanternSwitch)
{
	ST_SCRIPT_FIELD(Lamp);
	ST_SCRIPT_FIELD(OnCandela);
}
