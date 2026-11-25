// A toy state machine: two states, one float parameter, two transitions. One update checks the current state's
// transitions in order, and the first whose condition holds fires; at most one fires per update.
#include <cstddef>
#include <cstdio>
#include <string>
#include <utility>
#include <vector>

namespace
{

	enum class Mode { Greater, Less };

	struct Transition
	{
		size_t From = 0;
		size_t To = 0;
		Mode Test = Mode::Greater;
		float Threshold = 0.0f;
	};

	class ToyMachine
	{
	public:
		ToyMachine(std::vector<std::string> states, std::vector<Transition> transitions)
			: m_States(std::move(states)), m_Transitions(std::move(transitions))
		{
		}

		void Update(float speed)
		{
			for (const Transition& transition : m_Transitions)
			{
				if (transition.From != m_Current)
					continue;
				const bool holds = transition.Test == Mode::Greater ? speed > transition.Threshold : speed < transition.Threshold;
				if (!holds)
					continue;
				m_Current = transition.To;
				return;
			}
		}

		const std::string& GetCurrentName() const { return m_States[m_Current]; }

	private:
		std::vector<std::string> m_States;
		std::vector<Transition> m_Transitions;
		size_t m_Current = 0;
	};

}

int main()
{
	ToyMachine machine({ "Idle", "Walk" }, { { 0, 1, Mode::Greater, 0.1f }, { 1, 0, Mode::Less, 0.1f } });
	const float speeds[] = { 0.0f, 0.05f, 2.0f, 2.0f, 0.1f, 0.08f };
	int update = 1;
	for (const float speed : speeds)
	{
		machine.Update(speed);
		std::printf("update %d: Speed %.2f -> %s\n", update++, speed, machine.GetCurrentName().c_str());
	}
	return 0;
}
