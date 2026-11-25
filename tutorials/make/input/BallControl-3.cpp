#include "StrataScript/StrataScript.h"

using namespace Strata;

// Moves its entity over the ground with the Move action.
class BallControl : public Script
{
public:
	float Speed = 4.0f; // Metres per second

	void OnUpdate(float deltaTime) override
	{
		// Up on the action (+Y) is forward on the level (-Z).
		const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
		const glm::vec3 direction(move.x, 0.0f, -move.y);

		TransformComponent transform = GetTransform();
		transform.SetTranslation(transform.GetTranslation() + direction * Speed * deltaTime);
	}
};

ST_SCRIPT_CLASS(BallControl)
{
	ST_SCRIPT_FIELD(Speed);
}
