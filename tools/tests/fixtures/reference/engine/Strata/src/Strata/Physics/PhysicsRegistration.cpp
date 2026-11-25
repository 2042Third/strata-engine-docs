// A pretend engine file: a scene system's stage and a stage timed by the macro (tools/tests/test_reference.py).
namespace Strata
{
	void RegisterPhysicsModule(SceneSystemDescriptor& descriptor)
	{
		descriptor.ProfileStage = "Scene.Physics";
	}

	void PhysicsSystem::Step()
	{
		ST_PROFILE_STAGE("Scene.Transforms");
	}
}
