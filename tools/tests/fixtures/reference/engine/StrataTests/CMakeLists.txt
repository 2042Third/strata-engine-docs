# A pretend engine file in the shape of the CTest names (tools/tests/test_reference.py).
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/CoreShards.json" STRATA_CORE_SHARDS)
foreach(index RANGE ${lastShard})
	string(JSON shardName GET "${STRATA_CORE_SHARDS}" Shards ${index} Name)
	add_test(NAME StrataTests.Core.${shardName}
		COMMAND StrataTests "--test-suite=${shardSuites}")
	set_tests_properties(StrataTests.Core.${shardName} PROPERTIES LABELS "core")
endforeach()

add_test(NAME StrataTests.Perf COMMAND StrataTests --test-suite=Perf.*)
set_tests_properties(StrataTests.Perf PROPERTIES LABELS "perf;gpu" RUN_SERIAL TRUE)

# A frame count that is not a whole number is refused.
foreach(frames abc 0)
	add_test(NAME StrataRuntime.InvalidFrames.${frames}
		COMMAND "${CMAKE_COMMAND}" "-DCOMMAND=Game;--frames;${frames}")
endforeach()

if(WIN32)
	add_test(NAME StrataTools.Offline COMMAND python Offline.py)
else()
	add_test(NAME StrataTools.Offline COMMAND python3 Offline.py)
endif()
