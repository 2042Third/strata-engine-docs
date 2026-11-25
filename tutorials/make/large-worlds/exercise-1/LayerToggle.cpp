#include "StrataScript/StrataScript.h"

using namespace Strata;

// Switches the Props layer off and on with a key.
class LayerToggle : public Script
{
public:
	void OnUpdate(float) override
	{
		if (!Input::IsKeyPressed(Key::P))
			return;
		const bool enabled = World::IsLayerEnabled("Props").value_or(true);
		World::SetLayerEnabled("Props", !enabled);
	}
};

ST_SCRIPT_CLASS(LayerToggle)
{
}
