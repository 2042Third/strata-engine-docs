#include "StrataScript/StrataScript.h"

using namespace Strata;

// Moves its entity with the Move action, faster while Boost is held. The Pause action stops and starts the game's time.
class BallControl : public Script
{
public:
	float Speed = 4.0f;       // Metres per second
	float BoostFactor = 2.0f; // Speed is multiplied by it while Boost is held

	void OnUpdate(float deltaTime) override
	{
		if (Input::IsActionPressed("Gameplay/Pause"))
			Time::SetTimeScale(Time::GetTimeScale() == 0.0f ? 1.0f : 0.0f);

		if (Input::IsActionPressed("Gameplay/Jump"))
			Log::Info("Jump pressed");

		const float speed = Input::IsActionDown("Gameplay/Boost") ? Speed * BoostFactor : Speed;

		// Up on the action (+Y) is forward on the level (-Z).
		const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
		const glm::vec3 direction(move.x, 0.0f, -move.y);

		TransformComponent transform = GetTransform();
		transform.SetTranslation(transform.GetTranslation() + direction * speed * deltaTime);
	}
};

ST_SCRIPT_CLASS(BallControl)
{
	ST_SCRIPT_FIELD(Speed);
	ST_SCRIPT_FIELD(BoostFactor);
}
