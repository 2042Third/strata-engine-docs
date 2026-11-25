// A pretend engine file: the frame profiler's built-in stages (tools/tests/test_reference.py).
#pragma once

namespace Strata
{
	inline constexpr std::array<BuiltinFrameStage, 3> c_BuiltinFrameStages = { {
		{ "Input", true },          // The window's events
		{ "Render.Extract", true }, // Gathering the draws
		{ "Present", false }        // After the work time
	} };
}
