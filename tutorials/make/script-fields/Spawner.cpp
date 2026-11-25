#include "StrataScript/StrataScript.h"

using namespace Strata;

class Spawner : public Script
{
public:
	bool Enabled = true;
	int32_t MaxCrates = 5;
	float Interval = 2.0f;
	glm::vec2 Jitter = glm::vec2(0.0f);
	glm::vec3 Offset = glm::vec3(0.0f, 1.0f, 0.0f);
	glm::vec4 Tint = glm::vec4(1.0f);
	glm::quat Tilt = glm::quat(1.0f, 0.0f, 0.0f, 0.0f);
	std::string Label = "Crates";
	Entity SpawnPoint;
	AssetHandle CratePrefab;

	void OnCreate() override
	{
		Assets::RequestLoad(CratePrefab);
	}

	void OnUpdate(float deltaTime) override
	{
		if (!Enabled || m_Spawned >= MaxCrates || !SpawnPoint.IsValid())
			return;

		m_Waited += deltaTime;
		if (m_Waited < Interval || !Assets::IsLoaded(CratePrefab))
			return;

		const glm::vec3 where = SpawnPoint.GetTransform().GetWorldPosition() + Offset;
		const Entity crate = Scene::Instantiate(CratePrefab, where, Tilt);
		if (!crate.IsValid())
			return;

		m_Waited = 0.0f;
		m_Spawned++;
	}

private:
	float m_Waited = 0.0f;
	int32_t m_Spawned = 0;
};

ST_SCRIPT_CLASS(Spawner)
{
	ST_SCRIPT_FIELD(Enabled);
	ST_SCRIPT_FIELD(MaxCrates);
	ST_SCRIPT_FIELD(Interval);
	ST_SCRIPT_FIELD(Jitter);
	ST_SCRIPT_FIELD(Offset);
	ST_SCRIPT_FIELD(Tint);
	ST_SCRIPT_FIELD(Tilt);
	ST_SCRIPT_FIELD(Label);
	ST_SCRIPT_FIELD(SpawnPoint);
	ST_SCRIPT_FIELD(CratePrefab);
}
