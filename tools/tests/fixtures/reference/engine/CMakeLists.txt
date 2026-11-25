# A pretend engine file in the shape of the build's options (tools/tests/test_reference.py).
cmake_minimum_required(VERSION 3.25)
project(Strata VERSION 0.7.0)

option(STRATA_BUILD_TESTS "Build the unit tests" ON)
option(STRATA_WITH_AUDIO
	"Build the audio module (\"miniaudio\")"
	OFF)
