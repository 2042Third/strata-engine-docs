// A scoped enumeration with a fixed type, cast to a number and back, and used as a set of flags.
#include <cstdint>
#include <iostream>

enum class Access : uint8_t
{
	None = 0,
	Read = 1u << 0,
	Write = 1u << 1,
	Execute = 1u << 2
};

constexpr Access operator|(Access a, Access b) { return static_cast<Access>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b)); }
constexpr Access operator&(Access a, Access b) { return static_cast<Access>(static_cast<uint8_t>(a) & static_cast<uint8_t>(b)); }
constexpr bool HasFlag(Access value, Access flag) { return (value & flag) == flag; }

int main()
{
	const Access mine = Access::Read | Access::Execute;
	std::cout << "number " << static_cast<int>(mine) << ", size " << sizeof(Access) << '\n';
	std::cout << "read " << HasFlag(mine, Access::Read) << ", write " << HasFlag(mine, Access::Write) << '\n';
	std::cout << "from number 2: " << (static_cast<Access>(2) == Access::Write) << '\n';
	return 0;
}
