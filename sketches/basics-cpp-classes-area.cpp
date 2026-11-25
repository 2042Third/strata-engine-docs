// Practice 2: one call through a base reference reaches the derived Area because Area is virtual.
#include <iostream>

struct Shape
{
	virtual ~Shape() = default;
	virtual float Area() const { return 0.0f; }
};

struct Square : Shape
{
	float Side = 4.0f;
	float Area() const override { return Side * Side; }
};

void Print(const Shape& shape) { std::cout << "area " << shape.Area() << "\n"; }

int main()
{
	Print(Square());
}
