// A pretend engine file: the runtime's perf log group (tools/tests/test_reference.py).
namespace Strata
{

	FramePerfColumnGroup GameRuntime::MakePerfLogColumns() const
	{
		FramePerfColumnGroup group;
		group.Names = { "WorldCellsLoaded", "PhysicsBodies" };
		return group;
	}

}
