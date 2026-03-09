#include <iostream>
using namespace std;

#define MAX 100

int main(){
	int disk[MAX];
	int nDisk, nChange, count;
	
	cout << "Input number of disks: ";
	cin >> nDisk;
	for (int i = 0; i < nDisk; i++){
		disk[i] = i + 1;
	}
	
	int change[MAX];
	cout << "Input number of changes: ";
	cin >> nChange;
	cout << "The order of changes: ";
	for (int i = 0; i < nChange; i++){
		cin >> change[i];
	}
	
	int pos = nDisk - 1;
	for(int i = 0; i < nChange; i++){
		for(int j = nDisk - 1; j >= 0; j--){
			if (disk[j] != change[i]){
				disk[pos--] = disk[j];
			}
		}
		count++;
		disk[0] = change[i];
	}
	for(int i = 0; i < nDisk; i++){
		cout << disk[i];
	}
	return 0;
}

