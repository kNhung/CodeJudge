#include<iostream>

using namespace std;

int main() {
	int n;
	cin >> n;
	if (n <= 0) {
		cout << "n khong hop le !";
		return 1;
	}
	int Binh_Phuong = n * n;

	int dem = 0;
	int k = 10;

	while (true) {

		if ( Binh_Phuong % k == n) {
			dem++;
			break;
		}

		k *= 10;
	}

	if (dem != 0) {
		cout << "1";
	}
	else {
		cout << "0";
	}

	return 0;
}