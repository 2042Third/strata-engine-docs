// A toy playhead: it loops, counts the loops and collects the events it passes, forwards and backwards.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

struct ToyEvent
{
	const char* Name = "";
	float Time = 0.0f;
};

struct ToyPlayhead
{
	float Duration = 1.0f;
	float Time = 0.0f;
	int64_t Loops = 0;
	bool Fresh = true; // nothing has played yet, so an event at time 0 is still to fire

	double GetNormalized() const { return static_cast<double>(Loops) + static_cast<double>(Time) / static_cast<double>(Duration); }
};

// Events in (from, to] going forwards and in [to, from) going backwards; includeFrom also takes an event at from.
static void Collect(const std::vector<ToyEvent>& events, float from, float to, bool includeFrom, std::vector<ToyEvent>& out)
{
	if (to >= from)
	{
		for (const ToyEvent& event : events)
			if ((event.Time > from || (includeFrom && event.Time == from)) && event.Time <= to)
				out.push_back(event);
	}
	else
	{
		for (size_t index = events.size(); index > 0; index--)
			if ((events[index - 1].Time < from || (includeFrom && events[index - 1].Time == from)) && events[index - 1].Time >= to)
				out.push_back(events[index - 1]);
	}
}

// One update: walk the playhead to the loop boundary, count the crossing, continue with what is left.
static void Advance(ToyPlayhead& playhead, float seconds, const std::vector<ToyEvent>& events, std::vector<ToyEvent>& out)
{
	float remaining = seconds;
	float position = playhead.Time;
	bool includeFrom = playhead.Fresh;
	while (remaining != 0.0f)
	{
		const float step = remaining > 0.0f ? std::min(remaining, playhead.Duration - position) : std::max(remaining, -position);
		Collect(events, position, position + step, includeFrom, out);
		position += step;
		remaining -= step;
		includeFrom = false;
		if (remaining > 0.0f || position >= playhead.Duration)
		{
			position = 0.0f;
			playhead.Loops++;
			includeFrom = true;
		}
		else if (remaining < 0.0f)
		{
			position = playhead.Duration;
			playhead.Loops--;
			includeFrom = true;
		}
	}
	playhead.Time = position;
	playhead.Fresh = false;
}

int main()
{
	const std::vector<ToyEvent> events = { { "StepLeft", 0.25f }, { "StepRight", 0.75f } };
	ToyPlayhead playhead;
	const float updates[] = { 0.875f, 0.5f, 2.0f, -1.75f };
	for (const float seconds : updates)
	{
		std::vector<ToyEvent> fired;
		Advance(playhead, seconds, events, fired);
		std::printf("advance %6.3f: time %.3f loops %lld normalized %.3f events:", seconds, playhead.Time, static_cast<long long>(playhead.Loops), playhead.GetNormalized());
		for (const ToyEvent& event : fired)
			std::printf(" %s", event.Name);
		std::printf("\n");
	}
	return 0;
}
