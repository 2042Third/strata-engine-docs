#include <iostream>
struct Module
{
	virtual ~Module() = default;
	virtual void OnUpdate() const = 0;
};

struct Audio : Module
{
	void OnUpdate() const override { std::cout << "mixing sound\n"; }
};

struct Physics : Module
{
	void OnUpdate() const override { std::cout << "moving bodies\n"; }
};

void Run(const Module& module) { module.OnUpdate(); }

int main()
{
	Run(Audio());
	Run(Physics());
}
