# Part review: gpu/shaders (group 1 of 2)

- wrong: "The shared include files ... there are 40 of them"; Strata/shaders/Include holds 42 .slang files at the pin; now 42.
- wrong: "Editing Forward.frag.slang compiles its six entries again"; at the pin Scene/Forward.frag has 23 variants (area lights and field forms included, Strata/CMakeLists.txt:179-201), 24 entries in all; now 24.
