#include <cmath>
#include <cstdio>
#include <set>
#include <thread>

struct Context
{
	float TimeScale = 1.0f;
};

// The table: plain function pointers, each taking the context first.
struct HostTable
{
	void (*SetTimeScale)(Context* context, float timeScale);
	float (*GetTimeScale)(Context* context);
};

static std::set<const Context*> s_Contexts;
static std::thread::id s_OwnerThread = std::this_thread::get_id();
static bool s_CallInProgress = false;
static int s_SetCalls = 0;

// The first guard: refuse every call that is not allowed, and say why.
static Context* ResolveContext(Context* context, const char* function)
{
	if (!context || !s_Contexts.count(context))
		std::printf("%s: invalid context\n", function);
	else if (std::this_thread::get_id() != s_OwnerThread)
		std::printf("%s: wrong thread\n", function);
	else if (!s_CallInProgress)
		std::printf("%s: no script call in progress\n", function);
	else
		return context;
	return nullptr;
}

static void HostSetTimeScale(Context* context, float timeScale)
{
	s_SetCalls++;
	Context* resolved = ResolveContext(context, "SetTimeScale");
	if (!resolved)
		return;
	if (!std::isfinite(timeScale) || timeScale < 0.0f)
	{
		std::printf("SetTimeScale: %.1f is not a finite, non-negative number\n", timeScale);
		return;
	}
	resolved->TimeScale = timeScale;
}

static float HostGetTimeScale(Context* context)
{
	Context* resolved = ResolveContext(context, "GetTimeScale");
	return resolved ? resolved->TimeScale : 1.0f;
}

int main()
{
	Context context;
	s_Contexts.insert(&context);
	const HostTable host = { &HostSetTimeScale, &HostGetTimeScale };

	host.SetTimeScale(&context, 0.5f);
	s_CallInProgress = true;
	host.SetTimeScale(nullptr, 0.5f);
	host.SetTimeScale(&context, -1.0f);
	std::thread([&]() { host.SetTimeScale(&context, 2.0f); }).join();
	host.SetTimeScale(&context, 0.5f);
	std::printf("time scale %.1f after %d calls\n", host.GetTimeScale(&context), s_SetCalls);
	return 0;
}
