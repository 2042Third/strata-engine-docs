# Part review of `engineering/releasing`

- contradiction: "Everyday CI tests Release" against `engineering/ci`'s Windows (Debug) job; now "Release, and Debug on Windows".
- step: Exercise 3 pushed `v0.7.0-rc1` and expected `Strata Editor 0.7.0`; at the pin `project(Strata VERSION 0.8.0)` refuses that tag, so the example is `v0.8.0-rc1` and `Strata Editor 0.8.0`.
