// A pretend engine file in the shape of the component registrations (tools/tests/test_reference.py).
namespace Strata
{

	namespace
	{

		std::string PerspectiveOnly(const CameraComponent& camera)
		{
			return camera.Projection == ProjectionType::Perspective ? std::string() : "The camera's projection is Orthographic";
		}

		std::string WithFocus(const CameraComponent& camera)
		{
			const std::string first = PerspectiveOnly(camera);
			if (!first.empty())
				return first;
			return camera.DepthOfField ? std::string() : "Depth Of Field is off";
		}

	}

	void RegisterSceneComponents()
	{
		ComponentRegistry::Register<IDComponent>("ID")
			.Category("Core")
			.Flags(ComponentFlags::Hidden | ComponentFlags::NoSerialize)
			.EntityProperty("ID", &IDComponent::ID, { .Flags = PropertyFlags::ReadOnly });

		ComponentRegistry::Register<CameraComponent>("Camera")
			.Category("Rendering")
			.Description("Looks at the scene")
			.Property("FieldOfView", &CameraComponent::FieldOfView)
			.Property("FocusDistance", &CameraComponent::FocusDistance)
			.CustomProperty("Cache", PropertyType::String, GetCache, SetCache, { .Flags = PropertyFlags::Transient });

		for (const char* property : { "FieldOfView" })
			ComponentRegistry::SetInactiveReason<CameraComponent>(property, &PerspectiveOnly);
		ComponentRegistry::SetInactiveReason<CameraComponent>("FocusDistance", &WithFocus);
	}

}
