// A toy discovery: the session files are rows in a vector, and "alive" stands for the check of the process.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

struct Session
{
	uint32_t ProcessId = 0;
	uint16_t Port = 0;
	std::string StartedAt;
	std::string ProjectPath;
	bool Alive = false;
};

// Newest first: the timestamps have one fixed format, so comparing the text compares the times.
static std::vector<Session> FindSessions(std::vector<Session> files)
{
	std::erase_if(files, [](const Session& session) { return !session.Alive; });
	std::sort(files.begin(), files.end(), [](const Session& left, const Session& right)
	{
		if (left.StartedAt != right.StartedAt)
			return left.StartedAt > right.StartedAt;
		return left.ProcessId > right.ProcessId;
	});
	return files;
}

// With a project, only the editors that have it open; without one, every editor.
static std::vector<Session> Discover(const std::vector<Session>& files, const std::string& project)
{
	std::vector<Session> sessions = FindSessions(files);
	if (!project.empty())
		std::erase_if(sessions, [&](const Session& session) { return session.ProjectPath != project; });
	return sessions;
}

static void Print(const std::string& title, const std::vector<Session>& sessions)
{
	std::cout << title << ":";
	for (const Session& session : sessions)
		std::cout << " " << session.Port;
	std::cout << "\n";
}

int main()
{
	const std::vector<Session> files = {
		{ 40101, 51001, "2026-01-01T00:00:00Z", "Cave", true },
		{ 40102, 51002, "2026-02-01T00:00:00Z", "Beach", true },
		{ 40103, 51003, "2026-03-01T00:00:00Z", "", true },
		{ 40104, 51004, "2025-12-01T00:00:00Z", "Cave", true },
		{ 40105, 51005, "2026-04-01T00:00:00Z", "Beach", false } };

	Print("every editor", Discover(files, ""));
	Print("project Cave", Discover(files, "Cave"));
	Print("project Beach", Discover(files, "Beach"));
	return 0;
}
