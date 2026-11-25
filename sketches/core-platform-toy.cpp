// A toy platform seam: one interface, two implementations, one of them chosen when the program is built.
// In Strata the build chooses between two files; here one file holds both, so that #if does the choosing.
#include <cstdio>
#include <string>
#include <string_view>

// Detection: exactly one TOY_PLATFORM_* is defined, or the build stops.
#if defined(_WIN32)
	#define TOY_PLATFORM_WINDOWS
#elif defined(__linux__) || defined(__APPLE__)
	#define TOY_PLATFORM_POSIX
#else
	#error "The toy supports Windows, Linux and macOS"
#endif

// What the rest of the program sees: no operating-system header and no #if.
class Platform
{
public:
	static std::string_view GetName();
	static std::string GetUserDataRule(std::string_view applicationName);
};

#if defined(TOY_PLATFORM_WINDOWS)

// This block stands for Platform/Windows/WindowsPlatform.cpp.
std::string_view Platform::GetName() { return "Windows"; }

std::string Platform::GetUserDataRule(std::string_view applicationName)
{
	return "%LOCALAPPDATA%/" + std::string(applicationName);
}

#else

// This block stands for Platform/Posix/PosixPlatform.cpp.
std::string_view Platform::GetName() { return "a POSIX system"; }

std::string Platform::GetUserDataRule(std::string_view applicationName)
{
	return "$XDG_DATA_HOME/" + std::string(applicationName);
}

#endif

int main()
{
	// Game code calls the seam and never asks which system it runs on.
	std::printf("Running on %s\n", std::string(Platform::GetName()).c_str());
	std::printf("Settings go to %s\n", Platform::GetUserDataRule("Toy").c_str());
	return 0;
}
