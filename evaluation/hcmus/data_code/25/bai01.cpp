#include <iostream>
using namespace std;

const int N = 1e4 + 25;

int num_disk, num_change;
int order[N];
int new_order[N];

void solve(int disk) {
    int index = 2;
    new_order[1] = disk;
    for (int i = 1; i <= num_disk; ++i) {
        if (order[i] != disk) {
            new_order[index] = order[i];
            ++index;
        }
    }
    for (int i = 1; i <= num_disk; ++i) order[i] = new_order[i];
    for (int i = 1; i <= num_disk; ++i) new_order[i] = 0;
}

int main() {
    cout << "Input number of disks: ";
    cin >> num_disk;

    cout << "Input number of changes: ";
    cin >> num_change;

    for (int i = 1; i <= num_disk; ++i) order[i] = i;
    cout << "The order of changes: ";
    for (int i = 1; i <= num_change; ++i) {
        int disk;
        cin >> disk;
        solve(disk);
    }

    cout << "Disk stack: ";
    for (int i = 1; i <= num_disk; ++i) cout << order[i] << " ";
    return 0;
}
