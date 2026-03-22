#include <iostream>

using namespace std;

int main() {
	int a, b, tong;
	if (a > b) {
		int c = a;
		a = b;
		b = c;
	}
	cin >> a;
	cin >> b;
	for (int i = a; i <= b; i++) {
		if (i % 2 == 0) {
			tong += i;
		}
	}
	cout << tong;
	
	return 0;
}
