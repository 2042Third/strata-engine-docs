#include "StrataScript/StrataScript.h"

#include <optional>

using namespace Strata;

// Moves the ball to the FarMarker once the ground there is loaded.
class Teleport : public Script
{
public:
	float ReachRadius = 48.0f; // Meters around the marker whose cells must be loaded

	void OnUpdate(float) override
	{
		if (m_Waiting)
			Arrive();
		else if (Input::IsActionPressed("Gameplay/Teleport"))
			Begin();
	}

private:
	void Begin()
	{
		Entity marker = Scene::FindEntityByName("FarMarker");
		if (!marker.IsValid())
			return;
		m_Target = marker.GetTransform().GetWorldPosition();
		GetEntity().GetRigidBody().Teleport(m_Target + glm::vec3(0.0f, 1.0f, 0.0f));
		return;
		m_Request = World::RequestCellsAround(m_Target, ReachRadius);
		m_Waiting = m_Request.IsValid();
	}

	void Arrive()
	{
		if (!World::IsLoadedAround(m_Target, ReachRadius))
			return;
		const std::optional<RaycastHit> ground = Physics::Raycast(m_Target + glm::vec3(0.0f, 100.0f, 0.0f), glm::vec3(0.0f, -1.0f, 0.0f), 200.0f);
		if (!ground)
			return;
		RigidBody body = GetEntity().GetRigidBody();
		body.Teleport(ground->Point + glm::vec3(0.0f, 1.0f, 0.0f));
		body.SetLinearVelocity(glm::vec3(0.0f));
		body.SetAngularVelocity(glm::vec3(0.0f));
		m_Request.Release();
		m_Waiting = false;
	}

	glm::vec3 m_Target = glm::vec3(0.0f);
	WorldCellRequest m_Request;
	bool m_Waiting = false;
};

ST_SCRIPT_CLASS(Teleport)
{
	ST_SCRIPT_FIELD(ReachRadius);
}
