#include "StrataScript/StrataScript.h"

using namespace Strata;

// Changes the game's master volume in steps of 0.1: Minus lowers it, Equal raises it.
class VolumeKeys : public Script
{
public:
	void OnUpdate(float deltaTime) override
	{
		float volume = Audio::GetMasterVolume();
		if (Input::IsKeyPressed(Key::Minus))
			volume -= 0.1f;
		if (Input::IsKeyPressed(Key::Equal))
			volume += 0.1f;
		Audio::SetMasterVolume(volume);
	}
};

ST_SCRIPT_CLASS(VolumeKeys)
{
}
