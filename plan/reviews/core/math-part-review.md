# Part review of `core/math`

- wrong: "How it is tested" said `Scene.Timing.Sweep` and `Scene.Transforms.Sweep` both compare matrices bit for bit; at the pin the timing sweep compares bit for bit, while the transforms sweep compares each cached matrix with a recomputation within the relative tolerance 1.0e-5 (`StrataTests/src/Scene/SceneTransformTests.cpp`, `c_TransformValidationTolerance`), and the paragraph now says so.
- wrong: Check-yourself answer 5 said the scene compares cached against recomputed matrices exactly, and physics against the cache; it now names the bit-for-bit check (interpolated against not) and the tight tolerance of the cache check, as the pin's tests do.
- unclear: "What went wrong before" now adds that the one-ulp difference lay a little above the check's tolerance (commit 4de73aa4), so the history agrees with the corrected test paragraph.
- unclear: the projections section bolded **infinite far plane**, a term homed on `gpu/coordinates`, outside the closure; the bold is removed (the sentence still says what it is and links the home).
