// A toy command runner: a command that cannot answer in its frame returns a poll function, polled once per frame.
#include <algorithm>
#include <cstdio>
#include <functional>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace
{
	struct Result;
	// Gets the clock in milliseconds, as the real poll gets the editor context; returns nothing while the command runs.
	using Poll = std::function<std::optional<Result>(int nowMs)>;

	struct Result
	{
		std::string Text;
		Poll Pending; // Set while the command still runs.
	};

	class Runner
	{
	public:
		void Run(const std::string& name, Result result)
		{
			if (!result.Pending)
			{
				std::printf("frame %d: %s answers %s at once\n", m_Frame, name.c_str(), result.Text.c_str());
				return;
			}
			std::printf("frame %d: %s starts and waits\n", m_Frame, name.c_str());
			m_Pending.push_back({ name, std::move(result.Pending), false });
		}

		void Update()
		{
			m_Frame++;
			m_NowMs += 16;
			// A poll may issue commands, which grow m_Pending: poll only the commands issued before this update.
			const size_t count = m_Pending.size();
			for (size_t index = 0; index < count; index++)
			{
				Poll poll = std::move(m_Pending[index].Function);
				const std::optional<Result> finished = poll(m_NowMs);
				if (!finished)
				{
					m_Pending[index].Function = std::move(poll);
					continue;
				}
				std::printf("frame %d: %s answers %s\n", m_Frame, m_Pending[index].Name.c_str(), finished->Text.c_str());
				m_Pending[index].Done = true;
			}
			std::erase_if(m_Pending, [](const Entry& entry) { return entry.Done; });
		}

		int GetNowMs() const { return m_NowMs; }

	private:
		struct Entry
		{
			std::string Name;
			Poll Function;
			bool Done;
		};

		std::vector<Entry> m_Pending;
		int m_Frame = 0;
		int m_NowMs = 0;
	};

	// Finishes at the poll that counts the last frame. The count is the poll's own copy.
	Result WaitFrames(int frames)
	{
		return { "done", [remaining = frames](int) mutable -> std::optional<Result>
		{
			if (--remaining > 0)
				return std::nullopt;
			return Result { "done", {} };
		} };
	}

	// Finishes at the first poll whose clock has reached the deadline, however long the frames are.
	Result WaitUntil(int deadlineMs)
	{
		return { "done", [deadlineMs](int nowMs) -> std::optional<Result>
		{
			if (nowMs < deadlineMs)
				return std::nullopt;
			return Result { "done", {} };
		} };
	}
}

int main()
{
	Runner runner;
	runner.Run("ping", { "pong", {} });
	runner.Run("wait 2 frames", WaitFrames(2));
	runner.Run("wait 40 ms", WaitUntil(runner.GetNowMs() + 40));
	for (int frame = 0; frame < 4; frame++)
		runner.Update();
	return 0;
}
