# Part review of `audio/spatial`

No correction: the attenuation formulas (`AudioSource.h:18-23`), `SetAttenuation` and `c_MinAttenuationDistance` 0.01, miniaudio's speed of sound 343.3 and Doppler factor 1, `c_MaxDopplerSpeed` 150, the smoothing time 0.1, two still fixed steps, `GetBodyVelocity` through `GetSimulatingBody` and `GetPointVelocity`, the component without an attenuation field (default `Inverse`), the test names and the callout line numbers hold at the pin (319075e3) and agree with the part's other pages.
