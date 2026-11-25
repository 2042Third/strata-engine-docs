// A pretend engine file: GPU stages (tools/tests/test_reference.py).
namespace Strata
{

	namespace
	{

		FrameStageID RegisterGPUStage(std::string_view name)
		{
			return FrameProfiler::Get().RegisterStage(name, false, FrameStageKind::GPU);
		}

	}

	const RendererGPUStages& RendererGPUStages::Get()
	{
		static const RendererGPUStages s_Stages = []()
		{
			RendererGPUStages stages;
			stages.Shadows = RegisterGPUStage("GPU.Shadows");
			stages.Opaque = RegisterGPUStage("GPU.Opaque");
			return stages;
		}();
		return s_Stages;
	}

}
