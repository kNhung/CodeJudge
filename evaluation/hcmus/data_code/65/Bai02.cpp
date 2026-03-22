#include <iostream>
#include <cmath>

using namespace std;

int demChuSo (int n) {
	int i = 0;
	
	while (n != 0) {
		n = n / 10;
		i = i + 1;
	}
	
	return i;
}

int kiemTraSoAutomorphic(int a, int b) {
	int temp = b;
	int i = demChuSo (b);
	int mu = pow (10, i);
	
	while (temp >= a) {
		temp = temp % mu;
		if (temp == a) {
			return 1;
		}
		mu = mu / 10;
	}
	
	return 0;
}

int main () {
	int n;
	
	cin >> n;
	
	if (n > 0) {
		int BinhPhuong = n * n;
		cout << kiemTraSoAutomorphic(n, BinhPhuong);
	} else {
		cout << "n phai > 0";
	}
	
	return 0;
}
