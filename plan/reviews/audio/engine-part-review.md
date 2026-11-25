# Part review of `audio/engine`

- wrong: "The test of `Master volume scales the mix` ... a negative or `NaN` volume gives 0": `SetMasterVolume` ignores a non-finite value (`AudioEngine.cpp:276-280`), so the test's `NaN` leaves the 0 the negative value set; now says the `NaN` is ignored and the volume stays 0, as the page's own section on master volume says.
- wrong: `ApplyPendingWorldUp` "is the only place that writes the up vector into the mixer": `ApplyListener` writes it at `Init`, before the engine mixes (`AudioEngine.cpp:73-81`); now "Once the engine mixes, it is the only place".

Checked and holding: the `Impact` example (1.5, 10, 0.45, 0.99), the soft order, the sample-rate range, the device fallback, `InitializeEngine`, `AdvanceNullDevice` and its chunks, the headless frame rate 60, the minimized-window skip (`Application.cpp:311-316`), `OnShutdown` after `JobSystem::Shutdown` (`Application.cpp:171-175`), `MaxOneShots` 128, the up-vector test and the null-device test, the callout line numbers of every quote.
