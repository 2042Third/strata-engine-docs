// The Hard exercise: a counter that never reaches 10, because a callback that runs every frame sets it back to zero.
#include <cstdio>

struct Playground
{
	int Counter = 0;
	void OnUpdate()
	{
		Counter++;
		std::printf("counter %d\n", Counter);
		if (Counter == 10)
			std::printf("ten frames reached\n");
	}
	void OnLateUpdate() { Counter = 0; } // meant to run once, in OnCreate
};

int main()
{
	Playground script;
	for (int frame = 1; frame <= 12; frame++)
	{
		script.OnUpdate();
		script.OnLateUpdate();
	}
}
