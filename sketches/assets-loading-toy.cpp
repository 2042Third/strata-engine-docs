// A toy asset manager: a waiting list, one worker, a completion list that the frame polls, and a generation counter.
// The worker's steps run on the main thread, in turn, so that the output is the same on every run.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <map>

namespace
{

	enum class State { Unloaded, Loading, Ready, Failed };

	const char* ToString(State state)
	{
		switch (state)
		{
			case State::Unloaded: return "Unloaded";
			case State::Loading:  return "Loading";
			case State::Ready:    return "Ready";
			case State::Failed:   return "Failed";
		}
		return "?";
	}

	struct Guards
	{
		bool CheckGeneration = true;     // Discard a completion whose load is no longer wanted
		bool OnlyWhenUnloaded = true;    // Start a load only from the Unloaded state
		bool CatchFailures = true;       // A load that fails still ends in a completion
		uint64_t MaxInFlightBytes = 128; // Megabytes; 0 means no limit
	};

	struct Entry
	{
		State Current = State::Unloaded;
		uint64_t Generation = 1;
		uint64_t Megabytes = 0;
		bool Broken = false;
	};

	struct Job { int Handle; uint64_t Generation; uint64_t Megabytes; bool Broken; };
	struct Completion { Job Source; bool Ok; };

	class ToyManager
	{
	public:
		explicit ToyManager(Guards guards)
			: m_Guards(guards)
		{
		}

		void Add(int handle, uint64_t megabytes, bool broken) { m_Entries[handle] = Entry { State::Unloaded, 1, megabytes, broken }; }

		bool GetAsset(int handle)
		{
			Entry& entry = m_Entries[handle];
			if (entry.Current == State::Ready)
				return true;
			if (!m_Guards.OnlyWhenUnloaded || entry.Current == State::Unloaded)
			{
				entry.Current = State::Loading;
				m_Waiting.push_back(Job { handle, entry.Generation, entry.Megabytes, entry.Broken });
				m_LoadsStarted++;
				Pump();
			}
			return false;
		}

		void Unload(int handle)
		{
			Entry& entry = m_Entries[handle];
			entry.Current = State::Unloaded;
			entry.Generation++;
		}

		void StepWorker()
		{
			if (m_Dispatched.empty())
				return;
			const Job job = m_Dispatched.front();
			m_Dispatched.pop_front();
			if (job.Broken && !m_Guards.CatchFailures)
				return; // The exception ended the job: no completion, and its bytes never leave the flight
			m_Completions.push_back(Completion { job, !job.Broken });
		}

		void Update()
		{
			while (!m_Completions.empty())
			{
				const Completion completion = m_Completions.front();
				m_Completions.pop_front();
				m_InFlightBytes -= completion.Source.Megabytes;
				m_InFlightLoads--;
				Entry& entry = m_Entries[completion.Source.Handle];
				if (m_Guards.CheckGeneration && entry.Generation != completion.Source.Generation)
					continue;
				entry.Current = completion.Ok ? State::Ready : State::Failed;
			}
			Pump();
		}

		State GetState(int handle) { return m_Entries[handle].Current; }
		uint64_t GetInFlightBytes() const { return m_InFlightBytes; }
		uint64_t GetPeakBytes() const { return m_PeakBytes; }
		uint32_t GetLoadsStarted() const { return m_LoadsStarted; }

	private:
		bool CanDispatch() const
		{
			return m_Guards.MaxInFlightBytes == 0 || m_InFlightLoads == 0 || m_InFlightBytes < m_Guards.MaxInFlightBytes;
		}

		void Pump()
		{
			while (!m_Waiting.empty() && CanDispatch())
			{
				m_InFlightBytes += m_Waiting.front().Megabytes;
				m_InFlightLoads++;
				m_PeakBytes = std::max(m_PeakBytes, m_InFlightBytes);
				m_Dispatched.push_back(m_Waiting.front());
				m_Waiting.pop_front();
			}
		}

		Guards m_Guards;
		std::map<int, Entry> m_Entries;
		std::deque<Job> m_Waiting;
		std::deque<Job> m_Dispatched;
		std::deque<Completion> m_Completions;
		uint64_t m_InFlightBytes = 0;
		uint64_t m_PeakBytes = 0;
		uint32_t m_InFlightLoads = 0;
		uint32_t m_LoadsStarted = 0;
	};

	void RunScenarios(const char* name, Guards guards)
	{
		std::printf("%s\n", name);

		ToyManager unloaded(guards);
		unloaded.Add(1, 10, false);
		unloaded.GetAsset(1);
		unloaded.Unload(1);
		unloaded.StepWorker();
		unloaded.Update();
		std::printf("  unloaded while loading: %s\n", ToString(unloaded.GetState(1)));

		ToyManager broken(guards);
		broken.Add(2, 10, true);
		broken.GetAsset(2);
		broken.StepWorker();
		broken.Update();
		std::printf("  broken file: %s, %llu MB in flight\n", ToString(broken.GetState(2)), static_cast<unsigned long long>(broken.GetInFlightBytes()));

		ToyManager asked(guards);
		asked.Add(3, 10, false);
		for (int system = 0; system < 3; system++)
			asked.GetAsset(3);
		std::printf("  three systems ask in one frame, loads started: %u\n", asked.GetLoadsStarted());

		ToyManager burst(guards);
		for (int handle = 10; handle < 20; handle++)
		{
			burst.Add(handle, 40, false);
			burst.GetAsset(handle);
		}
		std::printf("  ten 40 MB assets at once: %llu MB in flight at most\n", static_cast<unsigned long long>(burst.GetPeakBytes()));
	}

}

int main()
{
	RunScenarios("naive manager", Guards { false, false, false, 0 });
	RunScenarios("guarded manager", Guards {});
	return 0;
}
