#include "StrataScript/StrataScript.h"

using namespace Strata;

// Scrolling credits: the text moves up inside a mask and starts again below it.
class Credits : public Script
{
public:
	Entity Content;
	float Speed = 45.0f;      // Canvas units per second
	float ViewHeight = 360.0f; // The mask's height

	void OnUpdate(float) override
	{
		if (!Content.IsValid())
			return;
		glm::vec2 position = Content.GetProperty<glm::vec2>("UIRect", "Position").value_or(glm::vec2(0.0f));
		const float height = Content.GetProperty<glm::vec2>("UIRect", "Size").value_or(glm::vec2(0.0f)).y;
		position.y -= Speed * Time::GetUnscaledDeltaTime();
		if (position.y < -height)
			position.y = ViewHeight;
		Content.SetProperty("UIRect", "Position", position);
	}
};

ST_SCRIPT_CLASS(Credits)
{
	ST_SCRIPT_FIELD(Content);
	ST_SCRIPT_FIELD(Speed);
	ST_SCRIPT_FIELD(ViewHeight);
}
