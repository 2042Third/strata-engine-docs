// A server steps a ball 60 times a second and sends its position every third tick. One snapshot is lost.
// The client draws the ball c_DelayTicks behind the newest tick, between the two snapshots around that time.
#include <cstdio>
#include <vector>

namespace
{
	constexpr int c_SnapshotEvery = 3; // ticks between two snapshots: one snapshot interval
	constexpr int c_LostTick = 30;     // the snapshot taken at this tick never arrives
	constexpr int c_DelayTicks = 3;    // how far behind the newest tick the client draws

	struct Snapshot
	{
		int Tick = 0;
		double X = 0.0;
	};

	// The server's ball moves at 4 m/s and is pushed to 8 m/s at tick 30 (0.5 s).
	double ServerPosition(int tick)
	{
		const double seconds = tick / 60.0;
		return seconds <= 0.5 ? 4.0 * seconds : 2.0 + 8.0 * (seconds - 0.5);
	}
}

int main()
{
	std::vector<Snapshot> received;
	std::printf("now drawn  shown  true  error (m)\n");
	for (int now = 0; now <= 45; now++)
	{
		if (now % c_SnapshotEvery == 0 && now != c_LostTick)
			received.push_back({ now, ServerPosition(now) });
		if (now < 24)
			continue;

		const int drawnTick = now - c_DelayTicks;
		const Snapshot* before = nullptr;
		const Snapshot* after = nullptr;
		for (const Snapshot& snapshot : received)
		{
			if (snapshot.Tick <= drawnTick)
				before = &snapshot;
			if (snapshot.Tick >= drawnTick && !after)
				after = &snapshot;
		}

		// With no newer snapshot, the ball waits where the last one put it.
		double shown = before->X;
		if (after && after->Tick != before->Tick)
			shown += (after->X - before->X) * (drawnTick - before->Tick) / (after->Tick - before->Tick);
		const double truth = ServerPosition(drawnTick);
		std::printf("%3d %5d %7.3f %6.3f %6.3f\n", now, drawnTick, shown, truth, shown - truth);
	}
	return 0;
}
