#include <cstdio>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

struct Entity
{
	std::string Name;
	int Parent = -1;
	bool HasRigidBody = false;
	float Mass = 1.0f;
	float Radius = 0.0f; // A sphere collider when above zero
};

struct Body
{
	std::vector<float> Radii;
	float Mass = 0.0f;
	int Builds = 0;
};

// The entity whose body holds this entity's colliders, or -1 when it has no physics components.
int FindOwner(const std::vector<Entity>& entities, int index)
{
	if (entities[index].HasRigidBody)
		return index;
	if (entities[index].Radius <= 0.0f)
		return -1;
	for (int parent = entities[index].Parent; parent >= 0; parent = entities[parent].Parent)
	{
		if (entities[parent].HasRigidBody)
			return parent;
	}
	return index;
}

class ToyWorld
{
public:
	explicit ToyWorld(std::vector<Entity> entities)
		: m_Entities(std::move(entities))
	{
		for (int index = 0; index < static_cast<int>(m_Entities.size()); index++)
			MarkChanged(index);
		ApplyChanges();
	}

	Entity& Get(int index) { return m_Entities[index]; }
	void MarkChanged(int index) { m_Changes.insert(index); }

	// Rounds: a change can hand a collider to another body, which is a change in turn.
	void ApplyChanges()
	{
		for (int round = 0; round < c_MaxRounds && !m_Changes.empty(); round++)
		{
			std::set<int> owners;
			for (int index : m_Changes)
			{
				const int owner = FindOwner(m_Entities, index);
				if (owner != index)
					m_Bodies.erase(index);
				if (owner >= 0)
					owners.insert(owner);
			}
			m_Changes.clear();
			for (int owner : owners)
				Build(owner);
		}
	}

	void Print() const
	{
		for (const auto& [index, body] : m_Bodies)
		{
			std::printf("%-8s shapes %zu, mass %.1f, built %d time(s)%s\n", m_Entities[index].Name.c_str(), body.Radii.size(), body.Mass,
				body.Builds, body.Radii.empty() ? ", pending: no collider" : "");
		}
	}
private:
	void Build(int owner)
	{
		Body& body = m_Bodies[owner];
		body.Radii.clear();
		body.Mass = m_Entities[owner].HasRigidBody ? m_Entities[owner].Mass : 0.0f;
		for (int index = 0; index < static_cast<int>(m_Entities.size()); index++)
		{
			if (m_Entities[index].Radius > 0.0f && FindOwner(m_Entities, index) == owner)
				body.Radii.push_back(m_Entities[index].Radius);
		}
		body.Builds++;
	}
private:
	static constexpr int c_MaxRounds = 16;
	std::vector<Entity> m_Entities;
	std::map<int, Body> m_Bodies;
	std::set<int> m_Changes;
};

int main()
{
	ToyWorld world({ { "Crate", -1, true, 4.0f, 0.0f }, { "Lid", 0, false, 1.0f, 0.5f }, { "Handle", 0, false, 1.0f, 0.25f },
		{ "Boulder", 0, true, 10.0f, 1.0f }, { "Rock", -1, false, 1.0f, 0.3f }, { "Marker", -1, true, 1.0f, 0.0f } });
	world.Print();

	std::printf("-- the handle grows\n");
	world.Get(2).Radius = 0.4f;
	world.MarkChanged(2);
	world.ApplyChanges();
	world.Print();

	std::printf("-- the boulder loses its rigid body\n");
	world.Get(3).HasRigidBody = false;
	world.MarkChanged(3);
	world.ApplyChanges();
	world.Print();
	return 0;
}
