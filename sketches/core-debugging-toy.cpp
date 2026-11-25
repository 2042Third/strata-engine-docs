// A toy asynchronous log: lines are queued, a writer thread prints them in order, and a warning waits for its own line.
#include <condition_variable>
#include <cstdio>
#include <deque>
#include <mutex>
#include <string>
#include <thread>

class ToySink
{
public:
	ToySink()
		: m_Thread([this]() { Run(); })
	{
	}
	~ToySink() { Stop(); }

	void Log(const std::string& line, bool isWarning)
	{
		std::unique_lock<std::mutex> lock(m_Mutex);
		m_Progress.wait(lock, [this]() { return m_Queue.size() < c_MaxQueued; }); // a burst waits for room
		m_Queue.push_back(line);
		const size_t target = ++m_Queued;
		m_Wake.notify_one();
		if (isWarning)
			m_Progress.wait(lock, [&]() { return m_Written >= target; }); // returns once the line is out
	}

	void Stop()
	{
		{
			std::scoped_lock<std::mutex> lock(m_Mutex);
			m_Stopping = true;
		}
		m_Wake.notify_one();
		if (m_Thread.joinable())
			m_Thread.join();
	}
private:
	void Run()
	{
		std::unique_lock<std::mutex> lock(m_Mutex);
		while (true)
		{
			m_Wake.wait(lock, [this]() { return !m_Queue.empty() || m_Stopping; });
			if (m_Queue.empty())
				return; // stopping, and everything is written
			const std::string line = m_Queue.front();
			m_Queue.pop_front();
			m_Progress.notify_all(); // there is room again
			lock.unlock();
			std::printf("writer: %s\n", line.c_str()); // the slow part runs outside the lock
			lock.lock();
			m_Written++;
			m_Progress.notify_all();
		}
	}
	static constexpr size_t c_MaxQueued = 4;
	std::mutex m_Mutex;
	std::condition_variable m_Wake;     // for the writer: a line or Stop
	std::condition_variable m_Progress; // for the loggers: room, or a line written
	std::deque<std::string> m_Queue;
	size_t m_Queued = 0;
	size_t m_Written = 0;
	bool m_Stopping = false;
	std::thread m_Thread; // last, so that everything it uses exists before it starts
};

int main()
{
	ToySink sink;
	sink.Log("info: loading the scene", false);
	sink.Log("info: 3 meshes", false);
	sink.Log("warning: a texture is missing", true);
	std::printf("main: the warning returned, so three lines are out\n");
	sink.Log("info: using the fallback", false);
	sink.Log("info: scene ready", false);
	sink.Stop();
	std::printf("main: stopped, nothing is left in the queue\n");
}
