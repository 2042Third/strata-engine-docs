# Part review of `audio/scene-system`

No correction: the registration and soft order, the component ranges and defaults, the five `AssetManager::GetActive()` calls, `OnRuntimeStart`, `OnRuntimeStarted`, `OnRuntimeStop` resetting the listener, the gameplay calls (`IsPlaying` true while waiting or held by the pause), the one-shot cap 64 and wait 0.25 s, the drop warnings once per clip per second, the ten host functions, `IAudioOutput` in `SceneServices.h`, the `Impact` example, the test names and every callout line number hold at the pin (319075e3).
