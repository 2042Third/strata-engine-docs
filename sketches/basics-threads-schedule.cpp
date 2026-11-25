// One order in which two threads can run "counter = counter + 1": each thread's line is three steps.
#include <iostream>

int main()
{
	int counter = 5;
	int registerA = counter;   // thread A reads 5
	int registerB = counter;   // thread B reads 5, before A has written
	registerA = registerA + 1; // thread A computes 6
	registerB = registerB + 1; // thread B computes 6
	counter = registerA;       // thread A writes 6
	counter = registerB;       // thread B writes 6 over it
	std::cout << "counter = " << counter << " after two increments of 5\n";
	return 0;
}
