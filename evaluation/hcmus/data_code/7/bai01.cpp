#include <iostream>

using namespace std;

const int MAXDISK = 10000;

void orderDiskStack(int a[], int disks, int diskListening){
	int pos = disks - 1, temp = diskListening;
	for (int i = disks - 1; i >= 0; i--){
		if (a[i] != diskListening){
			a[pos] = a[i];
			pos--;
		}
	}
	a[0] = diskListening;
}

int main(){
	int disks, changes, diskListening;
	int A[MAXDISK];
	cout << "Input number of disks: ";
	cin >> disks;
	cout << "Input number of changes: ";
	cin >> changes;
	for (int i = 0; i < disks; i++){
		A[i] = i + 1;
	}
	cout << "The order of changes: ";
	for (int i = 0; i < changes; i++){
		cin >> diskListening;
		orderDiskStack(A, disks, diskListening);
	}
	cout << "Disk stack: ";
	for (int i = 0; i < disks; i++){
		cout << A[i] << ' ';
	}
	return 0;
}
