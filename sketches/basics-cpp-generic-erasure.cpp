// Type erasure: one getter type for fields of different classes, built from a pointer to a member.
#include <functional>
#include <iostream>

struct Coin { float Speed = 2.0f; };
struct Light { float Intensity = 800.0f; };

template<typename T>
std::function<float(const void*)> MakeGetter(float T::* member)
{
	return [member](const void* object) { return static_cast<const T*>(object)->*member; };
}

int main()
{
	Coin coin;
	Light light;
	std::function<float(const void*)> getters[2] = { MakeGetter(&Coin::Speed), MakeGetter(&Light::Intensity) };
	std::cout << getters[0](&coin) << ' ' << getters[1](&light) << '\n';
	return 0;
}
