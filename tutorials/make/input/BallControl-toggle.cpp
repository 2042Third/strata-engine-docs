#include "StrataScript/StrataScript.h"

using namespace Strata;

// Boost as a toggle: one press switches it on, the next press switches it off.
class BallControl : public Script
{
public:
	float Speed = 4.0f;
	float BoostFactor = 2.0f;

	void OnUpdate(float deltaTime) override
	{
		if (Input::IsActionPressed("Gameplay/Boost"))
			m_BoostLatched = !m_BoostLatched;

		const float speed = m_BoostLatched ? Speed * BoostFactor : Speed;
		const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
		const glm::vec3 direction(move.x, 0.0f, -move.y);

		TransformComponent transform = GetTransform();
		transform.SetTranslation(transform.GetTranslation() + direction * speed * deltaTime);
	}

private:
	bool m_BoostLatched = false;
};

ST_SCRIPT_CLASS(BallControl)
{
	ST_SCRIPT_FIELD(Speed);
	ST_SCRIPT_FIELD(BoostFactor);
}
