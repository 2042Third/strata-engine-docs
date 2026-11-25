// A toy script boundary: a host table that grows at its end, a class descriptor with null callbacks, and a module that
// fills a description no larger than the engine's struct holds.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>

#define TOY_HAS_MEMBER(type, pointer, member) \
	((pointer)->StructSize >= offsetof(type, member) + sizeof(((type*)0)->member))

struct ToyHostAPI
{
	uint32_t StructSize;
	void (*Log)(const char* text);
	float (*GetTime)();
	float (*GetScale)(); // Appended after the first release
};

struct ToyClassDesc
{
	uint32_t StructSize;
	const char* Name;
	void (*OnCreate)();
	void (*OnUpdate)(float deltaTime);
};

struct ToyModuleAPI
{
	uint32_t StructSize;
	uint32_t ClassCount;
	const ToyClassDesc* const* Classes;
};

namespace
{

	const ToyHostAPI* s_Host = nullptr;

	void SpinnerUpdate(float deltaTime)
	{
		s_Host->Log("Spinner update");
		float scale = 1.0f;
		if (TOY_HAS_MEMBER(ToyHostAPI, s_Host, GetScale) && s_Host->GetScale)
			scale = s_Host->GetScale();
		std::printf("turned %.2f degrees at time %.1f\n", 90.0f * deltaTime * scale, s_Host->GetTime());
	}

	const ToyClassDesc c_Spinner = { sizeof(ToyClassDesc), "Spinner", nullptr, &SpinnerUpdate };
	const ToyClassDesc* const c_Classes[] = { &c_Spinner };

}

void ModuleLoad(const ToyHostAPI* host, ToyModuleAPI* outModule)
{
	s_Host = host;
	const ToyModuleAPI description = { sizeof(ToyModuleAPI), 1, c_Classes };
	const uint32_t capacity = outModule->StructSize;
	std::memcpy(outModule, &description, capacity < sizeof(description) ? capacity : sizeof(description));
	outModule->StructSize = sizeof(description);
}

void EngineLog(const char* text) { std::printf("[log] %s\n", text); }
float EngineTime() { return 12.5f; }
float EngineScale() { return 2.0f; }

int main()
{
	ToyHostAPI host = { static_cast<uint32_t>(offsetof(ToyHostAPI, GetScale)), &EngineLog, &EngineTime, nullptr };
	for (int release = 1; release <= 2; release++)
	{
		if (release == 2)
		{
			host.StructSize = sizeof(ToyHostAPI);
			host.GetScale = &EngineScale;
		}
		ToyModuleAPI module = {};
		module.StructSize = sizeof(ToyModuleAPI);
		ModuleLoad(&host, &module);
		const ToyClassDesc* desc = module.Classes[0];
		std::printf("engine %d: %s, OnCreate %s, OnUpdate %s\n", release, desc->Name, desc->OnCreate ? "set" : "null", desc->OnUpdate ? "set" : "null");
		if (desc->OnUpdate)
			desc->OnUpdate(0.5f);
	}
	return 0;
}
