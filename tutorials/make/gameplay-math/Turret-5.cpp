#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Turns to face the ball with the SDK's LookAt.
class Turret : public Script
{
public:
	Entity Target; // The ball

	void OnUpdate(float) override
	{
		if (!Target)
			return;
		const glm::vec3 position = GetTransform().GetWorldPosition();
		const glm::vec3 targetPosition = Target.GetTransform().GetWorldPosition();
		GetTransform().SetWorldRotation(Motion::LookAt(position, targetPosition));
	}
};

ST_SCRIPT_CLASS(Turret)
{
	ST_SCRIPT_FIELD(Target);
}
