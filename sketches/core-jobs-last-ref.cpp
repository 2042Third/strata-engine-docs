// Where is the last reference to what a job captured released? A Submit that keeps a copy of the function lets the
// submitting thread release it; a Submit that empties the function leaves the release to the thread that ran the job.
#include <cstdio>
#include <functional>
#include <memory>
#include <thread>

namespace
{
	std::thread::id s_ReleasedOn; // written by Probe's destructor

	struct Probe
	{
		~Probe() { s_ReleasedOn = std::this_thread::get_id(); }
	};

	struct Job
	{
		std::function<void()> Function;
	};

	// Runs the job on a worker thread before it returns, as a free worker does with a short job.
	void Submit(std::function<void()> function, bool emptyTheParameter)
	{
		auto job = std::make_shared<Job>();
		if (emptyTheParameter)
		{
			job->Function = std::move(function);
			function = nullptr; // a moved std::function need not be empty: say so
		}
		else
			job->Function = function; // a copy stays in the parameter until Submit returns

		std::thread worker([job]()
		{
			job->Function();
			job->Function = nullptr; // the job lets go of its function when it ran
		});
		worker.join();
	}

	void Run(const char* name, bool emptyTheParameter)
	{
		long seen = 0;
		Submit([probe = std::make_shared<Probe>(), &seen]() { seen = probe.use_count(); }, emptyTheParameter);
		const bool onMain = s_ReleasedOn == std::this_thread::get_id();
		std::printf("%s: the job saw %ld reference(s); the last one went on the %s thread\n", name, seen, onMain ? "submitting" : "worker");
	}
}

int main()
{
	Run("copying", false);
	Run("emptying", true);
	return 0;
}
