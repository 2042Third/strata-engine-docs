# Part review of `reference/core`

- wrong: the first include listed the Core basics of `Strata/src/stpch.h` as `Base.h`, `Log.h`, `Assert.h` and `Profiling.h`; the file at the pin also includes `PlatformDetection.h`, which the list now names.
- checked without change: the `UUID` text form (`{:016X}`), the CRC-32C check value, `ReadArray` and `ReadString` defaults, `c_MaxSizeOption` 65,535, the fields of `Version.h.in` and the CMake files named in the last section.
