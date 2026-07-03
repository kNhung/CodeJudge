#include<iostream>
using namespace std;


int  main() {

	int n;
	cin >> n;

	if (1000 >= n || n >= 9999) {
		cout << "n khong hop le";
		return 1;
	}

	int a, b, c, d;
	a = n / 1000;
	b = (n - a * 1000) / 100;
	c = (n - a * 1000 - b * 100) / 10;
	d = n % 10;

	if (a == d && c == b) {
		cout << n;
	}
	else if ((a == d && b != c) || (a == c && b != d) || (b == d && a != c)) {
		if (a == d && b != c) {
			if (b > c) cout << a << b << d;
			else cout << a << c << d;
		}
		if (a == c && b != d) {
			cout << a << b << c;
		}
		if (b == d && a != c) {
			cout << b << c << d;
		}
	}
	else {
		cout << "-1";
	}


	return 0;
}