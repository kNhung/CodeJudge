#include <iostream>

void swap(int &a, int &b) {
	int t = a;
	a = b;
	b = t;
}

int main(void) {
	int disks[10000], indexes[10000];
	int n_disks;
	std::cout << "Input number of disks: ";
	std::cin >> n_disks;
	
	for (int i = 0; i < n_disks; ++i) {
		disks[i] = i;
		indexes[i] = i + 1;
	}
	
	int changes;
	std::cout << "Input number of changes: ";
	std::cin >> changes;
	std::cout << "The order of changes: ";
	
	for (int i = 0; i < changes; ++i) {
		int disk;
		std::cin >> disk;
		disks[disk - 1] = -i - 1;
	}
	
	for (int i = 1; i < n_disks; ++i) {
		for (int j = i; j > 0; --j) {
			if (disks[j] < disks[j - 1]) {
				swap(disks[j], disks[j - 1]);
				swap(indexes[j], indexes[j - 1]);
			} else break;
		}
	}
	
	std::cout << "Disk stack: ";
	
	for (int i = 0; i < n_disks; ++i) {
		std::cout << indexes[i] << ' ';
	}
	
	std::cout << '\n';
	
	return 0;
}
