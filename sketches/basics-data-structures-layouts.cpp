// The bytes an update of one field sweeps in an array of structs and in a struct of arrays.
#include <iostream>
#include <vector>

struct Particle
{
	float Position[3];
	float Velocity[3];
	float Life;
	unsigned Color;
};

int main()
{
	const size_t count = 1000;
	std::vector<Particle> particles(count);
	std::vector<float> lives(count);
	for (Particle& particle : particles)
		particle.Life -= 0.016f; // touches one field of each 32-byte struct
	for (float& life : lives)
		life -= 0.016f; // touches a packed array of that field alone

	std::cout << "array of structs, bytes swept: " << particles.size() * sizeof(Particle) << '\n';
	std::cout << "struct of arrays, bytes swept: " << lives.size() * sizeof(float) << '\n';
}
