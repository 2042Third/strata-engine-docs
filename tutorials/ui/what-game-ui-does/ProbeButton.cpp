#include "StrataScript/StrataScript.h"

using namespace Strata;

// A probe for the exercise: stops game time at once, then reports what the UI and the input see each update.
class ProbeButton : public Script
{
public:
	void OnCreate() override { Time::SetTimeScale(0.0f); }

	void OnUpdate(float) override
	{
		Log::Info("ProbeButton over UI: ", UI::IsPointerOverUI(), ", left press: ", Input::IsMouseButtonPressed(Mouse::ButtonLeft));
	}

	void OnUIClick(Entity) override { Log::Info("ProbeButton clicked"); }
};

ST_SCRIPT_CLASS(ProbeButton)
{
}
