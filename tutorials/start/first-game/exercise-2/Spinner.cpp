// An example script. Attach it to an entity to make it spin: select the entity, Add Component > Script in the
// Inspector, and pick Spinner (or run the editor command
//   script.add {"entity": "<entity id>", "class": "Spinner", "fields": {"DegreesPerSecond": 45}}).
// Scripts see only the StrataScript SDK. How to create, build, debug and hot reload scripts, and to open them in an IDE:
// Docs/Manual/Scripting.md in the Strata engine's folder.

#include "StrataScript/StrataScript.h"

using namespace Strata;

// Turns its entity around the world's Y axis.
class Spinner : public Script
{
public:
	float DegreesPerSecond = -90.0f; // A field: editable per entity, kept across hot reloads

	void OnCreate() override
	{
		Log::Info("Spinner starts with ", DegreesPerSecond, " degrees per second");
	}

	void OnUpdate(float deltaTime) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());
	}
};

ST_SCRIPT_CLASS(Spinner)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
}
