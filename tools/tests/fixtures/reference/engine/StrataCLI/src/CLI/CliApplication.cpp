// A pretend engine file in the shape of the CLI's usage text (tools/tests/test_reference.py).
namespace Strata::CLI
{

	std::string GetUsageText()
	{
		return fmt::format(
			"StrataCLI {} - command-line client\n"
			"\n"
			"Usage:\n"
			"  StrataCLI call <method> [params] [connection options] [--timeout <ms>]\n"
			"  StrataCLI launch [--project <dir>] [--headless | --no-gpu]\n"
			"                   [--idle-timeout <s>]\n"
			"  StrataCLI --help | --version\n"
			"\n"
			"Commands:\n"
			"  call     Call an editor method and print its result ({{\"Image\"}} results are saved)\n"
			"  launch   Start an editor and wait until it accepts\n"
			"           connections\n"
			"\n"
			"Connection options, in discovery order:\n"
			"  --port <n>                Explicit endpoint, with STRATA_EDITOR_TOKEN or --token <t>\n"
			"  (none)                    The newest running editor\n"
			"Avoid --token where possible.\n"
			"\n"
			"Other options:\n"
			"  --verbose                 Log diagnostics to stderr\n"
			"\n"
			"Environment:\n"
			"  STRATA_SESSION_DIR  Private directory of session files (default: %LOCALAPPDATA%\\Strata\\Sessions,\n"
			"                      ~/.local/share/Strata/Sessions)\n"
			"\n"
			"Exit codes: 0 success; 1 the editor answered with an error.\n",
			c_EngineVersion);
	}

}
