#include <iostream>
using namespace std;
int main() {
	int a, b, tong1 = 0, tong2 = 0;
	cout << "Nhap vao hai so ban be de kiem tra: ";
	cin >> a >> b;
	for (int i = 1; i <= a / 2; i++) {
		if (a % i == 0) tong1 += i;
	}
	for (int j = 1; j <= b / 2; j++) {
		if (b % j == 0) tong2 += j;
	}
	if (tong2 == a && tong1 == b) cout << a << " và " << b << " la số bạn bè";
	else cout << a << " và " << b << " không là số bạn bè";
	return 0;
}