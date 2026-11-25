# Part review: image/tone-mapping

- wrong: the Filmic value two stops above middle gray (example and Summary) was 0.5069 from $0.6923^{1.3825} = 0.6013$; with the pin's `c_FilmicContrast` 1.39788385 the power is 0.6015 and the value 0.5068 (code 189 unchanged).
- wrong: Check yourself 2 gave $0.5385^{1.3825} = 0.4250$ and 0.6515; the values are 0.4249, 0.5751 and 0.6516.
- wrong: Exercise 2 put the `Tonemapper` registration near line 452 of `RendererComponents.cpp`; at the pin it is line 486.
