#include <cmath>
#include <cstdio>
enum class GuardState { Patrol, Chase, Return };
GuardState Next(GuardState state, float playerDistance, float x)
{
	switch (state)
	{
		case GuardState::Patrol: return playerDistance < 5.0f ? GuardState::Chase : state;
		case GuardState::Chase: return playerDistance > 8.0f ? GuardState::Return : state;
		default: return x <= 0.0f ? GuardState::Patrol : state;
	}
}
int main()
{
	const float playerPath[] = { 10, 4, 4, 4, 20, 20, 20 };
	GuardState state = GuardState::Patrol;
	float x = 0.0f;
	for (float player : playerPath)
	{
		state = Next(state, std::fabs(player - x), x);
		if (state == GuardState::Chase) x += std::fmin(std::fabs(player - x), 2.0f) * (player > x ? 1.0f : -1.0f);
		else if (state == GuardState::Return) x = std::fmax(0.0f, x - 2.0f);
		std::printf("player at %2.0f: state %d, guard at %.0f\n", player, static_cast<int>(state), x);
	}
}
