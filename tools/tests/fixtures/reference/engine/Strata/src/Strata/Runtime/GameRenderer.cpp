// A pretend engine file: the game renderer's perf log group (tools/tests/test_reference.py).
namespace Strata
{

	FramePerfColumnGroup GameRenderer::MakePerfLogColumns(const GameRenderer* renderer)
	{
		FramePerfColumnGroup group;
		group.Names = { "DrawCalls" };
		return group;
	}

}
