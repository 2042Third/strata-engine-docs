// The streaming queue's order: a map keyed by priority, negated score and request order. Raising a waiting request
// erases it and inserts it again under a better key, with its old request order.
#include <cstdint>
#include <cstdio>
#include <map>
#include <string>
#include <tuple>

namespace
{

	using Key = std::tuple<uint8_t, float, uint64_t>;

	struct Request
	{
		std::string Name;
		uint8_t Priority;
		float Score;
		uint64_t Order;
	};

	Key MakeKey(const Request& request)
	{
		return Key(request.Priority, -request.Score, request.Order);
	}

	class Queue
	{
	public:
		void Enqueue(const std::string& name, uint8_t priority, float score)
		{
			const Request request { name, priority, score, m_NextOrder++ };
			m_Waiting.emplace(MakeKey(request), request);
		}

		void Raise(const std::string& name, uint8_t priority, float score)
		{
			for (auto it = m_Waiting.begin(); it != m_Waiting.end(); ++it)
			{
				if (it->second.Name != name)
					continue;
				Request request = it->second;
				const bool better = priority < request.Priority || (priority == request.Priority && score > request.Score);
				if (!better)
					return;
				request.Priority = priority;
				request.Score = score;
				m_Waiting.erase(it);
				m_Waiting.emplace(MakeKey(request), request);
				return;
			}
		}

		void PrintDispatchOrder() const
		{
			for (const auto& [key, request] : m_Waiting)
				std::printf("%s ", request.Name.c_str());
			std::printf("\n");
		}

	private:
		std::map<Key, Request> m_Waiting;
		uint64_t m_NextOrder = 0;
	};

}

int main()
{
	Queue queue;
	queue.Enqueue("Tree", 2, 0.0f);
	queue.Enqueue("Rock", 1, 2.0f);
	queue.Enqueue("Door", 1, 2.0f);
	queue.Enqueue("Sky", 0, 0.0f);
	queue.Enqueue("Grass", 1, 7.0f);
	queue.Enqueue("Bush", 1, -1.0f);
	queue.Raise("Rock", 0, 0.0f);
	queue.PrintDispatchOrder();
	return 0;
}
