#include "StrataScript/StrataScript.h"

using namespace Strata;

class Coin : public Script
{
public:
	float DegreesPerSecond = 90.0f;

	void OnCreate() override
	{
		Log::Info("Coin starts with ", DegreesPerSecond, " degrees per second");
	}

	void OnUpdate(float deltaTime) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(1.0f, 0.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());
	}
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
}
