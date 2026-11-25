// A toy physics step: copy in what changed, step what is awake, copy out what moved.
#include <cstddef>
#include <cstdio>
#include <vector>

struct Entity
{
	float Height = 0.0f;
	bool Signalled = false;
};

struct Body
{
	float Height = 0.0f;
	float Speed = 0.0f;
	bool Awake = true;
	bool Moved = false;
};

struct StepCounts
{
	int Synced = 0;
	int Stepped = 0;
	int Written = 0;
};

class ToyWorld
{
public:
	std::vector<Entity> Entities;
	std::vector<Body> Bodies;

	StepCounts Step(float timestep)
	{
		StepCounts counts;
		SyncEntitiesToBodies(counts);
		Simulate(timestep, counts);
		WriteBack(counts);
		return counts;
	}
private:
	// Before the step: look only at signalled entities and awake bodies.
	void SyncEntitiesToBodies(StepCounts& counts)
	{
		for (std::size_t index = 0; index < Bodies.size(); index++)
		{
			Body& body = Bodies[index];
			Entity& entity = Entities[index];
			if (!entity.Signalled && !body.Awake)
				continue;
			counts.Synced++;
			if (entity.Height != body.Height)
			{
				body.Height = entity.Height;
				body.Awake = true;
			}
			entity.Signalled = false;
		}
	}

	// The library's step: only awake bodies fall, and a body that lands falls asleep.
	void Simulate(float timestep, StepCounts& counts)
	{
		for (Body& body : Bodies)
		{
			if (!body.Awake)
				continue;
			counts.Stepped++;
			body.Speed -= 9.81f * timestep;
			body.Height += body.Speed * timestep;
			if (body.Height <= 0.0f)
			{
				body.Height = 0.0f;
				body.Speed = 0.0f;
				body.Awake = false;
			}
			body.Moved = true;
		}
	}

	// After the step: copy back only the bodies that moved.
	void WriteBack(StepCounts& counts)
	{
		for (std::size_t index = 0; index < Bodies.size(); index++)
		{
			if (!Bodies[index].Moved)
				continue;
			Entities[index].Height = Bodies[index].Height;
			Bodies[index].Moved = false;
			counts.Written++;
		}
	}
};

void Report(const ToyWorld& world, int step, const StepCounts& counts)
{
	std::printf("step %3d: synced %d, stepped %d, written %d; last entity %.2f m, its body %.2f m\n", step, counts.Synced, counts.Stepped,
		counts.Written, world.Entities[3].Height, world.Bodies[3].Height);
}

int main()
{
	ToyWorld world;
	const float heights[] = { 3.0f, 2.0f, 1.0f, 0.0f };
	for (const float height : heights)
	{
		world.Entities.push_back(Entity { height, false });
		world.Bodies.push_back(Body { height, 0.0f, height > 0.0f, false });
	}

	const float timestep = 1.0f / 60.0f;
	Report(world, 1, world.Step(timestep));
	for (int step = 2; step <= 60; step++)
		world.Step(timestep);
	Report(world, 61, world.Step(timestep));

	world.Entities[3].Height = 5.0f; // A write nobody signalled
	Report(world, 62, world.Step(timestep));
	world.Entities[3].Signalled = true;
	Report(world, 63, world.Step(timestep));
}
