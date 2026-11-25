#include "StrataScript/StrataScript.h"

#include <string>

using namespace Strata;

// The settings screen: volume, window mode, resolution and vsync.
class SettingsMenu : public Script
{
public:
	Entity VolumeSlider;

	void OnCreate() override
	{
		// Values set from code raise no OnUIValueChanged, so showing the volume sets nothing.
		if (VolumeSlider.IsValid())
			VolumeSlider.GetUI().SetValue(Audio::GetMasterVolume());
	}

	void OnUIValueChanged(Entity widget, float value) override
	{
		const std::string name = widget.GetName();
		if (name == "Volume")
			Audio::SetMasterVolume(value);
		else if (name == "VSync")
			Game::SetVSync(value != 0.0f);
		else if (value != 0.0f)
			ChooseWindowMode(name);
	}

	void OnUIClick(Entity widget) override
	{
		const std::string name = widget.GetName();
		if (name == "Size720")
			Game::SetResolution(1280, 720);
		else if (name == "Size1080")
			Game::SetResolution(1920, 1080);
		else if (name == "Size1440")
			Game::SetResolution(2560, 1440);
	}

private:
	// Called only for a toggle that turned on: its group turned the others off and raised their 0 first.
	void ChooseWindowMode(const std::string& name)
	{
		if (name == "Windowed")
			Game::SetWindowMode(WindowMode::Windowed);
		else if (name == "Borderless")
			Game::SetWindowMode(WindowMode::Borderless);
		else if (name == "Fullscreen")
			Game::SetWindowMode(WindowMode::Fullscreen);
	}
};

ST_SCRIPT_CLASS(SettingsMenu)
{
	ST_SCRIPT_FIELD(VolumeSlider);
}
