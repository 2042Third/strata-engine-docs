// A toy handshake and the three ways to break it. ToyMac is a 64-bit non-cryptographic hash: it only lets the
// protocol run and is never a real message authentication code.
#include <cstdint>
#include <cstdio>
#include <string>

std::string ToyMac(const std::string& key, const std::string& message)
{
	uint64_t hash = 14695981039346656037ull;
	for (const char character : key + "|" + message)
	{
		hash ^= static_cast<uint8_t>(character);
		hash *= 1099511628211ull;
	}
	char text[17];
	std::snprintf(text, sizeof(text), "%016llx", static_cast<unsigned long long>(hash));
	return text;
}

size_t g_Examined = 0; // Stands in for the time a comparison takes

bool EarlyExitEquals(const std::string& left, const std::string& right)
{
	for (size_t index = 0; index < left.size() && index < right.size(); index++)
	{
		g_Examined++;
		if (left[index] != right[index])
			return false;
	}
	return left.size() == right.size();
}

bool ConstantTimeEquals(const std::string& left, const std::string& right)
{
	bool same = left.size() == right.size();
	for (size_t index = 0; index < left.size() && index < right.size(); index++)
	{
		g_Examined++;
		same = same && left[index] == right[index];
	}
	return same;
}

// The attacker knows the proof has 16 hexadecimal digits, and sees only how long each comparison took.
std::string GuessProof(const std::string& expected, bool (*equals)(const std::string&, const std::string&))
{
	std::string guess(16, '0');
	for (size_t position = 0; position < guess.size(); position++)
	{
		size_t bestExamined = 0;
		char bestDigit = '0';
		for (const char digit : std::string("0123456789abcdef"))
		{
			guess[position] = digit;
			g_Examined = 0;
			if (equals(guess, expected))
				return guess; // Accepted: the attacker sees that too
			if (g_Examined > bestExamined)
			{
				bestExamined = g_Examined;
				bestDigit = digit;
			}
		}
		guess[position] = bestDigit;
	}
	return guess;
}

int main()
{
	const std::string token = "6c1f0a9e55d27b3a";
	const std::string clientNonce = "c0ffee00";
	const std::string serverNonce = "5eed1234";
	const std::string serverProof = ToyMac(token, "server" + clientNonce + serverNonce);
	const std::string clientProof = ToyMac(token, "client" + serverNonce + clientNonce);
	std::printf("handshake: client accepts server %d, server accepts client %d\n",
		ConstantTimeEquals(serverProof, ToyMac(token, "server" + clientNonce + serverNonce)),
		ConstantTimeEquals(clientProof, ToyMac(token, "client" + serverNonce + clientNonce)));

	// Break 1: the token travels. Anyone who reads the connection now holds the secret.
	std::printf("break 1: the wire carried token=%s\n", token.c_str());

	// Break 2: an early exit tells how many leading digits of a guess are right.
	const bool early = GuessProof(clientProof, EarlyExitEquals) == clientProof;
	const bool constant = GuessProof(clientProof, ConstantTimeEquals) == clientProof;
	std::printf("break 2: guessed the proof with ==: %d, in constant time: %d\n", early, constant);

	// Break 3: the client proves first, so an impostor that sends any nonce gets a proof to guess against.
	const std::string weakToken = "4821";
	const std::string sample = ToyMac(weakToken, "client" + serverNonce + clientNonce);
	for (int candidate = 0; candidate < 10000; candidate++)
	{
		char text[16];
		std::snprintf(text, sizeof(text), "%04d", candidate);
		if (ToyMac(text, "client" + serverNonce + clientNonce) == sample)
			std::printf("break 3: the impostor found the token %s in %d tries\n", text, candidate + 1);
	}
	return 0;
}
