#include "StrataScript/StrataScript.h"

using namespace Strata;

// Moves its entity over the ground with W, A, S and D or with the left stick of a gamepad.
class BallControl : public Script
{
public:
	float Speed = 4.0f; // Metres per second

	void OnUpdate(float deltaTime) override
	{
		glm::vec3 direction(0.0f);
		if (Input::IsKeyDown(Key::W))
			direction.z -= 1.0f; // Forward is -Z
		if (Input::IsKeyDown(Key::S))
			direction.z += 1.0f;
		if (Input::IsKeyDown(Key::A))
			direction.x -= 1.0f;
		if (Input::IsKeyDown(Key::D))
			direction.x += 1.0f;

		if (Input::IsGamepadConnected())
		{
			const glm::vec2 stick = Input::GetGamepadStick(GamepadStick::Left);
			direction.x += stick.x;
			direction.z -= stick.y; // The stick's +Y is up, the level's forward is -Z
		}

		if (glm::length(direction) > 1.0f)
			direction = glm::normalize(direction);

		TransformComponent transform = GetTransform();
		transform.SetTranslation(transform.GetTranslation() + direction * Speed * deltaTime);
	}
};

ST_SCRIPT_CLASS(BallControl)
{
	ST_SCRIPT_FIELD(Speed);
}
