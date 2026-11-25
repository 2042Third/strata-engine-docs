#include "StrataScript/StrataScript.h"

using namespace Strata;

// V switches between walking (the Gameplay map) and driving (the Vehicle map, twice as fast).
class BallControl : public Script
{
public:
	float Speed = 4.0f;

	void OnUpdate(float deltaTime) override
	{
		if (Input::IsKeyPressed(Key::V)) // A test switch, not a control for players
		{
			const bool driving = Input::IsActionMapEnabled("Vehicle").value_or(false);
			Input::SetActionMapEnabled("Vehicle", !driving);
			Input::SetActionMapEnabled("Gameplay", driving);
		}

		// The disabled map reads as up: only one of the two vectors is not zero.
		const glm::vec2 walk = Input::GetActionValue("Gameplay/Move");
		const glm::vec2 drive = Input::GetActionValue("Vehicle/Drive");
		const glm::vec2 move = walk + drive * 2.0f;
		const glm::vec3 direction(move.x, 0.0f, -move.y);

		TransformComponent transform = GetTransform();
		transform.SetTranslation(transform.GetTranslation() + direction * Speed * deltaTime);
	}
};

ST_SCRIPT_CLASS(BallControl)
{
	ST_SCRIPT_FIELD(Speed);
}
