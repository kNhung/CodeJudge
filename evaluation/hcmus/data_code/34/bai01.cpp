#include<iostream>
#include<string>
#include<cmath>
using namespace std;

void print(int a[], int n){
	for (int i = 0; i < n; i++) cout << a[i] << ' ';
}

void input(int a[], int n){
	for (int i = 0; i < n; i++) cin >> a[i];
}

void Execute(int a[], int n, int b[], int changes){
	int j = 0;
	while(j < changes){
		for (int i = 0; i < n; i++){
			if (a[i] == b[j]){
				swap(a[0], a[i]);
				for (int k = 1; k < i; k++)
					swap(a[k], a[i]);
			}
		}
		j++;
	}
}

int main(){
	int n;
	cout << "Input number of disks: ";
	cin >> n;
	int a[n];
	for (int i = 0; i < n; i++) a[i] = i + 1;
	int changes;
	cout << "Input number of changes: ";
	cin >> changes;
	int b[changes];
	cout << "The order of changes: ";
	for (int i = 0; i < changes; i++) cin >> b[i];
	Execute(a, n, b, changes);
	cout << "Disk stack: ";
	print(a, n);
	return 0;
}
