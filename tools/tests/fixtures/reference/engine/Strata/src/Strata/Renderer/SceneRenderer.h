#pragma once
// A pretend engine file in the shape of the scene renderer's structs (tools/tests/test_reference.py).

namespace Strata
{

	struct SceneRendererSpecification
	{
		std::string DebugName = "SceneRenderer";
		// Point and spot lights rendered per frame.
		uint32_t MaxLights = 4096;
		glm::uvec3 LightClusterGrid = { 16, 9, 24 };
		bool EntityIDs = true; // Picking reads them
		void Validate() const;
	};

	struct SceneRendererStats
	{
		uint32_t DrawCalls = 0; // Draw calls of the frame
		uint32_t CascadeCount = 0;
		struct Cascade
		{
			float Near = 0.0f;
		};
		std::array<Cascade, 4> Cascades = {};
	};

}
