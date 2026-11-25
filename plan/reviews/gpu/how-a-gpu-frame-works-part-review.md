# Part review: gpu/how-a-gpu-frame-works (group 1 of 2)

No corrections: the present-mode choice and image count (VulkanGraphicsDevice.cpp:1155-1167), the pacing loop at the start of BeginFrame (1444-1452), the event query set at the end of EndFrame after the present, MaxFramesInFlight 2 (GraphicsDevice.h:28), WindowSpecification::VSync true (Window.h:63) and the Vulkan 1.2 floor (c_MinimumVulkanVersion) hold at the pin; no contradiction with the digest.
