---
id: gpu/vulkan-nvrhi
title: "Vulkan, NVRHI, the graphics device and the Renderer's services"
description: "How Strata opens a GPU through NVRHI and Vulkan, keeps it busy frame after frame, and gives every renderer the same shared services."
kind: internals
size: XL
tracks: [E]
needs: [basics/cpp-classes, basics/numbers, gpu/how-a-gpu-frame-works, core/layers-registries, core/platform]
time: 140
learn:
  - id: device-map
    text: name the objects between the application and the driver, and say which folders may include Vulkan headers
  - id: pick-gpu
    text: compute the score of each GPU of a machine, and predict which one Strata selects and why another is skipped
  - id: device-frame
    text: trace one frame through the device's begin, acquire, back-buffer and present steps, and say where each wait happens
  - id: write-desc
    text: write the NVRHI description of a render target, an upload staging buffer and a readback buffer
  - id: renderer-services
    text: name what the Renderer creates at its start, in which order it releases it, and what its frame begin does
since: 0.3.0
status: final
---

When a Strata program starts, it must open a :term[graphics processing unit]{id=gpu} (GPU) and keep it busy for as long as the program runs. It also gives every part of the :term[renderer]{id=renderer} the same tools: a device, samplers, and plain textures to use while real ones load. This page teaches the code that does this: the graphics device, the module that runs it, and the `Renderer` that holds the shared services. It does not teach how to enable validation or read its messages, how uploads are scheduled, how resources are released, or how textures are bound to :term[shaders]{id=shader}. Links to those pages stand where they belong.

## The problem and how engines solve it

Every GPU maker ships a driver, and the driver speaks one or more graphics application programming interfaces (APIs). Windows programs often use Direct3D, Apple machines use Metal, and Linux and Windows drivers also offer Vulkan. An engine for three :term[operating systems]{id=operating-system} must decide how its renderer talks to all of them. The renderer is the biggest user of the GPU, so the choice shapes every rendering feature that follows.

There are three common answers. The first is one backend per API: the renderer calls an engine interface, and the engine writes one class that implements it for each API. This fits each platform best, but every feature is written, tested and fixed two or three times. The second is a third-party library called a render hardware interface (**RHI**), which offers one set of calls and implements them on each API. The third is one API everywhere, with a translation layer where a platform lacks it: the engine writes only Vulkan, and on macOS a layer turns Vulkan calls into Metal calls.

Strata combines the second and third answers. **Vulkan** is a :term[graphics API]{id=graphics-api} from an open standards group. In it the program, not the driver, does the tracking: it names every queue and announces the state of every resource. The driver adds no checks at run time.

**NVRHI** is a render hardware interface (RHI) from NVIDIA that wraps that tracking behind a smaller set of calls. It records the barriers between uses of a resource from the states you tell it about. Strata uses NVRHI on Vulkan only, and `Platform/Vulkan` is the one folder of the renderer that includes Vulkan :term[headers]{id=header}.

On macOS no driver speaks Vulkan, so **MoltenVK** translates Vulkan calls to Metal. The person installs it as a library, and Strata treats it as a Vulkan driver with limits. Its limits are the reason for a rule that comes back later: renderer code gates on what the device can do, never on the operating system.

:::why[One backend through a library]
A renderer with one backend has one set of bugs, and one set of GPU tests covers all platforms. NVRHI already carries the work of tracking resource states, which is the hardest part of Vulkan to write correctly. The cost is real. A Windows machine whose driver lacks Vulkan 1.2 cannot run Strata, because no Direct3D path exists, and macOS pays for a translation layer with tight limits. A feature that NVRHI cannot express needs a change in the library or a call below it.
:::

:::caution
NVRHI does not make Vulkan safe. It reduces the code you write. A resource used in a state you did not announce is still a mistake, and so is a descriptor written while the GPU reads it, and the library may not catch either. NVRHI has its own validation layer for such mistakes, and Strata enables it together with the Vulkan one in Debug builds.
:::

## The map: who owns what

The program talks to the GPU through a chain of owners. The `Application` runs the `GraphicsModule`, which owns the `GraphicsDevice` and starts the `Renderer`. `VulkanGraphicsDevice` is the only implementation of the `GraphicsDevice` interface. It owns the NVRHI device, which calls Vulkan, which reaches the driver or MoltenVK. The window system gives the device one more thing, a way to present: `Platform/GLFW` implements `VulkanPresentation`.

```mermaid caption="The chain from the program to the driver: each box owns or calls the next, the shared services stand beside the device, and the window system gives the device a way to present." alt="A diagram of boxes joined by arrows. The application runs the graphics module. The module owns the graphics device and starts the service hub, which also uses the device. The Vulkan device owns an NVRHI device, which calls Vulkan, which reaches the driver, or MoltenVK on macOS. The window backend gives the Vulkan device its presentation seam."
flowchart TD
	App["Application"] --> GM["GraphicsModule (engine module)"]
	GM --> GD["GraphicsDevice (interface)"]
	GD --> VGD["VulkanGraphicsDevice"]
	VGD --> NV["NVRHI"]
	NV --> VK["Vulkan"]
	VK --> DR["Driver, or MoltenVK on macOS"]
	GM --> RN["Renderer (service hub)"]
	RN --> GD
	GL["Platform/GLFW: VulkanPresentation"] --> VGD
```

All of it runs on the :term[main thread]{id=main-thread}: the main thread owns rendering submission, and background work never touches the device. The :term[layer table]{id=layer-table} places `Renderer/**` and `Platform/Vulkan/**` in the Renderer layer, with two exceptions. `VulkanLoader` and `VulkanPresentation` belong to the App layer, because the window system implements them and they depend only on Core. The [layer table](../core/layers-registries.md) lists the rest, and `ExternalOwners` keeps GLFW and Vulkan headers in their `Platform/` folders.

## The contract: what callers may assume

The `GraphicsDevice` interface in `Strata/src/Strata/Renderer/GraphicsDevice.h` is what the rest of the engine sees. It has no Vulkan type in any signature, only NVRHI types and plain numbers, so no file outside `Platform/Vulkan` needs a Vulkan header. The interface carries these rules, each with its reason.

- **`GraphicsDevice::Create` returns null after logging why.** A missing driver or a GPU that falls short of the requirements is a normal event on a person's machine. The caller turns it into a message for the person instead of crashing.
- **`BeginFrame` returns false when nothing may render, and `EndFrame` must not follow.** A minimized window or a lost device has no image to draw into, so the whole frame is skipped.
- **`PrepareBackBuffer` runs before the first command list that uses the back buffer.** The GPU waits for the display from that point on, so earlier work such as uploads never queues behind the display. The [upload queue page](../gpu/upload-queue.md) explains why uploads come first.
- **`GetErrorCount` counts every validation error and every NVRHI error.** Tests require it to stay zero.
- **`IsDeviceLost` stays true once set.** After a driver reset or a removed GPU, nothing renders.
- **The main thread makes every call.** Nothing in the interface is made for two threads.

A `GraphicsDeviceSpecification` makes the device. It holds the application name, whether to enable validation and whether the device is headless (no presentation). It also holds the window to present into, the :term[frames in flight]{id=frames-in-flight} and an adapter index. `MaxFramesInFlight` defaults to 2, and the device clamps it to the range 1 to 4.

The `GraphicsDeviceInfo` that the device fills at its start holds what it found. That is the adapter's name and memory, support for block compression, timestamps and indirect draws, the largest 2D texture and the size of the bindless table.

:::rule[Layers]
No Vulkan header appears outside `Platform/Vulkan` and the window seam. A file under `Strata/src` includes only the layers the table allows, and a failing include is fixed by inverting the dependency, never by an :term[allowlist]{id=allowlist} line. The reason: a second backend, or a test double, then needs a change in one folder. See the [layer table](../core/layers-registries.md).
:::

The interface's frame calls, quoted below, are the part the next sections follow. Read the comments on `BeginFrame` and `PrepareBackBuffer`: they state the contract in words.

```cpp src="Strata/src/Strata/Renderer/GraphicsDevice.h#L147-L175"
// Presentation. Not available on headless devices. A minimized window gets its swapchain once it has a size.
virtual bool CreateSwapchain(Window& window, bool vsync) = 0;
virtual void DestroySwapchain() = 0;
virtual bool HasSwapchain() const = 0; // True while presenting to a window
// Whether CreateSwapchain may be called: the device was made for a window it can present into (not headless).
virtual bool CanPresent() const = 0;

virtual void SetVSync(bool vsync) = 0;
virtual bool IsVSync() const = 0;
virtual nvrhi::ITexture* GetBackBuffer() const = 0;
virtual nvrhi::IFramebuffer* GetBackBufferFramebuffer() const = 0;
virtual nvrhi::Format GetBackBufferFormat() const = 0;
virtual glm::uvec2 GetBackBufferSize() const = 0;

// BeginFrame waits for a free frame slot and, with a swapchain, acquires the next back buffer (recreating
// the swapchain after resizes). It returns false when nothing should be rendered this frame (e.g. the
// window is minimized, or the device was lost); EndFrame must then not be called. EndFrame presents and
// advances the frame index.
virtual bool BeginFrame() = 0;
virtual void EndFrame() = 0;
// The GPU waits for the display to release the acquired back buffer only from here on: call it before the first
// command list of the frame that uses the back buffer (Renderer::PrepareBackBuffer does), so that the frame's earlier
// work - asset uploads, offscreen rendering - never queues behind the display. Does nothing after the first call of a
// frame; EndFrame calls it when nothing did. False when the frame has no back buffer (headless, or the wait could not
// be submitted: the back buffer is gone for the frame).
virtual bool PrepareBackBuffer() = 0;
virtual uint64_t GetFrameIndex() const = 0;
virtual uint32_t GetMaxFramesInFlight() const = 0;
virtual void WaitForIdle() = 0;
```

1. **Line 148:** the swap chain is made for a `Window` and a :term[vsync]{id=vsync} flag, and no Vulkan type appears.
2. **Line 152:** `CanPresent` tells a caller whether `CreateSwapchain` may be called at all.
3. **Line 165:** `BeginFrame` returns false when nothing may render, and then `EndFrame` must not follow.
4. **Line 172:** `PrepareBackBuffer` is the moment the GPU starts to wait for the display.
5. **Lines 173–175:** the frame index, the frames in flight and `WaitForIdle` let other code pace itself and stop safely.

## A toy version

A toy shows three ideas of the device without Vulkan: a score that picks one GPU, a queue that paces frames, and a function that sorts messages and counts the errors. It has no real GPU, so a `Gpu` is a few numbers, and the "wait" of the pacing queue is a line of output.

```cpp sketch="gpu-vulkan-nvrhi-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <queue>
#include <string>
#include <vector>

enum class GpuType
{
	Other,
	Integrated,
	Discrete
};

struct Gpu
{
	std::string Name;
	GpuType Type = GpuType::Other;
	uint32_t VulkanMinor = 2;
	bool DynamicRendering = true;
	uint64_t MemoryMiB = 0;
};

// Picks the best GPU that meets the requirements; every rejection is logged with its reason.
int SelectGpu(const std::vector<Gpu>& gpus)
{
	int best = -1;
	int64_t bestScore = -1;
	for (size_t index = 0; index < gpus.size(); index++)
	{
		const Gpu& gpu = gpus[index];
		if (gpu.VulkanMinor < 2)
		{
			std::printf("GPU '%s' skipped: Vulkan 1.%u (1.2 required)\n", gpu.Name.c_str(), static_cast<unsigned>(gpu.VulkanMinor));
			continue;
		}
		if (!gpu.DynamicRendering)
		{
			std::printf("GPU '%s' skipped: no dynamic rendering support\n", gpu.Name.c_str());
			continue;
		}
		int64_t score = static_cast<int64_t>(gpu.MemoryMiB);
		if (gpu.Type == GpuType::Discrete)
			score += 1'000'000;
		else if (gpu.Type == GpuType::Integrated)
			score += 100'000;
		std::printf("GPU '%s' scores %lld\n", gpu.Name.c_str(), static_cast<long long>(score));
		if (score <= bestScore)
			continue;
		bestScore = score;
		best = static_cast<int>(index);
	}
	return best;
}

// One ticket per submitted frame; a frame may begin only while fewer than the limit are still queued.
class FramePacer
{
public:
	explicit FramePacer(size_t maxFramesInFlight)
		: m_MaxFramesInFlight(maxFramesInFlight)
	{
	}

	void BeginFrame(uint32_t frame)
	{
		while (m_InFlight.size() >= m_MaxFramesInFlight)
		{
			std::printf("frame %u waits for frame %u\n", static_cast<unsigned>(frame), static_cast<unsigned>(m_InFlight.front()));
			m_InFlight.pop(); // the real device waits for the GPU's event query here
		}
	}

	void EndFrame(uint32_t frame) { m_InFlight.push(frame); }
private:
	size_t m_MaxFramesInFlight;
	std::queue<uint32_t> m_InFlight;
};

struct Message
{
	bool IsError = false;
	std::string Id;
};

// Errors count, a known false report is traced, everything else is a warning.
int Classify(const Message& message)
{
	if (message.IsError)
		return 2;
	return message.Id == "Loader Message" ? 0 : 1;
}

int main()
{
	const std::vector<Gpu> gpus = {
		{ "Old Card", GpuType::Discrete, 1, true, 4096 },
		{ "Laptop Integrated", GpuType::Integrated, 3, true, 16384 },
		{ "Big Discrete", GpuType::Discrete, 3, true, 8192 },
		{ "No Dynamic", GpuType::Discrete, 2, false, 24576 },
	};
	std::printf("chosen: %d\n", SelectGpu(gpus));

	FramePacer pacer(2);
	for (uint32_t frame = 0; frame < 4; frame++)
	{
		pacer.BeginFrame(frame);
		pacer.EndFrame(frame);
	}

	int errors = 0;
	const Message messages[] = { { true, "VUID-x" }, { false, "Loader Message" }, { false, "mvk-warn" } };
	for (const Message& message : messages)
		errors += Classify(message) == 2 ? 1 : 0;
	std::printf("errors counted: %d\n", errors);
	return 0;
}
```

```text output-of="gpu-vulkan-nvrhi-toy.cpp"
GPU 'Old Card' skipped: Vulkan 1.1 (1.2 required)
GPU 'Laptop Integrated' scores 116384
GPU 'Big Discrete' scores 1008192
GPU 'No Dynamic' skipped: no dynamic rendering support
chosen: 2
frame 2 waits for frame 0
frame 3 waits for frame 1
errors counted: 1
```

1. **Lines 31–40:** each failed requirement logs its reason and skips the GPU, as the real selection does.
2. **Lines 41–45:** the score is the memory in `MiB` plus a bonus for the kind of GPU.
3. **Lines 47–50:** a GPU replaces the best only with a strictly higher score, so a tie keeps the first.
4. **Lines 66–70:** while the queue is full the oldest ticket is removed, where the real device waits for an :term[event query]{id=fence}.
5. **Lines 86–91:** an error counts, one known false report is lowered to a trace, and everything else is a warning.

The output shows each idea at small scale. "Old Card" and "No Dynamic" are skipped with their reasons. The integrated GPU scores 116,384 and the big discrete card 1,008,192, so the discrete one wins whatever the integrated GPU's memory. The pacing queue lets frames 0 and 1 begin at once; frame 2 must wait for frame 0, and frame 3 for frame 1. Of three messages, only the error counts.

The real device does the same jobs with more checks, and with a real GPU behind each step. The next sections follow the order in which it runs.

## Opening the GPU: loader and instance

The first step is the Vulkan loader, a library that the operating system or the Vulkan software development kit (SDK) provides and that finds the drivers. `VulkanLoader` loads it once per process and returns its `vkGetInstanceProcAddr` function. GLFW is told to use the same function, so the instance and the window's surfaces always come from one loader. When the loader is missing, the error ends with advice that names what to install on this operating system. That is the GPU driver on Windows, the loader and a driver package on Linux, and MoltenVK and the loader on macOS.

Next the device creates the **instance**, the object that represents the program's connection to the Vulkan library. The instance decides which extensions and layers exist for the whole program. Strata requires Vulkan 1.2 and asks for at most 1.3. If the loader reports less than 1.2, the device logs the version it found and fails.

Extensions come from three places. A device with a window asks `VulkanPresentation` for the extensions the window system's surfaces need, and fails if the system reports no presentation support. The extension `VK_EXT_debug_utils` is added when present, so that messages from the layer reach the engine. The extension for portable devices is added when present, because without it the loader hides MoltenVK's devices.

## Validation: what the layer checks

Vulkan is explicit, so a call with a wrong argument does not fail politely. It may crash, hang, or draw wrong pictures on one vendor's driver and not on another's. A **validation layer** is a library that the loader inserts between the program and the driver. It checks every call against the specification and reports each violation as a message that names the rule that was broken. An explicit API needs one because the driver, to be fast, does not check.

The layer costs time on every call, so Strata asks for it only in Debug builds and in tests. `GraphicsModuleSpecification::Validation` is empty by default, and the module turns an empty value into true in Debug and false otherwise. NVRHI has a second validation layer that checks the library's rules, such as using a resource in the wrong state. A :term[Dist]{id=dist} build never includes that one: the code that wraps the device in it is compiled out, and a request for it only logs a warning.

If validation is requested and `VK_LAYER_KHRONOS_validation` is not installed, the device logs a warning and continues with NVRHI's validation alone. If the layer is listed but cannot be loaded, the first `vkCreateInstance` fails. Loaders fail differently here: with `VK_ERROR_LAYER_NOT_PRESENT` on macOS and with an out-of-memory error on Windows.

The device therefore tries again without the layer, whatever the first failure was. It logs the first result as a warning. Only when the second try fails too does it report an error.

Every message from the layer reaches one :term[callback]{id=callback} that sorts it. An error is logged and added to the error count. A warning is only logged. A few reports are known to be false or irrelevant, and the sorting function lowers them to trace level instead of hiding them. The quote below is the whole function.

```cpp src="Strata/src/Platform/Vulkan/VulkanDebugMessages.cpp#L24-L52"
VulkanMessageDisposition ClassifyVulkanMessage(const VulkanMessage& message, const VulkanMessageContext& context)
{
	if (message.Error)
	{
		// The validation layer's report of a descriptor set layout beyond the device's limits that the driver's support
		// query rejects. Where the query under-reports the bindless table, it says nothing about the table; the layer
		// still checks every set against the update-after-bind limits.
		if (context.SupportQueryUnderReportsBindlessTable && Equals(message.IdName, "VUID-vkCreateDescriptorSetLayout-support-09582"))
			return VulkanMessageDisposition::Trace;
		// The loader's reports of a validation layer it lists but cannot load (its library's search, "Requested layer ...
		// failed to load!"): the instance is created again without the layer, which is no error of the device.
		if (context.CreatingInstanceWithLayers && Equals(message.IdName, "Loader Message"))
			return VulkanMessageDisposition::Warning;
		return VulkanMessageDisposition::Error;
	}
	if (!message.Warning)
		return VulkanMessageDisposition::Trace;

	// The loader reports its search (e.g. missing registry keys for layer manifests) as warnings.
	if (Equals(message.IdName, "Loader Message"))
		return VulkanMessageDisposition::Trace;
	// MoltenVK reports every color attachment whose format Metal cannot blend (the prepass's R32_UINT entity IDs) as
	// "Blending is enabled ...", whether or not the pipeline blends it, and creates the pipeline without blending. The
	// engine never blends such a target; doing so would be invalid usage, which the validation layer reports as an error
	// (VUID-VkGraphicsPipelineCreateInfo-renderPass-06062, -06041 with render passes) where it is loaded.
	if (Equals(message.IdName, "mvk-warn") && Contains(message.Text, "Blending is enabled for attachment with format"))
		return VulkanMessageDisposition::Trace;
	return VulkanMessageDisposition::Warning;
}
```

1. **Lines 26–37:** an error is lowered only for the bindless support query on drivers that under-report it (lines 31–32) and for the loader's layer messages while the instance tries the layer (lines 35–36). Every other error counts.
2. **Lines 39–40:** a message that is neither an error nor a warning is only traced.
3. **Lines 43–44:** the loader's reports of its own search are traced.
4. **Lines 49–50:** MoltenVK's blending report is traced, because no pipeline of the engine blends that target.
5. **Line 51:** every other warning stays a warning.

NVRHI reports its own problems through a callback class. Info becomes a trace line, a warning becomes a warning, and an error or fatal message becomes an error line and adds one to a second counter. `GetErrorCount` returns the sum of both counters, so one number covers the layer and the library. A GPU test remembers the count at its start and ends with `CHECK(gpu.GetNewErrorCount() == 0)`.

:::caution
A scene that renders correctly can still produce warnings and errors. Ignoring them because "it renders" lets a mistake that one driver forgives crash on another driver. Strata counts every error, lowers only reports it has understood, and keeps the rest visible. The [debugging page](../gpu/debugging.md) shows how to enable validation and read its messages.
:::

## Choosing a GPU: the physical device

A machine may hold several GPUs: a laptop often has a small integrated one and a large discrete one. Vulkan calls each a **physical device**: one GPU as the driver reports it, with its properties, features, memory and :term[queue families]{id=queue-family}. `SelectPhysicalDevice` lists them all and keeps the best one that meets the requirements. For each GPU that fails a requirement it logs `GPU '<name>' skipped: <reason>` at info level.

The requirements are the features the engine's code relies on. The comments of the quote below give the reason for the first four. Search it for the one `reject` line per failed check.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L659-L711"
// Required features: dynamic rendering (NVRHI render passes), synchronization2 (NVRHI barriers), timeline
// semaphores (NVRHI queues) and descriptor indexing (bindless textures). Vulkan 1.2 devices provide the first
// two through extensions.
const uint32_t deviceApiVersion = std::min(m_InstanceApiVersion, properties.apiVersion);
const bool vulkan13 = deviceApiVersion >= VK_API_VERSION_1_3;
VkPhysicalDeviceVulkan13Features features13 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES };
VkPhysicalDeviceDynamicRenderingFeaturesKHR dynamicRendering = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DYNAMIC_RENDERING_FEATURES_KHR };
VkPhysicalDeviceSynchronization2FeaturesKHR synchronization2 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SYNCHRONIZATION_2_FEATURES_KHR };
VkPhysicalDeviceVulkan12Features features12 = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES };
VkPhysicalDeviceFeatures2 features = { VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2 };
features.pNext = &features12;
if (vulkan13)
{
	features12.pNext = &features13;
}
else
{
	features12.pNext = &dynamicRendering;
	dynamicRendering.pNext = &synchronization2;
}
dispatch.vkGetPhysicalDeviceFeatures2(physicalDevice, &features);

const bool hasDynamicRendering = vulkan13 ? features13.dynamicRendering == VK_TRUE
	: (HasExtension(extensions, VK_KHR_DYNAMIC_RENDERING_EXTENSION_NAME) && dynamicRendering.dynamicRendering == VK_TRUE);
if (!hasDynamicRendering)
{
	reject("no dynamic rendering support");
	continue;
}
const bool hasSynchronization2 = vulkan13 ? features13.synchronization2 == VK_TRUE
	: (HasExtension(extensions, VK_KHR_SYNCHRONIZATION_2_EXTENSION_NAME) && synchronization2.synchronization2 == VK_TRUE);
if (!hasSynchronization2)
{
	reject("no synchronization2 support");
	continue;
}
if (!features12.timelineSemaphore || !features12.descriptorIndexing || !features12.runtimeDescriptorArray
	|| !features12.descriptorBindingPartiallyBound || !features12.shaderSampledImageArrayNonUniformIndexing
	|| !features12.descriptorBindingSampledImageUpdateAfterBind || !features12.descriptorBindingUpdateUnusedWhilePending)
{
	reject("missing timeline semaphores or descriptor indexing features");
	continue;
}
if (!features.features.samplerAnisotropy)
{
	reject("no anisotropic filtering");
	continue;
}
// The scene passes' one binding layout holds the reflection probes' cube array, which SPIR-V may sample only with
// the feature enabled.
if (!features.features.imageCubeArray)
{
	reject("no cube map arrays (imageCubeArray)");
```

1. **Lines 659–661:** the comment names the features that NVRHI and the bindless table need.
2. **Lines 681–686:** on Vulkan 1.3 dynamic rendering is core; on 1.2 the check needs the extension and its feature flag.
3. **Lines 695–701:** one check covers the `timelineSemaphore` feature and the descriptor indexing group, and its message names both.
4. **Lines 702–704:** the sampler feature `samplerAnisotropy` is required.
5. **Lines 709–711:** the cube map array feature is required for the reflection probes.

Each check has a reason. Vulkan 1.2 is the floor: its core already holds the `timelineSemaphore` and descriptor indexing features that later checks require. A swap chain extension is needed unless the device is headless. Dynamic rendering lets NVRHI draw without render pass objects, and synchronization2 lets it write barriers. The feature `timelineSemaphore` is how NVRHI's queues wait for each other.

Descriptor indexing is the set of features that lets the renderer's one big table of textures work, so that a shader picks a texture by number. The sampler feature `samplerAnisotropy` serves the sampler whose `maxAnisotropy` is 16, and cube map arrays serve the reflection probes in the scene passes' one binding layout. Last, the GPU needs a queue family that can run graphics and compute and present to the window.

The score then decides among the GPUs that pass. It counts the device-local memory, the memory the GPU holds itself, in units of 2^20 :term[bytes]{id=byte} (`MiB`), and adds 1,000,000 for a discrete GPU or 100,000 for an integrated one. A GPU replaces the best so far only when its score is strictly higher.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L736-L754"
VkPhysicalDeviceMemoryProperties memoryProperties;
dispatch.vkGetPhysicalDeviceMemoryProperties(physicalDevice, &memoryProperties);
uint64_t dedicatedMemory = 0;
for (uint32_t heap = 0; heap < memoryProperties.memoryHeapCount; heap++)
{
	if (memoryProperties.memoryHeaps[heap].flags & VK_MEMORY_HEAP_DEVICE_LOCAL_BIT)
		dedicatedMemory += memoryProperties.memoryHeaps[heap].size;
}

int64_t score = static_cast<int64_t>(dedicatedMemory >> 20);
if (properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU)
	score += 1'000'000;
else if (properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU)
	score += 100'000;

if (score <= bestScore)
	continue;

bestScore = score;
```

1. **Lines 736–743:** the sizes of all device-local heaps add up.
2. **Line 745:** shifting by 20 bits gives the memory in `MiB`, the base of the score.
3. **Lines 746–749:** a discrete GPU adds 1,000,000 and an integrated one 100,000.
4. **Lines 751–752:** a score that is not higher than the best so far is skipped, so a tie keeps the first GPU.
5. **Line 754:** the GPU becomes the best so far.

:::example[A laptop with two GPUs]
The laptop has an integrated GPU whose driver reports 16,384 `MiB` of device-local memory (it shares the system's memory) and a discrete GPU with 8,192 `MiB`. The integrated GPU scores 16,384 + 100,000 = 116,384. The discrete one scores 8,192 + 1,000,000 = 1,008,192. The discrete GPU wins, as the toy's output showed, although the integrated GPU reports twice the memory.

With two discrete cards of 8,192 and 12,288 `MiB`, the second scores 1,012,288 and wins. With two identical cards the first stays chosen, because the test is `score <= bestScore`.
:::

No program chooses the GPU. The specification has an `AdapterIndex` field, with -1 meaning "the best", but at the pin only `GraphicsDevice.h` and `VulkanGraphicsDevice.cpp` mention it. The `GraphicsModule` never sets it, so the score alone decides. The log names every GPU the device skipped, with the reason, so a person can see why a card was not used.

## Queues, the logical device and the memory budget

A Vulkan queue accepts the commands the program submits. Queues come in families, and a family lists what its queues can do: graphics, compute, transfer. The device first takes the family that does graphics and compute together and can present: the graphics queue. It then searches for a dedicated compute family (compute without graphics) and a dedicated transfer family (transfer without compute or graphics), which many discrete GPUs offer as separate hardware engines.

The device creates one queue in each family it found. Whether uploads use the transfer queue is the upload queue's concern, which [the upload queue page](../gpu/upload-queue.md) teaches.

The **logical device** is the object the program creates from a physical device to use it: it enables a set of features and extensions and creates the queues. Strata enables the required features, plus every useful optional feature that exists, so later code can ask `GraphicsDeviceInfo` what is on. On Vulkan 1.2 it adds the dynamic rendering and synchronization2 extensions, which 1.3 includes. It adds `VK_KHR_portability_subset` whenever the device offers it, because MoltenVK requires that, and it adds the memory budget extension when present.

`GetMemoryBudget` reads that extension for each device-local heap and adds the heaps' budgets and usages. Without the extension it reports the total device-local memory as the budget and no usage. [The residency page](../assets/residency.md) uses these numbers to decide how much to keep loaded.

:::note
MoltenVK lacks some features that other drivers have: `drawIndirectCount`, sampler min-max filtering, geometry and mesh shaders and a dedicated transfer queue, among others. Its limits are tighter too. Renderer code therefore asks the device's features and never asks "is this macOS?". The reason: the same missing feature can appear on a Windows driver, and a test on the feature catches it where a test on the operating system does not.
:::

## Wrapping the device in NVRHI

Strata creates the Vulkan device itself, because it chooses the features and queues. It then hands the handles to NVRHI in a `DeviceDesc` and gets back an NVRHI device, the object the whole renderer calls. Search the quote for the `try` block, for what the code does when NVRHI fails, and for the `#if` that removes the validation layer from Dist.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L948-L988"
nvrhi::vulkan::DeviceDesc nvrhiDesc;
nvrhiDesc.errorCB = &m_MessageCallback;
nvrhiDesc.instance = m_Instance;
nvrhiDesc.physicalDevice = m_PhysicalDevice;
nvrhiDesc.device = m_Device;
nvrhiDesc.graphicsQueue = m_GraphicsQueue;
nvrhiDesc.graphicsQueueIndex = m_GraphicsFamily;
nvrhiDesc.computeQueue = m_ComputeQueue;
nvrhiDesc.computeQueueIndex = m_ComputeFamily;
nvrhiDesc.transferQueue = m_TransferQueue;
nvrhiDesc.transferQueueIndex = m_TransferFamily;
nvrhiDesc.instanceExtensions = instanceExtensionNames.data();
nvrhiDesc.numInstanceExtensions = instanceExtensionNames.size();
nvrhiDesc.deviceExtensions = extensionNames.data();
nvrhiDesc.numDeviceExtensions = extensionNames.size();
nvrhiDesc.descriptorBindingUniformBufferUpdateAfterBind = enabled12.descriptorBindingUniformBufferUpdateAfterBind == VK_TRUE;

// NVRHI uses vulkan.hpp with exceptions enabled; failures surface as vk::SystemError.
try
{
	m_NvrhiVulkanDevice = nvrhi::vulkan::createDevice(nvrhiDesc);
}
catch (const vk::SystemError& error)
{
	ST_CORE_ERROR("Failed to create the NVRHI Vulkan device: {}", error.what());
	return false;
}
if (!m_NvrhiVulkanDevice)
{
	ST_CORE_ERROR("Failed to create the NVRHI Vulkan device");
	return false;
}

#if defined(ST_DIST)
// NVRHI's validation layer is not part of shipping builds (games never ask for it): the plain device.
if (m_Specification.EnableValidation)
	ST_CORE_WARN("NVRHI validation is not part of Dist builds: the device runs without it");
m_NvrhiDevice = nvrhi::DeviceHandle(m_NvrhiVulkanDevice);
#else
m_NvrhiDevice = m_Specification.EnableValidation ? nvrhi::validation::createValidationLayer(m_NvrhiVulkanDevice) : nvrhi::DeviceHandle(m_NvrhiVulkanDevice);
#endif
```

1. **Lines 948–949:** the description starts with the callback that counts NVRHI's errors.
2. **Lines 966–973:** `createDevice` runs in a `try`, and a `vk::SystemError` is logged and turned into false.
3. **Lines 975–979:** a null device is a failure too.
4. **Lines 981–985:** in Dist the plain device is used, and a request for validation only logs a warning.
5. **Lines 986–988:** in other builds the device is wrapped in NVRHI's validation layer when validation is on.

NVRHI uses `vulkan.hpp` with exceptions on, so a failure arrives as a `vk::SystemError`. Engine code does not throw and does not let a third-party exception cross its borders, so the call site catches it, logs the reason and returns false.

:::rule[Exceptions]
Exceptions from NVRHI and `vulkan.hpp` are caught at the call site. The reason: Strata's own code returns errors, so a caller above must never see an exception. The same holds for `nlohmann::json`.
:::

## The swap chain

A window does not hand out pixels directly. A **surface** is Vulkan's handle for the window's picture area, and the swap chain is a set of images that belong to that surface and that the display shows one after another. `VulkanPresentation` creates the surface for the device, so the device names no window system. If creating it fails, `BeginFrame` tries again in the next frame.

The swap chain's images need a format. Strata asks for 8-bit `B8G8R8A8_UNORM` first, then `R8G8B8A8_UNORM`, both with the :term[sRGB]{id=srgb} non-linear :term[color space]{id=color-space}.

A **UNORM** (unsigned :term[normalized]{id=normalization}) format stores each channel as an unsigned number from 0 to 1 in equal steps and applies no conversion.

The **sRGB formats** hold the same bytes with a promise: the hardware converts between linear light and the sRGB curve when you write or read.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L1130-L1168"
// The engine writes display-encoded (sRGB) values itself, so it wants a UNORM back buffer.
VkSurfaceFormatKHR surfaceFormat = { VK_FORMAT_UNDEFINED, VK_COLOR_SPACE_SRGB_NONLINEAR_KHR };
for (const VkFormat preferred : { VK_FORMAT_B8G8R8A8_UNORM, VK_FORMAT_R8G8B8A8_UNORM })
{
	for (const VkSurfaceFormatKHR& format : formats)
	{
		if (format.format == preferred && format.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR)
		{
			surfaceFormat = format;
			break;
		}
	}
	if (surfaceFormat.format != VK_FORMAT_UNDEFINED)
		break;
}
if (surfaceFormat.format == VK_FORMAT_UNDEFINED)
{
	ST_CORE_ERROR("The window surface supports no 8-bit UNORM sRGB format");
	return false;
}

uint32_t presentModeCount = 0;
dispatch.vkGetPhysicalDeviceSurfacePresentModesKHR(m_PhysicalDevice, m_Surface, &presentModeCount, nullptr);
std::vector<VkPresentModeKHR> presentModes(presentModeCount);
dispatch.vkGetPhysicalDeviceSurfacePresentModesKHR(m_PhysicalDevice, m_Surface, &presentModeCount, presentModes.data());
auto supportsMode = [&](VkPresentModeKHR mode) { return std::find(presentModes.begin(), presentModes.end(), mode) != presentModes.end(); };

VkPresentModeKHR presentMode = VK_PRESENT_MODE_FIFO_KHR; // Always supported
if (!m_VSync)
{
	if (supportsMode(VK_PRESENT_MODE_MAILBOX_KHR))
		presentMode = VK_PRESENT_MODE_MAILBOX_KHR;
	else if (supportsMode(VK_PRESENT_MODE_IMMEDIATE_KHR))
		presentMode = VK_PRESENT_MODE_IMMEDIATE_KHR;
}

uint32_t imageCount = std::max(capabilities.minImageCount + 1, m_Specification.MaxFramesInFlight + 1);
if (capabilities.maxImageCount > 0)
	imageCount = std::min(imageCount, capabilities.maxImageCount);
```

1. **Lines 1130–1143:** the engine prefers `B8G8R8A8_UNORM`, then `R8G8B8A8_UNORM`, with the sRGB non-linear color space, and the comment gives the reason.
2. **Lines 1145–1149:** a surface with neither format is an error and no swap chain is made.
3. **Lines 1157–1164:** `FIFO` is the default; with vsync off, `MAILBOX` and then `IMMEDIATE` replace it where offered.
4. **Lines 1166–1168:** the image count and its cap by the surface's maximum.

The choice of an unsigned normalized (UNORM) format has a reason: the engine writes display-encoded values itself, in its last pass. With an sRGB image, the hardware would encode the values a second time. A mid-grey that the engine already encoded to 0.5 would be encoded again to about 0.735, and the whole picture would look washed out.

The :term[present mode]{id=present-mode} is `FIFO` when :term[vsync]{id=vsync} is on, because the specification guarantees it. With vsync off, the device takes `MAILBOX` when the surface offers it, then `IMMEDIATE`, then falls back to `FIFO`. The image count is the larger of the surface's minimum plus one and the frames in flight plus one, clamped to the surface's maximum when it has one.

:::example[How many images?]
A typical surface has a minimum of 2 and no maximum. With 2 frames in flight, the count is max(2 + 1, 2 + 1) = 3. With 4 frames in flight it is max(3, 5) = 5. A surface with a minimum of 3 and a maximum of 4, with 4 frames in flight, would want 5 and gets 4. The extra image beyond the frames in flight lets the display hold one image while the GPU works on every frame still in flight.
:::

The swap chain has a short life cycle. It does not exist while the window is minimized: a window that starts with no size gets its swap chain in the `BeginFrame` that first finds a size. Each frame then acquires an image, prepares it, presents it, and goes around again. A change of window size, or a report that the images are out of date or no longer fit well, destroys the images and makes new ones. A lost device ends the cycle.

```mermaid caption="The states of the swap chain: none without a window size, a loop of acquire, prepare and present, a side path to rebuild it, and a dead end when the device is lost." alt="A state diagram. It starts with no swap chain, which becomes created once the window has a size. Created leads to acquired, prepared, then presented, which returns to acquired for the next frame. Acquired and presented lead to recreated when the window changes, which returns to acquired. Acquired, prepared and presented can lead to device lost, which has no exit."
stateDiagram-v2
	[*] --> NoSwapChain
	NoSwapChain --> Created: window has a size
	Created --> Acquired: BeginFrame
	Acquired --> Prepared: PrepareBackBuffer
	Prepared --> Presented: EndFrame
	Presented --> Acquired: next frame
	Acquired --> Recreated: out of date
	Presented --> Recreated: changed or no longer fits
	Recreated --> Acquired
	Acquired --> DeviceLost
	Prepared --> DeviceLost
	Presented --> DeviceLost
	DeviceLost --> [*]
```

## The device's frame: pacing, acquire and present

Every frame goes through `BeginFrame` and `EndFrame` of the device. The first problem is pacing. The :term[central processing unit]{id=processor} (CPU) records a frame much faster than the GPU runs it, so without a limit the CPU would run far ahead and the pictures would lag behind input. Frames in flight are the limit: with 2, the CPU may be at most two frames ahead.

The device keeps a queue of :term[event queries]{id=fence}, one per submitted frame. An event query is an NVRHI object that the GPU signals when the work before it is done. `BeginFrame` waits for the oldest query while the queue holds as many as the limit allows.

:::example[Frame pacing with 2 frames in flight]
Frames 0 and 1 begin without waiting, because the queue holds fewer than 2 queries. Frame 2 finds 2 in the queue, waits for frame 0's query and then begins. Frame 3 waits for frame 1, and so on. If the GPU finishes each frame in 8 ms and the CPU needs 4 ms, the CPU waits about 4 ms a frame, and the pictures lag input by at most two frames.
:::

The first quote is the first half of `BeginFrame`: the pacing wait, the window's state and the swap chain's recreation. Read what each early `return false` means.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L1438-L1474"
bool VulkanGraphicsDevice::BeginFrame()
{
	m_ImageAcquired = false;
	if (m_DeviceLost)
		return false;

	// Frame pacing: wait until the GPU has finished the frame that last used this slot.
	try
	{
		while (m_FramesInFlight.size() >= m_Specification.MaxFramesInFlight)
		{
			nvrhi::EventQueryHandle query = m_FramesInFlight.front();
			m_FramesInFlight.pop();
			m_NvrhiDevice->waitEventQuery(query);
			m_EventQueryPool.push_back(query);
		}
	}
	catch (const vk::SystemError& error)
	{
		OnDeviceLost(error.what());
		return false;
	}

	if (!m_Window)
		return true; // Headless or no window: offscreen rendering only
	if (m_Surface == VK_NULL_HANDLE && !CreateSurface())
		return false; // Retried every frame

	const glm::uvec2 framebufferSize = m_Window->GetFramebufferSize();
	if (framebufferSize.x == 0 || framebufferSize.y == 0)
		return false; // Minimized

	if (m_Swapchain == VK_NULL_HANDLE || m_SwapchainDirty || framebufferSize != GetBackBufferSize())
	{
		if (!RecreateSwapchainResources() || m_Swapchain == VK_NULL_HANDLE)
			return false;
	}
```

1. **Lines 1444–1458:** the pacing wait for the oldest event query, and a `vk::SystemError` there means the device is lost.
2. **Lines 1461–1464:** without a window the frame renders into textures only and begins at once; a missing surface is created again each frame.
3. **Lines 1466–1468:** a window of size 0 is minimized, so the frame is skipped.
4. **Lines 1470–1474:** the swap chain is rebuilt when it is missing, marked dirty or no longer the window's size.

After that the device asks the swap chain for an image. This is the acquire, and it may need a second try. Vulkan hands out an image together with a **semaphore**: a signal that the GPU can wait on, which the display raises when the image is free. The second half of `BeginFrame` shows the loop with two attempts.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L1476-L1513"
	const auto& dispatch = VULKAN_HPP_DEFAULT_DISPATCHER;
	for (int attempt = 0; attempt < 2; attempt++)
	{
		VkSemaphore acquireSemaphore = m_AcquireSemaphores[m_AcquireSemaphoreIndex];
		VkResult result = dispatch.vkAcquireNextImageKHR(m_Device, m_Swapchain, UINT64_MAX, acquireSemaphore, VK_NULL_HANDLE, &m_CurrentImageIndex);
		if (result == VK_ERROR_OUT_OF_DATE_KHR)
		{
			if (!RecreateSwapchainResources() || m_Swapchain == VK_NULL_HANDLE)
				return false;
			continue;
		}
		if (result == VK_ERROR_DEVICE_LOST)
		{
			OnDeviceLost("vkAcquireNextImageKHR");
			return false;
		}
		if (result != VK_SUCCESS && result != VK_SUBOPTIMAL_KHR)
		{
			ST_CORE_ERROR("vkAcquireNextImageKHR failed: {}", nvrhi::vulkan::resultToString(result));
			// Rebuild the surface and swapchain next frame (e.g. after VK_ERROR_SURFACE_LOST_KHR).
			DestroySwapchainResources();
			DestroySurface();
			return false;
		}

		if (result == VK_SUBOPTIMAL_KHR)
			m_SwapchainDirty = true; // Present this frame, recreate before the next one

		m_AcquireSemaphoreIndex = (m_AcquireSemaphoreIndex + 1) % static_cast<uint32_t>(m_AcquireSemaphores.size());

		// The GPU waits for the image only once the frame's first work on it is about to be submitted (PrepareBackBuffer):
		// waiting here would make every submission of the frame wait for the display, the asset uploads too.
		m_PendingAcquireWait = acquireSemaphore;
		m_ImageAcquired = true;
		return true;
	}
	return false;
}
```

1. **Lines 1477–1485:** two attempts: an out-of-date report rebuilds the swap chain and tries again.
2. **Lines 1487–1491:** a lost device is recorded and the frame fails.
3. **Lines 1492–1498:** any other failure destroys the swap chain and the surface, so the next frame builds both again.
4. **Lines 1501–1502:** an image reported as `VK_SUBOPTIMAL_KHR` still presents, and the chain is rebuilt before the next frame.
5. **Lines 1506–1510:** the semaphore is kept as the pending wait, and the GPU does not wait for it yet.

The second try matters when the report is `VK_ERROR_OUT_OF_DATE_KHR`: the window changed, so the images are useless. The device rebuilds them and tries again. A report of `VK_SUBOPTIMAL_KHR` is not a failure: the frame presents, and the chain is rebuilt before the next one.

The device does not make the GPU wait for the acquire semaphore here. A frame's first work is uploads and passes that draw into textures and never touch the image. If the GPU waited at the start, all of it would queue behind the display.

The wait is submitted only at the :term[back buffer's]{id=back-buffer} first use, in `PrepareBackBuffer`, which calls `SubmitPendingAcquireWait`. The wait uses the `ALL_COMMANDS` stage because NVRHI's own semaphore waits use the top of the pipeline, which blocks nothing.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L1515-L1555"
VkResult VulkanGraphicsDevice::SubmitPendingAcquireWait()
{
	// Every later submission on the graphics queue waits for the image. NVRHI's own semaphore waits use the TOP_OF_PIPE
	// stage, which blocks nothing, so the wait is submitted here with ALL_COMMANDS: a semaphore wait also orders all work
	// submitted after it on the same queue (and none submitted before it, such as the frame's uploads).
	const VkPipelineStageFlags waitStage = VK_PIPELINE_STAGE_ALL_COMMANDS_BIT;
	VkSubmitInfo submitInfo = { VK_STRUCTURE_TYPE_SUBMIT_INFO };
	submitInfo.waitSemaphoreCount = 1;
	submitInfo.pWaitSemaphores = &m_PendingAcquireWait;
	submitInfo.pWaitDstStageMask = &waitStage;
	const VkResult result = VULKAN_HPP_DEFAULT_DISPATCHER.vkQueueSubmit(m_GraphicsQueue, 1, &submitInfo, VK_NULL_HANDLE);
	m_PendingAcquireWait = VK_NULL_HANDLE;
	return result;
}

bool VulkanGraphicsDevice::PrepareBackBuffer()
{
	if (!m_ImageAcquired)
		return false;
	if (m_PendingAcquireWait == VK_NULL_HANDLE)
		return true; // Submitted earlier in the frame

	const VkResult result = SubmitPendingAcquireWait();
	if (result != VK_SUCCESS)
	{
		if (result == VK_ERROR_DEVICE_LOST)
		{
			OnDeviceLost("vkQueueSubmit");
		}
		else
		{
			// The acquired image and its signaled semaphore cannot be used; start over with a new swapchain.
			ST_CORE_ERROR("vkQueueSubmit failed: {}", nvrhi::vulkan::resultToString(result));
			DestroySwapchainResources();
		}
		m_ImageAcquired = false;
		return false;
	}
	InitializeAcquiredImage();
	return true;
}
```

1. **Lines 1517–1520:** the wait is submitted with the `ALL_COMMANDS` stage, which orders all later work on the queue and none of the earlier work.
2. **Lines 1532–1535:** with no image, or when the wait is already submitted, there is nothing to do.
3. **Lines 1538–1551:** a failed submission either marks the device lost or destroys the swap chain, and the frame has no back buffer.

At the end of the frame, `EndFrame` presents. NVRHI attaches a queued signal to the next submission, so the device queues the present semaphore's signal and submits an empty :term[command list]{id=command-list}, which flushes it. `vkQueuePresentKHR` then waits on that semaphore, so the image goes to the display only after the frame's work is done.

The device then adds the frame's event query to the pacing queue, lets NVRHI collect finished work with `runGarbageCollection` and advances the frame index. The [GPU frame page](../gpu/how-a-gpu-frame-works.md) explains the frame as a whole. The quote shows how this device does it.

```cpp src="Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp#L1557-L1605"
void VulkanGraphicsDevice::EndFrame()
{
	// Present waits for the image's acquisition too, also in a frame that never used the back buffer.
	if (m_ImageAcquired)
		PrepareBackBuffer();
	if (m_ImageAcquired)
	{
		VkSemaphore presentSemaphore = m_PresentSemaphores[m_CurrentImageIndex];
		m_NvrhiVulkanDevice->queueSignalSemaphore(nvrhi::CommandQueue::Graphics, presentSemaphore, 0);

		// NVRHI attaches queued semaphore signals to the next submission; submit an empty command list to flush.
		m_BarrierCommandList->open();
		m_BarrierCommandList->close();
		m_NvrhiDevice->executeCommandList(m_BarrierCommandList);

		VkPresentInfoKHR presentInfo = { VK_STRUCTURE_TYPE_PRESENT_INFO_KHR };
		presentInfo.waitSemaphoreCount = 1;
		presentInfo.pWaitSemaphores = &presentSemaphore;
		presentInfo.swapchainCount = 1;
		presentInfo.pSwapchains = &m_Swapchain;
		presentInfo.pImageIndices = &m_CurrentImageIndex;
		const VkResult result = VULKAN_HPP_DEFAULT_DISPATCHER.vkQueuePresentKHR(m_GraphicsQueue, &presentInfo);
		if (result == VK_ERROR_OUT_OF_DATE_KHR || result == VK_SUBOPTIMAL_KHR)
			m_SwapchainDirty = true;
		else if (result == VK_ERROR_DEVICE_LOST)
			OnDeviceLost("vkQueuePresentKHR");
		else if (result != VK_SUCCESS)
			ST_CORE_ERROR("vkQueuePresentKHR failed: {}", nvrhi::vulkan::resultToString(result));

		m_ImageAcquired = false;
	}

	nvrhi::EventQueryHandle query;
	if (!m_EventQueryPool.empty())
	{
		query = m_EventQueryPool.back();
		m_EventQueryPool.pop_back();
	}
	else
	{
		query = m_NvrhiDevice->createEventQuery();
	}
	m_NvrhiDevice->resetEventQuery(query);
	m_NvrhiDevice->setEventQuery(query, nvrhi::CommandQueue::Graphics);
	m_FramesInFlight.push(query);

	m_NvrhiDevice->runGarbageCollection();
	m_FrameIndex++;
}
```

1. **Lines 1559–1561:** a frame that never used the back buffer still submits the wait before it presents.
2. **Lines 1565–1570:** the present semaphore's signal is queued and an empty command list flushes it.
3. **Lines 1578–1584:** the present call can report `VK_ERROR_OUT_OF_DATE_KHR` or `VK_SUBOPTIMAL_KHR`, which mark the chain dirty, or a lost device.
4. **Lines 1589–1601:** a pooled event query is set after the frame's work and joins the pacing queue.
5. **Lines 1603–1604:** NVRHI collects finished work and the frame index advances.

When Vulkan reports `VK_ERROR_DEVICE_LOST`, or a `vk::SystemError` is caught in the pacing wait, the device is **device lost**: the driver reset, or the GPU was removed or crashed, and every handle is dead. `OnDeviceLost` logs a critical message that names the call, sets the flag and drops the acquired image. From then on `BeginFrame` returns false, and the graphics module closes the program. Recovery would mean rebuilding every resource, and Strata does not attempt it.

## Command lists and GPU resources in NVRHI

A command list is the NVRHI object that records commands for the GPU. The pattern is always the same: `open()`, record, `close()`, then `executeCommandList`. Recording does not run anything. Execution submits the closed list to a queue, and the GPU runs it later.

An **immediate command list** is one made with NVRHI's default parameters, which ask for immediate execution. Its one visible rule is that NVRHI's validation layer refuses a second open immediate list. A list that may open while another is open, such as the upload batch's transfer list, is created with `setEnableImmediateExecution(false)`. The [lifetimes page](../gpu/resources-lifetimes.md) teaches the rule in full.

The main thread records and submits every command list. The renderer's jobs run only CPU work: extraction of draws, queries for shadow casters, poses and staging copies. The reason is that a command list is not made for recording from two threads, and the order of the queue's work must be known. The [jobs page](../core/jobs.md) describes the job system.

NVRHI creates GPU resources from a description, a plain :term[struct]{id=struct} that you fill and pass to the device. A texture's description holds its size, format, mip levels, array layers and dimension. Its uses are flags: `isRenderTarget` for drawing into it, `isUAV` to let shaders write it, and a depth format for depth targets. A texture that a shader only samples needs no flag. A buffer's description holds a byte size and flags in the same way.

A description also holds two settings about state. `initialState` is the state the resource starts in, such as `RenderTarget` or `ShaderResource`. With `keepInitialState` set to true, NVRHI returns the resource to that state at the end of each command list, so you write no barriers for it by hand. A third field, `debugName`, labels the resource in validation messages and in GPU debuggers, and costs nothing, so Strata sets it on everything.

Memory that the CPU can touch is a separate case. A plain buffer or texture lives in device memory, and its `cpuAccess` is `None`. A staging buffer that the CPU writes before the GPU copies from it has `CpuAccessMode::Write`. A readback buffer that the GPU writes before the CPU reads it has `CpuAccessMode::Read`. A part of a texture, one mip level of one array layer, is a `subresource`, and `AllSubresources` names every part.

The first quote is the engine's one function for render targets.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L215-L226"
nvrhi::TextureHandle SceneRenderer::CreateRenderTarget(nvrhi::IDevice* device, uint32_t width, uint32_t height, nvrhi::Format format, const std::string& name, bool depth)
{
	nvrhi::TextureDesc desc;
	desc.width = width;
	desc.height = height;
	desc.format = format;
	desc.debugName = name;
	desc.isRenderTarget = true;
	desc.initialState = depth ? nvrhi::ResourceStates::DepthWrite : nvrhi::ResourceStates::RenderTarget;
	desc.keepInitialState = true;
	return device->createTexture(desc);
}
```

1. **Line 221:** the debug name labels the texture in validation messages.
2. **Line 222:** `isRenderTarget` is the use: the texture can be drawn into.
3. **Lines 223–224:** the initial state is `DepthWrite` or `RenderTarget`, and `keepInitialState` makes NVRHI return it to that state after each command list.

The second is the upload staging buffer's description in the staging pool. Compare it with the first: it is a buffer, the CPU writes it, and the GPU only reads it.

```cpp src="Strata/src/Strata/Renderer/StagingPool.cpp#L52-L60"
nvrhi::BufferDesc desc;
desc.byteSize = size;
desc.cpuAccess = nvrhi::CpuAccessMode::Write;
desc.debugName = "UploadStagingBuffer";
// Only ever copied from; the copies that read it are recorded after the CPU wrote it.
desc.initialState = nvrhi::ResourceStates::CopySource;
desc.keepInitialState = true;
MakeRoom(size, limit);
nvrhi::BufferHandle staging = m_Device->createBuffer(desc);
```

A readback does the reverse. `TextureReadback` makes a staging texture with `CpuAccessMode::Read` and the state `CopyDest`, and `BufferReadback` makes a buffer with the same access and state. The GPU copies into them, and the CPU reads once an event query reports the copy done.

To draw, you create an `IFramebuffer` from the textures that are drawn into and a pipeline from the shaders and fixed-function state. You then fill a `GraphicsState`: the pipeline, the target textures, the viewport and the bindings. The engine's test of its clip-space conventions does exactly that with the smallest setup. Read the order: set the state, draw, close, execute.

```cpp src="StrataTests/src/Renderer/GPURendererTests.cpp#L152-L159"
commandList->clearTextureFloat(target, nvrhi::AllSubresources, nvrhi::Color(0.0f, 0.0f, 1.0f, 1.0f));
nvrhi::GraphicsState state;
state.pipeline = pipeline;
state.framebuffer = framebuffer;
state.viewport.addViewportAndScissorRect(nvrhi::Viewport(static_cast<float>(size), static_cast<float>(size)));
commandList->setGraphicsState(state);
commandList->draw(nvrhi::DrawArguments().setVertexCount(3));
commandList->close();
```

The test then reads the pixels back with `Renderer::ReadTexture`, which blocks and so belongs to tests and tools.

## The graphics module

The `GraphicsModule` is the :term[engine module]{id=engine-module} that owns all of this: the device, its swap chain when the program has a window, and the `Renderer`. [The engine modules page](../core/engine-modules.md) teaches modules in general. This section covers what this one does. The editor lists the module in a windowed run and in a headless run (without a window, for captures), and not at all with `--no-gpu`. The :term[runtime]{id=runtime} lists it in a windowed run and omits it when headless.

`OnInit` creates the device, then the swap chain if the device can present, then `Renderer::Init`. The module's specification holds `Validation` (empty: on in Debug) and `TransferQueueUploads`. If anything fails, the module resets the device and sets a start failure, whose advice is the install advice of the platform.

```cpp src="Strata/src/Strata/Renderer/GraphicsModule.cpp#L27-L79"
bool GraphicsModule::OnInit(EngineContext& context)
{
	m_Window = context.MainWindow;
	const std::string& name = context.App.GetSpecification().Name;

	GraphicsDeviceSpecification deviceSpecification;
	deviceSpecification.ApplicationName = name;
	deviceSpecification.Headless = m_Window == nullptr;
	deviceSpecification.PresentationWindow = m_Window;
#if defined(ST_DEBUG)
	deviceSpecification.EnableValidation = m_Specification.Validation.value_or(true);
#else
	deviceSpecification.EnableValidation = m_Specification.Validation.value_or(false);
#endif

	m_Device = GraphicsDevice::Create(deviceSpecification);
	bool started = m_Device != nullptr;
	// A window that cannot present (a test's stand-in) gets a device that renders offscreen, and no swapchain.
	if (started && m_Window && m_Device->CanPresent())
		started = m_Device->CreateSwapchain(*m_Window, m_Window->IsVSync());
	if (started)
	{
		RendererSpecification rendererSpecification;
		rendererSpecification.TransferQueueUploads = m_Specification.TransferQueueUploads;
		started = Renderer::Init(*m_Device, rendererSpecification);
	}
	if (started)
		return true;

	// The device logged why; the person learns what to do about it.
	m_Device.reset();
	m_Window = nullptr;
	m_StartFailure.Problem = fmt::format("{} cannot start: no usable graphics device was found (it needs Vulkan 1.2 or later).", name);
	m_StartFailure.Advice = GraphicsDevice::GetDriverInstallAdvice();
	return false;
}

EngineFrameAction GraphicsModule::OnBeginFrame(EngineFrame& frame)
{
	if (m_Window && m_Window->IsVSync() != m_Device->IsVSync())
		m_Device->SetVSync(m_Window->IsVSync());

	// Waits for the GPU to finish an earlier frame and for the display to hand out an image.
	const double waitStart = Time::GetTime();
	const bool began = m_Device->BeginFrame();
	frame.WaitSeconds += Time::GetTime() - waitStart;
	// A device that cannot render this frame (e.g. a swapchain mid-resize) skips the whole frame.
	if (!began)
		return m_Device->IsDeviceLost() ? EngineFrameAction::Close : EngineFrameAction::Skip;
	Renderer::BeginFrame();
	PollBackBufferReadbacks();
	return EngineFrameAction::Continue;
}
```

1. **Lines 34–40:** the device is headless without a window, and validation is on by default only in Debug.
2. **Lines 42–46:** the device is created, and the swap chain only when the device can present.
3. **Lines 47–51:** `Renderer::Init` runs after the device.
4. **Lines 56–60:** after a failure the module resets the device and sets a start failure with the platform's install advice.
5. **Lines 66–77:** each frame applies vsync, begins the device, skips or closes when it cannot, then begins the renderer and polls the window readbacks.

In each frame, `OnBeginFrame` applies the window's vsync setting, calls the device's `BeginFrame` and adds the time it waited to the frame's wait time. A device that cannot begin returns `Skip` (the frame is not counted), or `Close` when the device is lost. Otherwise the module calls `Renderer::BeginFrame` and polls the window readbacks that earlier frames started.

`OnEndFrame` runs last of all modules. It prepares the back buffer, so a frame that drew nothing still presents black, then answers the back-buffer captures, starts the window readbacks asked for and presents.

`RequestBackBufferCapture` takes a callback and is safe to call from any thread. The callback runs on the main thread at the end of the next rendered frame, after the user interface (UI) is drawn and before presenting. The image comes from `Renderer::ReadTexture`. When nothing can be read (headless, a failed read or the program ending), the callback gets an empty image.

`RequestBackBufferReadback` is the form that does not block, for the main thread only (the editor uses it). It takes a region of the window and a callback that gets an image and an error. The end of the frame starts a `TextureReadback` of that region, and each later `OnBeginFrame` asks whether the copy is ready. The callback then gets the pixels, or an error when the program is headless, the GPU did not finish within 30 seconds (`c_BackBufferReadbackTimeout`) or the program is ending.

## The services of the renderer

`Renderer` is a static hub: one place where every renderer finds the device and the shared GPU services. `Renderer::Init` builds the services in dependency order, and `RendererData` declares the members in this order:

- the shader library
- the bindless table and the texture table
- the staging pool
- the upload queue, which records into the staging pool
- the upload context, which records into the upload queue
- the deferred release queue and the GPU profiler
- the geometry pool and the render scene cache

`Renderer::Shutdown` waits for the GPU to be idle and then resets the data. C++ destroys members in reverse order of declaration, so the render scene cache goes first and the shader library goes last.

The upload queue records into the staging pool, so it is destroyed before the pool. The upload context records into the queue, so it is destroyed before the queue.

The hub also holds four samplers, all made at the start: linear with clamping, linear with wrapping, linear with wrapping and a `maxAnisotropy` of 16, and point filtering with clamping. A pass picks one by name and never creates samplers of its own, so the device holds four, not hundreds.

The hub holds eight fallback textures too. A fallback stands in while the real texture loads, so a frame never waits for an asset. The eight are:

- a 1x1 white texture
- a 1x1 black texture
- a flat normal
- a black cube of 1x1 faces
- a black cube array of one cube
- a 64x64 blue noise texture
- a 1x1x1 black 3D texture
- a 1x1x1 3D texture of zeros in `R32_UINT`

All are written in one command list at the start, and three take reserved slots in the bindless table. The quote is the first part of `Renderer::Init`. Read the flat normal's comment.

```cpp src="Strata/src/Strata/Renderer/Renderer.cpp#L86-L114"
bool Renderer::Init(GraphicsDevice& device, const RendererSpecification& specification)
{
	ST_CORE_VERIFY(!s_Data, "Renderer initialized twice");
	s_Data = CreateScope<RendererData>();
	s_Data->Device = &device;
	nvrhi::IDevice* nvrhiDevice = device.GetDevice();
	s_Data->Shaders = CreateScope<ShaderLibrary>(nvrhiDevice);

	nvrhi::SamplerDesc samplerDesc;
	samplerDesc.setAllFilters(true).setAllAddressModes(nvrhi::SamplerAddressMode::Clamp);
	s_Data->LinearClamp = nvrhiDevice->createSampler(samplerDesc);
	samplerDesc.setAllAddressModes(nvrhi::SamplerAddressMode::Wrap);
	s_Data->LinearWrap = nvrhiDevice->createSampler(samplerDesc);
	samplerDesc.setMaxAnisotropy(16.0f);
	s_Data->AnisotropicWrap = nvrhiDevice->createSampler(samplerDesc);
	nvrhi::SamplerDesc pointDesc;
	pointDesc.setAllFilters(false).setAllAddressModes(nvrhi::SamplerAddressMode::Clamp);
	s_Data->PointClamp = nvrhiDevice->createSampler(pointDesc);

	nvrhi::CommandListHandle commandList = nvrhiDevice->createCommandList();
	commandList->open();
	s_Data->WhiteTexture = CreateSolidTexture(commandList, 0xFFFFFFFFu, "WhiteTexture");
	s_Data->BlackTexture = CreateSolidTexture(commandList, 0xFF000000u, "BlackTexture");
	// (0.5, 0.5, 1, 1) exactly, in half floats: in 8 bits 0.5 is 128/255, which tilted every surface without a normal map by
	// 0.3 degrees, and a mirror turned its reflected rays by twice that (a wall 10 m away lost the top 8 cm of its image in a
	// mirror floor).
	constexpr uint16_t c_FlatNormalTexel[4] = { 0x3800u, 0x3800u, 0x3C00u, 0x3C00u };
	s_Data->FlatNormalTexture = CreateSolidTexture(commandList, c_FlatNormalTexel, sizeof(c_FlatNormalTexel), nvrhi::Format::RGBA16_FLOAT, "FlatNormalTexture");
	s_Data->BlackCubeTexture = CreateSolidTexture(commandList, 0xFF000000u, "BlackCubeTexture", nvrhi::TextureDimension::TextureCube);
```

1. **Lines 96–103:** the four samplers are made from two descriptions, one of which gets `setMaxAnisotropy(16.0f)`.
2. **Lines 105–107:** one command list is opened for all the fallback textures.
3. **Lines 109–113:** the flat normal is written as exact half floats, and the comment says why 8 bits were not enough.

The flat normal stores (0.5, 0.5, 1, 1) as four half floats: `0x3800`, `0x3800`, `0x3C00` and `0x3C00`. In a half float, 0x3800 has a sign of 0, a biased :term[exponent]{id=exponent} of 14 and a :term[mantissa]{id=significand} of 0, which is 2^(14 - 15) = 0.5 exactly. 0x3C00 has an exponent of 15, which is 1.0. In 8 bits the closest value to 0.5 is 128/255 = 0.50196, and the shader's mapping 2x - 1 gives 0.0039 instead of 0. A normal of (0.0039, 0.0039, 1) leans by about 0.32 degrees, on every surface without a normal map.

`Renderer::BeginFrame` runs at the start of each frame, after the device's `BeginFrame`. It begins the profiler, the geometry pool and the render scene cache. It lets the bindless and texture tables recycle the slots of frames the GPU has finished, rolls the staging pool and the upload queue, and collects deferred releases within a budget. It then clears the flag that remembers whether the back buffer was prepared and adds one to the frame number. The order matters: the tables and the staging pool read the device's frame index, which has advanced.

```cpp src="Strata/src/Strata/Renderer/Renderer.cpp#L288-L303"
void Renderer::BeginFrame()
{
	if (!s_Data)
		return;

	s_Data->Profiler->BeginFrame();
	s_Data->Geometry->BeginFrame();
	s_Data->SceneGPUs->BeginFrame();
	s_Data->BindlessTextures->BeginFrame(s_Data->Device->GetFrameIndex());
	s_Data->Textures->BeginFrame(s_Data->Device->GetFrameIndex());
	s_Data->Staging->BeginFrame(s_Data->Device->GetFrameIndex());
	s_Data->UploadQueue->BeginFrame();
	s_Data->DeferredReleases->Collect(DeferredReleaseQueue::c_FrameDestroyBudget);
	s_Data->BackBufferPrepared = false;
	s_Data->FrameNumber++;
}
```

1. **Lines 293–295:** the profiler, the geometry pool and the scene cache begin their frame.
2. **Lines 296–299:** the tables, the staging pool and the upload queue read the device's frame index.
3. **Line 300:** deferred releases are collected within `c_FrameDestroyBudget`.
4. **Lines 301–302:** the back buffer is marked as not prepared, and the frame number advances.

`GetFrameNumber` returns the frames begun so far. A renderer that wants to know whether it rendered in the previous frame stores the number at its end and compares it with the current one.

Last, `RegisterRendererModule` is the renderer's entry in the :term[composition root]{id=composition-root}. It registers the components of this area (`MeshRendererComponent`, the lights, the sky, fog, reflection probes, post-processing and `TextComponent`) and the `IAssetGraphics` service that lets the asset layer upload through the renderer. It also registers the GPU stages, the `Renderer.Quality` settings section, and the loaders for the Texture, Mesh, Material, Font and color lookup asset types, with the texture streamer. Built-in assets follow: the default material and eight primitive meshes. Only `Engine::RegisterBuiltinModules` calls it.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One backend per API, written by the engine | Engines with their own backends for Direct3D 12, Vulkan and Metal | The best use of each platform's API, no translation layer on macOS | Each rendering feature written and tested two or three times |
| A different third-party RHI | Open-source libraries that offer one set of calls over many APIs | A library with more backends, such as Direct3D | A rewrite of every call, and NVRHI's state tracking |
| Vulkan directly, with no RHI | Renderers that want every detail | No library between the engine and the API | All the barrier and state tracking, written by hand |
| A chosen adapter | Tools for machines with several GPUs | A person's choice on laptops with two GPUs | A setting, its tests and the cases where the chosen GPU fails |
| Command lists recorded on several threads | Engines that spread draw recording across cores | Less main thread time for scenes with very many draws | Locks or per-thread lists, and ordering rules for every pass |

## How it is tested

The suite `Renderer.VulkanMessages` in `StrataTests/src/Renderer/VulkanDebugMessagesTests.cpp` tests the sorting function without a GPU. Errors count with and without a message id. The bindless layout report counts unless the driver under-reports. The loader's layer errors are warnings while the instance tries the layer, and MoltenVK's blending report is traced. The suite `Renderer.GraphicsDevice` in `GraphicsDeviceTests.cpp` checks that the install advice names what to install on each platform.

Everything that needs a device lives in `GPU*` suites, which share one device through `Tests::GPUContext` and end with `CHECK(gpu.GetNewErrorCount() == 0)`. Run the unit tests of this page with `build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer*`, and the GPU ones with `ctest --preset windows-debug -L gpu`.

## Changing it safely

- **A new requirement.** Add a check to `SelectPhysicalDevice` with a `reject` that says what is missing, enable the feature in `CreateLogicalDevice`, and add a field to `GraphicsDeviceInfo` if code needs to ask. Gate on the feature, never on the operating system.
- **A new message to lower.** Add the case to `ClassifyVulkanMessage`, with the reason in a comment and a test in `Renderer.VulkanMessages` that also shows what still counts. Never hide a report you have not understood.
- **A Vulkan call outside `Platform/Vulkan`.** Do not add one. Add a function to the `GraphicsDevice` interface, and implement it in `VulkanGraphicsDevice`.
- **A wait in the frame.** Put it where the work needs it. The acquire wait belongs at the first use of the back buffer, not in `BeginFrame`.
- **A new shared service.** Add it to `RendererData` after what it depends on, so that the destruction order stays right.
- **Checks.** Run the `gpu` tests under validation, confirm that the error count stays zero, and check that none of the warnings is new.

## What went wrong before

The flat normal texture was once an 8-bit texture with the value `0x8080FF`. Every surface without a normal map leaned by 0.32 degrees, which shading hides. A mirror turns its reflected rays by twice the lean. In the test with a wall 10 m away across a mirror floor, the reflection lost the top 8 cm of the wall, 10 pixels at a width of 1,536 pixels.

The fix, in commit `1e0fa713`, stores the texture as half floats, which hold 0.5 exactly. Its regression test is in `GPU.SceneRenderer.Materials`: it compares a flat plane's normal with the geometric one, and it fails without the fix.

## Summary

- The chain is the application, the graphics module, the `GraphicsDevice` interface, `VulkanGraphicsDevice`, NVRHI, Vulkan and the driver or MoltenVK, and only `Platform/Vulkan` (with the window seam) includes Vulkan headers.
- The device skips each GPU that lacks a required feature and scores the rest: a discrete GPU adds 1,000,000, an integrated one 100,000, and each `MiB` of device-local memory adds one.
- A frame waits for the oldest event query when the frames in flight are full, then acquires an image. The GPU waits for that image only at the back buffer's first use, and the frame presents through an empty submission.
- An NVRHI texture or buffer comes from a description: its size, format and uses, its CPU access, its initial state kept, and a debug name.
- The `Renderer` creates its services in dependency order, destroys them in reverse, holds four samplers and eight fallback textures, and runs its frame begin right after the device's.

## Check yourself

1. A laptop has an integrated GPU with 16,384 `MiB` and a discrete GPU with 6,144 `MiB` that lacks synchronization2. Which GPU does Strata select, and what does the log say?

   :::answer{tests="pick-gpu"}
   The discrete GPU is skipped with `GPU '<name>' skipped: no synchronization2 support`. The integrated GPU scores 16,384 + 100,000 = 116,384 and is the only candidate, so it is selected. The discrete card's size and type never matter once it fails a requirement.
   :::

2. Why does the swap chain use a UNORM format? (a) The display cannot show sRGB images. (b) The engine writes display-encoded values itself, and an sRGB image would encode them twice. (c) UNORM images are faster to present.

   :::answer{tests="device-frame"}
   The answer is (b). With an sRGB image the hardware would convert on writing, so a value the engine already encoded to 0.5 would become about 0.735. Answer (a) is wrong, because displays show sRGB images. Answer (c) is wrong, because the code's comment gives the double encoding as the reason, not speed.
   :::

3. A new file in `Strata/src/Strata/Renderer/` calls `vkCreateImage` and includes `vulkan/vulkan.h`. Which rule does this break, and what do you do instead?

   :::answer{tests="device-map"}
   The new file breaks the layer rule: only `Platform/Vulkan` includes Vulkan headers, and the Renderer layer reaches the GPU through NVRHI and the `GraphicsDevice` interface. Do not add an allowlist line. Create the image through NVRHI (`createTexture`), or add a function to the interface and implement it in `VulkanGraphicsDevice`.
   :::

4. Where does the GPU wait for the display's image, and why not in `BeginFrame`?

   :::answer{tests="device-frame"}
   The wait is submitted in `PrepareBackBuffer`, at the back buffer's first use, with the `ALL_COMMANDS` stage. A wait in `BeginFrame` would put every later submission, uploads and passes into textures included, behind the display.
   :::

5. A staging buffer is written by the CPU and read by a GPU copy. Which `cpuAccess` and `initialState` fit it, and which fit a buffer that the CPU reads after a GPU copy?

   :::answer{tests="write-desc"}
   The upload staging buffer has `CpuAccessMode::Write` and `CopySource`. The readback buffer has `CpuAccessMode::Read` and `CopyDest`. Both set `keepInitialState` to true and a debug name.
   :::

6. In which order are the shader library and the upload queue destroyed, and why does the order matter?

   :::answer{tests="renderer-services"}
   `RendererData` destroys members in reverse order of declaration, so the upload queue (declared later) goes before the shader library, which is declared first and destroyed last. The order matters because each service is destroyed before what it uses: the upload queue goes before the staging pool it records into.
   :::

## Exercises

1. **Basic.** A surface has a minimum of 3 images and a maximum of 5. Give the image count for 1, 2 and 4 frames in flight.

   :::answer[Worked solution]{tests="device-frame"}
   The count is max(3 + 1, frames + 1), limited to 5. For 1 frame: max(4, 2) = 4. For 2 frames: max(4, 3) = 4. For 4 frames: max(4, 5) = 5. Frames in flight start to matter only when they exceed the surface's own minimum.
   :::

2. **Medium.** Write a function that returns the image count and one that picks the present mode from vsync and the modes a surface offers. Test them on four surfaces.

   :::answer[Worked solution]{tests="device-frame" solution="sketches/gpu-vulkan-nvrhi-chain.cpp"}
   The first function takes the larger of the minimum plus one and the frames plus one, then caps it at the maximum when the maximum is not 0. The second returns `FIFO` with vsync on, `MAILBOX` if offered, then `IMMEDIATE`, then `FIFO`.

   ```cpp sketch="gpu-vulkan-nvrhi-chain.cpp"
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>

   // The swap chain's image count: one more than the surface's minimum and than the frames in flight, and no more than the
   // surface's maximum (0 means the surface has no maximum).
   uint32_t ChooseImageCount(uint32_t minImageCount, uint32_t maxImageCount, uint32_t framesInFlight)
   {
   	uint32_t count = std::max(minImageCount + 1, framesInFlight + 1);
   	if (maxImageCount > 0)
   		count = std::min(count, maxImageCount);
   	return count;
   }

   // 0 is first in, first out (always supported), 1 is mailbox, 2 is immediate.
   int ChoosePresentMode(bool vsync, bool hasMailbox, bool hasImmediate)
   {
   	if (vsync)
   		return 0;
   	if (hasMailbox)
   		return 1;
   	return hasImmediate ? 2 : 0;
   }

   int main()
   {
   	struct Case
   	{
   		uint32_t Min;
   		uint32_t Max;
   		uint32_t Frames;
   	};
   	const Case cases[] = { { 2, 0, 2 }, { 2, 0, 4 }, { 3, 4, 4 }, { 2, 2, 2 } };
   	for (const Case& item : cases)
   		std::printf("min %u max %u frames %u -> %u images\n", static_cast<unsigned>(item.Min), static_cast<unsigned>(item.Max),
   			static_cast<unsigned>(item.Frames), static_cast<unsigned>(ChooseImageCount(item.Min, item.Max, item.Frames)));
   	std::printf("vsync on: mode %d\n", ChoosePresentMode(true, true, true));
   	std::printf("vsync off, mailbox: mode %d\n", ChoosePresentMode(false, true, true));
   	std::printf("vsync off, only immediate: mode %d\n", ChoosePresentMode(false, false, true));
   	std::printf("vsync off, neither: mode %d\n", ChoosePresentMode(false, false, false));
   	return 0;
   }
   ```

   ```text output-of="gpu-vulkan-nvrhi-chain.cpp"
   min 2 max 0 frames 2 -> 3 images
   min 2 max 0 frames 4 -> 5 images
   min 3 max 4 frames 4 -> 4 images
   min 2 max 2 frames 2 -> 2 images
   vsync on: mode 0
   vsync off, mailbox: mode 1
   vsync off, only immediate: mode 2
   vsync off, neither: mode 0
   ```

   1. **Lines 9–12:** the larger of the two wanted counts, capped by the maximum when there is one.
   2. **Lines 16–23:** vsync gives `FIFO`; otherwise mailbox, then immediate, then `FIFO`.
   3. **Lines 37–40:** the four cases of vsync and offered modes print their mode numbers.
   :::

3. **Medium.** Trace it yourself: find which GPU Strata picks on your machine. Build the editor in Debug, set a breakpoint in the selection loop of `SelectPhysicalDevice`, and write down each GPU's score and the log lines of the ones it skipped.

   :::answer[Worked solution]{tests="pick-gpu"}
   The function is `VulkanGraphicsDevice::SelectPhysicalDevice` in `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp`. Break on the line `if (score <= bestScore)`, and read `score` for each GPU that gets there. The editor's log holds one `GPU '<name>' skipped: <reason>` line per rejected GPU, which you match to the check that failed: version, swap chain, dynamic rendering, synchronization2, descriptor indexing, the sampler feature, cube arrays or the queue. The line `Graphics device: <name> (Vulkan <version>, driver <version>)` names the winner.
   :::

4. **Hard.** The device is lost in the middle of `EndFrame`'s present. Say which functions run next, and which part of the program closes it.

   :::answer[Worked solution]{tests="device-frame"}
   `vkQueuePresentKHR` returns `VK_ERROR_DEVICE_LOST`, `EndFrame` calls `OnDeviceLost("vkQueuePresentKHR")`, which logs the critical message and sets the flag. The frame's work is finished. In the next frame `GraphicsDevice::BeginFrame` sees the flag and returns false, so `GraphicsModule::OnBeginFrame` finds `IsDeviceLost()` true and returns `EngineFrameAction::Close`. The application then ends its loop and stops its modules in reverse order.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/GraphicsDevice.h`: the interface, the specification and the information struct.
- `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp`: instance, selection, logical device, NVRHI wrap, swap chain and frame.
- `Strata/src/Platform/Vulkan/VulkanDebugMessages.cpp`, `VulkanLoader.cpp` and `VulkanPresentation.h`: the sorting function, the loader and the window seam.
- `Strata/src/Strata/Renderer/GraphicsModule.cpp` and `Renderer.cpp`: the module and the service hub. `RendererRegistration.cpp` holds `RegisterRendererModule`.
- `StrataTests/src/Renderer/VulkanDebugMessagesTests.cpp`, `GraphicsDeviceTests.cpp` and `GPUTestUtils.h`: the suites `Renderer.VulkanMessages` and `Renderer.GraphicsDevice`, and the shared `GPUContext`.

## Further reading

- The [NVRHI repository](https://github.com/NVIDIA-RTX/NVRHI) on GitHub, in its README: what the library wraps and how its command lists and state tracking work, intermediate.
- The Vulkan specification and the Vulkan Guide of the Khronos Group: the objects of this page, from instance to swap chain, advanced.
- The [Vulkan SDK page](https://vulkan.lunarg.com/sdk/home) of LunarG: the installation of the validation layer, beginner.
- Alexander Overvoorde, the Vulkan Tutorial: a first Vulkan program with the same steps as the device's start, beginner.
- The documentation of bgfx, an open-source library that offers one set of calls over many graphics APIs: the RHI approach in another project, intermediate.
