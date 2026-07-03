#include <iostream>

using namespace std;

int tinhTongSoChan (int a, int b) {
	int sum = 0;
	
	for (int i = a; i <= b; i++) {
		if ((i % 2) == 0) {
			sum = sum + i;
		}
	}
	
	return sum;
}

int main () {
	int a, b;
	
	cout << "Nhap a: ";
	cin >> a;
	cout << "Nhap b: ";
	cin >> b;
	
	if (a <= b) {
		cout << tinhTongSoChan (a, b);
	} else {
		cout << "a phai <= b";
	}
	
	return 0;
}
