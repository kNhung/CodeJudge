#include <iostream>

using namespace std;

int KTraSoDoiXung(int n) {
	int a, b, c, d;
	int x, y;
	int n2 = n;
	a = n / 1000;
	d = n % 10;
	x = n / 10;
	c = x % 10;
	y = x / 10;
	b = y % 10;
	
	if ((a == d) && (b == c)) {
		cout << n2;
		return 0;
	}
	if ((a == d) && (b != c)) {
		if (b > c) {
			cout << a*100 + b*10 + d;
			return 0;
		}
		if (c > b) {
			cout << a*100 + c*10 + d;
			return 0;
		}
	}
	if (a == c) {
		cout << a*100 + b*10 + c;
		return 0;
	}
	if (b == d) {
		cout << b*100 + c*10 + d;
		return 0;
	}
	else {
		cout << "-1";
		return 0;
	}
	return 0;
 }
 
 int main() {
 	int n;
 	cout << "Nhap n (1000 <= n <= 9999): ";
 	cin >> n;
 	KTraSoDoiXung(n);
 	
 	return 0;
 }