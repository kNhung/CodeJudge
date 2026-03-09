#include<iostream>
#include<cstring>
#include<fstream>
using namespace std;

void inputArray(int a[], int &n) {
	for (int i=0; i < n; i++) {
		cin >> a[i];
	}
}

void printArray(int a[], int n) {
	for (int i=0; i < n; i++) {
		cout << a[i] << " ";
	}
}

void removeElement(int a[], int &n, int index) {
	for (int i = index; i < n-1; i++) {
		a[i] = a[i+1];
	}
	n--;
} 


void addElement(int a[], int &n, int index, int value) {
	
	for (int i = n; i > index; i--) {
		a[i] = a[i-1];
		a[index] = value;
	}
	n++;
} 

int main() {
	int a[10000];
	int order[100];
	int disk, change;
	int n=0;
	int num = 0;
	do {
		cout << "Input number of disks: ";
		cin >> disk;
	} while (n > 10000);

	for (int i=0; i < disk; i++) {
		num+=1;
		a[i] = num; 
	}
	cout << "Input number of changes: ";
	cin >> change;
	
	cout << "The order of changes: ";
	inputArray(order, change);
	for (int i=0; i < change; i++) {
		for (int j =0; j < disk; j++) {
			if(a[j] == order[i]) {
				removeElement(a, disk, j);
				addElement(a, disk, 0, order[i]);
				
			}
		}
		
	}
	printArray(a, n);
	
	return 0;
}
