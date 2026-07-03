#include <iostream>

using namespace std;

int tonguocso(int n) {
	int sum = 0;
	for (int i = 1; i < n; i++) {
		if (n % i == 0) {
			sum += i;
		}
	}
	return sum;
}

bool ktrsobanbe(int a, int b) {
	if (tonguocso(a) == b && tonguocso(b) == a) {
		return true;
	}
}

int main() {
	int a, b;
	cout << "Nhap a: ";
	cin >> a;
	cout << "Nhap b: ";
	cin >> b;
	
	cout << ktrsobanbe(a, b);
	
	return 0;
}