// A coin, on a static sphere trigger tagged "Coin" whose child is the coin's model: the model spins, and the player
// walking through the trigger collects the coin once (CourseState counts it).

#include "CourseState.h"

#include <cmath>

using namespace Strata;

class Coin : public Script
{
public:
	float SpinSpeed = 180.0f; // Degrees per second
	bool Collected = false;

	void OnCreate() override
	{
		const std::vector<Entity> children = GetEntity().GetChildren();
		m_Visual = children.empty() ? Entity() : children.front();
	}

	void OnReload() override { OnCreate(); }

	void OnUpdate(float deltaTime) override
	{
		if (!m_Visual.IsValid())
			return;
		m_Angle = std::fmod(m_Angle + SpinSpeed * deltaTime, 360.0f);
		m_Visual.GetTransform().SetRotation(glm::angleAxis(glm::radians(m_Angle), glm::vec3(0.0f, 1.0f, 0.0f)));
	}

	void OnTriggerEnter(const Collision& collision) override
	{
		if (Collected || !collision.Other.IsValid() || collision.Other.GetTag() != "Player")
			return;
		Collected = true;
		if (CourseState* course = Scene::FindEntityByName("Game").GetScript<CourseState>())
			course->AddCoin(GetTransform().GetWorldPosition());
		GetEntity().SetActive(false);
	}
private:
	Entity m_Visual;
	float m_Angle = 0.0f;
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(SpinSpeed);
	ST_SCRIPT_FIELD(Collected);
}
