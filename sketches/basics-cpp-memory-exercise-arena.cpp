// Exercise 4: an arena over a fixed buffer, whose bytes become Particle objects through std::construct_at.
#include <cstddef>
#include <iostream>
#include <memory>

struct Particle { float X; int Id; };
struct Arena
{
	alignas(8) unsigned char Bytes[64];
	std::size_t Used = 0;
	Particle* Create(float x, int id)
	{
		std::size_t start = (Used + alignof(Particle) - 1) / alignof(Particle) * alignof(Particle);
		if (start + sizeof(Particle) > sizeof(Bytes)) return nullptr;
		Used = start + sizeof(Particle);
		return std::construct_at(reinterpret_cast<Particle*>(Bytes + start), Particle{ x, id });
	}
};
int main()
{
	Arena arena; int made = 0;
	while (arena.Create(0.5f, made) != nullptr) made++;
	std::cout << "made " << made << ", used " << arena.Used << " bytes\n";
	std::destroy_at(reinterpret_cast<Particle*>(arena.Bytes)); // nothing to clean up here; shows the call
}
