#include <iostream>
#include <cmath>
using namespace std;

void createArray (int a[], int n){
	int val = 1;
	for (int i = 0; i < n; i++){
		a[i] = val;
		val++;
	}
}

void inputArray (int a[], int n){
	cout << "The order of changes: ";
	for (int i = 0; i < n; i++){
		cin >> a[i];
	}
}
void printArray (int a[], int n){
	for (int i = 0; i < n; i++){
		cout << a[i] << " ";
	}
}

void removeElement (int a[], int &n, int pos){
	for (int i = n - 1; i > pos; i--){
		a[i] = a[i + 1];
	}
	n--;
}

void removeVal (int a[], int &n, int val){
	for (int i = 0; i < n; i++){
		if (a[i] == val){
			removeElement(a, n, i);
			i--;
		}
	}
}

void addElement (int a[], int &n, int k){
	n++;
	for (int i = 0; i < n; i++){
		a[i] = a[i - 1];
	}
	a[0] = k;
}

void findDiskStack (int a[], int &n, int change[], int nchange){
	for (int i = 0; i < nchange; i++){
		for (int j = 0; j < n; j++){
			if (change[i] == a[i]){
				removeVal(a, n, a[j]);
				addElement(a, n, a[j]);
			}
		}
	}
}
int main (){
	int a[10000], change[10000];
	int n,nchange;
	do{
		cout << "Input number of disks: ";
		cin >> n;
	} while (n <= 0 || n >= 10000);
	createArray(a, n);
	
	do{
		cout << "Input number of changes: ";
		cin >> nchange;
	} while (nchange < 0);
	inputArray(change, nchange);
	
	cout << "Disk stack: ";
	findDiskStack(a, n, change, nchange);
	printArray(a, n);
	return 0;
}
