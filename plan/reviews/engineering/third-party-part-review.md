# Part review of `engineering/third-party`

- wrong: the list of what `EXCLUDE_FROM_ALL` marks left out Dear ImGui (`add_library(imgui STATIC EXCLUDE_FROM_ALL`, `Strata/vendor/CMakeLists.txt:92`); added.
- gap: the two groups left out `MikkTSpace` and `meshoptimizer`, which are built by default and linked by the renderer layer (`Strata/CMakeLists.txt:70`) though the notices list them as editor only; one sentence added.
- wrong: the derived-code table of `ThirdPartyNotices.md` was said to have one row; it has two (radiance-cascades-lab and `ltc_code`), so the item and Exercise 1's answer name both license texts.
