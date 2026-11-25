// A toy end-to-end test: start a program, wait for it by the clock, check its exit code and its output.
// The program under test is this executable itself, started again with a mode argument.
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <future>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>

struct RunResult
{
	bool TimedOut = false;
	int ExitCode = -1;
	std::string Output;
};

// Runs `program mode`, sends its output to a file and gives up waiting after `timeout`.
RunResult RunProgram(const std::string& program, const std::string& mode, std::chrono::milliseconds timeout)
{
	const std::filesystem::path outputPath = std::filesystem::path("toy-" + mode + ".txt");
	std::string command = "\"" + program + "\" " + mode + " > \"" + outputPath.string() + "\"";
#if defined(_WIN32)
	command = "\"" + command + "\""; // cmd.exe strips one pair of quotes
#endif
	std::future<int> child = std::async(std::launch::async, [command]() { return std::system(command.c_str()); });

	RunResult result;
	// The deadline is a time, never a count of polls or frames.
	result.TimedOut = child.wait_for(timeout) != std::future_status::ready;
	result.ExitCode = child.get(); // a real harness would terminate the child here instead of waiting
	std::stringstream text;
	text << std::ifstream(outputPath).rdbuf(); // the temporary closes the file before it is removed
	result.Output = text.str();
	std::filesystem::remove(outputPath);
	return result;
}

int main(int argc, char** argv)
{
	if (argc > 1 && std::string(argv[1]) == "ready")
	{
		std::cout << "Running headless\n";
		return 0;
	}
	if (argc > 1 && std::string(argv[1]) == "slow")
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(400));
		return 0;
	}

	const RunResult quick = RunProgram(argv[0], "ready", std::chrono::seconds(10));
	std::cout << "ready: timed out " << quick.TimedOut << ", exit " << quick.ExitCode << ", says '" << quick.Output.substr(0, 16) << "'\n";
	const RunResult slow = RunProgram(argv[0], "slow", std::chrono::milliseconds(100));
	std::cout << "slow: timed out " << slow.TimedOut << ", exit " << slow.ExitCode << "\n";
	return 0;
}
