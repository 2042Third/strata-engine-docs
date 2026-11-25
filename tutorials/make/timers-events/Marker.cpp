#include "StrataScript/StrataScript.h"

using namespace Strata;

// A marker above a row of five cubes: an arrow key moves it one cube, and holding the key repeats the move.
class Marker : public Script
{
public:
	void OnUpdate(float deltaTime) override
	{
		if (m_Left.Update(deltaTime))
			m_Index = glm::max(m_Index - 1, 0);
		if (m_Right.Update(deltaTime))
			m_Index = glm::min(m_Index + 1, 4);

		glm::vec3 position = GetTransform().GetTranslation();
		position.x = static_cast<float>(m_Index - 2) * 2.0f;
		GetTransform().SetTranslation(position);
	}

private:
	KeyRepeat m_Left = KeyRepeat(Key::Left);
	KeyRepeat m_Right = KeyRepeat(Key::Right);
	int32_t m_Index = 2;
};

ST_SCRIPT_CLASS(Marker) {}
