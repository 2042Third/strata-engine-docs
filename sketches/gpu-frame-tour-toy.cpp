#include <cstdio>
#include <vector>

// A toy frame on a 12 by 4 screen: a prepass, a forward pass and one post pass. Reversed-Z: a larger depth is nearer,
// and the depth buffer is cleared to 0, the far plane.
namespace
{
	constexpr int c_Width = 12;
	constexpr int c_Height = 4;

	struct Quad
	{
		int X0, X1; // Columns covered, X1 exclusive
		float Depth;
		float Brightness;
	};

	struct Frame
	{
		std::vector<float> Depth = std::vector<float>(c_Width * c_Height, 0.0f);
		std::vector<float> Color = std::vector<float>(c_Width * c_Height, 0.05f); // The clear color
		int Shaded = 0; // Fragments the expensive shader ran for
	};

	enum class Mode
	{
		DepthOnly, // The prepass
		Forward,   // A forward pass that tests greater-or-equal and writes depth
		Equal      // A forward pass after a prepass: shades only where the depth is equal
	};

	// The vertex math: the same formula in both passes, or a rearranged one that is equal on paper.
	float QuadDepth(const Quad& quad, int x, bool rearranged)
	{
		const float column = static_cast<float>(x);
		return rearranged ? quad.Depth * 0.3f + 0.0003f * column : (quad.Depth + 0.001f * column) * 0.3f;
	}

	void Draw(Frame& frame, const std::vector<Quad>& quads, Mode mode, bool rearranged)
	{
		for (const Quad& quad : quads)
			for (int y = 0; y < c_Height; y++)
				for (int x = quad.X0; x < quad.X1; x++)
				{
					float& stored = frame.Depth[y * c_Width + x];
					const float depth = QuadDepth(quad, x, rearranged);
					if (mode == Mode::Equal ? depth != stored : depth < stored)
						continue;
					if (mode != Mode::Equal)
						stored = depth;
					if (mode == Mode::DepthOnly)
						continue;
					frame.Shaded++;
					frame.Color[y * c_Width + x] = quad.Brightness;
				}
	}

	void Report(const char* name, const Frame& frame)
	{
		int holes = 0;
		for (float value : frame.Color)
			holes += value == 0.05f ? 1 : 0;
		std::printf("%s %d fragments shaded, %d holes\n", name, frame.Shaded, holes);
	}
}

int main()
{
	// The far quad is drawn first, the near quad over it: the worst order for a forward pass alone.
	const std::vector<Quad> quads = { { 0, 9, 2.0f, 1.0f }, { 5, 12, 3.0f, 4.0f } };

	Frame forwardOnly;
	Draw(forwardOnly, quads, Mode::Forward, false);
	Report("forward only:        ", forwardOnly);

	Frame withPrepass;
	Draw(withPrepass, quads, Mode::DepthOnly, false);
	Draw(withPrepass, quads, Mode::Equal, false);
	Report("prepass, same math:  ", withPrepass);

	Frame mismatched;
	Draw(mismatched, quads, Mode::DepthOnly, false);
	Draw(mismatched, quads, Mode::Equal, true);
	Report("prepass, other math: ", mismatched);

	std::printf("post pass, top row:  "); // Tone mapping: x / (1 + x) maps any brightness into 0 to 1
	for (int x = 0; x < c_Width; x++)
		std::printf(" %.2f", withPrepass.Color[x] / (1.0f + withPrepass.Color[x]));
	std::printf("\n");
	return 0;
}
