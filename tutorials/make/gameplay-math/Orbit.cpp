#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Moves the entity round a circle of the given radius, about the point (0, 0.5, 0).
class Orbit : public Script
{
public:
	float Radius = 4.0f;
	float Speed = 0.5f; // Radians per second

	void OnUpdate(float deltaTime) override
	{
		m_Angle += Speed * deltaTime;
		GetTransform().SetTranslation(glm::vec3(std::cos(m_Angle) * Radius, 0.5f, std::sin(m_Angle) * Radius));
	}
private:
	float m_Angle = 0.0f;
};

ST_SCRIPT_CLASS(Orbit)
{
	ST_SCRIPT_FIELD(Radius);
	ST_SCRIPT_FIELD(Speed);
}
