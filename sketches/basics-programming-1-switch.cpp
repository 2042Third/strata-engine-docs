// A scoped enumeration and a switch on it: one case runs on into the next, and default catches the rest.
#include <iostream>

enum class Mode { Normal, Hidden, Locked };

int main()
{
	const Mode mode = Mode::Hidden;
	switch (mode)
	{
		case Mode::Hidden:
			std::cout << "hidden\n";
			[[fallthrough]]; // no break: the lines of the next case run too
		case Mode::Locked:
			std::cout << "locked\n";
			break;
		default:
			std::cout << "other\n";
			break;
	}
}
