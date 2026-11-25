#include "StrataScript/StrataScript.h"

using namespace Strata;

// Keys 1 and 2 and P change the time scale; L writes the clocks to the log.
class TimeControl : public Script
{
public:
	void OnUpdate(float deltaTime) override
	{
		if (Input::IsKeyPressed(Key::D1))
			Time::SetTimeScale(1.0f);
		if (Input::IsKeyPressed(Key::D2))
			Time::SetTimeScale(0.25f);
		if (Input::IsKeyPressed(Key::P))
			Time::SetTimeScale(Time::GetTimeScale() > 0.0f ? 0.0f : 1.0f);

		if (Input::IsKeyPressed(Key::L))
			Log::Info("scale ", Time::GetTimeScale(), " delta ", deltaTime, " unscaled ", Time::GetUnscaledDeltaTime(),
				" elapsed ", Time::GetElapsedTime(), " real ", Time::GetRealTime());
	}
};

ST_SCRIPT_CLASS(TimeControl) {}
