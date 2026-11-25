#pragma once
// A pretend engine file in the shape of the perf log's header comment (tools/tests/test_reference.py).

namespace Strata
{

	// A CSV file with one row per frame. The header names the columns:
	//   Frame, WorkMs                            the frame (its index and work time)
	//   <stage>...                               each registered stage, in milliseconds
	//   LoadingAssets, QueuedLoads,
	//   InFlightLoads                            the asset manager after the frame;
	//                                            empty without one
	//   <group columns>...                       the columns of the groups
	// A row describes one frame.
	class FramePerfLog
	{
	};

}
