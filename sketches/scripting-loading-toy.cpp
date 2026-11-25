// A toy host: open a shared library, look up two functions by name, call them, close the library.
// The library is the C runtime of the system, so the program needs no file of its own.
#include <cstddef>
#include <cstdio>

#if defined(_WIN32)
#include <windows.h>
#else
#include <dlfcn.h>
#endif

namespace
{

	using AbsFunction = int (*)(int);
	using LengthFunction = std::size_t (*)(const char*);

#if defined(_WIN32)
	constexpr const char* c_LibraryName = "msvcrt.dll";
	void* OpenLibrary(const char* name) { return reinterpret_cast<void*>(LoadLibraryA(name)); }
	void* FindSymbol(void* library, const char* name) { return reinterpret_cast<void*>(GetProcAddress(static_cast<HMODULE>(library), name)); }
	void CloseLibrary(void* library) { FreeLibrary(static_cast<HMODULE>(library)); }
#else
#if defined(__APPLE__)
	constexpr const char* c_LibraryName = "libSystem.dylib";
#else
	constexpr const char* c_LibraryName = "libc.so.6";
#endif
	void* OpenLibrary(const char* name) { return dlopen(name, RTLD_NOW); }
	void* FindSymbol(void* library, const char* name) { return dlsym(library, name); }
	void CloseLibrary(void* library) { dlclose(library); }
#endif

}

int main()
{
	void* library = OpenLibrary(c_LibraryName);
	if (!library)
	{
		std::printf("cannot load the library\n");
		return 1;
	}

	const auto absolute = reinterpret_cast<AbsFunction>(FindSymbol(library, "abs"));
	const auto length = reinterpret_cast<LengthFunction>(FindSymbol(library, "strlen"));
	if (!absolute || !length)
	{
		std::printf("a function is missing\n");
		CloseLibrary(library);
		return 1;
	}

	std::printf("abs(-42) = %d\n", absolute(-42));
	std::printf("strlen(\"strata\") = %zu\n", length("strata"));
	CloseLibrary(library);
	return 0;
}
