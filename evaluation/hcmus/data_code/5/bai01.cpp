#include <iostream>
#include <cstring>
#include <string>

using namespace std;

#define MAX 10000

void printArr (int a[], int n){
	for (int i=0; i<n; i++){
		cout << a[i] << " ";
	}
}

void fillArr (int a[], int n){
	for (int i=0; i<n; i++){
		a[i] = i+1;
	}
}

void deleteNum (int a[], int &n, int pos){
	for (int i=pos; i<n; i++){
		a[i] = a[i+1];
	}
	n--;
}

void change (int a[], int &n, int b[], int &b1){
	
	for (int i=0; i<b1; i++){
		for (int j=0; j<n; j++){
			if (b[i] == a[j]){
				deleteNum (a,n,j);
			}
		}
	}
	n = n + b1;
	
	for (int i=n-b1-1; i>=0; i--){
		a[i+b1] = a[i];
	}

	for (int i=0 ;i<b1; i++){
		a[i] = b[b1-1-i];
	}
	
}

int main(){
	int n = 0;
		do{
		cout << "Input number of disks : ";
		cin >> n;
		if (n < 1 || n > 10000)
			cout << "Too many disks";
	}while (n < 1 || n > 10000);
	
	int arr[n];
	fillArr (arr,n);
	
	int b1 = 0;
	do{
		cout << "Input number of changes: ";
		cin >> b1;
		if (b1 < 1 || b1 > 10000)
			cout << "Invalid";
	}while (b1 < 1 || b1 > 10000);
	
	int b[b1];
	
	cout << "The order of changes : ";
		for (int i=0; i<b1; i++){
			cin >> b[i];
		}
	
	change (arr,n,b,b1);
	
	cout << "Disk stack : ";
	
	printArr (arr,n);
	
	
	return 0;
}
