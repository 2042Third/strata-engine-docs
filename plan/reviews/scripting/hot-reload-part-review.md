# Part review of `scripting/hot-reload`

- wrong: the why box said the C ABI is described in scripting/script-system; it is taught on scripting/abi-sdk; the link now goes there ("the page on the ABI").
- contradiction: the note said the rule "only fields survive" is stated in scripting/script-system; this page is the rule's home and script-system states no such rule; now it says that the script system's `Coin` follows it (its `OnReload` calls `OnCreate`).
- wrong: the Coin example said `m_Phase` makes "the bob keep its place"; the bob is `sin(m_Time * 2.5 + m_Phase)` and `m_Time` restarts, so it jumps; now "the coins still bob out of step with each other".
- wrong: the log line was given as `Reloaded script module 'Game' (4 classes)` for a ThirdPerson copy; the module is named by its CMake target and the sample registers 13 classes: now `Reloaded script module 'ThirdPersonScripts' (13 classes)` (ScriptEngine.cpp:120, Samples/ThirdPerson/Scripts/CMakeLists.txt).
