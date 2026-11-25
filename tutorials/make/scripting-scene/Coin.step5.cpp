// The Coin script of Coin Run: it turns, bobs and finds the ball once.

#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

class Coin : public Script
{
public:
	float DegreesPerSecond = 90.0f; // Fields: editable per entity
	float BobHeight = 0.1f;
	float BobSpeed = 2.0f;

	void OnCreate() override
	{
		// The height the coin was placed at: the bob swings around it.
		m_BaseHeight = GetTransform().GetTranslation().y;
		m_Ball = Scene::FindEntityByName("Ball");
		if (!m_Ball.IsValid())
			Log::Warn("The scene has no entity named Ball");
	}

	void OnUpdate(float deltaTime) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());

		// Time::GetElapsedTime() is a double; the sine and the fields are floats.
		const float swing = std::sin(BobSpeed * static_cast<float>(Time::GetElapsedTime()));
		glm::vec3 position = transform.GetTranslation();
		position.y = m_BaseHeight + BobHeight * swing;
		transform.SetTranslation(position);
	}
private:
	Entity m_Ball;
	float m_BaseHeight = 0.0f;
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
	ST_SCRIPT_FIELD(BobHeight);
	ST_SCRIPT_FIELD(BobSpeed);
}
