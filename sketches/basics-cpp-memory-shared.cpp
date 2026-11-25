// A shared pointer counts its owners, and the object is deleted when the count reaches 0.
#include <iostream>
#include <memory>

struct Texture
{
	~Texture() { std::cout << "texture deleted\n"; }
};

int main()
{
	std::shared_ptr<Texture> a = std::make_shared<Texture>();
	std::cout << "count " << a.use_count() << '\n';
	{
		std::shared_ptr<Texture> b = a; // a copy: a second owner
		std::cout << "count " << a.use_count() << '\n';
	}
	std::cout << "count " << a.use_count() << '\n';
	a.reset(); // the last owner lets go
	std::cout << "sizes " << sizeof(std::unique_ptr<Texture>) << " and " << sizeof(std::shared_ptr<Texture>) << '\n';
}
