#include <cstdint>
#include <cstdio>
#include <map>
#include <mutex>
#include <string>
#include <string_view>
#include <vector>

enum class ShaderStage
{
	None,
	Vertex,
	Pixel,
	Compute
};

// What the build would generate: a name and the words of its module.
struct EmbeddedShader
{
	std::string_view Name;
	std::vector<uint32_t> Words;
};

static const std::vector<EmbeddedShader> s_Registry = {
	{ "PostProcess/Fullscreen.vert", { 0x07230203, 0x00010500, 1, 2, 3 } },
	{ "Toy/Gradient.frag", { 0x07230203, 0x00010500, 4, 5 } },
};

class ToyShaderLibrary
{
public:
	static ShaderStage GetStageFromName(std::string_view name)
	{
		auto endsWith = [name](std::string_view suffix)
		{
			return name.size() >= suffix.size() && name.substr(name.size() - suffix.size()) == suffix;
		};
		if (endsWith(".vert"))
			return ShaderStage::Vertex;
		if (endsWith(".frag"))
			return ShaderStage::Pixel;
		if (endsWith(".comp"))
			return ShaderStage::Compute;
		return ShaderStage::None;
	}

	// Returns the stage of the named shader, or None when the name is unknown.
	ShaderStage Get(std::string_view name)
	{
		std::scoped_lock<std::mutex> lock(m_Mutex);
		auto cached = m_Stages.find(std::string(name));
		if (cached != m_Stages.end())
			return cached->second;

		for (const EmbeddedShader& embedded : s_Registry)
		{
			if (embedded.Name != name)
				continue;
			m_Created++;
			return m_Stages.emplace(std::string(name), GetStageFromName(name)).first->second;
		}
		return ShaderStage::None;
	}

	int GetCreatedCount() const { return m_Created; }

private:
	std::mutex m_Mutex;
	std::map<std::string, ShaderStage> m_Stages;
	int m_Created = 0;
};

int main()
{
	ToyShaderLibrary library;
	const char* names[] = { "PostProcess/Fullscreen.vert", "PostProcess/Fullscreen.vert", "Toy/Missing.frag" };
	for (const char* name : names)
	{
		const ShaderStage stage = library.Get(name);
		std::printf("%s: stage %d, objects created so far: %d\n", name, static_cast<int>(stage), library.GetCreatedCount());
	}
	return 0;
}
