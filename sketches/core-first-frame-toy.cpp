// A toy program start: a launch made before the application, startup steps that unwind, a loop and the exit codes.
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace
{
	struct Step
	{
		std::string Name;
		bool Works = true;
	};

	class Application
	{
	public:
		Application(const std::vector<Step>& steps, int maxFrames)
			: m_MaxFrames(maxFrames)
		{
			for (const Step& step : steps)
			{
				if (!step.Works)
				{
					std::printf("  %s failed\n", step.Name.c_str());
					Unwind();
					m_ExitCode = 1;
					return;
				}
				std::printf("  started %s\n", step.Name.c_str());
				m_Started.push_back(step.Name);
			}
			m_Running = true;
		}

		~Application() { Unwind(); }

		void Run()
		{
			for (int frame = 1; m_Running && frame <= m_MaxFrames; frame++)
				std::printf("  frame %d\n", frame);
		}

		int GetExitCode() const { return m_ExitCode; }
	private:
		void Unwind()
		{
			for (; !m_Started.empty(); m_Started.pop_back())
				std::printf("  stopped %s\n", m_Started.back().c_str());
		}
	private:
		std::vector<std::string> m_Started;
		int m_MaxFrames;
		bool m_Running = false;
		int m_ExitCode = 0;
	};

	struct Launch
	{
		std::function<std::unique_ptr<Application>()> Create;
	};

	int s_StartupExitCode = 1;

	// Reads the command line. Nothing to run: no launch, and the exit code the process ends with.
	std::optional<Launch> CreateApplication(const std::vector<std::string>& arguments)
	{
		bool audioWorks = true;
		int frames = 0;
		for (size_t index = 0; index < arguments.size(); index++)
		{
			if (arguments[index] == "--help")
			{
				std::printf("  usage: toy [--fail-audio] [--frames <count>]\n");
				s_StartupExitCode = 0;
				return std::nullopt;
			}
			if (arguments[index] == "--fail-audio")
				audioWorks = false;
			else if (arguments[index] == "--frames" && index + 1 < arguments.size())
				frames = std::atoi(arguments[++index].c_str());
			else
			{
				std::printf("  unknown argument '%s'\n", arguments[index].c_str());
				s_StartupExitCode = 3;
				return std::nullopt;
			}
		}
		const std::vector<Step> steps = { { "jobs" }, { "window" }, { "audio", audioWorks }, { "project" } };
		return Launch { [steps, frames]() { return std::make_unique<Application>(steps, frames); } };
	}

	int RunProgram(const std::vector<std::string>& arguments)
	{
		std::optional<Launch> launch = CreateApplication(arguments);
		if (!launch)
			return s_StartupExitCode;
		std::unique_ptr<Application> application = launch->Create();
		application->Run();
		return application->GetExitCode();
	}
}

int main()
{
	const std::vector<std::vector<std::string>> runs = { { "--frames", "2" }, { "--fail-audio" }, { "--help" }, { "--bogus" } };
	for (const std::vector<std::string>& arguments : runs)
	{
		std::printf("toy");
		for (const std::string& argument : arguments)
			std::printf(" %s", argument.c_str());
		std::printf("\n");
		s_StartupExitCode = 1;
		const int exitCode = RunProgram(arguments);
		std::printf("  exit code %d\n", exitCode);
	}
}
