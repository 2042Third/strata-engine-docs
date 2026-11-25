# Part review: `animation/blending`

- wrong: "`Advance` adds the time of each update, times the animator's speed setting, to the fade's clock": the clock adds the absolute value (`AnimatorInstance.cpp:702`, `m_FadeElapsed += std::abs(scaled)`), so a backward speed still advances a fade; now "times the animator's speed without its sign".
