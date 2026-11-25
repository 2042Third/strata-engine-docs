# Part review of `core/jobs`

- wrong: the worked number said Strata measured frames of about 3 ms stretching to 10-30 ms while an import ran; the pin's `Docs/Architecture.md` gives that as what a full-size pool at normal priority would do (only the 5-27 ms and 2.0-2.8 ms are measured), and the sentence now says "would stretch", by Strata's own estimate.
- unclear: the problem section bolded **main thread**, a term homed on `core/frame-loop` and marked at its first use on this page; the bold is removed.
