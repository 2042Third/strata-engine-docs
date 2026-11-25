#include "StrataScript/StrataScript.h"

using namespace Strata;

// Keys 1 and 2 and P change the time scale; the word "Paused" blinks on unscaled time while the scale is 0.
class TimeControl : public Script
{
public:
	void OnCreate() override
	{
		m_PausedText = Scene::FindEntityByName("PausedText");
		m_Blink.Start(0.5f, true);
	}

	void OnReload() override { OnCreate(); }

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

		if (m_Blink.Update(Time::GetUnscaledDeltaTime()) % 2 == 1)
			m_BlinkOn = !m_BlinkOn;
		const bool paused = Time::GetTimeScale() == 0.0f;
		if (m_PausedText.IsValid())
			m_PausedText.GetUI().SetColor(glm::vec4(1.0f, 1.0f, 1.0f, paused && m_BlinkOn ? 1.0f : 0.0f));
	}

private:
	Entity m_PausedText;
	Timer m_Blink;
	bool m_BlinkOn = true;
};

ST_SCRIPT_CLASS(TimeControl) {}
