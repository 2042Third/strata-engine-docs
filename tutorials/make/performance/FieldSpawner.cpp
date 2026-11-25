#include "StrataScript/StrataScript.h"

#include <vector>

using namespace Strata;

class FieldSpawner : public Script
{
public:
	float Spacing = 3.0f; // Metres between two props

	void OnCreate() override
	{
		for (int row = 0; row < 50; row++)
		{
			for (int column = 0; column < 100; column++)
			{
				const glm::vec3 position(column * Spacing, 0.0f, row * Spacing);
				m_Transforms.push_back(glm::translate(glm::mat4(1.0f), position));
			}
		}
	}

	void OnUpdate([[maybe_unused]] float deltaTime) override
	{
		if (m_Spawned)
			return;
		// The call returns nothing while the prefab still loads, and it starts the load: ask again next frame.
		const std::vector<Entity> roots = Scene::InstantiateMany("Prefabs/Rock.stprefab", m_Transforms);
		m_Spawned = !roots.empty();
	}

private:
	std::vector<glm::mat4> m_Transforms;
	bool m_Spawned = false;
};

ST_SCRIPT_CLASS(FieldSpawner)
{
	ST_SCRIPT_FIELD(Spacing);
}
