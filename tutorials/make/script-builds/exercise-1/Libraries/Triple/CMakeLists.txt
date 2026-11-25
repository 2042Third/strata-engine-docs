add_library(Triple STATIC Triple.cpp)
target_include_directories(Triple PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
# A static library is copied into the module, so it is built as the module is: position independent code and the same C runtime.
set_target_properties(Triple PROPERTIES POSITION_INDEPENDENT_CODE ON MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
