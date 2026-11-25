#include <cstdio>
#include <memory>
#include <string>
#include <utility>
#include <vector>

struct Script
{
	virtual ~Script() = default;
	virtual void OnUpdate(float deltaTime) = 0;
};

struct Spinner : Script
{
	float Angle = 0.0f;
	void OnUpdate(float deltaTime) override
	{
		Angle += 90.0f * deltaTime;
		std::printf("Spinner at %.1f degrees\n", Angle);
	}
};

struct Logger : Script
{
	void OnUpdate(float) override { std::printf("Logger ran\n"); }
};

std::unique_ptr<Script> Create(const std::string& className)
{
	if (className == "Spinner")
		return std::make_unique<Spinner>();
	if (className == "Logger")
		return std::make_unique<Logger>();
	return nullptr;
}

int main()
{
	const std::vector<std::string> entries = { "Spinner", "Logger", "Missing" };
	std::vector<std::unique_ptr<Script>> instances;
	for (const std::string& className : entries)
	{
		std::unique_ptr<Script> instance = Create(className);
		if (instance)
			instances.push_back(std::move(instance));
		else
			std::printf("No class named %s\n", className.c_str());
	}
	for (int step = 0; step < 2; ++step)
		for (const std::unique_ptr<Script>& instance : instances)
			instance->OnUpdate(0.5f);
}
