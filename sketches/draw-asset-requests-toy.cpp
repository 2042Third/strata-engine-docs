#include <cstdio>
#include <string>
#include <unordered_map>

// A slow lookup that stands for the asset manager: it counts how often it is asked.
class SlowManager
{
public:
	std::string Get(int handle)
	{
		m_Calls++;
		return "asset" + std::to_string(handle);
	}

	int GetCalls() const { return m_Calls; }
private:
	int m_Calls = 0;
};

// Answers each handle once per frame and forgets everything when the frame ends.
class FrameMemo
{
public:
	void BeginFrame(SlowManager* manager) { m_Manager = manager; }

	void EndFrame()
	{
		m_Answers.clear();
		m_Manager = nullptr;
	}

	const std::string& Resolve(int handle)
	{
		auto found = m_Answers.find(handle);
		if (found == m_Answers.end())
			found = m_Answers.insert({ handle, m_Manager->Get(handle) }).first;
		return found->second;
	}
private:
	SlowManager* m_Manager = nullptr;
	std::unordered_map<int, std::string> m_Answers;
};

int main()
{
	SlowManager manager;
	FrameMemo memo;

	const int frames[2][6] = { { 1, 2, 1, 3, 2, 1 }, { 1, 1, 1, 1, 1, 1 } };
	for (int frame = 0; frame < 2; frame++)
	{
		const int before = manager.GetCalls();
		memo.BeginFrame(&manager);
		for (const int handle : frames[frame])
			memo.Resolve(handle);
		memo.EndFrame();
		std::printf("frame %d: 6 lookups, %d manager calls\n", frame + 1, manager.GetCalls() - before);
	}
	return 0;
}
