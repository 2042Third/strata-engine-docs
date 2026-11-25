# Part review: world/serialization

- contradiction: the contract listed "a value out of range" among data that gives a warning; a file load clamps a ranged value silently (`PropertyInfo::SetValue`, as `world/reflection` and the round trip test of `world/tutorial-component` say). Now "an unknown component", which warns in both forms.
- contradiction: the toy section defined **union-find** in bold, a term homed on `basics/trees-graphs`; now plain, and markterms marks its first use there instead of the later one.
