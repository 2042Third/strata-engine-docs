#include "Scoreboard.h"

#include <string>

using namespace Strata;

void Scoreboard::AddPoint()
{
	Score++;
	const Entity text = Scene::FindEntityByName("ScoreText");
	if (text.IsValid())
		text.GetUI().SetText("Score: " + std::to_string(Score));
}

ST_SCRIPT_CLASS(Scoreboard)
{
	ST_SCRIPT_FIELD(Score);
}
