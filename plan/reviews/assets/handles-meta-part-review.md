# Part review of `assets/handles-meta`

- wrong: Check yourself 4 said a scan gives a new handle to a `.meta` holding 0; `ReadAssetMeta` treats a zero handle as `Invalid`, so the scan reports it and ignores the source; only `0x10` (built-in range) gets a new handle.
