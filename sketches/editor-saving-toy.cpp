// A toy background save: snapshot in the frame, write on another thread, then mark the save point.
#include <atomic>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

struct Scene
{
	std::vector<std::string> Names;
};

static void WriteAtomically(const std::filesystem::path& target, const Scene& snapshot)
{
	// Write beside the target, then replace it in one step: a crash leaves the old file or the new one.
	const std::filesystem::path temporary = target.string() + ".tmp";
	{
		std::ofstream file(temporary);
		for (const std::string& name : snapshot.Names)
			file << name << '\n';
	}
	std::filesystem::rename(temporary, target);
}

int main()
{
	const std::filesystem::path target = "strata-toy-save.txt";
	Scene scene{ { "Camera", "Sun" } };
	size_t edits = 2;      // Edits applied to the scene so far
	size_t savedEdits = 0; // The save point: how many edits the file on disk holds

	// Frame 1: the only work of the frame is a copy and a number.
	const Scene snapshot = scene;
	const size_t savePoint = edits;
	std::atomic<bool> release = false; // Holds the job so that the frames below happen while it "writes"
	std::atomic<bool> done = false;
	std::thread job([&]()
	{
		while (!release.load())
			std::this_thread::yield();
		WriteAtomically(target, snapshot);
		done.store(true, std::memory_order_release);
	});

	// Frames 2 and 3: the person goes on editing.
	scene.Names.push_back("Tree");
	edits++;
	scene.Names.push_back("Rock");
	edits++;
	release.store(true);

	// A later frame: the job ended, so the main thread publishes the result.
	while (!done.load(std::memory_order_acquire))
		std::this_thread::yield();
	job.join();
	savedEdits = savePoint;
	const size_t naiveSaved = edits; // What marking "everything saved" now would claim

	std::ifstream file(target);
	std::string line;
	size_t lines = 0;
	while (std::getline(file, line))
		lines++;
	std::cout << "file holds " << lines << " names, scene has " << scene.Names.size() << "\n";
	std::cout << "modified: " << (edits != savedEdits ? "yes" : "no") << "\n";
	std::cout << "naive mark at the end would say modified: " << (edits != naiveSaved ? "yes" : "no") << "\n";
	file.close(); // Windows refuses to remove an open file
	std::filesystem::remove(target);
	return 0;
}
