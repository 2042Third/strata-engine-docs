# Part review: appendix/networking (group 1 of 1)

- wrong: "the project fixes the rate" of fixed steps; the project's `Scene.Timing` `FixedRate` defaults to `Scene` (each scene's own step) and only can override it (`Strata/src/Strata/Scene/ProjectSceneTiming.h`), so the page now says the project can fix the rate for every scene.
