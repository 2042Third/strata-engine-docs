---
id: world/reflection
title: "Reflection: one registration, many uses"
description: "How one registration of a component's fields, limits and rules drives Strata's files, Inspector, commands, undo, scripts, cooking and prefab differences."
kind: internals
size: XL
tracks: [E]
needs: [world/ecs, basics/cpp-modern, basics/data-formats, core/layers-registries]
time: 130
learn:
  - id: register
    text: write a component registration with properties, ranges and descriptive text
  - id: mechanism
    text: explain how Register fills the type-erased operations of a component from one template
  - id: paths
    text: predict what a file, a command and the Inspector each do with a value out of range
  - id: requirements
    text: trace how AddComponent adds required components first and ends a cycle
  - id: bypass
    text: name the code paths that bypass reflection and what a field that is not registered costs
since: 0.3.0
status: final
---

A camera has a field of view, a near plane, a far plane and a dozen other fields. At least seven parts of the engine need to know them:

- the code that saves and loads a scene;
- the Inspector;
- the commands an agent sends;
- the undo stack;
- the scripts;
- the cooker that packs a scene for shipping;
- the comparison of a prefab instance with its prefab.

Strata gives each component type one description of its fields, their limits and its rules, and all seven read that description. This page is about the description, the code that builds it (`ComponentRegistry`, `ComponentInfo`, `PropertyInfo` and their builders) and `ComponentAccess`, the path that reads and writes through it. It does not cover how registries open, accept and freeze in general ([Layers and registries](../core/layers-registries.md) does), how the Inspector draws a property, or how a command checks its parameters against a schema.

## The problem and how engines solve it

Start with the camera and count. Suppose the engine has 40 component types, a figure close to the 44 registrations in the engine's module sources. Suppose each of the seven parts writes its own code for each type: 40 times 7 is 280 pieces of code, and every new field touches seven of them. Forget one and a field is saved but never shown, or shown but never undone. The bugs are silent, because each piece compiles on its own.

:::example[Counting what one field costs]
Add a field such as `Lens Shift` to the camera. By hand, you edit seven places: the scene files, the Inspector, the command that sets values, the undo snapshot, the script interface, the cooker and the prefab comparison. No tool checks the seven against each other. With a shared description you add one line to the camera's registration, and all seven places change together. The cost moved from every consumer to one description that you must write correctly.
:::

The :term[compiler]{id=compiler} knows every field of the camera, but the finished program keeps no list of them. A program that can list the fields of a type, and read or write them by name, has **reflection**. Some languages build it in. C++ at the standard Strata uses, C++20, has none, so an engine adds it, and the engines that do differ in who writes the list.

| Approach | How the list of fields appears | Main cost |
| --- | --- | --- |
| Marked fields and a generator | You mark fields with :term[macros]{id=macro}. A tool reads the :term[headers]{id=header} before the build and writes code that holds the list. | A second program in every build, and the marks must match the generator's rules. |
| A separate tool reading the headers | A tool parses the source and writes tables. Nothing in the source is marked, or the marks are comments. | The tool needs a full C++ :term[parser]{id=parser}, which is large and slow to keep current. |
| Registration in C++ | You write the list as C++ code in one place, with calls that name each field. Templates supply the details. | You must keep the list in step with the :term[struct]{id=struct} by hand. |

:::elsewhere[Reflection in other engines and libraries]
Unreal Engine uses the first approach: its Unreal Header Tool reads macros such as `UPROPERTY` and writes the generated code. The meta-object compiler of `Qt` works the same way for the types of `Qt`. `RTTR` (Run Time Type Reflection) and EnTT's `meta` module use the third approach: you register a type and its members at run time with calls in C++. The Further reading section names the sources.
:::

Strata uses the third approach and adds no tool. The cost is the last cell of the table: nothing forces you to register a field. [A field that is not registered](#a-field-that-is-not-registered) shows the cost, and the tests below check the engine's own components against a snapshot. The gain is that the engine has no generator step, a registration is plain C++ that a debugger steps through, and the list is data in memory that every consumer can read.

## How the parts fit

The description has three levels. `ComponentRegistry` is a static class that holds one `ComponentInfo` for each component type. A `ComponentInfo` holds the type's name, data about it, a list of `PropertyInfo` and a set of type-erased operations: functions that add, find or copy the component without naming its C++ type. A `PropertyInfo` describes one field: its name, type, range and flags, and two functions that read and write the field through a `void` pointer. [Templates and type erasure](../basics/cpp-generic.md) teaches the C++ used here; this page applies it.

```mermaid caption="One registry holds one description for each component type, and each description holds its properties. The consumers read the descriptions and never name a component type." alt="A box for the registry points to a box for one component description, which points to a box for its properties. Seven boxes stand around them, one for each consumer: scene files, the Inspector, commands, undo, scripts, cooked scenes and prefab differences. Each consumer has an arrow to the component description."
flowchart LR
    R["Registry of components"]
    C["One description per component: name, details, operations"]
    P["Its properties: name, type, range, flags, read and write functions"]
    R --> C --> P
    F["Scene files"] --> C
    I["Inspector"] --> C
    M["Commands"] --> C
    U["Undo"] --> C
    S["Scripts"] --> C
    K["Cooked scenes"] --> C
    D["Prefab differences"] --> C
```

Each consumer reaches the description through a few functions of `ComponentAccess`, the checked path that a later section describes.

| Consumer | What it calls |
| --- | --- |
| Scene files | `Serialize` to write a component, `Deserialize` to read it |
| Inspector | `SetProperty`, `GetProperty` and `GetInactiveReason` |
| Commands | The range check `IsInRange`, then `Deserialize` |
| Undo | `SerializeEntityComponents` to record an entity, `Deserialize` to restore it |
| Scripts | `GetProperty`, `SetProperty`, `AddComponent` and `RemoveComponent` |
| Cooked scenes | The list of properties, with `GetValue` and the binary form of each value |
| Prefab differences | `Serialize` and `Deserialize` |

Files, undo and prefab differences read forgivingly. Commands read strictly, and the Inspector and scripts write through `SetProperty`, which clamps. [Validation, clamping and refusal](#validation-clamping-and-refusal) shows each difference.

The code lives in two places. `Strata/src/Strata/Reflection/` holds the types and builders, which know nothing about scenes: `Property.h`, `PropertyBuilder.h`, `PropertyOptions.h`, `ComponentRegistry.h` and `PropertyJson.h`. `Strata/src/Strata/Scene/ComponentAccess.h` holds the checked path, because it works on an `Entity`. Each :term[engine module]{id=engine-module} registers its own components in its own folder, and the :term[composition root]{id=composition-root} calls each module's registration function in a fixed order, which also fixes the order of `GetAll`.

The :term[main thread]{id=main-thread} owns the scene, so the registry is built on the main thread. While it is open, one thread registers. Once it is frozen, nothing changes, and any thread, including a job on a worker, may read it without a lock. That promise is the reason registration has a window at all.

## What callers may assume, and must do

Code that uses the registry may rely on five things.

- A pointer from `Find`, `FindByTypeId` or `GetAll` stays valid for the life of the program, and after the freeze the set never changes.
- `GetAll` lists components in registration order, and the composition root's module table fixes that order: Input, Scene, :term[Renderer]{id=renderer}, then the others.
- Lookups by name ignore case, for components (`Find`) and for properties (`FindProperty`).
- `PropertyInfo::SetValue` leaves the object unchanged when it returns false.
- `ComponentAccess::SetProperty` signals the change after it writes.

Code that registers or writes must follow six rules, each with its reason.

1. Register components only while the registry is open. The freeze lets workers read without a lock, and a late registration is refused with an error.
2. Never rename a registered component or property. The names are the keys of every saved scene and of every command, so a renamed field loads as an unknown one and its saved values are lost.
3. Choose ranges that make a bad state impossible. One range protects every path: files clamp, commands refuse, and scripts and the Inspector clamp.
4. Give data that is not a property a description of its references (`ExtraReferences`). Without it, a copied entity keeps pointing at the original, and an export drops the assets that only that data names.
5. Let a property that another property disables say why, through an inactive reason.
6. Engine code that writes a field directly, outside this path, signals the change itself.

:::rule[Register components through the module system]
Each module has one registration function, called only by the composition root; games and tests pass theirs as extras. The reason is the freeze: components registered anywhere else could arrive after it. [Layers and registries](../core/layers-registries.md) explains the composition root.
:::

:::rule[A property that another property disables gets an inactive reason]
Without one, people and agents edit a value that does nothing. The camera's registration shows the pattern, and [Requirements and inactive reasons](#requirements-and-inactive-reasons) teaches it.
:::

## A toy version

Before the real code, here is a toy that does the job in 80 lines. It registers a `Camera` with three fields through a builder that works out each field's type from a member pointer. Then it asks the one description what a command and a file load do with a field of view of 200. A generic save then writes the camera without naming its type. Notice the two functions `IsInRange` and `SetValue`, which answer the first two questions differently on purpose.

```cpp sketch="world-reflection-toy.cpp"
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
```

```text output-of="world-reflection-toy.cpp"
command: refused, FieldOfView must be between 1 and 179
file load: FieldOfView is 179
save: FieldOfView = 179
save: Layer = 0
save: Primary = 1
```

1. **Line 9:** a `std::variant` holds a value of any property type, so one `Getter` signature serves every field.
2. **Lines 15–16:** the read and write functions take `void` pointers, so a property of `Camera` and one of any other type have the same shape and fit in one vector.
3. **Lines 40–48:** the member pointer fixes the type of the field, and two :term[lambdas]{id=lambda} capture it; the `static_cast` back to `T` is safe because only this builder creates them.
4. **Lines 20–31:** a command asks `IsInRange` and refuses, a file load calls `SetValue` and gets a clamped value.
5. **Lines 74–78:** the save loop reads every property through its `Getter` and never names `Camera`.

The toy shows the whole idea. The engine adds what a real program needs. It has 14 property types instead of three, flags and sections, a registry with states, type-erased operations for storage, text in :term[JSON]{id=json} and requirements between components.

## Properties: types, values and flags

A **property** is a field of a component that reflection describes: its name, type, limits and flags, and the functions that read and write it. The type of a property is one of 14 values of `PropertyType` in `Strata/src/Strata/Reflection/Property.h`: `Bool`, `Int`, `UInt`, `Float`, `Vec2`, `Vec3`, `Vec4`, `Quat`, `Color3`, `Color4`, `String`, `Enum`, `Asset` and `Entity`. The value of any property travels as a `PropertyValue`, a `std::variant` of ten alternatives: `bool`, `int32_t`, `uint32_t`, `float`, the three glm vectors, the glm quaternion, `std::string` and `UUID`.

Fourteen types share ten alternatives because some types only differ in meaning. A `Color3` is a `glm::vec3` that the Inspector draws as a color picker. An `Enum` is an `int32_t` with named options. An `Asset` and an `Entity` are both a `UUID`, one naming an asset and the other an entity. `GetPropertyValueIndex` maps a type to its alternative, and a run of `static_assert` lines in `Property.cpp` pins the order, because the mapping depends on it.

`PropertyInfo` carries more than the type:

- the name, the stable key in files and commands;
- a display name for the Inspector, a hint text (`Tooltip`) and a section, the group the Inspector shows the property under;
- the type, the flags, a minimum and a maximum, and a drag speed;
- an asset filter for asset properties and the named options of an enum;
- the `Getter` and `Setter` functions;
- the inactive reason, which a later section teaches.

The range is enforced only when the maximum is larger than the minimum, so `Range(0.0f, 0.0f, 0.05f)` sets only a drag speed. The transform's `Translation` is registered that way. The display name defaults to the name split into words: `PascalCaseToDisplayName` turns `HalfExtents` into `Half Extents` and `PerspectiveFOV` into `Perspective FOV`, and it keeps a run of capitals together.

`PropertyFlags` has seven bits. `ReadOnly` means the property is visible but the Inspector, commands and scripts cannot change it. `Hidden` hides it from the Inspector but still saves it. `Transient` keeps it out of files, which suits :term[runtime]{id=runtime} state.

`MultiLine` edits a string in a larger box, and `Slider` edits a number with a slider over its range. `PowerOfTwoLimit` chooses an unsigned limit among the powers of two. `PhysicsLayer` chooses a collision layer by its name.

`PropertyOptions` is what a registration passes with each property. Its fields mirror `PropertyInfo`, and four helpers in `PropertyOptions.h` build one: `Range(min, max, speed)`, `Slider(min, max)`, `Color()` and `WithTooltip(options, text)`. The same file holds the constant `c_Unbounded`. The constant is a million. It is the bound of a range that exists only to keep a value finite, such as a light's intensity.

## The builder: a type from a member pointer

A registration is a chain of calls: `Property("PerspectiveFOV", &CameraComponent::PerspectiveFOV, Range(1.0f, 179.0f))`. The second argument is a :term[pointer to a member]{id=pointer-to-a-member}, and the compiler knows its type, so you never state it. A function in `PropertyBuilder.h` turns that type into a `PropertyType`.

```cpp src="Strata/src/Strata/Reflection/PropertyBuilder.h#L17-L40"
template<typename Member>
constexpr PropertyType DeducePropertyType(bool color)
{
	if constexpr (std::is_same_v<Member, bool>)
		return PropertyType::Bool;
	else if constexpr (std::is_same_v<Member, int32_t>)
		return PropertyType::Int;
	else if constexpr (std::is_same_v<Member, uint32_t>)
		return PropertyType::UInt;
	else if constexpr (std::is_same_v<Member, float>)
		return PropertyType::Float;
	else if constexpr (std::is_same_v<Member, glm::vec2>)
		return PropertyType::Vec2;
	else if constexpr (std::is_same_v<Member, glm::vec3>)
		return color ? PropertyType::Color3 : PropertyType::Vec3;
	else if constexpr (std::is_same_v<Member, glm::vec4>)
		return color ? PropertyType::Color4 : PropertyType::Vec4;
	else if constexpr (std::is_same_v<Member, glm::quat>)
		return PropertyType::Quat;
	else if constexpr (std::is_same_v<Member, std::string>)
		return PropertyType::String;
	else
		static_assert(sizeof(Member) == 0, "Unsupported property member type (use EnumProperty, AssetProperty or EntityProperty)");
}
```

1. **Line 18:** the function is `constexpr` and runs at :term[compile time]{id=compile-time}; its argument says whether a vector member is a color.
2. **Lines 20–37:** `if constexpr` keeps only the branch for the member's type, so a `float` member never compiles the `vec3` branch.
3. **Lines 30–31:** the same `glm::vec3` becomes `Vec3` or `Color3` depending on the option, because the type alone cannot tell them apart.
4. **Line 39:** a member type with no branch fails to compile, and the message names the three calls for enums, assets and entities.

The builder that calls this function is a class template with an unusual second parameter.

```cpp src="Strata/src/Strata/Reflection/PropertyBuilder.h#L57-L65"
template<typename Member>
Derived& Property(std::string name, Member T::* member, const PropertyOptions& options = {})
{
	PropertyInfo& property = AddProperty();
	Detail::ApplyPropertyOptions(property, name, Detail::DeducePropertyType<Member>(options.Color), options);
	property.Getter = [member](const void* object) -> PropertyValue { return static_cast<const T*>(object)->*member; };
	property.Setter = [member](void* object, const PropertyValue& value) { static_cast<T*>(object)->*member = std::get<Member>(value); };
	return Self();
}
```

`PropertyBuilderBase<T, Derived>` takes the concrete builder as `Derived`, which is the :term[curiously recurring template pattern]{id=crtp}, and every call returns `Derived&` through `Self()`. That is why a chain such as `.Category("Rendering").Property(...)` compiles: `Property` returns the full `ComponentInfoBuilder`, so `Category` is still available after it. `Property` makes a `PropertyInfo`, fills it from the options, and stores two functions, one that reads and one that writes, which capture the member pointer. The `Setter` calls `std::get<Member>`, which throws if the variant holds another type, so `SetValue` checks the type first.

Five more calls cover what a plain member cannot. `EnumProperty` takes an enum member and its named options, and stores the value as an `int32_t`. `AssetProperty` takes a `UUID` member and the asset type it accepts. `EntityProperty` takes a `UUID` member that names an entity. `CustomProperty` takes a type and two functions, one that reads and one that writes, for a value that no member holds.

`Section` sets the group of every property registered after it; a registration may return to an earlier section, and editors draw sections in the order of their first property.

`PropertyListBuilder<T>` is the same builder with no component around it. Materials use it to list their parameters, which are plain structs and not components.

## ComponentInfo and the code Register fills

A **ComponentInfo** is the description of one component type: data about it, its properties and about twenty type-erased operations that work on an EnTT registry without naming the type. The data about the type is `Name`, `DisplayName`, `Category`, `Description`, `Flags`, the type's :term[hash]{id=hash}, its size and the list of properties. The operations are functions such as `Has`, `Get`, `Add`, `Remove`, `MarkModified`, `Copy`, `CopyStorage`, `Observe` and `SerializeExtra`. Beside them, `Requires` is a list of the names of the components it needs.

Why erase the type? Code that loops over all components, such as the Inspector or the scene writer, holds a `const ComponentInfo*` and not a `T`. It cannot call `registry.get<T>` because it does not know `T`. So each operation is a `std::function` that was made inside a template where `T` was known and that casts the `void` pointer back. `Register<T>` creates all of them in one place.

```cpp src="Strata/src/Strata/Reflection/ComponentRegistry.h#L383-L423"
ComponentInfoBuilder<T> ComponentRegistry::Register(std::string name)
{
	ComponentInfo* registered = CreateInfo(std::move(name), entt::type_id<T>().hash());
	if (!registered)
		return ComponentInfoBuilder<T>(nullptr);

	ComponentInfo& info = *registered;
	info.Size = std::is_empty_v<T> ? 0 : sizeof(T);
	info.Has = [](const entt::registry& registry, entt::entity entity) { return registry.all_of<T>(entity); };
	if constexpr (std::is_empty_v<T>)
	{
		// Tag components have no storage; a shared instance stands in so callers can treat "non-null" as "present".
		info.Get = [](entt::registry& registry, entt::entity entity) -> void*
		{
			static T s_Instance;
			return registry.all_of<T>(entity) ? &s_Instance : nullptr;
		};
		info.Add = [](entt::registry& registry, entt::entity entity) -> void*
		{
			static T s_Instance;
			if (!registry.all_of<T>(entity))
				registry.emplace<T>(entity);
			return &s_Instance;
		};
		info.MarkModified = [](entt::registry&, entt::entity) {};
	}
	else
	{
		info.Get = [](entt::registry& registry, entt::entity entity) -> void* { return registry.try_get<T>(entity); };
		info.Add = [](entt::registry& registry, entt::entity entity) -> void*
		{
			if (T* existing = registry.try_get<T>(entity))
				return existing;
			return &registry.emplace<T>(entity);
		};
		info.MarkModified = [](entt::registry& registry, entt::entity entity)
		{
			if (registry.all_of<T>(entity))
				registry.patch<T>(entity);
		};
	}
```

1. **Line 385:** `CreateInfo` may refuse, for a frozen registry, an empty or taken name, or a type already registered; the builder that follows then discards what it is given.
2. **Line 390:** a :term[tag component]{id=tag-component} has size 0 and no storage per entity.
3. **Line 392:** `if constexpr` chooses the tag branch or the data branch while the compiler builds `Register<T>`; the other branch is not compiled.
4. **Lines 395–398:** a tag has no storage, so `Get` returns a pointer to one shared static instance whenever the entity has the tag; callers may treat non-null as present.
5. **Lines 418–422:** `MarkModified` calls `registry.patch<T>`, which emits the update signal that caches and observers listen for.

The remaining operations follow the same pattern, one lambda each, with `if constexpr` wherever tags and data differ.

```cpp src="Strata/src/Strata/Reflection/ComponentRegistry.h#L424-L476"
	info.Remove = [](entt::registry& registry, entt::entity entity) { registry.remove<T>(entity); };
	info.Copy = [](entt::registry& destination, entt::entity destinationEntity, const entt::registry& source, entt::entity sourceEntity)
	{
		if constexpr (std::is_empty_v<T>)
		{
			if (source.all_of<T>(sourceEntity))
				destination.emplace_or_replace<T>(destinationEntity);
		}
		else
		{
			if (const T* component = source.try_get<T>(sourceEntity))
				destination.emplace_or_replace<T>(destinationEntity, *component);
		}
	};
	info.AssureStorage = [](entt::registry& registry) { registry.storage<T>(); };
	info.CopyStorage = [](entt::registry& destination, const entt::registry& source)
	{
		const auto* from = source.storage<T>();
		if (!from || from->empty())
			return;
		auto& to = destination.storage<T>();
		to.reserve(to.size() + from->size());
		if constexpr (std::is_empty_v<T>)
		{
			for (const entt::entity entity : static_cast<const entt::sparse_set&>(*from))
				to.emplace(entity);
		}
		else
		{
			for (const auto [entity, component] : from->each())
				to.emplace(entity, component);
		}
	};
	info.CreateValueArray = []() -> Scope<ComponentValueArray> { return CreateScope<Detail::TypedComponentValueArray<T>>(); };
	info.EmplaceCopy = [](entt::registry& registry, entt::entity entity, [[maybe_unused]] const void* component)
	{
		if constexpr (std::is_empty_v<T>)
			registry.emplace_or_replace<T>(entity);
		else
			registry.emplace_or_replace<T>(entity, *static_cast<const T*>(component));
	};
	info.Observe = [](entt::registry& registry, ComponentObserver& observer, bool updates)
	{
		std::vector<entt::connection> connections;
		connections.emplace_back(registry.on_construct<T>().template connect<&ComponentObserver::OnComponentChanged>(observer));
		connections.emplace_back(registry.on_destroy<T>().template connect<&ComponentObserver::OnComponentChanged>(observer));
		if (updates)
			connections.emplace_back(registry.on_update<T>().template connect<&ComponentObserver::OnComponentChanged>(observer));
		return connections;
	};

	return ComponentInfoBuilder<T>(registered);
}
```

1. **Lines 425–437:** `Copy` moves one entity's component between registries, and a tag is copied as presence only.
2. **Lines 438–456:** `AssureStorage` and `CopyStorage` copy a whole storage at once, for scene copies; they touch only this type's storage, so different types may be copied on different threads.
3. **Lines 457–464:** `CreateValueArray` and `EmplaceCopy` serve components kept outside a registry, such as a prefab's prototype.
4. **Lines 465–473:** `Observe` connects a listener to the construct, destroy and optional update signals of the type.

`Register<T>` sets eleven operations. Builder calls set the rest of the twenty: `Extra`, `ExtraReferences`, `ExtraBinary` and `Gizmo`. One template and one `if constexpr` replace what would otherwise be about 40 hand-written copies, one for each component type.

:::example[What one `Register` call gives a tag]
`InactiveComponent` is an empty struct, registered as `ComponentRegistry::Register<InactiveComponent>("Inactive")` with a category, a description and the `Hidden` flag, and no properties. Its `Size` is 0. `Has` asks the registry whether the entity has it, `Add` adds it, and `Get` returns the shared static instance when the entity has it and null when it does not. The same call for a struct with data makes `Get` return a pointer into the real storage. The page on [entities and components](../world/ecs.md) explains why a tag needs no storage.
:::

**Component flags** are the bits of `ComponentFlags` that say how the engine treats a type:

- `Hidden`: not shown in the Inspector or the Add Component menu;
- `NotRemovable`: every entity has it, as with `Transform`;
- `NoCopy`: not copied when play mode starts;
- `NoSerialize`: the scene writer stores it itself, as with an entity's `ID` and parent;
- `EngineAdded`: visible, and a user may remove it, but only the engine adds it, as with prefab links.

Helper functions read the bits. `IsAddable`, for example, is true for a component that is not hidden, not added by the engine and saved in scenes.

## The registry: names, refusals and lookups

`ComponentRegistry` has three states: closed, open and frozen, drawn on the page about [layers and registries](../core/layers-registries.md). Using it while closed is a programmer error, and `ST_CORE_VERIFY` stops the program. `Register<T>` while open creates the info. After the freeze, it logs an error and returns a builder that converts to `false` and discards every call that follows. The program continues, and the component is absent.

Three more refusals share that response: a type that is registered already, a name that another component has (compared without case, so "camera" and "Camera" clash), and an empty name. The discarding builder needs no `if` around each call: the builder writes into a scratch `ComponentInfo` that is thrown away.

Three lookups read the result. `Find(name)` compares without regard to case and returns null for an unknown name. `Find<T>()` and `FindByTypeId(id)` use the type's hash in a map. `GetAll` returns the list in registration order. Because registrations are guarded by a :term[mutex]{id=mutex} while the registry is open and never change after the freeze, no reader needs a lock.

`Freeze` does one more job: it checks every `Requires` entry. A name that matches no registered component, or the component itself, is dropped with an error, so that adding a component never fails over a bad requirement.

## A real registration: the camera

The camera's registration in `Strata/src/Strata/Scene/ComponentRegistration.cpp` uses nearly every feature of the builder. It sets a category, one enum, ranges, hint texts, a color, a new section, an entity reference and loops of inactive reasons.

```cpp src="Strata/src/Strata/Scene/ComponentRegistration.cpp#L153-L185"
ComponentRegistry::Register<CameraComponent>("Camera")
	.Category("Rendering")
	.EnumProperty("Projection", &CameraComponent::Projection, { { "Perspective", 0 }, { "Orthographic", 1 } })
	.Property("PerspectiveFOV", &CameraComponent::PerspectiveFOV, WithTooltip(Range(1.0f, 179.0f, 0.1f), "Vertical field of view in degrees"))
	.Property("PerspectiveNear", &CameraComponent::PerspectiveNear, Range(0.001f, c_Unbounded, 0.01f))
	.Property("PerspectiveFar", &CameraComponent::PerspectiveFar, Range(0.01f, c_Unbounded, 1.0f))
	.Property("OrthographicSize", &CameraComponent::OrthographicSize, WithTooltip(Range(0.001f, c_Unbounded, 0.1f), "Vertical extent in world units"))
	.Property("OrthographicNear", &CameraComponent::OrthographicNear, Range(-c_Unbounded, c_Unbounded, 0.01f))
	.Property("OrthographicFar", &CameraComponent::OrthographicFar, Range(-c_Unbounded, c_Unbounded, 1.0f))
	.Property("Primary", &CameraComponent::Primary, WithTooltip({}, "The first active primary camera renders the game view"))
	.Property("ClearColor", &CameraComponent::ClearColor, Color())
	.Section("Depth of field")
	.Property("DepthOfField", &CameraComponent::DepthOfField,
		WithTooltip({}, "Blurs what lies nearer or farther than the focus, as a camera's lens does (perspective cameras); players can "
			"turn it off"))
	.Property("FocusDistance", &CameraComponent::FocusDistance,
		WithTooltip(Range(0.1f, 10000.0f, 0.05f), "Meters from the camera to the sharpest plane"))
	.EntityProperty("FocusEntity", &CameraComponent::FocusEntity,
		{ .Tooltip = "Keeps this entity in focus (its distance along the camera's view, at least the near plane); none: Focus Distance" })
	.Property("Aperture", &CameraComponent::Aperture,
		WithTooltip(Range(1.0f, 32.0f, 0.1f), "The lens's f-number: lower blurs more (f/1.4 a portrait lens wide open), higher keeps more "
			"in focus (f/16)"))
	.Property("SensorHeight", &CameraComponent::SensorHeight,
		WithTooltip(Range(4.0f, 100.0f, 0.5f), "Millimeters: with the field of view it sets the focal length; larger sensors blur more "
			"at the same view (24 full frame, 15.6 APS-C, 8.8 a 1-inch sensor)"));
for (const char* property : { "PerspectiveFOV", "PerspectiveNear", "PerspectiveFar" })
	ComponentRegistry::SetInactiveReason<CameraComponent>(property, &PerspectiveOnly);
for (const char* property : { "FocusEntity", "Aperture", "SensorHeight" })
	ComponentRegistry::SetInactiveReason<CameraComponent>(property, &WithLens);
ComponentRegistry::SetInactiveReason<CameraComponent>("FocusDistance", &WithFocusDistance);
ComponentRegistry::SetInactiveReason<CameraComponent>("DepthOfField", &PerspectiveOnly);
for (const char* property : { "OrthographicSize", "OrthographicNear", "OrthographicFar" })
	ComponentRegistry::SetInactiveReason<CameraComponent>(property, &OrthographicOnly);
```

1. **Line 153:** the name `Camera` is the key in files and commands; the display name is derived from it.
2. **Line 155:** `EnumProperty` lists the options with their numbers, and files and commands use the names.
3. **Line 156:** a range of 1 to 179 degrees, a drag speed of 0.1 and a hint text, all in one expression.
4. **Lines 157–158:** `c_Unbounded` keeps near and far finite without a real limit.
5. **Line 164:** every property below this call joins the section "Depth of field".

The last lines of the quote attach inactive reasons: loops of `SetInactiveReason` calls bind property names to small functions such as `PerspectiveOnly`. The whole block runs while the registry is open, inside the Scene module's registration.

:::example[A field of view of 200 on three paths]
The camera's `PerspectiveFOV` has the range 1 to 179. A command that sets 200 is refused with `Camera.PerspectiveFOV must be between 1 and 179, not 200`, and the scene does not change. A scene file that holds 200, after a hand edit, loads as 179, with no warning in the log. An Inspector drag past the end of the field stays at 179. Exercise 1 asks you to predict and then run it.
:::

Where does this registration run? `RegisterSceneModule` in `Strata/src/Strata/Scene/SceneRegistration.cpp` calls `RegisterSceneComponents`, which holds the camera's registration and the other components of the Scene module, and then adds the module's other registrations. It is second in the composition root's table, after Input.

```cpp src="Strata/src/Strata/Scene/SceneRegistration.cpp#L14-L22"
void RegisterSceneModule()
{
	RegisterSceneComponents();
	// The project's collision layers are Scene's: the type, the parser and every reader of names are, so a build or game
	// without physics keeps them.
	SettingsRegistry::GetProcessRegistry().Register(ProjectCollisionLayers::MakeSection());
	// The fixed rate is Scene's: the step drives scripts and animation as well as physics, so a build without physics keeps
	// it.
	SettingsRegistry::GetProcessRegistry().Register(ProjectSceneTiming::MakeSection());
```

Besides the components, the module registers two settings sections, `Scene.CollisionLayers` and `Scene.Timing`, and three asset loaders for prefabs, models and scenes. A module that has no physics still owns the collision layers, because the type and the parser live in Scene.

What does the registration buy? Nearly everything below comes from the one description, with no more code.

::figure{id=directional-light-sections}

The Inspector draws a component's properties in the sections they declare. The directional light, registered with the sections "Light" and "Shadows", shows two headings, and the Inspector needs no code for them. Below Shadows stands the one part that comes from code written for the light: a line with the size of the shadow maps and a link to the Graphics Quality page.

The Add Component menu lists each component that users may add under its `Category`, so every `.Category("Lighting")` call puts a component in that group. The editor sorts the groups by name and keeps registration order inside each group. A component with no category lands under "General". The drawing below sets out the groups that Strata's own registrations give, in three columns where the menu has one list.

::figure{id=add-component-groups}

## Validation, clamping and refusal

Every write ends in `PropertyInfo::SetValue`, which checks the value against the property before it assigns it. The first half handles the types that need a check of their own.

```cpp src="Strata/src/Strata/Reflection/Property.cpp#L192-L235"
bool PropertyInfo::SetValue(void* object, const PropertyValue& value, std::string* outError) const
{
	if (value.index() != GetPropertyValueIndex(Type))
	{
		if (outError)
			*outError = fmt::format("Property '{}' expects a value of type {}", Name, PropertyTypeToString(Type));
		return false;
	}

	PropertyValue finalValue = value;
	switch (Type)
	{
		case PropertyType::Enum:
		{
			const int32_t enumValue = std::get<int32_t>(value);
			if (!FindEnumValue(enumValue))
			{
				if (outError)
					*outError = fmt::format("Value {} is not a valid option for property '{}'", enumValue, Name);
				return false;
			}
			break;
		}
		case PropertyType::Int:
			if (HasRange())
				finalValue = std::clamp(std::get<int32_t>(value), static_cast<int32_t>(Min), static_cast<int32_t>(Max));
			break;
		case PropertyType::UInt:
			if (HasRange())
				finalValue = std::clamp(std::get<uint32_t>(value), static_cast<uint32_t>(std::max(Min, 0.0f)), static_cast<uint32_t>(std::max(Max, 0.0f)));
			break;
		case PropertyType::Float:
		{
			const float floatValue = std::get<float>(value);
			if (!std::isfinite(floatValue))
			{
				if (outError)
					*outError = fmt::format("Property '{}' must be a finite number", Name);
				return false;
			}
			if (HasRange())
				finalValue = std::clamp(floatValue, Min, Max);
			break;
		}
```

1. **Lines 194–199:** a value of the wrong alternative fails with a message and leaves the object unchanged.
2. **Lines 204–214:** an enum value must be one of the registered options.
3. **Lines 215–222:** :term[integer]{id=integer} values are clamped to the range when there is one.
4. **Lines 223–235:** a float must be finite, and then it is clamped; :term[NaN]{id=nan} and infinity are refused, not clamped.

The second half handles vectors and quaternions.

```cpp src="Strata/src/Strata/Reflection/Property.cpp#L236-L286"
		case PropertyType::Vec2:
		case PropertyType::Vec3:
		case PropertyType::Vec4:
		case PropertyType::Color3:
		case PropertyType::Color4:
		{
			bool finite = true;
			std::visit([&](auto& vector)
			{
				using VectorType = std::decay_t<decltype(vector)>;
				if constexpr (std::is_same_v<VectorType, glm::vec2> || std::is_same_v<VectorType, glm::vec3> || std::is_same_v<VectorType, glm::vec4>)
				{
					for (glm::length_t index = 0; index < VectorType::length(); index++)
					{
						finite &= std::isfinite(vector[index]);
						if (HasRange())
							vector[index] = std::clamp(vector[index], Min, Max);
					}
				}
			}, finalValue);
			if (!finite)
			{
				if (outError)
					*outError = fmt::format("Property '{}' components must be finite numbers", Name);
				return false;
			}
			break;
		}
		case PropertyType::Quat:
		{
			const glm::quat rotation = std::get<glm::quat>(value);
			const float length = glm::length(rotation);
			if (!std::isfinite(length) || length < 1e-6f)
			{
				if (outError)
					*outError = fmt::format("Property '{}' requires a non-zero rotation quaternion", Name);
				return false;
			}
			// Only correct rotations that are noticeably off unit length, so that values which already are
			// (within float precision) survive save/load round trips bit-exactly.
			if (glm::abs(length - 1.0f) > 1e-4f)
				finalValue = rotation / length;
			break;
		}
		default:
			break;
	}

	Setter(object, finalValue);
	return true;
}
```

1. **Lines 236–263:** every component of a vector or color is clamped and checked to be finite, and one component that is not finite fails the whole value.
2. **Lines 264–279:** a quaternion must have a length above a tiny bound. The code divides by the length only when the quaternion is noticeably off unit length, so unit values survive a save and a load bit for bit.
3. **Line 284:** the write function runs only after every check, so a refused value changes nothing.

`SetValue` clamps, and a second function refuses. `PropertyInfo::IsInRange` returns false for a number outside the range and writes a message such as "must be between 1 and 512, not 0.5". Vectors report the first component outside. The Inspector and files clamp, which suits a drag past the end of a slider and an old file with a stale value. Commands refuse, because an agent that sends 200 should learn that 200 was not taken instead of finding 179 in its place.

The same split exists between strict and forgiving reads. `ComponentAccess::Deserialize` takes a `strict` flag.

```cpp src="Strata/src/Strata/Scene/ComponentAccess.cpp#L41-L78"
for (const auto& [key, value] : json.items())
{
	const PropertyInfo* property = info.FindProperty(key);
	if (!property)
	{
		// Keys consumed by DeserializeExtra are not properties.
		if (info.DeserializeExtra)
			continue;

		const std::string message = fmt::format("Component '{}' has no property '{}'", info.Name, key);
		if (strict)
		{
			if (outError)
				*outError = message;
			return false;
		}
		if (outWarnings)
			outWarnings->push_back(message);
		continue;
	}

	if (property->IsTransient())
		continue;

	std::string error;
	std::optional<PropertyValue> parsed = PropertyValueFromJson(*property, value, &error);
	if (parsed && property->SetValue(component, *parsed, &error))
		continue;

	if (strict)
	{
		if (outError)
			*outError = fmt::format("{}: {}", info.Name, error);
		return false;
	}
	if (outWarnings)
		outWarnings->push_back(fmt::format("{}: {}", info.Name, error));
}
```

1. **Lines 44–60:** an unknown property is skipped with a warning, or, in a strict read, fails the call, unless the component has extra data that reads it.
2. **Lines 62–63:** a transient property in a file is ignored.
3. **Lines 65–68:** the text is parsed into a `PropertyValue`, then `SetValue` validates it, and success moves to the next key.
4. **Lines 70–77:** a strict read returns the first failure; a forgiving read records a warning and continues.

Scene loading, prefab overrides and undo call it with `strict` false; the `component.set` command calls it with `strict` true, after its own range check. A scene load logs the warnings, as in `Scene '<path>': <warning>`. A component whose name no module registers is kept unchanged on the entity, so a scene made with a module that this build lacks is not damaged on the next save.

:::example[Three values, three readers]
Take the camera's `PerspectiveFOV` with the range 1 to 179. The value 90 passes every reader. The value 200 is refused by a command, clamped to 179 by a file or the Inspector, and the file load logs nothing, because `SetValue` succeeds. The text `"wide"` fails in every reader: the file load logs a warning and keeps the old value, the command refuses.
:::

`ComponentAccess::SetProperty` is the write that everything else shares.

```cpp src="Strata/src/Strata/Scene/ComponentAccess.cpp#L117-L146"
bool ComponentAccess::SetProperty(Entity entity, const ComponentInfo& info, const PropertyInfo& property, const PropertyValue& value, std::string* outError)
{
	if (!entity.IsValid())
	{
		if (outError)
			*outError = "Invalid entity";
		return false;
	}
	if (property.IsReadOnly())
	{
		if (outError)
			*outError = fmt::format("Property '{}.{}' is read-only", info.Name, property.Name);
		return false;
	}

	entt::registry& registry = entity.GetScene()->GetRegistry();
	void* component = info.Get(registry, entity.GetHandle());
	if (!component)
	{
		if (outError)
			*outError = fmt::format("Entity '{}' has no {} component", entity.GetName(), info.Name);
		return false;
	}

	if (!property.SetValue(component, value, outError))
		return false;

	info.MarkModified(registry, entity.GetHandle());
	return true;
}
```

1. **Lines 119–124:** an invalid entity is an error, never an assert.
2. **Lines 125–130:** a read-only property is refused for every caller.
3. **Lines 132–139:** the entity must have the component; the error names it.
4. **Lines 141–144:** the value is validated and assigned first, and then `MarkModified` signals the change so caches and observers hear it.

## Requirements and inactive reasons

A **requirement** is a component that another component needs on its entity: an image of the game's user interface (UI) needs a `UIRect`. A registration states it with `Requires("UIRect")`. Many components of the game user interface module do this, for the same rect. The paths that add a component by name add the missing ones first, in the same edit. Removing a required component is still allowed, and the dependent one then has no effect.

```cpp src="Strata/src/Strata/Scene/ComponentAccess.cpp#L153-L192"
bool AddWithRequirements(Entity entity, const ComponentInfo& info, std::vector<const ComponentInfo*>& adding, std::string* outError)
{
	if (info.IsHidden())
	{
		if (outError)
			*outError = fmt::format("Component '{}' is internal and cannot be added directly", info.Name);
		return false;
	}
	entt::registry& registry = entity.GetScene()->GetRegistry();
	// Already present: nothing to add, even for components only the engine adds.
	if (info.Has(registry, entity.GetHandle()))
		return true;
	if (HasFlag(info.Flags, ComponentFlags::EngineAdded))
	{
		if (outError)
			*outError = fmt::format("Component '{}' is added by the engine (e.g. when instantiating a prefab) and cannot be added directly", info.Name);
		return false;
	}

	// The components it needs first (ComponentInfo::Requires: names of other registered components, which the registry
	// checked when it froze), so that systems hearing of it find them.
	adding.push_back(&info);
	for (const std::string& requiredName : info.Requires)
	{
		const ComponentInfo* required = ComponentRegistry::Find(requiredName);
		if (!required || std::find(adding.begin(), adding.end(), required) != adding.end())
			continue;
		std::string error;
		if (!AddWithRequirements(entity, *required, adding, &error))
		{
			if (outError)
				*outError = fmt::format("Component '{}' needs '{}', which cannot be added: {}", info.Name, required->Name, error);
			adding.pop_back();
			return false;
		}
	}
	adding.pop_back();
	info.Add(registry, entity.GetHandle());
	return true;
}
```

1. **Lines 155–160:** hidden components cannot be added by name.
2. **Lines 163–170:** a component the entity has already counts as added, and one that only the engine may add is refused.
3. **Lines 174–179:** `adding` lists the components on the way up the chain, and one already in it is skipped, which ends a cycle.
4. **Lines 180–187:** a requirement that cannot be added fails the whole call with a message that names both components.
5. **Lines 189–190:** the component itself is added last, so that systems that hear of it find what it needs.

Exercise 3 builds the same idea on plain names.

:::example[Adding a `UIImage`]
Add `UIImage` to an entity that has no `UIRect`. `AddWithRequirements` puts `UIImage` on the chain, finds `UIRect` in its requirements and calls itself for the rect. The rect needs nothing, so it is added first. Then the image is added, in the same edit, and the systems that hear of the image find its rect. Adding `UIImage` a second time changes nothing, because the entity has it.
:::

An **inactive reason** is text that says why a property has no effect in its component's current state, and the empty text when it has one. In the camera, `PerspectiveFOV` does nothing while the projection is orthographic, and `OrthographicSize` does nothing while it is perspective. An editor that shows an inactive property as disabled, with the reason, saves people from editing a value that changes nothing. Agents benefit too: `component.get` returns an `inactive` object that lists them.

The call is `ComponentRegistry::SetInactiveReason<T>(property, reason)`. It runs next to the property's registration, while the registry is open, and `reason` is a function of the component: it returns the reason, or "" when the property is active. It returns false, with the cause logged, when the registry is not open, when the component is not registered or when the component has no property of that name. The property name is matched exactly here, with its case, unlike the lookups that ignore case. A property that is always active has no function, and `GetInactiveReason` returns "".

The function is a plain function of the component. In the camera it is `PerspectiveOnly`, which returns "The camera's projection is Orthographic" for an orthographic camera. `WithLens` and `WithFocusDistance` build longer chains: the focus distance is inactive without a lens, and also while a focus entity sets the distance. How the Inspector shows a reason, and how a multiple selection merges them, belongs to [Inspectors](../editor-ui/inspectors.md).

Two things make this data about the property rather than behavior. The reasons are data on the description, read by anything that wants them. And the registry closes: a test (`Inactive reasons are set only while the registry is open, on properties it has`) checks that a call after the freeze returns false and sets nothing.

## Data that is not a property

Some component data does not fit the property model. A script component stores the fields of its scripts, whose names and types the script defines. **Extra data** is data of a component that its own functions save and load, outside the property list: `Extra(serialize, deserialize)` on the builder sets the two functions. `Extra` writes into the same :term[JSON object]{id=json-object} as the properties, and `ComponentAccess::Deserialize` leaves keys that the extra reader consumes alone. `ExtraBinary` is the form for cooked scenes, taught in the page on scene :term[serialization]{id=serialization}.

Extra data may hold references to entities and assets. Other code needs to find them without knowing the type. Copying must remap an entity reference, a prefab instance is compared with its prefab through them, and an export must include the assets that only extra data names.

`ExtraReferences` takes four functions: `Visit` reports every reference, `Set` replaces one, `Equals` compares two components with a remap, and `VisitJson` finds the references in saved JSON without making a component. A reference has two indices that the component chooses; for scripts they are the script and its field. Omit it and a copy's reference points at the original, and an export drops assets.

Two more types complete the set. `ComponentValueArray` holds values of one component type outside any registry, in one array. Prefab prototypes use it, because an EnTT storage allocates 1,024 elements at a time, which is much for a prefab of three entities. `ComponentObserver` is a listener that `Observe` connects to a type's signals, for caches that depend on which entities have a component. `ComponentGizmo` is a shape that a component asks the editor to draw, named in the builder as `Gizmo`; [Debug drawing](../gpu/debug-drawing.md) teaches it.

## Values as JSON

Files and commands carry values as JSON, and the form matters, because a scene file is read by people, compared by tools and saved again. **Canonical JSON** is the one exact form in which property values are written, and `PropertyValueToJson` writes it. The forms are:

- :term[booleans]{id=boolean}, integers and floats as plain JSON values;
- vectors and colors as arrays;
- a quaternion as `[x, y, z, w]`;
- a string as a string;
- an enum as its option name;
- an asset or entity as 16 :term[hexadecimal]{id=hexadecimal} digits.

Floats need care. A float such as 0.1 is stored in 32 bits, and written as a 64-bit double it becomes 0.10000000149011612, which reads back correctly but looks wrong and makes :term[diffs]{id=diff} noisy. `FloatToJson` uses the shortest decimal text that reads back as the same float, so 0.1 stays "0.1". A float that is not finite becomes 0, because JSON cannot hold it. The functions `AppendFloatJson` and `AppendPropertyValueJson` write the same :term[bytes]{id=byte} straight into a string with no JSON tree, for the writers of large scenes that format millions of floats.

:::example[Reading what an agent might send]
`PropertyValueFromJson` is the forgiving direction. For a `Vec3`, `[1, 2, 3]`, `{"x": 1, "y": 2, "z": 3}` and a single number `5` (every component 5) all work. A `Quat` accepts `[x, y, z, w]`, three Euler angles `[pitch, yaw, roll]` in degrees, or `{"Euler": [10, 20, 30]}`. An `Enum` accepts its name in any case or its number, and an `Asset` or `Entity` accepts hexadecimal text, an integer, or null, 0 or an empty string for none. The wide input lets agents succeed; the narrow output keeps files stable.
:::

`DescribeProperty` returns a JSON description of a property for tools: its name, display name, type, hint text, section, range, asset type, enum options and flags. Commands such as `component.list` use it, so an agent learns a component's fields from the same description the Inspector draws.

## `ComponentAccess`: the one validated path

`ComponentAccess` is the one validated path to component data. The scene writer and reader, the Inspector, commands, undo and scripts call it. Every one gets the same checks: the entity is valid, the property is not read-only, the value has the right type and the range holds. The change is then signaled. A new consumer calls it and inherits every rule.

There is a second path, and engine code uses it all the time. `Entity::AddComponent<T>` and `GetComponent<T>` are typed calls that go straight to the EnTT registry. They check nothing about ranges, they validate no value, and they ignore `Requires`. A range holds only on the paths that run through reflection. Engine code that writes a field directly must signal the change itself, as the transform contract of [the scene graph](../world/scene-graph.md) requires.

### A field that is not registered

A newcomer's error: add a field to a component struct and forget to register it. Nothing warns. The compiler is content, the tests that do not look at the field pass, and the field works in the code that reads the struct. But the field is not saved in a scene, not shown in the Inspector, and out of reach of commands and scripts.

A play copy still copies it, because `CopyStorage` copies the whole struct, so the bug can hide until the first reload or the first agent that asks for the field. The defense is a habit: register a field in the same edit that adds it, and extend the tests that read the component.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Macros and a header tool | Unreal Engine's Unreal Header Tool; the `Qt` meta-object compiler | A field cannot be forgotten once a macro marks it; fewer lines per field | A second program in the build, generated files, and a macro language to learn |
| A separate generator that reads the headers | Projects that run a C++ parser over their headers | A list that follows the struct without a hand-written line | A parsing tool to build and to keep current as C++ grows |
| Run-time registration libraries | `RTTR`, EnTT's `meta` | A tested library and no engine code for the base | Their types in every interface, and rules for ranges, sections and inactive reasons that Strata still adds |
| Language reflection | Languages that build it in; C++26, a later standard than Strata's | No lists at all | Not available in C++20, the standard Strata builds with |
| Hand-written code per consumer | Projects with a handful of components | No machinery to learn | The 280 pieces of code of the first section, and silent differences between consumers |

Strata chose registration because it needs no tool, it is plain C++ that a debugger steps through, and one description can carry what a generator would not know: ranges, hint texts, sections and reasons. The statements about other engines come from their public documentation; see Further reading.

## How it is tested

The suites live in `StrataTests/src/Scene/ReflectionTests.cpp` and `StrataTests/src/Reflection/`. The suite `Reflection` checks that:

- every built-in component has a unique name;
- display names follow from names, as in `PerspectiveFOV` to `Perspective FOV`;
- properties read and write with validation: the camera's 500 becomes 179, and NaN and `"wide"` are refused;
- JSON conversion accepts the canonical and the convenient forms;
- `DescribeProperty` shows the data about a property to tools;
- components that only the engine adds cannot be added directly;
- `Section` applies to the properties after it.

The suite `Reflection.ComponentSchema` compares the live registry with a snapshot, `StrataTests/Architecture/ComponentSchema.json`, so a move of a component between modules cannot change a name, the data about a component, a property or the order. Components added since are allowed. The suite `Scene.InactiveProperties` checks that properties name their reason only while another property disables them. A second case checks that a frozen registry refuses the call.

Run part of the tests directly with the test program and a doctest filter, for example `build/windows/bin/Debug/StrataTests.exe --test-suite=Reflection*`, or run everything with `ctest --preset windows-debug`.

## Changing it safely

The extension points are few. To add a property, add one call to the component's registration, in the module's own folder. To add a kind of data about components, add a field to `ComponentInfo` and a builder method, and extend `DescribeProperty` or the schema snapshot if tools should see it. To add a property type, extend `PropertyType`, `PropertyValue`, the mapping functions, `SetValue`, the JSON functions and the binary form; this is rare and touches many files.

Rules that apply, with reasons:

- Register in the module that owns the component, and only while the registry is open. Registration after the freeze is refused, and the component is missing.
- Never rename a name. Names are keys in files, so a rename leaves saved values under a name that nothing reads.
- Append properties to the end of a registration and give each a sensible default. Order is the order the Inspector shows, and the snapshot test checks order.
- Choose ranges that make bad states impossible, and test both the clamp and the refusal.
- Give a property that another disables an inactive reason, in the same edit that adds the property that disables it.
- Describe every reference in extra data, and add the matching tests.

Before a change merges, run the suites `Reflection*` and `Scene.InactiveProperties`. The feature test must exercise a new component, and the snapshot test fails when a name or the order changed by accident.

## Summary

- Reflection gives every component type one description that all seven consumers read, with no code generator. A field that is not registered is invisible to all of them.
- `Register<T>` fills eleven type-erased operations from one template, with `if constexpr` for tag components, and the builder adds the descriptive data, the extra data and the requirements.
- A file load and the Inspector clamp a value into its range, and a command refuses it; non-finite numbers and unknown enum values are refused by every reader.
- `AddComponent` adds the required components first and skips any component already on the chain of requirements, so cycles end; `Freeze` drops requirements that name nothing.
- `ComponentAccess` is the validated path. The typed `AddComponent` and `GetComponent` of `Entity` bypass ranges and requirements, and a field that is not registered is not saved, not shown and out of reach of commands and scripts.

## Check yourself

1. A command sets the camera's `PerspectiveFOV` to 200, and a scene file holds 200 for the same field. What does each do, and what does the log say?

   :::answer{tests="paths"}
   The command is refused with `Camera.PerspectiveFOV must be between 1 and 179, not 200`, and the scene does not change. The file loads with 179, and the log has no warning, because `SetValue` clamps and succeeds. The command checks `IsInRange` first and refuses; the file path never asks it.
   :::

2. A programmer adds `float Exposure` to a component and does not register it. Which is true? (a) The field is saved but not shown. (b) The field is not saved, not shown and out of reach of commands and scripts, and nothing warns. (c) `Freeze` logs an error that names the field.

   :::answer{tests="bypass"}
   Option (b). The description lists only what the registration names, so the field has no entry in any consumer. Option (a) is false because files are written from the property list. Option (c) is false because `Freeze` checks only requirements. A play copy still copies the field, because `CopyStorage` copies the whole struct.
   :::

3. Why does `Register<T>` choose between two bodies with `if constexpr (std::is_empty_v<T>)` and not an ordinary `if`?

   :::answer{tests="mechanism"}
   An ordinary `if` compiles both branches, and the data branch calls `registry.try_get<T>` and `registry.patch<T>`, which an empty struct cannot use because it has no storage. `if constexpr` discards the branch that does not apply while the template is built, so each component type compiles only the operations that suit it.
   :::

4. Component `A` requires `B`, and `B` requires `A`. What does `AddComponent` for `A` do on an entity that has neither?

   :::answer{tests="requirements"}
   The call adds `B` first, then `A`. While adding `A`, it lists `A` as on the chain; `B` then sees that `A` is on the chain and skips it, so there is no endless loop of calls. The result has both components, each added once.
   :::

5. A `Vec3` property has the range -1 to 1. A command sends `[0.5, 2, -3]`. What message does the refusal give?

   :::answer{tests="paths"}
   The message ends with "must be between -1 and 1, not 2". `IsInRange` checks the components in order and stops at the first one outside, which is 2. The same value in a file loads as `[0.5, 1, -1]`.
   :::

6. A game's setup code calls `ComponentRegistry::Register<Spinner>("Spinner")` after the engine's modules finished registering. What happens?

   :::answer{tests="register"}
   The registry is frozen, so the call logs an error and returns a builder that converts to `false` and discards the calls that follow. No crash occurs, and the component is missing from files, the Inspector and commands. The game registers it through the module options instead.
   :::

## Exercises

1. **Basic.** Predict, then run: a camera's `PerspectiveFOV` is set to 200 with the `component.set` command, and the same value is written into a copy of a scene file by hand. What does each give? Write your prediction down, then check it on a copy of a sample.

   Start the editor, press **Open Sample...** in the launcher, choose **Third-Person Adventure** and press **Copy and Open**, as on [Your first game](../start/first-game.md); type a new **Folder** name if `ThirdPerson` exists. While the editor runs, open a terminal in the Strata folder, where [How to read this book](../start/how-to-read.md#how-to-read-a-command) runs `StrataCLI`. The four lines open the Course scene, find the camera's id, try the value and read the camera back. [The editor commands](../editor/commands.md) teach every command.

   ::::tabs{sync=os}
   :::tab[Windows]
   Windows PowerShell 5.1 drops the quotes inside a JSON argument, so each line pipes its parameters in: the `-` reads them from :term[standard input]{id=standard-input}.

   ```powershell
   '{ "scene": "Scenes/Course.stscene" }' | .\StrataCLI call scene.open -
   '{ "name": "Camera" }' | .\StrataCLI call entity.find -
   '{ "entity": "350D7DDD7ED21DD5", "component": "Camera", "values": { "PerspectiveFOV": 200 } }' | .\StrataCLI call component.set -
   '{ "entity": "350D7DDD7ED21DD5", "component": "Camera" }' | .\StrataCLI call component.get -
   ```

   Each line prints its answer as JSON, and the third one prints an error.
   :::
   :::tab[Linux]

   ```sh
   ./StrataCLI call scene.open '{ "scene": "Scenes/Course.stscene" }'
   ./StrataCLI call entity.find '{ "name": "Camera" }'
   ./StrataCLI call component.set '{ "entity": "350D7DDD7ED21DD5", "component": "Camera", "values": { "PerspectiveFOV": 200 } }'
   ./StrataCLI call component.get '{ "entity": "350D7DDD7ED21DD5", "component": "Camera" }'
   ```

   Each line prints its answer as JSON, and the third one prints an error.
   :::
   :::tab[macOS]

   ```sh
   ./StrataCLI call scene.open '{ "scene": "Scenes/Course.stscene" }'
   ./StrataCLI call entity.find '{ "name": "Camera" }'
   ./StrataCLI call component.set '{ "entity": "350D7DDD7ED21DD5", "component": "Camera", "values": { "PerspectiveFOV": 200 } }'
   ./StrataCLI call component.get '{ "entity": "350D7DDD7ED21DD5", "component": "Camera" }'
   ```

   Each line prints its answer as JSON, and the third one prints an error.
   :::
   ::::

   The scene file stores the camera's id, so `entity.find` prints `350D7DDD7ED21DD5` in every copy of the sample; if it prints another, use that one. For the edit by hand, open `Assets/Scenes/Course.stscene` of your copy in a :term[code editor]{id=code-editor}. Change `"PerspectiveFOV":60` to `"PerspectiveFOV":200`, save, and run the first and the last line again: `scene.open` reads the file again.

   :::answer[Worked solution]{tests="paths"}
   The prediction: the command is refused, and the file loads clamped to 179. `component.set` prints an error whose `message` is `Camera.PerspectiveFOV must be between 1 and 179, not 200`, and `component.get` still shows 60. After the edit by hand (game makers use commands for this), the field reads 179. The Console shows no warning about the camera, because `SetValue` succeeded; the warnings of the sample itself, scripts not built yet and a model's morph targets, appear either way.
   :::

2. **Medium.** Trace it yourself: find where the `component.set` command checks a value against the range, starting at its registration.

   :::answer[Worked solution]{tests="paths"}
   The command is registered in `StrataEditor/src/Editor/Commands/EntityCommands.cpp`, and its handler calls `ApplyComponents` in `StrataEditor/src/Editor/CommandUtils.cpp`. For each property that has a range, `ApplyComponents` reads the value with `PropertyValueFromJson` and calls `PropertyInfo::IsInRange` in `Strata/src/Strata/Reflection/Property.cpp`; a false result becomes the failure message and rolls the edit back. Only values that pass reach `ComponentAccess::Deserialize` with `strict` true, which calls `SetValue`.
   :::

3. **Medium.** Write a function that adds a component after the components it requires, ends a cycle of requirements, and prints each component as it is added. Test it with a rect and an image that requires it, and with two components that require each other.

   :::answer[Worked solution]{tests="requirements" solution="sketches/world-reflection-requires.cpp"}
   Keep the chain of names being added in a vector. Before the loop over the requirements, push the component; for each requirement, skip it if it is on the chain and add it otherwise. After the loop, pop the chain, insert the component and print it. A component already on the entity returns at once. The whole program and its output are:

   ```cpp sketch="world-reflection-requires.cpp"
   // Adding a component after the components it requires, with a guard against requirements that name each other.
   #include <algorithm>
   #include <cstdio>
   #include <map>
   #include <set>
   #include <string>
   #include <vector>

   namespace
   {
   	const std::map<std::string, std::vector<std::string>> c_Requires = {
   		{ "UIRect", {} },
   		{ "UIImage", { "UIRect" } },
   		{ "Ping", { "Pong" } },
   		{ "Pong", { "Ping" } },
   	};

   	void Add(const std::string& name, std::set<std::string>& entity, std::vector<std::string>& adding)
   	{
   		if (entity.contains(name))
   			return;
   		adding.push_back(name);
   		for (const std::string& required : c_Requires.at(name))
   		{
   			if (std::find(adding.begin(), adding.end(), required) == adding.end())
   				Add(required, entity, adding);
   		}
   		adding.pop_back();
   		entity.insert(name);
   		std::printf("added %s\n", name.c_str());
   	}
   }

   int main()
   {
   	std::set<std::string> entity;
   	std::vector<std::string> adding;
   	Add("UIImage", entity, adding);
   	Add("UIImage", entity, adding);
   	Add("Ping", entity, adding);
   	std::printf("the entity has %zu components\n", entity.size());
   	return 0;
   }
   ```

   ```text output-of="world-reflection-requires.cpp"
   added UIRect
   added UIImage
   added Pong
   added Ping
   the entity has 4 components
   ```

   1. **Lines 11–16:** the requirements are data: each name maps to the names it needs.
   2. **Lines 20–21:** a component the entity has already is skipped.
   3. **Lines 22–26:** the name is put on the chain, and a requirement already on the chain is skipped, which ends the cycle.
   4. **Lines 28–30:** the component is added and printed after its requirements.
   5. **Lines 38–40:** `UIImage` is added twice and `Ping` once.

   The second `Add("UIImage")` prints nothing, because the entity has it. `Ping` and `Pong` each print once, `Pong` first.
   :::

4. **Hard.** Write the registration of a new component `Spinner` with a `Speed` in degrees per second from -720 to 720, an `Axis` enum of X, Y and Z, and a `Pause` flag. Make `Speed` inactive while `Pause` is on, and make the Inspector place both under a section named "Motion".

   :::answer[Worked solution]{tests="register"}
   The registration, written as :term[pseudocode]{id=pseudocode} because it needs the engine, is:

   ```pseudocode
   struct SpinnerComponent { float Speed = 90; AxisType Axis = Y; bool Pause = false; }

   ComponentRegistry::Register<SpinnerComponent>("Spinner")
       .Category("Gameplay")
       .Description("Turns the entity around an axis")
       .Section("Motion")
       .EnumProperty("Axis", &SpinnerComponent::Axis, { {"X", 0}, {"Y", 1}, {"Z", 2} })
       .Property("Speed", &SpinnerComponent::Speed, WithTooltip(Range(-720, 720, 1), "Degrees per second"))
       .Property("Pause", &SpinnerComponent::Pause)

   ComponentRegistry::SetInactiveReason<SpinnerComponent>("Speed",
       [](const SpinnerComponent& spinner) { return spinner.Pause ? "Pause is on" : ""; })
   ```

   1. **Line 6:** `Section` applies to every property registered after it.
   2. **Line 7:** the enum lists its options with their numbers.
   3. **Line 8:** the range of -720 to 720 makes a speed of 1,000 impossible on every path.
   4. **Lines 11–12:** the function returns the reason, or empty text when `Speed` is active.

   Both calls run while the registry is open, in the module's registration function.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Reflection/Property.h` and `Property.cpp`: `PropertyType`, `PropertyValue`, `PropertyFlags`, `PropertyInfo`, `SetValue`, `IsInRange`.
- `Strata/src/Strata/Reflection/PropertyBuilder.h`, `PropertyOptions.h`: `PropertyBuilderBase`, `PropertyListBuilder`, `Range`, `Slider`, `Color`, `WithTooltip`, `c_Unbounded`.
- `Strata/src/Strata/Reflection/ComponentRegistry.h` and `ComponentRegistry.cpp`: `ComponentInfo`, `ComponentFlags`, `ComponentRegistry`, `ComponentInfoBuilder`, `ComponentValueArray`, `ComponentExtraReferences`, `ComponentObserver`.
- `Strata/src/Strata/Reflection/PropertyJson.h` and `PropertyJson.cpp`: `PropertyValueToJson`, `PropertyValueFromJson`, `FloatToJson`, `DescribeProperty`.
- `Strata/src/Strata/Scene/ComponentAccess.h` and `ComponentAccess.cpp`: `ComponentAccess`.
- `Strata/src/Strata/Scene/ComponentRegistration.cpp` and `SceneRegistration.cpp`: the Scene module's components and `RegisterSceneModule`.
- Tests: `StrataTests/src/Scene/ReflectionTests.cpp` (suites `Reflection` and `Scene.InactiveProperties`), `StrataTests/src/Reflection/ComponentSchemaTests.cpp`.
- Commands: `component.list`, `component.get`, `component.set`, `component.add`.

## Further reading

- [EnTT, the library's repository and its documentation of `meta`](https://github.com/skypjack/entt): how another registration-based reflection works (intermediate).
- Epic Games, the Unreal Engine documentation on properties and the Unreal Header Tool: how the macro and generator approach works (intermediate).
- Qt Project, the documentation of the meta-object compiler: a generator that reads headers (intermediate).
- The RTTR library's documentation: run-time registration with a C++ API (intermediate).
- [cppreference, `std::variant`](https://en.cppreference.com/w/cpp/utility/variant): the type behind `PropertyValue` (beginner).
