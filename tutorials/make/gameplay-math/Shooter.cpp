#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Shoots a ball through the cursor at every left click.
class Shooter : public Script
{
public:
	AssetHandle Prefab; // The ball
	float Speed = 14.0f; // Metres per second

	void OnCreate() override { Assets::RequestLoad(Prefab); }

	void OnUpdate(float) override
	{
		glm::vec3 origin, direction;
		if (Input::IsMouseButtonPressed(Mouse::ButtonLeft) && Assets::IsLoaded(Prefab) && GetPointerRay(origin, direction))
			Shoot(origin, direction);
	}

	void OnFixedUpdate(float) override
	{
		// A new ball has its body from the next fixed step: offer the speed until the call succeeds.
		if (m_Shot && m_Shot.GetRigidBody().SetLinearVelocity(m_Velocity))
			m_Shot = Entity();
	}
private:
	void Shoot(const glm::vec3& origin, const glm::vec3& direction)
	{
		Entity ball = Scene::Instantiate(Prefab, origin + direction * 1.5f, glm::quat(1.0f, 0.0f, 0.0f, 0.0f), glm::vec3(0.3f));
		if (!ball)
			return;
		m_Shot = ball;
		m_Velocity = direction * Speed;
	}

	// The ray from the camera through the cursor, in the world.
	bool GetPointerRay(glm::vec3& outOrigin, glm::vec3& outDirection) const
	{
		Entity camera = Scene::GetPrimaryCamera();
		const glm::uvec2 window = Game::GetWindowSize();
		const glm::vec2 mouse = Input::GetMousePosition();
		if (!camera || window.x == 0 || window.y == 0)
			return false;
		TransformComponent transform = camera.GetTransform();
		const float fov = glm::radians(camera.GetProperty<float>("Camera", "PerspectiveFOV").value_or(60.0f));
		const float aspect = static_cast<float>(window.x) / static_cast<float>(window.y);
		const float x = (2.0f * mouse.x / static_cast<float>(window.x) - 1.0f) * std::tan(fov * 0.5f) * aspect;
		const float y = (1.0f - 2.0f * mouse.y / static_cast<float>(window.y)) * std::tan(fov * 0.5f);
		outOrigin = transform.GetWorldPosition();
		outDirection = glm::normalize(transform.GetForward() + transform.GetRight() * x + transform.GetUp() * y);
		return true;
	}

	Entity m_Shot;
	glm::vec3 m_Velocity = glm::vec3(0.0f);
};

ST_SCRIPT_CLASS(Shooter)
{
	ST_SCRIPT_FIELD(Prefab);
	ST_SCRIPT_FIELD(Speed);
}
