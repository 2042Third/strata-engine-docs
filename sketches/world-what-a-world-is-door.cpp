// A door that opens when the player comes near, written in three object models.
#include <cmath>
#include <cstdio>
#include <memory>
#include <vector>

const float c_Reach = 2.5f;

// 1. A class hierarchy: the door is a class with its own virtual Update.
struct Thing
{
	float X = 0.0f;
	virtual ~Thing() = default;
	virtual void Update(float playerX) = 0;
};

struct HierarchyDoor : Thing
{
	bool Open = false;
	void Update(float playerX) override { if (std::fabs(playerX - X) < c_Reach) Open = true; }
};

// 2. A game object that owns components, and each component has its own virtual Update.
struct GameObject;

struct Behaviour
{
	GameObject* Owner = nullptr;
	virtual ~Behaviour() = default;
	virtual void Update(float playerX) = 0;
};

struct GameObject
{
	float X = 0.0f;
	std::vector<std::unique_ptr<Behaviour>> Behaviours;
};

struct OpenWhenNear : Behaviour
{
	bool Open = false;
	void Update(float playerX) override { if (std::fabs(playerX - Owner->X) < c_Reach) Open = true; }
};

// 3. An entity component system: the door is data, and one system runs over every door.
struct DoorComponent
{
	float X = 0.0f; // Strata keeps the position in a Transform component of its own
	bool Open = false;
};

void DoorSystem(std::vector<DoorComponent>& doors, float playerX)
{
	for (DoorComponent& door : doors)
		if (std::fabs(playerX - door.X) < c_Reach)
			door.Open = true;
}

int main()
{
	HierarchyDoor hierarchyDoor;
	GameObject gameObject;
	gameObject.Behaviours.push_back(std::make_unique<OpenWhenNear>());
	gameObject.Behaviours[0]->Owner = &gameObject;
	std::vector<DoorComponent> doors(1);
	for (int frame = 1; frame <= 4; frame++)
	{
		const float playerX = 5.0f - static_cast<float>(frame);
		hierarchyDoor.Update(playerX);
		gameObject.Behaviours[0]->Update(playerX);
		DoorSystem(doors, playerX);
		const OpenWhenNear& behaviour = static_cast<const OpenWhenNear&>(*gameObject.Behaviours[0]);
		std::printf("frame %d, player at %g: hierarchy %d, objects %d, ecs %d\n", frame, playerX, hierarchyDoor.Open, behaviour.Open, doors[0].Open);
	}
	return 0;
}
