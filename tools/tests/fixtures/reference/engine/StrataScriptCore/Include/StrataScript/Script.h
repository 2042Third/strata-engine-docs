#pragma once
// A pretend engine file: the SDK's macros (tools/tests/test_reference.py).

// Registers a script class.
#define ST_SCRIPT_CLASS(Type) ST_SCRIPT_DETAIL_CLASS(Type, __COUNTER__)

// Declares a field of the class.
#define ST_SCRIPT_FIELD(Member) \
	ST_SCRIPT_DETAIL_FIELD(Member)

#define ST_SCRIPT_DETAIL_CLASS(Type, Number) struct Type##Number
