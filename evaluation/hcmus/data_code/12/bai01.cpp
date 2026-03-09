#include <iostream>

using namespace std;

void inputArr (int arr [], int len) {
	for (int i = 0; i < len; i++) {
		cin >> arr [i];
	}
}

void printArr (int arr [], int len) {
	for (int i = 0; i < len; i++) {
		if (i == len - 1) cout << arr [i];
		else cout << arr [i] << ' ';
	}
}

void setStack (int arr[], int n, int change_list[], int changes) {
	int pos = 0;
	while (pos < changes) {
		for (int j = 0; j < n; j ++) {
			if (arr[j] == change_list[pos]) {
				if (j == 0) continue;
				else {
					for (int k = j; k > 0; k--) {
						arr[k] = arr [k - 1];
					}
					arr [0] = change_list[pos];
				}
			}
		}
		pos ++;
	}
}

int main() {
	int n, changes;
	do {
		cout << "Input number of disks: ";
		cin >> n;
	} while (n < 1 || n > 10000);
	
	do {
		cout << "Input number of changes: ";
		cin >> changes;
	} while (n < 1 || changes > n);	
	
	int change_list [changes], disk_stack [n];
	
	for (int i = 0; i < n; i++) {
		disk_stack[i] = i + 1;
	}
		
	cout << "The order of changes: ";
	inputArr (change_list, changes);
	
	setStack (disk_stack, n, change_list, changes);
	
	cout << "Disk stack: ";
	
	printArr (disk_stack, n);

	return 0;
}
