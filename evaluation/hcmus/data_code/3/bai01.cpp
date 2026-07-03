#include <iostream>
#include <cmath>
#include <string>
#include <cstdlib>
#include <fstream>

using namespace std;

//int MAX = 100;

void createArr(int arr[], int n){
	for (int i = 1; i <= n; i++){
		arr[i-1] = i;
	}
}
void printArr(int arr[], int n){
	for (int i = 0; i < n; i++){
		cout << arr[i] << " ";
	}
}

int findpos(int arr[], int n, int k){
	for (int i = 0; i < n; i++){
		if (arr[i] == k) return i;
	}
}

void deleteAtPos(int arr[], int n, int k){
	int temp[100];
	for (int i = 0; i < k; i++){
		temp[i] = arr[i];
	}
	for (int i = k + 1; i < n; i++){
		temp[i - 1] = arr[i];
	}
	for (int i = 0; i < n - 1; i++){
		arr[i] = temp[i];
	}
	arr[n] = NULL;
}

void addAtStart(int arr[], int n, int k){
	int temp[100];
	temp[0] = k;
	for (int i = 0; i < n - 1; i++){
		temp[i + 1] = arr[i];
	}
	for (int i = 0; i < n; i++){
		arr[i] = temp[i];
	}
}

void Changing(int arr[], int changes[], int n, int k){
	for (int i = 0; i < k; i++){
		int pos = findpos(arr, n, changes[i]);
		deleteAtPos(arr, n, pos);
		addAtStart(arr, n, changes[i]);
	}
}

int main(){
	int n, k;
	string s;
	cout << "Input number of disks: ";
	cin >> n;
	int arr[100];
	createArr(arr, n);
	cout << "Input number of changes: ";
	cin >> k;
	int changes[100];
	cout << "The order of changes: ";
	for (int i = 0; i < k; i++){
		cin >> changes[i];
	}
	Changing(arr, changes, n, k);
	printArr(arr, n); 
	return 0;
}