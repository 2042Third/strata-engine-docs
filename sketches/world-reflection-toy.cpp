// A toy reflection: one registration of a component's members drives a save, a command and a file load.
#include <algorithm>
#include <cstdio>
#include <functional>
#include <string>
#include <variant>
#include <vector>

using Value = std::variant<bool, int, float>;

struct PropertyInfo
{
	std::string Name;
	float Min = 0.0f, Max = 0.0f; // a range exists only when Max > Min
	std::function<Value(const void*)> Getter;
	std::function<void(void*, const Value&)> Setter;

	bool HasRange() const { return Max > Min; }

	bool IsInRange(const Value& value) const // what a command asks: refuse, never change
	{
		const float* number = std::get_if<float>(&value);
		return !HasRange() || !number || (*number >= Min && *number <= Max);
	}

	void SetValue(void* object, Value value) const // what a file load asks: clamp, then assign
	{
		if (float* number = std::get_if<float>(&value); number && HasRange())
			*number = std::clamp(*number, Min, Max);
		Setter(object, value);
	}
};

template<typename T>
class Builder
{
public:
	explicit Builder(std::vector<PropertyInfo>& properties) : m_Properties(properties) {}

	template<typename Member>
	Builder& Property(std::string name, Member T::* member, float min = 0.0f, float max = 0.0f)
	{
		PropertyInfo& property = m_Properties.emplace_back();
		property.Name = std::move(name);
		property.Min = min;
		property.Max = max;
		property.Getter = [member](const void* object) -> Value { return static_cast<const T*>(object)->*member; };
		property.Setter = [member](void* object, const Value& value) { static_cast<T*>(object)->*member = std::get<Member>(value); };
		return *this;
	}
private:
	std::vector<PropertyInfo>& m_Properties;
};

struct Camera
{
	float FieldOfView = 60.0f;
	int Layer = 0;
	bool Primary = true;
};

int main()
{
	std::vector<PropertyInfo> properties; // the whole registration of Camera
	Builder<Camera>(properties).Property("FieldOfView", &Camera::FieldOfView, 1.0f, 179.0f).Property("Layer", &Camera::Layer).Property("Primary", &Camera::Primary);

	Camera camera;
	const PropertyInfo& fov = properties[0];
	if (!fov.IsInRange(200.0f))
		std::printf("command: refused, FieldOfView must be between 1 and 179\n");
	fov.SetValue(&camera, 200.0f);
	std::printf("file load: FieldOfView is %g\n", camera.FieldOfView);

	for (const PropertyInfo& property : properties) // a generic save: no code names Camera
	{
		const Value value = property.Getter(&camera);
		std::visit([&](auto number) { std::printf("save: %s = %g\n", property.Name.c_str(), static_cast<double>(number)); }, value);
	}
	return 0;
}
