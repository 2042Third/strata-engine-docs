// A pretend engine file: a GPU stage and a CPU stage registered directly (tools/tests/test_reference.py).
namespace Strata
{

	void GameUIRenderer::Render()
	{
		static const FrameStageID s_Stage = FrameProfiler::Get().RegisterStage("GPU.UI", false, FrameStageKind::GPU);
		FrameProfiler::Get().RegisterStage("Render.UI");
	}

}
