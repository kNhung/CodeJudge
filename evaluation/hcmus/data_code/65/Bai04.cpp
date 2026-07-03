#include <iostream>

using namespace std;

int tongUoc (int n) {
	int sum = 0;
	
	for (int i = 1; i < n; i++) {
		if ((n % i) == 0) {
			sum = sum + i;
		}
	}
	
	return sum;
}

int kiemTraCapSoBanBe (int a, int b) {
	if (a == tongUoc (b) && b == tongUoc (a)) {
		return 1;
	} else {
		return 0;
	}
}

int main () {
	int a, b;
	
	cout << "Nhap a: ";
	cin >> a;
	cout << "Nhap b: ";
	cin >> b;
	
	cout << kiemTraCapSoBanBe(a, b);
	
	return 0;
}
