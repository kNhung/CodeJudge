#include<iostream>
using namespace std;



int main() {
	int a, b, tong = 0;
	cin >> a >> b;

	for (int i = a;i <= b;i++) {
		if (i % 2 == 0) {
			tong += i;
		}
	}

	cout << tong;

	return 0;
}