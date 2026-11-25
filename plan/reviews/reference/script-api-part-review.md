# Part review of `reference/script-api`

- wrong: "Any other type fails to compile, with a `static_assert` that names the member"; the assert in `ScriptClassBuilder::Field` (`StrataScriptCore/Include/StrataScript/Script.h`) prints "Unsupported script field type: use bool, int32_t, ..." and names no member; the sentence now says its message lists the types it accepts.
