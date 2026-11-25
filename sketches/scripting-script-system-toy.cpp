// A toy script system: instances, a deferred destroy and a sync point at both ends of the update.
#include <cstdio>
#include <memory>
#include <string>
#include <vector>

struct Instance
{
	std::string Name;
	std::string Target; // Another instance this one asks to destroy in its first update
	bool Spawns = false;
	bool Created = false;
	bool Removed = false;
};

class ToySystem
{
public:
	void Add(const std::string& name, const std::string& target, bool spawns)
	{
		auto instance = std::make_shared<Instance>();
		instance->Name = name;
		instance->Target = target;
		instance->Spawns = spawns;
		m_Order.push_back(instance);
		m_PendingStart.push_back(instance);
	}

	void Frame(int number)
	{
		std::printf("frame %d\n", number);
		SyncPoint();
		// The count is taken once: instances added during the walk wait for the next frame.
		const size_t count = m_Order.size();
		for (size_t index = 0; index < count; index++)
		{
			Instance& instance = *m_Order[index];
			if (instance.Removed)
				continue;
			std::printf("  update %s\n", instance.Name.c_str());
			if (!instance.Target.empty())
				m_Deferred.push_back(instance.Target);
			instance.Target.clear();
			if (instance.Spawns)
				Add("D", "", false);
			instance.Spawns = false;
		}
		SyncPoint();
	}

private:
	void SyncPoint()
	{
		// Copies: the callbacks may ask for more destroys and creations.
		const std::vector<std::string> destroys = std::move(m_Deferred);
		m_Deferred.clear();
		for (const std::string& name : destroys)
		{
			for (const std::shared_ptr<Instance>& instance : m_Order)
			{
				if (instance->Name == name && !instance->Removed)
				{
					instance->Removed = true;
					std::printf("  destroy %s\n", name.c_str());
				}
			}
		}
		const std::vector<std::shared_ptr<Instance>> starts = std::move(m_PendingStart);
		m_PendingStart.clear();
		for (const std::shared_ptr<Instance>& instance : starts)
		{
			instance->Created = true;
			std::printf("  create %s\n", instance->Name.c_str());
		}
	}

	std::vector<std::shared_ptr<Instance>> m_Order;
	std::vector<std::shared_ptr<Instance>> m_PendingStart;
	std::vector<std::string> m_Deferred;
};

int main()
{
	ToySystem system;
	system.Add("A", "B", false);
	system.Add("B", "B", false);
	system.Add("C", "", true);
	system.Frame(1);
	system.Frame(2);
	return 0;
}
