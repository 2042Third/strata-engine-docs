// A pretend engine file in the shape of renderStats (tools/tests/test_reference.py).
namespace Strata
{

	namespace
	{

		nlohmann::json DescribeGeometryPool()
		{
			return { { "usedMB", 1.0 }, { "moves", 0 } };
		}

		nlohmann::json DescribeRenderStats(const SceneRendererStats& stats, const SceneRendererGPUStats& gpu)
		{
			nlohmann::json cascades = nlohmann::json::array();
			for (uint32_t cascade = 0; cascade < stats.CascadeCount; cascade++)
				cascades.push_back({ { "near", stats.Cascades[cascade].Near }, { "far", stats.Cascades[cascade].Far } });
			return {
				// What the frame drew with.
				{ "quality", RendererQuality::ToSectionValue(stats.Quality) },
				{ "cascades", std::move(cascades) },
				{ "draws", stats.DrawCalls },
				{ "geometryPool", DescribeGeometryPool() },
				{ "exposure", stats.Exposure ? nlohmann::json { { "ev100", *stats.Exposure + 3.0f } } : nlohmann::json(nullptr) } };
		}

	}

}
