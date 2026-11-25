#include <cstdint>
#include <cstdio>
#include <map>
#include <optional>
#include <string>

// A model of the pinned fetch: the cache is a map from folder name to the digest stamped on it.
// FNV-1a stands in for SHA-256 here; the shape of the algorithm is what the toy shows.
struct Network
{
	std::string Body;
	int FailuresLeft = 0;
};

static std::uint64_t Digest(const std::string& bytes)
{
	std::uint64_t hash = 14695981039346656037ull;
	for (char c : bytes)
		hash = (hash ^ static_cast<unsigned char>(c)) * 1099511628211ull;
	return hash;
}

static std::optional<std::string> Download(Network& network)
{
	if (network.FailuresLeft > 0)
	{
		network.FailuresLeft--;
		return std::nullopt;
	}
	return network.Body;
}

// Returns an empty string on success, else the reason. Never stops the program.
static std::string Fetch(std::map<std::string, std::uint64_t>& cache, Network& network, const std::string& name, std::uint64_t expected)
{
	const auto stamp = cache.find(name);
	if (stamp != cache.end() && stamp->second == expected)
	{
		std::printf("  stamp matches: no lock, no network\n");
		return "";
	}

	std::printf("  lock taken\n");
	std::optional<std::string> body;
	for (int attempt = 1; attempt <= 3 && !body; ++attempt)
	{
		std::printf("  download attempt %d\n", attempt);
		body = Download(network);
	}
	if (!body)
		return "could not download after 3 attempts";
	if (Digest(*body) != expected)
		return "digest differs from the pin: the download was not used";

	// Extract next to the final folder, then rename: nobody sees half an extraction.
	cache[name + ".staging"] = expected;
	cache[name] = cache[name + ".staging"];
	cache.erase(name + ".staging");
	std::printf("  extracted and renamed\n");
	return "";
}

static void Run(const char* title, std::map<std::string, std::uint64_t>& cache, Network& network, std::uint64_t expected)
{
	std::printf("%s\n", title);
	const std::string error = Fetch(cache, network, "slang", expected);
	std::printf("  result: %s\n", error.empty() ? "ready" : error.c_str());
}

int main()
{
	std::map<std::string, std::uint64_t> cache;
	Network network = { "archive bytes", 1 };
	const std::uint64_t pin = Digest("archive bytes");

	Run("1. first configure, one network failure", cache, network, pin);
	Run("2. second configure", cache, network, pin);
	Network replaced = { "other bytes", 0 };
	Run("3. the pin changed, the server sends other bytes", cache, replaced, Digest("archive bytes v2"));
	return 0;
}
