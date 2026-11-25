// A composition root with two registries: components open, accept and freeze; loaders stay open.
#include <cstdio>
#include <functional>
#include <map>
#include <string>
#include <vector>

namespace Toy
{

	enum class State
	{
		Closed,
		Open,
		Frozen
	};

	class ComponentRegistry
	{
	public:
		static void Open() { s_State = State::Open; }
		static void Freeze() { s_State = State::Frozen; }

		static bool Register(const std::string& name)
		{
			if (s_State != State::Open)
			{
				std::printf("  refused %s: the registry is %s\n", name.c_str(), s_State == State::Closed ? "closed" : "frozen");
				return false;
			}
			s_Names.push_back(name);
			return true;
		}

		static const std::vector<std::string>& GetAll() { return s_Names; }

	private:
		static inline State s_State = State::Closed;
		static inline std::vector<std::string> s_Names;
	};

	// Never frozen: a later registration replaces an earlier one.
	class LoaderRegistry
	{
	public:
		static void Register(const std::string& type, const std::string& name) { s_Loaders[type] = name; }
		static const std::string& Find(const std::string& type) { return s_Loaders[type]; }

	private:
		static inline std::map<std::string, std::string> s_Loaders;
	};

	void RegisterSceneModule() { ComponentRegistry::Register("Transform"); LoaderRegistry::Register("Scene", "built-in"); }
	void RegisterRendererModule() { ComponentRegistry::Register("MeshRenderer"); LoaderRegistry::Register("Mesh", "built-in"); }
	void RegisterPhysicsModule() { ComponentRegistry::Register("RigidBody"); }

	struct Module
	{
		const char* Name;
		void (*Register)();
	};

	constexpr Module c_Modules[] = { { "Scene", RegisterSceneModule }, { "Renderer", RegisterRendererModule }, { "Physics", RegisterPhysicsModule } };

	struct Options
	{
		std::vector<std::function<void()>> Extra;
	};

	void RegisterBuiltinModules(const Options& options)
	{
		static bool s_Registered = false;
		if (s_Registered)
		{
			std::printf("  error: called again, ignoring %zu extra registration(s)\n", options.Extra.size());
			return;
		}
		s_Registered = true;

		ComponentRegistry::Open();
		for (const Module& module : c_Modules)
			module.Register();
		for (const std::function<void()>& registration : options.Extra)
			registration();
		ComponentRegistry::Freeze();
	}

}

int main()
{
	std::printf("before the root:\n");
	Toy::ComponentRegistry::Register("Early");

	Toy::Options game;
	game.Extra.push_back([]() { Toy::ComponentRegistry::Register("Spinner"); });
	Toy::RegisterBuiltinModules(game);

	std::printf("after the root:\n");
	Toy::ComponentRegistry::Register("Late");
	Toy::LoaderRegistry::Register("Scene", "a tool's loader");
	Toy::RegisterBuiltinModules(game);

	std::printf("components:");
	for (const std::string& name : Toy::ComponentRegistry::GetAll())
		std::printf(" %s", name.c_str());
	std::printf("\nScene loader: %s\n", Toy::LoaderRegistry::Find("Scene").c_str());
	return 0;
}
