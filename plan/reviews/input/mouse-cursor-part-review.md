# Part review of `input/mouse-cursor`

No corrections: the viewport scale and its fallbacks, the only `SetViewport` caller (GameViewPanel.cpp:279), the cursor modes and raw motion (GLFWWindow.cpp), `SetGameCursorMode` and `SetEnabled`, `ResetGameShell` setting the game's cursor to Normal at play start and stop, the follow camera's 0.12 degrees per pixel and 0.75 m per notch and its signs, the pause menu's calls, `HostSetCursorMode` and the static_assert in ScriptHostAPI.cpp, and the three test names hold at the pin; no contradiction with the other pages of the part.
