// The Coin script of Coin Run: it turns, bobs, glows when the ball comes near and is collected when the ball arrives.

#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

class Coin : public Script
{
public:
	float DegreesPerSecond = 90.0f;
	float BobHeight = 0.1f;
	float BobSpeed = 2.0f;
	float GlowDistance = 2.0f;
	float CollectDistance = 0.7f;

	void OnCreate() override
	{
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

		const float swing = std::sin(BobSpeed * static_cast<float>(Time::GetElapsedTime()));
		glm::vec3 position = transform.GetTranslation();
		position.y = m_BaseHeight + BobHeight * swing;
		transform.SetTranslation(position);

		if (!m_Ball.IsValid())
			return;
		const float distance = glm::distance(transform.GetWorldPosition(), m_Ball.GetTransform().GetWorldPosition());
		if (distance < GlowDistance)
			Glow();
		if (distance < CollectDistance)
			GetEntity().Destroy();
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

	float m_BaseHeight = 0.0f;
	bool m_Glowing = false;
	Entity m_Ball;
	AssetHandle m_GlowMaterial;
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
	ST_SCRIPT_FIELD(BobHeight);
	ST_SCRIPT_FIELD(BobSpeed);
	ST_SCRIPT_FIELD(GlowDistance);
	ST_SCRIPT_FIELD(CollectDistance);
}
