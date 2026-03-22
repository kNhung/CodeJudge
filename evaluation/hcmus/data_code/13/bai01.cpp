#include <iostream>

const int MAX_DISKS = 10000;

void rearrangeDisks(int disks[], int numDisks, int changes[], int numChanges) {
    for (int i = 0; i < numChanges; i++) {
        int diskToMove = changes[i];

        int diskPosition = -1;
        for (int j = 0; j < numDisks; j++) {
            if (disks[j] == diskToMove) {
                diskPosition = j;
                break;
            }
        }

        for (int j = diskPosition; j > 0; j--) {
            disks[j] = disks[j - 1];
        }
        disks[0] = diskToMove;
    }
}

int main() {
    int numDisks;
    std::cout << "Input number of disks: ";
    std::cin >> numDisks;

    int disks[MAX_DISKS];
    std::cout << "Disk stack: ";
    for (int i = 0; i < numDisks; i++) {
        disks[i] = i + 1;
        std::cout << disks[i] << " ";
    }
    std::cout << std::endl;

    int numChanges;
    std::cout << "Input number of changes: ";
    std::cin >> numChanges;

    int changes[MAX_DISKS];
    std::cout << "The order of changes: ";
    for (int i = 0; i < numChanges; i++) {
        std::cin >> changes[i];
    }

    rearrangeDisks(disks, numDisks, changes, numChanges);

    std::cout << "Disk stack: ";
    for (int i = 0; i < numDisks; i++) {
        std::cout << disks[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}
