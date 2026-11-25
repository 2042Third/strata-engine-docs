// A toy animation system on one thread: records, a step per record, an ordered publish, then event dispatch.
#include <algorithm>
#include <cstdio>
#include <functional>
#include <utility>
#include <vector>

struct Clip
{
	float Duration;
	float EventTime;
	float Travel;
};

struct Record
{
	int Entity = 0;
	const Clip* Source = nullptr;
	bool Removed = false;
	float Time = 0.0f;
	float Pose = 0.0f;
	float RootMove = 0.0f;
	bool EventFired = false;
	int PoseVersion = 0;
};

struct Event
{
	int Entity;
	float Time;
};

class ToySystem
{
public:
	std::vector<float> Positions = std::vector<float>(2, 0.0f);
	std::vector<std::function<void(const Event&)>> Listeners;

	void Add(int entity, const Clip* clip)
	{
		Record record;
		record.Entity = entity;
		record.Source = clip;
		m_Records.push_back(record);
	}

	void Remove(int entity)
	{
		for (Record& record : m_Records)
			record.Removed = record.Removed || record.Entity == entity;
	}

	void Update(float deltaTime)
	{
		std::erase_if(m_Records, [](const Record& record) { return record.Removed; }); // Keeps the order of the rest.
		for (Record& record : m_Records)
			Step(record, deltaTime);
		for (Record& record : m_Records) // Publish in record order.
		{
			record.PoseVersion++;
			if (record.EventFired)
				m_Pending.push_back({ record.Entity, record.Time });
			Positions[record.Entity] += record.RootMove; // Root motion last.
			std::printf("  entity %d: pose %.2f, position %.2f\n", record.Entity, record.Pose, Positions[record.Entity]);
		}
		const std::vector<Event> events = std::move(m_Pending);
		m_Pending.clear();
		const auto listeners = Listeners; // A snapshot: a listener may change the list.
		for (const Event& event : events)
			for (const auto& listener : listeners)
				listener(event);
	}

private:
	void Step(Record& record, float deltaTime) const
	{
		const Clip& clip = *record.Source;
		const float before = record.Time;
		record.Time = std::min(before + deltaTime, clip.Duration);
		record.EventFired = before < clip.EventTime && record.Time >= clip.EventTime;
		record.Pose = 90.0f * record.Time / clip.Duration;
		record.RootMove = clip.Travel * (record.Time - before) / clip.Duration;
	}

	std::vector<Record> m_Records;
	std::vector<Event> m_Pending;
};

int main()
{
	const Clip wave { 1.0f, 0.5f, 2.0f };
	const Clip swing { 2.0f, 0.5f, 4.0f };
	ToySystem system;
	system.Add(0, &wave);
	system.Add(1, &swing);
	system.Listeners.push_back([](const Event& event) { std::printf("  event: entity %d at %.2f\n", event.Entity, event.Time); });
	for (int update = 1; update <= 3; update++)
	{
		std::printf("update %d\n", update);
		if (update == 3)
			system.Remove(0);
		system.Update(0.25f);
	}
	return 0;
}
