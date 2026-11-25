# Part review of `reference/commands`

- unclear: the Vector row's "or one number for every component" read as an array with one number per component; `ReadVector` in `Strata/src/Strata/Reflection/PropertyJson.cpp` takes a single number and sets every component to it, so the row now says "or one number, which every component takes".
