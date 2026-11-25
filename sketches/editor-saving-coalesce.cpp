// A toy save queue: one request writes, at most one waits, and a newer request replaces the waiting one.
#include <iostream>
#include <optional>
#include <utility>
#include <vector>

struct Request
{
	int Snapshot = 0;                // Which state of the scene the request holds
	std::vector<int> CompletionIds;  // Everyone who is told when it is written
};

class Queue
{
public:
	int Submit(int snapshot)
	{
		const int id = m_NextId++;
		if (!m_Running)
		{
			m_Running = Request{ snapshot, { id } };
			return id;
		}
		if (m_Waiting)
		{
			// The waiting request never started: the newer snapshot is written for both.
			m_Waiting->Snapshot = snapshot;
			m_Waiting->CompletionIds.push_back(id);
			return id;
		}
		m_Waiting = Request{ snapshot, { id } };
		return id;
	}

	void Finish()
	{
		std::cout << "wrote snapshot " << m_Running->Snapshot << " for requests";
		for (const int id : m_Running->CompletionIds)
			std::cout << " " << id;
		std::cout << "\n";
		m_Running = std::move(m_Waiting);
		m_Waiting.reset();
	}

	bool IsBusy() const { return m_Running.has_value(); }
private:
	std::optional<Request> m_Running;
	std::optional<Request> m_Waiting;
	int m_NextId = 1;
};

int main()
{
	Queue queue;
	queue.Submit(10); // Starts writing at once
	queue.Submit(11); // Waits
	queue.Submit(12); // Replaces 11's snapshot
	queue.Submit(13); // Replaces 12's snapshot
	while (queue.IsBusy())
		queue.Finish();
	return 0;
}
