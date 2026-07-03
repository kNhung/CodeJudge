#include <iostream>
using namespace std;

void swap (int &a, int &b) {
	int tmp = a;
	a = b;
	b = tmp;
}

int main() {
	int n_disks, n_changes, c[10000], d[10000];
	cout << "Input number of disks: ";
	cin >> n_disks;
	for (int i = 0; i < n_disks; i++) {
		d[i] = i + 1;
	}
	cout << "Input number of changes: ";
	cin >> n_changes;
	cout << "The order of changes: ";
	for (int i = 0; i < n_changes; i++) {
		cin >> c[i];
	}
	for (int i = 0; i < n_changes; i++) {
		for (int j = 0; j < n_disks; j++) {
			if (c[i] == d[j]) {
				for (int k = j; k > 0; k--) {
					swap (d[k], d[k - 1]);
				}
			}
		}
	}
	for (int i = 0; i < n_disks; i++) {
		cout << d[i] << " ";
	}
	return 0;
}
