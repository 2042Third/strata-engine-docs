// A pretend engine file in the shape of the editor's options (tools/tests/test_reference.py).
namespace Strata
{

	namespace
	{

		// Every option the editor understands.
		constexpr CommandLineOption c_Arguments[] = {
			{ "--project", "<directory>", "Open this project" },
			{ "--no-gpu", nullptr, "Run without a graphics device "
				"(implies --headless)" },
			{ "--help", nullptr, "Print this help and exit" } };

	}

}
