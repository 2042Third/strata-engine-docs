# Part review: `animation/clips`

No corrections. Checked at the pin: the limits (`c_MaxChannels` 3 x 65535, 2^24 keys, 2^26 values), the 20-byte channel record and the header, the reduction's tolerances, window and cancel interval and its skip of cubic channels, every callout's line against `AnimationClip.cpp` and `AnimationTypes.h`, the loader's later checks (targets, ranges, times, duplicates, duration), the two binding sites in `AnimationSystem.cpp` (`:485`, `:529`), the tests' descriptions, the roadmap's "compressed clips if measured to help", and the worked numbers.
