// The toy with a Jump state, a transition from Any State on a trigger, and a transition without a condition.
// Any State is tried first and consumes the trigger when it fires; it skips its own target (no self transition).
#include <cstdio>

namespace
{

	enum class State { Idle, Walk, Jump };

	const char* GetName(State state)
	{
		switch (state)
		{
			case State::Idle: return "Idle";
			case State::Walk: return "Walk";
			case State::Jump: return "Jump";
		}
		return "?";
	}

	struct ToyMachine
	{
		State Current = State::Idle;
		float Speed = 0.0f;
		bool JumpTrigger = false;

		void Update()
		{
			if (JumpTrigger && Current != State::Jump)
			{
				JumpTrigger = false; // Consumed by the transition that fires
				Current = State::Jump;
				return;
			}
			if (Current == State::Idle && Speed > 0.1f)
				Current = State::Walk;
			else if (Current == State::Walk && Speed < 0.1f)
				Current = State::Idle;
			else if (Current == State::Jump)
				Current = State::Idle; // No condition, no exit time: fires in the first update
		}
	};

}

int main()
{
	ToyMachine machine;
	const bool presses[] = { false, true, true, false, false };
	int update = 1;
	for (const bool press : presses)
	{
		machine.JumpTrigger = machine.JumpTrigger || press;
		machine.Update();
		std::printf("update %d: pressed %d -> %s, trigger still set: %d\n", update++, press ? 1 : 0, GetName(machine.Current), machine.JumpTrigger ? 1 : 0);
	}
	return 0;
}
