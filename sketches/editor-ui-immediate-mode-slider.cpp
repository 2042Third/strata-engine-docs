#include <cstdio>
#include <functional>

struct Light
{
	float Intensity = 0.5f;
};

// What the person does with the mouse in one frame.
struct Mouse
{
	bool Dragging = false;
	float Position = 0.0f; // Where along the slider the mouse is, from 0 to 1
};

// Retained: a long-lived object that keeps its own copy of the value and calls back on a change.
class RetainedSlider
{
public:
	float Value = 0.0f;
	std::function<void(float)> OnChange;

	void Update(const Mouse& mouse)
	{
		if (!mouse.Dragging)
			return;
		Value = mouse.Position;
		if (OnChange)
			OnChange(Value);
	}
};

// Immediate: one function that draws the slider from the caller's variable and reports a change.
bool Slider(const Mouse& mouse, float* value)
{
	if (!mouse.Dragging)
		return false;
	*value = mouse.Position;
	return true;
}

int main()
{
	const Mouse frames[3] = { { true, 0.4f }, { true, 0.7f }, { false, 0.0f } };

	Light retainedLight;
	RetainedSlider retained;
	retained.Value = retainedLight.Intensity; // The copy is made once, when the slider is built
	retained.OnChange = [&retainedLight](float value) { retainedLight.Intensity = value; };

	Light immediateLight;
	for (int frame = 0; frame < 3; frame++)
	{
		if (frame == 2)
		{
			// Undo restores the light's old value behind the slider's back.
			retainedLight.Intensity = 0.5f;
			immediateLight.Intensity = 0.5f;
		}
		retained.Update(frames[frame]);
		Slider(frames[frame], &immediateLight.Intensity);
		std::printf("frame %d: retained slider %.2f, light %.2f | immediate slider %.2f, light %.2f\n", frame + 1,
			retained.Value, retainedLight.Intensity, immediateLight.Intensity, immediateLight.Intensity);
	}
	return 0;
}
