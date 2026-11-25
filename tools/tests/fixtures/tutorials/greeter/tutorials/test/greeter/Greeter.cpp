// The test tutorial's script: it greets once and turns its entity by a fixed angle every fixed step, so that the turn
// after n steps is the same on every machine.

#include "StrataScript/StrataScript.h"

using namespace Strata;

class Greeter : public Script
{
public:
	float DegreesPerStep = 1.0f;

	void OnCreate() override
	{
		Log::Info("Hello from Greeter");
	}

	void OnFixedUpdate(float) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerStep), glm::vec3(0.0f, 1.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());
	}
};

ST_SCRIPT_CLASS(Greeter)
{
	ST_SCRIPT_FIELD(DegreesPerStep);
}
