# Part review of `assets/loading`

- wrong: the ReplaceLoadedAsset callouts split at line 826/827, but `SetStateLocked(..., Ready)` is line 826; the callouts are now lines 823-825 (abandon, set Loaded) and 826-830 (Ready, generation, content change).
