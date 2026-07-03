#include <iostream>

using namespace std;

bool KiemTraAutomorphic(int n) {
	int Automorphic;
	int d;
	d = n % 10;
	Automorphic = n * n;
	if (Automorphic > 100) {
		if (Automorphic % 100 == n){
			return 1;
		}
		else {
			return 0;
		}
	}
	if (Automorphic > 10) {
		if (Automorphic % 10 == d) {
			return 1;
		}
		else {
			return 0;
		}
	}
	return 0;
}

int main() {
	int n;
	cout << "Nhap n: ";
	cin >> n;
	
	while (n < 0) {
		cout << "ERROR!!! Nhap lai n (n > 0): ";
		cin >> n;
	}
	cout << KiemTraAutomorphic(n);
	
	return 0;
}