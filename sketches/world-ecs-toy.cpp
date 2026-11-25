// A toy sparse set (emplace, remove by swapping with the last element, contains, iterate) and a view over two of them.
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace
{
	constexpr uint32_t c_Empty = 0xFFFFFFFF;

	template<typename T>
	class SparseSet
	{
	public:
		void Emplace(uint32_t entity, T value)
		{
			if (entity >= m_Sparse.size())
				m_Sparse.resize(entity + 1, c_Empty);
			m_Sparse[entity] = static_cast<uint32_t>(m_Dense.size());
			m_Dense.push_back(entity);
			m_Values.push_back(value);
		}

		void Remove(uint32_t entity)
		{
			const uint32_t hole = m_Sparse[entity];
			const uint32_t last = m_Dense.back();
			m_Dense[hole] = last; // the last element moves into the hole
			m_Values[hole] = m_Values.back();
			m_Sparse[last] = hole;
			m_Sparse[entity] = c_Empty;
			m_Dense.pop_back();
			m_Values.pop_back();
		}

		bool Contains(uint32_t entity) const { return entity < m_Sparse.size() && m_Sparse[entity] != c_Empty; }
		uint32_t PositionOf(uint32_t entity) const { return m_Sparse[entity]; }
		T& Get(uint32_t entity) { return m_Values[m_Sparse[entity]]; }
		const std::vector<uint32_t>& Entities() const { return m_Dense; }
	private:
		std::vector<uint32_t> m_Sparse; // entity -> position in the packed arrays
		std::vector<uint32_t> m_Dense;  // the entities, packed
		std::vector<T> m_Values;        // their values, in the same order
	};

	// Walks the shorter set and asks the other one: the work follows the rarer component.
	template<typename A, typename B, typename Function>
	void ForEachWith(SparseSet<A>& first, SparseSet<B>& second, Function function)
	{
		const auto visit = [&](uint32_t entity)
		{
			if (first.Contains(entity) && second.Contains(entity))
				function(entity, first.Get(entity), second.Get(entity));
		};
		const std::vector<uint32_t>& walked = first.Entities().size() <= second.Entities().size() ? first.Entities() : second.Entities();
		for (uint32_t entity : walked)
			visit(entity);
	}

	void Print(const char* label, const std::vector<uint32_t>& entities)
	{
		std::printf("%s:", label);
		for (uint32_t entity : entities)
			std::printf(" %u", entity);
		std::printf("\n");
	}
}

int main()
{
	SparseSet<std::string> names;
	SparseSet<int> healths;
	const char* spelled[] = { "Ada", "Bo", "Cy", "Di", "Ed" };
	for (uint32_t entity = 0; entity < 5; entity++)
		names.Emplace(entity, spelled[entity]);
	healths.Emplace(1, 10);
	healths.Emplace(3, 30);
	healths.Emplace(4, 40);

	Print("names, packed", names.Entities());
	std::printf("entity 4 sits at position %u\n", names.PositionOf(4));
	names.Remove(1);
	Print("names after removing entity 1", names.Entities());
	std::printf("entity 4 sits at position %u, entity 1 has a name: %s\n", names.PositionOf(4), names.Contains(1) ? "yes" : "no");

	ForEachWith(names, healths, [](uint32_t entity, const std::string& name, int health)
	{
		std::printf("view: entity %u is %s with %d health\n", entity, name.c_str(), health);
	});
	return 0;
}
