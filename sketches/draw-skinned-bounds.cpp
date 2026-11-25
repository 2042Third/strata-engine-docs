// A two-joint arm: its bounds before and after Sync, as RenderScene computes posed bounds.
#include <array>
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

struct Box
{
	glm::vec3 Min = glm::vec3(1.0e9f);
	glm::vec3 Max = glm::vec3(-1.0e9f);

	void Expand(const Box& other)
	{
		Min = glm::min(Min, other.Min);
		Max = glm::max(Max, other.Max);
	}

	// The box around the eight corners after the matrix moved them.
	Box Transformed(const glm::mat4& matrix) const
	{
		Box result;
		for (int corner = 0; corner < 8; corner++)
		{
			const glm::vec3 point((corner & 1) ? Max.x : Min.x, (corner & 2) ? Max.y : Min.y, (corner & 4) ? Max.z : Min.z);
			const glm::vec3 moved = glm::vec3(matrix * glm::vec4(point, 1.0f));
			result.Expand(Box { moved, moved });
		}
		return result;
	}
};

struct Skin
{
	std::array<glm::mat4, 2> InverseBindMatrices;
	std::array<Box, 2> JointBounds; // Bind-pose extent of the vertices of each joint
};

class Proxy
{
public:
	explicit Proxy(const Skin& skin)
		: m_Skin(skin)
	{
		for (const Box& box : skin.JointBounds)
			m_LocalBounds.Expand(box); // Before the first Sync: the bind pose
	}

	void Sync(const std::array<glm::mat4, 2>& pose)
	{
		m_LocalBounds = Box();
		for (size_t joint = 0; joint < 2; joint++)
		{
			const glm::mat4 palette = pose[joint] * m_Skin.InverseBindMatrices[joint];
			m_LocalBounds.Expand(m_Skin.JointBounds[joint].Transformed(palette));
		}
	}

	const Box& GetLocalBounds() const { return m_LocalBounds; }

private:
	Skin m_Skin;
	Box m_LocalBounds;
};

// Rounds to hundredths and drops the sign of zero, so that rounding noise never prints as "-0.00".
float Clean(float value)
{
	return std::round(value * 100.0f) / 100.0f + 0.0f;
}

void Print(const char* label, const Box& box)
{
	std::printf("%-10s min (%.2f, %.2f, %.2f) max (%.2f, %.2f, %.2f)\n", label, Clean(box.Min.x), Clean(box.Min.y), Clean(box.Min.z), Clean(box.Max.x),
		Clean(box.Max.y), Clean(box.Max.z));
}

int main()
{
	// The upper arm stands from the origin to y = 1, the forearm from the elbow at y = 1 to y = 2; both are 0.4 wide.
	Skin skin;
	skin.InverseBindMatrices = { glm::mat4(1.0f), glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, -1.0f, 0.0f)) };
	skin.JointBounds = { Box { glm::vec3(-0.2f, 0.0f, -0.2f), glm::vec3(0.2f, 1.0f, 0.2f) }, Box { glm::vec3(-0.2f, 1.0f, -0.2f), glm::vec3(0.2f, 2.0f, 0.2f) } };

	Proxy proxy(skin);
	Print("before", proxy.GetLocalBounds());
	for (const float degrees : { 90.0f, 180.0f })
	{
		// The elbow joint sits at (0, 1, 0) and turns about z.
		const glm::mat4 elbow = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 1.0f, 0.0f)) * glm::rotate(glm::mat4(1.0f), glm::radians(degrees), glm::vec3(0.0f, 0.0f, 1.0f));
		proxy.Sync({ glm::mat4(1.0f), elbow });
		Print(degrees == 90.0f ? "bent 90" : "folded 180", proxy.GetLocalBounds());
	}
}
