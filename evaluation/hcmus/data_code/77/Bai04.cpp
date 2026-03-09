#include<iostream>
using namespace std;

int Tong_Uoc(int n, int Tong) {
	for (int i = 1;i < n;i++) {
		if (n % i == 0) {
			Tong += i;
		}
	}
	return Tong;
}

int main() {
	int Tonguoc1 = 0, Tonguoc2 = 0;
	int a, b;
	cin >> a >> b;

	if (Tong_Uoc(a, Tonguoc1) == b && Tong_Uoc(b, Tonguoc2) == a) {
		cout << "1";
	}
	else cout << "0";

	return 0;
}