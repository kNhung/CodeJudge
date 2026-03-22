#include <iostream> 

using namespace std;

bool TinhTongUocSo(int a, int b) {
	int i = 1;
	int Tong1 = 0;
	int Tong2 = 0;
	for (i = 1; i < a; i++){
		if (a % i == 0) {
			Tong1 = Tong1 + i;
		}
	}
	for (i = 1; i < b; i++) {
		if (b % i == 0) {
			Tong2 = Tong2 + i;
		}
	}
	if (Tong1 == b && Tong2 == a){
		return 1;
	}
	else {
		return 0;
	}
	return 0;
}

int main() {
	int a;
	int b;
	cout << "Nhap a: ";
	cin >> a;
	cout << "Nhap b: ";
	cin >> b;
	
	cout << TinhTongUocSo(a, b);
	
	return 0;
}