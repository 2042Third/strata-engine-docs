#include <algorithm>
#include <cstdint>
#include <cstdio>

constexpr int64_t c_StallTimeoutMs = 30000;

// What the server remembers about one client's output.
struct Client
{
	const char* Name = "";
	int64_t PendingBytes = 0;
	int64_t LastProgressMs = 0;
	int64_t ReadEveryMs = 0;     // The client takes some bytes this often
	int64_t BytesPerRead = 0;
	int64_t StopsReadingMs = -1; // -1: the client never stops
	bool Closed = false;
};

// The client's side: the socket takes bytes only while the client reads.
void Flush(Client& client, int64_t nowMs)
{
	if (client.Closed || client.PendingBytes == 0 || nowMs % client.ReadEveryMs != 0)
		return;
	if (client.StopsReadingMs >= 0 && nowMs >= client.StopsReadingMs)
		return;
	client.PendingBytes -= std::min(client.PendingBytes, client.BytesPerRead);
	client.LastProgressMs = nowMs;
}

// The server's side: output waiting and no progress for the timeout means a stalled client.
void CheckDeadline(Client& client, int64_t nowMs)
{
	if (client.Closed || client.PendingBytes == 0)
		return;
	if (nowMs - client.LastProgressMs >= c_StallTimeoutMs)
	{
		client.Closed = true;
		std::printf("%s dropped at %lld ms with %lld bytes waiting\n", client.Name, static_cast<long long>(nowMs), static_cast<long long>(client.PendingBytes));
	}
}

int main()
{
	Client clients[2];
	clients[0] = { "stopped", 100000, 0, 1000, 20000, 3500, false };
	clients[1] = { "slow", 100000, 0, 10000, 1000, -1, false };
	for (int64_t nowMs = 1000; nowMs <= 100000; nowMs += 1000)
	{
		for (Client& client : clients)
		{
			Flush(client, nowMs);
			CheckDeadline(client, nowMs);
		}
	}
	for (const Client& client : clients)
		std::printf("%s: %s, %lld bytes waiting\n", client.Name, client.Closed ? "closed" : "connected", static_cast<long long>(client.PendingBytes));
	return 0;
}
