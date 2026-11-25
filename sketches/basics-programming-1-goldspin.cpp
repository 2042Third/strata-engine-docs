// Practice 5: the turn of one frame for a plain coin and a gold coin, as the script's OnUpdate computes it.
#include <iostream>

int main()
{
	const float degreesPerSecond = 90.0f;
	const float deltaTime = 0.02f; // one frame of 0.02 seconds, 50 frames per second

	bool isGold = false; // the coin as the Inspector shows it: the box is not ticked
	float speed = degreesPerSecond;
	if (isGold)
		speed = speed * 2.0f;
	std::cout << "plain coin: " << speed * deltaTime << " degrees\n";

	isGold = true; // the box is ticked
	speed = degreesPerSecond;
	if (isGold)
		speed = speed * 2.0f;
	std::cout << "gold coin: " << speed * deltaTime << " degrees\n";
	return 0;
}
