# Part review: image/motion-blur

No correction.

Checked without change: the component's defaults (off, 180, 0.02) and clamps, `GetBlurVelocity`, the length formula and its examples, the 1-pixel floor at 1080 rows and the half-pixel keep, the tile size (11 at 1080), the 64-thread tile pass, the neighbor pass's diagonal rule and spread, the gather's even and odd directions (1.5 pixels), `c_DepthTolerance` 0.05, the half-pixel minimum radius, the CPU model, `motionBlurWanted`, the cut and history conditions, the sample counts 8, 12 and 16, `options.MotionBlur` in ViewportRenderer.cpp, the blur mask in the tone mapping, the look-dev shots `tp.live.turn.mb180` and `.mb90`, and the tests of both suites.
