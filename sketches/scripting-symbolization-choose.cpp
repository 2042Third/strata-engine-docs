// The fault location of the toy: the first frame of the module that has a file and is no runtime code.
#include <cstdio>
#include <optional>
#include <string>
#include <vector>

namespace
{
	struct Frame
	{
		std::string Module;
		std::string Function;
		std::string File; // Empty when unknown
	};

	bool IsRuntime(const Frame& frame)
	{
		return frame.File.find("\\crt\\src\\") != std::string::npos || frame.File.ends_with("ScriptModuleEntry.cpp");
	}

	std::optional<Frame> Choose(const std::vector<Frame>& stack, const std::string& module)
	{
		const Frame* first = nullptr;
		for (const Frame& frame : stack)
		{
			if (frame.Module != module)
				continue;
			if (!first)
				first = &frame;
			if (!frame.File.empty() && !IsRuntime(frame))
				return frame;
		}
		return first ? std::optional<Frame>(*first) : std::nullopt;
	}

	void Show(const char* title, const std::vector<Frame>& stack)
	{
		const std::optional<Frame> chosen = Choose(stack, "Game.dll");
		const char* name = !chosen ? "none" : chosen->Function.empty() ? "(first frame, no name)" : chosen->Function.c_str();
		std::printf("%s: %s\n", title, name);
	}
}

int main()
{
	Show("abort in a script", { { "Game.dll", "abort", "d:\\crt\\src\\abort.cpp" }, { "Game.dll", "AbortHandler", "ScriptModuleEntry.cpp" }, { "Game.dll", "Crash", "FaultScripts.cpp" } });
	Show("no debug information", { { "Game.dll", "", "" }, { "Game.dll", "", "" } });
	Show("a fault in the engine", { { "Strata.exe", "Update", "Scene.cpp" } });
	return 0;
}
