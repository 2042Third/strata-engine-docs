// CRTP: the base template returns the derived type, so calls chain without losing it.
#include <iostream>

template<typename Derived>
struct Builder
{
	int Id = 0;
	Derived& WithId(int id)
	{
		Id = id;
		return static_cast<Derived&>(*this);
	}
};
struct CoinBuilder : Builder<CoinBuilder>
{
	bool IsGold = false;
	CoinBuilder& Gold() { IsGold = true; return *this; }
};

int main()
{
	CoinBuilder builder;
	builder.WithId(7).Gold();
	std::cout << "id " << builder.Id << ", gold " << builder.IsGold << '\n';
}
