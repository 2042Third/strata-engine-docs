#include <cstdint>
#include <cstdio>
#include <vector>

namespace Toy
{

	constexpr uint32_t c_Invalid = ~0u;
	constexpr size_t c_MaxChanges = 8;

	struct Change
	{
		uint64_t Version;
		uint32_t Proxy;
	};

	// Keeps its own copy of one field per entity, in a dense array indexed by proxy.
	class ProxyStore
	{
	public:
		void MarkDirty(uint32_t entity)
		{
			if (entity >= m_Queued.size())
				m_Queued.resize(entity + 1, false);
			if (m_Queued[entity])
				return;
			m_Queued[entity] = true;
			m_Pending.push_back(entity);
		}

		uint32_t Sync(const std::vector<float>& scene)
		{
			uint32_t updates = 0;
			for (const uint32_t entity : m_Pending)
			{
				m_Queued[entity] = false;
				uint32_t proxy = FindProxy(entity);
				if (proxy == c_Invalid)
					proxy = CreateProxy(entity);
				else if (m_Positions[proxy] == scene[entity])
					continue;
				m_Positions[proxy] = scene[entity];
				RecordChange(proxy);
				updates++;
			}
			m_Pending.clear();
			return updates;
		}

		void Destroy(uint32_t entity)
		{
			const uint32_t proxy = FindProxy(entity);
			m_ByEntity[entity] = c_Invalid;
			m_Entities[proxy] = c_Invalid;
			m_FreeProxies.push_back(proxy);
			RecordChange(proxy);
		}

		uint32_t FindProxy(uint32_t entity) const { return entity < m_ByEntity.size() ? m_ByEntity[entity] : c_Invalid; }
		uint64_t GetVersion() const { return m_Version; }

		bool GetChanges(uint64_t since, std::vector<uint32_t>& out) const
		{
			if (since < m_Floor)
				return false;
			for (const Change& change : m_Changes)
			{
				if (change.Version > since)
					out.push_back(change.Proxy);
			}
			return true;
		}
	private:
		uint32_t CreateProxy(uint32_t entity)
		{
			uint32_t proxy = static_cast<uint32_t>(m_Entities.size());
			if (!m_FreeProxies.empty())
			{
				proxy = m_FreeProxies.back();
				m_FreeProxies.pop_back();
			}
			else
			{
				m_Entities.push_back(c_Invalid);
				m_Positions.push_back(0.0f);
			}
			m_Entities[proxy] = entity;
			if (entity >= m_ByEntity.size())
				m_ByEntity.resize(entity + 1, c_Invalid);
			m_ByEntity[entity] = proxy;
			return proxy;
		}

		void RecordChange(uint32_t proxy)
		{
			m_Changes.push_back(Change { ++m_Version, proxy });
			if (m_Changes.size() > c_MaxChanges)
			{
				m_Floor = m_Changes.front().Version;
				m_Changes.erase(m_Changes.begin());
			}
		}

		std::vector<uint32_t> m_Entities;
		std::vector<float> m_Positions;
		std::vector<uint32_t> m_FreeProxies;
		std::vector<uint32_t> m_ByEntity;
		std::vector<bool> m_Queued;
		std::vector<uint32_t> m_Pending;
		std::vector<Change> m_Changes;
		uint64_t m_Version = 0;
		uint64_t m_Floor = 0;
	};

}

int main()
{
	std::vector<float> scene = { 0.0f, 2.0f, 4.0f, 6.0f, 8.0f, 10.0f };
	Toy::ProxyStore store;
	for (uint32_t entity = 0; entity < 5; entity++)
		store.MarkDirty(entity);
	std::printf("first sync: %u updates\n", store.Sync(scene));
	std::printf("still sync: %u updates\n", store.Sync(scene));

	const uint64_t seen = store.GetVersion();
	scene[3] += 1.0f;
	store.MarkDirty(3);
	store.MarkDirty(3);
	std::vector<uint32_t> changed;
	std::printf("one move, signaled twice: %u update\n", store.Sync(scene));
	const bool followed = store.GetChanges(seen, changed);
	std::printf("reader at version %llu: followed %d, changed %zu, proxy %u\n", static_cast<unsigned long long>(seen), followed, changed.size(), changed[0]);

	store.Destroy(1);
	store.MarkDirty(5);
	store.Sync(scene);
	std::printf("entity 5 took the proxy of entity 1: proxy %u\n", store.FindProxy(5));

	for (int move = 0; move < 8; move++)
	{
		scene[0] += 1.0f;
		store.MarkDirty(0);
		store.Sync(scene);
	}
	changed.clear();
	std::printf("version %llu: the reader at %llu %s\n", static_cast<unsigned long long>(store.GetVersion()), static_cast<unsigned long long>(seen),
		store.GetChanges(seen, changed) ? "follows the log" : "must read everything");
}
