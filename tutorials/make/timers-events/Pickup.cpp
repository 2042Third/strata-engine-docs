#include "Pickup.h"

using namespace Strata;

void Pickup::OnUpdate([[maybe_unused]] float deltaTime)
{
	const Entity player = Scene::FindEntityByName("Player");
	if (!player.IsValid())
		return;
	const float distance = glm::distance(player.GetTransform().GetWorldPosition(), GetTransform().GetWorldPosition());
	if (distance > Reach)
		return;

	if (Scoreboard* scoreboard = Scene::FindEntityByName("Game").GetScript<Scoreboard>())
		scoreboard->AddPoint();
	GetEntity().Destroy();
}

ST_SCRIPT_CLASS(Pickup)
{
	ST_SCRIPT_FIELD(Reach);
}
