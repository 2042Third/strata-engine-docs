#include "StrataScript/StrataScript.h"

using namespace Strata;

// Switches the game's view between this camera and Other when the C key is pressed.
class CameraSwitch : public Script
{
public:
	Entity Other; // The second camera, set in the Inspector

	void OnUpdate(float) override
	{
		if (!Input::IsKeyPressed(Key::C) || !Other.IsValid())
			return;
		// The game is drawn from the first active camera that is Primary: clear the flag on one, set it on the other.
		const bool viewingThis = Scene::GetPrimaryCamera() == GetEntity();
		Entity from = viewingThis ? GetEntity() : Other;
		Entity to = viewingThis ? Other : GetEntity();
		from.SetProperty("Camera", "Primary", false);
		to.SetProperty("Camera", "Primary", true);
	}
};

ST_SCRIPT_CLASS(CameraSwitch)
{
	ST_SCRIPT_FIELD(Other);
}
