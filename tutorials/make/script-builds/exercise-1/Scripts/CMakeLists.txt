# Game scripts of "Coin Run": every .cpp and .h file in this directory (and below) belongs to the script module CoinRunScripts.
cmake_minimum_required(VERSION 3.25)
project(CoinRunScripts CXX)

set(STRATA_ENGINE_DIR "" CACHE PATH "The Strata folder, a source checkout or an installation (the editor sets it)")
find_package(StrataScriptCore CONFIG REQUIRED PATHS "${STRATA_ENGINE_DIR}/StrataScriptCore/CMake" NO_DEFAULT_PATH)
strata_add_script_module(CoinRunScripts SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")

# The library lies outside this folder, so add_subdirectory needs a folder in the build tree for its files.
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../Libraries/Triple" "${CMAKE_CURRENT_BINARY_DIR}/Triple")
target_link_libraries(CoinRunScripts PRIVATE Triple)
