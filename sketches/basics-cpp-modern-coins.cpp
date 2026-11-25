// Practice 5: the nearest coin as an optional, a game state with a switch, and the coin count as a constexpr.
#include <cstdint>
#include <iostream>
#include <optional>
enum class GameState : uint8_t { Playing, Won };
constexpr size_t c_CoinCount = 3;
struct Coin { float Distance = 0.0f; bool Taken = false; };
std::optional<size_t> FindNearest(const Coin (&coins)[c_CoinCount])
{
	std::optional<size_t> best;
	for (size_t index = 0; index < c_CoinCount; index++)
		if (!coins[index].Taken && (!best || coins[index].Distance < coins[*best].Distance)) best = index;
	return best;
}
int main()
{
	const Coin open[c_CoinCount] = { { 4.0f, true }, { 1.5f }, { 9.0f } };
	const Coin taken[c_CoinCount] = { { 4.0f, true }, { 1.5f, true }, { 9.0f, true } };
	std::cout << "nearest: " << *FindNearest(open) << '\n';
	switch (FindNearest(taken) ? GameState::Playing : GameState::Won)
	{
		case GameState::Playing: std::cout << "keep going\n"; break;
		case GameState::Won: std::cout << "you win\n"; break;
	}
}
