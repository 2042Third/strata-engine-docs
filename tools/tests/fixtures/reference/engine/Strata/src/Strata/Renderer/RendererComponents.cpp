// A pretend engine file: inactive reasons through a helper template (tools/tests/test_reference.py).
namespace Strata
{

	namespace
	{

		template<typename T>
		void SetInactiveReasons(std::initializer_list<const char*> properties, std::string (*reason)(const T&))
		{
			for (const char* property : properties)
				ComponentRegistry::SetInactiveReason<T>(property, reason);
		}

		template<typename Value, Value TemporalSettings::*Field>
		std::string WithCustomTunable(const PostProcessComponent& post)
		{
			return post.Custom ? std::string() : fmt::format("Only a Custom preset uses it (the preset is {})", post.Preset);
		}

		std::string WithBloom(const PostProcessComponent& post)
		{
			return post.Bloom ? std::string() : "Bloom is off";
		}

	}

	void RegisterRendererComponents()
	{
		ComponentRegistry::Register<PostProcessComponent>("PostProcess")
			.DisplayName("Post Process")
			.Category("Rendering")
			.Property("Bloom", &PostProcessComponent::Bloom)
			.Property("BloomIntensity", &PostProcessComponent::BloomIntensity)
			.Property("HistoryFrames", &PostProcessComponent::HistoryFrames);

		SetInactiveReasons<PostProcessComponent>({ "BloomIntensity" }, &WithBloom);
		SetInactiveReasons<PostProcessComponent>({ "HistoryFrames" }, &WithCustomTunable<uint32_t, &TemporalSettings::HistoryFrames>);
	}

}
