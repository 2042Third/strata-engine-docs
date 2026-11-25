# Part review: basics/cpp-modern

- unclear: "At the pin" in the concepts section is the book's own word, unknown to the reader; dropped.
- gap: the section said Strata writes no requires clause, but the script header `StrataScriptCore/Include/StrataScript/Script.h` uses requires expressions 15 times (`if constexpr (requires { &T::OnCreate; })`); one sentence now names the form and reads it.
