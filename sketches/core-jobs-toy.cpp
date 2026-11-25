// A toy job system: one queue, a few threads, and a Wait that runs the job itself when no thread has started it.
#include <atomic>
#include <condition_variable>
#include <cstdio>
#include <deque>
#include <functional>
#include <memory>
#include <mutex>
#include <thread>
#include <vector>

namespace
{
	struct Job
	{
		std::function<void()> Function;
		std::atomic<bool> Claimed = false;
		std::atomic<bool> Completed = false;
		std::mutex Mutex;
		std::condition_variable Condition;
	};

	using JobRef = std::shared_ptr<Job>;

	// Runs the job unless another thread claimed it first.
	void RunIfFirst(Job& job)
	{
		if (job.Claimed.exchange(true))
			return;
		job.Function();
		job.Function = nullptr;
		{
			std::scoped_lock lock(job.Mutex);
			job.Completed = true;
		}
		job.Condition.notify_all();
	}

	void Wait(const JobRef& job)
	{
		RunIfFirst(*job); // does nothing when a pool thread has the job
		std::unique_lock lock(job->Mutex);
		job->Condition.wait(lock, [&job]() { return job->Completed.load(); });
	}

	class Pool
	{
	public:
		explicit Pool(unsigned threadCount)
		{
			for (unsigned index = 0; index < threadCount; index++)
				m_Threads.emplace_back([this]() { ThreadMain(); });
		}

		~Pool()
		{
			{
				std::scoped_lock lock(m_Mutex);
				m_Stopping = true;
			}
			m_Condition.notify_all();
			for (std::thread& thread : m_Threads)
				thread.join();
		}

		JobRef Submit(std::function<void()> function)
		{
			auto job = std::make_shared<Job>();
			job->Function = std::move(function);
			{
				std::scoped_lock lock(m_Mutex);
				m_Queue.push_back(job);
			}
			m_Condition.notify_one();
			return job;
		}
	private:
		void ThreadMain()
		{
			while (true)
			{
				JobRef job;
				{
					std::unique_lock lock(m_Mutex);
					m_Condition.wait(lock, [this]() { return m_Stopping || !m_Queue.empty(); });
					if (m_Queue.empty())
						return;
					job = std::move(m_Queue.front());
					m_Queue.pop_front();
				}
				RunIfFirst(*job);
			}
		}
	private:
		std::mutex m_Mutex;
		std::condition_variable m_Condition;
		std::deque<JobRef> m_Queue;
		std::vector<std::thread> m_Threads;
		bool m_Stopping = false;
	};
}

int main()
{
	const std::thread::id mainThread = std::this_thread::get_id();
	Pool pool(1); // one thread: the case where a waiting job would deadlock a pool without the claim

	std::atomic<int> value = 0;
	const JobRef outer = pool.Submit([&]()
	{
		const JobRef inner = pool.Submit([&]() { value = 41; });
		Wait(inner);
		value++;
	});
	Wait(outer);
	std::printf("outer waited for inner: value is %d\n", value.load());

	std::atomic<bool> holding = false;
	std::atomic<bool> release = false;
	pool.Submit([&]()
	{
		holding = true;
		while (!release.load())
			std::this_thread::yield();
	});
	while (!holding.load())
		std::this_thread::yield();

	std::atomic<bool> ranHere = false;
	const JobRef quick = pool.Submit([&]() { ranHere = std::this_thread::get_id() == mainThread; });
	Wait(quick); // the only thread is busy, so the waiting thread runs the job
	std::printf("the job ran on the waiting thread: %s\n", ranHere.load() ? "yes" : "no");
	release = true;
	return 0;
}
