#pragma once
// A pretend engine file in the shape of the scene's limits (tools/tests/test_reference.py).

namespace Strata
{

	struct SceneSettings
	{
		static constexpr uint32_t c_MaxBodiesLimit = 1u << 21;
		static constexpr double c_Seconds = 2.0;
	};

	class Scene
	{
	public:
		// A registry holds at most this many live entities.
		static constexpr size_t c_MaxEntities = static_cast<size_t>(entt::entt_traits<entt::entity>::entity_mask);
		static constexpr size_t c_MaxMoves = 4'096;
		static constexpr double c_Budget = c_Seconds * 1000.0;
	};

}
