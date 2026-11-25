// A toy of input actions: one Button and one Vector2, evaluated once per frame from a list of bindings.
#include <glm/glm.hpp>

#include <array>
#include <cstdio>
#include <vector>

enum class Key
{
	Space = 0,
	W,
	S,
	A,
	D
};

struct Devices
{
	std::array<bool, 5> Keys = {};
	glm::vec2 LeftStick = glm::vec2(0.0f);
};

enum class Shape
{
	Key,
	Composite2D,
	Stick
};

// Key: Keys[0]. Composite2D: up, down, left, right. Stick: the left stick.
struct Binding
{
	Shape Type = Shape::Key;
	std::array<Key, 4> Keys = {};
};

struct Action
{
	bool IsVector = false;
	float DeadZone = 0.15f;
	std::vector<Binding> Bindings;
	bool Down = false;
	bool Pressed = false;
	bool Released = false;
	glm::vec2 Value = glm::vec2(0.0f);
};

static float Read(const Devices& devices, Key key)
{
	return devices.Keys[static_cast<size_t>(key)] ? 1.0f : 0.0f;
}

static glm::vec2 ReadBinding(const Binding& binding, const Devices& devices)
{
	if (binding.Type == Shape::Stick)
		return devices.LeftStick;
	if (binding.Type == Shape::Key)
		return glm::vec2(Read(devices, binding.Keys[0]), 0.0f);
	glm::vec2 vector(Read(devices, binding.Keys[3]) - Read(devices, binding.Keys[2]), Read(devices, binding.Keys[0]) - Read(devices, binding.Keys[1]));
	const float length = glm::length(vector);
	return length > 1.0f ? vector / length : vector;
}

static glm::vec2 ApplyDeadZone(const glm::vec2& value, float deadZone)
{
	const float length = glm::length(value);
	if (!(length > deadZone))
		return glm::vec2(0.0f);
	return value / length * ((length - deadZone) / (1.0f - deadZone));
}

static void Evaluate(Action& action, const Devices& devices)
{
	const bool wasDown = action.Down;
	glm::vec2 value(0.0f);
	for (const Binding& binding : action.Bindings)
	{
		const glm::vec2 read = ReadBinding(binding, devices);
		if (glm::dot(read, read) > glm::dot(value, value))
			value = read;
	}
	if (action.IsVector)
	{
		value = ApplyDeadZone(value, action.DeadZone);
		action.Down = glm::length(value) > 0.5f;
	}
	else
	{
		action.Down = value.x > 0.0f;
		value = glm::vec2(action.Down ? 1.0f : 0.0f, 0.0f);
	}
	action.Pressed = action.Down && !wasDown;
	action.Released = !action.Down && wasDown;
	action.Value = value;
}

int main()
{
	Action jump;
	jump.Bindings.push_back({ Shape::Key, { Key::Space } });
	Action move;
	move.IsVector = true;
	move.Bindings.push_back({ Shape::Composite2D, { Key::W, Key::S, Key::A, Key::D } });
	move.Bindings.push_back({ Shape::Stick, {} });

	Devices frames[5];
	frames[1].Keys[static_cast<size_t>(Key::Space)] = true;
	frames[2].Keys[static_cast<size_t>(Key::W)] = true;
	frames[3].Keys[static_cast<size_t>(Key::W)] = true;
	frames[3].Keys[static_cast<size_t>(Key::D)] = true;
	frames[4].LeftStick = glm::vec2(0.3f, 0.4f);
	for (int frame = 0; frame < 5; frame++)
	{
		Evaluate(jump, frames[frame]);
		Evaluate(move, frames[frame]);
		std::printf("frame %d: Jump down=%d pressed=%d released=%d | Move (%.2f, %.2f) down=%d\n", frame, jump.Down, jump.Pressed, jump.Released,
			move.Value.x, move.Value.y, move.Down);
	}
	return 0;
}
