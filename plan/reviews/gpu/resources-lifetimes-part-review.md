# Part review: gpu/resources-lifetimes (group 1 of 2)

- wrong: "The last line of the function, line 2340, is Renderer::ReleaseDeferred(std::move(released))"; at the pin ReleaseRenderTargets ends with that call on line 2400 of SceneRenderer.cpp; now 2400.
- wrong: Exercise 3's answer gave the same call as line 2340; now 2400.
