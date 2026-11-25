# Part review: world/sub-scenes

- wrong: the request's state diagram had no Cancel from `LoadingScene`; `SceneLoadRequest::Cancel` cancels any unfinished request (`SceneLoader.cpp:333-340`). Added the arrow, and the alt now says the first three states lead to Cancelled.
- wrong: the worked example of 20,000 entities said the update creates 1,341 entities "in about 2.04 ms"; at 1,500 ns each they take 2.01 ms.
