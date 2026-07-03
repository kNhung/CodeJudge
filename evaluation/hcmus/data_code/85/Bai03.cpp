#include <iostream>
#include <cmath>

using namespace std;

int main() {
	int n;
	cin >> n;
	if (n < 1000 || n > 9999) {
		cout << "Wrong input";
	} else {
		int a = n / 1000;
		int b = (n - a * 1000) / 100;
		int c = (n - a * 1000 - b * 100) / 10;
		int d = n % 10;
		if (a == d && b == c) {
			cout << n;
		} else if (a == d && b > c) {
			cout << a << b << d;
		} else if (a == d && b < c) {
			cout << a << c << d;
		} else if (a != d && b == c) {
			cout << b << c;
		} else if (a != c && b == d) {
			cout << b << c << d;
		} else if (a == c && b != d) {
			cout << a << b << c;
		} else cout << -1;
	}
	return 0;
}
