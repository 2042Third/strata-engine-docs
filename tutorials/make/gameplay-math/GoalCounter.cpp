#include "StrataScript/StrataScript.h"

using namespace Strata;

// Counts the balls that enter the goal and removes them.
class GoalCounter : public Script
{
public:
	void OnTriggerEnter(const Collision& collision) override
	{
		if (collision.Other.GetName() != "Shot")
			return;
		m_Count++;
		Log::Info("Goal: ", m_Count);
		Entity ball = collision.Other;
		ball.Destroy();
	}
private:
	int32_t m_Count = 0;
};

ST_SCRIPT_CLASS(GoalCounter)
{
}
