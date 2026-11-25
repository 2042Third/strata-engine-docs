#pragma once
// A pretend engine file in the shape of an SDK header (tools/tests/test_reference.py).

namespace Strata
{

	class Entity
	{
	public:
		Entity() = default;
		// Whether the entity still exists.
		bool IsValid() const;
		// Finds an entity by its name.
		static Entity Find(std::string_view name);
		template<typename T>
		T GetComponent() const
		{
			return T(*this);
		}
		virtual void OnHit() = 0;
	private:
		void Forget();
	};

	namespace Key
	{
		// Whether a key is held.
		bool IsDown(int key);
	}

	namespace Detail
	{
		void Hidden();
	}

}
