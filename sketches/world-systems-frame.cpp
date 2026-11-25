// A toy scene: systems called in three phases, fixed steps from an accumulator, and a cap that drops the backlog.
#include <cstdio>
#include <vector>

namespace
{
	// Whole milliseconds keep the numbers exact; Strata's scene uses floats of seconds.
	constexpr int c_StepMs = 10;
	constexpr int c_MaxSteps = 8;

	class System
	{
	public:
		virtual ~System() = default;
		virtual void OnUpdate(int) {}
		virtual void OnFixedUpdate(int) {}
		virtual void OnLateUpdate(int) {}
	};

	class Counter : public System
	{
	public:
		void OnUpdate(int) override { Updates++; }
		void OnFixedUpdate(int) override { FixedUpdates++; }
		void OnLateUpdate(int) override { LateUpdates++; }

		int Updates = 0;
		int FixedUpdates = 0;
		int LateUpdates = 0;
	};

	class Scene
	{
	public:
		void AddSystem(System& system) { m_Systems.push_back(&system); }

		void Update(int frameMs)
		{
			for (System* system : m_Systems)
				system->OnUpdate(frameMs);

			m_AccumulatorMs += frameMs;
			int steps = 0;
			while (m_AccumulatorMs >= c_StepMs && steps < c_MaxSteps)
			{
				for (System* system : m_Systems)
					system->OnFixedUpdate(c_StepMs);
				m_AccumulatorMs -= c_StepMs;
				steps++;
			}
			int dropped = 0;
			if (steps == c_MaxSteps && m_AccumulatorMs > c_StepMs)
			{
				dropped = (m_AccumulatorMs - c_StepMs) / c_StepMs;
				m_AccumulatorMs = c_StepMs;
			}

			for (System* system : m_Systems)
				system->OnLateUpdate(frameMs);
			std::printf("frame of %5d ms: %d steps, %d dropped, %d ms carried\n", frameMs, steps, dropped, m_AccumulatorMs);
		}
	private:
		std::vector<System*> m_Systems;
		int m_AccumulatorMs = 0;
	};
}

int main()
{
	Scene scene;
	Counter counter;
	scene.AddSystem(counter);
	for (int frameMs : { 35, 6, 10000 })
		scene.Update(frameMs);
	std::printf("calls: %d update, %d fixed, %d late\n", counter.Updates, counter.FixedUpdates, counter.LateUpdates);
	return 0;
}
