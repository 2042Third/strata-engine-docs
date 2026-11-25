// The goal's next level: the player entering the goal's trigger loads the scene in the field Next.

#include "StrataScript/StrataScript.h"

using namespace Strata;

class NextLevel : public Script
{
public:
	AssetHandle Next;

	void OnTriggerEnter(const Collision& collision) override
	{
		if (collision.Other.IsValid() && collision.Other.GetTag() == "Player")
			Game::LoadScene(Next);
	}
};

ST_SCRIPT_CLASS(NextLevel)
{
	ST_SCRIPT_FIELD(Next);
}
