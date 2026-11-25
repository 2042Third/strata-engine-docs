# Part review: `indirect/ibl`

- wrong: the atmosphere's 14 refresh steps were counted as six faces, "one step for the cube's levels and the irradiance" and six prefiltered levels (13); at the pin the levels and the irradiance are two steps (`c_AtmosphereRefreshSteps = 6 + 2 + 6`), now said so.
- wrong: "Test the horizon fade by hand, since no capture switch disables it" contradicted the page's own `GetFrameHorizonFade` callout and the pin, where a capture's renderer switch `HorizonFade` (`StrataEditor/src/Editor/ViewportRenderer.cpp`) turns the fade off; the sentence now names that switch.
