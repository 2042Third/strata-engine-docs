#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Vertex
{
	float X = 0.0f;
	float Y = 0.0f;
	float Z = 0.0f;
	uint32_t Color = 0;
};

enum class Depth : uint8_t
{
	Tested = 0,
	OnTop
};

// Red in the lowest byte, each channel clamped to [0, 1] and rounded to a byte.
uint32_t PackColor(float red, float green, float blue, float alpha)
{
	const float channels[4] = { red, green, blue, alpha };
	uint32_t packed = 0;
	for (int index = 0; index < 4; index++)
	{
		const float clamped = std::clamp(channels[index], 0.0f, 1.0f);
		packed |= static_cast<uint32_t>(clamped * 255.0f + 0.5f) << (8 * index);
	}
	return packed;
}

// Records lines during a frame; the renderer reads them once and the owner clears them.
class LineRecorder
{
public:
	void Line(const Vertex& from, const Vertex& to, Depth depth)
	{
		std::vector<Vertex>& list = m_Lists[static_cast<size_t>(depth)];
		list.push_back(from);
		list.push_back(to);
	}

	void Clear()
	{
		m_Lists[0].clear();
		m_Lists[1].clear();
	}

	const std::vector<Vertex>& GetVertices(Depth depth) const { return m_Lists[static_cast<size_t>(depth)]; }
private:
	std::vector<Vertex> m_Lists[2];
};

// What the renderer does before the upload: one list, tested lines first, positions relative to the camera.
std::vector<Vertex> PrepareUpload(const LineRecorder& recorder, double cameraX)
{
	std::vector<Vertex> upload = recorder.GetVertices(Depth::Tested);
	const std::vector<Vertex>& onTop = recorder.GetVertices(Depth::OnTop);
	upload.insert(upload.end(), onTop.begin(), onTop.end());
	for (Vertex& vertex : upload)
		vertex.X = static_cast<float>(static_cast<double>(vertex.X) - cameraX);
	return upload;
}

int main()
{
	const uint32_t orange = PackColor(1.0f, 0.5f, 0.0f, 1.0f);
	std::printf("orange packs to %08X\n", orange);

	LineRecorder recorder;
	recorder.Line({ 5000000.5f, 2.0f, 0.0f, orange }, { 5000003.0f, 2.0f, 0.0f, orange }, Depth::OnTop);
	recorder.Line({ 5000001.0f, 0.0f, 0.0f, orange }, { 5000001.0f, 4.0f, 0.0f, orange }, Depth::Tested);
	std::printf("tested vertices: %zu, on top: %zu\n", recorder.GetVertices(Depth::Tested).size(), recorder.GetVertices(Depth::OnTop).size());

	const std::vector<Vertex> upload = PrepareUpload(recorder, 5000000.0);
	for (const Vertex& vertex : upload)
		std::printf("x = %.1f\n", vertex.X);

	const float far = 5000000.5f;
	std::printf("floats near %.1f are %.7f apart\n", far, std::nextafter(far, 1.0e9f) - far);
	std::printf("floats near 2.5 are %.7f apart\n", std::nextafter(2.5f, 1.0e9f) - 2.5f);
	recorder.Clear();
	std::printf("after Clear: %zu vertices\n", recorder.GetVertices(Depth::Tested).size() + recorder.GetVertices(Depth::OnTop).size());
	return 0;
}
