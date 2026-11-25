// The Coin script of Coin Run: it turns, bobs, finds the ball and can swap its material for a glowing one.

#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

class Coin : public Script
{
public:
	float DegreesPerSecond = 90.0f; // Fields: editable per entity
	float BobHeight = 0.1f;
	float BobSpeed = 2.0f;
	float GlowDistance = 2.0f;

	void OnCreate() override
	{
		// The height the coin was placed at: the bob swings around it.
		m_BaseHeight = GetTransform().GetTranslation().y;
		m_Ball = Scene::FindEntityByName("Ball");
		if (!m_Ball.IsValid())
			Log::Warn("The scene has no entity named Ball");
		m_GlowMaterial = Assets::Find("Materials/GoldGlow.stmat");
		Assets::RequestLoad(m_GlowMaterial);
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
	// The Mesh Renderer sits on a descendant of the prefab's root: search the children.
	static Entity FindMeshEntity(Entity entity)
	{
		if (entity.HasComponent("MeshRenderer"))
			return entity;
		for (Entity child : entity.GetChildren())
		{
			const Entity found = FindMeshEntity(child);
			if (found.IsValid())
				return found;
		}
		return Entity();
	}

	void Glow()
	{
		if (m_Glowing || !Assets::IsLoaded(m_GlowMaterial))
			return;
		Entity mesh = FindMeshEntity(GetEntity());
		m_Glowing = mesh.IsValid() && mesh.SetProperty("MeshRenderer", "Material", m_GlowMaterial);
	}

	Entity m_Ball;
	float m_BaseHeight = 0.0f;
	AssetHandle m_GlowMaterial;
	bool m_Glowing = false;
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
	ST_SCRIPT_FIELD(BobHeight);
	ST_SCRIPT_FIELD(BobSpeed);
	ST_SCRIPT_FIELD(GlowDistance);
}
