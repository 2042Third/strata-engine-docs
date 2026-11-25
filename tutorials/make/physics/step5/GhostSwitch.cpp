#include "StrataScript/StrataScript.h"

using namespace Strata;

// Press G to close or open the ghost wall to the ball.
class GhostSwitch : public Script
{
public:
	void OnUpdate(float) override
	{
		if (!Input::IsKeyPressed(Key::G))
			return;
		const int32_t ball = Physics::GetLayerIndex("Ball");
		const int32_t ghost = Physics::GetLayerIndex("Ghost");
		if (ball < 0 || ghost < 0)
			return;
		const uint32_t ballLayer = static_cast<uint32_t>(ball);
		const uint32_t ghostLayer = static_cast<uint32_t>(ghost);
		Physics::SetLayersCollide(ballLayer, ghostLayer, !Physics::GetLayersCollide(ballLayer, ghostLayer));
	}
};

ST_SCRIPT_CLASS(GhostSwitch)
{
}
