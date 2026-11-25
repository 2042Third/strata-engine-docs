// The preprocessor replaces macro text before the compiler reads it, so parentheses decide the result.
#include <iostream>

#define BAD_SQUARE(x) x * x
#define SQUARE(x) ((x) * (x))
#define SHOW(expression) std::cout << #expression << " = " << (expression) << " at line " << __LINE__ << '\n'

#if defined(ST_DIST)
	#define MODE "shipping"
#else
	#define MODE "development"
#endif

int main()
{
	SHOW(BAD_SQUARE(1 + 2));
	SHOW(SQUARE(1 + 2));
	std::cout << "mode " << MODE << '\n';
	return 0;
}
