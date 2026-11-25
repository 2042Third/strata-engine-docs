// A door that loads a room beside the level while the player stands in its trigger, shows on a bar how far the room has
// loaded, and unloads the room when the player leaves.

#include "StrataScript/StrataScript.h"

using namespace Strata;

class RoomDoor : public Script
{
public:
	AssetHandle Room; // The room's scene
	Entity Bar;       // A UI image of the type Filled

	void OnTriggerEnter(const Collision& collision) override
	{
		if (IsPlayer(collision) && !m_Room.IsValid())
			m_Room = Scene::LoadAdditive(Room);
	}

	void OnTriggerExit(const Collision& collision) override
	{
		if (IsPlayer(collision) && m_Room.IsValid())
		{
			m_Room.Unload();
			m_Room = SubScene();
		}
	}

	void OnUpdate(float) override
	{
		if (Bar.IsValid())
			Bar.SetProperty("UIImage", "FillAmount", Assets::GetLoadProgress(Room));
	}

private:
	static bool IsPlayer(const Collision& collision)
	{
		return collision.Other.IsValid() && collision.Other.GetTag() == "Player";
	}

	SubScene m_Room;
};

ST_SCRIPT_CLASS(RoomDoor)
{
	ST_SCRIPT_FIELD(Room);
	ST_SCRIPT_FIELD(Bar);
}
