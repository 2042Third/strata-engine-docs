#pragma once
/* A pretend engine file in the shape of the script ABI (tools/tests/test_reference.py). */

#ifdef __cplusplus
extern "C" {
#endif

	/*
	 * Engine services for scripts.
	 */
	typedef struct StrataScriptHostAPI
	{
		uint32_t StructSize; /* sizeof(StrataScriptHostAPI) as built into the engine */
		uint32_t ABIVersion;

		/* Diagnostics (callable from any thread). */
		void (*Log)(uint32_t level, StrataScriptString message);

		/* Time. */
		float (*GetDeltaTime)(StrataScriptContext* context);
		uint64_t (*GetFrameIndex)(StrataScriptContext* context);
		void (*SetTimeScale)(StrataScriptContext* context, float timeScale);
	} StrataScriptHostAPI;

	typedef struct StrataScriptClassDesc
	{
		uint32_t StructSize;
		StrataScriptString Name; /* Unique within the module */

		uint32_t (*OnCreate)(StrataScriptInstance instance);
		uint32_t (*OnUpdate)(StrataScriptInstance instance, float deltaTime);
	} StrataScriptClassDesc;

#ifdef __cplusplus
}
#endif
