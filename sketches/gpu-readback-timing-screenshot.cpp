#include <cstdint>
#include <cstdio>
#include <optional>

namespace
{
	constexpr uint32_t c_GPUFrames = 3; // Frames the pretend GPU needs to finish one copy

	struct Readback
	{
		uint32_t IssuedFrame = 0;

		bool IsReady(uint32_t frame) const { return frame >= IssuedFrame + c_GPUFrames; }
	};

	// Request starts one readback; Update polls it once per frame and never waits.
	class ScreenshotTool
	{
	public:
		bool Request(uint32_t frame)
		{
			if (m_Pending)
				return false;
			m_Pending = Readback { frame };
			return true;
		}

		void Update(uint32_t frame)
		{
			if (!m_Pending || !m_Pending->IsReady(frame))
				return;
			std::printf("frame %u: saved the screenshot of frame %u\n", frame, m_Pending->IssuedFrame);
			m_Pending.reset();
		}
	private:
		std::optional<Readback> m_Pending;
	};
}

int main()
{
	ScreenshotTool tool;
	for (uint32_t frame = 0; frame < 8; frame++)
	{
		if ((frame == 2 || frame == 3) && !tool.Request(frame))
			std::printf("frame %u: a screenshot is still pending\n", frame);
		tool.Update(frame);
		std::printf("frame %u: drawn\n", frame);
	}
}
