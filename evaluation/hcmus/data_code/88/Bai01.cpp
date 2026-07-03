#include <iostream>
using namespace std;

int main() {
	int a, b, tong = 0;
	int minz=0, maxz=0;
	cout << "Nhap vao hai so a va b: ";
	cin >> a >> b;
	if (a > b) {
		for (int i = b; i <= a; i++) {
			if (i % 2 == 0) { tong += i; }
		}
		cout << "Tong cac so chan cua doan a va b la: " << tong << endl;
	}
	else {
		for (int i = a; i <=b ; i++) {
			if (i % 2 == 0) { tong += i; }
			
		}
		cout << "Tong cac so chan cua doan a va b la: " << tong << endl;
	}
	return 0;
}