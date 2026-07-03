#include <iostream>

using namespace std;

bool KiemTraSoChan(int n) {
	if (n % 2 == 0){
		return 1;
	}
	else{
		return 0;
	}
	return 0;
}

int main() {
	int a;
	int b;
	int i;
	int Tong = 0;
	
	cout << "Nhap a: ";
	cin >> a;
	cout << "Nhap b: ";
	cin >> b;
	
	for (int i = a; i <= b; i++) {
		if(KiemTraSoChan(i)) {
			Tong = Tong + i;
		} 
	}
	cout << Tong;
	return 0;
}