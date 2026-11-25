#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Turns and bobs, and is collected when the ball enters its trigger: a chime plays where the coin was.
class Coin : public Script
{
public:
	float DegreesPerSecond = 120.0f;
	float BobHeight = 0.15f;

	void OnCreate() override
	{
		m_BaseHeight = GetTransform().GetTranslation().y;
		m_Sound = Assets::Find("Sounds/Coin.ogg");
		Assets::RequestLoad(m_Sound);
	}

	void OnReload() override
	{
		OnCreate();
	}

	void OnUpdate(float deltaTime) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());
		glm::vec3 position = transform.GetTranslation();
		position.y = m_BaseHeight + BobHeight * std::sin(Time::GetElapsedTime() * 2.0f);
		transform.SetTranslation(position);
	}

	void OnTriggerEnter(const Collision& collision) override
	{
		if (collision.Other.GetName() == "Ball")
		{
			Log::Info("Coin collected in frame ", Time::GetFrameIndex());
			Audio::PlayOneShotAt(m_Sound, GetTransform().GetWorldPosition());
			GetEntity().Destroy();
		}
	}
private:
	float m_BaseHeight = 0.0f;
	AssetHandle m_Sound;
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
	ST_SCRIPT_FIELD(BobHeight);
}
