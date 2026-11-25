// Forwarding keeps an argument's kind: a named object is copied, a moved one is moved.
#include <iostream>
#include <utility>

struct Tracer
{
	Tracer() = default;
	Tracer(const Tracer&) { std::cout << "copied\n"; }
	Tracer(Tracer&&) noexcept { std::cout << "moved\n"; }
};

template<typename... Args>
void Forwarding(Args&&... args) { Tracer item(std::forward<Args>(args)...); }

template<typename... Args>
void Naive(Args&&... args) { Tracer item(args...); }

int main()
{
	Tracer tracer;
	std::cout << "forwarding a named object: "; Forwarding(tracer);
	std::cout << "forwarding a moved object: "; Forwarding(std::move(tracer));
	std::cout << "naive, a moved object: "; Naive(std::move(tracer));
}
