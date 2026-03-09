#include <iostream>
#include <cmath>

using namespace std;

int tinh_tong_cac_uoc(int n) {
	int sum = 0;
	for ( int i = 1; i < n; i++) {
		if (n % i == 0){
			sum += i;
		}
	}
	return sum;
}

int main() {
	int a, b;
	cin >> a;
	cin >> b;
	if (tinh_tong_cac_uoc(a) == b && tinh_tong_cac_uoc(b) == a) {
		cout << 1;
	} else cout << 0;
	return 0;
}
