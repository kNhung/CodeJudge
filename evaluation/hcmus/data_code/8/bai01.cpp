#include <iostream>
#include <cstring>
#include <string>
#include <cmath>
using namespace std;
void nhapGiaTri(int &n, int &m, int a[]) {
	cout << "Input number of disks: ";
	cin >> n;
	cout << "Input number of changes: ";
	cin >> m;
	cout << "The order of changes: ";
	for (int i = 0; i < m; i++) {
		cin >> a[i];
	}
}
void doiGiaTri(int n, int a[]) {
	for (int i = n; i >= 1; i--) {
		a[i] = a[i-1];
	} 
}
int timGiaTri(int a[], int b[], int n, int m, int x) {
	int k = 0;
		for (int j = 0; j < n; j++) {
			if (b[x] == a[j]) {
				k = j;
				break;
			}
	}
	return k;
}
int main() {
	int n, m;
	int a[1000];
	int b[1000];
	nhapGiaTri(n, m, a);
	int d = 1;
	for (int i = 0;i < n; i++) {
		b[i] = d;
		d++;
	}
	for (int j = 0; j < m; j++) {
		int k = timGiaTri(b, a, n, m, j);
		doiGiaTri(k, b);
		b[0] = a[j]; 
		}
	cout << "Disk stack: ";
	for (int i = 0; i < n; i++) {
		cout << b[i] << " ";
	}
	return 0;
}
