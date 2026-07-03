# include <iostream>
# include <cmath>
# include <string>
# include <cstring>
# include <cstdlib>
# include <stdlib.h>

# define Max 100

using namespace std;

void inputArr (int arr[], int &n) {
	for (int i = 0; i < n; i++) {
		arr[i] = i + 1;
	}
}

void inputNewArr (int arr[], int &n) {
	for (int i = 0; i < n; i++) {
		cin >> arr[i];
	}
}

void printArr (int arr[], int &n) {
	for (int i = 0; i < n; i++) {
		cout << arr[i] << " ";
	}
}

void inputChanges (int arr[], int nArr, int newArr[], int &nNewArr) {
	int temp [Max];
	int m = nNewArr - 1;
	
	// Dao chu so trong mang moi
	for (int i = 0; i < nNewArr; i++) {
		temp[i] = newArr[m];
		m--;
	}
	
	for (int i = 0; i < nNewArr; i++) {
		newArr[i] = temp[i];
	}	

}

int main () {
	int n, m;
	int arr[Max], newArr[Max];
	
	cout << "Input number of disks: ";
	cin >> n;
	inputArr (arr, n);
	
	cout << "Input number of changes: ";
	cin >> m;
	
	cout << "The order of changes: ";
	inputNewArr (newArr, m);
	
	cout << "Disk stack: ";
	inputChanges (arr, n, newArr, m);
	printArr (newArr, m);
	printArr (arr, n);
	
	return 0;
}
