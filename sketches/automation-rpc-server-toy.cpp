#include <cstdio>
#include <deque>
#include <memory>
#include <string>
#include <vector>

constexpr size_t c_MaxQueued = 3;
constexpr int c_MaxInFlight = 2;

struct Request
{
	int Id = 0;
	std::string Method;
};

// Answers exactly once: a responder destroyed without an answer answers "dropped".
class Responder
{
public:
	Responder(int id, int& inFlight)
		: m_Id(id), m_InFlight(inFlight)
	{
	}

	~Responder()
	{
		if (!m_Answered)
			Respond("error: dropped");
	}

	void Respond(const char* text)
	{
		if (m_Answered)
			return;
		m_Answered = true;
		m_InFlight--;
		std::printf("  answer #%d: %s\n", m_Id, text);
	}
private:
	int m_Id;
	int& m_InFlight;
	bool m_Answered = false;
};

struct Waiting
{
	int DueFrame = 0;
	std::shared_ptr<Responder> Handle;
};

class ToyServer
{
public:
	// The "network thread": reads from the wire only while there is room.
	void Read(std::deque<Request>& wire)
	{
		while (!wire.empty() && m_Queue.size() < c_MaxQueued && m_InFlight < c_MaxInFlight)
		{
			m_Queue.push_back(wire.front());
			wire.pop_front();
			m_InFlight++;
		}
	}

	// The "main thread": once per frame, handles what the queue holds.
	void ProcessRequests(int frame)
	{
		std::deque<Request> requests;
		requests.swap(m_Queue);
		for (const Request& request : requests)
		{
			auto responder = std::make_shared<Responder>(request.Id, m_InFlight);
			if (request.Method == "wait")
				m_Waiting.push_back({ frame + 2, responder });
			else if (request.Method != "drop")
				responder->Respond("ok");
		}
		std::erase_if(m_Waiting, [frame](Waiting& waiting)
		{
			if (waiting.DueFrame > frame)
				return false;
			waiting.Handle->Respond("ok, after two frames");
			return true;
		});
	}
private:
	std::deque<Request> m_Queue;
	std::vector<Waiting> m_Waiting;
	int m_InFlight = 0;
};

int main()
{
	std::deque<Request> wire = { { 1, "wait" }, { 2, "ping" }, { 3, "drop" }, { 4, "ping" }, { 5, "ping" } };
	ToyServer server;
	for (int frame = 1; frame <= 4; frame++)
	{
		server.Read(wire);
		std::printf("frame %d: %zu requests still on the wire\n", frame, wire.size());
		server.ProcessRequests(frame);
	}
	return 0;
}
