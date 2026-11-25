#include <algorithm>
#include <cctype>
#include <cstdio>
#include <string>

// The fast path of the fetch: a folder is reused when its stamp equals the pinned digest.
// Both sides are compared in lower case, as the real code does.
static std::string Lower(std::string text)
{
	std::transform(text.begin(), text.end(), text.begin(), [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
	return text;
}

static const char* Decide(const std::string& stamp, const std::string& pin)
{
	return Lower(stamp) == Lower(pin) ? "reuse the folder, no lock, no network" : "take the lock and fetch";
}

int main()
{
	std::printf("no stamp:         %s\n", Decide("", "E6DD32"));
	std::printf("same digest:      %s\n", Decide("e6dd32", "E6DD32"));
	std::printf("pin was bumped:   %s\n", Decide("e6dd32", "B83147"));
	return 0;
}
