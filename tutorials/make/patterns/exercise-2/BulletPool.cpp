#include "StrataScript/StrataScript.h"

#include <vector>

using namespace Strata;

class BulletPool : public Script
{
public:
	int32_t PoolSize = 20;
	float ShotsPerSecond = 4.0f;
	float LifeSeconds = 1.5f;
	float Speed = 12.0f;

	void OnCreate() override
	{
		for (int32_t index = 0; index < PoolSize; index++)
		{
			Entity bullet = Scene::CreateEntity("Bullet", GetEntity());
			bullet.SetActive(false);
		}
		FindBullets();
	}

	void OnReload() override
	{
		FindBullets();
	}

	void OnUpdate(float deltaTime) override
	{
		m_Cooldown -= deltaTime;
		for (size_t index = 0; index < m_Bullets.size(); index++)
		{
			if (!m_Bullets[index].IsActive())
				continue;
			m_Ages[index] += deltaTime;
			TransformComponent transform = m_Bullets[index].GetTransform();
			transform.SetTranslation(transform.GetTranslation() + glm::vec3(0.0f, 0.0f, -Speed * deltaTime));
			if (m_Ages[index] >= LifeSeconds)
				m_Bullets[index].SetActive(false);
		}
		if (m_Cooldown <= 0.0f)
		{
			m_Cooldown = 1.0f / ShotsPerSecond;
			Fire();
		}
	}
private:
	void FindBullets()
	{
		m_Bullets = GetEntity().GetChildren();
		m_Ages.assign(m_Bullets.size(), 0.0f);
	}

	void Fire()
	{
		for (size_t index = 0; index < m_Bullets.size(); index++)
		{
			if (m_Bullets[index].IsActive())
				continue;
			m_Ages[index] = 0.0f;
			m_Bullets[index].GetTransform().SetTranslation(GetTransform().GetTranslation());
			m_Bullets[index].SetActive(true);
			return;
		}
		Log::Info("BulletPool: every bullet is in flight, the shot is skipped");
	}

	std::vector<Entity> m_Bullets;
	std::vector<float> m_Ages;
	float m_Cooldown = 0.0f;
};

ST_SCRIPT_CLASS(BulletPool)
{
	ST_SCRIPT_FIELD(PoolSize);
	ST_SCRIPT_FIELD(ShotsPerSecond);
	ST_SCRIPT_FIELD(LifeSeconds);
	ST_SCRIPT_FIELD(Speed);
}
