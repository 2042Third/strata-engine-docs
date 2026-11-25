#include "StrataScript/StrataScript.h"

using namespace Strata;

// Moves along the row with A and D; Left Shift dashes, then waits DashCooldown seconds of game time.
class Player : public Script
{
public:
	float Speed = 4.0f;
	float DashDistance = 3.0f;
	float DashCooldown = 1.5f;

	void OnUpdate(float deltaTime) override
	{
		if (Time::GetTimeScale() == 0.0f)
			return;
		float move = 0.0f;
		if (Input::IsKeyDown(Key::A))
			move -= 1.0f;
		if (Input::IsKeyDown(Key::D))
			move += 1.0f;
		if (move != 0.0f)
			m_Facing = move;

		glm::vec3 position = GetTransform().GetTranslation();
		position.x += move * Speed * deltaTime;
		if (Input::IsKeyPressed(Key::LeftShift) && !m_Cooldown.IsRunning())
		{
			position.x += m_Facing * DashDistance;
			m_Cooldown.Start(DashCooldown);
		}
		m_Cooldown.Update(deltaTime);
		position.x = glm::clamp(position.x, -8.0f, 8.0f);
		GetTransform().SetTranslation(position);
	}

private:
	Timer m_Cooldown;
	float m_Facing = 1.0f;
};

ST_SCRIPT_CLASS(Player)
{
	ST_SCRIPT_FIELD(Speed);
	ST_SCRIPT_FIELD(DashDistance);
	ST_SCRIPT_FIELD(DashCooldown);
}
