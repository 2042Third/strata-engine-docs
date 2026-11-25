// A pretend engine file in the shape of the runtime's options (tools/tests/test_reference.py).
namespace Strata
{

	namespace
	{

		constexpr CommandLineOption c_Arguments[] = {
			{ "--game", "<file.stgame>", "Play this game" },
			{ "--quality", "<low|medium|high|ultra>", "Draw with this preset" } };

	}

}
